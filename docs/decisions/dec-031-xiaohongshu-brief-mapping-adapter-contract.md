# DEC-031：Xiaohongshu Brief Mapping Adapter 采用 Brief 锁定、版本化平台政策快照、真实体验边界与方向化输出契约

> **Type:** Platform Adapter Contract / Platform Architecture
> **Status:** Accepted — Amended by DEC-046 / DEC-060
> **Date:** 2026-07-29
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)（概念 Platform Adapter Spec，仅概念）
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** [DEC-004](dec-004-platform-neutral-core-xiaohongshu-demo.md) by defining the Xiaohongshu platform mapping layer（在 DEC-004「核心平台中立 + 小红书首个 MVP 演示场景」基础上，正式定义小红书平台映射层的概念层边界与契约，**不推翻** DEC-004 的平台中立核心）与 [DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md) by defining the Xiaohongshu Brief Mapping Adapter contract（在 DEC-020「4 Core Skills + 1 Platform Adapter」结构基础上，正式定义该「+1 Platform Adapter」的概念层执行契约，完成 DEC-020 核心链路，**不推翻** DEC-020 的 Skill 清单与裁剪结论）。
> **Amended By:** [DEC-046](dec-046-review-brief-and-export-product-contract.md)（将既有概念输出收束为六个稳定的产品语义组，并冻结正式 Xiaohongshu Brief 的不可变版本行为；不冻结最终公共 Schema）；[DEC-060](dec-060-evidence-bound-claim-integrity-and-proportional-compliance-boundary.md)（将平台风险限制在已提供或已接受的版本化约束，不授权通用平台合规引擎）

---

## 用户确认

用户对该 Xiaohongshu Brief Mapping Adapter Contract Proposal 明确回复：

> 确认

本决定经 Decision Gate 通过，记录为 Accepted Decision（Type: Platform Adapter Contract / Platform Architecture）。

被接受的核心结论：

- Xiaohongshu Brief Mapping Adapter 是 DEC-020「4 Core Skills + 1 Platform Adapter」中的「+1 Platform Adapter」，位于平台无关 Marketing Brief 与小红书平台执行之间。它负责将平台无关 Brief + 版本化小红书平台政策快照 + 账号与活动上下文映射为小红书 Execution Brief（方向），**不**生成最终可发布小红书文案。
- 边界明确：Business Skill 决定「讲什么」，Platform Adapter 决定「在小红书上如何组织和呈现」。Adapter 必须锁定 Marketing Brief 的 Audience / Core Message / Benefit Hierarchy / Proof Points / Mandatory Messages / Prohibited Claims / Hypotheses / Evidence Limitations，不得重新做战略、不得创建新 Proof Point、不得生成最终标题/正文/Hashtags、不得把 Hypothesis 转为 Fact、不得通过平台表达规避 Prohibited Claims。
- 平台政策是外部、随时间变化的来源。Adapter 必须读取版本化的 Platform Policy Snapshot，**不得**在 Prompt 中硬编码假设长期有效的平台规则；每次执行必须记录所使用的 Snapshot。
- Adapter 可以映射内容格式、内容模式、标题方向、封面方向、叙事结构、内容角度、语气、搜索意图、关键词方向、Hashtag 方向、CTA 方向、平台风险注释，但所有平台化输出均为「方向」而非「最终可发布内容」。最终小红书文案生成是未来独立能力，不在当前 MVP 范围内。

---

## Decision

DEC-020「4 Core Skills + 1 Platform Adapter」中的 Platform Adapter 正式定义为：

```text
Xiaohongshu Brief Mapping Adapter
```

其业务目标是：

将当前唯一有效的平台无关 Marketing Brief Version + 版本化小红书 Platform Policy Snapshot + 账号与活动上下文映射为结构化、可追溯、可校验的小红书 Execution Brief（方向），作为未来最终文案生成的稳定上游输入。

Adapter 是 DEC-020 核心链路的最后一个组件（非 Core Skill）：

```text
Product Intake & Fact Extraction
→ Customer Insight Analysis
→ Product Positioning
→ Human Review Gate
→ Marketing Brief Generation
→ Xiaohongshu Brief Mapping   (本 Adapter)
```

概念流程：

