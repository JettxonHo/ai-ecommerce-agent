# Hybrid Retrieval and Evidence Runtime — 概念 Specification

> **Status: FROZEN BY DEC-067～070；RFC-005 ACCEPTED 2026-08-07**
> 来源决定：[DEC-032](../../decisions/dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)、[DEC-067](../../decisions/dec-067-versioned-source-intake-and-format-aware-fragment-contract.md)、[DEC-068](../../decisions/dec-068-postgresql-native-versioned-and-deterministic-retrieval-baseline.md)、[DEC-069](../../decisions/dec-069-authoritative-retrieval-scope-referenced-evidence-and-explicit-degradation.md) 与 [DEC-070](../../decisions/dec-070-fixed-embedding-contract-and-accelerated-mvp0-adoption.md)（Accepted）。DEC-067～069 冻结 Source / Retrieval / Evidence 基线；DEC-070 冻结 exact Profile / catalog 并定义快速分阶段采用。
> DEC-070 已冻结 `text-embedding-3-small` / 1536 / cosine 与公共 catalog，并将快速 MVP-0 限于 Direct / Exact / Lexical；text PDF、Embedding / Semantic / Hybrid 后移 MVP-1。本文件仍不是物理实现 Schema。
> Development Status: **NOT READY**。

---

## §0 来源与范围

本 Specification 把 DEC-032 已确认的 Hybrid Retrieval and Evidence Runtime Architecture 整理为结构化概念规格。Hybrid Retrieval and Evidence Runtime 是**跨 Skill 的共享运行架构层**，服务于所有 Skill（Product Intake / Customer Insight / Product Positioning / Marketing Brief / Xiaohongshu Adapter）与 Evidence Validator：

```text
Skill Retrieval Request
→ Hybrid Retrieval and Evidence Runtime
→ Candidate Fragments + Evidence Package
→ Skill Analysis
→ Evidence Validator
→ Formal Evidence Links
```

承接 DEC-008（分级证据）、DEC-009（阶段级失效）、DEC-013（任务级 task_id 隔离）、DEC-014（按需混合 RAG + 分层数据访问，**Amended by DEC-032**）、DEC-015（Skill 显式声明检索依赖）、DEC-023（检索以结构化 IO 被 Skill / Node Adapter 调用）、DEC-024（版本化 Domain Objects + Current Truth Pointers）、DEC-025（Source / Source Version / Fragment / Evidence Link + Source Scope 隔离 + Evidence Package + Evidence Validator）、DEC-026 / 027 / 028 / 030 / 031（各 Skill / Adapter 的允许 Source Scope 与证据边界）。

本 Runtime 输出 **Candidate Fragments + Retrieval Logs + Reproducible Evidence Package**，是 Skill 的可复现证据输入，**不**生成 Formal Evidence Link / Fact / Insight / Positioning / Approved Strategy / Execution Brief。

---

## §1 Purpose

在严格限定任务 / 权限 / 商品身份 / 来源范围 / 来源版本的前提下，为 Skill 提供可复现、可解释、可校验的候选证据输入（Candidate Fragments + Evidence Package），并保证检索结果不自动成为正式证据、不泄露跨任务或跨商品身份的私有资料、不用 Top-K 召回结果推断总体频率。

核心原则：**能直接读取时不使用检索；需要检索时先限定任务 / 权限 / 商品身份 / 来源范围 / 来源版本，再选择 Lexical / Semantic / Hybrid。**

---

## §2 Responsibilities

- 按需提供候选证据（Candidate Fragments）；
- 确定性规划检索方式（Deterministic Retrieval Planner）；
- 强制 Permission / Task / Product Identity / Source Scope / Source Version 过滤；
- 保证可复现性（同 Plan + 同 Source Set Version + 同组件版本 → 稳定 Candidate identity / order 与当时 Evidence Package references；不宣称 Provider output bitwise deterministic）；
- 保证可解释性（dev / debug / eval 能回答「为什么这个 Fragment 被召回 / 排除」）；
- 记录检索日志（RetrievalRun）；
- 装配可复现 Evidence Package；
- 报告 Evidence Coverage 与 Evidence Limitations。

---

## §3 Non-responsibilities

