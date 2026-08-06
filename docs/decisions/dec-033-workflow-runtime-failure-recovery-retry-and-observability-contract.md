# DEC-033：Workflow Runtime 采用分层运行记录、分类故障处置、有界重试、安全恢复、事务幂等与端到端可观测性契约

> **Type:** Runtime Architecture / Reliability Architecture / Observability Architecture
> **Status:** Accepted
> **Date:** 2026-07-29
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)（概念 Runtime Spec，仅概念）
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** DEC-023、DEC-024、DEC-029（在 LangGraph StateGraph 选型、版本化 Domain State 与四标识符边界、Human Review and Approved Strategy Contract 基础上，正式定义 Workflow Runtime 的运行身份分层、有界技术恢复、Checkpoint 与业务状态协调、Human Review Resume 可靠行为与端到端可观测性；**不推翻** DEC-023 / DEC-024 / DEC-029 既有结论）。
> **Amended by:** [DEC-049](dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md) 收敛生产 Checkpoint 与对账边界；[DEC-050](dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md) 收敛 Durable Dispatch、Lease / fencing 与协作式取消；[DEC-051](dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md) 收敛显式兼容、Safe Resume Action Matrix、迁移 / 回滚与验收证据。其余概念契约保持有效。

---

## 用户确认

用户对该 Workflow Runtime Failure Recovery, Retry and Observability Contract Proposal 明确回复：

> 确认

本决定经 Decision Gate 通过，记录为 Accepted Decision（Type: Runtime Architecture / Reliability Architecture / Observability Architecture）。对应 DEC-032 的「下一议题」（Workflow Runtime Failure Recovery, Retry and Observability Contract）。

被接受的核心结论：

- Workflow Runtime 的失败恢复、重试与可观测性是**跨 Skill 的共享运行架构层**（非 Core Skill Contract、非 Platform Adapter Contract、非 Retrieval Runtime）。它服务于所有 Skill、Evidence Validator、Human Review、Tool 调用与业务事务，提供统一的执行身份分层、错误分类、有界重试、显式降级、安全 Checkpoint 恢复、事务幂等与端到端可观测性。
- 核心原则：**业务等待不等于技术失败；技术 Retry 不等于业务 Rerun；Checkpoint 不等于业务 Current Truth；任何失败恢复都不能绕过业务版本、Evidence Validator、Review Package 或 Current Truth 规则。**
- 本决定承接并**收紧**既有约束：Retry / Rerun 边界、Partial Write Prevention、Checkpoint 职责边界与 Business Wait 概念在 DEC-029（Human Review 事务）等决定中已有雏形，本决定将其统一形式化为运行时契约。本决定**不**实现正式 Retry Middleware / Tracing / Alerting / Recovery Worker / Worker / Queue 等任何业务或基础设施代码，**不**选择具体重试参数、Timeout 秒数、可观测性 Provider、数据库、Outbox 或分布式锁。

---

## Decision

AI Ecommerce Agent 的 Workflow Runtime 正式采用：

```text
Layered Runtime Records
+
Structured Error Classification
+
Bounded Retry
+
Explicit Fallback
+
Safe Checkpoint Resume
+
Transactional and Idempotent Commit
+
Manual Recovery
+
End-to-end Observability
```

核心原则：

> 业务等待不等于技术失败；技术 Retry 不等于业务 Rerun；Checkpoint 不等于业务 Current Truth；任何失败恢复都不能绕过业务版本、Evidence Validator、Review Package 或 Current Truth 规则。

整体运行链路：

```text
Task
↓
Workflow Run / Resume
↓
Skill Run
↓
Node Execution
↓
Execution Attempt
↓
LLM / Retrieval / Tool / Repository Calls
↓
Structured Candidate Output
↓
Deterministic Validation
↓
Transactional Business Commit
↓
Checkpoint + Runtime Records + Trace + Metrics
```

---

## Runtime Hierarchy

运行时必须区分以下层级：

```text
Task
Workflow Run
Skill Run
Node Execution
Execution Attempt
```

### Task

`task_id` 表示长期存在的业务任务。Task 可以跨越：多次 Workflow Run；多次暂停与恢复；多次人工审核；多次阶段 Rerun；多个业务版本；多次失败恢复。Task 不等于一次程序执行。

### Workflow Run

继续使用 DEC-024 中定义的 `run_id`，它表示一次工作流调用、恢复或明确重跑。同一个业务 Task 可以拥有多个 Run。`thread_id` 用于关联同一 LangGraph 执行线程。

### Skill Run

每次核心业务 Skill 执行必须创建 `skill_run_id`。Skill Run 至少关联：`task_id` / `run_id` / `skill_name` / `input_version_ids` / `source_set_version_id` / `skill_contract_version` / `execution_configuration_version`。

### Node Execution

每个可恢复、可观测的执行节点创建 `node_execution_id`。例如：`build_evidence_package` / `generate_fact_candidates` / `validate_fact_candidates` / `commit_fact_version`。

### Execution Attempt

