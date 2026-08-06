# Workflow Runtime Failure Recovery, Retry and Observability — 概念 Specification

> **Status: CONCEPTUAL（概念）**
> 来源决定：[DEC-033 — Workflow Runtime 采用分层运行记录、分类故障处置、有界重试、安全恢复、事务幂等与端到端可观测性契约](../../decisions/dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)（Accepted，Runtime Architecture / Reliability Architecture / Observability Architecture，2026-07-29）。Amends DEC-023 / DEC-024 / DEC-029。
> 本文件是 DEC-033 的**概念结构化记录**，**不是最终实现契约**。所有字段名、枚举、Schema、阈值、算法、Provider、技术选型均未确认。
> Development Status: **NOT READY**。

---

## §0 来源与范围

本 Specification 把 DEC-033 已确认的 Workflow Runtime Failure Recovery, Retry and Observability Contract 整理为结构化概念规格。它是**跨 Skill 的共享运行架构层**（非 Core Skill Contract、非 Platform Adapter Contract、非 Retrieval Runtime），服务于所有 Skill、Evidence Validator、Human Review、Tool 调用与业务事务。承接 DEC-023（LangGraph 选型）/ DEC-024（版本化 Domain State + 四标识符）/ DEC-029（Human Review 事务），并在 DEC-032（检索与证据装配运行时）之后，统一形式化失败恢复、重试与可观测性契约。

核心原则：**业务等待不等于技术失败；技术 Retry 不等于业务 Rerun；Checkpoint 不等于业务 Current Truth；任何失败恢复都不能绕过业务版本、Evidence Validator、Review Package 或 Current Truth 规则。**

---

## §1 Purpose

在严格限定业务版本、Evidence Validator、Review Package 与 Current Truth 规则的前提下，为 Workflow Runtime 提供统一的：

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

防止业务等待被误判为系统失败、技术 Retry 创建重复业务版本、Checkpoint 覆盖新的 Current Truth、事务失败留下部分写入、Review Resume 绕过版本校验、Fallback 静默降低证据质量、以及恢复过程绕过 Evidence 与 Strategy 规则。

---

## §2 Responsibilities

- 维护 Task / Workflow Run / Skill Run / Node Execution / Execution Attempt 五层执行身份与关联链。
- 区分 Retry（技术恢复）与 Rerun（新业务计算）。
- 对错误统一分类（Error Taxonomy）并给出 Severity / Retryability / Failure Disposition。
- 对明确可重试错误执行有界 Retry 与统一 Retry Budget。
- 提供显式 Fallback 并传播 Evidence Limitation。
- 从安全边界 Resume，对 Checkpoint 与业务版本做 Reconciliation。
- 保证 Skill Business Commit、Side-effect Tool、Review Resume 等操作的幂等性。
- 防止部分业务写入；事务化提交或整体回滚。
- 提供结构化日志、分布式 Tracing、Metrics 与区分用户 / 运维的 Alerting。
- 在自动恢复失败后创建结构化 RecoveryCase 与 Manual Recovery Queue。

---

## §3 Non-responsibilities

- **不**保存业务 Current Truth（由业务 Repository 负责）。
- **不**替代业务 Repository / Validator / 版本规则。
- **不**判断业务候选是否有效（由确定性 Validator 决定）。
- **不**绕过 DEC-029 Review Package 版本校验。
- **不**实现业务 Skill 的内部逻辑。
- **不**承担 DEC-032 检索与证据装配的职责。
- 本文件**不**定义最终数据库 Schema、Provider、阈值或算法。

---

## §4 Runtime Hierarchy

```text
Task
Workflow Run
Skill Run
Node Execution
Execution Attempt
```

### Task

`task_id` 表示长期存在的业务任务，可跨越多次 Workflow Run、多次暂停与恢复、多次人工审核、多次阶段 Rerun、多个业务版本、多次失败恢复。Task 不等于一次程序执行。

### Workflow Run

继续使用 DEC-024 的 `run_id`，表示一次工作流调用、恢复或明确重跑。同一 Task 可有多个 Run。`thread_id` 关联同一 LangGraph 执行线程。

### Skill Run

每次核心业务 Skill 执行创建 `skill_run_id`，至少关联 `task_id` / `run_id` / `skill_name` / `input_version_ids` / `source_set_version_id` / `skill_contract_version` / `execution_configuration_version`。

### Node Execution

