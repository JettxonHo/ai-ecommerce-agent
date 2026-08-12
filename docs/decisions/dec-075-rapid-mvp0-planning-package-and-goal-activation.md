# DEC-075：接受快速 MVP-0 策划包并激活长期 Goal

## Type

Governance / Development Plan / Testing / Goal Activation

## Status

Amended by [DEC-078](dec-078-mvp0-fast-lane-execution-rebaseline.md)

DEC-075 remains the authority for completed work, long-running authorization, Agent routing and high-risk human gates. DEC-078 replaces the remaining horizontal MVP-0 Goal, Testing and Readiness execution plan with the vertical Fast Lane.

## Decision

用户整体接受以下策划与执行 Gate：

- [MVP-0 Development Plan](../development/mvp0-development-plan.md)；
- [Testing Strategy](../development/testing-strategy.md)；
- [End-to-end Demo MVP-0 Goal](../goals/end-to-end-demo-mvp0-goal.md)；
- [Rapid MVP-0 Readiness Review](../reviews/review-2026-08-08-rapid-mvp0-predevelopment-readiness.md)。

结合 RFC-007 整体接受、P-71A～P-73A 接受与 [DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md) 的长期执行授权，MVP-0 的开发前 Gate 已闭合。规划 PR #59 合并后，Goal 状态切换为 `ACTIVE`，Sol 可以创建首批有界 Issues，并将实现任务按完整任务合同交给准确的自定义 Agent `luna-worker`。

## Reason

产品范围、技术架构、公共契约、测试层级、里程碑、停止条件、Agent 路由和人工 Gate 已达到快速 MVP-0 的实现就绪标准。继续停留在策划阶段不会降低剩余技术风险；这些风险已被拆入 stop-first compatibility Issues 和逐 PR 验收。

## Impact

- Business / Production Implementation 在 Accepted Goal 和 Issue 合同范围内获得授权。
- `luna-worker` 负责边界明确的实现与修复；Sol 负责策划、调度和独立 Review。未经用户明确许可不使用 Terra。
- 普通低风险 PR 在验收、Required Checks 和 Sol 独立 Review 全部通过后可自主合并。
- 数据破坏、不可逆迁移、重大公共契约或产品范围变化、安全 / 隐私高风险、主要技术栈更换和降低质量标准仍须人工确认。
- 完整 ARP、TS-02 / 04 / 05、PDF、Embedding / Semantic / Hybrid、公开部署与其他 Non-goals 继续后移，不因 Goal 激活而进入范围。

## Related

- [DEC-078](dec-078-mvp0-fast-lane-execution-rebaseline.md)
- [DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md)
- [Implementation Readiness](../handoffs/implementation-readiness.md)
- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)
- [Issue #58](https://github.com/JettxonHo/ai-ecommerce-agent/issues/58)
- [PR #59](https://github.com/JettxonHo/ai-ecommerce-agent/pull/59)

## Source

用户于 2026-08-08 明确接受 Development Plan、Testing Strategy、MVP-0 Goal 与 Readiness Review 整体；同一指令接受 P-68A～P-73A 与 RFC-007 整体。
