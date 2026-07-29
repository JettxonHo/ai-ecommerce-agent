# DEC-036：Spike-001 采用 Claude 主执行、受控 Git/GitHub 权限、独立 Branch、Issue/PR 追踪、阶段化提交与用户保留 Merge 和 READY 决策权的执行授权契约

> **Status: Accepted**
> **Date: 2026-07-29**
> **Type: Agent Governance / Git and GitHub Operations / Spike Execution Authorization**
> **Related Session: Session-002**
> **Supersedes: None**
> **Amends: DEC-034 and DEC-035**（为 Spike-001 定义授权执行 Agent、Git/GitHub 工作流、仓库边界与人工审批 Gate）
> **Contract Authorization Status: ACCEPTED**
> **Spike Execution Authorization Status: NOT GRANTED**
> **Spike Execution Status: NOT STARTED**
> **Architecture Readiness Status: NOT READY**
> **Development Status: NOT READY**

---

## 用户确认

用户于 2026-07-29 对 **Spike-001 Execution Authorization and Agent Handoff Contract** 议题明确回复：

> 确认形成 DEC-036

通过 Decision Gate。本决定为 **Accepted Decision**，归档为 DEC-036。

---

## Core Decision

`Spike-001：LangGraph Runtime and Recovery` 正式采用以下执行治理模式：

```text
Product Decision Owner:
User

Primary Spike Execution Agent:
Claude Code

Optional Independent Reviewer:
Codex

Git Workflow:
Stable Baseline
→ Dedicated Spike Branch
→ Stage Commits
→ Push
→ Spike Issue
→ Draft Pull Request
→ Tests and Evidence
→ Human Review
→ User Merge Decision

Architecture Readiness:
Agent Recommendation
→ User Decision
```

Claude Code 获得在明确边界内进行 Git、GitHub 和 Spike 执行操作的权限。用户保留：

- Accepted Decision 变更权；
- Scope 扩张批准权；
- Pull Request Merge 权；
- Branch 历史改写批准权；
- Architecture Readiness 最终确认权；
- Development Status 变更权。

**本决定接受的是权限和执行契约，不是立即开始执行 Spike。**

---

## Authorization Layers

必须区分两种授权。

### Contract Authorization

本次 DEC-036 表示：Claude Code 被允许在正式启动 Spike 后，按照本契约管理 Spike Branch、Commits、GitHub Issue、Draft PR、测试和执行证据。该权限契约已经接受。

### Execution Authorization

表示：用户明确要求 Claude 实际创建 Branch、Issue、代码、测试和 PR，并开始执行 S0—S6。

**DEC-036 被接受后，Spike 仍不得自动启动。** 正式启动需要用户后续明确指令，例如：

```text
正式授权执行 Spike-001。
```

在该指令出现前，状态保持：

```text
Spike Execution Status = NOT STARTED
Architecture Readiness Status = NOT READY
Development Status = NOT READY
```

---

## Agent Roles

### Claude Code

正式角色：

```text
Primary Spike Execution Agent
Git Operator
GitHub Issue and PR Operator
Spike Evidence Producer
Readiness Recommendation Author
```

Claude 负责：

- Repository Audit；
- Spike Branch；
- Spike Issue；
- Draft PR；
- S0—S6 实现；
- 自动化测试；
- Fault Injection；
- Runtime Evidence；
- Spike Findings；
- Spike Report；
- Readiness Recommendation。

### Codex

默认角色：

```text
Optional Independent Reviewer
```

Codex 可以在获得单独任务后：

- 审查 Spike Diff；
- 运行测试；
- 核对 Scenario Assertions；
- 检查 DEC 和 Specs 一致性；
- 审查 Spike Report；
- 提交独立 Review Report；
- 在 PR 中提出 Review 意见。

Codex 默认**不得**与 Claude 同时修改同一个 Branch。Codex 默认**不得**：

- Push Claude Branch；
- Merge PR；
- 修改 Accepted DEC；
- 自行宣布 READY。

