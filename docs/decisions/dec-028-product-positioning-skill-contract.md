# DEC-028：Product Positioning Skill 采用多候选、证据约束与强制人工决策契约

> **Type:** Skill Contract / Strategy Architecture
> **Status:** Accepted
> **Date:** 2026-07-28
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)（概念 Skill Spec，仅概念）
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** [DEC-018](dec-018-adapt-product-differentiation-for-positioning-skill.md) by defining the formal Product Positioning Skill Contract（在 DEC-018 评估结论「`product-differentiation-shopify` 作为 Product Positioning Skill 改造供体」基础上，正式定义该 Skill 的概念层执行契约，**不推翻** DEC-018 的评估结论与 Adapt 方向）。

---

## 用户确认

用户对该 Product Positioning Skill Contract Proposal 明确回复：

> 确认

本决定经 Decision Gate 通过，记录为 Accepted Decision（Type: Skill Contract / Strategy Architecture）。

被接受的核心结论：

- Product Positioning Skill 负责将当前有效商品事实、用户洞察、竞品证据和业务约束，组合成多个可解释、可比较、可追溯的商品定位候选。
- Positioning 属于战略推断，不属于 Explicit Fact。系统不得将定位候选表示为来源中直接存在的事实，也不得由模型自动决定最终定位。
- 所有 Proof Point 必须回溯到当前有效商品事实；竞品证据不能证明当前商品拥有某项能力；无直接用户证据时仍可生成定位候选，但目标用户、用户需求和市场机会必须标记为假设并传播证据限制。
- Product Positioning Skill 输出候选后，工作流必须进入强制 Human Review。只有经用户选择、修改、合并或确认后形成的 Approved Strategy Version，才能进入 Marketing Brief Generation。

---

## Decision

MVP 的第三个核心业务 Skill 正式定义为：

```text
Product Positioning Skill
```

其业务目标是：

将当前有效商品事实、用户洞察、竞品证据和业务约束，转换为多个可解释、可比较、可供人工决策的商品定位候选。

该 Skill 只生成：

- Positioning Candidates；
- Comparison Matrix；
- Recommendation；
- Assumptions；
- Evidence Limitations；
- Strategic Risks；
- Human Review Package。

该 Skill 不负责：

- 创建新的商品事实；
- 自动决定最终定位；
- 自动创建 Approved Strategy；
- 自动生成 Marketing Brief；
- 自动发布内容；
- 将竞品能力归因于当前商品；
- 使用无依据比较级或最高级；
- 将 Hypothesis 表达为已验证用户事实。

### Positioning Nature

Positioning 属于：

```text
Strategic Inference
```

而不是：

```text
Explicit Fact
```

定位的推导链为：

```text
Valid Facts
+
Valid or Limited Insights
+
Competitor Evidence
+
Business Constraints
↓
Positioning Candidates
↓
Human Review
↓
Approved Strategy Version
```

系统不得将模型生成的定位候选描述为：

- 已证明的市场结论；
- 唯一正确答案；
- 用户已经确认的真实需求；
- 来源文档直接表达的事实。

---

## Skill Inputs

### Required Inputs

#### Current Valid Facts Version

必须满足：

```text
Fact Stage = valid
```

所有商品能力、规格、认证、性能和 Proof Point 必须来自当前有效 Facts Version。

#### Current Insights Version

允许：

```text
valid
```

或：

```text
valid_with_limitations
```

Positioning Skill 必须读取：

- Evidence Class；
- Evidence Coverage；
- Supporting Evidence；
- Contradicting Evidence；
- Evidence Limitations；
- Hypothesis 标识；
- Source Scope。

#### Product and Task Context

至少包括：

- 商品身份；
- 商品品类；
- 核心用途；
- 当前市场或业务目标；
- 用户明确提供的业务约束。

### Optional Inputs

可以包括：

- 竞品商品事实；
- 竞品评论洞察；
- 市场常见价值表达；
- 品牌方向；
- 价格带；
- 销售渠道；
- 目标平台；
- 禁止表达；
- 已有目标用户；
- 企业希望测试的战略方向。

缺少竞品资料时，仍允许生成定位候选，但不得输出确定性的竞品优势或市场空白结论。

---

## Facts, Insights and Positioning Boundary

### Fact

例如：

```text
杯体重量为 260 克。
```

### Insight

例如：

