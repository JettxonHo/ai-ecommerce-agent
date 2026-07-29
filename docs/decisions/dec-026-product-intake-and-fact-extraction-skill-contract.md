# DEC-026 — Product Intake & Fact Extraction Skill 采用分层输入完整度、零无来源事实与冲突暂停契约

- **Type:** Skill Contract / Reliability Architecture
- **Status:** Accepted
- **Date:** 2026-07-28
- **Related Session:** [../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)（Session-002）
- **Related Specification:** [../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)
- **Related RFC:** None
- **Supersedes:** None
- **Amends:** [DEC-005](dec-005-layered-mvp-inputs.md) by defining the minimum runnable input contract in more detail.

---

## 用户确认

用户对该 Skill Contract Proposal 明确回复「确认」，通过 Decision Gate。

被接受的核心结论是：

> Product Intake & Fact Extraction Skill 合并输入诊断和商品事实提取能力。它负责判断当前商品资料是否足以继续运行，并将可用资料转换为结构化、可追溯、可校验、可版本化的商品事实候选。
>
> 模型不得通过常识或推理创造新的 Explicit Fact。所有进入正式 Facts Version 的事实都必须关联当前商品范围内真实、有效、可定位的 Fragment。
>
> 营销表达、未经验证的商品声明和存在检测或认证支持的事实必须明确区分。关键商品身份、规格、SKU、认证或来源冲突不得由模型自行选择，应暂停并交由用户处理。

---

## Decision

MVP 的第一个核心业务 Skill 正式定义为：

```text
Product Intake & Fact Extraction Skill
```

该 Skill 合并：

```text
Product Input Assessment
+
Product Fact Extraction
```

其业务目标是：判断当前输入是否达到最低可运行条件，并将当前商品资料转换为可追溯、可校验、可版本化的商品事实候选。

该 Skill **不**负责：

- 用户需求分析；
- 用户洞察生成；
- 商品定位；
- 竞品差异化；
- 营销 Brief；
- 小红书内容映射；
- 完整风险或法律审核。

---

## Skill Responsibilities

该 Skill 负责：

- 检查来源是否存在；
- 检查来源权限和可用性；
- 判断商品输入完整度；
- 识别当前商品身份；
- 提取商品事实候选；
- 对字段和单位进行安全标准化；
- 识别重复事实；
- 识别来源冲突；
- 区分事实、声明和营销表达；
- 识别需要验证的商品声明；
- 生成缺失信息清单；
- 生成证据限制；
- 判断当前阶段应继续、暂停、等待输入或失败；
- 生成版本化 Facts 候选；
- 为所有正式 Fact 建立有效证据引用。

概念流程：

```text
Source and Permission Validation
→ Input Completeness Assessment
→ Fact Candidate Extraction
→ Field and Unit Normalization
→ Deduplication
→ Conflict Detection
→ Assertion Classification
→ Evidence Validation
→ Facts Version
```

---

## Minimum Runnable Input

一个任务要完成 Fact Stage，至少需要满足以下条件。

### 1. Product Identity

至少提供：

- 商品名称或临时工作名称；
- 商品品类。

### 2. Core Purpose

需要存在商品主要用途的明确描述。用途可以来自：

- 用户手动输入；
- 当前商品说明；
- 当前商品参数资料。

### 3. At Least One Current-product Source

必须至少存在一个：

```text
source_scope = current_product
```

且对应 Source Version 状态可用。可接受来源包括：

- 用户手动输入；
- 商品参数表；
- 商品说明书；
- 当前商品页面快照；
- 检测报告；
- 当前商品结构化资料。

竞品资料**不能**替代当前商品来源。

### 4. At Least One Core Product Attribute

除商品名称与品类外，至少需要一个有直接来源支持的核心属性，例如：

- 材质；
- 容量；
- 尺寸；
- 重量；
- 组成；
- 功能；
- 兼容范围；
- 使用方式。

### 5. No Blocking Identity Conflict

不能存在尚未解决的阻断性身份冲突，例如：

