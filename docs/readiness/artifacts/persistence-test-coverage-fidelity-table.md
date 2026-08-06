# ARP-09 — Persistence Test Coverage & Fidelity Table（TS-01 Minimum Slice）

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

Full ARP-09 Completion =
NOT CLAIMED

Artifact Acceptance =
ACCEPTED — USER DECISION 2026-08-06

Artifact Creation Authorization =
AUTHORIZED

Technical Spike Planning / Execution =
NOT AUTHORIZED

Common Persistence Test Harness =
NOT CREATED

Implementation =
NOT AUTHORIZED
```

> 本文件由 Wave 1 Readiness Artifact Creation Authorization（Level 2）创建。用户于 2026-08-06 明确接受本 TS-01 Minimum Slice；本 Slice 仅覆盖 TS-01 所需的最小测试覆盖与保真度声明，**不声称完成完整 ARP-09**。`Artifact Acceptance ≠ Spike Authorization`。
> 本 Slice **不创建测试代码、Fixture、Container 或 CI Workflow**；未知实测值一律写 `REQUIRES TS-01 EVIDENCE`；`Evidence Produced` 统一为 `NOT YET AVAILABLE`。
> 现有 SQLite Spike-001 证据**不得**当作 PostgreSQL Acceptance Evidence（DQ-16：SQLite 仅可选非权威 Test Double）。

---

## 1. Artifact Identity

| 项 | 值 |
|---|---|
| Artifact ID | ARP-09 |
| Exact Name | Persistence Test Coverage & Fidelity Table |
| Purpose | 为 TS-01 声明每项持久化/并发/幂等不变量所需的测试层、保真度要求（真实 PostgreSQL、连接/进程数、隔离级别、Commit Visibility、Fault Injection）与 CI 层级，作为实现前置测试覆盖规划。 |
| Scope | TS-01 MINIMUM SLICE ONLY |
| Source / Traceability | RFC-002-DQ-16 §3.17（Persistence Test Coverage & Fidelity Table = REQUIRED / NOT AUTHORIZED，18 项字段）· §3.18（Common Harness Qualification） |
| Decision Status | ACCEPTED — TS-01 MINIMUM SLICE ONLY（2026-08-06） |

---

## 2. Owning DQ / DEC / RFC

| 项 | 值 | Source / Traceability |
|---|---|---|
| Primary Owning DQ | RFC-002-DQ-16（Persistence Testing Strategy，Accepted Principle = Layered Test Strategy） | rfc-002-decision-questions.md §DQ-16 |
| Contributing DQ | DQ-07（Concurrency）· DQ-08（Idempotency）· DQ-09（Dispatch）· DQ-11（Versioning）· DQ-17（Synthetic Fixture / Redaction） | rfc-002-decision-questions.md |
| Related DEC | DEC-035（Atomic Commit）· DEC-022（并发需真实验证） | docs/decisions/ |
| Related Qualification | QL-01（Common Persistence Test Harness Qualification）· QL-02 TS-01 Slice（见 ARP-10） | docs/readiness/artifacts/sensitive-data-secret-cryptographic-control-matrix.md §9 |

---

## 3. Authoritative Inputs

| 输入 | 角色 | Source / Traceability |
|---|---|---|
| RFC-002-DQ-16 Accepted Decision | 分层测试策略 + 18 列 + Harness 原则 + CI 层级 + 禁止 Retry-to-green | rfc-002-decision-questions.md §DQ-16 |
| RFC-002-DQ-07 §58-59 | TS-01 Spike 必须使用真实 PostgreSQL / 多连接 / ≥2 Workers / 确定性故障注入 | rfc-002-decision-questions.md §DQ-07 |
| RFC-002-DQ-17 | 合成测试数据、受控 Secret Injection、失败日志 Redaction | rfc-002-decision-questions.md §DQ-17 |

---

## 4. Ownership & Review Roles

| 角色 | 值 | 说明 |
|---|---|---|
| Primary Owner Role | Persistence Test Architecture Owner | 具体人选 = PENDING USER DECISION。 |
| Contributors | TS-01 Spike Owner（未授权）· QL-01 Harness Owner | Harness Qualification 与 Spike 执行者。 |
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

Common Persistence Test Harness =
NOT CREATED

Implementation =
NOT AUTHORIZED
```

