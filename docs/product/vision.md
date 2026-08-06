# Product Vision

> **Status: ACTIVE PRE-DEVELOPMENT PRODUCT VISION — 高层产品与架构方向已确认，最终定位句、JTBD / Persona 假设和演示成功标准仍待策划**
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：项目总体导向（DEC-001）、MVP 首要用户（DEC-002）、MVP 核心任务（DEC-003）、平台范围与首个演示场景（DEC-004），以及受控单工作区、本地端到端演示和引导式任务工作台交付边界（DEC-041）。

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

> 注：统一单 Agent、LangGraph StateGraph、按需混合 Retrieval、4 个 Core Skills、Xiaohongshu Adapter 与 PostgreSQL 持久化均已确认；仍待策划的是最终产品定位表述、JTBD / Persona 假设、输入与 Brief 最终字段、工作台交互以及 RFC-003～007 / Frontend Architecture 的实现细节（见下方「待讨论的开放问题」与 [mvp-scope.md](mvp-scope.md)）。

---

## 当前状态

- 项目处于 **Pre-development Planning（正式开发前策划）阶段**；业务实现与长期 Goal 均未启动。
- 已确认总体导向、首要用户、核心任务、平台范围、Agent / Workflow / Retrieval 概念架构、生产持久化基础与本地演示包络；最终产品表述、用户研究假设和交互 / 契约细节仍待策划。
- 其余具体内容，必须等到对应 Proposed Decision 被用户明确接受并记为 Accepted Decision（见 [../decisions/](../decisions/)）后，才能写入。

---

## 待讨论的开放问题（Vision 相关）

> 以下事项尚未确认，列出以便后续讨论，**不构成已接受决定**：

- 最终目标用户：**MVP 首要用户已确认**（DEC-002）；Persona 细节见 [user-personas.md](user-personas.md)。
- 商家端 / 消费者端：**已确认商家端**（DEC-002）。
- 要解决的核心业务问题：**已确认**（DEC-003）。
- 最终产品定位：**已基本明确**（用户 DEC-002 + 任务 DEC-003 + 平台 DEC-004）；正式产品名称 / 定位表述未单独作为决定接受。
- 产品的差异化价值、最终定位句与演示成功标准：待本轮产品策划确认。
- Agent / Workflow：**已确认**为一个统一用户侧 Agent + LangGraph StateGraph 确定性工作流，不采用 Multi-Agent 主架构或 LLM Supervisor（DEC-021 / DEC-023）。
- Retrieval / Skills：**已确认**按需混合 Retrieval 概念边界、4 个 Core Skills 与 1 个 Xiaohongshu Adapter（DEC-014 / DEC-020 / DEC-026～032）；具体 Provider、索引、Prompt 与实现仍待 RFC-005 / 006。
- 平台范围：**已确认**核心中立 + 小红书 Brief 映射；其他平台、完整平台正文与自动发布不进入首个 Goal（DEC-004 / DEC-031 / DEC-041）。

这些问题的讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得为使文档「完整」而补充未经讨论的事实。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