- 不同容量；
- 不同型号；
- 不同 SKU；
- 不同产品版本；
- 当前商品与竞品资料混淆。

若无法确认资料是否属于同一商品或同一 SKU，工作流**不得**静默继续。

---

## Input Completeness Levels

输入完整度采用四档，而**不是**模型生成的百分制分数。

### `insufficient`

不能形成最低商品事实画像。典型情况：

- 只有商品名称；
- 没有当前商品来源；
- 所有文件解析失败；
- 商品身份无法确定；
- 存在阻断性冲突。

对应阶段决策：

```text
waiting_input
```

或：

```text
paused
```

### `minimal`

达到最低可运行条件，但资料明显有限。系统可以继续运行，但必须输出：

- `missing_information`；
- `evidence_limitations`；
- `hypotheses_to_validate`；
- 对后续结论限制的明确说明。

### `standard`

包含主要商品信息，例如：

- 核心规格；
- 材料或组成；
- 主要功能；
- 使用场景；
- 包装内容；
- 使用限制；
- 基础证明资料。

足以支持正常的 Customer Insight 和 Product Positioning 候选生成。

### `evidence_rich`

除 Standard 信息外，还包含：

- 检测报告；
- 认证或资质；
- 多来源相互印证；
- 完整参数表；
- 使用说明；
- 可验证性能证明。

`evidence_rich` 只代表证据更丰富，**不代表**所有商品声明自动成为已验证事实。

---

## Enhanced Inputs

增强输入**不是** Fact Stage 成功的硬性条件。可以包括：

- 品牌；
- SKU；
- Variant；
- 详细规格；
- 材料与组成；
- 包装清单；
- 使用条件；
- 使用限制；
- 检测报告；
- 认证与资质；
- 保修与售后；
- 当前售价和采集时间；
- 商品图片说明；
- 历史营销资料；
- 当前目标市场；
- 用户评论；
- 竞品资料。

用户评论和竞品资料可以被登记为后续阶段可用来源，但**不能**被用于证明当前商品本身拥有某项属性。

---

## Fact Categories

MVP 概念上至少覆盖：

```text
product_identity
product_category
materials_and_components
dimensions_and_weight
capacity_and_quantity
functions_and_features
performance
compatibility
usage_conditions
included_items
certifications_and_qualifications
warranty_and_service
commercial_terms
restrictions_and_warnings
```

最终分类名称和 Schema **尚未确认**。

---

## Time-sensitive Facts

价格、促销、库存和其他会快速变化的内容，可以被提取，但必须记录：

```text
observed_at
source_version_id
time_sensitive = true
```

系统**不得**将旧页面或旧资料中的时间敏感内容长期显示为当前事实。

---

## Fact Item Concept

每个事实候选概念上至少包括：

```text
FactItem
├── fact_id
├── category
├── attribute_key
├── raw_value
├── normalized_value
├── unit
├── assertion_type
├── verification_status
├── supporting_fragment_ids[]
├── contradicting_fragment_ids[]
├── conflict_id
├── review_status
└── notes
```

以上**不是**最终数据库 Schema。

---

## Assertion Classification

来源中的表达必须区分为以下类型。

### `direct_fact`

来源直接明确表达、可以直接读取的事实。例如：

```text
容量：500 mL
材质：304 不锈钢
```

### `documented_claim`

来源明确提出，但尚未拥有充分证明材料的商品声明。例如：

```text
保温 24 小时
完全防漏
抑菌率 99%
```

如果只存在营销页面，而没有相应检测或认证资料，只能归类为 `documented_claim`。

### `certified_or_tested_fact`

存在有效检测报告、认证或其他可靠证明材料支持的事实。系统必须准确表达证明材料实际支持的范围，**不得**扩张报告结论。

### `marketing_expression`

营销性、主观性或难以直接验证的表达。例如：

```text
行业领先
高端品质
颠覆性设计
最佳选择
```

