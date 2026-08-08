# Spike-001 Temporary Stack

> **Current Status: HISTORICAL PLAN — SPIKE COMPLETED / MERGED**
> 来源决定：[DEC-035](../../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)
> 概念规格：[../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)
> **Historical planning record:** 本文件记录执行前临时栈；Spike 后续已完成。临时选择仍不构成任何生产承诺，结果以 [spike-report.md](spike-report.md) 为准。

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

该栈只验证：StateGraph 执行 / Interrupt·Resume / Checkpoint / 业务状态与执行状态分离 / Transaction Rollback / Idempotency / Retry / Stale Review / Stale Checkpoint / Retrieval Fallback / Cancellation / Manual Recovery / Trace Correlation。**不构成任何生产技术承诺。**

---

## Language

```text
Python 3.13.x
```

选择理由仅限：便于快速验证 LangGraph Runtime / 标准库具有 SQLite 和事务能力 / 便于使用 pytest 进行故障注入 / Spike 不需验证浏览器或正式前端 / 可将 Graph·Repository·Fault Injection·Test 集中在独立实验目录。

**不**表示：

```text
Production Backend must use Python
```

生产后端语言仍需后续 RFC 确认。

---

## Dependency Version Strategy

直接依赖必须精确固定（`pyproject.toml` 声明 + 生成并提交 Lockfile + 不用浮动 `latest` + Spike 期间不自动升级 + Spike Report 记录完整依赖版本 + 运行证据关联依赖版本 + 版本调整形成 Spike Finding）。

建议 Spike 基线：

```text
Python = 3.13.x
LangGraph = 1.2.9
langgraph-checkpoint-sqlite = compatible pinned version
pytest = pinned stable version
```

临时包管理工具：`uv`（创建环境 / 安装依赖 / 生成 Lockfile / 执行测试 / 提供可复现运行入口）。`uv` **不**自动成为生产构建或部署工具。

---

## Version Change Boundary

Spike Agent **不得**擅自将 LangGraph 1.2.9 替换为其他版本。遇到无法安装 / Python 3.13 不兼容 / SqliteSaver 不兼容 / Interrupt 行为与预期不一致 / 依赖严重缺陷 / 安全配置无法满足时，必须：

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

```text
StateGraph
+
Synchronous Invoke
```

暂**不**以 Async Graph / Worker / Queue 为主路径。同步模式减少 Event Loop / Async Repository / 并发事务 / 分布式 Worker / Queue Retry / Async Cancellation 对核心架构验证的干扰。

**不**表示生产系统必须使用同步运行（生产 Sync / Async / Worker / Queue / Background Execution 仍需后续 RFC 决定）。

---

## Physical Storage Separation

```text
.spike-data/
├── business.sqlite
├── runtime.sqlite
└── checkpoints.sqlite
```

直接验证：

```text
Business State
≠
Runtime State
≠
Checkpoint State
```

未来生产即使使用同一数据库实例，也必须保持逻辑职责分离。

> 上述 SQLite 仅属 Spike 实验存储，**不构成正式数据库设计**。

---

## Checkpoint Security

必须启用严格 Checkpoint 反序列化边界（`LANGGRAPH_STRICT_MSGPACK=true` 或语义等价的显式安全配置）。Graph State 只保存简单、明确、允许的类型；**不**保存任意 Python 对象 / Secret / 完整业务文档 / 不必要模型输出；**不**允许任意模块反序列化；Spike Report 记录实际安全配置。版本不支持时必须创建 Spike Finding，**不**静默忽略。

---

## Transaction Layer

```text
Python sqlite3
```

暂**不**用 ORM，以直接观察 Transaction Begin / Domain Version Insert / Evidence Link Insert / Current Truth Pointer Update / Stage State Update / Audit Insert / Idempotency Insert / Commit / Rollback。所有正式业务写入经统一 `BusinessCommitService`（概念接口：`commit_fact_version()` / `commit_insight_version()` / `commit_review_package()` / `commit_approved_strategy()` / `commit_marketing_brief()`）。

---

## Model Strategy

Readiness 必选场景默认使用 `ScriptedModelProvider`（按 Scenario ID / Node / Attempt Number / Fault Plan 返回确定性结果），用于保证可重复 / 控制 Structured Output Failure / 控制 Retry / 控制 Validator Failure / 避免真实模型随机性影响 Readiness 结论。

允许独立可选 `Spike-Optional-01 Real Model Structured Output Smoke Test`（仅验证 Model Adapter 可调用 / 输出进相同 Schema Validator / Token·Latency Metadata 可记录 / Provider Error 进 Runtime Error Contract / 模型失败不绕过 Validator）。**不**属 READY 必选 / **不**替代 Scripted Tests / **不**验证业务输出质量 / 无 API Key 自动 Skip / **不**影响必选 Scenario / **不**用真实用户数据。

---

## Retrieval Strategy

使用 `MockRetrievalRuntime`（`direct_read()` / `lexical_search()` / `semantic_search()` / `build_evidence_package()`）+ 固定 Mock Fragment（容量 500 mL / 重量 260 g / 通勤漏水顾虑 / 密封表现认可）。保留 Fragment ID / Source Scope / Product Identity / Source Version / Retrieval Channel / Retrieval Run ID / Evidence Limitation。

`semantic_available = false` 时走 Direct Read + Lexical → Evidence Package with Limitation，必须验证不扩大 Source Scope / 不用竞品补当前商品 / Retrieval Run 记 Fallback / Evidence Package 记限制 / 下游 `succeeded_with_limitations` / 用户可见限制存在。Spike **不**实现 Embedding / Vector Database / Rank Fusion / Top-K / Reranker / Production Retrieval Index。

---

## Test Framework

```text
pytest
```

分类 unit / integration / failure_injection / e2e / optional_external，对应 `@pytest.mark.*` Marker。必要运行命令：

```text
pytest -m unit
pytest -m integration
pytest -m failure_injection
pytest -m e2e
pytest -m "not optional_external"
```

结果导出 `artifacts/test-results/`（junit.xml / pytest-summary.txt / scenario-results.json）。

---

## Observability

**不**选正式 Provider（LangSmith / OpenTelemetry / Datadog / Grafana / Jaeger / Sentry 全部不引入）。使用 `LocalTraceRecorder`，每 Scenario 输出 `artifacts/traces/<scenario-id>.jsonl`。事件含 event / timestamp / task_id / thread_id / run_id / skill_run_id / node_execution_id / attempt_id / trace_id / checkpoint_id / error_category / fallback / transaction_status。

Local Trace 用于验证关联 ID 和运行行为，**不**表示生产系统使用 JSONL Trace。

---

## Production Commitment Boundary

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

Spike 验证的是 Required Architecture Behavior，而**不**是 Final Production Infrastructure。
