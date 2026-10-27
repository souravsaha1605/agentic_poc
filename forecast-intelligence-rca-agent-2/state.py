"""Durable owner-scoped state with one atomic commit per completed turn.

The stored document contains turns, cases, immutable versions and request
receipts. A compare-and-swap prevents concurrent turns overwriting each other.
SQLite is for local development; Delta is the notebook adapter. Neither adapter
falls back to an empty history when storage fails.
"""

import copy
import json
import re
import sqlite3
from pathlib import Path


class ConflictError(RuntimeError):
    """Reload state before retrying a turn after another writer committed."""


def new_session():
    return {
        "revision": 0,
        "active_case": None,
        "cases": {},
        "turns": [],
        "receipts": {},
        "providers": {},
    }


class SQLiteStateStore:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS sessions "
                "(id TEXT PRIMARY KEY, owner TEXT NOT NULL, revision INTEGER NOT NULL, body TEXT NOT NULL)"
            )

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def load(self, owner, session_id):
        with self.connect() as db:
            row = db.execute(
                "SELECT owner, body FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
        if not row:
            return new_session()
        if row[0] != owner:
            raise PermissionError("Session is unavailable for this principal.")
        return json.loads(row[1])

    def commit(self, owner, session_id, expected, document):
        updated = copy.deepcopy(document)
        updated["revision"] = expected + 1
        body = json.dumps(updated, allow_nan=False)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT owner, revision FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
            if row and row[0] != owner:
                raise PermissionError("Session is unavailable for this principal.")
            if (row[1] if row else 0) != expected:
                raise ConflictError(
                    "Session changed; reload and retry with the same request ID."
                )
            db.execute(
                "INSERT INTO sessions VALUES (?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
                "revision=excluded.revision, body=excluded.body",
                (session_id, owner, expected + 1, body),
            )
        return updated

    def delete(self, owner, session_id):
        """Explicit owner-authorized deletion for retention/erasure workflows."""
        self.load(owner, session_id)
        with self.connect() as db:
            db.execute(
                "DELETE FROM sessions WHERE id=? AND owner=?", (session_id, owner)
            )

    def restore(self, owner, session_id, document):
        """Operator cutover only: create an absent session, preserving revisions."""
        with self.connect() as db:
            try:
                db.execute(
                    "INSERT INTO sessions VALUES (?,?,?,?)",
                    (
                        session_id,
                        owner,
                        document["revision"],
                        json.dumps(document, allow_nan=False),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ConflictError(
                    "Restore refuses to overwrite an existing session."
                ) from exc


def checked_table(table):
    # Identifiers come from deployment configuration, never from a model.
    if not re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*){1,2}", table
    ):
        raise ValueError("Expected a schema-qualified table identifier.")
    return table


class DeltaStateStore:
    """Dedicated Delta document table; serialize notebook writes per session.

    Delta MERGE uses the expected revision. A random commit token also detects
    a lost compare-and-swap. Delta tables need serializable isolation; the job
    and notebook host must not have two independent initializers for one ID.
    Use SQLite/Azure ETags for a host with simultaneous new-session admissions.
    """

    def __init__(self, spark, table):
        self.spark, self.table = spark, checked_table(table)
        spark.sql(
            f"CREATE TABLE IF NOT EXISTS {self.table} "
            "(id STRING, owner STRING, revision BIGINT, body STRING, token STRING) USING DELTA "
            "TBLPROPERTIES ('delta.isolationLevel'='Serializable')"
        )

    def load(self, owner, session_id):
        from pyspark.sql import functions as F

        rows = (
            self.spark.table(self.table)
            .where(F.col("id") == F.lit(session_id))
            .select("owner", "body")
            .collect()
        )
        if not rows:
            return new_session()
        if len(rows) != 1:
            raise ConflictError("Duplicate session IDs require operator repair.")
        if rows[0]["owner"] != owner:
            raise PermissionError("Session is unavailable for this principal.")
        return json.loads(rows[0]["body"])

    def commit(self, owner, session_id, expected, document):
        import uuid

        current = self.load(owner, session_id)
        if current["revision"] != expected:
            raise ConflictError("Session changed; reload before retrying.")
        updated = copy.deepcopy(document)
        updated["revision"] = expected + 1
        token = uuid.uuid4().hex
        from delta.tables import DeltaTable
        from pyspark.sql import functions as F

        source = self.spark.createDataFrame(
            [
                (
                    session_id,
                    owner,
                    expected + 1,
                    json.dumps(updated, allow_nan=False),
                    token,
                )
            ],
            "id STRING, owner STRING, revision LONG, body STRING, token STRING",
        )
        (
            DeltaTable.forName(self.spark, self.table)
            .alias("t")
            .merge(source.alias("s"), F.col("t.id") == F.col("s.id"))
            .whenMatchedUpdateAll(
                condition=(F.col("t.owner") == F.col("s.owner"))
                & (F.col("t.revision") == F.lit(expected))
            )
            .whenNotMatchedInsertAll(condition=F.lit(expected == 0))
            .execute()
        )
        rows = (
            self.spark.table(self.table)
            .where(F.col("id") == F.lit(session_id))
            .select("token")
            .collect()
        )
        if len(rows) != 1 or rows[0]["token"] != token:
            raise ConflictError("Concurrent update detected; reload state.")
        return updated

    def restore(self, owner, session_id, document):
        """Run with notebook writes paused, as part of a verified cutover."""
        if self.load(owner, session_id)["revision"]:
            raise ConflictError("Restore refuses to overwrite an existing session.")
        import uuid

        token = uuid.uuid4().hex
        from delta.tables import DeltaTable
        from pyspark.sql import functions as F

        source = self.spark.createDataFrame(
            [
                (
                    session_id,
                    owner,
                    document["revision"],
                    json.dumps(document, allow_nan=False),
                    token,
                )
            ],
            "id STRING, owner STRING, revision LONG, body STRING, token STRING",
        )
        (
            DeltaTable.forName(self.spark, self.table)
            .alias("t")
            .merge(source.alias("s"), F.col("t.id") == F.col("s.id"))
            .whenNotMatchedInsertAll()
            .execute()
        )
        rows = (
            self.spark.table(self.table)
            .where(F.col("id") == F.lit(session_id))
            .select("token")
            .collect()
        )
        if len(rows) != 1 or rows[0]["token"] != token:
            raise ConflictError("Restore refused an existing/concurrent session.")

    def delete(self, owner, session_id):
        self.load(owner, session_id)
        from delta.tables import DeltaTable
        from pyspark.sql import functions as F

        DeltaTable.forName(self.spark, self.table).delete(
            (F.col("id") == F.lit(session_id)) & (F.col("owner") == F.lit(owner))
        )


class AzureBlobStateStore:
    """Small durable application store using one JSON blob and ETag per session.

    Azure SDK imports are lazy so offline tests need no cloud credentials.
    Owner checks precede reads/updates and ETags protect concurrent workers.
    """

    def __init__(self, container):
        self.container = container

    def _blob(self, session_id):
        import hashlib

        return self.container.get_blob_client(
            hashlib.sha256(session_id.encode()).hexdigest() + ".json"
        )

    def _read(self, owner, session_id):
        from azure.core.exceptions import ResourceNotFoundError

        try:
            download = self._blob(session_id).download_blob()
            stored = json.loads(download.readall())
        except ResourceNotFoundError:
            return new_session(), None
        if stored["owner"] != owner:
            raise PermissionError("Session is unavailable for this principal.")
        return stored["document"], download.properties.etag

    def load(self, owner, session_id):
        return self._read(owner, session_id)[0]

    def commit(self, owner, session_id, expected, document):
        from azure.core import MatchConditions
        from azure.core.exceptions import ResourceExistsError, ResourceModifiedError

        current, etag = self._read(owner, session_id)
        if current["revision"] != expected:
            raise ConflictError("Session changed; reload before retrying.")
        updated = copy.deepcopy(document)
        updated["revision"] = expected + 1
        payload = json.dumps({"owner": owner, "document": updated}, allow_nan=False)
        try:
            if etag:
                self._blob(session_id).upload_blob(
                    payload,
                    overwrite=True,
                    etag=etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            else:
                self._blob(session_id).upload_blob(payload, overwrite=False)
        except (ResourceExistsError, ResourceModifiedError) as exc:
            raise ConflictError(
                "Concurrent state update; retry with the same request ID."
            ) from exc
        return updated

    def restore(self, owner, session_id, document):
        from azure.core.exceptions import ResourceExistsError

        try:
            self._blob(session_id).upload_blob(
                json.dumps({"owner": owner, "document": document}, allow_nan=False),
                overwrite=False,
            )
        except ResourceExistsError as exc:
            raise ConflictError(
                "Restore refuses to overwrite an existing session."
            ) from exc

    def delete(self, owner, session_id):
        from azure.core import MatchConditions

        _, etag = self._read(owner, session_id)
        if etag:
            self._blob(session_id).delete_blob(
                etag=etag, match_condition=MatchConditions.IfNotModified
            )
