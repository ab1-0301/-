# AI_LOG.md — C5-AG2 Submission by 张照航

> 本文件记录从项目搭建到提交的全部 AI 协作过程。Elite20 AI-First 原则要求：
> 每一步都有 AI 参与，每一处手动步骤都有反向举证。

## Project metadata / 项目信息

| | |
|---|---|
| Repo URL | https://github.com/ab1-0301/- |
| Track | `multi-agent` |
| Base | from scratch |
| AG2 version | `ag2 >=0.8.0` |
| Beta vs legacy | **Beta** |
| Models used | `qwen-plus` (DashScope) |

## AI tools used / 使用的 AI 工具

| Tool | What for |
|------|----------|
| Claude Code | Architecture design + implementation + documentation |
| AG2 Beta docs | Reference for `autogen.beta.Agent` API and patterns |

## Iteration log / 迭代日志

### Iteration 1 — 设计系统架构

- **AI used:** Claude Code
- **Prompt summary:** 设计一个 WMS 多 agent 系统，使用 AG2 Beta，Coordinator + Inventory 两个 agent 通过 sub-task delegation 协作
- **AI output (excerpt):** 生成了 architecture design doc，包含 Coordinator/Inventory 职责划分、Agent-as-tool 模式、项目结构
- **Verification:** 设计文档已写入 `docs/superpowers/specs/2026-05-06-wms-agents-design.md`
- **Adopted?** ✅
- **What I changed manually and why:** 无修改

### Iteration 2 — 创建项目骨架和数据层

- **AI used:** Claude Code
- **Prompt summary:** 创建项目目录结构、mock inventory JSON 数据、requirements.txt、.env.example
- **AI output (excerpt):** inventory.json 包含 A/B/C 三类共 12 个商品，以及低库存/高库存预警配置
- **Verification:** `python -m json.tool data/inventory.json` 验证 JSON 格式正确
- **Adopted?** ✅
- **What I changed manually and why:** 无修改

### Iteration 3 — 实现 Inventory Agent 数据层

- **AI used:** Claude Code
- **Prompt summary:** 实现 inventory.py：query_stock、query_alerts、search_product 三个函数
- **AI output (excerpt):** 三个函数完整实现，支持按类别查询（A/B/C/全部）、预警检查（低库存/高库存阈值）、关键字搜索
- **Verification:** 6 个 pytest 测试全部通过，覆盖正常查询、无效类别、搜索命中/未命中
- **Adopted?** ✅
- **What I changed manually and why:** 无修改

### Iteration 4 — 实现 Coordinator Agent + Agent-as-tool 模式

- **AI used:** Claude Code
- **Prompt summary:** 实现 coordinator.py，用 AG2 Beta 创建 Coordinator agent，将 Inventory 作为 tool 注册
- **AI output (excerpt):** 使用 `Agent.as_tool()` 暴露 `consult_inventory` 工具，Coordinator 通过 tool 调用 Inventory Agent
- **Verification:** 冒烟测试验证 agent 可创建、工具注册正常；实机测试 A 类库存查询返回正确结果
- **Adopted?** ✅
- **What I changed manually and why:** 上线后发现 `Agent.tools` 是 list 而非 set，将 `.add()` 改为 `.append()`

### Iteration 5 — CLI 入口和交互式 REPL

- **AI used:** Claude Code
- **Prompt summary:** 实现 main.py CLI 入口，读取 .env 配置，启动 REPL 交互循环
- **AI output (excerpt):** 支持通过 `OpenAIConfig` 配置 API、交互式问答、quit 退出
- **Verification:** `python main.py` 启动正常，输入测试问题得到 agent 回复
- **Adopted?** ✅
- **What I changed manually and why:** 将 `GeminiConfig` 替换为 `OpenAIConfig`（阿里云 DashScope 使用 OpenAI 兼容接口）

### Iteration 6 — 完善文档和提交清单

- **AI used:** Claude Code
- **Prompt summary:** 按照 C5-AG2 PDF 清单检查并完善 README、AI_LOG、ATTRIBUTION，添加 LICENSE 和 prompts/ 目录
- **AI output (excerpt):** 更新 README 增加 tagline、预期输出、故障排查；完善 AI_LOG 和 ATTRIBUTION 各字段
- **Verification:** 文件格式正确，所有测试通过（8/8）
- **Adopted?** ✅
- **What I changed manually and why:** 无修改

### Iteration 7 — API 配置和实机测试

- **AI used:** Claude Code
- **Prompt summary:** 配置阿里云百炼 DashScope API，测试完整 Agent 协作链路
- **AI output (excerpt):** 使用 qwen-plus 模型通过 DashScope OpenAI 兼容接口成功运行
- **Verification:** 测试查询 "A类仓库有哪些商品？" 得到正确结构化回复
- **Adopted?** ✅
- **What I changed manually and why:** 配置 .env 文件

## Manual steps & justification / 手动步骤反向举证

| Step | Why manual? |
|------|-------------|
| 注册 API Key（阿里云百炼） | 账户绑定，AI 不应接触私密信息 |
| 录制 60-90 秒 demo 视频 | 需要真人语音和屏幕操作 |
| git push | SSH 认证绑定 |

## Self-audit / 自审

- [x] At least 5 iterations documented (7 iterations)
- [x] Each iteration has a verification step
- [x] Each manual step has a justification
- [x] No API keys leaked into this log
- [x] No private personal info leaked into this log

## What I would do differently next time / 下次改进

下次可以在项目初期就确定好 API 提供商（如阿里云百炼），避免在 GeminiConfig 和 OpenAIConfig 之间反复切换。另外可以提前规划好 prompts/ 目录，将 agent 提示词外置化，便于调试和迭代。
