# MVP Scope（最小可行产品范围）

> **Status: ACCEPTED CURRENT TRUTH — Product Specification accepted; DEC-082 local Action Workbench direction synchronized**
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：MVP 核心任务与交付物（DEC-003）、平台与输入输出边界（DEC-004～006）、Human Review / 证据 / 失效重跑（DEC-007～009）、三维评价（DEC-010）、本地演示包络（DEC-041）、行为型成功边界（DEC-042）、单任务工作台与确认式局部重跑（DEC-044）、最小输入、文件限制与冲突分级（DEC-045）、审核 / Brief / 版本 / 导出产品契约（DEC-046）、证据披露、编辑意图、阶段进度和恢复交互（DEC-047）、代表性验收包、行为门禁、人工验收与 Markdown-first 用户导出（DEC-048）、产品 / 技术契约权威边界（DEC-057）、虚构 Anchor SKU 验收策略（DEC-058）、有限结构化 Needs Input 行动请求（DEC-059）、证据约束声明完整性（DEC-060）、Task 范围资料与可逆移除（DEC-061）、最小最近任务入口与稳定深链（DEC-062），以及 Frontend Architecture（DEC-055 / 056）。公共 Schema、Fixture 物理文件与 E2E 证据格式属于下游 RFC / Testing Strategy，不得在产品文档擅自补全。
> **DEC-041 同步：** 首个本地演示只接收结构化表单、文本、TXT / Markdown、文本型 PDF 与评论 CSV；不做 OCR、图片理解或扫描文档。下文 DEC-005 的旧“图片或文字”示例按此最新边界修订。
> **DEC-042 同步：** 产品定位为证据驱动商品上新策略工作台；复合 Persona / JTBD 作为演示期假设；成功以端到端行为与人工可用性判断，不使用机械总分自动接受。
> **DEC-044 同步：** 单任务工作台使用阶段导航、当前工作区和可收起证据 / 上下文面板；最低输入通过即可启动，真实阻塞进入 Needs Input；用户确认失效预览后才局部重跑。
> **DEC-045 同步：** Task 创建需名称 / 临时名称、品类和推广目标；Fact Stage 需核心用途、当前商品来源、有来源核心属性且无阻断性身份冲突；演示默认限制为 20 文件 / 任务、10 MB / 文件、文本 PDF 100 页、评论 CSV 10,000 行。
> **DEC-046 同步：** Review Package / Approved Strategy / Marketing Brief / Xiaohongshu Brief 的产品语义组已冻结；正式对象不覆盖，Review Draft 使用 revision，导出冻结 Current Truth 快照；最终公共字段、revision / Conflict 传输与下载协议由 RFC-004 冻结，物理持久化遵守 RFC-002 并留给 Goal Issue。
> **DEC-047 同步：** 证据在当前上下文渐进展开，修改按语义组和编辑意图判断影响，进度使用阶段时间线，错误提供匹配恢复动作，导出前确认 Current Truth 版本和限制；组件架构与前端投影由 DEC-056 冻结，公共传输 / 导出模板与 Evidence 关系分别由 RFC-004 / 005 冻结。
> **DEC-048 同步：** 首个演示使用三个固定资料包 + 一个变更脚本，行为硬门禁与人工 `PASS / FAIL` 分离；Release Candidate 执行一次真实 Provider 正常任务 Smoke；当前有效 Marketing Brief / Xiaohongshu Brief 使用 UTF-8 Markdown 用户导出，PDF / JSON 文件导出不进入首个 Goal。
> **DEC-057～059 同步：** 产品层只冻结稳定语义与行为；验收包共享虚构“城市通勤双肩包”Anchor SKU；Needs Input 只显示当前真实阻断派生的有限结构化行动请求。
> **DEC-060～062 同步：** 无依据高风险声明优先只阻断进入 Current Brief，有诚实替代时 Task 继续；用户资料默认 Task-scoped，可逆移除 / 替换不等于物理永久删除；固定工作区提供最小最近任务入口与稳定深链，不建设完整运营 Dashboard。
> **DEC-055 / 056 同步：** Frontend 使用 `apps/web/` React / Vite SPA、显式状态所有权与 OpenAPI 生成；一个深 TaskWorkbench 使用 Native / 按需 Radix + CSS Modules、私有 WorkbenchProjection、revision-safe 串行 Autosave / 语义组 Diff，以及 WCAG / Desktop Chrome / Reflow 与 Evidence-driven Performance。最终公共 Resource、字段、状态、错误、Conflict、Pagination 与下载协议仍待 RFC-004 / 005。
> **DEC-082 同步：** 产品化先服务固定本地单用户；`/tasks` 为行动首页，Task 深链采用中文五阶段轨道、一个 Active Workspace 与可折叠 `320–360px` Context Rail。Review / Results 使用产品语义视图，AI 是上下文进度 / 状态而非 chat-first。图表、搜索、筛选、批量、mega-nav、手机产品及销售 / 订单 / 物流 / 支付扩展不进入该切片。

