# Codex Skill Hub

[中文](README.md) | [English](README.en.md)

`codex-skill-hub` 是可复用 Codex Skill 的中央源码与导航仓库。它把项目治理、论文交付、跨项目工具和个人教学能力分开维护，使每项能力只有一个正式源码位置，同时让使用者能够从一个简洁入口找到正确流程。

本仓库当前直接维护 20 个活动 Skill：`10-paper-build` 9 个、`20-project-build` 6 个、`50-core-utils` 4 个、`90-personal` 1 个。版本注册基础设施、外部项目快捷入口、暂存区和归档区不计入活动 Skill。

> 仓库可以公开可复用指令、脚本、测试、模板和文档。论文原文、实验数据、学习画像、会话记录、凭据、令牌及机器私有状态不属于公开内容。

## 整体框架

```text
首次项目接入与持续治理 ──→ 20-project-build
研究成果到论文交付       ──→ 10-paper-build
跨项目维护与质量工具     ──→ 50-core-utils
个人学习与教学           ──→ 90-personal
外部与兼容入口           ──→ 30-papertrace / 40-skill-registry
待审核与历史材料         ──→ 98-inbox / 99-archive
```

三层文档各有唯一职责：

1. 本 README 解释仓库级框架、分类和入口选择。
2. 编号分类 README 解释本分类的组件、流程、边界与验证方法。
3. 每个 Skill 的 `SKILL.md` 是正式执行契约；README 不复制其完整规则。

## 分类导航

| 分类 | 性质 | 用途 | 详细说明 |
|---|---|---|---|
| `10-paper-build` | 活动源码 | 从研究逻辑、证据设计和分析走向图件、中文稿、审核与投稿 | [论文构建框架](10-paper-build/README.md) |
| `20-project-build` | 活动源码 | 项目首次接入、治理合同、持续研究管理、协议审核和提交审计 | [项目构建框架](20-project-build/README.md) |
| `30-papertrace` | 外部导航 | 指向 PaperTrace 项目拥有的阅读、教学和资讯 Skill | [PaperTrace 入口](30-papertrace/README.md) |
| `40-skill-registry` | 兼容导航 | 指向仓库内唯一 Skill Registry 源码 | [Registry 入口](40-skill-registry/README.md) |
| `50-core-utils` | 活动源码与基础设施 | 项目信息维护、交接、Skill 审计、训练代码架构和版本治理 | [核心工具](50-core-utils/README.md) |
| `90-personal` | 活动源码 | 面向个人学习方式的教学 Skill | [个人 Skill](90-personal/README.md) |
| `98-inbox` | 未审核暂存 | 保存尚未批准应用的补丁、计划和候选文档 | [暂存规则](98-inbox/README.md) |
| `99-archive` | 历史归档 | 保存不参与当前发现和运行的历史材料 | [归档规则](99-archive/README.md) |

`.agents/` 保存项目 Agent 上下文与长期知识，`.codex/` 保存项目级启动加载。二者不是人类总览的替代品，也不会在根目录生成另一份 `AGENTS.md`。

## 20 个活动 Skill

