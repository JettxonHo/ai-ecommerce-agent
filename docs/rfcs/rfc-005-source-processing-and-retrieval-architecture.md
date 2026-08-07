# RFC-005：Source Processing and Retrieval Architecture

## Metadata

- **Status:** ACCEPTED — 2026-08-07 USER OVERALL ACCEPTANCE
- **Date:** 2026-08-07
- **Issue:** [#56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56)
- **Pull Request:** [#57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)
- **RFC Acceptance:** GRANTED — 2026-08-07
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
- PostgreSQL 的 [`pg_trgm`](https://www.postgresql.org/docs/current/pgtrgm.html) 扩展提供基于 trigram 的相似度与 GIN / GiST 索引操作符，可作为 CJK / identifier-heavy 输入的 PostgreSQL-native 词法候选能力。是否采用及其阈值仍须由本 RFC 的用户 Decision 与固定评测证据决定。
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
| DQ-01 | Source authority, Task association, version / artifact manifest and reproducibility identity | ACCEPTED — P-58A / DEC-067 |
| DQ-02 | Registration, processing lifecycle, partial acceptance and typed item outcome | ACCEPTED — P-59A / DEC-067 |
| DQ-03 | Format-aware Fragment and Locator contract | ACCEPTED — P-60A / DEC-067 |
| DQ-04 | PostgreSQL Lexical / Vector topology and Exact / ANN boundary | ACCEPTED — P-61A / DEC-068 |
| DQ-05 | Embedding, index entry versioning, update / rebuild and consistency | ACCEPTED — P-62A / DEC-068 |
| DQ-06 | Planner, Query Rewrite, fusion, Top-K and optional reranking | ACCEPTED — P-63A / DEC-068 |
| DQ-07 | Scope filtering, Source Set Version and public Source / Evidence transport | ACCEPTED — P-64A / DEC-069 |
| DQ-08 | Retrieval Run, Evidence Package, Dataset Statistic and Formal Evidence Link | ACCEPTED — P-65A / DEC-069 |
| DQ-09 | Retrieval evaluation, fallback, degraded behavior and quality gates | ACCEPTED — P-66A / DEC-069 |
| DQ-10 | Exact Embedding Profile, public contract closure, adoption order, reconciliation and verification evidence | ACCEPTED — P-67A with explicit MVP-0 staging amendment / DEC-070 |

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

- `P-58A + P-59A + P-60A = ACCEPTED` by explicit user decision on 2026-08-07 and archived in [DEC-067](../decisions/dec-067-versioned-source-intake-and-format-aware-fragment-contract.md).
- P-58A explicitly amends DEC-032 by removing the Evidence Package `package_hash` step / field. Existing RFC-002 object-integrity controls remain private, algorithm-neutral and unchanged; no new Hash / SHA-256 or public digest is introduced.
- P-59A makes `registered / processing / ready / ready_with_rejections / failed / superseded` the Source Version processing lifecycle and keeps association / availability / integrity as separate dimensions.
- P-60A freezes four supported format-aware Fragment / Locator lanes without OCR or a generic document platform.
- This round does not create Source schemas, database tables, object storage, parser code, Embeddings, indexes, API operations, frontend components, fixtures, dependencies, Technical Spikes or a Goal.

## Proposal Round 2

### P-61 — PostgreSQL Lexical / Vector Topology and Exact / ANN Boundary

#### P-61A — PostgreSQL-native Derived Retrieval Plane + Exact-first Vector Search（推荐）

- Keep one PostgreSQL service as the production data platform already accepted by RFC-002. Authoritative Source / Fragment / association / availability records remain owned by the Source / Evidence capability; lexical and vector entries live in separate retrieval-owned derived tables / schema and remain rebuildable, non-authoritative projections.
- Use a PostgreSQL-native lexical lane rather than a second search service. Exact identifiers and normalized keys use deterministic equality / prefix lookup. Language-configured text may use `tsvector` + GIN where its tokenizer is proven suitable; CJK / identifier-heavy text uses a bounded `pg_trgm` GIN lane so Chinese ecommerce material is not forced through an unsuitable word tokenizer. Both representations point to the same eligible Fragment identity and preserve channel-specific ranks.
- Use `pgvector` for the semantic lane in the same PostgreSQL service. The first-Goal baseline uses filtered exact nearest-neighbor queries, with ordinary indexes on authoritative filter columns / joins. Mandatory Task, Source Set Version, association, Source Scope, product / competitor identity, Source Version and availability predicates are part of the SQL candidate relation before relevance ordering; application-side post-filtering of a broad cross-scope result is prohibited.
- HNSW / IVFFlat are not enabled by default. ANN becomes an optional later optimization only when the accepted fixture / expected data envelope shows exact search misses a documented latency budget and an isolated evaluation proves filtered recall, no cross-scope candidate exposure, explainable fallback and rebuild behavior. Enabling ANN requires its own focused Issue / PR and cannot weaken mandatory filters.
- Direct / Exact / bounded reads and lexical retrieval remain available when Embedding or vector search is unavailable. A semantic outage cannot cause a switch to an external vector database, cross-task scope, or a fabricated result.
- Exact PostgreSQL / extension patch versions, index DDL and query plans are compatibility evidence for the authorized Goal, not choices for an implementation Agent to invent. The RFC freezes topology and activation gates, not speculative scale tuning.

**优点：** one operational data service, transactional identity joins, CJK-aware lexical behavior, simplest isolation proof and no premature ANN / external search infrastructure.

**代价：** exact vector search may eventually need optimization at larger scale; the lexical lane has two deterministic representations instead of pretending one tokenizer fits every supported language.

#### P-61B — PostgreSQL FTS + ANN from Day One

Use only `tsvector` / GIN for all languages and create an HNSW vector index before any measured need.

**优点：** familiar single lexical path and immediately available approximate search.

**代价：** risks weak Chinese tokenization, adds recall / filtering behavior before the local MVP needs it, and makes mandatory scope proof harder because pgvector documents that approximate-index filtering occurs after index scan.

#### P-61C — Dedicated External Search / Vector Service

Replicate Source / Fragment metadata into an external full-text and vector platform and query it as the primary retrieval engine.

**优点：** mature large-scale search features and independent scaling.

**代价：** creates a second consistency plane, new credentials / deployment / reconciliation, and cross-service scope-filter risk without a first-Goal scale requirement.

#### Recommendation

Choose P-61A. It is the smallest topology that honestly supports Chinese / identifier-heavy material, semantic retrieval and authoritative filtering while keeping ANN as evidence-driven optimization rather than assumed infrastructure.

### P-62 — Embedding Profile, Index Versioning and Reconciliation

#### P-62A — Single Versioned Embedding Profile + Immutable Index Generations + Eligibility-first Switching（推荐）

- Define a narrow Retrieval-owned Embedding Port with one active OpenAI Embeddings adapter / profile for the first Goal, aligned with the already accepted single-Provider boundary. No second Provider, automatic failover or direct SDK use outside the adapter is allowed. The exact current model identifier and dimensions must be frozen in RFC-005's final contract closure from official compatibility evidence; an implementation Issue cannot choose or change them.
- An `EmbeddingProfileVersion` is readable and at least identifies provider family, model identifier, output dimensions, distance / normalization policy, input-normalization version and batching policy. It contains no Secret and is not a public Product status.
- Every lexical / vector `RetrievalIndexEntry` references the exact Fragment, Source Version, Derived Artifact / Fragmenter version, index generation and applicable lexical / embedding profile. One Retrieval Run uses one compatible profile per channel; it never mixes vector dimensions or silently combines entries from different Embedding profiles.
- New Source Version or new Derived Artifact creates new entries. remove / replace / restriction changes authoritative eligibility immediately, so stale entries become unqueryable through the authoritative candidate relation even before physical cleanup. Reparse, refragment, model or profile change creates a new immutable generation; it does not overwrite old provenance.
- Build and reconcile a new generation side-by-side. Only after every expected eligible Fragment is accounted for and representative retrieval checks pass may one atomic current-generation pointer / equivalent eligibility switch make it active. Failed or partial builds remain non-current and cannot be blended into results.
- Historical Retrieval Runs retain profile / generation references. Old generations are cleaned only under later retention rules; rebuild loss or index corruption never changes Source, Evidence Link or Business Current Truth.
- Reconciliation compares readable identities, expected / present / missing / extra entry sets and eligibility state. It does not add a package digest, general integrity framework or low-probability test matrix.

**优点：** reproducible profile changes, no mixed-vector ambiguity, immediate removal safety through authoritative eligibility and rollback by pointer without treating the index as truth.

**代价：** side-by-side rebuild temporarily uses extra storage; the exact model ID still needs a time-sensitive final closure check before RFC acceptance.

#### P-62B — Mutable In-place Re-embedding

Update embeddings and lexical fields on existing entries whenever Parser, Fragmenter or model configuration changes.

**优点：** minimal temporary storage and no generation switch.

**代价：** old Retrieval Runs become irreproducible, partial updates can mix dimensions / versions, and rollback is unclear.

#### P-62C — Multiple Embedding Providers with Runtime Failover

Maintain two providers / profiles and fail over automatically when one is unavailable.

**优点：** higher theoretical availability.

**代价：** score spaces, dimensions and behavior differ; it violates the single-Provider MVP boundary and adds recovery complexity unsupported by the demo goal.

#### Recommendation

Choose P-62A. It creates one auditable change / rebuild path and keeps eligibility authoritative without inventing multi-provider resilience. The exact OpenAI embedding model remains a named final-closure evidence item, not an implementation-time choice.

### P-63 — Deterministic Planner, Fusion, Candidate Bounds and Reranking

#### P-63A — Rule-based Direct-first Planner + Rank Fusion + No Baseline Reranker（推荐）

- Use a versioned deterministic strategy catalog: `direct`, `exact`, `bounded_document`, `lexical`, `semantic`, `hybrid`. Structured / exact / bounded paths win whenever they satisfy the request; evidence discovery uses hybrid by default only after mandatory scope and eligibility are fixed.
- The first Goal does not use LLM Query Rewrite. Query construction is deterministic from retrieval purpose, user / Skill query, structured aliases and exact identifiers; exact identifiers are preserved byte-for-byte. A later LLM rewrite path requires evaluation evidence and an RFC amendment because it changes reproducibility and Model Runtime use.
- Lexical and semantic channels run independently against the same authorized candidate relation, deduplicate by stable Fragment identity, and preserve channel ranks / matched queries. Hybrid uses Reciprocal Rank Fusion rather than adding incomparable lexical and vector scores.
- Seed configuration is bounded and versioned: at most 4 deterministic query variants, at most 20 candidates per retrieval channel, RRF rank constant `60`, and at most 12 fused Candidate Fragments returned to coverage checks / Evidence Package assembly. These are retrieval candidate limits, not evidence strength, dataset frequency or mechanical acceptance scores; the fixed evaluation set may justify a documented change before implementation activation.
- Reranking is not part of the first-Goal baseline. It may be proposed only if the accepted evaluation set shows a material relevance failure that deterministic planning + RRF cannot resolve; it may only reorder already allowed candidates and must fall back to fusion.
- Zero eligible / relevant results return `insufficient_information`; semantic failure degrades explicitly to Direct / Exact / Lexical when those lanes are valid. No fallback expands scope, changes Source Set Version or turns a rank into Formal Evidence.
- Planner and fusion tests cover the strategy table, exact-identifier preservation, mandatory-filter application, stable dedup / RRF behavior, bounded candidates, semantic fallback and zero-result behavior. They do not enumerate arbitrary query permutations.

**优点：** reproducible, easy to test, avoids a second LLM decision loop and combines channel ranks without false score equivalence; bounded candidates control latency and review load.

**代价：** deterministic rewrite handles fewer linguistic variations than an LLM planner; the seed limits require evaluation against the fixed Anchor SKU set before activation.

#### P-63B — Weighted Raw-score Fusion + Mandatory Cross-encoder Reranker

Normalize or directly weight channel scores, then require a reranker on every hybrid request.

**优点：** potentially stronger ranking after careful calibration.

**代价：** introduces calibration, latency, another model profile and failure path before the fixture proves need; direct raw-score addition would violate DEC-032.

#### P-63C — LLM-generated Query Plan and Dynamic Candidate Budget

Let the LLM decide strategy, query rewrites, candidate count and whether to rerank for every request.

**优点：** flexible natural-language planning.

**代价：** less reproducible, can drift from exact identifiers / scope, expands Model Runtime coupling and makes latency / candidate volume unpredictable.

#### Recommendation

Choose P-63A. It preserves the already accepted deterministic planner boundary, gives implementers an explicit bounded baseline and leaves reranking / LLM rewrite behind evidence rather than speculation.

## Round 2 decision status and next gate

- 用户于 2026-08-07 明确接受 `P-61A + P-62A + P-63A`，并归档为 [DEC-068](../decisions/dec-068-postgresql-native-versioned-and-deterministic-retrieval-baseline.md)；P-61B / C、P-62B / C、P-63B / C 保留为未采用 Alternative。
- `DQ-04～06 = ACCEPTED`；PostgreSQL-native derived retrieval plane、filtered exact NN baseline、单一版本化 OpenAI Embedding Profile、immutable index generation、deterministic Direct-first Planner、RRF、seed candidate bounds 与 no-baseline-reranker 已成为 Current Truth。
- Exact OpenAI Embedding model identifier / dimensions 仍是 RFC-005 Final Closure 的强制 evidence item，不得由 Implementation Agent 临场选择。
- This round does not install PostgreSQL extensions, call OpenAI, create indexes / schemas / migrations / retrieval code, execute evaluation or Technical Spikes, or activate the Goal.

## Proposal Round 3

### P-64 — Authoritative Scope, Source Set and Public Source / Evidence Transport

#### P-64A — Server-derived Scope + SQL Eligibility Boundary + Narrow Public Projections（推荐）

- Fixed Workspace identity 继续由 RFC-004 的 server configuration 注入；Browser、Skill 或 Provider payload 都不能提交任意 Workspace / Task / Source Scope 以扩大访问范围。调用方只表达已接受的 retrieval purpose / exact reference，服务端从 Task、Skill Contract、TaskSourceAssociation revision、SourceSetVersion manifest 与 Product / Competitor identity 推导 allowed scope。
- 同一条 authoritative eligible-candidate relation 同时约束 Direct / Exact / Lexical / Semantic / Hybrid。它至少连接当前 Task association、精确 Source Version、SourceSetVersion membership、Source Scope、Product / Competitor identity、processing readiness、availability 与 current index generation；不允许先检索跨范围正文、再在 Application 或 Frontend 中删除。
- SourceSetVersion 是不可变的运行输入 manifest，固定 association identity + revision、精确 Source Version 与 eligibility basis。Source remove / replace / restriction 使新的运行不能继续使用旧 membership；历史 Retrieval Run / Evidence Package 仍引用当时 manifest，但不得冒充 Current input。
- 填充 RFC-004 已委托的 Source / Evidence refs，而不创建第二 HTTP authority：提供 task-scoped Source intake / item result、Source summary / exact SourceVersion processing read、Source collection 与 Evidence collection read；remove / replace 仍使用 RFC-004 已冻结的四个 Preview / Confirm operations。
- Source / Evidence list 使用 opaque cursor keyset pagination，稳定排序为服务端时间 + stable identity；默认 20、最大 50。Cursor 只用于翻页，不承担 authorization、revision、idempotency 或 integrity proof；参数越界使用既有 RFC-004 validation Problem。
- Public Source projection 只暴露工作台需要的 identity、display metadata、association / version reference、processing / availability、typed item issues、Locator-safe preview 与 Capability。Public Evidence projection 只暴露 stable Evidence Link / target version / Fragment reference、verbatim excerpt、honest Locator、Evidence role / class、availability 与 limitation。不得暴露 embedding vector、raw index row、Provider payload、SQL filter、private storage reference 或把 rank 显示成 confidence。
- Source content download / preview 仍受同一 Task / SourceSet / availability check；外部对象 URL 不成为长期公共 identity。首个 Goal 不增加 Login、RBAC、多租户、跨 Task knowledge browser、public share link 或 permanent-delete endpoint。

**优点：** 范围在内容进入检索前即被权威关系约束，公共投影足够支撑 Workbench 与 Evidence drill-down，又不泄漏 Index / Storage 实现；cursor pagination 可稳定处理大量 Source / Evidence。

**代价：** OpenAPI Contract Issue 需要补齐 RFC-005 refs、cursor envelope 与 Source lifecycle operations；服务端必须维护一条可被多个 channel 复用的 candidate relation。

#### P-64B — Client-selected Scope + Offset Pagination

客户端提交 Workspace、Source scopes 与 offset / page，Backend 只校验字段格式并据此检索。

**优点：** UI 筛选灵活，接口容易理解。

**代价：** 把 authorization / business scope 变成不可信客户端输入；offset 在异步处理和 Source 变化时容易重复 / 跳项，也会诱导 Frontend 维护第二套 eligibility 状态。

#### P-64C — Broad Retrieval + Application Post-filter + Public Index Detail

先从所有 indexed Fragment 召回，再由 Application 删除不允许结果，并向 UI 暴露 raw score、vector / index metadata 方便诊断。

**优点：** Retrieval query 简单，调试信息丰富。

**代价：** 不允许内容已越过授权边界，违反 Task-scoped private material；公共 Index 细节会形成不必要兼容承诺并把 rank 误读成证据质量。

#### Recommendation

Choose P-64A. It makes scope a server-owned precondition, preserves RFC-004 as the single HTTP authority and exposes only the stable Source / Evidence semantics the Workbench can act on.

### P-65 — Retrieval Run, Evidence Package, Dataset Statistic and Formal Evidence Link

#### P-65A — Immutable Execution Record + Referenced Package + Atomic Validated Evidence Commit（推荐）

- 每次实际 Retrieval execution 创建不可变 `RetrievalRun`，记录 task / purpose、Retrieval Plan version、SourceSetVersion、authorized filter summary、query identities、channel / component profile and generation references、bounded candidate identity / rank summary、degraded / zero-result outcome、started / completed time 与 correlation reference。它是运行解释记录，不是业务 Current Truth，也不保存 Secret / Provider payload。
- `EvidencePackage` 是不可变的 Skill input snapshot：引用 exact SourceSetVersion、RetrievalPlan、RetrievalRun(s)、selected Candidate Fragment identities、适用 verified Fact references、DatasetStatistic identities、known conflicts、coverage summary、limitations 与可读 component versions。它不复制整库正文、不绑定 latest-at-read，也不使用 package Hash / Digest。
- Candidate Fragment body / excerpt 可在同一受控事务读取，但 Package 的 identity / version reference 是重现权威。历史 Package 打开时明确展示其 current / superseded / unavailable relationship；availability 变化不改写历史 Package。
- `DatasetStatistic` 只能由确定性 dataset-analysis path 对完整、明确可计数的 Record set 生成，固定 dataset / SourceSet version、population definition、included / rejected counts、deterministic method version 与 limitations。Top-K Candidate、RRF rank 或 LLM summary 不得生成正式 frequency / proportion。
- Skill 输出只携带待验证 Fragment / DatasetStatistic references。Evidence Validator 按当前 Task、Package membership、Source scope / version / availability、Locator 与 target claim boundary 校验；同一业务事务原子创建 Versioned Domain Object、Formal Evidence Link 与 Current Truth pointer / audit effect。任一校验或提交失败不留下部分 Evidence Link 或部分 Current Truth。
- Formal Evidence Link 使用稳定 identity，至少关联 target domain object version、Fragment 或 DatasetStatistic reference、Evidence role / class、accepted wording / claim target、source / locator projection 与 availability。Retrieval rank 仅留在 RetrievalRun / Candidate explanation，不成为 link confidence。
- Public API 只返回 task-scoped Package / Evidence projection 和 stable references；内部 full RetrievalRun 主要供 dev / eval / operator 使用，RFC-007 决定日志、Trace、redaction 与保留，而非在 RFC-005 复制运维协议。

**优点：** 清楚分开执行记录、Skill 输入、统计证据与正式业务关系，支持历史解释和原子提交，又不复制敏感正文或引入 digest。

**代价：** 读取历史 Package 需要解析多个 immutable references；Dataset Statistic 必须有独立确定性路径，不能复用 Top-K 结果偷算比例。

#### P-65B — Fully Copied Evidence Package as Business Truth

把全部候选正文、scores、统计和 Skill 结论复制进 Package，并把 Package 本身作为可批准的 Current Truth。

**优点：** 单对象读取方便。

**代价：** 重复私有内容、模糊 Candidate / Formal Evidence / Business Truth，移除与保留复杂，并可能把 rank 或生成结果误作已验证事实。

#### P-65C — One Generic Evidence Object

用一个可变对象同时表示 Candidate、统计、正式 Evidence Link、用户展示和运行日志。

**优点：** Schema 数量少。

**代价：** 不同生命周期、事务与可信度被压成同一状态，容易让 QC / retrieval success 等同 approval，并破坏历史版本和独立验证。

#### Recommendation

Choose P-65A. It preserves the accepted Candidate-to-Validator-to-Formal-Link transition and gives statistics a truthful complete-dataset basis without turning the Evidence Package into a second business database.

### P-66 — Retrieval Evaluation, Fallback and Degraded Behavior

#### P-66A — Fixed Representative Evaluation + Behavioral Hard Gates + Explicit Degradation（推荐）

- 基于 DEC-058 的同一个虚构 Anchor SKU 三资料变体和 mutation，建立版本化 Retrieval evaluation manifest；覆盖 exact identifier、CJK lexical、semantic paraphrase、hybrid / counter-evidence、scope isolation、complete review-dataset statistic、zero result、removed / replaced Source、semantic outage 与 incomplete generation。Fixture 内容和最终 runner 由 Testing Strategy / Goal Issue 创建，本 RFC 只冻结行为。
- Hard gates 为行为不变量：零跨 Task / Scope / Product leakage；零 stale / unavailable / non-current-generation candidate；零 Top-K frequency extrapolation；zero result 不生成答案；Exact identifiers 原样命中；相同 manifest + plan + component tuple 产生相同 candidate identities / order；Formal Evidence 只在 Validator + atomic commit 后出现。任一失败阻断对应生产 slice。
- Retrieval usefulness 由代表性 query 的 Recall@K / reciprocal-rank、coverage / counter-evidence 与人工 `PASS / FAIL` 判断共同说明。数值指标用于诊断和比较，不用单一 aggregate score、机械 rubric 或为了达分堆叠低价值 queries；K 与通过阈值由 Testing Strategy 在固定 fixture 内容可见后冻结。
- Semantic unavailable 时只运行适用的 Direct / Exact / Lexical 并传播 `semantic_retrieval_unavailable` limitation；Lexical unavailable 时 Direct / Exact 保持，Semantic 只在 authorized candidate relation 和 exact identifier coverage 均成立时继续，否则返回 limitation / `insufficient_information`。任何 fallback 都不扩大 Scope 或改用旧 generation。
- 当前 generation incomplete / failed 时不切换；继续使用仍兼容且 eligibility-current 的上一 generation，或只运行 Direct / Exact / applicable Lexical 并显式限制。没有安全兼容 generation 时返回 temporary unavailable / actionable recovery，不让客户端模拟完成。
- Reranker、LLM rewrite 或 ANN 只有在 fixed evaluation 显示 deterministic exact + RRF baseline 的实质质量 / latency缺口时才可提案；提案必须带 before / after、Scope isolation、rollback 与额外 failure behavior 证据。
- RFC-007 继续拥有 metric export、latency / error operational threshold、alerts、retry delay 与 runbook；RFC-005 只输出 typed retrieval outcome / limitation 与 evaluation evidence contract。

**优点：** 关键隔离与证据真实性是不可协商行为门禁，相关性仍由数据和人工可用性共同判断；故障降级诚实且不会扩大范围。

**代价：** 最终 K / relevance threshold 必须等固定 Fixture 内容形成后才能校准；部分 outage 会降低证据覆盖而非伪装正常。

#### P-66B — One Aggregate Retrieval Score Gate

把 recall、latency、cost、coverage 与人工评分合成一个总分，达到阈值即可接受。

**优点：** 报告简洁、容易比较。

**代价：** 严重的 Scope leakage 可被其他高分抵消，Rubric 变成机械接受器，也掩盖不同查询类型的失败。

#### P-66C — Live-provider-only Evaluation and Silent Fallback

主要依赖实时 Provider / ad hoc queries 验证；任何 channel 失败时静默切换其余 channel 并继续生成。

**优点：** 看起来接近真实运行且流程不中断。

**代价：** 不可重复、依赖 Secret / 网络、难以定位回归；静默降级会让用户误判证据覆盖，并可能在关键缺口下继续生成。

#### Recommendation

Choose P-66A. It separates non-negotiable correctness from relevance judgment, uses the already accepted representative fixture strategy and keeps degraded behavior explicit instead of optimistic.

## Round 3 decision status and next gate

- `P-64A / P-65A / P-66A = ACCEPTED` and archived as [DEC-069](../decisions/dec-069-authoritative-retrieval-scope-referenced-evidence-and-explicit-degradation.md).
- RFC-005 DQ-07～09 are closed. Acceptance preserves RFC-004 as the HTTP / Problem authority and RFC-007 as the operations / telemetry authority.
- Round 3 acceptance does not create OpenAPI, schemas, fixtures, migrations, indexes, evaluation code, Source / Evidence API, Technical Spikes or Goal execution.

## Proposal Round 4 — Final Closure

### P-67 — Exact Embedding Profile, Public Contract Catalog and Adoption Evidence

#### Current official compatibility evidence

- OpenAI's current [Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings#how-to-get-embeddings) documents `text-embedding-3-small` with a default 1536-dimensional output and supports an explicit `dimensions` parameter for third-generation models. The current API reference accepts the model identifier, input, dimensions and output encoding as request fields.
- OpenAI's current [distance FAQ](https://developers.openai.com/api/docs/guides/embeddings#which-distance-function-should-i-use) recommends cosine similarity and states that OpenAI embeddings are normalized to length one. This supports a fixed cosine policy without adding an application-owned normalization heuristic.
- The pgvector [official project documentation](https://github.com/pgvector/pgvector) supports `vector` dimensions above 1536, cosine distance through `<=>`, exact nearest-neighbor by default and filtered queries. It also confirms that approximate indexes change recall and apply filtering with additional trade-offs, supporting the already accepted exact baseline.
- These sources establish capability and the profile choice as of 2026-08-07. They do not authorize dependency installation, live calls or a permanent package version. Exact PostgreSQL, pgvector, OpenAI SDK and parser package versions must be recorded from the Goal's locked environment and official compatibility evidence in their implementation PRs.

#### P-67A — Contract-first Closure + `text-embedding-3-small` 1536 Cosine + Bounded Verification（推荐）

##### Exact active Embedding Profile

- Freeze the first-Goal active profile as provider family `openai`, API family `embeddings`, model identifier `text-embedding-3-small`, explicit output dimensions `1536`, `encoding_format=float` and cosine distance. The adapter sends `dimensions=1536`; PostgreSQL stores compatible `vector(1536)` values and exact semantic ordering uses pgvector cosine distance `<=>`.
- Use the readable profile identity `openai-text-embedding-3-small-1536-cosine-v1`. Its input-normalization version and bounded batching policy remain explicit readable profile fields; batching can improve transport efficiency but cannot change per-input identity, Source / Fragment references or authorized scope.
- Do not perform a second application normalization pass merely because vectors are stored in PostgreSQL. Boundary validation checks response count, dimensions, finite numeric values and request-to-response order; it does not create a broad statistical validator or repeated low-probability case matrix.
- Provider responses are not promised bitwise deterministic. PR tests use the accepted deterministic Embedding Port substitute. Live profile verification is one manual opt-in RC smoke, while generation identity, response model metadata and evaluation evidence explain which profile produced a stored entry.
- A future model, dimension, distance or normalization change creates a new readable `EmbeddingProfileVersion` and immutable generation; it never mixes vectors in place. It requires an explicit Decision / RFC amendment if it changes this active first-Goal contract.

##### Source / Evidence operation catalog delegated by RFC-004

The future single `contracts/openapi/openapi.yaml` must add exactly these RFC-005-owned first-Goal operations without changing RFC-004's existing four Source-change operations:

| Family | Operations frozen for the first Goal |
|---|---|
| Source intake | `POST /api/v1/tasks/{taskId}/source-intakes`; `GET /api/v1/source-intakes/{sourceIntakeId}` |
| Task Source collection / detail | `GET /api/v1/tasks/{taskId}/source-associations`; `GET /api/v1/source-associations/{sourceAssociationId}`; `GET /api/v1/source-associations/{sourceAssociationId}/source-versions`; `GET /api/v1/source-versions/{sourceVersionId}` |
| Formal Evidence | `GET /api/v1/tasks/{taskId}/evidence-links`; `GET /api/v1/evidence-links/{evidenceLinkId}` |

- `POST .../source-intakes` accepts the supported structured form / manual text as `application/json`, or a bounded `multipart/form-data` intake manifest plus file parts for TXT / Markdown、text PDF and review CSV. It requires `Idempotency-Key`. Envelope-invalid requests use RFC-004 Problem Details; supported sibling items return typed per-item acceptance / rejection rather than all-or-nothing rollback.
- A fully synchronous accepted intake first returns `201`; an intake with any registered asynchronous processing first returns `202` with one immutable `SourceIntakeReceipt` and `Location` pointing to the `SourceIntake` read resource; a same-key / same-input committed replay returns `200` with the same receipt. `SourceIntake` projects per-item canonical Source Version processing states and does not create a competing generic operation state machine.
- Source collection, Source Version history and Evidence Link collection use DEC-069's opaque cursor keyset pagination with default `20` and maximum `50`. Detail operations return the narrow Source / Evidence projections accepted in P-64A; there is no public Fragment search, vector, raw Candidate, Retrieval Run, Evidence Package, index administration, delete / purge or cross-Task operation.
- Schema families are `SourceIntakeRequest` / `SourceFileManifestItem` / `SourceIntakeReceipt` / `SourceItemResult` / `SourceIntake`、`SourceAssociationSummary` / `SourceAssociation` / `SourceVersionSummary` / `SourceVersion` / the six-value `SourceProcessingStatus`、`CursorPage` / `PageCursor`、and `EvidenceLinkSummary` / `EvidenceLink` with format-specific Locator discriminators. RFC-004's Reference、revision、Capability、Problem、Idempotency and fixed-workspace conventions are reused rather than redefined.
- Read ordering, cursor behavior and public availability are server-owned projections. Unknown additive read-only enum values use RFC-004's safe frontend fallback; new write semantics, Operation paths or Scope behavior require an explicit compatibility review.

##### Adoption order and bounded evidence

After the full planning package and Goal are separately approved, implementation Issues must follow this dependency order:

1. Extend the one OpenAPI authority with the above Source / Evidence paths, schemas, examples and generated-client clean diff; no API or Frontend implementation precedes this contract PR.
2. In a bounded real-PostgreSQL compatibility subtask, prove the Goal's locked PostgreSQL / pgvector / driver / OpenAI SDK versions support `vector(1536)`, cosine exact ordering and the required parameterized authorized relation. Record official sources and locked versions; do not call the live Provider in PR CI.
3. Implement the authoritative Source graph, registration / processing lifecycle and four format-aware Parser / Fragment lanes before any index consumer. External-object work remains gated by ARP-05 / TS-02.
4. Implement lexical / vector derived entries, immutable generation build, expected / present / missing / extra reconciliation, atomic current-generation switch and rollback before enabling Semantic / Hybrid retrieval.
5. Implement deterministic Planner、Exact / Lexical / Semantic / Hybrid channels、RRF and the DEC-069 fixture evaluation before any Core Skill may consume retrieval output.
6. Implement referenced Evidence Package、DatasetStatistic、Evidence Validator and atomic Domain Version + Formal Evidence Link commit before exposing Evidence Link reads.
7. Implement Source / Evidence API handlers and generated-client / TaskWorkbench integration only after owning Application Contracts pass. RFC-007 diagnostics are added through its later accepted extensions, not invented here.

Required evidence is intentionally finite:

- OpenAPI parse / `$ref` / example / operationId / media / status validation and generated-client clean diff;
- real PostgreSQL Integration Tests for `vector(1536)` cosine exact ordering, SQL pre-ranking scope isolation, Source removal eligibility, generation reconciliation / switch / rollback and concurrent read during switch;
- deterministic unit / contract tests for four processing lanes、six processing states、planner strategy、RRF tie order、candidate bounds、zero result、degraded limitation and Validator + atomic commit;
- DEC-058 / DEC-069 representative Retrieval evaluation with behavior hard gates plus non-mechanical human relevance judgment;
- one opt-in RC live Embedding smoke using non-sensitive fictional Fixture text, verifying response model / 1536 dimensions / finite values without committing Secret or raw provider payload.

No new standalone Technical Spike is required merely to repeat capabilities already established by official documentation. The bounded real-PostgreSQL compatibility subtask is a stop-first slice inside the first authorized Retrieval foundation Issue; if it fails, downstream Retrieval production Issues stop and return to the RFC / architecture Gate.

Stop and request a new decision if the exact model is unavailable, the response cannot honor 1536 dimensions, the locked environment cannot provide required PostgreSQL extensions, the authorized relation cannot filter before ranking, or representative behavior gates fail. Latency evidence may justify an ANN proposal, but never a Scope or correctness relaxation.

**优点：** freezes every implementation-time choice that would otherwise split API, Index and Frontend contracts; uses the smaller documented embedding profile and exact retrieval appropriate to the MVP; makes compatibility failure stop before downstream work while avoiding a speculative standalone Spike.

**代价：** Source / Evidence contract and real-PostgreSQL foundation must land before visible UI work; an embedding profile change requires a new generation and explicit contract update rather than an in-place switch.

#### P-67B — `text-embedding-3-large` 3072 Cosine with the Same Contract-first Order

Use `text-embedding-3-large` with explicit 3072 dimensions and exact cosine retrieval, while keeping the same API catalog and adoption order.

**优点：** current OpenAI documentation reports a stronger general embedding benchmark and the full default dimensions preserve that model's largest representation.

**代价：** doubles vector width relative to P-67A, increases provider / storage / transfer cost, and has no project fixture evidence that the gain matters. Full 3072-dimensional `vector` also exceeds pgvector's current approximate `vector` index dimensional limit, making a later ANN path require dimension reduction or another storage choice. That complexity is unnecessary for the first Goal.

#### P-67C — Defer Model, Paths and Compatibility to Implementation Issues

Keep only conceptual Source / Retrieval types and let the OpenAPI, persistence and retrieval implementers select the model, dimensions, paths, pagination details and verification order.

**优点：** shortest planning phase and maximum local flexibility.

**代价：** violates the accepted contract-first boundary and P-62A requirement, prevents independent Agent tasks from sharing one contract, and reopens high-cost choices inside implementation PRs.

#### Recommendation and next gate

P-67A was recommended as the smallest profile and contract set that closes DQ-10 without adding ANN, a second Provider, a generic search API or a new speculative Technical Spike.

The user accepted P-67A together with the accelerated MVP-0 Gate. [DEC-070](../decisions/dec-070-fixed-embedding-contract-and-accelerated-mvp0-adoption.md) freezes the target profile and public catalog while explicitly amending adoption order: MVP-0 may deliver verified Direct / Exact / PostgreSQL Lexical retrieval before text PDF、Embedding / Semantic / Hybrid, which move to MVP-1 without changing Scope / Evidence / public identity contracts. DQ-01～10 are closed, the [RFC-005 Final Consistency Review](../reviews/review-2026-08-07-rfc-005-final-consistency.md) is PASS, and the user accepted RFC-005 overall on 2026-08-07.

## Risks and stop conditions

- Stop if Source removal or replacement is treated as physical deletion or historical mutation.
- Stop if processing success, retrieval rank or Evidence Package membership is treated as verified Fact, QC pass or Human approval.
- Stop if an implementation choice requires OCR, Web scraping, broad office formats, cross-task private retrieval, multi-tenancy or a second public error envelope.
- Stop if a proposed filter can only remove disallowed candidates after their content has already crossed the authorized retrieval boundary.
- Stop if a new Hash / SHA-256 requirement is introduced without a separate core-integrity proposal that satisfies DEC-039.
- Stop if pgvector / PostgreSQL filtering evidence cannot satisfy the accepted Task / Scope / Source Version boundary; propose a topology change rather than weakening isolation.
- Stop if an index or object store is treated as Business Current Truth or cannot be rebuilt / reconciled from the authoritative graph.

## Acceptance and authorization boundary

RFC-005 DQ-01～10 and RFC-005 overall are Accepted; Final Consistency Review is PASS. Accepted Decision text is Current Truth; historical Proposal alternatives do not authorize implementation.

Even though P-58A～P-67A are accepted, the following remain `NOT GRANTED`:

- dependency installation or exact version locking;
- Parser / Fragmenter / Embedding / Index / Retrieval / API / Frontend / Database / Migration implementation;
- ARP / TS-01～TS-05 execution or any Live Provider call;
- RFC-007 acceptance, Goal creation / activation or release.

## Outcome

P-58A～P-60A ACCEPTED AND ARCHIVED AS DEC-067. P-61A～P-63A ACCEPTED AND ARCHIVED AS DEC-068. P-64A～P-66A ACCEPTED AND ARCHIVED AS DEC-069. P-67A ACCEPTED WITH EXPLICIT MVP-0 STAGING AMENDMENT AND ARCHIVED AS DEC-070; P-67B / C REJECTED AS CURRENT DIRECTION. FINAL CONSISTENCY REVIEW = PASS. RFC-005 OVERALL ACCEPTED BY USER ON 2026-08-07. IMPLEMENTATION / SPIKE / LIVE CALL / GOAL ACTIVATION REMAIN NOT GRANTED.
