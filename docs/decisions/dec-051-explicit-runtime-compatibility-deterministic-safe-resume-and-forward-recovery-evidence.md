# DEC-051：采用显式运行时兼容、确定性安全恢复与前向恢复证据边界

## Type

Workflow Runtime / Compatibility / Safe Resume / Migration and Recovery Evidence

## Status

Accepted

## Date

2026-08-06

## Decision

### 显式 Compatibility Tuple 与受控前向升级

每个可恢复执行必须显式绑定以下兼容身份：

- `workflow_definition_version`；
- `graph_state_schema_version`；
- `serializer_profile_version`；
- 已验证的 Checkpointer Package 与 Store Schema 兼容范围。

实施时通过依赖锁文件与小型 Compatibility Matrix 固定经过验证的实际组合。Runtime 只能恢复明确判定为 `exact_compatible` 的状态，或使用已经测试的纯转换器处理 `upgradable` 状态；“依赖可以导入”或“框架尝试后未立即报错”都不是兼容证据。

升级顺序为 Preflight → 受控 Checkpointer Migration Task → 新 Runtime 健康验证 → 有界 Worker 切换。历史 Checkpoint 不原地改写。旧、新 Worker 只有在各自只领取兼容 Work Intent，且共同遵守 Lease / fencing 与最终 Commit Fence 时，才可短暂共存。不能证明兼容的执行进入局部重跑、新安全分支或人工恢复。

本决定冻结兼容策略和证据要求，不在策划阶段虚构精确包版本；具体 Python、LangGraph、Checkpointer 与 PostgreSQL 组合须在实施当时依据官方资料与 TS-03 证据固定。

### Current-Truth-first 确定性恢复判定

恢复请求先由 Application 层读取并对账：请求动作、Runtime Registry、Durable Work Intent 与执行所有权、Checkpoint metadata、Business Current Truth、Source / Review / Stage revisions、失效状态和幂等结果。恢复决定只能返回以下受控动作之一：

1. `resume_same_thread`：Checkpoint 与当前 Workflow / State / Serializer / Store、Task 归属、输入引用、Review / Stage 和执行所有权均兼容；
2. `reconcile_committed_result`：提交结果未知，但幂等记录与 Business Current Truth 能证明正式结果已提交，只修复运行状态；
3. `retry_current_stage`：技术失败可重试，输入与业务 revision 未变，以新 Attempt 延续同一逻辑幂等语义；
4. `rerun_from_earliest_invalid_stage`：Source、Domain、Review 或上游状态变化使旧计划陈旧，以新 Run / 安全执行分支从最早失效阶段重跑；
5. `restart_from_safe_boundary`：Checkpoint 缺失或不可用，但 Business Current Truth 能证明可重建的安全阶段边界；
6. `manual_recovery_required`：foreign、corrupt、无转换器的不兼容状态、未知外部副作用、所有权冲突或无法证明安全边界；
7. `reject_request`：陈旧 Review、非法状态转换、已取消 / 已取代运行或无权恢复的请求。

每次实际恢复保留稳定 `task_id` / `thread_id`，但创建新的 `run_id` 与 Attempt；同一逻辑操作可以复用幂等语义，不复用旧运行身份。API 与 Frontend 只提交恢复意图，不能指定 Checkpoint 作为恢复授权。恢复记录须保存选择原因、所读取的关键 revisions、选定动作和新的执行身份；正式业务 Commit 前仍执行 Current Truth、Cancellation、Lease、Fencing、Revision 与幂等校验。

### 风险切片证据包与前向恢复优先

RFC-003 在整体接受前冻结测试清单、证据格式和停止条件；实际测试执行进入长期 Goal 的 TS-01 / TS-03 及对应实现 Issues。本决定要求证据至少覆盖：

- 锁定的 Python、LangGraph、Checkpointer 与 PostgreSQL 组合及官方兼容依据；
- Checkpointer setup / migration 由受控部署任务执行，Worker 不隐式迁移；
- 真实 PostgreSQL 下的多 Worker claim、Lease expiry、takeover、stale commit rejection 与协作式取消；
- Interrupt / Resume、Node re-execution、Commit Outcome Unknown、stale / foreign / incompatible Checkpoint 与上述 Recovery Action Matrix；
- Checkpoint Database 与 Business Database 的 Role、Credential、Pool 和故障隔离；
- 旧 Runtime + 扩展后 Store Schema、新 Runtime + 扩展后 Store Schema、有界切换、失败停止与恢复演练。

迁移优先采用兼容扩展和 Forward Repair。只有证据证明旧 Runtime 与当前 Store Schema 兼容时才允许代码回滚；Vendor Migration 无安全降级路径时，Worker 停止领取新工作并 Roll Forward。Checkpoint Store 不可用时，只能从受控备份恢复，或依据 Business Current Truth / Runtime Registry 创建安全新运行；Checkpoint 永远不能晋升为业务真相。

