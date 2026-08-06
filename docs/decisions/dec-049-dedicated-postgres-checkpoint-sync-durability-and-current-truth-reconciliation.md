# DEC-049：采用独立 PostgreSQL Checkpoint 数据库、同步持久性与 Current-Truth-first 对账

## Type

Workflow Architecture / Checkpoint Architecture / Recovery Architecture

## Status

Accepted

## Date

2026-08-06

## Decision

### 生产 Checkpointer 与存储边界

首个演示 MVP 的生产 Workflow Runtime 使用 LangGraph 官方 PostgreSQL Checkpointer：

- 采用 `langgraph-checkpoint-postgres` 的同步 `PostgresSaver`；
- Checkpoint 与业务数据使用同一个 PostgreSQL Service，但使用**独立 Checkpoint Database**；
- Checkpoint Database 使用独立 Runtime Role、Credential 与 Connection Pool，不与 Business Database 共用 Repository、Session 或事务；
- Checkpointer 的初始化、`setup` 与后续兼容性迁移由受控部署任务执行，不在 API / Worker 启动时隐式执行，也不纳入 Business Alembic migration chain；
- 最终包版本、PostgreSQL 版本范围与序列化兼容矩阵，须在 RFC-003 的兼容性证据完成后精确固定；本决定不授权安装依赖或执行迁移。

该物理部署复用 RFC-002 已接受的 PostgreSQL 能力，减少本地演示组件数量；独立 Database 保持 `Business Current Truth / Application Runtime Registry / LangGraph Checkpoint` 的职责与故障边界。

### 同步持久性与可重入节点

正式 Workflow 采用 LangGraph `sync` durability：每个已完成 Super-step 的 Checkpoint 持久化完成后，才继续后续执行。Graph State 保持紧凑、可序列化并以业务版本引用为主，不复制业务正文或 Current Truth。

节点必须按**可能从起点重新执行**设计：

1. `Prepare`：读取当前业务版本、建立执行身份与幂等意图，不产生不可逆业务效果；
2. `Execute`：执行模型、检索或工具调用；不得跨外部调用持有业务数据库事务；
3. `Commit`：通过 Application Command / Business Commit 路径重新校验版本、Lease / fencing、幂等身份与 Validator，并原子提交正式业务效果。

Checkpoint、Retry 或 Replay 不承诺 Node 或外部调用的 exactly-once。项目只承诺：在 Accepted RFC-002 事务与幂等约束下，重复执行不会产生重复或陈旧的 Business Current Truth 效果。

`Time Travel / Replay` 只用于从已有 Checkpoint 创建受控的新执行分支或调试，不等于 Business Restore，不得回退、覆盖或重新选择较旧的 Current Truth。

### Business-Current-Truth-first Reconciliation

Resume、Crash Recovery、Replay 或 Manual Recovery 前，Runtime 必须先以 PostgreSQL Business Current Truth 和 Application Runtime Registry 为准完成对账，再决定是否使用 Checkpoint。

对账至少读取并比较：

- 稳定的 `task_id` 与 `thread_id`；
- 本次新建的 `run_id`、执行 Attempt 与触发原因；
- Workflow Runtime Registry、Pending Durable Work Intent 与当前执行所有权；
- Checkpoint 的 Task / Thread ownership、Workflow Definition Version、State Schema Version 和输入版本引用；
- 当前 Source Set、Domain Current Truth Pointer、Stage validity、Invalidation、Review Package / Review Draft revision 与 Approved Strategy 状态；
- 请求的恢复动作是否仍然合法。

处理结果：

- **Compatible：** 同一 `thread_id` 可通过 LangGraph `Command(resume=...)` 或对应 crash-recovery 路径继续，但仍须在业务提交前重新验证当前版本与执行所有权；
- **Stale / Foreign / Incompatible：** 不得继续旧计划、不得写入 Business Current Truth、不得用 Checkpoint 覆盖新业务版本；应进入确定性局部重跑、创建新的安全执行分支，或建立 Manual Recovery Case；
- 对账结论写入 Application Runtime Registry / Recovery Record，不修改历史 Checkpoint 来伪造兼容状态。

Checkpoint 是恢复候选证据，不是恢复授权器。业务库中的 Current Truth、有效版本、审核状态、失效状态和 Accepted Application Command 始终优先。

## Alternatives Considered

### P-19B：Business Database 内独立 Schema

- 优点：数据库与 Credential 数量更少，初始配置最简单。
- 缺点：Business Alembic、Checkpointer setup、`search_path`、Pool 与权限边界容易耦合；Checkpoint 高写入量也更难独立诊断。
- 结论：不采用。

### P-19C：独立 PostgreSQL Service 或托管 Workflow Runtime

- 优点：故障和容量隔离最强。
- 缺点：超出本地演示需要，增加部署、Secret 与运维组件。
- 结论：不进入首个 Goal。

### P-20B：`async` durability

- 优点：Checkpoint 写入与执行重叠，吞吐更高。
- 缺点：进程故障时可能丢失最近的已执行步骤；首个演示更看重可解释恢复而非吞吐。
- 结论：不采用。

### P-20C：`exit` durability

