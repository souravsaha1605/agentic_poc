from models import (
    ForecastRequest,
    InventoryRequest,
    ForecastAccuracyRequest,
    ForecastBiasRequest,
    RegionComparisonRequest
)

from services.supply_chain_service import SupplyChainService


# Single service instance
service = SupplyChainService()


# ==========================================================
# Forecast
# ==========================================================

def get_forecast_summary(request: ForecastRequest):
    """
    Returns forecast summary for a product.
    """
    return service.get_forecast_summary(
        product_id=request.product_id,
        store_id=request.store_id
    )


def get_forecast_context(request: ForecastRequest):
    """
    Returns combined business context.
    Used for RCA and Executive Summary.
    """
    return service.get_forecast_context(
        product_id=request.product_id,
        store_id=request.store_id
    )


# ==========================================================
# Inventory
# ==========================================================

def get_inventory_status(request: InventoryRequest):
    """
    Returns latest inventory status.
    """
    return service.get_inventory_summary(
        product_id=request.product_id,
        store_id=request.store_id
    )


# ==========================================================
# Forecast Metrics
# ==========================================================

def calculate_forecast_accuracy(
    request: ForecastAccuracyRequest
):
    """
    Returns forecast accuracy.
    """
    return service.calculate_forecast_accuracy(
        product_id=request.product_id,
        store_id=request.store_id
    )


def calculate_forecast_bias(
    request: ForecastBiasRequest
):
    """
    Returns forecast bias.
    """
    return service.calculate_forecast_bias(
        product_id=request.product_id,
        store_id=request.store_id
    )


# ==========================================================
# Comparison
# ==========================================================

def compare_regions(
    request: RegionComparisonRequest
):
    """
    Compares forecast metrics between two regions.
    """
    return service.compare_regions(
        region_1=request.region_1,
        region_2=request.region_2
    )


# ==========================================================
# Trend Analysis
# ==========================================================

def get_trend_summary(
    request: ForecastRequest
):
    """
    Returns recent sales and forecast trend.
    """
    return service.get_trend_summary(
        product_id=request.product_id,
        store_id=request.store_id
    )