# MVP-0 FL-2 Product Intake 离线诊断

## 结论

`INSUFFICIENT_SANITIZED_EVIDENCE`

第二次受控 smoke 的脱敏事实，结合当前 `product_intake_v1 / v1` 的真实离线控制流，不能唯一识别历史内部失败边界。一个完全相同的保留安全签名，在最小真实 seam 中可由至少三个实际 `ModelRuntimeError` 类别以及多个不同拒绝分支产生。因此本报告不主张历史响应是截断、空内容、JSON 问题、非成功 finish、Schema 拒绝或 Domain admission 拒绝中的任一种。

## 范围与执行边界

- Issue: [#287](https://github.com/JettxonHo/ai-ecommerce-agent/issues/287)
- 基线与 `origin/main`: `d02620c2667a8ce0e8c56af5b784a63139102dd0`
- 分支: `codex/mvp0-fl2-product-intake-diagnosis`
- 唯一新增路径:
  - `apps/backend/tests/integration/test_fl2_deepseek_offline_diagnosis.py`
  - 本文档
- 本次执行使用用户对 Issue #287 的一次性 Terra 例外授权（`授权 Terra 仅执行 Issue #287 两文件离线诊断`）。请求的调度身份是 `gpt-5.6-terra` / `xhigh` / `AUXILIARY_IMPLEMENTER`；运行时实例模型未单独暴露，故为 `UNVERIFIED_RUNTIME_MODEL`，未作推断。

没有读取或检查 Secret / 环境值，没有 Provider 或网络调用、付费行为、PostgreSQL、HTTP API、live smoke、raw Provider material，也没有生产、既有文件、依赖、迁移或公共契约改动。`httpx.MockTransport` 使 OpenAI SDK 请求只在进程内完成。

## 接受的历史安全事实

本诊断只保留以下第二次 smoke 已接受的事实：

- 一个 `product_intake_v1 / v1` Provider call，后续 stage 2～5 未运行；
- `deepseek / deepseek-v4-pro / chat_completions`；
- input / output / total usage 为 `2353 / 8192 / 10545`；
- latency 为 `106434 ms`，低于 `120 s` application profile；
- retry / recovery 为 `0 / 0`；
- 在 `awaiting_review` 前以固定安全 HTTP 500 停止，所有 behavior gates 为 false；
- 证据不包含 finish reason、raw response、reasoning、prompt、candidate、traceback 或内部错误类别。

`8192` 与该 Profile 的 `max_tokens` 相等仍只是线索，不被当作历史 finish reason 或根因。

## 真实 seam 与探针

探针由 `DeterministicPipelineCoordinator` 调用真实 `DeepSeekModelRuntime`。每个 case 都使用真实五个 output-spec factory 和同一份虚构的“城市通勤双肩包” sufficient input；runtime factory 只为该 coordinator 构造 `openai.OpenAI(max_retries=0)` 和 `httpx.MockTransport`。

Mock handler 按实际 first-stage request 的 Chat Completions 路径、模型、JSON mode、thinking、reasoning effort 与 `8192` profile 生成一个 Chat Completion。它的 usage 固定为 `2353 / 8192 / 10545`；每个 case 将 `_monotonic` 固定为 `(0.0, 0.0, 0.0, 106.434)`，所以实际 Provider metadata 记录 `106434 ms`，且保持在 `120 s` deadline 内。

```text
Coordinator stage 1
  -> DeepSeek request preparation and SDK call over MockTransport
  -> actual Chat Completion mapping
  -> actual structured JSON / project-schema validation
  -> actual Fast Lane domain admission
  -> first ModelRuntimeError stops stages 2-5
```

安全签名直接从每个真实 runtime 的 Provider metadata 与 runtime 记录读取：Provider/API、configured/resolved model、execution profile、usage、latency、attempt count、runtime call count 与 retry count。每个 case 都得到一条相同签名：一个 stage-1 call、一个 attempt、`product_intake_v1 / v1`、`deepseek-v4-pro`、`2353 / 8192 / 10545`、`106434 ms` 与 zero retry。这是本测试直接证明的全部观测面。

## TRUE RED

先写入的诊断断言是假设“相同历史安全签名只对应一个内部类别”。运行命令为：

```text
uv run --project apps/backend --offline pytest apps/backend/tests/integration/test_fl2_deepseek_offline_diagnosis.py -q
```

初次有效运行在 `0.53 s` 后按预期失败：安全签名相等断言通过，但“只有一个实际类别”断言得到 3。真实 runtime 给出了 `INCOMPLETE_OUTPUT`、`INVALID_CANDIDATE` 与 `TRANSIENT_PROVIDER_FAILURE`。这不是生产故障或历史 root-cause assertion；它是本 Issue 所需的反证实验。

最终测试只保留可证实的 invariant：相同安全签名必须对应至少两个实际类别。最终同一 focused command 通过（`1 passed in 0.49 s`）。

## 现有 application flattening 路径（只读代码追踪，不是本测试观测）

本离线测试没有启动 PostgreSQL、FastAPI 或 HTTP endpoint，也没有实际观察历史 safe HTTP 500、recovery count 或 behavior gates。它只在 coordinator / runtime seam 中观察一条 first-stage call 和安全 metadata。

现有代码说明历史记录中的安全 HTTP 500 如何可以由该类异常形成：`DeterministicResultPostgresApplication.generate_result` 调用 coordinator；若其抛出异常，代码将其包装为 `generation_failed`，而 `task_routes._result_problem` 把该 code 映射为 fixed safe HTTP 500。这个执行链没有向 HTTP 层传递 runtime candidate 或 traceback。

同一 coordinator 的五阶段循环没有在 stage error 后继续迭代：stage 1 的 runtime、JSON / Schema 或 Domain exception 会在返回 `awaiting_review` 前逸出，因此 stage 2～5 不会被请求。若此异常通过上述 application path，调用在 commit 之前失败，后续 result-dependent behavior gates 也没有进入条件；这个解释与已接受历史 evidence 的“后续 stages / gates 未发生”一致，但不是本测试对 PG/API/gates 的重复验证。测试实际读取的 runtime retry count 为 zero，且该 coordinator / runtime seam 不调用 recovery。

## 代表性分支与边界地图

| 代表性真实分支 | 首次拒绝的真实边界 | 实际类别 | 是否保留相同安全签名 |
|---|---|---|---|
| `finish_reason=length` | DeepSeek response mapper | `INCOMPLETE_OUTPUT` | 是 |
| empty content | DeepSeek response mapper | `INCOMPLETE_OUTPUT` | 是 |
| malformed JSON | DeepSeek response mapper | `INVALID_CANDIDATE` | 是 |
| non-success `content_filter` finish | DeepSeek response mapper | `TRANSIENT_PROVIDER_FAILURE` | 是 |
| mapped JSON object `{}` | Product Intake project-schema validation | `INVALID_CANDIDATE` | 是 |
| 只把 real `payloads[0]` 的 `workflow_stage_decision` 改为 schema-valid `waiting_input` | Fast Lane domain admission | `INVALID_CANDIDATE` | 是 |

每一类别都从捕获到的实际 `ModelRuntimeError` 读取；测试没有为任何 case 手工指定顶层错误类别。第三、五、六行因此不仅说明 mapper 可能失败，也证明 mapper 之后的真实 Schema 与 Domain 边界仍可产生相同保留 metadata。

## 可证伪假设的排序与结果

1. **输出上限 / 截断。** 若历史响应为 `finish_reason=length`，真实 mapper 会在保留安全签名下给出 incomplete-output。该预测在 synthetic case 成立，但不证明历史响应满足条件。
2. **JSON 语法、object 或项目 Schema 拒绝。** 若响应为 malformed JSON 或 `{}`，真实 mapper / structured validator 会在同一签名下给出 invalid-candidate。预测成立；两者仍无法凭历史安全事实区分。
3. **非成功 Provider response shape / finish。** 若 finish 为 `content_filter`，真实 mapper 会在同一签名下给出 safe transient failure。预测成立，但没有把该 synthetic case 回推为历史事实。
4. **Schema-valid、Domain-invalid Product Intake candidate。** 若只把真实第一阶段 payload 的 `workflow_stage_decision` 改为 `waiting_input`，它会先通过 mapper 与 Schema，再被 Fast Lane domain admission 拒绝，保留同一签名。预测成立。
5. **deadline、transport 或 request construction。** 当前这些路径若在真实 runtime 中失败，会缺少成功 response 的 usage，或不能同时保留 `106434 ms < 120 s` 的返回后 acceptance boundary。这个预测与保留的非空 usage 和 latency 不符，故从本报告的 retained set 排除。

## 最小不可区分集合与限制

唯一性已经被最小 witness 推翻：`finish_reason=length` 与 malformed JSON 在相同保留安全签名下给出不同的实际类别。故无需假定更多隐藏历史事实即可证明当前 evidence 不足。

完整的代表性 retained set 还包含 empty content、non-success finish、mapped-object Schema rejection 与 schema-valid Domain rejection。在现有 application path 中，它们都会在被 `generation_failed` / safe HTTP 500 flatten 前保留不同的真实拒绝边界；安全 HTTP 500 本身不是诊断标签。

本报告不能声称：

- 任何 synthetic branch 就是历史 Provider response；
- `8192` ceiling 等于截断或需要提高 Profile；
- 真实 Provider、网络、账户、Secret、raw material、prompt 或 candidate 已被访问；
- Phase B repair 已存在、已获授权或有可执行的修复方向；
- 离线 GREEN 等于 live acceptance 或解除 `GOAL_BLOCKED`。

## 后续边界

DEC-081 要求在 `ORCHESTRATOR_REVIEWER` 独立审阅此离线证据并冻结新的 exact repair contract 后，Phase B 才可能存在；本 Phase A 不创建该合同，也不修改 production behavior。

**Proposal, not an authorized change:** 若未来需要区分同类 terminal failure，最小新增证据可以是一个非原始、有限枚举的 first-stage `rejection_disposition`。它只记录派生的拒绝边界（例如 length、empty-content、malformed-json、non-success-finish、project-schema、domain-admission），不记录 raw response、reasoning、prompt、candidate、traceback 或 Secret。是否设计、存储或暴露该字段需要单独的 Decision / repair contract；本 Issue 没有实现它。

## 最终验证

- `uv run --project apps/backend --offline pytest apps/backend/tests/integration/test_fl2_deepseek_offline_diagnosis.py apps/backend/tests/unit/test_deepseek_runtime.py apps/backend/tests/unit/test_deepseek_response_mapping.py apps/backend/tests/unit/test_deterministic_pipeline.py apps/backend/tests/unit/test_structured_output_validation.py apps/backend/tests/unit/test_product_intake_output_schema.py -q` — `207 passed`。
- `uv run --project apps/backend --offline ruff format --check apps/backend/tests/integration/test_fl2_deepseek_offline_diagnosis.py` — pass。
- `uv run --project apps/backend --offline ruff check apps/backend/tests/integration/test_fl2_deepseek_offline_diagnosis.py` — pass。
- Canonical backend type check, from `apps/backend`: `uv run pyright` — `0 errors, 0 warnings, 0 informations`。
- `git diff --check` 与 exact two-path scope audit 均通过。