---

## 已确认内容（Confirmed）

> 来源：[DEC-003](../decisions/dec-003-product-launch-positioning-and-marketing-brief.md) + [DEC-004](../decisions/dec-004-platform-neutral-core-xiaohongshu-demo.md) + [DEC-005](../decisions/dec-005-layered-mvp-inputs.md) + [DEC-006](../decisions/dec-006-four-layer-structured-marketing-brief.md) + [DEC-007](../decisions/dec-007-single-review-node-and-exception-pauses.md) + [DEC-008](../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md) + [DEC-009](../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md) + [DEC-010](../decisions/dec-010-three-dimensional-mvp-evaluation-framework.md) + [DEC-041](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md) + [DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) + [DEC-044](../decisions/dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md) + [DEC-045](../decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md) + [DEC-046](../decisions/dec-046-review-brief-and-export-product-contract.md) + [DEC-047](../decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) + [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) + [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md) + [DEC-056](../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md) + [DEC-057](../decisions/dec-057-product-semantics-and-technical-contract-authority-boundary.md) + [DEC-058](../decisions/dec-058-fictional-anchor-sku-acceptance-fixture-strategy.md) + [DEC-059](../decisions/dec-059-targeted-needs-input-action-request-model.md) + [DEC-060](../decisions/dec-060-evidence-bound-claim-integrity-and-proportional-compliance-boundary.md) + [DEC-061](../decisions/dec-061-task-scoped-private-material-and-reversible-removal.md) + [DEC-062](../decisions/dec-062-minimal-recent-task-index-and-stable-deep-links.md)

- **MVP 核心任务：** 商品上新（或正式内容推广前）的定位分析 + 结构化营销 Brief 生成，服务中小电商商家的商品运营与内容运营人员（DEC-002）。
- **产品定位（DEC-042）：** 证据驱动商品上新策略工作台；把用户资料转化为可审核、可追溯的定位分析、平台中立 Marketing Brief 与 Xiaohongshu Brief 映射。
- **核心交付物：** 结构化商品上新营销 Brief。
- **基础任务闭环（方向）：** 提交资料 → 检查完整性 → 提取事实与卖点 → 分析目标用户 → 分析需求 / 动机 / 阻碍 → 形成定位与差异化 → 形成内容方向与营销策略 → 生成 Brief → 质量检查与依据展示。
- **平台范围：** 核心能力**平台中立**；**小红书商品种草** 为首个 MVP 演示场景（DEC-004）。
- **产品逻辑边界：** 通用层（通用定位 + 通用 Brief）为核心；平台适配层将通用 Brief 映射为平台表达，首个适配＝**小红书种草 Brief 模板**。
- **输入分层（DEC-005）：**
  - **Task 创建：** 商品名称或临时工作名称、品类、推广目标；创建后进入稳定任务工作台。
  - **Fact Stage 可运行：** 核心用途、至少一个可用当前商品来源（手动结构化输入可计入）、至少一个有来源核心属性、无阻断性商品身份冲突。
  - **价格 / 当前卖点：** 不是全局硬必填；相关缺失作为限制和建议补充展示。
  - **推荐增强输入：** 用户评论、用户调研、常见用户问题、商品详情页、已有营销内容、品牌定位 / 资料。
  - **可选扩展输入：** 竞品资料、行业报告、平台案例、运营知识文档、历史推广结果、其他。
  - 缺少增强 / 可选输入**不得阻断**基础流程；资料不足须诚实表达。
