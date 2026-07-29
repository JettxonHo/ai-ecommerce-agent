# Technical Spike and Architecture Readiness Gate — 概念 Specification

> **Status: CONCEPTUAL（概念）**
> 来源决定：[DEC-034 — Technical Spike Plan and Architecture Readiness Gate](../../decisions/dec-034-technical-spike-and-architecture-readiness-gate.md)。Amends DEC-023 / DEC-033。
> 本文件是 DEC-034 的**概念结构化记录**，**不是最终实现契约**，也**不是 Spike 执行计划**。它记录 Spike 必须验证的架构行为、必选场景、证据要求、Readiness Gate 判据与产出，但不规定具体语言、版本、数据库、Checkpointer Backend、测试框架、Trace Provider 或 Spike 代码目录。这些属于下一议题 `Technical Spike Execution Brief and Temporary Spike Stack`。
> **当前阶段只创建规划和规格文档，不实现 Spike 代码。**
> Development Status: **NOT READY**。

---

## §0 目的（Purpose）

本 Spec 概念化地定义：在 AI Ecommerce Agent 进入正式业务开发前，必须完成的最小架构 Technical Spike，以及以 Spike 证据、Readiness Review 和用户明确确认为基础的 Architecture Readiness Gate。

正式流程（概念）：

```text
Accepted Decisions + Current Specifications + Architecture Documents
↓
Technical Spike Plan
↓
Minimal Architecture Prototype
↓
Automated Failure and Recovery Tests
↓
Spike Evidence
↓
Spike Report
↓
Architecture Readiness Review
↓
Explicit User Decision
↓
READY / CONDITIONALLY READY / NOT READY
```

在用户明确确认 READY 前，`Development Status = NOT READY`。

---

## §1 职责与非职责（Responsibilities / Non-responsibilities）

Spike 职责：

- 验证已接受的 Workflow / State / Persistence / Human Review / Evidence / Retry / Recovery / Transaction / Observability 架构在最小代码环境中是否真正可运行；
- 验证架构行为（非完整业务输出质量）；
- 产出可审查证据（Test Results / Runtime Evidence / State and Version Evidence / Transaction Evidence / Trace Evidence / Limitations）；
- 作为 RFC 与 Roadmap 的输入。

Spike 非职责（**不是**）：

- MVP 第一版；
- 正式后端；
- 正式业务 Graph；
- 四个核心 Skill 的生产实现；
- 最终 Prompt；
- 正式数据库 Schema；
- 最终 API；
- 前端产品；
- 可直接部署的生产代码。

---

## §2 Technical Spike 验证的架构风险

Spike 至少验证以下 16 项架构风险：

1. StateGraph 是否能够确定性 Compile 和 Invoke；
2. Graph State 是否可以保持紧凑，只保存业务对象引用；
3. Business Domain State 是否与 LangGraph Checkpoint 分离；
4. Human Review 是否能够正确 Interrupt 和 Resume；
5. Resume 是否会重复执行已经完成的 Node；
6. Review Package 是否能够固定上游版本；
7. 旧 Review Package 是否会被可靠拒绝；
8. Checkpoint 是否能够与 Current Truth 对账；
9. 旧 Checkpoint 是否会被可靠拒绝；
10. Retry 是否会错误创建重复业务版本；
11. 事务失败后是否能够完整回滚；
12. Idempotency 是否能够防止重复 Submit 和 Commit；
13. Cancellation 是否会留下部分业务状态；
14. Retrieval Fallback 是否能够传播 Evidence Limitation；
15. Structured Output Failure 是否会被阻止写入 Current Truth；
16. Runtime Records、Logs 和 Trace 是否能够关联完整执行链。

---

## §3 最小 Spike Workflow（Minimum Spike Workflow）

```text
START
↓
load_task_context
↓
mock_fact_generation
↓
validate_and_commit_facts
↓
mock_insight_generation
↓
validate_and_commit_insights
↓
mock_positioning_generation
↓
create_review_package
↓
INTERRUPT: waiting_for_review
↓
submit_review
↓
commit_approved_strategy
↓
mock_marketing_brief_generation
↓
commit_marketing_brief
↓
END
```

