# DEC-035：Technical Spike 临时采用 Python、同步 LangGraph StateGraph、分离式 SQLite 存储、确定性 Mock 与场景化故障注入执行契约

> **Status: Accepted**
> **Date: 2026-07-29**
> **Type: Technical Spike Execution / Temporary Architecture / Validation Environment**
> **Related Session: Session-002**
> **Supersedes: None**
> **Amends: DEC-034**（为 Spike-001 定义可执行的临时技术栈与 Spike Agent 操作边界）
> **Development Status: NOT READY**
> **Spike Execution Status: NOT STARTED**

---

## 用户确认

用户于 2026-07-29 对 **Technical Spike Execution Brief and Temporary Spike Stack** 议题明确回复：

> 确认形成 DEC-035

通过 Decision Gate。本决定为 **Accepted Decision**，归档为 DEC-035。

---

## Core Decision

`Spike-001：LangGraph Runtime and Recovery` 临时采用以下技术组合：

```text
Python 3.13
+
Precisely pinned LangGraph 1.2.9
+
Synchronous StateGraph Invoke
+
Separated SQLite Stores
+
LangGraph SqliteSaver
+
Python sqlite3 Transactions
+
Scripted Deterministic Model
+
Mock Retrieval Runtime
+
Scenario-based Fault Injection
+
pytest
+
Local JSONL Trace
+
CLI Scenario Runner
```

该技术栈只用于验证：

- StateGraph 执行；
- Interrupt / Resume；
- Checkpoint；
- 业务状态与执行状态分离；
- Transaction Rollback；
- Idempotency；
- Retry；
- Stale Review；
- Stale Checkpoint；
- Retrieval Fallback；
- Cancellation；
- Manual Recovery；
- Trace Correlation。

**它不构成任何生产技术承诺。**

---

## Temporary Stack Summary

```text
Spike:
Spike-001 LangGraph Runtime and Recovery
Temporary Language:
Python 3.13.x
Temporary Orchestration:
LangGraph StateGraph 1.2.9
Temporary Execution:
Synchronous Invoke
Temporary Business Store:
SQLite — business.sqlite
Temporary Runtime Store:
SQLite — runtime.sqlite
Temporary Checkpoint Store:
LangGraph SqliteSaver — checkpoints.sqlite
Temporary Transaction Layer:
Python sqlite3
Temporary Model:
Scripted deterministic provider
Temporary Retrieval:
Mock Direct / Lexical / Semantic provider
Testing:
pytest
Fault Injection:
Scenario-based FaultPlan
Observability:
Structured JSONL events and LocalTraceRecorder
Interface:
CLI Scenario Runner
Production Commitment:
None
```

---

## Temporary Language

Spike 临时使用：

```text
Python 3.13.x
```

选择 Python 的理由仅限于：

- 便于快速验证 LangGraph Runtime；
- 标准库具有 SQLite 和事务能力；
- 便于使用 pytest 进行故障注入；
- Spike 不需要验证浏览器或正式前端；
- 可以将 Graph、Repository、Fault Injection 和 Test 集中在独立实验目录。

该决定**不**表示：

```text
Production Backend must use Python
```

生产后端语言仍需后续 RFC 确认。

---

## Temporary Dependency Strategy

直接依赖必须精确固定。建议 Spike 基线：

```text
Python = 3.13.x
LangGraph = 1.2.9
langgraph-checkpoint-sqlite = compatible pinned version
pytest = pinned stable version
```

必须满足：

- 在 `pyproject.toml` 中声明直接依赖；
- 生成并提交 Lockfile；
- 不使用浮动 `latest`；
- Spike 执行期间不自动升级依赖；
- Spike Report 记录完整依赖版本；
- 运行证据必须关联依赖版本；
- 版本调整必须形成 Spike Finding。

临时包管理工具采用：

```text
uv
```

用于：

- 创建 Python 环境；
- 安装依赖；
- 生成 Lockfile；
- 执行测试；
- 提供可复现运行入口。

`uv` **不**自动成为生产构建或部署工具。

---

## Version Change Boundary

Spike Agent **不得**擅自将：

```text
LangGraph 1.2.9
```

替换为其他版本。若出现以下情况：

- 无法安装；
- Python 3.13 不兼容；
- SqliteSaver 不兼容；
- Interrupt 行为与预期不一致；
- 依赖存在严重缺陷；
- 安全配置无法满足；

