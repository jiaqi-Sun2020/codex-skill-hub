# Skill Registry

这是项目通用 Skill 的唯一中央源码和版本发布中心。

## 核心规则

1. 通用 Skill 只在 `sources/<skill-id>/` 中正式编辑。
2. 项目中的 `skills/` 是受版本锁定的本地发布副本，不是通用源码。
3. `releases/<skill-id>/<version>/` 是不可变发布快照。
4. 项目通过 `skills.manifest.json` 声明版本，通过 `skills.lock.json` 记录内容哈希。
5. 同步默认只预览；只有显式加入 `--apply` 才会写入项目。
6. 已锁定副本出现本地漂移时，同步工具拒绝覆盖。
7. 首次接管已有副本必须使用 `--bootstrap`，原目录会保存在项目的 `.skill-registry/backups/`。
8. 项目差异明显的 Skill 使用 `forked`，不得被中央版本自动覆盖。

## 目录

```text
skill-registry/
├─ registry.json
├─ sources/
│  └─ reader-learner/
├─ releases/
│  └─ reader-learner/
│     └─ 1.0.0/
├─ tools/
│  └─ skill_registry.py
└─ tests/
   └─ test_skill_registry.py
```

## 常用命令

以下命令均从仓库内的 `50-core-utils/skill-registry` 运行。

验证中央注册中心：

```powershell
python .\tools\skill_registry.py registry-check --registry .
```

检查 PaperTrace 项目：

```powershell
python .\tools\skill_registry.py check --project "<project-root>"
```

查看一个 Skill 的文件差异：

```powershell
python .\tools\skill_registry.py diff --project "<project-root>" --skill <skill-id>
```

预览更新：

```powershell
python .\tools\skill_registry.py sync --project "<project-root>" --skill <skill-id>
```

确认差异后应用更新：

```powershell
python .\tools\skill_registry.py sync --project "<project-root>" --skill <skill-id> --apply
```

从中央源码发布新版本时，先预览：

```powershell
python .\tools\skill_registry.py release --registry . --skill reader-learner --version 1.0.1
```

确认后创建不可变发布：

```powershell
python .\tools\skill_registry.py release --registry . --skill reader-learner --version 1.0.1 --apply
```

然后在项目的 `skills.manifest.json` 中选择新版本，执行 `diff`、预览 `sync`，最后显式应用。

当前 PaperTrace 的实现包含项目专属的聊天画像、reader-v3 和教学接口，已全部登记为 `forked`；中央 `reader-learner 1.0.0` 仅作为历史发布保留，不会覆盖 PaperTrace。

## 状态含义

| 状态 | 含义 |
|---|---|
| `current` | 本地副本、锁文件和中央发布完全一致 |
| `update_available` | 本地没有漂移，但清单请求了另一个版本 |
| `local_drift` | 项目内有人直接修改了受管副本；同步会拒绝覆盖 |
| `unlocked_match` | 内容与中央一致，但还没有锁文件记录 |
| `unmanaged_existing` | 首次接管时发现已有且不同的副本 |
| `missing` | 项目声明了依赖，但本地副本不存在 |
| `ignored` | `forked` 或 `project-owned`，不参与自动同步 |

## 回滚

每次替换既有本地副本时，旧版本都保存在：

```text
<project>\.skill-registry\backups\<skill-id>\
```

同步工具不会自动删除这些备份。项目也应把 `skills.manifest.json`、`skills.lock.json` 和实际 Skill 副本一起提交到 Git，以便通过版本控制回滚。
