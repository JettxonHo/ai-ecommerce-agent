# Agents（Agent 规格）

本目录是 Current Truth Layer 的一部分，存放 AI Ecommerce Agent 项目中各 Agent 的规格说明。

> **当前状态（用户决策后）：** Spike Execution Status = **COMPLETED** · Architecture Readiness Status = **CONDITIONALLY READY**（用户已确认，User Decision 记录于 [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md) §16）· Development Status = **CONDITIONALLY READY**（**仅限**规划与治理范围）。
> **授权范围：** Architecture RFC · Technical Research · Additional Technical Spike · Implementation Planning · MVP Roadmap 草案 · Epic and Dependency Planning · Acceptance Criteria Planning · Technical Risk Resolution。
> **禁止范围（当前不授权）：** Production Business / Database / API / Retrieval / LLM Runtime / Observability Implementation；正式业务 Coding Issues；未经 RFC 支持的生产实现；Coding Agent 临场选择生产数据库 / ORM / Checkpointer / API / Retrieval / LLM Runtime / Observability；将 Spike 代码迁移为生产模块；将状态更新为完全 READY。
> **下一议题：** **FND-002 Pull Request Review and Merge Gate**。**RFC-001 已于 2026-07-30 被用户正式接受（`ACCEPTED`）**，DQ-01~DQ-10 全部接受且 Final Consistency Review 通过。**FND-001 = COMPLETED**（PR #7 已由用户 Merge，Merge Commit `5b75bcf`）。**FND-002 已经用户明确授权「确认授权创建并实施 FND-002」**（2026-07-30）：Issue #9 已创建，Branch `foundation/002-architecture-test-foundation`，FND-002 Status = IN IMPLEMENTATION，Merge = USER DECISION REQUIRED。**FND-003 = READY, BLOCKED BY FND-002**，Issue Creation 与 Implementation 均未授权；Foundation（除单项授权外）/ Business / Production Implementation 未授权。**下一 Gate：FND-002 PR 完成验证后由用户审查并决定 Merge；Coding Agent 不得自行 Merge；该授权不包括 FND-003 或任何业务实现；FND-002 完成并合并前不创建 FND-003 Issue、不开始 FND-003 实施。**Architecture Readiness 保持 **CONDITIONALLY READY**。详见 [../foundation/foundation-issue-candidates.md](../foundation/foundation-issue-candidates.md) 与 [../rfcs/rfc-register.md](../rfcs/rfc-register.md)。

---

## 定位

- Agent Spec 描述「某个 Agent 当前应该怎样工作」：职责、边界、输入输出、可用 Skill、依赖与失败模式。
- Agent Spec 的内容只能来自用户明确接受的 Decision。
- **当前没有任何已确认的具体 Agent 规格（Agent Spec）**；但已确认：MVP **不采用** Multi-Agent 主架构，产品对用户呈现为统一 `Ecommerce Strategy Agent`，内部由确定性 Workflow Controller 编排（DEC-021，见下）；工作流框架须满足 DEC-022 的能力需求（State-first / 确定性 / 持久化 / HITL / 阶段失效 / 局部重跑 / 节点级契约 / 可测试 / 可观测）；工作流运行框架已由 DEC-023 选定为 LangGraph（StateGraph / Graph API），主流程不采用 ReAct Agent / LLM Supervisor / 多自治 Agent，LangGraph 仅作运行时与编排层（非业务 Domain Layer）；**Workflow State 架构已由 DEC-024 确认为「版本化 Domain State + 紧凑 LangGraph State + Runtime Checkpoint + 派生 Interaction State」四类边界，Skill 与 Human Review 须基于版本引用与结构化 ReviewState 工作（不读 Checkpoint、不静默覆盖业务结果）**；**来源与证据架构已由 DEC-025 确认为 `Source → Source Version → Document / Record → Fragment → Evidence Link → Versioned Domain Object` 分层，Skill 须基于 Evidence Package（候选 Fragment 允许集合）工作、LLM 不得自由生成 Source/Fragment ID、所有引用须经确定性 Evidence Validator 校验后才写入 Evidence Link**；**首个核心业务 Skill Contract（Product Intake & Fact Extraction）已由 DEC-026 确认：合并输入诊断与事实提取、Hard Rule = No Fact without a valid current-product Fragment、四档输入完整度（非模型百分制）、声明五分类（direct_fact / documented_claim / certified_or_tested_fact / marketing_expression / unknown_or_ambiguous）、模型不得创造 Explicit Fact、关键身份/规格/SKU/认证/来源冲突须暂停交用户、确定性 Validator 15 项校验为写入 Facts Current Truth 前的必要 Gate、不使用模型数字 Confidence；**第二个核心业务 Skill Contract（Customer Insight Analysis）已由 DEC-027 确认：采用 Evidence-backed Mode + Degraded Hypothesis Mode、必须区分 Theme 与 Insight、支持 4 类证据（Direct / Competitor / Indirect / Non-customer，竞品反馈不能证明当前商品用户）、Evidence Coverage 5 状态（none / anecdotal / repeated_signal / dataset_supported / multi_source_corroborated，不用模型百分制 Confidence）、不设统一样本门槛且单条反馈只能 Anecdotal Signal、Hard Rules = No fabricated customer quote / No Top-K frequency extrapolation / No competitor feedback misattribution / No unsupported consensus claim、正式频率必须由确定性统计产生、用户原声必须来自真实 Fragment 并经 Evidence Validator、Insights Version 须经 Validator 18 项校验才写入 Insights Current Truth、不使用模型单一综合 Confidence**；**第三个核心业务 Skill Contract（Product Positioning）已由 DEC-028 确认：采用多候选（默认 3、允许 2–4、必须实质差异）、Positioning 属 Strategic Inference 非 Explicit Fact、Positioning Elements（Target Segment / Usage Context / Job or Core Need / Category Frame / Value Proposition / Differentiation / Reasons to Believe / Proof Points）、Hard Rules = No Proof Point without a valid Fact / No competitor capability attributed to current product / No hypothesis presented as verified customer truth / No automatic final positioning decision、Proof Point 必须回溯到有效 Fact、竞品证据只能用于 Gap 和 Context、不使用不透明综合数字分数（改用可解释 7 维排序）、Insight `valid_with_limitations` 时进入 Limited Evidence Mode 传播证据限制、输出五组 + 强制 Human Review、Approved Strategy Version 才能进入 Marketing Brief、确定性 Validator 20 项校验为进入 Human Review 前的必要 Gate；Amends DEC-018**；**强制 Human Review 与 Approved Strategy Contract 已由 DEC-029 确认：采用版本化 Review Package（固定上游版本）+ 结构化用户决策 + 18 步原子提交事务；8 项 Review Actions（select / edit / merge / reject / request_more_information / save_draft / submit / withdraw）；Strategy Draft（不属 Current Truth）与 Approved Strategy Version（Marketing Brief 唯一战略输入）分离；Hypothesis 接受 ≠ Hypothesis→Fact；Evidence Limitations 不得静默删除；Proof Point 须完整追溯；Hard Rules = No Approved Strategy without explicit submission / No stale Review Package submission / No unsupported Proof Point / No automatic Hypothesis approval；Amends DEC-007 + DEC-024，不推翻既有结论**；**第四个核心业务 Skill Contract（Marketing Brief Generation）已由 DEC-030 确认：将当前唯一有效 Approved Strategy Version 转换为结构化、平台无关、可追溯的 Marketing Brief，为 Xiaohongshu 及未来其他平台 Adapter 提供稳定输入；Authoritative Input 仅 `approved_strategy_version_id`（不得用未审核 Candidate / Strategy Draft / Model Recommendation / 已撤回或已失效 Strategy / 历史旧版本 Strategy）；Strategy Lock 六字段受控（target_segment / usage_context / job_or_core_need / category_frame / value_proposition / differentiation，可精炼表达 / 拆分 / 调传播顺序 / 转化为利益点与内容角度，但不得替换目标用户 / 改变核心需求 / 引入新定位 / 次要能力升核心 / 创造新竞争优势 / 删除真实证据限制；须改 Strategy 则返回 `strategy_change_required` 回 Human Review）；MarketingBrief 概念对象（brief_id / brief_version_id / approved_strategy_version_id / facts_version_id / insights_version_id / communication_objective / audience / audience_context / core_message / message_hierarchy / benefit_hierarchy / key_benefits[] / reasons_to_believe[] / proof_points[] / objections[] / objection_responses[] / content_angles[] / tone_and_voice / call_to_action_objective / mandatory_messages[] / prohibited_claims[] / accepted_hypotheses[] / hypotheses_to_test[] / evidence_limitations[] / risk_notes[] / platform_adaptation_rules / workflow_decision）；Communication Objective（主+次级，不得全部同优先级，未明时候选标 business_assumption）/ Audience（必须继承 Strategy，Target Segment 为 Hypothesis 时继续标记）/ Core Message（一句话，与 Approved Value Proposition 一致，不含无证据承诺）/ Message Hierarchy（Primary Message → Secondary Benefits → Supporting Proof，转换链 Fact → Product Capability → User Benefit → Core Message）/ Benefit Hierarchy（1 Primary + 2–4 Secondary，资料不足不得凑数）/ Reasons to Believe / Proof Points（须建立 Proof Point → Valid Fact → Evidence Link → Fragment → Source Version 追溯链）/ Objection Handling（1–3 障碍，Response 须基于 Fact / Insight / Strategy，证据不足标 insufficient_evidence）/ Content Angles（3–5，须实质差异）/ Tone and Voice（无规范时输出 suggested_tone，不得假装品牌确认）/ CTA Objective（平台无关业务目的）；Hypothesis 传播（接受 ≠ 转 Fact，须保留 requires_validation=true）+ Evidence Limitation 传播（不得删除或弱化）；Mandatory Messages + Prohibited Claims（须传给所有 Platform Adapters）；平台无关边界（不含小红书标题 / 正文 / Emoji / Hashtags / 封面文字 / 平台字数 / 热词 / 发布格式 / 最终广告文案）；六组输出（Brief Context / Audience and Message Architecture / Evidence and Trust / Creative Direction / Guardrails / Workflow Decision，6 值 valid / valid_with_limitations / strategy_change_required / waiting_input / paused / failed）；Brief 编辑（→ 新 Brief Version + 保留原模型版本 + 重跑 Validator + 更新 Pointer；承接 DEC-009：Brief 修改不使 Facts / Insights / Positioning / Approved Strategy 失效但使 Xiaohongshu Mapping 失效；改 Strategy 返回 strategy_change_required；MVP 不增第二个强制 Review Gate）；确定性 Validator 23 项为写入 Brief Current Truth 前的必要 Gate；Hard Rules = No Strategy Drift / No unsupported Proof Point / No Hypothesis converted to Fact / No removal of Evidence Limitations / No platform-specific final copy；Amends DEC-006 + DEC-019，不推翻既有结论**；**平台 Adapter Contract（Xiaohongshu Brief Mapping）已由 DEC-031 确认：将当前唯一有效的平台无关 Marketing Brief Version + 版本化小红书 Platform Policy Snapshot + 账号与活动上下文映射为结构化、可追溯、可校验的小红书 Execution Brief（方向），作为未来最终文案生成的稳定上游输入；边界明确 Business Skill 决定讲什么、Platform Adapter 决定在小红书上如何组织和呈现；Authoritative Input 仅 `marketing_brief_version_id`（并引用 approved_strategy_version_id / facts_version_id / platform_policy_snapshot_id；不得用未审核 Positioning Candidate / Strategy Draft / 未审核 Marketing Brief 草稿或旧版本）；版本化 Platform Policy Snapshot（外部·随时间变化，不得在 Prompt 硬编码假设长期有效规则，每次执行记录所用 Snapshot，失效返回 platform_policy_update_required）；Account and Campaign Context（account_type / content_relationship / commercial_context / campaign_objective / available_asset_types[]，输出 review_route_notes / required_qualification_notes / commercial_disclosure_notes，不代替平台判定审核 / 不保证通过 / 不隐藏商业性质）；Adapter Lock 锁定 audience / core_message / primary_benefit / benefit_hierarchy / proof_points / mandatory_messages / prohibited_claims / hypotheses / evidence_limitations，可调序 / 选笔记形式 / 映射 Content Angle / 调整平台语气 / 生成标题封面方向 / 映射搜索意图与 CTA / 加平台风险注释，不得替换 Audience / 改 Core Message / 改 Benefit Hierarchy / 创新商品能力或 Proof Point / 删 Evidence Limitation / 把 Hypothesis 转 Fact / 重定义 Approved Strategy / 用平台热词覆盖业务事实 / 通过平台表达规避 Prohibited Claims，须改 Brief 返回 brief_change_required；MVP 输出为 Execution Brief（方向）非 Final Post，支持 image_text_note_brief + video_note_brief，不支持直播脚本 / 评论区运营 / 私信销售 / 广告创意组合 / 自动发布 / 最终视频 Storyboard；Platform Objective Mapping（不得默认一切为立即购买）/ Content Modes（Experience Sharing 仅在有真实素材时用 / Comparison Context 不得踩一捧一贬损竞品）/ Title Directions（3–5 方向，非最终标题）/ Cover Direction（突出一个主信息）/ Narrative Structure（模块化）/ Content Angle Mapping / Customer Language（真实原声必须来自真实 Fragment）/ Experience 边界（不得虚构亲测）/ Tone Mapping（小红书风格 ≠ Emoji 堆砌 / 热词堆砌 / 伪造素人身份）/ CTA Mapping / Search and Hashtag Directions（MVP 仅输出方向不输出最终 Hashtags）/ Prohibited Claims 完整继承并可加 xiaohongshu_specific_risk_notes；六组输出（Platform Context / Note Strategy / Content Architecture / Discovery and Interaction / Evidence and Guardrails / Workflow Decision，7 值 valid / valid_with_limitations / brief_change_required / platform_policy_update_required / waiting_input / paused / failed）；Execution Brief 编辑（→ 新 Execution Brief Version + 保留原模型版本 + 重跑 Validator + 更新 Pointer；承接 DEC-009：Execution Brief 修改不使 Marketing Brief 与上游失效；因 Execution Brief 为当前 MVP 最终输出，普通编辑不触发下游失效；改 Brief 返回 brief_change_required；MVP 不增额外强制 Review Gate 承接 DEC-007）；确定性 Validator 28 项为写入 Execution Brief Current Truth 前的必要 Gate；Hard Rules = No Strategy Drift / No Marketing Brief Drift / No Fabricated Experience / No unsupported Proof Point / No removal or evasion of Prohibited Claims / No Final Xiaohongshu Copy in MVP；Amends DEC-004 + DEC-020，不推翻既有结论****检索与证据装配运行架构已由 DEC-032 确认：Hybrid Retrieval and Evidence Runtime 为跨 Skill 共享运行架构层（非 Core Skill Contract、非 Platform Adapter Contract），采用 Direct-first + Retrieval-on-demand + Deterministic Retrieval Planning + Mandatory Permission and Version Filtering + Reproducible Evidence Package；核心原则 = 能直接读取时不使用检索，需要检索时先限定任务/权限/商品身份/来源范围/来源版本再选 Lexical/Semantic/Hybrid，一个高度相关但不属于当前任务或当前允许 Source Set 的 Fragment 必须被排除而不是仅降低排名；检索优先级 Structured Direct Read → Exact ID/Key Lookup → Bounded Direct Document Read → Lexical → Semantic → Hybrid → Optional Reranking（前置能解决就不走后置；非每个请求跑完所有层）；输出 = Candidate Fragments + Retrieval Logs + Reproducible Evidence Package（不是 Formal Evidence Links/Fact/Insight/Positioning/Approved Strategy）；6 项 Hard Rules = Permission and Source Version filters before relevance / No cross-task retrieval / No Current Product·Competitor leakage / Retrieval result is not Formal Evidence / No Top-K frequency extrapolation / No fabricated answer on zero retrieval；BM25 与 Vector similarity 不同量纲不得直接相加，可用 Rank Fusion 或 Score Normalization+Weighted Combination（须可复现/可版本化/保留 raw ranks/可解释/可替换）；Deterministic Retrieval Planner（RetrievalRequest → RetrievalPlan，概念结构非最终 Schema）；LLM 可辅助意图/子查询/有限 Query Rewrite，但不得决定 task_id/权限/Source Scope/Product Scope/Source Set Version，精确标识符须逐字保留且 Query Rewrite 数量有确定性上限；Mandatory Metadata Filters（task_id/permission_scope/source_scope/product_id/competitor_id/source_set_version_id 等）在召回前/中生效而非先全召回再删除；Current Product 与 Competitor Source Scope 隔离（不得默认 all_product_sources，各 Skill 允许 Scope 不同：Product Intake=current_product+manual_input，Customer Insight=current_product_customer+competitor_customer，Positioning=当前+竞品 facts/insights 身份不合并）；Source Set Version 边界（Superseded/Deleted 排除，Restricted 权限错误）；Candidate Fragment（排名分数只解释为何被召回不是 Fact Confidence/Evidence Strength）/ 按 fragment_id Deduplication（保留 record_id）/ 可选 Reranking（非 MVP 硬依赖）/ 14 步 Evidence Package Construction / Evidence Coverage（不只 Top 10）/ Dataset Analysis 边界（禁用 Top-K 算总体频率/共识/份额）；降级模式（Semantic/Lexical/Reranker/Vector Index 不可用各自回退 + Zero Results 返回 insufficient_information 模型不得虚构）/ Formal Evidence Link 事务边界（仅 Skill 输出过 Evidence Validator 后才创建，Evidence Package=可复现输入 vs Formal Evidence Link=正式关系）/ Cache 边界（Version 变化不返回旧缓存）；Hard Reliability 6 项全=0%；Amends DEC-014，不推翻既有结论**；**Workflow Runtime 的失败恢复、重试与可观测性运行架构已由 DEC-033 确认（运行身份分层 Task / Workflow Run / Skill Run / Node Execution / Execution Attempt；业务等待≠技术失败、技术 Retry≠业务 Rerun、Checkpoint≠业务 Current Truth、任何失败恢复都不能绕过业务版本 / Evidence Validator / Review Package / Current Truth 规则；采用分层运行记录 + 结构化错误分类 + 有界 Retry + 显式 Fallback + Safe Checkpoint Resume + 事务幂等提交 + Manual Recovery + 端到端可观测性；新增 skill_run_id / node_execution_id / attempt_id / error_id / trace_id / recovery_case_id 执行关联链；Amends DEC-023 / DEC-024 / DEC-029，不推翻既有结论）**；**Technical Spike 计划与 Architecture Readiness Gate 已由 DEC-034 确认：正式开发前必须完成最小架构 Technical Spike（验证 LangGraph StateGraph 确定性 Compile/Invoke、紧凑 Graph State 仅存引用、Business Domain State 与 LangGraph Checkpoint 分离、Human Review Interrupt/Resume、Checkpoint 对账、有界 Retry 不产生重复业务版本、事务失败整体回滚、幂等提交、Cancellation 不留部分业务状态、Trace 全链关联等 16 项架构风险），Spike 为非生产实验而非 MVP；Architecture Readiness Gate 在 Spike 证据 + Readiness Review + 用户明确确认三者同时满足前 Development Status 保持 NOT READY，Agent 不得自行宣布 READY；Amends DEC-023 / DEC-033，不推翻既有结论）**；**Technical Spike 临时技术栈与执行契约已由 DEC-035 确认：在 DEC-034「必须完成 Technical Spike 并经 Readiness Gate」基础上，定义 Spike-001 的可执行临时栈（Python 3.13 + 精确固定 LangGraph 1.2.9 + 同步 StateGraph Invoke + 分离式 SQLite[business/runtime/checkpoints] + SqliteSaver + Python sqlite3 事务[统一 BusinessCommitService] + Scripted Deterministic Model + Mock Retrieval + Scenario-based Fault Injection + pytest + Local JSONL Trace + CLI Scenario Runner）、Human Review 节点边界（Review Package 创建与 Interrupt 分离）、Checkpoint 安全（严格反序列化）、Atomic Commit Contract、S0—S6 执行阶段、Spike Agent 权限与禁止、Secret 边界、结果接受边界；所有临时选择均不构成生产承诺；Spike Agent 仅可在 Spike 范围内工作、不得自行宣布 READY、不得修改 Accepted DEC；Amends DEC-034，不推翻既有结论）**；**Spike-001 的执行授权契约已由 DEC-036 确认：采用 Agent-controlled mechanical workflow + User-controlled irreversible decisions；Primary Execution Agent=Claude Code（Git Operator/GitHub Issue and PR Operator/Spike Evidence Producer/Readiness Recommendation Author），Optional Independent Reviewer=Codex；两种授权分离（Contract Authorization=ACCEPTED ≠ Execution Authorization=NOT GRANTED）；Repository Audit→Stable Baseline→Dedicated Spike Branch（spike/001-langgraph-runtime-recovery）→Stage Commits→Spike Issue→Draft PR→Tests and Evidence→Human Review→User Merge Decision；Authorized/Prohibited Git 与 GitHub 操作边界明确（禁止 Force Push/Merge/改写共享历史/删 Branch/改仓库权限）；Mandatory Stop Conditions 6 类；Final Human Gate 保留 Merge 与 READY 决策（Merge PR≠READY）；Amends DEC-034 + DEC-035，不推翻既有结论）**；**Spike-001 的正式执行授权已由 DEC-037 确认；**RFC-001-DQ-01 已确认 Modular Monolith First**（Single Repository + One Primary Backend Deployment Unit + 业务能力与平台能力模块 + 严格依赖方向 + 显式接口 + 数据所有权分离 + 可替换基础设施 Adapter + 未来服务提取边界；当前不采用 Multi-service First；Domain 不依赖具体框架或基础设施；Shared Database Instance≠Shared Data Ownership；Graph Node 不得成为业务持久化规则所有者；服务拆分仅由可验证需求触发；RFC-001 Status=DRAFTING）：在 DEC-034/035/036 确认「必须 Spike + 临时栈 + Git/GitHub 权限与治理边界」基础上，正式授予 Claude Code 从规划与归档阶段进入实际仓库执行阶段的授权，执行 Spike-001 S0—S6 并创建受控 Issue / Branch / Commits / Push / Draft PR / 测试证据与 Readiness Recommendation；一次授权覆盖 S0—S6；First Required Action = 只读 Repository Audit；Execution Authorization 由 NOT GRANTED 转为 GRANTED，但 Spike Execution Status 保持 NOT STARTED（须待实际开始 Repository Audit 后才可更新为 IN PROGRESS）；Gate A—E 阶段更新；Mandatory Stop Conditions；S6 完成边界（S6 后停止，不 Merge / 不关闭 Issue / 不自行宣布 READY）；用户保留 Merge / Issue Closure / Decision 修订 / Architecture READY 决策（PR Merge≠READY、Issue Closed≠READY、Agent Recommendation≠READY）；Amends DEC-034 + DEC-035 + DEC-036，不推翻既有结论）**；以及多条 Agent 层原则（DEC-011~037，见下）与首批 MVP Skill 范围（DEC-020）。**未**确认 Workflow Controller 的工作流节点数量与最终图结构、Workflow State 最终 Python Schema、是否分模型、各 Skill 与工作流节点的最终对应、Agent Spec 最终内容、Node Adapter / Skill Service 接口、Evidence Validator / Retrieval Service / Evidence Package 构建接口、Source / Fragment ID 格式、Parser / OCR / Embedding / 向量数据库、Product Intake & Fact Extraction Skill 最终 Fact Schema / Prompt / 代码、Customer Insight Analysis Skill 最终 Insight Schema / Prompt / 代码、Product Positioning Skill 最终 Schema / Prompt / 代码 / 候选相似度与排序算法 / Human Review UI、Marketing Brief Generation Skill 最终 Brief Schema / Prompt / 代码 / Brief UI / Content Angle 分类表 / Tone 模板 / Brand Guidelines 格式 / 风险词库 / CTA 分类、最终 Insight Schema / Evidence Coverage 枚举名、评论主题分类表、聚类算法、情感分析实现、最低评论数量、频率阈值、Xiaohongshu Brief Mapping Adapter 最终 Execution Brief Schema / Prompt / 代码 / Execution Brief UI / Platform Policy Snapshot 采集与同步 / Account and Campaign Context 最终结构 / Content Mode 分类表 / Title Cover 模板 / 笔记形式选择规则 / Hashtag 方向数量边界 / 视频镜头信息方向结构 / Hybrid Retrieval and Evidence Runtime 最终 RetrievalPlan / RetrievalRequest / Candidate Fragment / Evidence Package Schema / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization 与融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / 最终错误代码 / Workflow Runtime 的 Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue·Worker·DLQ 技术 / Logging·Tracing·Metrics·Alerting Provider / 是否采用 OpenTelemetry / Checkpointer 实现 / 并发模型 / 最终 SLO / Spike 主执行 Agent / Spike 执行时间计划 / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术（生产后端语言 / 生产数据库 / 生产 Checkpointer / ORM / 生产 LLM / 生产 Retrieval / 生产 Observability / 生产部署平台）。

