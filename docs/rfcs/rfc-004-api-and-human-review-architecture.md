# RFC-004：API and Human Review Architecture

## Metadata

- **Status:** ACCEPTED
- **Date:** 2026-08-07
- **Accepted:** 2026-08-07（用户明确接受：「接受 RFC-004 整体」）
- **Issue:** [#54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54)
- **Pull Request:** [#55](https://github.com/JettxonHo/ai-ecommerce-agent/pull/55)
- **RFC Acceptance:** GRANTED
- **Final Consistency Review:** PASS（2026-08-07）
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
- executing a Technical Spike or activating the long-running Goal；RFC-004 的整体接受只确立架构基线，不授权实现。

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
| DQ-04 | Task creation, recent-task index and Workbench read models | ACCEPTED as P-51A（DEC-064） |
| DQ-05 | Needs Input, Source-facing task actions, cancel, resume, rerun and recovery commands | ACCEPTED as P-52A（DEC-064） |
| DQ-06 | Review Package, Review Draft, Review Decision and Approved Strategy protocol | ACCEPTED as P-53A（DEC-064） |
| DQ-07 | Brief versions, comparison, Current Truth result and Markdown export snapshot | ACCEPTED as P-54A（DEC-065） |
| DQ-08 | Problem types, HTTP status mapping and user / retry action semantics | ACCEPTED as P-55A（DEC-065） |
| DQ-09 | Fixed-workspace identity, transport and proportional authorization boundary | ACCEPTED as P-56A（DEC-065） |
| DQ-10 | OpenAPI operation / schema closure, compatibility, tests and adoption | ACCEPTED as P-57A（DEC-066） |

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

## Round 2 decision status and next gate

- 用户于 2026-08-07 明确接受 P-51A / P-52A / P-53A，三项归档为 [DEC-064](../decisions/dec-064-task-recovery-and-human-review-public-protocol.md)。
- `DQ-04 / DQ-05 / DQ-06 = ACCEPTED`；该部分接受不等于 RFC-004 整体接受。
- 下一提案组覆盖 DQ-07～DQ-09：Brief / Export、Problem taxonomy 与固定工作区 identity / transport。
- P-51A 不创建完整 Task Dashboard 或最终 Pagination 平台；P-52A 不抢占 RFC-005 Source Schema；P-53A 不授权 API、Database 或 Frontend 实现。

## Proposal Round 3

### P-54 — Brief Version, Comparison, Current Truth and Markdown Export

#### P-54A — Immutable Brief Resources + Typed Revision Command + Confirmed Export Snapshot（推荐）

- `MarketingBriefVersion` 与 `XiaohongshuBriefVersion` 是两个独立的不可变 Resource family。每个版本公开稳定 identity、Task identity、对象类型、单调 Domain Version number、有效性、创建来源、创建时间、必要上游 Version references、六个已接受产品语义组，以及 Hypotheses / Evidence Limitations / Risks / Evidence references。它们不公开 Prompt、Provider payload、ORM、Checkpoint 或内部 Validator record。
- Task Overview 的 Current Truth references 是“当前有效结果”的唯一发现入口。按稳定 Version identity 读取历史版本不会使其重新成为 Current Truth；服务端限制的版本历史只用于查看 / 比较，不承诺首个 Goal 的无限历史管理、搜索或批量恢复。
- 同一 Task、同一 Brief family 的两个版本可以请求无副作用的 typed `BriefComparison`。Comparison 绑定 base / target Version identities，按语义组和 field path 返回 before / after、model / user origin、edit intent 与确定性阶段影响；长文本的词 / 行差异仍只是 Frontend 视觉辅助。Comparison 不是新 Domain Version、Audit authority 或字段级依赖图。
- 用户编辑通过 family-specific typed `revise` Command 提交完整结构化候选、base Version identity、当前 Task revision、明确的 `business_change` 或 `presentation_polish` intent 与 `Idempotency-Key`。歧义自由文本由用户在界面确认 intent，LLM 不替用户作最终分类。服务端仍验证 Strategy / Brief lock、证据与声明边界，不能只相信 intent 字符串绕过业务约束。
- Marketing Brief 的业务修改首次成功同步创建新的不可变 Marketing Brief Version、更新 Current Truth 并使当前 Xiaohongshu Brief 失效；Xiaohongshu Brief 的业务修改只创建自身新版本，不反向失效上游。明确的展示性润色仍创建可追溯的新 Brief Version，但不触发业务重跑；若修改触及结构化业务字段或既有锁定边界，则不得以 `presentation_polish` 绕过应有的影响确认。
- 重跑生成的 Brief 继续由 Workflow 的原子 Business Commit 创建，并通过 Run Monitor 暴露；HTTP revise Command 不伪装模型生成，也不把生成成功等同于 Current Truth promotion 之外的人工批准。
- 导出采用无副作用 `ExportPreview` → typed `confirm-export`。Preview 冻结待确认的 Task revision、Brief family / Version identity、必要上游 references、Hypotheses、Evidence Limitations、Risks 与导出范围；Confirm 必须回传该 typed basis 和 `Idempotency-Key`。Current Truth 或任一适用 basis 已变化时返回 conflict，不为旧结果创建“当前导出”。
- Confirm 首次成功同步创建不可变 `ExportSnapshot` 并返回 `201 Created`；同输入重放返回 `200 OK` 同一 Snapshot。Snapshot 记录 Task、Brief Version、必要上游、导出时间和模板版本，但不创建新的业务事实、不改变 Current Truth，也不使用 Hash / SHA-256 / Digest。
- 每个 Snapshot 只包含一个当前有效 Marketing Brief 或一个当前有效 Xiaohongshu Brief，使用固定 UTF-8 Markdown 模板：标题与 Brief 类型 → Task / Version / 上游上下文 → 六个产品语义组 → Hypotheses / Evidence Limitations / Risks → Evidence references → Export metadata。无适用项诚实显示“无 / 不适用”，不得为模板完整制造内容。
- Snapshot content 通过稳定下载 Operation 返回 `text/markdown; charset=utf-8` 和 attachment disposition。服务端生成 ASCII-safe 文件名 `task-{taskId}-{briefKind}-v{versionNumber}-{exportedAtUtc}.md`，其中时间使用 `YYYYMMDDTHHMMSSZ`。已创建 Snapshot 后续不会因 Current Truth 前进而改变；它可以作为明确标识的历史快照读取，但不得被界面继续标成当前结果。物理保留 / 清理由 ARP-08 与 Development Plan 决定。

**优点：** 将 Current Truth、历史版本、用户修改、版本比较和用户文件快照分离；可以可靠重放导出又不引入第二套 JSON 用户导出、内容哈希或异步文件任务。

**代价：** 用户编辑和导出各有显式 basis / command；Frontend 需要在确认前展示版本上下文，并在冲突后刷新 / 比较。

#### P-54B — Mutable Current Brief + Export Current on Download

只公开一个可覆盖的 Current Brief；下载时即时把当前内容渲染为 Markdown，不创建 Export Snapshot。

**优点：** Resource 和 Operation 最少，下载实现直接。

**代价：** 无法解释历史编辑、失效、重跑和已下载文件对应哪个版本；响应丢失或 Current Truth 变化时不能可靠重放同一导出，违反已接受的不可变 Domain Version / Export Snapshot 行为。

#### P-54C — Asynchronous Export Job + Multi-format Artifact

所有导出均创建异步 Job，可生成 Markdown、JSON 与 PDF，并提供 Artifact history。

**优点：** 适合未来大文件、多格式和后台渲染。

**代价：** 首个 Goal 的单份结构化 Brief 很小；该方案会增加新的 Job 状态机、PDF / JSON 用户契约、对象存储和保留问题，扩大已明确排除的范围。

#### Recommendation

Choose P-54A. It is the smallest protocol that preserves immutable Brief history, user-visible comparison, Current Truth, confirmed Markdown export and reliable replay without creating a new document platform.

### P-55 — Problem Types, HTTP Mapping and Recovery Actions

#### P-55A — Small Stable Problem Catalog + Typed Context and Action（推荐）

- 所有 API 4xx / 5xx 使用 RFC 9457 `application/problem+json`，共同字段为 `type`、`title`、`status`、`detail`、`instance`；机器行为只依赖稳定 `type` 与窄型扩展，不解析人类文案。Problem Type 使用部署无关的项目 URN，例如 `urn:ai-ecommerce-agent:problem:revision-conflict`。
- 公共目录只包含真实改变客户端行为的有限类型：
  - `malformed-request` → `400`：请求语法、JSON 或查询形态无法读取；
  - `not-found` → `404`：当前固定工作区内不存在该 Resource；
  - `payload-too-large` → `413`、`unsupported-media-type` → `415`：整个上传 / 请求边界不被接受；单文件部分接受细节仍由 RFC-005 的 typed item result 表达；
  - `validation-failed` → `422`：请求可读取，但字段或业务候选不满足当前 Contract；包含有限 field issues，不返回内部 Validator dump；
  - `revision-conflict`、`idempotency-conflict`、`superseded-resource`、`capability-conflict` 与 `operation-in-progress` → `409`：分别表达 stale base、同 Key 不同输入、旧 Package / Action / Version、动作已不合法，以及同一逻辑操作仍由有效 Attempt 执行；
  - `rate-limited` → `429`：只用于当前 HTTP 边界真实限流，不把异步 Provider 的 Run failure 倒映成原请求 429；
  - `internal-error` → `500`、`service-unavailable` → `503`：请求本身无法完成；不暴露 Exception、SQLSTATE、Provider payload、Secret、Checkpoint 或 Worker internals。
- Conflict 扩展只返回安全恢复所需的 current Resource / revision / Version reference、冲突字段或 basis summary，以及一个 typed `action`：`correct_input`、`refresh`、`refresh_and_compare`、`open_current`、`retry_later`、`contact_operator` 或 `none`。不存在通用 arbitrary metadata bag，也不把 Rubric 分数作为接受条件。
- `operation-in-progress` 只用于尚无可重放 committed result 的并发窗口；若命令已经提交 Durable Acceptance 或最终结果，同 Key / 同输入必须按 DEC-063 重放 `200` 的同一结果，而不是继续报冲突。可合理估计时，`429`、`503` 或 `operation-in-progress` 使用 `Retry-After`；精确等待与 Backoff 仍由 RFC-007 冻结。
- Field validation 问题定位到公共 field path 与稳定 reason code；`detail` 只供人阅读。Trace / correlation reference 可作为可选安全扩展，但生成、记录和 Redaction 由 RFC-007 拥有。
- Needs Input、waiting Review、manual recovery、cancellation requested、failed Run、superseded result 与 Evidence Limitation 是正常 Resource state / representation，不用 HTTP Problem 伪装。成功读取失败 Run 仍是 `200`。
- Frontend 已有成功快照而 refresh 得到暂时性 Problem 时保留 stale snapshot 与本地编辑缓冲，暂停依赖新鲜前置条件的写入并提供匹配动作；Toast 不得成为错误或 Conflict 的唯一载体。

**优点：** 一个错误形态与有限机器语义足以覆盖真实恢复路径；不会把内部异常分类、每个业务状态或低概率变体机械展开为公共错误矩阵。

**代价：** 不同 `409` 需要稳定 Problem Type 和少量 typed context；实现与 Contract Tests 必须验证其动作语义，而不能只断言状态码。

#### P-55B — HTTP Status + Free-text Detail Only

只使用状态码和文字错误，不维护稳定 Problem Type 或扩展字段。

**优点：** Contract 最小，后端实现快。

**代价：** Frontend 只能解析文案或自行猜测刷新、比较、修正与重试动作；多语言或文案调整会变成破坏性 API 变化。

#### P-55C — Exhaustive Domain Error Enumeration

为每个内部 Validator、Workflow node、Provider error、SQLSTATE、Stage state 和异常分支定义独立公共 Problem Type 与错误码。

**优点：** 分类非常细，诊断表面完整。

**代价：** 泄漏内部实现、扩大兼容承诺并制造大量首个 Goal 不会发生或客户端无法处理的分支，违反适度校验和稳定边界原则。

#### Recommendation

Choose P-55A. It gives the Workbench stable recovery semantics while keeping the public catalog proportional to actions the controlled client can actually perform.

### P-56 — Fixed-workspace Identity, Transport and Proportional Authorization

#### P-56A — Server-bound Workspace + Loopback Same-origin Transport（推荐）

- 首个 Goal 只有一个由本地 Bootstrap / Configuration 选择的固定 Workspace。Workspace identity 由服务端请求上下文注入；Browser 不选择 Workspace，不提交任意 `workspaceId` Header / Body，也不能仅凭 Task ID 改变 Workspace scope。
- Task、Run、Review、Brief 与 Export Query / Command 始终由服务端限定在该固定 Workspace。不存在或不属于当前 scope 的 identity 统一映射为 `404`；公共 DTO 不暴露内部数据库 scope key，也不预先设计 Tenant selector。
- 浏览器只使用同源 `/api/v1`；Vite development proxy 保持 Frontend 与 API 的同源调用形态。API 默认只绑定 loopback，CORS 默认不开放；本地演示 HTTP 不声称具备公网 TLS、Internet exposure 或远程用户访问能力。
- Browser state-changing requests 使用明确 JSON / multipart Contract；当请求携带 `Origin` 时，服务端要求它匹配配置的本地 Workbench origin。API 不接受 cross-origin simple-form mutation 作为替代传输。该边界用于防止其他网页驱动本地工作台写入，不扩展为通用身份平台。
- 首个 Goal 不建设注册、登录、Session Cookie、Bearer Token、API Key、CSRF Token、RBAC、多人审核或 Tenant membership。Audit 中的本地操作者身份由服务端记录为固定受控 Actor context，不信任客户端自报用户 / 角色。
- OpenAPI / Contract Test 与本地人工 Smoke 可以从同一 loopback 环境调用；Secret、Provider Credential 和数据库 Credential 永不成为 Browser API 身份。Export download 与 Source upload 继续使用同源 API；外部对象访问和 Source 权限过滤由 RFC-005 冻结。
- 任何非 loopback 绑定、公开部署、第二 Workspace、远程用户、共享环境或真实权限区分都会触发新的 Product / Security / API Decision Gate；不得把 P-56A 静默当作可上线公网的认证方案。

**优点：** 与受控本地单工作区演示完全一致；消除伪多租户 Header 和无实际用户模型的 Login，同时保留对本地跨站写入的适度边界。

**代价：** 不能直接公开部署或支持多用户；未来进入 Beta 时必须引入真正的身份、成员关系和授权设计，而不是复用固定 Actor。

#### P-56B — Client-supplied Workspace Header

Frontend 在每个请求中发送静态 `X-Workspace-Id`，服务端按该 Header 过滤数据；仍不建设登录。

**优点：** 看似便于未来增加多个 Workspace，也便于手工切换测试数据。

**代价：** 未认证 Header 不是授权边界，会制造伪多租户协议和错误安全感；首个 Goal 没有切换 Workspace 的产品需求。

#### P-56C — Local Login or Shared API Token

即使本地单人演示也要求登录或静态 Bearer / API Token，并据此选择 Workspace 与 Actor。

**优点：** 更接近未来远程服务的表面形态。

**代价：** 增加 Credential 生命周期、Session / Token 存储、登录 UX、权限错误和测试矩阵，却没有真实账号、租户或公网部署需求；静态共享 Token 也不能替代未来正式身份模型。

#### Recommendation

Choose P-56A. It states the honest security boundary of the local demo, prevents client-selected workspace scope, and adds only the same-origin protections justified by the actual threat surface.

## Round 3 decision status

- 用户于 2026-08-07 明确接受 P-54A / P-55A / P-56A，三项归档为 [DEC-065](../decisions/dec-065-immutable-brief-export-problem-and-fixed-workspace-api-boundary.md)。
- `DQ-07 / DQ-08 / DQ-09 = ACCEPTED`；该部分接受不等于 RFC-004 整体接受。
- P-54A 不增加 PDF / JSON 用户导出、异步文档任务或内容 Hash；P-55A 不公开内部异常矩阵；P-56A 不是公网部署认证。
- 最后一个 Decision Gate 为 DQ-10：OpenAPI Operation / Schema closure、兼容、Generated Client adoption、Contract Tests 与 Final Consistency Review readiness。

## Proposal Round 4 — Final Contract Closure

### P-57 — OpenAPI Operation / Schema Closure, Compatibility, Tests and Adoption

#### P-57A — One Contract Artifact + Bounded Operation Catalog + Generated-client Clean Diff（推荐）

##### Contract artifact and naming

- Goal 激活后的第一个 API Contract Issue 创建并提交单一 OpenAPI 3.1 entry document `contracts/openapi/openapi.yaml`。允许按 domain 拆分被 `$ref` 引用的 sibling documents，但 entry document 是唯一入口；OpenAPI Description 整体是公共 HTTP 权威，不能由 Handler 反向生成，也不能与手写 DTO 文档并列为第二事实源。
- OpenAPI feature line 保持已接受的 `3.1`；当前核验采用 3.1.2 文义。`info.version` 独立表达本项目 API Contract revision，不把 OAS 版本、`/api/v1` 主版本和 Domain Version 混为一个字段。
- JSON field 与 query parameter 使用 `camelCase`；稳定 identity 字段使用明确的 `{resource}Id`，Domain Version 使用 `{resource}VersionId` + `versionNumber`，可变 Resource 使用 `revision`。时间使用 UTC RFC 3339 `date-time`；公开 enum 使用 `snake_case`，与已接受的 Domain / Product 语义一致。
- 每个 Operation 有唯一、稳定、动作明确的 `operationId`；每个 request、success response、Problem response、Header 与 media type 均显式引用 Schema。公共 body 默认 `application/json`，错误使用 `application/problem+json`，Snapshot 下载使用 `text/markdown; charset=utf-8`；不提供 undocumented body 或 alternate success shape。

##### Exact first-Goal operation catalog

| Family | Operations frozen for the first Goal |
|---|---|
| Task | `POST /api/v1/tasks`; `GET /api/v1/tasks`; `GET /api/v1/tasks/{taskId}`; `POST /api/v1/tasks/{taskId}/commands/start`; `POST /api/v1/tasks/{taskId}/commands/rerun` |
| Run / recovery | `GET /api/v1/runs/{runId}`; `POST /api/v1/runs/{runId}/commands/cancel`; `POST /api/v1/runs/{runId}/commands/resume`; capability-gated `POST /api/v1/runs/{runId}/commands/retry-current-stage`; capability-gated `POST /api/v1/runs/{runId}/commands/restart-from-safe-boundary` |
| Needs Input | `GET /api/v1/needs-input-requests/{actionRequestId}`; `POST /api/v1/needs-input-requests/{actionRequestId}/commands/resolve` |
| Task-facing Source change | `POST /api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/previews/remove`; `POST /api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/commands/remove`; `POST /api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/previews/replace`; `POST /api/v1/tasks/{taskId}/source-associations/{sourceAssociationId}/commands/replace`; Source content、upload、processing 与 Evidence operations 由 RFC-005 提供 |
| Human Review | `GET /api/v1/review-packages/{reviewPackageId}`; `GET /api/v1/review-packages/{reviewPackageId}/draft`; `PUT /api/v1/review-packages/{reviewPackageId}/draft`; `POST /api/v1/review-packages/{reviewPackageId}/commands/submit`; `POST /api/v1/review-packages/{reviewPackageId}/commands/request-more-information`; `POST /api/v1/review-packages/{reviewPackageId}/commands/reject-all-and-request-regeneration`; `GET /api/v1/approved-strategies/{approvedStrategyVersionId}`; `POST /api/v1/approved-strategies/{approvedStrategyVersionId}/commands/withdraw` |
| Marketing Brief | `GET /api/v1/tasks/{taskId}/marketing-briefs`; `GET /api/v1/marketing-briefs/{marketingBriefVersionId}`; `POST /api/v1/marketing-brief-comparisons`; `POST /api/v1/marketing-briefs/{marketingBriefVersionId}/commands/revise` |
| Xiaohongshu Brief | `GET /api/v1/tasks/{taskId}/xiaohongshu-briefs`; `GET /api/v1/xiaohongshu-briefs/{xiaohongshuBriefVersionId}`; `POST /api/v1/xiaohongshu-brief-comparisons`; `POST /api/v1/xiaohongshu-briefs/{xiaohongshuBriefVersionId}/commands/revise` |
| Export | `POST /api/v1/tasks/{taskId}/export-previews`; `POST /api/v1/export-snapshots`; `GET /api/v1/export-snapshots/{exportSnapshotId}`; `GET /api/v1/export-snapshots/{exportSnapshotId}/content` |

- RFC-005 补齐 Source / Source Version / Source Association identity 与 content / upload / processing / Evidence operations，但不得改变 DEC-064 的四个 Source-change typed Operation，也不得把它们合并成 generic action。实现 Agent 不得增删、改名或临场合并上述 RFC-004 Operation。
- `GET /api/v1/tasks` 只有可选 `limit`，默认 `20`、最大 `50`；响应只有 `items` 与实际 `limit`，不承诺 total、cursor、任意 offset、搜索或完整历史。Task 在窗口外仍可通过稳定 identity 深链读取。
- Brief history 同样使用 server-bounded recent window，默认 `10`、最大 `25`，不提供搜索、批量恢复或无限历史承诺。Comparison 始终由显式 base / target Version identity 驱动，不依赖列表位置。
- 不在首个 Goal 添加 delete / purge、generic PATCH Task status、generic `/commands` dispatcher、batch、webhook、callback、SSE、WebSocket、public health diagnostics、login 或 Tenant operations。

##### Public schema and state catalog

- Common Schema 固定为 typed stable references、`ResourceRevision`、`DomainVersionReference`、`StageSummary`、`PrimaryAction`、revision-bound `Capability[]`、`CommandReceipt`、`ProblemDetails`、`FieldIssue` 与 typed conflict context。Public DTO 不复用 ORM / Checkpoint / Provider type。
- First-Goal wire fields 至少冻结如下；OpenAPI 可以按复用关系拆成 Components，但不得删减、改义或把不同 identity 合并：

| Schema | Required public fields / groups |
|---|---|
| `CreateTaskRequest` | `taskName`, `productCategory`, `promotionGoal`；`Idempotency-Key` 位于 Header |
| `TaskSummary` | `taskId`, `taskName`, `productCategory`, `taskStatus`, `currentStage`, `waitingReason`, `updatedAt`, `revision`, `primaryAction`, `capabilities` |
| `TaskOverview` | Summary identity / status / revision fields + `stages[]`, `activeRun`, `latestRun`, `needsInputRequest`, `reviewPackage`, `approvedStrategy`, `marketingBrief`, `xiaohongshuBrief`, `primaryAction`, `capabilities`；各关联对象只返回 typed reference |
| `StageSummary` | `stage`, `status`, `currentVersion`, `lastValidVersion`, `lastRun`, `waitingReason`, `updatedAt` |
| `CommandReceipt` | `commandId`, `commandType`, `taskId`, `acceptedAt`, `monitor`, `resultReference`（同步主结果存在时）；不返回 Attempt / Work Intent identity |
| `Run` | `runId`, `taskId`, `sourceRunId`, `status`, `currentStage`, `startedAt`, `updatedAt`, `completedAt`, `failureSummary`, `lastValidResult`, `primaryAction`, `capabilities` |
| `NeedsInputActionRequest` | `actionRequestId`, `taskId`, `revision`, `status`, `reasonType`, `reasonSummary`, `affectedStages[]`, `sourceReferences[]`, `conflictValues[]`, `allowedResolutionTypes[]`, `expectedRecovery`, `supersededBy` |
| `ReviewPackage` / `ReviewDraft` | stable Review / Package identity, immutable Package Version, upstream Version references, accepted review semantic groups, required decisions, limitations, Draft `revision`, full structured Draft content, save / supersession metadata |
| `ReviewOutcomeResult` | `reviewDecision`, optional `approvedStrategy`, updated Task / Stage references, optional continuation `CommandReceipt`; each typed Outcome has only its accepted applicable fields |
| Brief Version | Brief family / Version identity, `taskId`, `versionNumber`, validity / provenance / time, upstream Version references, six product semantic groups, `hypotheses`, `evidenceLimitations`, `risks`, `evidenceReferences` |
| `BriefComparison` | family, `baseVersion`, `targetVersion`, `changes[]` grouped by semantic group / field path with before / after / origin / edit intent / affected stages |
| `ExportPreview` / `ExportSnapshot` | typed export basis; Task / Brief / upstream references; hypotheses / limitations / risks summary; template version; Snapshot identity, `exportedAt`, `fileName`, `mediaType`, `contentLocation` |
| `ProblemDetails` | RFC 9457 `type`, `title`, `status`, `detail`, `instance` + stable `action`; optional typed `fieldIssues`, current Resource / revision / Version references, safe basis summary, `correlationReference`, `retryAfterSeconds` only when applicable |

- `null` 只表示 Schema 明确允许的“当前不存在 / 不适用”；字段缺失只用于 contract-defined optional extension。空列表使用 `[]`，不以 `null` 替代。Reference 至少包含其稳定 identity 和 resource kind；Version Reference 另含 `versionNumber`，mutable Reference 另含 `revision`，两者不互换。
- Capability enum 只含实际公共语义动作：`start`, `cancel`, `resume`, `rerun`, `retry_current_stage`, `restart_from_safe_boundary`, `resolve_needs_input`, `preview_remove_source`, `remove_source`, `preview_replace_source`, `replace_source`, `save_review_draft`, `submit_review`, `request_more_information`, `reject_all_and_request_regeneration`, `withdraw_approved_strategy`, `compare_brief`, `revise_marketing_brief`, `revise_xiaohongshu_brief`, `preview_export`, `confirm_export`。Capability 不是授权凭证。
- `PrimaryAction` 是窄 discriminated union：`none`；`navigate` + `intake / needs_input / review / results / recovery` target；或 `command` + 上述 Capability。服务端可以指出应打开哪个已存在工作台 Panel，但不能把 URL、前端 Route State 或任意 action payload 塞入该字段。导航不是写 Capability，Frontend 也不得从导航文案推断可写权限。
- Task family 固定为 `CreateTaskRequest`、`TaskSummaryList`、`TaskSummary`、`TaskOverview`；Task 状态沿用 Accepted `draft / running / waiting_for_input / waiting_for_review / paused / completed / failed / cancelled`，Stage 状态沿用 `not_started / ready / running / waiting_input / waiting_review / valid / invalid / failed / skipped`。
- Run family 固定公开 `queued / running / retrying / waiting_for_input / waiting_for_review / paused / cancellation_requested / completed / failed / cancelled / superseded`。只有 `queued / running / retrying / cancellation_requested` 触发轮询；业务等待、manual recovery 与终态停止自动轮询。Run representation 包含 identity、Task reference、来源 Run（适用时）、状态、当前 / 最近 Stage、权威时间、safe failure summary、Primary Action 与 Capability，不公开 Attempt、Lease、Fence、Checkpoint 或 Provider payload。
- Needs Input / Source-change family 固定为 `NeedsInputActionRequest` + discriminated `NeedsInputResolution`，以及 `SourceChangePreview` / `SourceChangeBasis` / typed Confirm requests。RFC-005 只补齐它拥有的 Source / Version / Association / item-result reference Schema。
- Review family 固定为 immutable `ReviewPackage`、mutable `ReviewDraft`、typed full-snapshot `PutReviewDraftRequest`、四个 Outcome request / result、immutable `ReviewDecision` 与 `ApprovedStrategyVersion`。Candidate edit / select 只存在于 Draft；QC / validation success 不得映射为 approval。
- Brief / Export family 固定为 immutable `MarketingBriefVersion`、`XiaohongshuBriefVersion`、`BriefComparison`、family-specific Revise request / result、`ExportPreview`、`ConfirmExportRequest`、`ExportSnapshot` 与 Markdown content response。六个产品语义组、Hypotheses、Evidence Limitations、Risks 与 Evidence references 必须复用产品 / RFC-005 authority，不创建平行字段定义。
- Every non-read create / command that DEC-063 requires to survive uncertain retry requires `Idempotency-Key`; every mutable or version-sensitive write carries its real typed expected revision / base Version / basis. OpenAPI response matrix must preserve first success versus committed replay (`201` or `202` first, `200` replay) and typed `409` distinctions.
- P-55A 的 Problem Type / action catalog 是封闭的首 Goal集合；增加只会被同一受控 Workbench 忽略的内部 error 没有价值。RFC-005 / 007 可以提供该 catalog 已预留的 safe Source item details、correlation reference 与 `Retry-After`，不得创建第二 Problem envelope。

##### Compatibility and generated-client adoption

- `/api/v1` 只允许 additive evolution：新增 optional response field、optional request capability、new Operation 或新 Problem Type，且同一仓库的 Frontend 能安全忽略未知字段 / Capability。删除、改名、改变既有字段类型 / requiredness / enum 含义、改变幂等或状态码语义、复用 identity 字段，均属 breaking change，必须新 RFC；若确需公开破坏性 Contract，使用 `/api/v2`，首个 Goal 不维护并行双版本。
- Public enum 新值会改变 UI 控制流，不视为“天然安全的 optional addition”。增加 Task / Stage / Run / Primary Action / Problem action 值时必须同一 PR 更新 Contract、generated client、Frontend unknown fallback、Contract Tests 与文档；Frontend 对未知值只进入只读 `refresh / unavailable` 安全投影，不猜测可写 Capability。
- Frontend 使用 DEC-055 已接受的 `openapi-typescript` 生成不可手改的派生 Schema，并由 `openapi-fetch` 的窄 Adapter 消费。Contract 或 generator 变更后必须重新生成；CI 对生成结果执行 clean-diff，禁止手写平行 DTO 或为绕过生成器直接扩展 `any`。
- Goal 的依赖顺序为：Accepted RFC-004 / 005 / 007 → OpenAPI Contract Issue → generated client issue → Backend conformance / typed Adapter vertical slices。API Handler 与 Web Workbench 不得先于权威 Contract 自行发明 Request / Response shape。
- OpenAPI generator、validator 和精确 package patch 版本在 Goal Issue 中根据当时官方兼容证据锁定；若工具不能表达已接受的 Contract，应停止并提出工具替代或 RFC amendment，不得弱化 Contract 迁就生成器。

##### Contract tests and RFC closure readiness

- Contract PR 必须验证：OAS 3.1 解析 / validation、所有 `$ref` 可解析、`operationId` 唯一、example 符合 Schema、所有成功与 Problem media types / status 明确、generated client clean-diff。
- Backend Contract Tests 覆盖每个 Operation 的代表性成功路径，并重点覆盖首次提交 / 重放、stale revision、superseded resource、capability conflict、Run polling stop、Review Submit atomic continuation、Brief revise impact、Export basis conflict、Snapshot download 与 fixed-workspace / Origin boundary；不为每个字段排列组合堆叠低概率 case。
- Frontend typed-fixture Contract Tests 覆盖每类 Resource / Command / Problem action 和 unknown enum / Capability 的只读 fallback。Browser E2E 只覆盖产品固定闭环与代表性 conflict / temporary unavailable，不复制整套 API matrix。
- RFC-005 / 007 接受后若只是填充本 RFC 已声明的 Source / Evidence Schema refs 或 operational extensions，不重开 RFC-004；若要求改变 Resource ownership、Operation topology、Problem envelope、workspace boundary 或 public state semantics，则立即停止并提出 RFC-004 amendment。
- P-57A 被接受后，RFC-004 的 DQ-01～10 才算全部有 Accepted Decision；随后仍须进行独立 Final Consistency Review，清理跨 Decision / RFC-005 / RFC-007 handoff 冲突，再单独请求用户接受 RFC-004 整体。P-57A 接受本身不授权合并 PR #55、关闭 Issue #54、创建 OpenAPI 或启动实现。

**优点：** 在开发前把实现 Agent 最容易临场发明的 Operation、状态、Schema family、窗口限制、兼容与生成链闭合，同时把 Source / Observability 的真实所有权留给后续 RFC；可直接导出独立 Issue 和 Contract Tests。

**代价：** Contract Artifact 必须在 API / Frontend 实现之前独立完成，且公共 enum / Operation 变更需同步 generated client；RFC-005 / 007 接受后还需把其拥有的 Schema 与安全运维扩展接入同一 Description。

#### P-57B — Implementation-generated OpenAPI + Frontend Snapshot

先由 Backend Handler / serializer 定义接口，再从实现生成 OpenAPI；Frontend 把某次生成结果复制为类型输入。

**优点：** 后端开发启动快，Schema 看起来与当前 Handler 一致。

**代价：** 实现成为事实源，Contract Review 发生在代码之后；生成时机与复制快照可能漂移，Frontend / Backend 无法在实现前并行，也违反 DEC-055 / DEC-063 的 Contract-first 边界。

#### P-57C — Exhaustive Platform Contract Before Development

在 RFC-004 内同时定义 Source / Evidence 每个字段、Observability、认证、多租户、Retention、全部历史分页、通用搜索、Push、未来格式和每个内部错误。

**优点：** 表面上一次覆盖所有未来接口。

**代价：** 覆盖大量未授权范围和未接受 RFC 所有权，产生无需求依据的长期兼容承诺，并违反适度校验与首个 Goal 边界。

#### Recommendation

Choose P-57A. It closes the public contract tightly enough for independent implementation and testing while keeping RFC-005 / 007 handoffs explicit and avoiding an oversized speculative API platform.

## Round 4 decision status and next gate

- 用户于 2026-08-07 明确接受 P-57A，并归档为 [DEC-066](../decisions/dec-066-openapi-contract-catalog-compatibility-and-generated-client-adoption.md)；P-57B / P-57C 保留为未采用 Alternative。
- `DQ-10 = ACCEPTED`；RFC-004 的 DQ-01～10 均已有 Accepted Decision。
- Final Consistency Review 已于 2026-08-07 通过；用户随后明确接受 RFC-004 整体，并允许合并 PR #55、关闭 Issue #54、进入 RFC-005 策划 Gate。
- RFC-004 = `ACCEPTED`；下一活动 Gate 为 RFC-005 策划。本状态仍不创建 OpenAPI Artifact、不启动实现、Spike 或 Goal。

## Risks and stop conditions

- Stop if a proposed public operation changes accepted Product behavior or persistence / workflow invariants rather than transporting them.
- Stop if one field is asked to serve as Domain Version, mutable revision, command identity, Run identity and idempotency key.
- Stop if RFC-005 or RFC-007 cannot own its delegated contract without producing duplicate authorities.
- Stop if a public contract requires login, RBAC, multi-tenancy, push transport, broad compliance or physical purge in the first Goal.
- Stop if implementation evidence later proves the accepted OpenAPI toolchain cannot represent the contract without weakening it; propose an RFC amendment rather than silently hand-writing a second client contract.

## Final Consistency Review（PASS，2026-08-07）

### Review scope

- P-48A～P-57A、DEC-063～066 与 DQ-01～10 的完整性和双向追踪；
- Product Specification、Frontend Architecture、RFC-001 / 002 / 003 / 006 的已接受上游不变量；
- RFC-005 的 Source / Fragment / Evidence 所有权与 RFC-007 的 Observability / operational 参数所有权；
- Resource / typed Command topology、identity / revision / idempotency、async receipt / Run、Task / Recovery / Review、Brief / Export、Problem、fixed-workspace 与 OpenAPI adoption；
- Testing Strategy、Implementation Readiness、Traceability、授权边界与 PR #55 的实际文档差异。

### Findings

- Critical：0
- Important：0
- Suggestion：0
- Decision Conflict：NONE FOUND

没有发现需要新产品取舍、改变已接受架构或降低验收标准的问题。本轮只把用户接受的 P-57A 归档、消除 DQ-10 与入口状态的陈旧描述，并未改变 P-57A 的规范性内容。

### Consistency conclusions

| Review surface | Conclusion |
|---|---|
| Decision closure | DQ-01～10 分别由 DEC-063～066 支撑，未把 Proposal 或 Alternative 误标为 Accepted |
| Product behavior | Task 创建不隐式启动；Needs Input、Human Review、Brief version、证据限制、局部重跑与 Markdown export 均保持 Accepted Product Behavior |
| Identity and concurrency | stable identity、Domain Version、mutable revision、Idempotency Key、Command、Run 与 Attempt 职责分离；无 Hash / Digest 公共要求 |
| Async and recovery | `202` 只表示耐久接受；同输入重放、Run polling stop、Cancel requested、Resume / Rerun 新 Run 与 typed recovery 一致 |
| Human Review | QC / validation 不等于 approval；immutable Package、revision-safe Draft、explicit outcomes、Approved Strategy 与 atomic continuation 一致 |
| Contract boundary | RFC-004 拥有 HTTP topology / public semantics；RFC-005 / 007 可填充其已委托 Schema / operational extension，但不能创建第二 envelope 或改变所有权 |
| Frontend adoption | private WorkbenchProjection、generated client、unknown read-only fallback 与 clean-diff 顺序一致，不建立平行 DTO 或前端业务状态机 |
| Security and scope | fixed Workspace + loopback same-origin 边界诚实，不伪装登录 / RBAC / 多租户；校验与本地演示风险相称 |
| Verification | Contract / Backend / Frontend / Browser 分层覆盖代表性路径和关键不变量，不堆叠低概率字段矩阵 |
| Authorization | 未创建 OpenAPI、API、Client、DB、Migration、Spike 或 Goal；Final Review PASS 不等于 RFC Accepted 或实现授权 |

### Five-axis verdict

- **Correctness：PASS。** Operation、状态、错误、版本、幂等、Review 与 Export 语义完整承接 Accepted Decisions。
- **Readability：PASS。** 公共所有权、精确目录、状态目录、Non-goals 与后续 Gate 可独立读取。
- **Architecture：PASS。** Contract-first、模块边界、Current-Truth ownership 与 RFC-005 / 007 handoff 无冲突。
- **Security：PASS。** 没有 Secret、伪认证、越权 Workspace selector 或不成比例的防御设计。
- **Performance：PASS。** 最近 Task / Brief 窗口有界，轮询只在活动 Run 状态进行，没有无界列表或 Push 基础设施扩张。

完整可持续审查记录见 [RFC-004 Final Consistency Review](../reviews/review-2026-08-07-rfc-004-final-consistency.md)。

## Outcome

DQ-01～10 已全部闭合，Final Consistency Review = PASS。用户于 2026-08-07 明确接受 RFC-004 整体，并允许合并 PR #55、关闭 Issue #54、进入 RFC-005 策划 Gate。

**Final Decision：RFC-004 = ACCEPTED。** RFC-004 现为公共 HTTP 与 Human Review Architecture 基线；后续 RFC、Readiness Artifact、Contract 与实现不得违反或静默绕过其边界。该接受不创建 OpenAPI Artifact，不授权 API / Frontend / Database 实现、Technical Spike、数据迁移或 Goal 激活。
