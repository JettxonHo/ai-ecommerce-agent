# RFC-007：Minimal Observability and Runtime Operations for MVP-0

## Metadata

- **Status:** DRAFTING — PROPOSALS PENDING USER DECISION
- **Date:** 2026-08-07
- **Issue:** [#58](https://github.com/JettxonHo/ai-ecommerce-agent/issues/58)
- **Pull Request:** TBD
- **RFC Acceptance:** NOT GRANTED
- **Implementation Authorization:** NOT GRANTED
- **Goal Activation:** NOT GRANTED

## Problem

Product Specification、RFC-001～006、Frontend Architecture 与快速 MVP-0 分期已经接受，但运行期诊断仍缺少最后一个可执行契约：API、Worker、Workflow、Retrieval、Model Runtime 与 Frontend 如何使用同一关联身份解释一次运行；错误如何同时满足用户可操作与操作者可诊断；Timeout / Retry / Backoff 由谁拥有；哪些内容可以进入日志；本地演示如何证明可靠性，而不先建设完整 Observability Platform。

如果留给实现 Issue 临场决定，最容易出现四类问题：SDK 默认重试与项目重试叠加、日志包含 Source / Prompt / Secret、API / Worker 使用不同 correlation 字段、以及为了“完整”提前引入 Collector、Dashboard、Alerting 与 Circuit Breaker 平台。快速 MVP-0 需要关闭这些风险，但不需要生产级遥测基础设施。

## Context and authority

### Accepted upstream authority

- [DEC-033](../decisions/dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)：分层 Runtime identity、结构化错误、Retry ≠ Rerun、总体 Budget、敏感数据边界与可观测性目标；具体 Provider、参数和物理实现原本留给 RFC-007。
- [RFC-002](rfc-002-persistence-and-transaction-architecture.md)：业务事务重试最多 1 次初始 + 2 次重试，且每次使用全新 UoW / Session；外部调用不得进入数据库事务重试循环。
- [RFC-003](rfc-003-langgraph-runtime-and-checkpoint-architecture.md)：Durable Work Intent、Lease / Heartbeat / Fencing、协作式取消、Safe Resume 与 Current-Truth-first Reconciliation；RFC-007 只拥有运维字段、时序和诊断投影。
- [RFC-004](rfc-004-api-and-human-review-architecture.md)：RFC 9457 Problem、Run state、`correlationReference`、`retryAfterSeconds`、轮询停止语义与固定工作区 HTTP 边界；RFC-007 不创建第二错误协议。
- [RFC-005](rfc-005-source-processing-and-retrieval-architecture.md)：RetrievalRun、Evidence limitation、显式 degradation 与 Source / Evidence payload 边界；RFC-007 不保存正文、Candidate 或向量。
- [RFC-006](rfc-006-llm-runtime-and-structured-output.md)：OpenAI SDK `max_retries=0`、单一 Model Operation Budget、Provider call identity、payload-free telemetry 与 Secret boundary；RFC-007 不扩大 allowlist。
- [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md)：适度校验、禁止新增 Hash / SHA-256 要求、禁止低概率防御矩阵和机械 Rubric。
- [DEC-070](../decisions/dec-070-fixed-embedding-contract-and-accelerated-mvp0-adoption.md)：MVP-0 以快速核心闭环为目标，完整 Retrieval、完整 Readiness 与非必要平台能力后移。

### Current official capability evidence

- Python 标准库 [`logging.LoggerAdapter`](https://docs.python.org/3/library/logging.html#loggeradapter-objects) 支持把上下文字段加入 `LogRecord`；MVP-0 可以在不增加第三方 Logging SDK 的情况下输出结构化事件。
- OpenAI 官方 Python SDK 文档说明 SDK 默认对连接错误、408、409、429 与 5xx 重试两次，默认请求 Timeout 为 10 分钟，并公开成功响应 `_request_id` 与失败异常 `request_id`。这验证了 RFC-006 `max_retries=0` + 项目自有 Budget / Timeout / request ID 记录的必要性，而不是授权使用 SDK 默认值。
- [W3C Trace Context](https://www.w3.org/TR/trace-context/) 定义跨服务 HTTP trace context；MVP-0 只有本地受控 Web / API / PostgreSQL Worker，不需要先暴露或信任客户端 `traceparent`，但内部命名避免阻断未来兼容。
- [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/) 是生成、收集与导出 traces / metrics / logs 的框架，本身不是 Observability Backend。MVP-0 没有已选择的 Collector、Backend、Dashboard、On-call 或多服务部署，因此本 RFC 把其 SDK / Collector 接入延后，而不是声称不再需要可观测性。

外部资料只证明能力与当前默认行为；下列项目方案仍需用户明确接受。

## Goals

- 为每次 HTTP 接受、Run、Skill、Node、Attempt、Provider call、Retrieval、Review continuation 与错误提供可关联的最小诊断链。
- 让结构化日志、耐久 Runtime / Error records 与公共 Problem / Run projection 各自职责清晰，不形成第二业务事实源。
- 冻结 Timeout / Retry / Backoff 的唯一所有者和无嵌套规则，保留既有具体预算。
- 在不保存 Secret、Prompt、Source 正文、评论原文或 Provider payload 的情况下支持本地问题定位。
- 为固定 MVP-0 验收包生成可审阅的运行摘要和失败证据。
- 明确哪些完整 Observability 能力后移到 MVP-1 / 部署 Gate。

## Non-goals

- OpenTelemetry SDK / Collector、OTLP、Prometheus、Grafana、Jaeger、Sentry、LangSmith 或其他 SaaS / Backend；
- Dashboard、Pager、On-call、自动告警路由、SLO 平台、跨环境聚合或长期日志仓库；
- Circuit Breaker 库、服务网格、分布式采样策略或多 Provider 健康路由；
- 完整 Prompt / Context / Source / 评论 / Provider request / response 保存；
- 通用 Redaction Rule Engine、DLP、PII Scanner、低概率 Secret 变体矩阵或 Hash / SHA-256；
- 新公共错误 envelope、内部 Exception / SQLSTATE / Checkpoint / Lease / Fencing 暴露；
- 物理数据删除、Backup / Retention 执行、生产运维或公开部署。

## Authority boundaries

RFC-007 owns:

- Runtime diagnostic event envelope、关联传播和本地 sink；
- durable RuntimeErrorRecord 的最小 MVP-0 投影与 public correlation handoff；
- Timeout / Retry / Backoff ownership table and operational configuration discipline；
- local operator evidence、diagnostic summary 与 deferred telemetry capability catalog。

RFC-007 does not own:

- Business Current Truth、Audit、State Transition、Provider Call Ledger 或 RetrievalRun；
- public Problem type / Run state / HTTP topology；
- Workflow ownership、Lease、Checkpoint、business transaction retry 或 Model Recovery budget；
- Source / Evidence / Prompt / Candidate payload policy；
- Frontend product state or release acceptance。

## Decision map

| Decision Question | Topic | Status |
|---|---|---|
| DQ-01 | Diagnostic event、correlation、durable error 与 redaction boundary | PROPOSED — P-68A recommended |
| DQ-02 | Timeout / Retry / Backoff ownership and bounded MVP-0 behavior | PROPOSED — P-69A recommended |
| DQ-03 | Local operational evidence and deferred observability capabilities | PROPOSED — P-70A recommended |

## Proposal Round 1

### P-68 — Minimal diagnostic plane and correlation

#### P-68A — Allowlisted JSON Lines + server-generated correlation + durable error reference（推荐）

- API 与 Worker 使用 Python standard logging 输出一行一个 JSON object 到 stdout / stderr；不增加 Logging SDK 或应用内日志文件轮转。日志是非权威诊断流，业务状态继续来自 PostgreSQL Current Truth / Runtime records。
- 统一最小 event envelope：`occurred_at`、`level`、`event_name`、`service`、`environment`、`correlation_id`，并按场景加入已有 `task_id`、`run_id`、`skill_run_id`、`node_execution_id`、`attempt_id`、`error_id`、`model_call_id`、`provider_attempt_id`、`retrieval_run_id`、`review_id`、`source_version_id`。不要求每条事件填满所有 identity。
- `correlation_id` 由 Server 在 HTTP 接受或 Run 创建边界生成；同一异步逻辑链通过 Durable Receipt / Work Intent / Run record 传播，不能由 Browser 选择或扩展 Workspace / Task scope。新 Rerun 创建新 `run_id` 和新的 root correlation；技术 Retry 保持同一 correlation，使用新的 Attempt identity。
- public `ProblemDetails.correlationReference` 与 Run safe failure summary 只投影稳定、不可反推内容的 `error_id` 或 correlation reference；Frontend 不依赖其格式、不把它当 Resource identity。
- MVP-0 以 PostgreSQL `RuntimeErrorRecord` 保存最小耐久错误引用：identity chain、稳定 `error_category`、severity、retryability、disposition、component、`user_safe_message`、受控 `operator_summary`、Provider request / response reference（如存在）、时间和 remediation option。它不保存 raw exception message、stack、Prompt、Source /评论原文、Provider payload 或 HTTP Header。
- 日志采用正向 allowlist，不建设通用 Redaction Engine：只记录 identity、version、status、duration、usage、有限 error category / disposition 与预先定义的安全 summary。Secret value、Authorization / Cookie、连接字符串、完整 URL query、request / response body、Prompt、Source 正文、Review 内容和 Provider payload 从数据结构源头不进入日志。
- Unexpected exception 记录 `error_id`、异常类型的稳定分类、component 和通用 operator summary；开发者可在本地进程控制台看到受控 stack，但不得把异常 message / locals 自动序列化为结构化字段或返回 Browser。

**优点：** 无新运行依赖即可关联一次完整本地执行；与 RFC-004 / 006 allowlist 和 Durable Work Intent 对齐；风险集中在真实的 Secret / payload 边界，不建设泛化安全平台。

**代价：** 没有跨服务 span waterfall、集中检索或远程 Dashboard；stdout 生命周期由本地启动方式管理，应用不承诺长期日志保留。

#### P-68B — OpenTelemetry SDK + Collector + trace / log export

首个 Goal 接入 OTel API / SDK、自动 instrumentation、Collector 与一个本地 Backend，使用 trace / span / log correlation。

**优点：** 标准化、更接近未来分布式部署，并可获得 span timeline。

**代价：** 引入多项依赖、Collector 配置、Exporter 生命周期和新的验收面；当前没有多服务部署或 Backend 需求，延迟核心闭环。

#### P-68C — Free-text logs + exception stack only

只打印人工文案和异常堆栈，不持久化 RuntimeErrorRecord，也不规定关联字段。

**优点：** 实现最少。

**代价：** API / Worker / Provider failure 无法稳定关联，公共 correlationReference 无权威来源，容易泄漏正文或 Secret，也不能支撑异步恢复验收。

### P-69 — Timeout, retry and backoff ownership

#### P-69A — One owner per boundary + inherited budgets + bounded local polling（推荐）

- 不创建全局“自动重试一切”Middleware。每类 Retry 只有一个所有者，并沿用已接受预算：数据库短事务由 RFC-002 Transaction Runner 拥有；Workflow Node / Work Intent 由 RFC-003 Runtime 拥有；Model transport / recovery 由 RFC-006 Model Runtime 拥有；Browser 只重试安全读取和携带 Idempotency-Key 的不确定提交重放。
- OpenAI SDK 固定 `max_retries=0`；项目 Model Runtime 继续遵守“最多 2 个 Model Call、共享最多 1 次额外传输重试、整个 Operation 最多 3 个 Provider Attempt”和 Overall Deadline。Provider `Retry-After` 只有在剩余 Deadline 内才遵守。
- Timeout 使用层级 Deadline，不叠加无限内层计时器：HTTP request / database transaction、Provider attempt、Node active execution、Run active segment 各自显式配置；`waiting_for_input` / `waiting_for_review` 不计为技术超时。精确 Model Profile 秒数按 RFC-006 要求，在 Model Adapter Issue 的 bounded compatibility slice 中用固定 Fixture 校准并由 Sol Review，Luna / Terra 不得临场改变。
- 非 Model 的可重试 Node 默认只允许 **1 次额外技术尝试**；Authentication / Permission、invalid request、revision conflict、Validation / Data Integrity、cancel / superseded 和未知分类不自动重试。若上游 Accepted RFC 已给出更严格预算，以更严格者为准。
- Backoff 使用 bounded exponential + small jitter；实现配置必须包含 initial delay、maximum delay、attempt limit 和 overall deadline，且 sleep 发生在 open transaction / UoW / database connection 之外。MVP-0 不冻结一组跨所有组件复用的秒数。
- Frontend 对 `queued / running / retrying / cancellation_requested` 轮询；默认 1 秒，连续无变化时 2 秒、最大 5 秒；状态变化后回到 1 秒。对 `429 / 503` 优先遵守 1～30 秒内的 `Retry-After`，否则使用同一 1 / 2 / 5 秒上限；进入业务等待、manual recovery 或终态立即停止。浏览器离开页面不取消 Run，重新进入通过 Run resource 恢复。
- Circuit Breaker 的完整 `closed / open / half_open` 实现延后。MVP-0 依靠单一 Provider、硬 Attempt / Deadline、Durable failed / recovery state 和人工重跑避免故障放大；不得伪装已经具备生产 Circuit Breaker。

**优点：** 直接消除 SDK / Workflow / DB 嵌套重试；沿用既有风险预算，只新增本地轮询和配置所有权；无需通用容错框架。

**代价：** 不提供自动熔断；精确 Model Timeout 需要在对应实现 Issue 的有限兼容证据中校准，而不是在无真实调用证据的策划文档中臆测。

#### P-69B — SDK / framework defaults own retries and timeouts

保留 OpenAI SDK、HTTP client、database driver 与 Workflow framework 各自默认重试 / timeout。

**优点：** 配置和自有代码少。

**代价：** 默认预算相乘、真实调用次数不可解释；OpenAI SDK 默认 timeout 与 retry 明显不符合已接受的单一 Budget；可能重复外部调用并延长失败时间。

#### P-69C — No automatic retry anywhere

所有技术失败立即终止，由用户手动 Rerun。

**优点：** 行为最简单。

**代价：** 一次瞬时连接 / 429 / serialization failure 即破坏演示闭环，并把技术 Retry 错误地升级为新业务 Rerun。

### P-70 — MVP-0 operational evidence and deferred capabilities

#### P-70A — Durable records + correlated local timeline + release summary（推荐）

- MVP-0 不建设 OTel、Metrics SDK / Backend、Dashboard 或 Alerting Service。运行证据由三层组成：PostgreSQL 权威 Runtime / Error / Provider / Retrieval records；stdout JSON diagnostic events；固定验收包生成的只读 Release Evidence Summary。
- Release Evidence Summary 只针对固定 Anchor SKU 三个变体 + mutation，列出 Run outcome、stage / node durations、attempt / retry / timeout / fallback counts、error category、resume / stale rejection / cancellation、Provider usage / request references 与 known limitations。它是测试证据，不是业务 Current Truth，也不设置无基线的加权分数。
- DEC-033 的可靠性不变量继续是硬门禁：partial business write、duplicate business version、stale review success、stale checkpoint resume success、invalid Evidence commit 和 cross-task leakage 必须为零。所谓 100% observability completeness 在 MVP-0 按固定验收 Run 检查 identity / category / audit / limitation 是否存在，不建立持续 Metrics pipeline。
- Operator interface 限于本地 Run state、safe failure summary、correlation reference、结构化控制台事件和文档化恢复步骤；高风险 Data Integrity / Scope leakage / Current Truth conflict 进入 failed / manual recovery 并停止相关模块，不自动发 Page / Email / Slack。
- 不自动创建或清理日志文件；stdout 由本地启动进程管理。耐久 Runtime / Error records 随 Task 数据保留，MVP-0 不执行自动 Retention / Purge，不向用户承诺物理删除。敏感 Payload 仍禁止进入这些 records。
- MVP-1 / deployment Gate 再决定 OTel API / SDK、Collector / Backend、metrics cardinality、sampling、Dashboard、alert threshold / channel、Circuit Breaker 与日志保留。迁移必须复用本 RFC 的 event names / identity / allowlist，不改变业务状态或 public Problem envelope。

**优点：** 足以定位本地核心闭环并验收关键不变量；不把没有部署需求的遥测基础设施放进关键路径；未来仍保留标准化升级入口。

**代价：** 没有持续趋势、跨环境查询或自动告警；Release Summary 只代表固定验收运行，不能冒充生产 SLO。

#### P-70B — Full local observability stack before MVP-0

加入 Collector、trace / metrics backend、Dashboard、alerts 和 circuit breaker，再开始业务切片。

**优点：** 运维能力完整，未来扩展更顺畅。

**代价：** 把演示前门禁扩大为平台项目，显著增加依赖和故障面，违反快速 Gate 与适度校验。

#### P-70C — No operational evidence beyond test pass / fail

只保留 CI 结果，不要求 Runtime record、correlation 或 release summary。

**优点：** 文档和实现最少。

**代价：** 异步 Run、Retry、Resume、Provider failure 与 Current Truth commit 无法解释；测试失败之外的本地演示问题难以定位。

## Recommended combination

推荐 **P-68A + P-69A + P-70A**。这是能支撑本地单工作区异步工作流、真实 Provider Smoke 与人工 Review 的最小运行诊断面，同时显式延后完整 Observability Platform。

若接受，该组合将：

- Concretize DEC-033 的 MVP-0 日志、关联、Error、Retry 和运维物理载体；
- 明确 Amends DEC-033 的首阶段交付：Root Trace / Metrics / Alerting / Circuit Breaker 的完整物理实现延后，但其业务不变量、身份链和未来能力不删除；
- Extend RFC-003 / 004 / 005 / 006 的运维 handoff，不改变其权威契约；
- Conform DEC-039 / 070 的适度校验与快速分期。

在用户明确接受前，P-68A / P-69A / P-70A 仍为 Proposed，不创建 DEC，不把推荐方案写成 Accepted Current Truth。

## Testing strategy if accepted

- Event envelope unit tests：必需 base fields、按场景 identity、稳定 event name 和合法 level；不测试所有 identity 排列组合。
- Representative payload-boundary tests：一个合成 Secret、一个 Source / Prompt payload、一个 Provider error，证明 allowlist 输出不包含值；不建设低概率变体矩阵。
- Real PostgreSQL integration：HTTP acceptance → Work Intent → Worker → Run / Error / Provider / Retrieval references 保持 correlation；Retry 使用新 Attempt、不创建重复业务版本。
- Deterministic clock tests：非 Model 单次额外 Retry、取消中断、Deadline 阻止后续 Attempt、Backoff 在 transaction 外、`Retry-After` 超过剩余 Deadline 时不等待。
- API Contract：Problem / Run 只暴露 safe `correlationReference` / `retryAfterSeconds`，不暴露内部 error、Checkpoint、Lease、Provider payload。
- Frontend unit / browser：active polling 1 / 2 / 5 秒、状态变化重置、等待 / 终态停止、离页不取消、重进恢复、503 后保留 stale snapshot。
- Release Candidate：固定验收包生成一次 Release Evidence Summary；一次真实 Provider Smoke 记录 request reference、latency、usage、status 与 limitation，不记录 payload / Secret。

## Rollback and migration

- JSON event fields additive only；消费者必须忽略未知字段。MVP-0 没有远程 sink，因此 rollback 为停止新增 event emitter 或恢复上一版本，不迁移业务数据。
- RuntimeErrorRecord 是引用式耐久记录；Schema 变化使用常规受控 Migration。失败时停止 Runtime module，不删除失败历史或 Current Truth。
- 未来接入 OTel 时，以当前 identity / event allowlist 作为 attributes / log body 输入；不得反向要求业务层依赖 OTel SDK type。

## Risks and stop conditions

- Stop if diagnostics must contain Secret、Authorization、Prompt、Source /评论原文、完整 Provider payload or raw request / response body to proceed.
- Stop if a new public error envelope、Run state or operation is required; return to RFC-004 amendment.
- Stop if SDK / framework retry cannot be disabled or actual Attempt count cannot fit accepted Budget.
- Stop if correlation cannot survive Durable Work Intent / Worker restart without using process memory as authority.
- Stop if implementation requires OTel / Collector / Dashboard / Alerting / Circuit Breaker platform to make the MVP-0 core loop correct.
- Stop if Data Integrity、Scope leakage、stale review / checkpoint or duplicate business version appears; do not treat it as an observability-only issue.
- Stop if any proposal introduces Hash / SHA-256、generic security scanning or mechanical aggregate acceptance score.

## Acceptance and authorization boundary

- User acceptance of P-68A / P-69A / P-70A would close DQ-01～03 and authorize archiving a Decision plus final RFC consistency review only.
- RFC-007 overall still requires a separate explicit user acceptance after review.
- RFC acceptance, Issue #58 work or its documentation PR does not authorize implementation, dependency installation, Technical Spike, Live Provider or actual Goal.
- Development can begin only after the complete rapid MVP-0 package is shown, compact Readiness Review passes, and the user explicitly says “进入 MVP-0 Goal”.
