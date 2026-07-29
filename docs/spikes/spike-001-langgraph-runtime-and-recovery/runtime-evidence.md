# Spike-001 — Runtime Evidence（运行时证据）

> **Status: S6 — FINAL**
> 证据以 **JSON / JSONL** 导出（非 SQLite 二进制、非 Secret），可由测试与 CLI 场景复现。

## 1. 证据类型与位置

| 证据 | 生成者 | 位置（运行时，不入库） | 说明 |
|---|---|---|---|
| JSONL Trace | `LocalTraceRecorder` | `.spike-runs/<id>/trace.jsonl` | append-only，携带运行身份链 |
| Business Snapshot | `WorkflowHarness.business_snapshot()` | `.spike-runs/<id>/business-snapshot.json` | Current Truth pointers / domain versions / audit / 幂等 / 指标 |
| Scenario Result | `WorkflowHarness.export_evidence()` | `.spike-runs/<id>/scenario-result.json` | 含自动断言 `checks` |
| Checkpoint Summary | `evidence.export_checkpoint_summary()` | `checkpoint-summary.json` | 每线程 checkpoint 计数 |
| Runtime Events | `evidence.export_runtime_events()` | `runtime-events.json` | runtime store 事件导出 |
| JUnit XML | `evidence.write_junit()` | `junit.xml` | CI 风格报告 |

> `.spike-runs/**`、`*.sqlite*` 被 `.gitignore` 排除；上述 JSON/JSONL/XML 为可复现运行时数据，按需重新生成。

## 2. 运行身份关联链（DEC-033）

每个 trace 事件携带可关联标识：`trace_id` / `task_id` / `workflow_run_id`（resume 用新 `run_id`）/ `thread_id` / `review_id` / 各 `*_version_id`。`correlate_trace()` 断言：单 trace 贯穿一次运行、Current Truth 域齐全、`approved_strategy_version_count==1`、`partial_write_count==0`。

示例（spike-01，字段摘录）：

```json
{"seq": 1, "trace_id": "trace_…", "event_type": "run_start", "task_id": "task_…", "workflow_run_id": "run_…", "thread_id": "thread_…"}
{"seq": 2, "event_type": "interrupted", "interrupted": true, "review_id": "review_package_…", "facts_version_id": "facts_…", "positioning_version_id": "positioning_…"}
{"seq": 3, "event_type": "review_submit", "review_id": "review_package_…", "approved_strategy_version_id": "approved_strategy_…", "committed": true}
{"seq": 4, "event_type": "resumed", "workflow_run_id": "run_…(new)", "marketing_brief_version_id": "marketing_brief_…"}
{"seq": 5, "event_type": "run_end", "status": "pass"}
```

## 3. 事务回滚证据（spike-04）

注入失败于 version insert 之后、pointer update 之前 → 整体回滚。断言：

- `current_truth(domain)` 不变；
- `partial_write_count()==0`（无孤立的 domain_version）；
- 失败 key 无 idempotency 记录；
- 无指向不存在版本的 `commit` audit。

## 4. 幂等证据（spike-06 / S3）

同一 `idempotency_key` 重复提交：`committed==False`、`valid_version_count==1`、pointer 稳定。Recovery：回滚后用同一 key 重试 → `committed==True` 且仅一个版本。

## 5. Stale 防护证据（spike-07 / spike-08）

- **Stale Review**：提交后旧 package 再次提交（新幂等键）→ `StaleReviewError`。
- **Stale Checkpoint**：foreign `thread_id` 的 `Command(resume)` 在空 state 下从 START 运行，节点 `_require_identity` 在写前抛 `StaleResumeError`；Current Truth 前后一致、`partial_write_count==0`。

## 6. 失败与恢复证据（spike-02/03/09/10/11）

| 场景 | 证据要点 |
|---|---|
| spike-02 | transient 注入 attempt 1/2，attempt 3 成功（有界） |
| spike-03 | invalid output 不重试（`calls==1`） |
| spike-09 | degraded → `candidates==[]`/`coverage=none`，记录 `retrieval_degraded`，不伪造 |
| spike-10 | 取消后无 approved_strategy、无部分写入 |
| spike-11 | 预算耗尽 `RetryBudgetExhausted`，`calls==max_attempts`（无无限重试） |

## 7. 可观测性证据（S5）

- 每场景在独立 workspace 复现，两次运行 evidence 结构等价；
- `checkpoint-summary.json` 含本 `thread_id` 的 checkpoint；
- JUnit XML 正确生成 tests/failures。

> 完整数值见 `test-results.md`；结论与建议见 `spike-report.md`。
