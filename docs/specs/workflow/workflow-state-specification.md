# Workflow State Specification（工作流状态规格 — 概念）

> **Status: CONCEPTUAL — 仅记录概念 Schema、状态、版本与边界。**
> **本文件是 Current Truth Layer 的一部分。** 其内容只能来自用户明确接受的 Decision（来源：[DEC-024](../../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)；Review Draft revision、正式输出不可变版本与导出快照行为由 [DEC-046](../../decisions/dec-046-review-brief-and-export-product-contract.md) 修订）。
> 本文件**不**包含：最终数据库 Schema、Migration、LangGraph State Python 代码、Pydantic Models、TypedDict、Reducer、Checkpointer、API、正式业务 Graph。所有结构名为**概念示意，非最终数据契约 / 最终实现**。

---

## 1. 范围与来源

本规格记录 AI Ecommerce Agent 工作流状态的**概念层**结构，来源于 [DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](../../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)（Accepted，Data Architecture / Workflow Architecture，2026-07-28）。

承接：

- [DEC-008 — 分级证据标记与来源可追溯](../../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md)
- [DEC-009 — 阶段失效与局部重跑](../../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md)
- [DEC-012 — 结构化 Workflow State](../../decisions/dec-012-stage-state-and-structured-business-items.md)（被 DEC-024 补充细化）
- [DEC-013 — 任务级持久化](../../decisions/dec-013-task-level-persistent-state-and-cross-session-resume.md)（被 DEC-024 补充细化）
- [DEC-022 — 工作流框架能力需求](../../decisions/dec-022-workflow-framework-capability-requirements.md)
- [DEC-023 — 选择 LangGraph StateGraph](../../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)

> 当本规格与 DEC-024 冲突时，以 DEC-024 为准。本规格为 DEC-024 的概念展开，**不**新增任何决定。

---

## 2. 四类状态边界

```text
Domain State
+ Workflow State
+ Runtime State
+ Interaction State
```

| 状态类别 | 职责 | 主要存储 | 是否业务 Current Truth |
|----------|------|----------|------------------------|
| Domain State | 产品当前认可和管理的业务对象 | Business Database | **是**（权威来源） |
| Workflow State | 工作流判断下一步执行动作所需状态 | Compact LangGraph State | 否（紧凑、可重建、引用为主） |
| Runtime State | 某次工作流执行的信息 | LangGraph Checkpointer / Run Log | 否（恢复 / 调试 / 可观测性） |
| Interaction State | 当前前端应展示的交互状态 | 由前两类（加 Runtime）组合派生 | 否（派生产物，非独立 Truth） |

**不得**将以上状态职责混为一体。

### 2.1 Domain State

至少包括：Product Facts；Customer Insights；Positioning Candidates；Approved Strategy；Marketing Brief；Xiaohongshu Brief；Sources；Source Fragments；Evidence Relationships；Review Decisions；User Modifications；Invalidation Events；Current Truth Version Pointers。

属性：属于产品业务层；不依赖 LangGraph；必须存入正式业务数据库；即使替换工作流框架也必须继续存在；是业务查询、前端展示与审计的主要来源。

### 2.2 Workflow State

至少包括：`task_id`；`thread_id`；`task_status`；`current_stage`；各阶段状态；当前业务版本引用；输入与来源引用；当前 Review 引用；Pause State；最近错误；最早需要重新执行的阶段；必要的 Runtime Metadata。

属性：`compact` / `serializable` / `recoverable` / `reference-oriented`。不应成为所有业务内容和完整历史的容器。

### 2.3 Runtime State

概念上包括：`run_id`；当前节点；节点开始与完成时间；当前 Checkpoint；重试次数；错误类型；模型配置；Token 使用；节点耗时；运行进度；Skill / Prompt / Schema / Validator 版本。

用途：故障恢复；调试；可观测性；性能分析；成本分析；回归分析。

### 2.4 Interaction State

可能包括：等待输入；等待补充资料；等待事实冲突处理；等待人工审核；当前审核包；用户尚未提交的草稿；运行进度；当前允许执行的操作；错误与恢复选项。

由 Domain State、Workflow State 与 Runtime State 组合生成；**不**能成为另一套独立的业务 Current Truth。

---

## 3. 四个标识符边界

