# DEC-082：本地单用户行动工作台与 Kimi 前端路由

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-19
- **Decision Type:** Product / Frontend Experience / Agent Routing
- **Source:** [Session-007](../sessions/session-007-local-single-user-product-and-frontend-design.md)；用户明确确认 Direction A 的具体布局基线
- **Issue:** [#291](https://github.com/JettxonHo/ai-ecommerce-agent/issues/291)
- **Concretizes:** [DEC-055](dec-055-frontend-application-state-and-verification-foundation.md)、[DEC-056](dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md)、[DEC-062](dec-062-minimal-recent-task-index-and-stable-deep-links.md)
- **Narrowly amends:** [DEC-071](dec-071-luna-worker-exclusive-implementation-routing.md)、[DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md) 的前端设计与实现路由
- **Preserves:** [DEC-078](dec-078-mvp0-fast-lane-execution-rebaseline.md)、[DEC-081](dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) 与 MVP-0 Fast Lane `GOAL_BLOCKED`

## Context

FL-1 已证明固定本地工作区中的 deterministic browser-to-backend loop，但当前 Web 仍主要表现为实现纵向闭环所需的功能壳。下一步产品化需要先明确一个可辨认的本地单用户工作界面，而不是继续扩展 Dashboard、运营后台或聊天式 Agent。

DEC-055 / 056 已冻结 React / Vite、状态所有权、深 TaskWorkbench、CSS Modules、按需 Radix、可访问性与验证边界；DEC-062 已冻结 `/tasks` 最近任务入口与稳定深链。它们没有把页面层级、行动首页、上下文栏宽度、Review / Results 的信息表达或视觉语言具体化。

用户于 2026-08-19 明确确认 Direction A：先交付固定本地单用户产品，并采用“运营编辑部 / 策略桌”式行动工作台。用户同时明确允许本机 Kimi Code + Kimi K3 在后续精确前端合同下参与前端设计与实现。该许可需要与既有 Luna / Terra 路由、配置证据、运行时身份和独立 Review Gate 分开记录。

## Decision

### 1. 产品边界

首个产品化目标是**固定本地工作区中的单用户产品**：无登录、无租户切换、无公开部署。后端 Current Truth、现有 Task / revision / idempotency / same-origin / safe Markdown 边界继续有效。

`/tasks` 是行动首页，不是 Dashboard。它优先回答“现在应该处理哪件事”，提供创建 Task、恢复一个主要进行中 Task、查看少量最近 Task 与进入稳定深链的路径。首个产品化切片不加入图表、全局搜索、高级筛选、批量操作、巨型导航、销售 / 订单 / 物流 / 支付模块。

### 2. Action Workbench 布局

稳定 Task 深链中的工作台采用：

- 中文五阶段进度轨道：资料整理 → 用户洞察 → 商品定位 → 营销 Brief → 小红书 Brief；
- 一个当前 Active Workspace，任何时刻突出一个主要动作；
- 一个可折叠的 Context Rail，展开宽度为 `320–360px`，承载证据、来源、限制、风险与技术细节；
- 结构化 Review，以可决定的语义组、证据 / 限制、修改与确认操作为中心；
- 行动导向 Results，分别提供 Marketing Brief 与 Xiaohongshu Brief 视图、版本 / 限制摘要和 Markdown 导出；
- 原始 JSON 只位于明确标记的“技术细节”之后，不作为默认产品界面。

AI 以阶段进度、正在处理的上下文、结果来源、限制和下一步动作出现，不采用 chat-first 或聊天气泡主界面。

### 3. 视觉语言

视觉方向固定为中文优先的“运营编辑部 / 策略桌”：温暖中性色作为主要页面底色，墨色 / 深海军蓝用于文字与结构层级，只使用一个低饱和松绿 / 青绿色作为行动和状态强调色。界面依靠排版、间距、分组、语义状态与稳定工作区建立层级，不使用装饰性图表、泛化卡片墙、渐变式 AI 光效或伪造百分比。

重要前端设计必须使用适用的 taste skills，并在实施 Issue 中保留设计方向、约束、状态与代表性视觉验收证据。该要求不改变既有 React 19 + TypeScript + Vite 8、CSS Modules、原生语义 HTML / 按需 Radix、generated client、same-origin 和安全 Markdown 技术边界。

### 4. Kimi 前端专用例外

本机 Kimi Code + Kimi K3 可以在**用户已接受的精确前端设计或实现合同**下承担前端设计与前端实现。这是 DEC-071 / 072 的窄例外，适用范围只包括授权合同内的前端文件与视觉 / 交互工作。

- 该例外不是 `luna-worker` 不可用时的自动回退，也不是 Terra 的替代路由先例；
- 请求的 Kimi CLI / alias / model 配置证据与实际运行时身份必须分开记录；未独立暴露运行时模型时只能记录 `UNVERIFIED_RUNTIME_MODEL`；
- Kimi 产生的变更不能自我批准或合并；Sol `ORCHESTRATOR_REVIEWER` 负责独立五轴 Review 与合并判断；
- 每次 Kimi 调用仍需位于明确的 Issue / Task Contract 内；本 Decision 与 Issue #291 不授权任何 Kimi model call；
- 该例外不授权后端、Provider runtime、Secret、PostgreSQL、migration、OpenAPI、公开部署、认证、多租户或产品范围扩展。

### 5. 下一步 Gate

DEC-082 只冻结产品与前端方向。下一步必须是一个独立设计 Issue：使用适用 taste skills 形成可审阅的 `/tasks` 与 TaskWorkbench 关键状态设计、设计系统约束和验收证据。设计被明确接受后，才可创建独立实现 Issue。

Fast Lane Goal 继续保持 `GOAL_BLOCKED`。本决定不创建 DEC-081 Phase B、不修复 Provider 路径、不授权新的 Provider run，也不把前端产品化写成完整 Goal 接受。

## Alternatives Considered

### 通用运营 Dashboard

不采用。图表、搜索、筛选、批量、跨模块指标与宽导航会把当前单任务决策工作扩成后台产品，并稀释下一步行动。

### Chat-first Agent

不采用。聊天记录不应成为业务 Current Truth、阶段导航或 Review 载体；AI 应嵌入上下文和进度，而不是成为界面信息架构。

### 移动端优先或同步构建多端产品

不采用。当前产品先服务本地 Desktop Chrome 单用户路径；既有 320 CSS px reflow 仍是可访问性验证，不是手机产品授权。

### Action Workbench（Direction A）

采用。它在不扩展后端和公共契约的前提下，最直接地把已实现的 Task 流程转化为可理解、可恢复、可审核和可导出的运营工作。

## Consequences

- `/tasks` 与 TaskWorkbench 有了可用于设计验收的明确层级，不再依赖“Dashboard”或聊天式默认想象。
- 当前产品仍保持一个固定工作区、一个活跃任务工作面、一个主要动作和少量最近 Task，降低信息架构扩张风险。
- Marketing / Xiaohongshu、Review、Results、Evidence / Context 继续使用既有后端和公共契约；视觉设计不得发明新的业务状态或写权限。
- Kimi 可以在后续精确前端合同中参与，但它的调用、身份和 Diff 仍受显式证据及独立 Review 约束。
- 本决定不包含线框、组件实现、样式代码或 Kimi 调用；这些属于后续独立设计 / 实现 Issue。

## Authorization Boundary

Issue #291 只授权十个文档文件的同步。它不授权代码、测试、配置、依赖、锁文件、migration、OpenAPI、Web 实现、Kimi / Provider 调用、Secret / 环境读取、PostgreSQL / API / live action、DEC-081 Phase B 或 Goal closure。

后续设计 Issue 可以在精确合同内使用适用 taste skills；只有用户或当前 Accepted Decision 明确授权的 Kimi 前端合同才能调用 Kimi。任何超出前端专用边界的模型角色、后端、Provider 或产品范围变化必须重新进入 Decision / Task Contract Gate。
