# Data Architecture（数据架构与数据契约）

> **Status: PARTIAL — Workflow State 数据结构（DEC-012）+ 任务级持久化（DEC-013）+ 分层数据访问（DEC-014）+ MVP 业务能力范围（DEC-020）+ 工作流框架对数据架构的要求（DEC-022）+ Checkpoint 与业务 Current Truth 数据边界（DEC-023）+ 四类状态边界与版本化领域状态（DEC-024）+ 来源与证据分层架构（DEC-025）+ 首个核心 Skill Contract 的 Fact 数据职责（DEC-026）+ 第二个核心 Skill Contract 的 Insight 数据职责（DEC-027）+ 第三个核心 Skill Contract 的 Positioning 数据职责（DEC-028）+ Human Review 与 Approved Strategy 的数据职责（DEC-029）+ 第四个核心 Skill Contract 的 Marketing Brief 数据职责（DEC-030）+ Xiaohongshu Brief Mapping Adapter 的数据职责（DEC-031）+ Hybrid Retrieval and Evidence Runtime 的数据职责（DEC-032）+ Workflow Runtime 的数据职责（DEC-033）+ Technical Spike and Architecture Readiness Gate 的数据职责（DEC-034）+ Technical Spike 临时技术栈与执行契约的数据职责（DEC-035：三类物理分离 SQLite[business/runtime/checkpoints]仅 Spike 实验存储非正式数据库设计；Atomic Commit Contract 单一事务；Amends DEC-034）已确认；具体数据契约 / Schema / 数据库 / 向量库 / 检索实现仍待确认**
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：Workflow State 结构与分组原则（DEC-012）、任务级持久化与跨会话恢复原则（DEC-013）、分层数据访问与按需混合 RAG（DEC-014）、首批 MVP 业务能力范围（DEC-020）、工作流框架对数据架构的要求（DEC-022：结构化状态为强制、领域模型独立于框架、持久化范围与幂等并发）、Checkpoint 与业务 Current Truth 数据边界（DEC-023：LangGraph Checkpointer 仅承载执行恢复，业务数据库为正式 Current Truth 来源；Domain State 不绑定 LangGraph 类型；StateGraph 中的业务数据须映射到正式领域模型）、四类状态边界与版本化领域状态（DEC-024：状态划分为 Domain / Workflow / Runtime / Interaction 四类；业务结果版本化 + Current Truth Version Pointers；task_id 稳定业务 ID vs thread_id LangGraph 执行 ID vs run_id vs checkpoint_id 四标识符边界；Checkpointer 与业务数据库职责分离；LangGraph State 紧凑 + 引用为主）、**来源与证据分层架构（DEC-025：Source → Source Version → Document / Record → Fragment → Evidence Link → Versioned Domain Object；版本化来源；可定位 Fragment；Evidence Link 为独立关系对象；Evidence Role 显式；延续五类 Evidence Class；Retrieved Fragment 仅 Candidate Evidence，须经确定性 Validator + 创建 Evidence Link 才成正式证据；Source Set Version + Evidence Package；当前商品与竞品隔离；频率统计须完整可计数数据；Amends DEC-008 / DEC-014）、**首个核心 Skill Contract 的 Fact 数据职责（DEC-026：Fact `raw_value` 与 `normalized_value` 分离；Fact Assertion Type 五分类 direct_fact / documented_claim / certified_or_tested_fact / marketing_expression / unknown_or_ambiguous；Fact Verification Status 为可解释验证状态、不使用模型数字 Confidence；Facts Version 为版本化 Domain Object；当前商品 Source Scope 为正式 Fact 的必要条件（竞品不能证明当前商品）；关键冲突经 SourceConflict + Evidence Link 处理、不由模型自选；Documented Claim 不等于 Verified Fact；Amends DEC-005）、第二个核心 Skill Contract 的 Insight 数据职责（DEC-027：Theme 与 Insight 分离；Insight Evidence Coverage 5 状态 none / anecdotal / repeated_signal / dataset_supported / multi_source_corroborated，不用模型百分制 Confidence；用户原声必须关联真实 Fragment，禁止虚构 / 拼接 / 改写冒充直接引用；Dataset Statistic 与 Retrieved Fragment 分离，正式频率必须由确定性统计产生、禁止 Top-K 频率外推；当前商品与竞品用户证据分离，竞品反馈不能证明当前商品用户；Insights Version 为版本化 Domain Object；Hypothesis 与 Evidence-backed Insight 分离；Amends DEC-017）、第三个核心 Skill Contract 的 Positioning 数据职责（DEC-028：PositioningCandidate 概念对象；Positioning 属 Strategic Inference 非 Explicit Fact；Proof Point 必须回溯到有效 Fact（Proof Point → Fact → Evidence Link → Fragment → Source Version）；竞品证据只能用于 Gap 和 Context，不得归因当前商品能力；Positioning Candidate Version 为版本化 Domain Object；Approved Strategy Version 为经 Human Review 形成的独立版本化对象，是下游 Marketing Brief 的必要输入；Target Segment Hypothesis 与 Opportunity Hypothesis 须显式标记；Positioning 必须传播上游 Evidence Limitations；候选排序使用可解释 7 维而非不透明综合数字分数；Positioning Recommendation 只是建议不等于 Current Truth；Amends DEC-018）、**Human Review 与 Approved Strategy 的数据职责（DEC-029：Review Package Version 为固定上游版本输入快照（review_id / task_id / package_version / facts_version_id / insights_version_id / positioning_version_id / source_set_version_ids[] / positioning_candidates[] / critical_facts[] / critical_insights[] / hypotheses[] / evidence_limitations[] / source_conflicts[] / strategic_risks[] / model_recommendation / created_at / status）；上游版本变化 → Review Package 标 superseded；Strategy Draft Version（draft_id / review_id / draft_version / based_on_candidate_ids[] / selected_content / user_edits[] / merge_sources[] / hypothesis_decisions[] / proof_point_decisions[] / user_notes / updated_at / status，临时工作内容、不属 Current Truth）；Review Decisions（Hypothesis Decisions 5 动作 / Proof Point Decisions accept·remove·rephrase·downgrade·request_evidence / Evidence Limitation Acceptance[accepted_by_user=true 但不删除]）；Approved Strategy Version 为正式版本化 Domain Object（承接 DEC-024，Marketing Brief 唯一战略输入，approved_strategy_version_id / based_on_review_id / based_on_review_package_version / based_on_positioning_version_id / selected_candidate_ids[] / 全部 Positioning Elements / accepted_hypotheses[] / rejected_hypotheses[] / evidence_limitations[] / strategic_risks[] / user_notes / approved_by / approved_at / version_status）；Current Truth Pointer（approved_strategy_version_id，承接 DEC-024，提交事务原子更新）；Hypothesis Decision（接受 Hypothesis ≠ Hypothesis→Fact，须保留 evidence_class）；Evidence Limitation Acceptance（不得静默删除，Marketing Brief 须传播）；Proof Point Decision（无证据内容不得升级为 Proof Point）；Review Audit History（保留全部候选 / 编辑 / Merge / 拒绝 / 决策 / 时间戳 / 失败校验）；Withdrawal Record（撤回创建记录、保留原版本、清除 Pointer、下游失效）；Amends DEC-007 + DEC-024，不推翻既有结论）、**第四个核心 Skill Contract 的 Marketing Brief 数据职责（DEC-030：MarketingBrief Version 为版本化 Domain Object brief_id / brief_version_id / approved_strategy_version_id / facts_version_id / insights_version_id / communication_objective / audience / audience_context / core_message / message_hierarchy / benefit_hierarchy / key_benefits[] / reasons_to_believe[] / proof_points[] / objections[] / objection_responses[] / content_angles[] / tone_and_voice / call_to_action_objective / mandatory_messages[] / prohibited_claims[] / accepted_hypotheses[] / hypotheses_to_test[] / evidence_limitations[] / risk_notes[] / platform_adaptation_rules / workflow_decision）；Approved Strategy Dependency（Authoritative Input 仅 approved_strategy_version_id，不得用未审核 Candidate / Strategy Draft / 已撤回或失效 Strategy）；Message Hierarchy（Primary Message → Secondary Benefits → Supporting Proof，转换链 Fact → Product Capability → User Benefit → Core Message）；Benefit Hierarchy（primary_benefit / secondary_benefit / supporting_feature，1 Primary + 2–4 Secondary）；Proof Point References（proof_point / fact_id / supporting_fragment_ids[] / source_version_id / approved_wording，须 Proof Point → Valid Fact → Evidence Link → Fragment → Source Version）；Content Angles（angle_title / user_tension / message_focus / supporting_benefits[] / proof_points[] / hypothesis_status / risk_notes[]）；Mandatory Messages 与 Prohibited Claims（须传给所有 Platform Adapters）；Hypotheses（accepted_hypotheses[] / hypotheses_to_test[]，接受 ≠ 转 Fact，须保留 requires_validation）；Evidence Limitations（不得删除或弱化，承接 DEC-029）；Brief Current Truth Pointer（brief_version_id，承接 DEC-024；用户编辑创建新 Version + 保留原模型版本 + 重跑 Validator + 更新 Pointer；承接 DEC-009：Brief 修改不使 Facts / Insights / Positioning / Approved Strategy 失效但使 Xiaohongshu Mapping 失效）；Amends DEC-006 + DEC-019，不推翻既有结论）**。**Xiaohongshu Brief Mapping Adapter 的数据职责（DEC-031：Xiaohongshu Execution Brief Version 为版本化 Domain Object（execution_brief_id / execution_brief_version_id / marketing_brief_version_id / approved_strategy_version_id / facts_version_id / platform_policy_snapshot_id / account_context / campaign_context / commercial_context / note_strategy / content_architecture / discovery_and_interaction / evidence_and_guardrails / workflow_decision）；Platform Policy Snapshot（platform / policy_snapshot_id / policy_version / captured_at / applicable_content_type / applicable_industries[] / rule_source_version_ids[] / prohibited_patterns[] / disclosure_requirements[] / qualification_requirements[] / review_route_rules[] / availability_status，外部版本化来源，失效返回 platform_policy_update_required）；Account and Campaign Context（account_type / content_relationship[brand_owned / creator_collaboration / product_seeding / paid_campaign / organic_exploration] / commercial_context / campaign_objective / available_asset_types[]）；Execution Brief 六组输出（Platform Context / Note Strategy / Content Architecture / Discovery and Interaction / Evidence and Guardrails / Workflow Decision）；Content Mode（experience_sharing / problem_solution / usage_scenario / product_demonstration / selection_guide / knowledge_education / objection_response / comparison_context / new_product_introduction，1 主 + 可选次级）；Title Direction（title_direction / user_question_or_tension / primary_keyword / message_focus / proof_required / risk_notes，3–5 方向非最终标题）；Cover Direction（cover_message_direction / cover_visual_focus / cover_information_priority / cover_risk_notes）；Narrative Structure（hook / user_context / user_problem / product_response / proof_or_demonstration / limitations_or_fit_boundary / selection_guidance / interaction_or_CTA，模块化，limitations_or_fit_boundary 不可删）；Search Intent / Keyword Direction / Hashtag Direction（均为方向，非最终列表）；Platform Risk Notes（完整继承 Prohibited Claims + xiaohongshu_specific_risk_notes）；Execution Brief Current Truth Pointer（execution_brief_version_id，承接 DEC-024；用户编辑创建新 Version + 保留原模型版本 + 重跑 Validator + 更新 Pointer；承接 DEC-009：Execution Brief 修改不使 Marketing Brief 与上游失效，因 Execution Brief 为当前 MVP 最终输出，普通编辑不触发下游失效；改 Brief 返回 brief_change_required）；Amends DEC-004 + DEC-020，不推翻既有结论）**。**Hybrid Retrieval and Evidence Runtime 的数据职责（DEC-032：RetrievalRequest 概念字段 task_id / workspace_id / skill_name / retrieval_purpose / query_text / exact_identifiers[] / required_source_scopes[] / allowed_source_set_version_id / required_evidence_types[] / time_constraints / requested_output；RetrievalPlan 概念字段 strategy / structured_queries[] / lexical_queries[] / semantic_queries[] / mandatory_filters / optional_filters / fusion_required / reranking_allowed / coverage_requirements / fallback_strategy，可版本化 retrieval_plan_version；RetrievalRun（每次检索一条，记录 Plan / 过滤条件 / 组件版本 / 召回结果概要 / 时间）；Candidate Fragment 概念字段 fragment_id / source_id / source_version_id / source_scope / product_id / competitor_id / document_or_record_id / record_id / locator / content / retrieval_channels[] / lexical_rank / semantic_rank / fused_rank / rerank_score / matched_terms[] / query_ids[] / availability_status / retrieval_run_id，排名分数只解释为何被召回不是 Fact Confidence / Evidence Strength；各检索通道排名须保留（lexical_rank / semantic_rank / fused_rank / channel_ranks，BM25 与 Vector similarity 不同量纲不得直接相加）；Evidence Package 概念字段 evidence_package_id / task_id / skill_name / purpose / retrieval_plan_version / source_set_version_id / retrieval_run_ids[] / candidate_fragments[] / verified_facts[] / dataset_statistics[] / known_conflicts[] / coverage_summary / evidence_limitations[] / generated_at / package_hash，为 Skill 可复现证据输入快照（不进 Current Truth）；Source Set Version 依赖（Superseded / Deleted 排除，Restricted 权限错误，Processing not complete 不作完整数据集，Source Set 变化旧 Evidence Package 非当前输入）；package_hash 保证可复现；检索组件版本（Embedding 版本 / 索引版本 / Reranker 版本 / Fusion 方法版本）须记录以支持复现；Formal Evidence Link 事务边界（仅 Skill 输出过 Evidence Validator 后创建，Evidence Package = 可复现输入 vs Formal Evidence Link = 正式关系，承接 DEC-024 / DEC-025）；Amends DEC-014，不推翻既有结论）**。**Workflow Runtime 的数据职责（DEC-033：运行时分层运行记录——WorkflowRun（run_id / task_id / thread_id / trigger_type / resumed_from_checkpoint_id / started_at / completed_at / status / current_stage / initiator / cancellation_requested_at / failure_summary / trace_id）、SkillRun（skill_run_id / task_id / run_id / skill_name / skill_contract_version / execution_configuration_version / input_version_ids[] / source_set_version_id / evidence_package_id / input_fingerprint / started_at / completed_at / status / output_version_id / failure_disposition / retry_count）、NodeExecution（node_execution_id / skill_run_id / node_name / node_type / input_fingerprint / started_at / completed_at / status / attempt_count / output_reference / checkpoint_id / error_id / trace_span_id）、ExecutionAttempt（attempt_id / node_execution_id / attempt_number / started_at / completed_at / status / provider_or_component / timeout_deadline / retry_reason / request_reference / response_reference / error_id / usage_metadata）；RuntimeErrorRecord（error_id / task_id / run_id / skill_run_id / node_execution_id / attempt_id / error_code / error_category / severity / retryability / failure_disposition / component / user_safe_message / operator_message / cause_chain[] / input_version_ids[] / provider_error_reference / first_occurred_at / last_occurred_at / remediation_options[]）；Input Fingerprint（task_id / skill_name / input_version_ids / source_set_version_id / skill_contract_version / execution_configuration_version / logical_operation）作为幂等键；Idempotency Record 记录已成功提交操作的幂等结果（重复请求返回首次结果、不重复建业务版本）；RecoveryCase（recovery_case_id / task_id / run_id / failed_skill_run_id / failed_node_execution_id / error_ids[] / last_safe_checkpoint_id / current_business_versions[] / failed_input_versions[] / recommended_actions[] / status / assigned_operator / resolution / audit_history[]）；Cancellation Record 记录取消请求与受影响层；Runtime Audit Record 记录事务提交 / 回滚 / 恢复动作；Trace Correlation IDs（task_id / thread_id / run_id / skill_run_id / node_execution_id / attempt_id / trace_id / retrieval_run_id / evidence_package_id / review_id / source_version_id / model_call_id / tool_call_id）须贯穿日志 / Trace / Metric；Checkpoint Reconciliation Metadata（checkpoint.task_id / checkpoint.thread_id / checkpoint.input_version_ids / current_truth_pointers / stage_validity / review_package_version / checkpoint_status[含 stale]）；概念结构非最终 Schema，运行记录与业务 Domain Object 分离；Amends DEC-023 / DEC-024 / DEC-029，不推翻既有结论）**。**Technical Spike and Architecture Readiness Gate 的数据职责（DEC-034：Spike Graph State 须保持紧凑、引用导向，仅存 task_id / thread_id / current_run_id / current_stage / fact_version_id / insight_version_id / positioning_version_id / review_id / approved_strategy_version_id / marketing_brief_version_id / waiting_reason / last_error_id / cancellation_requested，不存完整业务对象（正式业务内容须从 Business Repository 读取）；Spike 须验证 Domain Version 事务生成与回滚、Current Truth Pointer 原子更新与不变性、Review Package Version 固定上游版本与 stale 拒绝、Runtime Records 可追溯、Checkpoint Metadata 与业务版本对账与 stale 标记、Idempotency Record 防重复 Submit / Commit、RecoveryCase 结构化恢复、Audit Record 记录事务提交 / 回滚 / 恢复；三类 Repository 逻辑分离 Business Repository / Runtime Repository / Checkpoint Store，`LangGraph Checkpoint Store ≠ Business Current Truth Repository`；Mock Business Objects 仅验证架构行为、非最终 Domain Schema；Amends DEC-023 / DEC-033，不推翻既有结论）**。**Technical Spike 临时技术栈与执行契约的数据职责（DEC-035：在 DEC-034 基础上把三类逻辑 Repository 落实为**三类物理分离 SQLite**——`business.sqlite`（Task / Stage State / Domain Versions / Review Package / Strategy Draft / Approved Strategy / Marketing Brief / Formal Evidence Links / Current Truth Pointers / Audit / Idempotency，业务 Current Truth 唯一权威）/ `runtime.sqlite`（Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error / Recovery Case / Cancellation / Runtime Events / Trace Metadata）/ `checkpoints.sqlite`（SqliteSaver 管理 Graph Checkpoint / Thread State / Interrupt / Resume / Pending Writes / Checkpoint Metadata），直接验证 `Business State ≠ Runtime State ≠ Checkpoint State`；**business.sqlite / runtime.sqlite / checkpoints.sqlite 只属于 Spike 实验存储，不构成正式数据库设计**；Atomic Commit Contract——每次正式业务 Commit 在单一事务内完成 Create Domain Version + Formal Evidence Links + Update Current Truth Pointer + Update Stage State + Write Audit + Write Idempotency Record，任一失败整体回滚，Graph Node 不得绕过统一 `BusinessCommitService`；Checkpoint 严格反序列化（`LANGGRAPH_STRICT_MSGPACK=true` 或等价，不存任意 Python 对象 / Secret / 完整业务文档 / 不必要模型输出）；Human Review 节点边界（Review Package 创建与 Interrupt 分离 Node：create_review_package → await_human_review → load_approved_strategy）；所有临时选择不构成生产承诺；Amends DEC-034，不推翻既有结论）**。**未**确认最终数据契约、字段与数据类型、Schema 技术（LangGraph State 使用 TypedDict / dataclass / Pydantic）、数据库、Checkpointer 类型、Reducer、State Version、向量数据库 / 检索实现、存储实现、Source / Fragment ID 格式、Fragment 切分规则、Parser / OCR / Embedding / Web Scraper / Review Importer、最终 Fact Schema、最终 Insight Schema、最终 Positioning Schema、最终 Approved Strategy Schema、Verification Status / Evidence Coverage 枚举名、评论主题分类表、聚类算法、情感分析实现、最低评论数量、频率阈值、候选相似度算法、Positioning 排序公式与维度权重、Xiaohongshu Brief Mapping Adapter 最终 Execution Brief Schema / 字段名、Platform Policy Snapshot 采集与同步、Account and Campaign Context 最终结构、Content Mode 分类表、笔记形式选择规则、Hashtag 方向数量边界、视频镜头信息方向结构、Hybrid Retrieval and Evidence Runtime 的 Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization 与融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / RetrievalPlan / RetrievalRequest / Candidate Fragment / Evidence Package / RetrievalRun 最终 Schema、Workflow Runtime 的 Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue·Worker·DLQ 技术 / Logging·Tracing·Metrics·Alerting Provider / 是否采用 OpenTelemetry / Checkpointer 实现 / 并发模型 / 最终 SLO / 各运行记录最终 Schema / 最终错误代码、Spike 主执行 Agent / Spike 执行时间计划 / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术（生产数据库 / 生产 Checkpointer / ORM / 生产后端语言 / 生产 Retrieval / 生产 Observability / 生产部署平台）。下一议题 Spike-001 Execution Authorization and Agent Handoff Contract（在该议题确认前，不启动 Spike、不安装依赖、不创建 Spike 代码、不运行测试、不创建正式 Roadmap、Development Status 保持 NOT READY）。

