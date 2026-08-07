# AI Ecommerce Agent

> **Status: Pre-development Planning · Development = CONDITIONALLY READY**
> 当前只允许产品规格闭合、架构 RFC、Readiness 规划、测试与 Goal 文档工作。Business / Production Implementation、TS-01～TS-05 执行与实际 Goal 均未启动。

---

## 产品定位

AI Ecommerce Agent 是面向中小电商商品与内容运营人员的**证据驱动商品上新策略工作台**，将用户提供的商品与市场资料转化为可审核、可追溯的商品定位分析、平台中立 Marketing Brief 与小红书 Brief 映射。

首个交付目标是**本地可复现、受控单工作区的端到端演示 MVP**。产品使用带阶段导航、当前工作区和可收起证据 / 上下文面板的单任务工作台；聊天记录不作为业务 Current Truth。名称 / 品类 / 推广目标用于创建任务，满足 DEC-026 的最小事实资料后运行 Fact Stage；真实阻塞进入 Needs Input，并显示由当前阻断派生的有限结构化行动请求，非阻断差异继续但显式说明限制。资料或上游内容变化先展示影响范围，由用户确认后局部重跑。

权威定位、范围和交互边界见 [DEC-042](docs/decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md)、[DEC-041](docs/decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md)、[DEC-044](docs/decisions/dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)、[DEC-045](docs/decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md)、[DEC-046](docs/decisions/dec-046-review-brief-and-export-product-contract.md)、[DEC-047](docs/decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)、[DEC-048](docs/decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) 与 [DEC-057～062](docs/decisions/decision-log.md)。生产 Workflow / LLM Runtime 与 Frontend Architecture 分别见 DEC-049～056。产品与技术契约的权威边界已冻结：最终公共 HTTP、Retrieval、Observability、物理数据生命周期与测试物理载体分别由 RFC-004 / 005 / 007、ARP-08 / Development Plan 和 Testing Strategy 完成；Product Specification 已于 2026-08-07 整体闭合。该接受不代表实现授权。

---

## 已确认的产品与架构基础

- 平台中立核心，小红书作为首个演示 Adapter；
- 一个统一 Ecommerce Agent，主流程不采用 Multi-Agent 或 LLM Supervisor；
- LangGraph StateGraph 承担确定性工作流编排，业务 Current Truth 与 Checkpoint 分离；
- 4 个 Core Skills：Product Intake & Fact Extraction、Customer Insight Analysis、Product Positioning、Marketing Brief Generation；
- 1 个 Xiaohongshu Brief Mapping Adapter；
- Review Package、Approved Strategy、平台中立 Marketing Brief 与 Xiaohongshu Brief 使用固定产品语义组；正式对象使用不可变 Domain Version，Review Draft 使用单调递增 revision，导出冻结 Current Truth 快照；
- 决策相关内容从当前上下文渐进展开证据；修改按语义组和编辑意图判断阶段影响；长任务使用阶段时间线和行动导向恢复，不显示虚构百分比；
- 首个演示使用虚构非管制商品“城市通勤双肩包”作为唯一 Anchor SKU，以三个资料变体和一个变更脚本验收；行为硬门禁与人工可用性判断分离，Release Candidate 执行一次真实 Provider 正常任务 Smoke；用户侧导出采用 UTF-8 Markdown，不提供首 Goal 的 PDF / JSON 文件导出；
- 声明完整性采用证据约束：Verified Fact 才能作为 Proof Point，无依据高风险声明不得进入 Current Brief；有诚实替代路径时 Task 继续，不建设通用法律或平台合规引擎；
- 用户资料默认 Task-scoped，可逆移除 / 替换通过版本与失效预览纠错，不等于物理永久删除；首个 Goal 不提供用户侧 Purge UI；
- 固定工作区提供 `/tasks` 最小最近任务入口与稳定深链，不建设搜索、批量、归档、统计或完整运营 Dashboard；
- 按需混合检索、版本化 Source / Fragment / Evidence Link、单一关键 Human Review、阶段失效与局部重跑；
- RFC-001 Repository and Application Architecture、RFC-002 Persistence and Transaction Architecture、RFC-003 LangGraph Runtime and Checkpoint Architecture 与 RFC-006 LLM Runtime and Structured Output 已 Accepted；
- Business Current Truth 的生产持久化栈已由 RFC-002 选定为 PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic；SQLite 不作为持久化验收引擎；
- FND-001～003 已完成，仓库已有 Python 后端 Package、质量工具、架构测试、CI 与 Repository Protection 基础。
- Frontend Architecture P-36～P-41 及整体已接受：`apps/web/` React / Vite SPA、显式状态职责、OpenAPI 生成、一个深 TaskWorkbench、Native / 按需 Radix + CSS Modules、私有交互投影、revision-safe Autosave / Diff、WCAG / Desktop Chrome / Reflow 与 Evidence-driven Performance；依赖尚未安装，前端尚未实现。
- RFC-004 DQ-01～10 已由 DEC-063～066 接受：OpenAPI 3.1 `/api/v1` 是唯一公共 HTTP Contract，查询使用窄 Resource、状态变更使用 typed Command；语义 revision / Idempotency、耐久 Receipt + Run Monitor、窄 Task / Recovery / Review、不可变 Brief Version / Comparison / Markdown Export Snapshot、有限 RFC 9457 Problem Catalog、server-bound fixed Workspace + loopback same-origin transport，以及最终 Operation / Schema / state catalog、有界窗口、additive compatibility、generated-client adoption 与 Contract Tests 已冻结；Final Consistency Review = PASS，用户已于 2026-08-07 明确接受 RFC-004 整体；OpenAPI 与 API 尚未实现。