Xiaohongshu Adapter 不属于主 Spike 路径的硬要求。可增加一个可选 Mock Adapter Node 验证 `Marketing Brief 修改 → Platform Mapping 失效`，但不得因此扩大 Spike 范围。

---

## §4 Mock Business Objects

Spike 可使用固定 Mock 数据。这些结构只用于验证架构行为，**不构成最终 Domain Schema**。

### Mock Facts

```text
商品名称：Mock 通勤杯
容量：500 mL
重量：260 g
材料：304 不锈钢
```

### Mock Insights

```text
Evidence-backed Insight: 部分通勤用户担心随身携带水杯时发生漏水。
Hypothesis: 通勤用户可能将轻量视为重要购买因素。
```

### Mock Positioning Candidates（至少两个实质不同候选）

```text
Candidate A: 轻量通勤
Candidate B: 密封安心
```

### Mock Approved Strategy

至少包括：Target Segment / Usage Context / Core Need / Value Proposition / Differentiation / Proof Points / Accepted Hypotheses / Evidence Limitations。

### Mock Marketing Brief

至少包括：Audience / Core Message / Primary Benefit / Proof Points / Content Angles / Prohibited Claims / Evidence Limitations。

---

## §5 Spike Graph State（紧凑、引用导向）

```text
SpikeGraphState
├── task_id
├── thread_id
├── current_run_id
├── current_stage
├── fact_version_id
├── insight_version_id
├── positioning_version_id
├── review_id
├── approved_strategy_version_id
├── marketing_brief_version_id
├── waiting_reason
├── last_error_id
└── cancellation_requested
```

Graph State 不保存：完整 Facts / 完整 Insights / 完整 Positioning Candidates / 完整 Review Draft / 完整 Evidence Package / 全部历史版本 / 完整文档或评论内容。正式业务内容必须从 Business Repository 读取。

---

## §6 Repository Separation（三类存储逻辑分离）

| 仓库 | 负责 |
|---|---|
| **Business Repository** | Task / Domain Versions / Current Truth Pointers / Stage State / Review Package / Strategy Draft / Approved Strategy / Marketing Brief / Evidence Links / Audit Records |
| **Runtime Repository** | Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error / Recovery Case / Idempotency Record / Cancellation Record |
| **Checkpoint Store** | LangGraph 执行状态 / Interrupt / Resume 位置 / 临时运行上下文 / Checkpoint Metadata |

即使 Spike 使用同一个物理存储，也必须保持逻辑边界。正式规则：`LangGraph Checkpoint Store ≠ Business Current Truth Repository`。

---

## §7 必选 Spike Scenarios（Required Spike Scenarios）

### Spike-01：Normal Workflow

成功标准：每个 Stage 只正式提交一次 / Current Truth Pointer 正确 / Graph 在 Review 前正确暂停 / Resume 创建新的 Workflow Run / Resume 后不重新执行已完成 Positioning / Trace 关联完整执行链。

### Spike-02：Transient Failure and Retry

成功标准：Skill Run ID 不变 / Node Execution ID 不变 / Attempt ID 不同 / 只创建一个业务版本 / Retry 与 Rerun 可明确区分 / Retry Record 和 Trace 完整。

### Spike-03：Invalid Structured Output

成功标准：Schema Validation 生效 / 允许有限 Deterministic Normalization / 允许有限 Constrained Repair / 超过上限后 Skill Run 失败 / 不创建业务版本 / 不更新 Current Truth / 不创建 Formal Evidence Link。

### Spike-04：Transactional Rollback

成功标准：Domain Version 回滚 / Evidence Link 回滚 / Current Truth Pointer 不变 / Stage State 不变 / Audit 不错误记录为成功 / Retry 后只创建一个正式版本。

### Spike-05：Human Review Interrupt and Resume

