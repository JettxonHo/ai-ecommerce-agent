# DEC-032：Hybrid Retrieval and Evidence Runtime 采用 Direct-first 检索、确定性检索规划、强制权限与版本过滤与可复现证据装配

> **Type:** Runtime Architecture / Retrieval Architecture / Evidence Architecture
> **Status:** Accepted
> **Date:** 2026-07-29
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)（概念 Runtime Spec，仅概念）
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** [DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md) by defining the formal Hybrid Retrieval and Evidence Runtime Architecture（在 DEC-014「按需、混合式 RAG + 分层数据访问，RAG 仅检索与证据提供」高层原则基础上，正式定义检索运行时与证据装配的概念层架构，**不推翻** DEC-014 的分层数据访问原则与「RAG 仅检索与证据提供」边界）。

---

## 用户确认

用户对该 Hybrid Retrieval and Evidence Runtime Architecture Proposal 明确回复：

> 确认形成

本决定经 Decision Gate 通过，记录为 Accepted Decision（Type: Runtime Architecture / Retrieval Architecture / Evidence Architecture）。

被接受的核心结论：

- Hybrid Retrieval and Evidence Runtime 是检索运行时与证据装配的共享运行架构，服务于所有 Skill（Product Intake / Customer Insight / Positioning / Marketing Brief / Xiaohongshu Adapter）与 Evidence Validator。它**不**是某个 Skill 的内部实现，**不**是 Core Skill Contract，**不**是 Platform Adapter Contract，而是一个跨 Skill 的**运行架构层**。
- 核心原则：**能直接读取时不使用检索；需要检索时先限定任务 / 权限 / 商品身份 / 来源范围 / 来源版本，再选择 Lexical / Semantic / Hybrid。** 一个高度相关但不属于当前任务或当前允许 Source Set 的 Fragment，必须被**排除**，而不是仅降低排名。
- Runtime 的输出是 **Candidate Fragments + Retrieval Logs + Reproducible Evidence Package**，而**不**是 Formal Evidence Links / Fact / Insight / Positioning / Approved Strategy / Execution Brief。检索结果仅为候选证据，须经 Evidence Validator 校验并经正式事务才创建 Formal Evidence Link（承接 DEC-025）。
- 检索方式与证据装配由**确定性逻辑**控制任务 / 权限 / 商品身份 / 来源范围 / 来源版本边界；LLM 可有限辅助 Query Planning，但**不**决定访问范围、**不**修改 Source Scope / Source Set Version、**不**跨任务检索。

---

## Decision

Hybrid Retrieval and Evidence Runtime 正式定义为：

```text
Direct-first Retrieval Runtime
+ Retrieval-on-demand
+ Deterministic Retrieval Planning
+ Mandatory Permission and Version Filtering
+ Reproducible Evidence Package
```

其业务目标是：

在严格限定任务 / 权限 / 商品身份 / 来源范围 / 来源版本的前提下，为 Skill 提供可复现、可解释、可校验的候选证据输入（Candidate Fragments + Evidence Package），并保证检索结果**不**自动成为正式证据、**不**泄露跨任务或跨商品身份的私有资料、**不**用 Top-K 召回结果推断总体频率。

### 检索优先级（Retrieval Priority）

不是每个请求都跑完所有层；Runtime 按以下优先级选择检索方式（前置能解决就不走后置）：

```text
1. Structured Direct Read      （结构化直读：直接读结构化字段 / 业务记录）
2. Exact ID / Key Lookup       （精确 ID / Key 查找：SKU / 型号 / 认证编号 / Fragment ID / Source Version ID）
3. Bounded Direct Document Read（有界直读：限定 Document / Record 范围内直接读全文）
4. Lexical Retrieval           （词法检索：BM25 等关键词检索）
5. Semantic Retrieval          （语义检索：向量相似检索）
6. Hybrid Retrieval            （混合检索：Lexical + Semantic 融合）
7. Optional Reranking          （可选 Reranking：对允许候选重排，非 MVP 硬依赖）
```

> 优先级 1–3 为 **Direct 读取**（确定性、可完全复现、无相关性打分），优先级 4–6 为 **Retrieval 检索**（基于相关性打分召回），优先级 7 为可选增强。

### 运行流程（Runtime Flow）

