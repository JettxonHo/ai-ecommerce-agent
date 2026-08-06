# DEC-024：Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State

> **Type:** Data Architecture / Workflow Architecture
> **Status:** Accepted — Amended by DEC-029 / DEC-046
> **Date:** 2026-07-28
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [Workflow State Specification（概念）](../specs/workflow/workflow-state-specification.md)
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** DEC-012 and DEC-013（补充细化状态与持久化边界，不推翻既有结论）
> **Amended By:** [DEC-029](dec-029-human-review-and-approved-strategy-contract.md)（Approved Strategy Current Truth transition）与 [DEC-046](dec-046-review-brief-and-export-product-contract.md)（Review Draft revision、正式输出不可变版本与导出快照行为）

---

## 用户确认

用户对 Workflow State Specification Proposal 明确回复：

> 确认

被接受的核心结论是：

> 每个用户业务任务拥有稳定的 `task_id`。LangGraph 使用独立的 `thread_id` 管理工作流执行、Checkpoint、Interrupt 和 Resume。
>
> 正式业务结果以版本化 Domain Objects 存入业务数据库，并通过 Current Truth Version Pointers 标记当前有效版本。LangGraph State 只保存当前执行所需的紧凑状态、阶段状态、业务对象引用、暂停信息和运行元数据。
>
> Checkpoint 用于工作流执行恢复，不作为产品唯一业务数据库。用户修改和模型重跑不得静默覆盖旧结果，而应生成新版本，并通过显式 Invalidation Event 使相关下游阶段失效。

---

## Decision

AI Ecommerce Agent 的状态架构正式划分为：

```text
Domain State
+
Workflow State
+
Runtime State
+
Interaction State
```

其中：

```text
Business Database
负责正式业务 Current Truth

LangGraph State
负责当前工作流执行所需的紧凑状态和业务引用

LangGraph Checkpointer
负责执行快照、Interrupt、Resume 和故障恢复

Frontend Interaction State
由业务状态和工作流状态组合产生
```

不得将以上状态职责混为一体。

### 1. Domain State

Domain State 表示产品当前认可和管理的业务对象。
至少包括：

- Product Facts；
- Customer Insights；
- Positioning Candidates；
- Approved Strategy；
- Marketing Brief；
- Xiaohongshu Brief；
- Sources；
- Source Fragments；
- Evidence Relationships；
- Review Decisions；
- User Modifications；
- Invalidation Events；
- Current Truth Version Pointers。

Domain State：

- 属于产品业务层；
- 不依赖 LangGraph；
- 必须存入正式业务数据库；
- 即使未来替换工作流框架，也必须继续存在；
- 是业务查询、前端展示和审计的主要来源。

### 2. Workflow State

Workflow State 表示工作流判断下一步执行动作所需要的状态。
至少包括：

- `task_id`；
- `thread_id`；
- `task_status`；
- `current_stage`；
- 各阶段状态；
- 当前业务版本引用；
- 输入和来源引用；
- 当前 Review 引用；
- Pause State；
- 最近错误；
- 最早需要重新执行的阶段；
- 必要的 Runtime Metadata。

Workflow State 应：

```text
compact
serializable
recoverable
reference-oriented
```

它不应成为所有业务内容和完整历史的容器。

### 3. Runtime State

Runtime State 表示某次工作流执行的信息。
概念上包括：

- `run_id`；
- 当前节点；
- 节点开始和完成时间；
- 当前 Checkpoint；
- 重试次数；
- 错误类型；
- 模型配置；
- Token 使用；
- 节点耗时；
- 运行进度；
- Skill、Prompt、Schema 和 Validator 版本。

Runtime State 主要用于：

- 故障恢复；
- 调试；
- 可观测性；
- 性能分析；
- 成本分析；
- 回归分析。

### 4. Interaction State

Interaction State 表示当前前端应该向用户展示的交互状态。
可能包括：

- 等待输入；
- 等待补充资料；
- 等待事实冲突处理；
- 等待人工审核；
- 当前审核包；
- 用户尚未提交的草稿；
- 运行进度；
- 当前允许执行的操作；
- 错误和恢复选项。