同一 Node 因技术故障重试时，为每次尝试创建 `attempt_id` / `attempt_number`。重试不会自动创建新的 Skill Run 或业务版本。

---

## Identifier Model

沿用 `task_id` / `thread_id` / `run_id` / `checkpoint_id`；新增 `skill_run_id` / `node_execution_id` / `attempt_id` / `error_id` / `trace_id` / `recovery_case_id`。相关能力还可能关联 `retrieval_run_id` / `evidence_package_id` / `review_id` / `tool_call_id` / `model_call_id` / `source_version_id`。这些 ID 必须能够形成完整的执行关联链。

---

## Retry and Rerun Boundary

必须正式区分 `Retry ≠ Rerun`。

### Retry

Retry 表示：同一逻辑操作、同一输入、同一幂等身份，因为暂时性技术故障再次尝试。例如：网络短暂中断；LLM 请求超时；429 限流；数据库连接暂时失败；Retrieval Service 暂时不可用。

Retry 的特征：

```text
Same Skill Run
Same Node Execution
Different Attempt
Same Logical Input
Same Idempotency Identity
```

Retry 不得创建新的业务版本。

### Rerun

Rerun 表示：因用户明确要求、上游版本变化、业务输出失效或执行配置变化，启动新的业务计算。例如：用户补充资料；Facts Version 变化；Approved Strategy 被撤回；用户要求重新分析；Skill Contract 或执行配置升级后重新运行。Rerun 应创建新的 `run_id` / `skill_run_id`，并可能创建新的业务候选版本。

正式边界：

```text
Retry
= Technical Recovery
Rerun
= New Business Computation
```

---

## Runtime Records

### Workflow Run Record

概念结构：

```text
WorkflowRun
├── run_id
├── task_id
├── thread_id
├── trigger_type
├── resumed_from_checkpoint_id
├── started_at
├── completed_at
├── status
├── current_stage
├── initiator
├── cancellation_requested_at
├── failure_summary
└── trace_id
```

`trigger_type` 概念类型：`initial_start` / `user_resume` / `human_review_resume` / `automatic_retry` / `explicit_rerun` / `recovery_resume`。

### Skill Run Record

```text
SkillRun
├── skill_run_id
├── task_id
├── run_id
├── skill_name
├── skill_contract_version
├── execution_configuration_version
├── input_version_ids[]
├── source_set_version_id
├── evidence_package_id
├── input_fingerprint
├── started_at
├── completed_at
├── status
├── output_version_id
├── failure_disposition
└── retry_count
```

### Node Execution Record

```text
NodeExecution
├── node_execution_id
├── skill_run_id
├── node_name
├── node_type
├── input_fingerprint
├── started_at
├── completed_at
├── status
├── attempt_count
├── output_reference
├── checkpoint_id
├── error_id
└── trace_span_id
```

### Execution Attempt Record

```text
ExecutionAttempt
├── attempt_id
├── node_execution_id
├── attempt_number
├── started_at
├── completed_at
├── status
├── provider_or_component
├── timeout_deadline
├── retry_reason
├── request_reference
├── response_reference
├── error_id
└── usage_metadata
```

以上是概念结构，不是最终数据库 Schema。

---

## Runtime Status Boundary

Workflow Run、Skill Run 和 Node Execution 不共用完全相同的状态语义。

### Workflow Run Status

概念状态：`queued` / `running` / `waiting_for_input` / `waiting_for_review` / `paused` / `completed` / `failed` / `cancelled`。

### Skill Run Status

概念状态：`queued` / `running` / `validating` / `committing` / `succeeded` / `succeeded_with_limitations` / `failed` / `cancelled` / `superseded`。

### Node Execution Status

概念状态：`queued` / `running` / `retry_scheduled` / `succeeded` / `failed` / `timed_out` / `cancelled` / `skipped`。

最终状态名称尚未确认，但各层语义必须明确分离。

---

## Business Control State and Technical Failure

以下状态属于**业务控制状态**，而不是技术失败：`waiting_for_input` / `waiting_for_review` / `paused`。

- `waiting_for_input`：例如缺少必须商品资料；用户要求评论分析但未提供评论；关键 Source 尚未上传；用户明确拒绝降级模式；缺少账号、品牌或商业上下文。
- `waiting_for_review`：例如 Positioning Candidates 已生成；Review Package 已创建；用户尚未提交审核；用户只保存了 Strategy Draft。
- `paused`：例如商品身份冲突；Current Product 与 Competitor 数据混淆；Source 权限被撤回；高风险声明需要人工处理；Approved Strategy 被撤回；数据污染或完整性问题需要人工解决。

业务等待和暂停不得：自动按技术错误反复重试；记录为 Provider Failure；触发基础设施故障告警；被描述为系统崩溃。

---

## Error Taxonomy

采用统一的结构化错误分类。

