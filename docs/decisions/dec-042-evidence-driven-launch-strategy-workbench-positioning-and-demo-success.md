# DEC-042：确认“证据驱动商品上新策略工作台”定位、复合 Persona 假设与行为型演示成功标准

## Type

Product / Positioning / Persona / Acceptance

## Status

Accepted — Amended by DEC-048

> **Current amendment:** [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) 冻结首个演示的代表性验收包、行为门禁、人工 `PASS / FAIL` 与 Release Candidate Live Smoke；本决定的产品定位、Persona 假设策略和行为型成功标准保持有效。

## Decision

### 产品定位

AI Ecommerce Agent 定位为：

> 面向中小电商商品与内容运营人员的**证据驱动商品上新策略工作台**，将用户提供的商品与市场资料转化为可审核、可追溯的商品定位分析、平台中立 Marketing Brief 与小红书 Brief 映射。

该定位强调业务决策、证据与人工审核，不将产品缩减为自由生成文案的聊天工具，也不扩大为覆盖全部电商经营场景的通用操作系统。

### Persona 与 JTBD 假设策略

- MVP 采用一个**复合主 Persona**：中小电商商家的商品运营与内容运营人员。
- “商品运营侧重”和“内容运营侧重”作为同一 Persona 下的两种职责视角，不在缺少研究证据时拆成两个完整 Persona。
- 当前 JTBD 基线假设承接 DEC-003：用户在商品上新或正式内容推广前，需要把分散的商品与市场资料整理为可追溯的定位判断和可审核 Brief，以支持后续内容策划与执行。
- 年龄、组织规模、工作年限、角色占比、具体痛点、行为习惯、付费意愿和购买者关系均保持 `Assumption / Open Question`，不得写成用户研究事实。
- 真实用户访谈是 Beta 前门禁，不是本地演示前置条件；访谈结果可以通过后续 Decision 修订 Persona 和 JTBD。

### 演示成功标准

首个本地演示采用行为与人工可用性验收。演示至少应证明：

1. 新环境可按权威文档启动本地演示栈；
2. 用户可通过引导式任务工作台提交 DEC-041 允许的资料；
3. 系统能完成事实、洞察、定位、单一 Human Review、平台中立 Marketing Brief、小红书 Brief 映射与导出闭环；
4. 用户可以理解主要结论、证据来源、假设、资料不足与冲突，并完成审核或补充资料；
5. 结果在关键中断后可按规格恢复，失效内容不会被继续当作当前有效结果；
6. 目标用户视角下的交付物可以用于后续内容策划，而不需要开发者解释系统内部实现才能完成流程。

Rubric 和指标只辅助专业判断。具体 Fixture、测试层级和必要阈值由 Testing Strategy 冻结，不以机械总分、语言流畅度或销量承诺自动判定成功。

## Alternatives Considered

### “AI 营销 Brief 生成器”

- 优点：表达简单、易理解。
- 缺点：弱化定位分析、证据追溯、人工审核和状态恢复价值。
- 结论：未采用。

### “电商 Agent 工作台”

- 优点：为未来扩展保留较大空间。
- 缺点：范围过宽，容易被误解为覆盖广告、库存、客服或店铺诊断。
- 结论：未采用。

### 立即拆分两个完整 Persona

- 优点：角色描述更细。
- 缺点：当前缺少访谈证据，容易把推测写成事实。
- 结论：暂不采用；保留同一复合 Persona 下的职责视角。

### 机械评分或仅完成演示脚本

- 机械评分更容易自动判断，但会在测试集与阈值未冻结时制造虚假精确；只完成脚本又不足以证明可靠性和人工可用性。
- 结论：均未采用，使用行为证据 + 人工可用性判断。

## Reason

该组合与 DEC-001 的业务价值优先、DEC-002 / 003 的用户与核心任务、DEC-039 的适度校验和 DEC-041 的本地演示包络一致。它为产品和验收提供清晰方向，同时避免伪造尚未完成的用户研究和过早机械化评分。

## Impact

- Product Vision、PRD、MVP Scope、Personas、User Flows、Testing Strategy 与 Goal 必须使用本定位和成功边界。
- Persona 研究项继续标为假设；后续真实访谈可触发修订，不静默覆盖本 DEC。
- 产品工作台和 Brief 的最终字段、交互、Fixture 与阈值仍需后续独立 Decision Gate。
- 本决定不授权业务实现、Technical Spike 执行或 Goal 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-003 至 RFC-007；本决定不接受任何 RFC 实现方案。

## Supersedes

None.

## Amends

- DEC-002：确认复合主 Persona 的策划方式，不改变已接受的首要用户群体。
- DEC-003：补充产品定位表述和 JTBD 基线假设。
- DEC-010 / DEC-041：补充行为型演示成功标准，不推翻三维评价框架或交付包络。

## Amended By

- [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)

## Notes

“证据驱动”表示结论须遵守既有 Evidence 与 Human Review 契约，不代表新增泛化安全工程、哈希要求或机械证据评分。

本决定接受时留给 Testing Strategy 的 Fixture、必要阈值和执行方法已由 DEC-048 在首个演示范围内解决；具体测试工具与 Fixture 内容仍待后续实例化。
