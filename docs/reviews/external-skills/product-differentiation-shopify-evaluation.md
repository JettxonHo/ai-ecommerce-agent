# External Skill Evaluation — product-differentiation-shopify

> 本文件是 **Candidate 2（`nexscope-ai/eCommerce-Skills/product-differentiation-shopify`）** 的正式评估记录。
> 来源：[DEC-016 — 优先研究成熟电商 Skills，并通过契约化改造后复用](../../decisions/dec-016-external-skill-research-and-contract-based-adaptation.md)（Accepted，Agent，2026-07-27）。
> 评估结论已由用户接受：[DEC-018 — Product Differentiation Shopify 作为 Product Positioning Skill 的改造供体](../../decisions/dec-018-adapt-product-differentiation-for-positioning-skill.md)（Accepted，Agent，2026-07-27，用户回复「确认」）。
>
> **重要：**
> - **Reuse Recommendation: Adapt**（已由用户接受，DEC-018）。
> - 该候选**不**作为项目正式 Skill 直接使用，也**不**直接采用其现有分析脚本作为最终商品定位引擎，而是作为 `Product Positioning Skill` 的**研究与改造供体**。
> - **Adapt 不等于已实现。** 该候选仍须走完 DEC-016 的「审计 → 裁剪 → 重构为 Skill Contract → 校验 → 接入 Workflow State」流程并形成后续规格，才能落地为正式 Skill。
> - 本文件**未**复制任何第三方 SKILL.md / Prompt / Python 脚本 / 关键词库 / 模板 / 示例 / 测试（仅记录研究方向与改造要求）。
> - 凡原始仓库未在本评估中确认的字段（License 类型、原始目标用户、原始精确输入 / 工作流 / 脚本细节），均**如实标注为未确认 / 待研究**，未作编造。

---

## Repository and Skill

- 仓库：`nexscope-ai/eCommerce-Skills`
- Skill：`product-differentiation-shopify`
- 访问日期 / commit / 版本：**未在本评估中记录**（待后续实际审计时补充）。

## License

- **License 类型未确认。** 本评估未核对该仓库的具体 License。
- 已确认的是 **Attribution Principle（归属原则，DEC-016 / DEC-018）**：若后续实际复制或修改原仓库中的 Prompt、分析框架文本、Python 代码、关键词库、数据结构、示例、输出模板，必须根据其 License——遵守原始 License；保留必要的版权与许可声明；在项目 README 或 Skill 文档中标明来源；说明哪些内容被保留 / 修改 / 重写；区分第三方供体和项目原创架构。
- 当前只确认**研究与契约化改造方向**，**不执行复制**。

## Original Business Goal

- 原始 Skill 面向电商商品（从命名看偏 Shopify 场景）的**差异化分析与商品定位**，提供渐进式输入、竞品比较、痛点 / 差距分析、USP 与价值主张、定位框架等能力。
- 该原始业务目标与项目链路「商品事实 + 用户洞察 + 竞品资料 → 差异化分析 → 商品定位候选 → 营销策略与 Brief」**高度匹配**。
- 但其**关键词匹配 / 频率统计引擎**不能作为项目的最终定位推理，且其原始实现缺少项目已确认的可靠性契约（见 Conflicts）。

## Original Target User

- **未在本评估中从原始仓库文档确认。** 按 Skill 命名（`product-differentiation-shopify`）可**推断**为 Shopify 或类似平台的电商商家 / 运营人员；此为推断，非确认（见 Open Questions）。

## Inputs

- 原始 Skill 的**精确输入契约未在本评估中转录**。
- 概念上，该类差异化 / 定位 Skill 消费：商品信息、竞品信息（可选）、用户评论（可选）、市场 / 广告资料（可选）。其精确字段 / 格式 / 是否假设不存在的数据，待实际审计时确认。

## Progressive Analysis Levels

> 本节记录的是**改造方向（保留的设计思想）**，不是原始仓库的精确实现，也不是最终 Schema。

保留按资料丰富程度逐步增强分析的渐进式输入设计，并与项目已有的「最低可运行输入 + 增强输入」（DEC-005）保持一致。概念映射：

```
Level 1  基础商品信息            → 形成基础定位候选
Level 2  增加竞品信息或竞品评论   → 形成差异化机会
Level 3  增加当前商品用户评论     → 形成有用户证据的卖点与价值主张
Level 4  增加市场、广告或渠道资料 → 形成更完整的定位与传播建议
```

