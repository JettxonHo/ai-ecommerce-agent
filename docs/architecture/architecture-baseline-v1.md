# Architecture Baseline v1

> **Status: DRAFT — Current Architecture Truth（基于已接受 DEC-001—DEC-037 综合）**
> **治理来源：** 本文件综合当前**已接受**的 DEC 与 Specs，形成 Current Architecture Truth。**不发明任何新的生产技术选择。**
> **关联：** [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md) · [../rfcs/rfc-register.md](../rfcs/rfc-register.md) · Spike-001（MERGED）
> **Base Commit：** `a60ff3b6a24bf8b35e1c2ba1031038bb7123a578`

---

## 0. 本文档定位与纪律

- 本文件描述「系统当前应该怎样工作」，内容**只能来自用户明确接受的 Decision**。
- Spike-001 的临时技术选择**一律标注** `Validated Temporary Implementation / Not Production Commitment`，**不**视为生产承诺。
- 任何尚未通过 RFC + Accepted Decision 收敛的生产技术（数据库 / Checkpointer / API / ORM / Retrieval / Observability / 部署平台）在本文件中标记为 **`PENDING RFC`**，**不得**由 Coding Agent 临场选择。

## 1. 系统分层（System Architecture）

> 来源：DEC-011 / DEC-012 / DEC-013 / DEC-021 / DEC-023 / DEC-024。

- **确定性 Workflow 编排**：以 StateGraph 表达核心工作流，LLM 推理受约束（DEC-011 / DEC-023）。
- **单审查节点 + 异常暂停**：核心流程单一 Human Review 节点，异常路径可暂停（DEC-007）。
- **MVP 不采用 Multi-Agent**：保留 Bounded Worker 扩展空间（DEC-021）。
- **分层状态**：业务状态 / 执行状态 / 检索证据 / Checkpoint 分离（DEC-012 / DEC-013 / DEC-024）。
- **任务级持久状态**：支持跨会话 Resume（DEC-013）。

```text
[Product Input] -> [Workflow Orchestration (StateGraph)]
   -> Skill Nodes (facts / insights / positioning / review / brief)
   -> [Human Review Node] -> [Approved Strategy]
   -> [Platform Adapter (Xiaohongshu brief mapping)]
```

## 2. 状态与版本模型（State & Versioning）

> 来源：DEC-024 / DEC-025 / DEC-029 / DEC-033。Spike 行为级验证：✅。

- **Versioned Domain State**：业务域以 Domain Version 演进；`current_truth_pointer` 指向当前有效版本；旧版本 `superseded`。
- **Compact Graph State**：Graph State 仅存运行身份 + `*_version_id` 引用，不存业务正文。
- **三类存储分离**：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）物理分离；**Checkpoint ≠ Current Truth**。
- **运行身份分层（DEC-033）**：`task_id` / `workflow_run_id` / `skill_run_id` / `node_execution_id` / `attempt_id` / `error_id` / `trace_id` / `recovery_case_id` 全链可关联。

## 3. 事务与幂等（Transaction & Idempotency）

> 来源：DEC-029 / DEC-033。Spike 行为级验证：✅。

- **原子提交契约**：每次正式业务提交在**一个事务**内完成：Create Domain Version + Evidence Links + Update Current Truth Pointer + Update Stage State + Business Audit + Idempotency Record；任一失败整体回滚。
- **幂等**：同一逻辑幂等键重放不产生重复版本；Retry / Recovery 复用同一幂等键。
- **节点不绕过**：Graph 节点不直接写 Current Truth，统一经 Business Commit 路径。

## 4. Human Review 与 Approved Strategy

> 来源：DEC-029。Spike 行为级验证：✅。

- **节点边界**：`create_review_package`（构建固定版本包，幂等）与 `interrupt()`（暂停等待）**分离**；Review Submit 为**独立业务事务**。
- **No Stale Submission**：过期/已 supersede 的 Review Package 不得再次提交（拒绝）。
- **Safe Resume**：Resume 使用相同 `thread_id` + 新 `run_id`，不重建 Review Package、不重生成 Positioning；stale/foreign Checkpoint 在业务写入前被拒绝。

## 5. 检索与证据（Retrieval & Evidence）

> 来源：DEC-014 / DEC-025 / DEC-032。Spike 微型验证：✅（降级不伪造）。

- **On-demand Hybrid RAG**：按需混合检索（词法/向量/融合），分层数据访问（DEC-014）。
- **Versioned Sources / Fragments / Evidence Links**：来源与证据版本化、可追溯（DEC-025）。
- **降级不伪造**：检索降级时记录 degraded 状态，不伪造候选或覆盖度。
- **生产实现**：`PENDING RFC`（Source Processing and Retrieval Architecture）。

## 6. 运行时失败 / 恢复 / 重试 / 可观测（Runtime Reliability）

> 来源：DEC-033。Spike 行为级验证：✅。

- **有界重试**：仅重试 transient 基础设施错误；non-transient（如 Invalid Structured Output）不重试；预算耗尽抛 `RetryBudgetExhausted`（无无限重试）。
- **取消无部分写入**：取消后不留 partial business state。
- **Manual Recovery**：失败提交经同一幂等键恢复，不重复。
- **Observability**：结构化 Trace + 运行身份关联 + Checkpoint Summary + JUnit（**生产 Provider `PENDING RFC`**）。

## 7. 集成边界（Integration Boundaries）

> 来源：DEC-004 / DEC-020 / DEC-031。

- **平台中立核心 + Xiaohongshu Demo**（DEC-004）。
- **MVP 四大核心 Skill + Xiaohongshu Adapter**（DEC-020）。
- **Xiaohongshu Brief Mapping Adapter 契约**（DEC-031）。
- **生产 API / Human Review Protocol**：`PENDING RFC`。

## 8. 临时技术栈（Spike-001）

> 以下仅为 Spike-001 的**临时**落地，**不构成生产承诺**。

```text
Validated Temporary Implementation — Not Production Commitment
- Python 3.13（uv 管理）          [临时]
- LangGraph StateGraph 1.2.9      [临时，精确固定]
- Synchronous Invoke              [临时]
- 三个分离 SQLite + SqliteSaver   [临时 Checkpointer]
- Python sqlite3 Transactions     [临时]
- Scripted Model + Mock Retrieval [临时]
- pytest + 本地 JSONL Trace + CLI [临时]
```

> 生产后端语言 / 数据库 / Checkpointer / ORM / LLM / Retrieval / Observability / 部署平台：**全部 `PENDING RFC`**（见 [../rfcs/rfc-register.md](../rfcs/rfc-register.md)）。

## 9. 未决技术决策（PENDING RFC）

| 领域 | 状态 |
|---|---|
| Repository and Application Architecture | PENDING RFC |
| Persistence and Transaction Architecture（生产 DB / ORM） | PENDING RFC |
| LangGraph Runtime and Checkpoint Architecture（生产 Checkpointer） | PENDING RFC |
| API and Human Review Protocol | PENDING RFC |
| Source Processing and Retrieval Architecture | PENDING RFC |
| LLM Runtime and Structured Output | PENDING RFC |
| Observability and Runtime Operations | PENDING RFC |

> 上述在生产实现前必须先经 RFC 提案 + 用户 Accepted Decision 收敛；**不得**临场选择。

## 10. Final Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = PENDING USER REVIEW
Development Status = NOT READY
```
