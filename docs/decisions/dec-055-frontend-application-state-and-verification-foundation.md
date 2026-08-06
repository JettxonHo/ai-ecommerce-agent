# DEC-055：采用 React / Vite SPA、显式前端状态所有权与适度浏览器验证

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-06
- **Decision Type:** Frontend Architecture / State Ownership / Contract Generation / Verification
- **Source:** Session-003；用户明确确认推荐组合 `P-36A + P-37A + P-38A`
- **Related Issue:** [#50](https://github.com/JettxonHo/ai-ecommerce-agent/issues/50)
- **Related PR:** [#51](https://github.com/JettxonHo/ai-ecommerce-agent/pull/51)（Draft；Frontend Architecture 仍待 P-39～P-41）

## Context

首个 Goal 需要一个本地可复现、受控单工作区的浏览器任务工作台。后端已经确定为独立 Python API / Worker 进程，业务 Current Truth、Review Draft revision、运行与恢复状态均由后端拥有；首个 Goal 没有公开站点、SEO、SSR、账号、多租户或 Node API Server 需求。

前端仍需冻结应用形态、路由模式、远程 / 表单 / URL 状态所有权、OpenAPI 类型生成、验证工具和本地启动接口。选择必须支持长任务轮询、结构化审核、陈旧 revision 拒绝与关键浏览器闭环，同时遵守 DEC-039 的适度校验原则。

## Decision

### 1. React / Vite 纯浏览器 SPA

- 在 RFC-001 已接受的唯一前端根 `apps/web/` 建立 React 19 + TypeScript + Vite 8 SPA。
- 使用 React Router Declarative Mode 表达可链接的 Task / Stage / Panel 位置；Route Loader / Action 不承担业务远程状态。
- 浏览器只访问同源 API Base Path；开发期由 Vite Development Proxy 转发到本地 Python API，构建产物为静态资源。
- 首个 Goal 不采用 SSR、React Server Components、React Router Framework Mode、Next.js App Router 或 Node Production API Server。
- React / Vite Major-line 与能力边界由本决定冻结；精确 Patch、Node 兼容组合和 Lockfile 在实施 Issue 中依据当时官方兼容性证据固定，不得由实现 Agent 临场改变架构。

### 2. 显式状态所有权

- TanStack Query v5 独占 Task、Run、Source、Review、Brief 等远程资源的缓存、Mutation、失效与自适应轮询；轮询必须在相应终态、等待用户、等待审核或错误投影出现时停止，最终状态名由 RFC-004 冻结。
- React Hook Form v7 只拥有尚未保存的输入、补充资料和 Review 表单编辑缓冲。
- 已保存 Review Draft、单调 revision 与跨标签 / 跨会话恢复状态属于后端远程资源，通过 Query / Mutation 同步；前端不得把浏览器内存升级为业务 Current Truth。
- URL Route / Search Params 保存可链接的 Task、Stage 与 Panel 选择；React 局部状态只保存短命视觉状态。
- 首个 Goal 不引入 Redux 或 Zustand。未来只有出现经过证据确认的大量跨页纯客户端状态时，才可另立 Decision。

### 3. OpenAPI 生成链与窄型客户端 Adapter

- RFC-004 产出的已提交 OpenAPI 3.1 Artifact 是 HTTP Contract 的唯一权威。
- `openapi-typescript` 从该 Artifact 生成类型，`openapi-fetch` 提供基于原生 `fetch` 的类型化 Client。
- 生成文件是不可手改的派生产物，随 Contract 变更提交；CI 重新生成并要求工作树无漂移，不创建第二套手写 DTO。
- React Module 不直接调用原始 `fetch`。窄型 Client / Query Adapter 负责请求身份、标准错误归一化和 DTO 到 View Projection 的转换；业务 revision、幂等、Conflict 与错误语义仍由 RFC-004 冻结。
- 前端同步校验只服务即时 UX，后端与公共 Contract 保持最终权威。首个 Goal 不机械复制全部后端 Schema 为 Zod，也不为同项目 API 的每个响应建设通用 Runtime Validation；真正的非类型输入在其实际边界做针对性解析。

### 4. npm、静态检查与浏览器验证

- 使用实施开始时仍处于 Active LTS、且被已接受 Vite Major 官方支持的 Node 版本，配套 npm 与提交的 `package-lock.json`；不引入 pnpm Workspace、Yarn 或 Bun。
- 前端 PR 基线为 Prettier Format Check、ESLint、`tsc --noEmit`、Vitest + React Testing Library / `user-event` 的 Unit / Module / State Transition Tests、类型化 Client Contract Tests 与 Vite Production Build。
- Playwright Chromium 覆盖关键浏览器纵向切片；相关前端 PR 运行受影响的关键 E2E，Release Candidate 运行完整固定 Browser E2E。
- Firefox / WebKit、Visual Regression 与额外浏览器矩阵只有出现明确发布目标或代表性缺陷时才可另行提案，不作为首个 Goal 的机械 Gate。
- Unit / Module Tests 使用注入式 Typed Transport / Fixture；Playwright 使用确定性本地 API / Model Substitute。首个 Goal 不建设通用 MSW 平台，也不允许普通测试访问真实 Provider。

### 5. 本地执行接口

- `npm run dev` 是前端单独启动入口，使用配置中冻结的严格端口和同源 API Development Proxy。
- `npm run build` 是可发布构建入口；`npm run preview` 只验证本地构建产物，不冒充 Production Server。
- 数据库、API、Worker 与 Frontend 的完整一键启动命令由 RFC-004 / 005 / 007 闭合后的 Development Plan 冻结，但必须复用上述前端标准脚本并正确回收子进程。

## Alternatives Rejected

### React Router Framework Mode

若同时采用独立 Query Layer，其 Loader / Action 与远程缓存、Mutation 和长轮询职责重叠；首个 Goal 也不需要额外服务端 / 构建语义，因此不采用。

### Next.js App Router + Static Export

Static Export 无法使用其 Server Features，而当前工作台没有 SEO / SSR 需求；承担 Server / Client Component 与额外缓存语义没有相称收益，因此不采用。

### Redux / RTK Query 或 Router-owned Data Layer

前者会把后端 Current Truth、表单缓冲和短命 UI State集中到一个全局 Store；后者会让长轮询、跨 Panel Cache 与 revision 冲突依附路由生命周期。两者均不如显式所有权组合清晰。

### Browser-first 或 Jest / Cypress 工具组合

Vitest Browser Mode 与 Playwright E2E 会形成两层浏览器职责；Jest 与 Vite 需要维护并行转换配置，Cypress 又增加另一套 Server / E2E 约定。当前没有证据证明这些额外边界能提高首个本地演示的可靠性。

## Consequences

- 浏览器客户端保持浅运行时、深业务投影：路由表达位置，Query Layer 表达远程状态，表单库只表达未保存缓冲，后端仍是业务权威。
- 前后端通过一个 OpenAPI 事实源连接，Contract Drift 可由生成检查发现，不维护手写重复类型。
- 前端具备静态检查、行为测试、Contract、Build 和关键 Chromium E2E，同时不扩大为多浏览器或泛化 Mock 工程。
- 工作台 Module / UI Primitive / Styling、状态与错误投影、自动保存 / Diff、可访问性、浏览器支持、响应式与性能边界仍由 P-39～P-41 冻结。

## Relationships

- **Applies [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 使用代表性浏览器闭环，不建设不相称的多浏览器矩阵、通用 Mock 或重复 Runtime Schema 层。
- **Concretizes [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md)：** 使用已接受的 `apps/web/` 根与 TypeScript Strict / Frontend Quality 基线，不改变 Modular Monolith 和 Python API / Worker 边界。
- **Concretizes [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md) / [DEC-046](dec-046-review-brief-and-export-product-contract.md) / [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：** 为单任务工作台、Review Draft revision、轮询、进度与恢复选择前端状态职责，不改变产品语义或公共状态。
- **Concretizes [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)：** 选择前端确定性测试与关键 Browser E2E 工具，不改变验收包或人工判断。
- **Input to RFC-004：** OpenAPI 3.1 Artifact 必须成为前端生成源；最终资源、字段、状态、错误、revision、幂等与 Conflict 协议仍由 RFC-004 决定。

## Authorization Boundary

本决定：

- 不授权安装 React、Vite、TanStack Query、React Hook Form、OpenAPI 或测试依赖；
- 不授权生成前端脚手架、`package.json`、Lockfile、组件、路由、样式、Client、测试或 CI Workflow；
- 不接受仍待 P-39～P-41 的 Frontend Architecture 整体；
- 不授权 RFC-004 / 005 / 007 实现、TS-01～TS-05 执行、业务实现或 Goal 创建 / 激活。

## Evidence

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-36～P-38 的三组选项、兼容矩阵与官方资料。
- 用户于 2026-08-06 明确回复：“确认推荐组合为 P-36A + P-37A + P-38A。”
- Draft PR [#51](https://github.com/JettxonHo/ai-ecommerce-agent/pull/51) 的 8 项 Required Checks 全部通过；首轮独立审查 Critical = 0、Required = 0、Optional = 0。
