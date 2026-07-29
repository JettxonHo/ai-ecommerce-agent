# DEC-027：Customer Insight Analysis Skill 采用证据模式与降级假设模式，并禁止虚构用户原声和检索样本频率外推

> **Type:** Skill Contract / Reliability Architecture
> **Status:** Accepted
> **Date:** 2026-07-28
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)（概念 Skill Spec，仅概念）
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** [DEC-017](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md) by defining the formal Customer Insight Analysis Skill Contract（在 DEC-017 评估结论「`product-review-analysis` 作为 Customer Insight Analysis Skill 改造供体」基础上，正式定义该 Skill 的概念层执行契约，**不推翻** DEC-017 的评估结论与 Adapt 方向）。

---

## 用户确认

用户对该 Customer Insight Analysis Skill Contract Proposal 明确回复：

> 确认

本决定经 Decision Gate 通过，记录为 Accepted Decision（Type: Skill Contract / Reliability Architecture）。

被接受的核心结论：

- Customer Insight Analysis Skill 负责将用户评论、访谈、问卷、售后反馈、竞品用户反馈和其他相关证据，转换为可追溯的用户主题、用户问题、需求、使用场景、购买动机、购买障碍、信任顾虑和用户原声。
- 该 Skill 必须支持 **Evidence-backed Mode** 和 **Degraded Hypothesis Mode**。存在真实用户证据时，可以生成 Evidence-backed Insights；不存在直接用户证据时，可以基于商品事实、使用场景、品类证据和竞品反馈生成待验证假设，但**不得**将其表示为真实用户共识。
- 系统禁止虚构用户原声，禁止把模型概括内容伪装成直接引语，禁止根据 RAG Top-K 召回样本推断总体比例，禁止把竞品用户反馈归因于当前商品用户。

---

## Decision

MVP 的第二个核心业务 Skill 正式定义为：

```text
Customer Insight Analysis Skill
```

其业务目标是：

将用户证据和相关市场证据转化为可追溯、可解释、可供商品定位使用的用户洞察，同时明确区分真实用户证据、模型推断和待验证假设。

该 Skill **不**负责：

- 决定最终商品定位；
- 选择最终目标人群；
- 生成 Marketing Brief；
- 生成小红书文案；
- 直接发布营销内容；
- 使用竞品反馈证明当前商品实际表现；
- 在没有证据时创造用户需求或用户原声。

### Skill 职责与概念流程

Skill 负责：

- 用户证据覆盖判断；
- 主题识别；
- 洞察形成；
- 反向证据分析；
- 假设分类；
- 证据校验；
- 输出可追溯、可版本化的用户洞察 / 待验证假设 / 用户原声 / 主题 / 证据评估 / 限制说明 / 阶段决策。

概念流程：

```text
Verified Facts
+
Customer Evidence Package
↓
Evidence Coverage Assessment
↓
Theme Detection
↓
Insight Formation
↓
Counter-evidence Analysis
↓
Hypothesis Classification
↓
Evidence Validation
↓
Customer Insights Version
```

---

## Skill Inputs

该 Skill 概念上接收：

```text
Valid Facts Version
+
Customer Insight Source Set Version
+
Customer Evidence Package
+
Optional Dataset Statistics
+
Task and Product Context
```

输入至少包括：

- 当前有效 Facts Version；
- 商品身份与品类；
- 当前商品用途；
- 当前商品用户证据；
- 可选竞品用户证据；
- 可选访谈、问卷、售后和客服资料；
- 可选评论统计；
- 当前 Source Set Version；
- 当前证据限制。

---

## Theme and Insight Boundary

必须区分 **Theme** 与 **Insight**。

### Theme

Theme 表示用户反馈中反复出现或具有业务意义的讨论主题。

例如：

```text
漏水
保温
重量
外观
清洗
价格
售后
```

Theme 只回答：

> 用户在讨论什么？

Theme 本身**不**自动构成业务洞察。

### Insight

Insight 至少需要表达：

```text
谁
+
在什么场景
+
遇到什么问题或需求
+
为什么重要
+
如何影响使用、购买或信任
```

例如：

> 经常将水杯放入通勤包的用户担心杯盖密封性，因为即使少量漏水也可能损坏电脑或文件，从而降低其购买信心。

**不得**将：

```text
用户提到了漏水
```

直接包装成完整用户洞察。