---

## 当前策划缺口

当前 Gate 顺序已由用户于 2026-08-07 明确确认为：**产品规格闭合 → RFC-004 → RFC-005 → RFC-007**。Product Specification 与 RFC-004 均已整体接受；PR #55 获准合并且 Issue #54 获准关闭。当前进入 RFC-005 Source Processing and Retrieval Architecture 策划 Gate；RFC-005 / 007 仍为 `PROPOSED`，未接受 Proposal 不得写成实现事实。

- Persona / JTBD 的后续研究证据；RFC-004 主协议和 OpenAPI closure 已由 DEC-063～066 冻结并整体接受；
- RFC-005 Source / Retrieval、RFC-007 Observability；
- ARP-02 / 03 / 09 完整 Artifact、ARP-05～08、TS-01～TS-05 Charter；
- MVP Development Plan、Testing Strategy 的技术层补全与长期 Goal 最终文本。

以上缺口必须在业务实现前闭合。模型运行基线已由 DEC-052～054 / RFC-006 冻结，Frontend 产品 / Module / 交互 / 质量边界已由 DEC-055～056 冻结；公共 API 与最终 Schema 仍未完成。

## Wave 1 Readiness 状态

- ARP-01、ARP-04、ARP-10：完整 Artifact 已 Accepted；
- ARP-02、ARP-03、ARP-09：仅 TS-01 Minimum Slice 已 Accepted，完整 Artifact 仍待扩展；
- PR #28 已合并，Issue #27 已关闭；该合并不授权 Spike 执行或业务实现。

---

## 协作方式

| 角色 | 职责 |
|------|------|
| 用户 | Decision / RFC / 范围 / 高风险操作 / Goal 激活的最终决策人 |
| GPT-5.6 Sol `xhigh` | `ORCHESTRATOR_REVIEWER`：策划、架构、任务合同、调度、复杂问题与独立 Review |
| GPT-5.6 Luna `max` | `IMPLEMENTER`：Goal 激活后按冻结规格和单一 Issue 完成首选代码实现 |
| GPT-5.6 Terra `xhigh` | `AUXILIARY_IMPLEMENTER`：调查、测试和边界明确的实现；Luna 不可用时可显式回退 |

实现 Agent 不得最终批准或合并自己的 PR；模型回退必须记录实际模型且不降低测试、Review 或验收要求。详见 [AGENTS.md](AGENTS.md)、[DEC-043](docs/decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md) 与 [Collaboration Model](docs/governance/collaboration-model.md)。

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
| `docs/development/` | Development | CI 治理、测试策略与后续开发计划 |
| `docs/goals/` | Goal | 待接受或已激活的长期执行计划 |
| `prompts/` | — | 人机协作提示词模板（如把 ChatGPT 输出交接给 Claude） |

> Current Truth 中只允许写入 Accepted 内容；Assumption、Proposal 与 Open Question 必须显式标注。

---

## 开发状态

**CONDITIONALLY READY（规划范围）** — Foundation、RFC-001～004、RFC-006 与 Frontend Architecture 已完成，但业务实现仍未授权。必须完成 RFC-005 / 007、Readiness 规划包、测试策略、Goal 文本和最终一致性 Review，并由用户明确批准“进入 Goal 执行阶段”后，才可开始长期开发。详见 [Implementation Readiness](docs/handoffs/implementation-readiness.md) 与 [AGENTS.md](AGENTS.md)。
