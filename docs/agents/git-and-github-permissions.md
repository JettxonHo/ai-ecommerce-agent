# Git and GitHub Permissions（DEC-036 / DEC-037 操作参考）

> **Status: Operational Reference — 权限与操作边界参考**
> **来源决定：** [../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md](../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md)（DEC-036，Accepted，2026-07-29；Agent Governance / Git and GitHub Operations / Spike Execution Authorization；Amends DEC-034 + DEC-035）· [../decisions/dec-037-formal-spike-001-execution-authorization.md](../decisions/dec-037-formal-spike-001-execution-authorization.md)（DEC-037，Accepted，2026-07-30；Execution Authorization / Agent Governance / GitHub Workflow；Amends DEC-034 + DEC-035 + DEC-036）
> **概念规格：** [../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md](../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md) · [../specs/readiness/formal-spike-001-execution-authorization.md](../specs/readiness/formal-spike-001-execution-authorization.md)
> **适用范围：** Spike-001（`spike/001-langgraph-runtime-recovery` Branch）及相关 Git / GitHub 操作。
> **本文件是权限边界参考，不创建 Spike Branch / Issue / PR / 代码，不执行 Spike，不运行 Repository Audit。**

---

## §0 定位

本文件把 DEC-036 的 Git/GitHub 权限与操作边界整理为可直接查阅的**操作参考**：谁能做什么、哪些操作安全、哪些操作被禁止、哪些不可逆决策保留给用户。核心治理模式：

```text
Agent-controlled mechanical workflow
+
User-controlled irreversible decisions
```

Claude Code 承担日常 Git/GitHub 机械操作；**不可逆、高风险、治理类决策继续由用户控制。**

> **两种授权分离与激活：** `Contract Authorization = ACCEPTED`（DEC-036，权限契约已接受）；`Execution Authorization = GRANTED`（DEC-037，已正式授权 Claude 执行 Spike-001 S0—S6）。但 `GRANTED` ≠ 已开始执行 —— **第一动作仍是只读 Repository Audit**，且在 Audit 与稳定文档基线通过前，任何写入 / 安装 / Spike 代码 / Branch / PR 均不开始。详见文末 §14 与「§15 DEC-037 执行授权激活」。

---

## §1 Agent Roles

| 角色 | 身份 | 职责 |
|---|---|---|
| **Primary Spike Execution Agent** | Claude Code | Git Operator / GitHub Issue and PR Operator / Spike Evidence Producer / Readiness Recommendation Author |
| **Optional Independent Reviewer** | Codex | 单独授权后审查 Diff / 测试 / Scenario Assertions / DEC 一致性 / Spike Report / 提交独立 Review Report |
| **Product Decision Owner** | User | 接受/拒绝 Scope 变化与 DEC 修订 / 审查 PR / 决定 Merge / 决定关闭 Spike Issue / 确认最终 Readiness / 确认 Development Status |

---

## §2 Safe Git Operations

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

**Explicit Add Rule：** 优先明确路径（如 `git add spikes/spike-001-langgraph-runtime-and-recovery`）；不默认 `git add .` / `git add -A`（确需使用须先完整审查 `git status` 与 Diff 并确认全属当前任务）。

Claude 可：创建受控 Spike Branch / 切换 Spike Branch / 查看本地与远程差异 / 按阶段组织 Commit / Commit 前运行测试 / Push 自己负责的 Branch / 根据 Review 修改自己 Branch / Push 修复 Commit / 报告 Commit SHA。

---

## §3 Prohibited Git Operations

未经用户针对性授权，禁止：

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

并禁止：改写已 Push 共享 Commit 历史 / 删除本地或远程 Branch / 强制覆盖远程 Branch / 冲突时自行破坏性恢复 / 删除用户未提交工作 / 清理无法确认归属的未跟踪文件。

需要上述操作时，必须停止并说明：当前状态 / 风险 / 候选方案 / 推荐操作 / 受影响数据。

---

## §4 Authorized GitHub Operations

GitHub Remote 正确且 `gh` 已认证时，可执行：

```bash
gh issue create / view / comment / edit
gh pr create / view / checks / comment / edit
```

Claude 可：创建 Spike-001 主 Issue / 更新 Issue 描述与 Checklist / 记录阶段进度 / 发布测试摘要 / 记录 Spike Finding / 关联 Commit 与 PR / 创建与更新 Draft PR / 查看 PR Checks / 回复 Review Comments / 修复自己 Branch / Push 修复 Commit / S6 完成后将 Draft PR 标 Ready for Review / 请求用户 Review。

---

## §5 Prohibited GitHub Operations

未经用户针对性授权，禁止：