成功标准：Review Package 成功创建 / Graph 正确 Interrupt / Task Status = `waiting_for_review` / Review Submit 事务创建 Approved Strategy / Resume 后读取 Approved Strategy Current Truth / 不重新生成 Positioning Candidates / Resume 幂等。

### Spike-06：Duplicate Review Submit

成功标准：只创建一个 Approved Strategy Version / 两次调用返回相同业务结果 / 下游 Workflow 只恢复一次 / 不创建重复 Audit Success Record。

### Spike-07：Stale Review Package

成功标准：提交被拒绝 / Review Package 标记 `superseded` / Approved Strategy 不创建 / 旧 Checkpoint 不继续执行 / 系统从最早受影响 Stage 重新规划。

### Spike-08：Stale Checkpoint

成功标准：Resume 被拒绝 / Checkpoint 标记为 stale / 不覆盖 Fact v2 / 返回明确 Rerun 或 Recovery 决策 / 不允许 Checkpointer 覆盖 Business Repository。

### Spike-09：Retrieval Degraded Mode

成功标准：启用 Direct Read 和 Lexical Retrieval Fallback / Retrieval Run 记录 Fallback / Evidence Package 记录限制 / Mock Insight Skill 标记 `succeeded_with_limitations` / Evidence Limitation 对用户和下游可见 / 不扩大 Source Scope。

### Spike-10：Cancellation

成功标准：不再调度新 Node / 当前事务完成或回滚 / 不留下部分业务版本 / Workflow Run 标记 `cancelled` / 已提交历史版本保留 / Cancellation Record 可审计。

### Spike-11：Retry Budget Exhaustion

成功标准：达到 Retry Budget 后停止 / 不无限循环 / 创建 Runtime Error / 创建 Recovery Case / 记录 Last Safe Checkpoint / 提供允许的人工恢复动作 / Recovery 不绕过 Validator。

### Spike-12：Downstream Invalidation（可选）

成功标准：Facts / Insights / Approved Strategy 保持有效 / Mock Platform Brief v1 失效 / 重新执行只从 Adapter Stage 开始。

---

## §8 Fault Injection

Spike 必须使用可控 Fault Injection（而非等待真实故障）。概念配置可包括：

```text
FAIL_NODE_ON_ATTEMPT=1
FAIL_TRANSACTION_AT=evidence_link_commit
SEMANTIC_RETRIEVAL_AVAILABLE=false
FORCE_STALE_CHECKPOINT=true
FORCE_INVALID_STRUCTURED_OUTPUT=true
CANCEL_AFTER_NODE=mock_positioning_generation
```

具体实现形式尚未确认。Fault Injection 必须满足：可重复 / 可自动化 / 可单独执行 / 可清除 / 不污染其他场景 / 能生成稳定预期结果。

---

## §9 必测测试类型（Required Test Types）

- **Unit Tests**：Error Classification / Input Fingerprint / Idempotency Key / Version Validation / Stage Invalidation / Retryability / Schema Validation / Checkpoint Staleness 判定。
- **Integration Tests**：StateGraph 与 Checkpoint Store / Business Repository / Runtime Repository / Transaction Rollback / Interrupt / Resume / Review Submit / Checkpoint Reconciliation。
- **Failure Injection Tests**：Transient Error / Timeout / Structured Output Error / Validation Error / Commit Failure / Cancellation / Stale Review / Stale Checkpoint / Retrieval Fallback / Retry Budget Exhaustion。
- **End-to-end Spike Test**：执行完整 Mock Workflow，生成 Runtime Records / Business Versions / Checkpoints / Trace / Test Report。

---

## §10 必备证据（Required Evidence Artifacts）

Spike 不能只输出「测试成功」，必须产生可审查证据。

