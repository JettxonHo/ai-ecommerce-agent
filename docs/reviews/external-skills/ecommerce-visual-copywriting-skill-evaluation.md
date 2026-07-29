# External Skill Evaluation — ecommerce-visual-copywriting-skill

> 本文件是 **Candidate 3（`feichanggege/ecommerce-visual-copywriting-skill`）** 的正式评估记录。
> 来源：[DEC-016 — 优先研究成熟电商 Skills，并通过契约化改造后复用](../../decisions/dec-016-external-skill-research-and-contract-based-adaptation.md)（Accepted，Agent，2026-07-27）。
> 评估结论已由用户接受：[DEC-019 — Ecommerce Visual Copywriting Skill 作为执行层 Brief 能力的改造供体](../../decisions/dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)（Accepted，Agent，2026-07-27，用户回复「确认」）。
>
> **重要：**
> - **Reuse Recommendation: Adapt**（已由用户接受，DEC-019）。该候选对**三个**目标 Skill 的复用粒度不同：Visual Execution Brief Skill（主目标，Adapt）、Marketing Brief Generation Skill（次目标，Partial Adapt）、Xiaohongshu Brief Mapping Skill（平台目标，Reference + 部分改造）。
> - 该候选**不**作为项目核心 Skill 安装或复制使用，而是作为上述能力的**外部业务与流程供体**。
> - **Adapt 不等于已实现**，也**不**代表 Visual Execution Brief Skill / Xiaohongshu Brief Mapping Skill 进入 MVP（均未决）。
> - 本文件**未**复制任何第三方 SKILL.md / 合规规则库 / 示例 / 测试 Prompt / 验证脚本 / 视觉资产 / 模板 / Prompt（仅记录研究方向与改造要求）。
> - **License 为 MIT**（已由用户在 DEC-019 Attribution 中确认）；其余原始仓库未确认的字段（访问日期 / commit、精确输入字段契约等）如实标注为未确认 / 待研究，未作编造。

---

## Repository and Skill

- 仓库：`feichanggege/ecommerce-visual-copywriting-skill`
- Skill：`ecommerce-visual-copywriting`
- 访问日期 / commit / 版本：**未在本评估中记录**（待后续实际审计时补充）。

## License

- **License 类型：MIT**（已由用户在 [DEC-019](../../decisions/dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md) Attribution 中确认）。
- Attribution Principle（DEC-016 / DEC-019）：后续实际复制或修改原仓库中的 `SKILL.md`、合规规则、示例、验证脚本、测试 Prompt、输出模板、Storyboard 方法、文案约束时，必须——保留 MIT License 要求的版权和许可信息；在项目 README 或相关 Skill 文档中标注来源；说明修改范围；区分第三方内容和项目原创内容；**不得将其包装为完全原创**。
- 当前只确认 **Adapt 方向**，**不执行复制**。

## Original Business Goal

- 原始 Skill 面向**电商内容运营和视觉执行场景**，提供从商品资料到视觉产出物的完整执行 SOP（含策划先行、Storyboard、人工确认、主图 / 详情页文案、设计说明、生图 Prompt）。
- 其原始主链路为：

  ```
  商品资料 → 视觉策划 → Storyboard → 用户确认 → 主图与详情页文案 → 设计说明 → 生图 Prompt
  ```

- 与本项目当前主链路（商品事实 → 用户洞察 → 商品定位 → 人工审核 → 营销 Brief）**部分重叠但不相同**：Candidate 3 主要服务执行层与视觉层，而本项目 MVP 当前止于营销 Brief。因此其定位是「核心营销 Brief 的部分机制供体 + 视觉执行扩展层的主要供体」。

## Original Target User

- **电商内容运营和视觉执行人员**（已由用户在 DEC-019 Business Fit 中确认：「主要服务电商内容运营和视觉执行场景」）。

## Inputs

- 原始 Skill 的**精确输入字段契约未在本评估中转录**。
- 概念上消费：商品资料、品牌 / 资质约束、平台上下文、风险约束等。其精确字段 / 格式待实际审计时确认。

## Workflow

- 原始主链路（已确认，见 Original Business Goal）：`商品资料 → 视觉策划 → Storyboard → 用户确认 → 主图与详情页文案 → 设计说明 → 生图 Prompt`。
- 该工作流含**两个常规强制审核 Gate**（视觉策划确认 + Storyboard 确认），与项目 DEC-007（单一关键审核节点 + 异常暂停）**冲突**（见 Conflicts）。

