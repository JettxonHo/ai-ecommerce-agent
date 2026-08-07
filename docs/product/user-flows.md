# User Flows（用户流程）

> **Status: READY FOR USER OVERALL ACCEPTANCE — P-42～P-47 已接受；Product Specification Final Consistency Review = PASS**
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：MVP 核心任务的高层级流程（DEC-003）、首个演示场景映射（DEC-004）、输入分层（DEC-005）、四层输出（DEC-006）、单一关键审核节点 + 异常暂停（DEC-007）、证据与可追溯（DEC-008）、阶段级失效（DEC-009）、单任务工作台与确认式局部重跑（DEC-044）、最小输入 / 文件限制 / 冲突分级（DEC-045）、审核 / Brief 产品语义、版本 / revision / 导出行为（DEC-046）、渐进式证据、编辑意图、阶段进度、恢复与导出确认（DEC-047）、代表性验收包和 Markdown-first 用户导出（DEC-048）、产品 / 技术权威边界（DEC-057）、虚构 Anchor SKU 验收策略（DEC-058）、有限结构化 Needs Input 行动请求（DEC-059）、证据约束声明完整性（DEC-060）、Task 范围资料与可逆移除（DEC-061）、最小最近任务入口与稳定深链（DEC-062），以及 Frontend Architecture（DEC-055 / 056）。公共 Schema / 状态与工作流技术实现由下游 RFC 冻结。
> **DEC-041 同步：** 交互形态为引导式任务工作台；允许结构化表单、文本、TXT / Markdown、文本型 PDF 与评论 CSV。不提供图片 / OCR、链接抓取、主动联网研究、完整小红书正文生成或自动发布流程。
> **DEC-042 同步：** 工作台必须让用户无需理解内部实现即可完成闭环，并能理解、审核和追溯主要结论；主信息架构由 DEC-044 冻结，Module / Primitive / Styling 与质量边界由 DEC-056 冻结。
> **DEC-044 同步：** 工作台信息架构为阶段导航 + 当前工作区 + 可收起证据 / 上下文面板；真实阻塞进入 Needs Input；资料或上游内容变化先展示影响范围，再由用户确认局部重跑。
> **DEC-045 同步：** Task 创建和 Fact Stage 使用不同门禁；单文件失败不回滚同批已接受文件；身份 / 关键事实冲突阻断，其他证据差异继续并显示限制。
> **DEC-047 同步：** 证据从当前条目按需展开；修改按语义组和编辑意图判断影响；长任务显示阶段时间线而非虚构百分比；错误提供匹配恢复动作；导出前确认当前版本与限制。
> **DEC-048 同步：** 当前有效 Marketing Brief 与 Xiaohongshu Brief 分别导出 UTF-8 Markdown；文件保留 Task、版本、必要上游、产品语义组、假设 / 限制 / 风险、证据与导出时间上下文。首个 Goal 不提供用户侧 PDF / JSON 文件导出。
> **DEC-060～062 同步：** 无依据高风险声明优先只阻断进入 Current Brief；用户资料默认 Task-scoped，可逆移除 / 替换先显示影响，不承诺永久清除；`/tasks` 提供最小最近任务入口并保留稳定深链，不建设运营 Dashboard。
> **DEC-055 / 056 同步：** 一个深 TaskWorkbench 在稳定 Task Route 内投影 Active Workspace；私有 WorkbenchProjection 不复制后端 FSM。Review Draft 采用 latest-buffer 串行 Save 和成功 revision 链，Save / Flush / Conflict / 未确认编辑意图阻止 Submit；正式支持 Desktop Chrome，并对关键路径做代表性 WCAG / Reflow / Performance 验证。

---

## 已确认内容（Confirmed）

