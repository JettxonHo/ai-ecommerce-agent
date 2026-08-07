# Source and Evidence Specification（来源与证据规格 — 概念）

> **Status: FROZEN BY DEC-025 / DEC-067～070；RFC-005 整体接受待用户决定。**
> **本文件是 Current Truth Layer 的一部分。** DEC-067～069 冻结 Source / Processing / Fragment、Retrieval、Scope、Evidence 与 evaluation；[DEC-070](../../decisions/dec-070-fixed-embedding-contract-and-accelerated-mvp0-adoption.md) 冻结 exact target Embedding Profile 与公共 Operation catalog，并定义 MVP-0 Direct / Exact / Lexical、MVP-1 PDF + Semantic / Hybrid 的分阶段 Capability。
> 本文件**不**包含：最终数据库表、Parser 代码、OCR、RAG 代码、Embedding、Vector Store、Web Scraper、Review Importer、最终 Evidence UI、正式 API。所有结构名为**概念示意，非最终数据契约 / 最终实现**。

---

## 1. 范围与来源

本规格记录 AI Ecommerce Agent 来源与证据系统的**概念层**结构，来源于 [DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](../../decisions/dec-025-versioned-sources-fragments-and-evidence-links.md)（Accepted，Data Architecture / Reliability Architecture，2026-07-28）。

承接：

