# Product Positioning Skill — 概念 Specification

> **Status: CONCEPTUAL（概念）**
> 来源决定：[DEC-028 — Product Positioning Skill 采用多候选、证据约束与强制人工决策契约](../../decisions/dec-028-product-positioning-skill-contract.md)（Accepted，Skill Contract / Strategy Architecture，2026-07-28）。Amends DEC-018。
> 本文件是 DEC-028 的**概念结构化记录**，**不是最终实现契约**。所有字段名、枚举、Schema、阈值、算法、Prompt、模型均未确认。
> Development Status: **NOT READY**。

---

## §0 来源与范围

本 Specification 把 DEC-028 已确认的 Skill Contract 整理为结构化概念规格。本 Skill 是 DEC-020 核心链路的**第三个 Core Skill**：

```text
Product Intake & Fact Extraction
→ Customer Insight Analysis
→ Product Positioning   (本文件)
→ Human Review Gate
→ Marketing Brief Generation
→ Xiaohongshu Brief Mapping
```

承接 DEC-008（五类 Evidence Class）、DEC-009（阶段级失效）、DEC-015（Contract-based Skill）、DEC-018（`product-differentiation-shopify` 改造供体，Amended by DEC-028）、DEC-020（MVP Core Skills）、DEC-024（版本化 Domain Objects + Current Truth Pointers）、DEC-025（Source / Source Version / Fragment / Evidence Link + Evidence Package + Source Scope 隔离）、DEC-026（上游 Facts Layer 契约）、DEC-027（上游 Insights Layer 契约）。

本 Skill 输出 **Positioning Candidates**，经强制 Human Review 形成下游可用的 **Approved Strategy Version**，是下游 Marketing Brief Generation 的主要输入之一。

---

## §1 Business Goal

将当前有效商品事实、用户洞察、竞品证据和业务约束，组合成多个可解释、可比较、可追溯、可供人工决策的商品定位候选。

该 Skill **不**追求「生成唯一正确答案」，而是：只生成证据边界明确、战略取舍可解释、来源可追溯的定位候选，并将最终战略决策交给用户。

---

## §2 Responsibilities

- 上游版本有效性确认（Facts / Insights）；
- 证据边界识别（强证据 / 有限证据 / 假设）；
- 目标人群候选生成（Target Segment Candidate）；
- 使用场景识别（Usage Context）；
- 核心任务或需求提炼（Job or Core Need）；
- 战略品类框架生成（Category Frame）；
- 价值主张形成（Value Proposition）；
- 差异化方向提出（Differentiation）；
- 信任理由与证明点组合（Reasons to Believe / Proof Points）；
- 候选之间实质差异保证；
- 假设与证据限制说明；
- 战略风险说明；
- 可解释候选排序与推荐理由；
- 输出可追溯、可版本化的定位候选 / 比较矩阵 / 推荐 / 假设与限制 / 人工审核包 / 阶段决策。

---

## §3 Non-responsibilities

该 Skill **不**负责：

- 创建新的商品事实；
- 修改用户洞察；
- 自动决定最终定位；
- 自动创建 Approved Strategy；
- 自动生成 Marketing Brief；
- 生成小红书文案；
- 自动发布营销内容；
- 将竞品能力归因于当前商品；
- 使用无来源数值、认证或性能声明；
- 使用无依据比较级或最高级；
- 将假设表达为已验证用户事实；
- 执行市场研究或市场调研。

---

## §4 Inputs

概念上接收：

```text
Current Valid Facts Version
+
Current Valid or Limited Insights Version
+
Optional Competitor Evidence
+
Business Constraints
+
Product and Task Context
```

### Required Inputs

- **Current Valid Facts Version**（必须 `Fact Stage = valid`）；
- **Current Insights Version**（允许 `valid` 或 `valid_with_limitations`）；
  - Positioning Skill 必须读取：Evidence Class / Evidence Coverage / Supporting Evidence / Contradicting Evidence / Evidence Limitations / Hypothesis 标识 / Source Scope；
