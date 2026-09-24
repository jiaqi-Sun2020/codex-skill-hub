# 核心工具

[中文](README.md) | [English](README.en.md) | [返回根 README](../README.md)

`50-core-utils/` 保存四个可跨项目复用的活动 Skill，以及一套不计入活动 Skill 的版本注册基础设施。这些组件不定义研究领域方法，也不替代 `20-project-build` 的项目治理所有权。

## 整体框架

```text
一次性框架生成完成
  ↓
neat-freak：重复维护项目信息与加载一致性
  ├─ skill-audit-refactor：审核或重构 Skill
  ├─ training-code-architecture：整理训练工程
  └─ handoff：暂停、转交或切换会话

中央 Skill 版本治理
  └─ skill-registry：源码、不可变发布与消费关系
```

## 组件职责

| 组件 | 性质 | 唯一职责 | 不负责 |
|---|---|---|---|
| [`neat-freak`](neat-freak/SKILL.md) | 活动 Skill | 在首次框架生成后重复审计和同步 README、`.agents`、长期知识与既有受管加载 | 首次生成框架、修改治理记录或解释科学结果 |
| [`handoff`](handoff/SKILL.md) | 活动 Skill | 生成紧凑、证据链接明确的后续任务交接 | 证明任务完成或扩大下一位 Agent 的授权 |
| [`skill-audit-refactor`](skill-audit-refactor/SKILL.md) | 活动 Skill | 审核 Skill 的触发、范围、资源、重复和安全边界，并做最小重构 | 无依据地扩张能力或删除必要安全门 |
| [`training-code-architecture`](training-code-architecture-skill/SKILL.md) | 活动 Skill | 将已有训练脚本提炼为配置、factory、adapter、训练循环和可复现输出架构 | 把特定数据集、模型或指标硬编码为所有项目标准 |
| [`skill-registry`](skill-registry/README.md) | 基础设施 | 维护可编辑源码、版本元数据、不可变发布快照和消费关系 | 充当第五个活动 Skill 或覆盖项目拥有的 fork |

## 何时使用

- 项目已经存在 Agent 框架，代码、目录或决定发生变化：使用 `neat-freak`。
- 需要判断一个 Skill 是否过长、职责重叠或缺少验证：使用 `skill-audit-refactor`。
- 需要把现有机器学习训练代码整理为可复用模板：使用 `training-code-architecture`。
- 任务暂停、压缩上下文或交给后续会话：使用 `handoff`。
- 需要检查、发布或同步 Registry 管理的版本：使用 `skill-registry` 工具。

首次缺失 `.agents` 框架时，应使用 `20-project-build/project-agent-generator-skill`，而不是让 Neat-Freak 重新生成框架。提交前变更面审核属于 `20-project-build/project-submission-audit`，不属于 Handoff。

## 边界与安全

- “audit / check / review” 默认只读；写入需要明确的初始化、同步、修复或维护请求。
- 保留用户改动和脏工作区；不使用整仓库回退清理不相关内容。
- Registry 的 `releases/` 是不可变快照，不直接编辑。
- 项目拥有的 fork 不从中央历史发布静默覆盖。
- Handoff 默认写到系统临时目录，不把敏感信息或完整聊天复制进去。
- 训练架构只抽取稳定接口；具体数据、损失、形状和领域规则留在项目 Adapter。

## 验证

从仓库根目录运行：

```powershell
python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit
python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"
python -X utf8 -B -m unittest discover -s ".\50-core-utils\neat-freak\tests" -p "test_*.py"
python -X utf8 -B ".\50-core-utils\skill-registry\tests\test_skill_registry.py"
```

具体命令、审批门和输入输出以相应 `SKILL.md` 或 Registry README 为准。

## 来源与许可

本地 `neat-freak` 借鉴了 KKKKhazix 的 [`neat-freak`](https://github.com/KKKKhazix/khazix-skills/blob/main/neat-freak/SKILL.md)（MIT）对知识整理和工作区一致性的思路，并扩展了 `.agents/memory/`、哈希绑定更新和 Codex 启动加载审计。本地 `handoff` 借鉴了 Matt Pocock 的 [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff)（MIT）关于临时目录、现有证据引用和敏感信息清理的原则。借鉴不表示原作者对本项目背书，第三方义务继续有效。