以下任一现象发生时，相关生产模块必须停止，不得通过降低标准继续：stale Worker 成功提交、跨 Task Resume、过期 Review 被接受、取消后结果成为 Current Truth、Worker 隐式执行迁移、或恢复分支无法由记录解释。

## Alternatives Considered

### P-25B：始终用新 Runtime 尝试 Resume 旧 Checkpoint

- 优点：部署流程少。
- 缺点：兼容错误可能到执行中才暴露，并可能重放错误 Node 或状态。
- 结论：不采用。

### P-25C：升级时使所有旧 Checkpoint 失效并全量重跑

- 优点：无需维护转换器。
- 缺点：浪费模型调用，破坏 Human Review Resume，把可判定的局部恢复退化为全量重跑。
- 结论：不采用。

### P-26B：Checkpoint-first，框架能恢复就继续

- 优点：路径短。
- 缺点：可能绕过 Current Truth、Source、Review、Cancellation、Ownership 与 revision 变化。
- 结论：不采用。

### P-26C：所有异常都进入人工恢复

- 优点：自动分支少。
- 缺点：将普通、可确定判定的恢复机械化为人工阻塞，与演示可用性和适度校验原则不符。
- 结论：不采用。

### P-27B：仅以 In-memory Checkpointer 和单元测试验收

- 优点：快速、稳定。
- 缺点：不能验证真实 Store Schema、连接隔离、多 Worker、接管、迁移或崩溃恢复。
- 结论：不足以开放生产模块。

### P-27C：直接升级本地 Checkpoint Database，失败时清库

- 优点：步骤少。
- 缺点：无法保护等待审核和可恢复运行，也不能产生可复核的迁移与恢复证据。
- 结论：不采用。

## Reason

LangGraph Checkpoint 会参与 Interrupt / Resume、Replay 与 Node 重执行，但它不是 Business Current Truth。显式兼容身份和 Current-Truth-first 恢复判定把“框架能够加载状态”与“业务允许恢复”分离；前向恢复优先则避免把未经证明的 Vendor Schema 降级当作通用回滚方案。

该方案只覆盖真实核心风险：跨 Task 恢复、陈旧 Worker、过期 Review、取消后的晚到结果、迁移兼容与提交结果未知。它不引入 Hash、SHA-256、签名链或大量基本不可能出现的防御变体。

## Consequences

### Positive

- 兼容、恢复和迁移分支可解释、可审计、可测试；
- Checkpoint 不会绕过 Business Current Truth、Review、Revision、Lease 或 Fencing；
- 已提交结果能够对账而不重复业务效果；
- 不兼容状态可局部重跑或安全重启，不被迫全量重跑；
- Vendor Migration 无安全降级时拥有明确的停止和 Roll Forward 路径。

### Costs and Risks

- 需要维护小型 Compatibility Matrix、纯转换器和 Recovery Action Matrix；
- TS-01 / TS-03 必须使用真实 PostgreSQL 做并发、恢复和迁移证据；
- 最终 Runtime Registry / Recovery Record 字段与 API / Frontend 投影仍须 RFC-004 冻结；
- Checkpoint retention、备份周期和运维参数仍须 ARP-08 / RFC-007 冻结。

## Amendments and Relationships

- **Amends [DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)：** 将“从正确阶段恢复”具体化为显式兼容判断与确定性 Recovery Action，不改变任务级持久化目标。
- **Amends [DEC-033](dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)：** 冻结 Safe Resume、Compatibility、Migration / Rollback 与停止条件；不冻结 RFC-007 的具体运维参数。
- **Complements [DEC-049](dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md)：** DEC-049 冻结 Checkpoint 拓扑、Durability 与对账权威，本决定冻结兼容与恢复动作。
- **Complements [DEC-050](dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md)：** DEC-050 冻结工作发现、执行所有权与取消，本决定冻结接管、恢复和迁移时的兼容与证据。
- **Conforms to [RFC-002](../rfcs/rfc-002-persistence-and-transaction-architecture.md)：** 不改变 Business Database、事务、幂等、Durable Work Intent、Lease / fencing 或 Migration Governance。

## Authorization Boundary

本决定只授权 Decision / RFC / Current Truth / Readiness / Traceability 文档同步：

- 不接受 RFC-003 整体；
- 不固定未经实施证据验证的精确依赖版本；
- 不授权创建 Runtime Registry、Recovery Record、Compatibility Matrix 实例、转换器、Worker、Graph 或数据库；
- 不授权执行 Checkpointer setup / migration、TS-01～TS-05 或任何故障演练；
- 不授权业务实现、生产实现或长期 Goal；
- RFC-003 仍须完成最终一致性 Review，并由用户单独明确接受。

## Accepted From

- Session-003：P-25A、P-26A、P-27A；用户于 2026-08-06 明确回复“接受 P-25A、P-26A、P-27A”。
- RFC-003 Draft：[LangGraph Runtime and Checkpoint Architecture](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)。
- GitHub：[Issue #46](https://github.com/JettxonHo/ai-ecommerce-agent/issues/46) / [Draft PR #47](https://github.com/JettxonHo/ai-ecommerce-agent/pull/47)。
