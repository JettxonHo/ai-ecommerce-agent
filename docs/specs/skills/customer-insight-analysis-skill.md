# Customer Insight Analysis Skill — 概念 Specification

> **Status: CONCEPTUAL（概念）**
> 来源决定：[DEC-027 — Customer Insight Analysis Skill 采用证据模式与降级假设模式，并禁止虚构用户原声和检索样本频率外推](../../decisions/dec-027-customer-insight-analysis-skill-contract.md)（Accepted，Skill Contract / Reliability Architecture，2026-07-28）。Amends DEC-017。
> 本文件是 DEC-027 的**概念结构化记录**，**不是最终实现契约**。所有字段名、枚举、Schema、阈值、算法、Prompt、模型均未确认。
> Development Status: **NOT READY**。

---

## §0 来源与范围

本 Specification 把 DEC-027 已确认的 Skill Contract 整理为结构化概念规格。本 Skill 是 DEC-020 核心链路的**第二个 Core Skill**：

```text
Product Intake & Fact Extraction
→ Customer Insight Analysis   (本文件)
→ Product Positioning
→ Human Review Gate
→ Marketing Brief Generation
→ Xiaohongshu Brief Mapping
```

承接 DEC-008（五类 Evidence Class）、DEC-009（阶段级失效）、DEC-014（Hybrid RAG 返回 Candidate Evidence）、DEC-015（Contract-based Skill）、DEC-017（`product-review-analysis` 改造供体，Amended by DEC-027）、DEC-020（MVP Core Skills）、DEC-024（版本化 Domain Objects + Current Truth Pointers）、DEC-025（Source / Source Version / Fragment / Evidence Link + Evidence Package + Source Scope 隔离）、DEC-026（上游 Facts Layer 契约）。

本 Skill 输出 **Customer Insights Version**（版本化 Domain Object），是下游 Product Positioning 的主要输入之一。

---

## §1 Business Goal

将用户证据和相关市场证据转化为可追溯、可解释、可供商品定位使用的用户洞察，同时明确区分真实用户证据、模型推断和待验证假设。

该 Skill **不**追求「生成看起来有深度的洞察」，而是：只生成证据边界明确、来源可追溯、限制可解释，并能被后续定位阶段正确使用的用户洞察或待验证假设。

---

## §2 Responsibilities

- 用户证据覆盖判断（Evidence Coverage Assessment）；
- 主题识别（Theme Detection）；
- 洞察形成（Insight Formation）；
- 反向证据分析（Counter-evidence Analysis）；
- 假设分类（Hypothesis Classification）；
- 证据校验（Evidence Validation）；
- 输出可追溯、可版本化的用户洞察 / 待验证假设 / 用户原声 / 主题 / 证据评估 / 限制说明 / 阶段决策。

---

## §3 Non-responsibilities

该 Skill **不**负责：

- 决定最终商品定位；
- 选择最终目标人群；
- 生成 Marketing Brief；
- 生成小红书文案；
- 直接发布营销内容；
- 使用竞品反馈证明当前商品实际表现；
- 在没有证据时创造用户需求或用户原声。

---

## §4 Inputs

概念上接收：

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

> 承接 DEC-025 Evidence Package：Skill 输入为可复现输入快照（`candidate_fragments[]` / `verified_facts[]` / `dataset_statistics[]` / `known_conflicts[]` / `evidence_limitations[]`）；Skill 输出中的 Fragment ID 必须来自该 Evidence Package 的允许集合，**不**直接读取整个来源数据库 / 检索索引 / 向量库。

---

## §5 Supported Evidence Types

| 证据类型 | 来源举例 | 可支持结论 | 限制 |
|----------|----------|-----------|------|
| **Direct Customer Evidence（第一优先级）** | 当前商品评论 / 用户访谈 / 问卷开放题 / 售后反馈 / 退货原因 / 客服记录 / 用户测试记录 / 用户主动提交的使用反馈 | 当前商品用户体验相关 Insight | 仍须遵守单条反馈不作普遍共识 |
| **Competitor Customer Evidence（第二优先级）** | 竞品评论 / 竞品问答 / 竞品用户讨论 / 竞品售后反馈 / 竞品退货或投诉资料 | 品类共性问题 / 用户期待 / 竞品弱点 / 市场用户语言 / 差异化机会假设 / 待验证用户需求 | **不能**直接证明当前商品用户具有同样体验 |
| **Indirect Business Evidence** | 搜索词 / 商品问答 / 点击或转化数据 / 退货率 / 售后问题分类 / 运营人员记录 / 市场调研材料 | 辅助形成 Insight | 必须明确证据性质和限制 |
| **Non-customer Evidence** | 商品参数 / 说明书 / 认证 / 检测报告 | 帮助解释商品能力和使用场景 | **不**属于用户反馈；**不能**单独证明用户真正需要 / 认可 / 担忧某项内容 |

