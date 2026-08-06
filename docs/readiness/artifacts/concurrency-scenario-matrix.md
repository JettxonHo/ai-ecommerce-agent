# ARP-02 — Concurrency Scenario Matrix（TS-01 Minimum Slice）

## 0. Artifact Status

```text
Status =
ACCEPTED — USER DECISION 2026-08-06

Wave =
WAVE 1

Scope =
TS-01 MINIMUM SLICE ONLY

TS-01 Minimum Slice =
ACCEPTED FOR TS-01 PLANNING BASELINE

Full ARP-02 Completion =
NOT CLAIMED

Artifact Acceptance =
ACCEPTED — USER DECISION 2026-08-06

Artifact Creation Authorization =
AUTHORIZED

Technical Spike Planning / Execution =
NOT AUTHORIZED

Implementation =
NOT AUTHORIZED
```

> 本文件由 Wave 1 Readiness Artifact Creation Authorization（Level 2）创建。用户于 2026-08-06 明确接受本 TS-01 Minimum Slice；本 Slice 仅覆盖 TS-01（PostgreSQL Multi-worker Concurrency Technical Spike）所需场景，**不声称完成完整 ARP-02**。`Artifact Acceptance ≠ Spike Authorization`。
> 全部场景 Evidence Status 统一为 `NOT YET EVIDENCED` / `REQUIRES TS-01`；本 Slice 不含任何真实测试结果。

---

## 1. Artifact Identity

| 项 | 值 |
|---|---|
| Artifact ID | ARP-02 |
| Exact Name | Concurrency Scenario Matrix |
| Purpose | 枚举 TS-01 必需的并发场景，标识其并发范围、受保护业务不变量、并发控制机制组合、重试分类与用户可见冲突结果，作为持久化/并发控制实现前置条件。 |
| Scope | TS-01 MINIMUM SLICE ONLY |
| Source / Traceability | RFC-002-DQ-07 §54-56（Concurrency Scenario Matrix = REQUIRED / NOT AUTHORIZED，字段清单）；DQ-09 §94（Dispatch 场景补充）；DQ-11 §154（版本分配/CAS/失效/恢复场景） |
| Decision Status | ACCEPTED — TS-01 MINIMUM SLICE ONLY（2026-08-06） |

---

## 2. Owning DQ / DEC / RFC

| 项 | 值 | Source / Traceability |
|---|---|---|
| Primary Owning DQ | RFC-002-DQ-07（Concurrency Control，Accepted Direction = Layered Concurrency Control） | rfc-002-decision-questions.md §DQ-07 |
| Contributing DQ | DQ-08（Idempotency）· DQ-09（Durable Dispatch）· DQ-10（Integration Event 重复投递）· DQ-11（Versioning）· DQ-16（Test）· DQ-17（Security） | rfc-002-decision-questions.md |
| Related DEC | DEC-029（Human Review 并发）· DEC-033（Runtime Retry）· DEC-035（Atomic Commit） | docs/decisions/ |
| Downstream RFC Boundary | RFC-003（Work Retry/Backoff/Dead-letter）· RFC-004（API 冲突状态码 / ETag / If-Match） | rfc-002-analysis-cross-rfc-boundary.md |

---

## 3. Authoritative Inputs

| 输入 | 角色 | Source / Traceability |
|---|---|---|
| RFC-002-DQ-07 Accepted Decision | 分层并发控制模型 + Matrix 字段 + TS-01 Spike 必备验证项 | rfc-002-decision-questions.md §DQ-07 |
| RFC-002-DQ-09 §94/§97 | Dispatch 并发场景（Claim Race / Lease Expiry / Worker Crash / stale fencing / duplicate Delivery / Cancel-vs-complete / simultaneous retry / ordering conflict） | rfc-002-decision-questions.md §DQ-09 |
| RFC-002-DQ-11 §154 | 版本竞争场景（Version Number Allocation / Pointer CAS / Invalidation / Promotion-vs-Invalidation / Restore-vs-New Write / Concurrent Restore / No Orphan Version） | rfc-002-decision-questions.md §DQ-11 |
| RFC-002-DQ-08 | 幂等并发（同 Key±Fingerprint） | rfc-002-decision-questions.md §DQ-08 |

