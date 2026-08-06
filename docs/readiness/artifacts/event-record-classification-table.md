# ARP-04 — Event & Record Classification Table

## 0. Artifact Status

```text
Status =
ACCEPTED — USER DECISION 2026-08-06

Wave =
WAVE 1

Scope =
WAVE 1 FULL VOCABULARY / FOUNDATION ARTIFACT

Artifact Acceptance =
ACCEPTED — USER DECISION 2026-08-06

Artifact Creation Authorization =
AUTHORIZED

Technical Spike Planning / Execution =
NOT AUTHORIZED

Implementation =
NOT AUTHORIZED
```

> 本文件由 Wave 1 Readiness Artifact Creation Authorization（Level 2）创建。用户于 2026-08-06 明确接受本 Artifact 的 Wave 1 Full Vocabulary / Foundation 范围。`Artifact Creation ≠ Artifact Acceptance`；`Artifact Acceptance ≠ Spike Authorization`。

---

## 1. Artifact Identity

| 项 | 值 |
|---|---|
| Artifact ID | ARP-04 |
| Exact Name | Event & Record Classification Table |
| Purpose | 对 Repository 中已有依据的 Business Occurrence / Record Class 建立受控分类，明确其是否持久化、与 Atomic Business Commit 的关系、是否需要 Delivery，并保持六类记录语义与相关概念分离。 |
| Scope | WAVE 1 FULL VOCABULARY / FOUNDATION ARTIFACT |
| Source / Traceability | RFC-002-DQ-10 §3.11（Classification Table = REQUIRED / NOT AUTHORIZED，16 项字段） |
| Decision Status | ACCEPTED — USER DECISION 2026-08-06 |

---

## 2. Owning DQ / DEC / RFC

| 项 | 值 | Source / Traceability |
|---|---|---|
| Primary Owning DQ | RFC-002-DQ-10（Event & Audit Persistence） | rfc-002-decision-questions.md §DQ-10 |
| Contributing DQ | RFC-002-DQ-09（Durable Dispatch）· DQ-11（Snapshot/History）· DQ-15（Retention）· DQ-17（Security Classification） | rfc-002-decision-questions.md |
| Related DEC | DEC-033（Runtime Records）· DEC-035（Atomic Commit）· DEC-029（Review/Audit History） | docs/decisions/ |
| Downstream RFC Boundary | RFC-003（Event Relay/Broker/Polling/Dead-letter）· RFC-007（Observability） | rfc-002-analysis-cross-rfc-boundary.md |

---

## 3. Authoritative Inputs

| 输入 | 角色 | Source / Traceability |
|---|---|---|
| RFC-002-DQ-10 Accepted Decision | 六类记录语义独立 + Classification Table 16 列 | rfc-002-decision-questions.md §DQ-10 |
| RFC-002-DQ-09 Accepted Decision | Durable Work Intent 独立语义（≠ Integration Event） | rfc-002-decision-questions.md §DQ-09 |
| DEC-033（Workflow Runtime 数据职责） | Runtime Records（Workflow Run / Skill Run / Attempt / RuntimeError） | docs/architecture/data-architecture.md §DEC-033 |
| DEC-029（Review Audit History） | Review 相关 Audit / State Transition | docs/architecture/data-architecture.md §DEC-029 |
| ARP-10 Security Vocabulary | Security Classification 列引用 | docs/readiness/artifacts/sensitive-data-secret-cryptographic-control-matrix.md |

---

## 4. Ownership & Review Roles

| 角色 | 值 | 说明 |
|---|---|---|
| Primary Owner Role | Event / Audit Architecture Owner | 具体人选 = PENDING USER DECISION。 |
| Contributors | Audit Capability Owner · Integration Event Capability Owner · 各业务模块 | 各记录类所有者。 |
| Reviewers | 用户（Product Decision Owner） | Artifact Acceptance 仅由用户决定。 |

---

## 5. Authorization Boundary

```text
Artifact Creation Authorization =
AUTHORIZED（本文件创建属 Level 2）

Artifact Acceptance =
ACCEPTED — USER DECISION 2026-08-06

Technical Spike Planning / Execution =
NOT AUTHORIZED

Implementation =
NOT AUTHORIZED
```

---

## 6. Controlled Vocabulary & Concept Separation（必须保持）

