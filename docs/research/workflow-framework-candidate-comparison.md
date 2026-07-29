# Research：Workflow Framework Candidate Research and Comparison

> 本文件是 **Exploration Layer** 研究记录，用于记录「为 AI Ecommerce Agent 选择工作流运行框架」的候选比较过程与结论，并支撑 [DEC-023](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)（MVP 选择 LangGraph StateGraph）。
> 评估标准来自 [DEC-022](../decisions/dec-022-workflow-framework-capability-requirements.md)（工作流框架能力需求：Must-have / Should-have / 100 分制评分维度 / 淘汰条件）。
> 相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 相关前置结论：[DEC-011](../decisions/dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)、[DEC-012](../decisions/dec-012-stage-state-and-structured-business-items.md)、[DEC-013](../decisions/dec-013-task-level-persistent-state-and-cross-session-resume.md)、[DEC-015](../decisions/dec-015-contract-based-reusable-business-skills.md)、[DEC-020](../decisions/dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)、[DEC-021](../decisions/dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)、[DEC-022](../decisions/dec-022-workflow-framework-capability-requirements.md)。

---

## 1. Research Question

为 AI Ecommerce Agent 的 MVP 选择工作流运行框架时，应**首先**把候选框架评估为「**有状态、确定性、可持久化的业务工作流运行时**」，而非 Multi-Agent 协作框架（DEC-022）。本研究比较候选框架，回答：

> 在 DEC-022 的能力需求、评分维度与淘汰条件下，哪个候选最适合承载 MVP 的确定性主业务工作流（`Facts → Insights → Positioning → Human Review → Marketing Brief → Xiaohongshu Mapping`）？

候选范围（DEC-022 / Session-002 下一议题约定）：**LangGraph**、**自研显式状态机**、**OpenAI Agents SDK**，必要时补充其他；本研究纳入 **Temporal** 作为补充候选。

---

## 2. Evaluation Criteria from DEC-022

评估采用 DEC-022 的 **100 分制 12 维度**，并叠加 DEC-022 的 **8 条淘汰条件**。

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

**淘汰条件（DEC-022，任一即淘汰，无论评分）：**
无法可靠持久化恢复；HitL 仅靠进程内存；无法稳定确定性主流程；业务状态只能存为聊天历史；难做阶段失效与局部重跑；强绑单一模型供应商；单节点难独立测试；框架复杂度明显超过 MVP 收益。

> 评估原则（承接 DEC-022）：**不得仅依据**流行程度 / GitHub Star / Multi-Agent Demo / 单一厂商宣传 / 个人偏好。

---

## 3. LangGraph

LangGraph 是整体有状态工作流运行框架，提供 Graph API（含 StateGraph）与 Functional API（`entrypoint` / `task`）两种表达方式，底层共用同一 Runtime。

**对 DEC-022 维度的契合度：**