---

## 已确认的 Agent 层原则（Confirmed）

> 来源：[DEC-011 — 确定性工作流控制流程，LLM 负责受约束的语义分析与业务判断](../decisions/dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)（Accepted，Architecture，2026-07-27）

- **LLM 不拥有完整流程控制权：** 工作流阶段、暂停、恢复、状态失效、局部重跑、最终结果有效性由确定性程序的显式规则控制；LLM 不自由决定完整执行路径、调用什么、下一步或何时结束。
- **LLM 负责受约束的语义分析：** 负责语义理解、信息归纳与业务判断（事实候选提取、需求 / 动机 / 阻碍分析、目标用户识别、定位 / 卖点优先级 / 差异化 / 传播策略建议、Brief 草稿、冲突判断、假设识别），输出须符合结构化契约。
- **LLM 输出进入程序校验和人工审核流程：** LLM 输出作为候选事实 / 候选洞察 / 模型推断 / 待验证假设 / 内容草稿进入系统，由程序校验（结构、来源、Schema、失效、风险规则）后再经人工审核确认；**未经校验或人工确认的 LLM 输出不得自动成为已确认业务事实**。

> 注：以上为 Agent 层**总体原则**（DEC-011）；**未**确认是否存在独立 Agent、单 vs Multi-Agent、Agent 数量、各 Agent 职责边界、Tool 定义、模型与框架。（Skill 的**定义**已由 DEC-015 确认，见下；具体实现机制仍开放。）具体 Agent Spec 待职责边界被确认为 Accepted Decision 后再创建。

### Workflow State 下的 LLM 约束（DEC-012，Accepted，2026-07-27）

> 来源：[DEC-012 — Workflow State 采用阶段状态与关键条目结构化设计](../decisions/dec-012-stage-state-and-structured-business-items.md)

- **LLM 节点读写受约束的结构化状态：** LLM 分析节点读写的是显式 Workflow State（阶段状态 + 结构化业务条目），而非自由文本或聊天上下文；LLM 不拥有对工作流状态的最终控制权（与 DEC-011 一致）。
- **LLM 不得直接覆盖原始输入：** 原始用户输入与来源资料独立保存，AI 解析结果不得覆盖用户原始内容；用户修改须保留明确更新状态。
- **LLM 输出首先作为候选条目进入校验和审核：** LLM 产出作为候选事实 / 候选洞察 / 模型推断 / 待验证假设 / 内容草稿（带 evidence_type / source_refs / status 等结构化字段）进入系统，先经程序校验与人工审核，**未经校验或人工确认不得自动成为已确认业务事实**。

> 注：以上为 Workflow State 下 LLM 的**行为约束**；**未**确认 LLM 节点数量、是否独立 Agent、状态 Schema 技术、读写契约的最终字段、Tool / Skill 定义。

### 持久化与恢复中的 LLM 角色（DEC-013，Accepted，2026-07-27）

> 来源：[DEC-013 — MVP 采用支持跨会话恢复的任务级持久化状态](../decisions/dec-013-task-level-persistent-state-and-cross-session-resume.md)

- **LLM 节点通过持久化 Workflow State 获取当前上下文：** 任务级持久化使跨页面 / 跨会话恢复成为可能；LLM 节点恢复执行时从持久化状态（当前阶段、阶段有效性、用户修改、重跑起点等）取得上下文，而非从内存或聊天上下文重建。
- **不依赖聊天记录猜测当前任务进度：** 恢复逻辑**不能**仅靠重新读取聊天记录让 LLM 推测当前进度；不得丢失原始输入 / 来源 / 用户修改、不得把失效重标为有效、不得从错误阶段执行。
- **恢复位置由工作流状态和确定性规则决定：** 由确定性程序基于持久化状态判定「下一步等待用户 / 重跑 / 继续生成」，LLM 不拥有恢复位置的最终控制权（与 DEC-011 一致）。

> 注：以上为持久化与恢复中 LLM 的**角色约束**；**未**确认 LangGraph Checkpointer / thread_id、Checkpoint 频率、序列化方式、任务保留期限、并发与任务锁、具体 Agent 划分。

### RAG / 证据检索中的 LLM 约束（DEC-014，Accepted，2026-07-27）

> 来源：[DEC-014 — MVP 采用按需、混合式 RAG 与分层数据访问策略](../decisions/dec-014-on-demand-hybrid-rag-and-layered-data-access.md)

- **LLM 使用检索到的证据进行受约束分析：** 检索（按需混合 RAG）返回带来源的真实证据片段，LLM 基于这些证据进行语义分析、归纳与业务判断。
- **LLM 不得伪造来源：** 不得引用未实际检索 / 读取的资料、伪造来源 ID / 用户评论、把模型常识包装成检索结果、把运营方法文档误认为商品事实来源。
- **检索结果不自动成为已确认事实：** RAG 返回的是**候选证据**，须经 LLM 分析 + 程序校验 + 必要时人工审核；与 DEC-008 证据标记衔接。
- **Agent 不通过 RAG 控制流程：** RAG 只负责检索与证据提供，不控制工作流阶段 / 继续 / 审核 / 暂停恢复 / 失效 / 重跑 / 事实确认 / 最终决策；是否执行检索、结果如何写入状态由确定性工作流控制（与 DEC-011 一致）。

> 注：以上为 RAG / 证据检索中 LLM 的**行为约束**；**未**确认具体向量数据库 / Embedding / BM25 / Reranker / Chunking / Top-K / 混合权重 / GraphRAG / 联网搜索 / 供应商文件检索 / RAG 触发规则、以及具体 Agent 划分。

### Skill 的定义与 Agent 边界（DEC-015，Accepted，2026-07-27）

> 来源：[DEC-015 — Skill 定义为带执行契约的可复用业务能力包](../decisions/dec-015-contract-based-reusable-business-skills.md)

- **Skill 是带执行契约的可复用业务能力包：** Skill = 面向特定业务目标、具备明确执行语义和可验证契约的能力包（业务目标 + 适用条件 + 输入契约 + 执行步骤 + 工具依赖 + 输出契约 + 确定性校验规则 + 失败与暂停条件 + 评价标准）。Skill 可组合 LLM、确定性程序、检索、Tool、人工审核中的一种或多种，但**不要求**必须使用 LLM。
- **Prompt / Tool / Node / Agent 与 Skill 的边界：** Prompt 只是 Skill 的组成部分；Tool 是可调用技术动作（Tool ≠ Skill）；Skill 不等于工作流节点（可不一一对应，**不得解释为每个 Skill 必须是一个 LangGraph Node**）；Skill 不等于独立 Agent。
- **Agent 可调用 Skill、确定性工作流也可直接调用 Skill：** Agent 是承担职责并使用能力的执行角色，可调用多个 Skill；确定性工作流也可直接调用 Skill。Skill **不要求**必须由独立 Agent 调用。
- **不得为增加 Agent 数量而人为拆分 Skill：** 是否为某 Skill 设立独立 Agent，取决于是否需要独立上下文 / 独立目标 / 长期状态 / 多工具自主选择 / 协作 / 独立业务责任；**不得为了展示 Multi-Agent 而把每个 Skill 包装成独立 Agent**。

