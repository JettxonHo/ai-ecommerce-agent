# DEC-022：Workflow Framework Capability Requirements

> 本决定记录用户已明确接受的 Architecture 决定（工作流框架能力需求）。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。
> 承接 [DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（确定性工作流控制）、[DEC-012](dec-012-stage-state-and-structured-business-items.md)（结构化 Workflow State）、[DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)（任务级持久化）、[DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（按需混合 RAG）、[DEC-015](dec-015-contract-based-reusable-business-skills.md)（契约化 Skill）、[DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（四个核心 Skills + 一个小红书 Adapter）、[DEC-021](dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)（MVP 不采用 Multi-Agent 主架构）。

## Type

Architecture

## Status

Accepted（2026-07-28，用户对工作流框架能力需求 Proposal 明确回复「确认」，通过 Decision Gate）

## Decision

AI Ecommerce Agent 选择工作流框架时，应**首先**把框架视为**结构化状态和确定性流程的运行时**，而**不是** Multi-Agent 协作框架。候选框架必须能够可靠支持任务级持久化、暂停与跨会话恢复、Human-in-the-loop、阶段失效、局部重跑、节点级输入输出契约、校验、重试、错误恢复和运行追踪。**具体框架仍未选择。**

AI Ecommerce Agent 的工作流框架必须优先满足：

```text
State-first
Deterministic
Persistent
Human-reviewable
Recoverable
Testable
Observable
Model-neutral
Extensible
```

框架的主要职责是：

```text
结构化任务状态
+
确定性流程控制
+
持久化
+
暂停与恢复
+
人工审核
+
阶段失效
+
局部重跑
+
节点级重试
+
错误恢复
+
运行追踪
```

框架**不负责**替代业务 Skill，也**不负责**通过 LLM Supervisor 自由决定主业务流程。

## Framework Responsibility Boundary

### Workflow Framework

负责：

- 当前任务状态；
- 节点执行顺序；
- 条件路由；
- 前置条件；
- 暂停和恢复；
- 人工审核节点；
- 错误状态；
- 节点重试；
- 阶段有效性；
- 局部重跑；
- 持久化；
- 运行历史；
- 进度事件。

### Business Skills

负责：

- 商品事实提取；
- 用户洞察分析；
- 商品定位；
- 营销 Brief 生成。

### LLM

负责：

- 受约束的语义分析；
- 结构化业务判断；
- 候选内容生成。

### Deterministic Validators

负责：

- Schema 校验；
- 引用 ID 校验；
- 必填字段校验；
- 风险规则；
- 阶段有效性检查；
- 量化数据约束；
- 输出写入前验证。

### Database and Storage

负责：

- 任务级持久化；
- 领域状态；
- 来源和证据；
- 运行记录；
- 用户修改；
- 文件和片段；
- 可选向量数据。

### Frontend

负责：

- 用户输入；
- 文件上传；
- 运行进度；
- Human Review；
- 补充资料；
- 状态展示；
- 结果展示。

## Must-have Requirements

### 1. Explicit Structured Workflow State

框架必须支持显式的结构化任务状态。

概念状态至少包括：

```text
task_id
raw_inputs
sources
fact_stage
insight_stage
positioning_stage
review_stage
marketing_brief_stage
xiaohongshu_mapping_stage
runtime_metadata
```

必须满足：

- State 不只由聊天消息组成；
- 原始输入与 AI 输出分离；
- 用户修改与模型生成结果可区分；
- 每个阶段可独立读取和更新；
- 阶段有效性可显式表达；
- 失效结果不能继续被下游使用；
- 状态能够序列化并写入持久化存储；
- 服务或进程重启后仍可恢复。

以下方式**不能**成为正式业务状态模型：

```text
messages[] as the only source of truth
```

### 2. Deterministic Routing

主业务流程由程序和状态规则控制：

```text
Product Intake & Fact Extraction
→ Customer Insight Analysis
→ Product Positioning
→ Human Review
→ Marketing Brief Generation
→ Xiaohongshu Brief Mapping
```

框架必须支持：

- 固定节点；
- 条件分支；
- 前置条件检查；
- 可选节点；
- 错误分支；
- 暂停分支；
- 指定阶段恢复；
- 阶段有效性判断。

**不采用**：

```text
让 Supervisor LLM 自由决定下一步调用哪个 Agent
```

### 3. Pause and Resume

必须支持：

```text
执行
→ 持久化暂停
→ 用户稍后返回
→ 从正确位置恢复
```

暂停和恢复必须：

- 支持跨页面；
- 支持跨会话；
- 支持服务重启；
- 保存暂停原因；
- 接收用户补充资料或修改；
- 不重复执行仍有效的已完成阶段；
- 从正确节点恢复。

可能的暂停原因包括：

```text
missing_required_information
source_unavailable
fact_conflict
pending_human_review
invalid_model_output
risk_requires_confirmation
```

### 4. Human-in-the-loop

框架必须能够在指定阶段：

- 暂停工作流；
- 保存当前状态；
- 返回结构化审核材料；
- 接收用户接受、修改或拒绝；
- 保存用户操作记录；
- 将修改回写 Domain State；
- 触发对应下游失效；
- 审核完成后继续执行。

Human Review **不只是**整体 Approve / Reject。需要支持：

- 修改商品事实；
- 删除或修改洞察；
- 选择定位候选；
- 调整卖点优先级；
- 补充来源；
- 标记假设需要验证。

### 5. Stage Invalidation and Partial Rerun

框架必须实现 [DEC-009](dec-009-stage-level-invalidation-and-partial-rerun.md) 已确认的阶段级失效规则。

```text
Fact 修改
→ Insight、Positioning、Brief、Platform Mapping 失效
Insight 修改
→ Positioning、Brief、Platform Mapping 失效
Positioning 修改
→ Brief、Platform Mapping 失效
最终 Brief 修改
→ 不要求上游重跑
```

必须支持：

- 显式标记失效阶段；
- 保存旧输出供追踪或查看；
- 阻止失效数据进入后续执行；
- 定位最早失效阶段；
- 只重跑需要重跑的阶段；
- 保留仍然有效的上游结果。

框架**不能只能**：

```text
从头重新 kickoff
```

### 6. Node-level Contracts

每个节点或 Skill 必须有明确的：

```text
Input Schema
Output Schema
Preconditions
Validation Rules
Failure Conditions
Retry Rules
```

框架必须支持或容易接入：

- JSON Schema；
- Pydantic 或同等级类型系统；
- Enum；
- 必填字段；
- 自定义 Validator；
- Structured Output；
- 引用 ID 校验；
- 输出修复；
- 输出重试。

**未经验证的 LLM 输出不得直接写入正式 Workflow State。**

### 7. Node-level Retry and Error Recovery

框架必须区分：

**可以自动重试的错误：**

- 临时网络失败；
- 模型超时；
- API 限流；
- 临时检索服务故障；
- JSON 或 Schema 输出失败。

**不应盲目自动重试的错误：**

- 缺少关键商品资料；
- 事实冲突；
- 来源不存在；
- 资质缺失；
- 用户请求高风险或无依据表达；
- 上游阶段失效。

框架必须支持：

- 节点级重试；
- 最大次数；
- Backoff；
- 错误分类；
- 失败状态保存；
- 从失败节点恢复；
- 人工处理后继续。

### 8. Task-level Persistence

一个业务任务必须拥有稳定的：

```text
task_id
```

至少持久化：

- 原始输入；
- 来源；
- 事实；
- 洞察；
- 定位；
- Marketing Brief；
- Platform Mapping；
- 阶段状态；
- 用户修改；
- 审核记录；
- 当前执行位置；
- 错误；
- 重试记录；
- Skill 版本；
- Prompt 版本；
- 模型配置；
- 运行历史。

框架可以提供 Checkpointer，也可以连接项目自己的数据库。但**不得依赖**：

```text
进程内存是任务恢复的唯一基础
```

### 9. Idempotency and Concurrency Protection

系统必须能够避免：

- 重复点击产生重复正式结果；
- 网络重发重复执行节点；
- 多标签页修改相互覆盖；
- 相同阶段并行写入；
- 重试生成重复业务条目。

需要允许实现：

- Node Run ID；
- Stage Run ID；
- 幂等键；
- 乐观锁或等效并发控制；
- 可安全重复执行的节点；
- 外部工具调用记录；
- 当前正式版本标记。

### 10. Observability

系统至少需要记录：

- 节点开始；
- 节点完成；
- 节点失败；
- 节点暂停；
- 使用模型；
- Token 使用；
- 节点耗时；
- 检索查询；
- 召回片段；
- Validator 结果；
- 重试；
- 错误原因；
- State 变更；
- 用户审核操作；
- Prompt、Schema 和 Skill 版本。

系统应能够解释：

> 一个定位或营销卖点如何从来源、事实和洞察进入最终 Brief。

## Should-have Requirements

### 1. Domain State Independent from Framework State

项目领域模型应独立于具体框架。例如：

```text
ProductFact
CustomerInsight
PositioningCandidate
MarketingBrief
SourceFragment
```

**不应只能**存在于某个框架的：

- Message；
- Checkpoint；
- Agent Memory；
- Runtime-specific Object。

目标是：

> 更换工作流框架时，不需要重写全部业务数据模型。

### 2. Independent Node Testing

每个 Skill 节点应能够独立测试：

```text
固定输入
→ 单独执行 Skill
→ 校验结构化输出
```

需要支持：

- Unit Test；
- Golden Test；
- Mock LLM；
- Mock Retrieval；
- 固定模型输出；
- Validator Test；
- Node Regression；
- Full Workflow Integration Test。

### 3. Skill Logic Decoupled from Workflow Runtime

推荐结构：

```text
Workflow Node Adapter
→ Business Skill Service
→ LLM / Retrieval / Validator
```

业务逻辑**不应**大量写入框架专属 Node API。

### 4. Node-specific Model and Tool Configuration

每个节点最好可独立设置：

- 模型；
- Temperature；
- Timeout；
- Token Limit；
- 工具权限；
- RAG 策略；
- 重试策略；
- Structured Output；
- Validator。

模型和工具配置属于**项目配置层**，**不应**被工作流框架硬编码。

### 5. Async and Long-running Execution

框架最好支持：

- 异步节点；
- 长耗时文件处理；
- 长耗时 LLM 调用；
- Embedding；
- 后台运行状态；
- 前端查询进度；
- 超时；
- 服务重启恢复。

首版**不强制**使用复杂分布式队列，但框架**不能阻止**后续接入。

### 6. Business Progress Events

框架最好能够输出：

```text
Node Started
Node Completed
Node Failed
Paused
Waiting for Review
Retrying
Completed
```

用户看到的是**业务阶段进度**，不要求暴露完整 Token 流。

### 7. Version Metadata

运行记录最好保存：

- Skill Version；
- Prompt Version；
- Schema Version；
- Model Version；
- Retrieval Configuration；
- Validator Version。

### 8. Future Bounded Worker Extension

未来允许在特定节点内部加入：

```text
Centralized Local Orchestrator
+
Bounded Parallel Workers
+
Structured Aggregation
```

但 Worker：

- 不控制主流程；
- 不直接修改最终 Workflow State；
- 不自行确认业务结论；
- 返回结构化结果；
- 可独立失败和重试。

这属于**次要扩展能力**，**不是** MVP 选择框架的首要因素。

## Could-have Requirements

以下能力可以加分，但**不是**框架选择的主要标准：

- 内置 Graph 可视化；
- 内置 Prompt 管理；
- 内置 LLM Judge；
- 分布式 Worker Runtime；
- 云端执行面板；
- 自动数据集评测；
- 内置人工审核 UI；
- 内置 Agent Marketplace。

## Anti-requirements

MVP **不要求**：

- Supervisor-led Multi-Agent；
- 多自治业务 Agent；
- Agent-to-Agent Messaging；
- LLM 动态控制主业务流程；
- 无限循环式 Agent；
- 自由规划整条业务链；
- Chat History 作为唯一正式业务状态；
- 自动平台发布；
- 多 Agent 讨论和投票；
- 强制绑定某一家模型供应商。

框架的 Multi-Agent 能力**不能单独**成为选择它的理由。

## Framework Evaluation Dimensions

后续候选框架采用 **100 分制**评估。

| Dimension                        | Weight |
| -------------------------------- | -----: |
| Structured State                 |     15 |
| Persistence and Recovery         |     15 |
| Human-in-the-loop                |     12 |
| Deterministic Routing            |     10 |
| Partial Rerun and Invalidation   |     10 |
| Structured Output and Validation |      8 |
| Testing and Debugging            |      8 |
| Observability                    |      6 |
| Framework Independence           |      5 |
| Development Complexity           |      5 |
| Async and Long-running Tasks     |      3 |
| Future Bounded Workers           |      3 |
| Total                            |    100 |

### Elimination Criteria

**无论评分多高**，存在以下任一问题时，可以直接淘汰：

- 无法可靠持久化和恢复；
- Human Review 只能依靠进程内存；
- 无法稳定实现确定性主流程；
- 业务状态只能存储为聊天历史；
- 很难实现阶段失效与局部重跑；
- 强绑定单一模型供应商；
- 单节点难以独立测试；
- 框架复杂度明显超过当前 MVP 收益。

## Reason

项目的核心任务是强顺序依赖的有状态业务流程：

```text
Facts
→ Insights
→ Positioning
→ Human Review
→ Marketing Brief
→ Platform Mapping
```

项目当前最重要的能力是：状态一致性；来源可追溯；人工审核；可恢复性；局部重跑；可测试性。

因此工作流框架应优先被评估为：

> 有状态、确定性、可持久化的业务工作流运行时。

而**不是**被评估为：

> 能够让多个自治 Agent 自由协作的框架。

## Impact

该决定将直接影响：工作流框架调研；LangGraph 评估；OpenAI Agents SDK 评估；自研状态机评估；其他候选框架评估；Workflow State；数据库；Human Review；错误恢复；Testing；Observability；前后端接口；项目部署；后续局部 Worker 扩展。

后续候选框架**必须**按照本决定中的需求和淘汰条件进行评估，**不得仅依据**：

- 流行程度；
- GitHub Star；
- Multi-Agent Demo；
- 单一厂商宣传；
- 开发者个人偏好。

## Decision Boundary

**本决定已经确认：**

- 工作流框架首先是状态和流程运行时；
- Structured State 是强制要求；
- 确定性路由是强制要求；
- Task-level Persistence 是强制要求；
- Pause and Resume 是强制要求；
- Human Review 回写是强制要求；
- 阶段失效和局部重跑是强制要求；
- 节点级 Schema、Validator、重试和错误恢复是强制要求；
- 幂等、并发保护和任务级可观测性属于必要能力；
- Domain State 应尽量独立于框架；
- 单节点必须易于独立测试；
- Multi-Agent 和 Supervisor 不是 MVP 需求；
- 未来受约束 Worker 是次要扩展要求；
- 候选框架使用统一评分维度和淘汰条件。

**本决定尚未确认：**

- 具体工作流框架；
- LangGraph；
- OpenAI Agents SDK；
- 自研状态机；
- Temporal；
- LangChain；
- 编程语言；
- 数据库；
- Checkpointer；
- 任务队列；
- Observability 产品；
- 部署方式；
- 前后端技术栈。

> 本决定**不**确认具体工作流框架、LangGraph、OpenAI Agents SDK、LangChain、CrewAI、Temporal、自研状态机、编程语言、数据库、Checkpointer、任务队列、Observability 产品、部署方式、前后端技术栈。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求（对应议题：Workflow Framework Capability Requirements）

## Related Decisions

- [DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（确定性工作流与受约束 LLM 节点）
- [DEC-012](dec-012-stage-state-and-structured-business-items.md)（结构化 Workflow State）
- [DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)（任务级持久化）
- [DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（按需混合 RAG）
- [DEC-015](dec-015-contract-based-reusable-business-skills.md)（契约化 Skill）
- [DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（四个核心 Skills 与一个小红书 Adapter）
- [DEC-021](dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)（MVP 不采用 Multi-Agent 主架构）

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 本决定**不选择**任何具体工作流框架；LangGraph / OpenAI Agents SDK / LangChain / CrewAI / Temporal / 自研状态机**均未确认、未选择**。
- 本决定**不创建**候选框架评估结论、不创建 RFC、不创建业务代码。
- 工作流框架的 Must-have（1–10）/ Should-have（1–8）/ Could-have / Anti-requirements、100 分制评分维度与淘汰条件，构成后续候选框架调研与比较的**统一标准**；候选框架必须同时通过淘汰条件，并按评分维度打分。
- 本决定**不**改变 DEC-021 的 Agent 架构形态结论（统一 Agent + 确定性编排 + 契约化 Skill，不采用 Multi-Agent 主架构）；它是 DEC-021 的**下一步技术前提**：在已确认不采用 Multi-Agent 后，明确「用什么标准评估承载该确定性工作流的运行时」。
- 下一议题（**尚未开始，需用户明确启动**）：`Workflow Framework Candidate Research and Comparison`。候选至少应包括 LangGraph / 自研显式状态机 / OpenAI Agents SDK，必要时补充其他符合需求的候选；调研顺序为「确认候选范围 → 阅读官方文档 → 按 DEC-022 评分 → 分析淘汰条件 → 给出 Recommendation → 用户确认后才形成框架选择 Decision」。在该议题得出 Recommendation 且用户确认前，**不**形成框架选择 Decision。
- 本决定保持 Development Status：`NOT READY`。
