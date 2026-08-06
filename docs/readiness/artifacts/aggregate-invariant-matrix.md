# ARP-01 — Aggregate / Invariant Matrix

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
| Artifact ID | ARP-01 |
| Exact Name | Aggregate / Invariant Matrix |
| Purpose | 枚举 Repository 文档中已有权威来源的 Aggregate / Business Object / Current Truth 类型，给出其业务不变量、所有模块、提交协议映射与 DQ-04/DQ-11 版本化/Current Truth/失效/恢复语义，作为持久化实施前的必备产出。 |
| Scope | WAVE 1 FULL VOCABULARY / FOUNDATION ARTIFACT |
| Source / Traceability | RFC-002-DQ-03 §7（Aggregate / Invariant Matrix = REQUIRED BEFORE PERSISTENCE IMPLEMENTATION）；RFC-002-DQ-11 §3.16（Matrix 扩展 14 列） |
| Decision Status | ACCEPTED — USER DECISION 2026-08-06 |

---

## 2. Owning DQ / DEC / RFC

| 项 | 值 | Source / Traceability |
|---|---|---|
| Primary Owning DQ | RFC-002-DQ-03（Aggregate / Persistence Boundary） | rfc-002-decision-questions.md §DQ-03 |
| Versioning Owning DQ | RFC-002-DQ-04（Domain State Versioning）· DQ-11（Snapshot vs History） | rfc-002-decision-questions.md |
| Transaction Owning DQ | RFC-002-DQ-05（Transaction Boundary）· DQ-06（Unit of Work） | rfc-002-decision-questions.md |
| Related DQ | DQ-09（Durable Dispatch 参与原子提交） | rfc-002-decision-questions.md |
| Related DEC | DEC-035 Atomic Business Commit（参与者定义见 architecture-baseline-v1 原子提交契约）· DEC-024 / DEC-025 / DEC-026~031 / DEC-012 / DEC-013 | docs/decisions/ · docs/architecture/architecture-baseline-v1.md |
| Related RFC | RFC-001（Module / Layer / Transaction Ownership） | rfc-001-repository-and-application-architecture.md |

---

## 3. Authoritative Inputs

| 输入 | 角色 | Source / Traceability |
|---|---|---|
| RFC-002-DQ-03 / DQ-11 Accepted Decision | Matrix 字段结构与版本化/Current Truth 语义 | rfc-002-decision-questions.md |
| DEC-024（版本化领域状态 + Current Truth Pointers + 四标识符） | 版本化 Domain Object 与 Pointer 语义 | docs/architecture/data-architecture.md §DEC-024 |
| DEC-025（Source/SourceVersion/Fragment/EvidenceLink） | 来源与证据对象 | docs/architecture/data-architecture.md §DEC-025 |
| DEC-026~DEC-031（Facts / Insights / Positioning / Review / Brief / Execution Brief 数据职责） | 各业务 Aggregate 字段与不变量 | docs/architecture/data-architecture.md |
| DEC-012 / DEC-013（Stage State / Task-level Persistence） | Task 与 Stage 状态 | docs/architecture/data-architecture.md |
| architecture-baseline-v1 原子提交契约 | Atomic Business Commit 参与者 | docs/architecture/architecture-baseline-v1.md |

---

## 4. Ownership & Review Roles

| 角色 | 值 | 说明 |
|---|---|---|
| Primary Owner Role | Persistence / Domain Architecture Owner | 具体人选 = PENDING USER DECISION。 |
| Contributors | 各业务模块 Domain Owner | 各 Aggregate 的业务不变量由相应模块 Domain Owner 提供。 |
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

> Atomic Business Commit 是提交协议，不是 Aggregate 成员资格判断。本 Matrix 不因某对象参与原子提交而把它归入某 Aggregate。

---

## 6. Column Index（20 正式列映射）

本 Matrix 的 20 个正式列按主题分组呈现于第 7 节 Table A–D；各表共享同一 `INV-xxx` 行 ID 与行序。列映射如下：

| 正式列 | 所在表 |
|---|---|
| Aggregate / Business Object · Business Invariant · Owning Module · Commit Protocol Mapping | Table A |
| Current Truth Owner · Versioned Object · Version Boundary · Version Creation Trigger · Snapshot Granularity · Logical Completeness Rule | Table B |
| Current Truth Selector · Promotion Rule · Invalidation Rule · Restore Rule · Historical Dependency References · Projection Source of Truth | Table C |
| Retention Owner · Related DQ / DEC / RFC · Source / Traceability · Decision Status | Table D |

