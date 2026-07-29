# DEC-037：正式授权 Claude Code 在 Repository Audit 和稳定文档基线通过后，执行 Spike-001 S0—S6，并创建受控 Issue、Branch、Commits、Push、Draft PR、测试证据与 Readiness Recommendation

> **Status: Accepted**
> **Date: 2026-07-30**
> **Type: Execution Authorization / Agent Governance / GitHub Workflow**
> **Related Session: Session-002**
> **Supersedes: None**
> **Amends: DEC-034、DEC-035 and DEC-036**（by formally granting execution authorization for Spike-001）
> **Contract Authorization Status: ACCEPTED**
> **Spike Execution Authorization Status: GRANTED**
> **Spike Execution Status: NOT STARTED**
> **Architecture Readiness Status: NOT READY**
> **Development Status: NOT READY**

---

## 用户确认

用户于 2026-07-30 对 **Formal Spike-001 Execution Authorization Proposal** 明确回复：

> 确认

通过 Decision Gate。本决定为 **Accepted Decision**，归档为 DEC-037。

---

## Core Decision

正式授权 Claude Code 作为 **Spike-001 Primary Execution Agent**，在符合 DEC-034、DEC-035 和 DEC-036 的前提下执行：

```text
Repository Audit
→ Stable Documentation Baseline
→ Spike Issue
→ Dedicated Spike Branch
→ S0—S6 Execution
→ Automated Tests
→ Runtime Evidence
→ Draft Pull Request
→ Spike Report
→ Readiness Recommendation
```

授权覆盖：

```text
S0：Environment and Skeleton
S1：Normal Workflow
S2：Human Review and Version Safety
S3：Transaction and Idempotency
S4：Failure and Recovery
S5：Observability and Evidence Export
S6：Spike Report and Readiness Recommendation
```

Claude 不需要在每个阶段重新获得用户授权，但必须遵守阶段更新 Gate 和强制停止条件。

**本决定接受的是「从规划和归档阶段进入实际仓库执行阶段」的授权，但仍以只读 Repository Audit 为第一动作，且在 Audit 与稳定文档基线通过前不得开始任何写入、安装或 Spike 代码。**

---

## Authorization Status

归档后状态更新为：

```text
Contract Authorization = ACCEPTED
Execution Authorization = GRANTED
Spike Execution Status = NOT STARTED
Architecture Readiness Status = NOT READY
Development Status = NOT READY
```

`Execution Authorization = GRANTED` 表示 Claude 已被允许开始执行。它**不**表示：

- Repository Audit 已经完成；
- Spike 已经开始；
- Spike 已经通过；
- Architecture 已经 READY；
- Development 已经 READY。

Claude 实际开始 Repository Audit 后，才可更新：

```text
Spike Execution Status = IN PROGRESS
```

---

## Authorized Repository

```text
Repository:
/Users/ketchup/Projects/AI Ecommerce Agent

Primary Execution Agent:
Claude Code

Optional Independent Reviewer:
Codex
```

---

## First Required Action

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

同时确认：

- Repository Root；
- 默认 Branch；
- 当前 Branch；
- Remote；
- GitHub 登录身份；
- 未提交改动；
- 未跟踪文件；
- Merge Conflict；
- DEC-001 至 DEC-037 的归档情况；
- DEC-035、DEC-036 和 DEC-037 是否已进入稳定 Git 历史；
- Current Specs 和 Architecture 是否已同步；
- `.gitignore` 是否覆盖 Spike 临时文件；
- 是否已存在 Spike Issue；
- 是否已存在 Spike Branch；
- 是否已存在 Spike PR。

**Claude 必须先形成 Repository Audit Report。** 不得在 Audit 完成前：

- 安装依赖；
- 创建 Spike 代码；
- 初始化数据库；
- 运行 Spike；
- 创建 Spike Branch；
- 创建 Draft PR。

---

## Audit Result Handling

### Audit Pass

若满足：工作区不存在未知修改 / Remote 正确 / GitHub 身份正确 / 文档基线已经提交 / 默认 Branch 可以作为稳定起点 / 不存在冲突的 Spike Branch、Issue 或 PR，则 Claude 可以继续：

```text
Create Spike Issue
→ Create Dedicated Branch
→ Begin S0
```

### Audit Blocked