```text
Platform-neutral Marketing Brief
+
Versioned Xiaohongshu Platform Policy Snapshot
+
Account and Campaign Context
↓
Platform Objective Mapping
↓
Content Mode and Note Format Decision
↓
Content Angle Mapping
↓
Title / Cover / Narrative Direction
↓
Search Intent and Keyword Direction
↓
CTA and Interaction Direction
↓
Platform Risk and Review Route Notes
↓
Xiaohongshu Execution Brief (directions)
```

### Adapter and Skill Boundary

**Business Skill 决定讲什么。** Product Intake / Customer Insight / Product Positioning / Human Review / Marketing Brief Generation 负责事实、洞察、定位、审核与平台无关信息架构。

**Platform Adapter 决定在小红书上如何组织和呈现。** Xiaohongshu Brief Mapping Adapter 负责把已锁定的 Brief 映射为小红书平台执行结构，包括格式、模式、标题方向、封面方向、叙事结构、角度映射、语气、搜索与 Hashtag 方向、CTA 方向、平台风险注释。

Adapter **不负责**：

- 重新做战略；
- 修改 Approved Strategy；
- 修改 Marketing Brief；
- 创建新 Proof Point；
- 扩大 Proof Point 含义；
- 生成最终小红书标题、正文、Hashtags、封面文案；
- 生成图片、视觉分镜、Storyboard；
- 自动发布内容；
- 保证小红书审核通过。

---

## Authoritative Input

Xiaohongshu Brief Mapping Adapter 只能读取当前有效：

```text
marketing_brief_version_id
```

并必须能够引用：

```text
approved_strategy_version_id
facts_version_id
platform_policy_snapshot_id
```

不得将以下对象作为正式输入：

- 未审核 Positioning Candidate；
- Strategy Draft；
- Model Recommendation；
- 已撤回或已失效 Approved Strategy；
- 未审核 Marketing Brief 草稿；
- 未审核 Marketing Brief Version；
- 历史旧版本 Marketing Brief。

必须输入：

- 当前 Marketing Brief Version；
- 当前 Approved Strategy Version（引用追溯）；
- 当前有效 Facts Version（引用追溯）；
- 当前有效的版本化 Xiaohongshu Platform Policy Snapshot；
- 账号与活动上下文。

Adapter 不得：

- 读取未审核 Positioning Candidate；
- 读取 Strategy Draft；
- 直接修改 Approved Strategy；
- 创建新 Proof Point；
- 生成最终可发布文案。

---

## Platform Policy Snapshot

平台政策是外部、随时间变化的来源（小红书规则、审核标准、行业适用规则会变化）。Adapter **不得**在 Prompt 中硬编码假设长期有效的平台规则，**必须**读取版本化的 Platform Policy Snapshot，并在每次执行中记录所使用的 Snapshot。

`PlatformPolicySnapshot` 概念字段：

```text
platform
policy_snapshot_id
policy_version
captured_at
applicable_content_type
applicable_industries[]
rule_source_version_ids[]
prohibited_patterns[]
disclosure_requirements[]
qualification_requirements[]
review_route_rules[]
availability_status
```

要求：

- 每次执行必须记录使用的 `policy_snapshot_id` 与 `policy_version`；
- Snapshot 失效或不可用时，Adapter 必须返回 `platform_policy_update_required`，不得静默使用过期规则；
- 公开网页与平台规则为时间敏感来源，页面变化后不得假设旧版本规则仍适用（承接 DEC-025 的时间敏感来源原则）。

以上为概念 Schema，不是最终数据库结构或 Python Model。

---

## Account and Campaign Context

Adapter 需要账号与活动上下文，用于决定呈现方式与风险注释：

```text
account_type
content_relationship
commercial_context
campaign_objective
available_asset_types[]
```

`content_relationship` 概念类型：

```text
brand_owned
creator_collaboration
product_seeding
paid_campaign
organic_exploration
```

Adapter 基于上下文输出：

```text
review_route_notes
required_qualification_notes
commercial_disclosure_notes
```

Adapter **不得**：

- 代替平台判定审核结果；
- 保证审核通过；
- 隐藏商业性质；
- 以「素人」身份掩盖付费或品牌Owned内容。

`account_type`、`content_relationship` 等具体枚举为概念性，最终字段未确认。

---

## Adapter Lock

Adapter 必须将以下 Marketing Brief 字段视为受控输入并锁定（继承与传播）：

```text
audience
core_message
primary_benefit
benefit_hierarchy
proof_points
mandatory_messages
prohibited_claims
hypotheses
evidence_limitations
```

