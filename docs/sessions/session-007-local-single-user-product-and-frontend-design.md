# Session-007：本地单用户产品与前端设计方向

## Metadata

- Status: Concluded
- Date: 2026-08-19
- Topic: 固定本地单用户产品、Action Workbench 与 Kimi 前端路由
- Related Decisions: [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md), [DEC-056](../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md), [DEC-062](../decisions/dec-062-minimal-recent-task-index-and-stable-deep-links.md), [DEC-071](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md), [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md), [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md), [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md), [DEC-082](../decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md)
- Related Issue: [#291](https://github.com/JettxonHo/ai-ecommerce-agent/issues/291)

## Context

FL-1 已形成可运行的本地 deterministic 产品纵向，FL-2 则保持 `GOAL_BLOCKED`。用户选择下一步先把现有能力变成固定本地单用户产品，并明确确认 Direction A 的界面基线，而不是先扩展 Provider、后台 Dashboard 或多租户能力。

既有 Frontend Decisions 已冻结技术栈、状态所有权和 TaskWorkbench 模块边界，但仍需要一个具体的页面层级、视觉语言与设计执行路由。用户也明确允许本地 Kimi Code + Kimi K3 参与后续前端设计和开发，因此必须把这一例外限定在前端并与 Luna / Terra 的默认实现路由分开。

## Goal

把用户确认的 Direction A 归档为 Accepted Decision，明确下一步设计 Issue 的边界，同时保持 Fast Lane、Provider、安全与实现授权不变。

## Non-goals

- 不创建设计稿、线框、组件、样式或 Web 代码；
- 不调用 Kimi 或其他模型；
- 不修改后端、Provider、Secret、PostgreSQL、migration、OpenAPI、认证、多租户或公开部署；
- 不创建 DEC-081 Phase B，不诊断或修复 FL-2；
- 不把 FL-1 foundation 或本次产品方向接受写成完整 Goal 成功。

## Discussion

### Fact

- 当前产品运行在固定本地工作区，已有 `/tasks`、稳定 Task 深链、TaskWorkbench、Review、Results 与 Markdown 导出。
- React 19 + TypeScript + Vite 8、CSS Modules、原生语义 HTML / 按需 Radix、generated client、same-origin 与安全 Markdown 已由现有 Decisions 冻结。
- MVP-0 Fast Lane 当前状态是 `GOAL_BLOCKED`；DEC-081 Phase A 以 `INSUFFICIENT_SANITIZED_EVIDENCE` 结束，没有 production repair 或 Phase B contract，也没有新的 Provider run 授权。
- 用户明确确认 Direction A，并明确授权本地 Kimi Code + Kimi K3 只在后续精确前端合同下参与设计与实现。

### Observation

- `/tasks` 若只被理解为最近任务列表，无法明确表达用户下一步行动；若直接扩成 Dashboard，则会带入无消费者的指标、搜索和批量范围。
- 一个活跃工作区配合窄上下文栏，能保持任务焦点，同时让证据、限制和风险按需可达。
- Review 与 Results 需要产品语义视图；默认暴露原始 JSON 会把实现结构推给运营用户。
- AI 更适合作为阶段状态、上下文和限制的解释层，而不是业务状态来源或聊天式信息架构。

### Alternatives

1. 通用运营 Dashboard；
2. Chat-first Agent；
3. 移动端优先的多端产品；
4. Direction A：本地单用户 Action Workbench。

### Risk

- 在设计合同前直接实现会把视觉偏好误写成组件与公共行为。
- 把 Kimi 许可解释成默认回退会破坏 DEC-071 / 072 的模型路由和身份治理。
- 用新视觉层发明业务状态、写权限或数据会违反后端 Current Truth。
- 同时加入 Dashboard、移动端和店铺经营模块会扩大 MVP 范围并掩盖核心 Task 流。

### Accepted Decision

- [DEC-082](../decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) — 用户于 2026-08-19 明确确认 Direction A。
- 首个产品化方向是固定本地单用户 Action Workbench；`/tasks` 是行动首页，不是 Dashboard。
- Task 深链采用中文五阶段轨道、一个 Active Workspace 与可折叠 `320–360px` Context Rail；Review 结构化，Results 行动导向，Marketing / Xiaohongshu 分视图，raw JSON 退到技术细节。
- 视觉使用中文优先“运营编辑部 / 策略桌”，温暖中性色 + 墨色 / 深海军蓝 + 一个低饱和松绿 / 青绿强调色；AI 作为上下文进度和状态，不采用 chat-first。
- 后续重要前端设计使用适用 taste skills；Kimi Code + Kimi K3 仅在精确前端合同中作为显式例外，不是 Luna / Terra fallback，且必须经过 Sol 独立五轴 Review。

### Open Question

- 下一独立设计 Issue 应如何把 Action Home、Intake、Needs Input、Running、Review、Results 与 Unavailable 状态投影为可审阅的关键屏幕？
- 设计稿应如何证明 `320–360px` Context Rail、Desktop Chrome 与 320 CSS px reflow 在不创造手机产品的情况下成立？
- 哪些既有组件可以保留，哪些视觉结构需要替换，只能在代码与设计审计后确定；当前不预选实现方案。

## Documentation Updates

- 新增 DEC-082 与本 Session；
- 更新 Decision Log；
- 同步 Frontend Architecture、User Flows、MVP Scope、Fast Lane Goal、AGENTS、README 与 Implementation Readiness；
- 保留 DEC-055 / 056 / 062 / 071 / 072 原文，通过 DEC-082 记录修订关系；
- 保持 DEC-078 / 081、`GOAL_BLOCKED`、无 Phase B / Provider authorization 的当前事实。

## Synchronization Checklist

- [x] Fact、Observation、Alternative、Risk、Accepted Decision 与 Open Question 已分开记录
- [x] DEC-082 记录 Concretizes / Narrowly amends / Preserves 关系
- [x] Direction A 的产品、布局、视觉和非目标已明确
- [x] Kimi 只作为后续精确前端合同的窄例外，不是默认回退
- [x] 本 Issue 不授权设计实现、Kimi 调用、Provider 行为或 Goal closure
