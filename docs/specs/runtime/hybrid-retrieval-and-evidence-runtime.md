# Hybrid Retrieval and Evidence Runtime — 概念 Specification

> **Status: CONCEPTUAL（概念）**
> 来源决定：[DEC-032 — Hybrid Retrieval and Evidence Runtime 采用 Direct-first 检索、确定性检索规划、强制权限与版本过滤与可复现证据装配](../../decisions/dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)（Accepted，Runtime Architecture / Retrieval Architecture / Evidence Architecture，2026-07-29）。Amends DEC-014。
> 本文件是 DEC-032 的**概念结构化记录**，**不是最终实现契约**。所有字段名、枚举、Schema、阈值、算法、Prompt、模型均未确认。
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
- 保证可复现性（同 Plan + 同 Source Set Version + 同组件版本 → 复现 Skill 当时看到的证据输入）；
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
- 不选择具体 Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization / 融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制。

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
7. Optional Reranking          （可选 Reranking）
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

词法检索（如 BM25）。

- 基于关键词 / term 匹配；
- 返回 `lexical_rank`、`matched_terms[]`；
- 精确标识符必须逐字保留；
- 仍须应用强制元数据过滤。

---

## §9 Semantic Retrieval

语义检索（向量相似检索）。

- 基于语义相似；
- 返回 `semantic_rank`；
- Embedding 模型未确认；
- 不可用时回退 Structured + Lexical（见 §27）。

---

## §10 Hybrid Retrieval

Lexical + Semantic 融合检索。

- 调用 §8 + §9；
- 经 §11 Fusion 合并；
- 记录 `fused_rank`；
- Fusion 方法与权重未确认。

---

## §11 Score and Fusion Boundary

- **不得直接相加不同量纲分数：** BM25（词法）与 Vector similarity（语义）属不同量纲，**不得**直接数值相加。
- **可用 Rank Fusion 或 Score Normalization + Weighted Combination。**
- **融合方法须满足：** 可复现、可版本化、保留原始各通道排名（raw ranks）、可解释、可替换。
- 本文件**不**选择具体融合算法 / Score Normalization 方法 / 融合权重。

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
- Planner 可有限借助 LLM 做 Query Planning（见 §14）。

---

## §14 LLM Query Planning Boundary

- **LLM 可辅助：** 意图识别 / 子查询拆分 / 有限 Query Rewrite / 同义表达 / 主题查询候选。
- **LLM 不得决定：** `task_id` / `workspace_id` / Permission / Source Scope / Product Scope / Source Set Version / 是否允许跨任务检索。
- **Exact identifiers 必须逐字保留：** SKU / 型号 / 认证编号 / 数字 / 单位 / 品牌名 / Fragment ID / Source Version ID 在 Query Rewrite 中不得改写、翻译或泛化。
- **Query Rewrite 数量有确定性上限：** 不允许无限发散查询。
- **LLM 不接触访问范围控制。**

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
- 本文件**不**选择具体向量数据库实现；Pre-filter / Post-filter 的具体工程实现未确认。

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

- Reranking 是**可选增强**，不是 MVP 硬依赖；
- Reranker 只能对「已允许」的 Candidate Fragments 重排；
- 不得新增来源、不得修改 Scope / Version、不得创建 Evidence Link；
- 必须记录 Reranker 模型与版本；
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
7.  Fusion（Rank Fusion 或 Score Normalization + Weighted）
8.  Optional Reranking（失败回退 Fusion）
9.  Coverage 检查
10. Conflict 检查（记录 known_conflicts[]）
11. 装配 Evidence Package
12. 计算 package_hash
13. 记录 RetrievalRun / 组件版本
14. 返回 Skill
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
- package_hash
```

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

- 每次检索记录一条 RetrievalRun（Plan、过滤条件、组件版本、召回结果概要、时间）；
- 可记录检索组件版本（Embedding 版本 / 索引版本 / Reranker 版本 / Fusion 方法版本）；
- 本文件暂不选择具体检索日志技术。

---

## §26 Explainability

- 在 dev / debug / eval 中必须能回答：**「为什么这个 Fragment 被返回？为什么被排除？」**
- 解释至少包含：命中检索通道、命中 Query、命中 term、应用的过滤条件、各通道排名。

---

## §27 Failure and Degraded Modes

- **Semantic Retrieval 不可用：** 回退 Structured + Lexical，记录 `semantic_retrieval_unavailable`，传播 Evidence Limitation。
- **Lexical Retrieval 不可用：** 回退 Semantic，但精确标识符未被完整校验 → `valid_with_limitations` 或暂停。
- **Reranker 不可用：** Fusion 结果继续，不阻塞。
- **Vector Index 不完整：** 仅使用 Direct / Structured / Lexical，不得查询不完整索引。
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

- **Hard Reliability（6 项，全部目标 0%）：**
  - Cross-task / Cross-scope leakage
  - Current Product / Competitor leakage
  - Retrieval result treated as Formal Evidence
  - Top-K frequency extrapolation
  - Fabricated answer on zero retrieval
  - Stale Source Version used
- **Retrieval Quality：** Recall@K 等（K 值未确认）、Precision、Coverage 命中率。
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

以下为 DEC-032 明确**未确认**的项目，须由后续议题与评测决定（本文件不发明答案）：

- Embedding 模型；
- 向量数据库（Vector Database）；
- 词法搜索引擎（Lexical Search Engine）/ BM25 实现；
- Rank Fusion 算法；
- Score Normalization 方法与融合权重；
- Top-K 值（K 未确认）；
- Reranker 模型与是否引入；
- Chunk Size / Chunk Overlap；
- Query Rewrite 模型；
- 缓存技术（Cache Technology）；
- 索引刷新机制（Index Refresh Strategy）；
- 数据库 / API 框架；
- 性能目标（延迟 / 成本阈值）；
- 最终字段名称、Schema、枚举；
- 最终错误代码；
- Pre-filter / Post-filter 的具体工程实现；
- 检索日志的具体技术；
- RetrievalPlan / RetrievalRequest / Candidate Fragment / EvidencePackage 的最终 Schema。

在 **Workflow Runtime Failure Recovery, Retry and Observability Contract** 议题确认前，**不**实现正式 Retry Middleware、Tracing、Alerting 或 Recovery Worker。
