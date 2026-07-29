# DEC-029：Human Review 采用版本化审核包、结构化用户决策与事务化 Approved Strategy 契约

> **Type:** Workflow Contract / Human-in-the-loop Architecture
> **Status:** Accepted
> **Date:** 2026-07-28
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Specification:** [../specs/workflow/human-review-and-approved-strategy-contract.md](../specs/workflow/human-review-and-approved-strategy-contract.md)（概念 Workflow Spec，仅概念）
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** [DEC-007](dec-007-single-review-node-and-exception-pauses.md) by defining the mandatory Human Review node and [DEC-024](dec-024-versioned-domain-state-and-compact-langgraph-state.md) by defining the Approved Strategy Current Truth transition（在 DEC-007「单一关键审核节点 + 异常暂停」与 DEC-024「版本化领域状态 + Current Truth Version Pointers」基础上，正式定义强制 Human Review 节点的结构化执行契约，**不推翻** DEC-007 与 DEC-024 的既有结论）。

---

## 用户确认

用户对该 Human Review and Approved Strategy Contract Proposal 明确回复：

> 确认

本决定经 Decision Gate 通过，记录为 Accepted Decision（Type: Workflow Contract / Human-in-the-loop Architecture）。

被接受的核心结论：

- Human Review 是核心工作流中的强制结构化决策节点，而不是简单的 Approve 按钮。
- 系统需要生成固定上游版本的 Review Package，集中展示 Positioning Candidates、关键 Facts、关键 Insights、Hypotheses、Evidence Limitations、Proof Points 和 Strategic Risks。
- 用户可以选择、编辑、合并、拒绝候选，要求补充资料，保存审核草稿并最终提交。
- Strategy Draft 不能被下游使用。只有用户明确提交、且通过版本、证据、Schema、幂等和事务校验后，系统才能创建 Approved Strategy Version。
- 用户接受 Hypothesis 不会将其转化为 Fact，Evidence Limitations 不能被静默删除，所有 Proof Point 必须继续追溯到有效 Fact。
- 上游版本变化后，旧 Review Package 必须失效；重复提交不能创建重复版本；用户撤回或修改 Approved Strategy 后，Marketing Brief 和 Xiaohongshu Mapping 必须失效。

---

## Decision

AI Ecommerce Agent 的核心工作流正式包含强制 Human Review：

```text
Facts
+
Insights
+
Positioning Candidates
↓
Versioned Review Package
↓
Structured User Decisions
↓
Deterministic Validation
↓
Approved Strategy Version
↓
Marketing Brief Generation
```

Product Positioning Skill 不得直接创建 Approved Strategy。

只有用户明确提交审核结果后，Human Review Service 才能创建 Approved Strategy Version。

### Review Purpose

Human Review 负责让用户承担以下战略判断：

- 目标用户是否符合实际业务方向；
- 哪个用户问题值得优先解决；
- 哪个定位方向符合品牌与市场；
- 哪些假设可以接受；
- 哪些假设只能用于测试；
- 哪些证据限制可以容忍；
- 哪些 Proof Points 可以使用；
- 是否需要补充信息；
- 是否需要重新生成候选。

Human Review 不是：

```text
AI 输出
→ 用户点击同意
```

而是：

```text
AI 提供候选与证据
→ 用户进行结构化选择和修改
→ 系统校验
→ 创建正式战略版本
```

---

## Review Package

Review Package 是某次审核使用的固定输入快照。

概念结构：

```text
ReviewPackage
├── review_id
├── task_id
├── package_version
├── facts_version_id
├── insights_version_id
├── positioning_version_id
├── source_set_version_ids[]
├── positioning_candidates[]
├── critical_facts[]
├── critical_insights[]
├── hypotheses[]
├── evidence_limitations[]
├── source_conflicts[]
├── strategic_risks[]
├── model_recommendation
├── created_at
└── status
```

Review Package 必须固定审核时使用的：

- Facts Version；
- Insights Version；
- Positioning Version；
- Source Set Versions；
- Positioning Candidates；
- Evidence Limitations。

