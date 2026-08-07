# DEC-025：采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构

> **Type:** Data Architecture / Reliability Architecture
> **Status:** Accepted — Amended by DEC-061
> **Date:** 2026-07-28
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [Source and Evidence Specification（概念）](../specs/evidence/source-and-evidence-specification.md)
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** DEC-008 and DEC-014 by defining detailed source, fragment and formal evidence boundaries.
> **Amended By:** [DEC-061](dec-061-task-scoped-private-material-and-reversible-removal.md)（冻结产品层从当前 Task 有效资料集移除与物理永久删除的区别；物理保留、Hold 与删除政策仍待后续权威文档）

---

## 用户确认

用户对 Source and Evidence Specification Proposal 明确回复：

> 确认

被接受的核心结论是：

> AI Ecommerce Agent 的来源与证据系统采用：
> `Source → Source Version → Document / Record → Fragment → Evidence Link → Versioned Domain Object`
> Source 表示逻辑来源，Source Version 表示具体内容快照，Document 或 Record 表示来源内容载体，Fragment 表示可精确定位和引用的原始内容单元，Evidence Link 表示某个业务结论与原始 Fragment 之间经过验证的支持、反驳、限定或上下文关系。
> RAG 检索返回的 Fragment 只能视为 Candidate Evidence。只有通过任务权限、来源版本、ID 存在性、原文定位、内容相关性与确定性 Validator 校验，并创建正式 Evidence Link 后，才能成为业务证据。
> 模型不能自由生成 `source_ref`、`fragment_id` 或虚构来源。模型只能从系统提供的候选 Fragment ID 集合中选择，所有引用必须经过确定性验证。

---

## Decision

AI Ecommerce Agent 的 Source and Evidence Architecture 正式采用：

```text
Source
↓
Source Version
↓
Document / Record
↓
Fragment
↓
Evidence Link
↓
Versioned Domain Object
```

其中：

```text
Source
= 信息来源的逻辑身份

Source Version
= 来源在某个时间点的具体内容快照

Document / Record
= 来源内容的载体

Fragment
= 可以精确定位、检索和展示的原始内容单元

Evidence Link
= Fragment 与业务结论之间经过验证的关系
```

不得将 Source、Fragment、检索结果和 Evidence 混为同一个概念。

---

## Source

Source 表示信息从哪里来。
概念结构：

