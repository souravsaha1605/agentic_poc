"""
tools/exception_tools.py
=======================
Tool functions that the LLM agent can invoke.

PURPOSE
-------
Each function here is a thin wrapper around the ExceptionService.  The
function receives a Pydantic request model (validated by the
ToolExecutor), calls the corresponding service method, and returns the
result as a JSON-serialisable dict or list.

ARCHITECTURE ROLE
-----------------
  LLM  ->  tool_executor  ->  **THIS FILE**  ->  ExceptionService  ->  Spark

These functions are intentionally lightweight — they contain NO business
logic, NO LLM calls, and NO Spark queries.  They are pure pass-through
wrappers that enforce the separation between the agent and the data layer.

WHY SEPARATE TOOLS FROM SERVICES?
---------------------------------
  • The service layer owns the Spark queries (single source of truth).
  • The tool layer owns the function signatures that the LLM sees.
  • Changing a Spark query does not require updating the tool registry.
  • Adding a new tool does not require touching service code.

INPUT
-----
  Each function receives a typed *Request model from models.py.

OUTPUT
------
  Each function returns a dict or list of dicts (JSON-serialisable).
"""

from models import (
    InventoryRequest, PurchaseOrderRequest, CustomerOrderRequest,
    SupplierRequest, AlternateSupplierRequest, DemandForecastRequest,
    ShipmentRequest, WarehouseInventoryRequest, ExceptionRequest,
    ExceptionListRequest, SupplierEventRequest
)
from services.exception_service import ExceptionService

# Single shared service instance — Spark session is reused across all calls
service = ExceptionService()


# ===========================================================================
# 1. INVENTORY TOOLS
# ===========================================================================

def get_inventory(request: InventoryRequest):
    """
    Retrieve current inventory position for a SKU.
    Optionally filtered to a single warehouse.

    WHEN TO USE:
      The agent needs to know how much stock is on hand, allocated,
      available, and in-transit for a given SKU.
    """
    return service.get_inventory(
        sku_id=request.sku_id,
        warehouse_id=request.warehouse_id
    )


def get_warehouse_inventory(request: WarehouseInventoryRequest):
    """
    Retrieve inventory for a SKU across ALL warehouses.
    Used to detect warehouse imbalances (BRD Scenario 5).

    WHEN TO USE:
      The agent suspects inventory is unevenly distributed and wants
      to compare stock levels across all warehouses.
    """
    return service.get_warehouse_inventory(sku_id=request.sku_id)


# ===========================================================================
# 2. PURCHASE ORDER TOOLS
# ===========================================================================

def get_open_purchase_orders(request: PurchaseOrderRequest):
    """
    Retrieve all purchase order lines for a SKU, including PO header info.

    WHEN TO USE:
      The agent needs to check if there are pending deliveries, the
      expected delivery dates, and whether any POs are delayed.
    """
    return service.get_open_purchase_orders(sku_id=request.sku_id)


# ===========================================================================
# 3. CUSTOMER ORDER TOOLS
# ===========================================================================

def get_customer_orders(request: CustomerOrderRequest):
    """
    Retrieve all customer orders dependent on a SKU.
    Includes priority, quantity, requested delivery date, and status.

    WHEN TO USE:
      The agent needs to assess customer impact — how many orders are
      affected, which customers have priority, and what quantities are
      at risk.
    """
    return service.get_customer_orders(sku_id=request.sku_id)


# ===========================================================================
# 4. SUPPLIER TOOLS
# ===========================================================================

def get_supplier_performance(request: SupplierRequest):
    """
    Retrieve supplier master record and performance metrics
    (reliability score, lead time, capacity, approved status).

    WHEN TO USE:
      The agent needs to evaluate a supplier's track record before
      recommending expedite or alternate sourcing.
    """
    return service.get_supplier(supplier_id=request.supplier_id)


def get_alternate_suppliers(request: AlternateSupplierRequest):
    """
    Find all alternate approved suppliers that could fulfill a SKU.

    WHEN TO USE:
      The agent needs to generate an alternate-sourcing resolution option
      and compare cost, lead time, and reliability of available suppliers.
    """
    return service.get_alternate_suppliers(sku_id=request.sku_id)


def get_supplier_events(request: SupplierEventRequest):
    """
    Retrieve supplier events (delivery delays, capacity constraints,
    quality issues, force majeure, price changes) for a supplier.

    WHEN TO USE:
      The agent needs to understand the triggering event behind an
      exception — what happened, when, and how severe it is.
    """
    return service.get_supplier_events(supplier_id=request.supplier_id)


# ===========================================================================
# 5. DEMAND FORECAST TOOLS
# ===========================================================================

def get_demand_forecast(request: DemandForecastRequest):
    """
    Retrieve demand forecast summary for a SKU over the 90-day horizon.
    Returns average forecast, average actual, max actual, and demand profile.

    WHEN TO USE:
      The agent needs to project inventory depletion, detect demand
      spikes, and calculate projected stockout dates.
    """
    return service.get_demand_forecast(sku_id=request.sku_id)


# ===========================================================================
# 6. SHIPMENT TOOLS
# ===========================================================================

def get_shipments(request: ShipmentRequest):
    """
    Retrieve shipment records for purchase orders containing a SKU.
    Includes origin, destination, carrier, status, and dates.

    WHEN TO USE:
      The agent needs to evaluate shipment delays, identify alternate
      transportation options, and track in-transit inventory.
    """
    return service.get_shipments(sku_id=request.sku_id)


# ===========================================================================
# 7. EXCEPTION TOOLS
# ===========================================================================

def get_exception_details(request: ExceptionRequest):
    """
    Retrieve details of a specific supply chain exception by ID.
    Includes type, severity, status, description, and dates.

    WHEN TO USE:
      The user provides an exception ID and wants the agent to
      investigate that specific exception.
    """
    return service.get_exception(exception_id=request.exception_id)


def list_exceptions(request: ExceptionListRequest):
    """
    List all supply chain exceptions, optionally filtered by status.

    WHEN TO USE:
      The user wants to see all open exceptions or filter by status
      (e.g., DETECTED, RESOLVED, AWAITING_APPROVAL).
    """
    return service.list_exceptions(status=request.status)