- **Product and Task Context**：商品身份 / 商品类目 / 核心用途 / 当前市场或业务目标 / 用户明确提供的业务约束。

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

> 缺少竞品资料时，仍允许生成定位候选，但**不得**输出确定性的竞品优势或市场空白结论。
>
> 承接 DEC-024：Skill 输入为可复现输入快照（当前有效 Facts Version / 当前有效或受限 Insights Version / 可选竞品 Evidence Set Version）；Proof Point / based_on_fact_ids[] / based_on_insight_ids[] / competitor_evidence_ids[] 必须指向该输入快照允许的版本化对象，**不**直接读取整个来源数据库 / 检索索引 / 向量库。
>
> 承接 DEC-027：当 Insights Version 为 `valid_with_limitations` 时，本 Skill 必须读取并展示其 Evidence Limitations，不得绕过下游限制。

---

## §5 Facts, Insights and Positioning Boundary

| 类型 | 举例 | 边界 |
|------|------|------|
| **Fact**（来自 DEC-026） | `杯体重量为 260 克` | Explicit Fact；必须可回溯 |
| **Insight**（来自 DEC-027） | `多条用户反馈表明，通勤携带时商品重量会影响购买选择` | Evidence-backed Insight 或 Hypothesis；可被定位引用 |
| **Positioning**（本 Skill） | `为每天携带水杯通勤的城市上班族，提供更轻便、减少携带负担的日常保温解决方案` | **Strategic Inference**；不是 Explicit Fact |

Positioning 通常属于：

```text
Evidence-backed Strategic Inference
```

当用户证据有限时，属于：

```text
Hypothesis-heavy Strategic Candidate
```

**不得**标记为 Explicit Fact。

> 承接 DEC-008：Fact / Evidence-backed Insight / Model Inference / Hypothesis to Validate / Insufficient Information 五类须明确区分。Positioning 属于在 Fact + Insight + 竞品证据 + 业务约束之上的 **Strategic Inference**，不得混同为来源直接表达的事实。

---

## §6 Positioning Nature

Positioning 的推导链为：

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

系统**不得**将模型生成的定位候选描述为：

- 已证明的市场结论；
- 唯一正确答案；
- 用户已经确认的真实需求；
- 来源文档直接表达的事实。

---

## §7 Positioning Candidate Concept

每个定位候选概念上至少包括（**非**最终数据库 Schema）：

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

> 承接 DEC-024（版本化 Domain Object + Current Truth Pointer）与 DEC-025（`based_on_fact_ids[]` / `based_on_insight_ids[]` / `competitor_evidence_ids[]` 须经 Evidence Link 关联真实版本化对象；竞品证据**不得**归因为当前商品能力）。

---

## §8 Target Segment

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

**不得**凭空生成过于精确的人口统计特征，例如：

- 精确年龄段；
- 收入；
- 城市等级；
- 性别；
- 职业；
- 家庭结构。

除非来源明确支持。

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

## §9 Usage Context

回答：

> 用户在什么具体场景中使用或购买商品？

场景应尽量来自：

- 用户证据；
- 当前商品用途；
- 业务方明确输入；
- 可验证品类场景。

---

## §10 Job or Core Need

回答：

> 用户希望完成什么任务或获得什么结果？

它应描述**用户任务**，而不只是商品功能列表。

> 承接 DEC-027：Job or Core Need 与用户 Insight 强相关，但属于定位层的战略提炼；当上游 Insight 标记为 Hypothesis 时，对应 Need 也应标记为待验证。

---

## §11 Category Frame

回答：

> 用户应该把商品理解成什么类别或解决方案？

允许生成新的战略品类表达，但如果不是已有市场分类，必须明确它是**定位候选**，而不是行业既定事实。

---

## §12 Value Proposition

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

---

## §13 Differentiation

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

差异化**不**要求绝对技术独占，但必须真实、清晰且不过度承诺。

---

## §14 Reasons to Believe

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

---

## §15 Proof Points

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

以下内容**不能**作为 Proof Point：

```text
用户一定会喜欢
非常适合年轻人
市场潜力巨大
行业领先
最佳选择
```

