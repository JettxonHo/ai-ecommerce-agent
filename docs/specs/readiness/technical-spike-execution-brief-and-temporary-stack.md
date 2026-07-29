# Technical Spike Execution Brief and Temporary Stack — 概念 Specification

> **Status: CONCEPTUAL（概念）**
> 来源决定：[DEC-035 — Technical Spike 临时采用 Python、同步 LangGraph StateGraph、分离式 SQLite 存储、确定性 Mock 与场景化故障注入执行契约](../../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)。Amends DEC-034。
> 本文件是 DEC-035 的**概念结构化记录**，**不是最终实现契约**，也**不是**生产技术选型。所有具体实现细节仍可由授权 Spike Agent 在职责边界内调整；所有生产技术决策仍待后续 RFC。
> **Development Status: NOT READY。Spike Execution Status: NOT STARTED。**

---

## §0 目的

为 `Spike-001：LangGraph Runtime and Recovery` 提供明确、可复现、确定性的**临时执行环境与操作边界**，用于验证已接受架构的运行时行为（承接 DEC-034 的 16 项架构风险与 Architecture Readiness Gate）。本规格定义**临时栈**（temporary stack）与**执行简报**（execution brief）两层内容。

- **Spike 验证的是 Required Architecture Behavior，而不是 Final Production Infrastructure。**
- **所有临时选择都不构成生产承诺。**

---

## §1 临时技术栈摘要（Temporary Stack Summary）

| 维度 | 临时选择 |
| --- | --- |
| Spike | Spike-001 LangGraph Runtime and Recovery |
| 临时语言 | Python 3.13.x |
| 临时编排 | LangGraph StateGraph 1.2.9 |
| 临时执行 | Synchronous Invoke |
| 临时业务存储 | SQLite — business.sqlite |
| 临时运行时存储 | SQLite — runtime.sqlite |
| 临时 Checkpoint 存储 | LangGraph SqliteSaver — checkpoints.sqlite |
| 临时事务层 | Python sqlite3 |
| 临时模型 | Scripted deterministic provider |
| 临时检索 | Mock Direct / Lexical / Semantic provider |
| 测试 | pytest |
| 故障注入 | Scenario-based FaultPlan |
| 可观测性 | Structured JSONL events and LocalTraceRecorder |
| 接口 | CLI Scenario Runner |
| 生产承诺 | None |

该栈只验证：StateGraph 执行 / Interrupt·Resume / Checkpoint / 业务状态与执行状态分离 / Transaction Rollback / Idempotency / Retry / Stale Review / Stale Checkpoint / Retrieval Fallback / Cancellation / Manual Recovery / Trace Correlation。

---

## §2 临时语言（Language）

临时使用 Python 3.13.x。理由仅限：便于快速验证 LangGraph Runtime / 标准库具有 SQLite 和事务能力 / 便于使用 pytest 进行故障注入 / Spike 不需要验证浏览器或正式前端 / 可将 Graph·Repository·Fault Injection·Test 集中在独立实验目录。

**不**表示生产后端必须使用 Python（仍需后续 RFC 确认）。

---

## §3 依赖版本策略与变更边界（Dependency Version Strategy + Version Change Boundary）

直接依赖必须精确固定（`pyproject.toml` 声明 + Lockfile + 不用浮动 `latest` + Spike 期间不自动升级 + Spike Report 记录完整依赖版本 + 运行证据关联依赖版本 + 版本调整形成 Spike Finding）。临时包管理工具采用 `uv`（**不**自动成为生产构建/部署工具）。

Spike Agent **不得**擅自将 LangGraph 1.2.9 替换为其他版本。遇到无法安装 / Python 3.13 不兼容 / SqliteSaver 不兼容 / Interrupt 行为与预期不一致 / 依赖严重缺陷 / 安全配置无法满足时，必须：停止相关场景 → 创建 Spike Finding → 记录版本·错误·复现步骤 → 说明候选替代版本 → 判断是否影响 DEC-023 / DEC-034 / DEC-035 → 提交变更建议 → 等待用户确认后再修改决策基线。**不能静默升级或降级。**