---

## 6. Test Layer Controlled Vocabulary（受控词汇）

```text
Pure Unit
Application Test Double
Port Contract
Real PostgreSQL Acceptance
Multi-connection Concurrency
Migration
Crash / Fault Injection
Production-topology Qualification
```

> 本 TS-01 Slice 仅使用 `Real PostgreSQL Acceptance` / `Multi-connection Concurrency` / `Crash / Fault Injection`（及 QL-01 Harness Qualification 行）。`Pure Unit` / `Application Test Double` / `Port Contract` 不证明 PostgreSQL 语义（DQ-16）。

### 6.1 Proportional Validation Guardrail（用户工程治理约束）

> 来源：用户当前明确指令（2026-08-06，优先级高于既有文档）；正式 DEC / AGENTS 同步在 PR #28 之后的独立文档任务归档，本节不替代该归档。

- 本表是覆盖目录，不要求为每一行、每一层重复创建独立测试；一个确定性场景可以覆盖多个 Row，但须保留清晰的 Evidence Mapping。
- `Required` 表示 TS-01 必须形成可信证据，不自动等于每项都成为永久 Required PR Check。CI 层级应按真实发生概率、业务影响、执行成本与回归价值决定；高成本、低概率场景可放入 Spike / Scheduled / Manual Tier。
- 已有代表性测试能够覆盖同一失效机制时，不再为基本不可能出现的细小变体反复增加防御性 Case。
- 普通校验不新增密码学算法或摘要要求；只有明确影响核心功能的重大安全或完整性风险，且普通业务约束无法解决时，才单独提出并说明理由、范围与成本。
- Rubric 用于帮助 Reviewer 判断，不作为机械打分或自动接受规则；最终结论保留基于上下文的专业判断。

---

## 7. Column Index（18 正式列 + Source/Traceability + Decision Status + Evidence Status 映射）

本 Slice 的 18 个正式列 + `Source / Traceability` + `Decision Status` + `Evidence Status` 按主题分组呈现于第 8 节 Table A–D；各表共享同一 `TEST-xxx` 行 ID 与行序。列映射如下：

| 正式列 | 所在表 |
|---|---|
| Requirement / Invariant · Owning DQ / DEC / RFC · Test Layer · Test Subject · Real PostgreSQL Required | Table A |
| Connection Count · Process / Worker Count · Isolation Level · Fixture Strategy · Commit Visibility Required · Expected SQLSTATE | Table B |
| Fault Injection · External Dependency · Cleanup Strategy · CI Tier · Required / Optional | Table C |
| Evidence Produced · Owner · Source / Traceability · Decision Status · Evidence Status | Table D |

---

## 8. Matrix（TS-01 Minimum Slice）

> 行 ID 规则：`TEST-001`…（Artifact Traceability ID，非数据库主键 / 生产 ID）。
> 未知实测值 = `REQUIRES TS-01 EVIDENCE`；`Evidence Produced` 统一 = `NOT YET AVAILABLE`。
>
> **并发 Actor 纪律（Review Remediation）**：需要并发冲突的场景（Concurrent Exact Replay / 40001 / 40P01 / Worker Claim / Lease-Fencing / Commit Outcome Unknown 并发路径）必须至少两个独立 Actor；涉及数据库并发时必须使用独立 Connection / Session / Transaction，不使用模糊 `≥1（并发 ≥2）`。
>
> **DQ-10 Integration Event TS-01 覆盖（Review Remediation）**：DQ-10 已明确将 Integration Event Duplicate Delivery / Consumer Dedup / Relay Crash / stale Event Publish Attempt 验证分配给 DQ-07 的真实 PostgreSQL Multi-worker Spike；本 Slice 新增 TEST-016（Consumer Dedup）/ TEST-017（Relay Crash Recovery）/ TEST-018（stale Event Publish Attempt）/ TEST-019（Polling Recovery）/ TEST-020（Simultaneous Work Retry）/ TEST-021（Ordering Conflict），与 ARP-02 CONC-013 / CONC-025~029 一一对应。不使用 SQLite 作为 Acceptance Evidence。