---

## 7. Matrix

> 行 ID 规则：`INV-001`…（Artifact Traceability ID，非数据库主键 / 生产 ID）。
> 受控未决标记：`PENDING BUSINESS DEFINITION` / `PENDING USER DECISION` / `DEFERRED TO RFC-00x` / `NOT APPLICABLE` / `NOT YET EVIDENCED`。
>
> **状态维度分离（Review Remediation）**：每行 `Decision Status`（Table D）不再用单一 `ACCEPTED DECISION` 同时表达多个维度，而是区分六个维度：`Source Object`（业务对象是否有 Accepted 来源）· `Aggregate Classification`（本 Artifact 的聚合分类）· `Invariant`（业务不变量）· `Version/Lifecycle`（版本/生命周期）· `Owning Module`（所有模块）· `Artifact Row`（本行审查状态）。Artifact Acceptance 只接受本 Matrix 作为后续规划基线，不把仍明确标记为 `PENDING` / `DEFERRED` 的取值改写成已决定。
>
> **Owning Module 未决项约定**：`exact module = PENDING BUSINESS DEFINITION` 意为具体 package 命名与边界未定，属 `NON-BLOCKING FOR WAVE 1 VOCABULARY REVIEW`、`BLOCKING BEFORE IMPLEMENTATION / FULL OWNERSHIP FREEZE`（除非 Accepted RFC 明确要求在本 Gate 决定）。本 Artifact 不声称 Full Foundation Acceptance 需先发明具体 package。

### Table A — Identity, Invariant & Ownership

| Row ID | Aggregate / Business Object | Business Invariant | Owning Module | Commit Protocol Mapping |
|---|---|---|---|---|
| INV-001 | Task（task_id + Stage State + Current Truth Pointers） | task_id 为稳定业务身份，不因 Resume/重跑改变；Stage 有效性显式记录；Task-to-thread Active Cardinality = DEFERRED TO RFC-003（DEC-024 仅有 MVP 约定「一个 task_id → 一个当前活跃 thread_id」，非运行时不变量；线程生命周期归 RFC-003）；thread_id ≠ task_id、≠ business identity、≠ concurrency lock、≠ idempotency key | Task/Workflow State 业务所有者（DEC-013/024）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit（Stage State + Pointer 更新参与） |
| INV-002 | Product Facts（Facts Version） | No Fact without a valid current-product Fragment；raw_value 与 normalized_value 分离并保留 raw_value；marketing_expression 不入 Facts Current Truth | Product Intake & Fact Extraction capability（DEC-026）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit |
| INV-003 | Customer Insights（Insights Version） | 用户原声必须关联真实 Fragment；正式频率须由确定性统计产生（禁 Top-K 外推）；当前商品与竞品用户证据分离 | Customer Insight Analysis capability（DEC-027）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit |
| INV-004 | Positioning Candidates（Positioning Candidate Version） | Positioning 属 Strategic Inference 非 Explicit Fact；Proof Point → Valid Fact → Evidence Link → Fragment → Source Version | Product Positioning capability（DEC-028）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit |
| INV-005 | Approved Strategy（Approved Strategy Version） | 仅 Approved Strategy Version 进入 Marketing Brief；接受 Hypothesis ≠ Hypothesis→Fact；Evidence Limitations 不得删除 | Human Review / Strategy capability（DEC-029）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit（submit 事务原子更新 Pointer） |
| INV-006 | Review Package（Review Package Version） | 固定上游版本输入快照；上游版本变化 → 标 superseded，旧提交被阻止 | Human Review capability（DEC-029）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit（创建与 Interrupt 分离） |
| INV-007 | Marketing Brief（Marketing Brief Version） | Authoritative Input 仅 approved_strategy_version_id；Message/Benefit Hierarchy 与 Proof Point 追溯链成立 | Marketing Brief Generation capability（DEC-030）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit |
| INV-008 | Xiaohongshu Execution Brief（Execution Brief Version） | Authoritative Input 仅 marketing_brief_version_id；limitations_or_fit_boundary 不可删 | Xiaohongshu Brief Mapping Adapter capability（DEC-031）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit |
| INV-009 | Source / Source Version（Raw Information Current Truth） | 业务结果必须引用具体 source_version_id（非 source_id）；source_scope 隔离当前商品/竞品 | Source / Evidence capability（DEC-025）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit（Source Blob 内容寻址 + 短事务 Finalize，DQ-12） |
| INV-010 | Evidence Link（Fragment↔业务结论已验证关系） | Formal Evidence Link 仅在 Skill 输出过 Evidence Validator 后创建；指向不可变 SourceVersion | Source / Evidence capability（DEC-025）；exact module = PENDING BUSINESS DEFINITION | DEC-035 Atomic Business Commit（与业务版本同事务） |
| INV-011 | Audit Record / State Transition Record（append-only history） | append-only 权威问责证据；与对应 Business Current Truth 修改同事务；更正仅追加 | Audit Capability（唯一，DQ-10） | DEC-035 Atomic Business Commit（与业务状态同事务） |

