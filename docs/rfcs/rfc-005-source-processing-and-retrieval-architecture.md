# RFC-005：Source Processing and Retrieval Architecture

## Metadata

- **Status:** DRAFTING — PROPOSAL ROUND 1；USER DECISIONS PENDING
- **Date:** 2026-08-07
- **Issue:** [#56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56)
- **Pull Request:** [#57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)（Draft）
- **RFC Acceptance:** NOT GRANTED
- **Implementation Authorization:** NOT GRANTED
- **Spike Execution Authorization:** NOT GRANTED
- **Goal Activation:** NOT GRANTED

## Problem

Product Specification、RFC-002、RFC-003、RFC-004、RFC-006 与 Frontend Architecture 已接受，但 Source / Evidence 概念架构仍未形成可供独立实现 Agent 使用的生产契约。当前已知“Source → Source Version → Document / Record → Fragment → Evidence Link”和 Direct-first Hybrid Retrieval 原则，却仍缺少以下闭合项：

- 用户输入如何登记、处理、部分接受、版本化和失效；
- 文本、TXT / Markdown、文本型 PDF 与评论 CSV 如何形成可定位 Fragment；
- 哪些内容进入直接读取、词法检索、语义检索或混合检索；
- PostgreSQL 权威 Source / Evidence 图与可重建 Retrieval Index 如何分工；
- Source Set Version、Task / Product / Competitor Scope 如何在召回前约束候选；
- Candidate Fragment、Retrieval Run、Evidence Package、Dataset Statistic 与 Formal Evidence Link 如何保持职责分离；
- RFC-004 的公共 HTTP Contract 与 RFC-007 的诊断 / 运维边界如何接入而不形成第二事实源。

若这些事项在开发 Issue 内临场决定，将导致 Parser、Retrieval、Skill、API 与 Frontend 各自定义不同的 Source 状态、Fragment 定位、过滤与证据语义，并可能违反已接受的 Task-scoped 私有资料、Evidence Validator、Current Truth 与适度校验边界。

## Context and Authority

### Accepted upstream authority

- [DEC-014](../decisions/dec-014-on-demand-hybrid-rag-and-layered-data-access.md)：按需、Direct-first、Lexical + Semantic 的分层数据访问；
- [DEC-025](../decisions/dec-025-versioned-sources-fragments-and-evidence-links.md)：版本化 Source / Fragment / Evidence Link 概念链；
- [DEC-032](../decisions/dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)：确定性 Planner、强制 Scope / Version 过滤、Candidate Fragment 与 Evidence Package 边界；
- [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md)：适度校验，不新增 Hash / SHA-256 要求；
- [DEC-045](../decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md)：输入格式、默认文件限制、单文件失败不回滚其他文件与冲突分级；
- [DEC-047](../decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：渐进式 Evidence 展示、编辑影响与行动导向恢复；
- [DEC-057](../decisions/dec-057-product-semantics-and-technical-contract-authority-boundary.md)、[DEC-059](../decisions/dec-059-targeted-needs-input-action-request-model.md)、[DEC-060](../decisions/dec-060-evidence-bound-claim-integrity-and-proportional-compliance-boundary.md)、[DEC-061](../decisions/dec-061-task-scoped-private-material-and-reversible-removal.md)：产品 / 技术权威、Needs Input、Claim Integrity 与 Task-scoped Source 生命周期；
- [RFC-002](rfc-002-persistence-and-transaction-architecture.md)：PostgreSQL 权威 Source / Evidence 图、版本化内容 / 派生产物、可重建非权威 Retrieval Index 与 External Object Consistency 边界；
- [RFC-003](rfc-003-langgraph-runtime-and-checkpoint-architecture.md)：Durable Dispatch、Worker ownership、取消、恢复与 Current-Truth-first Reconciliation；
- [RFC-004](rfc-004-api-and-human-review-architecture.md)：唯一 OpenAPI authority、Task-facing Source change、Problem envelope、Run monitor 与 fixed-workspace HTTP 边界；
- [RFC-006](rfc-006-llm-runtime-and-structured-output.md)：单一 Model Runtime Port、确定性测试替身、Provider payload 与 Secret 边界。

### Current official capability evidence

- PostgreSQL 的 [`tsvector` / `tsquery`](https://www.postgresql.org/docs/current/datatype-textsearch.html) 与 [GIN](https://www.postgresql.org/docs/current/textsearch-indexes.html) 为关系库内全文检索提供原生能力；官方文档把 GIN 作为常规全文检索的首选索引类型。该事实只证明能力存在，不自动决定本 RFC 的最终词法配置、语言配置或排名策略。
- [pgvector 官方说明](https://github.com/pgvector/pgvector)提供 PostgreSQL 内 exact nearest-neighbor、HNSW / IVFFlat、metadata filter 配合方式与 Hybrid Search 组合能力，也明确 approximate index 的过滤 / recall 取舍。该事实只支持候选可行性，精确扩展版本、Embedding 维度、距离函数与 ANN 参数必须留给获授权后的兼容证据和 Retrieval Evaluation。

## Goals

- Freeze one Source-processing contract for structured form / text, TXT / Markdown, text PDF and review CSV.
- Preserve stable Source identity, immutable Source Version, mutable Task Source Association revision and versioned Derived Artifact without treating removal as physical deletion.
- Make every formal citation resolvable to an allowed Fragment and honest format-specific Locator.
- Select a production Lexical / Vector topology consistent with the accepted PostgreSQL and local single-workspace MVP boundaries.
- Keep Task / Source Scope / Product / Competitor / Source Set Version filters authoritative and effective before or during retrieval.
- Define reproducible Retrieval Run and Evidence Package inputs without making rank scores, model output or retrieval results into Business Current Truth.
- Provide sufficient API / Worker / Frontend handoffs and proportionate tests for independent implementation Issues.

## Non-goals

- Implementing upload, parsing, PDF extraction, CSV ingestion, Fragmentation, Embedding, Vector Index, Retrieval Runtime, API, Frontend, Database, Migration, Test Fixture or deployment;
- OCR, image understanding, scanned PDFs, DOCX / spreadsheet parsing beyond the accepted review CSV, Web scraping, active online research or platform monitoring;
- cross-task private knowledge reuse, multi-tenant authorization, user-facing permanent deletion or physical purge;
- general document management, enterprise search, arbitrary SQL search, generic compliance, data-loss-prevention or security platforms;
- Multi-Provider Embedding failover, independent vector service, mandatory Reranker or speculative scale-out infrastructure unless later explicitly accepted;
- redefining RFC-004 paths, Problem envelope, Task / Run state or Human Review semantics;
- accepting RFC-005, executing TS-01～TS-05, installing dependencies, or activating the long-running Goal.

## Contract boundary and handoffs

RFC-005 owns:

- Source / Source Version / Task Source Association / Document / Record / Derived Artifact / Fragment / Source Set Version semantics required for processing and retrieval;
- parsing and fragmentation lifecycle, Locator families, per-item processing results and index eligibility;
- Direct / Exact / Lexical / Semantic / Hybrid planning, retrieval component topology, fusion, optional reranking and quality evaluation;
- mandatory retrieval filters, Candidate Fragment / Retrieval Run / Evidence Package / Dataset Statistic transport details;
- Retrieval Index entry lifecycle, rebuild, reindex and Source-Version-to-index consistency behavior;
- Source / Evidence public Schema refs and operations delegated by RFC-004.

RFC-002 remains authority for PostgreSQL transactions, storage classification, authoritative identity / relationship / status records, external-object finalize and persistence semantics. RFC-003 remains authority for Durable Work Intent, Worker execution, retry / cancel / resume and Checkpoint reconciliation. RFC-004 remains the only public HTTP topology, error envelope and fixed-workspace transport authority. RFC-006 remains the only production Model Runtime authority. RFC-007 will own diagnostics, redaction, metrics, operational thresholds, retry delays, runbooks and alerting. ARP-05 / 08 and Development Planning own full external-object consistency evidence, retention, hold and physical deletion.

## Decision map

| Decision Question | Topic | Status |
|---|---|---|
| DQ-01 | Source authority, Task association, version / artifact manifest and reproducibility identity | PROPOSED as P-58A / B / C |
| DQ-02 | Registration, processing lifecycle, partial acceptance and typed item outcome | PROPOSED as P-59A / B / C |
| DQ-03 | Format-aware Fragment and Locator contract | PROPOSED as P-60A / B / C |
| DQ-04 | PostgreSQL Lexical / Vector topology and Exact / ANN boundary | PENDING |
| DQ-05 | Embedding, index entry versioning, update / rebuild and consistency | PENDING |
| DQ-06 | Planner, Query Rewrite, fusion, Top-K and optional reranking | PENDING |
| DQ-07 | Scope filtering, Source Set Version and public Source / Evidence transport | PENDING |
| DQ-08 | Retrieval Run, Evidence Package, Dataset Statistic and Formal Evidence Link | PENDING |
| DQ-09 | Retrieval evaluation, fallback, degraded behavior and quality gates | PENDING |
| DQ-10 | Adoption order, reconciliation, Spike / test evidence and RFC closure | PENDING |

No item in this table is Accepted until the user explicitly accepts the corresponding proposal and it is archived in a Decision record.

## Proposal Round 1

### P-58 — Source Authority, Association and Reproducible Manifest

#### P-58A — Versioned Source Graph + Task Association + Reference Manifest（推荐）

- Preserve RFC-002 as the sole persistence authority: PostgreSQL owns Source / Evidence identity, relationship, status and provenance. Content placement remains governed by its accepted Inline / External storage classification; RFC-005 does not create a second content authority or choose an object-storage Provider.
- Keep `Source`, immutable `SourceVersion`, mutable `TaskSourceAssociation` and versioned `DerivedArtifact` distinct. `TaskSourceAssociation` carries active membership and monotonic `revision`; remove / replace changes the association and creates an impact / invalidation path but does not mutate historical Source Versions or imply physical deletion.
- Each processing or retrieval input uses a `SourceSetVersion` whose manifest lists stable Source Association identities, exact Source Version identities and eligibility status. Re-running against the same manifest and component version tuple can explain which inputs were allowed.
- Derived text, Records, Fragments and Embedding / Lexical index entries always reference the exact Source Version and a readable component version tuple. Parser / fragmenter / embedding changes create new Derived Artifact versions; they do not overwrite old provenance.
- Evidence Package reproducibility uses the Source Set manifest, Retrieval Plan version, Retrieval Run identities and readable component versions. It does not add or expose a new `package_hash`, SHA-256 field or client-visible digest. If accepted, this point explicitly amends DEC-032's conceptual `package_hash` requirement while leaving stable identities and core object-integrity controls under RFC-002 intact and algorithm-neutral.
- Existing RFC-002 content-integrity identity stays private to its already accepted external-object consistency boundary. This RFC neither selects an algorithm nor propagates that identity into public API, domain confidence, retrieval score or acceptance tests.

**优点：** preserves accepted transaction and storage authority, gives remove / replace a revision-safe membership object, makes retrieval reproducible through readable identities and versions, and honors the prohibition on new Hash / SHA requirements.

**代价：** a reproducibility check must compare a structured manifest and version tuple rather than one opaque digest; physical storage and object reconciliation still require later ARP-05 / TS-02 evidence.

#### P-58B — Self-contained Evidence Package Snapshot

Copy all selected source text, Fragment bodies and processing metadata into every Evidence Package so the package can be replayed without resolving Source Version or Derived Artifact references.

**优点：** each package is locally self-contained and simple to inspect.

**代价：** duplicates private text, complicates retention / removal, allows package copies to drift from availability status and makes large review CSV / PDF packages expensive. It also blurs Candidate input with the authoritative Source graph.

#### P-58C — Resolve Latest Source State at Read Time

Store only Source identities and resolve current Source Version, current association and current parser/index output whenever a Skill or user opens evidence.

**优点：** smallest manifest and fewest stored references.

**代价：** historical results cannot reproduce their actual inputs; replace / reparse / reindex silently changes what old output appears to cite and violates immutable version provenance.

#### Recommendation

Choose P-58A. It concretizes already accepted storage and evidence authority without reopening RFC-002, while replacing only the unnecessary Evidence Package digest concept with readable, independently auditable version references.

### P-59 — Registration, Processing Lifecycle and Partial Acceptance

#### P-59A — Per-source Atomic Registration + Durable Processing + Typed Partial Results（推荐）

- A multi-item intake request is a batch envelope, not one atomic business aggregate. Boundary-invalid items such as unsupported media type or configured size excess are rejected individually; valid items can register their own Source / Source Version without being rolled back by a sibling failure.
- Registration validates only the real external boundary, records the immutable submitted input reference and commits a Source Version before asynchronous work is accepted. Durable processing uses the accepted Work Intent / Worker / Run infrastructure; no in-process background task becomes the correctness path.
- Small manual form / text input may complete deterministic normalization synchronously. TXT / Markdown, text PDF and review CSV use the same explicit processing contract and may complete asynchronously; the client never fabricates `ready` before the server commits it.
- Processing status is a small finite lifecycle: `registered`, `processing`, `ready`, `ready_with_rejections`, `failed`, `superseded`. Task association state such as active / removed / replaced remains separate from Source Version processing status.
- Typed `SourceItemResult` reports accepted identity or a stable RFC-004 Problem item detail. For review CSV, valid Records may be accepted while invalid rows are reported with bounded row issues; the Source Version becomes `ready_with_rejections` only when the accepted subset is still honest and usable. TXT / Markdown / PDF are not fragmented into speculative page-level partial success merely to avoid a file-level parse failure.
- Processing failure preserves the registered Source Version and safe failure summary for retry / replace; it creates no eligible Fragments, Source Set membership or Current Truth. Retry reuses the logical processing operation and creates a new Attempt, while user replacement creates a new Source Version / association basis.
- Parser output is candidate source material only. Processing success does not confirm Facts, pass QC, approve Strategy or start downstream Workflow unless a separate accepted command and minimum gate allow it.

**优点：** matches the accepted product promise that one bad file does not discard good files, keeps correctness durable, supports honest CSV row-level recovery and avoids a second workflow engine.

**代价：** the UI and API must display per-item outcomes and distinguish registration from processing; CSV partial acceptance needs a clear usable-subset rule.

#### P-59B — All-or-nothing Intake Batch

Reject or roll back the entire batch when any file or row fails validation or parsing.

**优点：** one apparent success / failure result and simpler transaction shape.

**代价：** directly conflicts with the accepted partial-file behavior, makes recovery expensive and couples unrelated Sources into one transaction.

#### P-59C — Eager Parse Inside Upload Request

Keep the HTTP request open until every file is parsed, fragmented and indexed, then return one final result.

**优点：** no visible intermediate processing state.

**代价：** unsafe for PDF / large CSV latency, cannot recover cleanly from client disconnects, bypasses durable processing and encourages the frontend to infer terminal state from request completion.

#### Recommendation

Choose P-59A. It gives the workbench honest item-level progress and recovery while reusing accepted durable execution and keeping validation proportional to the supported formats.

### P-60 — Format-aware Fragment and Locator Contract

#### P-60A — Structural Format Lanes + Stable Locators + Versioned Fragmenter（推荐）

- Use deterministic, format-aware lanes rather than one universal token splitter:
  - structured form / manual text: one Record per accepted field and one or more field-bound Fragments with `formSection` / `fieldName` locator;
  - TXT / Markdown: heading / paragraph-aware blocks with normalized line-range locator and preserved heading path;
  - text PDF: page-bound extracted blocks with page number and block / character range in extracted text; no OCR bounding box or image coordinate is promised;
  - review CSV: one Record per accepted row with source row number and stable column names; optional sentence-level Fragments retain the parent Record identity so one review never becomes multiple users.
- A Fragment never crosses Source Version, Record identity or PDF page boundary. It preserves verbatim source text for citation; any normalized search text is a separate derived field and cannot replace the display / evidence text.
- Structural units may be deterministically combined or split only to satisfy an accepted model / retrieval context bound. Exact target size and limited overlap are configuration values proven by evaluation, not permanent product semantics. Overlap never creates independent evidence counts.
- `fragmentId` is stable only within the exact Source Version + Derived Artifact version. Reprocessing with a changed parser / fragmenter creates new Fragment identities and a new eligibility set; old Evidence Links continue to resolve to historical Fragments subject to availability rules.
- Locator validity is tested with one representative case per supported lane and the Anchor SKU fixtures. Do not add OCR, arbitrary office formats, every malformed Unicode variant or a mechanical locator scorecard.

**优点：** maximizes citation honesty, preserves countable review rows, supports exact / lexical / semantic retrieval and avoids false precision for text PDFs.

**代价：** four small processing lanes and locator variants are more work than one token splitter; exact context size remains an evaluation-controlled implementation parameter.

#### P-60B — Universal Fixed-token Chunks with Overlap

Normalize every input to text, split by one token count and fixed overlap, and use only character offsets into the normalized text.

**优点：** one implementation path and straightforward Embedding batches.

**代价：** destroys CSV record counting, splits PDF citations across pages, weakens Markdown structure and makes normalized offsets hard for users to reconcile with original content.

#### P-60C — Query-time Ephemeral Fragments

Store only full extracted text / rows and create query-specific spans when retrieval runs.

**优点：** avoids a persistent Fragment store and can tailor spans to each query.

**代价：** Fragment identity and Locator change by query, so Evidence Links and historical outputs cannot stably resolve; repeated queries cannot distinguish retrieval change from source change.

#### Recommendation

Choose P-60A. It is the smallest design that preserves honest citations and countable Records across every supported first-Goal input format without adding OCR or a general document platform.

## Round 1 decision status and next gate

- `P-58 / P-59 / P-60 = PROPOSED`；none is Accepted until the user explicitly chooses an option.
- Recommended combination: `P-58A + P-59A + P-60A`.
- If accepted, archive the three decisions in one RFC-005 Decision Record, update only accepted Current Truth, and proceed to DQ-04～06 covering retrieval topology, component versions and deterministic planning / fusion.
- This round does not create Source schemas, database tables, object storage, parser code, Embeddings, indexes, API operations, frontend components, fixtures, dependencies, Technical Spikes or a Goal.

## Risks and stop conditions

- Stop if Source removal or replacement is treated as physical deletion or historical mutation.
- Stop if processing success, retrieval rank or Evidence Package membership is treated as verified Fact, QC pass or Human approval.
- Stop if an implementation choice requires OCR, Web scraping, broad office formats, cross-task private retrieval, multi-tenancy or a second public error envelope.
- Stop if a proposed filter can only remove disallowed candidates after their content has already crossed the authorized retrieval boundary.
- Stop if a new Hash / SHA-256 requirement is introduced without a separate core-integrity proposal that satisfies DEC-039.
- Stop if pgvector / PostgreSQL filtering evidence cannot satisfy the accepted Task / Scope / Source Version boundary; propose a topology change rather than weakening isolation.
- Stop if an index or object store is treated as Business Current Truth or cannot be rebuilt / reconciled from the authoritative graph.

## Acceptance and authorization boundary

RFC-005 remains `DRAFTING`. Proposal text is not Current Truth and does not authorize implementation. Overall RFC acceptance requires all DQ decisions, downstream document synchronization, local-link and Required Check success, an independent Sol/xhigh five-axis Final Consistency Review, and a separate explicit user decision.

Even if P-58A / P-59A / P-60A are accepted, the following remain `NOT GRANTED`:

- RFC-005 overall acceptance;
- dependency installation or exact version locking;
- Parser / Fragmenter / Embedding / Index / Retrieval / API / Frontend / Database / Migration implementation;
- ARP / TS-01～TS-05 execution or any Live Provider call;
- RFC-007 acceptance, Goal creation / activation or release.

## Outcome

PENDING USER DECISIONS FOR P-58～P-60.