### User

正式角色：

```text
Product Decision Owner
Architecture Readiness Approver
Merge Authority
```

用户负责：

- 接受或拒绝 Scope 变化；
- 接受或拒绝 DEC 修订；
- 审查 PR；
- 决定是否 Merge；
- 决定是否关闭 Spike Issue；
- 确认最终 Readiness 状态；
- 确认 Development Status 是否变为 READY。

---

## Repository Audit

Claude 正式开始 Spike 前，必须先进行**只读** Repository Audit。至少执行或检查：

```bash
git status --short
git branch --show-current
git remote -v
git log --oneline --decorate -15
git diff --stat
git diff
gh auth status
```

Audit 还必须确认：

- Repository Root；
- 默认 Branch；
- 当前 Branch；
- 当前 Branch 是否跟踪远程；
- 是否存在未提交改动；
- 是否存在未跟踪文件；
- 是否存在与当前项目无关的修改；
- DEC-001 至 DEC-036 是否已经归档；
- DEC-035 和 DEC-036 是否已经进入稳定 Git 历史；
- `.gitignore` 是否覆盖临时 Spike 数据；
- 是否已经存在 Spike Branch；
- 是否已经存在 Spike Issue；
- 是否已经存在 Spike PR；
- GitHub Remote 是否指向预期仓库；
- 当前 `gh` 登录身份是否符合预期；
- 当前权限是否足以创建 Issue、Push Branch 和创建 PR。

**Claude 必须先输出 Repository Audit Report。存在未识别或可能冲突的改动时，不得继续覆盖。**

---

## Stable Baseline

Spike Branch 必须从稳定 Git Commit 创建。Baseline 至少应包含：

```text
DEC-001 through DEC-036
Current Business Specifications
Current Architecture Documents
Spike Plan
Test Scenarios
Temporary Stack
Execution Brief
Agent Handoff Contract
```

必须记录：

```text
base_branch
base_commit_sha
created_at
created_by
```

**不得**从包含大量未提交改动的工作区直接启动 Spike。如果 DEC-036 尚未进入默认 Branch，先完成文档归档和对应 Git 流程，再创建 Spike Branch。Claude 暂时**不得**自行创建正式 Git Tag。

---

## Dedicated Spike Branch

Spike 使用独立 Branch：

```text
spike/001-langgraph-runtime-recovery
```

**不得**直接在以下 Branch 开发：

```text
main
master
release/*
production/*
```

Spike Branch 主要允许修改：

```text
spikes/spike-001-langgraph-runtime-and-recovery/**
docs/spikes/spike-001-langgraph-runtime-and-recovery/**
```

经过本契约允许，还可以更新：

```text
docs/readiness/**
docs/agents/README.md
```

这些文件只能更新：

- Spike Execution Status；
- Scenario Progress；
- Evidence Links；
- Findings；
- Readiness Recommendation；
- Known Limitations。

Spike Branch **不得**修改 Accepted DEC 的含义。Spike Branch **不得**把 Mock Schema 写成正式 Data Architecture。

---

## Authorized Local Git Operations

Claude 可以执行以下安全 Git 操作：

```bash
git status
git diff
git diff --staged
git log
git show
git branch
git switch
git fetch
git add <explicit-paths>
git commit
git push -u origin <spike-branch>
```

Claude 可以：

- 创建受控 Spike Branch；
- 切换到 Spike Branch；
- 查看本地和远程差异；
- 按阶段组织 Commit；
- 在 Commit 前运行测试；
- Push 自己负责的 Branch；
- 根据 Review 修改自己的 Branch；
- Push 修复 Commit；
- 报告 Commit SHA。

### Explicit Add Rule

优先使用明确路径：

```bash
git add spikes/spike-001-langgraph-runtime-and-recovery
git add docs/spikes/spike-001-langgraph-runtime-and-recovery
```

**不得**在未检查全部变化时默认使用：