用户开始审核后，不得在后台静默替换审核内容。

---

## Review Package Version Validity

提交审核前，必须验证 Review Package 仍然基于当前有效上游版本。

若以下任一版本发生变化：

```text
facts_version_id
insights_version_id
positioning_version_id
relevant_source_set_version_id
```

原 Review Package 必须标记为：

```text
superseded
```

用户不得继续提交旧审核包。

系统应：

1. 阻止旧版本提交；
2. 说明哪些上游内容发生变化；
3. 创建新的 Review Package；
4. 要求用户重新确认受影响内容；
5. 不自动将旧审核选择应用到新版本。

---

## Mandatory Review Content

### Positioning Candidates

每个候选至少展示：

- Target Segment；
- Usage Context；
- Job or Core Need；
- Category Frame；
- Value Proposition；
- Differentiation；
- Key Benefits；
- Reasons to Believe；
- Proof Points；
- Assumptions；
- Evidence Limitations；
- Strategic Risks；
- Model Recommendation Rationale。

### Critical Facts

不要求用户逐条审核所有 Fact，但以下事实必须可见：

- 支撑 Value Proposition 的事实；
- 所有 Proof Points；
- 性能或功效声明；
- 认证和检测结果；
- 时间敏感事实；
- 用户修改过的事实；
- 曾存在冲突的事实。

### Critical Insights

至少包括：

- 定位候选实际使用的 Insights；
- 核心用户需求；
- 购买障碍；
- 信任顾虑；
- 证据有限的 Insights；
- 存在明显 Contradicting Evidence 的 Insights。

### Hypotheses

所有影响战略的 Hypothesis 必须集中展示，例如：

- Target Segment Hypothesis；
- User Need Hypothesis；
- Usage Context Hypothesis；
- Opportunity Hypothesis；
- Purchase Motivation Hypothesis。

### Evidence Limitations

至少展示：

- 没有当前商品用户评论；
- 只有竞品用户证据；
- 样本量有限；
- 缺少完整市场数据；
- 缺少竞品参数；
- 声明只有营销页面支持；
- Source Version 较旧；
- 某些数据无法验证。

---

## Review Actions

用户可以执行：

```text
select
edit
merge
reject
request_more_information
save_draft
submit
withdraw
```

### select

选择一个 Positioning Candidate 作为 Strategy Draft 的主要基础。

Select 不等于 Approve。

### edit

用户可以修改：

- Target Segment；
- Usage Context；
- Job or Core Need；
- Category Frame；
- Value Proposition；
- Differentiation；
- Key Benefits；
- Reasons to Believe；
- Proof Points；
- 卖点优先级；
- Assumptions；
- User Notes。

修改不得静默覆盖原始候选，必须保留原模型版本和用户修改记录。

### merge

用户可以组合多个候选，例如：

```text
Candidate A Target Segment
+
Candidate B Value Proposition
+
Candidate C Proof Points
```

合并后形成新的 Strategy Draft。

Merge 后必须重新执行：

- Schema Validation；
- Fact Reference Validation；
- Insight Reference Validation；
- Proof Point Validation；
- Logical Consistency Validation；
- Evidence Limitation Validation。

### reject

用户可以：

- 拒绝某个候选；
- 拒绝所有候选；
- 说明拒绝原因；
- 要求重新生成。

拒绝全部候选后，不得进入 Marketing Brief Generation。

### request_more_information

用户可以要求补充：

- 商品资料；
- 用户评论；
- 用户访谈；
- 问卷；
- 竞品资料；
- 检测报告；
- 品牌方向；
- 市场约束。

此动作会将任务设置为：

```text
waiting_for_input
```

并根据新增或修改的来源触发上游阶段失效与重跑。

### save_draft

保存未完成的审核草稿。

Review Draft：

- 可以不完整；
- 可以尚未处理所有 Hypothesis；
- 可以尚未通过 Validator；
- 不更新 Approved Strategy Current Truth；
- 不允许 Marketing Brief 读取。

### submit

提交审核结果，触发事务化 Approved Strategy 创建。