> 承接 DEC-026：Proof Point 必须指向当前有效 Fact；Fact 失效时 Proof Point 同步失效。
>
> 承接 DEC-025：Proof Point 通过 Fact ID 追溯到 Fragment / Source Version；无 Source Version 的证明材料**不得**进入候选。

---

## §16 Competitor Gap Boundary

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

但**不得**扩张为：

> 比所有竞品都更容易清洗。

除非存在充分、覆盖明确的比较证据。

### Opportunity Hypothesis

当竞品资料有限时，只能表达为：

```text
Opportunity Hypothesis
```

例如：

> 易清洗可能是值得验证的差异化方向。

**不得**表示为已验证市场空白。

### Prohibited Competitor Claims

禁止：

- 使用竞品评论证明当前商品性能；
- 把单个竞品弱点表述为全市场问题；
- 将未进行实际比较的属性写成「更好」；
- 使用过期竞品页面作为当前市场事实；
- 使用无来源的「行业第一」；
- 将竞品功能写入当前商品 Proof Point。

> 承接 DEC-025 Source Scope 与 DEC-027 Competitor Customer Evidence：竞品证据只能用于 Gap 和品类上下文，**不得**归因为当前商品能力。

---

## §17 Candidate Quantity

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

证据不足时，**不得**为了达到数量要求生成重复、空洞或虚假候选。

候选之间必须存在**实质差异**，例如：

```text
Candidate A:
通勤轻量

Candidate B:
密封安心

Candidate C:
清洁便利
```

**不得**只是同一句定位的语言改写。

---

## §18 Candidate Strategy Types

可以根据证据生成不同战略方向：

| 类型 | 含义 |
|------|------|
| **Need-led Candidate** | 围绕用户最重要的问题或需求 |
| **Product-strength-led Candidate** | 围绕当前商品最可信、最突出的能力 |
| **Gap-led Candidate** | 围绕竞品问题或市场机会假设 |

> 并非每次必须严格各生成一个，具体应由证据决定。最终类型名称与组合策略未确认。

---

## §19 Candidate Ranking

**不**采用模型生成的不透明综合数字分数，例如：

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

| 维度 | 含义 |
|------|------|
| `product_truth_fit` | 定位是否真实建立在当前商品能力上 |
| `customer_relevance` | 定位是否回应真实或合理的用户问题 |
| `evidence_support` | 候选依赖强证据、有限证据还是假设 |
| `differentiation_credibility` | 差异化是否真实、可解释、不过度承诺 |
| `strategic_clarity` | 目标用户、场景、核心需求和价值是否清晰 |
| `execution_potential` | 是否能够转化为明确的 Marketing Brief |
| `risk_level` | 是否存在无依据比较、敏感功效、来源不足或品牌冲突 |

模型可以输出：

- 推荐候选；
- 推荐理由；
- 主要风险；
- 成功条件；
- 需要验证的假设。

> 推荐只是一项建议，**不**自动成为 Approved Strategy。最终类型名称、维度权重与排序公式未确认。

---

## §20 Limited Evidence Mode

当 Customer Insight Stage 为：

```text
valid_with_limitations
```

Positioning Skill 仍可运行，但必须：

- 显示用户洞察主要属于 Hypothesis；
- 降低对 Target Segment 的确定性表达；
- 不使用「用户普遍」「用户最关心」等表述；
- 将重要需求标记为待验证；
- 避免生成过度精确的用户画像；
- 在每个候选中展示 Evidence Limitations；
- 要求 Human Review 明确接受相关假设。

> 承接 DEC-027 `valid_with_limitations`：本 Skill **不**绕过上游限制，而是把限制传播到候选并显式标注；缺竞品 / 无直接评论 / Target Segment 假设 / 市场 Gap 未验证时进入 `ready_for_review_with_limitations`，而非隐藏限制继续。

---

## §21 Outputs

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

> 模型推荐只是一项建议。

### 5. Workflow Decision

```text
stage_decision:
- ready_for_review
- ready_for_review_with_limitations
- waiting_input
- paused
- failed
```

