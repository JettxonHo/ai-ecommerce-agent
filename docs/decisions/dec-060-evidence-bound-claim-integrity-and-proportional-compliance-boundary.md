# DEC-060：采用证据约束的声明完整性边界，不建设通用合规引擎

## Type

Product / Claim Integrity / Evidence / Proportional Risk Control

## Status

Accepted

## Decision

首个 Goal 只处理与当前商品资料、证据关系和 Brief 诚实性直接相关的声明完整性，不建设通用法律或平台合规引擎。

### 声明与证据边界

- 有直接、有效证据支持的 Verified Fact 可以作为 Proof Point；
- 只有商品页或用户资料自述、但缺少必要检测、认证或独立支持的内容，必须保持 `documented_claim / claim_to_verify` 语义，不得提升为已验证事实；
- 无依据绝对化、功效、认证或贬低式比较声明不得进入 Current Brief；
- 如果移除、降级或改写该声明后仍能形成诚实、可用的 Brief，系统继续任务，并在 Review 中显示风险、证据限制和建议动作；
- 只有当前策略本身必须依赖该声明、且没有可信替代表达时，才进入 Needs Input，并遵守 DEC-059 的有限结构化行动请求模型；
- Human Review 仍保留最终业务判断权，但不得把未经验证声明批准成 Verified Fact，也不得绕过 Prohibited Claims。

### 明确不承担的能力

系统不宣称提供法律意见、实时法规判断、平台审核保证或最终发布许可。首个 Goal 不建设：

- 全品类或多法域法规库；
- 自动法律分类器或独立 Compliance Agent；
- 主动联网抓取法规、平台政策或审核案例；
- 泛化风险词库、规避变体穷举或机械合规总分；
- 对最终小红书正文的自动合规审核，因为最终正文不在首个 Goal 范围内。

用户提供或项目已接受的品牌约束、禁用表达、必要免责声明和版本化平台政策快照，仍可作为结构化约束进入 Brief 与 Adapter；它们不构成系统的法律保证。

## Alternatives Considered

### P-45B：广泛自动化合规门禁

- 优点：表面覆盖更多品类和平台规则。
- 缺点：依赖持续更新的规则来源、法域判断、敏感品类分类和专业验证，超出本地演示边界，并易产生过度阻断或错误保证。
- 结论：不采用。

### P-45C：完全交给人工审核，不设置确定性声明边界

- 优点：实现要求最少。
- 缺点：可能允许无依据声明进入 Brief 草稿，并破坏 Fact、Claim、Proof Point 和 Evidence 的既有契约。
- 结论：不采用。

## Reason

项目必须保护事实与对外声明的核心可靠性，但不是安全攻防论文或法律合规产品。按声明本身是否有证据、是否会污染 Current Brief、是否存在诚实替代表达来决定阻断范围，能够保护核心结果，同时遵守 DEC-039 的适度校验原则。

## Impact

- 高风险表达默认阻断相关声明进入 Current Brief，而不是机械阻断整个 Task。
- Fact Extraction、Marketing Brief 与 Xiaohongshu Adapter 必须传播 Claim / Evidence / Prohibited Claims 边界，不得把 Claim 升格为 Fact 或通过平台表达规避限制。
- Testing Strategy 只覆盖代表性的 Verified Fact、Claim-to-verify、可降级禁用声明和确需 Needs Input 的策略依赖场景，不建设法规矩阵或低概率变体集合。
- RFC-004 负责冻结用户可见风险、Needs Input 和 Brief 限制的公共传输契约；RFC-005 负责证据关系；RFC-007 只记录与运行相关的必要可观测信息，不记录敏感正文或构建合规平台。
- 本决定不接受任何 RFC，不提供法律意见，不授权业务实现、联网抓取、规则库、Technical Spike 或 Goal 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-004、RFC-005、RFC-007；均仍待策划与用户接受。

## Supersedes

None.

## Amends

- [DEC-007](dec-007-single-review-node-and-exception-pauses.md)：将“高风险表达可触发暂停”收紧为证据约束、声明级阻断优先，只有没有可信替代表达且策略依赖该声明时才进入 Needs Input；
- [DEC-026](dec-026-product-intake-and-fact-extraction-skill-contract.md)：补充 Documented Claim / Verified Fact 分类后的产品响应，不改变零无来源事实和关键事实冲突暂停；
- [DEC-030](dec-030-marketing-brief-generation-skill-contract.md)：补充 Prohibited Claims 的声明级阻断和任务继续边界；
- [DEC-031](dec-031-xiaohongshu-brief-mapping-adapter-contract.md)：将平台风险处理限制在已提供或已接受的版本化约束，不授权通用平台合规引擎。

## Notes

用户于 2026-08-07 明确接受 `P-45A`。Issue #52 / Draft PR #53 负责本决定与 Product Current Truth 的归档。
