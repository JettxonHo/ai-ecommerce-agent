# Session-004：MVP-0 Fast Lane 执行重基线

## Metadata

- Status: Concluded
- Date: 2026-08-12
- Topic: 过度设计审阅、最小 MVP 裁剪与 Goal 重基线
- Related RFCs: RFC-001～007（历史/按需引用）
- Related Decisions: [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md), [DEC-075](../decisions/dec-075-rapid-mvp0-planning-package-and-goal-activation.md), [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md)

## Context

用户认为开发速度过慢，要求审阅项目与规划文档是否过度设计，特别检查安全防范，并针对“最快且保留核心功能的最小 MVP”优化。

## Goal

区分真实 MVP 安全边界与防御性证明成本，选择一个不推倒已实现基础、但能尽快交付用户闭环的新执行路径。

## Non-goals

- 不在本轮修改业务代码；
- 不删除历史 RFC / DEC / Session；
- 不降低 Secret、SQL、scope、XSS/Markdown、幂等或原子提交边界；
- 不立即清理已存在的复杂模块和测试。

## Discussion

### Facts

- 审阅基线附近约有 14,037 行后端生产代码、44,275 行后端测试和 10,974 行架构测试。
- 规划文档约 65,079 行，Decision Log 已有 77 个 Decision。
- GitHub Required Checks 通常在数分钟内完成；主要延迟来自测试/守卫编写、微型合同切片、复审往返和元数据维护，而不是 CI wall-clock。
- Web 已有 generated client、Task gateway、Task routes 和 TaskWorkbench shell；FastAPI application factory 尚未注册业务 routes。
- README、旧 Goal 和 Readiness 仍把部分已合并 Web 能力描述为未实现。
- DEC-039 已明确要求与真实风险相称、停止低概率变体堆叠，但实际执行出现偏离。

### Observations

- 项目过度设计主要表现为内部结构证明，而不是必要的运行时安全。
- 横向完成 Contract / DTO / Protocol / Persistence / Runtime 后再集成的顺序推迟了第一个用户闭环。
- 大量文档不再提供单一当前事实，反而提高 Agent 协调成本。

### Proposals

1. 只精简治理与测试，不改变旧产品执行路径；
2. 建立 MVP Fast Lane，以纵向闭环取代剩余横向 Backlog；
3. 绕开现有架构创建一次性独立 Demo。

### Trade-offs

- 方案 1 风险最低，但不能解除高级能力的前置依赖。
- 方案 2 复用现有基础并冻结高级设计，能最快形成真实产品证据。
- 方案 3 首屏可能最快，但产生双实现和长期分叉。

### Risks

- 过度裁剪可能误删真实安全边界；因此 DEC-078 明确保留 input/scope/SQL/atomicity/XSS/idempotency/Secret。
- 旧 Accepted Decision 与新执行范围可能冲突；因此使用 Amends / Defers 关系，不静默删除历史设计。
- 只修改 Goal 而不修改入口文档会让 Agent 继续读取旧 Backlog；因此 FL-0 同步 AGENTS、README、Readiness 和 Testing Strategy。

## Accepted Decisions

- [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) — 用户选择方案 B，确认第一阶段输入收窄为粘贴文本/TXT/Markdown，确认先完成文档重基线并接受详细 Fast Lane Goal（2026-08-12）。

## Rejected Approaches

- 只清理治理、不改变横向执行顺序：无法确保开发资源转向端到端闭环。
- 建立独立一次性 Demo：会绕开已经投入的合同和实现，形成双轨技术债。
- 删除全部旧复杂代码和测试：清理本身会推迟 MVP，且可能破坏仍有价值的真实边界。

## Open Questions

- Required Checks 的具体去重和 Secret / dependency 扫描 cadence 由后续独立低风险 CI Issue 依据实际 workflow 证据确定。

## Deferred Topics

完整 Retrieval/Evidence、Distributed Worker/Recovery、Source lifecycle、高级 Review、Auth/Multi-tenant/Public Deployment 均按 DEC-078 后移。

## Documentation Updates

- 新增 DEC-078 和 MVP-0 Fast Lane Goal；
- 标记旧 Goal 的剩余执行被取代；
- 同步 AGENTS、README、Implementation Readiness 和 Testing Strategy；
- 更新 Decision Log 与 Session index。

## Synchronization Checklist

- [x] 本轮讨论记录了事实、方案、权衡、风险和延期项
- [x] 用户的明确接受写入 DEC-078 与 Decision Log
- [x] 受影响的 Current Truth / execution documents 已同步
- [x] 与旧 Goal / DEC-075 的 Amends 关系已保留
- [x] 未创建业务实现代码