---

## 已确认内容（Confirmed）

> 来源：[DEC-012 — Workflow State 采用阶段状态与关键条目结构化设计](../decisions/dec-012-stage-state-and-structured-business-items.md)（Accepted，Architecture，2026-07-27）

- **分开表达（必须独立保存）：** 以下五类数据必须分开、不得互相覆盖：
  - **原始输入**（用户原始商品资料、推广目标、上传来源、可选资料）——不能被模型生成结果覆盖；用户后续修改保留明确更新状态；AI 解析结果与用户原始内容分开保存；
  - **来源资料**（已解析资料、来源、来源片段、提取错误、缺失信息、检测到的冲突）——每个来源须有唯一可追踪的来源标识；
  - **四层业务条目**（事实 / 洞察 / 策略 / 执行 Brief）；
  - **人工审核**（审核评论、用户编辑、接受 / 否定条目、确认的假设、审核时间）；
  - **运行状态**（任务与工作流状态、阶段有效性、失效阶段与原因、运行历史、生成尝试、阶段耗时、错误）。
- **四层结果以结构化条目保存：** 事实 / 洞察 / 策略 / 执行内容**不得**只存为一段不可拆分的自由文本；以结构化条目为基本单位（概念示意：`item_id / content / evidence_type / source_refs / status / generated_by / user_modified` 等）。
- **阶段有效性需要显式保存：** Workflow State 显式记录每个阶段的 valid / invalid、失效原因、重跑起点（如改事实层 → 洞察 / 策略 / 执行 invalid、`rerun_from_stage: insights`）；失效阶段内容不得作为当前有效输出。
- **字段级依赖图不属于 MVP：** MVP 暂不实现精细字段级依赖图或完整知识图谱；关键结论保留主要依据，但局部重跑控制单位仍为阶段（沿用 DEC-009）。
- **当前态与历史态分离：** 区分原始输入 / AI 候选 / 当前有效 / 用户确认 / 已失效 / 历史运行记录；旧结果可留作审计调试，不得与当前有效结果混淆。

> 注：以上为 Workflow State **数据结构与分组原则**；**未**确认是否采用 LangGraph State / Pydantic / JSON Schema、最终字段与数据类型、阶段最终枚举、技术节点数量、数据库存储方式、Checkpoint 实现、跨会话持久化、完整版本历史、来源片段保存方式、状态迁移规则、并发与任务锁、数据隐私与保存期限、开源基底仓库。文中字段名 / 枚举 / Schema 均为**概念示意，非最终数据契约**。

### 任务级持久化范围（DEC-013，Accepted，2026-07-27）

> 来源：[DEC-013](../decisions/dec-013-task-level-persistent-state-and-cross-session-resume.md)

- **需要持久化的内容（至少）：** 任务与阶段状态（task_id / current_stage / workflow_status / review_status / pause_reason / rerun_from_stage / stage_validity）、输入与来源（原始输入 / 推广目标 / 上传引用 / 已解析来源 / 来源片段 / 缺失 / 冲突）、四层业务结果（facts / insights / strategies / execution_brief）、审核与修改（用户修改 / 接受 / 否定条目 / 已确认假设 / 审核意见 / 时间）、运行与评价信息（运行次数 / 阶段耗时 / 失败 / 重跑记录 / 完成时间）。
- **当前有效状态与失效状态必须区分：** 必须区分当前有效状态、当前失效状态、用户修改后状态；旧结果可技术性保留用于调试 / 审计，但**不得**与当前有效结果混淆，恢复时不得把失效重标为有效。
- **完整事件溯源不属于 MVP：** 首版不要求把每次状态变化表达为独立领域事件、不要求事件重放 / 任意历史时刻恢复 / 事件总线 / 完整审计时间线 / 多分支版本合并；可保存必要运行历史与修改记录，但不作为首版前置条件。
- **内存边界：** 内存仅用于节点临时变量 / 请求缓存 / 无业务意义中间结果；人工审核任务、当前有效四层结果、来源证据、阶段有效性、用户修改、重跑位置、任务完成状态**不得**只存内存。

