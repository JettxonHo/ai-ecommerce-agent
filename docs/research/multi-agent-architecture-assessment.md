# Multi-Agent Architecture Assessment（Multi-Agent 架构评估）

> 本文件是 **Exploration Layer（研究 / 评估记录）**，记录用于判断「AI Ecommerce Agent 的 MVP 是否需要 Multi-Agent」的评估过程与结论。
> 本评估**不是** Decision；其结论已由 [DEC-021 — MVP 不采用 Multi-Agent 主架构，保留评测驱动的受约束并行 Worker 扩展](../decisions/dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)（Accepted，Architecture，2026-07-28）采纳。
> 相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)；对应开放问题 Question-008（是否需要 Multi-Agent）。
> **诚实性说明：** 本评估的**分析内容**来自用户已接受的 DEC-021 推理与项目已确认约束（DEC-001~020）；具体外部文献的标题 / 作者 / URL / 访问日期**未在归档材料中捕获**，因此「Sources and Access Dates」一节仅记录所调研的**来源类别**，具体引用记为「未记录 / 待补充」，**不编造**具体出处。

---

## 1. Research Question

> 评估问题（对应 Question-008）

AI Ecommerce Agent 的**首个 MVP** 是否应当采用 **Multi-Agent 主架构**（例如 Supervisor + 多个自治 Agent）？

具体需要回答：

- 当前业务链路是否真正需要多个**独立、自治、可并行**的 Agent？
- Multi-Agent 相对「确定性工作流 + 受约束 LLM 节点 + 人工审核」是否带来**净收益**？
- 是否存在更合适的**中间形态**（统一 Agent + 确定性编排 + 契约化 Skill + 可选受约束并行 Worker）？
- 满足什么条件时，未来才应重新评估升级到 Multi-Agent？

> 本评估**不是**从热门技术关键词出发选择架构，而是**从已确认业务流程与可靠性需求出发**判断 Multi-Agent 的适用性（承接 Session-002 Constraint 1：业务驱动技术）。

---

## 2. Current Workflow Characteristics

> 项目当前已确认的核心业务链路特征（DEC-003 / DEC-006 / DEC-007 / DEC-009 / DEC-011 / DEC-020）

- **强顺序依赖的核心价值链：**

  ```
  Facts → Insights → Positioning → Marketing Brief
  ```

  商品事实错误会向下游传播：错误事实 → 错误洞察 → 错误定位 → 错误 Brief。该链路具有明确的上游→下游依赖。

- **共享同一任务状态与证据链：** 所有业务阶段共享 `task_id`、原始输入、来源、事实、洞察、定位、用户修改、审核结果、阶段有效性、局部重跑状态（DEC-012 / DEC-013）。

- **单一连续交付物：** MVP 的主要交付物是**一条连续业务价值链**（理解商品 → 理解用户 → 确定定位 → 形成营销 Brief + 小红书映射），而非多个互相独立的交付物（DEC-003 / DEC-020）。

- **可靠性优先级高于并行性：** MVP 更关注来源可追溯、无依据事实受控、状态一致性、人工审核、阶段失效、局部重跑、可测试性（DEC-008 / DEC-009 / DEC-010 / DEC-011）。

- **单一关键审核节点：** 在定位之后、Brief 之前保留一个常规强制人工审核 Gate（DEC-007 / DEC-020），用户拥有最终判断权。

> 结论：当前业务链路本质上是**顺序的、状态强耦合的、单一交付物**的流程。

---

## 3. Workflow vs Agent

> 概念区分（承接 DEC-015 / DEC-011）

| 维度 | 确定性 Workflow + 受约束 LLM 节点 | 自治 Multi-Agent |
| --- | --- | --- |
| 流程控制 | 由代码 + 状态决定（显式规则） | 由 Agent 自行决定下一步 |
| 状态 | 集中、显式 Workflow State（单一来源） | 可能分散、需 Agent 间同步 |
| 专业化 | 不同 Skill 可用不同 Prompt / 模型 / 工具（Skill-specialized LLM Node） | 每个 Agent 独立目标 / 上下文 / 执行循环 |
| 可测试性 | 阶段可单独测试、局部重跑 | Agent 间交互更难复现 |
| 适用场景 | 顺序、强耦合、可靠性优先 | 真正独立、可并行、需上下文 / 权限隔离 |

关键区分（DEC-021 明确）：

```
Skill ≠ Agent
多次 LLM 调用 ≠ Multi-Agent
```