```text
Source
├── source_id
├── task_id
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

Source 可以包括：

- 用户手动输入；
- 用户上传文档；
- 用户上传表格；
- 当前商品页面；
- 当前商品评论；
- 竞品商品页面；
- 竞品评论；
- 用户访谈；
- 问卷回答；
- 内部业务文档；
- 平台运营规则；
- 公开网页；
- 确定性系统统计。

Source 是逻辑身份，不直接代表某一次不可变化的内容快照。

---

## Source Version

来源内容发生变化时，必须创建新的 Source Version。
典型场景包括：

- 用户修改表单；
- 用户重新上传文件；
- 评论数据重新导入；
- 商品页面发生变化；
- 平台规则更新；
- 竞品页面重新抓取；
- 检测报告被更新或替代。

概念结构：

```text
SourceVersion
├── source_version_id
├── source_id
├── version_number
├── content_hash
├── captured_at
├── effective_at
├── supersedes_version_id
├── storage_ref
├── parsing_status
├── availability_status
└── metadata
```

业务结果必须引用具体：

```text
source_version_id
```

而不能只引用可能持续变化的：

```text
source_id
```

旧 Source Version 可以保留用于审计，但不一定继续允许用于新的分析。

---

## Document and Record

### Document

Document 适用于长文本或文件类来源，例如：

- PDF；
- Word；
- Markdown；
- 网页快照；
- 商品说明书；
- 检测报告；
- 内部运营文档。

概念结构：

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

### Record

Record 适用于独立、可计数的结构化或半结构化数据，例如：

- 单条评论；
- 单条访谈回答；
- 单条问卷回答；
- 单个商品参数；
- 单个竞品 SKU；
- 单个用户手动输入字段。

概念结构：

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

评论、问卷和结构化数据不得为了方便全部拼接成不可计数的巨大文档。

---

## Fragment

Fragment 是系统能够精确引用、检索和向用户展示的最小原始内容单元。
概念结构：

```text
Fragment
├── fragment_id
├── task_id
├── source_id
├── source_version_id
├── document_id_or_record_id
├── fragment_type
├── content
├── locator
├── content_hash
├── parser_version
├── created_at
└── status
```

Fragment 必须能够回到真实原文位置。

### Locator

根据来源类型，Locator 可以包含：

PDF

```text
page
paragraph_index
bounding_box
```

Web Page

```text
url
heading_path
paragraph_index
captured_at
```

Review Dataset

```text
review_id
product_id
row_number
```

Spreadsheet

```text
sheet
row
column
```

Manual Input

```text
form_section
field_name
```

Interview

```text
speaker
timestamp
response_number
```

最终 Locator Schema 尚未确认，但必须满足可追溯与可返回原文要求。

---

## Source Types

来源类型至少需要覆盖以下概念：

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

`system_generated` 只能用于：

- 确定性统计；
- 可复现的数据转换；
- 经过验证的聚合结果。

不得使用 `system_generated` 将模型推断伪装成外部事实来源。

---

## User Manual Input as Source

用户手动填写的商品信息属于正式 Source。
例如：

```text
商品名称：轻量保温杯
材质：304 不锈钢
容量：500 mL
```

应被建模为：

```text
Source Type:
manual_input
```

每个字段成为独立 Record 或 Fragment，并至少记录：

```text
field_name
content
submitted_by
submitted_at
source_version_id
```

用户修改某个字段时：

1. 创建新的 Source Version；
2. 创建新的字段 Record 或 Fragment；
3. 重新判断依赖该来源的 Fact；
4. 必要时创建 Invalidation Event；
5. 使依赖旧版本的下游阶段失效。

用户手动输入不等于"没有来源"。

---

## Review Data Model

一批评论文件或评论导出可以作为一个逻辑 Source。
每一条评论必须保留独立 Record：

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

评论内部可以拆成多个语义 Fragment，但必须保留这些 Fragment 属于同一个 Review Record 的关系。
例如：

```text
一条评论：
"保温效果不错，但是杯盖容易漏水。"

Fragment A：
"保温效果不错"

Fragment B：
"杯盖容易漏水"
```

系统不得将两个 Fragment 误认为来自两名不同用户。

---

## Frequency and Statistics Boundary

正式比例、频率和覆盖率必须基于完整、可计数的数据集计算。
例如：

```text
37% 的评论提到漏水
```

只有在以下条件满足时才能输出：

- 完整评论数据集可访问；
- 有明确有效样本量；
- 评论去重规则明确；
- 统计过程可复现；
- 分子和分母可验证；
- 统计结果有 Dataset Statistic 记录。

禁止根据 RAG Top-K 召回结果推断总体频率。
必须区分：

```text
Dataset-derived Statistic
= 可以用于正式频率和比例

Retrieved Evidence Sample
= 只能证明该现象存在，不代表总体比例
```

---

## Current Product and Competitor Isolation

当前商品来源与竞品来源必须显式隔离。
建议使用：

```text
source_scope:
current_product

source_scope:
competitor_product

source_scope:
platform_knowledge

