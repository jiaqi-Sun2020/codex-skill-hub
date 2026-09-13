# Codex Skill Hub

[中文](README.md) | [English](README.en.md)

`codex-skill-hub` 是面向 Codex 与兼容 Agent 的 Skill 中央源码、导航和版本治理仓库。它直接维护通用研究工具、学术图工作流和个人教学 Skill，同时为独立维护的 [S Paper Skills](https://github.com/jiaqi-Sun2020/S_paper_skills) 与 [PaperTrace](https://github.com/jiaqi-Sun2020/PaperTrace) 提供统一索引。

截至 2026-09-13，本目录索引 **25 个活动 Skill**：本仓库直接维护 8 个，S Paper Skills 维护 8 个，PaperTrace 维护 9 个。`skill-registry` 是版本治理基础设施，不单独计为 Skill。

> 本仓库公开的是可复用指令、脚本、测试、模板和文档。论文原文、实验数据、学习画像、会话记录、凭据和机器本地状态不属于公开内容。

## 快速开始

```powershell
git clone https://github.com/jiaqi-Sun2020/codex-skill-hub.git
cd codex-skill-hub
```

使用本仓库直接维护的 Skill 时，把对应 `SKILL.md` 路径交给 Codex，或将该 Skill 目录安装到 Skill 搜索路径。S Paper Skills 与 PaperTrace 的项目专属 Skill 应从它们各自的仓库获取，不要复制进本仓库。

## 仓库结构

```text
codex-skill-hub/
|-- README.md / README.en.md
|-- .agents/                         Agent 上下文与长期知识入口
|-- .codex/                          项目级 Codex 启动 Hook
|-- 10-paper-build/
|   `-- academic-figure-workflow/    学术图正式源码
|-- 50-core-utils/
|   |-- project-agent-generator-skill/
|   |-- research-project-pipeline/
|   |-- research-workspace-governance/
|   |-- skill-audit-refactor/
|   |-- training-code-architecture-skill/
|   |-- neat-freak/
|   `-- skill-registry/              已整合的共享版本注册中心
`-- 90-personal/
    `-- logic-chain-tutor/
```

## 如何选择 Skill

| 目标 | 首选 Skill |
|---|---|
| 判断研究想法是否形成机制级贡献 | `research-logic` |
| 把想法变成可审稿的实验方案 | `experiment-design` |
| 分析实验结果及统计证据 | `data-analysis` |
| 构建、拆分或交付 LaTeX 论文 | `latex-paper-build-skill` |
| 制作论文图、架构图和多面板图 | `academic-figure-workflow` |
| 生成项目级 Agent 上下文 | `project-agent-generator-skill` |
| 治理完整研究工作区 | `research-workspace-governance` |
| 审核或精简现有 Skill | `skill-audit-refactor` |
| 阅读论文并生成双语阅读器 | `nature-reader` → `reader-skill` |
| 维护个人阅读知识画像 | `reader-learner` |
| 从当前卡点逐步学习陌生概念 | `logic-chain-tutor` |

## 论文与研究构建 Skill（9 个）

以下 8 个 Skill 由 [S Paper Skills](https://github.com/jiaqi-Sun2020/S_paper_skills) 维护；`academic-figure-workflow` 的正式源码位于本仓库。

### `research-logic`

- **领域：** 方法融合、机制分析、论文创新性判断、克制的贡献表述。
- **输出：** 浅层拼接诊断、机制级连接、状态/转移逻辑和可验证 claim。
- **示例：** “分析 CTQW 与动态图网络是否形成机制级结合，而不是模块拼接。”；“把这个模型贡献改写成证据边界明确的论文 claim。”
- **源码：** `S_paper_skills/research-logic-skill/`。

### `experiment-design`

- **领域：** 机器学习、图学习、物理启发模型和方法论文的实验设计。
- **输出：** 研究问题、假设、数据集、基线、消融、指标、机制检查和失败案例。
- **示例：** “为动态图模型设计能回答三条核心 claim 的实验矩阵。”；“补齐基线、消融和统计检验，使方案达到论文评审标准。”
- **源码：** `S_paper_skills/experiment-design-skill/`。

### `data-analysis`

- **领域：** CSV/JSON/NPZ、训练日志、重复实验和论文结果的统计分析。
- **输出：** 完整性检查、显著性检验、效应量、置信区间和结果解释。
- **示例：** “比较五个模型跨 seed 的均值、95% 置信区间和效应量。”；“检查现有结果是否足以支撑性能提升声明。”
- **源码：** `S_paper_skills/data-analsys-skill/`；目录拼写为兼容历史暂未调整。

### `research-html-report`

- **领域：** 研究简报、论文规划页、机制说明和可打印的学术 HTML。
- **输出：** 带图、表、公式、引用和风险边界的独立 HTML 报告。
- **示例：** “把研究逻辑和实验计划整理成可分享的 HTML research brief。”；“生成包含公式、消融表和逐图解释的论文风格网页。”
- **源码：** `S_paper_skills/util_skills/research-html-report/`。

### `latex-paper-build-skill`

- **领域：** LaTeX 论文搭建、单体文稿拆分、REVTeX/ctex、BibTeX 和投稿检查。
- **输出：** 可编译论文框架、统一 `figures/` 与 `.bib` 管理、构建和交付检查结果。
- **示例：** “把这个单体 `main.tex` 拆成可维护的章节结构并保持标签不变。”；“为 QCT 论文建立 REVTeX 工程并检查图片、引用和编译链。”
- **源码：** `S_paper_skills/latex-paper-build-skill/`。

### `paper-polishing-skill`

- **领域：** 作者审核后的中英翻译、Nature/PRL/PRA 风格润色和论证结构修订。
- **输出：** 保留公式、标签、引用和事实边界的英文终稿或修改说明。
- **示例：** “在不改变 claim 的前提下，把已审核中文结果段翻译成 PRL 风格英文。”；“检查全文重复数值是否与主表一致并压缩引言。”
- **边界：** 不在作者确认科学内容前擅自生成最终英文版本。
- **源码：** `S_paper_skills/paper-polishing-skill/`。

### `interactive-skill-builder`

- **领域：** 通过访谈把重复工作流沉淀成 Codex Skill。
- **输出：** 经确认的 Skill 规格、目录结构、资源计划、实现和验证记录。
- **示例：** “通过逐步访谈帮我把实验复盘流程做成 Skill。”；“先审核触发条件和输出契约，再更新现有 Skill。”
- **源码：** `S_paper_skills/util_skills/interactive-skill-builder/`。

### `prl-manuscript-polisher`

- **领域：** Physical Review Letters 稿件适配、压缩、证据审计和 REVTeX 一致性。
- **输出：** PRL fit 审计、逐段修订、字数预算、claim-evidence 检查和投稿清单。
- **示例：** “审计这篇稿件是否适合 PRL，并列出最影响编辑判断的三处问题。”；“在保持物理含义的前提下压缩摘要和引言。”
- **源码：** `S_paper_skills/util_skills/prl-manuscript-polisher/`。

### `academic-figure-workflow`

- **领域：** 学术机制图、神经网络架构图、真实数据绘图、多面板组装和投稿图 QA。
- **输出：** 可编辑 SVG/Draw.io/PPT、可复现图表、图注、证据追踪和最终尺寸检查。
- **示例：** “根据模型代码制作可编辑的神经网络架构图并验证连线。”；“把实验数据做成 Nature 风格多面板图，附图注和最终尺寸可读性检查。”
- **源码：** [`10-paper-build/academic-figure-workflow/`](10-paper-build/academic-figure-workflow/)。

## 中央核心工具（6 个）

### `project-agent-generator-skill`

- **领域：** 陌生项目接手、Agent onboarding、长期知识入口和项目级 Codex 启动加载。
- **输出：** `.agents/` 文档、`AGENTS.md` 入口、记忆索引和安全的项目 Hook。
- **示例：** “扫描这个仓库并生成项目级 Agent 上下文，但不要改业务代码。”；“安全刷新已有 `.agents`，保留人工确认的长期知识。”
- **源码：** [`50-core-utils/project-agent-generator-skill/`](50-core-utils/project-agent-generator-skill/)。

### `research-project-pipeline`

- **领域：** 新旧研究项目的完整接入、迁移、治理和交接。
- **输出：** 只读发现结果、工作区设计、迁移方案、Agent 上下文、知识审计和对抗验收。
- **示例：** “把这个遗留研究项目接入统一工作流，先盘点再迁移。”；“为新课题建立从目录治理到 Agent 交接的完整流水线。”
- **源码：** [`50-core-utils/research-project-pipeline/`](50-core-utils/research-project-pipeline/)。

### `research-workspace-governance`

- **领域：** 研究项目目录、证据生命周期、来源追踪、归档与清理策略。
- **输出：** SOURCE/derived/intermediate/final/temporary 边界、产物清单和可复现政策。
- **示例：** “设计一个不会混淆原始数据和生成结果的研究目录。”；“审计实验产物能否追溯到配置、代码和数据来源。”
- **源码：** [`50-core-utils/research-workspace-governance/`](50-core-utils/research-workspace-governance/)。

### `skill-audit-refactor`

- **领域：** Skill 触发质量、上下文成本、资源拆分和安全边界审核。
- **输出：** 问题分级、精简方案、拆分建议和保持能力的重构结果。
- **示例：** “审核这个 Skill 是否过长、过宽或容易误触发。”；“把条件性细节移到 references，同时保持原有能力。”
- **源码：** [`50-core-utils/skill-audit-refactor/`](50-core-utils/skill-audit-refactor/)。

### `training-code-architecture`

- **领域：** 可复用机器学习训练工程、配置驱动实验和多任务适配。
- **输出：** `main.py → train(args)` 薄入口、factory、adapter、checkpoint、日志和结果契约。
- **示例：** “把现有训练脚本重构成配置驱动且可复现实验的结构。”；“保留训练框架，用 adapter 同时支持静态图和动态图任务。”
- **源码：** [`50-core-utils/training-code-architecture-skill/`](50-core-utils/training-code-architecture-skill/)。

### `neat-freak`

- **领域：** `.agents/memory/`、项目文档、知识去重和 Codex 启动加载审计。
- **输出：** 只读审计、哈希绑定更新计划、知识同步和 bootstrap 验证。
- **示例：** “检查 MEMORY 索引、主题文件和项目文档是否冲突。”；“为这次长期决策生成可审核的 plan，再显式应用。”
- **源码：** [`50-core-utils/neat-freak/`](50-core-utils/neat-freak/)。

## PaperTrace Skill（9 个）

这些 Skill 由 [PaperTrace](https://github.com/jiaqi-Sun2020/PaperTrace/tree/main/skills) 独立维护，并按项目专属 `forked` 模式登记。

### `adaptive-teach`

- **领域：** 基于学习画像的诊断、教学、复习和迁移练习。
- **输出：** 单主题学习决策、短课、诊断题和可验证的教学反馈交接。
- **示例：** “根据我的学习画像选择下一个最需要补的概念。”；“安排一次到期复习，并用真实答题证据判断是否掌握。”

### `ai-quantum-news-briefing`

- **领域：** AI、量子科技、论文、模型发布、政策和产业动态简报。
- **输出：** 有来源依据的简报、概念寓言、交互式 HTML 和反馈 JSON。
- **示例：** “生成近三天 AI 与量子计算的重要进展简报。”；“把今日快报制作成可反馈的交互式 HTML。”

### `allegory-teach`

- **领域：** 用中文寓言直观讲解一个高级技术概念。
- **输出：** 延迟揭示概念名的因果故事、定义、类比边界、误解提示和映射表。
- **示例：** “从我的研究边界选一个概念，用不先说名称的寓言解释。”；“用故事解释量子纠错，并明确类比在哪些地方会失效。”
- **边界：** 不修改学习画像，不负责新闻收集或课程状态管理。

### `nature-reader`

- **领域：** 从 PDF、DOI、arXiv、出版商网页或文本构建可追溯的双语论文证据层。
- **输出：** 原文锚点、翻译、公式/图表抽取、来源映射和 reader bundle。
- **示例：** “读取这篇论文并建立逐段中英对照与来源锚点。”；“抽取全部图表和公式，保留页码及证据映射。”

### `reader-skill`

- **领域：** 将论文证据包转换为独立、可交互的中英双语阅读器。
- **输出：** HTML 阅读器、忠实翻译检查、学习标注元数据和反馈导出。
- **示例：** “把这个 `paper_reader` 目录制作成浏览器可用的双语阅读器。”；“审核阅读器是否覆盖全文并能正确导出反馈。”

### `reader-learner`

- **领域：** 阅读、资讯和教学反馈导入、学习画像维护和可见知识 Wiki。
- **输出：** 经验证的知识状态、事件、来源、复习队列和 Obsidian 页面。
- **示例：** “导入 reader_feedback.json 并同步可见 Wiki。”；“列出正在学习和需要复习的概念，不要直接改画像文件。”
- **版本说明：** 中央 registry 保留通用 `1.0.0` 历史发布；PaperTrace 当前实现因聊天画像和 reader-v3 接口已转为项目专属 fork。

### `chat-knowledge-profile`

- **领域：** 从本地 ChatGPT、Claude、DeepSeek 等会话导出中提取可审核的学习信号。
- **输出：** 有界事件、会话摘要、候选画像信号和人工审核后的更新补丁。
- **示例：** “从这些聊天导出中提取我经常卡住的概念，但先不要修改画像。”；“生成可审核的 profile patch，并标明每条证据来源。”

### `demo-skill`

- **领域：** 从已验证的 README 和 Agent 契约生成双语项目演示页。
- **输出：** 中文/英文 HTML demo、项目流程叙事、交互效果和发布前审计。
- **示例：** “基于当前 README 生成四条项目流水线的双语演示页。”；“审核 demo 是否与仓库事实一致并修复错误描述。”

### `lean-html-skill`

- **领域：** PaperTrace 的共享 HTML 外壳、视觉系统和反馈导出组件。
- **输出：** 内嵌 CSS/JS、交互式反馈面板、复制/下载 JSON 和统一页面样式。
- **示例：** “为论文阅读器添加统一的反馈导出面板。”；“把简报 HTML 重构为共享外壳，避免复制样式和脚本。”

## 个人 Skill（1 个）

### `logic-chain-tutor`

- **领域：** 前置知识诊断、逐步推导、概念辨析、物理意义和论文方法教学。
- **输出：** 从当前卡点开始的逻辑链、小例子、误解修复和适配长度的解释。
- **示例：** “我忘了线性代数基础，请从特征向量开始解释图卷积。”；“逐步推导这个公式，区分数学对象、操作和信息载体。”
- **边界：** 简短事实查询或纯执行任务不需要触发该 Skill。
- **源码：** [`90-personal/logic-chain-tutor/`](90-personal/logic-chain-tutor/)。

## 推荐工作流

```text
研究想法 → research-logic → experiment-design → training-code-architecture
        → data-analysis → academic-figure-workflow → research-html-report
        → latex-paper-build-skill → paper-polishing-skill / prl-manuscript-polisher

论文学习 → nature-reader → reader-skill → reader-learner
        → adaptive-teach / allegory-teach

项目治理 → research-workspace-governance → project-agent-generator-skill
        → neat-freak → research-project-pipeline（需要完整编排时）
```

## Skill Registry

`50-core-utils/skill-registry/` 管理必须以锁定副本进入项目的共享 Skill：

- `sources/`：可编辑中央源码。
- `releases/`：不可变发布快照。
- `forked`：项目拥有实现，不受中央覆盖。
- `vendored`：项目使用中央发布的锁定副本。

PaperTrace 当前的 9 个 Skill 均登记为项目专属 `forked`；中央 `reader-learner 1.0.0` 仅保留为可追溯历史发布。

## 验证

从仓库根目录运行：

```powershell
python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\50-core-utils\<skill-folder>"
python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"
python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit
```

## 维护与许可证

1. 每个 Skill 只有一个正式源码位置；项目专属 Skill 留在原仓库。
2. 不直接修改不可变 `releases/`；需要升级时创建新版本。
3. 推送前检查暂存区、测试、敏感信息和许可证。
4. 不公开论文、实验数据、学习画像、会话记录或凭据。

各 Skill 和外部仓库保留自己的许可证与来源说明。在逐项确认兼容性前，本仓库不以一个总许可证覆盖全部内容。
