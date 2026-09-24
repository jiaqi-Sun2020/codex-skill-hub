# 论文构建框架

[中文](README.md) | [English](README.en.md) | [返回根 README](../README.md)

`10-paper-build/` 直接维护九个同级 Skill，用于把研究问题、证据和分析组织成可审核的图件、中文作者审阅稿及最终投稿材料。本目录是论文构建分类的人类入口；每个 Skill 的正式执行规则仍以其 `SKILL.md` 为准。

> 论文 Pipeline 管理研究论证和交付物，不执行具体研究任务，不虚构数据，也不会因为图件、编译或润色通过而宣告科学主张成立。

## 整体框架

```text
研究逻辑
  ↓
实验与证据设计 ──→ 图件论点规划
  ↓
研究执行与数据分析 ──→ 可用证据
  ↓                         ↓
HTML 报告（可选）   academic-figure-workflow
  ↓                         ↓
中文 LaTeX 稿件 ← 图件包、图注、证据追踪、QA
  ↓
作者科学与视觉审核
  ↓
英文润色与投稿检查
```

这不是必须从头执行的线性流水线。应从当前最早缺失或证据不足的阶段进入；图件和 HTML 报告都是按需支线。

## 第一性原理

1. **先有主张，再设计证据。**不能从已有图表或方便运行的实验反推更强结论。
2. **研究执行不属于论文 Skill。**计算、现场、实验室、定性或其他研究工作由项目代码、领域 Skill 或人工专家完成。
3. **数据分析与作图分工。**`data-analysis` 判断数据、统计和不确定性是否可信；`academic-figure-workflow` 把获准材料转成图件。
4. **图件是证据表达，不是证据本身。**视觉和结构 QA 通过不能提升科学主张状态。
5. **中文内容先审核，英文润色后执行。**除非用户明确覆盖，先确认科学内容、边界和图表意图，再翻译和适配期刊。
6. **简单项目保持简单。**没有图件、统计或 HTML 报告需求时，不生成空目录、空 manifest 或形式化占位物。

## 九个 Skill 的唯一职责

| Skill | 负责 | 不负责 |
|---|---|---|
| [`research-logic`](research-logic-skill/SKILL.md) | 机制级研究逻辑、贡献主张和理论缺口 | 实现代码或虚构结果 |
| [`experiment-design`](experiment-design-skill/SKILL.md) | 研究问题、证据缺口、对照、消融、指标和 claim boundary | 执行实验、实现运行器或授予执行权限 |
| [`data-analysis`](data-analysis/SKILL.md) | 数据完整性、统计检验、效应量、区间、不确定性和可复核解释 | 把缺失或不可靠数据包装成肯定结论 |
| [`research-html-report`](research-html-report/SKILL.md) | 独立 HTML 研究简报、证据计划和风险展示 | 替代研究设计或制造证据 |
| [`academic-figure-workflow`](academic-figure-workflow/SKILL.md) | 图件论点、可编辑源、样式、导出、图注、证据追踪和渲染 QA | 虚构数据、机制、模块或科学支持 |
| [`latex-paper-build-skill`](latex-paper-build-skill/SKILL.md) | Pipeline 编排、LaTeX 架构、图件装配、交叉引用和编译 | 重复实现统计分析或制图逻辑 |
| [`paper-polishing-skill`](paper-polishing-skill/SKILL.md) | 获批内容的翻译、结构修订和 Nature/PRL/PRA 风格润色 | 发明数据、引用或更强主张 |
| [`prl-manuscript-polisher`](prl-manuscript-polisher/SKILL.md) | 技术完整物理稿件的 PRL 压缩、适配和证据校准 | 用措辞掩盖证据不足 |
| [`interactive-skill-builder`](interactive-skill-builder/SKILL.md) | 通过访谈、规格确认、审批门和验证创建 Skill | 绕过作者确认生成最终 Skill |

`latex-paper-build-skill` 是论文 Pipeline 的编排入口，但不拥有其他 Skill 的专业能力。`interactive-skill-builder` 是同级辅助工具，不是论文生命周期的强制阶段。

## 阶段 0–7

| 阶段 | 何时进入 | 负责人 | 核心产物 | 退出条件 |
|---|---|---|---|---|
| 0 接收与盘点 | 新论文或接入已有稿件 | LaTeX Pipeline | `paper_config.json`、资产与缺口清单 | 当前来源、目标期刊、语言和缺失决定可见 |
| 1 研究逻辑 | 贡献、机制或组合关系不清 | `research-logic` | `research_logic.md` | 中心机制和可守住的主张明确 |
| 2 实验与证据设计 | 主张已知但证据计划不足 | `experiment-design` | `experiment_plan.md`、可选 Figure Evidence Plan | 每个主张映射到证据或明确 TODO |
| 3 研究执行与分析 | 需要产生或核验结果 | 项目/领域执行者 + `data-analysis` | 原始结果、分析代码、统计与解释 | 来源、单位、变换、不确定性和边界可审查 |
| 4 研究简报 | 需要共享或打印研究计划 | `research-html-report` | 独立 HTML 报告 | 主张、证据矩阵、风险和 TODO 可见 |
| 5 图件与中文稿 | 需要正式图件或论文结构 | 图件 Skill + LaTeX Pipeline | 图件包、`caption.md`、中文 LaTeX 稿件 | 路径解析、图注、正文解读和编译关系成立 |
| 6 作者审核 | 中文稿和适用图件已形成 | 作者/领域专家 | 审核决定和保留 TODO | 科学内容、主张边界、术语、图表和元数据获批 |
| 7 英文润色与投稿检查 | 作者已批准科学内容 | polishing / PRL Skill | 英文稿、构建与投稿检查 | PDF、引用、图件、匿名和期刊约束通过或列明缺口 |

