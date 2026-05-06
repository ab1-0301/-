"""Smoke test — verifies imports and agent creation work (no API call)."""
from agents.inventory import query_stock


def test_query_stock_imports():
    """Verify inventory functions are importable and runnable."""
    result = query_stock("B")
    assert "USB-C" in result


def test_coordinator_creation():
    """Verify coordinator agent can be instantiated (no API key needed)."""
    try:
        from agents.coordinator import create_coordinator
        from autogen.beta.config import GeminiConfig

        config = GeminiConfig(model="test-model", temperature=0)
        agent = create_coordinator(config)
        assert agent is not None
        assert agent.name == "coordinator"
    except ImportError:
        pass  # AG2 not installed in CI, skip