Adapter 可以：

- 调整信息顺序；
- 选择笔记形式与表达方式；
- 映射 Content Angle 到小红书执行方向；
- 调整平台语气；
- 生成标题方向、封面方向；
- 映射搜索意图与 CTA 方向；
- 增加平台风险注释。

Adapter 不得：

- 替换 Audience；
- 改变 Core Message；
- 改变 Benefit Hierarchy；
- 创建新商品能力；
- 创建新 Proof Point；
- 扩大 Proof Point 含义；
- 删除 Evidence Limitation；
- 将 Hypothesis 转为 Fact；
- 重新定义 Approved Strategy；
- 用平台热词覆盖业务事实；
- 通过平台表达规避 Prohibited Claims。

若映射必须改变 Brief，应返回：

```text
brief_change_required
```

并交回上游。不得通过 Adapter 映射或编辑静默修改 Marketing Brief。

---

## MVP Output Boundary

Adapter 的 MVP 输出是**小红书 Execution Brief（方向）**，**不是** Final Xiaohongshu Post。

Execution Brief 可以包括：

- 推荐格式与模式；
- 标题方向；
- 封面信息方向；
- 开头风格方向；
- 笔记结构方向；
- 各段落内容重点；
- Proof Point 放置方向；
- 用户语言使用建议；
- 搜索关键词方向；
- Hashtag 方向；
- CTA 方向；
- 平台风险注释；
- 商业审核路径注释。

Execution Brief **不**包括：

- 最终可发布标题；
- 最终可发布正文；
- 最终 Hashtags 列表；
- 最终封面文字；
- 平台字数终稿；
- 视频分镜终稿。

最终文案生成是未来独立能力，不在当前 MVP 范围内。

---

## Supported Note Formats

MVP 支持的笔记形式：

```text
image_text_note_brief
video_note_brief
```

MVP **不**支持：

- 直播脚本；
- 评论区运营；
- 私信销售；
- 广告创意组合；
- 自动发布；
- 最终视频 Storyboard。

视频的「镜头信息」仅作为执行方向，不是正式 Storyboard。

---

## Platform Objective Mapping

Adapter 将 Brief 的 Communication Objective 映射为小红书平台目标，避免默认一切以「立即购买」为目标：

```text
awareness        → 使用场景 / 品类认知
education        → 说明功能 / 用法 / 选购
consideration    → 回应顾虑 + 证据
trust_building   → 来源 / 细节 / 检测 / 反馈
conversion_support → 帮助判断是否适合
product_launch   → 说明新品解决的问题
```

Adapter 不得把所有目标默认映射为「立即下单」或「促转化」。

---

## Content Modes

每份 Execution Brief 确定一个主要 Content Mode，可附带可选次级 Mode：

```text
experience_sharing
problem_solution
usage_scenario
product_demonstration
selection_guide
knowledge_education
objection_response
comparison_context
new_product_introduction
```

边界规则：

- **Experience Sharing** 仅在有真实素材时使用；不得虚构使用时长、亲测结论、购买故事、朋友推荐或伪造素人身份。
- **Comparison Context** 可说明对比维度，但不得：踩一捧一；无依据贬损竞品；不公平比较；将单个竞品问题放大为全市场问题；输出无依据的优越性。

---

## Title Directions

Adapter 输出标题**方向**（非最终标题）：

```text
3–5 title directions
```

每个 Title Direction 概念上包括：

```text
title_direction
user_question_or_tension
primary_keyword
message_focus
proof_required
risk_notes
```

不得：

- 输出无依据的猎奇标题；
- 输出虚假紧迫感；
- 输出虚构体验标题；
- 输出无依据最高级；
- 标题与正文方向不一致；
- 恶意攻击竞品；
- 把 Hypothesis 表达为事实；
- 通过错字 / 拼音 / 谐音 / 拆字 / 符号规避 Prohibited Claims；
- 以模糊表达规避 Prohibited Claims。

Title Direction 是方向，不是最终可发布标题。

---

## Cover Direction

Adapter 输出封面**方向**（非最终封面文字）：

```text
cover_message_direction
cover_visual_focus
cover_information_priority
cover_risk_notes
```

封面方向应突出**一个主信息**（核心问题 或 核心利益 或 关键演示结果），不得：

- 堆叠全部参数；
- 堆叠全部利益点；
- 堆叠多个 CTA；
- 放无来源数字；
- 放夸张对比；
- 信息与 Core Message 不一致。

