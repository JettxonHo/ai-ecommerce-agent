# Integration Boundaries（集成边界）

> **Current sync（2026-08-07）：** RFC-001～RFC-004 与 RFC-006 已 Accepted；API / Worker / CLI 进程边界和 PostgreSQL 持久化边界已经确认。DEC-049～054 冻结 Workflow / Model Runtime，DEC-046～048 与 DEC-055～056 冻结产品 / Frontend，DEC-063～066 冻结 RFC-004 HTTP Contract。DEC-067 进一步冻结 Source / SourceVersion / revisioned TaskSourceAssociation / DerivedArtifact 分离、逐资料 Durable Processing、typed partial result、六值 processing lifecycle、SourceSet reference manifest 与四类格式感知 Fragment / Locator；Evidence Package 不再使用 `package_hash`。Source / Evidence Capability 负责权威 eligibility，RFC-003 Worker 承担耐久处理，Frontend 只消费服务端状态。RFC-005 DQ-04～10 的 Retrieval / Index / public transport 与 RFC-007 Observability 仍待闭合。
> **Product integration constraint sync（2026-08-07）：** DEC-060～062 要求 Skill / Review / Adapter 传播 Claim Integrity 而不建设通用合规系统；Retrieval 与 Source 处理默认限于当前 Task，移除 / 替换与物理删除分离；Frontend 外层增加最小 Task Index，但同一个深 TaskWorkbench 与 Typed Adapter Seam 不变。公共 List / Claim / Source Command、Retrieval 过滤和运行边界分别由 RFC-004 / 005 / 007 冻结。
> **Historical expansion note：** 正文按 DEC-013～037 的形成顺序累积；其中 `NOT STARTED`、`NOT READY`、`下一动作 / 下一议题`、旧 PENDING 列表和 Spike Handoff 只记录当时状态，不是当前授权或执行指令。当前状态仅以上述 Current sync、[AGENTS.md](../../AGENTS.md) 与 [Implementation Readiness](../handoffs/implementation-readiness.md) 为准。

> **Status: PARTIAL — 集成方向已确认（DEC-013 编排层 ↔ 持久化存储；DEC-014 检索 / 知识库组件；DEC-015 Skill 依赖；DEC-016 外部仓库角色区分；DEC-020 MVP 平台 Adapter 与共享能力集成面；DEC-021 未来受约束 Worker Runtime 边界；DEC-022 工作流框架与领域状态 / 配置 / Worker 集成边界；DEC-023 LangGraph 与 Skill Service / Worker / 模型供应商集成边界；DEC-024 LangGraph State 与 Domain Objects / Checkpointer 与 Business Repository 集成边界；DEC-025 Skill / LLM / Retrieval Service / Evidence Validator / Business Repository / Frontend 与来源证据集成边界；DEC-026 Product Intake & Fact Extraction Skill 与 Evidence Package / Evidence Validator / Business Repository / 下游 Skill / Human Review 集成边界；DEC-027 Customer Insight Analysis Skill 与 Evidence Package / 确定性统计服务 / Evidence Validator / Business Repository / 下游 Positioning Skill 集成边界；DEC-028 Product Positioning Skill 与 Facts / Insights / Validator / Repository / Human Review / 下游 Marketing Brief Skill 集成边界 / DEC-029 Review Service / LangGraph Interrupt / Frontend / Approved Strategy Service / 下游 Marketing Brief Skill 集成边界 / DEC-030 Marketing Brief Generation Skill 与 Approved Strategy / Proof Point / 下游 Xiaohongshu Adapter 集成边界 / DEC-031 Xiaohongshu Brief Mapping Adapter 与 Marketing Brief / Platform Policy Repository / Final Copy 集成边界 / DEC-032 Hybrid Retrieval and Evidence Runtime 集成边界 / DEC-033 Workflow Runtime Failure Recovery, Retry and Observability 集成边界 / DEC-034 Technical Spike Plan and Architecture Readiness Gate 集成边界 / DEC-035 Technical Spike 临时技术栈与执行契约集成边界[Spike 代码不能被生产模块 Import / Spike Graph 不能直接成为生产 Graph / Scripted Model 不构成生产 LLM 决策 / Mock Retrieval 不构成生产 Retrieval 决策 / SqliteSaver 不构成生产 Checkpointer 决策 / Spike Agent 不得修改 Accepted DEC / 不得创建正式 Roadmap 或 Issues / 不得执行外部 Side Effect；Amends DEC-034]）；具体存储 / 数据库 / 向量库 / 检索 / Skill 实现 / Checkpointer / 基底仓库供应商仍未确认**
> **Status clarification：** 上述累积 Status 的“Checkpointer / 模型 API 仍未确认”是 DEC-049 / DEC-052 之前的历史边界；当前 Workflow Runtime、Checkpoint 与已接受的 Model Runtime 输入以 RFC-003、DEC-049～052 和本文件 Current sync 为准。
> 本文件是 Current Truth Layer 的一部分。其内容只能来自用户明确接受的 Decision。
> 当前已确认：编排层需与持久化存储集成（DEC-013）；未来可能集成关键词检索、语义检索与知识库存储组件（DEC-014）；Skill 作为业务能力包可能依赖 LLM、检索、文档解析与外部 Tool（DEC-015）；项目区分工作流基底仓库与 Skill 供体仓库两类外部仓库角色（DEC-016）；工作流运行框架已由 DEC-023 选定为 LangGraph（StateGraph / Graph API），须遵守 Node Adapter ↔ Skill Service 分离、LangGraph 仅以结构化 IO 调用 Skill、Skill 不控制主 Graph、Worker 不写正式 Workflow State、模型供应商经 LLM Gateway 隔离；DEC-024 进一步确认 LangGraph State 通过 Version ID 引用 Domain Objects、Node Adapter 负责加载正式 Domain Objects、Skill Service 不直接读取 LangGraph Checkpoint、Frontend 不直接读取 Checkpointer 作正式业务结果、Checkpointer 与 Business Repository 使用独立接口、业务版本与 Checkpoint 版本不得混用；**DEC-025 进一步确认 Skill 只能引用 Evidence Package 中允许的 Fragment ID、LLM 不得自由生成 Source ID、Retrieval Service 返回 Candidate Fragments、Evidence Validator 负责正式引用校验、Business Repository 保存 Evidence Links、Frontend 通过业务 API 获取来源和原文定位、Skill 不直接读取整个来源数据库、当前商品和竞品 Source Scope 必须隔离**；**DEC-026 进一步确认 Product Intake & Fact Extraction Skill 经 Evidence Package 获得当前商品 Source Version 输入、输出 Facts Version 须经确定性 Validator 15 项校验才写入 Business Repository 的 Facts Current Truth、关键冲突创建 SourceConflict 并触发暂停交 Human Review、下游 Skill（Customer Insight / Positioning）消费 Facts Version、Skill 不直接读取来源数据库；**DEC-027 进一步确认 Customer Insight Analysis Skill 经 Evidence Package 获得用户证据输入（只读当前 Evidence Package 允许的 Fragment 集合）、统计比例由确定性统计服务生成而 LLM 不直接计算正式总体频率、用户原声引用必须通过 Evidence Validator、竞品 Source Scope 不得转换为当前商品用户事实、下游 Positioning Skill 必须读取 Insight 的 Evidence Class 和 Limitations、Insights Version 须经 Validator 18 项校验才写入 Business Repository 的 Insights Current Truth**；**DEC-028 进一步确认 Product Positioning Skill 只能读取当前有效 Facts Version（`Fact Stage = valid`）和当前有效或 `valid_with_limitations` 的 Insights Version；Proof Point 通过 Fact ID 经 Evidence Link 追溯到 Fragment / Source Version；Competitor Evidence 只能用于 Gap 和品类 Context、不得归因当前商品能力或进入当前商品 Proof Point；Positioning Candidates 须经确定性 Validator 20 项校验、硬校验失败不写入候选 / 不进入 Human Review；Positioning Skill 不能直接创建 Approved Strategy；Approved Strategy Version 由 Human Review（select / edit / merge[须重新通过 Validator] / reject / request_more_information）在 Human Review Service 中形成；Marketing Brief Skill 只能读取 Approved Strategy Version，未经审核的候选不直接生成 Brief；业务证据不足（waiting_input / paused）与技术失败（failed）严格分离；**DEC-029 进一步确认 Positioning Skill 只创建候选、不创建 Approved Strategy；Review Service 创建固定上游版本的 Review Package；LangGraph 负责 Interrupt 暂停与 Resume 恢复（不替代业务事务）；Frontend 提交结构化 Review Decision（含 Hypothesis / Proof Point / Evidence Limitation Decisions）；Approved Strategy Service 执行 18 步原子提交事务（幂等 + 并发保护 + Current Truth Pointer 原子更新）；Marketing Brief Skill 只能读取 Approved Strategy Version、不得读取未审核候选或 Strategy Draft；LLM 不得自动选择候选 / 自动接受 Hypothesis / 自动删除 Evidence Limitation / 自动提交审核 / 把无证据内容升级为 Proof Point / 绕过 Validator；Checkpointer 不替代 Review Business Repository（审核历史 / Withdrawal Record / Audit 由业务库保存）**。**DEC-030 进一步确认 Marketing Brief Skill 只能读取当前有效 Approved Strategy Version、不得读取未审核候选或 Strategy Draft；Strategy Lock 六字段受控；Proof Point 通过 Fact ID 追溯；Brief 输出保持平台无关；Xiaohongshu Adapter 只能映射 Brief、不得改 Audience / Core Message / Benefit Hierarchy / Proof Points / Evidence Limitations / Prohibited Claims / Approved Strategy；Brief 修改使 Xiaohongshu Mapping 失效、Strategy Change 必须返回 Human Review；DEC-031 进一步确认 Xiaohongshu Brief Mapping Adapter 只能读取当前有效 Marketing Brief Version（并引用 approved_strategy_version_id / facts_version_id / platform_policy_snapshot_id）、不得读取未审核 Candidate / Strategy Draft / 未审核 Brief 草稿；读取版本化 Platform Policy Snapshot（每次记录 policy_snapshot_id / policy_version，不得 Prompt 硬编码长期有效规则，失效返回 platform_policy_update_required）；读取 Account and Campaign Context 输出商业性注释但不代替平台审核；Adapter Lock 锁定 Brief 九字段、不得改 Audience / Core Message / Benefit Hierarchy / Proof Point / 把 Hypothesis 转 Fact / 规避 Prohibited Claims；真实用户原声必须来自真实 Fragment、禁止虚构体验；用户原声 / Execution Brief 须经 Evidence Validator；Execution Brief 须经确定性 Validator 28 项才写入 Business Repository 的 Execution Brief Current Truth；Execution Brief 普通编辑不触发下游失效（当前 MVP 无下游）；Final Copy Generator / 发布 / 自动审核不进 MVP**。**DEC-032 进一步确认 Hybrid Retrieval and Evidence Runtime 为跨 Skill 共享运行架构层，Skill 不直接查询任意 Source、只能通过 Retrieval Runtime 请求证据；Deterministic Retrieval Planner 决定检索方式（Direct-first：能直接读取时不使用检索）；Permission / Task / Product Identity / Source Scope / Source Version 由确定性逻辑控制、在召回前 / 召回中生效（非先全召回再删除）；LLM 可有限辅助 Query Planning 但不得决定 task_id / 权限 / Source Scope / Source Set Version，精确标识符须逐字保留；检索结果仅为 Candidate Fragments + Evidence Package，不是 Formal Evidence，须经 Evidence Validator 才创建 Evidence Link；Dataset Statistics 不由 Top-K Retrieval 产生；Formal Evidence Link 仅在 Skill 输出过 Evidence Validator 后才创建；Retrieval Checkpoint 或 Cache 不替代业务 Source Repository**。**Workflow Runtime 的集成边界（DEC-033：Workflow Runtime 统一协调 Retry Budget（per_attempt_timeout / per_node_retry_limit / per_skill_retry_budget / per_workflow_run_deadline，防嵌套放大）；LLM Wrapper 不直接决定业务 Rerun（只重试或回退，业务 Rerun 由确定性 Workflow 控制与用户 / 上游版本触发）；Retrieval Runtime（DEC-032）使用明确 Fallback 并传播 Evidence Limitation；Repository Commit 必须事务化（Create Domain Version / Create Evidence Links / Update Pointer / Update Stage / Write Audit 任一失败整体回滚）；LangGraph Checkpointer 不替代业务 Current Truth Repository（只恢复执行状态 / Interrupt / Node 进度）；Human Review Resume 必须验证 Review Package（携带 review_id / package_version / draft_version，幂等，不绕过 DEC-029）；Recovery Worker 不得绕过 Validator / 伪造 Fact / 改 Evidence Link / 直接改 Pointer；Side-effect Tool 必须支持 idempotency_key 或可确认结果（首次成功未知不得盲目重试）；Observability（Logging / Tracing / Metrics / Alerting）不得泄漏 Secret / Key / 完整敏感数据 / 未脱敏评论 / 其他 Workspace / 内部 Prompt；Amends DEC-023 / DEC-024 / DEC-029，不推翻既有结论）**。**Technical Spike and Architecture Readiness Gate 的集成边界（DEC-034：Spike Graph 不得直接成为生产 Graph（须独立 PR 经 Review 迁入，不得整个 Prototype 改名生产实现）；Checkpoint Store 不替代 Business Repository（三类 Repository 逻辑分离，`LangGraph Checkpoint Store ≠ Business Current Truth Repository`）；Mock Business Objects 不构成最终 Domain Schema（仅验证架构行为）；Spike 成功不自动改变 Development Status（须 Readiness Review + 用户明确确认才可 READY / CONDITIONALLY READY / NOT READY）；MVP Roadmap / Epic Map / GitHub Issues / RFC Register 只能在 Readiness Gate 通过并经用户确认后正式生成；Coding Agent 不得在 Spike 中锁定生产基础设施（Production Database / Checkpointer / ORM / API / Frontend / Vector DB / Embedding / Logging / Tracing / Deployment 等须经 RFC 或正式技术决策）；Architecture Agent 只能提交 Readiness Recommendation、不得自行写 Development Status = READY；Amends DEC-023 / DEC-033，不推翻既有结论）**。**Technical Spike 临时技术栈与执行契约的集成边界（DEC-035：Spike 代码不能被生产模块 Import（Spike 是独立可抛弃实验目录）；Spike Graph 不能直接成为生产 Graph（须独立 PR 经 Review 迁入）；Scripted Model 不构成生产 LLM 决策（生产 LLM 仍待 RFC）；Mock Retrieval 不构成生产 Retrieval 决策（生产 Embedding / 向量库 / Retrieval 仍待 RFC）；SqliteSaver 不构成生产 Checkpointer 决策；Spike Agent 不得修改 Accepted DEC；Spike Agent 不得创建正式 Roadmap / Epics / Issues；Spike Agent 不得执行外部 Side Effect（含真实发布 / 外部调用）；Spike Agent 不得擅自更改 LangGraph 1.2.9（失败走 Spike Finding 等用户确认）；三类物理分离 SQLite 仅 Spike 实验存储不构成正式数据库设计；所有临时选择不构成生产承诺；Amends DEC-034，不推翻既有结论）**。**Spike-001 执行授权契约的集成边界（DEC-036：GitHub Issue 不替代 Spec / PR 描述不替代 Accepted DEC / Merge 不代表 READY / Check 通过不代表 READY / Agent Recommendation 不代表 READY / 用户保留不可逆 Git·GitHub 操作 / Claude 与 Codex 默认不得并发修改同一 Branch；Amends DEC-034 + DEC-035，不推翻既有结论）**。**Formal Spike-001 Execution Authorization 的集成边界（DEC-037：Execution Authorization 由 NOT GRANTED 转为 GRANTED 不等于已开始执行或已通过 / 第一动作仍是只读 Repository Audit、Audit 与稳定文档基线通过前不得写入·安装·建 Spike 代码·Branch·PR / 授权 Spike Issue·独立 Branch·Draft PR 不得越权修改 Accepted Business Specs 或 Accepted DEC 含义 / 隔离依赖授权不得改全局 Python·静默更换 LangGraph 版本 / S6 完成边界[S6 后停止，不 Merge·不关闭 Issue·不自行宣布 READY] / 用户保留不可逆 Git·GitHub 操作与 Architecture READY 确认[PR Merge≠READY、Issue Closed≠READY、Agent Recommendation≠READY]；Amends DEC-034 + DEC-035 + DEC-036，不推翻既有结论）**。**未**确认文件存储、数据库、Checkpointer 类型、向量数据库、检索组件、模型 API、Skill 实现、工作流基底仓库及任何具体第三方服务 / 供应商 / GitHub 仓库、API / Python 后端框架、前端、部署方式、LangSmith / Observability 工具、Parser / OCR / Embedding / Vector Store / Web Scraper / Review Importer、前三个 Skill 的最终 Schema / Prompt / 代码、其余一个 Core Skill（Marketing Brief）Contract、最终 Insight Schema / Evidence Coverage 枚举名、最终 Positioning Schema / Approved Strategy Schema、候选相似度算法、Positioning 排序公式、Human Review Payload、评论主题分类表、聚类算法、情感分析实现、最低评论数量、频率阈值、Xiaohongshu Brief Mapping Adapter 最终 Execution Brief Schema / Adapter 接口 / Prompt / 代码、Platform Policy Snapshot Repository、Account Context 输入接口、Execution Brief UI、Final Copy Generator、发布 API、视频镜头信息方向结构、Hybrid Retrieval and Evidence Runtime 的 Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization 与融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / RetrievalPlan / RetrievalRequest / Candidate Fragment / Evidence Package / RetrievalRun 最终 Schema、Workflow Runtime 的 Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue·Worker·DLQ 技术 / Logging·Tracing·Metrics·Alerting Provider / 是否采用 OpenTelemetry / Checkpointer 实现 / 并发模型 / 最终 SLO / 各运行记录最终 Schema / 最终错误代码、立即启动 Spike / Baseline Commit SHA / 实际 Spike Issue 编号 / 实际 PR 编号 / GitHub Labels / GitHub Project / GitHub Actions / CI Provider / Codex 是否执行独立 Review / Reviewer 身份 / Merge Strategy / Spike PR 是否最终 Merge / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术（生产后端语言 / 生产数据库 / 生产 Checkpointer / ORM / 生产 LLM / 生产 Retrieval / 生产 Observability / 生产部署平台）。下一动作 Spike-001 Execution Handoff（归档进入稳定 Git 基线后以独立任务执行；第一步必须是只读 Repository Audit；当前 Contract Authorization = ACCEPTED / Execution Authorization = GRANTED / Spike Execution Status = NOT STARTED / Architecture Readiness = NOT READY / Development Status = NOT READY，在归档完成并进入稳定 Git 基线前不启动 Spike、不安装依赖、不创建 Spike Branch / Issue / PR / 代码、不运行测试）。