---

## 4. Ownership & Review Roles

| 角色 | 值 | 说明 |
|---|---|---|
| Primary Owner Role | Concurrency / Persistence Architecture Owner | 具体人选 = PENDING USER DECISION。 |
| Contributors | 各业务模块 Owner · Workflow Runtime Owner | 场景受保护不变量来源。 |
| Reviewers | 用户（Product Decision Owner） | Artifact Acceptance 仅由用户决定。 |

---

## 5. Authorization Boundary

```text
Artifact Creation Authorization =
AUTHORIZED（本文件创建属 Level 2）

Artifact Acceptance =
ACCEPTED — TS-01 MINIMUM SLICE ONLY（2026-08-06）

Technical Spike Planning / Execution =
NOT AUTHORIZED

TS-01 Execution =
NOT AUTHORIZED

Implementation =
NOT AUTHORIZED
```

---

## 6. Column Index（16 正式列映射）

本 Slice 的 16 个正式列按主题分组呈现于第 7 节 Table A–D；各表共享同一 `CONC-xxx` 行 ID 与行序。列映射如下：

| 正式列 | 所在表 |
|---|---|
| Scenario · Concurrency Scope · Protected Business Invariant | Table A |
| Optimistic Revision · Database Unique Constraint · Durable Lease · fencing_token · Pessimistic Lock | Table B |
| Retry Classification · Retry Owner · Maximum Attempts · User-visible Conflict Result | Table C |
| Related DQ / DEC / RFC · Source / Traceability · Decision Status · Evidence Status | Table D |

> Table B 单元格受控取值：`REQUIRED` / `DEFAULT` / `NOT REQUIRED` / `PROHIBITED` / `RESTRICTED（queue-claim only）` / `NOT APPLICABLE`。

---

## 7. Matrix（TS-01 Minimum Slice）

> 行 ID 规则：`CONC-001`…（Artifact Traceability ID，非数据库主键 / 生产 ID）。

### Table A — Scenario Identity & Scope

> Protected Business Invariant 列：每行至少一个精确 `INV-xxx`（ARP-01）。若场景同时涉及 Record / Identity，另列 `Supporting Record / Identity: REC-xxx / IDEM-xxx`。业务对象缩写：Task=INV-001 · Facts=INV-002 · Insights=INV-003 · Positioning=INV-004 · Strategy=INV-005 · ReviewPkg=INV-006 · Brief=INV-007 · ExecBrief=INV-008 · Source=INV-009 · EvLink=INV-010 · Audit=INV-011。