封面方向必须与 Core Message 一致。

---

## Narrative Structure

Adapter 采用**模块化**叙事结构，而非单一固定模板：

```text
hook
user_context
user_problem
product_response
proof_or_demonstration
limitations_or_fit_boundary
selection_guidance
interaction_or_CTA
```

- Hook 来源：用户场景 / 具体问题 / 选购困难 / 可验证结果 / 真实用户原声，**不得**来自虚构体验或无依据承诺。
- `limitations_or_fit_boundary` 不得为营销效果被自动删除。

---

## Content Angle Mapping

Adapter 将 Brief 的每个上游 Content Angle 映射为一个或多个小红书执行方向：

```text
source_content_angle_id
xiaohongshu_angle
note_format
content_mode
narrative_structure
proof_points[]
customer_language[]
hypotheses[]
limitations[]
risk_notes[]
```

规则：

- 不得创建与 Brief 无关的新战略角度；
- 可以拆分一个上游角度为多个执行方向，但必须保留与 `source_content_angle_id` 的来源关系。

---

## Customer Language Boundary

真实用户原声必须来自真实 Fragment：

```text
fragment_id
source_scope
quote_type
locator
```

- 当前商品语言 → 用于用户问题 / 场景 / 顾虑 / 购买语言 / 真实体验。
- 竞品语言 → 仅用于品类问题背景 / 选购标准 / Opportunity Context / 市场假设，**不得**展示为当前商品用户评价。

不得 Fabricated Experience：

- 不得「用了一个月真的离不开」；
- 不得「闺蜜推荐后入手」；
- 不得「亲测完全不漏」；
- 不得伪造素人身份。

Adapter 可以输出能力解释 / 演示方向 / 选购建议 / 待验证体验方向，但不得伪装为真实个人体验（承接 DEC-027 的 Customer Language Rules 与 DEC-025 的 Fragment 追溯）。

---

## Experience Boundary

Adapter 不得将任何无真实素材支持的内容表达为真实个人体验。仅当存在真实 Fragment 支持时，方可使用 Experience Sharing Mode 或引用真实体验语言。无真实素材时，相关内容必须降级为待验证方向、演示方向或能力说明，并显式标记。

---

## Tone Mapping

Adapter 将稳定的 Brief Tone 映射为小红书平台执行原则：

```text
具体场景化
优先说明实际使用价值
减少企业式介绍
保留证据和限制
避免空泛形容词
避免夸张表达
```

「小红书风格」**不得**等于：

- Emoji 堆砌；
- 热词堆砌；
- 过度口语化；
- 伪造素人身份；
- 模仿特定创作者；
- 夸张情绪；
- 隐藏商业性质。

---

## CTA Mapping

Adapter 继承 Brief 的 CTA Objective，并映射为小红书 CTA 方向：

```text
invite_discussion
encourage_saving
encourage_comparison
view_product_details
check_specifications
consider_trial
```

不得：

- 输出未确认的折扣；
- 输出虚假紧迫感；
- 强制私信；
- 恶意截流竞品；
- 输出虚假稀缺；
- 输出无依据焦虑。

CTA 方向是方向，不是最终 CTA 文案。

---

## Search and Hashtag Directions

Adapter 输出搜索与 Hashtag **方向**：

```text
primary_search_intent
primary_keywords[]
secondary_keywords[]
topic_directions[]
hashtag_directions[]
```

关键词来源：品类 / 用户问题 / 使用场景 / 真实用户语言 / 有效商品属性。

不得：

- 虚构热搜；
- 无来源声称关键词正在流行；
- 堆砌无关关键词；
- 竞品品牌词截流；
- 输出最终 Hashtags 列表。

MVP 仅输出 Hashtag **方向**，不输出最终 Hashtags。

---

## Prohibited Claims Inheritance

Adapter 必须完整继承 `MarketingBrief.prohibited_claims`，并可增加：

```text
xiaohongshu_specific_risk_notes
```

不得：

- 删除 Prohibited Claims；
- 降低风险等级；
- 通过晦涩表达规避；
- 通过 Emoji / 拼音 / 谐音 / 拆字规避；
- 以伪造素人语气规避；
- 隐藏风险；
- 把无来源内容包装为个人体验。

---

## Xiaohongshu Execution Brief Concept

小红书 Execution Brief 概念上分为六组：

