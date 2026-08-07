# RFC Register（RFC 清单与优先级）

> **Status: ACTIVE — DEC-038 Accepted（RFC Planning Phase）**
> **治理来源：** DEC-034 · [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md)
> **关联：** [Architecture Readiness Review v1 Issue #3](https://github.com/JettxonHo/ai-ecommerce-agent/issues/3)
> **纪律：** 本文件**只**登记 Required RFC 的**清单与优先级**，**不替用户接受任何 RFC**。每个 RFC 的实际创建（`rfc-NNN-*.md`）、讨论、接受与否，均由用户在后续 Decision Gate 决定。RFC ≠ Accepted Decision。
> 
> **Current truth（2026-08-07）：** Product Specification 已整体闭合；RFC-001 / RFC-002 / RFC-003 / RFC-006 = `ACCEPTED`；RFC-006 的 P-28A～P-35A 已由 DEC-052～054 接受，DQ-01～DQ-08 已闭合且 Final Consistency Review = PASS，用户已明确接受 RFC 整体；Frontend Architecture P-36～P-41、Final Consistency Review 与整体接受均已完成；当前进入 [RFC-004](rfc-004-api-and-human-review-architecture.md) 策划 Gate，Issue #54 承载本轮工作，RFC-004 = `DRAFTING`，P-48A～P-56A / DQ-01～09 已由 DEC-063～065 接受，P-57 / DQ-10 为 `PROPOSED`，Final Review 与整体接受仍待后续 Gate；RFC-005 / 007 = `PROPOSED`。FND-001～003 已完成。Wave 1 中 ARP-01 / 04 / 10 完整 Accepted，ARP-02 / 03 / 09 仅 TS-01 Minimum Slice Accepted。当前授权 RFC 与 Readiness 规划，不授权 TS-01～TS-05 执行、Business / Production Implementation 或实际 Goal；已完成的 Spike-001 不在本禁令所指范围内。
> **Historical snapshot：** 下列“当前阶段”长段和 RFC-001 DQ / Foundation 时间线保留其形成时状态；如与上面的 Current truth 或最新 Accepted Decision 冲突，以后者为准。
> **当前阶段：** DEC-038 已接受，**RFC-001 已于 2026-07-30 被用户正式接受（`ACCEPTED`）**，DQ-01~DQ-10 全部 ACCEPTED 且 Final Consistency Review 通过。**RFC-002 已于 2026-08-04 被用户正式接受（`ACCEPTED`）**：RFC-002-DQ-01~DQ-17 全部 ACCEPTED（Pending Decision Questions = 0）；最终一致性审查未发现跨 DQ 实质架构冲突，Documentation-only Final Consistency Remediation 已消除文档状态冲突（详见 `rfc-002-persistence-and-transaction-architecture.md` §33 Decision Log 2026-08-04 Final Decision 记录）。RFC-002 的接受**不授权任何实现**：Implementation、Architecture Readiness Package、Technical Spikes、测试与基础设施均 NOT AUTHORIZED；PR #24 Merge = USER DECISION REQUIRED / NOT AUTHORIZED；后续 RFC、Architecture Readiness Package、Technical Spike 与 Persistence Implementation 不得违反或静默绕过 RFC-002。RFC-001 的接受**仅开放 Foundation Planning**；Foundation Implementation、Business Implementation 与 Production Implementation 仍未授权。**FND-001、FND-002 与 FND-003 Issue Candidate 均已经形成，Foundation Candidate Planning 与 Final Review（PASS，2026-07-30，Decision Conflict = NONE）均已完成**——当前 Candidate 状态（以 [../foundation/foundation-issue-candidates.md](../foundation/foundation-issue-candidates.md)「授权边界（恒定成立）」为基准）：**FND-001 = COMPLETED（PR #7 已合并，Merge Commit 5b75bcf，归档 PR #8）；FND-002 = IN REVIEW（Issue #9 已创建，实施完成并提交 PR #10，Merge = USER DECISION REQUIRED）；FND-003 = READY, BLOCKED BY FND-002**，Issue Creation / Implementation 均未授权。下一正式 Gate：**FND-002 Pull Request Review and Merge Gate**（由用户审查 FND-002 PR #10 并决定 Merge；Coding Agent 不得自行 Merge，用户 Merge 前 FND-002 Status 不标记 COMPLETED；FND-002 的授权不包括 FND-003 或任何业务实现；FND-002 完成并合并前不创建 FND-003 Issue / Branch / PR，不开始 FND-003 实施）。

---

## 说明

- 优先级 `P0` = 阻塞对应生产模块开始（开始该模块生产实现**前**必须接受）。
- 优先级 `P1` = 建议在相关生产实现早期接受。
- **RFC-001、RFC-002、RFC-003 与 RFC-006 已 `ACCEPTED`**（用户正式决定）；RFC-004 当前为 `DRAFTING`，DQ-01～09 已接受而 DQ-10 / P-57 仍 Proposed；RFC-005 / RFC-007 为 `PROPOSED`。各 RFC 的正文与接受与否由用户在相应 Decision Gate 决定。
- 在对应 RFC 被**接受**前，任何生产实现**不得**临场选择相关技术。

## Required RFC 清单

| # | RFC 主题 | Wave | 优先级 | 当前状态 | 阻塞的生产模块 | 关联 DEC / Spec | 关联 Spike 未验证项 |
|---|---|---|---|---|---|---|---|
| RFC-001 | **Repository and Application Architecture**（生产代码仓与应用结构、模块边界、部署单元） | Wave 1 | P0 | `ACCEPTED` | 所有生产模块 | DEC-011/021/023 · architecture/system-architecture | R-1 |
| RFC-002 | **Persistence and Transaction Architecture**（生产数据库、ORM、原子提交与幂等的生产实现） | Wave 1 | P0 | `ACCEPTED`（2026-08-04 用户正式决定；DQ-01~17 全部 ACCEPTED） | Business Repository / Current Truth | DEC-024/029/033 · architecture/data-architecture | R-1, R-4 |
| RFC-003 | **[LangGraph Runtime and Checkpoint Architecture](rfc-003-langgraph-runtime-and-checkpoint-architecture.md)**（生产 Checkpointer、Safe Resume、Worker、Checkpoint 对账与兼容） | Wave 2 | P0 | `ACCEPTED`（2026-08-06 用户明确整体接受） | Workflow Runtime / Resume | DEC-013/023/024/033/049/050/051 · runtime/failure-recovery spec | R-3 |
| RFC-004 | **[API and Human Review Architecture](rfc-004-api-and-human-review-architecture.md)**（生产 API 边界、Human Review 提交/暂停协议、固定工作区边界） | Wave 3 | P0 | `DRAFTING`（Issue #54；DQ-01～09 Accepted，DQ-10 Proposed as P-57） | Review / Orchestration 接口层 | DEC-007/029/044～047/055～057/059～065 · workflow/human-review spec | R-1 |
| RFC-005 | **Source Processing and Retrieval Architecture**（生产检索：词法/向量/融合、权限与版本过滤、证据装配） | Wave 3 | P0 | `PROPOSED` | Retrieval & Evidence Runtime | DEC-014/025/032 · runtime/hybrid-retrieval spec | R-2 |
| RFC-006 | **[LLM Runtime and Structured Output](rfc-006-llm-runtime-and-structured-output.md)**（生产 LLM Provider、结构化输出、真实模型 Smoke 策略、Secret 注入边界） | Wave 2 | P0 | `ACCEPTED`（2026-08-06 用户明确整体接受） | 所有 LLM 驱动 Skill | DEC-011/026/027/028/030/052/053/054 · skills specs | R-2 |
| RFC-007 | **Observability and Runtime Operations**（结构化日志 / Tracing / Metrics、是否 OpenTelemetry、Retry/Timeout/Backoff/Circuit Breaker 生产参数） | Wave 4 | P1 | `PROPOSED` | Runtime Operations | DEC-033 · runtime/failure-recovery spec | R-1, R-4 |

## 与 Spike-001 Required RFC List 的映射

Spike Report 第 7 节的 7 项与本表对应：1→RFC-003（Checkpointer）、2→RFC-001/002（并发与锁/持久化）、3→RFC-006（LLM Provider 与 Smoke）、4→RFC-005（Retrieval）、5→RFC-002（DB 与 ORM）、6→RFC-007（Observability Provider）、7→RFC-007（Retry/Timeout/Backoff/Circuit Breaker 参数）。

## 接受流程（提醒）

```text
RFC Draft
  -> IN REVIEW（用户与架构审查）
  -> ACCEPTED（用户明确确认）
  -> 对应生产模块方可开始实现
```

> 在 RFC-001—RFC-007 被接受前：**不允许**开始未经 RFC 支持的生产实现；**不允许** Coding Agent 临场选择生产数据库 / Checkpointer / API / ORM / Retrieval / Observability。

## 依赖顺序

```text
RFC-001 Repository and Application Architecture
│
├── RFC-002 Persistence and Transaction Architecture
│   ├── RFC-003 LangGraph Runtime and Checkpoint Architecture
│   │   └── RFC-004 API and Human Review Protocol
│   └── RFC-005 Source Processing and Retrieval Architecture
├── RFC-006 LLM Runtime and Structured Output
└── RFC-007 Observability and Runtime Operations
```

- RFC-003 与 RFC-006 可并行调研和起草。
- RFC-004 可提前整理 API Questions，但接受前须 RFC-002 与 RFC-003 已 `ACCEPTED`。
- RFC-005 可提前比较 Retrieval 方案，但接受前须 RFC-002 已 `ACCEPTED` 且 RFC-006 模型接口边界已明确。
- RFC-007 可提前调研，但最终接受应在 RFC-002 至 RFC-006 主要运行结构明确后。

## Roadmap Gates

### Roadmap Draft v0 Gate

当以下 RFC 被接受：

```text
RFC-001 = ACCEPTED
RFC-002 = ACCEPTED
RFC-003 = ACCEPTED
```

允许生成 MVP Roadmap Draft v0、Epic Skeleton、Dependency Graph、Foundation Issue Candidates。不得生成完整业务功能 Backlog。

### Roadmap v1 Gate

当 RFC-001 至 RFC-007 全部被接受，允许生成 MVP Development Roadmap v1、Final Epic Map、Implementation Backlog、Acceptance Criteria、Traceability Matrix v1。

## RFC-001 Current Status

```text
RFC-001 Status = ACCEPTED (2026-07-30，用户明确接受，Final Consistency Review 通过)
RFC-001-DQ-01 Modular Monolith First = ACCEPTED
RFC-001-DQ-02 Backend Language and LangGraph Binding = ACCEPTED
RFC-001-DQ-03 Repository and Package Directory Structure = ACCEPTED
RFC-001-DQ-04 Layer Responsibilities and Dependency Rules = ACCEPTED
RFC-001-DQ-05 Skill Code Shape and Architectural Relationships = ACCEPTED
RFC-001-DQ-06 Dependency Injection, Configuration and Application Bootstrap = ACCEPTED
RFC-001-DQ-07 Process Boundaries and Sync/Async Execution Strategy = ACCEPTED
RFC-001-DQ-08 Module Public Contracts, Cross-module Collaboration and Cycle Governance = ACCEPTED
RFC-001-DQ-09 Quality Toolchain, Architecture Enforcement, CI Quality Gates and Test Baseline = ACCEPTED
RFC-001-DQ-10 Production Skeleton Scope, Foundation Authorization Gate and RFC Closure = ACCEPTED
```

**接受后授权状态：** `Foundation Planning = AUTHORIZED`；`Foundation Implementation = NOT AUTHORIZED`；`Business Implementation = NOT AUTHORIZED`；`Production Implementation = NOT AUTHORIZED`；`Architecture Readiness / Development Status = CONDITIONALLY READY`。

> **关于 Merge PR / Delete Branch：** RFC-001 决策文档直接在本 Repository 的 `main` 分支上开发与提交，未创建独立的 RFC-001 PR 或 RFC Branch，故 DEC-038 的「Merge RFC-001 PR / Delete RFC Branch」步骤在当前工作流下不适用；对应 GitHub Issue #5 已随接受关闭。

## DQ-10: Production Skeleton Scope, Foundation Authorization Gate and RFC Closure（已接受）

RFC-001-DQ-10 已接受：

1. **Acceptance 与 Authorization 严格分离**——`RFC-001 Acceptance ≠ Foundation Planning Authorization ≠ Foundation Implementation Authorization ≠ Business Implementation Authorization`；接受 DQ 或 RFC-001 整体均不授权开发。
2. **RFC-001 最终接受仅开放 Foundation Planning**——不开放自动创建 Foundation Issues / 自动执行 Foundation Work / 自动建立 Production Skeleton / 业务功能开发；每个 Foundation Issue 需单独明确授权。
3. **Initial Foundation Scope = Package + Quality Tooling + Architecture Tests + CI + Repository Security**；首批可创建 `apps/backend/`（`pyproject.toml` / `uv.lock` / `.python-version` / Package Root / `py.typed` / `tests/`）与 `.github/` / `scripts/` / `tooling/`；只创建承担真实职责的文件。
4. **Prohibited Scope**——首批不创建业务模块、`platform/` 具体实现、Production Orchestration / LangGraph、API / Worker / CLI、Production Bootstrap、Database / ORM / Migration、Queue / Checkpointer、Model / Retrieval / Observability Runtime、Frontend Runtime。
5. **Spike Source Migration PROHIBITED**——Spike-001 仅作 Architecture Evidence / Failure Catalogue / Test Design Input，禁止复制或重命名迁移进 Production。
6. **Foundation Issue Candidates = FND-001 → FND-002 → FND-003**（依赖顺序，One Issue → One Branch → One PR → Required Verification → User Merge Gate）。
7. **Mandatory Stop Conditions** 17 类——遇未决架构问题必须停止并提交 Decision Conflict Report / Mandatory Stop Report，不得静默决定。
8. **RFC-001 Final Acceptance Flow**——DQ-10 ACCEPTED → Archive DQ-10 → **RFC-001 Final Consistency Review** → Final Review Report → 用户明确接受 → RFC-001 Status = ACCEPTED → Merge PR → Close Issue → Delete Branch；PR Merge 不能替代用户接受。
9. **Production Business Implementation Gate**——按 DEC-038，`RFC-001/002/003 = ACCEPTED` 后才生成 Roadmap Draft v0；`RFC-001~007 = ACCEPTED` 后才生成 Roadmap v1 与完整业务 Backlog。

在 RFC-001 整体被用户明确接受前：

- 不创建 Production Skeleton；
- 不创建 Production CI；
- 不创建 Foundation Issue；
- 不创建业务模块、API、Worker、CLI、Database、Production LangGraph；
- 不迁移 Spike 代码；
- Foundation Planning 不得开始；
- RFC-001 保持 `DRAFTING`。

## Historical Timeline：FND-002 Pull Request Review and Merge Gate

**RFC-001 已于 2026-07-30 被用户正式接受（`ACCEPTED`）**——DQ-01~DQ-10 全部 ACCEPTED 且 Final Consistency Review 通过（八项审查全部 PASS，Decision Conflict = NONE FOUND）。RFC-001 的接受**仅开放 Foundation Planning**。

**FND-001 / FND-002 / FND-003 Issue Candidate 均已经形成并经用户确认（2026-07-30）**，追踪分别为 RFC-001-DQ-02/03/09/10、DQ-03~06/08/09/10、DQ-06/08/09/10 + DEC-036 / DEC-038。规划文档见 [../foundation/foundation-issue-candidates.md](../foundation/foundation-issue-candidates.md)。

**Foundation Candidate Final Review 已完成（PASS，2026-07-30）**——范围完整性（COMPLETE）/ 职责分离（NO DUPLICATION）/ 依赖顺序 `FND-001→FND-002→FND-003`（VALID、ACYCLIC）/ 后续 RFC 范围泄漏（RFC-002~007 均 NO SCOPE LEAKAGE）/ RFC-001-DQ-10 一致性（PASS）/ Acceptance Criteria（三者均 EXECUTABLE）/ Mandatory Stop Conditions（SUFFICIENT）/ Decision Conflict（NONE）全部通过。完整报告见规划文档「Foundation Candidate Final Review」。

当前 Candidate 状态（以规划文档「授权边界（恒定成立）」为基准）：

```text
FND-001  Backend Package and Local Tooling Foundation        = COMPLETED（PR #7 已合并，Merge Commit 5b75bcf，归档 PR #8）
FND-002  Architecture Enforcement and Test Foundation        = IN REVIEW（Issue #9，实施完成并提交 PR #10，Merge = USER DECISION REQUIRED）
FND-003  CI, Security and Repository Protection              = READY, BLOCKED BY FND-002
```

**FND-001 已完成（2026-07-30）：** 用户授权「确认授权创建并实施 FND-001」后，Issue #6 → Branch `foundation/001-backend-package-local-tooling` → PR #7 → Required Verification（PASS）→ 用户 Merge 决定「我已 merged」；Merge Commit `5b75bcf99eba45f47fa501bfcf60d1e637601a07`。完成归档经独立 Documentation PR（PR #8）记录并已合并。

**FND-002 已经用户单独授权并实施完成（2026-07-30）：** 用户明确授权「确认授权创建并实施 FND-002」后，[Issue #9](https://github.com/JettxonHo/ai-ecommerce-agent/issues/9) 已创建，实施完成并提交 [PR #10](https://github.com/JettxonHo/ai-ecommerce-agent/pull/10)（`foundation: enforce architecture and test boundaries`），Status = IN REVIEW。FND-002 的授权来源于用户另行单独授权，非 FND-001 完成的自动授权。

**下一正式 Gate：** 由用户审查 FND-002 PR #10 并决定 Merge（`FND-002 Merge = USER DECISION REQUIRED`，Coding Agent 不得自行 Merge；用户 Merge 前 FND-002 Status 不标记 COMPLETED）。该授权仍**不**包括 FND-003 或任何业务实现，也**不**代表自动 Merge、自动执行后续 Issue、自动创建业务模块、自动进入 RFC-002。

- **Final Review 是审查，不是实施授权**——不自动创建 GitHub Issue，不开始任何 Foundation Implementation。
- 每个 Foundation Issue 仍需**单独明确的用户授权**，按依赖顺序 `FND-001 → FND-002 → FND-003` 执行，遵循 One Issue → One Branch → One PR → Required Verification → User Merge Gate。
- FND-003 Issue Creation / Implementation 保持 `NOT AUTHORIZED`；FND-002 完成并合并前不创建 FND-003 Issue、不开始 FND-003 实施。
- Foundation Implementation（除 FND-001 / FND-002 单项授权外）、Business Implementation 与 Production Implementation 保持 `NOT AUTHORIZED`；Mandatory Stop Conditions 持续有效。

## DQ-09: 代码质量工具链、Architecture Enforcement、CI Quality Gate 与测试基线

RFC-001-DQ-09 已接受：

1. 生产代码采用 Ruff（Formatter + Linter）、Pyright（Type Checker）、pytest（Test Runner）、Import Linter（Import Architecture）与自定义 pytest Architecture Tests（Semantic Architecture）构成统一质量工具链；不同时引入 Black / isort / Flake8 作为平行 Source of Truth；配置集中于 `apps/backend/pyproject.toml`；
2. Strict-first Type Discipline 优先适用于 Domain / Application / Public Contract；`Any` 只能存在于明确外部边界，第三方动态类型在 Infrastructure Adapter 收窄；禁止全局 `Any` / 全局 Ignore / 关闭核心诊断绕过类型检查；
3. 测试分类为 unit / integration / contract / architecture / e2e / evaluation / live / slow；pytest Marker 必须预注册，CI 严格 Marker 模式，未知 Marker 必须失败；普通 Required PR Tests 不访问实时外部 Provider；
4. Architecture Enforcement 双层机制：Import Linter 验证结构规则（Domain / Application Independence、Module Isolation、Public Facade-only、Orchestration / Entrypoint / Spike / Shared Kernel Boundary、DAG），自定义 Architecture Tests 验证语义规则（Public Contract / Skill / Orchestration / Configuration / Entrypoint Boundary）；
5. Unit 确定性；Integration 使用隔离可重建资源验证 Commit/Rollback；Contract 验证 Public Contract / Port / Event / Dispatch Payload / Graph State；E2E 覆盖主流程 + 失败场景；Evaluation 与确定性测试分离，Live Evaluation 默认运行于 Nightly / 手动 / Release Candidate；
6. 可执行生产代码进入后启用 Branch Coverage，Global Fail-under = 80%；关键业务规则必须有行为测试；Warnings = Error by default；Required CI 禁止用自动重跑掩盖 Flaky Test；Snapshot 更新需人工语义审查；
7. Dependency Audit 使用 pip-audit，启用 Dependabot Alerts 与受控 Security Updates；CI 必须具备 Secret Detection Gate（检出 → CI Failure → 移除 → 真实凭证则轮换/吊销）；
8. CI 分为 Fast Static / Deterministic Test / Runtime Confidence / Extended Gate；`main` 使用稳定 Required Status Checks 保护（PR 合并、禁止直接 Push / Force Push、Required Checks 通过、Review 解决、用户保留最终 Merge 权限，当前个人项目不强制第二名 Reviewer）；Coding Agent 不得关闭检查 / 降低阈值 / 删除测试绕过 CI；本地与 CI 使用统一命令入口；
9. 本 Decision 不锁定工具版本 / Secret Scanner / 前端工具 / CI YAML；接受后仍不授权创建 Production CI 或 Skeleton；RFC-001 保持 `DRAFTING`。

## DQ-08: 模块公开契约、跨模块 Command / Query / Event 协作与循环依赖治理

RFC-001-DQ-08 已接受：

1. 每个业务模块通过唯一稳定入口 `modules.<module>.public`（`modules/<module>/public.py`）暴露跨模块契约，其他模块只能通过该 Public Facade 使用公开能力；
2. Public Facade 可暴露 Command / Query / Result / Public Error / Application Service Protocol / Published Application Event / Stable Identifier / Version Reference / Immutable Snapshot；不得暴露 ORM Model / Database Session / Repository Implementation / Mutable Domain Entity / Graph State / LangGraph Node / Provider SDK / Secret；Public Contract 必须 Typed / Immutable / Serializable / Version-aware / Infrastructure-neutral；
3. 跨模块数据读取返回不可变 Owner Module Public Snapshot，不返回内部 Aggregate / ORM Entity；
4. 跨模块读取经 `Target Module Public Query`；Query 无副作用、返回 Public Snapshot；禁止 `Consumer Module → Target Module Repository → Direct SQL / ORM`；共享 Database Instance ≠ 共享数据所有权；
5. 状态修改由数据所有模块 Application Service 执行；`Direct module-to-module state-changing Command = PROHIBITED BY DEFAULT`；跨 Stage 协调由 Orchestration 完成；跨模块原子操作仅经 Explicit Composite Application Use Case；
6. Domain Event 模块内部（过去式，不发送）；Application Event 表示已提交业务事实，仅用于非关键提交后副作用；Human Review / Current Truth / Idempotency / 核心路由 / Durable Resume 不得依赖普通最终一致 Event；`Workflow Orchestration ≠ Event Choreography`；进程内 Event Bus 不承担 API→Worker 可靠调度；Event Handler 必须 Idempotent / Duplicate-consumption-safe；
7. 模块依赖图必须为 Directed Acyclic Graph，禁止循环依赖（含逻辑业务调用循环）；循环依赖须通过提升 Orchestration / Public Query / Port 注入 / 提取基础概念 / 重新划分模块 / Composite Use Case 解决，不得用延迟 Import 或扩大 Shared Kernel 掩盖；`shared_kernel/` 保持最小；
8. Public Error 稳定结构化（`error_code / category / message / retryability / relevant_reference`），不泄漏技术异常；Breaking Change 显式版本化并更新 Consumer Contract Tests；Architecture Tests 强制跨模块 Import 只能指向 Public Facade 且依赖图无环；
9. 本 Decision 不选择 Event Bus / Outbox / Schema Library / Contract Test Framework；接受后仍不授权创建正式 Public Contract、Application Event Runtime、Event Bus 或生产业务代码。

## DQ-07: Process Boundaries and Sync/Async Execution Strategy

RFC-001-DQ-07 已接受：

1. 保持单一 Modular Monolith 应用与统一版本化 Release Boundary，但生产运行时分离 API Process 与 Workflow Worker Process，CLI 为按需临时进程；
2. `Application Architecture ≠ Release Artifact ≠ Runtime Process`；“一个主要后端部署单元”不要求所有能力同进程；
3. API 与 Worker 使用同一 Python Package / Application Layer / Domain Contract，默认从同一 Release Version 构建部署；
4. `Long Workflow inside HTTP Request = PROHIBITED`；长 Workflow 采用 Durable Dispatch 后台异步执行；API 在 Durable Work Intent 可靠记录后才返回接受状态；
5. 生产可靠任务禁止 `asyncio.create_task(...)` 或 Web Framework 临时 Background Task；
6. API 与 Worker 通过 `WorkflowDispatchPort`（schedule_start/resume/rerun/cancel/recovery）协作；当前不选择具体 Queue / Broker / Dispatch Backend；
7. Worker Crash 后工作可重新领取；重复投递经 Idempotency 防重复业务版本；Worker 仅经 Application Service 提交业务状态；
8. Human Review Submit 同步完成业务校验与 Approved Strategy 提交，并可靠记录 Durable Resume Intent；Approved Commit 与 Resume Intent 必须原子或可靠协调；Workflow Resume 由 Worker 异步执行；
9. Application Core 采用 Sync-first，Domain 保持纯同步；并发优先有界 Worker Process / Worker Slot；当前不采用全栈 Async-first；禁止业务代码随意 `asyncio.run()`；
10. API 与 Worker 使用窄化的不同 Bootstrap Factory；Dispatch Payload 只含 ID / 版本 / Runtime Reference；Cancellation 使用 Durable Cancellation Intent；Local/Test 允许 Combined Runtime 与 Inline Runner；
11. 本 Decision 不选择 API Framework / Queue / Database Driver / Worker Framework / Deployment Platform；接受后仍不授权创建 API、Worker 或 Production Runtime。

## DQ-06: Dependency Injection, Configuration and Application Bootstrap

RFC-001-DQ-06 已接受：

1. 默认采用 Constructor Injection + 显式 Factory Functions + 集中式 Composition Root（`bootstrap/`）；
2. MVP 不引入第三方 DI Framework；
3. 禁止全局 Service Locator 与可变运行状态；
4. 配置仅由 Bootstrap 加载，类型化、验证、不可变，验证失败 fail-fast；
5. Domain 不接收配置；Application 只接收业务流程级配置；Infrastructure 只接收适配器级配置；
6. Secret 只注入需要它的 Infrastructure Adapter，不进入 Domain / Application / Skill / Graph State / Checkpoint / Audit / Trace / API Response / Git / Issue / PR；
7. Repository 只提交 `.env.example`（占位值），`.env` 不得提交；
8. 资源生命周期由 Application Bootstrap 统一管理，按 Application / UseCase / WorkflowRun / SkillExecution 作用域分级；
9. 测试通过注入 Fake / Stub 替换真实 Adapter，无需修改业务代码；
10. 同步/异步与 API / Worker / CLI 进程边界留待 RFC-001-DQ-07；
11. 本 Decision 不选择 DI Framework、Secret Manager、Settings Library 或 Deployment Platform。

## DQ-05: Skill Code Shape and Architectural Relationships

RFC-001-DQ-05 已接受：

1. Skill 是业务模块 Application Layer 内具有明确执行契约、可独立运行和独立评估的无状态业务能力组件；
2. Skill 落位 `modules/<module>/application/skills/<skill_slug>/`；
3. Application Use Case 以 Prepare–Execute–Commit 协调 Skill 与业务事务；
4. Skill 只参与 Execute 阶段，产出 Candidate Result（业务候选，未落库）；
5. Skill 直接访问业务 Repository = PROHIBITED；Skill 业务事务所有权 = NO；
6. Skill 不读/写 Current Truth、不更新 Evidence / Audit / Idempotency；
7. Skill 只能通过 Application 定义的 ModelRuntimePort / RetrievalPort 调用 Provider 能力；
8. Skill 直接 import 具体 Provider SDK = PROHIBITED；
9. LangGraph Node 经 Stage Application Service + Skill Executor 间接调用 Skill，不直接调用；
10. Skill 与 LangGraph Node 不是同一概念；Skill 不感知 LangGraph；
11. Skill 必须能脱离 LangGraph 独立运行与独立评估 = REQUIRED；
12. Skill 版本分 Contract / Implementation / Prompt / Output Schema 四维度分管；
13. Skill 须支持 Contract / Unit / Integration / Evaluation / Architecture 五类测试；
14. 本 Decision 不选择模型 Provider、Retrieval Backend、Schema Library、Prompt Registry 或 Evaluation Framework。

## DQ-04: Layer Responsibilities and Dependency Rules

RFC-001-DQ-04 已接受：

1. Domain 是纯业务核心，不依赖框架、数据库、LangGraph、ORM 或外部 SDK；
2. Application 负责 Use Case、Port 和业务流程协调；
3. Repository、Provider 与 Unit of Work Port 默认由 Application 定义；
4. Infrastructure 实现 Application Port，不得拥有业务规则；
5. 业务事务由 Application Use Case 拥有；
6. 长 Workflow 由多个短 Application Transaction 组成；
7. LangGraph Orchestration 是独立 Adapter Layer；
8. Graph Node 只能调用公开 Application Service，禁止直接访问业务 Repository；
9. Entrypoint 只负责协议转换，不直接调用 Domain 或 Repository；
10. Bootstrap 是 Composition Root；
11. 默认采用 Constructor Injection 和显式 Factory；
12. 跨模块调用必须经过公开 Application Contract；
13. Architecture Tests 必须强制依赖边界；
14. 本 Decision 不选择 ORM、Database、API Framework、DI Framework、Event Broker 或 Deployment。

## Historical Final Status Snapshot（RFC-004 Gate 开始前）

> 本段保留其形成时状态；当前状态始终以文件顶部 Current truth 与 Required RFC 清单为准。

```text
Spike Execution Status = COMPLETED
RFC-001 Status = ACCEPTED (2026-07-30)
RFC-002 Status = ACCEPTED (2026-08-04; PR #24 merged; Issue #23 closed)
RFC-003 Status = ACCEPTED (2026-08-06 user final acceptance; implementation, spike execution, and Goal activation not granted)
RFC-004 / RFC-005 / RFC-007 Status = PROPOSED
RFC-006 Status = ACCEPTED (2026-08-06 user final acceptance; implementation, spike execution, and Goal activation not granted)
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY (planning and governance only)

FND-001 Status = COMPLETED (PR #7; archive PR #8)
FND-002 Status = COMPLETED (PR #10; archive PR #13)
FND-003 Status = COMPLETED (PR #15; archive PR #22)
Foundation Program Status = COMPLETED

ARP-01 / ARP-04 / ARP-10 = ACCEPTED (full declared scope)
ARP-02 / ARP-03 / ARP-09 = ACCEPTED (TS-01 minimum slice only; full artifact pending)
ARP-05 / ARP-06 / ARP-07 / ARP-08 = NOT CREATED

Pre-development RFC and readiness planning = AUTHORIZED
TS-01～TS-05 Execution = NOT AUTHORIZED
Business / Production Implementation = NOT AUTHORIZED
Actual Goal = NOT CREATED / NOT ACTIVATED

Next Gate: product specification closure and RFC-004 / RFC-005 / RFC-007; then complete readiness planning package, testing strategy, Goal text, project-wide planning consistency review, and explicit user approval (Frontend Architecture overall accepted 2026-08-07)
```