> 具体 Level 名称、数量和解锁规则**后续确定**（见 DEC-018 Decision Boundary）。

## Workflow

- 原始 Skill 的**精确执行步骤未在本评估中转录**（原仓库含分析脚本，本评估未复制其实现）。
- 本评估记录的是**目标改造后的概念工作流位置**（见 Required Modifications 与 DEC-018 Workflow Position）。

## Outputs

- 原始 Skill 倾向输出**定位建议 / 差异化结论 / 行动建议**（可能含基于关键词的结果）。
- 其覆盖的分析维度（按本评估用于「保留 / 参考」的内容归纳）包括：渐进式输入设计、竞品比较矩阵、用户痛点与竞品弱点分析、商品优势识别、USP 提取方法、品牌与商品定位框架、价值主张设计、差异化机会分析、定位结果和行动建议的表达方式。
- **完整原始实现 / 关键词引擎不被直接采用**（见 Required Modifications 中的「不直接采用」）；输出须改造为**待审核定位候选**。

## Existing Script Analysis

> 原始仓库的分析脚本（Python 代码 / 关键词库）**未在本评估中复制或转录**；以下为对其**角色定位**的结论。

- 候选仓库中的**关键词匹配和频率统计**可以作为：预处理、基础分类、召回辅助、规则基线、测试对照组。
- 但**不得直接作为最终洞察或定位依据**。项目**不采用**「关键词命中 = 用户需求已确认」，也**不采用**「提及次数最高 = 必须成为核心定位」。
- 原因：相同词语在不同语境中含义不同；用户可能在负面语境中提到某特征；关键词无法稳定理解隐含需求；高频不等于高商业价值；少量高影响反馈可能比高频轻微反馈更重要。
- 因此关键词匹配代码**只能作为辅助分析基线**，不能替代语义分析和业务判断。
- 是否将关键词分析保留为确定性工具，**未确认**（见 DEC-018 Decision Boundary）。

## Reliability Mechanisms

- 原始 Skill 的可靠性机制**未在本评估中确认**（是否保留来源、是否区分事实与推断、是否编造数据、是否含冲突识别、是否支持资料不足标记）。
- 这正是其**不能直接 Adopt** 的核心原因之一：缺少项目已确认（DEC-008 / DEC-011 / DEC-012 / DEC-015）的结构化证据契约；其关键词匹配更可能放大「高频 ≠ 高价值」的可靠性风险。

## Human Review Mechanisms

- 原始 Skill 的人工审核机制**未在本评估中确认**（是否存在确认 Gate、是否支持暂停、用户能否修改中间结果、修改后能否重生成）。
- 改造后**必须**满足 DEC-007（人工审核 / 异常暂停）与 DEC-009（阶段失效 / 局部重跑）；输出必须进入项目已有的关键人工审核节点。

## Strengths

- 直接命中 MVP 最核心业务问题之一：把商品事实 + 用户洞察转化为可使用的商品定位与卖点优先级。
- 渐进式输入设计与 DEC-005 输入分层理念契合。
- 竞品比较矩阵、痛点 / 差距分析、USP / 价值主张、定位框架覆盖较全。
- 关键词脚本可作为辅助基线 / 测试对照组，有一定工程价值。

## Conflicts with Current Decisions

- **关键词匹配作为最终推理** 与 DEC-008（分级证据）/ DEC-011（受约束 LLM）冲突 → 仅作辅助信号 / 基线，不作最终依据。
- **缺少来源与证据契约** 与 DEC-008 / DEC-012 冲突 → 须增加事实 / 洞察 / 来源关联。
- **可能输出无审核的最终定位** 与 DEC-007（审核）/ DEC-006（四层结构化输出）冲突 → 输出必须是 Positioning Candidate，而非 Confirmed Positioning。
- **可能含未支撑的商业影响估算**（转化率 / 销售额 / LTV / 市场份额 / 机会规模 / 收入影响）与可靠性原则冲突 → 无真实测试数据时不得输出，须标为推断 / 待验证。
- **含超 MVP 的定价 / 品牌战略模块**（价格策略 / 利润模型 / 品牌视觉体系 / 全渠道品牌战略 / 广告预算 / 长期品牌路线图 / 自动营销执行）须移除或隔离。

