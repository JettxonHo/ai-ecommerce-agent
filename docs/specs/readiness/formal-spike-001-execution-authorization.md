# Formal Spike-001 Execution Authorization（概念规格）

> **Status: CONCEPTUAL — 仅概念，非最终实现**
> **来源决定：** [../../decisions/dec-037-formal-spike-001-execution-authorization.md](../../decisions/dec-037-formal-spike-001-execution-authorization.md)（DEC-037，Accepted，2026-07-30；Execution Authorization / Agent Governance / GitHub Workflow；Amends DEC-034 + DEC-035 + DEC-036）
> **相关：** [../../agents/git-and-github-permissions.md](../../agents/git-and-github-permissions.md)（Git/GitHub 权限操作参考）；[../../spikes/spike-001-langgraph-runtime-and-recovery/](../../spikes/spike-001-langgraph-runtime-and-recovery/)（Spike 工作区）；[spike-001-execution-authorization-and-agent-handoff-contract.md](spike-001-execution-authorization-and-agent-handoff-contract.md)（DEC-036 概念规格）
> **本文件是概念层规格记录，不创建 Spike Branch / Issue / PR / 代码，不执行 Spike，不运行 Repository Audit。**

---

## §0 定位

本规格把 DEC-037 的**正式执行授权**展开为概念层结构：授权状态迁移 / 授权仓库与 Agent / 第一必需动作（Repository Audit）/ Audit 结果处理 / 稳定文档基线 / 授权 Issue·Branch·Draft PR / 授权与禁止的 Git·GitHub 操作 / 隔离依赖授权 / 版本兼容边界 / 执行 Gate A—E / Mandatory Stop Conditions / S6 完成边界 / 用户权限。

它回答的是：**DEC-036 已确认的权限契约，如何被正式激活为「可实际执行 Spike-001 S0—S6」的授权，以及激活后哪些边界与 Gate 仍然有效。** 它**不**改变已确认的角色、权限边界或临时技术栈（这些由 DEC-035 / DEC-036 定义），只定义**授权的授予与激活顺序**。

> **核心迁移：** `Contract Authorization = ACCEPTED`（DEC-036）保持；`Execution Authorization` 从 `NOT GRANTED`（DEC-036 后）变为 **`GRANTED`**（DEC-037）。但 `GRANTED` ≠ 已开始执行 —— 执行的第一动作仍是只读 Repository Audit。

---

## §1 授权状态迁移（Authorization Status Transition）

| 层级 | DEC-036 后 | DEC-037 后 | 含义 |
|---|---|---|---|
| **Contract Authorization** | `ACCEPTED` | `ACCEPTED` | 权限与执行契约已接受（DEC-036），不变。 |
| **Execution Authorization** | `NOT GRANTED` | **`GRANTED`** | Claude 已被允许开始执行 Spike-001 S0—S6。 |
| **Spike Execution Status** | `NOT STARTED` | `NOT STARTED` | Spike 尚未开始；Claude 实际开始 Repository Audit 后才可更新为 `IN PROGRESS`。 |
| **Architecture Readiness Status** | `NOT READY` | `NOT READY` | 不变。 |
| **Development Status** | `NOT READY` | `NOT READY` | 不变。 |

`Execution Authorization = GRANTED` **不表示**：Repository Audit 已完成 / Spike 已开始 / Spike 已通过 / Architecture 已 READY / Development 已 READY。

---

## §2 授权仓库与 Agent（Authorized Repository and Agents）

```text
Repository:
/Users/ketchup/Projects/AI Ecommerce Agent

Primary Execution Agent:
Claude Code

Optional Independent Reviewer:
Codex
```

角色与权限边界沿用 DEC-036（见 [git-and-github-permissions.md](../../agents/git-and-github-permissions.md)）；本规格不重复定义，只激活其执行。

---

## §3 第一必需动作（First Required Action）

Claude 的第一项执行操作**必须**是**只读** Repository Audit。至少检查：

```bash
git status --short
git branch --show-current
git remote -v
git log --oneline --decorate -15
git diff --stat
git diff
gh auth status
```

同时确认：Repository Root / 默认 Branch / 当前 Branch / Remote / GitHub 登录身份 / 未提交改动 / 未跟踪文件 / Merge Conflict / DEC-001 至 DEC-037 的归档情况 / DEC-035·036·037 是否已进入稳定 Git 历史 / Current Specs 和 Architecture 是否已同步 / `.gitignore` 是否覆盖 Spike 临时文件 / 是否已存在 Spike Issue / 是否已存在 Spike Branch / 是否已存在 Spike PR。

**Claude 必须先形成 Repository Audit Report。** 在 Audit 完成前**不得**：安装依赖 / 创建 Spike 代码 / 初始化数据库 / 运行 Spike / 创建 Spike Branch / 创建 Draft PR。

---

## §4 Audit 结果处理（Audit Result Handling）

### Audit Pass