- **Transient Infrastructure Error**：临时网络故障 / DNS 故障 / 服务短暂不可用 / 数据库连接中断 / 临时锁冲突。通常可重试。
- **Rate Limit Error**：LLM 429 / Retrieval Service 限流 / 外部 API 配额限制。允许有限重试，但必须尊重 `Retry-After` 和整体 Deadline。
- **Timeout Error**：Model Call Timeout / Retrieval Timeout / Tool Call Timeout / Node Deadline / Skill Deadline。是否重试取决于操作幂等性 / 剩余 Deadline / 已执行 Attempt 数量 / 是否存在 Side Effect。
- **Structured Output Error**：JSON 不合法 / 缺少必填字段 / Enum 不合法 / ID 格式错误 / 输出不符合 Skill Schema。允许有限次数的结构修复或重新生成。无效自由文本不得写入 Current Truth。
- **Validation Error**：Fact ID 无效 / Proof Point 无证据 / Competitor Capability Leakage / Hypothesis 被写成 Fact / Evidence Limitation 丢失 / Strategy Drift / Fabricated Customer Quote。这类错误不能通过普通基础设施 Retry 掩盖。可进行有限的候选修正或当前 Node 重新生成。
- **Permission or Authentication Error**：Source 权限失效 / Workspace Access 被撤回 / Credential 无效。默认不可自动重试，应进入暂停或人工处理。
- **Data Integrity Error**：Current Truth Pointer 指向不存在版本 / Evidence Link 引用不存在 Fragment / Task 与 Source Task 不一致 / Checkpoint 与业务版本不一致 / 事务状态不完整。属于高严重性错误，不得由 LLM 自行修复。
- **Dependency Configuration Error**：模型配置不存在 / Retrieval Component 未配置 / Schema Version 不支持 / 必需 Repository 未连接 / Index Version 不兼容。通常不可自动重试。
- **Provider Content Rejection**：模型或工具供应商因内容规则拒绝请求时，不得伪装为网络错误，不得无限重试，必须记录拒绝类别，根据业务允许范围决定降级、暂停或失败。
- **Cancellation**：用户或系统主动取消运行。Cancellation 不属于 Failure。

---

## Runtime Error Record

概念结构：

```text
RuntimeErrorRecord
├── error_id
├── task_id
├── run_id
├── skill_run_id
├── node_execution_id
├── attempt_id
├── error_code
├── error_category
├── severity
├── retryability
├── failure_disposition
├── component
├── user_safe_message
├── operator_message
├── cause_chain[]
├── input_version_ids[]
├── provider_error_reference
├── first_occurred_at
├── last_occurred_at
└── remediation_options[]
```

- **Severity**：`info` / `warning` / `error` / `critical`。
- **Retryability**：`retryable` / `conditionally_retryable` / `non_retryable` / `unknown`。
- **Failure Disposition**：`retry` / `fallback` / `wait` / `pause` / `fail` / `cancel` / `manual_recovery`。

用户只能看到安全、可操作的 `user_safe_message`。内部敏感信息、Prompt、Secret 和未脱敏堆栈不得直接展示给用户。

---

## Retry Policy

自动 Retry 必须满足：仅适用于明确可重试错误；有最大 Attempt 数；有时间上限；有总体 Deadline；有结构化日志；支持取消；保持幂等；不产生重复业务版本。

默认策略原则：

```text
Bounded Retry
+
Exponential Backoff
+
Jitter
+
Respect Retry-After
+
Overall Deadline
```

本决定不确认具体次数、间隔和秒数。

---

## Retry Budget

Runtime 应统一协调 `per_attempt_timeout` / `per_node_retry_limit` / `per_skill_retry_budget` / `per_workflow_run_deadline`。必须避免嵌套重试放大，例如 `Workflow Retry × Skill Retry × Tool Internal Retry`。各层组件不得独立无限重试。Runtime 应控制总体 Retry Budget。

---

## LLM Structured Output Recovery

正式处理顺序：

```text
1. Receive model output
2. Parse output
3. Validate schema
4. Apply deterministic normalization
5. Perform constrained repair
6. Regenerate current node if permitted
7. Fail after bounded attempts
```

### Deterministic Normalization

只允许语义不变的修复，例如：去除 Markdown JSON Fence；修复明确的尾随逗号；标准化已知 Enum 大小写；补充可确定的容器结构。不得：猜测缺失业务事实；创造 Fragment ID；自动补充 Proof Point；将任意自由文本推断为正式业务字段。

### Constrained Repair

可向模型返回 Schema 错误 / 缺失字段 / 非法 Enum / 无效引用 / Validator 拒绝原因。Repair 只能修正当前候选输出，不得扩大 Source Scope、改变输入版本或绕过权限。达到修复上限后 `error_category = structured_output_error`，`failure_disposition = fail`。无效输出不得写入 Current Truth。

---

## Evidence Validator Failure

当 Schema 合法，但业务候选违反硬性证据规则时，可以有限执行 `candidate_regeneration`。Validator 错误必须作为结构化反馈返回。例如：Invalid Fragment Reference；Current Product / Competitor Scope Error；Unsupported Proof Point；Fabricated Quote；Top-K Frequency Extrapolation；Strategy Drift。