```bash
git add .
git add -A
```

若确需使用，必须先完整审查 `git status` 和 Diff，并确认所有变化都属于当前任务。

---

## Authorized GitHub Operations

在 GitHub Remote 正确且 `gh` 已认证时，Claude 可以执行：

```bash
gh issue create
gh issue view
gh issue comment
gh issue edit

gh pr create
gh pr view
gh pr checks
gh pr comment
gh pr edit
```

Claude 获准：

- 创建 Spike-001 主 Issue；
- 更新 Issue 描述；
- 更新 Issue Checklist；
- 在 Issue 中记录阶段进度；
- 在 Issue 中发布测试摘要；
- 在 Issue 中记录 Spike Finding；
- 关联 Commit 和 PR；
- 创建 Draft PR；
- 更新 Draft PR 描述；
- 查看 PR Checks；
- 回复 Review Comments；
- 修复自己 Branch 中的问题；
- Push 修复 Commit；
- 在 S6 完成后将 Draft PR 标记为 Ready for Review；
- 请求用户 Review。

---

## Prohibited Git Operations

未经用户针对性授权，Claude 禁止执行：

```bash
git push --force
git push --force-with-lease
git reset --hard
git clean -fd
git clean -fdx
git rebase
git commit --amend
git branch -D
git tag
git tag -d
git push --delete
```

Claude **不得**：

- 改写已 Push 的共享 Commit 历史；
- 删除本地或远程 Branch；
- 强制覆盖远程 Branch；
- 在出现冲突时自行采用破坏性恢复；
- 删除用户未提交工作；
- 清理无法确认归属的未跟踪文件。

需要上述操作时，必须停止并向用户说明：

- 当前状态；
- 风险；
- 候选方案；
- 推荐操作；
- 哪些数据可能被影响。

---

## Prohibited GitHub Operations

未经用户针对性授权，Claude 禁止执行：

```bash
gh pr merge
gh pr close
gh issue close
```

同时禁止：

- 启用 Auto-merge；
- 绕过失败 Checks；
- 自行批准自己的 PR；
- 删除 Review Comments；
- 删除远程 Branch；
- 修改 PR Base Branch；
- 修改 Branch Protection；
- 修改 Repository Visibility；
- 修改 Collaborator 权限；
- 修改 GitHub Secrets；
- 创建或删除 Deploy Key；
- 修改 GitHub Actions 权限；
- 删除用户创建的 Issue 或 PR；
- 修改 Repository Settings；
- 将 Spike PR 转为正式生产 Feature PR。

---

## Spike Issue Contract

Claude 获准创建一个主要 Spike Issue。建议标题：

```text
Spike-001: Validate LangGraph runtime, recovery and idempotency
```

Issue 至少包含以下内容。

### Objective

验证与以下决策相关的高风险架构行为：

```text
DEC-023
DEC-024
DEC-029
DEC-032
DEC-033
DEC-034
DEC-035
DEC-036
```

### Scope

```text
S0 Environment and Skeleton
S1 Normal Workflow
S2 Human Review and Version Safety
S3 Transaction and Idempotency
S4 Failure and Recovery
S5 Observability and Evidence Export
S6 Spike Report and Readiness Recommendation
```

### Required Scenarios

- Normal Workflow；
- Transient Retry；
- Invalid Structured Output；
- Transaction Rollback；
- Human Review Interrupt and Resume；
- Duplicate Review Submit；
- Stale Review Package；
- Stale Checkpoint；
- Retrieval Fallback；
- Cancellation；
- Retry Budget Exhaustion；
- Manual Recovery。

### Deliverables

- Spike Code；
- Automated Tests；
- Scenario Results；
- Runtime Records；
- Trace Evidence；
- Transaction Evidence；
- Spike Findings；
- Spike Report；
- Required RFC List；
- Readiness Recommendation。

### Non-goals

- Production Backend；
- Production Database；
- Production API；
- Production UI；
- Production Prompt；
- Production Retrieval；
- Production Deployment；
- MVP Roadmap；
- 正式业务 Backlog。