```text
多条用户反馈表明，
通勤携带时商品重量会影响购买选择。
```

### Positioning

例如：

```text
为每天携带水杯通勤的城市上班族，
提供更轻便、减少携带负担的日常保温解决方案。
```

Positioning 通常属于：

```text
Evidence-backed Strategic Inference
```

当用户证据有限时，属于：

```text
Hypothesis-heavy Strategic Candidate
```

不得标记为 Explicit Fact。

---

## Positioning Candidate Concept

每个定位候选概念上至少包括：

```text
PositioningCandidate
├── candidate_id
├── candidate_title
├── target_segment
├── usage_context
├── job_or_core_need
├── category_frame
├── value_proposition
├── key_benefits[]
├── differentiation
├── reasons_to_believe[]
├── proof_points[]
├── based_on_fact_ids[]
├── based_on_insight_ids[]
├── competitor_evidence_ids[]
├── assumptions[]
├── evidence_limitations[]
├── strategic_risks[]
├── evidence_profile
├── ranking_rationale
└── review_status
```

以上是概念结构，不是最终数据库 Schema。

---

## Positioning Elements

### Target Segment

回答：

> 优先服务谁？

Target Segment 可以来自：

- 直接用户证据；
- 用户明确提供的目标人群；
- 评论、访谈或问卷中反复出现的用户类型；
- 有证据支持的使用场景。

若缺乏直接证据，应标记为：

```text
Target Segment Hypothesis
```

不得凭空生成过于精确的人口统计特征，例如：

- 精确年龄段；
- 收入；
- 城市等级；
- 性别；
- 职业；
- 家庭结构。

除非来源明确支持。

### Usage Context

回答：

> 用户在什么具体场景中使用或购买商品？

场景应尽量来自：

- 用户证据；
- 当前商品用途；
- 业务方明确输入；
- 可验证品类场景。

### Job or Core Need

回答：

> 用户希望完成什么任务或获得什么结果？

它应描述用户任务，而不只是商品功能列表。

### Category Frame

回答：

> 用户应该把商品理解成什么类别或解决方案？

允许生成新的战略品类表达，但如果不是已有市场分类，必须明确它是定位候选，而不是行业既定事实。

### Value Proposition

回答：

> 为什么目标用户应选择该商品？

建议概念结构：

```text
For [target segment]
who [job or need],
this product is [category frame]
that [primary value],
because [reasons to believe].
```

Value Proposition 必须能够连接：

```text
Target Segment
→ User Need
→ Product Capability
→ Business Value
```

### Differentiation

回答：

> 相比当前替代方案或竞品，为什么值得优先考虑？

差异化可以来自：

- 当前商品真实能力；
- 可验证属性差异；
- 对用户问题的不同回应；
- 不同目标场景；
- 不同服务人群；
- 不同价值表达；
- 竞品用户证据与当前商品能力之间的匹配。

差异化不要求绝对技术独占，但必须真实、清晰且不过度承诺。

### Reasons to Believe

回答：

> 用户为什么应该相信该价值主张？

可以包括：

- 有效商品规格；
- 材料和组成；
- 检测结果；
- 认证；
- 商品结构或设计机制；
- 用户反馈；
- 售后或保障。

所有 Reasons to Believe 必须能够回溯到有效 Fact 或 Evidence。

### Proof Points

Proof Point 是后续 Marketing Brief 可以直接使用的证明材料。

链路必须成立：

```text
Proof Point
→ Valid Fact
→ Evidence Link
→ Fragment
→ Source Version
```

例如：

```text
260 克杯体重量
500 mL 容量
304 不锈钢材质
检测报告中的具体性能结果
```

以下内容不能作为 Proof Point：

```text
用户一定会喜欢
非常适合年轻人
市场潜力巨大
行业领先
最佳选择
```

---

## Competitor Gap Boundary

### Evidence-supported Gap

当存在可比较的竞品事实和用户证据时，可以形成较强差异化候选。

例如：

```text
竞品评论反复提到杯盖难清洗
+
当前商品事实证明杯盖可拆卸
```

可以形成：

> 通过可拆洗结构，回应用户对清洁复杂度的顾虑。

但不得扩张为：

> 比所有竞品都更容易清洗。

除非存在充分、覆盖明确的比较证据。

### Opportunity Hypothesis

当竞品资料有限时，只能表达为：

```text
Opportunity Hypothesis
```

例如：

