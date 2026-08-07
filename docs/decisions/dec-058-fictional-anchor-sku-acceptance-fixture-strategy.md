# DEC-058：固定一个虚构 Anchor SKU 及三种资料变体作为验收基线

## Type

Product Acceptance / Fixture Strategy / Testing

## Status

Accepted

## Decision

首个端到端演示以明确标注为虚构、非管制类商品的**“城市通勤双肩包”**作为唯一 Anchor SKU。DEC-048 的三个资料包和一个变更脚本按同一商品实例化：

1. **资料充分变体：** 支撑正常 Fact → Insight → Positioning → Human Review → Marketing Brief → Xiaohongshu Brief → Markdown Export 闭环；
2. **资料不足但可运行变体：** 保持同一商品身份，移除增强或可选资料，验证诚实降级而非机械阻断；
3. **阻断性冲突与恢复变体：** 保持同一商品上下文，引入一个真实影响商品身份或诚实事实层的冲突，验证 Needs Input、用户裁决或补料及正确恢复；
4. **正常任务变更脚本：** 修改一个重要商品事实，验证 Source / Domain Version、失效预览、陈旧 Review 拒绝、确认式局部重跑与 Current Truth 导出。

三个资料包共享基础商品身份和大部分可比内容，只改变与目标行为直接相关的资料完整性、冲突和版本。资料与 expected behavior 必须显式标为测试数据，不得包装成真实品牌资料、真实用户研究或跨品类泛化证据。

具体文件内容、文件名、目录、expected-output 表示和测试装载方式仍由 Testing Strategy 与 Goal 内独立测试 Issue 实例化。不得为了让 Fixture 看起来真实而使用未授权品牌、评论、商标或来源，也不新增 Hash、SHA-256 或内容指纹要求。

## Alternatives Considered

### P-43B：三个不同虚构品类

- 优点：表面覆盖更多业务表达和输入结构。
- 缺点：品类差异与状态差异相互混杂，失败原因更难定位，资料维护量也更高。
- 结论：不采用为首个演示基线。

### P-43C：真实品牌或真实 Listing 数据集

- 优点：演示观感更接近真实业务。
- 缺点：引入来源许可、商标、隐私、内容变化和可复现性问题，也不能替代 Beta 用户研究。
- 结论：不采用。

## Reason

首个演示的核心是验证证据、版本、审核、失效和恢复闭环，而不是证明跨品类泛化。单一虚构 Anchor SKU 让各场景差异主要来自系统行为，减少无关变量、资料治理和维护成本，符合 DEC-039 的适度校验原则。

## Impact

- Testing Strategy、PRD、MVP Scope、User Flows、Traceability 与长期 Goal 必须使用该 Anchor SKU 和四个场景角色。
- 真实 Provider Release Candidate Smoke 只使用资料充分变体，不扩大为 Live Edge-case Matrix。
- “城市通勤双肩包”只是一项可维护测试基线，不构成产品品类限制，也不证明跨品类适用性。
- 本决定不创建实际 Fixture 文件，不执行测试、Technical Spike 或真实模型调用，不授权业务实现或 Goal 创建 / 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-004、RFC-005、RFC-006；本决定不接受其技术方案。

## Supersedes

None.

## Amends

- [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)：实例化三个固定资料包和一个变更脚本的商品策略，不改变四个场景语义、行为门禁、人工判断或 Markdown-first 导出。

## Does Not Amend

- DEC-042：真实用户访谈仍是 Beta 前门禁；虚构 Fixture 不能成为用户研究证据。
- DEC-039：不增加机械 Rubric、罕见变体矩阵或普通内容哈希要求。

## Notes

用户于 2026-08-07 明确接受 `P-43A`。Issue #52 / Draft PR #53 负责本决定和验收策略输入的归档。
