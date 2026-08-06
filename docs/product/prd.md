# PRD（产品需求文档）

> **Status: PARTIAL — 产品定位、Persona / JTBD 假设、工作台、输入、审核 / Brief、证据 / 恢复交互、代表性验收包、行为门禁与 Markdown-first 用户导出已确认；最终公共 Schema、视觉组件、工作流实现和测试工具仍待确认**
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：产品设计原则（DEC-001）、首要用户与核心任务（DEC-002 / 003）、平台与输入输出范围（DEC-004～006）、Human Review、证据与失效规则（DEC-007～009）、三维评价框架（DEC-010）、本地演示包络（DEC-041）、产品定位与行为型成功边界（DEC-042）、单任务工作台与确认式局部重跑（DEC-044）、最小输入、文件限制和冲突分级（DEC-045）、审核 / Brief / 版本 / 导出产品契约（DEC-046）、证据披露、编辑意图、阶段进度和恢复交互（DEC-047），以及代表性验收包、行为门禁、人工验收和 Markdown-first 用户导出（DEC-048）。
> **DEC-041 同步：** 首个交付为本地可复现、受控单工作区的引导式任务工作台；输入限结构化表单、文本、TXT / Markdown、文本型 PDF 与评论 CSV，不做 OCR、图片理解、链接抓取或主动联网研究；完整小红书正文、图片 / 视频生成和自动发布均不在首个 Goal。
> **DEC-044 同步：** 工作台采用阶段导航 + 当前工作区 + 可收起证据 / 上下文面板；最低可运行输入通过后即可启动，真实阻塞进入 Needs Input；变更先展示失效范围，由用户确认后局部重跑，旧 Review Package 不得提交。
> **DEC-046 同步：** Review Package / Approved Strategy / Marketing Brief / Xiaohongshu Brief 的产品语义组已冻结；正式对象采用不可变 Domain Version，Review Draft 使用单调递增 revision，导出冻结 Current Truth 快照。最终公共字段与实现仍由 RFC-004 / 006 冻结。
> **DEC-047 同步：** 五类标记从当前条目渐进展开证据；语义组差异和编辑意图决定既有阶段级失效；阶段时间线不使用虚构百分比，错误按恢复动作组织，导出前确认 Current Truth 版本和限制摘要。最终组件、状态、传输与导出模板仍待 Frontend Architecture / RFC。
> **DEC-048 同步：** 首个演示使用三个固定资料包和一个变更脚本；行为硬门禁与非机械人工 `PASS / FAIL` 分离；Release Candidate 使用资料充分 Fixture 完成一次真实 Provider Smoke；当前有效 Marketing Brief 与 Xiaohongshu Brief 分别导出 UTF-8 Markdown，用户侧 PDF / JSON 文件导出不进入首个 Goal。
> **DEC-045 同步：** 名称 / 临时名称、品类和推广目标用于创建 Task；Fact Stage 还需核心用途、至少一个当前商品来源、至少一个有来源的核心属性且无阻断性身份冲突。默认每任务 20 文件、10 MB / 文件、文本 PDF 100 页、评论 CSV 10,000 行；单文件失败不回滚已接受文件。

---

## 产品设计原则（Confirmed）

> 来源：[DEC-001 — 真实电商业务价值优先于 Agent 技术复杂度](../decisions/dec-001-business-value-before-agent-complexity.md)（Accepted，2026-07-27）

- 产品设计、MVP 范围与技术选择应优先证明对真实电商用户、业务问题、工作流程与价值闭环的理解。
- LangGraph、RAG、Skill、Multi-Agent、Tool Calling 等技术仅在能改善业务任务完成效果、可靠性、可追溯性或用户体验时采用。
- 不得为了展示技术复杂度而无业务依据地增加 Agent 数量、框架组件或系统层级。
- **技术准入问题：** 任何技术方案都需回答「该技术具体解决了哪一个业务问题或可靠性问题？」无法回答的能力默认不进入 MVP。

---

## 已确认内容（Confirmed）

### 产品定位、Persona 与 JTBD（DEC-042，Accepted，2026-08-06）