## Outputs

- 原始 Skill 倾向输出**完整 Markdown 视觉方案**：主图与详情页文案、设计说明、生图 Prompt、Storyboard 等。
- 原始输出为**自由文本 / 完整文档**，不直接适合作为结构化 Workflow State（见 Conflicts 与 Required Modifications）。

## Reliability Mechanisms

- 原始 Skill 具备若干可靠性方向：信息缺失处理（不编造、只追问关键资料、明确标记假设）、资质 / 证据边界、风险表达识别、`Feature → Advantage → Benefit → Evidence` 方法。
- 但其**质量门依赖 LLM 自评分**（生成内容 → 自己评分），不能充分证明内容质量（见 Conflicts / Required Modifications）。
- 原始 Skill 的来源 / 证据追踪机制、事实与推断区分的成熟度**未在本评估中确认**。

## Human Review Mechanisms

- 原始 Skill 设置**两个常规强制审核 Gate**：视觉策划确认 + Storyboard 确认。
- 与项目 DEC-007（**一个**常规强制人工审核节点 + 异常暂停）冲突；不直接采用两个 Gate。未来视觉执行阶段可增加**可选** Storyboard Review，但需单独经过 Decision Gate（未确认）。

## Compliance Rule Analysis

- 原始 Skill 含静态合规规则，覆盖方向：绝对化用语、数据宣称、认证和资质、功效宣称、医疗化表达、竞品贬低、无依据用户评价、虚构销量、虚构检测报告、虚构专利或批准文号。
- 这些规则应作为 **Risk Rules Candidate（风险规则候选）**，而**不是** Final Legal or Platform Decision。
- 仓库内静态合规规则**不得**自动被视为：当前法律全文、当前平台官方规则、最终合规判断、上架审核保证、法律意见。
- 实际实现需要：`确定性风险规则 + 当前官方规则检索 + LLM 语义风险识别 + 人工审核`。

## Verification Script Analysis

- 原始仓库含验证脚本，主要完成：文件是否存在、必要文本是否存在、是否可能泄漏凭证（Secret Scanning）、仓库结构是否完整。
- 它**并不证明**：模型运行结果正确、风险识别准确、审核节点稳定执行、自评分客观、不同模型和 Prompt 版本下结果一致。
- 是否复用该验证脚本**未确认**（见 Open Questions）。

## Test Prompt Analysis

- 原始仓库含 Test Prompts 与 Expected Behavior / 示例，主要用于静态行为测试。
- 项目后续需要在此基础上**增加真正的运行评测**，不能只进行字符串存在性检查。

## Engineering Evaluation

> 本节为对原始仓库工程完整度的定性结论（来自 DEC-019）。

Candidate 3 的工程完整度高于普通 Prompt Skill。它包含：核心 Skill、中英文版本、规则库、Examples、Test Prompts、Verification Script、展示资产、Marketplace Metadata。

但目前验证脚本主要完成文件 / 文本存在性、凭证泄漏、仓库结构检查，并不证明运行结果正确性、风险识别准确性、审核稳定性、自评分客观性、跨模型 / Prompt 一致性。因此评定为：

```
Documentation and Packaging Quality: High
Runtime Evaluation Maturity:          Medium-Low
```

## Strengths

- 成熟的电商执行 SOP、Human-in-the-loop、风险边界、测试样例和工程验证结构，可显著降低执行层 Skill 从零设计的成本。
- 文档与打包质量高（含中英文、规则库、示例、验证脚本、Marketplace 元数据）。
- 信息缺失处理、证据边界、策略先行、风险检查方向覆盖较全。

## Conflicts with Current Decisions

- **两个常规强制审核 Gate** 与 DEC-007（单一关键审核节点 + 异常暂停）冲突 → 不采用两个 Gate。
- **静态合规规则作为最终事实** 与 DEC-008（分级证据）/ DEC-011（受约束 LLM）冲突 → 仅作风险规则候选，须叠加官方规则检索 + LLM 语义识别 + 人工审核。
- **LLM 自评分为唯一质量门** 与可靠性原则冲突 → 须结合 Schema 校验 / 来源校验 / 确定性风险规则 / 人工验收 / 测试案例 / 可选独立 Judge。
- **自由文本 / 完整 Markdown 作为正式状态** 与 DEC-012（结构化 Workflow State）冲突 → 须拆分为结构化条目。
- **完整视觉生产范围**（五张主图 / 完整详情页 / 图内文案 / 设计稿 / 生图 Prompt / 自动生图 / 自动上架 / 自动发布）超出当前核心 MVP。
- **淘宝详情页结构 ≠ 小红书内容结构** → 平台映射须重新适配。

