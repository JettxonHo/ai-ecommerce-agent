# Technical Spike：LangGraph StateGraph Workflow Spike

> **Status: PLANNED — NOT STARTED**
> **Spike 触发依据：** [DEC-023 — MVP 选择 LangGraph StateGraph 作为核心工作流运行方式](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)
> **评估标准来源：** [DEC-022 — Workflow Framework Capability Requirements](../decisions/dec-022-workflow-framework-capability-requirements.md)
> **相关 Session：** [Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)
>
> **范围约束（重要）：** 本 Spike **不包含正式业务实现**。不创建正式业务 Graph、不创建正式业务 Skill、不编写正式业务 Prompt、不创建正式数据库表、不创建前端、不实现自动发布、不创建 Multi-Agent / Supervisor / Worker。本文件**只**记录验证目标、Fake Workflow、测试场景、成功标准与失败标准。

---

## 1. 验证目标（Spike Goal）

验证 LangGraph StateGraph 是否能够满足 DEC-022 与 DEC-023 的关键架构要求：

- 显式结构化 Domain State（非聊天历史）；
- 持久化 Checkpointer（非进程内存）下的恢复 / Interrupt / Resume；
- Human Review 回写 Domain State 并触发下游失效；
- 阶段失效与局部重跑（由 Domain Layer 定义失效、StateGraph 据此路由）；
- 节点级重试与错误恢复；
- 幂等与并发保护（Interrupt 前后副作用可控）；
- 单节点可独立测试；
- Domain Model 不绑定 LangGraph 类型。

---

## 2. Fake Workflow

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

约束：

- **不**编写真实业务 Prompt；
- **不**接入正式外部 Skills；
- 各节点返回 Fake 结构化数据（结构上贴近 DEC-023 Domain Model 概念形态，但仅为 Spike 占位，**非**正式数据契约）。

---

## 3. 测试场景（Test Scenarios / Spike Must Prove）

> 共 **18 项**必须证明。逐项设计测试场景并记录结果（结果栏待 Spike 执行时填充，本文件当前**不**预先填写通过 / 失败）。

| # | 须证明项 | 测试场景（要点） | 结果 |
|---|----------|------------------|------|
| 1 | 使用结构化 Domain State | Fake 节点读写显式结构化状态，而非 messages[] | 待测 |
| 2 | Domain Model 不依赖 LangGraph 类型 | Domain 模型类不继承 / 引入 LangGraph 专属类型 | 待测 |
| 3 | 使用持久化 Checkpointer（非内存） | 配置非内存 Checkpointer 并持久化 | 待测 |
| 4 | 服务重启后能够恢复任务 | 模拟重启后从 Checkpoint 续跑 | 待测 |
| 5 | 用户可通过 Human Review 修改结构化内容 | Interrupt 后提交结构化修改并回写 | 待测 |
| 6 | 修改 Fact 后 Insight/Positioning/Brief 正确失效 | 修改 Fact 后下游阶段标记 invalid | 待测 |
| 7 | 可以只从最早失效阶段重新运行 | 仅重跑最早失效阶段 | 待测 |
| 8 | 有效上游阶段不会重复运行 | 未失效上游节点不重复执行 | 待测 |
| 9 | 节点失败能够根据错误类型重试 | 可重试错误按策略重试 | 待测 |
| 10 | 非重试错误能够暂停并保留状态 | 非重试错误进入暂停且状态不丢 | 待测 |
| 11 | 重复请求不会产生重复正式结果 | 幂等键 / 版本避免重复正式写入 | 待测 |
| 12 | Interrupt 前后操作满足幂等要求 | Interrupt 重放不产生重复副作用 | 待测 |
| 13 | 单个节点可脱离完整 Graph 测试 | 节点可独立调用并 Mock 依赖 | 待测 |
| 14 | 可以读取当前 State 与 State History | 可读当前态与历史 Checkpoint | 待测 |
| 15 | Checkpoint 与业务数据库职责能够分离 | 执行恢复数据与业务 Current Truth 分别存放 | 待测 |
| 16 | 业务进度事件能够被前端或 API 获取 | 进度事件可对外暴露（机制占位即可） | 待测 |
| 17 | Graph 保持确定性，不依赖 LLM Supervisor | 路由由代码 / 状态决定，无自由 Agent | 待测 |
| 18 | 不创建自治业务 Agent | Spike 中无自治 Agent / Supervisor | 待测 |

---

## 4. 成功标准（Success Criteria）

Spike 视为**成功**，当且仅当：

- 第 3 节 18 项**全部**为「通过」；
- Domain Model 与 LangGraph 解耦可验证（第 2、15 项）；
- Checkpointer 与业务数据库职责可分离（第 15 项）；
- Interrupt 重放副作用可控（第 12 项）；
- 持久化方案可适配目标部署环境（暂未选择部署方式，但须证明可适配，非绑定某一具体部署）。

成功后：进入下一议题 `Workflow State Specification`（由用户主导讨论），**不**自动开始正式业务 Graph 实现。

---

## 5. 失败标准（Failure Conditions）

出现以下**任一**问题时，**不**直接进入正式实现：

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

## 6. 范围排除（本 Spike 不包含）

- 正式业务 Graph；
- 正式业务 Skill；
- 正式 Prompt；
- 正式数据库表；
- 前端；
- 自动发布；
- Multi-Agent；
- Supervisor；
- Worker；
- 任何具体框架 / 供应商的正式选型（Checkpointer / 数据库 / FastAPI / Next.js / LangSmith / 模型供应商 / Embedding / 向量数据库——这些在 DEC-023 中明确**尚未确认**，本 Spike **不**对其进行选型）。

---

## 7. 记录规则

- 本文件在 Spike 执行前**只**含规划（验证目标 / Fake Workflow / 测试场景 / 成功标准 / 失败标准），不含执行结果。
- Spike 执行时逐项填充第 3 节「结果」列，并附可复现的最小证据说明；不得预先填写「通过」。
- 任何超出本规划范围的决定（如正式选型、正式业务实现）须先回到用户主导的 Decision Gate，不在本 Spike 中擅自确认。
