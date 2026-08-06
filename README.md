# AI Ecommerce Agent

> **Status: Pre-development Planning · Development = CONDITIONALLY READY**
> 当前只允许产品规格闭合、架构 RFC、Readiness 规划、测试与 Goal 文档工作。Business / Production Implementation、TS-01～TS-05 执行与实际 Goal 均未启动。

---

## 产品定位

AI Ecommerce Agent 是面向中小电商商品与内容运营人员的**证据驱动商品上新策略工作台**，将用户提供的商品与市场资料转化为可审核、可追溯的商品定位分析、平台中立 Marketing Brief 与小红书 Brief 映射。

首个交付目标是**本地可复现、受控单工作区的端到端演示 MVP**。产品使用带阶段导航、当前工作区和可收起证据 / 上下文面板的单任务工作台；聊天记录不作为业务 Current Truth。名称 / 品类 / 推广目标用于创建任务，满足 DEC-026 的最小事实资料后运行 Fact Stage；真实阻塞进入 Needs Input，非阻断差异继续但显式说明限制。资料或上游内容变化先展示影响范围，由用户确认后局部重跑。

权威定位、范围和交互边界见 [DEC-042](docs/decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md)、[DEC-041](docs/decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md)、[DEC-044](docs/decisions/dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)、[DEC-045](docs/decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md)、[DEC-046](docs/decisions/dec-046-review-brief-and-export-product-contract.md)、[DEC-047](docs/decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)、[DEC-048](docs/decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)、[DEC-049](docs/decisions/dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md)、[DEC-050](docs/decisions/dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md) 与 [DEC-051](docs/decisions/dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md)。Review / Brief / 导出语义、渐进式证据、编辑影响、阶段进度、行动导向恢复、代表性验收包和 Markdown-first 用户导出已冻结；生产 Checkpointer、同步持久性、Current-Truth-first 对账、PostgreSQL Durable Dispatch、Fenced Worker Ownership、协作式取消、显式 Compatibility Tuple、七动作 Safe Resume Matrix 与前向恢复证据边界也已冻结。公共字段类型、API Schema、视觉组件、Frontend Architecture、Provider、精确运行时版本，以及 RFC-004～007 仍待后续 Decision Gate，不得从本简介自行推断。

---

## 已确认的产品与架构基础

- 平台中立核心，小红书作为首个演示 Adapter；
- 一个统一 Ecommerce Agent，主流程不采用 Multi-Agent 或 LLM Supervisor；
- LangGraph StateGraph 承担确定性工作流编排，业务 Current Truth 与 Checkpoint 分离；
- 4 个 Core Skills：Product Intake & Fact Extraction、Customer Insight Analysis、Product Positioning、Marketing Brief Generation；
- 1 个 Xiaohongshu Brief Mapping Adapter；
- Review Package、Approved Strategy、平台中立 Marketing Brief 与 Xiaohongshu Brief 使用固定产品语义组；正式对象使用不可变 Domain Version，Review Draft 使用单调递增 revision，导出冻结 Current Truth 快照；
- 决策相关内容从当前上下文渐进展开证据；修改按语义组和编辑意图判断阶段影响；长任务使用阶段时间线和行动导向恢复，不显示虚构百分比；
- 首个演示使用三个固定资料包和一个变更脚本验收；行为硬门禁与人工可用性判断分离，Release Candidate 执行一次真实 Provider 正常任务 Smoke；用户侧导出采用 UTF-8 Markdown，不提供首 Goal 的 PDF / JSON 文件导出；
- 按需混合检索、版本化 Source / Fragment / Evidence Link、单一关键 Human Review、阶段失效与局部重跑；
- RFC-001 Repository and Application Architecture、RFC-002 Persistence and Transaction Architecture 与 RFC-003 LangGraph Runtime and Checkpoint Architecture 已 Accepted；
- Business Current Truth 的生产持久化栈已由 RFC-002 选定为 PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic；SQLite 不作为持久化验收引擎；
- FND-001～003 已完成，仓库已有 Python 后端 Package、质量工具、架构测试、CI 与 Repository Protection 基础。

---

## 当前策划缺口

- 任务工作台的公共字段类型、最终组件 / 视觉布局和 Persona / JTBD 的后续研究证据；输入与冲突已由 DEC-045 冻结，审核 / Brief / 版本已由 DEC-046 冻结，证据 / 编辑 / 进度 / 恢复 / 导出确认已由 DEC-047 冻结，验收包与 Markdown-first 用户导出已由 DEC-048 冻结；
- Frontend Architecture；
- RFC-004 API / Human Review、RFC-005 Source / Retrieval、[RFC-006 LLM Runtime](docs/rfcs/rfc-006-llm-runtime-and-structured-output.md)（Issue #48，`DRAFTING`；P-28～P-30 仍待用户决定）、RFC-007 Observability；
- ARP-02 / 03 / 09 完整 Artifact、ARP-05～08、TS-01～TS-05 Charter；
- MVP Development Plan、Testing Strategy 的技术层补全与长期 Goal 最终文本。

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

**CONDITIONALLY READY（规划范围）** — Foundation 与 RFC-001～003 已完成，但业务实现仍未授权。必须完成 RFC-004～007、Frontend Architecture、Readiness 规划包、测试策略、Goal 文本和最终一致性 Review，并由用户明确批准“进入 Goal 执行阶段”后，才可开始长期开发。详见 [Implementation Readiness](docs/handoffs/implementation-readiness.md) 与 [AGENTS.md](AGENTS.md)。
