# DEC-012：Workflow State 采用阶段状态与关键条目结构化设计

## Type

Architecture

## Status

Accepted

## Decision

AI Ecommerce Agent 的 MVP Workflow State 采用两层状态结构：

```
阶段级状态
+
关键业务条目结构
```

阶段级状态用于控制：

- 当前流程位置；
- 阶段有效性；
- 暂停与恢复；
- 人工审核；
- 异常处理；
- 阶段级失效；
- 局部重跑范围。

关键业务条目结构用于保存：

- 事实；
- 洞察；
- 模型推断；
- 待验证假设；
- 资料不足；
- 策略；
- 执行 Brief；
- 来源和主要依据；
- 用户修改和审核结果。

MVP **不以单一 Markdown 文本或单一聊天记录作为完整工作流状态**。

MVP **暂不实现**精细的字段级依赖图或完整知识图谱。

## State Structure

Workflow State 至少分为以下六组。

### 1. Task and Workflow State

用于保存任务运行状态，例如：

```
task_id
current_stage
workflow_status
review_status
pause_reason
rerun_from_stage
created_at
updated_at
```

该状态应由确定性程序维护。它需要能够回答：

- 当前任务运行到哪个阶段；
- 当前是否等待用户审核；
- 当前是否因为异常而暂停；
- 暂停原因是什么；
- 用户操作后应从哪个阶段继续；
- 哪些阶段仍然有效；
- 哪些阶段需要重新生成。

> 具体字段名称和枚举值尚未最终确定。

### 2. Raw Input State

用于保存用户原始输入，例如：

```
raw_product_input
promotion_goal
uploaded_sources
optional_materials
```

原则：

- 原始输入**不能**被模型生成结果覆盖；
- 用户后续修改应保留明确的更新状态；
- AI 解析结果与用户原始内容**必须分开保存**。

> 具体文件保存方式和数据存储方式尚未确定。

### 3. Parsed Sources and Evidence State

用于保存已经解析的资料和来源关系，例如：

```
sources
source_fragments
parsed_documents
extraction_errors
missing_information
detected_conflicts
```

每个来源至少需要具备可以唯一识别和追踪的**来源标识**。

高层来源信息可能包括：

```
source_id
source_type
source_name
original_content_or_reference
```

来源片段可能进一步具有：

```
fragment_id
source_id
content
location
```

> 以上只是概念字段，**不是最终数据契约**。

### 4. Four-layer Business State

四层业务结果分别保存：

```
facts
insights
strategies
execution_brief
```

四层结果**不能**只保存为一段不可拆分的自由文本。

关键条目至少需要表达：

```
item_id
content
evidence_type
source_refs
status
generated_by
user_modified
```

可能还需要表达：

- 主要依据；
- 审核状态；
- 用户修改内容；
- 创建时间；
- 最后更新时间；
- 是否有效；
- 是否需要重新生成。

> 具体字段契约后续确定。

### 5. Human Review State

用于保存人工审核和修改，例如：

```
review_comments
user_edits
accepted_items
rejected_items
confirmed_assumptions
reviewed_at
```

该状态需要区分：

- AI 初始候选结果；
- 用户修改后的版本；
- 用户明确接受的条目；
- 用户明确否定的条目；
- 尚未审核的条目；
- 需要重新生成的条目。

> 具体是保存完整版本、差异记录还是最终值，尚未确定。

### 6. Invalidation and Runtime State

用于保存阶段有效性与运行过程，例如：

```
stage_validity
invalidated_stages
invalidation_reason
run_history
generation_attempts
stage_timings
errors
```

例如，用户修改事实层的重要内容后：

```
facts: valid
insights: invalid
strategies: invalid
execution_brief: invalid
rerun_from_stage: insights
```

系统**不得**继续将失效阶段的内容作为当前有效输出。

## Stage-level State

MVP 至少管理以下业务阶段：

```
input
source_processing
facts
insights
strategies
human_review
execution_brief
completed
```

> 这只是高层业务阶段示意，**不代表最终工作流节点已经确认**。一个业务阶段未来可以：对应一个节点；包含多个节点；包含确定性处理和 LLM 处理；被拆分成若干子步骤。

> **不得**在本次归档中将业务阶段直接等同于最终技术节点。

## Structured Item Principle

事实、洞察、策略和执行内容应以**结构化条目**为基本单位。示意：

```
item_id: fact-001
content: 商品重量为 320g
evidence_type: explicit_fact
source_refs:
  - source-002-fragment-014
status: pending_review
generated_by: llm
user_modified: false
```

> 该示例仅用于表达结构原则，**不是最终 Schema**。

结构化条目需要支持：

- 单条审核；
- 来源关联；
- 证据类型标记；
- 用户修改；
- 状态有效性判断；
- 后续结构化输出；
- 测试和评价。

## Stage-level Invalidation Principle

MVP 仍然按照 DEC-009 管理依赖：

```
事实层修改 → 洞察、策略和执行层失效
洞察层修改 → 策略和执行层失效
策略层修改 → 执行层失效
```

Workflow State 需要显式保存这种阶段有效性。

MVP **不要求**维护：

```
fact-001 → insight-003 → strategy-002 → brief-item-007
```

这类完整字段级依赖图。

> 关键结论可以保留主要依据，但局部重跑的**控制单位仍然是阶段**。