### Issue Permission Boundary

Claude 可以：创建 Spike 主 Issue / 添加和更新 Checklist / 添加 Spike 内部子任务 / 发布 S0—S6 进度 / 发布测试结果 / 发布 Finding / 关联 Commit / 关联 Draft PR / 更新 Current Readiness Recommendation。

Claude 暂时**不得**：创建完整 MVP Backlog / 创建正式业务 Epic / 创建 Fact Extraction 等生产实现 Issues / 将 Spike Issue 扩展为生产开发计划 / 关闭 Spike 主 Issue / 创建与 Spike 无关的 Issue。

**Spike Issue 只有在用户确认 Spike 完成或 Merge 对应 PR 后才允许关闭。**

---

## Draft Pull Request Contract

建议在 S0 完成并产生首个有效 Commit 后创建 Draft PR。建议标题：

```text
spike: validate LangGraph runtime and recovery architecture
```

Draft PR 至少包含：

```text
Objective
Related Decisions
Related Spike Issue
Stable Baseline
Temporary Stack
Scope
Non-goals
Scenario Checklist
Test Status
Evidence Artifacts
Spike Findings
Known Limitations
Current Readiness Recommendation
```

PR 可以关联：

```text
Closes #<spike-issue-number>
```

但 Issue 是否最终关闭仍由用户的 Merge 或明确决定控制。

### Pull Request Permission Boundary

Claude 可以：创建 Draft PR / 更新 PR 描述 / Push 阶段 Commit / 更新测试结果 / 更新 Scenario Checklist / 添加 Evidence Links / 回复 Review / 修复自己 Branch / 在 S6 完成后将 Draft PR 标记 Ready for Review。

Claude **不得**：Merge PR / 启用 Auto-merge / 自行 Approve / 绕过 Required Checks / Force Push / 删除 Branch / 更改 Base Branch / 隐藏失败 Scenario / 将 `NOT READY` 改写为 `READY`。

**Merge Spike PR 本身不等于 Architecture READY。**

---

## Commit Strategy

建议按 Spike 阶段保持可审查 Commit。概念 Commit 示例：

```text
chore(spike-001): bootstrap temporary runtime environment

feat(spike-001): implement normal workflow and review interrupt

test(spike-001): verify stale review and checkpoint rejection

feat(spike-001): add transactional commit and idempotency checks

test(spike-001): add retry fallback and cancellation scenarios

chore(spike-001): export runtime evidence and traces

docs(spike-001): publish spike report and readiness recommendation
```

每个 Commit 应：聚焦单一阶段或逻辑 / 使用清晰 Commit Message / 不包含 Secret / 不包含真实用户数据 / 不包含未经审查的大型二进制文件 / 尽可能在对应测试通过后创建 / 在 Issue 或 PR 中记录阶段结果。

Claude **不得**为了整理历史自行：Rebase / Amend 已 Push Commit / Squash 已共享 Commit。**最终是否采用 Squash Merge 由用户决定。**

---

## Generated Artifact Commit Rules

建议提交：Spike 源代码 / 测试代码 / `pyproject.toml` / Lockfile / Scenario Definitions / Sanitized Scenario Results / Test Summary / JSON Evidence / Spike Findings / Spike Report / Limitations / Readiness Recommendation。

默认**不得**提交：

```text
.spike-runs/**
.spike-data/**
*.sqlite
*.sqlite3
.env
.env.*
真实 Secret
完整原始模型响应
未脱敏用户数据
虚拟环境
缓存
临时日志
系统文件
```

应通过 `.gitignore` 排除。数据库运行证据应导出为可审查文件，例如：

```text
business-snapshot.json
checkpoint-summary.json
scenario-result.json
assertions.json
runtime-events.jsonl
```

**不得**默认提交 SQLite 二进制文件。

---

## Execution Stage Authorization