### withdraw

撤回已经批准的 Approved Strategy。

撤回不删除历史版本。

---

## Strategy Draft

Strategy Draft 是用户审核过程中的临时工作内容。

概念上需要保留：

```text
StrategyDraft
├── draft_id
├── review_id
├── draft_version
├── based_on_candidate_ids[]
├── selected_content
├── user_edits[]
├── merge_sources[]
├── hypothesis_decisions[]
├── proof_point_decisions[]
├── user_notes
├── updated_at
└── status
```

Strategy Draft：

- 不属于业务 Current Truth；
- 不允许下游使用；
- 可以多次修改；
- 可以自动保存；
- 必须记录版本；
- 提交前必须通过 Validator。

最终 Draft 自动保存频率和尚未确认。

---

## Approved Strategy

Approved Strategy 是用户明确提交并通过校验后生成的正式版本化业务对象。

概念结构：

```text
ApprovedStrategy
├── approved_strategy_version_id
├── task_id
├── based_on_review_id
├── based_on_review_package_version
├── based_on_positioning_version_id
├── selected_candidate_ids[]
├── target_segment
├── usage_context
├── job_or_core_need
├── category_frame
├── value_proposition
├── differentiation
├── key_benefits[]
├── reasons_to_believe[]
├── proof_points[]
├── accepted_hypotheses[]
├── rejected_hypotheses[]
├── evidence_limitations[]
├── strategic_risks[]
├── user_notes
├── approved_by
├── approved_at
└── version_status
```

Approved Strategy 是 Marketing Brief Generation 唯一允许读取的战略输入。

Marketing Brief Skill 不得直接读取未经审核的 Positioning Candidate 作为正式策略。

---

## Hypothesis Decisions

重要 Hypothesis 必须逐项处理。

允许动作：

```text
accept_for_execution
accept_for_testing
edit
reject
request_evidence
```

### accept_for_execution

用户允许该 Hypothesis 作为当前战略输入。

但系统必须继续保留：

```text
evidence_class = hypothesis_to_validate
```

或语义等价标识。

### accept_for_testing

允许该 Hypothesis 作为营销测试方向。

必须标记：

```text
requires_validation = true
```

不得转化为确定性商品承诺或 Proof Point。

### edit

用户可以修改 Hypothesis 的表述或范围。

修改后仍保持 Hypothesis 身份，除非新的直接证据经过上游流程生成正式 Fact 或 Insight。

### reject

从 Approved Strategy 中移除。

### request_evidence

暂停当前审核并要求补充证据。

用户接受 Hypothesis 不等于：

```text
Hypothesis → Fact
```

---

## Evidence Limitation Decisions

Evidence Limitations 必须继续保存在 Approved Strategy 中。

用户可以确认：

```text
accepted_by_user = true
```

但不能删除客观存在的限制。

例如：

```text
Limitation:
当前没有直接用户评论

User Decision:
接受该限制，先作为通勤场景测试方向
```

Marketing Brief Skill 必须读取并继续传播这些限制。

不得因为用户点击确认而将 Evidence Limitation 从数据中移除。

---

## Proof Point Review

每个 Proof Point 必须向用户展示完整追踪链：

```text
Proof Point
→ Fact
→ Evidence Link
→ Fragment
→ Source Version
```

用户可以：

- accept；
- remove；
- rephrase；
- downgrade_to_reason_to_believe；
- request_evidence。

用户修改 Proof Point 表述后，Validator 必须检查新表述是否仍然被原 Fact 支持。

用户不得把无证据内容直接升级为 Proof Point。

例如：

```text
"市场上最轻"
```

若没有市场比较证据，则必须拒绝进入 Proof Points。

可以保存为：

```text
Business Assumption
```

或：

```text
Positioning Hypothesis
```

但不能作为确定性证明点。

---

## Review Submission Transaction

`submit` 必须作为原子事务处理。

概念流程：

