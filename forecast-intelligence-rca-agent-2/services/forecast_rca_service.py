"""Deterministic business calculations for the six approved capabilities.

No model calculates a metric or chooses authorization. Missing evidence stays
missing. Correlation is supporting evidence, not proof of a business cause.
All methods operate on a small, explicitly scoped internal dataset.
"""

import math
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from data_access import as_date

LOGIC_VERSION = "rca-review-5.2"
FEATURE_VERSION = "weekly-5.2"
MIN_WEEKS = {
    "bias": 4,
    "trend": 8,
    "promotion": 8,
    "inventory": 8,
    "price": 8,
    "revenue": 4,
    "seasonality": 52,
    "competitor": 8,
    "weather": 8,
    "lifecycle": 8,
    "mix": 8,
    "quality": 1,
}


def number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def mean(values):
    values = [v for v in values if number(v)]
    return statistics.mean(values) if values else None


def change(previous, current):
    return (
        (current - previous) / abs(previous) * 100
        if previous not in (None, 0) and current is not None
        else None
    )


def rounded(value):
    return round(value, 2) if number(value) else None


def weekly(rows):
    groups = defaultdict(list)
    for r in rows:
        d = as_date(r["date"])
        groups[d - timedelta(days=d.weekday())].append(r)
    return [
        {
            "date": str(d),
            "actual": sum(r["units_sold"] for r in batch),
            "forecast": sum(r["demand_forecast"] for r in batch),
        }
        for d, batch in sorted(groups.items())
    ]