每个可恢复、可观测的执行节点创建 `node_execution_id`（例如 `build_evidence_package` / `generate_fact_candidates` / `validate_fact_candidates` / `commit_fact_version`）。

### Execution Attempt

同一 Node 因技术故障重试时，为每次尝试创建 `attempt_id` / `attempt_number`。重试不创建新的 Skill Run 或业务版本。

---

## §5 Identifier Model

沿用 DEC-024：`task_id` / `thread_id` / `run_id` / `checkpoint_id`。DEC-033 新增：`skill_run_id` / `node_execution_id` / `attempt_id` / `error_id` / `trace_id` / `recovery_case_id`。相关能力还可能关联 `retrieval_run_id` / `evidence_package_id` / `review_id` / `tool_call_id` / `model_call_id` / `source_version_id`。这些 ID 必须形成完整的执行关联链。

---

## §6 Retry and Rerun Boundary

`Retry ≠ Rerun`。

### Retry

同一逻辑操作、同一输入、同一幂等身份，因暂时性技术故障再次尝试。特征：Same Skill Run / Same Node Execution / Different Attempt / Same Logical Input / Same Idempotency Identity。Retry 不得创建新的业务版本。示例：网络中断、LLM 超时、429 限流、DB 连接失败、Retrieval 暂时不可用。

### Rerun

因用户明确要求、上游版本变化、业务输出失效或执行配置变化，启动新的业务计算。应创建新的 `run_id` / `skill_run_id`，并可能创建新的业务候选版本。示例：用户补充资料、Facts Version 变化、Approved Strategy 被撤回、执行配置升级。

正式边界：`Retry = Technical Recovery`；`Rerun = New Business Computation`。

---

## §7 Workflow Run Record

```text
WorkflowRun
├── run_id
├── task_id
├── thread_id
├── trigger_type          // initial_start / user_resume / human_review_resume / automatic_retry / explicit_rerun / recovery_resume
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

---

## §8 Skill Run Record

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

---

## §9 Node Execution Record

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

---

## §10 Execution Attempt Record

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

以上为概念结构，非最终数据库 Schema。

---

## §11 Runtime Status Boundary

Workflow Run / Skill Run / Node Execution 不共用完全相同的状态语义。

- **Workflow Run Status**：`queued` / `running` / `waiting_for_input` / `waiting_for_review` / `paused` / `completed` / `failed` / `cancelled`。
- **Skill Run Status**：`queued` / `running` / `validating` / `committing` / `succeeded` / `succeeded_with_limitations` / `failed` / `cancelled` / `superseded`。
- **Node Execution Status**：`queued` / `running` / `retry_scheduled` / `succeeded` / `failed` / `timed_out` / `cancelled` / `skipped`。

最终状态名称尚未确认，但各层语义必须明确分离。

---

## §12 Business Control State

`waiting_for_input` / `waiting_for_review` / `paused` 属于**业务控制状态**，不是技术失败。

- `waiting_for_input`：缺商品资料 / 未提供评论 / 关键 Source 未上传 / 用户拒绝降级 / 缺账号品牌上下文。
- `waiting_for_review`：Candidates 已生成 / Review Package 已创建 / 用户未提交 / 只保存 Draft。
- `paused`：商品身份冲突 / Current Product 与 Competitor 混淆 / Source 权限撤回 / 高风险声明需人工 / Approved Strategy 撤回 / 数据污染。

业务等待和暂停不得：自动按技术错误反复重试；记录为 Provider Failure；触发基础设施故障告警；被描述为系统崩溃。

---

## §13 Error Taxonomy

- **Transient Infrastructure Error**（网络 / DNS / 服务短暂不可用 / DB 连接 / 临时锁）— 通常可重试。
- **Rate Limit Error**（LLM 429 / Retrieval 限流 / 外部配额）— 有限重试，尊重 `Retry-After` 与 Deadline。
- **Timeout Error**（Model / Retrieval / Tool / Node / Skill Deadline）— 是否重试取决于幂等性 / 剩余 Deadline / Attempt 数 / Side Effect。
- **Structured Output Error**（非法 JSON / 缺字段 / 非法 Enum / ID 格式 / 不符合 Skill Schema）— 有限修复或重新生成；无效自由文本不得写入 Current Truth。
- **Validation Error**（Fact ID 无效 / Proof Point 无证据 / Competitor Capability Leakage / Hypothesis 写成 Fact / Evidence Limitation 丢失 / Strategy Drift / Fabricated Quote）— 不可被基础设施 Retry 掩盖；有限候选修正或重生成。
- **Permission or Authentication Error**（Source 权限失效 / Workspace 撤回 / Credential 无效）— 默认不可自动重试，进入暂停或人工处理。
- **Data Integrity Error**（Pointer 指向不存在版本 / Evidence Link 引用不存在 Fragment / Task 与 Source Task 不一致 / Checkpoint 与版本不一致 / 事务状态不完整）— 高严重性，不得由 LLM 自行修复。
- **Dependency Configuration Error**（模型配置缺失 / Retrieval 组件未配置 / Schema Version 不支持 / Repository 未连接 / Index 不兼容）— 通常不可自动重试。
- **Provider Content Rejection**（内容规则拒绝）— 不得伪装为网络错误，不得无限重试，记录拒绝类别，按业务范围降级 / 暂停 / 失败。
- **Cancellation**（用户或系统取消）— 不属于 Failure。

---

## §14 Runtime Error Record

```text
RuntimeErrorRecord
├── error_id
├── task_id
├── run_id
├── skill_run_id
├── node_execution_id
├── attempt_id
├── error_code            // 最终代码未确认
├── error_category        // 见 §13
├── severity              // info / warning / error / critical
├── retryability          // retryable / conditionally_retryable / non_retryable / unknown
├── failure_disposition   // retry / fallback / wait / pause / fail / cancel / manual_recovery
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