- **Structured State（强）：** 核心控制对象是结构化任务状态而非聊天历史；StateGraph 允许节点读取共享结构化 State 并返回明确的 Partial State Update。`messages[]` 不能作业务 Current Truth 唯一来源（承接 DEC-012 / DEC-022）。
- **Persistence and Recovery（强）：** Checkpointer 保存执行位置、图状态快照、中断、恢复、节点失败后继续、执行历史、可选 Replay；支持跨页面 / 跨会话 / 服务重启 / 从失败节点恢复、不重复运行仍有效阶段（承接 DEC-013）。
- **Human-in-the-loop（强）：** Interrupt / Resume 适合「准备审核 → 持久化暂停 → 用户提交结构化审核决定 → 回写 Domain State → 触发下游失效 → 从正确阶段恢复」；审核可超越整体 Approve / Reject（承接 DEC-007）。
- **Deterministic Routing（强）：** 显式定义固定节点 / 固定边 / 条件路由 / 暂停节点 / 错误分支 / 重试路径 / 从最早失效阶段继续；主流程不由 LLM Supervisor 自由决定（承接 DEC-011 / DEC-021）。
- **Partial Rerun and Invalidation（强，需 Domain Layer 配合）：** StateGraph 可据 Domain State 的阶段有效性路由到最早需重跑阶段；但**失效规则由 Domain Layer 定义**，StateGraph 只据失效状态决定从哪继续——LangGraph Checkpoint / Replay / Time Travel **不能替代**项目自己的业务失效规则（承接 DEC-009）。
- **Structured Output and Validation（强）：** 节点级契约（Input / Output Schema + 前置 / 校验 / 失败 / 重试）可接入；未验证 LLM 输出不得直写 State。
- **Testing and Debugging（强）：** 可单独调用节点、用固定 State 测试条件路由、Mock Skill / LLM / Retrieval、测试 Interrupt / Resume / 节点失败 / 指定阶段恢复 / 下游失效局部重跑 / 完整工作流。
- **Observability（强）：** 可记录节点开始 / 结束、State 版本、Checkpoint、模型、Token、检索、Validator、重试、错误、审核动作、状态变更。
- **Framework Independence（中）：** 存在框架锁定风险，须通过 Node Adapter / 独立 Skill Service / 独立 Domain Model 缓解（见 DEC-023 Framework Lock-in Protection）。
- **Development Complexity（中）：** 代码量更多、学习成本更高、Reducer 须谨慎设计、Graph 过度拆分易复杂、易产生框架耦合。
- **Async and Long-running Tasks（强）：** 支持异步节点、长耗时文件处理 / LLM 调用 / Embedding、后台运行、前端查询进度、超时、服务重启恢复。
- **Future Bounded Workers（强）：** 未来可在复杂节点内部加入受约束并行 Worker（结构化聚合），不改变主工作流由 StateGraph 确定性控制（承接 DEC-021）。

---

## 4. StateGraph and Functional API

**LangGraph 内部结构（须在项目文档中明确）：**

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

- LangGraph 是整体有状态工作流运行框架；
- StateGraph 是 Graph API 中用于构建状态图的 **Builder**；
- StateGraph 本身需要编译（`compile()`）后才能执行；
- 编译后的 Graph 负责实际节点运行、状态更新、Checkpoint、Interrupt 和恢复；
- Functional API 是同一 LangGraph Runtime 上的另一种表达方式；
- **StateGraph 不是 LangGraph 的竞品或替代方案。**

因此项目选择**不是**「LangGraph vs StateGraph」，而是「**使用 LangGraph + 以 StateGraph / Graph API 构建主业务流程**」。

### StateGraph / Graph API（主业务工作流）

**优势：** State 显式；节点显式；边和条件路由显式；审核节点显式；阶段失效路径易表达；适合可视化；适合团队共同理解；适合作品集架构展示；适合未来局部并行与汇合。

**缺点：** 代码量更多；学习成本更高；Reducer 须谨慎设计；Graph 过度拆分时可能复杂；容易产生框架耦合。

### Functional API（局部简单任务）

**优势：** 更接近普通 Python；代码较少；适合改造已有函数；简单任务易理解。

**限制：** 主业务阶段与条件路由不够直观；状态变化易隐藏在函数内部；阶段失效与局部重跑需更多自定义组织；不如 Graph API 适合作为核心流程统一架构表达。

**采用边界（DEC-023）：**

```text
Core Business Workflow: StateGraph / Graph API
Optional Simple Local Tasks: Functional API may be used when appropriate
```

Functional API **不**作为核心业务流程的主要表达方式。

---

## 5. Custom Explicit State Machine（自研显式状态机）

**定位：** 保留为**降级方案**。

**优点：** 完全符合 Domain State；框架锁定最低；失效规则最自由。

**缺点：** 须自行实现 Checkpoint、Pause / Resume、重试、恢复、运行历史、幂等、并发、调试工具。

**对 DEC-022 维度的契合度：** Structured State（强）；Deterministic Routing（强）；Partial Rerun / Invalidation（强）；Framework Independence（强，锁定最低）；但 Persistence / Recovery（中，须自实现 Checkpoint）、Testing / Debugging（中，须自建调试工具）、Observability（弱，须自实现）、Development Complexity（弱，开发成本最高）。