四个 Core Skills 可以拥有**独立**的 System Instructions / Prompt / 输入契约 / 输出 Schema / 模型配置 / Temperature / Tool 权限 / RAG 策略 / 校验规则 / 重试规则 / 测试案例 / 版本，但这些差异**不自动意味着**它们是独立 Agent。例如 Customer Insight Analysis Skill 拥有专门的评论分析 Prompt 和检索工具，但它不决定下一步调用哪个阶段、不拥有独立长期目标、不维护独立任务状态、不与 Positioning Skill 自由协商、不直接修改最终定位、不控制人工审核——因此它是 **Skill-specialized LLM Node**，而非 **Autonomous Customer Insight Agent**。

---

## 4. Multi-Agent Benefits

> Multi-Agent 架构在**通用意义上**的优势（用于判断这些优势是否适用于当前 MVP）

- **真正并行：** 当存在多个互不依赖、可并行的任务时，可缩短端到端时延。
- **上下文隔离：** 每个Agent 拥有独立上下文窗口，可处理需要大量独立上下文的任务。
- **权限隔离：** 不同执行实体可拥有严格不同的系统权限（只读研究 vs 写入发布 vs 仅审批）。
- **独立目标与交付物：** 适合多个拥有不同、相对独立目标的执行实体。
- **专业化深度：** 每个 Agent 可深度聚焦单一职责、长期记忆与多工具自主选择。

> 评估重点：这些优势**是否在当前 MVP 的业务链路中真正成立**，还是仅在理论上成立。见第 6、8 节。

---

## 5. Multi-Agent Costs and Failure Modes

> Multi-Agent 在**当前可靠性优先**的 MVP 中可能引入的成本与风险

- **状态复制与上下文重复：** 共享同一任务状态时，多个自治 Agent 会增加状态复制与上下文重复。
- **Agent 间通信与状态不一致：** 拆分多个自治 Agent 会增加 Agent 间通信、状态不一致、来源关系丢失、调试复杂度。
- **理解偏差与冲突：** Agent 间理解偏差、状态冲突、通信失败、重复推理。
- **成本与延迟：** Token 成本、响应延迟上升。
- **错误传播：** 上游错误在 Agent 协作中更易传播且更难定位。
- **可调试性与失败恢复复杂度：** Agent 间交互更难复现、局部重跑边界模糊。

> 这些正是 DEC-008（证据可追溯）、DEC-009（阶段失效 / 局部重跑）、DEC-011（确定性控制）、DEC-013（任务级持久化）所要控制的可靠性维度——Multi-Agent 在没有明确收益证据前会**增加**这些风险。

---

## 6. Sequential vs Parallel Task Analysis

> 逐项判断当前 MVP 任务是否真正需要并行 Multi-Agent

| 当前 MVP 任务 | 是否可独立并行？ | 说明 |
| --- | --- | --- |
| Product Intake & Fact Extraction | 否（链路起点，下游全依赖） | 事实错误向下游传播 |
| Customer Insight Analysis | 否（依赖有效事实） | 顺序依赖 |
| Product Positioning | 否（依赖事实 + 洞察） | 顺序依赖 |
| Marketing Brief Generation | 否（依赖已审核定位） | 须先经人工审核 |
| Xiaohongshu Brief Mapping | 弱并行（依赖通用 Brief） | 可视为下游适配，非独立交付 |

当前 MVP **不同时**生成：定价方案、客服手册、库存计划、广告预算、多平台内容、多份独立研究报告。因此**缺少必须使用多个自治 Agent 的业务理由**。

> 未来**可能**出现真正并行的场景（大批量评论分析、多竞品研究、多平台映射、独立评测），这些在第 10 节作为「未来受约束并行 Worker」的候选，**不**作为当前采用 Multi-Agent 主架构的理由。

---

## 7. E-commerce Open-source Comparisons

> 对外部电商 / Agent 开源实现的观察类别

调研覆盖的**来源类别**（具体仓库 / 项目 / URL / 访问日期未在归档材料中记录，记为「未记录 / 待补充」，不编造具体出处）：

- **官方 Agent 与工作流架构指南：** 关于 Workflow vs Agent、何时使用 Multi-Agent、编排模式的通用指引。
- **Multi-Agent 扩展与失败研究：** 关于 Multi-Agent 在规模化时的成本、失败模式、调试难度的研究与经验报告。
- **电商 / 内容生成类开源实现：** 关于现有电商 Agent / 内容生产项目如何组织 Agent、Skill、工作流与人工审核的观察。

**观察要点（通用结论，非对特定仓库的采用决定）：**