```text
1. Receive submission with idempotency key
2. Lock or verify current Review Draft version
3. Validate Review Package status
4. Validate upstream versions
5. Validate mandatory review items
6. Validate Strategy Draft schema
7. Validate Fact and Insight references
8. Validate Proof Points
9. Validate Hypothesis decisions
10. Validate Evidence Limitations
11. Create Approved Strategy Version
12. Update Current Truth Pointer
13. Review Status → approved
14. Positioning Stage → valid
15. Review Stage → valid
16. Marketing Brief Stage → ready
17. Write Audit Record
18. Commit transaction
```

任何步骤失败时：

- 不创建 Approved Strategy Version；
- 不更新 Current Truth Pointer；
- 不改变下游阶段状态；
- 不允许 Marketing Brief 执行；
- 返回可恢复的校验错误。

---

## Idempotency and Concurrency

提交请求必须至少携带：

```text
review_id
package_version
draft_version
idempotency_key
```

### Duplicate Submission

相同 `idempotency_key` 重复提交时：

- 返回第一次成功生成的 Approved Strategy；
- 不创建第二个版本；
- 不重复推进 Workflow。

### Stale Submission

若提交使用的：

- Package Version；
- Draft Version；
- Facts Version；
- Insights Version；
- Positioning Version；

已经过期，则必须拒绝。

### Concurrent Editing

多个标签页或客户端同时编辑时，不得静默覆盖较新的 Draft。

具体采用：

- Optimistic Lock；
- Revision Number；
- ETag；
- Database Lock；

尚未确认。

---

## Review Withdrawal

用户可以撤回已经批准的 Strategy。

撤回操作必须：

1. 创建 Withdrawal Record；
2. 保留原 Approved Strategy；
3. 将其标记为 `withdrawn` 或 `superseded`；
4. 清除当前 Approved Strategy Pointer；
5. 使 Marketing Brief Stage 失效；
6. 使 Xiaohongshu Mapping Stage 失效；
7. 保留旧 Brief 和 Mapping 历史；
8. 创建新的 Review Cycle；
9. Task Status → `waiting_for_review`。

若下游尚未生成，只影响 Review 和 Approved Strategy。

若下游已经生成，遵循 DEC-009：

```text
Approved Strategy 修改或撤回
→ Marketing Brief invalid
→ Xiaohongshu Mapping invalid
```

---

## Review History and Audit

系统必须保留：

- 原始 Positioning Candidates；
- Model Recommendation；
- 用户选择；
- 用户编辑；
- Merge 来源；
- 被拒绝候选；
- Hypothesis Decisions；
- Proof Point Decisions；
- Evidence Limitation Decisions；
- Request More Information；
- Draft Versions；
- Submission；
- Approved Strategy Versions；
- Withdrawal；
- 审核时间；
- 用户备注；
- 失败校验记录。

审核历史用于：

- 业务审计；
- 人机协作分析；
- 模型质量评估；
- Prompt 回归；
- 用户修改量统计；
- 决策复盘；
- Approved Strategy 版本追踪。

---

## Review Status

概念状态：

```text
not_ready
pending
in_progress
changes_requested
submitted
approved
superseded
withdrawn
cancelled
```

### not_ready

上游尚未生成可审核 Positioning Candidates。

### pending

Review Package 已创建，等待用户开始。

### in_progress

用户正在审核或已经保存 Draft。

### changes_requested

用户要求补充资料或重新生成。

### submitted

用户已经提交，系统正在执行事务处理。

### approved

Approved Strategy Version 已成功创建。

### superseded

上游版本变化导致当前 Review Package 或 Review 失效。

### withdrawn

用户撤回已经批准的 Strategy。

### cancelled

用户取消本次 Review Cycle。

最终状态名称尚未确认，但必须覆盖以上语义。

---

## Deterministic Validator

Approved Strategy 创建前，至少检查：