若发现：未知未提交修改 / Remote 错误 / GitHub 身份错误 / 当前 Branch 异常 / Merge Conflict / 文档基线不完整 / 已存在冲突 Branch、Issue 或 PR，Claude **必须停止并报告**：

```text
Audit Finding
Current Repository State
Blocking Risk
Recommended Resolution
Safe Next Actions
```

不得覆盖、删除、Reset 或隐藏现有修改。

---

## Stable Documentation Baseline

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

必须记录：

```text
base_branch
base_commit_sha
created_at
created_by
```

如果 DEC-037 尚未进入稳定默认 Branch，Claude 必须先创建**文档基线 Branch**，例如：

```text
docs/session-002-spike-governance
```

该 Branch 只允许包含：DEC-035 / DEC-036 / DEC-037 / Decision Log / Agent Permissions / Spike Planning Documents / Readiness Status / 必要 Architecture 同步。

流程：

```text
Documentation Branch
→ Commit
→ Push
→ Documentation PR
→ Stop for User Review
```

用户 Merge 文档 PR 后，才能创建 Spike Branch。**不得从存在大量未提交文件的工作区直接开始 Spike。**

---

## Authorized Spike Issue

Baseline 通过后，Claude 获准创建：

```text
Spike-001: Validate LangGraph runtime, recovery and idempotency
```

Issue 至少包含：Objective / Related DEC / Temporary Stack / S0—S6 Checklist / Required Scenarios / Deliverables / Non-goals / Current Status / Findings / PR Link / Readiness Recommendation。

**Claude 当前只允许创建 Spike 相关 Issue。** 不得创建：正式 MVP Backlog / 正式 Business Epics / Fact Extraction 生产实现 Issue / Customer Insight 生产实现 Issue / Product Positioning 生产实现 Issue / Production Infrastructure Issue。这些内容必须等待 Architecture READY。

---

## Authorized Spike Branch

使用独立 Branch：

```text
spike/001-langgraph-runtime-recovery
```

不得在以下 Branch 上开发：

```text
main
master
release/*
production/*
```

主要允许修改：

```text
spikes/spike-001-langgraph-runtime-and-recovery/**
docs/spikes/spike-001-langgraph-runtime-and-recovery/**
```

可以有限更新（仅限 Spike Execution Status / Scenario Progress / Findings / Evidence Links / Known Limitations / Readiness Recommendation）：

```text
docs/readiness/**
docs/agents/README.md
```

**不得借助 Spike Branch 修改 Accepted Business Specs 或 Accepted DEC 的含义。**

---

## Authorized Draft Pull Request

完成 S0 并产生第一个有效 Commit 后，Claude 获准创建 Draft PR。建议标题：

```text
spike: validate LangGraph runtime and recovery architecture
```

PR 至少包含：Objective / Related Decisions / Related Spike Issue / Base Commit / Temporary Stack / Scope / Non-goals / Scenario Checklist / Test Status / Evidence Artifacts / Spike Findings / Known Limitations / Current Readiness Recommendation。

S1—S6 继续通过**同一个** Draft PR 更新。**不得为每个阶段分别创建 PR。**

---

## Authorized Git and GitHub Operations

Claude 可以：

```text
Repository Audit
Create documentation baseline Branch when required
Create Spike Issue
Create dedicated Spike Branch
git add explicit paths
git commit
git push authorized Branch
Create Draft PR
Update Issue
Update PR
View PR Checks
Respond to Review
Fix its own Branch
Run tests
Export evidence
Mark Draft PR ready for review after S6
```

Claude 不得：

```text
Work directly on main
Force Push
Rebase shared history
Amend pushed commits
Reset --hard
Clean unknown files
Delete Branch
Delete remote Branch
Merge PR
Enable Auto-merge
Close Issue
Self-approve PR
Modify Branch Protection
Modify Repository Settings
Modify Secrets
Modify Collaborator permissions
Self-declare READY
```

---

## Isolated Dependency Authorization

Audit 和 Spike Branch 创建完成后，Claude 获准在以下**隔离目录**内安装依赖：

```text
spikes/spike-001-langgraph-runtime-and-recovery
```

允许：

```bash
uv sync
pytest
python -m spike_runtime ...
```

允许：创建 Spike 虚拟环境 / 安装 Lockfile 中的依赖 / 创建本地临时 SQLite 文件 / 运行 Scenario Runner / 执行 Tests / 生成 Evidence。

