# Architecture Readiness Report v1

> **Status: DRAFT — PENDING USER REVIEW**
> **治理来源：** DEC-034（Technical Spike & Architecture Readiness Gate）
> **关联：** [Architecture Readiness Review v1 Issue #3](https://github.com/JettxonHo/ai-ecommerce-agent/issues/3) · Spike Issue #1（CLOSED）· Spike PR #2（MERGED，merge commit `a60ff3b`）
> **Spike 证据：** [../spikes/spike-001-langgraph-runtime-and-recovery/spike-report.md](../spikes/spike-001-langgraph-runtime-and-recovery/spike-report.md) · [test-results](../spikes/spike-001-langgraph-runtime-and-recovery/test-results.md) · [runtime-evidence](../spikes/spike-001-langgraph-runtime-and-recovery/runtime-evidence.md) · [limitations](../spikes/spike-001-langgraph-runtime-and-recovery/limitations.md)
> **Base Commit：** `a60ff3b6a24bf8b35e1c2ba1031038bb7123a578`（main，Spike-001 合并后）

---

## 1. Executive Summary

Spike-001 在最小、确定性、可复现、可抛弃的临时环境中，对已接受架构（DEC-023/024/029/032/033，落地契约 DEC-035）的**运行时行为**完成行为级验证：StateGraph 编译与同步 invoke、Interrupt/Resume、Checkpoint 持久化、业务/执行/Checkpoint 三类状态分离、事务回滚、幂等提交、有界重试、Stale Review 拒绝、Stale Checkpoint 防推进、检索降级不伪造、取消无部分写入、失败恢复不重复、Trace 关联、场景可复现。

- **25/25 自动化测试通过**；关键可靠性指标 **Partial Business Write Rate = 0%** · **Duplicate Business Version Rate = 0%**。
- 暴露并修复 **4 个实现层缺陷**（F-01~F-04，其中 F-01/F-02 具架构风险含义），**无架构级阻塞**，**无推翻 Accepted DEC 的候选**。
- Post-Spike Review（PR #2）未发现新的 blocking / major finding。

**核心架构在 Spike 范围内可行。** 但仍存在**明确、有限、可隔离**的未决项（并发/分布式、真实模型与检索、生产 Checkpointer、规模/性能），需在进入正式 Roadmap / Epic / Issue 拆分前以 Required RFC 收敛。

## 2. Current Status

```text
Spike Execution Status = COMPLETED（S0—S6 全部完成，Gate A—E 通过）
Architecture Readiness Status = PENDING USER REVIEW
Development Status = NOT READY
```

## 3. MVP Scope Coverage

| 范围项 | 状态 | 说明 |
|---|---|---|
| 核心价值 / 目标用户（DEC-001/002） | 规格就绪 | 业务定位先行，非本 Spike 验证对象 |
| 核心工作流（DEC-003/007/011/012/013） | 行为级验证 | Spike 微型实现：extract→insights→positioning→review→brief |
| 四大核心 Skill 契约（DEC-026/027/028/030） | 契约就绪 | 生产实现未开始；Spike 仅验证工作流骨架 |
| Human Review Contract（DEC-029） | 行为级验证 | 节点边界 + 独立提交事务 + Stale 拒绝 |
| 平台 Adapter（DEC-031） | 契约就绪 | 未在 Spike 验证（非运行时风险重点） |

> Spike 验证**架构运行时行为**，不验证业务输出质量 / 最终 Prompt / 四大 Skill 的生产逻辑。

## 4. Decision Coverage

| DEC | 主题 | 覆盖 |
|---|---|---|
| DEC-023 | LangGraph StateGraph 选型 | ✅ 编译/同步 invoke/Checkpoint 验证 |
| DEC-024 | Versioned Domain State + Compact State | ✅ 三类存储分离 + 仅存引用 |
| DEC-029 | Human Review & Approved Strategy | ✅ 节点边界 + 独立事务 + 原子提交 |
| DEC-032 | Hybrid Retrieval & Evidence Runtime | ✅ 降级不伪造、候选≠正式证据（微型） |
| DEC-033 | Failure/Recovery/Retry/Observability | ✅ 运行身份分层 + 有界重试 + Safe Resume + 幂等 + Trace |
| DEC-035 | Temporary Stack & Execution Contract | ✅ 全栈落地并锁定（`uv.lock`） |
| DEC-034 | Spike Plan & Readiness Gate | ✅ 16 项架构风险行为级验证 |

> DEC-001—DEC-022、DEC-025—DEC-028、DEC-030、DEC-031 为业务/Skill/检索/Adapter 层决策，其契约文档就绪，生产实现待 RFC。

## 5. Specification Coverage

| Spec | 覆盖 |
|---|---|
| workflow/human-review-and-approved-strategy-contract | ✅ 行为级（节点边界 / 独立提交 / Stale 拒绝 / 幂等） |
| runtime/hybrid-retrieval-and-evidence-runtime | ✅ 微型实现（降级不伪造） |
| runtime/workflow-runtime-failure-recovery-retry-and-observability | ✅ 行为级（重试/恢复/取消/Trace） |
| readiness/*（Gate / Temporary Stack / Authorization） | ✅ 流程与契约遵循 |

## 6. Architecture Coverage

- **State Model**：Graph State 仅存运行身份 + `*_version_id` 引用；Current Truth 由 `current_truth_pointer` 维护；Checkpoint 不作 Current Truth。✅
- **Runtime Boundary**：Business / Runtime / Checkpoint 三类存储物理分离。✅
- **Human Review Boundary**：`create_review_package` 与 `interrupt()` 分节点；Review Submit 独立事务。✅
- **Transaction / Idempotency**：六要素单事务提交或整体回滚；同幂等键重放不重复。✅
- **Failure / Recovery**：有界重试（仅 transient）、RetryBudgetExhausted、Safe Resume（`_require_identity` 写前拦截）、Recovery 同幂等键不重复。✅
- **Observability**：append-only JSONL Trace + 运行身份关联链 + Checkpoint Summary + JUnit。✅

## 7. Spike Evidence

- **测试**：`uv run pytest` → **25 passed / 0 failed**（unit 6 / integration 1 / review_safety 4 / transaction_idempotency 4 / failure_recovery 7 / observability 4）。
- **CLI**：`spike-01-normal-workflow` → `pass`（4 项 checks 全 true）。
- **证据导出**：`scenario-result.json` / `business-snapshot.json` / `trace.jsonl` / `checkpoint-summary.json` / `runtime-events.json` / `junit.xml`（运行时数据，不入库）。
- 详见 `test-results.md` 与 `runtime-evidence.md`。

## 8. Scenario Matrix

| 场景 | 结果 | 关键断言 |
|---|---|---|
| spike-01 Normal Workflow | ✅ | interrupted→submit→resume；truth 齐全；approved==1；partial==0 |
| spike-02 Transient Retry | ✅ | 有界重试，calls==3 成功 |
| spike-03 Invalid Structured Output | ✅ | 不重试，calls==1 |
| spike-04 Transaction Rollback | ✅ | 无部分写入，pointer 不变，partial==0 |
| spike-05 Interrupt/Resume 幂等 | ✅ | 同 thread_id 新 run_id；pos_count==1；approved==1 |
| spike-06 Duplicate Submit | ✅ | committed=False；approved==1；partial==0 |
| spike-07 Stale Review | ✅ | `StaleReviewError`；approved==1 |
| spike-08 Stale Checkpoint | ✅ | `StaleResumeError` 写前拦截；truth 不变；partial==0 |
| spike-09 Retrieval Fallback | ✅ | degraded → candidates==[]/coverage=none，不伪造 |
| spike-10 Cancellation | ✅ | 无 approved_strategy；partial==0 |
| spike-11 Retry Budget Exhaustion | ✅ | `RetryBudgetExhausted`；无无限重试 |
| Recovery Case | ✅ | 同幂等键重试 committed=True；仅一个版本 |
| Trace Correlation | ✅ | 单 trace 贯穿 + 关联断言 |

## 9. Findings

> 全部为 **Implementation Bug**（实现层，已修复，含回归测试）。无 Architecture Blocking Failure。

| ID | 类别 | 摘要 | 状态 |
|---|---|---|---|
| F-01 | Implementation（具架构风险含义） | Stale Review 未被拒绝 | FIXED（`3934baa`） |
| F-02 | Implementation（具架构风险含义） | Stale/foreign Checkpoint 可在错误身份下推进 | FIXED（`3934baa`） |
| F-03 | Implementation | review_package pointer 生命周期 | FIXED（`bdc9fb4`） |
| F-04 | Implementation | Fault 注入时机 | FIXED（`1cdb313`） |

Post-Spike Review 未发现新的 blocking / major / minor / documentation finding。

## 10. Blocking Risks

**无新增 blocking risk。** Spike 范围内的架构运行时行为全部通过；无影响核心 Domain Model / 事务边界 / 权限边界 / Resume 正确性的未解决阻塞。

## 11. Non-blocking Limitations

| ID | 限制 | 影响 |
|---|---|---|
| R-1 | 并发/分布式未验证（单线程同步） | 生产部署前需并发模型与一致性 RFC |
| R-2 | 真实模型/检索质量未验证（Scripted/Mock） | 需真实模型 Smoke 与检索 RFC |
| R-3 | 生产 Checkpointer 未锁定（SQLite 临时） | 换 Postgres/Redis 需重新验证 Safe Resume 与序列化 |
| R-4 | 规模/性能未验证 | 需性能基线与 Checkpoint 体积 RFC |

> 上述**不**削弱 Spike 已验证的行为级结论，但属进入 READY 前必须补足的「未验证清单」。

## 12. Required RFCs

进入 Implementation Planning 前建议补齐（清单与优先级见 [../rfcs/rfc-register.md](../rfcs/rfc-register.md)；本报告**不替用户接受任何 RFC**）：

1. Repository and Application Architecture
2. Persistence and Transaction Architecture
3. LangGraph Runtime and Checkpoint Architecture
4. API and Human Review Protocol
5. Source Processing and Retrieval Architecture
6. LLM Runtime and Structured Output
7. Observability and Runtime Operations

## 13. Allowed Next Work（建议，待用户确认）

- 起草并接受上述 Required RFC。
- 形成 / 完善 Architecture Baseline v1（见 [../architecture/architecture-baseline-v1.md](../architecture/architecture-baseline-v1.md)）。
- 进行 Implementation Planning（仅规划，非生产实现）。
- 维护 Traceability Matrix 的 Future Placeholder。

## 14. Prohibited Next Work（在用户明确确认前）

- 开始未经 RFC 支持的生产实现。
- Coding Agent 临场选择生产数据库 / Checkpointer / API / ORM / Retrieval / Observability。
- 将 Spike 代码直接迁移为生产模块。
- 创建正式 MVP Roadmap / Epic / 生产业务 Issue。
- 将 Development Status 改为 READY。

## 15. Readiness Recommendation（仅建议）

> `Claude Recommendation ≠ READY`。最终 READY / CONDITIONALLY READY / NOT READY 由用户人工 Gate 明确确认。

**RECOMMENDED: CONDITIONALLY READY**

理由：
- Spike 范围内**架构运行时行为全部通过**，核心架构**可行**。
- 暴露的 4 个缺陷均为**可隔离、已修复、有回归测试**的实现层问题；**无**未解决的核心架构阻塞。
- 存在**明确、有限、可隔离**的未决项（R-1~R-4），需以 Required RFC 收敛后方可开始对应生产实现。

**Conditions（条件）：**
- 允许开始 Architecture RFC 与 Implementation Planning。
- **不允许**开始未经 RFC 支持的生产实现。
- **不允许** Coding Agent 临场选择生产数据库 / Checkpointer / API / ORM / Retrieval / Observability。
- 对应生产模块开始前必须先接受相关 RFC。

## 16. User Decision

```text
PENDING
```

> 由用户在人工 Gate 后填写：READY / CONDITIONALLY READY / NOT READY，及允许范围与条件。**本报告不替用户填写 READY。**

## 17. Final Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = PENDING USER REVIEW
Development Status = NOT READY
```

> 本报告的提交**不**改变上述状态；不 Merge Readiness PR、不关闭 Readiness Issue、不自行宣布 READY、不创建 MVP Roadmap、不开始生产开发。等待用户最终人工 Gate。
