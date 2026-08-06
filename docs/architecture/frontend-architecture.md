# Frontend Architecture

> **Status: PARTIAL CURRENT TRUTH — application, state ownership, contract generation and verification accepted; P-39～P-41 pending**
> **Authority:** [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md)

本文只记录已经接受的 Frontend Architecture。工作台 Module / UI Primitive / Styling、状态与错误投影、自动保存与 Diff、可访问性、浏览器支持、响应式与性能边界仍是 Open Question，不得从本文空白处推断实现事实。

## 1. Application Shape

- 唯一前端根：`apps/web/`（RFC-001）。
- Runtime：React 19 + TypeScript + Vite 8 的纯浏览器 SPA。
- Routing：React Router Declarative Mode，只表达可链接的 Task / Stage / Panel 位置。
- Backend：浏览器只访问同源 API Base Path；开发期由 Vite Proxy 转发到独立 Python API。
- 不进入首个 Goal：SSR、React Server Components、React Router Framework Mode、Next.js、Node Production API Server。

精确 Patch、实施时 Node Active LTS 兼容组合与 Lockfile 由实施 Issue 根据官方兼容性证据固定，不得改变上述 Major-line 与职责边界。

## 2. State Ownership

| State class | Owner | Rule |
|---|---|---|
| Task / Run / Source / Review / Brief 远程资源 | TanStack Query v5 + Backend | 后端是 Current Truth；Query 管理 Cache、Mutation、失效与自适应轮询 |
| 已保存 Review Draft / revision | Backend remote resource | 支持跨标签 / 跨会话恢复；陈旧保存或提交由后端拒绝 |
| 尚未保存的表单编辑缓冲 | React Hook Form v7 | 只服务当前编辑会话，不得成为业务状态来源 |
| 可链接 Task / Stage / Panel 选择 | URL Route / Search Params | 刷新和深链后可恢复位置，不保存业务内容 |
| 展开、焦点等短命视觉状态 | React local state | 不引入 Redux / Zustand |

轮询终止条件必须来自 RFC-004 接受的状态 / 能力契约及当前 Mutation 状态，前端不得发明业务终态。

## 3. HTTP Contract and Adapter Seam

- RFC-004 的已提交 OpenAPI 3.1 Artifact 是唯一 HTTP Contract Source of Truth。
- `openapi-typescript` 生成不可手改的派生类型；`openapi-fetch` 提供类型化原生 Fetch Client。
- 生成文件随 Contract 变更提交，并由重新生成后的 Clean Diff Gate 检查漂移。
- React Module 不直接使用原始 `fetch`；窄型 Client / Query Adapter 负责传输、标准错误归一化和 DTO → View Projection。
- 前端校验服务即时 UX；后端与公共 Contract 是最终权威。不建立第二套手写 DTO，也不机械复制全部后端 Schema 为 Zod。

最终资源、路径、字段、状态、错误、revision、幂等、Conflict 和下载协议仍由 RFC-004 冻结。

## 4. Verification

- Package：实施时兼容的 Node Active LTS + npm + committed `package-lock.json`。
- Static：Prettier、ESLint、`tsc --noEmit`。
- Behavior：Vitest + React Testing Library + `user-event`。
- Contract：类型化 Client Contract Tests，使用注入式 Typed Transport / Fixture。
- Build：Vite Production Build。
- Browser：Playwright Chromium；相关 PR 跑受影响纵向切片，Release Candidate 跑完整固定 Browser E2E。
- Determinism：Playwright 使用本地确定性 API / Model Substitute；普通前端测试不得访问真实 Provider。

首个 Goal 不建设通用 MSW 平台、每 PR Firefox / WebKit 矩阵或 Visual Regression 平台。若未来发布目标或代表性缺陷需要这些能力，必须提交独立提案。

## 5. Local Commands

- `npm run dev`：前端开发入口，严格端口 + 同源 API Development Proxy。
- `npm run build`：可发布静态构建入口。
- `npm run preview`：只用于本地构建预览。

完整数据库 / API / Worker / Frontend 一键启动命令由 Development Plan 在 RFC-004 / 005 / 007 后冻结，但必须复用这些前端标准脚本并正确回收子进程。

## 6. Open Questions

- P-39：Task Workspace Module、Feature Module、UI Primitive 与 Styling 方案。
- P-40：Interaction Projection、自动保存、语义组 Diff、陈旧 revision、错误与恢复表现。
- P-41：可访问性、支持浏览器、响应式范围和证据驱动性能边界。
- RFC-004：最终 HTTP Resource / Command / Error / Conflict Contract。
- Development Plan：精确版本、本地进程编排、CI Job 分组和一键启动。

## Authorization Boundary

本规格不表示前端已经实现，也不授权依赖安装、脚手架、组件、样式、Client、测试、CI、RFC 实现、Technical Spike 或 Goal 激活。
