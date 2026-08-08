# Goals

本目录保存待接受、已激活和已完成的长期 Goal。Goal 是执行计划，不替代 Accepted Decision、RFC、产品规格、Architecture 或 Testing Strategy。

## 状态

- `PROPOSED`：策划文本可审查，但不得创建实现 Issue 或开始编码；
- `ACCEPTED / NOT ACTIVE`：内容已接受，仍有明确 Readiness 阻塞；
- `ACTIVE`：全部前置 Gate 已闭合，按里程碑持续执行；
- `BLOCKED`：满足项目阻塞规则，记录证据与恢复条件；
- `COMPLETE`：全部完成标准满足且 Goal 级最终 Review 通过。

当前 Goal：

- [端到端演示 MVP-0 Goal](end-to-end-demo-mvp0-goal.md) — `PROPOSED / NOT ACTIVE`

Goal 激活与长期自主执行遵守 [DEC-072](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md)。实现任务使用准确自定义 Agent `luna-worker`，实现者不得最终批准或合并自己的 PR。