> 来源：[DEC-003](../decisions/dec-003-product-launch-positioning-and-marketing-brief.md) + [DEC-004](../decisions/dec-004-platform-neutral-core-xiaohongshu-demo.md) + [DEC-005](../decisions/dec-005-layered-mvp-inputs.md) + [DEC-006](../decisions/dec-006-four-layer-structured-marketing-brief.md) + [DEC-007](../decisions/dec-007-single-review-node-and-exception-pauses.md) + [DEC-008](../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md) + [DEC-009](../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md) + [DEC-041](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md) + [DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) + [DEC-044](../decisions/dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md) + [DEC-045](../decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md) + [DEC-046](../decisions/dec-046-review-brief-and-export-product-contract.md) + [DEC-047](../decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) + [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) + [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md) + [DEC-056](../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md) + [DEC-057](../decisions/dec-057-product-semantics-and-technical-contract-authority-boundary.md) + [DEC-058](../decisions/dec-058-fictional-anchor-sku-acceptance-fixture-strategy.md) + [DEC-059](../decisions/dec-059-targeted-needs-input-action-request-model.md) + [DEC-060](../decisions/dec-060-evidence-bound-claim-integrity-and-proportional-compliance-boundary.md) + [DEC-061](../decisions/dec-061-task-scoped-private-material-and-reversible-removal.md) + [DEC-062](../decisions/dec-062-minimal-recent-task-index-and-stable-deep-links.md)

- **跨会话进入（DEC-062）：** 用户可从 `/tasks` 创建新任务或查看最近任务；任务摘要显示名称 / 临时名称、品类、当前阶段或等待状态、最近更新时间和主要下一步动作。选择后进入稳定 Task 深链，并继续使用同一个 TaskWorkbench。首个 Goal 不提供搜索、高级筛选、批量操作、归档或 Dashboard。

- **高层级流程（已确认）：**

```
提交资料
        ↓
输入检查（资料完整性与冲突检查；提示可选增强资料）
        ↓
生成分析草稿（事实层 → 洞察层 → 初步策略层）
        ↓
用户审核与修改（单一关键审核节点）
        ↓
用户确认
        ↓
生成最终营销 Brief（执行层 + 平台模板映射；首个演示＝小红书种草 Brief）
        ↓
最终编辑与导出
```

  - **输入检查（DEC-005 / DEC-044 / DEC-045）：** 名称 / 临时名称、品类和推广目标用于创建 Task。Fact Stage 还需核心用途、至少一个可用当前商品来源、至少一个有来源核心属性且无阻断性身份冲突；手动结构化输入可构成来源，不强制上传文件。价格 / 当前卖点与增强资料缺失不机械阻断。
  - **生成分析草稿（DEC-006）：** 按四层结构逐层形成，后层可追溯前层依据——事实层（**不得混入未标记推断**）→ 洞察层（区分「有证据 / 有限推断 / 待补」）→ 初步策略层（定位 / 价值主张 / 差异化 / 卖点优先级 / 传播角度）。
  - **用户审核与修改（DEC-007，单一关键审核节点）：** 在草稿生成后、最终 Brief 生成前，用户可修正事实、补充资料、删改洞察、接受 / 否定假设、调整目标用户 / 卖点优先级 / 商品定位、标记不可公开信息、选择继续或退回重分析；**不要求**每层分别确认。用户保留最终业务判断权。
  - **生成最终营销 Brief（DEC-003 / 004 / 006）：** 用户确认后生成执行层 Brief，并将通用 Brief 映射为平台展示模板；**首个演示场景＝小红书种草 Brief**（完整小红书标题 / 正文非核心交付物）。
  - **最终编辑与导出：** 用户查看、编辑并导出最终结果。

> **异常分支（DEC-007 / 059 / 060）：** 检测到关键冲突或缺失（资料矛盾 / 关键参数缺失 / 无法判断目标用户 / 事实与推断难区分，或策略必须依赖无证据声明且没有可信替代表达）时：

```
检测到关键冲突或缺失
        ↓
暂停工作流
        ↓
说明问题、影响、可见来源 / 冲突值与有限可执行动作
        ↓
用户补充 / 选择 / 纠正 / 确认 / 取消
        ↓
按行动结果继续、恢复或重跑相关步骤
```

> 阻断性商品身份或关键事实冲突时，工作台展示冲突值、来源、影响和用户动作，系统**不得**自行猜测后继续；非阻断性证据差异允许继续，但必须展示资料限制与受影响结论。