```text
Skill Retrieval Request
→ Deterministic Retrieval Planner
→ Permission / Task / Product Identity / Source Scope / Source Version Filters
→ ( Structured Direct Read
   | Exact ID / Key Lookup
   | Bounded Direct Document Read
   | Lexical Retrieval
   | Semantic Retrieval
   | Hybrid Retrieval )
→ Candidate Fragments
→ Deduplication
→ Fusion
→ Optional Reranking
→ Coverage and Conflict Checks
→ Reproducible Evidence Package
→ Skill Analysis
→ Evidence Validator
→ Transactional Formal Evidence Links
```

---

## Responsibilities

- **按需提供候选证据：** 当 Skill 需要证据时，Runtime 负责在严格限定范围内召回 Candidate Fragments 并装配可复现 Evidence Package。
- **确定性规划检索方式：** Deterministic Retrieval Planner 根据请求决定使用 Direct Read / Exact Lookup / Lexical / Semantic / Hybrid，以及是否需要 Fusion / Reranking。
- **强制 Permission / Task / Product / Source Scope / Source Version 过滤：** 在召回前 / 召回中应用强制过滤，排除不属于当前任务或当前允许 Source Set 的 Fragment。
- **保证可复现性：** 同一 Retrieval Plan + 同一 Source Set Version + 同一组件版本应能复现 Skill 当时看到的证据输入（Evidence Package）。
- **保证可解释性：** 在 dev / debug / eval 中能回答「为什么这个 Fragment 被召回 / 为什么被排除」。
- **记录检索日志：** 每次检索记录 RetrievalRun（使用的 Plan、组件版本、过滤条件、召回结果概要），供复现、审计与评测。
- **明确边界：** Runtime 只负责检索与证据装配，不负责业务结论；检索结果不是 Formal Evidence，须经 Evidence Validator 才能成为正式证据（承接 DEC-025）。

## Non-responsibilities

- **不**做业务分析 / 战略判断 / 文案生成（这些是各 Skill 的职责）。
- **不**创建 Formal Evidence Link / Fact / Insight / Positioning / Approved Strategy / Execution Brief（这些须经对应 Validator 与业务事务）。
- **不**计算正式总体频率 / 统计比例（须由确定性统计服务基于完整可计数数据集产生，承接 DEC-027）。
- **不**决定最终 Source Scope / Product Scope / Source Set Version / 访问权限（这些由业务身份与确定性逻辑在前置阶段确定，Runtime 仅执行过滤）。
- **不**选择具体 Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization / 融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制（本决定仅在概念层定义架构与边界，具体技术选型未确认）。

---

## Hard Rules

```text
Hard Rules:
- Permission and Source Version filters before relevance
- No cross-task retrieval
- No Current Product / Competitor leakage
- Retrieval result is not Formal Evidence
- No Top-K frequency extrapolation
- No fabricated answer on zero retrieval
```

1. **Permission and Source Version filters before relevance：** 权限与 Source Version 过滤在相关性打分之前 / 之中生效。一个高度相关但不属于当前任务或当前允许 Source Set 的 Fragment，必须被**排除**，而不是仅降低排名。
2. **No cross-task retrieval：** 跨任务召回私有资料必须拒绝，即使 Fragment ID 真实存在、不属于当前授权范围也必须拒绝引用（承接 DEC-025 Source Scope 隔离）。
3. **No Current Product / Competitor leakage：** 当前商品与竞品的 Source Scope 必须隔离；竞品资料不能直接证明当前商品事实；不得默认 all_product_sources。
4. **Retrieval result is not Formal Evidence：** Candidate Fragment 仅候选证据，须经 Evidence Validator 校验并通过正式事务才创建 Formal Evidence Link。
5. **No Top-K frequency extrapolation：** Top-K 召回结果仅表示与 Query 相关的候选证据，非总体样本的完整或随机分布；禁止根据 Top-K 计算或推断总体比例 / 频率 / 共识 / 市场份额 / 分布。
6. **No fabricated answer on zero retrieval：** 零召回时返回 `insufficient_information` 并传播 Evidence Limitation，模型不得虚构答案、不得用记忆或常识冒充证据。

---

## Score and Fusion Boundary