### Table B — Current Truth & Versioning

| Row ID | Current Truth Owner | Versioned Object | Version Boundary | Version Creation Trigger | Snapshot Granularity | Logical Completeness Rule |
|---|---|---|---|---|---|---|
| INV-001 | Task 业务所有者 | Current Truth Pointers + Stage State | Task 级 | Stage 完成 / 失效 / Pointer 更新 | Task 级指针集合 | Pointer 集合逻辑一致；不得由字段为空推断有效性 |
| INV-002 | Facts capability | Facts Version（domain_version_id / version_number） | Facts 层整体 | 首次生成 / 用户修改 / 重跑 / 来源更新 | Facts Version 整体 | 版本逻辑完整、不可变、独立可读（DQ-11） |
| INV-003 | Insights capability | Insights Version | Insights 层整体 | 同上 | Insights Version 整体 | 同上 |
| INV-004 | Positioning capability | Positioning Candidate Version | Positioning 候选集 | 同上（默认 3、允许 2–4 候选） | Candidate 集合整体 | 候选间实质差异 |
| INV-005 | Strategy/Review capability | Approved Strategy Version | 单次 Human Review submit | 用户 submit 通过事务校验 | Approved Strategy 整体 | 承接全部 Positioning Elements + Hypothesis Decisions |
| INV-006 | Review capability | Review Package Version | 单次审核输入快照 | create_review_package | Package 整体 | 固定上游版本；上游变化标 superseded |
| INV-007 | Brief capability | Marketing Brief Version | 单次 Brief 生成/编辑 | 生成 / 用户编辑 | Brief 整体 | Authoritative Input 仅 approved_strategy_version_id |
| INV-008 | Adapter capability | Execution Brief Version | 单次 Execution Brief 生成/编辑 | 生成 / 用户编辑 | Execution Brief 整体 | Authoritative Input 仅 marketing_brief_version_id |
| INV-009 | Source/Evidence capability | Source Version + Document/Record + Fragment | 单来源内容快照 | 来源采集 / 更新 | Source Version 整体 | Raw Information Current Truth = SourceVersion+Document/Record+Fragment（DEC-025） |
| INV-010 | Source/Evidence capability | Evidence Link（关系对象） | 单条已验证关系 | Evidence Validator 通过 | 单关系对象 | 指向不可变 SourceVersion + 适用 Fragment/Selector |
| INV-011 | Audit Capability | Audit / State Transition Record（append-only） | 单条记录 | 每次业务提交/迁移 | 单记录 | append-only；不覆盖 |

### Table C — Selection & Lifecycle