- **输出主结构（DEC-006）：** MVP 核心输出采用 **事实层 → 洞察层 → 策略层 → 执行层** 四层结构。系统先形成可检查、可追溯的商品分析与营销决策依据，再形成供运营人员使用的执行 Brief；后层内容应能追溯前层依据，**不得**「输入少量信息 → 无依据生成完整营销文案」。**完整小红书标题与正文暂不属于 MVP 核心交付物**（小红书种草 Brief 是执行层的一种平台映射）。
- **人机协作（DEC-007 / 060）：** MVP 采用 Human-in-the-loop——**一个常规强制审核节点**（分析草稿生成后、最终 Brief 前）+ **异常暂停与追问**（资料矛盾 / 关键缺失或确需补充的声明依赖）+ **用户保留最终业务判断权**。常规流程**不要求**每层分别确认；关键事实冲突时系统**不得**自行猜测后继续。无依据高风险声明优先只阻断其进入 Current Brief；移除或降级后仍能形成诚实 Brief 时 Task 继续，只有策略必须依赖且无可信替代表达时才进入 Needs Input。
- **输出可靠性（DEC-008）：** MVP 采用**五类结论标记**（明确事实 / 有证据洞察 / 模型推断 / 待验证假设 / 资料不足）。**事实可追溯**；事实与推断分离；重要洞察保留依据；资料不足时**不得编造**（禁止伪造文档名 / 评论原文 / 引用编号 / 来源）；**用户修改上游事实或关键洞察后，下游依赖内容须重新处理或标记失效**。只展示最终结论、强制逐条原文引用两个方案**未采用但保留为备选**（非永久禁止）。
- **失效与重跑（DEC-009）：** MVP 按**阶段级依赖**（事实 → 洞察 → 策略 → 执行）处理失效：改事实层 → 洞察 / 策略 / 执行失效；改洞察层 → 策略 / 执行失效；改策略层 → 执行失效；直接编辑执行层 Brief 默认不触发上游重跑。重要业务修改（价格 / 参数 / 功能 / 目标用户 / 定位等）触发下游失效，纯文字修改（错别字 / 标点 / 润色）可不触发失效。失效内容不得显示为有效 / 进入最终 Brief / 作后续依据。**字段级依赖图暂缓到后续版本**；全量重跑、只改直接字段不更新下游两个方案**未采用但保留为备选**（非永久禁止）。
- **工作台与输入门禁（DEC-044 / 059）：** 一个稳定任务在阶段导航 + 当前工作区 + 可收起证据 / 上下文面板中完成全流程。最低可运行输入决定能否启动；增强 / 可选资料缺失不阻塞。真实阻塞进入 Needs Input，以有限结构化行动请求说明问题、影响、来源 / 冲突值、允许动作和恢复范围。
- **文件限制与冲突分级（DEC-045）：** 默认 20 文件 / 任务、10 MB / 文件、文本 PDF 100 页、评论 CSV 10,000 行；单文件失败不回滚已接受文件。身份 / 关键事实冲突进入 Needs Input，非阻断证据差异继续并显式说明限制。
- **确认式局部重跑（DEC-044）：** Source 变化创建新 Source Version，业务结果编辑创建新 Domain Object Version；系统先展示失效 / 保留阶段和建议重跑起点，用户确认后才局部重跑。旧 Review Package 过期并拒绝提交，受影响内容重跑后进入同一审核 Gate。
- **审核与输出产品契约（DEC-046）：** Review Package / Approved Strategy 使用决策导向语义组；平台中立 Marketing Brief 与 Xiaohongshu Brief 各使用六个稳定产品语义组。Review Package 是不可变输入快照；三个正式业务结果采用不可变 Domain Version；Review Draft 使用单调递增 revision；Task 用 Current Truth Pointer；导出冻结对象版本、上游引用、限制与导出时间。最终公共 Schema 与并发实现不在本决定中冻结。
- **证据、编辑与恢复交互（DEC-047）：** 决策相关条目显示五类标记并从当前上下文展开证据卡片 / 面板；无真实定位时不伪造，不显示未经校准数字置信度。差异按语义组表达，明确业务修改触发既有阶段级失效，展示性润色不触发上游重跑，歧义修改由用户确认一次编辑意图。进度使用阶段时间线和下一步动作，不显示虚构百分比；错误提供补料、恢复、重试、刷新比较、取消或返回最后有效结果等匹配动作；导出前确认当前版本和限制摘要。
- **Frontend 工作台与交互实现边界（DEC-055 / 056）：** 一个深 TaskWorkbench 集中承载 Intake、Progress / Recovery、Review、Results / Export 与 Evidence / Context；使用私有 WorkbenchProjection 和 Capability / Intent，不复制后端 FSM。Review Draft 串行保存最新缓冲，Submit 只使用成功 Flush 的最新 revision；可访问性、Desktop Chrome、Reflow 与性能采用代表性证据验证，不建设多浏览器 / 手机 / 机械评分矩阵。
- **本地 Action Workbench（DEC-082）：** `/tasks` 只组织当前主要行动、创建入口和少量最近 Task；稳定 Task 内用中文五阶段进度、一个 Active Workspace 与 `320–360px` 可折叠 Context Rail 呈现结构化 Review、Marketing / Xiaohongshu Results 和技术细节。视觉为中文优先“运营编辑部 / 策略桌”，不采用 Dashboard 或 chat-first 产品形态。
- **评价框架（DEC-010）：** MVP 用**任务质量 / 结果可靠性 / 用户效率**三维评价，**不**把流畅度或销量作为唯一标准。优先六项指标：事实来源可追溯率、无依据事实数量、四层 Brief 完整率、关键结论人工接受率、生成可用 Brief 任务完成时间、下游失效正确率。销量 / 点击 / 转化 / 互动为未来真实试点业务指标，**非** MVP 唯一验收依据。
- **演示成功边界（DEC-042）：** 新环境可启动、允许资料可提交、端到端闭环可完成、证据 / 假设 / 不足 / 冲突可理解和审核、中断可恢复、失效结果不再有效、结果可导出且从目标用户视角可用。
- **验收包与 Markdown 导出（DEC-048 / 058）：** 虚构“城市通勤双肩包”作为唯一 Anchor SKU，三个资料变体覆盖正常、资料不足但可运行、阻断冲突恢复，一个变更脚本覆盖 Source 更新、业务编辑、陈旧 Review 和确认式局部重跑；行为硬门禁全部通过后仍需人工 `PASS / FAIL`。当前有效 Marketing Brief / Xiaohongshu Brief 分别导出 UTF-8 Markdown；用户侧 PDF / JSON 文件导出不进入首个 Goal。
- **声明完整性（DEC-060）：** Verified Fact 可以作为 Proof Point；Documented Claim / Claim-to-verify 不得提升为已验证事实。无依据绝对化、功效、认证或贬低式比较声明不得进入 Current Brief；系统不提供法律意见、平台审核保证、法规库或自动合规引擎。
- **Task 范围资料与可逆移除（DEC-061）：** 用户资料默认只属于当前 Task，不静默跨任务共享。用户可从当前有效资料集移除或替换 Source，并查看影响预览；该动作创建版本变化，不等于物理永久删除。首个 Goal 不提供用户侧 Purge UI。
- **跨会话任务返回（DEC-062）：** `/tasks` 提供创建任务和最近任务摘要，按名称 / 品类、当前阶段或等待状态、更新时间和主要下一步动作返回稳定 Task 深链；不建设搜索、高级筛选、批量、归档、统计或完整运营 Dashboard。
- **功能准入原则：** 与「更准确、更高效地完成商品上新定位和营销 Brief」无直接关系的能力，默认不进入 MVP。

