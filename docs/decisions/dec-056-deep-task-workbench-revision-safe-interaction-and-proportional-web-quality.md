# DEC-056：采用深 TaskWorkbench、Revision-safe 交互与适度 Web 质量边界

## Metadata

- **Status:** Accepted — Amended by DEC-062
- **Date:** 2026-08-06
- **Decision Type:** Frontend Architecture / Workbench Module / Interaction Projection / Accessibility / Performance
- **Source:** Session-003；用户明确接受 `P-39A + P-40A + P-41A`
- **Related Issue:** [#50](https://github.com/JettxonHo/ai-ecommerce-agent/issues/50)
- **Related PR:** [#51](https://github.com/JettxonHo/ai-ecommerce-agent/pull/51)（Draft；Final Consistency Review = PASS，Frontend Architecture 整体已于 2026-08-07 接受）
- **Amended By:** [DEC-062](dec-062-minimal-recent-task-index-and-stable-deep-links.md)（外层 Router 增加最小 `/tasks` 最近任务入口；TaskWorkbench 内部 Module 与 Router-thin 原则不变）

## Context

[DEC-055](dec-055-frontend-application-state-and-verification-foundation.md) 已冻结 React / Vite SPA、前端状态所有权、OpenAPI 类型生成与验证基础，但尚未决定工作台 Module、UI Primitive / Styling、交互投影、Review Draft 自动保存、Diff、可访问性、浏览器、响应式与性能边界。

首个 Goal 是本地演示的单任务工作台，不是公开内容站点、插件平台或多终端产品。选择需要把跨阶段 Current Truth、Human Review、失效、恢复和导出复杂度隐藏在深 Module 中，同时支持 DEC-046 / 047 的 revision、编辑意图和恢复语义，并遵守 DEC-039 的适度校验原则。

## Decision

### 1. 一个深 TaskWorkbench Module

- `app` 层只负责 Composition、Provider 和外层 Declarative Router；它拥有 `/tasks/new` 与稳定 Task Route 的匹配和 Task Identity 提取。
- 一个深 `TaskWorkbench Module` 校验 / 规范化 Task 内可链接的 Stage / Panel 位置，并投影 Active Workspace。Router 不学习 Upload、Start、Resume、Review、Rerun 或 Export 的逐动作回调。
- Workbench 内部使用固定私有 Module：Intake、Progress / Recovery、Review、Results / Export、Evidence / Context。它们共同消费私有 `WorkbenchProjection`、产生语义化 `WorkbenchIntent`，不直接消费 HTTP DTO，也不互相导入 Implementation。
- Python API 作为 remote-but-owned 依赖，只设置两个真实 Adapter：生成 Client 驱动的 Typed HTTP Adapter，以及固定资料包 / 变更脚本驱动的 Deterministic Test Adapter。TanStack Query 包装该 Seam 并拥有 Cache、Mutation、失效和轮询。
- 首个 Goal 不建设 Contribution Registry、动态插件、任意 Slot / Hook / Middleware 或每 Stage 独立的数据架构。

### 2. Native-first Primitive 与项目自有样式

- 优先使用语义化原生 HTML；只有 Dialog、Alert Dialog、Popover、Tabs、Tooltip、Collapsible 等原生能力不足的复杂交互，才按需使用兼容 React 19 的 Radix Primitives。
- Styling 使用 CSS Modules + 少量语义 CSS Custom Properties，集中表达 Color、Typography、Spacing、Radius、Elevation、Focus 与 Motion Token；不引入 Tailwind、CSS-in-JS Runtime 或完整主题框架。
- 视觉方向是专业、证据优先的信息工作台：稳定 Stage Timeline、清晰 Active Workspace、按需 Evidence Context、一个主要 Accent；不得使用 Chat Bubble 主界面、无意义 Card Grid、虚构百分比 / 置信度或只靠颜色表达状态。
- 用户、Source 与 Model 提供的文本默认通过 React Text Rendering 展示，禁止 `dangerouslySetInnerHTML` 或 Raw HTML。若已接受路径需要 Markdown Preview，必须关闭 Raw HTML、只允许明确安全的 Link Protocol，并用代表性行为测试覆盖；没有 Raw HTML 边界时不建设泛化 Sanitizer 平台。

### 3. 私有 WorkbenchProjection 与 Capability / Intent

- `WorkbenchProjection` 由 RFC-004 资源、TanStack Query 状态、当前 Mutation、URL 和本地编辑缓冲确定性派生；它不是第二套后端业务状态机或公共状态枚举。
- 产品模式覆盖 `intake`、`running`、`needs_input`、`review`、`invalidation_preview`、`results`、`recovery` 与 `unavailable`。每次突出一个主要动作，同时保留 Stage Timeline、明确标记的最后有效结果和少量合法次动作。
- Action 只能来自 RFC-004 接受的 Resource / Command Capability 与本地 Mutation 状态；未知状态或显示文案不得被用来猜测写操作。业务 Cancel 是显式 Intent，浏览器 Abort 只取消等待。
- 固定显示优先级为：无成功快照且首次读取明确失败 / Task 不存在 → Unavailable；当前写入 Conflict / Confirmation → Recovery / Confirmation；Needs Input；Human Review；Invalidation Preview；Active Run；Current Results；其余为 Intake。
- 已有成功快照但暂时刷新失败时保持原产品模式并显示 `stale + retry`；依赖新鲜前置条件的远程写入暂停到刷新成功，本地编辑缓冲保留。失效结果不得显示为 Current Truth 或导出。
- Query Mutation 不乐观制造 Current Truth；成功后按统一规则失效 / 刷新再投影。轮询只在需要远程变化的模式继续，并在业务等待、审核、终态或明确错误时停止。

### 4. Revision-safe 串行自动保存与结构化 Diff

- Review Draft 使用短空闲 Debounce 自动保存，实施起始值为 1 秒；同时最多一个 Save Mutation。
- In-flight Save 期间继续编辑时只排队最新缓冲；前一 Save 成功后，使用它返回的新 revision 保存最新缓冲，不回放中间快照。
- `saving / saved / unsaved / conflict` 是必须显式呈现的产品语义。自动保存失败时保留缓冲和持久 `unsaved`，提供手动重试，不无限重试或丢弃内容。
- DEC-047 定义的歧义自由文本必须先由用户确认编辑意图，才能进入相应 Save Queue；未确认内容保留为本地未保存缓冲。
- Submit 必须等待 In-flight Save 和最新缓冲 Flush，只使用最后一次成功 Flush 返回的新 revision；Save / Flush 失败、Conflict 或编辑意图未确认时必须阻止 Submit，不得退回旧 revision 提交。
- Stale / Superseded 时保留本地缓冲、刷新权威 Draft、按语义组比较，并由用户重新应用或放弃；不得自动 Merge、覆盖或提交。
- Diff 的权威单位是结构化语义组 + Field Path + Before / After + Model / User Origin + Object Version。词 / 行 Diff 只能作为长文本视觉辅助；LLM 不替用户作编辑意图 Gate。
- 1 秒是可由真实表单体验证据在实施 Issue 中调整并记录的起始配置；不得因此改变串行保存、revision 链或 Submit 阻断语义，也无需为纯调参另立架构 Decision。

### 5. 错误与恢复表现

- Field Error 紧邻字段，单文件拒绝留在文件行；Needs Input、Review 和 Invalidation 是正常 Workspace，不进入通用错误页。
- 暂时读取失败保留最后成功快照、更新时间和手动重试；不可恢复 UI Error 使用 Route Error Boundary。
- Toast 只用于非关键短暂确认，不作为错误、Conflict、未保存或恢复状态的唯一载体。

### 6. WCAG、浏览器与响应式边界

- WCAG 2.2 A / AA 是首个 Goal Workbench 状态的设计与验证基线，但不宣称未经完整审计的法律合规认证。
- 使用语义化 HTML、完整 Label / Description、键盘导航、可见 Focus、合理 Focus 进入 / 返回、非颜色唯一状态、`prefers-reduced-motion` 与必要的异步状态 Announcement。
- 关键 Browser E2E 使用少量代表性 `@axe-core/playwright` A / AA 检查；同时人工验证完整键盘主路径、Dialog / Drawer Focus、动态 Announcement、200% Text Resize，以及等价 `320 CSS px` / 400% Zoom 的关键路径 Reflow。自动扫描不替代人工判断，也不建立全页面扫描矩阵。
- 正式支持目标是当前稳定 Desktop Chrome；Playwright Chromium 是硬 Gate，Release Candidate 在实际 Chrome 人工 Smoke。Edge / Firefox / Safari 为 Best-effort，不作支持声明或阻塞 Gate。
- `1280×800` 是主要桌面目标；`1024×768` 保持完整多区布局或可收起 Context；`768×1024` 使用单列 Active Workspace，并让 Stage Navigation / Evidence Context 成为可访问折叠区或 Sheet。
- 等价 `320 CSS px` 只验证支持桌面 Chrome 高缩放下的 Reflow，不构成手机设备、触控手势或手机专用布局支持。手机专用优化不进入首个 Goal。
- 页面级不得横向滚动；宽表或长 Locator 可在自身 Region 内滚动。证据、历史与长 Diff 按需加载；评论 / Evidence 列表不得无界抓取或一次渲染全部记录，Pagination Contract 仍由 RFC-004 / 005 冻结。

### 7. Evidence-driven Performance

- 性能遵循 Measure → Identify → Fix → Verify。首个完整纵向切片建立固定本地 Profile 基线，记录 Shell 可见、Task Hydration、表单输入、Stage 切换、轮询更新和 Evidence / Diff 打开的用户可观察体验；Release Candidate 在同一 Profile 复测并记录差异理由。
- 在获得实现基线前，不把公共网站 Core Web Vitals、Lighthouse 总分、Bundle KB 或固定毫秒设为自动 Goal Gate。
- 可观察的输入卡顿 / 丢失、轮询导致整页闪烁、无界 Fetch / Render、Focus 丢失、Evidence 打开阻塞主操作是 Blocking Finding；必须先 Profile 再优化，不预先散布 `memo` / `useMemo` 或通用虚拟化。

## Alternatives Rejected

### Static Contribution Registry + shadcn/ui / Tailwind

它更易增加未来 Stage / Panel，但当前固定工作台没有证据支持 Registry、Contribution Taxonomy、排序、生成组件与内部插件框架成本。

### Route-first Stage Pages + Material UI

它能快速获得完整组件，但会让 Current Truth、Evidence、Review revision、恢复和导出规则散落到 Route，并引入与项目视觉不相称的完整主题 / Runtime Styling 约束。

### XState Client Statechart

客户端显式 Statechart 适合由客户端拥有的复杂长流程；本项目业务状态和转换已由后端 Domain / Workflow / Runtime 拥有，再建 Statechart 会复制状态并增加 Query / Actor 同步复杂度。

### Route-local Conditions + Explicit Save + Toast

初期直接，但会分散状态优先级、轮询、未保存、Conflict、最后有效结果和恢复规则，且通用文本 Diff / Toast 无法承载版本化业务语义。

### Full Browser / Mobile / Automated Compliance Matrix

Chrome、Edge、Firefox、Safari、手机、多浏览器 E2E、全状态 Axe、Visual Regression 与 Lighthouse 数字预算明显扩大首个本地演示范围，自动扫描仍不能证明完整可访问性。

### Desktop Chromium Visual-only

只做桌面视觉检查会遗漏审核、Drawer、错误恢复和长表单的键盘 / Focus / Reflow 问题，低于已接受的人工可用性要求。

## Consequences

- Workbench 对 Router 暴露小 Interface，将远程状态、revision、失效、恢复与导出复杂度集中在一个深 Module 内。
- 视觉 Primitive、业务投影和 HTTP Adapter 各自保持 Locality；不会提前建设插件平台或完整设计系统。
- 自动保存与 Submit 使用可验证的 revision 顺序，避免旧 revision 提交或静默覆盖。
- 质量边界覆盖真实工作台风险，同时不扩张为多浏览器、手机或机械性能评分平台。
- RFC-004 仍须冻结最终 Resource、字段、状态、错误、revision、幂等、Conflict 与下载协议；RFC-005 仍须冻结 Pagination / Retrieval 相关契约。

## Relationships

- **Concretizes [DEC-055](dec-055-frontend-application-state-and-verification-foundation.md)：** 完成其留给 P-39～P-41 的 Module、交互与质量边界。
- **Concretizes [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)：** 用深 TaskWorkbench 和单一主要动作承载稳定任务上下文、Needs Input 与确认式局部重跑。
- **Concretizes [DEC-046](dec-046-review-brief-and-export-product-contract.md)：** 冻结 Review Draft 自动保存的产品侧顺序和 revision-safe Submit，不冻结传输字段或数据库并发实现。
- **Concretizes [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：** 冻结语义组 Diff、编辑意图、证据 / 错误表现与前端恢复投影。
- **Applies [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 使用代表性可访问性、浏览器与性能证据，不建设不相称的矩阵或机械评分器。
- **Input to RFC-004 / RFC-005：** 公共 Capability、状态、错误、Conflict、Pagination 和下载契约必须支持本决定，但仍由各 RFC 定义。

## Authorization Boundary

本决定：

- 不授权安装 Radix、axe 或其他前端依赖；
- 不授权生成前端脚手架、组件、样式、Client、测试、CI Workflow 或业务代码；
- 不冻结 RFC-004 / 005 / 007 的公共字段、路径、枚举、错误码、Pagination 或运维参数；
- 本决定形成时不授权 Technical Spike、Frontend Implementation、业务实现、PR 合并或 Goal 创建 / 激活；用户于 2026-08-07 接受 Frontend Architecture 整体后，PR #51 可在最新提交的 Required Checks 全部通过且独立五轴 Review 无阻塞 Finding 时合并，但仍不授权实现、Spike 或 Goal 创建 / 激活。

## Evidence

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-39～P-41 的备选方案、权衡、推荐与 Primary Sources。
- 用户于 2026-08-06 明确回复：“接受 P-39A、P-40A、P-41A”。
- 用户于 2026-08-07 在 Final Consistency Review 通过后明确回复：“接受 Frontend Architecture 整体”。
- 接受前独立五轴 Review 对提案给出 Critical = 0、Required = 0、Optional = 0；Draft PR #51 的上一归档提交 8 项 Required Checks 全部通过。
