# MVP Traceability Matrix（可追溯矩阵 v1）

> **Status: DRAFT — PENDING USER REVIEW**
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

### G. RFC Gate 与下一议题

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| RFC Planning and Dependency Order | DEC-038 | specs/governance/rfc-planning-and-dependency-order.md | — | DEC-038 decision file | RFC-001—RFC-007 | _(placeholder)_ | _(placeholder)_ |
| Repository and Application Architecture Gate | DEC-038 | specs/governance/rfc-planning-and-dependency-order.md | — | architecture-baseline-v1 §9 | RFC-001 | _(placeholder)_ | _(placeholder)_ |
| Persistence and Transaction Architecture Gate | DEC-038 | specs/governance/rfc-planning-and-dependency-order.md | — | architecture-baseline-v1 §9 | RFC-002 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-01 Modular Monolith First | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §19 | RFC-001 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-02 Backend Language and LangGraph Binding | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §18 | RFC-001, RFC-003 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-03 Repository and Package Directory Structure | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §17 | RFC-001, RFC-002, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-04 Layer Responsibilities and Dependency Rules（Domain Independence / Application Transaction Ownership / Atomic Business Commit / Graph Node Boundary / Human Review Transaction / Module Public Contract / Architecture Tests） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §16 | RFC-001, RFC-002, RFC-003, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-05 Skill Code Shape and Architectural Relationships（Skill Position / Prepare-Execute-Commit / Repository & Transaction Boundary / Provider Port Boundary / LangGraph Boundary / Independent Execution / Version Boundary / Skill Tests） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §14 | RFC-001, RFC-006 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-06 Dependency Injection, Configuration and Application Bootstrap（Constructor Injection / Composition Root / Configuration Loading & Validation / Layer Boundary / Secret Boundary / Resource Lifetime / Test Replacement） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §15 | RFC-001, RFC-006, RFC-007 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-07 Process Boundaries and Sync/Async Execution Strategy（Modular Monolith Release Boundary / API·Worker·CLI Process / Durable Dispatch / Human Review Resume / Atomic Resume Coordination / Worker Recovery / Sync-first / Bounded Concurrency / Dispatch Payload / Cancellation） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §13 | RFC-001, RFC-002, RFC-003, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-08 Module Public Contracts, Cross-module Collaboration and Cycle Governance（Public Facade `modules.<module>.public` / Immutable Snapshot / Cross-module Public Query / Owning Application Service State Change / Orchestration Coordination / Composite Use Case / Application Event Post-commit / DAG Dependency / Public Error Contract / Architecture Tests） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §12 | RFC-001, RFC-002, RFC-003, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-09 Quality Toolchain, Architecture Enforcement, CI Quality Gates and Test Baseline（Ruff Formatter/Linter / Pyright Strict-first / pytest Strict Markers / Import Linter + Custom Architecture Tests / Deterministic Required PR Tests / Branch-aware Coverage 80% / pip-audit / Secret Detection / Protected main Required Checks / Live Evaluation separated） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §11 | RFC-001 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-10 Production Skeleton Scope, Foundation Authorization Gate and RFC Closure（Acceptance vs Authorization Separation / Foundation Planning Gate / Foundation Implementation separate authorization / Initial Foundation Scope = Package + Quality + Architecture Tests + CI + Repository Security / Business Modules·Platform·Orchestration·API·Worker·Bootstrap·DB·LangGraph·Model·Retrieval·Observability NOT IMPLEMENTED / Spike Source Migration Prohibited / FND-001→FND-002→FND-003 / Mandatory Stop Conditions） | DEC-034, DEC-036, DEC-038 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §10 | RFC-001, RFC-002, RFC-003, RFC-004, RFC-005, RFC-006, RFC-007 | _(placeholder: Future Roadmap Draft v0)_ | _(placeholder)_ |
| **FND-001 — Backend Package and Local Tooling Foundation**（**COMPLETED**；Issue #6 CLOSED；PR #7 MERGED；Merge Commit `5b75bcf99eba45f47fa501bfcf60d1e637601a07`；Merged 2026-07-30T12:38:48Z by JettxonHo（用户 Merge 决定「我已 merged」）；Post-merge Smoke Verification = PASS；Backend Package `apps/backend/src/ai_ecommerce_agent/` + Python 3.13 + uv Lockfile + Ruff/Pyright/pytest/Coverage Local Tooling + Unified Local Commands；Code Status = COMPLETED，Archive Status = COMPLETED（经文档归档 PR #8 记录），Overall Status = COMPLETED） | DEC-036, DEC-038 | docs/foundation/foundation-issue-candidates.md | apps/backend/ | PR #7 + docs/foundation/foundation-issue-candidates.md | RFC-001（DQ-02 / DQ-03 / DQ-09 / DQ-10） | [Issue #6](https://github.com/JettxonHo/ai-ecommerce-agent/issues/6) | [PR #7](https://github.com/JettxonHo/ai-ecommerce-agent/pull/7)（MERGED） |
| **FND-002 — Architecture Enforcement and Test Foundation**（**COMPLETED**；Issue Creation COMPLETED（[Issue #9](https://github.com/JettxonHo/ai-ecommerce-agent/issues/9)，CLOSED / COMPLETED）；PR #10 已由用户人工 Merge（Merge Commit `b966491865f57910d186542b1eb5191544a254f3`，2026-07-30T17:03:04Z，Merged By = JettxonHo）；Post-merge Verification = PASS；Import Linter 10 Contracts + 自定义 grimp 规则（Public Facade / Module DAG）+ AST 语义测试（环境访问 / 技术泄漏 / Skill Boundary）+ pytest 8-Marker 分类 + 默认 Network Protection + 统一 Architecture Test 命令；Branch `foundation/002-architecture-test-foundation`（已完全合并）；依赖 FND-001 = MERGED ✓；Code Status = COMPLETED，Archive Status = COMPLETED（经文档归档 PR #13 记录），Overall Status = COMPLETED） | DEC-036, DEC-038 | docs/foundation/foundation-issue-candidates.md | apps/backend/tests/architecture/ | PR #10 + docs/foundation/foundation-issue-candidates.md | RFC-001（DQ-03 / DQ-04 / DQ-05 / DQ-06 / DQ-08 / DQ-09 / DQ-10） | [Issue #9](https://github.com/JettxonHo/ai-ecommerce-agent/issues/9)（CLOSED） | [PR #10](https://github.com/JettxonHo/ai-ecommerce-agent/pull/10)（MERGED） |
| **FND-003 — CI, Security and Repository Protection**（**COMPLETED**；2026-07-31 用户授权创建并实施；PR #15 已由用户 Merge（Merge Commit `3f012b6405a6464b629873441ff50eff8c5d52ec`，2026-07-30T20:34:09Z / SGT 2026-07-31T04:34:09+08:00，Merged By = JettxonHo）；Post-merge Verification = PASS（main 8/8 Required Checks + 本地全量验证）；deps: FND-001 = MERGED ✓，FND-002 = MERGED ✓；3 Workflows + 8 Stable Required Checks（`quality / format`・`lint`・`typecheck`・`architecture`；`test / unit-contract`・`package-build`；`security / dependency-audit`・`secret-detection`）+ Dependency Audit（pip-audit，锁定 dev 依赖）+ Secret Detection（gitleaks 8.30.1，SHA-256 校验发布二进制，全历史 + `--redact`，内置默认规则）+ Dependabot（github-actions + uv 生态，weekly，不自动 Merge）+ PR / Issue Templates + `main` Branch Protection（Require PR / 8 Required Checks / strict / Conversation Resolution / enforce_admins）+ Repository Governance Documentation；PR #15 Required Checks 全绿；受控负向验证 9 场景全部真实阻止（含 `mergeable_state = blocked`）；5 维度对抗审计 PASS（0 BLOCKING/HIGH）；负向验证发现并修复 gitleaks `useDefault` 静默漏检缺陷；完成归档经本 Documentation PR #22 记录，合并后 Archive / Overall Status = COMPLETED） | DEC-036, DEC-038 | docs/foundation/foundation-issue-candidates.md | — | PR #15 + docs/foundation/foundation-issue-candidates.md + docs/development/ci-and-repository-governance.md | RFC-001（DQ-06 / DQ-08 / DQ-09 / DQ-10）, FND-001, FND-002, GitHub Governance, Security Foundation | [Issue #14](https://github.com/JettxonHo/ai-ecommerce-agent/issues/14)（CLOSED） | [PR #15](https://github.com/JettxonHo/ai-ecommerce-agent/pull/15)（MERGED） |


### A. 核心工作流与编排

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| 确定性 Workflow 编排（LLM 受约束） | DEC-011, DEC-023 | specs/workflow/workflow-state-specification | spike-01 | test_skeleton::test_normal_workflow_end_to_end | RFC-A, RFC-C | _(placeholder)_ | _(placeholder)_ |
| 任务级持久状态 + 跨会话 Resume | DEC-013, DEC-024 | specs/workflow/workflow-state-specification | spike-05, spike-08 | test_review_safety::spike05/spike08 | RFC-C | _(placeholder)_ | _(placeholder)_ |
| 单审查节点 + 异常暂停 | DEC-007 | specs/workflow/human-review-and-approved-strategy-contract | spike-01, spike-05 | test_skeleton / test_review_safety | RFC-D | _(placeholder)_ | _(placeholder)_ |
| MVP 不用 Multi-Agent（Bounded Worker） | DEC-021 | architecture/system-architecture | — | architecture-baseline-v1 | RFC-A | _(placeholder)_ | _(placeholder)_ |

### B. 状态、版本与事务

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| Versioned Domain State + Compact State | DEC-024 | specs/workflow/workflow-state-specification | spike-01, spike-06 | test_transaction_idempotency | RFC-B | _(placeholder)_ | _(placeholder)_ |
| 三类存储分离；Checkpoint≠Current Truth | DEC-024, DEC-033 | specs/runtime/workflow-runtime-failure-recovery-retry-and-observability | spike-01, spike-08 | test_skeleton::test_three_stores_are_separate | RFC-B, RFC-C | _(placeholder)_ | _(placeholder)_ |
| 原子提交 + 幂等 + 回滚 | DEC-029, DEC-033 | specs/workflow/human-review-and-approved-strategy-contract | spike-04, spike-06, Recovery | test_transaction_idempotency::spike04 | RFC-B | _(placeholder)_ | _(placeholder)_ |
| 阶段级失效与部分重跑 | DEC-009 | specs/workflow/workflow-state-specification | spike-05 | test_review_safety::spike05（pos_count==1） | RFC-B | _(placeholder)_ | _(placeholder)_ |

### C. Human Review 与 Approved Strategy

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| Human Review 节点边界 + 独立提交事务 | DEC-029 | specs/workflow/human-review-and-approved-strategy-contract | spike-01, spike-05 | graph.py 节点分离 + review.py | RFC-D | _(placeholder)_ | _(placeholder)_ |
| No Stale Review Package Submission | DEC-029 | 同上 | spike-07 | test_review_safety::spike07（StaleReviewError） | RFC-D | _(placeholder)_ | _(placeholder)_ |
| Duplicate Submit 幂等 | DEC-029 | 同上 | spike-06 | test_review_safety::spike06 | RFC-B, RFC-D | _(placeholder)_ | _(placeholder)_ |

### D. 检索与证据

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| On-demand Hybrid RAG + 分层数据访问 | DEC-014, DEC-032 | specs/runtime/hybrid-retrieval-and-evidence-runtime | spike-09 | test_failure_recovery::spike09（degraded 不伪造） | RFC-E | _(placeholder)_ | _(placeholder)_ |
| Versioned Sources / Fragments / Evidence Links | DEC-025 | specs/evidence/source-and-evidence-specification | spike-01 | commit.py evidence_links + business_audit | RFC-E | _(placeholder)_ | _(placeholder)_ |
| 分层证据 + 可追溯结论 | DEC-008 | specs/evidence/source-and-evidence-specification | — | runtime-evidence.md | RFC-E | _(placeholder)_ | _(placeholder)_ |

### E. 运行时可靠性（失败/恢复/重试/可观测）

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| 有界重试（仅 transient）+ 预算耗尽 | DEC-033 | specs/runtime/workflow-runtime-failure-recovery-retry-and-observability | spike-02, spike-11 | test_failure_recovery::spike02/spike11 | RFC-G | _(placeholder)_ | _(placeholder)_ |
| Invalid Structured Output 不重试 | DEC-033 | 同上 | spike-03 | test_failure_recovery::spike03 | RFC-F, RFC-G | _(placeholder)_ | _(placeholder)_ |
| 取消无部分写入 | DEC-033 | 同上 | spike-10 | test_failure_recovery::spike10 | RFC-B | _(placeholder)_ | _(placeholder)_ |
| Manual Recovery 不重复 | DEC-033 | 同上 | Recovery Case | test_failure_recovery::recovery_case | RFC-B | _(placeholder)_ | _(placeholder)_ |
| 运行身份分层 + Trace 关联 | DEC-033 | 同上 | Trace Correlation | test_observability::correlation | RFC-G | _(placeholder)_ | _(placeholder)_ |

### F. 核心 Skill 契约（生产实现待 RFC）

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| Product Intake & Fact Extraction Skill | DEC-026 | specs/skills/product-intake-and-fact-extraction-skill | spike-01（骨架） | graph.py extract_facts（临时） | RFC-F | _(placeholder)_ | _(placeholder)_ |
| Customer Insight Analysis Skill | DEC-027 | specs/skills/customer-insight-analysis-skill | spike-01（骨架） | graph.py analyze_insights（临时） | RFC-E, RFC-F | _(placeholder)_ | _(placeholder)_ |
| Product Positioning Skill | DEC-028 | specs/skills/product-positioning-skill | spike-01（骨架） | graph.py generate_positioning（临时） | RFC-F | _(placeholder)_ | _(placeholder)_ |
| Marketing Brief Generation Skill | DEC-030 | specs/skills/marketing-brief-generation-skill | spike-01（骨架） | graph.py generate_marketing_brief（临时） | RFC-F | _(placeholder)_ | _(placeholder)_ |
| 四层结构化 Marketing Brief | DEC-006 | specs/skills/marketing-brief-generation-skill | — | DEC-006 | RFC-F | _(placeholder)_ | _(placeholder)_ |

### G. 平台 Adapter

| Requirement | DEC | Spec | Spike Scenario | Evidence | Required RFC | Future Epic | Future Test |
|---|---|---|---|---|---|---|---|
| 平台中立核心 + Xiaohongshu Demo | DEC-004 | architecture/integration-boundaries | — | DEC-004 | RFC-D | _(placeholder)_ | _(placeholder)_ |
| Xiaohongshu Brief Mapping Adapter | DEC-031 | specs/adapters/xiaohongshu-brief-mapping-adapter | — | DEC-031 spec | RFC-D, RFC-F | _(placeholder)_ | _(placeholder)_ |

---

## 备注

- `—`（Spike Scenario 列）表示该需求属**业务输出质量 / 契约层**，非 Spike-001 的运行时风险验证对象；其生产验证在对应 RFC 接受后、由 Future Test（占位）覆盖。
- Spike-001 的临时实现（`spikes/spike-001-*/**`）**不**作为生产模块；Future Epic 实现对应 Skill / Runtime 时应基于 Accepted DEC + RFC 重新实现，而非直接迁移 Spike 代码。
- `Future Epic` / `Future Test` 全部为空占位，**待用户明确 READY / CONDITIONALLY READY 决策并接受相关 RFC 后**方可实例化。

## Final Status

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
RFC-002 Authorization = NOT AUTHORIZED

Next Topic: RFC-002 Authorization Gate（RFC-002 — Persistence and Transaction Architecture；状态 = PENDING USER DECISION；RFC-002 Drafting / Issue Creation / Implementation 均 NOT AUTHORIZED；Coding Agent 不得起草或开始；业务实现仍未授权）
```
