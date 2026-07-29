# External Skill Evaluation — product-review-analysis

> 本文件是 **Candidate 1（`nexscope-ai/eCommerce-Skills/product-review-analysis`）** 的正式评估记录。
> 来源：[DEC-016 — 优先研究成熟电商 Skills，并通过契约化改造后复用](../../decisions/dec-016-external-skill-research-and-contract-based-adaptation.md)（Accepted，Agent，2026-07-27）。
> 评估结论已由用户接受：[DEC-017 — Product Review Analysis 作为 Customer Insight Skill 的改造供体](../../decisions/dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)（Accepted，Agent，2026-07-27，用户回复「确认」）。
>
> **重要：**
> - **Reuse Recommendation: Adapt**（已由用户接受，DEC-017）。
> - 该候选**不**作为项目正式 Skill 直接使用，而是作为 `Customer Insight Analysis Skill` 的**研究与改造供体**。
> - **Adapt 不等于已实现。** 该候选仍须走完 DEC-016 的「审计 → 裁剪 → 重构为 Skill Contract → 校验 → 接入 Workflow State」流程并形成后续规格，才能落地为正式 Skill。
> - 本文件**未**复制任何第三方 Prompt / SKILL.md / 代码 / 模板 / 测试 / 示例（仅记录研究方向与改造要求）。
> - 凡原始仓库未在本评估中确认的字段（License 类型、原始目标用户、原始精确输入 / 工作流），均**如实标注为未确认 / 待研究**，未作编造。

---

## Repository and Skill

- 仓库：`nexscope-ai/eCommerce-Skills`
- Skill：`product-review-analysis`
- 访问日期 / commit / 版本：**未在本评估中记录**（待后续实际审计时补充）。

## License

- **License 类型未确认。** 本评估未核对该仓库的具体 License。
- 已确认的是 **Attribution Principle（归属原则，DEC-016 / DEC-017）**：若后续实际复制或修改原仓库中的 Prompt、文档、模板、规则、代码、示例，必须根据其 License——保留必要的版权与许可声明；在项目 README 或相关 Skill 文档中标明来源；说明项目进行了哪些修改；区分第三方框架与项目原创契约和实现。
- 当前只确认**研究与改造方向**，**不执行复制**。

## Original Business Goal

- 原始 Skill 偏向**一次性生成完整的产品评论分析报告**（report-first），用于从用户评论中归纳痛点、价值感知、需求、用户语言、竞品对比等。
- 该原始业务目标与项目链路「用户评论与反馈 → 用户需求 / 痛点 / 动机 / 阻碍 → Customer Insights → 商品定位 → 营销 Brief」**有较高匹配度**，但其**完整报告式输出**与项目需求**不直接兼容**。

## Original Target User

- **未在本评估中从原始仓库文档确认。** 按仓库定位（`eCommerce-Skills`）可**推断**为电商商家 / 运营人员；此为推断，非确认（见 Open Questions）。

## Inputs

- 原始 Skill 的**精确输入契约未在本评估中转录**。
- 概念上，该类评论分析 Skill 消费：商品上下文、用户评论（必要时含竞品评论）。其精确字段 / 格式 / 是否假设不存在的数据，待实际审计时确认。

## Workflow

- 原始 Skill 的**精确执行步骤未在本评估中转录**（原仓库主要为报告型指令）。
- 本评估记录的是**目标改造方向**（见 Required Modifications 与 Reusable Components），而非原始工作流。

## Outputs

- 原始 Skill 倾向**完整 Markdown 分析报告**。
- 其覆盖的分析维度（按本评估用于「保留 / 参考」的内容归纳）包括：评论分析维度、用户痛点识别、好评主题与价值感知、功能需求提取、用户语言、购买阻碍、使用场景、竞品评论对比、评论洞察向营销信息的转化思路、报告结构。
- **完整报告式输出不被直接采用**（见 Required Modifications 中的「不直接采用」）。

## Reliability Mechanisms

- 原始 Skill 的可靠性机制**未在本评估中确认**（是否保留来源、是否区分事实与推断、是否编造数据、是否含冲突识别、是否支持资料不足标记）。
- 这正是其**不能直接 Adopt** 的核心原因之一：缺少项目已确认（DEC-008 / DEC-011 / DEC-012 / DEC-015）的结构化证据契约。

## Human Review Mechanisms

