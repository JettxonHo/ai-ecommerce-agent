# Spike-001 — LangGraph Runtime and Recovery（Spike 工作区）

> **Status: IN PROGRESS（S0—S6 执行中）**
> **来源决定：** [DEC-034 — Technical Spike Plan and Architecture Readiness Gate](../../decisions/dec-034-technical-spike-and-architecture-readiness-gate.md) · [DEC-035 — Technical Spike 临时技术栈与执行契约](../../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)
> **概念规格：** [../../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../../specs/readiness/technical-spike-and-architecture-readiness-gate.md) · [../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)
> **相关 Session：** [Session-002](../../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Spike Issue：** [#1](https://github.com/JettxonHo/ai-ecommerce-agent/issues/1) · **Dedicated Branch：** `spike/001-langgraph-runtime-recovery`
> **Development Status: NOT READY · Spike Execution Status: IN PROGRESS · Architecture Readiness Status: NOT READY**

---

## 本工作区是什么

这是 DEC-034 治理下的**最小架构 Technical Spike 工作区**，用于在进入正式业务开发前，用最小 Mock Workflow 验证高风险架构行为：StateGraph 执行、Checkpoint 持久化、Interrupt / Resume、事务回滚、幂等提交、有界重试、Stale Review 拒绝、Stale Checkpoint 拒绝、Retrieval Fallback、Cancellation、Trace 关联。

Spike **不是** MVP、**不是** 正式业务 Graph、**不是** 四个核心 Skill 的生产实现、**不是** 最终 Prompt、**不是** 正式数据库 Schema。Spike 验证**架构行为**而非业务输出质量。

## 范围约束（重要）

本 Spike **不包含正式业务实现**：不创建正式业务 Graph、不创建正式业务 Skill、不编写正式业务 Prompt、不创建正式数据库表、不创建前端、不实现自动发布、不创建 Multi-Agent / Supervisor / Worker。本工作区**只**记录验证目标、Mock Workflow、测试场景、成功标准、证据要求与失败标准。

## 临时技术栈（DEC-035，临时选择不构成生产承诺）

DEC-035 已为 Spike-001 确定明确、可复现、确定性的临时执行环境（详见 [`temporary-stack.md`](./temporary-stack.md) 与 [`execution-brief.md`](./execution-brief.md)）：

```text
Python 3.13
+
LangGraph StateGraph 1.2.9（精确固定）
+
Synchronous Invoke
+
三个分离 SQLite（business.sqlite / runtime.sqlite / checkpoints.sqlite）
+
LangGraph SqliteSaver
+
Python sqlite3 Transactions（统一 BusinessCommitService）
+
Scripted Deterministic Model
+
Mock Retrieval Runtime
+
Scenario-based Fault Injection
+
pytest
+
Local JSONL Trace（LocalTraceRecorder）
+
CLI Scenario Runner
```

**所有临时选择都不构成生产技术承诺**（生产后端语言 / 数据库 / Checkpointer / ORM / Observability / Retrieval / 部署平台仍待后续 RFC）。

## 当前文件

- `README.md`（本文件）— Spike 工作区概览。
- `spike-plan.md` — Spike 计划（目的 / 范围 / 最小 Workflow / Mock 对象 / Graph State / 仓库分离 / 验证项 / Fault Injection / 证据 / 完成标准）。
- `test-scenarios.md` — 12 个必选（含 1 个可选）Spike 场景与各自成功标准。
- `temporary-stack.md` — 临时技术栈（DEC-035：Python 3.13 / LangGraph 1.2.9 / 同步 / 三 SQLite / SqliteSaver / Scripted Model / Mock Retrieval / pytest / JSONL / CLI）。
- `execution-brief.md` — 执行简报（DEC-035：Spike Objective / Human Review 节点边界 / Repository 职责 / Atomic Commit / Fault Injection / Scenario Runner / Scenario Isolation / S0—S6 / Agent 权限与禁止 / Secret 边界 / 交付物 / 结果接受边界）。

## Spike 执行后才会产生（当前不创建）

```text
implementation-notes.md
test-results.md
runtime-evidence.md
limitations.md
spike-report.md
```

## 与历史 Spike 文档的关系

仓库根 `docs/spikes/` 下另有一份历史 Spike 规划：[`langgraph-stategraph-workflow-spike.md`](../langgraph-stategraph-workflow-spike.md)（DEC-023 时期）。它是更早的、范围较窄的 Spike 概念记录，**作为历史记录保留不动**。本 `spike-001` 工作区是 DEC-034 治理下**当前权威**的 Spike 工作区（范围更全：纳入 DEC-033 的失败恢复 / 重试 / 事务 / 可观测性与 Stale Review / Stale Checkpoint / 幂等 / Cancellation 等可靠性场景）。

## 何时执行 Spike

**当前不执行 Spike。** 临时技术栈由 DEC-035 确认；执行授权契约已由 **DEC-036（Spike-001 Execution Authorization and Agent Handoff Contract，Accepted，2026-07-29）** 确认；正式执行授权已由 **DEC-037（Formal Spike-001 Execution Authorization，Accepted，2026-07-30）** 授予。DEC-036 确认的执行治理项（详见 [`../../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md`](../../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md) 与 [`../../agents/git-and-github-permissions.md`](../../agents/git-and-github-permissions.md)）：

- **Primary Execution Agent = Claude Code**（Git Operator / GitHub Issue and PR Operator / Spike Evidence Producer / Readiness Recommendation Author）。
- **Optional Independent Reviewer = Codex**（S6 完成后单独授权独立 Review）。
- **Repository Audit**：正式执行前先只读审计（`git status --short` / `git branch --show-current` / `git remote -v` / `git log --oneline --decorate -15` / `git diff --stat` / `git diff` / `gh auth status` 等），输出 Repository Audit Report 后方可继续。
- **Dedicated Branch**：`spike/001-langgraph-runtime-recovery`，禁止直接在 `main`/`master`/`release/*`/`production/*` 开发。
- **Stage Commits**：按阶段保持可审查 Commit（无 Secret / 无真实用户数据），Squash Merge 由用户决定。
- **Issue and PR**：一个 Spike 主 Issue + S0 首个有效 Commit 后创建 Draft PR；`GitHub Issue 不能替代 Spec，PR 描述不能替代 Accepted Decision`。
- **Mandatory Stop Conditions**：Decision Conflict / Scope Expansion / Version Conflict / Repository Risk / Secret or Data Risk / Architecture Blocking Failure —— 出现必须停止并报告，不得掩盖绕过。
- **Final Human Gate**：用户审查 Issue / PR Diff / 测试 / 证据 / Findings / Report / Codex Review 后决定 Merge 与 Readiness；`Merge PR ≠ READY，关闭 Issue ≠ READY，Claude Recommendation ≠ READY`。

**授权状态：** DEC-036 接受的是**权限与执行契约（`Contract Authorization = ACCEPTED`）**；DEC-037 正式授予**执行授权（`Execution Authorization = GRANTED`）**——Claude 已被允许执行 Spike-001 S0—S6，但这**不表示** Spike 已开始或已通过。执行的第一动作仍是**只读 Repository Audit**，且在 Audit 与稳定文档基线通过前**不**安装依赖、**不**创建 Spike 代码 / Branch / Issue / PR、**不**运行测试。`Spike Execution Status = NOT STARTED`（须待 Claude 实际开始 Repository Audit 后才可更新为 `IN PROGRESS`）、`Architecture Readiness Status = NOT READY`、`Development Status = NOT READY`。下一动作为 **`Spike-001 Execution Handoff`**（归档进入稳定 Git 基线后以独立任务执行；第一步必须是只读 Repository Audit）。