| Row ID | Current Truth Selector | Promotion Rule | Invalidation Rule | Restore Rule | Historical Dependency References | Projection Source of Truth |
|---|---|---|---|---|---|---|
| INV-001 | 显式 Pointer（facts_version_id 等）经 CAS；`MAX(version_number)` 禁止 | 仅成功 Atomic Business Commit 提升 Pointer | Stage 失效显式记录原因/触发者；不删历史 | Business Restore（新前向 Command）≠ Workflow Time Travel | Pointer 引用各版本 ID | 业务数据库为权威；Interaction State 为派生 |
| INV-002 | facts_version_id 经 CAS | 成功 Commit 产生正式版本并提升 | 来源/上游失效 → 标 invalid，不删版本 | Business Restore（新 domain_version_id + restored_from_version_id，非 Rollback） | based_on_version_ids / source_refs | Facts Version 为权威；Projection 派生 |
| INV-003 | insights_version_id 经 CAS | 同上 | 同上 | 同上 | based_on_source_set_version_id | Insights Version 权威 |
| INV-004 | positioning_version_id 经 CAS | 同上 | 同上 | 同上 | based_on_fact_ids / based_on_insight_ids | Positioning Version 权威 |
| INV-005 | approved_strategy_version_id 经 CAS | submit 事务原子更新 Pointer | Withdrawal → 标 withdrawn/superseded，清 Pointer，下游失效 | Business Restore（新前向 Command） | based_on_review_id / based_on_positioning_version_id | Approved Strategy Version 权威 |
| INV-006 | Review Package 固定版本（无 current pointer promotion） | NOT APPLICABLE（快照对象） | 上游变化 → superseded，阻止旧提交 | NOT APPLICABLE（不 Restore 审核快照） | facts/insights/positioning/source_set version_ids | Package 快照本身 |
| INV-007 | brief_version_id 经 CAS | 成功 Commit 提升 | Brief 修改不使上游失效，但使 Xiaohongshu Mapping 失效 | Business Restore | approved_strategy_version_id | Brief Version 权威 |
| INV-008 | execution_brief_version_id 经 CAS | 成功 Commit 提升 | 当前 MVP 最终输出，普通编辑不触发下游失效 | Business Restore | marketing_brief_version_id | Execution Brief Version 权威 |
| INV-009 | Source current_version_id | Source Version Finalize 后更新 | Source Version Status 7 值；invalid/superseded 等 | Business Restore（新 Source Version） | rule_source_version_ids（如 Platform Policy） | Source Version 权威（Raw Information Current Truth） |
| INV-010 | Evidence Link 为关系对象（无 promotion） | Validator 通过后创建 | 来源失效按 Evidence Link 判断受影响对象 | NOT APPLICABLE | fragment_id / target_version_id | 关系对象本身 |
| INV-011 | Audit 无 Current Truth（append-only） | NOT APPLICABLE | 不得删除/覆盖；更正仅追加 | NOT APPLICABLE | before/after revision、causation | Audit Ledger 本身（非 Current Truth） |

### Table D — Ownership & Traceability

| Row ID | Retention Owner | Related DQ / DEC / RFC | Source / Traceability | Decision Status |
|---|---|---|---|---|
| INV-001 | Task 业务模块（DQ-15） | DQ-11 · DEC-013 · DEC-024 · DEC-012 · RFC-001 · RFC-003 | data-architecture.md §DEC-013/024/012 | Source Object = ACCEPTED DECISION（DEC-013/024/012）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE SOURCED（thread cardinality DEFERRED TO RFC-003）；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-002 | Facts capability（DQ-15） | DQ-11 · DEC-026 · DEC-024 · DEC-025 | data-architecture.md §DEC-026 | Source Object = ACCEPTED DECISION（DEC-026）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-003 | Insights capability（DQ-15） | DQ-11 · DEC-027 · DEC-024 · DEC-025 | data-architecture.md §DEC-027 | Source Object = ACCEPTED DECISION（DEC-027）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-004 | Positioning capability（DQ-15） | DQ-11 · DEC-028 · DEC-024 · DEC-025 | data-architecture.md §DEC-028 | Source Object = ACCEPTED DECISION（DEC-028）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-005 | Strategy/Review capability（DQ-15） | DQ-11 · DEC-029 · DEC-024 · DEC-028 | data-architecture.md §DEC-029 | Source Object = ACCEPTED DECISION（DEC-029）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-006 | Review capability（DQ-15） | DQ-11 · DEC-029 | data-architecture.md §DEC-029 | Source Object = ACCEPTED DECISION（DEC-029）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（快照对象，DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-007 | Brief capability（DQ-15） | DQ-11 · DEC-030 · DEC-024 · DEC-029 | data-architecture.md §DEC-030 | Source Object = ACCEPTED DECISION（DEC-030）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-008 | Adapter capability（DQ-15） | DQ-11 · DEC-031 · DEC-024 · DEC-030 | data-architecture.md §DEC-031 | Source Object = ACCEPTED DECISION（DEC-031）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11）；Owning Module = PENDING BUSINESS DEFINITION；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-009 | Source/Evidence capability（DQ-15） | DQ-11 · DQ-12 · DEC-025 | data-architecture.md §DEC-025 · rfc-002-decision-questions.md §DQ-12 | Source Object = ACCEPTED DECISION（DEC-025/DQ-12）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（DQ-11/DQ-12）；Owning Module = SOURCE/EVIDENCE CAPABILITY（具体 package 命名待定）；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-010 | Source/Evidence capability（DQ-15） | DQ-12 · DEC-025 · DEC-032 | data-architecture.md §DEC-025/032 | Source Object = ACCEPTED DECISION（DEC-025/032）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（关系对象）；Owning Module = SOURCE/EVIDENCE CAPABILITY（具体 package 命名待定）；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |
| INV-011 | Audit Capability（DQ-15） | DQ-10 · DQ-11 · DEC-024 | rfc-002-decision-questions.md §DQ-10 | Source Object = ACCEPTED DECISION（DQ-10）；Aggregate Classification = ACCEPTED AS ARP-01 PLANNING BASELINE（append-only 记录类，非 Current Truth）；Invariant = ACCEPTED WHERE EXPLICITLY SOURCED；Version/Lifecycle = ACCEPTED WHERE EXPLICITLY SOURCED（append-only）；Owning Module = AUDIT CAPABILITY（具体 package 命名待定）；Artifact Row = ACCEPTED / OPEN QUESTIONS PRESERVED |