- 原始 Skill 的人工审核机制**未在本评估中确认**（是否存在确认 Gate、是否支持暂停、用户能否修改中间结果、修改后能否重生成）。
- 改造后**必须**满足 DEC-007（人工审核 / 异常暂停）与 DEC-009（阶段失效 / 局部重跑）。

## Strengths

- 评论分析维度覆盖较全（痛点、价值感知、需求、语言、竞品对比等）。
- 与项目 Insight Layer 高度相关，可减少从零设计评论分析维度的成本。
- 提供可参考的报告结构与测试场景思路。

## Conflicts with Current Decisions

- **报告式输出** 与 DEC-006（四层结构化输出）/ DEC-012（结构化 Workflow State 条目）冲突 → 须重构为「结构化 insight items + 必要摘要」。
- **缺少来源与证据契约** 与 DEC-008（分级证据标记）/ DEC-012（evidence_type / source_refs）冲突 → 须增加来源关系。
- **缺少校验 / 暂停 / 审核** 与 DEC-007 / DEC-011 / DEC-015 冲突 → 须增加校验、暂停与人工审核。
- **可能含未支撑的量化**（百分比 / 频率 / 评分影响 / 市场规模 / 收入与转化率承诺）与可靠性原则冲突 → 无真实统计时不得输出。
- **含超出 MVP 的运营模块**（产品路线图 / 客服回复 / 持续监控 / 质量管理 / 长期经营 / 完整营销活动）须移除或隔离。

## Reusable Components

改造时优先保留以下分析能力（作为**方法 / 框架供体**，非直接复制实现）：

- **Customer Pain Points**：反复出现的使用问题、用户不满意的原因、影响购买或复购的障碍、用户对质量 / 功能 / 尺寸 / 使用体验 / 价值的负面反馈。
- **Positive Value Perception**：用户持续称赞的特点、用户实际感知到的产品价值、可能形成核心卖点的正向反馈、用户愿意推荐或复购的原因。
- **Customer Needs and Requests**：用户明确提出的功能需求、隐含但反复出现的未满足需求、期望的改进方向、使用场景中的需求缺口。
- **Customer Language**：保留用户描述商品、痛点和价值时的原始表达方式，用于后续商品定位、卖点表达、营销 Brief、平台内容适配。
- **Competitive Review Intelligence**：在用户提供竞品评论时，支持比较用户对不同商品的主要评价、竞品常见弱点、当前商品的相对优势、潜在差异化机会。

> 这些结果改造后仍**只作为 Insight 或 Opportunity Candidate**，不自动成为最终商品定位。

## Required Modifications

**不直接采用：**

- **Report-first Output**：不采用一次性完整报告；重构为「结构化 insight items + 必要摘要视图」，完整 Markdown 报告不能成为唯一正式输出。
- **Unsupported Quantification**：无真实统计或样本计算时不得输出精确百分比、频率、评分影响、市场规模、收入提升预测、转化率提升承诺；仅当程序真实计算并保留样本范围时才输出量化结果。
- **Final Product Positioning**：原 Skill 中可能包含的市场机会、产品定位和营销建议**不能直接成为最终策略**，只作为洞察 / 机会候选 / 定位输入 / 待审核建议；最终定位由 Product Positioning Skill 与人工审核流程处理。
- **Broad Operational Modules**：产品开发路线图、客服回复策略、持续评论监控、生产质量管理计划、长期经营计划、完整营销活动方案——不属本 Skill 的 MVP 核心职责，须从本 Skill 移除或隔离（可作为未来扩展）。

**必须增加（重构为 Skill Contract，DEC-015；详见 [DEC-017](../../decisions/dec-017-adapt-product-review-analysis-for-customer-insight-skill.md) 的 Target Skill Contract Direction）：**