**结论：** 不作为 MVP 首选；若 LangGraph Technical Spike 无法满足核心要求，再重新评估自研状态机（见 DEC-023 Spike Failure Conditions）。

---

## 6. OpenAI Agents SDK

**定位：** 不作为主工作流运行时。

**不选择其单独承担主流程的原因：** 更偏 Agent Run / Tool / Session / Tracing；阶段图与阶段失效须项目自行构建；Human Review 主要围绕工具审批；持久化长时流程仍需额外 Durable Execution 层。

**对 DEC-022 维度的契合度：** Observability（中，Tracing 内置）、Future Workers（强，Agent 取向，但属本项目不采用的 Multi-Agent 方向）；Structured State（中偏弱，Session / Message 取向）、Persistence / Recovery（弱，须额外 Durable 层）、HitL（弱，工具审批为主）、Partial Rerun / Invalidation（弱，须自建）、Framework Independence（中，OpenAI 取向）。

**淘汰条件触发：** 触发「难做阶段失效与局部重跑」「强绑单一模型供应商（OpenAI 取向）」「业务状态可能只能存为聊天历史 / Session」等风险。

**结论：** 未来可作为某个 Skill 内部的可选节点运行时，但当前**不做选择**、**不作为主流程运行时**。

---

## 7. Temporal

**定位：** 不进入 MVP。

**原因：** 基础设施和运行复杂度较高；需要 Server / Cloud、Worker、Task Queue；确定性重放带来额外工程约束；当前产品规模不足以证明这些成本合理。

**对 DEC-022 维度的契合度：** Persistence / Recovery（强，Durable Execution / Replay）、Deterministic Routing（强）、Observability（强，内置）、Async / Long-running（强）、Future Workers（强）；但 Framework Independence（弱，重型基础设施锁定）、Development Complexity（弱，复杂度超 MVP 收益）、Partial Rerun / Invalidation（中偏弱，Replay ≠ 阶段失效）。

**淘汰条件触发：** 明确触发「框架复杂度明显超过当前 MVP 收益」。

**结论：** 未来出现长时间、多服务、高并发、严格 SLA 后，可重新评估；MVP 不采用。

---

## 8. Weighted Score

> **重要披露（诚实性声明）：** 下表评分与加权总分由**归档者**依据 DEC-022 的维度权重（已确认）与用户在 DEC-023 中提供的候选比较理由**定性推导**而来。用户**未提供逐项精确数值**；评级采用 `◉ Strong = 1.0×权重 / ◑ Partial = 0.6×权重 / ○ Weak = 0.25×权重` 的标尺，四舍五入。**最终选择以定性契合度 + DEC-022 淘汰条件为准，而非以加权总分的精确数值为准。** 任何数值不构成用户逐项确认。

| Dimension (weight) | LangGraph + StateGraph | Custom SM | OpenAI Agents SDK | Temporal |
|---|---|---|---|---|
| Structured State (15)        | ◉ 15 | ◉ 15   | ◑ 9    | ◑ 9    |
| Persistence & Recovery (15)  | ◉ 15 | ◑ 9    | ○ 3.75 | ◉ 15   |
| Human-in-the-loop (12)       | ◉ 12 | ◑ 7.2  | ○ 3    | ◑ 7.2  |
| Deterministic Routing (10)   | ◉ 10 | ◉ 10   | ◑ 6    | ◉ 10   |
| Partial Rerun & Invalidation (10) | ◉ 10 | ◉ 10 | ○ 2.5  | ◑ 6    |
| Structured Output & Validation (8) | ◉ 8 | ◉ 8  | ◑ 4.8  | ◑ 4.8  |
| Testing & Debugging (8)      | ◉ 8  | ◑ 4.8  | ◑ 4.8  | ◑ 4.8  |
| Observability (6)            | ◉ 6  | ○ 1.5  | ◑ 3.6  | ◉ 6    |
| Framework Independence (5)   | ◑ 3  | ◉ 5    | ◑ 3    | ○ 1.25 |
| Development Complexity (5)   | ◑ 3  | ○ 1.25 | ◑ 3    | ○ 1.25 |
| Async & Long-running (3)     | ◉ 3  | ◑ 1.8  | ◑ 1.8  | ◉ 3    |
| Future Bounded Workers (3)   | ◉ 3  | ◑ 1.8  | ◉ 3    | ◉ 3    |
| **Derived Total（/100，推导）** | **96** | **≈75** | **≈48** | **≈71** |

