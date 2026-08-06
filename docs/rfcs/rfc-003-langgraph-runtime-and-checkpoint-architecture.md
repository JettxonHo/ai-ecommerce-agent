# RFC-003：LangGraph Runtime and Checkpoint Architecture

## Metadata

- **Status:** IN REVIEW
- **Date:** 2026-08-06
- **Issue:** [#46](https://github.com/JettxonHo/ai-ecommerce-agent/issues/46)
- **Draft PR:** [#47](https://github.com/JettxonHo/ai-ecommerce-agent/pull/47)
- **RFC Acceptance:** NOT GRANTED
- **Implementation Authorization:** NOT GRANTED
- **Spike Execution Authorization:** NOT GRANTED
- **Goal Activation:** NOT GRANTED

## Problem

项目已经选择 Python 同步后端、LangGraph StateGraph 与 PostgreSQL Business Current Truth；DEC-049 / DEC-050 / DEC-051 已冻结生产 Checkpointer、持久性、Node 重执行、Checkpoint 对账、Durable Dispatch、Worker 所有权、协作式取消、Compatibility / Upgrade、Safe Resume Action Matrix，以及迁移 / 回滚与验收证据边界。DQ-01～DQ-09 已全部闭合；RFC-003 现进入最终一致性 Review，仍须用户单独明确接受，才能整体 Accepted。

## Context

RFC-003 必须同时满足：

- LangGraph Checkpoint 只负责执行恢复，不是 Business Current Truth；
- Graph State 紧凑、引用化，正式业务对象由 Business Repository 管理；
- Retry 不等于 Rerun，Checkpoint Resume 不得绕过 Validator、版本、Review 或事务；
- PostgreSQL Durable Work Intent 是 MVP 内部可靠调度的权威来源；
- Worker 的 Lease / fencing、幂等和并发写入须遵守 RFC-002；
- 首个交付是本地可复现的单工作区演示，不引入独立 Broker、Multi-Agent Runtime 或多区域容灾。

## Related Decisions and Specifications

- [DEC-013](../decisions/dec-013-task-level-persistent-state-and-cross-session-resume.md)
- [DEC-023](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)
- [DEC-024](../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)
- [DEC-033](../decisions/dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)
- [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md)
- [DEC-041](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md)
- [DEC-049](../decisions/dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md)
- [DEC-050](../decisions/dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md)
- [DEC-051](../decisions/dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md)
- [RFC-001](rfc-001-repository-and-application-architecture.md)
- [RFC-002](rfc-002-persistence-and-transaction-architecture.md)
- [Workflow Runtime Failure / Recovery Spec](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)

## Scope

- Production LangGraph Checkpointer 与数据库边界；
- Checkpoint durability、Node re-execution 与业务副作用边界；
- Durable Dispatch、Worker claim、Lease / fencing / heartbeat；
- Crash Recovery、Human Review Resume、Retry、Rerun 与 Cancellation；
- Checkpoint / Workflow / State Schema 版本兼容与升级；
- Current-Truth-first reconciliation；
- RFC-003 生产实现前的契约测试、集成测试与 TS-03 验证边界。

## Non-goals

- 不定义 Task / Run / Review HTTP API（RFC-004）；
- 不选择 Retrieval、LLM 或 Observability Provider（RFC-005 / 006 / 007）；
- 不引入独立 Message Broker、Temporal、Multi-Agent Supervisor 或多 Provider；
- 不实现 Checkpointer、Worker、Migration、Graph、API 或业务模块；
- 不执行 TS-01～TS-05；
- 不激活长期 Goal。

## Decision Status

| Decision Question | Status | Source |
|---|---|---|
| DQ-01 Checkpointer product and database topology | ACCEPTED INPUT | P-19A / DEC-049 |
| DQ-02 Durability and node re-execution contract | ACCEPTED INPUT | P-20A / DEC-049 |
| DQ-03 Checkpoint reconciliation authority | ACCEPTED INPUT | P-21A / DEC-049 |
| DQ-04 Durable dispatch and worker claim | ACCEPTED INPUT | P-22A / DEC-050 |
| DQ-05 Worker lease, fencing and heartbeat | ACCEPTED INPUT | P-23A / DEC-050 |
| DQ-06 Cancellation and supersession | ACCEPTED INPUT | P-24A / DEC-050 |
| DQ-07 Workflow / state compatibility and upgrade | ACCEPTED INPUT | P-25A / DEC-051 |
| DQ-08 Safe resume protocol and recovery action matrix | ACCEPTED INPUT | P-26A / DEC-051 |
| DQ-09 Testing, migration, rollback and acceptance evidence | ACCEPTED INPUT | P-27A / DEC-051 |

`ACCEPTED INPUT` 表示对应子决策已由用户接受；不表示 RFC-003 整体 Accepted。

## Accepted Inputs

### DQ-01 — P-19A：独立 Checkpoint Database

- 同一 PostgreSQL Service；独立 Checkpoint Database；
- 独立 Runtime Role、Credential 与 Pool；
- 官方同步 `langgraph-checkpoint-postgres` / `PostgresSaver`；
- Checkpointer setup / migration 由受控部署任务执行，不在 Worker 启动时隐式执行，不进入 Business Alembic chain；
- 精确兼容版本待 DQ-07 证据后固定。

### DQ-02 — P-20A：`sync` durability 与可重入 Node

- 正式 Graph 使用 `sync` durability；
- State 保持紧凑、引用化；
- Node 可从起点重执行，业务能力遵守 `Prepare → Execute → Commit`；
- 外部调用不跨 Business Transaction；
- 正式写入只经幂等 Application Command / Business Commit；
- 不承诺 Node exactly-once，只承诺 duplicate-safe Business Effect；
- Time Travel / Replay 不等于 Business Restore。

### DQ-03 — P-21A：Business-Current-Truth-first Reconciliation

- `task_id` / `thread_id` 稳定，每次调用、恢复或明确重跑创建新的 `run_id` 与 Attempt；
- Resume 前比较 Runtime Registry、Durable Work Intent、Checkpoint、当前业务版本、Review / Source / Stage / Invalidation 与恢复动作；
- compatible Checkpoint 可使用同一 `thread_id` Resume；
- stale / foreign / incompatible Checkpoint 不得写 Business Current Truth；
- 不兼容时进入确定性局部重跑、新安全分支或 Manual Recovery；
- 对账结果写入 Application Runtime Registry / Recovery Record，不篡改历史 Checkpoint。

### DQ-04 — P-22A：PostgreSQL Durable Work Intent + Poll-and-claim

- Transactional Durable Work Intent 是唯一权威待执行来源；
- Worker 以短事务和 `FOR UPDATE SKIP LOCKED` 领取有界小批工作；
- Claim / Lease / fencing 持久化后立即提交，外部执行不持有 Claim 或业务事务；
- 数据库轮询是正确性基线，`LISTEN / NOTIFY` 仅可作为可选 Wake-up；
- 首个 Goal 不引入独立 Broker 或进程内任务作为可靠调度来源。

### DQ-05 — P-23A：数据库权威 Lease + 单调 Fencing Token

- Claim 原子写入 `holder_id`、`lease_expires_at` 与单调递增 `fencing_token`；
- Heartbeat、完成、释放和由该 Worker 执行产生的业务 Commit 均验证当前 Holder + Token；
- Lease 过期后新 Owner 使用更高 Token，旧 Worker 不得提交；
- 执行在 Claim 事务外，Heartbeat 使用短事务；
- 具体时间参数留 TS-01 / RFC-007 按证据校准。

### DQ-06 — P-24A：持久化协作式取消 + Commit Fence

- 取消或取代先持久化 `cancellation_requested` / `superseded`；
- Worker 在外部调用前后、Node 边界和 Commit 前检查；
- 请求态不等于终态，须由当前 Owner 确认停止，或由恢复流程证明不存在可提交 Owner；
- 已发出的 Provider 调用可完成，但在取消、取代或 Ownership Loss 后必须丢弃结果；
- 取消 Run 不删除先前有效的业务版本，删除 / Retention 另行处理。

### DQ-07 — P-25A：显式 Compatibility Tuple + 受控前向升级

- 每个可恢复执行绑定 Workflow Definition、Graph State Schema、Serializer Profile 与已验证的 Checkpointer Package / Store Schema 兼容范围；
- 实施时由锁文件与 Compatibility Matrix 固定实际组合，不在策划阶段虚构精确依赖版本；
- 只 Resume `exact_compatible` 或存在已测试纯转换器的 `upgradable` 状态；
- 升级采用 Preflight → Checkpointer Migration Task → 新 Runtime 健康验证 → 有界 Worker 切换；
- 历史 Checkpoint 不原地改写；旧、新 Worker 只能领取各自兼容工作并共同遵守 Lease / fencing；
- 无法证明兼容时进入局部重跑、新安全分支或 Manual Recovery。

### DQ-08 — P-26A：Current-Truth-first Deterministic Recovery Decision

- Application 层先对账请求动作、Runtime Registry、Work Intent / Ownership、Checkpoint metadata、Current Truth、Source / Review / Stage revisions、失效状态和幂等结果；
- 恢复决定只返回 `resume_same_thread`、`reconcile_committed_result`、`retry_current_stage`、`rerun_from_earliest_invalid_stage`、`restart_from_safe_boundary`、`manual_recovery_required` 或 `reject_request`；
- 每次实际恢复保留稳定 `task_id` / `thread_id`，创建新的 `run_id` 与 Attempt；
- API / Frontend 只能表达恢复意图，不能把 Checkpoint ID 当作恢复授权；
- 恢复记录保存原因、关键 revisions、动作和新执行身份，正式 Commit 前仍执行最终 Fence。

### DQ-09 — P-27A：风险切片证据包 + 前向恢复优先

- RFC 接受前冻结测试清单、证据格式与停止条件；实际执行留给长期 Goal 的 TS-01 / TS-03 和实现 Issues；
- 真实 PostgreSQL 证据覆盖兼容组合、受控迁移、多 Worker、Lease 接管、陈旧提交拒绝、取消、Interrupt / Resume、Checkpoint 分类与 Recovery Action Matrix；
- 迁移优先兼容扩展与 Forward Repair；代码回滚须先证明旧 Runtime 与当前 Store Schema 兼容；
- Vendor Migration 无安全降级路径时停止领取新工作并 Roll Forward；
- Checkpoint Store 不可用时从受控备份恢复，或依据 Business Current Truth / Runtime Registry 创建安全新运行；
- stale Worker 成功提交、跨 Task Resume、过期 Review 被接受、取消后形成 Current Truth、隐式迁移或不可解释恢复分支均为停止条件。

## Accepted Decision Round 2 — Historical Proposal Detail

### P-22：Durable Dispatch and Worker Claim

#### P-22A（推荐）：PostgreSQL Durable Work Intent + Poll-and-claim

以 RFC-002 已接受的 Transactional Durable Work Intent 作为唯一权威待执行来源。Worker 用短事务和 `FOR UPDATE SKIP LOCKED` 领取小批任务，持久化 Claim / Lease / fencing 后立即提交，随后在事务外执行。轮询是正确性基线；PostgreSQL `LISTEN / NOTIFY` 只可作为减少等待的可选 Wake-up，不是消息可靠性来源。首个 Goal 不引入独立 Broker。

- 优点：与业务事务原子产生 Intent；本地栈简单；崩溃后可从数据库重新发现；符合 RFC-002。
- 缺点：需要设计公平性、空轮询退避和数据库负载；吞吐上限低于专用 Broker。

#### P-22B：Database Intent + 外部 Broker 投递

数据库仍为权威，Relay 将 Intent 投递到 Broker，Worker 消费 Broker 后回查数据库。

- 优点：Wake-up 与水平扩展能力较强。
- 缺点：新增 Relay、Broker、重复投递和两套故障面；不符合首个本地演示的最小运维边界。

#### P-22C：进程内 Background Task

- 优点：实现最少、延迟低。
- 缺点：进程退出即丢失工作，不能提供跨会话恢复和 Durable Dispatch。

**Recommendation:** P-22A。

### P-23：Worker Lease, Fencing and Heartbeat

#### P-23A（推荐）：数据库权威 Lease + 单调 Fencing Token

每次 Claim 原子写入 `holder_id`、`lease_expires_at` 与单调递增 `fencing_token`。Heartbeat、完成、释放和业务 Commit 都必须以当前 Holder + Token 做条件校验。Lease 过期后允许新 Worker 以更高 Token 接管；旧 Worker 即使晚到，也不能提交 Current Truth。执行在 Claim 事务外完成；Heartbeat 使用短事务。具体 Lease / Heartbeat 秒数在 TS-01 与 RFC-007 运维参数中校准，不在本轮机械固定。

- 优点：进程崩溃后可恢复；能明确拒绝 stale Worker；与 RFC-002 并发模型一致。
- 缺点：需要时钟、续租与接管测试；参数过短会误接管，过长会延迟恢复。

#### P-23B：只有 Claim 状态，无 Lease / Fencing

- 优点：Schema 和 Worker 逻辑较少。
- 缺点：崩溃后容易永久卡住；旧 Worker 可能在接管后提交。

#### P-23C：Session-level Advisory Lock

- 优点：PostgreSQL 原生，获取释放简单。
- 缺点：绑定连接生命周期、难以表达持久执行所有权，且已被 RFC-002 禁止作为该正确性来源。

**Recommendation:** P-23A。

### P-24：Cancellation and Supersession

#### P-24A（推荐）：持久化协作式取消 + Commit Fence

取消先写入 durable `cancellation_requested` 或 `superseded` 意图；Worker 在领取后、外部调用前后、Node 边界和 Commit 前检查。`cancellation_requested` 不等于终态 `cancelled`：只有当前 Holder 确认已停止且无部分业务提交，或恢复流程确认旧 Lease 已失效且不存在可提交 Owner 后，才进入终态。已经发出的 Provider 调用可能完成，但其结果必须被 fencing / revision / cancellation check 丢弃，不能成为 Current Truth。取消当前 Run 不删除既有有效业务版本；Task 删除与数据保留由独立 Retention 决策处理。

- 优点：不依赖 Python 强杀语义；能覆盖外部调用无法即时中断的现实情况；无部分写入。
- 缺点：取消可能不是瞬时完成；所有安全边界和 Commit 路径必须配合检查。

#### P-24B：强制终止 Worker / Thread

- 优点：表面响应快。
- 缺点：无法证明外部调用和事务状态，容易留下不确定状态；不适合作为正确性机制。

#### P-24C：只允许执行前取消

- 优点：最简单。
- 缺点：不能满足长任务运行中的用户取消、失效与 Supersession。

**Recommendation:** P-24A。

P-22A / P-23A / P-24A 已于 2026-08-06 被用户明确接受并归档为 [DEC-050](../decisions/dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md)。以上备选与取舍保留为历史决策证据，不再是待确认提案。

## Accepted Decision Round 3 — Historical Proposal Detail

### P-25：Workflow / State Compatibility and Upgrade

#### P-25A（推荐）：显式 Compatibility Tuple + 受控前向升级

每个可恢复执行记录显式绑定 `workflow_definition_version`、`graph_state_schema_version`、`serializer_profile_version` 与已验证的 Checkpointer Package / Store Schema 兼容范围。部署前以锁文件和 Compatibility Matrix 固定实际组合；Runtime 只对明确标记为 `exact_compatible` 或存在已测试纯转换器的 `upgradable` 状态执行 Resume。升级采用 Preflight → Checkpointer Migration Task → 新 Runtime 健康验证 → 有界 Worker 切换；历史 Checkpoint 不原地改写。旧、新 Worker 只有在各自只领取兼容 Work Intent 且共同遵守 Lease / fencing 时才可短暂共存。不兼容执行进入局部重跑、新安全分支或 Manual Recovery。

- 优点：兼容判断可审计；支持安全滚动切换；不把“包能导入”误当成旧状态可恢复。
- 缺点：需要维护小型 Compatibility Matrix、转换器和部署前证据；升级速度低于直接覆盖。

#### P-25B：始终尝试用新 Runtime Resume 旧 Checkpoint

- 优点：部署流程最少。
- 缺点：Node、State、Serializer 或 Store Schema 变化可能在运行中才暴露，并可能重执行错误路径。

#### P-25C：每次升级都使全部旧 Checkpoint 失效并从头运行

- 优点：不维护兼容转换器。
- 缺点：浪费模型调用，破坏 Human Review Resume，也会把安全局部恢复退化为全量重跑。

**Recommendation:** P-25A。

### P-26：Safe Resume Protocol and Recovery Action Matrix

#### P-26A（推荐）：Current-Truth-first Deterministic Recovery Decision

建立一个应用层确定性 Recovery Decision，先读取请求动作、Runtime Registry、Work Intent / Ownership、Checkpoint metadata、Current Truth / Source / Review / Stage revision 和幂等结果，再且只返回以下受控动作之一。每次实际恢复调用继续遵守 DQ-03：保留稳定 `task_id` / `thread_id`，创建新的 `run_id` 与 Attempt；相同逻辑操作可复用幂等语义，但不复用旧运行身份。

1. `resume_same_thread`：Checkpoint、Workflow / State 版本、任务归属、当前 Review / Stage 与输入引用均兼容，并能取得有效执行所有权；
2. `reconcile_committed_result`：Commit Outcome Unknown，但 Idempotency / Business Current Truth 能证明正式结果已提交，只回收运行状态，不重做业务效果；
3. `retry_current_stage`：可重试技术失败，输入与业务 revision 未变，使用新的 Attempt 记录并继续遵守同一幂等语义；
4. `rerun_from_earliest_invalid_stage`：Source / Domain / Review 变化使旧计划陈旧，创建新 Run / 安全执行分支，从最早失效阶段重跑；
5. `restart_from_safe_boundary`：Checkpoint 缺失或不能使用，但 Current Truth 能证明一个可重建的安全阶段边界；
6. `manual_recovery_required`：foreign / corrupt / 无转换器的不兼容状态、未知外部副作用、所有权冲突或无法证明安全边界；
7. `reject_request`：陈旧 Review、非法状态转换、已取消 / 已取代运行或无权限恢复请求。

API / Frontend 只能请求恢复意图，不能指定 Checkpoint 作为恢复授权。每次决定记录原因、读取的业务 revision、选择动作和新执行身份；Resume 后仍在 Commit 前执行最终 Fence。

- 优点：把框架 Resume、业务重试、局部重跑和人工恢复分开；行为可测试、可解释。
- 缺点：需要明确状态映射与场景测试；公共错误和投影仍需 RFC-004 对齐。

#### P-26B：Checkpoint-first，框架能 Resume 就继续

- 优点：路径短。
- 缺点：会绕过 Source、Review、Current Truth、Cancellation 与 Ownership 变化。

#### P-26C：所有异常均转 Manual Recovery

- 优点：自动路径最保守。
- 缺点：把已知可判定的普通恢复机械化为人工阻塞，不符合演示可用性和适度校验原则。

**Recommendation:** P-26A。

### P-27：Testing, Migration, Rollback and Acceptance Evidence

#### P-27A（推荐）：风险切片证据包 + Forward-compatible Rollback Matrix

RFC-003 接受前冻结测试清单和证据格式；实际执行留给长期 Goal 的 TS-01 / TS-03 与对应实现 Issues。证据至少覆盖：

- 锁定的 Python、LangGraph、Checkpointer 与 PostgreSQL 组合及官方兼容依据；
- Checkpointer setup / migration 由部署任务执行且 Worker 不隐式迁移；
- 真实 PostgreSQL 下的多 Worker claim、Lease expiry、takeover、stale commit rejection 与协作式取消；
- Interrupt / Resume、Node re-execution、Commit Outcome Unknown、陈旧 / foreign / incompatible Checkpoint 与 P-26 Action Matrix；
- Checkpoint Database 与 Business Database 的 Role / Pool / 故障隔离；
- 旧 Runtime + 扩展后 Schema、新 Runtime + 扩展后 Schema、停止旧 Worker、失败切换与恢复演练。

迁移优先使用兼容扩展和前向修复。代码回滚只有在旧 Runtime 与当前 Store Schema 的兼容性已被证据证明时允许；若 Vendor Migration 不支持安全降级，则停止领取新工作并 Roll Forward。Checkpoint Store 不可用时，从受控备份恢复或依据 Business Current Truth / Runtime Registry 创建安全新运行，绝不把 Checkpoint 提升为业务真相。任何 stale Worker 成功提交、跨 Task Resume、过期 Review 被接受、取消后形成 Current Truth、迁移隐式发生或无法解释的恢复分支都属于停止条件。

- 优点：验证真正的并发、恢复和迁移风险；回滚路径不依赖未经证明的数据库降级。
- 缺点：需要真实 PostgreSQL 和受控故障演练；实施成本高于单元测试。

#### P-27B：仅使用 In-memory Checkpointer 与单元测试验收

- 优点：快速、稳定。
- 缺点：不能验证 PostgreSQL Store Schema、连接隔离、多 Worker 或崩溃接管，不足以开放生产模块。

#### P-27C：直接升级本地 Checkpoint Database，失败时人工清库

- 优点：步骤少。
- 缺点：无法保护等待审核和可恢复运行，也不能产生可复核的迁移 / 回滚证据。

**Recommendation:** P-27A。

P-25A / P-26A / P-27A 已于 2026-08-06 被用户明确接受并归档为 [DEC-051](../decisions/dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md)。以上备选与取舍保留为历史决策证据，不再是待确认提案。

## Architecture Boundaries

- Checkpoint Database、Application Runtime Registry 与 Business Database 不共用职责或事务。
- LangGraph Node Adapter 可以调用 Application Service；Skill Service 不直接读写 Checkpoint。
- Worker / Checkpointer 不能直接创建 Domain Version、移动 Current Truth Pointer 或接受 Review。
- 所有正式业务写入仍由 RFC-002 的 Application Transaction / UoW / Idempotency / Lease / fencing 规则控制。
- API 只能请求动作并读取投影；不能把客户端提交的 Checkpoint ID 当恢复授权。

## Error and Recovery Boundaries

- Transient 技术故障可在同一逻辑身份下有界 Retry；业务输入、版本或配置变化使用 Rerun。
- Checkpoint missing / stale / foreign / incompatible 是分类结果，不用通用异常吞掉。
- Resume 前后均可能发现业务状态变化；Commit 前验证是最终防线。
- 未知外部 Side Effect 不盲目 Retry；进入确定性对账或 Manual Recovery。
- 任何 Recovery 不得绕过 Validator、Review、Current Truth Pointer、expected revision、Lease 或 fencing。

## Security and Proportional Validation

- Checkpoint Credential 仅注入 Workflow Runtime，不能进入 Graph State、Checkpoint payload、日志、Issue 或 PR。
- 独立 Database Role 只授予 Checkpointer 所需权限；Business Role 不依赖 Checkpoint tables。
- 不在本 RFC 引入内容 Hash、SHA-256、签名链或极低概率恢复变体。
- 安全、异常和性能测试聚焦跨 Task 隔离、stale Worker、陈旧 Resume、取消与迁移等真实核心风险。

## Testing Strategy — Accepted Planning Boundary

最终接受前至少需要规划并授权以下证据；本 Draft 不执行测试：

- Checkpointer setup / migration 可重复执行与 Worker 不隐式迁移；
- 同 `thread_id` Interrupt / Resume 与 crash recovery；
- Node 重执行不产生重复 Domain Version 或外部业务效果；
- Checkpoint Database 与 Business Database 权限、Pool 和故障隔离；
- stale / foreign / incompatible Checkpoint 全部在业务写入前拒绝；
- Durable Work Intent 多 Worker Claim、Lease expiry、fencing takeover 与 stale Worker commit rejection；
- Cancellation / Supersession 无部分 Current Truth；
- Workflow / State Schema 升级、回滚与不兼容停止；
- Checkpoint unavailable / slow / migration mismatch 的用户和运维恢复行为。

其中 Checkpoint Isolation / Reconciliation 的生产风险验证进入 TS-03 Charter；真实 PostgreSQL 多 Worker并发进入 TS-01。Spike 失败时停止对应生产模块，不降低验收标准继续。

## Migration and Rollback — Accepted Planning Boundary

- 实施时须以官方资料、锁文件与 TS-03 证据冻结 Checkpointer package / PostgreSQL / Workflow Definition / State Schema 的实际兼容矩阵；
- setup / migration 必须有 preflight、备份 / 恢复边界、失败停止和 rollback / roll-forward 说明；
- Graph / State 不兼容时不得让旧 Worker 与新 Worker同时处理同一执行所有权；
- 不通过修改历史 Checkpoint 伪造升级成功。

## Operational Impact — Planning Baseline

- 本地演示新增一个 Checkpoint Database、独立 Credential 与 Pool，但不新增 PostgreSQL Service 或 Broker；
- API 与 Worker 是独立进程；Worker 数量与并发保持有界；
- RFC-007 负责最终日志、Trace、Metrics、告警、Timeout / Backoff / Lease 参数与 Runbook；
- Checkpoint retention、备份与恢复边界须与 ARP-08 保留 / 删除规划一致。

## Blocking Dependencies

- RFC-001 / RFC-002 = ACCEPTED；
- DQ-01～DQ-09 已全部关闭；
- ARP-06 Checkpoint Reconciliation Artifact 与 TS-03 Charter 完成；
- Final Consistency Review 证明与 RFC-001 / 002、DEC-024 / 033 / 049 / 050 / 051 及 RFC-004 边界无冲突；
- 用户明确接受 RFC-003。

## Open Questions

- Workflow Definition / State Schema / Serializer / Checkpointer 的精确实施版本、Compatibility Matrix 实例与所需转换器；
- Runtime Registry / Recovery Record 的最终公共字段，以及 RFC-004 的状态 / 错误投影；
- Checkpoint retention、cleanup、backup / restore 与 operator recovery；
- 最终测试命令、TS-03 场景、迁移演练、性能基线和停止条件。

## Final Consistency Review（PASS，2026-08-06）

> **Review Status:** PASS · **Decision Conflict:** NONE FOUND · **Review is not RFC Acceptance or implementation authorization.**

- **Decision completeness:** DQ-01～DQ-09 均有 Chosen Option、Rejected Alternatives、Trade-offs 与 Accepted Decision 来源；没有未决 RFC-003 子决策。
- **Internal consistency:** Checkpoint 始终是 Runtime State，不是 Business Current Truth；Durability、Node 重执行、Dispatch、Lease / fencing、Cancellation、Compatibility、Recovery Action 与 Migration / Recovery 形成一致闭环。
- **Accepted architecture alignment:** 与 RFC-001 / RFC-002、DEC-013 / 023 / 024 / 033 / 039 / 049 / 050 / 051 一致；Business Transaction、Idempotency、Current Truth、Review Revision 与 Worker Ownership 边界未被绕过。
- **Later-RFC separation:** RFC-004 继续拥有公共 API / 状态 / 错误与恢复请求协议；RFC-007 继续拥有运维参数与 Observability；ARP-06 / TS-03、ARP-08 和 TS-01 继续拥有各自证据与生命周期规划。
- **Proportional validation:** 证据聚焦跨 Task Resume、stale Worker、陈旧 Review、Cancellation late result、Migration compatibility 与 Commit Outcome Unknown；未新增 Hash / SHA-256 要求或低概率防御变体。
- **Authorization boundary:** RFC-003 仍为 `IN REVIEW`；Implementation、Spike Execution 与 Goal Activation 均为 `NOT GRANTED`。全部 DQ Accepted、PR Merge 或检查通过均不能替代用户接受 RFC 整体。
- **Independent review:** 独立审阅 Agent 按 correctness / readability / architecture / security / performance-ops 五轴复核实际文件，Blocking = 0、Non-blocking = 0，最终 PASS。
- **Verification:** 141 份 Markdown、1,436 个本地链接、0 个损坏；`git diff --check`、Format、Lint、Type、Import Contracts、Architecture、Unit、Contract、Fast Suite、Lockfile、Package Build、isolated import 与 Dependency Audit 均通过。PR Required Checks 在最新 Commit 推送后重新确认。

## User Acceptance Gate

RFC-003 只有在以下条件全部满足后才可进入最终用户接受：

1. DQ-01～DQ-09 均有明确 Chosen Option、Rejected Alternatives 与 Trade-offs；
2. 兼容、迁移、Rollback、测试与停止条件完整；
3. 与 Accepted DEC、RFC-001 / 002、Current Specs 和后续 RFC 边界一致；
4. 独立五轴 Review 与文档链接校验通过；
5. 用户明确回复接受 RFC-003。

PR Merge、Required Checks 通过、DEC-049 / DEC-050 / DEC-051 Accepted 或全部 DQ Accepted，均不能替代 RFC-003 整体接受，也不授权实现、Spike 或 Goal。