本表保持以下 12 个概念分离，不得混淆：

```text
Domain Event            （模块内部过去式业务事实，默认不自动持久化）
Audit Record            （append-only 权威问责证据）
State Transition Record （显式类型 Audit Record）
Application Event       （Commit 后本地 best-effort 通知，NON-DURABLE）
Integration Event       （跨边界事实，AT-LEAST-ONCE，不承诺 exactly-once）
Observability Event     （RFC-007 非权威 Telemetry）
Durable Work Intent     （DQ-09 可靠工作调度意图，≠ Integration Event）
Workflow Checkpoint     （Runtime Recovery State，≠ Business Current Truth）
Business Current Truth  （权威当前业务状态）
Immutable Business Version（不可变正式业务版本）
Derived Query Projection（派生非权威读取模型）
Provider Call Ledger    （Provider 调用账本，无 Secret Value）
```

硬性规则（源自 DQ-10/DQ-09/DQ-13/DQ-17）：
- **不得承诺 Exactly-once Delivery**；Integration Event Delivery = AT-LEAST-ONCE，exactly-once business effect 依赖 DQ-08 幂等 + Consumer Dedup + 命名唯一约束 + DQ-07 Lease/Fencing + revision + Atomic Commit 组合。
- **Durable Work Intent 不得分类为 Integration Event。**
- **Audit 不得充当通用 Event Bus。**
- **Observability Event 不得成为业务权威记录。**
- **Workflow Checkpoint 不得成为 Business Current Truth。**
- `Schema Version` 具体值未知时使用 `PENDING OWNER DECISION`，不得虚构。
- **Retention Period 不得填写**（留 DQ-15）。

> Source / Traceability：RFC-002-DQ-10 · DQ-09 · DQ-13 · DQ-17。Decision Status = ACCEPTED DECISION（分离原则）。

---

## 7. Column Index（16 正式列 + Source/Traceability + Decision Status 映射）

本表的 16 个正式列 + `Source / Traceability` + `Decision Status` 按主题分组呈现于第 8 节 Table A–C；各表共享同一 `REC-xxx` 行 ID 与行序。列映射如下：

| 正式列 | 所在表 |
|---|---|
| Business Occurrence · Domain Event · Audit Record · State Transition Record · Application Event · Integration Event · Observability Event | Table A |
| Owning Module · Persistence Required · Transaction Boundary · Delivery Guarantee · Idempotency Identity | Table B |
| Schema Version · Retention Owner · Security Classification · Related DQ / DEC / RFC · Source / Traceability · Decision Status | Table C |

---

## 8. Matrix

> 行 ID 规则：`REC-001`…（Artifact Traceability ID，非数据库主键 / 生产 ID）。
> 记录类列取值：具体记录/事件名（过去式）/ `NOT PRODUCED` / `NOT APPLICABLE` / `DEFERRED TO RFC-00x` / `CANDIDATE EVENT NAME — NOT ACCEPTED` / `PENDING OWNER DECISION` / `NONE CURRENTLY EVIDENCED`。
>
> **事件生产纪律（Review Remediation）**：Domain Event / Application Event 的具体事件名与「某业务发生必产生某事件」的映射，若无精确 Accepted 来源，一律标 `CANDIDATE EVENT NAME — NOT ACCEPTED` / `PENDING OWNER DECISION` / `NOT REQUIRED BY RFC-002`，不得标为 Accepted Decision。`Persistence Required` 必须指明具体哪一种 Record Class 必持久化；Domain Event 默认不因业务提交存在而自动视为持久化（DQ-10）。

### Table A — Business Occurrence & Record-type Mapping