> 来源：[DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md)

- **产品定位：** 面向中小电商商品与内容运营人员的证据驱动商品上新策略工作台。
- **价值链：** 用户资料 → 可审核、可追溯的定位分析 → 平台中立 Marketing Brief → Xiaohongshu Brief 映射。
- **Persona：** 一个复合主 Persona，商品运营和内容运营作为职责视角；详细画像与角色关系继续作为待验证假设。
- **JTBD 基线假设：** 商品上新或正式内容推广前，将分散资料整理为可追溯的定位判断和可审核 Brief，以支持后续内容策划与执行。
- **研究门禁：** 真实用户访谈是 Beta 前门禁，不是本地演示的前置条件。

### MVP 首要目标用户（DEC-002，Accepted，2026-07-27）

> 来源：[DEC-002](../decisions/dec-002-primary-mvp-users.md)

- **首要用户：** 中小电商商家的**商品运营人员**与**内容运营人员**。
- 产品应优先围绕该群体的真实工作任务、信息输入、决策过程、交付物与效果评价设计。

### MVP 核心任务与交付物（DEC-003，Accepted，2026-07-27）

> 来源：[DEC-003](../decisions/dec-003-product-launch-positioning-and-marketing-brief.md)

- **核心任务：** 帮助商品运营与内容运营人员，在商品上新或正式开展内容推广前，完成商品定位分析，并生成可供后续内容策划与执行使用的结构化营销 Brief。
- **核心交付物：** 结构化商品上新营销 Brief。
- **基础任务闭环（方向）：** 提交资料 → 检查完整性 → 提取事实与卖点 → 分析目标用户 → 分析需求 / 动机 / 阻碍 → 形成定位与差异化 → 形成内容方向与营销策略 → 生成 Brief → 质量检查与依据展示。该闭环为业务任务方向，**不代表**每一步的 Agent、技术实现与数据来源已确定。
- **功能准入问题：** 任何 MVP 功能都需回答「这项能力是否有助于用户更准确、更高效地完成商品上新定位和营销 Brief？」与该核心任务无直接关系的能力默认不进入 MVP。

### 平台范围与产品逻辑边界（DEC-004，Accepted，2026-07-27）

> 来源：[DEC-004](../decisions/dec-004-platform-neutral-core-xiaohongshu-demo.md)

- **平台中立：** 核心商品定位分析与营销 Brief 能力不绑定单一平台。
- **首个演示场景：** MVP 选择 **小红书商品种草** 作为首个具体展示场景。
- **产品逻辑边界（确认）：** 通用层（通用定位 + 通用 Brief）为核心；平台适配层将通用 Brief 映射为平台表达，首个＝小红书种草模板。小红书模板是通用 Brief 的一种适配方式，**不是**唯一输出形态。

### MVP 输入分层（DEC-005，Accepted，2026-07-27）

> 来源：[DEC-005](../decisions/dec-005-layered-mvp-inputs.md)

- **分层原则：** 输入分为 **最低可运行输入 / 推荐增强输入 / 可选扩展输入** 三层。仅凭最低可运行输入即可完成基础定位分析并生成 Brief；缺少增强 / 可选输入**不得阻断**基础流程。
- **Task 创建门禁：** 商品名称或临时工作名称、商品品类、本次推广目标。通过后创建稳定任务，但不代表 Fact Stage 已可运行。
- **Fact Stage 可运行门禁：** 商品核心用途、至少一个可用的当前商品来源（结构化表单手动输入可计入，不强制上传文件）、至少一个有直接来源支持的核心商品属性、无尚未解决的阻断性商品身份冲突。
- **非全局硬必填：** 价格 / 价格区间与商家当前卖点缺失时，按任务相关性显示限制与建议补充，不机械阻断。
- **推荐增强输入：** 用户评论、用户调研资料、常见用户问题、当前商品详情页、已有营销内容、品牌定位 / 品牌资料。
- **可选扩展输入：** 竞品资料、行业报告、平台案例、运营知识文档、历史推广结果、其他支持定位与营销决策的资料。
- **诚实原则：** 资料不足时不得假装拥有不存在的信息；应区分「用户提供事实 / 资料提取事实 / 证据推断 / 无法判断 / 需补充」，并可降低置信度、标记依据不足、提出补充建议。
- **字段准入问题：** 每个输入字段都需回答「是基础流程必须使用，还是只用于提高结果质量？」