### Table A — Requirement, Layer & Subject

| Row ID | Requirement / Invariant（→ ARP-01/02/03/04/10） | Owning DQ / DEC / RFC | Test Layer | Test Subject | Real PostgreSQL Required |
|---|---|---|---|---|---|
| TEST-001 | `expected_revision` CAS 并发（CONC-001） | DQ-07 · DQ-04 | Multi-connection Concurrency | Business Current Truth CAS 写 | YES |
| TEST-002 | Named Unique Constraint 重复业务事实防线（CONC-003） | DQ-07 · DQ-08 | Real PostgreSQL Acceptance | 命名唯一约束 | YES |
| TEST-003 | Lease Expiry / Takeover + fencing_token（CONC-006/007） | DQ-07 · DQ-09 | Multi-connection Concurrency | Durable Lease + fencing | YES |
| TEST-004 | `SKIP LOCKED` 无双重领取（CONC-005） | DQ-07 · DQ-09 | Multi-connection Concurrency | 短事务队列式 Claim | YES |
| TEST-005 | SQLSTATE `40001` serialization 重试（CONC-008） | DQ-07 §36-40 | Multi-connection Concurrency | Application Transaction Runner 重试 | YES |
| TEST-006 | SQLSTATE `40P01` deadlock 重试（CONC-009） | DQ-07 §36-40 | Multi-connection Concurrency | Application Transaction Runner 重试 | YES |
| TEST-007 | Transaction Retry Identity Preservation（CONC-010 / IDEM-005） | DQ-07 · DQ-08 | Real PostgreSQL Acceptance | Retry 复用身份、新 Attempt ID | YES |
| TEST-008 | Idempotency Replay：同 Key + 同 Fingerprint（CONC-011 / IDEM-002） | DQ-08 | Real PostgreSQL Acceptance | 幂等重放 | YES |
| TEST-009 | Idempotency Conflict：同 Key + 不同 Fingerprint（CONC-012 / IDEM-004） | DQ-08 | Real PostgreSQL Acceptance | 幂等冲突 | YES |
| TEST-010 | Durable Work Intent Claim + No Duplicate（CONC-004/019 / IDEM-008） | DQ-09 | Multi-connection Concurrency | Intent 唯一性 + Claim | YES |
| TEST-011 | Worker Crash after Claim / Recovery（CONC-014） | DQ-09 · DQ-07 | Crash / Fault Injection | Crash 后重新领取 | YES |
| TEST-012 | Atomic Business Commit Fault Windows 全有或全无（CONC-016） | DQ-16 · DEC-035 | Crash / Fault Injection | DEC-035 原子提交 | YES |
| TEST-013 | No Partial Business Commit / No Orphan Version（CONC-017/018） | DQ-07 · DQ-11 | Crash / Fault Injection | 冲突回滚零部分写入 | YES |
| TEST-014 | QL-01 Common Persistence Test Harness Qualification | DQ-16 §3.18 | Real PostgreSQL Acceptance（Harness 原则） | 真实 PG / 钉定版本 / 确定性协调 / 环境记录 / 可复核证据 / 非 SQLite 验收 | YES |
| TEST-015 | TS-01 Applicable QL-02 Slice（安全） | DQ-17 · ARP-10 §9.2 | Real PostgreSQL Acceptance（安全 Slice） | Synthetic Data / Non-prod Credentials / Role / Redaction / Secret-not-persisted | YES |
| TEST-016 | Duplicate Integration Event Delivery + Consumer Dedup Marker + Consumer Business Update（CONC-013 / IDEM-011 / IDEM-012） | DQ-10 · DQ-08 | Multi-connection Concurrency | Integration Event Consumer 去重与业务更新同事务 | YES |
| TEST-017 | Integration Event Relay Crash Recovery（CONC-028 / IDEM-015） | DQ-10 · DQ-09 | Crash / Fault Injection | Relay 崩溃后 Event 可恢复投递，Event Identity 稳定 | YES |
| TEST-018 | Stale Integration Event Publish Attempt Rejection（CONC-029 / IDEM-015） | DQ-10 | Real PostgreSQL Acceptance | stale publish attempt 不覆盖当前发布状态 | YES |
| TEST-019 | Authoritative Polling Recovery after Lost Wake-up（CONC-027） | DQ-09 | Real PostgreSQL Acceptance | wake-up 丢失后权威 PostgreSQL Polling 重新发现已提交 Intent | YES |
| TEST-020 | Simultaneous Work Retry（CONC-025 / IDEM-008） | DQ-09 · DQ-08 | Multi-connection Concurrency | 同一 Work Intent 并发重试不产生重复业务效果 | YES |
| TEST-021 | Ordering Conflict（CONC-026） | DQ-09 | Multi-connection Concurrency | 顺序语义边界（仅验证 RFC-002 已接受语义，不选择调度算法） | YES |

