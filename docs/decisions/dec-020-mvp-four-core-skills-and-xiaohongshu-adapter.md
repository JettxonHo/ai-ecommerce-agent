# DEC-020：MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter

> 本决定记录用户已明确接受的 MVP Skill 范围决定。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill = 带执行契约的可复用业务能力包）、[DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 复用策略）与首轮三候选评估（[DEC-017](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md) / [DEC-018](dec-018-adapt-product-differentiation-for-positioning-skill.md) / [DEC-019](dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)）。

## Type

Product Architecture

## Status

Accepted（2026-07-28，用户对 MVP Skill 裁剪方案明确回复「确认」，通过 Decision Gate）

## Decision

AI Ecommerce Agent 首个可运行 MVP 的业务能力范围确定为：

```
4 个 Core Business Skills
+
1 个 Platform Adapter
+
若干 Shared Capabilities
```

核心业务链路为：

```
Product Intake & Fact Extraction
↓
Customer Insight Analysis
↓
Product Positioning
↓
Human Review Gate
↓
Marketing Brief Generation
↓
Xiaohongshu Brief Mapping
```

其中：

- 前四项属于平台无关的核心业务能力；
- 小红书映射属于平台适配层；
- 系统仍采用一个常规强制人工审核节点；
- 完整视觉执行和自动内容生产不进入首版 MVP。

## MVP Core Skills

### Core Skill 1：Product Intake & Fact Extraction Skill

**Business Goal**

接收商品基础资料和增强资料，对输入进行完整度检查、来源处理、事实提取和冲突识别，形成可追溯的商品事实候选。

**Responsibilities**

该 Skill 负责：

- 接收最低可运行输入；
- 接收可选增强资料；
- 解析商品资料；
- 标记信息缺失；
- 识别关键冲突；
- 提取商品事实候选；
- 为事实关联来源；
- 区分明确事实、待确认内容和资料不足；
- 输出风险和警告；
- 在关键资料不足时触发异常暂停。

**Candidate Outputs**

概念输出包括：

```
facts[]
missing_information[]
conflicts[]
warnings[]
source_fragments[]
```

> 以上不是最终 Schema。

**Scope Decision**

原候选能力：

```
Product Input Assessment
Product Fact Extraction
```

在 MVP 中合并为一个 Skill。

**Reason for Merge**

两者处理同一批原始商品资料，流程紧密相连：

```
读取资料
→ 检查完整度
→ 提取事实
→ 检查冲突
```

在首版拆成两个 Skill 会增加：重复解析、重复数据转换、Skill 间接口、状态同步成本、调试复杂度。未来当资料解析、事实抽取和输入诊断复杂度明显增加时，可以重新评估是否拆分。

### Core Skill 2：Customer Insight Analysis Skill

**External Donor**

```
nexscope-ai/eCommerce-Skills/product-review-analysis
Reuse Mode: Adapt
Related Decision: DEC-017
```

**Business Goal**

根据当前有效商品事实、用户评论、用户访谈、竞品反馈或其他用户证据，形成可追溯的用户洞察候选。

**Responsibilities**

该 Skill 负责识别：用户需求、用户痛点、购买动机、购买阻碍、使用场景、正向价值感知、用户原声、功能诉求、待验证用户假设、资料不足。

**Evidence Classification**

重要输出需要区分：

```
evidence-backed insight
model inference
hypothesis to validate
insufficient information
```

**Degraded Mode**

没有用户评论、访谈或反馈资料时，该 Skill 仍可基于商品事实生成初步用户假设，但必须明确标记为 `hypothesis to validate`。不得将模型推断包装成真实用户洞察。

### Core Skill 3：Product Positioning Skill

**External Donor**

```
nexscope-ai/eCommerce-Skills/product-differentiation-shopify
Reuse Mode: Adapt
Related Decision: DEC-018
```

**Business Goal**

将当前有效商品事实、用户洞察、竞品资料和推广目标转化为带依据、可审核的商品定位候选。

**Responsibilities**

该 Skill 负责形成：目标用户候选、核心需求、使用场景、商品角色、核心价值、价值主张、差异化方向、卖点优先级、定位陈述候选、竞品差异候选、待验证假设、资料限制。

**Output Status**

正式输出为：

```
Positioning Candidates
```

而不是 `Confirmed Positioning`。商品定位需要在人工审核节点中由用户确认、修改或拒绝。

**Evidence Boundary**

定位候选应关联：商品事实、用户洞察、可选竞品证据、当前推广目标。没有竞品资料时可以形成基础定位，但不得声称已完成可靠的竞品差异化验证。

### Human Review Gate

MVP 保留一个常规强制人工审核节点。该节点位于：

```
Customer Insight Analysis
+
Product Positioning
↓
Human Review
↓
Marketing Brief Generation
```

人工审核材料至少应包含：商品事实摘要、关键用户洞察、用户假设、定位候选、卖点优先级、来源和主要证据、冲突、缺失信息、风险提示。

用户应能够：修改商品事实、接受或否定洞察、修改用户假设、选择或修改定位候选、调整卖点优先级、补充资料、拒绝不符合业务方向的建议。

用户修改后，按照 [DEC-009](dec-009-stage-level-invalidation-and-partial-rerun.md) 执行阶段失效和局部重跑。

> 本决定不增加第二个常规审核 Gate（与 DEC-007 一致）。

### Core Skill 4：Marketing Brief Generation Skill

**External Mechanism Donor**

```
feichanggege/ecommerce-visual-copywriting-skill
Reuse Mode: Partial Adapt
Related Decision: DEC-019
```

**Business Goal**

将已经完成审核的商品事实、用户洞察、商品定位、卖点优先级和推广目标，转化为平台无关的结构化营销 Brief。

**Preconditions**

调用前需要：Fact Layer 有效；Insight Layer 有效；Positioning 已经过人工审核；当前策略状态有效；必要来源仍可访问。

**Candidate Outputs**

概念输出包括：

```
target_user
primary_need
purchase_motivations
purchase_barriers
positioning_statement
core_message
selling_points[]
proof_points[]
content_angles[]
usage_scenarios[]
prohibited_claims[]
required_disclaimers[]
missing_information[]
assumptions[]
```

> 以上不是最终 Schema。

**Retained Candidate 3 Mechanisms**

该 Skill 可以吸收：Feature → Advantage → Benefit → Evidence；卖点证据边界；信息缺失标记；风险提示；禁止表达；免责声明要求；先审核策略、后进入执行；执行前质量检查。

**Excluded Outputs**

当前 Marketing Brief Generation Skill 不负责：商品主图、详情页、Storyboard、最终图片卡片、生图 Prompt、完整小红书笔记、自动内容发布。

## Platform Adapter

### Xiaohongshu Brief Mapping Adapter

**Classification**

```
Platform Adapter
```

而不是 `Core Business Reasoning Skill`。

**Business Goal**

将平台无关的 Marketing Brief 映射为适合小红书种草场景的结构化执行 Brief。

**Conceptual Flow**

```
Generic Marketing Brief
↓
Xiaohongshu Brief Mapping
↓
Xiaohongshu-specific Brief
```

**Candidate Outputs**

概念输出可以包括：

```
platform_goal
target_reader
seeding_scenario
core_content_angle
cover_direction
note_structure
image_card_tasks[]
user_concern_responses[]
proof_display_guidance[]
creator_execution_notes[]
prohibited_expressions[]
required_disclaimers[]
```

> 以上不是最终 Schema。

**Responsibility Boundary**

该 Adapter：不重新提取商品事实、不重新生成用户洞察、不自行修改商品定位、不推翻已经审核的卖点优先级、不控制完整工作流、不自动发布内容。它只负责：将已经确认的通用营销策略映射为小红书场景中的执行要求。

**Product Principle**

该结构延续已经确认的（DEC-004）：平台无关核心 + 小红书作为首个 Demo 场景。未来增加淘宝、抖音或其他平台时，应通过新的 Platform Adapter 扩展，而不是将平台规则写入核心分析 Skills。

## Shared Capabilities

> 以下能力进入 MVP，但**不**作为独立业务 Skill。

### Document Parsing

负责：读取商品资料、解析短文档、提取文本、识别文档和来源、提供结构化片段。它是技术能力，不独立承担完整业务目标。

### Hybrid Retrieval

根据 [DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)，采用按需、混合式检索。负责：关键词检索、语义检索、精确术语检索、返回来源片段、为业务 Skill 提供证据。它不负责：流程控制、最终业务判断、自动确认事实、人工审核、阶段失效。

当前分类为：

```
Shared Retrieval Capability
```

而不是独立 `Evidence Retrieval Skill`。未来如果检索过程发展为复杂的查询规划、证据包生成、检索质量判断和多轮研究，可以重新评估是否升级为独立业务 Skill。

### Source Management

负责：`source_id`、`fragment_id`、来源定位、证据关系、来源可用性、当前任务来源隔离。

### Schema Validation

分类为：

```
Deterministic Validator / Tool
```

负责：输入结构校验、输出结构校验、必填字段检查、ID 引用检查、类型检查。它不是 Skill。

### Risk Validation

首版采用嵌入式风险验证，而不是独立 Compliance Review Skill。可能包括：

```
确定性风险规则
+
Marketing Brief 内部风险检查
+
按需检索当前运营或平台知识
+
人工审核
```

> 当前不创建独立法律、合规或平台审核 Agent。

### Task Persistence

负责：`task_id`、跨页面恢复、跨会话恢复、输入持久化、中间结果持久化、审核记录、运行历史。

### Stage Invalidation and Partial Rerun

负责：上游修改后的下游失效、阶段级重跑、有效状态检查、防止使用失效结果、恢复正确执行起点。

> 这些属于 Workflow Controller 和 Workflow State，不是 Skill。

## Capabilities Not Defined as Independent Skills

> 以下能力在首版不单独创建 Skill。

### Evidence Retrieval

原因：本质上是多个业务 Skills 共用的检索能力；真正业务目标由调用方决定；单独包装会增加不必要的节点和接口。

### Compliance Review

原因：当前风险校验可以嵌入 Marketing Brief 和确定性 Validator；单独拆分可能造成第二套审核流程；容易让用户误解为最终法律意见；官方规则时效维护成本较高。

### Workflow State Management

属于基础设施，不属于业务能力包。

### Schema Validation

属于确定性 Tool / Validator，不属于业务 Skill。

### Platform Publishing

不进入首版，也不创建发布 Skill。

## Future Extensions

> 以下能力不进入首个 MVP。

### Visual Execution Brief Skill

Candidate 3 的主要未来改造目标。未来可能负责：Campaign Style Lock、Storyboard、视觉任务、画面描述、图内文案要求、设计说明、生图约束。

> 当前只保留设计输入，不创建正式 Skill Specification。

### Visual and Content Production

暂不包括：主图生成、详情页生成、图片卡片生成、视频分镜生成、图像生成、最终小红书笔记生成。

### Automated Publishing

暂不包括：小红书发布、淘宝上架、抖音发布、自动修改店铺、自动投放广告、自动发送给设计师。

### Operational Extensions

暂不包括：评论持续监控、运营数据监控、定价、利润计算、库存、广告预算、PPC、完整品牌战略、全渠道运营、客服 SOP。

## Final MVP Capability Map

```
Deterministic Workflow Controller

1. Product Intake & Fact Extraction Skill
                ↓
2. Customer Insight Analysis Skill
                ↓
3. Product Positioning Skill
                ↓
        Human Review Gate
                ↓
4. Marketing Brief Generation Skill
                ↓
5. Xiaohongshu Brief Mapping Adapter
```

共享能力：

```
Document Parsing
Hybrid Retrieval
Source Management
Schema Validation
Risk Validation
Task Persistence
Stage Invalidation
Partial Rerun
```

## MVP Classification Table

| Capability | Classification | MVP |
| --- | --- | --- |
| Product Intake & Fact Extraction | Core Skill | Yes |
| Customer Insight Analysis | Core Skill | Yes |
| Product Positioning | Core Skill | Yes |
| Marketing Brief Generation | Core Skill | Yes |
| Xiaohongshu Brief Mapping | Platform Adapter | Yes |
| Document Parsing | Shared Capability | Yes |
| Hybrid Retrieval | Shared Capability | Yes |
| Source Management | Shared Capability | Yes |
| Schema Validation | Deterministic Validator | Yes |
| Risk Validation | Embedded Validation | Yes |
| Task Persistence | Infrastructure | Yes |
| Stage Invalidation | Infrastructure | Yes |
| Partial Rerun | Infrastructure | Yes |
| Visual Execution Brief | Future Skill | No |
| Storyboard | Future Extension | No |
| Main Image / Detail Page | Future Extension | No |
| Automatic Image Generation | Future Extension | No |
| Final Xiaohongshu Post Generation | Future Extension | No |
| Automatic Publishing | Future Extension | No |

## Reason

如果将每一个技术动作都包装成 Skill，会造成：Skill 数量膨胀、业务能力与基础设施混淆、工作流节点增加、状态接口复杂、调试和测试成本提高、为展示 Agent 技术而过度设计。

四个 Core Skills 已经覆盖完整核心价值链：

```
理解商品
→ 理解用户
→ 确定定位
→ 形成营销执行 Brief
```

小红书 Adapter 则负责展示首个真实平台场景，同时保持核心架构平台无关。

将完整视觉执行和自动发布放到未来，可以避免 MVP 从「商品定位和 Brief Agent」扩张为「完整电商内容生产平台」。

## Impact

该决定将影响：MVP Scope、Skill Specification 数量、Workflow Graph、Workflow State、Agent 数量判断、Shared Capabilities、RAG 使用位置、Human Review、GitHub 基底仓库筛选、前后端界面、测试计划、Demo 场景、简历项目描述、实现排期。

后续技术方案必须回答：

> 它是否能够用四个核心业务 Skills 和一个平台 Adapter 跑通完整业务价值链，同时将检索、状态、校验和持久化保持为明确的共享系统能力？

## Decision Boundary

**本决定已经确认：**

- MVP 使用四个核心业务 Skills；
- Product Input Assessment 与 Product Fact Extraction 合并；
- Customer Insight Analysis 进入核心 MVP；
- Product Positioning 进入核心 MVP；
- Marketing Brief Generation 进入核心 MVP；
- Xiaohongshu Brief Mapping 作为平台 Adapter 进入 MVP Demo；
- Evidence Retrieval 是共享能力；
- Compliance Review 不单独成为 Skill；
- Workflow State 和 Schema Validation 不是 Skill；
- 保留一个常规人工审核 Gate；
- Visual Execution Brief 不进入首版；
- Storyboard、主图详情页、生图和自动发布不进入首版。

**本决定尚未确认：**

- 四个 Skills 的最终名称；
- 每个 Skill 的最终 Specification；
- 最终输入输出 Schema；
- 小红书 Adapter 的最终输出；
- 是否生成完整小红书笔记；
- 官方平台知识来源；
- Risk Validator 的具体规则；
- Skill 的代码接口；
- Skill 注册机制；
- Skill 对应的工作流节点数量；
- Agent 数量；
- Multi-Agent；
- LangGraph；
- 工作流基底仓库；
- 模型和数据库；
- 前后端技术栈。

> 本决定**不**确认 Multi-Agent、Agent 数量、LangGraph、Skill 最终 Schema、Skill 目录、模型供应商、向量数据库、GitHub 基底仓库、前后端技术栈。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related Decisions

- [DEC-004](dec-004-platform-neutral-core-xiaohongshu-demo.md)：平台中立核心 + 小红书首个 Demo
- [DEC-005](dec-005-layered-mvp-inputs.md)：最低可运行输入与增强输入分层
- [DEC-006](dec-006-four-layer-structured-marketing-brief.md)：四层结构化营销 Brief
- [DEC-007](dec-007-single-review-node-and-exception-pauses.md)：一个常规人工审核节点与异常暂停
- [DEC-008](dec-008-tiered-evidence-and-traceable-conclusions.md)：证据类型与来源可追溯
- [DEC-009](dec-009-stage-level-invalidation-and-partial-rerun.md)：阶段失效与局部重跑
- [DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)：确定性工作流控制流程
- [DEC-012](dec-012-stage-state-and-structured-business-items.md)：结构化 Workflow State
- [DEC-013](dec-013-task-level-persistent-state-and-cross-session-resume.md)：任务级持久化
- [DEC-014](dec-014-on-demand-hybrid-rag-and-layered-data-access.md)：按需、混合式 RAG
- [DEC-015](dec-015-contract-based-reusable-business-skills.md)：Skill 是带执行契约的业务能力包
- [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)：外部 Skill 研究和契约化改造
- [DEC-017](dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)：Product Review Analysis Adapt
- [DEC-018](dec-018-adapt-product-differentiation-for-positioning-skill.md)：Product Differentiation Adapt
- [DEC-019](dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)：Ecommerce Visual Copywriting Adapt

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 承接 [DEC-015](dec-015-contract-based-reusable-business-skills.md)（Skill 契约化定义）与 [DEC-016](dec-016-external-skill-research-and-contract-based-adaptation.md)（外部 Skill 复用策略）；本决定是「首批 MVP Skill 清单裁剪」议题的确认结果，区分了 Core Skill / Platform Adapter / Shared Capability / Deterministic Validator / Infrastructure / Future Extension。
- 三个外部供体映射在 MVP 中的落点：Customer Insight Analysis Skill ← Candidate 1（DEC-017，Adapt）；Product Positioning Skill ← Candidate 2（DEC-018，Adapt）；Marketing Brief Generation Skill ← Candidate 3（DEC-019，Partial Adapt）。Visual Execution Brief Skill（Candidate 3 主目标）**不进入首版 MVP**。
- 本决定**不**创建四个 Core Skill 的正式 Skill Specification，也**不**创建小红书 Adapter 的正式 Specification，也**不**创建任何 Skill 代码、Visual Execution Brief / Storyboard / 主图 / 详情页 / 生图 Prompt / 自动发布。
- 文中 Candidate Outputs / Candidate Inputs 均为**概念性方向，非最终数据契约**。
- 本决定**不**确认 Multi-Agent（Question-008 在本决定基础上可继续讨论）、Agent 数量、LangGraph、Skill 最终 Schema / 目录、模型供应商、向量数据库、工作流基底仓库、前后端技术栈。
