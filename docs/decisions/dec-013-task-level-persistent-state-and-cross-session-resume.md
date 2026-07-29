# DEC-013：MVP 采用支持跨会话恢复的任务级持久化状态

## Type

Architecture

## Status

Accepted

## Decision

AI Ecommerce Agent 的 MVP 采用**任务级持久化状态**。

每一次商品定位分析与营销 Brief 生成流程，都应被视为一个独立任务，并拥有稳定的任务标识，例如：

```
task_id
```

系统需要在关键阶段保存 Workflow State，使用户能够：

- 暂停当前任务；
- 离开当前页面；
- 结束当前会话；
- 稍后重新打开任务；
- 查看当前状态；
- 继续人工审核；
- 提交修改；
- 从正确阶段恢复执行；
- 重新生成已经失效的下游阶段；
- 查看最终完成结果。

任务状态**不能**只存在于单次 HTTP 请求、LLM 上下文窗口或应用进程内存中。

## Task Lifecycle

MVP 的高层任务生命周期可以表达为：

```
created
→ processing_sources
→ generating_analysis
→ awaiting_review
→ review_submitted
→ regenerating
→ generating_final_brief
→ completed
```

异常状态可能包括：

```
paused_for_missing_information
paused_for_conflict
failed
cancelled
```

> 上述状态名称只是概念示意，**不是最终状态枚举**。

## Persistence Moments

系统至少应在以下关键时机保存任务状态。

### 1. 任务创建后

保存：任务标识、原始商品输入、推广目标、用户上传资料的引用、创建时间、初始工作流状态。

### 2. 来源资料处理后

保存：已识别来源、解析结果、来源片段、解析错误、缺失信息、检测到的资料冲突。

### 3. 分析草稿生成后

保存：事实层候选结果、洞察层候选结果、初步策略层、证据类型、来源关系、当前有效性状态。

### 4. 进入人工审核时

保存：`awaiting_review` 或语义等价状态、需要用户检查的内容、待验证假设、异常提醒、暂停原因、下一步允许的用户操作。

### 5. 用户完成修改或确认后

保存：用户修改内容、接受和否定的条目、已确认假设、审核时间、受影响阶段、需要从哪个阶段重新运行。

### 6. 阶段失效时

保存：哪些阶段已经失效、失效原因、由哪一项用户修改触发、推荐的重跑起点。

### 7. 局部重跑完成后

保存：新生成结果、当前有效阶段、重跑次数、运行耗时、错误信息、是否需要再次审核。

### 8. 最终 Brief 生成后

保存：当前有效的最终 Brief、用户最终编辑、完成状态、完成时间、评价相关运行数据。

### 9. 工作流发生异常时

保存：失败阶段、错误类型、错误信息、已完成状态、是否允许重试、推荐恢复位置。

## Cross-session Resume

MVP 需要支持以下用户场景：

```
用户提交商品资料
  → 系统生成分析草稿
  → 任务进入 awaiting_review
  → 用户关闭页面
  → 用户稍后重新进入任务
  → 系统恢复分析草稿与审核状态
  → 用户修改并确认
  → 系统继续生成最终 Brief
```

恢复时**不得**：

- 丢失原始输入；
- 丢失来源关系；
- 丢失用户已经完成的修改；
- 将失效内容重新标记为有效；
- 从错误的阶段重新执行；
- 重新创建一个与原任务无关的新任务。

## Persistence Scope

MVP 需要持久化的内容至少包括：

**任务与阶段状态**

- task_id、current_stage、workflow_status、review_status、pause_reason、rerun_from_stage、stage_validity。

**输入与来源**

- 原始商品输入、推广目标、上传资料引用、已解析来源、来源片段、缺失信息、冲突信息。

**四层业务结果**

- facts、insights、strategies、execution_brief。

**审核与修改**

- 用户修改、接受条目、否定条目、已确认假设、审核意见、审核时间。

**运行与评价信息**

- 运行次数、阶段耗时、失败信息、重跑记录、最终完成时间。

> 具体字段和存储结构仍需后续设计。

## In-memory State Boundary

内存状态**可以**用于：

- 单个节点执行中的临时变量；
- 当前请求中的计算缓存；
- 尚未形成业务意义的中间计算结果。

但内存**不能**作为以下内容的唯一保存位置：

- 人工审核任务；
- 当前有效四层结果；
- 来源与证据关系；
- 阶段有效性；
- 用户修改；
- 局部重跑位置；
- 任务完成状态。

## Event Sourcing Boundary

MVP **暂不实现**完整事件溯源系统。首版不要求将每一次状态变化都表达为独立领域事件，例如：

```
FactExtracted
FactEdited
InsightInvalidated
ReviewCompleted
StrategyRegenerated
```

MVP 也**暂不要求**：

- 恢复到任意历史时刻；
- 对所有状态变化进行事件重放；
- 建立复杂事件总线；
- 建立完整审计时间线；
- 支持多分支版本合并。

> 系统可以保存必要的运行历史和用户修改记录，但**不将完整 Event Sourcing 作为首版前置条件**。

## Version History Boundary

MVP **必须**区分：