必须：

1. 停止相关场景；
2. 创建 Spike Finding；
3. 记录当前版本、错误和复现步骤；
4. 说明候选替代版本；
5. 判断是否影响 DEC-023、DEC-034 或 DEC-035；
6. 提交变更建议；
7. 等待用户确认后再修改决策基线。

**不能静默升级或降级。**

---

## LangGraph Execution Mode

Spike 主验证路径采用：

```text
StateGraph
+
Synchronous Invoke
```

暂**不**以 Async Graph、Worker 或 Queue 为主路径。

同步模式用于减少以下因素对核心架构验证的干扰：

- Event Loop；
- Async Repository；
- 并发事务；
- 分布式 Worker；
- Queue Retry；
- Async Cancellation。

该选择**不**表示生产系统必须使用同步运行。生产系统是否采用 Sync / Async / Worker / Queue / Background Execution 仍需后续 RFC 决定。

---

## Human Review Node Boundary

由于包含 `interrupt()` 的 Node 在 Resume 时可能从 Node 开头重新执行，因此 Review Package 创建与 Interrupt 必须拆成不同 Node。

**禁止**：

```text
create_review_package
write_business_data
interrupt()
```

全部放在同一个 Node 中。

正式 Spike 节点边界：

```text
create_review_package
↓
await_human_review
↓
load_approved_strategy
```

### create_review_package

负责：

- 读取当前有效 Facts、Insights 和 Positioning Versions；
- 创建固定版本的 Review Package；
- 原子提交 Review Package；
- 保存 `review_id`；
- 更新 Task Status；
- 更新 Stage Status；
- 写入 Business Audit Record；
- 保持幂等。

### await_human_review

负责：

- 读取已创建的 `review_id`；
- 验证 Review Package 当前有效；
- 调用 LangGraph `interrupt()`；
- 输出用户需要处理的 Review Reference；
- **不**在 Interrupt 前执行非幂等业务写入。

### Review Submit

Review Submit 应通过独立业务事务完成：

```text
Review Submit Request
↓
Review Package Validation
↓
Approved Strategy Commit
↓
Current Truth Update
↓
Audit Record
```

### Resume

Approved Strategy 已经成功提交后，使用：

```text
Command(resume=review_submission_reference)
```

恢复 Graph。恢复时：

- 保持原 `thread_id`；
- 创建新的 `run_id`；
- **不**重新创建 Review Package；
- **不**重新生成 Positioning Candidates；
- 必须验证 Approved Strategy Current Truth；
- 必须保持 Resume 幂等。

---

## Temporary Physical Storage Separation

Spike 使用三个独立 SQLite 文件：

```text
.spike-data/
├── business.sqlite
├── runtime.sqlite
└── checkpoints.sqlite
```

该物理分离用于直接验证：

```text
Business State
≠
Runtime State
≠
Checkpoint State
```

---

## Business Store

临时文件：

```text
business.sqlite
```

至少保存：

- Task；
- Stage State；
- Fact Version；
- Insight Version；
- Positioning Version；
- Review Package；
- Strategy Draft；
- Approved Strategy；
- Marketing Brief；
- Formal Evidence Links；
- Current Truth Pointers；
- Business Audit Records；
- Idempotency Records。

**Business Store 是 Spike 中业务 Current Truth 的唯一权威来源。** Checkpoint **不能**覆盖或替代 Business Store。

---

## Runtime Store

临时文件：

```text
runtime.sqlite
```

至少保存：

- Workflow Run；
- Skill Run；
- Node Execution；
- Execution Attempt；
- Runtime Error；
- Recovery Case；
- Cancellation Record；
- Runtime Events；
- Trace Correlation Metadata。

**Runtime Store 不保存正式业务 Current Truth。**

---

## Checkpoint Store

临时文件：

```text
checkpoints.sqlite
```

由 LangGraph `SqliteSaver` 管理。只用于：

- Graph Checkpoint；
- Thread State；
- Interrupt；
- Resume 位置；
- Pending Writes；
- Checkpoint Metadata。

Checkpoint Store **不**负责：

- Domain Version；
- Current Truth Pointer；
- Review Package；
- Approved Strategy；
- Formal Evidence Link；
- Business Audit。

正式边界：

```text
business.sqlite
≠
runtime.sqlite
≠
checkpoints.sqlite
```

未来生产环境即使使用同一个数据库实例，也必须保持逻辑职责分离。