---

## §4 LangGraph 执行模式（Execution Mode）

主验证路径：`StateGraph + Synchronous Invoke`。暂**不**以 Async Graph / Worker / Queue 为主路径（减少 Event Loop / Async Repository / 并发事务 / 分布式 Worker / Queue Retry / Async Cancellation 对核心架构验证的干扰）。

**不**表示生产系统必须使用同步运行（生产 Sync / Async / Worker / Queue / Background Execution 仍需后续 RFC 决定）。

---

## §5 物理存储分离（Physical Storage Separation）

三个独立 SQLite 文件直接验证 `Business State ≠ Runtime State ≠ Checkpoint State`：

```text
.spike-data/
├── business.sqlite
├── runtime.sqlite
└── checkpoints.sqlite
```

- **business.sqlite**：Task / Stage State / Fact Version / Insight Version / Positioning Version / Review Package / Strategy Draft / Approved Strategy / Marketing Brief / Formal Evidence Links / Current Truth Pointers / Business Audit Records / Idempotency Records。**业务 Current Truth 的唯一权威来源。** Checkpoint 不能覆盖或替代。
- **runtime.sqlite**：Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error / Recovery Case / Cancellation Record / Runtime Events / Trace Correlation Metadata。**不**保存正式业务 Current Truth。
- **checkpoints.sqlite**（SqliteSaver 管理）：Graph Checkpoint / Thread State / Interrupt / Resume 位置 / Pending Writes / Checkpoint Metadata。**不**负责 Domain Version / Current Truth Pointer / Review Package / Approved Strategy / Formal Evidence Link / Business Audit。

未来生产即使使用同一数据库实例，也必须保持逻辑职责分离。

> 上述 SQLite 仅属 Spike 实验存储，**不构成正式数据库设计**。

---

## §6 Checkpoint 安全（Checkpoint Security）

必须启用严格 Checkpoint 反序列化边界（`LANGGRAPH_STRICT_MSGPACK=true` 或语义等价的显式安全配置）。Graph State 只保存简单、明确、允许的类型；**不**保存任意 Python 对象 / Secret / 完整业务文档 / 不必要模型输出；**不**允许任意模块反序列化；Spike Report 记录实际安全配置。版本不支持时必须创建 Spike Finding，**不**静默忽略。

---

## §7 事务层与原子提交契约（Transaction Layer + Atomic Commit）

使用 Python `sqlite3`（暂**不**用 ORM）以直接观察 Begin / Domain Version Insert / Evidence Link Insert / Pointer Update / Stage Update / Audit Insert / Idempotency Insert / Commit / Rollback。所有正式业务写入经统一 `BusinessCommitService`（概念接口：`commit_fact_version()` / `commit_insight_version()` / `commit_review_package()` / `commit_approved_strategy()` / `commit_marketing_brief()`）。

每次正式 Commit 在一个事务内完成：Create Domain Version + Create Formal Evidence Links + Update Current Truth Pointer + Update Stage State + Write Business Audit Record + Write Idempotency Record。任一失败整体 Rollback（Pointer 不变 / Stage 不错误推进 / 无部分 Domain Version / 无部分 Evidence Link / 无错误成功 Audit / Retry 用同一逻辑幂等身份）。Graph Node **不得**绕过 `BusinessCommitService` 分别写入。

---

## §8 模型策略（Model Strategy）

Readiness 必选场景默认使用 `ScriptedModelProvider`（按 Scenario ID / Node / Attempt Number / Fault Plan 返回确定性结果），用于保证可重复 / 控制 Structured Output Failure / 控制 Retry / 控制 Validator Failure / 避免真实模型随机性影响 Readiness 结论。

允许独立可选 `Spike-Optional-01 Real Model Structured Output Smoke Test`（仅验证 Model Adapter 可调用 / 输出进相同 Schema Validator / Token·Latency Metadata 可记录 / Provider Error 进 Runtime Error Contract / 模型失败不绕过 Validator）。该场景：**不**属 READY 必选 / **不**替代 Scripted Tests / **不**验证业务输出质量 / 无 API Key 自动 Skip / **不**影响必选 Scenario / **不**用真实用户数据。