> 注：以上为**持久化范围与原则**；**未**确认 LangGraph Checkpointer / thread_id / PostgreSQL / SQLite / Redis / 关系库 + 对象存储组合 / Checkpoint 频率 / 序列化方式 / 文件持久化 / 任务保留期限 / 删除机制 / 隐私权限 / 并发编辑 / 任务锁 / 版本 UI / 开源基底仓库。

### 分层数据访问（DEC-014，Accepted，2026-07-27）

> 来源：[DEC-014](../decisions/dec-014-on-demand-hybrid-rag-and-layered-data-access.md)

- **结构化业务数据直接读取：** 商品名称 / 品类 / 价格 / 参数 / 推广目标、工作流阶段 / 审核状态 / 阶段有效性 / 用户修改 / 运行状态 / 重跑起点 / 已确认业务字段等，**精确读取结构化字段，不强制向量化**（如读价格不应靠语义相似度检索）。
- **短资料可以全文解析：** 较短、少量、可安全放入上下文的资料直接读取全文 / 结构化解析 / 提取事实候选，不强制走向量检索（短长阈值未定）。
- **长资料和大量评论使用混合检索：** 商品详情页 / 品牌手册 / 访谈 / 调研 / 大量评论 / 历史方案 / 竞品 / 行业报告 / 平台资料 / 运营案例等，用关键词检索 + 语义检索（+ 可选排序），按任务检索相关片段而非全量入 Prompt。
- **任务资料与运营知识逻辑分离：** 任务证据（商品与用户资料实际内容）vs 运营知识（分析方法 / Brief 规范 / 平台规范 / 合规 / 创作指引）逻辑区分；**不得**把运营知识误标为商品事实证据。
- **来源与片段需要唯一标识：** 每个来源 / 来源片段须有唯一可追踪标识（概念：source_id / fragment_id / content / location 等），检索结果写入 Workflow State 并与证据标记（DEC-008）衔接。

> 注：以上为**数据访问分层原则**；**未**确认具体向量数据库 / Embedding 模型 / BM25 实现 / Reranker / Chunking / Top-K / 混合检索权重 / GraphRAG / 供应商文件检索 / 联网搜索 / 知识库更新方式 / 短长资料阈值 / RAG 触发规则 / 最终数据契约 / 开源基底仓库。

### MVP 业务能力与四层数据的对应（DEC-020，Accepted，2026-07-28）

> 来源：[DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](../decisions/dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)

- **四个 Core Skills 对应四层结构化业务条目：** Product Intake & Fact Extraction → Fact 层；Customer Insight Analysis → Insight 层；Product Positioning → Strategy 层；Marketing Brief Generation → Execution 层（承接 DEC-006 四层输出与 DEC-012 结构化条目）。这四层结果仍按 DEC-012 以结构化条目（带 `evidence_type` / `source_refs` / `status` 等）保存，**不**因 Skill 划分而改变数据分组原则。
- **新增平台 Brief 适配层（非核心四层）：** Xiaohongshu Brief Mapping Adapter 将平台无关的 Marketing Brief（Execution 层）映射为小红书场景的结构化执行 Brief；平台 Brief 为独立适配产物，**不**覆盖核心四层业务条目，也**不**重新提取事实 / 洞察 / 定位。
- **共享能力数据职责不变：** Hybrid Retrieval 返回带来源证据片段写入 Workflow State（DEC-014）；Source Management 维护 `source_id` / `fragment_id`；Schema Validation 作为确定性 Validator 校验各 Skill 输入输出结构；Task Persistence / Stage Invalidation / Partial Rerun 维护任务状态与阶段有效性（DEC-012 / 013 / 009）。这些共享能力**不**产生独立业务数据契约。

> 注：本节仅确认 MVP 业务能力与已有四层数据结构的**对应关系**与平台适配层位置；**不**确认任何 Skill 的最终输入输出 Schema、字段与数据类型、平台 Brief 最终字段、Schema 技术、数据库、存储实现。

### 工作流框架对数据架构的要求（DEC-022，Accepted，2026-07-28）

> 来源：[DEC-022 — Workflow Framework Capability Requirements](../decisions/dec-022-workflow-framework-capability-requirements.md)

- **显式结构化任务状态为强制要求：** 工作流框架必须支持显式结构化 Workflow State；概念状态至少包括 `task_id` / `raw_inputs` / `sources` / `fact_stage` / `insight_stage` / `positioning_stage` / `review_stage` / `marketing_brief_stage` / `xiaohongshu_mapping_stage` / `runtime_metadata`（承接 DEC-012 两层状态）。`messages[]` **不能**作为唯一正式业务状态来源。
- **Domain State 应独立于框架存储：** 领域模型（`ProductFact` / `CustomerInsight` / `PositioningCandidate` / `MarketingBrief` / `SourceFragment`）**不应只能**存在于某框架的 Message / Checkpoint / Agent Memory / Runtime Object；目标是更换框架时无需重写全部业务数据模型。
- **持久化不得只依赖进程内存：** 框架可提供 Checkpointer，也可连接项目自己的数据库；任务恢复**不得**以进程内存为唯一基础（承接 DEC-013）。至少持久化原始输入 / 来源 / 事实 / 洞察 / 定位 / Marketing Brief / Platform Mapping / 阶段状态 / 用户修改 / 审核记录 / 当前执行位置 / 错误 / 重试记录 / Skill 版本 / Prompt 版本 / 模型配置 / 运行历史。
- **幂等与并发保护需要数据支撑：** 需要允许实现 Node Run ID / Stage Run ID / 幂等键 / 乐观锁或等效并发控制 / 当前正式版本标记，以避免重复正式结果、多标签页覆盖、相同阶段并行写入、重试生成重复业务条目。

> 注：本节确认工作流框架对数据架构的**要求**（结构化状态 / 领域模型独立于框架 / 持久化范围 / 幂等并发）；**不**确认最终数据契约、字段与数据类型、Schema 技术、具体数据库 / Checkpointer / 存储实现、序列化方式、框架绑定方式（LangGraph / OpenAI Agents SDK / LangChain / CrewAI / Temporal / 自研状态机均未选择）。

### Checkpoint 与业务 Current Truth 数据边界（DEC-023，Accepted，2026-07-28）

> 来源：[DEC-023 — MVP 选择 LangGraph StateGraph 作为核心工作流运行方式](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)

MVP 选择 LangGraph（StateGraph / Graph API）为工作流运行框架后，须明确以下数据边界（承接 DEC-013 / DEC-022）：

- **Checkpoint 与 Business Current Truth 分离：** LangGraph Checkpointer **仅**承载执行恢复、图状态快照、Interrupt 和 Resume；正式业务 Current Truth、来源、用户修改、当前有效版本、审计记录存于业务数据库。**不得**把 LangGraph Checkpoint 数据库作为整个产品唯一的业务数据库。
- **Domain State 不绑定 LangGraph 专属类型：** Domain Model（`ProductFact` / `CustomerInsight` / `PositioningCandidate` / `MarketingBrief` / `XiaohongshuBrief` / `SourceReference` / `ReviewDecision` / `StageStatus` / `Invalidation Rules` / `Domain Errors`）**不应**继承或依赖 LangGraph 专属类型（承接 DEC-022 领域模型独立于框架）。
- **业务数据库是正式业务查询与 Current Truth 的来源：** 正式业务数据查询、当前有效版本、用户修改、审计记录以业务数据库为准；Checkpoint 数据不作为业务查询的权威来源。
- **StateGraph 中的业务数据仍需映射到正式领域模型：** 进入 / 离开 LangGraph 状态的业务数据须经 Node Adapter 映射到正式 Domain Model / Repository（Framework Lock-in Protection：`Node Adapter → 框架无关 Skill Service → Domain Models / Repositories / LLM Gateway`）。
- **Reducer 暂定原则（与 DEC-023 一致）：** 阶段主结果（facts / insights / positioning / brief）默认整体替换 + 显式版本 + 业务 Repository 幂等写入，**不**默认自动 Append；Runtime Events 可 Append-only；用户修改须显式覆盖或新建业务版本，不得因 Reducer 自动追加保留多个「当前有效值」。
- **Interrupt Safety 的数据含义：** Interrupt 前的写入操作须幂等（幂等键），不可逆操作不放在 Interrupt 前；审核拆为 Prepare / Interrupt / Apply 三节点，避免重放产生重复正式结果。

> 注：本节确认 **Checkpoint 与业务 Current Truth 的数据边界**（承接 DEC-023 选定 LangGraph 后的持久化分层）；**仍待确认** Workflow State 最终 Schema、State 技术（TypedDict / dataclass / Pydantic）、Checkpointer 类型、数据库（PostgreSQL / 其他）、数据库 Schema、task_id↔thread_id 映射、Reducer 与 State Version 最终规则、Node Adapter 接口、序列化方式。本节**不**选择 Checkpointer / 数据库 / 存储供应商。

### 四类状态边界与版本化领域状态（DEC-024，Accepted，2026-07-28）

> 来源：[DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)；概念规格：[../specs/workflow/workflow-state-specification.md](../specs/workflow/workflow-state-specification.md)。Amends DEC-012 / DEC-013。

状态架构正式划分为四类，**不得混为一体**：

```text
Authoritative Business State:
Versioned Domain Objects in Business Database

Workflow Execution State:
Compact LangGraph State

Execution Recovery:
LangGraph Checkpointer

User-facing Interaction State:
Derived from Domain, Workflow and Runtime State
```

- **Domain State（业务 Current Truth，权威来源）：** 产品当前认可和管理的业务对象（Product Facts / Customer Insights / Positioning Candidates / Approved Strategy / Marketing Brief / Xiaohongshu Brief / Sources / Source Fragments / Evidence Relationships / Review Decisions / User Modifications / Invalidation Events / Current Truth Version Pointers）；属于产品业务层、不依赖 LangGraph、必须存入正式业务数据库、即使替换工作流框架也必须继续存在。
- **Workflow State（紧凑执行态）：** 工作流判断下一步所需状态（`task_id` / `thread_id` / `task_status` / `current_stage` / 各阶段状态 / 当前业务版本引用 / 输入与来源引用 / Review 引用 / Pause State / 最近错误 / 最早重跑阶段 / Runtime Metadata）；应 `compact / serializable / recoverable / reference-oriented`，**不**应成为业务内容和完整历史的容器。
- **Runtime State（执行恢复态）：** 某次执行信息（`run_id` / 当前节点 / 节点时间 / Checkpoint / 重试次数 / 错误类型 / 模型配置 / Token / 节点耗时 / 进度 / Skill·Prompt·Schema·Validator 版本）；用于故障恢复 / 调试 / 可观测性 / 性能·成本·回归分析。
- **Interaction State（前端派生态）：** 当前前端应展示的交互状态（等待输入 / 等待审核 / 审核包 / 草稿 / 进度 / 允许操作 / 错误恢复选项）；由 Domain + Workflow + Runtime 组合生成，**不**能成为另一套独立业务 Current Truth。
- **版本化 Domain Objects：** 正式业务结果**不得**直接覆盖；首次生成 / 用户修改 / 审核后 / 重跑 / Prompt·模型升级 / 迁移 / 来源更新均创建新版本（`version_id` / `task_id` / `version_number` / `created_by` / `creation_type` / `based_on_version_ids` / `source_refs[]` / `content` / `status` / `created_at`）。
- **Current Truth Version Pointers：** Task 级显式保存当前有效版本指针（`facts_version_id` / `insights_version_id` / `positioning_version_id` / `approved_strategy_version_id` / `marketing_brief_version_id` / `xiaohongshu_brief_version_id`）；**不得**通过字段是否为空推断有效性。
- **四标识符边界：** `task_id`（稳定产品业务 ID，Domain Layer，与 LangGraph 无关，不因 Resume/重跑改变）/ `thread_id`（LangGraph 执行上下文 ID）/ `run_id`（一次调用或恢复）/ `checkpoint_id`（Checkpointer 执行快照，Runtime Layer）；`task_id` 与 `thread_id` **不得**定义为相同概念；MVP 约定一个 `task_id` → 一个当前活跃 `thread_id`。
- **Checkpointer 与 Business Database 职责分离：** Checkpointer 存 Graph State Snapshot / 执行位置 / Interrupt / Resume / State History / Runtime Recovery；Business Database 存 Task / Inputs / Sources / Fragments / 各层 Versions / Review Decisions / Pointers / Invalidation / User Mods / Audit。前端正式业务查询以业务数据库为准。
- **Reference-over-copy：** LangGraph State 优先保存 `facts_version_id` 而非复制 `facts[]`；完整 PDF / 图片二进制 / 评论原文 / Embedding / 向量 / 知识库 / 全部历史版本 / 无限 Message History / 全量模型响应 / 日志存 Business DB / Object Storage / Retrieval Index / Run Log。
- **InvalidationEvent 显式记录：** 失效须保留旧版本 + 标 Stage `invalid` + 更新清除 Pointer + 记原因触发者 + 找最早重跑阶段 + 不删历史 + 不重跑有效上游（承接 DEC-009）。
- **User Modification Model：** 不静默覆盖，保存 `model_generated_content + user_patch + resolved_content`（或语义等价），可回溯模型候选 / 用户修改 / 原因 / 新版本 / 失效下游。

