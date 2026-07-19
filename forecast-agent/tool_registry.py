from models import (
    ForecastRequest,
    InventoryRequest,
    ForecastAccuracyRequest,
    ForecastBiasRequest,
    RegionComparisonRequest
)

TOOLS = [

    # ==========================================================
    # Forecast Summary
    # ==========================================================
    {
        "type": "function",
        "name": "get_forecast_summary",
        "description": (
            "Retrieve forecast summary including average forecast "
            "and average actual sales for a product."
        ),
        "parameters": ForecastRequest.model_json_schema()
    },

    # ==========================================================
    # Forecast Context
    # ==========================================================
    {
        "type": "function",
        "name": "get_forecast_context",
        "description": (
            "Retrieve complete business context for a product. "
            "Use this for RCA, executive summaries and business recommendations."
        ),
        "parameters": ForecastRequest.model_json_schema()
    },

    # ==========================================================
    # Inventory
    # ==========================================================
    {
        "type": "function",
        "name": "get_inventory_status",
        "description": (
            "Retrieve the latest inventory level and inventory status."
        ),
        "parameters": InventoryRequest.model_json_schema()
    },

    # ==========================================================
    # Forecast Accuracy
    # ==========================================================
    {
        "type": "function",
        "name": "calculate_forecast_accuracy",
        "description": (
            "Calculate forecast accuracy for a product."
        ),
        "parameters": ForecastAccuracyRequest.model_json_schema()
    },

    # ==========================================================
    # Forecast Bias
    # ==========================================================
    {
        "type": "function",
        "name": "calculate_forecast_bias",
        "description": (
            "Calculate forecast bias for a product."
        ),
        "parameters": ForecastBiasRequest.model_json_schema()
    },

    # ==========================================================
    # Region Comparison
    # ==========================================================
    {
        "type": "function",
        "name": "compare_regions",
        "description": (
            "Compare forecast performance between two regions."
        ),
        "parameters": RegionComparisonRequest.model_json_schema()
    },

    # ==========================================================
    # Trend Summary
    # ==========================================================
    {
        "type": "function",
        "name": "get_trend_summary",
        "description": (
            "Retrieve recent sales and forecast trend for a product."
        ),
        "parameters": ForecastRequest.model_json_schema()
    }

]