---

## Supported Evidence Types

### Direct Customer Evidence（第一优先级）

包括：

- 当前商品评论；
- 用户访谈；
- 问卷开放题；
- 售后反馈；
- 退货原因；
- 客服记录；
- 用户测试记录；
- 用户主动提交的使用反馈。

这类来源可以支持当前商品用户体验相关洞察。

### Competitor Customer Evidence（第二优先级）

包括：

- 竞品评论；
- 竞品问答；
- 竞品用户讨论；
- 竞品售后反馈；
- 竞品退货或投诉资料。

竞品用户证据可以支持：

- 品类共性问题；
- 用户期待；
- 竞品弱点；
- 市场用户语言；
- 差异化机会假设；
- 待验证用户需求。

竞品证据**不能**直接证明：

> 当前商品用户具有同样体验。

### Indirect Business Evidence

可以包括：

- 搜索词；
- 商品问答；
- 点击或转化数据；
- 退货率；
- 售后问题分类；
- 运营人员记录；
- 市场调研材料。

这类来源可以辅助形成 Insight，但必须明确证据性质和限制。

### Non-customer Evidence

商品参数、说明书、认证和检测报告属于商品事实来源，**不**属于用户反馈。

它们可以帮助解释商品能力和使用场景，但**不能**单独证明：

> 用户真正需要、认可或担忧某项内容。

---

## Two Operating Modes

### Evidence-backed Mode

存在真实用户证据时使用。

允许输出：

```text
Evidence-backed Insight
```

要求：

- 有真实用户 Fragment；
- Fragment ID 可追溯；
- Source Scope 明确；
- Source Version 有效；
- 支持证据可查看；
- 反向证据可查看；
- 不扩大样本范围；
- 不使用少量反馈代表所有用户。

### Degraded Hypothesis Mode

不存在足够直接用户证据时使用。

可以基于：

- 商品事实；
- 商品用途；
- 合理使用场景；
- 品类常见任务；
- 竞品用户证据；
- 用户提供的目标人群描述；

生成：

```text
Hypothesis to Validate
```

例如：

> 对需要随身携带水杯的通勤用户而言，防漏能力可能是重要购买因素。

必须明确标记：

```text
当前没有直接用户证据
该结论为待验证假设
```

不得表达为：

```text
用户最关心防漏
```

无真实用户原文时，**不得**生成带引号的模拟用户语言。

---

## Evidence Coverage

不使用模型主观百分制 Confidence。采用可解释的证据覆盖状态：

```text
none
anecdotal
repeated_signal
dataset_supported
multi_source_corroborated
```

### none

没有用户证据，只能进入 Degraded Hypothesis Mode。

### anecdotal

只有单条或极少数独立反馈。

只能表达为：

```text
Observed Signal
```

或：

```text
Anecdotal Signal
```

不能表达为稳定模式或普遍共识。

### repeated_signal

多个独立用户或记录出现相似问题，可以形成有限范围的 Evidence-backed Insight。

### dataset_supported

基于完整、可计数数据集分析，具备明确样本量、统计方法和记录范围。

### multi_source_corroborated

评论、访谈、售后、问卷或其他不同来源相互印证。

这是较强的用户证据状态。

---

## No Universal Sample Threshold

MVP **不**设定统一规则：

```text
至少 N 条评论才能形成 Insight
```

原因包括：

- 一条严重安全投诉可能具有高业务价值；
- 多条重复或机器人评论可能没有独立性；
- 一次深入访谈可能比多条短评包含更多信息；
- 不同证据类型不能只按数量比较。

洞察形成需要结合：

```text
独立记录数量
+
来源类型
+
证据覆盖
+
数据质量
+
反向证据
+
业务严重性
```

但必须遵守：

> 单条反馈不能被表达为普遍用户共识。

单条严重反馈可以输出：

```text
Critical Anecdotal Signal
```

---

## Insight Types

MVP 概念上至少支持：

```text
pain_point
desired_outcome
functional_need
emotional_need
usage_context
purchase_motivation
purchase_barrier
trust_concern
product_satisfaction
product_dissatisfaction
unmet_need
switching_trigger
customer_language
```