- 优点：持久化开销最低。
- 缺点：不能满足跨会话 Interrupt / Resume 和节点级故障恢复要求。
- 结论：不采用。

### P-21B：Checkpoint-first 恢复

- 优点：Resume 路径短，更贴近框架默认状态。
- 缺点：可能把较旧输入、Review 或 Domain Version 当成有效状态，与 DEC-024 / DEC-033 冲突。
- 结论：不采用。

### P-21C：任何恢复都从头运行

- 优点：避免兼容旧 Checkpoint 的复杂度。
- 缺点：浪费模型调用，弱化 Human Review Resume，并可能重复外部调用。
- 结论：不采用；不兼容时优先从最早受影响阶段安全重跑，而非无条件全量重跑。

## Reason

官方 PostgreSQL Checkpointer 与当前同步 Python Runtime、RFC-002 PostgreSQL 基线和本地可复现演示最匹配。独立 Database 在不引入第二个数据库服务的前提下保留明确的权限、迁移和故障边界。

LangGraph 会在 Replay、Retry 与 Interrupt Resume 中重新执行 Checkpoint 之后的 Node；因此项目必须把 Node 设计为可重入，并把正式业务效果收口到可幂等、可再次校验的 Application Commit。`sync` durability 提供首个演示所需的清晰故障边界，而 Business-Current-Truth-first 对账防止框架状态越权成为业务事实。

## Impact

- RFC-003 必须以 `PostgresSaver` 同步路径、独立 Checkpoint Database、可重入 Node 与 Current-Truth-first Reconciliation 为已接受输入。
- RFC-003 仍须决定 Durable Dispatch、Worker Claim / Lease / Heartbeat、Cancellation、Compatibility / Upgrade 和验收测试；这些问题未关闭前，RFC-003 不能整体 Accepted。
- RFC-004 的 Resume API 必须映射到 RFC-003 的合法恢复动作，不得让客户端 Checkpoint 身份直接授权业务写入。
- RFC-007 必须观测 Checkpoint latency、Reconciliation outcome、stale / foreign / incompatible checkpoint 与恢复路径，但不得把 Checkpoint 内容当日志正文泄露。
- Readiness 的 TS-03 / ARP-06 必须验证 Checkpoint isolation 与 reconciliation；本决定不授权执行该 Spike。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

[RFC-003 — LangGraph Runtime and Checkpoint Architecture](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)（Drafting；整体尚未 Accepted）

## Official Capability Evidence

- [LangGraph persistence and PostgreSQL checkpointer](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangGraph checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [LangGraph Graph API durability and checkpoints](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph time travel and replay](https://docs.langchain.com/oss/python/langgraph/use-time-travel)

## Supersedes

None.

## Amends

- [DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)：为跨会话恢复选择生产 Checkpointer 部署边界和同步持久性。
- [DEC-023](dec-023-select-langgraph-stategraph-for-mvp-workflow.md)：在 StateGraph 选型上冻结生产 Checkpointer 类型与 Node 重执行约束。
- [DEC-024](dec-024-versioned-domain-state-and-compact-langgraph-state.md)：冻结紧凑 State 的生产持久化方式与 Current-Truth-first 对账，不改变 Domain / Workflow / Runtime / Interaction 四层职责。
- [DEC-033](dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)：将 Safe Resume 与 Checkpoint Reconciliation 收敛为具体的生产基线。

## Does Not Amend

- RFC-002 的 Business Database、Application Transaction、Durable Work Intent、Lease / fencing 与幂等规则继续有效。
- DEC-039 的适度校验约束继续有效；本决定不新增 Hash、SHA-256、内容指纹或不成比例的恢复变体。

## Decision Boundary

**本决定已经确认：**

- 同 PostgreSQL Service、独立 Checkpoint Database；
- 独立 Checkpoint Runtime Role、Credential、Pool 与迁移生命周期；
- 官方同步 `PostgresSaver`；
- 正式 Graph 使用 `sync` durability；
- 紧凑引用型 State、可重入 Node 与 `Prepare → Execute → Commit`；
- Node exactly-once 不作承诺，Business Effect 必须 duplicate-safe；
- Business-Current-Truth-first Reconciliation；
- compatible Resume 与 stale / foreign / incompatible 分流；
- Time Travel 不等于 Business Restore。

**本决定尚未确认：**

- 精确 LangGraph / Checkpointer / PostgreSQL 兼容版本；
- Durable Dispatch、Worker Claim、Lease / Heartbeat、Cancellation 与 Shutdown；
- Workflow / State Schema 兼容矩阵、Migrator 与不兼容升级流程；
- Checkpoint retention、清理、备份与恢复运维；
- 最终 Runtime Registry / Recovery Record / Checkpoint metadata Schema；
- RFC-003 验收测试、TS-03 具体场景与性能阈值。

## Notes

- 用户于 2026-08-06 明确接受 `P-19A`、`P-20A` 与 `P-21A`。
- Issue #46 / RFC-003 Draft PR 负责本决定与 Current Truth 的一致性归档。
- 本决定不接受 RFC-003 整体，不授权 Spike、依赖安装、数据库创建 / 迁移、业务实现或 Goal 激活。