---

## 已确认内容（Confirmed）

> 来源：[DEC-013 — MVP 采用支持跨会话恢复的任务级持久化状态](../decisions/dec-013-task-level-persistent-state-and-cross-session-resume.md)（Accepted，Architecture，2026-07-27）

- **工作流引擎 / 编排层未来需要与持久化存储集成：** 每个商品分析流程作为独立持久化任务（`task_id`），工作流引擎 / 编排层须能以任务为单位读写结构化 Workflow State，并在人工暂停后可靠恢复（跨页面 / 跨会话）。
- **文件存储、数据库和 Checkpoint 供应商仍未确认：** 是否采用关系数据库（PostgreSQL / SQLite 等）、对象 / 文件存储、Redis、LangGraph Checkpointer / thread_id、Checkpoint 频率与序列化方式、任务保留期限、隐私权限等**均未决定**。

> 注：本节仅确认**集成方向**（编排层 ↔ 持久化存储），**不**确认任何具体存储 / 数据库 / Checkpoint 供应商、文件存储服务、模型 API、电商平台 API 或第三方服务。

### 检索与知识库集成方向（DEC-014，Accepted，2026-07-27）

> 来源：[DEC-014](../decisions/dec-014-on-demand-hybrid-rag-and-layered-data-access.md)

- **未来可能集成关键词检索、语义检索和知识库存储组件：** 系统采用按需混合数据访问，对长资料 / 大量评论用「关键词检索 + 语义检索（+ 可选排序）」，运营方法与平台知识用独立知识库按需检索。
- **具体供应商和数据库尚未确认：** 关键词检索实现（如 BM25）、向量索引 / 向量数据库、Embedding 模型、Reranker、知识库存储、是否使用供应商文件检索 / 联网搜索等**均未决定**；任务资料与运营知识在逻辑上分离。

> 注：本节仅确认**检索 / 知识库集成方向**，**不**确认任何具体检索引擎、向量数据库、Embedding 模型、Reranker、供应商文件检索服务或具体 GitHub 仓库。

### Skill 依赖（DEC-015，Accepted，2026-07-27）

> 来源：[DEC-015 — Skill 定义为带执行契约的可复用业务能力包](../decisions/dec-015-contract-based-reusable-business-skills.md)

- **Skill 可能依赖 LLM、检索、文档解析和外部 Tool：** 一个 Skill 可组合 LLM 调用、确定性程序、RAG 检索、Tool 调用、人工审核逻辑中的一种或多种；Skill 在契约中需**显式声明**其工具与能力依赖（文档解析、关键词检索、语义检索、Schema 校验、风险规则、来源查询、LLM、用户确认等），不应隐式调用未声明的外部能力。
- **具体供应商与实现接口尚未确认：** Skill 所依赖的 LLM、检索、文档解析与外部 Tool 的具体供应商、接口，以及是否使用 Anthropic Skills / OpenAI Skills / MCP / LangChain Tools 等**均未决定**；这些依赖的边界与故障隔离待后续集成设计时讨论。

> 注：本节仅确认 Skill **可能依赖的能力类别**，**不**确认任何具体供应商、接口、第三方服务或 GitHub 仓库。

### 外部仓库角色区分（DEC-016，Accepted，2026-07-27）

> 来源：[DEC-016 — 优先研究成熟电商 Skills，并通过契约化改造后复用](../decisions/dec-016-external-skill-research-and-contract-based-adaptation.md)

- **区分两类外部仓库角色：**
  - **Workflow Base Repository（工作流基底仓库）：** 可能提供 / 参考显式工作流、状态管理、暂停与恢复、持久化、人工审核、局部重跑、RAG 集成、结构化输出、测试框架——**尚未选择**。
  - **Skill Donor Repository（Skill 供体仓库）：** 可能提供 / 参考电商业务 SOP、分析方法、输入输出模板、风险规则、行业经验、测试案例、可复用工具。一个供体仓库**不需要**承担整个工作流基底。
- **项目可采用「一个主工作流基底 + 多个外部 Skill 供体 + 项目自有的状态 / 证据 / 审核 / 可靠性契约」：** 复用外部内容须遵守 License、记录来源，并接入项目自己的 Workflow State（DEC-012）、证据标记（DEC-008）、审核与暂停（DEC-007）。
- **具体仓库与接口尚未确认：** 工作流基底仓库、是否实际集成、具体 GitHub 仓库组合、供应商接口**均未决定**；首轮三候选已全部完成评估（Candidate 1 `product-review-analysis` [DEC-017](../decisions/dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)、Candidate 2 `product-differentiation-shopify` [DEC-018](../decisions/dec-018-adapt-product-differentiation-for-positioning-skill.md)、Candidate 3 `ecommerce-visual-copywriting-skill` [DEC-019](../decisions/dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)，均 = Adapt，分别作为 Customer Insight Analysis / Product Positioning / 执行层 Brief 能力的研究与改造供体）；候选的 Adapt 仅为研究与改造方向，**不代表进入 MVP**。

> 注：本节仅确认**外部仓库角色区分**与复用约束；**不**确认任何具体基底仓库、GitHub 仓库组合、第三方服务或供应商接口。

### MVP 平台 Adapter 与共享能力集成面（DEC-020，Accepted，2026-07-28）

> 来源：[DEC-020 — MVP 采用四个核心业务 Skills 与一个小红书平台 Adapter](../decisions/dec-020-mvp-four-core-skills-and-xiaohongshu-adapter.md)

- **首个平台集成 / 适配点为 Xiaohongshu Brief Mapping Adapter：** 它将平台无关的 Marketing Brief 映射为小红书场景的结构化执行 Brief，是**适配层**而非平台 API / 发布集成。**自动发布、小红书 API 接入、抓取不进入首版 MVP**；平台官方知识（笔记结构 / 平台规范）作为按需检索的运营知识处理（承接 DEC-014）。
- **Skill 依赖面（DEC-015）已有具体 MVP 落点：** 四个 Core Skills（Product Intake & Fact Extraction / Customer Insight Analysis / Product Positioning / Marketing Brief Generation）+ Xiaohongshu Adapter 均可能依赖 LLM、文档解析、混合检索、Schema 校验、来源查询等共享能力；但每个 Skill 的**具体依赖、供应商与接口仍未确认**（承接 DEC-015）。
- **Risk Validation 为嵌入式集成：** 采用「确定性风险规则 + Marketing Brief 内部风险检查 + 按需检索当前运营 / 平台知识 + 人工审核」组合；**不**创建独立 Compliance Review Skill / 法律或平台审核 Agent。

> 注：本节仅确认 MVP **平台适配方向与共享能力集成面**；**不**确认小红书 API / 抓取 / 发布、平台官方知识具体来源、各 Skill 具体供应商与接口、向量数据库、模型 API、具体 GitHub 仓库组合。

### 未来受约束 Worker Runtime 边界（DEC-021，Accepted，2026-07-28）

> 来源：[DEC-021 — MVP 不采用 Multi-Agent 主架构，保留评测驱动的受约束并行 Worker 扩展](../decisions/dec-021-no-multi-agent-for-mvp-and-bounded-worker-extension.md)