用户只看到安全、可操作的 `user_safe_message`；敏感信息、Prompt、Secret、未脱敏堆栈不展示给用户。

---

## §15 Retry Policy

自动 Retry 须满足：仅适用于明确可重试错误；有最大 Attempt 数；有时间上限；有总体 Deadline；有结构化日志；支持取消；保持幂等；不产生重复业务版本。默认策略：`Bounded Retry + Exponential Backoff + Jitter + Respect Retry-After + Overall Deadline`。具体次数、间隔、秒数**未确认**。

---

## §16 Retry Budget

统一协调 `per_attempt_timeout` / `per_node_retry_limit` / `per_skill_retry_budget` / `per_workflow_run_deadline`。避免嵌套重试放大（`Workflow Retry × Skill Retry × Tool Internal Retry`）。各层组件不得独立无限重试。Runtime 控制总体 Retry Budget。

---

## §17 Structured Output Recovery

```text
1. Receive model output
2. Parse output
3. Validate schema
4. Apply deterministic normalization
5. Perform constrained repair
6. Regenerate current node if permitted
7. Fail after bounded attempts
```

- **Deterministic Normalization**：仅允许语义不变修复（去 JSON Fence / 修尾随逗号 / 标准化 Enum 大小写 / 补容器结构）。不得猜测业务事实 / 创造 Fragment ID / 自动补 Proof Point / 把自由文本推断为业务字段。
- **Constrained Repair**：可向模型返回 Schema 错误 / 缺失字段 / 非法 Enum / 无效引用 / Validator 拒绝原因。只能修正当前候选，不得扩大 Source Scope / 改输入版本 / 绕权限。达上限后 `error_category = structured_output_error`、`failure_disposition = fail`。无效输出不得写入 Current Truth。

---

## §18 Evidence Validator Failure

Schema 合法但业务候选违反硬证据规则时，可有限 `candidate_regeneration`。Validator 错误作为结构化反馈返回。若模型重复违反相同硬规则：停止自动修复；Skill Run 标记失败；保留失败候选供调试评估；不创建业务版本；不创建 Formal Evidence Link；不更新 Current Truth。

---

## §19 Retrieval Failure

遵循 DEC-032。

- **Semantic Retrieval Failure**：回退 Structured Direct Read + Lexical，传播 `semantic_retrieval_unavailable`；需语义召回的 Skill 输出 Evidence Limitation。
- **Lexical Retrieval Failure**：数字 / 型号 / 认证 / 单位 / 直接引语不能被声称为已充分验证。
- **Reranker Failure**：用融合结果继续，默认不使整个 Skill 失败。
- **Zero Retrieval Result**：返回 `insufficient_information`，模型不得自行补全。
- **Scope or Permission Failure**：不得扩大 Source Scope 降级；Current Product 结果为空不得自动检索其他商品或所有 Workspace 数据。

---

## §20 Source Processing Failure

每个 Source Version 独立处理状态：`uploaded` / `processing` / `ready` / `partially_ready` / `failed` / `restricted` / `withdrawn` / `superseded`。

