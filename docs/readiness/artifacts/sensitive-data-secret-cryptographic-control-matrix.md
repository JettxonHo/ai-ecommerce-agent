# ARP-10 — Sensitive Data, Secret & Cryptographic Control Matrix

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

> 本文件由 Wave 1 Readiness Artifact Creation Authorization（Level 2）创建。用户于 2026-08-06 明确接受本 Artifact 的 Wave 1 Full Vocabulary / Foundation 范围。`Artifact Creation ≠ Artifact Acceptance`，`Artifact Acceptance ≠ Spike Authorization`。

---

## 1. Artifact Identity

| 项 | 值 |
|---|---|
| Artifact ID | ARP-10 |
| Exact Name | Sensitive Data, Secret & Cryptographic Control Matrix |
| Purpose | 建立跨全部持久化平面的敏感数据分类与密码学控制词汇，对每个已有数据平面 / 记录类给出分类与允许/禁止的持久化传播边界，并承载 Cross-cutting Persistence Security Qualification Catalog（QL-02）的规划分配（仅规划，不执行）。 |
| Scope | WAVE 1 FULL VOCABULARY / FOUNDATION ARTIFACT |
| Source / Traceability | RFC-002-DQ-17 §3.23（Matrix = REQUIRED / NOT AUTHORIZED，26 项字段）；RFC-002-DQ-17 §3.24（Cross-cutting Persistence Security Qualification = REQUIRED IN FIRST AUTHORIZED PERSISTENCE SPIKES / NOT AUTHORIZED） |
| Decision Status | ACCEPTED — USER DECISION 2026-08-06 |

---

## 2. Owning DQ / DEC / RFC

| 项 | 值 | Source / Traceability |
|---|---|---|
| Primary Owning DQ | RFC-002-DQ-17（Security & Sensitive Data Boundary） | rfc-002-decision-questions.md §DQ-17 |
| Contributing DQ | RFC-002-DQ-12（Source & Evidence）· DQ-13（Checkpoint）· DQ-15（Retention & Deletion）· DQ-16（Testing） | rfc-002-decision-questions.md |
| Related DEC | DEC-033（Sensitive Data Boundary）· DEC-035（Checkpoint 严格反序列化） | docs/decisions/ |
| Downstream RFC Boundary | RFC-003（Checkpoint Runtime 配置）· RFC-004（API 认证授权传输）· RFC-005（Retrieval/Index）· RFC-006（LLM Secret 注入）· RFC-007（日志 Redaction / 安全监控） | rfc-002-analysis-cross-rfc-boundary.md |

---

## 3. Authoritative Inputs

| 输入 | 角色 | Source / Traceability |
|---|---|---|
| RFC-002-DQ-17 Accepted Decision | 26 列字段定义 + 分类模型 + 三层加密责任 + Least Privilege + Redaction 顺序 + QL-02 最低安全验证清单 | rfc-002-decision-questions.md §DQ-17 |
| RFC-002-DQ-12 Accepted Decision | Source/Evidence 存储分类、Content Hash ≠ 匿名化、跨安全域去重边界 | rfc-002-decision-questions.md §DQ-12 |
| RFC-002-DQ-13 Accepted Decision | Checkpoint Payload 最小化、Serializer Allowlist、Role/Pool 隔离 | rfc-002-decision-questions.md §DQ-13 |
| RFC-002-DQ-15 Accepted Decision | Retention / Hold / Deletion / Backup Expiry / Deletion Proof 不含敏感载荷 | rfc-002-decision-questions.md §DQ-15 |
| RFC-002-DQ-16 Accepted Decision | 合成测试数据、失败日志 Redaction、Fixture 规则由已接受 DQ-17 治理 | rfc-002-decision-questions.md §DQ-16 |
| RFC-001-DQ-06 | Secret Boundary（Configuration / Bootstrap） | rfc-001-repository-and-application-architecture.md |

---

## 4. Ownership & Review Roles

| 角色 | 值 | 说明 |
|---|---|---|
| Primary Owner Role | Security Governance Owner | 三层所有权中的 Security Governance 层（DQ-17）。具体人选 = PENDING USER DECISION。 |
| Contributors | 各业务模块 Data Owner · Infrastructure Owner | 业务模块为自身数据唯一所有者（DQ-15/DQ-02）；Infrastructure 负责传输/静态加密基线。 |
| Reviewers | 用户（Product Decision Owner） | Artifact Acceptance 仅由用户决定。 |

---

## 5. Authorization Boundary

```text
Artifact Creation Authorization =
AUTHORIZED（本文件创建属 Level 2）

Artifact Acceptance =
ACCEPTED — USER DECISION 2026-08-06

QL-02 Catalog =
ACCEPTED AS PLANNING CATALOG / NOT EXECUTED

QL-02 Execution =
NOT PERFORMED / NOT AUTHORIZED

All QL-02 Items in TS-01 =
NOT REQUIRED

Independent QL-02 Spike =
NOT REQUIRED / NOT AUTHORIZED

Selective Field Encryption & Key Rotation Spike =
CONDITIONALLY REQUIRED / NOT AUTHORIZED

Technical Spike Planning / Execution =
NOT AUTHORIZED

Implementation =
NOT AUTHORIZED
```

