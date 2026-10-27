"""
tool_executor.py
================
Maps LLM tool-call names to Python functions and executes them.

PURPOSE
-------
When the LLM returns a `function_call` item, the agent extracts the tool
name and JSON arguments.  The ToolExecutor:
  1. Looks up the tool name in its mapping table
  2. Validates the arguments against the corresponding Pydantic model
  3. Calls the tool function with the validated request
  4. Returns the result (dict or list) to the agent

ARCHITECTURE ROLE
-----------------
  agent  -->  tool_executor.execute("get_inventory", {"sku_id": "SKU-001"})
                     |
                     +--> InventoryRequest(sku_id="SKU-001")  # Pydantic validation
                     +--> tools.exception_tools.get_inventory(request)
                     +--> services.ExceptionService.get_inventory(...)
                     +--> returns [{"warehouse_id": "WH01", ...}, ...]

WHY A MAPPING TABLE?
-------------------
  • The LLM can only call tools that are in the mapping — this prevents
    arbitrary function execution (security guardrail, BRD §26).
  • Each entry maps a string name to (function, pydantic_model) so
    arguments are always validated before execution.
  • Adding a new tool requires one line in the mapping and one entry in
    tool_registry.py — no other code changes.
"""

from models import (
    InventoryRequest, PurchaseOrderRequest, CustomerOrderRequest,
    SupplierRequest, AlternateSupplierRequest, DemandForecastRequest,
    ShipmentRequest, WarehouseInventoryRequest, ExceptionRequest,
    ExceptionListRequest, SupplierEventRequest
)

from tools.exception_tools import (
    get_inventory,
    get_warehouse_inventory,
    get_open_purchase_orders,
    get_customer_orders,
    get_supplier_performance,
    get_alternate_suppliers,
    get_supplier_events,
    get_demand_forecast,
    get_shipments,
    get_exception_details,
    list_exceptions
)


class ToolExecutor:
    """
    Routes LLM tool calls to the appropriate Python function.

    Each entry in self.tool_mapping is:
        "tool_name": (callable_function, PydanticRequestModel)

    The PydanticRequestModel is used to validate the JSON arguments that
    the LLM provides.  If validation fails, a ValidationError is raised
    (caught by the agent, which then reports the error to the LLM).
    """

    def __init__(self):
        self.tool_mapping = {

            # --- Inventory ---
            "get_inventory": (
                get_inventory,
                InventoryRequest
            ),
            "get_warehouse_inventory": (
                get_warehouse_inventory,
                WarehouseInventoryRequest
            ),

            # --- Purchase Orders ---
            "get_open_purchase_orders": (
                get_open_purchase_orders,
                PurchaseOrderRequest
            ),

            # --- Customer Orders ---
            "get_customer_orders": (
                get_customer_orders,
                CustomerOrderRequest
            ),

            # --- Suppliers ---
            "get_supplier_performance": (
                get_supplier_performance,
                SupplierRequest
            ),
            "get_alternate_suppliers": (
                get_alternate_suppliers,
                AlternateSupplierRequest
            ),
            "get_supplier_events": (
                get_supplier_events,
                SupplierEventRequest
            ),

            # --- Demand Forecast ---
            "get_demand_forecast": (
                get_demand_forecast,
                DemandForecastRequest
            ),

            # --- Shipments ---
            "get_shipments": (
                get_shipments,
                ShipmentRequest
            ),

            # --- Exceptions ---
            "get_exception_details": (
                get_exception_details,
                ExceptionRequest
            ),
            "list_exceptions": (
                list_exceptions,
                ExceptionListRequest
            ),
        }

    def execute(self, tool_name: str, arguments: dict):
        """
        Execute a tool by name with the given arguments.

        Parameters:
            tool_name : str  – must be a key in self.tool_mapping
            arguments : dict – raw JSON from the LLM's function_call

        Returns:
            dict or list – the tool's output (JSON-serialisable)

        Raises:
            ValueError – if tool_name is not in the mapping
            pydantic.ValidationError – if arguments don't match the schema
        """
        if tool_name not in self.tool_mapping:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool_function, request_model = self.tool_mapping[tool_name]

        # Validate arguments against the Pydantic model before calling
        request = request_model(**arguments)

        return tool_function(request)