> 承接 DEC-025 Source Scope：当前商品（current_product）与竞品（competitor_product）证据必须隔离；竞品用户反馈**不得**归因于当前商品用户。

---

## §6 Evidence-backed Mode

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

---

## §7 Degraded Hypothesis Mode

不存在足够直接用户证据时使用。

可以基于：商品事实 / 商品用途 / 合理使用场景 / 品类常见任务 / 竞品用户证据 / 用户提供的目标人群描述，生成：

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

**不得**表达为：

```text
用户最关心防漏
```

无真实用户原文时，**不得**生成带引号的模拟用户语言。

> 默认情况下，MVP 可以在没有用户证据时使用 Degraded Hypothesis Mode 继续运行（除非用户明确要求必须基于评论 / 访谈分析且不接受假设模式 → `waiting_input`）。

---

## §8 Theme and Insight Boundary

必须区分 **Theme** 与 **Insight**。

- **Theme** — 用户反馈中反复出现或具有业务意义的**讨论主题**（漏水 / 保温 / 重量 / 外观 / 清洗 / 价格 / 售后 …）。Theme 只回答「用户在讨论什么？」，本身**不**自动构成业务洞察。
- **Insight** — 至少需要表达「谁 + 在什么场景 + 遇到什么问题或需求 + 为什么重要 + 如何影响使用、购买或信任」。

例如（合格 Insight）：

> 经常将水杯放入通勤包的用户担心杯盖密封性，因为即使少量漏水也可能损坏电脑或文件，从而降低其购买信心。

**不得**将「用户提到了漏水」直接包装成完整用户洞察。

---

## §9 Evidence Coverage

不使用模型主观百分制 Confidence。采用可解释的证据覆盖状态：

| 状态 | 含义 | 可输出结论 |
|------|------|-----------|
| `none` | 没有用户证据 | 只能进入 Degraded Hypothesis Mode |
| `anecdotal` | 只有单条或极少数独立反馈 | 只能表达为 `Observed Signal` / `Anecdotal Signal`，不能表达为稳定模式或普遍共识 |
| `repeated_signal` | 多个独立用户或记录出现相似问题 | 可形成有限范围的 Evidence-backed Insight |
| `dataset_supported` | 基于完整、可计数数据集分析，具备明确样本量、统计方法和记录范围 | Evidence-backed Insight（可引用 Dataset Statistic） |
| `multi_source_corroborated` | 评论、访谈、售后、问卷或其他不同来源相互印证 | 较强的用户证据状态 |

> 单条严重反馈可以输出 `Critical Anecdotal Signal`（低频但高影响），但**不得**被表达为普遍共识。

### No Universal Sample Threshold

MVP **不**设定统一规则「至少 N 条评论才能形成 Insight」。原因：一条严重安全投诉可能高价值；多条重复或机器人评论可能没有独立性；一次深入访谈可能比多条短评包含更多信息；不同证据类型不能只按数量比较。洞察形成须结合：独立记录数量 + 来源类型 + 证据覆盖 + 数据质量 + 反向证据 + 业务严重性。但必须遵守：**单条反馈不能被表达为普遍用户共识**。

---

## §10 Insight Types

MVP 概念上至少支持：

| 类型 | 含义 |
|------|------|
| `pain_point` | 用户实际遇到的问题 |
| `desired_outcome` | 用户希望获得的结果 |
| `functional_need` | 用户希望商品完成的功能任务 |
| `emotional_need` | 安心、轻松、体面、控制感或其他心理需求 |
| `usage_context` | 问题或需求发生的实际场景 |
| `purchase_motivation` | 推动购买的理由 |
| `purchase_barrier` | 阻碍购买的顾虑、成本或限制 |
| `trust_concern` | 用户对安全、质量、认证、真实性或售后的担忧 |
| `product_satisfaction` | 用户对商品的正面反馈 |
| `product_dissatisfaction` | 用户对商品的负面反馈 |
| `unmet_need` | 当前商品或市场没有充分满足的需求 |
| `switching_trigger` | 用户更换商品 / 品牌的触发因素 |
| `customer_language` | 用户的真实表达语言（用于营销文案） |

> 最终类型名称与 Schema 未确认。

---

## §11 Insight Item Concept

概念结构（**非**最终数据库 Schema）：

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

> 承接 DEC-024（版本化 Domain Object + Current Truth Pointer）与 DEC-025（`supporting_fragment_ids[]` / `contradicting_fragment_ids[]` 须经 Evidence Link 关联真实 Fragment；竞品 Fragment 不得归因为当前商品证据）。

---

## §12 Customer Language Rules

用户原声是重要业务输入，但必须严格防止伪造。

