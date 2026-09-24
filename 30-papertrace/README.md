# PaperTrace 外部入口

[中文](README.md) | [English](README.en.md) | [返回根 README](../README.md)

`30-papertrace/` 是外部项目导航目录，不保存 PaperTrace Skill 的正式源码。目录中的 `papertrace-skills.lnk` 只是仓库所有者机器上的便捷入口，在其他机器或克隆环境中可能无效。

## 项目定位

PaperTrace 维护论文证据抽取、双语阅读、学习画像、适应性教学、寓言教学、资讯简报和 HTML 展示等项目专属 Skill。当前源码、脚本和约束以 [PaperTrace skills](https://github.com/jiaqi-Sun2020/PaperTrace/tree/main/skills) 为准。

## 使用边界

- 不把 `.lnk` 文件当作可移植源码、依赖或安装机制。
- 不从本仓库修改快捷方式指向的外部项目。
- 不把 PaperTrace 项目专属 Skill 复制进本仓库制造第二份正式源码。
- 不在公开文档中记录快捷方式的机器绝对路径。
- 使用 PaperTrace Skill 前，读取其项目 README、Agent 规则和对应 `SKILL.md`。

## 维护方式

当 PaperTrace 的公开仓库位置或能力分类发生变化时，只更新本导航说明。外部项目的实现、测试和发布仍在 PaperTrace 仓库完成。