> 注：以上为输入**分层原则与产品门禁**；DEC-041 已冻结允许格式，DEC-045 已冻结最低必填语义和演示默认限制。仍未确认公共字段名与数据类型、具体补充问题、隐私 / 权限 / 数据保存策略。

### 单任务工作台与输入交互（DEC-044，Accepted，2026-08-06）

> 来源：[DEC-044](../decisions/dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)

- **信息架构：** 同一稳定任务通过阶段导航、当前工作区和可收起证据 / 上下文面板完成创建、资料提交、进度、补充资料、审核、重跑、结果与导出。
- **两级门禁：** 最低可运行输入决定能否启动；增强 / 可选资料只提升覆盖与证据质量，不作为机械完整度强制项。
- **Needs Input：** 真实阻塞时显示原因、受影响阶段、需补充 / 确认内容与恢复方式；这是用户可见语言，不是已冻结 API 枚举。
- **范围边界：** 最终视觉布局、控件、公共字段 / 状态枚举与前端框架仍待后续规格或 RFC。

### 最小输入、文件限制与冲突处理（DEC-045，Accepted，2026-08-06）

> 来源：[DEC-045](../decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md)

- **默认文件限制：** 每任务 20 个文件、单文件 10 MB、文本型 PDF 100 页、评论 CSV 10,000 行；允许配置调整，但默认值必须契约测试。
- **部分接受：** 超限、格式不允许、不可读或密码保护只拒绝对应文件，已接受文件保持有效；若剩余资料未通过 Fact Stage 门禁，再进入 Needs Input。
- **阻断性冲突：** 商品 / SKU / 型号 / 版本身份或形成诚实事实层必需的关键事实冲突进入 Needs Input，显示冲突值、来源、影响和用户动作；模型不得静默裁决。
- **非阻断性差异：** 流程继续，但显式展示资料限制、受影响结论和证据。

### MVP 输出主结构（DEC-006，Accepted，2026-07-27）

> 来源：[DEC-006](../decisions/dec-006-four-layer-structured-marketing-brief.md)

- **四层结构：** MVP 核心输出采用 **事实层 → 洞察层 → 策略层 → 执行层** 四层结构。系统首先形成可检查、可追溯的商品分析与营销决策依据，再形成供商品运营与内容运营人员使用的执行 Brief。
- **核心原则：** 后层内容应能追溯到前层依据；**不得**出现「输入少量商品信息 → 无依据生成完整营销文案」这种缺乏分析过程和证据关系的核心路径。
- **事实层：** 记录有明确资料依据的信息（商品基本信息 / 功能参数 / 价格 / 商家卖点 / 已知限制 / 信息来源 / 资料缺失项）；事实层**不得混入未经标记的模型推断**。
- **洞察层：** 基于事实和增强资料分析（潜在用户 / 核心需求 / 场景 / 动机 / 阻碍 / 高频问题 / 关注点）；须区分「有直接证据」「有限资料推断」「资料不足无法判断」。
- **策略层：** 面向运营与营销的业务判断（定位 / 价值主张 / 差异化 / 卖点优先级 / 传播角度 / 需避免的表达 / 待验证假设）。
- **执行层：** 将分析转化为结构化 Brief（内容目标 / 受众 / 核心信息 / 内容角度 / 支撑证据 / 行动引导 / 平台模板映射 / 小红书种草 Brief）。
- **小红书定位：** 小红书种草 Brief 是执行层的一种**平台映射**（与 DEC-004 一致）；**完整小红书标题与正文暂不属于 MVP 核心交付物**。

