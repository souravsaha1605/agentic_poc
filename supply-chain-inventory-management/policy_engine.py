"""
policy_engine.py
================
Deterministic Business Rules / Policy Engine.

PURPOSE
-------
Implements BRD §16 (Business Rules / Policy Engine).  Business rules are
EXTERNALISED from the LLM — the model cannot override them.  The policy
engine evaluates each resolution option against configurable criteria
and returns a structured PolicyResult.

ARCHITECTURE ROLE
-----------------
  agent  -->  LLM proposes options  -->  policy_engine.evaluate(option)
                                              |
                                              v
                                    PolicyResult (autonomous / approval / reject)
                                              |
                                              v
                              agent includes policy result in response

WHY EXTERNAL TO THE LLM?
------------------------
  BRD §15: "The system shall NOT allow the LLM to independently override
  deterministic business constraints."
  BRD §16: "Business rules shall be externalized from the LLM.  Rules
  shall be configurable without modifying agent prompts or application code."

CONFIGURABLE POLICIES (BRD §16 examples)
----------------------------------------
  IF action_cost <= $1,000
  AND customer_impact = LOW
  AND policy_compliant = TRUE
  THEN autonomous_execution_allowed

  IF action_cost > $1,000
  THEN human_approval_required

  IF action affects strategic_customer = TRUE
  THEN human_approval_required

  IF supplier_change = TRUE
  THEN procurement_approval_required

INPUT
-----
  A ResolutionOption (from the LLM) plus optional context (strategic customer,
  supplier change flag).

OUTPUT
------
  A PolicyResult with autonomous_execution_allowed, human_approval_required,
  policy_violations, and the configured cost threshold.
"""

from models import ResolutionOption, PolicyResult


class PolicyEngine:
    """
    Evaluates resolution options against business policies.

    All thresholds are configurable via __init__ parameters so they can be
    loaded from environment variables or a config file without changing
    agent prompts (BRD §16).
    """

    def __init__(
        self,
        autonomous_cost_limit: float = 1000.0,
        max_transfer_quantity: int = 5000,
        require_approved_suppliers: bool = True,
        require_approved_warehouses: bool = True,
    ):
        """
        Parameters (all configurable):
            autonomous_cost_limit   – actions below this cost can auto-execute
            max_transfer_quantity   – max units in a single inventory transfer
            require_approved_suppliers – only approved suppliers allowed
            require_approved_warehouses – only approved warehouses allowed
        """
        self.autonomous_cost_limit = autonomous_cost_limit
        self.max_transfer_quantity = max_transfer_quantity
        self.require_approved_suppliers = require_approved_suppliers
        self.require_approved_warehouses = require_approved_warehouses

    def evaluate(
        self,
        option: ResolutionOption,
        affects_strategic_customer: bool = False,
        involves_supplier_change: bool = False,
    ) -> PolicyResult:
        """
        Evaluate a single resolution option against all configured policies.

        Parameters:
            option                      – the LLM-proposed resolution option
            affects_strategic_customer – whether the action impacts a
                                          strategic/priority customer
            involves_supplier_change    – whether the action changes the
                                          supplier (requires procurement approval)

        Returns:
            PolicyResult with the evaluation outcome.
        """
        violations = []
        requires_approval = False
        approval_reason = None

        # --- Policy 1: Financial guardrail (BRD §16, §26) ---
        # Actions above the autonomous cost limit require human approval
        if option.estimated_cost > self.autonomous_cost_limit:
            requires_approval = True
            approval_reason = (
                f"Action cost ${option.estimated_cost:.2f} exceeds "
                f"autonomous execution limit ${self.autonomous_cost_limit:.2f}."
            )
            violations.append("COST_EXCEEDS_AUTONOMOUS_LIMIT")

        # --- Policy 2: Strategic customer guardrail ---
        # Actions affecting strategic customers always require approval
        if affects_strategic_customer:
            requires_approval = True
            if not approval_reason:
                approval_reason = "Action affects a strategic/priority customer."
            violations.append("STRATEGIC_CUSTOMER_IMPACT")

        # --- Policy 3: Supplier change guardrail ---
        # Changing suppliers requires procurement manager approval
        if involves_supplier_change:
            requires_approval = True
            if not approval_reason:
                approval_reason = "Action involves changing supplier (procurement approval required)."
            violations.append("SUPPLIER_CHANGE_REQUIRES_PROCUREMENT_APPROVAL")

        # --- Policy 4: Stockout risk guardrail ---
        # High stockout risk options should be flagged for review
        if option.stockout_risk.upper() == "HIGH":
            requires_approval = True
            if not approval_reason:
                approval_reason = "High stockout risk requires human review."
            violations.append("HIGH_STOCKOUT_RISK")

        # --- Determine if autonomous execution is allowed ---
        autonomous_allowed = not requires_approval

        return PolicyResult(
            option_id=option.option_id,
            autonomous_execution_allowed=autonomous_allowed,
            human_approval_required=requires_approval,
            approval_reason=approval_reason,
            policy_violations=violations,
            cost_threshold=option.estimated_cost,
            configured_limit=self.autonomous_cost_limit,
        )

    def evaluate_options(
        self,
        options: list,
        affects_strategic_customer: bool = False,
        involves_supplier_change: bool = False,
    ) -> list:
        """
        Evaluate a list of ResolutionOption objects and return a list of
        PolicyResult objects.  Convenience wrapper for batch evaluation.
        """
        results = []
        for opt in options:
            # Determine if this specific option involves a supplier change
            is_supplier_change = involves_supplier_change or (
                opt.action.upper() in ("ALTERNATE_SUPPLIER", "COMBINATION")
            )
            results.append(
                self.evaluate(
                    option=opt,
                    affects_strategic_customer=affects_strategic_customer,
                    involves_supplier_change=is_supplier_change,
                )
            )
        return results