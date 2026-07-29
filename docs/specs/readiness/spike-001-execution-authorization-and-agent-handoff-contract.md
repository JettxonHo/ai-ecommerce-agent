# Spike-001 Execution Authorization and Agent Handoff Contract（概念规格）

> **Status: CONCEPTUAL — 仅概念，非最终实现**
> **来源决定：** [../../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md](../../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md)（DEC-036，Accepted，2026-07-29；Agent Governance / Git and GitHub Operations / Spike Execution Authorization；Amends DEC-034 + DEC-035）
> **相关：** [../../agents/git-and-github-permissions.md](../../agents/git-and-github-permissions.md)（Git/GitHub 权限操作参考）；[../../spikes/spike-001-langgraph-runtime-and-recovery/](../../spikes/spike-001-langgraph-runtime-and-recovery/)（Spike 工作区）
> **本文件是概念层规格记录，不创建 Spike Branch / Issue / PR / 代码，不执行 Spike。**

---

## §0 定位

本规格把 DEC-036 的**执行授权契约**展开为概念层结构：授权层级 / Agent 角色 / Repository Audit / Stable Baseline / Dedicated Branch / Git 与 GitHub 操作边界 / Issue 与 PR 契约 / Commit 策略 / 阶段授权 Gate / Mandatory Stop Conditions / Spike Finding / 依赖失败处理 / Codex 独立 Review / Readiness Recommendation / Final Human Gate / 必需 Handoff 输入。

它回答的是：**Spike-001 由谁、在什么权限边界内、用什么 Git/GitHub 工作流执行，以及哪些不可逆决策保留给用户。** 它**不**授予执行授权（Execution Authorization 仍 `NOT GRANTED`），**不**定义 Spike 代码实现（实现属后续正式 Execution Authorization 之后的执行阶段）。

> **核心区分：** `Contract Authorization = ACCEPTED`（权限契约已接受）≠ `Execution Authorization = NOT GRANTED`（尚未授权实际启动 Spike）。

---

## §1 授权层级（Authorization Layers）

| 层级 | 含义 | 当前状态 |
|---|---|---|
| **Contract Authorization** | Claude Code 被允许在正式启动 Spike 后，按本契约管理 Spike Branch / Commits / Issue / Draft PR / 测试 / 证据。 | `ACCEPTED`（DEC-036） |
| **Execution Authorization** | 用户明确要求 Claude 实际创建 Branch / Issue / 代码 / 测试 / PR 并开始 S0—S6。 | `NOT GRANTED` |

DEC-036 被接受后 Spike 仍**不得自动启动**。正式启动需用户后续明确指令（如「正式授权执行 Spike-001」）。在该指令前：`Spike Execution Status = NOT STARTED` / `Architecture Readiness Status = NOT READY` / `Development Status = NOT READY`。

---

## §2 Agent 角色（Agent Roles）

### Claude Code — Primary Spike Execution Agent

```text
Primary Spike Execution Agent
Git Operator
GitHub Issue and PR Operator
Spike Evidence Producer
Readiness Recommendation Author
```

负责：Repository Audit / Spike Branch / Spike Issue / Draft PR / S0—S6 实现 / 自动化测试 / Fault Injection / Runtime Evidence / Spike Findings / Spike Report / Readiness Recommendation。

### Codex — Optional Independent Reviewer

可在获得单独任务后：审查 Spike Diff / 运行测试 / 核对 Scenario Assertions / 检查 DEC 与 Specs 一致性 / 审查 Spike Report / 提交独立 Review Report / 在 PR 中提出 Review 意见。

默认**不得**：与 Claude 同时修改同一 Branch / Push Claude Branch / Merge PR / 修改 Accepted DEC / 自行宣布 READY。

### User — Product Decision Owner

```text
Product Decision Owner
Architecture Readiness Approver
Merge Authority
```

保留：Scope 变化接受/拒绝 / DEC 修订接受/拒绝 / 审查 PR / 决定是否 Merge / 决定是否关闭 Spike Issue / 确认最终 Readiness 状态 / 确认 Development Status 是否 READY。

---

## §3 Repository Audit（只读，先于一切执行）

正式执行前 Claude 必须先做只读 Repository Audit，至少：

```bash
git status --short
git branch --show-current
git remote -v
git log --oneline --decorate -15
git diff --stat
git diff
gh auth status
```

并确认：Repository Root / 默认 Branch / 当前 Branch 及其远程跟踪 / 未提交改动 / 未跟踪文件 / 与项目无关的修改 / DEC-001~036 是否归档 / DEC-035·036 是否已进入稳定 Git 历史 / `.gitignore` 是否覆盖临时 Spike 数据 / 是否已存在 Spike Branch·Issue·PR / GitHub Remote 是否指向预期仓库 / `gh` 登录身份 / 创建 Issue·Push·PR 权限。