---

## 8. Cross-artifact References

| 本 Artifact 元素 | 引用目标 | 关系 |
|---|---|---|
| INV-001~INV-011 | ARP-02 `Protected Business Invariant` | ARP-02 并发场景的 Protected Invariant 指向本 Artifact INV-xxx。 |
| INV-002~INV-011 | ARP-04 REC-xxx | 业务对象产生的 Record Class 见 ARP-04。 |
| INV-001~INV-011 | ARP-03 IDEM-xxx | 幂等身份 Operation 指向本 Artifact Aggregate 边界。 |
| INV-002~INV-011 | ARP-10 SEC-003 / SEC-004 / SEC-005 / SEC-006 | 业务对象对应敏感数据平面（Current Truth / Immutable Version / Audit / State Transition）。 |

---

## 9. Review Checklist（Artifact-specific）

- [x] 覆盖当前 Repository 中全部有权威来源的候选 Aggregate / Business Object / Current Truth 类型。
- [x] 每行有具体文档依据（Source / Traceability），无无来源推断。
- [x] 不为填满矩阵发明新 Aggregate。
- [x] 未将 Task 或任何顶层对象默认建模为 Mega Aggregate（各 Aggregate 独立列出）。
- [x] Atomic Business Commit 作为提交协议呈现，未作为 Aggregate 成员资格判断。
- [x] 区分 Current Truth / Immutable Version / Audit / Projection。
- [x] Restore Rule 区分 Business Restore 与 Workflow Time Travel。
- [x] 具体 package 名称保留 `PENDING BUSINESS DEFINITION`，不阻塞 Wave 1 Vocabulary Acceptance，但须在 Implementation / Full Ownership Freeze 前确定。Source/Evidence 与 Audit 的唯一能力所有权分别由 DQ-12 与 DQ-10 已接受决定支撑。
- [x] 无物理 Schema（无表名/列名/DDL）。
- [x] 20 正式列全部出现于 Table A–D（见第 6 节 Column Index）。

---

## 10. Open Questions

| # | 问题 | 决定所有者 | 下一 Gate |
|---|---|---|---|
| OQ-1 | 各 Aggregate 的正式 Owning Module package 命名与边界 | 用户 + Persistence/Domain Owner | `PENDING BUSINESS DEFINITION`：NON-BLOCKING FOR WAVE 1 VOCABULARY REVIEW；BLOCKING BEFORE IMPLEMENTATION / FULL OWNERSHIP FREEZE（RFC-001 DQ-03 已定模块原则，具体模块实例化未授权） |
| OQ-2 | Source / Evidence 是否作为独立模块或跨模块能力 | 用户 + Source/Evidence Owner | RESOLVED：按 RFC-002-DQ-12，Source/Evidence Capability 是相关持久化资产的唯一所有者；具体 package 命名仍归 OQ-1。 |
| OQ-3 | Audit Capability 的唯一所有者模块实例化 | 用户 + Audit Owner | RESOLVED：按 RFC-002-DQ-10，Audit Ledger 由明确且唯一的 Audit Capability 所有；具体 package 命名仍归 OQ-1。 |
| OQ-4 | 各 Aggregate Retention Period 数值 | 用户（DQ-15 拥有） | DQ-15 Retention Policy Table Gate |

---

## 11. Explicit Non-decisions

- 本 Artifact 不定义任何物理 Schema、表名、列名、ORM Model、Migration Revision。
- 本 Artifact 不发明 Repository 文档中不存在的 Aggregate。
- 本 Artifact 不由 `revision` / `expected_revision` / `domain_version_id` / `version_number` 等 RFC-002 已命名字段推导物理数据库设计。
- 本 Artifact 不自我接受；用户已于 2026-08-06 作出外部接受决定，且只接受文件声明的 Wave 1 Full Vocabulary / Foundation 范围。
- 本 Artifact 不授权 Technical Spike Planning / Execution 或任何实现。
