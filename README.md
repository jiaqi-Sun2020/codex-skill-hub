# Codex Skill Hub

[中文](README.md) | [English](README.en.md)

`codex-skill-hub` 是可复用 Codex Skill 的中央源码与版本治理仓库。本文档重点说明**实际收录在本仓库中的 8 个活动 Skill**及其配套基础设施；独立维护在 S Paper Skills 和 PaperTrace 中的 Skill 仅在文末提供概览与入口。

截至 2026-09-13，本仓库包含：

- 8 个直接维护的活动 Skill；
- 1 套整合在 `50-core-utils/skill-registry/` 下的版本注册基础设施；
- 两个外部 Skill 项目的轻量索引，不复制它们的项目专属源码。

> 本仓库公开的是可复用指令、脚本、测试、模板和文档。论文原文、实验数据、学习画像、会话记录、凭据和机器本地状态不属于公开内容。

## 快速开始

```powershell
git clone https://github.com/jiaqi-Sun2020/codex-skill-hub.git
Set-Location .\codex-skill-hub
```

使用某个 Skill 时，可以让 Codex 读取对应目录中的 `SKILL.md`，也可以把整个 Skill 目录安装到自己的 Skill 搜索路径。不要只复制 `SKILL.md`：相关 `scripts/`、`references/`、`assets/` 和 `templates/` 也可能属于执行契约。

## 本仓库结构

```text
codex-skill-hub/
|-- README.md / README.en.md
|-- .agents/                         项目上下文与长期知识
|-- .codex/                          项目级 Codex 启动 Hook
|-- 10-paper-build/
|   `-- academic-figure-workflow/    学术图工作流
|-- 50-core-utils/
|   |-- project-agent-generator-skill/
|   |-- research-project-pipeline/
|   |-- research-workspace-governance/
|   |-- skill-audit-refactor/
|   |-- training-code-architecture-skill/
|   |-- neat-freak/
|   `-- skill-registry/              版本注册基础设施，不计为活动 Skill
`-- 90-personal/
    `-- logic-chain-tutor/
```

## 如何选择本仓库中的 Skill

| 你的目标 | 使用的 Skill |
|---|---|
| 制作论文图、模型架构图、多面板图或可编辑 PPT 图件 | `academic-figure-workflow` |
| 为项目生成 `.agents/`、长期知识入口和 Codex 启动加载 | `project-agent-generator-skill` |
| 完整接入或迁移一个新旧研究项目 | `research-project-pipeline` |
| 设计研究目录、证据生命周期、来源追踪和归档规则 | `research-workspace-governance` |
| 审核、精简、拆分或重构一个已有 Skill | `skill-audit-refactor` |
| 把机器学习脚本重构为可复用、配置驱动的训练工程 | `training-code-architecture` |
| 维护 `.agents/memory/` 并审计项目知识和启动加载 | `neat-freak` |
| 从当前知识卡点开始逐步学习概念或公式 | `logic-chain-tutor` |

## 1. 学术图工作流

### `academic-figure-workflow`

**适用领域**

用于论文、学位论文和研究报告中的正式图件，包括机制示意图、神经网络或系统架构图、真实数据图、多面板组合图、可编辑 PowerPoint 图件、图注和投稿前视觉质量检查。

**什么时候使用**

- 需要根据论文论点和证据规划整套图，而不只是“画得好看”；
- 需要把参考图的视觉语言迁移到自己的内容，同时避免复制其科学内容；
- 需要 Draw.io、SVG、Matplotlib、PDF、PNG 或 PPTX 等可编辑、可复现交付物；
- 需要检查最终尺寸下的字体、线宽、图例、标记、颜色、面板布局和可访问性；
- 需要让图、图注、数据、代码和论文 claim 保持可追溯关系。

**典型输入与输出**

- 输入：论文段落、模型代码、数据表、公式、草图、参考图、目标期刊和最终尺寸；
- 输出：可编辑源文件、SVG/PDF/PNG 导出、PPT 图件、`caption.md`、样式清单、证据追踪和渲染 QA 结果。

**关键边界**

它不会虚构数据、单位、误差、机制或模型模块。数据型图表先核对数据和不确定性来源；复杂图件在最终尺寸渲染后才可视为完成。

