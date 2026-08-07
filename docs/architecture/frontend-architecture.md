# Frontend Architecture

> **Status: ACCEPTED PRE-DEVELOPMENT CURRENT TRUTH — P-36～P-41 accepted; Final Consistency Review passed; Frontend Architecture overall accepted; public HTTP contract and implementation pending**
> **Authority:** [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md) · [DEC-056](../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md) · product inputs [DEC-059](../decisions/dec-059-targeted-needs-input-action-request-model.md) · [DEC-060](../decisions/dec-060-evidence-bound-claim-integrity-and-proportional-compliance-boundary.md) · [DEC-061](../decisions/dec-061-task-scoped-private-material-and-reversible-removal.md) · [DEC-062](../decisions/dec-062-minimal-recent-task-index-and-stable-deep-links.md)

本文记录已整体接受的 Frontend Architecture；P-36～P-41 已逐项接受，Final Consistency Review 已通过，用户于 2026-08-07 明确接受整体。最终 HTTP Resource / 字段 / 状态 / 错误 / revision / 幂等 / Conflict / Pagination / 下载协议、精确依赖版本、实现与运行证据仍未完成，不得从本文空白处推断实现事实。整体接受不授权依赖安装或实现。

## 1. Application Shape

- 唯一前端根：`apps/web/`（RFC-001）。
- Runtime：React 19 + TypeScript + Vite 8 的纯浏览器 SPA。
- Routing：React Router Declarative Mode；外层拥有 `/tasks` 最小最近任务入口、`/tasks/new` 与稳定 Task / Stage / Panel 位置。
- Backend：浏览器只访问同源 API Base Path；开发期由 Vite Proxy 转发到独立 Python API。
- 不进入首个 Goal：SSR、React Server Components、React Router Framework Mode、Next.js、Node Production API Server。

精确 Patch、实施时 Node Active LTS 兼容组合与 Lockfile 由实施 Issue 根据官方兼容性证据固定，不得改变上述 Major-line 与职责边界。

## 2. State Ownership

| State class | Owner | Rule |
|---|---|---|
| Task Summary / Task / Run / Source / Review / Brief 远程资源 | TanStack Query v5 + Backend | 后端是 Current Truth；Query 管理 Cache、Mutation、失效与自适应轮询；最近任务列表不成为第二套状态 |
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
- 最小 Browser 路径覆盖 `/tasks` 空状态、创建 / 最近任务返回稳定深链、TaskWorkbench 闭环与暂时读取失败；不建立搜索、分页、批量或 Dashboard 测试矩阵。
- Determinism：Playwright 使用本地确定性 API / Model Substitute；普通前端测试不得访问真实 Provider。

首个 Goal 不建设通用 MSW 平台、每 PR Firefox / WebKit 矩阵或 Visual Regression 平台。若未来发布目标或代表性缺陷需要这些能力，必须提交独立提案。

## 5. TaskWorkbench Module and Visual Boundary

- `app` 层只负责 Composition、Provider、`/tasks` 最小 Task Index、`/tasks/new` 与稳定 Task Route 的匹配和 Task Identity 提取。
- Task Index 只显示 RFC-004 提供的名称 / 临时名称、品类、当前阶段或等待状态、最近更新时间和主要下一步 Capability；不通过 Cache 残留或文案猜测终态，不增加搜索、批量、归档、统计或 Dashboard Module。
- 一个深 `TaskWorkbench Module` 负责 Task 内 Stage / Panel 位置的校验 / 规范化与 Active Workspace 投影；Router 不学习 Upload、Start、Resume、Review、Rerun 或 Export 的逐动作回调。
- Workbench 私有 Module 固定为 Intake、Progress / Recovery、Review、Results / Export、Evidence / Context；它们消费私有 `WorkbenchProjection`、产生语义化 `WorkbenchIntent`，不直接消费 HTTP DTO 或互相导入 Implementation。
- Remote Seam 只有生成 Client 驱动的 Typed HTTP Adapter 与固定资料包 / 变更脚本驱动的 Deterministic Test Adapter；TanStack Query 包装该 Seam。
- 首个 Goal 不建设 Contribution Registry、动态插件、任意 Slot / Hook / Middleware 或每 Stage 独立数据架构。