> 注：以上为业务任务方向、平台边界、输入分层原则、输出主结构、人机协作原则、可靠性原则、失效重跑规则与评价框架；DEC-047～062 已冻结当前交互、验收 Anchor SKU、产品 / 技术权威边界、声明完整性、Task 资料生命周期和跨会话入口，DEC-055 / 056 已冻结 Frontend Architecture，但**不代表**业务实现、公共字段、Beta 指标、Fixture 物理文件、物理删除流程或最终 E2E 步骤已确定。

---

## In Scope（当前确认的方向，细节待定）

- 通用商品上新前的定位分析（方向）。
- 证据驱动商品上新策略工作台与复合主 Persona 假设（DEC-042）。
- 通用结构化营销 Brief 生成（方向）。
- **四层输出主结构（方向）：** 事实层 → 洞察层 → 策略层 → 执行层；后层可追溯前层（DEC-006）。
- **人机协作（方向）：** 单一关键审核节点（草稿后、最终 Brief 前）+ 异常暂停 + 用户最终判断权（DEC-007）。
- **输出可靠性（方向）：** 五类结论标记 + 事实可追溯 + 重要洞察保留依据 + 资料不足不得编造 + 修改产生依赖失效（DEC-008）。
- **阶段级失效与局部重跑（方向）：** 事实→洞察→策略→执行阶段级依赖失效 + 重要/非重要修改区分 + 重跑后复核；字段级依赖图暂缓（DEC-009）。
- **单任务工作台与输入门禁：** 阶段导航 + 当前工作区 + 可收起证据上下文；最低输入可运行，增强输入非强制，真实阻塞进入 Needs Input（DEC-044）。
- **确认式局部重跑：** 失效预览 + 用户确认 + 受影响阶段重跑 + 过期审核拒绝（DEC-044）。
- **渐进式证据与可恢复交互：** 五类标记 + 当前上下文证据入口 + 真实可用定位 + 语义组差异 / 编辑意图 + 阶段时间线 + 行动导向恢复 + 导出确认（DEC-047）。
- **证据约束的声明完整性：** Claim / Fact / Proof Point 边界 + 声明级阻断优先 + 无诚实替代时 Needs Input；不建设合规引擎（DEC-060）。
- **Task 范围资料纠错：** 用户资料不默认跨任务共享；可逆移除 / 替换 + 影响预览，不承诺用户侧永久清除（DEC-061）。
- **跨会话返回：** 最小最近任务入口 + 稳定深链，不建设运营 Dashboard（DEC-062）。
- **固定本地单用户产品化：** `/tasks` 行动首页 + 一个 Active Workspace + 可折叠 Context Rail；重要前端设计使用适用 taste skills，先完成独立设计 Issue，再授权实现（DEC-082）。
- **三维评价（方向）：** 任务质量 / 可靠性 / 用户效率 + 六项优先指标；不以流畅度或销量为唯一标准（DEC-010）。
- **行为型演示成功（方向）：** 本地启动、完整闭环、可理解 / 审核 / 追溯 / 恢复 / 导出与人工可用性（DEC-042）。
- 平台适配层（方向）：将通用 Brief 映射为平台表达。
- **首个平台演示场景：小红书商品种草 Brief 模板**（方向）。
- **输入分层（方向）：** 最低可运行输入 + 推荐增强 + 可选扩展；仅最低输入即可运行。
- 服务对象：商品运营与内容运营人员（DEC-002）。