> 注：本节确认**四类状态边界与版本化领域状态**（Amends DEC-012 / DEC-013，不推翻既有结论）；概念 Schema 见 [../specs/workflow/workflow-state-specification.md](../specs/workflow/workflow-state-specification.md)（仅概念，非最终实现）。**仍待确认** 最终字段名称、最终 Python Schema、TypedDict / dataclass / Pydantic、数据库（PostgreSQL / MongoDB / 其他）、Checkpointer 类型、数据库表结构、`task_id` / `thread_id` / Version ID 生成格式、State Reducer、Snapshot 与 Patch 策略、Review Payload、数据保留周期、是否支持业务历史 Fork、并发控制、事务边界、Technical Spike 代码。本节**不**创建最终数据库 Schema / Migration / LangGraph State Python 代码 / Pydantic / TypedDict / Reducer / Checkpointer / API，**不**选择 PostgreSQL / MongoDB / Redis / SQLite / Checkpointer / Object Storage / 向量数据库 / ORM。

### 版本化来源、可定位 Fragment 与显式 Evidence Link（DEC-025，Accepted，2026-07-28）

> 来源：[DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](../decisions/dec-025-versioned-sources-fragments-and-evidence-links.md)；概念规格：[../specs/evidence/source-and-evidence-specification.md](../specs/evidence/source-and-evidence-specification.md)。Amends DEC-008 / DEC-014。

来源与证据系统正式采用分层链路：

```text
Source
→ Source Version
→ Document / Record
→ Fragment
→ Evidence Link
→ Versioned Domain Object
```

- **Source 是逻辑身份，不是内容快照：** Source（信息来源的逻辑身份，含 `source_id` / `task_id` / `source_type` / `source_scope` / `ownership` / `status` / `current_version_id` 等）覆盖用户手动输入 / 上传文档与表格 / 当前商品页面与评论 / 竞品页面与评论 / 访谈 / 问卷 / 内部业务文档 / 平台规则 / 公开网页 / 确定性系统统计。业务结果必须引用具体 `source_version_id`，**不能**只引用可能持续变化的 `source_id`。
- **Document / Record 区分载体：** Document 适用于长文本 / 文件类（PDF / Word / 网页快照 / 商品说明书 / 检测报告）；Record 适用于独立可计数结构化 · 半结构化数据（单条评论 / 单条访谈 / 问卷回答 / 商品参数 / 竞品 SKU / 用户手动输入字段）。评论、问卷、结构化数据**不得**为方便全部拼接成不可计数的巨大文档。
- **Fragment 必须可回到原文：** Fragment 是可精确定位、检索、展示的最小原始内容单元（含 `fragment_id` / `source_id` / `source_version_id` / `document_id_or_record_id` / `content` / `locator` / `content_hash` / `status` 等）；Locator 按来源类型表达（PDF 页 / Web URL+heading / Review 行号 / Sheet 行列 / Manual 字段 / Interview speaker 等），最终 Locator Schema 未确认但必须满足可追溯与可返回原文。
- **Evidence Link 是独立关系对象、非文本副本：** `EvidenceLink`（`evidence_link_id` / `target_entity_type` / `target_entity_id` / `target_version_id` / `fragment_id` / `evidence_role` / `support_strength` / `validator_status` 等）是 Fragment 与业务结论之间**经过验证**的关系；Target Entity Types 含 fact / insight / positioning_candidate / selling_point / proof_point / brief_item / risk_warning 等；Evidence Role 显式（supports / contradicts / qualifies / provides_context / example_only）。
- **延续五类 Evidence Class（DEC-008）：** Explicit Fact（须直接 Source Fragment，模型不得生成无来源 Fact）/ Evidence-backed Insight（可基于事实 / 评论 / 访谈 / 问卷 / 统计 / 竞品评论，须说明样本限制）/ Model Inference（标记为推断，不得成无条件 Proof Point）/ Hypothesis to Validate（标记待验证，不得作确定性承诺）/ Insufficient Information（不猜测填补，触发补充或暂停）。
- **Retrieved Fragment ≠ Formal Evidence：** RAG 召回结果初始仅为 `Retrieved Fragment` / `Candidate Evidence`；须经 Permission / Source Version / Existence / Relevance 校验 + 确定性 Validator + 创建正式 Evidence Link 后才成正式证据（9 条条件）。
- **防止虚构来源引用：** 模型**不得**自由生成 `source_id` / `source_version_id` / `fragment_id` / 文件名 / 页码 / 评论 ID / URL / 引用位置；系统提供候选 Fragment 集合，模型只能从允许集合选择，经 Validator 校验后才写入 Evidence Link；**禁止**只存自然语言引用而无真实 Fragment ID 与 Locator。
- **Source Set Version + Evidence Package：** SourceSetVersion 固定某次分析参与的具体 Source Version 集合（不复制内容，Insights Version 记 `based_on_source_set_version_id`）；EvidencePackage 是 Skill 可复现输入快照（`candidate_fragments[]` / `verified_facts[]` / `dataset_statistics[]` / `known_conflicts[]` / `evidence_limitations[]`），限制模型可见证据范围，Skill 输出 Fragment ID 必须来自该 Package 允许集合。
- **Source Version Status + Source Conflict：** Source Version 状态枚举 7 值（available / processing / invalid / unavailable / superseded / deleted / restricted）；来源冲突结构化为 `SourceConflict`（关键事实冲突 → Fact Stage waiting_input / paused，系统不得由模型自选值写成事实）。
- **频率统计须完整可计数数据：** 正式比例 / 频率 / 覆盖率须基于完整、可计数数据集（完整可访问 / 明确样本量 / 去重规则明确 / 统计可复现 / 分母分子可验证 / 有 Dataset Statistic 记录）；**禁止**以 RAG Top-K 召回结果推断总体频率；区分 `Dataset-derived Statistic`（可作正式频率）与 `Retrieved Evidence Sample`（仅证明现象存在）。
- **当前商品与竞品隔离：** `source_scope` 区分 current_product / competitor_product / platform_knowledge / internal_business；竞品资料**不能**直接证明当前商品事实——当前商品事实必须由当前商品自己的来源支持。
- **来源失效可追溯：** 来源失效按 Evidence Link 判断受影响对象（关键 Fact 主来源失效 → Fact Stage 及下游失效；Insight 主证据来源失效 → Insight Stage 及下游失效；仅 Context / Example 来源失效 → 记 Warning 由 Validator 决定）；失效处理含更新状态 / 查依赖 Evidence Links / 创建 Invalidation Event / 标阶段失效 / 清 Pointer / 保留历史 / 从最早失效阶段重跑（承接 DEC-009 / DEC-024）。
- **权威边界：** Raw Information Current Truth = Source Version + Document / Record + Fragment；Business Conclusion Current Truth = Versioned Domain Object + Current Truth Pointer（DEC-024）；二者关系 = Evidence Link；临时检索 = Retrieved Candidate Fragment（非正式 Current Truth）。

> 注：本节确认**来源与证据分层架构**（Amends DEC-008 / DEC-014，不推翻既有结论）；概念 Schema 见 [../specs/evidence/source-and-evidence-specification.md](../specs/evidence/source-and-evidence-specification.md)（仅概念，非最终实现）。**仍待确认** 最终数据库字段、Source ID / Fragment ID 格式、Fragment 切分规则、Chunk Size / Overlap、Parser、OCR、Embedding 模型、全文检索、向量数据库、Top-K、Reranker、Evidence Strength 评分、网页抓取方案、评论导入格式、Source Retention、删除策略、官方平台知识来源、前端 Evidence UI、最终 API。本节**不**创建最终数据库表 / Parser 代码 / OCR / RAG 代码 / Embedding / Vector Store / Web Scraper / Review Importer / Evidence UI / 正式 API，**不**选择 PostgreSQL / MongoDB / Elasticsearch / pgvector / Pinecone / Weaviate / Chroma / Embedding 模型 / Reranker / PDF Parser / OCR Provider。

### 首个核心 Skill Contract 的 Fact 数据职责（DEC-026，Accepted，2026-07-28）

> 来源：[DEC-026 — Product Intake & Fact Extraction Skill 采用分层输入完整度、零无来源事实与冲突暂停契约](../decisions/dec-026-product-intake-and-fact-extraction-skill-contract.md)；概念 Skill Spec：[../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)。Amends DEC-005。

承接 DEC-012（结构化条目）、DEC-020（Fact 层 = Product Intake & Fact Extraction Skill）、DEC-024（Facts Version 为版本化 Domain Object）、DEC-025（Fact 须经 Evidence Link 关联 Fragment），DEC-026 进一步确认 Fact Layer 的数据职责：

- **Fact `raw_value` 与 `normalized_value` 分离：** 每个事实候选概念上同时保存 `raw_value`（原文值）与 `normalized_value`（安全语义等价标准化后的值）+ `unit`；允许 `0.5 L / 500 ml / 500 毫升 → normalized_value = 500, unit = mL`，但**必须**保留 `raw_value`；`raw_value` 与原文一致由 Validator 校验。语义不同的表达（约 / 最大 / 推荐 / 实际容量）**不得**未经确认自动合并。
- **Fact Assertion Type 五分类：** 来源表达须区分 `direct_fact`（来源直接明确）/ `documented_claim`（来源明确提出但无充分证明）/ `certified_or_tested_fact`（有有效检测报告 / 认证支持，不得扩张报告结论）/ `marketing_expression`（营销性主观，**不**进 Facts Current Truth）/ `unknown_or_ambiguous`（含义不明）。
- **Fact Verification Status（可解释、非模型数字 Confidence）：** MVP **不**使用模型主观通用数字置信度（如 `0.87`），改用可解释验证状态（概念：`user_provided` / `single_source_direct` / `multi_source_corroborated` / `documented_claim` / `verified_by_test_or_certificate` / `conflicting` / `insufficient`，最终名称未确认）；必须表达「为什么可信或为什么不确定」。
- **Facts Version 为版本化 Domain Object：** Fact 候选写入正式 `Facts Version`（承接 DEC-024 版本化 Domain Objects + Current Truth Pointer）；正式业务结果不得直接覆盖，须创建新版本；写入前须经确定性 Validator 15 项硬校验，硬校验失败**不得**写入 Facts Current Truth。
- **当前商品 Source Scope 为正式 Fact 的必要条件：** 正式 Fact **必须**关联 `source_scope = current_product` 范围内真实、有效、可定位的 Fragment（承接 DEC-025 当前商品与竞品隔离）；竞品来源**不能**证明当前商品事实；用户手动输入（`manual_input`）可作为合法直接来源。Hard Rule：**No Fact without a valid current-product Fragment。**
- **冲突与 Evidence Link：** Numeric / Material / SKU or Variant / Certification / Usage Restriction 冲突**不得**由模型自行解决；关键冲突创建正式 `SourceConflict`（承接 DEC-025）并经 Evidence Link 关联 `supporting_fragment_ids[]` / `contradicting_fragment_ids[]`，触发 `waiting_input` / `paused` 交用户；MVP **不**建立复杂来源优先级；冲突值**不得**同时成为 Current Truth。
- **Documented Claim 不等于 Verified Fact：** 只有营销页面而无检测 / 认证资料的声明只能归 `documented_claim` 并写入 `claims_to_verify[]`，**不得**标记为 `certified_or_tested_fact`；Marketing Expression 可存为原始营销素材但**不得**进入正式 Facts Current Truth。