- [DEC-008 — 分级证据标记与来源可追溯](../../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md)（被 DEC-025 补充细化）
- [DEC-009 — 阶段失效与局部重跑](../../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md)
- [DEC-012 — 结构化 Workflow State](../../decisions/dec-012-stage-state-and-structured-business-items.md)
- [DEC-014 — 按需、混合式 RAG 与分层数据访问](../../decisions/dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（被 DEC-025 补充细化）
- [DEC-017 — Customer Insight Skill Adapt](../../decisions/dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)
- [DEC-018 — Product Positioning Skill Adapt](../../decisions/dec-018-adapt-product-differentiation-for-positioning-skill.md)
- [DEC-024 — 版本化领域状态与紧凑 LangGraph State](../../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)
- [DEC-067 — 版本化 Source 关联、逐资料耐久处理与格式感知 Fragment 契约](../../decisions/dec-067-versioned-source-intake-and-format-aware-fragment-contract.md)
- [DEC-068 — PostgreSQL-native、版本化且确定性的 Retrieval 基线](../../decisions/dec-068-postgresql-native-versioned-and-deterministic-retrieval-baseline.md)
- [DEC-069 — 权威检索范围、引用式 Evidence Package 与显式降级](../../decisions/dec-069-authoritative-retrieval-scope-referenced-evidence-and-explicit-degradation.md)
- [DEC-070 — 固定 Embedding 契约与快速 MVP-0 分阶段交付](../../decisions/dec-070-fixed-embedding-contract-and-accelerated-mvp0-adoption.md)

> DEC-067 明确修订 DEC-025 的 Task 成员关系与 Fragment / Locator 细节：Source 不直接承载可变 Task membership，processing / association / availability / integrity 状态分离。旧概念示例与现行条款冲突时以 DEC-067 为准。

---

## 2. 证据链分层

```text
Source
→ Source Version
→ Document / Record
→ Fragment
→ Evidence Link
→ Versioned Domain Object
```

| 概念 | 含义 |
|------|------|
| Source | 信息来源的逻辑身份（信息从哪里来） |
| Source Version | 来源在某个时间点的具体内容快照 |
| Document / Record | 来源内容的载体（长文本 / 文件 vs 独立可计数结构化数据） |
| Fragment | 可以精确定位、检索和展示的最小原始内容单元 |
| Evidence Link | Fragment 与业务结论之间**经过验证**的关系（独立关系对象） |
| Versioned Domain Object | 业务结论 Current Truth（承接 DEC-024） |

**不得**将 Source、Fragment、检索结果和 Evidence 混为同一个概念。

---

## 3. Source（概念）

```text
Source
├── source_id
├── source_type
├── source_scope
├── ownership
├── title
├── origin
├── status
├── current_version_id
├── created_by
├── created_at
└── metadata
```

Source 的历史概念分类可以覆盖手工输入、上传资料、评论、访谈、规则或网页等来源；但首个 Goal 的已接受 intake 仅为结构化表单 / 手工文本、TXT / Markdown、文本型 PDF 与评论 CSV，且全部由用户提供。网页抓取、访谈采集、OCR、图片与通用办公文件不因该概念分类获得授权。

Source 是**逻辑身份**，不直接代表某一次不可变化的内容快照。

### 3.1 Task Source Association（现行契约）

```text
TaskSourceAssociation
├── task_source_association_id
├── task_id
├── source_id
├── active_source_version_id
├── membership_state           (active / removed / replaced)
├── revision
├── replacement_reference
├── changed_at
└── changed_by
```

Task-scoped 使用范围、移除与替换由该关联表达。关联变化不改写 Source / Source Version，也不等于物理删除；后续 SourceSetVersion 必须固定关联 identity、revision 与精确 Source Version。

---

## 4. Source Version（概念）

来源内容发生变化时必须创建新的 Source Version。典型场景：用户修改表单；用户重新上传文件；评论数据重新导入；商品页面变化；平台规则更新；竞品页面重新抓取；检测报告被更新或替代。

```text
SourceVersion
├── source_version_id
├── source_id
├── version_number
├── captured_at
├── effective_at
├── supersedes_version_id
├── storage_ref
├── processing_status
├── availability_status
└── metadata
```

业务结果必须引用具体 `source_version_id`，而**不能**只引用可能持续变化的 `source_id`。旧 Source Version 可保留用于审计，但不一定继续允许用于新的分析。

`processing_status` 使用 DEC-067 的 `registered / processing / ready / ready_with_rejections / failed / superseded`。ContentObject 的既有私有完整性记录由 RFC-002 管理，不扩散成公共 Source / Evidence digest。

### 4.1 Derived Artifact（现行契约）

Parsed text、normalized search text、Record / Fragment set 与后续 lexical / embedding output 都是精确 Source Version 的版本化派生产物。Processor / Parser / Fragmenter 配置变化创建新 Derived Artifact version 和新 Fragment identity，不覆盖历史 Provenance。

Retrieval Index 是同 PostgreSQL Service 下可重建、非权威的派生平面。每个 lexical / vector entry 必须引用精确 Fragment、Source Version、Derived Artifact / Fragmenter version、index generation 与适用 lexical / Embedding Profile。目标 vector Profile 为 `openai-text-embedding-3-small-1536-cosine-v1`；不默认启用 ANN。快速 MVP-0 只启用 Direct / Exact / PostgreSQL Lexical；vector generation、Semantic / Hybrid 与 text PDF 进入 MVP-1，在启用前 Capability 必须保持不可用。

---

## 5. Document（概念）

Document 适用于长文本或文件类来源。首个 Goal 只实现 TXT / Markdown 与文本型 PDF；Word、网页快照、扫描文件及其他办公格式仍是历史概念示例，不在当前实现范围。

```text
Document
├── document_id
├── source_version_id
├── document_type
├── page_count
├── language
├── parser_version
├── extracted_text_ref
└── parsing_metadata
```

---

## 6. Record（概念）

Record 适用于独立、可计数的结构化或半结构化数据（单条评论 / 单条访谈回答 / 单条问卷回答 / 单个商品参数 / 单个竞品 SKU / 单个用户手动输入字段）。

```text
Record
├── record_id
├── source_version_id
├── record_type
├── external_record_id
├── structured_content
├── occurred_at
└── metadata
```

评论、问卷和结构化数据**不得**为了方便全部拼接成不可计数的巨大文档。

---

## 7. Fragment（概念）

Fragment 是系统能够精确引用、检索和向用户展示的最小原始内容单元。

```text
Fragment
├── fragment_id
├── source_id
├── source_version_id
├── derived_artifact_version_id
├── document_id_or_record_id
├── fragment_type
├── verbatim_content
├── normalized_search_text
├── locator
├── parser_version
├── fragmenter_version
├── created_at
└── status
```

Fragment **必须**能够回到真实原文位置。

### 7.1 Locator（概念，按来源类型）

| 来源类型 | Locator 概念字段 |
|----------|------------------|
| Structured Form / Manual Text | `formSection` / `fieldName` |
| TXT / Markdown | `headingPath` / normalized `lineStart` / `lineEnd` |
| Text PDF | `pageNumber` / extracted-text `block` or `characterRange` |
| Review CSV | `sourceRowNumber` / stable `columnNames` / parent `recordId` |

Fragment 不跨 Source Version、Record 或 PDF page。Text PDF 不承诺 OCR bounding box / image coordinate；其他历史来源类型不属于首个 Goal 的可实现 Locator 范围。

---

## 8. Source Type（概念枚举）

下列是 DEC-025 的历史概念全集，不是首个 Goal 的 importer 清单。当前可实现 subset 以 DEC-067 与 Product Specification 为准；任何网页 / 平台来源都不得被解释为自动抓取授权。

```text
manual_input
uploaded_document
uploaded_table
product_page
competitor_page
customer_review
competitor_review
customer_interview
survey_response
internal_business_document
platform_guideline
public_web_source
system_generated
```

`system_generated` 只能用于：确定性统计；可复现的数据转换；经过验证的聚合结果。
**不得**使用 `system_generated` 将模型推断伪装成外部事实来源。

---

## 9. Source Scope（概念）

当前商品来源与竞品来源必须显式隔离：

```text
current_product
competitor_product
platform_knowledge
internal_business
```

竞品来源至少应关联：`competitor_id` / `competitor_product_id` / `competitor_name` / `platform_or_marketplace` / `captured_at`。

竞品资料可以支持：竞品卖点；竞品表达；竞品评论洞察；差异化候选；市场空白假设。
竞品资料**不能**直接证明当前商品拥有某项功能——当前商品事实必须由当前商品自己的来源支持。

---

## 10. Review Record（概念）

一批评论文件或评论导出可以作为一个逻辑 Source；每一条评论必须保留独立 Record：

```text
ReviewRecord
├── review_id
├── source_version_id
├── product_id
├── rating
├── review_text
├── review_date
├── variant
├── locale
├── verified_purchase
└── metadata
```

评论内部可拆成多个语义 Fragment，但必须保留这些 Fragment 属于同一个 Review Record 的关系。系统**不得**将同一评论的不同 Fragment 误认为来自两名不同用户。

### 10.1 User Manual Input as Source

用户手动填写的商品信息属于正式 Source（`source_type = manual_input`）；每个字段成为独立 Record 或 Fragment，并至少记录：`field_name` / `content` / `submitted_by` / `submitted_at` / `source_version_id`。

用户修改某字段时：① 创建新 Source Version；② 创建新字段 Record 或 Fragment；③ 重新判断依赖该来源的 Fact；④ 必要时创建 Invalidation Event；⑤ 使依赖旧版本的下游阶段失效。用户手动输入**不等于**"没有来源"。

---

## 11. Evidence Link（概念）

Evidence Link 是**独立关系对象**，不是证据文本副本。

```text
EvidenceLink
├── evidence_link_id
├── task_id
├── target_entity_type
├── target_entity_id
├── target_version_id
├── fragment_id
├── evidence_role
├── support_strength
├── attribution_type
├── created_by
├── validator_status
├── created_at
└── notes
```

### 11.1 Target Entity Types（概念）

```text
fact
insight
positioning_candidate
selling_point
proof_point
marketing_brief_item
xiaohongshu_brief_item
risk_warning
```

---

## 12. Evidence Role（概念枚举）

```text
supports
contradicts
qualifies
provides_context
example_only
```

同一个 Fragment 可能支持某结论 / 反驳某结论 / 限定适用范围 / 只提供背景 / 仅作示例（但不证明总体情况）。

---

## 13. Evidence Class（概念，承接 DEC-008）

业务内容必须明确区分五类：

| Evidence Class | 要求 |
|----------------|------|
| Explicit Fact | 来源直接明确表达的事实；至少一个直接支持 Fragment；来源版本有效；引用定位真实；不依赖模型推断填补关键内容 |
| Evidence-backed Insight | 由事实 / 评论 / 访谈 / 调查 / 统计支持；关联支持证据（可关联反向证据）；说明样本限制；不得把单条评论扩大为普遍结论 |
| Model Inference | 明确标记为推断；不得显示为已验证事实；不得直接成为无条件 Proof Point |
| Hypothesis to Validate | 明确标记待验证；不得作为确定性营销承诺；可在 Human Review 被接受为策略实验方向 |
| Insufficient Information | 不用模型猜测填补；说明缺失信息；必要时触发用户补充或异常暂停 |

### 13.1 Evidence Requirements by Business Layer

- **Facts：** 每个 Explicit Fact 必须关联直接 Source Fragment；用户手动输入本身可作为直接 Source Fragment；模型**不得**生成没有来源的 Explicit Fact。
- **Insights：** 可基于 Valid Facts / Review Fragments / Interview Records / Survey Records / Dataset Statistics / Competitor Review Evidence；概念字段 `evidence_class` / `supporting_fragment_ids[]` / `contradicting_fragment_ids[]` / `dataset_statistic_ids[]` / `analysis_summary` / `evidence_limitations` / `sample_size` / `coverage`（字段名为概念性）。
- **Positioning Candidates：** 属于业务策略推断（通常 `Evidence-backed Strategic Inference`），不是原始事实；概念字段 `based_on_fact_ids[]` / `based_on_insight_ids[]` / `competitor_evidence_ids[]` / `inference_summary` / `validation_status`。
- **Marketing Brief：** Proof Point 必须能回溯到 `Proof Point → Fact → Evidence Link → Fragment → Source Version`；Content Angle 可由 Insight + Positioning 推导（`Content Angle → Positioning → Insight → Evidence`）；Hypothesis-based Angle 允许进入候选但必须标记 `requires_validation`，不得转化为确定性商品承诺。

---

## 14. Frequency and Statistics Boundary（概念）

正式比例 / 频率 / 覆盖率必须基于完整、可计数的数据集计算。

只有满足以下条件才能输出（如「37% 的评论提到漏水」）：完整评论数据集可访问；有明确有效样本量；评论去重规则明确；统计过程可复现；分母分子可验证；统计结果有 Dataset Statistic 记录。

**禁止**根据 RAG Top-K 召回结果推断总体频率。必须区分：

```text
Dataset-derived Statistic
= 可以用于正式频率和比例

Retrieved Evidence Sample
= 只能证明该现象存在，不代表总体比例
```

---

## 15. Retrieved Fragment vs Formal Evidence（概念）

RAG 召回流程：

```text
Query
→ Retrieved Fragments
→ Candidate Evidence
→ Permission Validation
→ Source Version Validation
→ Existence Validation
→ Relevance Validation
→ Selected Evidence
→ Evidence Link
```

检索结果初始只能称为 `Retrieved Fragment` 或 `Candidate Evidence`。只有满足以下条件后才能成为正式 Evidence：

1. `fragment_id` 真实存在；
2. 属于当前 Task 或合法 Workspace；
3. 当前 Skill 有权限访问；
4. Source Version 当前可用；
5. Locator 可返回；
6. Fragment 内容未被错误截断；
7. 与目标业务结论相关；
8. 通过确定性 Validator；
9. 创建正式 Evidence Link。

---

## 16. Preventing Hallucinated Source References（概念）

模型**不得**自由生成 `source_id` / `source_version_id` / `fragment_id` / 文件名 / 页码 / 评论 ID / URL / 引用位置。

推荐流程：

- **Step 1：** 系统提供允许引用的候选 Fragment（如 `frag_101` / `frag_102` / `frag_103`）。
- **Step 2：** 模型只能从允许集合中选择（如 `supporting_fragment_ids: [frag_101, frag_103]`）。
- **Step 3：** 确定性 Validator 检查——ID 是否存在 / 是否属于当前任务 / 是否来自允许的 Source Scope / Source Version 是否可用 / 是否是本次 Evidence Package 中的候选 / 是否重复 / 是否已失效 / Locator 是否存在。
- **Step 4：** 只有校验通过的引用才写入 Evidence Link。

**禁止**只保存模型生成的自然语言引用（如「来源：产品说明书第 3 页」）但系统中不存在真实 Fragment ID 和 Locator。

---

## 17. Source Set Version（概念）

一个 Skill 通常依赖一组来源。

```text
SourceSetVersion
├── source_set_version_id
├── task_id
├── purpose
├── association_manifest[]     (association identity + revision + exact source_version_id + eligibility)
├── created_at
└── component_versions
```

对应 Insights Version 应记录 `based_on_source_set_version_id`（如 `customer_insight_source_set_v3`）。用户新增、移除、替换资料后应生成新的 Source Set Version。旧业务结果可据此判断是否基于旧来源集合。Source Set Version **不复制**所有来源内容，也不使用额外 package digest；它固定参与分析的关联 revision、精确 Source Version、eligibility 与可读组件版本。

---

## 18. Source Status（概念枚举）

### 18.1 Source Version Processing Status

```text
registered
processing
ready
ready_with_rejections
failed
superseded
```

| 取值 | 含义 |
|------|------|
| `registered` | 已原子登记，等待或准备处理 |
| `processing` | 正在耐久处理，客户端不得推断完成 |
| `ready` | 当前 Source Version 已完整产生 eligible output |
| `ready_with_rejections` | 评论 CSV 的合法 Record 子集诚实可用，并有有界 row issues |
| `failed` | 处理失败；保留登记与失败摘要，不产生 eligible Fragment |
| `superseded` | 已由新 Source Version 替代，历史仍可解释 |

association 的 `active / removed / replaced`、availability、integrity 与 processing status 分属不同维度，不能用一个枚举互相代替。

### 18.2 Source Conflict（概念）

```text
SourceConflict
├── conflict_id
├── task_id
├── entity_or_field
├── conflicting_fragment_ids[]
├── conflict_type
├── severity
├── resolution_status
├── resolved_value
├── resolved_by
└── resolution_reason
```

Conflict Status（概念枚举）：`open` / `user_resolved` / `rule_resolved` / `source_superseded` / `unresolved`。

关键事实冲突时 → Fact Stage `waiting_input` 或 `paused`；用户确认后生成新事实版本并记录冲突处理原因。系统**不得**由模型自行选择一个值并写成事实。

---

## 19. Evidence Package（概念）

Skill **不**直接接触整个来源数据库。执行前应构建可复现的 Evidence Package：

```text
EvidencePackage
├── task_id
├── purpose
├── source_set_version_id
├── candidate_fragments[]
├── verified_facts[]
├── dataset_statistics[]
├── known_conflicts[]
├── evidence_limitations[]
└── generated_at
```

Evidence Package：是一次 immutable、reference-based 执行输入快照；不是新的 Source，不复制整套私有正文，不修改原始来源；它引用 Source Set、Retrieval Run、Candidate Fragment 与可读组件版本，限制模型可见证据范围并支持确定性引用校验。Availability 变化可阻止新的业务使用，但不得把历史 Package latest-at-read 改绑到新 Source Version。

Skill 输出中的 Fragment ID 必须来自对应 Evidence Package 的允许集合。

---

## 20. Invalidation（概念）

来源失效后，根据正式 Evidence Link 判断受影响的业务对象。由于 MVP 仍采用阶段级失效（不实现完整字段级依赖图），采用以下原则：

```text
关键 Fact 的主要来源失效
→ Fact Stage 及其下游失效

Insight 的主要证据来源失效
→ Insight Stage 及其下游失效

仅 Context 或 Example 来源失效
→ 记录 Warning，由 Validator 决定是否触发阶段失效
```

来源失效处理至少包括：① 更新 Source Version 状态；② 查询依赖该来源的 Evidence Links；③ 确定受影响的业务层；④ 创建 Invalidation Event；⑤ 标记对应阶段失效；⑥ 清除无效 Current Truth Pointer；⑦ 保留历史记录；⑧ 从最早失效阶段重新执行（承接 DEC-009 / DEC-024）。

---

## 21. Data Isolation（概念）

所有以下对象必须关联当前任务或固定 Workspace：Source / Source Version / Document / Record / Fragment / Evidence Link / Source Set Version / Evidence Package。

检索、模型调用和 Skill Runtime **不能**跨任务召回其他用户的私有资料。Workspace / Task / Product / Source Scope、TaskSourceAssociation、SourceSetVersion、Source Version、availability 与 eligibility 由服务端从 Accepted Task / Skill Contract / 权威 Source 图推导，并形成所有检索 channel 共同使用的 SQL authorized candidate relation，在 ranking 前生效。即使 Fragment ID 真实存在，如果不属于当前授权范围，也必须拒绝引用；Browser、Skill 或 Provider 不能扩大范围。

---

## 22. Frontend Evidence Presentation（概念）

前端展示 Fact / Insight / Positioning / Brief Item 时，应尽量允许用户查看：结论；Evidence Class；支持来源数量；反向证据；来源名称；原文摘录；Locator；样本范围；证据限制；来源冲突；模型推断标识；待验证假设标识。

示例：

```text
用户洞察：部分用户担心杯盖漏水
证据等级：Evidence-backed Insight
支持证据：12 条评论
样本范围：共 120 条有效评论
示例原文："放包里有一点漏水……"
来源：商品评论导出文件，第 47 行
```

对于 Model Inference 必须提示「该结论为模型推断，当前没有直接用户反馈验证」；对于 Hypothesis 必须提示「待验证假设，不建议作为确定性营销承诺」。

---

## 23. Authoritative Boundaries（概念）

```text
Raw Information Current Truth
= Source Version + Document / Record + Fragment

Business Conclusion Current Truth
= Versioned Domain Object + Current Truth Pointer（承接 DEC-024）

Relationship between Conclusion and Source
= Evidence Link

Temporary Retrieval Output
= Retrieved Candidate Fragment（不属于正式业务 Current Truth）
```

---

## 24. Accepted Data Flow（概念）

### Ingestion

```text
User Input / Upload / External Capture
→ Source
→ Source Version
→ Document or Records
→ Fragments
```

### Analysis

```text
Skill Query
→ Candidate Fragments
→ Evidence Package
→ LLM / Deterministic Analysis
→ Structured Business Output
→ Evidence Validator
→ Evidence Links
→ Versioned Domain Object
```

### Source Update

```text
New Source Version
→ Dependency Check
→ Invalidation Event
→ Affected Stage Invalid
→ Rerun from Earliest Invalid Stage
```

---

## 25. Accepted Design Principles

1. **Source Is Not Evidence** — Source 只是信息来源；只有与结论正式绑定后才形成证据关系。
2. **Version-specific Citation** — 业务结果引用具体 Source Version。
3. **Fragment-level Traceability** — 正式引用必须能够定位到原文 Fragment。
4. **Retrieval Is Candidate Evidence** — RAG 召回结果不自动成为正式证据。
5. **Deterministic Reference Validation** — 所有 Fragment ID 必须经过确定性校验。
6. **Manual Input Is a Source** — 用户表单输入属于正式来源。
7. **Current and Competitor Data Are Isolated** — 竞品来源不能直接证明当前商品事实。
8. **Dataset Statistics Require Full Countable Data** — 不得用 Top-K 检索结果推断总体比例。
9. **Evidence Role Is Explicit** — 证据可以支持、反驳、限定、提供上下文或仅作为示例。
10. **Source Invalidation Is Traceable** — 来源变化或失效必须能够追踪到受影响业务结果。
11. **Evidence Package Controls Skill Context** — 每次 Skill 执行使用可复现的证据输入快照。
12. **Evidence Class Is User-visible** — 事实、证据洞察、模型推断、待验证假设和资料不足必须可区分。

---

## 26. Product Presentation Projection（DEC-047）

- 决策相关条目显示五类结论类型，并从当前条目打开证据卡片或可收起面板。
- 展示 Source Label、Source Version、真实可用 Locator、支持关系、Evidence Limitation 与 Conflict；无可靠定位时不得伪造。
- 直接证据可显示短摘录，综合判断可显示忠实摘要和主要依据，不强制逐句引用。
- 不显示未经校准数字置信度或机械证据覆盖总分。

本节只定义业务数据向用户交互的投影要求。DEC-069 已冻结 Task-scoped 窄投影、opaque cursor pagination（默认 20、最大 50）与禁止暴露项；DEC-070 已冻结 Source intake read / write、association / version read 与 Evidence Link read Operation family。MVP-0 只在 Capability 中开放 JSON / text / TXT / Markdown / CSV；text PDF 作为 additive MVP-1 capability。

---

## 27. 明确不包含（Out of Scope）

本规格**不**包含以下内容（来源：DEC-025 归档要求）：

- 最终数据库表；
- Parser 代码；
- OCR；
- RAG 代码；
- Embedding；
- Vector Store；
- Web Scraper；
- Review Importer；
- 最终 Evidence UI 组件与视觉布局；
- 正式 API。

以下选型**仍未确认**（不得在本规格中擅自选择）：PostgreSQL / MongoDB / Elasticsearch / pgvector / Pinecone / Weaviate / Chroma / Embedding 模型 / Reranker / PDF Parser / OCR Provider。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得为使文档「完整」而补充未经讨论的字段或选型。
- 冲突时按 [../../governance/documentation-rules.md](../../governance/documentation-rules.md) 第 6 节优先级裁决；与 DEC-025 冲突时以 DEC-025 为准。
