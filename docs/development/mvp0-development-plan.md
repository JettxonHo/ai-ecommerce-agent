# 快速 MVP-0 Development Plan

> **Status: SUPERSEDED FOR REMAINING MVP-0 EXECUTION BY DEC-078**
>
> Product Specification、Frontend Architecture、RFC-001～007、P-71A～P-73A 与本计划支撑的已完成工作继续有效。[DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md) 和 [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md) 取代本文件的剩余横向里程碑、范围和执行顺序。下文保留为历史计划，不得据此自动创建新 MVP-0 Issue。

## 1. 交付目标

交付一个本地可复现、受控单工作区的端到端演示 MVP：运营人员通过浏览器创建 Task，输入 JSON / 表单文本、TXT、Markdown 或评论 CSV，系统完成事实、洞察、定位、Human Review、通用 Marketing Brief、小红书 Brief 映射与 Markdown 导出。

MVP-0 优先证明闭环、版本 / Current Truth、证据、恢复与人工可用性，不追求完整平台能力。

## 2. 当前基线

- `apps/backend/` 已提供 Python 3.13 Foundation 与 Task Management Task / Run / Stage Domain / Persistence vertical slice（shared values、UoW / PostgreSQL adapter、Alembic `0002_task_management`、application commands 与 CAS），以及 Ruff、Pyright、pytest、Import Linter、Architecture Tests、Build 与 8 项 backend CI Gate；repository-wide strict checks 现为 11 项（backend 8 + Web 3）。
- Spike-001 已证明 LangGraph 小型单线程 SQLite / scripted substitute 路径，但它是 disposable evidence，禁止复制进生产。
- `apps/web/` 已由 MVP0-036（PR #104，merge `adcc38f`）交付 React 19 + TypeScript + Vite 8 no-API foundation shell、锁定 Node/npm tuple、local scripts 与 deterministic unit / contract / Chromium smoke，并接入独立 Web workflow；authored OpenAPI 与 M1 compatibility / fixture 物理载体已存在。Source / Review / Brief persistence、API、Worker、Workflow Runtime、Model / Retrieval Runtime、业务 Skills、Web 业务页面与演示启动脚本仍由后续 Issues 负责；该 foundation 不调用 API，也不包含 generated client。
- PostgreSQL、同步 SQLAlchemy / Psycopg、Alembic、LangGraph + 同步 `PostgresSaver`、React / TypeScript / Vite、OpenAI Responses 与 MVP-0 Retrieval 范围已经由 Accepted RFC 冻结。

## 3. MVP-0 范围

### In Scope

- fixed workspace、Task 创建 / 最近任务 / 深链；
- JSON / 手工文本、TXT、Markdown、评论 CSV；
- Source / Source Version / Association / Fragment / Locator；
- Direct / Exact / PostgreSQL Lexical Retrieval；
- Task、Run、Stage、Review、Brief、Evidence、Export 的版本与状态协议；
- PostgreSQL Business DB + 独立 Checkpoint DB；
- Durable Work Intent、Lease / Heartbeat / Fencing、Cancel / Resume / Rerun；
- 一个 OpenAI Responses Provider + 同 Port 确定性替身；
- 四个 Core Skills + Xiaohongshu Brief Adapter；
- React Task Workbench、轮询、Needs Input、Human Review 与 Markdown 导出；
- 最小结构化日志、correlation、Runtime Error reference 和 Release Evidence Summary；
- 固定虚构验收包、确定性 E2E 与一次人工 RC Live Smoke。

### Non-goals

- 登录、计费、多租户、多人协作、公开部署；
- 自动网页抓取、主动联网研究、竞品监控；
- OCR、图片理解、扫描 PDF、任意 Office 文件；
- 文本 PDF、Embedding / Semantic / Hybrid、pgvector 实现（MVP-1）；
- 完整正文 / 图片 / 视频生成或自动发布；
- Multi-Agent 产品运行时、Supervisor、多 Provider 容灾；
- OTel Collector、Metrics Backend、Dashboard、Pager、完整 Circuit Breaker；
- 物理永久删除平台、通用合规引擎或泛化安全工程。

## 4. Development Plan 待决方案

### P-71 — Python HTTP Adapter

#### P-71A（推荐）：FastAPI + Uvicorn，authored OpenAPI 为唯一权威

- FastAPI / Uvicorn 只位于 `entrypoints/http` 与 Composition Root；Domain / Application 不 import framework 类型。
- `contracts/openapi/openapi.yaml` 是 RFC-004 定义的唯一权威。实现必须通过 Contract Tests 证明运行时行为与 authored contract 一致；不得让 FastAPI 自动生成结果覆盖权威文件。
- 请求 / 响应 DTO 在 HTTP Adapter 完成校验与项目类型转换；Application 继续使用 framework-neutral Commands / Queries / Results。

优点：OpenAPI / JSON Schema 生态与 typed HTTP 接口匹配，开发速度快；测试与本地 ASGI 服务成熟。FastAPI 官方说明其以 OpenAPI / JSON Schema 为基础并提供可配置的 OpenAPI / 文档端点。