> 注：以上为输出**四层主结构、追溯原则与小红书 Brief 映射边界**。DEC-046 已冻结 Review Package / Approved Strategy 的决策导向分组、平台中立 Marketing Brief 与 Xiaohongshu Brief 各六组产品语义；DEC-047 已冻结渐进式证据披露和非数字置信度边界。最终公共字段、类型、逐字段必填表达、组件和外部表示仍由后续规格与 RFC 冻结。完整小红书正文、图片 / 视频生成与自动发布不进入首个 Goal。

### 审核、Brief 与导出产品契约（DEC-046，Accepted，2026-08-06）

> 来源：[DEC-046](../decisions/dec-046-review-brief-and-export-product-contract.md)

- **Review Package：** 版本上下文 / Positioning Candidates / 关键 Facts 与 Insights / Hypotheses / Evidence Limitations / Conflicts 与 Strategic Risks / Model Recommendation。
- **Approved Strategy：** 目标与情境 / 定位 / 说服结构 / 假设决策 / 证据与风险 / 审核与版本元数据。
- **Marketing Brief：** Objective and Audience / Message Architecture / Reasons to Believe and Evidence / Execution Direction / Constraints and Honesty / Version and Workflow Context。
- **Xiaohongshu Brief：** Platform and Campaign Context / Note Format and Content Mode / Creative Structure Directions / Discovery and Action Directions / Evidence and Platform Constraints / Workflow and Version Context。
- **版本行为：** Review Package 是带 Package Version 的不可变输入快照；Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 是不可变 Domain Version，用户业务编辑或重跑创建新版本。Task 通过 Current Truth Pointer 标明当前有效结果。Review Draft 仅使用单调递增 revision，陈旧保存 / 提交拒绝，不能被下游读取。
- **导出：** 冻结发起导出时的当前有效对象版本、必要上游与证据引用、Hypotheses / Limitations / Risks、Task 上下文和导出时间；导出不改变 Current Truth，也不新增 Hash / SHA-256 要求。

这些分组是稳定产品语义，不等于最终 JSON / OpenAPI / 数据库字段。无适用内容时不得为满足结构而制造事实、证据、假设或风险。

### 证据、编辑、进度与恢复交互（DEC-047，Accepted，2026-08-06）

> 来源：[DEC-047](../decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)

- **渐进式证据：** 决策相关条目显示五类结论标记和查看依据入口；在当前工作台打开证据卡片或可收起面板，展示来源标签、Source Version、真实可用定位、支持关系、限制与冲突。无可靠定位时不得伪造，不使用未经校准数字置信度或机械覆盖总分。
- **结构化差异：** 审核和正式 Brief 至少按语义组显示修改前后、模型 / 用户来源和相关版本；最终行内、并排或摘要式组件不在本决定中冻结。
- **编辑影响：** 明确上游业务语义修改直接视为重要修改；纯错字、标点、格式或同义润色可以标记为展示性润色；歧义自由文本由用户一次确认编辑意图，不由 LLM 分类器作最终 Gate。
- **阶段进度：** 展示当前 / 已完成 / 待处理阶段、最近更新时间、等待原因和下一步动作，不显示无可靠基础的百分比。
- **错误与恢复：** 说明原因、受影响阶段、最近有效结果和匹配动作；支持补料继续、恢复、重试当前阶段、失效预览 / 确认重跑、刷新比较陈旧 Draft、取消或返回最后有效结果。失效结果不得恢复为 Current Truth。
- **导出确认：** 导出前展示将冻结的当前对象版本、必要上游引用、Hypotheses / Limitations / Risks 摘要；失效结果不可作为当前结果导出。

### MVP 人机协作审核机制（DEC-007，Accepted，2026-07-27）

> 来源：[DEC-007](../decisions/dec-007-single-review-node-and-exception-pauses.md)