### Allowed

直接用户原声**必须**来自真实 Fragment。必须能够追踪：Fragment ID / Source / Source Version / Review·Interview·Survey Record / Locator / 必要上下文。

### Forbidden

模型**不得**：

- 自己写一句话并加引号；
- 将多条评论拼接成虚构用户原声；
- 修改原文后仍声称是直接引用；
- 把模型概括伪装为原文；
- 把竞品评论展示为当前商品用户原声；
- 把翻译文本伪装成原语言直接引用。

### Presentation Boundary

系统可以分别展示 `Original Customer Language` 与 `Model Summary`，两者必须明确区分。

---

## §13 Dataset Statistics Boundary

### Theme Discovery（LLM 可辅助）

LLM 可以辅助：主题识别 / 相似表达归类 / 场景分类 / 正负面判断 / 用户需求归纳。

### Formal Frequency（确定性统计）

正式比例和频率**必须**由确定性统计产生。例如：

```text
120 条有效评论中，18 条提到漏水，占 15%
```

必须至少记录：有效数据集版本 / 评论总数 / 去重规则 / 分子记录 ID / 分母 / 主题分类规则或版本 / 统计时间 / 统计方法。

### Prohibited Frequency Inference

**禁止**根据 RAG Top-K 召回结果计算或推断总体比例。Top-K 表示「与当前 Query 相关的候选证据」，**不**表示「总体样本的随机或完整分布」。

> 承接 DEC-025：须区分 Dataset-derived Statistic（可作正式频率）与 Retrieved Evidence Sample（仅证明现象存在）；禁止以 Top-K 召回结果推断总体频率。

---

## §14 Supporting and Contradicting Evidence

重要 Insight 应尽量检查反向证据。

例如：

```text
Insight：部分用户担心杯盖漏水
Supporting Evidence：12 条评论提到漏水
Contradicting Evidence：8 条评论明确认可密封性
```

最终表达应反映真实证据差异：

> 部分用户报告了漏水问题，但也存在明确认可密封性的反馈，问题可能与使用方式、批次或型号有关。

模型**不得**只选择符合预期的证据并隐藏反向信息。

---

## §15 Conflicting User Needs

不同用户群可能存在相反需求（如「希望杯体更轻」vs「认为轻量降低质感」）。可被表达为 `Conflicting User Needs`，可能说明：用户细分不同 / 使用场景不同 / 价格期待不同 / 型号需求不同。

但系统**不得**在证据不足时凭空创造用户细分。细分解释可以先标记为 `Hypothesis to Validate`。

---

## §16 Facts and Insights Boundary

- **Fact**（来自 DEC-026）：`商品重量为 260 克`
- **Evidence-backed Insight**：`多条通勤用户反馈显示，长时间携带时重量会影响购买选择。`
- **Hypothesis**（无用户反馈时）：`需要长时间携带水杯的用户，可能更加关注商品重量。`

**不得**从商品事实直接推断：`用户一定认为商品很轻`。

> 承接 DEC-008：Fact / Evidence-backed Insight / Model Inference / Hypothesis to Validate / Insufficient Information 五类须明确区分，不得混用。

---

## §17 Outputs

输出分为五个部分：

### 1. Evidence Assessment

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

## §18 Workflow Decisions

| 阶段决策 | 触发条件 |
|----------|----------|
| `valid` | 存在足够真实证据，可以形成一组可追溯用户洞察 |
| `valid_with_limitations` | 可继续进入 Product Positioning，但存在明显限制（当前商品评论较少 / 只有竞品评论 / 只有用户提供的目标人群 / 缺少完整数据集 / 当前运行于 Degraded Hypothesis Mode）。**Product Positioning Skill 必须能够读取并展示这些限制。** |
| `waiting_input` | 用户明确要求必须基于评论或访谈分析，但没提供资料，且不接受假设模式时。默认 MVP 可在没有用户证据时使用 Degraded Hypothesis Mode 继续运行 |
| `paused` | 见 §19 |
| `failed` | 见 §20 |

---

## §19 Pause Conditions

`paused` 适用于（需人工判断或权限处理）：

- 当前商品评论和竞品评论严重混淆；
- 用户数据权限异常；
- 评论属于错误商品；
- 数据中存在大量重复、污染或异常内容；
- 主要用户证据来源被撤回。

---

## §20 Failure Conditions

`failed` 适用于技术故障：

- 评论解析失败；
- 模型多次无法输出合法 Schema；
- 统计服务异常；
- Evidence Validator 内部错误；
- 数据持久化失败。

> 业务证据不足**不得**错误标记为技术失败（`waiting_input` / `paused` 与 `failed` 严格分离）。

---

## §21 Validator

Insight 写入正式 Insights Version 前，至少检查（18 项）：

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