## Reusable Components

改造时优先保留以下方法（作为**机制 / 流程供体**，非直接复制实现）：

- **Information-gap Handling**：缺失信息不得编造；只追问影响关键方向的资料；当前假设明确标记；资质文件不存在不得生成对应宣称；无依据数据不得进入最终执行内容。接入项目已有的 `missing_information` / `assumptions_to_validate` / `pause_reason` / `source_refs` / 人工审核状态。
- **Feature-to-Benefit Translation**：`Feature → Advantage → Customer Benefit → Evidence`；改造后须区分商品明确事实 / 用户洞察 / 模型推断 / 待验证表达 / 证据不足；不得因 Benefit 营销合理就写成有证据结论。
- **Strategy-before-execution Principle**：方向、卖点、表达边界未确认前不进入高成本执行内容生成；映射为「事实 / 洞察 / 定位 / 卖点优先级 → 统一人工审核 → Marketing Brief Generation」。
- **Execution Brief Structure**：核心传播任务、目标用户、使用场景、主要卖点、证据表达、内容叙事、风险边界、免责声明、设计执行说明 —— 改造成结构化 Workflow State，而非单份 Markdown。
- **Storyboard Method**：可作为未来视觉执行扩展（主图 / 详情页 / 图片卡片 / 小红书图文 / 视频分镜 / 生成式视觉 Prompt）；**当前不是核心 MVP 必填输出**。
- **Compliance and Risk Review（方向）**：绝对化用语 / 数据宣称 / 认证资质 / 功效宣称 / 医疗化表达 / 竞品贬低 / 无依据评价 / 虚构销量 / 虚构检测报告 / 虚构专利或批准文号 —— 作为 Risk Rules Candidate。
- **Skill Verification Pattern（工程方法）**：必要文件 / 章节检查、示例存在性、Test Prompt、Expected Behavior、Secret Scanning、中英文一致性、发布前验证脚本 —— 须增加真正运行评测。

## Required Modifications

**不直接采用：**

- **Full Visual-production Scope**：五张商品主图、完整详情页、图内最终文案、设计师执行稿、图像生成 Prompt、自动生图、自动上架、自动发布 —— 不自动进入首个 MVP。
- **Two Mandatory Review Gates**：视觉策划确认 + Storyboard 确认不直接采用；MVP 保留「一个常规强制人工审核节点 + 异常暂停」（DEC-007）；未来可选 Storyboard Review 需单独 Decision Gate。
- **Static Rules as Final Compliance Truth**：静态规则不得自动作为法律 / 平台 / 上架 / 合规最终判断。
- **LLM Self-score as Sole Quality Gate**：自评分仅作检查清单参考，不作唯一验收。
- **Free-text Output as Formal State**：完整 Markdown 方案不能成为唯一 Workflow State；须拆分为结构化条目。

**必须增加（重构为 Skill Contract，DEC-015；详见 [DEC-019](../../decisions/dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md) 的 Target Skill Mapping / Candidate Inputs / Outputs）：**

- 结构化输入输出（概念输入 / 概念输出见 DEC-019，但**非最终 Schema**）。
- 证据要求：只使用当前有效事实 / 洞察 / 定位；卖点须关联事实或洞察；数据宣称须关联真实来源；认证宣称须存在对应资料；无依据用户评价不得生成；模型不得虚构销量 / 检测报告 / 资质；风险表达进入 Warning 或 Review State；失效上游结果不得进入执行 Brief。
- 校验、失败与暂停条件、人工审核、测试方向（详见 DEC-019 Validation Requirements / Failure and Pause Conditions / Testing Direction）。
- 工作流位置：核心 MVP 概念流程 `Product Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review → Marketing Brief Generation`；未来扩展流程 `Marketing Brief → Platform Mapping → Visual Execution Brief → Optional Storyboard Review → Visual or Content Production`（第二段流程**尚未确认进入 MVP**）。
- 增加真正的运行评测（不能只做字符串存在性检查）。

