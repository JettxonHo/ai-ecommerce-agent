# DEC-068：采用 PostgreSQL-native、版本化且确定性的 Retrieval 基线

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-07
- **Decision Type:** Retrieval Architecture / Embedding and Index Versioning / Deterministic Planning and Fusion
- **Source:** Session-003；用户明确接受 `P-61A / P-62A / P-63A`
- **Related Issue:** [#56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56)
- **Related PR:** [#57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)

## Context

RFC-002 已将 PostgreSQL 确立为业务 Current Truth，并把 Retrieval Index 定义为可重建的非权威派生层。DEC-067 又冻结了 Source / Source Version / Task Source Association / Derived Artifact、格式感知 Fragment 与 Source Set manifest。仍需决定首个 Goal 的词法与向量拓扑、Embedding / Index 如何版本化，以及 Planner、Fusion、候选上限与 Reranker 的默认边界。

首个 Goal 是本地单工作区演示，需要同时处理中文、英文和 SKU / 型号等 identifier-heavy 内容，但没有证据支持从第一天引入外部搜索服务、ANN、第二 Embedding Provider、LLM Query Rewrite 或强制 Reranker。

## Decision

### 1. PostgreSQL-native Derived Retrieval Plane

- Retrieval 使用已接受的同一 PostgreSQL Service；权威 Source / Evidence 图与 Retrieval-owned derived tables / schema 职责分离。Retrieval Index 可从权威 Fragment 与可读组件版本重建，不成为 Business Current Truth。
- Structured Direct Read、Exact ID / Key Lookup 与 Bounded Document Read 优先。精确 identifier 使用确定性 equality / prefix lane，不交给模糊或语义匹配替代。
- 词法候选使用语言适配的 PostgreSQL `tsvector` + GIN；对 CJK 或 identifier-heavy 内容提供有界 `pg_trgm` + GIN lane。具体 tokenizer、language configuration 与 trigram threshold 仍须由固定 Retrieval Evaluation 证明。
- 语义候选使用 `pgvector`。首个 Goal 以经过完整过滤的 exact nearest-neighbor 为基线；HNSW / IVFFlat 不默认启用。只有实测延迟与 filtered recall 证明必要、且 Scope isolation 仍可验证时，才可通过独立 Issue / PR 提出 ANN。
- Task、固定 Workspace、TaskSourceAssociation、SourceSetVersion、Source Scope、Product / Competitor identity、Source Version 与 availability / eligibility 必须共同形成 SQL authorized candidate relation，并在 lexical / vector ranking 前生效。禁止先广泛召回再由应用层删除不允许候选。

### 2. One Versioned Embedding Profile and Immutable Index Generations

- Retrieval 定义窄型 Embedding Port；首个 Goal 只允许一个 OpenAI Embeddings Adapter / active profile，不提供第二 Provider 或自动 Failover，也不允许业务模块直接调用 Provider SDK。
- RFC-005 最终闭合时必须依据当时官方兼容证据冻结 exact model identifier 与 output dimensions；Implementation Agent 不得临场选择或修改。该最终证据项尚未由本决定填充。
- `EmbeddingProfileVersion` 使用可读字段描述 provider family、model identifier、dimensions、distance / normalization policy、input-normalization version 与 batching policy；不包含 Secret，也不是用户业务状态。
- 每个 lexical / vector `RetrievalIndexEntry` 引用精确 Fragment、Source Version、Derived Artifact / Fragmenter version、index generation 与适用 profile。一次 Retrieval Run 的同一 channel 不混合不兼容 profile 或 vector dimensions。
- reparse、refragment、model 或 profile change 创建新的 immutable index generation。新 generation 旁路构建；只有 expected / present / missing / extra entry set 对账完成且代表性 Retrieval checks 通过后，才原子切换 current-generation pointer 或等价 eligibility reference。部分或失败 generation 不参与查询。
- Source remove / replace / restriction 先通过权威 eligibility 立即排除，即使物理 index cleanup 尚未完成。历史 Retrieval Run 保留 generation / profile reference；旧 generation 的清理由后续 retention 规则决定。
- 对账使用可读 identity、version 与 entry set，不新增 package digest、Hash / SHA-256 或通用完整性平台。

### 3. Deterministic Direct-first Planning and RRF

- Retrieval Planner 使用版本化、规则驱动的 strategy catalog：`direct`、`exact`、`bounded_document`、`lexical`、`semantic`、`hybrid`。Direct / Exact / Bounded 能满足请求时不启动相关性检索。
- 首个 Goal 不使用 LLM Query Rewrite。Query 由 retrieval purpose、Skill / user query、结构化 aliases 与 exact identifiers 确定性构造；exact identifiers 逐字保留。未来引入 LLM rewrite 必须以评测证据和 RFC amendment 为前提。
- Lexical 与 Semantic channel 使用同一 authorized candidate relation，保留 channel rank / matched query，并按稳定 Fragment identity 去重。Hybrid 使用 Reciprocal Rank Fusion（RRF），禁止直接相加不同量纲 raw scores。
- Seed configuration 固定为：最多 4 个确定性 query variants；每个 retrieval channel 最多 20 个 candidates；RRF rank constant 为 60；Fusion 后最多向 Coverage / Evidence Package 返回 12 个 Candidate Fragments。
- 上述数字是可版本化的运行候选边界，不是 Evidence strength、Dataset frequency、Rubric 分数或自动接受阈值。固定评测集在实现激活前若证明需调整，必须形成可审阅的文档变更，不由实现 Agent 静默修改。
- 首个 Goal 不配置 baseline Reranker。只有确定性 Planning + RRF 在已接受评测集上存在实质相关性缺陷时，才可单独提案；Reranker 只能重排已授权候选并可回退到 Fusion。
- Zero eligible / relevant result 返回 `insufficient_information`。Semantic lane 失败只可显式降级到适用的 Direct / Exact / Lexical lane；Fallback 不扩大 Scope、不改变 SourceSetVersion，也不把 rank 转成 Formal Evidence。

## Alternatives Considered

### FTS-only + ANN from Day One

词法只有一条路径且向量一开始即使用 approximate index，表面组件更少，但 CJK / identifier-heavy recall 风险未解决，ANN filter / recall 复杂度也早于本地 MVP 的实际规模证据，因此不采用。

### External Search / Vector Service + Multiple Embedding Providers

外部平台和 Provider failover 提供更强扩展性，却增加第二一致性平面、凭证、部署、跨服务 Scope filter 以及不可比向量空间；首个 Goal 没有相应可用性或规模需求，因此不采用。

### Mutable Index + LLM Planner + Mandatory Reranker

原地改写 index、动态 LLM Query Planning 和每次 Rerank 看似灵活，但会混合版本、降低可复现性、增加模型调用和失败路径，也让候选预算与 Scope 行为难以独立验证，因此不采用。

## Reason

该方案用已接受的 PostgreSQL 边界覆盖首个 Goal 的 exact、中文 / identifier-heavy lexical 与 semantic needs，同时把可重建 Index 与权威 Source / Evidence 图明确分开。确定性 Planner、RRF、有限候选和无 baseline Reranker 使行为可复现、可测试且与演示负载相称；ANN、LLM rewrite 与额外模型仅在真实证据出现后再讨论。

## Consequences

- RFC-005 DQ-04～06 已闭合；DQ-07～10 与 RFC-005 整体仍未接受。
- PostgreSQL 扩展、精确 package / extension version、Embedding exact model / dimensions、tokenizer / threshold 与性能目标仍不得由实现 Agent 决定；其中 model / dimensions 必须在 RFC-005 最终闭合时明确。
- Side-by-side generation 会短期占用额外存储，但提供可审阅的切换、回滚与历史解释能力。
- exact nearest-neighbor 是首个 Goal 的正确性基线；ANN 不是被禁止，而是必须由规模和质量证据解锁。
- Retrieval rank 仍只解释召回，不成为 Fact confidence、Evidence strength、QC 或 Human approval。

## Relationships

- **Amends [DEC-032](dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)：** 选择 PostgreSQL-native lexical / vector topology、RRF、确定性无 LLM rewrite 的首 Goal Planner、candidate bounds 与 no-baseline-reranker；其 Direct-first、mandatory filtering 与 Candidate / Formal Evidence 边界保持有效。
- **Extends [DEC-067](dec-067-versioned-source-intake-and-format-aware-fragment-contract.md)：** 将版本化 Derived Artifact 延伸到 Embedding Profile、Retrieval Index Entry 与 immutable generation。
- **Complements [RFC-002](../rfcs/rfc-002-persistence-and-transaction-architecture.md)：** Index 仍是非权威、可重建派生层，PostgreSQL 仍是权威身份 / eligibility 来源。
- **Complements [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)：** generation build / reconciliation 的耐久执行仍服从既有 Worker、Retry、Cancel 与 Commit Fence。
- **Complements [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)：** Embedding 使用同 Provider family 但独立窄 Port / Profile；不改变 Responses Model Runtime Port 或增加第二 Provider。
- **Conforms to [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 不提前建设 ANN、Reranker、多 Provider、通用完整性或不现实测试矩阵。
- **Extended by [DEC-069](dec-069-authoritative-retrieval-scope-referenced-evidence-and-explicit-degradation.md)：** 后续已闭合 server-derived Scope、公共投影、RetrievalRun / EvidencePackage、Formal Evidence commit、evaluation 与 degraded behavior；本决定形成时的 DQ-07～09 pending 状态作为历史保留。
- **Input to [RFC-005](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md)：** 接受 DQ-04～06，并开放 DQ-07～09 的策划讨论。

## Authorization Boundary

本决定只授权 Decision、RFC、Current Truth、Readiness、Testing 与 Traceability 文档同步：

- 不接受 RFC-005 整体，不授权合并 PR #57 或关闭 Issue #56；
- 不授权安装 PostgreSQL extension / SDK / dependency，创建 Schema、Migration、Index、Embedding、Retrieval Runtime、API、Frontend、Fixture 或 Test Implementation；
- 不授权 Live Provider call、Retrieval Evaluation、Technical Spike、RFC-007、业务实现或长期 Goal；
- 下一 Gate 仅为 RFC-005 DQ-07～09 的 Scope / public transport、Retrieval Run / Evidence Package / Formal Evidence Link，以及 evaluation / degraded behavior 决策。

## Accepted From

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-61A / P-62A / P-63A；用户于 2026-08-07 明确回复“接受 P-61A、P-62A、P-63A”。
- [RFC-005 Proposal Round 2](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md#proposal-round-2)。
- GitHub：[Issue #56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56) / [Draft PR #57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)。