- **pain_point** — 用户实际遇到的问题。
- **desired_outcome** — 用户希望获得的结果。
- **functional_need** — 用户希望商品完成的功能任务。
- **emotional_need** — 安心、轻松、体面、控制感或其他心理需求。
- **usage_context** — 问题或需求发生的实际场景。
- **purchase_motivation** — 推动购买的理由。
- **purchase_barrier** — 阻碍购买的顾虑、成本或限制。
- **trust_concern** — 用户对安全、质量、认证、真实性或售后的担忧。
- **unmet_need** — 当前商品或市场没有充分满足的需求。

（其余类型 product_satisfaction / product_dissatisfaction / switching_trigger / customer_language 含义按其名称语义理解；最终名称与 Schema 未确认。）

---

## Insight Item Concept

概念结构：

```text
InsightItem
├── insight_id
├── insight_type
├── statement
├── audience_segment
├── usage_context
├── user_problem_or_need
├── underlying_reason
├── behavioral_or_purchase_impact
├── evidence_class
├── evidence_coverage
├── supporting_fragment_ids[]
├── contradicting_fragment_ids[]
├── dataset_statistic_ids[]
├── customer_language_ids[]
├── based_on_fact_ids[]
├── source_scope
├── limitations[]
├── review_status
└── notes
```

以上**不**是最终数据库 Schema。

---

## Customer Language Rules

用户原声是重要业务输入，但必须严格防止伪造。

### Allowed

直接用户原声必须来自真实 Fragment。

必须能够追踪：

- Fragment ID；
- Source；
- Source Version；
- Review、Interview 或 Survey Record；
- Locator；
- 必要上下文。

### Forbidden

模型**不得**：

- 自己写一句话并加引号；
- 将多条评论拼接成虚构用户原声；
- 修改原文后仍声称是直接引用；
- 把模型概括伪装为原文；
- 把竞品评论展示为当前商品用户原声；
- 把翻译文本伪装成原语言直接引用。

### Presentation Boundary

系统可以分别展示：

```text
Original Customer Language
```

和：

```text
Model Summary
```

两者必须明确区分。

---

## Dataset Statistics Boundary

### Theme Discovery

LLM 可以辅助：

- 主题识别；
- 相似表达归类；
- 场景分类；
- 正负面判断；
- 用户需求归纳。

### Formal Frequency

正式比例和频率**必须**由确定性统计产生。

例如：

```text
120 条有效评论中，
18 条提到漏水，
占 15%
```

必须至少记录：

- 有效数据集版本；
- 评论总数；
- 去重规则；
- 分子记录 ID；
- 分母；
- 主题分类规则或版本；
- 统计时间；
- 统计方法。

### Prohibited Frequency Inference

**禁止**根据 RAG Top-K 召回结果计算或推断总体比例。

Top-K 表示：

```text
与当前 Query 相关的候选证据
```

**不**表示：

```text
总体样本的随机或完整分布
```

---

## Supporting and Contradicting Evidence

重要 Insight 应尽量检查反向证据。

例如：

```text
Insight：
部分用户担心杯盖漏水

Supporting Evidence：
12 条评论提到漏水

Contradicting Evidence：
8 条评论明确认可密封性
```

最终表达应反映真实证据差异，例如：

> 部分用户报告了漏水问题，但也存在明确认可密封性的反馈，问题可能与使用方式、批次或型号有关。

模型**不得**只选择符合预期的证据并隐藏反向信息。

---

## Conflicting User Needs

不同用户群可能存在相反需求。

例如：

```text
一部分用户希望杯体更轻
另一部分用户认为轻量降低质感
```

这可以被表达为：

```text
Conflicting User Needs
```

可能说明：

- 用户细分不同；
- 使用场景不同；
- 价格期待不同；
- 型号需求不同。

但系统**不得**在证据不足时凭空创造用户细分。细分解释可以先标记为：

```text
Hypothesis to Validate
```

---

## Facts and Insights Boundary

**Fact**

```text
商品重量为 260 克
```

**Evidence-backed Insight**

```text
多条通勤用户反馈显示，
长时间携带时重量会影响购买选择。
```

**Hypothesis**

如果没有用户反馈，只能表达为：

```text
需要长时间携带水杯的用户，
可能更加关注商品重量。
```

**不得**从商品事实直接推断：

```text
用户一定认为商品很轻
```

---

## Skill Outputs

输出分为五个部分。

### 1. Evidence Assessment

概念输出：