| Row ID | Scenario | Concurrency Scope | Protected Business Invariant（→ ARP-01） |
|---|---|---|---|
| CONC-001 | `expected_revision` compare-and-swap 并发（普通业务写） | 单业务对象 Current Truth 更新 | Protected Invariant: INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008 / INV-009（Facts/Insights/Positioning/Strategy/Brief/ExecutionBrief/Source 的版本化 Current Truth CAS；冲突回滚零部分写入） |
| CONC-002 | Current Truth Pointer Promotion Race | Task 级 Pointer CAS | Protected Invariant: INV-001（Task 级 Current Truth Pointer CAS；仅一个正式版本被提升为 Current Truth） |
| CONC-003 | Named Unique Constraint Race（重复业务事实） | 命名唯一约束范围 | Protected Invariant: INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（各版本化业务对象的重复业务事实最终防线） |
| CONC-004 | Concurrent Work Intent Claim | Durable Work Intent 队列式 Claim | Protected Invariant: INV-001（task 级业务操作单次执行所有权）；Supporting Record / Identity: REC-009（ARP-04 Durable Work Intent）/ IDEM-008（ARP-03） |
| CONC-005 | `SKIP LOCKED` No-double-claim | 短事务队列式 Claim | Protected Invariant: INV-001（不双重领取同一工作项，保障业务操作单次执行）；Supporting Record / Identity: REC-009（ARP-04） |
| CONC-006 | Lease Expiry and Takeover | 执行所有权（Lease + fencing） | Protected Invariant: INV-001（接管产生更高 fencing_token，保障业务操作执行所有权唯一）；Supporting Record / Identity: REC-009（ARP-04） |
| CONC-007 | Stale `fencing_token` Commit Rejection | 最终提交重验 | Protected Invariant: INV-001（旧 Worker 不得完成业务提交）；Supporting Record / Identity: REC-009（ARP-04） |
| CONC-008 | SQLSTATE `40001` serialization_failure | 数据库事务失败分类 | Protected Invariant: INV-001（Task 事务）+ INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008 / INV-009 / INV-010 / INV-011（各业务 Atomic Commit 事务重试身份保持） |
| CONC-009 | SQLSTATE `40P01` deadlock_detected | 数据库事务失败分类 | Protected Invariant: INV-001（Task 事务）+ INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008 / INV-009 / INV-010 / INV-011（各业务 Atomic Commit 事务重试身份保持） |
| CONC-010 | Transaction Retry Identity Preservation | 重试复用 Command ID 等身份 | Protected Invariant: INV-001（Task 事务）+ INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（Retry 不创建新 Domain Version）；Supporting Record / Identity: IDEM-005（ARP-03 Transient Failure Retry） |
| CONC-011 | Same Idempotency Key + Same Fingerprint | 幂等重放 | Protected Invariant: INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（重放原 Application Result，业务对象不重复副作用）；Supporting Record / Identity: IDEM-002（ARP-03 Exact Replay） |
| CONC-012 | Same Idempotency Key + Different Fingerprint | 幂等冲突 | Protected Invariant: INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（返回 Idempotency Key Conflict，不覆盖不执行）；Supporting Record / Identity: IDEM-004（ARP-03 Same Key/Diff Fingerprint） |
| CONC-013 | Duplicate Delivery / Consumer Dedup | Integration Event Consumer | Protected Invariant: INV-001（消费产生的业务状态更新目标，重复投递仅一次业务效果）；Supporting Record / Identity: REC-013（ARP-04 Integration Event / Outbox Row）/ IDEM-011（ARP-03 Consumer Dedup）/ IDEM-012（ARP-03 Integration Event Identity） |
| CONC-014 | Worker Crash after Claim | Work Intent 领取后崩溃 | Protected Invariant: INV-001（崩溃后可重新领取，业务操作不丢失不重复）；Supporting Record / Identity: REC-009（ARP-04） |
| CONC-015 | Commit Outcome Unknown | 提交结果未知重试 | Protected Invariant: INV-001（Task 事务）+ INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（重试不重复外部 Provider 调用）；Supporting Record / Identity: IDEM-006（ARP-03）/ REC-010（ARP-04 Provider Call Ledger） |
| CONC-016 | Atomic Business Commit Fault Windows | DEC-035 原子提交故障窗口 | Protected Invariant: INV-001（Task）+ INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008 + INV-010（Evidence Link 同生共死）+ INV-011（Audit 同事务）：全有或全无，无部分写入 |
| CONC-017 | No Partial Business Commit | 冲突回滚 | Protected Invariant: INV-001（Task）+ INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（零部分 Current Truth 写入） |
| CONC-018 | No Orphan Domain Version | 并发版本分配 | Protected Invariant: INV-010（Evidence Link 与 Domain Version 同生共死）+ INV-002（Facts Version 代表性版本化对象） |
| CONC-019 | No Duplicate Work Intent | Intent 唯一性 | Protected Invariant: INV-001（同一业务操作不重复创建 Intent）；Supporting Record / Identity: REC-009（ARP-04）/ IDEM-008（ARP-03） |
| CONC-020 | Restore-versus-new-write（限 RFC-002 已由 TS-01 验证的语义） | Business Restore 与新写并发 | Protected Invariant: INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（Restore 为新前向 Command，不覆盖较新写） |
| CONC-021 | Concurrent Version Number Allocation | 并发 version_number 分配 | Protected Invariant: INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008 / INV-009（不产生重复 Domain Version） |
| CONC-022 | Current Version Invalidation Race | Invalidation 与读/写并发 | Protected Invariant: INV-002 / INV-003 / INV-004 / INV-007 / INV-009（Invalidation 不删版本、不静默回退） |
| CONC-023 | Promotion-versus-Invalidation | 提升与失效并发 | Protected Invariant: INV-001（Pointer）+ INV-002 / INV-003 / INV-004 / INV-007（显式语义，不产生冲突 Current Truth） |
| CONC-024 | Cancel-versus-complete（Dispatch） | 取消与完成并发 | Protected Invariant: INV-001（协作式取消不产生部分写）；Supporting Record / Identity: REC-009（ARP-04 Durable Work Intent） |
| CONC-025 | Simultaneous Work Retry（同一 Work Intent 并发重试） | Work Intent 重试并发 | Protected Invariant: INV-001（同一业务工作不因并发重试产生重复业务效果）；Supporting Record / Identity: REC-009（ARP-04 Durable Work Intent）/ IDEM-008（ARP-03） |
| CONC-026 | Ordering Conflict（工作/投递顺序冲突） | Dispatch 顺序语义 | Protected Invariant: INV-001（仅验证 RFC-002 已接受的顺序语义边界，不选择最终调度算法）；Supporting Record / Identity: REC-009（ARP-04 Durable Work Intent） |
| CONC-027 | Authoritative Polling Recovery after Lost Wake-up | Wake-up（非权威）与 PostgreSQL Polling（权威） | Protected Invariant: INV-001（wake-up 可能丢失；PostgreSQL polling 保持权威；已提交 available Intent 最终被重新发现；wake-up 不授予所有权，数据库 Claim 授予所有权）；Supporting Record / Identity: REC-009（ARP-04 Durable Work Intent） |
| CONC-028 | Integration Event Relay Crash Recovery | Relay 崩溃与恢复 | Protected Invariant: INV-001（已提交业务事实不因 Relay Crash 丢失；Event 最终可恢复投递；Retry 保持同一 Event Identity，新 publish attempt 使用新 Attempt Identity）；Supporting Record / Identity: REC-013（ARP-04 Integration Event / Outbox）/ IDEM-015（ARP-03 Publish Attempt） |
| CONC-029 | Stale Integration Event Publish Attempt Rejection | 过期 Publish Attempt 与当前发布状态 | Protected Invariant: INV-001（stale publish attempt 不改变已完成或更新后的发布状态；Event Identity 不变、Attempt Identity 不同；无重复业务事实）；Supporting Record / Identity: REC-013（ARP-04 Integration Event / Outbox）/ IDEM-015 / IDEM-012（ARP-03） |

