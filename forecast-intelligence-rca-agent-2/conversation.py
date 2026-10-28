"""Shared conversation core: identity -> context -> plan -> facts -> saved answer.

Simple supported language is resolved deterministically. Ambiguity produces a
small clarification rather than an expensive model guess. Channel adapters must
provide an authenticated Principal and stable request/session IDs.
"""

import copy
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from contracts import AnalysisPlan, TurnRequest
from state import ConflictError
from tool_executor import ToolExecutor


def now():
    return datetime.now(timezone.utc).isoformat()


class ConversationService:
    def __init__(self, business, store, selector=None):
        self.business, self.store, self.selector = business, store, selector

    def resolve(self, message, principal, active):
        catalog = []
        for item in self.business.provider.catalog():
            try:
                principal.authorize(
                    item["product_id"], item["region"], item["category"]
                )
                catalog.append(item)
            except PermissionError:
                continue
        ids = re.findall(r"\b(?:P\d{3,5}|SKU-?\d+)\b", message, re.I)
        ids = list(dict.fromkeys(i.upper() for i in ids))
        region = next(
            (
                r
                for r in ["North", "South", "East", "West", "Central"]
                if re.search(r"\b" + r + r"\b", message, re.I)
            ),
            None,
        )
        category = next(
            (
                r["category"]
                for r in catalog
                if re.search(r"\b" + re.escape(r["category"]) + r"\b", message, re.I)
            ),
            None,
        )
        store = re.search(r"\b(?:S\d{3}|STORE\d+)\b", message, re.I)
        # Category aggregation is explicit and limited to one region. The trusted
        # principal must have a wildcard product grant; row scopes are checked
        # again after retrieval by BusinessService.
        if (
            not ids
            and category
            and region
            and re.search(r"\bcategory\b", message, re.I)
        ):
            if "*" not in principal.products:
                return (
                    None,
                    "Category aggregation is unavailable in your approved product scope.",
                )
            matches = [
                row
                for row in catalog
                if row["category"] == category and row["region"] == region
            ]
            if not matches:
                return None, "No approved products match that category and region."
            return {
                "product_id": "*",
                "product_name": category + " category",
                "region": region,
                "category": category,
                "store_id": store.group().upper() if store else None,
            }, None
        if (
            not ids
            and active
            and active["entity"].get("product_id") == "*"
            and "another product" not in message.lower()
        ):
            entity = copy.deepcopy(active["entity"])
            requested_region = region or entity["region"]
            requested_category = category or entity["category"]
            matches = [
                row
                for row in catalog
                if row["region"] == requested_region
                and row["category"] == requested_category
            ]
            if not matches:
                return None, "No approved products match that aggregate scope."
            entity.update(region=requested_region, category=requested_category)
            if store:
                entity["store_id"] = store.group().upper()
            return entity, None
        if len(ids) > 1:
            return (
                None,
                "Please select one product for this case; compare saved cases separately.",
            )
        candidates = []
        if ids:
            candidates = [r for r in catalog if r["product_id"].upper() == ids[0]]
            if not candidates:
                aliases = self.business.provider.resolve_alias(ids[0])
                candidates = [r for r in catalog if r["product_id"] in aliases]
            if not candidates:
                return (
                    None,
                    "That product is unavailable in your approved scope. Please check the exact ID.",
                )
        else:
            candidates = [
                r
                for r in catalog
                if r.get("product_name")
                and re.search(
                    r"\b" + re.escape(r["product_name"]) + r"\b", message, re.I
                )
            ]
            if not candidates:
                # Names/aliases are governed data. Never turn P001 into P0001.
                for token in re.findall(r"\b[\w-]+\b", message):
                    approved = self.business.provider.resolve_alias(token)
                    candidates.extend(r for r in catalog if r["product_id"] in approved)
            if not candidates and active and "another product" not in message.lower():
                candidates = [
                    r
                    for r in catalog
                    if r["product_id"] == active["entity"]["product_id"]
                ]
        if region:
            candidates = [r for r in candidates if r["region"] == region]
        elif (
            active
            and candidates
            and all(
                r["product_id"] == active["entity"]["product_id"] for r in candidates
            )
        ):
            candidates = [
                r for r in candidates if r["region"] == active["entity"]["region"]
            ]
        if category:
            candidates = [r for r in candidates if r["category"] == category]
        unique = {(r["product_id"], r["region"], r["category"]): r for r in candidates}
        if len(unique) != 1:
            choices = ", ".join(f"{p}/{r}" for p, r, _ in list(unique)[:5])
            return None, (
                "Please choose a product and region"
                + (f": {choices}." if choices else ".")
            )
        entity = copy.deepcopy(next(iter(unique.values())))
        if store:
            entity["store_id"] = store.group().upper()
        elif (
            active
            and entity["product_id"] == active["entity"]["product_id"]
            and entity["region"] == active["entity"]["region"]
        ):
            entity["store_id"] = active["entity"].get("store_id")
        return entity, None

    @staticmethod
    def classify(message):
        text = message.lower()
        if re.search(r"\b(close|resolve) (this |the )?case\b", text):
            return "CLOSE_CASE", None
        if re.search(r"what[ -]if", text):
            return "WHAT_IF", "compare_scenarios"
        if any(
            s in text
            for s in [
                "we changed",
                "we increased",
                "we decreased",
                "outcome",
                "accuracy improved",
            ]
        ):
            return "OUTCOME_UPDATE", None
        if any(
            s in text
            for s in [
                "why",
                "root cause",
                "rca",
                "contributor",
                "caused",
                "constraining",
                "constrained",
                "deteriorat",
                "accuracy is poor",
            ]
        ):
            return "RCA", "run_forecast_rca"
        if any(s in text for s in ["inventory", "stockout", "stock"]):
            return "INVENTORY_RETRIEVAL", "get_inventory_context"
        if "revenue" in text:
            return "REVENUE_RETRIEVAL", "get_revenue_context"
        if any(
            s in text for s in ["trend", "pattern", "history", "historical", "last "]
        ):
            return "TREND_ANALYSIS", "analyze_historical_pattern"
        if re.search(r"forecast|analy[sz]e|performance|\bP\d{3,5}\b", message, re.I):
            return "FORECAST_RETRIEVAL", "get_forecast_context"
        return "UNSUPPORTED", None

    def handle(self, principal, request):
        request = TurnRequest.model_validate(request)
        doc = self.store.load(principal.owner, request.session_id)
        signature = hashlib.sha256(
            json.dumps(
                {"message": request.message, "case": request.case_id}, sort_keys=True
            ).encode()
        ).hexdigest()
        receipt = doc["receipts"].get(request.request_id)
        if receipt:
            if receipt["signature"] != signature:
                raise ValueError("Request ID was already used with different content.")
            if receipt.get("grants") != principal.model_dump(mode="json"):
                raise PermissionError(
                    "Entitlements changed; issue a new authorized request."
                )
            # Entitlements may have changed since the original delivery.
            entity = receipt["answer"].get("entity")
            if entity:
                principal.authorize(
                    entity["product_id"], entity["region"], entity["category"]
                )
            return copy.deepcopy(receipt["answer"])
        if (
            request.expected_version is not None
            and request.expected_version != doc["revision"]
        ):
            raise ConflictError("Expected session version does not match.")
        if len(doc["turns"]) >= 2000:
            raise ValueError(
                "Session retention limit reached; archive it and start a new owned session."
            )
        active_id = request.case_id or doc["active_case"]
        if request.case_id and request.case_id not in doc["cases"]:
            raise PermissionError("Case is unavailable in this owned session.")
        active = doc["cases"].get(active_id)
        entity, question = self.resolve(request.message, principal, active)
        if question:
            return self.finish(
                principal,
                request,
                doc,
                signature,
                {
                    "response": question,
                    "intent": "CLARIFICATION",
                    "scenario_action": "AMBIGUOUS_NEEDS_CLARIFICATION",
                    "tools_called": [],
                },
            )
        intent, tool = self.classify(request.message)
        if intent == "UNSUPPORTED":
            return self.finish(
                principal,
                request,
                doc,
                signature,
                {
                    "response": "Please ask for forecast, inventory, revenue, a historical pattern, RCA or a specific what-if.",
                    "entity": entity,
                    "intent": "CLARIFICATION",
                    "scenario_action": "AMBIGUOUS_NEEDS_CLARIFICATION",
                    "tools_called": [],
                },
            )
        changed = not active or any(
            entity.get(k) != active["entity"].get(k)
            for k in ["product_id", "region", "store_id", "category"]
        )
        new = changed or bool(
            re.search(r"\b(new case|start over|forget this)\b", request.message, re.I)
        )
        action = (
            "CREATE_NEW_SCENARIO"
            if new
            else "UPDATE_ACTIVE_SCENARIO"
            if intent in ("WHAT_IF", "OUTCOME_UPDATE")
            else "CONTINUE_ACTIVE_SCENARIO"
        )
        case = (
            {
                "id": "SCN-" + uuid.uuid4().hex[:12],
                "entity": entity,
                "versions": [],
                "outcomes": [],
                "baseline": None,
                "current": None,
                "previous": None,
                "created_at": now(),
            }
            if new
            else copy.deepcopy(active)
        )
        version = len(case["versions"]) + 1
        evidence, clarification = None, None
        if intent == "CLOSE_CASE":
            if new:
                clarification = "Select an existing owned case before closing it."
            else:
                evidence = {
                    "case_status": "CLOSED",
                    "message": "The saved case and its versions remain available for authorized review.",
                }
        elif intent == "WHAT_IF":
            evidence, clarification = self.what_if(request.message, case)
            if not clarification:
                case["previous"] = copy.deepcopy(case["current"])
                case["current"] = copy.deepcopy(evidence["current"])
                assumption = evidence["assumption"]
                case.setdefault("assumptions", {})[assumption["measure"]] = (
                    copy.deepcopy(assumption)
                )
                if case.get("last_period"):
                    evidence["period"] = copy.deepcopy(case["last_period"])
                    evidence["provenance"] = copy.deepcopy(case["last_provenance"])
        elif intent == "OUTCOME_UPDATE":
            if new:
                clarification = "Select an existing case before reporting its outcome."
            else:
                case["outcomes"].append(
                    {
                        "message": request.message,
                        "reported_at": now(),
                        "provenance": "USER_REPORTED",
                        "verified": False,
                    }
                )
                evidence = {
                    "outcome": "Saved as user-reported and unverified. No causal improvement has been established."
                }
        else:
            # Period and vintage survive follow-ups. Explicit changes replace only those fields.
            params = copy.deepcopy(case.get("plan", {}))
            params.update(
                tool=tool,
                product_id=entity["product_id"],
                region=entity["region"],
                category=entity["category"],
                store_id=entity.get("store_id"),
            )
            dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", request.message)
            if "as of" in request.message.lower() and dates:
                params.update(
                    as_of=dates[0],
                    start=None,
                    end=None,
                    fiscal_period=None,
                    lookback_months=None,
                    relative_period=None,
                )
            elif "vintage" in request.message.lower() and dates:
                params["vintage"] = dates[-1]
            elif len(dates) == 4:
                params.update(
                    start=dates[0],
                    end=dates[1],
                    comparison_start=dates[2],
                    comparison_end=dates[3],
                    compare_previous_period=False,
                    lookback_months=None,
                    relative_period=None,
                    as_of=None,
                    fiscal_period=None,
                )
            elif len(dates) == 2:
                params.update(
                    start=dates[0],
                    end=dates[1],
                    lookback_months=None,
                    relative_period=None,
                    comparison_start=None,
                    comparison_end=None,
                    as_of=None,
                    fiscal_period=None,
                )
            elif dates:
                clarification = 'Specify both ISO start and end dates, or use "as of YYYY-MM-DD" for inventory.'
            weeks = re.search(r"last\s+(\d+)\s+weeks?", request.message, re.I)
            if weeks:
                params.update(
                    lookback_weeks=int(weeks[1]),
                    lookback_months=None,
                    relative_period=None,
                    comparison_start=None,
                    comparison_end=None,
                    start=None,
                    end=None,
                    as_of=None,
                    fiscal_period=None,
                )
            months = re.search(r"last\s+(\d+)\s+months?", request.message, re.I)
            if months:
                params.update(
                    lookback_months=int(months[1]),
                    relative_period=None,
                    comparison_start=None,
                    comparison_end=None,
                    start=None,
                    end=None,
                    as_of=None,
                    fiscal_period=None,
                )
            elif re.search(r"\b(?:last|previous) month\b", request.message, re.I):
                params.update(
                    lookback_months=None,
                    relative_period="previous_month",
                    comparison_start=None,
                    comparison_end=None,
                    start=None,
                    end=None,
                    as_of=None,
                    fiscal_period=None,
                )
            elif re.search(r"\bthis month\b", request.message, re.I):
                params.update(
                    lookback_months=None,
                    relative_period="this_month",
                    comparison_start=None,
                    comparison_end=None,
                    start=None,
                    end=None,
                    as_of=None,
                    fiscal_period=None,
                )
            params["compare_previous_period"] = bool(
                re.search(
                    r"previous period|period.over.period|month.over.month",
                    request.message,
                    re.I,
                )
            )
            fiscal = re.search(r"\bFY\d{4}-P(?:0[1-9]|1[0-2])\b", request.message, re.I)
            if fiscal:
                params.update(
                    fiscal_period=fiscal.group().upper(),
                    lookback_months=None,
                    relative_period=None,
                    start=None,
                    end=None,
                    as_of=None,
                )
            elif re.search(r"\bfiscal\b", request.message, re.I):
                clarification = "Specify an approved source fiscal period such as FY2026-P09. The lab uses calendar-year monthly periods."
            channel = re.search(r"\bchannel\s+(Retail|Online)\b", request.message, re.I)
            if channel:
                params["channel"] = channel[1].title()
            elif re.search(r"\bchannel\b", request.message, re.I):
                clarification = "Select a source channel: Retail or Online."
            mentioned_regions = [
                region
                for region in ["North", "South", "East", "West", "Central"]
                if re.search(r"\b" + region + r"\b", request.message, re.I)
            ]
            if len(mentioned_regions) == 2 and re.search(
                r"compare|comparison|versus", request.message, re.I
            ):
                params["comparison_region"] = next(
                    region for region in mentioned_regions if region != entity["region"]
                )
            params["hypotheses"] = (
                [
                    h
                    for h in [
                        "promotion",
                        "inventory",
                        "price",
                        "seasonality",
                        "competitor",
                        "weather",
                        "revenue",
                        "lifecycle",
                        "mix",
                    ]
                    if h in request.message.lower()
                ]
                if tool == "run_forecast_rca"
                else []
            )
            params["revenue_type"] = (
                "gross" if "gross" in request.message.lower() else "net"
            )
            params["include_trend"] = bool(
                re.search(r"trend|change|comparison", request.message, re.I)
            )
            if entity["product_id"] == "*" and tool == "run_forecast_rca":
                clarification = "RCA requires one resolved product. Use category aggregation for forecast, revenue, inventory or historical patterns."
            if not clarification:
                plan = AnalysisPlan.model_validate(params)
                try:
                    evidence = ToolExecutor(self.business, principal).execute(
                        tool, plan.model_dump()
                    )
                except (ValueError, RuntimeError):
                    return self.finish(
                        principal,
                        request,
                        doc,
                        signature,
                        {
                            "response": "Data is unavailable or failed validation for this scope. No analytical result was fabricated.",
                            "entity": entity,
                            "intent": intent,
                            "scenario_action": action,
                            "tools_called": [tool],
                            "error_code": "DATA_UNAVAILABLE",
                            "success": False,
                        },
                    )
                case["plan"] = plan.model_dump(mode="json")
                case["last_period"] = copy.deepcopy(evidence["period"])
                case["last_provenance"] = copy.deepcopy(evidence["provenance"])
                additions = {}
                if evidence.get("metrics"):
                    metrics = evidence["metrics"]
                    values = {
                        "demand": metrics.get("actual"),
                        "forecast": metrics.get("forecast"),
                    }
                    additions.update(values)
                # What-if inputs come from previously retrieved, validated facts.
                if "inventory" in evidence:
                    additions["inventory"] = evidence["inventory"]
                if "net_revenue" in evidence:
                    additions["revenue"] = evidence["net_revenue"]
                if evidence.get("unit_price") is not None:
                    additions["price"] = evidence["unit_price"]
                if additions:
                    case.setdefault("facts", {}).update(copy.deepcopy(additions))
                    # Reading actual facts must not undo an explicit scenario assumption.
                    applicable = {
                        key: value
                        for key, value in additions.items()
                        if key not in case.get("assumptions", {})
                    }
                    case["current"] = {**(case["current"] or {}), **applicable}
                    if case["baseline"] is None:
                        case["baseline"] = copy.deepcopy(case["current"])
        if clarification:
            return self.finish(
                principal,
                request,
                doc,
                signature,
                {
                    "response": clarification,
                    "entity": entity,
                    "intent": "CLARIFICATION",
                    "scenario_action": "AMBIGUOUS_NEEDS_CLARIFICATION",
                    "tools_called": [],
                },
            )
        case["status"] = {
            "WHAT_IF": "WHAT_IF",
            "OUTCOME_UPDATE": "OUTCOME_REPORTED",
            "RCA": "RCA_IDENTIFIED",
            "CLOSE_CASE": "CLOSED",
        }.get(intent, "ACTIVE")
        snapshot = {
            "version": version,
            "parent_version": version - 1 or None,
            "timestamp": now(),
            "intent": intent,
            "entity": copy.deepcopy(entity),
            "plan": copy.deepcopy(case.get("plan")),
            "baseline": copy.deepcopy(case["baseline"]),
            "current": copy.deepcopy(case["current"]),
            "assumptions": copy.deepcopy(case.get("assumptions", {})),
            "previous": copy.deepcopy(case["previous"]),
            "evidence": evidence,
            "outcomes": copy.deepcopy(case["outcomes"]),
        }
        # Append a fresh object. No earlier version is mutated.
        case["versions"].append(snapshot)
        doc["cases"][case["id"]] = case
        doc["active_case"] = case["id"]
        if intent == "CLOSE_CASE":
            doc["active_case"] = None
        answer = {
            "response": self.render(entity, evidence),
            "entity": entity,
            "scenario_id": case["id"],
            "scenario_version": version,
            "intent": intent,
            "scenario_action": action,
            "tools_called": [tool] if tool else [],
            "evidence": evidence,
        }
        return self.finish(principal, request, doc, signature, answer)

    @staticmethod
    def what_if(message, case):
        if len(re.findall(r"\d+(?:\.\d+)?\s*%", message)) != 1:
            return (
                None,
                "Change one explicit demand, price or inventory assumption at a time.",
            )
        match = re.search(
            r"(demand|price|inventory).*?(increas\w*|decreas\w*|higher|lower|\+|-)\s*(?:by\s*)?(\d+(?:\.\d+)?)\s*%",
            message,
            re.I,
        )
        # Also accepts the original "demand is 15% higher" phrasing.
        if not match:
            match = re.search(
                r"(demand|price|inventory).*?(\d+(?:\.\d+)?)\s*%\s*(higher|lower)",
                message,
                re.I,
            )
            parts = (match[1], match[3], match[2]) if match else None
        else:
            parts = match[1], match[2], match[3]
        if not parts or not case.get("current"):
            return (
                None,
                "First retrieve the baseline; then specify demand, price or inventory and a percentage change.",
            )
        measure, direction, pct = parts
        measure = measure.lower()
        pct = float(pct) * (
            -1 if direction.lower().startswith(("decreas", "lower", "-")) else 1
        )
        if pct < -100 or pct > 1000:
            return None, "Use a percentage between -100% and +1000%."
        current = copy.deepcopy(case["current"])
        if measure not in current or current[measure] is None:
            return (
                None,
                f"The active case has no validated {measure} baseline. Retrieve it before this what-if.",
            )
        previous = current[measure]
        current[measure] = round(previous * (1 + pct / 100), 2)
        return {
            "baseline": copy.deepcopy(case["baseline"]),
            "previous": copy.deepcopy(case["current"]),
            "current": current,
            "assumption": {"measure": measure, "change_pct": pct},
            "delta": round(current[measure] - previous, 2),
            "limitations": [
                "Arithmetic scenario only. A price change does not predict demand; no elasticity or causal effect is assumed.",
                "The demand baseline uses observed sales as an arithmetic proxy; inventory constraints may censor true demand.",
            ],
        }, None

    def render(self, entity, evidence):
        # Facts and labels are backend-owned. A model can rank labels, never invent prose/numbers.
        facts = {
            k: json.dumps(v, default=str, ensure_ascii=True)
            for k, v in evidence.items()
            if k not in ("provenance", "entity")
        }
        chosen = []
        if self.selector:
            try:
                chosen = self.selector.select(
                    {
                        k: v
                        for k, v in facts.items()
                        if k not in ("history", "hypotheses")
                    }
                )
                if not isinstance(chosen, list) or any(
                    key not in facts for key in chosen
                ):
                    chosen = []
            except Exception:
                # Do not expose endpoint/key/error bodies to chat; the facts still work.
                chosen = []
        order = list(dict.fromkeys(chosen + list(facts)))
        lines = [f"{entity['product_id']} | {entity['region']} | {entity['category']}"]
        if evidence.get("period"):
            lines.append(
                f"Period: {evidence['period']['start']} to {evidence['period']['end']}"
            )
        metrics = evidence.get("metrics")
        if metrics:

            def display(value, suffix=""):
                return "unavailable" if value is None else f"{value}{suffix}"

            quantities = [
                f"{label}: {display(metrics[key], ' units')}"
                for key, label in [("forecast", "Forecast"), ("actual", "Actual")]
                if key in metrics
            ]
            percentages = [
                f"{label}: {display(metrics[key], '%')}"
                for key, label in [
                    ("accuracy_pct", "Accuracy (100 - WMAPE)"),
                    ("bias_pct", "Bias"),
                ]
                if key in metrics
            ]
            if quantities:
                lines.append(" | ".join(quantities))
            if percentages:
                lines.append(" | ".join(percentages))
        if "inventory" in evidence:
            lines.append(
                f"Inventory: {evidence['inventory']} | Availability: {evidence['availability']} | Freshness: {evidence.get('freshness', 'unknown')}"
            )
            lines.append(
                "Inventory is a point-in-time balance. Snapshot observations do not establish stockout days."
            )
        if "net_revenue" in evidence:
            lines.append(
                f"Revenue ({evidence['currency']}): gross {evidence['gross_revenue']}; net {evidence['net_revenue']} | {evidence['availability']}"
            )
            if "revenue_change_pct" in evidence:
                lines.append(
                    f"Mean weekly net revenue change: {evidence['revenue_change_pct']}%."
                )
        if "hypotheses" in evidence:
            for hypothesis in evidence["hypotheses"]:
                lines.append(
                    f"{hypothesis['cause'].title()}: {hypothesis['status']} | {hypothesis['reason']}"
                )
                if hypothesis["evidence"]:
                    lines.append(
                        "Evidence: " + json.dumps(hypothesis["evidence"], default=str)
                    )
            lines.append("Confidence: " + evidence["confidence"])
        # Other small deterministic sections (patterns, what-if deltas, outcomes)
        # are rendered by label. Large raw histories are never included here.
        special = {
            "period",
            "metrics",
            "inventory",
            "availability",
            "freshness",
            "snapshot_dates",
            "stockout_days",
            "stockout_snapshots",
            "definition",
            "as_of",
            "hypotheses",
            "confidence",
            "gross_revenue",
            "net_revenue",
            "primary_revenue",
            "revenue_type",
            "currency",
            "unit_price",
            "trend",
            "comparison_definition",
            "revenue_change_pct",
            "forecast_revenue_exposure",
            "exposure_definition",
        }
        lines.extend(
            f"{key.replace('_', ' ').title()}: {facts[key]}"
            for key in order
            if key not in special
        )
        if "provenance" in evidence:
            p = evidence["provenance"]
            lines.append(
                f"Source: {p['source_view']} | as of {p['data_as_of']} | logic {p['logic_version']}"
            )
        return "\n".join(lines)

    def finish(self, principal, request, doc, signature, answer):
        answer["session_version"] = doc["revision"] + 1
        doc["turns"].append(
            {
                "request_id": request.request_id,
                "at": now(),
                "channel": request.channel,
                "user": request.message,
                "assistant": answer["response"],
                "case_id": answer.get("scenario_id"),
                "intent": answer["intent"],
                "action": answer["scenario_action"],
                "tools": answer["tools_called"],
            }
        )
        doc["receipts"][request.request_id] = {
            "signature": signature,
            "answer": copy.deepcopy(answer),
            "grants": principal.model_dump(mode="json"),
        }
        self.store.commit(principal.owner, request.session_id, doc["revision"], doc)
        return answer