- **不得直接相加不同量纲的相关性分数：** BM25（词法）分数与 Vector similarity（语义）分数属不同量纲，**不得**直接数值相加。
- **可用 Rank Fusion 或 Score Normalization + Weighted Combination：** 若需融合，可使用 Rank Fusion（基于排名）或 Score Normalization + Weighted Combination（分数归一化后加权组合）。
- **融合方法须满足：** 可复现、可版本化、保留原始各通道排名（raw ranks）、可解释、可替换。
- **本决定不选择具体融合算法 / Score Normalization 方法 / 融合权重。**

---

## Deterministic Retrieval Planner

Deterministic Retrieval Planner 接收 RetrievalRequest，输出 RetrievalPlan。以下为**概念结构**，非最终数据库 / API Schema。

**输入：RetrievalRequest（概念字段）**

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

**输出：RetrievalPlan（概念字段）**

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

> Planner 的任务是确定**检索方式与边界**，不是确定业务结论。Planner 本身是确定性逻辑（可有限借助 LLM 做 Query Planning，见下节），其产出的 Plan 必须可复现、可版本化（`retrieval_plan_version`）。

---

## LLM Query Planning Boundary

- **LLM 可辅助：** 意图识别 / 子查询拆分 / 有限的 Query Rewrite / 同义表达 / 主题查询候选。
- **LLM 不得决定：** `task_id` / `workspace_id` / Permission / Source Scope / Product Scope / Source Set Version，以及是否允许跨任务检索。
- **Exact identifiers 必须逐字保留：** SKU / 型号 / 认证编号 / 数字 / 单位 / 品牌名 / Fragment ID / Source Version ID 等**精确标识符**在 Query Rewrite 中必须**逐字保留**，不得改写、不得翻译、不得泛化。
- **Query Rewrite 数量有确定性上限：** 单次请求产生的 Query 数量有确定上限，不允许无限发散查询。
- **LLM 不接触访问范围控制：** 访问范围由确定性逻辑与业务身份决定，LLM 不能修改。

---

## Mandatory Metadata Filters

每次检索必须在召回前 / 召回中应用以下强制元数据过滤（概念维度）：

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

> 核心原则：**一个高度相关但不属于当前任务或当前允许 Source Set 的 Fragment，必须被排除，而不是仅降低排名。**

---

## Pre-filter and Post-filter Boundary

- **过滤在召回前 / 召回中生效，不是「先全召回再删除」：** 强制过滤（权限 / 任务 / 商品身份 / Source Scope / Source Version）应在索引层 / 查询层前置应用，避免把越权候选召回后再丢弃。
- **本决定不选择具体向量数据库实现。** Pre-filter / Post-filter 的具体工程实现（索引是否原生支持 pre-filter、是否需要两阶段）属于未确认的技术选型。

---

## Current Product and Competitor Isolation

**Source Scope 概念集合：**

```text
- current_product             （当前商品资料）
- current_product_customer    （当前商品用户反馈）
- competitor_product          （竞品商品资料）
- competitor_customer         （竞品用户反馈）
- manual_input                （用户手工输入）
- platform_policy             （平台政策知识）
- business_context            （业务 / 账号 / 活动上下文）
```

**不得默认 all_product_sources。** 每个 Skill 在 Evidence Package 中只能看到其被允许的 Source Scope 子集。

**各 Skill 允许 Scope（概念，承接各 Skill Contract）：**

- **Product Intake & Fact Extraction：** 仅 `current_product` + `manual_input`（竞品资料可登记为后续阶段可用，但不用于证明当前商品属性）。
- **Customer Insight Analysis：** `current_product_customer` + `competitor_customer`（竞品反馈支持品类共性 / 竞品弱点 / 差异化假设，但不能证明当前商品用户事实；scope 必须保留）。
- **Product Positioning：** 当前商品 facts / insights + 竞品 facts / insights（竞品证据只能用于 Gap / Context，不得归因当前商品能力；身份不得合并）。

**每个 Candidate Fragment 必须保留：** `source_scope` / `product_id` / `competitor_id`。

---

## Source Set Version Boundary

每个 Skill 分析的来源范围由 **SourceSetVersion** 固定：