| Row ID | Business Occurrence | Domain Event | Audit Record | State Transition Record | Application Event | Integration Event | Observability Event |
|---|---|---|---|---|---|---|---|
| REC-001 | Strategy Approved（Human Review submit 成功） | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：StrategyApproved；Domain Event 默认不自动持久化） | YES（submit 问责，append-only） | strategy DRAFT→APPROVED（显式类型 Audit） | PENDING OWNER DECISION（可选 post-commit Application Event；LOCAL/BEST-EFFORT/NON-DURABLE） | NONE CURRENTLY EVIDENCED（Outbox 记录类见 REC-013） | DEFERRED TO RFC-007（runtime telemetry；非业务权威） |
| REC-002 | Facts Version Committed | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：FactsExtracted） | YES | facts stage valid | PENDING OWNER DECISION（可选 post-commit；NON-DURABLE） | NONE CURRENTLY EVIDENCED（见 REC-013） | DEFERRED TO RFC-007 |
| REC-003 | Insights Version Committed | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：InsightsAnalyzed） | YES | insights stage valid | PENDING OWNER DECISION（可选 post-commit；NON-DURABLE） | NONE CURRENTLY EVIDENCED（见 REC-013） | DEFERRED TO RFC-007 |
| REC-004 | Positioning Candidates Generated | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：PositioningCandidatesGenerated） | YES | positioning stage valid | PENDING OWNER DECISION（可选 post-commit；NON-DURABLE） | NONE CURRENTLY EVIDENCED（见 REC-013） | DEFERRED TO RFC-007 |
| REC-005 | Marketing Brief Generated | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：BriefGenerated） | YES | brief stage valid | PENDING OWNER DECISION（可选 post-commit；NON-DURABLE） | NONE CURRENTLY EVIDENCED（见 REC-013） | DEFERRED TO RFC-007 |
| REC-006 | Execution Brief Generated（Xiaohongshu Mapping） | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：ExecutionBriefGenerated） | YES | execution-brief stage valid | PENDING OWNER DECISION（可选 post-commit；NON-DURABLE） | NONE CURRENTLY EVIDENCED（见 REC-013） | DEFERRED TO RFC-007 |
| REC-007 | Source Invalidated（来源失效） | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：SourceInvalidated） | YES | source available→invalid | PENDING OWNER DECISION（下游失效经 Orchestration，非 Event Choreography） | NONE CURRENTLY EVIDENCED（见 REC-013） | DEFERRED TO RFC-007 |
| REC-008 | Review Package Created（审核请求） | CANDIDATE EVENT NAME — NOT ACCEPTED（候选：ReviewRequested） | YES | review created / awaiting | PENDING OWNER DECISION（可选 post-commit；NON-DURABLE） | NONE CURRENTLY EVIDENCED（见 REC-013） | DEFERRED TO RFC-007 |
| REC-009 | Durable Work Intent Recorded（可靠工作意图） | NOT PRODUCED（Intent 非 Domain Event） | YES（意图持久化问责） | NOT APPLICABLE | NOT APPLICABLE | NOT PRODUCED（Durable Work Intent ≠ Integration Event） | DEFERRED TO RFC-007 |
| REC-010 | Provider Call Completed | NOT PRODUCED | 可选（调用问责） | NOT APPLICABLE | NOT APPLICABLE | NOT PRODUCED（结果落 Provider Call Ledger） | DEFERRED TO RFC-007 |
| REC-011 | Workflow Checkpoint Written | NOT PRODUCED | NOT PRODUCED（Checkpoint ≠ Audit） | NOT APPLICABLE | NOT APPLICABLE | NOT PRODUCED | DEFERRED TO RFC-007（runtime recovery metadata） |
| REC-012 | Execution Observation（运行观测记录类） | NOT PRODUCED | NOT PRODUCED（Observability ≠ Audit） | NOT APPLICABLE | NOT APPLICABLE | NOT PRODUCED | 记录类本身（Observability Event；非业务权威；捕获范围归 RFC-007） |
| REC-013 | Integration Event Recorded in Outbox（记录类，非特定当前业务发生） | NOT APPLICABLE | 可选（Outbox 写入问责） | NOT APPLICABLE | NOT APPLICABLE | 记录类本身（Integration Event Outbox；Delivery = AT-LEAST-ONCE，不承诺 exactly-once） | DEFERRED TO RFC-007 |

### Table B — Ownership & Persistence