Marketing Expression 可以作为原始营销素材保存，但**不得**进入正式 Facts Current Truth。

### `unknown_or_ambiguous`

含义不明确、上下文不足或无法确定具体属性的表达。

---

## No Inferred Facts Rule

模型**不得**通过常识、联想或业务推理补充 Explicit Fact。

例如，来源只说明：

```text
304 不锈钢
```

模型**不得**自动增加：

```text
一定食品级
一定耐腐蚀
适用于所有饮品
绝对安全
```

LLM **可以**执行：

- 非结构化事实抽取；
- 同义字段识别；
- 安全单位标准化；
- 营销表达识别；
- 声明分类；
- 潜在冲突识别；
- 缺失信息说明；
- 标准化候选生成。

LLM **不得**执行：

- 猜测材质；
- 猜测规格；
- 猜测认证；
- 猜测功能；
- 将竞品功能写入当前商品；
- 将 Marketing Expression 转换为 Fact；
- 将 documented claim 转换为 verified fact；
- 生成不存在的 Fragment ID。

合理但没有直接来源支持的内容，应进入：

```text
Model Inference
```

或：

```text
Hypothesis to Validate
```

**不得**进入 Fact Layer。

---

## Normalization Rules

系统允许安全、语义等价的标准化，例如：

```text
0.5 L
500 ml
500 毫升
```

可以标准化为：

```text
normalized_value = 500
unit = mL
```

但**必须**保留：

```text
raw_value
```

以下表达**不得**未经确认自动合并：

```text
约 500 mL
最大容量 500 mL
推荐容量 450 mL
实际容量 480 mL
```

因为它们描述的属性语义不同。

---

## Deduplication

可以自动合并：

- 完全相同事实；
- 安全单位换算后相同的事实；
- 同一来源中的重复表达；
- 多个有效来源明确表达相同值。

合并后**必须**保留所有 Supporting Fragments。自动合并**不得**删除来源关系。

---

## Conflict Handling

以下冲突**不得**由模型自行解决：

### Numeric Conflict

```text
450 mL
vs
500 mL
```

### Material Conflict

```text
304 不锈钢
vs
316 不锈钢
```

### SKU or Variant Conflict

不同 SKU 或产品版本的参数被错误合并。

### Certification Conflict

商品页面声明存在认证，但：

- 没有认证文件；
- 认证已过期；
- 认证对象与当前 SKU 不一致。

### Usage Restriction Conflict

例如：

```text
商品页面：可放入洗碗机
说明书：不可放入洗碗机
```

关键冲突必须创建正式：

```text
SourceConflict
```

并触发：

```text
waiting_input
```

或：

```text
paused
```

MVP **不**建立复杂来源优先级，**不让**模型自行判断哪个来源更可信。

---

## Skill Outputs

Skill 输出分为以下五组。

### 1. Intake Assessment

概念输出：

```text
completeness_level
runnable
available_source_types[]
excluded_sources[]
missing_information[]
warnings[]
```

### 2. Fact Candidates

```text
facts[]
```

所有候选正式 Fact **必须**关联当前商品范围中的真实 Fragment ID。

### 3. Claims Requiring Verification

```text
claims_to_verify[]
```

例如：

- 保温时长；
- 防漏性能；
- 食品级声明；
- 抑菌或健康声明；
- 安全认证；
- 其他性能承诺。

### 4. Conflicts and Limitations

```text
source_conflicts[]
evidence_limitations[]
insufficient_information[]
```

### 5. Workflow Stage Decision

```text
stage_decision:
- valid
- waiting_input
- paused
- failed
```

---

## Pause and Failure Boundary

### `waiting_input`

用于可以通过用户补充资料解决的业务问题，例如：

- 缺少商品品类；
- 缺少核心用途；
- 没有核心商品属性；
- 关键参数冲突；
- SKU 无法区分；
- 声称有认证但未提供证明资料。

### `paused`

用于需要人工判断或权限处理的异常，例如：

