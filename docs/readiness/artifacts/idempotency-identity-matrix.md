# ARP-03 — Idempotency Identity Matrix（TS-01 Minimum Slice）

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

Full ARP-03 Completion =
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

> 本文件由 Wave 1 Readiness Artifact Creation Authorization（Level 2）创建。用户于 2026-08-06 明确接受本 TS-01 Minimum Slice；本 Slice 仅覆盖 TS-01 所需的最小幂等身份语义，**不声称完成完整 ARP-03**。`Artifact Acceptance ≠ Spike Authorization`。
> 本 Slice **不设计统一跨模块万能幂等表**（Candidate A 已被 DQ-08 拒绝）；**不发明具体 HTTP Idempotency Header**（留 RFC-004）；**不设置具体 Retention Period**（留 DQ-15）。

---

## 1. Artifact Identity

| 项 | 值 |
|---|---|
| Artifact ID | ARP-03 |
| Exact Name | Idempotency Identity Matrix |
| Purpose | 为 TS-01 所需操作建立幂等身份语义矩阵，明确区分 Command ID / Idempotency Key / Attempt ID / Stage Run ID / Dispatch ID / Delivery Attempt ID / Provider Call Identity，并给出 Retry 与 Rerun 的身份分离。 |
| Scope | TS-01 MINIMUM SLICE ONLY |
| Source / Traceability | RFC-002-DQ-08 §4.11（Idempotency Identity Matrix = REQUIRED / NOT AUTHORIZED，18 项字段）；RFC-002-DQ-09 §93（补充 Dispatch ID / Delivery Attempt Identity / Consumer Scope / Provider Call Identity） |
| Decision Status | ACCEPTED — TS-01 MINIMUM SLICE ONLY（2026-08-06） |

---

## 2. Owning DQ / DEC / RFC

| 项 | 值 | Source / Traceability |
|---|---|---|
| Primary Owning DQ | RFC-002-DQ-08（Idempotency Model，Primary Direction = Candidate B，Supporting Principle = Candidate C） | rfc-002-decision-questions.md §DQ-08 |
| Contributing DQ | RFC-002-DQ-09（Durable Dispatch 身份）· DQ-07（Lease/Fencing 协同）· DQ-15（Retention）· DQ-17（Security） | rfc-002-decision-questions.md |
| Related DEC | DEC-033（Input Fingerprint / Idempotency Record）· DEC-035（Atomic Commit） | docs/decisions/ |
| Downstream RFC Boundary | RFC-004（HTTP 幂等 Header/状态码/响应协议） | rfc-002-analysis-cross-rfc-boundary.md |

---

## 3. Authoritative Inputs

| 输入 | 角色 | Source / Traceability |
|---|---|---|
| RFC-002-DQ-08 Accepted Decision | 分层幂等模型 + 身份语义 + Matrix 18 列 | rfc-002-decision-questions.md §DQ-08 |
| RFC-002-DQ-09 §93 | Matrix 补充 4 列（Dispatch ID / Delivery Attempt Identity / Consumer Scope / Provider Call Identity） | rfc-002-decision-questions.md §DQ-09 |
| DEC-033（Workflow Runtime） | Input Fingerprint 字段（task_id / skill_name / input_version_ids / source_set_version_id / skill_contract_version / execution_configuration_version / logical_operation） | docs/architecture/data-architecture.md §DEC-033 |

---

## 4. Ownership & Review Roles

| 角色 | 值 | 说明 |
|---|---|---|
| Primary Owner Role | Idempotency Architecture Owner | 具体人选 = PENDING USER DECISION。 |
| Contributors | 各幂等层 Owning Module | 每份幂等记录有且仅有一个 Owning Module（DQ-02/DQ-08）。 |
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