**推导排名：** LangGraph + StateGraph（96）＞ Custom SM（≈75）＞ Temporal（≈71）＞ OpenAI Agents SDK（≈48）。

> 数值与用户在 DEC-023 中的定性选择一致（选 LangGraph；OpenAI Agents SDK / Temporal 不作为主流程；自研状态机作降级方案）。本表为**研究归档推导**，非用户逐项确认的评分。

---

## 9. Elimination Criteria

对每个候选应用 DEC-022 的 8 条淘汰条件：

- **LangGraph：** 全部通过——可持久化恢复（Checkpointer）、HitL 不靠内存（Interrupt / Resume + Checkpoint）、可稳定确定性主流程（显式 Graph）、状态非聊天历史（结构化 State）、可做阶段失效局部重跑（StateGraph 路由 + Domain 失效规则）、不强绑单一模型供应商（Model-neutral，须 LLM Gateway）、单节点可独立测试、复杂度与 MVP 收益匹配。→ **通过，进入选择。**
- **OpenAI Agents SDK：** 触发多条（难做阶段失效局部重跑、强绑 OpenAI 取向、状态 Session/Message 取向、HitL 工具审批为主、持久化须额外 Durable 层）。→ **不作为主流程运行时。**
- **Temporal：** 触发「框架复杂度明显超过当前 MVP 收益」（Server / Cloud / Worker / Task Queue / 确定性重放约束，当前规模无法证明）。→ **MVP 淘汰，未来重评。**
- **Custom Explicit State Machine：** 不触发淘汰条件，但 Persistence / Recovery、Observability、Development Complexity 成本高（须自实现 Checkpoint / 恢复 / 幂等 / 并发 / 调试）。→ **不淘汰，保留为降级方案；当 LangGraph Spike 失败时启用对比。**

---

## 10. Recommendation

**推荐（已由用户在 DEC-023 中接受）：**

```text
Workflow Framework: LangGraph
Primary Workflow Modeling API: StateGraph / Graph API
```

理由：项目核心是一条强顺序依赖、结构化阶段状态、Human Review、跨会话恢复、阶段失效、局部重跑、证据追踪、节点级测试的业务工作流；StateGraph 能将状态 / 节点 / 路由 / 暂停 / 恢复显式表达，并保留未来在局部节点内部增加受约束 Worker 的可能；其额外代码与学习成本具有明确业务价值。

**伴随约束（与 DEC-023 一致）：**

- Domain State 独立于 LangGraph；
- Skill Service 独立于 LangGraph；
- Checkpoint ≠ 业务数据库；
- Interrupt 副作用必须幂等；
- Graph 只控制核心阶段，不承载所有业务细节；
- **正式实现前必须完成 Technical Spike**（见第 12 节与 [Spike 文档](../spikes/langgraph-stategraph-workflow-spike.md)）。

---

## 11. Risks