若模型重复违反相同硬规则：停止自动修复；Skill Run 标记失败；保留失败候选供调试与评估；不创建业务版本；不创建 Formal Evidence Link；不更新 Current Truth。

---

## Retrieval Failure

遵循 DEC-032。

- **Semantic Retrieval Failure**：允许回退到 Structured Direct Read + Lexical Retrieval，并传播 `semantic_retrieval_unavailable`。需要语义召回的 Skill 应输出 Evidence Limitation。
- **Lexical Retrieval Failure**：数字、型号、认证、单位和直接引语不能被声称为已充分验证。
- **Reranker Failure**：使用融合结果继续。Reranker 失败默认不使整个 Skill 失败。
- **Zero Retrieval Result**：返回 `insufficient_information`，不得由模型自行补全。
- **Scope or Permission Failure**：不得通过扩大 Source Scope 进行降级。Current Product 结果为空时，不得自动检索其他商品或所有 Workspace 数据。

---

## Source Processing Failure

每个 Source Version 应具有独立处理状态：`uploaded` / `processing` / `ready` / `partially_ready` / `failed` / `restricted` / `withdrawn` / `superseded`。

- **Optional Source Failure**：若失败 Source 不是当前 Skill 的关键输入，允许使用其他有效 Source，Evidence Package 记录缺失，输出可标记 `valid_with_limitations`。
- **Critical Source Failure**：若用户明确要求分析的关键 Source 处理失败，不得静默忽略，返回等待、暂停或技术失败，提供重新上传或重新处理入口。
- **Partially Ready**：必须记录已成功处理范围 / 失败范围 / Parser Error / 是否允许当前 Skill 使用。部分解析 Source 不得被表示为完整来源。

---

## Tool Failure

每次 Tool Call 概念上记录 `tool_call_id` / `tool_name` / `request_fingerprint` / `attempt_number` / `started_at` / `completed_at` / `status` / `response_reference` / `error_id`。

- **Read-only Tool**（Retrieval / Parsing / Metadata Read / Repository Read）：暂时性错误通常允许有限重试。
- **Side-effect Tool**（未来可能包括发布 / 发消息 / 创建外部对象 / 上传 / 提交平台任务）：必须使用 `idempotency_key`。当第一次调用是否成功不确定时，不得盲目重复执行。MVP 不实现自动发布，但运行时必须保留该边界。

---

## Timeout Hierarchy

必须区分：Call Timeout / Node Timeout / Skill Deadline / Workflow Run Deadline。

- **Call Timeout**：单次 LLM、Retrieval、Tool 或 Repository 调用的限制。
- **Node Timeout**：整个 Node Execution 的最大时间。
- **Skill Deadline**：整个 Skill Run 的最大执行窗口。
- **Workflow Run Deadline**：一次 Workflow Invocation 或 Resume 的整体期限。

下层调用必须继承上层剩余 Deadline。不得在上层 Deadline 即将耗尽时启动超过剩余时间的长调用。

---

## Cancellation

系统支持取消当前 Workflow Run / 当前 Skill Run / 整个 Task。取消采用协作式 Cancellation。收到取消请求后：

```text
1. Record cancellation request
2. Stop scheduling new nodes
3. Propagate cancellation to cancellable calls
4. Finish or rollback current atomic transaction
5. Persist runtime records
6. Mark appropriate layer cancelled
7. Preserve committed historical versions
8. Do not create incomplete Current Truth
```

不得在事务中间强制终止并留下部分业务状态。

---

## Idempotency

以下操作至少需要幂等保护：Workflow Resume；Skill Business Commit；Node Side Effect；Approved Strategy Submission；Marketing Brief Version Commit；Xiaohongshu Execution Brief Commit；Retry 后的数据库写入；外部 Side-effect Tool。

### Input Fingerprint

概念上由以下内容组成：`task_id` / `skill_name` / `input_version_ids` / `source_set_version_id` / `skill_contract_version` / `execution_configuration_version` / `logical_operation`。

相同业务请求因网络重试、客户端重复请求或 Worker 重启再次到达时，应返回原成功结果，不得重复创建业务版本。

---

## Partial Write Prevention

业务写入必须遵循 `Candidate Generation → Deterministic Validation → Atomic Business Commit`。正式事务至少同时处理：Create Domain Version；Create Formal Evidence Links；Update Current Truth Pointer；Update Stage State；Write Audit Record。

任一部分失败：整体回滚；不留下部分 Current Truth；不推进 Workflow；Retry 使用相同幂等身份。本决定不选择具体数据库事务、Outbox 或锁技术。

---

## Checkpoint Recovery

LangGraph Checkpointer 负责：执行状态恢复；Interrupt / Resume；Node 进度；临时运行上下文。Checkpointer 不负责：保存业务 Current Truth；替代业务 Repository；判断业务版本是否有效；覆盖较新的业务状态；创建正式业务对象。

---

## Safe Resume Boundary

