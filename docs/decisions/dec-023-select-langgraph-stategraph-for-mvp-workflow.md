# DEC-023：MVP 选择 LangGraph StateGraph 作为核心工作流运行方式

> **Type:** Architecture
> **Status:** Accepted
> **Date:** 2026-07-28
> **Related Session:** [Session-002 — Agent 工作流、可靠性架构与技术能力需求](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
> **Related Research:** [Workflow Framework Candidate Research and Comparison](../research/workflow-framework-candidate-comparison.md)
> **Related RFC:** None
> **Supersedes:** None
> **Amends:** None

---

## 用户确认

用户明确回复：

> 确认通过，可将完整结论归档为 DEC-023

被接受的完整结论是：

> AI Ecommerce Agent 的 MVP 选择 LangGraph 作为工作流运行框架，并使用 LangGraph Graph API 中的 StateGraph 作为核心业务流程的主要建模方式。StateGraph 不是独立于 LangGraph 的另一套框架，而是 LangGraph 中用于声明结构化 State、Nodes、Edges 和 Conditional Edges 的核心工作流 Builder。
>
> 项目不采用高层 ReAct Agent、LLM Supervisor 或多个自治 Agent 来控制主业务流程。LangGraph 仅负责工作流编排、Checkpoint、Interrupt、Resume、节点重试和执行恢复。项目的 Domain State、Skill Services、Validators、Repositories 和正式业务数据库必须保持相对独立，避免业务逻辑与 LangGraph Runtime 深度绑定。
>
> 实现正式业务流程前，必须先完成一个最小 Technical Spike，验证持久化恢复、人工审核、结构化状态修改、阶段失效、局部重跑、节点级重试、幂等和单节点测试。

---

## Decision

AI Ecommerce Agent 的 MVP 正式选择：

```text
Workflow Framework:
LangGraph

Primary Workflow Modeling API:
StateGraph / Graph API
```

项目核心工作流将使用：

```text
State
+
Nodes
+
Edges
+
Conditional Edges
+
Checkpoint
+
Interrupt / Resume
```

表达。

概念主流程为：

```text
START
↓
Product Intake & Fact Extraction
↓
Customer Insight Analysis
↓
Product Positioning
↓
Prepare Human Review
↓
Human Review Interrupt
↓
Apply Review Decision
↓
Marketing Brief Generation
↓
Xiaohongshu Brief Mapping
↓
END
```

具体节点数量和最终图结构仍需在 Workflow State 与 Skill Contract 设计完成后确定。

---

## Relationship between LangGraph and StateGraph

必须在项目文档中明确：

```text
LangGraph
├── Graph API
│   └── StateGraph
│       └── compile()
│           └── CompiledStateGraph
│
└── Functional API
    ├── entrypoint
    └── task
```

其中：

- LangGraph 是整体有状态工作流运行框架；
- StateGraph 是 Graph API 中用于构建状态图的 Builder；
- StateGraph 本身需要编译后才能执行；
- 编译后的 Graph 负责实际节点运行、状态更新、Checkpoint、Interrupt 和恢复；
- Functional API 是同一 LangGraph Runtime 上的另一种表达方式；
- **StateGraph 不是 LangGraph 的竞品或替代方案。**

因此项目选择不是：

```text
LangGraph vs StateGraph
```

而是：

```text
使用 LangGraph
+
以 StateGraph / Graph API 构建主业务流程
```

---

## Why StateGraph Is Selected

### 1. State-first Architecture

项目的核心控制对象是结构化任务状态，而不是聊天历史。需要管理：

- 当前有效商品事实；
- 当前有效用户洞察；
- 商品定位候选；
- 人工审核状态；
- 营销 Brief；
- 小红书映射；
- 来源；
- 阶段有效性；
- 暂停原因；
- 运行状态；
- 用户修改；
- 下游失效。

StateGraph 允许节点读取共享结构化 State，并返回明确的 Partial State Update。这与以下已确认决定一致：

- DEC-012：结构化 Workflow State；
- DEC-013：任务级持久化；
- DEC-022：工作流框架以 State 为中心。

正式业务状态不能只保存为：

```text
messages[]
```

聊天消息可以作为交互上下文，但不能成为业务 Current Truth 的唯一来源。

### 2. Explicit Deterministic Workflow

当前业务流程具有明确顺序：

```text
Facts
→ Insights
→ Positioning
→ Human Review
→ Marketing Brief
→ Xiaohongshu Mapping
```

StateGraph 可以显式定义：

- 固定节点；
- 固定边；
- 条件路由；
- 暂停节点；
- 错误分支；
- 重试路径；
- 从最早失效阶段继续执行。

主流程不得由 LLM Supervisor 自由决定。

### 3. Human-in-the-loop

项目需要的人工审核包括：

- 修改商品事实；
- 接受、修改或拒绝洞察；
- 选择定位候选；
- 修改定位；
- 调整卖点优先级；
- 补充资料；
- 触发下游失效。

StateGraph 的 Interrupt / Resume 模型适合实现：

```text
准备审核材料
→ 持久化暂停
→ 前端展示审核内容
→ 用户提交结构化审核决定
→ 回写 Domain State
→ 根据修改内容使下游失效
→ 从正确阶段恢复
```

审核不能只实现为工具调用的 Approve / Reject。

### 4. Persistence and Recovery

LangGraph Checkpointer 用于保存工作流执行状态和 Checkpoint。它主要负责：

- 当前执行位置；
- 图状态快照；
- 中断；
- 恢复；
- 节点失败后的继续执行；
- 执行历史；
- 可选 Replay。

它支持项目需要的：

- 跨页面恢复；
- 跨会话恢复；
- 服务重启后恢复；
- 从失败节点恢复；
- 不重复运行仍有效阶段。

### 5. Stage Invalidation and Partial Rerun

StateGraph 适合根据 Domain State 中的阶段有效性，路由到最早需要重跑的阶段。已确认规则包括：

```text
修改 Fact
→ Insight、Positioning、Brief、Platform Mapping 失效

修改 Insight
→ Positioning、Brief、Platform Mapping 失效

修改 Positioning
→ Brief、Platform Mapping 失效

修改最终 Brief
→ 不要求上游重跑
```

必须明确区分：

```text
Domain Layer
决定什么结果已经失效

StateGraph
根据失效状态决定从哪里继续
```

LangGraph Checkpoint、Replay 或 Time Travel 不能替代项目自己的业务失效规则。

### 6. Testing and Observability

StateGraph 主流程应允许：

- 单独调用节点；
- 使用固定 State 测试条件路由；
- Mock Skill Service；
- Mock LLM；
- Mock Retrieval；
- 测试 Interrupt；
- 测试 Resume；
- 测试节点失败；
- 测试从指定阶段恢复；
- 测试下游失效与局部重跑；
- 测试完整工作流。

运行轨迹需要记录：

- 节点开始与结束；
- State 版本；
- Checkpoint；
- 模型；
- Token；
- 检索；
- Validator；
- 重试；
- 错误；
- 审核动作；
- 状态变更。

### 7. Future Bounded Workers

未来在某个复杂节点内部，可以加入受约束并行 Worker，例如：

```text
Customer Insight Node
├── Current Product Review Worker
├── Competitor A Review Worker
└── Competitor B Review Worker
```

Worker 返回结构化临时结果，由主节点聚合。这不改变：

- 主工作流由 StateGraph 确定性控制；
- Worker 不控制主流程；
- Worker 不直接修改最终 Workflow State；
- 项目不采用 Supervisor-led Multi-Agent 主架构。

---

## StateGraph vs Functional API

LangGraph 的 Graph API 与 Functional API 共用底层 Runtime，但主项目采用不同定位。

### StateGraph / Graph API

主要用于核心业务工作流。

**优势：**

- State 显式；
- 节点显式；
- 边和条件路由显式；
- 审核节点显式；
- 阶段失效路径容易表达；
- 适合可视化；
- 适合团队共同理解；
- 适合作品集架构展示；
- 适合未来局部并行与汇合。

**缺点：**

- 代码量更多；
- 学习成本更高；
- Reducer 需要谨慎设计；
- Graph 过度拆分时可能复杂；
- 容易产生框架耦合。

### Functional API

可以用于局部、简单、顺序明确的任务或技术辅助流程。

**优势：**

- 更接近普通 Python；
- 代码较少；
- 适合改造已有函数；
- 简单任务容易理解。

**限制：**

- 主业务阶段与条件路由不够直观；
- 状态变化更容易隐藏在函数内部；
- 阶段失效与局部重跑需要更多自定义组织；
- 不如 Graph API 适合作为核心流程的统一架构表达。

### Accepted Boundary

```text
Core Business Workflow:
StateGraph / Graph API

Optional Simple Local Tasks:
Functional API may be used when appropriate
```

Functional API **不**作为核心业务流程的主要表达方式。

---

## StateGraph vs Prebuilt Agent

项目**不**使用预构建 ReAct Agent 控制主业务流程。预构建 Agent 更适合：

- 开放式工具使用；
- 动态研究；
- 不确定步骤；
- 模型自行选择工具；
- 迭代直到完成。

当前核心流程已经确定，不需要模型自由规划。

允许的未来结构是：

```text
StateGraph Main Workflow
↓
Selected Research Node
↓
Optional Internal Research Agent
↓
Structured Result
↓
Return to StateGraph
```

内部 Agent 只能作为局部能力，不能取代主 Workflow Controller。

---

## Architecture Boundaries

### LangGraph Layer

负责：

- 图定义；
- 节点编排；
- 条件路由；
- Checkpoint；
- Interrupt；
- Resume；
- 节点运行；
- 节点重试；
- 执行恢复；
- 业务进度事件。

### Node Adapter Layer

负责：

- 将 LangGraph State 转换为 Skill Input；
- 调用 Skill Service；
- 将 Skill Output 转换为 State Update；
- 处理框架相关配置；
- 调用框架级 Retry 和 Interrupt。

Node Adapter **不应**包含大量业务逻辑。

### Skill Service Layer

负责：

- 业务目标；
- 输入契约；
- LLM 调用；
- Retrieval；
- 业务分析；
- 输出契约；
- Validator；
- 失败条件；
- 评价逻辑。

Skill Service 应能够脱离 LangGraph 单独执行和测试。

### Domain Layer

负责定义：

- ProductFact；
- CustomerInsight；
- PositioningCandidate；
- MarketingBrief；
- XiaohongshuBrief；
- SourceReference；
- ReviewDecision；
- StageStatus；
- Invalidation Rules；
- Domain Errors。

Domain Model **不应**继承或依赖 LangGraph 专属类型。

### Persistence Layer

分为：

```text
LangGraph Checkpointer
→ 执行恢复、图状态快照、Interrupt 和 Resume

Business Database
→ 正式业务 Current Truth、来源、用户修改、当前有效版本和审计记录

Object Storage
→ 原始文件

Retrieval Index
→ 搜索、Embedding 和证据召回
```

**不得**把 LangGraph Checkpoint 数据库作为整个产品唯一的业务数据库。

---

## State and Reducer Rules

Reducer 需要在 Technical Spike 与正式 State Specification 中谨慎设计。暂定原则：

### Stage Main Results

例如：facts；insights；positioning candidates；marketing brief。

默认采用：

- 整体替换；
- 显式版本更新；
- 通过业务 Repository 幂等写入。

**不**默认自动 Append。

### Runtime Events

例如：node_started；node_completed；retry；error。

可以采用 Append-only。

### Parallel Worker Results

只在未来局部并行场景中使用明确 Reducer 聚合。

### User-edited Results

用户修改必须明确覆盖或创建新业务版本，不能因 Reducer 自动追加而同时保留多个「当前有效值」。

> 具体状态字段和 Reducer 规则尚未确认（见 Decision Boundary）。

---

## Interrupt Safety Rules

LangGraph 从 Interrupt 恢复时，包含 Interrupt 的节点可能从开头重新执行。因此：

- Interrupt 前的操作必须幂等；
- 不可逆操作不能放在 Interrupt 前；
- 写入操作需要幂等键；
- 审核准备与审核决定应用应尽量拆分；
- 自动发布、收费、外部平台写入不得位于可重放的审核准备代码中。

推荐审核结构：

```text
Prepare Review Package Node
↓
Human Review Interrupt Node
↓
Apply Review Decision Node
```

**不应**在 Interrupt Node 中混合大量外部副作用。

---

## Graph Complexity Control

核心 Graph 应保持为少量大的业务阶段，而不是把所有细节都建成节点。

**Graph 负责：** 大阶段；关键路由；人工审核；错误恢复；暂停；阶段恢复。

**Skill Service 负责：** 阶段内部业务逻辑；Prompt；Retrieval；业务分类；数据整理；内部校验。

**Validator 负责：** Schema；ID；来源；风险；阶段前置条件。

**不应**为每一个：缺失字段；风险词；评论主题；Prompt 步骤；内部转换；单独创建 Graph Node。

---

## Framework Lock-in Protection

为避免 LangGraph 深度绑定，必须遵守：

```text
LangGraph Node Adapter
↓
Framework-independent Skill Service
↓
Domain Models / Repositories / LLM Gateway
```

**禁止：**

- Domain Model 继承 LangGraph 类型；
- 所有业务逻辑写在 Node 中；
- 正式业务数据只保存在 Checkpoint；
- 所有服务依赖 LangGraph RunnableConfig；
- 用 LangGraph 内部 Thread 对象替代正式 task_id；
- 把 Prompt、Schema 和业务校验硬编码在 Graph Builder 中。

---

## Rejected Alternatives for MVP

### OpenAI Agents SDK as Main Workflow Runtime

**不**选择其单独承担主流程，原因是：

- 更偏 Agent Run、Tool、Session 和 Tracing；
- 阶段图与阶段失效需要项目自行构建；
- Human Review 主要围绕工具审批；
- 持久化长时流程仍需额外 Durable Execution 层。

它未来可以作为某个 Skill 内部的可选节点运行时，但**当前不做选择**。

### Temporal

**不**进入 MVP。原因：

- 基础设施和运行复杂度较高；
- 需要 Server / Cloud、Worker、Task Queue；
- 确定性重放带来额外工程约束；
- 当前产品规模不足以证明这些成本合理。

未来出现长时间、多服务、高并发和严格 SLA 后，可以重新评估。

### Custom Explicit State Machine

保留为**降级方案**。

**优点：** 完全符合 Domain State；框架锁定最低；失效规则最自由。

**缺点：** 需要自行实现 Checkpoint；Pause / Resume；重试；恢复；运行历史；幂等；并发；调试工具。

如果 LangGraph Technical Spike 无法满足核心要求，再重新评估自研状态机。

---

## Mandatory Technical Spike

正式业务代码开发前，必须先完成一个最小工作流验证。完整规划见 [../spikes/langgraph-stategraph-workflow-spike.md](../spikes/langgraph-stategraph-workflow-spike.md)。

### Spike Goal

验证 LangGraph StateGraph 是否能够满足 DEC-022 和 DEC-023 的关键架构要求。

### Fake Workflow

```text
START
→ Fake Fact Node
→ Fake Insight Node
→ Fake Positioning Node
→ Prepare Review Node
→ Human Review Interrupt
→ Apply Review Decision Node
→ Fake Brief Node
→ END
```

不编写真实业务 Prompt，不接入正式外部 Skills。

### Spike Must Prove（18 项）

1. 使用结构化 Domain State；
2. Domain Model 不依赖 LangGraph 类型；
3. 使用持久化 Checkpointer，而非内存 Checkpointer；
4. 服务重启后能够恢复任务；
5. 用户可以通过 Human Review 修改结构化内容；
6. 用户修改 Fact 后，Insight、Positioning 和 Brief 正确失效；
7. 可以只从最早失效阶段重新运行；
8. 有效的上游阶段不会重复运行；
9. 节点失败能够根据错误类型重试；
10. 非重试错误能够暂停并保留状态；
11. 重复请求不会产生重复正式结果；
12. Interrupt 前后的操作满足幂等要求；
13. 单个节点可以脱离完整 Graph 测试；
14. 可以读取当前 State 和 State History；
15. Checkpoint 与业务数据库职责能够分离；
16. 业务进度事件能够被前端或 API 获取；
17. Graph 保持确定性，不依赖 LLM Supervisor；
18. 不创建自治业务 Agent。

### Spike Failure Conditions

出现以下任一问题时，不直接进入正式实现：

- 服务重启后无法恢复；
- Human Review 回写不稳定；
- 修改上游结果后无法正确局部重跑；
- Domain State 与 LangGraph 深度耦合；
- Checkpointer 很难与业务数据库分离；
- Interrupt 重放导致无法控制副作用；
- 节点无法独立测试；
- Graph 复杂度明显超过收益；
- 持久化方案无法用于目标部署环境。

如果 Spike 失败：

```text
重新比较 LangGraph
vs
自研显式状态机
```

不擅自继续实现。

---

## Reason

项目核心是一条具有：

- 强顺序依赖；
- 结构化阶段状态；
- Human Review；
- 跨会话恢复；
- 阶段失效；
- 局部重跑；
- 证据追踪；
- 节点级测试；

的业务工作流。StateGraph 能够将状态、节点、路由、暂停和恢复显式表达，同时保留未来在局部节点内部增加受约束 Worker 的可能性。其额外代码和学习成本具有明确业务价值。

为了避免框架绑定和实现风险，项目同时确认：

- Domain State 独立；
- Skill Service 独立；
- Checkpoint 不等于业务数据库；
- Interrupt 副作用必须幂等；
- Graph 控制核心阶段，不承载所有业务细节；
- 正式实现前必须经过 Technical Spike。

---

## Impact

该决定将影响：

- Python 后端倾向；
- Workflow Runtime；
- Workflow State Specification；
- Human Review；
- Persistence；
- Error Recovery；
- Testing；
- Observability；
- Repository Structure；
- Technical Spike；
- 后续数据库和部署选择；
- LangGraph Checkpointer 选择；
- Skill Node Adapter 设计；
- 简历和架构图表达。

后续技术方案必须遵守：**LangGraph 是运行时和编排层，不是业务 Domain Layer。**

---

## Decision Boundary

### 本决定已经确认

- MVP 选择 LangGraph；
- 主流程使用 StateGraph / Graph API；
- StateGraph 是 LangGraph Graph API 的 Builder；
- Functional API 不作为主业务流程的主要表达方式；
- Functional API 可以用于适合的局部简单任务；
- 不使用高层 ReAct Agent 控制主流程；
- 不使用 LLM Supervisor；
- 不创建多个自治业务 Agent；
- Domain State 独立于 LangGraph；
- Skill Service 独立于 LangGraph；
- Checkpointer 不作为唯一业务数据库；
- StateGraph 负责调度、Checkpoint、Interrupt、Resume 与执行恢复；
- 阶段失效由 Domain Layer 定义；
- Graph 只表达核心业务阶段；
- Interrupt 前副作用必须幂等；
- Temporal 不进入 MVP；
- OpenAI Agents SDK 不作为主工作流运行时；
- 自研状态机作为降级方案；
- 正式业务实现前必须完成 Technical Spike。

### 本决定尚未确认

- Workflow State 最终 Schema；
- LangGraph State 使用 TypedDict、dataclass 或 Pydantic；
- Checkpointer 类型；
- PostgreSQL；
- 数据库 Schema；
- task_id 与 thread_id 映射；
- Reducer；
- State Version；
- Node Adapter 接口；
- Skill Service 接口；
- Human Review Payload；
- API 框架；
- Python 后端框架；
- 前端；
- 部署方式；
- Observability 工具；
- 是否使用 LangSmith；
- 具体模型；
- LLM Gateway；
- Technical Spike 实现细节。

---

## Related Decisions

- [DEC-009](dec-009-stage-level-invalidation-and-partial-rerun.md)：阶段失效与局部重跑；
- [DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)：确定性工作流；
- [DEC-012](dec-012-stage-state-and-structured-business-items.md)：结构化 Workflow State；
- [DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)：任务级持久化；
- [DEC-015](dec-015-contract-based-reusable-business-skills.md)：契约化 Skill；
- [DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)：四个核心 Skills 与一个 Platform Adapter；
- [DEC-021](dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)：MVP 不采用 Multi-Agent 主架构；
- [DEC-022](dec-022-workflow-framework-capability-requirements.md)：Workflow Framework Capability Requirements。

---

## Notes

- 本决定是项目**首个具体工作流框架选择**，翻转了此前多处「LangGraph / 具体框架未确认」的表述；Current Truth 文件已据此同步（详见各架构文档的 DEC-023 小节与 [Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md) 同步检查表）。
- [DEC-022](dec-022-workflow-framework-capability-requirements.md) 作为历史记录**未被修改**：其「具体框架未选择」在 DEC-022 确认时为真；框架选择在 DEC-023 完成。
- 本决定**不**包含正式业务实现（不创建正式业务 Graph / Skill / Prompt / 数据库表 / 前端 / 自动发布 / Multi-Agent / Supervisor / Worker）；**不**选择 Checkpointer / 数据库 / FastAPI / Next.js / LangSmith / 模型供应商 / Embedding / 向量数据库（见 Decision Boundary「尚未确认」）。
- Development Status 保持 `NOT READY`。
- Immediate Next Topic（未启动）：`Workflow State Specification`。在 Workflow State Specification 确认前，不开始正式 LangGraph 业务 Graph 实现。