---

## Checkpoint Security

Spike 必须启用严格的 Checkpoint 反序列化边界。至少应：

```text
LANGGRAPH_STRICT_MSGPACK=true
```

或使用语义等价的显式安全配置。要求：

- Graph State 只保存简单、明确、允许的类型；
- **不**在 Checkpoint 中保存任意 Python 对象；
- **不**保存 Secret；
- **不**保存完整业务文档；
- **不**保存不必要的模型输出；
- **不**允许任意模块反序列化；
- Spike Report 记录实际安全配置。

若当前版本不支持预期配置，必须创建 Spike Finding，**不能**静默忽略。

---

## Temporary Transaction Layer

Spike 使用：

```text
Python sqlite3
```

暂**不**使用 ORM。这样可以直接观察：

- Transaction Begin；
- Domain Version Insert；
- Evidence Link Insert；
- Current Truth Pointer Update；
- Stage State Update；
- Audit Insert；
- Idempotency Insert；
- Commit；
- Rollback。

所有正式业务写入必须经过统一：

```text
BusinessCommitService
```

概念接口至少包括：

```text
commit_fact_version()
commit_insight_version()
commit_review_package()
commit_approved_strategy()
commit_marketing_brief()
```

---

## Atomic Commit Contract

每次正式业务 Commit 必须在一个事务内完成：

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

任一步失败：

- 整体 Rollback；
- Current Truth Pointer 不变化；
- Stage State 不错误推进；
- **不**留下部分 Domain Version；
- **不**留下部分 Evidence Link；
- **不**记录错误的成功 Audit；
- Retry 使用同一逻辑幂等身份。

Graph Node **不得**绕过 `BusinessCommitService` 分别写入这些对象。

---

## Scripted Deterministic Model

所有 Readiness 必选场景默认使用：

```text
ScriptedModelProvider
```

它根据：

- Scenario ID；
- Node；
- Attempt Number；
- Fault Plan；

返回确定性结果。概念行为：

```text
normal
→ valid structured output
invalid_json / attempt 1
→ malformed JSON
invalid_json / attempt 2
→ valid structured output
invalid_fact_reference
→ structured output with unknown fact_id
persistent_failure
→ transient error for every attempt
```

使用 Deterministic Model 的目的：

- 保证测试可重复；
- 控制 Structured Output Failure；
- 控制 Retry；
- 控制 Validator Failure；
- 避免真实模型随机性影响 Readiness 结论。

---

## Optional Real Model Smoke Test

允许添加独立可选场景：

```text
Spike-Optional-01:
Real Model Structured Output Smoke Test
```

该场景仅验证：

- Model Adapter 能调用；
- 输出进入相同 Schema Validator；
- Token 和 Latency Metadata 可以记录；
- Provider Error 能进入 Runtime Error Contract；
- 模型失败不会绕过 Validator。

该场景：

- **不**属于 READY 必选条件；
- **不**能替代 Scripted Model Tests；
- **不**验证业务输出质量；
- 无 API Key 时必须自动 Skip；
- **不**允许影响必选 Scenario 结果；
- **不**允许使用真实用户数据。

---

## Mock Retrieval Runtime

Spike 使用：

```text
MockRetrievalRuntime
```

概念接口：

```text
direct_read()
lexical_search()
semantic_search()
build_evidence_package()
```

使用固定 Mock Fragment：

```text
Fragment-001:
商品容量为 500 mL。
Fragment-002:
商品重量为 260 g。
Fragment-003:
用户担心将水杯放入通勤包时漏水。
Fragment-004:
部分用户认可密封表现。
```

Mock Retrieval 必须保留：

- Fragment ID；
- Source Scope；
- Product Identity；
- Source Version；
- Retrieval Channel；
- Retrieval Run ID；
- Evidence Limitation。

---

## Retrieval Degraded Mode

配置：

```text
semantic_available = false
```

时，预期执行：

```text
Direct Read
+
Lexical Retrieval
↓
Evidence Package with Limitation
```

必须验证：

- 没有扩大 Source Scope；
- 没有使用竞品资料补充当前商品；
- Retrieval Run 记录 Fallback；
- Evidence Package 记录限制；
- 下游 Skill 状态为 `succeeded_with_limitations`；
- 用户可见限制存在。

Spike **不**实现：Embedding / Vector Database / Rank Fusion / Top-K 优化 / Reranker / Production Retrieval Index。

