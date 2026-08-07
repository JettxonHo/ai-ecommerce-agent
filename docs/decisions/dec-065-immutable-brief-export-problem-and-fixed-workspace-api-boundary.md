# DEC-065：采用不可变 Brief / Export、有限 Problem Catalog 与固定工作区 API 边界

## Metadata

- **Status:** Accepted — Extended by [DEC-066](dec-066-openapi-contract-catalog-compatibility-and-generated-client-adoption.md)
- **Date:** 2026-08-07
- **Decision Type:** API Architecture / Brief and Export / Error Contract / Local Transport Boundary
- **Source:** Session-003；用户明确接受 `P-54A / P-55A / P-56A`
- **Related Issue:** [#54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54)
- **Related PR:** [#55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)

## Context

[DEC-063](dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md) 与 [DEC-064](dec-064-task-recovery-and-human-review-public-protocol.md) 已冻结公共 Contract、语义并发、Task、恢复和 Human Review 主协议。RFC-004 仍需把不可变 Brief、版本比较、用户导出、可执行错误恢复，以及本地固定工作区的真实传输边界映射为稳定公共协议，同时避免建设文档平台、内部异常目录或伪多租户认证。

## Decision

### 1. Immutable Brief Resources + Typed Revision + Confirmed Markdown Export

- `MarketingBriefVersion` 与 `XiaohongshuBriefVersion` 是独立的不可变 Resource family；Task Overview 的 Current Truth references 是发现当前有效结果的唯一入口。按稳定 Version identity 读取历史不会使旧版本重新成为 Current Truth。
- 同一 Task、同一 Brief family 的两个版本可以请求无副作用的 `BriefComparison`。Comparison 按产品语义组和 field path 表达 before / after、来源、编辑意图与确定性阶段影响，但不是新业务版本、审计权威或字段级依赖图。
- 用户编辑使用 family-specific typed `revise` Command，携带 base Version、Task revision、`business_change` 或 `presentation_polish` intent 与 `Idempotency-Key`。服务端仍复核 Strategy / Brief lock、Evidence 与 Claim boundary；intent 不能绕过业务约束。
- Marketing Brief 的业务修改创建新不可变版本、更新 Current Truth 并使当前 Xiaohongshu Brief 失效；Xiaohongshu Brief 的业务修改只创建自身新版本。展示性润色同样创建可追踪版本，但不触发业务重跑。
- 导出采用无副作用 `ExportPreview` → typed `confirm-export`。Preview 绑定 Task revision、Brief family / Version、必要上游、Hypotheses、Evidence Limitations、Risks 与导出范围；Confirm 时任一适用 basis 已变化即返回 conflict。
- Confirm 首次成功同步创建不可变 `ExportSnapshot` 并返回 `201 Created`；同 Key / 同输入重放返回 `200 OK` 同一 Snapshot。Snapshot 不改变 Current Truth，也不使用 Hash、SHA-256 或 Digest。
- 每个 Snapshot 只含一个当前有效 Marketing Brief 或 Xiaohongshu Brief，使用固定 UTF-8 Markdown 模板。无适用内容诚实显示“无 / 不适用”，不得为填满模板制造事实。
- 下载使用 `text/markdown; charset=utf-8` 与 attachment disposition；文件名为 `task-{taskId}-{briefKind}-v{versionNumber}-{exportedAtUtc}.md`，时间采用 `YYYYMMDDTHHMMSSZ`。Snapshot 后续不随 Current Truth 改变，物理保留 / 清理由 ARP-08 与 Development Plan 冻结。

### 2. RFC 9457 + Small Stable Problem Catalog

- 所有 4xx / 5xx 使用 RFC 9457 `application/problem+json`；机器行为只依赖稳定 Problem `type` 与窄型扩展，不解析 `title` / `detail` 文案。Problem Type 使用部署无关的项目 URN。
- 公共目录只包含会真实改变客户端行为的类型：`malformed-request` (`400`)、`not-found` (`404`)、`payload-too-large` (`413`)、`unsupported-media-type` (`415`)、`validation-failed` (`422`)、五类 typed `409` conflict、真实 HTTP `rate-limited` (`429`)、`internal-error` (`500`) 与 `service-unavailable` (`503`)。
- `409` 类型为 `revision-conflict`、`idempotency-conflict`、`superseded-resource`、`capability-conflict` 与 `operation-in-progress`。扩展只携带安全恢复所需的 current Resource / revision / Version reference、冲突字段或 basis summary。
- 客户端动作只使用 `correct_input`、`refresh`、`refresh_and_compare`、`open_current`、`retry_later`、`contact_operator` 或 `none`。不存在 arbitrary metadata bag、内部 Validator dump 或机械 Rubric 分数。
- `operation-in-progress` 只表示尚无可重放结果的并发窗口。已提交的同 Key / 同输入必须重放既有结果；可合理估计时才为 `429`、`503` 或 in-progress conflict 返回 `Retry-After`。
- Needs Input、waiting Review、manual recovery、cancellation requested、failed Run、superseded result 与 Evidence Limitation 是正常 Resource state，不伪装为 HTTP Problem；成功读取 failed Run 仍返回 `200`。
- Exception、SQLSTATE、Provider payload、Secret、Checkpoint 与 Worker internals 不进入公共错误。Trace / correlation reference 可以是安全可选扩展，其生成、Redaction 与运维语义归 RFC-007。

### 3. Server-bound Fixed Workspace + Loopback Same-origin Transport

- 首个 Goal 只有一个由本地配置选择的固定 Workspace。Workspace identity 由服务端请求上下文注入；Browser 不提交或选择任意 `workspaceId`，也不能凭 Task ID 改变 scope。
- 所有 Resource / Command 由服务端限定在固定 Workspace；不存在或不属于当前 scope 的 identity 统一返回 `404`。公共 DTO 不暴露内部 scope key，也不预先设计 Tenant selector。
- Browser 只使用同源 `/api/v1`；API 默认绑定 loopback，CORS 默认关闭。本地演示 HTTP 不声称支持公网、远程用户或 TLS 部署。
- Browser state-changing request 使用明确 JSON / multipart Contract；请求带 `Origin` 时必须匹配配置的本地 Workbench origin，不接受 cross-origin simple-form mutation 作为替代传输。
- 首个 Goal 不建设注册、登录、Cookie / Token、API Key、CSRF Token、RBAC、多人审核或 Tenant membership。Audit actor 是服务端拥有的固定受控上下文，不信任客户端自报身份或角色。
- Provider / Database Credential 不成为 Browser API 身份。任何非 loopback 绑定、公开部署、第二 Workspace、远程用户、共享环境或真实权限区分都触发新的 Product / Security / API Decision Gate；本决定不得被描述为公网认证方案。

## Alternatives Considered

### Mutable Current Brief or Asynchronous Multi-format Export Platform

覆盖式 Current Brief 无法可靠解释版本、失效和已下载文件；异步 Markdown / JSON / PDF Job 则引入不必要的新状态机、格式契约、对象存储与保留范围。两者均不采用。

### Free-text-only Errors or Exhaustive Internal Error Enumeration

只返回文案会迫使 Frontend 解析文字；穷举内部异常则泄漏实现、扩大兼容承诺并制造大量客户端无法处理的分支。两者均不采用。

### Client-selected Workspace or Local Login / Shared Token

未认证 Workspace Header 不是授权边界；为单机演示增加 Login 或共享 Token 会产生没有真实用户模型支撑的 Credential 与权限矩阵。两者均不采用。

## Reason

该组合完整承接已接受的不可变业务版本、导出确认、行动导向恢复与受控单工作区演示边界。它为用户提供可比较、可重放、可追溯的 Brief 与 Markdown 文件，并给 Frontend 一套稳定且有限的错误动作，同时保持校验与真实风险成比例，不增加 Hash、多格式文档平台、内部异常矩阵或伪认证。

## Consequences

- RFC-004 DQ-07～09 已闭合；DQ-10 后由 DEC-066 冻结最终 Operation / Schema catalog、默认最近任务窗口、兼容规则、Generated Client adoption 与 Contract Tests。Final Consistency Review 已通过，用户已于 2026-08-07 明确接受 RFC-004 整体。
- RFC-005 继续拥有 Source / Fragment / Evidence Locator、上传与处理结果、检索和外部对象权限过滤；RFC-007 继续拥有 Retry / Poll 参数、Trace / correlation、Redaction 与运维阈值。
- Contract / Application / Frontend / Browser Tests 必须覆盖 Brief Current Truth、版本比较、revise 影响、Export Preview conflict、Snapshot 重放、Problem action、正常业务状态非 Problem、fixed-workspace scope 与 same-origin write boundary。
- OpenAPI Artifact、API Handler、Frontend Client、数据库记录、导出文件实现与测试均尚未创建。

## Relationships

- **Concretizes [DEC-046](dec-046-review-brief-and-export-product-contract.md) / [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) / [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)：** 将 Brief 版本、比较、影响和 Markdown 导出映射为公共协议。
- **Concretizes [DEC-041](dec-041-end-to-end-demo-mvp-delivery-envelope.md) / [DEC-061](dec-061-task-scoped-private-material-and-reversible-removal.md)：** 明确本地固定工作区与物理数据生命周期之间的边界。
- **Extends [DEC-063](dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md) / [DEC-064](dec-064-task-recovery-and-human-review-public-protocol.md)：** 闭合 RFC-004 DQ-07～09，不改变既有 Resource / Command、revision、idempotency、Run、Task、Recovery 或 Review 协议。
- **Input to [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md)：** DQ-10 后由 DEC-066 接受，Final Consistency Review 已通过；用户已于 2026-08-07 明确接受 RFC-004 整体。

## Authorization Boundary

本决定只授权 Decision、RFC、Current Truth、Readiness、Testing 与 Traceability 文档同步：

- 不接受 RFC-004 整体；
- 不授权创建 OpenAPI Artifact、Schema、API Route、Handler、Frontend Client、Export Implementation、Database Record、Migration 或 Test Implementation；
- 不授权安装依赖、执行 Technical Spike、业务实现、生产实现或长期 Goal；
- DQ-10 后由 DEC-066 接受，Final Consistency Review 已通过；用户 RFC 整体接受仍是后续 Gate。

## Accepted From

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-54A、P-55A、P-56A；用户于 2026-08-07 明确回复“接受 P-54A、P-55A、P-56A”。
- [RFC-004 Draft](../rfcs/rfc-004-api-and-human-review-architecture.md)。
- GitHub：[Issue #54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54) / [Draft PR #55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)。