- **Test Results**：Scenario ID / 输入 / 故障注入条件 / 预期结果 / 实际结果 / Pass·Fail / 关联日志和 Trace。
- **Runtime Evidence**：展示一条完整链路 `Task → Workflow Run → Skill Run → Node Execution → Execution Attempts`。
- **State and Version Evidence**：Graph State / Domain Versions / Current Truth Pointers / Stage Status / Checkpoint Metadata。
- **Transaction Evidence**：失败前后 Domain Version 数量 / Evidence Link 数量 / Current Truth Pointer / Stage State / Audit Record（证明没有 Partial Write）。
- **Trace Evidence**：展示含 Retry / Fallback / Validator / Transaction / Interrupt / Resume / Checkpoint / Final Commit 的 Trace。
- **Limitations**：使用了哪些 Mock / 未验证哪些生产能力 / 哪些结果不能推广到生产 / 哪些问题需要 RFC。

---

## §11 Spike 文档与 Report

Spike 工作区：`docs/spikes/spike-001-langgraph-runtime-and-recovery/`。

至少创建：`README.md` / `spike-plan.md` / `test-scenarios.md`。执行后逐步产生：`implementation-notes.md` / `test-results.md` / `runtime-evidence.md` / `limitations.md` / `spike-report.md`。**当前归档阶段只创建计划和规格文档，不实现 Spike 代码。**

Spike Report 至少包括：Objective / Scope / Architecture Under Test / Mock Components / Scenarios Executed / Test Results / Failed Scenarios / Unexpected Findings / Architecture Risks / Required RFCs / Recommended Architecture Changes / Known Limitations / Readiness Recommendation。Agent 不得仅凭口头总结宣布 Spike 通过。

---

## §12 Spike Code Disposition

- **Discard**：实验代码不进入正式代码目录，只保留测试证据和结论。
- **Reference**：代码保留在 `spikes/`，只供参考，生产模块不得直接依赖。
- **Promote Selectively**：仅接口清晰 / 测试充分 / 不依赖 Mock / 不依赖临时 Schema / 符合 Architecture Baseline / 经过正式 Review / 有对应 RFC 或 Spec 支持的部分，通过独立 PR 迁入正式代码。

不得将整个 Spike Prototype 直接改名为生产实现。

---

## §13 Architecture Readiness Gate

Spike 完成后必须进入 Architecture Readiness Gate。Gate 回答：当前产品规格、架构模型、Spike 证据和未决技术问题，是否已经足够稳定，可以开始正式 Roadmap、Epic 和 GitHub Issue 拆分？**Spike 通过不自动等于 Architecture READY。**

### Gate Inputs

- **Product and Scope**：MVP 用户 / 核心业务问题 / MVP 范围 / 非目标 / 核心 Workflow 明确。
- **Business Contracts**：四个核心 Skill Contract / Human Review Contract / Xiaohongshu Adapter Contract 已接受；输入输出边界 / Validator 边界 / Strategy Lock 明确。
- **State and Data Architecture**：Domain State 分层 / Runtime State 分层 / Versioning / Current Truth / Source·Fragment·Evidence Link / Stage Invalidation / Transaction Boundary 明确。
- **Runtime Architecture**：StateGraph 主架构 / Checkpoint 与 Business Repository 分离 / Retry 与 Rerun 分离 / Idempotency / Safe Resume / Human Review Resume / Cancellation / Observability 明确。
- **Spike Evidence**：所有必选场景已执行 / 关键可靠性场景通过 / 失败原因已解释 / Spike Report 完成 / 未解决风险有明确处理路径。
- **Open Questions**：阻塞问题已解决或进入明确 RFC / 未决问题有 Owner 和优先级 / Specs 之间无已知冲突 / DEC 之间无未处理冲突 / 无隐藏核心业务决策。

---

## §14 Gate Outcomes（READY / CONDITIONALLY READY / NOT READY）

