# DEC-016：优先研究成熟电商 Skills，并通过契约化改造后复用

> 本决定记录用户已明确接受的 Agent 与架构策略。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill = 带执行契约的可复用业务能力包）。

## Type

Agent

## Status

Accepted（2026-07-27，用户对该策略明确回复「确定」，通过 Decision Gate）

## Decision

AI Ecommerce Agent 项目在设计 MVP Skills 时，**优先调研和评估** GitHub 上已有的成熟电商业务 Skills、SOP、分析框架、输出模板、规则库和测试案例。

对于与当前业务方向匹配的外部 Skill，可以复用或改造以下内容：

- 业务分析框架；
- 执行步骤；
- 输入信息清单；
- 输出结构；
- 行业术语；
- 风险边界；
- 追问策略；
- 人工确认节点；
- 校验规则；
- 评分方法；
- 测试场景；
- 确定性工具代码。

但**第三方 Skill 不得未经审计直接成为项目正式 Skill**。正式引入前必须经过：

```
发现候选 Skill
→ 分析业务目标和适用范围
→ 审计输入输出与隐含假设
→ 审计证据、合规和失败处理
→ 删除与 MVP 无关内容
→ 重构为项目 Skill Contract
→ 增加结构化输入输出
→ 增加来源与证据关系
→ 增加暂停和人工审核条件
→ 增加确定性校验
→ 增加测试与评价标准
→ 接入 Workflow State
```

> 该改造流程衔接 DEC-015 的 Skill Contract（业务目标 / 适用条件 / 输入契约 / 执行步骤 / 工具依赖 / 输出契约 / 确定性校验 / 失败暂停条件 / 评价标准）与 DEC-012 的 Workflow State。

## Repository Roles

项目需要区分两类外部仓库。

### 1. Workflow Base Repository（工作流基底仓库）

负责提供或参考：

- 显式工作流；
- 状态管理；
- 暂停与恢复；
- 持久化；
- 人工审核；
- 局部重跑；
- RAG 集成；
- 结构化输出；
- 测试框架。

> **该仓库尚未选择。**

### 2. Skill Donor Repository（Skill 供体仓库）

负责提供或参考：

- 电商业务 SOP；
- 分析方法；
- 输入输出模板；
- 风险规则；
- 行业经验；
- 测试案例；
- 可复用工具。

一个 Skill Donor Repository **不需要**同时承担整个项目的工作流基底。

项目未来可以采用：

```
一个主要工作流基底
+ 多个外部 Skill 供体
+ 项目自有的状态、证据、审核和可靠性契约
```

## Reuse Levels

外部 Skill 的处理结果分为四种。

### Adopt

可以在较少修改后使用。要求：

- 业务目标高度匹配；
- License 允许；
- 输入输出基本清晰；
- 不违反当前 Decisions；
- 可靠性风险较低；
- 改造成本可控。

### Adapt

保留核心业务方法，但重构为项目 Skill Contract。通常需要：

- 删除无关模块；
- 修改输入输出；
- 增加来源关系；
- 增加结构化状态；
- 增加暂停条件；
- 增加校验和测试。

> **这是当前最可能采用的方式。**（仍属策略预期，不代表任何候选已被判定为 Adapt。）

### Reference Only

只参考：

- 分析维度；
- 行业方法；
- 输出模板；
- 测试案例；
- 风险规则。

**不复制其完整实现。**

### Reject

当候选 Skill 出现以下问题时排除：

- 业务方向不匹配；
- 依赖大量未确认技术；
- 自动编造缺失信息；
- 无法区分事实和推断；
- 无来源或伪引用风险；
- 直接自动发布或执行高风险操作；
- License 不明确或不兼容；
- 代码或文档质量过低；
- 改造成本高于重新设计。

## Mandatory Evaluation Dimensions

每个候选 Skill 至少从以下维度评估。

### 1. Business Fit

- 是否服务商品运营或内容运营人员；
- 是否支持商品上新定位和营销 Brief；
- 属于核心分析层、执行层还是未来扩展层；
- 是否明显超出 MVP。

### 2. Input Fit

- 需要哪些输入；
- 是否能在最低可运行输入下工作；
- 是否支持增强输入；
- 缺失信息时怎样处理；
- 是否偷偷假设不存在的数据。

### 3. Output Fit

- 输出能否映射到事实、洞察、策略和执行四层；
- 是否具有结构化输出；
- 是否适合作为 Workflow State 条目；
- 是否输出过大或过宽的报告。

### 4. Evidence and Reliability

- 是否保留来源；
- 是否区分事实与推断；
- 是否会编造数据；
- 是否包含冲突识别；
- 是否存在风险和合规边界；
- 是否支持资料不足标记。

### 5. Human-in-the-loop

- 是否存在确认 Gate；
- 是否支持暂停；
- 用户能否修改中间结果；
- 用户修改后是否能重新生成受影响内容。

### 6. Contract Completeness

是否具备：业务目标、适用条件、输入契约、执行步骤、工具依赖、输出契约、校验规则、失败和暂停条件、评价标准、测试场景。

### 7. Engineering Quality

- 是否包含可执行代码；
- 是否有测试；
- 是否有验证脚本；
- 是否容易拆分；
- 是否依赖特定运行时；
- 是否容易接入项目 Workflow State。

### 8. Legal and Attribution