### Table B — Control Mechanisms

| Row ID | Optimistic Revision | Database Unique Constraint | Durable Lease | fencing_token | Pessimistic Lock |
|---|---|---|---|---|---|
| CONC-001 | DEFAULT（expected_revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-002 | DEFAULT（Pointer 独立 revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-003 | NOT REQUIRED | REQUIRED（命名唯一约束） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-004 | NOT REQUIRED | NOT REQUIRED FOR CLAIM EXCLUSIVITY（Claim Exclusivity = SKIP LOCKED 短事务 + Durable Lease + fencing_token；Intent 重复创建防线由 CONC-019 承载） | REQUIRED | REQUIRED | RESTRICTED（SKIP LOCKED 短事务） |
| CONC-005 | NOT REQUIRED | NOT REQUIRED | REQUIRED | REQUIRED | RESTRICTED（SKIP LOCKED，仅 queue claim） |
| CONC-006 | NOT REQUIRED | NOT REQUIRED | REQUIRED | REQUIRED（单调递增） | NOT REQUIRED |
| CONC-007 | REQUIRED（最终提交重验 expected_revision） | NOT REQUIRED | REQUIRED（重验 Lease Holder） | REQUIRED（重验 fencing_token） | NOT REQUIRED |
| CONC-008 | DEFAULT（重试后重验） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-009 | DEFAULT（重试后重验） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-010 | DEFAULT | 按 DQ-08 | 按 DQ-08/DQ-09 | 按 DQ-09 | NOT REQUIRED |
| CONC-011 | DEFAULT | REQUIRED（Scope+Key+Fingerprint） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-012 | DEFAULT | REQUIRED（Scope+Key） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-013 | DEFAULT | REQUIRED（Consumer Dedup Marker） | 按 Consumer | 按 Consumer | NOT REQUIRED |
| CONC-014 | NOT REQUIRED | NOT REQUIRED FOR CLAIM EXCLUSIVITY（Crash 接管经 Lease 过期 + 重新领取，非唯一约束机制） | REQUIRED | REQUIRED | RESTRICTED（SKIP LOCKED） |
| CONC-015 | DEFAULT | 按 DQ-08 | 按 DQ-09 | 按 DQ-09 | NOT REQUIRED |
| CONC-016 | DEFAULT | 按参与者 | 按参与者 | 按参与者 | NOT REQUIRED |
| CONC-017 | DEFAULT | 按参与者 | 按参与者 | 按参与者 | NOT REQUIRED |
| CONC-018 | DEFAULT | REQUIRED（版本唯一性） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-019 | NOT REQUIRED | REQUIRED（Intent 唯一性） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-020 | DEFAULT（Restore 新前向 Command） | 按 DQ-11 | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-021 | DEFAULT | REQUIRED（version_number 唯一性） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-022 | DEFAULT（revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-023 | DEFAULT（revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-024 | DEFAULT | 按 DQ-09 | REQUIRED | REQUIRED | NOT REQUIRED |
| CONC-025 | DEFAULT | 按 DQ-08（幂等记录） | REQUIRED | REQUIRED | NOT REQUIRED |
| CONC-026 | DEFAULT | 按 DQ-09 | REQUIRED | REQUIRED | NOT REQUIRED |
| CONC-027 | DEFAULT | NOT REQUIRED | REQUIRED（数据库 Claim 授予所有权） | REQUIRED | RESTRICTED（SKIP LOCKED Claim） |
| CONC-028 | DEFAULT | NOT REQUIRED（Outbox 记录已持久化） | 按 Relay（RFC-003） | 按 Relay（RFC-003） | NOT REQUIRED |
| CONC-029 | REQUIRED（发布状态 CAS / 版本重验） | NOT REQUIRED | 按 Relay（RFC-003） | 按 Relay（RFC-003） | NOT REQUIRED |