**1. Platform Context**

```text
platform
platform_policy_snapshot_id
account_type
commercial_context
campaign_objective
available_asset_types[]
```

**2. Note Strategy**

```text
recommended_note_format
primary_content_mode
secondary_content_mode
platform_objective
source_content_angle_ids[]
```

**3. Content Architecture**

```text
title_directions[]
cover_direction
narrative_structure[]
message_priority
proof_placement[]
fit_boundary
```

**4. Discovery and Interaction**

```text
search_intent
keyword_directions[]
hashtag_directions[]
CTA_mapping
interaction_prompt_direction
```

**5. Evidence and Guardrails**

```text
proof_points[]
customer_language[]
mandatory_messages[]
prohibited_claims[]
hypotheses[]
evidence_limitations[]
platform_risk_notes[]
review_route_notes[]
```

**6. Workflow Decision**

```text
stage_decision:
- valid
- valid_with_limitations
- brief_change_required
- platform_policy_update_required
- waiting_input
- paused
- failed
```

以上为概念 Schema，不是最终数据库结构或 Python Model。Xiaohongshu Execution Brief 为版本化 Domain Object（承接 DEC-024）。

---

## Workflow Decisions

**`valid`** — 映射完整、Brief 锁定、平台政策快照有效，可以输出 Execution Brief。

**`valid_with_limitations`** — 允许继续，但必须保留相关限制（Hypothesis-based 方向 / 用户证据不足 / 品牌语气未确认 / 平台政策快照部分覆盖 / 竞品证据有限）。非关键缺失默认优先生成 `valid_with_limitations`，避免过度暂停。

**`brief_change_required`** — 映射需要改变 Audience / Core Message / Benefit Hierarchy / Proof Point / Approved Strategy。此时不得生成新的 Execution Brief Current Truth，应返回上游 Marketing Brief。

**`platform_policy_update_required`** — Platform Policy Snapshot 失效、不可用或与当前内容类型 / 行业不匹配。此时不得使用过期规则继续，应要求刷新 Snapshot。

**`waiting_input`** — 用户明确要求但缺少必要输入（账号类型 / 合作关系 / 活动目标 / 可用素材类型 / 行业必要信息）。非关键缺失默认优先生成 `valid_with_limitations`。

**`paused`** — Marketing Brief 已失效 / Approved Strategy 已撤回 / Platform Policy Snapshot 撤回 / Strategy 与当前 Facts 冲突 / 存在高风险平台违规可能 / Source Permission 异常。

**`failed`** — 仅用于技术错误（模型无法输出合法 Schema / Validator 内部错误 / 数据持久化失败 / 版本写入失败）。

---

## Editing and Invalidation

用户可以编辑 Xiaohongshu Execution Brief。用户编辑必须：

- 创建新的 Execution Brief Version；
- 保留原模型版本；
- 记录用户修改；
- 重新执行 Validator；
- 更新 Current Truth Pointer。

根据 DEC-009：

```text
Xiaohongshu Execution Brief 修改
→ 不使 Marketing Brief 失效
→ 不使上游失效
```

由于 Xiaohongshu Execution Brief 是当前 MVP 的最终输出，普通编辑**不**触发下游失效（当前 MVP 无下游）。

如果用户编辑实际改变 Audience / Core Message / Benefit Hierarchy / Proof Point / Approved Strategy，则必须返回：

```text
brief_change_required
```

不得通过 Execution Brief 编辑绕过 Marketing Brief 与 Approved Strategy。MVP **不**增加额外强制 Human Review Gate（承接 DEC-007 单一审核节点）。

---

## Deterministic Validator

Xiaohongshu Execution Brief 写入 Current Truth 前，至少检查（28 项）：

1. Marketing Brief 当前有效；
2. Approved Strategy 当前有效；
3. Platform Policy Snapshot 存在且可用；
4. Audience 与 Marketing Brief 一致；
5. Core Message 未改变；
6. Benefit Hierarchy 未改变；
7. 所有 Proof Point 来自 Marketing Brief；
8. 不存在新无来源能力；
9. Hypothesis 未被转为 Fact；
10. Evidence Limitations 完整传播；
11. Prohibited Claims 完整继承；
12. 当前商品与竞品资料未混淆；
13. 用户原声拥有真实 Fragment；
14. 不存在虚构体验；
15. 不存在无依据比较级或最高级；
16. 不存在恶意攻击竞品；
17. 不存在通过变体字规避 Prohibited Claims；
18. Title Direction 与 Narrative Structure 一致；
19. Cover Direction 与 Core Message 一致；
20. Keyword Direction 与内容相关；
21. Hashtag 仅为方向（非最终列表）；
22. CTA 不含未确认折扣；
23. CTA 不含虚假紧迫感；
24. 输出非最终平台文案；
25. 上游版本未变化；
26. 输出符合 Schema；
27. 写入操作满足幂等要求；
28. Platform Policy Snapshot 版本已记录。

