# DEC-061：用户资料采用 Task 范围私有与可逆移除，不提供首个 Goal 的永久删除界面

## Type

Product / Data Scope / Source Lifecycle / Reversible Removal

## Status

Accepted

## Decision

固定单工作区中的用户资料默认只属于当前 Task 的有效资料集，不得静默提升为跨任务共享知识。商品任务证据与通用运营知识保持逻辑分离；未来若要跨任务复用用户资料，必须另立产品、权限和来源范围 Decision。

### 当前 Task 的资料纠错

- 用户可以把 Source 从当前有效资料集中移除，或用新 Source Version 替换；
- 移除或替换是可追踪的版本变化，必须显示影响预览，并遵守 Current Truth、阶段失效、陈旧审核拒绝和用户确认后的局部重跑规则；
- 被移除的 Source 及其旧版本不得继续用于新的分析，也不得继续支撑 Current Brief；
- 该产品动作不等于立即物理擦除历史文件、解析结果、Fragment、索引、Evidence Link、Checkpoint、导出或最小运行记录；
- 用户界面与导出说明必须诚实区分“已从当前任务资料集中移除”和“已物理永久删除”。

### 首个 Goal 的数据生命周期边界

首个 Goal 不建设登录、RBAC、多人权限、面向最终用户的永久删除按钮或跨存储 Purge 编排。物理保留、Hold、删除顺序、恢复保护、开发环境清理和操作员重置方式，由 ARP-08、RFC-005、RFC-007 与 Development Plan 冻结；涉及不可逆删除时仍属于人工确认 Gate。

## Alternatives Considered

### P-46B：首个 Goal 提供完整用户侧永久删除

- 优点：表面上的用户控制最直接。
- 缺点：需要跨业务数据、对象、索引、Checkpoint 与导出的删除一致性、恢复和误删保护，必须先完成 Retention / Deletion Safety 规划与验证。
- 结论：不采用。

### P-46C：用户资料默认在工作区跨任务复用

- 优点：后续任务可能减少重复上传。
- 缺点：扩大来源范围、权限、过期与跨商品污染风险，不符合受控单工作区演示的最小边界。
- 结论：不采用。

## Reason

用户需要能够纠正当前任务使用的资料，但本地演示不能把可逆业务移除伪装成已完成跨存储永久擦除。Task 范围私有与可逆移除既提供真实纠错路径，也避免在 Retention / Deletion Safety 尚未闭合前承诺不可逆能力。

## Impact

- RFC-004 需表达 Source 的当前 Task 关联、移除 / 替换 Capability、版本前置条件、影响预览与冲突响应；
- RFC-005 需冻结 Source 范围、Task 过滤、失效后 Retrieval / Evidence 行为，以及物理对象与索引的一致性边界；
- RFC-007、ARP-08 与 Development Plan 需冻结本地演示的数据保留、操作员重置和物理删除 / 清理运行手册；
- Frontend 只提供可逆的移除 / 替换交互，不得显示“永久删除”“已彻底清除”等未经实现与验证的文案；
- Testing Strategy 覆盖 Source 从当前有效集移除、影响预览、Current Truth 失效和替换后的局部重跑，不把未实现的物理 Purge 加入产品 E2E；
- 本决定不冻结数据库列、存储供应商、Retention 时长或物理删除算法，不授权 Migration、Purge、Technical Spike、业务实现或 Goal 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC and Readiness

RFC-004、RFC-005、RFC-007、ARP-08；均仍待对应 Gate。

## Supersedes

None.

## Amends

- [DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)：明确用户商品资料默认 Task-scoped，不自动进入跨任务共享知识层；
- [DEC-025](dec-025-versioned-sources-fragments-and-evidence-links.md)：冻结产品层“从当前有效集移除”与“物理永久删除”的区别，物理删除政策仍由后续权威文档决定；
- [DEC-041](dec-041-end-to-end-demo-mvp-delivery-envelope.md)：补充受控单工作区的数据生命周期体验，不引入登录、RBAC 或多租户；
- [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)：补充 Source 可逆移除 / 替换及其影响预览和局部重跑行为。

## Notes

用户于 2026-08-07 明确接受 `P-46A`。Issue #52 / Draft PR #53 负责本决定与 Product Current Truth 的归档。
