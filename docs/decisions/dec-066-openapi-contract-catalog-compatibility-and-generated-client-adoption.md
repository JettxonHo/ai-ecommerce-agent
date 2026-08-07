# DEC-066：采用单一 OpenAPI 契约、有限操作目录与生成客户端 Clean Diff

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-07
- **Decision Type:** API Architecture / OpenAPI Closure / Compatibility / Client Generation / Contract Verification
- **Source:** Session-003；用户明确接受 `P-57A`
- **Related Issue:** [#54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54)
- **Related PR:** [#55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)

## Context

[DEC-063](dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md)、[DEC-064](dec-064-task-recovery-and-human-review-public-protocol.md) 与 [DEC-065](dec-065-immutable-brief-export-problem-and-fixed-workspace-api-boundary.md) 已冻结 RFC-004 的公共契约基础、Task / Recovery / Human Review，以及 Brief / Export / Problem / 固定工作区协议。最后仍需关闭具体 Operation / Schema family、列表窗口、兼容规则、生成客户端采用顺序与 Contract Test 边界，避免实现 Agent 在 API、Frontend 或 Backend Issue 中临场发明公共接口。

## Decision

### 1. One OpenAPI Authority and Stable Naming

- Goal 激活后的第一个 API Contract Issue 创建并提交 `contracts/openapi/openapi.yaml`。可使用 sibling `$ref` 文档，但该 entry document 及其解析后的 OpenAPI Description 是唯一公共 HTTP 权威；不得由 Handler 反向生成，也不得维护平行手写 DTO 文档。
- OpenAPI feature line 保持 `3.1`，当前标准文义按 OAS 3.1.2 核验。`info.version`、`/api/v1` 与 Domain Version 分别表达 Contract revision、HTTP major namespace 与业务版本，不得混用。
- JSON field 与 query parameter 使用 `camelCase`；稳定 identity 使用明确的 `{resource}Id`；Domain Version 使用 `{resource}VersionId` + `versionNumber`；可变 Resource 使用 `revision`；时间使用 UTC RFC 3339；公共 enum 使用 `snake_case`。
- 每个 Operation、request、success response、Problem response、Header 与 media type 都必须显式、稳定且可生成。公共 JSON、RFC 9457 Problem JSON 与 UTF-8 Markdown download 不提供未记录的替代形态。

### 2. Bounded First-Goal Operation Catalog

- Task：创建、最近任务窗口、Task Overview、Start 与 confirmed Rerun。
- Run / Recovery：读取 Run、Cancel、Resume，以及 capability-gated Retry Current Stage / Restart From Safe Boundary。
- Needs Input：读取当前 Action Request 与 typed Resolve。
- Task-facing Source Change：Remove / Replace 各自使用无副作用 Preview 与 typed Confirm；Source content、upload、processing、Source / Fragment / Evidence identity 和 Evidence operations 仍由 RFC-005 拥有。
- Human Review：读取 immutable Package、读取 / full-snapshot 保存 Draft、Submit、Request More Information、Reject All and Request Regeneration，以及读取 / Withdraw Approved Strategy。
- Marketing Brief 与 Xiaohongshu Brief：分别提供 task-scoped bounded history、按 Version identity 读取、显式 Comparison 与 family-specific typed Revise。
- Export：创建 Preview、Confirm 为 immutable Snapshot、读取 Snapshot metadata 与下载 Markdown content。
- 精确 method / path 目录以 [RFC-004 Proposal Round 4](../rfcs/rfc-004-api-and-human-review-architecture.md#proposal-round-4--final-contract-closure) 为本决定的规范性明细；实现 Agent 不得增删、改名、合并或改成 generic dispatcher。
- 最近 Task 窗口只支持可选 `limit`，默认 20、最大 50；Brief history 默认 10、最大 25。两者都不承诺 total、cursor、offset、搜索、批量或完整历史；稳定 identity 深链不依赖窗口位置。
- 首个 Goal 不增加 purge / delete、generic Task status PATCH、generic command bus、batch、webhook、callback、push transport、公开健康诊断、login 或 Tenant operation。

### 3. Public Schema, State and Action Closure

- 公共 Schema families 至少覆盖 Create Task、Task Summary / Overview、Stage Summary、Command Receipt、Run、Needs Input、Source Change Preview / Basis、Review Package / Draft / Outcome、Approved Strategy、两个 Brief Version、Brief Comparison、Export Preview / Snapshot 与 Problem Details。
- Reference、Domain Version、mutable revision、Command、Run、Attempt 与 Idempotency identity 保持分离；ORM、Checkpoint、Lease、Fence、Work Intent、Provider payload 与 Secret 不进入 wire contract。
- Task 状态固定为 `draft / running / waiting_for_input / waiting_for_review / paused / completed / failed / cancelled`；Stage 状态固定为 `not_started / ready / running / waiting_input / waiting_review / valid / invalid / failed / skipped`。
- Run 状态固定为 `queued / running / retrying / waiting_for_input / waiting_for_review / paused / cancellation_requested / completed / failed / cancelled / superseded`；只有前四个活动状态中的 `queued / running / retrying / cancellation_requested` 自动轮询。
- `Capability` 只包含 RFC-004 明列的真实语义动作，并与 Resource revision 绑定；它是建议性投影，不是授权凭证。`PrimaryAction` 只允许 `none`、现有 Workbench target 的 `navigate`，或指向合法 Capability 的 `command`。
- `null` 只表示 Schema 明确允许的当前不存在或不适用；`[]` 表达空集合。QC / validation success 不得映射为 Human approval，Frontend 不得从文案、导航或耗时推断终态或写权限。
- 所有适用的 create / command 使用 DEC-063 的项目定义 `Idempotency-Key`；所有 mutable / version-sensitive write 携带真实 expected revision、base Version 或 basis。Response matrix 保留首次 `201 / 202` 与 committed replay `200`，以及 DEC-065 的 typed `409` 差异。

### 4. Additive Compatibility and Generated-client Adoption

- `/api/v1` 只允许兼容性新增。删除、改名、改变既有字段类型 / requiredness / enum 含义、状态码 / 幂等语义或 identity 用途均属 breaking change，必须经新 RFC；确需公开破坏性契约时进入 `/api/v2`，首个 Goal 不维护双版本。
- 公共状态、Primary Action 或 Problem action enum 新值会影响前端控制流，不按普通 optional field 处理；同一 PR 必须更新 Contract、generated client、Frontend unknown fallback、Contract Tests 与文档。未知值只进入只读 refresh / unavailable 投影，不猜测写 Capability。
- Frontend 使用已接受的 `openapi-typescript` 生成不可手改类型，由 `openapi-fetch` 窄 Adapter 消费。Contract 或 generator 变化后必须重新生成，并由 CI clean-diff 检查漂移；禁止平行手写 DTO 或用 `any` 绕过生成契约。
- 实施依赖顺序固定为 Accepted RFC-004 / 005 / 007 → OpenAPI Contract Issue → generated client Issue → Backend conformance / typed Adapter vertical slices。Handler 与 Workbench 不得先于 Contract 发明 shape。
- 精确 generator / validator patch 版本留给 Goal Issue 依据当时官方兼容证据锁定。若工具无法表达已接受契约，必须停止并提出工具替代或 RFC amendment，不能弱化 Contract 迁就工具。

### 5. Proportionate Contract Verification

- Contract PR 验证 OAS 3.1 parsing / validation、全部 `$ref`、唯一 `operationId`、example conformity、success / Problem media type 与 status，以及 generated-client clean diff。
- Backend Contract Tests 覆盖每个 Operation 的代表性成功路径，并重点验证 retry replay、stale revision、superseded / capability conflict、Run polling stop、Review atomic continuation、Brief revise impact、Export basis / download 与 fixed-workspace / Origin boundary。
- Frontend typed-fixture tests 覆盖每类 Resource / Command / Problem action 与 unknown enum / Capability 的只读 fallback；Browser E2E 只覆盖固定产品闭环和代表性 conflict / temporary unavailable。
- 已有代表性路径与关键不变量后，不为字段排列组合堆叠低概率变体，不建设泛化 API 安全工程。
- RFC-005 / 007 若只填充已经委托的 Source / Evidence Schema refs 或 operational extensions，不重开 RFC-004；若改变 Resource ownership、Operation topology、Problem envelope、workspace boundary 或公共状态语义，必须停止并提出 RFC-004 amendment。

## Alternatives Considered

### Implementation-generated OpenAPI + Frontend Snapshot

由 Backend Handler / serializer 产生接口，再复制一次结果供 Frontend 使用。该方案使实现先于 Contract Review，并产生生成时机与快照漂移风险，违反既有 Contract-first 边界，因此不采用。

### Exhaustive Future Platform Contract

同时定义认证、多租户、Push、全部历史、通用搜索、物理删除、Observability 与全部内部错误。该方案越过 RFC-005 / 007、ARP-08 与首个 Goal 范围，制造无需求依据的兼容承诺，因此不采用。

## Reason

该方案把独立实现最容易临场发明的公共目录、状态、Schema family、窗口、兼容与生成链闭合，同时保留 RFC-005 / 007 的真实所有权。它能支持 Contract-first 的 Backend / Frontend 分工和可验证的生成链，又没有把本地演示扩大为通用平台或过度防御性测试矩阵。

## Consequences

- RFC-004 DQ-01～10 均已有 Accepted Decision；Final Consistency Review 已通过，用户已于 2026-08-07 明确接受 RFC-004 整体。
- RFC-005 / 007 仍须闭合其委托范围，OpenAPI Contract Issue 不能早于三份 RFC 整体接受。
- Contract Artifact、generated client、API Handler、Frontend Adapter 与 Contract Test implementation 均尚未创建。
- 对公共 Operation、状态、Problem envelope 或 workspace boundary 的后续实质变化需要显式 RFC amendment，不得在实现 PR 中静默修改。

## Relationships

- **Extends [DEC-063](dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md)：** 闭合 Contract authority 的具体目录、Schema 与 generated-client adoption。
- **Extends [DEC-064](dec-064-task-recovery-and-human-review-public-protocol.md)：** 将 Task / Recovery / Review 协议冻结为有限 Operation / state family。
- **Extends [DEC-065](dec-065-immutable-brief-export-problem-and-fixed-workspace-api-boundary.md)：** 将 Brief / Export / Problem / fixed-workspace 边界冻结为可生成、可测试的最终公共目录。
- **Conforms to [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 不使用 Hash / SHA-256，不堆叠低概率防御变体，不把 Contract Test 清单变成机械接受器。
- **Input to [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md)：** 接受 DQ-10；Final Consistency Review 通过后，用户已于 2026-08-07 独立接受 RFC-004 整体。

## Authorization Boundary

本决定形成时只授权 Decision、RFC、Current Truth、Readiness、Testing、Traceability 与 Review 文档同步：

- 不接受 RFC-004 整体；
- 不授权合并 PR #55 或关闭 Issue #54；
- 不授权创建 `contracts/openapi/openapi.yaml`、Schema、generated client、API Route、Handler、Frontend Adapter、Database Record、Migration 或 Test Implementation；
- 不授权安装依赖、执行 Technical Spike、业务实现、生产实现或长期 Goal；
- 只有 Final Consistency Review 通过且用户另行接受 RFC-004 整体后，才可合并当前策划 PR 并进入 RFC-005 策划 Gate；这仍不等于实现授权。

> **Post-decision acceptance（2026-08-07）：** 上述后续 Gate 已满足。用户明确接受 RFC-004 整体，并允许合并 PR #55、关闭 Issue #54、进入 RFC-005 策划 Gate；OpenAPI Artifact、依赖安装、实现、Spike 与 Goal 仍未授权。

## Accepted From

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-57A；用户于 2026-08-07 明确回复“接受 P-57A”。
- [RFC-004 Draft Proposal Round 4](../rfcs/rfc-004-api-and-human-review-architecture.md#proposal-round-4--final-contract-closure)。
- GitHub：[Issue #54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54) / [Draft PR #55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)。