---

## Responsibility Boundary

**Deterministic Logic** 负责：

- 上游版本有效性；
- Platform Policy Snapshot 版本与可用性；
- Proof Point 引用；
- Mandatory Messages；
- Prohibited Claims；
- Source Scope；
- Schema；
- 幂等；
- Stage Status；
- Current Truth；
- Risk Flags。

**LLM** 负责：

- 推荐格式；
- 映射 Content Mode；
- Title Directions；
- Cover Direction；
- Narrative Structure；
- 映射 Content Angles；
- Tone；
- CTA；
- Search Intent；
- Keyword Directions；
- 平台风险注释。

**Human** 可以：

- 选择图文或视频；
- 调整标题方向；
- 调整结构；
- 删除不适合的 Angle；
- 选择 CTA；
- 提供账号与合作信息；
- 请求修改 Marketing Brief；
- 编辑 Execution Brief。

人类修改不能绕过 Adapter Lock 和 Validator。

---

## Evaluation Metrics

**Hard Reliability Metrics**（MVP 目标全部 = 0%）：

```text
Strategy Drift Rate = 0%
Marketing Brief Drift Rate = 0%
Unsupported Proof Point Rate = 0%
Prohibited Claim Loss Rate = 0%
Fabricated Experience Rate = 0%
Competitor Misattribution Rate = 0%
```

**Platform Mapping Quality Metrics**：Platform Objective Mapping Correctness / Content Mode Appropriateness / Title Direction Quality / Cover Direction Consistency / Narrative Structure Coverage / Content Angle Fidelity / Tone Mapping Appropriateness / Keyword Direction Relevance / CTA Mapping Consistency / Platform Risk Note Coverage。

**User Value Metrics**：Execution Brief 用户接受率 / 用户修改字段数量 / Title Direction 删除率 / Marketing Brief 到 Execution Brief 映射时间 / Execution Brief 对 Brief 的保留率 / 最终内容方向与 Core Message 的一致性。

模型自报 Confidence 不作核心指标。

---

## Required Test Scenarios

**1. Valid Platform Mapping** — 预期：生成完整 Execution Brief；Audience / Core Message / Proof Points 与 Brief 一致；输出为方向非最终文案；Workflow Decision 为 `valid`。

**2. No Real Experience Material** — 预期：不得使用 Experience Sharing；不得虚构亲测语言；相关内容降级为待验证方向；Workflow Decision 为 `valid_with_limitations`。

**3. Competitor Reviews Only** — 预期：竞品语言仅用于品类背景 / 选购标准 / Opportunity Context；不得展示为当前商品用户评价；不输出无依据竞品优越性。

**4. Unsupported Industry-leading Request** — 预期：Validator 拒绝；加入 Prohibited Claims；不进入 Execution Brief。

**5. Expired Platform Policy Snapshot** — 预期：返回 `platform_policy_update_required`；不得使用过期规则继续。

**6. Adapter Attempts to Change Core Message** — 预期：返回 `brief_change_required`；不写入新的 Execution Brief Current Truth；返回上游 Marketing Brief。

**7. User Edits Execution Brief** — 预期：创建新 Execution Brief Version；上游保持有效；不触发下游失效（当前 MVP 无下游）。

以上为概念测试场景，非最终 Golden Dataset。

---

## Contract Summary

```text
Platform Adapter:
Xiaohongshu Brief Mapping

Input:
- Current Marketing Brief Version
- Versioned Xiaohongshu Platform Policy Snapshot
- Account and Campaign Context

Output:
- Xiaohongshu Execution Brief (directions)

Hard Rules:
- No Strategy Drift
- No Marketing Brief Drift
- No Fabricated Experience
- No unsupported Proof Point
- No removal or evasion of Prohibited Claims
- No Final Xiaohongshu Copy in MVP
```