> **声明完整性分支（DEC-060）：** Verified Fact 可以作为 Proof Point；Documented Claim / Claim-to-verify 不得提升为已验证事实。无依据绝对化、功效、认证或贬低式比较声明不得进入 Current Brief。若移除或降级后仍有诚实 Brief 路径，Task 继续并在 Review 显示风险与建议；只有无可信替代且策略必须依赖时进入 Needs Input。系统不提供法律或平台审核保证。

> **文件接收分支（DEC-045）：** 默认限制为每任务 20 文件、10 MB / 文件、文本 PDF 100 页、评论 CSV 10,000 行。超限、格式不允许、不可读或密码保护只拒绝对应文件；同批已接受文件保留。若剩余资料不足以运行 Fact Stage，再进入 Needs Input。

> **证据标记与可追溯（DEC-008）：** 分析草稿与最终 Brief 中的内容须标注五类类型（明确事实 / 有证据洞察 / 模型推断 / 待验证假设 / 资料不足）；明确事实须可追溯到用户输入 / 资料 / 已确认来源 / 审核修正；重要结论须保留与主要上游依据的关系。**用户在审核节点修改某项事实或关键洞察后，依赖该内容的下游策略与执行 Brief 不再被视为有效**；具体重跑采用 DEC-044 的失效预览与用户确认流程。

> **渐进式证据查看（DEC-047）：** 决策相关条目同时显示五类结论标记和“查看依据”入口。用户从当前条目打开证据卡片或可收起面板，查看来源标签、Source Version、真实可用定位、支持关系、Evidence Limitation 与 Conflict；无可靠页码 / 行号 / 段落时不显示伪造定位。直接证据可以显示短摘录，综合判断显示忠实摘要和主要依据，不要求每句话密集引用，也不显示未经校准数字置信度或机械覆盖总分。

> **阶段级失效与局部重跑分支（DEC-009 / DEC-044 / DEC-047）：** MVP 按阶段级依赖（非字段级依赖图）处理用户修改后的失效与重跑。明确结构化业务修改触发下游失效，纯展示润色不触发上游重跑，歧义自由文本由用户确认一次编辑意图；失效内容不得显示为有效 / 进入最终 Brief / 作后续依据。重跑交互统一为：

```
保存变更（新 Source Version 或 Domain Object Version）
        ↓
计算并展示失效预览（失效阶段 / 保留阶段 / 建议起点）
        ↓
用户确认局部重跑 ── 否 → 变更保留，失效结果仍不可用
        ↓ 是
仅重跑受影响阶段
        ↓
重新查看受影响内容；必要时进入新的 Review Package
```

```
用户修改事实层（价格 / 参数 / 功能 / 卖点等）
        ↓
下游阶段标记失效（洞察 / 策略 / 执行层）
        ↓
展示影响范围并等待用户确认
        ↓
重新生成洞察、策略与执行层
        ↓
用户重新查看受影响内容（进入 / 重新进入审核节点）
```

```
用户修改洞察层（目标用户 / 需求 / 动机 / 阻碍 / 场景等）
        ↓
策略与执行层标记失效（事实层不变）
        ↓
展示影响范围并等待用户确认
        ↓
局部重新生成策略与执行层
        ↓
用户重新查看受影响内容
```

```
用户修改策略层（定位 / 价值主张 / 卖点优先级 / 差异化 / 传播方向）
        ↓
执行层标记失效（事实 / 洞察层不变）
        ↓
展示影响范围并等待用户确认
        ↓
重新生成最终 Brief
        ↓
用户重新查看受影响内容
```

> 直接编辑**执行层**最终 Brief：保存为新的不可变 Domain Version，**默认不触发上游重跑**（视为最终业务调整），但 Marketing Brief 编辑会使既有 Xiaohongshu Brief 失效。Xiaohongshu Brief 自身编辑不反向使 Strategy 或 Marketing Brief 失效。上游重要修改采用失效预览 + 用户确认 + 阶段级局部重跑。若审核输入已变化，旧 Review Package 标记 `superseded` 且旧提交被拒绝；Review Draft 每次成功保存递增 revision，陈旧保存 / 提交同样拒绝。