- **Optional Source Failure**：失败 Source 非关键输入 → 用其他有效 Source；Evidence Package 记录缺失；可标记 `valid_with_limitations`。
- **Critical Source Failure**：用户明确要求分析的关键 Source 失败 → 不得静默忽略；返回等待 / 暂停 / 技术失败；提供重新上传或重新处理入口。
- **Partially Ready**：记录已处理范围 / 失败范围 / Parser Error / 是否允许 Skill 使用。部分解析 Source 不得表示为完整来源。

---

## §21 Tool Failure

每次 Tool Call 概念记录 `tool_call_id` / `tool_name` / `request_fingerprint` / `attempt_number` / `started_at` / `completed_at` / `status` / `response_reference` / `error_id`。

- **Read-only Tool**（Retrieval / Parsing / Metadata Read / Repository Read）：暂时性错误通常允许有限重试。
- **Side-effect Tool**（发布 / 发消息 / 创建外部对象 / 上传 / 提交平台任务）：必须用 `idempotency_key`；首次调用成功与否不确定时不得盲目重试。MVP 不实现自动发布，但运行时须保留该边界。

---

## §22 Timeout Hierarchy

区分 Call Timeout / Node Timeout / Skill Deadline / Workflow Run Deadline。下层调用继承上层剩余 Deadline；不得在上层 Deadline 即将耗尽时启动超过剩余时间的长调用。

---

## §23 Cancellation

支持取消当前 Workflow Run / Skill Run / 整个 Task，采用协作式 Cancellation。收到取消请求后：记录请求 → 停止调度新 Node → 传播到可取消调用 → 完成或回滚当前原子事务 → 持久化运行记录 → 标记对应层 cancelled → 保留已提交历史版本 → 不创建不完整 Current Truth。不得在事务中间强制终止并留下部分业务状态。

---

## §24 Idempotency

需要幂等保护的操作：Workflow Resume；Skill Business Commit；Node Side Effect；Approved Strategy Submission；Marketing Brief Version Commit；Xiaohongshu Execution Brief Commit；Retry 后数据库写入；外部 Side-effect Tool。

### Input Fingerprint

由 `task_id` / `skill_name` / `input_version_ids` / `source_set_version_id` / `skill_contract_version` / `execution_configuration_version` / `logical_operation` 组成。相同业务请求因网络重试、客户端重复请求或 Worker 重启再次到达时，返回原成功结果，不得重复创建业务版本。

---

## §25 Partial Write Prevention

业务写入遵循 `Candidate Generation → Deterministic Validation → Atomic Business Commit`。正式事务至少同时处理 Create Domain Version / Create Formal Evidence Links / Update Current Truth Pointer / Update Stage State / Write Audit Record。任一部分失败：整体回滚；不留下部分 Current Truth；不推进 Workflow；Retry 用相同幂等身份。本决定不选具体数据库事务、Outbox 或锁技术。

---

## §26 Checkpoint Recovery

LangGraph Checkpointer 负责：执行状态恢复；Interrupt / Resume；Node 进度；临时运行上下文。**不负责**：保存业务 Current Truth；替代业务 Repository；判断业务版本是否有效；覆盖较新的业务状态；创建正式业务对象。

---

## §27 Safe Resume Boundary

只允许从安全边界 Resume：Node 尚未开始 / Node 已完整成功 / 业务事务已完整提交 / Human Review Interrupt / 明确失败且可安全重试的 Node。不得从中间状态任意恢复：模型输出只生成一部分 / Evidence Link 只写入一部分 / Pointer 已更新但 Stage 未更新 / 外部 Side Effect 成功状态未知 / DB 事务结果不确定。

---

## §28 Checkpoint Reconciliation

Resume 前验证 `checkpoint.task_id` / `checkpoint.thread_id` / `checkpoint.input_version_ids` / `current_truth_pointers` / `stage_validity` / `review_package_version`。若 Checkpoint 基于旧业务版本：`checkpoint_status = stale`，不得继续旧计划；从当前最早失效阶段重新规划，或创建 Manual Recovery Case；不得自动覆盖新业务版本。

---

## §29 Human Review Resume

Resume 必须表达 `review_id` / `review_package_version` / Review Draft `revision` / `approved_strategy_submission_reference` 的语义。Resume 前检查：1. Review Package 未被 superseded；2. Draft revision 未过期；3. Facts / Insights / Positioning 版本仍有效；4. Review 提交事务已成功；5. Approved Strategy Current Truth 已存在；6. 当前 Stage 允许 Resume；7. Resume 未被重复处理。必须幂等。旧 Package 或 revision 不得通过 Checkpoint 绕过 DEC-029 / DEC-046 版本校验；最终传输字段名由 RFC-004 冻结。