---

## Reason

Xiaohongshu Brief Mapping Adapter 是平台无关 Brief 与小红书平台执行之间的映射层。如果该层能够擅自修改 Brief 或直接生成最终平台文案，将导致：

- Marketing Brief 被绕过；
- 平台 Adapter 重新做战略；
- Proof Point 失去来源；
- Hypothesis 变成事实；
- Evidence Limitations 丢失；
- 平台政策被硬编码而随时间失效；
- 虚构体验与无依据声明进入平台内容；
- Prohibited Claims 被通过平台表达规避。

因此 Xiaohongshu Brief Mapping Adapter 必须：锁定平台无关 Marketing Brief，以版本化平台政策快照与账号上下文为约束，把 Brief 映射为小红书方向化执行结构，同时完整保留所有假设、证据限制与风险边界，且不生成最终可发布文案。

---

## Impact

该决定将影响：

- Xiaohongshu Execution Brief Domain Model；
- Execution Brief Version；
- Platform Adapter Input / Output；
- Marketing Brief Integration；
- Platform Policy Snapshot Repository；
- Account and Campaign Context；
- Evidence Validator；
- Risk Validator；
- Execution Brief Editing；
- Invalidation；
- Frontend Execution Brief Page；
- Evaluation Dataset；
- 后续最终文案生成能力与多平台扩展。

---

## Decision Boundary

本决定已经确认：

- Xiaohongshu Brief Mapping Adapter 的业务边界；
- Adapter 与 Skill 的边界；
- 只能读取当前 Marketing Brief；
- Authoritative Input；
- 版本化 Platform Policy Snapshot；
- Account and Campaign Context；
- Adapter Lock；
- MVP 输出为 Execution Brief（方向）；
- 支持的笔记形式（图文 / 视频）；
- Platform Objective Mapping；
- Content Modes；
- Title Directions；
- Cover Direction；
- Narrative Structure；
- Content Angle Mapping；
- Customer Language 边界；
- Experience 边界；
- Tone Mapping；
- CTA Mapping；
- Search and Hashtag Directions；
- Prohibited Claims 继承；
- 六组 Execution Brief 输出；
- Workflow Decision；
- 不生成最终平台文案；
- 不设置额外强制 Review Gate；
- 用户可以编辑 Execution Brief；
- Execution Brief 普通编辑不触发下游失效；
- Execution Brief 编辑不能绕过 Brief 与 Strategy；
- Validator 28 项规则；
- 硬性可靠性指标。

本决定原本尚未确认、现由 DEC-046 部分闭合：

- Xiaohongshu Brief 的六个产品语义组和不可变版本行为已冻结；

仍未确认：

- 最终 Xiaohongshu Brief 公共 Schema、字段名、类型与逐字段必填表达；
- Platform Policy Snapshot 的采集与同步机制；
- Account and Campaign Context 最终结构；
- 数据库表；
- Content Mode 分类表；
- Title / Cover 模板；
- 风险词库；
- 具体平台合规规则；
- Prompt；
- 模型；
- Execution Brief UI；
- CTA 分类；
- 最终错误代码。

---

## Related Decisions