- **Superseded（已被取代）来源：** 默认排除。
- **Deleted（已删除）来源：** 排除。
- **Restricted（受限）来源：** 返回权限错误，不得静默忽略。
- **Processing not complete（处理未完成）来源：** 不作为完整可计数数据集使用（影响 Dataset Statistics）。
- **Source Set 变化：** 旧 Evidence Package 不再是当前输入；须基于新 Source Set Version 重新装配。

---

## Candidate Fragment

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
- retrieval_channels[]         （经哪些检索通道召回）
- lexical_rank
- semantic_rank
- fused_rank
- rerank_score
- matched_terms[]
- query_ids[]
- availability_status
- retrieval_run_id
```

> **排名 / 分数只解释「为何被召回」，不是 Fact Confidence / Evidence Strength。** 相关性高 ≠ 证据强、≠ 事实可信。

---

## Deduplication

- **按稳定 `fragment_id` 去重：** 同一 Fragment 经多条 Query / 多个通道召回，合并为一个 Candidate Fragment。
- **合并时保留：** `retrieval_channels[]` / `matched_queries[]` / 各通道 `channel_ranks`。
- **同一 Fragment 经多条 Query 召回 ≠ 多条独立证据。**
- **用户评论类去重须保留 `record_id`：** 去重不得合并不同评论记录（否则破坏可计数性）。

---

## Reranking

- **Reranking 是可选增强，不是 MVP 硬依赖。**
- **Reranker 只能对「已允许」的 Candidate Fragments 重排：** 不得新增来源、不得修改 Scope / Version、不得创建 Evidence Link。
- **必须记录 Reranker 模型与版本。**
- **Reranker 失败 → 回退到 Fusion 结果。**
- **是否引入 Reranking 由 Retrieval Evaluation 决定，不在本决定强制。**

---

## Evidence Package Construction

Evidence Package 是 Skill 的**可复现证据输入**。构建流程（概念步骤）：

```text
1.  接收 Skill Retrieval Request
2.  Deterministic Retrieval Planner 生成 RetrievalPlan
3.  应用 Permission / Task / Product / Source Scope / Source Version 过滤
4.  执行 Direct Read / Exact Lookup / Lexical / Semantic / Hybrid
5.  召回 Candidate Fragments
6.  去重（按 fragment_id，保留通道与 record_id）
7.  Fusion（Rank Fusion 或 Score Normalization + Weighted）
8.  Optional Reranking（失败回退 Fusion）
9.  Coverage 检查（子问题 / 支持 / 反向 / 单一来源 / 同一 Record / 全竞品 / 缺失当前商品 / 旧版本 / 缺口）
10. Conflict 检查（已知来源冲突记录到 known_conflicts[]）
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
- verified_facts[]            （仅含已校验事实，非本次新产生）
- dataset_statistics[]        （确定性统计，承接 DEC-027）
- known_conflicts[]
- coverage_summary
- evidence_limitations[]
- generated_at
- package_hash
```

> Evidence Package 必须能复现 Skill 当时看到的证据输入。

---

## Evidence Coverage

Evidence Coverage 不得只展示 Top 10。必须检查并报告：

- 子问题是否都有证据；
- 支持（supporting）与反向（contradicting）证据是否都召回；
- 是否只有单一来源（single-source）；
- 是否全部来自同一 Record（同一评论 / 同一文档）；
- 是否召回全部竞品资料（all-competitor）；
- 是否缺失当前商品资料；
- 是否混入旧版本来源；
- 明确的证据缺口（gaps）。

---

## Dataset Analysis Boundary

- **检索（Retrieval）回答：「哪些 Fragment 与问题相关？」**
- **数据集分析（Dataset Analysis）回答：「某主题下有多少条独立 Record？」**
- **正式统计需要：** Dataset Version + 完整 Record 集合 + 确定性计数。
- **禁止：** 用 Top-K 召回结果计算比例 / 频率 / 共识 / 市场份额 / 分布（承接 DEC-025 / DEC-027）。

---

## Retrieval Logging

- 每次检索记录一条 **RetrievalRun**（使用的 Plan、过滤条件、组件版本、召回结果概要、时间）。
- 可记录检索组件版本（Embedding 版本 / 索引版本 / Reranker 版本 / Fusion 方法版本）。
- **本决定暂不选择具体检索日志技术。**

---

## Explainability

- 在 dev / debug / eval 中必须能回答：**「为什么这个 Fragment 被返回？为什么这个 Fragment 被排除？」**
- 解释至少包含：命中的检索通道、命中的 Query、命中的 term、应用的过滤条件、各通道排名。

---

## Failure and Degraded Modes

- **Semantic Retrieval 不可用：** 回退 Structured + Lexical，记录 `semantic_retrieval_unavailable`，传播 Evidence Limitation。
- **Lexical Retrieval 不可用：** 回退 Semantic，但精确标识符（SKU / 型号 / 认证编号）未被完整校验 → 返回 `valid_with_limitations` 或暂停。
- **Reranker 不可用：** Fusion 结果继续，不阻塞。
- **Vector Index 不完整：** 仅使用 Direct / Structured / Lexical，不得查询不完整索引。
- **Source Processing 待完成：** 等待 / 返回 incomplete 状态，不作为完整可计数数据集。
- **Zero Results（零召回）：** 返回 `insufficient_information`，模型不得虚构答案。

---

## Formal Evidence Link Transaction Boundary

Formal Evidence Link 仅在 Skill 输出通过 Evidence Validator 后才创建。事务流程（概念步骤）：

```text
1.  Skill 基于 Evidence Package 产出结论（含 fragment_id 引用）
2.  Evidence Validator 校验引用（ID 存在 / 属当前 task / 来自允许 Source Scope / Source Version 可用 / 属本次 Evidence Package 候选 / 未重复 / 未失效 / Locator 存在）
3.  若校验通过 → 进入事务
4.  创建 Formal Evidence Link（Versioned Domain Object ↔ Fragment）
5.  写入 Business Repository（承接 DEC-024 / DEC-025）
6.  记录审计
7.  提交事务（幂等）
8.  若任一步失败 → 不创建 / 不更新 Current Truth / 不写部分对象
9.  失败时：Candidate Fragment + Retrieval Log 可保留；Skill 可重跑；Retrieval 可重新规划
```

> **边界：** Evidence Package = 可复现的 Skill 输入；Formal Evidence Link = 正式关系。二者不同。Evidence Package 不进 Current Truth；Formal Evidence Link 进 Current Truth（承接 DEC-025）。

---

## Cache Boundary

- **可缓存：** Source Version 解析、Fragment Embedding、同一 Retrieval Plan 的结果、Evidence Package。
- **缓存键必须包含：** `task_or_workspace_scope` / `source_set_version_id` / `query` / `retrieval_strategy` / `filter_set` / `component_versions`。
- **Source Set Version 变化后不得返回旧缓存。**
- **本决定不选择具体缓存技术。**

---

## Evaluation Metrics

- **Hard Reliability（硬可靠性，6 项，全部目标 0%）：**
  - Cross-task / Cross-scope leakage（跨任务 / 跨范围泄露）
  - Current Product / Competitor leakage（当前商品 / 竞品泄露）
  - Retrieval result treated as Formal Evidence（检索结果被当作正式证据）
  - Top-K frequency extrapolation（Top-K 频率外推）
  - Fabricated answer on zero retrieval（零召回虚构答案）
  - Stale Source Version used（使用过期 Source Version）
- **Retrieval Quality（检索质量）：** Recall@K 等（K 值未确认）、Precision、Coverage 命中率。
- **Runtime Metrics（运行指标）：** 延迟、成本、降级频率。
- **Business Metrics（业务指标）：** 下游 Skill 结论可追溯率、Evidence Validator 通过率。

---

## Evaluation Dataset（概念测试集）

- **Exact Fact Query：** 精确事实查询（SKU / 型号 / 认证），验证 Direct Read / Exact Lookup。
- **Semantic Customer Query：** 语义用户反馈查询，验证 Semantic Retrieval。
- **Hybrid Query：** 词法 + 语义混合查询，验证 Fusion。
- **Scope Isolation Query：** 范围隔离查询（竞品冒充当前商品 / 跨任务），验证强制过滤。
- **Counter-evidence Query：** 反向证据查询，验证 Coverage 是否召回反向证据。

---

## Contract Summary

```text
Hybrid Retrieval and Evidence Runtime:
Direct-first + Retrieval-on-demand
+ Deterministic Retrieval Planning
+ Mandatory Permission and Version Filtering
+ Reproducible Evidence Package