> 注：本节确认**首个核心 Skill Contract 对 Fact 数据职责的影响**（raw/normalized 分离 + Assertion 五分类 + 可解释 Verification Status + Facts Version + current_product Source Scope + 冲突经 SourceConflict/Evidence Link + Documented Claim≠Verified Fact；承接 DEC-005/008/009/012/020/024/025）；详细 Skill 契约见 [../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)（仅概念）。**仍待确认** 最终 Fact Schema、字段名、Python 类型、Verification Status 枚举名、Fact Categories 最终分类名、单位库、数据库表。本节**不**创建最终数据库表 / Prompt / Skill 代码 / 单位库 / 前端表单，**不**选择数据库 / ORM / 模型 / 单位处理库。

### 第二个核心 Skill Contract 的 Insight 数据职责（DEC-027，Accepted，2026-07-28）

> 来源：[DEC-027 — Customer Insight Analysis Skill 采用证据模式与降级假设模式，并禁止虚构用户原声和检索样本频率外推](../decisions/dec-027-customer-insight-analysis-skill-contract.md)；概念 Skill Spec：[../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)。Amends DEC-017。

承接 DEC-008（五类 Evidence Class）、DEC-020（Insight 层 = Customer Insight Analysis Skill）、DEC-024（Insights Version 为版本化 Domain Object + Current Truth Pointer）、DEC-025（Evidence Link + Evidence Package + Source Scope 隔离）、DEC-026（上游 Facts Version），DEC-027 进一步确认 Insight Layer 的数据职责：

- **Theme 与 Insight 分离：** `Theme`（用户反馈中反复出现的讨论主题，只回答「用户在讨论什么？」）本身**不**自动构成业务洞察；`Insight` 至少须表达「谁 + 在什么场景 + 遇到什么问题或需求 + 为什么重要 + 如何影响使用 / 购买 / 信任」。「用户提到了漏水」不得直接包装成完整 Insight。Themes 与 Insights 作为不同结构化对象分别保存。
- **Insight Evidence Coverage（可解释、非模型百分制 Confidence）：** Insight 须记录可解释的 `evidence_coverage` 状态——`none` / `anecdotal` / `repeated_signal` / `dataset_supported` / `multi_source_corroborated`（最终名称未确认）；`anecdotal` 只能表达为 Observed / Anecdotal Signal，**不**得表达为稳定模式或普遍共识；MVP **不**使用模型主观百分制 Confidence。
- **用户原声必须关联真实 Fragment：** 直接用户原声（Customer Language）**必须**来自真实 Fragment（可追踪 Fragment ID / Source / Source Version / Review·Interview·Survey Record / Locator / 上下文）；**禁止**模型自己写一句话加引号、多条评论拼接成虚构原声、修改原文后声称直接引用、把模型概括伪装原文、把竞品评论展示为当前商品用户原声、把翻译文本伪装原语言直接引用；`Original Customer Language` 与 `Model Summary` 必须分别展示。
- **Dataset Statistic 与 Retrieved Fragment 分离：** 正式比例 / 频率**必须**由确定性统计产生（须记录数据集版本 / 评论总数 / 去重规则 / 分子记录 ID / 分母 / 主题分类规则版本 / 统计时间 / 统计方法），作为独立 `Dataset Statistic` 对象；`Retrieved Fragment`（RAG Top-K 召回）只能作为相关证据示例，**不得**用作总体频率统计（承接 DEC-025：区分 Dataset-derived Statistic 与 Retrieved Evidence Sample；禁止 Top-K 频率外推）。
- **当前商品和竞品用户证据分离：** Insight 须显式记录 `source_scope`；竞品用户反馈（`competitor_product`）可支持品类共性问题 / 用户期待 / 竞品弱点 / 差异化机会假设，但**不能**直接证明当前商品（`current_product`）用户具有同样体验；竞品 Fragment 不得归因为当前商品用户证据（承接 DEC-025 Source Scope 隔离）。
- **Insights Version 为版本化 Domain Object：** Insight 候选写入正式 `Insights Version`（承接 DEC-024 版本化 Domain Objects + Current Truth Pointer `insights_version_id`）；正式业务结果不得直接覆盖，须创建新版本；写入前须经确定性 Validator 18 项硬校验，硬校验失败**不得**写入 Insights Current Truth；下游 Product Positioning 以 Insights Version 为输入。
- **Hypothesis 与 Evidence-backed Insight 分离：** Evidence-backed Insight（有真实用户 Fragment）与 Hypothesis to Validate（无足够直接用户证据，基于商品事实 / 场景 / 品类 / 竞品 / 用户提供目标人群生成）作为不同结构化对象分别保存（`insights[]` vs `hypotheses_to_validate[]`）；Hypothesis 必须明确标记「当前没有直接用户证据·待验证假设」，**不得**表示为真实用户共识；运行于 Degraded Hypothesis Mode 时阶段为 `valid_with_limitations`，Product Positioning Skill 必须能读取并展示这些限制。

> 注：本节确认**第二个核心 Skill Contract 对 Insight 数据职责的影响**（Theme/Insight 分离 + Evidence Coverage 5 状态 + 用户原声关联真实 Fragment + Dataset Statistic 与 Retrieved Fragment 分离 + 当前商品与竞品用户证据分离 + Insights Version + Hypothesis 与 Evidence-backed Insight 分离；承接 DEC-008/009/014/015/017/020/024/025/026）；详细 Skill 契约见 [../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)（仅概念）。**仍待确认** 最终 Insight Schema、字段名、Insight Types 最终名称、Evidence Coverage 枚举名、评论主题分类表、聚类算法、情感分析实现、Dataset Statistic 记录格式、Customer Language Locator Schema、数据库表。本节**不**创建最终数据库表 / 评论分析 Prompt / Skill 代码 / 聚类代码 / Embedding / 评论导入器 / 情感分析实现，**不**选择模型 / Embedding / 聚类算法 / 情感分析工具 / 数据库 / 评论文件格式 / 最低评论数量 / 频率阈值。

### 第三个核心 Skill Contract 的 Positioning 数据职责（DEC-028，Accepted，2026-07-28）

> 来源：[DEC-028 — Product Positioning Skill 采用多候选、证据约束与强制人工决策契约](../decisions/dec-028-product-positioning-skill-contract.md)；概念 Skill Spec：[../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)。Amends DEC-018。

承接 DEC-008（五类 Evidence Class）、DEC-020（Positioning 层 = Product Positioning Skill）、DEC-024（版本化 Domain Objects + Current Truth Pointer）、DEC-025（Evidence Link + Evidence Package + Source Scope 隔离）、DEC-026（上游 Facts Version）、DEC-027（上游 Insights Version），DEC-028 进一步确认 Positioning Layer 的数据职责：

- **PositioningCandidate 概念对象：** 每个定位候选作为独立概念对象（candidate_id / candidate_title / target_segment / usage_context / job_or_core_need / category_frame / value_proposition / key_benefits[] / differentiation / reasons_to_believe[] / proof_points[] / based_on_fact_ids[] / based_on_insight_ids[] / competitor_evidence_ids[] / assumptions[] / evidence_limitations[] / strategic_risks[] / evidence_profile / ranking_rationale / review_status，最终 Schema 未确认，**非**最终数据库表）；`based_on_fact_ids[]` / `based_on_insight_ids[]` / `competitor_evidence_ids[]` 必须经 Evidence Link 关联真实版本化对象（承接 DEC-025）。
- **Candidate Version（版本化 Domain Object）：** 定位候选写入正式版本化对象，承接 DEC-024（业务结果不得直接覆盖，须创建新版本）；默认生成 3 个、允许 2–4 个，候选之间必须具有**实质差异**（不得仅为同一句定位的语言改写）。
- **Approved Strategy Version：** 经 Human Review（select / edit / merge[须重新通过 Validator] / reject / request_more_information）形成的 **Approved Strategy Version** 是独立版本化 Domain Object，是下游 Marketing Brief Generation 的必要输入；只有 Approved Strategy Version 才能进入 Marketing Brief，未经审核的候选**不**直接生成 Brief。
- **Positioning 属 Strategic Inference 非 Explicit Fact：** Positioning 是在 Facts + Insights + 竞品证据 + 业务约束之上的战略推断；推导链 `Valid Facts + Valid/Limited Insights + Competitor Evidence + Business Constraints → Positioning Candidates → Human Review → Approved Strategy Version`；系统**不得**将定位候选描述为来源直接表达的事实、已证明的市场结论、唯一正确答案或用户已确认真实需求。
- **Target Segment Hypothesis：** 缺乏直接用户证据时 Target Segment 须标记为 `Target Segment Hypothesis`；**不得**凭空生成过于精确的人口统计特征（精确年龄 / 收入 / 城市等级 / 性别 / 职业 / 家庭结构），除非来源明确支持。
- **Opportunity Hypothesis：** 竞品资料有限时的市场机会只能表达为 `Opportunity Hypothesis`（「易清洗可能是值得验证的差异化方向」），**不得**表示为已验证市场空白或确定性竞品优势。
- **Proof Point 与 Fact 的关系：** Proof Point 是后续 Marketing Brief 可直接使用的证明材料，链路必须成立 `Proof Point → Valid Fact → Evidence Link → Fragment → Source Version`；Fact 失效时 Proof Point 同步失效（承接 DEC-026）；竞品证据**不能**证明当前商品能力，竞品功能**不得**写入当前商品 Proof Point；无 Source Version 的证明材料**不得**进入候选。
- **Positioning 与 Evidence Limitations：** 当上游 Insights Version 为 `valid_with_limitations` 时，Positioning Skill **不**绕过上游限制，而把 Evidence Limitations 传播到每个候选并显式标注（Limited Evidence Mode）；不得使用「用户普遍」「用户最关心」等表述，重要需求须标记为待验证，要求 Human Review 明确接受相关假设。
- **Positioning Recommendation 不等于 Current Truth：** 模型可输出推荐候选 + 推荐理由 + 主要风险 + 成功条件 + 需验证假设，但 Recommendation 只是建议，**不**自动成为 Approved Strategy，也**不**等于已确认业务事实；MVP **不**使用模型生成的不透明综合数字分数（如 `positioning_score = 91`），改用可解释 7 维排序（product_truth_fit / customer_relevance / evidence_support / differentiation_credibility / strategic_clarity / execution_potential / risk_level）。

> 注：本节确认**第三个核心 Skill Contract 对 Positioning 数据职责的影响**（PositioningCandidate 概念对象 + Candidate Version + Approved Strategy Version + Positioning 属 Strategic Inference + Target Segment Hypothesis + Opportunity Hypothesis + Proof Point 与 Fact 的关系 + Positioning 与 Evidence Limitations + Positioning Recommendation 不等于 Current Truth；承接 DEC-008/009/015/018/020/024/025/026/027）；详细 Skill 契约见 [../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)（仅概念）。**仍待确认** 最终 Positioning Schema、Approved Strategy Schema、字段名、Comparison Matrix 最终字段、候选相似度算法、排序公式与维度权重、竞品数量、Human Review Payload、数据库表。本节**不**创建最终数据库表 / Positioning Prompt / Skill 代码 / LangGraph Node / Human Review 页面 / 候选相似度算法 / 排序算法 / 市场研究代码，**不**选择模型 / Prompt Framework / 竞品数量 / 排序公式 / Human Review UI 技术 / 数据库 / 高风险比较声明规则实现。

### Human Review 与 Approved Strategy 的数据职责（DEC-029，Accepted，2026-07-28）

> 来源：[DEC-029 — Human Review 采用版本化审核包、结构化用户决策与事务化 Approved Strategy 契约](../decisions/dec-029-human-review-and-approved-strategy-contract.md)；概念规格：[../specs/workflow/human-review-and-approved-strategy-contract.md](../specs/workflow/human-review-and-approved-strategy-contract.md)。Amends DEC-007 / DEC-024。

承接 DEC-007（单审核 Gate）、DEC-009（阶段失效）、DEC-012（结构化条目）、DEC-020（Human Review Gate 位于 Positioning 与 Marketing Brief 之间）、DEC-023 / DEC-024（版本化 Domain Objects + Current Truth Pointer + Checkpointer 与业务库分离）、DEC-025（Proof Point → Fact → Evidence Link → Fragment → Source Version）、DEC-028（上游 Positioning Candidates），DEC-029 进一步确认 Human Review 与 Approved Strategy 的数据职责：