Interaction State 可以由 Domain State、Workflow State 和 Runtime State 组合生成。
它不能成为另一套独立的业务 Current Truth。

---

## Top-level Task State

概念顶层结构为：

```text
TaskState
├── identity
├── task_status
├── current_stage
├── input_refs
├── source_refs
├── stages
├── current_truth
├── review_state
├── pause_state
├── invalidation_state
└── runtime_metadata
```

可展开为：

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

以上是概念结构，不是最终 Python Schema 或数据库表。

---

## Task Status

任务级状态确定为以下概念集合：

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

- **draft：** 任务已经创建，但最低可运行输入尚未提交完整。
- **running：** 工作流正在执行节点。
- **waiting_for_input：** 当前阶段缺少必要资料，需要用户补充。
- **waiting_for_review：** 当前任务已到达强制 Human Review。
- **paused：** 因为冲突、风险、来源失效或其他需要人工处理的情况暂停。
- **completed：** 当前 MVP 定义的最终产物已经成功生成。
- **failed：** 系统错误导致任务无法自动继续，需要重试或人工恢复。
- **cancelled：** 用户主动取消任务。

`task_status` 只描述整个任务状态，不替代阶段级状态。

---

## Unified Stage State

所有主要业务阶段应尽量采用统一 Stage State 结构。
概念结构：

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

### Stage Status

阶段状态确定为以下概念集合：

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

- **not_started：** 尚未进入该阶段。
- **ready：** 前置条件已满足，可以运行。
- **running：** 阶段节点正在执行。
- **waiting_input：** 当前阶段缺少必要资料，需要用户补充。
- **waiting_review：** 当前阶段等待用户审核。
- **valid：** 阶段已经成功完成，其当前版本允许下游使用。
- **invalid：** 阶段曾经完成，但由于上游变化，其结果已经失效。
- **failed：** 阶段执行失败。
- **skipped：** 该阶段或阶段内部可选能力根据当前任务条件被合法跳过。

`skipped` 不得用于掩盖失败或资料不足。

---

## Versioned Domain Objects

正式业务结果不得通过直接覆盖的方式修改。
以下情况均应创建新版本：

- 模型首次生成；
- 用户修改；
- 用户审核后形成新版本；
- 模型重新生成；
- Prompt 或模型升级后的重新运行；
- 数据迁移；
- 来源更新后的重新计算。

每个业务版本概念上至少记录：

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

- **created_by** 概念取值：

```text
system
model
user
```

- **creation_type** 概念取值：

```text
initial_generation
user_edit
regeneration
review_approval
migration
```

- **version status** 概念取值：

```text
candidate
current
superseded
invalid
rejected
```

本决定确认版本化原则，不确认最终字段名称、Enum 或数据库实现。

---

## Current Truth Version Pointers

Task 级状态中必须明确保存当前有效业务版本指针。
概念结构：

```text
current_truth
├── facts_version_id
├── insights_version_id
├── positioning_version_id
├── approved_strategy_version_id
├── marketing_brief_version_id
└── xiaohongshu_brief_version_id
```

Current Truth Pointer 的作用是：

- 明确当前有效结果；
- 避免前端猜测最新版本；
- 避免下游节点读取历史结果；
- 支持版本追踪；
- 支持阶段失效；
- 支持局部重跑；
- 支持审核后的正式策略版本。

当某一层结果失效时：

- 保留历史版本；
- 清除或替换对应 Current Truth Pointer；
- 将对应阶段标记为 `invalid`；
- 阻止下游继续使用失效版本。

不得通过「字段是否为空」推断阶段有效性。

---

## Version Dependencies

每一个下游业务结果都必须记录其生成时依赖的上游版本。
例如：

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

在运行下游节点前，系统必须能够验证：
当前上游版本是否仍然与该结果生成时使用的版本一致。
若版本不一致，即使阶段被错误标记为 `valid`，前置条件 Validator 也应阻止继续执行。

---

## Invalidation Event

