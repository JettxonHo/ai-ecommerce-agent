# System Architecture（系统架构）

> **Current sync（2026-08-06）：** RFC-001～RFC-003 与 RFC-006 已 Accepted，FND-001～003 已完成；统一 Ecommerce Agent、LangGraph StateGraph、持久化架构与 LLM Runtime 架构均已确定。DEC-049～051 与 RFC-003 已冻结 Checkpoint、Durable Dispatch、Fenced Ownership、取消、兼容和 Safe Resume。DEC-052～054 与 RFC-006 已冻结首个 Goal 的 OpenAI Responses API / `gpt-5.6-terra`、窄型同步 Port、Structured Output、有界 Recovery、可读 Version Tuple、五个固定 Profile、确定性 Context Assembly、Adapter Secret / Payload Allowlist、同 Port Scripted Substitute 与单次人工 RC Smoke。DEC-046～048 已冻结 Review / Brief / 交互 / 验收 / Markdown 导出产品语义；DEC-055 / DEC-056 已冻结 React / Vite SPA、状态所有权、深 TaskWorkbench、revision-safe 交互与适度 Web 质量边界，但不冻结公共 HTTP Schema。正文中“具体框架 / 数据库 / Provider 尚未决定”只代表相关章节形成时的历史状态。API、Retrieval 与 Observability 仍由 RFC-004 / 005 / 007 决定。
> **Product constraint sync（2026-08-07）：** DEC-060～062 已冻结证据约束的声明完整性、Task 范围用户资料与可逆移除，以及 `/tasks` 最小最近任务入口。它们是 RFC-004 / 005 / 007 的上游产品约束，不授权通用 Compliance Engine、跨任务默认资料复用、用户侧永久删除或完整运营 Dashboard。
> **Historical expansion note：** 正文按 DEC-013～037 的形成顺序累积；其中 `NOT STARTED`、`NOT READY`、`下一动作 / 下一议题`、旧 PENDING 列表和 Spike Handoff 只记录当时状态，不是当前授权或执行指令。当前状态仅以上述 Current sync、[AGENTS.md](../../AGENTS.md) 与 [Implementation Readiness](../handoffs/implementation-readiness.md) 为准。