- **协作模式：** MVP 采用 Human-in-the-loop。常规流程设置**一个强制关键审核节点**——在事实层、洞察层与初步策略层生成后、最终执行层 Brief 生成前，用户集中审核、修改并确认分析草稿。**不要求**在每一层分别确认。
- **异常暂停：** 当出现资料矛盾、关键参数缺失、卖点缺乏依据、无法合理判断目标用户 / 场景、基础与增强资料冲突、无法可靠区分事实与推断、或可能含夸大 / 高风险表达时，系统可暂停工作流并向用户提出补充问题；**关键事实冲突时系统不得自行猜测后继续生成最终 Brief**。
- **用户最终判断权：** 运营人员保留对商品事实、目标人群、商品定位、卖点优先级、对外传播边界、最终 Brief 的最终判断权；Agent 负责整理 / 提取 / 分析 / 暴露假设 / 建议 / 生成结构化交付物，**不替代**用户最终确认。
- **未采用方案（保留为备选，非永久禁止）：** 完全自动生成（无审核节点）、每层分别审核确认。

> 注：单一强制 Human Review、异常暂停、用户最终判断权、LangGraph StateGraph、任务级持久化和确认式局部重跑均已确认；该审核节点不可在常规成功路径中跳过。Review Package 是不可变快照；Review Draft 每次成功保存递增 revision，陈旧保存 / 提交被拒绝；Approved Strategy 提交后形成不可变 Domain Version。DEC-047 已冻结语义组差异和编辑影响判断；多人协作不进入首个 Goal。具体 Interrupt / Checkpoint、并发传输、自动保存频率和视觉组件仍待 RFC-003 / 004 与 Frontend Architecture。

### MVP 分级证据与结论可追溯（DEC-008，Accepted，2026-07-27）

> 来源：[DEC-008](../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md)

- **五类结论标记：** 输出必须区分 **①明确事实 / ②有证据洞察 / ③模型推断 / ④待验证假设 / ⑤资料不足**，不得将用户输入、资料事实、模型分析与未验证假设混合呈现。
  - 明确事实须可追溯到用户输入 / 资料 / 已确认来源 / 审核修正；**不得由模型补充**。
  - 有证据洞察须有支撑资料；推断须显式标记并说明依据；待验证假设须提示用户确认；资料不足须明确表达「无法判断」，**不得用模型常识自动补全**。
- **事实可追溯：** 所有明确事实必须可追溯到用户字段、上传资料、已确认外部来源或审核阶段修正。
- **事实与推断分离：** 内部数据与用户可见输出都要区分事实 / 洞察 / 推断 / 假设 / 无法判断。
- **重要洞察保留依据：** 影响目标用户、商品定位、卖点优先级、内容策略的重要洞察应保留主要依据。
- **资料不足保持诚实：** 标记资料不足 / 降低确定性 / 建议补充 / 或标记为待验证假设；**禁止伪造来源**（不生成不存在文档、不伪造评论原文 / 引用编号、不把模型常识包装为用户资料、不引用未读取来源）。
- **修改产生依赖影响：** 用户在审核节点修改事实或关键洞察后，依赖该内容的下游策略与执行 Brief **不应继续被视为有效**。系统展示失效预览，用户确认后从最早受影响阶段局部重跑（DEC-044）。
- **未采用方案（保留为备选，非永久禁止）：** 只展示最终结论、所有结论强制逐条原文引用。

> 注：五类结论标记、渐进式证据披露、非数字置信度边界、版本化 Source / Fragment / Evidence Link、按需混合 Retrieval、阶段级局部重跑、LangGraph State 与 PostgreSQL Current Truth 边界均已确认；网页抓取与主动联网研究不进入首个 Goal。最终组件、来源公共 Schema、权限过滤、Retrieval Backend、生产 Checkpointer 和来源处理细节仍待 Frontend Architecture / RFC-003 / 005。

### MVP 阶段级失效与局部重跑（DEC-009，Accepted，2026-07-27）

> 来源：[DEC-009](../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md)

- **阶段级依赖（非字段级依赖图）：** 按事实 → 洞察 → 策略 → 执行的阶段关系处理失效与重跑。MVP **暂不实现**精细字段级依赖图。
- **失效规则：**
  - 修改**事实层** → 洞察 / 策略 / 执行层失效并重生成（**不得**沿用旧事实下游结论）；
  - 修改**洞察层** → 策略 / 执行层失效并重生成（事实层不变）；
  - 修改**策略层** → 执行层失效并重生成（事实 / 洞察不变）；
  - 直接编辑**执行层** Brief → 保存编辑，**默认不触发上游重跑**（视为最终业务调整）。