| 标识符 | 所属层 | 含义 | 是否稳定 |
|--------|--------|------|----------|
| `task_id` | Domain Layer | 长期稳定的产品业务 ID（一个电商商品策略分析任务）；与 LangGraph 框架无关；用于业务查询 / 权限 / 审计 / 历史任务；不因 Resume 或重新运行而改变 | 稳定 |
| `thread_id` | LangGraph 执行上下文 | LangGraph 执行上下文 ID；用于 Checkpoint / Interrupt / Resume / State History / 可选 Replay 或 Fork | MVP 内一个 task_id → 一个当前活跃 thread_id；未来可关联多 Thread |
| `run_id` | Runtime Layer | 一次工作流调用或恢复执行（如 START→Review 为 run_id_1；Resume→完成 为 run_id_2；改 Fact 重跑 为 run_id_3） | 每次执行 / 恢复不同 |
| `checkpoint_id` | Runtime Layer | LangGraph Checkpointer 管理的具体执行快照；不作产品主要业务 ID；不替代业务版本 ID；不作前端主要导航身份 | 每次快照不同 |

`task_id` 与 `thread_id` **不得**被定义为相同概念。

> **MVP 约定：** 一个 `task_id` → 一个当前活跃 `thread_id`。
> **未来扩展：** 一个 Task 可关联主执行 Thread / 历史分支 Thread / 测试重跑 Thread / 数据迁移 Thread / 恢复 Thread。

---

## 4. 顶层 Task State（概念）

```text
TaskState
├── task_id
├── thread_id
├── task_status
├── current_stage
├── input_refs[]
├── source_refs[]
│
├── stages
│   ├── product_intake_and_fact_extraction
│   ├── customer_insight_analysis
│   ├── product_positioning
│   ├── human_review
│   ├── marketing_brief_generation
│   └── xiaohongshu_brief_mapping
│
├── current_truth
│   ├── facts_version_id
│   ├── insights_version_id
│   ├── positioning_version_id
│   ├── approved_strategy_version_id
│   ├── marketing_brief_version_id
│   └── xiaohongshu_brief_version_id
│
├── review_state
├── pause_state
├── invalidation_events[]
└── runtime_metadata
```

**以上是概念结构，不是最终 Python Schema 或数据库表。**

---

## 5. Task Status（概念枚举）

```text
draft
running
waiting_for_input
waiting_for_review
paused
completed
failed
cancelled
```

| 取值 | 含义 |
|------|------|
| `draft` | 任务已创建，但最低可运行输入尚未提交完整 |
| `running` | 工作流正在执行节点 |
| `waiting_for_input` | 当前阶段缺少必要资料，需要用户补充 |
| `waiting_for_review` | 当前任务已到达强制 Human Review |
| `paused` | 因冲突 / 风险 / 来源失效或其他需人工处理的情况暂停 |
| `completed` | 当前 MVP 定义的最终产物已成功生成 |
| `failed` | 系统错误导致任务无法自动继续，需重试或人工恢复 |
| `cancelled` | 用户主动取消任务 |

`task_status` 只描述整个任务状态，**不替代**阶段级状态。

---

## 6. Unified Stage State（概念）

```text
StageState
├── stage_name
├── status
├── current_version_id
├── last_valid_version_id
├── based_on_versions
├── last_run_id
├── invalidation
├── error
├── started_at
├── completed_at
└── updated_at
```

### 6.1 Stage Status（概念枚举）

```text
not_started
ready
running
waiting_input
waiting_review
valid
invalid
failed
skipped
```

| 取值 | 含义 |
|------|------|
| `not_started` | 尚未进入该阶段 |
| `ready` | 前置条件已满足，可以运行 |
| `running` | 阶段节点正在执行 |
| `waiting_input` | 当前阶段缺少必要资料，需要用户补充 |
| `waiting_review` | 当前阶段等待用户审核 |
| `valid` | 阶段已成功完成，其当前版本允许下游使用 |
| `invalid` | 阶段曾完成，但由于上游变化，其结果已失效 |
| `failed` | 阶段执行失败 |
| `skipped` | 该阶段或阶段内部可选能力根据当前任务条件被合法跳过 |

> `skipped` **不得**用于掩盖失败或资料不足。

---

## 7. 版本化 Domain Objects（概念）

正式业务结果**不得**通过直接覆盖修改。以下情况均应创建新版本：模型首次生成 / 用户修改 / 用户审核后形成新版本 / 模型重新生成 / Prompt 或模型升级后重新运行 / 数据迁移 / 来源更新后重新计算。

### 7.1 业务版本概念字段

```text
version_id
task_id
version_number
created_by
creation_type
based_on_version_ids
source_refs[]
content
status
created_at
```

### 7.2 `created_by` 概念取值

```text
system
model
user
```

### 7.3 `creation_type` 概念取值

```text
initial_generation
user_edit
regeneration
review_approval
migration
```

