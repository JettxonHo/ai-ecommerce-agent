# Architecture Readiness

> **来源决定：** [DEC-034 — Technical Spike Plan and Architecture Readiness Gate](../decisions/dec-034-technical-spike-and-architecture-readiness-gate.md) · [DEC-035 — Technical Spike 临时技术栈与执行契约](../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md) · [DEC-036 — Spike-001 Execution Authorization and Agent Handoff Contract](../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md) · [DEC-037 — Formal Spike-001 Execution Authorization](../decisions/dec-037-formal-spike-001-execution-authorization.md)
> **概念规格：** [../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../specs/readiness/technical-spike-and-architecture-readiness-gate.md) · [../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md) · [../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md](../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md) · [../specs/readiness/formal-spike-001-execution-authorization.md](../specs/readiness/formal-spike-001-execution-authorization.md)
> **当前 Contract Authorization Status: ACCEPTED · Spike Execution Authorization Status: GRANTED · Spike Execution Status: NOT STARTED · Architecture Readiness Status: NOT READY · Development Status: NOT READY**

---

## 本目录是什么

本目录是 **Architecture Readiness Gate** 的入口与（未来）Readiness Report 的归宿。它由 DEC-034 治理。Gate 回答一个问题：

> 当前产品规格、架构模型、Spike 证据和未决技术问题，是否已经足够稳定，可以开始正式 Roadmap、Epic 和 GitHub Issue 拆分？

**Spike 通过不自动等于 Architecture READY。** Development Status 变为 READY 需要 Spike 证据 + Readiness Review + 用户明确确认三者同时满足。

## Gate 的三种正式结果

| 结果 | 含义 |
|---|---|
| **READY** | 架构和规格具备进入 Implementation Planning 的条件。READY 后可创建 RFC Register / Architecture Baseline v1 / MVP Roadmap / Epic Map / GitHub Issues / Traceability Matrix / 允许范围内的正式开发。READY 不代表产品已完成，也不代表所有生产技术已选定。 |
| **CONDITIONALLY READY** | 核心架构可行，但仍存在少量明确、有限、可隔离的问题。必须记录未解决事项 / Owner / 阻塞模块 / 允许开始的开发范围 / 禁止开始的开发范围 / 重新评审条件。影响核心 Domain Model、事务边界、权限边界或 Resume 正确性的问题，不得通过 CONDITIONALLY READY 绕过。 |
| **NOT READY** | Spike 关键场景失败 / 事务无法保证原子性 / Retry 产生重复版本 / Stale Review 可提交 / Stale Checkpoint 可恢复 / Resume 覆盖 Current Truth / Specs 核心冲突 / 无法定义 Issue 可靠验收标准。NOT READY 后返回 Architecture Discussion / Technical Spike / RFC / Decision Revision，处理后重新评审。 |

## 决策权限（Readiness Decision Authority）

```text
Architecture Agent → 提交 Readiness Recommendation
Product Decision Owner（用户）→ 明确确认最终状态
```

Architecture Agent 可以建议 `RECOMMENDED: READY`，但**不能**自行将 `Development Status = READY` 写入 Current Truth。**只有用户明确确认后，才能更新 Development Status。**

## Readiness Report 要求

Gate 完成后应创建本目录下 `architecture-readiness-report-v1.md`，至少包含：

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

> **当前状态：** 该报告尚未创建。Gate 尚未进入——Technical Spike 尚未执行。Spike-001 的**临时技术栈与执行契约已由 DEC-035 确认**（Python 3.13 + LangGraph 1.2.9 + 同步 StateGraph + 三类分离 SQLite + SqliteSaver + sqlite3 事务 + Scripted Model + Mock Retrieval + Scenario Fault Injection + pytest + Local JSONL Trace + CLI Runner；临时选择不构成生产承诺）；**执行授权契约已由 DEC-036 确认**（Claude 主执行 / Codex 可选 Reviewer / Repository Audit / Dedicated Branch / Stage Commits / Issue·PR / Mandatory Stop Conditions / Final Human Gate；`Contract Authorization = ACCEPTED`）；**正式执行授权已由 DEC-037 授予**（`Execution Authorization = GRANTED`：Claude 已被允许执行 Spike-001 S0—S6，但第一动作仍是只读 Repository Audit，且在 Audit 与稳定文档基线通过前不得写入、安装或创建 Spike 代码 / Branch / PR）。但 **Spike Execution Status = NOT STARTED**（须待 Claude 实际开始 Repository Audit 后才可更新为 `IN PROGRESS`）/ **Architecture Readiness Status = NOT READY** / **Development Status = NOT READY**。下一动作为 `Spike-001 Execution Handoff`（归档进入稳定 Git 基线后以独立任务执行；第一步必须是只读 Repository Audit）。

## 必备 READY 条件（摘要）

- **Business Baseline**：MVP Scope / Core Workflow / Core Skill Contracts / Human Review Contract / Platform Adapter Contract。
- **Architecture Baseline**：State Model / Source and Evidence Model / Version and Invalidation / Runtime Boundary / Integration Boundaries。
- **Spike Reliability**：Interrupt·Resume / Transactional Rollback / Idempotent Submit / Stale Review Rejection / Stale Checkpoint Rejection / Retry Without Duplicate Version / Cancellation Without Partial Write / Trace Correlation（**任一失败不得标记 READY**）。
- **Planning Readiness**：Blocking Open Questions Identified / Required RFC List Produced / Architecture Baseline Drafted / Traceability Structure Defined。

详见 DEC-034 与概念规格。

## 当前 Development Status

```text
NOT READY
```

- **Contract Authorization Status: ACCEPTED**（DEC-036 已接受 Spike-001 权限与执行契约）
- **Spike Execution Authorization Status: GRANTED**（DEC-037 已正式授予 Claude 执行 Spike-001 S0—S6 的授权；但 `GRANTED` 不表示 Spike 已开始或已通过，第一动作仍是只读 Repository Audit）
- **Spike Execution Status: NOT STARTED**（临时栈由 DEC-035 确认、执行契约由 DEC-036 确认、执行授权由 DEC-037 授予，但 Spike 尚未开始；须待 Claude 实际开始 Repository Audit 后才可更新为 `IN PROGRESS`）
- **Architecture Readiness Status: NOT READY**
- **Development Status: NOT READY**（未经 Spike 证据 + Readiness Review + 用户明确确认）

在归档完成并进入稳定 Git 基线、且以独立任务 `Spike-001 Execution Handoff` 正式启动前：**不**启动 Spike；**不**安装依赖；**不**创建 Spike Branch / Issue / PR / 代码；**不**运行测试；**不**创建正式 Roadmap；Development Status 保持 `NOT READY`。`Spike-001 Execution Handoff` 的第一步必须是只读 Repository Audit。
