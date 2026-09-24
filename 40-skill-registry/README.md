# Skill Registry 兼容入口

[中文](README.md) | [English](README.en.md) | [返回根 README](../README.md)

`40-skill-registry/` 是兼容导航目录，不是第二套 Registry。目录中的 `skill-registry.lnk` 只提供本机快捷入口；唯一正式源码位于 [`50-core-utils/skill-registry/`](../50-core-utils/skill-registry/README.md)。

## 唯一源码关系

```text
40-skill-registry/skill-registry.lnk
  └─ 导航到 50-core-utils/skill-registry/
       ├─ registry.json
       ├─ sources/
       ├─ releases/
       ├─ tools/
       └─ tests/
```

## 使用边界

- 不在 `40-skill-registry/` 创建 Registry 副本、发布快照或配置。
- 不直接编辑 `releases/` 中的不可变发布；升级时从中央源码创建新版本。
- 不把 `.lnk` 当作跨机器可移植接口。
- 项目拥有的 fork 不得被中央历史发布静默覆盖。
- Registry 是版本治理基础设施，不计入 20 个活动 Skill。

## 验证入口

从仓库根目录运行：

```powershell
python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"
```

完整接口和兼容策略见 [Registry README](../50-core-utils/skill-registry/README.md)。