阶段失效必须显式记录。
概念结构：

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

例如：

```text
changed_entity_type: facts
old_version_id: facts_v1
new_version_id: facts_v2

invalidated_stages:
- customer_insight_analysis
- product_positioning
- human_review
- marketing_brief_generation
- xiaohongshu_brief_mapping
```

失效操作必须：

1. 保留旧业务版本；
2. 将对应 Stage 标记为 `invalid`；
3. 更新或清除 Current Truth Pointer；
4. 保存失效原因；
5. 记录触发者；
6. 找到最早需要重新执行的阶段；
7. 不删除历史结果；
8. 不重跑仍然有效的上游阶段。

### Accepted Invalidation Rules

继续遵循 DEC-009：

```text
Fact 修改
→ Insight、Positioning、Review、Marketing Brief、Platform Mapping 失效

Insight 修改
→ Positioning、Review、Marketing Brief、Platform Mapping 失效

Positioning 修改
→ Review、Marketing Brief、Platform Mapping 失效

已审核 Strategy 修改
→ Marketing Brief、Platform Mapping 失效

最终 Marketing Brief 修改
→ 不要求上游重跑

Xiaohongshu Brief 修改
→ 不要求重跑平台无关上游
```

其中 Human Review 在上游关键结果变化后应被标记为：

```text
superseded
```

或在最终 Schema 中采用语义等价状态。
最终 Review Status 名称尚未确认。

---

## User Modification Model

用户修改不得静默覆盖模型输出。
系统需要能够保存：

```text
model_generated_content
+
user_patch
+
resolved_content
```

或语义等价的版本关系。
至少必须能够回溯：

- 模型原始候选；
- 用户修改内容；
- 修改原因或评论；
- 修改后生成的业务版本；
- 哪些下游阶段因此失效。

该机制用于：

- 模型质量评估；
- 人工修改量统计；
- Prompt 回归；
- 错误分析；
- Human-in-the-loop 价值验证；
- 业务审计。

本决定确认需要保留以上信息，不确认最终采用 Patch、Diff 或完整快照。

---

## Review State

Human Review 使用独立结构化状态。
概念结构：

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

### Review Status

概念取值：

```text
not_ready
pending
in_progress
submitted
approved
changes_requested
superseded
```

### Review Decision

概念结构：

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

### Review Action

概念取值：

```text
accept
edit
reject
replace
request_more_information
```

Human Review 完成不意味着用户接受所有模型建议。
它意味着：
用户已经处理必要的事实、洞察和定位，并形成可供 Marketing Brief Generation 使用的已审核策略版本。

---

## Identifier Boundaries

### task_id

`task_id` 是长期稳定的产品业务 ID。
它表示：
用户创建的一个电商商品策略分析任务。

`task_id`：

- 属于 Domain Layer；
- 与 LangGraph 框架无关；
- 用于业务查询；
- 用于权限、审计和历史任务；
- 不因 Resume 或重新运行而改变。

### thread_id

`thread_id` 是 LangGraph 执行上下文 ID。
用于：

- Checkpoint；
- Interrupt；
- Resume；
- State History；
- 可选 Replay 或 Fork。

MVP 可以采用：

```text
一个 task_id
→ 一个当前活跃 thread_id
```

但 `task_id` 与 `thread_id` 不得被定义为相同概念。
未来一个 Task 可以关联：

- 主执行 Thread；
- 历史分支 Thread；
- 测试重跑 Thread；
- 数据迁移 Thread；
- 恢复 Thread。

### run_id

`run_id` 表示一次工作流调用或恢复执行。
例如：

```text
START 到 Human Review
→ run_id_1

Human Review Resume 到完成
→ run_id_2

用户修改 Fact 后重新运行
→ run_id_3
```

### checkpoint_id

`checkpoint_id` 表示 LangGraph Checkpointer 管理的具体执行快照。
它：

- 属于 Runtime Layer；
- 不作为产品主要业务 ID；
- 不直接替代业务版本 ID；
- 不作为前端主要导航身份。

---

## LangGraph State Content Boundary

