# 个人 Skill

[中文](README.md) | [English](README.en.md) | [返回根 README](../README.md)

`90-personal/` 保存针对个人学习方式长期调整的 Skill。当前唯一活动源码是 [`logic-chain-tutor`](logic-chain-tutor/SKILL.md)。它不属于项目治理或论文交付 Pipeline，也不会自动修改外部学习画像。

## 整体框架

```text
当前卡点
  ↓
识别真正缺失的前置知识
  ↓
已知锚点 → 缺失桥梁 → 目标概念
  ↓
最小完整例子 / 推导 / 反例 / 对比
  ↓
检查理解并按需继续
```

## 何时使用

- 遇到陌生概念、符号、公式或论文方法；
- 忘记关键基础，希望从当前卡点补桥而不是重学整门课程；
- 需要区分容易混淆的数学对象、操作和物理含义；
- 需要详细推导、具体例子、反例或完整复习。

简单事实查询、纯翻译或只需要执行操作的任务不应触发教学流程。用户要求简短回答、只给提示、局部解释或限定长度时，输出合同优先于默认深度。

## 职责边界

- 只在当前对话中适应学习者，不从未经批准的外部资料推断个人画像。
- 不把类比当作证明，也不让故事增加真实概念不存在的机制。
- 不把概念相似、数值近似、实现等价和理论等价混为一谈。
- 不替代领域实验、项目执行或科学结论审核。

## 使用入口

> 使用 `logic-chain-tutor` 解释这个知识点。从我当前卡住的步骤开始，先给出逻辑地图，再逐步解释符号、操作、原因和物理含义，并用一个最小完整例子验证。

详细教学协议、输出模式和安全边界见 [`logic-chain-tutor/SKILL.md`](logic-chain-tutor/SKILL.md)。

## 验证

从仓库根目录运行：

```powershell
python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\90-personal\logic-chain-tutor"
```