> **编辑意图与差异（DEC-047）：** 修改前后至少按语义组展示内容、模型 / 用户来源和相关版本。明确改变 Fact、Insight、Approved Strategy 等结构化业务语义时自动视为重要修改；纯错别字、标点、格式或同义润色可以标记为展示性润色；歧义自由文本在保存或继续前由用户一次确认“业务内容修改”或“展示性润色”。LLM 不作最终分类 Gate，字段级依赖图不进入首个 Goal。

> 该流程通过一个深 TaskWorkbench 承载：外层 Router 提供 `/tasks` 最小最近任务入口、`/tasks/new` 与稳定 Task Route，并提取 Task Identity；Workbench 内部的 Intake、Progress / Recovery、Review、Results / Export 与 Evidence / Context 私有 Module 投影当前工作区。最近任务入口与聊天记录都不成为第二套业务状态。每次突出一个主要动作，Needs Input / Review / Invalidation 是正常 Workspace。Native / 按需 Radix + CSS Modules、语义化 Text Rendering 与可访问性边界由 DEC-056 / 062 冻结；最终公共 Resource、字段、状态、错误和传输由 RFC-004 / 005 冻结。

> **Review Draft 自动保存（DEC-056）：** 实施起始 Debounce 为 1 秒，同时最多一个 Save；In-flight Save 后只排队最新缓冲，并用前次成功返回的新 revision 继续保存。歧义文本先确认编辑意图；Submit 必须等待最新 Flush，Save / Flush 失败、Conflict 或意图未确认均阻止提交。Stale / Superseded 保留本地缓冲并由用户重新应用或放弃，不自动 Merge / 覆盖。

> **阶段进度与恢复（DEC-047）：** 长任务显示当前 / 已完成 / 待处理阶段、最近更新时间、当前等待原因和下一项动作，不显示虚构百分比。暂停或错误说明原因、受影响阶段以及最近有效结果，并按情形提供补料继续、恢复、重试当前阶段、查看失效预览并确认重跑、刷新比较陈旧 Draft、取消或返回最后有效结果。返回旧结果不改变其有效性；失效或部分提交结果不得标成 Current Truth。技术详情按需展开，最终公共错误 / 状态 / 动作映射由 RFC-004 冻结，运行可观测字段由 RFC-007 冻结。

> **Needs Input 行动请求（DEC-059）：** 每项只由当前真实阻断派生，展示缺失 / 冲突信息、影响、可见来源 / 冲突值、用户可以执行的补充 / 选择 / 纠正 / 确认 / 取消动作，以及完成后的恢复或重跑范围。非阻断增强资料仍是建议；不使用完整问卷或自由聊天保存事实。

> **Source 移除 / 替换（DEC-061）：** 用户资料默认只属于当前 Task。用户从当前有效资料集移除 Source 或用新 Source Version 替换时，系统先展示将受影响 / 保留的阶段与建议重跑起点；确认后按既有版本与失效规则处理。该动作不得显示为“永久删除”或“彻底清除”，因为物理保留、Hold、索引清理、Checkpoint 和导出处理尚由下游权威文档冻结。

> **Markdown 用户导出（DEC-048）：** 用户在 DEC-047 的版本与限制确认后，可分别导出当前有效的 Marketing Brief 或 Xiaohongshu Brief。导出文件是 UTF-8 Markdown，并携带能够解释其 Task、对象版本、必要上游、语义组、Hypotheses、Limitations、Risks、证据与导出时间的上下文；失效或部分提交结果不提供“作为当前结果导出”。导出位于 Results / Export Module；最终文件名、模板与下载协议仍待 RFC-004。

> **结果与导出：** Task 的 Current Truth Pointer 决定当前有效 Approved Strategy、Marketing Brief 与 Xiaohongshu Brief。导出前展示将被冻结的当前对象版本、必要上游引用、Hypotheses / Limitations / Risks 摘要；用户确认后冻结 Task 上下文和导出时间。失效结果不可作为当前结果导出，导出不修改 Current Truth。视觉边界由 DEC-056 冻结；模板、文件名和下载协议仍待 RFC-004。

---

## 下游技术与实施交接（产品语义已确认）

> P-42～P-47 已全部接受；下列内容不是产品开放 Proposal，而是 DEC-057 明确的 RFC / Testing / Goal 交接项：