- **Review Package Version（固定上游版本输入快照）：** Review Package 为某次审核使用的固定输入快照（概念字段：`review_id` / `task_id` / `package_version` / `facts_version_id` / `insights_version_id` / `positioning_version_id` / `source_set_version_ids[]` / `positioning_candidates[]` / `critical_facts[]` / `critical_insights[]` / `hypotheses[]` / `evidence_limitations[]` / `source_conflicts[]` / `strategic_risks[]` / `model_recommendation` / `created_at` / `status`，最终 Schema 未确认，非最终数据库表）；必须固定审核时的 Facts / Insights / Positioning / Source Set Versions / Candidates / Evidence Limitations；审核开始后**不得**后台静默替换。
- **Review Package Version Validity：** 若 `facts_version_id` / `insights_version_id` / `positioning_version_id` / `relevant_source_set_version_id` 任一变化 → 原 Review Package 标 `superseded`，旧提交被阻止，创建新 Package，不自动迁移旧审核选择。
- **Strategy Draft Version（临时工作内容，不属 Current Truth）：** 概念字段 `draft_id` / `review_id` / `draft_version` / `based_on_candidate_ids[]` / `selected_content` / `user_edits[]` / `merge_sources[]` / `hypothesis_decisions[]` / `proof_point_decisions[]` / `user_notes` / `updated_at` / `status`；可多次修改、可自动保存、须记版本；**不属于**业务 Current Truth、**不允许**下游使用、**不允许** Marketing Brief 读取；提交前必须通过 Validator。
- **Review Decisions（结构化用户决策）：** 含 Hypothesis Decisions（5 动作 accept_for_execution / accept_for_testing / edit / reject / request_evidence）、Proof Point Decisions（accept / remove / rephrase / downgrade_to_reason_to_believe / request_evidence）、Evidence Limitation Acceptance（`accepted_by_user = true` 但**不得**删除客观限制）；编辑保留 `model_generated_content + user_patch + resolved_content`（承接 DEC-024 不静默覆盖）。
- **Approved Strategy Version（正式版本化 Domain Object）：** 用户明确 submit 并通过事务校验后生成（承接 DEC-024）；概念字段 `approved_strategy_version_id` / `task_id` / `based_on_review_id` / `based_on_review_package_version` / `based_on_positioning_version_id` / `selected_candidate_ids[]` / 全部 Positioning Elements / `accepted_hypotheses[]` / `rejected_hypotheses[]` / `evidence_limitations[]` / `strategic_risks[]` / `user_notes` / `approved_by` / `approved_at` / `version_status`（最终 Schema 未确认）；是 Marketing Brief Generation **唯一**正式战略输入。
- **Current Truth Pointer：** `approved_strategy_version_id`（承接 DEC-024 Current Truth Version Pointers）；由 submit 事务**原子更新**（事务任一步失败不更新 Pointer）。
- **Hypothesis Decision：** 接受 Hypothesis **不等于** `Hypothesis → Fact`；`accept_for_execution` 须保留 `evidence_class = hypothesis_to_validate`，`accept_for_testing` 须标 `requires_validation = true`；不得转化为确定性承诺或 Proof Point。
- **Evidence Limitation Acceptance：** Evidence Limitations 必须**继续保存**在 Approved Strategy 中；用户可 `accepted_by_user = true` 但**不能**删除客观限制；Marketing Brief Skill 须读取并继续传播。
- **Proof Point Decision：** Proof Point 须展示完整追溯 `Proof Point → Fact → Evidence Link → Fragment → Source Version`；用户改写后须校验仍被原 Fact 支持；无证据内容（如「市场上最轻」无市场比较证据）**不得**升级为 Proof Point，只能存为 Business Assumption / Positioning Hypothesis。
- **Review Audit History：** 保留原始 Candidates / Model Recommendation / 用户选择 / 编辑 / Merge 来源 / 拒绝 / Hypothesis·Proof Point·Evidence Limitation Decisions / 补料请求 / Draft 版本 / 提交 / Approved Strategy 版本 / 撤回 / 时间戳 / 用户备注 / 失败校验记录。
- **Withdrawal Record：** 撤回创建 Withdrawal Record，保留原 Approved Strategy 标 `withdrawn` / `superseded`，清除当前 Pointer，使 Marketing Brief + Xiaohongshu Mapping 失效（承接 DEC-009），保留旧 Brief / Mapping 历史，创建新 Review Cycle。

> 注：本节确认**Human Review 与 Approved Strategy 的数据职责**（Review Package Version + Strategy Draft Version + Review Decisions + Approved Strategy Version + Current Truth Pointer + Hypothesis Decision + Evidence Limitation Acceptance + Proof Point Decision + Review Audit History + Withdrawal Record；承接 DEC-007/009/012/020/023/024/025/028，Amends DEC-007 / DEC-024 不推翻既有结论）；概念规格见 [../specs/workflow/human-review-and-approved-strategy-contract.md](../specs/workflow/human-review-and-approved-strategy-contract.md)（仅概念）。**仍待确认** 最终 Review Schema、最终 Approved Strategy Schema、Strategy Draft 最终 Schema、字段名、Review Status 最终枚举名、Hypothesis / Proof Point / Evidence Limitation Decision 最终字段、Audit Record / Withdrawal Record 最终 Schema、并发锁实现、数据库事务实现、数据库表。本节**不**创建最终数据库表 / Review UI / LangGraph Interrupt 代码 / Resume 代码 / Transaction 代码 / Draft 自动保存代码 / Approved Strategy Service 代码，**不**选择数据库 / 并发控制技术 / Draft 存储方案 / 权限系统 / 多人审批系统。

---

### Marketing Brief Generation Skill 的数据职责（DEC-030，Accepted，2026-07-28）

> 来源：[DEC-030 — Marketing Brief Generation 采用 Approved Strategy 锁定、平台无关信息架构与证据限制传播契约](../decisions/dec-030-marketing-brief-generation-skill-contract.md)（Skill Contract / Marketing Architecture；Amends DEC-006 + DEC-019）。

- **Marketing Brief Version（版本化 Domain Object）：** `brief_id` / `brief_version_id` / `approved_strategy_version_id` / `facts_version_id` / `insights_version_id` / `communication_objective` / `audience` / `audience_context` / `core_message` / `message_hierarchy` / `benefit_hierarchy` / `key_benefits[]` / `reasons_to_believe[]` / `proof_points[]` / `objections[]` / `objection_responses[]` / `content_angles[]` / `tone_and_voice` / `call_to_action_objective` / `mandatory_messages[]` / `prohibited_claims[]` / `accepted_hypotheses[]` / `hypotheses_to_test[]` / `evidence_limitations[]` / `risk_notes[]` / `platform_adaptation_rules` / `workflow_decision`（概念字段，非最终 Schema；承接 DEC-024）。
- **Approved Strategy Dependency：** Authoritative Input 仅 `approved_strategy_version_id`；不得用未审核 Candidate / Strategy Draft / Model Recommendation / 已撤回或失效 Approved Strategy / 历史旧版本 Strategy；Facts / Insights Version 须当前有效（承接 DEC-029）。
- **Message Hierarchy：** 三级 Primary Message → Secondary Benefits → Supporting Proof；转换链 Fact → Product Capability → User Benefit → Core Message，不得跳过中间逻辑。
- **Benefit Hierarchy：** `primary_benefit` / `secondary_benefit` / `supporting_feature`；MVP 默认 1 Primary + 2–4 Secondary，资料不足不得凑数。
- **Proof Point References：** `proof_point` / `fact_id` / `supporting_fragment_ids[]` / `source_version_id` / `approved_wording`；须建立 Proof Point → Valid Fact → Evidence Link → Fragment → Source Version 追溯链，不得扩大检测认证性能范围（承接 DEC-025 / DEC-028 / DEC-029）。
- **Content Angles：** `angle_title` / `user_tension` / `message_focus` / `supporting_benefits[]` / `proof_points[]` / `hypothesis_status` / `risk_notes[]`；3–5 个，须实质差异。
- **Mandatory Messages 与 Prohibited Claims：** Mandatory Messages（Approved Core Positioning / Primary Benefit / 关键 Proof Points / 使用限制 / 免责 / 品牌要求）+ Prohibited Claims（无依据最高级 / 无来源数值 / 未验证认证 / 超检测范围 / 竞品误归因 / Hypothesis 表达为共识 / Marketing Expression 表达为 Fact / 医疗健康安全功效 / 无比较绝对优势）；两者须传给所有 Platform Adapters。
- **Hypotheses：** `accepted_hypotheses[]` / `hypotheses_to_test[]`；接受 Hypothesis ≠ Hypothesis→Fact，须保留 evidence_class / requires_validation（承接 DEC-029）。
- **Evidence Limitations：** `evidence_limitations[]`；不得在 Brief 生成中删除或弱化，用户 accepted_by_user 不等于客观限制消失（承接 DEC-029 硬规则）。
- **Brief Current Truth Pointer：** `brief_version_id`（承接 DEC-024）；用户编辑 → 新 Brief Version + 保留原模型版本 + 记录用户修改 + 重跑 Validator + 更新 Pointer；承接 DEC-009：Brief 修改不使 Facts / Insights / Positioning / Approved Strategy 失效，但使 Xiaohongshu Mapping 失效。

> 注：本节确认**Marketing Brief Generation Skill 的数据职责**（Marketing Brief Version + Approved Strategy Dependency + Message Hierarchy + Benefit Hierarchy + Proof Point References + Content Angles + Mandatory Messages / Prohibited Claims + Hypotheses + Evidence Limitations + Brief Current Truth Pointer；承接 DEC-006/009/015/019/020/024/025/028/029，Amends DEC-006 / DEC-019 不推翻既有结论）；概念 Skill Spec 见 [../specs/skills/marketing-brief-generation-skill.md](../specs/skills/marketing-brief-generation-skill.md)（仅概念）。**仍待确认** 最终 Marketing Brief Schema、字段名、Content Angle 分类表、Tone 模板、Brand Guidelines 格式、风险词库、CTA 分类、approved_wording 改写边界、数据库表。本节**不**创建最终数据库表 / 正式 Brief Prompt / Skill 代码 / LangGraph Node / Brief UI / Risk Validator 实现 / Brand Guideline Parser / 平台内容生成器，**不**选择模型 / Prompt Framework / Tone 模板 / 风险词库 / CTA 分类 / 前端框架 / 数据库。

### Xiaohongshu Brief Mapping Adapter 的数据职责（DEC-031，Accepted，2026-07-29）

> 来源：[DEC-031 — Xiaohongshu Brief Mapping Adapter 采用 Brief 锁定、版本化平台政策快照、真实体验边界与方向化输出契约](../decisions/dec-031-xiaohongshu-brief-mapping-adapter-contract.md)（Platform Adapter Contract / Platform Architecture；Amends DEC-004 + DEC-020）。概念 Platform Adapter Spec 见 [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)。