一次后续明确的正式 Execution Authorization 可以覆盖 S0—S6。Claude 不需要在每个阶段等待用户再次批准，但必须在以下 Gate 更新 Issue 和 PR：

```text
Gate A: Repository Audit completed
Gate B: S0 completed
Gate C: S2 completed
Gate D: S4 completed
Gate E: S6 completed
```

每次更新至少包括：已完成内容 / 当前 Commit SHA / 测试状态 / Scenario Pass / Fail / 新 Finding / 当前阻塞 / 下一阶段计划 / Scope 是否仍符合契约。

这些属于**进度与审计 Gate，不自动表示需要暂停。**

---

## Mandatory Stop Conditions

出现以下情况，Claude 必须**停止受影响工作并报告**。

### Decision Conflict

- 实现要求违反 Accepted DEC；
- Specs 与 DEC 无法调和；
- 两个 Accepted Decisions 出现冲突；
- 需要改变核心业务流程；
- 需要改变 Evidence 或 Human Review 边界。

### Scope Expansion

- 需要修改允许目录之外的生产代码；
- 需要建立正式 Domain Schema；
- 需要引入正式 API；
- 需要实现正式前端；
- 需要创建正式 Roadmap；
- 需要创建生产 Backlog；
- 需要实现自动发布。

### Version Conflict

- Python 3.13 无法满足依赖；
- LangGraph 1.2.9 无法安装；
- SqliteSaver 不支持所需行为；
- 必须改变已确认依赖版本；
- Checkpoint 安全设置无法满足。

### Repository Risk

- 存在不明未提交改动；
- Branch 与远程严重分叉；
- 出现 Merge Conflict；
- Remote 指向错误仓库；
- GitHub 登录身份不符合预期；
- Base Commit 与预期不一致。

### Secret or Data Risk

- 必选场景需要真实 API Key；
- 需要使用真实用户数据；
- Secret 可能进入 Git；
- Secret 可能进入 Trace；
- 需要执行外部 Side Effect。

### Architecture Blocking Failure

- Partial Write 无法避免；
- Retry 创建重复业务版本；
- Stale Review 可以提交；
- Stale Checkpoint 可以恢复；
- Resume 无法幂等；
- Checkpoint 会覆盖 Current Truth；
- Cancellation 留下中间业务状态；
- Recovery 必须绕过 Validator 才能继续。

**Claude 不得为了让测试「变绿」而掩盖或绕过这些问题。**

---

## Spike Finding Contract

每个重要发现必须形成结构化 Spike Finding。至少包括：

```text
Finding ID
Category
Scenario
Expected Behavior
Actual Behavior
Reproduction Steps
Relevant Commit
Relevant Trace
Root Cause Hypothesis
Implementation Bug or Architecture Risk
Affected Decisions
Affected Specifications
Candidate Options
Recommended Action
Execution Status
```

分类可以包括：

```text
implementation_bug
dependency_incompatibility
architecture_risk
decision_conflict
scope_change_required
non_blocking_limitation
```

如果 Finding 可能推翻 Accepted DEC：Claude 只能提交修订建议；**不得**修改 Decision；**不得**按未经确认的新方案继续；**必须**等待用户决定。

---

## Dependency Installation Failure

如果 `uv sync` 或依赖安装失败：

1. 保存脱敏错误输出；
2. 记录 Python 版本；
3. 记录操作系统；
4. 记录目标依赖版本；
5. 尝试一次不改变版本的可复现修复；
6. **不得**自行修改 LangGraph 版本；
7. 创建 Dependency Compatibility Finding；
8. 停止受影响阶段；
9. 向用户提交可选方案。

Claude 可以：删除并重建 Spike 自己的虚拟环境 / 修复明显包名错误 / 修复 Spike Lockfile / 重新执行隔离安装。

Claude **不得**：修改全局 Python / 卸载用户全局软件 / 使用管理员权限改变系统 / 静默切换依赖版本 / 修改项目其他环境。

---