1. Review Package 真实存在；
2. Package Version 与提交版本一致；
3. Review Package 未被 superseded；
4. Facts Version 当前有效；
5. Insights Version 当前有效；
6. Positioning Version 当前有效；
7. 选择或 Merge 来源可追踪；
8. Target Segment 不为空；
9. Usage Context 满足最低要求；
10. Job or Core Need 不为空；
11. Value Proposition 不为空；
12. Differentiation 不为空；
13. 所有 Proof Point 关联有效 Fact；
14. 不存在竞品能力泄漏；
15. 不存在无来源数值、认证或性能声明；
16. Hypothesis 未被转换为 Fact；
17. 所有关键 Hypothesis 已处理；
18. Evidence Limitations 未被静默删除；
19. 用户编辑内容符合 Schema；
20. Merge 内容不存在明显逻辑冲突；
21. Fact、Insight 与 Proof Point 引用仍有效；
22. Source Versions 当前可用；
23. Draft Version 未过期；
24. 提交满足幂等要求；
25. Approved Strategy 尚未被重复创建。

---

## Responsibility Boundary

### LLM

允许：

- 解释候选差异；
- 辅助润色用户编辑；
- 检查 Strategy Draft 表述一致性；
- 提示可能遗漏的假设；
- 提示可能遗漏的风险；
- 帮助总结用户修改。

禁止：

- 自动选择候选；
- 自动接受 Hypothesis；
- 自动删除 Evidence Limitation；
- 自动批准 Strategy；
- 自动提交 Review；
- 将无证据内容升级为 Proof Point；
- 绕过确定性 Validator。

### Deterministic Logic

负责：

- Package Version；
- Upstream Version Validation；
- Schema；
- Evidence Link；
- Proof Point Validation；
- Hypothesis Status；
- Evidence Limitation Preservation；
- Idempotency；
- Concurrency；
- Transaction；
- Current Truth Pointer；
- Workflow Status；
- Downstream Invalidation；
- Audit Record。

### Human

负责：

- Select；
- Edit；
- Merge；
- Reject；
- Request More Information；
- 接受、测试或拒绝 Hypothesis；
- 处理 Proof Points；
- 接受 Evidence Limitations；
- Submit；
- Withdraw；
- 最终战略决策。

---

## Evaluation Metrics

### Hard Reliability Metrics

MVP 目标：

```text
Approved Strategy Without Review Rate = 0%
Unsupported Proof Point Approval Rate = 0%
Stale Review Submission Success Rate = 0%
Duplicate Approved Version Rate = 0%
Unresolved Critical Hypothesis Rate = 0%
Silent Evidence Limitation Removal Rate = 0%
```

### User Efficiency Metrics

包括：

- 打开 Review 到提交的时间；
- 用户修改字段数量；
- 直接选择候选比例；
- Merge 使用率；
- Request More Information 比例；
- 全部候选拒绝率；
- Review Withdrawal Rate；
- Draft Resume Success Rate。

### Human-AI Collaboration Metrics

包括：

- Model Recommendation 被选择比例；
- 推荐候选的用户修改量；
- 用户删除的 Proof Point 数量；
- 用户拒绝的 Hypothesis 数量；
- Approved Strategy 与原 Positioning Candidate 的差异程度；
- 人工修改后策略质量提升程度。

---

## Required Test Scenarios

### Direct Candidate Selection

预期：

- 用户选择一个候选；
- 处理 Hypotheses；
- 确认 Evidence Limitations；
- 创建 Approved Strategy；
- Marketing Brief Stage → ready。

### Merge Candidates

预期：

- 形成新 Strategy Draft；
- 保存 Merge 来源；
- 重新校验 Proof Points；
- Validator 通过后才允许提交。

### Upstream Changes During Review

预期：

- 原 Review Package → superseded；
- 旧提交被拒绝；
- 创建新 Review Package；
- 不自动迁移旧审批。

### Duplicate Submission

预期：

- 只创建一个 Approved Strategy Version；
- 重复请求返回相同结果。

### Unsupported User-added Proof Point

预期：

- Validator 拒绝；
- 可以降级为 Business Assumption；
- 不允许进入正式 Proof Points。

### Withdraw Approved Strategy

预期：

- 保留历史 Strategy；
- 当前 Strategy Pointer 清除；
- Brief 与 Mapping 失效；
- 创建新 Review Cycle。

