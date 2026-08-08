# Spike-001 — LangGraph Runtime and Recovery（代码工作区）

> **Status: COMPLETED（S0—S6 已完成；临时验证代码，非生产实现）**
> **治理来源：** DEC-034 · DEC-035 · DEC-036 · DEC-037
> **执行简报：** [`../../docs/spikes/spike-001-langgraph-runtime-and-recovery/execution-brief.md`](../../docs/spikes/spike-001-langgraph-runtime-and-recovery/execution-brief.md)
> **临时栈：** [`../../docs/spikes/spike-001-langgraph-runtime-and-recovery/temporary-stack.md`](../../docs/spikes/spike-001-langgraph-runtime-and-recovery/temporary-stack.md)
> **Spike Issue：** [#1](https://github.com/JettxonHo/ai-ecommerce-agent/issues/1) · **Branch：** `spike/001-langgraph-runtime-recovery`

这是 Spike-001 的**临时、可抛弃**代码工作区。它验证**架构运行时行为**（StateGraph 执行 / Interrupt·Resume / Checkpoint / 三类存储分离 / 事务回滚 / 幂等 / 有界重试 / Stale Review / Stale Checkpoint / Retrieval Fallback / Cancellation / Trace 关联），**不是** MVP、**不是**正式业务 Graph、**不是**生产技术承诺。

## 临时技术栈（DEC-035）

```text
Python 3.13 (uv-managed, 3.13.14)
langgraph==1.2.9              # 精确固定
langgraph-checkpoint-sqlite==3.1.0
pytest==9.0.3                 # dev; post-Spike dependency maintenance
同步 StateGraph Invoke + SqliteSaver + 三类分离 SQLite
```

锁定见 `uv.lock`（`uv lock` / `uv sync --frozen` 可复现）。

## 环境准备

```bash
cd spikes/spike-001-langgraph-runtime-and-recovery
uv sync --frozen        # 按 uv.lock 复现环境（含 Python 3.13）
```

## 运行测试

```bash
uv run pytest
```

## CLI Scenario Runner

```bash
uv run python -m spike_runtime run \
  --scenario spike-00-skeleton \
  --workspace .spike-runs/spike-00
```

每个 Scenario 在独立目录 `.spike-runs/<scenario-id>/` 下产生 `business.sqlite` / `runtime.sqlite` / `checkpoints.sqlite` / `trace.jsonl` / `scenario-result.json` 等（这些产物被 `.gitignore` 排除，属本地可复现运行时数据）。

## 目录

```text
src/spike_runtime/
  ids.py       # 运行身份标识（task/run/node/attempt/trace/recovery）
  stores.py    # 三类分离 SQLite（business / runtime / checkpoints）
  commit.py    # BusinessCommitService — 原子提交契约（唯一写 Current Truth 的入口）
  graph.py     # 最小 StateGraph 骨架 + SqliteSaver + Human Review 三节点边界
  trace.py     # LocalTraceRecorder — JSONL Trace
  __main__.py  # CLI Scenario Runner
tests/
  test_skeleton.py  # S0 smoke
```

## 边界（重要）

- Human Review 节点边界：`create_review_package → await_human_review → load_approved_strategy` 三节点分离；**禁止** `create_review_package + write_business_data + interrupt()` 同节点。
- 所有正式业务写入只经 `BusinessCommitService`（原子提交）；Graph 节点不得绕过。
- 必选场景无需真实 API Key；可选 Real Model Smoke Test 无 Secret 自动 Skip。
- 产物 `.spike-runs/**`、`.spike-data/**`、`*.sqlite*` 不入库；导出证据用 JSON。
