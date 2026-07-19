from models import (
    ForecastRequest,
    InventoryRequest,
    ForecastAccuracyRequest,
    ForecastBiasRequest,
    RegionComparisonRequest
)

from tools.supply_chain_tools import (
    get_forecast_summary,
    get_forecast_context,
    get_inventory_status,
    calculate_forecast_accuracy,
    calculate_forecast_bias,
    compare_regions,
    get_trend_summary
)


class ToolExecutor:

    def __init__(self):

        self.tool_mapping = {

            "get_forecast_summary": (
                get_forecast_summary,
                ForecastRequest
            ),

            "get_forecast_context": (
                get_forecast_context,
                ForecastRequest
            ),

            "get_inventory_status": (
                get_inventory_status,
                InventoryRequest
            ),

            "calculate_forecast_accuracy": (
                calculate_forecast_accuracy,
                ForecastAccuracyRequest
            ),

            "calculate_forecast_bias": (
                calculate_forecast_bias,
                ForecastBiasRequest
            ),

            "compare_regions": (
                compare_regions,
                RegionComparisonRequest
            ),

            "get_trend_summary": (
                get_trend_summary,
                ForecastRequest
            )

        }

    def execute(
        self,
        tool_name: str,
        arguments: dict
    ):

        if tool_name not in self.tool_mapping:

            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        tool_function, request_model = self.tool_mapping[tool_name]

        request = request_model(**arguments)

        return tool_function(request)