> 承接 DEC-025 确定性 Evidence Validator + DEC-011「未经校验的 LLM 输出不得自动成为已确认业务事实」；硬校验失败**不得**写入正式 Insights Version。

---

## §22 Responsibility Boundary

### Deterministic Logic

数据集计数 / 评论去重 / 样本量 / 百分比 / Source Scope / Fragment ID / 来源权限 / Evidence Link / Schema / Version Dependency / 幂等写入 / 阶段状态 / Current Truth 更新。

### LLM

主题发现 / 用户问题归纳 / 使用场景识别 / 需求和动机分析 / 相似表达聚类 / 正向与反向证据总结 / Insight 表述 / Hypothesis 生成 / 证据限制说明。

### Human

修正错误主题 / 合并或拆分洞察 / 判断业务重要性 / 选择值得进入定位阶段的洞察 / 补充实际业务背景 / 在统一 Human Review Gate（DEC-007）中确认关键洞察。

### Confidence Boundary

MVP **不**使用模型主观百分制 Confidence（如 0.87），改用可解释的 Evidence Coverage（none / anecdotal / repeated_signal / dataset_supported / multi_source_corroborated）。

---

## §23 Prioritization

可输出候选优先级，但**不**使用模型自由生成的单一综合 Confidence 分数。优先级可参考以下可解释维度：

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

## §24 Evaluation Metrics

### Hard Reliability Metrics（MVP 目标）

```text
Invalid Fragment Reference Rate = 0%
Fabricated Customer Quote Rate = 0%
Top-K Frequency Hallucination Rate = 0%
Current-product / Competitor Misattribution Rate = 0%
Unsupported Consensus Claim Rate = 0%
```

### Insight Quality Metrics

Theme Classification Accuracy / Insight Evidence Relevance / Pain Point Extraction Precision / Usage Context Accuracy / Purchase Barrier Recall / Counter-evidence Coverage / Hypothesis Classification Accuracy / Duplicate Insight Rate。

### User Value Metrics

用户接受的洞察比例 / 用户修改洞察的数量 / 用户认为可用于定位的洞察比例 / 从用户资料到可用 Insights 的时间 / Insight 对最终 Positioning 的实际使用率。

> 模型自报 Confidence **不**作为核心评价指标。

---

## §25 Test Scenarios（概念测试场景，非最终 Golden Dataset）

| 场景 | 输入 | 预期 |
|------|------|------|
| **TS-1：No Customer Evidence** | 有效商品事实 + 无评论 / 访谈 / 问卷 | Degraded Hypothesis Mode；不生成虚构用户原声；用户需求结论标记为 Hypothesis；阶段 `valid_with_limitations` |
| **TS-2：One Negative Review** | 单条负面评论 | 只能输出 Anecdotal Signal；不表达为普遍问题；严重问题可单独警告 |
| **TS-3：Complete Review Dataset** | 完整可计数评论数据集 | 确定性计算频率；输出样本量；生成 Evidence-backed Insights；保存分子记录 ID 和数据集版本 |
| **TS-4：Competitor Reviews Only** | 仅有竞品评论 | 可生成品类问题和市场假设；不描述为当前商品用户反馈；阶段 `valid_with_limitations` |
| **TS-5：Supporting and Contradicting Evidence** | 同时存在正反向证据 | 同时展示正向和反向证据；不隐瞒证据冲突；用户细分解释在证据不足时标记为 Hypothesis |
| **TS-6：Top-K Retrieved Reviews** | RAG Top-K 召回评论 | 可作为相关证据示例；**不允许**输出总体比例 |

> 以上为**概念测试场景，非最终 Golden Dataset**；最终测试数据、阈值与评价实现未确认。

---

## §26 Open Questions

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
- 具体错误代码；
- Insight Types 最终名称与 Schema；
- Customer Language 最终 Locator Schema；
- Dataset Statistic 最终记录格式；
- Evidence Validator 接口；
- Evidence Package 构建接口；
- Business Repository 接口；
- Node Adapter / Skill Service 接口；
- Human Review Payload；
- Golden Dataset 最终数据与阈值。

---

## §27 Out-of-Scope

当前**不**创建：

- 正式评论分析 Prompt；
- Skill 代码；
- LangGraph Node；
- 评论聚类代码；
- Embedding；
- 评论导入器；
- 数据库表；
- 前端页面；
- 情感分析实现。

当前**不**选择：

- 模型；
- Embedding；
- 聚类算法；
- 情感分析工具；
- 数据库；
- 评论文件格式；
- 最低评论数量；
- 频率阈值。

当前**不**创建 RFC。

保持 **Development Status: NOT READY**。

> 在 **Product Positioning Skill Contract** 确认前，**不**创建正式 Positioning Prompt 或代码。