满足：工作区不存在未知修改 / Remote 正确 / GitHub 身份正确 / 文档基线已经提交 / 默认 Branch 可作为稳定起点 / 不存在冲突的 Spike Branch·Issue·PR → 可继续：

```text
Create Spike Issue
→ Create Dedicated Branch
→ Begin S0
```

### Audit Blocked

发现：未知未提交修改 / Remote 错误 / GitHub 身份错误 / 当前 Branch 异常 / Merge Conflict / 文档基线不完整 / 已存在冲突 Branch·Issue·PR → **必须停止并报告**：

```text
Audit Finding
Current Repository State
Blocking Risk
Recommended Resolution
Safe Next Actions
```

不得覆盖、删除、Reset 或隐藏现有修改。

---

## §5 稳定文档基线（Stable Documentation Baseline）

Spike Branch 必须基于包含以下内容的稳定 Commit：

```text
DEC-001 through DEC-037
Current Specifications
Architecture Documents
Spike Plan
Test Scenarios
Temporary Stack
Execution Brief
Git and GitHub Permissions
Agent Handoff Contract
Formal Execution Authorization
```

必须记录 `base_branch` / `base_commit_sha` / `created_at` / `created_by`。

若 DEC-037 尚未进入稳定默认 Branch，Claude 必须先创建**文档基线 Branch**（例如 `docs/session-002-spike-governance`），只允许包含 DEC-035 / DEC-036 / DEC-037 / Decision Log / Agent Permissions / Spike Planning Documents / Readiness Status / 必要 Architecture 同步。流程：

```text
Documentation Branch
→ Commit
→ Push
→ Documentation PR
→ Stop for User Review
```

用户 Merge 文档 PR 后才能创建 Spike Branch。**不得从存在大量未提交文件的工作区直接开始 Spike。**

---

## §6 授权 Spike Issue / Branch / Draft PR

### Spike Issue（Baseline 通过后）

标题 `Spike-001: Validate LangGraph runtime, recovery and idempotency`，至少含 Objective / Related DEC / Temporary Stack / S0—S6 Checklist / Required Scenarios / Deliverables / Non-goals / Current Status / Findings / PR Link / Readiness Recommendation。**只允许创建 Spike 相关 Issue**；不得创建正式 MVP Backlog / Business Epics / 生产实现 Issues（Fact Extraction / Customer Insight / Product Positioning / Production Infrastructure）——这些须等 Architecture READY。

### Spike Branch

`spike/001-langgraph-runtime-recovery`。禁止 `main`/`master`/`release/*`/`production/*`。主要允许修改 `spikes/spike-001-langgraph-runtime-and-recovery/**` 与 `docs/spikes/spike-001-langgraph-runtime-and-recovery/**`；可有限更新 `docs/readiness/**` 与 `docs/agents/README.md`（仅限 Spike Execution Status / Scenario Progress / Findings / Evidence Links / Known Limitations / Readiness Recommendation）。**不得修改 Accepted Business Specs 或 Accepted DEC 的含义。**

### Draft Pull Request

S0 完成并产生第一个有效 Commit 后创建，建议标题 `spike: validate LangGraph runtime and recovery architecture`，至少含 Objective / Related Decisions / Related Spike Issue / Base Commit / Temporary Stack / Scope / Non-goals / Scenario Checklist / Test Status / Evidence Artifacts / Spike Findings / Known Limitations / Current Readiness Recommendation。S1—S6 经**同一个** Draft PR 更新，**不得**为每阶段分别建 PR。

---

## §7 授权与禁止的 Git / GitHub 操作

**Claude 可以：** Repository Audit / 需要时创建文档基线 Branch / 创建 Spike Issue / 创建独立 Spike Branch / `git add` 明确路径 / `git commit` / `git push` 授权 Branch / 创建 Draft PR / 更新 Issue / 更新 PR / 查看 PR Checks / 回应 Review / 修复自己 Branch / 运行测试 / 导出证据 / S6 后将 Draft PR 标 Ready for Review。

**Claude 不得：** 直接在 main 工作 / Force Push / Rebase 共享历史 / Amend 已 Push Commit / Reset --hard / Clean 未知文件 / 删除 Branch / 删除远程 Branch / Merge PR / 启用 Auto-merge / 关闭 Issue / 自批 PR / 修改 Branch Protection / 修改 Repository Settings / 修改 Secrets / 修改 Collaborator 权限 / 自行宣布 READY。

---

## §8 隔离依赖授权（Isolated Dependency Authorization）

Audit 和 Spike Branch 创建完成后，Claude 获准在隔离目录 `spikes/spike-001-langgraph-runtime-and-recovery` 内安装依赖。允许 `uv sync` / `pytest` / `python -m spike_runtime ...`；允许创建 Spike 虚拟环境 / 安装 Lockfile 依赖 / 创建本地临时 SQLite / 运行 Scenario Runner / 执行 Tests / 生成 Evidence。**不得**修改系统全局 Python / 用管理员权限安装 / 卸载用户全局软件 / 修改项目其他环境 / 静默更换 LangGraph 版本 / 把 Spike 依赖加入生产依赖。

