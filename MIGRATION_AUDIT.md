# 首次迁移审计

审计日期：2026-07-26

比较来源：

- PAPER：`C:\Users\SSS\Desktop\PAPER\skills`
- PaperTrace：`D:\AI\PaperTrace\skills`

## 分类结论

| Skill | PAPER 文件数 | PaperTrace 文件数 | 完全相同 | 内容不同 | 仅 PaperTrace | 初始模式 |
|---|---:|---:|---:|---:|---:|---|
| `reader-learner` | 18 | 18 | 16 | 2 | 0 | `vendored` |
| `adaptive-teach` | 17 | 17 | 16 | 1 | 0 | `forked` |
| `chat-knowledge-profile` | 7 | 7 | 5 | 2 | 0 | `forked` |
| `demo-skill` | 5 | 5 | 2 | 3 | 0 | `forked` |
| `lean-html-skill` | 7 | 7 | 2 | 5 | 0 | `forked` |
| `ai-quantum-news-briefing` | 20 | 21 | 10 | 10 | 1 | `forked` |
| `nature-reader` | 18 | 29 | 10 | 8 | 11 | `forked` |
| `reader-skill` | 8 | 19 | 1 | 7 | 11 | `forked` |

## 首次共享项

`reader-learner` 的代码和测试主体相同。两处差异为：

1. `SKILL.md` 中一条项目专属的 HTML 报告所有权说明。
2. `references/visible-wiki-schema.md` 中的项目根绝对路径。

中央版本采用项目无关表述，并把命令位置统一写成“从项目根目录运行”。项目级所有权继续由各项目的 `AGENTS.md` 负责。

## 暂不合并项

- `adaptive-teach` 的 PaperTrace 版增加了完整的 Pipeline 4 身份和终止条件。
- `chat-knowledge-profile` 包含项目身份、流水线终止条件和脚本输出措辞差异。
- `demo-skill` 的三个流水线与四个流水线模板不同。
- `lean-html-skill` 的共享 HTML 代码和调用关系已经分叉。
- `ai-quantum-news-briefing`、`nature-reader`、`reader-skill` 存在实质脚本、测试、契约和新增文件差异。

这些项先登记为 `forked`。只有经过单独的行为契约审计、测试对齐和项目适配设计后，才允许升级为 `vendored` 或 `shared+overlay`。
