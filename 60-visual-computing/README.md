# 实时视觉计算

[English](README.en.md) | [仓库总览](../README.md)

`60-visual-computing` 保存可跨项目复用的网页实时视觉计算 Skill。这里的 Skill
覆盖实时图形、GSAP 交互动画、性能和可复现验证；它不替代天文学问答、科学建模或
某个具体项目的领域结论，也不会未经项目选择而替换现有动画库。

## 当前 Skill

| Skill | 用途 | 边界 |
|---|---|---|
| `celestial-body-formation-skill` | 从几何、能量、时间和采样出发，构建、改进或审核网页中的行星、恒星、中子星、黑洞及其表面与发射结构的实时视觉效果。 | 不用于纯天文学知识问答，也不把视觉近似表述为科学上的天体形成或演化模拟。 |
| `gsap-core` | 使用 GSAP 核心补间、缓动、交错、默认值与响应式动画。 | 只在项目选择或需要 GSAP 时使用，不替代已选动画库。 |
| `gsap-timeline` | 用时间线、位置参数、嵌套和播放控制编排多步骤动画。 | 不把多个独立延迟当成可靠的动画编排证据。 |
| `gsap-scrolltrigger` | 实现滚动触发、固定、scrub 和视差类动画。 | 只处理滚动交互；组件卸载与布局变化仍须在所属框架中处理。 |
| `gsap-plugins` | 注册并使用交互、SVG、文本、物理和缓动插件。 | 不生成私有 registry、`.npmrc` 或认证令牌。 |
| `gsap-utils` | 用 `gsap.utils` 映射、裁剪、插值、随机、吸附和处理集合。 | 工具函数不替代业务状态、可访问性或交互设计。 |
| `gsap-react` | 在 React 或 Next.js 中使用 `useGSAP`、引用、作用域和清理。 | 不把 React 生命周期模式套用到 Vue 或 Svelte。 |
| `gsap-performance` | 优先变换、批处理和受控 `will-change`，降低卡顿。 | 性能建议需要在目标设备和实际页面验证。 |
| `gsap-frameworks` | 在 Vue、Svelte 等非 React 框架中管理挂载、选择器作用域和卸载清理。 | React 应改用 `gsap-react`。 |

## 使用与边界

先读取 [`celestial-body-formation-skill/SKILL.md`](celestial-body-formation-skill/SKILL.md)。它要求把空间、能量、时间和采样关系与实际入口、设备和证据绑定；画质认可、运行证据和科学结论仍是独立事实。

天体 Skill 的通用参考资料说明渲染表示与对抗性验证。恒星日珥与中子星材料页只提供可复用的渲染表示、生成顺序与验证边界，不会把视觉参考升级为科学模型。GSAP Skill 按核心 API、时间线、滚动、插件、工具函数、框架和性能路由；它们不安装依赖、不改写打包配置，也不推翻用户已选的动画库。项目专属案例、机器路径、内部构建记录和会话信息不属于本分类，也不应补回公开仓库；需要追溯某个项目时，只能在获得授权的目标项目内读取其自身记录。

## 来源与许可

天体 Skill 由用户从本地 Codex Skill 导入。`references/` 中的说明引用 [PBRT](https://www.pbr-book.org/) 与 [WGSL 规范](https://www.w3.org/TR/WGSL/) 作为方法依据，但未复制其实现或文档。

八个 GSAP Skill 经用户确认从 [GreenSock 的官方 `gsap-skills` 项目](https://github.com/greensock/gsap-skills)导入，仅保留其 `SKILL.md` 执行契约。该上游项目声明 MIT；本分类保留其 [MIT 通知](GSAP_SKILLS_LICENSE)。这不改变或替代 GSAP 运行库自身的许可与依赖要求。

仓库中可再许可的内容适用根目录 [MIT License](../LICENSE)；外部资料继续遵守其自身条款。

## 验证

从仓库根目录运行：

```powershell
$skills = @('celestial-body-formation-skill', 'gsap-core', 'gsap-timeline', 'gsap-scrolltrigger', 'gsap-plugins', 'gsap-utils', 'gsap-react', 'gsap-performance', 'gsap-frameworks')
foreach ($skill in $skills) {
  python -X utf8 -B "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" ".\60-visual-computing\$skill"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```