---

## §30 Fallback and Degraded Mode

所有 Fallback 显式记录 `original_component` / `fallback_component` / `reason` / `effect_on_evidence` / `effect_on_output` / `user_visible_limitation`。不得静默降级。限制必须传递给当前 Skill / Evidence Package / 下游业务对象 / 用户可见状态。

示例：`Semantic Retrieval unavailable → Lexical-only fallback → Synonym recall may be incomplete → Customer Insight output valid_with_limitations`。

---

## §31 Circuit Breaker Capability

概念状态 `closed` / `open` / `half_open`。目的：防止无意义重复请求；避免故障放大；快速进入明确 Fallback；保护外部依赖；缩短故障期响应时间。本决定只确认能力需求，不确认阈值、算法或实现库。

---

## §32 Manual Recovery

自动恢复失败后创建结构化 `RecoveryCase`：

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

允许的恢复动作：`retry_failed_node` / `restart_skill_from_safe_boundary` / `rerun_invalid_stage` / `rebuild_source` / `refresh_platform_policy` / `discard_stale_checkpoint` / `cancel_task` / `mark_dependency_resolved`。

Manual Recovery 不得：手工伪造 Fact；绕过 Validator；直接修改 Formal Evidence Link；强制将旧 Checkpoint 应用于新业务版本；删除失败历史；直接修改 Current Truth Pointer 而不经正式事务。

---

## §33 Recovery Queue

无法自动恢复的后台任务可进入 Manual Recovery Queue。进入条件：达到最大 Retry Budget；外部 Side Effect 状态不确定；Data Integrity Error；Checkpoint 与 Current Truth 冲突；重复出现不可解释 Validator Failure；Source Processing 持续失败；关键依赖配置错误。是否采用正式 Dead-letter Queue 技术**尚未确认**。

---

## §34 Structured Logging

每条日志含适用关联 ID：`task_id` / `thread_id` / `run_id` / `skill_run_id` / `node_execution_id` / `attempt_id` / `trace_id`。相关场景还含 `retrieval_run_id` / `evidence_package_id` / `review_id` / `source_version_id` / `model_call_id` / `tool_call_id`。

概念事件：`workflow.started` / `workflow.resumed` / `workflow.completed` / `workflow.failed` / `workflow.cancelled` / `skill.started` / `skill.completed` / `skill.failed` / `node.started` / `node.completed` / `node.failed` / `llm.call.started` / `llm.call.completed` / `retrieval.completed` / `retry.scheduled` / `fallback.activated` / `business.waiting_for_input` / `human_review.waiting` / `transaction.committed` / `transaction.rolled_back` / `checkpoint.saved` / `checkpoint.rejected_as_stale` / `recovery_case.created`。

---

## §35 Sensitive Data Boundary

Logs / Traces 不得默认保存：API Key / Authorization Header / 密码 / Secret / DB 连接串 / 完整敏感个人信息 / 不必要完整文档 / 未脱敏评论 / 其他 Workspace 内容 / 内部敏感 Prompt。

允许记录：内容 Hash / Fragment ID / Source Version ID / Prompt Template Version / Output Schema Version / Token Usage / Latency / Error Category / Component Version。完整输入输出的保存受 `environment` / `permission` / `data_sensitivity` / `retention_policy` 控制。

---

## §36 Tracing

每次 Workflow Run 产生一个 Root Trace：

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

Trace 须能回答：哪步最慢 / 哪步重试 / 哪个模型调用失败 / 用了哪个 Evidence Package / 哪个 Validator 拒绝 / Current Truth 是否提交 / Checkpoint 在哪个安全点 / Resume 从哪开始 / 是否启用 Fallback / 业务版本是否重复创建。

---

## §37 Metrics