> 注：以上为 Skill **定义层**原则（Question-007 已在定义层解决）；**未**确认 Skill 数量、哪些候选 Skill 进入 MVP、Skill 目录、Skill Specification 最终模板、Skill 代码接口、注册与发现、运行时动态选择、Prompt 管理方式、Schema 技术、版本机制、测试框架、Anthropic Skills / OpenAI Skills / MCP / LangGraph / Agent 数量 / Multi-Agent / GitHub 仓库。通用 Skill Spec 结构见 [skill-spec-template.md](skill-spec-template.md)。 **RFC-001-DQ-02 已确认 Backend Language and LangGraph Binding**（MVP 与首个生产版本采用 Python 3.13 作为正式后端语言、TypeScript 作为正式前端语言；Workflow Runtime 使用 Python LangGraph，但 Domain Layer 不依赖 LangGraph，Application Service 不依赖 Graph State 或 Checkpoint；LangGraph 位于 Orchestration / Workflow Runtime Boundary；MVP 不采用 Python 与 TypeScript 混合后端；前后端通过正式版本化 Schema Contract 协作；未来可在明确服务或 Adapter 边界引入其他语言但须由可验证需求触发；Spike Python 代码不得直接成为生产代码；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。 **RFC-001-DQ-03 已确认 Repository and Package Directory Structure**（Single Repository + Multi-project Layout；`apps/backend/` 为 Python 后端根，`apps/backend/src/ai_ecommerce_agent/` 为生产源码唯一根路径，正式 Package 名 `ai_ecommerce_agent`；`apps/web/` 为 TypeScript 前端；`contracts/` 为前后端共享正式契约；后端以业务模块优先组织于 `modules/`，内部使用 `domain/application/infrastructure/public.py` 边界；`platform/` 为平台能力；`orchestration/` 为 LangGraph 与跨模块 Workflow；`entrypoints/` 为 API/Worker/CLI；`bootstrap/` 为依赖装配；`shared_kernel/` 必须最小化；测试位于 `apps/backend/tests/`，分为 unit/integration/contract/architecture/e2e；Migration 位于 `apps/backend/migrations/`；Spike/Prototype 与生产代码物理隔离；当前不创建生产 Skeleton，不迁移 Spike 代码；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。 **RFC-001-DQ-04 已确认 Layer Responsibilities and Dependency Rules**（Domain 纯业务核心 / Application 负责 Use Case、Port 与事务 / Infrastructure 实现 Port / Orchestration 为 LangGraph Adapter / Graph Node 禁止直接访问业务 Repository / Entrypoint 仅协议转换 / Bootstrap 为 Composition Root；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。 **RFC-001-DQ-05 已确认 Skill Code Shape and Architectural Relationships**（Skill 是业务模块 Application Layer 内具有明确执行契约、可独立运行和独立评估的无状态业务能力组件，落位 `modules/<module>/application/skills/<skill_slug>/`；Application Use Case 以 Prepare–Execute–Commit 协调 Skill 与业务事务，Skill 只参与 Execute 阶段产出 Candidate Result（业务候选，未落库）；Skill 直接访问业务 Repository=PROHIBITED、Skill 业务事务所有权=NO、不读/写 Current Truth、不更新 Evidence/Audit/Idempotency；Skill 只能通过 Application 定义的 ModelRuntimePort/RetrievalPort 调用 Provider 能力，直接 import 具体 Provider SDK=PROHIBITED；LangGraph Node 经 Stage Application Service + Skill Executor 间接调用 Skill，Skill 与 LangGraph Node 不同、不感知 LangGraph；Skill 必须能脱离 LangGraph 独立运行与独立评估=REQUIRED；Skill 版本分 Contract/Implementation/Prompt/Output Schema 四维度分管；Skill 须支持 Contract/Unit/Integration/Evaluation/Architecture 五类测试；本 Decision 不选择模型 Provider/Retrieval Backend/Schema Library/Prompt Registry/Evaluation Framework；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。 **RFC-001-DQ-06 已确认 Dependency Injection, Configuration and Application Bootstrap**（默认采用 Constructor Injection + 显式 Factory Functions + 集中式 Composition Root（`bootstrap/`），MVP 不引入第三方 DI Framework，禁止全局 Service Locator 与可变运行状态；配置仅由 Bootstrap 加载、类型化、验证、不可变、验证失败 fail-fast；Domain 不接收配置、Application 只接收业务流程级配置、Infrastructure 只接收适配器级配置；Secret 只注入需要它的 Infrastructure Adapter，不进入 Domain/Application/Skill/Graph State/Checkpoint/Audit/Trace/API Response/Git/Issue/PR，不打印或持久化完整 Secret 值；Repository 只提交 `.env.example`（占位值）、`.env` 不得提交；资源生命周期由 Application Bootstrap 统一管理，按 Application/UseCase/WorkflowRun/SkillExecution 作用域分级；测试通过注入 Fake/Stub 替换真实 Adapter 无需修改业务代码；同步/异步与 API/Worker/CLI 进程边界留待 RFC-001-DQ-07；本 Decision 不选择 DI Framework/Secret Manager/Settings Library/Deployment Platform；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。 **RFC-001-DQ-07 已确认 Process Boundaries and Sync/Async Execution Strategy**（保持单一 Modular Monolith 应用与统一版本化 Release Boundary，但生产运行时分离 API Process / Workflow Worker Process / CLI Process（`Application Architecture ≠ Release Artifact ≠ Runtime Process`，一个主要后端部署单元不要求同进程）；`Long Workflow inside HTTP Request = PROHIBITED`，长 Workflow 经 `WorkflowDispatchPort` Durable Dispatch 后台异步执行，API 在 Durable Work Intent 可靠记录后才返回接受状态，禁止 `asyncio.create_task` 或临时 Background Task 承担生产可靠工作；Worker Crash 后工作可重新领取、重复投递经 Idempotency 防重复业务版本、仅经 Application Service 提交业务状态；Human Review Submit 同步完成业务校验与 Approved Strategy 提交并可靠记录 Durable Resume Intent（Approved Commit + Resume Intent 原子或可靠协调）、Workflow Resume 由 Worker 异步执行；Application Core Sync-first、Domain 纯同步、并发优先有界 Worker、禁止业务代码随意 `asyncio.run()`；API/Worker 窄化 Bootstrap Factory；Dispatch Payload 只含 ID/版本/Runtime Reference；Cancellation 用 Durable Cancellation Intent；Local/Test 允许 Combined Runtime 与 Inline Runner；本 Decision 不选择 API Framework/Queue/Database Driver/Worker Framework/Deployment Platform；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。 **RFC-001-DQ-08 已确认 Module Public Contracts, Cross-module Collaboration and Cycle Governance**（每个业务模块通过唯一稳定入口 `modules.<module>.public`（`public.py`）暴露跨模块契约，其他模块只能通过该 Public Facade；Public Contract 可暴露 Command/Query/Result/Public Error/Application Service Protocol/Published Event/Immutable Snapshot，不得暴露 ORM/Database Session/Repository/内部 Entity/Graph State/Provider SDK/Secret，必须 Typed/Immutable/Serializable/Version-aware/Infrastructure-neutral；跨模块读取经 Target Module Public Query 返回不可变 Owner Module Public Snapshot，禁止 Direct SQL/ORM/Repository，共享 Database Instance≠共享数据所有权；状态修改由数据所有模块 Application Service 执行，模块间直接状态修改 Command 默认禁止，跨 Stage 协调由 Orchestration，跨模块原子操作仅经 Composite Application Use Case；Domain Event 模块内部、Application Event 表示已提交事实仅用于非关键提交后副作用，Human Review/Current Truth/Idempotency/核心路由/Durable Resume 不得依赖普通最终一致 Event，Workflow Orchestration≠Event Choreography，进程内 Event Bus 不承担 API→Worker 可靠调度，Event Handler 重复消费安全；模块依赖图必须为 DAG，循环依赖不得用延迟 Import 或扩大 Shared Kernel 掩盖，须通过 Orchestration/Public Query/Port 注入/Composite Use Case 解决，shared_kernel 保持最小；Public Error 稳定结构化不泄漏技术异常，Breaking Change 显式版本化，Architecture Tests 强制跨模块 Import 只能指向 Public Facade 且依赖图无环；本 Decision 不选择 Event Bus/Outbox/Schema Library/Contract Test Framework，接受后仍不授权创建正式 Public Contract/Event Bus/生产业务代码；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。 **RFC-001-DQ-09 已确认 Quality Toolchain, Architecture Enforcement, CI Quality Gates and Test Baseline**（生产代码采用 Ruff（Formatter+Linter）、Pyright、pytest、Import Linter 与自定义 pytest Architecture Tests 构成统一质量工具链，不同时引入 Black/isort/Flake8 作为平行 Source of Truth，配置集中于 `apps/backend/pyproject.toml`；Strict-first Type Discipline 优先适用于 Domain/Application/Public Contract，`Any` 只能在明确外部边界，禁止全局 Any/Ignore/关闭核心诊断；测试分类 unit/integration/contract/architecture/e2e/evaluation/live/slow，pytest Marker 预注册 + CI 严格 Marker 模式，未知 Marker 失败，普通 Required PR Tests 不访问实时外部 Provider；Architecture Enforcement 双层=Import Linter 结构规则 + 自定义 Architecture Tests 语义规则；Unit 确定性、Integration 隔离可重建、Contract 验证 Public Contract/Port/Event/Dispatch Payload、E2E 覆盖主流程+失败场景、Evaluation 与确定性测试分离且 Live Evaluation 默认 Nightly/手动/Release Candidate；可执行生产代码后启用 Branch Coverage Global Fail-under 80%，关键业务规则必须有行为测试，Warnings=Error by default，Required CI 禁止自动重跑掩盖 Flaky Test，Snapshot 更新需人工语义审查；Dependency Audit 用 pip-audit + Dependabot，CI 必须有 Secret Detection Gate（检出→失败→移除→真实凭证轮换/吊销）；CI 分 Fast Static/Deterministic Test/Runtime Confidence/Extended 四层，`main` 由稳定 Required Status Checks 保护（PR 合并、禁止直接/Force Push、Review 解决、用户保留最终 Merge 权限，个人项目不强制第二名 Reviewer），Coding Agent 不得关闭检查/降低阈值/删除测试绕过 CI，本地=CI 统一命令；本 Decision 不锁定工具版本/Secret Scanner/前端工具/CI YAML，接受后仍不授权创建 Production CI 或 Skeleton；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING） **RFC-001-DQ-10 已确认 Production Skeleton Scope, Foundation Authorization Gate and RFC Closure**（Acceptance 与 Authorization 严格分离——RFC-001 Acceptance ≠ Foundation Planning Authorization ≠ Foundation Implementation Authorization ≠ Business Implementation Authorization，接受 DQ 或 RFC-001 整体均不授权开发；RFC-001 最终接受仅开放 Foundation Planning，每个 Foundation Issue 需单独明确授权（One Issue→One Branch→One PR→User Merge Gate）；Initial Foundation Scope = Package + Quality Tooling + Architecture Tests + CI + Repository Security；首批不创建业务模块 / platform 具体实现 / Production Orchestration·LangGraph / API·Worker·CLI / Production Bootstrap / Database·ORM·Migration / Queue·Checkpointer / Model·Retrieval·Observability Runtime / Frontend Runtime；Spike Source Migration PROHIBITED（Spike-001 仅作 Evidence 与 Test Design Input）；Foundation Issue Candidates = FND-001→FND-002→FND-003（依赖顺序）；Mandatory Stop Conditions 17 类（遇未决架构问题必须停止并提交 Decision Conflict / Mandatory Stop Report）；RFC-001 Final Acceptance 需 Final Consistency Review + 用户明确接受，PR Merge 不能替代用户接受；按 DEC-038 RFC-001~003 ACCEPTED 后才生成 Roadmap Draft v0、RFC-001~007 ACCEPTED 后才生成 Roadmap v1 与完整业务 Backlog；Decision Status=ACCEPTED；RFC-001 Status=DRAFTING）。。

### 外部 Skill 复用与契约化改造策略（DEC-016，Accepted，2026-07-27）

> 来源：[DEC-016 — 优先研究成熟电商 Skills，并通过契约化改造后复用](../decisions/dec-016-external-skill-research-and-contract-based-adaptation.md)

- **优先研究成熟外部电商 Skills：** 设计 MVP Skills 时优先调研 / 评估 GitHub 上已有的成熟电商 Skills、SOP、分析框架、输出模板、规则库、测试案例；不要求所有 Skill 从零设计。
- **外部 Skill 不得未经审计直接成为项目正式 Skill：** 须经「发现 → 分析业务目标和适用范围 → 审计输入输出与隐含假设 → 审计证据 / 合规 / 失败处理 → 删除 MVP 无关内容 → 重构为项目 Skill Contract → 增加结构化 IO / 来源证据 / 暂停与人工审核 / 确定性校验 / 测试评价 → 接入 Workflow State」流程，改造为符合 DEC-015 的 Skill Contract。
- **复用分级：** Adopt / Adapt / Reference Only / Reject；首轮 3 个候选（`nexscope-ai/eCommerce-Skills` 两个 + `feichanggege/ecommerce-visual-copywriting-skill`）**已全部完成评估**：Candidate 1（DEC-017）、Candidate 2（DEC-018）、Candidate 3（DEC-019）均评估为 Adapt（仍为研究与改造方向，未进入 MVP）。
- **区分工作流基底仓库与 Skill 供体仓库：** Workflow Base Repository（提供工作流 / 状态 / 暂停恢复 / 持久化 / 审核 / 重跑 / RAG / 结构化输出 / 测试框架，**尚未选择**）vs Skill Donor Repository（提供 SOP / 方法 / 模板 / 规则 / 经验 / 测试案例）。项目可采用「一个主工作流基底 + 多个外部 Skill 供体 + 项目自有的状态 / 证据 / 审核 / 可靠性契约」。
- **License 与归属：** 复用第三方代码 / Prompt / 模板 / 规则 / 文档须遵守原始 License、保留版权声明、文档标明来源、说明修改、区分第三方与原创贡献；**不得将第三方方案包装为完全原创**。

> 注：本节为外部 Skill **复用策略**；首轮三候选均已评估完成（Candidate 1 DEC-017、Candidate 2 DEC-018、Candidate 3 DEC-019，均为 Adapt，仍为研究方向未进入 MVP）。**未**确认哪些 Skill 进入 MVP、是否直接复制任何代码、Skill 最终数量 / 目录、具体实现框架、工作流基底仓库、LangGraph、具体 GitHub 仓库组合、Multi-Agent、改造排期。外部 Skill 评估模板见 [../reviews/external-skill-evaluation-template.md](../reviews/external-skill-evaluation-template.md)；评估记录见 [../reviews/external-skills/product-review-analysis-evaluation.md](../reviews/external-skills/product-review-analysis-evaluation.md)（Candidate 1）、[../reviews/external-skills/product-differentiation-shopify-evaluation.md](../reviews/external-skills/product-differentiation-shopify-evaluation.md)（Candidate 2）、[../reviews/external-skills/ecommerce-visual-copywriting-skill-evaluation.md](../reviews/external-skills/ecommerce-visual-copywriting-skill-evaluation.md)（Candidate 3）。

### 候选 Skill 供体映射（DEC-017，Candidate 1，Accepted，2026-07-27）

> 来源：[DEC-017 — Product Review Analysis 作为 Customer Insight Skill 的改造供体](../decisions/dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)

```
Customer Insight Analysis Skill
- External donor under evaluation and adaptation:
  nexscope-ai/eCommerce-Skills/product-review-analysis
- Reuse mode: Adapt
```

- 该映射仅为「外部供体 → 目标 Skill」的**研究与改造方向**，**不是**正式 Skill Specification。
- Adapt 不等于已实现：Candidate 1 仍须走完 DEC-016 的改造流程（审计 → 裁剪 → 重构为 Skill Contract → 校验 → 接入 Workflow State）并形成后续 Skill Spec，才能成为项目正式 Skill。
- 候选 3（`ecommerce-visual-copywriting-skill`）仍**待评估**（Candidate 2 见下节 DEC-018）。

> 注：本节**未**确认 Customer Insight Analysis Skill 的最终名称、Schema、实现；**未**创建正式 Skill Spec。

### 候选 Skill 供体映射（DEC-018，Candidate 2，Accepted，2026-07-27）

> 来源：[DEC-018 — Product Differentiation Shopify 作为 Product Positioning Skill 的改造供体](../decisions/dec-018-adapt-product-differentiation-for-positioning-skill.md)

```
Product Positioning Skill
- External donor under evaluation and adaptation:
  nexscope-ai/eCommerce-Skills/product-differentiation-shopify
- Reuse mode: Adapt
```

- 该映射仅为「外部供体 → 目标 Skill」的**研究与改造方向**，**不是**正式 Skill Specification。
- Adapt 不等于已实现：Candidate 2 仍须走完 DEC-016 的改造流程（审计 → 裁剪 → 重构为 Skill Contract → 校验 → 接入 Workflow State）并形成后续 Skill Spec，才能成为项目正式 Skill。
- 关键词匹配 / 频率统计**只作为辅助信号或基线**，不作为最终定位推理依据；不直接采用原始分析脚本作为最终定位引擎。
- 首轮三候选已全部评估完成（Candidate 3 见下节 DEC-019）。

> 注：本节**未**确认 Product Positioning Skill 的最终名称、Schema、渐进级别、实现；**未**创建正式 Skill Spec。

### 候选 Skill 供体映射（DEC-019，Candidate 3，Accepted，2026-07-27）

> 来源：[DEC-019 — Ecommerce Visual Copywriting Skill 作为执行层 Brief 能力的改造供体](../decisions/dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)

