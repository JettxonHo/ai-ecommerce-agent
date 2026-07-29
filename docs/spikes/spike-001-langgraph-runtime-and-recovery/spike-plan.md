# Spike-001 — Spike Plan

> **Status: PLANNED — NOT STARTED**
> **来源决定：** [DEC-034](../../decisions/dec-034-technical-spike-and-architecture-readiness-gate.md) · [DEC-035](../../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)
> **概念规格：** [../../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../../specs/readiness/technical-spike-and-architecture-readiness-gate.md) · [../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)
> **临时栈与执行简报：** [./temporary-stack.md](./temporary-stack.md) · [./execution-brief.md](./execution-brief.md)
> 本文件是**计划**，不是已执行结果。临时技术栈（语言 / 版本 / 执行模式 / 存储 / 事务 / Mock / Fault Injection / 测试 / Trace / Runner）已由 DEC-035 确认（详见 temporary-stack.md / execution-brief.md）；执行授权属下一议题 `Spike-001 Execution Authorization and Agent Handoff Contract`，**尚未确认**。

---

## 1. 目的（Objective）

用最小 Mock Workflow 验证已接受的架构（Workflow / State / Persistence / Human Review / Evidence / Retry / Recovery / Transaction / Observability）在最小代码环境中是否真正可运行。验证**架构行为**，不验证完整业务输出质量。

## 2. 验证目标（来自 DEC-034 §Architecture Risks Under Test）

至少验证 16 项架构风险：StateGraph 确定性 Compile/Invoke；Graph State 紧凑只存引用；Business Domain State 与 LangGraph Checkpoint 分离；Human Review Interrupt/Resume；Resume 不重复已完成 Node；Review Package 固定上游版本；旧 Review Package 被拒绝；Checkpoint 与 Current Truth 对账；旧 Checkpoint 被拒绝；Retry 不创建重复业务版本；事务失败完整回滚；Idempotency 防重复 Submit/Commit；Cancellation 不留部分业务状态；Retrieval Fallback 传播 Evidence Limitation；Structured Output Failure 不写入 Current Truth；Runtime Records/Logs/Trace 关联完整执行链。

## 3. 最小 Spike Workflow

```text
START → load_task_context → mock_fact_generation → validate_and_commit_facts
→ mock_insight_generation → validate_and_commit_insights
→ mock_positioning_generation → create_review_package
→ INTERRUPT: waiting_for_review
→ submit_review → commit_approved_strategy
→ mock_marketing_brief_generation → commit_marketing_brief → END
```

Xiaohongshu Adapter 非主路径硬要求；可加一个可选 Mock Adapter Node 验证 `Marketing Brief 修改 → Platform Mapping 失效`，但不得因此扩大范围。

## 4. Mock Business Objects（仅验证架构行为，非最终 Domain Schema）

- **Mock Facts**：商品名称 Mock 通勤杯 / 容量 500 mL / 重量 260 g / 材料 304 不锈钢。
- **Mock Insights**：Evidence-backed Insight（部分通勤用户担心漏水）；Hypothesis（通勤用户可能将轻量视为重要购买因素）。
- **Mock Positioning Candidates**：Candidate A 轻量通勤；Candidate B 密封安心（至少两个实质不同候选）。
- **Mock Approved Strategy**：Target Segment / Usage Context / Core Need / Value Proposition / Differentiation / Proof Points / Accepted Hypotheses / Evidence Limitations。
- **Mock Marketing Brief**：Audience / Core Message / Primary Benefit / Proof Points / Content Angles / Prohibited Claims / Evidence Limitations。

## 5. Spike Graph State（紧凑、引用导向）

```text
SpikeGraphState: task_id / thread_id / current_run_id / current_stage
/ fact_version_id / insight_version_id / positioning_version_id
/ review_id / approved_strategy_version_id / marketing_brief_version_id
/ waiting_reason / last_error_id / cancellation_requested
```

Graph State **不**保存完整 Facts/Insights/Positioning Candidates/Review Draft/Evidence Package/全部历史版本/完整文档或评论。正式业务内容必须从 Business Repository 读取。

## 6. Repository Separation（三类逻辑分离）

| 仓库 | 负责保存 |
|---|---|
| Business Repository | Task / Domain Versions / Current Truth Pointers / Stage State / Review Package / Strategy Draft / Approved Strategy / Marketing Brief / Evidence Links / Audit Records |
| Runtime Repository | Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error / Recovery Case / Idempotency Record / Cancellation Record |
| Checkpoint Store | LangGraph 执行状态 / Interrupt / Resume 位置 / 临时运行上下文 / Checkpoint Metadata |

Spike 采用三类**物理分离** SQLite（DEC-035）：`business.sqlite` / `runtime.sqlite` / `checkpoints.sqlite`（SqliteSaver 管理），直接验证 `Business State ≠ Runtime State ≠ Checkpoint State`。即使同一物理存储，也必须保持逻辑边界：`LangGraph Checkpoint Store ≠ Business Current Truth Repository`。

## 7. Fault Injection（可控、可重复）

概念配置（实现形式未确认）：