- License 是否明确；
- 是否允许修改和再发布；
- 是否需要保留版权声明；
- README 是否需要标注来源；
- 项目简历和文档中是否能够清楚说明原创贡献。

## Initial Candidate Set

首轮正式评估以下三个候选（**目前只是研究对象，不代表已进入 MVP**）：

| 候选 | 仓库 | 拟评估用途 |
|------|------|------------|
| Candidate 1 | `nexscope-ai/eCommerce-Skills/product-review-analysis` | Customer Insight Analysis Skill 的业务方法和输出框架供体 |
| Candidate 2 | `nexscope-ai/eCommerce-Skills/product-differentiation-shopify` | Product Positioning Skill 的差异化分析、渐进输入和定位框架供体 |
| Candidate 3 | `feichanggege/ecommerce-visual-copywriting-skill` | 输入缺失处理、人工确认 Gate、合规检查以及执行层营销与视觉 Brief 的供体 |

> 以上三个候选目前只是**研究对象**，**不代表已进入 MVP**，也**未被标记为** Adopt / Adapt / Reference Only。

## Expected Research Output

每个候选 Skill 的评估结果至少包含（详见 [../reviews/external-skill-evaluation-template.md](../reviews/external-skill-evaluation-template.md)）：

```
# External Skill Evaluation
## Repository and Skill
## License
## Original Business Goal
## Original Target User
## Inputs
## Workflow
## Outputs
## Reliability Mechanisms
## Human Review Mechanisms
## Strengths
## Conflicts with Current Decisions
## Reusable Components
## Required Modifications
## Reuse Recommendation (Adopt / Adapt / Reference Only / Reject)
## Estimated Adaptation Effort
## Risks
## Related MVP Skill
## Open Questions
```

## Attribution Principle

如果项目实际复制或修改第三方代码、Prompt、模板、规则库或文档内容，必须：

- 遵守原始 License；
- 保留必要版权声明；
- 在项目文档中标明来源；
- 说明修改内容；
- 区分第三方贡献和项目原创贡献。

**不得将第三方成熟方案包装为完全原创。** README 后续应包含类似内容：

```
## Open-source References and Adaptations

This project studies and adapts selected open-source
e-commerce skills. Each adaptation is documented with
its source, license, retained concepts and original changes.
```

> 具体格式后续确定。

## Reason

从零设计所有 Skill 会重复解决已经存在的问题，例如：电商业务步骤梳理、评论分析维度、商品差异化框架、输入资料清单、风险边界、输出模板、测试案例。

研究成熟 Skill 可以：

- 缩短业务研究时间；
- 降低遗漏重要步骤的风险；
- 学习已落地的工作流；
- 获得更成熟的行业表达；
- 提高 MVP 完成速度；
- 形成清晰的开源改造案例。

但直接复制第三方 Skill 会产生：

- 业务范围不匹配；
- Prompt 化而非契约化；
- 缺乏来源和结构化状态；
- 与项目可靠性原则冲突；
- 无法证明项目所有者的原创贡献；
- License 和归属风险。

因此应采用「研究、审计、裁剪、重构、验证」的方式复用。

## Impact

该决定将影响：MVP Skill 清单、Skill 研究流程、Agent 架构、开源仓库筛选、项目目录、Skill Specification、测试设计、README、License 管理、简历项目表达、后续 Multi-Agent 决策、实现工作量。

后续技术方案必须回答：**它是否便于把审计后的外部业务方法接入项目自己的 Workflow State、证据、审核和可靠性契约，而非整体照搬第三方实现？**

## Decision Boundary

**本决定已经确认：**

- 优先研究成熟外部电商 Skills；
- 不要求所有 Skill 从零设计；
- 外部 Skill 必须经过审计和契约化改造；
- 区分工作流基底仓库和 Skill 供体仓库；
- 外部 Skill 分为 Adopt、Adapt、Reference Only 和 Reject；
- 首轮评估三个候选 Skill；
- 必须遵守 License 并记录来源；
- 复用后仍需接入项目自己的 Workflow State、证据和审核机制。

**本决定尚未确认：**

- 三个候选的最终评价；
- 哪些 Skill 进入 MVP；
- 是否直接复制任何代码；
- Skill 的最终数量；
- Skill 目录结构；
- 具体实现框架；
- Multi-Agent；
- 工作流基底仓库；
- LangGraph；
- 具体 GitHub 仓库组合；
- 改造排期。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill 契约化定义）：外部 Skill 复用必须重构为符合 DEC-015 的 Skill Contract，并接入 DEC-012 的 Workflow State、DEC-008 的证据标记、DEC-007 的人工审核与异常暂停。
- 区分「工作流基底仓库」（Workflow Base，未选择）与「Skill 供体仓库」（Skill Donor）——与 Question-009（开源基底仓库筛选标准）相关，但**未**确认任何具体基底仓库或 GitHub 仓库组合。
- Multi-Agent 讨论暂时顺延到候选 Skill 和 MVP Skill 清单明确之后（Question-008 仍开放）。
- 三个候选仅为首轮研究对象，**未被评价、未被标记为 Adopt / Adapt / Reference Only、未进入 MVP**。
- 本决定**不**确认 LangGraph、工作流基底仓库、Skill 最终数量、具体实现框架、Anthropic Skills / OpenAI Skills / MCP、或任何具体 GitHub 仓库组合。