- 当前商品与竞品资料混淆；
- 关键来源被撤回；
- 高风险功效声明；
- 来源访问权限异常；
- 用户需要选择哪个来源版本有效。

### `failed`

用于系统技术故障，例如：

- Parser 内部异常；
- 数据库存储失败；
- 模型连续无法输出合法 Schema；
- Evidence Validator 内部错误；
- 文件损坏且无法处理。

业务资料不足**不得**错误标记为技术失败。

---

## Deterministic Validator

LLM 输出写入正式 Facts Version 前，必须至少检查：

1. 每个正式 Fact 都有 Supporting Fragment；
2. Fragment ID 真实存在；
3. Fragment 属于当前 `task_id`；
4. 来源 Scope 为 `current_product` 或合法 Manual Input；
5. Source Version 当前可用；
6. 没有使用竞品来源证明当前商品事实；
7. 数值可以在对应来源中定位；
8. 单位转换合法；
9. `raw_value` 与原文一致；
10. Marketing Expression 没有被写成 Fact；
11. Documented Claim 没有被标记为 Certified or Tested Fact；
12. 冲突值没有同时成为 Current Truth；
13. 输出符合 Schema；
14. 必填商品身份信息存在；
15. 不存在虚构 Source、Source Version 或 Fragment ID。

硬校验失败时，**不得**写入 Facts Current Truth。

---

## Responsibility Boundary

### Deterministic Logic

负责：

- 来源权限；
- Source Version 状态；
- Schema 校验；
- Fragment ID 校验；
- 单位安全转换；
- 完全重复检测；
- 阶段状态；
- 幂等写入；
- Current Truth 更新；
- 冲突状态管理。

### LLM

负责：

- 从非结构化文本中抽取事实候选；
- 理解非标准字段语义；
- 识别 Marketing Expression；
- 识别 Documented Claim；
- 识别潜在冲突；
- 提出标准化候选；
- 生成缺失信息说明。

### Human

负责：

- 解决关键来源冲突；
- 确认当前 SKU；
- 修正错误事实；
- 补充资料；
- 处理高风险声明；
- 在统一 Human Review Gate 中确认关键 Facts。

---

## Confidence Boundary

MVP **不**使用模型主观通用数字置信度，例如：

```text
confidence = 0.87
```

因为该数值通常未经校准，可能造成虚假精确感。改用可解释的验证状态，例如：

```text
user_provided
single_source_direct
multi_source_corroborated
documented_claim
verified_by_test_or_certificate
conflicting
insufficient
```

最终状态名称**尚未确认**，但必须表达「为什么可信或为什么不确定」。

---

## Evaluation Metrics

### Hard Reliability Metrics

MVP 目标：

```text
Fact Traceability Rate = 100%
Invalid Fragment Reference Rate = 0%
Unsupported Numeric Fact Rate = 0%
Competitor Leakage Rate = 0%
Marketing Expression Misclassified as Fact = 0%
```

### Quality Metrics

通过 Golden Dataset 评估：

- Fact Extraction Precision；
- Fact Extraction Recall；
- Unit Normalization Accuracy；
- Claim Classification Accuracy；
- Conflict Detection Recall；
- Duplicate Merge Accuracy；
- Source Scope Classification Accuracy。

### User-efficiency Metrics

包括：

- 用户修改 Fact 的数量；
- 用户补充资料的次数；
- 从输入提交到可用 Facts 的时间；
- Human Review 中 Facts 的接受率。

模型自报 Confidence **不**作为核心评价指标。

---

## Skill Contract Summary

```text
Skill:
Product Intake & Fact Extraction

Input:
- Task context
- Current-product source versions
- Optional enhanced sources

Output:
- Intake assessment
- Fact candidates
- Claims requiring verification
- Source conflicts
- Missing information
- Evidence limitations
- Workflow stage decision

Hard Rule:
No formal Fact without a valid current-product Fragment.

Pause Rule:
Critical identity, specification, certification, SKU or source conflicts
must be handled by the user.

Failure Rule:
Technical failures must remain separate from insufficient business input.
```