```
Marketing Brief Generation Skill
- External mechanism donor:
  feichanggege/ecommerce-visual-copywriting-skill
- Reuse mode: Partial Adapt

Visual Execution Brief Skill
- External donor:
  feichanggege/ecommerce-visual-copywriting-skill
- Reuse mode: Adapt
- MVP inclusion: Not in first MVP (resolved by DEC-020)

Xiaohongshu Brief Mapping Skill
- External workflow reference:
  feichanggege/ecommerce-visual-copywriting-skill
- Reuse mode: Reference and partial adaptation
- MVP inclusion: In MVP as Platform Adapter (resolved by DEC-020)
```

- 该映射仅为「外部供体 → 目标 Skill」的**研究与改造方向**，**不是**正式 Skill Specification。
- Adapt 不等于已实现：Candidate 3 仍须走完 DEC-016 的改造流程并形成后续 Skill Spec。
- Candidate 3 对三个目标 Skill 的复用粒度不同（Partial Adapt / Adapt / Reference + 部分改造）。
- Visual Execution Brief Skill **不进入首版 MVP**（DEC-020）；Xiaohongshu Brief Mapping Skill 作为平台 Adapter **进入 MVP Demo**（DEC-020）；Marketing Brief Generation Skill 作为 Core Skill 进入 MVP（DEC-020），吸收部分机制，不在当前阶段生成完整视觉方案。
- 不采用完整视觉生产范围、两个强制审核 Gate（与 DEC-007 冲突，回归单 Gate）、静态规则为最终事实、LLM 自评分为唯一质量门。

> 注：本节**未**确认 Visual Execution Brief / Xiaohongshu Brief Mapping / Marketing Brief Generation Skill 的最终名称、Schema、实现、MVP 纳入；**未**创建正式 Skill Spec。

### MVP Skill 范围与分类（DEC-020，Accepted，2026-07-28）

> 来源：[DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](../decisions/dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)

```
Core Skills
- Product Intake & Fact Extraction
- Customer Insight Analysis
- Product Positioning
- Marketing Brief Generation

Platform Adapters
- Xiaohongshu Brief Mapping

Shared Capabilities
- Document Parsing
- Hybrid Retrieval
- Source Management
- Schema Validation
- Risk Validation

Future Skills
- Visual Execution Brief
```

- 该分类是「首批 MVP Skill 清单裁剪」的确认结果：4 个 Core Skills + 1 个 Platform Adapter；Document Parsing / Hybrid Retrieval / Source Management / Task Persistence / Stage Invalidation / Partial Rerun 为**共享能力（非 Skill）**；Schema Validation 为**确定性 Validator（非 Skill）**；Risk Validation 为**嵌入式校验（不独立 Compliance Review Skill）**。
- **Product Input Assessment 与 Product Fact Extraction 在 MVP 合并**为 Product Intake & Fact Extraction Skill。
- 三个外部供体在 MVP 中的落点：Customer Insight Analysis ← Candidate 1（DEC-017，Adapt）；Product Positioning ← Candidate 2（DEC-018，Adapt）；Marketing Brief Generation ← Candidate 3（DEC-019，Partial Adapt）。**Visual Execution Brief Skill（Candidate 3 主目标）不进入首版 MVP**，仅保留为 Future Skill。
- 保留**一个**常规人工审核 Gate（DEC-007），不增加第二个 Gate。
- 上述 Core Skill / Adapter **仅为 MVP 范围与职责方向**，**不是**正式 Skill Specification。

> 注：本节**未**确认四个 Skills 的最终名称 / Schema / Specification、小红书 Adapter 最终输出、是否生成完整小红书笔记、Risk Validator 具体规则、Skill 代码接口 / 注册机制 / 工作流节点数、Agent 数量、Multi-Agent、LangGraph、工作流基底仓库、模型与数据库、前后端技术栈；**未**创建正式 Skill Spec。

### MVP Agent 架构与 Multi-Agent 判断（DEC-021，Accepted，2026-07-28）

> 来源：[DEC-021 — MVP 不采用 Multi-Agent 主架构，保留评测驱动的受约束并行 Worker 扩展](../decisions/dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)；研究记录：[../research/multi-agent-architecture-assessment.md](../research/multi-agent-architecture-assessment.md)。

```
User-facing Agent
- Ecommerce Strategy Agent

Internal Architecture
- Deterministic Workflow Controller
- Contract-based Skills
- Platform Adapter
- Shared Capabilities

MVP Multi-Agent Status
- Not adopted

Future Extension
- Centralized Orchestrator with bounded parallel Workers,
  only when justified by evaluation.
```

- MVP **不采用** Supervisor + 多自治 Agent 主架构；产品对用户呈现为**统一 `Ecommerce Strategy Agent`**（产品交互身份），内部由**确定性 Workflow Controller** 编排 4 个 Core Skills + 1 个小红书 Adapter。
- **Skill ≠ Agent；多次 LLM 调用 ≠ Multi-Agent：** 各 Skill 可拥有独立 Prompt / 模型配置 / 工具 / 输出 Schema，但**不拥有独立流程控制权**（不决定下一步阶段、不维护独立任务状态、不自由协商、不控制人工审核）——它们是 **Skill-specialized LLM Node**，而非自治 Agent。
- **不创建 LLM Supervisor：** 工作流路由由代码与状态决定；**不采用**「Supervisor LLM 自由判断下一步」。
- **主 Workflow State 是唯一当前任务状态来源：** LLM、Skill 或未来 Worker 不得自行修改完整工作流顺序或另立状态。
- **未来允许局部受约束并行 Worker：** 仅在出现真实并行需求 + 对照评测证明收益超过成本时，在特定节点内部引入「中心化 Orchestrator + Bounded Parallel Workers」（评论分析 / 多竞品 / 多平台映射 / Evaluator Node）；Worker 须经汇总校验、不控制主流程。
- 对外描述优先用 `Stateful Agentic Workflow` / `Contract-based Skill Architecture` / `Human-in-the-loop AI Workflow`，**不**用 `Multi-Agent E-commerce Platform`。

> 注：本节确认 MVP 的 **Agent 架构形态**（统一 Agent + 确定性编排 + 契约化 Skill；不采用 Multi-Agent）；**不**创建 Supervisor / 子 Agent / Agent-to-Agent Messaging / Multi-Agent Runtime / Worker 代码；**不**确认 Workflow Controller 框架（LangGraph / OpenAI Agents SDK / LangChain / 自研状态机）、CrewAI / AutoGen、Worker 实现框架、独立 Evaluator 是否进 MVP、并行评论处理是否进 MVP、模型数量 / 是否分模型、基底仓库、模型供应商。

### 工作流框架能力需求（DEC-022，Accepted，2026-07-28）

> 来源：[DEC-022 — Workflow Framework Capability Requirements](../decisions/dec-022-workflow-framework-capability-requirements.md)

```
Framework Evaluation Focus
- State-first, deterministic, persistent business workflow runtime
- Human-in-the-loop with state write-back
- Stage invalidation and partial rerun
- Node-level contracts, validation, and retries
- Model-neutral (per-node model / tool config in project config layer)
- Domain State independent of framework
- Single node independently testable
```

- 工作流框架**首先**被评估为「有状态、确定性、可持久化的业务工作流运行时」，而**不是** Multi-Agent 协作框架（与 DEC-021 一致）。框架承载确定性 Workflow Controller，编排四个 Skill-specialized LLM Node + 小红书 Adapter + 人工审核节点。
- 框架**不替代**业务 Skill、**不**通过 LLM Supervisor 自由决定主流程（承接 DEC-011 / 021）；各 Skill 可拥有独立 Prompt / 模型配置 / 工具 / 输出 Schema，但**不拥有独立流程控制权**。
- 模型与工具配置属**项目配置层**，**不**被工作流框架硬编码；Skill 逻辑与运行时解耦（`Workflow Node Adapter → Business Skill Service`）。
- 后续候选框架按 DEC-022 的 100 分制评分维度与淘汰条件评估；**不得仅依据**流行程度 / GitHub Star / Multi-Agent Demo 选择。

> 注：本节确认**工作流框架对 Agent 层的能力需求**；**不**选择具体框架（LangGraph / OpenAI Agents SDK / LangChain / CrewAI / Temporal / 自研状态机）、模型数量 / 供应商、Skill Spec 最终内容、Agent Spec 最终内容。

### 工作流运行框架与主要建模方式（DEC-023，Accepted，2026-07-28）

> 来源：[DEC-023 — MVP 选择 LangGraph StateGraph 作为核心工作流运行方式](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)；研究记录：[../research/workflow-framework-candidate-comparison.md](../research/workflow-framework-candidate-comparison.md)。

```
Workflow Runtime: LangGraph
Primary Workflow API: StateGraph / Graph API
Main Flow Control: NOT ReAct Agent / NOT LLM Supervisor / NOT multiple autonomous Agents
LangGraph Role: runtime and orchestration layer only (NOT business Domain Layer)
```

- **工作流运行框架已选定 LangGraph（StateGraph / Graph API）：** 主业务流程以 `State + Nodes + Edges + Conditional Edges + Checkpoint + Interrupt / Resume` 表达；StateGraph 是 Graph API 的核心 Builder（`compile()` → `CompiledStateGraph`），**不是** LangGraph 的竞品；Functional API 仅用于可选局部简单任务。
- **对 Agent 层的影响（承接 DEC-021）：** LangGraph **不**改变 MVP 的 Agent 架构形态——仍为统一用户侧 `Ecommerce Strategy Agent` + 确定性 Workflow Controller 编排四个 Skill-specialized LLM Node + 小红书 Adapter；**不**创建 LLM Supervisor、**不**创建多个自治业务 Agent、**不**用预构建 ReAct Agent 控制主流程。四个 Core Skills 由 Node Adapter 以结构化 IO 调用，**不**拥有独立流程控制权（不控制主 Graph 路由）。
- **Skill Service 与 LangGraph 解耦：** Skill Service 应能脱离 LangGraph 单独执行和测试；业务逻辑写在 Skill Service，**不**写在 Node Adapter；Domain Model **不**继承 LangGraph 类型（`Node Adapter → 框架无关 Skill Service → Domain / Repositories / LLM Gateway`）。Skill ≠ 工作流节点（承接 DEC-015），Graph 只表达少量大阶段。
- **未来内部 Agent 只作局部能力：** 允许的未来结构为 `StateGraph Main Workflow → Selected Research Node → Optional Internal Research Agent → Structured Result → Return to StateGraph`；内部 Agent **只**能作为局部能力，**不**取代主 Workflow Controller。
- **强制 Technical Spike（见 ../spikes/langgraph-stategraph-workflow-spike.md）：** 正式业务实现前必须完成最小工作流验证（18 项 Must Prove / 9 条 Failure Conditions；失败则重新比较 LangGraph vs 自研状态机）。

> 注：本节确认**工作流运行框架选定后对 Agent 层的影响**（仍为统一 Agent + 确定性编排 + 契约化 Skill；不创建 Supervisor / 多自治 Agent）；**仍待确认** Workflow Controller 的工作流节点数量与最终图结构、各 Skill 与节点的最终对应、Node Adapter / Skill Service 接口、是否分模型、Agent Spec 最终内容、Workflow State Schema。本节**不**创建 Supervisor / 子 Agent / Agent-to-Agent Messaging / Multi-Agent Runtime / Worker 代码，**不**选择 Checkpointer / 数据库 / 模型供应商 / LangSmith。

### Workflow State 架构对 Agent 层的影响（DEC-024，Accepted，2026-07-28）

> 来源：[DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)；概念规格：[../specs/workflow/workflow-state-specification.md](../specs/workflow/workflow-state-specification.md)。Amends DEC-012 / DEC-013。

```
State Architecture
- Domain State       (authoritative business truth, in Business Database)
- Workflow State     (compact LangGraph state, reference-oriented)
- Runtime State      (execution recovery via Checkpointer)
- Interaction State  (derived frontend state)

Identifier Boundaries
- task_id        -> stable product business identity
- thread_id      -> LangGraph execution context
- run_id         -> one invocation or resume
- checkpoint_id  -> runtime snapshot
```

- **状态四分，Agent / Skill 不越界读写：** 业务 Current Truth 在 Domain State（业务数据库），执行态在紧凑 Workflow State，恢复态在 Runtime Checkpoint，前端态为派生 Interaction State。Skill-specialized LLM Node（承接 DEC-021）通过 Node Adapter 拿到的是**版本引用 + 必要小型结构化输入**，**不**直接读 Checkpointer、**不**把 Checkpoint 当业务库（承接 DEC-023 集成边界）。
- **Skill 基于版本引用工作：** Skill 输入输出面向结构化契约（承接 DEC-015）；Node Adapter 按 Version ID 从 Business Repository 加载正式 Domain Objects 转为 Skill Input，Skill Output 经校验后生成**新版本**写入业务库并更新 Current Truth Pointer（承接 DEC-012 结构化条目 + DEC-008 证据标记）。
- **Human Review 为结构化 ReviewState：** 单审核 Gate（DEC-007）使用 `ReviewState`（status / review_package_version / reviewed_entities / user_decisions[]）+ `ReviewDecision`（action ∈ accept / edit / reject / replace / request_more_information）；Review 完成产生**已审核策略版本**（approved_strategy_version_id），**不**等于接受所有模型建议。
- **用户修改不静默覆盖：** 用户编辑生成新业务版本（`creation_type = user_edit`，`created_by = user`），保留 `model_generated_content + user_patch + resolved_content`（或语义等价），可回溯模型候选 / 修改 / 原因 / 失效下游；下游阶段经显式 InvalidationEvent 失效（承接 DEC-009）。
- **阶段失效由 Domain Layer 定义、不由 LangGraph 推断：** StageStatus（valid / invalid / skipped …）与 InvalidationEvent 是业务规则（承接 DEC-011 确定性控制 + DEC-023 阶段失效由 Domain Layer 定义）；StateGraph 仅据失效状态与 earliest rerun stage 决定从哪继续，LangGraph Replay / Time Travel **不替代**项目失效规则。
- **`task_id` 稳定、与 LangGraph 解耦：** 统一用户侧 `Ecommerce Strategy Agent` 的业务身份是 `task_id`（Domain Layer，不因 Resume / 重跑改变）；`thread_id` 仅是 LangGraph 执行上下文（MVP 一个 task_id → 一个当前活跃 thread_id）。Agent Spec 未来若创建，须以 `task_id` 为业务导航身份，**不**以 `checkpoint_id` 作前端主要导航。

> 注：本节确认 **Workflow State 架构对 Agent 层的影响**（Skill 基于版本引用 + 结构化 ReviewState + 不静默覆盖 + 失效由 Domain 定义；承接 DEC-007/008/009/011/012/013/015/020/021/023）；详细数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-024 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-024 节。**仍待确认** 各 Skill 最终 Schema / Specification、Skill 代码接口、Review Payload 最终字段、Node Adapter / Skill Service 接口、工作流节点数量、是否分模型、Agent Spec 最终内容。本节**不**创建正式 Skill Spec / 业务代码 / Checkpointer / 数据库 / API，**不**选择数据库 / ORM / 模型供应商。

### 来源与证据架构对 Agent 层的影响（DEC-025，Accepted，2026-07-28）

> 来源：[DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](../decisions/dec-025-versioned-sources-fragments-and-evidence-links.md)；概念规格：[../specs/evidence/source-and-evidence-specification.md](../specs/evidence/source-and-evidence-specification.md)。Amends DEC-008 / DEC-014。

```
Source → Source Version → Document / Record → Fragment → Evidence Link → Versioned Domain Object

Evidence Role: supports / contradicts / qualifies / provides_context / example_only
Evidence Class (DEC-008): Explicit Fact / Evidence-backed Insight / Model Inference / Hypothesis / Insufficient
```