**输出 Repository Audit Report 后方可继续；存在未识别或可能冲突改动时不得覆盖。**

---

## §4 Stable Baseline

Spike Branch 从稳定 Git Commit 创建，Baseline 至少含 DEC-001~036 + Current Specs + Architecture Docs + Spike Plan + Test Scenarios + Temporary Stack + Execution Brief + Agent Handoff Contract。记录 `base_branch` / `base_commit_sha` / `created_at` / `created_by`。不从大量未提交改动工作区启动；DEC-036 未进默认 Branch 时先完成文档归档与 Git 流程。Claude 暂不自行创建正式 Git Tag。

---

## §5 Dedicated Spike Branch

```text
spike/001-langgraph-runtime-recovery
```

不在 `main` / `master` / `release/*` / `production/*` 直接开发。

允许修改：

```text
spikes/spike-001-langgraph-runtime-and-recovery/**
docs/spikes/spike-001-langgraph-runtime-and-recovery/**
```

经本契约允许还可更新（仅限 Spike Execution Status / Scenario Progress / Evidence Links / Findings / Readiness Recommendation / Known Limitations）：

```text
docs/readiness/**
docs/agents/README.md
```

不得修改 Accepted DEC 含义；不得把 Mock Schema 写成正式 Data Architecture。

---

## §6 Git 操作边界

### Authorized Local Git Operations

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

**Explicit Add Rule：** 优先明确路径；不默认 `git add .` / `git add -A`（确需使用须先完整审查 status 与 Diff 并确认全属当前任务）。

### Prohibited Git Operations（未经用户针对性授权）

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

不得：改写已 Push 共享历史 / 删除本地或远程 Branch / 强制覆盖远程 / 冲突时自行破坏性恢复 / 删除用户未提交工作 / 清理无法确认归属的未跟踪文件。需要时停止并说明：当前状态 / 风险 / 候选方案 / 推荐操作 / 受影响数据。

---

## §7 GitHub 操作边界

### Authorized GitHub Operations（Remote 正确且 `gh` 已认证）

```bash
gh issue create / view / comment / edit
gh pr create / view / checks / comment / edit
```

### Prohibited GitHub Operations（未经用户针对性授权）

```bash
gh pr merge
gh pr close
gh issue close
```

并禁止：启用 Auto-merge / 绕过失败 Checks / 自行批准自己的 PR / 删除 Review Comments / 删除远程 Branch / 修改 PR Base Branch / 修改 Branch Protection / 修改 Repository Visibility / 修改 Collaborator 权限 / 修改 GitHub Secrets / 创建或删除 Deploy Key / 修改 GitHub Actions 权限 / 删除用户创建的 Issue 或 PR / 修改 Repository Settings / 将 Spike PR 转为正式生产 Feature PR。

---

## §8 Spike Issue Contract

建议标题：`Spike-001: Validate LangGraph runtime, recovery and idempotency`。

- **Objective**：验证 DEC-023 / 024 / 029 / 032 / 033 / 034 / 035 / 036 相关高风险架构行为。
- **Scope**：S0—S6。
- **Required Scenarios**：Normal Workflow / Transient Retry / Invalid Structured Output / Transaction Rollback / Human Review Interrupt·Resume / Duplicate Review Submit / Stale Review Package / Stale Checkpoint / Retrieval Fallback / Cancellation / Retry Budget Exhaustion / Manual Recovery。
- **Deliverables**：Spike Code / Automated Tests / Scenario Results / Runtime Records / Trace Evidence / Transaction Evidence / Spike Findings / Spike Report / Required RFC List / Readiness Recommendation。
- **Non-goals**：Production Backend / Database / API / UI / Prompt / Retrieval / Deployment / MVP Roadmap / 正式业务 Backlog。

**Issue 权限边界：** Claude 可创建主 Issue / 更新 Checklist / 加子任务 / 发布进度 / 发布测试与 Finding / 关联 Commit·PR / 更新 Current Readiness Recommendation；暂不创建 MVP Backlog / 正式 Epic / 生产实现 Issues / 不扩展为生产计划 / 不关闭主 Issue / 不建无关 Issue。**Spike Issue 仅在用户确认完成或 Merge PR 后才允许关闭。**

---

## §9 Draft Pull Request Contract

S0 完成并产生首个有效 Commit 后创建 Draft PR，建议标题：`spike: validate LangGraph runtime and recovery architecture`。至少含：Objective / Related Decisions / Related Spike Issue / Stable Baseline / Temporary Stack / Scope / Non-goals / Scenario Checklist / Test Status / Evidence Artifacts / Spike Findings / Known Limitations / Current Readiness Recommendation。可关联 `Closes #<spike-issue-number>`，但 Issue 是否关闭由用户 Merge 或明确决定控制。

