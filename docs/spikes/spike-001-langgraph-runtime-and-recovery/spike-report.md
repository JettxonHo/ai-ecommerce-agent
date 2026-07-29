# Spike-001 — Spike Report（报告与 Readiness Recommendation）

> **Status: S6 — EXECUTION COMPLETE**
> **治理来源：** DEC-034 · DEC-035 · DEC-036 · DEC-037
> **Spike Issue：** [#1](https://github.com/JettxonHo/ai-ecommerce-agent/issues/1) · **Draft PR：** [#2](https://github.com/JettxonHo/ai-ecommerce-agent/pull/2) · **Branch：** `spike/001-langgraph-runtime-recovery`
> **最终测试：** `uv run pytest` → **25 passed**（0 failed）
> **关联文档：** [implementation-notes](./implementation-notes.md) · [test-results](./test-results.md) · [runtime-evidence](./runtime-evidence.md) · [limitations](./limitations.md)

---

## 1. Executive Summary

Spike-001 在最小、确定性、可复现、可抛弃的临时环境中，验证了已接受架构（DEC-023/024/029/032/033，落地契约 DEC-035）的**运行时行为**：StateGraph 编译与同步 invoke、Interrupt/Resume、Checkpoint 持久化、业务状态与执行状态分离、事务回滚、幂等提交、有界重试、Stale Review 拒绝、Stale Checkpoint 防推进、检索降级不伪造、取消无部分写入、失败恢复不重复、Trace 关联、场景可复现。

全部 6 个阶段（S0—S6）完成，Gate A—E 通过，25 个自动化测试全部通过，关键可靠性指标达成：`Partial Business Write Rate = 0%` · `Duplicate Business Version Rate = 0%` · 无无限重试 · Resume 幂等。

过程中暴露并修复了 **4 个实现层缺陷**（F-01~F-04），其中 F-01/F-02 属「若不修复即架构风险」类——它们在最小环境中被发现，正是 Spike 的价值。**未发现需要推翻任何 Accepted DEC 的架构级阻塞。**

## 2. Spike Objective 覆盖（DEC-034 验证目标）

| 验证目标 | 结果 | 证据 |
|---|---|---|
| StateGraph 执行 | ✅ | S0/S1，graph 编译 + 同步 invoke |
| Interrupt / Resume | ✅ | S1/S2，spike-01/05 |
| Checkpoint 持久化 | ✅ | S0/S5，checkpoint-summary 含本线程 |
| 业务/执行状态分离 | ✅ | S0，三类 SQLite 物理分离 |
| Transaction Rollback | ✅ | S3，spike-04（无部分写入） |
| Idempotency | ✅ | S3，spike-06 / 重复提交不重复版本 |
| Retry（有界） | ✅ | S4，spike-02/11 |
| Stale Review 拒绝 | ✅ | S2，spike-07 |
| Stale Checkpoint 拒绝 | ✅ | S2，spike-08 |
| Retrieval Fallback | ✅ | S4，spike-09（降级不伪造） |
| Cancellation | ✅ | S4，spike-10（无部分写入） |
| Manual Recovery | ✅ | S4，recovery case（同幂等键不重复） |
| Trace Correlation | ✅ | S5，单 trace 贯穿 + 关联断言 |

DEC-034 的 16 项架构风险在本 Spike 的最小范围内均得到行为级验证（详见 `runtime-evidence.md`）。

## 3. Findings（发现）

> 全部为 **Implementation Bug**（实现层，已修复），无 Architecture Blocking Failure，无推翻 Accepted DEC 的候选。

### F-01 — Stale Review 未被拒绝（Architecture Risk → 已修）
- **Category：** Implementation Bug（具架构风险含义） · **Scenario：** spike-07
- **Expected：** 已提交的 Review Package 不能二次提交产生重复 Approved Strategy。
- **Actual：** 原 stale 判定只看 `current_truth_pointer`，提交后未失效旧包 → 仍可提交。
- **Reproduction：** 提交后用过期 package + 新幂等键再次 `submit`。
- **Relevant Commit：** 修复于 `3934baa` · **Relevant Trace：** `review_submit` 事件。
- **Root Cause Hypothesis：** pending package 生命周期未建模（提交后未 supersede/清 pointer）。
- **Affected Decisions/Specs：** DEC-029（No stale Review Package submission）。
- **Candidate Options：** (a) 提交后 supersede + 删除 pending pointer（采用）；(b) 仅标状态。
- **Recommended Action：** 采用 (a)。**Execution Status：** FIXED，由 spike-06/07 回归验证。

### F-02 — Stale/foreign Checkpoint 可在错误身份下推进（Architecture Risk → 已修）
- **Category：** Implementation Bug（具架构风险含义） · **Scenario：** spike-08
- **Expected：** 无匹配 checkpoint 的 resume 不得写业务数据。
- **Actual：** `Command(resume)` 在空 state 下从 START 运行，节点缺 `task_id` → 可能在错误身份下写入。
- **Reproduction：** 用 foreign `thread_id` 调 `Command(resume=...)`。
- **Relevant Commit：** 修复于 `3934baa` · **Root Cause：** 节点入口未校验运行身份。
- **Affected Decisions/Specs：** DEC-024（Checkpoint ≠ Current Truth）、DEC-033（Safe Checkpoint Resume）。
- **Candidate Options：** (a) 节点入口 `_require_identity` 写前拦截（采用）；(b) 依赖 LangGraph 默认行为。
- **Recommended Action：** 采用 (a)。**Execution Status：** FIXED，由 spike-08 回归验证。

### F-03 — review_package pointer 生命周期（Implementation Bug → 已修）
- **Category：** Implementation Bug · **Scenario：** S3 pointer validation
- **Expected：** Current Truth Pointer 始终指向 `valid` 版本。
- **Actual：** 提交后 `review_package` pointer 仍指向已 supersede 版本。
- **Relevant Commit：** `bdc9fb4` · **Affected：** DEC-029（Review Package ≠ Current Truth after submit）。
- **Recommended Action：** 提交后删除 pending `review_package` pointer（Approved Strategy 成为新 truth）。**Execution Status：** FIXED。

### F-04 — Fault 注入时机（Implementation Bug → 已修）
- **Category：** Implementation Bug · **Scenario：** spike-02/11
- **Expected：** 瞬态故障应发生在工作调用**期间**，使真实尝试计入重试。
- **Actual：** 原 `run_with_retry` 在 `fn()` 前注入，拦截了真实工作调用。
- **Relevant Commit：** `1cdb313` · **Root Cause：** 注入点设计。
- **Recommended Action：** 改为 `FaultPlan.call` 在调用期间注入。**Execution Status：** FIXED，由 spike-02/11 回归验证。

## 4. Reliability Evidence（可靠性证据）

| 指标 | 目标 | 实测 |
|---|---|---|
| Partial Business Write Rate | 0% | **0%** |
| Duplicate Business Version Rate | 0% | **0%** |
| approved_strategy_version_count（正常流） | == 1 | **1** |
| 无限重试 | 禁止 | 有界（spike-11 预算耗尽） |
| Resume 幂等 / Positioning 不重生 | 是 | 是（spike-05） |
| Stale Review / Stale Checkpoint | 拒绝 | 拒绝（spike-07/08） |
| Trace 关联 | 全链 | 单 trace + 关联断言（S5） |

证据细节见 `runtime-evidence.md`；逐场景断言见 `test-results.md`。

## 5. Specification / Decision Coverage

- **DEC-024**（状态四类边界）：✅ 三类存储分离 + 紧凑 Graph State（仅存引用）。
- **DEC-029**（Human Review / Approved Strategy / 原子提交）：✅ 三节点边界 + 独立 Review Submit 事务 + 原子提交。
- **DEC-032**（检索与证据装配）：✅ 降级不伪造、候选≠正式证据（微型实现）。
- **DEC-033**（失败恢复 / 重试 / 可观测）：✅ 运行身份分层 + 有界重试 + Safe Resume + 幂等提交 + Manual Recovery + Trace。
- **DEC-035**（临时栈与执行契约）：✅ 全栈落地并锁定。
- **DEC-034**（Spike 计划与 Readiness Gate）：✅ 16 项架构风险行为级验证。

## 6. Open Risks（未决风险）

- **R-1（并发/分布式未验证）**：单线程同步模型未覆盖并发 Checkpoint、多任务锁、多副本一致性。→ 进入生产前需 RFC。
- **R-2（真实模型/检索未验证）**：Scripted/Mock 不代表真实 LLM 与检索质量。→ 真实模型 Smoke 与检索 RFC。
- **R-3（生产 Checkpointer 未锁定）**：SQLite 临时；换 Postgres/Redis 需重新验证 Safe Resume 与序列化。→ Checkpointer RFC。
- **R-4（规模/性能未验证）**：未测大规模性能与 Checkpoint 体积。→ 性能基线 RFC。

> 上述均**不**影响本 Spike 已验证的行为级结论，但属进入 READY 前必须补足的「未验证清单」。

## 7. Required RFC List（必需 RFC 清单）

进入 Implementation Planning 前建议补齐（编号待定，属后续 Decision，不在本 Spike 内创建）：

1. **RFC: Production Checkpointer 选型**（Postgres/Redis/其他 + Safe Resume + 序列化兼容）。
2. **RFC: 并发与任务锁模型**（多任务 / 多副本 / 分布式 Checkpoint 一致性）。
3. **RFC: 生产 LLM Provider 与真实模型 Smoke 测试策略**（含 Secret 注入边界）。
4. **RFC: 生产 Retrieval 运行时**（词法/向量/融合 + 权限与版本过滤 + 证据装配）。
5. **RFC: 生产数据库与 ORM**（Business Repository 持久化）。
6. **RFC: Observability Provider**（结构化日志 / Tracing / Metrics，是否 OpenTelemetry）。
7. **RFC: Retry/Timeout/Backoff/Circuit Breaker 生产参数**。

## 8. Readiness Recommendation

> **仅为建议。** `Claude Recommendation ≠ READY`。最终 READY / CONDITIONALLY READY / NOT READY 由用户在审查 Issue / PR Diff / 测试 / 证据 / Findings / 本报告后，经人工 Gate 明确确认。

**RECOMMENDED: CONDITIONALLY READY**

理由：
- 本 Spike 范围内的**架构运行时行为全部通过**（25/25 测试、关键可靠性指标 0% 失败、无无限重试、Resume 幂等、Stale 双拒绝）。核心架构**可行**。
- 暴露的 4 个缺陷均为**可隔离、已修复、有回归测试**的实现层问题；**无**影响核心 Domain Model / 事务边界 / 权限边界 / Resume 正确性的**未解决**架构阻塞。
- 但仍存在**明确、有限、可隔离**的未决项（Open Risks R-1~R-4：并发/分布式、真实模型与检索、生产 Checkpointer、规模/性能），需在进入正式 Roadmap / Epic / Issue 拆分前以上述 **Required RFC List** 收敛。

**允许开始的方向（建议）**：在临时栈已验证的行为契约基础上，起草上述 RFC 与 Architecture Baseline v1。
**禁止开始的方向（建议）**：在选择生产 Checkpointer / 并发模型 / 生产数据库前，不开始正式生产开发；不将 Spike 代码直接迁移为生产模块。

## 9. User Decision（待用户填写）

> （由用户在人工 Gate 后填写：READY / CONDITIONALLY READY / NOT READY，及允许范围与条件。）

## 10. Final Status

```text
Spike Execution Status = COMPLETED（S0—S6 全部完成，Gate A—E 通过）
Architecture Readiness Status = PENDING USER REVIEW
Development Status = NOT READY
```

> S6 不自动改变 Development Status；不 Merge PR、不关闭 Issue、不自行宣布 READY、不创建 MVP Roadmap、不开始生产开发。等待用户最终人工 Gate。