---

## 6. Classification Vocabulary（受控词汇，必须首先建立）

### 6.1 四类语义独立（不得混用）

```text
SECRET
≠
PII
≠
SENSITIVE BUSINESS DATA
≠
PUBLIC / INTERNAL DATA
```

| 类别 | 定义（源自 DQ-17） | 持久化总则 |
|---|---|---|
| SECRET | 能力凭证（API Key / Token / 密码 / 私钥等）。独立禁止持久化特殊类别。 | Secret Value 禁止进入任何持久化或派生存储；仅允许无明文能力引用（`credential_ref` / `secret_reference_id`）。 |
| PII | 可识别个人身份的数据。Handling Tag = `PII`。 | 受分类传播与 Redaction / 选择性加密约束；PII protection principles are governed by accepted DQ-17（Retention/Deletion 由 DQ-15 拥有）；per-data-element PII classification remains PENDING OWNER DECISION。 |
| SENSITIVE BUSINESS DATA | 敏感业务数据（如 Provider Payload / Model Content / User Content）。 | 数据最小化多平面传播；按 Protection Profile 决定选择性加密。 |
| PUBLIC / INTERNAL DATA | 公开或内部非敏感数据。 | 常规持久化，仍受访问控制与传输/静态加密基线。 |

> Source / Traceability：RFC-002-DQ-17（SECRET ≠ PII ≠ SENSITIVE BUSINESS DATA ≠ PUBLIC/INTERNAL 语义独立）。Decision Status = ACCEPTED DECISION（DQ-17）。

### 6.2 Confidentiality Level（受控词汇）

```text
PUBLIC
INTERNAL
CONFIDENTIAL
RESTRICTED
```

> Source / Traceability：RFC-002-DQ-17（数据分类 = Confidentiality Level）。Decision Status = ACCEPTED DECISION。具体某 Data Element 的级别赋值见 Table A；未定者标 `PENDING OWNER DECISION`。

### 6.3 Handling Tags（受控词汇）

```text
PII
PROVIDER_PAYLOAD
MODEL_CONTENT
USER_CONTENT
LEGAL_HOLD
SECURITY_INCIDENT
EXPORT_RESTRICTED
AUTH_CREDENTIAL
```

> `SECRET` 为独立禁止持久化特殊类别，不作为 Handling Tag 持久化。Source / Traceability：RFC-002-DQ-17。Decision Status = ACCEPTED DECISION。

### 6.4 Persistence Plane Vocabulary（17 类持久化平面）

本 Matrix 分类的 17 个已有数据平面 / 记录类：Secret Reference、Resolved Secret in Adapter Memory、Business Current Truth、Immutable Business Version、Audit Record、State Transition Record、Durable Work Intent、Integration Event Outbox、Provider Call Ledger、Workflow Checkpoint、Source Blob、Derived Artifact、Evidence Fragment / Evidence Link、Retrieval Index Entry、Application Log / Trace、Backup / PITR Data、Synthetic Test Fixture。

> Source / Traceability：RFC-002-DQ-17（分类规则传播至全部 17 类持久化平面，不得只分类 PostgreSQL Column）；RFC-002-DQ-12/13（Source/Evidence、Checkpoint 平面）。Decision Status = ACCEPTED DECISION（平面集合）；各平面属性见第 8 节。

### 6.5 Two Classification Axes（Review Remediation：不得混用两轴）

本 Matrix 使用两条独立分类轴，不得把一条轴的值当作另一条轴使用：

```text
Security Classification Axis =
SECRET / PII / SENSITIVE BUSINESS DATA / PUBLIC-INTERNAL

Data Nature Axis used by “Secret or Business Data” column =
SECRET REFERENCE
SECRET VALUE
BUSINESS DATA
RUNTIME DATA
DERIVED DATA
OBSERVABILITY DATA
BACKUP COPY
SYNTHETIC TEST DATA
```

- `Security Classification Axis`（第 6.1 节四类）表达数据的敏感类别，由 Confidentiality Level + Handling Tags 细化。
- `Data Nature Axis` 是正式列 `Secret or Business Data` 的取值轴，表达数据平面 / 记录类的性质（引用 / 明文值 / 业务数据 / 运行时 / 派生 / 观测 / 备份 / 合成测试数据），**不是**敏感类别。
- Table A 的 `Secret or Business Data` 列单元格统一规范化为 Data Nature Axis 受控值；原 `Runtime State` / `Derived` / `Observability` / `Synthetic` / `Backup` 等性质归入本轴，不再与四类安全语义混用、不再声称只有四类却在正式列中使用未定义类别。

---

## 7. Column Index（26 正式列 + Source/Traceability + Decision Status 映射）

本 Matrix 的 26 个正式列 + `Source / Traceability` + `Decision Status` 按主题分组呈现于第 8 节 Table A–D；各表共享同一 `SEC-xxx` 行 ID 与行序，合起来构成完整 Matrix。列映射如下：