class BusinessService:
    def __init__(self, provider, today=None):
        self.provider = provider
        self.today = today or date.today()

    def prepare(self, plan, principal):
        # A host grant is checked even if the model proposes a different product.
        principal.authorize(plan.product_id, plan.region, plan.category)
        rows = self.provider.fetch(plan)
        if not rows:
            raise ValueError("No data is available for this entity and period.")
        for r in rows:
            principal.authorize(r["product_id"], r["region"], r["category"])
        dates = [as_date(r["date"]) for r in rows]
        end = plan.end or plan.as_of or min(max(dates), self.today)
        start = plan.start or end - timedelta(weeks=plan.lookback_weeks) + timedelta(
            days=1
        )
        # Inventory as-of must search all prior snapshots, including an old one.
        scoped = [
            r
            for r in rows
            if as_date(r["date"]) <= end
            and (plan.tool == "get_inventory_context" or as_date(r["date"]) >= start)
        ]
        if not scoped:
            raise ValueError("No observations at or before the requested cutoff.")
        limitations = []
        # Choose one forecast per target/store. Never duplicate an actual across vintages.
        by_target = defaultdict(list)
        for r in scoped:
            by_target[(str(r["date"]), r["store_id"])].append(r)
        selected = []
        for batch in by_target.values():
            if len({r.get("units_sold") for r in batch}) > 1:
                raise ValueError("Conflicting actuals across forecast vintages.")
            eligible = [
                r
                for r in batch
                if r.get("forecast_generated_date")
                and as_date(r["forecast_generated_date"]) <= as_date(r["date"])
                and (
                    not plan.vintage
                    or as_date(r["forecast_generated_date"]) == plan.vintage
                )
            ]
            if not eligible:
                raise ValueError(
                    "Forecast vintage is unavailable or later than its target date."
                )
            latest = max(as_date(r["forecast_generated_date"]) for r in eligible)
            chosen = [
                r for r in eligible if as_date(r["forecast_generated_date"]) == latest
            ]
            if len(chosen) != 1:
                raise ValueError("Duplicate source grain: product/store/date/vintage.")
            selected.append(chosen[0])
        selected.sort(key=lambda r: (str(r["date"]), r["store_id"]))
        valid = [
            r
            for r in selected
            if number(r.get("units_sold")) and number(r.get("demand_forecast"))
        ]
        if len(valid) != len(selected):
            limitations.append(
                "Null/non-finite actual or forecast: metrics use paired valid observations only."
            )
        if any(r["units_sold"] < 0 for r in valid):
            limitations.append(
                "Returns present: WMAPE denominator uses absolute actual units; bias uses signed net actual."
            )
        points = weekly(valid)
        gaps = any(
            (as_date(b["date"]) - as_date(a["date"])).days > 7
            for a, b in zip(points, points[1:])
        )
        if gaps:
            limitations.append(
                "Missing calendar weeks; historical patterns are not certified for this window."
            )
        provenance = {
            "source_view": self.provider.source,
            "source_version": self.provider.source_version,
            "feature_version": FEATURE_VERSION,
            "logic_version": LOGIC_VERSION,
            "coverage_start": str(min(as_date(r["date"]) for r in selected)),
            "coverage_end": str(max(as_date(r["date"]) for r in selected)),
            "requested_start": str(start),
            "requested_end": str(end),
            "data_as_of": str(max(as_date(r["date"]) for r in selected)),
            "vintage_policy": str(plan.vintage)
            if plan.vintage
            else "latest issued at/before each target",
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
        return selected, valid, points, limitations, provenance, gaps

    def readiness(self, plan, capability, provenance):
        """Scoped lookup only. Full certification runs in bootstrap/scheduled maintenance."""
        matches = [
            r
            for r in self.provider.registry
            if r["product_id"] == plan.product_id
            and r["region"] == plan.region
            and r["capability"] == capability
            and r.get("category") == plan.category
            and r.get("store_id") == (plan.store_id or "*")
            and r["source_version"] == self.provider.source_version
            and str(r["coverage_start"])[:10] <= provenance["coverage_start"]
            and str(r["coverage_end"])[:10] >= provenance["coverage_end"]
        ]
        if not matches:
            return "NOT_TESTABLE"
        row = matches[-1]
        if row["validation"] == "FAIL":
            return "BLOCKED"
        validated = datetime.fromisoformat(
            str(row["validated_at"]).replace("Z", "+00:00")
        )
        if validated.tzinfo is None:
            validated = validated.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - validated > timedelta(days=7):
            return "STALE"
        return row["status"]

    def execute(self, plan, principal):
        selected, rows, points, limits, source, gaps = self.prepare(plan, principal)
        base = {
            "entity": {
                "product_id": plan.product_id,
                "region": plan.region,
                "store_id": plan.store_id,
                "category": plan.category,
                "channel": plan.channel,
                "fiscal_period": plan.fiscal_period,
            },
            "period": {
                "start": source["coverage_start"],
                "end": source["coverage_end"],
            },
            "provenance": source,
            "limitations": limits,
            "data_quality": {
                "status": "PARTIAL" if limits else "SUFFICIENT",
                "observations": len(selected),
                "paired_valid": len(rows),
                "weeks": len(points),
                "gaps": gaps,
            },
        }
        if plan.tool == "get_inventory_context":
            base.update(self.inventory(selected, plan.as_of or plan.end or self.today))
            base["period"] = {
                "start": source["requested_start"],
                "end": source["requested_end"],
            }
        elif plan.tool == "get_revenue_context":
            base.update(self.revenue(selected, plan.revenue_type))
            if plan.include_trend:
                by_week = defaultdict(list)
                for row in selected:
                    day = as_date(row["date"])
                    by_week[day - timedelta(days=day.weekday())].append(row)
                trend = [
                    {
                        "week": str(day),
                        "net_revenue": self.revenue(batch)["net_revenue"],
                    }
                    for day, batch in sorted(by_week.items())
                ]
                base["trend"] = trend[-12:]
                values = [r["net_revenue"] for r in trend]
                half = len(values) // 2
                base["revenue_change_pct"] = (
                    rounded(change(mean(values[:half]), mean(values[half:])))
                    if half
                    else None
                )
                base["comparison_definition"] = (
                    "Change in mean observed weekly net revenue: earlier half versus recent half."
                )
        elif plan.tool == "analyze_historical_pattern":
            base["patterns"] = self.patterns(points)
        elif plan.tool == "run_forecast_rca":
            hyps = plan.hypotheses or list(MIN_WEEKS)
            base["metrics"] = self.forecast(rows)
            base["hypotheses"] = [
                self.hypothesis(h, rows, points, plan, source, gaps, bool(limits))
                for h in hyps
            ]
            base["confidence"] = (
                "MEDIUM"
                if any(h["status"] == "SUPPORTED" for h in base["hypotheses"])
                and not limits
                else "LOW"
            )
            base["recommendations"] = [
                "Validate supported associations with the planning/data owner before intervention."
            ]
            limits.append(
                "Associations do not establish causality; observed sales may be inventory-censored demand."
            )
        elif plan.tool == "get_forecast_context":
            base["metrics"] = self.forecast(rows)
            if not plan.include_summary:
                for key in ("actual", "forecast", "signed_error", "absolute_error"):
                    base["metrics"].pop(key, None)
            if not plan.include_accuracy:
                base["metrics"].pop("wmape_pct", None)
                base["metrics"].pop("accuracy_pct", None)
            if not plan.include_bias:
                base["metrics"].pop("bias_pct", None)
            if plan.include_history:
                base["history"] = points[
                    -12:
                ]  # aggregated weeks, never transaction history
            if plan.include_trend:
                base["patterns"] = self.patterns(points)
        else:
            raise ValueError(
                "Scenario comparisons require authorized persisted state, not source rows."
            )
        if plan.comparison_region or plan.comparison_start:
            # Explicit comparison scopes are independently authorized. Recursive
            # requests clear comparison fields, so this is at most two bounded
            # additional deterministic reads, never a model/tool loop.
            comparisons = {}
            for label, updates in [
                ("region", {"region": plan.comparison_region}),
                (
                    "period",
                    {
                        "start": plan.comparison_start,
                        "end": plan.comparison_end,
                        "as_of": None,
                        "fiscal_period": None,
                    },
                ),
            ]:
                if label == "region" and not plan.comparison_region:
                    continue
                if label == "period" and not plan.comparison_start:
                    continue
                other = plan.model_copy(
                    update={
                        **updates,
                        "comparison_region": None,
                        "comparison_start": None,
                        "comparison_end": None,
                    }
                )
                reference = self.execute(other, principal)
                comparisons[label] = {
                    "entity": reference["entity"],
                    "period": reference["period"],
                    "metrics": reference.get("metrics"),
                    "net_revenue": reference.get("net_revenue"),
                    "provenance": reference["provenance"],
                }
                if base.get("metrics") and reference.get("metrics"):
                    comparisons[label]["accuracy_gap_pp"] = (
                        rounded(
                            base["metrics"]["accuracy_pct"]
                            - reference["metrics"]["accuracy_pct"]
                        )
                        if number(base["metrics"].get("accuracy_pct"))
                        and number(reference["metrics"].get("accuracy_pct"))
                        else None
                    )
            base["comparisons"] = comparisons
        return base

    @staticmethod
    def forecast(rows):
        actual = sum(r["units_sold"] for r in rows)
        forecast = sum(r["demand_forecast"] for r in rows)
        denominator = sum(abs(r["units_sold"]) for r in rows)
        error = sum(abs(r["demand_forecast"] - r["units_sold"]) for r in rows)
        wmape = error / denominator * 100 if denominator else None
        return {
            "actual": rounded(actual) if rows else None,
            "forecast": rounded(forecast) if rows else None,
            "signed_error": rounded(forecast - actual) if rows else None,
            "absolute_error": rounded(error) if rows else None,
            "wmape_pct": rounded(wmape),
            "accuracy_pct": rounded(100 - wmape) if wmape is not None else None,
            "bias_pct": rounded((forecast - actual) / actual * 100) if actual else None,
            "definition": "WMAPE=sum(abs(forecast-actual))/sum(abs(actual)); accuracy=100-WMAPE; units",
        }

    @staticmethod
    def inventory(rows, cutoff):
        # Latest snapshot PER STORE. Summation is allowed across stores, never dates.
        latest = {}
        for r in rows:
            if as_date(r["date"]) <= cutoff:
                latest[r["store_id"]] = r
        snapshots = list(latest.values())
        if not snapshots or any(
            not number(r.get("inventory_level")) for r in snapshots
        ):
            return {
                "inventory": None,
                "availability": "UNAVAILABLE",
                "stockout_days": None,
            }
        conflict = any(
            as_date(r.get("inventory_timestamp")) != as_date(r["date"])
            for r in snapshots
        )
        ages = [(cutoff - as_date(r["date"])).days for r in snapshots]
        return {
            "inventory": sum(r["inventory_level"] for r in snapshots),
            "as_of": str(cutoff),
            "snapshot_dates": sorted({str(r["date"]) for r in snapshots}),
            "freshness": "CONFLICT"
            if conflict
            else "STALE"
            if max(ages) > 14
            else "FRESH",
            "availability": "PARTIAL"
            if conflict or min(ages) != max(ages)
            else "AVAILABLE",
            "stockout_snapshots": sum(r["inventory_level"] <= 0 for r in snapshots),
            "stockout_days": None,
            "definition": "Latest known balance per store at/before cutoff; snapshots do not measure stockout days.",
        }

    @staticmethod
    def revenue(rows, convention="net"):
        currencies = {r.get("currency") for r in rows}
        gross_valid = all(
            number(r.get("units_sold")) and number(r.get("price")) and r["price"] >= 0
            for r in rows
        )
        valid = (
            gross_valid
            and len(currencies) == 1
            and None not in currencies
            and all(
                number(r.get("discount"))
                and 0 <= r["discount"] <= 100
                and r.get("discount_unit") == "percent"
                for r in rows
            )
        )
        gross = (
            sum(r["units_sold"] * r["price"] for r in rows)
            if gross_valid and len(currencies) == 1
            else None
        )
        net = (
            sum(r["units_sold"] * r["price"] * (1 - r["discount"] / 100) for r in rows)
            if valid
            else None
        )
        exposure = (
            sum(
                (r["demand_forecast"] - r["units_sold"])
                * r["price"]
                * (1 - r["discount"] / 100)
                for r in rows
            )
            if valid and all(number(r.get("demand_forecast")) for r in rows)
            else None
        )
        return {
            "gross_revenue": rounded(gross),
            "net_revenue": rounded(net),
            "unit_price": rows[0]["price"]
            if gross_valid and len({r["price"] for r in rows}) == 1
            else None,
            "primary_revenue": rounded(gross if convention == "gross" else net),
            "revenue_type": convention,
            "currency": next(iter(currencies)) if len(currencies) == 1 else None,
            "forecast_revenue_exposure": rounded(exposure),
            "exposure_definition": "Signed forecast-minus-actual units at observed net unit prices; not a causal loss estimate.",
            "availability": "AVAILABLE" if valid else "PARTIAL",
            "definition": "gross=units*unit_price; net=gross*(1-discount/100). Missing/invalid net never falls back to gross.",
        }

    @staticmethod
    def patterns(points):
        if len(points) < 8:
            return {
                "status": "NOT_TESTABLE",
                "reason": "At least 8 complete weekly observations are required.",
            }
        values = [p["actual"] for p in points]
        half = len(points) // 2
        early, recent = mean(values[:half]), mean(values[half:])
        shift = change(early, recent)
        biases = [p["forecast"] - p["actual"] for p in points]
        weekly_errors = [
            abs(p["forecast"] - p["actual"]) / abs(p["actual"]) * 100
            if p["actual"]
            else None
            for p in points
        ]
        nonzero = [v for v in values if v != 0]
        avg = mean(values)
        return {
            "status": "AVAILABLE",
            "level_shift_pct": rounded(shift),
            "trend": "up"
            if shift is not None and shift > 15
            else "down"
            if shift is not None and shift < -15
            else "stable",
            "volatility_cv": rounded(statistics.pstdev(values) / abs(avg))
            if avg
            else None,
            "bias_drift_units": rounded(mean(biases[half:]) - mean(biases[:half])),
            "accuracy_deterioration_pp": rounded(
                (mean(weekly_errors[half:]) or 0) - (mean(weekly_errors[:half]) or 0)
            ),
            "divergence_units": rounded(mean([abs(b) for b in biases])),
            "spike_or_drop": any(
                abs(v - (early or 0)) > max(abs(early or 0) * 0.5, 1)
                for v in values[half:]
            ),
            "intermittency_ratio": rounded(1 - len(nonzero) / len(values)),
        }

    def hypothesis(self, kind, rows, points, plan, source, gaps, partial):
        result = {
            "cause": kind,
            "status": "NOT_TESTABLE",
            "strength": "LOW",
            "evidence": {},
            "reason": "Required fields, coverage or certification are unavailable.",
        }
        ready = self.readiness(plan, kind, source)
        result["readiness"] = ready
        if ready in ("BLOCKED", "STALE"):
            result["reason"] = (
                f"Capability certification is {ready}; maintenance is required."
            )
            return result
        if (
            ready not in ("READY", "PARTIAL")
            or gaps
            or len(points) < MIN_WEEKS[kind]
            or not rows
        ):
            return result
        if partial and kind != "quality":
            result["reason"] = (
                "Incomplete paired observations prevent a reliable contributor assessment."
            )
            return result
        metric, supported, possible = None, False, False
        if kind == "bias":
            metric = self.forecast(rows)["bias_pct"]
            supported = metric is not None and abs(metric) > 10
        elif kind == "trend":
            metric = self.patterns(points).get("level_shift_pct")
            supported = metric is not None and abs(metric) > 15
        elif kind == "promotion":
            if any(r.get("holiday_promotion") is None for r in rows):
                return result
            promo = mean([r["units_sold"] for r in rows if r["holiday_promotion"] > 0])
            normal = mean(
                [r["units_sold"] for r in rows if r["holiday_promotion"] == 0]
            )
            metric = change(normal, promo)
            if metric is None:
                return result
            supported = abs(metric) > 10
        elif kind == "inventory":
            if any(not number(r.get("inventory_level")) for r in rows):
                return result
            constrained = [r for r in rows if r["inventory_level"] <= 0]
            normal = [r for r in rows if r["inventory_level"] > 0]
            metric = {
                "stockout_snapshots": len(constrained),
                "sales_change_pct": rounded(
                    change(
                        mean([r["units_sold"] for r in normal]),
                        mean([r["units_sold"] for r in constrained]),
                    )
                ),
            }
            supported = (
                bool(constrained)
                and metric["sales_change_pct"] is not None
                and metric["sales_change_pct"] < 0
            )
        elif kind == "price":
            prices = [r.get("price") for r in rows]
            if not all(number(v) and v > 0 for v in prices):
                return result
            metric = change(min(prices), max(prices))
            possible = metric is not None and metric > 10
        elif kind == "revenue":
            half = len(rows) // 2
            a, b = self.revenue(rows[:half]), self.revenue(rows[half:])
            metric = change(a["net_revenue"], b["net_revenue"])
            if metric is None:
                return result
            supported = metric < -10
        elif kind == "seasonality":
            if not all(r.get("seasonality") == "synthetic_26_week" for r in rows):
                result["reason"] = (
                    "A validated seasonal cadence and at least two cycles are required."
                )
                return result
            # Two recurrences of a documented 26-week synthetic cycle.
            values = [p["actual"] for p in points]
            a, b = values[:-26], values[26:]
            if len(a) < 26 or not statistics.pstdev(a) or not statistics.pstdev(b):
                return result
            metric = statistics.correlation(a, b)
            supported = metric > 0.7
        elif kind == "competitor":
            if any(
                not number(r.get("competitor_pricing"))
                or r["competitor_pricing"] <= 0
                or not number(r.get("price"))
                for r in rows
            ):
                return result
            cheaper = [
                r["units_sold"] for r in rows if r["competitor_pricing"] < r["price"]
            ]
            other = [
                r["units_sold"] for r in rows if r["competitor_pricing"] >= r["price"]
            ]
            if min(len(cheaper), len(other)) < 4:
                return result
            metric = {
                "sales_change_when_competitor_cheaper_pct": rounded(
                    change(mean(other), mean(cheaper))
                )
            }
            possible = (
                metric["sales_change_when_competitor_cheaper_pct"] is not None
                and abs(metric["sales_change_when_competitor_cheaper_pct"]) > 10
            )
        elif kind == "weather":
            groups = defaultdict(list)
            for row in rows:
                if not row.get("weather_condition") or as_date(
                    row.get("weather_observed_at")
                ) != as_date(row["date"]):
                    return result
                groups[row["weather_condition"]].append(row["units_sold"])
            if len(groups) < 2 or any(len(values) < 4 for values in groups.values()):
                return result
            averages = {key: mean(values) for key, values in groups.items()}
            maximum = max(averages.values())
            metric = {
                "average_sales_by_observed_weather": {
                    key: rounded(value) for key, value in averages.items()
                },
                "spread_pct": rounded(
                    (maximum - min(averages.values())) / maximum * 100
                )
                if maximum
                else None,
            }
            possible = metric["spread_pct"] is not None and metric["spread_pct"] > 10
        elif kind == "lifecycle":
            launches = {r.get("launch_date") for r in rows}
            if len(launches) != 1 or None in launches:
                return result
            launch = as_date(next(iter(launches)))
            if any(as_date(r["date"]) < launch for r in rows):
                return result
            age = (max(as_date(r["date"]) for r in rows) - launch).days
            metric = {
                "age_days": age,
                "launch_date": str(launch),
                "sales_level_shift_pct": self.patterns(points).get("level_shift_pct"),
            }
            possible = (
                age <= 90
                and metric["sales_level_shift_pct"] is not None
                and abs(metric["sales_level_shift_pct"]) > 15
            )
        elif kind == "mix":
            stores = {r["store_id"] for r in rows}
            if len(stores) < 2:
                return result
            dates = sorted({as_date(r["date"]) for r in rows})
            middle = dates[len(dates) // 2]
            totals = []
            for is_recent in (False, True):
                counts = {
                    store: sum(
                        r["units_sold"]
                        for r in rows
                        if r["store_id"] == store
                        and ((as_date(r["date"]) >= middle) == is_recent)
                    )
                    for store in stores
                }
                total = sum(counts.values())
                if total <= 0 or any(value < 0 for value in counts.values()):
                    return result
                totals.append({key: value / total for key, value in counts.items()})
            shifts = {
                key: rounded((totals[1][key] - totals[0][key]) * 100)
                for key in sorted(stores)
            }
            variation = sum(abs(totals[1][key] - totals[0][key]) for key in stores) / 2
            metric = {
                "store_share_changes_pp": shifts,
                "total_variation": rounded(variation),
            }
            possible = variation > 0.2
        elif kind == "quality":
            metric = {"partial": partial}
            supported = partial
        else:
            result["reason"] = (
                "This contributor has no validated detection contract; no causal inference is made."
            )
            return result
        result.update(
            status="SUPPORTED"
            if supported
            else "POSSIBLE"
            if possible
            else "NOT_SUPPORTED",
            strength="MEDIUM" if supported else "LOW",
            evidence={"metric": rounded(metric) if number(metric) else metric},
            reason="Deterministic association within this scope; not a causal claim.",
        )
        return result