LangGraph State 应优先保存：

- `task_id`；
- `thread_id`；
- `task_status`；
- `current_stage`；
- 各阶段 `StageState`；
- Current Truth Version IDs；
- Input IDs；
- Source IDs；
- Review ID；
- Pause State；
- Last Error；
- Earliest Invalid Stage；
- 必要的小型结构化节点结果；
- Runtime Metadata。

LangGraph State 不应直接保存：

- 完整 PDF；
- 图片或文件二进制；
- 全部评论原文；
- 完整 Embedding；
- 全部向量；
- 整个知识库；
- 全部业务历史版本；
- 无限增长的 Message History；
- 全量模型原始响应；
- 所有运行日志；
- API Key；
- 数据库连接；
- 不可序列化对象。

以上内容应存储在：

```text
Business Database
Object Storage
Retrieval Index
Run Log Storage
```

LangGraph State 只保存对应引用。

### Checkpointer and Business Database Boundary

**LangGraph Checkpointer** 负责保存：

- Graph State Snapshot；
- 当前执行位置；
- Interrupt；
- Resume 信息；
- 节点执行快照；
- State History；
- Runtime Recovery 信息。

**Business Database** 负责保存：

- Task；
- Inputs；
- Sources；
- Source Fragments；
- Facts Versions；
- Insights Versions；
- Positioning Versions；
- Approved Strategy Versions；
- Review Decisions；
- Marketing Brief Versions；
- Xiaohongshu Brief Versions；
- Current Truth Pointers；
- Invalidation Events；
- User Modifications；
- Audit Records。

### Product Query Rule

前端读取正式业务内容时，应以 Business Database 为主要数据来源。
不得将 LangGraph Checkpoint 数据库直接作为：

- 产品查询 API；
- 唯一业务数据库；
- 唯一 Current Truth；
- 唯一版本系统；
- 唯一审计系统。

### Reference-over-copy Principle

LangGraph State 中应优先保存：

```text
facts_version_id
```

而不是无限复制完整：

```text
facts[]
```

但在以下情况下，可以在 Graph State 中保存有限的小型结构化数据：

- 当前节点所需且体积较小；
- 避免频繁数据库读取；
- 不会成为长期唯一数据源；
- 可以由业务数据库重新构建；
- 不含大量历史；
- 不影响 Checkpoint 体积。

最终哪些字段保存内容、哪些只保存引用，需要在 Technical Spike 和最终 State Schema 中验证。

---

## Workflow Example

### Initial Run

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

### Human Review Resume

```text
9. Save Review Decisions
10. Create Approved Strategy Version
11. Review Stage → valid
12. Resume LangGraph
13. Marketing Brief Stage → valid
14. Xiaohongshu Mapping Stage → valid
15. Task → completed
```

### Upstream User Modification

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

## Accepted State Design Principles

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

## Reason

项目需要同时满足：

- 跨会话恢复；
- Human Review；
- 用户修改；
- 阶段失效；
- 局部重跑；
- 来源追踪；
- 版本审计；
- 模型效果评估；
- 框架可替换性。

如果将业务 Current Truth、LangGraph State 和 Checkpoint 混为一体，将产生：

- 业务查询依赖框架内部结构；
- 用户修改难以追踪；
- 阶段失效难以准确表达；
- Checkpoint 体积持续膨胀；
- 更换框架成本过高；
- 前端无法可靠判断当前有效版本；
- 运行恢复与产品版本冲突；
- 调试和审计困难。

因此采用：

```text
Versioned Domain State
+
Compact Workflow State
+
Persistent Runtime Checkpoint
+
Derived Interaction State
```

---

## Impact

该决定将影响：

- LangGraph State Schema；
- 数据库设计；
- Checkpointer；
- Node Adapter；
- Skill Input；
- Skill Output；
- Human Review；
- Invalidation；
- Partial Rerun；
- API；
- Frontend；
- Observability；
- Evaluation；
- Technical Spike；
- 数据迁移和版本管理。