生成候选后，工作流**必须**进入 Human Review。

**不得**直接进入 Marketing Brief Generation。

---

## §22 Human Review Package

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

| 操作 | 含义 |
|------|------|
| `select` | 选择一个候选作为主要定位方向 |
| `edit` | 修改候选中的目标用户、用户需求、价值主张、差异化或证明点 |
| `merge` | 合并多个候选的部分内容；**合并后必须重新通过 Validator** |
| `reject` | 拒绝单个或全部候选 |
| `request_more_information` | 要求补充商品资料 / 评论 / 访谈 / 竞品资料 / 检测报告 / 业务约束 / 品牌信息 |

> Human Review 最终形成 **Approved Strategy Version**。只有 Approved Strategy Version 才能进入 Marketing Brief Generation。
>
> Human Review Service / Gate 与 Approved Strategy Version 的正式契约将在 **Human Review and Approved Strategy Contract** 中确认。在该契约确认前，**不**实现正式审核 UI 或 Resume 逻辑。

---

## §23 Workflow Decisions

| 阶段决策 | 触发条件 |
|----------|----------|
| `ready_for_review` | 事实、洞察和证据足够，可以生成正常定位候选 |
| `ready_for_review_with_limitations` | 候选可以进入审核，但存在明显限制（无直接用户反馈 / 只有竞品用户证据 / 缺少竞品资料 / Target Segment 属于假设 / 市场 Gap 尚未验证） |
| `waiting_input` | 用户明确要求竞品差异定位但没有竞品资料 / 商品事实不足以形成有意义价值差异 / 缺少用户明确要求的业务约束 / 上游提示必须补充关键信息。**默认证据有限时优先生成带限制候选，而不是过度暂停** |
| `paused` | 见 §24 |
| `failed` | 见 §25 |

---

## §24 Pause Conditions

`paused` 适用于（需人工判断或权限处理）：

- 关键 Fact 已失效；
- 使用错误 SKU；
- 当前商品和竞品资料混淆；
- 定位依赖高风险或无法验证的功效声明；
- 主要竞品来源被撤回；
- 上游存在未解决严重冲突。

> 承接 DEC-009（阶段级失效与局部重跑）：定位依赖的 Fact 失效时，定位候选需失效或暂停，并返回最早需要重跑的上游阶段。

---

## §25 Failure Conditions

`failed` 适用于技术故障：

- 模型持续无法输出合法 Schema；
- Evidence Package 构建失败；
- Validator 内部错误；
- 数据库存储失败；
- 业务版本写入失败。

> 业务证据不足**不得**错误标记为技术失败（`waiting_input` / `paused` 与 `failed` 严格分离）。

---

## §26 Validator

定位候选进入 Human Review 前，至少检查（20 项）：

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

> 承接 DEC-025 确定性 Evidence Validator + DEC-011「未经校验的 LLM 输出不得自动成为已确认业务事实」。
>
> Validator **不**负责决定哪个候选最有创意，只负责保证候选没有违反事实、来源和证据边界。硬校验失败**不得**写入正式候选、**不得**进入 Human Review、**不得**自动创建 Approved Strategy。

---

## §27 Responsibility Boundary

### Deterministic Logic

上游版本有效性 / ID 校验 / Evidence 校验 / Proof Point 追踪 / 比较证据范围 / Schema / 候选数量 / 版本写入 / 阶段状态 / 幂等 / Current Truth 更新。

### LLM

组合 Facts 和 Insights / 提出 Target Segment Candidate / 提炼 Job or Core Need / 形成 Category Frame / 形成 Value Proposition / 提出差异化方向 / 生成多个战略候选 / 比较候选优缺点 / 说明假设和风险 / 生成推荐理由。

### Human

选择最终方向 / 修改定位 / 合并候选 / 拒绝候选 / 判断品牌和市场适配 / 接受或拒绝关键假设 / 决定是否补充资料 / 形成 Approved Strategy Version。

### Confidence Boundary

MVP **不**使用模型生成的不透明综合数字分数（如 `positioning_score = 91`），改用可解释的排序维度（§19）。