## Current-state Principle

系统需要区分：

- 原始输入；
- AI 候选结果；
- 当前有效结果；
- 用户确认结果；
- 已失效结果；
- 历史运行记录。

旧结果可以被保留用于审计或调试，但**不得**与当前有效结果混淆。

> 是否在 MVP 用户界面中提供完整版本历史，尚未确定。

## State Is Not Chat History

Workflow State **不等于**：

- 用户和 Agent 的聊天记录；
- 一段完整 Prompt；
- 一段最终 Markdown 报告；
- LLM 上下文窗口中的临时信息。

聊天记录可以作为附加上下文，但**不能**成为以下能力的唯一依据：

- 审核恢复；
- 阶段失效；
- 来源追溯；
- 局部重跑；
- 状态一致性；
- 验收与评估。

## Reason

如果只保存最终文本，系统将难以可靠支持：

- 事实与推断分离；
- 来源关系；
- 单条内容审核；
- 用户修改；
- 状态失效；
- 局部重跑；
- 暂停后恢复；
- 评价指标；
- 自动化测试。

如果首版直接实现完整字段级依赖图，又会增加：

- 数据结构复杂度；
- 依赖维护成本；
- 生成逻辑复杂度；
- 测试范围；
- 用户编辑后的依赖计算；
- MVP 实现时间。

「阶段状态 + 关键条目结构化」可以在可靠性和实现成本之间取得平衡：

- 结构化条目支持来源、审核和修改；
- 阶段状态支持暂停、失效和局部重跑；
- 不需要在 MVP 中维护完整细粒度依赖图。

## Impact

该决定将影响：

- 系统架构；
- 数据架构；
- 工作流框架筛选；
- LangGraph 或其他编排框架评估；
- 状态 Schema；
- 数据库存储；
- Checkpoint；
- 暂停与恢复；
- 人工审核；
- 阶段失效；
- 局部重跑；
- RAG 检索结果保存；
- 来源与证据管理；
- 前端编辑和状态提示；
- 可观测性；
- 测试与验收；
- GitHub 基底仓库筛选。

> 后续技术方案必须能够回答：它如何保存结构化业务条目，并可靠管理阶段状态、人工暂停和局部重跑？

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求（[../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)）

## Related RFC

None

## Supersedes

None

## Amends

None

## Decision Boundary

**本决定已经确认：**

- Workflow State 采用阶段状态与关键条目结构化组合；
- 原始输入和 AI 生成结果分开保存；
- 四层业务结果以结构化条目保存；
- 条目保留证据类型、来源和审核相关信息；
- 工作流显式保存当前阶段和阶段有效性；
- 失效和局部重跑仍以阶段为单位；
- Workflow State 不等于聊天历史；
- MVP 不采用纯文本状态；
- MVP 暂不实现完整字段级依赖图。

**本决定尚未确认：**

- 是否采用 LangGraph State；
- 是否采用 Pydantic；
- 是否采用 JSON Schema；
- 最终字段和数据类型；
- 工作流阶段的最终枚举；
- 技术节点数量；
- 数据库存储方式；
- Checkpoint 实现；
- 是否跨会话持久化；
- 是否保留完整版本历史；
- 来源片段如何保存；
- 状态迁移规则；
- 并发与任务锁；
- 数据隐私和保存期限；
- 具体开源基底仓库。

## Notes

- 用户于 2026-07-27 对该 Workflow State 方案明确回复「确认」，通过 Decision Gate。第二项 Architecture 决定（Type: Architecture，Session-002）。
- 对应 Session-002 Question-002（工作流状态需要保存什么）、Question-004（阶段级失效与局部重跑如何表达）、Question-005（证据和来源关系如何保存）在**原则层**的部分回答。
- **未采用方案（保留为备选 / 暂缓，非永久禁止）：** 纯文本 / 单一 Markdown / 聊天记录作为完整状态（未采用）；完整字段级依赖图（暂缓到后续版本，与 DEC-009 一致）。
- 本决定确认的是**两层状态结构 + 结构化条目原则**；**不构成**对 LangGraph State / Pydantic / JSON Schema / 最终字段与数据类型 / 阶段最终枚举 / 技术节点数量 / 数据库存储 / Checkpoint / 跨会话持久化 / 版本历史 / 来源片段保存方式 / 状态迁移规则 / 并发与任务锁 / 数据隐私与保存期限 / 开源基底仓库的确认（见 Decision Boundary）。文中所有字段名、枚举、Schema 示例均为**概念示意，非最终数据契约**。
- 与 [DEC-008](dec-008-tiered-evidence-and-traceable-conclusions.md)（五类证据标记）、[DEC-009](dec-009-stage-level-invalidation-and-partial-rerun.md)（阶段级失效）、[DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（确定性工作流控制）协同：结构化条目承载五类证据与来源；阶段状态承载失效与重跑；确定性程序维护状态。
- **RFC 判断（暂不创建）：** 当前不创建 RFC；改变核心数据模型属重大议题，后续在比较状态 Schema / 数据库 / Checkpoint 实现方案时，再判断是否建立架构 RFC。
- 已同步至 [../architecture/system-architecture.md](../architecture/system-architecture.md)、[../architecture/data-architecture.md](../architecture/data-architecture.md)、[../agents/README.md](../agents/README.md)。无业务代码；Development Status 仍 NOT READY。