只允许从安全边界 Resume，例如：Node 尚未开始；Node 已完整成功；业务事务已经完整提交；Human Review Interrupt；明确失败且可安全重试的 Node。

不得从以下中间状态任意恢复：模型输出只生成了一部分；Evidence Link 只写入了一部分；Current Truth Pointer 已更新但 Stage 未更新；外部 Side Effect 成功状态未知；数据库事务结果不确定。

---

## Checkpoint Reconciliation

Resume 前必须验证 `checkpoint.task_id` / `checkpoint.thread_id` / `checkpoint.input_version_ids` / `current_truth_pointers` / `stage_validity` / `review_package_version`。

如果 Checkpoint 基于旧业务版本：`checkpoint_status = stale`，不得继续执行旧计划。系统应：从当前最早失效阶段重新规划；或创建 Manual Recovery Case；不得自动覆盖新的业务版本。

---

## Human Review Resume

Human Review Resume 必须携带 `review_id` / `review_package_version` / `draft_version` / `approved_strategy_submission_reference`。

Resume 前必须检查：1. Review Package 未被 superseded；2. Facts、Insights 和 Positioning 版本仍有效；3. Review 提交事务已经成功；4. Approved Strategy Current Truth 已存在；5. 当前 Workflow Stage 允许 Resume；6. Resume 尚未被重复处理。

Human Review Resume 必须幂等。旧 Review Package 不得通过 Checkpoint 绕过 DEC-029 的版本校验。

---

## Fallback and Degraded Mode

所有 Fallback 必须显式记录 `original_component` / `fallback_component` / `reason` / `effect_on_evidence` / `effect_on_output` / `user_visible_limitation`。例如：

```text
Semantic Retrieval unavailable
→ Lexical-only fallback
→ Synonym recall may be incomplete
→ Customer Insight output valid_with_limitations
```

不得静默降级。Fallback 的限制必须传递给当前 Skill、Evidence Package、下游业务对象、用户可见状态。

---

## Circuit Breaker Capability

Runtime 需要具备概念上的 Circuit Breaker 能力：`closed` / `open` / `half_open`。目的：防止无意义重复请求；避免故障放大；快速进入明确 Fallback；保护外部依赖；缩短故障期间响应时间。本决定只确认能力需求，不确认阈值、算法或实现库。

---

## Manual Recovery

自动恢复失败后，应创建结构化 `RecoveryCase`：

```text
RecoveryCase
├── recovery_case_id
├── task_id
├── run_id
├── failed_skill_run_id
├── failed_node_execution_id
├── error_ids[]
├── last_safe_checkpoint_id
├── current_business_versions[]
├── failed_input_versions[]
├── recommended_actions[]
├── status
├── assigned_operator
├── resolution
└── audit_history[]
```

允许的恢复动作可以包括：`retry_failed_node` / `restart_skill_from_safe_boundary` / `rerun_invalid_stage` / `rebuild_source` / `refresh_platform_policy` / `discard_stale_checkpoint` / `cancel_task` / `mark_dependency_resolved`。

Manual Recovery 不得：手工伪造 Fact；绕过 Validator；直接修改 Formal Evidence Link；强制将旧 Checkpoint 应用于新业务版本；删除失败历史；直接修改 Current Truth Pointer 而不经过正式事务。

---

## Manual Recovery Queue

无法自动恢复的后台任务可以进入 Manual Recovery Queue。可能进入恢复队列的情况：达到最大 Retry Budget；外部 Side Effect 状态不确定；Data Integrity Error；Checkpoint 与 Current Truth 冲突；重复出现不可解释 Validator Failure；Source Processing 持续失败；关键依赖配置错误。是否采用正式 Dead-letter Queue 技术尚未确认。

---

## Structured Logging

每条结构化日志应包含适用的关联 ID：`task_id` / `thread_id` / `run_id` / `skill_run_id` / `node_execution_id` / `attempt_id` / `trace_id`。相关场景还应包含 `retrieval_run_id` / `evidence_package_id` / `review_id` / `source_version_id` / `model_call_id` / `tool_call_id`。

概念事件包括：`workflow.started` / `workflow.resumed` / `workflow.completed` / `workflow.failed` / `workflow.cancelled` / `skill.started` / `skill.completed` / `skill.failed` / `node.started` / `node.completed` / `node.failed` / `llm.call.started` / `llm.call.completed` / `retrieval.completed` / `retry.scheduled` / `fallback.activated` / `business.waiting_for_input` / `human_review.waiting` / `transaction.committed` / `transaction.rolled_back` / `checkpoint.saved` / `checkpoint.rejected_as_stale` / `recovery_case.created`。

---

## Sensitive Data Boundary

Logs 和 Traces 不得默认保存：API Key；Authorization Header；密码；Secret；数据库连接字符串；完整敏感个人信息；不必要的完整文档；未脱敏用户评论；其他 Workspace 内容；内部敏感 Prompt 内容。