- 结构化输入输出（概念输入 / 概念输出见 DEC-017，但**非最终 Schema**）。
- 来源与证据关系：每个有证据洞察条目须关联真实 `source_ref`、可定位到评论 / 访谈 / 竞品片段；不得引用未读取内容、不得伪造评论、不得把模型常识包装成用户反馈、不得因语义合理就自动标记为事实。
- 分析分类：区分 Evidence-backed Insight / Model Inference / Hypothesis to Validate / Insufficient Information；不得把所有结果统一写成确定结论。
- 校验规则：有证据洞察须有真实来源；`source_ref` 须属于当前任务；无证据内容不得标记为明确事实；洞察不能直接覆盖商品事实；输出须符合结构化 Schema；当前事实阶段失效时不得继续分析；量化结论须来自真实统计；输入样本过少时标记局限；评论来源不明时不得声称代表整体用户；竞品评论不得错误归属到当前商品。
- 失败与暂停条件：无评论却要求评论洞察、来源不可识别、评论严重重复或疑似污染、商品与竞品评论混淆、关键来源不可读、LLM 多次无法返回有效结构、出现不存在的来源引用、资料严重冲突、当前事实层已失效。
- 人工审核：接受 / 修改 / 否定洞察、确认待验证假设、补充资料、触发下游失效与局部重跑。
- 测试方向：正常评论集合 / 少量评论 / 没有评论 / 全部正面 / 全部负面 / 中英文混合 / 当前商品与竞品评论混合 / 重复评论 / 来源缺失 / 评论与商品事实冲突 / 模型生成不存在的引用 / 用户修改事实后重新分析 / RAG 未召回足够证据 / 输出 Schema 失败。
- 工作流位置：位于「资料处理 → 商品事实候选 → Customer Insight Analysis Skill → Product Positioning Skill → Human Review → Marketing Brief Generation」；具体节点顺序与调用次数**未确认**；本 Skill 不拥有完整工作流控制权。

## Reuse Recommendation

**Adapt**（已由用户接受，DEC-017，回复「确认」）。

- 保留评论分析方法和部分输出框架；
- 重构为项目 Skill Contract；
- 增加结构化输出、来源证据关系、校验 / 暂停 / 测试；
- 不直接采用完整报告式输出；
- 不直接生成最终商品定位；
- 不直接复制实现。

## Estimated Adaptation Effort

- **未量化。** 改造工作量（人天 / 排期）未在本评估中估算，属后续规格设计范畴。
- 定性判断：属**中高改造**——须重构输出形态、新增证据 / 校验 / 暂停 / 测试、剥离超 MVP 模块。

## Risks

- 原始 Skill 为报告型纯文本指令，缺少项目已确认的结构化 Workflow State / 来源证据契约 / 五类结果标记 / 人工审核 / 阶段失效 / 局部重跑 / 任务级持久化 / 确定性校验 → 直接使用会与可靠性原则冲突（Adapt 而非 Adopt 的核心原因）。
- 量化幻觉风险：可能在无真实统计时输出精确百分比 / 频率 / 收入 / 转化率承诺。
- 范围蔓延风险：若不剥离运营类模块，Skill 职责会超出 MVP。
- License / 归属风险：若未核对 License 即复制 Prompt / 代码，存在合规风险。
- 来源伪造风险：评论分析场景下易产生不存在的引用，须强校验。

## Related MVP Skill

- **Customer Insight Analysis Skill**（DEC-015 候选 MVP Skill 之一）。
- **仅为候选关联，不代表该 Skill 已进入 MVP**；其最终名称 / 输入输出 Schema / 实现均**未确认**（见 DEC-017 Decision Boundary）。

## Open Questions

- 原始仓库的 License 类型？（须在复制任何内容前核对）
- 原始仓库的目标用户 / 精确输入契约 / 执行步骤？（待实际审计）
- 访问日期 / commit / 版本？（待补充）
- 改造后是否在 MVP 中处理竞品评论？是否支持持续评论监控？（均未确认）
- 该 Skill 对应几个工作流节点？（未确认）
- Customer Insight Analysis Skill 的最终名称、Schema、分析分类、评论统计方法、情绪分析模型、具体 Prompt / 代码？（均未确认）

---

## 评估维度参考（来自 DEC-016，覆盖情况）

| 维度 | 本评估覆盖位置 |
|------|----------------|
| 1. Business Fit | Strengths / Conflicts / Required Modifications |
| 2. Input Fit | Inputs / Open Questions |
| 3. Output Fit | Outputs / Required Modifications（Report-first 重构） |
| 4. Evidence and Reliability | Reliability Mechanisms / Required Modifications（来源契约、分析分类、校验） |
| 5. Human-in-the-loop | Human Review Mechanisms / Required Modifications（人工审核） |
| 6. Contract Completeness | Required Modifications（Skill Contract 八项） |
| 7. Engineering Quality | Risks / Estimated Adaptation Effort |
| 8. Legal and Attribution | License / Risks |
