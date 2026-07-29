# Spike-001 — Test Scenarios

> **Status: PLANNED — NOT STARTED**
> **来源决定：** [DEC-034](../../decisions/dec-034-technical-spike-and-architecture-readiness-gate.md) · [DEC-035](../../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md) · **概念规格：** [../../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../../specs/readiness/technical-spike-and-architecture-readiness-gate.md) · [../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)
> 本文件记录 **12 个必选 / 可选 Spike 场景与各自成功标准**。临时测试栈（pytest + Scenario-based FaultPlan + Scripted Deterministic Model + CLI Scenario Runner）已由 DEC-035 确认；执行授权属下一议题，**尚未确认**。当前**不实现**测试代码。

---

## Spike-01：Normal Workflow

**流程**：`Start → Facts → Insights → Positioning → Review Interrupt → Review Submit → Approved Strategy → Marketing Brief → Complete`

**成功标准**：
- 每个 Stage 只正式提交一次；
- Current Truth Pointer 正确；
- Graph 在 Review 前正确暂停；
- Resume 创建新的 Workflow Run；
- Resume 后不重新执行已完成 Positioning；
- Trace 能关联完整执行链。

---

## Spike-02：Transient Failure and Retry

**模拟**：`Attempt 1 → Transient Error；Attempt 2 → Success`

**成功标准**：
- Skill Run ID 不变；
- Node Execution ID 不变；
- Attempt ID 不同；
- 只创建一个业务版本；
- Retry 与 Rerun 可以明确区分；
- Retry Record 和 Trace 完整。

---

## Spike-03：Invalid Structured Output

**模拟**：非法 JSON / 缺少必填字段 / 非法 Enum / 不存在的 Fact ID 或 Fragment ID。

**成功标准**：
- Schema Validation 生效；
- 允许有限 Deterministic Normalization；
- 允许有限 Constrained Repair；
- 超过上限后 Skill Run 失败；
- 不创建业务版本；
- 不更新 Current Truth；
- 不创建 Formal Evidence Link。

---

## Spike-04：Transactional Rollback

**模拟**：`Domain Version 创建成功 → Evidence Link 写入失败`

**成功标准**：
- Domain Version 回滚；
- Evidence Link 回滚；
- Current Truth Pointer 不变；
- Stage State 不变；
- Audit 不错误记录为成功；
- Retry 后只创建一个正式版本。

---

## Spike-05：Human Review Interrupt and Resume

**成功标准**：
- Review Package 成功创建；
- Graph 正确 Interrupt；
- Task Status 为 `waiting_for_review`；
- Review Submit 事务创建 Approved Strategy；
- Resume 后读取 Approved Strategy Current Truth；
- 不重新生成 Positioning Candidates；
- Resume 操作幂等。

---

## Spike-06：Duplicate Review Submit

**模拟**：使用相同 `review_id / package_version / draft_version / idempotency_key` 提交两次。

**成功标准**：
- 只创建一个 Approved Strategy Version；
- 两次调用返回相同业务结果；
- 下游 Workflow 只恢复一次；
- 不创建重复 Audit Success Record。

---

## Spike-07：Stale Review Package

**流程**：`Review Package 基于 Facts v1 → 审核过程中 Current Facts 变为 v2 → 用户提交旧 Review Package`

**成功标准**：
- 提交被拒绝；
- Review Package 标记为 `superseded`；
- Approved Strategy 不创建；
- 旧 Checkpoint 不继续执行；
- 系统从最早受影响 Stage 重新规划。

---

## Spike-08：Stale Checkpoint

**条件**：Checkpoint 保存时 `fact_version_id = fact-v1`；Resume 时 Current Truth 已是 `fact_version_id = fact-v2`。

**成功标准**：
- Resume 被拒绝；
- Checkpoint 标记为 stale；
- 不覆盖 Fact v2；
- 返回明确 Rerun 或 Recovery 决策；
- 不允许 Checkpointer 覆盖 Business Repository。

---

## Spike-09：Retrieval Degraded Mode

**模拟**：Semantic Retrieval 不可用。

**成功标准**：
- 启用 Direct Read 和 Lexical Retrieval Fallback；
- Retrieval Run 记录 Fallback；
- Evidence Package 记录限制；
- Mock Insight Skill 标记 `succeeded_with_limitations`；
- Evidence Limitation 对用户和下游可见；
- 不扩大 Source Scope。

---

## Spike-10：Cancellation

**模拟**：在长运行 Node 中请求取消。

**成功标准**：
- 不再调度新 Node；
- 当前事务完成或回滚；
- 不留下部分业务版本；
- Workflow Run 标记 `cancelled`；
- 已提交历史版本保留；
- Cancellation Record 可审计。

---

## Spike-11：Retry Budget Exhaustion

**模拟**：让某个 Node 持续失败。

**成功标准**：
- 达到 Retry Budget 后停止；
- 不无限循环；
- 创建 Runtime Error；
- 创建 Recovery Case；
- 记录 Last Safe Checkpoint；
- 提供允许的人工恢复动作；
- Recovery 不绕过 Validator。

---

## Spike-12：Downstream Invalidation（可选）

**流程**：`Marketing Brief v1 → Mock Platform Brief v1 → 用户修改 Marketing Brief，形成 v2`

**成功标准**：
- Facts 保持有效；
- Insights 保持有效；
- Approved Strategy 保持有效；
- Mock Platform Brief v1 失效；
- 重新执行只从 Adapter Stage 开始。

---

## Spike-Optional-01：Real Model Structured Output Smoke Test（可选，不属于 READY 必选）

**模拟**：用真实模型 Adapter 调用一次结构化输出。

**成功标准 / 边界**：
- Model Adapter 能调用；
- 输出进入与 Scripted Model **相同**的 Schema Validator；
- Token 与 Latency Metadata 可记录；
- Provider Error 能进入 Runtime Error Contract；
- 模型失败不绕过 Validator。

**强制边界**：不属于 READY 必选条件；不替代 Scripted Model Tests；不验证业务输出质量；无 API Key 自动 Skip；不影响必选 Scenario 结果；不使用真实用户数据。

---

## 证据与失败处理（适用于所有场景）

- 每个场景须产出 Test Results（Scenario ID / 输入 / 故障注入条件 / 预期 / 实际 / Pass·Fail / 关联日志和 Trace）。
- 关键可靠性场景另须 Transaction Evidence（失败前后 Domain Version 数 / Evidence Link 数 / Current Truth Pointer / Stage State / Audit Record）与 Trace Evidence。
- 失败须创建 Spike Finding（Failed Scenario / Expected / Actual / Root Cause / Implementation Error or Architecture Defect / Candidate Solutions / Affected Decisions / Affected Specifications / RFC Requirement / Recommendation）。
- **当前不实现测试代码。** 临时测试栈已由 DEC-035 确认，但执行授权属下一议题 `Spike-001 Execution Authorization and Agent Handoff Contract`。在该议题经用户确认前：不启动 Spike、不安装依赖、不创建测试代码、不运行测试，Development Status 保持 `NOT READY`，Spike Execution Status 保持 `NOT STARTED`。