```bash
gh pr merge
gh pr close
gh issue close
```

并禁止：启用 Auto-merge / 绕过失败 Checks / 自行批准自己的 PR / 删除 Review Comments / 删除远程 Branch / 修改 PR Base Branch / 修改 Branch Protection / 修改 Repository Visibility / 修改 Collaborator 权限 / 修改 GitHub Secrets / 创建或删除 Deploy Key / 修改 GitHub Actions 权限 / 删除用户创建的 Issue 或 PR / 修改 Repository Settings / 将 Spike PR 转为正式生产 Feature PR。

---

## §6 Branch Rules

```text
Dedicated Spike Branch: spike/001-langgraph-runtime-recovery
```

- **禁止直接开发：** `main` / `master` / `release/*` / `production/*`。
- **主要允许修改：** `spikes/spike-001-langgraph-runtime-and-recovery/**` / `docs/spikes/spike-001-langgraph-runtime-and-recovery/**`。
- **经契约允许还可更新（仅限 Spike Execution Status / Scenario Progress / Evidence Links / Findings / Readiness Recommendation / Known Limitations）：** `docs/readiness/**` / `docs/agents/README.md`。
- **Stable Baseline：** 从含 DEC-001~036 + Specs + Architecture + Spike 文档的稳定 Commit 创建；记录 `base_branch` / `base_commit_sha` / `created_at` / `created_by`；不从大量未提交改动工作区启动；Claude 暂不自行创建 Git Tag。
- 不得修改 Accepted DEC 含义；不得把 Mock Schema 写成正式 Data Architecture。

---

## §7 Commit Rules

- 按 Spike 阶段保持**可审查** Commit（`chore/` `feat/` `test/` `docs/` 前缀，单一阶段聚焦，清晰 Message）。
- 每个 Commit：无 Secret / 无真实用户数据 / 无未审查大二进制 / 尽可能测试通过后创建 / 在 Issue 或 PR 记录阶段结果。
- **建议提交：** Spike 源码 / 测试 / `pyproject.toml` / Lockfile / Scenario Definitions / Sanitized Results / Test Summary / JSON Evidence / Findings / Report / Limitations / Readiness Recommendation。
- **默认不提交（经 `.gitignore` 排除）：** `.spike-runs/**` / `.spike-data/**` / `*.sqlite*` / `.env*` / 真实 Secret / 完整原始模型响应 / 未脱敏用户数据 / 虚拟环境 / 缓存 / 临时日志 / 系统文件。
- 数据库运行证据导出为可审查 JSON（`business-snapshot.json` / `checkpoint-summary.json` / `scenario-result.json` / `assertions.json` / `runtime-events.jsonl`）；不默认提交 SQLite 二进制。
- **不得**为整理历史自行 Rebase / Amend 已 Push Commit / Squash 已共享 Commit；Squash Merge 由用户决定。

---

## §8 Issue Rules

- 一个主要 Spike Issue，建议标题：`Spike-001: Validate LangGraph runtime, recovery and idempotency`。
- **Claude 可：** 创建主 Issue / 更新 Checklist / 添加 Spike 内部子任务 / 发布 S0—S6 进度 / 发布测试与 Finding / 关联 Commit 与 Draft PR / 更新 Current Readiness Recommendation。
- **Claude 暂不：** 创建完整 MVP Backlog / 正式业务 Epic / Fact Extraction 等生产实现 Issues / 将 Spike Issue 扩展为生产开发计划 / 关闭 Spike 主 Issue / 创建与 Spike 无关的 Issue。
- **关闭边界：** Spike Issue 仅在用户确认 Spike 完成或 Merge 对应 PR 后才允许关闭。
- **GitHub Issue 不能替代 Spec。**

---

## §9 PR Rules

- S0 完成并产生首个有效 Commit 后创建 **Draft PR**，建议标题：`spike: validate LangGraph runtime and recovery architecture`。
- Draft PR 至少含：Objective / Related Decisions / Related Spike Issue / Stable Baseline / Temporary Stack / Scope / Non-goals / Scenario Checklist / Test Status / Evidence Artifacts / Spike Findings / Known Limitations / Current Readiness Recommendation。
- 可关联 `Closes #<spike-issue-number>`，但 Issue 是否关闭由用户 Merge 或明确决定控制。
- **Claude 可：** 创建 Draft PR / 更新描述 / Push 阶段 Commit / 更新测试结果与 Scenario Checklist / 添加 Evidence Links / 回复 Review / 修复自己 Branch / S6 后标 Ready for Review。
- **Claude 不得：** Merge PR / Auto-merge / 自批 / 绕 Required Checks / Force Push / 删 Branch / 改 Base / 隐藏失败 Scenario / 把 `NOT READY` 改写为 `READY`。
- **PR 描述不能替代 Accepted Decision。Merge Spike PR ≠ Architecture READY。**