- **未来可能接入 Worker Runtime：** 当出现真实并行需求（大批量评论分析 / 多竞品研究 / 多平台映射 / 独立评测）且对照评测证明收益超过成本时，可能在特定节点内部接入「中心化 Orchestrator + 受约束并行 Worker」。当前 MVP **不接入** Worker Runtime。
- **当前不选择具体 Multi-Agent / Worker 框架：** LangGraph / CrewAI / AutoGen / OpenAI Agents SDK / LangChain / 自研等任何具体 Multi-Agent 或 Worker 实现框架**均未确认、未选择**。
- **Worker 只能通过结构化输入输出与主工作流交互：** Worker 接收明确任务与有限输入、返回结构化输出、不控制主工作流、不直接修改最终状态、输出经主 Skill 汇总与校验、失败可单独重试、不影响其他 Worker 状态。Worker **不**通过自由对话 / Agent-to-Agent Messaging 与主工作流交互。

> 注：本节仅确认未来 Worker Runtime 的**集成边界与约束**；**不**确认 Worker 实现框架、是否进入 MVP、Multi-Agent 框架选型、独立 Evaluator 是否进 MVP、具体供应商 / 接口 / GitHub 仓库。

### 工作流框架与领域状态 / 配置 / Worker 集成边界（DEC-022，Accepted，2026-07-28）

> 来源：[DEC-022 — Workflow Framework Capability Requirements](../decisions/dec-022-workflow-framework-capability-requirements.md)

- **Domain State 不应绑定具体工作流框架：** 项目领域模型（如 `ProductFact` / `CustomerInsight` / `PositioningCandidate` / `MarketingBrief` / `SourceFragment`）应独立于框架，**不应只能**存在于某框架的 Message / Checkpoint / Agent Memory / Runtime-specific Object；目标是更换工作流框架时无需重写全部业务数据模型。框架的持久化 / Checkpointer / 数据库供应商**仍未确认**。
- **Skill Service 与 Workflow Node Adapter 分离：** 推荐结构为 `Workflow Node Adapter → Business Skill Service → LLM / Retrieval / Validator`；业务逻辑**不应**大量写入框架专属 Node API，以便单节点独立测试与未来更换框架（承接 DEC-015 Skill 显式声明工具依赖）。
- **模型与工具配置通过项目配置层注入：** 每个节点的模型 / Temperature / Timeout / Token Limit / 工具权限 / RAG 策略 / 重试策略 / Structured Output / Validator 属于**项目配置层**，**不应**被工作流框架硬编码。
- **Future Worker 只能通过结构化输入输出连接主流程：** 未来受约束 Worker（承接 DEC-021）只接收有限输入、返回结构化输出、不控制主工作流、不直接修改最终状态、输出经汇总校验；**不**通过自由对话 / Agent-to-Agent Messaging 与主流程交互。

> 注：本节确认工作流框架与领域状态 / 配置 / Worker 的**集成边界**；**不**选择具体工作流框架（LangGraph / OpenAI Agents SDK / LangChain / CrewAI / Temporal / 自研状态机）、数据库 / Checkpointer / 任务队列、模型供应商、工具接口、GitHub 基底仓库。

### LangGraph 与 Skill Service / Worker / 模型供应商集成边界（DEC-023，Accepted，2026-07-28）

> 来源：[DEC-023 — MVP 选择 LangGraph StateGraph 作为核心工作流运行方式](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)

工作流运行框架已选定 **LangGraph（StateGraph / Graph API）**。该框架与项目其它层的集成边界（承接 DEC-015 / DEC-021 / DEC-022）：

- **Workflow Node Adapter 与 Skill Service 分离：** Node Adapter 仅负责把 LangGraph State 转换为 Skill Input、调用 Skill Service、把 Skill Output 转换为 State Update、处理框架级配置与 Retry / Interrupt；**不应**包含大量业务逻辑。Skill Service 须能脱离 LangGraph 单独执行和测试。
- **LangGraph 只能通过结构化输入输出调用 Skill：** 主 Graph 经 Node Adapter 以结构化 IO 调用 Skill Service（`LangGraph Node Adapter → 框架无关 Skill Service → Domain Models / Repositories / LLM Gateway`）；不得把 Prompt / Schema / 业务校验硬编码在 Graph Builder 中、不得让所有业务逻辑写在 Node 中、不得让所有服务依赖 LangGraph RunnableConfig。
- **Skill 不直接控制主 Graph：** Skill 是业务能力层（承接 DEC-015），可拥有独立 Prompt / 模型配置 / 工具 / 输出 Schema，但**不**拥有独立流程控制权（不决定下一步阶段、不控制主 Graph 路由）；主流程路由由代码与状态决定，**不**经 LLM Supervisor 自由判断（承接 DEC-021）。
- **Worker 不直接写入正式 Workflow State：** 未来受约束并行 Worker（承接 DEC-021）只接收有限输入、返回结构化临时结果、由主节点聚合校验、**不**控制主工作流、**不**直接修改最终 Workflow State、**不**通过自由对话 / Agent-to-Agent Messaging 与主流程交互。
- **模型供应商通过 LLM Gateway 隔离：** 模型与工具配置属**项目配置层**（每个节点的模型 / Temperature / Timeout / Token Limit / 工具权限 / RAG 策略 / 重试策略 / Structured Output / Validator，承接 DEC-022），由 LLM Gateway 与外部模型供应商交互；**不**被工作流框架硬编码，**不**强绑单一模型供应商。

> 注：本节确认 **LangGraph 选定后与 Skill Service / Worker / 模型供应商的集成边界**；**仍待确认** Node Adapter 接口、Skill Service 接口、LLM Gateway 接口、Human Review Payload、API / Python 后端框架、具体模型供应商、Checkpointer 类型、数据库、向量数据库、检索组件、LangSmith / Observability 工具、基底仓库。本节**不**选择 Checkpointer / 数据库 / FastAPI / Next.js / LangSmith / 模型供应商 / Embedding / 向量数据库。

### LangGraph State 与 Domain Objects / Checkpointer 与 Business Repository 集成边界（DEC-024，Accepted，2026-07-28）

> 来源：[DEC-024 — Workflow State 采用任务级业务身份、版本化领域状态与紧凑 LangGraph State](../decisions/dec-024-versioned-domain-state-and-compact-langgraph-state.md)；概念规格：[../specs/workflow/workflow-state-specification.md](../specs/workflow/workflow-state-specification.md)。

承接 DEC-023（Checkpointer 仅执行恢复、业务数据库为 Current Truth），DEC-024 进一步确认 LangGraph State、Domain Objects、Checkpointer 与 Business Repository 之间的集成边界：

- **LangGraph State 通过 Version ID 引用 Domain Objects：** Workflow State 保持紧凑、引用为主（`compact / serializable / recoverable / reference-oriented`）；State 中保存 `facts_version_id` / `insights_version_id` 等版本指针，**不**复制完整 `facts[]` / 业务内容。完整 PDF / 图片二进制 / 评论原文 / Embedding / 向量 / 知识库 / 全部历史版本存 Business Database / Object Storage / Retrieval Index / Run Log。
- **Node Adapter 负责加载正式 Domain Objects：** 节点执行需要正式业务内容时，由 Node Adapter（承接 DEC-022 / 023 的 `Node Adapter → 框架无关 Skill Service → Domain Models / Repositories / LLM Gateway`）按 Version ID 从 Business Repository 加载正式 Domain Objects，再转换为 Skill Input；**不**把加载业务对象的职责交给 LangGraph Runtime 或 Skill 内部隐式读取。
- **Skill Service 不直接读取 LangGraph Checkpoint：** Skill Service 只接收 Node Adapter 传入的结构化输入、返回结构化输出（承接 DEC-015 / DEC-023）；**不**直接访问 Checkpointer / Graph State Snapshot / State History；执行恢复与快照由 LangGraph Layer 负责，业务读写由 Business Repository 负责。
- **Frontend 不直接读取 Checkpointer 作为正式业务结果：** 前端读取正式业务内容时以 Business Database 为主要数据来源（Product Query Rule）；**不得**将 LangGraph Checkpoint 数据库直接作为产品查询 API / 唯一业务数据库 / 唯一 Current Truth / 唯一版本系统 / 唯一审计系统。前端交互态（Interaction State）由 Domain + Workflow + Runtime 组合派生。
- **Checkpointer 与 Business Repository 使用独立接口：** LangGraph Checkpointer（执行快照 / Interrupt / Resume / State History / Runtime Recovery）与 Business Repository（Task / Inputs / Sources / Fragments / 各层 Versions / Review Decisions / Pointers / Invalidation / User Mods / Audit）为**两套独立职责与接口**；Node Adapter / Skill Service 通过 Business Repository 读写正式业务数据，通过 LangGraph Runtime 触发 / 恢复执行，二者**不**共用同一接口或同一存储作为唯一来源。
- **业务版本和 Checkpoint 版本不得混用：** 业务版本（`version_id`，由版本化 Domain Objects 产生，`candidate / current / superseded / invalid / rejected`）与 Checkpoint 版本（`checkpoint_id`，Runtime 执行快照）属不同层、不同语义；`checkpoint_id` **不作**产品主要业务 ID、**不**替代业务版本 ID、**不**作前端主要导航身份；Current Truth 以业务版本指针为准，**不**以 Checkpoint 位置推断业务有效性。

> 注：本节确认 **LangGraph State 与 Domain Objects / Checkpointer 与 Business Repository 的集成边界**（承接 DEC-023 + DEC-024）；**仍待确认** Node Adapter 接口、Skill Service 接口、Business Repository 接口、Checkpointer 类型、数据库、Object Storage / Retrieval Index 供应商、API / Python 后端框架、并发控制、事务边界。本节**不**创建正式业务实现，**不**选择 Checkpointer / 数据库 / Object Storage / 向量数据库 / ORM。

### Skill / LLM / Retrieval / Evidence Validator / Business Repository / Frontend 与来源证据集成边界（DEC-025，Accepted，2026-07-28）

> 来源：[DEC-025 — 采用版本化来源、可定位 Fragment 与显式 Evidence Link 的证据架构](../decisions/dec-025-versioned-sources-fragments-and-evidence-links.md)；概念规格：[../specs/evidence/source-and-evidence-specification.md](../specs/evidence/source-and-evidence-specification.md)。Amends DEC-008 / DEC-014。

承接 DEC-014（RAG 仅检索与证据提供）、DEC-015（Skill 显式声明工具依赖）、DEC-023 / DEC-024（Node Adapter 加载 Domain Objects、Skill 不读 Checkpoint、Business Repository 读写正式业务数据），DEC-025 进一步确认来源与证据系统各组件之间的集成边界：

- **Skill 只能引用 Evidence Package 中允许的 Fragment ID：** 每次 Skill 执行使用可复现的 Evidence Package（`candidate_fragments[]` / `verified_facts[]` / `dataset_statistics[]` / `known_conflicts[]` / `evidence_limitations[]`）；Skill 输出中的 `fragment_id` / `source_version_id` 必须来自该 Evidence Package 的允许集合，**不**得引用集合外的 Fragment。
- **LLM 不得自由生成 Source ID：** LLM **不**得自由生成 `source_id` / `source_version_id` / `fragment_id` / 文件名 / 页码 / 评论 ID / URL / 引用位置；模型只能从系统提供的候选 Fragment ID 集合中选择；**禁止**只保存自然语言引用而无真实 Fragment ID 与 Locator。
- **Retrieval Service 返回 Candidate Fragments：** 检索（按需混合 RAG，承接 DEC-014）返回的是 `Retrieved Fragment` / `Candidate Evidence`，**不**自动成为正式证据；须经 Permission / Source Version / Existence / Relevance 校验后才可能成为 Selected Evidence。
- **Evidence Validator 负责正式引用校验：** 确定性 Validator 校验引用是否成立（ID 是否存在 / 是否属当前任务 / 是否来自允许 Source Scope / Source Version 是否可用 / 是否本次 Evidence Package 候选 / 是否重复 / 是否已失效 / Locator 是否存在）；只有校验通过的引用才创建 Evidence Link 进入正式业务对象。
- **Business Repository 保存 Evidence Links：** Evidence Link 是独立关系对象（`Versioned Domain Object ↔ Fragment`），由 Business Repository 保存（承接 DEC-024 Business Database 存 Sources / Source Fragments / Evidence Relationships）；**不**以 Checkpoint / LangGraph State 作为正式业务证据存储。
- **Frontend 通过业务 API 获取来源和原文定位：** 前端展示结论的 Evidence Class / 来源数量 / 原文摘录 / Locator / 样本范围 / 证据限制 / 来源冲突等时，通过业务 API（以 Business Database 为准）读取，**不**直接读取 Checkpointer / Retrieval 内部存储。
- **Skill 不直接读取整个来源数据库：** Skill 通过 Evidence Package 获得受限、可复现的证据输入快照（限制模型可见证据范围、支持独立测试与确定性引用校验），**不**直接接触整个来源数据库 / 检索索引 / 向量库。
- **当前商品和竞品 Source Scope 必须隔离：** `source_scope`（current_product / competitor_product / platform_knowledge / internal_business）显式隔离；竞品资料**不能**直接证明当前商品事实；所有来源对象关联当前 Task 或合法 Workspace，跨任务召回私有资料必须拒绝（即使 Fragment ID 真实存在，不属于当前授权范围也必须拒绝引用）。

