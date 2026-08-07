# MVP Traceability Matrix（可追溯矩阵 v1）

> **Status: ACTIVE PRE-DEVELOPMENT DRAFT — final Epic / Issue / Test links pending Goal acceptance**
> **治理来源：** DEC-034 · [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md)
> **关联：** [Architecture Readiness Review v1 Issue #3](https://github.com/JettxonHo/ai-ecommerce-agent/issues/3) · [../rfcs/rfc-register.md](../rfcs/rfc-register.md)
> **纪律：** 本矩阵**只**建立 `Requirement → DEC → Spec → Spike Scenario → Evidence → Required RFC → Future Epic → Future Test` 的连接关系。**当前不创建正式 Epic 与生产 Issue**，`Future Epic` / `Future Test` 仅为 **Placeholder（占位）**。

---

## 列含义

| 列 | 含义 |
|---|---|
| Requirement | 业务/架构需求（源自产品定位与已接受 DEC） |
| DEC | 支撑该需求的已接受决定 |
| Spec | 对应概念规格文档 |
| Spike Scenario | Spike-001 中验证该需求运行时行为的场景（`—` = Spike 未覆盖，属业务质量层） |
| Evidence | 证据位置（测试 / 运行时证据 / 文档） |
| Required RFC | 进入对应生产实现前必须接受的 RFC（见 rfc-register） |
| Future Epic | **占位**：未来正式 Epic（当前不创建） |
| Future Test | **占位**：未来生产测试（当前不创建） |

---

## 矩阵

### 0. Governance 与 RFC Gate

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| Proportional validation and review | DEC-039 | [AGENTS](../../AGENTS.md) | — | PR #31 Sol/xhigh review | All | Governance only | Per-change relevant checks |
| Autonomous low-risk PR flow and model roles | DEC-040, DEC-043 | [Collaboration Model](../governance/collaboration-model.md) | — | PR #31 + Issue #34 | All | Goal governance | Independent Sol review + Required Checks |
| Local end-to-end demo MVP envelope | DEC-041 | [MVP Scope](../product/mvp-scope.md) | — | DEC-041 | RFC-003—RFC-007 | _(placeholder)_ | Browser E2E + release smoke _(planned)_ |
| Evidence-driven launch strategy workbench positioning, composite Persona assumptions and behavior-based demo success | DEC-042 | [PRD](../product/prd.md) | — | DEC-042 | RFC-003—RFC-007 | _(placeholder)_ | Browser E2E + human usability review _(planned)_ |
| Sol/Luna/Terra task routing, thread isolation and review independence | DEC-043 | [Collaboration Model](../governance/collaboration-model.md) | — | DEC-043 + Issue #34 | All | Goal governance | Actual model disclosure + independent reviewer + Required Checks |
| Single-task workbench, two-level input gate, Needs Input, reversible Source change and confirmed partial rerun | DEC-044, DEC-059, DEC-061 | [User Flows](../product/user-flows.md) | — | DEC-044 + DEC-059 + DEC-061 | RFC-003, RFC-004, RFC-005 | _(placeholder)_ | Browser E2E + action-request + Source remove / replace + state / stale-review tests _(planned)_ |
| Task / Fact Stage minimum gates, demo file limits and classified conflict handling | DEC-045 | [PRD](../product/prd.md) | — | DEC-045 + Issue #38 / PR #39 | RFC-003, RFC-004, RFC-005 | _(placeholder)_ | Input contract + partial file acceptance + conflict behavior tests _(planned)_ |
| Review / Brief semantic groups, immutable domain versions, draft revision and export snapshot | DEC-046 | [PRD](../product/prd.md) | — | DEC-046 + Issue #40 / PR #41 | RFC-004, RFC-006 | _(placeholder)_ | Semantic contract + stale-revision + export snapshot tests _(planned)_ |
| Progressive evidence, edit intent, stage progress, actionable recovery and export confirmation | DEC-047 | [User Flows](../product/user-flows.md) | — | DEC-047 + Issue #42 / PR #43 | RFC-003, RFC-004, RFC-005, RFC-007 | _(placeholder)_ | Browser evidence / edit / recovery / export interaction E2E _(planned)_ |
| Small representative acceptance pack, behavior gates, human usability judgment and Markdown-first export | DEC-048 | [Testing Strategy](../development/testing-strategy.md) | — | DEC-048 + Issue #44 / PR #45 | RFC-004, RFC-006 | _(placeholder)_ | 3 fixed fixtures + mutation script + RC live smoke + human PASS / FAIL _(planned)_ |
| Dedicated PostgreSQL Checkpoint Database, sync durability, reentrant nodes and Current-Truth-first reconciliation | DEC-049 | [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md) | spike-05, spike-08 | DEC-049 + Issue #46 / PR #47 | RFC-003（ACCEPTED） | _(placeholder)_ | TS-03 isolation / reconciliation + interrupt / resume + duplicate-safe replay _(planned)_ |
| PostgreSQL Durable Work Intent dispatch, fenced worker ownership and cooperative cancellation | DEC-050 | [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md) | — | DEC-050 + Issue #46 / PR #47 | RFC-003（ACCEPTED） | _(placeholder)_ | TS-01 multi-worker claim / takeover / stale commit rejection + cancellation commit fence _(planned)_ |
| Explicit runtime compatibility, deterministic Safe Resume and forward-recovery evidence | DEC-051 | [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md) | — | DEC-051 + Issue #46 / PR #47 | RFC-003（ACCEPTED） | _(placeholder)_ | TS-01 / TS-03 compatibility + seven-action recovery + migration / forward repair _(planned)_ |
| Single OpenAI Responses provider, narrow sync Model Runtime Port and project-authoritative Structured Output validation | DEC-052 | [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md) | spike-03（test-design evidence only） | DEC-052 + Issue #48 / PR #49 | RFC-006（ACCEPTED） | _(placeholder)_ | Port contract + SDK isolation + strict output / project schema / domain-validator order _(planned)_ |
| Bounded Model Recovery, readable Version Tuple and five deterministic invocation profiles | DEC-053 | [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md) | spike-03（test-design evidence only） | DEC-053 + Issue #48 / PR #49 | RFC-006（ACCEPTED） | _(placeholder)_ | Retry / recovery budget + version snapshot + profile / context contract _(planned)_ |
| Adapter Secret / Payload allowlist, deterministic model substitute and one manual RC smoke | DEC-054 | [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md) | spike-03（test-design evidence only） | DEC-054 + Issue #48 / PR #49 | RFC-006（ACCEPTED） | _(placeholder)_ | Secret boundary + payload-free ledger / telemetry + offline contract layers + opt-in live smoke _(planned)_ |
| React / Vite SPA, explicit frontend state ownership, generated OpenAPI client and proportional Chromium verification | DEC-055 | [Frontend Architecture](../architecture/frontend-architecture.md) | — | DEC-055 + Issue #50 / Draft PR #51 | RFC-004 | _(placeholder)_ | Static / type / module / client-contract / build + key Playwright Chromium E2E _(planned)_ |
| Deep TaskWorkbench, minimal Task Index, revision-safe interaction projection and proportional web quality boundary | DEC-056, DEC-062 | [Frontend Architecture](../architecture/frontend-architecture.md) | — | DEC-056 / DEC-062 + Issues #50 / #52 | RFC-004 / RFC-005 | _(placeholder)_ | Task return + projection priority + latest-buffer revision chain + submit blocking + representative WCAG / Chrome / Reflow / performance evidence _(planned)_ |
| Product semantics / technical contract authority separation | DEC-057 | [PRD](../product/prd.md) | — | DEC-057 + Issue #52 / merged PR #53 | RFC-004 / RFC-005 / RFC-007 | Planning governance | Product Final Consistency Review = PASS；user overall acceptance = ACCEPTED |
| Contract-first typed HTTP, semantic revision / idempotency and durable async acceptance | DEC-063 | [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md) | — | DEC-063 + Issue #54 / PR #55 | RFC-004（ACCEPTED；DQ-01～03） | _(placeholder)_ | Resource / typed-command contract + first `202` / replay `200` same receipt + key-reuse / stale `409` + Run polling-stop tests _(planned)_ |
| Narrow Task navigation, revision-bound recovery and immutable Human Review protocol | DEC-064 | [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md) | — | DEC-064 + Issue #54 / PR #55 | RFC-004（ACCEPTED；DQ-04～06） | _(placeholder)_ | Task create/replay + bounded index + Needs Input supersession + Source basis conflict + new-Run resume + Review atomic continuation _(planned)_ |
| Immutable Brief / Export, finite Problem action and fixed-workspace transport | DEC-065 | [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md) | — | DEC-065 + Issue #54 / PR #55 | RFC-004（ACCEPTED；DQ-07～09） | _(placeholder)_ | Brief Current Truth / compare / revise + Export basis / replay + RFC 9457 action + normal state `200` + fixed-workspace Origin boundary _(planned)_ |
| One OpenAPI authority, bounded Operation / Schema / state catalog, additive compatibility and generated-client clean diff | DEC-066 | [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md) | — | DEC-066 + Issue #54 / PR #55 | RFC-004（ACCEPTED；DQ-10；Final Review PASS） | _(placeholder)_ | OAS / `$ref` / example validation + operation representative paths + generated-client clean diff + unknown read-only fallback _(planned)_ |
| One fictional “城市通勤双肩包” Anchor SKU across three variants and one mutation | DEC-058 | [Testing Strategy](../development/testing-strategy.md) | — | DEC-058 + Issue #52 / Draft PR #53 | RFC-004 / RFC-005 / RFC-006 | _(placeholder)_ | 3 fixed Anchor SKU variants + mutation + RC sufficient-variant smoke _(planned)_ |
| Targeted finite Needs Input action request derived from a real blocker | DEC-059 | [User Flows](../product/user-flows.md) | — | DEC-059 + Issue #52 / Draft PR #53 | RFC-004 / RFC-005 | _(placeholder)_ | Missing-input / conflict action request + non-blocking suggestion + recovery behavior tests _(planned)_ |
| Evidence-bound Claim Integrity without a generic compliance engine | DEC-060 | [PRD](../product/prd.md) | — | DEC-060 + Issue #52 / Draft PR #53 | RFC-004 / RFC-005 / RFC-007 | _(placeholder)_ | Verified Fact / Claim-to-verify + claim-level block + honest alternative + Needs Input boundary _(planned)_ |
| Task-scoped private material, reversible remove / replace and no user purge UI | DEC-061 | [User Flows](../product/user-flows.md) | — | DEC-061 + Issue #52 / Draft PR #53 | RFC-004 / RFC-005 / RFC-007 / ARP-08 | _(placeholder)_ | Task scope + remove / replace invalidation + no false permanent-delete claim _(planned)_ |
| Minimal recent-task index and stable deep links | DEC-062 | [Frontend Architecture](../architecture/frontend-architecture.md) | — | DEC-062 + Issue #52 / Draft PR #53 | RFC-004 | _(placeholder)_ | Empty list + recent task summary + stable return link + transient read recovery _(planned)_ |
| RFC Planning and Dependency Order | DEC-038 | [RFC Planning](../specs/governance/rfc-planning-and-dependency-order.md) | — | DEC-038 decision file | RFC-001—RFC-007 | _(placeholder)_ | _(placeholder)_ |
| Repository and Application Architecture Gate | DEC-038 | [RFC Planning](../specs/governance/rfc-planning-and-dependency-order.md) | — | architecture-baseline-v1 §9 | RFC-001 | _(placeholder)_ | _(placeholder)_ |
| Persistence and Transaction Architecture Gate | DEC-038 | [RFC Planning](../specs/governance/rfc-planning-and-dependency-order.md) | — | architecture-baseline-v1 §9 | RFC-002 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-01 Modular Monolith First | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §19 | RFC-001 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-02 Backend Language and LangGraph Binding | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §18 | RFC-001, RFC-003 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-03 Repository and Package Directory Structure | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §17 | RFC-001, RFC-002, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-04 Layer Responsibilities and Dependency Rules（Domain Independence / Application Transaction Ownership / Atomic Business Commit / Graph Node Boundary / Human Review Transaction / Module Public Contract / Architecture Tests） | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §16 | RFC-001, RFC-002, RFC-003, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-05 Skill Code Shape and Architectural Relationships（Skill Position / Prepare-Execute-Commit / Repository & Transaction Boundary / Provider Port Boundary / LangGraph Boundary / Independent Execution / Version Boundary / Skill Tests） | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §14 | RFC-001, RFC-006 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-06 Dependency Injection, Configuration and Application Bootstrap（Constructor Injection / Composition Root / Configuration Loading & Validation / Layer Boundary / Secret Boundary / Resource Lifetime / Test Replacement） | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §15 | RFC-001, RFC-006, RFC-007 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-07 Process Boundaries and Sync/Async Execution Strategy（Modular Monolith Release Boundary / API·Worker·CLI Process / Durable Dispatch / Human Review Resume / Atomic Resume Coordination / Worker Recovery / Sync-first / Bounded Concurrency / Dispatch Payload / Cancellation） | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §13 | RFC-001, RFC-002, RFC-003, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-08 Module Public Contracts, Cross-module Collaboration and Cycle Governance（Public Facade `modules.<module>.public` / Immutable Snapshot / Cross-module Public Query / Owning Application Service State Change / Orchestration Coordination / Composite Use Case / Application Event Post-commit / DAG Dependency / Public Error Contract / Architecture Tests） | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §12 | RFC-001, RFC-002, RFC-003, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-09 Quality Toolchain, Architecture Enforcement, CI Quality Gates and Test Baseline（Ruff Formatter/Linter / Pyright Strict-first / pytest Strict Markers / Import Linter + Custom Architecture Tests / Deterministic Required PR Tests / Branch-aware Coverage 80% / pip-audit / Secret Detection / Protected main Required Checks / Live Evaluation separated） | RFC-001 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §11 | RFC-001 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-10 Production Skeleton Scope, Foundation Authorization Gate and RFC Closure（Acceptance vs Authorization Separation / Foundation Planning Gate / Foundation Implementation separate authorization / Initial Foundation Scope = Package + Quality + Architecture Tests + CI + Repository Security / Business Modules·Platform·Orchestration·API·Worker·Bootstrap·DB·LangGraph·Model·Retrieval·Observability NOT IMPLEMENTED / Spike Source Migration Prohibited / FND-001→FND-002→FND-003 / Mandatory Stop Conditions） | DEC-034, DEC-036, DEC-038 | [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md) | — | architecture-baseline-v1 §10 | RFC-001—RFC-007 | _(placeholder: Future Roadmap Draft v0)_ | _(placeholder)_ |
| **FND-001 — Backend Package and Local Tooling Foundation**（**COMPLETED**；Issue #6 CLOSED；PR #7 MERGED；Merge Commit `5b75bcf99eba45f47fa501bfcf60d1e637601a07`；Merged 2026-07-30T12:38:48Z by JettxonHo（用户 Merge 决定「我已 merged」）；Post-merge Smoke Verification = PASS；Backend Package `apps/backend/src/ai_ecommerce_agent/` + Python 3.13 + uv Lockfile + Ruff/Pyright/pytest/Coverage Local Tooling + Unified Local Commands；Code Status = COMPLETED，Archive Status = COMPLETED（经文档归档 PR #8 记录），Overall Status = COMPLETED） | DEC-036, DEC-038 | docs/foundation/foundation-issue-candidates.md | apps/backend/ | PR #7 + docs/foundation/foundation-issue-candidates.md | RFC-001（DQ-02 / DQ-03 / DQ-09 / DQ-10） | [Issue #6](https://github.com/JettxonHo/ai-ecommerce-agent/issues/6) | [PR #7](https://github.com/JettxonHo/ai-ecommerce-agent/pull/7)（MERGED） |
| **FND-002 — Architecture Enforcement and Test Foundation**（**COMPLETED**；Issue Creation COMPLETED（[Issue #9](https://github.com/JettxonHo/ai-ecommerce-agent/issues/9)，CLOSED / COMPLETED）；PR #10 已由用户人工 Merge（Merge Commit `b966491865f57910d186542b1eb5191544a254f3`，2026-07-30T17:03:04Z，Merged By = JettxonHo）；Post-merge Verification = PASS；Import Linter 10 Contracts + 自定义 grimp 规则（Public Facade / Module DAG）+ AST 语义测试（环境访问 / 技术泄漏 / Skill Boundary）+ pytest 8-Marker 分类 + 默认 Network Protection + 统一 Architecture Test 命令；Branch `foundation/002-architecture-test-foundation`（已完全合并）；依赖 FND-001 = MERGED ✓；Code Status = COMPLETED，Archive Status = COMPLETED（经文档归档 PR #13 记录），Overall Status = COMPLETED） | DEC-036, DEC-038 | docs/foundation/foundation-issue-candidates.md | apps/backend/tests/architecture/ | PR #10 + docs/foundation/foundation-issue-candidates.md | RFC-001（DQ-03 / DQ-04 / DQ-05 / DQ-06 / DQ-08 / DQ-09 / DQ-10） | [Issue #9](https://github.com/JettxonHo/ai-ecommerce-agent/issues/9)（CLOSED） | [PR #10](https://github.com/JettxonHo/ai-ecommerce-agent/pull/10)（MERGED） |
| **FND-003 — CI, Security and Repository Protection**（**COMPLETED**；2026-07-31 用户授权创建并实施；PR #15 已由用户 Merge（Merge Commit `3f012b6405a6464b629873441ff50eff8c5d52ec`，2026-07-30T20:34:09Z / SGT 2026-07-31T04:34:09+08:00，Merged By = JettxonHo）；Post-merge Verification = PASS（main 8/8 Required Checks + 本地全量验证）；deps: FND-001 = MERGED ✓，FND-002 = MERGED ✓；3 Workflows + 8 Stable Required Checks（`quality / format`・`lint`・`typecheck`・`architecture`；`test / unit-contract`・`package-build`；`security / dependency-audit`・`secret-detection`）+ Dependency Audit（pip-audit，锁定 dev 依赖）+ Secret Detection（gitleaks 8.30.1，SHA-256 校验发布二进制，全历史 + `--redact`，内置默认规则）+ Dependabot（github-actions + uv 生态，weekly，不自动 Merge）+ PR / Issue Templates + `main` Branch Protection（Require PR / 8 Required Checks / strict / Conversation Resolution / enforce_admins）+ Repository Governance Documentation；PR #15 Required Checks 全绿；受控负向验证 9 场景全部真实阻止（含 `mergeable_state = blocked`）；5 维度对抗审计 PASS（0 BLOCKING/HIGH）；负向验证发现并修复 gitleaks `useDefault` 静默漏检缺陷；完成归档经本 Documentation PR #22 记录，合并后 Archive / Overall Status = COMPLETED） | DEC-036, DEC-038 | docs/foundation/foundation-issue-candidates.md | — | PR #15 + docs/foundation/foundation-issue-candidates.md + docs/development/ci-and-repository-governance.md | RFC-001（DQ-06 / DQ-08 / DQ-09 / DQ-10）, FND-001, FND-002, GitHub Governance, Security Foundation | [Issue #14](https://github.com/JettxonHo/ai-ecommerce-agent/issues/14)（CLOSED） | [PR #15](https://github.com/JettxonHo/ai-ecommerce-agent/pull/15)（MERGED） |


### A. 核心工作流与编排

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| 确定性 Workflow 编排（LLM 受约束） | DEC-011, DEC-023 | [Workflow State](../specs/workflow/workflow-state-specification.md) | spike-01 | test_skeleton::test_normal_workflow_end_to_end | RFC-001, RFC-003 | _(placeholder)_ | _(placeholder)_ |
| 任务级持久状态 + 跨会话 Resume | DEC-013, DEC-024, DEC-049, DEC-050, DEC-051 | [Workflow State](../specs/workflow/workflow-state-specification.md) | spike-05, spike-08 | test_review_safety::spike05/spike08 + DEC-049 / DEC-050 / DEC-051 | RFC-003 | _(placeholder)_ | PostgresSaver interrupt / resume + Current Truth reconciliation + fenced ownership + recovery action matrix _(planned)_ |
| 单审查节点 + 异常暂停 + 声明级阻断优先 | DEC-007, DEC-060 | [Human Review](../specs/workflow/human-review-and-approved-strategy-contract.md) | spike-01, spike-05 | test_skeleton / test_review_safety + DEC-060 | RFC-004 | _(placeholder)_ | Honest alternative continues; strategy-dependent claim enters Needs Input _(planned)_ |
| MVP 不用 Multi-Agent（Bounded Worker） | DEC-021 | [System Architecture](../architecture/system-architecture.md) | — | architecture-baseline-v1 | RFC-001 | _(placeholder)_ | _(placeholder)_ |

### B. 状态、版本与事务

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| Versioned Domain State + Compact State | DEC-024 | [Workflow State](../specs/workflow/workflow-state-specification.md) | spike-01, spike-06 | test_transaction_idempotency | RFC-002 | _(placeholder)_ | _(placeholder)_ |
| 三类存储分离；Checkpoint≠Current Truth；独立 Checkpoint Database + sync durability | DEC-024, DEC-033, DEC-049 | [Runtime Failure / Recovery](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md) | spike-01, spike-08 | test_skeleton::test_three_stores_are_separate + DEC-049 | RFC-002, RFC-003 | _(placeholder)_ | Database / role / pool isolation + stale / foreign / incompatible rejection _(planned)_ |
| Durable Work Intent + poll-and-claim + Lease / fencing + cooperative cancellation | DEC-033, DEC-050 | [Runtime Failure / Recovery](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md) | — | DEC-050 + Issue #46 / PR #47 | RFC-002, RFC-003, RFC-007 | _(placeholder)_ | Real PostgreSQL claim contention + lease takeover + stale commit rejection + cancellation / supersession _(planned)_ |
| Compatibility Tuple + deterministic Safe Resume + controlled migration / forward repair | DEC-033, DEC-049, DEC-050, DEC-051 | [Runtime Failure / Recovery](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md) | — | DEC-051 + Issue #46 / PR #47 | RFC-003, RFC-004, RFC-007 | _(placeholder)_ | Real PostgreSQL compatibility / interrupt / recovery action / migration / cutover evidence _(planned)_ |
| 原子提交 + 幂等 + 回滚 | DEC-029, DEC-033 | [Human Review](../specs/workflow/human-review-and-approved-strategy-contract.md) | spike-04, spike-06, Recovery | test_transaction_idempotency::spike04 | RFC-002 | _(placeholder)_ | _(placeholder)_ |
| 阶段级失效、编辑意图、语义组差异、影响预览与确认式部分重跑 | DEC-009, DEC-044, DEC-047 | [Workflow State](../specs/workflow/workflow-state-specification.md) | spike-05 | test_review_safety::spike05（pos_count==1）+ DEC-047 | RFC-002, RFC-003, RFC-004 | _(placeholder)_ | Material / presentation edit + invalidation preview + affected-stage rerun _(planned)_ |
| 不可变正式对象 + Review Draft revision | DEC-024, DEC-029, DEC-046 | [Human Review](../specs/workflow/human-review-and-approved-strategy-contract.md) | — | DEC-046 | RFC-002, RFC-004 | _(placeholder)_ | Immutable versions + stale revision save/submit _(planned)_ |
| Current Truth 导出快照、导出前确认与 Markdown 用户文件 | DEC-046, DEC-047, DEC-048 | [PRD](../product/prd.md) | — | DEC-046 / DEC-047 / DEC-048 | RFC-004 | _(placeholder)_ | Current-version confirmation + Markdown snapshot consistency _(planned)_ |

### C. Human Review 与 Approved Strategy

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| Human Review 节点边界 + 独立提交事务 | DEC-029 | [Human Review](../specs/workflow/human-review-and-approved-strategy-contract.md) | spike-01, spike-05 | graph.py 节点分离 + review.py | RFC-004 | _(placeholder)_ | _(placeholder)_ |
| No Stale Review Package Submission | DEC-029 | 同上 | spike-07 | test_review_safety::spike07（StaleReviewError） | RFC-004 | _(placeholder)_ | _(placeholder)_ |
| Duplicate Submit 幂等 | DEC-029 | 同上 | spike-06 | test_review_safety::spike06 | RFC-002, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| Review Package / Approved Strategy 产品语义组 | DEC-029, DEC-046 | 同上 | — | DEC-046 | RFC-004 | _(placeholder)_ | Semantic groups + no fabricated empty-group content _(planned)_ |
| Review semantic-group diff + edit-intent confirmation + stale draft recovery | DEC-047 | 同上 | — | DEC-047 | RFC-004 | _(placeholder)_ | Model/user diff + ambiguous edit intent + refresh/compare recovery _(planned)_ |

### D. 检索与证据

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| On-demand Hybrid RAG + 分层数据访问 | DEC-014, DEC-032 | [Hybrid Retrieval](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md) | spike-09 | test_failure_recovery::spike09（degraded 不伪造） | RFC-005 | _(placeholder)_ | _(placeholder)_ |
| Versioned Sources / Task Associations / Durable Processing / Format-aware Fragments / Evidence Links + reversible removal | DEC-025, DEC-061, DEC-067 | [Source and Evidence](../specs/evidence/source-and-evidence-specification.md) | spike-01 | commit.py evidence_links + business_audit + DEC-061 / 067 | RFC-004, RFC-005, RFC-007 / ARP-08 | _(placeholder)_ | Per-source partial acceptance + six-state processing + four locator lanes + removed Source excluded from Current Truth; physical purge handled separately _(planned)_ |
| PostgreSQL-native retrieval plane + versioned index generation + deterministic RRF baseline | DEC-032, DEC-068 | [Hybrid Retrieval](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md) | — | DEC-068 + Issue #56 / Draft PR #57 | RFC-005 | _(placeholder)_ | Same authorized candidate relation + exact / CJK lexical / semantic / hybrid + generation reconcile / switch + 4 / 20 / 60 / 12 bounds + no baseline reranker _(planned)_ |
| Server-derived retrieval scope + referenced Evidence Package + atomic Formal Evidence + explicit degradation | DEC-058, DEC-061, DEC-069 | [Hybrid Retrieval](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md), [Source and Evidence](../specs/evidence/source-and-evidence-specification.md) | — | DEC-069 + Issue #56 / Draft PR #57 | RFC-005 / RFC-007 | _(placeholder)_ | SQL pre-ranking scope isolation + narrow Source / Evidence projection + immutable RetrievalRun / referenced package + complete DatasetStatistic + Validator atomic commit + representative hard gates / human relevance + explicit limitation _(planned)_ |
| Fixed Embedding target + Source / Evidence public catalog + accelerated MVP-0 profile | DEC-070 | [Hybrid Retrieval](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md), [Source and Evidence](../specs/evidence/source-and-evidence-specification.md) | bounded TS-01 / TS-03 inside foundation Issues | DEC-070 + RFC-005 Final Review | RFC-005 | MVP-0 Contract / Retrieval foundation | MVP-0 Direct / Exact / Lexical + JSON / text / TXT / MD / CSV; MVP-1 text PDF + `text-embedding-3-small` 1536 cosine / Semantic / Hybrid |
| 分层证据 + 可追溯结论 + 渐进式证据披露 | DEC-008, DEC-047 | [Source and Evidence](../specs/evidence/source-and-evidence-specification.md) | — | runtime-evidence.md + DEC-047 | RFC-004, RFC-005 | _(placeholder)_ | Five-class badge + truthful locator + no fabricated confidence _(planned)_ |

### E. 运行时可靠性（失败/恢复/重试/可观测）

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| 有界重试（仅 transient）+ 预算耗尽 | DEC-033 | [Runtime Failure / Recovery](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md) | spike-02, spike-11 | test_failure_recovery::spike02/spike11 | RFC-007 | _(placeholder)_ | _(placeholder)_ |
| Invalid Structured Output 不做基础设施盲重试；只按有界预算执行 Normalization → re-parse / validate → 最多一次 Constrained Repair | DEC-033, DEC-053 | 同上 | spike-03 | test_failure_recovery::spike03 | RFC-006, RFC-007 | _(placeholder)_ | Structured-output recovery order + shared budget _(planned)_ |
| 取消无部分写入 | DEC-033 | 同上 | spike-10 | test_failure_recovery::spike10 | RFC-002 | _(placeholder)_ | _(placeholder)_ |
| Manual Recovery 不重复 | DEC-033 | 同上 | Recovery Case | test_failure_recovery::recovery_case | RFC-002 | _(placeholder)_ | _(placeholder)_ |
| 阶段时间线 + 行动导向错误与恢复 | DEC-033, DEC-047 | 同上 | — | DEC-047 | RFC-003, RFC-004, RFC-007 | _(placeholder)_ | No fake percentage + state-appropriate recovery actions _(planned)_ |
| 运行身份分层 + Trace 关联 | DEC-033 | 同上 | Trace Correlation | test_observability::correlation | RFC-007 | _(placeholder)_ | _(placeholder)_ |

### F. 核心 Skill 契约（生产实现待 RFC）

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| Product Intake & Fact Extraction Skill + Fact / Claim integrity | DEC-026, DEC-060 | [Product Intake](../specs/skills/product-intake-and-fact-extraction-skill.md) | spike-01（骨架） | graph.py extract_facts（临时）+ DEC-060 | RFC-004, RFC-005, RFC-006 | _(placeholder)_ | Verified Fact vs Documented Claim and no unsupported promotion _(planned)_ |
| Customer Insight Analysis Skill | DEC-027 | [Customer Insight](../specs/skills/customer-insight-analysis-skill.md) | spike-01（骨架） | graph.py analyze_insights（临时） | RFC-005, RFC-006 | _(placeholder)_ | _(placeholder)_ |
| Product Positioning Skill | DEC-028 | [Product Positioning](../specs/skills/product-positioning-skill.md) | spike-01（骨架） | graph.py generate_positioning（临时） | RFC-006 | _(placeholder)_ | _(placeholder)_ |
| Marketing Brief Generation Skill + 六组产品语义 + 声明完整性 + 下游失效 | DEC-030, DEC-046, DEC-047, DEC-060 | [Marketing Brief](../specs/skills/marketing-brief-generation-skill.md) | spike-01（骨架） | graph.py generate_marketing_brief（临时）+ DEC-046 / 047 / 060 | RFC-004, RFC-005, RFC-006 | _(placeholder)_ | Six-group contract + claim-level exclusion + strategy-lock versioning + XHS invalidation _(planned)_ |
| 四层结构化 Marketing Brief | DEC-006 | [Marketing Brief](../specs/skills/marketing-brief-generation-skill.md) | — | DEC-006 | RFC-006 | _(placeholder)_ | _(placeholder)_ |

### G. 平台 Adapter

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| 平台中立核心 + Xiaohongshu Demo | DEC-004 | [Integration Boundaries](../architecture/integration-boundaries.md) | — | DEC-004 | RFC-004 | _(placeholder)_ | _(placeholder)_ |
| Xiaohongshu Brief Mapping Adapter + 六组产品语义 + Claim 继承 + 自身编辑边界 | DEC-031, DEC-046, DEC-047, DEC-060 | [Xiaohongshu Adapter](../specs/adapters/xiaohongshu-brief-mapping-adapter.md) | — | DEC-031 spec + DEC-046 / 047 / 060 | RFC-004, RFC-005, RFC-006 | _(placeholder)_ | Six-group mapping + no prohibited-claim evasion + brief-lock versioning _(planned)_ |

---

## 备注

- `—`（Spike Scenario 列）表示该需求属**业务输出质量 / 契约层**，非 Spike-001 的运行时风险验证对象；其生产验证在对应 RFC 接受后、由 Future Test（占位）覆盖。
- Spike-001 的临时实现（`spikes/spike-001-*/**`）**不**作为生产模块；Future Epic 实现对应 Skill / Runtime 时应基于 Accepted DEC + RFC 重新实现，而非直接迁移 Spike 代码。
- `Future Epic` / `Future Test` 全部为空占位；只有在完整策划文档包与 Goal 文本被用户接受、最终 Implementation Readiness Review 通过，并收到用户明确的“进入 Goal 执行阶段”指令后方可实例化。RFC Acceptance 是必要条件，不是充分条件。

## Current Status（2026-08-07）

```text
Spike-001 = COMPLETED
RFC-001 / RFC-002 / RFC-003 / RFC-006 = ACCEPTED
RFC-004 = ACCEPTED
RFC-005 = ACCEPTED (2026-08-07; DQ-01～10 by DEC-067～070; Final Review PASS)
RFC-007 = DRAFTING (Issue #58; P-68A / P-69A / P-70A proposed)
FND-001 / FND-002 / FND-003 = COMPLETED

ARP-01 / ARP-04 / ARP-10 = ACCEPTED (full declared scope)
ARP-02 / ARP-03 / ARP-09 = ACCEPTED (TS-01 minimum slice only; full artifact pending)
ARP-05 / ARP-06 / ARP-07 / ARP-08 = NOT CREATED

Pre-development planning = AUTHORIZED
TS-01～TS-05 Execution = NOT AUTHORIZED
Business / Production Implementation = NOT AUTHORIZED
Actual Goal = NOT CREATED / NOT ACTIVATED

Future Epic / Issue / Test links = PENDING final planning package and Goal acceptance
```

## Historical Status Snapshot（PR #28 之前）

```text
Spike Execution Status = COMPLETED
RFC-001 Status = ACCEPTED (2026-07-30)
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY

Foundation Planning = AUTHORIZED（生成并审查 FND Issue Candidates）
Foundation Candidate Planning = COMPLETED（FND-001 / FND-002 / FND-003 均已形成）
Foundation Candidate Final Review = PASS（2026-07-30，范围完整性 / 职责分离 / 依赖顺序 / RFC-001 一致性 / 后续 RFC 范围保护全部 PASS，Decision Conflict = NONE）
FND-001 Candidate Status = COMPLETED
FND-001 Issue Creation = COMPLETED（Issue #6，CLOSED）
FND-001 Implementation = COMPLETED（PR #7 MERGED，Merge Commit 5b75bcf99eba45f47fa501bfcf60d1e637601a07，2026-07-30）
FND-001 Merge = COMPLETED（用户 Merge 决定「我已 merged」确认；Merge Method = Merge Commit；Merged By = JettxonHo）
FND-001 Verification = PASS（Post-merge Smoke Verification）
FND-001 Code Status = COMPLETED
FND-001 Archive Status = COMPLETED（经文档归档 PR #8 记录，Archive Merge Commit e109452a55a30536e5b2a78547bc52b2e466cab9）
FND-001 Overall Status = COMPLETED
FND-001 Completed Date = 2026-07-30
FND-002 Candidate Status = COMPLETED（2026-07-30 用户明确授权「确认授权创建并实施 FND-002」；PR #10 已由用户 Merge）
FND-002 Issue Creation = COMPLETED（2026-07-30，用户明确授权「确认授权创建并实施 FND-002」，Issue #9，CLOSED / COMPLETED）
FND-002 Implementation = COMPLETED（2026-07-30，Branch foundation/002-architecture-test-foundation；PR #10 已合并）
FND-002 Merge = COMPLETED（用户人工 Merge；Merge Commit b966491865f57910d186542b1eb5191544a254f3；Merge Method = Merge Commit；Merged At = 2026-07-30T17:03:04Z；Merged By = JettxonHo）
FND-002 Verification = PASS（Post-merge Verification，合并后于 main 执行）
FND-002 Status = COMPLETED
FND-002 Completed Date = 2026-07-30
FND-002 Code Status = COMPLETED
FND-002 Archive Status = COMPLETED（经文档归档 PR #13 记录，本归档 PR 合并后正式生效）
FND-002 Overall Status = COMPLETED
FND-003 Candidate Status = COMPLETED（2026-07-31 用户授权创建并实施；PR #15 已由用户 Merge；经本 Documentation 归档 PR #22 记录，本归档 PR 合并后正式生效）
FND-003 Issue Creation = COMPLETED（2026-07-31，Issue #14，CLOSED / COMPLETED）
FND-003 Implementation = COMPLETED（2026-07-31，PR #15 已由用户 Merge）
FND-003 Merge = COMPLETED（Merge Commit 3f012b6405a6464b629873441ff50eff8c5d52ec；Merge Method = Merge Commit；Merged At = 2026-07-30T20:34:09Z / SGT 2026-07-31T04:34:09+08:00；Merged By = JettxonHo）
FND-003 Verification = PASS（Post-merge：main 8/8 Required Checks + 本地全量验证）
FND-003 Code Status = COMPLETED
FND-003 Archive Status = COMPLETED（经本 Documentation 归档 PR #22 记录，本归档 PR 合并后正式生效）
FND-003 Overall Status = COMPLETED
FND-003 Completed Date = 2026-07-31
Foundation Implementation Status = COMPLETED（FND-001 / FND-002 / FND-003 全部完成并合并；本归档 PR 合并后正式生效）
Foundation Archive Status = COMPLETED（PR #8 / PR #13 / 本归档 PR；本归档 PR 合并后正式生效）
Foundation Program Status = COMPLETED（本归档 PR 合并后正式生效）
Business / Production Implementation = NOT AUTHORIZED（Foundation 完成不授权任何业务或生产实现）
RFC-002 Status = ACCEPTED（2026-08-04 用户正式决定；Acceptance ≠ Authorization）
RFC-002 Merge = COMPLETED（PR #24；Merge Commit a71e2b3201f2e67f0173cd9691a04011b1b65b09；RFC-002 Issue #23 = CLOSED / COMPLETED）
RFC-002-DQ-01 through DQ-17 = ACCEPTED
Pending Decision Questions = 0
RFC-002 Implementation = NOT AUTHORIZED（Acceptance ≠ Authorization）

Architecture Readiness Package Planning = COMPLETED
Architecture Readiness Package Planning Report = ACCEPTED（2026-08-04 用户正式决定）
Accepted Planning Model = DEPENDENCY WAVES + FIRST-SPIKE MINIMUM SLICE（ACCEPTED PLANNING MODEL）
QL-02 Model = CROSS-CUTTING SECURITY QUALIFICATION CATALOG WITH PER-SPIKE APPLICABLE SLICES
Planning Model Acceptance = NOT Artifact Content Acceptance
Planning Model Acceptance = NOT Technical Spike Authorization
Planning Model Acceptance = NOT Production Implementation Authorization

Architecture Readiness Artifact Creation = NOT AUTHORIZED
Technical Spike Planning = NOT AUTHORIZED
TS-01～TS-05 Execution = NOT AUTHORIZED
Persistence Implementation = NOT AUTHORIZED
Production Implementation = NOT AUTHORIZED

ARP-01～ARP-10 definitions exist in RFC-002; the Artifact files have not been created.
Planning Acceptance ≠ Artifact Creation Authorization.

Next Topic: READINESS ARTIFACT CREATION AUTHORIZATION（状态 = PENDING USER DECISION；Planning Acceptance ≠ Artifact Creation Authorization；Artifact Creation / Spike Planning / Spike Execution / Implementation 均 NOT AUTHORIZED；Coding Agent 不得创建任何 Readiness Artifact 或开始 Spike）
```