## Reuse Recommendation

**Adapt**（已由用户接受，DEC-019，回复「确认」）。按目标 Skill 的复用粒度：

- **Visual Execution Brief Skill（主目标）：Adapt** —— 主要供体；MVP 是否纳入**未决**。
- **Marketing Brief Generation Skill（次目标）：Partial Adapt** —— 吸收 Feature-to-Benefit、证据边界、风险表达、缺失信息、执行前检查、内容角度、使用场景、禁止表达、免责声明等机制；不应在当前阶段直接生成完整视觉方案。
- **Xiaohongshu Brief Mapping Skill（平台目标）：Reference + 部分改造** —— 参考封面视觉任务 / 场景代入 / 用户语言 / 单一核心卖点 / 证据可视化 / Storyboard / 图片卡片叙事；必须重新适配小红书笔记结构 / 封面标题 / 图片卡片 / 种草逻辑 / 内容节奏 / 平台规范 / 用户互动方式；MVP 是否纳入**未决**。

## Estimated Adaptation Effort

- **未量化。** 改造工作量（人天 / 排期）未在本评估中估算，属后续规格设计范畴。
- 定性判断：属**中高改造**——须大幅裁剪超 MVP 的视觉生产范围、把双 Gate 收敛为单 Gate、把静态规则降级为风险候选、把自由文本重构为结构化状态、补充运行评测。

## Risks

- **范围蔓延**：完整视觉生产范围明显超过当前核心 MVP，若不裁剪会拖累 MVP。
- **静态规则时效风险**：合规规则可能过期或与当前官方资料冲突，作为最终事实会误导。
- **自评分偏差**：同模型生成 → 自评分不能充分证明质量。
- **平台错配**：淘宝详情页结构不能直接作为小红书 Brief。
- **双 Gate 复杂度**：两个常规 Gate 与 DEC-007 单 Gate 架构冲突。
- **License / 归属**：MIT 允许复用但须保留版权声明与来源标注；不得包装为原创。
- **来源伪造 / 资质虚构**：执行层场景易生成不存在的资质编号 / 检测报告，须强校验。

## Related MVP Skill

- **Primary Target：Visual Execution Brief Skill**（未来执行层 Skill；**MVP 是否纳入未决**）。
- **Secondary Target：Marketing Brief Generation Skill**（DEC-015 候选 MVP Skill 之一；吸收部分机制）。
- **Platform Target：Xiaohongshu Brief Mapping Skill**（DEC-015 候选 MVP Skill 之一；作流程参考 + 部分改造；**首批是否纳入未决**）。
- **均为候选关联，不代表已进入 MVP**；最终名称 / Schema / 实现均**未确认**（见 DEC-019 Decision Boundary）。

## Open Questions

- Visual Execution Brief Skill 是否进入首个 MVP？（未确认）
- Xiaohongshu Brief Mapping Skill 是否进入首批 Skills？（未确认）
- Storyboard 是否进入 MVP？（未确认）
- 是否创建独立 Compliance Review Skill？（未确认）
- 是否复用原仓库验证脚本？是否复制合规规则？（未确认）
- 官方规则检索方式？（未确认）
- 访问日期 / commit / 版本？（待补充）
- 原始仓库精确输入字段契约？（待实际审计）
- 最终各 Skill Schema、Prompt、模型、视觉生成工具？（均未确认）

---

## 评估维度参考（来自 DEC-016，覆盖情况）

| 维度 | 本评估覆盖位置 |
|------|----------------|
| 1. Business Fit | Strengths / Conflicts / Required Modifications（范围裁剪） |
| 2. Input Fit | Inputs / Required Modifications（证据要求、前置条件） |
| 3. Output Fit | Outputs / Required Modifications（结构化拆分、候选化） |
| 4. Evidence and Reliability | Reliability Mechanisms / Compliance Rule Analysis / Required Modifications |
| 5. Human-in-the-loop | Human Review Mechanisms / Required Modifications（单 Gate） |
| 6. Contract Completeness | Required Modifications（Skill Contract 八项） |
| 7. Engineering Quality | Verification Script Analysis / Test Prompt Analysis / Engineering Evaluation / Risks |
| 8. Legal and Attribution | License（MIT）/ Risks |