| Row ID | Owning Module | Persistence Required | Transaction Boundary | Delivery Guarantee | Idempotency Identity |
|---|---|---|---|---|---|
| REC-001 | Human Review / Strategy capability | Business Version（Approved Strategy Version）+ Audit + State Transition = 必持久化；Domain Event = 不自动持久化；Application Event = NON-DURABLE | 同一 DEC-035 Atomic Business Commit | Audit：NOT APPLICABLE（同事务）；App Event：BEST-EFFORT（若启用） | command_id + idempotency key（DQ-08） |
| REC-002 | Facts capability | Business Version（Facts Version）+ Audit = 必持久化；Domain Event = 不自动持久化 | 同一 Atomic Business Commit | Audit：NOT APPLICABLE；App Event：BEST-EFFORT（若启用） | command_id + input fingerprint |
| REC-003 | Insights capability | Business Version（Insights Version）+ Audit = 必持久化；Domain Event = 不自动持久化 | 同一 Atomic Business Commit | 同上 | command_id + input fingerprint |
| REC-004 | Positioning capability | Business Version（Positioning Candidate Version）+ Audit = 必持久化；Domain Event = 不自动持久化 | 同一 Atomic Business Commit | 同上 | command_id + input fingerprint |
| REC-005 | Brief capability | Business Version（Marketing Brief Version）+ Audit = 必持久化；Domain Event = 不自动持久化 | 同一 Atomic Business Commit | 同上 | command_id + input fingerprint |
| REC-006 | Adapter capability | Business Version（Execution Brief Version）+ Audit = 必持久化；Domain Event = 不自动持久化 | 同一 Atomic Business Commit | 同上 | command_id + input fingerprint |
| REC-007 | Source / Evidence capability | Source Version 状态 + Audit = 必持久化；Domain Event = 不自动持久化 | 同一 Atomic Business Commit | 同上 | command_id + source_version identity |
| REC-008 | Review capability | Review Package Version + Audit = 必持久化；Domain Event = 不自动持久化 | 同一 Atomic Business Commit（创建与 Interrupt 分离） | 同上 | review_id + package_version |
| REC-009 | Integration/Dispatch Capability | Durable Work Intent + Audit = 必持久化（与业务同事务写入 Intent） | 同一 Atomic Business Commit | Intent Claim：AT-LEAST-ONCE（不承诺 exactly-once） | dispatch_id（Retry 稳定）+ delivery_attempt_id（每次新建） |
| REC-010 | Provider/Integration 模块 | Provider Call Ledger = 必持久化 | 与业务结果同事务或按 DQ-08 Provider Ledger 规则 | NOT APPLICABLE（账本非投递） | provider call identity（Retry 复用，DQ-08） |
| REC-011 | Workflow Runtime（RFC-003 平面） | Checkpoint = 必持久化（隔离平面） | 非业务 Atomic Commit（Checkpoint Write ≠ Business Commit） | NOT APPLICABLE | thread_id + checkpoint_id（不作业务幂等键） |
| REC-012 | Observability（RFC-007） | OPTIONAL（可采样/删除；非权威） | 不在业务事务内 | BEST-EFFORT | trace_id / span_id |
| REC-013 | Integration Event Capability（唯一） | Integration Event Outbox Record = 若启用，与产生事实的业务状态同一 Atomic Commit 持久化 | 与业务事实 + Audit 同一 PostgreSQL Atomic Business Commit | Delivery = AT-LEAST-ONCE（不承诺 exactly-once） | source + event_id；Consumer 依 Event Identity + Consumer Scope 去重 |

### Table C — Schema, Retention, Security & Traceability