不得：修改系统全局 Python / 使用管理员权限安装 / 卸载用户全局软件 / 修改项目其他环境 / 静默更换 LangGraph 版本 / 把 Spike 依赖加入生产依赖。

---

## Version Compatibility Boundary

已接受的临时组合为：

```text
Python 3.13
LangGraph 1.2.9
Compatible pinned langgraph-checkpoint-sqlite
```

如果无法安装或无法支持关键行为，Claude **只允许**：

1. 检查明显配置或包名错误；
2. 重建 Spike 自己的隔离环境；
3. 在不改变版本的情况下重试一次；
4. 保存脱敏错误；
5. 创建 Dependency Compatibility Finding；
6. 停止受影响阶段；
7. 向用户提交候选方案。

Claude **不得自行**：升级 LangGraph / 降级 LangGraph / 更换 Python / 更换 Checkpointer / 切换到其他 Workflow Framework。

---

## Execution Gates

Claude 必须在以下 Gate 更新 Issue 和 PR。

- **Gate A：Repository Audit** —— 至少报告：Repository Root / Current Branch / Default Branch / Remote / GitHub Identity / Working Tree / Baseline Status / Existing Issue·Branch·PR / Safe to Continue / Blocking Findings。
- **Gate B：S0 Complete** —— 至少报告：Python 和依赖版本 / Lockfile / 三个 SQLite Store / Minimal Graph / Runtime IDs / First Commit SHA / Draft PR / Test Status。
- **Gate C：S2 Complete** —— 至少报告：Interrupt·Resume / Duplicate Submit / Stale Review / Stale Checkpoint / Scenario Results / Findings。
- **Gate D：S4 Complete** —— 至少报告：Transaction Rollback / Retry / Structured Output Failure / Retrieval Fallback / Cancellation / Retry Budget Exhaustion / Recovery Case / Blocking Findings。
- **Gate E：S6 Complete** —— 至少报告：全部 Scenario Pass·Fail / Test Results / Runtime Evidence / Transaction Evidence / Trace / Spike Findings / Limitations / Required RFC List / Readiness Recommendation。

---

## Mandatory Stop Conditions

即使已经获得 S0—S6 连续授权，出现以下情况时必须**停止受影响工作**。

### Decision Conflict

- 必须违反 Accepted DEC 才能继续；
- Specs 与 DEC 存在无法调和的核心冲突；
- 需要改变 Human Review、Evidence 或 Current Truth 规则。

### Scope Expansion

- 需要修改正式生产目录；
- 需要创建正式 Domain Schema；
- 需要创建正式 API；
- 需要实现正式前端；
- 需要编写生产 Prompt；
- 需要创建 MVP Roadmap 或生产 Backlog。

### Repository Risk

- 未知工作区修改；
- Merge Conflict；
- Remote 异常；
- GitHub 身份异常；
- Base Commit 不正确；
- Branch 严重分叉。

### Dependency Conflict

- 确认版本无法满足 Spike；
- 需要修改已接受临时版本；
- Checkpoint 安全设置无法满足。

### Architecture Blocking Failure

- Partial Write 无法避免；
- Retry 创建重复业务版本；
- Stale Review 可以提交；
- Stale Checkpoint 可以恢复；
- Resume 无法幂等；
- Checkpoint 会覆盖 Current Truth；
- Cancellation 留下部分业务状态；
- Recovery 只有绕过 Validator 才能继续。

### Data or Secret Risk

- 必选测试需要真实 Secret；
- 必须使用真实用户数据；
- Secret 可能进入 Git、Log 或 Trace；
- 需要执行外部 Side Effect。

**Claude 必须创建 Spike Finding，不得为了让测试通过而隐藏问题。**

---

## S6 Completion Boundary

Claude 完成 S6 后必须**停止**。允许提交：

```text
RECOMMENDED: READY
```

或：

```text
RECOMMENDED: CONDITIONALLY READY
```

或：

```text
RECOMMENDED: NOT READY
```

但**不得**：Merge PR / 关闭 Spike Issue / 更新 Architecture Readiness 为 READY / 更新 Development Status 为 READY / 创建 MVP Roadmap / 创建正式 Epics / 创建正式 Business Issues / 启动生产开发。