**PR 权限边界：** Claude 可创建 / 更新描述 / Push 阶段 Commit / 更新测试与 Checklist / 加 Evidence Links / 回复 Review / 修复自己 Branch / S6 后标 Ready for Review；**不得** Merge / Auto-merge / 自批 / 绕 Required Checks / Force Push / 删 Branch / 改 Base / 隐藏失败 Scenario / 把 `NOT READY` 改写为 `READY`。**Merge Spike PR ≠ Architecture READY。**

---

## §10 Commit 策略与产物提交规则

按阶段保持可审查 Commit（chore/feat/test/docs 前缀示例见 DEC-036）。每个 Commit 聚焦单一阶段 / 清晰 Message / 无 Secret / 无真实用户数据 / 无未审查大二进制 / 尽可能测试通过后创建 / 在 Issue 或 PR 记录阶段结果。**不得**为整理历史自行 Rebase / Amend 已 Push Commit / Squash 已共享 Commit；Squash Merge 由用户决定。

**建议提交：** Spike 源码 / 测试 / `pyproject.toml` / Lockfile / Scenario Definitions / Sanitized Results / Test Summary / JSON Evidence / Findings / Report / Limitations / Readiness Recommendation。
**默认不提交（经 `.gitignore` 排除）：** `.spike-runs/**` / `.spike-data/**` / `*.sqlite*` / `.env*` / 真实 Secret / 完整原始模型响应 / 未脱敏用户数据 / 虚拟环境 / 缓存 / 临时日志 / 系统文件。数据库运行证据导出为 `business-snapshot.json` / `checkpoint-summary.json` / `scenario-result.json` / `assertions.json` / `runtime-events.jsonl`；不默认提交 SQLite 二进制。

---

## §11 执行阶段授权与进度 Gate

一次正式 Execution Authorization 可覆盖 S0—S6；Claude 不必每阶段等待，但须在以下 Gate 更新 Issue 与 PR（进度与审计 Gate，不自动暂停）：

```text
Gate A: Repository Audit completed
Gate B: S0 completed
Gate C: S2 completed
Gate D: S4 completed
Gate E: S6 completed
```

每次更新含：已完成内容 / 当前 Commit SHA / 测试状态 / Scenario Pass·Fail / 新 Finding / 当前阻塞 / 下一阶段计划 / Scope 是否仍符合契约。

---

## §12 Mandatory Stop Conditions

出现以下情况必须停止受影响工作并报告（**不得**为让测试「变绿」而掩盖或绕过）：

- **Decision Conflict**：违反 Accepted DEC / Specs 与 DEC 无法调和 / 两个 DEC 冲突 / 需改核心业务流程 / 需改 Evidence 或 Human Review 边界。
- **Scope Expansion**：需改允许目录外生产代码 / 建正式 Domain Schema / 引入正式 API / 实现正式前端 / 建正式 Roadmap / 建生产 Backlog / 实现自动发布。
- **Version Conflict**：Python 3.13 无法满足依赖 / LangGraph 1.2.9 无法安装 / SqliteSaver 不支持 / 必须改已确认依赖版本 / Checkpoint 安全无法满足。
- **Repository Risk**：不明未提交改动 / Branch 与远程严重分叉 / Merge Conflict / Remote 指向错误 / `gh` 身份不符 / Base Commit 不符。
- **Secret or Data Risk**：必选场景需真实 API Key / 需真实用户数据 / Secret 可能进 Git 或 Trace / 需外部 Side Effect。
- **Architecture Blocking Failure**：Partial Write 无法避免 / Retry 创建重复业务版本 / Stale Review 可提交 / Stale Checkpoint 可恢复 / Resume 无法幂等 / Checkpoint 覆盖 Current Truth / Cancellation 留中间业务状态 / Recovery 须绕 Validator。

---

## §13 Spike Finding Contract

每个重要发现形成结构化 Finding：`Finding ID / Category / Scenario / Expected Behavior / Actual Behavior / Reproduction Steps / Relevant Commit / Relevant Trace / Root Cause Hypothesis / Implementation Bug or Architecture Risk / Affected Decisions / Affected Specifications / Candidate Options / Recommended Action / Execution Status`。

分类：`implementation_bug / dependency_incompatibility / architecture_risk / decision_conflict / scope_change_required / non_blocking_limitation`。

可能推翻 Accepted DEC 的 Finding：Claude 仅提交修订建议，不改 Decision、不按未确认新方案继续、等待用户决定。

---

