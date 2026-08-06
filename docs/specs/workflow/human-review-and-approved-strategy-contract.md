# Human Review and Approved Strategy Contract（概念 Workflow Spec）

> **Status:** PRODUCT SEMANTICS ACCEPTED / IMPLEMENTATION CONTRACT CONCEPTUAL（产品语义已确认；最终 Schema / 字段名 / 数据库表 / API / Review UI / LangGraph Interrupt Payload / 并发实现 / Transaction 实现仍未确认）
> **来源 Decision：** [DEC-029 — Human Review 采用版本化审核包、结构化用户决策与事务化 Approved Strategy 契约](../../decisions/dec-029-human-review-and-approved-strategy-contract.md) 与 [DEC-046 — 冻结审核、Brief 与导出的产品语义和版本行为](../../decisions/dec-046-review-brief-and-export-product-contract.md)（均 Accepted）
> **承接：** DEC-009（阶段失效）/ DEC-012（阶段状态 + 结构化条目）/ DEC-013（任务级持久化与 Resume）/ DEC-020（核心工作流单审核 Gate）/ DEC-023（LangGraph Interrupt / Resume）/ DEC-024（版本化 Domain Objects + Current Truth Pointer + 结构化 ReviewState）/ DEC-025（Proof Point → Fact → Evidence Link → Fragment → Source Version）/ DEC-028（上游 Positioning Candidates）
> **本文件是 Current Truth Layer 的一部分，但当前仅为概念规格。** 所有字段名 / 枚举 / 概念结构均为**概念示意，非最终数据契约**。

---

## §0 定位

本规格定义 MVP 核心工作流中 **强制 Human Review 节点** 的概念层执行契约。

Human Review 不是「AI 输出 → 用户点击同意」，而是：

```text
AI 提供候选与证据
→ 用户进行结构化选择和修改
→ 系统校验
→ 创建正式战略版本（Approved Strategy Version）
```

该节点在 DEC-020 核心链路中位于 Product Positioning 与 Marketing Brief Generation 之间：

```text
Product Positioning
→ Human Review Gate（本规格）
→ Marketing Brief Generation
```

只有经 Human Review 形成的 **Approved Strategy Version** 才能进入 Marketing Brief Generation。

---

## §1 Purpose

Human Review 让用户承担以下战略判断（非模型可代劳）：

- 目标用户是否符合实际业务方向；
- 哪个用户问题值得优先解决；
- 哪个定位方向符合品牌与市场；
- 哪些假设可以接受；
- 哪些假设只能用于测试；
- 哪些证据限制可以容忍；
- 哪些 Proof Points 可以使用；
- 是否需要补充信息；
- 是否需要重新生成候选。

---

## §2 Review Package

Review Package 是某次审核使用的**固定输入快照**（不可在审核进行中后台静默替换）。DEC-046 冻结其产品语义组为：版本上下文 / Positioning Candidates / 关键 Facts 与 Insights / Hypotheses / Evidence Limitations / Conflicts 与 Strategic Risks / Model Recommendation。以下字段仅说明这些语义的概念展开，不是最终公共 Schema；不要求为凑齐分组而制造不存在的内容。

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

Review Package 必须固定审核时使用的：Facts Version / Insights Version / Positioning Version / Source Set Versions / Positioning Candidates / Evidence Limitations。用户开始审核后，**不得**在后台静默替换审核内容。

---

## §3 Version Validity

提交审核前，必须验证 Review Package 仍然基于当前有效上游版本。若以下任一版本发生变化——`facts_version_id` / `insights_version_id` / `positioning_version_id` / `relevant_source_set_version_id`——原 Review Package 必须标记为 `superseded`，用户不得继续提交旧审核包。

系统应：

1. 阻止旧版本提交；
2. 说明哪些上游内容发生变化；
3. 创建新的 Review Package；
4. 要求用户重新确认受影响内容；
5. 不自动将旧审核选择应用到新版本。

---

## §4 Mandatory Review Content

### 4.1 Positioning Candidates

每个候选至少展示：Target Segment / Usage Context / Job or Core Need / Category Frame / Value Proposition / Differentiation / Key Benefits / Reasons to Believe / Proof Points / Assumptions / Evidence Limitations / Strategic Risks / Model Recommendation Rationale。

### 4.2 Critical Facts

不要求用户逐条审核所有 Fact，但以下事实必须可见：支撑 Value Proposition 的事实 / 所有 Proof Points / 性能或功效声明 / 认证和检测结果 / 时间敏感事实 / 用户修改过的事实 / 曾存在冲突的事实。

### 4.3 Critical Insights

至少包括：定位候选实际使用的 Insights / 核心用户需求 / 购买障碍 / 信任顾虑 / 证据有限的 Insights / 存在明显 Contradicting Evidence 的 Insights。