> 注：本节确认**来源与证据系统各组件的集成边界**（承接 DEC-014 / 015 / 023 / 024）；**仍待确认** Evidence Validator 接口、Retrieval Service 接口、Evidence Package 构建接口、Business Repository 接口、Fragment 切分规则、Parser / OCR / Embedding / 向量数据库 / Reranker / Top-K、Source / Fragment ID 格式、Web Scraper / Review Importer、官方平台知识来源、前端 Evidence UI、正式 API。本节**不**创建 Parser / RAG / Embedding / Vector Store / Evidence Validator 代码 / 正式 API，**不**选择 PostgreSQL / MongoDB / Elasticsearch / pgvector / Pinecone / Weaviate / Chroma / Embedding 模型 / Reranker / PDF Parser / OCR Provider。

### Product Intake & Fact Extraction Skill 与来源证据 / Validator / Repository / 下游 Skill 集成边界（DEC-026，Accepted，2026-07-28）

> 来源：[DEC-026 — Product Intake & Fact Extraction Skill 采用分层输入完整度、零无来源事实与冲突暂停契约](../decisions/dec-026-product-intake-and-fact-extraction-skill-contract.md)；概念 Skill Spec：[../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)。Amends DEC-005。

承接 DEC-014（RAG 返回 Candidate Evidence）、DEC-015（Skill 显式声明工具依赖）、DEC-023 / DEC-024（Node Adapter 加载 Domain Objects、Skill 不读 Checkpoint、Business Repository 读写正式业务数据）、DEC-025（Evidence Package + Evidence Validator + Evidence Link），DEC-026 进一步确认首个 Core Skill 的集成边界：

- **Skill 经 Evidence Package 获得当前商品 Source Version 输入：** Skill 输入为 Task context + 当前商品 Source Versions（`source_scope = current_product`）+ 可选增强来源（承接 DEC-025 Evidence Package：`candidate_fragments[]` / `verified_facts[]` / `dataset_statistics[]` / `known_conflicts[]` / `evidence_limitations[]`）；竞品资料可登记为后续阶段可用来源，但**不**用于证明当前商品属性；Skill **不**直接读取整个来源数据库 / 检索索引 / 向量库。
- **输出 Facts Version 须经确定性 Validator 15 项校验才写入 Business Repository：** Skill 输出（Intake Assessment / Fact Candidates / Claims to Verify / Conflicts & Limitations / Stage Decision）中所有正式 Fact 须经 15 项硬校验（每个 Fact 有 Supporting Fragment / Fragment ID 真实存在 / 属当前 task_id / Scope 为 current_product 或合法 Manual Input / Source Version 可用 / 未用竞品来源 / 数值可定位 / 单位转换合法 / raw_value 与原文一致 / Marketing Expression 未写成 Fact / Documented Claim 未标 Certified / 冲突值未同时成 Current Truth / 符合 Schema / 必填身份存在 / 无虚构 ID），校验通过才写入 Business Repository 的 Facts Current Truth；硬校验失败**不得**写入（承接 DEC-025 Evidence Validator）。
- **关键冲突创建 SourceConflict 并触发暂停交 Human Review：** Numeric / Material / SKU or Variant / Certification / Usage Restriction 冲突**不得**由模型自行解决，创建正式 `SourceConflict`（承接 DEC-025）并触发 `waiting_input` / `paused`，交用户在统一 Human Review Gate（DEC-007）处理；MVP **不**建立复杂来源优先级。
- **下游 Skill 消费 Facts Version：** Customer Insight Analysis / Product Positioning 等下游 Skill 以 Facts Version（版本化 Domain Object，承接 DEC-024）为输入；Fact Layer 错误会传播至所有下游阶段，故 Fact 须可追溯 / 可校验 / 可版本化。
- **业务资料不足与技术失败分离：** `waiting_input` / `paused`（业务问题，经业务 API / Human Review 处理）与 `failed`（Parser 异常 / 数据库失败 / 模型连续无法输出合法 Schema / Evidence Validator 错误 / 文件损坏，技术故障）严格分离；业务资料不足**不得**误标为技术失败。
- **Frontend 通过业务 API 读取 Facts / Conflicts / Stage Decision：** 前端展示输入完整度 / Facts / 待验证声明 / 冲突 / 缺失信息 / 证据限制 / 阶段决策时，通过业务 API（以 Business Database 为准）读取，**不**直接读取 Checkpointer / Retrieval 内部存储。

> 注：本节确认**首个 Core Skill 与来源证据 / Validator / Repository / 下游 Skill / Human Review 的集成边界**（承接 DEC-005 / 007 / 014 / 015 / 023 / 024 / 025）；详细 Skill 契约见 [../specs/skills/product-intake-and-fact-extraction-skill.md](../specs/skills/product-intake-and-fact-extraction-skill.md)（仅概念）。**仍待确认** Skill Service 接口、Node Adapter 接口、Evidence Validator 接口、Evidence Package 构建接口、Business Repository 接口、Parser / OCR / 单位库、Verification Status 枚举名、最终 Fact Schema、前端表单 UI、正式 API。本节**不**创建正式 Prompt / Skill 代码 / LangGraph Node / 数据库表 / Parser / OCR / Unit Library / 前端表单 / 风险规则实现，**不**选择模型 / Parser / OCR Provider / 数据库 / ORM / 文件格式实现 / 单位处理库。

### Customer Insight Analysis Skill 与 Evidence Package / 确定性统计服务 / Validator / Repository / 下游 Skill 集成边界（DEC-027，Accepted，2026-07-28）

> 来源：[DEC-027 — Customer Insight Analysis Skill 采用证据模式与降级假设模式，并禁止虚构用户原声和检索样本频率外推](../decisions/dec-027-customer-insight-analysis-skill-contract.md)；概念 Skill Spec：[../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)。Amends DEC-017。

承接 DEC-014（RAG 返回 Candidate Evidence）、DEC-015（Skill 显式声明工具依赖）、DEC-023 / DEC-024（Node Adapter 加载 Domain Objects、Skill 不读 Checkpoint、Business Repository 读写正式业务数据）、DEC-025（Evidence Package + Evidence Validator + Evidence Link + Source Scope 隔离）、DEC-026（上游 Facts Version），DEC-027 进一步确认第二个 Core Skill 的集成边界：

- **Customer Insight Skill 只能读取当前 Evidence Package：** Skill 输入为可复现的 Customer Evidence Package（`candidate_fragments[]` / `verified_facts[]` / `dataset_statistics[]` / `known_conflicts[]` / `evidence_limitations[]`，承接 DEC-025）；Skill 输出中的 `fragment_id` / `source_version_id` 必须来自该 Evidence Package 的允许集合，**不**直接读取整个来源数据库 / 检索索引 / 向量库；跨任务召回私有资料必须拒绝。
- **统计比例由确定性统计服务生成：** 正式比例 / 频率（如「120 条评论中 18 条提到漏水，占 15%」）**必须**由确定性统计服务产生，并记录数据集版本 / 评论总数 / 去重规则 / 分子记录 ID / 分母 / 主题分类规则版本 / 统计时间 / 统计方法，作为独立 `Dataset Statistic` 对象写入 Business Repository。
- **LLM 不直接计算正式总体频率：** LLM 可辅助主题识别 / 相似归类 / 场景分类 / 正负判断 / 需求归纳，但**不得**自行计算或推断总体比例；**禁止**根据 RAG Top-K 召回结果计算或推断总体频率（Top-K 表示与 Query 相关的候选证据，非总体样本的完整或随机分布）。
- **用户原声引用必须通过 Evidence Validator：** 直接用户原声必须来自真实 Fragment（可追踪 Fragment ID / Source / Source Version / Record / Locator / 上下文）；模型**不得**自造引语、拼接虚构原声、改写后冒充直接引用、把模型概括伪装原文、把竞品评论冒充当前商品用户原声、把翻译伪装原语言引用；所有引用须经确定性 Evidence Validator 校验通过后才创建 Evidence Link 进入 Insights Version（承接 DEC-025）；`Original Customer Language` 与 `Model Summary` 必须分别展示。
- **下游 Positioning Skill 必须读取 Insight 的 Evidence Class 和 Limitations：** Product Positioning 以 Insights Version 为输入；运行于 `valid_with_limitations`（当前商品评论较少 / 只有竞品评论 / 只有用户提供的目标人群 / 缺少完整数据集 / Degraded Hypothesis Mode）时，Positioning Skill **必须**读取并展示 Insight 的 `evidence_class` 与 `limitations[]`，**不**得把 Hypothesis 当作 Evidence-backed Insight 使用。
- **Competitor Source Scope 不得转换为当前商品用户事实：** `source_scope = competitor_product` 的用户反馈可支持品类共性问题 / 用户期待 / 竞品弱点 / 差异化机会假设，但**不能**直接证明当前商品用户具有同样体验；竞品 Fragment 不得归因为当前商品用户证据（承接 DEC-025 Source Scope 隔离 + Validator 第 4 / 18 项）。
- **Insights Version 须经 Validator 18 项才写入 Insights Current Truth：** LLM 输出写入正式 Insights Version 前须经 18 项硬校验（Fragment ID 真实存在 / 属当前 task_id / Source Version 可用 / 当前商品与竞品 Scope 未混淆 / 原声来自原始 Fragment / 直接引语未被改写 / Dataset Statistic 可回溯完整数据集 / 分子分母合法 / Top-K 未当总体统计 / 单条反馈未表达为普遍共识 / 无直接证据结论标为 Hypothesis / Supporting Evidence 语义相关 / Contradicting Evidence 未误标为支持 / 符合 Schema / 引用 Facts Version 当前有效 / 无虚构用户细分 / 无虚构用户语言 / 无竞品体验写成当前商品体验），校验通过才写入 Business Repository 的 Insights Current Truth；硬校验失败**不得**写入（承接 DEC-025 Evidence Validator）。
- **业务证据不足 ≠ 技术失败：** `waiting_input`（用户要求评论 / 访谈分析但未提供资料且拒绝假设模式）/ `paused`（当前与竞品评论严重混淆 / 数据权限异常 / 错误商品评论 / 大量重复污染异常 / 主要证据来源撤回）与 `failed`（评论解析失败 / 模型多次无法输出合法 Schema / 统计服务异常 / Evidence Validator 内部错误 / 持久化失败）严格分离；业务证据不足**不得**误标为技术失败（承接 DEC-026 的失败边界分离）。
- **Frontend 通过业务 API 读取 Insights / Themes / Limitations / Stage Decision：** 前端展示 Evidence Coverage / Themes / Insights / Hypotheses / 用户原声 / 反向证据 / 数据集统计 / 限制 / 阶段决策时，通过业务 API（以 Business Database 为准）读取，**不**直接读取 Checkpointer / Retrieval 内部存储。

> 注：本节确认**第二个 Core Skill 与 Evidence Package / 确定性统计服务 / Evidence Validator / Business Repository / 下游 Positioning Skill / Human Review 的集成边界**（承接 DEC-014 / 015 / 023 / 024 / 025 / 026）；详细 Skill 契约见 [../specs/skills/customer-insight-analysis-skill.md](../specs/skills/customer-insight-analysis-skill.md)（仅概念）。**仍待确认** Skill Service 接口、Node Adapter 接口、确定性统计服务接口、Evidence Validator 接口、Evidence Package 构建接口、Business Repository 接口、Dataset Statistic 记录格式、Customer Language Locator Schema、评论主题分类表、聚类算法、情感分析实现、前端 Insight UI、正式 API。本节**不**创建正式评论分析 Prompt / Skill 代码 / LangGraph Node / 评论聚类代码 / Embedding / 评论导入器 / 数据库表 / 前端页面 / 情感分析实现，**不**选择模型 / Embedding / 聚类算法 / 情感分析工具 / 数据库 / 评论文件格式 / 最低评论数量 / 频率阈值。

### Product Positioning Skill 与 Facts / Insights / Validator / Repository / Human Review / 下游 Marketing Brief Skill 集成边界（DEC-028，Accepted，2026-07-28）

> 来源：[DEC-028 — Product Positioning Skill 采用多候选、证据约束与强制人工决策契约](../decisions/dec-028-product-positioning-skill-contract.md)；概念 Skill Spec：[../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)。Amends DEC-018。

承接 DEC-014 / 015 / 023 / 024 / 025 / 026 / 027，DEC-028 进一步确认第三个 Core Skill 的集成边界：