- 不做业务分析 / 战略判断 / 文案生成（各 Skill 职责）；
- 不创建 Formal Evidence Link / Fact / Insight / Positioning / Approved Strategy / Execution Brief（须经对应 Validator 与业务事务）；
- 不计算正式总体频率 / 统计比例（须由确定性统计服务基于完整可计数数据集产生，承接 DEC-027）；
- 不决定最终 Source Scope / Product Scope / Source Set Version / 访问权限（由业务身份与确定性逻辑前置确定，Runtime 仅执行过滤）；
- 不自行选择 exact Embedding model / dimensions、tokenizer / threshold、ANN 参数、Chunk Size / Overlap、缓存技术或运维阈值；这些只能由 RFC-005 final closure、固定评测证据、Testing Strategy 或 RFC-007 的相应权威冻结。

---

## §4 Retrieval Priority

不是每个请求都跑完所有层；Runtime 按以下优先级选择检索方式（前置能解决就不走后置）：

```text
1. Structured Direct Read      （结构化直读）
2. Exact ID / Key Lookup       （精确 ID / Key 查找）
3. Bounded Direct Document Read（有界直读）
4. Lexical Retrieval           （词法检索）
5. Semantic Retrieval          （语义检索）
6. Hybrid Retrieval            （混合检索）
7. Optional Reranking          （首个 Goal baseline 不启用）
```

优先级 1–3 为 **Direct 读取**（确定性、可完全复现、无相关性打分）；优先级 4–6 为 **Retrieval 检索**（基于相关性打分召回）；优先级 7 为可选增强。

---

## §5 Structured Direct Read

直接读取结构化字段 / 业务记录（如商品规格表、已存在的 Fact / Insight 记录、业务配置）。

- 确定性、可完全复现；
- 无相关性打分；
- 当所需信息已存在于结构化记录时，**不**使用检索。

---

## §6 Exact ID / Key Lookup

基于精确标识符查找：SKU / 型号 / 认证编号 / Fragment ID / Source Version ID / Record ID。

- 精确匹配，确定性；
- 精确标识符必须**逐字保留**，不得改写、翻译或泛化；
- 优于相关性检索。

---

## §7 Bounded Direct Document Read

在限定 Document / Record 范围内直接读全文（例如某份 PDF、某条评论记录的完整内容）。

- 范围由业务身份与 Source Set Version 限定；
- 确定性、可复现；
- 不引入跨范围相关性召回。

---

## §8 Lexical Retrieval

词法检索使用 PostgreSQL-native derived plane：语言适配的 `tsvector` + GIN，并为 CJK / identifier-heavy 内容提供有界 `pg_trgm` + GIN lane。

- 基于关键词 / term 匹配；
- 返回 `lexical_rank`、`matched_terms[]`；
- 精确标识符必须逐字保留；
- 仍须应用强制元数据过滤。

---

## §9 Semantic Retrieval

语义检索（向量相似检索）。

- 基于语义相似；
- 返回 `semantic_rank`；
- 使用 `pgvector` filtered exact nearest-neighbor 作为首个 Goal 基线；HNSW / IVFFlat 只有在评测证明 latency / recall 需要且 Scope isolation 仍安全时才可另行提案；
- exact OpenAI Embedding model identifier / dimensions 尚待 RFC-005 final closure；
- 不可用时回退 Structured + Lexical（见 §27）。

---

## §10 Hybrid Retrieval

Lexical + Semantic 融合检索。

- 调用 §8 + §9；
- 经 §11 Fusion 合并；
- 记录 `fused_rank`；
- 使用 RRF，保留每个 channel 的原始 rank；不直接组合 raw scores。

---

## §11 Score and Fusion Boundary

- **不得直接相加不同量纲分数：** BM25（词法）与 Vector similarity（语义）属不同量纲，**不得**直接数值相加。
- **采用 Reciprocal Rank Fusion：** RRF rank constant seed 为 60；保留原始各通道排名、matched query 与可读 Fusion version。
- **候选边界：** 每通道最多 20 个 candidates，Fusion 后最多返回 12 个 Candidate Fragments；这些不是 Evidence strength、统计频率或机械验收分。

---

## §12 Retrieval Request

RetrievalRequest 为概念结构（非最终 API Schema）：

```text
- task_id
- workspace_id
- skill_name
- retrieval_purpose
- query_text
- exact_identifiers[]          （SKU / 型号 / 认证编号 / Fragment ID / Source Version ID 等）
- required_source_scopes[]     （current_product / current_product_customer / ... ）
- allowed_source_set_version_id
- required_evidence_types[]
- time_constraints
- requested_output
```