---

## §10 Merge Authority

- **Merge Authority = User。** Claude 不得 Merge PR、不得启用 Auto-merge、不得绕过失败 Checks、不得自行批准自己的 PR。
- 用户审查 Spike Issue / PR Diff / 测试结果 / Scenario Evidence / Spike Findings / Spike Report / Codex 独立 Review（如有）后，决定是否 Merge。
- **Merge PR ≠ READY；关闭 Spike Issue ≠ READY；Claude Recommendation ≠ READY。**

---

## §11 Mandatory Stop Conditions

出现以下情况必须停止受影响工作并报告（不得为让测试「变绿」而掩盖或绕过）：

- **Decision Conflict**：违反 Accepted DEC / Specs 与 DEC 无法调和 / 两个 DEC 冲突 / 需改核心业务流程 / 需改 Evidence 或 Human Review 边界。
- **Scope Expansion**：需改允许目录外生产代码 / 建正式 Domain Schema / 引入正式 API / 实现正式前端 / 建正式 Roadmap / 建生产 Backlog / 实现自动发布。
- **Version Conflict**：Python 3.13 无法满足依赖 / LangGraph 1.2.9 无法安装 / SqliteSaver 不支持 / 必须改已确认依赖版本 / Checkpoint 安全无法满足。
- **Repository Risk**：不明未提交改动 / Branch 与远程严重分叉 / Merge Conflict / Remote 指向错误 / `gh` 身份不符 / Base Commit 不符。
- **Secret or Data Risk**：必选场景需真实 API Key / 需真实用户数据 / Secret 可能进 Git 或 Trace / 需外部 Side Effect。
- **Architecture Blocking Failure**：Partial Write 无法避免 / Retry 创建重复业务版本 / Stale Review 可提交 / Stale Checkpoint 可恢复 / Resume 无法幂等 / Checkpoint 覆盖 Current Truth / Cancellation 留中间业务状态 / Recovery 须绕 Validator。

---

## §12 Secret Boundary

- 任何 Secret / 真实 API Key / 真实用户数据**不得**进入 Git 提交、Trace、Issue、PR 或模型响应。
- `.env*` / 真实 Secret / 完整原始模型响应 / 未脱敏用户数据**默认不提交**，经 `.gitignore` 排除。
- 必选场景若需真实 API Key / 真实用户数据 / 外部 Side Effect → 触发 **Secret or Data Risk** Mandatory Stop Condition。
- Secret 可能进入 Git 或 Trace 时 → 立即停止并报告。

---

## §13 Readiness Authority

- **Readiness Recommendation Author = Claude Code**（`RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`）。
- **Architecture Readiness Approver = User。** 仅当用户明确确认「确认 Architecture READY」才可更新 `Architecture Readiness Status = READY` / `Development Status = READY`。
- Readiness Recommendation **不会自动**更新 Development Status / 创建正式 Roadmap / Epics / 业务 Issues / Merge PR。
- **Agent Recommendation ≠ READY。**

---

## §14 当前授权状态（已由 DEC-037 更新）

```text
Contract Authorization = ACCEPTED
Execution Authorization = GRANTED
Spike Execution Status = NOT STARTED
Architecture Readiness Status = NOT READY
Development Status = NOT READY
```

下一动作：`Spike-001 Execution Handoff`（归档进入稳定 Git 基线后以独立任务执行；第一步必须是只读 Repository Audit）。在归档完成并进入稳定 Git 基线前，不创建 Spike Branch / Issue / PR / 代码，不安装依赖，不运行测试，不启动 S0。

---

## §15 DEC-037 执行授权激活（Execution Authorization Activation）

DEC-037（Accepted，2026-07-30）正式把 `Execution Authorization` 从 `NOT GRANTED` 转为 **`GRANTED`**，允许 Claude Code 作为 Spike-001 Primary Execution Agent 从规划与归档阶段进入实际仓库执行阶段。本节记录激活后的**执行顺序与额外边界**；§1—§13 的角色、操作白名单与禁止项**保持不变**，继续有效。

### §15.1 授权状态迁移

| 层级 | DEC-036 后 | DEC-037 后 |
|---|---|---|
| Contract Authorization | `ACCEPTED` | `ACCEPTED`（不变） |
| Execution Authorization | `NOT GRANTED` | **`GRANTED`** |
| Spike Execution Status | `NOT STARTED` | `NOT STARTED`（实际开始 Repository Audit 后才可更新为 `IN PROGRESS`） |
| Architecture Readiness Status | `NOT READY` | `NOT READY`（不变） |
| Development Status | `NOT READY` | `NOT READY`（不变） |