> 易清洗可能是值得验证的差异化方向。

不得表示为已验证市场空白。

### Prohibited Competitor Claims

禁止：

- 使用竞品评论证明当前商品性能；
- 把单个竞品弱点表述为全市场问题；
- 将未进行实际比较的属性写成"更好"；
- 使用过期竞品页面作为当前市场事实；
- 使用无来源的"行业第一"；
- 将竞品功能写入当前商品 Proof Point。

---

## Candidate Quantity

默认生成：

```text
3 Positioning Candidates
```

允许范围：

```text
Minimum: 2
Maximum: 4
```

原因：

- 单一候选容易被误认为最终答案；
- 过多候选增加 Human Review 负担；
- 三个候选能够体现战略取舍。

证据不足时，不得为了达到数量要求生成重复、空洞或虚假候选。

候选之间必须存在实质差异，例如：

```text
Candidate A:
通勤轻量

Candidate B:
密封安心

Candidate C:
清洁便利
```

不得只是同一句定位的语言改写。

---

## Candidate Strategy Types

可以根据证据生成不同战略方向：

### Need-led Candidate

围绕用户最重要的问题或需求。

### Product-strength-led Candidate

围绕当前商品最可信、最突出的能力。

### Gap-led Candidate

围绕竞品问题或市场机会假设。

并非每次必须严格各生成一个，具体应由证据决定。

---

## Candidate Ranking

不采用模型生成的不透明综合数字分数，例如：

```text
positioning_score = 91
```

候选排序应使用可解释维度：

```text
product_truth_fit
customer_relevance
evidence_support
differentiation_credibility
strategic_clarity
execution_potential
risk_level
```

### Product Truth Fit

定位是否真实建立在当前商品能力上。

### Customer Relevance

定位是否回应真实或合理的用户问题。

### Evidence Support

候选依赖强证据、有限证据还是假设。

### Differentiation Credibility

差异化是否真实、可解释、不过度承诺。

### Strategic Clarity

目标用户、场景、核心需求和价值是否清晰。

### Execution Potential

是否能够转化为明确的 Marketing Brief。

### Risk Level

是否存在无依据比较、敏感功效、来源不足或品牌冲突。

模型可以输出：

- 推荐候选；
- 推荐理由；
- 主要风险；
- 成功条件；
- 需要验证的假设。

推荐不能自动成为 Approved Strategy。

---

## Limited Evidence Mode

当 Customer Insight Stage 为：

```text
valid_with_limitations
```

Positioning Skill 仍可运行，但必须：

- 显示用户洞察主要属于 Hypothesis；
- 降低对 Target Segment 的确定性表达；
- 不使用"用户普遍""用户最关心"等表述；
- 将重要需求标记为待验证；
- 避免生成过度精确的用户画像；
- 在每个候选中展示 Evidence Limitations；
- 要求 Human Review 明确接受相关假设。

例如：

```text
Target Segment Candidate:
经常携带水杯通勤的人群

Status:
Target Segment Hypothesis

Limitation:
当前没有直接访谈或当前商品评论支持。
```

---

## Skill Outputs

Skill 输出分为以下五部分。

### 1. Positioning Context

```text
facts_version_id
insights_version_id
competitor_source_set_version_id
business_constraints
input_limitations[]
```

### 2. Positioning Candidates

```text
candidates[]
```

默认三个，允许二至四个。

### 3. Comparison Matrix

至少包括：

```text
candidate
target_segment
core_need
primary_value
key_differentiation
evidence_profile
main_risk
```

用于帮助用户理解不同战略取舍。

### 4. Recommendation

```text
recommended_candidate_id
recommendation_rationale
conditions_for_success[]
validation_needed[]
```

模型推荐只是一项建议。

### 5. Workflow Decision

```text
stage_decision:
- ready_for_review
- ready_for_review_with_limitations
- waiting_input
- paused
- failed
```

生成候选后，工作流必须进入 Human Review。

不得直接进入 Marketing Brief Generation。

---

## Human Review Package

Human Review 至少需要展示：

- 每个定位候选；
- Target Segment；
- Usage Context；
- Job or Core Need；
- Category Frame；
- Value Proposition；
- Differentiation；
- Reasons to Believe；
- Proof Points；
- Supporting Facts；
- Supporting Insights；
- Competitor Evidence；
- Assumptions；
- Evidence Limitations；
- Strategic Risks；
- 模型推荐理由。