> 悲观锁说明：`SELECT FOR UPDATE / NOWAIT / 悲观行锁` 不是全局默认（DQ-07 §30）；`SKIP LOCKED` 仅限显式队列式 Claim 的短事务（DQ-07 §28-29）；Session-level Advisory Lock = PROHIBITED（DQ-07 §33）。

### Table C — Retry & Outcome

| Row ID | Retry Classification | Retry Owner | Maximum Attempts | User-visible Conflict Result |
|---|---|---|---|---|
| CONC-001 | 语义冲突（stale revision）不盲目重试 | 调用方 / Application 明确策略 | NOT APPLICABLE（不自动重试） | stale revision 拒绝；冲突语义呈现（HTTP 协议留 RFC-004） |
| CONC-002 | 语义冲突不盲目重试 | Application | NOT APPLICABLE | Pointer 未被非法提升 |
| CONC-003 | unique_violation 未分类不盲目重试 | Application（按 DQ-08 转幂等响应） | NOT APPLICABLE | 重复业务事实被拒或幂等响应 |
| CONC-004 | Claim 失败不重试同一领取 | Worker | NOT APPLICABLE | 未被领取者可再次 Claim |
| CONC-005 | 未领取到项不视为错误 | Worker | NOT APPLICABLE | 无双重领取 |
| CONC-006 | Lease 过期由接管处理 | Worker/Runtime（RFC-003 前为 DQ-09 语义） | NOT APPLICABLE | 旧 Holder 失去执行所有权 |
| CONC-007 | stale fencing 拒绝，不重试 | Application Transaction Runner | NOT APPLICABLE | 旧 Worker 提交被拒 |
| CONC-008 | 可能瞬时（transient） | Application Transaction Runner / Command Executor | 3 次总事务尝试（1 初始 + 2 重试；DQ-07 §40） | 重试后成功或终局失败 |
| CONC-009 | 可能瞬时（transient） | Application Transaction Runner / Command Executor | 3 次总事务尝试（DQ-07 §40） | 重试后成功或终局失败 |
| CONC-010 | Retry 复用 Command ID/Idempotency Key/Stage Run ID/Fingerprint，新 Attempt ID | Application Transaction Runner | 按 DQ-07/DQ-08 | 无新 Domain Version |
| CONC-011 | 幂等重放（非重试错误） | 幂等层 Owning Module | NOT APPLICABLE | 重放原 Application Result |
| CONC-012 | 幂等冲突（不覆盖不执行不盲目重试） | 幂等层 Owning Module | NOT APPLICABLE | Idempotency Key Conflict |
| CONC-013 | Consumer Dedup（同事务 Dedup Marker） | Consumer 模块 | NOT APPLICABLE | 一次业务效果 |
| CONC-014 | Crash 后重新领取（新 Attempt） | Worker/Runtime | 按 DQ-09/RFC-003 | 工作不丢失不重复 |
| CONC-015 | Commit 重试复用已产生不可变外部结果，不重调 Provider | Application Transaction Runner | 按 DQ-07 §47-48 | 不重复外部副作用 |
| CONC-016 | Fault Injection 验证全有或全无 | Test（TS-01） | NOT APPLICABLE | 无部分写入 |
| CONC-017 | 冲突回滚 | Application | NOT APPLICABLE | 零部分 Current Truth 写入 |
| CONC-018 | 版本与 Evidence Link 同事务 | Application | NOT APPLICABLE | 无孤儿版本 |
| CONC-019 | Intent 唯一约束 | Dispatch Capability | NOT APPLICABLE | 不重复 Intent |
| CONC-020 | Restore 为新前向 Command | Application | NOT APPLICABLE | 不覆盖较新写 |
| CONC-021 | 并发版本分配不重复 | Application | NOT APPLICABLE | 无重复 Domain Version |
| CONC-022 | Invalidation 显式 | Application | NOT APPLICABLE | 不静默回退 |
| CONC-023 | 显式语义 | Application | NOT APPLICABLE | 无冲突 Current Truth |
| CONC-024 | Cancel 协作式传播 | Runtime（RFC-003） | NOT APPLICABLE | 无部分写 |
| CONC-025 | 并发重试受 Lease + fencing + 幂等约束，不产生重复业务效果 | Worker/Runtime（RFC-003 前为 DQ-09 语义） | 按 DQ-09/RFC-003 | 一次业务效果 |
| CONC-026 | 顺序冲突按 DQ-09 语义处理（不选择最终调度算法） | Runtime（RFC-003） | 按 DQ-09/RFC-003 | 顺序语义边界保持 |
| CONC-027 | wake-up 丢失不视为错误；权威 PostgreSQL Polling 重新发现 available Intent | Worker/Runtime（Polling Interval / Backend 留 RFC-003） | 权威 Polling 周期性（具体间隔留 RFC-003） | 已提交 Intent 最终被领取；wake-up 不授予所有权，数据库 Claim 授予所有权 |
| CONC-028 | Relay Crash 后重新投递；Event Identity 稳定，Publish Attempt Identity 每次新建 | Relay（RFC-003） | 按 RFC-003（AT-LEAST-ONCE，不承诺 exactly-once） | Event 不丢失 |
| CONC-029 | stale Attempt 拒绝，不覆盖当前发布状态；Event Identity 不变、Attempt Identity 不同 | Relay（RFC-003） | NOT APPLICABLE（stale 拒绝不盲目重试） | 无重复业务事实 |

