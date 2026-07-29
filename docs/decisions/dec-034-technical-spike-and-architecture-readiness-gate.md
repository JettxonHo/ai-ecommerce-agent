# DEC-034 — Technical Spike Plan and Architecture Readiness Gate

> **Status: Accepted**
> **Date: 2026-07-29**
> **Type: Architecture Governance / Technical Validation / Development Readiness**
> **用户确认：** 对 Technical Spike Plan and Architecture Readiness Gate Proposal 明确回复「确认」，通过 Decision Gate → 形成 DEC-034。
> **来源 Session：** [Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Amends:** DEC-023、DEC-033（在 DEC-023 选定 LangGraph StateGraph、DEC-033 定义 Workflow Runtime 失败恢复 / 重试 / 可观测性契约的基础上，正式定义进入正式开发前必须完成的 LangGraph Technical Spike 与运行架构被视为 Implementation-ready 所需的证据；**不推翻** DEC-023 / DEC-033 既有结论）。
> **Development Status: NOT READY**

---

## 用户确认

用户于 2026-07-29 对 Technical Spike Plan and Architecture Readiness Gate Proposal 明确回复「确认」，通过 Decision Gate。形成 DEC-034。对应 DEC-033 的「下一议题」（Workflow Runtime → Technical Spike Plan and Architecture Readiness Gate）。承接 DEC-011 / 013 / 023 / 024 / 025 / 029 / 032 / 033。

---

## Decision

AI Ecommerce Agent 在进入正式业务开发前，必须先完成最小架构 Technical Spike，并经过 Architecture Readiness Gate。正式流程为：

```text
Accepted Decisions
+
Current Specifications
+
Architecture Documents
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

在用户明确确认 READY 前：

```text
Development Status = NOT READY
```

- Technical Spike 通过不自动意味着进入正式开发。
- Architecture Agent 只能提交 Readiness Recommendation。
- 最终 Development Status 变化必须由用户明确确认。

---

## Technical Spike Purpose

Technical Spike 的目标是验证：已接受的 Workflow、State、Persistence、Human Review、Evidence、Retry、Recovery、Transaction 和 Observability 架构，在最小代码环境中是否真正可运行。

Spike 主要验证架构行为，不验证完整业务输出质量。

Spike 是：

- 非生产实验；
- 最小架构原型；
- 可丢弃代码；
- 风险验证工具；
- RFC 和 Roadmap 的输入。

Spike 不是：

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

## Architecture Risks Under Test

Spike 至少验证以下架构风险：

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

## Minimum Spike Workflow

Spike 使用以下最小 Mock Workflow：

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

Xiaohongshu Adapter 不属于主 Spike 路径的硬要求。可以增加一个可选 Mock Adapter Node，用于验证：

```text
Marketing Brief 修改
→ Platform Mapping 失效
```

但不能因此扩大 Spike 范围。

---

## Mock Business Objects

Spike 可以使用固定 Mock 数据。这些结构只用于验证架构行为，不构成最终 Domain Schema。

### Mock Facts

至少包括：

```text
商品名称：Mock 通勤杯
容量：500 mL
重量：260 g
材料：304 不锈钢
```

### Mock Insights

至少包括：

```text
Evidence-backed Insight:
部分通勤用户担心随身携带水杯时发生漏水。

Hypothesis:
通勤用户可能将轻量视为重要购买因素。
```

### Mock Positioning Candidates

至少包括两个实质不同候选：

```text
Candidate A:
轻量通勤

Candidate B:
密封安心
```

### Mock Approved Strategy

至少包括：

- Target Segment；
- Usage Context；
- Core Need；
- Value Proposition；
- Differentiation；
- Proof Points；
- Accepted Hypotheses；
- Evidence Limitations。

### Mock Marketing Brief

至少包括：

- Audience；
- Core Message；
- Primary Benefit；
- Proof Points；
- Content Angles；
- Prohibited Claims；
- Evidence Limitations。

---

## Spike Graph State

Spike Graph State 必须保持紧凑、引用导向。概念结构：

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

Graph State 不保存：

- 完整 Facts；
- 完整 Insights；
- 完整 Positioning Candidates；
- 完整 Review Draft；
- 完整 Evidence Package；
- 全部历史版本；
- 完整文档或评论内容。

正式业务内容必须从 Business Repository 读取。

---

## Repository Separation

Spike 至少在逻辑上区分三类存储。

### Business Repository

负责保存：

- Task；
- Domain Versions；
- Current Truth Pointers；
- Stage State；
- Review Package；
- Strategy Draft；
- Approved Strategy；
- Marketing Brief；
- Evidence Links；
- Audit Records。

### Runtime Repository

负责保存：

- Workflow Run；
- Skill Run；
- Node Execution；
- Execution Attempt；
- Runtime Error；
- Recovery Case；
- Idempotency Record；
- Cancellation Record。

### Checkpoint Store

负责保存：

- LangGraph 执行状态；
- Interrupt；
- Resume 位置；
- 临时运行上下文；
- Checkpoint Metadata。

即使 Spike 使用同一个物理存储，也必须保持逻辑边界。正式规则：

```text
LangGraph Checkpoint Store
≠
Business Current Truth Repository
```

---

## Required Spike Scenarios

以下场景属于 Architecture Readiness 的必选验证场景。

### Spike-01：Normal Workflow

流程：

```text
Start
→ Facts
→ Insights
→ Positioning
→ Review Interrupt
→ Review Submit
→ Approved Strategy
→ Marketing Brief
→ Complete
```

成功标准：

- 每个 Stage 只正式提交一次；
- Current Truth Pointer 正确；
- Graph 在 Review 前正确暂停；
- Resume 创建新的 Workflow Run；
- Resume 后不重新执行已完成 Positioning；
- Trace 能关联完整执行链。

### Spike-02：Transient Failure and Retry

模拟某个 Node：

```text
Attempt 1 → Transient Error
Attempt 2 → Success
```

成功标准：

- Skill Run ID 不变；
- Node Execution ID 不变；
- Attempt ID 不同；
- 只创建一个业务版本；
- Retry 与 Rerun 可以明确区分；
- Retry Record 和 Trace 完整。

### Spike-03：Invalid Structured Output

模拟：

- 非法 JSON；
- 缺少必填字段；
- 非法 Enum；
- 不存在的 Fact ID 或 Fragment ID。

成功标准：

- Schema Validation 生效；
- 允许有限 Deterministic Normalization；
- 允许有限 Constrained Repair；
- 超过上限后 Skill Run 失败；
- 不创建业务版本；
- 不更新 Current Truth；
- 不创建 Formal Evidence Link。

### Spike-04：Transactional Rollback

模拟事务中间失败：

```text
Domain Version 创建成功
↓
Evidence Link 写入失败
```

成功标准：

- Domain Version 回滚；
- Evidence Link 回滚；
- Current Truth Pointer 不变；
- Stage State 不变；
- Audit 不错误记录为成功；
- Retry 后只创建一个正式版本。

### Spike-05：Human Review Interrupt and Resume

成功标准：

- Review Package 成功创建；
- Graph 正确 Interrupt；
- Task Status 为 `waiting_for_review`；
- Review Submit 事务创建 Approved Strategy；
- Resume 后读取 Approved Strategy Current Truth；
- 不重新生成 Positioning Candidates；
- Resume 操作幂等。

### Spike-06：Duplicate Review Submit

使用相同：

```text
review_id
package_version
draft_version
idempotency_key
```

提交两次。

成功标准：

- 只创建一个 Approved Strategy Version；
- 两次调用返回相同业务结果；
- 下游 Workflow 只恢复一次；
- 不创建重复 Audit Success Record。

### Spike-07：Stale Review Package

流程：

```text
Review Package 基于 Facts v1
↓
审核过程中 Current Facts 变为 v2
↓
用户提交旧 Review Package
```

成功标准：

- 提交被拒绝；
- Review Package 标记为 `superseded`；
- Approved Strategy 不创建；
- 旧 Checkpoint 不继续执行；
- 系统从最早受影响 Stage 重新规划。

### Spike-08：Stale Checkpoint

Checkpoint 保存时：

```text
fact_version_id = fact-v1
```

Resume 时 Current Truth 已经是：

```text
fact_version_id = fact-v2
```

成功标准：

- Resume 被拒绝；
- Checkpoint 标记为 stale；
- 不覆盖 Fact v2；
- 返回明确 Rerun 或 Recovery 决策；
- 不允许 Checkpointer 覆盖 Business Repository。

### Spike-09：Retrieval Degraded Mode

模拟 Semantic Retrieval 不可用。

成功标准：

- 启用 Direct Read 和 Lexical Retrieval Fallback；
- Retrieval Run 记录 Fallback；
- Evidence Package 记录限制；
- Mock Insight Skill 标记 `succeeded_with_limitations`；
- Evidence Limitation 对用户和下游可见；
- 不扩大 Source Scope。

### Spike-10：Cancellation

在长运行 Node 中请求取消。

成功标准：

- 不再调度新 Node；
- 当前事务完成或回滚；
- 不留下部分业务版本；
- Workflow Run 标记 `cancelled`；
- 已提交历史版本保留；
- Cancellation Record 可审计。

### Spike-11：Retry Budget Exhaustion

让某个 Node 持续失败。

成功标准：

- 达到 Retry Budget 后停止；
- 不无限循环；
- 创建 Runtime Error；
- 创建 Recovery Case；
- 记录 Last Safe Checkpoint；
- 提供允许的人工恢复动作；
- Recovery 不绕过 Validator。

### Spike-12：Downstream Invalidation（可选）

可选验证：

```text
Marketing Brief v1
→ Mock Platform Brief v1
→ 用户修改 Marketing Brief，形成 v2
```

成功标准：

- Facts 保持有效；
- Insights 保持有效；
- Approved Strategy 保持有效；
- Mock Platform Brief v1 失效；
- 重新执行只从 Adapter Stage 开始。

---

## Fault Injection

Spike 必须使用可控 Fault Injection，而不是等待真实故障偶然发生。概念配置可以包括：

```text
FAIL_NODE_ON_ATTEMPT=1
FAIL_TRANSACTION_AT=evidence_link_commit
SEMANTIC_RETRIEVAL_AVAILABLE=false
FORCE_STALE_CHECKPOINT=true
FORCE_INVALID_STRUCTURED_OUTPUT=true
CANCEL_AFTER_NODE=mock_positioning_generation
```

具体实现形式尚未确认。Fault Injection 必须满足：

- 可重复；
- 可自动化；
- 可单独执行；
- 可清除；
- 不污染其他场景；
- 能生成稳定预期结果。

---

## Required Test Types

### Unit Tests

至少覆盖：

- Error Classification；
- Input Fingerprint；
- Idempotency Key；
- Version Validation；
- Stage Invalidation；
- Retryability；
- Schema Validation；
- Checkpoint Staleness 判定。

### Integration Tests

至少覆盖：

- StateGraph 与 Checkpoint Store；
- Business Repository；
- Runtime Repository；
- Transaction Rollback；
- Interrupt / Resume；
- Review Submit；
- Checkpoint Reconciliation。

### Failure Injection Tests

至少覆盖：

- Transient Error；
- Timeout；
- Structured Output Error；
- Validation Error；
- Commit Failure；
- Cancellation；
- Stale Review；
- Stale Checkpoint；
- Retrieval Fallback；
- Retry Budget Exhaustion。

### End-to-end Spike Test

必须执行完整 Mock Workflow，并生成：

- Runtime Records；
- Business Versions；
- Checkpoints；
- Trace；
- Test Report。

---

## Required Evidence Artifacts

Spike 不能只输出「测试成功」，必须产生可审查证据。

### Test Results

至少记录：

- Scenario ID；
- 输入；
- 故障注入条件；
- 预期结果；
- 实际结果；
- Pass / Fail；
- 关联日志和 Trace。

### Runtime Evidence

至少展示一条完整链路：

```text
Task
→ Workflow Run
→ Skill Run
→ Node Execution
→ Execution Attempts
```

### State and Version Evidence

展示：

- Graph State；
- Domain Versions；
- Current Truth Pointers；
- Stage Status；
- Checkpoint Metadata。

### Transaction Evidence

展示失败前后：

- Domain Version 数量；
- Evidence Link 数量；
- Current Truth Pointer；
- Stage State；
- Audit Record。

用于证明没有 Partial Write。

### Trace Evidence

至少展示一个包含以下内容的 Trace：

- Retry；
- Fallback；
- Validator；
- Transaction；
- Interrupt；
- Resume；
- Checkpoint；
- Final Commit。

### Limitations

明确记录：

- 使用了哪些 Mock；
- 未验证哪些生产能力；
- 哪些结果不能推广到生产环境；
- 哪些问题需要 RFC。

---

## Spike Documentation

创建 Spike 工作区：

```text
docs/spikes/spike-001-langgraph-runtime-and-recovery/
```

至少创建：

```text
README.md
spike-plan.md
test-scenarios.md
```

Spike 执行后再逐步产生：

```text
implementation-notes.md
test-results.md
runtime-evidence.md
limitations.md
spike-report.md
```

**当前归档阶段只创建计划和规格文档，不实现 Spike 代码。**

---

## Spike Report

Spike Report 至少包括：

```text
Objective
Scope
Architecture Under Test
Mock Components
Scenarios Executed
Test Results
Failed Scenarios
Unexpected Findings
Architecture Risks
Required RFCs
Recommended Architecture Changes
Known Limitations
Readiness Recommendation
```

Agent 不得仅凭口头总结宣布 Spike 通过。

---

## Spike Code Disposition

Spike 代码有三种处理方式。

### Discard

实验代码不进入正式代码目录，只保留测试证据和结论。

### Reference

代码保留在 `spikes/`，只供参考，生产模块不得直接依赖。

### Promote Selectively

只有符合以下条件的部分才允许通过独立 PR 迁入正式代码：

- 接口清晰；
- 测试充分；
- 不依赖 Mock；
- 不依赖临时 Schema；
- 符合 Architecture Baseline；
- 经过正式 Review；
- 有对应 RFC 或 Spec 支持。

不得将整个 Spike Prototype 直接改名为生产实现。

---

## Architecture Readiness Gate

Spike 完成后必须进入 Architecture Readiness Gate。Gate 回答：当前产品规格、架构模型、Spike 证据和未决技术问题，是否已经足够稳定，可以开始正式 Roadmap、Epic 和 GitHub Issue 拆分？

**Spike 通过不自动等于 Architecture READY。**

### Readiness Gate Inputs

#### Product and Scope

检查：

- MVP 用户明确；
- 核心业务问题明确；
- MVP 范围明确；
- 非目标明确；
- 核心 Workflow 明确。

#### Business Contracts

检查：

- 四个核心 Skill Contract 已接受；
- Human Review Contract 已接受；
- Xiaohongshu Adapter Contract 已接受；
- 各组件输入输出边界明确；
- Validator 边界明确；
- Strategy Lock 明确。

#### State and Data Architecture

检查：

- Domain State 分层明确；
- Runtime State 分层明确；
- Versioning 明确；
- Current Truth 明确；
- Source、Fragment 和 Evidence Link 明确；
- Stage Invalidation 明确；
- Transaction Boundary 明确。

#### Runtime Architecture

检查：

- StateGraph 主架构明确；
- Checkpoint 和 Business Repository 分离；
- Retry 与 Rerun 分离；
- Idempotency 明确；
- Safe Resume 明确；
- Human Review Resume 明确；
- Cancellation 明确；
- Observability 明确。

#### Spike Evidence

检查：

- 所有必选场景已经执行；
- 关键可靠性场景通过；
- 失败原因已经解释；
- Spike Report 完成；
- 未解决风险有明确处理路径。

#### Open Questions

检查：

- 阻塞问题已解决或进入明确 RFC；
- 未决问题有 Owner 和优先级；
- Specs 之间没有已知冲突；
- DEC 之间没有未处理冲突；
- 没有隐藏的核心业务决策。

---

## Readiness Gate Outcomes

Gate 支持三种正式结果。

### READY

表示：架构和规格已经具备进入 Implementation Planning 的条件。

READY 后可以：

- 创建正式 RFC Register；
- 完成 Architecture Baseline v1；
- 生成 MVP Roadmap；
- 生成 Epic Map；
- 拆分 GitHub Issues；
- 建立 Traceability Matrix；
- 启动允许范围内的正式开发。

READY 不代表产品已完成，也不代表所有生产技术已经选定。

### CONDITIONALLY READY

表示：核心架构可行，但仍存在少量明确、有限、可隔离的问题。

必须记录：

- 未解决事项；
- Owner；
- 阻塞模块；
- 允许开始的开发范围；
- 禁止开始的开发范围；
- 重新评审条件。

影响核心 Domain Model、事务边界、权限边界或 Resume 正确性的问题，不得通过 CONDITIONALLY READY 绕过。

### NOT READY

适用于：

- Spike 关键场景失败；
- 事务无法保证原子性；
- Retry 会产生重复版本；
- Stale Review 可以提交；
- Stale Checkpoint 可以恢复；
- Resume 会覆盖 Current Truth；
- Specs 存在核心冲突；
- 无法定义 Issue 的可靠验收标准。

NOT READY 后应返回：

```text
Architecture Discussion
Technical Spike
RFC
或
Decision Revision
```

处理后重新评审。

---

## Mandatory READY Conditions

以下条件必须全部满足。

### Business Baseline

```text
MVP Scope Defined
Core Workflow Defined
Core Skill Contracts Accepted
Human Review Contract Accepted
Platform Adapter Contract Accepted
```

### Architecture Baseline

```text
State Model Defined
Source and Evidence Model Defined
Version and Invalidation Defined
Runtime Boundary Defined
Integration Boundaries Defined
```

### Spike Reliability

```text
Interrupt / Resume Pass
Transactional Rollback Pass
Idempotent Submit Pass
Stale Review Rejection Pass
Stale Checkpoint Rejection Pass
Retry Without Duplicate Version Pass
Cancellation Without Partial Write Pass
Trace Correlation Pass
```

### Planning Readiness

```text
Blocking Open Questions Identified
Required RFC List Produced
Architecture Baseline Drafted
Traceability Structure Defined
```

**任一关键可靠性条件失败时，不得标记 READY。**

---

## Matters Allowed to Remain Open

Gate 时以下内容可以尚未最终确定，但必须进入明确 RFC：

- Production Database；
- ORM；
- Checkpointer Backend；
- API Framework；
- Frontend Framework；
- Logging Provider；
- Tracing Provider；
- Vector Database；
- Embedding Model；
- Rank Fusion；
- Deployment Platform。

前提是：Spike 已证明至少存在一种可行实现方式，并且未决选型不影响核心架构正确性。

---

## Matters Coding Agents Must Not Decide Ad Hoc

在对应模块正式实现前，以下内容必须经过 RFC 或正式技术决策：

- Domain Schema；
- Current Truth 写入机制；
- Transaction Boundary；
- Checkpoint Backend；
- Idempotency Storage；
- Review Submit Protocol；
- API Contract；
- Source Processing Pipeline；
- Retrieval Backend；
- Workspace Isolation；
- Error Contract；
- Production Observability；
- Authentication and Authorization Boundary。

Coding Agent 不得在单个 Issue 或 PR 中擅自选择这些核心方案。

---

## Readiness Decision Authority

正式流程：

```text
Architecture Agent
→ 提交 Readiness Recommendation

Product Decision Owner
→ 明确确认最终状态
```

Architecture Agent 可以建议：

```text
RECOMMENDED: READY
```

但不能自行将：

```text
Development Status = READY
```

写入 Current Truth。**只有用户明确确认后，才能更新 Development Status。**

---

## Readiness Report

Gate 完成后应创建：

```text
docs/readiness/architecture-readiness-report-v1.md
```

至少包含：

```text
Executive Summary
MVP Scope Status
Decision Coverage
Specification Coverage
Architecture Coverage
Spike Results
Reliability Evidence
Open Risks
Required RFCs
Development Constraints
Readiness Recommendation
User Decision
Final Status
```

---

## Outputs After READY

Gate 通过并得到用户确认后，按顺序生成。

### Architecture Baseline

```text
docs/architecture/architecture-baseline-v1.md
```

### RFC Register

```text
docs/rfcs/rfc-register.md
```

### MVP Roadmap

```text
docs/roadmap/mvp-development-roadmap.md
```

### Epic Map

```text
docs/roadmap/mvp-epic-map.md
```

### GitHub Issues

每个 Issue 必须关联：

- Goal；
- Relevant Specs；
- Architecture；
- RFC；
- DEC；
- In Scope；
- Out of Scope；
- Acceptance Criteria；
- Required Tests；
- Dependencies。

### Traceability Matrix

```text
docs/traceability/mvp-traceability-matrix.md
```

正式追踪：

```text
Requirement
→ DEC
→ Spec
→ RFC
→ Epic
→ Issue
→ Test
```

**当前归档阶段不生成上述任何输出。**

---

## Expected RFC Areas After Spike

Spike Report 应根据实际发现生成 Required RFC List。预计可能涉及：

```text
Repository and Application Architecture
Persistence and Transaction Architecture
LangGraph Runtime and Checkpoint Architecture
API and Human Review Protocol
Source Processing and Retrieval Architecture
LLM Runtime and Structured Output
Observability and Runtime Operations
```

**当前不正式创建 RFC，也不固定 RFC 数量和编号。**

---

## Spike Completion Criteria

Technical Spike 只有在以下内容全部完成时才算结束：

```text
Spike Plan archived
Minimum Graph implemented
Required scenarios automated
Test results persisted
Runtime records inspectable
Transaction rollback evidence available
Interrupt / Resume evidence available
Stale Review test passed
Stale Checkpoint test passed
Idempotency test passed
Cancellation test passed
Trace correlation verified
Spike Report completed
Required RFC list completed
Readiness Recommendation completed
```

「代码成功运行一次」不构成 Spike 完成。

---

## Blocking Spike Failures

以下问题属于 Architecture Readiness 阻塞项：

- Duplicate Domain Version；
- Partial Business Write；
- Resume 覆盖 Current Truth；
- Stale Review 提交成功；
- Stale Checkpoint Resume 成功；
- Retry 与 Rerun 无法区分；
- Review Resume 无法幂等；
- Cancellation 留下中间业务状态；
- Checkpoint 无法与业务版本对账；
- Recovery 绕过 Validator；
- Trace 无法关联业务 Commit。

---

## Failed Spike Handling

关键场景失败后必须创建 Spike Finding，至少包括：

```text
Failed Scenario
Expected Behavior
Actual Behavior
Root Cause
Implementation Error or Architecture Defect
Candidate Solutions
Affected Decisions
Affected Specifications
RFC Requirement
Recommendation
```

处理方式可以是：

- 修复 Spike 实现；
- 调整技术使用方式；
- 创建 RFC；
- 修改 Specification；
- 提议修订 DEC。

已接受 DEC 被实验推翻时，必须提交正式修订提案并由用户重新确认。**Agent 不得静默修改 Accepted Decision。**

---

## Contract Summary

```text
Component:
Technical Spike Plan and Architecture Readiness Gate

Spike Purpose:
Validate high-risk architecture behavior before production development

Minimum Workflow:
Facts
→ Insights
→ Positioning
→ Human Review Interrupt
→ Approved Strategy
→ Marketing Brief

Required Validation:
- StateGraph execution
- Checkpoint persistence
- Interrupt and Resume
- Transaction rollback
- Idempotent commit
- Bounded retry
- Stale Review rejection
- Stale Checkpoint rejection
- Retrieval fallback
- Cancellation
- Trace correlation

Gate Results:
- READY
- CONDITIONALLY READY
- NOT READY

Hard Rule:
Development Status can become READY only after Spike evidence,
Readiness Review and explicit user acceptance.
```

---

## Reason

当前项目已经形成大量业务与架构决策，但这些文档只能证明设计在逻辑上相对完整，不能证明：

- LangGraph Interrupt 和 Resume 真正可靠；
- Checkpoint 能与业务版本正确对账；
- Retry 不会产生重复业务版本；
- 事务失败不会产生 Partial Write；
- Review Submit 和 Resume 能够幂等；
- Cancellation 不会破坏业务状态；
- Runtime Trace 能关联完整执行链。

直接开始正式业务开发，会将架构风险、业务复杂度和 Prompt 质量问题混合在一起。因此正式开发前必须先用最小 Mock Workflow 验证高风险架构行为，并以测试结果、运行记录、事务证据和 Trace 作为 Readiness Gate 输入。

---

## Impact

该决定将影响：

- Session-002 结束条件；
- LangGraph Technical Spike；
- Spike 目录；
- Fault Injection；
- Runtime Tests；
- Spike Report；
- Readiness Report；
- Development Status；
- RFC Register；
- Architecture Baseline；
- MVP Roadmap；
- Epic Map；
- GitHub Issues；
- Traceability Matrix；
- Coding Agent 启动条件。

---

## Decision Boundary

本决定已经确认：

- Spike 是非生产架构实验；
- Spike 不等于 MVP；
- Spike 验证架构行为而非业务质量；
- 最小 Mock Workflow；
- Mock Business Objects；
- Compact Graph State；
- Business、Runtime 和 Checkpoint Repository 分离；
- 必选 Spike Scenarios；
- Fault Injection；
- Unit、Integration、Failure Injection 和 End-to-end Tests；
- Required Evidence Artifacts；
- Spike Report；
- Spike Code Disposition；
- Architecture Readiness Gate；
- READY、CONDITIONALLY READY 和 NOT READY；
- Mandatory READY Conditions；
- Blocking Spike Failures；
- Readiness Decision Authority；
- Explicit User Acceptance；
- READY 后的文档输出；
- Coding Agent 不得临场决定核心技术方案；
- Failed Spike Handling；
- 当前继续保持 NOT READY。

本决定尚未确认：

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

---

## Related Session

- [Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)：Agent 工作流、可靠性架构与技术能力需求

---

## Related Decisions

- DEC-011：Deterministic Workflow Control；
- DEC-013：Task-level Persistence；
- DEC-023：LangGraph StateGraph；
- DEC-024：Versioned Domain State；
- DEC-025：Source and Evidence Architecture；
- DEC-029：Human Review and Approved Strategy；
- DEC-032：Hybrid Retrieval and Evidence Runtime；
- DEC-033：Workflow Runtime Failure Recovery, Retry and Observability。

---

## Related RFC

None。

---

## Supersedes

None。

---

## Amends

**Amends DEC-023、DEC-033。**

- 对 DEC-023：正式定义进入正式开发前必须完成的 LangGraph Technical Spike（验证 StateGraph Compile / Invoke、Checkpoint 持久化、Interrupt / Resume 等高风险行为），**不推翻** DEC-023 选定 LangGraph StateGraph 的结论。
- 对 DEC-033：正式定义 Workflow Runtime 失败恢复 / 重试 / 可观测性架构被视为 Implementation-ready 所需的 Spike 证据与 Readiness Gate，**不推翻** DEC-033 的运行架构契约。
- DEC-023 / DEC-033 行作为历史记录不修改，本 Amends 关系仅在此处及 decision-log DEC-034 行记录。

---

## Notes

DEC-034 确认了正式开发前的最小架构 Technical Spike 与基于证据和用户确认的 Architecture Readiness Gate。它**不**实现 Spike 代码、**不**创建正式业务 Graph、**不**编写四个核心 Skill 的生产 Prompt、**不**建立正式数据库 Schema、**不**选择生产级基础设施、**不**创建 RFC、**不**生成 MVP Roadmap / Epic Map / GitHub Issues。

下一议题（尚未开始，需用户明确启动）：`Technical Spike Execution Brief and Temporary Spike Stack`（Spike 语言选择 / LangGraph 临时版本策略 / Mock LLM 与真实 LLM 边界 / Spike Business·Runtime·Checkpoint 仓库 / 临时事务实现 / Fault Injection 机制 / 测试框架 / Trace 与日志最小实现 / Spike 代码目录 / Scenario Runner / Spike 执行顺序 / Evidence 输出格式 / Spike Agent 执行权限 / 哪些临时技术选择不构成生产承诺）。

在 **Technical Spike Execution Brief and Temporary Spike Stack** 议题确认前：**不**执行 Spike；**不**创建正式业务 Graph；**不**生成 MVP Roadmap；**不**拆分正式开发 Issues；Development Status 保持 `NOT READY`。
