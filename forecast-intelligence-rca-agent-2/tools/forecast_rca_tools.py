"""Thin wrappers: no SQL, global current user or conversation state lives here."""


def dispatch(business, principal, plan):
    # A comparison must load an owned baseline in ConversationService. A model
    # cannot submit invented baseline/current numbers as authoritative facts.
    if plan.tool == "compare_scenarios":
        raise ValueError(
            "Compare only persisted versions through the conversation service."
        )
    return business.execute(plan, principal)
