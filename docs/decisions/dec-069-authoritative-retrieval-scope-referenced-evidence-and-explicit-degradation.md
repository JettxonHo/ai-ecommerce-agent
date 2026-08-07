# DEC-069：采用权威检索范围、引用式 Evidence Package 与显式降级

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-07
- **Decision Type:** Retrieval Scope / Public Source and Evidence Transport / Evidence Commit / Evaluation and Degradation
- **Source:** Session-003；用户明确接受 `P-64A / P-65A / P-66A`
- **Related Issue:** [#56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56)
- **Related PR:** [#57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)

## Context

DEC-067 已冻结版本化 Source 图、逐资料耐久处理与格式感知 Fragment；DEC-068 已冻结 PostgreSQL-native derived retrieval plane、单一版本化 Embedding Profile、immutable index generation、确定性 Direct-first Planner 与 RRF。仍需闭合三个容易被实现层错误混用的边界：谁决定检索范围、运行时候选怎样成为正式证据，以及检索质量与故障降级怎样验收。

首个 Goal 是本地固定工作区演示，不建设登录、RBAC、多租户或公共分享。这个简化不允许 Browser、Skill 或 Provider 自行扩大 Task / Source 范围，也不允许把 retrieval success、排名或 QC 结果当作业务批准。

## Decision

### 1. Server-derived Scope and Narrow Public Transport

- 固定 Workspace、Task、Product / Competitor identity、Source Scope、`TaskSourceAssociation`、`SourceSetVersion`、精确 `SourceVersion`、availability 与 eligibility 由服务端基于 Accepted Task、Skill Contract 与权威 Source 图推导。Browser、Skill 输入、模型或 Provider payload 不能增加允许范围。
- Direct / Exact / Lexical / Semantic / Hybrid 共用同一个 SQL authorized candidate relation；必要谓词在 ranking 前生效。禁止先广泛召回私有内容再由应用层后过滤。
- `SourceSetVersion` 的 immutable manifest 固定 association identity + revision、精确 Source Version 与当时 eligibility。历史 Retrieval Run / Evidence Package 不在读取时改绑最新版本。
- RFC-005 只填充 RFC-004 已委托的 Source intake / item result、Source summary / version processing、Source / Evidence collection 与 locator-safe detail；DEC-064 已冻结的 remove / replace Preview / Confirm 四个 Operation 保持不变。
- Source / Evidence collection 使用 opaque cursor keyset pagination，按服务端权威时间和稳定 identity 排序；默认 `20`、最大 `50`。Cursor 不是授权凭证，也不承诺 total、offset、任意搜索或无限历史。
- 公共 Source 投影只包含稳定 identity、显示元数据、association / version reference、processing、availability、bounded item issues、locator-safe preview 与 Capability。公共 Evidence 投影只包含 Evidence Link、目标 Domain Version、Fragment / Source Version reference、忠实 excerpt、诚实 Locator、role / class、availability 与 limitation。
- 公共 API 不暴露 vectors、raw index rows、Provider payload、SQL filter、private storage reference，也不把 rank / distance 投影为 confidence。首个 Goal 不新增登录、RBAC、多租户、跨 Task 浏览、公共分享或永久删除 Operation。

### 2. Immutable Retrieval Record and Referenced Evidence Commit

- 每次相关性检索创建 immutable `RetrievalRun`，至少记录 Retrieval Plan / Source Set reference、授权过滤摘要、query identities、组件 / generation references、candidate summary、degraded outcome、权威时间与 correlation reference；它是运行解释记录，不是 Business Current Truth。
- `EvidencePackage` 是 immutable、reference-based Skill 输入：引用 Retrieval Run、Source Set、Candidate Fragment 与可读组件版本，不复制整套私有资料、不 latest-at-read，也不新增 Digest / Hash / SHA-256。
- `DatasetStatistic` 只能由确定性、完整且可计数的 Record 集合产生，并记录 dataset version、population definition、counts、method 与 limitations。Top-K Candidate、overlap Fragment 或 rank 不能推断总体频率、比例或共识。
- Evidence Validator 必须验证 Task / package / scope / version / availability / locator / claim boundary。只有验证通过后，才可在一个业务事务内原子创建 Domain Version、Formal Evidence Link、Current Truth pointer 与 audit；任何一步失败都不得部分提交。
- `FormalEvidenceLink` 使用稳定 identity，绑定 claim target、role / class、精确 Fragment / Source Version 与诚实 Locator。Retrieval rank 只留在运行解释中，不成为 Evidence strength、Fact confidence、QC pass 或 Human approval。
- 公共 API 只提供 Task-scoped Source / Evidence projection。日志、Trace、Metric、Redaction、Retention 和运维阈值仍由 RFC-007 / ARP-08 拥有，不在 RFC-005 建立第二诊断或保留系统。

### 3. Representative Evaluation and Explicit Degradation

- 复用 DEC-058 的虚构“城市通勤双肩包”三个资料变体与一个 mutation，覆盖 exact identifier、CJK lexical、semantic paraphrase、hybrid / counter-evidence、scope isolation、complete review-dataset statistic、zero result、removed / replaced Source、semantic outage 与 incomplete generation。
- 下列是对应生产 Slice 的行为硬门禁：零跨 Task / Scope / Product leakage；零 stale / unavailable / non-current-generation candidate；零 Top-K frequency extrapolation；zero result 不伪造答案；exact identifiers 原样保留；相同 manifest + plan + component tuple 产生稳定 candidate identities / order；Formal Evidence 仅在 Validator + atomic commit 后出现。
- Relevance 使用代表性查询的 Recall@K、reciprocal rank、coverage / counter-evidence 与人工 `PASS / FAIL` 共同判断。K 与通过阈值等 Fixture 内容可见后由 Testing Strategy 冻结；不合成机械总分，也不为得分堆叠低价值 case。
- Semantic 不可用时只运行适用的 Direct / Exact / Lexical 并传播 `semantic_retrieval_unavailable` limitation。Lexical 不可用时 Direct / Exact 保持；Semantic 只有在 authorized candidate relation 与 exact identifier coverage 均成立时才可继续，否则返回 limitation 或 `insufficient_information`。
- incomplete / failed generation 不切换。系统继续使用仍兼容且 eligibility-current 的上一 generation，或仅运行安全适用的 Direct / Exact / Lexical 并显式限制；没有安全 generation 时返回 temporary unavailable / actionable recovery。Fallback 不扩大 Scope、不切换到不安全 generation，也不让 Frontend 模拟终态。
- ANN、Reranker 与 LLM Query Rewrite 只有在固定评测显示当前 exact + deterministic RRF baseline 存在实质 latency / relevance 缺口时才可另行提案，并必须提供 before / after、Scope isolation、rollback 与新增失败行为证据。

## Alternatives Considered

### Client-selected Scope + Broad Retrieval + Application Post-filter

由 Client 选择 Source 范围、先全局召回再后过滤，并暴露 index / score 细节。该方案调试直观，但会让不可信输入扩大范围、让私有内容先越界，并使 rank 看起来像业务可信度，因此不采用。

### Copied Evidence Package as Mutable Business Truth

把候选全文复制到 Evidence Package，并用一个可变 Evidence 对象同时表达 Candidate、统计、正式引用、用户展示和运行日志。该方案 Schema 少，但会复制私有正文、破坏 availability / retention、混淆不同生命周期与事务边界，因此不采用。

### Aggregate Score Gate + Live-only Evaluation + Silent Fallback

把隔离、相关性、延迟、成本和人工评分合成总分，主要用实时 Provider / ad hoc queries 验证，失败时静默切换。该方案报告短，但严重 leakage 可被其他分数抵消，结果不可重复，且会把证据覆盖缺口伪装成正常，因此不采用。

## Reason

该组合将授权范围、候选检索、Skill 输入、正式证据与业务 Current Truth 分成可独立审查的生命周期，并用固定代表性资料验证真实风险。它既阻止跨范围召回和部分 Evidence 提交，又不引入通用权限平台、机械评分或过量防御，符合本地单工作区 MVP 与 DEC-039 的适度校验原则。

## Consequences

- RFC-005 DQ-07～09 已闭合；只剩 DQ-10 的 exact Embedding Profile、公共 Operation / Schema closure、采用顺序、对账证据与最终 Review Gate。
- Source / Evidence API、Retrieval Runtime、Skill、Worker 与 Frontend 必须复用同一 server-derived scope 和公共 projection，不能各自创建平行授权或状态语义。
- Evidence Package 依赖稳定 reference resolution；availability 变化可以阻止新业务使用，但不能静默改写历史 Run / Package 的输入身份。
- 显式降级可能让部分流程暂停或返回资料不足；这是比扩大范围、使用旧 generation 或伪造完整性更诚实的结果。
- 本决定不冻结 exact Embedding model / dimensions、OpenAPI path catalog、package / extension version 或运维阈值；这些仍由 DQ-10、实施兼容证据与 RFC-007 分别闭合。

## Relationships

- **Extends [DEC-068](dec-068-postgresql-native-versioned-and-deterministic-retrieval-baseline.md)：** 把统一 authorized candidate relation、immutable Retrieval Run、Evidence Package、evaluation 与 degraded behavior 具体化。
- **Amends [DEC-032](dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)：** 以 reference-based Evidence Package、RRF 解释边界、固定代表性评测和显式降级替代其较宽泛的运行示例；Direct-first 与 Candidate / Formal Evidence 分离保持有效。
- **Concretizes [DEC-061](dec-061-task-scoped-private-material-and-reversible-removal.md)：** 所有 retrieval channel 在 ranking 前执行同一 Task / association / availability / version 范围。
- **Concretizes [DEC-058](dec-058-fictional-anchor-sku-acceptance-fixture-strategy.md)：** 将三个资料变体与 mutation 用作 Retrieval behavior / relevance 验收基础。
- **Complements [DEC-063](dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md)、[DEC-064](dec-064-task-recovery-and-human-review-public-protocol.md)、[DEC-065](dec-065-immutable-brief-export-problem-and-fixed-workspace-api-boundary.md) 与 [DEC-066](dec-066-openapi-contract-catalog-compatibility-and-generated-client-adoption.md)：** 只填充 RFC-004 已委托的 Source / Evidence refs、collection 与 lifecycle transport，不改变既有 Operation / Problem / workspace authority。
- **Conforms to [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 使用真实 Scope、事务与代表性评测门禁，不新增 Hash / SHA-256、机械总分或泛化安全平台。
- **Input to [RFC-005](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md)：** 接受 DQ-07～09，并开放 DQ-10 的最终闭合提案。

## Authorization Boundary

本决定只授权 Decision、RFC、Current Truth、Readiness、Testing 与 Traceability 文档同步：

- 不接受 RFC-005 整体，不授权合并 PR #57 或关闭 Issue #56；
- 不授权创建 OpenAPI Artifact、Schema、Source / Evidence API、数据库表、Migration、Parser、Embedding、Index、Retrieval Runtime、Fixture、Frontend 或测试实现；
- 不授权依赖 / PostgreSQL extension 安装、Technical Spike、Live Provider 调用、RFC-007、业务实现或长期 Goal；
- 下一 Gate 仅为 RFC-005 DQ-10 的 exact Embedding Profile、公共 Operation / Schema closure、adoption / reconciliation / verification 顺序与 RFC final-review readiness。

## Accepted From

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-64A / P-65A / P-66A；用户于 2026-08-07 明确回复“接受 P-64A、P-65A、P-66A”。
- [RFC-005 Proposal Round 3](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md#proposal-round-3)。
- GitHub：[Issue #56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56) / [Draft PR #57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)。