---

## §9 检索策略（Retrieval Strategy）

使用 `MockRetrievalRuntime`（`direct_read()` / `lexical_search()` / `semantic_search()` / `build_evidence_package()`）+ 固定 Mock Fragment（容量 500 mL / 重量 260 g / 通勤漏水顾虑 / 密封表现认可）。保留 Fragment ID / Source Scope / Product Identity / Source Version / Retrieval Channel / Retrieval Run ID / Evidence Limitation。

`semantic_available = false` 时走 Direct Read + Lexical → Evidence Package with Limitation，必须验证不扩大 Source Scope / 不用竞品补当前商品 / Retrieval Run 记 Fallback / Evidence Package 记限制 / 下游 `succeeded_with_limitations` / 用户可见限制存在。Spike **不**实现 Embedding / Vector Database / Rank Fusion / Top-K / Reranker / Production Retrieval Index。

---

## §10 测试框架（Test Framework）

pytest，分类 unit / integration / failure_injection / e2e / optional_external，对应 Marker。结果导出 `artifacts/test-results/`（junit.xml / pytest-summary.txt / scenario-results.json）。

---

## §11 可观测性（Observability）

**不**选正式 Provider（LangSmith / OpenTelemetry / Datadog / Grafana / Jaeger / Sentry 全部不引入）。使用 `LocalTraceRecorder`，每 Scenario 输出 `artifacts/traces/<scenario-id>.jsonl`，事件含 event / timestamp / task_id / thread_id / run_id / skill_run_id / node_execution_id / attempt_id / trace_id / checkpoint_id / error_category / fallback / transaction_status。

Trace 必须支持回答：Node 起止 / 哪个 Attempt 失败 / Retry 是否同 Node / Resume 是否同 Thread / Resume 是否新 Run / 用了哪个输入版本 / 哪个 Validator 拒绝 / 哪个事务成功或回滚 / 是否 Fallback / 用了哪个 Checkpoint / 创建了哪个 Domain Version / 是否创建 RecoveryCase。

---

## §12 生产承诺边界（Production Commitment Boundary）

| Temporary Spike Choice | Does Not Mean |
| --- | --- |
| Python 3.13 | Production backend must use Python |
| LangGraph 1.2.9 | Production permanently uses this version |
| Sync Invoke | Production cannot use Async |
| SQLite | Production uses SQLite |
| SqliteSaver | Production checkpoint backend is SQLite |
| Python sqlite3 | Production cannot use an ORM |
| JSONL Trace | Production will not use OpenTelemetry |
| CLI Runner | Final product uses CLI |
| Scripted Model | Final system does not use real LLMs |
| Mock Retrieval | Final system does not use vector retrieval |
| Three SQLite files | Production requires three physical databases |

---

## §13 Human Review 节点边界

含 `interrupt()` 的 Node 在 Resume 时可能从 Node 开头重新执行，故 Review Package 创建与 Interrupt 必须拆成不同 Node。**禁止** `create_review_package` + `write_business_data` + `interrupt()` 同处一个 Node。

正式节点边界：

```text
create_review_package
↓
await_human_review
↓
load_approved_strategy
```

- **create_review_package**：读当前有效 Facts/Insights/Positioning Versions → 创建固定版本 Review Package → 原子提交 → 保存 `review_id` → 更新 Task/Stage Status → 写 Business Audit → 保持幂等。
- **await_human_review**：读 `review_id` → 验证 Review Package 当前有效 → 调 `interrupt()` → 输出 Review Reference → Interrupt 前**不**执行非幂等业务写入。
- **Review Submit**：Review Submit Request → Review Package Validation → Approved Strategy Commit → Current Truth Update → Audit Record（独立业务事务）。
- **Resume**：`Command(resume=review_submission_reference)`；保持原 `thread_id`；创建新 `run_id`；**不**重建 Review Package；**不**重生 Positioning Candidates；验证 Approved Strategy Current Truth；保持 Resume 幂等。

