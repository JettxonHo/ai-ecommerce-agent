# Xiaohongshu Brief Mapping Adapter — 概念 Specification

> **Status: PRODUCT SEMANTICS ACCEPTED / IMPLEMENTATION CONTRACT CONCEPTUAL**
> 来源决定：[DEC-031 — Xiaohongshu Brief Mapping Adapter 采用 Brief 锁定、版本化平台政策快照、真实体验边界与方向化输出契约](../../decisions/dec-031-xiaohongshu-brief-mapping-adapter-contract.md)、[DEC-046 — 冻结审核、Brief 与导出的产品语义和版本行为](../../decisions/dec-046-review-brief-and-export-product-contract.md)、[DEC-047 — 渐进式证据、编辑意图与行动导向恢复交互](../../decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)与 [DEC-056 — 深 TaskWorkbench、revision-safe 交互与适度 Web 质量边界](../../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md)（均 Accepted）。
> 本文件的六个产品语义组、不可变正式版本、语义组差异和“Xiaohongshu Brief 自身编辑不反向失效上游”行为已确认；DEC-056 已冻结前端语义组级 Diff，公共 Change Set、字段名、类型、枚举、Schema、阈值、Prompt 与模型仍是概念，不是最终实现契约。
> Development Status: **NOT READY**。

---

## §0 来源与范围

本 Specification 把 DEC-031 已确认的 Platform Adapter Contract 整理为结构化概念规格。本 Adapter 是 DEC-020「4 Core Skills + 1 Platform Adapter」中的「+1 Platform Adapter」，是核心链路的最后一个组件：

```text
Product Intake & Fact Extraction
→ Customer Insight Analysis
→ Product Positioning
→ Human Review Gate
→ Marketing Brief Generation
→ Xiaohongshu Brief Mapping   (本文件)
```

承接 DEC-004（平台中立核心 + 小红书首个演示，Amended by DEC-031）、DEC-009（阶段级失效：Execution Brief 普通编辑不触发下游失效）、DEC-014（Hybrid Retrieval 与时间敏感来源）、DEC-019（Xiaohongshu Brief Mapping 候选 Reference+部分改造供体）、DEC-020（4 Core Skills + 1 Platform Adapter，Amended by DEC-031）、DEC-024（版本化 Domain Objects + Current Truth Pointers）、DEC-025（Source / Source Version / Fragment / Evidence Link + 用户原声 Fragment 追溯）、DEC-029（Approved Strategy Contract）、DEC-030（Authoritative Input = 平台无关 Marketing Brief Version 契约）。

本 Adapter 输出**小红书 Execution Brief（方向）**，是未来最终文案生成的稳定上游输入，**不**生成最终可发布小红书文案。

---

## §1 Business Goal

将当前唯一有效的平台无关 Marketing Brief Version + 版本化小红书 Platform Policy Snapshot + 账号与活动上下文映射为结构化、可追溯、可校验的小红书 Execution Brief（方向），作为未来最终文案生成的稳定上游输入。

该 Adapter **不**追求「直接生成最终平台文案」，而是：锁定平台无关 Marketing Brief，以版本化平台政策快照与账号上下文为约束，把 Brief 映射为小红书方向化执行结构，同时完整保留所有假设、证据限制与风险边界。

---

## §2 Adapter and Skill Boundary

**Business Skill 决定讲什么。** Product Intake / Customer Insight / Product Positioning / Human Review / Marketing Brief Generation 负责事实、洞察、定位、审核与平台无关信息架构。

**Platform Adapter 决定在小红书上如何组织和呈现。** Xiaohongshu Brief Mapping Adapter 负责把已锁定的 Brief 映射为小红书平台执行结构。

---

## §3 Responsibilities

- 推荐笔记格式与内容模式；
- 映射 Communication Objective 到平台目标；
- 映射 Content Angles 到小红书执行方向；
- 生成标题方向、封面方向；
- 组织叙事结构方向；
- 映射语气到平台执行原则；
- 输出搜索意图、关键词方向、Hashtag 方向；
- 映射 CTA 方向；
- 增加平台风险注释与审核路径注释；
- 完整继承 Proof Points / Mandatory Messages / Prohibited Claims / Hypotheses / Evidence Limitations；
- 生成版本化、方向化的小红书 Execution Brief。