S6 后状态应为：

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = PENDING USER REVIEW
Development Status = NOT READY
```

---

## User Authority

用户继续保留：

- Accepted Decision 修订权；
- Scope 扩张批准权；
- PR Merge 权；
- Issue Closure 权；
- Git 历史危险操作批准权；
- Architecture Readiness 最终确认权；
- Development Status 变更权。

只有用户明确确认：

```text
Architecture READY
```

才能更新：

```text
Architecture Readiness Status = READY
Development Status = READY
```

**PR Merge 不等于 READY。Issue Closed 不等于 READY。Agent Recommendation 不等于 READY。**

---

## Contract Summary

```text
Decision:
DEC-037

Authorization:
Claude may execute Spike-001 S0—S6

First Action:
Read-only Repository Audit

After Safe Audit and Stable Baseline:
- Create Spike Issue
- Create dedicated Branch
- Install isolated dependencies
- Implement Spike
- Run tests
- Export evidence
- Create and update Draft PR
- Submit Readiness Recommendation

Required Progress Gates:
A / B / C / D / E

User Retains:
- Merge authority
- Issue closure authority
- Decision revision authority
- Architecture READY authority
```

---

## Reason

DEC-034 已确定正式开发前必须执行 Spike。DEC-035 已确定 Spike 临时技术栈和执行方式。DEC-036 已确定 Claude 的 Git/GitHub 权限和用户保留的治理权限。因此需要正式的 **Execution Authorization**，明确允许 Claude 从规划和归档阶段进入实际仓库执行阶段，同时继续保留 Repository Audit / Stable Baseline / Scope Boundary / Mandatory Stop / Human Merge / Human READY 这些安全边界。

---

## Impact

该决定将允许后续 Claude Code 实际执行：Repository Audit / GitHub Spike Issue / Spike Branch / Dependency Installation / Spike Code / Automated Tests / Evidence Export / Draft Pull Request / Spike Report / Readiness Recommendation。

**不**改变 Architecture Readiness Status（保持 `NOT READY`）；**不**改变 Development Status（保持 `NOT READY`）；**不**改变 Spike Execution Status（保持 `NOT STARTED`，直到 Claude 实际开始 Repository Audit 后才可更新为 `IN PROGRESS`）。唯一变化：`Execution Authorization` 从 `NOT GRANTED` 变为 `GRANTED`。

---

## Decision Boundary

本决定**已经确认**：正式执行授权 / Claude 为执行 Agent / 一次授权覆盖 S0—S6 / First Action 必须是 Repository Audit / Audit Block Handling / Stable Documentation Baseline / Documentation PR / Spike Issue / Dedicated Branch / Draft PR / Stage Commits / Isolated Dependency Installation / Version Conflict Handling / Gate A—E / Mandatory Stop Conditions / S6 Completion Boundary / User Final Authority / Architecture 和 Development 继续 NOT READY。

本决定**尚未确认**：实际 Repository Audit 结果 / Baseline Commit SHA / Issue 编号 / Branch 是否已经创建 / PR 编号 / 测试结果 / Spike Findings / Codex Independent Review / Merge Strategy / Spike PR 是否 Merge / Architecture Readiness Result / Development Status 是否 READY。

---

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related Decisions

- DEC-023：LangGraph StateGraph；
- DEC-024：Versioned Domain State；
- DEC-029：Human Review and Approved Strategy；
- DEC-032：Hybrid Retrieval and Evidence Runtime；
- DEC-033：Workflow Runtime Failure Recovery, Retry and Observability；
- DEC-034：Technical Spike and Architecture Readiness Gate；
- DEC-035：Technical Spike Temporary Stack and Execution Contract；
- DEC-036：Spike-001 Execution Authorization and Agent Handoff Contract。

## Related RFC

None

## Supersedes

None

## Amends

**DEC-034、DEC-035 and DEC-036** —— by formally granting execution authorization for Spike-001.

> 本归档**不修改** DEC-034 / DEC-035 / DEC-036 决定文件、其概念规格或其在 decision-log 中的行（历史记录保留不动）；Amends 关系仅记录于本 DEC-037 文件与 decision-log 的 DEC-037 行。DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 的历史记录同样保持不动。

---

## Notes

下一动作（尚未开始，需在归档进入稳定 Git 基线后以独立任务执行）：**`Spike-001 Execution Handoff`**——该任务第一步必须是**只读 Repository Audit**。

在归档完成并进入稳定 Git 基线前：

```text
Contract Authorization = ACCEPTED
Execution Authorization = GRANTED
Spike Execution Status = NOT STARTED
Architecture Readiness Status = NOT READY
Development Status = NOT READY
```