**调用示例**

> 根据模型代码和论文方法段制作一张可编辑的 Draw.io 神经网络架构图，并验证每条连线。

> 把 CSV 实验结果制作成 Nature 风格多面板图，同时输出可编辑 PPT、图注和最终尺寸 QA。

源码：[`10-paper-build/academic-figure-workflow/`](10-paper-build/academic-figure-workflow/)

## 2. 中央核心工具

### `project-agent-generator-skill`

**适用领域**

为陌生或长期维护的代码仓库生成项目级 Agent 上下文，使 Codex 能从经过验证的仓库事实中了解项目结构、命令、配置、决策和安全边界。

**主要能力**

- 生成或安全刷新 `.agents/` 文档包；
- 初始化 `.agents/memory/` 长期知识索引；
- 安装项目级 `.codex/` Hook，让 `.agents/AGENTS.md` 在启动和恢复时被加载；
- 刷新旧文档时保留人工内容，并在强制刷新前创建恢复备份；
- 拒绝项目外路径、链接目标和疑似凭据内容。

**典型输出**

`AGENTS.md`、`PROJECT_CONTEXT.md`、`ARCHITECTURE.md`、`CONFIG_SPEC.md`、`RUNBOOK.md`、`DECISIONS.md`、文档索引、长期知识基线和项目启动 Hook。

**调用示例**

> 扫描这个仓库并生成项目级 `.agents` 上下文；先预览写入位置，不修改业务代码。

> 刷新已有 Agent 文档，保留人工确认的架构、命令和长期知识。

源码：[`50-core-utils/project-agent-generator-skill/`](50-core-utils/project-agent-generator-skill/)

### `research-project-pipeline`

**适用领域**

用于新研究项目初始化或遗留研究项目接入。当任务同时涉及目录治理、迁移、Agent 上下文、知识审计和最终验收时，由它编排完整流水线。

**主要能力**

- 先做只读发现，区分事实、风险和待确认事项；
- 调用研究工作区治理规则设计目标结构；
- 生成可审核、可回滚的迁移方案；
- 创建或保留项目 Agent 上下文；
- 执行知识、启动加载和对抗性验收。

**与相邻 Skill 的区别**

- 只需要生成 `.agents/`：使用 `project-agent-generator-skill`；
- 只需要设计研究目录和证据规则：使用 `research-workspace-governance`；
- 两者都需要，并且还包括迁移和交接：使用本 Skill。

**调用示例**

> 把这个遗留研究项目接入统一工作流：先只读盘点，再给出迁移计划，确认后执行。

> 为新课题建立从工作区结构、Agent 上下文到对抗验收的完整流水线。

源码：[`50-core-utils/research-project-pipeline/`](50-core-utils/research-project-pipeline/)

### `research-workspace-governance`

**适用领域**

治理研究工作区的生命周期，重点解决原始证据、派生产物、临时文件、最终交付物混杂，以及实验结果无法追溯的问题。

**主要能力**

- 定义 `source / derived / intermediate / final / temporary` 等产物角色；
- 建立数据、配置、代码、运行记录、图表和论文 claim 之间的追踪链；
- 设计实验隔离、命名、保留、归档和清理规则；
- 在迁移或清理前保护不可变证据，并提供失败安全策略；
- 审核项目是否具备复现和交接条件。

**边界**

它负责研究工作区与证据治理，不替代科学方法设计、训练代码架构、Skill 重构或一般桌面文件整理。

**调用示例**

> 设计一个不会混淆原始数据、处理结果和论文终稿的研究目录，并说明每类文件的生命周期。

> 审计现有实验结果能否追溯到数据、配置、代码版本和运行记录。

源码：[`50-core-utils/research-workspace-governance/`](50-core-utils/research-workspace-governance/)

### `skill-audit-refactor`

**适用领域**

审核和重构已有 Codex Skill，尤其适合处理触发描述模糊、正文过长、职责过宽、资源重复、缺少验证或安全边界不清的问题。

**主要能力**

- 审核 frontmatter、触发条件、正文、脚本、引用、模板和 Agent 元数据；
- 区分必须保留、可以压缩、应移入引用和应删除的内容；
- 判断 Skill 应保持单体、拆分子 Skill，还是仅拆分资源；
- 在不损失关键能力和安全规则的前提下减小上下文成本；
- 提供重构前后验证和风险说明。