## §14 Dependency Installation Failure

`uv sync` 或依赖安装失败时：保存脱敏错误输出 / 记录 Python 版本 / 操作系统 / 目标依赖版本 / 尝试一次不改版本的可复现修复 / **不得**自行改 LangGraph 版本 / 创建 Dependency Compatibility Finding / 停止受影响阶段 / 提交可选方案。

Claude 可：删除重建 Spike 自己的虚拟环境 / 修复明显包名错误 / 修复 Spike Lockfile / 重新隔离安装。**不得**：改全局 Python / 卸载用户全局软件 / 管理员权限改系统 / 静默切换依赖版本 / 改项目其他环境。

---

## §15 Codex Independent Review

S6 完成后可单独授权 Codex 独立 Review（Spike Branch Diff / Test Results / Scenario Assertions / Trace Correlation / Transaction Evidence / Decision Compliance / Spike Findings / Readiness Recommendation）。Codex 可运行测试并提交 Review Report；默认不改 Claude Branch；需 Codex 修复代码须另行明确授权并避免两 Agent 并发写同一工作区。

---

## §16 Readiness Recommendation

S6 后 Claude 提交 `RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`，附：Scenario 通过情况 / 阻塞 Findings / 非阻塞 Limitations / 可靠性结果 / Required RFC List / 允许启动的开发范围 / 禁止启动的开发范围。

**不会自动**：更新 Development Status / 创建正式 Roadmap / Epics / 业务 Issues / Merge PR。

---

## §17 Final Human Gate

用户最终负责：审查 Spike Issue / PR Diff / 测试结果 / Scenario Evidence / Spike Findings / Spike Report / Codex 独立 Review（如有）/ 决定是否 Merge PR / 决定 Readiness 状态 / 决定是否进入 RFC 和 Roadmap。

仅当用户明确确认「确认 Architecture READY」才可更新 `Architecture Readiness Status = READY` / `Development Status = READY`。

**Merge PR ≠ READY；关闭 Spike Issue ≠ READY；Claude Recommendation ≠ READY。**

---

## §18 Required Agent Handoff Inputs

- **Governance**：`AGENTS.md` / `docs/agents/README.md`。
- **Accepted Decisions**：至少 DEC-023 / 024 / 029 / 032 / 033 / 034 / 035 / 036（必要时前置 Decision）。
- **Specifications**：`docs/specs/workflow/human-review-and-approved-strategy-contract.md` / `docs/specs/runtime/hybrid-retrieval-and-evidence-runtime.md` / `docs/specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md` / `docs/specs/readiness/technical-spike-and-architecture-readiness-gate.md` / `docs/specs/readiness/technical-spike-execution-brief-and-temporary-stack.md`。
- **Architecture**：`docs/architecture/system-architecture.md` / `data-architecture.md` / `integration-boundaries.md`。
- **Spike Documents**：`docs/spikes/spike-001-langgraph-runtime-and-recovery/`（README / spike-plan / test-scenarios / temporary-stack / execution-brief）。
- **GitHub Context**（正式创建后）：Spike Issue / Draft PR / Review Comments / Checks / Commit History。

**GitHub Issue 不能替代 Spec；PR 描述不能替代 Accepted Decision。**

---

## §19 Decision Boundary

**已确认（本规格承接 DEC-036）：** Claude 主执行 / Codex 可选 Reviewer / 两种授权分离 / Repository Audit / Stable Baseline / Dedicated Branch / 安全 Git 操作 / Issue 与 Draft PR 操作 / 禁止 Force Push·Merge·改写历史·删 Branch·改仓库权限 / Issue·PR 权限边界 / Commit 策略 / 产物提交规则 / S0—S6 阶段 Gate / Mandatory Stop Conditions / Spike Finding / 依赖失败处理 / Codex 独立 Review / Readiness Recommendation / Final Human Gate / Handoff 输入 / 用户保留 Merge 与 READY 权。

**尚未确认：** 立即启动 Spike / Baseline Commit SHA / 实际 Issue·PR 编号 / GitHub Labels·Project·Actions / CI Provider / Codex 是否执行 Review / Reviewer 身份 / Merge Strategy / Spike PR 是否最终 Merge / Architecture Readiness 结果 / Development Status 是否 READY。

---

## §20 当前授权状态（不变）

```text
Contract Authorization = ACCEPTED
Execution Authorization = NOT GRANTED
Spike Execution Status = NOT STARTED
Architecture Readiness Status = NOT READY
Development Status = NOT READY
```

下一议题：`Formal Spike-001 Execution Authorization`。在用户明确授权前，不创建 Spike Branch / Issue / PR / 代码，不安装依赖，不运行测试，不启动 S0。
