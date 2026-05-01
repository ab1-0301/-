# 仓库分析：neoskills

## 1. 这个仓库是做什么的？（一句话）
neoskills 是一个类似 Homebrew 的技能管理器，用来管理 AI Agent 的技能包，让 AI 能像安装软件一样装“技能”[reference:0]。

## 2. 仓库的目录结构是怎样的？
根据 `README.md` 的描述，它的工作区结构是这样的：

- `~/.neoskills/` – 工作区根目录
- `├── config.yaml` – 全局配置文件
- `├── taps/` – 存放所有技能仓库（源）
- │   └── mySkills/ – 默认技能仓库
- │       └── skills/ – 存放具体技能的文件夹
- │           └── <skill-name>/ – 具体的某个技能目录
- │               ├── SKILL.md – 技能的核心定义文件
- │               ├── ontology.yaml – 技能知识图谱的元数据
- │               ├── scripts/ – 可执行脚本
- │               ├── references/ – 辅助参考文档
- │               └── assets/ – 媒体或模板资源
- └── cache/ – 备份和临时文件

源码的主要项目结构则如下：
- `src/neoskills/` – 项目的主要源代码目录
-   ├── cli/ – 命令行接口实现，例如 `neoskills list`
-   ├── core/ – 核心功能模块，包含配置、链接管理
-   └── ontology/ – 知识图谱逻辑层，用来分析技能之间的关系
技能名称	作用	输入	输出
bank-status	查询 neoskills 技能库的状态和清单。	分析当前所有技能，包括它们的数量、标签、更新时间、不同目标端的技能数量等。	一份包含以下内容的总结报告。
skill-dedup	检查并清理 neoskills 技能仓库和多处目标端中的重复技能。	一组提示词，用于处理重复对象的合并、移除或保留的决策指令。	一个更干净、无冗余的技能集合。