允许用户执行：

```text
select
edit
merge
reject
request_more_information
```

### select

选择一个候选作为主要定位方向。

### edit

修改候选中的目标用户、用户需求、价值主张、差异化或证明点。

### merge

合并多个候选的部分内容。

合并后必须重新通过 Validator。

### reject

拒绝单个或全部候选。

### request_more_information

要求补充：

- 商品资料；
- 评论；
- 访谈；
- 竞品资料；
- 检测报告；
- 业务约束；
- 品牌信息。

Human Review 最终形成：

```text
Approved Strategy Version
```

只有 Approved Strategy Version 才能进入 Marketing Brief Generation。

---

## Workflow Decision Boundary

### ready_for_review

事实、洞察和证据足够，可以生成正常定位候选。

### ready_for_review_with_limitations

候选可以进入审核，但存在明显限制，例如：

- 无直接用户反馈；
- 只有竞品用户证据；
- 缺少竞品资料；
- Target Segment 属于假设；
- 市场 Gap 尚未验证。

### waiting_input

例如：

- 用户明确要求竞品差异定位，但没有竞品资料；
- 商品事实不足以形成有意义价值差异；
- 缺少用户明确要求的业务约束；
- 上游提示必须补充关键信息。

默认情况下，证据有限时优先生成带限制候选，而不是过度暂停。

### paused

例如：

- 关键 Fact 已失效；
- 使用错误 SKU；
- 当前商品和竞品资料混淆；
- 定位依赖高风险或无法验证的功效声明；
- 主要竞品来源被撤回；
- 上游存在未解决严重冲突。

### failed

用于技术错误，例如：

- 模型持续无法输出合法 Schema；
- Evidence Package 构建失败；
- Validator 内部错误；
- 数据库存储失败；
- 业务版本写入失败。

---

## Deterministic Validator

定位候选进入 Human Review 前，必须至少检查：

1. Facts Version 当前有效；
2. Insights Version 当前有效或 `valid_with_limitations`；
3. 所有 Fact ID 真实存在；
4. 所有 Insight ID 真实存在；
5. Proof Point 可回溯到有效 Fact；
6. Competitor Evidence 未被表示为当前商品能力；
7. 不存在无来源数值、认证或性能声明；
8. Hypothesis 未被表示为用户共识；
9. 未虚构人口统计特征；
10. 比较级和最高级拥有可靠依据；
11. Reasons to Believe 与商品事实语义相关；
12. Differentiation 未超出竞品证据范围；
13. 候选之间具有实质差异；
14. 候选数量在允许范围内；
15. Evidence Limitations 已传播；
16. Source Version 当前可用；
17. 未使用已失效上游结果；
18. 输出符合 Schema；
19. Proof Point 不包含 Marketing Expression；
20. Approved Strategy 尚未被自动创建。

Validator 不负责决定哪个候选最有创意，而负责保证候选没有违反事实、来源和证据边界。

---

## Responsibility Boundary

### Deterministic Logic

负责：

- 上游版本有效性；
- ID 校验；
- Evidence 校验；
- Proof Point 追踪；
- 比较证据范围；
- Schema；
- 候选数量；
- 版本写入；
- 阶段状态；
- 幂等；
- Current Truth 更新。

### LLM

负责：

- 组合 Facts 和 Insights；
- 提出 Target Segment Candidate；
- 提炼 Job or Core Need；
- 形成 Category Frame；
- 形成 Value Proposition；
- 提出差异化方向；
- 生成多个战略候选；
- 比较候选优缺点；
- 说明假设和风险；
- 生成推荐理由。

### Human

负责：

- 选择最终方向；
- 修改定位；
- 合并候选；
- 拒绝候选；
- 判断品牌和市场适配；
- 接受或拒绝关键假设；
- 决定是否补充资料；
- 形成 Approved Strategy Version。

---

## Evaluation Metrics

### Hard Reliability Metrics

MVP 目标：

```text
Unsupported Proof Point Rate = 0%
Invalid Fact Reference Rate = 0%
Invalid Insight Reference Rate = 0%
Competitor Capability Leakage Rate = 0%
Unsupported Superiority Claim Rate = 0%
Hypothesis Presented as Fact Rate = 0%
```

### Positioning Quality Metrics

包括：