---

## Fault Injection Contract

Spike 使用显式：

```text
FaultPlan
```

概念结构：

```text
FaultPlan
├── scenario_id
├── target_component
├── target_operation
├── fail_on_attempts[]
├── failure_type
├── failure_payload
├── release_after_attempt
└── enabled
```

示例：

```text
Scenario:
spike-02-transient-retry
Target:
mock_insight_generation
Fail:
attempt 1
Error:
transient_infrastructure_error
Release:
attempt 2
```

**禁止**在业务代码中散落难以追踪的：

```text
if test_mode:
    raise Exception()
```

---

## Fault Injection Rules

Fault Injection 必须：

- 默认关闭；
- 只在 Spike Runtime 中存在；
- 可通过 Scenario 明确启用；
- 可重复；
- 可单独运行；
- 测试结束后自动清理；
- **不**依赖测试执行顺序；
- **不**污染其他 Scenario；
- **不**进入正式生产模块；
- **不**修改 Accepted Business Contract。

可以使用 pytest：Fixtures / `monkeypatch` / `tmp_path` / `caplog`。

---

## Test Framework

Spike 使用：

```text
pytest
```

测试分类：

```text
unit
integration
failure_injection
e2e
optional_external
```

建议 Marker：

```text
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.failure_injection
@pytest.mark.e2e
@pytest.mark.optional_external
```

必要运行命令：

```text
pytest -m unit
pytest -m integration
pytest -m failure_injection
pytest -m e2e
pytest -m "not optional_external"
```

测试结果至少导出：

```text
artifacts/test-results/
├── junit.xml
├── pytest-summary.txt
└── scenario-results.json
```

---

## Local Observability

Spike **不**选择正式 Observability Provider。暂**不**引入：LangSmith / OpenTelemetry / Datadog / Grafana / Jaeger / Sentry。

使用最小：

```text
LocalTraceRecorder
```

每个 Scenario 输出 JSON Lines：

```text
artifacts/traces/<scenario-id>.jsonl
```

事件至少包含适用的：

```text
event
timestamp
task_id
thread_id
run_id
skill_run_id
node_execution_id
attempt_id
trace_id
checkpoint_id
error_category
fallback
transaction_status
```

Local Trace 用于验证关联 ID 和运行行为，**不**表示生产系统使用 JSONL Trace。

---

## Trace Requirements

Trace 必须支持回答：

- 哪个 Node 开始和结束；
- 哪个 Attempt 失败；
- Retry 是否仍属于同一 Node；
- Resume 是否使用相同 Thread；
- Resume 是否创建新 Run；
- 使用了哪个输入版本；
- 哪个 Validator 拒绝输出；
- 哪个事务成功或回滚；
- 是否发生 Fallback；
- 使用了哪个 Checkpoint；
- 创建了哪个 Domain Version；
- 是否创建 RecoveryCase。

---

## CLI Scenario Runner

Spike 提供统一命令行入口，概念形式：

```text
python -m spike_runtime run \
  --scenario spike-01-normal-workflow \
  --workspace .spike-runs/spike-01
```

Runner 负责：

1. 创建隔离工作目录；
2. 初始化 Business Store；
3. 初始化 Runtime Store；
4. 初始化 Checkpoint Store；
5. 写入 Mock Sources；
6. 初始化 Fault Plan；
7. 执行 Graph；
8. 必要时模拟 Review Submit；
9. Resume Graph；
10. 导出业务状态；
11. 导出 Runtime Events；
12. 导出 Checkpoint Summary；
13. 运行 Automated Assertions；
14. 生成 Scenario Result。

---

## Scenario Isolation

每个 Scenario 使用独立目录：

```text
.spike-runs/<scenario-id>/
```

至少输出：

```text
business.sqlite
runtime.sqlite
checkpoints.sqlite
scenario-input.json
scenario-result.json
runtime-events.jsonl
trace.jsonl
business-snapshot.json
checkpoint-summary.json
assertions.json
```

**禁止**多个 Scenario 共享可变数据库状态。每次运行必须能够从空工作目录复现。

---

## Spike Code Directory

建议创建：