- **Reliability Metrics**：Workflow Success Rate / Skill Success Rate / Node Failure Rate / Retry Success Rate / Fallback Rate / Timeout Rate / Cancellation Rate / Resume Success Rate / Manual Recovery Rate。
- **Data Integrity Metrics**（目标 `0%`）：Partial Business Write Rate / Duplicate Business Version Rate / Invalid Current Truth Pointer Rate / Stale Checkpoint Resume Success Rate / Invalid Evidence Link Commit Rate。
- **LLM Runtime Metrics**：Structured Output Failure Rate / Repair Success Rate / Candidate Regeneration Rate / Schema Validation Failure Rate / Evidence Validator Failure Rate / Model Latency / Token Usage。
- **Retrieval Runtime Metrics**：继承 DEC-032，增加 Retrieval Failure Rate / Retrieval Fallback Rate / Evidence Package Build Failure Rate / Index Unavailable Rate。
- **Human Review Metrics**：Review Resume Success Rate / Duplicate Resume Prevention Rate / Stale Review Rejection Rate / Review Waiting Duration / Withdrawal Recovery Success Rate。
- **Runtime Performance Metrics**：Workflow Duration / Skill Duration / Node Duration / External Call Latency / Commit Latency / Checkpoint Latency / Queue Waiting Time。

最终 SLO 未确认。

---

## §38 Alerting Boundary

区分 `User-facing Notification` 与 `Operator Alert`。

- **User-facing Notification**：等待补充资料 / Review Package 过期 / 临时不可用 / 已用降级方案 / 任务取消 / 需人工恢复。须说明发生了什么 / 数据是否安全 / 是否已重试 / 是否启用 Fallback / 用户需做什么 / 流程能否继续。
- **Operator Alert**：Data Integrity Error / Cross-task 或 Scope Leakage Risk / Pointer 异常 / Duplicate Business Version / 持续 Provider 故障 / 大量任务卡同一 Node / Checkpoint 与业务状态不一致 / Recovery Queue 堆积。

告警阈值、渠道、值班系统**未确认**。

---

## §39 User-visible Error Experience

用户不应只看到 `Something went wrong`。推荐结构：`What happened` / `Whether current data is safe` / `Whether automatic retry occurred` / `Whether fallback was used` / `What the user needs to do` / `Whether the workflow can continue`。不得暴露内部异常堆栈、连接信息或敏感 Provider 请求。

---

## §40 Failure Matrix

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

具体次数与 Deadline 未确认。

---

## §41 Technical Spike Scenarios

实现正式业务 Workflow Graph 前，Technical Spike 须验证：1. Transient Node Failure；2. Structured Output Failure；3. Transaction Commit Failure；4. Human Review Interrupt and Resume；5. Stale Review；6. Retrieval Degraded Mode；7. Cancellation；8. Stale Checkpoint；9. Duplicate Request；10. Manual Recovery。各场景验证项见 DEC-033「Required Technical Spike Scenarios」。

---

## §42 Reliability Targets

MVP 目标（`= 0%`）：Partial Business Write Rate / Duplicate Business Version Rate / Stale Review Submission Success Rate / Stale Checkpoint Resume Success Rate / Invalid Evidence Link Commit Rate / Cross-task Recovery Leakage Rate。

Observability 完整率目标（`= 100%`）：Runs with Trace ID / Skill Runs with Input Version References / Node Executions with Attempt Records / Errors with Structured Category / Business Commits with Audit Record / Fallbacks with User-visible Limitation。

---

## Open Questions

以下均**未虚构**，仅记录为待确认（受 Technical Spike Plan and Architecture Readiness Gate 议题约束）：

- Retry 次数、Timeout 秒数、Backoff 参数、Jitter 策略。
- Circuit Breaker 阈值、算法、实现库。
- Queue System / Worker Framework / Dead-letter Queue 技术是否采用。
- Logging / Tracing / Metrics / Alerting Provider；是否采用 OpenTelemetry。
- LangGraph Checkpointer 实现 / Backend。
- 数据库 / Outbox 技术 / 分布式锁 / 并发模型。
- 数据保留周期、日志采样率、PII 脱敏实现。
- 最终 SLO、最终字段名称、最终错误代码、最终状态枚举名称。
- Retry 的「Optional backup channel」是否存在（Failure Matrix LLM timeout 行）。
- Technical Spike 的目标、最小验证 Graph、Success/Failure Criteria、Spike Report、Architecture Readiness Checklist、READY/NOT READY 决策权限、Spike 后哪些问题进入 RFC、正式业务实现启动条件。

在 **Technical Spike Plan and Architecture Readiness Gate** 议题确认前：**不**实现正式业务 Graph；**不**编写四个核心 Skill 的生产 Prompt；**不**建立正式数据库 Schema；**不**选择生产级基础设施；Development Status 保持 `NOT READY`。