- Target Segment Clarity；
- Job or Need Clarity；
- Fact-to-Value Alignment；
- Insight-to-Positioning Alignment；
- Differentiation Credibility；
- Candidate Distinctiveness；
- Reasons-to-Believe Relevance；
- Evidence Limitation Coverage；
- Strategic Risk Coverage。

### User Value Metrics

包括：

- 用户选择至少一个候选的比例；
- 候选直接接受率；
- 用户修改量；
- 用户拒绝全部候选的比例；
- 从候选生成到 Approved Strategy 的时间；
- Approved Strategy 被最终 Brief 使用的比例。

---

## Required Test Scenarios

### TS-1：Facts and Customer Evidence Are Sufficient

预期：

- 生成三个实质不同的候选；
- Proof Points 全部可追溯；
- 推荐理由清晰；
- 进入 `ready_for_review`。

### TS-2：No Direct Customer Evidence

预期：

- 仍可生成候选；
- Target Segment 和 Need 标记为 Hypothesis；
- 不表达为用户共识；
- 进入 `ready_for_review_with_limitations`。

### TS-3：No Competitor Evidence

预期：

- 可生成 Need-led 和 Product-strength-led 候选；
- 不输出确定性竞品优势；
- 明确差异化限制。

### TS-4：Competitor Reviews Only

预期：

- 可以识别品类机会；
- 不将竞品体验归因于当前商品；
- Gap 标记为 Opportunity Hypothesis。

### TS-5：Unsupported "Industry-leading" Claim

预期：

- 不进入 Proof Point；
- 不作为已验证差异化；
- 除非存在可靠比较证据。

### TS-6：Highly Similar Candidates

预期：

- Validator 拒绝；
- 要求重新生成实质不同的候选。

### TS-7：Invalid Upstream Version

预期：

- 不生成候选；
- 阶段暂停；
- 返回最早需要重跑的上游阶段。

> 以上为**概念测试场景，非最终 Golden Dataset**；最终测试数据、阈值与评价实现未确认。

---

## Skill Contract Summary

```text
Skill:
Product Positioning

Input:
- Valid Facts Version
- Valid or Limited Insights Version
- Optional Competitor Evidence
- Business Constraints

Output:
- 2–4 Positioning Candidates
- Comparison Matrix
- Recommendation
- Assumptions and Limitations
- Human Review Package
- Workflow Decision

Hard Rules:
- No Proof Point without a valid Fact
- No competitor capability attributed to current product
- No hypothesis presented as verified customer truth
- No automatic final positioning decision

Required Next Step:
Human Review
```

---

## Reason

Product Positioning 是从业务事实和用户证据走向营销策略的关键转换层。

如果该层允许：

- 无来源 Proof Point；
- 将竞品能力归因于当前商品；
- 将假设表述为用户共识；
- 只生成一个看似正确的答案；
- 自动替用户做最终战略决策；
- 生成无依据比较级或最高级；

错误会直接传播至：

```text
Product Positioning
→ Approved Strategy
→ Marketing Brief
→ Xiaohongshu Mapping
```

因此该 Skill 必须：

> 生成多个证据边界明确、战略取舍可解释的定位候选，并将最终决策交给用户。

---

## Impact

该决定将影响：

- Positioning Domain Model；
- Skill Input / Output；
- Human Review；
- Approved Strategy；
- Marketing Brief Skill；
- Evidence Validator；
- Comparison Matrix；
- 前端审核页面；
- Evaluation Dataset；
- Positioning Prompt；
- Workflow Graph。

---

## Decision Boundary

本决定已经确认：

- Product Positioning Skill 的业务边界；
- Positioning 属于 Strategic Inference；
- 必须使用当前有效 Facts 和 Insights；
- Insights 可以为 `valid_with_limitations`；
- 默认三个、允许二至四个候选；
- 候选必须具有实质差异；
- Positioning Candidate 核心要素；
- Target Segment Hypothesis；
- Category Frame；
- Value Proposition；
- Differentiation；
- Reasons to Believe；
- Proof Point；
- Proof Point 必须回溯到 Fact；
- Competitor Gap 边界；
- Opportunity Hypothesis；
- 不使用不透明综合 Confidence 分数；
- 使用可解释排序维度；
- 有限证据模式；
- 五部分 Skill 输出；
- 强制 Human Review；
- Human Review 操作；
- Approved Strategy Version；
- Validator 规则；
- LLM、确定性逻辑和人工职责；
- 硬性可靠性指标。

