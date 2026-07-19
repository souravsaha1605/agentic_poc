from typing import Optional, List
from pydantic import BaseModel, Field


# ==========================================================
# User Query
# ==========================================================

class UserQuery(BaseModel):
    query: str = Field(
        description="Natural language question from the user."
    )


# ==========================================================
# Tool Request Models
# ==========================================================

class ForecastRequest(BaseModel):
    product_id: str = Field(
        description="Product ID."
    )
    store_id: Optional[str] = Field(
        default=None,
        description="Optional Store ID."
    )


class InventoryRequest(BaseModel):
    product_id: str = Field(
        description="Product ID."
    )
    store_id: Optional[str] = Field(
        default=None,
        description="Optional Store ID."
    )


class ForecastAccuracyRequest(BaseModel):
    product_id: str = Field(
        description="Product ID."
    )
    store_id: Optional[str] = Field(
        default=None,
        description="Optional Store ID."
    )


class ForecastBiasRequest(BaseModel):
    product_id: str = Field(
        description="Product ID."
    )
    store_id: Optional[str] = Field(
        default=None,
        description="Optional Store ID."
    )


class RegionComparisonRequest(BaseModel):
    region_1: str = Field(
        description="First region."
    )
    region_2: str = Field(
        description="Second region."
    )


# ==========================================================
# Service Response Models
# ==========================================================

class ForecastSummary(BaseModel):
    average_forecast: float
    average_actual_sales: float
    forecast_accuracy: float
    forecast_bias: float


class InventorySummary(BaseModel):
    inventory_level: float
    inventory_status: str


class BusinessContext(BaseModel):
    forecast: ForecastSummary
    inventory: InventorySummary


class RCAResult(BaseModel):
    observations: List[str]
    probable_causes: List[str]
    recommendations: List[str]
    confidence: str


class AgentResponse(BaseModel):
    response: str