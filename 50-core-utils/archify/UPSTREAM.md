# 上游来源与受管快照 / Upstream snapshot

与同级 `taste-skill`、`find-skills` 相同，本目录是中央源码快照，不是全局安装、Git 子模块或自动更新连接。
Like the adjacent `taste-skill` and `find-skills`, this is a central source snapshot, not a global installation, Git submodule, or automatic update subscription.

## 固定来源 / Pinned source

- Repository: https://github.com/tt-a1i/archify
- Commit: https://github.com/tt-a1i/archify/commit/81c6be8d87090670c45d08a8f97f9d29c5af0bec
- Upstream path: `archify/`
- Package version: `3.2.0`; Skill metadata version: `3.2`; invocation name: `archify`.
- Import date: 2026-10-26 (Asia/Shanghai).
- Copyright: tt-a1i (Archify), 2026; Cocoon AI, 2025.
- License: Apache-2.0, subject to the retained `NOTICE`, historical `LICENSE-MIT`, `THIRD_PARTY_NOTICES.md`, and component-specific licenses. The Hub MIT license does not replace them.

## 纳入范围 / Included content

固定提交下单个 `archify/` 目录的206个文件完整保留、未改写。包含 SKILL、bin、renderers、schemas、references、examples、explainer、assets、locales、brand-marks、recipes、delta、migrations、scripts、package 元数据与全部许可通知；本地只添加本来源记录及受限的 `.gitattributes` 空白检查例外。该属性仅覆盖上游预渲染 HTML 与一个已核验的带尾随空白的布局源行，不改写上游字节。导入后逐文件以 Git blob SHA 与固定提交目录树核对。

All 206 upstream files are retained unchanged; only this provenance record and a narrowly scoped `.gitattributes` whitespace-check exception are added. The attribute covers upstream pre-rendered HTML and one verified trailing-space line in a layout source file; it does not rewrite upstream bytes. The upstream website, viewer development source, repository-level tests/build tooling, integrations, promotional media, archive, and Git metadata are not imported. This is one active Skill. Parent-relative npm development scripts belong to the upstream repository, not this source snapshot; do not run `npm test` or those build scripts from this Hub as if their parent were the upstream repository. Runtime CLI assets and prebuilt validators are included.

## 能力、准备与权限 / Capability, prerequisites and authority

- 将描述、Mermaid 语义或已获准读取的代码证据转为独立 HTML 交互图；支持 architecture、workflow、sequence、dataflow、lifecycle、ERD、class、tree、timeline、waterfall，以及用户按需选择的一页解释。
- 不把示例图当成项目事实，不替代研究方法、科学审核或论文图件的 `academic-figure-workflow`。
- 包声明 Node 18+；运行时不要求在包内安装 npm 依赖。浏览器审核与导出仍需对应的已有浏览器和运行条件，不能因导入成功宣称已验收。
- 将来运行通常会写入调用目录的 `.archify/`、候选、HTML 与检查回执；浏览器检查会启动进程，具体输出或覆盖须按实际任务审查。
- `finalize`、`deliver` 包含有界更新检查，可能联网并使用缓存；引入固定快照不等于授权将来联网或更新。未经明确请求，不运行更新、snooze 或 ignore 命令。
- 上游可选主动解释模式及全局规则写入保持未启用；本次不修改用户级规则、Hook、记忆、浏览器设置或任何外部项目，不创建用户级 Codex 发现入口。
- 品牌图标的商标和个别 CC-BY、CC-BY-SA、非商业等限制独立适用；字体保留 SIL OFL，Pele 保留 MIT。使用或传播具体素材前核对其条款，不能概括为全包均可按 Hub MIT 再许可。

Importing source authorizes none of its future project writes, browser launches, network update checks, global-rule edits, or publication. No npm packages, browsers or global Skills are installed by this import. The original Skill contract is preserved, but user instructions and applicable project rules take precedence.

## 更新与验证 / Updates and verification

更新需选定明确提交，比较文件、依赖、许可及行为差异后人工应用，不自动跟踪 main、不覆盖本地改动。

From the Hub root, syntax-check without running the imported programs:

```powershell
Get-ChildItem '.\50-core-utils\archify' -Recurse -File |
  Where-Object { $_.Extension -in @('.mjs', '.js') } |
  ForEach-Object {
    node --check $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "Syntax check failed: $($_.FullName)" }
  }
```

文件摘要、JSON、引用和语法检查不等于真实 HTML 交付、浏览器运行、视觉质量或跨平台验收；未运行项保持未验证。