- **Xiaohongshu Execution Brief Version（版本化 Domain Object）：** `execution_brief_id` / `execution_brief_version_id` / `marketing_brief_version_id` / `approved_strategy_version_id` / `facts_version_id` / `platform_policy_snapshot_id` / `account_context` / `campaign_context` / `commercial_context` / `note_strategy` / `content_architecture` / `discovery_and_interaction` / `evidence_and_guardrails` / `workflow_decision`（概念字段，非最终 Schema；承接 DEC-024）。Authoritative Input 仅 `marketing_brief_version_id`（并引用 approved_strategy_version_id / facts_version_id / platform_policy_snapshot_id；不得用未审核 Positioning Candidate / Strategy Draft / 未审核 Brief 草稿或旧版本）。
- **Platform Policy Snapshot：** 外部、随时间变化的版本化来源 `platform` / `policy_snapshot_id` / `policy_version` / `captured_at` / `applicable_content_type` / `applicable_industries[]` / `rule_source_version_ids[]` / `prohibited_patterns[]` / `disclosure_requirements[]` / `qualification_requirements[]` / `review_route_rules[]` / `availability_status`；每次执行必须记录所用 `policy_snapshot_id` / `policy_version`；Snapshot 失效或不可用返回 `platform_policy_update_required`，不得 Prompt 硬编码长期有效规则（承接 DEC-025 时间敏感来源）。
- **Account Context：** `account_type`；不得隐藏商业性质、不得以素人身份掩盖付费或品牌 Owned 内容。
- **Commercial Context：** 基于 account 与 campaign 上下文输出 `review_route_notes` / `required_qualification_notes` / `commercial_disclosure_notes`；不代替平台判定审核结果、不保证审核通过。
- **Campaign Context：** `campaign_objective` / `available_asset_types[]`；MVP 支持笔记形式 `image_text_note_brief` + `video_note_brief`，不支持直播脚本 / 评论区运营 / 私信销售 / 广告创意组合 / 自动发布 / 最终视频 Storyboard。
- **Content Mode：** 1 主 + 可选次级（experience_sharing / problem_solution / usage_scenario / product_demonstration / selection_guide / knowledge_education / objection_response / comparison_context / new_product_introduction）；Experience Sharing 仅在有真实素材时使用；Comparison Context 不得踩一捧一贬损竞品。
- **Title Direction：** 3–5 方向，每个 `title_direction` / `user_question_or_tension` / `primary_keyword` / `message_focus` / `proof_required` / `risk_notes`；方向非最终标题，不得虚构体验 / 无依据最高级 / 变体字规避 Prohibited Claims。
- **Cover Direction：** `cover_message_direction` / `cover_visual_focus` / `cover_information_priority` / `cover_risk_notes`；突出一个主信息，须与 Core Message 一致。
- **Narrative Structure：** 模块化 `hook` / `user_context` / `user_problem` / `product_response` / `proof_or_demonstration` / `limitations_or_fit_boundary` / `selection_guidance` / `interaction_or_CTA`；`limitations_or_fit_boundary` 不得为营销效果被自动删除。
- **Search Intent：** `primary_search_intent`；不得虚构热搜 / 无来源声称关键词流行 / 竞品品牌词截流。
- **Keyword Direction：** `primary_keywords[]` / `secondary_keywords[]` / `topic_directions[]`；来源限于品类 / 用户问题 / 使用场景 / 真实用户语言 / 有效商品属性。
- **Hashtag Direction：** `hashtag_directions[]`；MVP 仅输出方向，不输出最终 Hashtags 列表。
- **Platform Risk Notes：** 完整继承 `MarketingBrief.prohibited_claims`，并可增加 `xiaohongshu_specific_risk_notes`；不得删除 / 降低风险等级 / 通过晦涩或 Emoji·拼音·谐音·拆字规避 / 伪造素人语气隐藏风险。
- **Execution Brief Current Truth Pointer：** `execution_brief_version_id`（承接 DEC-024）；用户编辑 → 新 Execution Brief Version + 保留原模型版本 + 记录用户修改 + 重跑 Validator + 更新 Pointer；承接 DEC-009：Execution Brief 修改不使 Marketing Brief 与上游失效；因 Execution Brief 为当前 MVP 最终输出，普通编辑不触发下游失效（当前 MVP 无下游）；若编辑改变 Audience / Core Message / Benefit Hierarchy / Proof Point / Approved Strategy 返回 `brief_change_required`；MVP 不增额外强制 Review Gate（承接 DEC-007）。

> 注：本节确认**Xiaohongshu Brief Mapping Adapter 的数据职责**（Execution Brief Version + Platform Policy Snapshot + Account / Commercial / Campaign Context + Content Mode + Title / Cover Direction + Narrative Structure + Search Intent / Keyword / Hashtag Direction + Platform Risk Notes + Execution Brief Current Truth Pointer；承接 DEC-004/006/009/015/019/020/024/025/029/030，Amends DEC-004 / DEC-020 不推翻既有结论）；概念 Platform Adapter Spec 见 [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)（仅概念）。**仍待确认** 最终 Execution Brief Schema、字段名、Platform Policy Snapshot 采集与同步机制、Account and Campaign Context 最终结构、Content Mode 分类表、Title / Cover 模板、Narrative Structure 模块组合规则、笔记形式选择规则、关键词相关性判定算法、Hashtag 方向数量边界、视频镜头信息方向结构、风险词库、数据库表。本节**不**创建最终数据库表 / 正式小红书 Prompt / Adapter 代码 / LangGraph Node / Execution Brief UI / Risk Validator 实现 / Final Copy Generator / Platform Policy Sync 代码，**不**选择平台数据供应商 / 热点接口 / 搜索关键词工具 / 风险审核供应商 / 视频时长 / 图文页数 / Hashtag 数量 / 发布 API / 最终 LLM。下一议题 Hybrid Retrieval and Evidence Runtime Architecture 已由 DEC-032 确认（见下节）。

---

### Hybrid Retrieval and Evidence Runtime 的数据职责（DEC-032，Accepted，2026-07-29）

> 来源：[DEC-032 — Hybrid Retrieval and Evidence Runtime 采用 Direct-first 检索、确定性检索规划、强制权限与版本过滤与可复现证据装配](../decisions/dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)（Runtime Architecture / Retrieval Architecture / Evidence Architecture；Amends DEC-014）。概念 Runtime Spec 见 [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)。

- **Retrieval Request（概念输入）：** `task_id` / `workspace_id` / `skill_name` / `retrieval_purpose` / `query_text` / `exact_identifiers[]` / `required_source_scopes[]` / `allowed_source_set_version_id` / `required_evidence_types[]` / `time_constraints` / `requested_output`（概念字段，非最终 Schema）。
- **Retrieval Plan（概念输出，可版本化）：** `strategy` / `structured_queries[]` / `lexical_queries[]` / `semantic_queries[]` / `mandatory_filters` / `optional_filters` / `fusion_required` / `reranking_allowed` / `coverage_requirements` / `fallback_strategy`，可版本化（`retrieval_plan_version`）。Deterministic Retrieval Planner 决定检索方式与边界，LLM 可有限辅助 Query Planning 但不得决定 `task_id` / 权限 / Source Scope / Source Set Version，精确标识符须逐字保留。
- **Retrieval Run（检索日志）：** 每次检索记录一条 RetrievalRun（使用的 Plan、过滤条件、组件版本、召回结果概要、时间）。
- **Candidate Fragment（概念对象）：** `fragment_id` / `source_id` / `source_version_id` / `source_scope` / `product_id` / `competitor_id` / `document_or_record_id` / `record_id` / `locator` / `content` / `retrieval_channels[]` / `lexical_rank` / `semantic_rank` / `fused_rank` / `rerank_score` / `matched_terms[]` / `query_ids[]` / `availability_status` / `retrieval_run_id`（非最终 Schema）。
- **Retrieval Channel Ranks：** 各检索通道排名须保留（`lexical_rank` / `semantic_rank` / `fused_rank` / `channel_ranks`）；BM25 与 Vector similarity 属不同量纲，**不得**直接相加，可用 Rank Fusion 或 Score Normalization + Weighted Combination；排名分数只解释「为何被召回」，不是 Fact Confidence / Evidence Strength。
- **Evidence Package（Skill 可复现证据输入快照）：** `evidence_package_id` / `task_id` / `skill_name` / `purpose` / `retrieval_plan_version` / `source_set_version_id` / `retrieval_run_ids[]` / `candidate_fragments[]` / `verified_facts[]` / `dataset_statistics[]` / `known_conflicts[]` / `coverage_summary` / `evidence_limitations[]` / `generated_at` / `package_hash`；Evidence Package 是 Skill 输入快照，**不**进 Current Truth。
- **Source Set Version Dependency：** Supersceeded 默认排除、Deleted 排除、Restricted 返回权限错误、Processing not complete 不作完整可计数数据集；Source Set 变化时旧 Evidence Package 不再是当前输入，须基于新 Source Set Version 重新装配。
- **Package Hash：** `package_hash` 保证同 Plan + 同 Source Set Version + 同组件版本可复现 Skill 当时看到的证据输入。
- **Retrieval Component Versions：** 检索组件版本（Embedding 版本 / 索引版本 / Reranker 版本 / Fusion 方法版本）须记录以支持复现与可解释性。
- **Mandatory Metadata Filters：** 过滤在召回前 / 召回中生效（`task_id` / `workspace_id` / `permission_scope` / `source_scope` / `product_id` / `competitor_id` / `source_set_version_id` / `source_version_status` / `document_or_record_status` / `fragment_status` / `language` / `time_range`），**不**是「先全召回再删除」。
- **Formal Evidence Link Transaction Boundary：** Formal Evidence Link 仅在 Skill 输出通过 Evidence Validator 后才创建；Evidence Package = 可复现的 Skill 输入，Formal Evidence Link = 正式关系（承接 DEC-024 / DEC-025）。

> 注：本节确认**Hybrid Retrieval and Evidence Runtime 的数据职责**（Retrieval Request / Retrieval Plan / Retrieval Run / Candidate Fragment / Retrieval Channel Ranks / Evidence Package / Source Set Version Dependency / Package Hash / Retrieval Component Versions / Mandatory Metadata Filters / Formal Evidence Link Transaction Boundary；承接 DEC-008/009/013/014/015/023/024/025/026/027/028/030/031，Amends DEC-014 不推翻既有结论）；概念 Runtime Spec 见 [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)（仅概念）。**仍待确认** Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization 与融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / RetrievalPlan / RetrievalRequest / Candidate Fragment / Evidence Package / RetrievalRun 最终 Schema / 最终错误代码。本节**不**创建正式 Embedding / Vector Index / Full-text Index 代码 / Retrieval API / Query Rewrite Prompt / Reranker 代码 / Fusion 代码 / Cache 代码 / 数据库表 / LangGraph Retrieval Node，**不**选择上述技术选型。下一议题 Workflow Runtime Failure Recovery, Retry and Observability Contract 已由 DEC-033 确认（见下节）。

---

### Workflow Runtime 的数据职责（DEC-033，Accepted，2026-07-29）

> 来源：[DEC-033 — Workflow Runtime 采用分层运行记录、分类故障处置、有界重试、安全恢复、事务幂等与端到端可观测性契约](../decisions/dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)（Runtime Architecture / Reliability Architecture / Observability Architecture；Amends DEC-023 / DEC-024 / DEC-029）。概念 Runtime Spec 见 [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)。

- **Workflow Run Record（概念对象）：** `run_id` / `task_id` / `thread_id` / `trigger_type`（initial_start / user_resume / human_review_resume / automatic_retry / explicit_rerun / recovery_resume）/ `resumed_from_checkpoint_id` / `started_at` / `completed_at` / `status` / `current_stage` / `initiator` / `cancellation_requested_at` / `failure_summary` / `trace_id`。
- **Skill Run Record（概念对象）：** `skill_run_id` / `task_id` / `run_id` / `skill_name` / `skill_contract_version` / `execution_configuration_version` / `input_version_ids[]` / `source_set_version_id` / `evidence_package_id` / `input_fingerprint` / `started_at` / `completed_at` / `status` / `output_version_id` / `failure_disposition` / `retry_count`。
- **Node Execution Record（概念对象）：** `node_execution_id` / `skill_run_id` / `node_name` / `node_type` / `input_fingerprint` / `started_at` / `completed_at` / `status` / `attempt_count` / `output_reference` / `checkpoint_id` / `error_id` / `trace_span_id`。
- **Execution Attempt（概念对象）：** `attempt_id` / `node_execution_id` / `attempt_number` / `started_at` / `completed_at` / `status` / `provider_or_component` / `timeout_deadline` / `retry_reason` / `request_reference` / `response_reference` / `error_id` / `usage_metadata`。重试不创建新的 Skill Run 或业务版本（承接 DEC-024）。
- **Runtime Error Record（概念对象）：** `error_id` / `task_id` / `run_id` / `skill_run_id` / `node_execution_id` / `attempt_id` / `error_code` / `error_category` / `severity`（info / warning / error / critical）/ `retryability`（retryable / conditionally_retryable / non_retryable / unknown）/ `failure_disposition`（retry / fallback / wait / pause / fail / cancel / manual_recovery）/ `component` / `user_safe_message` / `operator_message` / `cause_chain[]` / `input_version_ids[]` / `provider_error_reference` / `first_occurred_at` / `last_occurred_at` / `remediation_options[]`。
- **Input Fingerprint（幂等键概念）：** `task_id` / `skill_name` / `input_version_ids` / `source_set_version_id` / `skill_contract_version` / `execution_configuration_version` / `logical_operation`；相同业务请求重复到达返回首次成功结果，不重复创建业务版本。
- **Idempotency Record：** 记录已成功提交操作的幂等结果（Workflow Resume / Skill Commit / Node Side Effect / Approved Strategy Submission / Brief Commit / Retry 后 DB 写入 / 外部 Side-effect Tool）。
- **Recovery Case（概念对象）：** `recovery_case_id` / `task_id` / `run_id` / `failed_skill_run_id` / `failed_node_execution_id` / `error_ids[]` / `last_safe_checkpoint_id` / `current_business_versions[]` / `failed_input_versions[]` / `recommended_actions[]` / `status` / `assigned_operator` / `resolution` / `audit_history[]`。
- **Cancellation Record：** 记录取消请求、受影响层（Workflow Run / Skill Run / Task）、协作式取消传播结果与已回滚 / 已保留的事务。
- **Runtime Audit Record：** 记录事务提交 / 回滚 / Checkpoint 保存 / Checkpoint 拒绝为 stale / 恢复动作（manual_recovery 不得伪造 Fact / 绕 Validator / 改 Evidence Link / 直接改 Pointer）。
- **Trace Correlation IDs：** `task_id` / `thread_id` / `run_id` / `skill_run_id` / `node_execution_id` / `attempt_id` / `trace_id` / `retrieval_run_id` / `evidence_package_id` / `review_id` / `source_version_id` / `model_call_id` / `tool_call_id` 须贯穿日志 / Trace / Metric，形成完整执行关联链。
- **Checkpoint Reconciliation Metadata：** `checkpoint.task_id` / `checkpoint.thread_id` / `checkpoint.input_version_ids` / `current_truth_pointers` / `stage_validity` / `review_package_version` / `checkpoint_status`（含 `stale`）；Resume 前验证，旧业务版本 → `stale` 不执行旧计划。