```text
FAIL_NODE_ON_ATTEMPT=1
FAIL_TRANSACTION_AT=evidence_link_commit
SEMANTIC_RETRIEVAL_AVAILABLE=false
FORCE_STALE_CHECKPOINT=true
FORCE_INVALID_STRUCTURED_OUTPUT=true
CANCEL_AFTER_NODE=mock_positioning_generation
```

要求：可重复 / 可自动化 / 可单独执行 / 可清除 / 不污染其他场景 / 能生成稳定预期结果。

## 8. 测试类型

- **Unit**：Error Classification / Input Fingerprint / Idempotency Key / Version Validation / Stage Invalidation / Retryability / Schema Validation / Checkpoint Staleness 判定。
- **Integration**：StateGraph 与 Checkpoint Store / Business Repository / Runtime Repository / Transaction Rollback / Interrupt·Resume / Review Submit / Checkpoint Reconciliation。
- **Failure Injection**：Transient Error / Timeout / Structured Output Error / Validation Error / Commit Failure / Cancellation / Stale Review / Stale Checkpoint / Retrieval Fallback / Retry Budget Exhaustion。
- **End-to-end**：执行完整 Mock Workflow，生成 Runtime Records / Business Versions / Checkpoints / Trace / Test Report。

## 9. 必备证据（不能只输出「测试成功」）

- **Test Results**：Scenario ID / 输入 / 故障注入条件 / 预期 / 实际 / Pass·Fail / 关联日志和 Trace。
- **Runtime Evidence**：完整链路 `Task → Workflow Run → Skill Run → Node Execution → Execution Attempts`。
- **State and Version Evidence**：Graph State / Domain Versions / Current Truth Pointers / Stage Status / Checkpoint Metadata。
- **Transaction Evidence**：失败前后 Domain Version 数 / Evidence Link 数 / Current Truth Pointer / Stage State / Audit Record（证明没有 Partial Write）。
- **Trace Evidence**：含 Retry / Fallback / Validator / Transaction / Interrupt / Resume / Checkpoint / Final Commit 的 Trace。
- **Limitations**：用了哪些 Mock / 未验证哪些生产能力 / 哪些结果不能推广到生产 / 哪些问题需要 RFC。

## 10. Spike 完成标准

全部完成才算结束：Spike Plan archived / Minimum Graph implemented / Required scenarios automated / Test results persisted / Runtime records inspectable / Transaction rollback evidence / Interrupt·Resume evidence / Stale Review passed / Stale Checkpoint passed / Idempotency passed / Cancellation passed / Trace correlation verified / Spike Report completed / Required RFC list completed / Readiness Recommendation completed。「代码成功运行一次」不构成完成。

## 11. Blocking Spike Failures

Duplicate Domain Version / Partial Business Write / Resume 覆盖 Current Truth / Stale Review 提交成功 / Stale Checkpoint Resume 成功 / Retry 与 Rerun 无法区分 / Review Resume 无法幂等 / Cancellation 留下中间业务状态 / Checkpoint 无法与业务版本对账 / Recovery 绕过 Validator / Trace 无法关联业务 Commit。

## 12. 临时技术栈已确认（DEC-035）/ 仍开放事项

**已由 DEC-035 确认（临时选择，不构成生产承诺）：** Spike 语言 = Python 3.13.x；LangGraph = 1.2.9（精确固定）；同步 StateGraph Invoke；包管理 = `uv`；三类物理分离 SQLite（business.sqlite / runtime.sqlite / checkpoints.sqlite，SqliteSaver 管理 Checkpoint）；严格 Checkpoint 反序列化；Python `sqlite3` 事务（统一 `BusinessCommitService`）；Review Package 创建与 Interrupt 分离节点；Scripted Deterministic Model（+ 可选 Real Model Smoke Test）；Mock Retrieval；Scenario-based FaultPlan；pytest；JSONL Local Trace（LocalTraceRecorder）；CLI Scenario Runner；Scenario Isolation；S0—S6 执行顺序；Spike Agent 权限与禁止事项；Secret 与数据边界；Scenario Result Contract；Automated Assertions。

**仍开放（留待下一议题 / 后续 RFC）：** Spike 具体执行时间 / **Spike 由 Claude 还是 Codex 主执行** / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号 / 以及所有生产技术（生产后端语言 / LangGraph 版本 / 同步或异步 / 数据库 / ORM / Checkpointer / API / Worker / Queue / Observability Provider / LLM / Retrieval / 部署平台）。

## 13. 何时执行

**当前不执行 Spike。** 临时技术栈已由 DEC-035 确认，但执行授权属下一议题 `Spike-001 Execution Authorization and Agent Handoff Contract`（Spike 主执行 Agent / 独立 Git Branch / 输入文件清单 / Repository Audit / 允许与禁止修改目录 / S0—S6 分阶段授权 / 每阶段证据 / 决策冲突停止 / 依赖安装失败处理 / Spike Finding 格式 / 自动 Commit / PR / 用户 Review Gate / Spike Report 人工验收 / 是否授权正式开始执行）。在该议题经用户确认前：**不**启动 Spike、**不**安装依赖、**不**创建 Spike 代码、**不**运行测试、不创建正式 Roadmap，Development Status 保持 `NOT READY`，Spike Execution Status 保持 `NOT STARTED`。
