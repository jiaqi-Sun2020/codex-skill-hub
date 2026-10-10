# 上游来源与受管快照

本目录是 [AI Roasting 的 find-skills](https://github.com/airoasting/find-skills) 的可执行受管快照，用于在用户明确授权前，发现、检查并推荐候选 Agent Skill。它不是 Git 子模块、没有嵌套 Git 仓库，也不会自动安装到用户级 Codex 配置。

## 固定来源

- 上游仓库：<https://github.com/airoasting/find-skills>
- 固定提交：<https://github.com/airoasting/find-skills/commit/55aba1789fe0504734964d98ae1ccd39e2fefea0>
- 上游版本：v1.2.1
- 上游许可：MIT，Copyright (c) 2026 AI ROASTING；完整通知保留在本目录的 LICENSE。

根仓库的 MIT 许可不取代该第三方通知或其后续义务。

## 纳入范围

为保持 Codex 执行契约和离线回归检查完整，本快照保留：

- SKILL.md、上游 README.md、LICENSE
- scripts/find_installed.py、scripts/find_library.py、scripts/find_search.py、scripts/find_inspect.py
- docs/skills.json
- evals/evals.json 和 evals/test_inspect_patterns.py

刻意不纳入 .claude-plugin、网站 HTML/JavaScript、图片、字体、网站同步脚本、发布检查脚本或 Git 元数据。它们不参与该 Skill 在 Codex 中的发现、审查或离线回归。

## 运行与更新边界

该 Skill 的搜索和检查会读取本机已安装 Skill，并访问 AI Roasting 目录、skills.sh 与 GitHub；候选安装仍必须取得用户明确同意。本 Hub 只保存源码，未将本目录复制或链接到用户级 Codex Skill 目录，因此不会自动在 Codex 会话中加载。

更新必须人工进行：先比较一个明确的上游候选提交与本固定提交，逐项审查许可证、执行契约、脚本和数据文件，只更新上述纳入范围，再更新本记录中的提交与版本。不得跟踪上游 main 自动更新，也不得覆盖本地适配而未先审查差异。

从仓库根目录验证导入快照：

    python -X utf8 -B ".\50-core-utils\find-skills\evals\test_inspect_patterns.py"