| Row ID | Schema Version | Retention Owner | Security Classification | Related DQ / DEC / RFC | Source / Traceability | Decision Status |
|---|---|---|---|---|---|---|
| REC-001 | PENDING OWNER DECISION | Strategy/Review capability（DQ-15） | 引用 ARP-10（SEC-004/SEC-005；含 USER_CONTENT） | DQ-10 · DQ-11 · DEC-029 · DQ-17 | rfc-002-decision-questions.md §DQ-10 · data-architecture.md §DEC-029 | Record Class Semantics = ACCEPTED DECISION；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema 值 = PENDING |
| REC-002 | PENDING OWNER DECISION | Facts capability（DQ-15） | 引用 ARP-10（SEC-004） | DQ-10 · DEC-026 · DQ-17 | rfc-002-decision-questions.md §DQ-10 | Record Class Semantics = ACCEPTED；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema = PENDING |
| REC-003 | PENDING OWNER DECISION | Insights capability（DQ-15） | 引用 ARP-10（SEC-004；含 USER_CONTENT） | DQ-10 · DEC-027 · DQ-17 | rfc-002-decision-questions.md §DQ-10 | Record Class Semantics = ACCEPTED；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema = PENDING |
| REC-004 | PENDING OWNER DECISION | Positioning capability（DQ-15） | 引用 ARP-10（SEC-004） | DQ-10 · DEC-028 · DQ-17 | rfc-002-decision-questions.md §DQ-10 | Record Class Semantics = ACCEPTED；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema = PENDING |
| REC-005 | PENDING OWNER DECISION | Brief capability（DQ-15） | 引用 ARP-10（SEC-004；含 MODEL_CONTENT） | DQ-10 · DEC-030 · DQ-17 | rfc-002-decision-questions.md §DQ-10 | Record Class Semantics = ACCEPTED；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema = PENDING |
| REC-006 | PENDING OWNER DECISION | Adapter capability（DQ-15） | 引用 ARP-10（SEC-004） | DQ-10 · DEC-031 · DQ-17 | rfc-002-decision-questions.md §DQ-10 | Record Class Semantics = ACCEPTED；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema = PENDING |
| REC-007 | PENDING OWNER DECISION | Source/Evidence capability（DQ-15） | 引用 ARP-10（SEC-009/SEC-011） | DQ-10 · DQ-12 · DEC-025 · DQ-17 | rfc-002-decision-questions.md §DQ-10/12 | Record Class Semantics = ACCEPTED；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema = PENDING |
| REC-008 | PENDING OWNER DECISION | Review capability（DQ-15） | 引用 ARP-10（SEC-004/SEC-005） | DQ-10 · DEC-029 · DQ-17 | rfc-002-decision-questions.md §DQ-10 · data-architecture.md §DEC-029 | Record Class Semantics = ACCEPTED；事件产生映射 = CANDIDATE — NOT ACCEPTED；Schema = PENDING |
| REC-009 | PENDING OWNER DECISION | Integration/Dispatch Capability（DQ-15） | 引用 ARP-10（SEC-007；可含 PROVIDER_PAYLOAD） | DQ-09 · DQ-10 · DQ-17 | rfc-002-decision-questions.md §DQ-09 | Record Class Semantics = ACCEPTED；Schema = PENDING；Relay = DEFERRED TO RFC-003 |
| REC-010 | PENDING OWNER DECISION | Provider/Integration 模块（DQ-15） | 引用 ARP-10（SEC-009；PROVIDER_PAYLOAD） | DQ-08 · DQ-10 · DQ-17 | rfc-002-decision-questions.md §DQ-08 | Record Class Semantics = ACCEPTED；Schema = PENDING |
| REC-011 | PENDING OWNER DECISION（checkpoint_schema_version） | Workflow Runtime（DQ-15/DQ-13） | 引用 ARP-10（SEC-010；MODEL_CONTENT 最小化） | DQ-13 · DQ-10 · DQ-17 · RFC-003 | rfc-002-decision-questions.md §DQ-13 | Record Class Semantics = ACCEPTED；Checkpoint ≠ Current Truth；Runtime 配置 = DEFERRED TO RFC-003 |
| REC-012 | PENDING OWNER DECISION | Observability（DQ-15/RFC-007） | 引用 ARP-10（SEC-015；可含 PII，须 Redaction） | DQ-10 · DQ-17 · RFC-007 | rfc-002-decision-questions.md §DQ-10 | Record Class Semantics = ACCEPTED；非业务权威；日志 Redaction = DEFERRED TO RFC-007 |
| REC-013 | PENDING OWNER DECISION（event_schema_version） | Integration Event Capability（DQ-15） | 引用 ARP-10（SEC-008；Outbox 平面） | DQ-10 · DQ-08 · DQ-17 · RFC-003 | rfc-002-decision-questions.md §DQ-10 | Record Class Semantics = ACCEPTED；Current Business Occurrence Mapping = PENDING OWNER DECISION / NONE CURRENTLY EVIDENCED；Relay / Broker / Publication Runtime = DEFERRED TO RFC-003 |

---

## 9. Cross-artifact References