```text
spikes/
└── spike-001-langgraph-runtime-and-recovery/
    ├── pyproject.toml
    ├── uv.lock
    ├── README.md
    ├── src/
    │   └── spike_runtime/
    │       ├── graph.py
    │       ├── state.py
    │       ├── identifiers.py
    │       ├── scenarios.py
    │       ├── fault_injection.py
    │       ├── model_provider.py
    │       ├── retrieval.py
    │       ├── validation.py
    │       ├── commit_service.py
    │       ├── cancellation.py
    │       ├── tracing.py
    │       └── repositories/
    │           ├── business.py
    │           ├── runtime.py
    │           └── schema.py
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   ├── failure_injection/
    │   └── e2e/
    └── artifacts/
        └── .gitkeep
```

目录名称可以在实现时做轻微、不改变职责边界的调整。

> **归档说明：** 上述为**建议的 Spike 代码目录结构**，属于规划性质记录。**本归档任务不创建该代码**（Spike 执行属下一议题 `Spike-001 Execution Authorization and Agent Handoff Contract`，尚未确认）。实际代码由授权的 Spike 执行 Agent 在用户明确授权后创建。

---

## Spike Isolation Boundary

必须遵守：

- `spikes/` 代码**不得**被正式产品模块 Import；
- 暂**不**创建正式产品 `src/` 架构；
- Spike Schema **不**构成正式 Domain Schema；
- Spike Dependencies **不**自动进入生产依赖；
- Spike Graph **不**构成正式业务 Graph；
- Spike CLI **不**构成正式产品接口；
- Spike Repository **不**构成生产 Repository；
- Spike Checkpointer **不**构成生产 Checkpointer。

---

## Spike Execution Stages

Spike 按以下阶段执行。

### S0：Environment and Skeleton

完成：Python 环境 / `pyproject.toml` / Lockfile / StateGraph Compile / 三个 SQLite Store / Runtime Identifiers / Scenario Runner / LocalTraceRecorder。

退出条件：

```text
Minimal Graph can run
and
Runtime Record can be generated
```

### S1：Normal Workflow

完成：Mock Facts / Mock Insights / Mock Positioning / Review Package / Interrupt / Approved Strategy / Marketing Brief。

执行：

```text
Spike-01 Normal Workflow
```

退出条件：Current Truth 正确；Graph 正确暂停和恢复；Trace 完整。

### S2：Human Review and Version Safety

执行：Interrupt / Resume / Duplicate Submit / Stale Review / Stale Checkpoint。

退出条件：旧 Review 无法提交；旧 Checkpoint 无法推进；Resume 幂等；Positioning 不重复生成。

### S3：Transaction and Idempotency

执行：Transaction Rollback / Commit Retry / Duplicate Commit / Current Truth Pointer Validation。

退出条件：

```text
Partial Business Write Rate = 0%
Duplicate Business Version Rate = 0%
```

### S4：Failure and Recovery

执行：Transient Retry / Structured Output Failure / Retrieval Fallback / Cancellation / Retry Budget Exhaustion / Recovery Case。

退出条件：每种处置都有结构化 Runtime Evidence；无无限重试；Recovery 不绕过 Validator。

### S5：Observability and Evidence Export

完成：Runtime Records / JSONL Trace / Business Snapshot / Checkpoint Summary / Scenario Result / JUnit XML。

退出条件：每个 Scenario 可独立重现；所有关键 ID 可关联；Automated Assertions 可运行。

### S6：Report and Recommendation

完成：`implementation-notes.md` / `test-results.md` / `runtime-evidence.md` / `limitations.md` / `spike-report.md` / Required RFC List / Readiness Recommendation。

**S6 不得自动改变 Development Status。**

---

## Spike Agent Permissions

Spike Agent 可以：

- 创建和修改 `spikes/spike-001-*`；
- 更新对应 `docs/spikes/spike-001-*` 文档；
- 创建本地临时 SQLite 文件；
- 安装 Spike Lockfile 中的依赖；
- 执行测试；
- 运行 Scenario Runner；
- 创建 Evidence Artifacts；
- 创建 Spike Finding；
- 提交 Readiness Recommendation；
- 建议 RFC；
- 建议修订未接受的实现细节。

---

## Spike Agent Prohibitions

Spike Agent **不得**：

- 修改 Accepted DEC 的含义；
- 修改正式业务 Specs 的业务边界；
- 将 Spike Schema 写成正式 Data Architecture；
- 创建正式业务 Graph；
- 创建生产目录；
- 生成 MVP Roadmap；
- 生成正式开发 Epics；
- 创建正式 GitHub Issues；
- 将 Development Status 改为 READY；
- 选择生产数据库；
- 选择生产 Checkpointer；
- 选择生产 Observability Provider；
- 引入自动发布；
- 使用真实用户数据；
- 执行外部 Side Effect；
- 将可选真实模型测试作为 Readiness 必选条件；
- 将 Spike 代码直接迁移到生产模块。

