# Architecture Readiness

> **Current sync（2026-08-07）：** Architecture / Development = `CONDITIONALLY READY`（仅策划）。Product Specification、RFC-001～006、Frontend Architecture 与 FND-001～003 已完成；RFC-005 Final Review = PASS。用户已确认快速 MVP-0 Gate：完整 ARP-02 / 03 / 09、ARP-05～08 与 TS-02 / 04 / 05 不再阻塞 MVP-0；TS-01 / TS-03 收敛为对应 Foundation Issue 内 stop-first compatibility slice。当前只授权最小 RFC-007、Development Plan、Testing Strategy、Goal 文本与精简 Readiness Review；完整展示前不执行 Spike、Live Provider、业务实现或实际 Goal。当前 Gate 见 [Implementation Readiness](../handoffs/implementation-readiness.md)。
> **Historical record note：** 下方 DEC-034～037、Spike-001 和最初 Readiness Gate 的执行顺序保留历史原貌；其中 `GRANTED`、`下一议题` 等只描述当时的 Spike 授权，不得用于重新执行 Spike 或启动当前 Goal。

> **来源决定：** [DEC-034 — Technical Spike Plan and Architecture Readiness Gate](../decisions/dec-034-technical-spike-and-architecture-readiness-gate.md) · [DEC-035 — Technical Spike 临时技术栈与执行契约](../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md) · [DEC-036 — Spike-001 Execution Authorization and Agent Handoff Contract](../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md) · [DEC-037 — Formal Spike-001 Execution Authorization](../decisions/dec-037-formal-spike-001-execution-authorization.md)
> **概念规格：** [../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../specs/readiness/technical-spike-and-architecture-readiness-gate.md) · [../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md) · [../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md](../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md) · [../specs/readiness/formal-spike-001-execution-authorization.md](../specs/readiness/formal-spike-001-execution-authorization.md)
> **当前 Contract Authorization Status: ACCEPTED · Spike Execution Authorization Status: GRANTED · Spike Execution Status: COMPLETED · Architecture Readiness Status: CONDITIONALLY READY · Development Status: CONDITIONALLY READY**

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

### Historical PR #4 Closure Snapshot

> 下方引文中的“当前状态”和“下一议题”只表示 PR #4 完成时的状态，不是 2026-08-06 当前执行指令。

> **当前状态：** Spike-001 已**执行完成**（S0—S6 全部完成，Gate A—E 通过，25 个自动化测试全部通过），Spike PR #2 已 **MERGED**（merge commit `a60ff3b`）、Spike Issue #1 已 **CLOSED**。Readiness Review 交付物**已创建并经用户决策**：`architecture-readiness-report-v1.md`（本目录）+ [`../architecture/architecture-baseline-v1.md`](../architecture/architecture-baseline-v1.md) + [`../rfcs/rfc-register.md`](../rfcs/rfc-register.md) + [`../traceability/mvp-traceability-matrix.md`](../traceability/mvp-traceability-matrix.md)，经 [Readiness Issue #3](https://github.com/JettxonHo/ai-ecommerce-agent/issues/3) 与 [Readiness PR #4](https://github.com/JettxonHo/ai-ecommerce-agent/pull/4) 提交并已由用户审查。**用户最终决定：Architecture Readiness Decision = CONDITIONALLY READY**（User Decision 已记录于报告 §16）。当前 **Spike Execution Status = COMPLETED** / **Architecture Readiness Status = CONDITIONALLY READY** / **Development Status = CONDITIONALLY READY**（**仅限授权的规划与治理范围**：Architecture RFC / Implementation Planning / MVP Roadmap 草案 / Epic and Dependency Planning / Technical Risk Resolution；**不授权**任何生产实现与正式业务 Coding Issues）。下一议题为 **RFC Planning and Dependency Order**（RFC-001…RFC-007 按依赖顺序逐个提交用户评审；未替用户接受任何 RFC）。

## 必备 READY 条件（摘要）

- **Business Baseline**：MVP Scope / Core Workflow / Core Skill Contracts / Human Review Contract / Platform Adapter Contract。
- **Architecture Baseline**：State Model / Source and Evidence Model / Version and Invalidation / Runtime Boundary / Integration Boundaries。
- **Spike Reliability**：Interrupt·Resume / Transactional Rollback / Idempotent Submit / Stale Review Rejection / Stale Checkpoint Rejection / Retry Without Duplicate Version / Cancellation Without Partial Write / Trace Correlation（**任一失败不得标记 READY**）。
- **Planning Readiness**：Blocking Open Questions Identified / Required RFC List Produced / Architecture Baseline Drafted / Traceability Structure Defined。

详见 DEC-034 与概念规格。

## 当前 Development Status

```text
CONDITIONALLY READY
```

- **Contract Authorization Status: ACCEPTED**（DEC-036 已接受 Spike-001 权限与执行契约）
- **Spike Execution Authorization Status: GRANTED**（DEC-037 已正式授予 Claude 执行 Spike-001 S0—S6 的授权）
- **Spike Execution Status: COMPLETED**（Claude 已完成只读 Repository Audit、稳定文档基线、Spike Issue、Dedicated Branch、S0—S6 全部阶段，Gate A—E 通过，并产出 Spike Report 与 Readiness Recommendation）
- **Architecture Readiness Status: CONDITIONALLY READY**（用户已在人工 Gate 明确确认；`User Decision = CONDITIONALLY READY` 已记录于 [architecture-readiness-report-v1.md](architecture-readiness-report-v1.md) §16）
- **Development Status: CONDITIONALLY READY**（用户授权，**仅限**规划与治理范围）

**授权范围（允许开始）：** Architecture RFC · Implementation Planning · MVP Roadmap 草案 · Epic and Dependency Planning · Technical Risk Resolution。

**禁止范围（当前不授权）：** Production Business / Database / API / Retrieval / LLM Runtime / Observability Implementation；正式业务 Coding Issues；未经 RFC 支持的生产实现；Coding Agent 临场选择生产数据库 / ORM / Checkpointer / API / Retrieval / LLM Runtime / Observability；将 Spike 代码迁移为生产模块；将状态更新为完全 READY。

> `CONDITIONALLY READY ≠ 完全 READY`：Product Specification、RFC-001～006 与 Frontend Architecture 已完成；最小 RFC-007 与快速 MVP-0 策划包仍待接受。在全部重大 Proposal 与 Readiness Gate 被用户接受前，不实例化生产 Issue、不执行兼容性切片、不启动业务实现；闭合后按 DEC-072 的持续执行授权激活 Goal，不再要求重复固定口令。
