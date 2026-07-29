# DEC-021：MVP 不采用 Multi-Agent 主架构，保留评测驱动的受约束并行 Worker 扩展

> 本决定记录用户已明确接受的 Architecture 决定（Multi-Agent 架构判断）。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。对应研究记录：[../research/multi-agent-architecture-assessment.md](../research/multi-agent-architecture-assessment.md)（对应 Question-008）。
> 承接 [DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（确定性工作流控制）、[DEC-012](dec-012-stage-state-and-structured-business-items.md)（结构化 Workflow State）、[DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)（任务级持久化）、[DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（按需混合 RAG）、[DEC-015](dec-015-contract-based-reusable-business-skills.md)（契约化 Skill）、[DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（四个核心 Skills + 一个小红书 Adapter）。

## Type

Architecture

## Status

Accepted（2026-07-28，用户对 Multi-Agent 调研结论明确回复「同意」，通过 Decision Gate）

## Decision

AI Ecommerce Agent 的 MVP **不采用** Supervisor + 多个自治 Agent 作为主架构。系统采用**一个统一的 Ecommerce Agent 用户交互入口**，由**确定性 Workflow Controller** 编排**四个核心业务 Skills** 和**一个小红书 Platform Adapter**。不同 Skills 可以使用不同 Prompt、模型配置、工具和结构化输出，但**不拥有独立流程控制权**。未来仅在出现真实并行需求，并通过评测证明收益超过成本时，才在特定节点内部引入**中心化 Orchestrator 与受约束的并行 Workers**。

MVP **不采用**以下架构作为主架构：

```
Supervisor Agent
├── Product Agent
├── Customer Insight Agent
├── Positioning Agent
├── Marketing Agent
└── Review Agent
```

MVP **采用**：

```
Unified Ecommerce Agent Interface
              ↓
Deterministic Workflow Controller
              ↓
Contract-based Skills and Platform Adapter
```

内部业务流程为：

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

系统架构应被描述为：

```
Stateful Agentic Workflow
+
Deterministic Orchestration
+
Skill-specialized LLM Nodes
+
Human-in-the-loop
+
Hybrid RAG
```

而**不是**：

```
Supervisor-led Autonomous Multi-Agent System
```

## User-facing Agent Boundary

产品对用户可以呈现为一个统一 Agent：

```
Ecommerce Strategy Agent
```

该 Agent 负责：接收用户商品资料；展示任务进度；请求必要补充；展示事实、洞察和定位；发起人工审核；返回营销 Brief；返回小红书场景 Brief。

用户不需要理解内部存在多少 Prompt、节点、模型调用或工具。统一 Agent 是**产品交互身份**，不代表所有任务必须由一次 LLM 调用完成。

## Internal Execution Boundary

系统内部由确定性 Workflow Controller 管理：执行顺序、当前阶段、阶段有效性、暂停与恢复、人工审核、下游失效、局部重跑、错误处理、重试、持久化、Skill 调用、Platform Adapter 调用。

LLM、Skill 或未来 Worker **不得**自行修改完整工作流顺序。

## Skill-specialized LLM Nodes

四个业务 Skills 可以具有独立的：System Instructions、Prompt、输入契约、输出 Schema、模型配置、Temperature、Tool 权限、RAG 查询策略、校验规则、重试规则、测试案例、版本。

但这些差异**不自动意味着**它们是独立 Agent。例如：

```
Customer Insight Analysis Skill
```

可以拥有专门的评论分析 Prompt 和检索工具，但它：不决定下一步调用哪个业务阶段；不拥有独立长期目标；不维护独立任务状态；不与 Product Positioning Skill 自由协商；不直接修改最终定位；不控制人工审核。

因此它属于：

```
Skill-specialized LLM Node
```

而不是：

```
Autonomous Customer Insight Agent
```

即：

```
Skill ≠ Agent
Multiple LLM Calls ≠ Multi-Agent
```

## Reasons for Not Using Multi-Agent in MVP

### 1. Core Workflow Is Sequential

当前业务链具有明确上游依赖：

```
Facts
→ Insights
→ Positioning
→ Marketing Brief
```

如果商品事实错误，下游洞察、定位和 Brief 都会受影响。该链路不适合多个自治 Agent 独立并行决策。

### 2. Shared State Is Strongly Coupled

所有业务阶段共享：`task_id`；原始输入；来源；事实；洞察；定位；用户修改；审核结果；阶段有效性；局部重跑状态。拆分多个自治 Agent 会增加：状态复制；上下文重复；Agent 间通信；状态不一致；来源关系丢失；调试复杂度。

### 3. No Independent Final Deliverables

当前 MVP 的主要交付物是一条连续业务价值链，而不是多个互相独立的交付物。当前不同时生成：定价方案；客服手册；库存计划；广告预算；多平台内容；多份独立研究报告。因此缺少必须使用多个自治 Agent 的业务理由。

### 4. No Independent Permissions

当前四个 Skills 不需要完全不同的系统权限。它们主要读取和写入同一个任务的结构化 Workflow State。

### 5. Reliability Has Higher Priority

当前 MVP 更关注：来源可追溯；无依据事实受控；状态一致性；人工审核；阶段失效；局部重跑；可测试性。Multi-Agent 会引入额外的：Agent 间理解偏差；状态冲突；通信失败；重复推理；成本；延迟；错误传播。在没有明确收益证据前，不增加这些风险。

## Architecture Terminology

项目 README、架构文档和简历中优先使用以下表达：

```
Stateful Agentic Workflow
Deterministically Orchestrated Agent Workflow
Contract-based Skill Architecture
Human-in-the-loop AI Workflow
Evidence-grounded E-commerce Strategy Agent
```

**不应**为了技术关键词将系统描述为：

```
Multi-Agent E-commerce Platform
```

除非未来真正实现多个具有独立目标、上下文和执行循环的 Agent。

## Bounded Parallel Workers

本决定**不禁止**未来在局部节点中使用并行 Worker。未来可能采用：

```
Deterministic Main Workflow
+
Centralized Orchestrator
+
Bounded Parallel Workers
```

Worker 必须满足：接收明确任务；接收有限输入；返回结构化输出；不控制主工作流；不直接修改最终状态；不自行确认业务结论；不拥有无限工具权限；输出经过汇总与校验；失败可被单独重试；不影响其他 Worker 状态。

### Potential Future Worker Scenarios

**1. Large-scale Review Analysis**

```
Review Analysis Orchestrator
├── Current Product Positive Review Worker
├── Current Product Negative Review Worker
├── Competitor A Review Worker
└── Competitor B Review Worker
```

各 Worker 只返回结构化证据和主题候选。最终 Customer Insight 仍由主 Skill 汇总和校验。

**2. Competitor Research**

```
Competitor Research Orchestrator
├── Competitor A Worker
├── Competitor B Worker
├── Competitor C Worker
└── Competitor D Worker
```

每个 Worker 只能分析指定竞品。

**3. Multi-platform Mapping**

未来在 Generic Marketing Brief 完成后，可以并行生成：

```
Xiaohongshu Adapter
Taobao Adapter
Douyin Adapter
```

这些属于并行 Platform Adapters，不一定需要成为长期自治 Agent。

**4. Independent Evaluation**

可以使用独立模型调用进行：来源一致性检查；Brief 质量评测；风险检查；Schema 或内容 Judge。该组件优先定义为：

```
Evaluator Node
```

而不是自治 Review Agent。

## Multi-Agent Entry Criteria

只有满足以下至少一个条件，才重新评估 Multi-Agent。

- **Criterion A — True Parallelism：** 出现多个真正互不依赖、可以并行完成的业务任务。
- **Criterion B — Context Isolation：** 某项任务需要大量独立上下文，并且混合 RAG、按需加载、状态压缩、Skill-specific Context 仍无法有效解决。
- **Criterion C — Permission Isolation：** 不同执行实体需要严格不同的权限（如 Research Worker 只读公开资料；Publishing Agent 拥有平台写入权限；Approval Agent 只能审批、不能修改）。
- **Criterion D — Independent Objectives：** 多个执行实体拥有不同且相对独立的目标和交付物。
- **Criterion E — Tool Overload：** 单一 Agent 持有过多工具并稳定出现工具选择失败，并且无法通过 Tool 命名空间、Skill 加载、确定性路由、权限裁剪解决。
- **Criterion F — Evaluation Evidence：** 对照评测证明 Multi-Agent 明显优于当前基线。

## Required Evaluation Before Upgrade

未来升级前必须比较：

```
Baseline:
Deterministic Skill Workflow

Variant:
Centralized Multi-Agent or Worker Architecture
```

至少评估：Fact traceability；Unsupported fact rate；Insight quality；Positioning acceptance；Brief completeness；Human edit amount；State consistency；Failure recovery；Latency；Token usage；API cost；Debugging complexity；Partial rerun correctness。

只有在业务质量或效率提升足够显著时，才采用 Multi-Agent。

## Supervisor Boundary

MVP **不创建** LLM Supervisor Agent。工作流路由由代码和状态决定，例如：

```
if fact_stage_invalid:
    run_fact_extraction

elif insight_stage_invalid:
    run_customer_insight

elif positioning_pending_review:
    pause_for_human_review

elif review_accepted:
    run_marketing_brief
```

**不采用**「让 Supervisor LLM 自由判断下一步调用哪个 Agent」。未来如果出现开放式研究任务，可以引入局部 Research Orchestrator，但**不得**替代主 Workflow Controller。

## Relation to Existing Decisions

该决定延续：[DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（确定性工作流控制流程）；[DEC-012](dec-012-stage-state-and-structured-business-items.md)（结构化 Workflow State）；[DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)（任务级持久化）；[DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)（按需、混合式 RAG）；[DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill 是带执行契约的业务能力包）；[DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)（四个核心 Skills 与一个小红书 Adapter）。

该决定明确：

```
Skill ≠ Agent
```

以及：

```
Multiple LLM Calls ≠ Multi-Agent
```

## Reason

当前 MVP 的核心任务是高度顺序依赖、共享同一任务状态和证据链的业务流程。采用 Multi-Agent 不会显著提高并行能力，反而可能增加：Token 成本；响应延迟；状态同步；上下文重复；Agent 间冲突；错误传播；调试成本；失败恢复复杂度。

确定性工作流与契约化 Skills 已经能够满足：专业化 Prompt；不同模型配置；工具隔离；结构化输出；可测试性；人工审核；状态持久化；局部重跑。

因此 MVP **不需要**通过自治 Agent 数量证明 Agent 能力。详见研究记录 [../research/multi-agent-architecture-assessment.md](../research/multi-agent-architecture-assessment.md)。

## Impact

该决定将影响：系统架构；Agent 定义；Workflow Graph；Skill 调用方式；GitHub 基底仓库筛选；框架选择；状态模型；测试策略；成本控制；README；架构图；简历项目描述；后续扩展策略。

后续技术方案必须回答：

> 它是否支持由确定性主工作流编排多个独立测试的 Skill 节点，并允许未来在特定节点中增加受约束并行 Worker，而不要求当前使用 Supervisor + 多自治 Agent？

## Decision Boundary

**本决定已经确认：**

- MVP 不采用 Multi-Agent 主架构；
- 不创建 Supervisor LLM；
- 不为四个 Skills 分别创建自治 Agent；
- 产品对用户呈现一个统一 Ecommerce Agent；
- 内部由确定性 Workflow Controller 编排；
- 各 Skill 可以使用不同 Prompt、模型和工具；
- 多次 LLM 调用不等于 Multi-Agent；
- 未来允许局部受约束并行 Worker；
- Multi-Agent 升级必须由真实需求和评测驱动；
- 当前项目应描述为 Stateful Agentic Workflow。

**本决定尚未确认：**

- Workflow Controller 的具体框架；
- 是否使用 LangGraph；
- 是否使用 OpenAI Agents SDK；
- 是否使用 LangChain；
- 是否使用自研状态机；
- 具体模型数量；
- 是否使用不同模型处理不同 Skill；
- Worker 实现框架；
- 并行评论处理是否进入 MVP；
- 独立 Evaluator 是否进入 MVP；
- GitHub 基底仓库；
- 前后端技术栈。

> 本决定**不**确认 LangGraph、CrewAI、AutoGen、OpenAI Agents SDK、LangChain、Worker 实现、独立 Evaluator、基底仓库、模型供应商。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求（对应 Question-008：是否需要 Multi-Agent）

## Related Decisions

- [DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)
- [DEC-012](dec-012-stage-state-and-structured-business-items.md)
- [DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)
- [DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)
- [DEC-015](dec-015-contract-based-reusable-business-skills.md)
- [DEC-020](dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)

## Related Research

- [Multi-Agent Architecture Assessment](../research/multi-agent-architecture-assessment.md)
- Effective agent and workflow architecture guidance；
- Multi-Agent scaling and failure research；
- External e-commerce Multi-Agent implementation review。
- > 具体文献出处 / URL / 访问日期未在归档材料中捕获，记为「未记录 / 待补充」（见研究记录第 12 节）。

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 本决定正式回答了 Question-008（是否需要 Multi-Agent）：**MVP 不需要 Multi-Agent 主架构**；Multi-Agent 升级须由真实需求 + 对照评测驱动。
- 本决定**不**创建 Supervisor Agent / Product Agent / Customer Insight Agent / Positioning Agent / Marketing Agent / Review Agent / Agent-to-Agent Messaging / Multi-Agent Runtime / 并行 Worker 代码。
- 「统一 Ecommerce Agent」是**用户交互身份**，内部由确定性 Workflow Controller 编排多个 Skill-specialized LLM Node；这与「单次 LLM 调用完成所有任务」**不同**。
- 未来受约束并行 Worker 是**局部节点内部**的扩展（中心化 Orchestrator + Bounded Workers），**不**替代主 Workflow Controller，也**不**等同于无约束 Multi-Agent。
- 本决定**不**确认 Workflow Controller 框架（LangGraph / OpenAI Agents SDK / LangChain / 自研状态机）、Worker 实现框架、独立 Evaluator 是否进 MVP、并行评论处理是否进 MVP、具体模型数量 / 是否分模型、GitHub 基底仓库、前后端技术栈、模型供应商。
- 项目对外描述优先使用 `Stateful Agentic Workflow` / `Deterministically Orchestrated Agent Workflow` / `Contract-based Skill Architecture` / `Human-in-the-loop AI Workflow` / `Evidence-grounded E-commerce Strategy Agent`，**不**使用 `Multi-Agent E-commerce Platform`。