---

## Data and Secret Boundary

必选 Spike 场景默认不需要任何真实 API Key。使用：Mock Product / Mock Reviews / Scripted Model / Mock Retrieval / Local SQLite / Local Trace。

可选 Real Model Smoke Test 必须：

- 使用环境变量注入 Secret；
- Secret **不**写入文件；
- Secret **不**写入日志；
- Secret **不**进入 Trace；
- Secret **不**进入 Git；
- 无 Secret 时自动 Skip；
- **不**使用真实客户或用户数据。

---

## Scenario Result Contract

每个 Scenario Result 至少包含：

```text
scenario_id
scenario_version
status
expected_outcome
actual_outcome
assertions[]
fault_plan
runtime_ids
input_version_ids
output_version_ids
checkpoint_ids
errors[]
fallbacks[]
artifact_paths[]
started_at
completed_at
dependency_versions
```

Automated Assertions 概念示例：

```text
approved_strategy_version_count == 1
current_truth_pointer == expected_version
invalid_evidence_link_count == 0
stale_checkpoint_resume_success == false
transaction_partial_write_count == 0
duplicate_business_version_count == 0
```

---

## Result Acceptance Boundary

Scenario **不得**只依赖 Agent 的自然语言判断。每个场景必须同时提供：

```text
Automated Assertion
+
Runtime Evidence
+
Human-readable Explanation
```

只有自然语言「看起来成功」**不能**算 Pass。

---

## Temporary Choices Are Not Production Commitments

必须在 Spike 文档和代码 README 中明确记录：

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

Spike 验证的是：

```text
Required Architecture Behavior
```

而**不**是：

```text
Final Production Infrastructure
```

---

## Required Deliverables

### Spike Code

```text
spikes/spike-001-langgraph-runtime-and-recovery/
```

### Automated Tests

Unit / Integration / Failure Injection / End-to-end / Optional External Smoke Test。

### Evidence

Scenario Results / Runtime Records / Business Snapshots / Checkpoint Summaries / JSONL Traces / Transaction Rollback Evidence / Idempotency Evidence / Recovery Case Evidence。

### Documentation

```text
docs/spikes/spike-001-langgraph-runtime-and-recovery/
├── README.md
├── spike-plan.md
├── test-scenarios.md
├── temporary-stack.md
├── execution-brief.md
├── implementation-notes.md
├── test-results.md
├── runtime-evidence.md
├── limitations.md
└── spike-report.md
```

> **归档说明：** 归档当前决策时，只创建或更新规划性质文件。**不得在本次归档任务中执行 Spike。** `implementation-notes.md` / `test-results.md` / `runtime-evidence.md` / `limitations.md` / `spike-report.md` 为执行阶段产物，本归档**不创建**。

### Recommendation

Spike 结束后输出：

```text
RECOMMENDED:
READY
or
CONDITIONALLY READY
or
NOT READY
```

该内容只是建议。

---

## Production Commitment Boundary

本决定已经接受的**仅**是：

> 使用一套明确、可复现、确定性的临时栈执行 Spike-001。

本决定**没有**接受：正式后端语言 / 正式 LangGraph 版本 / Async 或 Sync 生产模式 / 正式数据库 / 正式 ORM / 正式 Checkpointer / 正式 API / 正式 Worker / 正式 Queue / 正式 Observability / 正式模型供应商 / 正式 Retrieval Backend / 正式部署平台。

---

## Contract Summary