### Save Draft and Resume

预期：

- Draft 可恢复；
- 不改变 Current Truth；
- 不推进下游工作流。

---

## Contract Summary

```text
Component:
Human Review and Approved Strategy

Input:
- Versioned Review Package
- Positioning Candidates
- Critical Facts and Insights
- Hypotheses
- Evidence Limitations
- Strategic Risks

User Actions:
- Select
- Edit
- Merge
- Reject
- Request More Information
- Save Draft
- Submit
- Withdraw

Output:
- Approved Strategy Version
- Review Decisions
- Audit Record
- Downstream Workflow Decision

Hard Rules:
- No Approved Strategy without explicit user submission
- No stale Review Package submission
- No unsupported Proof Point
- No silent removal of Evidence Limitations
- No automatic Hypothesis-to-Fact conversion
```

---

## Reason

Product Positioning 是战略推断，不存在模型可以自动证明的唯一正确方向。

如果允许模型自动创建 Approved Strategy，或者将 Review 简化为无上下文的同意按钮，将产生：

- 用户不了解证据限制；
- 假设被误当作事实；
- Proof Point 缺少依据；
- 模型替用户完成战略选择；
- 上游变化后继续使用旧审核；
- 重复提交产生多个 Current Truth；
- 用户修改无法审计；
- 下游 Brief 建立在未确认策略上。

因此 Human Review 必须成为：

> 版本固定、证据透明、操作结构化、提交事务化、历史可追踪的强制战略决策节点。

---

## Impact

该决定将影响：

- LangGraph Interrupt / Resume；
- Review Service；
- Review Package；
- Strategy Draft；
- Approved Strategy Domain Model；
- Database Transactions；
- Idempotency；
- Concurrency；
- Workflow State；
- Current Truth；
- Invalidation；
- Marketing Brief Skill；
- Frontend Review UI；
- Evaluation；
- Audit Logs。

---

## Decision Boundary

本决定已经确认：

- Human Review 是强制结构化决策节点；
- Review Package 固定上游具体版本；
- 上游变化使 Review Package superseded；
- 必审内容；
- Select、Edit、Merge、Reject；
- Request More Information；
- Save Draft；
- Submit；
- Withdraw；
- Strategy Draft 与 Approved Strategy 分离；
- 只有明确提交才能创建 Approved Strategy；
- 重要 Hypothesis 逐项处理；
- 接受 Hypothesis 不会将其转成 Fact；
- Evidence Limitations 必须保留；
- Proof Point 必须继续追溯到 Fact；
- 提交使用原子事务；
- 提交必须幂等；
- 旧版本提交必须拒绝；
- 支持撤回；
- 撤回使下游失效；
- 保留完整审核历史；
- LLM 只能辅助，不能自动批准；
- 确定性 Validator 是创建 Approved Strategy 的必要 Gate；
- Approved Strategy 是 Marketing Brief 唯一正式战略输入。

本决定尚未确认：

- 最终 Review Schema；
- 最终 Approved Strategy Schema；
- 最终字段名称；
- Review UI；
- Draft 自动保存频率；
- Patch 或完整 Snapshot；
- 并发锁实现；
- 数据库事务实现；
- LangGraph Interrupt Payload；
- API；
- 审核权限；
- 多人协作审核；
- 电子签名；
- 审批链；
- 具体错误代码。

---

## Related Session

[Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)

---

## Related Decisions

