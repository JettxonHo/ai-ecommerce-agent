# Marketing Brief Generation Skill — 概念 Specification

> **Status: PRODUCT SEMANTICS ACCEPTED / IMPLEMENTATION CONTRACT CONCEPTUAL**
> 来源决定：[DEC-030 — Marketing Brief Generation 采用 Approved Strategy 锁定、平台无关信息架构与证据限制传播契约](../../decisions/dec-030-marketing-brief-generation-skill-contract.md)、[DEC-046 — 冻结审核、Brief 与导出的产品语义和版本行为](../../decisions/dec-046-review-brief-and-export-product-contract.md)与 [DEC-047 — 渐进式证据、编辑意图与行动导向恢复交互](../../decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)（均 Accepted）。
> 本文件的六个产品语义组、不可变正式版本、语义组差异和“Marketing Brief 修改使当前 Xiaohongshu Brief 失效”行为已确认；字段名、类型、枚举、Schema、Diff 算法、阈值、Prompt 与模型仍是概念，不是最终实现契约。
> Development Status: **NOT READY**。

---

## §0 来源与范围

本 Specification 把 DEC-030 已确认的 Skill Contract 整理为结构化概念规格。本 Skill 是 DEC-020 核心链路的**第四个 Core Skill**：

```text
Product Intake & Fact Extraction
→ Customer Insight Analysis
→ Product Positioning
→ Human Review Gate
→ Marketing Brief Generation   (本文件)
→ Xiaohongshu Brief Mapping
```

承接 DEC-006（四层结构化营销 Brief，Amended by DEC-030）、DEC-009（阶段级失效：Marketing Brief 修改不使上游失效但使 Xiaohongshu Mapping 失效）、DEC-015（Contract-based Skill）、DEC-019（Marketing Brief Generation 次目标 Partial Adapt，Amended by DEC-030）、DEC-020（MVP Core Skills）、DEC-024（版本化 Domain Objects + Current Truth Pointers）、DEC-025（Source / Source Version / Fragment / Evidence Link + Proof Point 追溯）、DEC-028（上游 Positioning Layer 契约）、DEC-029（Authoritative Input = Approved Strategy Version 契约）。

本 Skill 输出**平台无关的 Marketing Brief Version**，是下游 Xiaohongshu Brief Mapping Adapter 及未来其他平台 Adapter 的唯一稳定输入。

---

## §1 Business Goal

将当前唯一有效的 Approved Strategy Version 转换为结构化、平台无关、可追溯的 Marketing Brief，为 Xiaohongshu Brief Mapping Adapter 及未来其他平台 Adapter 提供稳定输入。

该 Skill **不**追求「直接生成最终平台文案」，而是：锁定 Approved Strategy，以平台无关的信息架构组织核心消息、利益点、证据、内容方向和风险边界，把战略转化为可执行的内容结构，同时保留所有假设与证据限制。

---

## §2 Responsibilities

- 明确 Communication Objective；
- 继承目标用户和使用场景；
- 提炼 Core Message；
- 建立 Message Hierarchy；
- 建立 Benefit Hierarchy；
- 组织 Reasons to Believe；
- 关联 Proof Points；
- 识别购买障碍；
- 形成有证据支持的 Objection Responses；
- 生成 Content Angles；
- 建议 Tone and Voice；
- 定义 CTA Objective；
- 传播 Hypotheses；
- 传播 Evidence Limitations；
- 传播 Strategic Risks；
- 输出 Mandatory Messages；
- 输出 Prohibited Claims；
- 生成版本化、平台无关的 Marketing Brief。

---

## §3 Non-responsibilities

该 Skill **不**负责：

- 修改 Approved Strategy；
- 重新选择 Target Segment；
- 重新定义 Job or Core Need；
- 重新定义 Value Proposition；
- 创建新商品 Fact；
- 创建无证据 Proof Point；
- 删除 Hypothesis 或 Evidence Limitation；
- 生成最终小红书标题、正文、标签或封面文案；
- 生成图片、视觉分镜或 Storyboard；
- 自动发布内容。

---

## §4 Authoritative Input

Marketing Brief Skill 只能读取当前有效：

```text
approved_strategy_version_id
```

**不得**作为正式战略输入：