```text
mode
evidence_coverage
source_types[]
source_set_version_id
sample_summary
limitations[]
```

### 2. Themes

```text
themes[]
```

Themes 用于展示主要讨论内容，**不**自动作为正式 Insight。

### 3. Customer Insights

```text
insights[]
```

用于保存 Evidence-backed Insights。

### 4. Hypotheses

```text
hypotheses_to_validate[]
```

用于保存证据不足或降级模式下的假设。

### 5. Workflow Decision

```text
stage_decision:
- valid
- valid_with_limitations
- waiting_input
- paused
- failed
```

---

## Workflow Decision Boundary

### valid

存在足够真实证据，可以形成一组可追溯用户洞察。

### valid_with_limitations

可以继续进入 Product Positioning，但存在明显限制，例如：

- 当前商品评论较少；
- 只有竞品评论；
- 只有用户提供的目标人群；
- 缺少完整数据集；
- 当前运行于 Degraded Hypothesis Mode。

Product Positioning Skill **必须**能够读取并展示这些限制。

### waiting_input

当用户明确要求必须基于评论或访谈分析，但没有提供资料，且不接受假设模式时使用。

默认情况下，MVP 可以在没有用户证据时使用 Degraded Hypothesis Mode 继续运行。

### paused

适用于：

- 当前商品评论和竞品评论严重混淆；
- 用户数据权限异常；
- 评论属于错误商品；
- 数据中存在大量重复、污染或异常内容；
- 主要用户证据来源被撤回。

### failed

适用于技术故障，例如：

- 评论解析失败；
- 模型多次无法输出合法 Schema；
- 统计服务异常；
- Evidence Validator 内部错误；
- 数据持久化失败。

业务证据不足**不得**错误标记为技术失败。

---

## Deterministic Validator

Insight 写入正式 Insights Version 前，至少检查：

1. 所有 Fragment ID 真实存在；
2. Fragment 属于当前任务或合法 Workspace；
3. Source Version 当前可用；
4. 当前商品与竞品 Source Scope 没有混淆；
5. 用户原声确实来自原始 Fragment；
6. 直接引语未被模型改写；
7. Dataset Statistic 可以回溯到完整数据集；
8. 比例分子与分母合法；
9. Top-K 召回没有被当作总体统计；
10. 单条反馈没有被表达为普遍共识；
11. 无直接证据的用户结论被标记为 Hypothesis；
12. Supporting Evidence 与 Insight 语义相关；
13. Contradicting Evidence 没有被误标为支持证据；
14. 输出符合 Schema；
15. 所引用 Facts Version 当前有效；
16. 没有虚构用户细分；
17. 没有虚构用户语言；
18. 没有把竞品用户体验写成当前商品用户体验。

Validator 负责证据边界和引用可靠性，**不**负责评价洞察是否足够有创意。

---

## Responsibility Boundary

### Deterministic Logic

负责：

- 数据集计数；
- 评论去重；
- 样本量；
- 百分比；
- Source Scope；
- Fragment ID；
- 来源权限；
- Evidence Link；
- Schema；
- Version Dependency；
- 幂等写入；
- 阶段状态；
- Current Truth 更新。

### LLM

负责：

- 主题发现；
- 用户问题归纳；
- 使用场景识别；
- 需求和动机分析；
- 相似表达聚类；
- 正向与反向证据总结；
- Insight 表述；
- Hypothesis 生成；
- 证据限制说明。

### Human

负责：

- 修正错误主题；
- 合并或拆分洞察；
- 判断业务重要性；
- 选择值得进入定位阶段的洞察；
- 补充实际业务背景；
- 在统一 Human Review Gate 中确认关键洞察。

---

## Insight Prioritization

可以输出候选优先级，但**不**使用模型自由生成的单一综合 Confidence 分数。

优先级可参考以下可解释维度：

```text
evidence_coverage
frequency
severity
purchase_impact
strategic_relevance
actionability
```

约束：

- `frequency` 只有存在正式统计时才能使用；
- `severity` 可以标记低频但高影响问题；
- `purchase_impact` 可能属于模型业务推断；
- `strategic_relevance` 需要结合商品事实；
- `actionability` 表示是否可以被产品或营销响应。

该排序只是候选排序，**不**等于最终商品战略优先级。

---

## Evaluation Metrics

### Hard Reliability Metrics

MVP 目标：

