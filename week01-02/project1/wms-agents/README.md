# WMS Multi-Agent System

**WMS 多智能体仓库管理系统** — 用自然语言查库存，两个 AI Agent 协作完成

> **Track:** `multi-agent`
> **Base:** from scratch
> **AG2 version:** `ag2 >=0.8.0` (Beta · `autogen.beta`)

---

## What it is / 一句话定位

**Input:** 用户关于仓库库存的自然语言问题
**Output:** 协调 Coordinator + Inventory 两个 agent 协作后的结构化回答

多智能体架构展示 **Sub-task delegation** 模式：
- **Coordinator Agent** — 接收问题、分解子任务、调用 Inventory Agent、整合回复
- **Inventory Agent** — 查询库存数据、检查预警、搜索商品

---

## 5-minute setup / 5 分钟跑起来

```bash
# 1. clone
git clone <your-repo-url>
cd wms-agents

# 2. python env
python -m venv .venv && source .venv/bin/activate    # Python 3.10–3.13
pip install -r requirements.txt

# 3. set keys
cp .env.example .env
# 编辑 .env 填入你的 API Key（支持阿里云百炼 DashScope / OpenRouter）

# 4. run
python main.py
```

Expected first-run output:

```
==================================================
  WMS 多智能体系统 / WMS Multi-Agent System
  C5-AG2 Challenge — Track: multi-agent
==================================================
Agent: Coordinator <-> Inventory Specialist
输入 'quit' 退出 / Type 'quit' to exit

🧑‍💻 You:
```

---

## Multi-agent design / 多 agent 架构

```
+-------------+   consult_inventory   +-------------------+
| Coordinator | ------------------->  | Inventory Agent   |
|   Agent     |                      | (get_stock,       |
|             | <------------------- |  get_alerts,       |
+-------------+     return data      |  find_product)    |
                                     +-------------------+
```

| Agent | Role | Tools | Source |
|-------|------|-------|--------|
| Coordinator | 分解任务、调用子 agent、整合回复 | `consult_inventory` | mine |
| Inventory | 查询库存、预警检查、商品搜索 | `get_stock`, `get_alerts`, `find_product` | adapted from AG2 Beta docs |

---

## Live demo / 现场演示

- **Video:** _(录制 60-90 秒 Loom 视频后贴链接)_

---

## Project structure / 项目结构

```
wms-agents/
├── main.py                 CLI entry point
├── agents/
│   ├── coordinator.py      Coordinator Agent + agent-as-tool wiring
│   └── inventory.py        Inventory data layer
├── prompts/
│   ├── coordinator.txt     Coordinator system prompt
│   └── inventory.txt       Inventory system prompt
├── data/
│   └── inventory.json      Mock warehouse inventory
├── tests/
│   ├── test_inventory.py   Unit tests for data functions
│   └── test_smoke.py       Smoke tests
├── README.md
├── AI_LOG.md
├── ATTRIBUTION.md
├── LICENSE
├── .env.example
└── requirements.txt
```

---

## Tech stack / 技术栈

- AG2 Beta (`autogen.beta`)
- Python 3.10+
- 阿里云百炼 DashScope / OpenRouter / Gemini

---

## Tests

```bash
pytest -q
```

The smoke test gracefully handles missing AG2 installation (try/except ImportError), so tests can run offline.

---

## Troubleshooting / 常见问题

- **`ModuleNotFoundError: No module named 'autogen.beta'`** — 执行 `pip install "ag2[openai]"` 安装 AG2 及 OpenAI 扩展
- **`ImportError: OpenAIConfig requires optional dependencies`** — 执行 `pip install "ag2[openai]"`
- **`401` or `403` from API** — 检查 API Key 是否正确，或模型在所在区域不可用
- **`402` Payment Required** — API 提供商账户需要充值

---

## License

MIT. See `LICENSE`.

## Acknowledgements

- AG2 team (Qingyun Wu, Vasiliy Radostev, contributors).
- AG2 Beta docs — API 参考和协作模式灵感来源。
- Elite20 C5-AG2 challenge framing.