### Table D — Traceability

| Row ID | Related DQ / DEC / RFC | Source / Traceability | Decision Status | Evidence Status |
|---|---|---|---|---|
| CONC-001 | DQ-07 · DQ-04 · DEC-024 | rfc-002-decision-questions.md §DQ-07 §49 | Scenario = ACCEPTED DECISION（DQ-07） | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-002 | DQ-11 · DQ-07 · DEC-024 | rfc-002-decision-questions.md §DQ-11 §154 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-003 | DQ-07 · DQ-08 | rfc-002-decision-questions.md §DQ-07 §49 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-004 | DQ-09 · DQ-07 | rfc-002-decision-questions.md §DQ-09 §94/97 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-005 | DQ-09 · DQ-07 §28-29 | rfc-002-decision-questions.md §DQ-07/09 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-006 | DQ-07 · DQ-09 | rfc-002-decision-questions.md §DQ-07 §59 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-007 | DQ-07 · DQ-09 | rfc-002-decision-questions.md §DQ-07 §59 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-008 | DQ-07 §36-40 | rfc-002-decision-questions.md §DQ-07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-009 | DQ-07 §36-40 | rfc-002-decision-questions.md §DQ-07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-010 | DQ-07 §39 · DQ-08 | rfc-002-decision-questions.md §DQ-07/08 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-011 | DQ-08 | rfc-002-decision-questions.md §DQ-08 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-012 | DQ-08 | rfc-002-decision-questions.md §DQ-08 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-013 | DQ-09 · DQ-10 · DQ-08 | rfc-002-decision-questions.md §DQ-09 §94 · §DQ-10 §121 | Scenario = ACCEPTED DECISION（DQ-09 duplicate Delivery + DQ-10 Integration Event Duplicate Delivery / Consumer Dedup） | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-014 | DQ-09 · DQ-07 | rfc-002-decision-questions.md §DQ-09 §97 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-015 | DQ-07 §47-48 · DQ-16 | rfc-002-decision-questions.md §DQ-07/16 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-016 | DQ-16 · DEC-035 | rfc-002-decision-questions.md §DQ-16 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-017 | DQ-07 §59 · DEC-035 | rfc-002-decision-questions.md §DQ-07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-018 | DQ-11 · DQ-07 §59 | rfc-002-decision-questions.md §DQ-11/07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-019 | DQ-09 | rfc-002-decision-questions.md §DQ-09 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-020 | DQ-11 §154 | rfc-002-decision-questions.md §DQ-11 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-021 | DQ-11 §154 · DQ-07 §59 | rfc-002-decision-questions.md §DQ-11/07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-022 | DQ-11 §154 | rfc-002-decision-questions.md §DQ-11 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-023 | DQ-11 §154 | rfc-002-decision-questions.md §DQ-11 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-024 | DQ-09 §94 · DEC-033 | rfc-002-decision-questions.md §DQ-09 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-025 | DQ-09 §3.16 item 94 · DQ-08 | rfc-002-decision-questions.md §DQ-09 §94 | Scenario = ACCEPTED DECISION（DQ-09） | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-026 | DQ-09 §3.16 item 94 | rfc-002-decision-questions.md §DQ-09 §94 | Scenario = ACCEPTED DECISION（DQ-09） | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-027 | DQ-09 §3.16 item 97 | rfc-002-decision-questions.md §DQ-09 §97 | Scenario = ACCEPTED DECISION（DQ-09） | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-028 | DQ-10 §121 · DQ-08 | rfc-002-decision-questions.md §DQ-10 §121 | Scenario = ACCEPTED DECISION（DQ-10） | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-029 | DQ-10 §121 | rfc-002-decision-questions.md §DQ-10 §121 | Scenario = ACCEPTED DECISION（DQ-10） | NOT YET EVIDENCED / REQUIRES TS-01 |