---

## §13 Deterministic Retrieval Planner

Planner 接收 RetrievalRequest，输出 RetrievalPlan（概念字段）：

```text
- strategy
- structured_queries[]
- lexical_queries[]
- semantic_queries[]
- mandatory_filters
- optional_filters
- fusion_required
- reranking_allowed
- coverage_requirements
- fallback_strategy
```

- Planner 决定**检索方式与边界**，不是业务结论；
- Plan 可复现、可版本化（`retrieval_plan_version`）；
- 首个 Goal Planner 不调用 LLM；使用最多 4 个确定性 query variants，并逐字保留 exact identifiers。

---

## §14 Query Planning Boundary

- 首个 Goal 不使用 LLM Query Rewrite；Query 由 purpose、Skill / user query、结构化 aliases 与 exact identifiers 确定性构造。
- Exact identifiers 必须逐字保留，不得改写、翻译或泛化。
- 未来引入 LLM rewrite 必须由固定评测证明必要并形成 RFC amendment；即使引入，LLM 也不得决定 Task / Workspace / Permission / Source Scope / Product Scope / SourceSetVersion。

---

## §15 Mandatory Metadata Filters

每次检索必须在召回前 / 召回中应用以下强制过滤（概念维度）：

```text
- task_id
- workspace_id
- permission_scope
- source_scope
- product_id
- competitor_id
- source_set_version_id
- source_version_status
- document_or_record_status
- fragment_status
- language
- time_range
```

核心原则：**一个高度相关但不属于当前任务或当前允许 Source Set 的 Fragment，必须被排除，而不是仅降低排名。**

---

## §16 Pre-filter and Post-filter Boundary

- 过滤在召回前 / 召回中生效，不是「先全召回再删除」；
- 强制过滤应在索引层 / 查询层前置应用；
- Direct / Exact / Lexical / Semantic / Hybrid 复用同一 PostgreSQL SQL authorized candidate relation；应用层 post-filter 不能作为隔离正确性路径。

---

## §17 Current Product and Competitor Isolation

**Source Scope 概念集合：**

```text
- current_product
- current_product_customer
- competitor_product
- competitor_customer
- manual_input
- platform_policy
- business_context
```

**不得默认 all_product_sources。** 每个 Skill 只能看到其被允许的 Source Scope 子集。

**各 Skill 允许 Scope（概念，承接各 Skill Contract）：**

| Skill | 允许 Source Scope |
|---|---|
| Product Intake & Fact Extraction | `current_product` + `manual_input` |
| Customer Insight Analysis | `current_product_customer` + `competitor_customer`（scope 保留） |
| Product Positioning | 当前 facts / insights + 竞品 facts / insights（身份不合并） |

每个 Candidate Fragment 必须保留 `source_scope` / `product_id` / `competitor_id`。

---

## §18 Source Set Version Boundary

每个 Skill 分析的来源范围由 **SourceSetVersion** 固定：

- **Superseded：** 默认排除；
- **Deleted：** 排除；
- **Restricted：** 返回权限错误，不得静默忽略；
- **Processing not complete：** 不作为完整可计数数据集使用；
- **Source Set 变化：** 旧 Evidence Package 不再是当前输入；须基于新 Source Set Version 重新装配。

---

## §19 Candidate Fragment

Candidate Fragment 为概念对象（非最终 Schema）：

```text
- fragment_id
- source_id
- source_version_id
- source_scope
- product_id
- competitor_id
- document_or_record_id
- record_id
- locator
- content
- retrieval_channels[]
- lexical_rank
- semantic_rank
- fused_rank
- rerank_score
- matched_terms[]
- query_ids[]
- availability_status
- retrieval_run_id
```

**排名 / 分数只解释「为何被召回」，不是 Fact Confidence / Evidence Strength。** 相关性高 ≠ 证据强、≠ 事实可信。

---

## §20 Deduplication

- 按稳定 `fragment_id` 去重；
- 合并时保留 `retrieval_channels[]` / `matched_queries[]` / 各通道 `channel_ranks`；
- 同一 Fragment 经多条 Query 召回 ≠ 多条独立证据；
- 用户评论类去重须保留 `record_id`，不得合并不同评论记录（否则破坏可计数性）。

---

## §21 Reranking

