"""Verified state cutover with writes paused; never two live authoritative stores.

Archives contain private conversations: keep them in restricted storage, apply
retention rules, and never commit them to Git. Checksums detect corruption, not
authorization; only a trusted operator may supply an import archive.
"""

import hashlib
import json


def checksum(document):
    return hashlib.sha256(
        json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def export_sessions(store, principal, session_ids):
    entries = []
    for session in session_ids:
        document = store.load(principal.owner, session)
        if not document["revision"]:
            raise ValueError("Cannot export a session that does not exist.")
        entries.append(
            {
                "session_id": session,
                "document": document,
                "checksum": checksum(document),
            }
        )
    return {"schema_version": 1, "owner": principal.owner, "sessions": entries}


def import_sessions(target, principal, archive):
    if archive.get("schema_version") != 1 or archive.get("owner") != principal.owner:
        raise PermissionError("Archive schema/owner is not authorized for this import.")
    # Validate every document before performing any writes.
    seen = set()
    for entry in archive["sessions"]:
        if entry["session_id"] in seen:
            raise ValueError("Duplicate session ID in archive.")
        seen.add(entry["session_id"])
        document = entry["document"]
        if checksum(document) != entry["checksum"]:
            raise ValueError("State checksum mismatch.")
        if target.load(principal.owner, entry["session_id"])["revision"]:
            raise ValueError("Cutover target already contains this session.")
        for case in document["cases"].values():
            entity = case["entity"]
            principal.authorize(
                entity["product_id"], entity["region"], entity["category"]
            )
            versions = [v["version"] for v in case["versions"]]
            if versions != list(range(1, len(versions) + 1)):
                raise ValueError("Scenario version chain is incomplete.")
    # A multi-session cutover is not one distributed transaction. Record imported
    # IDs, keep source frozen, and resume/rollback explicitly if a later write fails.
    imported = []
    for entry in archive["sessions"]:
        target.restore(principal.owner, entry["session_id"], entry["document"])
        restored = target.load(principal.owner, entry["session_id"])
        if checksum(restored) != entry["checksum"]:
            raise RuntimeError(
                "Restored state checksum mismatch; keep cutover disabled."
            )
        imported.append(entry["session_id"])
    return imported


def transfer_paid_budget(source, target):
    """With both hosts stopped, carry spent calls into an unused target ledger.

    Do not resume the old writer after cutover. This transfers, rather than
    resets, the 70-call ceiling. Ledger transfer is separate from case archives.
    """
    used = source.used
    target.restore_used(used)
    if target.used != used:
        raise RuntimeError("Paid-call ledger verification failed.")
    return used
