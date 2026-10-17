# 上游来源与受管快照 / Upstream snapshot

本目录与同级 `find-skills` 一样，是中央源码快照，不是全局安装、Git 子模块或自动更新连接。
This folder is a central source snapshot, like the adjacent `find-skills`; it is not a global installation, Git submodule, or automatic update subscription.

## 固定来源 / Pinned source

- Repository: https://github.com/Leonxlnx/taste-skill
- Commit: https://github.com/Leonxlnx/taste-skill/commit/f624f37a8c650b9cc550253104925efe4c8de246
- Upstream path: `skills/taste-skill/`
- Product: tasteskill v2; Skill invocation name: `design-taste-frontend`.
- Import date: 2026-10-17 (Asia/Shanghai).
- License: MIT, Copyright (c) 2026 Leonxlnx. The repository-root LICENSE from the same commit is retained locally as `LICENSE`; the Hub license does not replace this notice.

## 纳入范围 / Included content

完整保留该提交下 `skills/taste-skill/` 的29个文件：`SKILL.md`、Skill 自带 README、全部 `scripts/`（含 `lib/`）、`references/`、`library/`、`assets/` 和 `evals/`。不改写上游执行契约；本地仅补充 LICENSE 和本来源记录。导入时逐文件核对 Git blob SHA 与固定提交目录树。

All 29 files in the upstream Skill directory are retained unchanged. Only the root license and this provenance record are added locally. Other Skills, the upstream website, promotional media, plugin packaging, installer, and Git metadata are not imported. This is one active Skill, not the entire upstream bundle.

## 能力、准备与权限 / Capability, prerequisites and authority

- 面向落地页、品牌站、作品集及产品展示等公开网页；不是仪表盘或应用屏幕的默认 Skill。
- 保留上游特定的排版、配图和动效偏好，不将其视为所有项目通用的设计标准。优先遵守用户目标和适用项目规范。
- `draw.mjs`、`lint.mjs`、`assets.mjs` 需要 Node 18+；完整浏览器检查需要 Node 22+ 以及已安装的 Chrome、Edge 或 Chromium。当前导入不安装运行时、浏览器或 npm 包。
- `assets.mjs` 访问开放图片与视频来源，下载素材并记录许可；素材许可与代码 MIT 许可分开核对，不视为客户自有素材。
- 使用时脚本可在调用项目创建 `.taste-skill/`，素材下载会写入输出目录，浏览器检查会启动进程、临时本地服务并保存截图；这些动作不因下载本 Skill 而自动获准。
- 不自动全局安装、启用 Hook、改浏览器配置或注册到外部项目。导入不等于已完成真实网页画质或浏览器运行验收。

The scripts may write working files, download assets, launch browser processes and a temporary local server when invoked. Review the actual request and project permissions first. The Hub import grants none of those future actions and creates no user-level Codex discovery entry.

## 更新与验证 / Updates and verification

更新时选定一个明确的上游提交，比较全部文件、依赖及许可证后再人工应用；不自动追踪 main，不覆盖已有本地修改。保留同级 find-skills 和其他 Skill 不变。

From the Hub root, syntax-check without running the imported programs:

```powershell
Get-ChildItem '.\50-core-utils\taste-skill' -Recurse -File |
  Where-Object { $_.Extension -in @('.mjs', '.js') } |
  ForEach-Object {
    node --check $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "Syntax check failed: $($_.FullName)" }
  }
```

结构、JSON 和语法检查不是实际设计质量、浏览器兼容或安全认证；未运行的检查不得标为通过。