| 正式列 | 所在表 |
|---|---|
| Data Element · Owning Module · Confidentiality Level · Handling Tags · Purpose · Secret or Business Data | Table A |
| Authoritative Store · Derived Stores · Plaintext Allowed · Graph State Allowed · Checkpoint Allowed · Audit Allowed · Outbox / Work Intent Allowed · Index / Cache Allowed · Object Store Allowed · Backup Allowed | Table B |
| Required Redaction · Transport Encryption · Infrastructure At-rest Encryption · Field-level Encryption · Key Owner / Reference · Authorized Roles | Table C |
| Retention / Erasure · Test Fixture Rule · Incident Response · Related DQ / DEC / RFC | Table D |
| Source / Traceability · Decision Status | Table D |

---

## 8. Matrix

> 行 ID 规则：`SEC-001`…`SEC-017`（Artifact Traceability ID，非数据库主键 / 生产 ID）。
> 受控单元格取值：`PROHIBITED` / `ALLOWED` / `REFERENCE-ONLY` / `CONDITIONAL` / `REQUIRED` / `NOT DECIDED` / `PENDING OWNER DECISION` / `DEFERRED TO RFC-00x` / `REQUIRES SPIKE EVIDENCE` / `NOT APPLICABLE`。

### Table A — Identity & Classification

| Row ID | Data Element | Owning Module | Confidentiality Level | Handling Tags | Purpose | Secret or Business Data（Data Nature Axis） |
|---|---|---|---|---|---|---|
| SEC-001 | Secret Reference（`credential_ref` / `secret_reference_id`） | Security Governance / 相应 Adapter 能力注册 | RESTRICTED | AUTH_CREDENTIAL | 以无明文引用指向 Secret 能力，替代 Secret Value 持久化 | SECRET REFERENCE（无明文能力引用） |
| SEC-002 | Resolved Secret in Adapter Memory | 相应 Provider/Platform Adapter | RESTRICTED | AUTH_CREDENTIAL | 运行时 ephemeral 解析 Secret 供 Adapter 调用；adapter-scoped | SECRET VALUE（ephemeral，禁止持久化） |
| SEC-003 | Business Current Truth | 相应业务模块（Facts / Insights / Positioning / Strategy / Brief / Review 等） | PENDING OWNER DECISION | 按数据类（可含 USER_CONTENT / MODEL_CONTENT） | 权威当前业务状态 | BUSINESS DATA |
| SEC-004 | Immutable Business Version | 相应业务模块 | PENDING OWNER DECISION | 按数据类 | 不可变正式业务版本快照 | BUSINESS DATA |
| SEC-005 | Audit Record | Audit Capability（唯一） | PENDING OWNER DECISION | 按行为元数据 | 权威问责证据（append-only） | BUSINESS DATA（问责元数据） |
| SEC-006 | State Transition Record | Audit Capability（显式类型 Audit） | PENDING OWNER DECISION | 按行为元数据 | 业务状态机迁移审计 | BUSINESS DATA |
| SEC-007 | Durable Work Intent | Integration/Dispatch Capability（RFC-003 前为 DQ-09 语义） | PENDING OWNER DECISION | 可含 PROVIDER_PAYLOAD | 可靠工作调度意图（同业务原子提交） | BUSINESS DATA |
| SEC-008 | Integration Event Outbox | Integration Event Capability（唯一） | PENDING OWNER DECISION | 可含 PROVIDER_PAYLOAD | 跨边界事实可靠发布（at-least-once） | BUSINESS DATA |
| SEC-009 | Provider Call Ledger | 相应 Provider/Integration 模块 | PENDING OWNER DECISION | PROVIDER_PAYLOAD | Provider 调用身份/结果/对账记录（无 Secret Value） | BUSINESS DATA |
| SEC-010 | Workflow Checkpoint | Workflow Runtime（RFC-003 平面） | PENDING OWNER DECISION | MODEL_CONTENT（最小化） | Runtime Recovery State（≠ Current Truth） | RUNTIME DATA（非业务 Secret/Business Data） |
| SEC-011 | Source Blob（Source Version / Content Object） | Source/Evidence 模块（DEC-025） | PENDING OWNER DECISION | USER_CONTENT / PROVIDER_PAYLOAD | 不可变内容寻址原始来源 | BUSINESS DATA（原始内容） |
| SEC-012 | Derived Artifact（Fragment / FragmentSet） | Source/Evidence 模块 | PENDING OWNER DECISION | USER_CONTENT | 解析/规范化/切分派生产物 | DERIVED DATA（Source/Evidence 派生产物） |
| SEC-013 | Evidence Fragment / Evidence Link | Source/Evidence 模块 | PENDING OWNER DECISION | USER_CONTENT | Fragment 与业务结论的已验证关系 | BUSINESS DATA（关系对象） |
| SEC-014 | Retrieval Index Entry | Retrieval/Index（RFC-005） | PENDING OWNER DECISION | USER_CONTENT | 可重建非权威检索索引条目 | DERIVED DATA（非权威） |
| SEC-015 | Application Log / Trace | Observability（RFC-007） | PENDING OWNER DECISION | 可含 PII / PROVIDER_PAYLOAD | 非权威运行观测 | OBSERVABILITY DATA（非业务权威） |
| SEC-016 | Backup / PITR Data | Infrastructure | 继承源数据 | 继承源数据 | 主数据备份 / 时点恢复 | BACKUP COPY（继承源数据 Data Nature） |
| SEC-017 | Synthetic Test Fixture | Test Harness（QL-01） | INTERNAL | 无真实 PII / AUTH_CREDENTIAL | 合成测试数据（禁止真实凭证/PII） | SYNTHETIC TEST DATA（非生产数据） |

