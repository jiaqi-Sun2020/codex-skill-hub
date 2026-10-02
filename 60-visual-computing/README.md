# 实时视觉计算

[English](README.en.md) | [仓库总览](../README.md)

`60-visual-computing` 保存可跨项目复用的网页实时视觉计算 Skill。这里的 Skill
关注实现与审核实时图形效果所需的表示、材质、动画、性能和可复现验证；它不替代
天文学问答、科学建模或某个具体项目的领域结论。

## 当前 Skill

| Skill | 用途 | 边界 |
|---|---|---|
| `celestial-body-formation-skill` | 从几何、能量、时间和采样出发，构建、改进或审核网页中的行星、恒星、黑洞及其表面与发射结构的实时视觉效果。 | 不用于纯天文学知识问答，也不把视觉近似表述为科学上的天体形成或演化模拟。 |

## 使用与边界

先读取 [`celestial-body-formation-skill/SKILL.md`](celestial-body-formation-skill/SKILL.md)。它要求把空间、能量、时间和采样关系与实际入口、设备和证据绑定；画质认可、运行证据和科学结论仍是独立事实。

Skill 中的通用参考资料说明渲染表示与对抗性验证。项目专属案例、机器路径、内部构建记录和会话信息不属于本分类，也不应补回公开仓库；需要追溯某个项目时，只能在获得授权的目标项目内读取其自身记录。

## 来源与许可

本分类由用户从本地 Codex Skill 导入。`references/` 中的说明引用 [PBRT](https://www.pbr-book.org/) 与 [WGSL 规范](https://www.w3.org/TR/WGSL/) 作为方法依据，但未复制其实现或文档。仓库中可再许可的内容适用根目录 [MIT License](../LICENSE)；外部资料继续遵守其自身条款。

## 验证

从仓库根目录运行：

```powershell
python -X utf8 -B "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" ".\60-visual-computing\celestial-body-formation-skill"
```
