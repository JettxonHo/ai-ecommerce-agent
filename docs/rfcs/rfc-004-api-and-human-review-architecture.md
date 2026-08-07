# RFC-004：API and Human Review Architecture

## Metadata

- **Status:** DRAFTING
- **Date:** 2026-08-07
- **Issue:** [#54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54)
- **Pull Request:** [#55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)（Draft）
- **RFC Acceptance:** NOT GRANTED
- **Implementation Authorization:** NOT GRANTED
- **Spike Execution Authorization:** NOT GRANTED
- **Goal Activation:** NOT GRANTED

## Problem

Product Specification 已整体闭合，RFC-001 / 002 / 003 / 006 与 Frontend Architecture 已接受，但 API、Worker 与 Web Workbench 之间仍缺少唯一、稳定的公共 HTTP Contract。若不在开发前冻结该边界，实现 Agent 将不得不临场决定 Resource、Command、状态、错误、revision、幂等、异步接受、Human Review、恢复与导出协议，从而形成多套事实来源或改变已接受的产品行为。

RFC-004 必须在不实现 API、不创建 OpenAPI 文件、不安装依赖的前提下，冻结足以支持本地单工作区端到端演示的公共契约。它只定义公共 HTTP 与 Human Review 协议，不重新决定 Product、Persistence、Workflow、LLM、Retrieval 或 Observability 架构。

## Context and Authority

### Accepted upstream authority

- [Product PRD](../product/prd.md)、[MVP Scope](../product/mvp-scope.md) 与 [User Flows](../product/user-flows.md)；
- [Frontend Architecture](../architecture/frontend-architecture.md)；
- [RFC-001](rfc-001-repository-and-application-architecture.md)、[RFC-002](rfc-002-persistence-and-transaction-architecture.md)、[RFC-003](rfc-003-langgraph-runtime-and-checkpoint-architecture.md) 与 [RFC-006](rfc-006-llm-runtime-and-structured-output.md)；
- DEC-044～048、DEC-050、DEC-055～057、DEC-059～062；
- [Testing Strategy](../development/testing-strategy.md) 与 [Implementation Readiness](../handoffs/implementation-readiness.md)。

### External standards evidence

- [OpenAPI Specification 3.1.2](https://spec.openapis.org/oas/v3.1.2.html) confirms that an OpenAPI Description is a language-neutral HTTP interface description and distinguishes the OAS feature version from the API's own version. The accepted Frontend Architecture already fixes the project to the OpenAPI 3.1 feature line; this RFC does not upgrade that decision to OAS 3.2.
- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) defines `202 Accepted` as accepted for processing but not completed, and defines strong `If-Match` preconditions for lost-update protection.
- [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) defines `application/problem+json`, stable problem-type identity, occurrence detail, and extensible machine-readable members.
- The IETF `Idempotency-Key` work was still an Internet-Draft at the evidence date. If this RFC adopts that field name, the project must define its own complete semantics and must not present the draft as a finalized Internet Standard.

## Goals

- Establish one committed OpenAPI 3.1 Contract as the only public HTTP source of truth after implementation is authorized.
- Separate query resources, durable asynchronous work, domain commands, and Human Review writes so the right behavior is difficult to misuse.
- Preserve accepted identity, domain version, mutable revision, idempotency, stale-result, stale-review, cancellation, rerun, restore and Current Truth invariants.
- Give the Frontend an explicit server-owned projection of status, primary next action and legal capabilities without creating a second business state machine.
- Define one predictable error and conflict protocol that supports user correction without exposing internal exceptions or inventing excessive defensive cases.
- Keep the fixed-workspace demo boundary explicit without building login, RBAC or multi-tenancy.
- Make Contract, Workflow, Persistence, Frontend and browser acceptance tests independently derivable from the public contract.

## Non-goals

- Implementing routes, handlers, schemas, generated clients, frontend queries, Worker behavior, database models, migrations, downloads or tests;
- selecting a web framework, ASGI server, serializer, authentication product, object-storage Provider or deployment platform;
- defining Source / Fragment / Evidence Locator and retrieval ranking details owned by RFC-005;
- defining log, Trace, Metric, polling threshold, retry delay or operational alert values owned by RFC-007;
- defining physical retention, hold, purge or deletion execution owned by ARP-08 and later Development Planning;
- adding account registration, login, RBAC, multi-tenancy, public API consumers, callbacks, webhooks, SSE, WebSocket or push notifications to the first Goal;
- accepting RFC-004, executing a Technical Spike, or activating the long-running Goal.

## Contract boundary and handoffs

RFC-004 owns:

- public paths, operations, request / response schema and HTTP media types;
- public Resource, Command Receipt, status, capability, error and conflict semantics;
- request identity, idempotency, expected revision and stale-write mapping;
- Task / Run polling, Human Review and export download protocol;
- fixed-workspace request identity and proportional transport boundary;
- OpenAPI compatibility and generated-client contract tests.

RFC-005 owns Source / Fragment / Evidence Locator, retrieval, ranking, evidence collection pagination and Evidence Package transport details. RFC-007 owns diagnostics, telemetry, redaction, operational thresholds and runbooks. Internal ORM, UoW, Dispatch, Checkpoint and Provider types remain private even when their effects are visible through RFC-004 resources.

## Decision map

| Decision Question | Topic | Status |
|---|---|---|
| DQ-01 | Contract authority, namespace and Resource / Command topology | ACCEPTED as P-48A（DEC-063） |
| DQ-02 | Revision preconditions, idempotency and conflict semantics | ACCEPTED as P-49A（DEC-063） |
| DQ-03 | Durable asynchronous acceptance, polling and capability projection | ACCEPTED as P-50A（DEC-063） |
| DQ-04 | Task creation, recent-task index and Workbench read models | PROPOSED as P-51 |
| DQ-05 | Needs Input, Source-facing task actions, cancel, resume, rerun and recovery commands | PROPOSED as P-52 |
| DQ-06 | Review Package, Review Draft, Review Decision and Approved Strategy protocol | PROPOSED as P-53 |
| DQ-07 | Brief versions, comparison, Current Truth result and Markdown export snapshot | PENDING |
| DQ-08 | Problem types, HTTP status mapping and user / retry action semantics | PENDING |
| DQ-09 | Fixed-workspace identity, transport and proportional authorization boundary | PENDING |
| DQ-10 | OpenAPI compatibility, tests, adoption and RFC closure | PENDING |

No item in this table is Accepted until the user explicitly accepts the corresponding proposal and it is archived in a Decision record.

## Proposal Round 1

### P-48 — Contract Authority, Namespace and Resource / Command Topology

#### P-48A — Contract-first Resource Queries + Explicit Typed Commands（推荐）

- The future committed OpenAPI 3.1 Description is the only public HTTP contract. Generated TypeScript types and client code are derived artifacts and must not be edited or treated as a second authority.
- Use `/api/v1` as the single current major HTTP namespace and evolve it additively. The precise server origin remains deployment configuration; the same-origin frontend development proxy continues to route `/api` without making the frontend own API versioning.
- Stable query surfaces use explicit resources such as Task, Run, Review Package, Approved Strategy and Brief. State-changing business operations use individually named, typed command operations; they do not ask clients to patch a status string and do not use a generic `actionName + arbitrary payload` dispatcher.
- The stable resource families are deliberately limited to Task / recent Task summary, task-scoped Source summary and lifecycle entry, Run, Needs Input Action Request, Review plus typed business results, and Export Snapshot. Task is the navigation spine, not a public mega-payload containing every Source, Evidence, Review and Brief body.
- Each command maps to one Public Application Contract and returns one documented result or durable receipt. Public DTOs never expose ORM entities, UoW, Dispatch records, Checkpoint state, LangGraph SDK objects or Provider SDK objects.
- The API exposes a narrow Task overview plus separately versioned related resources. The frontend Query Adapter composes those responses and deterministically derives its private `WorkbenchProjection`; RFC-004 does not publish that private projection as a wire schema or create a new Business Current Truth.
- CRUD is used only for honest resource creation / reading and revision-guarded Draft editing. Start, resume, retry, confirmed rerun, cancel, resolve Needs Input, remove / replace a Source association and submit Review remain explicit typed commands owned by the relevant resource; no cross-module universal `/commands` bus is introduced.

**优点：** preserves explicit business invariants, produces stable generated clients, and keeps command intent reviewable without pretending every domain transition is CRUD.

**代价：** more operations than a generic action endpoint; the RFC must name each supported command and response instead of hiding diversity behind one payload.

#### P-48B — Pure REST Resource Mutation

Expose resources and use `PATCH` / `PUT` for nearly every transition, including cancel, approve, rerun and restore, by changing resource fields or status values.

**优点：** uniform HTTP verbs and fewer conceptual operation types.

**代价：** invites illegal transition requests and last-write-style state mutation, hides command identity and makes Human Review / rerun intent ambiguous. It also pressures the API to expose internal state fields as writable public data.

#### P-48C — One Workbench Endpoint + Generic Action Dispatcher

Expose one large Task Workbench snapshot and one generic action endpoint whose body carries an action name and arbitrary action payload.

**优点：** minimal route count and initially simple frontend integration.

**代价：** couples the public API to the current screen, weakens typed code generation, creates a generic service-locator-style command surface and makes additions silently expand one unstable union.

#### Recommendation

Choose P-48A. It is the smallest interface that respects the accepted Public Application Contract, durable command and Frontend projection boundaries. It does not create endpoints merely to imitate tables or UI components.

### P-49 — Revision Preconditions, Idempotency and Conflict Semantics

#### P-49A — Explicit Semantic Preconditions + Project-defined `Idempotency-Key`（推荐）

- Every protected mutable representation exposes its current monotonic `revision`; immutable Domain Versions keep their separate stable identity and version number.
- Each state-changing request carries only the semantic preconditions it actually needs in its typed request, such as an expected Review Draft revision, base Domain Version or target Stage Run identity. There is no universal last-write-wins mutation and no invented precondition for read-only operations.
- Non-idempotent create / command operations that can be retried after an uncertain response require a project-defined `Idempotency-Key` request header. Its scope, allowed reuse, input-fingerprint comparison, in-progress behavior and stable result replay must exactly map RFC-002 DQ-08; the field name does not rely on the expired Internet-Draft for correctness.
- Same scope + key + same versioned input replays the original immutable public Application result. For an asynchronous command this is the exact same Command Receipt body and monitor identity; the replay response is always `200 OK`, while only the first newly accepted command uses `202 Accepted`. The receipt schema and status do not change with current Run state; callers read `Location` for current status. Same scope + key + different input is an idempotency conflict and executes nothing.
- For a known key, same-input replay is resolved before re-evaluating the now-current revision; otherwise a command that committed but lost its response would be incorrectly rejected as stale. Only a genuinely new logical command evaluates current semantic preconditions and capability before execution.
- The public key remains distinct from server-owned Command ID, Run ID and Attempt ID. No public request or response exposes a hash or digest; internal input identity stays algorithm-neutral under RFC-002 and DEC-039.
- A stale semantic precondition returns a typed `409 Conflict` problem with the current safe refresh / compare / retry action. It is never blindly retried. Internal CAS, unique-constraint, Lease or fencing details stay private.
- Strong ETag / `If-Match` is not a required write protocol in the first Goal. It may be added later for representation caching or a narrowly justified public consumer, but cannot become a second revision authority without an RFC amendment.

**优点：** one revision concept remains visible to the product and generated client; domain commands can express the exact base version they depend on; HTTP retry identity stays separate from concurrency control.

**代价：** less HTTP-native than universal `If-Match`; every command schema must document its real precondition rather than inheriting one generic header.

#### P-49B — Strong ETag / `If-Match` for All Protected Writes + `Idempotency-Key`

Singular GET responses return strong ETags; every protected mutation requires `If-Match`; non-idempotent operations also require `Idempotency-Key`. Failed preconditions return `412 Precondition Failed`.

**优点：** uses standardized HTTP conditional-request semantics and is familiar to generic HTTP infrastructure.

**代价：** one command can depend on several domain versions or a Review Draft plus Package state, while `If-Match` validates one selected representation. The frontend must retain transport validators in addition to product revision and version identities, creating more state without a current external-consumer need.

#### P-49C — Mixed ETag for Resource Edits + Body Preconditions for Commands

Use strong ETag / `If-Match` for Review Draft and other resource edits, explicit body preconditions for multi-resource commands, and `Idempotency-Key` where retries can create duplicate effects.

**优点：** applies standard conditional requests where the target is a single selected representation while preserving typed multi-resource command preconditions.

**代价：** creates two public concurrency transports and both `412` and `409` stale outcomes. The frontend must retain ETag state alongside product revision and command-specific base versions; this complexity is not justified by the first Goal's single controlled client.

#### Recommendation

Choose P-49A. It makes concurrency visible only where the user action truly depends on a base state and avoids maintaining both domain revision and HTTP entity-tag state in the first Goal. This is a deliberate project contract, not a claim that `Idempotency-Key` is already a finalized IETF standard.

### P-50 — Durable Async Acceptance, Polling and Capability Projection

#### P-50A — `202` Durable Receipt + Run Monitor + Narrow Task Overview（推荐）

- Only truly asynchronous Start, Resume, confirmed Rerun, Cancel and equivalent commands return `202 Accepted`. Start / Resume / Rerun require their Durable Work Intent, acceptance state and idempotency result to commit atomically first; Cancel requires its authoritative `cancellation_requested` state and idempotency result to commit atomically, without implying that cancellation creates a second Work Intent. Synchronously completed Task creation or Review Draft save uses its honest `201` / `200` result instead of mechanically returning `202`.
- `202` means reliably recorded for processing, never Worker claimed, Provider called, cancellation completed, stage succeeded, review approved or result current. An accepted command that later fails is represented by the monitor resource; it does not retroactively turn the original accepted request into a 4xx / 5xx response.
- The response carries a typed Command Receipt and `Location` for the canonical monitor. Workflow operations reuse the stable Run resource. If Source processing needs an asynchronous monitor, its natural lifecycle resource remains an RFC-005 decision; RFC-004 does not preemptively create a second generic Operation state machine for the same work.
- Idempotent replay always preserves the same logical command, immutable Command Receipt body and monitor identity. The first accepted request returns `202`; every committed same-input replay returns `200` with that same receipt regardless of current Run state. Current status is never folded into the replay response and is always read from the canonical monitor.
- The frontend polls the narrow Run projection during active queued / running / retrying / cancellation-requested states, then refreshes the Task overview and affected related resources when stage or terminal state changes. Its private `WorkbenchProjection` is re-derived locally. Needs Input, waiting Review, manual recovery and terminal states stop automatic polling until a user action or normal refresh requires it.
- Run detail supplies execution-specific status and safe failure / recovery information. A successful GET of a failed Run is still `200` with a Run representation; HTTP 5xx means the GET itself failed. No resource exposes a fictional percentage or infers completion from elapsed time.
- Resource-local capability is a small revision-bound allowlist of currently meaningful semantic actions, optionally with one primary action. It is advisory projection rather than an authorization token; every command still revalidates revision, idempotency, capability and business invariants atomically. Unknown capability is ignored, and the API does not emit a growing `canX=false` boolean matrix.
- HTTP 4xx / 5xx errors use RFC 9457 `application/problem+json` as the common shape. Human-readable `title` / `detail` is not parsed as control data; problem-type identity and a narrow typed extension set drive client behavior. Needs Input, waiting Review and manual recovery are normal resource states, not HTTP errors. Detailed public problem taxonomy remains DQ-08.
- Exact poll interval, jitter, transient backoff, `Retry-After` generation, deadlines, error correlation, redaction and operational thresholds remain RFC-007 inputs.

**优点：** aligns HTTP acceptance with durable dispatch, preserves an inspectable Run identity, and lets the frontend re-derive its private Workbench projection from narrow server-owned resources without simulating terminal state.

**代价：** requires two related read surfaces—Task overview for navigation and Run for execution detail—and precise rules for which fields each owns.

#### P-50B — `202` + Task Snapshot Only

Return `202` and have the client poll one public aggregate Task / Workbench snapshot; do not expose a stable Run resource.

**优点：** fewer public resources and requests.

**代价：** repeated runs, retry / rerun, cancellation, failure diagnosis and command receipt replay become ambiguous; the Task snapshot must absorb execution history and internal dispatch concerns.

#### P-50C — Push-first SSE / WebSocket Status

Return a receipt and require an SSE or WebSocket channel for subsequent state changes, with polling only as fallback.

**优点：** faster perceived updates and fewer steady-state poll requests.

**代价：** adds connection lifecycle, reconnect, ordering, deployment and test complexity that the local single-workspace MVP does not need; it expands RFC-007 and frontend runtime scope.

#### Recommendation

Choose P-50A. It is the minimum design that keeps `accepted != completed`, supports durable Run identity, and gives the Frontend explicit status / capability ownership without adding push infrastructure.

## Round 1 decision status and next gate

- 用户于 2026-08-07 明确接受 P-48A / P-49A / P-50A，三项归档为 [DEC-063](../decisions/dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md)。
- `DQ-01 / DQ-02 / DQ-03 = ACCEPTED`；该部分接受不等于 RFC-004 整体接受。
- 下一提案组覆盖 DQ-04～DQ-06：Task / Workbench Query、Recovery Command 与 Human Review Protocol。
- 本 Draft 不授权 OpenAPI 生成、代码、依赖安装、测试实现、Technical Spike 或 Goal 激活。

## Proposal Round 2

### P-51 — Task Creation, Recent-task Index and Workbench Read Model

#### P-51A — Synchronous Task Creation + Bounded Recent Index + Narrow Task Overview（推荐）

- `POST /api/v1/tasks` 只创建 Task identity 与初始业务上下文，不隐式启动 Workflow。请求携带已接受的 Task 名称 / 临时名称、商品品类和推广目标语义，并要求 `Idempotency-Key`；首次成功返回 `201 Created`、稳定 Task identity、Task Overview 与 `Location`，同 Key / 同输入重放返回 `200` 和同一 Task identity。
- `GET /api/v1/tasks` 只返回固定工作区的 server-bounded recent-task window，按后端权威最近更新时间倒序投影；首个 Goal 不提供全文搜索、高级筛选、批量、归档、统计、总数承诺或分页优化。精确默认 / 最大窗口值留给 DQ-10 的 OpenAPI Closure 冻结。
- `TaskSummary` 只表达稳定 Task identity、显示名称、商品品类、当前阶段或等待语义、后端权威更新时间、当前 Task revision、Primary Action 与绑定该 revision 的小型 Capability allowlist。列表不携带 Source、Evidence、Review 或 Brief 正文；列表 Capability 仍是 advisory，执行前由 Command 原子复核。
- `GET /api/v1/tasks/{taskId}` 返回窄 `TaskOverview`：Task identity / lifecycle、当前 revision、Stage summaries、当前活动或最近 Run reference、当前 Needs Input / Review reference、Current Truth result references、Primary Action 与 Capability。它不嵌入完整 Run history、Review Package、Evidence collection 或 Brief body。
- Task Overview 中的 Reference 只是稳定 Resource identity，不是 ORM Foreign Key、Checkpoint ID 或前端 Route State。Frontend 使用独立 Query 读取当前 Panel 真正需要的 Resource，再派生私有 `WorkbenchProjection`。
- Empty recent list 是 `200` + empty items；不存在的稳定 Task identity 是 typed `404`。暂时读取失败使用 DQ-08 的 Problem Details，不把 stale cache 推断为 Current Truth。

**优点：** 同时满足创建、跨会话返回和深工作台导航，保持 Task 为窄导航主轴；不会为了一个页面制造 mega-snapshot，也不会要求前端盲目扇出所有资源。

**代价：** 打开具体 Panel 需要额外窄查询；Recent Window 之外的 Task 只可通过稳定深链进入，首个 Goal 不承诺完整任务管理体验。

#### P-51B — Expanded Task Overview with Embedded Latest Resource Summaries

Task Overview 除 Stage / Reference 外，还嵌入最新 Source、Review、Approved Strategy、Brief 和 Export 的摘要或部分正文；详情正文仍由独立 Resource 提供。

**优点：** 首屏请求较少，工作台可用一个响应渲染更多内容。

**代价：** 摘要与独立 Resource 容易产生新鲜度和字段重复；每个下游模块变更都会扩大 Task Contract，使 Task 逐步退化为半个 Workbench mega-payload。

#### P-51C — Fully Decomposed Reads without Task Overview

只提供 Task identity 和最近列表；进入 Task 后由前端并行读取 Stage、Run、Needs Input、Review、Brief 等所有资源并自行决定主要状态。

**优点：** 每个 Resource 最窄，Task Contract 最小。

**代价：** Frontend 必须从多个不同时间点的响应推断导航状态与 Primary Action，增加短暂矛盾和启动请求数量，也更容易形成第二套业务状态机。

#### Recommendation

Choose P-51A. A narrow server-owned overview is the minimum coherent navigation projection, while independent resources keep review, evidence and result bodies authoritative and separately refreshable.

### P-52 — Needs Input, Source-facing Actions and Runtime Recovery Commands

#### P-52A — Revision-bound Action Request + Explicit Preview / Confirm and Run Commands（推荐）

- 当前真实阻断通过 task-scoped `NeedsInputActionRequest` Resource 表达。它具有稳定 identity、当前 revision、阻断类型与原因、受影响阶段、可见 Source / 冲突值 Reference、允许的 typed Resolution、预期恢复 / 重跑范围和当前状态；上游变化后旧请求变为 superseded，不能继续提交。
- Resolution 使用与该 Action Request 类型匹配的 discriminated request，例如补充资料 Reference、选择现有值、提交纠正值、确认已知限制或取消当前路径；自由文本只能是说明，不能成为唯一不可追踪的业务事实。Command 必须携带 Action Request revision 和 `Idempotency-Key`。
- Resolution 本身先同步提交业务输入 / 裁决并返回更新后的 Action Request / Task references。只有当服务端重新计算后提供 `resume` / `rerun` Capability，客户端才可调用对应 typed Command；Frontend 可以在一次用户动作内顺序执行，但不得在 Resolution 成功前或没有 Capability 时乐观 Resume。
- Source Association remove / replace 遵循 typed preview → confirm：Preview 是无副作用的影响计算，并返回 typed `SourceChangeBasis`，至少绑定当前 Task revision、目标 Source Association revision、当前 Source Version identity，以及实际受影响的 Stage / Current Truth / Review Package / Brief version 或 revision references。Confirm Command 回传同一 Basis、目标 Source Association identity、Replacement reference（如适用）与 `Idempotency-Key`；服务端重新计算并验证全部适用 Basis，任一已变化即返回 typed conflict 且不提交。该 Basis 只引用 RFC-005 拥有的 Source identity / version，不定义其内容 Schema，也不使用 Hash / Digest 或通用 Diff Token。
- `cancel` 明确针对当前 Run identity；成功接受只表示 `cancellation_requested` 已耐久记录，直到 Run Monitor 表达 terminal cancellation 前不得显示“已取消完成”。
- `resume` 只用于服务端 Capability 明确允许继续的兼容 `thread_id` / execution context，并为该次恢复创建新的 Run identity 与 Attempt，可引用来源 Run；`confirmed-rerun` 明确携带 Task revision、最早重跑 Stage 与用户已看到的受影响 Stage set，服务端复核影响集合后同样创建新 Run identity。二者不得复用为模糊 `retry`，也不得复用旧 Run identity。
- Manual Recovery 只暴露与 DEC-051 当前 Recovery Decision 对应的少量用户可执行 typed Commands；Checkpoint identity、Lease、Fencing Token、Worker Attempt 或内部七动作枚举不进入公共 Request。
- Source 内容、解析状态与异步 Source lifecycle 由 RFC-005 冻结；RFC-004 只拥有 Task-facing Command、前置条件、Receipt / Problem 映射和对 Run / Task 的影响。

**优点：** 用户看到的阻断、预览与动作具有同一 revision 基础；Frontend 不负责推演恢复状态，Source 变更和 Run 控制仍保持明确意图与可审计性。

**代价：** Resolution 与后续 Resume / Rerun 是两个公共 Command；客户端需要按服务端 Capability 安全串联，而不是只调用一个万能恢复接口。

#### P-52B — One Generic Recovery Command

使用一个 `/recovery-actions` Endpoint，Request 传 `actionType` 和可变 Payload，统一处理补料、冲突、Source 变化、Cancel、Resume 与 Rerun。

**优点：** 路由少，服务端可集中调度。

**代价：** 与 DEC-063 的 explicit typed Command 冲突，Payload union 会不断扩大，并把 Source / Review / Workflow 的前置条件藏进通用 Dispatcher。

#### P-52C — Frontend-orchestrated Recovery

服务端只提供细粒度 Source mutation 和 Run mutation；Frontend 根据页面状态自行决定顺序、何时恢复、从哪个 Stage 重跑以及失败后如何补偿。

**优点：** 后端公共 Operation 较少，交互迭代看似更快。

**代价：** 把业务恢复状态机移到浏览器，容易在响应丢失、跨会话或多标签场景重复执行，并违反 Server-owned Current Truth / Capability 边界。

#### Recommendation

Choose P-52A. It keeps user actions narrow and reviewable, supports confirmed invalidation without opaque integrity machinery, and makes the server—not the screen—the authority for whether work may resume or rerun.

### P-53 — Human Review Package, Draft, Decision and Approved Strategy Protocol

#### P-53A — Immutable Package + Full-snapshot Draft Save + Explicit Outcome Commands（推荐）

- `ReviewPackage` 是不可变、按 `reviewId + packageVersion` 读取的审核输入快照，公开已接受的七个产品语义组和精确上游 Version references。上游变化不会改写旧 Package，而是使其 superseded 并创建新 Package。
- 每个当前 Review Package 最多有一个 active `ReviewDraft` Resource。Draft 只保存当前结构化 Strategy Draft、Candidate selection / merge provenance、Hypothesis decisions、Proof Point decisions、Evidence Limitation decisions 与 User Notes；服务端从 revision history 生成 Audit，不要求客户端回传完整历史事件。
- Autosave 使用 full structured snapshot `PUT`，不采用 JSON Patch。首次创建使用 `expectedRevision = 0`，后续保存携带当前 revision；每次成功保存返回 canonical Draft snapshot 和更高 revision。所有保存使用 `Idempotency-Key`，同 Key / 同输入重放同一保存结果；stale revision 返回 typed `409`，不覆盖较新 Draft。
- `select / edit / merge / reject candidate` 是 Draft 内容与 provenance，不等于批准。`submit` 是独立 typed Command，必须携带 `reviewId`、`packageVersion`、最新 Draft revision 与 `Idempotency-Key`；服务端重新验证 Package、上游版本、Draft 和全部业务不变量后，在一个事务中创建不可变 `ReviewDecision`、新的 `ApprovedStrategy` Domain Version、Current Truth Pointer 与 Stage updates。
- `submit` 的同一原子事务必须同时提交 Review Decision、Approved Strategy、Current Truth / Stage updates、Audit、幂等结果与唯一 Durable Resume Work Intent；客户端不再发送第二个 Resume Command。首次成功返回 `201 Created` 的 Approved Strategy / Review Decision references，并携带该 continuation 的不可变 Command Receipt、新 Run identity 与 canonical Run monitor reference；同输入重放返回 `200` 的同一完整结果且不得重复调度。`201` 表达主 Resource 已同步创建，Receipt 只表达下游 continuation 已耐久接受，不表示 Brief 已生成。
- `request-more-information`、`reject-all-and-request-regeneration` 与 `withdraw-approved-strategy` 是各自 typed Outcome Command，不伪装为 `submit`。Request More Information 同步记录 Review outcome 并创建 / 关联 Needs Input Action Request，不创建 Approved Strategy 或 Work Intent。Reject-all-and-request-regeneration 原子记录拒绝、幂等结果与唯一 Durable Work Intent，首次返回 `202` + 新 Run Receipt，重放返回 `200` 同一 Receipt，不创建 Approved Strategy。Withdraw 保留原 Approved Strategy history、清理 Current Pointer、失效下游并创建新 Review Cycle，不自动重跑；它须使用当前 Strategy Version / Task revision 与 `Idempotency-Key`。
- 所有 state-changing Review Outcome 均继承 RFC-002 对其适用 Business State、State Transition / Audit 与 Idempotency Result 的原子参与者规则；上述公共响应描述不构成内部事务记录的穷举清单。
- Approved Strategy 只能按稳定 Version identity 读取；Current Strategy 通过 Task 的 Current Truth reference 发现。Review Package、Draft、Decision 与 Approved Strategy 身份、version / revision 和生命周期保持分离。

**优点：** 与前端 latest-buffer autosave 完全一致；一个可预测的 Draft Snapshot Contract 比 JSON Patch 更易生成类型和恢复冲突，同时保留不可变 Package、Decision 与 Approved Strategy 的业务边界。

**代价：** 每次保存发送完整 Draft；服务端需要保存 revision history / audit，并为 Submit、Request More Information、Regeneration 与 Withdraw 维护多个明确 Command。

#### P-53B — JSON Patch Review Draft + Submit Command

Draft 保存使用 RFC 6902-style Patch，按 revision 应用细粒度操作；Package、Submit 与 Approved Strategy 边界保持不变。

**优点：** 大 Draft 的传输量较小，单项变更表达精确。

**代价：** 数组索引、Candidate merge、冲突重放和生成 Client 类型更复杂；首个单 Review 工作台没有证据表明 Draft 大到需要维护 Patch 语言。

#### P-53C — Review Operation Log as the Public Write Model

客户端分别发送 select / edit-field / merge / decide-hypothesis / reject-proof-point 等 Operation，服务端从 Event Log 还原 Draft；Submit 再冻结 Approved Strategy。

**优点：** 审核操作天然可审计，并可支持细粒度协作。

**代价：** 把公共 API 扩展为事件编辑协议，增加顺序、撤销、重放和兼容复杂度；首个 Goal 不做多人协作，内部 Audit 不需要成为公共 Event Sourcing Contract。

#### Recommendation

Choose P-53A. A full-snapshot, revision-guarded Draft is the shallowest transport that preserves the accepted autosave and stale-conflict behavior; explicit terminal commands keep approval, more-information, regeneration and withdrawal semantically distinct.

## Round 2 proposal status and next gate

- P-51 / P-52 / P-53 are `PROPOSED`; no option is Accepted until the user explicitly confirms it and a Decision record is archived.
- P-51A does not create a full Task dashboard or final pagination platform. P-52A does not preempt RFC-005 Source schemas. P-53A does not authorize API, database or frontend implementation.
- If this round is accepted, the next proposal group will cover DQ-07～DQ-09: Brief / Export, Problem taxonomy and fixed-workspace identity / transport.

## Risks and stop conditions

- Stop if a proposed public operation changes accepted Product behavior or persistence / workflow invariants rather than transporting them.
- Stop if one field is asked to serve as Domain Version, mutable revision, command identity, Run identity and idempotency key.
- Stop if RFC-005 or RFC-007 cannot own its delegated contract without producing duplicate authorities.
- Stop if a public contract requires login, RBAC, multi-tenancy, push transport, broad compliance or physical purge in the first Goal.
- Stop if implementation evidence later proves the accepted OpenAPI toolchain cannot represent the contract without weakening it; propose an RFC amendment rather than silently hand-writing a second client contract.

## Outcome

Pending. RFC-004 remains Drafting and has no implementation authorization.