- 任务创建、返回任务、深链、资料选择 / 拖放与解析进度的具体组件组合；Module / Primitive / Styling / 状态呈现原则已冻结，实施不得另创架构；
- 输入门禁：Task / Fact Stage 最低字段语义、文件限制、冲突分级、真实阻断与有限结构化 Needs Input 行动请求已确认；公共字段、动作和状态映射由 RFC-004 / 005 冻结；
- 人工审核 / 审阅 / 修改节点：**位置、不可跳过、Draft revision、结构化 Diff 与 1 秒起始串行 Autosave / Submit 阻断已确认**；公共 revision 与冲突传输由 RFC-004 冻结，物理持久化遵守已接受 RFC-002 并留给 Goal Issue；多人协作不进入首个 Goal；
- 异常与回退路径：**异常暂停、行动请求、恢复与声明级阻断边界已确认**（DEC-007 / 047 / 059 / 060）；Workflow Runtime 边界已由 RFC-003 接受，公共错误 / 动作传输由 RFC-004 冻结，具体节点组合留给实施 Issue；
- 阶段级失效与局部重跑：**失效范围、编辑意图、结构化 Diff、影响预览、用户确认后重跑和过期审核拒绝已确认**；公共 Change Set / 状态映射由 RFC-004 / 005 冻结，字段级依赖图不进入首个 Goal；
- Retrieval / Evidence 与 4 个 Core Skills 的概念边界，以及阶段进度和行动导向异常语义已确认；RFC-003 / 006 已冻结 Workflow / Model Runtime 边界，剩余公共状态与传输、Retrieval / Evidence、运行可观测映射分别交给 RFC-004 / 005 / 007，具体节点触发留给实施计划与 Issue；
- 通用 Brief 与小红书 Brief 的产品语义、导出快照、导出前确认、UTF-8 Markdown 与 Frontend 视觉边界已确认；模板和下载协议由 RFC-004 冻结；
- 四层与 Review / Brief 的产品语义组、渐进式证据与非数字置信度边界已确认；最终公共字段名 / 类型 / 逐字段必填表达和 Markdown 模板由 RFC-004 冻结，组件组合留给实现 Issue；
- 证据标记与可追溯（DEC-008 / 047 / 056）：**五类标记 + 当前上下文入口 + Evidence / Context Module + 真实可用定位 + 非数字置信度 + 按需加载已确认**；来源公共结构、Locator Schema、权限与 Evidence API 仍未确认；
- 各层查看 / 编辑的产品能力和人工审核位置 / 单一性已确认；具体控件组合留给实现 Issue，不再作为产品开放问题；
- Xiaohongshu Brief 的六个产品语义组和 Markdown 用户导出已确认；公共字段、模板与下载实现由 RFC-004 冻结；完整小红书正文、图片 / 视频生成和自动发布不进入首个 Goal；
- Xiaohongshu Adapter 的映射链、阶段进度和失败恢复产品语义已确认；公共状态、错误代码与传输由 RFC-004 冻结，具体触发留给实施计划与 Issue。

---

## 文档骨架（占位，内容待填充）

> 以下章节标题仅作为未来结构占位，**除已标注外当前为空**，不构成任何流程声明。

- 核心场景列表 —— 正常闭环、资料不足但可运行、阻断冲突恢复与重要事实 mutation 已由 DEC-048 / 058 确认
- 关键流程（触发条件、步骤、分支、异常、成功标准）—— 高层流程、审核、Needs Input、声明完整性、Task 资料移除 / 替换、最近任务入口、证据、阶段级失效重跑和行为型成功边界已确认；公共传输与技术状态映射交给下游 RFC
- 与 Agent / Retrieval / Skill 的交互点 —— 概念职责已确认；最终公共状态与传输由 RFC-004 / 005 冻结，具体节点触发留给实施计划与 Issue

---

## 当前状态