允许记录：内容 Hash；Fragment ID；Source Version ID；Prompt Template Version；Output Schema Version；Token Usage；Latency；Error Category；Component Version。完整输入输出的保存必须受 `environment` / `permission` / `data_sensitivity` / `retention_policy` 控制。

---

## Distributed Tracing

每次 Workflow Run 应产生一个 Root Trace：

```text
Workflow Run Span
├── Skill Run Span
│   ├── Retrieval Span
│   ├── LLM Call Span
│   ├── Validator Span
│   ├── Repository Transaction Span
│   └── Checkpoint Span
└── Human Review Resume Span
```

Trace 必须支持回答：哪一步最慢；哪一步发生重试；哪个模型调用失败；使用了哪个 Evidence Package；哪个 Validator 拒绝输出；Current Truth 是否成功提交；Checkpoint 保存在哪个安全点；Resume 从哪个位置开始；是否启用了 Fallback；业务版本是否重复创建。

---

## Metrics

### Reliability Metrics

`Workflow Success Rate` / `Skill Success Rate` / `Node Failure Rate` / `Retry Success Rate` / `Fallback Rate` / `Timeout Rate` / `Cancellation Rate` / `Resume Success Rate` / `Manual Recovery Rate`。

### Data Integrity Metrics

`Partial Business Write Rate` / `Duplicate Business Version Rate` / `Invalid Current Truth Pointer Rate` / `Stale Checkpoint Resume Success Rate` / `Invalid Evidence Link Commit Rate`。这些高风险指标的目标为 `0%`。

### LLM Runtime Metrics

Structured Output Failure Rate；Repair Success Rate；Candidate Regeneration Rate；Schema Validation Failure Rate；Evidence Validator Failure Rate；Model Latency；Token Usage。

### Retrieval Runtime Metrics

继承 DEC-032，并增加 Retrieval Failure Rate；Retrieval Fallback Rate；Evidence Package Build Failure Rate；Index Unavailable Rate。

### Human Review Metrics

Review Resume Success Rate；Duplicate Resume Prevention Rate；Stale Review Rejection Rate；Review Waiting Duration；Withdrawal Recovery Success Rate。

### Runtime Performance Metrics

Workflow Duration；Skill Duration；Node Duration；External Call Latency；Commit Latency；Checkpoint Latency；Queue Waiting Time。

---

## Alerting Boundary

必须区分 `User-facing Notification` 与 `Operator Alert`。

### User-facing Notification

适用于：等待补充资料；Review Package 已过期；临时服务不可用；已使用降级方案；任务已取消；需要人工恢复。用户提示必须说明：发生了什么；当前数据是否安全；系统是否已重试；是否启用了 Fallback；用户需要执行什么动作；当前流程能否继续。

### Operator Alert

适用于：Data Integrity Error；Cross-task 或 Scope Leakage Risk；Current Truth Pointer 异常；Duplicate Business Version；持续 Provider 故障；大量任务卡在同一 Node；Checkpoint 与业务状态不一致；Manual Recovery Queue 堆积。本决定不确认告警阈值、渠道或值班系统。

---

## User-visible Error Experience

用户不应只看到 `Something went wrong`。推荐错误信息结构：`What happened` / `Whether current data is safe` / `Whether automatic retry occurred` / `Whether fallback was used` / `What the user needs to do` / `Whether the workflow can continue`。不得直接向用户暴露内部异常堆栈、连接信息或敏感 Provider 请求。

---

## Failure Handling Matrix

概念矩阵：

| Scenario | Automatic Retry | Fallback | Final Disposition |
| --- | ---: | ---: | --- |
| LLM request timeout | Bounded | Optional backup channel not yet decided | Fail or recovery |
| Invalid LLM JSON | Bounded repair | Never commit free text | Skill failure |
| Rate limit | Bounded backoff | Depends on deadline | Fail or wait |
| Semantic retrieval unavailable | Bounded | Direct + lexical | Limited output |
| Reranker unavailable | Optional | Use fused results | Continue |
| Temporary DB connection failure | Bounded | None | Fail after budget |
| Business validation failure | Not infrastructure retry | Candidate regeneration | Skill failure |
| Permission revoked | No | No | Pause |
| Review Package stale | No | No | Create new package |
| User cancellation | No | No | Cancelled |
| Checkpoint stale | No | Replan from valid state | Recovery |
| Source partially parsed | Conditional | Use valid range | Limited or wait |
| Zero evidence | No | No | Insufficient information |

具体次数和 Deadline 尚未确认。

---

## Required Technical Spike Scenarios

在实现正式业务 Workflow Graph 前，Technical Spike 必须验证以下场景。