### Table B — Fidelity

| Row ID | Connection Count | Process / Worker Count | Isolation Level | Fixture Strategy | Commit Visibility Required | Expected SQLSTATE |
|---|---|---|---|---|---|---|
| TEST-001 | 多独立连接（≥2）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 Workers/进程；精确 = REQUIRES TS-01 EVIDENCE | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据（无真实 PII/凭证） | YES | 无（stale revision 语义冲突） |
| TEST-002 | ≥2；精确 = REQUIRES TS-01 EVIDENCE | ≥2 | 正式默认 | 合成测试数据 | YES | unique_violation（分类 = REQUIRES TS-01 EVIDENCE） |
| TEST-003 | ≥2 独立 Connection/Session/Transaction；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors/Workers | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES | 无（Lease/fencing 语义） |
| TEST-004 | ≥2 独立 Connection/Session/Transaction（并发 Claim）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors/Workers | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES（真实 Commit，非永不提交外层事务） | 无 |
| TEST-005 | ≥2 独立 Connection/Session/Transaction（高争用）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors/Workers | Scenario-specific isolation capable of deterministically producing 40001；Exact isolation choice = TS-01 SPIKE PLANNING DECISION（项目默认 READ COMMITTED 本身不保证产生 40001 场景；本 Artifact 阶段不选择最终生产隔离策略） | 合成测试数据 + 确定性协调 | YES | 40001 |
| TEST-006 | ≥2 独立 Connection/Session/Transaction；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors（intentionally opposing lock acquisition order） | 正式默认 Isolation Level（deadlock 触发与隔离级别无强绑定）；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 + Deterministic actor coordination + intentionally opposing lock acquisition order（test-only fault construction；生产代码应在适用处使用一致全局锁顺序） | YES | 40P01 |
| TEST-007 | ≥1；重试经新 UoW/Session | ≥1 | 正式默认 | 合成测试数据 | YES | 40001/40P01（触发重试路径） |
| TEST-008 | ≥2 独立 Connection/Session/Transaction（并发重放）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors/Workers | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES | 无（重放语义） |
| TEST-009 | ≥1 | ≥1 | 正式默认 | 合成测试数据 | YES | 无（Idempotency Key Conflict 语义） |
| TEST-010 | ≥2 独立 Connection/Session/Transaction（并发 Claim）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors/Workers | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES | 无 |
| TEST-011 | 多独立连接 | ≥2 Workers（模拟 Crash） | 正式默认 | 合成测试数据 + 确定性故障注入 | YES | 无（Crash 恢复） |
| TEST-012 | ≥2 独立 Connection/Session/Transaction（含 Commit Outcome Unknown 并发路径）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors（Fault Injection + 并发验证） | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 + Fault Injection | YES（Commit Outcome Unknown 不只 Mock commit 抛异常） | 无（全有或全无） |
| TEST-013 | 多独立连接 | ≥2 Workers | 正式默认 | 合成测试数据 + Fault Injection | YES | 无 |
| TEST-014 | 钉定版本真实 PG；隔离 Database/Schema + 独立 Test Role | 按测试 | 正式默认 Isolation Level | 合成测试数据；单连接 SAVEPOINT 仅限非 Commit Visibility Adapter Test | 按测试类型 | 按测试 |
| TEST-015 | ≥1 | ≥1 | 正式默认 | 合成测试数据 + 受控 Secret Injection | YES | 无（安全断言） |
| TEST-016 | ≥2 独立 Connection/Session/Transaction（≥2 Delivery/Consumer Actor）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES（Dedup Marker 与消费业务更新真实 Commit 同事务） | 无（去重语义） |
| TEST-017 | ≥2 独立 Connection/Session/Transaction；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors（Relay + 恢复验证） | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 + 确定性故障注入（Relay Crash） | YES（Event 持久化真实 Commit） | 无（Crash 恢复） |
| TEST-018 | ≥2 独立 Connection/Session/Transaction（新旧 Publish Attempt）；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES | 无（stale 拒绝语义） |
| TEST-019 | 独立提交连接 + 独立 Polling 连接；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors（提交者 + Poller） | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 + wake-up 丢失注入 | YES（Intent 已真实 Commit） | 无（Polling 恢复） |
| TEST-020 | ≥2 独立 Connection/Session/Transaction；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors（并发重试） | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES | 无（幂等 + Lease 语义） |
| TEST-021 | ≥2 独立 Connection/Session/Transaction；精确 = REQUIRES TS-01 EVIDENCE | ≥2 独立 Actors | 正式默认 Isolation Level；精确 = REQUIRES TS-01 EVIDENCE | 合成测试数据 | YES | 无（顺序语义边界） |