---

## §4 Non-responsibilities

该 Adapter **不**负责：

- 修改 Approved Strategy；
- 修改 Marketing Brief；
- 创建新商品能力或新 Proof Point；
- 扩大 Proof Point 含义；
- 删除 Evidence Limitation；
- 将 Hypothesis 转为 Fact；
- 生成最终小红书标题、正文、Hashtags、封面文案；
- 生成图片、视觉分镜、Storyboard；
- 自动发布内容；
- 保证小红书审核通过。

---

## §5 Authoritative Input

Adapter 只能读取当前有效：

```text
marketing_brief_version_id
```

并必须能够引用：

```text
approved_strategy_version_id
facts_version_id
platform_policy_snapshot_id
```

**不得**作为正式输入：

- 未审核 Positioning Candidate；
- Strategy Draft；
- Model Recommendation；
- 已撤回或已失效 Approved Strategy；
- 未审核 Marketing Brief 草稿；
- 未审核 Marketing Brief Version；
- 历史旧版本 Marketing Brief。

**必须**输入：

- 当前 Marketing Brief Version；
- 当前 Approved Strategy Version（引用追溯）；
- 当前有效 Facts Version（引用追溯）；
- 当前有效的版本化 Xiaohongshu Platform Policy Snapshot；
- 账号与活动上下文。

Adapter 不得读取未审核 Positioning Candidate / Strategy Draft，不得直接修改 Approved Strategy，不得创建新 Proof Point，不得生成最终可发布文案。

---

## §6 Platform Policy Snapshot

平台政策是外部、随时间变化的来源。Adapter **不得**在 Prompt 中硬编码假设长期有效的平台规则，**必须**读取版本化的 Platform Policy Snapshot。

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
- Snapshot 失效或不可用时，返回 `platform_policy_update_required`，不得静默使用过期规则；
- 公开网页与平台规则为时间敏感来源，页面变化后不得假设旧版本规则仍适用（承接 DEC-025）。

以上为概念 Schema，不是最终数据库结构或 Python Model。

---

## §7 Account and Campaign Context

Adapter 需要账号与活动上下文：

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

Adapter 不得代替平台判定审核结果、不得保证审核通过、不得隐藏商业性质、不得以素人身份掩盖付费或品牌 Owned 内容。具体枚举为概念性，最终字段未确认。

---

## §8 Adapter Lock

Adapter 必须将以下 Marketing Brief 字段视为受控输入并锁定：

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

**Adapter 可以：**

- 调整信息顺序；
- 选择笔记形式与表达方式；
- 映射 Content Angle 到小红书执行方向；
- 调整平台语气；
- 生成标题方向、封面方向；
- 映射搜索意图与 CTA 方向；
- 增加平台风险注释。

**Adapter 不得：**

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

若映射必须改变 Brief，应返回 `brief_change_required` 并交回上游。不得通过 Adapter 映射或编辑静默修改 Marketing Brief。

---

## §9 MVP Output Boundary

Adapter 的 MVP 输出是**小红书 Execution Brief（方向）**，**不是** Final Xiaohongshu Post。

Execution Brief 可以包括：推荐格式与模式 / 标题方向 / 封面信息方向 / 开头风格方向 / 笔记结构方向 / 各段落内容重点 / Proof Point 放置方向 / 用户语言使用建议 / 搜索关键词方向 / Hashtag 方向 / CTA 方向 / 平台风险注释 / 商业审核路径注释。

Execution Brief **不**包括：最终可发布标题 / 最终可发布正文 / 最终 Hashtags 列表 / 最终封面文字 / 平台字数终稿 / 视频分镜终稿。

最终文案生成是未来独立能力，不在当前 MVP 范围内。

---

## §10 Supported Note Formats

MVP 支持的笔记形式：

```text
image_text_note_brief
video_note_brief
```

MVP **不**支持：直播脚本 / 评论区运营 / 私信销售 / 广告创意组合 / 自动发布 / 最终视频 Storyboard。视频的「镜头信息」仅作为执行方向，不是正式 Storyboard。