- 未审核 Positioning Candidate；
- Strategy Draft；
- Model Recommendation；
- 已撤回 Approved Strategy；
- 已失效 Approved Strategy；
- 历史旧版本 Strategy。

**必须**输入：

- 当前 Approved Strategy Version；
- 当前有效 Facts Version；
- 与 Strategy 相关的 Insights 和 Hypotheses；
- Business Constraints；
- 当前 Communication Objective 或其候选。

**可选**输入：

- Brand Tone；
- Brand Guidelines；
- 禁用词；
- 上市阶段；
- 价格带；
- 活动信息；
- 销售渠道；
- 内容资产限制；
- 风险或行业规则；
- 用户希望测试的卖点。

---

## §5 Strategy Lock

Marketing Brief 必须将以下字段视为受控战略输入：

```text
target_segment
usage_context
job_or_core_need
category_frame
value_proposition
differentiation
```

**Skill 可以：**

- 精炼表达；
- 拆分信息；
- 调整传播顺序；
- 将战略转化为利益点和内容角度；
- 提高 Brief 的可执行性。

**Skill 不得：**

- 替换目标用户；
- 改变核心用户需求；
- 引入新的定位；
- 将次要能力升级为新的核心定位；
- 创造新的竞争优势；
- 删除用户已经接受但仍真实存在的证据限制。

若生成 Brief 必须改变 Strategy，应返回 `strategy_change_required` 并重新进入 Human Review。不得通过 Brief 生成或编辑绕过 Approved Strategy。

---

## §6 Positioning and Brief Boundary

**Positioning 回答：** 为谁、解决什么问题、为什么值得被选择？

**Marketing Brief 回答：** 为了向该用户传达已批准定位，内容应该重点讲什么、按什么顺序讲、用哪些证据讲，以及哪些内容不能讲？

Marketing Brief 是 Approved Strategy 的沟通执行结构，不是新的战略决策。

---

## §7 Marketing Brief Concept

概念结构：

```text
MarketingBrief
├── brief_id
├── brief_version_id
├── approved_strategy_version_id
├── facts_version_id
├── insights_version_id
├── communication_objective
├── audience
├── audience_context
├── core_message
├── message_hierarchy
├── benefit_hierarchy
├── key_benefits[]
├── reasons_to_believe[]
├── proof_points[]
├── objections[]
├── objection_responses[]
├── content_angles[]
├── tone_and_voice
├── call_to_action_objective
├── mandatory_messages[]
├── prohibited_claims[]
├── accepted_hypotheses[]
├── hypotheses_to_test[]
├── evidence_limitations[]
├── risk_notes[]
├── platform_adaptation_rules
└── workflow_decision
```

以上为概念 Schema，不是最终数据库结构或 Python Model。MarketingBrief 为版本化 Domain Object（承接 DEC-024）。

---

## §8 Communication Objective

每份 Brief 应有一个主要 Communication Objective，可以附带次级目标。概念类型可以包括：

```text
awareness
consideration
education
conversion_support
trust_building
product_launch
```

不得将认知、教育、转化、品牌、售后解释和全部商品功能同时设置为相同优先级。若用户没有明确业务目标，Skill 可以提出候选，但必须标记为 `business_assumption`。

---

## §9 Audience

Audience 必须继承自 Approved Strategy。允许补充与内容执行相关的语境，例如：

```text
Approved Target Segment:
经常随身携带水杯的通勤人群

Content Context:
早高峰、办公室、通勤包携带
```

不得添加无来源支持的精确人口属性。若 Target Segment 属于 Hypothesis，Brief 必须继续标记其 Hypothesis 状态。

---

## §10 Core Message

每份 Brief 必须拥有一个主要 Core Message。要求：

- 与 Approved Value Proposition 一致；
- 可以用一句话说明；
- 不包含无证据承诺；
- 不同时堆叠全部功能；
- 能够指导后续平台内容；
- 不直接作为最终平台文案。

---

## §11 Message Hierarchy

建议采用三级结构：

```text
Primary Message
↓
Secondary Benefits
↓
Supporting Proof
```

概念转换链：

```text
Fact
→ Product Capability
→ User Benefit
→ Core Message
```

Skill 不得跳过中间逻辑，将普通商品参数夸张为不受支持的用户价值。

---

## §12 Benefit Hierarchy

利益点区分为：

```text
primary_benefit
secondary_benefit
supporting_feature
```