### Table B — Persistence-plane Permissions

| Row ID | Authoritative Store | Derived Stores | Plaintext Allowed | Graph State Allowed | Checkpoint Allowed | Audit Allowed | Outbox / Work Intent Allowed | Index / Cache Allowed | Object Store Allowed | Backup Allowed |
|---|---|---|---|---|---|---|---|---|---|---|
| SEC-001 | Secret 能力注册（引用） | NOT APPLICABLE | REFERENCE-ONLY（引用可存，值禁止） | REFERENCE-ONLY | PROHIBITED | REFERENCE-ONLY | REFERENCE-ONLY | PROHIBITED | PROHIBITED | PROHIBITED（值）/ PENDING（引用） |
| SEC-002 | NOT APPLICABLE（ephemeral，不落权威存储） | NOT APPLICABLE | PROHIBITED（持久化） | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED |
| SEC-003 | 业务数据库（PostgreSQL 业务模型） | Query Projection（派生非权威） | ALLOWED（受 Profile 选择性加密） | PROHIBITED（仅版本引用） | PROHIBITED | PROHIBITED（原文，见 SEC-005） | PROHIBITED（原文） | PROHIBITED（原文） | 按 Storage Classification（DQ-12） | ALLOWED（继承策略） |
| SEC-004 | 业务数据库（不可变版本） | NOT APPLICABLE | ALLOWED（受 Profile） | PROHIBITED（仅引用） | PROHIBITED | PROHIBITED（原文） | PROHIBITED（原文） | PROHIBITED（原文） | 按 Storage Classification（DQ-12） | ALLOWED |
| SEC-005 | Audit Ledger（append-only） | NOT APPLICABLE | ALLOWED（不得含 Secret Value / 完整敏感载荷） | PROHIBITED | PROHIBITED | ALLOWED（自身即 Audit） | PROHIBITED | PROHIBITED | NOT DECIDED | ALLOWED（继承） |
| SEC-006 | Audit Ledger（显式类型） | NOT APPLICABLE | ALLOWED（不得含 Secret Value） | PROHIBITED | PROHIBITED | ALLOWED（自身即 Audit） | PROHIBITED | PROHIBITED | NOT DECIDED | ALLOWED（继承） |
| SEC-007 | 业务数据库（与业务同事务） | NOT APPLICABLE | ALLOWED（Payload 数据最小化，DQ-17） | PROHIBITED | PROHIBITED | PROHIBITED（原文） | ALLOWED（自身即 Work Intent） | PROHIBITED | NOT DECIDED | ALLOWED（继承） |
| SEC-008 | Integration Event Outbox | NOT APPLICABLE | ALLOWED（Payload 最小化） | PROHIBITED | PROHIBITED | PROHIBITED（原文） | ALLOWED（自身即 Outbox） | PROHIBITED | NOT DECIDED | ALLOWED（继承） |
| SEC-009 | Provider/Integration 模块账本 | NOT APPLICABLE | ALLOWED（无 Secret Value） | PROHIBITED | PROHIBITED | PROHIBITED（原文） | ALLOWED（调用身份引用） | PROHIBITED | NOT DECIDED | ALLOWED（继承） |
| SEC-010 | Checkpoint 隔离平面（专用 Schema/DB + Role/Pool） | NOT APPLICABLE | ALLOWED（仅最小 Runtime State + Allowlist） | ALLOWED（严格 Msgpack Allowlist） | ALLOWED（自身即 Checkpoint） | PROHIBITED（原文） | PROHIBITED | PROHIBITED | NOT DECIDED | NOT DECIDED（留 DQ-15） |
| SEC-011 | PostgreSQL 权威身份 + 对象存储内容（DQ-12） | Fragment（SEC-012） | ALLOWED（内容按 Storage Classification） | PROHIBITED | PROHIBITED | PROHIBITED（原文） | PROHIBITED（原文） | PROHIBITED（原文） | ALLOWED（不可变内容寻址对象） | ALLOWED |
| SEC-012 | 业务数据库（派生产物） | Retrieval Chunk（非权威） | ALLOWED（按分类） | PROHIBITED | PROHIBITED | PROHIBITED（原文） | PROHIBITED（原文） | PROHIBITED（原文） | 按 Storage Classification | ALLOWED |
| SEC-013 | 业务数据库（关系对象） | NOT APPLICABLE | ALLOWED（引用 + 元数据） | PROHIBITED | PROHIBITED | PROHIBITED（原文） | PROHIBITED（原文） | PROHIBITED（原文） | NOT DECIDED | ALLOWED |
| SEC-014 | Retrieval Index（RFC-005，可重建） | NOT APPLICABLE | ALLOWED（派生） | PROHIBITED | PROHIBITED | PROHIBITED | PROHIBITED | ALLOWED（自身即 Index） | NOT DECIDED | NOT DECIDED |
| SEC-015 | Observability Backend（RFC-007） | NOT APPLICABLE | CONDITIONAL（须 Redaction，DQ-17/RFC-007） | PROHIBITED（原文） | PROHIBITED | PROHIBITED（替代 Audit） | PROHIBITED | PROHIBITED | NOT DECIDED | NOT APPLICABLE |
| SEC-016 | Backup 存储 | NOT APPLICABLE | 继承源数据 | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT DECIDED | ALLOWED（自身即 Backup） |
| SEC-017 | Test Harness 隔离存储 | NOT APPLICABLE | ALLOWED（合成） | NOT APPLICABLE | PROHIBITED（生产 Checkpoint） | PROHIBITED（真实 Audit） | PROHIBITED | PROHIBITED | PROHIBITED（真实对象） | PROHIBITED（生产备份） |