### Table C — Fault, Environment & CI

| Row ID | Fault Injection | External Dependency | Cleanup Strategy | CI Tier | Required / Optional |
|---|---|---|---|---|---|
| TEST-001 | 确定性时序注入 | 无真实外部 Provider | 隔离 Database/Schema，独立清理 | Required PR Check（correctness-critical） | Required |
| TEST-002 | 无 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-003 | Lease 过期/接管注入 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-004 | 并发时序 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-005 | serialization 触发 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-006 | deadlock 触发 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-007 | 事务失败触发重试 | 不重调外部 Provider | 隔离 Schema | Required PR Check | Required |
| TEST-008 | Commit 成功响应丢失场景 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-009 | 无 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-010 | 并发 Claim 时序 | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-011 | Worker Crash 注入（bounded deterministic crash/reclaim） | 无 | 隔离 Schema | Bounded deterministic crash/reclaim correctness scenario = REQUIRED PR CHECK；Heavy recovery / soak / prolonged contention = SCHEDULED OR MANUAL（DQ-16） | Required |
| TEST-012 | Fault Injection（DEC-035 10 注入位置） | 无 | 隔离 Schema | Required PR Check（correctness-critical）+ Scheduled/Manual 高强度 | Required |
| TEST-013 | Fault Injection | 无 | 隔离 Schema | Required PR Check | Required |
| TEST-014 | 环境记录 + 确定性协调 | 无真实 Provider/凭证 | 独立 Test Role + 隔离 Database/Schema；并行 CI Worker 独立隔离 | Harness Qualification（随首个获授权 Persistence Spike） | Required（Harness 原则） |
| TEST-015 | 受控 Secret Injection + 失败日志 Redaction | 无真实凭证 | 隔离 Schema；无真实 Secret 泄漏 | Required PR Check（安全 Slice） | Required |
| TEST-016 | 重复 Delivery 注入 + Consumer 失败事务注入 | 无真实 Relay/Broker（语义验证） | 隔离 Schema | Required PR Check（correctness-critical，DQ-10） | Required |
| TEST-017 | Relay Crash 注入（durable publication 完成前崩溃） | 无真实 Relay/Broker 实现（不选择拓扑） | 隔离 Schema | Bounded relay-crash recoverability = REQUIRED PR CHECK；Heavy recovery / soak = SCHEDULED OR MANUAL（DQ-16） | Required |
| TEST-018 | stale Publish Attempt 注入（在新有效 Attempt 或完成状态之后返回） | 无真实 Relay 实现 | 隔离 Schema | Required PR Check（correctness-critical） | Required |
| TEST-019 | wake-up 丢失注入（Poll Interval / LISTEN-NOTIFY 配置留 RFC-003） | 无真实 Worker Backend（留 RFC-003） | 隔离 Schema | Required PR Check（bounded polling recoverability） | Required |
| TEST-020 | 并发重试时序注入 | 无真实外部 Provider | 隔离 Schema | Required PR Check（correctness-critical） | Required |
| TEST-021 | 顺序冲突构造（仅验证已接受语义边界） | 无真实调度算法（不选择） | 隔离 Schema | Required PR Check（bounded ordering semantic boundary） | Required |