---

## §11 Platform Objective Mapping

Adapter 将 Brief 的 Communication Objective 映射为小红书平台目标：

```text
awareness          → 使用场景 / 品类认知
education          → 说明功能 / 用法 / 选购
consideration      → 回应顾虑 + 证据
trust_building     → 来源 / 细节 / 检测 / 反馈
conversion_support → 帮助判断是否适合
product_launch     → 说明新品解决的问题
```

Adapter 不得把所有目标默认映射为「立即下单」或「促转化」。

---

## §12 Content Modes

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

**Experience Sharing** 仅在有真实素材时使用；不得虚构使用时长、亲测结论、购买故事、朋友推荐或伪造素人身份。

**Comparison Context** 可说明对比维度，但不得：踩一捧一；无依据贬损竞品；不公平比较；将单个竞品问题放大为全市场问题；输出无依据的优越性。

---

## §13 Title Directions

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

不得：输出无依据的猎奇标题 / 虚假紧迫感 / 虚构体验标题 / 无依据最高级 / 标题与正文方向不一致 / 恶意攻击竞品 / 把 Hypothesis 表达为事实 / 通过错字、拼音、谐音、拆字、符号规避 Prohibited Claims / 以模糊表达规避 Prohibited Claims。Title Direction 是方向，不是最终可发布标题。

---

## §14 Cover Direction

Adapter 输出封面**方向**（非最终封面文字）：

```text
cover_message_direction
cover_visual_focus
cover_information_priority
cover_risk_notes
```

封面方向应突出**一个主信息**（核心问题 或 核心利益 或 关键演示结果），不得：堆叠全部参数 / 堆叠全部利益点 / 堆叠多个 CTA / 放无来源数字 / 放夸张对比 / 信息与 Core Message 不一致。封面方向必须与 Core Message 一致。

---

## §15 Narrative Structure

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

Hook 来源：用户场景 / 具体问题 / 选购困难 / 可验证结果 / 真实用户原声，**不得**来自虚构体验或无依据承诺。`limitations_or_fit_boundary` 不得为营销效果被自动删除。

---

## §16 Content Angle Mapping

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

不得创建与 Brief 无关的新战略角度；可以拆分一个上游角度为多个执行方向，但必须保留与 `source_content_angle_id` 的来源关系。

---

## §17 Customer Language

真实用户原声必须来自真实 Fragment：

```text
fragment_id
source_scope
quote_type
locator
```

- 当前商品语言 → 用于用户问题 / 场景 / 顾虑 / 购买语言 / 真实体验。
- 竞品语言 → 仅用于品类问题背景 / 选购标准 / Opportunity Context / 市场假设，**不得**展示为当前商品用户评价。

Adapter 可以输出能力解释 / 演示方向 / 选购建议 / 待验证体验方向，但不得伪装为真实个人体验（承接 DEC-027 / DEC-025）。

---

## §18 Experience Boundary

Adapter 不得将任何无真实素材支持的内容表达为真实个人体验。不得：「用了一个月真的离不开」；「闺蜜推荐后入手」；「亲测完全不漏」；伪造素人身份。仅当存在真实 Fragment 支持时，方可使用 Experience Sharing Mode 或引用真实体验语言。无真实素材时，相关内容必须降级为待验证方向、演示方向或能力说明，并显式标记。

---

## §19 Tone Mapping

Adapter 将稳定的 Brief Tone 映射为小红书平台执行原则：

```text
具体场景化
优先说明实际使用价值
减少企业式介绍
保留证据和限制
避免空泛形容词
避免夸张表达
```

「小红书风格」**不得**等于：Emoji 堆砌 / 热词堆砌 / 过度口语化 / 伪造素人身份 / 模仿特定创作者 / 夸张情绪 / 隐藏商业性质。

---

## §20 CTA Mapping

Adapter 继承 Brief 的 CTA Objective，并映射为小红书 CTA 方向：

```text
invite_discussion
encourage_saving
encourage_comparison
view_product_details
check_specifications
consider_trial
```

不得：输出未确认的折扣 / 虚假紧迫感 / 强制私信 / 恶意截流竞品 / 虚假稀缺 / 无依据焦虑。CTA 方向是方向，不是最终 CTA 文案。