- 许多「Multi-Agent」标签的项目，其核心业务链路本质仍是**顺序工作流 + 多个受约束 LLM 步骤**，而非真正独立自治 Agent。
- 电商商品分析这类**强顺序依赖 + 共享状态 + 可靠性优先**的场景，普遍采用**确定性编排 + 专业化 LLM 节点 + 人工审核**而非 Supervisor + 多自治 Agent。
- 真正从 Multi-Agent 获益的场景，通常具备**真并行 / 上下文隔离 / 权限隔离 / 独立交付物**等特征——当前 MVP 不具备。

> 这些观察与第 2、6、8 节的分析一致。本节**不**确认采用任何具体开源仓库或基底仓库（承接 DEC-016 的 Workflow Base / Skill Donor 区分；具体基底仓库仍未选择）。

---

## 8. Applicability Matrix

> Multi-Agent 适用性矩阵：逐条判断当前 MVP 是否满足「应使用 Multi-Agent」的条件

| 适用条件（来自第 10 节 Entry Criteria） | 当前 MVP 是否满足 | 判断 |
| --- | --- | --- |
| Criterion A：真正并行（多个互不依赖、可并行任务） | 否 | 核心链路强顺序依赖（第 6 节） |
| Criterion B：上下文隔离需求（混合 RAG / 按需加载 / 状态压缩 / Skill 上下文仍无法解决） | 否 | DEC-014 分层数据访问 + 按需混合 RAG 已提供上下文管理；当前未观察到无法解决的大上下文任务 |
| Criterion C：权限隔离（不同执行实体需严格不同权限） | 否 | 四个 Skills 主要读写同一任务的结构化 Workflow State，不需要完全不同权限 |
| Criterion D：独立目标与交付物 | 否 | MVP 是单一连续价值链，非多个独立交付物 |
| Criterion E：工具过载（单 Agent 工具过多、稳定工具选择失败，且 Tool 命名空间 / Skill 加载 / 确定性路由 / 权限裁剪无法解决） | 否 | 未观察到；当前采用确定性路由 + 契约化 Skill |
| Criterion F：评测证据（对照评测证明 Multi-Agent 明显优于基线） | 否 | 尚无此类评测 |

> 结论：当前 MVP **不满足**任何一条「应使用 Multi-Agent」的准入条件。

---

## 9. Recommended Architecture

> 推荐架构（已被 DEC-021 采纳）

**MVP 不采用** Supervisor + 多个自治 Agent 作为主架构。**采用：**

```
Unified Ecommerce Agent Interface（用户交互身份）
              ↓
Deterministic Workflow Controller（编排）
              ↓
Contract-based Skills + Platform Adapter
```

内部业务流程：

```
Product Intake & Fact Extraction Skill
        ↓
Customer Insight Analysis Skill
        ↓
Product Positioning Skill
        ↓
   Human Review Gate
        ↓
Marketing Brief Generation Skill
        ↓
Xiaohongshu Brief Mapping Adapter
```

系统应被描述为：

```
Stateful Agentic Workflow
+ Deterministic Orchestration
+ Skill-specialized LLM Nodes
+ Human-in-the-loop
+ Hybrid RAG
```

而**不是** `Supervisor-led Autonomous Multi-Agent System`。

**用户侧：** 产品对用户呈现为统一 `Ecommerce Strategy Agent`（接收资料 / 展示进度 / 请求补充 / 展示事实洞察定位 / 发起审核 / 返回 Brief / 返回小红书 Brief）；用户无需理解内部存在多少 Prompt / 节点 / 模型调用 / 工具。统一 Agent 是**产品交互身份**，不代表所有任务必须由一次 LLM 调用完成。

**内部侧：** 由确定性 Workflow Controller 管理执行顺序 / 当前阶段 / 阶段有效性 / 暂停恢复 / 人工审核 / 下游失效 / 局部重跑 / 错误处理 / 重试 / 持久化 / Skill 调用 / Adapter 调用。LLM、Skill 或未来 Worker **不得**自行修改完整工作流顺序。**主 Workflow State 是唯一当前任务状态来源。**

---

## 10. Future Entry Criteria

> 重新评估 Multi-Agent 的准入条件（满足**至少一条**才重新评估）