source_scope:
internal_business
```

竞品来源至少应关联：

```text
competitor_id
competitor_product_id
competitor_name
platform_or_marketplace
captured_at
```

竞品资料可以支持：

- 竞品卖点；
- 竞品表达；
- 竞品评论洞察；
- 差异化候选；
- 市场空白假设。

竞品资料不能直接证明：
当前商品拥有某项功能。
当前商品事实必须由当前商品自己的来源支持。

---

## Evidence Link

Evidence Link 是独立关系对象，不是证据文本副本。
概念结构：

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

### Target Entity Types

可以包括：

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

### Evidence Roles

至少支持以下概念：

```text
supports
contradicts
qualifies
provides_context
example_only
```

同一个 Fragment 可能：

- 支持某项结论；
- 反驳某项结论；
- 限定结论的适用范围；
- 只提供背景；
- 作为示例但不证明总体情况。

---

## Evidence Classes

延续 DEC-008，业务内容必须明确区分：

### Explicit Fact

来源直接明确表达的事实。
要求：

- 至少一个直接支持 Fragment；
- 来源版本有效；
- 引用定位真实；
- 不依赖模型推断填补关键内容。

### Evidence-backed Insight

由事实、评论、访谈、调查或统计支持的洞察。
要求：

- 关联支持证据；
- 可以关联反向证据；
- 说明样本限制；
- 不得把单条评论扩大为普遍结论。

### Model Inference

模型根据现有事实和证据作出的合理推断。
要求：

- 明确标记为推断；
- 不得显示为已验证事实；
- 不得直接成为无条件 Proof Point。

### Hypothesis to Validate

当前证据不足、但值得测试的业务假设。
要求：

- 明确标记待验证；
- 不得作为确定性营销承诺；
- 可以在 Human Review 中被用户接受为策略实验方向。

### Insufficient Information

系统明确无法形成可靠结论。
要求：

- 不用模型猜测填补；
- 说明缺失的信息；
- 必要时触发用户补充或异常暂停。

---

## Evidence Requirements by Business Layer

### Facts

每个 Explicit Fact 必须关联直接 Source Fragment。
用户当前手动输入本身可以作为直接 Source Fragment。
模型不得生成没有来源的 Explicit Fact。

### Insights

Insight 可以基于：

- Valid Facts；
- Review Fragments；
- Interview Records；
- Survey Records；
- Dataset Statistics；
- Competitor Review Evidence。

Insight 应记录：

```text
evidence_class
supporting_fragment_ids[]
contradicting_fragment_ids[]
dataset_statistic_ids[]
analysis_summary
evidence_limitations
sample_size
coverage
```

以上字段名称是概念性的。

### Positioning Candidates

定位候选属于业务策略推断，不是原始事实。
应记录：

```text
based_on_fact_ids[]
based_on_insight_ids[]
competitor_evidence_ids[]
inference_summary
validation_status
```

定位候选通常属于：

```text
Evidence-backed Strategic Inference
```

不能被表示为来源原文直接给出的事实。

### Marketing Brief

Proof Point 必须能够回溯到：

```text
Proof Point
→ Fact
→ Evidence Link
→ Fragment
→ Source Version
```

Content Angle 可以由 Insight 和 Positioning 推导，但应保存：

```text
Content Angle
→ Positioning
→ Insight
→ Evidence
```

Hypothesis-based Angle 允许进入候选内容角度，但必须明确标记：

```text
requires_validation
```

且不能转化为确定性商品承诺。

---

## Retrieved Fragment vs Formal Evidence

RAG 召回流程正式定义为：

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

检索结果初始只能称为：

```text
Retrieved Fragment
```

或：

```text
Candidate Evidence
```

只有满足以下条件后才能成为正式 Evidence：

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

## Preventing Hallucinated Source References

模型不得自由生成：

- `source_id`；
- `source_version_id`；
- `fragment_id`；
- 文件名；
- 页码；
- 评论 ID；
- URL；
- 引用位置。

推荐流程：
Step 1：系统提供允许引用的候选 Fragment

```text
frag_101
frag_102
frag_103
```

Step 2：模型只能从允许集合中选择

```text
supporting_fragment_ids:
- frag_101
- frag_103
```

Step 3：确定性 Validator 检查
至少检查：

- ID 是否存在；
- 是否属于当前任务；
- 是否来自允许的 Source Scope；
- Source Version 是否可用；
- 是否是本次 Evidence Package 中的候选；
- 是否重复；
- 是否已失效；
- Locator 是否存在。

Step 4：写入 Evidence Link
只有校验通过的引用才能进入正式业务对象。
禁止只保存模型生成的自然语言引用，例如：

```text
来源：产品说明书第 3 页
```

但系统中不存在真实 Fragment ID 和 Locator。

---

## Source Set Version

一个 Skill 通常依赖一组来源。
建议引入：

```text
SourceSetVersion
├── source_set_version_id
├── task_id
├── purpose
├── source_version_ids[]
├── created_at
└── content_hash
```

例如：

```text
customer_insight_source_set_v3
```

对应 Insights Version 应记录：

```text
based_on_source_set_version_id:
customer_insight_source_set_v3
```

用户新增评论、访谈或竞品资料后，应生成新的 Source Set Version。
旧业务结果可以据此判断是否基于旧来源集合。
Source Set Version 不复制所有来源内容，只固定参与分析的具体 Source Version 集合。

---

## Source Version Status

Source Version 至少需要表达以下概念状态：

```text
available
processing
invalid
unavailable
superseded
deleted
restricted
```

### available

当前可正常访问和引用。

### processing

尚未完成解析或索引。

### invalid

解析失败、内容损坏或已确认不可信。

### unavailable

暂时无法访问，但历史快照可能仍存在。

### superseded

已有新版本替代，旧版本保留审计。

### deleted

用户要求删除，不允许用于新的分析。

### restricted

来源存在，但当前任务、用户或 Skill 没有权限。

---

## Source Invalidation

来源失效后，应根据正式 Evidence Link 判断受影响的业务对象。
由于 MVP 仍采用阶段级失效，不实现完整字段级依赖图，采用以下原则：

```text
关键 Fact 的主要来源失效
→ Fact Stage 及其下游失效