- [DEC-004 — 产品核心保持平台中立，小红书种草作为首个 MVP 演示场景](dec-004-platform-neutral-core-xiaohongshu-demo.md)（Platform-neutral Core + Xiaohongshu Demo；**本决定 Amends DEC-004**）
- [DEC-006 — MVP 输出采用四层结构化营销 Brief](dec-006-four-layer-structured-marketing-brief.md)（Four-layer Output）
- [DEC-014 — MVP 采用按需、混合式 RAG 与分层数据访问策略](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（Hybrid Retrieval；Platform Policy Snapshot 检索与时间敏感来源）
- [DEC-019 — Ecommerce Visual Copywriting Skill 作为执行层 Brief 能力的改造供体](dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)（Xiaohongshu Brief Mapping 候选 Reference+部分改造供体）
- [DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（4 Core Skills + 1 Platform Adapter；**本决定 Amends DEC-020**）
- [DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](dec-025-versioned-sources-fragments-and-evidence-links.md)（Source and Evidence Architecture；用户原声 Fragment 追溯与时间敏感来源）
- [DEC-029 — Human Review 采用版本化审核包、结构化用户决策与事务化 Approved Strategy 契约](dec-029-human-review-and-approved-strategy-contract.md)（Approved Strategy Contract；上游 Authoritative Input 来源）
- [DEC-030 — Marketing Brief Generation 采用 Approved Strategy 锁定、平台无关信息架构与证据限制传播契约](dec-030-marketing-brief-generation-skill-contract.md)（Marketing Brief Generation Contract；本 Adapter 的直接 Authoritative Input 来源）

---

## Related RFC

None

---

## Supersedes

None

---

## Amends

**Amends [DEC-004](dec-004-platform-neutral-core-xiaohongshu-demo.md)** by defining the Xiaohongshu platform mapping layer.

- DEC-004 确认产品核心保持平台中立，小红书种草作为首个 MVP 演示场景，但模板字段 / API / 抓取 / 其他平台 / 适配层技术均未确认。
- DEC-031 在此基础上正式定义小红书平台映射层的**概念层边界与执行契约**（Adapter 与 Skill 边界 / Authoritative Input / 版本化 Platform Policy Snapshot / Account and Campaign Context / Adapter Lock / MVP 输出为方向化 Execution Brief / 笔记形式 / Platform Objective Mapping / Content Modes / Title Directions / Cover Direction / Narrative Structure / Content Angle Mapping / Customer Language 与 Experience 边界 / Tone Mapping / CTA Mapping / Search and Hashtag Directions / Prohibited Claims 继承 / 六组输出 / Workflow Decision / Validator 28 项 / 不生成最终平台文案）。
- **不推翻** DEC-004 的平台中立核心；DEC-004 行作为历史记录不修改，本 Amends 关系仅在此处记录。

**Amends [DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)** by defining the Xiaohongshu Brief Mapping Adapter contract.

- DEC-020 确认 MVP 采用 4 Core Skills + 1 Platform Adapter（Xiaohongshu Brief Mapping），但 Xiaohongshu Adapter 最终输出 / 是否生成完整笔记 / 规则接口均未确认。
- DEC-031 在此基础上正式定义该「+1 Platform Adapter」的**概念层执行契约**（业务目标 / 职责 / 非职责 / Authoritative Input / Platform Policy Snapshot / Account and Campaign Context / Adapter Lock / MVP 输出边界 / 笔记形式 / Platform Objective Mapping / Content Modes / Title Directions / Cover Direction / Narrative Structure / Content Angle Mapping / Customer Language / Experience 边界 / Tone Mapping / CTA Mapping / Search and Hashtag Directions / Prohibited Claims 继承 / 六组 Execution Brief 输出 / Workflow Decision / Editing 与 Invalidation / Validator 28 项 / 职责边界 / 评价指标 / 测试场景），完成 DEC-020 核心链路。
- **不推翻** DEC-020 的 Skill 清单与裁剪结论；DEC-020 行作为历史记录不修改，本 Amends 关系仅在此处记录。

---

## Notes

- 本决定保持 **Development Status: NOT READY**。
- 当前**不**创建正式小红书 Prompt / 最终标题 / 最终正文 / 最终 Hashtags / Final Copy Generator / 发布代码 / Platform Policy Sync 代码 / 数据库表 / 风险词库 / 自动审核实现 / 图文或视频生成代码。
- 当前**不**选择平台数据供应商 / 热点接口 / 搜索关键词工具 / 风险审核供应商 / 视频时长 / 图文页数 / Hashtag 数量 / 发布 API / 最终 LLM。
- 当前**不**创建 RFC。
- 该 Adapter 是 DEC-020「4 Core Skills + 1 Platform Adapter」中的「+1 Platform Adapter」，是核心链路的最后一个组件（`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation → Xiaohongshu Brief Mapping`）；其 Authoritative Input 为 DEC-030 形成的平台无关 Marketing Brief Version；其输出的 Execution Brief 是当前 MVP 的最终方向化输出。Adapter 若能擅自修改 Brief 或直接生成最终平台文案，将导致 Marketing Brief 被绕过、平台 Adapter 重新做战略、Proof Point 失去来源、Hypothesis 变成事实、Evidence Limitations 丢失、平台政策随时间失效、虚构体验进入平台内容，以及 Prohibited Claims 被规避。
- 概念 Platform Adapter Spec 见 [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)（仅概念，非最终实现）。
- 在 **Hybrid Retrieval and Evidence Runtime Architecture** 议题确认前，**不**选择 Embedding 模型、向量数据库、Chunk Size、Top-K 或 Reranker。
