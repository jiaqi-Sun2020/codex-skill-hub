# Paper Build Skills

[中文](README.md) | [English](README.en.md)

`10-paper-build/` 直接维护 9 个论文研究、证据设计、分析、写作和图件 Skill。它们是同级组件，不是 `academic-figure-workflow` 的子 Skill，也不属于 `20-project-build/` 的六组件项目治理架构。

## 选择指南

| Skill | 负责什么 | 不负责什么 |
|---|---|---|
| [`research-logic`](research-logic-skill/) | 诊断浅层模块拼接，建立机制级研究逻辑和可守住的贡献主张 | 实现代码或虚构实验结果 |
| [`experiment-design`](experiment-design-skill/) | 从 claim 推导研究问题、假设、证据缺口、数据集、基线、消融、指标、对照和 claim boundary | 执行实验、实现运行器或建立运行时门禁 |
| [`data-analysis`](data-analysis/) | 检查实验数据完整性，选择统计检验，报告效应量、区间和可复核解释 | 把缺失或不可靠数据包装成肯定结论 |
| [`research-html-report`](research-html-report/) | 将研究逻辑、证据计划和风险整理为独立 HTML 研究报告 | 替代研究设计或制造证据 |
| [`latex-paper-build-skill`](latex-paper-build-skill/) | 构建、重组和维护以 LaTeX 为中心的论文交付流水线 | 在作者审批前擅自改变科学内容 |
| [`paper-polishing-skill`](paper-polishing-skill/) | 在科学内容获批后进行翻译、结构修订和 Nature/PRL/PRA 风格润色 | 发明数据、引用、机制或更强主张 |
| [`prl-manuscript-polisher`](prl-manuscript-polisher/) | 对技术完整的物理稿件做 PRL 适配、压缩和证据校准 | 用措辞掩盖证据不足 |
| [`academic-figure-workflow`](academic-figure-workflow/) | 规划、制作、验证和打包可编辑、可追溯的学术图件 | 虚构数据、机制、模块或视觉证据 |
| [`interactive-skill-builder`](interactive-skill-builder/) | 通过访谈、规格确认、审批门和验证创建或更新 Codex Skill | 绕过作者确认直接生成最终 Skill |

## 推荐组合

主线不是必须全部执行。根据当前缺口选择最小组合：

```text
研究想法
  -> research-logic
  -> experiment-design
  -> 实验执行（由项目代码或专用执行 Skill 负责）
  -> data-analysis
  -> research-html-report（可选研究简报）
  -> latex-paper-build-skill
  -> paper-polishing-skill
  -> prl-manuscript-polisher（仅 PRL 目标）

论文 claim / 代码 / 数据
  -> academic-figure-workflow
  -> 可编辑源文件 + 导出 + 图注 + QA
```

`experiment-design` 的终点是“说明需要做什么、缺什么证据、如何设置对照、结论最多能到哪里”。它不实现实验执行器，不替代项目运行时，也不授予实验、发布或主张权限。

## 迁移说明

2026-09-24，本目录从已退役的 `jiaqi-Sun2020/S_paper_skills` 仓库 `main` 快照导入 8 个 Skill（源提交 `dcd573b1768e48e794975100f8548dc0f1bcb50e`）。导入只保留源码快照，不带旧仓库提交历史；旧仓库的全部 refs 已在删除前另行保存为 Git bundle。

目录映射：

| 旧路径 | 新路径 |
|---|---|
| `research-logic-skill/` | `10-paper-build/research-logic-skill/` |
| `experiment-design-skill/` | `10-paper-build/experiment-design-skill/` |
| `data-analsys-skill/` | `10-paper-build/data-analysis/` |
| `latex-paper-build-skill/` | `10-paper-build/latex-paper-build-skill/` |
| `paper-polishing-skill/` | `10-paper-build/paper-polishing-skill/` |
| `util_skills/research-html-report/` | `10-paper-build/research-html-report/` |
| `util_skills/interactive-skill-builder/` | `10-paper-build/interactive-skill-builder/` |
| `util_skills/prl-manuscript-polisher/` | `10-paper-build/prl-manuscript-polisher/` |

原仓库 MIT 声明保存在 [`S_PAPER_SKILLS_LICENSE`](S_PAPER_SKILLS_LICENSE)。这些 Skill 是 Hub 直接维护源码，不加入 Skill Registry 的不可变 `releases/`。

## 验证

在仓库根目录运行：

```powershell
Get-ChildItem .\10-paper-build -Directory | ForEach-Object {
    if (Test-Path (Join-Path $_.FullName 'SKILL.md')) {
        python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" $_.FullName
    }
}

python -X utf8 -B -m py_compile `
  .\10-paper-build\latex-paper-build-skill\scripts\create_paper_pipeline.py `
  .\10-paper-build\latex-paper-build-skill\scripts\scaffold_latex_paper.py `
  .\10-paper-build\prl-manuscript-polisher\scripts\audit_tex.py
```
