# AI Ecommerce Agent

> **Status: Product Discovery 阶段**
> 本项目目前**仅进行产品探索、方案设计、决策治理与文档固化**。
> 在用户明确宣布进入开发阶段以前，不编写任何业务实现代码。

---

## 项目简介（背景，非最终决定）

面向电商业务场景的 Agent 项目。后续将围绕以下主题展开讨论：

- 目标用户
- 核心业务问题
- MVP 范围
- Agent 架构
- RAG
- Skills
- 数据结构
- 开源项目改造
- 产品化方式

> ⚠️ 以上仅为项目背景，**不代表以下事项已经确定**：
> 最终目标用户、商家端或消费者端、单 Agent 或 Multi-Agent、是否采用 LangGraph、RAG 的具体实现、Skill 的具体定义、使用哪个开源项目作为底座、最终技术栈、MVP 功能范围。
>
> 除非用户明确确认，否则一切讨论建议均不构成已接受决定。

---

## 当前目标

完成产品定位、MVP、Agent 架构、RAG、Skill 与开源改造策略的讨论，并把讨论与决策准确归档到本仓库。

---

## 关于技术栈的声明

**本项目尚未确定任何技术栈。** README 与其他文档中不宣称项目已实现任何能力。当前仓库中只存在文档与模板，不存在业务实现代码。

---

## 协作方式

| 角色 | 职责 |
|------|------|
| 用户 | 最终决策人 |
| ChatGPT | 主持讨论、提出方案、输出 Proposed Decisions |
| Claude | 维护、归档、校验项目文件 |

详见 [AGENTS.md](AGENTS.md) 与 [docs/governance/collaboration-model.md](docs/governance/collaboration-model.md)。

---

## 文档目录说明

| 目录 / 文件 | 层级 | 用途 |
|-------------|------|------|
| `AGENTS.md` | — | 协作者入口规范：角色、优先级、禁止事项、检查清单 |
| `docs/governance/` | Governance | 产品设计协议、协作模型、文档规则 |
| `docs/sessions/` | Exploration Layer | 讨论历史、假设、备选方案、被否决方案、开放问题 |
| `docs/rfcs/` | Proposal Layer | 重大方案及替代方案（RFC ≠ 已接受决定） |
| `docs/decisions/` | Decision Layer | 用户明确接受的决定及原因（DEC） |
| `docs/product/` | Current Truth Layer | 当前有效的产品事实（Vision / PRD / MVP / Personas / Flows） |
| `docs/agents/` | Current Truth Layer | Agent 规格 |
| `docs/architecture/` | Current Truth Layer | 系统、数据架构与集成边界 |
| `docs/reviews/` | Execution Gate | 实现就绪审查 |
| `docs/handoffs/` | Execution Gate | 交接与进入开发前的就绪状态 |
| `prompts/` | — | 人机协作提示词模板（如把 ChatGPT 输出交接给 Claude） |

> 注意：`docs/product/`、`docs/agents/`、`docs/architecture/` 下的文档当前均为 **NOT READY / 待讨论** 的初始化桩文件，不包含任何已确认的产品或系统事实。

---

## 开发状态

**NOT READY** — 当前不可进入开发。进入开发的条件详见 [docs/handoffs/implementation-readiness.md](docs/handoffs/implementation-readiness.md)。
