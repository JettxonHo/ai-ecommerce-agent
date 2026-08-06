# DEC-050：采用 PostgreSQL Durable Dispatch、Fenced Worker Ownership 与协作式取消

## Type

Workflow Runtime / Durable Dispatch / Worker Ownership / Cancellation

## Status

Accepted

> **Follow-up:** [DEC-051](dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md) 冻结与本决定配套的显式兼容、确定性恢复动作、迁移 / 回滚与验收证据；不改变本决定的 Dispatch、Ownership 或 Cancellation 语义。

## Date

2026-08-06

## Decision

### PostgreSQL Durable Work Intent 是调度权威来源

首个演示 MVP 使用 RFC-002 已接受的 Transactional Durable Work Intent 作为内部待执行工作的唯一权威来源：

- 产生业务变更与创建 Work Intent 必须遵守 RFC-002 的原子事务边界；
- Worker 使用短 PostgreSQL 事务，以 `FOR UPDATE SKIP LOCKED` 领取有界小批工作；
- Claim 事务只负责选择、建立执行所有权并持久化 Lease / fencing 信息，随后立即提交；
- 模型、检索、文件处理或其他外部调用均在 Claim 事务外执行；
- 数据库轮询是重新发现待处理工作的正确性基线；
- PostgreSQL `LISTEN / NOTIFY` 只可作为减少等待的可选 Wake-up 优化，不是可靠消息来源，也不能替代持久化 Work Intent；
- 首个 Goal 不引入独立 Broker、Relay 或进程内 Background Task 作为可靠调度基础。

公平性、空轮询退避、批大小和最大并发属于 RFC-007 / TS-01 的可调运维参数；本决定不机械固定秒数或数量。

### 数据库权威 Lease、Heartbeat 与单调 Fencing Token

每次成功 Claim 必须原子记录当前 `holder_id`、`lease_expires_at` 和单调递增的 `fencing_token`。执行所有权遵守：

1. Heartbeat、完成、释放和**由该 Worker 执行产生的**正式业务 Commit 均须条件校验当前 Holder 与 Fencing Token；
2. Heartbeat 使用短事务，不延长或复用外部调用期间的业务事务；
3. Lease 过期后，新 Worker 可通过新的 Claim 取得更高 Fencing Token；
4. 旧 Worker 即使在接管后返回，也不得完成 Work Intent、提交 Domain Version 或移动 Current Truth Pointer；
5. 失去 Lease 或 Fencing 校验失败属于明确的 Ownership Loss，不得用通用 Retry 掩盖；
6. Lease / Heartbeat 时长须在 TS-01 与 RFC-007 中按真实执行时间和故障恢复证据校准。

Lease 不是“任务一定只执行一次”的证明。系统仍只承诺在幂等 Application Command、Current Truth revision 和 Commit Fence 共同作用下，陈旧或重复执行不能形成重复或过期业务效果。

### 持久化协作式取消与 Supersession

运行中取消采用 durable cooperative cancellation，不以强杀 Worker / Thread 作为正确性机制：

- 取消、上游失效或新运行取代旧运行时，先持久化 `cancellation_requested` 或 `superseded` 意图；
- Worker 至少在 Claim 后、外部调用前后、Node 边界和正式 Commit 前检查取消、Supersession、Current Revision、Lease 与 Fencing；
- `cancellation_requested` 是请求态，不等于终态 `cancelled`；
- 只有当前 Holder 确认已停止且没有部分业务提交，或恢复流程证明旧 Lease 已失效且不存在仍可提交的 Owner，才可进入终态；
- 已经发出的 Provider 调用可能无法即时中断并最终返回；如果运行已取消、被取代或失去所有权，其结果必须丢弃，不得进入 Business Current Truth；
- 取消当前 Run 不删除先前仍有效的 Domain Version、Source、Review 或 Brief；Task 删除、保留和 Legal Hold 由独立 Retention Decision 处理。

用户可见的取消状态、轮询投影和错误协议由 RFC-004 冻结；日志、指标、超时与参数由 RFC-007 冻结。

## Alternatives Considered

### P-22B：Database Intent + 外部 Broker / Relay

- 优点：Wake-up 延迟与水平扩展能力更强。
- 缺点：新增 Relay、Broker、重复投递和第二套故障面，超出本地演示的最小运维边界。
- 结论：首个 Goal 不采用；出现经过测量的吞吐或延迟需求后再单独提案。