Implementation =
NOT AUTHORIZED
```

> 分层幂等模型（Candidate B）：各幂等层由相应 Owning Module 分层存储，共享统一概念与行为契约，不采用统一物理表；Candidate A（跨模块万能 Idempotency Table）已拒绝。

---

## 6. Column Index（22 正式列 + Source/Traceability + Decision Status + Evidence Status 映射）

本 Slice 的 22 个正式列（DQ-08 18 列 + DQ-09 4 补充列）+ `Source / Traceability` + `Decision Status` + `Evidence Status` 按主题分组呈现于第 7 节 Table A–E；各表共享同一 `IDEM-xxx` 行 ID 与行序。列映射如下：

| 正式列 | 所在表 |
|---|---|
| Operation · Owning Module · Logical Command ID · Idempotency Scope · Idempotency Key Source | Table A |
| Retry Identity · Rerun Identity · Attempt ID · Stage Run ID | Table B |
| Input Fingerprint Fields · Fingerprint Schema Version · State Machine · Unique Constraint · Atomic Transaction Boundary | Table C |
| Result Replay · Provider Idempotency · Retention Owner | Table D |
| Dispatch ID · Delivery Attempt Identity · Consumer Scope · Provider Call Identity · Related DQ / DEC / RFC · Source / Traceability · Decision Status · Evidence Status | Table E |

---

## 7. Matrix（TS-01 Minimum Slice）

> 行 ID 规则：`IDEM-001`…（Artifact Traceability ID，非数据库主键 / 生产 ID）。
> 受控未决标记：`PENDING OWNER DECISION` / `DEFERRED TO RFC-004` / `DEFERRED TO RFC-003` / `NOT APPLICABLE` / `NOT YET EVIDENCED` / `REQUIRES TS-01`。

### Table A — Operation Identity & Scope

| Row ID | Operation | Owning Module | Logical Command ID | Idempotency Scope | Idempotency Key Source |
|---|---|---|---|---|---|
| IDEM-001 | Transactional Application Command（业务状态修改） | 执行该业务修改的业务模块（DQ-08(a)）；exact module = PENDING BUSINESS DEFINITION | Application 层生成；Retry 复用同一 Command ID | owning module / operation type / target business scope | 调用者提供或 Application 派生（Scope 内唯一） |
| IDEM-002 | Exact Replay（同 Key + 同 Fingerprint 重放） | 同 IDEM-001 Owning Module | 复用原 Command ID | 同 IDEM-001 | 同 IDEM-001 |
| IDEM-003 | Concurrent Exact Replay（并发精确重放） | 同 IDEM-001 Owning Module | 复用原 Command ID | 同 IDEM-001 | 同 IDEM-001 |
| IDEM-004 | Same Key / Different Fingerprint（幂等冲突） | 同 IDEM-001 Owning Module | 不得覆盖原 Command 记录 | 同 IDEM-001 | 同 Key，不同 Fingerprint |
| IDEM-005 | Transient Failure Retry（瞬时失败重试） | 同 IDEM-001 Owning Module | 复用同一 Command ID | 同 IDEM-001 | 同 IDEM-001 |
| IDEM-006 | Commit Outcome Unknown Retry（提交结果未知重试） | 同 IDEM-001 Owning Module | 复用同一 Command ID | 同 IDEM-001 | 同 IDEM-001 |
| IDEM-007 | Intentional Rerun（有意重跑） | 同 IDEM-001 Owning Module | 新 Command ID（保留 rerun_of / parent_command_id） | 新逻辑幂等身份 | 新 Idempotency Key |
| IDEM-008 | Durable Work Intent（可靠工作意图） | Integration/Dispatch Capability（DQ-09） | 关联触发 Command ID | Dispatch Scope | dispatch_id（Retry 稳定） |
| IDEM-009 | Work Intent Claim Attempt（意图领取尝试） | Dispatch Capability | 关联 Intent 的 Command | Dispatch Scope | dispatch_id + holder/lease |
| IDEM-010 | Durable Work Intent Delivery / Execution Attempt | Dispatch Capability | 关联 Intent Command | Dispatch Scope | delivery_attempt_id（每次 Work Intent claim/execution attempt 新建） |
| IDEM-011 | Consumer Dedup（消费者去重） | 消费模块（DQ-08(b)） | 关联被消费事件身份 | Consumer Scope | Integration Event 使用 `source + event_id + Consumer Scope`；Work Intent 如需消费去重则使用其独立 `dispatch_id + Consumer Scope`，两类身份不得互换 |
| IDEM-012 | Integration Event Identity（集成事件身份） | Integration Event Capability | 关联产生事实的 Command | source + event_id | source + event_id 唯一识别逻辑事件 |
| IDEM-013 | Provider Call Identity（Provider 调用身份语义边界） | Provider/Integration 模块（DQ-08(d)） | 关联触发 Command | Provider Call Scope | 稳定 Provider Call Identity（绑定 Input Fingerprint） |
| IDEM-014 | Retry 与 Rerun 身份分离（对照） | 各相应 Owning Module | 见 Retry/Rerun Identity 列 | — | — |
| IDEM-015 | Integration Event Publish / Delivery Attempt | Integration Event Capability | 关联产生事实的 Command | Integration Event Scope | Logical Event Identity = source + event_id（稳定）；Publish Attempt Identity = 每次 relay publication 新建 |

### Table B — Retry / Rerun / Attempt Identity

| Row ID | Retry Identity | Rerun Identity | Attempt ID | Stage Run ID |
|---|---|---|---|---|
| IDEM-001 | same Command ID + same Idempotency Key + same Stage Run ID + same Input Fingerprint + new Attempt ID + no new intended business operation | new Command ID + new logical Idempotency identity + new Stage Run ID + new Attempt ID + explicit relation + may produce new business version | 每次 Retry 新建 | 同一 Stage Run 内 Retry 保持相同 |
| IDEM-002 | 重放不创建新 Attempt（返回首次结果） | NOT APPLICABLE | NOT APPLICABLE | 保持原 Stage Run |
| IDEM-003 | 并发重放仅一次业务效果（唯一约束 + 执行所有权） | NOT APPLICABLE | 按 DQ-07 | 保持原 Stage Run |
| IDEM-004 | 不盲目自动重试 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE |
| IDEM-005 | 新 Attempt ID；不永久固化瞬时失败 | NOT APPLICABLE | 每次 Retry 新建 | 保持相同 Stage Run |
| IDEM-006 | 复用已产生不可变外部结果重试 Commit；不重调 Provider | NOT APPLICABLE | 新 Attempt ID | 保持相同 Stage Run |
| IDEM-007 | NOT APPLICABLE（Rerun 非 Retry） | new Command ID + rerun_of；成功后可产生新 Domain Version | new Attempt ID | new Stage Run ID |
| IDEM-008 | dispatch_id Retry 稳定 | Intentional Rerun 新 dispatch_id（保留 rerun_of） | 按 Attempt | NOT APPLICABLE |
| IDEM-009 | Claim 失败不重复领取 | NOT APPLICABLE | 新 Attempt | NOT APPLICABLE |
| IDEM-010 | Work Intent Delivery Retry 保持 dispatch_id，新 delivery_attempt_id | Intentional Rerun 新 Dispatch ID | delivery_attempt_id 每次 Work Intent claim/execution attempt 新建 | NOT APPLICABLE |
| IDEM-011 | Consumer Dedup Marker 与业务更新同事务 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE |
| IDEM-012 | Retry/重复投递保持相同 Event Identity | Intentional Rerun 可新 Event Identity（保留 Causation/Correlation） | NOT APPLICABLE | NOT APPLICABLE |
| IDEM-013 | 同一逻辑调用 Retry 复用相同 Provider Idempotency Key | Intentional Rerun 新 Provider Call Identity | 关联 Attempt | NOT APPLICABLE |
| IDEM-014 | Retry = same Command ID + same Key + same Stage Run + same Fingerprint + new Attempt | Rerun = new Command ID + new 身份 + relation | Retry/Rerun 均 new Attempt | Retry same / Rerun new |
| IDEM-015 | Retry/重复投递保持同一 Event Identity（source + event_id） | Intentional Rerun 新业务事实可新 Event Identity（保留 Causation/Correlation） | Publish Attempt Identity 每次 relay publication 新建 | NOT APPLICABLE |

### Table C — Fingerprint & State

| Row ID | Input Fingerprint Fields | Fingerprint Schema Version | State Machine | Unique Constraint | Atomic Transaction Boundary |
|---|---|---|---|---|---|
| IDEM-001 | task_id / skill_name / input_version_ids / source_set_version_id / skill_contract_version / execution_configuration_version / logical_operation（DEC-033）；含决定业务效果字段，排除 trace/arrival/retry/Attempt 等观测字段 | PENDING OWNER DECISION（canonicalization version + fingerprint schema version + comparison semantics；不预设密码学算法） | IN_PROGRESS / SUCCEEDED / FAILED_TERMINAL / ABANDONED-EXPIRED-RETRYABLE（精确 Enum 留实现） | Scope + Key（+ Fingerprint 冲突检测） | 与业务状态更新同一 PostgreSQL 事务 |
| IDEM-002 | 同 IDEM-001 | 同 IDEM-001 | 复用原记录状态 | 同 IDEM-001 | 重放不再执行业务副作用 |
| IDEM-003 | 同 IDEM-001 | 同 IDEM-001 | 并发仅一次 SUCCEEDED | 同 IDEM-001 | 同 IDEM-001 |
| IDEM-004 | 同 Key 不同 Fingerprint | 同 IDEM-001 | 返回 Idempotency Key Conflict | Scope + Key | 不覆盖不执行 |
| IDEM-005 | 同 IDEM-001 | 同 IDEM-001 | 瞬时失败不固化为终局 | 同 IDEM-001 | 同 IDEM-001 |
| IDEM-006 | 同 IDEM-001 | 同 IDEM-001 | 重放或继续 | 同 IDEM-001 | 同 IDEM-001 |
| IDEM-007 | 新 Fingerprint（新逻辑身份） | 同 IDEM-001 | 新记录生命周期 | 新 Scope + Key | 新业务事务 |
| IDEM-008 | 关联业务 Fingerprint | PENDING OWNER DECISION | Intent 状态机（留 DQ-09/RFC-003） | Intent 唯一性 | Intent 与业务状态同一 Atomic Commit |
| IDEM-009 | 关联 Intent Fingerprint | PENDING OWNER DECISION | Claim 状态 | Lease/Holder 唯一 | 短事务 Claim（DQ-07） |
| IDEM-010 | 关联 Intent Fingerprint | PENDING OWNER DECISION | Delivery 状态 | delivery_attempt 身份 | 按 DQ-09 |
| IDEM-011 | 被消费事件身份 | PENDING OWNER DECISION | Dedup 状态 | Integration Event Identity + Consumer Scope 唯一；Work Intent identity 在自身 Scope 内独立 | Dedup Marker 与消费业务更新同事务 |
| IDEM-012 | event payload fingerprint | PENDING OWNER DECISION（event_schema_version） | Outbox 发布状态机（留 RFC-003） | source + event_id 唯一 | Outbox 与业务事实同一 Atomic Commit |
| IDEM-013 | Input Fingerprint 绑定 Provider Key | PENDING OWNER DECISION | Provider Call Ledger 状态 | Provider Call Identity 唯一 | DB 事务 Retry 不生成新 Provider Key |
| IDEM-014 | — | — | — | — | — |
| IDEM-015 | event payload fingerprint（含 source + event_id） | PENDING OWNER DECISION（exact physical field = DEFERRED TO RFC-003） | Outbox 发布状态机（留 RFC-003） | source + event_id 唯一（逻辑事件） | Outbox 与业务事实同一 Atomic Commit |

### Table D — Replay, Provider & Retention

| Row ID | Result Replay | Provider Idempotency | Retention Owner |
|---|---|---|---|
| IDEM-001 | 业务成功时重放原 Application Result Snapshot（不重新执行副作用；不含 ORM Entity/Session/Exception/未脱敏 Secret） | 按 IDEM-013 | 幂等层 Owning Module（DQ-15） |
| IDEM-002 | 重放首次成功 Application Result | 不重调 Provider | 同 IDEM-001 |
| IDEM-003 | 仅一次结果可重放 | 不重调 Provider | 同 IDEM-001 |
| IDEM-004 | 不重放为新结果 | NOT APPLICABLE | 同 IDEM-001 |
| IDEM-005 | 瞬时失败不永久固化终局 | 不重调 Provider | 同 IDEM-001 |
| IDEM-006 | Commit 成功后重放原结果 | 不重调 Provider | 同 IDEM-001 |
| IDEM-007 | Rerun 成功可产生新结果（非重放旧结果） | Intentional Rerun 新 Provider Call Identity | 同 IDEM-001 |
| IDEM-008 | Intent 完成语义留 DQ-09/RFC-003 | 按 IDEM-013 | Dispatch Capability（DQ-15） |
| IDEM-009 | NOT APPLICABLE | NOT APPLICABLE | Dispatch Capability（DQ-15） |
| IDEM-010 | NOT APPLICABLE | 按 IDEM-013 | Dispatch Capability（DQ-15） |
| IDEM-011 | Consumer 重复投递只一次业务效果 | NOT APPLICABLE | 消费模块（DQ-15） |
| IDEM-012 | Consumer 依 Event Identity 去重 | NOT APPLICABLE | Integration Event Capability（DQ-15） |
| IDEM-013 | Provider 结果引用（不存 Secret Value） | 稳定 Provider Call Identity；不支持原生 Key 时维护 Durable Call Ledger | Provider/Integration 模块（DQ-15） |
| IDEM-014 | — | — | — |
| IDEM-015 | Consumer 依 Event Identity 去重；重复投递只一次业务效果 | NOT APPLICABLE（Publish Attempt Identity ≠ dispatch_id ≠ Work Intent delivery_attempt_id） | Integration Event Capability（DQ-15） |

### Table E — Dispatch Identity & Traceability

| Row ID | Dispatch ID | Delivery Attempt Identity | Consumer Scope | Provider Call Identity | Related DQ / DEC / RFC | Source / Traceability | Decision Status | Evidence Status |
|---|---|---|---|---|---|---|---|---|
| IDEM-001 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | DQ-08 · DEC-033 · DEC-035 | rfc-002-decision-questions.md §DQ-08 | Identity Semantics = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-002 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | DQ-08 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-003 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | DQ-08 · DQ-07 | rfc-002-decision-questions.md §DQ-08/07 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-004 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | DQ-08 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-005 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | DQ-08 · DQ-07 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-006 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | 复用同一 Provider Call Identity | DQ-08 · DQ-07 §47-48 | rfc-002-decision-questions.md §DQ-08/07 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-007 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | Intentional Rerun 新 Provider Call Identity | DQ-08 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-008 | dispatch_id（Retry 稳定） | NOT APPLICABLE | NOT APPLICABLE | 按 IDEM-013 | DQ-09 · DQ-08 | rfc-002-decision-questions.md §DQ-09 | ACCEPTED DECISION；Relay = DEFERRED TO RFC-003 | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-009 | dispatch_id | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | DQ-09 · DQ-07 | rfc-002-decision-questions.md §DQ-09 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-010 | dispatch_id（stable for the logical Work Intent） | delivery_attempt_id（new for each Work Intent claim/execution attempt） | NOT APPLICABLE | NOT APPLICABLE（Work Intent Delivery，非 Integration Event Publication Attempt） | DQ-09 | rfc-002-decision-questions.md §DQ-09 | ACCEPTED DECISION（DQ-09 Work Intent） | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-011 | Integration Event Consumer = NOT APPLICABLE；Work Intent Consumer 如适用则使用其独立 dispatch_id | NOT APPLICABLE | Consumer Scope（与被消费的逻辑身份组合去重） | NOT APPLICABLE | DQ-08(b) · DQ-10 | rfc-002-decision-questions.md §DQ-08/10 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-012 | NOT APPLICABLE | NOT APPLICABLE | Consumer Scope（消费去重） | NOT APPLICABLE | DQ-10 | rfc-002-decision-questions.md §DQ-10 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-013 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | 稳定 Provider Call Identity（绑定 Fingerprint） | DQ-08(d) · DQ-17 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION；不调用真实 Provider | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-014 | 按各层 | 按各层 | 按各层 | 按各层 | DQ-08 · DQ-07 · DQ-09 | rfc-002-decision-questions.md §DQ-08 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| IDEM-015 | NOT APPLICABLE（Integration Event ≠ Durable Work Intent；≠ dispatch_id） | Publish Attempt Identity（new for each relay publication attempt；exact physical field = PENDING OWNER DECISION / DEFERRED TO RFC-003） | Consumer Scope（消费去重） | NOT APPLICABLE | DQ-10 · DQ-08 · RFC-003 | rfc-002-decision-questions.md §DQ-10 | ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |

---

## 8. Cross-artifact References

| 本 Artifact 元素 | 引用目标 | 关系 |
|---|---|---|
| IDEM-001~IDEM-007 Operation/Boundary | ARP-01 INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008 / INV-009 | **通用幂等身份契约**（适用于全部版本化业务对象：Facts/Insights/Positioning/Strategy/Brief/ExecutionBrief/Source），非特定单一 Aggregate。 |
| IDEM-008 Durable Work Intent | ARP-04 REC-009（Durable Work Intent Row） | Work Intent 身份（dispatch_id Retry 稳定）。 |
| IDEM-009 Work Intent Claim | ARP-04 REC-009（Durable Work Intent Row） | Claim 身份（dispatch_id + holder/lease）。 |
| IDEM-010 Durable Work Intent Delivery / Execution Attempt | ARP-04 REC-009（Durable Work Intent Row） | delivery_attempt_id 属 DQ-09 Work Intent 投递/执行语义；**不用于 Integration Event Publication Attempt**。 |
| IDEM-011 Consumer Dedup | ARP-04 REC-013（Integration Event / Outbox Row）· ARP-02 CONC-013 | Consumer 依 Event Identity + Consumer Scope 去重。 |
| IDEM-012 Integration Event Identity | ARP-04 REC-013（Integration Event / Outbox Row） | source + event_id 唯一识别逻辑事件；**不指向 Observability Event 记录类**。 |
| IDEM-013 Provider Call Identity | ARP-04 REC-010（Provider Call Ledger Row） | 稳定 Provider Call Identity（TS-01 不调用真实 Provider）。 |
| IDEM-002 Exact Replay | ARP-02 CONC-011 · ARP-09 TEST-008 | 幂等重放并发场景与测试。 |
| IDEM-003 Concurrent Exact Replay | ARP-02 CONC-011 · ARP-09 TEST-008 | 并发精确重放仅一次业务效果。 |
| IDEM-004 Same Key / Different Fingerprint | ARP-02 CONC-012 · ARP-09 TEST-009 | 幂等冲突。 |
| IDEM-005 Transient Failure Retry | ARP-02 CONC-010 · ARP-09 TEST-007 | 事务重试身份保持。 |
| IDEM-006 Commit Outcome Unknown Retry | ARP-02 CONC-015 | 提交结果未知重试（TS-01 Slice 无独立 TEST 行，随 CONC-015 覆盖）。 |
| IDEM-007 Intentional Rerun | ARP-01 INV-002 / INV-003 / INV-004 / INV-005 / INV-007 / INV-008（Rerun 成功后可产生新业务版本） | 通用 Rerun 身份契约。 |
| IDEM-008~IDEM-010 | ARP-02 CONC-004 / CONC-005 / CONC-019 / CONC-025 / CONC-027 · ARP-09 TEST-010 / TEST-019 / TEST-020 | Work Intent Claim / No Duplicate / Simultaneous Retry / Polling Recovery 并发场景与测试。 |
| IDEM-011 Consumer Dedup | ARP-04 REC-013 · ARP-02 CONC-013 · ARP-09 TEST-016 | Consumer 依 Event Identity + Consumer Scope 去重（DQ-10 已分配给 DQ-07 真实 PostgreSQL Multi-worker Spike）。 |
| IDEM-012 Integration Event Identity | ARP-04 REC-013 · ARP-02 CONC-013 / CONC-028 / CONC-029 · ARP-09 TEST-016 / TEST-017 / TEST-018 | Event Identity（source + event_id）在 Retry / 重复投递中保持稳定。 |
| IDEM-015 Integration Event Publish / Delivery Attempt | ARP-04 REC-013（Integration Event / Outbox）· ARP-02 CONC-028（Relay Crash）/ CONC-029（Stale Publish Attempt）· ARP-09 TEST-017 / TEST-018 | Publish / Delivery Attempt Identity 每次 relay publication 新建。 |
| IDEM-014 Retry 与 Rerun 身份分离 | 通用身份契约（跨 IDEM-005 / IDEM-007） | 对照行，不指向特定 Aggregate。 |

> **身份分离（Review Remediation）**：
> `Integration Event Publish Attempt Identity ≠ dispatch_id`；
> `Integration Event Publish Attempt Identity ≠ Durable Work Intent delivery_attempt_id`；
> `Integration Event Identity（source + event_id）≠ Publish Attempt Identity`。
> IDEM-010 仅承载 Durable Work Intent Delivery / Execution Attempt（DQ-09）；Integration Event Publish / Delivery Attempt 由独立的 IDEM-015 承载（DQ-10），二者身份不得复用或混用。

---

## 9. Review Checklist（Artifact-specific）

- [x] 覆盖 TS-01 所需最小身份 Slice（Transactional Application Command / Exact Replay / Concurrent Exact Replay / Same Key-Different Fingerprint / Transient Failure Retry / Commit Outcome Unknown Retry / Intentional Rerun / Durable Work Intent / Work Intent Claim / Durable Work Intent Delivery-Execution Attempt / Consumer Dedup / Integration Event Identity / Integration Event Publish-Delivery Attempt / Provider Call Identity / Retry-vs-Rerun 分离）。
- [x] Work Intent Attempt（IDEM-010）与 Integration Event Publish Attempt（IDEM-015）身份彻底分离；未把 `dispatch_id` / `delivery_attempt_id` 用作 Integration Event 默认 Identity。
- [x] 未设计统一跨模块万能幂等表（Candidate A 已拒绝）。
- [x] 未发明具体 HTTP Idempotency Header（留 RFC-004）。
- [x] 未设置具体 Retention Period（留 DQ-15）。
- [x] Retry 与 Rerun 身份语义明确分离。
- [x] 数据库事务 Retry 不生成新 Provider Key、不重调 Provider。
- [x] Checkpoint / thread_id 未作为业务幂等记录。
- [x] 每行有 Source / Traceability；Evidence Status = NOT YET EVIDENCED / REQUIRES TS-01。
- [x] 22 正式列 + Source/Traceability + Decision Status + Evidence Status 全部出现于 Table A–E（见第 6 节 Column Index）。

---

## 10. Open Questions

| # | 问题 | 决定所有者 | 下一 Gate |
|---|---|---|---|
| OQ-1 | Fingerprint Schema Version / canonicalization version / comparison semantics 具体值（不预设密码学算法） | 幂等层 Owning Module + 用户 | ARP-03 Acceptance 前 |
| OQ-2 | HTTP 幂等 Header / 状态码 / 响应协议 | 用户 | DEFERRED TO RFC-004 |
| OQ-3 | 幂等记录 Retention Period | 用户（DQ-15 拥有） | DQ-15 Retention Policy Table Gate |
| OQ-4 | 完整 ARP-03（非 TS-01 操作）补齐范围 | 用户 | 后续 Wave / Full ARP-03 Gate |

---

## 11. Explicit Non-decisions

- 本 Slice 不设计统一跨模块万能幂等表。
- 本 Slice 不发明 HTTP Idempotency Header。
- 本 Slice 不设置 Retention Period 数值。
- 本 Slice 不调用真实 Provider（Provider Call Identity 仅语义边界）。
- 本 Slice 不声称完成完整 ARP-03。
- 本 Slice 不自我接受；用户已于 2026-08-06 作出外部接受决定，范围仅为 TS-01 Minimum Slice。
- 本 Slice 不授权 Technical Spike Planning / Execution 或任何实现。