1. **Transient Node Failure** — 模拟首次失败、第二次成功。验证 Attempt Record；Retry；Trace 连续；不产生重复业务版本。
2. **Structured Output Failure** — 模拟非法 JSON / 缺少字段 / 无效 ID。验证 Schema Repair；有界重试；最终失败不写入 Current Truth。
3. **Transaction Commit Failure** — 在事务过程中模拟失败。验证完整回滚；Current Truth Pointer 不变化；Retry 不产生重复版本。
4. **Human Review Interrupt and Resume** — 验证 Checkpoint 保存；Review Package Version；用户提交；新 Workflow Run Resume；重复 Resume 幂等。
5. **Stale Review** — 审核过程中修改上游业务版本。验证旧 Review 被拒绝；旧 Checkpoint 不恢复；创建新 Review Package。
6. **Retrieval Degraded Mode** — 模拟 Semantic Retrieval 不可用。验证 Fallback；Evidence Limitation；Retrieval Log；Skill 可继续或明确受限。
7. **Cancellation** — 运行期间取消。验证不再调度新 Node；当前事务完成或回滚；不产生部分业务写入。
8. **Stale Checkpoint** — Checkpoint 基于旧 Facts Version。验证 Resume 被拒绝；从最早失效 Stage 重规划；不覆盖 Current Truth。
9. **Duplicate Request** — 重复发送相同幂等请求。验证返回相同成功结果；不创建重复业务版本。
10. **Manual Recovery** — 模拟达到最大 Retry Budget。验证创建 Recovery Case；保留失败上下文；能从安全边界恢复；恢复过程不绕过 Validator。

---

## Hard Reliability Targets

MVP 目标：

```text
Partial Business Write Rate = 0%
Duplicate Business Version Rate = 0%
Stale Review Submission Success Rate = 0%
Stale Checkpoint Resume Success Rate = 0%
Invalid Evidence Link Commit Rate = 0%
Cross-task Recovery Leakage Rate = 0%
```

Observability 记录完整率目标：

```text
Runs with Trace ID = 100%
Skill Runs with Input Version References = 100%
Node Executions with Attempt Records = 100%
Errors with Structured Category = 100%
Business Commits with Audit Record = 100%
Fallbacks with User-visible Limitation = 100%
```

---

## Contract Summary

```text
Component:
Workflow Runtime Failure Recovery, Retry and Observability
Runtime Levels:
- Task
- Workflow Run
- Skill Run
- Node Execution
- Attempt
Core Capabilities:
- Error Classification
- Bounded Retry
- Explicit Fallback
- Safe Checkpoint Resume
- Transactional Commit
- Idempotency
- Cancellation
- Manual Recovery
- Structured Logging
- Distributed Tracing
- Metrics
- Alerting
Hard Rules:
- Business waiting is not technical failure
- Retry is not Rerun
- No infinite retry
- No partial business write
- No stale checkpoint resume
- No duplicate business version
- No Validator bypass during recovery
```

---

## Reason

该系统依赖 LLM、Retrieval、Source Processing、LangGraph Checkpoint、Human Review、数据库事务、外部工具、平台规则和外部服务。这些组件均可能发生暂时故障、结构输出错误、版本过期、并发重复或不可恢复异常。如果没有统一运行时契约，将产生：业务等待被误判为系统失败；技术 Retry 创建重复业务版本；Checkpoint 覆盖新的 Current Truth；事务失败留下部分写入；Review Resume 绕过版本校验；Fallback 静默降低证据质量；无法知道错误发生在哪个 Node；无法重现模型、检索和 Validator 的执行过程；恢复过程绕过 Evidence 和 Strategy 规则。

因此 Runtime 必须采用：

```text
Layered Execution Identity
+
Bounded Technical Recovery
+
Business-state-aware Resume
+
Atomic Business Commit
+
End-to-end Runtime Observability
```

---

## Impact

该决定将影响：LangGraph Runtime；Checkpointer；Workflow Run Repository；Skill Run Repository；Node Execution Records；Retry Middleware；LLM Wrapper；Retrieval Runtime；Tool Runtime；Repository Transactions；Human Review Resume；Cancellation；Manual Recovery；Logging；Tracing；Metrics；Alerting；Technical Spike；后续生产部署架构。

---

## Decision Boundary

本决定已经确认：

Task、Workflow Run、Skill Run、Node Execution、Attempt 分层；新增运行标识符；Retry 与 Rerun 分离；Business Wait、Pause 与 Technical Failure 分离；Error Taxonomy；Severity；Retryability；Failure Disposition；Runtime Error Record；有界 Retry；Retry Budget；Structured Output Recovery；Evidence Validator Failure 处理；Retrieval Failure 处理；Source Processing Failure；Tool Side Effect 幂等；Timeout 层级；Cooperative Cancellation；Input Fingerprint；Idempotent Commit；Partial Write Prevention；Checkpoint 职责边界；Safe Resume Boundary；Checkpoint Reconciliation；Human Review Resume；Explicit Fallback；Circuit Breaker 能力需求；Recovery Case；Manual Recovery Queue；Structured Logging；Sensitive Data Boundary；Distributed Tracing；Runtime Metrics；Alerting Boundary；User-visible Error Experience；Failure Handling Matrix；Technical Spike 必测场景；Hard Reliability Targets；Observability Completeness Targets。

本决定尚未确认：