Output:
Candidate Fragments + Retrieval Logs + Evidence Package
(NOT Formal Evidence Links / Fact / Insight / Positioning / Approved Strategy)

Hard Rules:
- Permission and Source Version filters before relevance
- No cross-task retrieval
- No Current Product / Competitor leakage
- Retrieval result is not Formal Evidence
- No Top-K frequency extrapolation
- No fabricated answer on zero retrieval
```

---

## Reason

- **承接 DEC-014：** DEC-014 仅在高层确认「按需、混合式 RAG + 分层数据访问，RAG 仅检索与证据提供」，但未定义检索运行时如何规划、如何强制权限与版本过滤、如何装配可复现证据、如何与 Skill 与 Evidence Validator 集成。DEC-032 填补这一概念层运行架构空白。
- **承接 DEC-025 / 026 / 027 / 028 / 030 / 031：** 各 Skill 与 Adapter 都依赖 Evidence Package 作为可复现输入，并要求 Fragment ID 可追溯、Source Scope 隔离、Evidence Validator 校验后才创建 Evidence Link。DEC-032 定义统一的检索与证据装配运行架构，支撑这些契约。
- **防止三类系统性失败：** ①跨任务 / 跨商品身份泄露私有资料；②检索结果被误当正式证据或总体频率；③Evidence Package 不可复现导致结论不可追溯。
- **把具体技术选型推迟到评测驱动：** Embedding / 向量数据库 / BM25 / Reranker / Top-K / Chunk Size 等是难回滚且依赖评测结论的选型，本决定仅在概念层定义架构与边界，不锁定技术。

## Impact

- **检索与证据装配成为共享运行架构：** 所有 Skill 与 Evidence Validator 经由统一 Runtime 获得 Candidate Fragments 与 Evidence Package。
- **Skill 不直接查询任意 Source：** Skill 通过 Retrieval Runtime 请求证据，Runtime 负责规划、过滤、装配（承接 DEC-025）。
- **为后续技术选型建立边界：** 在 Workflow Runtime Failure Recovery 议题与具体技术选型确认前，不实现正式 Retry / Tracing / Alerting / Recovery Worker，不选择具体 Embedding / 向量数据库 / 检索引擎 / 缓存技术。
- **本决定不影响既有 Core Skill Contract / Platform Adapter Contract 的已确认结论：** DEC-032 仅定义检索与证据装配运行架构，不推翻各 Skill / Adapter 契约。

## Decision Boundary（尚未确认 / 不选择）

**尚未确认的技术选型（本决定不选择，须由后续议题与评测决定）：**

- Embedding 模型
- 向量数据库（Vector Database）
- 词法搜索引擎（Lexical Search Engine）/ BM25 实现
- Rank Fusion 算法
- Score Normalization 方法与融合权重
- Top-K 值
- Reranker 模型与是否引入
- Chunk Size / Chunk Overlap
- Query Rewrite 模型
- 缓存技术（Cache Technology）
- 索引刷新机制（Index Refresh Strategy）
- 数据库 / API 框架
- 性能目标（延迟 / 成本阈值）
- 最终字段名称
- 最终错误代码

**本决定不创建：**

- 正式 Embedding / Vector Index / Full-text Index 代码
- 正式 Retrieval API
- Query Rewrite Prompt
- Reranker 代码
- Fusion 代码
- Cache 代码
- 数据库表
- LangGraph Retrieval Node
- 任何业务实现代码

---

## Related Decisions

- [DEC-008 — 输出采用分级证据标记与结论可追溯机制](dec-008-graded-evidence-and-traceable-conclusions.md)（Graded Evidence；检索结果须经校验才成正式证据）
- [DEC-009 — 用户修改上游内容后采用阶段级失效与局部重跑](dec-009-stage-level-invalidation-and-partial-rerun.md)（Source Set Version 变化触发重新装配）
- [DEC-013 — MVP 采用支持跨会话恢复的任务级持久化状态](dec-013-task-level-persistent-state-and-cross-session-resume.md)（任务级 task_id 隔离）
- [DEC-014 — MVP 采用按需、混合式 RAG 与分层数据访问策略](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（本决定 Amends 的来源；按需混合 RAG + 分层数据访问）
- [DEC-015 — Skill 定义为带执行契约的可复用业务能力包](dec-015-contract-based-reusable-business-skills.md)（Skill 显式声明检索依赖）
- [DEC-023 — MVP 选择 LangGraph StateGraph 作为核心工作流运行方式](dec-023-select-langgraph-stategraph-for-mvp-workflow.md)（检索以结构化 IO 被 Skill / Node Adapter 调用）
- [DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](dec-024-versioned-domain-state-and-compact-langgraph-state.md)（Version ID 引用 Domain Objects）
- [DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](dec-025-versioned-sources-fragments-and-evidence-links.md)（Evidence Package + Evidence Validator + Evidence Link + Source Scope 隔离；本 Runtime 的直接下游证据架构）
- [DEC-026 — Product Intake & Fact Extraction Skill Contract](dec-026-product-intake-and-fact-extraction-skill-contract.md)（仅 current_product + manual_input scope）
- [DEC-027 — Customer Insight Analysis Skill Contract](dec-027-customer-insight-analysis-skill-contract.md)（current_product_customer + competitor_customer scope；禁止 Top-K 频率外推）
- [DEC-028 — Product Positioning Skill Contract](dec-028-product-positioning-skill-contract.md)（当前 + 竞品 facts / insights，身份不合并）
- [DEC-030 — Marketing Brief Generation Skill Contract](dec-030-marketing-brief-generation-skill-contract.md)（消费上游版本化证据输入）
- [DEC-031 — Xiaohongshu Brief Mapping Adapter Contract](dec-031-xiaohongshu-brief-mapping-adapter-contract.md)（真实用户原声须来自真实 Fragment）

---

## Related RFC

None

---

## Supersedes

None

---

## Amends

**Amends [DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)** by defining the formal Hybrid Retrieval and Evidence Runtime Architecture.

- DEC-014 确认 MVP 采用按需、混合式 RAG 与分层数据访问（结构化直读 / 短资料全文 / 长资料混合检索 / 运营知识独立库），RAG 仅检索与证据提供；但向量库 / Embedding / BM25 / Reranker / Chunking / Top-K / 混合权重 / 触发规则 / 数据契约均未确认。
- DEC-032 在此基础上正式定义**检索运行时与证据装配的概念层架构**（Direct-first + Retrieval-on-demand / Deterministic Retrieval Planner / 强制 Permission 与 Version 过滤 / 可复现 Evidence Package / 检索优先级 / 运行流程 / Hard Rules / 各类边界 / 降级模式 / Formal Evidence Link 事务 / Cache 边界 / 评价指标）。
- **不推翻** DEC-014 的分层数据访问原则与「RAG 仅检索与证据提供」边界；DEC-014 行作为历史记录不修改，本 Amends 关系仅在此处记录。

---

## Notes

- 本决定保持 **Development Status: NOT READY**。
- 当前**不**创建正式 Embedding / Vector Index / Full-text Index 代码 / 正式 Retrieval API / Query Rewrite Prompt / Reranker 代码 / Fusion 代码 / Cache 代码 / 数据库表 / LangGraph Retrieval Node / 任何业务实现代码。
- 当前**不**选择 Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization 方法与融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / 数据库 / API 框架 / 性能目标 / 最终字段名称 / 最终错误代码。
- 当前**不**创建 RFC。
- Hybrid Retrieval and Evidence Runtime 是跨 Skill 的共享运行架构层（非 Core Skill Contract、非 Platform Adapter Contract），服务于所有 Skill 与 Evidence Validator；其输出（Candidate Fragments + Evidence Package）是 Skill 的可复现证据输入，而非正式证据。若检索运行时能跨任务 / 跨商品身份泄露私有资料、把检索结果当作正式证据或总体频率、或装配不可复现的 Evidence Package，将导致证据不可追溯、竞品资料冒充当前商品事实、Top-K 召回被误用为市场结论、以及 Skill 结论无法独立复现与校验。
- 概念 Runtime Spec 见 [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)（仅概念，非最终实现）。
- 在 **Workflow Runtime Failure Recovery, Retry and Observability Contract** 议题确认前，**不**实现正式 Retry Middleware、Tracing、Alerting 或 Recovery Worker。