**调用示例**

> 审核这个 Skill 是否过长、过宽或容易误触发，先给出分级问题和重构计划。

> 把条件性细节移到 `references/`，但保留所有安全门和输出质量契约。

源码：[`50-core-utils/skill-audit-refactor/`](50-core-utils/skill-audit-refactor/)

### `training-code-architecture`

**适用领域**

把已有机器学习训练代码提炼成可复用工程架构。它保留的是执行框架和接口，而不是某个数据集、模型或任务的专用逻辑。

**主要能力**

- 建立轻量 `main.py → train(args)` 入口；
- 使用 JSON 配置组织实验、数据、模型、训练、任务和输出；
- 通过 factory 隔离模型、优化器、调度器和组件构建；
- 通过 `TaskAdapter` 隔离批处理、图结构、模型调用、损失和指标；
- 统一 checkpoint、日志、配置副本、历史记录和最终指标；
- 用同一训练框架适配静态图、动态图、序列或其他任务。

**关键边界**

示例项目中的固定张量形状、数据预处理、图结构、损失函数和模型名不会被误当成通用架构硬编码。

**调用示例**

> 根据现有训练脚本生成配置驱动的可复用模板，保留 `main.py → train(args)` 工作流。

> 用 adapter 隔离任务逻辑，使同一训练引擎同时支持静态图和动态图实验。

源码：[`50-core-utils/training-code-architecture-skill/`](50-core-utils/training-code-architecture-skill/)

### `neat-freak`

**适用领域**

维护项目本地的 Markdown 长期知识与 Agent 文档，避免 `.agents/memory/`、README、架构说明和实际代码之间出现重复、冲突或过时内容。

**主要能力**

- 只读审计知识索引、主题文件、项目文档和来源关系；
- 初始化缺失的知识基线，但不覆盖已有内容；
- 通过哈希绑定的 `plan → apply` 流程安全更新长期知识；
- 审核 `.agents/AGENTS.md` 与项目级 Codex Hook 是否正确加载；
- 合并重复知识、修复索引并准备可复用的项目交接信息。

**关键边界**

“audit / check / review” 默认只读；只有明确要求初始化、同步、修复或维护时才写入。

**调用示例**

> 审计 MEMORY 索引、主题文件和项目文档是否冲突，不要修改文件。

> 为这项长期决策生成哈希绑定的更新计划，审核通过后再应用。

源码：[`50-core-utils/neat-freak/`](50-core-utils/neat-freak/)

## 3. 个人教学 Skill

### `logic-chain-tutor`

**适用领域**

从学习者当前卡住的逻辑环节开始讲解陌生概念、数学公式、物理意义或论文方法，适合“是什么、为什么、怎么来、这两个有什么区别”等需要建立理解链的问题。

**主要能力**

- 判断真正缺失的前置知识，而不是机械地从整门课程开头重讲；
- 给出“已知锚点 → 缺失桥梁 → 目标概念 → 应用”的逻辑地图；
- 逐步解释符号的类型、形状、操作和物理含义；
- 使用最小完整例子、反例和概念对比修复误解；
- 遵守“简短解释、只给提示词、局部改写”等输出长度契约。

**边界**

简单事实查询或纯执行任务不应触发它。它提供当前对话中的适应性教学，不自动修改外部学习画像。

**调用示例**

> 我忘了线性代数基础，请从特征向量开始解释图卷积，每一步说明为什么成立。

> 区分量子态、算符、特征值和测量结果，并用一个最小例子说明它们不能互换的原因。

源码：[`90-personal/logic-chain-tutor/`](90-personal/logic-chain-tutor/)

## Skill Registry 基础设施

[`50-core-utils/skill-registry/`](50-core-utils/skill-registry/) 是整合在本仓库中的版本治理工具，不是第 9 个活动 Skill，也不再作为独立仓库发布。

| 路径 | 用途 |
|---|---|
| `registry.json` | 记录受治理 Skill 的版本和校验信息 |
| `sources/` | 可编辑的中央源码 |
| `releases/` | 已发布的不可变快照 |
| `tools/skill_registry.py` | 检查、发布和同步工具 |
| `tests/` | Registry 行为测试 |