- **框架锁定风险：** Domain Model / Skill / 业务数据库与 LangGraph 深度绑定；缓解 = Node Adapter → 独立 Skill Service → 独立 Domain / Repository / LLM Gateway（DEC-023 Framework Lock-in Protection）。
- **Interrupt 重放副作用风险：** 含 Interrupt 的节点可能从开头重新执行；缓解 = Interrupt 前操作必须幂等、不可逆操作不放在 Interrupt 前、写入用幂等键、审核准备与审核决定拆分（Prepare / Interrupt / Apply 三节点）。
- **Reducer 设计风险：** 阶段主结果默认整体替换 + 显式版本 + 幂等写入，不默认自动 Append；用户修改须显式覆盖或新建版本，不能因 Reducer 自动追加保留多个「当前有效值」。
- **Graph 过度拆分风险：** 不为每个缺失字段 / 风险词 / 评论主题 / Prompt 步骤 / 内部转换单独建 Node；Graph 只表达大阶段与关键路由。
- **Checkpoint 与业务数据库混淆风险：** Checkpointer 仅承载执行恢复 / 图状态快照 / Interrupt / Resume；正式业务 Current Truth、来源、用户修改、当前有效版本、审计记录在业务数据库。
- **Spike 失败风险：** 若服务重启无法恢复 / HitL 回写不稳 / 局部重跑失效 / Domain State 深度耦合 / Checkpointer 难与业务库分离 / Interrupt 重放副作用失控 / 节点无法独立测试 / Graph 复杂度超收益 / 持久化方案不适配目标部署——则**重新比较 LangGraph vs 自研状态机**，不擅自继续实现。

---

## 12. Technical Spike Plan

> 完整 Spike 规划见 [../spikes/langgraph-stategraph-workflow-spike.md](../spikes/langgraph-stategraph-workflow-spike.md)。本节为摘要。

**Spike 目标：** 验证 LangGraph StateGraph 能否满足 DEC-022 与 DEC-023 的关键架构要求。

**Fake Workflow：**

```text
START → Fake Fact → Fake Insight → Fake Positioning
→ Prepare Review → Human Review Interrupt → Apply Review Decision
→ Fake Brief → END
```

不编写真实业务 Prompt，不接入正式外部 Skills。

**须证明（18 项，摘要）：** 结构化 Domain State；Domain Model 不依赖 LangGraph 类型；持久化 Checkpointer（非内存）；服务重启后恢复；HitL 修改结构化内容；修改 Fact 后下游正确失效；只从最早失效阶段重跑；有效上游不重复运行；节点失败按错误类型重试；非重试错误暂停并保留状态；重复请求不产生重复正式结果；Interrupt 前后操作幂等；单节点脱离 Graph 测试；可读 State 与 State History；Checkpoint 与业务数据库职责分离；业务进度事件可被前端 / API 获取；Graph 确定性不依赖 LLM Supervisor；不创建自治业务 Agent。

**失败条件：** 见 Spike 文档；失败则重新比较 LangGraph vs 自研状态机，不擅自进入正式实现。

**范围约束：** Spike **不包含**正式业务实现（不创建正式业务 Graph / Skill / Prompt / 数据库表 / 前端 / 自动发布 / Multi-Agent / Supervisor / Worker）。

---

## 13. Sources and Access Dates

> **诚实性声明：** 本研究的评估内容来自用户在 DEC-023 中提供的候选比较结论（视为本研究的研究输入与结论来源），并对照 DEC-022 的能力需求 / 评分维度 / 淘汰条件。下列为**来源类别**；**具体文献标题 / URL / 访问日期未在归档材料中捕获，记为「未记录 / 待补充」**，不编造。

- **LangGraph 官方架构文档：** StateGraph / Graph API（`compile()` → CompiledStateGraph）、Functional API（`entrypoint` / `task`）、Checkpoint、Interrupt / Resume 的官方说明。—— 具体标题 / URL / 访问日期：未记录 / 待补充。
- **OpenAI Agents SDK 官方文档：** Agent Run / Tool / Session / Tracing 模型说明。—— 具体标题 / URL / 访问日期：未记录 / 待补充。
- **Temporal 官方文档：** Server / Cloud、Worker、Task Queue、确定性重放（Durable Execution）说明。—— 具体标题 / URL / 访问日期：未记录 / 待补充。
- **项目既有决定：** DEC-022（评估标准）、DEC-021（不采用 Multi-Agent）、DEC-011 / 012 / 013 / 015 / 020（控制分工 / 状态 / 持久化 / Skill 契约 / MVP 能力范围）。

> 如需精确引用，后续可在进入正式实现前补全 URL 与访问日期；本研究**不**凭空补造引用。