- **重要 vs 非重要修改：** 明确改变 Fact / Insight / Approved Strategy 等结构化业务语义的修改直接触发既有下游失效；纯错字 / 标点 / 格式 / 同义润色可标记为展示性润色；歧义自由文本由用户确认一次编辑意图。LLM 不作为影响判断的最终 Gate。
- **失效内容：** 不得继续显示为有效、不得进入最终 Brief、不得作为后续生成依据；旧版本按版本化领域状态保留，并至少按语义组展示修改前后、修改来源与相关版本。
- **确认式局部重跑（DEC-044）：** 变更保存后先展示变更来源、将失效 / 保留的阶段与建议重跑起点；用户确认后才启动新的局部生成。取消或暂不确认不恢复旧下游结果的有效性。
- **重跑后复核：** 重跑内容须由用户重新查看；若影响 Human Review 输入，则旧 Package 标记 `superseded`、旧提交被拒绝，并创建新 Package 进入同一审核 Gate。
- **未采用方案（保留为备选，非永久禁止）：** 全量重跑、只改直接字段不更新下游；字段级依赖图暂缓到后续版本。

> 注：阶段级失效、编辑影响识别、语义组差异、用户确认后局部重跑、过期审核拒绝、LangGraph StateGraph、PostgreSQL Current Truth 与一个统一用户侧 Agent 均已确认；字段级依赖图不进入首个 Goal。生产 Checkpointer / Interrupt 对账、Diff 算法、公共 API 状态映射和具体节点实现仍待 RFC-003 / 004 / Frontend Architecture。

### MVP 三维评价框架（DEC-010，Accepted，2026-07-27）

> 来源：[DEC-010](../decisions/dec-010-three-dimensional-mvp-evaluation-framework.md)

- **三维评价：** MVP 同时评估 **①任务质量 / ②结果可靠性 / ③用户效率**；**不**把语言流畅度或最终销量作为唯一成功标准。
  - 任务质量：事实 / 卖点覆盖、四层 Brief 完整性、定位与资料一致性、可用性、关键结论接受率。
  - 结果可靠性：事实来源可追溯率、事实与推断分类准确性、无依据事实数、伪造来源数、资料冲突识别、资料不足标记、上游修改后下游失效正确性、重跑后一致性。
  - 用户效率：提交到可用 Brief 的总耗时、相对人工节省时间、补充资料轮次、审核修改数、完成成功率、人工修改量、交互步骤。
- **六项优先指标：** ①事实来源可追溯率 ②无依据事实数量（目标趋近零）③四层 Brief 完整率 ④关键结论人工接受率 ⑤生成可用 Brief 任务完成时间 ⑥下游失效正确率。
- **评价原则：** 任务完成 + 结果可信 + 用户节省成本；销量 / 点击 / 转化 / 互动作为未来真实试点的业务结果指标，当前**非** MVP 唯一验收依据。

> 注：以上为**评价框架与方向**；**未**确认每项指标公式、目标阈值、测试数据集、用户测试人数、人工评分标准、是否使用 LLM-as-a-Judge、埋点方案、对照组设计、测试环境、是否接入真实业务数据、是否展示评测 Dashboard。

### 行为型演示成功边界（DEC-042，Accepted，2026-08-06）

- 新环境可按权威文档启动本地演示栈；
- 用户可以提交允许的资料并完成事实、洞察、定位、Human Review、Marketing Brief、Xiaohongshu Brief 映射与导出；
- 主要结论、证据、假设、资料不足和冲突对用户可理解、可审核；
- 关键中断可恢复，失效内容不会继续作为当前有效结果；
- 目标用户视角下的 Brief 可用于后续内容策划，不要求开发者解释内部实现才能完成流程。

DEC-048 已冻结三个固定资料包 + 一个变更脚本、必要行为门禁、人工 `PASS / FAIL`、Release Candidate 单次 Live Smoke 与 Critical / Blocking 缺陷为零的完成边界。测试工具、Fixture 具体内容和最终 E2E 步骤由 Testing Strategy 补全；Rubric 只辅助判断，不以机械总分、语言流畅度或销量承诺自动接受。

