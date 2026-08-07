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
| DQ-01 | Contract authority, namespace and Resource / Command topology | PROPOSED as P-48 |
| DQ-02 | Revision preconditions, idempotency and conflict semantics | PROPOSED as P-49 |
| DQ-03 | Durable asynchronous acceptance, polling and capability projection | PROPOSED as P-50 |
| DQ-04 | Task creation, recent-task index and Workbench read models | PENDING |
| DQ-05 | Needs Input, Source-facing task actions, cancel, resume, rerun and recovery commands | PENDING |
| DQ-06 | Review Package, Review Draft, Review Decision and Approved Strategy protocol | PENDING |
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

## Proposal status and next gate

- P-48 / P-49 / P-50 are `PROPOSED`.
- No Current Truth document may describe any option as Accepted before explicit user confirmation.
- After this round, the next proposal group will cover DQ-04 through DQ-06: Task / Workbench query shape, recovery commands, and Human Review protocol.
- This draft does not authorize OpenAPI generation, code, dependency installation, tests, Technical Spikes or Goal activation.

## Risks and stop conditions

- Stop if a proposed public operation changes accepted Product behavior or persistence / workflow invariants rather than transporting them.
- Stop if one field is asked to serve as Domain Version, mutable revision, command identity, Run identity and idempotency key.
- Stop if RFC-005 or RFC-007 cannot own its delegated contract without producing duplicate authorities.
- Stop if a public contract requires login, RBAC, multi-tenancy, push transport, broad compliance or physical purge in the first Goal.
- Stop if implementation evidence later proves the accepted OpenAPI toolchain cannot represent the contract without weakening it; propose an RFC amendment rather than silently hand-writing a second client contract.

## Outcome

Pending. RFC-004 remains Drafting and has no implementation authorization.