```text
Decision:
DEC-035
Spike:
Spike-001 LangGraph Runtime and Recovery
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

## Reason

Spike 的主要目标是验证架构行为，而**不**是验证最终技术栈或业务质量。如果 Spike 同时引入：生产数据库 / 正式 API / 前端 / 真实 Retrieval / 真实 LLM / Worker / Queue / 正式 Observability，则会增加过多变量，使失败根因难以识别。

因此需要使用：

```text
Minimal
Deterministic
Local
Inspectable
Reproducible
Disposable
```

的临时环境。

分离式 SQLite 可以直观验证：Business Current Truth / Runtime Records / LangGraph Checkpoint 三者是否真正保持独立。Scripted Model 和 Mock Retrieval 可以确保关键可靠性测试不受外部服务和模型随机性影响。

---

## Impact

- 为 Spike-001 提供明确、可复现、确定性的执行环境与边界。
- 临时技术选择（Python 3.13 / LangGraph 1.2.9 / 同步 / 三 SQLite / SqliteSaver / Scripted Model / Mock Retrieval / pytest / JSONL / CLI）**不**构成任何生产技术承诺。
- 明确 Review Package 创建与 Interrupt 分离的节点边界（承接 DEC-029 + DEC-034）。
- 明确三类存储物理分离（承接 DEC-033 + DEC-034 的 `LangGraph Checkpoint Store ≠ Business Current Truth Repository`）。
- 明确统一 `BusinessCommitService` + Atomic Commit 契约（承接 DEC-024 / DEC-033）。
- 明确 Spike Agent 权限与禁止事项（承接 DEC-034）。
- **不**改变 Development Status（保持 `NOT READY`）；**不**改变 Spike Execution Status（保持 `NOT STARTED`）。

---

## Decision Boundary

本决定**已经确认**：Python 3.13 / 精确固定 LangGraph 1.2.9 / 同步 StateGraph Invoke / 使用 `uv` 管理 Spike 环境 / 三个独立 SQLite 文件 / LangGraph SqliteSaver / 严格 Checkpoint 反序列化 / Python `sqlite3` 事务 / 统一 `BusinessCommitService` / Review Package 创建和 Interrupt 分离 / Scripted Deterministic model / 可选 Real Model Smoke Test / Mock Retrieval / Scenario-based FaultPlan / pytest / JSONL Local Trace / CLI Scenario Runner / Scenario Isolation / 建议 Spike 代码目录 / S0—S6 执行顺序 / Spike Agent 权限 / Spike Agent 禁止事项 / Secret 和数据边界 / Scenario Result Contract / Automated Assertions / 临时技术选择不构成生产承诺 / Spike Agent 不能自行宣布 READY。

本决定**尚未确认**：Production Backend Language / Production LangGraph Version / Production Async Model / Production Database / Production ORM / Production Checkpointer / API Framework / Worker Framework / Queue / OpenTelemetry / LangSmith / Logging Provider / Tracing Provider / Real LLM Provider / Embedding Model / Vector Database / Deployment Platform / Spike 具体执行时间 / **Spike 由 Claude 还是 Codex 主执行** / 实际依赖兼容性结果 / Spike Readiness Recommendation。

---

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related Decisions

- DEC-023：LangGraph StateGraph；
- DEC-024：Versioned Domain State；
- DEC-029：Human Review and Approved Strategy；
- DEC-032：Hybrid Retrieval and Evidence Runtime；
- DEC-033：Workflow Runtime Failure Recovery, Retry and Observability；
- DEC-034：Technical Spike and Architecture Readiness Gate。

## Related RFC

None

## Supersedes

None

## Amends

**DEC-034** —— 为 Spike-001 定义可执行的临时技术栈（temporary stack）与 Spike Agent 操作边界（operating boundaries）。

> 本归档**不修改** DEC-034 决定文件、其概念 Readiness Spec 或其在 decision-log 中的行（历史记录保留不动）；Amends 关系仅记录于本 DEC-035 文件与 decision-log 的 DEC-035 行。DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 的历史记录同样保持不动。

---

## Notes

下一议题（尚未开始，需用户明确启动）：`Spike-001 Execution Authorization and Agent Handoff Contract`——优先讨论：Spike 由 Codex 还是 Claude 主执行 / 是否创建独立 Git Branch / 执行 Agent 的完整输入文件清单 / Agent 开始前的 Repository Audit / 允许修改的目录 / 禁止修改的目录 / S0—S6 是否一次执行或分阶段授权 / 每阶段结束需要提交什么证据 / Agent 遇到决策冲突时如何停止 / 依赖安装失败如何处理 / Spike Finding 格式 / 是否允许自动提交 Commit / 是否允许创建 PR / 用户在哪些 Gate 进行 Review / Spike Report 的人工验收 / 是否授权正式开始执行 Spike。

在 **Spike-001 Execution Authorization and Agent Handoff Contract** 议题确认前：**不**启动 Spike；**不**安装依赖；**不**创建 Spike 代码；**不**运行测试；**不**创建正式 Roadmap；Development Status 保持 `NOT READY`。