Registry 支持两种项目关系：

- `vendored`：项目消费锁定的中央版本；
- `forked`：项目拥有自己的实现，中央同步不得覆盖。

当前保留的中央 `reader-learner 1.0.0` 是可追溯的历史发布。PaperTrace 的现行 `reader-learner` 已是项目专属 fork，不应从这里直接覆盖。

## 常见组合流程

```text
科研项目治理
research-workspace-governance
  → project-agent-generator-skill
  → neat-freak
  → research-project-pipeline（需要完整编排时）

机器学习工程
现有代码 → training-code-architecture → 可复用训练模板

论文图件
论文 claim / 代码 / 数据 → academic-figure-workflow → 可编辑源文件 + 导出 + QA

概念学习
当前卡点 → logic-chain-tutor → 前置桥梁 → 推导 / 例子 / 验证
```

## 外部 Skill 项目概览

以下 Skill 不在本仓库中维护。这里仅提供导航；完整说明、最新脚本和项目约束请以对应仓库为准。

| 外部仓库 | 大致用途 | 包含的 Skill |
|---|---|---|
| [S Paper Skills](https://github.com/jiaqi-Sun2020/S_paper_skills) | 科研逻辑、实验设计、数据分析、LaTeX 建稿、论文润色和期刊适配 | `research-logic`、`experiment-design`、`data-analysis`、`research-html-report`、`latex-paper-build-skill`、`paper-polishing-skill`、`interactive-skill-builder`、`prl-manuscript-polisher` |
| [PaperTrace](https://github.com/jiaqi-Sun2020/PaperTrace/tree/main/skills) | 论文证据抽取、双语阅读器、学习画像、教学、资讯简报和 HTML 展示 | `nature-reader`、`reader-skill`、`reader-learner`、`adaptive-teach`、`allegory-teach`、`chat-knowledge-profile`、`ai-quantum-news-briefing`、`demo-skill`、`lean-html-skill` |

外部 Skill 应从各自仓库获取，不要因为本 README 提供索引就复制到本仓库。

## 致谢与借鉴

感谢以下开源 Skill 的作者和维护者。本仓库中能够明确追溯的 Skill 级借鉴主要集中在 `academic-figure-workflow`；相关本地实现经过重新组织和扩展，致谢不表示原作者对本项目背书。

- [`nature-figure`](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure)，来自 Yuan1z0825 维护的 `nature-skills`（Apache-2.0）。本仓库借鉴了以论文论点组织多面板信息、语义配色、可编辑 SVG 和投稿前 QA 的设计思想。
- [`scipilot-figure-skill`](https://github.com/Haojae/scipilot-figure-skill)，由 Haojae 维护（MIT）。本仓库借鉴了“先理解数据和论证目标，再选图”的可视化顾问思路，以及对常见科研作图反模式的主动拦截。

同时感谢 Nature、PLOS、Springer Nature、Elsevier、IEEE、ACM、SIGACCESS 和 JCB 公开的作者与图件规范；这些规范为本仓库的出版质量、可访问性和导出检查提供了标准依据。具体来源链接记录在 [`publisher-visual-source-map.md`](10-paper-build/academic-figure-workflow/references/publisher-visual-source-map.md)。

如果后续 Skill 明确借鉴新的开源 Skill，应在合并时同步补充作者、项目链接、借鉴范围和许可证，而不是只在提交信息中留下记录。

## 验证

以下命令均从仓库根目录运行：

```powershell
Set-Location C:\path\to\codex-skill-hub

python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\50-core-utils\<skill-folder>"

python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"

python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit
```

## 维护与许可

1. 每个 Skill 只保留一个正式源码位置。
2. 外部项目专属 Skill 留在对应项目，不在本仓库制造副本。
3. 不直接编辑 Registry 中的不可变 `releases/`；升级时创建新版本。
4. 推送前检查差异、测试、敏感信息、机器路径和许可证兼容性。
5. 不公开论文原文、实验数据、学习画像、会话记录或凭据。

每个 Skill 和外部仓库保留自己的来源与许可边界。在逐项确认兼容性前，本仓库暂不应用覆盖全部内容的统一许可证。