```text
Invalid Fragment Reference Rate = 0%
Fabricated Customer Quote Rate = 0%
Top-K Frequency Hallucination Rate = 0%
Current-product / Competitor Misattribution Rate = 0%
Unsupported Consensus Claim Rate = 0%
```

### Insight Quality Metrics

包括：

- Theme Classification Accuracy；
- Insight Evidence Relevance；
- Pain Point Extraction Precision；
- Usage Context Accuracy；
- Purchase Barrier Recall；
- Counter-evidence Coverage；
- Hypothesis Classification Accuracy；
- Duplicate Insight Rate。

### User Value Metrics

包括：

- 用户接受的洞察比例；
- 用户修改洞察的数量；
- 用户认为可用于定位的洞察比例；
- 从用户资料到可用 Insights 的时间；
- Insight 对最终 Positioning 的实际使用率。

模型自报 Confidence **不**作为核心评价指标。

---

## Required Test Scenarios

### TS-1：No Customer Evidence

输入：

- 有效商品事实；
- 无评论、访谈或问卷。

预期：

- 使用 Degraded Hypothesis Mode；
- 不生成虚构用户原声；
- 用户需求结论标记为 Hypothesis；
- 阶段为 `valid_with_limitations`。

### TS-2：One Negative Review

预期：

- 只能输出 Anecdotal Signal；
- 不表达为普遍问题；
- 严重问题可以单独警告。

### TS-3：Complete Review Dataset

预期：

- 确定性计算频率；
- 输出样本量；
- 生成 Evidence-backed Insights；
- 保存分子记录 ID 和数据集版本。

### TS-4：Competitor Reviews Only

预期：

- 可以生成品类问题和市场假设；
- 不描述为当前商品用户反馈；
- 阶段为 `valid_with_limitations`。

### TS-5：Supporting and Contradicting Evidence

预期：

- 同时展示正向和反向证据；
- 不隐瞒证据冲突；
- 用户细分解释在证据不足时标记为 Hypothesis。

### TS-6：Top-K Retrieved Reviews

预期：

- 可以作为相关证据示例；
- **不允许**输出总体比例。

> 以上为**概念测试场景，非最终 Golden Dataset**；最终测试数据、阈值与评价实现未确认。

---

## Skill Contract Summary

```text
Skill:
Customer Insight Analysis

Input:
- Valid Facts Version
- Customer Evidence Package
- Customer Insight Source Set Version
- Optional Dataset Statistics

Modes:
- Evidence-backed Mode
- Degraded Hypothesis Mode

Output:
- Evidence assessment
- Themes
- Customer insights
- Customer language
- Counter-evidence
- Hypotheses
- Limitations
- Workflow decision

Hard Rules:
- No fabricated customer quote
- No Top-K-based frequency claim
- No competitor feedback attributed to current product
- No unsupported consensus claim
```

---

## Reason

用户洞察是商品定位的主要输入之一。

如果该层允许：

- 虚构用户原声；
- 使用少量检索结果推断总体频率；
- 将竞品反馈冒充当前商品反馈；
- 将商品事实直接转换成用户需求；
- 将单条反馈表示为用户共识；

则错误会进入：

```text
Customer Insight
→ Product Positioning
→ Marketing Brief
→ Platform Mapping
```

因此该 Skill 的目标**不是**生成看起来有深度的洞察，而是：

> 只生成证据边界明确、来源可追溯、限制可解释，并能被后续定位阶段正确使用的用户洞察或待验证假设。

---

## Impact

该决定将影响：

- Insight Domain Model；
- Customer Insight Evidence Package；
- 评论导入和解析；
- 评论统计；
- Source Scope；
- Evidence Validator；
- Product Positioning Skill；
- Human Review；
- 前端洞察展示；
- Evaluation Dataset；
- RAG 设计；
- 用户证据不足时的产品体验。

---

## Decision Boundary

本决定**已经确认**：