- 当前有效状态；
- 当前失效状态；
- 用户修改后的状态。

但**尚未确认**是否向用户提供：

- 完整历史版本；
- 任意版本恢复；
- 修改前后差异比较；
- 多版本并行；
- 版本命名和发布。

> 旧结果可以在技术层面保留用于调试和审计，但**不得**与当前有效结果混淆。

## Recovery Principle

恢复任务时，系统需要基于持久化状态确定：

1. 当前任务处于哪个阶段；
2. 是否正在等待用户；
3. 是否存在异常暂停；
4. 哪些阶段有效；
5. 哪些阶段失效；
6. 是否存在用户尚未提交的修改；
7. 下一步应该等待用户、重跑或继续生成。

> 恢复逻辑**不能**仅依赖重新读取聊天记录并让 LLM 猜测当前进度。

## Reason

当前产品已经确认：存在强制人工审核节点；存在异常暂停；用户可能补充资料；用户可以修改分析结果；上游修改会使下游阶段失效；系统需要局部重跑；需要记录任务效率和运行指标。

如果状态只保存在内存中，将出现：页面关闭后任务丢失；服务重启后审核无法继续；用户修改无法可靠保存；阶段有效性丢失；无法判断从哪里重跑；无法形成真实的任务历史；难以支持产品评价指标。

完整事件溯源虽然能力更强，但会显著增加首个 MVP 的数据模型、开发和测试成本。任务级持久化能够满足真实 Human-in-the-loop 工作流，同时保持 MVP 范围可控。

## Impact

该决定将影响：系统架构、状态存储、工作流框架筛选、暂停与恢复机制、Checkpoint 需求、任务列表与任务详情、人工审核流程、局部重跑、错误恢复、运行历史、可观测性、评价指标采集、数据库选型、GitHub 基底仓库筛选、测试与验收标准。

> 后续框架和仓库筛选必须回答：它是否能够以任务或线程为单位持久化自定义结构化状态，并在人工暂停后可靠恢复？

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求（[../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)）

## Related RFC

None

## Supersedes

None

## Amends

None

## Decision Boundary

**本决定已经确认：**

- 每个商品分析流程拥有独立任务标识；
- 重要 Workflow State 必须持久化；
- 人工审核任务支持跨页面和跨会话恢复；
- 用户修改和阶段失效状态需要保存；
- 系统能够从正确阶段恢复；
- 内存不能作为重要业务状态的唯一存储位置；
- MVP 暂不实现完整事件溯源；
- MVP 暂不实现任意历史版本恢复。

**本决定尚未确认：**

- 是否采用 LangGraph Checkpointer；
- 是否采用 thread_id；
- 是否采用 PostgreSQL；
- 是否采用 SQLite；
- 是否采用 Redis；
- 是否同时使用关系数据库和对象存储；
- Checkpoint 保存频率；
- 状态序列化方式；
- 文件如何持久化；
- 任务保留期限；
- 数据删除机制；
- 数据隐私与权限；
- 并发编辑；
- 任务锁；
- 历史版本 UI；
- 最终 GitHub 基底仓库。

## Notes

- 用户于 2026-07-27 对该状态持久化原则明确回复「确认」，通过 Decision Gate。第三项 Architecture 决定（Type: Architecture，Session-002）。
- 对应 Session-002 Question-003（暂停与恢复需要达到什么程度）在**原则层**的回答——已确认需要**跨会话恢复**与**任务级持久化**。
- **未采用方案（保留为备选 / 暂缓，非永久禁止）：** 纯内存状态（未采用）；完整事件溯源（暂缓到后续版本）；任意历史版本恢复（暂缓）。
- 本决定确认的是**任务级持久化 + 跨会话恢复原则**；**不构成**对 LangGraph Checkpointer / thread_id / PostgreSQL / SQLite / Redis / 关系库+对象存储组合 / Checkpoint 频率 / 序列化方式 / 文件持久化 / 任务保留期限 / 删除机制 / 隐私权限 / 并发编辑 / 任务锁 / 版本 UI / 开源基底仓库的确认（见 Decision Boundary）。Task Lifecycle 与状态名为概念示意，非最终枚举。
- 与 [DEC-007](dec-007-single-review-node-and-exception-pauses.md)（审核暂停）、[DEC-009](dec-009-stage-level-invalidation-and-partial-rerun.md)（失效重跑）、[DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（确定性控制）、[DEC-012](dec-012-stage-state-and-structured-business-items.md)（状态结构）协同：持久化使这些能力在跨会话后仍然成立。
- **RFC 判断（暂不创建）：** 当前不创建 RFC；后续比较工作流框架及其持久化、暂停恢复能力时，可将 **DEC-011 / DEC-012 / DEC-013** 作为架构 RFC 的主要约束。
- 已同步至 [../architecture/system-architecture.md](../architecture/system-architecture.md)、[../architecture/data-architecture.md](../architecture/data-architecture.md)、[../architecture/integration-boundaries.md](../architecture/integration-boundaries.md)、[../agents/README.md](../agents/README.md)。无业务代码；Development Status 仍 NOT READY。