- **Positioning Skill 只能读取当前有效 Facts 和 Insights：** Skill 输入须为当前有效 Facts Version（`Fact Stage = valid`）和当前有效或 `valid_with_limitations` 的 Insights Version（必须读取其 Evidence Class / Evidence Coverage / Supporting·Contradicting Evidence / Evidence Limitations / Hypothesis 标识 / Source Scope）；Skill 通过可复现输入快照（Facts Version ID / Insights Version ID / 可选竞品 Evidence Set Version）读取，**不**直接读取整个来源数据库 / 检索索引 / 向量库；跨任务召回私有资料必须拒绝（承接 DEC-025 Evidence Package + DEC-027 限制传播）。
- **Proof Point 通过 Fact ID 追溯：** 所有 Proof Point 必须成立 `Proof Point → Valid Fact → Evidence Link → Fragment → Source Version`；模型**不得**自由生成 Fact ID / Fragment ID / Source Version ID，只能从当前 Evidence Package 允许集合选择并经确定性 Evidence Validator 校验；无 Source Version 的证明材料不得进入候选（承接 DEC-025 / DEC-026）。
- **Competitor Evidence 只能用于 Gap 和 Context：** `source_scope = competitor_product` 的证据可支持品类共性问题 / 竞品弱点 / 差异化机会假设（Evidence-supported Gap / Opportunity Hypothesis），但**不能**证明当前商品拥有某项能力，**不得**进入当前商品 Proof Point；竞品资料有限时只能输出 Opportunity Hypothesis，**不得**表示为已验证市场空白或确定性竞品优势；禁止将竞品功能写入当前商品 Proof Point（承接 DEC-025 Source Scope 隔离 + Validator 第 6 / 12 项）。
- **Positioning Skill 不能直接创建 Approved Strategy：** Skill 只输出 Positioning Candidates / Comparison Matrix / Recommendation（仅建议）/ Assumptions / Evidence Limitations / Strategic Risks / Human Review Package / Workflow Decision；模型推荐**不**自动成为 Approved Strategy，**不**直接写 Current Truth 为最终战略。
- **Approved Strategy Version 由 Human Review Service 形成：** Human Review（在统一 Human Review Gate，承接 DEC-007）展示候选 + 全部要素 + Supporting Facts / Insights / Competitor Evidence / Assumptions / Limitations / Risks + 模型推荐理由；允许操作 select / edit / merge[合并后必须重新通过 Validator] / reject / request_more_information；审核完成形成 **Approved Strategy Version** 写入 Business Repository（承接 DEC-024 版本化 Domain Object + Current Truth Pointer）。
- **Marketing Brief Skill 只能读取 Approved Strategy：** 下游 Marketing Brief Generation 的必要输入是 Approved Strategy Version（而非未审核的候选）；Positioning 候选生成后工作流**必须**进入 Human Review，**不得**直接进入 Marketing Brief Generation。
- **业务证据不足 ≠ 技术失败：** `waiting_input`（用户要求竞品差异定位但无竞品资料 / 事实不足以形成价值差异 / 缺用户明确业务约束）/ `ready_for_review_with_limitations`（无直接用户反馈 / 只有竞品用户证据 / Target Segment 假设 / 市场 Gap 未验证）/ `paused`（关键 Fact 失效 / 错误 SKU / 当前商品与竞品资料混淆 / 高风险无法验证功效声明 / 主要竞品来源撤回 / 上游未解决严重冲突）与 `failed`（模型连续无法输出合法 Schema / Evidence Package 构建失败 / Validator 内部错误 / 数据库存储失败 / 版本写入失败）严格分离；业务证据不足**不得**误标为技术失败（承接 DEC-026 / DEC-027 的失败边界分离）。
- **Validator 20 项校验、硬校验失败不进入 Human Review：** Positioning Candidates 进入 Human Review 前须经 20 项硬校验（Facts / Insights Version 有效 / Fact·Insight ID 真实存在 / Proof Point 可回溯有效 Fact / Competitor Evidence 未表示当前商品能力 / 无无来源数值认证性能声明 / Hypothesis 未表示为用户共识 / 未虚构人口统计特征 / 比较级最高级有可靠依据 / Reasons to Believe 与商品事实语义相关 / Differentiation 未超出竞品证据范围 / 候选间实质差异 / 候选数量在范围内 / Evidence Limitations 已传播 / Source Version 可用 / 未用失效上游结果 / 符合 Schema / Proof Point 不含 Marketing Expression / Approved Strategy 未自动创建），校验通过才进入 Human Review 并可写入候选；硬校验失败**不得**进入审核、**不得**自动创建 Approved Strategy（承接 DEC-025 Evidence Validator）。
- **Frontend 通过业务 API 读取 Candidates / Matrix / Recommendation / Limitations / Stage Decision：** 前端展示 Positioning Candidates / Comparison Matrix / Recommendation / Assumptions / Evidence Limitations / Strategic Risks / 阶段决策时，通过业务 API（以 Business Database 为准）读取，**不**直接读取 Checkpointer；Human Review 页面通过业务 API 读取候选并提交审核决策。

> 注：本节确认**第三个 Core Skill 与 Facts / Insights / Validator / Repository / Human Review / 下游 Marketing Brief Skill 的集成边界**（承接 DEC-014 / 015 / 023 / 024 / 025 / 026 / 027）；详细 Skill 契约见 [../specs/skills/product-positioning-skill.md](../specs/skills/product-positioning-skill.md)（仅概念）。**仍待确认** Skill Service 接口、Node Adapter 接口、Evidence Validator 接口、Evidence Package 构建接口、Business Repository 接口、Human Review Service / Gate 接口、Approved Strategy Version Schema、Positioning Schema、Comparison Matrix 最终字段、Human Review Payload、候选相似度算法、排序公式、正式 API。本节**不**创建正式 Positioning Prompt / Skill 代码 / LangGraph Node / Human Review 页面 / 数据库表 / 候选相似度算法 / 排序算法 / 市场研究代码，**不**选择模型 / Prompt Framework / 竞品数量 / 排序公式 / Human Review UI 技术 / 数据库 / 高风险比较声明规则实现。（Human Review and Approved Strategy Contract 已由 DEC-029 在概念层确认；具体 Review UI / Resume / Draft 自动保存等仍属 NOT READY。）

### Human Review Service / LangGraph Interrupt / Frontend / Approved Strategy Service 与下游 Marketing Brief Skill 集成边界（DEC-029，Accepted，2026-07-28）

> 来源：[DEC-029 — Human Review 采用版本化审核包、结构化用户决策与事务化 Approved Strategy 契约](../decisions/dec-029-human-review-and-approved-strategy-contract.md)；概念规格：[../specs/workflow/human-review-and-approved-strategy-contract.md](../specs/workflow/human-review-and-approved-strategy-contract.md)。Amends DEC-007 / DEC-024。

承接 DEC-007（单审核 Gate）、DEC-023 / DEC-024（LangGraph Interrupt / Resume + Checkpointer 与业务库分离）、DEC-025（Proof Point 追溯）、DEC-028（Positioning 只输出候选），DEC-029 进一步确认 Human Review 与 Approved Strategy 各组件的集成边界：

- **Positioning Skill 只创建候选、不创建 Approved Strategy：** Product Positioning Skill（承接 DEC-028）输出 Positioning Candidates / Recommendation（仅建议）/ Human Review Package / Workflow Decision；**不得**直接创建 Approved Strategy、**不得**直接写 Current Truth 为最终战略。
- **Review Service 创建固定上游版本的 Review Package：** Review Service 构建固定上游版本的输入快照（Facts / Insights / Positioning / Source Set Versions / Candidates / Evidence Limitations）；审核开始后**不得**后台静默替换；上游版本变化 → 旧 Package 标 `superseded`、旧提交被阻止。
- **LangGraph 负责 Interrupt 暂停与 Resume 恢复：** 工作流在生成候选后进入 Human Review Interrupt（承接 DEC-023），等待用户结构化决策后 Resume；LangGraph **仅**负责暂停与恢复，**不替代**业务事务、**不替代** Approved Strategy Service、**不替代** Review Business Repository。
- **Frontend 提交结构化 Review Decision：** 前端通过业务 API读取不可变 Review Package 和 revision-guarded full-snapshot Review Draft；Candidate select / edit / merge / reject 只是 Draft，不等于批准。`submit` / `request-more-information` / `reject-all-and-request-regeneration` / `withdraw-approved-strategy` 是不同 typed Outcome；前端**不**直接读取 Checkpointer，也不得在 Submit 成功后另发第二个 Resume。
- **Approved Strategy Service 执行原子提交事务：** submit 锁定并校验 Package、Draft revision、上游版本、必审项、Evidence / Proof Point / Hypothesis / Limitation 后，在同一事务中创建 Review Decision 与 Approved Strategy Version、更新 Current Truth / Stage、写 Audit / Idempotency Result，并创建唯一 Durable Resume Work Intent；任一步失败不创建版本、不更新 Pointer、不调度 continuation。首次结果与同 Key 重放分别按 DEC-064 返回 `201` / `200`，并引用同一 continuation Receipt / Run。
- **Marketing Brief Skill 只能读取 Approved Strategy Version：** 下游 Marketing Brief Generation 的必要输入是 Approved Strategy Version（承接 DEC-024 版本化 Domain Object + Current Truth Pointer）；**不得**读取未经审核的 Positioning Candidate、**不得**读取 Strategy Draft；Evidence Limitations 须由 Marketing Brief 继续传播。
- **LLM 不得自动提交审核：** LLM 仅可辅助（解释候选差异 / 润色编辑 / 检查一致性 / 提示遗漏假设风险 / 总结修改）；**禁止**自动选择候选 / 自动接受 Hypothesis / 自动删除 Evidence Limitation / 自动批准 / 自动提交 / 把无证据内容升级为 Proof Point / 绕过 Validator（承接 DEC-011 受约束 LLM）。
- **Checkpointer 不替代 Review Business Repository：** 审核历史 / Review Decisions / Approved Strategy Versions / Withdrawal Record / Audit Record 由 Business Repository 保存（承接 DEC-024）；Checkpointer 仅承载 Interrupt / Resume / 执行快照，**不**作正式审核业务数据存储、**不**作 Current Truth。

> 注：本节确认**Human Review 与 Approved Strategy 各组件的集成边界**；DEC-064 已冻结不可变 Package、full-snapshot Draft、显式 Outcome 和 Submit + Durable Resume Work Intent 原子 continuation 的公共协议，DEC-066 已冻结 OpenAPI operation / schema closure；Repository、Transaction、UI 与 Runtime 实现均未授权。首个 Goal 不建设审核权限系统或多人协作审核。

### Marketing Brief Generation Skill 与 Approved Strategy / Proof Point / 下游 Xiaohongshu Adapter 集成边界（DEC-030，Accepted，2026-07-28）

> 来源：[DEC-030 — Marketing Brief Generation 采用 Approved Strategy 锁定、平台无关信息架构与证据限制传播契约](../decisions/dec-030-marketing-brief-generation-skill-contract.md)（Skill Contract / Marketing Architecture；Amends DEC-006 + DEC-019）。

- **Marketing Brief Skill 只能读取当前有效 Approved Strategy：** 不得用未审核 Positioning Candidate / Strategy Draft / Model Recommendation / 已撤回或已失效 Approved Strategy / 历史旧版本 Strategy 作为正式战略输入（承接 DEC-029）。
- **Positioning Candidate 不能绕过 Review：** 只有经 DEC-029 Human Review submit + Validator 形成的 Approved Strategy Version 才能进入 Marketing Brief；Candidate / Draft 不得直接进入。
- **Brief Skill 不能改变 Strategy：** Strategy Lock 六字段（target_segment / usage_context / job_or_core_need / category_frame / value_proposition / differentiation）受控；若须改变返回 `strategy_change_required` 重新进入 Human Review，不写入新 Brief Current Truth。
- **Proof Points 通过 Fact ID 追溯：** 每个 Proof Point 须建立 `Proof Point → Valid Fact → Evidence Link → Fragment → Source Version` 追溯链（proof_point / fact_id / supporting_fragment_ids[] / source_version_id / approved_wording），不得扩大检测认证性能范围（承接 DEC-025 / DEC-028 / DEC-029）。
- **Brief 输出保持平台无关：** 不含小红书标题 / 正文 / Emoji / Hashtags / 封面文字 / 平台字数 / 热词 / 发布格式 / 最终广告文案；只含 message_priority / content_angles / tone / proof_points / risk_constraints / CTA objective / platform_adaptation_rules。
- **Xiaohongshu Adapter 只能映射 Brief：** 可改变表达结构，但不得改变 Audience / Core Message / Benefit Hierarchy / Proof Points / Evidence Limitations / Prohibited Claims / Approved Strategy。
- **Brief 修改会使 Xiaohongshu Mapping 失效：** 用户编辑 → 新 Brief Version + 保留原模型版本 + 重跑 Validator + 更新 Pointer；承接 DEC-009，Brief 修改不使 Facts / Insights / Positioning / Approved Strategy 失效但使 Xiaohongshu Mapping 失效。
- **Strategy Change 必须返回 Human Review：** Brief 生成或编辑若须改变 Target Segment / Value Proposition / Differentiation / Approved Proof Point 等，返回 `strategy_change_required`，不得绕过 DEC-029。

> 注：本节确认**Marketing Brief Generation Skill 的集成边界**（只读 Approved Strategy / Candidate 不绕过 Review / 不改 Strategy / Proof Point 通过 Fact ID 追溯 / 平台无关 / Xiaohongshu 只映射 Brief / Brief 修改使 Mapping 失效 / Strategy Change 回 Human Review；承接 DEC-006/009/015/019/020/024/025/028/029）；概念 Skill Spec 见 [../specs/skills/marketing-brief-generation-skill.md](../specs/skills/marketing-brief-generation-skill.md)（仅概念）。**仍待确认** 该 Skill 最终 Marketing Brief Schema / 接口 / Prompt / 代码 / LangGraph Node 对应、Content Angle 分类表、Tone 模板、Brand Guidelines 解析、风险词库、CTA 分类、Brief UI、Risk Validator 实现、Xiaohongshu Brief Mapping Adapter Contract（已由 DEC-031 确认，见下节）。本节**不**创建正式 Brief Prompt / Skill 代码 / LangGraph Node / Brief UI / 数据库表 / Risk Validator 实现 / Brand Guideline Parser / 平台内容生成器，**不**选择模型 / Prompt Framework / Tone 模板 / 风险词库 / CTA 分类 / 前端框架 / 数据库。