---

## §21 Search and Hashtag Directions

Adapter 输出搜索与 Hashtag **方向**：

```text
primary_search_intent
primary_keywords[]
secondary_keywords[]
topic_directions[]
hashtag_directions[]
```

关键词来源：品类 / 用户问题 / 使用场景 / 真实用户语言 / 有效商品属性。不得：虚构热搜 / 无来源声称关键词正在流行 / 堆砌无关关键词 / 竞品品牌词截流 / 输出最终 Hashtags 列表。MVP 仅输出 Hashtag **方向**，不输出最终 Hashtags。

---

## §22 Prohibited Claims Inheritance

Adapter 必须完整继承 `MarketingBrief.prohibited_claims`，并可增加：

```text
xiaohongshu_specific_risk_notes
```

不得：删除 Prohibited Claims / 降低风险等级 / 通过晦涩表达规避 / 通过 Emoji、拼音、谐音、拆字规避 / 以伪造素人语气规避 / 隐藏风险 / 把无来源内容包装为个人体验。

---

## §23 Commercial Context

Adapter 基于账号与活动上下文输出商业性注释：

```text
review_route_notes
required_qualification_notes
commercial_disclosure_notes
```

这些注释用于提示审核路径、所需资质与商业披露要求。Adapter 不得代替平台判定审核结果，不得保证审核通过，不得隐藏商业性质（承接 DEC-030 的 Mandatory Messages / Prohibited Claims 传播）。

---

## §24 Xiaohongshu Execution Brief Concept

Xiaohongshu Brief 固定为六个产品语义组。下列字段仅为概念展开，不是最终公共 Schema；Adapter 不得为满足结构而重新制定战略或制造证据。

**1. Platform and Campaign Context**

```text
platform
account_type
commercial_context
campaign_objective
available_asset_types[]
```

**2. Note Format and Content Mode**

```text
recommended_note_format
primary_content_mode
secondary_content_mode
platform_objective
source_content_angle_ids[]
```

**3. Creative Structure Directions**

```text
title_directions[]
cover_direction
narrative_structure[]
message_priority
proof_placement[]
fit_boundary
```

**4. Discovery and Action Directions**

```text
search_intent
keyword_directions[]
hashtag_directions[]
CTA_mapping
interaction_prompt_direction
```

**5. Evidence and Platform Constraints**

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

**6. Workflow and Version Context**