UI 与 Styling：

- 优先原生语义 HTML；只对 Dialog、Alert Dialog、Popover、Tabs、Tooltip、Collapsible 等复杂交互按需使用兼容 React 19 的 Radix Primitives。
- Styling 使用 CSS Modules + 少量语义 CSS Custom Properties；不引入 Tailwind、CSS-in-JS Runtime 或完整主题框架。
- 视觉是证据优先的信息工作台：稳定 Stage Timeline、清晰 Active Workspace、按需 Evidence Context、一个主要 Accent；禁止 Chat Bubble 主界面、无意义 Card Grid、虚构百分比 / 置信度与只靠颜色表达状态。
- 用户、Source 与 Model 文本默认使用 React Text Rendering，禁止 `dangerouslySetInnerHTML` / Raw HTML。若已接受路径需要 Markdown Preview，关闭 Raw HTML、限制安全 Link Protocol 并覆盖代表性行为测试；不建设无实际边界的泛化 Sanitizer 平台。

## 6. Workbench Projection and Interaction

`WorkbenchProjection` 是由 RFC-004 资源、Query 状态、Mutation、URL 与本地编辑缓冲确定性派生的私有投影，不是第二套后端 FSM 或公共枚举。

产品模式覆盖：

- `intake`
- `running`
- `needs_input`
- `review`
- `invalidation_preview`
- `results`
- `recovery`
- `unavailable`

显示优先级：无成功快照且首次读取明确失败 / Task 不存在 → Unavailable；当前写入 Conflict / Confirmation → Recovery / Confirmation；Needs Input；Human Review；Invalidation Preview；Active Run；Current Results；其余为 Intake。

- 每次突出一个主要动作；Stage Timeline、明确标记的最后有效结果和少量合法次动作保持可达。
- Action 只能来自 RFC-004 接受的 Capability 与本地 Mutation 状态；未知状态不得被解释为写权限。业务 Cancel 是显式 Intent，浏览器 Abort 只取消等待。
- 已有成功快照但暂时刷新失败时保持原模式并显示 `stale + retry`；依赖新鲜前置条件的远程写入暂停，本地缓冲保留。
- Mutation 不乐观制造 Current Truth；成功后统一失效 / 刷新。轮询只在需要远程变化的模式继续，并在业务等待、审核、终态或明确错误时停止。
- Field Error 紧邻字段，单文件拒绝留在文件行，Needs Input / Review / Invalidation 是正常 Workspace；暂时读取失败保留快照、更新时间与重试。Toast 不作为错误、Conflict、未保存或恢复状态的唯一载体。
- Needs Input Workspace 只投影 RFC-004 / 005 提供的当前真实阻断：缺失 / 冲突、影响、来源 / 冲突值、允许动作和恢复范围；非阻断增强资料仍是建议，前端不创建完整问卷、自由聊天或虚构恢复能力。
- Claim Integrity 只投影 RFC-004 / 005 提供的 Fact / Claim / Proof Point、Prohibited Claim、风险、限制与合法动作。有诚实替代时只阻断相关声明进入 Current Brief；前端不得把 QC / Human Review 呈现为法律或平台审核保证，也不创建通用 Compliance Dashboard。
- Source 移除 / 替换使用既有 Invalidation Preview 与 Confirmation；界面必须区分“从当前 Task 有效资料集移除”和“物理永久删除”。首个 Goal 不显示 Purge / 永久清除能力。

### 6.1 Revision-safe Review Draft