Insight 的主要证据来源失效
→ Insight Stage 及其下游失效

仅 Context 或 Example 来源失效
→ 记录 Warning，由 Validator 决定是否触发阶段失效
```

来源失效处理至少包括：

1. 更新 Source Version 状态；
2. 查询依赖该来源的 Evidence Links；
3. 确定受影响的业务层；
4. 创建 Invalidation Event；
5. 标记对应阶段失效；
6. 清除无效 Current Truth Pointer；
7. 保留历史记录；
8. 从最早失效阶段重新执行。

---

## Source Conflict

来源之间可能冲突，例如：

```text
用户表单：
容量 500 mL

商品说明书：
容量 450 mL
```

系统不得由模型自行选择一个值并写成事实。
应创建结构化 Source Conflict：

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

### Conflict Status

概念状态：

```text
open
user_resolved
rule_resolved
source_superseded
unresolved
```

关键事实冲突时：

```text
Fact Stage
→ waiting_input
```

或：

```text
Fact Stage
→ paused
```

用户确认后生成新的事实版本，并记录冲突处理原因。

---

## Evidence Package

Skill 不直接接触整个来源数据库。
执行前应构建可复现的 Evidence Package：

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

Evidence Package：

- 是一次执行输入快照；
- 不是新的 Source；
- 不修改原始来源；
- 限制模型可见证据范围；
- 支持 Skill 独立测试；
- 支持重现模型当时看到了什么；
- 支持确定性引用校验；
- 支持上下文控制。

Skill 输出中的 Fragment ID 必须来自对应 Evidence Package 的允许集合。

---

## Frontend Evidence Presentation

前端展示 Fact、Insight、Positioning 或 Brief Item 时，应尽量允许用户查看：

- 结论；
- Evidence Class；
- 支持来源数量；
- 反向证据；
- 来源名称；
- 原文摘录；
- Locator；
- 样本范围；
- 证据限制；
- 来源冲突；
- 模型推断标识；
- 待验证假设标识。

Example

```text
用户洞察：
部分用户担心杯盖漏水

证据等级：
Evidence-backed Insight

支持证据：
12 条评论

样本范围：
共 120 条有效评论

示例原文：
"放包里有一点漏水……"