```text
xiaohongshu_brief_version_id
marketing_brief_version_id
approved_strategy_version_id
platform_policy_snapshot_id
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

## §25 Workflow Decisions

**`valid`** — 映射完整、Brief 锁定、平台政策快照有效，可以输出 Execution Brief。

**`valid_with_limitations`** — 允许继续，但必须保留相关限制（Hypothesis-based 方向 / 用户证据不足 / 品牌语气未确认 / 平台政策快照部分覆盖 / 竞品证据有限）。非关键缺失默认优先生成 `valid_with_limitations`，避免过度暂停。

**`brief_change_required`** — 映射需要改变 Audience / Core Message / Benefit Hierarchy / Proof Point / Approved Strategy。此时不得生成新的 Execution Brief Current Truth，应返回上游 Marketing Brief。

**`platform_policy_update_required`** — Platform Policy Snapshot 失效、不可用或与当前内容类型 / 行业不匹配。此时不得使用过期规则继续，应要求刷新 Snapshot。

**`waiting_input`** — 用户明确要求但缺少必要输入（账号类型 / 合作关系 / 活动目标 / 可用素材类型 / 行业必要信息）。非关键缺失默认优先生成 `valid_with_limitations`。

**`paused`** — Marketing Brief 已失效 / Approved Strategy 已撤回 / Platform Policy Snapshot 撤回 / Strategy 与当前 Facts 冲突 / 存在高风险平台违规可能 / Source Permission 异常。

**`failed`** — 仅用于技术错误（模型无法输出合法 Schema / Validator 内部错误 / 数据持久化失败 / 版本写入失败）。

---

## §26 Editing and Invalidation

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

如果用户编辑实际改变 Audience / Core Message / Benefit Hierarchy / Proof Point / Approved Strategy，则必须返回 `brief_change_required`。不得通过 Execution Brief 编辑绕过 Marketing Brief 与 Approved Strategy。MVP **不**增加额外强制 Human Review Gate（承接 DEC-007）。

---

## §27 Deterministic Validator

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

## §28 Responsibility Boundary

**Deterministic Logic** 负责：上游版本有效性 / Platform Policy Snapshot 版本与可用性 / Proof Point 引用 / Mandatory Messages / Prohibited Claims / Source Scope / Schema / 幂等 / Stage Status / Current Truth / Risk Flags。

**LLM** 负责：推荐格式 / 映射 Content Mode / Title Directions / Cover Direction / Narrative Structure / 映射 Content Angles / Tone / CTA / Search Intent / Keyword Directions / 平台风险注释。

**Human** 可以：选择图文或视频 / 调整标题方向 / 调整结构 / 删除不适合的 Angle / 选择 CTA / 提供账号与合作信息 / 请求修改 Marketing Brief / 编辑 Execution Brief。人类修改不能绕过 Adapter Lock 和 Validator。

---

## §29 Evaluation Metrics

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

## §30 Test Scenarios

**1. Valid Platform Mapping** — 预期：生成完整 Execution Brief；Audience / Core Message / Proof Points 与 Brief 一致；输出为方向非最终文案；Workflow Decision 为 `valid`。

**2. No Real Experience Material** — 预期：不得使用 Experience Sharing；不得虚构亲测语言；相关内容降级为待验证方向；Workflow Decision 为 `valid_with_limitations`。

**3. Competitor Reviews Only** — 预期：竞品语言仅用于品类背景 / 选购标准 / Opportunity Context；不得展示为当前商品用户评价；不输出无依据竞品优越性。

**4. Unsupported Industry-leading Request** — 预期：Validator 拒绝；加入 Prohibited Claims；不进入 Execution Brief。

**5. Expired Platform Policy Snapshot** — 预期：返回 `platform_policy_update_required`；不得使用过期规则继续。

**6. Adapter Attempts to Change Core Message** — 预期：返回 `brief_change_required`；不写入新的 Execution Brief Current Truth；返回上游 Marketing Brief。

**7. User Edits Execution Brief** — 预期：创建新 Execution Brief Version；上游保持有效；不触发下游失效（当前 MVP 无下游）。

以上为概念测试场景，非最终 Golden Dataset。

---

## §31 Open Questions（记录而非虚构）

- 最终 Xiaohongshu Brief 公共 Schema、字段名、类型与逐字段必填表达；
- Platform Policy Snapshot 的采集、版本管理与同步机制；
- Platform Policy Snapshot 的存储与可用性判断；
- Account and Campaign Context 最终结构与字段；
- 数据库表结构；
- Content Mode 分类表（最终枚举）；
- Title / Cover 方向模板；
- Narrative Structure 模块组合规则；
- 风险词库；
- 具体平台合规规则；
- Prompt 与模型选择；
- Execution Brief UI；
- CTA 分类（最终枚举）；
- 笔记形式选择规则（图文 vs 视频）；
- 关键词方向相关性判定算法；
- Hashtag 方向数量与边界；
- 视频镜头信息方向的结构；
- 最终错误代码；
- Golden Dataset 最终数据与阈值。

---

## §32 Out-of-Scope（当前不创建）

- 正式小红书 Prompt；
- 最终标题 / 正文 / Hashtags 生成；
- Final Copy Generator；
- 发布代码；
- Platform Policy Sync 代码；
- 数据库表；
- 风险词库；
- 自动审核实现；
- 图文或视频生成代码。

当前**不**选择：平台数据供应商 / 热点接口 / 搜索关键词工具 / 风险审核供应商 / 视频时长 / 图文页数 / Hashtag 数量 / 发布 API / 最终 LLM。当前**不**创建 RFC。保持 Development Status: **NOT READY**。

在 **Hybrid Retrieval and Evidence Runtime Architecture** 议题确认前，**不**选择 Embedding 模型、向量数据库、Chunk Size、Top-K 或 Reranker。