## Reusable Components

改造时优先保留以下分析能力（作为**方法 / 框架供体**，非直接复制实现）：

- **Progressive Input Levels**：按资料丰富程度逐步增强分析（见 Progressive Analysis Levels）。
- **Competitor Comparison Matrix**：可能比较功能 / 质量 / 设计 / 价格 / 服务 / 目标用户 / 使用场景 / 品牌表达 / 用户反馈 / 社会证明 / 价值主张；比较维度必须来自当前任务真实资料，不得为填满矩阵而编造。
- **Pain-point and Gap Analysis**：从当前商品评论、竞品评论、商品资料、用户访谈、市场资料中寻找差异机会，形成未满足需求 / 竞品常见问题 / 购买阻碍 / 潜在优势 / 待验证机会（属洞察或机会候选，不自动成为商品事实）。
- **USP and Value Proposition**：从事实和洞察中形成核心价值、关键差异点、核心卖点、价值主张、对比表达方向；USP 不得只由宽泛形容词组成（例：不推荐「质量很好」；推荐方向「针对高频通勤人群，通过轻量和紧凑设计降低携带负担」）；最终表达必须与真实事实和用户洞察关联。
- **Positioning Framework**：形成目标用户候选、核心需求、购买阻碍、商品角色、使用场景、核心价值、差异化角度、卖点优先级、定位陈述候选、待验证假设等候选结果。

## Required Modifications

**不直接采用：**

- **Keyword Matching as Final Reasoning**：关键词匹配 / 频率统计仅作预处理 / 基础分类 / 召回辅助 / 规则基线 / 测试对照组；不作最终洞察或定位依据；不采用「关键词命中 = 需求已确认」「提及最高 = 核心定位」。
- **Final Positioning without Review**：定位 / 目标用户 / 差异化建议**不能自动成为项目当前事实**；输出必须是 `Positioning Candidate`，而非 `Confirmed Positioning`。
- **Unsupported Business-impact Estimates**：无真实测试数据时不得输出转化率提升、销售额预测、LTV 预测、市场份额、精确机会规模、确定收入影响；须标为推断或待验证假设。
- **Pricing and Full Brand Strategy**：完整价格策略、利润模型、品牌视觉体系、全渠道品牌战略、广告预算配置、长期品牌建设路线图、自动营销执行——不属本 Skill MVP 职责，须移除或隔离。

**必须增加（重构为 Skill Contract，DEC-015；详见 [DEC-018](../../decisions/dec-018-adapt-product-differentiation-for-positioning-skill.md) 的 Target Skill Contract Direction）：**

- 结构化输入输出（概念输入 / 概念输出见 DEC-018，但**非最终 Schema**）。
- 前置条件：商品事实层有效；输入来源可识别；当前任务拥有最低可运行输入；用于定位的洞察已生成或明确标记资料不足；无竞品资料时可生成基础定位候选但必须标记 `competitive_evidence: insufficient`，不得编造竞品。
- 证据关联：定位候选须关联商品事实、用户洞察（存在竞品分析时还可关联竞品事实 / 竞品评论 / 差异化证据）；不得仅基于模型常识生成并标记为有证据定位。
- 分析分类：区分 Evidence-backed Positioning Candidate / Model-inferred Positioning Candidate / Hypothesis to Validate / Insufficient Competitive Evidence。
- 校验规则：输入 Fact/Insight Layer 须有效；引用的事实 / 洞察 ID 须存在；来源须属于当前任务；定位中的功能或参数不得超出商品事实；目标用户不得无依据写成已确认事实；卖点不得只有宽泛形容词；竞品差异须有真实竞品依据；无竞品资料须标记限制；无用户证据不得声称代表整体消费者；输出须符合结构化 Schema；量化商业影响须有真实依据；失效上游状态不得进入定位生成。
- 失败与暂停条件：商品事实严重缺失 / 关键冲突；Customer Insight Layer 已失效；引用的来源或 Insight 不存在；要求竞品定位但未提供任何竞品资料；定位候选依赖未确认高风险假设；LLM 多次返回无效结构；输出出现无依据参数或卖点；竞品资料与当前商品资料错误归属。
- 人工审核：选择定位候选、修改定位陈述、接受 / 否定目标用户候选、调整卖点优先级、确认待验证假设、补充竞品或用户资料、拒绝不符合品牌方向的建议；用户确认后当前有效定位才进入执行层 Brief。
- 测试方向：最低可运行输入 / 完整增强输入 / 无用户评论 / 无竞品资料 / 多个竞品 / 商品无明显差异 / 商品事实与用户评价冲突 / 高频关键词出现在负面语境 / 多个定位候选均合理 / 目标用户证据不足 / 生成不存在的事实引用 / 生成不存在的竞品 / 用户修改洞察后局部重跑 / 上游 Insight Layer 已失效 / 输出 Schema 失败。
- 工作流位置：位于「Product Fact Extraction → Customer Insight Analysis → Product Positioning Skill → Human Review → Marketing Brief Generation」；具体工作流节点数量**未确认**；本 Skill 不拥有完整工作流控制权。