Retry 次数；Timeout 秒数；Backoff 参数；Circuit Breaker 阈值；Queue System；Worker Framework；Dead-letter Queue 技术；Logging Provider；Tracing Provider；Metrics Provider；Alerting Provider；数据保留周期；日志采样率；PII 脱敏实现；是否采用 OpenTelemetry；LangGraph Checkpointer 实现；数据库；Outbox；分布式锁；API；并发模型；最终 SLO；最终字段名称；最终错误代码。

---

## Related Decisions

- [DEC-007 — Mandatory Human Review](dec-007-single-review-node-and-exception-pauses.md)
- [DEC-009 — Stage Invalidation](dec-009-stage-level-invalidation-and-partial-rerun.md)
- [DEC-011 — Deterministic Workflow Control](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)
- [DEC-012 — Structured Workflow State](dec-012-stage-state-and-structured-business-items.md)
- [DEC-013 — Task-level Persistence](dec-013-task-level-persistent-state-and-cross-session-resume.md)
- [DEC-023 — LangGraph StateGraph](dec-023-select-langgraph-stategraph-for-mvp-workflow.md)
- [DEC-024 — Versioned Domain State](dec-024-versioned-domain-state-and-compact-langgraph-state.md)
- [DEC-025 — Source and Evidence Architecture](dec-025-versioned-sources-fragments-and-evidence-links.md)
- [DEC-029 — Human Review and Approved Strategy](dec-029-human-review-and-approved-strategy-contract.md)
- [DEC-032 — Hybrid Retrieval and Evidence Runtime](dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)

---

## Related RFC

None

---

## Supersedes

None

---

## Amends

**Amends DEC-023、DEC-024、DEC-029。**

- **DEC-023**（LangGraph + StateGraph / Graph API 选型）确认框架须为有状态 / 确定性 / 可持久化的业务工作流运行时，但未定义运行时失败恢复、重试与可观测性契约。DEC-033 在此基础上正式定义 LangGraph 运行时的分层执行身份、有界技术恢复、Safe Checkpoint Resume、Checkpointer 职责边界与端到端可观测性。
- **DEC-024**（版本化 Domain Objects + Current Truth Version Pointers；task_id / thread_id / run_id / checkpoint_id 四标识符边界；Checkpointer 与业务数据库分离）确认了执行标识符与 Checkpointer 分离原则。DEC-033 在此基础上**扩展**运行身份（新增 skill_run_id / node_execution_id / attempt_id / error_id / trace_id / recovery_case_id），定义 Checkpoint Reconciliation 与 Safe Resume Boundary，并明确 Checkpoint 不等于业务 Current Truth。
- **DEC-029**（Human Review and Approved Strategy Contract；版本化 Review Package；Review Package 提交事务）确认 Human Review 须强制人工审核与版本化。DEC-033 在此基础上正式定义可靠的 Human Review Resume 行为（携带 review_id / review_package_version / draft_version；幂等；旧 Review Package 不得通过 Checkpoint 绕过 DEC-029 版本校验）。
- **不推翻** DEC-023 / DEC-024 / DEC-029 既有结论；DEC-023 / DEC-024 / DEC-029 行作为历史记录不修改，本 Amends 关系仅在此处记录。

---

## Notes

- 本决定保持 **Development Status: NOT READY**。
- 当前**不**创建正式 Retry Middleware 代码 / LangGraph Recovery 代码 / Checkpointer 实现 / Worker / Queue / Dead-letter Queue / Recovery Worker / Logging Pipeline / Tracing Pipeline / Metrics Dashboard / Alerting Rules / 数据库表 / Outbox / 分布式锁 / API / 任何业务实现代码。
- 当前**不**选择 Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue Provider / Worker Framework / Logging Provider / Tracing Provider / Metrics Provider / Alerting Provider / OpenTelemetry / Checkpointer Backend / Database / Outbox Technology / Distributed Lock / Data Retention Period / Log Sampling Rate / PII 脱敏实现 / 并发模型 / 最终 SLO / 最终字段名称 / 最终错误代码。
- 当前**不**创建 RFC。
- Workflow Runtime 的失败恢复、重试与可观测性是跨 Skill 的共享运行架构层（非 Core Skill Contract、非 Platform Adapter Contract、非 Retrieval Runtime）。若运行时把业务等待误判为系统失败、用技术 Retry 创建重复业务版本、用 Checkpoint 覆盖新的 Current Truth、在事务失败时留下部分写入、让 Review Resume 绕过版本校验、让 Fallback 静默降低证据质量，或在恢复中绕过 Evidence Validator / Strategy 规则，将直接破坏 DEC-008~DEC-032 建立的可追溯证据链、版本化领域状态与人工审核契约。
- 概念 Runtime Spec 见 [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)（仅概念，非最终实现）。
- 在 **Technical Spike Plan and Architecture Readiness Gate** 议题确认前：**不**实现正式业务 Graph；**不**编写四个核心 Skill 的生产 Prompt；**不**建立正式数据库 Schema；**不**选择生产级基础设施；Development Status 保持 `NOT READY`。