### Xiaohongshu Brief Mapping Adapter 与 Marketing Brief / Platform Policy Snapshot / 下游 Final Copy 集成边界（DEC-031，Accepted，2026-07-29）

> 来源：[DEC-031 — Xiaohongshu Brief Mapping Adapter 采用 Brief 锁定、版本化平台政策快照、真实体验边界与方向化输出契约](../decisions/dec-031-xiaohongshu-brief-mapping-adapter-contract.md)（Platform Adapter Contract / Platform Architecture；Amends DEC-004 + DEC-020）。概念 Platform Adapter Spec 见 [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)。

- **Adapter 只能读取当前有效 Marketing Brief：** 不得用未审核 Positioning Candidate / Strategy Draft / 未审核 Marketing Brief 草稿或旧版本 Brief；不得直接修改 Approved Strategy 或创建新 Proof Point（承接 DEC-030）。
- **Platform Policy Snapshot 版本化且每次记录：** 平台政策为外部、随时间变化的来源；Adapter 不得在 Prompt 硬编码长期有效规则，每次执行记录 `policy_snapshot_id` / `policy_version`；Snapshot 失效或不可用返回 `platform_policy_update_required`，不得静默使用过期规则（承接 DEC-025）。
- **Account and Campaign Context 为输入：** Adapter 读取 account_type / content_relationship / commercial_context / campaign_objective / available_asset_types[]，输出 review_route_notes / required_qualification_notes / commercial_disclosure_notes；不代替平台判定审核结果、不保证审核通过、不隐藏商业性质。
- **Adapter 不能修改 Brief：** 若映射须改 Audience / Core Message / Benefit Hierarchy / Proof Point / Approved Strategy，返回 `brief_change_required` 交回上游 Marketing Brief，不静默修改 Brief、不写入新 Execution Brief Current Truth。
- **Customer Language 必须来自真实 Fragment：** 真实用户原声须关联真实 Fragment（fragment_id / source_scope / quote_type / locator）；竞品语言不得展示为当前商品用户评价；禁止虚构体验 / 闺蜜推荐 / 伪造素人身份（承接 DEC-025 / DEC-027）。
- **Execution Brief 须经 Validator 才写入 Current Truth：** 确定性 Validator 28 项为写入 Execution Brief Current Truth Pointer 前的必要 Gate；Execution Brief 为版本化 Domain Object（承接 DEC-024）。
- **Execution Brief 编辑不触发下游失效：** 承接 DEC-009 / DEC-030，Execution Brief 修改不使 Marketing Brief 与上游失效；因 Execution Brief 为当前 MVP 最终输出，普通编辑不触发下游失效（当前 MVP 无下游）；改 Brief 返回 `brief_change_required`；MVP 不增额外强制 Review Gate（承接 DEC-007）。
- **LLM 不得生成最终文案：** MVP 输出为方向化 Execution Brief，不含最终小红书标题 / 正文 / Hashtags / 封面文字 / 视频分镜终稿；Final Copy Generator / 发布 / 自动审核不进 MVP。

> 注：本节确认**Xiaohongshu Brief Mapping Adapter 的集成边界**（只读当前 Brief / 版本化 Policy Snapshot / Account Context 输入 / 不改 Brief / 真实 Fragment 原声 / Validator 28 项 Gate / 编辑不触发下游失效 / 不生成最终文案；承接 DEC-004/006/009/011/015/019/020/024/025/027/029/030）；概念 Platform Adapter Spec 见 [../specs/adapters/xiaohongshu-brief-mapping-adapter.md](../specs/adapters/xiaohongshu-brief-mapping-adapter.md)（仅概念）。**仍待确认** 最终 Execution Brief Schema、Adapter 接口、Platform Policy Snapshot Repository、Account Context 输入接口、Execution Brief UI、Risk Validator 实现、Final Copy Generator 边界、发布 API、视频镜头信息方向结构。本节**不**创建正式小红书 Prompt / Adapter 代码 / LangGraph Node / Execution Brief UI / 数据库表 / Risk Validator 实现 / Final Copy Generator / Platform Policy Sync 代码 / 发布代码，**不**选择平台数据供应商 / 热点接口 / 搜索关键词工具 / 风险审核供应商 / 视频时长 / 图文页数 / Hashtag 数量 / 发布 API / 最终 LLM。下一议题 Hybrid Retrieval and Evidence Runtime Architecture 已由 DEC-032 确认（见下节）。

---

### Hybrid Retrieval and Evidence Runtime 的集成边界（DEC-032，Accepted，2026-07-29）

> 来源：[DEC-032 — Hybrid Retrieval and Evidence Runtime 采用 Direct-first 检索、确定性检索规划、强制权限与版本过滤与可复现证据装配](../decisions/dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)（Runtime Architecture / Retrieval Architecture / Evidence Architecture；Amends DEC-014）。概念 Runtime Spec 见 [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)。

承接 DEC-014（按需混合 RAG + 分层数据访问）、DEC-015（Skill 显式声明检索依赖）、DEC-023 / DEC-024（Node Adapter 加载 Domain Objects、Skill 不读 Checkpoint）、DEC-025（Evidence Package + Evidence Validator + Evidence Link + Source Scope 隔离），DEC-032 进一步确认 Hybrid Retrieval and Evidence Runtime 与各组件之间的集成边界：

- **Skill 不直接查询任意 Source：** Skill（Product Intake / Customer Insight / Positioning / Marketing Brief / Xiaohongshu Adapter）不直接访问来源数据库 / 检索索引 / 向量库；不直接绕过 Runtime（承接 DEC-025）。
- **Skill 通过 Retrieval Runtime 请求证据：** Skill 提交 RetrievalRequest，Runtime 返回 Candidate Fragments + Evidence Package 作为可复现证据输入快照。
- **Retrieval Planner 决定检索方式：** Deterministic Retrieval Planner 按检索优先级（Structured Direct Read → Exact Lookup → Bounded Direct Document Read → Lexical → Semantic → Hybrid → Optional Reranking）决定检索方式；Direct-first 原则 = 能直接读取时不使用检索。
- **Permission / Task / Product Scope / Source Version 由确定性逻辑控制：** 强制过滤（task_id / workspace_id / permission_scope / source_scope / product_id / competitor_id / source_set_version_id 等）在召回前 / 召回中生效，**不**是「先全召回再删除」；跨任务 / 跨商品身份召回私有资料必须拒绝。
- **LLM 不能修改访问范围：** LLM 可有限辅助 Query Planning（意图 / 子查询 / 有限 Query Rewrite / 同义表达），但**不得**决定 task_id / workspace_id / Permission / Source Scope / Product Scope / Source Set Version / 跨任务；精确标识符须逐字保留。
- **Dataset Statistics 不由 Top-K Retrieval 产生：** 正式频率 / 比例 / 共识 / 市场份额须由确定性统计服务基于完整可计数数据集产生；禁止用 Top-K 召回结果推断总体分布（承接 DEC-027）。
- **Evidence Validator 通过后才创建 Formal Evidence Link：** 检索结果仅为 Candidate Fragments + Evidence Package，不是 Formal Evidence；须经 Evidence Validator 校验并通过正式事务才创建 Evidence Link（承接 DEC-025）。Evidence Package = 可复现的 Skill 输入（不进 Current Truth）；Formal Evidence Link = 正式关系（进 Current Truth）。
- **Retrieval Checkpoint 或 Cache 不替代业务 Source Repository：** Cache（Source Version 解析 / Fragment Embedding / 同 Plan 结果 / Evidence Package）仅为性能优化，缓存键须含 task_or_workspace_scope / source_set_version_id / component_versions 等；Source Set Version 变化后不得返回旧缓存；Retrieval Run Log 与 Cache **不**作为正式业务来源 / Current Truth 存储（承接 DEC-024 Business Repository 保存正式业务数据）。

> 注：本节确认**Hybrid Retrieval and Evidence Runtime 与各组件的集成边界**（Skill 不直接查询 / 通过 Runtime 请求证据 / Planner 决定检索方式 / 确定性范围控制 / LLM 不修改范围 / Dataset Statistics 非 Top-K / Evidence Validator 后才建 Evidence Link / Cache 不替代业务库；承接 DEC-008/009/013/014/015/023/024/025/026/027/028/030/031，Amends DEC-014 不推翻既有结论）；概念 Runtime Spec 见 [../specs/runtime/hybrid-retrieval-and-evidence-runtime.md](../specs/runtime/hybrid-retrieval-and-evidence-runtime.md)（仅概念）。**仍待确认** Embedding 模型 / 向量数据库 / 词法搜索引擎 / BM25 实现 / Rank Fusion 算法 / Score Normalization 与融合权重 / Top-K / Reranker / Chunk Size / Chunk Overlap / Query Rewrite 模型 / 缓存技术 / 索引刷新机制 / RetrievalPlan / RetrievalRequest / Candidate Fragment / Evidence Package / RetrievalRun 最终 Schema / 最终错误代码。本节**不**创建正式 Embedding / Vector Index / Full-text Index 代码 / Retrieval API / Query Rewrite Prompt / Reranker 代码 / Fusion 代码 / Cache 代码 / 数据库表 / LangGraph Retrieval Node，**不**选择上述技术选型。下一议题 Workflow Runtime Failure Recovery, Retry and Observability Contract 已由 DEC-033 确认（见下节）。

---

### Workflow Runtime 的集成边界（DEC-033，Accepted，2026-07-29）

> 来源：[DEC-033 — Workflow Runtime 采用分层运行记录、分类故障处置、有界重试、安全恢复、事务幂等与端到端可观测性契约](../decisions/dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)（Runtime Architecture / Reliability Architecture / Observability Architecture；Amends DEC-023 / DEC-024 / DEC-029）。概念 Runtime Spec 见 [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)。

承接 DEC-011（确定性 Workflow 控制）、DEC-013（任务级持久化与跨会话恢复）、DEC-023 / DEC-024（LangGraph 运行时 + Checkpointer 与业务数据库分离）、DEC-025（Evidence Validator + Evidence Link）、DEC-029（Review Package 事务）、DEC-032（Retrieval Runtime Fallback），DEC-033 进一步确认 Workflow Runtime 与各组件之间的集成边界：

- **Workflow Runtime 统一协调 Retry Budget：** 统一管理 `per_attempt_timeout` / `per_node_retry_limit` / `per_skill_retry_budget` / `per_workflow_run_deadline`；各层组件（Workflow / Skill / Tool）不得独立无限重试，避免 `Workflow Retry × Skill Retry × Tool Internal Retry` 嵌套放大。
- **LLM Wrapper 不直接决定业务 Rerun：** LLM Wrapper（Structured Output Recovery / Constrained Repair / Candidate Regeneration）只负责重试或回退当前候选输出；业务 Rerun（创建新 `run_id` + `skill_run_id` + 新业务版本）由确定性 Workflow 控制、用户明确要求或上游版本变化触发。
- **Retrieval Runtime 使用明确 Fallback：** Retrieval Runtime（DEC-032）的降级（Semantic 失败 → Structured + Lexical + `semantic_retrieval_unavailable`；Reranker 失败 → 融合结果继续；Zero → `insufficient_information`）必须显式记录并传播 Evidence Limitation 给当前 Skill / Evidence Package / 下游业务对象，不得静默降级。
- **Repository Commit 必须事务化：** 业务写入遵循 `Candidate → Deterministic Validation → Atomic Commit`，正式事务至少同时处理 Create Domain Version / Create Formal Evidence Links / Update Current Truth Pointer / Update Stage State / Write Audit Record；任一失败整体回滚，不留下部分 Current Truth（承接 DEC-024 / DEC-029）。
- **Checkpointer 不替代业务 Repository：** LangGraph Checkpointer 只负责执行状态恢复 / Interrupt / Resume / Node 进度 / 临时运行上下文；**不**保存业务 Current Truth、**不**替代业务 Repository、**不**判断业务版本是否有效、**不**覆盖较新的业务状态、**不**创建正式业务对象（承接 DEC-023 / DEC-024）。
- **Human Review Resume 必须验证 Review Package：** Resume 必须表达 `review_id` / `review_package_version` / Review Draft `revision` / `approved_strategy_submission_reference` 的语义；Resume 前检查 Package 未被 superseded、Draft revision 未过期、上游版本仍有效、提交事务已成功、Approved Strategy Current Truth 已存在；须幂等；旧 Package 或 revision 不得通过 Checkpoint 绕过 DEC-029 / DEC-046 校验。最终传输字段名由 RFC-004 冻结。
- **Recovery Worker 不得绕过 Validator：** Manual Recovery（`retry_failed_node` / `restart_skill_from_safe_boundary` / `rerun_invalid_stage` / `rebuild_source` / `refresh_platform_policy` / `discard_stale_checkpoint` / `cancel_task` / `mark_dependency_resolved`）不得手工伪造 Fact、绕过 Evidence Validator、直接修改 Formal Evidence Link、强制将旧 Checkpoint 应用于新业务版本、删除失败历史，或直接修改 Current Truth Pointer 而不经正式事务。
- **Side-effect Tool 必须支持幂等或可确认结果：** 未来 Side-effect Tool（发布 / 发消息 / 创建外部对象 / 上传 / 提交平台任务）必须使用 `idempotency_key`；首次调用成功与否不确定时不得盲目重复执行；MVP 不实现自动发布，但运行时必须保留该边界。
- **Observability 不得泄漏敏感数据：** Logging / Tracing / Metrics / Alerting 不得默认保存 API Key / Authorization Header / 密码 / Secret / DB 连接串 / 完整敏感个人信息 / 未脱敏评论 / 其他 Workspace 内容 / 内部敏感 Prompt；只允许记录 Hash / Fragment ID / Source Version ID / Template Version / Schema Version / Token Usage / Latency / Error Category；User-facing Notification 与 Operator Alert 分离。

