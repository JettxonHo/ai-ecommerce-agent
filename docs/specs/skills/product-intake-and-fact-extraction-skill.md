# Product Intake & Fact Extraction Skill — 概念 Skill Specification

> **Status: CONCEPTUAL — 首个核心业务 Skill Contract 已由 DEC-026 确认（概念层），产品门禁、默认文件限制与冲突分级已由 DEC-045 确认；最终 Fact Schema / 公共字段 / Python 类型 / Prompt / 代码 / Parser / 单位库 / 前端表单尚未确认。**
> 本文件是 Current Truth Layer 的一部分，记录**概念层 Skill Contract**。其内容只能来自用户明确接受的 Decision（[DEC-026](../../decisions/dec-026-product-intake-and-fact-extraction-skill-contract.md)）。
> 所有结构名 / 字段名 / 枚举值均为**概念示意，非最终数据契约 / 最终实现**。

---

## 0. 来源与范围

- 来源决定：[DEC-026 — Product Intake & Fact Extraction Skill 采用分层输入完整度、零无来源事实与冲突暂停契约](../../decisions/dec-026-product-intake-and-fact-extraction-skill-contract.md)（Accepted，Skill Contract / Reliability Architecture，2026-07-28）。Amends [DEC-005](../../decisions/dec-005-layered-mvp-inputs.md)。
- 产品门禁：[DEC-045](../../decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md)（Accepted，2026-08-06）将本规格的 Minimum Runnable Input 明确为 Fact Stage 门禁，并冻结默认文件限制与阻断 / 非阻断冲突行为；不改变 DEC-026 的最低事实条件。
- 承接：[DEC-005](../../decisions/dec-005-layered-mvp-inputs.md)（分层输入）、[DEC-008](../../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md)（五类 Evidence Class）、[DEC-009](../../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md)（阶段级失效）、[DEC-015](../../decisions/dec-015-contract-based-reusable-business-skills.md)（Skill 契约）、[DEC-020](../../decisions/dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（MVP 四 Core Skills）、[DEC-024](../../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)（版本化 Domain State）、[DEC-025](../../decisions/dec-025-versioned-sources-fragments-and-evidence-links.md)（来源与证据架构）。
- 本规格**仅记录概念层 Skill Contract**；与本 Skill 相关的 Evidence / Fragment / Evidence Link / Source Version 等概念定义以 [DEC-025 概念规格](../evidence/source-and-evidence-specification.md) 与 [DEC-024 工作流状态规格](../workflow/workflow-state-specification.md) 为准。

---

## 1. Business Goal（业务目标）

判断当前输入是否达到最低可运行条件，并将当前商品资料转换为**可追溯、可校验、可版本化**的商品事实候选。

该 Skill 合并 `Product Input Assessment` + `Product Fact Extraction`，是 MVP 的第一个核心业务 Skill（DEC-020 链路 `Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation → Xiaohongshu Brief Mapping` 的起点）。

首要目标**不是**「尽可能多地生成事实」，而是：只生成有真实来源、可解释、可验证的商品事实，并在无法确认时明确暂停或输出资料不足。

---

## 2. Responsibilities（职责）

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

## 3. Non-responsibilities（不负责）

- 用户需求分析；
- 用户洞察生成；
- 商品定位；
- 竞品差异化；
- 营销 Brief；
- 小红书内容映射；
- 完整风险或法律审核。

---

## 4. Minimum Runnable Input（最低可运行输入）

一个任务要完成 Fact Stage，至少需要满足以下五项条件。

Task 创建在此之前完成：名称 / 临时名称、品类和推广目标用于创建稳定 Task；价格与商家当前卖点不是全局硬必填。用户在结构化表单中的手动输入可以构成下述 current-product Source，不强制上传文件（DEC-045）。

### 4.1 Product Identity

至少提供：

- 商品名称或临时工作名称；
- 商品品类。

### 4.2 Core Purpose

需要存在商品主要用途的明确描述。用途可以来自：

- 用户手动输入；
- 当前商品说明；
- 当前商品参数资料。

### 4.3 At Least One Current-product Source

必须至少存在一个 `source_scope = current_product` 且对应 Source Version 状态可用的来源。可接受来源包括：

- 用户手动输入；
- 商品参数表；
- 商品说明书；
- 当前商品页面快照；
- 检测报告；
- 当前商品结构化资料。

竞品资料**不能**替代当前商品来源（承接 DEC-025 当前商品与竞品隔离）。

### 4.4 At Least One Core Product Attribute

除商品名称与品类外，至少需要一个有直接来源支持的核心属性，例如：

- 材质；
- 容量；
- 尺寸；
- 重量；
- 组成；
- 功能；
- 兼容范围；
- 使用方式。

### 4.5 No Blocking Identity Conflict

不能存在尚未解决的阻断性身份冲突（不同容量 / 不同型号 / 不同 SKU / 不同产品版本 / 当前商品与竞品资料混淆）。若无法确认资料是否属于同一商品或同一 SKU，工作流**不得**静默继续。

---

## 5. Enhanced Input（增强输入）

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

## 6. Input Completeness Levels（输入完整度四档）

输入完整度采用四档，而**不是**模型生成的百分制分数。

| Level | 含义 | 阶段决策 |
|-------|------|----------|
| `insufficient` | 不能形成最低商品事实画像（只有商品名称 / 没有当前商品来源 / 所有文件解析失败 / 商品身份无法确定 / 存在阻断性冲突） | `waiting_input` 或 `paused` |
| `minimal` | 达到最低可运行条件，但资料明显有限；系统可继续运行，但**必须**输出 `missing_information` / `evidence_limitations` / `hypotheses_to_validate` / 对后续结论限制的明确说明 | `valid`（带限制） |
| `standard` | 包含主要商品信息（核心规格 / 材料或组成 / 主要功能 / 使用场景 / 包装内容 / 使用限制 / 基础证明资料）；足以支持正常的 Customer Insight 与 Product Positioning 候选生成 | `valid` |
| `evidence_rich` | 除 Standard 信息外还包含检测报告 / 认证或资质 / 多来源相互印证 / 完整参数表 / 使用说明 / 可验证性能证明。**只代表证据更丰富，不代表所有商品声明自动成为已验证事实** | `valid` |

---

## 7. Fact Categories（事实分类方向）

MVP 概念上至少覆盖以下 14 类（最终分类名称和 Schema **尚未确认**）：

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

### Time-sensitive Facts

价格、促销、库存和其他会快速变化的内容可以被提取，但**必须**记录 `observed_at` / `source_version_id` / `time_sensitive = true`。系统**不得**将旧页面或旧资料中的时间敏感内容长期显示为当前事实。

---

## 8. Fact Item Concept（事实条目概念结构）

每个事实候选概念上至少包括（**非**最终数据库 Schema）：

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

> `raw_value` 与 `normalized_value` **必须分离保存**（见 §11）；`supporting_fragment_ids[]` / `contradicting_fragment_ids[]` 通过 Evidence Link 关联 Fragment（承接 DEC-025）。

---

## 9. Assertion Types（声明分类，5 类）

来源中的表达必须区分为以下类型。

| Assertion Type | 含义 | 能否进入正式 Facts Current Truth |
|----------------|------|----------------------------------|
| `direct_fact` | 来源直接明确表达、可以直接读取的事实（如 `容量：500 mL` / `材质：304 不锈钢`） | 可以（须有 Supporting Fragment） |
| `documented_claim` | 来源明确提出但尚未拥有充分证明材料的商品声明（如 `保温 24 小时` / `完全防漏` / `抑菌率 99%`）；只有营销页面而无检测 / 认证资料时只能归此类 | 作为声明记录，**不得**标记为已验证事实 |
| `certified_or_tested_fact` | 存在有效检测报告、认证或其他可靠证明材料支持的事实；**必须**准确表达证明材料实际支持的范围，**不得**扩张报告结论 | 可以（证明材料范围内） |
| `marketing_expression` | 营销性、主观性或难以直接验证的表达（如 `行业领先` / `高端品质` / `颠覆性设计` / `最佳选择`） | 可作为原始营销素材保存，**不得**进入正式 Facts Current Truth |
| `unknown_or_ambiguous` | 含义不明确、上下文不足或无法确定具体属性的表达 | 标记为不确定，**不得**写成 Fact |

---

## 10. No-inferred-facts Rule（零无来源事实规则）

模型**不得**通过常识、联想或业务推理补充 Explicit Fact。

例如，来源只说明 `304 不锈钢`，模型**不得**自动增加 `一定食品级` / `一定耐腐蚀` / `适用于所有饮品` / `绝对安全`。

### LLM 可以执行

- 非结构化事实抽取；
- 同义字段识别；
- 安全单位标准化；
- 营销表达识别；
- 声明分类；
- 潜在冲突识别；
- 缺失信息说明；
- 标准化候选生成。

### LLM 不得执行

- 猜测材质 / 规格 / 认证 / 功能；
- 将竞品功能写入当前商品；
- 将 Marketing Expression 转换为 Fact；
- 将 documented claim 转换为 verified fact；
- 生成不存在的 Fragment ID。

合理但没有直接来源支持的内容，应进入 `Model Inference` 或 `Hypothesis to Validate`，**不得**进入 Fact Layer（承接 DEC-008 五类 Evidence Class）。

---

## 11. Normalization（标准化规则）

系统允许安全、语义等价的标准化：

```text
0.5 L  /  500 ml  /  500 毫升   →   normalized_value = 500, unit = mL
```

但**必须**保留 `raw_value`。

以下表达**不得**未经确认自动合并（属性语义不同）：

```text
约 500 mL
最大容量 500 mL
推荐容量 450 mL
实际容量 480 mL
```

---

## 12. Deduplication（去重规则）

可以自动合并：

- 完全相同事实；
- 安全单位换算后相同的事实；
- 同一来源中的重复表达；
- 多个有效来源明确表达相同值。

合并后**必须**保留所有 Supporting Fragments；自动合并**不得**删除来源关系。

---

## 13. Conflict Handling（冲突处理）

以下冲突在涉及当前商品身份或形成诚实事实层所需的关键事实时，**不得**由模型自行解决：

| 冲突类型 | 示例 |
|----------|------|
| Numeric Conflict | `450 mL` vs `500 mL` |
| Material Conflict | `304 不锈钢` vs `316 不锈钢` |
| SKU or Variant Conflict | 不同 SKU 或产品版本的参数被错误合并 |
| Certification Conflict | 商品页面声明存在认证，但没有认证文件 / 认证已过期 / 认证对象与当前 SKU 不一致 |
| Usage Restriction Conflict | 商品页面：可放入洗碗机 vs 说明书：不可放入洗碗机 |

阻断性冲突必须创建正式 `SourceConflict`（承接 DEC-025）并触发 `waiting_input` 或 `paused`，向用户展示冲突值、来源、受影响阶段和可执行动作。MVP **不**建立复杂来源优先级，**不让**模型自行判断哪个来源更可信。

不影响商品身份、也不妨碍形成诚实基础事实层的证据差异不阻断 Fact Stage；它们进入 `source_conflicts[]` / `evidence_limitations[]`，并标明受影响结论。该分类按真实业务影响判断，不维护穷举式低概率冲突目录（DEC-039 / DEC-045）。

---

## 14. Outputs（输出五大组）

### 14.1 Intake Assessment

```text
completeness_level
runnable
available_source_types[]
excluded_sources[]
missing_information[]
warnings[]
```

### 14.2 Fact Candidates

```text
facts[]
```

所有候选正式 Fact **必须**关联当前商品范围中的真实 Fragment ID。

### 14.3 Claims Requiring Verification

```text
claims_to_verify[]
```

例如：保温时长 / 防漏性能 / 食品级声明 / 抑菌或健康声明 / 安全认证 / 其他性能承诺。

### 14.4 Conflicts and Limitations

```text
source_conflicts[]
evidence_limitations[]
insufficient_information[]
```

### 14.5 Workflow Stage Decision

```text
stage_decision:  valid | waiting_input | paused | failed
```

---

## 15. Pause Conditions（暂停条件）

### `waiting_input`（等待输入）

用于可以通过用户补充资料解决的业务问题：

- 缺少商品品类；
- 缺少核心用途；
- 没有核心商品属性；
- 关键参数冲突；
- SKU 无法区分；
- 声称有认证但未提供证明资料。

### `paused`（暂停）

用于需要人工判断或权限处理的异常：

- 当前商品与竞品资料混淆；
- 关键来源被撤回；
- 高风险功效声明；
- 来源访问权限异常；
- 用户需要选择哪个来源版本有效。

---

## 16. Failure Conditions（失败条件）

### `failed`（技术失败）

用于系统技术故障：

- Parser 内部异常；
- 数据库存储失败；
- 模型连续无法输出合法 Schema；
- Evidence Validator 内部错误；
- 文件损坏且无法处理。

**业务资料不足不得错误标记为技术失败。**

---

## 17. Validator（确定性 Validator）

LLM 输出写入正式 Facts Version 前，必须至少检查以下 15 项：

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

硬校验失败时，**不得**写入 Facts Current Truth（承接 DEC-025 确定性 Reference Validation + DEC-024 版本化 Domain State）。

---

## 18. Responsibility Boundary（职责边界）

### Deterministic Logic（确定性逻辑）

来源权限 / Source Version 状态 / Schema 校验 / Fragment ID 校验 / 单位安全转换 / 完全重复检测 / 阶段状态 / 幂等写入 / Current Truth 更新 / 冲突状态管理。

### LLM

从非结构化文本中抽取事实候选 / 理解非标准字段语义 / 识别 Marketing Expression / 识别 Documented Claim / 识别潜在冲突 / 提出标准化候选 / 生成缺失信息说明。

### Human

解决关键来源冲突 / 确认当前 SKU / 修正错误事实 / 补充资料 / 处理高风险声明 / 在统一 Human Review Gate 中确认关键 Facts（承接 DEC-007 单审核 Gate）。

### Confidence Boundary（置信度边界）

MVP **不**使用模型主观通用数字置信度（如 `confidence = 0.87`），因为该数值通常未经校准，可能造成虚假精确感。改用可解释的验证状态（概念示例）：

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

## 19. Evaluation Metrics（评价指标）

### 19.1 Hard Reliability Metrics（硬性可靠性指标，MVP 目标）

```text
Fact Traceability Rate = 100%
Invalid Fragment Reference Rate = 0%
Unsupported Numeric Fact Rate = 0%
Competitor Leakage Rate = 0%
Marketing Expression Misclassified as Fact = 0%
```

### 19.2 Quality Metrics（质量指标，通过 Golden Dataset 评估）

Fact Extraction Precision / Fact Extraction Recall / Unit Normalization Accuracy / Claim Classification Accuracy / Conflict Detection Recall / Duplicate Merge Accuracy / Source Scope Classification Accuracy。

### 19.3 User-efficiency Metrics（用户效率指标）

用户修改 Fact 的数量 / 用户补充资料的次数 / 从输入提交到可用 Facts 的时间 / Human Review 中 Facts 的接受率。

模型自报 Confidence **不**作为核心评价指标。

---

## 20. Test Scenarios（概念测试场景，非最终 Golden Dataset）

> 以下为**概念测试场景**，用于说明 Skill Contract 的硬规则；**非**最终 Golden Dataset，最终测试数据 / 阈值 / 评分方式尚未确认。每个场景对应一条已确认规则。

| 场景 | 输入特征 | 期望行为 | 验证的硬规则 |
|------|----------|----------|--------------|
| TS-1 资料不足 | 只有商品名称，无当前商品来源 | `completeness_level = insufficient` → `stage_decision = waiting_input`；不生成 Facts | 最低可运行输入（§4） |
| TS-2 最低可运行 | 名称 + 品类 + 用途 + 1 个 current_product 来源 + 1 个核心属性 | `completeness_level = minimal`；可继续但输出 `missing_information` / `evidence_limitations` / `hypotheses_to_validate` | 最低可运行输入 + minimal 输出（§4 / §6） |
| TS-3 无来源事实拒绝 | LLM 试图基于 `304 不锈钢` 推断「食品级 / 耐腐蚀」 | 推断内容进入 `Model Inference` / `Hypothesis to Validate`，**不**进入 Fact Layer | No-inferred-facts Rule（§10） |
| TS-4 营销表达分类 | 来源含「行业领先 / 最佳选择」 | 归为 `marketing_expression`，保存为原始素材，**不**进入 Facts Current Truth | Assertion Types（§9）+ Validator #10 |
| TS-5 声明需验证 | 营销页面声明「保温 24 小时」但无检测报告 | 归为 `documented_claim` + 写入 `claims_to_verify[]`，**不**标为 certified | Assertion Types（§9）+ Validator #11 |
| TS-6 检测报告支持 | 有检测报告支持的保温时长 | 归为 `certified_or_tested_fact`，仅表达报告实际支持范围，**不**扩张结论 | Assertion Types（§9） |
| TS-7 数值冲突 | 两个来源给出 `450 mL` vs `500 mL` | 创建 `SourceConflict` → `waiting_input`，模型**不**自选值 | Conflict Handling（§13） |
| TS-8 身份冲突 | 不同 SKU 参数被错误合并 | 阻断性身份冲突 → `paused`，交用户处理 | Minimum Runnable Input §4.5 + Pause（§15） |
| TS-9 竞品泄漏拒绝 | LLM 试图用竞品来源证明当前商品属性 | Validator 拒绝；竞品来源登记为后续阶段可用，**不**证明当前商品 | Validator #6 + Enhanced Input（§5） |
| TS-10 标准化保留原值 | `0.5 L` / `500 ml` 标准化为 `500 mL`，保留 `raw_value` | `normalized_value = 500`，`raw_value` 保留 | Normalization（§11）+ Validator #9 |
| TS-11 语义不同不合并 | `最大容量 500 mL` vs `推荐容量 450 mL` | **不**自动合并（属性语义不同） | Normalization（§11） |
| TS-12 时间敏感事实 | 价格 / 促销 | 提取但记录 `observed_at` / `source_version_id` / `time_sensitive = true` | Time-sensitive Facts（§7） |
| TS-13 技术失败 vs 业务不足 | Parser 内部异常 vs 资料不足 | Parser 异常 → `failed`；资料不足 → `waiting_input`（**不**误标为 failed） | Pause / Failure Boundary（§15 / §16） |
| TS-14 幻觉 Fragment 拒绝 | LLM 输出不存在的 Fragment ID | Validator #15 拒绝写入 Facts Current Truth | Validator #2 / #15 + DEC-025 防幻觉 |
| TS-15 非阻断证据差异 | 两个来源在不影响商品身份或基础事实层的辅助描述上不同 | Fact Stage 继续；差异进入 `source_conflicts[]` / `evidence_limitations[]` 并标明受影响结论 | Conflict Handling（§13）+ DEC-045 |

---

## 21. Open Questions（未解决问题）

- 最终 Fact Schema 与字段名称；
- Python 类型（TypedDict / dataclass / Pydantic）；
- 数据库表；
- Prompt；
- 模型（数量 / 是否分模型 / 供应商）；
- 文件格式实现；
- 文本型 PDF Parser；OCR / 图片识别不进入首个 Goal（DEC-041）；
- 单位库（Unit Library）；
- 高风险声明规则；
- 默认文件限制的运行配置与公共错误映射（默认值已由 DEC-045 冻结）；
- 错误代码；
- 最终表单 UI；
- 验证状态（Verification Status）最终枚举名称；
- Fact Categories 最终分类名称；
- Golden Dataset 最终测试数据 / 阈值 / 评分方式；
- Evidence Package / Evidence Validator / Retrieval Service 构建接口（承接 DEC-025）；
- Skill 代码接口 / 注册机制 / 与 LangGraph Node 的最终对应（承接 DEC-015 / 023）。

---

## 22. 明确不包含（Out of Scope）

> 本规格**仅**记录概念层 Skill Contract。以下内容**不属于**本规格，**尚未创建**：

### 22.1 不创建（req-10）

- 正式 Prompt；
- Skill 代码；
- LangGraph Node；
- 数据库表；
- Parser；
- OCR；
- Unit Library（单位库）；
- 前端表单；
- 风险规则实现。

### 22.2 不选择（req-11）

- 模型；
- Parser；
- OCR Provider；
- 数据库；
- ORM；
- 文件格式实现；
- 单位处理库。

### 22.3 其他边界

- **不**创建 RFC（[../../rfcs/](../../rfcs/) 仍仅 README + template）。
- **Development Status: NOT READY。**
- 在 Customer Insight Analysis Skill Contract 确认前，**不**创建正式评论分析 Prompt 或代码。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得为使文档「完整」而补充未经讨论的字段、Schema 或实现。
- 冲突时按 [../../governance/documentation-rules.md](../../governance/documentation-rules.md) 第 6 节优先级裁决。
