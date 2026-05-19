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
