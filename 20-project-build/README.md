# 项目构建架构

[中文](README.md) | [English](README.en.md) | [返回根 README](../README.md)

**20-project-build/** 收录六个面向研究项目接入、治理、持续管理和交付检查
的中央 Skill。本文档是该目录的技术架构入口；仓库级 Skill 总览、安装和其他
类别请见根 [README](../README.md)。

> 本目录定义可复用的职责、数据合同和只读验证边界。它不执行研究任务、不选择
> 领域方法，也不会仅因某个检查通过而授予执行、发布或科学主张权限。

## 框架流程简介

### 一次性项目接入

```text
项目目录
  ↓
research-project-pipeline：只读发现
  ↓
research-workspace-governance：位置、资产、合同与迁移设计
  ↓
人工审核：确认精确写入、风险和回退
  ↓
project-agent-generator-skill：仅在缺少框架时创建 .agents
  ↓
重新发现与分轴验证
  ↓
交接给日常研究管理
```

Onboarding Pipeline 只编排，不执行研究任务。Governance 不创建 Agent 入口；
Generator 只负责一次性框架创建或受限 Bootstrap，不负责日常更新。已有安全
Agent 框架时不重新生成。接入通过只说明接入合同满足，不产生实验、发布或
科学主张授权。

### 接入后的重复研究管理

```text
research-management-pipeline
  ↓
定位唯一治理根与合同注册表
  ↓
research-workspace-governance 只读验证
  ↓
汇总 SCI / STAT / ENG / GOV 合同
  ↓
汇总七条独立状态轴与 amendment 失效范围
  ↓
选择一个最小下一动作
  ├─ experiment-protocol-audit / 领域专家
  ├─ neat-freak：项目信息更新
  ├─ project-submission-audit：最终变更面
  └─ 人工审批或补充证据
```

Management Pipeline 重复读取事实并路由下一步，但不执行 Adapter、创建
`.agents`、选择领域方法或签发授权。`neat-freak` 和 `handoff` 位于
`50-core-utils`，只作为明确的外部衔接点，不成为本目录的合同 owner。

### 工程修复闭环

本目录不新增 `project-engineering-repair` Skill。Workspace Governance 通过
additive sidecar 合同拥有 `engineering-repair-record/v1`、
`engineering-execution-plan/v1`、`engineering-execution-receipt/v1` 和
`github-actions-evidence/v1`；Management Pipeline 只路由下一动作；项目代码或
获授权 operator 复现、诊断和实施；Submission Audit 最终只读复核。execution
receipt 的 `operator` 与 `delegation` 同时承担 operator receipt，避免重复事实源。

```text
工程修复：reported → reproduced → diagnosed → planned → approved → fixed
          → locally_verified → ci_verified → closed
运行授权：not_started → awaiting_authorization → prepared
          → awaiting_authorization → canary_passed
          → awaiting_authorization → full_authorized
```

两条状态机独立；`blocked`、`stale`、`rolled_back` 显式记录异常。单测、commit、
push、CI 和修复关闭都不能自动授权 formal prepare、数据生成、canary 或完整实验。
事务和 Windows 路径规则见
[transaction safety](research-workspace-governance/references/transaction-safety.md)，
Git/Actions 规则见
[engineering operations](research-management-pipeline/references/engineering-operations.md)。

| 当前情况 | 正确入口 |
|---|---|
| 新项目或尚未完成接入的遗留项目 | `research-project-pipeline` |
| 已有唯一安全 Agent 文档包，只缺受管启动加载 | Onboarding Pipeline 的 `bootstrap-only` 分支 |
| 已接入，合同、方法、证据或环境发生变化 | `research-management-pipeline` |
| 需要独立核验显式领域协议和规范化证据 | `experiment-protocol-audit` |
| 准备 commit、PR、release、交付或交接 | `project-submission-audit`，按需再使用 `handoff` |
| 工程故障需要证据化修复与验证 | `research-management-pipeline` 路由，Governance 验证记录，获授权 operator 实施 |

## 组件与职责树

~~~text
20-project-build/
├── project-agent-generator-skill
│   └── 仅一次：创建缺失 Agent 框架与受管启动加载
├── research-project-pipeline
│   └── 仅一次：发现 → 治理设计 → 人工审核 → 受控接入 → 验证
├── research-workspace-governance
│   └── 持续：合同注册表、资产边界、状态、修订、失效影响与追踪矩阵
├── research-management-pipeline
│   └── 接入后重复：读取治理结果，选择并路由一个最小下一动作
├── experiment-protocol-audit
│   └── 独立只读：核验显式 Profile、Protocol、清单与运行证据
└── project-submission-audit
    └── 最终只读：审计将提交、交付或交接的实际变更面
~~~

| 组件 | 唯一职责 | 明确不做 |
|---|---|---|
| [Generator](project-agent-generator-skill/SKILL.md) | 首次创建缺失 .agents 框架；对唯一既有安全文档包可只补缺失 Bootstrap | 日常刷新知识、合并冲突的启动文件、创建根 AGENTS.md |
| [Onboarding Pipeline](research-project-pipeline/SKILL.md) | 一次性发现、设计、审核和协调受控接入 | 重复管理研究生命周期、执行研究或定义领域方法 |
| [Workspace Governance](research-workspace-governance/SKILL.md) | 合同、位置、资产、修订、状态、授权引用和派生追踪 | 执行合同中的命令、推断科学结论或替代领域评审 |
| [Management Pipeline](research-management-pipeline/SKILL.md) | 接入后把事实、缺口和门禁路由为一个最小下一动作 | 执行研究、Adapter、Agent 生成、方法选择或授权 |
| [Protocol Audit](experiment-protocol-audit/SKILL.md) | 用显式机器可读输入独立核验协议与证据一致性 | 运行实验、Adapter 或项目命令 |
| [Submission Audit](project-submission-audit/SKILL.md) | 对精确变更面给出 PASS、BLOCKED 或 INCOMPLETE | commit、push、发布或建立科学有效性 |

[Neat-Freak](../50-core-utils/neat-freak/SKILL.md) 在接入后维护项目知识与
已标记启动接线；[Handoff](../50-core-utils/handoff/SKILL.md) 生成受控的后续
交接。它们不是本目录的合同 owner。

## 四类合同

合同分类用于分配责任，不要求每个项目实例化每一项。领域 Profile 可以增加
命名空间合同，但必须归入一个已有类别并指向权威定义。

~~~text
research-contract-registry/v1              Governance 拥有的单一事实源
├── SCI  科学有效性                         SCI-01 … SCI-09
│   └── 问题、机制、测量定义、比较、反驳、主张范围与领域验证
├── STAT 证据设计                           STAT-01 … STAT-13
│   └── 证据选择、重复/依赖、缺失性、不确定性、稳健性与分析计划
├── ENG  实现与工件完整性                  ENG-01 … ENG-17
│   └── Schema、身份、工作图、来源、环境、可复现性、恢复、发布与访问
│       └── ENG-08.1 … ENG-08.6：工具链、仪器、精度、隔离、资源与跨环境比较
└── GOV  权限与生命周期治理                 GOV-01 … GOV-14
    └── 边界、优先级、审核、停止条件、保留、证据准入、修订、伦理与更正
~~~

**跨类别规则：一个事实只有一个规范性 owner。**其他类别只能引用它。例如
SCI-03 定义测量含义，ENG-08.2 记录仪器状态，GOV-13 记录适用审批；三者不能
相互替代或重复定义。完整编号和责任见
[合同分类](research-workspace-governance/references/contract-taxonomy.md)。

## 注册表、证据与状态树

**research-project-contract/v3** 可以通过 **contract_registry_path** 指向
治理根内唯一的 **research-contract-registry/v1** JSON 文件。注册表及其
字符串、路径和引用均为不可信数据，不能作为 Agent 指令或可执行命令。

~~~text
Project Contract
└── contract_registry_path
    └── Contract Registry
        ├── Profile / Protocol references       领域定义仍归领域 owner
        ├── applicable SCI / STAT / ENG / GOV instances
        │   ├── definition and dependency references
        │   ├── implementation / verification / work references
        │   ├── evidence / claim / authorization / deliverable references
        │   └── required gates
        ├── append-only amendments
        │   └── reverse dependency impact → 当前项标记 stale，历史记录保留
        └── derived traceability matrix          派生视图，绝非第二份手工状态表
~~~

每个合同实例分别保存和报告下列状态轴：

~~~text
definition_state       定义是否草拟、审核、冻结或已被替代
implementation_state   声明的实现引用状态
verification_state     技术或审查验证状态
work_state             工作是否实际完成及其偏差
evidence_state         证据是否被验证、准入、缺失或陈旧
claim_state            独立评审后的支持、反驳、拒绝或未支持
authorization_state    可追溯决定所声明的授权状态
~~~

这些轴彼此独立：成功退出码、匹配哈希、PASS、完成工作或证据准入都只证明其
声明范围。claim_ceiling 仅限制可审查的最大主张范围，不产生 claim_state；
实际授权也不能仅由注册表文本产生。

## 详细生命周期与路由规则

~~~text
尚未接入的项目
└── Research Project Pipeline
    ├── Workspace Governance：发现与治理设计
    ├── 人工审核：精确写入、风险与回退
    ├── Generator：仅创建缺失框架或受限 Bootstrap
    └── Neat-Freak：知识与加载验收

已接入的项目
└── Research Management Pipeline
    ├── Governance：合同覆盖、状态、修订和失效影响
    ├── Protocol Audit / 领域专家：协议、证据及主张语义
    ├── 项目代码或获授权操作员：实际研究工作
    └── Neat-Freak：项目知识变化

交付、发布、更正或归档
└── Submission Audit → Handoff（需要继续时）→ Governance 的保留/更正边界
~~~

| 决策阶段 | 允许路由 | 不会自动发生 |
|---|---|---|
| 发现与范围界定 | Governance inventory；列出事实、未知项和风险 | 根据名称推断科学含义或授权 |
| 合同实例化 | Governance registry；声明 required/optional/not-applicable/unresolved | 强迫理论、定性或综述项目提供不适用工件 |
| 方法与证据设计 | Domain Profile/专家；必要时 Protocol Audit | 由 Governance 选择领域方法 |
| 执行准备与实际工作 | 项目代码、仪器或获授权操作员 | 因注册表含有命令便执行它 |
| 证据、主张与交付 | 独立评审、Submission Audit、Handoff | 将完成、交接或发布等同于科学支持 |

未解决的合同只阻止依赖它的动作；安全的无关只读分析可继续。修订必须追加
amendment 并计算反向依赖影响，不能重写历史 PASS、证据或结论记录。

## 人工审核点

每个门禁都应同时保留机器可读状态和普通研究人员能判断的摘要。摘要至少说明
当前审核对象、必须审核的原因、应查看的证据、通过标准、驳回条件以及下一步。

| 审核点 | 审核什么与为什么 | 通过意味着 | 驳回与最小修正 |
|---|---|---|---|
| 接入写入 | 精确目标路径、将创建或修改的文件、冲突、风险和回退；避免覆盖既有项目事实 | 仅允许执行已批准的接入写入 | 修正路径、缩小写入面或补齐回退后重新预览 |
| 合同与治理 | 合同适用性、owner、依赖、状态来源、证据引用和 amendment 影响；避免多 owner 与陈旧状态 | 该作用域可按当前治理状态继续 | 补定义、裁决歧义或标记受影响项 stale，不改写历史记录 |
| 领域协议与主张 | 方法语义、规范化证据、缺口、反例和 claim boundary；避免把结构合法当成科学有效 | 只在已审核范围内接受领域结果或主张状态 | 交回领域专家补证据、修协议或降低主张范围 |
| 提交与交付 | 实际变更面、未记录的合同语义变化、失效传播和未解决阻塞项；避免漏交或越权发布 | 变更面可进入下一项明确批准动作 | 修复阻塞项或排除不应提交的内容；不会自动 commit、push 或发布 |

审核冲突必须显式呈现并交由有权人员裁决。通过某一门禁不代表其他门禁通过，
驳回也只阻塞依赖该决定的动作。

## 实际使用入口

以下命令均从仓库根目录运行。先生成并审核计划；没有用户批准时不执行写入：

```powershell
$projectRoot = 'D:\path\to\project'
$pipeline = '.\20-project-build\research-project-pipeline\scripts\research_pipeline.py'
$plan = Join-Path $env:TEMP ('research-onboarding-' + [guid]::NewGuid().ToString('N') + '.json')

python -X utf8 -B $pipeline plan $projectRoot --profile minimal --output $plan
python -X utf8 -B $pipeline verify $projectRoot
```

如果项目缺少 Agent 框架，应先审阅计划中的写入、风险、回退和
`plan_sha256`，再按 `research-project-pipeline/SKILL.md` 的审批合同执行
`bootstrap-agents --apply`。若项目已有唯一安全文档包，只缺 Bootstrap，则使用
哈希绑定的 `bootstrap-only` 预览和应用，不改写知识文件。

接入后的重复管理通过 `research-management-pipeline` 读取 Governance 结果并
返回一个最小下一动作。日常文档和长期知识更新交给 `neat-freak`；提交前审计与
`handoff` 分开调用，任何 PASS 都不会自动 commit、push 或发布。

## 只读合同接口

在仓库根目录运行。以下命令仅输出 JSON，不创建目标项目目录、不执行研究代码：

~~~powershell
Set-Location 'C:\path\to\codex-skill-hub'
$projectRoot = 'D:\path\to\project'
$registry = '.agents\governance\contract_registry.json'
$validator = '.\20-project-build\research-workspace-governance\scripts\validate_contract_registry.py'

python -X utf8 -B $validator validate $projectRoot --registry $registry
python -X utf8 -B $validator matrix $projectRoot --registry $registry
python -X utf8 -B $validator impact $projectRoot --registry $registry --change-id 'change-001'
~~~

工程修复 sidecar 记录使用独立的只读验证器；记录路径相对于项目根：

~~~powershell
$repairValidator = '.\20-project-build\research-workspace-governance\scripts\validate_engineering_records.py'
python -X utf8 -B $repairValidator bundle $projectRoot --record '.agents/governance/repairs/ENG-001.json' --plan '.agents/governance/plans/ENG-001.json' --receipt '.agents/governance/receipts/ENG-001.json' --ci-evidence '.agents/governance/evidence/ENG-001-ci.json'
~~~

退出码 0 表示结构和交叉绑定完整，1 表示 incomplete、failed 或 stale，2 表示
输入不安全或 invalid。输出始终声明 `commands_executed: false`。

退出码 0 表示所请求的结构/追踪评估完整，1 表示评估完成但有不完整或失败发现，
2 表示输入不安全或无法评估。任一结果都不授权执行、发布或科学结论。接口细节
见 [合同追踪](research-workspace-governance/references/contract-traceability.md)
和 [生命周期路由](research-management-pipeline/references/lifecycle-interface.md)。

## 使用边界

- 新项目或遗留项目接入：从 Research Project Pipeline 开始，不从持续管理
  Pipeline 开始。
- 日常项目说明、长期知识与既有受管启动接线：使用 Neat-Freak，不重新生成框架。
- 科学定义、协议语义、证据解释与 Claim Review：由领域 Profile、领域 Skill 或
  具名专家负责。
- 提交前：由 Submission Audit 审查实际 staged、unstaged 和 untracked 变更面；
  只有用户可授权 commit、push 或发布。