---

## Reason

Fact Layer 是所有下游结果的基础：

```text
Fact
→ Insight
→ Positioning
→ Marketing Brief
```

如果模型在 Fact Layer 中：

- 猜测参数；
- 混入竞品信息；
- 将营销表达当作事实；
- 虚构来源；
- 忽略来源冲突；

错误会传播至所有下游阶段。因此该 Skill 的首要目标**不是**「尽可能多地生成事实」，而是：只生成有真实来源、可解释、可验证的商品事实，并在无法确认时明确暂停或输出资料不足。

---

## Impact

该决定将影响：

- Fact Domain Model；
- Skill Input / Output；
- Source Parser；
- Evidence Package；
- Validator；
- Human Review；
- Invalidation；
- Customer Insight Skill；
- Product Positioning Skill；
- Golden Dataset；
- 前端输入表单；
- 错误和暂停体验；
- Technical Spike 后的正式业务实现。

---

## Decision Boundary

### 已经确认

- Input Assessment 与 Fact Extraction 合并为一个 Skill；
- 最低可运行输入；
- 四档输入完整度；
- 当前商品来源为必要条件；
- 竞品资料不能证明当前商品事实；
- Fact 分类方向；
- Assertion Classification；
- 模型不得创造 Explicit Fact；
- 原始值与标准化值并存；
- 关键冲突不能自动解决；
- 输出五大组成部分；
- 业务资料不足与技术失败分离；
- 确定性 Validator 是正式写入前的必要 Gate；
- 不使用通用模型数字 Confidence；
- 使用可解释来源与验证状态；
- Fact Traceability 等指标作为硬性质量门槛。

### 尚未确认

- 最终 Fact Schema；
- 最终字段名称；
- Python 类型；
- 数据库表；
- Prompt；
- 模型；
- 文件格式；
- PDF Parser；
- OCR；
- 图片识别；
- 单位库；
- 高风险声明规则；
- 一次上传限制；
- 错误代码；
- 最终表单 UI。

---

## Related Session

- [Session-002：Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)

---

## Related Decisions

- [DEC-005 — MVP 采用最低可运行输入与增强输入分层](dec-005-layered-mvp-inputs.md)
- [DEC-008 — MVP 采用分级证据标记与结论可追溯机制](dec-008-tiered-evidence-and-traceable-conclusions.md)
- [DEC-009 — MVP 采用阶段级依赖失效与局部重跑](dec-009-stage-level-invalidation-and-partial-rerun.md)
- [DEC-015 — Skill 定义为带执行契约的可复用业务能力包](dec-015-contract-based-reusable-business-skills.md)
- [DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)
- [DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](dec-024-versioned-domain-state-and-compact-langgraph-state.md)
- [DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](dec-025-versioned-sources-fragments-and-evidence-links.md)

---

## Related RFC

None。

---

## Supersedes

None。

---

## Amends

[DEC-005](dec-005-layered-mvp-inputs.md) — by defining the minimum runnable input contract in more detail（细化最低可运行输入契约：明确 Product Identity / Core Purpose / 至少一个 current_product Source / 至少一个核心属性 / 无阻断性身份冲突五项条件 + 四档输入完整度）。**不推翻** DEC-005 的输入分层原则。

---

## Notes

- 本决定为**首个核心业务 Skill Contract**（承接 DEC-020 的 Product Intake & Fact Extraction Skill）。
- 概念 Skill Specification 见 [../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)（仅概念，非最终实现）。
- **Development Status: NOT READY。**
- 在 Customer Insight Analysis Skill Contract 确认前，**不**创建正式评论分析 Prompt 或代码；本 Skill 的最终 Prompt / Skill 代码 / LangGraph Node / 数据库表 / Parser / OCR / Unit Library / 前端表单 / 风险规则实现同样**尚未创建**。
- Amends DEC-005（细化最低可运行输入契约）；承接 DEC-005 / 008 / 009 / 015 / 020 / 024 / 025。
