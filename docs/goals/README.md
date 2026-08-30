# Goals

本目录保存待接受、已激活和已完成的长期 Goal。Goal 是执行计划，不替代 Accepted Decision、RFC、产品规格、Architecture 或 Testing Strategy。

## 状态

- `PROPOSED`：策划文本可审查，但不得创建实现 Issue 或开始编码；
- `ACCEPTED / NOT ACTIVE`：内容已接受，仍有明确 Readiness 阻塞；
- `ACTIVE`：全部前置 Gate 已闭合，按里程碑持续执行；
- `BLOCKED`：满足项目阻塞规则，记录证据与恢复条件；
- `COMPLETE`：全部完成标准满足且 Goal 级最终 Review 通过。

当前 Goal：

- [MVP-0L Local AI Web App Delivery Goal](mvp0-local-ai-web-app-delivery-goal.md) — `TERMINAL_INCOMPLETE_L5_FAILED`（L0–L4 preserved；L5 `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` / no exports；L6 `NOT_EXECUTED`；Agent UI frozen）
- [Real Product-to-Brief Pilot Goal](real-product-to-brief-pilot-goal.md) — `ACTIVE` under [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md); Issue #341 P0 is `CONTRACT_FREEZE_PENDING` with P01–P08 `ADMISSION_PENDING_REVIEW` and denominator `FREEZE_PENDING_REVIEW` before this record reaches `main`, then `P0_CONTRACT_FROZEN` with exact denominator 8 and P1 `READY_NOT_STARTED` once present on `main`（[P0 plan](../product/real-product-to-brief-pilot-p0-plan.md)）
- [MVP-0P Local Action Workbench Productization Goal](mvp0-local-action-workbench-productization-goal.md) — historical `MVP0P_GOAL_COMPLETE`
- [MVP-0 Fast Lane Goal](mvp0-fast-lane-goal.md) — historical terminal `GOAL_BLOCKED`

Goal 激活与长期自主执行遵守 [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md)。实现任务使用准确自定义 Agent `luna-worker`，实现者不得最终批准或合并自己的 PR。
