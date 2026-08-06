# DEC-040：采用分级自主执行权限与固定模型角色

## Type

Agent Governance / Git and GitHub Operations / Model Roles

## Status

Accepted

## Decision

项目采用“普通工作自主闭环、高风险事项人工 Gate”的 Agent 执行模式，并按任务性质固定模型角色。

### 普通工作自主闭环

在对应阶段已经获得授权、需求与公共契约已经冻结、且不存在停止条件时，Agent 可以自主：

- 创建或整理 Issue，建立独立分支并完成范围内工作；
- 提交、Push、创建 Pull Request、更新 PR 描述与证据；
- 执行测试和职责范围内的自检，修复发现并重新验证；
- 对可执行代码 PR，由 Luna/max 实现并自检后，必须由 Sol/xhigh 在合并前完成独立五轴 Review；Luna 的自检不能替代该 Review；
- 在验收标准与 Required Checks 全部通过、无阻塞 Finding 后，合并普通低风险 PR、关闭 Issue，并同步进度与文档。

自主合并不等于 Agent 可以自行接受产品 Decision、RFC 或启动 Goal。

### 保留人工 Gate

遇到下列情况必须停止受影响工作并请求用户确认：

- 破坏性操作、历史重写、不可逆外部操作或生产凭证处理；
- 重大架构变更、公共契约替换、数据迁移或数据库/运行时/Provider 变更；
- 安全事故、影响核心功能的重大安全或一致性风险；
- 产品范围变化，或新增认证、多租户、联网抓取、多 Provider 等非范围能力；
- 与 Accepted Decision / RFC 冲突，或需要降低测试与验收标准才能继续。

用户继续保留 Accepted Decision、RFC Acceptance、产品范围、Goal 激活与最终发布条件的决定权。

### 模型角色

| 任务类型 | 指定模型 | 职责边界 |
|---|---|---|
| 策划、架构、RFC、复杂任务拆分、复杂诊断、PR/阶段/Goal Review | GPT-5.6 Sol，`xhigh` | 高推理工作；输出方案、拆分、风险判断和技术 Review 结论 |
| 规格冻结后的代码实现与常规修复 | GPT-5.6 Luna，`max` | 按 Accepted 文档和单一 Issue 边界实现，不临场改变产品或架构 |

若平台当时无法提供任务所要求的模型，Agent 必须暂停该类任务并报告，不得静默换用其他模型。可执行代码变更的 Review Agent 与 Implementation Agent 必须职责分离；Luna/max 的技术自审不能替代 Sol/xhigh Review、Required Checks 或必要的人类 Gate。

## Reason

普通、可逆且有完整自动化证据的工作由 Agent 闭环能降低等待成本；高风险和治理类决定仍需人工确认。固定高推理与实现角色可减少策划漂移，也能避免实现 Agent 在 Issue 内临场作出重大设计选择。

## Impact

- 长期 Goal 必须写明每个阶段的 Agent 角色、模型、权限和停止条件。
- 当前只授权策划文档工作；业务代码仍须等待完整策划包被接受并由用户明确启动 Goal。
- 当前环境若无 GPT-5.6 Luna `max`，不影响策划，但会阻塞后续代码实现，直至该模型可用或用户通过新决定修改角色。
- 低风险 PR 的自主合并权限替代旧的“一律由用户最终 Merge”规则；历史 Spike 操作记录保持不变。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-001、RFC-002；后续 RFC-003 至 RFC-007。

## Supersedes

None.

## Amends

- DEC-036、DEC-037：其 Spike-001 历史执行结果不变；未来普通低风险 PR 不再一律等待用户 Merge。
- RFC-001 DQ-09 / DQ-10 的未来 Git 合并权限与 Agent 角色：保留 Required Checks、Issue/Branch/PR 隔离和授权分离，改为分级自主合并。

## Notes

本决定不等于“进入 Goal 执行阶段”，也不授权业务代码、Technical Spike 或生产迁移。