- [DEC-009 — MVP 采用阶段级依赖失效与局部重跑](dec-009-stage-level-invalidation-and-partial-rerun.md)（Stage Invalidation；撤回 / 上游变化触发的下游失效）
- [DEC-012 — Workflow State 采用阶段状态与关键条目结构化设计](dec-012-stage-state-and-structured-business-items.md)（阶段状态 + 结构化业务条目）
- [DEC-013 — MVP 采用支持跨会话恢复的任务级持久化状态](dec-013-task-level-persistent-state-and-cross-session-resume.md)（任务级持久化与 Resume）
- [DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（Core Workflow 与单审核 Gate）
- [DEC-023 — MVP 选择 LangGraph StateGraph 作为核心工作流运行方式](dec-023-select-langgraph-stategraph-for-mvp-workflow.md)（LangGraph Interrupt / Resume / Checkpoint）
- [DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](dec-024-versioned-domain-state-and-compact-langgraph-state.md)（版本化 Domain Objects + Current Truth Pointer + 结构化 ReviewState；**本决定 Amends DEC-024**）
- [DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](dec-025-versioned-sources-fragments-and-evidence-links.md)（Proof Point 追溯至 Fact → Evidence Link → Fragment → Source Version）
- [DEC-028 — Product Positioning Skill 采用多候选、证据约束与强制人工决策契约](dec-028-product-positioning-skill-contract.md)（上游 Positioning Candidates；Product Positioning Skill 不得直接创建 Approved Strategy）

---

## Related RFC

None

---

## Supersedes

None

---

## Amends

**Amends [DEC-007](dec-007-single-review-node-and-exception-pauses.md)** by defining the mandatory Human Review node，并 **Amends [DEC-024](dec-024-versioned-domain-state-and-compact-langgraph-state.md)** by defining the Approved Strategy Current Truth transition。

- DEC-007 确认 MVP 采用单一关键审核节点 + 异常暂停 + 用户最终判断权（尚未确认 LangGraph / Interrupt / Checkpoint / 审核页面 / 风险规则）。
- DEC-024 确认版本化 Domain Objects + Current Truth Version Pointers + 结构化 ReviewState（ReviewState 含 status / review_package_version / reviewed_entities / user_decisions[] / unresolved_items[]；ReviewDecision action ∈ accept / edit / reject / replace / request_more_information；Review 完成意味形成已审核策略版本而非接受所有模型建议）。
- DEC-029 在此基础上正式定义该 **Human Review 节点的概念层执行契约**（版本化 Review Package / 版本有效性 / 必审内容 / Review Actions 含 select·edit·merge·reject·request_more_information·save_draft·submit·withdraw / Strategy Draft / Approved Strategy / Hypothesis Decisions / Evidence Limitation Decisions / Proof Point Review / 提交事务 / 幂等与并发 / 撤回 / 审核历史 / Review Status / Validator 25 项 / 职责边界 / 评价指标 / 测试场景），并把 Review Actions 在 DEC-024 的 5 项（accept / edit / reject / replace / request_more_information）基础上细化为面向候选与提交事务的完整动作集。
- **不推翻** DEC-007「单一关键审核节点 + 异常暂停 + 用户最终判断权」与 DEC-024「版本化领域状态 + Current Truth Pointer + 结构化 ReviewState」既有结论；DEC-007 与 DEC-024 行作为历史记录不修改，本 Amends 关系仅在此处记录。

---

## Notes

- 本决定保持 **Development Status: NOT READY**。
- 当前**不**创建 Review UI / LangGraph Interrupt 代码 / Resume 代码 / 数据库表 / API / 并发锁实现 / Transaction 代码 / Draft 自动保存代码 / Approved Strategy Service 代码。
- 当前**不**选择前端框架 / 数据库 / 并发控制技术 / Draft 存储方案 / API 框架 / 权限系统 / 多人审批系统。
- 当前**不**创建 RFC。
- 概念 Workflow Spec 见 [../specs/workflow/human-review-and-approved-strategy-contract.md](../specs/workflow/human-review-and-approved-strategy-contract.md)（仅概念，非最终实现）。
- 该节点承接 DEC-020 核心链路中的强制 Human Review Gate（`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation → Xiaohongshu Brief Mapping`）；其输入为 Product Positioning Skill（DEC-028）输出的 Positioning Candidates，其输出 Approved Strategy Version 是下游 Marketing Brief Generation 的唯一正式战略输入。
- 审核错误（业务资料不足 / 假设未处理 / Proof Point 无依据）与技术失败（事务失败 / 并发冲突 / 持久化失败）严格分离，业务审核问题**不得**误标为技术失败。
