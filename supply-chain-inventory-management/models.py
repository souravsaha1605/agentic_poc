"""
models.py
=========
Pydantic data models for the Agentic AI Supply Chain Exception Management
Platform.

PURPOSE
-------
Defines strongly-typed request and response schemas for every tool the
agent can invoke.  Using Pydantic (rather than raw dicts) gives us:
  • Automatic parameter validation before tool execution
  • JSON Schema generation for the LLM tool registry
  • Self-documenting code (each model serves as a mini spec)

ARCHITECTURE ROLE
-----------------
  app.py  -->  agent  -->  tool_executor  -->  tools  -->  services
     |            |            |               |          |
     |     models.py <--------+---- models.py <--+---- models.py
     |            |            |               |          |
  UserQuery   AgentResponse  *Request    *Request    *Summary

Every layer speaks the language of these models, ensuring end-to-end
type safety from the LLM's JSON tool-call arguments all the way down
to the Spark queries.

DESIGN DECISIONS (per BRD)
--------------------------
  • BRD §21 (Tool Layer): every tool must have an input schema and an
    output schema.  Each *Request model is an input schema; each *Info
    or *Summary model is an output schema.
  • BRD §24 (LLM Requirements): the LLM must NOT be the source of truth
    for quantities, dates, or financial amounts.  These values originate
    from Spark queries and flow through typed models.
  • BRD §16 (Policy Engine): policy evaluation results are structured
    (PolicyResult) so they can be logged and audited independently
    of the LLM.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


# ===========================================================================
# SECTION 1: USER-FACING REQUEST
# ===========================================================================

class UserQuery(BaseModel):
    """The natural-language prompt from the user (planner, manager, etc.)."""
    query: str = Field(description="Natural language question or exception description from the user.")


# ===========================================================================
# SECTION 2: TOOL REQUEST MODELS (input schemas for each tool)
# ===========================================================================

class InventoryRequest(BaseModel):
    """Parameters for querying current inventory position."""
    sku_id: str = Field(description="SKU identifier (e.g. SKU-001).")
    warehouse_id: Optional[str] = Field(default=None, description="Optional warehouse ID to filter to a single warehouse.")


class PurchaseOrderRequest(BaseModel):
    """Parameters for querying open purchase orders for a SKU."""
    sku_id: str = Field(description="SKU identifier to find related purchase orders.")


class CustomerOrderRequest(BaseModel):
    """Parameters for querying customer orders dependent on a SKU."""
    sku_id: str = Field(description="SKU identifier to find dependent customer orders.")


class SupplierRequest(BaseModel):
    """Parameters for querying supplier performance metrics."""
    supplier_id: str = Field(description="Supplier identifier (e.g. S001).")


class AlternateSupplierRequest(BaseModel):
    """Parameters for finding alternate approved suppliers for a SKU."""
    sku_id: str = Field(description="SKU identifier to find alternate suppliers for.")

class DemandForecastRequest(BaseModel):
    """Parameters for querying demand forecast data for a SKU."""
    sku_id: str = Field(description="SKU identifier for demand forecast lookup.")


class ShipmentRequest(BaseModel):
    """Parameters for querying shipment status for a SKU."""
    sku_id: str = Field(description="SKU identifier to find related shipments.")

class WarehouseInventoryRequest(BaseModel):
    """Parameters for querying inventory across ALL warehouses for a SKU.
    Used to detect warehouse imbalances (BRD Scenario 5)."""
    sku_id: str = Field(description="SKU identifier to check inventory across all warehouses.")

class ExceptionRequest(BaseModel):
    """Parameters for retrieving details of a specific supply chain exception."""
    exception_id: str = Field(description="Exception ID (e.g. EXC-001).")

class ExceptionListRequest(BaseModel):
    """Parameters for listing all exceptions (optionally filtered by status)."""
    status: Optional[str] = Field(default=None, description="Optional status filter: DETECTED, CLASSIFIED, INVESTIGATING, RESOLVED, etc.")


class SupplierEventRequest(BaseModel):
    """Parameters for querying supplier events (triggers for exceptions)."""
    supplier_id: str = Field(description="Supplier identifier to find recent events.")


# ===========================================================================
# SECTION 3: TOOL RESPONSE MODELS (output schemas)
# ===========================================================================

class InventoryInfo(BaseModel):
    """Current inventory position for a single SKU/warehouse combination."""
    warehouse_id: str
    sku_id: str
    on_hand: int = Field(description="Physical units currently in the warehouse.")
    allocated: int = Field(description="Units reserved for existing customer orders.")
    available: int = Field(description="on_hand minus allocated (always >= 0).")
    in_transit: int = Field(description="Units en route from supplier.")
    safety_stock: int = Field(description="Minimum buffer from SKU master data.")


class SupplierInfo(BaseModel):
    """Supplier master record and performance metrics."""
    supplier_id: str
    supplier_name: str
    country: str
    region: str
    status: str
    lead_time_days: int
    reliability_score: float
    approved_supplier: bool
    capacity_units: int
    unit_cost: float


class PurchaseOrderInfo(BaseModel):
    """Purchase order header and line details for a SKU."""
    po_id: str
    supplier_id: str
    status: str
    order_date: str
    expected_delivery: str
    actual_delivery: Optional[str] = None
    line_id: int
    sku_id: str
    ordered_quantity: int
    received_quantity: int
    unit_cost: float


class CustomerOrderInfo(BaseModel):
    """Customer order details — used for impact analysis."""
    order_id: str
    customer_id: str
    sku_id: str
    quantity: int
    order_date: str
    requested_delivery_date: str
    priority: str
    status: str


class ShipmentInfo(BaseModel):
    """Shipment tracking details."""
    shipment_id: str
    po_id: str
    origin: str
    destination_warehouse: str
    status: str
    ship_date: str
    expected_arrival: str
    actual_arrival: Optional[str] = None
    carrier: str


class DemandForecastInfo(BaseModel):
    """Demand forecast summary for a SKU over the forecast horizon."""
    sku_id: str
    avg_forecast: float
    avg_actual: float
    max_actual: int
    demand_profile: str


class ExceptionInfo(BaseModel):
    """Supply chain exception record from the exceptions table."""
    exception_id: str
    exception_type: str
    severity: str
    status: str
    source_event_id: Optional[str] = None
    description: str
    created_at: str
    updated_at: str


class SupplierEventInfo(BaseModel):
    """Supplier event that may trigger an exception."""
    event_id: str
    supplier_id: str
    po_id: Optional[str] = None
    event_type: str
    event_date: str
    description: str
    severity: str


# ===========================================================================
# SECTION 4: COMPOSITE / BUSINESS MODELS
# ===========================================================================

class ImpactAnalysis(BaseModel):
    """Structured impact analysis output (BRD §12).
    Combines inventory, customer, supply, and logistics impact into a
    single typed object that the LLM can reference when generating
    recommendations."""
    sku_id: str
    current_inventory: int
    safety_stock: int
    available_inventory: int
    in_transit: int
    projected_stockout_date: Optional[str] = None
    shortage_quantity: Optional[int] = None
    affected_customer_orders: int
    affected_order_details: List[CustomerOrderInfo] = []
    demand_profile: str
    avg_daily_demand: float


class ResolutionOption(BaseModel):
    """One feasible mitigation option (BRD §14).
    The LLM proposes options; the policy engine evaluates them."""
    option_id: str
    action: str = Field(description="INVENTORY_TRANSFER, EXPEDITE_SUPPLIER, ALTERNATE_SUPPLIER, CUSTOMER_REALLOCATION, or COMBINATION.")
    description: str
    estimated_cost: float
    expected_resolution_date: str
    service_impact: str = Field(description="LOW, MEDIUM, or HIGH.")
    stockout_risk: str = Field(description="LOW, MEDIUM, or HIGH.")
    requires_approval: bool


class PolicyResult(BaseModel):
    """Deterministic policy evaluation result (BRD §16).
    This is computed OUTSIDE the LLM by the policy engine and cannot
    be overridden by the model."""
    option_id: str
    autonomous_execution_allowed: bool
    human_approval_required: bool
    approval_reason: Optional[str] = None
    policy_violations: List[str] = []
    cost_threshold: float
    configured_limit: float


class AgentResponse(BaseModel):
    """Final structured response returned to the user."""
    response: str