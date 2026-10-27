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
INVENTORY_HISTORY_FRESH_DAYS = 14
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


class NoDataError(ValueError):
    """The requested scope has no observations; integrity errors use ValueError."""


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


def shift_months(day, months):
    """Shift a date by whole calendar months, clamping to month end."""
    import calendar

    index = day.year * 12 + day.month - 1 + months
    year, month_index = divmod(index, 12)
    month = month_index + 1
    return day.replace(
        year=year, month=month, day=min(day.day, calendar.monthrange(year, month)[1])
    )


def weekly(rows, start=None, end=None):
    groups = defaultdict(list)
    for r in rows:
        d = as_date(r["date"])
        groups[d - timedelta(days=d.weekday())].append(r)
    points = [
        {
            "date": str(d),
            "actual": sum(r["units_sold"] for r in batch),
            "forecast": sum(r["demand_forecast"] for r in batch),
        }
        for d, batch in sorted(groups.items())
    ]
    if start is not None:
        points = [point for point in points if as_date(point["date"]) >= start]
    if end is not None:
        points = [
            point
            for point in points
            if as_date(point["date"]) + timedelta(days=6) <= end
        ]
    return points


class BusinessService:
    def __init__(self, provider, today=None):
        self.provider = provider
        self.today = today or date.today()

    def prepare(self, plan, principal):
        # A host grant is checked even if the model proposes a different product.
        principal.authorize(plan.product_id, plan.region, plan.category)
        rows = self.provider.fetch(plan)
        if not rows:
            raise NoDataError("No data is available for this entity and period.")
        for r in rows:
            principal.authorize(r["product_id"], r["region"], r["category"])
        if plan.product_id == "*":
            units = {r.get("unit_of_measure") for r in rows}
            if None in units or "" in units or len(units) != 1:
                raise ValueError(
                    "Aggregate scope requires one certified unit of measure."
                )
        dates = [as_date(r["date"]) for r in rows]
        end = plan.end or plan.as_of or min(max(dates), self.today)
        if plan.start:
            start = plan.start
        elif plan.relative_period == "this_month":
            start = end.replace(day=1)
        elif plan.relative_period == "previous_month":
            end = end.replace(day=1) - timedelta(days=1)
            start = end.replace(day=1)
        elif plan.lookback_months:
            start = shift_months(end, -plan.lookback_months) + timedelta(days=1)
        else:
            start = end - timedelta(weeks=plan.lookback_weeks) + timedelta(days=1)
        # Inventory as-of must search all prior snapshots, including an old one.
        scoped = [
            r
            for r in rows
            if as_date(r["date"]) <= end
            and (plan.tool == "get_inventory_context" or as_date(r["date"]) >= start)
        ]
        if not scoped:
            raise NoDataError("No observations at or before the requested cutoff.")
        limitations = []
        # Choose one forecast per target/store. Never duplicate an actual across vintages.
        by_target = defaultdict(list)
        for r in scoped:
            by_target[(r["product_id"], str(r["date"]), r["store_id"])].append(r)
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
        points = weekly(valid, start, end)
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
        if plan.product_id == "*":
            base["aggregation"] = {
                "included_products": sorted({r["product_id"] for r in selected}),
                "unit_of_measure": next(iter({r["unit_of_measure"] for r in selected})),
                "definition": "Sum across the listed products only after source certification confirms one homogeneous unit of measure.",
            }
        if plan.tool == "get_inventory_context":
            cutoff = as_date(source["requested_end"])
            period_start = as_date(source["requested_start"])
            base.update(self.inventory(selected, cutoff))
            base["inventory_trend"] = self.inventory_trend(
                selected, period_start, cutoff
            )
            base["forecast_error_inventory_exposure"] = self.inventory_exposure(
                [row for row in rows if period_start <= as_date(row["date"]) <= cutoff]
            )
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
        comparison_start = plan.comparison_start
        comparison_end = plan.comparison_end
        if plan.compare_previous_period and not comparison_start:
            current_start = as_date(source["requested_start"])
            current_end = as_date(source["requested_end"])
            comparison_end = current_start - timedelta(days=1)
            if plan.lookback_months:
                comparison_start = shift_months(
                    comparison_end, -plan.lookback_months
                ) + timedelta(days=1)
            elif plan.relative_period:
                comparison_start = comparison_end.replace(day=1)
            else:
                days = (current_end - current_start).days + 1
                comparison_start = comparison_end - timedelta(days=days - 1)
        if plan.comparison_region or comparison_start:
            # Explicit comparison scopes are independently authorized. Recursive
            # requests clear comparison fields, so this is at most two bounded
            # additional deterministic reads, never a model/tool loop.
            comparisons = {}
            for label, updates in [
                ("region", {"region": plan.comparison_region}),
                (
                    "period",
                    {
                        "start": comparison_start,
                        "end": comparison_end,
                        "as_of": None,
                        "fiscal_period": None,
                    },
                ),
            ]:
                if label == "region" and not plan.comparison_region:
                    continue
                if label == "period" and not comparison_start:
                    continue
                other = plan.model_copy(
                    update={
                        **updates,
                        "comparison_region": None,
                        "comparison_start": None,
                        "comparison_end": None,
                        "compare_previous_period": False,
                        "relative_period": None,
                        "lookback_months": None,
                    }
                )
                try:
                    reference = self.execute(other, principal)
                except NoDataError:
                    comparisons[label] = {
                        "period": {
                            "start": str(comparison_start),
                            "end": str(comparison_end),
                        },
                        "availability": "UNAVAILABLE",
                        "limitation": "No validated observations exist for the comparison scope.",
                    }
                    continue
                comparisons[label] = {
                    "entity": reference["entity"],
                    "period": reference["period"],
                    "metrics": reference.get("metrics"),
                    "net_revenue": reference.get("net_revenue"),
                    "inventory": reference.get("inventory"),
                    "provenance": reference["provenance"],
                }
                comparisons[label]["deltas"] = self.comparison_deltas(base, reference)
                if "accuracy_gap_pp" in comparisons[label]["deltas"]:
                    comparisons[label]["accuracy_gap_pp"] = comparisons[label][
                        "deltas"
                    ]["accuracy_gap_pp"]
            base["comparisons"] = comparisons
        return base

    @staticmethod
    def comparison_deltas(current, reference):
        """Current minus reference, with unit and percentage-point conventions."""
        deltas = {
            "definition": "Current minus reference; percent changes divide by the absolute reference value; accuracy, WMAPE and bias use percentage points. Zero reference values have no percent change."
        }
        current_metrics = current.get("metrics") or {}
        reference_metrics = reference.get("metrics") or {}
        for name in ("actual", "forecast", "signed_error", "absolute_error"):
            current_value = current_metrics.get(name)
            reference_value = reference_metrics.get(name)
            if number(current_value) and number(reference_value):
                deltas[name + "_units"] = rounded(current_value - reference_value)
                deltas[name + "_pct"] = rounded(change(reference_value, current_value))
        for name, output in (
            ("wmape_pct", "wmape_gap_pp"),
            ("accuracy_pct", "accuracy_gap_pp"),
            ("bias_pct", "bias_gap_pp"),
        ):
            current_value = current_metrics.get(name)
            reference_value = reference_metrics.get(name)
            if number(current_value) and number(reference_value):
                deltas[output] = rounded(current_value - reference_value)
        for name, unit in (("net_revenue", "currency"), ("inventory", "units")):
            current_value = current.get(name)
            reference_value = reference.get(name)
            if number(current_value) and number(reference_value):
                deltas[name + "_change"] = rounded(current_value - reference_value)
                deltas[name + "_change_pct"] = rounded(
                    change(reference_value, current_value)
                )
                deltas[name + "_unit"] = unit
        return deltas

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
                latest[(r["product_id"], r["store_id"])] = r
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
    def inventory_trend(rows, start, end):
        """Historical balances carried forward for at most the freshness limit."""
        ordered = sorted(rows, key=lambda row: as_date(row["date"]))
        entities = sorted({(row["product_id"], row["store_id"]) for row in ordered})
        dates = sorted(
            {
                as_date(row["date"])
                for row in ordered
                if start <= as_date(row["date"]) <= end
            }
        )
        trend = []
        for day in dates:
            values = []
            stale = 0
            for entity in entities:
                candidates = [
                    row
                    for row in ordered
                    if (row["product_id"], row["store_id"]) == entity
                    and as_date(row["date"]) <= day
                    and number(row.get("inventory_level"))
                ]
                if not candidates:
                    continue
                latest = candidates[-1]
                if (day - as_date(latest["date"])).days > INVENTORY_HISTORY_FRESH_DAYS:
                    stale += 1
                    continue
                values.append(latest)
            available = len(values)
            expected = len(entities)
            trend.append(
                {
                    "date": str(day),
                    "inventory": rounded(sum(r["inventory_level"] for r in values))
                    if values
                    else None,
                    "stockout_snapshots": sum(
                        r["inventory_level"] <= 0 for r in values
                    ),
                    "available_entities": available,
                    "expected_entities": expected,
                    "stale_entities": stale,
                    "availability": "AVAILABLE"
                    if available == expected
                    else "PARTIAL"
                    if available
                    else "UNAVAILABLE",
                }
            )
        complete = [point for point in trend if point["inventory"] is not None]
        return {
            "points": trend,
            "change_pct": rounded(change(trend[0]["inventory"], trend[-1]["inventory"]))
            if len(trend) >= 2
            and trend[0]["inventory"] is not None
            and trend[-1]["inventory"] is not None
            else None,
            "availability": "AVAILABLE"
            if trend
            and len(complete) == len(trend)
            and all(p["availability"] == "AVAILABLE" for p in trend)
            else "PARTIAL"
            if complete
            else "UNAVAILABLE",
            "freshness_limit_days": INVENTORY_HISTORY_FRESH_DAYS,
            "definition": "At each observation date, sum the latest product/store balance no more than 14 days old. Dates are never added together; missing or stale entities make that point partial.",
        }

    @staticmethod
    def inventory_exposure(rows):
        """Describe forecast error observed alongside available or zero inventory."""
        usable = [r for r in rows if number(r.get("inventory_level"))]
        missing = len(rows) - len(usable)
        if not usable:
            return {
                "availability": "UNAVAILABLE",
                "usable_observations": 0,
                "missing_observations": missing,
                "absolute_error_units_at_stockout": None,
                "signed_error_units_at_stockout": None,
                "absolute_error_units_with_inventory": None,
                "stockout_snapshots": None,
                "definition": "Inventory evidence is unavailable; forecast-error exposure cannot be calculated.",
            }
        low = [r for r in usable if r["inventory_level"] <= 0]
        available = [r for r in usable if r["inventory_level"] > 0]

        def absolute_error(batch):
            return sum(abs(r["demand_forecast"] - r["units_sold"]) for r in batch)

        return {
            "availability": "PARTIAL" if missing else "AVAILABLE",
            "usable_observations": len(usable),
            "missing_observations": missing,
            "absolute_error_units_at_stockout": rounded(absolute_error(low)),
            "signed_error_units_at_stockout": rounded(
                sum(r["demand_forecast"] - r["units_sold"] for r in low)
            ),
            "absolute_error_units_with_inventory": rounded(absolute_error(available)),
            "stockout_snapshots": len(low),
            "definition": "Forecast-minus-actual error grouped by contemporaneous inventory snapshot; association only, not lost demand or causality.",
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
        rolling = []
        for index in range(3, len(points)):
            window = points[index - 3 : index + 1]
            if any(
                (as_date(right["date"]) - as_date(left["date"])).days != 7
                for left, right in zip(window, window[1:])
            ):
                continue
            actual = mean([point["actual"] for point in window])
            forecast = mean([point["forecast"] for point in window])
            denominator = sum(abs(point["actual"]) for point in window)
            wmape = (
                sum(abs(point["forecast"] - point["actual"]) for point in window)
                / denominator
                * 100
                if denominator
                else None
            )
            rolling.append(
                {
                    "week": points[index]["date"],
                    "window_start": window[0]["date"],
                    "actual_4w_avg": rounded(actual),
                    "forecast_4w_avg": rounded(forecast),
                    "accuracy_4w_pct": rounded(100 - wmape)
                    if wmape is not None
                    else None,
                }
            )
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
            "rolling_4_week": rolling[-12:],
            "rolling_definition": "Four consecutive completed weekly aggregates ending on each listed week; accuracy is 100 minus four-week WMAPE. Windows spanning missing weeks are omitted.",
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
