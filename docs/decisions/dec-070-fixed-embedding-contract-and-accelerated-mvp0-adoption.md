# DEC-070：采用固定 Embedding 契约与快速 MVP-0 分阶段交付顺序

## Metadata

- **Status:** Accepted with explicit MVP-0 staging amendment — activation wording amended by [DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md)
- **Date:** 2026-08-07
- **Decision Type:** Retrieval Contract / Embedding Profile / Public API Catalog / Accelerated Delivery Gate
- **Source:** Session-003；用户明确接受 `P-67A`，并同时确认快速 MVP-0 Gate
- **Related Issue:** [#56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56)
- **Related PR:** [#57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)

> **Amendment notice（2026-08-08）：** MVP-0 技术分期保持不变。DEC-072 已提供全部重大 Proposal 与 Readiness Gate 闭合后的持续执行授权，因此不再要求闭合后重复固定启动口令。

## Context

DEC-067～069 已闭合 Source、Processing、Fragment、Retrieval topology、Scope、Evidence commit 与 evaluation。P-67A 需要冻结 exact Embedding Profile、Source / Evidence Operation catalog 与采用证据；与此同时，用户选择快速 MVP-0 纵向切片，明确要求先交付 Direct / Exact / PostgreSQL Lexical 支撑的核心业务闭环，并把 Embedding / Semantic / Hybrid、文本 PDF、多 Worker 与完整运维能力后移。

两项决定若不显式协调，会让实现 Agent 同时看到“Semantic / Hybrid 必须先于 Core Skill”与“MVP-0 暂缓 Semantic / Hybrid”两种顺序。本决定保留 P-67A 的目标契约，同时修订其对快速 MVP-0 的实施先后关系。

## Decision

### 1. Fixed target Embedding Profile

- RFC-005 的首个目标 Embedding Profile 固定为 Provider family `openai`、API family `embeddings`、model `text-embedding-3-small`、显式 `dimensions=1536`、`encoding_format=float` 与 cosine distance。
- 可读 Profile identity 为 `openai-text-embedding-3-small-1536-cosine-v1`；PostgreSQL vector slice 使用兼容 `vector(1536)`，exact semantic ordering 使用 pgvector cosine `<=>`。
- Provider response 不承诺 bitwise deterministic。边界只验证响应数量、1536 维、有限数值和请求顺序；PR 使用确定性 Embedding Port substitute，未来启用该 Slice 时只做一次 opt-in RC smoke。
- 不增加第二次应用层归一化、第二 Provider、ANN、Reranker、LLM Query Rewrite、Digest、Hash 或 SHA-256。未来改变 model / dimensions / distance / normalization 时创建新 Profile Version 与 immutable generation，不原地混合。

### 2. Fixed Source / Evidence public catalog

RFC-004 的单一 `contracts/openapi/openapi.yaml` 在相应 Contract Issue 中增加以下 RFC-005-owned Operation：

| Family | First-Goal target operations |
|---|---|
| Source intake | `POST /api/v1/tasks/{taskId}/source-intakes`; `GET /api/v1/source-intakes/{sourceIntakeId}` |
| Source association / versions | `GET /api/v1/tasks/{taskId}/source-associations`; `GET /api/v1/source-associations/{sourceAssociationId}`; `GET /api/v1/source-associations/{sourceAssociationId}/source-versions`; `GET /api/v1/source-versions/{sourceVersionId}` |
| Formal Evidence | `GET /api/v1/tasks/{taskId}/evidence-links`; `GET /api/v1/evidence-links/{evidenceLinkId}` |

- Source intake 支持 `application/json` 或 bounded `multipart/form-data`；需要 `Idempotency-Key`。Envelope-invalid 使用 RFC-004 Problem Details；合法同批项目使用 typed per-item result。
- 首次全同步接受返回 `201`；存在已登记异步处理返回 `202` + immutable receipt + `Location`；same-key / same-input committed replay 返回 `200` + 同一 receipt。
- Source association、Source version 与 Evidence Link collection 使用 opaque cursor keyset pagination，默认 `20`、最大 `50`。公共投影与禁止暴露项以 DEC-069 为准。
- Schema family 固定为 Source intake / receipt / item result、Source association / version / six-state processing、cursor page 与 locator-discriminated Evidence Link family；复用 RFC-004 identity、revision、Capability、Problem、Idempotency 与 fixed-workspace 约定。

### 3. Accelerated MVP-0 staging amendment

- **目标契约不缩窄，交付顺序分层。** 快速 MVP-0 先实现结构化表单、手工文本、TXT / Markdown 与评论 CSV；文本型 PDF 作为 additive capability 后移到 MVP-1。
- MVP-0 Retrieval 只启用 Direct、Exact 与 PostgreSQL Lexical，并继续使用同一 server-derived SQL authorized candidate relation、Source Set Version、Evidence Validator 与 Formal Evidence atomic commit。Core Skills 可以消费经过验证的这一有限 Retrieval Profile，不必等待 Embedding / Semantic / Hybrid。
- `text-embedding-3-small` Profile 与 vector generation 契约现在冻结，但实现、pgvector compatibility slice、Semantic / Hybrid evaluation 与 RC Embedding smoke 后移到 MVP-1；在完成对应证据前 Capability 不得宣称 Semantic / Hybrid 可用。
- MVP-0 仍先落单一 OpenAPI authority、真实 PostgreSQL、Task / Source graph、四个核心业务阶段、单 Worker LangGraph、Human Review、双 Brief、Markdown Export 与浏览器 E2E。Frontend 只消费服务端 Capability 和真实状态，不模拟被后移的能力。
- 本分阶段顺序只修订 P-67A 原始“Semantic / Hybrid 必须先于任何 Core Skill 消费”的要求；不修订 Scope、Evidence、版本、错误、幂等、Human Review 或测试质量底线。

### 4. Bounded evidence and stop conditions

- MVP-0 必备证据：OpenAPI / generated-client clean diff；真实 PostgreSQL 的 revision、idempotency、authorized Direct / Exact / Lexical 与 atomic Evidence commit；确定性四阶段业务测试；Review / recovery；浏览器主链 E2E；一次真实 Responses Provider smoke。
- TS-01 / TS-03 不先扩建为大型独立 Spike，而是在对应 Persistence / Workflow foundation Issue 中执行 stop-first compatibility slice。失败即停止依赖实现并回到架构 Gate。
- Embedding / pgvector 证据在 MVP-1 Semantic / Hybrid Issue 开始时执行。模型不可用、不能返回 1536 维、pgvector 不兼容、pre-ranking Scope filter 失败或代表性硬门禁失败时必须停止，不得降低正确性标准。
- 不因快速交付增加低概率防御矩阵、通用安全平台或机械质量总分。

## Alternatives Considered

### 完成完整 Retrieval 与全部 Readiness 后才启动任何 Core Skill

契约最完整，但继续延迟用户看到可运行闭环；许多风险与 Direct / Exact / Lexical 主链无直接关系，因此不采用为 MVP-0 Gate。

### 抛弃已接受架构制作一次性内存原型

最快展示，但绕开 PostgreSQL、LangGraph、版本、Review 与 Evidence，后续需要重写且不能作为可持续 MVP，因此不采用。

### 实现 Agent 临场决定模型、接口与交付顺序

表面灵活，但会重新打开 P-62A / P-67A 的高成本契约并破坏并行任务交接，因此不采用。

## Consequences

- RFC-005 DQ-01～10 已由 DEC-067～070 全部闭合，具备最终一致性审查条件；RFC-005 整体仍需用户单独接受。
- 快速 MVP-0 可以在不实现 Embedding / Hybrid 与 PDF 的情况下交付核心价值闭环，但不得宣称完整 Retrieval 或最终 Demo MVP 已完成。
- MVP-1 必须在相同公共契约内补齐 text PDF、Embedding / Semantic / Hybrid 与相关评测；若需改变契约，必须另行 Decision。
- 该分层会降低首个可用版本的语义召回能力；系统必须通过 Capability 与 Evidence limitation 诚实表达，而不是静默伪装完整。

## Relationships

- **Extends [DEC-068](dec-068-postgresql-native-versioned-and-deterministic-retrieval-baseline.md)：** 冻结 exact active Embedding Profile。
- **Extends [DEC-069](dec-069-authoritative-retrieval-scope-referenced-evidence-and-explicit-degradation.md)：** 冻结公共 Operation / Schema family 与采用证据。
- **Amends P-67A adoption order：** 快速 MVP-0 允许经过同一 Scope / Validator / atomic commit 的 Direct / Exact / Lexical Profile 先供 Core Skills 使用；Semantic / Hybrid 后移。
- **Amends [DEC-038](dec-038-rfc-planning-and-dependency-order.md) 的开发前 Gate：** 只在快速 MVP-0 范围内，以精简 Readiness Review 代替全部 Readiness Artifact 先行完成；未被替代的最终质量与人工 Gate 保持有效。
- **Conforms to [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 保留真实风险门禁，不建设过度防御。

## Authorization Boundary

本决定只授权继续完成 RFC-005 Final Review、最小 RFC-007、MVP-0 Development Plan / Testing Strategy / Goal 文本与精简 Readiness Review：

- 不接受 RFC-005 整体，不授权合并 PR #57 或关闭 Issue #56；
- 不创建实际 Goal，不创建生产 Issue / Branch，不安装依赖，不执行 Spike，不调用 Live Provider；
- 不编写 OpenAPI Artifact、数据库、Migration、Workflow、Retrieval、API、Frontend 或业务代码；
- 只有完整快速策划包展示后，用户再明确发出“进入 MVP-0 Goal”指令，开发授权才可能开启。

## Accepted From

- 用户于 2026-08-07 明确回复：“确认接受快速 MVP-0 Gate；接受 P-67A；允许完成 RFC-005 最终审查，并按最小范围策划 RFC-007、Development Plan、Testing Strategy、Goal 与精简 Readiness Review。完成展示前不启动开发。”
- [RFC-005 P-67A](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md#p-67a--contract-first-closure--text-embedding-3-small-1536-cosine--bounded-verification推荐)。

## Subsequent RFC Outcome

RFC-005 Final Consistency Review 通过后，用户于 2026-08-07 明确接受 RFC-005 整体，并授权合并 PR #57、关闭 Issue #56、继续最小 RFC-007 与快速 MVP-0 策划包。该后续接受没有改变本 Decision 的 MVP-0 / MVP-1 分期，也没有授权实现、Spike、Live Provider 或实际 Goal。
