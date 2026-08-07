# DEC-041：冻结本地端到端演示 MVP 的交付边界

## Type

Product / Scope / Delivery

## Status

Accepted — Amended by DEC-044 / DEC-061

> **Current amendments:** [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md) 将本决定的“引导式任务工作台”具体化为单任务工作台、两级输入门禁与确认式局部重跑交互；[DEC-061](dec-061-task-scoped-private-material-and-reversible-removal.md) 补充受控单工作区的 Task 范围资料与可逆移除体验，不引入登录、RBAC、多租户或用户侧永久删除。二者均不扩大演示交付边界。

## Decision

首个长期 Goal 的交付目标是一个**本地可复现的端到端演示 MVP**。它面向受控单工作区中的电商商品运营与内容运营人员，以引导式任务工作台完成商品资料输入、事实与洞察生成、定位、人工审核、通用 Marketing Brief 和小红书 Brief 映射闭环。

### In Scope

- 受控单工作区；不建设登录系统，以固定工作区身份完成演示。
- 引导式任务工作台；聊天记录不作为业务 Current Truth。
- 用户提供的结构化表单、文本、TXT、Markdown、文本型 PDF 和评论 CSV。
- 四层结构化 Brief、单一关键 Human Review、证据追溯、版本失效、恢复和局部重跑。
- 一个真实 LLM Provider 与一个确定性测试替身。Provider、模型和具体 SDK 由 RFC-006 决定，本 DEC 不作选择。
- 以明确标注的 JTBD / Persona 假设支持演示；真实用户访谈是 Beta 前门禁，不是本地演示的前置条件。

### Out of Scope

- 公开部署、账号注册、计费、多租户、多人协作与复杂权限系统；
- 自动网页抓取、竞品监控、评论抓取和主动联网研究；
- OCR、图片理解、扫描文档和广泛办公文件解析；
- 完整小红书正文、图片或视频生成、自动发布；
- Multi-Agent、LLM Supervisor、多 Provider 容灾；
- 销量预测、广告、库存、客服和店铺诊断。

### Success Boundary

演示成功以端到端流程可靠、用户能够理解并审核结果、证据可追溯、错误可恢复和本地启动可复现为主，不以机械评分、销量承诺或大规模生产运维指标作为本阶段验收标准。

## Reason

该边界能验证项目最核心的业务价值和可靠性闭环，同时避免将认证、抓取、多媒体、Multi-Agent 或生产运营能力提前带入首个 MVP。

## Impact

- 产品规格、架构 RFC、公共契约、测试策略和 Goal 必须以此交付边界为准。
- 未列入 In Scope 的能力不得由单个 Issue 或实现 PR 擅自加入。
- 产品主信息架构与重跑交互已由 DEC-044 冻结；最终字段、详细控件、框架与 Provider 仍需后续 Decision Gate，本决定不自行补全。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-001、RFC-002；后续 RFC-003 至 RFC-007。

## Supersedes

None.

## Amends

DEC-004、DEC-005、DEC-006、DEC-010、DEC-020 与 DEC-021：在不推翻其原则的前提下，补充并收紧首个端到端演示的交付范围。

## Amended By

[DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)、[DEC-061](dec-061-task-scoped-private-material-and-reversible-removal.md)

## Notes

本决定冻结交付包络，不授权创建或启动实际 Goal。