- 短空闲 Debounce 的实施起始值为 1 秒，同时最多一个 Save Mutation。
- In-flight Save 期间只排队最新缓冲；前一 Save 成功后使用其返回的新 revision 保存最新缓冲，不回放中间快照。
- 显示 `saving / saved / unsaved / conflict`；失败保留缓冲和持久 `unsaved`，支持手动重试，不无限重试。
- 歧义自由文本先确认编辑意图，再进入相应 Save Queue；未确认内容保持本地未保存。
- Submit 等待所有 In-flight Save 与最新缓冲 Flush，只使用最后成功 Flush 返回的新 revision；Save / Flush 失败、Conflict 或编辑意图未确认时阻止 Submit。
- Stale / Superseded 保留本地缓冲、刷新权威 Draft、按语义组比较，由用户重新应用或放弃；禁止自动 Merge / 覆盖 / 提交。
- Diff 权威单位为语义组 + Field Path + Before / After + Model / User Origin + Object Version；词 / 行 Diff 只是长文本视觉辅助，LLM 不作编辑意图最终 Gate。
- 1 秒可在实施 Issue 中依据真实表单证据调整并记录，但不得改变串行保存、revision 链和 Submit 阻断语义。

## 7. Accessibility, Browser and Responsive Boundary

- WCAG 2.2 A / AA 是设计与验证基线，但不宣称未经完整审计的法律合规认证。
- 使用语义化 HTML、完整 Label / Description、键盘导航、可见 Focus、合理 Focus 进入 / 返回、非颜色唯一状态、`prefers-reduced-motion` 和必要的异步 Announcement。
- 关键 E2E 做少量代表性 `@axe-core/playwright` A / AA 检查；人工验证键盘主路径、Dialog / Drawer Focus、动态 Announcement、200% Text Resize，以及等价 `320 CSS px` / 400% Zoom 的关键路径 Reflow。
- 正式支持当前稳定 Desktop Chrome；Playwright Chromium 是硬 Gate，Release Candidate 在实际 Chrome 人工 Smoke。Edge / Firefox / Safari 为 Best-effort。
- 主要 Viewport 为 `1280×800`；`1024×768` 保持多区布局或可收起 Context；`768×1024` 使用单列 Active Workspace 和可访问折叠 / Sheet。
- 等价 `320 CSS px` 只验证桌面 Chrome 高缩放 Reflow，不构成手机设备、触控手势或手机专用布局支持。
- 页面级不得横向滚动；宽表或长 Locator 可在自身 Region 滚动。证据、历史、长 Diff 按需加载；评论 / Evidence 不得无界抓取或一次渲染全部记录。

## 8. Evidence-driven Performance

- 首个完整纵向切片建立固定本地 Profile，记录 Shell 可见、Task Hydration、表单输入、Stage 切换、轮询更新与 Evidence / Diff 打开的可观察体验；Release Candidate 在同一 Profile 复测。
- 性能采用 Measure → Identify → Fix → Verify；取得基线前不把 Core Web Vitals、Lighthouse 总分、Bundle KB 或固定毫秒设为自动 Gate。
- 输入卡顿 / 丢失、轮询整页闪烁、无界 Fetch / Render、Focus 丢失、Evidence 打开阻塞主操作是 Blocking Finding；先 Profile 再优化，不预先散布 Memoization 或通用虚拟化。

## 9. Local Commands

- `npm run dev`：前端开发入口，严格端口 + 同源 API Development Proxy。
- `npm run build`：可发布静态构建入口。
- `npm run preview`：只用于本地构建预览。

完整数据库 / API / Worker / Frontend 一键启动命令由 Development Plan 在 RFC-004 / 005 / 007 后冻结，但必须复用这些前端标准脚本并正确回收子进程。

## 10. Open Questions

- RFC-004：最终 HTTP Resource / Command / Error / Conflict，以及最小 Task List / Summary / Capability、Claim Risk 与 Source Remove / Replace 公共契约。
- RFC-005：Source / Evidence Pagination 与 Retrieval Contract。
- Development Plan：精确依赖版本、本地进程编排、CI Job 分组和一键启动。
- Testing Strategy：Fixture 实例、最终浏览器 E2E 步骤 / 证据格式与 RC 运行手册。

## Authorization Boundary

本规格不表示前端已经实现，也不授权依赖安装、脚手架、组件、样式、Client、测试、CI、RFC 实现、Technical Spike 或 Goal 激活。
