# WMS Multi-Agent System — C5-AG2 Challenge

**Date:** 2026-05-06
**Track:** multi-agent
**Approach:** From scratch with AG2 Beta
**Status:** Approved

## Overview

Build a Warehouse Management System multi-agent system using AG2 Beta framework.
Two collaborating agents (Coordinator + Inventory) communicate via sub-task delegation
to answer warehouse inventory queries.

## Architecture

```
User (CLI) → Coordinator Agent → [delegates] → Inventory Agent → Data
                                  ← [returns] ←
```

### Agents

1. **Coordinator Agent** — Receives user questions about inventory, decomposes,
   delegates sub-tasks to Inventory Agent, synthesizes results, responds.

2. **Inventory Agent** — Queries inventory data (JSON), returns structured results
   about stock levels, product categories, and low-stock alerts.

### Collaboration Pattern

- Sub-task delegation via Agent-as-tool
- Coordinator has `query_inventory` tool from Inventory Agent
- Async `asyncio.run` for the main loop

### Data

Static JSON inventory with categories, products, quantities, locations.

## Project Structure

```
wms-agents/
├── main.py               # CLI entry point
├── agents/
│   ├── __init__.py
│   ├── coordinator.py    # Coordinator Agent
│   └── inventory.py      # Inventory Agent + data layer
├── data/
│   └── inventory.json    # Mock inventory
├── tests/
│   └── test_smoke.py     # Smoke test
├── README.md
├── AI_LOG.md
├── ATTRIBUTION.md
├── .env.example
└── requirements.txt
```

## Tech Stack

- AG2 Beta (`autogen.beta`)
- Python 3.10+
- OpenRouter / Gemini API
- CLI interface

## Success Criteria

1. `git clone → pip install → python main.py` works in under 5 min
2. Coordinator + Inventory Agent cooperate on ≥ 2 query types
3. AI_LOG.md has ≥ 5 verifiable iterations
4. 60-90s demo video can be recorded
