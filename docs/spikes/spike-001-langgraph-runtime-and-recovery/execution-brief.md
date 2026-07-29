# Spike-001 Execution Brief

> **Status: IN PROGRESS（S0—S6 执行中）· Issue: [#1](https://github.com/JettxonHo/ai-ecommerce-agent/issues/1) · Branch: `spike/001-langgraph-runtime-recovery`**
> 来源决定：[DEC-035](../../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)
> 概念规格：[../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)
> 临时栈：[./temporary-stack.md](./temporary-stack.md)
> **本文件是规划性质记录，不创建 Spike 代码、不执行 Spike。**

---

## Spike Objective

在正式业务实现开始前，用最小、确定性、可检视、可复现、可抛弃的临时环境验证已接受架构的运行时行为（承接 DEC-034 的 16 项架构风险与 Architecture Readiness Gate），而**不**验证最终技术栈或业务质量。

验证目标：StateGraph 执行 / Interrupt·Resume / Checkpoint / 业务状态与执行状态分离 / Transaction Rollback / Idempotency / Retry / Stale Review / Stale Checkpoint / Retrieval Fallback / Cancellation / Manual Recovery / Trace Correlation。

最小化原则：

```text
Minimal
Deterministic
Local
Inspectable
Reproducible
Disposable
```

---

## Human Review Node Boundary

含 `interrupt()` 的 Node 在 Resume 时可能从 Node 开头重新执行，故 Review Package 创建与 Interrupt 必须拆成不同 Node。**禁止** `create_review_package` + `write_business_data` + `interrupt()` 同处一个 Node。

正式节点边界：

```text
create_review_package
↓
await_human_review
↓
load_approved_strategy
```

- **create_review_package**：读当前有效 Facts/Insights/Positioning Versions → 创建固定版本 Review Package → 原子提交 → 保存 `review_id` → 更新 Task Status / Stage Status → 写 Business Audit Record → 保持幂等。
- **await_human_review**：读 `review_id` → 验证 Review Package 当前有效 → 调 `interrupt()` → 输出 Review Reference → Interrupt 前**不**执行非幂等业务写入。
- **Review Submit**（独立业务事务）：Review Submit Request → Review Package Validation → Approved Strategy Commit → Current Truth Update → Audit Record。
- **Resume**：`Command(resume=review_submission_reference)`；保持原 `thread_id`；创建新 `run_id`；**不**重建 Review Package；**不**重生 Positioning Candidates；验证 Approved Strategy Current Truth；保持 Resume 幂等。

---

## Repository Responsibilities

三类物理分离（直接验证 `Business State ≠ Runtime State ≠ Checkpoint State`）：

- **business.sqlite**：Task / Stage State / Fact Version / Insight Version / Positioning Version / Review Package / Strategy Draft / Approved Strategy / Marketing Brief / Formal Evidence Links / Current Truth Pointers / Business Audit Records / Idempotency Records。**业务 Current Truth 唯一权威来源。** Checkpoint 不能覆盖或替代。
- **runtime.sqlite**：Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error / Recovery Case / Cancellation Record / Runtime Events / Trace Correlation Metadata。**不**保存正式业务 Current Truth。
- **checkpoints.sqlite**（LangGraph `SqliteSaver` 管理）：Graph Checkpoint / Thread State / Interrupt / Resume 位置 / Pending Writes / Checkpoint Metadata。**不**负责 Domain Version / Current Truth Pointer / Review Package / Approved Strategy / Formal Evidence Link / Business Audit。

> 上述 SQLite 仅属 Spike 实验存储，**不构成正式数据库设计**。

---

## Atomic Commit Contract

每次正式业务 Commit 在一个事务内完成：

```text
Create Domain Version
+
Create Formal Evidence Links
+
Update Current Truth Pointer
+
Update Stage State
+
Write Business Audit Record
+
Write Idempotency Record
```

任一失败：整体 Rollback / Pointer 不变 / Stage 不错误推进 / 无部分 Domain Version / 无部分 Evidence Link / 无错误成功 Audit / Retry 用同一逻辑幂等身份。Graph Node **不得**绕过 `BusinessCommitService` 分别写入。

---

## Fault Injection

显式 `FaultPlan`（scenario_id / target_component / target_operation / fail_on_attempts[] / failure_type / failure_payload / release_after_attempt / enabled）。示例：`spike-02-transient-retry` → `mock_insight_generation` → attempt 1 失败 `transient_infrastructure_error` → attempt 2 release。**禁止**业务代码散落 `if test_mode: raise Exception()`。

规则：默认关闭 / 只在 Spike Runtime 存在 / 可由 Scenario 启用 / 可重复 / 可单独运行 / 测试后自动清理 / 不依赖执行顺序 / 不污染其他 Scenario / 不进生产模块 / 不改 Accepted Business Contract。可用 pytest Fixtures / `monkeypatch` / `tmp_path` / `caplog`。

---

## Scenario Runner

CLI 统一入口：

```text
python -m spike_runtime run \
  --scenario spike-01-normal-workflow \
  --workspace .spike-runs/spike-01
```

Runner 14 步：创建隔离工作目录 → 初始化 Business Store → 初始化 Runtime Store → 初始化 Checkpoint Store → 写 Mock Sources → 初始化 Fault Plan → 执行 Graph → 模拟 Review Submit → Resume Graph → 导出业务状态 → 导出 Runtime Events → 导出 Checkpoint Summary → 运行 Automated Assertions → 生成 Scenario Result。

---

## Scenario Isolation

每 Scenario 独立目录 `.spike-runs/<scenario-id>/`，输出 business.sqlite / runtime.sqlite / checkpoints.sqlite / scenario-input.json / scenario-result.json / runtime-events.jsonl / trace.jsonl / business-snapshot.json / checkpoint-summary.json / assertions.json。**禁止**多 Scenario 共享可变数据库状态；每次可从空工作目录复现。

---

## Execution Stages S0—S6

- **S0 Environment and Skeleton**：Python 环境 / pyproject / Lockfile / StateGraph Compile / 三 SQLite Store / Runtime Identifiers / Scenario Runner / LocalTraceRecorder。退出 = Minimal Graph 可运行 + Runtime Record 可生成。
- **S1 Normal Workflow**：Mock Facts/Insights/Positioning / Review Package / Interrupt / Approved Strategy / Marketing Brief。执行 Spike-01。退出 = Current Truth 正确 + Graph 正确暂停恢复 + Trace 完整。
- **S2 Human Review and Version Safety**：Interrupt·Resume / Duplicate Submit / Stale Review / Stale Checkpoint。退出 = 旧 Review 无法提交 + 旧 Checkpoint 无法推进 + Resume 幂等 + Positioning 不重生。
- **S3 Transaction and Idempotency**：Transaction Rollback / Commit Retry / Duplicate Commit / Current Truth Pointer Validation。退出 = Partial Business Write Rate = 0% + Duplicate Business Version Rate = 0%。
- **S4 Failure and Recovery**：Transient Retry / Structured Output Failure / Retrieval Fallback / Cancellation / Retry Budget Exhaustion / Recovery Case。退出 = 每种处置有结构化 Runtime Evidence + 无无限重试 + Recovery 不绕 Validator。
- **S5 Observability and Evidence Export**：Runtime Records / JSONL Trace / Business Snapshot / Checkpoint Summary / Scenario Result / JUnit XML。退出 = 每 Scenario 独立重现 + 所有关键 ID 可关联 + Automated Assertions 可运行。
- **S6 Report and Recommendation**：implementation-notes / test-results / runtime-evidence / limitations / spike-report / Required RFC List / Readiness Recommendation。**S6 不得自动改变 Development Status。**

---

## Spike Agent Permissions

Spike Agent **可**：创建和修改 `spikes/spike-001-*`；更新对应 `docs/spikes/spike-001-*`；创建本地临时 SQLite；安装 Spike Lockfile 中依赖；执行测试；运行 Scenario Runner；创建 Evidence Artifacts；创建 Spike Finding；提交 Readiness Recommendation；建议 RFC；建议修订未接受的实现细节。

---

## Spike Agent Prohibitions

Spike Agent **不得**：修改 Accepted DEC 含义；修改正式业务 Specs 业务边界；将 Spike Schema 写成正式 Data Architecture；创建正式业务 Graph；创建生产目录；生成 MVP Roadmap；生成正式开发 Epics；创建正式 GitHub Issues；将 Development Status 改为 READY；选择生产数据库/Checkpointer/Observability Provider；引入自动发布；使用真实用户数据；执行外部 Side Effect；将可选真实模型测试作为 Readiness 必选条件；将 Spike 代码直接迁移到生产模块。

---

## Secret Boundary

必选场景默认无需真实 API Key（Mock Product / Mock Reviews / Scripted Model / Mock Retrieval / Local SQLite / Local Trace）。可选 Real Model Smoke Test 必须：环境变量注入 Secret / Secret **不**写入文件·日志·Trace·Git / 无 Secret 自动 Skip / **不**用真实客户或用户数据。

---

## Required Deliverables

- **Spike Code**：`spikes/spike-001-langgraph-runtime-and-recovery/`。
- **Automated Tests**：unit / integration / failure_injection / e2e / optional_external。
- **Evidence**：Scenario Results / Runtime Records / Business Snapshots / Checkpoint Summaries / JSONL Traces / Transaction Rollback Evidence / Idempotency Evidence / Recovery Case Evidence。
- **Documentation**：README / spike-plan / test-scenarios / temporary-stack / execution-brief（本归档已创建）+ 执行阶段产物 implementation-notes / test-results / runtime-evidence / limitations / spike-report（执行阶段创建，本归档**不创建**）。
- **Recommendation**：`RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`（仅建议）。

---

## Result Acceptance Boundary

Scenario **不得**只依赖 Agent 自然语言判断。每场景必须同时提供：

```text
Automated Assertion
+
Runtime Evidence
+
Human-readable Explanation
```

只有自然语言「看起来成功」**不**算 Pass。Automated Assertions 示例：approved_strategy_version_count == 1 / current_truth_pointer == expected_version / invalid_evidence_link_count == 0 / stale_checkpoint_resume_success == false / transaction_partial_write_count == 0 / duplicate_business_version_count == 0。

---

> **Status: PLANNED — NOT STARTED（执行授权已授予，尚未开始）。** 执行授权契约已由 **DEC-036（Accepted，2026-07-29）** 确认：Primary Execution Agent = **Claude Code**，Optional Independent Reviewer = **Codex**；正式执行前先做只读 **Repository Audit**；使用 Dedicated Branch `spike/001-langgraph-runtime-recovery` + Stage Commits + Spike Issue + Draft PR；遵循 Mandatory Stop Conditions；Merge / READY 属 **Final Human Gate**（`Merge PR ≠ READY`）。**正式执行授权已由 DEC-037（Accepted，2026-07-30）授予**：`Contract Authorization = ACCEPTED` / `Execution Authorization = GRANTED`——Claude 已被允许执行 Spike-001 S0—S6，但这**不表示** Spike 已开始或已通过。执行的第一动作仍是**只读 Repository Audit**，且在 Audit 与稳定文档基线通过前**不**安装依赖、**不**创建 Spike 代码 / Branch / Issue / PR、**不**运行测试、**不**初始化 SQLite、**不**启动 S0。`Spike Execution Status = NOT STARTED`（须待实际开始 Repository Audit 后才可更新为 `IN PROGRESS`）、`Architecture Readiness Status = NOT READY`、`Development Status = NOT READY`。下一动作为 **`Spike-001 Execution Handoff`**（归档进入稳定 Git 基线后以独立任务执行；第一步必须是只读 Repository Audit）。
