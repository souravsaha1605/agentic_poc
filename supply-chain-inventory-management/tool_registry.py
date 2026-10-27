"""
tool_registry.py
================
Defines the tool schemas that the LLM sees and can call.

PURPOSE
-------
This file produces the `TOOLS` list — a JSON-array of function definitions
that is passed to the OpenAI Responses API as the `tools` parameter.  Each
tool definition includes:
  • type   – always "function"
  • name   – the function name (must match a key in tool_executor.py)
  • description – tells the LLM WHEN to use this tool
  • parameters  – a JSON Schema derived from the Pydantic request model

ARCHITECTURE ROLE
-----------------
  agent  -->  client.responses.create(tools=TOOLS)  -->  LLM
                                                           |
                                                           v
                                                   returns function_call
                                                           |
                                                           v
                                          tool_executor.execute(name, args)

WHY Pydantic model_json_schema()?
---------------------------------
  • The JSON Schema is generated from the same Pydantic models used by
    the tool executor, guaranteeing that the schema the LLM sees matches
    the schema the executor validates against.
  • No manual schema maintenance — changing the model auto-updates the
    tool definition.

BRD REFERENCE
-------------
  §21 (Tool Layer) — required tool categories:
    Inventory, Purchase Orders, Suppliers, Orders, Logistics,
    Procurement, Notifications.  This registry covers the first five;
  Procurement and Notifications are simulated (no write operations in POC).
"""

from models import (
    InventoryRequest, PurchaseOrderRequest, CustomerOrderRequest,
    SupplierRequest, AlternateSupplierRequest, DemandForecastRequest,
    ShipmentRequest, WarehouseInventoryRequest, ExceptionRequest,
    ExceptionListRequest, SupplierEventRequest
)

TOOLS = [

    # =======================================================================
    # INVENTORY TOOLS  (BRD §21 — Inventory category)
    # =======================================================================
    {
        "type": "function",
        "name": "get_inventory",
        "description": (
            "Retrieve current inventory position for a SKU. "
            "Returns on_hand, allocated, available, in_transit, and safety_stock "
            "for each warehouse that stocks the SKU. "
            "Optionally filter to a single warehouse."
        ),
        "parameters": InventoryRequest.model_json_schema()
    },
    {
        "type": "function",
        "name": "get_warehouse_inventory",
        "description": (
            "Retrieve inventory for a SKU across ALL warehouses. "
            "Use this to detect warehouse imbalances — when one warehouse "
            "has excess stock while another is running low."
        ),
        "parameters": WarehouseInventoryRequest.model_json_schema()
    },

    # =======================================================================
    # PURCHASE ORDER TOOLS  (BRD §21 — Purchase Orders category)
    # =======================================================================
    {
        "type": "function",
        "name": "get_open_purchase_orders",
        "description": (
            "Retrieve all purchase order lines for a SKU, including the PO "
            "header (supplier, status, expected delivery, actual delivery). "
            "Use this to check pending deliveries and identify delayed POs."
        ),
        "parameters": PurchaseOrderRequest.model_json_schema()
    },

    # =======================================================================
    # CUSTOMER ORDER TOOLS  (BRD §21 — Orders category)
    # =======================================================================
    {
        "type": "function",
        "name": "get_customer_orders",
        "description": (
            "Retrieve all customer orders dependent on a SKU. "
            "Includes priority, quantity, requested delivery date, and status. "
            "Use this to assess customer impact from supply disruptions."
        ),
        "parameters": CustomerOrderRequest.model_json_schema()
    },

    # =======================================================================
    # SUPPLIER TOOLS  (BRD §21 — Suppliers category)
    # =======================================================================
    {
        "type": "function",
        "name": "get_supplier_performance",
        "description": (
            "Retrieve supplier master record and performance metrics: "
            "reliability score, lead time, capacity, approved status. "
            "Use this to evaluate a supplier before recommending expedite or "
            "alternate sourcing."
        ),
        "parameters": SupplierRequest.model_json_schema()
    },
    {
        "type": "function",
        "name": "get_alternate_suppliers",
        "description": (
            "Find all alternate approved suppliers that could fulfill a SKU. "
            "Returns supplier name, country, lead time, reliability, capacity, "
            "and unit cost. Use this to generate an alternate-sourcing "
            "resolution option."
        ),
        "parameters": AlternateSupplierRequest.model_json_schema()
    },
    {
        "type": "function",
        "name": "get_supplier_events",
        "description": (
            "Retrieve supplier events (delivery delays, capacity constraints, "
            "quality issues, force majeure, price changes) for a supplier. "
            "Use this to understand the triggering event behind an exception."
        ),
        "parameters": SupplierEventRequest.model_json_schema()
    },

    # =======================================================================
    # DEMAND FORECAST TOOLS
    # =======================================================================
    {
        "type": "function",
        "name": "get_demand_forecast",
        "description": (
            "Retrieve demand forecast summary for a SKU over the 90-day "
            "horizon. Returns average forecast, average actual demand, max "
            "actual demand, and demand profile. Use this to project inventory "
            "depletion and detect demand spikes."
        ),
        "parameters": DemandForecastRequest.model_json_schema()
    },

    # =======================================================================
    # SHIPMENT TOOLS  (BRD §21 — Logistics category)
    # =======================================================================
    {
        "type": "function",
        "name": "get_shipments",
        "description": (
            "Retrieve shipment records for purchase orders containing a SKU. "
            "Includes origin, destination warehouse, carrier, status, ship "
            "date, expected and actual arrival. Use this to evaluate shipment "
            "delays and alternate transportation."
        ),
        "parameters": ShipmentRequest.model_json_schema()
    },

    # =======================================================================
    # EXCEPTION TOOLS
    # =======================================================================
    {
        "type": "function",
        "name": "get_exception_details",
        "description": (
            "Retrieve details of a specific supply chain exception by ID. "
            "Includes exception type, severity, status, description, and dates."
        ),
        "parameters": ExceptionRequest.model_json_schema()
    },
    {
        "type": "function",
        "name": "list_exceptions",
        "description": (
            "List all supply chain exceptions, optionally filtered by status "
            "(DETECTED, CLASSIFIED, INVESTIGATING, RESOLVED, AWAITING_APPROVAL). "
            "Use this when the user asks to see all open exceptions."
        ),
        "parameters": ExceptionListRequest.model_json_schema()
    },
]