## Reuse Recommendation

**Adapt**（已由用户接受，DEC-018，回复「确认」）。

- 保留渐进式输入、竞品矩阵、USP 和定位框架；
- 关键词匹配只作为辅助信号或基线；
- 不直接采用原始分析脚本作为最终定位引擎；
- 定位结果必须是待审核候选；
- 增加结构化输出、事实 / 洞察 / 来源关联、校验 / 失败处理 / 测试；
- 不直接复制实现。

## Estimated Adaptation Effort

- **未量化。** 改造工作量（人天 / 排期）未在本评估中估算，属后续规格设计范畴。
- 定性判断：属**中高改造**——须重构输出形态（候选化）、剥离关键词作为最终推理、新增证据 / 校验 / 暂停 / 测试、剥离超 MVP 的定价 / 品牌模块。

## Risks

- 关键词匹配放大「高频 ≠ 高价值」风险：若误用作最终推理，会输出与真实价值不符的定位。
- 原始实现缺少结构化 Workflow State / 分级证据 / 来源追踪 / 人工审核 / 阶段失效 / 局部重跑 / 任务级持久化 / 确定性校验 → 直接使用会与可靠性原则冲突（Adapt 而非 Adopt 的核心原因）。
- 量化幻觉风险：可能在无真实测试数据时输出转化率 / 销售额 / LTV / 市场份额 / 收入影响。
- 范围蔓延风险：若不剥离定价 / 品牌战略模块，Skill 职责会超出 MVP。
- License / 归属风险：若未核对 License 即复制 Python 脚本 / 关键词库，存在合规风险。
- 来源伪造风险：定位场景下可能生成不存在的事实引用或竞品，须强校验。

## Related MVP Skill

- **Product Positioning Skill**（DEC-015 候选 MVP Skill 之一）。
- **仅为候选关联，不代表该 Skill 已进入 MVP**；其最终名称 / 输入输出 Schema / 实现均**未确认**（见 DEC-018 Decision Boundary）。

## Open Questions

- 原始仓库的 License 类型？（须在复制任何内容前核对）
- 原始仓库的目标用户 / 精确输入契约 / 执行步骤 / Python 脚本与关键词库细节？（待实际审计）
- 访问日期 / commit / 版本？（待补充）
- 渐进式输入的最终级别名称 / 数量 / 解锁规则？（未确认）
- 是否在 MVP 中要求竞品资料？竞品资料采集方式？（未确认）
- 关键词分析是否保留为确定性工具？（未确认）
- 定位候选数量、置信度机制、人工审核 UI？（未确认）
- 该 Skill 对应几个工作流节点？（未确认）

---

## 评估维度参考（来自 DEC-016，覆盖情况）

| 维度 | 本评估覆盖位置 |
|------|----------------|
| 1. Business Fit | Strengths / Conflicts / Required Modifications |
| 2. Input Fit | Inputs / Progressive Analysis Levels / Required Modifications（前置条件） |
| 3. Output Fit | Outputs / Required Modifications（候选化） |
| 4. Evidence and Reliability | Reliability Mechanisms / Existing Script Analysis / Required Modifications（证据关联、分类、校验） |
| 5. Human-in-the-loop | Human Review Mechanisms / Required Modifications（人工审核） |
| 6. Contract Completeness | Required Modifications（Skill Contract 八项） |
| 7. Engineering Quality | Existing Script Analysis / Risks / Estimated Adaptation Effort |
| 8. Legal and Attribution | License / Risks |