### P-22C：进程内 Background Task

- 优点：实现少、启动简单。
- 缺点：进程退出即丢失工作，不能满足 Durable Dispatch 与跨会话恢复。
- 结论：不得作为可靠调度机制。

### P-23B：只有 Claim 状态，无 Lease / Fencing

- 优点：Schema 与 Worker 逻辑较少。
- 缺点：崩溃后可能永久卡住，接管后旧 Worker 仍可能晚到提交。
- 结论：不采用。

### P-23C：Session-level Advisory Lock

- 优点：PostgreSQL 原生，获取和释放直接。
- 缺点：绑定连接生命周期，不能形成持久执行所有权；RFC-002 已禁止把它作为该正确性来源。
- 结论：不采用。

### P-24B：强制终止 Worker / Thread

- 优点：表面上的取消响应更快。
- 缺点：无法证明外部调用或事务的最终状态，可能留下未知副作用。
- 结论：不作为正确性机制；进程级终止只能是运维动作，仍须经过对账。

### P-24C：只允许执行前取消

- 优点：状态最少。
- 缺点：不能覆盖长任务运行中的取消、上游失效与 Supersession。
- 结论：不采用。

## Reason

该方案复用 RFC-002 已接受的 PostgreSQL 事务、Work Intent、幂等与并发基础，在不引入独立 Broker 的情况下提供可重新发现的工作、崩溃接管和陈旧 Worker 隔离。协作式取消承认外部调用不一定可中断，通过 Commit Fence 保护真正重要的 Business Current Truth，而不是堆叠不现实的强杀和 exactly-once 承诺。

## Consequences

### Positive

- API 提交成功后，进程崩溃不会让已持久化 Work Intent 静默丢失；
- Worker 可以在短事务和有界并发下安全竞争工作；
- Lease 接管后，旧 Worker 不能提交陈旧结果；
- 取消与 Supersession 不依赖 Provider 或 Python Thread 的即时终止能力；
- 本地演示栈保持 PostgreSQL + API + Worker，不新增 Broker。

### Costs and Risks

- Worker 需要 Claim、Heartbeat、Ownership Loss、Takeover 和 Commit Fence 路径；
- 外部调用期间可能发生重复计算，但不得形成重复业务效果；
- Lease、Heartbeat、轮询和批大小需要 TS-01 / RFC-007 证据校准；
- 取消可能是短暂的请求态，不能虚假宣称瞬时完成；
- Safe Resume Matrix、版本兼容、迁移、回滚与最终验证已由 DEC-051 冻结；精确实施版本、公共字段和运维参数仍待后续规划。

## Amendments and Relationships

- **Amends [DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)：** 将任务级恢复所需的 Durable Dispatch、执行所有权与运行中取消具体化；不改变 PostgreSQL Current Truth 和跨会话恢复目标。
- **Amends [DEC-033](dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)：** 在既有有界 Retry、安全恢复、事务幂等和 Manual Recovery 契约上冻结数据库 Claim、Lease / fencing 与取消 Commit Fence；不冻结 RFC-007 的具体运维参数。
- **Complements [DEC-049](dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md)：** DEC-049 冻结 Checkpoint 和对账权威，本决定冻结对账前后的工作发现与执行所有权。
- **Conforms to [RFC-002](../rfcs/rfc-002-persistence-and-transaction-architecture.md)：** 不新增与 RFC-002 冲突的队列、事务或 Advisory Lock 正确性来源。

## Authorization Boundary

本决定只授权 Decision / RFC / Current Truth / Readiness / Traceability 文档同步：

- 不接受 RFC-003 整体；
- 不授权创建 Work Intent 表、Worker、Claim SQL、Lease / Heartbeat、Cancellation API 或进程；
- 不授权安装 Broker、LangGraph Checkpointer 或其他运行依赖；
- 不授权创建或迁移任何数据库；
- 不授权执行 TS-01～TS-05；
- 不授权业务实现或长期 Goal。

## Accepted From

- Session-003：P-22A、P-23A、P-24A；用户于 2026-08-06 明确回复“接受 P-22A、P-23A、P-24A”。
- RFC-003 Draft：[LangGraph Runtime and Checkpoint Architecture](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)。
- GitHub：[Issue #46](https://github.com/JettxonHo/ai-ecommerce-agent/issues/46) / [Draft PR #47](https://github.com/JettxonHo/ai-ecommerce-agent/pull/47)。
