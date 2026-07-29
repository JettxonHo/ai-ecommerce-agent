# DEC-017：Product Review Analysis 作为 Customer Insight Skill 的改造供体

> 本决定记录用户已明确接受的 Agent 决定（Candidate 1 评估结论）。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill = 带执行契约的可复用业务能力包）与 [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 优先研究、契约化改造后复用）。
> 对应评估记录：[../reviews/external-skills/product-review-analysis-evaluation.md](../reviews/external-skills/product-review-analysis-evaluation.md)。

## Type

Agent

## Status

Accepted（2026-07-27，用户对 Candidate 1 评估结论明确回复「确认」，通过 Decision Gate）

## Decision

项目正式将外部 Skill `nexscope-ai/eCommerce-Skills/product-review-analysis`（Candidate 1）评定为：

```
Reuse Recommendation: Adapt
```

候选来源：

```
Repository: nexscope-ai/eCommerce-Skills
Skill:      product-review-analysis
```

目标用途：

```
Customer Insight Analysis Skill
```

该外部 Skill**不作为项目正式 Skill 直接使用**，而是作为以下内容的**研究和改造供体**：

- 评论分析维度；
- 用户痛点识别方法；
- 好评主题和价值感知分析；
- 功能需求提取；
- 用户语言分析；
- 购买阻碍分析；
- 使用场景归纳；
- 竞品评论对比方法；
- 评论洞察向营销信息转化的思路；
- 测试案例和报告结构参考。

> 该结论承接 DEC-016 的「审计 → 裁剪 → 重构为 Skill Contract → 校验 → 接入 Workflow State」流程，改造后的 Skill 须符合 DEC-015 的 Skill Contract。

## Business Fit

该候选与项目核心链路具有较高匹配度：

```
用户评论与反馈
→ 用户需求、痛点、动机与阻碍
→ Customer Insights
→ 商品定位
→ 营销 Brief
```

它主要对应项目四层结构中的：

```
Insight Layer
```

而**不是**：

- Fact Layer 的完整事实提取；
- Product Positioning 的最终决策；
- Strategy Layer 的完整生成；
- Execution Brief 的最终文案输出。

## Retained Concepts

改造时优先保留以下分析能力。

### Customer Pain Points

识别：

- 反复出现的使用问题；
- 用户不满意的原因；
- 影响购买或复购的障碍；
- 用户对质量、功能、尺寸、使用体验和价值的负面反馈。

### Positive Value Perception

识别：

- 用户持续称赞的特点；
- 用户实际感知到的产品价值；
- 可能形成核心卖点的正向反馈；
- 用户愿意推荐或复购的原因。

### Customer Needs and Requests

识别：

- 用户明确提出的功能需求；
- 隐含但反复出现的未满足需求；
- 期望的改进方向；
- 使用场景中的需求缺口。

### Customer Language

保留用户描述商品、痛点和价值时的原始表达方式，用于后续：

- 商品定位；
- 卖点表达；
- 营销 Brief；
- 平台内容适配。

### Competitive Review Intelligence

在用户提供竞品评论时，支持比较：

- 用户对不同商品的主要评价；
- 竞品常见弱点；
- 当前商品的相对优势；
- 潜在差异化机会。

> 这些结果仍然只作为 **Insight 或 Opportunity Candidate**，不自动成为最终商品定位。

## Components Not Adopted Directly

以下部分不直接照搬。

### Report-first Output

原 Skill 偏向一次性生成完整评论分析报告。项目需要重构为：

```
结构化 insight items
+
必要的摘要视图
```

完整 Markdown 报告不能成为唯一正式输出。

### Unsupported Quantification

不得在没有真实统计数据或样本计算时自动输出：

- 精确百分比；
- 精确频率；
- 精确评分影响；
- 市场规模；
- 收入提升预测；
- 转化率提升承诺。

只有在程序真实计算并保留样本范围时，才能输出量化结果。

### Final Product Positioning

原 Skill 中可能包含的市场机会、产品定位和营销建议，不能直接成为最终策略。这些内容只能作为：

- 洞察；
- 机会候选；
- 定位输入；
- 待审核建议。

最终定位由后续 Product Positioning Skill 和人工审核流程处理。

### Broad Operational Modules

以下内容**不属于**本 Skill 的 MVP 核心职责：

- 产品开发路线图；
- 客服回复策略；
- 持续评论监控；
- 生产质量管理计划；
- 长期经营计划；
- 完整营销活动方案。

这些内容可以作为未来扩展，但当前需要从 Customer Insight Analysis Skill 中移除或隔离。

## Target Skill Contract Direction

> **以下为改造方向的概念性描述，不是最终 Skill Specification，也不是最终数据 Schema。** 具体名称、字段、Schema、分类、统计方法、Prompt、代码均见 Decision Boundary「尚未确认」项。

改造后的 Skill 暂定概念名称为：

```
Customer Insight Analysis Skill
```

名称仍可在后续规格设计中调整。

### Business Goal

基于当前有效商品事实、用户评论、用户访谈或竞品反馈，形成可追溯的用户洞察候选。

### Candidate Inputs

> **概念输入，不是最终 Schema。**

```
product_context
current_valid_facts[]
review_sources[]
competitor_review_sources[]
promotion_goal
retrieved_evidence[]
```

### Candidate Outputs

> **概念输出，不是最终数据契约。**

```
customer_needs[]
pain_points[]
purchase_motivations[]
purchase_barriers[]
usage_scenarios[]
positive_value_signals[]
customer_language_patterns[]
feature_requests[]
competitor_insights[]
insufficient_information[]
```

每个关键洞察条目应能够表达：

```
item_id
insight_type
content
evidence_type
source_refs
status
generated_by
user_modified
```

### Evidence Requirements

每一个被标记为有证据洞察的条目必须：

- 关联真实 `source_ref`；
- 能够定位到用户评论、访谈或竞品资料片段；
- 不得引用未被读取的内容；
- 不得伪造评论；
- 不得将模型常识包装成用户反馈；
- 不得因为语义合理就自动标记为事实。

例如：

```
insight-001
内容：部分通勤用户重视商品的便携性
类型：evidence_backed_insight
source_refs:
  - review-fragment-012
  - review-fragment-027
status: pending_review
```

### Analysis Classification

改造后的 Skill 需要区分：

- **Evidence-backed Insight**：存在真实评论或资料片段支持的归纳。
- **Model Inference**：基于事实和评论形成，但证据不足以直接确认的推断。
- **Hypothesis to Validate**：需要用户或更多资料进一步确认的假设。
- **Insufficient Information**：当前资料不足以形成可靠结论。

> 不得把所有分析结果统一写成确定结论。

### Workflow Position

该 Skill 原则上位于：

```
资料处理
→ 商品事实候选
→ Customer Insight Analysis Skill
→ Product Positioning Skill
→ Human Review
→ Marketing Brief Generation
```

> 具体节点顺序和调用次数仍未确认。该 Skill 不拥有完整工作流控制权。

### Human Review

Customer Insight Analysis Skill 的结果应进入人工审核材料。用户需要能够：

- 接受洞察；
- 修改洞察；
- 否定洞察；
- 确认待验证假设；
- 补充资料；
- 触发下游失效与局部重跑。

> 人工审核的具体 UI 和操作仍未确定。

### Validation Requirements

正式 Skill 至少需要以下校验方向：

- 有证据洞察必须存在真实来源；
- `source_ref` 必须属于当前任务；
- 无证据内容不得标记为明确事实；
- 洞察不能直接覆盖商品事实；
- 输出必须符合结构化 Schema；
- 当前事实阶段失效时不得继续分析；
- 量化结论必须来自真实统计；
- 输入样本过少时必须标记局限；
- 评论来源不明时不得声称代表整体用户；
- 竞品评论不得错误归属到当前商品。

> 具体校验规则和阈值后续确定。

### Failure and Pause Conditions

以下情况可能需要暂停或降级：

- 没有任何评论或用户反馈，但任务要求评论洞察；
- 评论来源无法识别；
- 评论内容严重重复或疑似污染；
- 当前商品与竞品评论混淆；
- 关键来源无法读取；
- LLM 多次无法返回有效结构；
- 输出出现不存在的来源引用；
- 资料之间存在严重冲突；
- 当前事实层已经失效。

> 具体暂停规则后续确定。

### Testing Direction

正式 Skill 至少需要覆盖：

- 正常评论集合；
- 少量评论；
- 没有评论；
- 全部正面评论；
- 全部负面评论；
- 中英文混合评论；
- 当前商品和竞品评论混合；
- 重复评论；
- 来源缺失；
- 评论与商品事实冲突；
- 模型生成不存在的引用；
- 用户修改事实后重新分析；
- RAG 未召回足够证据；
- 输出 Schema 失败。

## Attribution

如果后续实际复制或修改原仓库中的：

- Prompt；
- 文档；
- 模板；
- 规则；
- 代码；
- 示例；

必须根据其 License：

- 保留必要的版权和许可声明；
- 在项目 README 或相关 Skill 文档中标明来源；
- 说明项目进行了哪些修改；
- 区分第三方框架与项目原创契约和实现。

> 当前只确认研究与改造方向，**不执行复制**。原始仓库 License 类型尚未核对（见评估记录 Open Questions）。

## Reason

该候选覆盖的评论分析能力与商品定位和营销 Brief 链路高度相关，可以减少从零设计以下内容的成本：

- 评论分析维度；
- 用户痛点分类；
- 好评主题分析；
- 用户语言提取；
- 功能需求识别；
- 竞品反馈对比；
- 输出模板；
- 测试场景。

但原 Skill 主要是报告型纯文本指令，缺少项目已经确认的：

- 结构化 Workflow State；
- 来源和证据契约；
- 五类结果标记；
- 人工审核；
- 阶段失效；
- 局部重跑；
- 任务级持久化；
- 确定性校验。

因此最合理的复用方式是 **Adapt**，而不是直接 Adopt。

## Impact

该决定将影响：

- MVP Skill 清单；
- Customer Insight Analysis Skill；
- 评论数据模型；
- 混合 RAG；
- 来源片段结构；
- Workflow State；
- 人工审核；
- 商品定位输入；
- 测试数据集；
- Skill Attribution；
- 后续开源改造说明。

## Decision Boundary

**本决定已经确认：**

- Candidate 1 的评价为 Adapt；
- 它作为 Customer Insight Analysis Skill 的供体；
- 保留评论分析方法和部分输出框架；
- 不直接采用完整报告式输出；
- 需要增加结构化输出；
- 需要增加来源与证据关系；
- 需要增加校验、暂停和测试；
- 不直接生成最终商品定位；
- 不直接复制实现；
- 后续实际复制时必须遵守 License 和 Attribution 要求。

**本决定尚未确认：**

- Customer Insight Analysis Skill 的最终名称；
- 最终输入输出 Schema；
- 具体分析分类；
- 评论统计方法；
- 情绪分析模型；
- 具体 Prompt；
- 具体代码；
- 评论数据采集方式；
- RAG Chunking；
- Top-K；
- 是否使用该仓库的任何具体代码；
- 是否在 MVP 中处理竞品评论；
- 是否在 MVP 中支持持续评论监控；
- 该 Skill 对应几个工作流节点；
- Multi-Agent；
- 具体实现框架。

> 本决定**不**确认 LangGraph、最终 Skill Schema、实现框架、Agent 数量、Multi-Agent、评论采集方案、模型供应商。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related Review

Candidate 1：`product-review-analysis` —— [../reviews/external-skills/product-review-analysis-evaluation.md](../reviews/external-skills/product-review-analysis-evaluation.md)

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill 契约化定义）与 [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 复用策略）：本决定是 DEC-016 首轮三候选中 **Candidate 1** 的正式评估结论。
- Adapt 不等于已实现：Candidate 1 仍须走完 DEC-016 的改造流程并形成后续 Skill Specification 后，才能成为项目正式 Skill。
- 本决定**不**创建正式 Customer Insight Analysis Skill Specification，也**不**复制任何第三方 Prompt / SKILL.md / 代码 / 模板 / 测试 / 示例。
- 文中 Candidate Inputs / Outputs、Evidence Requirements、Validation Requirements 等均为**概念性改造方向**，非最终数据契约；最终 Schema、统计方法、Prompt、代码、实现框架均未确认。
- 候选 2（`product-differentiation-shopify`）与候选 3（`feichanggege/ecommerce-visual-copywriting-skill`）仍**待评估**，本决定不影响其评价。
- 本决定**不**确认 Multi-Agent（Question-008 仍顺延）、Agent 数量、LangGraph、评论采集方案、模型供应商。