- **Skill 基于 Evidence Package 工作：** Skill-specialized LLM Node（承接 DEC-021）通过 Node Adapter 拿到的是可复现的 **Evidence Package**（`candidate_fragments[]` / `verified_facts[]` / `dataset_statistics[]` / `known_conflicts[]` / `evidence_limitations[]`），而非整个来源数据库 / 检索索引 / 向量库；Skill 输出中的 `fragment_id` / `source_version_id` **必须来自该 Evidence Package 的允许集合**。
- **LLM 不得自由生成 Source / Fragment ID：** LLM **不**得自由生成 `source_id` / `source_version_id` / `fragment_id` / 文件名 / 页码 / 评论 ID / URL / 引用位置；模型只能从系统提供的候选 Fragment ID 集合中选择；**禁止**只保存自然语言引用而无真实 Fragment ID 与 Locator（防幻觉引用）。
- **所有引用须经 Evidence Validator：** Skill 输出的引用须经确定性 Evidence Validator 校验（ID 存在 / 属当前任务 / 来自允许 Source Scope / Source Version 可用 / 是本次 Evidence Package 候选 / 未重复 / 未失效 / Locator 存在），只有校验通过才创建 Evidence Link 进入正式业务对象；承接 DEC-011「未经校验的 LLM 输出不得自动成为已确认业务事实」+ DEC-012「LLM 输出首先作为候选条目进入校验」。
- **Fact 须有直接来源、模型不得生成无来源 Fact：** 每个 Explicit Fact 必须关联直接 Source Fragment（用户手动输入本身可作为直接 Source Fragment）；模型**不得**生成没有来源的 Explicit Fact；Model Inference 须明确标记、不得显示为已验证事实或直接成为无条件 Proof Point（承接 DEC-008 五类 Evidence Class）。
- **业务结论引用具体 Source Version：** 正式业务结果引用 `source_version_id`（而非可能变化的 `source_id`）；Evidence Link 是独立关系对象（`Versioned Domain Object ↔ Fragment`），由 Business Repository 保存（承接 DEC-024）。
- **当前商品与竞品来源隔离：** `source_scope`（current_product / competitor_product / platform_knowledge / internal_business）显式隔离；竞品资料**不能**直接证明当前商品事实；所有来源对象关联当前 Task 或合法 Workspace，跨任务召回私有资料必须拒绝。
- **频率统计须完整可计数数据：** 正式比例 / 频率 / 覆盖率须基于完整、可计数数据集（有 Dataset Statistic 记录、分母分子可验证），**禁止**以 RAG Top-K 召回结果推断总体频率；区分 Dataset-derived Statistic 与 Retrieved Evidence Sample。
- **来源失效可追溯：** 来源失效按 Evidence Link 判断受影响对象，触发 InvalidationEvent + 阶段失效（承接 DEC-009 / DEC-024）；关键事实冲突 → Fact Stage waiting_input / paused，系统**不得**由模型自选值写成事实。

> 注：本节确认**来源与证据架构对 Agent 层的影响**（Skill 基于 Evidence Package + LLM 不生成 Source ID + 引用经 Evidence Validator + Fact 须有来源 + 竞品隔离；承接 DEC-008/009/011/012/014/020/021/024）；详细数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-025 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-025 节。**仍待确认** 各 Skill 最终 Schema / Specification、Evidence Validator / Retrieval Service / Evidence Package 构建接口、Fragment 切分规则、Source / Fragment ID 格式、Parser / OCR / Embedding / 向量数据库 / Reranker / Top-K、前端 Evidence UI、正式 API。本节**不**创建正式 Skill Spec / Parser / RAG / Embedding / Vector Store / Evidence Validator 代码，**不**选择 PostgreSQL / MongoDB / Elasticsearch / pgvector / Pinecone / Weaviate / Chroma / Embedding 模型 / Reranker / PDF Parser / OCR Provider。

### 首个核心 Skill Contract 对 Agent 层的影响（DEC-026，Accepted，2026-07-28）

> 来源：[DEC-026 — Product Intake & Fact Extraction Skill 采用分层输入完整度、零无来源事实与冲突暂停契约](../decisions/dec-026-product-intake-and-fact-extraction-skill-contract.md)；概念 Skill Spec：[../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)。Amends DEC-005。

```
Core Skill:
Product Intake & Fact Extraction

Hard Rule:
No Fact without a valid current-product Fragment.
```

- **首个 Core Skill Contract 已确认：** Product Intake & Fact Extraction Skill（DEC-020 链路起点，合并 Product Input Assessment + Product Fact Extraction）现在拥有**概念层执行契约**：业务目标 / 职责 / 非职责 / 最低可运行输入 / 四档完整度 / Fact 分类 / Fact Item 概念 / 声明五分类 / No-inferred-facts / 标准化 / 去重 / 冲突处理 / 五组输出 / 暂停与失败边界 / Validator 15 项 / 职责边界 / 置信度边界 / 评价指标（概念 Skill Spec 见 [../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)）。其余三个 Core Skill（Customer Insight / Positioning / Marketing Brief）Contract **仍待确认**。
- **Hard Rule：无有效当前商品 Fragment 不得成正式 Fact：** 所有进入正式 Facts Version 的事实都必须关联当前商品范围内真实、有效、可定位的 Fragment（承接 DEC-025 Evidence Link + Evidence Validator）。模型**不得**通过常识 / 联想 / 业务推理创造 Explicit Fact（如 `304 不锈钢` 不得自动增「食品级 / 耐腐蚀 / 绝对安全」）；合理但无直接来源的内容只能进入 `Model Inference` / `Hypothesis to Validate`，**不**进入 Fact Layer（承接 DEC-008 五类 Evidence Class）。
- **声明五分类，Marketing Expression / Documented Claim 不得混入 Fact：** 来源表达须区分 `direct_fact` / `documented_claim` / `certified_or_tested_fact` / `marketing_expression` / `unknown_or_ambiguous`；Marketing Expression 可存为原始素材但**不**进 Facts Current Truth；只有营销页面而无检测 / 认证资料的声明只能归 `documented_claim`；`certified_or_tested_fact` 不得扩张报告结论。
- **关键冲突暂停、不由模型自选：** Numeric / Material / SKU or Variant / Certification / Usage Restriction 冲突**不得**由模型自行解决，须创建正式 `SourceConflict` 并触发 `waiting_input` / `paused` 交用户处理（承接 DEC-025 SourceConflict + DEC-007 异常暂停）；MVP **不**建立复杂来源优先级。
- **确定性 Validator 是写入前的必要 Gate：** LLM 输出写入正式 Facts Version 前须经 15 项硬校验（每个 Fact 有 Supporting Fragment / Fragment ID 真实存在 / 属当前 task_id / Scope 为 current_product 或合法 Manual Input / Source Version 可用 / 未用竞品来源 / 数值可定位 / 单位转换合法 / raw_value 与原文一致 / Marketing Expression 未写成 Fact / Documented Claim 未标为 Certified / 冲突值未同时成 Current Truth / 符合 Schema / 必填身份存在 / 无虚构 Source·Version·Fragment ID）；硬校验失败**不得**写入 Facts Current Truth（承接 DEC-011「未经校验的 LLM 输出不得自动成为已确认业务事实」+ DEC-025 确定性 Reference Validation）。
- **业务资料不足 ≠ 技术失败：** `waiting_input`（可由用户补料解决的业务问题）/ `paused`（需人工判断或权限处理）/ `failed`（Parser 异常 / 数据库失败 / 模型连续无法输出合法 Schema / Evidence Validator 错误 / 文件损坏）严格分离；业务资料不足**不得**误标为技术失败。
- **不使用模型数字 Confidence：** MVP **不**使用模型主观通用数字置信度（如 `0.87`），改用可解释验证状态（user_provided / single_source_direct / multi_source_corroborated / documented_claim / verified_by_test_or_certificate / conflicting / insufficient，最终名称未确认）。

> 注：本节确认**首个核心 Skill Contract 对 Agent 层的影响**（Hard Rule + 声明五分类 + 关键冲突暂停 + Validator 15 项 + 业务不足≠技术失败 + 不用数字 Confidence；承接 DEC-005/007/008/009/011/015/020/024/025）；详细 Fact 数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-026 节。**仍待确认** 该 Skill 最终 Fact Schema / Prompt / 代码 / LangGraph Node 对应、Parser / OCR / 单位库、Verification Status 最终枚举名、Golden Dataset 最终数据；Product Positioning Skill 最终 Schema / Prompt / 代码 / 候选相似度与排序算法；以及其余一个 Core Skill（Marketing Brief）Contract。本节**不**创建正式 Prompt / Skill 代码 / LangGraph Node / 数据库表 / Parser / OCR / Unit Library / 前端表单 / 风险规则实现，**不**选择模型 / Parser / OCR Provider / 数据库 / ORM / 文件格式实现 / 单位处理库。

### 第二个核心 Skill Contract 对 Agent 层的影响（DEC-027，Accepted，2026-07-28）

> 来源：[DEC-027 — Customer Insight Analysis Skill 采用证据模式与降级假设模式，并禁止虚构用户原声和检索样本频率外推](../decisions/dec-027-customer-insight-analysis-skill-contract.md)；概念 Skill Spec：[../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)。Amends DEC-017。

```
Core Skill:
Customer Insight Analysis

Modes:
- Evidence-backed
- Degraded Hypothesis

Hard Rules:
- No fabricated customer quote
- No Top-K frequency extrapolation
- No competitor feedback misattribution
```

- **第二个 Core Skill Contract 已确认：** Customer Insight Analysis Skill（DEC-020 链路第二位，`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning`，承接 DEC-017 Adapt 供体方向）现在拥有**概念层执行契约**：业务目标 / 职责 / 非职责 / 两种运行模式 / 主题与洞察边界 / 4 类证据 / Evidence Coverage 5 状态 / 不设统一样本门槛 / Insight 类型与概念 / 用户原声规则 / 频率统计边界 / 正反向证据 / 冲突需求 / Facts 与 Insights 边界 / 五组输出 / 暂停与失败边界 / Validator 18 项 / 职责边界 / 置信度边界 / 优先级 / 评价指标 / 测试场景（概念 Skill Spec 见 [../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)）。其余一个 Core Skill（Marketing Brief）Contract **仍待确认**。
- **两种运行模式：** `Evidence-backed Mode`（有真实用户证据 → Evidence-backed Insight，须有真实 Fragment / 可追溯 ID / 明确 Source Scope / 有效 Source Version / 支持与反向证据可查看 / 不扩大样本 / 不以少量代表全部）与 `Degraded Hypothesis Mode`（无足够直接用户证据 → 基于商品事实 / 用途 / 场景 / 品类任务 / 竞品证据 / 用户提供目标人群生成 Hypothesis to Validate，必须标记「当前没有直接用户证据·待验证假设」，**不得**表示为用户共识，**不得**生成带引号的模拟用户原声；默认 MVP 可无证据时继续，阶段 `valid_with_limitations`）。
- **必须区分 Theme 与 Insight：** Theme（漏水 / 保温 / 重量 / 外观 / 清洗 / 价格 / 售后 …）只回答「用户在讨论什么？」，本身**不**自动构成洞察；Insight 至少须表达「谁 + 在什么场景 + 遇到什么问题或需求 + 为什么重要 + 如何影响使用 / 购买 / 信任」。「用户提到了漏水」**不得**包装成完整 Insight。
- **Hard Rules（Skill 契约硬规则）：** `No fabricated customer quote`（用户原声必须来自真实 Fragment，不得自造 / 拼接 / 改写冒充 / 概括伪装 / 竞品冒充当前商品 / 翻译伪装原文）；`No Top-K frequency extrapolation`（正式比例必须由确定性统计产生，禁止用 RAG Top-K 召回推断总体频率）；`No competitor feedback misattribution`（竞品反馈不得归因为当前商品用户证据）；`No unsupported consensus claim`（单条反馈只能 Anecdotal Signal，不得表达为普遍共识）。
- **Evidence Coverage 替代模型百分制 Confidence：** MVP **不**使用模型主观百分制 Confidence，改用可解释证据覆盖状态（none / anecdotal / repeated_signal / dataset_supported / multi_source_corroborated，最终名称未确认）；不设统一僵硬样本门槛（一条严重安全投诉可能高价值、机器人评论可能无独立性、一次深访可能胜过多条短评），但**单条反馈不能被表达为普遍用户共识**；单条严重反馈可输出 `Critical Anecdotal Signal`。
- **Insights Version 须经 Validator 18 项才写入 Current Truth：** LLM 输出写入正式 Insights Version 前须经 18 项硬校验（承接 DEC-025 Evidence Validator + DEC-011「未经校验的 LLM 输出不得自动成为已确认业务事实」），硬校验失败**不得**写入 Insights Current Truth；该 Skill 输出 Customer Insights Version 是下游 Product Positioning 的主要输入之一，Insight 错误会传播至 Positioning 与 Marketing Brief。
- **下游 Positioning 必须读取 Insight 的 Evidence Class 和 Limitations：** 运行于 `valid_with_limitations` 时，Product Positioning Skill **必须**读取并展示 Insight 的 `evidence_class` 与 `limitations[]`，**不**得把 Hypothesis 当作 Evidence-backed Insight 使用。

> 注：本节确认**第二个核心 Skill Contract 对 Agent 层的影响**（两种运行模式 + Theme/Insight 分离 + Hard Rules + Evidence Coverage 替代 Confidence + Validator 18 项 + 下游须读 Evidence Class/Limitations；承接 DEC-007/008/009/011/014/015/017/020/024/025/026）；详细 Insight 数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-027 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-027 节。**仍待确认** 该 Skill 最终 Insight Schema / Prompt / 代码 / LangGraph Node 对应、Insight Types 最终名称与 Schema、Evidence Coverage 最终枚举名、评论主题分类表、聚类算法、情感分析实现、Dataset Statistic 记录格式、Customer Language Locator Schema、Golden Dataset 最终数据；以及其余一个 Core Skill（Marketing Brief）Contract。本节**不**创建正式评论分析 Prompt / Skill 代码 / LangGraph Node / 评论聚类代码 / Embedding / 评论导入器 / 数据库表 / 前端页面 / 情感分析实现，**不**选择模型 / Embedding / 聚类算法 / 情感分析工具 / 数据库 / 评论文件格式 / 最低评论数量 / 频率阈值。

### 第三个核心 Skill Contract 对 Agent 层的影响（DEC-028，Accepted，2026-07-28）

> 来源：[DEC-028 — Product Positioning Skill 采用多候选、证据约束与强制人工决策契约](../decisions/dec-028-product-positioning-skill-contract.md)；概念 Skill Spec：[../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)。Amends DEC-018。

```
Core Skill:
Product Positioning

Output:
2–4 Positioning Candidates

Hard Rules:
- No Proof Point without Valid Fact
- No competitor capability leakage
- No automatic final positioning

Required Next Step:
Human Review
```

- **第三个 Core Skill Contract 已确认：** Product Positioning Skill（DEC-020 链路第三位，`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation`，承接 DEC-018 Adapt 供体方向）现在拥有**概念层执行契约**：业务目标 / 职责 / 非职责 / Positioning 属 Strategic Inference / 输入 / Facts·Insights·Positioning 边界 / Positioning Candidate 概念 / Positioning Elements / Competitor Gap 边界 / 候选数量与战略类型 / 可解释排序维度 / 有限证据模式 / 五组输出 / Human Review Package / 工作流决策边界 / Validator 20 项 / 职责边界 / 评价指标 / 测试场景（概念 Skill Spec 见 [../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)）。其余一个 Core Skill（Marketing Brief）Contract **仍待确认**。
- **Positioning 属 Strategic Inference 非 Explicit Fact：** Positioning 是在 Facts + Insights + 竞品证据 + 业务约束之上的战略推断；推导链 `Valid Facts + Valid/Limited Insights + Competitor Evidence + Business Constraints → Positioning Candidates → Human Review → Approved Strategy Version`；模型候选**不得**被描述为来源直接表达的事实、已证明市场结论、唯一正确答案或用户已确认真实需求。
- **Hard Rules（Skill 契约硬规则）：** `No Proof Point without a valid Fact`（Proof Point 必须成立 `Proof Point → Valid Fact → Evidence Link → Fragment → Source Version`，Fact 失效时 Proof Point 同步失效）；`No competitor capability attributed to current product`（竞品证据只能用于 Gap 和品类 Context，不得归因当前商品能力或进入当前商品 Proof Point）；`No hypothesis presented as verified customer truth`（Target Segment / Opportunity / 重要需求在证据不足时须标记 Hypothesis 并传播 Evidence Limitations）；`No automatic final positioning decision`（模型推荐仅是建议，不自动成为 Approved Strategy）。
- **多候选 + 实质差异 + 强制 Human Review：** 默认生成 3 个、允许 2–4 个定位候选；候选之间必须存在**实质差异**（如 通勤轻量 / 密封安心 / 清洁便利），不得仅为同一句定位的语言改写；证据不足时**不得**为达数量生成重复 / 空洞 / 虚假候选；生成候选后工作流**必须**进入 Human Review，**不得**直接进入 Marketing Brief Generation。
- **不使用不透明综合数字分数：** MVP **不**使用模型生成的不透明综合数字分数（如 `positioning_score = 91`），改用可解释 7 维排序（product_truth_fit / customer_relevance / evidence_support / differentiation_credibility / strategic_clarity / execution_potential / risk_level）；模型可输出推荐 + 理由 + 风险 + 成功条件 + 待验证假设，但 Recommendation **不**自动成为 Approved Strategy。
- **Positioning Candidates 须经 Validator 20 项才进入 Human Review：** 进入 Human Review 前须经 20 项硬校验（Facts / Insights Version 有效 / Fact·Insight ID 真实存在 / Proof Point 可回溯有效 Fact / Competitor Evidence 未表示当前商品能力 / 无无来源数值认证性能声明 / Hypothesis 未表示为用户共识 / 未虚构人口统计特征 / 比较级最高级有可靠依据 / Reasons to Believe 与商品事实语义相关 / Differentiation 未超出竞品证据范围 / 候选间实质差异 / 候选数量在范围内 / Evidence Limitations 已传播 / Source Version 可用 / 未用失效上游结果 / 符合 Schema / Proof Point 不含 Marketing Expression / Approved Strategy 未自动创建），硬校验失败**不得**进入审核；该 Skill 输出经 Human Review 形成的 Approved Strategy Version 是下游 Marketing Brief Generation 的主要输入之一，定位错误会传播至 Marketing Brief 与平台映射。