---

## §9 版本兼容边界（Version Compatibility Boundary）

已接受临时组合：Python 3.13 / LangGraph 1.2.9 / Compatible pinned langgraph-checkpoint-sqlite。若无法安装或无法支持关键行为，Claude 只允许：检查明显配置或包名错误 → 重建 Spike 自己的隔离环境 → 不改变版本重试一次 → 保存脱敏错误 → 创建 Dependency Compatibility Finding → 停止受影响阶段 → 提交候选方案。**不得自行**升级/降级 LangGraph、更换 Python、更换 Checkpointer 或切换其他 Workflow Framework。

---

## §10 执行 Gate（Execution Gates A—E）

| Gate | 触发 | 至少报告 |
|---|---|---|
| **A** | Repository Audit | Repository Root / Current Branch / Default Branch / Remote / GitHub Identity / Working Tree / Baseline Status / Existing Issue·Branch·PR / Safe to Continue / Blocking Findings |
| **B** | S0 Complete | Python 与依赖版本 / Lockfile / 三个 SQLite Store / Minimal Graph / Runtime IDs / First Commit SHA / Draft PR / Test Status |
| **C** | S2 Complete | Interrupt·Resume / Duplicate Submit / Stale Review / Stale Checkpoint / Scenario Results / Findings |
| **D** | S4 Complete | Transaction Rollback / Retry / Structured Output Failure / Retrieval Fallback / Cancellation / Retry Budget Exhaustion / Recovery Case / Blocking Findings |
| **E** | S6 Complete | 全部 Scenario Pass·Fail / Test Results / Runtime Evidence / Transaction Evidence / Trace / Spike Findings / Limitations / Required RFC List / Readiness Recommendation |

这些是**进度与审计 Gate，不自动表示需要暂停。**

---

## §11 Mandatory Stop Conditions

即使已获 S0—S6 连续授权，出现以下情况必须停止受影响工作：**Decision Conflict**（须违反 Accepted DEC / Specs 与 DEC 核心冲突 / 需改 Human Review·Evidence·Current Truth 规则）/ **Scope Expansion**（改生产目录 / 建正式 Domain Schema·API / 实现前端 / 写生产 Prompt / 建 MVP Roadmap·生产 Backlog）/ **Repository Risk**（未知修改 / Merge Conflict / Remote 异常 / GitHub 身份异常 / Base Commit 不正确 / Branch 严重分叉）/ **Dependency Conflict**（版本无法满足 / 需改临时版本 / Checkpoint 安全无法满足）/ **Architecture Blocking Failure**（Partial Write 无法避免 / Retry 重复业务版本 / Stale Review 可提交 / Stale Checkpoint 可恢复 / Resume 无法幂等 / Checkpoint 覆盖 Current Truth / Cancellation 留部分业务状态 / Recovery 须绕 Validator）/ **Data or Secret Risk**（必选需真实 Secret / 需真实用户数据 / Secret 可能进 Git·Log·Trace / 需外部 Side Effect）。**Claude 必须创建 Spike Finding，不得为了让测试通过而隐藏问题。**

---

## §12 S6 完成边界（S6 Completion Boundary）

Claude 完成 S6 后必须**停止**。允许提交 `RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`。但**不得** Merge PR / 关闭 Spike Issue / 更新 Architecture Readiness 为 READY / 更新 Development Status 为 READY / 创建 MVP Roadmap / 正式 Epics / 正式 Business Issues / 启动生产开发。

S6 后状态应为：`Spike Execution Status = COMPLETED` / `Architecture Readiness Status = PENDING USER REVIEW` / `Development Status = NOT READY`。

---

## §13 用户权限（User Authority）

用户继续保留：Accepted Decision 修订权 / Scope 扩张批准权 / PR Merge 权 / Issue Closure 权 / Git 历史危险操作批准权 / Architecture Readiness 最终确认权 / Development Status 变更权。仅当用户明确确认「Architecture READY」才可更新 `Architecture Readiness Status = READY` 与 `Development Status = READY`。**PR Merge ≠ READY；Issue Closed ≠ READY；Agent Recommendation ≠ READY。**

---

## §14 当前授权状态

```text
Contract Authorization = ACCEPTED
Execution Authorization = GRANTED
Spike Execution Status = NOT STARTED
Architecture Readiness Status = NOT READY
Development Status = NOT READY
```

下一动作：`Spike-001 Execution Handoff`（独立任务；第一步必须是只读 Repository Audit）。本归档**不**运行 Repository Audit / 创建实际 Issue·Branch·PR / Push / 安装依赖 / 创建 Spike 代码 / 运行测试 / 初始化 SQLite / 启动 S0。