`Execution Authorization = GRANTED` **不表示**：Repository Audit 已完成 / Spike 已开始 / Spike 已通过 / Architecture 已 READY / Development 已 READY。

### §15.2 授权仓库与执行流程

```text
Repository: /Users/ketchup/Projects/AI Ecommerce Agent
Primary Execution Agent: Claude Code
Optional Independent Reviewer: Codex

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

一次授权覆盖 S0—S6；Claude 不必每阶段重新授权，但须守 **Execution Gates A—E**（A Repository Audit / B S0 / C S2 / D S4 / E S6 更新 Issue + PR，进度与审计 Gate 不自动暂停）与 **Mandatory Stop Conditions**（§11，DEC-037 重述为 6 类：Decision Conflict / Scope Expansion / Repository Risk / Dependency Conflict / Architecture Blocking Failure / Data or Secret Risk）。

### §15.3 First Required Action — 只读 Repository Audit

Claude 的第一项执行操作**必须**是只读 Repository Audit（命令见 DEC-037 / DEC-036 §Repository Audit）。**须先形成 Repository Audit Report**；Audit 完成前**不得**安装依赖 / 创建 Spike 代码 / 初始化数据库 / 运行 Spike / 创建 Spike Branch / 创建 Draft PR。

- **Audit Pass** → Create Spike Issue → Create Dedicated Branch → Begin S0。
- **Audit Blocked** → 停止并报告 `Audit Finding / Current Repository State / Blocking Risk / Recommended Resolution / Safe Next Actions`；**不得**覆盖、删除、Reset 或隐藏现有修改。

### §15.4 Stable Documentation Baseline 与 Documentation PR

Spike Branch 须基于含 **DEC-001~037** + Current Specs + Architecture Documents + Spike Plan + Test Scenarios + Temporary Stack + Execution Brief + Git and GitHub Permissions + Agent Handoff Contract + Formal Execution Authorization 的稳定 Commit，记录 `base_branch` / `base_commit_sha` / `created_at` / `created_by`。若 DEC-037 尚未进入稳定默认 Branch，须先创建**文档基线 Branch**（如 `docs/session-002-spike-governance`，仅含 DEC-035/036/037 / Decision Log / Agent Permissions / Spike Planning Documents / Readiness Status / 必要 Architecture 同步），经 `Documentation Branch → Commit → Push → Documentation PR → Stop for User Review`；**用户 Merge 文档 PR 后才创建 Spike Branch。不得从大量未提交文件的工作区直接开始 Spike。**

### §15.5 Isolated Dependency Authorization 与 Version Compatibility Boundary

Audit 与 Spike Branch 创建后，Claude 获准在隔离目录 `spikes/spike-001-langgraph-runtime-and-recovery` 内 `uv sync` / `pytest` / `python -m spike_runtime ...`（创建 Spike 虚拟环境 / 安装 Lockfile 依赖 / 创建本地临时 SQLite / 运行 Scenario Runner / 执行 Tests / 生成 Evidence）。**不得**修改系统全局 Python / 管理员权限安装 / 卸载用户全局软件 / 修改项目其他环境 / 静默更换 LangGraph 版本 / 把 Spike 依赖加入生产依赖。已接受临时组合 = **Python 3.13 / LangGraph 1.2.9 / Compatible pinned langgraph-checkpoint-sqlite**；无法安装或支持关键行为时只允许检查配置包名错误→重建隔离环境→不改版本重试一次→保存脱敏错误→创建 Dependency Compatibility Finding→停止受影响阶段→提交候选方案，**不得自行**升级/降级 LangGraph、更换 Python、更换 Checkpointer 或切换其他 Workflow Framework。

### §15.6 S6 Completion Boundary 与 User Authority

完成 S6 后 Claude 必须**停止**，可提交 `RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`，但**不得** Merge PR / 关闭 Spike Issue / 更新 Architecture Readiness 为 READY / 更新 Development Status 为 READY / 创建 MVP Roadmap / 正式 Epics / 正式 Business Issues / 启动生产开发。S6 后状态：`Spike Execution Status = COMPLETED` / `Architecture Readiness Status = PENDING USER REVIEW` / `Development Status = NOT READY`。用户继续保留 Decision 修订 / Scope 批准 / PR Merge / Issue Closure / Git 历史危险操作批准 / Architecture READY 确认 / Development Status 变更权；**PR Merge ≠ READY；Issue Closed ≠ READY；Agent Recommendation ≠ READY。**
