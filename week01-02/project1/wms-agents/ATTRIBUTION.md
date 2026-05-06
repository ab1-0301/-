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