风险：框架默认生成 Schema 可能形成第二权威；通过 authored-contract-first、generated diff Gate、Adapter-only dependency 和关闭不需要的自动文档行为控制。

官方证据：[FastAPI Features](https://fastapi.tiangolo.com/features/) · [Metadata and Docs URLs](https://fastapi.tiangolo.com/tutorial/metadata/)

#### P-71B：Starlette + 手工 DTO / Contract Adapter

优点：轻量、低魔法、ASGI 边界清晰。缺点：请求校验、错误投影、OpenAPI 适配与 typed DTO 需要更多自建代码，不利于快速 MVP。Starlette 官方将其定义为轻量 ASGI framework/toolkit。

官方证据：[Starlette Introduction](https://www.starlette.io/)

#### P-71C：Flask / WSGI

优点：成熟简单。缺点：与当前异步 Run Monitor、未来 ASGI 生态和 typed OpenAPI 适配较弱，仍需额外 Contract plumbing。

**Recommendation:** P-71A。该决定选择 Adapter 框架，不改变 RFC-004 公共契约权威。

### P-72 — 本地可复现栈

#### P-72A（推荐）：Compose 管理两个 PostgreSQL Database，仓库脚本管理 Host 进程

- `compose.yaml` 只负责一个 PostgreSQL Service，初始化 Business / Checkpoint 两个独立 Database，并配置 readiness healthcheck；不引入 Redis、Queue 或 Observability 容器。
- `scripts/mvp0`（最终名称由实现 Issue 固定）提供 `up / down / reset-demo / verify` 等窄命令：启动 / 检查 PostgreSQL，运行 Migration，再启动 API、Worker 与 Web Host 进程；退出时正确回收子进程。
- 依赖安装保持显式：Backend 使用 `uv sync --locked`，Frontend 使用锁文件安装。启动命令不静默修改锁文件、不下载 Live 数据、不读取生产 Secret。

优点：数据库环境可复现，应用热重载与调试快，容器文件最少；适合本地演示。缺点：Host 需要 Python / uv / Node / npm；由 preflight 给出可操作错误。

Docker 官方说明 Compose 可通过 healthcheck 与 `service_healthy` 管理依赖 readiness；本方案只使用该必要能力，不引入 Compose Develop 平台。

官方证据：[Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/) · [Compose services / healthcheck](https://docs.docker.com/reference/compose-file/services/)

#### P-72B：API / Worker / Web / PostgreSQL 全部 Compose

优点：主机差异少、单命令。缺点：首个 Goal 需要三个额外镜像、构建缓存与开发挂载，显著扩大 Docker 和调试面。

#### P-72C：全部 Host 进程、用户自行安装 PostgreSQL

优点：仓库文件最少。缺点：最难在新环境复现，不满足演示栈一键恢复目标。

**Recommendation:** P-72A。

### P-73 — Worker 进程实现

#### P-73A（推荐）：项目自有同步 Python Poll Worker

- 独立 Python Entrypoint 使用 RFC-003 的 PostgreSQL Work Intent + Poll-and-claim；一次 claim 使用短事务，执行在事务外，提交使用 Lease / Fencing / revision Commit Fence。
- Worker 复用 Application Ports 和 Composition Root，不引入 Celery、RQ、Dramatiq、Redis 或第二调度协议。
- 一个进程可配置有限并发；MVP-0 correctness tests 至少使用两个独立 Worker / connection 证明 ownership，不把进程内锁作为权威。

优点：与已接受的数据库权威调度完全一致，依赖和双重 retry / ack 语义最少。缺点：需要项目维护窄 polling loop 与 shutdown；范围由 RFC-003 / 007 明确限制。

#### P-73B：Celery + Redis

优点：成熟任务生态。缺点：新增 Broker、第二 delivery / retry / ack 权威，与 PostgreSQL Work Intent 重复。

#### P-73C：API 进程内 Background Task

优点：最少进程。缺点：无法证明 Durable Dispatch、进程重启恢复、多 Worker Lease / Fencing，不满足 Accepted RFC。

**Recommendation:** P-73A。

### Proposal 状态

`P-71A / P-72A / P-73A = ACCEPTED`（DEC-074）。实现 Agent不得改变 authored OpenAPI 权威、local stack 拓扑或 Worker 运行模型；相关依赖只在对应有界 Issue 中加入。

## 5. 模块与物理边界

```text
contracts/openapi/                 Authored public HTTP contract
apps/backend/src/ai_ecommerce_agent/
  modules/                         Domain + Application + module public facades
  orchestration/                   LangGraph adapters and runtime coordination
  platform/                        PostgreSQL, model, retrieval, logging adapters
  entrypoints/                     HTTP and worker adapters
  bootstrap/                       Explicit composition roots
apps/backend/tests/                unit / contract / architecture / integration / e2e
apps/web/                          React/Vite no-API foundation shell; generated typed client remains future
tests/fixtures/mvp0/               Repository-level fictional acceptance pack authority
scripts/                           Narrow repeatable local commands
```

若现有 RFC 的最终目录约束给出更精确路径，以其为准。任何 Issue 需要改变这些顶层边界时停止并提交架构冲突。

## 6. 里程碑与依赖

### M0 — Planning and activation

完成 RFC-007、P-71～P-73、Testing Strategy、Goal、Readiness Review 和初始 Issue contracts。完成标准：全部 Proposal / RFC / 文档包被接受，Readiness = `READY FOR MVP-0`。

### M1 — Contract, fixture and compatibility foundation

1. 物理化 authored OpenAPI 3.1 catalog 与 lint / generated-client clean diff；
2. 物理化虚构 Anchor SKU fixture pack 与 expected behavior manifest；
3. P-72A local PostgreSQL service / preflight；
4. TS-01 / TS-03 stop-first bounded compatibility slices：真实 PostgreSQL transaction / multi-worker ownership、LangGraph sync `PostgresSaver` isolation / reconciliation。

失败停止对应下游；不得用 SQLite 或 Spike 代码代替。

### M2 — Domain and persistence vertical foundation

Task / Run / Stage / Source / Version / Evidence / Review / Brief 的最小 Domain、Application Ports、UoW、Migration 与真实 PostgreSQL Integration。优先提交窄纵向不变量，不一次建立空泛平台。

### M3 — Source and deterministic retrieval

完成 JSON / text / TXT / Markdown / CSV 注册与处理、Fragment / Locator、server-derived Scope、Direct / Exact / Lexical、Evidence Validator 与 atomic Formal Evidence。MVP-1 能力保持 unavailable。

### M4 — Workflow, Worker and model runtime

完成 Durable Worker、LangGraph StateGraph / Checkpoint / reconciliation、Cancel / Resume / Rerun / invalidation，以及 scripted model substitute 和 OpenAI Responses Adapter。普通 PR 不执行 Live call。

### M5 — Core business capabilities

逐个实现 Fact、Insight、Positioning、Marketing Brief Skills 与 Xiaohongshu Brief Adapter；每个 Skill 使用冻结的 Profile、Structured Output、Domain Validator、Evidence Link 和行为测试。

### M6 — API and Human Review

按 authored OpenAPI 纵向实现 Task / Source / Run / Recovery / Review / Brief / Export；完成 idempotency、revision conflict、Problem Details 和 generated client adoption。

### M7 — Web Workbench

MVP0-036 已交付 React/Vite no-API foundation shell 与稳定 CI scripts / shell smoke；MVP0-037～042 后续按 Task list → intake → progress / Needs Input → Review → Brief / Export 纵向 Slice 推进；不得在前端模拟服务端终态。

### M8 — Release candidate and final review

执行固定 deterministic Browser E2E、真实 PostgreSQL integration / migration / concurrency、一次 opt-in live model smoke、人工可用性验收、本地新环境复现和文档同步；然后做 Goal 级统一 Review 与最终报告。

## 7. Issue / PR 拆分原则

- 一个 Issue 一个可独立验证结果，一个 Branch / PR；默认 100～300 行实质修改，接近 1000 行或多个目标必须拆分。
- Contract / fixture / infrastructure foundation 先于其消费者；并行只发生在已冻结接口与文件所有权不重叠时。
- 依赖升级、文档迁移、重构、功能与测试平台原则上分开。
- 每个 PR 说明问题、方案、范围、Non-goals、测试、风险、回滚与文档影响。
- 实现由 `luna-worker` 完成；Sol 检查实际 Diff、测试和五轴质量，普通低风险 PR 才可由非实现者合并。

## 8. 测试与完成标准

详细层级见 [testing-strategy.md](testing-strategy.md)。每个 Issue 至少运行受影响的 Format / Lint / Type / Architecture / Unit / Contract / Build；持久化与 Workflow 使用真实 PostgreSQL Integration；Frontend foundation 使用 `format:check` / `lint` / `typecheck` / `test:unit` / `test:contract` / `build` 与 Chromium shell smoke，后续业务 slices 再按影响范围运行 Browser E2E。

里程碑只有在其验收、测试、文档、风险和回滚均闭合后完成。跳过、隐藏或降低 Gate 不属于完成。

## 9. 风险与停止条件

- P-71～P-73 或 RFC-007 未接受；
- authored OpenAPI 与实现 / generated client 冲突；
- TS-01 / TS-03 暴露 transaction、Lease / Fencing、Checkpoint isolation 或 reconciliation 核心缺陷；
- 必须扩大 MVP-0、启用 PDF / Embedding / Semantic、增加认证 / 多租户 / 抓取 / 多 Provider；
- 必须改变 PostgreSQL、LangGraph、OpenAI Provider、React / Vite 或公共契约；
- 数据破坏、不可逆 Migration、真实生产凭证、安全事故或质量 Gate 降级。

触发时停止受影响模块，记录证据并请求用户确认；其他独立范围可继续。

## 10. 接受边界

用户已接受 P-71A / P-72A / P-73A（DEC-074），并整体接受本计划、Testing Strategy、Goal 与 Readiness Review（DEC-075）。PR #59 合并后本计划随 Goal 进入执行状态。
