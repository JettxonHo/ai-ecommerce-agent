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
| RFC-001-DQ-01 Modular Monolith First | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §15 | RFC-001 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-02 Backend Language and LangGraph Binding | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §14 | RFC-001, RFC-003 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-03 Repository and Package Directory Structure | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §13 | RFC-001, RFC-002, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-04 Layer Responsibilities and Dependency Rules（Domain Independence / Application Transaction Ownership / Atomic Business Commit / Graph Node Boundary / Human Review Transaction / Module Public Contract / Architecture Tests） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §12 | RFC-001, RFC-002, RFC-003, RFC-004 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-05 Skill Code Shape and Architectural Relationships（Skill Position / Prepare-Execute-Commit / Repository & Transaction Boundary / Provider Port Boundary / LangGraph Boundary / Independent Execution / Version Boundary / Skill Tests） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §10 | RFC-001, RFC-006 | _(placeholder)_ | _(placeholder)_ |
| RFC-001-DQ-06 Dependency Injection, Configuration and Application Bootstrap（Constructor Injection / Composition Root / Configuration Loading & Validation / Layer Boundary / Secret Boundary / Resource Lifetime / Test Replacement） | RFC-001 | docs/rfcs/rfc-001-repository-and-application-architecture.md | — | architecture-baseline-v1 §11 | RFC-001, RFC-006, RFC-007 | _(placeholder)_ | _(placeholder)_ |


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
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY

Next Topic: RFC-001-DQ-07 Process Boundaries and Sync/Async Execution Strategy
```