---

## §14 Repository 职责

（见 §5：Business Store / Runtime Store / Checkpoint Store 三类物理分离与各自职责。）

---

## §15 故障注入（Fault Injection）

显式 `FaultPlan`（scenario_id / target_component / target_operation / fail_on_attempts[] / failure_type / failure_payload / release_after_attempt / enabled）。**禁止**业务代码散落 `if test_mode: raise Exception()`。

规则：默认关闭 / 只在 Spike Runtime 存在 / 可由 Scenario 启用 / 可重复 / 可单独运行 / 测试后自动清理 / 不依赖执行顺序 / 不污染其他 Scenario / 不进生产模块 / 不改 Accepted Business Contract。可用 pytest Fixtures / `monkeypatch` / `tmp_path` / `caplog`。

---

## §16 Scenario Runner 与 Scenario 隔离

CLI 统一入口 `python -m spike_runtime run --scenario <id> --workspace .spike-runs/<id>`（14 步：创建隔离工作目录 → 初始化三 Store → 写 Mock Sources → 初始化 Fault Plan → 执行 Graph → 模拟 Review Submit → Resume → 导出业务状态 / Runtime Events / Checkpoint Summary → 运行 Automated Assertions → 生成 Scenario Result）。

每 Scenario 独立目录，输出 business.sqlite / runtime.sqlite / checkpoints.sqlite / scenario-input.json / scenario-result.json / runtime-events.jsonl / trace.jsonl / business-snapshot.json / checkpoint-summary.json / assertions.json。**禁止**多 Scenario 共享可变数据库状态；每次可从空工作目录复现。

---

## §17 执行阶段 S0—S6

- **S0 Environment and Skeleton**：Python 环境 / pyproject / Lockfile / StateGraph Compile / 三 SQLite Store / Runtime Identifiers / Scenario Runner / LocalTraceRecorder。退出 = Minimal Graph 可运行 + Runtime Record 可生成。
- **S1 Normal Workflow**：Mock Facts/Insights/Positioning / Review Package / Interrupt / Approved Strategy / Marketing Brief。执行 Spike-01。退出 = Current Truth 正确 + Graph 正确暂停恢复 + Trace 完整。
- **S2 Human Review and Version Safety**：Interrupt·Resume / Duplicate Submit / Stale Review / Stale Checkpoint。退出 = 旧 Review 无法提交 + 旧 Checkpoint 无法推进 + Resume 幂等 + Positioning 不重生。
- **S3 Transaction and Idempotency**：Transaction Rollback / Commit Retry / Duplicate Commit / Current Truth Pointer Validation。退出 = Partial Business Write Rate = 0% + Duplicate Business Version Rate = 0%。
- **S4 Failure and Recovery**：Transient Retry / Structured Output Failure / Retrieval Fallback / Cancellation / Retry Budget Exhaustion / Recovery Case。退出 = 每种处置有结构化 Runtime Evidence + 无无限重试 + Recovery 不绕 Validator。
- **S5 Observability and Evidence Export**：Runtime Records / JSONL Trace / Business Snapshot / Checkpoint Summary / Scenario Result / JUnit XML。退出 = 每 Scenario 独立重现 + 所有关键 ID 可关联 + Automated Assertions 可运行。
- **S6 Report and Recommendation**：implementation-notes / test-results / runtime-evidence / limitations / spike-report / Required RFC List / Readiness Recommendation。**S6 不得自动改变 Development Status。**

---

## §18 Spike Agent 权限与禁止事项

**可**：创建和修改 `spikes/spike-001-*`；更新对应 `docs/spikes/spike-001-*`；创建本地临时 SQLite；安装 Lockfile 中依赖；执行测试；运行 Scenario Runner；创建 Evidence Artifacts；创建 Spike Finding；提交 Readiness Recommendation；建议 RFC；建议修订未接受的实现细节。

