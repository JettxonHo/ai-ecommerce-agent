# DEC-073：采用 MVP-0 最小可观测性与运行期运维契约

## Type

Architecture / Observability / Runtime Operations

## Status

Accepted

## Decision

用户接受 RFC-007 的推荐组合 `P-68A + P-69A + P-70A`，并接受 RFC-007 整体：

- 使用 allowlisted JSON Lines、服务端生成的 `correlation_id`、耐久 `RuntimeErrorRecord` 与安全的公共 correlation reference；日志不是业务事实源。
- 每个技术边界只有一个 Timeout / Retry / Backoff owner，继承 RFC-002 / 003 / 006 的预算；OpenAI SDK 保持 `max_retries=0`，不叠加无限重试。
- MVP-0 只交付本地运行时间线、失败摘要和 Release Evidence Summary；OpenTelemetry、Collector、Dashboard、Pager、Circuit Breaker 平台后移。
- Secret、Prompt、Source / 评论正文、Header 与 Provider payload 不进入日志或耐久错误记录；采用正向 allowlist 和代表性边界测试，不建设通用 DLP / Redaction 引擎。

RFC-007 DQ-01～03 均关闭，RFC-007 状态升级为 `ACCEPTED`。

## Reason

该组合足以支持本地异步 MVP 的故障定位、恢复与验收，同时避免为了演示提前建设生产级遥测平台。它沿用既有身份、错误、事务和模型恢复契约，不形成第二公共错误协议或第二业务事实源。

## Impact

- API、Worker、Workflow、Retrieval 与 Model Runtime 必须传播同一关联链并遵守 payload allowlist。
- 技术 Retry、Intentional Rerun 和用户重试保持不同身份语义。
- 完整遥测平台、长期日志保留、告警与 SLO 不进入 MVP-0。
- 实现与测试在已接受 MVP-0 Goal 内按独立 Issues 完成；本决定不降低任何已有质量门禁。

## Related

- [RFC-007](../rfcs/rfc-007-observability-and-runtime-operations.md)
- [RFC-007 Pre-acceptance Review](../reviews/review-2026-08-08-rfc-007-preacceptance-consistency.md)
- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Source

用户于 2026-08-08 明确回复：“接受 P-68A、P-69A、P-70A 与 RFC-007 整体”。
