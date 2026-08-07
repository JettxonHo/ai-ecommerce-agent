# DEC-064：采用窄 Task 读模型、显式恢复命令与不可变 Human Review 协议

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-07
- **Decision Type:** API Architecture / Task Navigation / Recovery / Human Review
- **Source:** Session-003；用户明确接受 `P-51A / P-52A / P-53A`
- **Related Issue:** [#54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54)
- **Related PR:** [#55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)（Draft；RFC-004 仍在策划）

## Context

[DEC-063](dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md) 已冻结 Contract-first Resource / typed Command、语义 revision、项目定义的幂等语义、耐久异步接受与 Run Monitor 基础。RFC-004 仍需把最小最近任务入口、真实 Needs Input、Source 变化、取消 / 恢复 / 重跑和 Human Review 映射为可生成、可恢复且不会把业务状态机移到浏览器的公共协议。

## Decision

### 1. Synchronous Task Creation + Bounded Recent Index + Narrow Task Overview

- `POST /api/v1/tasks` 只创建 Task identity 与初始上下文，不隐式启动 Workflow。首次成功返回 `201 Created`；同一 `Idempotency-Key` 与同一输入重放返回 `200 OK` 和同一 Task identity。
- `GET /api/v1/tasks` 只提供固定工作区内、由服务端限制数量的最近任务窗口。首个 Goal 不建设全文搜索、高级筛选、批量、归档、统计、完整历史或 Dashboard。
- `TaskSummary` 只表达 Task identity、显示名称、品类、当前阶段或等待语义、权威更新时间、Task revision、Primary Action 与绑定该 revision 的小型 Capability allowlist。
- `TaskOverview` 是窄导航投影，包含生命周期、Stage summaries、活动或最近 Run reference、当前 Needs Input / Review reference、Current Truth result references、Primary Action 与 Capability；不嵌入完整 Source、Evidence、Run history、Review 或 Brief 正文。
- Frontend 通过独立 Resource Query 读取当前 Panel 需要的正文，并派生私有 `WorkbenchProjection`。空列表是正常 `200`；不存在 Task 是 typed `404`。

### 2. Revision-bound Needs Input + Explicit Preview / Confirm + Run Commands

- 当前真实阻断通过 task-scoped `NeedsInputActionRequest` 表达。它具有稳定 identity、revision、阻断原因、受影响阶段、可见 Source / 冲突值 references、允许的 typed resolutions、预计恢复范围和当前状态；上游变化后旧请求变为 superseded，不可继续提交。
- Resolution 使用与请求类型匹配的 discriminated payload；自由文本只能补充说明，不能成为唯一不可追踪的业务事实。Resolution 先同步提交，只有服务端重新计算并返回 `resume` / `rerun` Capability 后，客户端才可继续对应命令。
- Source Association remove / replace 使用无副作用 Preview 与 typed Confirm。`SourceChangeBasis` 绑定 Task revision、Source Association revision、Source Version identity，以及实际受影响的 Stage、Current Truth、Review Package 与 Brief version / revision references；Confirm 时任一适用 Basis 已变化即返回 typed conflict，且不提交部分变更。
- `cancel` 明确针对当前 Run；耐久接受只表示 `cancellation_requested`，不表示取消已完成。
- `resume` 只用于服务端确认可兼容继续的 execution context；每次 Resume 都创建新的 Run identity 与 Attempt，并引用来源 Run。`confirmed-rerun` 携带 Task revision、最早重跑 Stage 与用户已查看的影响集合，也创建新的 Run identity。两者不得复用旧 Run 或混成模糊 `retry`。
- Manual Recovery 只公开与已接受 Recovery Decision 对应的少量 typed Commands；Checkpoint、Lease、Fencing Token、Worker Attempt 与内部恢复枚举不进入公共请求。

### 3. Immutable Review Package + Revision-safe Draft + Explicit Outcomes

- `ReviewPackage` 是按 Review identity 与 Package Version 读取的不可变审核输入快照；上游变化后旧 Package 被 supersede，并创建新 Package。
- 每个当前 Package 最多有一个 active `ReviewDraft`。Draft 使用 revision-guarded full structured snapshot `PUT` 自动保存，不使用 JSON Patch。首次保存以 `expectedRevision = 0` 创建；后续保存携带当前 revision。陈旧保存返回 typed `409`，不覆盖较新 Draft。
- Candidate select / edit / merge / reject 只是 Draft 内容与 provenance，不等于批准。`submit`、`request-more-information`、`reject-all-and-request-regeneration` 与 `withdraw-approved-strategy` 是不同的 typed Outcome Commands。
- `submit` 原子创建不可变 Review Decision、Approved Strategy Domain Version、Current Truth / Stage updates、Audit、幂等结果与唯一 Durable Resume Work Intent。首次返回 `201 Created` 的主结果和 continuation Receipt / 新 Run Monitor；同输入重放返回 `200 OK` 的同一完整结果，不重复调度。客户端不得再发送第二个 Resume Command。
- `request-more-information` 同步记录审核结果并创建或关联 Needs Input，不创建 Approved Strategy 或 Work Intent。
- `reject-all-and-request-regeneration` 原子记录拒绝、幂等结果与唯一 Durable Work Intent；首次返回 `202 Accepted` 的新 Run Receipt，同输入重放返回 `200 OK` 同一 Receipt。
- `withdraw-approved-strategy` 保留历史、清理 Current Truth、失效下游并创建新 Review Cycle，但不自动重跑。
- Review Package、Draft、Decision 与 Approved Strategy 的 identity、Package Version、Domain Version 和 mutable revision 始终分离。

## Alternatives Considered

### Expanded Task Mega-payload or Fully Frontend-composed Navigation

把下游正文嵌入 Task Overview 会产生重复和新鲜度冲突；完全取消 Overview 则迫使浏览器从多个不同时间点的响应推断业务状态。两者均不采用。

### Generic Recovery Dispatcher or Frontend-orchestrated Recovery

通用 `actionType + payload` 会隐藏不同命令的真实前置条件；由 Frontend 编排 Source mutation、Resume 与 Rerun 会把恢复状态机移到浏览器。两者均不采用。

### JSON Patch or Public Review Operation Log

JSON Patch 增加数组、合并与冲突复杂度；公开操作日志会把单人审核扩大为 Event Editing / Collaboration Protocol。首个 Goal 没有相称收益，因此均不采用。

## Reason

该组合为跨会话任务返回、阻断恢复和 Human Review 提供足够明确的公共协议，同时保持 Task 为窄导航主轴、服务端为业务状态权威、正式结果为不可变版本。它让浏览器只执行服务端允许的动作，不需要推断恢复顺序、覆盖较新 Draft 或发出重复 Resume，也没有引入 Dashboard、通用命令总线、JSON Patch 语言或多人协作模型。

## Consequences

- RFC-004 后续必须冻结 Brief / Export、Problem taxonomy、固定工作区身份与最终 OpenAPI Closure。
- RFC-005 继续拥有 Source 内容、Source / Fragment / Evidence schema、处理生命周期和 Retrieval transport；DEC-064 只拥有 Task-facing Source command basis 与公共结果映射。
- Contract / Application / Persistence / Frontend 测试必须覆盖 Task 创建重放、窄最近列表、revision-bound Capability、Needs Input supersession、Source Preview / Confirm 冲突、Cancel requested、Resume 新 Run、Review Draft stale save、Submit 原子 continuation 和各审核 Outcome 的不同副作用。
- OpenAPI Artifact、API Handler、Frontend Client、数据库记录、迁移与测试均尚未实现。

## Relationships

- **Concretizes [DEC-059](dec-059-targeted-needs-input-action-request-model.md)：** 将有限行动请求映射为 revision-bound Resource 与 typed Resolution。
- **Concretizes [DEC-061](dec-061-task-scoped-private-material-and-reversible-removal.md)：** 将可逆 remove / replace 映射为 Preview / Confirm，不改变物理删除边界。
- **Concretizes [DEC-062](dec-062-minimal-recent-task-index-and-stable-deep-links.md)：** 冻结最小 Task Index 与窄 Task Overview。
- **Concretizes [DEC-046](dec-046-review-brief-and-export-product-contract.md) / [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：** 冻结 Review Package、Draft revision、Outcome 与 continuation transport；不改变产品语义组。
- **Extends [DEC-063](dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md)：** 在其 Resource / Command、revision、idempotency 与 Run 基础上闭合 RFC-004 DQ-04～06。
- **Input to [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md)：** 接受 DQ-04～06；DQ-07～10 与 RFC 整体仍待后续 Gate。

## Authorization Boundary

本决定只授权 Decision、RFC、Current Truth、Readiness、Testing 与 Traceability 文档同步：

- 不接受 RFC-004 整体；
- 不授权创建 OpenAPI Artifact、Schema、API Route、Handler、Frontend Client、Database Record、Migration 或 Test Implementation；
- 不授权安装依赖、执行 Technical Spike、业务实现、生产实现或长期 Goal；
- DQ-07～10、Final Consistency Review 与用户 RFC 整体接受仍是后续 Gate。

## Accepted From

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-51A、P-52A、P-53A；用户于 2026-08-07 明确回复“接受 P-51A、P-52A、P-53A”。
- [RFC-004 Draft](../rfcs/rfc-004-api-and-human-review-architecture.md)。
- GitHub：[Issue #54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54) / [Draft PR #55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)。
