# 上游来源与中央快照 / Upstream snapshot

本目录与同级 `taste-skill`、`find-skills` 一样，是中央源码快照，不是全局安装、Git 子模块或自动更新连接。
This is a central source snapshot, not a global installation, submodule or auto-update subscription.

## 固定来源 / Pinned source

- Repository: https://github.com/blader/humanizer
- Commit: https://github.com/blader/humanizer/commit/8c307f367c91bd974002f10f2be2965d642c13df
- Version / invocation: `3.1.0` / `humanizer`.
- Import date: 2026-10-28 (Asia/Shanghai).
- License: MIT, Copyright (c) 2025 Siqi Chen; retained in `LICENSE`.
- The owner-provided local copy was the input. All nine selected files matched the Git blob IDs in this pinned upstream tree before import. No manuscript, private project material, or local source path is included.

## 纳入与排除 / Included and excluded

保留 `SKILL.md`、`README.md`、`CHANGELOG.md`、`LICENSE`、`agents/openai.yaml`、`scripts/validate-package.py` 和三份插件 JSON。插件 JSON 仅用于保留可核验的包元数据，并满足原版离线校验器；没有运行插件安装、注册或全局发现。

不导入上游 `.github/`、维护用 `AGENTS.md`、Git 元数据或本地论文文件。来源目录保持不变。本地新增本来源记录；README 两处行尾空格被清理以适配 Hub 差异检查，其余导入文件保持原字节，包括完整执行规则。

The nine-file subset preserves the prompt, OpenAI UI metadata, license, release notes and original offline package validator. Three inert plugin JSON files are retained because that validator reads them. No plugin installation is performed. Upstream workflows, issue templates, maintainer instructions and Git metadata are excluded. The only change to imported content is removal of two trailing spaces in README; no behavioral rule is rewritten.

## 使用与边界 / Use and authority

- 需要去除冗余、空泛拔高和模板化表达时，显式读取本目录 `SKILL.md`。本次只收录源码；不会自动出现在用户级 Skill 列表中。
- 上游 file mode 会改写指定文件。只有实际请求授权编辑该文件时才可写回；给出路径、询问或要求审核不自行产生改写授权。本次导入不授权任何后续改稿。
- 上游包含较强的标点与措辞偏好，不把它们提升为通用科学标准或论文审稿规则。保留科学限定、术语、数字、引用与原意；科学主张审核仍由 `paper-audit` 等适用流程承担，本次不修改这些流程。
- 不承诺绕过 AI 检测，不根据文字风格认定作者身份；结构校验不代表真实文本质量或科学正确性已经验收。
- 不安装运行时、依赖或 Hook，不修改 Agent/记忆加载关系，不自动发布或推送。

Upstream file mode writes the final prose back. Apply it only within a real edit request and the project's authority; merely naming a path is not permission. The upstream style preferences are not universal scientific standards. Source inclusion does not authorize manuscript edits, certify authorship or guarantee detector evasion. No prose rewrite was exercised during this import.

## 验证与更新 / Verify and update

从仓库根目录运行已安装的 Python：

```powershell
python -X utf8 -B ".\50-core-utils\humanizer\scripts\validate-package.py"
```

该标准库校验器只读本目录，核对版本、模式编号、引用和包元数据。它不安装插件、不联网、不改稿。更新时固定新提交，比较文件、规则、许可和本地差异后人工应用，不自动追踪 `main`。

The validator is a read-only standard-library package check, not behavioral acceptance. Choose an explicit commit for future updates and preserve local changes.

## 导入前原文件摘要 / Source SHA-256

These hashes identify the owner's original files, also verified against the pinned Git tree. README has the documented whitespace-only local adjustment.

| File | Original SHA-256 |
|---|---|
| `SKILL.md` | `0612f1dfb1672b0ea9b97e139bf1f06cabe98d8b27424fe8ff01e1fb4cc99cad` |
| `README.md` | `500b53c0d29cd3219d160b5f9a109c0969f706aec74b49a4a081d2026ba48ec7` |
| `CHANGELOG.md` | `b3591fe203429f1a6bd2f713c79272e9a8e58a487843d0908d2bbe0700722afa` |
| `LICENSE` | `4ac4810254ab36d45419141aeb8e69bf50652cfafe5b2dab947d06d44e5cbf96` |
| `agents/openai.yaml` | `9d87ff83149a04f86a372948b8ee35fa249de20923867bbc2a49304290aad736` |
| `scripts/validate-package.py` | `941bd99e52b2ba21449719bb7969607ac8117e3dc173d0c9dfe64fd274c65938` |
| `.claude-plugin/plugin.json` | `054c0afeeb03c12f01a7f156da949edfdec3a2b756588f5ff4ee7357b0c07f6a` |
| `.claude-plugin/marketplace.json` | `e539740285b660d2288a38b6d9b237396c6769828c671c46b9f91e760db6cc29` |
| `.cursor-plugin/plugin.json` | `d1e0b50594cf4bbe57fd164b771b401713a91b76b5a213ebe8f4558bb2036546` |