---

## 8. Cross-artifact References

| 本 Artifact 元素 | 引用目标 | 关系 |
|---|---|---|
| CONC-001~CONC-029 Protected Business Invariant | ARP-01 INV-xxx | 每行至少一个精确 INV 引用（见 Table A；业务对象缩写表见 Table A 前言）。 |
| CONC-004 / CONC-005 / CONC-006 / CONC-007 / CONC-014 / CONC-019 / CONC-024 / CONC-025 / CONC-026 / CONC-027 | ARP-04 REC-009（Durable Work Intent） | Work Intent Supporting Record（受保护不变量仍指向 INV-001）。 |
| CONC-013 | ARP-04 REC-013（Integration Event / Outbox Row）+ ARP-03 IDEM-011（Consumer Dedup）/ IDEM-012（Integration Event Identity） | Duplicate Delivery / Consumer Dedup 的正确引用目标（不再指向 Durable Work Intent / Provider Call Ledger 记录类）。 |
| CONC-028 / CONC-029 | ARP-04 REC-013（Integration Event / Outbox Row）+ ARP-03 IDEM-015（Integration Event Publish / Delivery Attempt；CONC-029 另含 IDEM-012） | Relay Crash Recovery / Stale Publish Attempt 的 Outbox 记录与 Publish Attempt 身份。 |
| CONC-015 | ARP-04 REC-010（Provider Call Ledger）+ ARP-03 IDEM-006 | Commit Outcome Unknown 的 Provider Supporting Record。 |
| CONC-010 / CONC-011 / CONC-012 | ARP-03 IDEM-005 / IDEM-002 / IDEM-004 | 幂等身份边界 Supporting Identity。 |
| CONC-008 / CONC-009 / CONC-016 / CONC-017 / CONC-013 / CONC-025 / CONC-026 / CONC-027 / CONC-028 / CONC-029 | ARP-09 TEST-xxx | 对应测试覆盖行（含新增 Consumer Dedup / Relay Crash / stale Publish / Polling Recovery / Simultaneous Retry / Ordering Conflict）。 |