> 产品语义组、输入门禁、默认文件限制、证据 / 编辑 / 进度 / 恢复 / 导出确认，以及 Frontend Module / Primitive / Styling / Interaction Projection 已确认；最终公共字段名 / 类型 / 逐字段必填表达、Markdown 模板、API / 数据库 Schema、并发传输与错误映射仍待后续 RFC，不得擅自补全。

---

## Out of Scope（明确不进入当前 MVP，可在未来扩展）

> 以下能力**不进入当前 MVP**，**不代表永久拒绝**，可作为后续扩展参考：

- 竞品自动监控；
- 多平台内容批量生成；
- 自动发布内容；
- 广告投放；
- 销售预测；
- 库存分析；
- 客服；
- 完整店铺经营诊断。
- 图表型运营 Dashboard、全局搜索 / 高级筛选、批量操作或 mega-nav；
- 手机专用产品；
- 销售、订单、物流或支付模块；
- chat-first Agent 主界面。

> **已关闭的范围问题：** DEC-041 已确认只接收结构化表单、文本、TXT / Markdown、文本型 PDF 与评论 CSV，不接收图片 / OCR，不抓取网页、评论或平台内容，不进行主动联网研究；DEC-023 已确认 LangGraph StateGraph；RFC-002 已确认生产数据库与事务栈；DEC-009 / DEC-044 已确认阶段级失效与用户确认后局部重跑；DEC-014 / DEC-032 已确认按需混合检索及证据运行边界；DEC-020 / DEC-031 / DEC-041 已确认首个演示只交付小红书 Brief 映射，不生成完整小红书正文，也不扩展其他平台。
>
> **已关闭的产品策划项：** DEC-060 已冻结声明完整性与高风险表达的最小边界；DEC-061 已冻结受控本地演示的数据生命周期体验；DEC-062 已冻结跨会话返回持久 Task 的最小入口；DEC-082 已冻结固定本地单用户 Action Workbench 方向。产品层当前无未接受 Proposal；下一步是独立前端设计 Issue，不是本文件中的实现授权。
>
> 根据 DEC-057，公共字段、传输、状态 / 错误、并发、Markdown 模板和下载协议分别由 RFC-004 / 005 作为下游权威，不再列为产品开放问题。
> - 技术实现：RFC-003～007 与 Frontend Architecture 覆盖的 Checkpointer、API、Retrieval、LLM Provider、Observability 和前端方案。
> - 评价：代表性验收包、行为硬门禁、非机械人工判断、Live Smoke 边界与 Frontend 核心测试工具已确认；Fixture 实例和最终 E2E 步骤 / 证据格式待 Testing Strategy 补全。Rubric 只辅助判断，不作为机械接受器。