## Codex Independent Review

Spike S6 完成后，可以单独授权 Codex 进行独立 Review。Codex 可审查：Spike Branch Diff / Test Results / Scenario Assertions / Trace Correlation / Transaction Evidence / Decision Compliance / Spike Findings / Readiness Recommendation。

Codex 可运行测试并提交 Review Report。Codex 默认**不得**修改 Claude Branch。如需 Codex 修复代码，必须另行明确授权，并避免两个 Agent 并发写入同一工作区。

---

## Readiness Recommendation

S6 完成后，Claude 可以提交：

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

推荐必须附带：Scenario 通过情况 / 阻塞 Findings / 非阻塞 Limitations / 可靠性结果 / Required RFC List / 允许启动的开发范围 / 禁止启动的开发范围。

Readiness Recommendation **不会自动**：更新 Development Status / 创建正式 Roadmap / 创建正式 Epics / 创建正式业务 Issues / Merge PR。

---

## Final Human Gate

用户最终负责：

1. 审查 Spike Issue；
2. 审查 PR Diff；
3. 查看测试结果；
4. 查看 Scenario Evidence；
5. 查看 Spike Findings；
6. 查看 Spike Report；
7. 查看 Codex 独立 Review，如有；
8. 决定是否 Merge PR；
9. 决定 Readiness 状态；
10. 决定是否进入 RFC 和 Roadmap。

只有用户明确确认：

```text
确认 Architecture READY
```

才可以更新：

```text
Architecture Readiness Status = READY
Development Status = READY
```

**Merge PR 不等于 READY。关闭 Spike Issue 不等于 READY。Claude Recommendation 不等于 READY。**

---

## Required Agent Handoff Inputs

Claude 正式执行前必须读取以下资料。

### Governance

```text
AGENTS.md
docs/agents/README.md
```

### Accepted Decisions

至少读取：

```text
DEC-023
DEC-024
DEC-029
DEC-032
DEC-033
DEC-034
DEC-035
DEC-036
```

必要时读取前置 Decision。

### Specifications

```text
docs/specs/workflow/human-review-and-approved-strategy-contract.md
docs/specs/runtime/hybrid-retrieval-and-evidence-runtime.md
docs/specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md
docs/specs/readiness/technical-spike-and-architecture-readiness-gate.md
docs/specs/readiness/technical-spike-execution-brief-and-temporary-stack.md
```

### Architecture

```text
docs/architecture/system-architecture.md
docs/architecture/data-architecture.md
docs/architecture/integration-boundaries.md
```

### Spike Documents

```text
docs/spikes/spike-001-langgraph-runtime-and-recovery/README.md
docs/spikes/spike-001-langgraph-runtime-and-recovery/spike-plan.md
docs/spikes/spike-001-langgraph-runtime-and-recovery/test-scenarios.md
docs/spikes/spike-001-langgraph-runtime-and-recovery/temporary-stack.md
docs/spikes/spike-001-langgraph-runtime-and-recovery/execution-brief.md
```

### GitHub Context

正式创建后还需读取：Spike Issue / Draft PR / Review Comments / Checks / 当前 Commit History。

**GitHub Issue 不能替代 Spec。PR 描述不能替代 Accepted Decision。**

---

## Contract Summary

```text
Decision:
DEC-036

Primary Execution Agent:
Claude Code

Optional Reviewer:
Codex

Claude May:
- Audit repository
- Create Spike Issue
- Create dedicated Branch
- Commit by stage
- Push Spike Branch
- Create and update Draft PR
- Run tests
- Publish evidence
- Respond to review
- Submit Readiness Recommendation

Claude May Not:
- Work directly on main
- Force push
- Rewrite shared history
- Merge PR
- Delete Branch
- Change repository permissions
- Modify Accepted Decisions
- Create production backlog
- Self-declare READY

User Retains:
- Scope approval
- Decision change authority
- Merge authority
- Architecture Readiness approval
```

---

## Reason

