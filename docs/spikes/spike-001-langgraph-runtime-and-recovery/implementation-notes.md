# Spike-001 — Implementation Notes（实现说明）

> **Status: S6 — EXECUTION COMPLETE · 建议见 `spike-report.md`**
> **治理来源：** DEC-034 · DEC-035 · DEC-036 · DEC-037
> **Spike Issue：** [#1](https://github.com/JettxonHo/ai-ecommerce-agent/issues/1) · **Draft PR：** [#2](https://github.com/JettxonHo/ai-ecommerce-agent/pull/2) · **Branch：** `spike/001-langgraph-runtime-recovery`
> **代码工作区：** [`../../../spikes/spike-001-langgraph-runtime-and-recovery/`](../../../spikes/spike-001-langgraph-runtime-and-recovery/)

本文说明 Spike-001 的实现结构、关键设计决策与对应 DEC 契约。这是**临时、可抛弃**的验证代码，**不是**生产实现。

---

## 1. 临时技术栈落地（DEC-035）

| 契约项 | 落地 | 证据 |
|---|---|---|
| Python 3.13 | 3.13.14（uv 管理的独立 CPython） | `pyproject.toml` `requires-python=">=3.13,<3.14"` |
| LangGraph 精确固定 | `langgraph==1.2.9` | `pyproject.toml` + `uv.lock` |
| Checkpoint SQLite | `langgraph-checkpoint-sqlite==3.1.0`（`SqliteSaver`） | `uv.lock` |
| 同步 StateGraph Invoke | `graph.invoke(...)` 同步驱动 | `src/spike_runtime/graph.py`、`harness.py` |
| 三类分离 SQLite | `business.sqlite` / `runtime.sqlite` / `checkpoints.sqlite` | `src/spike_runtime/stores.py` |
| 事务（统一入口） | `BusinessCommitService`（Python `sqlite3` 事务） | `src/spike_runtime/commit.py` |
| Scripted Model | `ScriptedModelProvider`（确定性脚本输出） | `src/spike_runtime/providers.py` |
| Mock Retrieval | `MockRetrievalRuntime`（含 degraded 模式） | `src/spike_runtime/providers.py` |
| Scenario Fault Injection | `FaultPlan` / `run_with_retry`（默认关闭） | `src/spike_runtime/faults.py` |
| pytest | `pytest==8.4.1` | `pyproject.toml` dev group |
| Local JSONL Trace | `LocalTraceRecorder`（append-only） | `src/spike_runtime/trace.py` |
| CLI Scenario Runner | `python -m spike_runtime run --scenario ... --workspace ...` | `src/spike_runtime/__main__.py` |

锁定与复现：`uv lock` → `uv sync --frozen`（`uv.lock` 已入库）。

## 2. 模块结构

```text
src/spike_runtime/
  ids.py        运行身份标识（task/run/skillrun/nodeexec/attempt/error/trace/recovery）
  stores.py     三类分离 SQLite schema 与初始化（business/runtime/checkpoints）
  commit.py     BusinessCommitService —— 原子提交契约的唯一写入入口
  graph.py      最小业务流 StateGraph（含 Human Review 三节点边界 + _require_identity）
  providers.py  ScriptedModelProvider + MockRetrievalRuntime
  review.py     ReviewService —— Review Submit 独立业务事务（stale/duplicate 防护）
  faults.py     FaultPlan + 有界重试（transient 重试 / invalid 不重试 / 预算耗尽）
  harness.py    WorkflowHarness —— 编排 invoke→submit→resume→export
  evidence.py   checkpoint summary / runtime events / JUnit XML / trace 关联
  trace.py      LocalTraceRecorder（JSONL）
  __main__.py   CLI Scenario Runner
tests/
  test_skeleton.py                S0/S1（6）
  test_review_safety.py           S2（4）
  test_transaction_idempotency.py S3（4）
  test_failure_recovery.py        S4（7）
  test_observability.py           S5（4）
```

## 3. 关键设计决策

- **唯一写入口（Atomic Commit Contract）**：所有正式业务写入只经 `BusinessCommitService.commit_domain_version`，单事务内完成「建版本 + 证据链 + 移动 Current Truth Pointer + 阶段状态 + 业务审计 + 幂等记录」。Graph 节点不绕过它。任一失败整体回滚。
- **幂等**：以 `idempotency_key` 为逻辑身份。重复提交返回 `committed=False` 且不产生重复业务版本；失败回滚后用**同一** key 重试可干净恢复（Recovery Case）。
- **Human Review 节点边界**：`create_review_package → await_human_review → load_approved_strategy` 三节点分离；`interrupt()` 只出现在 `await_human_review`，该节点不做业务写入。
- **Resume 契约**：同 `thread_id`、新 `run_id`、不重建 Review Package、不重生 Positioning candidates。
- **Staleness**：Review Package 的「可提交」= 当前 pointer 且状态 `valid`；提交后即 supersede 并删除 pending pointer。stale checkpoint/foreign resume 由节点入口 `_require_identity` 在写前拦截（`StaleResumeError`）。
- **Checkpoint ≠ Current Truth**：`checkpoints.sqlite` 由 `SqliteSaver` 自管，只存 graph 检查点；业务 Current Truth 只存 `business.sqlite`。

## 4. 与 DEC 的对应

DEC-024（状态四类边界）、DEC-029（Human Review / Approved Strategy / 原子提交）、DEC-032（检索与证据装配的降级与不伪造）、DEC-033（失败恢复 / 运行身份分层 / 有界重试 / 幂等提交 / Manual Recovery / 可观测）、DEC-035（临时栈与执行契约）。详见 `spike-report.md` 的 Decision Coverage。

## 5. 复现

```bash
cd spikes/spike-001-langgraph-runtime-and-recovery
uv sync --frozen
uv run pytest
uv run python -m spike_runtime run --scenario spike-01-normal-workflow --workspace .spike-runs/spike-01
```