| 分类 | Skill | 一句话职责 |
|---|---|---|
| 论文构建 | `research-logic` | 建立机制级研究逻辑和可守住的贡献主张 |
| 论文构建 | `experiment-design` | 从主张推导证据缺口、对照、消融和结论边界 |
| 论文构建 | `data-analysis` | 检查数据完整性并给出统计、区间和可复核解释 |
| 论文构建 | `research-html-report` | 将研究逻辑与证据计划整理为独立 HTML 报告 |
| 论文构建 | `academic-figure-workflow` | 制作可编辑、可追溯并经过渲染 QA 的学术图件 |
| 论文构建 | `latex-paper-build-skill` | 构建和维护以 LaTeX 为中心的论文交付 Pipeline |
| 论文构建 | `paper-polishing-skill` | 在内容获批后完成翻译、结构修订和期刊风格润色 |
| 论文构建 | `prl-manuscript-polisher` | 对技术完整稿件进行 PRL 适配、压缩和证据校准 |
| 论文构建 | `interactive-skill-builder` | 通过访谈、规格和审批门创建或更新 Skill |
| 项目构建 | `project-agent-generator-skill` | 一次性创建缺失的 `.agents` 框架与启动加载 |
| 项目构建 | `research-project-pipeline` | 一次性编排项目发现、接入、验证和交接 |
| 项目构建 | `research-workspace-governance` | 管理研究合同、状态、证据、迁移和追踪关系 |
| 项目构建 | `research-management-pipeline` | 接入后重复汇总状态并路由一个最小下一动作 |
| 项目构建 | `experiment-protocol-audit` | 只读审核显式 Profile、Protocol、清单和运行证据 |
| 项目构建 | `project-submission-audit` | 在提交或交付前只读审核实际变更面 |
| 核心工具 | `neat-freak` | 重复维护 README、Agent 文档和长期知识的一致性 |
| 核心工具 | `handoff` | 生成紧凑、证据链接明确的后续任务交接 |
| 核心工具 | `skill-audit-refactor` | 审核、精简、拆分或重构已有 Skill |
| 核心工具 | `training-code-architecture` | 将训练脚本提炼为配置驱动的可复用工程架构 |
| 个人教学 | `logic-chain-tutor` | 从当前卡点建立前置知识到目标概念的逻辑链 |

## 我应该从哪里开始

| 当前目标 | 入口 |
|---|---|
| 新研究项目或尚未接入的遗留项目 | 从 [20-project-build](20-project-build/README.md) 的一次性接入流程开始 |
| 已接入项目的合同、证据或状态发生变化 | 使用项目构建框架中的重复研究管理流程 |
| 把已有研究成果整理成论文 | 从 [10-paper-build](10-paper-build/README.md) 当前最早缺失的阶段进入 |
| 更新已初始化项目的 README、`.agents` 或长期知识 | 使用 [50-core-utils](50-core-utils/README.md) 中的持续维护工具 |
| 审核一个 Skill 或整理训练代码 | 从核心工具分类选择对应 Skill |
| 准备提交、交付或换会话 | 分别使用提交审计与任务交接，不把二者视为自动提交授权 |
| 学习陌生概念、公式或论文方法 | 使用 [90-personal](90-personal/README.md) 中的教学入口 |

## 快速开始

```powershell
git clone https://github.com/jiaqi-Sun2020/codex-skill-hub.git
Set-Location .\codex-skill-hub
```

让 Codex 读取目标目录的 `SKILL.md`，或安装整个 Skill 目录。不要只复制 `SKILL.md`，因为 `scripts/`、`references/`、`assets/` 和 `templates/` 也可能属于执行契约。

最小仓库检查均从仓库根目录运行：

```powershell
git diff --check
python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit
```

分类级命令和测试见相应分类 README；具体执行语义以各 Skill 的 `SKILL.md` 为准。

## 外部项目、来源与许可

PaperTrace 的项目专属 Skill 由其[独立仓库](https://github.com/jiaqi-Sun2020/PaperTrace/tree/main/skills)维护，本仓库只提供导航，不复制其当前源码。Skill Registry 的唯一源码位于 [`50-core-utils/skill-registry/`](50-core-utils/skill-registry/README.md)。

各分类 README 记录与该分类直接相关的迁移来源、开源借鉴和许可证。新增借鉴时，应记录作者或维护者、项目链接、借鉴范围和许可证，不得只在提交信息中留下来源。

本仓库中由 `jiaqi-Sun2020` 原创或有权再许可的内容采用 [MIT License](LICENSE)。第三方来源或衍生部分继续遵守其原始许可证、版权声明和通知要求；根 MIT License 不覆盖或取消这些义务。