> Table B Source / Traceability：RFC-002-DQ-17（Secret Value 禁止进入任何持久化/派生存储、仅引用；分类传播至 17 平面）；RFC-002-DQ-13（Checkpoint Payload 最小化 + Allowlist）；RFC-002-DQ-12（Source/Evidence 存储分类）；DEC-034（Graph State 紧凑引用，不存完整业务对象）。Decision Status：核心禁止规则 = ACCEPTED DECISION；按平面具体允许性中未决者 = NOT DECIDED / DEFERRED。

### Table C — Protection Controls

| Row ID | Required Redaction | Transport Encryption | Infrastructure At-rest Encryption | Field-level Encryption | Key Owner / Reference | Authorized Roles |
|---|---|---|---|---|---|---|
| SEC-001 | NOT APPLICABLE（无明文值可 Redact） | REQUIRED | REQUIRED BASELINE | NOT APPLICABLE（引用） | Secret 管理能力（KMS/Vault/HSM 未选） | 最小权限 Adapter / Governance |
| SEC-002 | REDACT before Emit/Persist | REQUIRED | NOT APPLICABLE（不落盘） | NOT APPLICABLE | PENDING（KMS/Vault 未选） | 单一 Adapter 进程内 |
| SEC-003 | CLASSIFY→MINIMIZE→REDACT→PERSIST | REQUIRED | REQUIRED BASELINE | CONDITIONAL（by Protection Profile） | PENDING（未选） | 业务 Runtime Role（非 Superuser/Owner/BYPASSRLS） |
| SEC-004 | 同 SEC-003 | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | 业务 Runtime Role |
| SEC-005 | 不记录 Secret Value / 完整敏感 Payload | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Audit Capability Role |
| SEC-006 | 同 SEC-005 | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Audit Capability Role |
| SEC-007 | Payload Redaction（DQ-17） | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Dispatch/Runtime Role |
| SEC-008 | Payload Redaction | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Integration Event Role |
| SEC-009 | 不含 Secret Value | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Provider/Integration Role |
| SEC-010 | 不存 Secret / 完整 PII；Serializer Allowlist | REQUIRED | REQUIRED BASELINE（实际加密范围须钉定版本验证） | CONDITIONAL（Checkpoint 加密 ≠ 允许存 Secret） | PENDING | Checkpoint Role（与 Business 隔离） |
| SEC-011 | 内容按分类 Redaction | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Source/Evidence Role |
| SEC-012 | 同 SEC-011 | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Source/Evidence Role |
| SEC-013 | 引用元数据最小化 | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Source/Evidence Role |
| SEC-014 | 派生索引不含 Secret | REQUIRED | REQUIRED BASELINE | CONDITIONAL | PENDING | Retrieval Role（RFC-005） |
| SEC-015 | Sink Redaction（失败日志 Redaction） | REQUIRED | REQUIRED BASELINE | NOT APPLICABLE（日志层 Redaction 为主） | NOT APPLICABLE | Observability Role（RFC-007） |
| SEC-016 | 继承源数据 Redaction | REQUIRED | REQUIRED BASELINE | 继承源数据 | 继承源数据 | Backup/PITR Role（PURGE/RESTORE 分离） |
| SEC-017 | 无真实敏感载荷（合成） | REQUIRED（测试环境） | NOT DECIDED（测试环境） | NOT APPLICABLE | NOT APPLICABLE | TEST Role（与生产分离） |

> Table C Source / Traceability：RFC-002-DQ-17（三层加密责任：Transport REQUIRED / Infrastructure At-rest REQUIRED BASELINE 但不替代应用控制 / Selective Envelope Encryption 条件启用；UNIVERSAL FIELD-LEVEL ENCRYPTION = REJECTED；Key 与 Ciphertext 分离；Redaction 顺序 CLASSIFY→MINIMIZE→REDACT→SERIALIZE/EMIT/PERSIST；Least Privilege 8 类 Role/Pool 分离）。Decision Status：三层责任与 Least Privilege = ACCEPTED DECISION；`Key Owner / Reference` 具体 KMS/Vault/HSM/算法/Rotation = NOT DECIDED（DQ-17 明确不选择）。

### Table D — Lifecycle, Testing, Traceability