### Table D — Evidence & Traceability

| Row ID | Evidence Produced | Owner | Source / Traceability | Decision Status | Evidence Status |
|---|---|---|---|---|---|
| TEST-001 | NOT YET AVAILABLE | TS-01 Spike Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-07 §59 | Coverage = ACCEPTED DECISION（DQ-07/16） | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-002 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-07 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-003 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-07 §59 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-004 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-07 §59 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-005 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-07 §59 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-006 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-07 §59 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-007 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-07/08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-008 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-009 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-010 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-09 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-011 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-09 §97 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-012 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-16 · DEC-035 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-013 | NOT YET AVAILABLE | 同 TEST-001 | rfc-002-decision-questions.md §DQ-07 §59 · DQ-11 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-014 | NOT YET AVAILABLE | QL-01 Harness Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-16 §56-57 | Harness Qualification = REQUIRED / NOT AUTHORIZED | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-015 | NOT YET AVAILABLE | TS-01 Spike Owner + Security Governance（未授权） | rfc-002-decision-questions.md §DQ-17 · ARP-10 §9.2 | QL-02 Slice = ACCEPTED AS PLANNING CATALOG / NOT EXECUTED | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-016 | NOT YET AVAILABLE | TS-01 Spike Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-10 §121 | Coverage = ACCEPTED DECISION（DQ-10） | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-017 | NOT YET AVAILABLE | TS-01 Spike Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-10 §121 | Coverage = ACCEPTED DECISION（DQ-10） | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-018 | NOT YET AVAILABLE | TS-01 Spike Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-10 §121 | Coverage = ACCEPTED DECISION（DQ-10） | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-019 | NOT YET AVAILABLE | TS-01 Spike Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-09 §97 | Coverage = ACCEPTED DECISION（DQ-09） | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-020 | NOT YET AVAILABLE | TS-01 Spike Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-09 §94 | Coverage = ACCEPTED DECISION（DQ-09） | NOT YET EVIDENCED / REQUIRES TS-01 |
| TEST-021 | NOT YET AVAILABLE | TS-01 Spike Owner（未授权）= PENDING USER DECISION | rfc-002-decision-questions.md §DQ-09 §94 | Coverage = ACCEPTED DECISION（DQ-09） | NOT YET EVIDENCED / REQUIRES TS-01 |

---

## 9. Cross-artifact References