- **READY**：架构和规格具备进入 Implementation Planning 的条件。READY 后可创建 RFC Register / Architecture Baseline v1 / MVP Roadmap / Epic Map / GitHub Issues / Traceability Matrix / 允许范围内的正式开发。READY 不代表产品已完成，也不代表所有生产技术已选定。
- **CONDITIONALLY READY**：核心架构可行，但仍存在少量明确、有限、可隔离的问题。必须记录未解决事项 / Owner / 阻塞模块 / 允许开始的开发范围 / 禁止开始的开发范围 / 重新评审条件。影响核心 Domain Model、事务边界、权限边界或 Resume 正确性的问题，不得通过 CONDITIONALLY READY 绕过。
- **NOT READY**：Spike 关键场景失败 / 事务无法保证原子性 / Retry 产生重复版本 / Stale Review 可提交 / Stale Checkpoint 可恢复 / Resume 覆盖 Current Truth / Specs 核心冲突 / 无法定义 Issue 可靠验收标准。NOT READY 后返回 Architecture Discussion / Technical Spike / RFC / Decision Revision，处理后重新评审。

---

## §15 Mandatory READY Conditions

- **Business Baseline**：MVP Scope Defined / Core Workflow Defined / Core Skill Contracts Accepted / Human Review Contract Accepted / Platform Adapter Contract Accepted。
- **Architecture Baseline**：State Model Defined / Source and Evidence Model Defined / Version and Invalidation Defined / Runtime Boundary Defined / Integration Boundaries Defined。
- **Spike Reliability**：Interrupt/Resume Pass / Transactional Rollback Pass / Idempotent Submit Pass / Stale Review Rejection Pass / Stale Checkpoint Rejection Pass / Retry Without Duplicate Version Pass / Cancellation Without Partial Write Pass / Trace Correlation Pass。
- **Planning Readiness**：Blocking Open Questions Identified / Required RFC List Produced / Architecture Baseline Drafted / Traceability Structure Defined。

**任一关键可靠性条件失败时，不得标记 READY。**

---

## §16 可保持开放、但必须进入 RFC 的事项

以下 Gate 时可尚未最终确定，但必须进入明确 RFC：Production Database / ORM / Checkpointer Backend / API Framework / Frontend Framework / Logging Provider / Tracing Provider / Vector Database / Embedding Model / Rank Fusion / Deployment Platform。

前提：Spike 已证明至少存在一种可行实现方式，并且未决选型不影响核心架构正确性。

---

## §17 Coding Agent 不得临场决定的事项

在对应模块正式实现前，以下内容必须经过 RFC 或正式技术决策：Domain Schema / Current Truth 写入机制 / Transaction Boundary / Checkpoint Backend / Idempotency Storage / Review Submit Protocol / API Contract / Source Processing Pipeline / Retrieval Backend / Workspace Isolation / Error Contract / Production Observability / Authentication and Authorization Boundary。Coding Agent 不得在单个 Issue 或 PR 中擅自选择这些核心方案。

---

## §18 Readiness Decision Authority

```text
Architecture Agent → 提交 Readiness Recommendation
Product Decision Owner → 明确确认最终状态
```

Architecture Agent 可建议 `RECOMMENDED: READY`，但不能自行将 `Development Status = READY` 写入 Current Truth。**只有用户明确确认后，才能更新 Development Status。**

---

## §19 Readiness Report 与 READY 后产出

Gate 完成后应创建 `docs/readiness/architecture-readiness-report-v1.md`，至少包含：Executive Summary / MVP Scope Status / Decision Coverage / Specification Coverage / Architecture Coverage / Spike Results / Reliability Evidence / Open Risks / Required RFCs / Development Constraints / Readiness Recommendation / User Decision / Final Status。

READY（并经用户确认）后按顺序生成：Architecture Baseline (`docs/architecture/architecture-baseline-v1.md`) / RFC Register (`docs/rfcs/rfc-register.md`) / MVP Roadmap (`docs/roadmap/mvp-development-roadmap.md`) / Epic Map (`docs/roadmap/mvp-epic-map.md`) / GitHub Issues（每个关联 Goal / Relevant Specs / Architecture / RFC / DEC / In Scope / Out of Scope / Acceptance Criteria / Required Tests / Dependencies）/ Traceability Matrix (`docs/traceability/mvp-traceability-matrix.md`，追踪 `Requirement → DEC → Spec → RFC → Epic → Issue → Test`)。