### 4.4 Hypotheses

所有影响战略的 Hypothesis 必须集中展示：Target Segment Hypothesis / User Need Hypothesis / Usage Context Hypothesis / Opportunity Hypothesis / Purchase Motivation Hypothesis。

### 4.5 Evidence Limitations

至少展示：没有当前商品用户评论 / 只有竞品用户证据 / 样本量有限 / 缺少完整市场数据 / 缺少竞品参数 / 声明只有营销页面支持 / Source Version 较旧 / 某些数据无法验证。

---

## §5 Review Actions

用户可执行：

```text
select / edit / merge / reject / request_more_information / save_draft / submit / withdraw
```

### 5.1 select

选择一个 Positioning Candidate 作为 Strategy Draft 的主要基础。**Select 不等于 Approve。**

### 5.2 edit

用户可修改 Target Segment / Usage Context / Job or Core Need / Category Frame / Value Proposition / Differentiation / Key Benefits / Reasons to Believe / Proof Points / 卖点优先级 / Assumptions / User Notes。修改**不得**静默覆盖原始候选，必须保留原模型版本和用户修改记录。

### 5.3 merge

用户可组合多个候选（如 Candidate A 的 Target Segment + Candidate B 的 Value Proposition + Candidate C 的 Proof Points），形成新的 Strategy Draft。**Merge 后必须重新执行：** Schema Validation / Fact Reference Validation / Insight Reference Validation / Proof Point Validation / Logical Consistency Validation / Evidence Limitation Validation。

### 5.4 reject

用户可拒绝某个候选 / 拒绝所有候选 / 说明拒绝原因 / 要求重新生成。拒绝全部候选后，**不得**进入 Marketing Brief Generation。

### 5.5 request_more_information

用户可要求补充：商品资料 / 用户评论 / 用户访谈 / 问卷 / 竞品资料 / 检测报告 / 品牌方向 / 市场约束。此动作将任务设置为 `waiting_for_input`，并根据新增或修改的来源触发上游阶段失效与重跑。

### 5.6 save_draft

保存未完成的审核草稿。Review Draft 可以不完整 / 可以尚未处理所有 Hypothesis / 可以尚未通过 Validator / **不更新** Approved Strategy Current Truth / **不允许** Marketing Brief 读取。

### 5.7 submit

提交审核结果，触发事务化 Approved Strategy 创建（见 §11）。

### 5.8 withdraw

撤回已经批准的 Approved Strategy。撤回不删除历史版本（见 §14）。

---

## §6 Strategy Draft

Strategy Draft 是用户审核过程中的**临时工作内容**，不属于业务 Current Truth。

概念结构：

```text
StrategyDraft
├── draft_id
├── review_id
├── revision
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

Strategy Draft：不属于业务 Current Truth / 不允许下游使用 / 可以多次修改 / 可以自动保存 / 必须记录单调递增 revision / 提交前必须通过 Validator。每次成功保存产生更高 revision；基于旧 revision 的保存或提交必须拒绝。**Draft 自动保存频率、传输字段名和并发实现仍未确认。**

---

## §7 Approved Strategy

Approved Strategy 是用户明确提交并通过校验后生成的**正式版本化业务对象**（版本化 Domain Object，承接 DEC-024）。

DEC-046 冻结其产品语义组为：目标与情境 / 定位 / 说服结构 / 假设决策 / 证据与风险 / 审核与版本元数据。以下字段为概念展开，最终公共 Schema 由 RFC-004 冻结。

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

Approved Strategy 是 Marketing Brief Generation **唯一允许读取的战略输入**。Marketing Brief Skill **不得**直接读取未经审核的 Positioning Candidate 作为正式策略。

---

## §8 Hypothesis Decisions

重要 Hypothesis 必须**逐项处理**。允许动作：`accept_for_execution` / `accept_for_testing` / `edit` / `reject` / `request_evidence`。

- **accept_for_execution：** 用户允许该 Hypothesis 作为当前战略输入，但系统必须继续保留 `evidence_class = hypothesis_to_validate`（或语义等价标识）。
- **accept_for_testing：** 允许作为营销测试方向，必须标记 `requires_validation = true`，**不得**转化为确定性商品承诺或 Proof Point。
- **edit：** 用户可修改 Hypothesis 的表述或范围；修改后仍保持 Hypothesis 身份，除非新的直接证据经过上游流程生成正式 Fact 或 Insight。
- **reject：** 从 Approved Strategy 中移除。
- **request_evidence：** 暂停当前审核并要求补充证据。

**用户接受 Hypothesis 不等于 `Hypothesis → Fact`。**

---

## §9 Evidence Limitation Decisions

Evidence Limitations 必须**继续保存在 Approved Strategy 中**。用户可确认 `accepted_by_user = true`，但**不能**删除客观存在的限制。

例如：

```text
Limitation:
当前没有直接用户评论

