# Spike-001 — Test Results（测试结果）

> **Status: S6 — FINAL**
> **最终命令：** `uv run pytest` → **25 passed**（0 failed）
> **代码工作区：** `spikes/spike-001-langgraph-runtime-and-recovery/`

## 总览

| 指标 | 值 |
|---|---|
| 总测试数 | **25** |
| 通过 | **25** |
| 失败 | **0** |
| 测试文件 | 5 |
| 测试框架 | pytest 8.4.1 |
| 运行环境 | Python 3.13.14 · langgraph 1.2.9 |

## 按文件

| 文件 | 阶段 | 测试数 | 标记 |
|---|---|---|---|
| `test_skeleton.py` | S0/S1 | 6 | unit ×5 · integration ×1 |
| `test_review_safety.py` | S2 | 4 | integration ×4 |
| `test_transaction_idempotency.py` | S3 | 4 | integration ×4 |
| `test_failure_recovery.py` | S4 | 7 | failure_injection ×4 · integration ×3 |
| `test_observability.py` | S5 | 4 | unit ×2 · integration ×2 |

## 场景 → 测试 → 断言 映射

| 场景 | 验证点 | 关键断言（自动） | 结果 |
|---|---|---|---|
| spike-00 skeleton | graph 编译 + invoke + checkpoint | graph 可编译；三存储分离 | ✅ |
| spike-01 normal workflow | 正常流 Current Truth | `approved_strategy_version_count==1` · `partial_write_count==0` · 六 pointer 就位 · Trace 完整 | ✅ |
| spike-02 transient retry | 瞬态故障有界重试 | attempt 1/2 失败、3 成功；`calls==3` | ✅ |
| spike-03 invalid structured output | 非瞬态不重试 | `InvalidStructuredOutputError` 抛出且 `calls==1` | ✅ |
| spike-04 transactional rollback | 事务回滚无部分写入 | pointer 不变 · `partial_write_count==0` · 无 idempotency/audit 泄漏 | ✅ |
| spike-05 interrupt + resume | 暂停/恢复幂等 | Positioning 不重生 · review package 不重建 · `approved_strategy_version_count==1` | ✅ |
| spike-06 duplicate review submit | 重复提交幂等 | 第二次 `committed==False` · 版本数仍 1 | ✅ |
| spike-07 stale review | 旧 Review 拒绝 | `StaleReviewError` 抛出 | ✅ |
| spike-08 stale checkpoint | 旧/外来 checkpoint 防推进 | `StaleResumeError` 抛出 · Current Truth 不变 | ✅ |
| spike-09 retrieval degraded | 降级不伪造 | `candidates==[]` · `coverage==none` · 记录 degraded | ✅ |
| spike-10 cancellation | 取消无部分写入 | 无 approved_strategy · `partial_write_count==0` | ✅ |
| spike-11 retry budget exhaustion | 重试预算耗尽 | `RetryBudgetExhausted` · `calls==max_attempts`（无无限重试） | ✅ |
| recovery case | 失败恢复不重复 | 同幂等键重试干净成功 · 版本数 1 | ✅ |
| S5 reproducibility | 场景独立重现 | 两次隔离运行 evidence 结构等价 | ✅ |
| S5 correlation | 关键 ID 可关联 | 单 trace · pointer 域齐 · checkpoint summary 有本线程 | ✅ |
| S5 junit | JUnit XML | testsuite tests/failures 正确 | ✅ |

## CLI 场景

```text
python -m spike_runtime run --scenario spike-01-normal-workflow --workspace .spike-runs/spike-01
→ {"scenario": "spike-01-normal-workflow", "status": "pass"}
```

产物（`.spike-runs/spike-01/`，不入库）：`business.sqlite` / `runtime.sqlite` / `checkpoints.sqlite` / `trace.jsonl` / `business-snapshot.json` / `scenario-result.json`。

## 备注

- 必选场景**无需真实 API Key**（Scripted Model + Mock Retrieval + 本地 SQLite + 本地 Trace）。
- 可选 Real Model Smoke Test 未启用（无 Secret，按契约自动 Skip）；不作为 Readiness 必选条件。