- **Criterion A — True Parallelism：** 出现多个真正互不依赖、可并行完成的业务任务。
- **Criterion B — Context Isolation：** 某项任务需要大量独立上下文，且混合 RAG / 按需加载 / 状态压缩 / Skill-specific Context 仍无法有效解决。
- **Criterion C — Permission Isolation：** 不同执行实体需要严格不同权限（如只读研究 Worker vs 拥有平台写入权限的发布 Agent vs 只能审批不能修改的审批 Agent）。
- **Criterion D — Independent Objectives：** 多个执行实体拥有不同且相对独立的目际与交付物。
- **Criterion E — Tool Overload：** 单一 Agent 持有过多工具并稳定出现工具选择失败，且 Tool 命名空间 / Skill 加载 / 确定性路由 / 权限裁剪无法解决。
- **Criterion F — Evaluation Evidence：** 对照评测证明 Multi-Agent 明显优于当前基线（见第 11 节）。

> 即使满足准入条件，升级方向也是「确定性主工作流 + 中心化 Orchestrator + **受约束并行 Worker**」，而**非**无约束的 Supervisor + 多自治 Agent。

**受约束 Worker 必须满足：** 接收明确任务 / 接收有限输入 / 返回结构化输出 / 不控制主工作流 / 不直接修改最终状态 / 不自行确认业务结论 / 不拥有无限工具权限 / 输出经汇总与校验 / 失败可单独重试 / 不影响其他 Worker 状态。

**未来 Worker 候选场景：** 大规模评论分析（按产品 / 竞品切片并行）、多竞品研究、多平台映射（小红书 / 淘宝 / 抖音 Adapter 并行）、独立评测（来源一致性 / Brief 质量 / 风险 / Schema 或内容 Judge，优先定义为 `Evaluator Node` 而非自治 Review Agent）。

> 本评估**不**确认 Worker 实现框架、并行评论处理是否进入 MVP、独立 Evaluator 是否进入 MVP（承接 DEC-021 Decision Boundary）。

---

## 11. Evaluation Plan

> 未来升级到 Multi-Agent / Worker 架构前必须进行的对照评测

比较：

```
Baseline:  Deterministic Skill Workflow
Variant:   Centralized Multi-Agent or Worker Architecture
```

至少评估以下维度（承接 DEC-010 三维评价 + DEC-008/009 可靠性）：

- Fact traceability（事实可追溯）
- Unsupported fact rate（无依据事实率）
- Insight quality（洞察质量）
- Positioning acceptance（定位接受度）
- Brief completeness（Brief 完整性）
- Human edit amount（人工修改量）
- State consistency（状态一致性）
- Failure recovery（失败恢复）
- Latency（延迟）
- Token usage（Token 用量）
- API cost（API 成本）
- Debugging complexity（调试复杂度）
- Partial rerun correctness（局部重跑正确性）

> **只有在业务质量或效率提升足够显著时，才采用 Multi-Agent。** 升级前不删除本评估；评测结果应作为新 Decision 的依据。

---

## 12. Sources and Access Dates

> **诚实性说明：** 本评估的来源为用户 / 协作 AI 所进行调研的结论；**具体文献标题 / 作者 / URL / 访问日期未在归档材料中捕获**。以下仅记录**来源类别**，具体引用记为「未记录 / 待补充」。**不编造**具体出处、URL 或日期。

调研覆盖的来源类别：

- **Effective agent and workflow architecture guidance**（官方 / 权威 Agent 与工作流架构指南）—— 具体出处：未记录 / 待补充。
- **Multi-Agent scaling and failure research**（Multi-Agent 扩展与失败模式研究）—— 具体出处：未记录 / 待补充。
- **External e-commerce Multi-Agent implementation review**（外部电商 Multi-Agent 实现观察）—— 具体出处：未记录 / 待补充。
- **项目已确认约束**（DEC-001~020）—— 见 [../decisions/decision-log.md](../decisions/decision-log.md)。

> 如后续需要可追溯的具体引用，应在重新评估或升级评测时补充真实来源与访问日期；在此之前，本节保持「未记录」状态，**不**补充未经核实的出处。

---

## 评估结论（Summary）

当前 MVP 的核心任务是**高度顺序依赖、共享同一任务状态与证据链**的业务流程。采用 Multi-Agent **不会**显著提高并行能力，反而可能增加 Token 成本、响应延迟、状态同步、上下文重复、Agent 间冲突、错误传播、调试成本与失败恢复复杂度。确定性工作流与契约化 Skills 已能满足专业化 Prompt / 不同模型配置 / 工具隔离 / 结构化输出 / 可测试性 / 人工审核 / 状态持久化 / 局部重跑。因此 MVP **不需要**通过自治 Agent 数量证明 Agent 能力。

**该结论已被 [DEC-021](../decisions/dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md) 采纳为 Accepted Decision。**