MVP 默认：

```text
1 Primary Benefit
2–4 Secondary Benefits
```

资料不足时，不得为了达到数量要求创造无依据利益点。Primary Benefit 必须直接支撑 Approved Strategy。Secondary Benefits 可以增强购买理由，但不能重新定义定位。

---

## §13 Reasons to Believe

Reasons to Believe 可以包括：

- 商品结构；
- 材料；
- 设计机制；
- 检测；
- 认证；
- 用户证据；
- 售后保障。

---

## §14 Proof Points

Proof Points 必须能够建立：

```text
Proof Point
→ Valid Fact
→ Evidence Link
→ Fragment
→ Source Version
```

每个 Proof Point 概念上应保留：

```text
proof_point
fact_id
supporting_fragment_ids[]
source_version_id
approved_wording
```

Skill 可以在不改变含义的前提下，将事实转化为更易理解的表达。不得扩大检测、认证或性能证明实际支持的范围（承接 DEC-025 / DEC-028 / DEC-029 的 Proof Point 追溯与不可升级规则）。

---

## §15 Objection Handling

Brief 应识别一至三个主要购买障碍，例如：漏水、重量、清洗、价格、认证、安全、售后。

每个 Objection Response 必须基于：

```text
Valid Fact
Evidence-backed Insight
Approved Strategy
```

若当前没有足够证据回应，必须标记 `insufficient_evidence`。不得创造保证或承诺。

---

## §16 Content Angles

默认生成：

```text
3–5 Content Angles
```

每个 Angle 概念上至少包括：

```text
angle_title
user_tension
message_focus
supporting_benefits[]
proof_points[]
hypothesis_status
risk_notes[]
```

可以包括：Problem–Solution / Usage Scenario / Product Demonstration / Objection Handling / Comparison Context / Educational / Social Proof / Story-led。

Content Angle 是内容方向，不是最终标题或正文。不同 Angle 必须具有实质差异，不能只是同一卖点的语言改写。

---

## §17 Tone and Voice

Tone and Voice 优先来源于：

1. 用户提供的 Brand Guidelines；
2. Approved Strategy；
3. 商品品类和目标用户；
4. 默认中性品牌表达。

没有品牌规范时，可以输出建议，例如 `clear / practical / trustworthy / non-exaggerated`，但必须标记为 `suggested_tone`。不得假装它是品牌已经确认的正式语气。

---

## §18 CTA Objective

平台无关 Brief 可以定义 CTA 的业务目的，例如：进一步了解 / 查看商品详情 / 查看参数 / 参与测试 / 收藏 / 进入购买考虑。

不得生成特定平台风格的最终 CTA 文案。

---

## §19 Hypothesis Propagation

Marketing Brief 必须继续携带：

```text
accepted_hypotheses[]
hypotheses_to_test[]
```

用户在 Human Review 中接受 Hypothesis，不意味着它可以被转换为 Fact 或用户共识。Hypothesis-based Content Angle 可以作为测试方向，但必须保留 `requires_validation = true`（承接 DEC-029）。

---

## §20 Evidence Limitation Propagation

Marketing Brief 必须继续携带：

```text
evidence_limitations[]
```

Evidence Limitations 不得在 Brief 生成过程中被删除或弱化（承接 DEC-029 的硬规则）。用户接受 Evidence Limitation 不等于客观限制消失；Marketing Brief 必须读取并继续传播至所有 Platform Adapters。

---

## §21 Mandatory Messages

Mandatory Messages 可以包括：

- Approved Core Positioning；
- Primary Benefit；
- 关键 Proof Points；
- 使用限制；
- 必要免责声明；
- 品牌要求；
- 用户明确要求保留的信息。

Mandatory Messages 必须传递给所有 Platform Adapters（Validator 校验未丢失）。

---

## §22 Prohibited Claims

Prohibited Claims 至少包括：

- 无依据的「最好」「第一」「领先」；
- 无来源性能数字；
- 未验证认证；
- 超出检测范围的表述；
- 竞品能力误归因；
- 将 Hypothesis 表达为用户共识；
- 将 Marketing Expression 表达为 Fact；
- 与商品限制冲突的内容；
- 无依据医疗、健康或安全功效；
- 无可靠比较证据的绝对优势。

Prohibited Claims 必须传递给所有 Platform Adapters。

---