> **Status: PARTIAL — 高层架构原则已确认（DEC-011 控制分工 / DEC-012 状态结构 / DEC-013 持久化恢复 / DEC-014 分层数据访问 + 按需混合 RAG / DEC-015 Skill 定义 / DEC-020 MVP 业务能力范围 / DEC-021 Agent 架构形态 / DEC-022 工作流框架能力需求 / DEC-023 选择 LangGraph StateGraph / DEC-024 四类状态边界与版本化领域状态 / DEC-025 来源与证据分层架构 / DEC-026 首个核心 Skill Contract / DEC-027 第二个核心 Skill Contract / DEC-028 第三个核心 Skill Contract / DEC-029 Human Review 与 Approved Strategy Contract / DEC-030 Marketing Brief Generation Skill Contract / DEC-031 Xiaohongshu Brief Mapping Adapter Contract / DEC-032 Hybrid Retrieval and Evidence Runtime Architecture / DEC-033 Workflow Runtime Failure Recovery, Retry and Observability Contract / DEC-034 Technical Spike Plan and Architecture Readiness Gate / DEC-035 Technical Spike 临时技术栈与执行契约[临时栈=Python 3.13+LangGraph 1.2.9+同步 StateGraph+三类分离 SQLite+SqliteSaver+sqlite3 事务+Scripted Model+Mock Retrieval+Scenario Fault Injection+pytest+Local JSONL Trace+CLI Runner，临时选择不构成生产承诺；Amends DEC-034]）；技术栈 / 节点划分 / 最终状态 Schema / 向量库 / 检索实现 / Skill 实现（除已确认 Contract 的概念层）仍待确认**
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：总体执行架构原则（DEC-011）、Workflow State 两层结构（DEC-012）、任务级持久化与跨会话恢复（DEC-013）、分层数据访问与按需混合 RAG（DEC-014）、Skill 的契约化业务能力包定义（DEC-015）、首批 MVP 业务能力范围（DEC-020：4 Core Skills + 1 平台 Adapter + 共享能力）、Agent 架构形态（DEC-021：统一用户侧 Agent + 确定性主工作流编排契约化 Skill，**不采用** Multi-Agent 主架构 / LLM Supervisor）、工作流框架能力需求（DEC-022：框架须为有状态/确定性/可持久化的业务工作流运行时，含 Must-have/Should-have/100 分制评分维度/淘汰条件）、工作流运行框架与主要建模方式（DEC-023：LangGraph + StateGraph / Graph API；不采用 ReAct Agent / LLM Supervisor / 多自治 Agent 主流程）、四类状态边界与版本化领域状态（DEC-024：状态划分为 Domain / Workflow / Runtime / Interaction 四类；版本化 Domain Objects + Current Truth Version Pointers；task_id / thread_id / run_id / checkpoint_id 四标识符边界；Checkpointer 与业务数据库分离）、**来源与证据分层架构（DEC-025：Source → Source Version → Document / Record → Fragment → Evidence Link → Versioned Domain Object；版本化来源、可定位 Fragment、Evidence Link 为独立关系对象、Evidence Role 显式；Retrieved Fragment 仅 Candidate Evidence，须经确定性 Validator + Evidence Link 才成正式证据；Source Set Version + Evidence Package；Amends DEC-008 / DEC-014）、首个核心 Skill Contract（DEC-026：Product Intake & Fact Extraction Skill 合并输入诊断与事实提取；Hard Rule = No Fact without a valid current-product Fragment；四档输入完整度；声明五分类；模型不得创造 Explicit Fact；关键冲突暂停交用户；确定性 Validator 15 项为写入 Facts Current Truth 前的必要 Gate；不使用模型数字 Confidence；Amends DEC-005）、第二个核心 Skill Contract（DEC-027：Customer Insight Analysis Skill 采用 Evidence-backed Mode + Degraded Hypothesis Mode；必须区分 Theme 与 Insight；4 类证据（Direct / Competitor / Indirect / Non-customer），竞品反馈不能证明当前商品用户；Evidence Coverage 5 状态（none / anecdotal / repeated_signal / dataset_supported / multi_source_corroborated，不用模型百分制 Confidence）；不设统一样本门槛，单条反馈只能 Anecdotal Signal；禁止虚构用户原声、改写冒充直接引用、竞品冒充当前商品用户；正式频率必须由确定性统计产生，禁止 Top-K 频率外推；重要 Insight 须检查反向证据；Insight Types 13 类 + InsightItem 概念；输出五组 + valid_with_limitations；确定性 Validator 18 项；不用模型单一综合 Confidence；Amends DEC-017）、第三个核心 Skill Contract（DEC-028：Product Positioning Skill 采用多候选、证据约束与强制人工决策契约；Positioning 属 Strategic Inference 非 Explicit Fact；默认 3 候选、允许 2–4 且必须实质差异；Positioning Elements（Target Segment / Usage Context / Job or Core Need / Category Frame / Value Proposition / Differentiation / Reasons to Believe / Proof Points）；Hard Rule = No Proof Point without a valid Fact，竞品证据只能用于 Gap 和 Context 不得归因当前商品能力；不使用不透明综合数字分数，改用可解释 7 维排序；Insight valid_with_limitations 时进入 Limited Evidence Mode 传播证据限制；输出五组（Positioning Context / Candidates / Comparison Matrix / Recommendation / Workflow Decision）+ 强制 Human Review；Approved Strategy Version 才能进入 Marketing Brief Generation；确定性 Validator 20 项；Amends DEC-018）、**Human Review 与 Approved Strategy Contract（DEC-029：强制结构化 Human Review 节点位于 Product Positioning 与 Marketing Brief Generation 之间，而非「AI 输出 → 用户点击同意」；流程 `Positioning Candidate → Review Package → LangGraph Interrupt → Strategy Draft → User Submit → Validation Transaction → Approved Strategy → Resume Workflow`；采用版本化 Review Package（固定审核时的 Facts / Insights / Positioning / Source Set Versions / Candidates / Evidence Limitations，审核开始后不得后台静默替换；上游版本变化 → 旧 Package superseded、旧提交被阻止）；必审内容（Positioning Candidates 全部要素 + Model Recommendation Rationale / Critical Facts / Critical Insights / 影响战略 Hypotheses / Evidence Limitations）；8 项 Review Actions（select[≠Approve] / edit[保留模型版本与用户修改、不静默覆盖] / merge[须重跑 Schema·Fact Ref·Insight Ref·Proof Point·Logical Consistency·Evidence Limitation 六类校验] / reject / request_more_information[→ waiting_for_input 触发上游失效重跑] / save_draft[不更新 Current Truth、Marketing Brief 不可读] / submit[触发原子事务] / withdraw[不删历史]）；Strategy Draft（临时工作内容、不属 Current Truth、须过 Validator 才能提交）与 Approved Strategy Version（版本化 Domain Object，承接 DEC-024，Marketing Brief 唯一正式战略输入）严格分离；Hypothesis Decisions 5 动作（accept_for_execution / accept_for_testing[requires_validation=true] / edit / reject / request_evidence，接受 Hypothesis ≠ Hypothesis→Fact）；Evidence Limitations 不得静默删除、可 accepted_by_user 但 Marketing Brief 须继续传播；Proof Point 须展示完整追溯 `Proof Point → Fact → Evidence Link → Fragment → Source Version`、用户改写后须校验仍被原 Fact 支持、无证据内容（如「市场上最轻」无市场比较证据）不得升级为 Proof Point；submit 为 18 步原子事务（任一失败不创建版本 / 不更新 Pointer / 不改下游阶段）+ 幂等（idempotency_key，重复返回首次结果、Stale 拒绝）+ 并发保护（不静默覆盖较新 Draft）+ 撤回（创建 Withdrawal Record、清除 Pointer、Marketing Brief + Xiaohongshu Mapping 失效，承接 DEC-009）+ 完整审核历史；Review Status 9 值（not_ready / pending / in_progress / changes_requested / submitted / approved / superseded / withdrawn / cancelled，最终名未确认）；确定性 Validator 25 项；Hard Rules = No Approved Strategy without explicit submission / No stale Review Package submission / No unsupported Proof Point / No silent removal of Evidence Limitations / No automatic Hypothesis-to-Fact conversion；Amends DEC-007（正式定义强制 Human Review 节点）+ DEC-024（定义 Approved Strategy Current Truth 转换，不推翻既有结论））、**第四个核心 Skill Contract 的 Marketing Brief 执行职责（DEC-030：将当前唯一有效 Approved Strategy Version 转换为结构化、平台无关、可追溯的 Marketing Brief，为 Xiaohongshu 及未来平台 Adapter 提供稳定输入；MarketingBrief 概念对象 brief_id / brief_version_id / approved_strategy_version_id / facts_version_id / insights_version_id / communication_objective / audience / audience_context / core_message / message_hierarchy / benefit_hierarchy / key_benefits[] / reasons_to_believe[] / proof_points[] / objections[] / objection_responses[] / content_angles[] / tone_and_voice / call_to_action_objective / mandatory_messages[] / prohibited_claims[] / accepted_hypotheses[] / hypotheses_to_test[] / evidence_limitations[] / risk_notes[] / platform_adaptation_rules / workflow_decision；Authoritative Input 仅 approved_strategy_version_id（不得用未审核 Candidate / Strategy Draft / 已撤回或失效 Strategy）；Strategy Lock 六字段受控（可精炼拆分调序、转化为利益点，但不得替换目标用户 / 改变核心需求 / 引入新定位 / 次要升核心 / 创造新竞争优势 / 删除真实证据限制，须改 Strategy 返回 strategy_change_required 回 Human Review）；Communication Objective / Audience（继承 Strategy）/ Core Message / Message Hierarchy（转换链 Fact → Product Capability → User Benefit → Core Message）/ Benefit Hierarchy（1 Primary + 2–4 Secondary，不得凑数）/ Reasons to Believe / Proof Points（须 Proof Point → Valid Fact → Evidence Link → Fragment → Source Version）/ Objection Handling（1–3 障碍，Response 须基于 Fact / Insight / Strategy）/ Content Angles（3–5，须实质差异）/ Tone and Voice（无规范输出 suggested_tone 不得假装品牌确认）/ CTA Objective（平台无关业务目的）；Hypothesis 传播（接受 ≠ 转 Fact，须保留 requires_validation）+ Evidence Limitation 传播（不得删除或弱化）；Mandatory Messages + Prohibited Claims（须传给所有 Platform Adapters）；平台无关（不含小红书标题 / 正文 / Emoji / Hashtags / 封面 / 平台字数 / 热词 / 发布格式 / 最终广告文案）；六组输出 + Workflow Decision 6 值（valid / valid_with_limitations / strategy_change_required / waiting_input / paused / failed）；Brief 修改不使上游失效但使 Xiaohongshu Mapping 失效（承接 DEC-009）；确定性 Validator 23 项为写入 Brief Current Truth 前的必要 Gate；Hard Rules = No Strategy Drift / No unsupported Proof Point / No Hypothesis converted to Fact / No removal of Evidence Limitations / No platform-specific final copy；Amends DEC-006 + DEC-019，不推翻既有结论）**。**平台 Adapter Contract 的 Xiaohongshu Brief Mapping 执行职责（DEC-031：将当前唯一有效的平台无关 Marketing Brief Version + 版本化小红书 Platform Policy Snapshot + 账号与活动上下文映射为结构化、可追溯、可校验的小红书 Execution Brief（方向），作为未来最终文案生成的稳定上游输入；执行链 `Approved Strategy → Marketing Brief → Xiaohongshu Adapter → Xiaohongshu Execution Brief`；Authoritative Input 仅 marketing_brief_version_id（并引用 approved_strategy_version_id / facts_version_id / platform_policy_snapshot_id；不得用未审核 Positioning Candidate / Strategy Draft / 未审核 Brief 草稿或旧版本）；版本化 Platform Policy Snapshot（外部·随时间变化，不得 Prompt 硬编码长期有效规则，每次记录 policy_snapshot_id / policy_version，失效返回 platform_policy_update_required）；Account and Campaign Context（account_type / content_relationship / commercial_context / campaign_objective / available_asset_types[]，输出 review_route_notes / required_qualification_notes / commercial_disclosure_notes，不代替平台审核 / 不保证通过 / 不隐藏商业性质）；Adapter Lock 锁定 audience / core_message / primary_benefit / benefit_hierarchy / proof_points / mandatory_messages / prohibited_claims / hypotheses / evidence_limitations（可调序 / 选笔记形式 / 映射 Content Angle / 调平台语气 / 生成标题封面方向 / 映射搜索意图与 CTA / 加风险注释；不得替换 Audience / 改 Core Message / 改 Benefit Hierarchy / 创新能力或 Proof Point / 删 Evidence Limitation / Hypothesis 转 Fact / 重定义 Strategy / 用热词覆盖事实 / 规避 Prohibited Claims，须改 Brief 返回 brief_change_required）；MVP 输出 Execution Brief（方向）非 Final Post，支持 image_text_note_brief + video_note_brief；Platform Objective Mapping（不得默认立即购买）/ Content Modes（Experience Sharing 仅真实素材 / Comparison Context 不得踩一捧一）/ Title Directions（3–5 方向）/ Cover Direction / Narrative Structure（模块化）/ Content Angle Mapping / Customer Language（真实原声须来自真实 Fragment）/ Experience 边界（不得虚构亲测）/ Tone Mapping（小红书风格 ≠ Emoji / 热词堆砌 / 伪造素人）/ CTA Mapping / Search and Hashtag Directions（仅方向）/ Prohibited Claims 完整继承 + xiaohongshu_specific_risk_notes；六组 Execution Brief 输出（Platform Context / Note Strategy / Content Architecture / Discovery and Interaction / Evidence and Guardrails / Workflow Decision）+ Workflow Decision 7 值（valid / valid_with_limitations / brief_change_required / platform_policy_update_required / waiting_input / paused / failed）；Execution Brief 普通编辑不触发下游失效（当前 MVP 无下游）、改 Brief 返回 brief_change_required（承接 DEC-009 / DEC-030）；确定性 Validator 28 项为写入 Execution Brief Current Truth 前的必要 Gate；Hard Rules = No Strategy Drift / No Marketing Brief Drift / No Fabricated Experience / No unsupported Proof Point / No removal or evasion of Prohibited Claims / No Final Xiaohongshu Copy in MVP；Amends DEC-004 + DEC-020，不推翻既有结论）**。**检索与证据装配运行架构（DEC-032：Hybrid Retrieval and Evidence Runtime 为跨 Skill 共享运行架构层，采用 Direct-first + Retrieval-on-demand + Deterministic Retrieval Planning + Mandatory Permission and Version Filtering + Reproducible Evidence Package；执行链 `Skill Retrieval Request → Deterministic Retrieval Planner → Direct / Lexical / Semantic / Hybrid Retrieval → Candidate Fragments → Evidence Package → Skill → Evidence Validator → Formal Evidence Links`；核心原则 = 能直接读取时不使用检索，需要检索时先限定任务 / 权限 / 商品身份 / 来源范围 / 来源版本再选 Lexical / Semantic / Hybrid，一个高度相关但不属于当前任务或当前允许 Source Set 的 Fragment 必须被排除而不是仅降低排名；检索优先级 Structured Direct Read → Exact ID / Key Lookup → Bounded Direct Document Read → Lexical → Semantic → Hybrid → Optional Reranking（前置能解决就不走后置）；输出 = Candidate Fragments + Retrieval Logs + Evidence Package（不是 Formal Evidence Links / Fact / Insight / Positioning / Approved Strategy）；6 项 Hard Rules = Permission and Source Version filters before relevance / No cross-task retrieval / No Current Product·Competitor leakage / Retrieval result is not Formal Evidence / No Top-K frequency extrapolation / No fabricated answer on zero retrieval；BM25 与 Vector similarity 不同量纲不得直接相加，可用 Rank Fusion 或 Score Normalization + Weighted；Deterministic Retrieval Planner（RetrievalRequest → RetrievalPlan，概念结构）；LLM 可辅助 Query Planning 但不得决定 task_id / 权限 / Source Scope / Source Set Version，精确标识符须逐字保留；Mandatory Metadata Filters 在召回前 / 中生效；Current Product 与 Competitor Source Scope 隔离；Source Set Version 边界；Candidate Fragment / Deduplication / 可选 Reranking / 14 步 Evidence Package Construction / Evidence Coverage（不只 Top 10）/ Dataset Analysis 边界（禁用 Top-K 算总体频率）；降级模式 / Formal Evidence Link 事务边界 / Cache 边界；Hard Reliability 6 项全 = 0%；Amends DEC-014，不推翻既有结论）**。**Workflow Runtime 的失败恢复、重试与可观测性运行架构（DEC-033：分层运行记录 + 结构化错误分类 + 有界 Retry + 显式 Fallback + Safe Checkpoint Resume + 事务幂等提交 + Manual Recovery + 端到端可观测性；运行身份分层 `Task → Workflow Run → Skill Run → Node Execution → Execution Attempt → Validation → Transactional Commit → Checkpoint and Observability`；核心原则 = 业务等待≠技术失败、技术 Retry≠业务 Rerun、Checkpoint≠业务 Current Truth、任何失败恢复都不能绕过业务版本 / Evidence Validator / Review Package / Current Truth 规则；`LangGraph Checkpointer ≠ Business Current Truth Repository`（Checkpointer 只负责执行状态恢复 / Interrupt / Node 进度 / 临时上下文，不保存 Current Truth、不替代业务 Repository、不判断版本有效、不覆盖新状态）；沿用 task_id / thread_id / run_id / checkpoint_id，新增 skill_run_id / node_execution_id / attempt_id / error_id / trace_id / recovery_case_id 形成执行关联链；Retry = 同一逻辑操作 + 同一幂等身份的有界技术重试不建业务版本，Rerun = 新业务计算建新 run_id + skill_run_id；Business Control State（waiting_for_input / waiting_for_review / paused）≠ 技术失败；Error Taxonomy + Severity + Retryability + Failure Disposition；Retry Budget 防嵌套放大；LLM Structured Output Recovery / Evidence Validator Failure / Retrieval Failure（遵循 DEC-032）/ Source Processing Failure / Side-effect Tool 幂等；Timeout 层级（Call / Node / Skill / Workflow Run Deadline）；协作式 Cancellation；Input Fingerprint + 幂等提交；Partial Write Prevention（Candidate→Validation→Atomic Commit）；Checkpoint 职责边界 + Safe Resume + Checkpoint Reconciliation（旧版本 stale 不执行旧计划）；Human Review Resume 须验证 Review Package（不绕过 DEC-029）；显式 Fallback 不静默降级；Circuit Breaker 能力；RecoveryCase + Manual Recovery Queue；Structured Logging + Sensitive Data Boundary + Distributed Tracing + Metrics（Data Integrity 与 Hard Reliability 6 项目标 0% + Observability 完整率 6 项目标 100%）+ Alerting 区分用户 / 运维；Amends DEC-023 / DEC-024 / DEC-029，不推翻既有结论）**。**Technical Spike and Architecture Readiness Gate 已由 DEC-034 确认（Architecture Governance / Technical Validation / Development Readiness）：正式开发前必须完成最小架构 Technical Spike 并经 Architecture Readiness Gate；流程 `Accepted Decisions + Current Specs + Architecture Docs → Technical Spike Plan → Minimal Architecture Prototype → Automated Failure and Recovery Tests → Spike Evidence → Spike Report → Architecture Readiness Review → Explicit User Decision → READY / CONDITIONALLY READY / NOT READY`；用户确认 READY 前 Development Status = NOT READY；Spike 通过≠正式开发；Agent 只能提交 Readiness Recommendation、最终状态须用户明确确认；最小 Mock Workflow（Facts → Insights → Positioning → Review Interrupt → Approved Strategy → Marketing Brief）；至少验证 16 项架构风险；三类 Repository 逻辑分离（Business / Runtime / Checkpoint，`LangGraph Checkpoint Store ≠ Business Current Truth Repository`）；12 个必选 / 可选 Spike 场景；Gate 三值 READY / CONDITIONALLY READY / NOT READY；Mandatory READY Conditions（Business + Architecture Baseline + Spike Reliability + Planning Readiness，关键可靠性任一失败不得 READY）；Blocking Spike Failures（Duplicate Domain Version / Partial Business Write / Resume 覆盖 Current Truth / Stale Review 提交成功 / Stale Checkpoint Resume 成功 / Retry 与 Rerun 无法区分 / Review Resume 无法幂等 / Cancellation 留中间业务状态 / Checkpoint 无法对账 / Recovery 绕过 Validator / Trace 无法关联业务 Commit）；Amends DEC-023 / DEC-033，不推翻既有结论**。**Technical Spike 临时技术栈与执行契约已由 DEC-035 确认（Technical Spike Execution / Temporary Architecture / Validation Environment）：在 DEC-034「必须完成 Technical Spike 并经 Readiness Gate」基础上，定义 Spike-001 的可执行临时栈与 Spike Agent 运行边界；临时栈 = Python 3.13 + 精确固定 LangGraph 1.2.9 + 同步 StateGraph Invoke + 分离式 SQLite（business.sqlite / runtime.sqlite / checkpoints.sqlite）+ SqliteSaver + Python sqlite3 事务（统一 BusinessCommitService，Atomic Commit Contract：Create Domain Version + Formal Evidence Links + Update Current Truth Pointer + Update Stage State + Write Audit + Write Idempotency Record 单一事务任一失败整体回滚，Graph Node 不得绕过 BusinessCommitService）+ Scripted Deterministic Model + Mock Retrieval Runtime + Scenario-based Fault Injection（显式 FaultPlan）+ pytest + Local JSONL Trace（LocalTraceRecorder）+ CLI Scenario Runner；Human Review 节点边界（含 interrupt() 的 Node 在 Resume 可能从头重执行，Review Package 创建与 Interrupt 必须分离 Node：create_review_package → await_human_review → load_approved_strategy，禁止 create_review_package+write_business_data+interrupt() 同 Node）；三类 SQLite 物理分离直接验证 `Business State ≠ Runtime State ≠ Checkpoint State`（仅 Spike 实验存储，非正式数据库设计）；Checkpoint 严格反序列化（LANGGRAPH_STRICT_MSGPACK=true 或等价）；S0—S6 执行阶段（S6 不得自动改 Development Status）；Spike Agent 权限（仅 spikes/spike-001-* + docs/spikes/spike-001-*）与禁止（不得改 Accepted DEC / 创建生产目录·Graph·Roadmap·Epics·Issues / 设 READY / 选生产 DB·Checkpointer·Observability / 用真实用户数据 / 外部 Side Effect / 迁移 Spike 代码到生产；不得擅自更改 LangGraph 1.2.9，失败走 Spike Finding 等用户确认）；Secret 边界（必选场景无需真实 API Key，可选 smoke test 经环境变量注入不落盘）；结果接受边界（每场景须 Automated Assertion + Runtime Evidence + Human-readable Explanation，自然语言「看起来成功」不算 Pass）；**所有临时选择不构成生产承诺（Temporary Spike Architecture ≠ Production Architecture）**；概念运行时形态 `StateGraph → Business Repository → Runtime Repository → Checkpoint Store → Fault Injection → Evidence Export`；Amends DEC-034，不推翻既有结论**。**未**确认工作流节点数量、Skill 与节点最终对应、Checkpointer 类型、数据库、模型（数量 / 是否分模型）、Tool、Skill 实现机制、向量数据库 / 检索实现、Source / Fragment ID 格式、Fragment 切分、Parser / OCR / Embedding、最终状态 Schema、存储实现、Worker 实现框架、State 技术（TypedDict / dataclass / Pydantic）、API / Python 后端框架、前端、部署方式、Observability / LangSmith、前两个 Skill 的最终 Schema / Prompt / 代码、Positioning 的最终 Schema / Prompt / 代码 / 候选相似度与排序算法、其余一个 Core Skill（Marketing Brief）Contract（已由 DEC-030 确认，见 DEC-030 节）、最终 Marketing Brief Schema / Prompt / 代码 / Brief UI / Content Angle 分类表 / Tone 模板 / Brand Guidelines 格式 / 风险词库 / CTA 分类、最终 Review Schema、最终 Approved Strategy Schema、Review UI、Draft 自动保存频率、Patch 或完整 Snapshot、并发锁实现、数据库事务实现、LangGraph Interrupt Payload、API、审核权限、多人协作审核、电子签名、审批链、Review Status 最终枚举名、Review / Hypothesis / Proof Point / Evidence Limitation Decision 最终字段、Audit Record / Withdrawal Record 最终 Schema、具体错误代码、Xiaohongshu Brief Mapping Adapter 最终 Execution Brief Schema / Prompt / 代码 / Execution Brief UI / Platform Policy Snapshot 采集与同步 / Account and Campaign Context 最终结构 / Content Mode 分类表 / Title Cover 模板 / 笔记形式选择规则 / Hashtag 方向数量边界、Final Copy Generator、发布 API、Hybrid Retrieval and Evidence Runtime 的 Embedding 模型 / BM25 / Rank Fusion 算法 / 融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / RetrievalPlan / RetrievalRequest / Candidate Fragment / Evidence Package 最终 Schema、Workflow Runtime 的 Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue·Worker·DLQ 技术 / Logging·Tracing·Metrics·Alerting Provider / 是否采用 OpenTelemetry / Checkpointer 实现 / 数据库 / Outbox / 分布式锁 / 数据保留周期 / 日志采样率 / PII 脱敏实现 / 并发模型 / 最终 SLO、Spike 主执行 Agent / Spike 执行时间计划 / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术（生产后端语言 / 生产数据库 / 生产 Checkpointer / ORM / 生产 LLM / 生产 Retrieval / 生产 Observability / 生产部署平台）。下一议题 Spike-001 Execution Authorization and Agent Handoff Contract（在该议题确认前，不启动 Spike、不安装依赖、不创建 Spike 代码、不运行测试、不创建正式 Roadmap、Development Status 保持 NOT READY）。