阶段完成只表示该阶段的合同满足。工作完成、数据可信、图件合格、稿件编译、主张获支持和获得发布授权必须分别判断。

## 可选图件证据支线

实验设计阶段只规划图件要回答的问题，不直接画图。交给 `academic-figure-workflow` 前，最小输入包括：

- figure ID 和目标稿件章节；
- primary claim anchor；
- 数据、代码、公式、文本或用户批准事实的来源；
- evidence readiness：`unavailable / unreviewed / verified_for_figure`；
- statistics readiness：`not_applicable / unreviewed / verified_for_figure`；
- 每个面板的非重复职责；
- 目标期刊、最终物理尺寸、可编辑源和导出格式；
- 尚未解决的科学决定。

图件输出包包括可编辑源、SVG/PDF/PNG 等导出、`caption.md`、放置建议、证据追踪、相关 claim anchor、渲染/结构 QA 和未解决问题。证据不足时只能交付规格、故事板或明确标记的草稿。

生成式论文 Pipeline 的唯一图件根是：

```text
05_manuscript_zh/figures/
├── style/                 # 仅在需要共享视觉系统时创建
└── figNN_<slug>/          # 仅在该图件存在时创建
    ├── source/
    ├── exports/
    ├── caption.md
    └── manifest
```

不得再创建根级 `figures/`，也不得向 `04_reports/` 或 `07_polished_submission/` 复制第二份图件包。独立调用图件 Skill 时仍可使用用户指定的 figure root。

## 默认工作区

```text
paper_pipeline/
├── paper_config.json
├── 00_research_logic/
├── 01_experiment_design/
├── 02_training_code/      # 仅在项目确有训练或分析代码时使用
├── 03_results/
├── 04_reports/            # 可选
├── 05_manuscript_zh/
│   ├── main.tex
│   ├── preamble.tex
│   ├── frontmatter.tex
│   ├── sections/
│   ├── figures/           # 有图件时创建
│   └── references/
├── 06_review_gate/
├── 07_polished_submission/
└── pipeline_context.md
```

目录编号为兼容合同，不因新增图件支线而重新编号。`02_training_code/` 也是兼容位置，不意味着所有研究都必须训练模型。

## 按当前状态选择入口

| 当前状态 | 起点 |
|---|---|
| 只有研究想法 | Stage 1 |
| 主张清楚但缺少证据计划 | Stage 2 |
| 已有结果但数据、统计或不确定性未核验 | Stage 3 |
| 需要可分享研究简报 | Stage 4 |
| 需要图件、图注、风格锁定或图件 QA | 可选图件支线，然后返回 Stage 5 |
| 已有 `.tex`，需要重组或接入配置 | Stage 5 |
| 中文科学内容等待作者决定 | Stage 6 |
| 内容已经批准，需要英文稿或 PRL 适配 | Stage 7 |

不要求小修改从 Stage 0 重跑。任何缺失证据、未批准决定或失败门禁都应返回最早受影响阶段，而不是靠润色绕过。

## 使用与验证

从仓库根目录创建新 Pipeline：

```powershell
python -X utf8 -B ".\10-paper-build\latex-paper-build-skill\scripts\create_paper_pipeline.py" `
  --project "D:\path\to\paper_pipeline" `
  --title "Paper Title"
```

接入已有 LaTeX 稿件时，可以增加 `--latex-source`、`--bib` 和 `--copy-figures`。命令不会自动执行实验、生成科学结论或批准投稿。

验证本分类：

```powershell
Get-ChildItem .\10-paper-build -Directory | ForEach-Object {
    if (Test-Path (Join-Path $_.FullName 'SKILL.md')) {
        python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" $_.FullName
    }
}

python -X utf8 -B -m unittest discover `
  -s ".\10-paper-build\latex-paper-build-skill\tests" `
  -p "test_*.py"
```

## 迁移、来源与许可

2026-09-24，本目录从已退役的 `jiaqi-Sun2020/S_paper_skills` 仓库 `main` 快照导入八个 Skill（源提交 `dcd573b1768e48e794975100f8548dc0f1bcb50e`），与既有 `academic-figure-workflow` 共同构成九个同级 Skill。旧目录 `data-analsys-skill/` 已规范为 `data-analysis/`；旧 wrapper、`util_skills/` 层和快捷方式不再使用。原仓库 MIT 声明保存在 [`S_PAPER_SKILLS_LICENSE`](S_PAPER_SKILLS_LICENSE)。

图件工作流借鉴了 [`nature-figure`](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure) 的论点驱动多面板、语义配色和投稿 QA 思路，以及 [`scipilot-figure-skill`](https://github.com/Haojae/scipilot-figure-skill) 的数据先行可视化顾问思路。具体出版规范来源记录在 [`publisher-visual-source-map.md`](academic-figure-workflow/references/publisher-visual-source-map.md)。借鉴不表示原作者对本项目背书，第三方材料继续遵守其原始许可证和通知要求。