| 本 Artifact 元素 | 引用目标 | 关系 |
|---|---|---|
| TEST-001~TEST-013 Requirement | ARP-02 CONC-xxx · ARP-03 IDEM-xxx | 测试覆盖指向并发/幂等场景行。 |
| TEST-012 | ARP-01 INV-xxx（Atomic Business Commit 参与者） | DEC-035 原子提交不变量。 |
| TEST-014 | ARP-10 §9（QL-01 关系） | Common Harness Qualification。 |
| TEST-015 | ARP-10 §9.2（QL-02 TS-01 Slice） | 安全 Slice 引用 ARP-10 Catalog。 |
| TEST-016 Consumer Dedup | ARP-02 CONC-013 · ARP-04 REC-013 · ARP-03 IDEM-011 / IDEM-012 | Duplicate Delivery + Consumer Dedup Marker + Consumer Business Update 同事务。 |
| TEST-017 Relay Crash Recovery | ARP-02 CONC-028 · ARP-04 REC-013 · ARP-03 IDEM-015 | Relay 崩溃后 Event 可恢复；Event Identity 稳定、Attempt Identity 每次新建。 |
| TEST-018 stale Event Publish Attempt | ARP-02 CONC-029 · ARP-04 REC-013 · ARP-03 IDEM-015 | stale Attempt 不覆盖当前发布状态。 |
| TEST-019 Polling Recovery | ARP-02 CONC-027 · ARP-04 REC-009 · ARP-03 IDEM-008 | wake-up 丢失后权威 Polling 重新发现 Intent；Claim 与 wake-up 分离。 |
| TEST-020 Simultaneous Work Retry | ARP-02 CONC-025 · ARP-04 REC-009 · ARP-03 IDEM-008 | 并发重试不重复业务效果。 |
| TEST-021 Ordering Conflict | ARP-02 CONC-026 · ARP-04 REC-009 | 顺序语义边界（不选择调度算法）。 |

---

## 10. Review Checklist（Artifact-specific）

- [x] 覆盖 TS-01 所需最小 Slice（revision CAS / unique constraint / Lease-Fencing / SKIP LOCKED / 40001 / 40P01 / retry identity / idempotency replay·conflict / Durable Work Intent / crash recovery / Atomic Commit fault windows / no partial write / QL-01 Harness / TS-01 QL-02 Slice / Consumer Dedup / Relay Crash Recovery / stale Event Publish Attempt / Polling Recovery / Simultaneous Work Retry / Ordering Conflict）。
- [x] DQ-10 Integration Event Duplicate Delivery / Consumer Dedup / Relay Crash / stale Publish Attempt 已由独立 TEST 行覆盖（DQ-10 分配给 DQ-07 真实 PostgreSQL Multi-worker Spike）。
- [x] Test Layer 仅使用受控词汇。
- [x] Real PostgreSQL Required = YES（全部正式持久化/并发/幂等/迁移语义）。
- [x] 未知实测值写 `REQUIRES TS-01 EVIDENCE`。
- [x] Evidence Produced 统一 = `NOT YET AVAILABLE`。
- [x] 未把 SQLite Spike-001 证据当作 PostgreSQL Acceptance Evidence。
- [x] 未创建测试代码 / Fixture / Container / CI Workflow。
- [x] 每行有 Source / Traceability；Evidence Status = NOT YET EVIDENCED / REQUIRES TS-01。
- [x] 18 正式列 + Source/Traceability + Decision Status + Evidence Status 全部出现于 Table A–D（见第 7 节 Column Index）。

---

## 11. Open Questions

| # | 问题 | 决定所有者 | 下一 Gate |
|---|---|---|---|
| OQ-1 | Connection Count / Worker Count / Isolation Level 精确实测值 | TS-01 Spike Owner + 用户 | TS-01 Spike Planning Gate |
| OQ-2 | Common Persistence Test Harness 具体钉定版本与环境 | 用户 | TS-01 Spike Planning Gate（QL-01） |
| OQ-3 | 完整 ARP-09（Migration / Production-topology Qualification 等）补齐范围 | 用户 | 后续 Wave / Full ARP-09 Gate |

---

## 12. Explicit Non-decisions

- 本 Slice 不创建测试代码、Fixture、Container 或 CI Workflow。
- 本 Slice 不创建 Common Persistence Test Harness（Common Persistence Test Harness = NOT CREATED）。
- 本 Slice 不把 SQLite Spike-001 证据当作 PostgreSQL Acceptance Evidence。
- 本 Slice 不填写未知实测值（统一 REQUIRES TS-01 EVIDENCE）。
- 本 Slice 不声称完成完整 ARP-09。
- 本 Slice 不自我接受；用户已于 2026-08-06 作出外部接受决定，范围仅为 TS-01 Minimum Slice。
- 本 Slice 不授权 TS-01 Planning / Execution 或任何实现。