来源：
商品评论导出文件，第 47 行
```

对于 Model Inference，必须提示：

```text
该结论为模型推断，
当前没有直接用户反馈验证。
```

对于 Hypothesis：

```text
待验证假设，
不建议作为确定性营销承诺。
```

---

## Task and Workspace Isolation

所有以下对象必须关联当前任务或合法 Workspace：

- Source；
- Source Version；
- Document；
- Record；
- Fragment；
- Evidence Link；
- Source Set Version；
- Evidence Package。

检索、模型调用和 Skill Runtime 不能跨任务召回其他用户的私有资料。
即使 Fragment ID 真实存在，如果不属于当前授权范围，也必须拒绝引用。

---

## Source Deletion Boundary

删除来源需要区分：

```text
从当前任务移除
删除原始文件
删除解析文本
删除 Fragment
删除检索索引
删除向量
删除 Evidence Link
删除正式业务结果
```

用户要求彻底删除时，系统应能够：

- 删除或不可恢复地隔离原始对象；
- 删除解析结果；
- 删除检索索引；
- 将相关 Fragment 标记为不可用；
- 停止在新分析中使用；
- 检查依赖结果并触发必要失效；
- 根据后续数据政策保留最小非内容审计记录。

最终数据保留与删除政策尚未确认。

---

## Public Web Sources

对于公开网页或平台规则，至少应保存：

```text
url
source_version_id
captured_at
content_hash
locator
availability_status
```

条件允许时保存内容快照或可验证摘要。
网页发生变化后，不得假设当前页面仍支持基于旧版本生成的历史结论。
平台规则属于时间敏感来源，后续使用时需要确认其版本或抓取时间。

---

## Authoritative Boundaries

Raw Information Current Truth

```text
Source Version
+
Document / Record
+
Fragment
```

Business Conclusion Current Truth

```text
Versioned Domain Object
+
Current Truth Pointer
```

Relationship between Conclusion and Source

```text
Evidence Link
```

Temporary Retrieval Output

```text
Retrieved Candidate Fragment
```

检索临时结果不属于正式业务 Current Truth。

---

## Accepted Data Flow

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

## Accepted Design Principles

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

## Reason

项目的核心可靠性要求包括：

- 来源可追溯；
- 防止无依据事实；
- 防止虚构引用；
- 区分事实与推断；
- 支持来源变化；
- 支持阶段失效；
- 支持用户审核；
- 支持评论统计；
- 支持竞品隔离；
- 支持 RAG 评估；
- 支持前端解释结论来源。

如果只保存自然语言 `source_ref` 或文件名，将无法可靠回答：

- 这条事实来自哪一页？
- 这条洞察基于哪些评论？
- 该比例是否来自完整数据集？
- 模型是否虚构了引用？
- 来源更新后哪些结果需要失效？
- 竞品资料是否被误当成当前商品资料？
- 用户当时审核的证据是什么？

因此采用版本化 Source、可定位 Fragment 和显式 Evidence Link。

---

## Impact

该决定将影响：

- 数据库设计；
- 文件解析；
- RAG；
- Skill Input；
- Skill Output；
- Evidence Validator；
- Workflow State；
- Invalidation；
- Human Review；
- Frontend；
- Evaluation；
- 数据隔离；
- 删除策略；
- 平台知识管理；
- Technical Spike；
- 后续 Source and Retrieval API。

后续任何检索方案都必须回答：
如何返回真实、可定位、版本明确、权限正确的 Fragment ID，并使其通过 Evidence Validator 后绑定到业务对象？

---

## Decision Boundary

本决定已经确认：

- Source、Source Version、Document、Record、Fragment 和 Evidence Link 分层；
- 业务结论引用具体 Source Version；
- 用户手动输入是正式 Source；
- 评论采用单条 Record；
- 评论 Fragment 必须保留原评论关系；
- 竞品来源与当前商品来源隔离；
- Evidence Link 是独立关系对象；
- Evidence Role 显式；
- 继续使用五类 Evidence Class；
- Fact 必须有直接来源；
- Insight 可以基于多条证据和统计；
- Positioning 记录事实、洞察和竞品证据链；
- Brief Proof Point 必须回溯到 Fact；
- RAG 召回结果只是 Candidate Evidence；
- 模型不能自由生成 Source 或 Fragment ID；
- Fragment ID 必须经过确定性校验；
- Source Set Version 固定某次分析的来源集合；
- 来源失效触发依赖检查；
- 关键来源冲突需要暂停或用户处理；
- 频率统计必须基于完整可计数数据；
- Evidence Package 是 Skill 的可复现输入；
- 前端应展示 Evidence Class、原文和限制；
- 私有来源必须按 Task 或 Workspace 隔离。

本决定尚未确认：

- 最终数据库字段；
- Source ID 格式；
- Fragment ID 格式；
- Fragment 切分规则；
- Chunk Size；
- Chunk Overlap；
- Parser；
- OCR；
- Embedding 模型；
- 全文检索；
- 向量数据库；
- Top-K；
- Reranker；
- Evidence Strength 评分；
- 网页抓取方案；
- 评论导入格式；
- Source Retention；
- 删除策略；
- 官方平台知识来源；
- 前端 Evidence UI；
- 最终 API。

---

## Related Session

- [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)

## Related Decisions

- [DEC-008 — Evidence Classes](dec-008-tiered-evidence-and-traceable-conclusions.md)（本决定 Amends）
- [DEC-009 — Stage Invalidation](dec-009-stage-level-invalidation-and-partial-rerun.md)
- [DEC-012 — Structured Workflow State](dec-012-stage-state-and-structured-business-items.md)
- [DEC-014 — On-demand Hybrid RAG](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（本决定 Amends）
- [DEC-017 — Customer Insight Skill Adapt](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)
- [DEC-018 — Product Positioning Skill Adapt](dec-018-adapt-product-differentiation-for-positioning-skill.md)
- [DEC-024 — Versioned Domain State and Compact LangGraph State](dec-024-versioned-domain-state-and-compact-langgraph-state.md)

## Related RFC

None

## Supersedes

None

## Amends

DEC-008 and DEC-014 by defining detailed source, fragment and formal evidence boundaries.

---

## Notes

- 本决定为**概念层来源与证据架构**确认：`Source → Source Version → Document / Record → Fragment → Evidence Link → Versioned Domain Object` 分层；版本化来源；可定位 Fragment；显式 Evidence Link（独立关系对象）；Evidence Role（supports / contradicts / qualifies / provides_context / example_only）；五类 Evidence Class（承接 DEC-008）；Retrieved Fragment vs Formal Evidence 边界；防止虚构来源引用（模型只能从候选 Fragment ID 集合选择 + 确定性 Validator）；Source Set Version；Source Version Status；来源失效与冲突；Evidence Package（Skill 可复现输入）；当前商品与竞品隔离；任务 / Workspace 隔离；频率统计需完整可计数数据。
- 本决定 **Amends** DEC-008（细化 Evidence Class 落地所需的来源层、Evidence Link 与 Fragment 级可追溯边界）与 DEC-014（细化 RAG 召回结果为 Candidate Evidence、须经确定性 Validator 与 Evidence Link 才成为正式证据），**不推翻**两者既有结论，而是在其基础上补充更精细的来源、片段与正式证据边界。
- 本决定与 DEC-024 一致：正式业务结果以版本化 Domain Object + Current Truth Version Pointer 表达；Evidence Link 是 `Versioned Domain Object ↔ Fragment` 之间的正式关系对象；来源失效触发 InvalidationEvent（承接 DEC-009）；Source Set Version / Evidence Package 作为 Skill 输入快照与 Version Dependencies 配合。
- 概念 Source and Evidence Specification 见 [../specs/evidence/source-and-evidence-specification.md](../specs/evidence/source-and-evidence-specification.md)（仅概念 Schema / 来源类型 / 状态 / Evidence 关系 / 边界，**不**含最终数据库表 / Parser / RAG 代码 / Embedding / Vector Store / API / 正式 Evidence UI）。
- Development Status 保持 `NOT READY`。本决定未启动任何业务代码；在 `Product Intake & Fact Extraction Skill Contract` 确认前，不设计正式 Prompt 或实现代码。