---

## 已确认内容（Confirmed）

> 来源：[DEC-011 — 确定性工作流控制流程，LLM 负责受约束的语义分析与业务判断](../decisions/dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（Accepted，Architecture，2026-07-27）

- **总体执行架构（三层职责分工）：**
  - **确定性工作流**：负责流程控制、状态一致性与规则执行；
  - **受约束的 LLM 分析节点**：负责语义理解、信息归纳与业务判断；
  - **人工审核**：负责关键业务结论的最终确认。
- **不采用 LLM 完全自治模式：** 工作流阶段、暂停、恢复、状态失效、局部重跑、最终结果有效性由**显式规则**控制；LLM 不自由决定完整执行路径。
- **确定性程序负责（示例）：** 必填 / 格式 / 文件校验、原始输入保存、来源 ID 分配、阶段记录、状态有效 / 失效 / 待审核标记、审核节点控制、异常暂停恢复、阶段级失效、局部重跑范围、输出 Schema 校验、防止失效结果入最终 Brief、耗时记录、错误重试状态。
- **LLM 负责（示例）：** 事实候选提取、需求 / 动机 / 阻碍归纳、目标用户识别、定位 / 卖点优先级 / 差异化 / 传播策略建议、Brief 草稿、语义冲突判断、假设识别。LLM 输出须符合结构化契约，作为候选事实 / 候选洞察 / 模型推断 / 待验证假设 / 内容草稿进入系统；**未经校验或人工确认的 LLM 输出不得自动成为已确认业务事实**。
- **混合任务模式：** `LLM 判断 → 结构化输出 → 程序校验 → 工作流处理`（适用于事实提取、冲突检测、证据类型分类、卖点策略分析、风险表达检测、Brief 生成）。
- **权限三层：** 程序拥有工作流状态最终控制权（阶段 / 继续条件 / 失效 / 重跑起点 / 暂停 / 契约校验）；LLM 提供语义分析与候选建议、暴露冲突与不确定性，**不拥有工作流状态最终控制权**；用户最终确认关键业务结论（事实 / 目标用户 / 定位 / 卖点优先级 / 传播边界 / 最终 Brief）。

> 注：以上为**高层架构原则**；**未**确认 LangGraph / LangChain 或其他工作流框架、工作流具体节点数量、四层是否一层对应一个节点、是否存在独立 Agent、单 vs Multi-Agent、状态数据模型、Schema 技术、Checkpoint 实现、数据库、风险检测具体规则、LLM 模型与供应商、开源基底仓库。

### Workflow State 原则（DEC-012，Accepted，2026-07-27）

> 来源：[DEC-012](../decisions/dec-012-stage-state-and-structured-business-items.md)

- **系统需要显式 Workflow State：** 采用「阶段级状态 + 关键业务条目结构」两层结构。阶段级状态控制流程位置、阶段有效性、暂停 / 恢复、人工审核、异常处理、阶段级失效、局部重跑范围；关键业务条目结构保存事实 / 洞察 / 推断 / 假设 / 资料不足 / 策略 / 执行 Brief / 来源与主要依据 / 用户修改与审核结果。
- **状态支持阶段、审核、暂停、失效和局部重跑：** 显式保存当前阶段、阶段有效性（valid / invalid）、审核状态、暂停原因、重跑起点；失效与局部重跑以**阶段**为单位（沿用 DEC-009）。
- **状态不只依赖聊天上下文：** Workflow State **不等于**聊天记录 / 单段 Prompt / 最终 Markdown / LLM 上下文临时信息；这些不能成为审核恢复、阶段失效、来源追溯、局部重跑、状态一致性、验收评估的唯一依据。
- **不采用纯文本状态；暂不实现完整字段级依赖图。** 关键结论可保留主要依据，但局部重跑控制单位仍为阶段。

> 注：以上为 Workflow State **结构与原则**；**未**确认 LangGraph State / Pydantic / JSON Schema、最终字段与数据类型、阶段最终枚举、技术节点数量、数据库存储、Checkpoint 实现、跨会话持久化、版本历史、来源片段保存方式、状态迁移规则、并发与任务锁、数据隐私与保存期限、开源基底仓库。文中字段名 / 枚举 / Schema 均为概念示意，非最终数据契约。

### 任务级持久化与跨会话恢复（DEC-013，Accepted，2026-07-27）

> 来源：[DEC-013](../decisions/dec-013-task-level-persistent-state-and-cross-session-resume.md)

- **每个业务流程作为独立持久化任务：** 每次商品分析流程拥有稳定 `task_id`；在关键阶段保存 Workflow State（任务创建 / 来源处理 / 草稿生成 / 进入审核 / 用户修改确认 / 阶段失效 / 局部重跑 / 最终 Brief / 异常）。
- **工作流支持暂停、稍后恢复和局部重跑：** 用户可关闭页面 / 结束会话后重新打开任务，恢复审核、提交修改、从正确阶段继续、重生成已失效下游阶段；恢复时不得丢失原始输入 / 来源 / 用户修改、不得把失效重标为有效、不得从错误阶段执行或新建无关任务。
- **重要状态不只存在于内存和聊天上下文：** 任务状态**不得**只存在于单次 HTTP 请求、LLM 上下文窗口或进程内存；内存仅用于节点临时变量 / 请求缓存 / 无业务意义中间结果。
- **MVP 暂不实现完整事件溯源与任意历史版本恢复**（保留运行历史与修改记录，但不作为首版前置条件）。

> 注：以上为**持久化与恢复原则**；**未**确认 LangGraph Checkpointer / thread_id / PostgreSQL / SQLite / Redis / 关系库+对象存储组合 / Checkpoint 频率 / 序列化方式 / 文件持久化 / 任务保留期限 / 删除机制 / 隐私权限 / 并发编辑 / 任务锁 / 版本 UI / 开源基底仓库。Task Lifecycle 与状态名为概念示意，非最终枚举。

### 分层数据访问与按需混合 RAG（DEC-014，Accepted，2026-07-27）

> 来源：[DEC-014](../decisions/dec-014-on-demand-hybrid-rag-and-layered-data-access.md)

- **系统采用分层数据访问：** 按数据类型 / 规模 / 查询目的选择访问方式——结构化业务数据精确直读（不强制向量化）；短资料直接解析或全文使用；长文档 / 多资料 / 大量评论用关键词 + 语义混合检索；运营方法与平台知识用独立知识库按需检索。任务证据（商品与用户资料实际内容）与运营知识（分析方法）逻辑分离，不得混淆。
- **RAG 是证据检索能力：** 负责按当前任务寻找相关资料、返回真实来源与可定位证据片段、支持来源引用、为 LLM 提供相关上下文；检索结果作为带来源的证据片段写入 Workflow State。
- **RAG 不控制工作流：** 不负责流程阶段 / 继续 / 审核 / 暂停恢复 / 失效判断 / 重跑位置 / 事实确认 / 最终业务决策；RAG 返回**候选证据**，须经 LLM 分析 + 程序校验 + 必要时人工审核。
- **检索结果进入结构化 Workflow State：** 与 DEC-008 证据标记衔接（来源 ID / 片段 / evidence_type / source_refs）；按需触发（由确定性工作流决定），非每步必检。

> 注：以上为**数据访问策略与 RAG 职责边界**；**未**确认具体向量数据库 / Embedding 模型 / BM25 实现 / Reranker / Chunking / Top-K / 混合检索权重 / GraphRAG / 供应商文件检索 / 联网搜索 / 知识库更新方式 / 短长资料阈值 / RAG 触发规则 / 最终数据契约 / 开源基底仓库。检索结果字段为概念示意，非最终契约。

### Skill 作为业务能力层（DEC-015，Accepted，2026-07-27）

> 来源：[DEC-015 — Skill 定义为带执行契约的可复用业务能力包](../decisions/dec-015-contract-based-reusable-business-skills.md)

- **Skill 是架构中的业务能力层概念：** Skill = 面向特定业务目标、带执行契约（输入契约 + 执行步骤 + 工具依赖 + 输出契约 + 确定性校验 + 失败暂停条件 + 评价标准）的可复用业务能力包。它把稳定、可复用的业务处理方式从整个工作流中分离出来，使每项能力可被定义、约束、校验、测试和复用。
- **Skill 可由确定性工作流或 Agent 调用：** Skill 与工作流节点不要求一一对应——一个节点可调用一个 Skill、一个阶段可调用多个 Skills、同一个 Skill 可被不同节点复用；Skill 也不要求必须由独立 Agent 调用（确定性工作流可直接调用 Skill）。这承接 DEC-011 的控制分工：调用时机与执行路径由确定性工作流控制，Skill 内部的语义分析由受约束 LLM 完成、输出须经校验与审核。
- **Skill 与 Prompt / Tool / Node / Agent 的边界已定义：** Prompt 仅为 Skill 组成部分；Tool ≠ Skill；Skill ≠ 节点（**不得解释为每个 Skill 必须是一个 LangGraph Node**）；Skill ≠ 独立 Agent；不得为增加 Agent 数量而人为拆分 Skill。
- **Skill 的具体运行框架未确认：** Skill 注册 / 发现、运行时动态选择、Skill Spec 最终模板、代码接口、目录结构、版本机制、测试框架，以及是否使用 Anthropic Skills / OpenAI Skills / MCP / LangGraph / LangChain Tools 等具体实现**均未决定**。

> 注：本节确认 Skill 作为**业务能力层**的概念位置与边界；**不**确认其具体运行框架、目录与代码接口。Skill 的详细定义见 DEC-015 与 [../agents/README.md](../agents/README.md)、[../agents/skill-spec-template.md](../agents/skill-spec-template.md)。

### MVP 业务能力范围（DEC-020，Accepted，2026-07-28）

> 来源：[DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](../decisions/dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)

- **MVP 业务能力层 = 4 个 Core Skills + 1 个 Platform Adapter**：由确定性 Workflow Controller 编排，链路为 `Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation → Xiaohongshu Brief Mapping`。前四项为平台无关核心能力，小红书映射为平台适配层。
- **共享能力不包装为独立业务 Skill：** Document Parsing、Hybrid Retrieval、Source Management、Task Persistence、Stage Invalidation、Partial Rerun 属于共享能力 / 基础设施；Schema Validation 属确定性 Validator / Tool；Risk Validation 采用嵌入式校验（不创建独立 Compliance Review Skill）。这些承接 DEC-011~014 已确认的控制 / 状态 / 持久化 / 检索职责分工。
- **Product Input Assessment 与 Product Fact Extraction 合并**为单个 Product Intake & Fact Extraction Skill。
- **保留一个常规强制人工审核 Gate**（与 DEC-007 一致），位于 Positioning 之后、Marketing Brief 之前；不增加第二个 Gate。
- **Visual Execution Brief / Storyboard / 主图详情页 / 生图 / 自动发布不进入首版 MVP**，保留为 Future Extension。

> 注：本节确认 MVP **业务能力范围与分类**（哪些能力是 Core Skill / Platform Adapter / 共享能力 / Validator / Future），承接 DEC-015 Skill 定义。**不**确认四个 Skills 的最终名称 / Schema / Specification、Skill 代码接口 / 注册机制 / 运行框架、Skill 与工作流节点的一一对应、节点数量、Agent 数量、Multi-Agent、LangGraph / 其他框架、模型与数据库、前后端技术栈。

### Agent 架构形态（DEC-021，Accepted，2026-07-28）

> 来源：[DEC-021 — MVP 不采用 Multi-Agent 主架构，保留评测驱动的受约束并行 Worker 扩展](../decisions/dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)；研究记录：[../research/multi-agent-architecture-assessment.md](../research/multi-agent-architecture-assessment.md)。

- **一个统一用户侧 Agent：** 产品对用户呈现为统一 `Ecommerce Strategy Agent`（产品交互身份）；用户无需理解内部 Prompt / 节点 / 模型调用 / 工具数量。统一 Agent **不代表**所有任务由一次 LLM 调用完成。
- **确定性主工作流编排：** 内部由确定性 Workflow Controller 管理执行顺序 / 阶段 / 阶段有效性 / 暂停恢复 / 人工审核 / 下游失效 / 局部重跑 / 错误处理 / 重试 / 持久化 / Skill 调用 / Adapter 调用。承接 DEC-011 控制分工。
- **Skills 不等于独立 Agent：** 四个 Core Skills 可拥有独立 Prompt / 模型配置 / 工具 / 输出 Schema，但**不拥有独立流程控制权**——它们是 **Skill-specialized LLM Node**，而非自治 Agent。即 `Skill ≠ Agent`、`多次 LLM 调用 ≠ Multi-Agent`（承接 DEC-015）。
- **不存在 LLM Supervisor：** MVP **不创建** LLM Supervisor Agent；工作流路由由代码与状态决定，**不采用**「Supervisor LLM 自由判断下一步调用哪个 Agent」。
- **未来 Worker 不能控制主流程：** 未来仅在真实并行需求 + 对照评测证明收益超过成本时，于特定节点内部引入「中心化 Orchestrator + 受约束并行 Worker」；Worker 只接收有限输入、返回结构化输出、不控制主工作流、不直接修改最终状态、输出经汇总校验。
- **主 Workflow State 是唯一当前任务状态来源：** LLM、Skill 或未来 Worker 不得自行修改完整工作流顺序或另立任务状态（承接 DEC-012 / DEC-013）。

> 注：本节确认 MVP 的 **Agent 架构形态**（统一 Agent + 确定性编排 + 契约化 Skill；不采用 Multi-Agent / Supervisor）；**不**确认 Workflow Controller 具体框架（LangGraph / OpenAI Agents SDK / LangChain / 自研状态机）、CrewAI / AutoGen、工作流节点数量、Skill 与节点最终对应、Worker 实现框架、独立 Evaluator 是否进 MVP、并行评论处理是否进 MVP、模型数量 / 是否分模型、基底仓库、模型供应商、前后端技术栈。系统应被描述为 `Stateful Agentic Workflow`，**不**描述为 `Multi-Agent E-commerce Platform`。

### 工作流框架能力需求（DEC-022，Accepted，2026-07-28）

> 来源：[DEC-022 — Workflow Framework Capability Requirements](../decisions/dec-022-workflow-framework-capability-requirements.md)

工作流框架首先被评估为**有状态、确定性、可持久化的业务工作流运行时**，而**不是** Multi-Agent 协作框架。具体框架**仍未选择**；后续候选必须按 DEC-022 的 Must-have / Should-have / Could-have / Anti-requirements、100 分制评分维度与淘汰条件评估，**不得仅依据**流行程度 / GitHub Star / Multi-Agent Demo / 单一厂商宣传 / 个人偏好。

```text
Workflow Runtime Requirements
- Structured domain state
- Deterministic routing
- Persistent pause and resume
- Human review state write-back
- Stage invalidation
- Partial rerun
- Node-level validation
- Node-level retries
- Task-level observability
```

- **强制能力（Must-have 1–10）：** 显式结构化 Workflow State；确定性路由；暂停与恢复；Human-in-the-loop（含修改回写 Domain State 与触发下游失效）；阶段失效与局部重跑（承接 DEC-009）；节点级契约（Input/Output Schema + 前置/校验/失败/重试）；节点级重试与错误恢复（区分可自动重试与不应盲目重试的错误）；任务级持久化；幂等与并发保护；任务级可观测性。承接 DEC-011 / 012 / 013 / 014。
- **应具备能力（Should-have 1–8）：** Domain State 独立于框架；单节点可独立测试；Skill 逻辑与运行时解耦（`Workflow Node Adapter → Business Skill Service → LLM / Retrieval / Validator`）；节点级模型与工具配置（属项目配置层，不被框架硬编码）；异步与长耗时执行；业务进度事件；版本元数据；未来受约束 Worker（次要扩展，非 MVP 选型首要因素）。
- **框架职责边界：** 框架只承担状态 / 路由 / 暂停恢复 / 人工审核节点 / 重试 / 阶段有效性 / 局部重跑 / 持久化 / 运行历史 / 进度事件；**不**承担业务 Skill、LLM 语义分析、确定性校验器、数据库存储或前端职责；**不**通过 LLM Supervisor 自由决定主业务流程（与 DEC-021 一致）。

> 注：本节确认**工作流框架的能力需求与选型标准**（含 100 分制评分维度与淘汰条件）；**不**选择任何具体框架（LangGraph / OpenAI Agents SDK / LangChain / CrewAI / Temporal / 自研状态机）、编程语言、数据库、Checkpointer、任务队列、Observability 产品、部署方式、前后端技术栈。框架选择须待候选研究与比较（下一议题 `Workflow Framework Candidate Research and Comparison`）形成 Recommendation 并经用户确认后，才作为单独 Decision。

### 工作流运行框架与主要建模方式（DEC-023，Accepted，2026-07-28）

> 来源：[DEC-023 — MVP 选择 LangGraph StateGraph 作为核心工作流运行方式](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)；研究记录：[../research/workflow-framework-candidate-comparison.md](../research/workflow-framework-candidate-comparison.md)；Spike 规划：[../spikes/langgraph-stategraph-workflow-spike.md](../spikes/langgraph-stategraph-workflow-spike.md)。

MVP 正式选择 **LangGraph** 作为工作流运行框架，以 **StateGraph / Graph API** 作为核心业务流程的主要建模方式（`State + Nodes + Edges + Conditional Edges + Checkpoint + Interrupt / Resume`）。StateGraph 是 LangGraph Graph API 的核心 Builder（`compile()` → `CompiledStateGraph`），**不是** LangGraph 的竞品或替代；Functional API 仅用于可选局部简单任务，**不**作为主流程主要表达。

```text
Workflow Runtime:
LangGraph

Primary Workflow API:
StateGraph / Graph API

Runtime Responsibilities:
- Node orchestration
- Conditional routing
- Checkpoint
- Interrupt
- Resume
- Retry
- Execution recovery

Independent Layers:
- Domain State
- Skill Services
- Validators
- Business Database
- Retrieval
```

- **LangGraph 仅是运行时与编排层，不是业务 Domain Layer：** 主流程**不**由 ReAct Agent / LLM Supervisor / 多自治 Agent 控制（承接 DEC-021）。阶段失效由 **Domain Layer 定义**，StateGraph 仅据失效状态决定从哪里继续；LangGraph Checkpoint / Replay / Time Travel **不能替代**项目自己的业务失效规则（承接 DEC-009）。
- **五层架构边界：** LangGraph Layer（图定义 / 编排 / 条件路由 / Checkpoint / Interrupt / Resume / 重试 / 恢复 / 进度事件）→ Node Adapter Layer（State↔Skill 转换，不含业务逻辑）→ Skill Service Layer（可脱离 LangGraph 独立测试，承接 DEC-015）→ Domain Layer（`ProductFact` / `CustomerInsight` / `PositioningCandidate` / `MarketingBrief` / `XiaohongshuBrief` / `SourceReference` / `ReviewDecision` / `StageStatus` / `Invalidation Rules` / `Domain Errors`，**不**继承 LangGraph 类型）→ Persistence Layer（Checkpointer 仅承载执行恢复 / 图状态快照 / Interrupt / Resume；Business Database 承载正式 Current Truth / 来源 / 用户修改 / 当前有效版本 / 审计记录；Object Storage 原始文件；Retrieval Index 检索——**不得**以 Checkpoint 库为唯一业务数据库）。
- **State / Reducer 暂定原则：** 阶段主结果（facts / insights / positioning / brief）默认整体替换 + 显式版本 + 业务 Repository 幂等写入，**不**默认自动 Append；Runtime Events（node_started / node_completed / retry / error）可 Append-only；用户修改须显式覆盖或新建业务版本。**Interrupt Safety：** Interrupt 前操作必须幂等、不可逆操作不放在 Interrupt 前、写入用幂等键、审核拆为 Prepare / Interrupt / Apply 三节点。**Graph Complexity Control：** 核心图只表达少量大阶段，不为每个缺失字段 / 风险词 / 评论主题 / Prompt 步骤 / 内部转换单独建 Node。**Framework Lock-in Protection：** `LangGraph Node Adapter → 框架无关 Skill Service → Domain Models / Repositories / LLM Gateway`。
- **强制 Technical Spike：** 正式业务实现前必须先完成最小工作流验证（Fake Workflow：`START→Fake Fact→Fake Insight→Fake Positioning→Prepare Review→Human Review Interrupt→Apply Review Decision→Fake Brief→END`；18 项 Must Prove；9 条 Failure Conditions；失败则重新比较 LangGraph vs 自研状态机，不擅自继续实现）。
- **概念主流程（节点数与最终图结构待 Workflow State 与 Skill Contract 设计完成后确定）：** `START → Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Prepare Human Review → Human Review Interrupt → Apply Review Decision → Marketing Brief Generation → Xiaohongshu Brief Mapping → END`。

> 注：本节确认**工作流运行框架与主要建模方式**（LangGraph + StateGraph / Graph API；不采用 ReAct Agent / Supervisor / 多自治 Agent 主流程）。**仍待确认**：工作流节点数量与最终图结构、Workflow State 最终 Schema、State 技术（TypedDict / dataclass / Pydantic）、Reducer 规则、State Version、Node Adapter 接口、Skill Service 接口、Human Review Payload、Checkpointer 类型、数据库、task_id↔thread_id 映射、模型、LLM Gateway、API / Python 后端框架、前端、部署方式、Observability / LangSmith、Worker 实现框架、Spike 实现细节。本节**不**包含正式业务实现，**不**对 Checkpointer / 数据库 / FastAPI / Next.js / LangSmith / 模型供应商 / Embedding / 向量数据库进行选型。

### 四类状态边界与版本化领域状态（DEC-024，Accepted，2026-07-28）

> 来源：[DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)；概念规格：[../specs/workflow/workflow-state-specification.md](../specs/workflow/workflow-state-specification.md)。Amends DEC-012 / DEC-013。

状态架构正式划分为 **Domain State + Workflow State + Runtime State + Interaction State** 四类（承接 DEC-012 两层状态、DEC-013 任务级持久化、DEC-023 Checkpoint 与业务库分离）。四个标识符边界：

```text
task_id
→ Product business identity

thread_id
→ LangGraph execution context

run_id
→ One invocation or resume

checkpoint_id
→ Runtime snapshot
```

- **`task_id`（稳定产品业务身份）：** 长期稳定、属 Domain Layer、与 LangGraph 框架无关、用于业务查询 / 权限 / 审计 / 历史任务；**不因 Resume 或重新运行而改变**。
- **`thread_id`（LangGraph 执行上下文）：** 用于 Checkpoint / Interrupt / Resume / State History / 可选 Replay 或 Fork。`task_id` 与 `thread_id` **不得**定义为相同概念；MVP 约定一个 `task_id` → 一个当前活跃 `thread_id`；未来一个 Task 可关联主执行 / 历史分支 / 测试重跑 / 数据迁移 / 恢复 Thread。
- **`run_id`（一次调用或恢复）：** 表示一次工作流调用或恢复执行（如 START→Review = run_id_1；Resume→完成 = run_id_2；改 Fact 重跑 = run_id_3）。
- **`checkpoint_id`（Runtime 快照）：** LangGraph Checkpointer 管理的具体执行快照；属 Runtime Layer，**不作**产品主要业务 ID、**不**替代业务版本 ID、**不**作前端主要导航身份。
- **版本化 Domain Objects + Current Truth Pointers：** 正式业务结果不得直接覆盖，均创建新版本；Task 级显式保存当前有效版本指针；失效须显式 InvalidationEvent（承接 DEC-009）。
- **LangGraph State 紧凑 + 引用为主：** State 优先保存版本引用而非复制业务内容；完整 PDF / 二进制 / 评论原文 / Embedding / 向量 / 历史版本存 Business Database / Object Storage / Retrieval Index / Run Log。前端正式查询以业务数据库为准（**不**以 Checkpoint 库为产品查询 API）。
- **统一 Stage State + 结构化 Review State：** 各阶段采用统一 StageState（status / current_version_id / last_valid_version_id / based_on_versions / invalidation 等）；Human Review 使用结构化 ReviewState（承接 DEC-007 单审核 Gate）。

> 注：本节确认**四类状态边界与版本化领域状态**（Amends DEC-012 / DEC-013，不推翻既有结论）；详细数据职责分层见 [data-architecture.md](data-architecture.md) DEC-024 节，概念 Schema 见 [../specs/workflow/workflow-state-specification.md](../specs/workflow/workflow-state-specification.md)。**仍待确认** 工作流节点数量与最终图结构、Workflow State 最终 Schema、State 技术（TypedDict / dataclass / Pydantic）、Reducer / State Version、Node Adapter 接口、Checkpointer 类型、数据库、Review Payload、并发控制、事务边界。本节**不**创建正式业务实现，**不**选择 Checkpointer / 数据库 / ORM。

---

## 当前状态

- 项目处于 **正式开发前策划阶段**；Business / Production Implementation 与 Goal 仍未授权。
- 已确认多条架构与 Agent 原则：控制分工（DEC-011）、Workflow State 结构（DEC-012）、任务级持久化与恢复（DEC-013）、分层数据访问与按需混合 RAG（DEC-014）、Skill 契约化定义（DEC-015）、外部 Skill 复用策略（DEC-016）与首轮三候选评估（DEC-017~019）、MVP 业务能力范围（DEC-020）、Agent 架构形态（DEC-021：统一 Agent + 确定性编排，**不采用** Multi-Agent）、工作流框架能力需求与选型标准（DEC-022：含 Must-have/Should-have/100 分制评分维度/淘汰条件）、**工作流运行框架与主要建模方式（DEC-023：LangGraph + StateGraph / Graph API）**。
- 仍未确认：工作流节点数量与最终公共 Schema、向量库 / 检索实现、API 框架与协议、前端、部署方式、Observability。**工作流框架已由 DEC-023 选定为 LangGraph；生产持久化与 Checkpointer 已由 RFC-002 / 003 冻结；Provider / Port / Structured Output / Recovery / Version / Profile / Secret / Payload / Test / Smoke 已由 DEC-052～054 与 RFC-006 冻结。**
- 本文件的具体架构内容，必须等到对应 Proposed Decision 被用户明确接受并记为 Accepted Decision（见 [../decisions/](../decisions/)）后，才能写入。

---

## 文档骨架（占位，内容待填充）

> 以下章节标题仅作为未来结构占位，**当前全部为空**，不构成任何架构声明。

- 架构总览（组件与关系）
- Agent 编排方式（单 Agent / Multi-Agent；是否使用 LangGraph）
- RAG 子系统
- Skill 机制
- 开源底座与改造范围
- 运行与部署形态

---

## 待讨论的开放问题（系统架构相关）

> DEC-011 已确认「确定性 / LLM / 人工审核」的职责分工原则；以下**具体技术选型与节点划分仍开放**：

- 工作流具体节点数量、四层是否一层对应一个节点？（DEC-011 未确认）
- ~~单 Agent 还是 Multi-Agent？是否存在独立 Agent？~~ **已由 DEC-021 确认：MVP 不采用 Multi-Agent 主架构；统一用户侧 `Ecommerce Strategy Agent` + 确定性工作流编排；四个 Skills 为 Skill-specialized LLM Node 而非自治 Agent；不创建 LLM Supervisor。** 具体 Workflow Controller 框架仍开放。
- ~~是否采用 LangGraph / LangChain 或其他工作流框架？~~ **已由 DEC-023 确认：MVP 选择 LangGraph 作为工作流运行框架，以 StateGraph / Graph API 作为核心业务流程主要建模方式；不采用 ReAct Agent / LLM Supervisor / 多自治 Agent 主流程；Functional API 仅用于可选局部简单任务；OpenAI Agents SDK 不作主运行时、Temporal 不进 MVP、自研状态机为降级方案；正式实现前必须完成 Technical Spike。** 选型标准与淘汰条件见 DEC-022。工作流节点数量、最终图结构、Workflow State Schema、Checkpointer / 数据库、模型等仍开放（下一议题 `Workflow State Specification`）。
- 状态数据模型、Schema 技术、Checkpoint 实现、数据库？
- RAG 的具体实现方式与职责边界？
- Skill 的具体实现机制（**定义已由 DEC-015 确认**：带执行契约的可复用业务能力包；注册 / 发现 / 目录 / 代码接口 / 运行框架仍开放）/ Tool 的具体定义与机制？
- 风险表达检测的具体规则？
- LLM 模型与供应商？
- 使用哪个开源项目作为底座？改造范围？

这些属于重大、跨模块、难回滚议题，通常应通过 RFC 讨论（见 [../rfcs/](../rfcs/)）。DEC-011 当前**不创建 RFC**；后续比较工作流框架、状态持久化与暂停恢复方案后再判断。

讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得擅自选择框架 / 数据库 / 模型 / 第三方服务。
- 不得为使文档「完整」而补充未经讨论的架构。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
