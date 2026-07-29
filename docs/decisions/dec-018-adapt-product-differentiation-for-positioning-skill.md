# DEC-018：Product Differentiation Shopify 作为 Product Positioning Skill 的改造供体

> 本决定记录用户已明确接受的 Agent 决定（Candidate 2 评估结论）。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill = 带执行契约的可复用业务能力包）与 [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 优先研究、契约化改造后复用）。
> 对应评估记录：[../reviews/external-skills/product-differentiation-shopify-evaluation.md](../reviews/external-skills/product-differentiation-shopify-evaluation.md)。

## Type

Agent

## Status

Accepted（2026-07-27，用户对 Candidate 2 评估结论明确回复「确认」，通过 Decision Gate）

## Decision

项目正式将外部 Skill `nexscope-ai/eCommerce-Skills/product-differentiation-shopify`（Candidate 2）评定为：

```
Reuse Recommendation: Adapt
```

候选来源：

```
Repository: nexscope-ai/eCommerce-Skills
Skill:      product-differentiation-shopify
```

目标映射：

```
Product Positioning Skill
```

该候选**不直接作为项目正式 Skill 使用**，也**不直接采用其现有分析脚本作为最终商品定位引擎**。项目主要研究和改造其：

- 渐进式输入设计；
- 竞品比较矩阵；
- 用户痛点与竞品弱点分析；
- 商品优势识别；
- USP 提取方法；
- 品牌与商品定位框架；
- 价值主张设计；
- 差异化机会分析；
- 定位结果和行动建议的表达方式。

> 该结论承接 DEC-016 的「审计 → 裁剪 → 重构为 Skill Contract → 校验 → 接入 Workflow State」流程，改造后的 Skill 须符合 DEC-015 的 Skill Contract。

## Business Fit

该候选与项目核心业务链路高度匹配：

```
商品事实
+
用户洞察
+
竞品资料
↓
差异化分析
↓
商品定位候选
↓
营销策略与 Brief
```

它主要对应项目四层结构中的：

```
Strategy Layer
```

但会读取：

- Fact Layer；
- Insight Layer；
- 竞品证据；
- 推广目标。

它**不负责**：

- 原始商品事实确认；
- 评论采集；
- 完整营销 Brief 生成；
- 平台内容最终执行；
- 自动发布；
- 定价和利润决策。

## Retained Concepts

### 1. Progressive Input Levels

保留按资料丰富程度逐步增强分析的设计思想。概念映射：

```
Level 1  基础商品信息            → 形成基础定位候选
Level 2  增加竞品信息或竞品评论   → 形成差异化机会
Level 3  增加当前商品用户评论     → 形成有用户证据的卖点与价值主张
Level 4  增加市场、广告或渠道资料 → 形成更完整的定位与传播建议
```

该设计需要与项目已有的「最低可运行输入 + 增强输入」（DEC-005）保持一致。

> 具体 Level 名称、数量和解锁规则后续确定。

### 2. Competitor Comparison Matrix

保留竞品比较方法。可能比较的维度包括：功能、质量、设计、价格、服务、目标用户、使用场景、品牌表达、用户反馈、社会证明、价值主张。

> 比较维度必须来自当前任务真实资料，**不得为了填满矩阵而编造**。

### 3. Pain-point and Gap Analysis

保留从以下资料寻找差异机会的方法：当前商品评论、竞品评论、商品资料、用户访谈、市场资料。

可能形成：未满足需求、竞品常见问题、用户购买阻碍、当前商品潜在优势、需要进一步验证的机会。

> 这些结果属于**洞察或机会候选**，不自动成为商品事实。

### 4. USP and Value Proposition

保留从事实和洞察中形成：商品核心价值、关键差异点、核心卖点、价值主张、对比表达方向。

> USP **不得只由宽泛形容词组成**。

例如：

```
不推荐：
质量很好

推荐方向：
针对高频通勤人群，
通过轻量和紧凑设计降低携带负担。
```

> 最终表达必须与真实事实和用户洞察相关联。

### 5. Positioning Framework

保留形成以下候选结果的框架：目标用户候选、核心需求、购买阻碍、商品角色、使用场景、核心价值、差异化角度、卖点优先级、定位陈述候选、待验证假设。

## Components Not Adopted Directly

### Keyword Matching as Final Reasoning

候选仓库中的关键词匹配和频率统计可以作为：预处理、基础分类、召回辅助、规则基线、测试对照组。

但**不得直接作为最终洞察或定位依据**。项目**不采用**：

```
关键词命中 = 用户需求已经确认
```

也**不采用**：

```
提及次数最高 = 必须成为核心定位
```

原因包括：

- 相同词语在不同语境中含义不同；
- 用户可能在负面语境中提到某特征；
- 关键词无法稳定理解隐含需求；
- 高频不等于高商业价值；
- 少量高影响反馈可能比高频轻微反馈更重要。

### Final Positioning without Review

原始 Skill 输出的定位、目标用户或差异化建议**不能自动成为项目当前事实**。改造后的输出必须是：

```
Positioning Candidate
```

而不是：

```
Confirmed Positioning
```

### Unsupported Business-impact Estimates

不得在缺乏真实测试数据时直接输出：转化率提升百分比、销售额提升预测、LTV 提升预测、市场份额、精确机会规模、确定的收入影响。

> 这些内容只能在具有真实依据时展示，否则必须标记为推断或待验证假设。

### Pricing and Full Brand Strategy

以下内容**不属于**本 Skill 的 MVP 核心职责：完整价格策略、利润模型、品牌视觉体系、全渠道品牌战略、广告预算配置、长期品牌建设路线图、自动营销执行。

## Target Skill Contract Direction

> **以下为改造方向的概念性描述，不是最终 Skill Specification，也不是最终数据 Schema。** 具体名称、字段、Schema、级别、统计方法、Prompt、代码均见 Decision Boundary「尚未确认」项。

改造后的概念 Skill 名称为：

```
Product Positioning Skill
```

名称仍可在正式 Skill 规格阶段调整。

### Business Goal

根据当前有效的商品事实、用户洞察、竞品资料和推广目标，形成带依据、可审核的商品定位与卖点优先级候选。

### Candidate Inputs

> **概念输入，不是最终 Schema。**

```
current_valid_facts[]
customer_insights[]
competitor_products[]
competitor_insights[]
promotion_goal
product_constraints
retrieved_evidence[]
```

### Preconditions

调用前至少需要：

- 商品事实层处于有效状态；
- 输入来源能够识别；
- 当前任务拥有最低可运行输入；
- 需要用于定位的洞察已经生成或明确标记为资料不足。

> 如果用户没有提供竞品资料，Skill 可以生成基础定位候选，但必须标记 `competitive_evidence: insufficient`，**不得自行编造竞品**。

### Candidate Outputs

> **概念输出，不是最终数据契约。**

```
positioning_candidates[]
target_user_candidates[]
value_propositions[]
key_differentiators[]
selling_point_priorities[]
usage_scenarios[]
competitive_angles[]
risks[]
assumptions_to_validate[]
insufficient_information[]
```

每个重要定位候选至少需要能够表达：

```
item_id
statement
target_user
customer_need
product_value
supporting_fact_refs
supporting_insight_refs
source_refs
evidence_type
confidence_or_uncertainty
status
```

### Positioning Candidate Example

```
item_id: positioning-001

statement:
面向高频城市通勤用户，
强调轻量、紧凑和随身携带便利性的商品定位。

target_user:
高频通勤和短途出行用户

customer_need:
降低日常携带负担

supporting_fact_refs:
- fact-003
- fact-008

supporting_insight_refs:
- insight-002
- insight-006

evidence_type:
evidence_backed_strategy

status:
pending_review

assumption:
当前资料尚不足以确认性别和年龄是否应作为主要定位条件
```

### Evidence Requirements

商品定位候选需要至少关联：商品事实、用户洞察。在存在竞品分析时，还可以关联：竞品事实、竞品评论、差异化证据。

> **不得仅基于模型常识生成并标记为有证据定位。**

需要区分：

- **Evidence-backed Positioning Candidate**：由真实事实和洞察支持。
- **Model-inferred Positioning Candidate**：逻辑上合理，但证据有限。
- **Hypothesis to Validate**：需要用户或更多市场资料确认。
- **Insufficient Competitive Evidence**：当前没有足够竞品资料支撑差异化结论。

### Workflow Position

概念流程为：

```
Product Fact Extraction
↓
Customer Insight Analysis
↓
Product Positioning Skill
↓
Human Review
↓
Marketing Brief Generation
```

> 具体工作流节点数量仍未确认。Product Positioning Skill **不拥有**完整工作流控制权。

### Human Review

Product Positioning Skill 的输出必须进入项目已有的关键人工审核节点。用户应能够：

- 选择定位候选；
- 修改定位陈述；
- 接受或否定目标用户候选；
- 调整卖点优先级；
- 确认待验证假设；
- 补充竞品或用户资料；
- 拒绝不符合品牌方向的建议。

> 用户确认后，当前有效定位才可以进入执行层 Brief。

### Validation Requirements

正式 Skill 至少需要考虑：

- 输入 Fact Layer 必须有效；
- 输入 Insight Layer 必须有效；
- 引用的事实和洞察 ID 必须存在；
- 来源必须属于当前任务；
- 定位中的功能或参数不能超出商品事实；
- 目标用户不能被无依据地写成已确认事实；
- 卖点不能只有宽泛形容词；
- 竞品差异必须存在真实竞品依据；
- 无竞品资料时必须标记限制；
- 无用户证据时不能声称代表整体消费者；
- 输出必须符合结构化 Schema；
- 量化商业影响必须具有真实依据；
- 失效的上游状态不得进入定位生成。

> 具体规则和阈值后续确定。

### Failure and Pause Conditions

以下情况可能需要暂停、降级或标记资料不足：

- 商品事实严重缺失；
- 商品事实存在关键冲突；
- Customer Insight Layer 已失效；
- 引用的来源或 Insight 不存在；
- 用户要求竞品定位但未提供任何竞品资料；
- 定位候选依赖未确认的高风险假设；
- LLM 多次返回无效结构；
- 输出出现无依据参数或卖点；
- 竞品资料和当前商品资料发生错误归属。

### Testing Direction

正式 Skill 至少需要测试：

- 最低可运行输入；
- 完整增强输入；
- 没有用户评论；
- 没有竞品资料；
- 多个竞品；
- 商品没有明显差异；
- 商品事实与用户评价冲突；
- 高频关键词出现在负面语境；
- 多个定位候选均合理；
- 目标用户证据不足；
- 生成不存在的事实引用；
- 生成不存在的竞品；
- 用户修改洞察后局部重跑；
- 上游 Insight Layer 已失效；
- 输出 Schema 失败。

## Attribution

如果后续实际复制或修改原仓库中的：Prompt、分析框架文本、Python 代码、关键词库、数据结构、示例、输出模板——必须：

- 遵守原始 License；
- 保留必要的版权与许可声明；
- 在项目 README 或 Skill 文档中标明来源；
- 说明哪些内容被保留、修改或重写；
- 区分第三方供体和项目原创架构。

> 当前只确认研究与契约化改造方向，**不执行复制**。原始仓库 License 类型尚未核对（见评估记录 Open Questions）。

## Reason

该候选解决了 MVP 最核心的业务问题之一：如何把商品事实和用户洞察转化为可使用的商品定位与卖点优先级。它提供的渐进式输入、竞品矩阵、痛点挖掘、USP 和定位框架，能够减少项目从零进行电商方法设计的成本。

但是其原始实现不具备项目已经确认的：结构化 Workflow State、分级证据、来源追踪、人工审核、阶段失效、局部重跑、任务级持久化、确定性校验。其中关键词匹配代码只能作为辅助分析基线，不能替代语义分析和业务判断。

因此最合理的复用方式是 **Adapt**，而不是直接 Adopt。

## Impact

该决定将影响：Product Positioning Skill、MVP 核心业务链路、渐进式输入设计、竞品数据结构、Insight 到 Strategy 的转换、商品定位审核、卖点优先级、Marketing Brief Generation、Skill Attribution、测试和评价、后续 Multi-Agent 判断。

## Decision Boundary

**本决定已经确认：**

- Candidate 2 的评价为 Adapt；
- 它作为 Product Positioning Skill 的业务供体；
- 保留渐进输入、竞品矩阵、USP 和定位框架；
- 关键词匹配只作为辅助信号或基线；
- 不直接采用原始分析脚本作为最终定位引擎；
- 定位结果必须是待审核候选；
- 需要增加结构化输出；
- 需要增加事实、洞察和来源关联；
- 需要增加校验、失败处理和测试；
- 不直接复制实现；
- 实际复制时必须遵守 License 与 Attribution。

**本决定尚未确认：**

- Product Positioning Skill 的最终名称；
- 最终输入输出 Schema；
- 渐进输入的最终级别；
- 是否在 MVP 中要求竞品资料；
- 竞品资料采集方式；
- 关键词分析是否保留为确定性工具；
- 具体 Prompt；
- 具体模型；
- 具体代码；
- 定位候选数量；
- 置信度机制；
- 人工审核 UI；
- Skill 对应几个节点；
- Multi-Agent；
- 工作流框架；
- GitHub 基底仓库。

> 本决定**不**确认最终 Skill Schema、渐进级别、竞品数据采集、模型供应商、Agent 数量、Multi-Agent、LangGraph、工作流基底仓库。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related Review

Candidate 2：`product-differentiation-shopify` —— [../reviews/external-skills/product-differentiation-shopify-evaluation.md](../reviews/external-skills/product-differentiation-shopify-evaluation.md)

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill 契约化定义）与 [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 复用策略）：本决定是 DEC-016 首轮三候选中 **Candidate 2** 的正式评估结论（Candidate 1 已由 [DEC-017](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md) 评估为 Adapt）。
- Adapt 不等于已实现：Candidate 2 仍须走完 DEC-016 的改造流程并形成后续 Skill Specification 后，才能成为项目正式 Skill。
- 本决定**不**创建正式 Product Positioning Skill Specification，也**不**复制任何第三方 SKILL.md / Prompt / Python 脚本 / 关键词库 / 模板 / 示例 / 测试。
- 文中 Candidate Inputs / Outputs、Progressive Input Levels、Evidence Requirements、Validation Requirements 等均为**概念性改造方向**，非最终数据契约；最终名称、Schema、级别、统计方法、Prompt、代码、实现框架均未确认。
- 关键词匹配 / 频率统计**只作为辅助信号或基线**，不得作为最终定位推理依据。
- 候选 3（`feichanggege/ecommerce-visual-copywriting-skill`）仍**待评估**，本决定不影响其评价。
- 本决定**不**确认 Multi-Agent（Question-008 仍顺延）、Agent 数量、LangGraph、工作流基底仓库、竞品资料采集方式、模型供应商。