### 验收包与用户导出（DEC-048，Accepted，2026-08-06）

> 来源：[DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) · [Testing Strategy](../development/testing-strategy.md)

- **固定验收包：** 资料充分正常任务、资料不足但可运行任务、阻断性冲突与恢复任务，以及覆盖 Source 更新、业务编辑、陈旧 Review 和确认式局部重跑的变更脚本。
- **验证分离：** 普通 PR 使用确定性替身；Release Candidate 使用正常任务执行一次真实 Provider Smoke；行为不变量全部通过后仍需人工从目标用户视角判断可理解、可审核、可恢复和可用于后续策划。
- **用户导出：** 当前有效 Marketing Brief 与 Xiaohongshu Brief 分别导出 UTF-8 Markdown，并保留 Task、版本、必要上游、语义组、Hypotheses、Limitations、Risks、证据与导出时间上下文。首个 Goal 不提供用户侧 PDF / JSON 文件导出。

---

## 当前状态

- 项目处于 **Pre-development Planning（正式开发前策划）阶段**；业务实现与长期 Goal 均未启动。
- 已确认产品定位、复合 Persona / JTBD 假设策略、核心任务、平台与输入输出范围、Human Review、证据、阶段失效、单任务工作台、输入门禁、确认式局部重跑、审核 / Brief 产品语义、版本 / revision / 导出行为、证据 / 编辑 / 进度 / 恢复交互，以及代表性验收包、行为门禁与 Markdown-first 用户导出（DEC-001～010 / DEC-041 / DEC-042 / DEC-044～048）；最终公共字段、视觉组件、工作流与数据实现、测试工具和 Fixture 实例仍待确认。
- 其余具体内容，必须等到对应 Proposed Decision 被用户明确接受并记为 Accepted Decision（见 [../decisions/](../decisions/)）后，才能写入。

---

## 文档骨架（占位，内容待填充）

> 以下章节标题仅作为未来结构占位，**除已标注外当前为空**，不构成任何需求声明。

- 背景与目标
- 目标用户与场景 —— **首要用户已确认**（DEC-002）；具体场景与 Persona 待 [user-personas.md](user-personas.md) / [user-flows.md](user-flows.md)
- 核心问题陈述 —— **核心任务已确认**（DEC-003）；任务细节与验收标准待 [mvp-scope.md](mvp-scope.md)
- 功能范围（与 [mvp-scope.md](mvp-scope.md) 保持一致）—— **核心任务 + 平台范围 + 输入分层 + 四层输出主结构已确认**；具体 In / Out of Scope 见 [mvp-scope.md](mvp-scope.md)
- 平台范围 —— **已确认**（DEC-004）；模板字段与适配层技术待确认
- 输入设计 —— **分层原则、允许格式、Task / Fact Stage 最低门禁、默认文件限制、分级冲突与 Needs Input 交互语言已确认**（DEC-005 / 041 / 044 / 045）；公共字段类型、补充问题与状态映射待确认
- 输出设计 —— **四层主结构 + Review / Approved Strategy / Marketing Brief / Xiaohongshu Brief 产品语义组 + 不可变版本、导出快照 / 确认和 Markdown 用户格式已确认**（DEC-006 / 046 / 047 / 048）；最终公共字段、Markdown 模板、下载实现与视觉组件待确认
- 人机协作 —— **单一关键审核节点 + 异常暂停 + 用户最终判断权 + 过期 Package / revision 拒绝 + 行动导向恢复已确认**（DEC-007 / 029 / 044 / 046 / 047）；自动保存频率、并发实现与工作流技术实现待确认
- 输出可靠性 —— **五类结论标记、渐进式证据、非数字置信度、可追溯、版本化 Source / Evidence 与按需混合 Retrieval 已确认**；最终组件、公共 Schema、Retrieval Backend 与索引方案待确认
- 失效与重跑 —— **阶段级失效 + 编辑意图 + 语义组差异 + 失效预览 + 用户确认后局部重跑已确认**；字段级依赖图不进入首个 Goal；生产 Checkpointer、Diff 算法和公共状态映射待确认
- 评价框架 —— **三维评价 + 六项优先指标、首个演示固定验收包、行为门禁与非机械人工判断已确认**（DEC-010 / DEC-048）；Beta 指标公式 / 阈值 / 人数 / 埋点 / Dashboard，以及 Fixture 实例与测试工具待确认
- 非目标 —— 见 [mvp-scope.md](mvp-scope.md)「Out of Scope」
- 关键体验与流程（与 [user-flows.md](user-flows.md) 保持一致）—— **高层流程已确认**（DEC-003 / 004 / 005）；具体步骤待 [user-flows.md](user-flows.md)
- 约束与假设
- 验收标准 —— **DEC-010 三维评价 + 六项优先指标与 DEC-048 固定验收包、行为硬门禁、人工 `PASS / FAIL` 和 Live Smoke 边界已确认**；Beta 指标、Fixture 实例、测试工具和最终执行步骤待确认
- 开放问题

