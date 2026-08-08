# AI Ecommerce Agent

> **Status: MVP-0 Goal ACTIVE · Development = ACTIVE**
> RFC-001～007、Development Plan、Testing Strategy、MVP-0 Goal 与 Readiness Review 已接受；PR #59 已合并，长期 Goal 正在执行。实现仅限有界 Issues，重大风险继续保留人工 Gate。

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
- RFC-005 已于 2026-08-07 获用户整体接受。DQ-01～10 由 DEC-067～070 支撑：目标 Profile 固定为 OpenAI Embeddings `text-embedding-3-small` / explicit 1536 / float / cosine，Source intake / association / version / Evidence Link 公共目录与有限验证已冻结；快速 MVP-0 先交付 Direct / Exact / PostgreSQL Lexical + JSON / text / TXT / Markdown / CSV，text PDF 与 Embedding / Semantic / Hybrid 后移 MVP-1。Final Consistency Review = PASS；Retrieval 实现尚未授权。

---

## 当前执行入口

开发前 Gate 已闭合：P-68A～P-70A 与 RFC-007 整体由 DEC-073 接受，P-71A～P-73A 由 DEC-074 接受，Development Plan、Testing Strategy、Goal 与 Readiness Review 由 DEC-075 接受。[PR #59](https://github.com/JettxonHo/ai-ecommerce-agent/pull/59) 已合并；Sol 已按 [MVP-0 Goal](docs/goals/end-to-end-demo-mvp0-goal.md) 创建 M1 Issues #63～#67 并开始路由 `luna-worker`。

- 首批执行顺序：authored OpenAPI 与固定 fixture → local PostgreSQL → TS-01 / TS-03 stop-first compatibility slices；
- 每个 Issue 使用独立分支、任务合同、测试和 PR；实现者不得批准或合并自己的变更；
- 高风险 / 不可逆 / 范围或公共契约变化继续请求用户确认。

Persona / JTBD 真实研究与完整 ARP-02 / 03 / 09、ARP-05～08、TS-02 / 04 / 05 已按快速 Gate 后移 MVP-1 / Beta，不阻塞 MVP-0。物理 OpenAPI / Schema、fixtures 与真实 PostgreSQL 证据由 Goal 首批 Issues 实现。

## MVP-0 本地 PostgreSQL 生命周期

MVP0-003 提供一个可复现的本地 PostgreSQL Service。Compose 只启动
`postgres` 这一个 Service；Business 与 Checkpoint 是同一 Service 内的两个独立
Database，并分别使用 `mvp0_business` / `mvp0_checkpoint` demo Role。API、Worker、Web
仍是未来的 host-process 边界，本 Issue 不实现、迁移或自动启动它们。

```bash
cp .env.example .env       # 可选：仅用于 loopback 的 demo 值
./scripts/mvp0/preflight
./scripts/mvp0/up
./scripts/mvp0/status
./scripts/mvp0/verify       # readiness + 两个 Database/Role 隔离检查
./scripts/mvp0/down         # 停止容器，保留本地 volume
./scripts/mvp0/test-static  # 不启动容器的 shell/Compose 拓扑检查
```

`up` 会等待 Compose healthcheck，并幂等确认两个 Database、owner、Role 登录状态和
CONNECT 隔离；不会创建生产 Schema，也不会运行 Migration。若未来要启动 host API /
Worker / Web，先执行 `./scripts/mvp0/preflight --host-processes`，再使用各自 Issue
提供的显式命令。Worker / Checkpointer setup 与 Migration 仍须由受控部署任务负责，
不得在 Worker 启动时隐式迁移。

默认端口为 `127.0.0.1:55432`。可供后续实现使用的本地连接目标是：

```text
Business:   postgresql://mvp0_business:<MVP0_BUSINESS_PASSWORD>@127.0.0.1:55432/ecommerce_business
Checkpoint: postgresql://mvp0_checkpoint:<MVP0_CHECKPOINT_PASSWORD>@127.0.0.1:55432/ecommerce_checkpoint
```

凭证来自 `.env`（默认值只用于本地演示，不是生产 Secret）；正常 `up` 不会静默轮换
已有 Role 密码。修改已初始化环境的 demo 凭证前，应先确认连接方并执行显式的
`./scripts/mvp0/reset-demo --confirm`，因为该命令会删除且只删除固定的
`ai-ecommerce-agent-mvp0-postgres-data` demo volume。`down`、`status` 和 `up` 都不会
删除 volume；reset 没有仓库内备份或自动回滚，恢复依赖操作者自己的备份。

镜像固定为官方 `postgres:16.14-bookworm`，以便在 MVP-0 compatibility slices 中复现；
PostgreSQL 16 仍在官方支持周期内（[PostgreSQL versioning policy](https://www.postgresql.org/support/versioning/)），
镜像标签与官方镜像说明见 [Postgres Official Image](https://hub.docker.com/_/postgres)。
升级 major 或 patch 前必须补充兼容性证据，不得通过环境变量静默替换镜像。

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
| 自定义 Agent `luna-worker`（GPT-5.6 Luna `max`） | `IMPLEMENTER`：Goal 激活后按冻结规格和单一 Issue 完成代码实现 |
| GPT-5.6 Terra `xhigh` | `AUXILIARY_IMPLEMENTER`：仅在用户对具体任务明确许可时参与；不作自动或默认实现回退 |

实现 Agent 不得最终批准或合并自己的 PR。实现线程必须按准确名称创建 `luna-worker`；不可用时停止新的实现任务并报告，不得自动回退 Terra。配置已验证、运行时未暴露时只记 `CONFIG_VERIFIED`。详见 [AGENTS.md](AGENTS.md)、[DEC-071](docs/decisions/dec-071-luna-worker-exclusive-implementation-routing.md)、[DEC-072](docs/decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md) 与 [Collaboration Model](docs/governance/collaboration-model.md)。

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

**CONDITIONALLY READY（规划范围）** — Foundation、Product Specification、RFC-001～006 与 Frontend Architecture 已完成。快速 MVP-0 只需再闭合最小 RFC-007、Development Plan、Testing Strategy、Goal 文本和精简 Readiness Review。完整策划包和重大 Proposal 被接受后，DEC-072 的持续执行授权允许激活 Goal；当前尚未达到该状态。详见 [Implementation Readiness](docs/handoffs/implementation-readiness.md) 与 [AGENTS.md](AGENTS.md)。