User Decision:
接受该限制，先作为通勤场景测试方向
```

Marketing Brief Skill 必须读取并继续传播这些限制。**不得**因为用户点击确认而将 Evidence Limitation 从数据中移除。

---

## §10 Proof Point Review

每个 Proof Point 必须向用户展示完整追踪链：

```text
Proof Point → Fact → Evidence Link → Fragment → Source Version
```

用户可：accept / remove / rephrase / downgrade_to_reason_to_believe / request_evidence。

- 用户修改 Proof Point 表述后，Validator 必须检查新表述是否仍然被原 Fact 支持。
- 用户**不得**把无证据内容直接升级为 Proof Point。例如「市场上最轻」若没有市场比较证据，则必须拒绝进入 Proof Points，可保存为 Business Assumption 或 Positioning Hypothesis，但不能作为确定性证明点。

---

## §11 Submission Transaction

`submit` 必须作为**原子事务**处理。概念流程：

```text
 1. Receive submission with idempotency key
 2. Lock or verify current Review Draft revision
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

任何步骤失败时：不创建 Approved Strategy Version / 不更新 Current Truth Pointer / 不改变下游阶段状态 / 不允许 Marketing Brief 执行 / 返回**可恢复**的校验错误。

---

## §12 Idempotency

提交请求必须至少表达 `review_id` / `package_version` / `revision` / `idempotency_key` 的语义；最终字段名由 RFC-004 冻结。

**Duplicate Submission：** 相同 `idempotency_key` 重复提交时，返回第一次成功生成的 Approved Strategy，不创建第二个版本，不重复推进 Workflow。

**Stale Submission：** 若提交使用的 Package Version / Draft Revision / Facts Version / Insights Version / Positioning Version 已经过期，则必须拒绝。

---

## §13 Concurrency

多个标签页或客户端同时编辑时，**不得静默覆盖较新的 Draft**。产品行为已冻结为单调递增 revision 与陈旧保存 / 提交拒绝；具体采用请求头、ETag、数据库锁或其他并发机制，**尚未确认**。

---

## §14 Withdrawal

用户可撤回已经批准的 Strategy。撤回操作必须：

1. 创建 Withdrawal Record；
2. 保留原 Approved Strategy；
3. 将其标记为 `withdrawn` 或 `superseded`；
4. 清除当前 Approved Strategy Pointer；
5. 使 Marketing Brief Stage 失效；
6. 使 Xiaohongshu Mapping Stage 失效；
7. 保留旧 Brief 和 Mapping 历史；
8. 创建新的 Review Cycle；
9. Task Status → `waiting_for_review`。

若下游尚未生成，只影响 Review 和 Approved Strategy。若下游已经生成，遵循 DEC-009：`Approved Strategy 修改或撤回 → Marketing Brief invalid → Xiaohongshu Mapping invalid`。

---

## §15 Review History and Audit

系统必须保留：原始 Positioning Candidates / Model Recommendation / 用户选择 / 用户编辑 / Merge 来源 / 被拒绝候选 / Hypothesis Decisions / Proof Point Decisions / Evidence Limitation Decisions / Request More Information / Draft Revisions / Submission / Approved Strategy Versions / Withdrawal / 审核时间 / 用户备注 / 失败校验记录。

审核历史用于：业务审计 / 人机协作分析 / 模型质量评估 / Prompt 回归 / 用户修改量统计 / 决策复盘 / Approved Strategy 版本追踪。

---

## §16 Review Status

概念状态（**最终状态名称尚未确认，但必须覆盖以下语义**）：

| 状态 | 含义 |
|------|------|
| `not_ready` | 上游尚未生成可审核 Positioning Candidates |
| `pending` | Review Package 已创建，等待用户开始 |
| `in_progress` | 用户正在审核或已经保存 Draft |
| `changes_requested` | 用户要求补充资料或重新生成 |
| `submitted` | 用户已经提交，系统正在执行事务处理 |
| `approved` | Approved Strategy Version 已成功创建 |
| `superseded` | 上游版本变化导致当前 Review Package 或 Review 失效 |
| `withdrawn` | 用户撤回已经批准的 Strategy |
| `cancelled` | 用户取消本次 Review Cycle |

---

## §17 Deterministic Validator

Approved Strategy 创建前，至少检查 **25 项**：

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
23. Draft Revision 未过期；
24. 提交满足幂等要求；
25. Approved Strategy 尚未被重复创建。

---

## §18 Responsibility Boundary

### 18.1 LLM

