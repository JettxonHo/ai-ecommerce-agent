# Product Vision

> **Status: ACTIVE PRE-DEVELOPMENT PRODUCT VISION — 产品定位、复合 Persona / JTBD 假设策略与行为型演示成功边界已确认；最终字段和交互仍待策划**
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：项目总体导向（DEC-001）、MVP 首要用户（DEC-002）、MVP 核心任务（DEC-003）、平台范围（DEC-004）、本地演示包络（DEC-041），以及证据驱动商品上新策略工作台定位、复合 Persona / JTBD 假设策略和行为型演示成功标准（DEC-042）。

---

## 已确认内容（Confirmed）

### DEC-001 — 真实电商业务价值优先于 Agent 技术复杂度（Accepted，2026-07-27）

> 来源：[DEC-001](../decisions/dec-001-business-value-before-agent-complexity.md)

- **项目总体导向：** 优先证明对真实电商用户、业务问题、工作流程与价值闭环的理解；Agent 技术复杂度服务于业务闭环，而非为展示技术而堆叠。
- **技术应用条件：** LangGraph、RAG、Skill、Multi-Agent、Tool Calling 等仅在能改善业务任务完成效果、可靠性、可追溯性或用户体验时采用；不得无业务依据地增加 Agent 数量、框架组件或系统层级。
- **方向性权重（非量化指标）：** 约 60% 用户问题 / 业务流程 / 产品闭环 / 效果评估；约 40% LangGraph / RAG / Skill / Agent 工作流 / 可靠性设计。

### DEC-002 — MVP 首要用户为中小电商商家的商品运营与内容运营人员（Accepted，2026-07-27）

> 来源：[DEC-002](../decisions/dec-002-primary-mvp-users.md)

- **MVP 首要目标用户：** 中小电商商家的**商品运营人员**与**内容运营人员**（当前作为一个首要群体对待）。
- 产品应优先围绕该群体的真实工作任务、信息输入、决策过程、交付物与效果评价设计。

### DEC-003 — MVP 核心任务为商品上新定位分析与营销 Brief 生成（Accepted，2026-07-27）

> 来源：[DEC-003](../decisions/dec-003-product-launch-positioning-and-marketing-brief.md)

- **MVP 核心任务：** 帮助商品运营与内容运营人员，在商品上新或正式开展内容推广前，完成商品定位分析，并生成可供后续内容策划与执行使用的结构化营销 Brief。
- **核心交付物：** 结构化商品上新营销 Brief。
- 该任务闭环为业务任务方向，**不代表**每一步的 Agent、技术实现与数据来源已确定。

### DEC-004 — 产品核心保持平台中立，小红书种草作为首个 MVP 演示场景（Accepted，2026-07-27）

> 来源：[DEC-004](../decisions/dec-004-platform-neutral-core-xiaohongshu-demo.md)

- **平台范围：** 核心商品定位分析与营销 Brief 能力保持**平台中立**，不绑定淘宝、小红书、抖音或其他单一平台。
- **首个演示场景：** MVP 在演示与作品集案例中选择 **小红书商品种草** 作为首个具体展示场景。
- **产品逻辑边界：** 通用层（通用定位与营销 Brief）为核心；平台适配层负责将通用 Brief 映射为平台表达（首个＝小红书种草模板）。小红书模板是通用 Brief 的一种适配方式，**不是**唯一输出形态。

### DEC-042 — 证据驱动商品上新策略工作台定位与行为型演示成功标准（Accepted，2026-08-06）

> 来源：[DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md)

- **定位：** 面向中小电商商品与内容运营人员的证据驱动商品上新策略工作台，将用户资料转化为可审核、可追溯的定位分析、平台中立 Marketing Brief 与小红书 Brief 映射。
- **Persona 策略：** 一个复合主 Persona，商品运营与内容运营作为职责视角；详细画像继续标为假设，真实访谈是 Beta 前门禁。
- **成功边界：** 以本地可启动、端到端闭环、结果可理解 / 审核 / 追溯 / 恢复 / 导出和人工可用性为主，不以机械总分或销量承诺自动接受。

> 注：统一单 Agent、LangGraph StateGraph、按需混合 Retrieval、4 个 Core Skills、Xiaohongshu Adapter、PostgreSQL 持久化、RFC-003 Workflow Runtime、RFC-006 LLM Runtime，以及首个演示的代表性验收包、行为门禁和 Markdown-first 用户导出均已确认；仍待策划的是输入与 Brief 最终公共字段、工作台组件、测试工具以及 RFC-004 / 005 / 007 与 Frontend Architecture 的实现细节（见 [mvp-scope.md](mvp-scope.md)）。

---

## 当前状态

- 项目处于 **Pre-development Planning（正式开发前策划）阶段**；业务实现与长期 Goal 均未启动。
- 已确认总体导向、首要用户、核心任务、平台范围、产品定位、复合 Persona / JTBD 假设策略、行为型演示成功边界、Agent / Workflow / Retrieval 概念架构、生产持久化基础与本地演示包络；详细用户研究证据和交互 / 契约细节仍待策划。
- 其余具体内容，必须等到对应 Proposed Decision 被用户明确接受并记为 Accepted Decision（见 [../decisions/](../decisions/)）后，才能写入。

---

## 待讨论的开放问题（Vision 相关）

> 以下事项尚未确认，列出以便后续讨论，**不构成已接受决定**：

- 最终目标用户：**MVP 首要用户已确认**（DEC-002）；Persona 细节见 [user-personas.md](user-personas.md)。
- 商家端 / 消费者端：**已确认商家端**（DEC-002）。
- 要解决的核心业务问题：**已确认**（DEC-003）。
- 最终产品定位与差异化价值：**已确认**为证据驱动商品上新策略工作台（DEC-042）；品牌命名和对外文案不是当前阻塞项。
- Persona / JTBD：复合 Persona 结构与基线假设已确认；画像具体取值和真实证据待 Beta 前访谈。
- 演示成功标准：行为与人工可用性边界、三个固定资料包 + 一个变更脚本、必要行为门禁、人工 `PASS / FAIL` 与 Release Candidate Live Smoke 已确认（DEC-042 / DEC-048）；测试工具、Fixture 实例和最终 E2E 步骤待 Testing Strategy 补全。
- Agent / Workflow：**已确认**为一个统一用户侧 Agent + LangGraph StateGraph 确定性工作流，不采用 Multi-Agent 主架构或 LLM Supervisor（DEC-021 / DEC-023）。
- Retrieval / Skills：**已确认**按需混合 Retrieval 概念边界、4 个 Core Skills 与 1 个 Xiaohongshu Adapter（DEC-014 / DEC-020 / DEC-026～032）；单一 OpenAI Provider / `gpt-5.6-terra`、窄型同步 Port、Structured Output、有界 Recovery、可读版本元组、确定性 Profile、Adapter Secret / Payload Allowlist、同 Port 测试替身与单次人工 RC Smoke 已由 DEC-052～054 与 RFC-006 冻结。索引仍待 RFC-005；实现仍待完整策划包和 Goal 激活。
- 平台范围：**已确认**核心中立 + 小红书 Brief 映射；其他平台、完整平台正文与自动发布不进入首个 Goal（DEC-004 / DEC-031 / DEC-041）。

这些问题的讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得为使文档「完整」而补充未经讨论的事实。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
