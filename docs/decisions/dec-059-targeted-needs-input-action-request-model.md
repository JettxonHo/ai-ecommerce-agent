# DEC-059：Needs Input 采用由当前真实阻断派生的有限结构化行动请求

## Type

Product / Interaction / Needs Input / Recovery

## Status

Accepted

## Decision

Needs Input 不采用不断扩张的固定问卷，也不退化为无结构聊天。系统只针对当前已经存在的真实阻断，生成有限、可操作的结构化行动请求。

每项行动请求必须让用户理解：

- 缺少或冲突的业务信息；
- 该问题为什么阻断当前阶段；
- 当前可见来源、Source Version、可用定位或冲突值；
- 用户可以执行的补充、选择、纠正、确认或取消动作；
- 动作完成后将恢复、重试或重跑的阶段范围。

行动请求只能基于已有 Task、Source、Conflict、Stage 与业务上下文，不得补造外部事实。非阻断的增强或可选资料继续作为建议呈现，不得伪装成必填项；同一阻断已有代表性请求后，不为基本不可能出现的变体反复增加问题。

用户的结构化补充或裁决必须进入既有 Source / Domain Version 与审计边界。聊天记录不是事实来源，系统不得通过自由对话绕过版本、证据、冲突或恢复契约。

“Needs Input”及上述字段是产品交互语义。最终公共 Resource、字段名、状态、错误码、revision、动作枚举和传输由 RFC-004 冻结；Source、Locator 与 Evidence 表达由 RFC-005 冻结。

## Alternatives Considered

### P-44B：完整品类问卷

- 优点：字段覆盖统一，表单结构直观。
- 缺点：把增强资料和低概率缺失机械化为强制项，违反最低可运行门禁与适度校验原则。
- 结论：不采用。

### P-44C：自由聊天追问

- 优点：表达灵活，前期字段设计较少。
- 缺点：聊天会成为不可追踪的事实来源，冲突裁决、版本、恢复和自动化验收难以可靠实现。
- 结论：不采用。

## Reason

目标用户需要知道为什么流程停止以及如何继续，而不是完成一张与当前问题无关的长问卷。由真实阻断派生的有限行动请求能延续两级门禁、分级冲突与行动导向恢复，同时保持结构化状态和可测试性，不建设通用聊天状态机。

## Impact

- PRD、MVP Scope、User Flows、Frontend Architecture、RFC-004 / 005、Testing Strategy 与 Goal 必须采用该行动请求模型。
- 测试至少覆盖缺失最低条件、阻断性冲突、非阻断资料建议、补料或裁决后的正确恢复，以及不得从自由聊天或虚构来源形成 Current Truth。
- 产品 UI 必须显示原因、影响、来源 / 冲突值、允许动作和恢复范围；具体组件和传输字段仍由 Frontend Architecture / RFC 冻结。
- 本决定不创建通用问卷、聊天页面、公共 API 或实现，不授权 Technical Spike、业务实现或 Goal 创建 / 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-004、RFC-005；本决定不接受其技术方案。

## Supersedes

None.

## Amends

- [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)：具体化 Needs Input 所需补充或确认内容，不改变两级门禁和确认式局部重跑。
- [DEC-045](dec-045-minimum-input-file-limits-and-conflict-handling.md)：具体化阻断性缺失或冲突的用户行动，不改变最低输入、文件限制和冲突分级。
- [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：具体化补料继续和冲突裁决的行动结构，不改变阶段进度或其他恢复语义。

## Does Not Amend

- DEC-041：聊天记录不作为业务 Current Truth，且首个演示仍不建设登录、多租户或主动联网研究。
- DEC-039：只覆盖真实阻断和代表性分支，不扩展为泛化防御问卷。

## Notes

用户于 2026-08-07 明确接受 `P-44A`。Issue #52 / Draft PR #53 负责本决定和产品流程的归档。
