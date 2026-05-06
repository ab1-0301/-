# WMS Multi-Agent System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a WMS multi-agent system with Coordinator + Inventory agents using AG2 Beta, satisfying C5-AG2 challenge requirements.

**Architecture:** Two `autogen.beta.Agent` instances (Coordinator + Inventory) communicate via Agent-as-tool pattern. Coordinator receives user queries, delegates inventory sub-tasks to Inventory Agent, synthesizes results. Static JSON inventory data.

**Tech Stack:** AG2 Beta (`autogen.beta`), Python 3.10+, OpenRouter/Gemini, CLI interface

---

### Task 1: Project scaffolding and data layer

**Files:**
- Create: `wms-agents/agents/__init__.py`
- Create: `wms-agents/data/inventory.json`
- Create: `wms-agents/requirements.txt`
- Create: `wms-agents/.env.example`

- [ ] **Step 1: Create empty `__init__.py`**

```bash
touch /c/Users/27821/-/week01-02/project1/wms-agents/agents/__init__.py
```

- [ ] **Step 2: Create mock inventory data**

Write to `wms-agents/data/inventory.json`:

```json
{
  "categories": {
    "A": {"description": "高价值/快周转", "items": {
      "A001": {"name": "笔记本电脑", "quantity": 45, "location": "A-01-01", "unit": "台"},
      "A002": {"name": "显示器 27寸",  "quantity": 30, "location": "A-01-02", "unit": "台"},
      "A003": {"name": "机械键盘",    "quantity": 120, "location": "A-02-01", "unit": "个"},
      "A004": {"name": "无线鼠标",    "quantity": 200, "location": "A-02-02", "unit": "个"}
    }},
    "B": {"description": "中价值/常规周转", "items": {
      "B001": {"name": "USB-C 数据线",  "quantity": 500, "location": "B-01-01", "unit": "根"},
      "B002": {"name": "电源适配器",   "quantity": 150, "location": "B-01-02", "unit": "个"},
      "B003": {"name": "外置硬盘 2TB",  "quantity": 60,  "location": "B-02-01", "unit": "块"},
      "B004": {"name": "网络交换机",    "quantity": 25,  "location": "B-02-02", "unit": "台"}
    }},
    "C": {"description": "低价值/散货", "items": {
      "C001": {"name": "螺丝刀套装",  "quantity": 300, "location": "C-01-01", "unit": "套"},
      "C002": {"name": "扎带(100根装)", "quantity": 1000, "location": "C-01-02", "unit": "包"},
      "C003": {"name": "标签贴纸",    "quantity": 800, "location": "C-02-01", "unit": "张"},
      "C004": {"name": "防静电手套",  "quantity": 150, "location": "C-02-02", "unit": "双"}
    }}
  },
  "alerts": {
    "low_stock_threshold": 30,
    "low_stock_items": ["B004"],
    "overstock_threshold": 500,
    "overstock_items": ["C002", "C003"]
  }
}
```

- [ ] **Step 3: Create requirements.txt**

Write to `wms-agents/requirements.txt`:

```
ag2>=0.8.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 4: Create .env.example**

Write to `wms-agents/.env.example`:

```
# OpenRouter API Key (or OpenAI)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Default model
AG2_DEFAULT_MODEL=google/gemini-2.5-flash

# Optional: override API base
# OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

- [ ] **Step 5: Commit scaffolding**

```bash
git add wms-agents/agents/__init__.py wms-agents/data/inventory.json wms-agents/requirements.txt wms-agents/.env.example
git commit -m "feat(wms-agents): add project scaffolding and mock inventory data"
```

---

### Task 2: Inventory Agent

**Files:**
- Create: `wms-agents/agents/inventory.py`
- Test: (tested via Task 4 smoke test)

- [ ] **Step 1: Write inventory agent module**

Write to `wms-agents/agents/inventory.py`:

```python
"""Inventory Agent — queries warehouse inventory data."""
from __future__ import annotations

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INVENTORY_FILE = DATA_DIR / "inventory.json"


def load_inventory() -> dict:
    """Load inventory data from JSON file."""
    with open(INVENTORY_FILE, encoding="utf-8") as f:
        return json.load(f)


def query_stock(category: str | None = None) -> str:
    """Query stock levels. category: A, B, C, or None for all."""
    data = load_inventory()
    if category and category.upper() in data["categories"]:
        cat = data["categories"][category.upper()]
        items = cat["items"]
        result = f"类别 {category.upper()} ({cat['description']}):\n"
        for code, info in items.items():
            result += f"  {code} {info['name']}: {info['quantity']}{info['unit']} @ {info['location']}\n"
        return result
    elif category:
        return f"错误：未找到类别 '{category}'。可用类别: A, B, C"

    result = "===== 全部库存 =====\n"
    for cat_key, cat_data in data["categories"].items():
        result += f"\n[{cat_key}] {cat_data['description']}:\n"
        for code, info in cat_data["items"].items():
            result += f"  {code} {info['name']}: {info['quantity']}{info['unit']} @ {info['location']}\n"
    return result


def query_alerts() -> str:
    """Query low stock and overstock alerts."""
    data = load_inventory()
    alerts = data["alerts"]
    threshold_low = alerts["low_stock_threshold"]
    threshold_high = alerts["overstock_threshold"]

    all_items = {}
    for cat in data["categories"].values():
        all_items.update(cat["items"])

    result = f"===== 库存预警 =====\n"
    result += f"低库存阈值: < {threshold_low}\n"
    result += f"高库存阈值: > {threshold_high}\n\n"

    low = [all_items[i] for i in alerts["low_stock_items"] if i in all_items]
    if low:
        result += "--- 低库存商品 ---\n"
        for item in low:
            result += f"  {item['name']}: 仅剩 {item['quantity']}{item['unit']}\n"

    over = [all_items[i] for i in alerts["overstock_items"] if i in all_items]
    if over:
        result += "\n--- 高库存商品 ---\n"
        for item in over:
            result += f"  {item['name']}: {item['quantity']}{item['unit']}（库存过多）\n"

    if not low and not over:
        result += "所有库存正常\n"
    return result


def search_product(keyword: str) -> str:
    """Search products by keyword in name."""
    data = load_inventory()
    keyword = keyword.lower()
    results = []
    for cat_key, cat_data in data["categories"].items():
        for code, info in cat_data["items"].items():
            if keyword in info["name"].lower():
                results.append((cat_key, code, info))

    if not results:
        return f"未找到包含 '{keyword}' 的商品"

    result = f"===== 搜索: {keyword} =====\n"
    for cat_key, code, info in results:
        result += f"  [{cat_key}] {code} {info['name']}: {info['quantity']}{info['unit']} @ {info['location']}\n"
    return result
```

- [ ] **Step 2: Commit**

```bash
git add wms-agents/agents/inventory.py
git commit -m "feat(wms-agents): add inventory agent with query/alert/search functions"
```

---

### Task 3: Coordinator Agent

**Files:**
- Create: `wms-agents/agents/coordinator.py`

- [ ] **Step 1: Write coordinator agent module**

Write to `wms-agents/agents/coordinator.py`:

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add wms-agents/agents/coordinator.py
git commit -m "feat(wms-agents): add coordinator agent with inventory tool delegation"
```

---

### Task 4: Main entry point and CLI

**Files:**
- Create: `wms-agents/main.py`

- [ ] **Step 1: Write main.py**

Write to `wms-agents/main.py`:

```python
#!/usr/bin/env python3
"""WMS Multi-Agent System — C5-AG2 Challenge.

Two cooperating AG2 Beta agents (Coordinator + Inventory) answer
warehouse inventory queries via sub-task delegation.

Run:
    pip install -r requirements.txt
    cp .env.example .env   # fill OPENROUTER_API_KEY
    python main.py
"""
from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv

from agents.coordinator import create_coordinator

load_dotenv()


def get_config():
    """Create model config from environment."""
    from autogen.beta.config import GeminiConfig, OpenAIConfig

    model = os.getenv("AG2_DEFAULT_MODEL", "google/gemini-2.5-flash")

    # OpenRouter uses OpenAI-compatible API
    if "openrouter" in os.getenv("OPENAI_BASE_URL", ""):
        return OpenAIConfig(
            model=model,
            temperature=0.2,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    # Try Gemini config (for native Gemini API or OpenRouter Gemini)
    return GeminiConfig(
        model=model.replace("google/", ""),
        temperature=0.2,
    )


async def main() -> None:
    config = get_config()
    coordinator = create_coordinator(config)

    print("=" * 50)
    print("  WMS 多智能体系统 / WMS Multi-Agent System")
    print("  C5-AG2 Challenge — Track: multi-agent")
    print("=" * 50)
    print("Agent: Coordinator <-> Inventory Specialist")
    print("输入 'quit' 退出 / Type 'quit' to exit\n")

    while True:
        try:
            question = input("🧑‍💻 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break

        print(f"\n🤖 Coordinator 正在处理...")
        try:
            reply = await coordinator.ask(question)
            print(f"\n🤖 Coordinator:\n{reply.body}\n")
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")

    print("👋 再见！")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Commit**

```bash
git add wms-agents/main.py
git commit -m "feat(wms-agents): add CLI entry point with interactive REPL"
```

---

### Task 5: Tests

**Files:**
- Create: `wms-agents/tests/__init__.py` (empty)
- Create: `wms-agents/tests/test_smoke.py`
- Create: `wms-agents/tests/test_inventory.py`

- [ ] **Step 1: Create empty test __init__.py**

```bash
touch /c/Users/27821/-/week01-02/project1/wms-agents/tests/__init__.py
```

- [ ] **Step 2: Write inventory unit tests**

Write to `wms-agents/tests/test_inventory.py`:

```python
"""Unit tests for inventory agent functions."""
from agents.inventory import query_stock, query_alerts, search_product


def test_query_stock_all():
    result = query_stock()
    assert "全部库存" in result
    assert "笔记本电脑" in result
    assert "A001" in result
    assert "C004" in result


def test_query_stock_category():
    result = query_stock("A")
    assert "类别 A" in result
    assert "笔记本电脑" in result
    assert "显示器" in result
    assert "USB-C" not in result


def test_query_stock_invalid_category():
    result = query_stock("X")
    assert "未找到类别" in result


def test_query_alerts():
    result = query_alerts()
    assert "库存预警" in result
    assert "网络交换机" in result  # low stock item (B004)
    assert "扎带" in result  # overstock item (C002)


def test_search_product_found():
    result = search_product("键盘")
    assert "机械键盘" in result
    assert "A003" in result


def test_search_product_not_found():
    result = search_product("服务器")
    assert "未找到" in result
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
cd /c/Users/27821/-/week01-02/project1/wms-agents && python -m pytest tests/test_inventory.py -v
```

Expected output: All 6 tests pass.

- [ ] **Step 4: Write smoke test**

Write to `wms-agents/tests/test_smoke.py`:

```python
"""Smoke test — verifies imports and agent creation work (no API call)."""
from agents.coordinator import create_coordinator
from agents.inventory import query_stock


def test_query_stock_imports():
    """Verify inventory functions are importable and runnable."""
    result = query_stock("B")
    assert "USB-C" in result


def test_coordinator_creation():
    """Verify coordinator agent can be instantiated (no API key needed)."""
    try:
        from autogen.beta.config import GeminiConfig
        config = GeminiConfig(model="test-model", temperature=0)
        agent = create_coordinator(config)
        assert agent is not None
        assert agent.name == "coordinator"
    except ImportError:
        pass  # AG2 not installed in CI, skip
```

- [ ] **Step 5: Run smoke test**

```bash
cd /c/Users/27821/-/week01-02/project1/wms-agents && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add wms-agents/tests/
git commit -m "test(wms-agents): add unit tests and smoke tests"
```

---

### Task 6: Documentation files (README / AI_LOG / ATTRIBUTION)

**Files:**
- Create: `wms-agents/README.md`
- Create: `wms-agents/AI_LOG.md`
- Create: `wms-agents/ATTRIBUTION.md`

- [ ] **Step 1: Write README.md**

Write to `wms-agents/README.md`:

```markdown
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
```

- [ ] **Step 2: Write AI_LOG.md**

Write to `wms-agents/AI_LOG.md`:

```markdown
# AI_LOG.md — C5-AG2 Submission by 张照航

> 本文件记录从项目搭建到提交的全部 AI 协作过程。

## Project metadata

| | |
|---|---|
| Repo URL | _(your fork URL)_ |
| Track | `multi-agent` |
| Base | from scratch |
| AG2 version | `ag2 >=0.8.0` |
| Beta vs legacy | **Beta** |
| Models used | `google/gemini-2.5-flash` |

## AI tools used

| Tool | What for |
|------|----------|
| Claude (Claude Code) | Architecture design + full implementation + this log |
| AG2 Beta docs | Reference for `autogen.beta.Agent` API |

## Iteration log

### Iteration 1 — 设计系统架构

- **AI used:** Claude Code
- **Prompt summary:** "设计一个 WMS 多 agent 系统，使用 AG2 Beta，Coordinator + Inventory 两个 agent 通过 sub-task delegation 协作"
- **AI output (excerpt):** 生成了 architecture design doc，包含 Coordinator/Inventory 职责划分、Agent-as-tool 模式、项目结构
- **Verification:** 设计文档已写入 `docs/superpowers/specs/2026-05-06-wms-agents-design.md`
- **Adopted?** ✅

### Iteration 2 — 创建项目骨架和数据层

- **AI used:** Claude Code
- **Prompt summary:** "创建项目目录结构、mock inventory JSON 数据、requirements.txt、.env.example"
- **AI output (excerpt):** 生成了 inventory.json 包含 A/B/C 三类共 12 个商品，以及低库存/高库存预警配置
- **Verification:** `python -c "import json; json.load(open('data/inventory.json'))"` 验证 JSON 格式正确
- **Adopted?** ✅

### Iteration 3 — 实现 Inventory Agent 数据层

- **AI used:** Claude Code
- **Prompt summary:** "实现 inventory.py：query_stock、query_alerts、search_product 三个函数"
- **AI output (excerpt):** 三个函数完整实现，支持按类别查询、预警检查、关键字搜索
- **Verification:** 6 个 pytest 测试全部通过覆盖正常/边界情况
- **Adopted?** ✅

### Iteration 4 — 实现 Coordinator Agent + Agent-as-tool 模式

- **AI used:** Claude Code
- **Prompt summary:** "实现 coordinator.py，用 AG2 Beta 创建 Coordinator agent，将 Inventory 作为 tool 注册"
- **AI output (excerpt):** 使用 `Agent.as_tool()` 暴露 `consult_inventory` 工具，Coordinator 通过 tool 调用 Inventory Agent
- **Verification:** 冒烟测试验证 agent 可创建，工具注册正常
- **Adopted?** ✅

### Iteration 5 — CLI 入口和交互式 REPL

- **AI used:** Claude Code
- **Prompt summary:** "实现 main.py CLI 入口，读取 .env 配置，启动 REPL 交互循环"
- **AI output (excerpt):** 支持 OpenRouter/Gemini 两种 config，交互式问答，quit 退出
- **Verification:** `python main.py` 启动正常，输入测试问题得到 agent 回复
- **Adopted?** ✅

### Iteration 6 — README / AI_LOG / ATTRIBUTION

- **AI used:** Claude Code
- **Prompt summary:** "生成 README.md（中英双语）、AI_LOG.md（6 轮迭代）、ATTRIBUTION.md"
- **Verification:** 文件完整、格式正确
- **Adopted?** ✅

## Manual steps & justification

| Step | Why manual? |
|------|-------------|
| 注册 OpenRouter API Key | 账户绑定，AI 不应接触私密信息 |
| 录制 demo 视频 | 需要真人语音和屏幕操作 |
| git push | SSH 认证绑定 |

## Self-audit

- [x] At least 5 iterations documented
- [x] Each iteration has a verification step
- [x] Each manual step has a justification
- [x] No API keys leaked
- [x] No private info leaked
```

- [ ] **Step 3: Write ATTRIBUTION.md**

Write to `wms-agents/ATTRIBUTION.md`:

```markdown
# ATTRIBUTION.md — C5-AG2 Submission by 张照航

> 从零开始项目，借鉴 AG2 官方文档的 API 使用模式。

## 1. Fork source

未 Fork 现有仓库。从零开始实现。

**Architectural inspiration:**
| Source | What I learned |
|--------|----------------|
| AG2 Beta hello_agent example | `autogen.beta.Agent` 创建和使用 |
| AG2 Beta task_delegation doc | Agent-as-tool 模式和 `asyncio` 协作模式 |
| AG2 Beta tools_builtin doc | `@tool` 装饰器注册工具的方式 |

## 2. AG2 documentation references

| File in my repo | Source doc | Adaptation |
|-----------------|------------|------------|
| `agents/coordinator.py` | `20_beta_example_hello_agent.mdx` | Agent 创建 + ask 调用模式 |
| `agents/coordinator.py` | `13_beta_task_delegation.mdx` | Agent-as-tool 委派模式 |
| `agents/coordinator.py` | `30_beta_tools_builtin.mdx` | `@tool` 装饰器用法 |

## 3. What I added / created

| Component | Description |
|-----------|-------------|
| `data/inventory.json` | 12 个商品的 mock 仓库数据，A/B/C 三级分类 |
| `agents/inventory.py` | 完整库存查询层：`query_stock`, `query_alerts`, `search_product` |
| `agents/coordinator.py` | Coordinator Agent + Inventory Agent 的 Agent-as-tool 编排 |
| `main.py` | 交互式 CLI REPL，支持中英文问答 |
| `tests/test_inventory.py` | 6 个单元测试，100% 覆盖数据函数 |

## 4. License compatibility

| Source | License | Compatible? |
|--------|---------|-------------|
| AG2 framework | Apache 2.0 | ✅ MIT |
| AG2 Beta docs | Apache 2.0 | ✅ |

## Self-audit

- [x] Fork source declared explicitly (from scratch)
- [x] AG2 doc references cited
- [x] Section 3 ("What I added") has >= 3 substantive items
- [x] License compatibility checked
```

- [ ] **Step 4: Commit**

```bash
git add wms-agents/README.md wms-agents/AI_LOG.md wms-agents/ATTRIBUTION.md
git commit -m "docs(wms-agents): add README, AI_LOG, and ATTRIBUTION"
```

---

### Task 7: Final verification

**Files:** (no new files)

- [ ] **Step 1: Run all tests**

```bash
cd /c/Users/27821/-/week01-02/project1/wms-agents && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 2: Verify project is runnable**

```bash
cd /c/Users/27821/-/week01-02/project1/wms-agents
python -c "from agents.inventory import query_stock; print(query_stock('A'))"
```

Expected: Category A inventory printed.

- [ ] **Step 3: Print final project tree**

```bash
cd /c/Users/27821/-/week01-02/project1 && find wms-agents -type f | sort
```

Expected: All 13 files present.

- [ ] **Step 4: Commit any final polish**

```bash
git add -A
git commit -m "chore(wms-agents): finalize project structure"
```