> 注：本节确认**第三个核心 Skill Contract 对 Agent 层的影响**（多候选 + Strategic Inference 边界 + Hard Rules + 可解释 7 维排序替代综合分数 + Validator 20 项 + 强制 Human Review → Approved Strategy Version；承接 DEC-007/008/009/011/015/018/020/024/025/026/027）；详细 Positioning 数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-028 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-028 节。**仍待确认** 该 Skill 最终 Positioning Schema / Prompt / 代码 / LangGraph Node 对应、Approved Strategy Version 最终 Schema、Comparison Matrix 最终字段、候选相似度算法、排序公式与维度权重、竞品数量、Human Review Payload、品类模板、高风险比较声明规则实现、Golden Dataset 最终数据；以及其余一个 Core Skill（Marketing Brief）Contract。本节**不**创建正式 Positioning Prompt / Skill 代码 / LangGraph Node / Human Review 页面 / 数据库表 / 候选相似度算法 / 排序算法 / 市场研究代码，**不**选择模型 / Prompt Framework / 竞品数量 / 排序公式 / Human Review UI 技术 / 数据库 / 高风险比较声明规则实现。（Human Review and Approved Strategy Contract 已由 DEC-029 在概念层确认；具体 Review UI / Resume / Draft 自动保存等仍属 NOT READY。）

### Human Review Contract 对 Agent 层的影响（DEC-029，Accepted，2026-07-28）

> 来源：[DEC-029 — Human Review 采用版本化审核包、结构化用户决策与事务化 Approved Strategy 契约](../decisions/dec-029-human-review-and-approved-strategy-contract.md)；概念规格：[../specs/workflow/human-review-and-approved-strategy-contract.md](../specs/workflow/human-review-and-approved-strategy-contract.md)。Amends DEC-007 / DEC-024。

```text
Mandatory Human Review:
Required after Product Positioning

Output:
Approved Strategy Version

Hard Rules:
- Explicit user submission required
- No stale review submission
- No unsupported Proof Point
- No automatic hypothesis approval
```

- **首个非 Skill 的核心工作流 Contract 已确认：** Human Review（DEC-020 链路中 Product Positioning 与 Marketing Brief Generation 之间的强制 Gate）现在拥有**概念层执行契约**：业务目标 / Review Package（版本化输入快照）/ Version Validity / 必审内容 / 8 项 Review Actions / Strategy Draft / Approved Strategy / Hypothesis Decisions / Evidence Limitation Decisions / Proof Point Review / 提交事务（18 步原子）/ 幂等与并发 / 撤回 / 审核历史 / Review Status 9 值 / Validator 25 项 / 职责边界 / 评价指标 / 测试场景（概念规格见 [../specs/workflow/human-review-and-approved-strategy-contract.md](../specs/workflow/human-review-and-approved-strategy-contract.md)）。Marketing Brief Generation Skill Contract **仍待确认**。
- **Mandatory Human Review（承接 DEC-021 Skill-specialized LLM Node + DEC-023 Interrupt / Resume + DEC-024 ReviewState）：** Product Positioning 生成候选后工作流**必须**进入 Human Review Interrupt，**不**直接进入 Marketing Brief Generation；用户明确 submit 并通过 Validator 后才创建 Approved Strategy Version；LLM 仅辅助（解释差异 / 润色编辑 / 检查一致性 / 提示遗漏假设风险 / 总结修改），**禁止**自动选择 / 自动接受 Hypothesis / 自动删除 Evidence Limitation / 自动批准 / 自动提交 / 把无证据内容升级为 Proof Point / 绕过 Validator。
- **Strategy Draft 不属 Current Truth、Approved Strategy Version 为唯一战略输入：** Strategy Draft 为临时工作内容（不更新 Current Truth、Marketing Brief 不可读）；只有 Approved Strategy Version（版本化 Domain Object，承接 DEC-024）是 Marketing Brief Generation 的唯一正式战略输入。
- **Hard Rules（契约硬规则）：** `Explicit user submission required`（无明确 submit 不创建 Approved Strategy）/ `No stale review submission`（上游版本变化 → 旧 Package superseded、旧提交拒绝）/ `No unsupported Proof Point`（无证据内容不得升级为 Proof Point）/ `No automatic hypothesis approval`（接受 Hypothesis ≠ Hypothesis→Fact，不得自动接受或转 Fact）。
- **Review Status 9 值 + Validator 25 项：** 概念状态 not_ready / pending / in_progress / changes_requested / submitted / approved / superseded / withdrawn / cancelled（最终名未确认）；Approved Strategy 创建前须经 25 项确定性校验（Package / 版本 / 必审项 / Schema / 证据 / Hypothesis / Evidence Limitation / 幂等 / 并发等）。

> 注：本节确认**首个 Workflow Contract 对 Agent 层的影响**（强制 Human Review + Review Package + 8 Review Actions + Strategy Draft / Approved Strategy 分离 + Hard Rules + Validator 25 项；承接 DEC-007/009/011/015/020/021/023/024/025/028，Amends DEC-007 / DEC-024 不推翻既有结论）；详细数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-029 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-029 节。**仍待确认** Review Service / Approved Strategy Service 接口、Review UI、LangGraph Interrupt Payload、Resume 实现、Draft 自动保存频率、并发锁实现、Review / Hypothesis / Proof Point / Evidence Limitation Decision 最终字段、Audit / Withdrawal Record 最终 Schema、Review Status 最终枚举名、错误代码；以及 Marketing Brief Generation Skill Contract（已由 DEC-030 确认，见下节）。本节**不**创建 Review UI / LangGraph Interrupt 代码 / Resume 代码 / 数据库表 / API / 并发锁实现 / Transaction 代码 / Draft 自动保存代码 / Approved Strategy Service 代码，**不**选择前端框架 / 数据库 / 并发控制技术 / Draft 存储方案 / API 框架 / 权限系统 / 多人审批系统。（Marketing Brief Generation Skill Contract 已由 DEC-030 在概念层确认；具体 Brief UI / Prompt / Tone 模板 / 风险词库 / CTA 分类等仍属 NOT READY。）

### Marketing Brief Generation Skill Contract 对 Agent 层的影响（DEC-030，Accepted，2026-07-28）

> 来源：[DEC-030 — Marketing Brief Generation 采用 Approved Strategy 锁定、平台无关信息架构与证据限制传播契约](../decisions/dec-030-marketing-brief-generation-skill-contract.md)（Skill Contract / Marketing Architecture；Amends DEC-006 + DEC-019）。概念 Skill Spec 见 [../specs/skills/marketing-brief-generation-skill.md](../specs/skills/marketing-brief-generation-skill.md)。

- **第四个 Core Skill Contract 已确认：** Marketing Brief Generation Skill（DEC-020 链路第四位，`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation → Xiaohongshu Brief Mapping`，承接 DEC-019 Partial Adapt 供体方向 + DEC-029 Approved Strategy Version 输入）现在拥有**概念层执行契约**：业务目标 / 职责 / 非职责 / Authoritative Input / Strategy Lock / Positioning 与 Brief 边界 / MarketingBrief 概念 / Communication Objective / Audience / Core Message / Message Hierarchy / Benefit Hierarchy / Reasons to Believe / Proof Points / Objection Handling / Content Angles / Tone and Voice / CTA Objective / Hypothesis 与 Evidence Limitation 传播 / Mandatory Messages / Prohibited Claims / 平台无关边界 / 六组输出 / Workflow Decision / Brief 编辑与失效 / Validator 23 项 / 职责边界 / 评价指标 / 测试场景（概念 Skill Spec 见 [../specs/skills/marketing-brief-generation-skill.md](../specs/skills/marketing-brief-generation-skill.md)）。Xiaohongshu Brief Mapping Adapter Contract **已由 DEC-031 确认，见下节**。
- **Approved Strategy 锁定 + 平台无关（承接 DEC-021 受约束 LLM Node + DEC-024 版本引用 + DEC-025 / DEC-028 / DEC-029 Proof Point 追溯）：** Marketing Brief Skill 只能读取当前有效 `approved_strategy_version_id`；不得用未审核 Candidate / Strategy Draft / Model Recommendation / 已撤回或失效 Strategy / 历史旧版本 Strategy；输出保持平台无关，不生成小红书标题 / 正文 / Emoji / Hashtags / 封面文字 / 平台字数 / 热词 / 发布格式 / 最终广告文案。
- **Strategy Lock 不可绕过：** Skill 可精炼表达 / 拆分信息 / 调传播顺序 / 把战略转化为利益点与内容角度，但不得替换目标用户 / 改变核心需求 / 引入新定位 / 次要能力升核心 / 创造新竞争优势 / 删除真实证据限制；若 Brief 须改变 Strategy 返回 `strategy_change_required` 重新进入 Human Review，不写入新 Brief Current Truth。

```text
Core Skill:
Marketing Brief Generation

Authoritative Input:
Approved Strategy Version

Output:
Platform-neutral Marketing Brief

Hard Rules:
- No Strategy Drift
- No unsupported Proof Point
- No platform-specific final copy
- Preserve Hypotheses and Evidence Limitations
```

- **六组输出 + Workflow Decision 6 值：** Brief Context / Audience and Message Architecture / Evidence and Trust / Creative Direction / Guardrails / Workflow Decision（`valid` / `valid_with_limitations` / `strategy_change_required` / `waiting_input` / `paused` / `failed`，非关键缺失优先 `valid_with_limitations` 避免过度暂停）；确定性 Validator 23 项为写入 Brief Current Truth 前的必要 Gate。

> 注：本节确认**第四个核心 Skill Contract 对 Agent 层的影响**（Approved Strategy 锁定 + 平台无关 + Strategy Lock + Hard Rules + Validator 23 项；承接 DEC-006/009/011/015/019/020/024/025/028/029，Amends DEC-006 / DEC-019 不推翻既有结论）；详细 Brief 数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-030 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-030 节。**仍待确认** 该 Skill 最终 Marketing Brief Schema / Prompt / 代码 / LangGraph Node 对应、Content Angle 分类表、Tone 模板、Brand Guidelines 格式与解析、风险词库、CTA 分类、Objection 选择规则、approved_wording 改写边界、Brief UI、最终错误代码、Golden Dataset 最终数据；以及 Xiaohongshu Brief Mapping Adapter Contract（已由 DEC-031 确认，见下节）。本节**不**创建正式 Brief Prompt / Skill 代码 / LangGraph Node / Brief UI / 数据库表 / Risk Validator 实现 / Brand Guideline Parser / 平台内容生成器，**不**选择模型 / Prompt Framework / Tone 模板 / 风险词库 / CTA 分类 / 前端框架 / 数据库。

### Xiaohongshu Brief Mapping Adapter Contract 对 Agent 层的影响（DEC-031，Accepted，2026-07-29）

> 来源：[DEC-031 — Xiaohongshu Brief Mapping Adapter 采用 Brief 锁定、版本化平台政策快照、真实体验边界与方向化输出契约](../decisions/dec-031-xiaohongshu-brief-mapping-adapter-contract.md)（Platform Adapter Contract / Platform Architecture；Amends DEC-004 + DEC-020）。概念 Platform Adapter Spec 见 [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)。

- **DEC-020「4 Core Skills + 1 Platform Adapter」中的「+1 Platform Adapter」概念层执行契约已确认：** Xiaohongshu Brief Mapping Adapter（DEC-020 核心链路最后一位，`Product Intake & Fact Extraction → Customer Insight Analysis → Product Positioning → Human Review Gate → Marketing Brief Generation → Xiaohongshu Brief Mapping`，承接 DEC-030 平台无关 Marketing Brief Version 输入）现在拥有**概念层执行契约**：业务目标 / 职责 / 非职责 / Adapter 与 Skill 边界 / Authoritative Input / Platform Policy Snapshot / Account and Campaign Context / Adapter Lock / MVP 输出边界 / 支持笔记形式 / Platform Objective Mapping / Content Modes / Title Directions / Cover Direction / Narrative Structure / Content Angle Mapping / Customer Language / Experience 边界 / Tone Mapping / CTA Mapping / Search and Hashtag Directions / Prohibited Claims 继承 / 六组 Execution Brief 输出 / Workflow Decision / Editing 与 Invalidation / Validator 28 项 / 职责边界 / 评价指标 / 测试场景（概念 Platform Adapter Spec 见 [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)）。至此 DEC-020 核心链路 4 Core Skills + 1 Platform Adapter 的全部概念层契约均已确认。
- **Business Skill 决定讲什么，Platform Adapter 决定在小红书上如何组织和呈现（承接 DEC-021 受约束 LLM Node + DEC-024 版本引用 + DEC-025 / DEC-030 Proof Point 与 Evidence Limitation 追溯）：** Adapter 只能读取当前有效 `marketing_brief_version_id`（并引用 approved_strategy_version_id / facts_version_id / platform_policy_snapshot_id）；不得用未审核 Positioning Candidate / Strategy Draft / 未审核 Marketing Brief 草稿或旧版本；不得直接修改 Approved Strategy 或创建新 Proof Point；输出为方向化 Execution Brief，**不**生成最终小红书标题 / 正文 / Hashtags / 封面文字 / 视频分镜终稿。
- **版本化 Platform Policy Snapshot + 真实体验边界（承接 DEC-025 时间敏感来源）：** 平台政策为外部、随时间变化的来源；Adapter **不得**在 Prompt 硬编码假设长期有效的平台规则，每次执行必须记录所用的 `policy_snapshot_id` / `policy_version`；Snapshot 失效或不可用返回 `platform_policy_update_required`。真实用户原声必须来自真实 Fragment；无真实素材时 Experience Sharing Mode 不得使用，相关内容降级为待验证方向，**禁止**虚构亲测 / 闺蜜推荐 / 伪造素人身份。
- **Adapter Lock 不可绕过：** Adapter 可调序 / 选笔记形式 / 映射 Content Angle / 调整平台语气 / 生成标题封面方向 / 映射搜索意图与 CTA / 加平台风险注释，但不得替换 Audience / 改 Core Message / 改 Benefit Hierarchy / 创新商品能力或 Proof Point / 删 Evidence Limitation / 把 Hypothesis 转 Fact / 重定义 Approved Strategy / 用平台热词覆盖业务事实 / 通过平台表达（含错字 / 拼音 / 谐音 / 拆字 / Emoji）规避 Prohibited Claims；须改 Brief 返回 `brief_change_required`，不静默修改 Marketing Brief。

```text
Platform Adapter:
Xiaohongshu Brief Mapping

Authoritative Input:
Current Marketing Brief Version

Output:
Xiaohongshu Execution Brief

Hard Rules:
- No Strategy Drift
- No Marketing Brief Drift
- No Fabricated Experience
- No Final Copy in MVP
```

- **六组 Execution Brief 输出 + Workflow Decision 7 值：** Platform Context / Note Strategy / Content Architecture / Discovery and Interaction / Evidence and Guardrails / Workflow Decision（`valid` / `valid_with_limitations` / `brief_change_required` / `platform_policy_update_required` / `waiting_input` / `paused` / `failed`，非关键缺失优先 `valid_with_limitations`）；确定性 Validator 28 项为写入 Execution Brief Current Truth 前的必要 Gate。