| Row ID | Retention / Erasure | Test Fixture Rule | Incident Response | Related DQ / DEC / RFC | Source / Traceability | Decision Status |
|---|---|---|---|---|---|---|
| SEC-001 | Secret 不长期持久化；REVOKE→ROTATE→INVESTIGATE→REMOVE ONLY WHEN AUTHORIZED | 禁止真实凭证入 Fixture | Secret Detection Failure = Merge Blocker | DQ-17 · RFC-001-DQ-06 · RFC-006 | RFC-002-DQ-17 | ACCEPTED DECISION（原则）；具体期限 = PERIOD NOT DECIDED（DQ-15） |
| SEC-002 | 进程结束即释放（ephemeral） | 受控 Secret Injection（合成） | 泄漏即 REVOKE→ROTATE | DQ-17 · RFC-006 | RFC-002-DQ-17 | ACCEPTED DECISION |
| SEC-003 | 正常生命周期不物理删除；Exceptional Erasure 留 DQ-15/17 | 合成数据 | 访问审计 | DQ-15 · DQ-17 · DQ-11 | RFC-002-DQ-15/17 | ACCEPTED DECISION（原则）；期限 = PERIOD NOT DECIDED |
| SEC-004 | 同 SEC-003（不可变） | 合成数据 | 访问审计 | DQ-15 · DQ-17 · DQ-11 | RFC-002-DQ-15/17 | ACCEPTED DECISION（原则） |
| SEC-005 | append-only；正常不删除；例外受治理 | 合成数据 | 不记录 Secret Value | DQ-15 · DQ-17 · DQ-10 | RFC-002-DQ-15/17 | ACCEPTED DECISION（原则） |
| SEC-006 | 同 SEC-005 | 合成数据 | 同 SEC-005 | DQ-15 · DQ-17 · DQ-10 | RFC-002-DQ-15/17 | ACCEPTED DECISION（原则） |
| SEC-007 | 责任期内不删（Retry/Replay） | 合成数据 | 访问审计 | DQ-15 · DQ-09 | RFC-002-DQ-15 | ACCEPTED DECISION（原则）；期限 = PERIOD NOT DECIDED |
| SEC-008 | Delivery/Replay 责任期内不删 | 合成数据 | 访问审计 | DQ-15 · DQ-10 | RFC-002-DQ-15 | ACCEPTED DECISION（原则） |
| SEC-009 | Provider 对账责任期内不删 | 合成数据（无真实 Token） | 访问审计 | DQ-15 · DQ-08 | RFC-002-DQ-15 | ACCEPTED DECISION（原则） |
| SEC-010 | Whole-thread Lifecycle Deletion（DQ-13/DQ-15） | 禁止生产 Checkpoint 入测试 | Malicious Checkpoint → INCOMPATIBLE/CORRUPT/SECURITY_REJECTED | DQ-13 · DQ-15 · RFC-003 | RFC-002-DQ-13 | ACCEPTED DECISION（原则） |
| SEC-011 | Reference-aware；Orphan Grace 留 DQ-15 | 合成来源 | Integrity Incident（对象缺失/损坏） | DQ-12 · DQ-15 · DQ-17 | RFC-002-DQ-12/15 | ACCEPTED DECISION（原则） |
| SEC-012 | 同 SEC-011 | 合成数据 | 同 SEC-011 | DQ-12 · DQ-15 | RFC-002-DQ-12/15 | ACCEPTED DECISION（原则） |
| SEC-013 | Reference-aware（Evidence Link 引用保护） | 合成数据 | 同 SEC-011 | DQ-12 · DQ-15 · DEC-025 | RFC-002-DQ-12/15 · DEC-025 | ACCEPTED DECISION（原则） |
| SEC-014 | 可重建；索引重建不改 Current Truth | 合成数据 | Index 损坏 → 重建 | DQ-12 · RFC-005 | RFC-002-DQ-12 · RFC-005 Boundary | ACCEPTED DECISION（原则）；RFC-005 = DEFERRED TO RFC-005 |
| SEC-015 | 可按运维策略采样/删除（非权威） | 合成日志 | Secret 不入 Log | DQ-16 · DQ-17 · RFC-007 | RFC-002-DQ-17 · RFC-007 Boundary | ACCEPTED DECISION（原则）；日志 Redaction = DEFERRED TO RFC-007 |
| SEC-016 | Backup Expiry；Restore 重放 Deletion Ledger | 禁止生产 Dump 入测试 | 恢复 Key Version 与 Deletion Ledger | DQ-15 · DQ-17 | RFC-002-DQ-15/17 | ACCEPTED DECISION（原则）；期限 = PERIOD NOT DECIDED |
| SEC-017 | 测试数据生命周期短；不含真实 PII | 仅合成（禁止真实凭证/PII/Checkpoint/Prompt） | Test Credential 最小 Scope/Sandbox/可撤销 | DQ-16 · DQ-17 | RFC-002-DQ-16/17 | ACCEPTED DECISION（原则） |

---

## 9. Cross-cutting Persistence Security Qualification Catalog（QL-02）

### 9.1 模型与状态

```text
QL-02 Catalog =
ACCEPTED AS PLANNING CATALOG / NOT EXECUTED

QL-02 Execution =
NOT PERFORMED / NOT AUTHORIZED

All QL-02 Items in TS-01 =
NOT REQUIRED

Independent QL-02 Spike =
NOT REQUIRED / NOT AUTHORIZED
```

