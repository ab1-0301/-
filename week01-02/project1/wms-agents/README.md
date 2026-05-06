# WMS Multi-Agent System

**WMS 多智能体仓库管理系统 — C5-AG2 Challenge**

> **Track:** `multi-agent`
> **AG2 version:** `ag2 >=0.8.0` (Beta · `autogen.beta`)
> **From scratch** — inspired by AG2 Beta examples

## What it is

**Input:** 用户关于仓库库存的自然语言问题
**Output:** 协调 Coordinator + Inventory 两个 agent 协作后的结构化回答

多智能体架构展示 Sub-task delegation 模式：
- **Coordinator Agent** — 接收问题、分解子任务、调用 Inventory Agent、整合回复
- **Inventory Agent** — 查询库存数据、检查预警、搜索商品

## 5-minute setup

```bash
git clone <your-repo-url>
cd wms-agents
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 OPENROUTER_API_KEY
python main.py
```

## Multi-agent design

```
+-------------+   consult_inventory   +-------------------+
| Coordinator | ------------------->  | Inventory Agent   |
|   Agent     |                      | (get_stock,       |
|             | <------------------- |  get_alerts,       |
+-------------+     return data      |  find_product)    |
                                     +-------------------+
```

## Tests

```bash
pytest -q
```

## Tech stack

- AG2 Beta (`autogen.beta`)
- Python 3.10+
- OpenRouter / Gemini

## Project structure

```
wms-agents/
├── main.py                 CLI entry point
├── agents/
│   ├── coordinator.py      Coordinator Agent + agent-as-tool wiring
│   └── inventory.py        Inventory data layer
├── data/
│   └── inventory.json      Mock warehouse inventory
├── tests/
│   ├── test_inventory.py   Unit tests for data functions
│   └── test_smoke.py       Smoke tests
├── README.md
├── AI_LOG.md
├── ATTRIBUTION.md
├── .env.example
└── requirements.txt
```

## License

MIT