> 注：本节确认**Xiaohongshu Brief Mapping Adapter Contract 对 Agent 层的影响**（Brief 锁定 + 版本化 Platform Policy Snapshot + 真实体验边界 + 方向化输出 + Adapter Lock + Hard Rules + Validator 28 项；承接 DEC-004/006/009/011/014/015/019/020/024/025/029/030，Amends DEC-004 / DEC-020 不推翻既有结论）；详细 Execution Brief 数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-031 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-031 节。**仍待确认** 该 Adapter 最终 Execution Brief Schema / Prompt / 代码 / LangGraph Node 对应、Platform Policy Snapshot 采集与同步机制、Account and Campaign Context 最终结构、Content Mode 分类表、Title / Cover 模板、Narrative Structure 模块组合规则、笔记形式选择规则、关键词相关性判定算法、Hashtag 方向数量边界、视频镜头信息方向结构、风险词库、Execution Brief UI、最终错误代码、Golden Dataset 最终数据；以及下一议题 Hybrid Retrieval and Evidence Runtime Architecture 已由 DEC-032 确认（见下节）。本节**不**创建正式小红书 Prompt / 最终标题 / 正文 / Hashtags 生成 / Final Copy Generator / 发布代码 / Platform Policy Sync 代码 / 数据库表 / 风险词库 / 自动审核实现 / 图文或视频生成代码，**不**选择平台数据供应商 / 热点接口 / 搜索关键词工具 / 风险审核供应商 / 视频时长 / 图文页数 / Hashtag 数量 / 发布 API / 最终 LLM。

---

### Hybrid Retrieval and Evidence Runtime Contract 对 Agent 层的影响（DEC-032，Accepted，2026-07-29）

> 来源：[DEC-032 — Hybrid Retrieval and Evidence Runtime 采用 Direct-first 检索、确定性检索规划、强制权限与版本过滤与可复现证据装配](../decisions/dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)（Runtime Architecture / Retrieval Architecture / Evidence Architecture；Amends DEC-014）。概念 Runtime Spec 见 [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)。

- **跨 Skill 共享运行架构层已确认（承接 DEC-014 / DEC-025，Amends DEC-014）：** Hybrid Retrieval and Evidence Runtime 不是某个 Skill 的内部实现，也不是 Core Skill Contract / Platform Adapter Contract，而是服务于所有 Skill（Product Intake / Customer Insight / Positioning / Marketing Brief / Xiaohongshu Adapter）与 Evidence Validator 的检索与证据装配运行架构（概念 Runtime Spec 见 [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)）。
- **Direct-first + Retrieval-on-demand（承接 DEC-021 受约束 LLM Node + DEC-024 版本引用 + DEC-025 Evidence Package + Source Scope 隔离）：** 能直接读取时不使用检索；需要检索时先限定任务 / 权限 / 商品身份 / 来源范围 / 来源版本，再选 Lexical / Semantic / Hybrid。一个高度相关但不属于当前任务或当前允许 Source Set 的 Fragment 必须被**排除**，而不是仅降低排名。检索优先级 = Structured Direct Read → Exact ID / Key Lookup → Bounded Direct Document Read → Lexical Retrieval → Semantic Retrieval → Hybrid Retrieval → Optional Reranking（前置能解决就不走后置，非每个请求跑完所有层）。
- **Skill 不直接查询任意 Source（承接 DEC-025）：** Skill 通过 Retrieval Runtime 请求证据；Deterministic Retrieval Planner 决定检索方式；Permission / Task / Product Identity / Source Scope / Source Version 由确定性逻辑控制；LLM 可有限辅助 Query Planning 但不得决定 task_id / 权限 / Source Scope / Source Set Version，精确标识符（SKU / 型号 / 认证编号 / Fragment ID / Source Version ID）须逐字保留。
- **检索结果不是正式证据（承接 DEC-025 Evidence Validator）：** Runtime 输出 = Candidate Fragments + Retrieval Logs + Reproducible Evidence Package，**不**是 Formal Evidence Link / Fact / Insight / Positioning / Approved Strategy / Execution Brief；检索结果仅候选证据，须经 Evidence Validator 校验并通过正式事务才创建 Formal Evidence Link；禁止用 Top-K 召回结果推断总体频率 / 共识 / 市场份额。

```text
Retrieval Runtime:
Direct-first and Retrieval-on-demand

Output:
Candidate Fragments and Evidence Package

Hard Rules:
- Scope filters before relevance
- No cross-task retrieval
- No Current Product / Competitor leakage
- Retrieval result is not Formal Evidence
- No Top-K frequency extrapolation
```

> 注：本节确认**Hybrid Retrieval and Evidence Runtime Contract 对 Agent 层的影响**（Direct-first + Retrieval-on-demand + Deterministic Retrieval Planning + Mandatory Permission and Version Filtering + Reproducible Evidence Package + Hard Rules；承接 DEC-008/009/013/014/015/021/023/024/025/026/027/028/030/031，Amends DEC-014 不推翻既有结论）；详细数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-032 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-032 节。**仍待确认** Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization 与融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / RetrievalPlan / RetrievalRequest / Candidate Fragment / Evidence Package 最终 Schema / 最终错误代码 / Golden Dataset 最终数据。本节**不**创建正式 Embedding / Vector Index / Full-text Index 代码 / Retrieval API / Query Rewrite Prompt / Reranker 代码 / Fusion 代码 / Cache 代码 / 数据库表 / LangGraph Retrieval Node / 业务实现代码。下一议题 Workflow Runtime Failure Recovery, Retry and Observability Contract 已由 DEC-033 确认（见下节）。

---

### Workflow Runtime Failure Recovery, Retry and Observability Contract 对 Agent 层的影响（DEC-033，Accepted，2026-07-29）

> 来源：[DEC-033 — Workflow Runtime 采用分层运行记录、分类故障处置、有界重试、安全恢复、事务幂等与端到端可观测性契约](../decisions/dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)（Runtime Architecture / Reliability Architecture / Observability Architecture；Amends DEC-023 / DEC-024 / DEC-029）。概念 Runtime Spec 见 [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)。

- **跨 Skill 共享运行架构层已确认（承接 DEC-023 / DEC-024 / DEC-029，Amends DEC-023 / DEC-024 / DEC-029）：** Workflow Runtime 的失败恢复、重试与可观测性不是某个 Skill 的内部实现，也不是 Core Skill Contract / Platform Adapter Contract / Retrieval Runtime，而是服务于所有 Skill、Evidence Validator、Human Review、Tool 调用与业务事务的共享运行架构层（概念 Runtime Spec 见 [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)）。
- **分层执行身份（承接 DEC-024 四标识符 + DEC-013 任务级持久化）：** 运行时区分 Task / Workflow Run / Skill Run / Node Execution / Execution Attempt 五层；沿用 `task_id` / `thread_id` / `run_id` / `checkpoint_id`，新增 `skill_run_id` / `node_execution_id` / `attempt_id` / `error_id` / `trace_id` / `recovery_case_id`，形成完整执行关联链。Agent（统一 `Ecommerce Strategy Agent`）对用户呈现的每一次业务交互都对应一个或多个上述运行记录。
- **Retry ≠ Rerun（承接 DEC-011 确定性控制 + DEC-009 阶段失效）：** 技术故障（网络 / LLM 超时 / 429 / DB / Retrieval 暂时不可用）在同一 Skill Run + 同一 Node + 不同 Attempt、同一逻辑输入与同一幂等身份下有界重试，**不创建业务版本**；用户要求 / 上游版本变化 / 业务失效 / 配置升级触发 Rerun，创建新 `run_id` + `skill_run_id`，可能创建新业务候选版本。Agent 不得用技术 Retry 伪装业务 Rerun，也不得用业务 Rerun 掩盖技术故障。
- **业务控制状态 ≠ 技术失败（承接 DEC-007 人工审核 + DEC-026/027 输入完整度 + DEC-029 Review Package）：** `waiting_for_input` / `waiting_for_review` / `paused` 是业务控制状态，不得自动重试、记为 Provider Failure、触发基础设施告警或描述为崩溃。Agent 须将这些状态作为对用户的可操作提示，而非系统错误。
- **恢复不得绕过业务规则（承接 DEC-025 Evidence Validator + DEC-029 Review Package + DEC-024 Current Truth）：** Checkpoint ≠ 业务 Current Truth；LangGraph Checkpointer 只负责执行状态恢复 / Interrupt / Node 进度 / 临时上下文，不保存 Current Truth、不替代业务 Repository、不判断版本有效、不覆盖新状态；Safe Resume Boundary 只从安全边界 Resume；Checkpoint Reconciliation 在 Resume 前验证 task_id / thread_id / input_version_ids / Current Truth Pointers / stage_validity / review_package_version，旧版本 → `stale` 不执行旧计划；Human Review Resume 携带 review_id / review_package_version / draft_version，须幂等，旧 Review Package 不得通过 Checkpoint 绕过 DEC-029 版本校验；Manual Recovery 不得伪造 Fact / 绕 Validator / 改 Evidence Link / 直接改 Pointer。
- **事务与可观测性（承接 DEC-032 Evidence Package + DEC-024 审计）：** 业务写入遵循 Candidate → Deterministic Validation → Atomic Commit，任一失败整体回滚，不留下部分 Current Truth；Side-effect Tool（未来发布等）须用 `idempotency_key`，MVP 不实现自动发布但保留边界；每次 Workflow Run 产生 Root Trace，结构化日志含全部关联 ID；Fallback 显式记录且限制须传递给用户；Data Integrity Metrics 与 6 项 Hard Reliability Targets 目标 = 0%。

```text
Workflow Runtime:
Layered execution, bounded retry and safe recovery
Runtime Levels:
- Task
- Workflow Run
- Skill Run
- Node Execution
- Attempt
Hard Rules:
- Business waiting is not technical failure
- Retry is not Rerun
- No partial business write
- No stale checkpoint resume
- No Validator bypass during recovery
```

> 注：本节确认**Workflow Runtime Failure Recovery, Retry and Observability Contract 对 Agent 层的影响**（分层执行身份 + 结构化错误分类 + 有界 Retry + 显式 Fallback + Safe Checkpoint Resume + 事务幂等提交 + Manual Recovery + 端到端可观测性；承接 DEC-007/009/011/012/013/023/024/025/029/032，Amends DEC-023 / DEC-024 / DEC-029 不推翻既有结论）；详细数据职责见 [../architecture/data-architecture.md](../architecture/data-architecture.md) DEC-033 节，集成边界见 [../architecture/integration-boundaries.md](../architecture/integration-boundaries.md) DEC-033 节。**仍待确认** Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue·Worker·DLQ 技术 / Logging·Tracing·Metrics·Alerting Provider / 是否采用 OpenTelemetry / Checkpointer 实现 / 数据库 / Outbox / 分布式锁 / 数据保留周期 / 日志采样率 / PII 脱敏实现 / 并发模型 / 最终 SLO / 最终字段名 / 最终错误代码。本节**不**创建正式 Retry Middleware / LangGraph Recovery / Checkpointer / Worker / Queue / DLQ / Recovery Worker / Logging·Tracing Pipeline / Metrics Dashboard / Alerting Rules / 数据库表 / Outbox / 分布式锁 / API / 业务实现代码。在 **Technical Spike Plan and Architecture Readiness Gate** 议题已由 DEC-034 确认（见下节）。

---

### Technical Spike Plan and Architecture Readiness Gate 对 Agent 层的影响（DEC-034，Accepted，2026-07-29）

> 来源：[DEC-034 — 正式开发前必须完成最小架构 Technical Spike，并通过基于证据和用户确认的 Architecture Readiness Gate](../decisions/dec-034-technical-spike-and-architecture-readiness-gate.md)（Architecture Governance / Technical Validation / Development Readiness；Amends DEC-023 / DEC-033）。概念 Readiness Spec 见 [../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../specs/readiness/technical-spike-and-architecture-readiness-gate.md)。

- **正式开发前必须通过 Architecture Readiness Gate（承接 DEC-023 + DEC-033，Amends DEC-023 / DEC-033）：** 决定正式业务实现是否可以开始，不只是某个 Skill 内部实现，而是所有 Skill、Workflow Runtime、Human Review、业务事务共同依赖的开发就绪治理边界（概念 Readiness Spec 见 [../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../specs/readiness/technical-spike-and-architecture-readiness-gate.md)）。
- **Technical Spike 是非生产实验而非 MVP：** Agent 不得将 Spike 当作正式业务实现，不得在 Spike 中产生生产 Prompt / 正式 Schema / 生产 API / 正式前端 / 正式 Retrieval Pipeline / 生产级 Worker / 生产部署配置；Spike 代码是可抛弃的最小架构原型，仅用于验证运行时架构行为，生产模块不得依赖它。
- **Architecture Agent 仅提交 Readiness Recommendation，不得自行宣布 READY：** 最终 Development Status 变化须由用户明确确认。Architecture Agent 可建议 `RECOMMENDED: READY`，但**不能**自行将 `Development Status = READY` 写入 Current Truth。
- **Spike 通过不自动等于 READY：** 在 Spike 证据 + Readiness Review + 用户明确确认三者同时满足前，Development Status 保持 `NOT READY`；且不执行 Spike（执行细节属下一议题 `Technical Spike Execution Brief and Temporary Spike Stack`，尚未确认）、不创建正式业务 Graph、不生成 MVP Roadmap、不拆分正式开发 Issues。

```text
Architecture Readiness:
Technical Spike required before production development

Current Development Status:
NOT READY

Hard Rules:
- Spike is not MVP
- Critical reliability scenarios must pass
- Agent cannot self-declare READY
- Explicit user acceptance is required
```

> 注：本节确认**Technical Spike Plan and Architecture Readiness Gate 对 Agent 层的影响**（正式开发前必须完成最小架构 Technical Spike + Architecture Readiness Gate；Spike 为非生产实验而非 MVP；Architecture Agent 仅提交 Readiness Recommendation、不得自行宣布 READY；Spike 通过不自动等于 READY；承接 DEC-023 / DEC-033，Amends DEC-023 / DEC-033 不推翻既有结论）；详细概念规格见 [../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../specs/readiness/technical-spike-and-architecture-readiness-gate.md)。**仍待确认** Spike 使用的语言和版本 / LangGraph 具体版本 / Spike 数据库 / Checkpointer Backend / Mock LLM 实现 / Fault Injection 工具 / 测试框架 / Trace Provider / 临时 API / Spike 代码目录 / Spike 执行 Agent / 执行时间计划 / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号。本节**不**创建正式业务 Graph / 四个核心 Skill 的生产 Prompt / 正式数据库 Schema / 生产 API / 正式前端 / 正式 Retrieval Pipeline / 生产级 Worker / 生产部署配置。**Technical Spike Execution Brief and Temporary Spike Stack 议题已由 DEC-035 确认（见下节）。**

---

### Technical Spike 临时技术栈与执行契约对 Agent 层的影响（DEC-035，Accepted，2026-07-29）

> 来源：[DEC-035 — Technical Spike 临时采用 Python、同步 LangGraph StateGraph、分离式 SQLite 存储、确定性 Mock 与场景化故障注入执行契约](../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)（Technical Spike Execution / Temporary Architecture / Validation Environment；Amends DEC-034）。概念规格见 [../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)；Spike 临时栈见 [../spikes/spike-001-langgraph-runtime-and-recovery/temporary-stack.md](../spikes/spike-001-langgraph-runtime-and-recovery/temporary-stack.md)；执行简报见 [../spikes/spike-001-langgraph-runtime-and-recovery/execution-brief.md](../spikes/spike-001-langgraph-runtime-and-recovery/execution-brief.md)。

```text
Spike-001 Temporary Stack:
- Python 3.13
- LangGraph 1.2.9
- Synchronous StateGraph
- Three separated SQLite stores
- Scripted Model
- Mock Retrieval
- pytest
- Local JSONL Trace

Current Development Status:
NOT READY

Hard Rules:
- Temporary stack is not production architecture
- Spike Agent may only work inside Spike scope
- Agent cannot self-declare READY
```