---

## §28 Evaluation Metrics

### Hard Reliability Metrics（MVP 目标，全部 = 0%）

```text
Unsupported Proof Point Rate = 0%
Invalid Fact Reference Rate = 0%
Invalid Insight Reference Rate = 0%
Competitor Capability Leakage Rate = 0%
Unsupported Superiority Claim Rate = 0%
Hypothesis Presented as Fact Rate = 0%
```

### Positioning Quality Metrics

Target Segment Clarity / Job or Need Clarity / Fact-to-Value Alignment / Insight-to-Positioning Alignment / Differentiation Credibility / Candidate Distinctiveness / Reasons-to-Believe Relevance / Evidence Limitation Coverage / Strategic Risk Coverage。

### User Value Metrics

用户选择至少一个候选的比例 / 候选直接接受率 / 用户修改量 / 用户拒绝全部候选的比例 / 从候选生成到 Approved Strategy 的时间 / Approved Strategy 被最终 Brief 使用的比例。

> 模型自报综合分数**不**作为核心评价指标。

---

## §29 Test Scenarios（概念测试场景，非最终 Golden Dataset）

| 场景 | 输入 | 预期 |
|------|------|------|
| **TS-1：Facts and Customer Evidence Are Sufficient** | 有效 Facts + 足够用户证据 | 生成三个实质不同的候选；Proof Points 全部可追溯；推荐理由清晰；阶段 `ready_for_review` |
| **TS-2：No Direct Customer Evidence** | 有效 Facts + 无直接用户证据 | 仍可生成候选；Target Segment 和 Need 标记为 Hypothesis；不表达为用户共识；阶段 `ready_for_review_with_limitations` |
| **TS-3：No Competitor Evidence** | 无竞品资料 | 可生成 Need-led 和 Product-strength-led 候选；不输出确定性竞品优势；明确差异化限制 |
| **TS-4：Competitor Reviews Only** | 仅有竞品评论 | 可以识别品类机会；不将竞品体验归因于当前商品；Gap 标记为 Opportunity Hypothesis |
| **TS-5：Unsupported "Industry-leading" Claim** | 无可靠比较证据的「行业领先」声明 | 不进入 Proof Point；不作为已验证差异化 |
| **TS-6：Highly Similar Candidates** | 候选之间实质差异不足 | Validator 拒绝；要求重新生成实质不同的候选 |
| **TS-7：Invalid Upstream Version** | 上游 Facts / Insights Version 失效 | 不生成候选；阶段暂停；返回最早需要重跑的上游阶段 |

> 以上为**概念测试场景，非最终 Golden Dataset**；最终测试数据、阈值与评价实现未确认。

---

## §30 Open Questions

- 最终 Positioning Schema；
- 最终字段名称；
- 数据库表；
- 候选相似度算法（判断「实质差异」）；
- 候选排序公式 / 维度权重；
- 竞品数量；
- 市场研究方法；
- Prompt；
- Prompt Framework；
- 模型；
- Human Review UI 技术；
- 品类模板；
- 高风险比较声明规则实现；
- 具体错误代码；
- Comparison Matrix 最终字段；
- Approved Strategy Version 最终 Schema；
- Human Review Payload 最终结构；
- Validator 接口；
- Evidence Package 构建接口；
- Business Repository 接口；
- Node Adapter / Skill Service 接口；
- Golden Dataset 最终数据与阈值。

---

## §31 Out-of-Scope

当前**不**创建：

- 正式 Positioning Prompt；
- Skill 代码；
- LangGraph Node；
- Human Review 页面；
- 数据库表；
- 候选相似度算法；
- 排序算法；
- 市场研究代码。

当前**不**选择：

- 模型；
- Prompt Framework；
- 竞品数量；
- 排序公式；
- Human Review UI 技术；
- 数据库；
- 高风险比较声明规则实现。

当前**不**创建 RFC。

保持 **Development Status: NOT READY**。

> 在 **Human Review and Approved Strategy Contract** 确认前，**不**实现正式审核 UI 或 Resume 逻辑。
