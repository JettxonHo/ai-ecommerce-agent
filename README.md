# AI Ecommerce Agent

> **Status: Pre-development Planning · Development = CONDITIONALLY READY**
> 当前只允许产品规格闭合、架构 RFC、Readiness 规划、测试与 Goal 文档工作。Business / Production Implementation、TS-01～TS-05 执行与实际 Goal 均未启动。

---

## 产品定位

AI Ecommerce Agent 面向中小电商商家的商品运营与内容运营人员，帮助其基于用户提供的商品与市场资料，完成上新定位分析、人工审核、平台中立 Marketing Brief 与小红书 Brief 映射。

首个交付目标是**本地可复现、受控单工作区的端到端演示 MVP**。产品使用引导式任务工作台；聊天记录不作为业务 Current Truth。

权威范围见 [DEC-041](docs/decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md)。最终字段、交互细节、Frontend Architecture、Provider 与 RFC-003～007 仍待后续 Decision Gate，不得从本简介自行推断。

---

## 已确认的产品与架构基础

- 平台中立核心，小红书作为首个演示 Adapter；
- 一个统一 Ecommerce Agent，主流程不采用 Multi-Agent 或 LLM Supervisor；
- LangGraph StateGraph 承担确定性工作流编排，业务 Current Truth 与 Checkpoint 分离；
- 4 个 Core Skills：Product Intake & Fact Extraction、Customer Insight Analysis、Product Positioning、Marketing Brief Generation；
- 1 个 Xiaohongshu Brief Mapping Adapter；
- 按需混合检索、版本化 Source / Fragment / Evidence Link、单一关键 Human Review、阶段失效与局部重跑；
- RFC-001 Repository and Application Architecture 与 RFC-002 Persistence and Transaction Architecture 已 Accepted；
- Business Current Truth 的生产持久化栈已由 RFC-002 选定为 PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic；SQLite 不作为持久化验收引擎；
- FND-001～003 已完成，仓库已有 Python 后端 Package、质量工具、架构测试、CI 与 Repository Protection 基础。

---

## 当前策划缺口

- 产品定位句、JTBD / Persona 假设、任务工作台完整流程和最终输入输出字段；
- Frontend Architecture；
- RFC-003 LangGraph Runtime、RFC-004 API / Human Review、RFC-005 Source / Retrieval、RFC-006 LLM Runtime、RFC-007 Observability；
- ARP-02 / 03 / 09 完整 Artifact、ARP-05～08、TS-01～TS-05 Charter；
- MVP Development Plan、Testing Strategy 与长期 Goal 最终文本。

以上缺口必须在业务实现前闭合。具体 Provider、前端框架、公共 API 和最终 Schema 尚未决定。

## Wave 1 Readiness 状态

- ARP-01、ARP-04、ARP-10：完整 Artifact 已 Accepted；
- ARP-02、ARP-03、ARP-09：仅 TS-01 Minimum Slice 已 Accepted，完整 Artifact 仍待扩展；
- PR #28 已合并，Issue #27 已关闭；该合并不授权 Spike 执行或业务实现。

---

## 协作方式

| 角色 | 职责 |
|------|------|
| 用户 | Decision / RFC / 范围 / 高风险操作 / Goal 激活的最终决策人 |
| GPT-5.6 Sol `xhigh` | 策划、架构、复杂拆分和独立 Review |
| GPT-5.6 Luna `max` | Goal 激活后按冻结规格完成代码实现；不可用时实现任务暂停，不得静默替换 |

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
| `docs/readiness/` | Readiness | Architecture Readiness Artifact 与 Spike 前置证据 |
| `docs/traceability/` | Traceability | 需求、Decision、RFC、未来 Issue 与测试的映射 |
| `docs/goals/` | Goal | 待接受或已激活的长期执行计划 |
| `prompts/` | — | 人机协作提示词模板（如把 ChatGPT 输出交接给 Claude） |

> Current Truth 中只允许写入 Accepted 内容；Assumption、Proposal 与 Open Question 必须显式标注。

---

## 开发状态

**CONDITIONALLY READY（规划范围）** — Foundation 已完成，但业务实现仍未授权。必须完成产品规格、RFC-003～007、Readiness 规划包、测试策略、Goal 文本和最终一致性 Review，并由用户明确批准“进入 Goal 执行阶段”后，才可开始长期开发。详见 [Implementation Readiness](docs/handoffs/implementation-readiness.md) 与 [AGENTS.md](AGENTS.md)。
