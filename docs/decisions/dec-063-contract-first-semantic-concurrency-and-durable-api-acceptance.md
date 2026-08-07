# DEC-063：采用 Contract-first Typed API、语义并发与耐久异步接受协议

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-07
- **Decision Type:** API Architecture / Public Contract / Concurrency / Idempotency / Async Processing
- **Source:** Session-003；用户明确接受 `P-48A / P-49A / P-50A`
- **Related Issue:** [#54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54)
- **Related PR:** [#55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)（Draft；RFC-004 仍在策划）

## Context

Frontend Architecture 已把已提交的 OpenAPI 3.1 Artifact 定义为前端类型生成源；RFC-002 / 003 已冻结业务 revision、幂等、Durable Work Intent、Run、取消和恢复的不变量。RFC-004 仍需把这些内部边界映射为唯一、可生成客户端、难以误用的公共 HTTP Contract，同时避免把前端私有投影、ORM、Checkpoint 或 Worker 所有权泄漏为公共协议。

## Decision

### 1. Contract-first Resource Query + Explicit Typed Command

- 实施获授权后，已提交的 OpenAPI 3.1 Description 是唯一公共 HTTP Contract；生成的 TypeScript 类型和 Client 是派生产物，不是第二事实源。
- 使用 `/api/v1` 作为首个 Goal 的单一当前主版本空间，以兼容性新增方式演进。
- 稳定查询使用明确 Resource；状态变化使用逐项命名、typed Command。客户端不得通过修改通用状态字段驱动业务迁移，也不得调用 `actionName + arbitrary payload` 的通用 Dispatcher。
- Task 是导航主轴，但不是包含全部 Source、Evidence、Review 与 Brief 正文的 mega-payload。API 提供窄 Task Overview 与独立、分别版本化的相关资源；前端 Query Adapter 组合响应并派生私有 `WorkbenchProjection`。
- 公共 DTO 不暴露 ORM Entity、UoW、Dispatch Record、Checkpoint State、LangGraph SDK Object 或 Provider SDK Object。
- CRUD 只用于真实的 Resource 创建 / 读取与 revision-guarded Draft 编辑；Start、Resume、confirmed Rerun、Cancel、Needs Input Resolution、Source Association Remove / Replace 与 Review Submit 使用显式 typed Command。首个 Goal 不建设跨模块通用 `/commands` Bus。

### 2. Semantic Preconditions + Project-defined `Idempotency-Key`

- 受保护的可变表示公开单调 `revision`；不可变 Domain Version 继续使用独立稳定身份和版本号。两者不得混用。
- 写请求只携带该业务动作真正依赖的语义前置条件，例如 Review Draft revision、基础 Domain Version 或目标 Run identity；只读操作不机械附加并发前置条件。
- 可在响应不确定后重试的非幂等 Create / Command 必须使用项目定义完整语义的 `Idempotency-Key` Request Header。项目不依赖已过期 IETF Internet-Draft 的标准状态来保证正确性。
- 同一 Scope + Key + 同一版本化输入重放第一次已提交的不可变 Public Application Result。异步 Command 首次接受返回 `202 Accepted`；已提交的同输入重放固定返回 `200 OK`，并返回完全相同的 Command Receipt 与 Monitor identity。当前 Run 状态只从 `Location` 指向的资源读取。
- 已知 Key 的同输入重放必须先于当前 revision 重检；同 Key + 不同输入返回 `409 Conflict` 且不执行。
- Public Idempotency Key、Command ID、Run ID 与 Attempt ID 保持独立。公共请求和响应不暴露 Hash / Digest，内部输入身份继续保持算法中立。
- 真正陈旧的语义前置条件返回 typed `409 Conflict`，并提供安全的刷新 / 比较 / 再试动作；不得盲目重试。首个 Goal 不强制 ETag / `If-Match` 成为第二套写入权威。

### 3. Durable `202` Receipt + Run Monitor

- 只有真正异步的 Start、Resume、confirmed Rerun、Cancel 等操作使用 `202 Accepted`。Start / Resume / Rerun 先原子提交 Durable Work Intent、接受状态和幂等结果；Cancel 先原子提交权威 `cancellation_requested` 与幂等结果，但不因此创建第二个 Work Intent。
- `202` 只表示请求已经耐久记录等待处理，不表示 Worker 已领取、Provider 已调用、取消已完成、Stage 已成功、Review 已批准或结果已成为 Current Truth。
- 响应返回 typed Command Receipt 和指向 canonical Run Monitor 的 `Location`。已接受命令后续失败通过 Run Resource 表达，不追溯改变最初的 `202`。
- 前端只在活动 Run 状态轮询窄 Run Projection；Stage 或终态变化后刷新 Task Overview 与受影响 Resource，再重新派生私有 `WorkbenchProjection`。Needs Input、waiting Review、manual recovery 与终态停止自动轮询。
- 成功读取一个失败 Run 仍返回 `200` Run Representation；HTTP 5xx 表示读取请求本身失败。公共资源不提供虚构完成百分比，也不按耗时推断终态。
- Resource-local Capability 是与 revision 绑定的小型、建议性合法动作 allowlist，可包含一个 Primary Action；它不是授权 Token。Command 执行时仍须原子复核 revision、幂等与业务不变量。未知 Capability 被忽略，不使用不断增长的 `canX=false` 矩阵。
- HTTP 4xx / 5xx 使用 RFC 9457 `application/problem+json` 共同形态；机器行为由 Problem Type 与窄型扩展字段驱动，不能解析 `title` / `detail` 文案。Needs Input、waiting Review 与 manual recovery 是 Resource 状态，不是 HTTP Error。
- 精确轮询间隔、Backoff、`Retry-After`、Deadline、Correlation、Redaction 与运维阈值继续由 RFC-007 冻结。

## Alternatives Considered

### Pure REST Status Mutation

用 `PATCH` / `PUT` 修改状态字段表达取消、批准与重跑。该方案路由较统一，但会把非法状态迁移伪装为普通字段更新，并模糊 Command 身份与业务意图，因此不采用。

### Public Workbench Mega-snapshot + Generic Action Dispatcher

用一个大 Workbench Response 和一个通用 Action Endpoint 承载全部交互。该方案初期端点较少，但耦合页面、弱化类型生成并创建不受控通用入口，因此不采用。

### Universal ETag / `If-Match` Write Protocol

所有受保护写操作均维护强 ETag，并与 Idempotency Key 并行。该方案更 HTTP-native，但多资源业务 Command 仍需独立语义版本，前端还要维护第二套 Transport Validator 和 `409 / 412` 冲突协议；首个受控客户端没有相称收益，因此不采用。

### Task-only Polling or Push-first Status

只轮询大 Task Snapshot 会模糊 Run、Retry、Rerun、Cancel 和 Receipt Replay；SSE / WebSocket Push-first 则扩大连接、部署、恢复与测试范围。两者均不采用。

## Reason

该组合把产品可见的 revision、业务 Command 与 Durable Run 显式映射为一个可生成、可验证的公共契约，同时保持内部执行和持久化细节私有。它支持响应丢失后的安全重放和跨会话进度恢复，又不引入第二套并发权威、通用命令总线、Push 基础设施或过度防御性错误矩阵。

## Consequences

- RFC-004 后续必须逐项冻结 Task / Run / Needs Input / Review / Brief / Export 的具体 Resource、Command、字段、状态与 Problem Type。
- Frontend 只能从 Server Resource、Capability、Query / Mutation 状态、URL 与本地未保存缓冲派生私有投影，不得模拟服务端终态。
- Contract Tests 必须覆盖首次接受、同 Key 同输入重放、同 Key 不同输入冲突、真正 stale revision、活动轮询停止和失败 Run 的读取语义。
- OpenAPI Artifact、API Handler、Client Generation、数据库记录和测试均尚未创建；这些只可在完整策划与 Goal 激活后按独立 Issue 实现。

## Relationships

- **Conforms to [RFC-002](../rfcs/rfc-002-persistence-and-transaction-architecture.md)：** 传输层 revision、Idempotency 与 Replay 映射不得改变业务事务和唯一约束权威。
- **Conforms to [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)：** `202`、Run、Durable Work Intent 与 cancellation semantics 映射已接受 Runtime 不变量，不把 Checkpoint 暴露为 Public Resource。
- **Concretizes [DEC-055](dec-055-frontend-application-state-and-verification-foundation.md) / [DEC-056](dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md)：** OpenAPI 生成链、私有 WorkbenchProjection、revision-safe 写入和轮询停止获得公共协议基础。
- **Conforms to [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 不新增 Hash / SHA-256，不堆叠低概率防御分支，不把 Capability 或 Rubric 变成机械接受器。
- **Input to [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md)：** 接受 DQ-01～DQ-03；DQ-04～DQ-10 与 RFC 整体仍待后续 Gate。

## Authorization Boundary

本决定只授权 Decision、RFC、Current Truth、Readiness、Testing 与 Traceability 文档同步：

- 不接受 RFC-004 整体；
- 不授权创建 OpenAPI Artifact、Schema、API Route、Handler、Frontend Client、Database Record、Migration 或 Test Implementation；
- 不授权安装依赖、执行 Technical Spike、业务实现、生产实现或长期 Goal；
- DQ-04～DQ-10、Final Consistency Review 与用户 RFC 整体接受仍是后续 Gate。

## Accepted From

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-48A、P-49A、P-50A；用户于 2026-08-07 明确回复“接受 P-48A、P-49A、P-50A”。
- [RFC-004 Draft](../rfcs/rfc-004-api-and-human-review-architecture.md)。
- GitHub：[Issue #54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54) / [Draft PR #55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)。