> 注：本节确认**Workflow Runtime 与各组件的集成边界**（Retry Budget 统一协调 / LLM Wrapper 不决定 Rerun / Retrieval 明确 Fallback / Repository 事务化 / Checkpointer 不替代业务库 / Human Review Resume 验证 Review Package / Recovery Worker 不绕 Validator / Side-effect Tool 幂等 / Observability 不泄漏敏感数据；承接 DEC-007/009/011/012/013/023/024/025/029/032，Amends DEC-023 / DEC-024 / DEC-029 不推翻既有结论）；概念 Runtime Spec 见 [../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md](../specs/runtime/workflow-runtime-failure-recovery-retry-and-observability.md)（仅概念）。**仍待确认** Retry 次数 / Timeout 秒数 / Backoff 参数 / Circuit Breaker 阈值 / Queue·Worker·DLQ 技术 / Logging·Tracing·Metrics·Alerting Provider / 是否采用 OpenTelemetry / Checkpointer 实现 / 数据库 / Outbox / 分布式锁 / 数据保留周期 / 日志采样率 / PII 脱敏实现 / 并发模型 / 最终 SLO / 各运行记录最终 Schema / 最终错误代码。本节**不**创建正式 Retry Middleware / LangGraph Recovery / Checkpointer / Worker / Queue / DLQ / Recovery Worker / Logging·Tracing Pipeline / Metrics Dashboard / Alerting Rules / 数据库表 / Outbox / 分布式锁 / API / 业务实现代码，**不**选择上述技术选型。在 **Technical Spike Plan and Architecture Readiness Gate** 议题已由 DEC-034 确认（见下节）。

### Production Checkpoint 与 Reconciliation 集成边界（DEC-049，Accepted，2026-08-06）

> 来源：[DEC-049 — 采用独立 PostgreSQL Checkpoint 数据库、同步持久性与 Current-Truth-first 对账](../decisions/dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md)；承载 RFC：[RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)（`ACCEPTED`，2026-08-06）。

- **物理复用、职责隔离：** Checkpointer 与 Business Database 复用同一 PostgreSQL Service，但使用独立 Checkpoint Database、Runtime Role、Credential 与 Pool；不共享 Repository、Session、事务或 Business Alembic chain。
- **受控生命周期：** 官方同步 `PostgresSaver` 的 setup / migration 由部署任务执行；API / Worker 启动不得隐式修改 Checkpoint Schema。
- **同步持久性：** 正式 Graph 使用 `sync` durability；Checkpoint 落盘定义 Super-step 恢复边界，但不把 Node 或外部调用变成 exactly-once。
- **可重入 Node：** Node 按 `Prepare → Execute → Commit` 设计；外部调用不持有业务事务，正式效果只经幂等 Application Command / Business Commit。
- **Current Truth 优先：** Resume / Recovery 比较 Runtime Registry、Durable Work Intent、Checkpoint、当前 Source / Domain / Review / Stage / Invalidation 与执行所有权；Checkpoint 只提供恢复候选位置，不授权写入。
- **不兼容分流：** stale / foreign / incompatible Checkpoint 不得继续旧计划或提交 Current Truth；进入确定性局部重跑、新安全执行分支或 Manual Recovery。对账结果写 Runtime / Recovery Record，不篡改历史 Checkpoint。
- **Time Travel 边界：** Replay / Fork 不等于 Business Restore，不得回退 Current Truth Pointer。

> 本节只同步 DEC-049 已接受输入。其接受当时尚未冻结的 Durable Dispatch、Worker Claim / Lease / Heartbeat 与 Cancellation 后续已由 DEC-050 冻结；Compatibility、Safe Resume、迁移 / 回滚与验收证据边界后续已由 DEC-051 冻结。Retention、精确实施版本与公共字段仍待后续规划。本节不授权依赖安装、Database 创建、setup / migration、Spike 或实现。

### Durable Dispatch、Worker Ownership 与 Cancellation 集成边界（DEC-050，Accepted，2026-08-06）

> 来源：[DEC-050 — 采用 PostgreSQL Durable Dispatch、Fenced Worker Ownership 与协作式取消](../decisions/dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md)；承载 RFC：[RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)（`ACCEPTED`，2026-08-06）。

- **可靠调度来源：** Transactional Durable Work Intent 是唯一权威待执行来源；Worker 用短事务和 `FOR UPDATE SKIP LOCKED` 领取有界小批工作，Claim 后立即提交，外部执行不持有业务事务。
- **Wake-up 边界：** 数据库轮询是正确性基线；`LISTEN / NOTIFY` 仅可优化等待，不承担可靠投递；首个 Goal 不引入独立 Broker。
- **执行所有权：** Claim 原子写 Holder、Lease expiry 与单调 Fencing Token；Heartbeat、完成、释放和由该 Worker 执行产生的 Business Commit 均条件校验当前 Holder + Token。
- **陈旧 Worker 隔离：** Lease 过期后的新 Owner 使用更高 Token，旧 Worker 不得完成 Work Intent、创建 Domain Version 或移动 Current Truth Pointer。
- **取消 / Supersession：** 先持久化请求，Worker 在外部调用前后、Node 边界和 Commit 前检查；请求态不冒充终态，无法中断的调用结果在取消、取代或 Ownership Loss 后被丢弃。
- **职责交接：** RFC-004 冻结用户 / API 状态与错误映射；RFC-007 冻结轮询、Lease / Heartbeat、并发、Shutdown 与可观测参数；TS-01 验证真实 PostgreSQL 多 Worker 风险。

> 本节不冻结最终表、字段、SQL、参数或公共 API，不授权 Worker、数据库、Migration、Spike 或业务实现。Compatibility、Safe Resume Action Matrix、迁移 / 回滚与 RFC-003 验收证据已由 DEC-051 冻结。

### Compatibility、Safe Resume 与 Forward Recovery 集成边界（DEC-051，Accepted，2026-08-06）

> 来源：[DEC-051 — 采用显式运行时兼容、确定性安全恢复与前向恢复证据边界](../decisions/dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md)；承载 RFC：[RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)（`ACCEPTED`，2026-08-06）。

- **Compatibility Tuple：** 可恢复执行绑定 Workflow Definition、Graph State Schema、Serializer Profile 与已验证的 Checkpointer Package / Store Schema 范围；Runtime 只恢复明确兼容或存在已测试纯转换器的状态。
- **升级交接：** Preflight → 受控 Checkpointer Migration Task → 新 Runtime 健康验证 → 有界 Worker 切换；历史 Checkpoint 不原地改写，旧、新 Worker 只领取各自兼容 Work Intent。
- **恢复授权：** Application 层依据 Current Truth、Runtime Registry、Work Intent / Ownership、Checkpoint metadata、Source / Review / Stage revisions、失效和幂等结果选择受控 Recovery Action；客户端 Checkpoint ID 不构成授权。
- **执行身份：** 实际恢复保留稳定 `task_id` / `thread_id`，创建新的 `run_id` 与 Attempt，并在 Commit 前重新执行 Cancellation、Revision、Lease、Fencing 与幂等校验。
- **恢复与回滚：** 优先兼容扩展和 Forward Repair；只有证明旧 Runtime 与当前 Store Schema 兼容时才允许代码回滚；Store 不可用时从受控备份或 Business Current Truth / Runtime Registry 的安全边界恢复。
- **职责交接：** RFC-004 冻结公共状态、错误与请求协议；RFC-007 冻结运维参数和观测；ARP-06 / TS-03 冻结并执行 Checkpoint Reconciliation 风险验证；ARP-08 冻结 Retention / Backup 生命周期。

> 本节不固定未经实施证据验证的精确依赖版本，不创建 Compatibility Matrix 实例、转换器、Runtime Registry、数据库或迁移，不执行 Spike，也不激活 Goal。RFC-003 整体后来已于 2026-08-06 由用户单独接受。

### Technical Spike and Architecture Readiness Gate 的集成边界（DEC-034，Accepted，2026-07-29）

本节确认 **Spike 与正式开发之间的集成边界**，约束 Spike 不得越界成为生产实现、不得擅自改变 Development Status。

- **Spike Graph 不得直接成为生产 Graph：** Spike 代码有三种处置（Discard / Reference / Promote Selectively）；只有接口清晰、测试充分、不依赖 Mock、不依赖临时 Schema、符合 Architecture Baseline、经过正式 Review、有对应 RFC 或 Spec 支持的部分，才允许通过独立 PR 迁入正式代码；**不得**将整个 Spike Prototype 直接改名为生产实现。
- **Checkpoint Store 不替代 Business Repository：** 三类 Repository 须逻辑分离（Business Repository / Runtime Repository / Checkpoint Store），即使 Spike 使用同一物理存储也须保持逻辑边界；`LangGraph Checkpoint Store ≠ Business Current Truth Repository`；Checkpointer 不得覆盖较新业务版本。
- **Mock Business Objects 不构成最终 Domain Schema：** Mock Facts / Insights / Positioning Candidates / Approved Strategy / Marketing Brief 仅验证架构行为，不得作为正式 Domain Schema、不得作为生产数据。
- **Spike 成功不自动改变 Development Status：** Spike 通过不等于 Architecture READY；Gate 支持三种正式结果 READY / CONDITIONALLY READY / NOT READY；Architecture Agent 只能提交 Readiness Recommendation，最终状态须用户明确确认。
- **Roadmap 与 GitHub Issues 只能在 Readiness Gate 后正式生成：** Architecture Baseline / RFC Register / MVP Roadmap / Epic Map / GitHub Issues / Traceability Matrix 须在 Gate 通过并经用户确认后按序生成；**当前不生成**。
- **Coding Agent 不得在 Spike 中锁定生产基础设施：** Production Database / Checkpointer Backend / ORM / API Framework / Frontend Framework / Vector Database / Embedding Model / Logging Provider / Tracing Provider / Deployment Platform 等，须经 RFC 或正式技术决策，不得在单个 Issue 或 PR 中擅自选择。

> 注：本节确认 **Technical Spike and Architecture Readiness Gate 的集成边界**（Spike Graph 不得成为生产 Graph / Checkpoint Store 不替代 Business Repository / Mock Objects 非最终 Schema / Spike 成功不改 Development Status / Roadmap 与 Issues 须 Gate 后生成 / Coding Agent 不得锁定生产基础设施；承接 DEC-011/013/023/024/025/029/032/033，Amends DEC-023 / DEC-033 不推翻既有结论）；概念 Readiness Spec 见 [../specs/readiness/technical-spike-and-architecture-readiness-gate.md](../specs/readiness/technical-spike-and-architecture-readiness-gate.md)（仅概念）；Spike 工作区见 [../spikes/spike-001-langgraph-runtime-and-recovery/](../spikes/spike-001-langgraph-runtime-and-recovery/)（仅规划，非实现）；Readiness 入口见 [../readiness/README.md](../readiness/README.md)。本节**不**实现 Spike 代码、**不**创建正式业务 Graph、**不**编写四个核心 Skill 的生产 Prompt、**不**建立正式数据库 Schema、**不**选择生产级基础设施、**不**生成 MVP Roadmap / Epic Map / GitHub Issues / RFC。**仍待确认** Spike 语言和版本 / LangGraph 具体版本 / Spike 数据库 / Checkpointer Backend / Mock LLM 实现 / Fault Injection 工具 / 测试框架 / Trace Provider / 临时 API / Spike 代码目录 / Spike 执行 Agent / 执行时间计划 / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号。**Technical Spike Execution Brief and Temporary Spike Stack 议题已由 DEC-035 确认（见下节）。**

---

### Technical Spike 临时技术栈与执行契约的集成边界（DEC-035，Accepted，2026-07-29）

> 来源：[DEC-035 — Technical Spike 临时采用 Python、同步 LangGraph StateGraph、分离式 SQLite 存储、确定性 Mock 与场景化故障注入执行契约](../decisions/dec-035-technical-spike-temporary-stack-and-execution-contract.md)（Technical Spike Execution / Temporary Architecture / Validation Environment；Amends DEC-034）。Spike 执行简报见 [../spikes/spike-001-langgraph-runtime-and-recovery/execution-brief.md](../spikes/spike-001-langgraph-runtime-and-recovery/execution-brief.md)。

本节确认 **Spike-001 临时栈与 Spike Agent 的集成边界**，约束临时选择不得越界成为生产承诺、Spike Agent 不得越权。

