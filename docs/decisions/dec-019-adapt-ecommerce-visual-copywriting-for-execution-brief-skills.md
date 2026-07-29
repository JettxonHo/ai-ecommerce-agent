# DEC-019：Ecommerce Visual Copywriting Skill 作为执行层 Brief 能力的改造供体

> 本决定记录用户已明确接受的 Agent 决定（Candidate 3 评估结论）。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill = 带执行契约的可复用业务能力包）与 [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 优先研究、契约化改造后复用）。
> 对应评估记录：[../reviews/external-skills/ecommerce-visual-copywriting-skill-evaluation.md](../reviews/external-skills/ecommerce-visual-copywriting-skill-evaluation.md)。

## Type

Agent

## Status

Accepted（2026-07-27，用户对 Candidate 3 评估结论明确回复「确认」，通过 Decision Gate）

## Decision

项目正式将外部 Skill `feichanggege/ecommerce-visual-copywriting-skill`（Candidate 3）评定为：

```
Reuse Recommendation: Adapt
```

候选来源：

```
Repository: feichanggege/ecommerce-visual-copywriting-skill
Skill:      ecommerce-visual-copywriting
```

主要目标映射：

```
Visual Execution Brief Skill
```

次要映射：

```
Marketing Brief Generation Skill
Xiaohongshu Brief Mapping Skill
```

该候选**不直接作为项目核心 Skill 安装或复制使用**。项目将研究和改造其中与当前产品方向一致的：

- 信息缺失处理；
- 资质和证据边界；
- Feature → Advantage → Benefit → Evidence 方法；
- 策划先行原则；
- 高成本执行前的人工确认机制；
- 风险表达识别；
- 分阶段输出；
- 执行 Brief 结构；
- Storyboard 方法；
- 视觉叙事方法；
- 示例与预期行为测试；
- Skill 静态验证方法；
- 敏感信息泄漏检查。

> 该结论承接 DEC-016 的「审计 → 裁剪 → 重构为 Skill Contract → 校验 → 接入 Workflow State」流程，改造后的 Skill 须符合 DEC-015 的 Skill Contract。

## Business Fit

该候选主要服务电商内容运营和视觉执行场景。其原始主链路为：

```
商品资料
→ 视觉策划
→ Storyboard
→ 用户确认
→ 主图与详情页文案
→ 设计说明
→ 生图 Prompt
```

而本项目当前主链路为：

```
商品事实
→ 用户洞察
→ 商品定位
→ 人工审核
→ 营销 Brief
```

因此 Candidate 3 与项目的关系是：

```
核心营销 Brief 的部分机制供体
+
视觉执行扩展层的主要供体
```

它**不替代**：Product Fact Extraction Skill、Customer Insight Analysis Skill、Product Positioning Skill、Workflow Controller、Workflow State、Evidence Retrieval。

## Retained Concepts

### 1. Information-gap Handling

保留以下原则：

- 缺失信息不得编造；
- 只追问影响关键方向的资料；
- 当前假设必须明确标记；
- 资质文件不存在时不得生成对应宣称；
- 无依据数据不得进入最终执行内容。

该机制应接入项目已有的：`missing_information`、`assumptions_to_validate`、`pause_reason`、`source_refs`、人工审核状态。

### 2. Feature-to-Benefit Translation

保留：

```
Feature → Advantage → Customer Benefit → Evidence
```

但改造后必须区分：商品明确事实、用户洞察、模型推断、待验证表达、证据不足。

> **不能只因为某个 Benefit 在营销上合理，就将其写成有证据结论。**

### 3. Strategy-before-execution Principle

在方向、卖点和表达边界未确认前，不直接进入高成本执行内容生成。在当前 MVP 中，该原则映射为：

```
事实、洞察、定位和卖点优先级
→ 统一人工审核
→ Marketing Brief Generation
```

### 4. Execution Brief Structure

保留其对真实内容生产有价值的结构思想，例如：核心传播任务、目标用户、使用场景、主要卖点、证据表达、内容叙事、风险边界、免责声明、设计执行说明。

> 但需要改造成**结构化 Workflow State**，而不是仅输出一份 Markdown 文档。

### 5. Storyboard Method

Storyboard 方法可以作为未来视觉执行扩展，用于：电商主图、详情页、图片卡片、小红书图文内容、视频分镜、生成式视觉 Prompt。

> Storyboard 当前**不是**核心 MVP 必填输出。

### 6. Compliance and Risk Review

保留以下风险检查方向：绝对化用语、数据宣称、认证和资质、功效宣称、医疗化表达、竞品贬低、无依据用户评价、虚构销量、虚构检测报告、虚构专利或批准文号。

这些规则应作为：

```
Risk Rules Candidate
```

而不是：

```
Final Legal or Platform Decision
```

### 7. Skill Verification Pattern

保留以下工程方法：必要文件检查、必要章节检查、示例存在性检查、测试 Prompt、Expected Behavior、Secret Scanning、中英文文档一致性检查、发布前验证脚本。

> 项目后续需要在此基础上**增加真正的运行评测**，不能只进行字符串存在性检查。

## Components Not Adopted Directly

### 1. Full Visual-production Scope

以下内容不自动进入首个 MVP：五张商品主图、完整详情页、图内最终文案、设计师执行稿、图像生成 Prompt、自动生图、自动上架、自动发布。

### 2. Two Mandatory Review Gates

原 Skill 的「视觉策划确认 + Storyboard 确认」不直接采用。根据 DEC-007，当前 MVP 仍然保留「一个常规强制人工审核节点 + 异常暂停」。未来视觉执行阶段可以增加可选 Storyboard Review，但需要单独经过 Decision Gate。

### 3. Static Rules as Final Compliance Truth

仓库内静态合规规则不得自动被视为：当前法律全文、当前平台官方规则、最终合规判断、上架审核保证、法律意见。

实际实现需要考虑：

```
确定性风险规则
+
当前官方规则检索
+
LLM 语义风险识别
+
人工审核
```

### 4. LLM Self-score as Sole Quality Gate

原 Skill 的自评分方法可以作为检查清单参考，但**不得成为唯一验收机制**。同一模型「生成内容 → 给自己评分」不能充分证明内容质量。项目需要结合：Schema 校验、来源校验、确定性风险规则、人工验收、测试案例、可选独立 Judge。

### 5. Free-text Output as Formal State

原 Skill 的完整 Markdown 方案不能成为唯一 Workflow State。正式输出需要拆分为结构化条目。

## Target Skill Mapping

### Primary Target：Visual Execution Brief Skill

候选业务目标：将已经确认的营销 Brief 转化为适合视觉设计、图片卡片或内容生产的结构化执行 Brief。可能输出：

```
visual_goal
campaign_style
storyboard_items[]
scene_requirements[]
in_image_copy_requirements[]
design_notes[]
generation_constraints[]
required_disclaimers[]
risk_warnings[]
```

> 该 Skill 是否进入首个 MVP **尚未确认**。

### Secondary Target：Marketing Brief Generation Skill

从 Candidate 3 中吸收：Feature-to-Benefit、证据边界、风险表达、缺失信息、执行前检查、内容角度、使用场景、禁止表达、免责声明要求。

> Marketing Brief Generation Skill **不应在当前阶段直接生成完整视觉方案**。

### Platform Target：Xiaohongshu Brief Mapping Skill

可参考：封面视觉任务、场景代入、用户语言、单一核心卖点、证据可视化、Storyboard、图片卡片叙事。

但必须重新适配：小红书笔记结构、封面标题、图片卡片、种草逻辑、内容节奏、平台规范、用户互动方式。

> 淘宝或详情页结构**不能**直接等同于小红书内容结构。

## Candidate Inputs after Adaptation

> **概念输入，不是最终 Schema。**

```
confirmed_facts[]
confirmed_insights[]
confirmed_positioning
selling_point_priorities[]
promotion_goal
platform_context
brand_constraints
qualification_documents[]
source_refs[]
risk_constraints[]
```

## Candidate Marketing Brief Outputs

> **概念输出，不是最终数据契约。**

```
core_message
target_user
primary_need
purchase_barriers
positioning_statement
selling_points[]
proof_points[]
content_angles[]
usage_scenarios[]
prohibited_claims[]
required_disclaimers[]
missing_information[]
assumptions[]
platform_mapping
```

每个关键卖点应支持：

```
item_id
content
fact_refs
insight_refs
source_refs
evidence_type
risk_status
review_status
```

## Evidence Requirements

改造后的 Skill 必须：

- 只使用当前有效的事实；
- 只使用当前有效的洞察和定位；
- 卖点必须关联事实或洞察；
- 数据宣称必须关联真实来源；
- 认证宣称必须存在对应资料；
- 无依据用户评价不得生成；
- 模型不得虚构销量、检测报告或资质；
- 风险表达必须进入 Warning 或 Review State；
- 失效的上游结果不得进入执行 Brief。

## Workflow Position

核心 MVP 概念流程：

```
Product Fact Extraction
↓
Customer Insight Analysis
↓
Product Positioning
↓
Human Review
↓
Marketing Brief Generation
```

未来扩展流程：

```
Marketing Brief
↓
Platform Mapping
↓
Visual Execution Brief
↓
Optional Storyboard Review
↓
Visual or Content Production
```

> 第二段流程目前**尚未确认进入 MVP**。

## Validation Requirements

正式改造后的相关 Skills 至少需要验证：

- 引用的事实是否存在；
- 引用的洞察是否有效；
- 卖点是否有依据；
- 是否出现无依据量化；
- 是否出现虚构资质；
- 是否出现绝对化表达；
- 是否出现医疗化或功效风险；
- 是否出现竞品贬低；
- 是否遗漏必要免责声明；
- 是否使用了已失效上游内容；
- 输出是否符合 Schema；
- 平台映射是否混用其他平台规则；
- 用户是否已经完成必要审核。

> 具体规则和阈值后续确定。

## Failure and Pause Conditions

可能需要暂停或阻断：关键资质缺失、商品品类无法确认、用户要求高风险功效表达、关键卖点没有任何事实依据、来源引用不存在、上游定位未审核、当前策略层已经失效、规则与当前官方资料发生冲突、LLM 多次生成无效结构、用户要求直接发布但项目没有发布权限、无法判断内容是否属于敏感品类。

## Testing Direction

应至少覆盖：普通消费品、普通食品、保健食品、运动器材、没有资质文件、存在完整检测资料、用户要求夸大效果、用户要求贬低竞品、输入事实和卖点冲突、上游定位失效、卖点无来源、多平台映射、小红书场景、Storyboard 未确认、输出 Schema 失败、静态规则过期或与官方资料冲突、模型生成不存在的资质编号。

## Engineering Evaluation

Candidate 3 的工程完整度高于普通 Prompt Skill。它包含：核心 Skill、中英文版本、规则库、Examples、Test Prompts、Verification Script、展示资产、Marketplace Metadata。

但目前验证脚本主要完成：文件是否存在、必要文本是否存在、是否可能泄漏凭证、仓库结构是否完整。它并不证明：模型运行结果正确、风险识别准确、审核节点稳定执行、自评分客观、不同模型和 Prompt 版本下结果一致。

因此评定为：

```
Documentation and Packaging Quality: High
Runtime Evaluation Maturity:          Medium-Low
```

## Attribution

后续实际复制或修改以下内容时：`SKILL.md`、合规规则、示例、验证脚本、测试 Prompt、输出模板、Storyboard 方法、文案约束——必须：

- 保留 **MIT License** 要求的版权和许可信息；
- 在项目 README 或相关 Skill 文档中标注来源；
- 说明修改范围；
- 区分第三方内容和项目原创内容；
- **不得将其包装为完全原创**。

> 当前只确认 Adapt 方向，**不执行复制**。

## Reason

Candidate 3 具有成熟的电商执行 SOP、Human-in-the-loop、风险边界、测试样例和工程验证结构，能够显著降低执行层 Skill 从零设计的成本。

但其完整能力范围明显超过当前核心 MVP，并且：使用两个常规审核 Gate；主要输出视觉执行内容；缺少项目结构化 Workflow State；静态规则具有时效风险；LLM 自评分不能作为唯一质量门；淘宝详情页结构不能直接作为小红书 Brief。

因此最合理的复用方式是 **Adapt**，而不是 Adopt 或直接复制。

## Impact

该决定将影响：Marketing Brief Generation Skill、Visual Execution Brief Skill、Xiaohongshu Brief Mapping Skill、风险与合规机制、Human-in-the-loop、Skill Evaluation Harness、Workflow State、测试样例、License 和 Attribution、MVP 范围裁剪、后续平台 Adapter 设计。

## Decision Boundary

**本决定已经确认：**

- Candidate 3 的评价为 Adapt；
- 它主要作为 Visual Execution Brief Skill 的供体；
- 它部分支持 Marketing Brief Generation Skill；
- 它可以为 Xiaohongshu Brief Mapping 提供流程参考；
- 保留信息缺失、证据边界、策略先行、风险检查和测试工程方法；
- 不直接采用完整主图与详情页生产流程；
- 不直接采用两个强制审核 Gate；
- 不把静态规则作为最终法律或平台事实；
- 不把 LLM 自评分作为唯一质量判断；
- 不直接复制实现；
- 后续实际复制时必须遵守 License（MIT）与 Attribution。

**本决定尚未确认：**

- Visual Execution Brief 是否进入 MVP；
- Xiaohongshu Brief Mapping 是否进入首批 Skills；
- Storyboard 是否进入 MVP；
- 是否创建独立 Compliance Review Skill；
- 最终 Skill Schema；
- 是否复用验证脚本；
- 是否复制合规规则；
- 官方规则检索方式；
- 具体 Prompt；
- 具体模型；
- 视觉生成工具；
- Multi-Agent；
- 工作流框架；
- GitHub 基底仓库。

> 本决定**不**确认 Visual Execution Brief / 小红书 Mapping 进入 MVP、第二个审核 Gate、Compliance Review Skill、模型供应商、Agent 数量、Multi-Agent、LangGraph、视觉生成工具、工作流基底仓库。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related Review

Candidate 3：`ecommerce-visual-copywriting-skill` —— [../reviews/external-skills/ecommerce-visual-copywriting-skill-evaluation.md](../reviews/external-skills/ecommerce-visual-copywriting-skill-evaluation.md)

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill 契约化定义）与 [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 复用策略）：本决定是 DEC-016 首轮三候选中 **Candidate 3** 的正式评估结论（Candidate 1、2 已分别由 [DEC-017](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)、[DEC-018](dec-018-adapt-product-differentiation-for-positioning-skill.md) 评估为 Adapt）。
- 本候选对**三个**目标 Skill 复用粒度不同：Visual Execution Brief Skill（Adapt，主目标）、Marketing Brief Generation Skill（Partial Adapt，次目标）、Xiaohongshu Brief Mapping Skill（Reference + 部分改造，平台目标）。
- Adapt 不等于已实现；Visual Execution Brief Skill 与 Xiaohongshu Brief Mapping Skill 是否进入 MVP **均未确认**。
- 本决定**不**创建正式 Marketing Brief Generation / Visual Execution Brief / Xiaohongshu Brief Mapping Skill Specification，也**不**复制任何第三方 SKILL.md / 合规规则库 / 示例 / 测试 Prompt / 验证脚本 / 视觉资产 / 模板 / Prompt。
- 文中 Candidate Inputs / Outputs、Target Skill Mapping、Validation Requirements 等均为**概念性改造方向**，非最终数据契约。
- 至此 DEC-016 首轮三候选评估**全部完成**；后续进入「首批 MVP Skill 清单裁剪」（区分 Core MVP Skill / Optional MVP Skill / Platform Adapter / Future Extension / 确定性 Tool / 暂不进入 MVP 的能力）——该议题为下一阶段讨论，**不**由本决定确认。
- 本决定**不**确认 Multi-Agent（Question-008 仍顺延）、Agent 数量、LangGraph、视觉生成工具、工作流基底仓库、模型供应商。