- Customer Insight Skill 的业务边界；
- Evidence-backed Mode；
- Degraded Hypothesis Mode；
- 无用户证据时允许继续；
- 无用户证据时只能生成 Hypothesis；
- Theme 与 Insight 分离；
- 当前商品反馈、竞品反馈和间接证据分离；
- 竞品反馈不能冒充当前商品反馈；
- 用户原声必须来自真实 Fragment；
- 禁止虚构用户原声；
- 禁止改写内容冒充直接引用；
- Evidence Coverage 状态；
- 不设统一僵硬样本门槛；
- 单条反馈只能作为 Anecdotal Signal；
- 评论总体比例必须基于完整数据集；
- 禁止 Top-K 频率外推；
- 重要洞察需要检查反向证据；
- 允许表达冲突用户需求；
- Facts 与 Insights 的边界；
- 五组 Skill 输出；
- `valid_with_limitations` 状态；
- Validator 规则；
- LLM、确定性逻辑和人工职责；
- 硬性可靠性指标。

本决定**尚未确认**：

- 最终 Insight Schema；
- 最终字段名称；
- 数据库表；
- 评论主题分类表；
- 聚类算法；
- Embedding；
- 评论去重算法；
- 情感分析实现；
- 最低评论数量；
- 频率阈值；
- 优先级公式；
- Prompt；
- 模型；
- 评论导入格式；
- 前端 Insight 页面；
- 具体错误代码。

---

## Related Session

[Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)

---

## Related Decisions

- [DEC-008 — MVP 采用分级证据标记与结论可追溯机制](dec-008-tiered-evidence-and-traceable-conclusions.md)（Evidence Classes）
- [DEC-009 — MVP 采用阶段级依赖失效与局部重跑](dec-009-stage-level-invalidation-and-partial-rerun.md)（Stage Invalidation）
- [DEC-014 — MVP 采用按需、混合式 RAG 与分层数据访问策略](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（Hybrid RAG）
- [DEC-015 — Skill 定义为带执行契约的可复用业务能力包](dec-015-contract-based-reusable-business-skills.md)（Contract-based Skill）
- [DEC-017 — Product Review Analysis 作为 Customer Insight Skill 的改造供体](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)（Customer Insight Candidate Adaptation；**本决定 Amends DEC-017**）
- [DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（Core Skills）
- [DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](dec-025-versioned-sources-fragments-and-evidence-links.md)（Source and Evidence Architecture）
- [DEC-026 — Product Intake & Fact Extraction Skill 采用分层输入完整度、零无来源事实与冲突暂停契约](dec-026-product-intake-and-fact-extraction-skill-contract.md)（Product Intake & Fact Extraction Skill Contract；本 Skill 的上游 Facts Layer）

---

## Related RFC

None

---

## Supersedes

None

---

## Amends

**Amends [DEC-017](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)** by defining the formal Customer Insight Analysis Skill Contract。

- DEC-017 评估结论为 Candidate 1（`product-review-analysis`）= Adapt，作为 Customer Insight Analysis Skill 的研究与改造供体，并保留评论分析方法（痛点 / 价值感知 / 需求 / 语言 / 竞品对比）、不采用报告式输出与未支撑量化、须重构为 Skill Contract。
- DEC-027 在此基础上正式定义该 Skill 的**概念层执行契约**（业务目标 / 职责 / 两种运行模式 / 主题与洞察边界 / 证据类型 / Evidence Coverage / Insight 类型与概念 / 用户原声规则 / 频率统计边界 / 正反向证据 / 冲突需求 / Facts 与 Insights 边界 / 输出 / 阶段决策 / Validator 18 项 / 职责边界 / 优先级 / 评价指标 / 测试场景）。
- **不推翻** DEC-017 的评估结论与 Adapt 方向；DEC-017 行作为历史记录不修改，本 Amends 关系仅在此处记录。

---

## Notes

- 本决定保持 **Development Status: NOT READY**。
- 当前**不**创建正式评论分析 Prompt / Skill 代码 / LangGraph Node / 评论聚类代码 / Embedding / 评论导入器 / 数据库表 / 前端页面 / 情感分析实现。
- 当前**不**选择模型 / Embedding / 聚类算法 / 情感分析工具 / 数据库 / 评论文件格式 / 最低评论数量 / 频率阈值。
- 当前**不**创建 RFC。
- 在 **Product Positioning Skill Contract** 确认前，**不**创建正式 Positioning Prompt 或代码。
- 概念 Skill Spec 见 [../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)（仅概念，非最终实现）。
- 该 Skill 是 DEC-020 核心链路的第二个 Skill（`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning`），其输出 Customer Insights Version 是下游 Product Positioning 的主要输入之一；Insight 错误会传播至 Positioning 与 Marketing Brief。