Spike-001 将涉及：依赖安装 / Branch / 多阶段 Commit / Fault Injection / 测试 / Issue / PR / Review / Readiness Recommendation。

如果不定义 Agent Git 和 GitHub 权限，可能产生：在 `main` 上直接开发 / 未经审查覆盖现有改动 / Force Push / 修改 Git 历史 / 自动 Merge / Agent 自己关闭 Issue / Spike 与正式开发混合 / 未通过 Gate 即创建生产 Backlog / Agent 自行宣布 READY。

因此必须采用：

```text
Agent-controlled mechanical workflow
+
User-controlled irreversible decisions
```

Claude 可以承担日常 Git 和 GitHub 操作，但不可逆、高风险和治理类操作继续由用户控制。

---

## Impact

该决定将影响：Claude Code 执行权限 / Codex Review 权限 / Repository Audit / Git Branch Strategy / Commit Strategy / GitHub Issue / Draft Pull Request / Review Workflow / Spike Findings / Readiness Recommendation / Merge Authority / Development Status Governance。

**不**改变 Development Status（保持 `NOT READY`）；**不**改变 Architecture Readiness Status（保持 `NOT READY`）；**不**改变 Spike Execution Status（保持 `NOT STARTED`）；**不**授予 Spike Execution Authorization（保持 `NOT GRANTED`）。

---

## Decision Boundary

本决定**已经确认**：Claude Code 是 Spike 主执行 Agent / Codex 是可选 Reviewer / Contract Authorization 与 Execution Authorization 分离 / Repository Audit / Stable Baseline / Dedicated Spike Branch / 安全 Git 操作 / GitHub Issue 操作 / Draft PR 操作 / 禁止 Force Push / 禁止 Merge / 禁止改写共享历史 / 禁止删除 Branch / 禁止修改仓库权限 / Spike Issue Contract / Issue 权限边界 / Draft PR Contract / PR 权限边界 / Commit Strategy / Generated Artifact Commit Rules / S0—S6 阶段更新 Gate / Mandatory Stop Conditions / Spike Finding Contract / Dependency Failure Handling / Codex Independent Review / Readiness Recommendation / Final Human Gate / Required Agent Handoff Inputs / 用户保留 Merge 和 READY 权限。

本决定**尚未确认**：立即启动 Spike / Baseline Commit SHA / 实际 Spike Issue 编号 / 实际 PR 编号 / GitHub Labels / GitHub Project / GitHub Actions / CI Provider / Codex 是否执行独立 Review / Reviewer 身份 / Merge Strategy / Spike PR 是否最终 Merge / Architecture Readiness 结果 / Development Status 是否变为 READY。

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
- DEC-035：Technical Spike Temporary Stack and Execution Contract。

## Related RFC

None

## Supersedes

None

## Amends

**DEC-034 and DEC-035** —— by defining the authorized execution agent, Git/GitHub workflow, repository boundaries and human approval gates for Spike-001.

> 本归档**不修改** DEC-034 / DEC-035 决定文件、其概念规格或其在 decision-log 中的行（历史记录保留不动）；Amends 关系仅记录于本 DEC-036 文件与 decision-log 的 DEC-036 行。DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 的历史记录同样保持不动。

---

## Notes

下一议题（尚未开始，需用户明确启动）：`Formal Spike-001 Execution Authorization`——需要明确：是否正式授权 Claude 开始执行 Spike / 是否先完成 Repository Audit / 是否允许 Claude 创建 Spike Issue / 是否允许 Claude 创建独立 Branch / 是否允许 Claude Push / 是否允许 Claude 创建 Draft PR / 是否一次授权覆盖 S0—S6 / 是否要求 Codex 在 S6 后进行独立 Review / 执行完成后用户需要审查哪些证据。

在用户明确授权前：

```text
Contract Authorization = ACCEPTED
Execution Authorization = NOT GRANTED
Spike Execution = NOT STARTED
Development Status = NOT READY
```