后续设计必须回答：
数据属于正式业务 Current Truth、当前工作流执行状态、Runtime 恢复数据，还是临时前端交互状态？
在无法回答前，不应把字段直接加入 LangGraph State。

---

## Decision Boundary

本决定已经确认：

- 四类状态边界；
- `task_id` 是稳定业务 ID；
- `thread_id` 是 LangGraph 执行 ID；
- `run_id` 表示一次执行；
- `checkpoint_id` 是执行快照 ID；
- 一个 Task 可以在未来关联多个 Thread；
- 每个阶段使用统一 Stage State；
- Task Status 与 Stage Status 分离；
- 业务结果采用版本化；
- 用户修改生成新版本；
- Current Truth 使用 Version Pointer；
- 下游结果记录上游版本依赖；
- 阶段失效显式记录 Invalidation Event；
- 失效结果保留但禁止继续使用；
- Human Review 使用结构化 Review State；
- Checkpoint 与业务数据库分离；
- LangGraph State 保持紧凑并以引用为主；
- 大文件、长评论和向量不进入 Graph State；
- 前端正式业务查询以业务数据库为主。

本决定尚未确认：

- 最终字段名称；
- 最终 Python Schema；
- TypedDict、dataclass 或 Pydantic；
- PostgreSQL、MongoDB 或其他数据库；
- LangGraph Checkpointer 类型；
- 数据库表结构；
- `task_id` 生成格式；
- `thread_id` 生成格式；
- Version ID 格式；
- State Reducer；
- Snapshot 与 Patch 策略；
- Review Payload；
- 数据保留周期；
- 是否支持业务历史 Fork；
- API；
- 并发控制；
- 最终事务边界；
- Technical Spike 代码。

---

## Related Session

- [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)

## Related Decisions

- [DEC-008 — 分级证据标记与来源可追溯](dec-008-tiered-evidence-and-traceable-conclusions.md)
- [DEC-009 — 阶段失效与局部重跑](dec-009-stage-level-invalidation-and-partial-rerun.md)
- [DEC-012 — 结构化 Workflow State](dec-012-stage-state-and-structured-business-items.md)（本决定 Amends）
- [DEC-013 — 任务级持久化](dec-013-task-level-persistent-state-and-cross-session-resume.md)（本决定 Amends）
- [DEC-022 — Workflow Framework Capability Requirements](dec-022-workflow-framework-capability-requirements.md)
- [DEC-023 — 选择 LangGraph StateGraph](dec-023-select-langgraph-stategraph-for-mvp-workflow.md)

## Related RFC

None

## Supersedes

None

## Amends

DEC-012 and DEC-013 by adding detailed state and persistence boundaries.

---

## Notes

- 本决定为**概念层状态架构**确认：四类状态边界（Domain / Workflow / Runtime / Interaction）、版本化 Domain Objects、Current Truth Version Pointers、统一 Stage State、结构化 Review State、显式 Invalidation Event、四个标识符边界（`task_id` / `thread_id` / `run_id` / `checkpoint_id`）、Checkpointer 与业务数据库边界、紧凑 LangGraph State 与 Reference-over-copy 原则。
- 本决定 **Amends** DEC-012（细化 Workflow State 为四类状态、引入版本化与 Pointer）与 DEC-013（细化持久化为 Business Database vs Checkpointer 双层），**不推翻**两者既有结论，而是在其基础上补充更精细的状态与持久化边界。
- 本决定与 DEC-023 一致：承接「Checkpointer 仅执行恢复、业务数据库为 Current Truth、不得以 Checkpoint 库为唯一业务库」「Reducer 暂定整体替换 + 显式版本 + 幂等写入」。
- 概念 State Specification 见 [../specs/workflow/workflow-state-specification.md](../specs/workflow/workflow-state-specification.md)（仅概念 Schema / 状态 / 版本 / 边界，**不**含最终数据库 Schema / Python 代码 / Pydantic / TypedDict / Reducer / Checkpointer / API）。
- Development Status 保持 `NOT READY`。在 Source and Evidence Specification 确认前，不设计最终 RAG 实现；本决定未启动任何业务代码。