| 本 Artifact 元素 | 引用目标 | 关系 |
|---|---|---|
| REC-001~REC-008 | ARP-01 INV-xxx | Business Occurrence 来源于相应 Aggregate / Business Object（REC-002→INV-002 Facts · REC-003→INV-003 Insights · REC-004→INV-004 Positioning · REC-001/REC-005→INV-005/INV-007 · REC-006→INV-008 Execution Brief · REC-007→INV-009 Source · REC-008→INV-006 Review Package）。 |
| REC-001~REC-013 Security Classification | ARP-10 SEC-xxx + 第 6 节词汇 | Security Classification 引用 ARP-10。 |
| REC-009 | ARP-03 IDEM-008~IDEM-010 | Durable Work Intent 的幂等身份见 ARP-03。 |
| REC-010 | ARP-03 IDEM-013 | Provider Call Identity 见 ARP-03。 |
| REC-013（Integration Event / Outbox） | ARP-03 IDEM-011（Consumer Dedup）/ IDEM-012（Integration Event Identity）/ IDEM-015（Integration Event Publish / Delivery Attempt） · ARP-02 CONC-013（Duplicate Delivery / Consumer Dedup）/ CONC-028（Relay Crash Recovery）/ CONC-029（Stale Publish Attempt Rejection） | Integration Event Identity / Consumer Dedup / Duplicate Delivery 的正确引用目标；**不使用 Durable Work Intent 的 `dispatch_id` / `delivery_attempt_id` 作为 Integration Event 默认 Identity**。 |
| REC-001~REC-013 | ARP-02 CONC-xxx | 并发场景（重复投递/Consumer Dedup）见 ARP-02 TS-01 Slice。 |

---

## 10. Review Checklist（Artifact-specific）

- [x] 每一行描述一个 Repository 中已有依据的 Business Occurrence 或 Record Class。
- [x] Domain Event / Application Event 的具体事件名与产生映射若无精确 Accepted 来源，标 `CANDIDATE EVENT NAME — NOT ACCEPTED` / `PENDING OWNER DECISION` / `NOT REQUIRED BY RFC-002`，未标为 Accepted Decision。
- [x] `Persistence Required` 指明具体哪一种 Record Class 必持久化；Domain Event 默认不自动持久化。
- [x] 明确与 Atomic Business Commit 的关系（Transaction Boundary）。
- [x] 明确是否需要 Delivery 及其 Guarantee。
- [x] 未承诺 Exactly-once（Integration Event = AT-LEAST-ONCE）。
- [x] Durable Work Intent（REC-009）未分类为 Integration Event。
- [x] Audit 未充当通用 Event Bus。
- [x] Observability Event（REC-012）未成为业务权威记录。
- [x] Workflow Checkpoint（REC-011）未成为 Business Current Truth。
- [x] Integration Event / Outbox 记录类（REC-013）区分 Record Class Semantics（ACCEPTED）/ Current Mapping（PENDING / NONE EVIDENCED）/ Relay（DEFERRED TO RFC-003）；未发明当前 MVP 必须发布的具体 Integration Event。
- [x] Schema Version 具体值未知处使用 `PENDING OWNER DECISION`，未虚构。
- [x] Retention Period 未填写。
- [x] 16 正式列 + Source/Traceability + Decision Status 全部出现于 Table A–C（见第 7 节 Column Index）。

---

## 11. Open Questions

| # | 问题 | 决定所有者 | 下一 Gate |
|---|---|---|---|
| OQ-1 | 各记录类的 event_schema_version / payload_schema_version 具体值 | 相应 Capability Owner + 用户 | ARP-04 Acceptance 前 |
| OQ-2 | 哪些流程未来确需 Integration Event（跨边界可靠通知） | 用户 + Integration Owner | RFC-003 Gate |
| OQ-3 | Event Relay / Broker / Polling / Dead-letter / 发布状态机 | 用户 | DEFERRED TO RFC-003 |
| OQ-4 | 各记录类 Retention Period | 用户（DQ-15 拥有） | DQ-15 Retention Policy Table Gate |

---

## 12. Explicit Non-decisions

- 本 Artifact 不创建 Audit Schema、Event Schema 或 Event Registry。
- 本 Artifact 不选择 Event Relay / Broker / 发布状态机 / Dead-letter（留 RFC-003）。
- 本 Artifact 不填写 Retention Period 数值。
- 本 Artifact 不承诺 Exactly-once Delivery。
- 本 Artifact 不自我接受；用户已于 2026-08-06 作出外部接受决定，且只接受文件声明的 Wave 1 Full Vocabulary / Foundation 范围。
- 本 Artifact 不授权 Technical Spike Planning / Execution 或任何实现。