- **Spike-001 的可执行临时栈已确认（承接 DEC-034，Amends DEC-034）：** DEC-034 确认「必须完成 Technical Spike 并经 Readiness Gate」，本决定在概念层定义 Spike-001 用什么临时环境执行——Python 3.13 + 精确固定 LangGraph 1.2.9 + 同步 StateGraph Invoke + 分离式 SQLite（`business.sqlite` / `runtime.sqlite` / `checkpoints.sqlite`）+ SqliteSaver + Python sqlite3 事务（统一 `BusinessCommitService`）+ Scripted Deterministic Model + Mock Retrieval Runtime + Scenario-based Fault Injection + pytest + Local JSONL Trace + CLI Scenario Runner。**所有临时选择都不构成任何生产承诺**（生产后端语言 / 数据库 / Checkpointer / ORM / Observability / Retrieval / 部署平台仍待后续 RFC）。
- **Human Review 节点边界 + 三类存储物理分离 + Atomic Commit Contract（承接 DEC-024 / DEC-029 / DEC-033）：** 含 `interrupt()` 的 Node 在 Resume 可能从 Node 开头重执行，故 Review Package 创建与 Interrupt 必须分离 Node（`create_review_package → await_human_review → load_approved_strategy`），禁止 `create_review_package + write_business_data + interrupt()` 同 Node；三类 SQLite 物理分离直接验证 `Business State ≠ Runtime State ≠ Checkpoint State`；每次正式业务 Commit 在单一事务内完成（Create Domain Version + Formal Evidence Links + Update Current Truth Pointer + Update Stage State + Write Audit + Write Idempotency Record，任一失败整体回滚），Graph Node 不得绕过 `BusinessCommitService`。Checkpoint 启用严格反序列化边界（`LANGGRAPH_STRICT_MSGPACK=true` 或等价），不存任意 Python 对象 / Secret / 完整业务文档。
- **确定性 Mock + 场景化故障注入 + 结果接受边界：** 必选场景默认使用 `ScriptedModelProvider`（按 Scenario ID / Node / Attempt / Fault Plan 确定性），可选 `Spike-Optional-01 Real Model Structured Output Smoke Test`（非 READY 必选 / 无 API Key 自动 Skip / 不用真实用户数据）；Fault Injection 用显式 `FaultPlan`（禁止散落 `if test_mode: raise`）；每场景须同时提供 Automated Assertion + Runtime Evidence + Human-readable Explanation，自然语言「看起来成功」不算 Pass。
- **Spike Agent 权限与禁止（对执行 Agent 的硬约束）：** Spike Agent 仅可在 `spikes/spike-001-*` + `docs/spikes/spike-001-*` 工作；**不得**修改 Accepted DEC / 创建生产目录或正式业务 Graph / 生成 MVP Roadmap / Epics / Issues / 设 Development Status = READY / 选生产 DB / Checkpointer / Observability / 用真实用户数据 / 外部 Side Effect / 迁移 Spike 代码到生产模块；**不得**擅自更改 LangGraph 1.2.9（遇失败须走 Spike Finding → 等待用户确认，不静默升降级）；S6 报告阶段**不得**自动改变 Development Status。

> 注：本节确认**Technical Spike 临时技术栈与执行契约对 Agent 层的影响**（可执行临时栈 + Human Review 节点边界 + 三类存储物理分离 + Atomic Commit Contract + 确定性 Mock 与故障注入 + Spike Agent 权限与禁止；承接 DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 / DEC-034，Amends DEC-034 不推翻既有结论）。**仍待确认** Spike 主执行 Agent（Codex vs Claude）/ Spike 执行时间计划 / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术。本节**不**创建 Spike 生产代码 / 正式业务 Graph / 生产 Backend / 生产 Database Schema / API / Worker / Queue / Production Observability / Production Retrieval / 正式 Prompt / MVP Roadmap / Epic Map / GitHub Issues，**不**执行 uv sync / 依赖安装 / StateGraph Compile / Scenario Runner / pytest / Fault Injection / SQLite 初始化 / Real Model Smoke Test，**不**选择 Spike 主执行 Agent / Production Backend Language / Database / Checkpointer / LLM / Retrieval / Observability / Deployment Platform，**不**创建 RFC；Development Status 保持 `NOT READY`、Architecture Readiness Status 保持 `NOT READY`、Spike Execution Status 保持 `NOT STARTED`。**Spike 主执行 Agent 与执行授权契约已由 DEC-036 确认（见下节）。**

---

### Spike-001 执行授权契约对 Agent 层的影响（DEC-036，Accepted，2026-07-29）

> 来源：[DEC-036 — Spike-001 采用 Claude 主执行、受控 Git/GitHub 权限、独立 Branch、Issue/PR 追踪、阶段化提交与用户保留 Merge 和 READY 决策权的执行授权契约](../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md)（Agent Governance / Git and GitHub Operations / Spike Execution Authorization；Amends DEC-034 and DEC-035）。概念规格见 [../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md](../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md)；Git/GitHub 权限操作参考见 [git-and-github-permissions.md](git-and-github-permissions.md)。

```text
Primary Execution Agent:
Claude Code

Optional Reviewer:
Codex

Claude Authorized[Audit, Branch, Commit, Issue, DraftPR, Tests, Evidence, Recommendation]

Claude Prohibited[ForcePush, Merge, RewriteHistory, DeleteBranch, ChangeRepoPermissions, SelfREADY]
```

- **核心治理模式 = Agent-controlled mechanical workflow + User-controlled irreversible decisions（承接 DEC-034 / DEC-035，Amends DEC-034 + DEC-035 不推翻既有结论）：** DEC-034 确认「必须完成 Technical Spike 并经 Readiness Gate」，DEC-035 确认「临时技术栈与 Spike Agent 运行边界」，本决定进一步定义 Spike-001 由谁、在什么权限边界内、用什么 Git/GitHub 工作流执行。Claude Code 承担日常 Git/GitHub 机械操作；不可逆、高风险、治理类决策（Accepted Decision 变更 / Scope 扩张批准 / Pull Request Merge / Branch 历史改写批准 / Architecture Readiness 最终确认 / Development Status 变更）继续由用户保留。
- **角色与两种授权分离：** Primary Execution Agent = **Claude Code**（Git Operator / GitHub Issue and PR Operator / Spike Evidence Producer / Readiness Recommendation Author）；Optional Independent Reviewer = **Codex**（S6 完成后单独授权独立 Review，默认不改 Claude Branch）；Product Decision Owner = **User**。`Contract Authorization = ACCEPTED`（本权限契约已接受）≠ `Execution Authorization = NOT GRANTED`（尚未授权实际启动 Spike）；DEC-036 接受后 Spike 仍不得自动启动，`Spike Execution Status = NOT STARTED`。
- **Git/GitHub 工作流与操作边界：** Repository Audit（只读）→ Stable Baseline（含 DEC-001~036）→ Dedicated Spike Branch `spike/001-langgraph-runtime-recovery`（禁止 `main`/`master`/`release/*`/`production/*` 直接开发）→ Stage Commits → Push → Spike Issue → Draft PR → Tests and Evidence → Human Review → User Merge Decision。Authorized Git：`git status/diff/diff --staged/log/show/branch/switch/fetch/add <explicit-paths>/commit/push -u origin <spike-branch>`（Explicit Add Rule：不默认 `git add .`/`-A`）。Prohibited Git：`push --force`/`--force-with-lease`/`reset --hard`/`clean -fd[x]`/`rebase`/`commit --amend`/`branch -D`/`tag`/`tag -d`/`push --delete`。Authorized GitHub：`gh issue create/view/comment/edit`、`gh pr create/view/checks/comment/edit`。Prohibited GitHub：`gh pr merge`/`pr close`/`issue close` + Auto-merge / 绕 Checks / 自批 / 删 Branch / 改 Base / 改仓库权限等。`GitHub Issue 不能替代 Spec；PR 描述不能替代 Accepted Decision；Merge Spike PR ≠ Architecture READY。`
- **Mandatory Stop Conditions + Final Human Gate：** 6 类停止条件（Decision Conflict / Scope Expansion / Version Conflict / Repository Risk / Secret or Data Risk / Architecture Blocking Failure）出现必须停止并报告，不得掩盖绕过；可能推翻 Accepted DEC 的 Spike Finding 仅提交修订建议并等待用户。用户审查 Issue / PR Diff / 测试 / 证据 / Findings / Report / Codex Review 后决定 Merge 与 Readiness；仅当用户明确确认「确认 Architecture READY」才可更新 `Architecture Readiness Status = READY` 与 `Development Status = READY`；`Merge PR ≠ READY，关闭 Issue ≠ READY，Claude Recommendation ≠ READY`。

> 注：本节确认 **Spike-001 执行授权契约对 Agent 层的影响**（Claude 主执行 / Codex 可选 Reviewer / 两种授权分离 / Git/GitHub 操作边界 / Issue·PR 契约 / Mandatory Stop Conditions / Final Human Gate；承接 DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 / DEC-034 / DEC-035，Amends DEC-034 + DEC-035 不推翻既有结论）。本决定接受的是**权限和执行契约，不是立即开始执行 Spike**；DEC-036 被接受后 Spike 仍不得自动启动。**仍待确认** 立即启动 Spike / Baseline Commit SHA / 实际 Issue·PR 编号 / GitHub Labels·Project·Actions / CI Provider / Codex 是否执行独立 Review / Reviewer 身份 / Merge Strategy / Spike PR 是否最终 Merge / Architecture Readiness 结果 / Development Status 是否变为 READY。本节**不**创建 Spike Branch / 实际 GitHub Issue / 实际 Pull Request，**不**执行 git push / 依赖安装 / Spike 代码 / 测试 / S0，**不**关闭 Issue / Merge PR / 更新 Development Status，**不**创建正式 MVP Backlog / Epics / 生产 Issues，**不**创建 RFC；保持 `Contract Authorization = ACCEPTED` / `Execution Authorization = NOT GRANTED` / `Spike Execution Status = NOT STARTED` / `Architecture Readiness Status = NOT READY` / `Development Status = NOT READY`。下一议题：**Formal Spike-001 Execution Authorization**（是否正式授权 Claude 开始执行 Spike / 是否先完成 Repository Audit / 是否允许创建 Spike Issue / 独立 Branch / Push / Draft PR / 是否一次授权覆盖 S0—S6 / 是否要求 Codex 在 S6 后独立 Review / 用户需审查哪些证据）**已由 DEC-037 确认（见下节）。**

---

### Formal Spike-001 Execution Authorization 对 Agent 层的影响（DEC-037，Accepted，2026-07-30）

> 来源：[DEC-037 — 正式授权 Claude Code 在 Repository Audit 和稳定文档基线通过后，执行 Spike-001 S0—S6，并创建受控 Issue、Branch、Commits、Push、Draft PR、测试证据与 Readiness Recommendation](../decisions/dec-037-formal-spike-001-execution-authorization.md)（Execution Authorization / Agent Governance / GitHub Workflow；Amends DEC-034、DEC-035 and DEC-036）。概念规格见 [../specs/readiness/formal-spike-001-execution-authorization.md](../specs/readiness/formal-spike-001-execution-authorization.md)；Git/GitHub 权限操作参考见 [git-and-github-permissions.md](git-and-github-permissions.md)。

```text
Spike-001 Execution Authorization:
GRANTED

Primary Execution Agent:
Claude Code

First Required Action:
Read-only Repository Audit

Execution Scope:
S0—S6

User Retains:
- Merge
- Issue closure
- Decision revision
- Architecture READY
```

- **正式执行授权（承接 DEC-034 / DEC-035 / DEC-036，Amends DEC-034 + DEC-035 + DEC-036 不推翻既有结论）：** DEC-034 确认「必须完成 Technical Spike 并经 Readiness Gate」，DEC-035 确认「临时技术栈与 Spike Agent 运行边界」，DEC-036 确认「Claude 的 Git/GitHub 权限与用户保留治理权限」；本决定正式授予 Claude Code 从规划与归档阶段进入实际仓库执行阶段的授权，作为 Spike-001 Primary Execution Agent 执行 Repository Audit→Stable Documentation Baseline→Spike Issue→Dedicated Spike Branch→S0—S6 Execution→Automated Tests→Runtime Evidence→Draft Pull Request→Spike Report→Readiness Recommendation。**本决定接受的是执行授权，但第一动作仍是只读 Repository Audit，且在 Audit 与稳定基线通过前不得开始任何写入、安装或 Spike 代码。**
- **授权状态迁移与范围：** `Contract Authorization = ACCEPTED`（DEC-036，不变）；`Execution Authorization` 由 `NOT GRANTED` 转为 **`GRANTED`**（Claude 已被允许开始执行，但不表示 Audit 已完成 / Spike 已开始 / 已通过 / Architecture 已 READY / Development 已 READY）；`Spike Execution Status = NOT STARTED`（须待 Claude 实际开始 Repository Audit 后才可更新为 `IN PROGRESS`）；`Architecture Readiness Status = NOT READY` / `Development Status = NOT READY`（不变）。一次授权覆盖 S0—S6，Claude 不必每阶段重新授权但须守阶段更新 Gate 与强制停止条件。
- **第一必需动作 + 稳定文档基线 + 授权产物：** First Required Action = **只读 Repository Audit**（须先形成 Repository Audit Report；Audit 完成前不得安装依赖 / 创建 Spike 代码 / 初始化数据库 / 运行 Spike / 创建 Spike Branch / 创建 Draft PR）。Audit Pass→Create Spike Issue→Create Dedicated Branch→Begin S0；Audit Blocked→停止并报告 Audit Finding / Blocking Risk / Safe Next Actions，不得覆盖删除 Reset 或隐藏修改。Spike Branch 须基于含 DEC-001~037 的稳定 Commit（记录 base_branch / base_commit_sha / created_at / created_by；DEC-037 未进默认 Branch 时先建文档基线 Branch 经 Documentation PR 由用户 Merge）。授权 Spike Issue / 独立 Branch `spike/001-langgraph-runtime-recovery` / S0 首个有效 Commit 后 Draft PR（S1—S6 经同一 Draft PR 更新）。Isolated Dependency Authorization（隔离目录内 `uv sync`/`pytest`）与 Version Compatibility Boundary（Python 3.13 / LangGraph 1.2.9 / pinned langgraph-checkpoint-sqlite，不得自行升降级或更换）。
- **Gate A—E + Mandatory Stop + S6 完成边界 + User Authority：** Execution Gates A（Repository Audit）/ B（S0）/ C（S2）/ D（S4）/ E（S6）更新 Issue + PR（进度与审计 Gate，不自动暂停）；6 类 Mandatory Stop Conditions（Decision Conflict / Scope Expansion / Repository Risk / Dependency Conflict / Architecture Blocking Failure / Data or Secret Risk）出现必须停止受影响工作并创建 Spike Finding，不得为让测试通过而隐藏问题；S6 完成后必须停止，可提交 `RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`，但不得 Merge PR / 关闭 Spike Issue / 自行宣布 READY（S6 后状态 `Spike Execution Status = COMPLETED` / `Architecture Readiness Status = PENDING USER REVIEW` / `Development Status = NOT READY`）；用户保留 Decision 修订 / Scope 批准 / PR Merge / Issue Closure / Git 历史危险操作批准 / Architecture READY 确认 / Development Status 变更权；`PR Merge ≠ READY、Issue Closed ≠ READY、Agent Recommendation ≠ READY`。

> 注：本节确认 **Formal Spike-001 Execution Authorization 对 Agent 层的影响**（正式执行授权 + 授权状态迁移 + First Required Action + 稳定文档基线 + 授权产物 + 隔离依赖授权 + Gate A—E + Mandatory Stop + S6 完成边界 + 用户保留权限；承接 DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 / DEC-034 / DEC-035 / DEC-036，Amends DEC-034 + DEC-035 + DEC-036 不推翻既有结论）。本决定接受的是**从规划和归档阶段进入实际仓库执行阶段的授权**，但第一动作仍是只读 Repository Audit，且在 Audit 与稳定基线通过前不得开始任何写入、安装或 Spike 代码。**已确认** 正式执行授权 / Claude 为执行 Agent / 一次授权覆盖 S0—S6 / First Action 必须是 Repository Audit / Audit Block Handling / Stable Documentation Baseline / Documentation PR / Spike Issue / Dedicated Branch / Draft PR / Stage Commits / Isolated Dependency Installation / Version Conflict Handling / Gate A—E / Mandatory Stop Conditions / S6 Completion Boundary / User Final Authority / Architecture 和 Development 继续 NOT READY。**尚未确认** 实际 Repository Audit 结果 / Baseline Commit SHA / Issue 编号 / Branch 是否已创建 / PR 编号 / 测试结果 / Spike Findings / Codex Independent Review / Merge Strategy / Spike PR 是否 Merge / Architecture Readiness Result / Development Status 是否 READY。本节**不**运行 Repository Audit / 创建实际 GitHub Issue·Branch·PR / Push / 安装依赖 / 创建 Spike 代码 / 运行测试 / 初始化 SQLite / 启动 S0，**不**创建 RFC；保持 `Spike Execution Status = NOT STARTED` / `Architecture Readiness Status = NOT READY` / `Development Status = NOT READY`。下一动作（归档进入稳定 Git 基线后以独立任务执行）：**`Spike-001 Execution Handoff`**（第一步必须是只读 Repository Audit）。

---

## 何时创建 Agent Spec

- 当某个 Agent 的职责边界、输入输出或依赖被用户明确接受为 Accepted Decision 后，复制 [agent-spec-template.md](agent-spec-template.md) 创建对应规格。
- 定义 Agent 职责边界属于重大议题，通常应先有对应 RFC（见 [../rfcs/](../rfcs/)）。

---

## 当前 Agent 列表

> 暂无。待 Agent 架构与职责边界被确认后再创建。

---

## 同步规则

- 仅在决定被明确接受后更新本目录文件。
- Agent Spec 必须与 [../product/](../product/)、[../architecture/](../architecture/) 保持一致。
- 不得为使文档「完整」而补充未经讨论的 Agent 事实。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
