"""Coordinator Agent — receives user queries, delegates to sub-agents."""
from __future__ import annotations

from autogen.beta import Agent
from autogen.beta.config import GeminiConfig

from .inventory import query_stock, query_alerts, search_product


def create_coordinator(config: GeminiConfig) -> Agent:
    """Create the lead Coordinator agent with inventory tools."""
    # Create Inventory sub-agent
    inventory_agent = Agent(
        "inventory_agent",
        prompt=(
            "You are a WMS Inventory Specialist. "
            "You answer questions about warehouse stock levels, "
            "product locations, and inventory alerts. "
            "Be precise and include quantities and locations."
        ),
        config=config,
    )

    # Register inventory tools on the sub-agent
    from autogen.beta import tool

    @tool
    def get_stock(category: str | None = None) -> str:
        """Query stock by category (A, B, C) or all if None."""
        return query_stock(category)

    @tool
    def get_alerts() -> str:
        """Check low stock and overstock alerts."""
        return query_alerts()

    @tool
    def find_product(keyword: str) -> str:
        """Search for a product by keyword in its name."""
        return search_product(keyword)

    inventory_agent.tools.add(get_stock)
    inventory_agent.tools.add(get_alerts)
    inventory_agent.tools.add(find_product)

    # Expose inventory agent as a tool for coordinator
    consult_inventory = inventory_agent.as_tool(
        name="consult_inventory",
        description="Ask the inventory specialist about stock levels, "
                    "product locations, or inventory alerts.",
    )

    # Create Coordinator agent
    coordinator = Agent(
        "coordinator",
        prompt=(
            "You are a WMS Coordinator. Your role: "
            "1. Receive user questions about warehouse operations.\n"
            "2. Decompose complex questions into sub-tasks.\n"
            "3. Use the `consult_inventory` tool to get inventory data.\n"
            "4. Synthesize the response in clear, organized Chinese or English.\n\n"
            "Always check inventory data before answering stock-related questions. "
            "If the user asks about low stock or alerts, call consult_inventory "
            "with an appropriate query."
        ),
        config=config,
    )
    coordinator.tools.add(consult_inventory)

    return coordinator


# Mapping of function names for direct use (non-AG2 mode fallback)
TOOL_MAP = {
    "get_stock": query_stock,
    "get_alerts": query_alerts,
    "find_product": search_product,
}