**当前归档阶段不生成上述任何输出。**

---

## §20 Expected RFC Areas（当前不创建）

预计 Spike Report 可能涉及：Repository and Application Architecture / Persistence and Transaction Architecture / LangGraph Runtime and Checkpoint Architecture / API and Human Review Protocol / Source Processing and Retrieval Architecture / LLM Runtime and Structured Output / Observability and Runtime Operations。**当前不正式创建 RFC，也不固定 RFC 数量和编号。**

---

## §21 Spike Completion Criteria

Technical Spike 只有在以下全部完成时才算结束：Spike Plan archived / Minimum Graph implemented / Required scenarios automated / Test results persisted / Runtime records inspectable / Transaction rollback evidence available / Interrupt·Resume evidence available / Stale Review test passed / Stale Checkpoint test passed / Idempotency test passed / Cancellation test passed / Trace correlation verified / Spike Report completed / Required RFC list completed / Readiness Recommendation completed。「代码成功运行一次」不构成 Spike 完成。

---

## §22 Blocking Spike Failures

以下问题属于 Architecture Readiness 阻塞项：Duplicate Domain Version / Partial Business Write / Resume 覆盖 Current Truth / Stale Review 提交成功 / Stale Checkpoint Resume 成功 / Retry 与 Rerun 无法区分 / Review Resume 无法幂等 / Cancellation 留下中间业务状态 / Checkpoint 无法与业务版本对账 / Recovery 绕过 Validator / Trace 无法关联业务 Commit。

---

## §23 Failed Spike Handling

关键场景失败后必须创建 Spike Finding：Failed Scenario / Expected Behavior / Actual Behavior / Root Cause / Implementation Error or Architecture Defect / Candidate Solutions / Affected Decisions / Affected Specifications / RFC Requirement / Recommendation。处理方式可以是修复 Spike 实现 / 调整技术使用方式 / 创建 RFC / 修改 Specification / 提议修订 DEC。已接受 DEC 被实验推翻时，必须提交正式修订提案并由用户重新确认。**Agent 不得静默修改 Accepted Decision。**

---

## Open Questions（尚未确认）

均为概念层开放、留待下一议题 `Technical Spike Execution Brief and Temporary Spike Stack` 与后续 RFC 决定，本 Spec **不**臆测答案：

- Spike 使用的具体语言和版本；
- LangGraph 具体版本；
- Spike 数据库；
- Checkpointer Backend；
- Mock LLM 实现；
- Fault Injection 工具；
- 测试框架；
- Trace Provider；
- 临时 API；
- Spike 代码目录；
- Spike 执行 Agent；
- Spike 执行时间计划；
- CONDITIONALLY READY 的具体允许范围；
- READY Checklist 最终字段；
- RFC 最终数量和编号。

**本 Spec 不实现 Spike 代码、不创建正式业务 Graph、不编写四个核心 Skill 的生产 Prompt、不建立正式数据库 Schema、不选择生产级基础设施、不创建 RFC、不生成 MVP Roadmap / Epic Map / GitHub Issues。**

---

## 下一议题（尚未开始，需用户明确启动）

`Technical Spike Execution Brief and Temporary Spike Stack`：Spike 语言选择 / LangGraph 临时版本策略 / Mock LLM 与真实 LLM 边界 / Spike Business·Runtime·Checkpoint 仓库 / 临时事务实现 / Fault Injection 机制 / 测试框架 / Trace 与日志最小实现 / Spike 代码目录 / Scenario Runner / Spike 执行顺序 / Evidence 输出格式 / Spike Agent 执行权限 / 哪些临时技术选择不构成生产承诺。

在 **Technical Spike Execution Brief and Temporary Spike Stack** 议题确认前：**不**执行 Spike；**不**创建正式业务 Graph；**不**生成 MVP Roadmap；**不**拆分正式开发 Issues；Development Status 保持 `NOT READY`。
