"""Small, explicit contracts shared by notebooks, the CLI and channel adapters."""

from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Principal(BaseModel):
    """Created by a trusted host after authentication, never from chat text.

    Empty entitlements deny access. Use '*' only for a reviewed global grant.
    Tenant and subject together own state; a conversation ID is not an owner.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    tenant: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=200)
    regions: tuple[str, ...] = ()
    products: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()

    @property
    def owner(self):
        # JSON prevents two different tenant/subject pairs producing the same key.
        import json

        return json.dumps([self.tenant, self.subject], separators=(",", ":"))

    def authorize(self, product, region, category):
        for value, grants in [
            (product, self.products),
            (region, self.regions),
            (category, self.categories),
        ]:
            if "*" not in grants and value not in grants:
                raise PermissionError("The requested business scope is not authorized.")


class TurnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    request_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    message: str = Field(min_length=1, max_length=2000)
    expected_version: int | None = Field(default=None, ge=0)
    case_id: str | None = Field(default=None, max_length=100)
    channel: Literal["development", "teams"] = "development"


class AnalysisPlan(BaseModel):
    """Only these tools and parameters can reach the deterministic backend."""

    model_config = ConfigDict(extra="forbid")
    tool: Literal[
        "get_forecast_context",
        "get_inventory_context",
        "get_revenue_context",
        "analyze_historical_pattern",
        "run_forecast_rca",
        "compare_scenarios",
    ]
    product_id: str = Field(min_length=1, max_length=80)
    region: str = Field(min_length=1, max_length=80)
    store_id: str | None = Field(default=None, max_length=80)
    category: str | None = Field(default=None, max_length=80)
    channel: str | None = Field(default=None, min_length=1, max_length=40)
    fiscal_period: str | None = Field(
        default=None, pattern=r"^FY\d{4}-P(?:0[1-9]|1[0-2])$"
    )
    comparison_region: str | None = Field(default=None, min_length=1, max_length=80)
    comparison_start: date | None = None
    comparison_end: date | None = None
    start: date | None = None
    end: date | None = None
    as_of: date | None = None
    lookback_weeks: int = Field(default=12, ge=1, le=104)
    lookback_months: int | None = Field(default=None, ge=1, le=24)
    relative_period: Literal["this_month", "previous_month"] | None = None
    compare_previous_period: bool = False
    vintage: date | None = None
    revenue_type: Literal["gross", "net", "both"] = "net"
    hypotheses: list[
        Literal[
            "bias",
            "trend",
            "promotion",
            "inventory",
            "price",
            "seasonality",
            "competitor",
            "weather",
            "revenue",
            "lifecycle",
            "mix",
            "quality",
        ]
    ] = Field(default_factory=list, max_length=12)
    include_summary: bool = True
    include_history: bool = False
    include_accuracy: bool = True
    include_bias: bool = True
    include_trend: bool = False

    @model_validator(mode="after")
    def valid_period(self):
        if self.product_id == "*" and (not self.category or self.category == "*"):
            raise ValueError("Aggregate product scope requires one concrete category.")
        if self.product_id == "*" and self.tool in (
            "run_forecast_rca",
            "compare_scenarios",
        ):
            raise ValueError(
                "Aggregate scope supports retrieval and historical patterns only."
            )
        selectors = sum(
            bool(value)
            for value in (
                self.start,
                self.fiscal_period,
                self.lookback_months,
                self.relative_period,
                self.as_of,
            )
        )
        if selectors > 1:
            raise ValueError(
                "Choose one period selector: explicit dates, fiscal period, month lookback, relative month or as-of."
            )
        if self.compare_previous_period and self.comparison_start:
            raise ValueError(
                "Choose either an explicit comparison period or the previous period."
            )
        if bool(self.comparison_start) != bool(self.comparison_end):
            raise ValueError("Provide both comparison dates.")
        if self.comparison_start and (
            self.comparison_start > self.comparison_end
            or (self.comparison_end - self.comparison_start).days > 728
        ):
            raise ValueError(
                "Comparison periods must be ordered and at most 104 weeks."
            )
        if bool(self.start) != bool(self.end):
            raise ValueError("Provide both start and end dates.")
        if self.start and (self.start > self.end or (self.end - self.start).days > 728):
            raise ValueError("Date windows must be ordered and at most 104 weeks.")
        return self