---

## 待讨论的开放问题（PRD 相关）

- 目标用户 / 商家端 vs 消费者端：**已确认**（DEC-002）。
- 要解决的核心业务问题：**已确认**（DEC-003）。
- 平台范围：**已确认**（DEC-004）；小红书模板字段与适配层技术实现待确认。
- 输入设计：**分层原则、首个演示允许格式、Task / Fact Stage 最低门禁、默认文件限制、分级冲突与 Needs Input 交互语言已确认**（DEC-005 / DEC-041 / DEC-044 / DEC-045）；公共字段类型、长期知识库 / 向量索引、具体补充问题与状态 / 错误映射待确认。
- 通用营销 Brief 的输出结构：**四层主结构、四类审核 / Brief 产品语义组、渐进式证据、不可变版本、导出确认与 Markdown 用户格式已确认**（DEC-006 / DEC-046 / DEC-047 / DEC-048）；最终公共 Schema、Markdown 模板、下载实现和视觉组件仍待确认。
- 人机协作 / 审核节点：**单一关键审核、异常暂停、用户最终判断权、不可变 Review Package、Draft revision、陈旧提交拒绝和行动导向恢复已确认**（DEC-007 / DEC-029 / DEC-044 / DEC-046 / DEC-047）；自动保存频率、并发实现、具体异常规则和工作流技术实现仍待确认。
- 输出可靠性 / 可追溯：**五类结论标记、渐进式证据、非数字置信度、版本化 Source / Evidence 与按需混合 Retrieval 已确认**；最终组件、公共 Schema、Retrieval Backend 与索引方案仍待确认。
- 失效与局部重跑：**阶段级失效、编辑意图、语义组差异、影响预览、用户确认后局部重跑和过期审核拒绝已确认**；生产 Checkpointer、Diff 算法和公共状态映射待确认，字段级依赖图不进入首个 Goal。
- 完整小红书标题 / 正文、图片 / 视频生成与自动发布：**不进入首个 Goal**（DEC-041）。
- 产品价值与评估指标（Question-003）：三维评价 + 六项优先指标由 DEC-010 确认；首个演示的固定验收包、行为门禁与非机械人工判断由 DEC-048 确认。真实用户指标公式 / 阈值、人数、埋点与 Dashboard 待 Beta 规划。
- Agent、Retrieval / Evidence、Skill 的职责边界：**概念层已确认**（DEC-020～033）；生产 Runtime 与具体 Provider / Backend 仍待 RFC-003～007。
- 演示成功边界：行为与人工可用性标准由 DEC-042 确认；固定验收包、必要行为门禁、人工 `PASS / FAIL` 和 Live Smoke 边界由 DEC-048 确认；测试工具、Fixture 实例和最终 E2E 步骤待 Testing Strategy 补全。

讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- PRD 必须与 [mvp-scope.md](mvp-scope.md)、[user-personas.md](user-personas.md)、[user-flows.md](user-flows.md) 保持一致；若不一致，按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
- 不得为使文档「完整」而补充未经讨论的事实。