QL-02 为 Cross-cutting Persistence Security Qualification Catalog：将 DQ-17 的最低安全验证项按 Persistence Plane 分配给各 Technical Spike 与 Common Persistence Test Harness Qualification（QL-01），**仅做规划分配，不执行验证**。每个 Spike 仅执行其适用 Slice；TS-01 不要求执行全部 QL-02 项；不设立独立 QL-02 Spike。

> Source / Traceability：RFC-002-DQ-17 §3.24（Cross-cutting Persistence Security Qualification = REQUIRED IN FIRST AUTHORIZED PERSISTENCE SPIKES / NOT AUTHORIZED；17 项最低安全验证）；Accepted Planning Report（QL-02 Model = Cross-cutting Catalog with per-spike applicable slices）。

### 9.2 TS-01 Slice（PostgreSQL Multi-worker Concurrency Spike 适用）

| QL-02 项（TS-01 Slice） | 规划分配对象 | Source / Traceability |
|---|---|---|
| Synthetic Test Data（无真实 PII/凭证） | TS-01 + QL-01 Harness | RFC-002-DQ-16/17 |
| Non-production Credentials（测试凭证最小 Scope/Sandbox/可撤销） | TS-01 + QL-01 Harness | RFC-002-DQ-17 |
| Runtime Role 非 Superuser / Table Owner / BYPASSRLS | TS-01 | RFC-002-DQ-17 |
| Runtime 与 Migration Credential 分离 | TS-01（与 TS-04 边界协同） | RFC-002-DQ-17 |
| Schema / Search Path 安全 | TS-01 | RFC-002-DQ-17 |
| Role Denial（越权访问被拒） | TS-01 | RFC-002-DQ-17 |
| Secret 不进入 Business Record / Audit / Work Intent / Outbox / 测试日志 | TS-01 | RFC-002-DQ-17 |
| Persist / Emit 前 Redaction | TS-01 | RFC-002-DQ-17 |
| QL-01 Evidence 不泄漏 Credential | TS-01 + QL-01 Harness | RFC-002-DQ-16/17 |

### 9.3 TS-02 Slice（External Object Consistency Spike 适用）

| QL-02 项（TS-02 Slice） | 规划分配对象 | Source / Traceability |
|---|---|---|
| Object Key 不包含敏感值 | TS-02 | RFC-002-DQ-17 |
| Content Hash ≠ 匿名化证明（低熵存在性/Dictionary Oracle 风险须限制访问） | TS-02 | RFC-002-DQ-17/DQ-12 |
| Cross-tenant / Cross-security-domain Dedup 被拒 | TS-02 | RFC-002-DQ-17 |
| Object Metadata 最小化 | TS-02 | RFC-002-DQ-17 |
| Orphan Object Access（不泄漏） | TS-02 | RFC-002-DQ-12/17 |
| Sensitive Object 引用与删除安全 | TS-02 | RFC-002-DQ-12/15/17 |

### 9.4 TS-03 Slice（Workflow Checkpoint Isolation Spike 适用）

| QL-02 项（TS-03 Slice） | 规划分配对象 | Source / Traceability |
|---|---|---|
| Strict Msgpack / Explicit Allowlist | TS-03 | RFC-002-DQ-17/DQ-13 |
| Pickle Fallback 禁止 | TS-03 | RFC-002-DQ-17/DQ-13 |
| Secret 不进入 Graph State / Checkpoint | TS-03 | RFC-002-DQ-17 |
| EncryptedSerializer 实际覆盖范围（钉定版本验证） | TS-03 | RFC-002-DQ-17 |
| Checkpoint Role / Pool 隔离 | TS-03 | RFC-002-DQ-13/17 |
| Malicious Checkpoint 不触发任意代码 | TS-03 | RFC-002-DQ-17 |
| Metadata 明文边界 | TS-03 | RFC-002-DQ-13/17 |
| Whole-thread Lifecycle | TS-03 | RFC-002-DQ-13/15 |
| Current-truth-first Reconciliation | TS-03 | RFC-002-DQ-13 |

### 9.5 TS-04 Slice（Schema Migration Rollout Spike 适用）

| QL-02 项（TS-04 Slice） | 规划分配对象 | Source / Traceability |
|---|---|---|
| Migration 与 Runtime Role 分离 | TS-04 | RFC-002-DQ-17/DQ-14 |
| Vendor Schema 排除（Autogenerate 排除 Checkpoint Tables） | TS-04 | RFC-002-DQ-14 |
| Search Path / DDL 权限 | TS-04 | RFC-002-DQ-17 |
| Migration Log Redaction | TS-04 | RFC-002-DQ-17 |
| Credential 不进入 Migration Artifact | TS-04 | RFC-002-DQ-17 |
| Destructive Gate | TS-04 | RFC-002-DQ-14 |
| Forward Repair | TS-04 | RFC-002-DQ-14 |
| Backup / Recovery 权限边界 | TS-04 | RFC-002-DQ-15/17 |

### 9.6 TS-05 Slice（Retention & Deletion Safety Spike 适用）