---

## 文档骨架（占位，内容待填充）

> 以下章节标题仅作为未来结构占位，**除已标注外当前为空**，不构成任何范围声明。

- MVP 目标 —— 产品定位 + 核心任务 + 平台范围 + 输入分层 + 四层输出 + Human Review + 渐进式证据 + 编辑影响 + 阶段进度 / 恢复 + 失效重跑 + 三维评价 + 代表性验收包 + Markdown-first 导出已确认；Frontend 核心测试工具已接受，Fixture 实例与最终 E2E 步骤待 Testing Strategy 补全
- 关键假设与依赖 —— Persona / JTBD 研究假设继续标注；Beta 前访谈、RFC-004 / 005 / 007 与 Readiness / Testing / Goal 是下游依赖
- 验收标准 —— DEC-010 三维评价 + 六项优先指标与 DEC-048 行为硬门禁 + 人工判断已确认；Beta 指标阈值、Fixture 实例和技术执行方式待补全
- 风险 —— 见 Session-001 Risk-001 / 002 / 003

---

## 当前状态

- 项目处于 MVP-0 Fast Lane `GOAL_BLOCKED`；FL-1 deterministic foundation 已实现，DEC-082 的本地单用户 Action Workbench 方向已接受，具体视觉设计与实现尚未授权。
- 已确认产品定位、复合 Persona / JTBD 假设策略、核心任务、平台与输入输出范围、Human Review、证据、阶段失效、单任务工作台、输入门禁、确认式局部重跑、审核 / Brief / 版本、证据 / 编辑 / 进度 / 恢复交互、Anchor SKU 验收策略、Markdown-first 用户导出、产品 / 技术权威边界、声明完整性、Task 范围资料生命周期、行动首页与 Frontend Architecture（DEC-003～010 / DEC-041 / DEC-042 / DEC-044～062 / DEC-082）。
- 后续具体设计、实现或范围扩展必须位于独立 Issue / Task Contract；未接受内容不得写成 Current Truth。

---

## 下游技术与研究交接（产品层已无未接受 Proposal）

- 产品成功定义：行为与人工可用性、代表性验收包、必要行为门禁、人工 `PASS / FAIL`、Live Smoke 边界与 Frontend 核心测试工具已确认；真实用户指标、Fixture 实例和最终 E2E 步骤待后续补全。
- 产品层开放 Proposal：**当前无**。声明完整性、受控本地数据生命周期体验和跨会话任务返回入口已由 DEC-060～062 接受；Beta 用户研究继续保持 Assumption / Future Gate。
- 输入契约：Task / Fact Stage 最低门禁、默认文件限制、分级冲突与有限结构化 Needs Input 行动请求已确认；公共字段、状态和错误映射由 RFC-004 / 005 冻结。
- 工作台交互：单任务信息架构、深 TaskWorkbench、Primitive / Styling、私有状态投影、revision-safe Autosave / Diff、渐进式证据、行动导向恢复与确认式重跑已确认；公共传输、字段和状态 / 错误映射由 RFC-004 / 005 冻结。
- 输出契约：产品语义组、不可变 Domain Version、Review Draft revision、Current Truth Pointer、导出快照、导出前确认与 Markdown-first 用户格式已确认；公共字段、Markdown 模板、下载协议和并发实现由 RFC-004 冻结。
- 技术细节：RFC-003～007 与 Frontend Architecture 中的 Checkpointer、API、Retrieval、LLM Provider、Observability 和前端方案。
- 验收实现：Anchor SKU 与三个变体 + mutation 的产品语义已确认；Fixture 物理文件 / expected output、最终浏览器 E2E 步骤 / 证据格式和 Live Smoke 运行手册由 Testing Strategy 与 Goal Issue 补全。

已关闭的输入格式、联网抓取、LangGraph、PostgreSQL、RAG 概念边界、Skill / Agent 形态和平台交付边界不得重新列为开放范围问题；若需改变，必须通过新的 Accepted Decision 或 RFC 明确 Amend / Supersede。

讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- MVP Scope 必须与 [prd.md](prd.md) 一致；**不得擅自扩大范围**（Out of Scope 项不得自动纳入）。
- 不得为使文档「完整」而补充未经讨论的功能或 Brief / 模板字段或输入技术细节。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