### 7.4 `version status` 概念取值

```text
candidate
current
superseded
invalid
rejected
```

> 本节确认**版本化原则**，不确认最终字段名称、Enum 或数据库实现。

---

## 8. Current Truth Version Pointers（概念）

```text
current_truth
├── facts_version_id
├── insights_version_id
├── positioning_version_id
├── approved_strategy_version_id
├── marketing_brief_version_id
└── xiaohongshu_brief_version_id
```

作用：明确当前有效结果；避免前端猜测最新版本；避免下游节点读取历史结果；支持版本追踪 / 阶段失效 / 局部重跑 / 审核后的正式策略版本。

**失效时：** 保留历史版本；清除或替换对应 Pointer；将对应阶段标记为 `invalid`；阻止下游继续使用失效版本。

> **不得**通过「字段是否为空」推断阶段有效性。

---

## 9. Version Dependencies（概念）

每个下游业务结果必须记录其生成时依赖的上游版本：

```text
Insights Version
based_on:
- facts_version_id
- source_set_version_id
```

```text
Positioning Version
based_on:
- facts_version_id
- insights_version_id
- competitor_source_set_version_id
```

```text
Marketing Brief Version
based_on:
- approved_strategy_version_id
```

运行下游节点前，系统必须能验证当前上游版本是否仍与该结果生成时使用的版本一致。若不一致，即使阶段被错误标记为 `valid`，前置条件 Validator 也应阻止继续执行。

---

## 10. Invalidation Event（概念）

```text
InvalidationEvent
├── event_id
├── task_id
├── triggered_by
├── changed_entity_type
├── old_version_id
├── new_version_id
├── invalidated_stages[]
├── reason
├── created_at
└── applied
```

失效操作必须：① 保留旧业务版本；② 将对应 Stage 标记为 `invalid`；③ 更新或清除 Current Truth Pointer；④ 保存失效原因；⑤ 记录触发者；⑥ 找到最早需要重新执行的阶段；⑦ 不删除历史结果；⑧ 不重跑仍然有效的上游阶段。

### 10.1 Accepted Invalidation Rules（承接 DEC-009）

```text
Fact 修改      → Insight、Positioning、Review、Marketing Brief、Platform Mapping 失效
Insight 修改   → Positioning、Review、Marketing Brief、Platform Mapping 失效
Positioning 修改 → Review、Marketing Brief、Platform Mapping 失效
已审核 Strategy 修改 → Marketing Brief、Platform Mapping 失效
最终 Marketing Brief 修改 → 不要求上游重跑
Xiaohongshu Brief 修改 → 不要求重跑平台无关上游
```

> Human Review 在上游关键结果变化后应被标记为 `superseded`（或在最终 Schema 中采用语义等价状态）。最终 Review Status 名称尚未确认。

---

## 11. User Modification Model（概念）

用户修改**不得**静默覆盖模型输出。系统需能保存：

```text
model_generated_content
+
user_patch
+
resolved_content
```

或语义等价的版本关系。至少必须能回溯：模型原始候选 / 用户修改内容 / 修改原因或评论 / 修改后生成的业务版本 / 哪些下游阶段因此失效。

> 本节确认需要保留以上信息，**不**确认最终采用 Patch、Diff 或完整快照。

---

## 12. Review State（概念）

```text
ReviewState
├── review_id
├── status
├── review_package_version
├── reviewed_entities
├── user_decisions[]
├── unresolved_items[]
├── started_at
├── submitted_at
└── reviewer
```

### 12.1 Review Status（概念枚举）

```text
not_ready
pending
in_progress
submitted
approved
changes_requested
superseded
```

### 12.2 Review Decision（概念）

```text
ReviewDecision
├── entity_type
├── entity_id
├── action
├── original_version_id
├── resulting_version_id
├── comment
└── decided_at
```

### 12.3 Review Action（概念枚举）

```text
accept
edit
reject
replace
request_more_information
```

> Human Review 完成不意味着用户接受所有模型建议；它意味着用户已处理必要的事实 / 洞察 / 定位，并形成可供 Marketing Brief Generation 使用的**已审核策略版本**。

---

## 13. LangGraph State 内容边界

### 13.1 应优先保存

`task_id`；`thread_id`；`task_status`；`current_stage`；各阶段 `StageState`；Current Truth Version IDs；Input IDs；Source IDs；Review ID；Pause State；Last Error；Earliest Invalid Stage；必要的小型结构化节点结果；Runtime Metadata。

### 13.2 不应直接保存