允许：解释候选差异 / 辅助润色用户编辑 / 检查 Strategy Draft 表述一致性 / 提示可能遗漏的假设 / 提示可能遗漏的风险 / 帮助总结用户修改。

禁止：自动选择候选 / 自动接受 Hypothesis / 自动删除 Evidence Limitation / 自动批准 Strategy / 自动提交 Review / 将无证据内容升级为 Proof Point / 绕过确定性 Validator。

### 18.2 Deterministic Logic

负责：Package Version / Upstream Version Validation / Schema / Evidence Link / Proof Point Validation / Hypothesis Status / Evidence Limitation Preservation / Idempotency / Concurrency / Transaction / Current Truth Pointer / Workflow Status / Downstream Invalidation / Audit Record。

### 18.3 Human

负责：Select / Edit / Merge / Reject / Request More Information / 接受·测试·拒绝 Hypothesis / 处理 Proof Points / 接受 Evidence Limitations / Submit / Withdraw / 最终战略决策。

---

## §19 Evaluation Metrics

### 19.1 Hard Reliability Metrics（MVP 目标全部 = 0%）

```text
Approved Strategy Without Review Rate = 0%
Unsupported Proof Point Approval Rate = 0%
Stale Review Submission Success Rate = 0%
Duplicate Approved Version Rate = 0%
Unresolved Critical Hypothesis Rate = 0%
Silent Evidence Limitation Removal Rate = 0%
```

### 19.2 User Efficiency Metrics

打开 Review 到提交的时间 / 用户修改字段数量 / 直接选择候选比例 / Merge 使用率 / Request More Information 比例 / 全部候选拒绝率 / Review Withdrawal Rate / Draft Resume Success Rate。

### 19.3 Human-AI Collaboration Metrics

Model Recommendation 被选择比例 / 推荐候选的用户修改量 / 用户删除的 Proof Point 数量 / 用户拒绝的 Hypothesis 数量 / Approved Strategy 与原 Positioning Candidate 的差异程度 / 人工修改后策略质量提升程度。

---

## §20 Test Scenarios

| 场景 | 预期 |
|------|------|
| **Direct Candidate Selection** | 用户选择一个候选 → 处理 Hypotheses → 确认 Evidence Limitations → 创建 Approved Strategy → Marketing Brief Stage → ready |
| **Merge Candidates** | 形成新 Strategy Draft → 保存 Merge 来源 → 重新校验 Proof Points → Validator 通过后才允许提交 |
| **Upstream Changes During Review** | 原 Review Package → superseded → 旧提交被拒绝 → 创建新 Review Package → 不自动迁移旧审批 |
| **Duplicate Submission** | 只创建一个 Approved Strategy Version → 重复请求返回相同结果 |
| **Unsupported User-added Proof Point** | Validator 拒绝 → 可降级为 Business Assumption → 不允许进入正式 Proof Points |
| **Withdraw Approved Strategy** | 保留历史 Strategy → 当前 Strategy Pointer 清除 → Brief 与 Mapping 失效 → 创建新 Review Cycle |
| **Save Draft and Resume** | Draft 可恢复 → 不改变 Current Truth → 不推进下游工作流 |

> 以上为**概念测试场景，非最终 Golden Dataset**；最终测试数据、阈值与评价实现未确认。

---

## §21 Contract Summary

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
- Select / Edit / Merge / Reject
- Request More Information
- Save Draft / Submit / Withdraw

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

## §22 Open Questions（记录而非虚构）

最终 Review / Approved Strategy 公共 Schema、字段名、类型与逐字段必填表达 / Review UI / Draft 自动保存频率 / Patch 或完整 Snapshot 策略 / revision 的传输和数据库并发实现 / 数据库事务实现 / LangGraph Interrupt Payload / API / 审核权限 / 多人协作审核 / 电子签名 / 审批链 / Review Status 最终枚举名 / Review Actions 最终字段 / Hypothesis Decision 最终字段 / Proof Point Decision 最终字段 / Evidence Limitation Decision 最终字段 / Audit Record 最终 Schema / Withdrawal Record 最终 Schema / 具体错误代码 / Golden Dataset 最终数据与阈值。

---

## §23 Out-of-Scope（当前不创建）

- Review UI；
- LangGraph Interrupt 代码；
- Resume 代码；
- 数据库表；
- API；
- 并发锁实现；
- Transaction 代码；
- Draft 自动保存代码；
- Approved Strategy Service 代码。

**当前不选择**：前端框架 / 数据库 / 并发控制技术 / Draft 存储方案 / API 框架 / 权限系统 / 多人审批系统。

**当前不创建 RFC。**

**保持 Development Status: NOT READY。**

> 在 **Marketing Brief Generation Skill Contract** 确认前，**不**创建正式 Brief Prompt 或生成代码。