---

## 9. Review Checklist（Artifact-specific）

- [x] 覆盖并从 RFC-002 重新提取全部 TS-01 必需场景（expected_revision CAS / Pointer Promotion / Named Unique Constraint / Work Intent Claim / SKIP LOCKED / Lease Expiry-Takeover / Stale fencing_token / 40001 / 40P01 / Retry Identity / Idempotency Key±Fingerprint / Duplicate Delivery / Worker Crash / Commit Outcome Unknown / Atomic Commit Fault Windows / No Partial Write / No Orphan Version / No Duplicate Work Intent / Restore-vs-new-write / Version Number Allocation / Invalidation / Promotion-vs-Invalidation / Cancel-vs-complete / Simultaneous Work Retry / Ordering Conflict / Authoritative Polling Recovery / Integration Event Relay Crash Recovery / Stale Integration Event Publish Attempt Rejection）。
- [x] Claim Exclusivity 归因正确（SKIP LOCKED 短事务 + Durable Lease + fencing_token；唯一约束不用于 Claim 互斥，Intent 重复创建防线由 CONC-019 承载）。
- [x] 每行有 Source / Traceability。
- [x] 全部行 Evidence Status = `NOT YET EVIDENCED` / `REQUIRES TS-01`；未出现 PASS / SUPPORTED / VERIFIED。
- [x] 未填写真实测试结果。
- [x] Maximum Attempts 对 40001/40P01 = 3 次总事务尝试（DQ-07），语义冲突不盲目重试。
- [x] Pessimistic Lock 未作为全局默认；Session-level Advisory Lock = PROHIBITED。
- [x] 16 正式列全部出现于 Table A–D（见第 6 节 Column Index）。
- [x] 明确 `Full ARP-02 Completion = NOT CLAIMED`。

---

## 10. Open Questions

| # | 问题 | 决定所有者 | 下一 Gate |
|---|---|---|---|
| OQ-1 | API 冲突状态码 / ETag / If-Match 协议 | 用户 | DEFERRED TO RFC-004 |
| OQ-2 | Work Retry / Backoff / Dead-letter / 人工恢复参数 | 用户 | DEFERRED TO RFC-003 |
| OQ-3 | 完整 ARP-02（非 TS-01 场景）补齐范围 | 用户 | 后续 Wave / Full ARP-02 Gate |

---

## 11. Explicit Non-decisions

- 本 Slice 不填写任何真实测试结果（全部 NOT YET EVIDENCED / REQUIRES TS-01）。
- 本 Slice 不声称完成完整 ARP-02（Full ARP-02 Completion = NOT CLAIMED）。
- 本 Slice 不定义具体 HTTP Status Code / Header（留 RFC-004）。
- 本 Slice 不设置 Retry backoff / jitter 数值（留 RFC-007）。
- 本 Slice 不自我接受；用户已于 2026-08-06 作出外部接受决定，范围仅为 TS-01 Minimum Slice。
- 本 Slice 不授权 TS-01 Planning / Execution 或任何实现。