- 项目处于 **Pre-development Planning（正式开发前策划）阶段**；业务实现与长期 Goal 均未启动。
- 已确认高层任务流程、平台映射、输入分层、四层输出、Human Review、证据追溯、工作台、输入与冲突、审核 / Brief 产品语义、版本 / revision / 导出、证据 / 编辑 / 进度 / 恢复交互、Anchor SKU 验收、Markdown-first 用户导出、声明完整性、Task 范围资料生命周期、最近任务入口与 Frontend Architecture（DEC-003～009 / DEC-042 / DEC-044～062）；产品层已无未接受 Proposal，公共 Schema / 状态与工作流实现属于 RFC / Goal。
- 后续若改变已确认流程或扩大产品范围，必须通过新的 Accepted Decision 明确 Amend / Supersede；公共传输与技术实现继续遵守下游 RFC 权威边界。

---

## 产品流程闭合状态与下游交接

> 产品层当前没有未接受的流程 Proposal。下列条目区分已关闭产品事项、Beta 研究假设与 RFC / Testing / 实施交接，不构成新的开放产品问题：

- 用户与 Agent 交互的核心入口是什么？—— **已确认**为一个深 TaskWorkbench，含阶段导航、当前工作区和 Evidence / Context；Module / Primitive / Styling 与响应式原则已冻结，具体组件组合留给实施 Issue。
- 关键业务流程的细节？—— 正常、有限资料、阻断恢复和 mutation 四个验收场景，以及声明风险、Task 资料移除 / 替换和最近任务入口均已确认（DEC-048 / 058 / 060～062）；公共传输和物理生命周期留给下游权威。
- 输入不足时如何与用户交互？—— **Task / Fact Stage 门禁、文件限制、冲突分级 + 有限结构化 Needs Input 行动请求已确认**（DEC-044 / DEC-045 / DEC-059）；公共字段与状态映射由 RFC-004 / 005 冻结。
- 四层与 Review / Brief 的产品语义组、渐进式证据、导出确认和 Markdown 用户格式已确认；公共字段 / 类型 / 逐字段必填表达和 Markdown 模板由 RFC-004 冻结，具体组件组合留给实现 Issue。
- 证据标记与可追溯如何呈现？—— **五类标记、Evidence / Context Module、真实可用定位、非数字置信度和按需加载已确认**（DEC-008 / DEC-047 / DEC-056）；来源公共结构和权限映射尚未确认。
- 审核节点：位置、单一性、不可跳过、Review Package 不可变、Draft revision、结构化 Diff、1 秒起始串行 Autosave 与 Submit 阻断已确认；公共 revision / Conflict 传输由 RFC-004 冻结，物理并发实现遵守 RFC-002 并留给 Goal Issue；多人协作不进入首个 Goal。
- 通用 Brief 到小红书 Brief 的 Adapter 映射链、阶段进度和行动导向恢复已确认；公共状态与传输由 RFC-004 冻结，具体触发留给实施计划与 Issue。
- Direct-first、按需混合 Retrieval 与 4 个 Core Skills 的职责已确认；RFC-003 / 006 已冻结 Workflow / Provider Runtime 边界，索引与 Retrieval / Evidence 映射交 RFC-005，公共进度传输交 RFC-004，运行可观测交 RFC-007，具体节点触发留给实施计划与 Issue。
- 异常与回退路径如何设计？—— **异常暂停、原因 / 影响、有限行动请求、声明级阻断和行动导向恢复已确认**（DEC-007 / DEC-047 / DEC-059 / DEC-060）；Runtime 边界已由 RFC-003 接受，公共错误 / 动作传输由 RFC-004 冻结，运行可观测由 RFC-007 冻结。
- 局部重跑如何设计？—— **阶段级失效范围、编辑意图、结构化 Diff、影响预览、用户确认后局部重跑和过期审核拒绝已确认**；公共 Change Set 和状态映射由 RFC-004 / 005 冻结，字段级依赖图不进入首个 Goal。

Persona 具体取值与真实证据继续是 Beta 前研究 Gate；公共 Resource、字段、状态、错误、并发、Retrieval / Evidence 和运行映射分别由 RFC-004 / 005 / 007 冻结，组件组合留给 Goal 内边界清晰的实施 Issue。

讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- Flows 必须与 [user-personas.md](user-personas.md)、[prd.md](prd.md)、Agent Specs 保持一致。
- 不得为使文档「完整」而补充未经讨论的流程（具体步骤 / 页面 / 异常分支 / 输入交互 / 小红书模板字段不得臆造）。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