本决定尚未确认：

- 最终 Positioning Schema；
- 最终字段名称；
- 数据库表；
- 候选相似度算法；
- 排序公式；
- 竞品数量；
- 市场研究方法；
- Prompt；
- 模型；
- Human Review UI；
- 品类模板；
- 比较声明规则实现；
- 最终错误代码。

---

## Related Session

[Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)

---

## Related Decisions

- [DEC-008 — MVP 采用分级证据标记与结论可追溯机制](dec-008-tiered-evidence-and-traceable-conclusions.md)（Evidence Classes）
- [DEC-009 — MVP 采用阶段级依赖失效与局部重跑](dec-009-stage-level-invalidation-and-partial-rerun.md)（Stage Invalidation）
- [DEC-015 — Skill 定义为带执行契约的可复用业务能力包](dec-015-contract-based-reusable-business-skills.md)（Contract-based Skill）
- [DEC-018 — Product Differentiation Shopify 作为 Product Positioning Skill 的改造供体](dec-018-adapt-product-differentiation-for-positioning-skill.md)（Product Positioning Candidate Adaptation；**本决定 Amends DEC-018**）
- [DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（Core Skills）
- [DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](dec-024-versioned-domain-state-and-compact-langgraph-state.md)（Versioned Domain State）
- [DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](dec-025-versioned-sources-fragments-and-evidence-links.md)（Source and Evidence Architecture）
- [DEC-026 — Product Intake & Fact Extraction Skill 采用分层输入完整度、零无来源事实与冲突暂停契约](dec-026-product-intake-and-fact-extraction-skill-contract.md)（Product Intake & Fact Extraction Skill Contract；本 Skill 的上游 Facts Layer）
- [DEC-027 — Customer Insight Analysis Skill 采用证据模式与降级假设模式，并禁止虚构用户原声和检索样本频率外推](dec-027-customer-insight-analysis-skill-contract.md)（Customer Insight Analysis Skill Contract；本 Skill 的上游 Insights Layer）

---

## Related RFC

None

---

## Supersedes

None

---

## Amends

**Amends [DEC-018](dec-018-adapt-product-differentiation-for-positioning-skill.md)** by defining the formal Product Positioning Skill Contract。

- DEC-018 评估结论为 Candidate 2（`product-differentiation-shopify`）= Adapt，作为 Product Positioning Skill 的研究与改造供体（不直接使用其分析脚本为最终定位引擎），并保留渐进输入 / 竞品矩阵 / USP / 定位框架为改造方向、关键词匹配仅作辅助信号或基线、输出为待审核定位候选、须重构为 Skill Contract。
- DEC-028 在此基础上正式定义该 Skill 的**概念层执行契约**（业务目标 / 职责 / 非职责 / Positioning 属于 Strategic Inference / 输入 / Facts·Insights·Positioning 边界 / Positioning Candidate 概念 / Target Segment / Usage Context / Job or Core Need / Category Frame / Value Proposition / Differentiation / Reasons to Believe / Proof Point / Competitor Gap 边界 / 候选数量与战略类型 / 可解释排序维度 / 有限证据模式 / 五部分输出 / 强制 Human Review / 暂停失败边界 / Validator 20 项 / 职责边界 / 评价指标 / 测试场景）。
- **不推翻** DEC-018 的评估结论与 Adapt 方向；DEC-018 行作为历史记录不修改，本 Amends 关系仅在此处记录。

---

## Notes

- 本决定保持 **Development Status: NOT READY**。
- 当前**不**创建正式 Positioning Prompt / Skill 代码 / LangGraph Node / Human Review 页面 / 数据库表 / 候选相似度算法 / 排序算法 / 市场研究代码。
- 当前**不**选择模型 / Prompt Framework / 竞品数量 / 排序公式 / Human Review UI 技术 / 数据库 / 高风险比较声明规则实现。
- 当前**不**创建 RFC。
- 在 **Human Review and Approved Strategy Contract** 确认前，**不**实现正式审核 UI 或 Resume 逻辑。
- 概念 Skill Spec 见 [../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)（仅概念，非最终实现）。
- 该 Skill 是 DEC-020 核心链路的第三个 Skill（`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation`）；其输出 Positioning Candidates（经 Human Review 形成的 Approved Strategy Version）是下游 Marketing Brief Generation 的主要输入之一；定位错误会传播至 Marketing Brief 与平台映射。