- 首个 Goal baseline 不启用 Reranking；只有固定评测证明 deterministic Planner + RRF 存在实质相关性缺陷时才可另行提案；
- Reranker 只能对「已允许」的 Candidate Fragments 重排；
- 不得新增来源、不得修改 Scope / Version、不得创建 Evidence Link；
- 未来获准使用 Reranker 时必须记录其模型与版本；
- Reranker 失败 → 回退到 Fusion 结果；
- 是否引入 Reranking 由 Retrieval Evaluation 决定。

---

## §22 Evidence Package Construction

Evidence Package 是 Skill 的可复现证据输入。构建流程（概念步骤）：

```text
1.  接收 Skill Retrieval Request
2.  Deterministic Retrieval Planner 生成 RetrievalPlan
3.  应用 Permission / Task / Product / Source Scope / Source Version 过滤
4.  执行 Direct Read / Exact Lookup / Lexical / Semantic / Hybrid
5.  召回 Candidate Fragments
6.  去重（按 fragment_id，保留通道与 record_id）
7.  RRF Fusion（按 fragment_id 去重并保留 channel ranks）
8.  首个 Goal 不 Rerank；未来获准时失败回退 Fusion
9.  Coverage 检查
10. Conflict 检查（记录 known_conflicts[]）
11. 装配 Evidence Package
12. 固定 Source Set manifest、RetrievalPlan / RetrievalRun identity 与可读组件版本
13. 返回 Skill
```

**EvidencePackage（概念字段）：**

```text
- evidence_package_id
- task_id
- skill_name
- purpose
- retrieval_plan_version
- source_set_version_id
- retrieval_run_ids[]
- candidate_fragments[]
- verified_facts[]
- dataset_statistics[]
- known_conflicts[]
- coverage_summary
- evidence_limitations[]
- generated_at
```

Evidence Package 不新增或公开 `package_hash`、SHA-256 或 client-visible digest；其可复现性由结构化 identity / version references 解释，接受 / 质量 / Evidence strength 不由 digest 推断。

---

## §23 Evidence Coverage

Evidence Coverage 不得只展示 Top 10。必须检查并报告：

- 子问题是否都有证据；
- supporting 与 contradicting 证据是否都召回；
- 是否只有单一来源（single-source）；
- 是否全部来自同一 Record；
- 是否召回全部竞品资料（all-competitor）；
- 是否缺失当前商品资料；
- 是否混入旧版本来源；
- 明确的证据缺口（gaps）。

---

## §24 Dataset Analysis Boundary

- **检索（Retrieval）回答：** 哪些 Fragment 与问题相关？
- **数据集分析（Dataset Analysis）回答：** 某主题下有多少条独立 Record？
- 正式统计需要 Dataset Version + 完整 Record 集合 + 确定性计数；
- 禁止用 Top-K 召回结果计算比例 / 频率 / 共识 / 市场份额 / 分布（承接 DEC-025 / DEC-027）。

---

## §25 Retrieval Logging

- 每次检索记录一条 immutable RetrievalRun（Plan / Source Set reference、授权过滤摘要、query identities、组件 / generation references、candidate summary、degraded outcome、权威时间与 correlation reference）；
- 必须记录适用的 Embedding Profile / index generation / lexical profile / Fusion version；未来获准 Reranker 时才记录其版本；RetrievalRun 是运行解释记录，不是 Business Current Truth；
- 本文件暂不选择具体检索日志技术。

---

## §26 Explainability

- 在 dev / debug / eval 中必须能回答：**「为什么这个 Fragment 被返回？为什么被排除？」**
- 解释至少包含：命中检索通道、命中 Query、命中 term、应用的过滤条件、各通道排名。

---

## §27 Failure and Degraded Modes

- **Semantic Retrieval 不可用：** 只运行适用的 Direct / Exact / Lexical，记录 `semantic_retrieval_unavailable` 并传播 Evidence Limitation。
- **Lexical Retrieval 不可用：** Direct / Exact 保持；Semantic 只有在 authorized candidate relation 与 exact identifier coverage 均成立时继续，否则返回 limitation / `insufficient_information`。
- **Reranker 不可用：** 首个 Goal baseline 本就不启用；未来获准后失败才回退 Fusion 结果。
- **Vector Index 不完整：** 不切换该 generation；继续使用仍兼容且 eligibility-current 的上一 generation，或仅使用安全适用的 Direct / Exact / Lexical。没有安全 generation 时返回 temporary unavailable / actionable recovery。
- **Source Processing 待完成：** 等待 / 返回 incomplete 状态，不作为完整可计数数据集。
- **Zero Results（零召回）：** 返回 `insufficient_information`，模型不得虚构答案。