> 注：本节确认**Workflow Runtime 的数据职责**（Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error Record / Input Fingerprint / Idempotency Record / Recovery Case / Cancellation Record / Runtime Audit Record / Trace Correlation IDs / Checkpoint Reconciliation Metadata；承接 DEC-007/009/011/012/013/023/024/025/029/032，Amends DEC-023 / DEC-024 / DEC-029 不推翻既有结论）；概念 Runtime Spec 见 [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)（仅概念）。以上均为概念结构，**非最终数据库 Schema**。运行记录与业务 Domain Object（Facts / Insights / Positioning / Approved Strategy / Marketing Brief / Execution Brief）分离；运行记录本身**不**是 Current Truth 业务对象。**仍待确认** Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue·Worker·DLQ 技术 / Logging·Tracing·Metrics·Alerting Provider / 是否采用 OpenTelemetry / Checkpointer 实现 / 数据库 / Outbox / 分布式锁 / 数据保留周期 / 日志采样率 / PII 脱敏实现 / 并发模型 / 最终 SLO / 各运行记录最终 Schema / 最终字段名 / 最终错误代码。本节**不**创建正式 Retry Middleware / LangGraph Recovery / Checkpointer / Worker / Queue / DLQ / Recovery Worker / Logging·Tracing Pipeline / Metrics Dashboard / Alerting Rules / 数据库表 / Outbox / 分布式锁 / API / 业务实现代码，**不**选择上述技术选型。在 **Technical Spike Plan and Architecture Readiness Gate** 议题已由 DEC-034 确认（见下节）。

### Technical Spike and Architecture Readiness Gate 的数据职责（DEC-034，Accepted，2026-07-29）

本节确认 **Spike 必须验证的数据行为**，**不**定义最终数据库 Schema。Spike 是非生产实验；Mock Business Objects 仅验证架构行为，不构成最终 Domain Schema。

- **Graph State References：** Spike Graph State 须保持紧凑、引用导向，仅存 `task_id` / `thread_id` / `current_run_id` / `current_stage` / `fact_version_id` / `insight_version_id` / `positioning_version_id` / `review_id` / `approved_strategy_version_id` / `marketing_brief_version_id` / `waiting_reason` / `last_error_id` / `cancellation_requested`；**不**保存完整 Facts / Insights / Positioning Candidates / Review Draft / Evidence Package / 历史版本 / 完整文档或评论（正式业务内容须从 Business Repository 读取）。
- **Domain Version：** 验证事务成功只创建一个业务版本、事务失败完整回滚（Domain Version 与 Evidence Link 同生共死），不产生重复 Domain Version、不产生 Partial Write。
- **Current Truth Pointer：** 验证提交事务原子更新 Pointer、失败时 Pointer 不变、Retry / Resume 不覆盖较新版本、不产生重复 Pointer。
- **Review Package Version：** 验证 Review Package 固定上游版本（facts / insights / positioning version）、上游变化 → 标 `superseded`、旧 Package 提交被可靠拒绝、不自动迁移旧选择。
- **Runtime Records：** 验证 WorkflowRun / SkillRun / NodeExecution / ExecutionAttempt 可追溯（Retry = Same Skill Run + Same Node + Different Attempt，且同一业务版本；与 Rerun 可区分）。
- **Checkpoint Metadata：** 验证 Checkpoint 与 Current Truth 对账、旧业务版本 → 标 `stale`、不覆盖较新业务版本、不允许 Checkpointer 覆盖 Business Repository。
- **Idempotency Record：** 验证重复 Submit / Commit（相同 idempotency_key）只创建一个版本、返回首次成功结果、下游只恢复一次、不创建重复 Audit Success Record。
- **Recovery Case：** 验证 RecoveryCase 结构化（`recovery_case_id` / `last_safe_checkpoint_id` / `recommended_actions[]` / `audit_history[]`），Recovery 不绕过 Validator、不改 Evidence Link、不删历史。
- **Audit Record：** 验证事务提交 / 回滚 / 恢复 / Cancellation 可审计；失败不得被错误记为成功。
- **三类 Repository 逻辑分离：** Business Repository（Task / Domain Versions / Current Truth Pointers / Stage State / Review Package / Strategy Draft / Approved Strategy / Marketing Brief / Evidence Links / Audit）vs Runtime Repository（Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error / Recovery Case / Idempotency / Cancellation）vs Checkpoint Store（LangGraph 执行状态 / Interrupt / Resume 位置 / 临时上下文 / Checkpoint Metadata）；即使同一物理存储也须保持逻辑边界，`LangGraph Checkpoint Store ≠ Business Current Truth Repository`。

> 注：本节确认 **Technical Spike and Architecture Readiness Gate 的数据职责**（Spike 验证的 9 类数据对象：Graph State References / Domain Version / Current Truth Pointer / Review Package Version / Runtime Records / Checkpoint Metadata / Idempotency Record / Recovery Case / Audit Record + 三类 Repository 逻辑分离；承接 DEC-011/013/023/024/025/029/032/033，Amends DEC-023 / DEC-033 不推翻既有结论）；概念 Readiness Spec 见 [../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../specs/readiness/technical-spike-and-architecture-readiness-gate.md)（仅概念）；Spike 工作区见 [../spikes/spike-001-langgraph-runtime-and-recovery/](../spikes/spike-001-langgraph-runtime-and-recovery/)（仅规划，非实现）。以上均为概念结构，**非最终数据库 Schema**。本节**不**实现 Spike 代码、**不**创建正式业务 Graph、**不**编写四个核心 Skill 的生产 Prompt、**不**建立正式数据库 Schema、**不**选择生产级基础设施。**仍待确认** Spike 语言和版本 / LangGraph 具体版本 / Spike 数据库 / Checkpointer Backend / Mock LLM 实现 / Fault Injection 工具 / 测试框架 / Trace Provider / 临时 API / Spike 代码目录 / Spike 执行 Agent / 执行时间计划 / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号。**Technical Spike Execution Brief and Temporary Spike Stack 议题已由 DEC-035 确认（见下节）。**

---

### Technical Spike 临时技术栈与执行契约的数据职责（DEC-035，Accepted，2026-07-29）

> 来源：[DEC-035 — Technical Spike 临时采用 Python、同步 LangGraph StateGraph、分离式 SQLite 存储、确定性 Mock 与场景化故障注入执行契约](../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)（Technical Spike Execution / Temporary Architecture / Validation Environment；Amends DEC-034）。Spike 临时栈见 [../spikes/spike-001-langgraph-runtime-and-recovery/temporary-stack.md](../spikes/spike-001-langgraph-runtime-and-recovery/temporary-stack.md)。

本节确认 **Spike-001 把 DEC-034 的三类逻辑 Repository 落实为三类物理分离 SQLite**，**不**定义最终数据库 Schema；三类 SQLite 仅属 Spike 实验存储，不构成正式数据库设计。

- **三类物理分离 SQLite：** `.spike-data/` 下 `business.sqlite` / `runtime.sqlite` / `checkpoints.sqlite`，直接验证 `Business State ≠ Runtime State ≠ Checkpoint State`（未来生产即使使用同一数据库实例，也必须保持逻辑职责分离）。
- **business.sqlite（业务 Current Truth 唯一权威）：** Task / Stage State / Domain Versions（Fact / Insight / Positioning / Review Package / Strategy Draft / Approved Strategy / Marketing Brief）/ Formal Evidence Links / Current Truth Pointers / Business Audit Records / Idempotency Records；Checkpoint 不能覆盖或替代。
- **runtime.sqlite：** Workflow Run / Skill Run / Node Execution / Execution Attempt / Runtime Error / Recovery Case / Cancellation Record / Runtime Events / Trace Correlation Metadata；**不**保存正式业务 Current Truth。
- **checkpoints.sqlite（LangGraph `SqliteSaver` 管理）：** Graph Checkpoint / Thread State / Interrupt / Resume 位置 / Pending Writes / Checkpoint Metadata；**不**负责 Domain Version / Current Truth Pointer / Review Package / Approved Strategy / Formal Evidence Link / Business Audit。
- **Atomic Commit Contract：** 每次正式业务 Commit 在单一事务内完成 Create Domain Version + Formal Evidence Links + Update Current Truth Pointer + Update Stage State + Write Audit + Write Idempotency Record，任一失败整体回滚；Graph Node **不得**绕过统一 `BusinessCommitService` 分别写入。
- **Checkpoint 安全：** 启用严格反序列化边界（`LANGGRAPH_STRICT_MSGPACK=true` 或等价）；Graph State 只存简单明确允许的类型，**不**存任意 Python 对象 / Secret / 完整业务文档 / 不必要模型输出。
- **Human Review 节点边界：** 含 `interrupt()` 的 Node 在 Resume 可能从头重执行，Review Package 创建与 Interrupt 必须分离 Node（`create_review_package → await_human_review → load_approved_strategy`），禁止 `create_review_package + write_business_data + interrupt()` 同 Node。

> 注：本节确认 **Technical Spike 临时技术栈与执行契约的数据职责**（三类物理分离 SQLite + Atomic Commit Contract + Checkpoint 安全 + Human Review 节点边界；承接 DEC-024 / DEC-029 / DEC-032 / DEC-033 / DEC-034，Amends DEC-034 不推翻既有结论）；概念规格见 [../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)（仅概念）。**business.sqlite / runtime.sqlite / checkpoints.sqlite 只属于 Spike 实验存储，不构成正式数据库设计**；以上均为概念结构，**非最终数据库 Schema**，所有临时选择**不构成生产承诺**。本节**不**实现 Spike 代码、**不**执行 uv sync / 依赖安装 / SQLite 初始化 / StateGraph Compile / Scenario Runner / pytest / Fault Injection，**不**选择生产数据库 / 生产 Checkpointer / ORM。**仍待确认** Spike 主执行 Agent / Spike 执行时间计划 / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术。下一议题（尚未开始，需用户明确启动）：`Spike-001 Execution Authorization and Agent Handoff Contract`。在该议题确认前：**不**启动 Spike、**不**安装依赖、**不**创建 Spike 代码、**不**运行测试、**不**创建正式 Roadmap、Development Status 保持 `NOT READY`。

---

## 当前状态

- 项目处于 **架构探索阶段**（Session-002 进行中）。
- 已确认 Workflow State 的数据结构与分组原则（DEC-012）；最终数据契约、字段类型、Schema 技术、数据库与存储实现均**尚未确认**。
- 本文件的具体数据内容，必须等到对应 Proposed Decision 被用户明确接受并记为 Accepted Decision（见 [../decisions/](../decisions/)）后，才能写入。

---

## 文档骨架（占位，内容待填充）

> 以下章节标题仅作为未来结构占位，**当前全部为空**，不构成任何数据声明。

- 数据源与数据分类
- 核心数据模型
- RAG 知识库结构（索引、切片、embedding 策略）
- 数据契约（各模块 / Agent 间的数据接口）
- 数据存储与访问
- 数据隐私与合规

---

## 待讨论的开放问题（数据架构相关）

- 需要哪些数据源？
- 核心数据结构如何设计？
- RAG 知识库如何组织？
- 各模块间的数据契约是什么？
- 涉及哪些隐私 / 合规约束？

改变核心数据模型属于重大议题，通常应通过 RFC 讨论（见 [../rfcs/](../rfcs/)）。

讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得擅自选择数据库或存储方案。
- 不得为使文档「完整」而补充未经讨论的数据结构。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
