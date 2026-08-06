# DEC-039：采用与真实风险相称的校验与审阅治理

## Type

Governance / Quality / Security

## Status

Accepted

## Decision

本项目的安全校验、异常处理、测试与 Review 必须服务于真实产品风险和核心功能，不以堆叠防御性规则作为质量目标。

具体约束如下：

1. 校验强度依据问题发生可能性、影响、可恢复性和回归价值决定。项目不是安全攻防论文，不建设超出演示 MVP 风险面的泛化安全工程。
2. 不新增哈希或 SHA-256 要求。仅当存在影响核心功能的重大完整性或安全风险时，才允许提交独立提案，并说明威胁、必要性、替代方案和成本。既有 `fingerprint`、内容身份等概念保持算法中立。
3. 在代表性正常路径、合理错误路径和关键业务不变量已有覆盖后，不继续为基本不可能发生的变体反复增加防御代码或测试。
4. Rubric 只用于帮助 Reviewer 形成专业判断，不作为机械评分、自动接受器或为了凑分而扩张范围的依据。
5. 本决定不取消必要的边界校验、Secret 保护、权限边界、事务一致性、故障恢复和关键行为测试；这些措施仍按变更相关性执行。
6. 若本决定改变既有 Accepted Decision、RFC 或规格，只能通过显式 `Amends` / `Supersedes` 关系同步，不得静默重写历史。

## Reason

用户明确要求避免过度防御、非必要哈希、低概率 Case 堆叠和机械 Rubric。该约束能让有限的开发与审阅成本集中在端到端闭环、数据一致性、恢复、人工审核和证据追溯等真正影响 MVP 的风险上。

## Impact

- Readiness Artifact、Technical Spike、测试策略和 PR Review 必须采用风险相关的最小充分证据。
- Security 与 Performance 轴仍保留，但只检查与当前变更相关的内容。
- 不得以本决定为理由绕过 Required Checks、隐藏失败测试或降低已接受的关键不变量。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-001、RFC-002；后续 RFC-003 至 RFC-007 必须遵守本决定。

## Supersedes

None.

## Amends

DEC-034、DEC-035 与 DEC-038 的未来校验治理：保留其关键可靠性 Gate，仅要求后续证据与真实风险相称。

## Notes

本决定不授权 Technical Spike 执行或业务实现。