## §23 Platform-neutral Boundary

Marketing Brief **不**包含：

- 小红书标题；
- 小红书正文；
- Emoji；
- Hashtags；
- 封面文字；
- 平台字数；
- 平台热词；
- 平台发布格式；
- 最终广告文案。

Marketing Brief **可以**包含：

```text
message_priority
content_angles
tone
proof_points
risk_constraints
CTA objective
platform_adaptation_rules
```

Xiaohongshu Brief Mapping Adapter 可以改变表达结构，但不能改变：Audience / Core Message / Benefit Hierarchy / Proof Points / Evidence Limitations / Prohibited Claims / Approved Strategy。

---

## §24 Outputs

输出固定为六个产品语义组。下列字段仅为概念展开，不是最终公共 Schema；没有可靠内容时不得为满足分组而制造内容。

**1. Objective and Audience**

```text
communication_objective
audience
audience_context
```

**2. Message Architecture**

```text
core_message
message_hierarchy
benefit_hierarchy
```

**3. Reasons to Believe and Evidence**

```text
reasons_to_believe[]
proof_points[]
```

**4. Execution Direction**

```text
objections[]
objection_responses[]
content_angles[]
tone_and_voice
CTA_objective
```

**5. Constraints and Honesty**

```text
mandatory_messages[]
prohibited_claims[]
hypotheses_to_test[]
evidence_limitations[]
risk_notes[]
```

**6. Version and Workflow Context**

```text
brief_version_id
approved_strategy_version_id
facts_version_id
insights_version_id
input_limitations[]
stage_decision:
- valid
- valid_with_limitations
- strategy_change_required
- waiting_input
- paused
- failed
```

---

## §25 Workflow Decisions

**`valid`** — Brief 完整、证据有效，可以进入 Xiaohongshu Brief Mapping。

**`valid_with_limitations`** — 允许继续，但必须保留相关限制（Hypothesis-based Angles / 用户证据不足 / 品牌语气未确认 / Objection 缺少充分证据 / 竞品差异证据有限）。

**`strategy_change_required`** — Brief 生成需要改变 Target Segment / Usage Context / Job or Core Need / Value Proposition / Differentiation / Approved Proof Point。此时不得生成新的 Current Truth Brief，应返回 Human Review。

**`waiting_input`** — 用户明确要求但缺少必要输入（指定品牌语气但未提供规范 / 强调某项无来源性能 / 缺少必须明确的 Communication Objective / 缺少行业必要信息）。非关键缺失默认优先生成 `valid_with_limitations`，避免过度暂停。

**`paused`** — Approved Strategy 已失效或撤回 / Proof Point 来源被撤回 / Strategy 与当前 Facts 冲突 / 存在高风险功效或比较声明 / Source Permission 异常。

**`failed`** — 仅用于技术错误（模型无法输出合法 Schema / Validator 内部错误 / 数据持久化失败 / 版本写入失败）。

---

## §26 Editing and Invalidation

用户可以编辑 Marketing Brief。用户编辑必须：

- 创建新的 Marketing Brief Version；
- 保留原模型版本；
- 记录用户修改；
- 重新执行 Validator；
- 更新 Current Truth Pointer。

根据 DEC-009：

```text
Marketing Brief 修改
→ 不使 Facts、Insights、Positioning、Approved Strategy 失效
```

但：

```text
Marketing Brief 修改
→ Xiaohongshu Mapping 失效
```

如果用户编辑实际改变 Strategy（例如替换 Target Segment 或 Value Proposition），则必须返回 `strategy_change_required`。不得通过 Brief 编辑绕过 Human Review。MVP 不增加第二个强制 Human Review Gate。

---

## §27 Deterministic Validator

Marketing Brief 写入 Current Truth 前，至少检查（23 项）：

1. Approved Strategy 当前有效；
2. Approved Strategy 未被撤回；
3. Facts Version 当前有效；
4. Insights Version 当前有效；
5. Audience 与 Approved Strategy 一致；
6. Core Message 未改变 Value Proposition；
7. Differentiation 未被擅自改变；
8. 所有 Proof Point 可回溯到有效 Fact；
9. 不存在新生成的无来源数值；
10. 不存在无依据比较级或最高级；
11. Hypothesis 未被表达为 Fact；
12. Evidence Limitations 完整传播；
13. Prohibited Claims 覆盖关键风险；
14. Objection Response 有事实或证据支持；
15. Content Angles 未创造新的商品能力；
16. 当前商品与竞品资料未混淆；
17. 输出保持平台无关；
18. 未生成最终平台文案；
19. Message Hierarchy 与 Benefit Hierarchy 一致；
20. Mandatory Messages 未丢失；
21. 上游版本未变化；
22. 输出符合 Schema；
23. 写入操作满足幂等要求。

