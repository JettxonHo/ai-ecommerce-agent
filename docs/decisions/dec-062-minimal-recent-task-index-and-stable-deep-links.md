# DEC-062：采用最小最近任务入口与稳定深链，不建设运营 Dashboard

## Type

Product / Navigation / Cross-session Recovery / Frontend Boundary

## Status

Accepted

## Decision

固定工作区提供一个最小任务入口，使用户在关闭页面或开始新会话后，不依赖自行保存 URL 即可返回持久 Task。

### 最小入口

- `/tasks` 提供创建任务和最近任务列表；
- 每个任务摘要至少表达 Task 名称或临时名称、品类、当前阶段或等待状态、最近更新时间和一个主要下一步动作；
- 选择任务后进入稳定 Task Route；Task 内 Stage / Panel 位置继续使用可链接的稳定深链；
- 最近任务入口只投影后端 Task Current Truth 与 Capability，不保存第二套业务状态，也不根据显示文案猜测动作；
- 用户从列表进入 Task 后，继续由同一个深 TaskWorkbench 承载 Intake、Progress / Recovery、Review、Results / Export 与 Evidence / Context。

### 明确不进入首个 Goal

- 全文搜索、高级筛选、复杂排序和分页优化；
- 批量操作、批量状态变更或异常队列；
- Task 归档策略、运营统计、图表或 Dashboard；
- 跨工作区切换、多人分配、权限管理或通知中心。

`/tasks` 是跨会话恢复入口，不是成熟运营控制台。RFC-004 只需冻结支持该体验的最小 List / Summary / Capability 契约，不得借机扩大为完整列表平台。

## Alternatives Considered

### P-47B：只提供稳定深链

- 优点：页面和 API 最少。
- 缺点：用户关闭页面后必须自行保存 URL，削弱任务级持久化与跨会话恢复对目标用户的实际可用性。
- 结论：不采用。

### P-47C：建设完整运营 Dashboard

- 优点：更接近成熟运营平台。
- 缺点：明显扩大首个 MVP，并引入当前没有验收依据的搜索、筛选、批量、报表和队列需求。
- 结论：不采用。

## Reason

任务级持久化和 Resume 只有在用户能够重新找到 Task 时才构成完整产品体验。一个最小最近任务入口足以支持跨会话返回，不需要提前建设完整运营 Dashboard。

## Impact

- Frontend Router 外层职责增加 `/tasks` 的匹配与最小 Task Index Composition；TaskWorkbench 的内部职责、私有投影与模块边界不变；
- RFC-004 必须冻结最小 Task List / Summary、稳定 Task Identity、更新时间、当前阶段 / 等待状态、主要下一步 Capability 与列表错误 / 空状态；
- Task Index 只读取后端 Current Truth；前端不得通过本地历史、缓存残留或文案推断任务终态；
- Browser E2E 增加“创建或发现最近 Task → 通过稳定深链返回工作台”的代表性路径，以及空列表和暂时读取失败；不建设搜索 / 分页 / 批量操作矩阵；
- 本决定不冻结最终路径参数、HTTP 字段名、分页协议、视觉组件或实现，不授权前端、API、数据库、Technical Spike 或 Goal 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-004；仍待策划与用户接受。

## Supersedes

None.

## Amends

- [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)：补充跨会话返回 Task 的最小入口，不改变单 Task 工作台的信息架构；
- [DEC-056](dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md)：将外层 Router 从仅拥有 `/tasks/new` 与稳定 Task Route，补充为还拥有最小 `/tasks` Task Index Route；TaskWorkbench 内部 Module 与 Router-thin 原则不变。

## Notes

用户于 2026-08-07 明确接受 `P-47A`。Issue #52 / Draft PR #53 负责本决定、Frontend Current Truth 与 Product Current Truth 的归档。