---

## §28 Formal Evidence Link Transaction Boundary

Formal Evidence Link 仅在 Skill 输出通过 Evidence Validator 后才创建。事务流程（概念步骤）：

```text
1.  Skill 基于 Evidence Package 产出结论（含 fragment_id 引用）
2.  Evidence Validator 校验引用（ID 存在 / 属当前 task / 来自允许 Source Scope / Source Version 可用 / 属本次候选 / 未重复 / 未失效 / Locator 存在）
3.  校验通过 → 进入事务
4.  创建 Formal Evidence Link（Versioned Domain Object ↔ Fragment）
5.  写入 Business Repository（承接 DEC-024 / DEC-025）
6.  记录审计
7.  提交事务（幂等）
8.  任一步失败 → 不创建 / 不更新 Current Truth / 不写部分对象
9.  失败时：Candidate Fragment + Retrieval Log 可保留；Skill 可重跑；Retrieval 可重新规划
```

**边界：** Evidence Package = 可复现的 Skill 输入；Formal Evidence Link = 正式关系。Evidence Package 不进 Current Truth；Formal Evidence Link 进 Current Truth。

---

## §29 Cache Boundary

- **可缓存：** Source Version 解析、Fragment Embedding、同一 Retrieval Plan 的结果、Evidence Package。
- **缓存键必须包含：** `task_or_workspace_scope` / `source_set_version_id` / `query` / `retrieval_strategy` / `filter_set` / `component_versions`。
- **Source Set Version 变化后不得返回旧缓存。**
- 本文件**不**选择具体缓存技术。

---

## §30 Evaluation Metrics

- **Behavioral Hard Gates（任一失败阻断对应生产 Slice）：**
  - Cross-task / Cross-scope leakage
  - Current Product / Competitor leakage
  - Stale / unavailable / non-current-generation candidate
  - Top-K frequency extrapolation
  - Fabricated answer on zero retrieval
  - Exact identifier mutation / loss
  - Nondeterministic candidate identity / order for the same manifest + plan + component tuple
  - Formal Evidence created before Validator + atomic commit
- **Retrieval Quality：** 代表性 query 的 Recall@K、reciprocal rank、Coverage / counter-evidence 与人工 `PASS / FAIL` 共同判断；K / threshold 待固定 Fixture 内容形成后由 Testing Strategy 冻结，不合成机械总分。
- **Runtime Metrics：** 延迟、成本、降级频率。
- **Business Metrics：** 下游 Skill 结论可追溯率、Evidence Validator 通过率。

---

## §31 Evaluation Dataset

- **Exact Fact Query：** 精确事实查询（SKU / 型号 / 认证），验证 §5 / §6。
- **Semantic Customer Query：** 语义用户反馈查询，验证 §9。
- **Hybrid Query：** 词法 + 语义混合查询，验证 §10 / §11。
- **Scope Isolation Query：** 范围隔离查询（竞品冒充当前商品 / 跨任务），验证 §15 / §17。
- **Counter-evidence Query：** 反向证据查询，验证 §23。

---

## Open Questions

以下为 DEC-067～070 后仍**未确认**的实施参数，须由 Testing Strategy、Goal Issue 或后续证据决定：

- PostgreSQL extension / package exact versions、tokenizer 与 trigram threshold；
- ANN 是否需要及其参数（默认不启用）；
- Reranker / LLM Query Rewrite 是否由未来评测解锁（默认不启用）；
- Chunk Size / Chunk Overlap；
- 缓存技术（Cache Technology）；
- MVP-1 Semantic / Hybrid 的实施 Issue 与启用时点（目标 Profile 已冻结）；
- 性能目标（延迟 / 成本阈值）；
- 最终字段名称、Schema、枚举；
- 最终错误代码；
- 检索日志的具体技术；
- RetrievalPlan / RetrievalRequest / Candidate Fragment / EvidencePackage 的最终 Schema。

在 **Workflow Runtime Failure Recovery, Retry and Observability Contract** 议题确认前，**不**实现正式 Retry Middleware、Tracing、Alerting 或 Recovery Worker。