完整 PDF；图片或文件二进制；全部评论原文；完整 Embedding；全部向量；整个知识库；全部业务历史版本；无限增长的 Message History；全量模型原始响应；所有运行日志；API Key；数据库连接；不可序列化对象。

以上内容存储于：

```text
Business Database
Object Storage
Retrieval Index
Run Log Storage
```

LangGraph State 只保存对应引用。

### 13.3 Checkpointer 与 Business Database 边界

| 层 | 负责 |
|----|------|
| LangGraph Checkpointer | Graph State Snapshot / 当前执行位置 / Interrupt / Resume 信息 / 节点执行快照 / State History / Runtime Recovery 信息 |
| Business Database | Task / Inputs / Sources / Source Fragments / Facts Versions / Insights Versions / Positioning Versions / Approved Strategy Versions / Review Decisions / Marketing Brief Versions / Xiaohongshu Brief Versions / Current Truth Pointers / Invalidation Events / User Modifications / Audit Records |

### 13.4 Product Query Rule

前端读取正式业务内容时，以 Business Database 为主要数据来源。不得将 LangGraph Checkpoint 数据库直接作为：产品查询 API / 唯一业务数据库 / 唯一 Current Truth / 唯一版本系统 / 唯一审计系统。

### 13.5 Reference-over-copy Principle

LangGraph State 优先保存 `facts_version_id`，而非无限复制完整 `facts[]`。

允许在 Graph State 中保存有限的小型结构化数据的条件：当前节点所需且体积较小 / 避免频繁数据库读取 / 不会成为长期唯一数据源 / 可由业务数据库重新构建 / 不含大量历史 / 不影响 Checkpoint 体积。

> 最终哪些字段保存内容、哪些只保存引用，需要在 Technical Spike 和最终 State Schema 中验证。

---

## 14. Workflow Example（概念行为）

### 14.1 Initial Run

```text
1. Create task_id
2. Create active thread_id
3. Save inputs and sources
4. Fact Stage → valid
5. Insight Stage → valid
6. Positioning Stage → valid
7. Review Stage → waiting_review
8. LangGraph interrupt
```

### 14.2 Human Review Resume

```text
9. Save Review Decisions
10. Create Approved Strategy Version
11. Review Stage → valid
12. Resume LangGraph
13. Marketing Brief Stage → valid
14. Xiaohongshu Mapping Stage → valid
15. Task → completed
```

### 14.3 Upstream User Modification

```text
16. Create new Facts Version
17. Create Invalidation Event
18. Insight Stage → invalid
19. Positioning Stage → invalid
20. Review State → superseded
21. Marketing Brief Stage → invalid
22. Xiaohongshu Mapping Stage → invalid
23. Clear invalid Current Truth Pointers
24. Set earliest rerun stage
25. Resume from Customer Insight Analysis
```

---

## 15. Accepted State Design Principles

1. **Reference over Copy** — Graph State 优先保存业务版本引用。
2. **Version over Overwrite** — 模型重跑和用户修改创建新版本。
3. **Explicit Validity** — 阶段有效性必须显式记录。
4. **Structured Domain State over Chat History** — 业务 Current Truth 使用结构化领域对象表达。
5. **Invalidation Does Not Mean Deletion** — 失效结果保留，但不能继续被下游使用。
6. **Recovery Is Separate from Business Truth** — Checkpoint 负责执行恢复，业务数据库负责正式结果。
7. **Validate Preconditions** — 每个节点运行前必须校验上游阶段和依赖版本。
8. **Compact Graph State** — 大文件、大文本、完整历史和向量通过引用访问。
9. **Stable Business Identity** — `task_id` 不依赖 LangGraph Runtime。
10. **Traceable Human Modification** — 用户修改必须能够回溯到模型原始版本和最终业务版本。

---

## 16. 明确不包含（Out of Scope）

本规格**不**包含以下内容（来源：DEC-024 归档要求）：

- 最终数据库 Schema；
- Migration；
- LangGraph State Python 代码；
- Pydantic Models；
- TypedDict 定义；
- Reducer 实现；
- Checkpointer 实现 / 类型选择；
- API；
- 正式业务 Graph。

以下选型**仍未确认**（不得在本规格中擅自选择）：PostgreSQL / MongoDB / Redis / SQLite / Checkpointer 类型 / Object Storage 供应商 / 向量数据库 / ORM。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得为使文档「完整」而补充未经讨论的字段或选型。
- 冲突时按 [../../governance/documentation-rules.md](../../governance/documentation-rules.md) 第 6 节优先级裁决；与 DEC-024 冲突时以 DEC-024 为准。
