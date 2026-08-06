# RFC-003：LangGraph Runtime and Checkpoint Architecture

## Metadata

- **Status:** DRAFTING
- **Date:** 2026-08-06
- **Issue:** [#46](https://github.com/JettxonHo/ai-ecommerce-agent/issues/46)
- **Draft PR:** Pending
- **RFC Acceptance:** NOT GRANTED
- **Implementation Authorization:** NOT GRANTED
- **Spike Execution Authorization:** NOT GRANTED
- **Goal Activation:** NOT GRANTED

## Problem

项目已经选择 Python 同步后端、LangGraph StateGraph、PostgreSQL Business Current Truth、事务化 Durable Work Intent 与跨会话恢复，但仍需冻结生产 Checkpointer、持久性、Node 重执行、Worker 调度、执行所有权、取消、兼容升级和 Checkpoint 对账，才能安全实现 Workflow Runtime。

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
| DQ-04 Durable dispatch and worker claim | PROPOSED | P-22A below |
| DQ-05 Worker lease, fencing and heartbeat | PROPOSED | P-23A below |
| DQ-06 Cancellation and supersession | PROPOSED | P-24A below |
| DQ-07 Workflow / state compatibility and upgrade | OPEN QUESTION | Next decision round |
| DQ-08 Safe resume protocol and recovery action matrix | OPEN QUESTION | Later decision round |
| DQ-09 Testing, migration, rollback and acceptance evidence | OPEN QUESTION | Later decision round |

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

## Proposed Decision Round 2

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

## Testing Strategy — Draft

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

## Migration and Rollback — Open

- DQ-07 须冻结 Checkpointer package / PostgreSQL / Workflow Definition / State Schema 的兼容矩阵；
- setup / migration 必须有 preflight、备份 / 恢复边界、失败停止和 rollback / roll-forward 说明；
- Graph / State 不兼容时不得让旧 Worker 与新 Worker同时处理同一执行所有权；
- 不通过修改历史 Checkpoint 伪造升级成功。

## Operational Impact — Draft

- 本地演示新增一个 Checkpoint Database、独立 Credential 与 Pool，但不新增 PostgreSQL Service 或 Broker；
- API 与 Worker 是独立进程；Worker 数量与并发保持有界；
- RFC-007 负责最终日志、Trace、Metrics、告警、Timeout / Backoff / Lease 参数与 Runbook；
- Checkpoint retention、备份与恢复边界须与 ARP-08 保留 / 删除规划一致。

## Blocking Dependencies

- RFC-001 / RFC-002 = ACCEPTED；
- DQ-04～DQ-09 全部关闭；
- ARP-06 Checkpoint Reconciliation Artifact 与 TS-03 Charter 完成；
- Final Consistency Review 证明与 RFC-001 / 002、DEC-024 / 033 / 049 及 RFC-004 边界无冲突；
- 用户明确接受 RFC-003。

## Open Questions

- P-22 / P-23 / P-24 的用户 Decision Gate；
- Workflow Definition / State Schema / Serializer / Checkpointer 版本兼容与升级；
- Safe Resume Command、Recovery Action Matrix 与 Runtime Registry 最终字段；
- Checkpoint retention、cleanup、backup / restore 与 operator recovery；
- 最终测试命令、TS-03 场景、迁移演练、性能基线和停止条件。

## User Acceptance Gate

RFC-003 只有在以下条件全部满足后才可进入最终用户接受：

1. DQ-01～DQ-09 均有明确 Chosen Option、Rejected Alternatives 与 Trade-offs；
2. 兼容、迁移、Rollback、测试与停止条件完整；
3. 与 Accepted DEC、RFC-001 / 002、Current Specs 和后续 RFC 边界一致；
4. 独立五轴 Review 与文档链接校验通过；
5. 用户明确回复接受 RFC-003。

PR Merge、Required Checks 通过、DEC-049 Accepted 或单个 DQ Accepted，均不能替代 RFC-003 整体接受，也不授权实现、Spike 或 Goal。