**不得**：修改 Accepted DEC 含义；修改正式业务 Specs 业务边界；将 Spike Schema 写成正式 Data Architecture；创建正式业务 Graph；创建生产目录；生成 MVP Roadmap；生成正式开发 Epics；创建正式 GitHub Issues；将 Development Status 改为 READY；选择生产数据库/Checkpointer/Observability Provider；引入自动发布；使用真实用户数据；执行外部 Side Effect；将可选真实模型测试作为 Readiness 必选条件；将 Spike 代码直接迁移到生产模块。

---

## §19 Secret 与数据边界

必选场景默认无需真实 API Key（Mock Product / Mock Reviews / Scripted Model / Mock Retrieval / Local SQLite / Local Trace）。可选 Real Model Smoke Test 必须：环境变量注入 Secret / Secret 不写入文件·日志·Trace·Git / 无 Secret 自动 Skip / **不**用真实客户或用户数据。

---

## §20 必需交付物与结果接受边界

**Required Deliverables**：Spike Code / Automated Tests（unit / integration / failure_injection / e2e / optional_external）/ Evidence（Scenario Results / Runtime Records / Business Snapshots / Checkpoint Summaries / JSONL Traces / Transaction Rollback Evidence / Idempotency Evidence / Recovery Case Evidence）/ Documentation（README / spike-plan / test-scenarios / temporary-stack / execution-brief + 执行阶段产物 implementation-notes / test-results / runtime-evidence / limitations / spike-report）。

**Result Acceptance Boundary**：Scenario **不得**只依赖 Agent 自然语言判断；每场景必须同时提供 Automated Assertion + Runtime Evidence + Human-readable Explanation。只有自然语言「看起来成功」**不**算 Pass。

**Scenario Result Contract**：scenario_id / scenario_version / status / expected_outcome / actual_outcome / assertions[] / fault_plan / runtime_ids / input_version_ids / output_version_ids / checkpoint_ids / errors[] / fallbacks[] / artifact_paths[] / started_at / completed_at / dependency_versions。Automated Assertions 示例：approved_strategy_version_count == 1 / current_truth_pointer == expected_version / invalid_evidence_link_count == 0 / stale_checkpoint_resume_success == false / transaction_partial_write_count == 0 / duplicate_business_version_count == 0。

---

## §21 建议（Recommendation）

Spike 结束后输出 `RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`（仅建议，承接 DEC-034 Readiness Decision Authority：Architecture Agent 提交 Recommendation，Product Decision Owner 明确确认最终状态）。

---

## §22 Contract Summary

```text
Decision: DEC-035
Spike: Spike-001 LangGraph Runtime and Recovery
Temporary Stack:
- Python 3.13
- LangGraph 1.2.9
- Synchronous StateGraph Invoke
- Three separated SQLite stores
- SqliteSaver
- Python sqlite3 transactions
- Scripted deterministic model
- Mock retrieval
- Scenario-based FaultPlan
- pytest
- JSONL local trace
- CLI scenario runner
Hard Rules:
- Temporary choices are not production decisions
- Review package creation and interrupt use separate nodes
- Business, runtime and checkpoint stores remain separate
- Required scenarios do not depend on a real LLM
- Every result requires automated assertions and runtime evidence
- Spike Agent cannot self-declare READY
```

---

## Open Questions（如实记录，不捏造）

尚未确认：Production Backend Language / Production LangGraph Version / Production Async Model / Production Database / Production ORM / Production Checkpointer / API Framework / Worker Framework / Queue / OpenTelemetry / LangSmith / Logging Provider / Tracing Provider / Real LLM Provider / Embedding Model / Vector Database / Deployment Platform / Spike 具体执行时间 / **Spike 由 Claude 还是 Codex 主执行** / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号。

下一议题（尚未开始，需用户明确启动）：`Spike-001 Execution Authorization and Agent Handoff Contract`。在 **Spike-001 Execution Authorization and Agent Handoff Contract** 议题确认前：**不**启动 Spike；**不**安装依赖；**不**创建 Spike 代码；**不**运行测试；**不**创建正式 Roadmap；Development Status 保持 `NOT READY`。