| QL-02 项（TS-05 Slice） | 规划分配对象 | Source / Traceability |
|---|---|---|
| Deletion Proof 不含敏感 Payload | TS-05 | RFC-002-DQ-15/17 |
| Hold 阻止 Purge | TS-05 | RFC-002-DQ-15 |
| Reference-aware Deletion | TS-05 | RFC-002-DQ-15 |
| Backup Expiry | TS-05 | RFC-002-DQ-15 |
| Restore 后 Deletion Ledger 重放 | TS-05 | RFC-002-DQ-15/17 |
| Key Version Recovery | TS-05 | RFC-002-DQ-17 |
| Purge Credential 隔离 | TS-05 | RFC-002-DQ-17 |
| Cross-plane Completion | TS-05 | RFC-002-DQ-15 |

> QL-02 与 QL-01 关系：Common Persistence Test Harness Qualification（QL-01）作为第一个获授权 Persistence Spike 的组成部分，同样承载上述与 Harness 相关的安全 Slice（合成数据、非生产凭证、证据不泄漏凭证）。QL-01 定义见 ARP-09 TS-01 Minimum Slice。

---

## 10. Cross-artifact References

| 本 Artifact 元素 | 引用目标 | 关系 |
|---|---|---|
| ARP-10 Classification Vocabulary | ARP-04 `Security Classification` 列 | ARP-04 的 Security Classification 引用本 Artifact 第 6 节词汇。 |
| ARP-10 QL-02 Catalog | TS-01 ~ TS-05 · QL-01 | 规划分配（不执行）；各 Slice 指向对应 Spike。 |
| ARP-10 SEC-003 / SEC-004 / SEC-005 / SEC-006 / SEC-007 / SEC-008 | ARP-01 INV-xxx · ARP-04 REC-xxx | 数据平面与 Aggregate / Record Class 对应。 |
| ARP-10 SEC-010（Checkpoint） | ARP-09 TS-01 Slice | Checkpoint 隔离安全在 TS-03 Spike 验证，非 TS-01；此处仅词汇对齐。 |

> 引用完整性规则：所有引用须存在、无循环定义、无术语漂移。行 ID 为 Artifact Traceability ID，非数据库主键。

---

## 11. Review Checklist（Artifact-specific）

- [x] 第 6.1 节四类语义独立（SECRET ≠ PII ≠ SENSITIVE BUSINESS DATA ≠ PUBLIC/INTERNAL）已建立且未混用。
- [x] Confidentiality Level 与 Handling Tags 使用受控词汇。
- [x] 26 正式列 + Source/Traceability + Decision Status 全部出现在 Table A–D（见第 7 节 Column Index）。
- [x] 每个 Data Element 行有 Source / Traceability。
- [x] Secret Value 在全部持久化/派生平面为 PROHIBITED，仅 REFERENCE-ONLY 引用。
- [x] 未选择 KMS / Vault / HSM / 算法 / Rotation Period / Key Hierarchy（相关单元格 = NOT DECIDED / PENDING）。
- [x] 未填写任何 Retention Period（期限 = PERIOD NOT DECIDED，留 DQ-15）。
- [x] QL-02 Catalog 按 TS-01~TS-05 + QL-01 分配，且明确 `QL-02 Execution = NOT PERFORMED / NOT AUTHORIZED`。
- [x] 明确 `All QL-02 Items in TS-01 = NOT REQUIRED` 与 `Independent QL-02 Spike = NOT REQUIRED / NOT AUTHORIZED`。
- [x] Artifact Acceptance 已归档；仍未出现 `COMPLETED` / `READY FOR IMPLEMENTATION` / `READY FOR SPIKE EXECUTION` 等越权状态。

---

## 12. Open Questions

| # | 问题 | 决定所有者 | 下一 Gate |
|---|---|---|---|
| OQ-1 | 各 Data Element 的具体 Confidentiality Level 赋值（当前多为 PENDING OWNER DECISION） | Security Governance Owner + 用户 | ARP-10 Acceptance 前 |
| OQ-2 | Key Owner / Reference 的 KMS / Vault / HSM / 算法 / Rotation Period / Key Hierarchy | 用户 + Infrastructure Owner | Selective Field Encryption & Key Rotation Spike 授权 Gate |
| OQ-3 | 各平面 Retention Period 数值 | 用户（DQ-15 拥有） | DQ-15 Retention Policy Table Gate |
| OQ-4 | Checkpoint 加密的实际范围（须基于钉定 PostgresSaver 版本验证） | 用户 + Workflow Runtime Owner | TS-03 Spike Planning Gate |
| OQ-5 | Object Store 上敏感对象的存储分类与加密 Profile | 用户 + Source/Evidence Owner | TS-02 Spike Planning Gate |

---

## 13. Explicit Non-decisions

- 本 Artifact 不选择任何 KMS / Vault / HSM / Encryption Algorithm / Key Hierarchy / Rotation Period。
- 本 Artifact 不填写任何 Retention Period 数值。
- 本 Artifact 不执行 QL-02 验证（QL-02 Execution = NOT PERFORMED / NOT AUTHORIZED）。
- 本 Artifact 不创建 RLS Policy、Role-Grant、Redaction Middleware、Secret Scanner、Encrypted Column、Key Registry、Rotation Job、测试、DDL、Migration 或基础设施。
- 本 Artifact 不自我接受；用户已于 2026-08-06 作出外部接受决定，且只接受文件声明的 Wave 1 Full Vocabulary / Foundation 范围。
- 本 Artifact 不授权 Technical Spike Planning / Execution 或任何实现。