---

## §28 Responsibility Boundary

**LLM** 负责：Message Architecture / 功能到利益转换 / Core Message / Content Angles / Objection 总结 / Tone 建议 / 风险和限制说明。

**Deterministic Logic** 负责：Approved Strategy 有效性 / 上游版本 / Fact 和 Proof Point 引用 / Schema / Prohibited Claims / Hypothesis 状态 / Evidence Limitation 传播 / 幂等 / Stage Status / Current Truth / 下游失效。

**Human** 可以：修改 Brief / 调整 Benefit Priority / 删除 Content Angle / 修改 Tone / 增加 Business Constraints / 要求修改 Strategy。人类修改不能绕过 Strategy Lock 和 Validator。

---

## §29 Evaluation Metrics

**Hard Reliability Metrics**（MVP 目标全部 = 0%）：

```text
Invalid Approved Strategy Reference Rate = 0%
Unsupported Proof Point Rate = 0%
Strategy Drift Rate = 0%
Hypothesis Presented as Fact Rate = 0%
Evidence Limitation Loss Rate = 0%
Platform-specific Leakage Rate = 0%
```

**Brief Quality Metrics**：Core Message Clarity / Benefit Hierarchy Quality / Fact-to-Benefit Alignment / Objection Coverage / Content Angle Distinctiveness / Proof Point Relevance / Tone Consistency / Guardrail Completeness。

**User Value Metrics**：Brief 用户接受率 / 用户修改字段数量 / Content Angle 删除率 / Brief 到 Platform Mapping 时间 / Platform Adapter 对 Brief 的保留率 / 最终内容与 Core Message 的一致性。

---

## §30 Test Scenarios

**1. Valid Approved Strategy** — 预期：生成完整平台无关 Brief；Core Message 与 Strategy 一致；Proof Points 可追溯；Workflow Decision 为 `valid`。

**2. Strategy Contains Hypotheses** — 预期：Hypothesis 作为测试角度；保留 `requires_validation`；不表达为用户共识；Workflow Decision 为 `valid_with_limitations`。

**3. No Brand Tone** — 预期：输出 Suggested Tone；标明未获品牌确认；不强制暂停。

**4. Unsupported「Industry-leading」Request** — 预期：Validator 拒绝；加入 Prohibited Claims；不进入正式 Brief。

**5. Brief Attempts to Change Target Segment** — 预期：返回 `strategy_change_required`；不写入新的 Brief Current Truth；返回 Human Review。

**6. User Edits Brief** — 预期：创建新 Brief Version；上游保持有效；Xiaohongshu Mapping 失效。

---

## §31 Open Questions（记录而非虚构）

- 最终 Marketing Brief 公共 Schema、字段名、类型与逐字段必填表达；
- 数据库表结构；
- Content Angle 分类表（最终枚举）；
- Tone 模板；
- Brand Guidelines 格式与解析；
- 风险词库；
- 具体合规规则；
- Prompt 与模型选择；
- Brief UI；
- CTA 分类（最终枚举）；
- 最终错误代码；
- Proof Point approved_wording 改写校验的精确边界；
- Content Angles 实质差异判定算法；
- Objection 数量与选择规则（1–3 的最终判定）；
- Golden Dataset 最终数据与阈值。

---

## §32 Out-of-Scope（当前不创建）

- 正式 Brief Prompt；
- Skill 代码；
- LangGraph Node；
- Brief UI；
- 数据库表；
- Risk Validator 实现；
- Brand Guideline Parser；
- 平台内容生成器。

当前**不**选择：模型 / Prompt Framework / Tone 模板 / 风险词库 / CTA 分类 / 前端框架 / 数据库。当前**不**创建 RFC。保持 Development Status: **NOT READY**。

在 **Xiaohongshu Brief Mapping Adapter Contract** 确认前，**不**生成正式小红书 Prompt、标题或正文。