- **Spike 代码不能被生产模块 Import：** Spike 是独立、可抛弃的实验目录（`spikes/spike-001-*`），生产模块**不得**直接依赖其代码。
- **Spike Graph 不能直接成为生产 Graph：** 迁移须经独立 PR + Review；**不得**将整个 Spike Prototype 改名为生产实现。
- **Scripted Model 不构成生产 LLM 决策：** `ScriptedModelProvider` 仅用于确定性验证；生产 LLM 选型仍待后续 RFC。
- **Mock Retrieval 不构成生产 Retrieval 决策：** `MockRetrievalRuntime` 仅验证 Retrieval Fallback 与 Evidence Limitation 传播；生产 Embedding / 向量库 / Retrieval Backend 仍待后续 RFC。
- **SqliteSaver 不构成生产 Checkpointer 决策：** Spike 用 LangGraph `SqliteSaver` + 三类分离 SQLite 仅为临时验证；生产 Checkpointer / 数据库仍待后续 RFC。
- **Spike Agent 不得修改 Accepted DEC：** Spike Agent 不得改动任何已接受 Decision 的含义或边界；已接受 DEC 被实验推翻须提交正式修订提案并由用户重新确认。
- **Spike Agent 不得创建正式 Roadmap / Epics / Issues：** 这些须在 Architecture Readiness Gate 通过并经用户确认后才正式生成；Spike 阶段**当前不生成**。
- **Spike Agent 不得执行外部 Side Effect：** 不做真实发布 / 外部调用 / 影响外部系统的动作；可选 Real Model Smoke Test 为唯一例外且 Secret 经环境变量注入、不落盘、无 API Key 自动 Skip。
- **Spike Agent 不得擅自更改 LangGraph 1.2.9：** 遇安装 / 兼容 / Interrupt / 安全失败须停止场景 → 创建 Spike Finding → 提交变更建议 → 等待用户确认，**不**静默升级或降级。

> 注：本节确认 **Technical Spike 临时技术栈与执行契约的集成边界**（Spike 代码不被生产 Import / Spike Graph 不直接成生产 Graph / Scripted Model 非生产 LLM / Mock Retrieval 非生产 Retrieval / SqliteSaver 非生产 Checkpointer / Spike Agent 不改 Accepted DEC / 不建正式 Roadmap·Issues / 不做外部 Side Effect / 不擅改 LangGraph 版本；承接 DEC-023 / DEC-032 / DEC-033 / DEC-034，Amends DEC-034 不推翻既有结论）；概念规格见 [../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md](../specs/readiness/technical-spike-execution-brief-and-temporary-stack.md)（仅概念）。**所有临时选择不构成生产承诺。**本节**不**实现 Spike 代码、**不**执行 uv sync / 依赖安装 / SQLite 初始化 / StateGraph Compile / Scenario Runner / pytest / Fault Injection / Real Model Smoke Test，**不**选择生产数据库 / 生产 Checkpointer / ORM / 生产 LLM / 生产 Retrieval / 生产 Observability / 生产部署平台。**仍待确认** Spike 执行时间计划 / 实际依赖兼容性结果 / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术。**Spike 主执行 Agent 与执行授权契约已由 DEC-036 确认（见下节）。**

---

### Spike-001 执行授权契约的集成边界（DEC-036，Accepted，2026-07-29）

> 来源：[DEC-036 — Spike-001 采用 Claude 主执行、受控 Git/GitHub 权限、独立 Branch、Issue/PR 追踪、阶段化提交与用户保留 Merge 和 READY 决策权的执行授权契约](../decisions/dec-036-spike-001-execution-authorization-and-agent-handoff-contract.md)（Agent Governance / Git and GitHub Operations / Spike Execution Authorization；Amends DEC-034 and DEC-035）。概念规格见 [../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md](../specs/readiness/spike-001-execution-authorization-and-agent-handoff-contract.md)；Git/GitHub 权限操作参考见 [../agents/git-and-github-permissions.md](../agents/git-and-github-permissions.md)。

本节确认 **Spike-001 执行授权契约的集成边界**，约束执行 Agent 的 Git/GitHub 操作与「执行产物 ≠ 正式业务真相 / READY」的边界。

- **GitHub Issue 不替代 Spec：** Spike Issue 是执行追踪载体，其内容不构成、不替代任何正式 Specification；业务规格只来自 Accepted DEC 与对应概念规格。
- **PR 描述不替代 Accepted Decision：** Draft PR 的描述、Checklist 与 Review 讨论不构成、不替代任何 Accepted Decision；Accepted DEC 只能经 Decision Gate 由用户确认。
- **Merge 不代表 READY：** Merge Spike PR 本身不等于 Architecture READY；READY 须经 Readiness Review + 用户明确确认「确认 Architecture READY」。
- **Check 通过不代表 READY：** CI / PR Checks / 测试全部通过不构成 Architecture READY；READY 判定还需 Spike 证据审查 + 用户确认。
- **Agent Recommendation 不代表 READY：** Claude 的 Readiness Recommendation（`RECOMMENDED: READY | CONDITIONALLY READY | NOT READY`）只是建议，不能自行写入 `Development Status = READY`。
- **用户保留不可逆 Git / GitHub 操作：** Force Push / 改写共享历史 / 删除 Branch / Merge PR / 关闭 Issue / 修改仓库权限（Branch Protection / Visibility / Collaborators / Secrets / Deploy Keys / Actions / Settings）等不可逆或治理类操作由用户保留；Claude 未经针对性授权不得执行。
- **Claude 与 Codex 默认不得并发修改同一 Branch：** Codex 默认只读 Review、不得 Push Claude Branch；如需 Codex 修复代码须另行明确授权，并避免两个 Agent 并发写入同一工作区。

> 注：本节确认 **Spike-001 执行授权契约的集成边界**（执行产物不替代正式真相或 READY + 用户保留不可逆操作 + 单 Branch 单写入者；承接 DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 / DEC-034 / DEC-035，Amends DEC-034 + DEC-035 不推翻既有结论）。本决定接受的是**权限和执行契约，不是立即开始执行 Spike**；DEC-036 被接受后 Spike 仍不得自动启动。本节**不**创建 Spike Branch / 实际 GitHub Issue / 实际 Pull Request，**不**执行 git push / 依赖安装 / Spike 代码 / 测试 / S0，**不**关闭 Issue / Merge PR / 更新 Development Status，**不**创建正式 MVP Backlog / Epics / 生产 Issues，**不**创建 RFC。**仍待确认** 立即启动 Spike / Baseline Commit SHA / 实际 Issue·PR 编号 / GitHub Labels·Project·Actions / CI Provider / Codex 是否执行独立 Review / Reviewer 身份 / Merge Strategy / Spike PR 是否最终 Merge / Spike Readiness Recommendation / CONDITIONALLY READY 具体允许范围 / READY Checklist 最终字段 / RFC 最终数量和编号，以及全部生产技术。保持 `Contract Authorization = ACCEPTED` / `Execution Authorization = NOT GRANTED` / `Spike Execution Status = NOT STARTED` / `Architecture Readiness Status = NOT READY` / `Development Status = NOT READY`。下一议题（尚未开始，需用户明确启动）：`Formal Spike-001 Execution Authorization` **已由 DEC-037 确认（见下节）。**

---

### Formal Spike-001 Execution Authorization 的集成边界（DEC-037，Accepted，2026-07-30）

> 来源：[DEC-037 — 正式授权 Claude Code 在 Repository Audit 和稳定文档基线通过后，执行 Spike-001 S0—S6，并创建受控 Issue、Branch、Commits、Push、Draft PR、测试证据与 Readiness Recommendation](../decisions/dec-037-formal-spike-001-execution-authorization.md)（Execution Authorization / Agent Governance / GitHub Workflow；Amends DEC-034、DEC-035 and DEC-036）。概念规格见 [../specs/readiness/formal-spike-001-execution-authorization.md](../specs/readiness/formal-spike-001-execution-authorization.md)；Git/GitHub 权限操作参考见 [../agents/git-and-github-permissions.md](../agents/git-and-github-permissions.md)。

本节确认 **Formal Spike-001 Execution Authorization 的集成边界**，约束「执行授权被激活」不等于「已开始执行或已通过」，以及授权产物与依赖安装不得越界成为正式业务真相或生产承诺。

- **Execution Authorization = GRANTED ≠ 已开始执行或已通过：** DEC-037 正式授予 Claude 执行 Spike-001 S0—S6 的授权，但 `GRANTED` 不表示 Repository Audit 已完成 / Spike 已开始 / Spike 已通过 / Architecture 已 READY / Development 已 READY。
- **第一动作仍是只读 Repository Audit：** 执行的第一项操作必须是只读 Repository Audit 并形成 Repository Audit Report；Audit 与稳定文档基线通过前**不得**写入 / 安装依赖 / 创建 Spike 代码 / Branch / PR。Audit Blocked 时停止并报告，**不得**覆盖、删除、Reset 或隐藏现有修改。
- **授权产物不得越权修改 Accepted Specs / DEC：** Spike Issue / 独立 Branch `spike/001-langgraph-runtime-recovery` / Draft PR 不得借助 Spike 修改 Accepted Business Specs 或 Accepted DEC 的含义；不得将 Mock Schema 写成正式 Data Architecture；不得创建正式 MVP Backlog / Business Epics / 生产实现 Issues。
- **隔离依赖授权不得越界：** 依赖安装仅限隔离目录 `spikes/spike-001-langgraph-runtime-and-recovery`；**不得**修改系统全局 Python / 管理员权限安装 / 卸载用户全局软件 / 修改项目其他环境 / 静默更换 LangGraph 版本 / 把 Spike 依赖加入生产依赖；不得自行升级 / 降级 LangGraph、更换 Python / Checkpointer / Workflow Framework。
- **S6 完成边界 + 用户保留不可逆操作：** S6 完成后 Claude 必须停止，可提交 Readiness Recommendation 但**不得** Merge PR / 关闭 Spike Issue / 自行宣布 READY；用户保留 Decision 修订 / Scope 批准 / PR Merge / Issue Closure / Git 历史危险操作批准 / Architecture READY 确认 / Development Status 变更权；**PR Merge ≠ READY、Issue Closed ≠ READY、Agent Recommendation ≠ READY。**

> 注：本节确认 **Formal Spike-001 Execution Authorization 的集成边界**（执行授权激活 ≠ 已开始执行或已通过 + 第一动作只读 Repository Audit + 授权产物不改 Accepted Specs·DEC + 隔离依赖授权不越界 + S6 完成边界 + 用户保留不可逆操作与 READY 确认；承接 DEC-023 / DEC-024 / DEC-029 / DEC-032 / DEC-033 / DEC-034 / DEC-035 / DEC-036，Amends DEC-034 + DEC-035 + DEC-036 不推翻既有结论）。本决定接受的是**从规划和归档阶段进入实际仓库执行阶段的授权**，但第一动作仍是只读 Repository Audit，且在 Audit 与稳定基线通过前不得开始任何写入、安装或 Spike 代码。本节**不**运行 Repository Audit / 创建实际 GitHub Issue·Branch·PR / Push / 安装依赖 / 创建 Spike 代码 / 运行测试 / 初始化 SQLite / 启动 S0，**不**创建 RFC。**尚未确认** 实际 Repository Audit 结果 / Baseline Commit SHA / Issue 编号 / Branch 是否已创建 / PR 编号 / 测试结果 / Spike Findings / Codex Independent Review / Merge Strategy / Spike PR 是否 Merge / Architecture Readiness Result / Development Status 是否 READY。保持 `Spike Execution Status = NOT STARTED` / `Architecture Readiness Status = NOT READY` / `Development Status = NOT READY`。下一动作（归档进入稳定 Git 基线后以独立任务执行）：`Spike-001 Execution Handoff`（第一步必须是只读 Repository Audit）。

---

## 当前状态

- 项目处于 **架构探索阶段**（Session-002 进行中）。
- 已确认编排层需与持久化存储集成（DEC-013）；具体集成对象（数据库 / 文件存储 / Checkpoint / 模型 API / 电商平台 API）、集成方式、权限与数据边界均**尚未确认**。
- 本文件的具体集成内容，必须等到对应 Proposed Decision 被用户明确接受并记为 Accepted Decision（见 [../decisions/](../decisions/)）后，才能写入。

---

## 文档骨架（占位，内容待填充）

> 以下章节标题仅作为未来结构占位，**当前全部为空**，不构成任何集成声明。

- 外部系统 / API 清单
- 集成方式与协议
- 数据进出边界与脱敏
- 权限与鉴权
- 依赖与故障隔离
- 成本与限额

---

## 待讨论的开放问题（集成边界相关）

- 需要接入哪些电商平台 / 外部服务？
- 使用哪个模型 API？以什么方式接入？
- 哪些数据可以流出系统？哪些必须保留在内部？
- 涉及哪些权限 / 安全 / 隐私约束？

引入外部系统或 API 属于重大议题，通常应通过 RFC 讨论（见 [../rfcs/](../rfcs/)）。

讨论与提案记录在 [../sessions/](../sessions/)；确认后的决定记录在 [../decisions/](../decisions/) 并同步回本文件。

---

## 同步规则

- 仅在决定被明确接受后更新本文件。
- 不得擅自选择第三方服务或模型供应商。
- 不得为使文档「完整」而补充未经讨论的集成。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
