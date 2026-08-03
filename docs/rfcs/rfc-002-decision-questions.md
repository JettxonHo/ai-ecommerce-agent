# RFC-002 Decision Questions：持久化与事务架构决策问题集（DQ-01~17 ACCEPTED；全部 DQ 已决定）

> **Status:** DQ-01 = **ACCEPTED**（2026-08-01 用户正式决定，Accepted with Revision）；DQ-02 = **ACCEPTED**（2026-08-01 用户正式决定，Accepted with Revision）；DQ-03 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-04 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-05 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-06 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-07 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision，Accepted Direction = Layered Concurrency Control）；DQ-08 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Primary Direction = Candidate B，Supporting Principle = Candidate C）；DQ-09 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate B，Formal Pattern = PostgreSQL-backed Transactional Durable Work Intent）；DQ-10 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A）；DQ-11 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A，Formal Model = Authoritative Current Truth + Immutable Business Version Snapshots + Append-only Audit/Transition History + Optional Derived Query Projections）；DQ-12 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A，Formal Model = PostgreSQL Authoritative Source/Evidence Graph + Immutable Content-addressed Source Blobs + Versioned Derived Artifacts and Fragments + Explicit Evidence-to-Claim Links + Rebuildable Non-authoritative Retrieval Index）；DQ-13 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A，Formal Model = Shared PostgreSQL Service + Isolated Checkpoint Persistence Plane + Dedicated Role/Connection Pool/Storage Namespace + Application-owned Workflow Execution Registry + Business-Current-Truth-first Reconciliation）；DQ-14 = **ACCEPTED**（2026-08-03 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A，Formal Model = Alembic-managed Business Schema Migrations + Single Business Migration Lineage + Forward-recovery-first Production Policy + Expand-Migrate-Contract Rolling Compatibility + Resumable Application-owned Data Backfills + Explicit Destructive/Non-transactional DDL Gates + Separate Vendor Migration Lifecycles）；DQ-15 = **ACCEPTED**（2026-08-03 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A，Formal Model = Classified Retention & Disposition Policies + Purpose/Legal-basis-driven Retention Clocks + Reference-aware Deletion Eligibility + Legal/Security/Incident Hold Overrides + Normal-lifecycle Immutability for Business History + Governed Exceptional Erasure/Redaction Paths + Idempotent Auditable Purge Orchestration + Separate Primary/Object/Index/Checkpoint/Backup Lifecycles）；DQ-16 = **ACCEPTED**（2026-08-03 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A，Accepted Principle = Layered Test Strategy，Formal Model = Pure Domain/Application Unit Tests + Port Contract Parity Tests + Real PostgreSQL Persistence Acceptance Tests + Deterministic Multi-connection Concurrency Tests + Real Migration/Upgrade/Recovery Tests + Crash-window/Fault-injection Tests + Production-topology-specific Qualification，SQLite = Optional Non-authoritative Test Double）；DQ-17 = **ACCEPTED**（2026-08-03 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A，Formal Model = Classified Sensitive-data Protection + Secret-reference-only Persistence + Ephemeral Adapter-scoped Secret Resolution + Data-minimized Multi-plane Propagation + Strict Allowlisted Checkpoint Serialization + Least-privilege Role/Credential/Pool Separation + Selective Envelope Encryption by Protection Profile + Infrastructure Encryption in Transit/at Rest + Auditable Access/Redaction/Rotation/Incident Response）；**DQ-01~DQ-17 全部 ACCEPTED（无一 PENDING）；RFC-002 = ACCEPTED（2026-08-04 用户正式决定；Acceptance ≠ Authorization，Implementation = NOT AUTHORIZED；见主文档 §33 Decision Log 2026-08-04 Final Decision 记录）**
> **服务 RFC：** RFC-002 — Persistence and Transaction Architecture
> **治理：** DEC-036（Controlled Git/GitHub Execution）· DEC-038（RFC and Issue Governance）
> **证据底座：** `rfc-002-research-persistence-requirements.md`（需求矩阵）· `rfc-002-analysis-cross-rfc-boundary.md`（边界矩阵）· 四条一手官方研究（SQLAlchemy / LangGraph Checkpointer / PostgreSQL-SQLite-Alembic / 模式定义）
> **纪律（恒定成立）：**
> - DQ-01~DQ-17 已由用户正式决定（均 `Status = ACCEPTED`；DQ-01~DQ-07 的 `User Decision = ACCEPTED WITH REVISION`，DQ-08/DQ-09/DQ-10/DQ-11/DQ-12/DQ-13/DQ-14/DQ-15/DQ-16/DQ-17 的 `User Decision = ACCEPTED WITH MAJOR REVISION`）；全部 17 个 DQ 已决定；**RFC-002 已于 2026-08-04 由用户正式接受（RFC-002 = ACCEPTED；Acceptance ≠ Authorization，Implementation = NOT AUTHORIZED）**；**只有用户**能把 DQ 或 RFC-002 整体标记为 ACCEPTED。
> - `Recommendation` 是**架构建议**，**绝不**写成 Accepted Decision；采纳与否由用户在 Decision Gate 决定。DQ-01/02/03/04/05/06/07/08/09/10/11/12/13/14/15/16/17 的历史 Recommendation 已被各自的 Accepted Decision 取代（Superseded by Accepted Revision / Major Revision）。
> - 每条区分：**[DEC 约束]**（已 Accepted 的项目决定，RFC 不得推翻）/ **[官方能力]**（官方文档/源码明确能力）/ **[架构推断]**（由官方事实推导的建议）/ **[未决假设]**。
> - 真正的架构分歧**写入 DQ**，不替用户私下决定。
> - **（Historical Snapshot）**：正文归档的各 Recommendation 与 Accepted Decision 均按其决定日期记录（Status at Time of Decision）；其中 `(PROPOSED / PENDING)`、「DQ-xx 决定前」、「留待 DQ-xx」等表述反映决定时点状态，相关事项均已由对应 DQ 正式决定（DQ-01~17 全部 ACCEPTED）或属真正仍未决定的实现细节（如 KMS/Vault/HSM 选择、具体保留期限）；原文不改写。

---

## DQ 总览

| DQ | 主题 | 核心分歧 | 主要证据 |
|---|---|---|---|
| DQ-01 | 主持久化技术（Business DB 引擎） | **已决定（2026-08-01 ACCEPTED）**：PostgreSQL-only；原分歧 PostgreSQL vs SQLite vs MVP-SQLite→PG | PG/SQLite 官方并发与部署边界 |
| DQ-02 | 持久化所有权 / 模块边界 | **已决定（2026-08-01 ACCEPTED）**：单一 PG 服务 + 每表唯一所有模块 + 架构测试强制；每模块独立 schema 暂缓 | DEC-034 逻辑分离恒定 |
| DQ-03 | Aggregate 与持久化边界 | **已决定（2026-08-02 ACCEPTED）**：聚合边界 = 业务不变量 + 唯一模块所有权；Task Mega Aggregate 拒绝；一 Use Case 一主聚合；UoW 形态移交 DQ-05/06 | DEC-035 六要素单事务（提交协议） |
| DQ-04 | Domain State Versioning | **已决定（2026-08-02 ACCEPTED）**：`domain_version_id` / `version_number` / `revision` 三类分离 + `expected_revision` 显式并发校验；原分歧 应用层版本 vs `xmin` vs SERIALIZABLE | SQLAlchemy version_id_col 边界（仅 Infrastructure 机制） |
| DQ-05 | Transaction Boundary | **已决定（2026-08-02 ACCEPTED）**：Application 拥有业务事务 + 一短显式事务一最终提交点 + 长流程多短事务与无事务执行阶段 + 四项 PROHIBITED + Commit-time Revision Revalidation + 默认 READ COMMITTED + SAVEPOINT 仅基础设施机制、嵌套/分布式事务拒绝；原分歧 一 Use Case 一短事务 vs 全程一事务 vs SAVEPOINT 混合 | 连接 checkout 机制（推断） |
| DQ-06 | Unit of Work Model | **已决定（2026-08-02 ACCEPTED）**：UoW Port 由 Application 定义 + Infrastructure SQLAlchemy 实现（Session 为不暴露的 Infrastructure 细节）+ 一次性 UoW（NEW→ACTIVE→COMMITTED/ROLLED_BACK→CLOSED）+ 一 UoW / 一 Session / 一短事务 / 一最终结果 + Use Case 显式 commit（Context 退出不自动提交）+ 未提交或异常退出 = rollback/close/discard + Repository 无事务控制权与 Session 暴露、无 Registry/Service Locator + 嵌套业务 UoW 禁止 + Composite 唯一外层 UoW + 纯读独立短 Query Scope；原分歧 显式 UoW vs 隐式自动提交 vs Repository 管理事务 | SQLAlchemy Session=UoW（官方能力；项目采用更严格一次性 UoW） |
| DQ-07 | Concurrency Control | **已决定（2026-08-02 ACCEPTED）**：分层并发控制（Layered Concurrency Control）——乐观 revision（DQ-04 协议）为普通业务写默认 + 命名数据库唯一约束为重复业务事实最终防线（完整幂等键留 DQ-08）+ Durable Lease + 单调 fencing_token 为执行所有权（进程内锁仅非权威优化）+ SELECT FOR UPDATE SKIP LOCKED 仅限短事务队列式 Claim + Session-level Advisory Lock 禁止 + 40001/40P01 由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试（语义冲突不盲目重试）；Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Technical Spike 为实现前置条件（均未授权）；原分歧 乐观/悲观/CAS/约束/应用锁取舍 | DEC-022/029/033 五类并发场景；R-1 GAP |
| DQ-08 | Idempotency Model | **已决定（2026-08-02 ACCEPTED）**：Candidate B 为主（各幂等层由 Owning Module 分层存储）+ Candidate C 为强制设计原则（天然幂等 set/ensure/replace 语义，不替代显式记录与唯一约束）+ 统一语义契约（非统一物理表）；Candidate A 作为跨模块万能 Idempotency Table 被拒绝；Retry 复用 Command ID/Idempotency Key/Stage Run ID/Input Fingerprint 并创建新 Attempt ID，Intentional Rerun 创建新逻辑身份（保留 rerun_of）；同 Scope+Key+Fingerprint 重放原 Application Result、不同 Fingerprint 返回 Idempotency Key Conflict；幂等成功记录与 Business Current Truth 同一 DEC-035 原子提交；Consumer Dedup Marker 与消费业务更新同事务；IN_PROGRESS 执行所有权与 DQ-07 Durable Lease/Holder/Attempt ID/fencing_token 协同（旧 Worker 不得完成记录）；瞬时失败不永久固化、确定性终局语义结果可稳定重放；数据库事务重试不得重新调用外部 Provider（复用同一 Provider Call Identity）；Checkpoint/thread_id 不是业务幂等记录；**Idempotency Identity Matrix 为实现前置条件——REQUIRED 但 NOT AUTHORIZED**；物理表/Retention/Security 留 DQ-13/15/17；原分歧 统一幂等表 vs 分层存储 vs 天然幂等语义 | Idempotent Consumer 权威 |
| DQ-09 | Transactional Outbox / Durable Dispatch | **已决定（2026-08-02 ACCEPTED）**：Candidate B（PostgreSQL-backed Transactional Durable Work Intent）作为 MVP 内部可靠工作调度模型 + Candidate A 不作 MVP 内部任务模型（保留为未来 Integration Event Outbox 方向）+ Candidate C 独立 Broker 不在 MVP 引入（未来仅作 Delivery Backend，不替代事务内 Durable Intent）；业务状态更新与 Durable Work Intent 同一 PostgreSQL Atomic Business Commit（Intent 写入失败整体回滚、回滚不留可领取 Intent）；API 仅在 Intent 持久化提交后返回 accepted（accepted 仅表示工作已可靠记录，不表示 Worker 或业务执行完成）；禁止 asyncio.create_task/内存 Queue/临时 Background Task/单独 Broker Publish/仅 LISTEN-NOTIFY 作为唯一可靠调度；Dispatch ID Retry 稳定、Delivery Attempt 每次新建、Intentional Rerun 新 Dispatch ID（保留 rerun_of）；短事务 SELECT FOR UPDATE SKIP LOCKED Claim + Lease Holder + 单调 fencing_token + Attempt Identity，长执行不持行锁/Session/UoW/连接，最终提交重新验证 Dispatch ID/Lease Holder/fencing_token/Attempt/Fingerprint/expected_revision（旧 Worker 或过期 Lease 不得完成 Intent）；Delivery = at-least-once（不承诺 exactly-once；唯一业务效果由 DQ-08 幂等 + Consumer Dedup + 命名唯一约束 + DQ-07 Lease/Fencing + revision + Atomic Commit 组合保证）；数据库事务 Retry 与 Work Execution Retry 分离（DQ-07 三次事务尝试不直接套用长任务次数；Work Retry/Backoff/Dead-letter/人工恢复/告警留 RFC-003/RFC-007）；LISTEN/NOTIFY 仅非权威唤醒优化、周期性 Polling 为权威恢复路径；不新增独立 Matrix，现有 Idempotency Identity Matrix 与 Concurrency Scenario Matrix 须补充 Dispatch 场景——REQUIRED 但 NOT AUTHORIZED；DQ-07 真实 PostgreSQL 多 Worker Spike 继续有效并覆盖 Durable Dispatch 并发与恢复语义；relay/Worker backend/部署拓扑留 RFC-003，Event 分类留 DQ-10，HTTP/Polling API 协议留 RFC-004，Retention 留 DQ-15，测试留 DQ-16，Security 留 DQ-17；原分歧 是否首版引入 Outbox | 双写问题权威；RFC-001 移交 |
| DQ-10 | Event & Audit Persistence | **已决定（2026-08-02 ACCEPTED）**：Domain Event / Audit Record / State Transition Record / Application Event / Integration Event / Observability Event 六类记录语义独立，拒绝 Universal Event / Audit Table（Candidate B）与全项目 Event-driven 架构（Candidate C）；Audit Record 为 append-only 权威问责证据、与对应 Business Current Truth 修改同一 DEC-035 原子提交（写入失败整体回滚，不得异步补写/覆盖/删除；更正仅追加 Correction/Superseding/Reversal Record）；State Transition Record 为显式类型 Audit Record（可物理共用 Audit Ledger，不代表语义合并，不得充当 Integration Event 或 Current Truth）；Domain Event 为模块内部过去式业务事实、默认不自动持久化，需同事务执行的 Handler 在最外层 UoW 内 Commit 前执行、不嵌套 UoW/不独立 Commit/不调用外部 Provider；Application Event 仅 Commit 后本地 best-effort 通知（LOCAL/BEST-EFFORT/NON-DURABLE，不承担必须执行工作）；必须执行工作用 DQ-09 Durable Work Intent，可靠跨边界事实用独立 Transactional Integration Event Outbox（与业务状态/Audit 同 PostgreSQL 事务写入，Delivery = at-least-once，不承诺 exactly-once；Consumer 依 Event Identity + Consumer Scope 去重，Dedup Marker 与消费业务更新同事务；Outbox 与 Work Intent 不共用 Identity/状态机/Payload/Retry/Retention）；CloudEvents-compatible Envelope 仅可选互操作方向，不替代 Outbox/原子提交/Dedup/Delivery Guarantee；Observability Event 归 RFC-007 非权威 Telemetry（失败不回滚业务、不替代 Audit）；六类分类 / Audit Capability / State Transition 共用 Audit Ledger / Application Event best-effort / Outbox 结构 / Classification Table 均为项目 Accepted Decision（非第三方官方强制架构）；Audit Ledger / State Transition / Outbox 不构成 Business Current Truth，不引入 Event Sourcing（Current Truth 留 DQ-11）；Event & Record Classification Table 为持久化实现前置 Architecture Readiness Package 必备——REQUIRED 但 NOT AUTHORIZED；不新增独立 Matrix 或 Technical Spike，DQ-07 真实 PostgreSQL 多 Worker Spike 继续有效并覆盖 Integration Event 重复投递 / Consumer Dedup / Relay Crash / stale Publish / 无部分业务写入；Event Relay/Broker/Polling/发布状态机/Dead-letter 留 RFC-003，Retention 留 DQ-15，测试留 DQ-16，Security 留 DQ-17；原分歧 审计 vs 事件分离与持久化 | Fowler Audit Log≠Domain Event（权威模式）；项目用户决定 |
| DQ-11 | Snapshot vs History | **已决定（2026-08-02 ACCEPTED）**：Candidate A（Accepted with Major Revision）——Formal Model = **Authoritative Current Truth + Immutable Business Version Snapshots + Append-only Audit/State Transition History + Optional Derived Query Projections**；Candidate B 完整 Event Sourcing 拒绝（违反 DEC-013）、Candidate C 仅当前状态覆盖拒绝（违反 DEC-024）、Delta-only Version History 不作权威历史模型；正式 Business Version 逻辑完整、不可变、独立可读，不依赖事件/Delta 链重放，不经后来变化的 Current Truth Pointer 解释历史；只有成功 Atomic Business Commit 产生正式版本（DB/Work/Provider Retry、Lease、Checkpoint、回滚事务、未提交 LLM 临时结果不得创建）；Current Truth 由带独立 `revision` 的显式 Current Truth Pointer 经 CAS 选择（`MAX(version_number)` 禁止；latest created/approved 与 current effective 语义分离）；Invalidation 不删除版本且不得静默回退（显式 No Current Truth/Promote/Replacement/Restore）；Restore 为新前向 Business Command（新 `domain_version_id`/`version_number`/`command_id`/Audit + `restored_from_version_id`，非数据库 Rollback）；Query Projection 为派生非权威读取模型；通用 Bitemporal Model / SQL AS-OF 不纳入 MVP；五种 Snapshot 术语语义分离；Aggregate / Invariant Matrix 扩展为 REQUIRED 但 NOT AUTHORIZED，不新增独立 Matrix/Spike（现有 DQ-07 Spike 覆盖版本分配/Pointer CAS/Invalidation/Restore 竞争，仍未授权）；原分歧 版本化历史 vs 完整 ES vs 仅当前状态 | DEC-013 排除 ES；DEC-024 不删除历史 |
| DQ-12 | Source & Evidence Persistence | **已决定（2026-08-02 ACCEPTED）**：Candidate A（Accepted with Major Revision）——Formal Model = **PostgreSQL Authoritative Source/Evidence Graph + Immutable Content-addressed Source Blobs + Versioned Derived Artifacts and Fragments + Explicit Evidence-to-Claim Links + Rebuildable Non-authoritative Retrieval Index**；Candidate B（全部内容无条件存 PostgreSQL 通用策略）与 Candidate C（全部内容无条件存对象存储仅 DB 引用通用策略）均拒绝；Source/SourceVersion/ContentObject/Acquisition/DerivedArtifact/Fragment/EvidenceLink/Retrieval Index Entry 身份分离（不得通用 `document_id` 合并）；物理 ContentObject 可按 Content Hash 去重但不得合并不同 Source/SourceVersion/Acquisition/Provenance/权限/Evidence Link；PostgreSQL 保存全部权威身份/状态/Provenance/Hash/Fragment/Evidence Link 与对象引用（唯一权威）；中小原始文本/规范化文本/结构化元数据可依显式 Storage Classification Policy 存 PostgreSQL，大型/二进制/流式/对备份影响显著的原始内容用不可变对象存储；TOAST 仅透明物理机制不作业务大小边界，PostgreSQL Large Object 不作 MVP 默认路径；Raw/Normalized/Parsed/Canonical Fragment/Retrieval Chunk 分离——Raw 不可变，Parser/Normalizer/OCR/Chunking 变化创建新 DerivedArtifact/FragmentSet 不覆盖旧结果；每 ContentObject 记录 Hash Algorithm + Content Hash + Byte Length + Media Type（Raw/Normalized Hash 分别计算，对象存储 ETag 不作项目权威 Content Hash）；外部 Blob 优先内容寻址 + 条件创建 + 不可覆盖 Key；不假设 PostgreSQL 与对象存储分布式事务——Prepare Content → Upload Immutable Object → Verify Checksum/Presence → Finalize Metadata in Short PostgreSQL Transaction（数据库不得提交指向未验证对象的正式 SourceVersion；上传成功而 DB Commit 失败只产生待 Reconciliation 的未引用 Orphan，不产生 Business Current Truth；正式引用后对象缺失/损坏 = Integrity Incident，不得静默切换 URL 最新内容或其他 SourceVersion）；EvidenceLink 显式指向不可变 SourceVersion 及适用 Canonical Fragment/Typed Selector（不得指向 Source Current Pointer/URL 最新内容/Pending SourceVersion/未验证对象/仅 Vector ID）；Evidence Links 与 Business Version/Current Truth Pointer 等适用参与者同一 DEC-035 Atomic Business Commit；Retrieval Index 属 RFC-005 派生/可重建/非权威（Embedding/Vector ID/Ranking Score/Search Result 不等于 Evidence；正式提交前回链验证 PostgreSQL SourceVersion/Fragment/Hash/Availability/业务不变量；Index 延迟/损坏/重建不改变 Current Truth 或既有 Evidence Link）；跨 Tenant/Security Domain Content Hash 去重在 DQ-17 决定前不得启用；Retention/Orphan Grace Period/Legal Hold/物理删除留 DQ-15，Encryption/Redaction/PII/对象 Key 安全/跨安全域去重留 DQ-17；**Source & Evidence Storage Classification Table 为 Architecture Readiness Package 必备——REQUIRED 但 NOT AUTHORIZED**；**External Object Consistency Technical Spike（条件写/Checksum/Multipart/Crash Window/Orphan Reconciliation/Missing/Corrupt Object/真实 Provider 一致性）为外部对象存储实现前置——REQUIRED BEFORE EXTERNAL STORAGE IMPLEMENTATION 但 NOT AUTHORIZED**；不新增独立 Matrix；原分歧 原始内容存 DB vs 引用 + 大内容边界 | DEC-025 Source/Evidence 语义；DEC-012 原始与解析分离；DEC-024 Retrieval Index 独立存储；PG TOAST/Large Object 官方能力 |
| DQ-13 | Workflow Checkpoint Separation | **已决定（2026-08-02 ACCEPTED）**：Candidate A（Accepted with Major Revision）——Formal Model = **Shared PostgreSQL Service + Isolated Checkpoint Persistence Plane + Dedicated Role/Connection Pool/Storage Namespace + Application-owned Workflow Execution Registry + Business-Current-Truth-first Reconciliation**；Candidate B 独立 PostgreSQL 服务/独立基础设施不作 MVP（Fallback = 同一 PostgreSQL Service 内独立 Checkpoint Database，不等于 Candidate B）；Candidate C 同表混存拒绝；优先物理形态 = 同 Database + Dedicated Checkpoint Schema（但必须用钉定的 Python PostgresSaver + 实际 Psycopg Pool + 部署 Pooler 证明 Setup 与全部运行时 SQL 落预期 Schema，不得仅凭文档推测；无法稳定保证则用 Dedicated Checkpoint Database Fallback）；Business Persistence / Application-owned Workflow Execution Registry / Vendor Checkpoint Tables 三平面分离（不得通用 Workflow 表/State JSON/ORM Model 合并）；独立 Business Pool 与 Checkpoint Pool、Checkpoint Role 最小权限、Checkpoint Connection 不进 Business UoW；Workflow Execution Registry 显式映射 workflow_run_id/thread_id/command_id/stage_run_id/目标业务对象/Base Domain Version/Expected Revision/Input Fingerprint/Runtime Lifecycle/Reconciliation Status/Graph Definition Version/Checkpoint Schema Version；workflow_run_id/thread_id/checkpoint_id/command_id/stage_run_id/attempt_id/dispatch_id/domain_version_id/Idempotency Key 身份分离（thread_id 不得作业务身份/Idempotency Key/执行锁）；Checkpoint = Runtime Recovery State only，≠Business Current Truth/Business Version/Audit/Idempotency/Work Intent/执行锁；Business Commit 与 Checkpoint Write 不构成同一 Atomic Transaction（Checkpoint 成功不表业务成功、Checkpoint 缺失不表业务未发生）；Resume/Retry/Human Interrupt 恢复/Time Travel Fork 前必须 Load Registry+Checkpoint+Current Truth 并验证身份版本后分类；Reconciliation 至少区分 RESUMABLE/ALREADY_COMMITTED/STALE/SUPERSEDED/INVALIDATED/ORPHANED/INCOMPATIBLE/CORRUPT（只有 RESUMABLE 可继续原 Thread、Stale Checkpoint 不覆盖新 Current Truth）；Checkpoint 不承担并发控制（执行所有权 = DQ-07 Lease+Attempt ID+Fencing Token，最终 Business Commit 重新验证 Fencing Token）；Graph Time Travel/Fork ≠ DQ-11 Business Restore（Fork 入正式状态须转 Intentional Rerun 创建新身份 + 新 DEC-035 Atomic Business Commit）；Checkpoint Payload 仅保存最小 Runtime State + 严格 Serializer Allowlist（不存 Session/UoW/Repository/ORM Entity/Connection/Coroutine/未脱敏 Secret/长期 Token/完整 PII）；Durability Mode 逐节点策略留 RFC-003（exit 禁用于 Human-in-the-loop/需故障恢复生产流程，sync 为 Interrupt/Human Review/Provider 结果落地/正式业务提交边界默认安全方向）；PostgresSaver Setup 经受控部署/Migration Job、不得所有 Worker 启动并发执行、Vendor Migration 与 Business Alembic 分离、Package 必须钉定；Checkpoint 可清理但仅 Terminal/无 Lease/无 Pending Resume/无 Interrupt/无 Incident-Legal Hold 的 Thread 可删（默认 Whole-thread Lifecycle Deletion，未验证 Package Version/Checkpoint Chain/DeltaChannel 完整性禁止 Partial Pruning，删除不改业务数据）；Encryption/Redaction/PII 留 DQ-17、Retention 留 DQ-15、测试留 DQ-16、Serializer 安全细节留 DQ-17/RFC-003；**Workflow Checkpoint Boundary & Reconciliation Table 为持久化实现前置——REQUIRED 但 NOT AUTHORIZED**；**Workflow Checkpoint Isolation & Reconciliation Technical Spike（钉定 PostgresSaver/Schema-Database Isolation/Role/Pool/Setup/Crash Window/并发 Resume/Stale Reconciliation/Serializer/Cleanup）为 Checkpoint 实现前置——REQUIRED BEFORE CHECKPOINT IMPLEMENTATION 但 NOT AUTHORIZED**；不新增独立 Matrix；原分歧 同库/分库、生命周期、对账权威 | DEC-023/024 Checkpoint 仅恢复≠Current Truth；DEC-033 Reconciliation；PostgresSaver 官方无同库建议 |
| DQ-14 | Schema Evolution & Migrations | **已决定（2026-08-03 ACCEPTED）**：Candidate A（Accepted with Major Revision）——Formal Model = **Alembic-managed Business Schema Migrations + Single Business Migration Lineage + Forward-recovery-first Production Policy + Expand-Migrate-Contract Rolling Compatibility + Resumable Application-owned Data Backfills + Explicit Destructive/Non-transactional DDL Gates + Separate Vendor Migration Lifecycles**；Candidate B 不作通用生产恢复保证（"所有 Migration 应支持安全 Downgrade" 方向拒绝；明确可逆、无数据损失且经真实 PostgreSQL 测试的 Migration 可选择性提供安全 Downgrade）；Candidate C 作为唯一 Migration System 拒绝（受治理 Alembic Revision 内允许人工编写 PostgreSQL SQL，不绕过 Revision Graph/Review/Deployment Gate/Migration History）；Migration Ownership（唯一 Migration Capability/Deployment Pipeline/受控 Migration Job 执行；Web/Background/Workflow Worker 不启动自动 upgrade head；Migration Role 与 Runtime Role 分离）；Single Business Migration Lineage（Merge/Release Gate 单一 Alembic Head；Multiple Heads 经 Rebase/重新生成 Revision/显式 Merge Revision 解决，不修改已发布历史 Revision；PostgresSaver Vendor Migration 不伪装成 Business Alembic Head）；Migration History Immutability（已执行 Revision 不可变发布记录，修复创建新 Forward Repair Revision；Migration History Immutability ≠ Business Version Immutability）；Autogenerate Discipline（仅作 Candidate Generator 必经人工审查；Rename/Type/Default/Nullable/Constraint/Index/FK/Enum/Schema/Partition/Data Migration/Drop 显式检查；drop_table/drop_column/drop_constraint 未过 Destructive Gate 不入生产；Autogenerate 排除 Vendor Checkpoint Tables）；Schema Drift Gate（alembic check 检测可识别 Metadata Drift，非 Migration 安全证明）；Forward-recovery-first（生产恢复不依赖通用 Schema Downgrade，默认 Rollback Compatible Application + Keep Expanded Schema + Forward Repair Migration）；Rollback 术语分离（Application Rollback/Schema Downgrade/Forward Repair/Database Restore/PITR/DQ-11 Business Restore 独立语义）；Reversibility Classification（REVERSIBLE_SCHEMA/FORWARD_FIX_ONLY/DATA_IRREVERSIBLE/NON_TRANSACTIONAL_DDL/DESTRUCTIVE_CONTRACT/VENDOR_MANAGED）；Expand-Migrate-Contract（Expand 与 Contract 不同一次发布；Contract 前证明旧 Application 退出+Backfill 完成+验证通过+兼容窗口关闭）；Resumable Backfill（大型 Backfill 不入长 Alembic Transaction；独立 backfill_run_id/批次游标/Lease/Attempt/Fencing/进度/验证，分批提交/暂停/恢复/幂等重试；遵循 DQ-07 Lease+Fencing 与 DQ-08 Idempotency；Technical Backfill ≠ Business Semantic Change，后者经正式 Business Application Contract+Audit+版本化规则）；PostgreSQL 低锁策略（大型表 Add Nullable Column；NOT VALID→修复→VALIDATE；CREATE INDEX CONCURRENTLY 独立 Non-transactional Boundary+Invalid Index Recovery；Type Change 默认 Shadow Column+Dual Write+Backfill+Cutover+Contract；Lock/Statement Timeout+资源预算）；Destructive Gate 与 Non-transactional DDL Gate（Drop Table/Column/Constraint/Type Narrowing/不可逆转换/Enum 删除/强制 Constraint/Partition Drop/大规模重写经显式 Gate；Non-transactional DDL 独立 Revision/Step，失败不自动回滚须验证实际状态）；Vendor Migration Separation（Business Alembic ≠ PostgresSaver Vendor Migration ≠ Retrieval Index Rebuild ≠ Object Storage Lifecycle）；Schema Version Identity Separation（alembic_revision ≠ domain_version_id/version_number/revision/checkpoint_schema_version/event_schema_version/payload_schema_version；Alembic Head ≠ Backfill/Validation/Contract 完成）；Deployment Protocol（Preflight→Expand→Compatible Application→Backfill→Verify→Switch Read→End Compatibility Window→Contract；Web/Worker 不自动执行 Migration；Offline SQL 对应正式 Revision 与 Target 版本）；CI 最低 Gate（单一 Business Head/alembic check/fresh+baseline upgrade/revision graph/offline SQL reviewable/destructive gated/vendor schema excluded）；**Schema Migration Compatibility & Risk Table 与 Schema Migration Rollout & Recovery Technical Spike 为实现前置条件——均 REQUIRED 但 NOT AUTHORIZED**；不新增独立 Matrix；原分歧 forward-only vs downgrade、autogenerate 纪律 | DEC-024 版本化语义；Alembic autogenerate 必须人工 review；PG 快速加列/CREATE INDEX CONCURRENTLY/NOT VALID+VALIDATE 两段式 |
| DQ-15 | Data Retention & Deletion Boundary | **已决定（2026-08-03 ACCEPTED）**：Candidate A（Accepted with Major Revision）——Formal Model = **Classified Retention & Disposition Policies + Purpose/Legal-basis-driven Retention Clocks + Reference-aware Deletion Eligibility + Legal/Security/Incident Hold Overrides + Normal-lifecycle Immutability for Business History + Governed Exceptional Erasure/Redaction Paths + Idempotent Auditable Purge Orchestration + Separate Primary/Object/Index/Checkpoint/Backup Lifecycles**；Candidate B Universal TTL 拒绝（违反数据语义与历史要求）；Candidate C Universal Permanent Retention 拒绝（不可持续且可能与 Retention-limitation 义务冲突）；每类数据独立 Retention Policy（Purpose/Owner/Trigger/Clock/Required Horizon/Permitted Horizon/Blockers/Hold/Disposition/Verification/Storage-plane Treatment），不设置或虚构具体保留周期（`PERIOD NOT DECIDED`）；Invalidation/Supersession/Archive/Access Restriction/Redaction/Pseudonymization/Anonymization/Tombstone/Logical Deletion/Physical Purge/Backup Expiry 语义独立（业务删除、Source Invalidation、Evidence Retraction、Workflow Terminal 不自动等同物理删除）；Business Current Truth/Immutable Business Version/Audit/State Transition 正常生命周期不物理删除或覆盖（但不得解释为无视法律/隐私/安全要求永久保留全部个人数据；受治理 Exceptional Erasure/Redaction Path 必需，精确 PII 分离/Redaction/Anonymization/Encryption/法律例外留 DQ-17）；Retention Clock 数据类专属（不统一 created_at；Checkpoint/Idempotency/Work Intent/Outbox/Consumer Dedup/Source/Evidence/Provider Payload/Logs/Orphan Blob/Backup 各依 Terminal/Superseded/Last-required/Delivery-completed/Replay-window-closed/Legal-basis-expired/Unreferenced 事件）；删除 Reference-aware（仍被 Business Version/EvidenceLink/Audit Requirement/Legal Hold/Security Incident/Review 引用不得物理删除；Content-addressed Object 须无有效引用/无 Hold/Grace Period 完成/Reconciliation 通过；物理去重不造成跨 Tenant/跨主体/跨安全域误删；未经审查的跨业务图广泛 ON DELETE CASCADE 禁止）；Checkpoint 继续 DQ-13 Whole-thread Lifecycle Deletion（仅 Workflow Terminal/无 Lease/无 Pending Resume/无 Human Interrupt/无 Retry Window/无 Incident-Legal Hold 可删，不删 Workflow 最小终态/Business Result/Audit/Idempotency/Work Intent/Provider Call Ledger/Domain Version）；Durable Work Intent/Integration Event Outbox/Consumer Dedup/Idempotency Record 承担 Retry/Replay/Delivery/Duplicate Prevention/Incident Investigation 责任期间不删；Raw Model Prompt/Response、Provider Payload、Tool Payload、Debug Trace 不默认永久保存（Business Result/Provider Call Ledger/Raw Payload 分离）；Central Retention Governance + Decentralized Data Ownership（各业务模块为自身数据唯一所有者；中央 Purge Orchestrator 不跨模块直接 SQL 删除，经目标模块类型化 Application Contract 获取 Eligibility/执行处置/验证结果；DQ-02 唯一表所有权继续有效）；每项 Retention/Deletion 决定记录 Policy ID/Version/Data Class/Trigger/Eligible Time/Disposition/Purpose/Legal Basis/Hold/Decision Reason/Verification Result（Policy Version 可审计，修改不静默改写历史删除依据）；Legal/Security Incident/Regulatory/Dispute/Review Hold 须有 Scope/Authority/Reason/Review/Release Trail 且存在时阻止 Physical Purge（不被普通 Retention Job 自动解除）；删除请求先形成受治理 Deletion/Erasure Case（请求者权限验证→适用规则判定→数据范围发现→Reference/Hold 检查→Deletion Plan→分存储平面执行→最终验证，不映射为单次 SQL DELETE，不自动包含其他主体/Tenant 数据）；Purge Worker 遵循 DQ-07 Lease/Fencing 与 DQ-08 Idempotency，分批短事务 + Crash Recovery，状态至少区分 Requested/Assessing/Blocked/Held/Eligible/Purge In Progress/Primary Purged/Derived-Object Purged/Backup Expiry Pending/Completed/Failed（重复执行不扩大删除范围或删除新合法引用）；Application Inaccessibility/Logical Database Deletion/Physical Storage Reclamation/Backup Expiry 分离（SQL DELETE Commit 不表底层字节立即消失；Primary 删除完成不表 Backup/PITR 到期；旧 Backup 恢复须隔离环境并重放已完成 Deletion Ledger 防止已删除数据重新进入生产服务）；删除后仅保留不含原敏感载荷的最小 Tombstone/Deletion Proof（Archive/Cold Storage/Encryption/Soft Delete/Access Restriction 均不得声称为 Physical Purge）；**Data Retention, Hold & Deletion Policy Table 为 Architecture Readiness Package 必备——REQUIRED 但 NOT AUTHORIZED**（不授权创建该表或填写具体期限）；**Retention & Deletion Safety Technical Spike（Reference/Hold、Checkpoint 删除、多引用 Content Object、跨存储 Crash Window、Backup Restore Deletion Replay、幂等重试、跨主体误删防护）为首个生产 Purge 实现前置——REQUIRED BEFORE PRODUCTION PURGE IMPLEMENTATION 但 NOT AUTHORIZED**；不新增独立 Matrix；原分歧 分类定责 vs 统一 TTL vs 全部保留 | DEC-013/025 保留周期未确认；DEC-024 历史不删除；checkpoint 无内建 TTL |
| DQ-16 | Persistence Testing Strategy | **已决定（2026-08-03 ACCEPTED）**：Candidate A（Accepted with Major Revision；Accepted Principle = Layered Test Strategy）——Formal Model = **Pure Domain/Application Unit Tests + Port Contract Parity Tests + Real PostgreSQL Persistence Acceptance Tests + Deterministic Multi-connection Concurrency Tests + Real Migration/Upgrade/Recovery Tests + Crash-window/Fault-injection Tests + Production-topology-specific Qualification**；Candidate B 全部真实 PostgreSQL 通用策略拒绝（REJECTED AS A UNIVERSAL ALL-TESTS-USE-POSTGRESQL POLICY）；Candidate C 全部 SQLite fake 拒绝（All-SQLite testing cannot prove PostgreSQL semantics）；Pure Domain Unit Test 不使用数据库；Application Test Double（In-memory Fake/Stub/Spy/Deterministic Clock/ID Generator）仅证明 Application Contract（不证明 SQL Constraint/Transaction Atomicity/Commit Visibility/Lock/MVCC/CAS/Migration/Idempotency/Crash Recovery）；**SQLite 仅为可选非权威开发 Test Double，不得作为 Persistence Acceptance Engine/Concurrency-Transaction-Migration-Idempotency Proof/Release Readiness Evidence**；Repository/UoW/ORM Mapping/PostgreSQL Types/Constraint/Transaction/Concurrency/CAS/Migration/Idempotency/Lease-Fencing/Work Intent/Outbox/Audit/Domain Version/Current Truth Pointer/Retention Referential Safety 正式测试必须真实 PostgreSQL（SQLite 通过不得描述为 PostgreSQL 语义通过）；可复用 Port Contract Suite（Fake Pass ≠ PostgreSQL Adapter Pass）；Test Double 必须声明 9 项差异；MVP 只测 SQLAlchemy 2.x sync + Psycopg 3 sync（Async Stack 不属 MVP 验收范围）；钉定版本 + 独立 Test Role + 隔离 Database/Schema + 不连共享开发库/生产库 + 正式 Alembic Migration + 正式默认 Isolation Level；测试证据记录 10 项元数据；单连接 SAVEPOINT Rollback Fixture 仅限不验证 Commit Visibility 的 Adapter Test（多连接/Commit Visibility/Outbox/Consumer/Pool/Deadlock/Serialization Retry/Worker Crash/Migration/Multi-worker Claim/Checkpoint/跨存储 Crash Window 必须真实 Commit；多连接测试不被永不提交外层事务包裹；并行 CI Worker 独立隔离）；并发 Actor 独立 Connection/Session/Transaction（不共享 Session）；确定性协调（Barrier/Latch/Event/Blocking Point，不主要依赖 sleep）；真实覆盖 19 类并发场景（expected_revision 竞争/CAS/Version Number 分配/唯一约束/40001/40P01/三次事务尝试/SKIP LOCKED/Lease Expiry-Takeover/Stale Fencing/Idempotency Key±Fingerprint/Duplicate Delivery/Promotion-Invalidation/Restore-New Write/Purge-New Reference）；DEC-035 Atomic Commit 经 Fault Injection 验证全有或全无（10 个注入位置；Commit Outcome Unknown 不只靠 Mock commit 抛异常）；9 类 Crash Window 覆盖；Idempotent Use Case 9 类覆盖 + 8 项验证；Migration Test 真实 PostgreSQL + 17 项覆盖（`metadata.create_all()` 不作 Migration Acceptance 唯一 Schema 来源）；Required PR Checks 含 correctness-critical PostgreSQL Transaction/Constraint/Concurrency/Idempotency/Migration（Scheduled/Manual Tier 仅限高强度 Contention/长 Recovery/Live Provider/Backup Restore/Performance/Soak；correctness-critical Invariant 不只 Nightly）；**禁止自动 Retry-to-green**（Application Retry Under Test ≠ CI Test Retry；Flaky Required Check 视为测试或架构缺陷；并发失败报告含 Seed/Timeline/SQLSTATE/Retry Count/Final Rows 等）；合成测试数据（无生产 PII/真实 Credential/真实 Provider Token/真实 Checkpoint/Prompt Payload；受控 Secret Injection；失败日志 Redaction；精确 Fixture 规则留 DQ-17）；**Persistence Test Coverage & Fidelity Table 为 Architecture Readiness Package 必备——REQUIRED 但 NOT AUTHORIZED**（18 项字段）；**不新增独立通用 Technical Spike**（已有 5 项专项 Spike 继续有效并共享合格真实 PostgreSQL Test Harness 原则）；**Common Persistence Test Harness Qualification 必须作为第一个获授权 Persistence Spike 的组成部分——NOT AUTHORIZED**；不授权创建 Harness/Container/CI Job/Fixture/Contract Suite/测试代码/基础设施；原分歧 真实 DB vs SQLite fake、测试分层 | 架构基线 §14.9 测试基线；DEC-022 并发需真实验证；R-1 GAP；SQLite 全库单写者 vs PG 行级 MVCC |
| DQ-17 | Security & Sensitive Data Boundary | **已决定（2026-08-03 ACCEPTED）**：Candidate A（Accepted with Major Revision）——Formal Model = **Classified Sensitive-data Protection + Secret-reference-only Persistence + Ephemeral Adapter-scoped Secret Resolution + Data-minimized Multi-plane Propagation + Strict Allowlisted Checkpoint Serialization + Least-privilege Role/Credential/Pool Separation + Selective Envelope Encryption by Protection Profile + Infrastructure Encryption in Transit/at Rest + Auditable Access/Redaction/Rotation/Incident Response**；Candidate B = NOT SELECTED AS UNIVERSAL FIELD ENCRYPTION（Selective Authenticated Envelope Encryption = CONDITIONAL ON DATA PROTECTION PROFILE）；Candidate C = REJECTED AS SOLE SECURITY CONTROL（Infrastructure At-rest Encryption 保留为 REQUIRED INFRASTRUCTURE DEFENSE IN DEPTH，不替代应用控制）；SECRET ≠ PII ≠ SENSITIVE BUSINESS DATA ≠ PUBLIC/INTERNAL 语义独立；Secret Value 禁止进入 Domain/Command/Current Truth/Business Version/Graph State/Checkpoint/Registry/Audit/State Transition/Event/Outbox/Work Intent/Idempotency/Fingerprint/Source/Evidence/Index/Cache/Log/Trace/Metric/Error/Test Snapshot/Object Key 等任何持久化或派生存储；仅允许无明文能力引用（credential_ref/secret_reference_id 等）；Secret 解析 = ephemeral/adapter-scoped（Application 仅知 Credential Profile，不得获取 Secret Value）；数据分类 = Confidentiality Level（PUBLIC/INTERNAL/CONFIDENTIAL/RESTRICTED）+ Handling Tags（PII/PROVIDER_PAYLOAD/MODEL_CONTENT/USER_CONTENT/LEGAL_HOLD/SECURITY_INCIDENT/EXPORT_RESTRICTED/AUTH_CREDENTIAL），SECRET 为独立禁止持久化特殊类别；分类规则传播至全部 17 类持久化平面（不得只分类 PostgreSQL Column）；SecretStr/Masked repr ≠ Non-persistence Guarantee（由类型边界/架构测试/Serializer Allowlist/Sink Redaction/禁止路径共同强制）；LANGGRAPH_STRICT_MSGPACK = REQUIRED、Pickle Fallback = PROHIBITED、恶意/损坏 Checkpoint 进入 INCOMPATIBLE/CORRUPT/SECURITY_REJECTED；Encrypted Checkpoint ≠ 允许存储 Secret（实际加密范围须基于钉定版本验证）；三层加密责任（Transport REQUIRED / Infrastructure At-rest REQUIRED BASELINE 但不替代应用控制 / Selective Envelope Encryption 条件启用；UNIVERSAL FIELD-LEVEL ENCRYPTION = REJECTED）；Key 与 Ciphertext 分离（数据库不存明文 DEK/KEK/Master Key；生命周期 CREATE/ACTIVATE/ROTATE/RETIRE/REVOKE/DESTROY/COMPROMISE RESPONSE）；禁止未经治理加密（pgcrypto raw/custom AES/home-grown crypto/key 与 ciphertext 同库）；PostgreSQL Least Privilege（8 类 Role/Pool 分离；Runtime Role 非 Superuser/Table Owner/BYPASSRLS/CREATEROLE/CREATEDB；Migration Credential 不进运行时；受控 search_path + public Schema 保护）；RLS = OPTIONAL DEFENSE IN DEPTH（不替代 DQ-02/Application Authorization，本次不创建 Policy）；BUSINESS/CHECKPOINT/MIGRATION/PURGE/TEST 连接与 Credential 分离；Redaction 顺序 CLASSIFY→MINIMIZE→REDACT→SERIALIZE/EMIT/PERSIST（不得先持久化再异步清理；15 类 Sink 前 Redact；优先结构化字段与分类，不只全局 Regex）；安全 Audit 元数据（14 类行为；Audit 不记录 Secret Value/明文 Key/完整敏感 Payload/Prompt/Provider Response/Source Content）；Provider/Prompt/Model Output = 不可信敏感输入（MODEL-GENERATED ≠ SAFE TO PERSIST）；Object Key 不含 PII/Token/Secret；Content Hash ≠ 匿名化证明（低熵 Hash 存在性/Dictionary Oracle 风险须限制访问）；CROSS-TENANT/CROSS-SECURITY-DOMAIN CONTENT DEDUPLICATION = PROHIBITED FOR MVP（正式关闭 DQ-12 暂缓边界；同域去重须满足分类/访问域/Retention/Legal Hold/存在性不暴露/引用完整/DQ-12/DQ-15 兼容）；测试仅合成数据（禁止 Production Dump/真实 PII/真实凭证/Production Checkpoint/Prompt/Key/Presigned URL；Test Credential 最小 Scope/Sandbox/可撤销/不进 Fixture/Fork PR 不暴露）；Secret Detection Failure = Merge Blocker（泄漏后 REVOKE→ROTATE→INVESTIGATE→REMOVE ONLY WHEN AUTHORIZED）；DQ-15 继续拥有 Retention/Deletion Case/Hold/Purge/Backup Expiry，DQ-17 决定 Secret 不长期持久化/Encrypted Data 仍受保护/Key Destruction ≠ 未验证完整删除/Redacted Data 重识别重评估/Backup Restore 恢复 Key Version 与 Deletion Ledger/Legal Hold 不要求保留 Secret Value/Deletion Proof 不存敏感 Payload；Security Governance/业务模块/Infrastructure 三层所有权；后续边界 RFC-003（Checkpoint Runtime 配置）/RFC-004（API 认证授权传输）/RFC-006（LLM Secret 注入）/RFC-007（日志 Redaction/安全监控）/DQ-15（Retention）；**Sensitive Data, Secret & Cryptographic Control Matrix = REQUIRED / NOT AUTHORIZED**（26 项字段，不授权创建）；**New Independent DQ-17 Technical Spike = NOT REQUIRED**；**Cross-cutting Persistence Security Qualification = REQUIRED IN FIRST AUTHORIZED PERSISTENCE SPIKES / NOT AUTHORIZED**（17 项最低安全验证加入首批获授权 Spike 与 Common Harness Qualification）；**Selective Field Encryption & Key Rotation Spike = CONDITIONALLY REQUIRED / NOT AUTHORIZED**；不选择 KMS/Vault/HSM/算法/Rotation Period/Key Hierarchy；不授权创建 Encryption Adapter/Encrypted Column/Key Registry/Rotation Job/Role-Grant/RLS/Checkpoint Encryption/Redaction Middleware/Security Audit/Secret Scanner/测试/DDL/Migration/Infrastructure | RFC-001-DQ-06 Secret 边界；DEC-033 Sensitive Data Boundary；LangGraph 宽松反序列化 RCE 风险、Secret 明文序列化进 checkpoint |

---

## DQ-01：主持久化技术（Primary Persistence Technology）

- **Question：** 生产 Business Current Truth Repository 采用哪种数据库引擎与数据访问栈？
- **Why：** 业务库是所有正式业务结果、版本、审计、幂等的权威；选型直接决定并发写吞吐、部署可迁移性、JSON/检索能力与迁移成本。Spike R-1/R-4 明确「生产数据库/ORM 未选型」。
- **Constraints（[DEC 约束]）：** 三类存储逻辑分离恒定（DEC-034）；单事务多步原子提交（DEC-035）；API/Worker 两进程可分离（RFC-001-DQ-07）；Sync-first Application Core（RFC-001-DQ-07）。
- **Candidates：**
  - **A. PostgreSQL + SQLAlchemy(sync) + Alembic**：行级 MVCC、多进程并发写、jsonb+GIN、约束完备、DDL 事务性、托管可迁移。
  - **B. SQLite + SQLAlchemy(sync) + Alembic**：零配置、单文件、ACID/serializable；但全库单写者、网络文件锁不可靠。
  - **C. MVP SQLite → 后期迁 PostgreSQL**：先零配置，后期重建 PG 迁移基线 + 一次性数据搬迁。
- **Trade-offs：** A 工程成本最高但生产正确性最强；B 开发最简但 API+Worker 并发写会撞全库单写者（`SQLITE_BUSY`），托管部署受限；C 前期快但**迁移脚本不可直接复用**（Alembic 跨方言）、类型语义/并发语义/序列需重做（官方推断的真实成本，非零成本切换）。
- **Failure modes：** 选 B 在并发写下频繁 `SQLITE_BUSY`；选 C 低估迁移成本导致 schema/并发回归；选 A 在本地开发引入 Docker 依赖降低上手速度。
- **Impact on later RFCs：** RFC-003（Checkpointer 是否同实例）、RFC-005（检索索引落点）、RFC-002-DQ-14（Schema Evolution and Migrations）。
- **Recommendation（历史提案；Superseded by the Accepted Revision below）：** **[架构推断] 倾向 A（PostgreSQL 为目标生产引擎），本地开发可用 SQLite 但须以 PG 语义为准**——依据：API+Worker 两进程并发写、托管部署、DEC-024 多指针/约束/版本化的关系完整性需求，均指向行级 MVCC。**置信度：中-高**（取决于 MVP 部署形态）。其中「本地开发可用 SQLite」已被下方用户正式决定取代；Accepted Decision 不建立任何 SQLite 方言兼容承诺。
- **User Decision：** ACCEPTED WITH REVISION
- **Accepted Candidate：** Candidate A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-01 用户正式决定）：**

  > RFC-002-DQ-01 — Primary Persistence Technology Boundary
  >
  > 1. PostgreSQL 是 Business Current Truth Repository 唯一受支持的权威数据库语义（sole supported authoritative database semantics）。
  > 2. 接受的持久化技术栈为：**PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**。
  > 3. 数据库 schema、约束、迁移、事务行为、并发行为与持久化正确性均**以 PostgreSQL 语义定义**。
  > 4. 本地开发使用 PostgreSQL。
  > 5. Repository contract tests、persistence integration tests、transaction tests、concurrency tests 与 migration tests 必须**对真实 PostgreSQL 运行**。
  > 6. SQLite **不是**受支持的 Business Current Truth backend，**不是** PostgreSQL 持久化语义的权威替代。
  > 7. SQLite-first → PostgreSQL-later 迁移策略**被拒绝（REJECTED）**。
  > 8. 错误的 RFC-014 迁移引用已修正为：**RFC-002-DQ-14 — Schema Evolution and Migrations**。

---

## DQ-02：持久化所有权与模块边界（Persistence Ownership / Module Boundaries）

- **Question：** 各业务模块的表/数据所有权如何在物理数据库上划分与强制？
- **Why：** DEC-034 确立「三类 Repository 逻辑分离，即使同一物理存储也须保持逻辑边界」与「Shared Database Instance ≠ Shared Data Ownership」；须防止 DB 表退化为隐式跨模块 API。
- **Constraints（[DEC 约束]）：** 模块只经 Public Application Contract 协作（RFC-001-DQ-08）；禁止 `Consumer → Target Repository → Direct SQL/ORM`（RFC-001-DQ-08）；业务库权威（DEC-023）。
- **Candidates：**
  - **A. 单库 + 按模块分 schema/表前缀 + 架构测试强制**：表命名/归属清晰，Import/AST 测试禁止跨模块直读。
  - **B. 单库 + 仅逻辑约定（无物理隔离）**：最简，依赖代码审查与测试。
  - **C. 多物理库**：隔离最强但违背 Modular Monolith 单库倾向、增加运维。
- **Trade-offs：** A 强制力与复杂度平衡最好；B 最灵活但易腐蚀；C 过度。
- **Failure modes：** B 下跨模块直读腐蚀边界；A 下 schema 划分与模块边界错位。
- **Impact on later RFCs：** RFC-003/004/005 各模块表边界。
- **Recommendation（历史提案；Superseded by the Accepted Revision below）：** **[架构推断] 倾向 A**——以模块分逻辑边界（命名/schema），用架构测试强制「不得跨模块直读表」。**置信度：高**。Candidate A 中「按模块分 schema/表前缀」作为候选历史保留；**最终 Accepted Decision 不强制每个业务模块拥有独立 PostgreSQL schema**（见下方第 9/10 点）。
- **User Decision：** ACCEPTED WITH REVISION
- **Accepted Candidate：** Candidate A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-01 用户正式决定）：**

  > RFC-002-DQ-02 — Persistence Ownership and Module Boundaries
  >
  > 1. MVP 使用**单一 PostgreSQL 数据库服务**。
  > 2. **每张业务表有且仅有一个所有模块**（exactly one owning module）。
  > 3. 所有模块**独占拥有**：其 Repository Port 定义；其 Infrastructure Repository 实现；其 ORM / Persistence Models；其所有表的 schema 与 migration 变更；其所有数据的状态修改 Application Use Cases。
  > 4. 其他模块**不得**：import 所有模块的 ORM / Persistence Models；获取或复用所有模块的 Database Session；调用所有模块的 Repository 实现；通过 SQL 或 ORM 直接查询或修改所有模块的表；使用共享表绕过所有模块的 Public Application Contract。
  > 5. 跨模块读取必须使用目标模块的 **Public Application Query**（或等价 Public Application Contract）。
  > 6. 跨模块状态修改必须使用所有模块的 **Public Application Use Case**。
  > 7. 直接的模块间状态修改访问**默认保持禁止**（与 RFC-001-DQ-08 一致）。
  > 8. 模块所有权边界必须由以下机制强制：Import Linter；AST / Architecture Tests；Repository Ownership Tests；Migration Ownership Conventions；Pull Request 审查规则。（**单独代码审查不构成充分强制。**）
  > 9. 架构接受**显式的数据库命名空间与所有权约定**，但 **MVP 不要求每个业务模块拥有独立 PostgreSQL schema**。
  > 10. 具体物理命名策略（PostgreSQL schema、表前缀或等价命名空间）**留待实现设计**，条件是不得削弱模块所有权。（此为 Deferred，非「不需要物理命名约定」。）
  > 11. Business / Runtime / Checkpoint 三类存储的物理划分**不由 DQ-02 决定**，继续指派 **RFC-002-DQ-13**（PROPOSED / PENDING）。

---

## DQ-03：Aggregate 与持久化边界（Aggregate / Persistence Boundary）

- **Question：** 哪些实体构成一个聚合、哪些更新必须在同一原子提交内完成？
- **Why：** 原子提交单元的划分决定事务大小与一致性边界；划分过大拉长事务（撞连接 checkout/锁），过小破坏不变量。
- **Constraints（[DEC 约束]）：** Atomic Business Commit 六要素单事务（DEC-035）：`Create Domain Version + Formal Evidence Links + Update Current Truth Pointer + Update Stage State + Write Audit + Write Idempotency Record` 不可拆；Graph Node 不得绕过 BusinessCommitService。
- **Candidates：**
  - **A. 以「业务不变量 + 六要素」为聚合边界**：聚合 = 一次原子提交必须一致的最小单元。
  - **B. 以实体生命周期为聚合边界**：按对象图自然聚。
  - **C. 以页面/读写频率为聚合边界**：按访问模式切。
- **Trade-offs：** A 与 DEC-035 对齐、事务边界清晰；B 直观但可能与六要素错位；C 优化读写但牺牲一致性语义。
- **Failure modes：** 聚合过大→长事务/锁争用；聚合过小→跨聚合不变量需补偿（Saga 复杂度）。
- **Impact on later RFCs：** RFC-004（Review 提交事务）、RFC-005（Evidence Link 一致性）。
- **Recommendation（历史提案；Superseded by the Accepted Revision below）：** **[架构推断] 倾向 A**——聚合边界服务于六要素原子提交。**置信度：高**。Candidate A 中「以『六要素』为聚合边界 / 聚合 = 一次原子提交必须一致的最小单元」表述已被下方用户正式决定取代（聚合边界 = 业务不变量 + 唯一模块所有权；Atomic Business Commit 六要素是事务提交协议，**不是**聚合成员资格判据）；**DEC-035 六要素单事务约束本身作为提交协议保持有效**。
- **User Decision：** ACCEPTED WITH REVISION
- **Accepted Candidate：** Candidate A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**

  > RFC-002-DQ-03 — Aggregate and Persistence Boundary
  >
  > 1. **Aggregate 边界 = 业务不变量 + 唯一模块所有权**（Business invariants + unique module ownership）：聚合是强制同一组业务不变量的最小单元，其数据归属唯一所有模块（与 RFC-002-DQ-02 Accepted Decision 一致）。
  > 2. **Atomic Business Commit（DEC-035 六要素）是事务提交协议**（transaction protocol：一次原子提交必须包含什么），**不是聚合成员资格判据**（not aggregate membership）；六要素单事务不可拆约束保持有效。
  > 3. **Task Mega Aggregate 被拒绝（REJECTED）**——不采用「整个 Task 作为单一大聚合」。
  > 4. **默认规则：一个 Application Use Case 默认提交一个主 Aggregate**（One primary Aggregate per Application Use Case）。
  > 5. **跨聚合 / 跨模块协调要求显式协调**（Explicit coordination required；经 Explicit Composite Application Use Case，与 RFC-001-DQ-08 一致）；跨聚合不变量不得依赖隐式单事务耦合。
  > 6. **Unit of Work / 事务实现形态不由 DQ-03 决定**，移交 **RFC-002-DQ-05（Transaction Boundary）与 DQ-06（Unit of Work Model）**（均 PROPOSED / PENDING）。
  > 7. **Aggregate / Invariant Matrix（聚合、其业务不变量、所有模块与提交协议映射的枚举）是持久化实施前的必备产出（REQUIRED BEFORE PERSISTENCE IMPLEMENTATION）**；该要求不授权任何实施（Implementation = NOT AUTHORIZED 恒定）。

---

## DQ-04：Domain State Versioning（领域状态版本化）

- **Question：** 版本化 Domain Object 的版本号如何产生、并发版本如何校验、在何种隔离级别运行？
- **Why：** DEC-024 固定六类版本指针；DEC-029 明确「Optimistic Lock/Revision Number/ETag/Database Lock 尚未确认」；须为 DQ-07 并发控制提供版本底座。
- **Constraints（[DEC 约束]）：** DEC-024 版本化 Domain Object + Current Truth Pointer；DEC-029 不得静默覆盖较新 Draft。
- **[官方能力]：** SQLAlchemy `version_id_col`/`version_id_generator` 原生乐观并发——`UPDATE ... WHERE version=:old` + rowcount 检测、0 行→`StaleDataError`；**仅 flush 单行生效、批量 UPDATE 不依赖**；`version_id` 须 NOT NULL；server 端版本需后端支持 RETURNING。PG 无内建行 version 列（需应用层或引擎隔离级 40001 重试）。
- **Candidates：**
  - **A. 应用层 `version_id` 列 + SQLAlchemy `version_id_col`**：客户端 generator（UUID/递增）显式维护。
  - **B. 服务端版本（PG `xmin`/触发器）**：DB 产生，依赖 RETURNING。
  - **C. 引擎隔离级（SERIALIZABLE 40001 重试）**：不显式 version 列。
- **Trade-offs：** A 显式可控、与 client-side ID 一致（INSERT 前可知）；B 省应用代码但耦合后端、官方「strongly recommended 仅在必要时」；C 最简但重试语义重、对批量更新无效。
- **Failure modes：** A 批量更新绕过校验；B 后端不可移植；C 高冲突下重试风暴。
- **Impact on later RFCs：** RFC-003（对账读版本）、RFC-004（审核版本）。
- **Recommendation（历史提案；Superseded by the Accepted Revision below）：** **[架构推断] 倾向 A**——应用层 version 列 + ORM 乐观校验，ID/版本由 Application 产生（契合显式传值优先 + INSERT 前可知 + 幂等键）。**置信度：中-高**。**候选关系：** Candidate A 的「应用层显式版本」方向被接受并由下方用户正式决定修订；Candidate B 中「PostgreSQL `xmin` 作为权威 Revision」的方向被拒绝；Candidate C 中「以 SERIALIZABLE 取代显式 Revision」的方向被拒绝（SERIALIZABLE 仍可能作为独立事务隔离策略由后续 DQ（如 DQ-05 / DQ-07）讨论）。
- **User Decision：** ACCEPTED WITH REVISION
- **Accepted Direction：** Candidate A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**
  > RFC-002-DQ-04 — Domain State Versioning
  > 1. 架构明确区分 **Domain Version Identity**（`domain_version_id`）、**Domain Version Number**（`version_number`）与 **Concurrency Revision**（`revision`）；三者不得共享同一字段，不得被视为可互换。
  > 2. **Domain Version Identity：** 每个不可变 Domain Version 拥有稳定且全局唯一的 `domain_version_id`；标识符**由 Application 层在 INSERT 前生成**；采用应用生成的 opaque UUID（具体 UUID variant 可在实现设计时选择）；标识符不可变且绝不得复用。不得将其解释为乐观锁计数器、SQLAlchemy Mapper Version、PostgreSQL `xmin` 或审核 Revision。
  > 3. **Domain Version Number：** 每个逻辑业务对象维护单调递增的 `version_number`（例如 Strategy Version 1、2、3）；唯一性约束至少覆盖 `(logical_object_id, version_number)`；历史版本在删除或失效后不得被覆盖、重新编号或复用。`version_number` 不得默认与 `revision` 相等。
  > 4. **Concurrency Revision：** 需要并发保护的可变记录使用独立 `revision` 字段；适用记录包括 Current Truth Pointers、Aggregate Roots、Stage State、Review Package state 以及后续设计识别的其他可变协调记录；`revision` 是 NOT NULL 单调递增整数；revision 表达成功的状态变更，不代表 Domain Version Identity 或 Domain Version Number，不得用作不可变 Domain Version Identity。
  > 5. 每一个针对 revision 保护记录的状态修改 Command 必须携带 `expected_revision` 或等效的显式并发前置条件。
  > 6. 更新使用显式 compare-and-swap 语义：`UPDATE ... WHERE id = :id AND revision = :expected_revision`；成功更新递增 `revision`；若影响零行，该操作即为 stale write 或并发冲突，Atomic Business Commit 必须回滚，不得静默覆盖较新状态。
  > 7. SQLAlchemy 2.x `version_id_col` 可作为 Infrastructure 层乐观并发控制机制使用；SQLAlchemy mapper 概念、Session 异常与 `version_id_col` 细节不得泄漏进 Domain Models 或 Public Application Contracts。
  > 8. Infrastructure 必须将 SQLAlchemy 特有的 stale-state 行为（适用时包括 `StaleDataError`）转换为项目自有的并发冲突结果或异常（例如 ConcurrencyConflict / StaleRevision / ExpectedRevisionMismatch 之类的项目自有冲突语义；具体命名留待实现设计；本决定不创建任何代码）。
  > 9. revision 保护记录不得通过绕过 revision 检查的 ORM bulk UPDATE 或 DELETE 操作修改；若明确需要批量操作，必须定义其 expected revision 规则、条件更新行为与 affected-row 校验。
  > 10. PostgreSQL `xmin` 不是项目权威业务 revision：它不是 Domain Version、不是 Public Contract 字段、不是 Review Package revision、不是稳定的跨系统持久化契约（Candidate B 方向被拒绝）。
  > 11. PostgreSQL SERIALIZABLE 隔离不是显式 Concurrency Revision 的替代方案（Candidate C 方向被拒绝）。
  > 12. Transaction Isolation 与 Optimistic Revision 是正交机制；SERIALIZABLE 仍可能作为独立事务隔离策略由后续 DQ 讨论。
  > 13. 以下内容留待 RFC-002-DQ-05 与 RFC-002-DQ-07（均 PROPOSED / PENDING）：默认事务隔离级别；需要更强隔离级别的 Use Cases；40001 serialization-failure 重试策略；40P01 deadlock 重试策略；SELECT FOR UPDATE 策略；悲观锁使用；retry 所有权与重试上限。
  > 14. 在 DEC-035 Atomic Business Commit 内，以下内容保持在同一事务中（六要素不可拆保持有效）：创建新的不可变 Domain Version；创建 Formal Evidence Links；更新 Current Truth Pointer；更新 Stage State；写入 Audit Record；写入 Idempotency Record。
  > 15. Current Truth Pointer、Aggregate Root 或其他受保护协调记录的 revision 检查必须发生在同一 Atomic Business Commit 内。
  > 16. 产生新的顺序 Domain Version Number 时，版本分配与 Current Truth revision 校验必须构成一个安全提交协议：读取当前 pointer/version → 校验 expected_revision → 分配或校验下一个 version_number → 插入不可变 Domain Version → 条件更新 pointer → 递增 revision → commit；任何 revision 冲突、唯一性冲突或写入失败都使整个事务回滚。
  > 17. RFC-004 可以将 Concurrency Revision 映射为 HTTP ETag / If-Match 语义，但 HTTP 协议不由 DQ-04 决定。
  > 18. 持久化语义验证必须使用真实 PostgreSQL，并至少覆盖：两个写者使用相同 expected_revision；过期 Human Review 提交；重复 resume 尝试；Domain Version 与 Pointer 的原子更新；防止无保护的批量更新；冲突回滚且零部分业务写入。
  > 19. 详细持久化测试策略由 RFC-002-DQ-16（PROPOSED / PENDING）拥有。

---

## DQ-05：Transaction Boundary（事务边界）

- **Question：** Application Use Case 与数据库事务如何对齐？外部调用（LLM/HTTP/工具）与事务的关系？
- **Why：** 事务边界决定一致性、连接占用时长与恢复语义。DEC-033 要求安全恢复边界；连接池机制使「长事务 + 外部调用」成为真实资源风险。
- **Constraints（[DEC 约束]）：** 业务事务由 Application Use Case 拥有（架构基线 §14.3）；长 Workflow 由多个短 Application Transaction 组成（§14.12）；Entrypoint/Graph Node 不 begin/commit。
- **[官方能力]：** 事务存续期连接被独占 checkout、事务结束才归还；池上限=`pool_size`+`max_overflow`（默认 5+10）；超时 `pool_timeout` 报错。`begin_nested`=SAVEPOINT 但 2.0 下 commit 总作用最外层（嵌套「业务 commit」并不真持久化）。
- **[架构推断]：** 「外部调用应在事务边界之外、或先 commit 再做外部调用、或拆多个短事务」由 checkout/pool 机制推导——**官方未以「建议」形式写明，本条 Recommendation 标注为推断、非 Accepted。**
- **Candidates：**
  - **A. 一 Use Case 一短事务，外部调用在事务外**（分段：装载→外部调用→新事务提交）。
  - **B. Use Case 全程一个事务**：边界最简但外部调用拉长事务。
  - **C. 混合：默认短事务，关键多步用 SAVEPOINT 部分回滚**。
- **Trade-offs：** A 连接占用最短、恢复清晰但需编排外部调用位置；B 简单但资源风险；C 灵活但 SAVEPOINT 会先 flush、易误写中间态。
- **Failure modes：** B 高并发下连接池耗尽；C 滥用 SAVEPOINT 产生意外部分提交语义。
- **Impact on later RFCs：** RFC-003（节点边界）、RFC-007（超时/重试参数）。
- **Recommendation（历史提案；Superseded by the Accepted Revision below）：** **[架构推断] 倾向 A**——Use Case 拥有唯一提交点、外部调用不持有 DB 事务、长流程拆多个短事务；SAVEPOINT 仅留少数确需部分回滚场景。**置信度：中-高**。**候选关系：** Candidate A 的「一 Use Case 一短事务、外部调用在事务外（装载→外部调用→新事务提交）」方向被接受并由下方用户正式决定修订（补充 Business Transaction Owner = Application 与唯一最终提交点、四项 PROHIBITED 边界、Commit-time Revision Revalidation、External Result Before Commit 非 Current Truth、默认 PostgreSQL 隔离 = READ COMMITTED、SAVEPOINT 仅为有限 Infrastructure 机制、嵌套业务事务禁止、与外部供应商的分布式事务拒绝）；Candidate B（Use Case 全程一个事务）被拒绝；Candidate C（SAVEPOINT 作业务部分回滚机制的混合策略）作为业务事务策略被拒绝（SAVEPOINT 降级为有限 Infrastructure 机制）。
- **User Decision：** ACCEPTED WITH REVISION
- **Accepted Candidate：** Candidate A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**

  > RFC-002-DQ-05 — Transaction Boundary
  >
  > 1. **Business Transaction Owner = Application：** 业务事务由 Application 层（Application Use Case）拥有；Entrypoint（API/CLI）与 Graph Node 不 begin/commit 业务事务（与架构基线 §14.3 和 RFC-001-DQ-04 一致）。
  > 2. **Transactional Application Command = 一个短显式事务 + 一个最终提交点：** 每个事务性 Application Command 在一个短的显式数据库事务中完成状态修改，且有且仅有一个最终提交点（One short explicit transaction, one final commit point）；Use Case 是唯一提交点。
  > 3. **Long-running Business Operation = 多个短事务 + 无事务执行阶段：** 长流程业务操作（含长 Workflow）由多个短 Application 事务与无事务执行阶段组成（Multiple short transactions + transaction-free execution phases）；不存在跨越整个长流程的单一长业务事务（与架构基线 §14.12 一致）。
  > 4. **执行模式 = Prepare → Execute Outside Transaction → Commit：** 事务性 Application Command 遵循三段式——Prepare（装载所需状态；任何读取在进入 Execute 阶段前完成）→ Execute Outside Transaction（业务计算与外部调用，不持有数据库事务）→ Commit（一个新的短显式事务完成原子提交）。
  > 5. **External Calls Inside Database Transaction = PROHIBITED：** 外部调用（LLM、HTTP、外部工具/供应商 I/O）不得在持有开放数据库事务期间进行；外部调用结果必须在随后的新短事务中持久化。
  > 6. **Human Review Across Open Transaction = PROHIBITED：** 人工审核等待不得跨越开放数据库事务；进入 Human Review 前相关状态（如 Review Package state）必须已提交持久化，审核通过后 Resume 使用新事务。
  > 7. **Workflow Pause Across Open Transaction = PROHIBITED：** 工作流暂停（interrupt、suspend、waiting 状态）不得跨越开放数据库事务；恢复所需状态必须在暂停前提交持久化（与 DEC-033 Safe Resume Boundary 一致）。
  > 8. **SQLAlchemy Session Across Workflow Boundary = PROHIBITED：** SQLAlchemy Session 不得跨 Workflow 边界（节点之间、interrupt/resume 之间）持有；Session 生命周期外置于 Application Use Case 边界，Resume 以新 Session、新事务重新执行（与 DEC-033 Safe Resume Boundary 和 Checkpoint Reconciliation 一致）。
  > 9. **Commit-time Revision Revalidation = REQUIRED：** RFC-002-DQ-04 Accepted Decision 定义的 revision 保护记录 `expected_revision` compare-and-swap 校验必须在提交事务内发生（commit-time revalidation）；不得使用提交前读取阶段获得的 revision 值作为跳过重新校验的直接提交依据；零影响行 = 冲突，Atomic Business Commit 整体回滚。
  > 10. **DEC-035 Atomic Business Commit = IN FORCE：** DEC-035 六要素单事务保持有效（Commit Together or Rollback Together）；DQ-05 定义业务事务的边界与执行模式，不拆分六要素、不修改 DEC-035。
  > 11. **External Result Before Commit = NOT CURRENT TRUTH：** 提交前获得的外部调用执行结果（LLM 输出、工具输出等）不是 Business Current Truth；只有经成功提交的 Atomic Business Commit 持久化后才成为正式业务状态；提交前返回给调用方的结果不得被视为权威业务真值。
  > 12. **Default PostgreSQL Isolation = READ COMMITTED：** 项目默认事务隔离级别为 PostgreSQL READ COMMITTED（即 PostgreSQL 默认隔离级别）；DQ-04 第 13 点留待 DQ-05/DQ-07 的「默认事务隔离级别」空白由本点正式决定。
  > 13. **Stronger Isolation / Locks / Retry Policy = DEFERRED TO DQ-07：** 需要更强隔离级别（如 SERIALIZABLE / REPEATABLE READ）的 Use Cases、悲观锁、SELECT FOR UPDATE / SKIP LOCKED 策略、40001 serialization-failure 重试、40P01 deadlock 重试、retry 所有权与重试上限，均留待 RFC-002-DQ-07（PROPOSED / PENDING）；DQ-05 不决定任何锁策略或重试策略。
  > 14. **SAVEPOINT = LIMITED INFRASTRUCTURE MECHANISM ONLY：** SAVEPOINT（SQLAlchemy `begin_nested`）仅可作为有限的 Infrastructure 层机制使用（少数确需事务内部分回滚的场景）；它不是业务事务机制、不构成嵌套业务事务；其提交语义须服从 SQLAlchemy 2.0 官方行为（commit 总作用最外层事务）。
  > 15. **Nested Business Transaction = PROHIBITED：** 嵌套业务事务被禁止；业务提交点不得嵌套；不得以 SAVEPOINT 构造嵌套的「业务 commit」语义。
  > 16. **Distributed Transaction with External Providers = REJECTED：** 与外部供应商（LLM provider、外部 HTTP 服务、消息 broker 等）协调的分布式事务 / 两阶段提交被拒绝；业务写入与外部效果之间的一致性经由 DQ-05 决定的事务边界模式（先提交再外部效果，或外部执行后再新事务提交）与幂等 / Durable Dispatch 机制（DQ-08/09，PROPOSED / PENDING）实现，不经由分布式事务。

---

## DQ-06：Unit of Work Model（工作单元模型）

- **Question：** Unit of Work Port 的形态、接口位置、Commit/Rollback 负责方、是否禁止嵌套业务事务？
- **Why：** UoW 是「Use Case 拥有事务」的落地机制；须与 SQLAlchemy Session 语义对齐且把生命周期外置。
- **Constraints（[DEC 约束]）：** UoW Port 由 Application 定义、Infrastructure 实现（RFC-001-DQ-04）；业务事务由 Use Case 拥有。
- **[官方能力]：** Session 天然 = UoW + identity map（commit 先 flush）；官方要求 Session 生命周期「separate and external」于数据访问代码、事务要短、非并发（Session per thread）；官方给 per-request 范例（**未用「per use case」措辞**）。
- **Candidates：**
  - **A. 显式 UoW 抽象（`UnitOfWork` Port + Use Case 边界 commit）**：Use Case 调用 `uow.commit()`。
  - **B. 隐式 UoW（装饰器/上下文管理器包裹 Use Case）**：边界自动 commit。
  - **C. Repository 内部自管理事务**：反模式（违反 Use Case 拥有）。
- **Trade-offs：** A 显式可控、与「唯一提交点」对齐；B 简洁但提交点隐式；C 违反 DEC。
- **Failure modes：** 嵌套业务事务导致「以为已提交实际未提交」；UoW 泄漏给 Graph Node/Entrypoint。
- **Impact on later RFCs：** 全部（UoW 是所有写路径基础）。
- **Recommendation（历史提案；Superseded by the Accepted Revision below）：** **[架构推断] 倾向 A 显式 UoW、禁止嵌套业务事务**（SAVEPOINT 仅基础设施级部分回滚）。**置信度：高**。**候选关系：** Candidate A 的「显式 UoW 抽象（`UnitOfWork` Port + Use Case 边界 commit）」方向被接受并由下方用户正式决定修订（补充：UnitOfWork Port 由 Application 定义、Infrastructure SQLAlchemy 实现、Session 为不暴露的 Infrastructure 细节、一次性生命周期状态机、一 UoW 对应一 Session/一短事务/一最终结果、显式 commit 且 Context 退出不得自动提交、未 commit 或异常退出必须 rollback/close/discard、Repository 无 begin/commit/rollback/close/SAVEPOINT 权限且不暴露 Session、禁止 Registry/Service Locator/动态 lookup、嵌套业务 UoW 禁止且检测必须立即失败、Composite Application Use Case 唯一外层 UoW 与唯一最终提交点、ACTIVE 期间禁止 ambient/全局/第二个 UoW、SAVEPOINT 与 flush 边界、Engine/sessionmaker 长生命周期 vs concrete Session 短生命周期、禁止 scoped_session/thread-local/ContextVar ambient 机制、并发执行独立 UoW/Session、与 DQ-05 的 Prepare/Commit/Workflow 边界一致、纯读 Query Scope 独立短生命周期、测试覆盖要求与剩余所有权分配）；Candidate B（装饰器/上下文管理器退出自动 commit 的隐式 UoW）作为项目 UnitOfWork 模型被拒绝（Context Manager 仍允许用于生命周期清理，但不得自动提交业务状态）；Candidate C（Repository 内部自管理事务）被拒绝（违反 Application 事务所有权与单一提交点）。
- **User Decision：** ACCEPTED WITH REVISION
- **Accepted Candidate：** Candidate A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**

  > RFC-002-DQ-06 — Unit of Work Model
  >
  > 1. **UnitOfWork Port 由 Application 层定义**（The UnitOfWork Port is defined by the Application layer）。
  > 2. **生产 UnitOfWork 实现属于 Infrastructure 层，可使用 SQLAlchemy**（The production UnitOfWork implementation belongs to the Infrastructure layer and may use SQLAlchemy）。
  > 3. **SQLAlchemy Session 是 Infrastructure 实现细节**（an Infrastructure implementation detail）。Session 不得暴露给：Domain Models 或 Domain Services；Application Use Cases；Entrypoints 或 API handlers；LangGraph nodes 或 Workflow adapters；Public Application Contracts；外部 Provider adapters。
  > 4. **每个 Transactional Application Command 创建一个新的 UnitOfWork 实例。**
  > 5. **一个 UnitOfWork 实例对应**：一个短数据库事务；一个 SQLAlchemy Session；一个显式业务状态迁移；一个最终 commit 或 rollback 结果。
  > 6. **UnitOfWork 是一次性生命周期对象**（one-shot lifecycle object）：NEW → ACTIVE → COMMITTED or ROLLED_BACK → CLOSED。
  > 7. **UnitOfWork 在 commit、rollback 或 close 之后不得重用。**
  > 8. **UnitOfWork 可暴露显式上下文边界**（conceptually：`with uow_factory() as uow: ... uow.commit()`）。
  > 9. **Application Use Case 必须显式调用 commit()。**
  > 10. **正常 context-manager 退出不得自动提交**（Normal context-manager exit must not automatically commit）。
  > 11. **未成功显式 commit 即退出 UnitOfWork 作用域，必须**：回滚活动事务；关闭并丢弃 Session；释放数据库连接；使 UnitOfWork 不可用。
  > 12. **Use Case 抛出异常时，UnitOfWork 必须**：回滚；关闭并丢弃 Session；释放连接；在 Application 错误边界保留或翻译原始失败。
  > 13. **Application 可在必要时显式请求 rollback**，但强制安全规则不变：exception or exit without commit → rollback → close → discard。
  > 14. **每个 Transactional Application Command 最多成功 commit 一次。**
  > 15. **非法生命周期操作必须显式失败**，包括：第二次 commit；成功 commit 之后 rollback；close 之后访问 Repository；rollback 之后使用事务；重用失败的 UnitOfWork；跨 Workflow 边界重用 UnitOfWork。
  > 16. **UnitOfWork 仅暴露所属 Application 能力或事务性操作所需的显式、类型化 Repository Ports。**
  > 17. **UnitOfWork 不得提供**：`get_repository(name)`；通用 repository 字典或 registry；Service Locator；raw Session accessor；通用 `execute_sql()`；任意跨模块 Repository lookup；按字符串或运行时类型的动态 Repository 解析。
  > 18. **每个业务模块继续拥有**其 Repository Ports、Infrastructure Repository 实现、ORM models 与 tables（与 RFC-002-DQ-02 一致）。
  > 19. **参与同一 UnitOfWork 的 Repositories 内部共享**同一 Infrastructure 事务与 Session，但该 Session 不得经其公共接口暴露。
  > 20. **Repository 实现不得调用或控制**：`begin()`；`commit()`；`rollback()`；`close()`；`begin_nested()`；SAVEPOINT 生命周期；UnitOfWork 生命周期迁移。
  > 21. **Repository 职责限于**：加载其 Port 允许的 Aggregates 或持久化记录；在当前 UoW 内暂存或持久化 Aggregate 变更；执行所属模块允许的查询；返回项目自有的 Domain/Application 结果；将持久化失败传播到 UoW/Application 边界。
  > 22. **嵌套业务 UnitOfWork 被禁止**（Nested Business UnitOfWork is prohibited）。
  > 23. **已拥有活动 UnitOfWork 的 Transactional Application Use Case，不得调用另一个会创建新 UnitOfWork 或独立提交的 Transactional Use Case。**
  > 24. **可复用业务行为必须改为提取为**：Domain Service；transaction-neutral Application Service；接收显式 Ports 的内部 Application 操作；在既有外层 UoW 下执行的另一个操作。
  > 25. **当多个操作必须参与同一个即时一致性事务时，由 Explicit Composite Application Use Case 拥有唯一外层 UnitOfWork 与唯一最终提交点。**
  > 26. **Composite Application Use Case 必须**：记录跨 Aggregate 业务不变量；使用显式类型化 Repository Ports；保持唯一模块与表所有权；在模块边界需要处使用 Public Application Contracts；避免共享全局 Session 状态；避免多个嵌套 UnitOfWork 实例；保留唯一外层提交权威。
  > 27. **UnitOfWork 处于 ACTIVE 期间，禁止**：隐式加入另一个 ambient UnitOfWork；打开第二个业务 UnitOfWork；把子操作的 commit 解释为部分提交；以 SAVEPOINT 作为嵌套业务 commit；把 commit 所有权移交给 Repository；把 UnitOfWork 存入全局、thread-local 或 Workflow 状态。
  > 28. **检测到嵌套业务 UnitOfWork 企图必须立即失败**，经由项目自有的架构或事务错误（确切错误名留待实现设计）。
  > 29. **SAVEPOINT 不是嵌套 UnitOfWork，也不由 Application UnitOfWork Port 暴露。**
  > 30. **任何有限的 Infrastructure 级 SAVEPOINT 使用仍受 RFC-002-DQ-05 治理，且不得**：创建独立业务 commit；拆分 DEC-035 Atomic Business Commit；包裹外部调用或等待期；授予 Repository 提交权威；削弱失败即回滚语义。
  > 31. **UnitOfWork Port 默认不暴露 flush()。**
  > 32. **Infrastructure 可在数据库约束、生成值或持久化排序需要时执行内部 SQLAlchemy flush。**
  > 33. **内部 flush 不是业务 commit，不得表示为业务成功完成。**
  > 34. **flush 失败时**：当前数据库事务必须回滚；Session 必须关闭并丢弃；当前 UnitOfWork 变为不可用；同一 UnitOfWork 不得继续追加业务写入。
  > 35. **Engine 与 sessionmaker 可作为 Composition Root 拥有的长生命周期 Infrastructure 资源。**
  > 36. **每个具体 Session 是短生命周期的**，由一个 UnitOfWork 为一个本地 Transactional Application Command 创建。
  > 37. **全局可变 Session 被禁止。**
  > 38. **`scoped_session`、thread-local Session、基于 ContextVar 的 ambient Session 或 ambient UnitOfWork，不得作为主要事务所有权或依赖注入机制。**
  > 39. **每个并发 Command、Worker 执行、Retry、Rerun 或 Resume 使用独立 UnitOfWork 与独立 Session。**
  > 40. **与 RFC-002-DQ-05 一致**：Prepare 与 Commit 作为不同 Transactional Application Commands 时使用不同 UnitOfWork 实例；Execute Outside Transaction 无活动 UnitOfWork；Human Review 等待不持有 UnitOfWork；LangGraph Interrupt 不持有 UnitOfWork；retry backoff 不持有 UnitOfWork；UnitOfWork 绝不序列化进 Checkpoint；UnitOfWork 绝不在 Resume 时恢复。
  > 41. **UnitOfWork 适用于状态修改的 Transactional Application Commands。**
  > 42. **纯读 Application Queries 使用独立的短 Query Scope 或 Read Model Adapter。**
  > 43. **纯 Query Scope 必须**：不暴露 commit()；查询结束后关闭 Session 并释放连接；不返回 ORM entities 或 lazy-loaded relationships；不复用 Command UnitOfWork；不成为跨模块持久化 API。
  > 44. **若读取结果参与后续原子状态变更或并发决策，它必须**：发生在拥有最终 commit 的 UnitOfWork 内；或在 Commit 事务内重新校验（与 RFC-002-DQ-04 和 DQ-05 一致）。
  > 45. **Candidate A 以此修订被接受**（Candidate A is accepted with this revision）。
  > 46. **Candidate B（装饰器或 context-manager 退出自动提交）作为项目 UnitOfWork 模型被拒绝。** Context managers 仍允许用于生命周期清理，但成功的业务提交必须保持显式。
  > 47. **Candidate C（Repository 管理事务）被拒绝**，因其违反 Application 事务所有权与单一提交点。
  > 48. **RFC-002-DQ-06 不决定**：乐观与悲观并发组合；数据库锁选择；序列化或死锁重试策略；幂等键层级；Outbox API 或 dispatch 实现；Event 或 Audit 发布顺序；HTTP 请求作用域；LangGraph 运行时作用域；Checkpoint 实现；完整持久化测试分类。
  > 49. **剩余所有权分配如下**：并发、锁与重试 → RFC-002-DQ-07；幂等 → RFC-002-DQ-08；Outbox 与 Durable Dispatch → RFC-002-DQ-09；Event 与 Audit 语义 → RFC-002-DQ-10；API 与 HTTP 请求协议 → RFC-004；Workflow 与 Checkpoint 运行时 → RFC-003；详细持久化测试策略 → RFC-002-DQ-16。
  > 50. **持久化语义验证必须使用真实 PostgreSQL，至少覆盖**：显式 Use Case commit 成功；未 commit 退出回滚；异常退出回滚；flush 失败回滚并丢弃 Session；Repository 无法独立 commit 或 rollback；嵌套 UnitOfWork 被拒绝；Composite Application Use Case 使用唯一外层 UnitOfWork；UnitOfWork 在 commit 后不可重用；并发 Commands 使用独立 Sessions；Prepare 与 Commit 使用不同 UnitOfWork 实例；Execute Outside Transaction 不持有 Session 或连接；只读 Query Scope 干净关闭；无 UnitOfWork 跨越 Human Review、Interrupt、Retry 或 Resume。详细测试组织与 CI 执行仍由 RFC-002-DQ-16 拥有。

---

## DQ-07：Concurrency Control（并发控制）

- **Question：** 采用何种并发控制组合覆盖 duplicate resume / concurrent approval / stale worker / repeated command / simultaneous invalidation？
- **Why：** Spike R-1 明确「并发/分布式未验证（单线程同步）」；DEC-029「不得静默覆盖较新 Draft」；DEC-033 要求 Resume 幂等。这是 Spike 最大 GAP。
- **Constraints（[DEC 约束]）：** DEC-022 乐观锁或等效；DEC-029 并发编辑不得静默覆盖；DEC-033 五类并发场景。
- **[官方能力]：** SQLAlchemy `version_id_col` 乐观并发（一等能力）；`with_for_update(nowait/skip_locked)` 悲观锁；PG FOR UPDATE/advisory locks；SQLite 全库单写者天然串行化写。**LangGraph OSS 无同一 thread_id 并发 resume 的锁/乐观并发**（防重复 resume 须应用层实现）。
- **Candidates（可组合）：**
  - **乐观并发（version 列 + WHERE version）**：冲突少、读多写少。
  - **悲观锁（SELECT FOR UPDATE / SKIP LOCKED）**：需先占位、task 领取。
  - **DB 唯一约束（幂等键/Command ID）**：防重复写入兜底。
  - **应用层序列化（task-level lock）**：同一 task 串行。
- **Trade-offs：** 乐观适合低冲突、失败重试；悲观保证串行但拉长持锁（与短事务张力）；唯一约束是幂等最后防线；应用锁实现重、需防死锁。
- **Failure modes：** 漏用唯一约束→重复业务版本；悲观锁→死锁；纯乐观在高冲突下重试风暴。
- **Impact on later RFCs：** RFC-003（重复 resume 防护）、RFC-004（并发编辑）。
- **Recommendation（历史提案；Superseded by the Accepted Revision below）：** **[架构推断] 分层组合**——以 **DB 唯一约束兜底幂等** + **乐观 version 列做 Current Truth 更新** + **task 领取用悲观/SKIP LOCKED** + **同 task 应用层序列化**。**置信度：中**（并发场景需真实 DB 验证，见 DQ-16）。**候选关系：** Optimistic revision（乐观并发 version 列 + WHERE version）被接受为普通业务状态修改的默认并发机制（ACCEPTED AS DEFAULT BUSINESS WRITE CONTROL）；Database unique constraints（DB 唯一约束防重复写入兜底）被接受为重复业务事实的最终完整性防线（ACCEPTED AS FINAL INTEGRITY DEFENSE；完整幂等键体系仍留 DQ-08）；SKIP LOCKED（悲观锁/task 领取）以受限方式被接受——仅限显式队列式 Claim 操作的短事务（ACCEPTED WITH RESTRICTION — QUEUE CLAIM ONLY）；应用层序列化（task-level lock / in-process task serialization）被修订为非权威性能优化（REVISED — NON-AUTHORITATIVE OPTIMIZATION ONLY），不得作为业务正确性来源；Durable Lease + Fencing Token 被要求为执行所有权机制（REQUIRED FOR EXECUTION OWNERSHIP）；Session-level Advisory Lock 被禁止（PROHIBITED）；Transaction-level Advisory Lock 非默认、仅在自然行对象无法表达锁范围时经独立架构审查考虑（NOT DEFAULT / SEPARATE REVIEW REQUIRED）；40001/40P01 有限自动重试归 Application Transaction Runner 所有（最多三次总尝试、每次全新 UoW/Session）；语义冲突（stale revision / stale fencing token / expired Lease / unclassified unique violation 等）不得盲目重试；Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Concurrency Technical Spike 为实现前置条件（均 REQUIRED 但本决定不授权）。
- **User Decision：** ACCEPTED WITH REVISION
- **Accepted Direction：** LAYERED CONCURRENCY CONTROL
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**

  > RFC-002-DQ-07 — Concurrency Control
  >
  > 1. **项目采用分层并发控制**（layered concurrency control），而非依赖单一通用锁机制。
  > 2. **Business Current Truth、Aggregate Roots、Current Truth Pointers、Stage State、Review Package state 及其他受保护可变记录的普通状态修改，使用 RFC-002-DQ-04 接受的乐观并发协议**：revision；expected_revision；conditional update（条件更新）；affected-row validation（影响行校验）。
  > 3. **乐观 revision 是普通业务状态修改的默认并发机制。**
  > 4. **expected_revision 不匹配是语义业务冲突**（semantic business conflict），不得作为瞬时数据库失败盲目重试。
  > 5. **以下语义冲突行为是必须的**：并发审批（concurrent approval）必须返回冲突；过期 Human Review 提交必须被拒绝；同时失效（simultaneous invalidation）只允许一个成功提交；后提交者不得静默覆盖较新状态；过期外部执行结果不得重新绑定到较新的 Domain Version。
  > 6. **SQLAlchemy `version_id_col` 可继续作为 Infrastructure 实现机制**，但 Infrastructure 必须将 stale-state 行为翻译为项目自有的并发结果。
  > 7. **revision 保护记录不得通过绕过 expected_revision 与 affected-row 校验的 ORM bulk UPDATE 或 DELETE 操作更新。**
  > 8. **数据库唯一约束是防止重复业务事实的最终完整性防线**（final integrity defense）。
  > 9. **唯一约束最终必须至少覆盖**：重复的不可变 Domain Version identity 或 numbering；重复的正式 Review Decision identity；重复的已提交业务 Command identity；后续接受的决定所要求的重复 Dispatch 或 Attempt identities；其他已命名的业务唯一性不变量。
  > 10. **唯一约束违反不得被统一视为可重试错误。**
  > 11. **Infrastructure 与 Application 错误边界必须识别被违反的命名约束，并至少区分**：已完成的重复操作（already-completed duplicate operation）；幂等重放（idempotent replay）；version-number 分配竞争（version-number allocation race）；重复 Review Decision；真实数据完整性缺陷（genuine data-integrity defect）；未分类唯一约束违反（unclassified unique violation）。
  > 12. **完整幂等键层级、输入指纹（input fingerprinting）、结果重放与去重存储仍由 RFC-002-DQ-08 拥有。**
  > 13. **Duplicate Resume、并发 Worker 执行以及同一并发范围的执行所有权，需要 Durable Execution Guard 或 Durable Lease。**
  > 14. **Durable Lease 模型必须包含以下概念**：`concurrency_scope_id` 或等效的持久化范围标识；当前持有者（current holder）或当前 Attempt identity；Lease 获取时间；Lease 过期时间；单调递增的 generation 或 `fencing_token`；active、released 与 expired 生命周期语义。
  > 15. **确切表名、字段名、索引与物理存储位置留待实现设计与 RFC-002-DQ-13 边界。**
  > 16. **Lease 获取必须发生在一个短的 PostgreSQL 事务内。**
  > 17. **成功的 Lease 获取必须在长时间执行开始前提交。**
  > 18. **Lease 获取提交之后，行锁、Session、UnitOfWork 与数据库连接必须被释放。**
  > 19. **Worker 在以下期间不得持有 PostgreSQL 行锁**：LLM 执行；外部 HTTP 或工具调用；Human Review 等待；Workflow Interrupt；retry backoff；长时间计算；跨进程执行。
  > 20. **每次成功的 Lease 获取、接管（takeover）或重新分配（reassignment）必须颁发一个单调递增的 fencing_token 或 generation。**
  > 21. **持有较旧 fencing_token 的过期 Worker 不得提交 Business Current Truth**——即使它仍在运行并最终返回一个看似有效的结果。
  > 22. **Worker Commit 必须在最终短事务内验证**：expected_revision；当前 Lease Holder；当前 fencing_token；当前 Attempt 或 Run identity；后续由 DQ-08 接受的适用幂等身份；Application Command 要求的全部业务不变量。
  > 23. **若 Lease 已过期、已释放或被另一 Worker 获取，旧 Worker 的结果必须作为 stale 被拒绝。**
  > 24. **进程本地 asyncio.Lock、threading.Lock、mutex 或内存任务锁只能作为非权威优化使用**（non-authoritative optimization），用于减少重复工作。
  > 25. **进程本地锁不得成为业务正确性的来源。**
  > 26. **正确性必须在以下情形下保持完整**：进程重启；Worker 崩溃；多个 Worker 进程；多个部署副本；机器替换；内存状态丢失。
  > 27. **SELECT FOR UPDATE SKIP LOCKED 仅允许用于显式的队列式 Claim 操作**（explicit queue-like Claim operations）。
  > 28. **SKIP LOCKED Claim 操作必须使用短事务**：select candidate → lock candidate → assign durable holder / Lease / fencing token → commit → release the lock and connection → execute outside the transaction。
  > 29. **SKIP LOCKED 不得用于**：普通 Current Truth 读取；Human Review 读取；需要完整一致结果集的查询；绕过 expected_revision 冲突；静默忽略正在被修改的业务对象；跨外部调用持有执行所有权。
  > 30. **SELECT FOR UPDATE、NOWAIT 及其他悲观行锁机制不是全局默认。**
  > 31. **Use Case 只有在记录以下内容时才可采用悲观锁**：受保护的业务不变量；为何乐观 expected_revision 不足；要锁定的确切行；确定性锁顺序；blocking、NOWAIT 或 SKIP LOCKED 行为；最大事务时长；超时与错误翻译；任何自动重试是否安全；真实 PostgreSQL 并发测试证据。
  > 32. **锁定多个业务对象的事务必须使用确定性全局锁顺序**（deterministic global lock order）以降低死锁风险。
  > 33. **Session-level PostgreSQL Advisory Locks 作为项目默认或权威并发控制机制被禁止。**
  > 34. **Transaction-level PostgreSQL Advisory Locks 不是默认机制。**
  > 35. **Transaction-level Advisory Lock 只有在自然数据库行无法表达并发范围时，才可经独立架构审查考虑。**
  > 36. **PostgreSQL SQLSTATE 40001 serialization_failure 与 SQLSTATE 40P01 deadlock_detected 被归类为可能瞬时的数据库事务失败。**
  > 37. **40001 与 40P01 的有限自动重试由 Application Transaction Runner 或 Command Executor 拥有。**
  > 38. **Repository 实现、SQLAlchemy Session 对象与 UnitOfWork 实现不得静默执行自己的事务重试循环。**
  > 39. **每次事务重试必须**：重新开始整个短事务；创建新的一次性 UnitOfWork；创建新的 SQLAlchemy Session；重新加载当前状态；重新评估业务前置条件；重新运行 revision 与 Lease 验证；丢弃失败尝试中的全部 ORM entities。
  > 40. **默认重试预算为**：一次初始事务尝试；最多两次重试尝试；共计三次事务尝试。
  > 41. **无限或无界重试被禁止。**
  > 42. **Retry backoff 与 jitter 必须发生在任何开放数据库事务、UnitOfWork 或 Session 之外。**
  > 43. **具体 backoff 时长、jitter 参数、指标与告警阈值可在 RFC-007 下配置**，但有界重试要求不得被移除。
  > 44. **以下冲突不得盲目或自动重试**：expected_revision 不匹配；stale fencing_token；丢失或过期的 Lease；过期 Human Review 提交；业务不变量拒绝；过期外部结果；未分类的 unique_violation；lock_not_available 或 NOWAIT 失败（除非特定 Use Case 定义了可接受的重试策略）。
  > 45. **已分类的重复操作只有在 DQ-08 幂等语义下才可转换为幂等响应。**
  > 46. **外部 LLM、HTTP Provider 或工具执行不得在数据库事务重试循环内运行。**
  > 47. **当业务前置条件仍然有效时，Commit 事务可使用已产生的、不可变的外部结果进行重试。**
  > 48. **重试 Commit 事务不得自动重新调用外部 Provider。**
  > 49. **五类必备并发场景使用以下控制组合**：duplicate resume = Durable Lease + fencing_token + DQ-08 幂等身份；concurrent approval = expected_revision compare-and-swap + 唯一 Review Decision identity；stale worker = Lease Holder 验证 + fencing_token + expected_revision；repeated command = 命名数据库唯一约束 + DQ-08 幂等记录；simultaneous invalidation = 对所属 Aggregate、Stage State 或 Current Truth Pointer 的 expected_revision compare-and-swap。
  > 50. **LangGraph thread_id 与 Checkpoint identity 用于定位工作流状态与恢复位置。**
  > 51. **LangGraph thread_id 与 Checkpoint identity 不得被视为**：Business Concurrency Lock；Durable Lease；fencing_token；业务 Idempotency Record；只有一个 Resume 处于活动状态的证明。
  > 52. **RFC-002-DQ-07 不决定**：完整幂等键层级与响应重放模型；Outbox 与 Dispatch Claim 实现；Event 与 Audit 持久化顺序；Checkpoint 并发与 Runtime 对账；API 冲突状态码或 ETag / If-Match 协议；完整持久化测试分类与 CI 执行设计。
  > 53. **剩余所有权分配如下**：幂等层级与重放 → RFC-002-DQ-08；Outbox / Durable Dispatch → RFC-002-DQ-09；Event / Audit 语义 → RFC-002-DQ-10；Checkpoint 并发与 Runtime 对账 → RFC-003；API 冲突协议与 ETag / If-Match → RFC-004；完整测试策略 → RFC-002-DQ-16；运维重试指标与阈值 → RFC-007。
  > 54. **Concurrency Scenario Matrix 在持久化或并发控制实现开始之前是必需的**（required before persistence or concurrency-control implementation begins）。
  > 55. **Concurrency Scenario Matrix 必须至少标识**：Scenario；Concurrency Scope；Protected Business Invariant；Optimistic Revision requirement；Database Unique Constraint；Durable Lease requirement；fencing_token requirement；Pessimistic Lock requirement；Retry classification；Retry owner；maximum attempts；user-visible conflict result；related DQ, DEC and RFC。
  > 56. **Concurrency Scenario Matrix 的创建不由 DQ-07 的接受授权**，需要后续的规划或实现就绪（implementation-readiness）授权。
  > 57. **真实 PostgreSQL 多 Worker Concurrency Technical Spike 在并发控制实现被授权之前是必需的。**
  > 58. **该 Technical Spike 必须使用**：真实 PostgreSQL；多个独立数据库连接；至少两个独立执行的 Workers 或进程；确定性故障与时序注入；没有任何部分 Current Truth 写入在冲突后存活的证据。
  > 59. **必备 Technical Spike 必须至少验证**：两个并发 Resume 尝试产生一个权威 Lease；Lease 过期与接管产生更高的 fencing_token；持有 stale fencing_token 的旧 Worker 无法提交；两个使用相同 expected_revision 的审批只允许一个提交；SKIP LOCKED 不会对一个队列项双重领取；40001 与 40P01 重试创建全新 UoW 与 Session 实例；事务重试不重复外部 Provider 调用；并发版本分配不产生重复 Domain Version；冲突回滚产生零部分 Current Truth 写入。
  > 60. **Concurrency Technical Spike 是必需的，但不被本 Accepted Decision 授权。**
  > 61. **Spike Issue、Branch、PR、代码、测试或基础设施的创建需要单独明确的用户授权。**
  > 62. **详细持久化测试组织仍由 DQ-16 拥有。**
  > 63. **所有正式并发语义测试必须使用真实 PostgreSQL**，而非 SQLite 或内存替代品。

---

## DQ-08：Idempotency Model（幂等模型）

- **Question：** 幂等键体系（Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID）与四层幂等语义如何设计、是否统一存储？
- **Why：** DEC-033 要求幂等覆盖 Workflow Resume / Skill Commit / Node Side Effect / Approved Strategy / Brief Commit / retry DB writes / external side-effect tools；Input Fingerprint 作为幂等键概念。at-least-once 使消费端幂等成为必然。
- **Constraints（[DEC 约束]）：** DEC-033 幂等键/Input Fingerprint 定义；Retry≠Rerun（Retry 用相同幂等身份、不创建新业务版本）。
- **[官方能力/权威]：** Idempotent Consumer/Receiver（dedup 表 + 主键判重，**去重须与业务更新同事务**）；Stripe 幂等键（持久化首个响应原样重放、键由客户端生成、唯一约束、参数比对防误用）。
- **[架构推断]：** 幂等分四层——(a) 业务操作幂等（API 幂等键、缓存响应）；(b) 消息消费幂等（判重消息 ID）；(c) workflow 节点重试幂等（不重复产生 Domain Version）；(d) 外部供应商调用幂等（存已调用凭证+结果）。分层框架本身为综合，非单一权威。
- **Candidates：**
  - **A. 统一 Idempotency Table（键 → 状态/结果，唯一约束）**：一处判重。
  - **B. 分层各自存储**：语义清晰但分散。
  - **C. 天然幂等语义设计（设值而非增量）**：减少显式判重。
- **Trade-offs：** A 简单统一但表语义混杂；B 清晰但多表；C 最优雅但非所有操作可设值化。
- **Failure modes：** 去重与业务更新不同事务→判重失效；键设计不含输入指纹→同键不同参数被误判重放。
- **Impact on later RFCs：** RFC-003（resume 幂等）、RFC-004（submit 幂等）。
- **Recommendation：** **[架构推断] 倾向 A 为主 + C 为辅**——统一带唯一约束的幂等表（含 input fingerprint + 首次结果），操作尽量设计为设值语义。**置信度：中-高**（历史提案；Superseded by the Accepted Major Revision below）。候选关系：**Candidate A = REJECTED AS UNIVERSAL CROSS-MODULE TABLE**（作为一张跨模块、跨 Command、Workflow、Consumer、Dispatch 与 Provider 调用的万能 Idempotency Table 被拒绝）；**Candidate B = ACCEPTED AS PRIMARY PERSISTENCE DIRECTION**（各幂等层由对应 Owning Module 分层存储）；**Candidate C = ACCEPTED AS MANDATORY DESIGN PRINCIPLE**（天然幂等 set / ensure / replace 语义为强制设计原则，但不替代显式幂等记录与数据库唯一约束）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Primary Direction：** CANDIDATE B（分层模块私有持久化）
- **Accepted Supporting Principle：** CANDIDATE C（天然幂等设计原则）
- **Rejected Direction：** CANDIDATE A AS UNIVERSAL CROSS-MODULE TABLE
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**
  > **4.1 分层持久化与统一语义**
  > 1. 项目采用分层幂等模型，不采用一张跨模块、跨所有语义的 Universal Idempotency Table。
  > 2. 不同幂等层由相应 Owning Module 持久化。
  > 3. 所有幂等层共享统一的概念与行为契约，包括：
  >    - logical operation identity；
  >    - owning module；
  >    - idempotency scope；
  >    - idempotency key；
  >    - input fingerprint；
  >    - execution status；
  >    - retry / rerun semantics；
  >    - unique constraint；
  >    - result replay semantics；
  >    - atomic transaction boundary。
  > 4. 统一概念契约不意味着统一物理表。
  > 5. 每份幂等记录必须有且仅有一个 Owning Module，并遵守 DQ-02 的表所有权与跨模块访问边界。
  > 6. Candidate B 作为主要持久化方向被接受。
  > 7. Candidate C 作为强制设计原则被接受。
  > 8. Candidate A 作为一张跨模块、跨 Command、Workflow、Consumer、Dispatch 和 Provider 调用的 Universal Idempotency Table 被拒绝。
  > 9. 一个具体 Owning Module 可以为其自身同类 Commands 使用模块私有的 Command Idempotency Table。
  >
  > **4.2 身份模型**
  > 10. 必须明确区分：
  >    - Command ID；
  >    - Idempotency Key；
  >    - Attempt ID；
  >    - Stage Run ID；
  >    - Review Decision ID；
  >    - Dispatch ID；
  >    - Provider Call Identity。
  > 11. 上述身份不得混用，不得由一个通用 ID 字段隐式取代。
  > 12. Command ID 表示一次逻辑状态修改 Command。
  > 13. Command ID 由 Application 层生成。
  > 14. 同一逻辑 Command 的数据库 Retry 或执行 Retry 必须复用同一 Command ID。
  > 15. Intentional Rerun 必须创建新的 Command ID。
  > 16. Rerun 应保留 `rerun_of`、`parent_command_id` 或等价关系。
  > 17. Idempotency Key 表示调用者要求去重与结果重放的逻辑身份。
  > 18. Idempotency Key 必须在明确的 Idempotency Scope 内唯一，不得只按整库裸 Key 推断语义。
  > 19. Idempotency Scope 至少必须等价表达：
  >    - owning module；
  >    - operation type；
  >    - target business scope；
  >    - tenant/account scope，如未来存在；
  >    - idempotency key。
  > 20. Attempt ID 表示一次具体执行尝试。
  > 21. 每次 Retry 创建新的 Attempt ID。
  > 22. Attempt ID 不是业务幂等 Key，不得用于判断逻辑 Command 是否已完成。
  > 23. Stage Run ID 表示一次有意启动的 Stage Run。
  > 24. 同一 Stage Run 内的 Retry 保持相同 Stage Run ID。
  > 25. Intentional Rerun 创建新的 Stage Run ID。
  > 26. Retry 不得创建新的正式 Domain Version。
  > 27. Intentional Rerun 成功后可以产生新的正式 Domain Version。
  > 28. Review Decision ID 是不可变的正式业务决定身份，必须由命名唯一约束保护。
  > 29. 同一 Review Decision 不得正式提交两次。
  > 30. Dispatch ID 的产生、Outbox 持久化和 Delivery 语义继续由 DQ-09 决定。
  >
  > **4.3 Retry 与 Rerun**
  > 31. Retry 的身份语义：
  >    ```text
  >    same Command ID
  >    same Idempotency Key
  >    same Stage Run ID
  >    same Input Fingerprint
  >    new Attempt ID
  >    no new intended business operation
  >    ```
  > 32. Intentional Rerun 的身份语义：
  >    ```text
  >    new Command ID
  >    new logical Idempotency identity
  >    new Stage Run ID
  >    new Attempt ID
  >    explicit relation to previous run
  >    may produce new business version after successful commit
  >    ```
  > 33. Retry 与 Rerun 不得通过是否发生异常来隐式判断，必须由明确的 Application Intent 区分。
  >
  > **4.4 Input Fingerprint**
  > 34. 每个需要幂等保护的操作必须计算 Versioned Input Fingerprint。
  > 35. Input Fingerprint 必须基于规范化后的业务有效输入，不得直接依赖原始 JSON 字节顺序或任意序列化结果。
  > 36. Fingerprint 定义必须明确：
  >    - canonicalization version；
  >    - fingerprint schema version；
  >    - hash algorithm；
  >    - included business fields；
  >    - excluded transport and observability fields。
  > 37. Fingerprint 应包含决定业务效果的字段，例如：
  >    - target business identity；
  >    - expected revision；
  >    - base Domain Version；
  >    - Command parameters；
  >    - Source/Evidence Version references；
  >    - selected operation mode。
  > 38. Fingerprint 不应包含：
  >    - trace ID；
  >    - arrival timestamp；
  >    - retry counter；
  >    - Attempt ID；
  >    - connection metadata；
  >    - 不影响业务效果的观测字段。
  > 39. 同一 Scope + Key + 相同 Fingerprint 表示同一个逻辑操作。
  > 40. 同一 Scope + Key + 不同 Fingerprint 必须返回 Idempotency Key Conflict。
  > 41. Idempotency Key Conflict 时不得：
  >    - 覆盖原记录；
  >    - 执行新业务操作；
  >    - 把旧结果重放为新请求结果；
  >    - 盲目自动重试。
  >
  > **4.5 状态机与执行所有权**
  > 42. 幂等执行至少需要表达：
  >    - IN_PROGRESS；
  >    - SUCCEEDED；
  >    - FAILED_TERMINAL；
  >    - ABANDONED、EXPIRED 或 RETRYABLE 等非终局状态。
  > 43. 精确 Enum 名称留待实现设计。
  > 44. IN_PROGRESS 表示逻辑操作已被一个有效 Attempt 领取。
  > 45. 重复请求看到有效 IN_PROGRESS 时不得再次执行相同业务副作用。
  > 46. IN_PROGRESS 执行所有权必须与 DQ-07 的：
  >    - Durable Lease；
  >    - Lease Holder；
  >    - Attempt ID；
  >    - fencing_token；
  >
  >    协同。
  > 47. 只有当前有效 Lease Holder 和 fencing_token 可以把幂等记录转换为最终成功状态。
  > 48. Lease 过期、被接管或 fencing_token 失效后，旧 Worker 不得写入 SUCCEEDED。
  > 49. Checkpoint 和 LangGraph thread_id 不作为 Business Idempotency Record。
  >
  > **4.6 原子提交与结果重放**
  > 50. 业务成功时，以下内容必须在同一个 DEC-035 Atomic Business Commit 中提交：
  >    - Business Current Truth 更新；
  >    - Domain Version；
  >    - Formal Evidence Links；
  >    - Current Truth Pointer；
  >    - Stage State；
  >    - Audit Record；
  >    - Idempotency Record 的成功状态；
  >    - 不可变 Application Result Snapshot 或结果引用。
  > 51. 如果业务事务回滚，不得留下 SUCCEEDED Idempotency Record。
  > 52. 如果业务 Commit 成功但响应丢失，相同 Scope + Key + Fingerprint 的后续请求必须重放原 Application Result。
  > 53. 结果重放不得再次执行业务副作用。
  > 54. 重放结果必须是项目自有的稳定 Application Result Snapshot 或不可变结果引用。
  > 55. 幂等记录不得直接保存或返回：
  >    - ORM Entity；
  >    - SQLAlchemy Session；
  >    - Python Exception 对象；
  >    - 原始数据库错误；
  >    - 未脱敏 Secret；
  >    - 与传输层强绑定的可变对象。
  > 56. HTTP Status、Headers、Response Body 和 Header 名称继续由 RFC-004 决定。
  >
  > **4.7 失败分类**
  > 57. 确定性的终局业务结果可以记录并稳定重放。
  > 58. 可记录的终局结果包括已正式确定且再次执行不会改变的业务拒绝或冲突。
  > 59. 瞬时基础设施失败不得永久固化为终局结果，包括：
  >    - 连接超时；
  >    - SQLSTATE 40001；
  >    - SQLSTATE 40P01；
  >    - 临时 Provider 不可用；
  >    - Worker Crash；
  >    - Lease 过期；
  >    - 可恢复的网络故障。
  > 60. 瞬时失败可以使用相同逻辑幂等身份重试，但必须创建新的 Attempt ID。
  > 61. 重试继续受 DQ-07 的有限重试、Lease 和 Fencing Token 规则约束。
  > 62. 在领取操作和副作用开始前发生的纯输入验证失败，可以不创建可重放终局记录。
  >
  > **4.8 分层幂等**
  > 63. Business Command Idempotency Record：
  >    - 由执行该业务状态修改的模块拥有；
  >    - 与业务状态更新同一 PostgreSQL 事务提交；
  >    - 不得成为跨模块共享读写表。
  > 64. Message Consumer Deduplication Record：
  >    - 由消费模块拥有；
  >    - 使用 Message ID/Dispatch ID + Consumer Scope 的组合唯一；
  >    - Dedup Marker 必须与消费产生的业务更新同事务提交；
  >    - 不得先提交 Dedup Marker 再执行实际业务写入。
  > 65. Workflow Retry Idempotency：
  >    - Runtime 负责 Attempt 和运行位置；
  >    - Business Module 负责防止重复 Business Commit；
  >    - Resume 必须经过 Command Identity、数据库幂等记录、Lease 与 Fencing 校验；
  >    - Checkpoint 不替代业务幂等记录。
  > 66. External Provider Idempotency：
  >    - Provider Adapter 使用稳定 Provider Call Identity；
  >    - 同一逻辑调用的 Retry 复用相同 Provider Idempotency Key；
  >    - Intentional Rerun 使用新的 Provider Call Identity；
  >    - Provider Key 必须绑定 Input Fingerprint；
  >    - 数据库事务 Retry 不得生成新的 Provider Key。
  > 67. Provider 原生支持 Idempotency Key 时，应稳定映射系统逻辑调用身份。
  > 68. Provider 不支持原生 Idempotency 时，Provider/Integration 模块必须维护 Durable Call Ledger。
  > 69. Durable Call Ledger 至少记录：
  >    - Provider Call Identity；
  >    - Input Fingerprint；
  >    - execution status；
  >    - Attempt relationship；
  >    - result reference；
  >    - reconciliation state。
  > 70. 已完成 Provider 调用不得因数据库事务重试被自动再次调用。
  > 71. 具体 Provider 对账和补偿策略留给相应 Provider RFC 或 Adapter 设计。
  >
  > **4.9 天然幂等语义**
  > 72. 状态修改应尽量采用：
  >    - set；
  >    - ensure；
  >    - replace-to-desired-state；
  >    - compare-and-set。
  > 73. 应避免无保护的：
  >    - increment；
  >    - append；
  >    - toggle；
  >    - duplicate create。
  > 74. 天然幂等语义不得替代显式记录、唯一约束或执行所有权控制，尤其涉及：
  >    - 创建 Domain Version；
  >    - 外部副作用；
  >    - Review Decision；
  >    - Dispatch；
  >    - 计费或配额；
  >    - append-only Audit；
  >    - 只能发生一次的正式业务事实。
  >
  > **4.10 物理模型与后续边界**
  > 75. 具体表名、字段名、索引、分区与 Storage Placement 留待实现设计和 DQ-13。
  > 76. Retention、TTL、删除和 Key 再利用策略由 DQ-15 决定。
  > 77. DQ-15 决定前不得：
  >    - 假设 Key 可被短期删除；
  >    - 自动复用归档 Key；
  >    - 依赖内存 Cache 作为权威幂等存储。
  > 78. Fingerprint 和结果存储不得无必要复制敏感原始载荷。
  > 79. Hashing、Encryption、Redaction、Secret 和 PII 规则继续由 DQ-17 决定。
  > 80. DQ-08 不提前决定：
  >    - Outbox/Dispatch 表和 Relay → DQ-09；
  >    - Event/Audit 分类和持久化顺序 → DQ-10；
  >    - Workflow Runtime/Checkpoint 协调 → RFC-003；
  >    - HTTP 幂等 Header、状态码和响应协议 → RFC-004；
  >    - Retention 数值 → DQ-15；
  >    - 完整测试分类和 CI → DQ-16；
  >    - Security/Encryption/PII → DQ-17。
  >
  > **4.11 Idempotency Identity Matrix**
  > 81. 开始幂等实现前必须完成 Idempotency Identity Matrix。
  > 82. Matrix 至少包含：
  >    - Operation；
  >    - Owning Module；
  >    - Logical Command ID；
  >    - Idempotency Scope；
  >    - Idempotency Key Source；
  >    - Retry Identity；
  >    - Rerun Identity；
  >    - Attempt ID；
  >    - Stage Run ID；
  >    - Input Fingerprint Fields；
  >    - Fingerprint Schema Version；
  >    - State Machine；
  >    - Unique Constraint；
  >    - Atomic Transaction Boundary；
  >    - Result Replay；
  >    - Provider Idempotency；
  >    - Retention Owner；
  >    - Related DQ/DEC/RFC。
  > 83. DQ-08 接受不授权创建该 Matrix。
  > 84. Idempotency Identity Matrix Creation = NOT AUTHORIZED。
  > 85. 本决定不要求新增独立 Technical Spike。
  > 86. DQ-07 已要求的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效，并应覆盖幂等并发场景。
  >
  > **4.12 测试前置语义**
  > 87. 所有正式幂等语义验证必须使用真实 PostgreSQL。
  > 88. 后续测试至少覆盖：
  >    - 同 Key + 同 Fingerprint 并发请求只有一次业务效果；
  >    - 同 Key + 不同 Fingerprint 返回冲突；
  >    - Commit 成功但响应丢失后重放原结果；
  >    - Retry 不创建新 Domain Version；
  >    - Intentional Rerun 创建新逻辑身份；
  >    - Review Decision 只提交一次；
  >    - Consumer Dedup 与业务更新同事务；
  >    - Worker Crash 后 IN_PROGRESS 接管；
  >    - stale fencing_token 无法完成记录；
  >    - Provider 成功但数据库 Commit 失败后不重复调用；
  >    - 瞬时失败创建新 Attempt；
  >    - 终局结果稳定重放。
  > 89. 详细测试组织和 CI 策略继续由 DQ-16 决定。

---

## DQ-09：Transactional Outbox / Durable Dispatch（事务性发件箱 / 可靠调度）

- **Question：** 是否首版引入 Transactional Outbox？Durable Work Intent 的落库形态？API 如何可靠触发 Worker？
- **Why：** RFC-001-DQ-07 已立 Durable Dispatch Boundary（API 返回 accepted 前 Intent 必须可靠记录），候选明确移交 RFC-002/003；这是「业务写入 + dispatch 意图」的双写问题。
- **Constraints（[DEC 约束]）：** Durable Dispatch Boundary（RFC-001-DQ-07）；Atomic Resume Coordination（Approved Commit + Resume Intent 原子或可靠协调）；禁止 `asyncio.create_task`/临时 Background Task。**不得在本 RFC 实施 Queue。**
- **[官方能力/权威]：** Transactional Outbox（业务实体 + outbox 记录同库事务写入，独立 relay 投递；at-least-once→消费端必幂等）；relay=Polling（可移植）vs Log Tailing（低延迟、库特定、Debezium）；Guaranteed Delivery（store-and-forward = Durable Dispatch 概念根源）。
- **Candidates：**
  - **A. Transactional Outbox 表 + 应用内 relay**：双写原子，relay 轮询/尾部。
  - **B. Database-backed Job Table（简化 Outbox）**：Intent 即任务行，Worker 领取。
  - **C. 独立 Message Broker**：引入额外基础设施（超出 MVP 倾向）。
- **Trade-offs：** A 语义最完整但需 relay 组件；B 最简单、与「DB 任务表」天然契合 MVP；C 强大但超范围。**relay/backend 实现属 RFC-003。**
- **Failure modes：** 开发者提交业务后忘写 outbox（权威缺点）；relay 重复投递（故消费端幂等）；B 高吞吐下轮询负载。
- **Impact on later RFCs：** RFC-003（dispatch backend 具体实现）、RFC-007（relay 观测）。
- **Recommendation（历史提案；Superseded by the Accepted Major Revision below）：** **[架构推断] 倾向 B（DB Job Table 形态的 Durable Work Intent，逻辑等价最简 Outbox）首版引入**，与业务写入同事务；relay/具体 backend 移交 RFC-003。**置信度：中**。候选关系：**Candidate B = ACCEPTED WITH MAJOR REVISION**（Formal Pattern: PostgreSQL-backed Transactional Durable Work Intent，作为 MVP 内部可靠工作调度模型）；**Candidate A = NOT SELECTED AS MVP INTERNAL WORK MODEL**（不作为 MVP 内部任务调度的主要模型；RETAINED FOR FUTURE INTEGRATION EVENT OUTBOX——当 DQ-10 或后续 RFC 确认需要可靠发布 Integration Event 时，可引入语义独立的 Transactional Event Outbox）；**Candidate C = NOT SELECTED FOR MVP**（独立 Message Broker 不在 MVP 中作为权威 Durable Dispatch 来源；MAY SERVE AS A FUTURE DELIVERY BACKEND；MUST NOT REPLACE TRANSACTIONAL DURABLE INTENT）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE B
- **Formal Pattern：** POSTGRESQL-BACKED TRANSACTIONAL DURABLE WORK INTENT
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**
  > **3.1 模式选择与语义边界**
  > 1. MVP 采用 PostgreSQL-backed Transactional Durable Work Intent。
  > 2. Candidate B 作为 MVP 内部 Durable Dispatch 的主要方向被接受。
  > 3. Durable Work Intent 表示：
  >    ```text
  >    The system must perform this work.
  >    ```
  > 4. Durable Work Intent 不表示：
  >    ```text
  >    This business fact has already happened.
  >    ```
  > 5. Durable Work Intent 不得与以下概念混用：
  >    - Domain Event；
  >    - Application Event；
  >    - Integration Event；
  >    - Audit Record；
  >    - State Transition Record；
  >    - Workflow Checkpoint；
  >    - Business Current Truth；
  >    - 通用 Message Envelope。
  > 6. Candidate A 不作为 MVP 内部任务调度的主要模型。
  > 7. 当 DQ-10 或后续 RFC 确认需要可靠发布 Integration Event 时，可以引入语义独立的 Transactional Event Outbox。
  > 8. Durable Work Intent 与 Integration Event Outbox 不得默认共用：
  >    - 业务身份；
  >    - 状态机；
  >    - Payload；
  >    - Retention；
  >    - Consumer Protocol；
  >    - Completion Semantics；
  >    - Retry Policy。
  > 9. Candidate C 独立 Message Broker 不在 MVP 中作为权威 Durable Dispatch 来源。
  > 10. 后续 Message Broker 只能作为：
  >    - Delivery Backend；
  >    - Relay Target；
  >    - Worker Transport；
  >    - 扩展性基础设施。
  > 11. Broker 不得替代在业务事务内写入的 Durable Work Intent。
  >
  > **3.2 所有权与模块边界**
  > 12. Durable Dispatch 必须具有明确且唯一的 Owning Module 或 Dispatch Capability。
  > 13. Dispatch Capability 拥有：
  >    - Work Intent Repository Port；
  >    - Infrastructure Repository；
  >    - ORM Model；
  >    - Migration；
  >    - Claim Application Contract；
  >    - Completion Application Contract；
  >    - Retry/Cancel/Supersede Application Contract。
  > 14. 业务模块不得直接访问 Dispatch ORM、表、Session 或 Repository。
  > 15. 跨模块创建 Work Intent 必须通过明确的 Public Application Contract、Composite Application Use Case 或同一顶层事务编排。
  > 16. 不得通过共享 ORM、直接 SQL 或 Repository Registry 绕过 DQ-02 的模块边界。
  >
  > **3.3 原子创建与 API accepted 边界**
  > 17. 当业务状态迁移需要可靠触发后续工作时，最外层 Transactional 或 Composite Application Use Case 必须在同一 PostgreSQL 事务中：
  >    - 写入业务状态；
  >    - 写入 DEC-035 Atomic Business Commit 的必要参与者；
  >    - 创建 Durable Work Intent；
  >    - Commit。
  > 18. Durable Work Intent 的创建与触发它的业务状态变化必须处于同一 Atomic Business Commit。
  > 19. Work Intent 写入失败时，整个业务事务必须回滚。
  > 20. 业务事务回滚时，不得留下可领取的 Work Intent。
  > 21. 不得先提交业务状态，再尝试以非原子方式补写 Work Intent。
  > 22. API 只有在 Durable Work Intent 成功持久化并 Commit 后才能返回：
  >    ```text
  >    accepted
  >    ```
  > 23. `accepted` 只表示：
  >    ```text
  >    Durable Work Intent has been reliably recorded.
  >    ```
  > 24. `accepted` 不表示：
  >    - Worker 已领取；
  >    - Worker 已启动；
  >    - 外部 Provider 已调用；
  >    - Workflow 已完成；
  >    - Business Result 已成功；
  >    - Current Truth 已更新为最终结果。
  > 25. HTTP Status、Header、Response Body 与 Polling API 协议继续由 RFC-004 决定。
  >
  > **3.4 被禁止的非持久化 Dispatch**
  > 26. 以下机制不得作为唯一可靠调度保证：
  >    - `asyncio.create_task`；
  >    - 临时 Background Task；
  >    - 进程内 Queue；
  >    - 内存 Flag；
  >    - 非持久化 Callback；
  >    - Fire-and-forget coroutine；
  >    - 仅依赖 LISTEN/NOTIFY；
  >    - 仅依赖 Broker Publish；
  >    - 仅依赖 LangGraph Runtime 内存状态。
  > 27. 上述机制可以在后续设计中作为性能或唤醒优化，但业务正确性必须依赖 Durable Work Intent。
  >
  > **3.5 Dispatch Identity**
  > 28. 每个逻辑 Durable Work Intent 使用稳定且唯一的 `dispatch_id`。
  > 29. 同一个逻辑 Intent 的 Work Execution Retry 必须保持相同 `dispatch_id`。
  > 30. 每次具体领取或执行尝试必须创建新的：
  >    - `delivery_attempt_id`；
  >    - 或与 DQ-08 明确一致的 Attempt Identity。
  > 31. Attempt Identity 不得替代 `dispatch_id`。
  > 32. Intentional Rerun 必须创建新的 `dispatch_id`。
  > 33. Intentional Rerun 必须保留：
  >    - `rerun_of`；
  >    - `parent_dispatch_id`；
  >    - 或等价关系。
  > 34. Retry 与 Rerun 必须由明确 Application Intent 区分，不得只依据异常是否发生来推断。
  >
  > **3.6 Durable Intent Envelope**
  > 35. Durable Work Intent 的稳定 Envelope 至少必须表达：
  >    - `dispatch_id`；
  >    - `intent_type`；
  >    - owning business operation；
  >    - target business scope；
  >    - `command_id`；
  >    - `stage_run_id`，如适用；
  >    - Input Fingerprint；
  >    - base `domain_version_id`，如适用；
  >    - `expected_revision`，如适用；
  >    - immutable payload 或 payload reference；
  >    - ordering key，如适用；
  >    - `created_at`；
  >    - `available_at`；
  >    - priority，如适用。
  > 36. Work Intent Payload 不得包含：
  >    - ORM Entity；
  >    - SQLAlchemy Session；
  >    - UnitOfWork；
  >    - Repository；
  >    - 数据库 Connection；
  >    - lazy-loaded ORM relation；
  >    - Python Coroutine；
  >    - 未脱敏 Secret；
  >    - 无法稳定序列化的进程内对象。
  > 37. Work Intent 不得只保存：
  >    ```text
  >    Go to the database and process the latest state.
  >    ```
  > 38. Intent 必须保存足够的不可变身份、版本与 Fingerprint，使 Worker 能判断：
  >    - 原计划处理什么；
  >    - 基于哪个业务版本；
  >    - 当前状态是否已变化；
  >    - 结果是否 stale；
  >    - 当前执行属于 Retry 还是 Rerun；
  >    - 当前 Worker 是否仍拥有执行权。
  > 39. Payload Snapshot 与 Payload Reference 的具体选择留待实现设计与 DQ-12、DQ-17 边界。
  >
  > **3.7 生命周期**
  > 40. Durable Work Intent 至少需要表达以下生命周期语义：
  >    - PENDING / AVAILABLE；
  >    - LEASED / IN_PROGRESS；
  >    - SUCCEEDED；
  >    - FAILED_RETRYABLE；
  >    - FAILED_TERMINAL；
  >    - CANCELLED；
  >    - SUPERSEDED。
  > 41. 精确 Enum 名称留待实现设计。
  > 42. 状态转换必须是显式、可审计且受并发保护的。
  > 43. 不得通过删除记录来表达普通成功、失败、取消或取代。
  > 44. Invalidation、Cancellation 与 Supersession 不等于物理删除。
  >
  > **3.8 Claim、Lease 与 Fencing**
  > 45. Work Intent Claim 必须使用短 PostgreSQL 事务。
  > 46. 队列式 Claim 可以采用：
  >    ```text
  >    select eligible intent
  >    → SELECT FOR UPDATE SKIP LOCKED
  >    → assign Lease Holder
  >    → issue monotonically increasing fencing_token
  >    → create Attempt Identity
  >    → update lifecycle state
  >    → commit
  >    → release lock/session/connection
  >    ```
  > 47. SKIP LOCKED 只允许用于队列式 Claim，不得用于普通 Current Truth 查询。
  > 48. Claim Commit 后必须释放：
  >    - PostgreSQL 行锁；
  >    - SQLAlchemy Session；
  >    - UnitOfWork；
  >    - 数据库连接。
  > 49. Worker 的长时间执行必须发生在数据库事务之外。
  > 50. Worker 不得在 LLM、HTTP、工具执行、Human Review、Interrupt、Backoff 或跨进程等待期间持有行锁或 Session。
  > 51. Worker 最终提交时必须在新的短事务中重新验证：
  >    - `dispatch_id`；
  >    - current Lease Holder；
  >    - `fencing_token`；
  >    - Attempt Identity；
  >    - `command_id`；
  >    - Input Fingerprint；
  >    - `expected_revision`；
  >    - applicable Idempotency Identity；
  >    - 所有相关业务不变量。
  > 52. 只有当前有效 Lease Holder 与 fencing_token 才能：
  >    - 完成 Intent；
  >    - 标记 Intent 为 SUCCEEDED；
  >    - 提交该执行产生的 Business Current Truth；
  >    - 写入最终结果引用。
  > 53. Lease 过期、被释放或被接管后，旧 Worker 不得：
  >    - 完成 Intent；
  >    - 写入 SUCCEEDED；
  >    - 提交 Current Truth；
  >    - 覆盖新 Worker 的结果；
  >    - 重新绑定到更新后的 Domain Version。
  >
  > **3.9 Completion Atomicity**
  > 54. 当 Work Intent Completion 与该次执行产生的业务结果需要立即一致时，以下内容必须在同一最终短事务中完成：
  >    - 新业务状态；
  >    - Domain Version；
  >    - Evidence Links；
  >    - Current Truth Pointer；
  >    - Stage State；
  >    - Audit Record；
  >    - Idempotency Result；
  >    - Work Intent Completion；
  >    - Result Reference。
  > 55. 如果最终业务 Commit 失败，不得留下已经成功完成的 Work Intent 状态。
  > 56. 如果 Work Intent 已成功标记完成，不能再由普通 Worker 重复完成。
  > 57. 具体完成事务参与者以 DEC-035、DQ-08 与业务不变量为准。
  >
  > **3.10 Provider 副作用**
  > 58. 如果外部 Provider 已成功，但最终数据库 Commit 失败：
  >    - Retry 保持相同 Provider Call Identity；
  >    - 不得因数据库事务 Retry 自动重新调用 Provider；
  >    - 必须通过 Provider 原生 Idempotency、Durable Call Ledger、结果查询或对账恢复。
  > 59. Provider 副作用与 Work Intent 状态不得被错误解释为分布式 Exactly-once Transaction。
  > 60. Provider 对账与补偿策略继续由对应 Provider RFC、Adapter 设计或 RFC-003 运行时恢复机制决定。
  >
  > **3.11 Delivery Semantics**
  > 61. Durable Dispatch 的交付语义为：
  >    ```text
  >    AT-LEAST-ONCE
  >    ```
  > 62. 架构不承诺：
  >    ```text
  >    EXACTLY-ONCE DELIVERY
  >    ```
  > 63. 唯一业务效果由以下机制组合保证：
  >    - DQ-08 Idempotency；
  >    - Consumer Dedup；
  >    - Named Unique Constraints；
  >    - DQ-07 Lease；
  >    - Fencing Token；
  >    - `revision` / `expected_revision`；
  >    - Atomic Business Commit。
  > 64. Worker、Relay 或进程 Crash 可能导致同一个 Intent 再次被领取或投递。
  > 65. 所有 Worker 和消费者必须能够安全处理重复 Delivery。
  >
  > **3.12 数据库事务 Retry 与 Work Retry**
  > 66. Database Transaction Retry 与 Work Execution Retry 是不同层级。
  > 67. Database Transaction Retry：
  >    - 只处理 40001 / 40P01 等事务级瞬时失败；
  >    - 使用新的 UoW 与 Session；
  >    - 默认最多三次总事务尝试；
  >    - 不重新调用外部 Provider；
  >    - 不创建新的逻辑 Dispatch。
  > 68. Work Execution Retry：
  >    - 保持相同 `dispatch_id`；
  >    - 创建新的 Attempt Identity；
  >    - 重新取得 Lease；
  >    - 获得新的 fencing_token；
  >    - 重新验证业务前置条件。
  > 69. DQ-07 的「三次事务尝试」不得直接用作 Work Execution 最大次数。
  > 70. Work Execution Retry 的以下策略由 RFC-003 与 RFC-007 决定：
  >    - 最大执行次数；
  >    - Backoff；
  >    - Jitter；
  >    - Dead-letter；
  >    - Terminal Failure；
  >    - 人工恢复；
  >    - 运维告警；
  >    - SLO 与监控指标。
  > 71. FAILED_RETRYABLE 只有在 `available_at` 满足条件后才可重新领取。
  > 72. FAILED_TERMINAL 不得由普通 Worker 自动重新领取。
  > 73. CANCELLED 或 SUPERSEDED Intent 不得启动新的执行。
  > 74. 已经执行中的 Intent 被取消或取代时，最终 Commit 仍必须通过 Lease、Fencing、Revision 与业务状态检查阻止旧结果落地。
  >
  > **3.13 Ordering**
  > 75. 默认不承诺全局严格顺序。
  > 76. 只有存在明确业务不变量时，才允许按：
  >    - Aggregate；
  >    - Task；
  >    - Stage；
  >    - ordering key；
  >    - 其他具名业务 Scope；
  >
  >    提供局部顺序。
  > 77. 需要顺序的 Intent 必须定义：
  >    - ordering scope；
  >    - sequence；
  >    - 前序失败行为；
  >    - 是否阻塞后续 Intent；
  >    - 超时规则；
  >    - 跳过或人工干预规则。
  > 78. 不得使用单一全局队列锁实现全系统顺序。
  > 79. 具体 Ordering 实现与调度算法留给 RFC-003。
  >
  > **3.14 Polling 与 Wake-up**
  > 80. 周期性 PostgreSQL Polling 是恢复所有可执行 Intent 的权威发现路径。
  > 81. PostgreSQL LISTEN/NOTIFY 或进程内 Signal 可以作为低延迟 Worker Wake-up 优化。
  > 82. Wake-up Signal 丢失时，Polling 必须仍能发现所有已提交且可执行的 Intent。
  > 83. LISTEN/NOTIFY、Signal 或 Broker Notification 不得作为：
  >    - Durable Dispatch Record；
  >    - Delivery Acknowledgement；
  >    - 唯一恢复依据；
  >    - Exactly-once Guarantee。
  > 84. Worker 唤醒与 Claim 必须保持分离：
  >    ```text
  >    Wake-up says:
  >    There may be work.
  >
  >    Database Claim decides:
  >    Which Worker owns which work.
  >    ```
  >
  > **3.15 RFC 与 DQ 边界**
  > 85. Relay 与 Worker Backend 的具体实现留给 RFC-003，包括：
  >    - direct PostgreSQL polling；
  >    - LISTEN/NOTIFY acceleration；
  >    - broker relay；
  >    - worker lifecycle；
  >    - deployment topology；
  >    - runtime reconciliation；
  >    - crash recovery。
  > 86. DQ-09 不决定 DQ-10 的：
  >    - Domain Event；
  >    - Application Event；
  >    - Integration Event；
  >    - Audit Record；
  >    - State Transition Record。
  > 87. 如果 DQ-10 确认需要 Integration Event 持久化，应使用语义独立的 Event Outbox，不得把 Durable Work Intent 当作事件历史。
  > 88. Work Intent Retention、Archive、Payload Cleanup 与物理删除由 DQ-15 决定。
  > 89. 在 DQ-15 决定前，不得依赖快速物理删除作为队列表性能或正确性前提。
  > 90. Dispatch Payload 的 Encryption、Redaction、Secret 与 PII 规则由 DQ-17 决定。
  > 91. 完整 Durable Dispatch 测试分类与 CI 执行策略由 DQ-16 决定。
  >
  > **3.16 Matrix 与 Spike**
  > 92. DQ-09 不新增独立 Matrix。
  > 93. 现有 Idempotency Identity Matrix 必须在后续获得授权时补充：
  >    - Dispatch ID；
  >    - Delivery Attempt Identity；
  >    - Consumer Scope；
  >    - Provider Call Identity；
  >    - Retry Identity；
  >    - Rerun Identity。
  > 94. 现有 Concurrency Scenario Matrix 必须在后续获得授权时补充：
  >    - Claim Race；
  >    - Lease Expiry；
  >    - Worker Crash；
  >    - stale fencing_token；
  >    - duplicate Delivery；
  >    - Cancel-versus-complete；
  >    - simultaneous retry；
  >    - ordering conflict。
  > 95. DQ-09 接受不授权创建或修改上述 Matrix。
  > 96. DQ-07 已要求的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效。
  > 97. 该 Spike 在后续获得独立授权后必须覆盖：
  >    - concurrent Claim；
  >    - SKIP LOCKED；
  >    - Lease Takeover；
  >    - stale Worker Completion；
  >    - duplicate Delivery；
  >    - Worker Crash Recovery；
  >    - Polling Recovery；
  >    - Cancel-versus-complete；
  >    - zero partial business writes。
  > 98. DQ-09 不要求在决策前新增独立 Technical Spike。
  > 99. Spike Issue、Branch、PR、代码、测试和基础设施仍需单独明确授权。
  >
  > **3.17 测试前置语义**
  > 100. 所有正式 Durable Dispatch 语义验证必须使用真实 PostgreSQL。
  > 101. 后续测试至少覆盖：
  >    - 业务写入与 Work Intent 同事务提交；
  >    - Intent 插入失败时业务整体回滚；
  >    - 业务事务回滚后无可领取 Intent；
  >    - Commit 成功但 Worker 未唤醒时 Polling 恢复；
  >    - 两个 Worker 不会同时取得同一权威 Lease；
  >    - Worker Crash 后 Intent 可被接管；
  >    - stale Worker 无法完成；
  >    - 同一 Intent 可重复 Delivery，但只有一次业务效果；
  >    - Provider 成功、数据库 Commit 失败后不重复 Provider 副作用；
  >    - CANCELLED / SUPERSEDED Intent 不产生 Current Truth；
  >    - Retry 使用相同 dispatch_id 和新 Attempt；
  >    - Rerun 创建新的 dispatch_id；
  >    - 数据库事务 Retry 不重复执行长任务；
  >    - Work Retry 不受三次事务尝试直接限制；
  >    - 无部分业务写入。
  > 102. 详细测试组织与 CI 策略继续由 DQ-16 决定。

---

## DQ-10：Event & Audit Persistence（事件与审计持久化）

- **Question：** Domain Event / Integration Event / Audit Record / State Transition Record / Observability Event 是否分离、哪些需持久化、落库形态？
- **Why：** DEC-013 要求可审计；DEC-033 列概念事件清单；须区分「为问责的审计」与「为通知的事件」，避免混淆。
- **Constraints（[DEC 约束]）：** RFC-001-DQ-08 区分 Domain Event（模块内部、过去式）vs Application Event（提交后发布）；Audit Record 纳入 Atomic Business Commit 同事务写；不吸收 RFC-007 观测范围。
- **[官方能力/权威]：** Fowler Audit Log（append-only、问责、简单，「a database table also makes a fine audit log」；建议区分 actual/record dates）；Audit Log ≠ Domain Event（前者问责取证、后者通知触发）；Fowler 四类事件（Notification/State Transfer/ES/CQRS）不可混淆。
- **Candidates：**
  - **A. append-only Audit 表（与业务同事务）+ Application Event 提交后通知**：审计走原子写、事件走通知。
  - **B. 统一事件表承载审计+事件**：简化但混淆语义。
  - **C. 仅审计、不持久化事件**：最简。
- **Trade-offs：** A 语义清晰、符合 Fowler 分界；B 表简但读者需区分；C 牺牲事件驱动能力。
- **Failure modes：** 审计与事件混表→问责取证困难；事件携带过多状态（State Transfer）→数据冗余拷贝。
- **Impact on later RFCs：** RFC-007（观测事件流）。
- **Recommendation（历史提案；Superseded by the Accepted Major Revision below）：** **[架构推断] 倾向 A**——审计 append-only 同事务原子写、Application Event 提交后通知（不持久化为 Current Truth）。**置信度：高**。候选关系：**Candidate A = ACCEPTED WITH MAJOR REVISION**（六类 Event/Record 独立语义 + append-only Audit Record 与业务状态同事务 + 重大修订补充 Integration Event Outbox / Observability / Classification Table 边界）；**Candidate B = REJECTED AS UNIVERSAL EVENT / AUDIT TABLE**（以一张统一事件表同时承载审计与事件被拒绝）；**Candidate C = REJECTED AS PROJECT-WIDE ARCHITECTURE**（仅审计、不持久化事件作为全项目架构被拒绝；Specific Flow With No Integration Event = ALLOWED WHEN NO RELIABLE CROSS-BOUNDARY FACT NOTIFICATION IS REQUIRED, AUDIT RECORD REMAINS REQUIRED WHEN DEC / BUSINESS RULE REQUIRES AUDIT）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**
  > **3.1 事件与记录分类**
  > 1. Domain Event、Audit Record、State Transition Record、Application Event、Integration Event 与 Observability Event 是不同语义类别。
  > 2. 不使用一张同时承载审计、业务事件、可靠通知、工作调度、Checkpoint 和 Telemetry 的 Universal Event Table。
  > 3. 以下类别不得因都具有时间戳或 Payload 而合并为同一种记录：
  >    - Domain Event；
  >    - Audit Record；
  >    - State Transition Record；
  >    - Application Event；
  >    - Integration Event；
  >    - Observability Event；
  >    - Durable Work Intent；
  >    - Workflow Checkpoint；
  >    - Business Current Truth。
  > 4. 逻辑语义、事务边界、可靠性等级、所有模块、状态机、Retention 和消费者协议必须分别定义。
  > 5. Candidate A 接受并进行重大修订。
  > 6. Candidate B 作为 Universal Event / Audit Table 被拒绝。
  > 7. Candidate C 作为全项目架构被拒绝。
  > 8. 某个具体业务流程在没有跨边界通知需求时，可以不创建 Integration Event，但不得因此移除 Audit Record。
  >
  > **3.2 Domain Event**
  > 9. Domain Event 表达所属业务模块内部已经发生的业务事实。
  > 10. Domain Event 名称必须采用过去式，例如：
  >    - `StrategyApproved`；
  >    - `BriefGenerated`；
  >    - `SourceInvalidated`；
  >    - `ReviewRequested`。
  > 11. Domain Event 由 Domain Model 创建。
  > 12. Domain Event 的收集、排序、处理与映射由 Application 层拥有。
  > 13. Domain Event 默认是模块内部的语义对象，不自动持久化。
  > 14. 不要求每个 Domain Event 都一对一映射为数据库记录。
  > 15. 同一 Atomic Business Commit 内需要执行的 Domain Event Handler 必须：
  >    - 在最外层 Application Use Case 拥有的 UoW 中执行；
  >    - 在最终 Commit 前执行；
  >    - 不创建新的嵌套 UoW；
  >    - 不独立 Commit；
  >    - 不访问外部 Provider；
  >    - 不执行 LLM、HTTP、工具调用、消息发布或长时间等待。
  > 16. Commit 前的 Domain Event Handler 可以修改同一事务内允许修改的业务状态，但必须继续遵守 DQ-03 的 Aggregate 边界和 DQ-06 的单一外层 UoW。
  > 17. Domain Event 不等于 Audit Record。
  > 18. Domain Event 不等于 Integration Event。
  > 19. Domain Event 不等于 Durable Work Intent。
  > 20. 一个 Domain Event 可以由 Application 显式映射为：
  >    - Audit Record；
  >    - State Transition Record；
  >    - Integration Event；
  >    - Durable Work Intent；
  >    - 或以上多个记录。
  > 21. 映射必须由明确的 Application Policy 决定，不得由 ORM Hook 或数据库触发器隐式推断。
  >
  > **3.3 Audit Record**
  > 22. Audit Record 是正式、持久化、append-only 的权威问责证据。
  > 23. Audit Record 的主要目的包括：
  >    - accountability；
  >    - investigation；
  >    - compliance；
  >    - user-visible history；
  >    - incident analysis；
  >    - business decision explanation。
  > 24. Audit Record 必须与对应 Business Current Truth 修改处于同一个 DEC-035 Atomic Business Commit。
  > 25. Audit Record 写入失败时，整个业务事务必须回滚。
  > 26. 业务事务回滚时，不得留下该操作的成功 Audit Record。
  > 27. 不得先提交业务状态，再异步补写必须存在的 Audit Record。
  > 28. Audit Record 至少应表达：
  >    - `audit_id`；
  >    - record type；
  >    - actor type；
  >    - actor identity；
  >    - action；
  >    - target type；
  >    - target identity；
  >    - business operation；
  >    - `command_id`；
  >    - correlation identity；
  >    - causation identity；
  >    - base Domain Version；
  >    - resulting Domain Version；
  >    - before revision；
  >    - after revision；
  >    - result；
  >    - reason 或 reason reference；
  >    - actual occurrence time；
  >    - recorded time；
  >    - schema version。
  > 29. `occurred_at` 与 `recorded_at` 必须在语义上分离。
  > 30. `occurred_at` 表示业务事实实际发生或被确认的时间。
  > 31. `recorded_at` 表示系统持久化该记录的时间。
  > 32. Audit Record 不得通过 UPDATE 覆盖或改写历史。
  > 33. Audit 历史更正必须追加新的：
  >    - Correction Record；
  >    - Superseding Record；
  >    - Reversal Record；
  >    - 或语义等价的 append-only 记录。
  > 34. 更正记录必须引用被更正记录。
  > 35. Invalidation 不删除旧 Audit Record。
  > 36. Retraction、Supersession 和 Reversal 不等于物理删除。
  > 37. Audit Record 不得无必要复制完整敏感 Payload。
  > 38. Audit Record 不得包含：
  >    - 明文 Secret；
  >    - 未脱敏 Token；
  >    - 原始密码；
  >    - 不需要的完整 PII；
  >    - ORM Entity；
  >    - SQLAlchemy Session；
  >    - Python Exception 对象；
  >    - 原始数据库错误对象。
  >
  > **3.4 State Transition Record**
  > 39. State Transition Record 表达一个明确的业务状态机迁移。
  > 40. 典型迁移包括：
  >    - DRAFT → IN_REVIEW；
  >    - IN_REVIEW → APPROVED；
  >    - AVAILABLE → LEASED；
  >    - IN_PROGRESS → FAILED_RETRYABLE；
  >    - ACTIVE → SUPERSEDED。
  > 41. State Transition Record 至少应表达：
  >    - state machine identity；
  >    - entity type；
  >    - entity identity；
  >    - from state；
  >    - to state；
  >    - transition type；
  >    - transition reason；
  >    - actor；
  >    - `command_id`；
  >    - expected revision；
  >    - resulting revision；
  >    - occurred time；
  >    - recorded time；
  >    - schema version。
  > 42. State Transition Record 是结构化的状态迁移审计。
  > 43. 当主要目的为问责、历史分析和状态迁移追踪时，它可以作为一种显式类型的 Audit Record。
  > 44. State Transition Record 可以物理存储在同一 append-only Audit Ledger 中，但必须具备：
  >    - 明确 `record_type`；
  >    - Typed Payload Schema；
  >    - Schema Version；
  >    - Transition-specific Constraints；
  >    - 可验证的 from/to state。
  > 45. 允许物理共用 Audit Ledger，不代表语义合并。
  > 46. State Transition Record 不得直接充当 Integration Event。
  > 47. 当状态迁移需要可靠通知其他边界时，必须额外创建独立 Integration Event Outbox Record。
  > 48. State Transition Record 不得充当 Business Current Truth。
  >
  > **3.5 Application Event**
  > 49. Application Event 是本进程、本应用边界内的 Commit 后通知。
  > 50. Application Event 只能在数据库事务成功 Commit 后发布。
  > 51. Application Event 不得在 Commit 前向外部或异步 Handler 发布。
  > 52. Application Event 不得携带：
  >    - 活跃 UoW；
  >    - SQLAlchemy Session；
  >    - ORM Entity；
  >    - Repository；
  >    - 数据库 Connection；
  >    - lazy-loaded relationship。
  > 53. Post-commit Application Event 默认具有以下语义：
  >    ```text
  >    LOCAL
  >    BEST-EFFORT
  >    NON-DURABLE
  >    ```
  > 54. 进程可能在数据库 Commit 后、Application Event 发布前崩溃。
  > 55. Application Event 的丢失不得破坏业务正确性。
  > 56. 任何必须执行的后续工作不得仅依赖 Application Event。
  > 57. 必须执行的后续工作使用 DQ-09 Durable Work Intent。
  > 58. 必须可靠传播到其他边界的事实使用 Transactional Integration Event Outbox。
  > 59. Application Event Handler 失败不得回滚已经成功提交的原业务事务。
  > 60. Application Event Handler 失败的观测、告警和恢复策略归 RFC-007 或相应 Runtime RFC。
  >
  > **3.6 Integration Event**
  > 61. Integration Event 表示已经成功发生、需要传播给其他模块、Bounded Context 或外部系统的业务事实。
  > 62. Integration Event 名称必须采用过去式。
  > 63. Integration Event 不得以 Event 名义表达命令式要求。
  > 64. 「请执行某项工作」的语义属于 Command 或 DQ-09 Durable Work Intent，而不是 Integration Event。
  > 65. 当 Integration Event 需要可靠发布时，必须使用独立的 Transactional Integration Event Outbox。
  > 66. Integration Event Outbox Record 必须与以下内容在同一 PostgreSQL Atomic Business Commit 中写入：
  >    - 产生该事实的业务状态；
  >    - 必要 Domain Version；
  >    - Current Truth Pointer；
  >    - Audit Record；
  >    - State Transition Record，如适用；
  >    - Idempotency Result；
  >    - Integration Event Outbox Record。
  > 67. Integration Event Outbox 写入失败时，业务事务必须整体回滚。
  > 68. 业务事务回滚时，不得留下可发布的成功 Integration Event。
  > 69. 不得先提交业务状态，再以非原子方式补写需要可靠发布的 Integration Event。
  > 70. Integration Event Outbox 与 DQ-09 Durable Work Intent 必须保持独立语义。
  > 71. 两者不得默认共用：
  >    - Identity；
  >    - State Machine；
  >    - Payload Schema；
  >    - Completion State；
  >    - Retry Policy；
  >    - Retention Policy；
  >    - Consumer Protocol。
  > 72. Integration Event 至少应表达：
  >    - `event_id`；
  >    - source；
  >    - event type；
  >    - event schema version；
  >    - subject；
  >    - occurred time；
  >    - recorded time；
  >    - correlation identity；
  >    - causation identity；
  >    - `command_id`；
  >    - Aggregate 或 Business Identity；
  >    - Domain Version Identity；
  >    - payload 或 immutable payload reference。
  > 73. `source` + `event_id` 必须能够唯一识别一个逻辑 Integration Event。
  > 74. 同一个逻辑 Integration Event 的 Retry 或重复投递必须保持相同 Event Identity。
  > 75. Intentional Rerun 所产生的新业务事实可以创建新的 Event Identity，但必须保留 Causation/Correlation 关系。
  > 76. Integration Event Payload 默认只携带消费者真正需要的业务事实和不可变引用。
  > 77. 默认不采用大型 Event-carried State Transfer。
  > 78. 只有在消费者必须脱离源系统独立运行时，才可采用 Event-carried State Transfer。
  > 79. 采用 Event-carried State Transfer 时必须明确：
  >    - 数据所有权；
  >    - Schema Evolution；
  >    - Consumer Compatibility；
  >    - PII/Security；
  >    - Payload Size；
  >    - Retention；
  >    - Correction/Supersession 语义。
  > 80. Integration Event Delivery 为：
  >    ```text
  >    AT-LEAST-ONCE
  >    ```
  > 81. 不承诺：
  >    ```text
  >    EXACTLY-ONCE DELIVERY
  >    ```
  > 82. Exactly-once Business Effect 依赖：
  >    - DQ-08 Idempotency；
  >    - Consumer Dedup；
  >    - Event Identity；
  >    - Consumer Scope；
  >    - Named Unique Constraints；
  >    - Atomic Business Commit。
  > 83. Consumer 必须依据 Event Identity 与 Consumer Scope 去重。
  > 84. Consumer Dedup Marker 与消费产生的业务状态修改必须处于同一数据库事务。
  > 85. Event Relay、Broker、Polling、发布状态机、Dead-letter 和部署拓扑继续由 RFC-003 决定。
  > 86. Integration Event Wire Format 可以采用 CloudEvents-compatible Envelope。
  > 87. CloudEvents-compatible Envelope 只解决事件格式和互操作元数据，不替代：
  >    - Transactional Outbox；
  >    - Atomic Commit；
  >    - Relay；
  >    - Retry；
  >    - Consumer Dedup；
  >    - Delivery Guarantee。
  > 88. CloudEvents 的具体版本、字段映射与协议选择留给 RFC-003 或独立 Integration Design。
  >
  > **3.7 Observability Event**
  > 89. Observability Event 属于 RFC-007 Telemetry 范围。
  > 90. Observability Event 是非权威运行记录，不是业务持久化权威。
  > 91. Observability Event 可以包含：
  >    - trace ID；
  >    - span ID；
  >    - severity；
  >    - timestamp；
  >    - observed timestamp；
  >    - duration；
  >    - retry count；
  >    - provider latency；
  >    - error classification；
  >    - resource attributes；
  >    - deployment information。
  > 92. Observability Event 不是：
  >    - Business Current Truth；
  >    - Audit Record；
  >    - State Transition Record；
  >    - Idempotency Record；
  >    - Durable Work Intent；
  >    - Integration Event。
  > 93. Observability Event 不得触发权威 Business Current Truth 修改。
  > 94. Telemetry Exporter、Collector 或 Backend 故障不得回滚业务事务。
  > 95. Observability Event 可以被采样、聚合或根据运维策略删除。
  > 96. Audit Record 不得因 Telemetry 已存在而省略。
  > 97. Telemetry 不得作为正式业务操作已经成功的唯一证据。
  >
  > **3.8 所有权和分层边界**
  > 98. Domain Event Definition 由所属 Business Module 所有。
  > 99. Audit Ledger 由明确且唯一的 Audit Capability 所有。
  > 100. Integration Event Outbox 由明确且唯一的 Integration Event Capability 所有。
  > 101. Observability Pipeline 由 RFC-007 所有。
  > 102. 业务模块不得直接访问 Audit 或 Integration Event 的 ORM、表、Session 或 Repository。
  > 103. 业务模块必须通过类型化 Application Port 或 Public Application Contract 创建 Audit 和 Integration Event Records。
  > 104. 最外层 Application Use Case 在同一个 UoW 中协调：
  >    - Business State；
  >    - Audit Record；
  >    - State Transition Record；
  >    - Integration Event Outbox；
  >    - 其他 DEC-035 参与者。
  > 105. Repository、ORM Hook、SQLAlchemy Event Listener 和数据库 Trigger 不得隐式决定：
  >    - 是否生成 Domain Event；
  >    - 是否生成 Audit Record；
  >    - 是否生成 Integration Event；
  >    - Integration Event 的业务语义；
  >    - Event Payload。
  > 106. Event Translation、Audit Creation 和 Integration Event Selection 由 Application 层显式拥有。
  > 107. Infrastructure 只负责按照已决定的 Port 和记录模型执行持久化或发布机制。
  >
  > **3.9 非 Event Sourcing**
  > 108. Audit Ledger、State Transition Record 和 Integration Event Outbox 都不是 Business Current Truth。
  > 109. 系统不得依赖上述记录重建全部 Business Current Truth。
  > 110. Business Current Truth 继续由 PostgreSQL 业务模型、版本化历史和 Current Truth Pointer 决定。
  > 111. DQ-10 不引入完整 Event Sourcing。
  > 112. Audit Log、历史记录或事件 Outbox 的存在不等于采用 Event Sourcing。
  > 113. Snapshot、Current Truth、版本化历史与历史保留模型继续由 DQ-11 决定。
  >
  > **3.10 Retention、安全与测试边界**
  > 114. Audit、State Transition 和 Integration Event 的 Retention、Archive 与物理删除由 DQ-15 决定。
  > 115. 在 DQ-15 决定前，不得假设 Audit Records 或 Integration Events 可以短期删除。
  > 116. 正式测试分类和 CI 执行策略由 DQ-16 决定。
  > 117. Encryption、Redaction、Secret、PII 和访问控制由 DQ-17 决定。
  > 118. 所有正式事务语义验证必须使用真实 PostgreSQL。
  > 119. 后续测试至少覆盖：
  >    - Business State 与 Audit Record 同事务提交；
  >    - Audit 写入失败导致业务整体回滚；
  >    - 业务回滚不留下成功 Audit；
  >    - State Transition Record 与对应状态修改同事务；
  >    - Audit Correction 通过追加而不是覆盖；
  >    - Integration Event Outbox 与业务事实同事务；
  >    - Outbox 写入失败导致业务整体回滚；
  >    - Commit 前不发布 Application Event；
  >    - Commit 成功后才发布 Application Event；
  >    - Application Event 丢失不影响业务正确性；
  >    - 重复 Integration Event Delivery 只产生一次业务效果；
  >    - Consumer Dedup 与消费业务更新同事务；
  >    - Telemetry Export 失败不回滚业务事务；
  >    - Durable Work Intent 与 Integration Event 不混用；
  >    - Event/Audit Records 不作为 Current Truth 重建来源。
  > 120. DQ-10 不要求新的独立 Technical Spike。
  > 121. DQ-07 已要求的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效，并应覆盖：
  >    - Integration Event 重复 Delivery；
  >    - Consumer Dedup；
  >    - Relay Crash；
  >    - stale Event Publish Attempt；
  >    - 无部分业务写入。
  >
  > **3.11 Event & Record Classification Table**
  > 122. DQ-10 不新增独立 Matrix。
  > 123. 在持久化实现授权前，Architecture Readiness Package 必须包含 Event & Record Classification Table。
  > 124. Classification Table 至少列出：
  >    - Business Occurrence；
  >    - Domain Event；
  >    - Audit Record；
  >    - State Transition Record；
  >    - Application Event；
  >    - Integration Event；
  >    - Observability Event；
  >    - Owning Module；
  >    - Persistence Required；
  >    - Transaction Boundary；
  >    - Delivery Guarantee；
  >    - Idempotency Identity；
  >    - Schema Version；
  >    - Retention Owner；
  >    - Security Classification；
  >    - Related DQ/DEC/RFC。
  > 125. DQ-10 接受不授权创建或修改该 Classification Table。
  > 126. Classification Table Creation = NOT AUTHORIZED。
  > 127. 不得借 DQ-10 归档任务创建 Audit Schema、Event Schema 或 Event Registry。

---

## DQ-11：Snapshot vs History（快照 vs 历史模型）

- **Question：** 采用 mutable projection / append-only history / versioned snapshots 的何种组合？是否引入 Event Sourcing？
- **Why：** DEC-013 明确「完整事件溯源不属 MVP」，但要求保存必要运行历史与用户修改记录、支持审计/历史对比/回滚分析。
- **Constraints（[DEC 约束]）：** DEC-013 排除完整 ES；DEC-024 版本化历史不删除、旧版本可标 invalid；Invalidation Does Not Mean Deletion。
- **[官方能力/权威]：** Fowler Event Sourcing 分界——「merely keeping a history or writing to a log file could give you an adequate history」，ES 额外之处仅在「用事件重建当前状态」；完整 ES 代价（外部交互重放、schema 演化、bi-temporal 复杂度）正对应 LLM 工作流风险。
- **Candidates：**
  - **A. Current Truth + 版本化历史（不可变旧版本）+ append-only 审计**：满足审计/历史对比/回滚分析，不上 ES。
  - **B. 完整 Event Sourcing**：DEC-013 已排除。
  - **C. 仅当前状态覆盖**：违反 DEC-024 不可覆盖。
- **Trade-offs：** A 满足 DEC 全部需求且无 ES 复杂度；B 提供「事件流重建状态」但 DEC 已排除且代价高；C 违规。
- **Failure modes：** 误上 ES→LLM 外部交互重放/bi-temporal 复杂度；历史与 Current Truth 混淆→旧结果被当有效。
- **Impact on later RFCs：** RFC-003（恢复证据）、RFC-007（回放观测）。
- **Recommendation（历史提案；Superseded by the Accepted Major Revision below）：** **[架构推断] 倾向 A**——current truth + 版本化历史 + append-only 审计；**显式立场：不采用完整 Event Sourcing**（与 DEC-013 一致）。**置信度：高**。候选关系：**Candidate A = ACCEPTED WITH MAJOR REVISION**（Formal Model = Authoritative Current Truth + Immutable Business Version Snapshots + Append-only Audit/State Transition History + Optional Derived Query Projections）；**Candidate B = REJECTED**（FULL EVENT SOURCING CONFLICTS WITH DEC-013）；**Candidate C = REJECTED**（CURRENT-STATE-ONLY OVERWRITE CONFLICTS WITH DEC-024）；**Delta-only Version History = REJECTED AS AUTHORITATIVE MVP HISTORY MODEL**。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**
  > **3.1 总体持久化模型**
  > 1. MVP 采用以下组合模型：
  >    ```text
  >    AUTHORITATIVE CURRENT TRUTH
  >    + IMMUTABLE BUSINESS VERSION SNAPSHOTS
  >    + APPEND-ONLY AUDIT / STATE TRANSITION HISTORY
  >    + OPTIONAL DERIVED QUERY PROJECTIONS
  >    ```
  > 2. PostgreSQL Business Current Truth 继续是唯一业务权威来源。
  > 3. Current Truth 由以下组合表达：
  >    ```text
  >    Logical Business Object
  >    + Explicit Current Truth Pointer
  >    + Selected Immutable Business Version
  >    ```
  > 4. Audit Record、State Transition Record、Domain Event、Integration Event、Workflow Checkpoint、Observability Event 和 Query Projection 均不构成 Business Current Truth。
  > 5. 项目不采用完整 Event Sourcing。
  > 6. 系统不得通过重放以下记录重建权威 Business Current Truth：
  >    - Audit Record；
  >    - State Transition Record；
  >    - Domain Event；
  >    - Application Event；
  >    - Integration Event；
  >    - Observability Event；
  >    - Durable Work Intent；
  >    - Workflow Checkpoint。
  > 7. Candidate A 被接受并进行重大修订。
  > 8. Candidate B 完整 Event Sourcing 被拒绝。
  > 9. Candidate C 仅覆盖 Current State、丢失版本历史的模型被拒绝。
  > 10. Delta-only Version History 不作为 MVP 权威业务历史模型。
  >
  > **3.2 Version Boundary**
  > 11. 每个需要历史、比较、审查、恢复或可追溯性的业务对象，必须具有明确的 Version Boundary。
  > 12. Version Boundary 必须遵守 DQ-03 的 Aggregate Boundary 与 DQ-02 的唯一模块所有权。
  > 13. 不得创建跨所有模块的 Task Mega Snapshot。
  > 14. 一个 Business Version 默认属于一个明确的 Logical Business Object。
  > 15. 跨 Aggregate Composite Commit 如有明确业务不变量，可以在同一事务中创建多个彼此独立的 Business Version。
  > 16. 多 Aggregate Commit 中，每个 Aggregate 必须保留自己的：
  >    - logical object identity；
  >    - domain version identity；
  >    - version number；
  >    - Current Truth Pointer；
  >    - Aggregate invariants。
  > 17. 多个版本可以通过：
  >    - Command ID；
  >    - Correlation ID；
  >    - Causation ID；
  >    - Commit Identity；
  >    建立因果关系，但不得因此合并成一个跨模块 Mega Snapshot。
  >
  > **3.3 Immutable Business Version Snapshot**
  > 18. 每个正式 Business Version 使用 DQ-04 已接受的：
  >    ```text
  >    logical_object_id
  >    domain_version_id
  >    version_number
  >    ```
  > 19. `domain_version_id` 不可变、不得复用。
  > 20. `version_number` 在同一 Logical Business Object 内单调递增。
  > 21. 已提交的 Version Number 不得因 Invalidation、Rejection、Supersession、Restore、Archive 或 Retention 而重新使用。
  > 22. 一个 Business Version 一经正式提交，其业务语义必须不可变。
  > 23. 普通 Application Command 不得 UPDATE 已提交版本的业务内容。
  > 24. 普通 Application Command 不得 DELETE 已提交历史版本。
  > 25. 修正业务内容必须创建新的正式 Business Version。
  > 26. Invalidation 必须保留原版本。
  > 27. Rejection 必须保留被拒绝版本。
  > 28. Supersession 必须保留被取代版本。
  > 29. Restore 不得修改被恢复来源版本。
  > 30. 每个正式版本至少必须包含或等价表达：
  >    - Snapshot Schema Version；
  >    - Logical Object Identity；
  >    - Domain Version Identity；
  >    - Version Number；
  >    - Creation Command Identity；
  >    - Creation Actor；
  >    - Created Time；
  >    - Recorded Time；
  >    - Business Content；
  >    - Immutable Dependency References；
  >    - Status 或 Validity；
  >    - Provenance；
  >    - Causation / Parent / Derived-from relationship。
  > 31. 精确表名、字段名、索引和物理模型留待实现设计。
  >
  > **3.4 逻辑完整 Snapshot**
  > 32. 正式 Business Version 必须具有逻辑完整快照语义。
  > 33. “逻辑完整”表示：读取某个历史版本时，无需从第一个版本开始重放全部 Event 或 Delta，即可恢复该版本的业务含义。
  > 34. Delta-only Chain 不作为权威历史读取路径。
  > 35. 不得要求使用：
  >    ```text
  >    V1 full
  >    + V2 delta
  >    + V3 delta
  >    + V4 delta
  >    ```
  >    才能理解 V4 的完整业务语义。
  > 36. 逻辑完整 Snapshot 可以物理分布在：
  >    - Version Root；
  >    - Version-owned Child Rows；
  >    - Immutable Value Objects；
  >    - Immutable Source/Evidence References；
  >    - Immutable External Object References；
  >    - Version-owned Association Rows。
  > 37. “逻辑完整”不意味着所有数据必须复制到一个 JSONB 字段。
  > 38. 物理规范化不能破坏版本语义独立性。
  > 39. 读取历史版本时，不得依赖后来变化的 Current Truth Pointer。
  > 40. 读取历史版本时，不得通过可变的 `current_source_version`、`current_dependency` 或其他 Current Pointer 解析当时业务含义。
  > 41. 影响历史版本业务语义的依赖必须固定到：
  >    - Source Version Identity；
  >    - Evidence Version Identity；
  >    - Dependency Version Identity；
  >    - Content Hash；
  >    - Prompt / Model / Configuration Version Reference；
  >    - 其他不可变引用。
  > 42. Source、Evidence、大对象和外部对象的持久化边界继续由 DQ-12 决定。
  > 43. Snapshot Schema Evolution、Upcasting、Compatibility Read 和数据迁移由 DQ-14 决定。
  > 44. Business Immutability 表示普通业务操作不能改写已提交版本的业务语义。
  > 45. Business Immutability 不排除以后经过明确治理的确定性 Schema Migration。
  > 46. Schema Migration 不得伪装成普通 Business Command。
  >
  > **3.5 Version Creation Boundary**
  > 47. 只有成功完成正式 Atomic Business Commit 的操作才能产生正式 Domain Version。
  > 48. 以下情况不得产生新的正式 Domain Version：
  >    - Database Transaction Retry；
  >    - SQLSTATE 40001 Retry；
  >    - SQLSTATE 40P01 Retry；
  >    - Work Execution Retry；
  >    - Provider Retry；
  >    - Worker Crash Recovery；
  >    - Lease Renewal；
  >    - Heartbeat；
  >    - Checkpoint Save；
  >    - Workflow Resume 本身；
  >    - Observability Update；
  >    - Telemetry Export；
  >    - 最终回滚的事务；
  >    - 未提交的 LLM 临时输出；
  >    - 草稿计算中间结果；
  >    - 仅状态探测或健康检查。
  > 49. Intentional Rerun 成功后可以产生新的 Domain Version。
  > 50. 正式改变业务内容或有效业务含义的操作应创建新版本。
  > 51. 仅改变以下运行状态不得创建 Domain Version：
  >    - Lease Holder；
  >    - Attempt ID；
  >    - Retry Counter；
  >    - Heartbeat；
  >    - Worker Runtime State；
  >    - Checkpoint Position；
  >    - Telemetry Metadata。
  > 52. Audit Record 的产生不必然意味着创建新的 Domain Version。
  > 53. Domain Version Creation Policy 必须由 Application 层显式决定。
  > 54. 不得仅依赖 ORM Dirty Tracking 或 SQLAlchemy Flush 检测决定是否创建正式版本。
  >
  > **3.6 Current Truth Pointer**
  > 55. Current Truth Pointer 是可变的权威当前版本选择器。
  > 56. Current Truth Pointer 必须拥有独立、非空的 `revision`。
  > 57. 修改 Current Truth Pointer 必须携带 `expected_revision`。
  > 58. Pointer 更新必须使用 DQ-04 的 Compare-and-Swap 条件更新。
  > 59. CAS 影响零行时必须返回并发冲突，并回滚完整 Atomic Business Commit。
  > 60. 一个明确 Business Scope 内最多只能有一个 Current Effective Version。
  > 61. 某些业务对象可以显式处于：
  >    ```text
  >    NO_CURRENT_TRUTH
  >    ```
  > 62. Current Truth Pointer 不得指向：
  >    - Invalid Version；
  >    - Rejected Version；
  >    - Physically Unavailable Version；
  >    - 不属于同一 Logical Business Object 的版本；
  >    - 未完成正式 Commit 的版本；
  >    - 已被安全策略禁止使用的版本。
  > 63. `MAX(version_number)` 不得被用作 Current Truth Selector。
  > 64. `ORDER BY version_number DESC LIMIT 1` 不得隐式等同于 Current Truth 查询。
  > 65. 以下概念必须具有独立命名与查询语义：
  >    ```text
  >    latest_created_version
  >    latest_approved_version
  >    current_effective_version
  >    ```
  > 66. Query、Repository、API 和 Application Contract 不得隐式混用上述选择器。
  > 67. Current Truth 查询必须通过 Current Truth Pointer 或等价的显式权威选择规则。
  > 68. Current Truth Pointer 不是历史记录本身，而是对不可变版本的权威当前选择。
  >
  > **3.7 Promotion**
  > 69. 一个已正式创建、但尚未成为 Current Truth 的不可变 Candidate Version，可以通过显式 Promotion Command 成为 Current Truth。
  > 70. Promotion 必须重新验证：
  >    - Candidate 状态；
  >    - Business Invariants；
  >    - expected revision；
  >    - Evidence Validity；
  >    - Source Validity；
  >    - Review Decision；
  >    - Security Constraints；
  >    - Current Concurrency Ownership；
  >    - Candidate 与 Logical Object 的所属关系。
  > 71. Promotion 必须与以下适用参与者在同一 PostgreSQL Atomic Business Commit 中提交：
  >    - Current Truth Pointer；
  >    - Stage State；
  >    - Audit Record；
  >    - State Transition Record；
  >    - Idempotency Result；
  >    - Integration Event Outbox；
  >    - Durable Work Intent；
  >    - 其他 DEC-035 必须参与者。
  > 72. Promotion 不得修改被 Promote 的不可变 Version Content。
  >
  > **3.8 Invalidation**
  > 73. Current Version 被 Invalidate 后不得继续作为 Current Truth。
  > 74. Invalidation 不得删除原版本。
  > 75. Invalidation 不得自动执行：
  >    ```text
  >    select previous maximum valid version
  >    ```
  > 76. Invalidation 不得静默回退至：
  >    - 前一个 Version Number；
  >    - 最近 Approved Version；
  >    - 任意仍标记 Valid 的历史版本；
  >    - 任何未经当前规则重新验证的版本。
  > 77. Invalidation 后必须显式选择：
  >    - 创建 Replacement Version；
  >    - Promote 一个已审查 Candidate Version；
  >    - 执行 Restore；
  >    - 进入 `NO_CURRENT_TRUTH`；
  >    - 或其他由明确业务不变量允许的状态。
  > 78. Invalidation 必须追加 Audit 与 State Transition Evidence。
  > 79. Invalidation 与 Current Truth Pointer 修改必须使用 CAS。
  >
  > **3.9 Restore**
  > 80. 将历史内容重新恢复为当前业务状态时，必须执行显式 Restore Command。
  > 81. Restore 是新的前向 Business Operation。
  > 82. Restore 不是 Database Transaction Rollback。
  > 83. Restore 必须创建新的：
  >    ```text
  >    domain_version_id
  >    version_number
  >    command_id
  >    audit record
  >    ```
  > 84. Restore 后的新版本必须记录：
  >    - `restored_from_version_id`；
  >    - restore reason；
  >    - restored by；
  >    - restore command identity；
  >    - restore time；
  >    - 当前验证通过的 Source/Evidence references。
  > 85. Restore 不得原地修改被引用的历史版本。
  > 86. Restore 不得简单把 Current Truth Pointer 直接重新指向一个曾被 Supersede、Invalidate 或失效的旧版本。
  > 87. Restore 必须重新验证：
  >    - 当前 Business Rules；
  >    - Current Source/Evidence Validity；
  >    - Security and Permission；
  >    - Review Requirements；
  >    - Current Schema Compatibility；
  >    - expected revision；
  >    - 并发状态；
  >    - 当前依赖有效性。
  > 88. Restore 必须作为新的 Atomic Business Commit。
  > 89. Restore 成功后产生的新版本可以在内容上等价于历史版本，但必须具有新的 Version Identity 和新的业务因果记录。
  > 90. Database Rollback 与 Business Restore 必须使用不同术语、不同 Port、不同 Application Contract 与不同测试。
  >
  > **3.10 Mutable Query Projection**
  > 91. Mutable Query Projection 可以用于提升读取、列表、搜索和聚合查询性能。
  > 92. Query Projection 默认是派生数据。
  > 93. Query Projection 不是 Business Current Truth。
  > 94. Query Projection 可以位于同一 PostgreSQL 服务中，不要求独立数据库。
  > 95. DQ-11 不强制采用 CQRS。
  > 96. DQ-11 不强制采用独立 Read Store。
  > 97. Projection 可以从 Current Truth Pointer 和 Version Tables 构建。
  > 98. Projection 不要求通过 Event Stream 重放构建。
  > 99. Projection 延迟、损坏、丢失或重建不得改变 Business Current Truth。
  > 100. State-changing Command 不得只依赖可能过期的 Projection 决定最终 Commit。
  > 101. 如果 Command 使用 Projection 进行候选筛选，最终 Commit 前必须重新读取并验证权威 Current Truth。
  > 102. Projection 必须具有明确：
  >    - Owning Module；
  >    - Source of Truth；
  >    - Rebuild Strategy；
  >    - Consistency Level；
  >    - Allowed Query Use；
  >    - Failure Handling；
  >    - Freshness Expectation。
  > 103. Projection 是事务内同步、异步维护或按需重建，留待具体 Query Model 设计。
  > 104. Projection Rebuild 不得创建新的 Domain Version。
  >
  > **3.11 历史读取语义**
  > 105. 系统至少必须支持以下逻辑读取能力：
  >    ```text
  >    Read Current Truth
  >    Read Version by domain_version_id
  >    Read Version by version_number
  >    List Version History
  >    Compare Two Versions
  >    Read Audit Timeline
  >    Read State Transition Timeline
  >    Request Explicit Restore
  >    ```
  > 106. 历史版本读取必须返回当时正式提交的业务语义。
  > 107. 后续 Current Truth、Source Current Pointer、Dependency Current Pointer 或 Projection 的变化，不得改变已提交历史版本的展示结果。
  > 108. Version History 使用 `version_number` 表达同一 Logical Object 内的业务版本顺序。
  > 109. Timestamp 不得作为唯一 Version Identity 或唯一版本排序依据。
  > 110. Audit Timeline 使用 DQ-10 的：
  >    - `occurred_at`；
  >    - `recorded_at`；
  >    - stable Audit Identity；
  >    表达审计顺序。
  > 111. Audit Timeline 可以解释状态如何变化，但不得作为重建 Business Current Truth 的权威输入。
  > 112. Version Compare 必须比较两个不可变 Business Version Snapshot。
  > 113. Version Compare 不得比较两个时间点的可变 Projection 并将其称为历史版本比较。
  > 114. API 路径、分页、Diff Response、Restore Endpoint、Authorization 与用户可见性继续由 RFC-004 决定。
  >
  > **3.12 Temporal / Bitemporal Boundary**
  > 115. DQ-11 不在 MVP 中引入通用 Bitemporal Database Model。
  > 116. Application Time 与 System / Recorded Time 是不同概念。
  > 117. 只有存在明确业务需求时，才为具体业务对象建模 Application Time。
  > 118. 不要求每张业务表具有：
  >    ```text
  >    valid_from
  >    valid_to
  >    system_from
  >    system_to
  >    ```
  > 119. 不要求实现全项目通用 SQL `AS OF` 查询层。
  > 120. 不要求通过数据库系统版本时间自动生成业务历史。
  > 121. 具有未来生效、追溯生效、法规时间或合同有效期需求的对象，应通过后续独立业务决定扩展。
  > 122. 普通 `created_at` 不得被当作完整 Application Time、Effective Time 或 Bitemporal Model。
  >
  > **3.13 Atomic Commit 与并发**
  > 123. 新 Domain Version 创建必须与所有适用参与者处于同一个 DEC-035 Atomic Business Commit。
  > 124. 适用参与者包括：
  >    - Evidence Links；
  >    - Current Truth Pointer；
  >    - Stage State；
  >    - Audit Record；
  >    - State Transition Record；
  >    - Idempotency Result；
  >    - Integration Event Outbox；
  >    - Durable Work Intent；
  >    - Result Reference；
  >    - 其他被业务不变量要求的记录。
  > 125. Version Number 分配与 Version Insert 必须处于同一事务。
  > 126. Version Insert 与 Current Truth Pointer CAS 必须处于同一事务。
  > 127. Current Truth Pointer CAS 失败时，整个事务必须回滚。
  > 128. 冲突或失败事务不得留下：
  >    - 孤立 Domain Version；
  >    - 已更新 Current Truth Pointer；
  >    - 已完成 Stage State；
  >    - 成功 Audit Record；
  >    - 成功 State Transition Record；
  >    - 成功 Idempotency Result；
  >    - 可发布 Integration Event；
  >    - 可领取 Durable Work Intent；
  >    - 部分 Evidence Links。
  > 129. 数据库事务 Retry 必须复用同一 Logical Command Identity。
  > 130. 数据库事务 Retry 不得创建额外正式版本。
  > 131. 并发 Version Creation 必须通过唯一约束与 CAS 防止：
  >    - 重复 Version Number；
  >    - 重复 Domain Version Identity；
  >    - 静默覆盖 Current Truth；
  >    - 孤立 Version。
  > 132. 跨 Aggregate Composite Commit 如确有明确同步不变量，可以创建多个独立版本，但不得创建跨所有模块的 Mega Snapshot。
  >
  > **3.14 Retention 与删除**
  > 133. 正常业务流程不得物理删除历史 Business Version。
  > 134. Invalidation、Rejection、Supersession、Promotion 和 Restore 均不得删除旧版本。
  > 135. Archive、Cold Storage、Physical Deletion、Legal Hold 与法规删除由 DQ-15 决定。
  > 136. PII、Encryption、Redaction、Access Control 与删除例外由 DQ-17 决定。
  > 137. 在 DQ-15 和 DQ-17 正式决定前，不得假设历史版本可以被短期删除。
  > 138. Physical Storage Optimization 不得破坏历史版本的逻辑完整性和可验证性。
  >
  > **3.15 Snapshot 术语边界**
  > 139. `Business Version Snapshot` 表示不可变业务版本。
  > 140. `Workflow Checkpoint` 表示 Runtime 恢复状态。
  > 141. `Database Backup Snapshot` 表示基础设施灾难恢复副本。
  > 142. `Event-Sourcing Snapshot` 表示 Event Stream 重放优化。
  > 143. `Query Projection` 表示派生读取模型。
  > 144. 上述五种概念必须保持独立语义。
  > 145. Business Version Snapshot 不得被 LangGraph Checkpoint 替代。
  > 146. Workflow Checkpoint 不得作为 Business Version History。
  > 147. Database Backup 不得作为用户可查询的业务历史。
  > 148. Query Projection 不得作为不可变历史证据。
  > 149. 本项目不使用 Event-Sourcing Snapshot，因为 Event Stream 不是 Business Current Truth。
  >
  > **3.16 实现前置条件**
  > 150. DQ-11 不新增独立 Matrix。
  > 151. 已要求的 Aggregate / Invariant Matrix 必须在未来获得授权时扩展：
  >    - Current Truth Owner；
  >    - Versioned Object；
  >    - Version Boundary；
  >    - Version Creation Trigger；
  >    - Snapshot Granularity；
  >    - Logical Completeness Rule；
  >    - Current Truth Selector；
  >    - Promotion Rule；
  >    - Invalidation Rule；
  >    - Restore Rule；
  >    - Historical Dependency References；
  >    - Projection Source of Truth；
  >    - Retention Owner；
  >    - Related DQ/DEC/RFC。
  > 152. DQ-11 接受不授权创建或修改 Aggregate / Invariant Matrix。
  > 153. DQ-11 不要求新的独立 Technical Spike。
  > 154. 已要求的真实 PostgreSQL Concurrency Technical Spike 在未来获得授权后必须覆盖：
  >    - Concurrent Version Number Allocation；
  >    - Current Truth Pointer CAS；
  >    - Current Version Invalidation；
  >    - Promotion-versus-Invalidation；
  >    - Restore-versus-New Write；
  >    - Concurrent Restore；
  >    - No Orphan Version；
  >    - No Partial Atomic Commit。
  > 155. 本次归档不得创建 Spike Issue、Branch、PR、代码、测试或基础设施。
  >
  > **3.17 测试前置语义**
  > 156. 所有正式 Snapshot / History 事务语义测试必须使用真实 PostgreSQL。
  > 157. 后续测试至少覆盖：
  >    - 正式 Commit 创建一个不可变 Business Version；
  >    - Database Retry 不创建额外正式版本；
  >    - Work Retry 不创建额外正式版本；
  >    - 事务回滚不留下 Version；
  >    - 普通业务 Command 不能修改历史版本；
  >    - `MAX(version_number)` 与 Current Truth 不同时仍返回正确 Current Truth；
  >    - Latest Created、Latest Approved 与 Current Effective 保持独立；
  >    - Invalidation 不删除历史版本；
  >    - Invalidation 不静默回退；
  >    - Promotion 重新验证业务条件；
  >    - Restore 创建新 Version 并保留 `restored_from_version_id`；
  >    - Restore 不修改来源版本；
  >    - Historical Read 不受后续 Current Truth 变化影响；
  >    - Historical Dependency 固定到不可变版本；
  >    - Projection 损坏不改变 Current Truth；
  >    - Audit/Event Replay 不是 Current Truth 恢复路径；
  >    - Concurrent Version Creation 不产生重复 Version Number；
  >    - CAS 冲突不产生部分写入；
  >    - 多 Aggregate Commit 不创建 Mega Snapshot；
  >    - Snapshot Schema Migration 与普通 Business Mutation 被正确区分。
  > 158. 详细测试分类与 CI 策略继续由 DQ-16 决定。

---

## DQ-12：Source & Evidence Persistence（来源与证据持久化）

- **Question：** 原始内容直接存业务库 vs 只存引用+对象存储？大内容/二进制边界？checksum/normalized source/provenance？Evidence-to-claim 链接形态？Retrieval Index 与 Current Truth 的持久化关系？
- **Why：** DEC-025 确立 Source/Evidence 独立语义；原始输入不被覆盖；Fragment 可回原文 + checksum + provenance。须定落库形态但**不决定检索实现（RFC-005）**。
- **Constraints（[DEC 约束]）：** DEC-025 Source/SourceVersion/Fragment/EvidenceLink 语义；DEC-012 原始与解析分离；DEC-024 Retrieval Index 为独立存储类别。
- **[官方能力]：** PG TOAST（大文本透明线外存储）/ bytea / Large Object（流式、特大）；jsonb+GIN。SQLite JSON=TEXT（无 GIN）。官方未强制「大 blob 一律外部存储」。
- **Candidates：**
  - **A. 中小原始内容存 DB（TOAST/jsonb），特大/二进制存外部对象存储 + DB 指针**。
  - **B. 全部存 DB**：一致性强但大对象膨胀。
  - **C. 全部外部存储 + DB 引用**：DB 轻但一致性协调复杂。
- **Trade-offs：** A 平衡事务一致性与体积；B 简单但不可伸缩；C 需「DB 指针+外部对象」一致性协调（官方未涵盖，推断）。
- **Failure modes：** 大对象入 DB→备份/查询膨胀；外部存储指针失效→证据不可回原文；Fragment 无 checksum→无法验证完整性。
- **Impact on later RFCs：** RFC-005（检索索引/embedding/chunking——**本 DQ 不决定**）。
- **Recommendation：** **[架构推断] 倾向 A**——DB 存中小原始内容与全部证据元数据/链接（含 content_hash、parser_version provenance），特大/二进制走外部对象存储 + 引用；Retrieval Index 落点边界定给 RFC-005。**置信度：中**。（**历史提案；Superseded by the Accepted Major Revision below。**）
- **Candidate 处置（2026-08-02 用户正式决定）：** Candidate A = **ACCEPTED WITH MAJOR REVISION**（Formal Model = PostgreSQL Authoritative Source/Evidence Graph + Immutable Content-addressed Source Blobs + Versioned Derived Artifacts and Fragments + Explicit Evidence-to-Claim Links + Rebuildable Non-authoritative Retrieval Index）；Candidate B = **REJECTED AS UNIVERSAL ALL-CONTENT-IN-POSTGRESQL POLICY**（不表示 PostgreSQL 不能保存中小文本/规范化内容/Fragment/结构化元数据）；Candidate C = **REJECTED AS UNIVERSAL ALL-CONTENT-IN-OBJECT-STORAGE POLICY**（不表示对象存储不能保存大型/二进制/流式/对备份影响显著的原始内容）；PostgreSQL Large Object = **NOT SELECTED AS DEFAULT MVP STORAGE PATH**（未来引入须独立架构与生命周期审查）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**

  > **3.1 总体模式**
  >
  > 1. MVP 采用以下 Source 与 Evidence 持久化模型：
  >
  >    ```text
  >    POSTGRESQL AUTHORITATIVE SOURCE / EVIDENCE GRAPH
  >    + IMMUTABLE CONTENT-ADDRESSED SOURCE BLOBS
  >    + VERSIONED DERIVED ARTIFACTS AND FRAGMENTS
  >    + EXPLICIT EVIDENCE-TO-CLAIM LINKS
  >    + REBUILDABLE NON-AUTHORITATIVE RETRIEVAL INDEX
  >    ```
  >
  > 2. PostgreSQL 是 Source/Evidence 业务身份、状态、关系、Provenance、Fragment 和 Evidence Link 的唯一权威来源。
  > 3. 对象存储只负责保存符合外部存储策略的不可变内容字节。
  > 4. 对象存储不是 Business Current Truth。
  > 5. Retrieval Index 不是 Business Current Truth。
  > 6. Search Result、Vector ID、Embedding 或 Ranking Score 均不是正式 Evidence。
  > 7. Candidate A 被接受并进行重大修订。
  > 8. Candidate B 作为「全部内容无条件存入 PostgreSQL」的通用策略被拒绝。
  > 9. Candidate C 作为「全部内容无条件存入对象存储，仅在数据库保存引用」的通用策略被拒绝。
  > 10. Candidate B 被拒绝不表示 PostgreSQL 不能保存中小文本、规范化内容、Fragment 或结构化元数据。
  > 11. Candidate C 被拒绝不表示对象存储不能保存大型、二进制、流式或对数据库备份有显著影响的原始内容。
  > 12. PostgreSQL Large Object 不作为 MVP 默认存储路径。
  > 13. 如果未来需要引入 PostgreSQL Large Object，必须进行独立架构与生命周期审查。
  >
  > **3.2 核心身份分离**
  >
  > 14. 必须明确区分：Source；SourceVersion；ContentObject；Acquisition；DerivedArtifact；Fragment；FragmentSet；EvidenceLink；RetrievalChunk；RetrievalIndexEntry。
  > 15. 上述身份不得通过一个通用 `document_id`、`source_id` 或无类型 JSON 对象隐式合并。
  > 16. Source 表示一个逻辑来源。
  > 17. Source 可以表示：网页；文件来源；API 资源；用户上传来源；外部数据库记录；Provider 返回来源；其他稳定逻辑来源。
  > 18. Source 不等于一次具体内容抓取结果。
  > 19. SourceVersion 表示某个 Source 在一次正式捕获中的不可变内容状态。
  > 20. SourceVersion 必须拥有稳定且不可复用的身份。
  > 21. SourceVersion 不得被后续抓取结果覆盖。
  > 22. ContentObject 表示实际物理字节对象。
  > 23. SourceVersion 必须引用一个已经验证的 ContentObject 或符合 Storage Policy 的 PostgreSQL Inline Content。
  > 24. Acquisition 表示一次获取尝试或获取活动。
  > 25. Acquisition 不等于 SourceVersion。
  > 26. 失败的下载、超时、认证失败、Parser Failure 或 Checksum Failure 不得产生正式 SourceVersion。
  > 27. DerivedArtifact 表示由 SourceVersion 或其他 DerivedArtifact 生成的版本化派生产物。
  > 28. Fragment 表示可稳定定位、可验证完整性并可用于 Evidence 引用的内容单位。
  > 29. RetrievalChunk 表示为检索效果生成的派生切片。
  > 30. Fragment 与 RetrievalChunk 可以在特定实现中重合，但不得被架构上定义为同一身份。
  > 31. EvidenceLink 是一个显式业务关系。
  > 32. EvidenceLink 不等于 Retrieval 命中结果。
  >
  > **3.3 Source 和 SourceVersion**
  >
  > 33. 一个 Source 可以拥有多个 SourceVersion。
  > 34. SourceVersion 必须保留：Source Identity；Content Identity；Acquisition Identity；Provenance；Captured/Observed Time；Recorded Time；Validity/Availability 状态；Schema Version。
  > 35. 同一 Source 多次抓取到不同内容时，必须创建不同 SourceVersion。
  > 36. 重复抓取到相同物理字节时，可以复用相同 ContentObject。
  > 37. 复用 ContentObject 不得自动合并不同 SourceVersion。
  > 38. 是否创建新的 SourceVersion 必须由显式 Application Policy 决定。
  > 39. 不得仅依据 Content Hash 自动合并：不同来源；不同获取时间；不同权限；不同 Provenance；不同法律或 Retention 要求。
  > 40. 如果业务需要 Current Source Version，必须使用显式 Source Current Pointer 或等价权威选择规则。
  > 41. 历史 Business Version 和 EvidenceLink 不得通过 Source Current Pointer 解析内容。
  > 42. 历史引用必须固定到不可变 SourceVersion。
  >
  > **3.4 PostgreSQL 权威数据**
  >
  > 43. PostgreSQL 至少保存或等价表达：Source；SourceVersion；Acquisition；ContentObject Metadata；Content Hash Algorithm；Content Hash；Byte Length；Media Type；Character Encoding；Storage Classification；Storage Location Type；Object Reference；Integrity State；Availability State；Provenance；DerivedArtifact；Fragment；FragmentSet；EvidenceLink；Current Pointer，如适用；Revision；Audit References。
  > 44. PostgreSQL 负责判断：哪个 SourceVersion 正式存在；哪个 ContentObject 已通过验证；哪个 Fragment 属于哪个 SourceVersion；哪个 EvidenceLink 支持哪个 Business Version 或 Claim；哪条关系当前有效；哪个对象发生 Integrity Incident。
  > 45. 对象存储不得成为 SourceVersion、EvidenceLink 或 Claim 关系的权威查询来源。
  > 46. Retrieval Index 不得成为 SourceVersion、Fragment 或 EvidenceLink 身份的权威来源。
  >
  > **3.5 Storage Classification Policy**
  >
  > 47. 内容存储位置必须依据显式 Storage Classification Policy 决定。
  > 48. RFC-002 不硬编码一个任意字节阈值作为所有内容的永久业务规则。
  > 49. Storage Classification 至少考虑：Content Size；Media Type；Character Encoding；Streaming Requirement；Range-read Requirement；Backup/Restore Impact；Query Pattern；Parsing Requirement；Retention；Security Classification；Legal Hold；Cost；Expected Access Frequency。
  > 50. 默认可存入 PostgreSQL 的内容包括：结构化元数据；Source/Evidence 关系；Provenance；中小原始文本；规范化文本；Parsed Structured Data；Canonical Fragment；EvidenceLink；小型 JSONB Metadata。
  > 51. 默认应考虑外部对象存储的内容包括：大型原始文档；二进制文件；图片；音频；视频；Archive；需要流式访问的内容；对数据库 Backup/Vacuum/Replication 产生显著影响的内容。
  > 52. 上述分类是默认方向，不替代未来正式 Storage Classification Table。
  > 53. PostgreSQL TOAST 是透明物理机制。
  > 54. TOAST 不得被描述为 Source/Evidence 业务存储策略。
  > 55. TOAST 内部阈值不得被直接当作业务上的 Inline/External 分界。
  > 56. PostgreSQL Large Object 不作为默认 MVP 路径。
  > 57. 若未来使用 Large Object，必须单独明确：Ownership；ACL；Backup/Restore；Orphan Cleanup；Driver Support；Transaction Semantics；Migration；Monitoring。
  >
  > **3.6 Raw 与 Derived 分离**
  >
  > 58. 必须分离：Raw Source Content；Normalized Content；Parsed Artifact；OCR Artifact；Canonical Fragment；Retrieval Chunk；Embedding。
  > 59. Raw Source Content 表示获取时的原始不可变字节。
  > 60. Raw Content 不得被 Parser、Normalizer、OCR 或 Chunking Process 原地覆盖。
  > 61. Normalized Content 是版本化 DerivedArtifact。
  > 62. Parsed Artifact 是版本化 DerivedArtifact。
  > 63. OCR Artifact 是版本化 DerivedArtifact。
  > 64. Parser、Normalizer、OCR、Extraction 或 Chunking 规则发生变化时，必须产生新的 DerivedArtifact Version 或 FragmentSet。
  > 65. 旧 DerivedArtifact 和旧 FragmentSet 不得因新处理流程运行而被覆盖。
  > 66. DerivedArtifact 至少必须记录：Derived Artifact Identity；Input SourceVersion/Artifact Identity；Process Type；Processor Identity；Processor Version；Configuration/Profile Version；Output ContentObject 或 Inline Content；Output Hash；Generated Time；Recorded Time；Provenance；Schema Version。
  > 67. DerivedArtifact 可以从另一个 DerivedArtifact 派生，但必须保留完整 Derivation Chain。
  > 68. DerivedArtifact 不得静默引用输入 Source 的最新版本。
  >
  > **3.7 Content Hash**
  >
  > 69. 每个 ContentObject 必须至少记录：Hash Algorithm；Content Hash；Byte Length；Media Type。
  > 70. Hash 字段不得只保存一个没有算法身份的通用 `checksum`。
  > 71. Raw Content Hash 必须基于原始字节计算。
  > 72. Normalized Content Hash 必须基于规范化结果单独计算。
  > 73. Raw Hash 与 Normalized Hash 不得混用。
  > 74. Parsed Artifact、Fragment 和 RetrievalChunk 可以拥有各自独立 Hash。
  > 75. 对象存储 ETag 不得作为项目权威 Content Hash。
  > 76. Provider 返回的 Checksum 可以作为辅助存储验证信息，但不能替代项目定义的 Content Hash。
  > 77. Hash Algorithm 升级与安全要求继续由 DQ-17 决定。
  > 78. 在 DQ-17 决定前，记录模型必须能够显式保存 Algorithm + Value。
  > 79. Hash 相同只能证明按对应算法计算的字节内容一致。
  > 80. Hash 相同不能证明：Source 相同；Provenance 相同；权限相同；法律状态相同；Evidence 含义相同。
  >
  > **3.8 Content-addressed Object Storage**
  >
  > 81. 外部 Blob 应优先使用内容寻址或等价不可变 Object Key。
  > 82. 推荐 Key 形态可以等价表达：
  >
  >    ```text
  >    <algorithm>/<content-hash>
  >    ```
  >
  > 83. 精确 Bucket、Provider、Region、Prefix 和 Key Encoding 留待实现设计与安全决定。
  > 84. 写入必须采用 Put-if-absent、Conditional Put 或等价条件创建机制。
  > 85. 不得无条件覆盖已存在的 Content-addressed Object。
  > 86. 相同 Key 已存在时，必须验证：Project Content Hash；Byte Length；Media Type，如适用；Provider Checksum，如适用。
  > 87. 同一 Key 对应不同字节时必须视为严重完整性冲突。
  > 88. Object Key 不得直接暴露：原始文件名；完整 Source URL；User Name；Tenant Identity；Token；Secret；不必要 PII。
  > 89. 对象 Key 安全规则由 DQ-17 决定。
  > 90. 对象存储 Versioning、Object Lock 和 Legal Hold 是否启用留待 DQ-15、DQ-17 和部署设计。
  >
  > **3.9 PostgreSQL 与对象存储一致性协议**
  >
  > 91. 项目不假设 PostgreSQL 与对象存储之间存在统一分布式 ACID 事务。
  > 92. 不采用 XA 或其他分布式事务作为 MVP 默认方案。
  > 93. 外部内容采用以下协议：
  >
  >    ```text
  >    PREPARE CONTENT
  >    → UPLOAD IMMUTABLE OBJECT
  >    → VERIFY CHECKSUM / PRESENCE
  >    → FINALIZE METADATA IN SHORT POSTGRESQL TRANSACTION
  >    ```
  >
  > 94. Prepare Content 阶段发生在数据库事务之外。
  > 95. Prepare 阶段至少包括：获取或生成内容；计算 Content Hash；计算 Byte Length；确定 Media Type；确定 Storage Classification；生成不可变 Object Key。
  > 96. Upload 阶段必须使用条件创建或等价不可覆盖语义。
  > 97. Upload 完成后必须通过服务端 Checksum、HEAD、Metadata 或等价方式验证对象存在和完整性。
  > 98. 只有验证成功的 Object 才能进入 PostgreSQL Finalization。
  > 99. Finalization 使用一个短 PostgreSQL 事务。
  > 100. Finalization 可以包含：ContentObject Metadata；SourceVersion；Acquisition Success；Provenance；DerivedArtifact；Fragment；Source Current Pointer CAS，如适用；Audit；Idempotency Result；Integration Event Outbox；Durable Work Intent。
  > 101. PostgreSQL 不得提交指向未验证 Object 的正式 SourceVersion。
  > 102. 不得先提交 Active SourceVersion，再异步尝试上传其 Object。
  > 103. PostgreSQL Commit 成功后，SourceVersion 才成为正式可引用记录。
  > 104. PostgreSQL Finalization 失败时，不得产生正式 Business Current Truth、EvidenceLink 或 SourceVersion。
  >
  > **3.10 Orphan Object**
  >
  > 105. Object Upload 成功但 PostgreSQL Commit 失败时，只产生未引用 Orphan Object。
  > 106. Orphan Object 不等于正式 ContentObject 业务记录。
  > 107. Orphan Object 不得自动成为 SourceVersion。
  > 108. Orphan Object 必须能够通过 Reconciliation 发现。
  > 109. Reconciler 只能在满足 Grace Period 和引用检查后处理 Orphan。
  > 110. Orphan Grace Period、Archive 和 Physical Deletion 由 DQ-15 决定。
  > 111. Reconciler 不得删除仍被任何正式 SourceVersion、DerivedArtifact、EvidenceLink、Legal Hold 或 Audit Requirement 引用的 Object。
  > 112. Orphan Cleanup 不得依据单次最终一致性读取结果立即删除对象。
  > 113. Orphan Reconciliation 必须记录可审计结果。
  >
  > **3.11 Missing 或 Corrupt Object**
  >
  > 114. PostgreSQL 已正式引用的 Object 后续缺失或 Checksum 不匹配时，必须视为 Integrity Incident。
  > 115. Integrity Incident 不得被静默忽略。
  > 116. 系统不得静默：重新抓取同一 URL 的最新内容并替换；切换到其他 SourceVersion；切换到其他 Hash；修改历史 SourceVersion；修改历史 EvidenceLink；将损坏对象继续标记为有效。
  > 117. Integrity Incident 必须至少导致：Availability/Integrity State 更新；Audit 或 Incident Record；告警；依赖分析；必要的 Claim/Evidence Review。
  > 118. 受影响的 Business Version 不得自动改绑到新 SourceVersion。
  > 119. 是否需要 Invalidate、Needs Review、Restore 或 Replacement，由对应业务不变量决定。
  > 120. Missing/Corrupt Object 的恢复与运营流程继续由 RFC-007、DQ-15 和 DQ-17 决定。
  >
  > **3.12 Acquisition**
  >
  > 121. Acquisition Attempt 与 SourceVersion 必须保持独立。
  > 122. Acquisition 至少应表达：Acquisition ID；Source Identity；Acquisition Method；Connector/Fetcher Identity；Connector Version；Actor/Agent；Requested Locator；Resolved Locator；Started Time；Completed Time；Upstream Observed Time；Result Classification；HTTP/Provider Metadata 的允许子集；Produced Content Hash，如成功；Error Classification，如失败；Correlation/Causation Identity。
  > 123. 失败 Acquisition 可以保留运行或 Audit 证据。
  > 124. 失败 Acquisition 不得创建正式 SourceVersion。
  > 125. Retry Acquisition 必须遵守 DQ-08 幂等身份模型。
  > 126. 相同字节的重复获取可以复用 ContentObject。
  > 127. 复用 ContentObject 不得删除 Acquisition 差异。
  > 128. Acquisition 是否产生新 SourceVersion，必须由 Application Policy 根据 Provenance、时间和业务语义决定。
  >
  > **3.13 Provenance**
  >
  > 129. Provenance 至少必须表达：
  >
  >    ```text
  >    Entity:
  >    SourceVersion / ContentObject / DerivedArtifact
  >
  >    Activity:
  >    Fetch / Upload / Parse / Normalize / OCR / Extract / Chunk
  >
  >    Agent:
  >    User / Connector / Crawler / Provider / Software Version
  >    ```
  >
  > 130. Provenance 至少应记录：`derived_from`；generated-by activity；used entities；responsible actor/agent；processor identity；processor version；model/config/profile version；acquisition method；original locator；resolved locator；occurred time；recorded time；Content Hash；Correlation/Causation Identity。
  > 131. 项目不要求实现通用 Provenance Graph Database。
  > 132. 核心 Provenance 身份、外键、状态和约束必须使用类型化字段表达。
  > 133. Provider-specific 扩展 Metadata 可以使用 Versioned JSONB。
  > 134. JSONB 扩展不得替代核心外键、身份、状态或约束。
  > 135. Provenance 记录不得包含未脱敏 Secret 或不必要 PII。
  >
  > **3.14 Fragment**
  >
  > 136. Fragment 必须属于明确的：SourceVersion；或 DerivedArtifact Version。
  > 137. Fragment 不得只属于可变 Source。
  > 138. Fragment 至少应表达：Fragment ID；SourceVersion ID；DerivedArtifact ID，如适用；FragmentSet ID；Segmentation/Profile Version；Ordinal；Locator/Selector；Offset Unit；Start/End；Page/Section/DOM Selector/Timecode，如适用；Fragment Text 或 Immutable Reference；Fragment Hash；Parser/Extractor Version；Created Time；Schema Version。
  > 139. Offset Unit 必须显式。
  > 140. 允许的 Offset Unit 示例包括：UTF-8 Byte Offset；Unicode Code Point；PDF Page Coordinate；Audio/Video Timecode；DOM Selector；Section/Paragraph Selector。
  > 141. 不得只保存无法解释的 `start=100`、`end=200`。
  > 142. Parser、OCR、Chunking 或 Segmentation Profile 变化时，必须创建新的 FragmentSet。
  > 143. 新 FragmentSet 不得覆盖旧 Fragment。
  > 144. Fragment 读取必须能够回到其 SourceVersion 或 DerivedArtifact 的不可变内容。
  > 145. Fragment Hash 必须与其 Canonical Content Definition 对应。
  >
  > **3.15 Canonical Fragment 与 RetrievalChunk**
  >
  > 146. Canonical Fragment 是 Evidence 可稳定引用的内容单位。
  > 147. RetrievalChunk 是检索系统为搜索性能和召回效果生成的派生单位。
  > 148. EvidenceLink 默认引用 SourceVersion + Canonical Fragment 或 Typed Selector。
  > 149. RetrievalIndexEntry 默认引用 RetrievalChunk。
  > 150. RetrievalChunk 必须能够回链到 Canonical Fragment、SourceVersion 或 DerivedArtifact。
  > 151. 重新 Chunk、重新 Embedding 或更换 Vector Store 不得破坏既有 EvidenceLink。
  > 152. EvidenceLink 不得只引用 Vector ID。
  > 153. RetrievalChunk 的生命周期不得隐式控制 SourceVersion 或 EvidenceLink 的生命周期。
  >
  > **3.16 EvidenceLink**
  >
  > 154. EvidenceLink 是显式的业务关系。
  > 155. EvidenceLink 至少应表达：EvidenceLink ID；Target Claim、Business Version 或 Decision Identity；SourceVersion ID；Fragment ID 或 Typed Selector；Relation Type；Exact Excerpt 或 Excerpt Hash，如适用；Created Command ID；Created Actor；Created Time；Rationale 或 Rationale Reference；Evidence Status；Schema Version。
  > 156. Relation Type 可以表达：SUPPORTS；CONTRADICTS；QUALIFIES；CONTEXT；PRIMARY_SOURCE；DERIVED_FROM。
  > 157. 精确 Relation Type Enum 留待业务模型设计。
  > 158. EvidenceLink 必须指向不可变 SourceVersion。
  > 159. EvidenceLink 不得指向：Source Current Pointer；URL 最新内容；Pending SourceVersion；Failed Acquisition；未验证 ContentObject；Missing/Corrupt Object，除非状态明确表达不可用；只有 Vector ID 的 Retrieval Entry。
  > 160. EvidenceLink 不得因 Source Current Pointer 变化而改变历史含义。
  > 161. EvidenceLink 的创建、Invalidation 和 Supersession 必须可审计。
  >
  > **3.17 Evidence Atomicity**
  >
  > 162. 当正式 Business Version 的业务有效性依赖 Evidence 时，以下适用参与者必须处于同一个 DEC-035 PostgreSQL Atomic Business Commit：Business Version；Evidence Links；Current Truth Pointer；Stage State；Audit Record；State Transition Record；Idempotency Result；Integration Event Outbox；Durable Work Intent；Result Reference。
  > 163. 外部 Blob 必须在最终 PostgreSQL 事务开始前准备并验证完成。
  > 164. 最终 Commit 只能引用已正式存在并验证可用的：ContentObject；SourceVersion；DerivedArtifact；Fragment。
  > 165. EvidenceLink 写入失败时，依赖该 Evidence 的 Business Commit 必须整体回滚。
  > 166. Business Commit 回滚时，不得留下已生效 EvidenceLink 或 Current Truth。
  > 167. CAS 冲突不得留下孤立 EvidenceLink。
  > 168. Database Retry 不得重新上传已经成功验证的相同 Blob。
  > 169. Database Retry 必须复用同一逻辑 Command 与 Content Identity。
  >
  > **3.18 Evidence Invalidation**
  >
  > 170. SourceVersion、ContentObject、DerivedArtifact 或 Fragment 后续被判定为以下状态时，不得改写历史 EvidenceLink：Corrupt；Unavailable；Retracted；Superseded；Unsafe；Legally Restricted；Integrity Failed。
  > 171. 应通过新的状态、Invalidation Record、Audit、State Transition 或 Review Workflow 表达变化。
  > 172. 历史 EvidenceLink 不得被静默改绑到 Source 的最新版本。
  > 173. 依赖该 Evidence 的 Business Version 不得被静默改写。
  > 174. 是否导致：Claim Invalid；Needs Review；Current Truth Invalidation；Replacement；Restore；仍可保留历史展示；由相应业务不变量决定。
  > 175. Invalidation Does Not Mean Deletion 继续有效。
  >
  > **3.19 Retrieval Index**
  >
  > 176. Retrieval Index 属于 RFC-005。
  > 177. RFC-005 拥有：Chunking Strategy；Embedding；Vector Store；Retrieval Index；Ranking；Search Runtime；Reindex/Rebuild Strategy。
  > 178. RFC-005 不得重新定义 Source、SourceVersion、Fragment 或 EvidenceLink 的权威身份。
  > 179. Retrieval Index 是派生、可重建、非权威存储。
  > 180. Index Entry 至少必须回链到：SourceVersion ID；Fragment ID 或 DerivedArtifact ID；Index Generation；Chunking Profile Version；Embedding Model/Version，如适用；Input Content Hash。
  > 181. Embedding、Vector ID、Ranking Score 和 Search Result 不等于 Evidence。
  > 182. 正式 Evidence Commit 前，必须解析回 PostgreSQL 中的 SourceVersion、Fragment 或 Typed Selector。
  > 183. 正式 Commit 前必须验证：Identity；Content Hash；Availability；Integrity；Evidence Policy；Business Invariants。
  > 184. Retrieval Index 延迟、损坏、丢失、删除或重建不得改变 Business Current Truth。
  > 185. Retrieval Index 变化不得改变既有 EvidenceLink 的历史含义。
  > 186. Index 可以被重新生成，而无需修改 SourceVersion 或 Business Version。
  >
  > **3.20 Deduplication**
  >
  > 187. ContentObject 可以按项目 Content Hash 物理去重。
  > 188. 物理去重不得合并：Source Identity；SourceVersion Identity；Acquisition；Provenance；Access Control；EvidenceLink；Retention Policy；Legal Hold；Security Classification。
  > 189. 跨 Tenant 或跨 Security Domain 的物理去重在 DQ-17 决定前不得启用。
  > 190. 同一 Security Domain 内的去重仍必须遵守权限和引用计数/引用追踪规则。
  > 191. 物理去重不得造成跨权限域的内容存在性泄露。
  >
  > **3.21 Retention 与删除**
  >
  > 192. Retention、Archive、Cold Storage、Legal Hold、Physical Deletion 和 Orphan Grace Period 由 DQ-15 决定。
  > 193. 只要仍存在必须保留的以下引用，就不得物理删除对应 ContentObject：Business Version；EvidenceLink；Audit Requirement；Legal Hold；Active SourceVersion；Required DerivedArtifact。
  > 194. 正常 Invalidation、Retraction 或 Supersession 不等于物理删除。
  > 195. 如果法规要求删除原始内容，应保留依法允许保留的：Tombstone；Deletion Proof；Hash 或受限完整性信息；受影响引用状态；Audit Evidence。
  > 196. 数据库引用不得因物理删除而静默变成无法解释的悬空引用。
  > 197. 具体删除例外由 DQ-15 和 DQ-17 决定。
  >
  > **3.22 安全边界**
  >
  > 198. Encryption、Redaction、Secret、PII、Access Control、Object Key Security 和跨域去重由 DQ-17 决定。
  > 199. 在 DQ-17 决定前不得：将 Secret 写入对象 Key；在日志中输出 Presigned URL；启用跨 Tenant 去重；依据 Hash 暴露内容存在性；无限制复制敏感原始载荷。
  > 200. Source/Evidence Metadata 和 ContentObject 必须能够分别应用安全策略。
  > 201. 对象存储访问权限不得通过公开 URL 作为默认长期授权模型。
  > 202. Presigned URL 等具体访问协议留给 RFC-004、DQ-17 或实现设计。
  >
  > **3.23 所有权边界**
  >
  > 203. Source/Evidence Capability 是以下持久化资产的唯一所有者：Source；SourceVersion；Acquisition；ContentObject Metadata；DerivedArtifact；Fragment；FragmentSet；EvidenceLink；Object Storage Adapter；Integrity Reconciliation。
  > 204. 业务模块不得直接访问 Source/Evidence ORM、表、Repository 或 Object Key。
  > 205. 业务模块不得直接通过对象存储 SDK 绕过 Source/Evidence Capability。
  > 206. 跨模块操作必须通过类型化 Application Port 或 Public Application Contract。
  > 207. Source/Evidence Capability 负责权威身份、完整性和引用验证。
  > 208. RFC-005 负责 Retrieval，但不拥有 Source/Evidence 权威业务身份。
  > 209. Infrastructure 负责 PostgreSQL 和 Object Storage 的技术实现，不拥有业务语义决定。
  >
  > **3.24 Readiness Artifact**
  >
  > 210. 在 Source/Evidence 持久化实现授权前，Architecture Readiness Package 必须包含：
  >
  >    ```text
  >    Source & Evidence Storage Classification Table
  >    ```
  >
  > 211. Classification Table 至少包含：Content Class；Media Type；Authoritative Identity；Inline/External；Size/Streaming Policy；Canonical Byte Definition；Hash Algorithm；Compression；Storage Key Strategy；Provenance Requirements；Parser/Normalizer；Fragment Strategy；Evidence Eligibility；Retrieval Index Mapping；Retention Owner；Security Classification；Failure Recovery；Related DQ/DEC/RFC。
  > 212. DQ-12 接受不授权创建该 Classification Table。
  > 213. Source & Evidence Storage Classification Table Creation = NOT AUTHORIZED。
  > 214. DQ-12 不新增独立 Matrix。
  > 215. 已要求的 Aggregate/Invariant、Idempotency 和其他 Readiness Artifacts 继续保持原授权状态。
  >
  > **3.25 External Object Consistency Technical Spike**
  >
  > 216. DQ-12 决策归档前不要求执行 Technical Spike。
  > 217. 在启用任何外部对象存储生产或正式持久化实现前，必须完成单独授权的：
  >
  >    ```text
  >    External Object Consistency Technical Spike
  >    ```
  >
  > 218. 该 Spike 与 PostgreSQL Concurrency Technical Spike 是不同的验证对象。
  > 219. PostgreSQL Concurrency Spike 不能证明对象存储 Provider 的：Conditional Write；Multipart Checksum；Read-after-write；Object Metadata；Crash Window；Orphan Reconciliation。
  > 220. External Object Consistency Spike 最低验证：Conditional Put / Put-if-absent；同 Hash 并发上传；同 Key 不同字节冲突；Provider Checksum；Multipart Upload Checksum；Upload 成功、DB Commit 失败产生可回收 Orphan；DB Commit 不引用未验证 Object；Missing Object 检测；Corrupt Object 检测；Retry 不重复创建 SourceVersion；Reconciler 不删除仍被引用 Object；真实目标 Provider 的 Read-after-write；无部分 Business Current Truth 写入。
  > 221. Spike 必须针对未来实际选定的 Provider 和配置执行。
  > 222. 本次接受不选择具体对象存储 Provider。
  > 223. 本次接受不授权创建 Spike Issue、Branch、PR、代码、测试、Bucket、账号或基础设施。
  > 224. External Object Consistency Technical Spike = REQUIRED / NOT AUTHORIZED。
  >
  > **3.26 测试前置语义**
  >
  > 225. 所有正式 PostgreSQL 事务语义测试必须使用真实 PostgreSQL。
  > 226. 外部对象一致性测试必须使用真实目标 Object Storage Provider 或与生产语义一致的正式测试环境。
  > 227. 后续测试至少覆盖：Source 与 SourceVersion 身份分离；同 Source 新内容创建新 SourceVersion；同字节可以复用 ContentObject；物理去重不合并 Provenance；Raw Content 不可变；DerivedArtifact 升级不覆盖旧版本；Raw Hash 与 Normalized Hash 分离；ETag 不作为权威 Content Hash；Fragment 固定到 SourceVersion；Offset Unit 可解释；EvidenceLink 不指向 Source Current Pointer；EvidenceLink 不只引用 Vector ID；Evidence 与 Business Version 同事务；Commit 失败无生效 EvidenceLink；Upload 成功、DB 失败只产生 Orphan；DB 不引用未验证 Object；Missing/Corrupt Object 不静默替换；Retrieval Index 重建不改变 Evidence；Rechunk/Re-embedding 不破坏历史 EvidenceLink；跨 Security Domain 去重在未授权时被阻止；Reconciler 不删除仍有引用的 Object；无部分 Business Current Truth 写入。
  > 228. 测试分类与 CI 策略继续由 DQ-16 决定。

---

## DQ-13：Workflow Checkpoint Separation（工作流检查点分离）

- **Question：** Checkpointer 与业务库同服务/同库/同 Schema？checkpoint 生命周期与删除策略？Business State 与 Graph State 对账的持久化权威？
- **Why：** DEC-023/024 恒定「Checkpoint 仅恢复、≠Current Truth」；须把逻辑分离落地为物理/库边界，并定对账权威。
- **Constraints（[DEC 约束]）：** DEC-024 Checkpoint 不作为业务查询权威来源；DEC-033 Checkpoint Reconciliation（旧业务版本→checkpoint 标 stale、让步业务真值、不覆盖较新业务状态）。
- **[官方能力]：** 生产推荐 PostgresSaver（4 张专用表 + setup()、无扩展依赖）；**官方对「Checkpointer 与业务库同库/分库」无建议**（真实决策空间）；checkpoint_id 单调可排序；`delete_thread` 可用、当前钉版 `prune` 不可用、无内建 TTL（官方建议应用层 cron）；durability=sync/async/exit；**OSS 无同一 thread_id 并发防护**。
- **[架构推断]：** 因 Business DB 才是 Current Truth，checkpoint 可视为可回收执行副产物，激进清理在架构上安全。
- **Candidates：**
  - **A. 同 PG 实例、独立 schema/表（逻辑分离）**：运维最简、满足 DEC 逻辑分离。
  - **B. 完全独立物理库**：隔离最强、运维更重。
  - **C. 同表混存**：违反 DEC，禁止。
- **Trade-offs：** A 满足「逻辑分离恒定」且运维简单（DEC 允许同实例保持逻辑边界）；B 隔离强但超 MVP 需求；C 违规。
- **Failure modes：** 混存→checkpoint 被误作业务真值；无清理策略→checkpoint 无限膨胀；对账权威倒置→旧 checkpoint 覆盖新业务版本。
- **Impact on later RFCs：** RFC-003（生产 Checkpointer 选型、durability、serde、并发防护——**本 DQ 不决定**）。
- **Recommendation：** **[架构推断] 倾向 A**——同实例独立 schema/表、逻辑分离；checkpoint 保留/清理由应用层实现（cron），对账以 Business Current Truth 为权威、checkpoint 让步。**置信度：高**。（**历史提案；Superseded by the Accepted Major Revision below。**）
- **Candidate 处置（2026-08-02 用户正式决定）：** Candidate A = **ACCEPTED WITH MAJOR REVISION**（Formal Model = Shared PostgreSQL Service + Isolated Checkpoint Persistence Plane + Dedicated Role/Connection Pool/Storage Namespace + Application-owned Workflow Execution Registry + Business-Current-Truth-first Reconciliation）；Candidate B = **NOT SELECTED AS AN INDEPENDENT POSTGRESQL SERVICE OR SEPARATE INFRASTRUCTURE FOR MVP**（同一 PostgreSQL Service 内独立 Checkpoint Database 是 Candidate A 的安全 Fallback，不等于 Candidate B）；Candidate C = **REJECTED**（Business 与 Checkpoint Record 不得同表混存）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-02 用户正式决定）：**

  > **3.1 正式模式**
  >
  > 1. MVP 采用：
  >
  >    ```text
  >    SHARED POSTGRESQL SERVICE
  >    + ISOLATED CHECKPOINT PERSISTENCE PLANE
  >    + DEDICATED ROLE / CONNECTION POOL / STORAGE NAMESPACE
  >    + APPLICATION-OWNED WORKFLOW EXECUTION REGISTRY
  >    + BUSINESS-CURRENT-TRUTH-FIRST RECONCILIATION
  >    ```
  >
  > 2. Candidate A 被接受并进行重大修订。
  > 3. Candidate B 不作为 MVP 默认方向。
  > 4. Candidate B 被拒绝的是：Independent PostgreSQL Service or Separate Checkpoint Infrastructure。
  > 5. 同一 PostgreSQL Service 内使用独立 Checkpoint Database，是 Candidate A 的安全 Fallback，不等于 Candidate B。
  > 6. Candidate C 同表混存被拒绝。
  > 7. Business Record 与 Vendor Checkpoint Record 不得存入同一业务表。
  > 8. Checkpoint 不得作为 Business Current Truth。
  >
  > **3.2 三个持久化平面**
  >
  > 9. 必须区分：Business Persistence Plane；Application-owned Workflow Execution Registry；Vendor Checkpoint Persistence Plane。
  > 10. 三个平面不得通过一个通用 Workflow 表、通用 State JSON 或 ORM Model 合并。
  > 11. Business Persistence Plane 保存正式业务权威状态。
  > 12. Business Persistence Plane 包括所有适用的：Business Current Truth；Immutable Business Version；Current Truth Pointer；Audit；State Transition；Evidence；Idempotency；Durable Work Intent；Integration Event Outbox；其他 DEC-035 参与者。
  > 13. Workflow Execution Registry 是项目自有 Runtime/Application 记录。
  > 14. Workflow Execution Registry 不等于 Business Current Truth。
  > 15. Workflow Execution Registry 是项目层面对 Workflow Run 与 Framework Thread 映射的权威来源。
  > 16. Vendor Checkpoint Persistence Plane 由 LangGraph Checkpointer 管理。
  > 17. Vendor Checkpoint Tables 只保存 Graph 恢复所需的状态、Blob、Pending Writes 与 Vendor Migration Metadata。
  > 18. Business Module 不得直接查询或修改 Vendor Checkpoint Tables。
  > 19. Vendor Checkpoint Tables 不得被 Business Repository 当作业务查询来源。
  >
  > **3.3 物理放置**
  >
  > 20. PostgreSQL Service 与 Business Persistence 共享。
  > 21. Checkpoint Persistence Plane 必须具有独立 Storage Namespace。
  > 22. 优先物理形态为：
  >
  >    ```text
  >    Same PostgreSQL Service
  >    + Same PostgreSQL Database
  >    + Dedicated Checkpoint Schema
  >    ```
  >
  > 23. 该优先形态只有在实际钉定的 Python PostgresSaver、Psycopg Pool 和部署 Pooler 被证明能够稳定解析到专用 Schema 时才能采用。
  > 24. 不得仅凭文档推测或开发环境偶然成功，声称 Schema Isolation 已成立。
  > 25. 必须证明：Setup DDL 落入预期 Schema；Runtime Put 落入预期 Schema；Runtime Get 落入预期 Schema；Runtime List 落入预期 Schema；Runtime Delete 落入预期 Schema；Pool Connection Reuse 后 `search_path` 不漂移；Worker 并发下 Namespace 不漂移；Pooler Transaction/Session Mode 不破坏 Schema Resolution。
  > 26. 如果无法稳定保证 Schema Resolution，则使用：
  >
  >    ```text
  >    Same PostgreSQL Service
  >    + Dedicated Checkpoint Database
  >    ```
  >
  > 27. Fallback Database 必须与 Business Database 保持独立 Credentials、Pool 和 Migration Lifecycle。
  > 28. DQ-13 不选择具体 Pooler。
  > 29. DQ-13 不授权创建 Database 或 Schema。
  >
  > **3.4 Role 和 Connection Pool**
  >
  > 30. 必须使用独立的 Business Connection Pool 与 Checkpoint Connection Pool。
  > 31. Business Pool 不得被 PostgresSaver 使用。
  > 32. Checkpoint Pool 不得被 Business Repository 使用。
  > 33. Checkpoint Connection 不得进入 Application UnitOfWork。
  > 34. Checkpoint Pool 必须只连接被授权的 Checkpoint Database 或 Schema。
  > 35. Checkpoint Pool 必须使用独立 Role。
  > 36. Checkpoint Role 采用最小权限。
  > 37. Checkpoint Role 不应拥有：Business Schema DDL；Business Table UPDATE；Business Table DELETE；Business Migration Owner；Audit Ledger 修改；Source/Evidence 业务表写入；Current Truth 修改。
  > 38. Business Role 不应直接修改 Vendor Checkpoint Tables。
  > 39. Migration Role 与 Runtime Checkpoint Role 可以分离。
  > 40. Checkpoint Pool 必须拥有独立：Pool Size；Connection Timeout；Health Check；Retry Policy；Observability；Credential Rotation。
  > 41. Worker 长时间执行期间不得持有 Business Session 或 Business UoW。
  > 42. Checkpointer 自身的短数据库操作不得被包装进业务 UoW。
  >
  > **3.5 Workflow Execution Registry**
  >
  > 43. 项目必须拥有 Workflow Execution Registry 的明确 Application Contract。
  > 44. Workflow Execution Registry 至少应表达：`workflow_run_id`；`thread_id`；`checkpoint_namespace`；`command_id`；`stage_run_id`；Target Business Type；Target Business Identity；Base Domain Version；Expected Revision；Input Fingerprint；Runtime Lifecycle；Reconciliation Status；Graph Definition Version；Checkpoint Schema Version；Serializer Version；Stale/Superseded Reason；Created/Updated Time；Retention Eligibility；Related Dispatch ID，如适用；Current Attempt ID，如适用。
  > 45. `workflow_run_id` 是项目自有的一次逻辑 Workflow Execution Identity。
  > 46. `thread_id` 是 Framework Checkpoint Identity。
  > 47. 一个 Workflow Run 必须显式映射到其 Thread。
  > 48. 该映射不得通过解析 `thread_id` 字符串推断。
  > 49. Registry 不得保存 SQLAlchemy Session、Repository 或 Vendor Connection。
  > 50. Registry 的精确表结构留待实现设计。
  >
  > **3.6 身份分离**
  >
  > 51. 以下身份必须保持分离：`workflow_run_id`；`thread_id`；`checkpoint_id`；`checkpoint_namespace`；`command_id`；`stage_run_id`；`attempt_id`；`dispatch_id`；`domain_version_id`；Idempotency Key；Provider Call Identity。
  > 52. `thread_id` 不得作为 Command ID。
  > 53. `thread_id` 不得作为 Stage Run ID。
  > 54. `thread_id` 不得作为 Idempotency Key。
  > 55. `thread_id` 不得作为 Lease Identity。
  > 56. `checkpoint_id` 不得作为 Domain Version ID。
  > 57. `checkpoint_id` 不得作为业务成功证明。
  > 58. Checkpoint 存在不表示 Business Commit 成功。
  > 59. Checkpoint 缺失不表示 Business Commit 未发生。
  > 60. Attempt Identity 不得替代 Workflow Run Identity。
  > 61. Intentional Rerun 必须创建新的 Workflow Run Identity 和 Thread Identity。
  >
  > **3.7 Checkpoint 权威边界**
  >
  > 62. Checkpoint 是 Runtime Recovery State。
  > 63. Checkpoint 不是：Business Current Truth；Business Version；Audit Record；State Transition Record；Idempotency Record；Durable Work Intent；Integration Event；EvidenceLink；Review Decision；Provider Call Ledger；执行所有权锁。
  > 64. Checkpoint 中复制的业务字段仅为恢复上下文。
  > 65. Checkpoint 中的业务字段不得覆盖 PostgreSQL Business Current Truth。
  > 66. Checkpoint 不得回答以下权威业务问题：当前正式版本；当前 Review Decision；当前 Evidence 状态；当前 Work Intent 状态；当前 Provider Side-effect 状态；当前 Idempotency Result；Current Truth Pointer；正式业务结果。
  > 67. Business Current Truth 发生变化时，Checkpoint 必须让步。
  >
  > **3.8 Payload 边界**
  >
  > 68. Checkpoint Payload 只保存恢复 Graph Execution 所需的最小 Runtime State。
  > 69. 允许保存的内容包括：Workflow Run Identity；Command Reference；Stage Run Reference；Base Domain Version；Expected Revision；Input Fingerprint；Node Cursor；Interrupt Payload；Tool/Node Result Reference；Pending Runtime Writes；Graph Definition Version；Checkpoint Schema Version；Reconciliation Metadata；Runtime-only Channel Values。
  > 70. Checkpoint Payload 不得保存：SQLAlchemy Session；UnitOfWork；Repository；ORM Entity；Database Connection；Coroutine；Generator；未脱敏 Secret；长期 Provider Token；长期 Presigned URL；不必要的完整 PII；数据库整行无选择复制；不受控制的任意 Python Object。
  > 71. Provider 响应如需恢复，应保存受控 Result Snapshot 或不可变 Result Reference。
  > 72. 大型内容应通过稳定 Reference 引用，不得无界复制进入 Checkpoint。
  > 73. Checkpoint State 不得替代 DQ-12 Source/Evidence 持久化。
  >
  > **3.9 Serializer 与安全**
  >
  > 74. Checkpoint Serializer 必须使用明确 Allowlist。
  > 75. 不得允许任意 Python Class 反序列化。
  > 76. Checkpoint 被视为不完全可信的持久化输入。
  > 77. Resume 前必须验证：Serializer Version；Payload Schema；Graph Definition Compatibility；必要 Integrity Metadata。
  > 78. 不兼容 Payload 必须分类为 INCOMPATIBLE，而不是尝试不安全恢复。
  > 79. 无法安全反序列化的 Payload 必须分类为 CORRUPT 或 INCOMPATIBLE。
  > 80. Encryption、Redaction、Secret、PII 与访问控制由 DQ-17 决定。
  > 81. 在 DQ-17 决定前，不得假设所有 Checkpoint Payload 可以明文长期保存。
  > 82. Runtime Log 不得输出完整 Checkpoint Payload、Secret 或长期访问 URL。
  >
  > **3.10 Business Commit 与 Checkpoint Write**
  >
  > 83. Business Commit 与 Checkpoint Write 不构成同一 Atomic Transaction。
  > 84. 即使位于同一 PostgreSQL Service，也不得声称两者属于同一个 Application UoW。
  > 85. Vendor Checkpoint Connection 不属于 DEC-035 Atomic Business Commit。
  > 86. 必须处理以下 Crash Window：
  >    - **A. Checkpoint 成功、Business Commit 未发生：**
  >
  > 87. Checkpoint 只表示 Graph 到达某个 Runtime 位置。
  > 88. Resume 时必须重新验证 Business Current Truth。
  > 89. 不得根据 Checkpoint 推断业务已提交。
  >
  >    - **B. Checkpoint 成功、Business Commit 回滚：**
  >
  > 90. Checkpoint 不得解释为成功 Business Result。
  > 91. Runtime 必须通过 Reconciliation 识别业务未提交。
  >
  >    - **C. Business Commit 成功、Checkpoint Write 失败：**
  >
  > 92. Business Commit 仍然有效。
  > 93. 后续 Resume 必须通过 DQ-08 Idempotency 和 Business Current Truth 识别已完成操作。
  > 94. 不得重新调用已经成功的 Provider 或重复业务副作用。
  >
  >    - **D. 两者都成功：**
  >
  > 95. 后续 Resume 仍必须执行 Reconciliation。
  > 96. 不得永久假设 Checkpoint 与 Current Truth 始终一致。
  > 97. Checkpoint Durability 与 Business Consistency 是互补机制，不是同一事务。
  >
  > **3.11 Resume Reconciliation**
  >
  > 98. 每次 Resume、Retry、Human Interrupt 恢复或 Time Travel Fork 前必须执行：
  >
  >    ```text
  >    Load Workflow Execution Registry
  >    → Load Checkpoint
  >    → Load Business Current Truth
  >    → Validate Identity and Version
  >    → Classify Reconciliation Result
  >    → Resume or Refuse
  >    ```
  >
  > 99. 至少验证：Workflow Run ID；Thread ID；Command ID；Stage Run ID；Input Fingerprint；Base Domain Version；Current Domain Version；Expected Revision；Current Stage State；Idempotency Result；Lease Holder；Attempt ID；Fencing Token；Graph Definition Version；Checkpoint Schema Version；Serializer Version；Workflow Runtime Status。
  > 100. Reconciliation 至少区分：
  >
  >    ```text
  >    RESUMABLE
  >    ALREADY_COMMITTED
  >    STALE
  >    SUPERSEDED
  >    INVALIDATED
  >    ORPHANED
  >    INCOMPATIBLE
  >    CORRUPT
  >    ```
  >
  > 101. 只有 RESUMABLE 可以继续原 Thread。
  > 102. ALREADY_COMMITTED 表示对应 Business Command 已成功完成。
  > 103. ALREADY_COMMITTED 不得再次执行业务副作用。
  > 104. ALREADY_COMMITTED 应重放业务结果或推进 Runtime Completion。
  > 105. STALE 表示 Business Current Truth 已前进，Checkpoint 基于旧状态。
  > 106. STALE Checkpoint 不得覆盖新 Current Truth。
  > 107. SUPERSEDED 表示 Workflow Run 已被 Intentional Rerun、Replacement 或其他正式操作取代。
  > 108. INVALIDATED 表示其引用的 Business Version、Source、Evidence、Review Decision 或其他依赖失效。
  > 109. ORPHANED 表示存在 Checkpoint，但 Registry、业务对象或合法 Workflow Run 不存在。
  > 110. INCOMPATIBLE 表示 Graph Definition、Serializer、Checkpoint Schema 或 Package Version 无法安全恢复。
  > 111. CORRUPT 表示数据损坏、完整性失败或无法可信读取。
  > 112. 非 RESUMABLE 结果必须停止原 Thread Resume。
  >
  > **3.12 Stale 和 Superseded**
  >
  > 113. STALE 或 SUPERSEDED Checkpoint 不得修改较新的 Business Current Truth。
  > 114. 不得静默修改 Checkpoint 的 Base Domain Version。
  > 115. 不得把 Retry 伪装成 Resume。
  > 116. 不得复用旧 Command Identity 创建新的逻辑业务操作。
  > 117. 允许的处理包括：将 Workflow Run 标记为 STALE；将 Workflow Run 标记为 SUPERSEDED；终止当前 Resume Attempt；保存诊断 Metadata；根据 DQ-15 决定保留或删除 Checkpoint；启动 Intentional Rerun。
  > 118. Intentional Rerun 必须创建新的：Command ID；Stage Run ID；Workflow Run ID；Thread ID；Attempt ID；Dispatch ID，如适用；Provider Call Identity，如适用。
  > 119. Intentional Rerun 必须保留父级和因果关系。
  >
  > **3.13 并发控制**
  >
  > 120. Checkpoint 不承担执行并发控制。
  > 121. 以下内容均不是执行锁：Thread ID；Checkpoint ID；Checkpoint Record；Checkpoint Write Success；Graph State 中的布尔 Flag。
  > 122. 执行所有权继续由 DQ-07 提供：Durable Lease；Lease Holder；Attempt ID；Monotonic Fencing Token。
  > 123. 同一 Workflow Run 或 Thread 的并发 Resume 必须：拒绝第二个执行；或通过 Durable Lease 串行化。
  > 124. 不得依赖 Checkpointer 自动阻止并发 Resume。
  > 125. 最终 Business Commit 必须重新验证 Fencing Token。
  > 126. Lease 过期或 Fencing Token 失效后，旧 Worker 不得提交 Business Result。
  > 127. Checkpoint 写入成功不得恢复旧 Worker 的执行权。
  >
  > **3.14 Durability Mode**
  >
  > 128. Durability Mode 的精确逐节点策略归 RFC-003。
  > 129. `exit` 不得用于：Human-in-the-loop；Awaiting Review；长时间等待；需要故障恢复的生产流程；跨多个节点的正式生产工作流。
  > 130. `async` 只有在以下条件同时满足时才允许：可容忍最近一个恢复点丢失；所有外部副作用受 DQ-08 幂等保护；必须执行的工作由 DQ-09 Durable Work Intent 持久化；Business Commit 可以独立对账；重算成本可接受。
  > 131. `sync` 是以下边界的默认安全方向：Interrupt 前；Human Review 等待前；不可廉价重算步骤后；Provider Side-effect Result 记录后；正式 Business Commit 相关边界；Runtime 释放 Lease 前。
  > 132. `sync` 不等于 Business Commit 与 Checkpoint Atomic。
  > 133. RFC-003 可以在不违反上述最低约束的前提下定义更细粒度策略。
  >
  > **3.15 Time Travel 与 Fork**
  >
  > 134. Graph Time Travel 不等于 Business Restore。
  > 135. 从旧 Checkpoint Fork 不得自动覆盖 Current Truth。
  > 136. Fork 不得自动复用旧业务 Command Identity。
  > 137. Debug Fork 不是正式业务结果。
  > 138. 要将 Fork 结果写入 Business Current Truth，必须转换为 Intentional Rerun。
  > 139. Intentional Rerun 必须创建新业务身份并通过新的 DEC-035 Atomic Business Commit。
  > 140. DQ-11 Business Restore 继续创建新的 Domain Version。
  > 141. Checkpoint Fork 不得替代 Restore Command。
  >
  > **3.16 Setup 与 Vendor Migration**
  >
  > 142. PostgresSaver Setup 属于 Vendor Checkpoint Schema 初始化和迁移。
  > 143. 生产 Worker 启动时不得无条件并发执行 Setup DDL。
  > 144. Setup 应通过：受控部署步骤；Migration Job；或其他单一受控初始化机制。
  > 145. `langgraph-checkpoint-postgres` 版本必须钉定。
  > 146. Vendor Checkpoint Migration 与 Business Alembic Migration 必须分离。
  > 147. Business Alembic 不得管理 Vendor Checkpoint Tables。
  > 148. Runtime Module 不得自行修改 Vendor Table Schema。
  > 149. Package 升级前必须验证：Schema Migration；Existing Checkpoint Compatibility；Resume Compatibility；Serializer Compatibility；Rollout/Rollback Boundary；Setup Idempotency；Pool/Search Path Compatibility。
  > 150. Setup 与 Runtime 必须使用一致的 Storage Namespace、Role 和 Schema Resolution。
  > 151. DQ-14 管理总体 Migration Discipline，但不得把 Vendor Table 纳入普通业务 Migration Ownership。
  >
  > **3.17 Retention 与删除**
  >
  > 152. Checkpoint 是可清理 Runtime Artifact。
  > 153. 可清理不等于任意时间可以删除。
  > 154. Thread 只有在以下条件满足时才可进入删除：Workflow Terminal；无有效 Lease；无 Pending Resume；无 Awaiting Human Input；无 Retry Window；无 Incident Hold；无 Debug Hold；无 Legal Hold；Registry 标记可清理。
  > 155. 不得删除以下状态对应的 Thread：ACTIVE；IN_PROGRESS；INTERRUPTED；AWAITING_REVIEW；FAILED_RETRYABLE；RECONCILING；INCIDENT_INVESTIGATION。
  > 156. 删除 Checkpoint 不得删除或改变：Business Current Truth；Audit；State Transition；Domain Version；Evidence；Work Intent；Integration Event；Idempotency Result；Provider Call Ledger。
  > 157. 默认采用 Whole-thread Lifecycle Deletion。
  > 158. 在没有验证 Package Version、Checkpoint Chain 和 DeltaChannel 完整性的情况下，不得执行部分历史 Pruning。
  > 159. 不得假设任意 PostgresSaver 版本都支持安全 Partial Pruning。
  > 160. Retention Period、Grace Period、Legal Hold 和 Physical Cleanup 由 DQ-15 决定。
  > 161. 删除操作必须可审计。
  >
  > **3.18 所有权边界**
  >
  > 162. Workflow Runtime Capability 拥有：Workflow Execution Registry；Reconciliation Application Contract；Checkpoint Adapter；Runtime Lifecycle；Checkpoint Cleanup Coordination。
  > 163. Vendor Checkpoint Tables 由 Checkpointer Package 的存储协议管理。
  > 164. Business Module 不拥有 Vendor Table。
  > 165. Business Module 不得直接使用 PostgresSaver Repository 或 SQL。
  > 166. Runtime Module 不得直接修改业务 Current Truth，除非通过正式 Business Application Contract。
  > 167. Reconciliation 读取 Business Current Truth 时必须使用业务模块公开的 Query/Application Contract。
  > 168. Cross-module Direct SQL 继续被 DQ-02 禁止。
  > 169. Checkpoint Storage Adapter 属于 Infrastructure。
  > 170. Workflow Identity、Reconciliation Policy 和 Runtime Lifecycle 属于 Application/Runtime 语义。
  >
  > **3.19 Readiness Artifact**
  >
  > 171. 在 Checkpoint 持久化实现授权前，Architecture Readiness Package 必须包含：
  >
  >    ```text
  >    Workflow Checkpoint Boundary & Reconciliation Table
  >    ```
  >
  > 172. 该表至少包含：Workflow Type；Workflow Run Identity；Thread ID Source；Checkpoint Namespace；Business Target；Base Domain Version；Expected Revision；Input Fingerprint；Interrupt Use；Durability Mode；Resume Preconditions；Stale Detection；Reconciliation Outcome；Lease/Fencing Requirement；Serializer Policy；Sensitive Payload Classification；Retention State；Delete Eligibility；Graph Definition Version；Checkpoint Schema Version；Related DQ/DEC/RFC。
  > 173. DQ-13 接受不授权创建该表。
  > 174. Workflow Checkpoint Boundary & Reconciliation Table Creation = NOT AUTHORIZED。
  > 175. DQ-13 不新增独立 Matrix。
  > 176. 现有 Matrix 与 Classification Artifacts 继续保持原授权状态。
  >
  > **3.20 Technical Spike**
  >
  > 177. DQ-13 决策归档前不要求执行 Technical Spike。
  > 178. 在启用正式 Checkpoint 实现前，必须完成单独授权的：
  >
  >    ```text
  >    Workflow Checkpoint Isolation & Reconciliation Technical Spike
  >    ```
  >
  > 179. Spike 必须针对项目实际钉定的 Python PostgresSaver 版本执行。
  > 180. Spike 必须使用实际 Psycopg Pool 与计划部署的 Pooler/Connection Mode。
  > 181. Spike 最低验证：Setup 落入预期 Schema 或 Database；Put/Get/List/Delete 不访问业务 Schema；Dedicated Role 最小权限；Dedicated Pool 的 Schema Resolution 不漂移；Pool Reuse；Pooler Session/Transaction Mode；多 Worker 并发 Setup；Setup Idempotency；同一 Thread 并发 Resume；Lease/Fencing 阻止旧 Worker；Checkpoint 成功、Business Commit 失败；Business Commit 成功、Checkpoint 失败；STALE 不覆盖 Current Truth；ALREADY_COMMITTED 不重复副作用；INCOMPATIBLE Graph Version；Strict Serializer；Corrupt Payload；Whole-thread Cleanup；无 Business Partial Write。
  > 182. 如果 Dedicated Schema 方案验证失败，Spike 必须验证同 Service Dedicated Database Fallback。
  > 183. Spike 可以与 PostgreSQL Concurrency Spike 共享基础设施，但验收目标和报告必须独立。
  > 184. 本次接受不授权创建 Spike Issue、Branch、PR、代码、测试、Role、Database、Schema、Pool 或基础设施。
  > 185. Workflow Checkpoint Isolation & Reconciliation Technical Spike = REQUIRED / NOT AUTHORIZED。
  >
  > **3.21 测试前置语义**
  >
  > 186. 正式 Checkpoint 数据库语义测试必须使用真实 PostgreSQL。
  > 187. 后续测试至少覆盖：Business、Registry 和 Vendor Checkpoint 三平面分离；Business Pool 与 Checkpoint Pool 分离；Business Role 不能写 Vendor Table；Checkpoint Role 不能写 Business Table；Thread ID 不作为业务身份；Checkpoint 成功、Business Commit 失败；Business Commit 成功、Checkpoint 失败；ALREADY_COMMITTED 不重复副作用；STALE 不覆盖新 Current Truth；SUPERSEDED 不继续旧 Thread；INVALIDATED 停止 Resume；ORPHANED 不自动恢复；INCOMPATIBLE 不进行不安全反序列化；CORRUPT 不被当作业务成功；并发 Resume 被 Lease/Fencing 阻止；Time Travel Fork 不等于 Business Restore；Intentional Rerun 创建新身份；Setup 不由所有 Worker 并发执行；Vendor Migration 与 Business Migration 分离；Whole-thread Delete 不影响 Business Data；Partial Pruning 在未验证时被禁止；无部分 Business Write。
  > 188. 详细测试分类与 CI 策略继续由 DQ-16 决定。

---

## DQ-14：Schema Evolution & Migrations（模式演进与迁移）

- **Question：** 迁移工具与纪律（ownership、forward-only vs downgrade、autogenerate 纪律、滚动升级兼容、backfill、destructive gate、schema version）？
- **Why：** RFC-002 Acceptance Criteria 含 Migration/Rollback；须建立安全的 schema 演进纪律但**不创建真实迁移**。
- **Constraints（[DEC 约束]）：** 不在本 RFC 创建真实迁移脚本；DEC-024 版本化语义。
- **[官方能力]：** Alembic autogenerate **必须人工 review**（改名误判 add/drop）；forward-only 是项目策略非强制；batch mode（SQLite move-copy）；offline SQL；PG 快速加列 + `CREATE INDEX CONCURRENTLY` + `NOT VALID`+`VALIDATE` 两段式（expand-contract 落点）；DDL 事务性（除 CONCURRENTLY）。
- **Candidates：**
  - **A. Alembic + forward-only + autogenerate 必经人工 review + expand-contract 滚动兼容**。
  - **B. Alembic + 支持 downgrade**：回退能力强但含数据迁移的 downgrade 常无法无损。
  - **C. 手写 SQL 迁移**：可控但失去 autogenerate 辅助。
- **Trade-offs：** A 安全且契合滚动升级；B 灵活但 downgrade 不可靠；C 最可控但维护重。
- **Failure modes：** autogenerate 未人工 review→改名误判；破坏性变更无 gate→数据丢失；在线低锁操作（CONCURRENTLY）混入事务→失去原子性。
- **Impact on later RFCs：** 全部（schema 是所有模块基础）。
- **Recommendation：** **[架构推断] 倾向 A**——forward-only、autogenerate 必经人工 review、破坏性变更显式 gate、滚动升级用 expand-contract、大 backfill 拆独立步骤。**置信度：中-高**。（**历史提案；Superseded by the Accepted Major Revision below。**）
- **Candidate 处置（2026-08-03 用户正式决定）：** Candidate A = **ACCEPTED WITH MAJOR REVISION**（Formal Model = Alembic-managed Business Schema Migrations + Single Business Migration Lineage + Forward-recovery-first Production Policy + Expand-Migrate-Contract Rolling Compatibility + Resumable Application-owned Data Backfills + Explicit Destructive/Non-transactional DDL Gates + Separate Vendor Migration Lifecycles）；Candidate B = **NOT SELECTED AS A UNIVERSAL PRODUCTION RECOVERY GUARANTEE**（"所有 Migration 都应支持安全 Downgrade" 方向拒绝；Safe Tested Downgrade = 对明确可逆、无数据损失且经真实 PostgreSQL 测试的 Migration 可选择性提供）；Candidate C = **REJECTED AS THE SOLE MIGRATION SYSTEM**（Hand-written PostgreSQL SQL = 当 Alembic Operations 不足时允许在受治理 Alembic Revision 内使用）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-03 用户正式决定）：**

  > **3.1 正式迁移模型**
  >
  > 1. Business Schema 使用受治理的 Alembic Migration Environment。
  > 2. MVP 采用：
  >
  >    ```text
  >    ALEMBIC-MANAGED BUSINESS SCHEMA MIGRATIONS
  >    + SINGLE BUSINESS MIGRATION LINEAGE
  >    + FORWARD-RECOVERY-FIRST PRODUCTION POLICY
  >    + EXPAND-MIGRATE-CONTRACT ROLLING COMPATIBILITY
  >    + RESUMABLE APPLICATION-OWNED DATA BACKFILLS
  >    + EXPLICIT DESTRUCTIVE / NON-TRANSACTIONAL DDL GATES
  >    + SEPARATE VENDOR MIGRATION LIFECYCLES
  >    ```
  >
  > 3. Candidate A 被接受并进行重大修订。
  > 4. Candidate B 不作为通用生产恢复保证。
  > 5. Candidate B 中「所有 Migration 都应支持安全 Downgrade」的方向被拒绝。
  > 6. 对明确可逆、无数据损失并经过真实 PostgreSQL 测试的 Migration，可以选择性提供安全 Downgrade。
  > 7. Candidate C 作为唯一 Migration System 被拒绝。
  > 8. 当 Alembic Operations 无法准确表达 PostgreSQL 能力时，允许在受治理的 Alembic Revision 内使用人工编写的 PostgreSQL SQL。
  > 9. 手写 SQL 不得绕过 Revision Graph、Review、Deployment Gate 或 Migration History。
  >
  > **3.2 Migration Ownership**
  >
  > 10. Business Schema 使用一个明确、受治理的 Business Alembic Migration Environment。
  > 11. 每张 Business Table 的唯一数据所有模块继续遵循 DQ-02。
  > 12. 表的所有模块负责提出和审查该表的 Schema Change。
  > 13. Migration 执行编排由唯一 Migration Capability、Deployment Pipeline 或受控 Migration Job 负责。
  > 14. Business Application Replica、Web Worker、Background Worker 和 Workflow Worker 不得在启动时自动运行：
  >
  >    ```text
  >    alembic upgrade head
  >    ```
  >
  > 15. 生产环境一次只能存在一个受控 Business Migration Executor。
  > 16. Migration Executor 必须具有独立身份、权限、日志与审计轨迹。
  > 17. Runtime Application Role 不应拥有生产 Schema DDL 权限。
  > 18. Migration Role 与 Runtime Role 应分离。
  > 19. 跨模块 Migration 必须明确：Owner；Affected Modules；Affected Tables；Compatibility Window；Backfill Owner；Verification Owner；Contract Approval；Reviewer。
  > 20. 一个 Migration Revision 可以影响多个模块，但不得因此改变每张表的唯一所有权。
  > 21. 跨模块 Revision 必须说明为什么不能拆为多个独立 Revision。
  >
  > **3.3 Single Business Migration Lineage**
  >
  > 22. MVP 的 Business Alembic Migration 在 Merge Gate 与 Release Gate 必须保持一个明确最终 Head。
  > 23. Local Feature Branch 可以短暂产生多个 Migration Heads。
  > 24. Multiple Heads 不得进入受保护主分支或生产 Release。
  > 25. CI 必须验证：
  >
  >    ```text
  >    alembic heads
  >    → exactly one Business Head
  >    ```
  >
  > 26. 发现 Multiple Heads 时必须采用以下一种显式方式解决：Rebase 后重新生成尚未发布的 Revision；调整尚未发布 Revision 的依赖关系；创建明确的 Alembic Merge Revision。
  > 27. 不得通过删除已发布 Revision 解决 Multiple Heads。
  > 28. 不得通过修改已在共享环境运行过的 `revision` 或 `down_revision` 伪造单一历史。
  > 29. Alembic Merge Revision 必须保留两个或多个 Parent Head 的完整因果关系。
  > 30. Migration Head 的单一性只适用于 Business Alembic Lineage。
  > 31. PostgresSaver Vendor Migration、其他 Vendor Migration 和外部存储版本不得被伪装成 Business Alembic Head。
  >
  > **3.4 Migration History Immutability**
  >
  > 32. Revision 一旦在任一共享环境执行，即视为已发布 Migration Record。
  > 33. 共享环境包括：Shared Development；Integration；CI Persistent Environment；Staging；Pre-production；Production；任何其他团队成员依赖的数据库。
  > 34. 已发布 Revision 不得修改：Revision ID；`down_revision`；Upgrade 语义；Downgrade 语义；数据转换逻辑；DDL；Migration Classification。
  > 35. 已发布 Revision 不得删除或重命名。
  > 36. 已发布 Migration 出错时必须创建新的 Forward Repair Revision。
  > 37. 尚未离开个人 Feature Branch、未在任何共享环境执行、没有外部消费者的 Revision，可以在 Merge 前重建。
  > 38. 重建未发布 Revision 前必须证明没有共享环境或其他 Branch 引用。
  > 39. Migration History Immutability 不等于 Business Version Immutability；两者是不同语义。
  >
  > **3.5 Autogenerate Discipline**
  >
  > 40. Alembic Autogenerate 只作为 Candidate Migration Generator。
  > 41. Autogenerate Output 不等于 Approved Migration。
  > 42. 所有 Autogenerate Revision 必须人工 Review。
  > 43. 人工 Review 至少检查：Table Rename；Column Rename；Type Change；Server Default；Python-side Default；Nullable；Foreign Key；Unique Constraint；Check Constraint；Index；Enum；Schema；Generated Column；Identity；Partition；Sequence；Data Migration；Lock Risk；Rewrite Risk；Destructive Operation。
  > 44. Table Rename 或 Column Rename 被识别成 Drop/Add 时必须人工修正为显式 Rename 或安全 Expand/Contract。
  > 45. 不得允许 Rename 误判导致数据丢失。
  > 46. Autogenerate 产生的以下操作必须默认阻塞：
  >
  >    ```text
  >    drop_table
  >    drop_column
  >    drop_constraint
  >    ```
  >
  > 47. 只有通过 Destructive Migration Gate 后，阻塞操作才可以进入正式生产 Migration。
  > 48. Business Autogenerate 必须排除：Vendor Checkpoint Tables；Vendor Migration Tables；非 Business-owned Schema；临时测试表；外部系统管理的对象；不受 Business Alembic 所有的数据库对象。
  > 49. `include_name`、`include_object`、Target Metadata 范围或等价过滤机制必须显式配置。
  > 50. 不得因为对象未出现在 Business Metadata 中，就自动判断该对象应该被删除。
  > 51. Autogenerate 不得替代 DBA、Migration Owner 或 Schema Reviewer 的风险审查。
  >
  > **3.6 Schema Drift Gate**
  >
  > 52. CI 应执行：
  >
  >    ```text
  >    alembic check
  >    ```
  >
  > 53. `alembic check` 用于识别当前 Autogenerate 能检测出的 ORM Metadata Drift。
  > 54. `alembic check PASS` 仅表示未检测到当前比较器能够发现的差异。
  > 55. `alembic check PASS` 不表示：Migration 安全；Migration 在线；Migration 可逆；Migration 无数据损失；Migration 无锁风险；Migration 已完成 Backfill；Migration 已通过 Compatibility 验证。
  > 56. CI 还必须验证：Revision Graph 有效；Business Head 单一；Revision ID 唯一；`down_revision` 可解析；Vendor Schema 未进入 Business Metadata；未授权 Destructive Operation 不存在。
  > 57. Schema Drift Gate 不得直接修改数据库。
  >
  > **3.7 Forward-recovery-first Production Policy**
  >
  > 58. Forward-only 的正式含义是：
  >
  >    ```text
  >    Production Recovery Does Not Depend on Universal Schema Downgrade
  >    ```
  >
  > 59. Forward-only 不表示所有 `downgrade()` 必须为空。
  > 60. Production Release Failure 的默认恢复顺序为：
  >
  >    ```text
  >    Rollback Compatible Application
  >    → Keep Expanded Schema
  >    → Apply Forward Repair Migration if Required
  >    ```
  >
  > 61. 已执行不可逆 Migration 后不得假装能够无损 Downgrade。
  > 62. Forward Repair 必须使用新的 Alembic Revision 或受治理恢复流程。
  > 63. Forward Repair 不得修改历史 Revision。
  > 64. 对仍处于 Expand 状态的 Schema，旧 Application 必须在 Compatibility Window 内继续可运行。
  > 65. 生产部署前必须证明 Application Rollback 不依赖危险的 Schema Downgrade。
  >
  > **3.8 Rollback 术语分离**
  >
  > 66. 必须区分：Application Rollback；Schema Downgrade；Forward Repair Migration；Database Restore；Point-in-time Recovery；DQ-11 Business Restore。
  > 67. Application Rollback 表示回滚到与当前 Expanded Schema 兼容的 Application 版本。
  > 68. Schema Downgrade 表示执行 Alembic Downgrade Revision。
  > 69. Forward Repair 表示创建新的 Migration 或数据修复流程。
  > 70. Database Restore/PITR 表示基础设施灾难恢复。
  > 71. DQ-11 Business Restore 表示创建新的前向 Business Version。
  > 72. 上述操作不得共享术语、Application Contract 或成功标准。
  > 73. Database Restore/PITR 不得被描述成普通 Alembic Downgrade。
  > 74. Alembic Downgrade 不得被描述成 Business Restore。
  >
  > **3.9 Migration Reversibility Classification**
  >
  > 75. 每个 Revision 必须明确分类为以下一种或多种受控类型：
  >
  >    ```text
  >    REVERSIBLE_SCHEMA
  >    FORWARD_FIX_ONLY
  >    DATA_IRREVERSIBLE
  >    NON_TRANSACTIONAL_DDL
  >    DESTRUCTIVE_CONTRACT
  >    VENDOR_MANAGED
  >    ```
  >
  > 76. `REVERSIBLE_SCHEMA` 表示 Upgrade 与 Downgrade 均无数据损失，并经过真实 PostgreSQL 验证。
  > 77. `FORWARD_FIX_ONLY` 表示生产恢复依赖新的 Forward Revision。
  > 78. `DATA_IRREVERSIBLE` 表示转换会丢失、合并或不可逆改变数据。
  > 79. `NON_TRANSACTIONAL_DDL` 表示包含不能安全放入普通事务的 DDL。
  > 80. `DESTRUCTIVE_CONTRACT` 表示移除旧结构或不可逆收紧契约。
  > 81. `VENDOR_MANAGED` 表示不属于 Business Alembic 生命周期。
  > 82. 每个 Revision 至少声明：Owner；Affected Tables；Revision Classification；Upgrade Strategy；Downgrade Classification；Compatibility Window；Data-loss Risk；Lock Risk；Rewrite Risk；Backfill Requirement；Verification Query；Recovery Strategy；Required Application Version；Related DQ/DEC/RFC。
  > 83. `FORWARD_FIX_ONLY`、`DATA_IRREVERSIBLE` 和 `DESTRUCTIVE_CONTRACT` 不得提供一个看似成功、实际丢失数据的虚假 Downgrade。
  > 84. 不支持安全 Downgrade 时应明确失败或标记为不支持，而不是伪造成功。
  >
  > **3.10 Expand–Migrate–Contract**
  >
  > 85. 所有不兼容 Schema Change 默认使用：
  >
  >    ```text
  >    EXPAND
  >    → COMPATIBLE APPLICATION
  >    → MIGRATE / BACKFILL
  >    → VERIFY / CUTOVER
  >    → CONTRACT
  >    ```
  >
  > 86. **Expand：** Expand 只增加旧 Application 可以忽略的新结构。
  > 87. Expand 可以包括：Nullable Column；New Table；New Optional Relationship；New Index；Shadow Column；新旧字段并存；`NOT VALID` Constraint；Compatibility View 或受控兼容结构。
  > 88. Expand 不得立即删除旧字段或旧表。
  > 89. Expand 不得在旧 Application 仍运行时改变旧字段的业务语义。
  > 90. **Compatible Application：** Compatibility Window 内必须支持必要组合：Old Code + Old Schema；Old Code + Expanded Schema；New Code + Expanded Schema；Application Rollback + Expanded Schema。
  > 91. 如果需要 Dual Write，必须明确唯一实现所有者。
  > 92. Dual Write 不得同时由 Application、ORM Hook、Database Trigger 和 Worker 隐式重复实现。
  > 93. Read Fallback 与 Cutover 条件必须明确。
  > 94. **Migrate / Backfill：** 历史数据转换通过独立、可恢复 Backfill 完成。
  > 95. Backfill 不得被视为 Alembic Head 到达即自动完成。
  > 96. **Verify / Cutover：** Cutover 前必须验证：Backfill 完成；新旧数据一致；Constraint Violation 为零；新读取路径稳定；业务校验通过；监控无阻塞异常；旧 Application 已进入退出流程。
  > 97. **Contract：** Contract 只能在 Compatibility Window 关闭后执行。
  > 98. Contract 可以包括：Drop Old Column；Drop Old Table；Remove Dual Write；Remove Compatibility Trigger；Remove Compatibility View；Enforce Final Constraint；Remove Old Index；Remove Old Read Path。
  > 99. Expand 与 Contract 不得在同一次发布完成。
  > 100. Contract Migration 必须经过 Destructive Gate。
  > 101. Contract 前必须证明所有旧 Application Replica 已退出。
  > 102. Contract 前必须证明 Rollback Target 不再依赖旧结构。
  >
  > **3.11 Resumable Application-owned Backfill**
  >
  > 103. 大型 Backfill 不得放入单个长时间 Alembic Transaction。
  > 104. 禁止在普通 `upgrade()` 中对大型表执行无界全表更新。
  > 105. 小型、确定性、低风险数据修正可以保留在 Migration 内，但必须声明规模和事务风险。
  > 106. 大型 Backfill 必须由项目拥有的 Backfill Runtime 或受控 Job 执行。
  > 107. Backfill 至少应表达：`backfill_run_id`；Migration Revision；Backfill Type；Owner；Batch Cursor；Batch Size；Status；Lease Holder；Attempt ID；Fencing Token；Started Time；Updated Time；Completed Time；Verification Status；Failure Classification。
  > 108. Backfill 必须支持：分批提交；暂停；恢复；安全重试；幂等执行；进度观测；失败诊断；完成验证。
  > 109. Backfill 必须遵循 DQ-07 Durable Lease 与 Fencing。
  > 110. Backfill 必须遵循 DQ-08 Idempotency。
  > 111. Backfill 不得持有长时间 SQLAlchemy Session 或 Application UoW。
  > 112. Backfill 不得在一次事务中处理完整大型数据集。
  > 113. Backfill Retry 不得重置已验证完成的批次。
  > 114. 多 Worker Backfill 必须防止重复业务效果和旧 Worker 提交。
  >
  > **3.12 Technical Backfill 与 Business Semantic Change**
  >
  > 115. 必须区分：
  >
  >    ```text
  >    TECHNICAL REPRESENTATION BACKFILL
  >    ≠
  >    BUSINESS SEMANTIC CHANGE
  >    ```
  >
  > 116. Technical Backfill 可以包括：复制等价字段；计算物理派生列；规范化等价存储表示；填充搜索辅助字段；建立新索引所需数据；不改变业务含义的编码转换。
  > 117. 如果 Backfill 会改变以下任一内容，则不能只作为 Technical Migration：Business Current Truth；Domain Version；Review Decision；Evidence；Business Validity；User-visible Business Meaning；Audit Semantics。
  > 118. Business Semantic Change 必须通过正式 Business Application Contract。
  > 119. Business Semantic Change 必须遵守：DQ-04 Versioning；DQ-08 Idempotency；DQ-10 Audit；DQ-11 Immutable Business Version；DEC-035 Atomic Business Commit。
  > 120. Migration Role 不得绕过业务不变量直接制造新的 Business Current Truth。
  >
  > **3.13 PostgreSQL Add Column**
  >
  > 121. 大型表默认优先增加 Nullable Column。
  > 122. 不得假设所有 `ADD COLUMN DEFAULT` 都是 Metadata-only 或无锁操作。
  > 123. 迁移策略必须基于项目实际钉定 PostgreSQL 版本验证。
  > 124. 以下情况必须特别评估 Rewrite 与 Lock 风险：Volatile Default；Stored Generated Column；Identity；Domain Constraint；Type Conversion；Existing Row Validation。
  > 125. 新 Non-null Column 默认采用：
  >
  >    ```text
  >    Add Nullable
  >    → Backfill
  >    → Verify
  >    → Add/Validate Constraint
  >    → Enforce Final Nullability
  >    ```
  >
  > 126. 不得在未分析大型表风险时直接加入强制 Non-null Default。
  >
  > **3.14 Constraint Migration**
  >
  > 127. 大型表 Constraint 应优先评估：
  >
  >    ```text
  >    ADD CONSTRAINT ... NOT VALID
  >    → REPAIR / BACKFILL
  >    → VALIDATE CONSTRAINT
  >    ```
  >
  > 128. `NOT VALID` 不表示新写入可以违反 Constraint。
  > 129. Validation 必须作为明确 Deployment Step。
  > 130. Validation Failure 不得被忽略。
  > 131. Constraint Migration 必须声明：Constraint Name；Existing Violation Query；Repair Strategy；Validation Step；Lock Risk；Recovery Strategy。
  > 132. Unique Constraint、Exclusion Constraint 和不同类型 Not-null Enforcement 必须依据实际 PostgreSQL 能力单独评估，不得笼统套用相同方案。
  >
  > **3.15 Concurrent Index**
  >
  > 133. 大型生产表新建索引优先评估：
  >
  >    ```text
  >    CREATE INDEX CONCURRENTLY
  >    ```
  >
  > 134. Concurrent Index 不能在普通 Transaction Block 中运行。
  > 135. Concurrent Index 必须置于独立、明确的 Non-transactional Migration Boundary。
  > 136. 不得将 Concurrent Index 与必须原子提交的其他 DDL 混入同一个普通事务。
  > 137. 使用 Alembic Autocommit Boundary 时必须承认此前事务可能被提交。
  > 138. Non-transactional Revision 必须明确 Crash Window。
  > 139. Concurrent Index 失败可能留下 Invalid Index。
  > 140. Migration 必须提供：Invalid Index Detection；Cleanup Strategy；Retry Strategy；Lock/Resource Budget；Verification Query。
  > 141. 不得盲目重试未知状态的 Concurrent Index Migration。
  > 142. 同一表并发 Index Build 的限制必须在计划中明确。
  >
  > **3.16 Type Change**
  >
  > 143. 可能触发表重写或长锁的 Type Change 默认采用：
  >
  >    ```text
  >    Add Shadow Column
  >    → Compatible Dual Write
  >    → Resumable Backfill
  >    → Verify
  >    → Switch Read Path
  >    → Contract Old Column
  >    ```
  >
  > 144. 不得默认在大型表直接执行高风险 `ALTER COLUMN TYPE`。
  > 145. 直接 Type Change 只有在完成数据量、Rewrite、Lock 和 Compatibility 证明后才可采用。
  > 146. Type Narrowing 属于 Destructive Migration。
  > 147. Type Conversion 必须处理无法转换的数据和失败恢复。
  >
  > **3.17 Lock 与资源预算**
  >
  > 148. 每个生产 Migration 必须声明：`lock_timeout`；`statement_timeout`；Expected Table Scan；Expected Table Rewrite；Expected Extra Disk；Expected WAL/Replication Impact；Maintenance Window；Estimated Runtime；Retry Safety。
  > 149. 获取危险 Lock 超时后应失败，而不是无限等待。
  > 150. Migration 不得在高流量期间意外长期持有 `ACCESS EXCLUSIVE` Lock。
  > 151. Table Rewrite、Index Build 和 Backfill 必须评估额外磁盘空间。
  > 152. 必须评估 WAL、Replica Lag、Vacuum 和 Backup 影响。
  > 153. Migration Failure 必须保留足够信息判断是否可安全重试。
  > 154. 不得盲目重试 Non-transactional DDL。
  > 155. Timeout 设置不得被全局无限放宽。
  >
  > **3.18 Destructive Migration Gate**
  >
  > 156. 以下操作必须通过显式 Destructive Migration Gate：Drop Table；Drop Column；Drop Constraint；Type Narrowing；不可逆数据转换；Enum Value 删除或重建；强制 Unique Constraint；强制 Non-null Constraint；Partition Drop/Detach；Retention 物理删除；大规模数据重写；无法安全 Downgrade 的 Contract 变更。
  > 157. Gate 至少要求：Owner Approval；Schema Reviewer Approval；Impact Analysis；Application Compatibility 证明；旧 Application 已退出证明；Backfill Verification；Data-loss Risk；Backup/Recovery Plan；DQ-15 Retention Compliance；DQ-17 Security/PII Review；Recovery Runbook；Deployment Window。
  > 158. Autogenerate 产生 Destructive Operation 不构成 Gate Approval。
  > 159. Merge Approval 不自动构成 Production Destructive Gate。
  > 160. DQ-14 接受不授权执行任何 Destructive Migration。
  >
  > **3.19 Non-transactional DDL Gate**
  >
  > 161. 以下操作必须明确标记为 Non-transactional 或部分提交风险：`CREATE INDEX CONCURRENTLY`；`DROP INDEX CONCURRENTLY`；其他实际 PostgreSQL 版本不允许在 Transaction Block 内运行的 DDL；使用 Alembic Autocommit Block 的操作。
  > 162. Non-transactional DDL 必须使用独立 Revision 或独立 Deployment Step。
  > 163. Non-transactional DDL 不得与必须同事务的 DDL 混合。
  > 164. Gate 必须记录：Precondition；Partial Commit Boundary；Failure State；Detection Query；Cleanup；Retry；Recovery。
  > 165. Non-transactional Migration 执行失败不意味着数据库自动恢复到执行前状态。
  > 166. 必须验证失败后的实际数据库对象状态。
  >
  > **3.20 Vendor Migration Separation**
  >
  > 167. 必须保持：
  >
  >    ```text
  >    BUSINESS ALEMBIC MIGRATION
  >    ≠
  >    POSTGRESSAVER VENDOR MIGRATION
  >    ≠
  >    RETRIEVAL INDEX REBUILD
  >    ≠
  >    OBJECT STORAGE LIFECYCLE
  >    ```
  >
  > 168. DQ-13 PostgresSaver Setup/Vendor Migration 不属于 Business Alembic Lineage。
  > 169. Business Alembic 不得：接管 Vendor Checkpoint Tables；修改 Vendor Migration Metadata；伪造 Vendor Setup；将 Vendor Schema 纳入 Autogenerate Drop；假设 Vendor Version 与 Business Head 相同。
  > 170. Retrieval Index Rebuild 不得被记录为 Business Alembic Revision。
  > 171. Object Storage Lifecycle Change 不得被记录为 Business Schema Migration。
  > 172. Vendor Upgrade 必须遵循其独立 Compatibility 与 Recovery 规则。
  >
  > **3.21 Schema Version Identity Separation**
  >
  > 173. 以下身份必须保持独立：`alembic_revision`；`domain_version_id`；Business `version_number`；Concurrency `revision`；`checkpoint_schema_version`；`graph_definition_version`；`event_schema_version`；`payload_schema_version`；`source_artifact_schema_version`。
  > 174. `alembic_revision` 只表示数据库物理 Schema Migration 位置。
  > 175. `alembic_revision` 不表示：Business Current Truth；Domain Version；API Version；Event Version；Checkpoint Compatibility；Payload Compatibility；Backfill Completion；Validation Completion；Contract Authorization。
  > 176. 数据库到达 Alembic Head 后，仍可能处于：
  >
  >    ```text
  >    BACKFILL_PENDING
  >    VALIDATION_PENDING
  >    CUTOVER_PENDING
  >    CONTRACT_NOT_AUTHORIZED
  >    ```
  >
  > 177. Application 必须根据显式 Compatibility/Feature State 判断能否使用新结构，而不是只检查 Alembic Head。
  >
  > **3.22 Migration Deployment Protocol**
  >
  > 178. 推荐生产顺序：
  >
  >    ```text
  >    1. PREFLIGHT
  >    2. EXPAND MIGRATION
  >    3. DEPLOY COMPATIBLE APPLICATION
  >    4. RUN RESUMABLE BACKFILL
  >    5. VERIFY DATA AND TRAFFIC
  >    6. SWITCH READ PATH
  >    7. END COMPATIBILITY WINDOW
  >    8. CONTRACT MIGRATION
  >    ```
  >
  > 179. Preflight 至少检查：Current Alembic Revision；Expected Parent Revision；Single Head；Lock/Statement Timeout；Disk Capacity；Replica Health；Pending Backfill；Old Application Version；Migration Executor Ownership；Destructive/Non-transactional Gate。
  > 180. Migration 必须由受控 Deployment Job 或 Migration Executor 执行。
  > 181. Web/Worker Replica 不得自动执行 Migration。
  > 182. 需要 DBA 审查或受限 DDL 权限时，可以使用 Alembic Offline SQL。
  > 183. Offline SQL 必须与正式 Revision 和 Target PostgreSQL 版本对应。
  > 184. 手工执行 Offline SQL 后必须正确记录 Migration Version，且不得绕过验证。
  > 185. Migration 执行成功不等于整个 Feature Rollout 完成。
  >
  > **3.23 CI 与测试最低要求**
  >
  > 186. DQ-16 负责最终测试分类，但 DQ-14 规定以下最低 Gate：
  >
  >    ```text
  >    alembic heads → exactly one Business Head
  >    alembic check → no detectable drift
  >    fresh PostgreSQL → upgrade to head
  >    supported baseline → upgrade to head
  >    revision graph → valid
  >    generated offline SQL → reviewable
  >    destructive operation → gated
  >    vendor schema → excluded
  >    ```
  >
  > 187. 后续测试至少覆盖：Fresh Database Upgrade；Current Supported Baseline Upgrade；单一 Business Head；Multiple Head Detection；Merge Revision；Autogenerate Rename 修正；Vendor Schema Exclusion；Reversible Migration Downgrade/Upgrade Round-trip；Expand 后 Old Application 运行；Expand 后 New Application 运行；Application Rollback + Expanded Schema；Resumable Backfill；Backfill Crash Recovery；Backfill Idempotency；Constraint Validation；Lock Timeout；Concurrent Index Success；Concurrent Index Failure；Invalid Index Cleanup；Non-transactional Crash Boundary；Contract 在旧 Application 存活时被阻止；Destructive Gate；Forward Repair；无 Business Partial Write。
  > 188. 标记为 Reversible 的 Migration 必须在真实 PostgreSQL 中测试 Downgrade/Upgrade Round-trip。
  > 189. 不可逆 Migration 不得通过虚假 Downgrade 测试获得绿色状态。
  >
  > **3.24 Readiness Artifact**
  >
  > 190. 在首个正式 Business Schema Migration 实现授权前，Architecture Readiness Package 必须包含：
  >
  >    ```text
  >    Schema Migration Compatibility & Risk Table
  >    ```
  >
  > 191. 该表至少包含：Migration/Feature；Owner Module；Affected Tables；Current Revision；Target Revision；Expand Step；Compatibility Code；Backfill Step；Verification Step；Cutover Step；Contract Step；Oldest Compatible Application；Destructive Operation；Non-transactional Operation；Lock Level/Risk；Table Rewrite Risk；Downgrade Classification；Recovery Strategy；Data-loss Risk；Retention/Security Impact；Deployment Gate；Related DQ/DEC/RFC。
  > 192. DQ-14 接受不授权创建该表。
  > 193. Schema Migration Compatibility & Risk Table Creation = NOT AUTHORIZED。
  > 194. DQ-14 不新增独立 Matrix。
  >
  > **3.25 Technical Spike**
  >
  > 195. DQ-14 决策归档前不要求执行 Technical Spike。
  > 196. 在首个生产 Migration Pipeline 实现前，必须完成单独授权的：
  >
  >    ```text
  >    Schema Migration Rollout & Recovery Technical Spike
  >    ```
  >
  > 197. Spike 最低验证：Single Head Gate；Revision Graph；Alembic Autogenerate 人工修正；Rename 不产生 Drop/Add；Vendor Schema Exclusion；Expand 后 Old/New Application Compatibility；Application Rollback 不依赖 Schema Downgrade；Resumable Backfill；Backfill Crash Recovery；Lock Timeout；`NOT VALID` / `VALIDATE`；`CREATE INDEX CONCURRENTLY`；Alembic Autocommit Partial Commit Boundary；Invalid Index Recovery；Multiple Head Merge Revision；Fresh Database Upgrade；Existing Database Upgrade；Destructive Gate；Forward Repair；无 Business Partial Write。
  > 198. Spike 必须使用项目实际钉定的 PostgreSQL、Alembic、SQLAlchemy 与 Psycopg 版本。
  > 199. Spike 可以共享 PostgreSQL 测试基础设施，但验收报告必须独立。
  > 200. 本次接受不授权创建 Spike Issue、Branch、PR、代码、测试、Alembic Environment、Revision、Database 或基础设施。
  > 201. Schema Migration Rollout & Recovery Technical Spike = REQUIRED / NOT AUTHORIZED。
  >
  > **3.26 授权边界**
  >
  > 202. DQ-14 只授权决策归档与文档同步。
  > 203. DQ-14 不授权创建：Alembic Environment；Alembic Config；Migration Revision；Migration Script；Migration Job；Migration Executor；Backfill Registry；Backfill Worker；DDL；Constraint；Index；Trigger；Readiness Table；Technical Spike；测试；部署配置。
  > 204. DQ-14 不授权修改 Production Database。
  > 205. DQ-14 不授权修改 Vendor Checkpoint Tables。
  > 206. DQ-14 不授权接受 DQ-15 或后续 DQ。

---

## DQ-15：Data Retention & Deletion Boundary（数据保留与删除边界）

- **Question：** Task / raw source / evidence / checkpoints / audit / model responses 各类数据的保留策略归属与边界？
- **Why：** DEC-013/025 明确「数据保留周期/删除策略尚未确认」；须划清保留责任但**不虚构保留周期数值**。
- **Constraints（[DEC 约束]）：** DEC-024 历史不删除（版本化业务真值）；Invalidation Does Not Mean Deletion；checkpoint 为执行副产物。
- **[官方能力]：** LangGraph checkpoint 无内建 TTL、`delete_thread` 可用、`prune` 当前钉版不可用、官方建议应用层 cron 清理；TTL 仅属 Store（非 Checkpointer）。
- **Candidates：**
  - **A. 分类定责：业务真值/审计不删除；checkpoint/运行日志可回收；原始来源按合规待定**。
  - **B. 统一 TTL**：简单粗暴但违反「历史不删除」。
  - **C. 全部保留**：存储膨胀。
- **Trade-offs：** A 符合 DEC 且给 checkpoint 回收空间；B 违规；C 不可持续。
- **Failure modes：** 误删业务历史→违反 DEC-024；无 checkpoint 清理→膨胀；原始来源无合规策略→合规风险。
- **Impact on later RFCs：** RFC-003（checkpoint 保留）、RFC-007（日志保留）。
- **Recommendation：** **[架构推断] 倾向 A**——分类定责，业务真值/审计 append-only 不删，checkpoint/运行记录由应用层可回收，原始来源保留策略留合规决定（**具体周期数值由用户定，不虚构**）。**置信度：中**。（**历史提案；Superseded by the Accepted Major Revision below。**）
- **Candidate 处置（2026-08-03 用户正式决定）：** Candidate A = **ACCEPTED WITH MAJOR REVISION**（Formal Model = Classified Retention & Disposition Policies + Purpose/Legal-basis-driven Retention Clocks + Reference-aware Deletion Eligibility + Legal/Security/Incident Hold Overrides + Normal-lifecycle Immutability for Business History + Governed Exceptional Erasure/Redaction Paths + Idempotent Auditable Purge Orchestration + Separate Primary/Object/Index/Checkpoint/Backup Lifecycles）；Candidate B = **REJECTED**（Universal TTL violates data semantics and history requirements）；Candidate C = **REJECTED**（Universal Permanent Retention is unsustainable and may conflict with retention-limitation obligations）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-03 用户正式决定）：**

  > **3.1 正式模型**
  >
  > 1. MVP 采用：
  >
  >    ```text
  >    CLASSIFIED RETENTION & DISPOSITION POLICIES
  >    + PURPOSE / LEGAL-BASIS-DRIVEN RETENTION CLOCKS
  >    + REFERENCE-AWARE DELETION ELIGIBILITY
  >    + LEGAL / SECURITY / INCIDENT HOLD OVERRIDES
  >    + NORMAL-LIFECYCLE IMMUTABILITY FOR BUSINESS HISTORY
  >    + GOVERNED EXCEPTIONAL ERASURE / REDACTION PATHS
  >    + IDEMPOTENT AUDITABLE PURGE ORCHESTRATION
  >    + SEPARATE PRIMARY / OBJECT / INDEX / CHECKPOINT / BACKUP LIFECYCLES
  >    ```
  >
  > 2. Candidate A 被接受并进行重大修订。
  > 3. Candidate B Universal TTL 被拒绝。
  > 4. Candidate C Universal Permanent Retention 被拒绝。
  > 5. 不得为整个项目设置一个通用 TTL。
  > 6. 不得假设所有数据都应永久保留。
  > 7. 本决定不设置任何具体保留天数、月数或年数。
  > 8. 具体期限必须由未来明确的业务、合规、合同、安全和运营决定提供。
  >
  > **3.2 数据生命周期术语分离**
  >
  > 9. 必须区分：
  >    - Invalidation；
  >    - Supersession；
  >    - Archive；
  >    - Cold Storage；
  >    - Access Restriction；
  >    - Redaction；
  >    - Pseudonymization；
  >    - Anonymization；
  >    - Tombstone；
  >    - Logical Deletion；
  >    - Physical Purge；
  >    - Backup Expiry。
  > 10. Invalidation 表示记录不再有效，不表示物理删除。
  > 11. Supersession 表示新记录取代旧记录，不表示旧记录被删除。
  > 12. Archive 表示访问频率或存储层级发生变化，不表示删除。
  > 13. Access Restriction 表示限制读取权限，不表示删除。
  > 14. Encryption 不表示删除。
  > 15. Soft Delete 不表示 Physical Purge。
  > 16. Redaction 表示受控删除或替换部分字段。
  > 17. Pseudonymization 不得被自动描述为不可逆匿名化。
  > 18. Anonymization 必须以无法合理重新识别为目标，但精确法律标准留给 DQ-17。
  > 19. Tombstone 是删除后允许保留的最小存在和处置证明。
  > 20. Physical Purge 表示从适用权威与派生存储中执行实际删除。
  > 21. 上述术语不得在数据库字段、API、运营手册或审核报告中混用。
  >
  > **3.3 Retention Policy 分类**
  >
  > 22. 每类数据必须拥有独立 Retention Policy。
  > 23. 每项 Policy 至少定义：
  >    - Data Class；
  >    - Owning Module；
  >    - Authoritative/Derived；
  >    - Business Purpose；
  >    - Legal/Contractual Basis；
  >    - Retention Trigger；
  >    - Retention Clock；
  >    - Minimum Required Horizon；
  >    - Maximum Permitted Horizon；
  >    - Deletion Blockers；
  >    - Hold Types；
  >    - Normal Disposition；
  >    - Exceptional Erasure Action；
  >    - Storage-plane Treatment；
  >    - Verification Owner。
  > 24. Retention Policy 不得只包含一个 TTL 数字。
  > 25. Retention Policy 必须区分最短必须保留时间和最长允许保留时间。
  > 26. 如果当前没有获得合法的具体期限，必须明确标记：
  >
  >    ```text
  >    PERIOD NOT DECIDED
  >    ```
  >
  > 27. 不得由实现人员自行虚构期限。
  >
  > **3.4 Retention Clock**
  >
  > 28. Retention Clock 不得统一使用 `created_at`。
  > 29. 可能的 Trigger 包括：
  >    - Workflow Terminal；
  >    - Business Relationship End；
  >    - Superseded；
  >    - Invalidated；
  >    - Delivery Completed；
  >    - Replay Window Closed；
  >    - Deduplication Window Closed；
  >    - Last Required；
  >    - Legal Basis Expired；
  >    - Incident Closed；
  >    - Object Became Unreferenced；
  >    - Contract Ended；
  >    - Review Completed。
  > 30. 每个 Data Class 必须使用与其语义一致的 Trigger。
  > 31. Checkpoint Retention 不得从 Checkpoint Created Time直接计算。
  > 32. Idempotency Retention 必须覆盖合法 Retry 与 Replay 风险。
  > 33. Consumer Dedup Retention 必须覆盖消息可能重复投递的窗口。
  > 34. Orphan Blob Retention 必须从确认没有正式引用且 Grace Period 开始后计算。
  > 35. Business Version 是否可删除不得仅由年龄判断。
  >
  > **3.5 Business Current Truth**
  >
  > 36. 正常业务生命周期中，Business Current Truth 不得被普通 Purge Worker 直接物理删除。
  > 37. 业务上的删除应首先通过明确业务状态表达，例如：
  >
  >    ```text
  >    INACTIVE
  >    INVALIDATED
  >    WITHDRAWN
  >    NO_CURRENT_TRUTH
  >    ```
  >
  > 38. 普通 Business Command 不得绕过业务不变量执行物理级联删除。
  > 39. 法律、隐私或安全要求需要处置 Personal Data 时，必须进入受治理的 Exceptional Erasure/Redaction Path。
  > 40. Exceptional Erasure 不得被普通 Soft Delete 代替。
  >
  > **3.6 Immutable Business Versions**
  >
  > 41. 正常生命周期中，Immutable Business Version 继续遵守：
  >
  >    ```text
  >    NO UPDATE
  >    NO OVERWRITE
  >    NO ROUTINE PHYSICAL DELETE
  >    ```
  >
  > 42. Invalidation、Rejection、Supersession 和 Restore 不得删除历史版本。
  > 43. 历史不可变不得被解释为无论法律要求如何都永久保留完整 PII。
  > 44. 如果历史版本包含受删除要求影响的数据，必须通过 DQ-17 后续决定的受治理机制处理。
  > 45. 允许考虑的机制包括：
  >    - Identity 与 Business Fact 分离；
  >    - 删除独立 Identity Mapping；
  >    - 受治理 Redaction；
  >    - 不可逆 Anonymization；
  >    - 最小 Tombstone；
  >    - 受影响引用状态。
  > 46. DQ-15 不决定具体 Redaction 或 Anonymization 算法。
  >
  > **3.7 Audit 与 State Transition**
  >
  > 47. Audit 与 State Transition 在正常生命周期内保持 Append-only。
  > 48. 不得对 Audit 实施普通统一 TTL。
  > 49. Audit 不得通过 UPDATE 覆盖。
  > 50. Audit 更正继续通过 Correction、Superseding 或 Reversal Record 表达。
  > 51. Audit Payload 必须最小化敏感数据。
  > 52. 不得因为 Audit Append-only 而永久复制：
  >    - Secret；
  >    - Access Token；
  >    - 完整 Provider Payload；
  >    - 不必要 PII；
  >    - 完整 Source Content。
  > 53. Audit 的 Exceptional Redaction 与 Legal Hold 冲突由 DQ-17 和适用法律决定。
  >
  > **3.8 Source、Evidence 与 ContentObject**
  >
  > 54. 不得删除仍被以下对象引用的 Source/Evidence 数据：
  >    - Current Business Version；
  >    - 必须保留的 Historical Business Version；
  >    - EvidenceLink；
  >    - Audit Requirement；
  >    - Legal Hold；
  >    - Security Incident；
  >    - Dispute；
  >    - Active Review；
  >    - Regulatory Hold。
  > 55. Raw Content、Normalized Artifact、Parsed Artifact、Fragment、EvidenceLink 与 Retrieval Index 必须拥有独立生命周期。
  > 56. Source Invalidation 不等于 Source Blob 物理删除。
  > 57. Evidence Retraction 不等于删除 EvidenceLink 历史。
  > 58. EvidenceLink 不得在底层 Source 删除后静默改绑至另一个 SourceVersion。
  > 59. 删除 Source Content 时，应根据策略保留允许保留的最小 Provenance、Hash、Tombstone 或 Deletion Proof。
  > 60. 如果底层 Evidence 被删除或无法使用，上层 Business Version 必须进入明确 Review、Invalidation 或 Evidence-unavailable 状态，而不是静默改变历史。
  >
  > **3.9 Content-addressed Object**
  >
  > 61. ContentObject 只有在以下条件全部满足时才可以进入 Physical Purge：
  >
  >    ```text
  >    active_reference_count = 0
  >    no legal hold
  >    no security hold
  >    no incident hold
  >    no regulatory hold
  >    no pending transaction
  >    grace period completed
  >    reconciliation passed
  >    ```
  >
  > 62. Hash Deduplication 不得合并业务所有权、权限、Tenant 或 Retention Policy。
  > 63. 一个 Blob 被多个合法引用共享时，单一主体或 Tenant 的删除请求不得删除其他仍合法需要的引用。
  > 64. 跨 Tenant 或跨 Security Domain 的误删必须被阻止。
  > 65. Object Purge 前必须重新核验正式数据库引用。
  > 66. 不得只依赖缓存中的 Reference Count。
  > 67. 删除对象后必须记录 Object Store 结果，但不得在证明中复制被删除内容。
  >
  > **3.10 DerivedArtifact、Fragment 与 Retrieval Index**
  >
  > 68. DerivedArtifact 和 Fragment 是否可删除必须考虑 EvidenceLink 与 Historical Business Version 引用。
  > 69. Retrieval Index 是派生、可重建、非权威存储。
  > 70. Retrieval Index 通常可以比 SourceVersion 更早清理。
  > 71. 删除 Retrieval Index 不得删除权威 Source、Fragment 或 EvidenceLink。
  > 72. 删除 Source 后不得通过 Index Rebuild 恢复依法已删除内容。
  > 73. Vector、Embedding Metadata、Search Cache 和 Index Snapshot 必须进入删除范围。
  > 74. EvidenceLink 不得依赖只有 Retrieval Index 才能解析的身份。
  >
  > **3.11 Workflow Checkpoint**
  >
  > 75. Checkpoint 继续采用 DQ-13 Whole-thread Lifecycle Deletion。
  > 76. Thread 只有在以下条件全部满足时才可删除：
  >    - Workflow Terminal；
  >    - 无有效 Lease；
  >    - 无 Pending Resume；
  >    - 无 Human Interrupt；
  >    - 无 Retry Window；
  >    - 无 Incident Hold；
  >    - 无 Legal Hold；
  >    - 无 Security Hold；
  >    - Registry 已标记可清理。
  > 77. ACTIVE、IN_PROGRESS、INTERRUPTED、AWAITING_REVIEW、FAILED_RETRYABLE 和 RECONCILING Thread 不得删除。
  > 78. Checkpoint 删除不得删除：
  >    - Workflow 最小终态；
  >    - Business Result；
  >    - Audit；
  >    - Idempotency；
  >    - Durable Work Intent；
  >    - Provider Call Ledger；
  >    - Domain Version；
  >    - Evidence；
  >    - Integration Event。
  > 79. 默认 Whole-thread Delete，不采用未经验证的 Partial Pruning。
  > 80. Workflow Execution Registry 可以保留最小 Terminal Summary。
  > 81. 精确终态字段留待实现设计。
  >
  > **3.12 Durable Work Intent**
  >
  > 82. Durable Work Intent 在以下状态不得删除：
  >    - Pending；
  >    - Claimed；
  >    - Running；
  >    - Retryable；
  >    - Lease Active；
  >    - Awaiting Manual Review。
  > 83. 只有满足以下条件后才可进入归档或清理：
  >    - Terminal；
  >    - 不可 Retry；
  >    - 无有效 Lease；
  >    - 无 Pending Claim；
  >    - 无 Dead-letter Review；
  >    - Business Result 已确认；
  >    - 所需 Audit 已保存；
  >    - Retention Horizon 已关闭。
  > 84. Work Intent 删除不得删除对应业务结果。
  >
  > **3.13 Integration Event Outbox**
  >
  > 85. Outbox Record 只有在以下条件满足后才可清理：
  >    - 所有规定 Destination 已完成；
  >    - Delivery 状态已确认；
  >    - Replay Window 已关闭；
  >    - Incident Hold 已解除；
  >    - Consumer/Destination Policy 允许。
  > 86. 不得只因单次 Publish 成功立即删除 Outbox。
  > 87. Relay Crash、Destination Retry 和 Late Replay 风险必须纳入 Retention。
  > 88. Dead-letter 或 Manual Review 状态不得删除。
  >
  > **3.14 Consumer Dedup 与 Idempotency**
  >
  > 89. Consumer Dedup 与 Idempotency Record 承担正确性责任。
  > 90. 其保留必须覆盖：
  >    - Maximum Legitimate Retry Window；
  >    - Maximum Replay Window；
  >    - Provider Ambiguity Window；
  >    - Late Duplicate Delivery；
  >    - Incident Investigation Window。
  > 91. 在重复消息或 Command 仍可能合法到达时不得提前删除。
  > 92. 删除 Dedup/Idempotency Record 不得重新开放重复业务效果风险。
  > 93. 具体时间长度留待未来 Policy Table 决定。
  >
  > **3.15 Provider Payload 与 Model Output**
  >
  > 94. 必须区分：
  >    - Business Result；
  >    - Provider Call Ledger；
  >    - Raw Provider Request；
  >    - Raw Provider Response；
  >    - Model Prompt；
  >    - Model Response；
  >    - Tool Payload；
  >    - Debug Trace。
  > 95. Business Result 按业务策略保留。
  > 96. Provider Call Ledger 按幂等、争议与诊断要求保留。
  > 97. Raw Prompt、Raw Response、Tool Payload 和 Debug Trace 不得默认永久保存。
  > 98. 保存完整 Raw Payload 必须有明确目的和安全分类。
  > 99. 不得以“以后可能有用”为理由无限期保留敏感原始载荷。
  > 100. Raw Payload 删除不得破坏正式 Business Result 或必要的 Provider Identity。
  >
  > **3.16 Logs、Metrics 与 Traces**
  >
  > 101. Logs、Metrics 和 Traces 属于 RFC-007 非权威 Observability。
  > 102. Observability 数据可以：
  >    - Sampling；
  >    - Aggregation；
  >    - Redaction；
  >    - Lower Precision；
  >    - Archive；
  >    - Purge。
  > 103. Observability Retention 不得替代 Audit Retention。
  > 104. Audit 删除不得依赖仍存在日志副本。
  > 105. 日志中不得保存本应由 Retention Policy 删除的完整敏感 Payload。
  >
  > **3.17 Migration 与 Backfill Records**
  >
  > 106. Alembic Migration Revision History 正常保留。
  > 107. Migration Outcome、Verification Result、Forward Repair Evidence 与 Destructive Gate Approval 不得作为普通运行日志随意删除。
  > 108. 临时 Backfill Batch、Lock Diagnostic 和低价值 Runtime Logs 可以按策略清理。
  > 109. 清理 Backfill Runtime Data 不得破坏 Migration 可验证性或 Incident Investigation。
  >
  > **3.18 Orphan Blob**
  >
  > 110. Upload 成功但 Database Commit 失败的 Blob 是 Orphan Candidate。
  > 111. Orphan Candidate 删除前必须：
  >    - 等待 Grace Period；
  >    - 再次检查正式引用；
  >    - 排除 Crash Recovery；
  >    - 排除 Eventual Visibility 风险；
  >    - 排除 Hold；
  >    - 记录 Reconciliation Result。
  > 112. 不得在上传后立即删除未找到引用的对象。
  > 113. Orphan Cleanup 必须幂等。
  >
  > **3.19 Policy Ownership**
  >
  > 114. 采用：
  >
  >    ```text
  >    CENTRAL RETENTION GOVERNANCE
  >    + DECENTRALIZED DATA OWNERSHIP
  >    ```
  >
  > 115. Retention Governance 负责：
  >    - Policy Schema；
  >    - Policy Version；
  >    - Hold Priority；
  >    - Deletion Case；
  >    - Execution Protocol；
  >    - Reporting；
  >    - Compliance Mapping。
  > 116. 各模块仍是自身数据的唯一所有者。
  > 117. 数据所有模块负责：
  >    - 判断 Eligibility；
  >    - 提供 Reference/Dependency Check；
  >    - 执行本模块处置；
  >    - 验证处置结果；
  >    - 返回最小 Deletion Proof。
  > 118. 中央 Purge Orchestrator 不得直接跨模块执行任意 SQL DELETE。
  > 119. 中央 Orchestrator 必须通过类型化 Application Contract 调用各所有模块。
  > 120. DQ-02 的唯一表所有权继续有效。
  >
  > **3.20 Policy Versioning**
  >
  > 121. 每项 Retention/Deletion 决定必须记录：
  >    - `retention_policy_id`；
  >    - `retention_policy_version`；
  >    - Data Class；
  >    - Policy Owner；
  >    - Retention Trigger；
  >    - Trigger Time；
  >    - Computed Eligible Time；
  >    - Disposition；
  >    - Business Purpose；
  >    - Legal/Contractual Basis；
  >    - Hold Status；
  >    - Decision Reason；
  >    - Verification Result。
  > 122. Policy 修改不得静默改写历史删除决定的依据。
  > 123. Policy Version 必须可审计。
  > 124. Policy 更新后对存量数据执行批量 Purge 前必须重新进行影响分析和授权。
  > 125. 新 Policy 不得自动扩大旧 Deletion Case 的 Scope。
  >
  > **3.21 Hold**
  >
  > 126. 至少支持：
  >
  >    ```text
  >    LEGAL_HOLD
  >    SECURITY_INCIDENT_HOLD
  >    REGULATORY_HOLD
  >    DISPUTE_OR_CLAIM_HOLD
  >    BUSINESS_REVIEW_HOLD
  >    ```
  >
  > 127. Hold 必须记录：
  >    - Scope；
  >    - Reason；
  >    - Authority；
  >    - Created Time；
  >    - Review Time；
  >    - Release Authority；
  >    - Status；
  >    - Audit Trail。
  > 128. Hold 存在时可以继续计算 Retention Clock。
  > 129. Hold 存在时必须阻止 Physical Purge。
  > 130. Hold 不得被普通 Retention Job 自动解除。
  > 131. 不得创建没有 Owner、Reason、Review 或 Release 机制的永久 Hold。
  > 132. Hold Release 必须可审计。
  >
  > **3.22 Deletion / Erasure Case**
  >
  > 133. 删除请求不得直接映射为单次 SQL DELETE。
  > 134. 每个请求必须形成受治理的：
  >
  >    ```text
  >    DELETION / ERASURE CASE
  >    ```
  >
  > 135. 流程至少包括：
  >
  >    ```text
  >    Receive Request
  >    → Verify Requester / Authority
  >    → Determine Applicable Policy
  >    → Discover Data Scope
  >    → Check References and Holds
  >    → Build Deletion Plan
  >    → Execute by Owning Modules
  >    → Verify All Storage Planes
  >    → Record Completion or Residual State
  >    ```
  >
  > 136. 必须记录为何执行删除、为何阻止、为何暂缓或为何继续保留。
  > 137. 删除请求身份与权限必须验证。
  > 138. Deletion Case 不得自动包含其他主体或 Tenant 的数据。
  > 139. Scope 扩展必须重新授权。
  >
  > **3.23 Reference-aware Eligibility**
  >
  > 140. 删除资格必须考虑完整依赖关系。
  > 141. 示例：
  >
  >    ```text
  >    ContentObject
  >    ← SourceVersion
  >    ← Fragment
  >    ← EvidenceLink
  >    ← BusinessVersion
  >    ```
  >
  > 142. 仍承担正式业务含义的下游引用必须阻止底层对象直接删除。
  > 143. 可能的处置包括：
  >    - Block Purge；
  >    - Redact Allowed Fields；
  >    - Retain Tombstone；
  >    - Apply Governed Anonymization；
  >    - Mark Evidence Unavailable；
  >    - Trigger Business Review；
  >    - Trigger Invalidation。
  > 144. 不得使用未经审查的广泛跨模块 `ON DELETE CASCADE`。
  > 145. Cascade 只允许用于同一所有模块内、生命周期完全一致、非权威或明确从属的 Child Record。
  > 146. Cascade 行为必须在未来 Data Retention Policy Table 中明确。
  >
  > **3.24 Deletion State Machine**
  >
  > 147. Deletion Case 至少区分：
  >
  >    ```text
  >    REQUESTED
  >    ASSESSING
  >    BLOCKED_BY_REFERENCE
  >    HELD
  >    ELIGIBLE
  >    PURGE_IN_PROGRESS
  >    PRIMARY_PURGED
  >    DERIVED_PURGED
  >    OBJECT_PURGED
  >    BACKUP_EXPIRY_PENDING
  >    COMPLETED
  >    FAILED_RETRYABLE
  >    FAILED_MANUAL_REVIEW
  >    ```
  >
  > 148. `COMPLETED` 不得在只删除一张表后立即设置。
  > 149. `PRIMARY_PURGED` 不表示 Object、Index、Cache 或 Backup 已完成处置。
  > 150. `BACKUP_EXPIRY_PENDING` 必须是合法的中间状态。
  > 151. Failed 状态必须保留可恢复信息。
  >
  > **3.25 Purge Orchestration**
  >
  > 152. Purge Worker 必须遵循 DQ-07 Lease、Attempt 与 Fencing Token。
  > 153. Purge Worker 必须遵循 DQ-08 Idempotency。
  > 154. Purge 使用分批短事务。
  > 155. Purge 必须支持：
  >    - Crash Recovery；
  >    - Resume；
  >    - Safe Retry；
  >    - Storage-plane-specific Progress；
  >    - Manual Review；
  >    - Partial Failure Classification。
  > 156. 重复执行同一 Deletion Case 不得：
  >    - 扩大删除范围；
  >    - 删除新创建的合法引用；
  >    - 删除其他 Tenant 或主体数据；
  >    - 生成互相矛盾的 Tombstone；
  >    - 重复触发不可逆外部副作用。
  > 157. 每个 Storage Plane 的执行必须拥有独立状态和验证结果。
  > 158. Final Completion 必须在全部要求的 Storage Plane 完成或被明确记录为 Backup Expiry Pending 后确定。
  >
  > **3.26 PostgreSQL 删除边界**
  >
  > 159. 必须区分：
  >    - Application Inaccessibility；
  >    - Logical Database Deletion；
  >    - Physical Storage Reclamation；
  >    - Backup Expiry。
  > 160. SQL `DELETE` Commit 表示数据库事务中的逻辑删除完成。
  > 161. SQL `DELETE` Commit 不得被描述为底层所有字节立即消失。
  > 162. VACUUM、存储重用和物理空间回收属于数据库存储生命周期。
  > 163. Physical Reclamation 不等于 Backup Expiry。
  > 164. 不得为证明删除完成而执行未经风险评估的 `VACUUM FULL` 或其他高风险操作。
  >
  > **3.27 Backup 与 PITR**
  >
  > 165. Primary Store 删除后，数据可能仍存在于受控 Backup/PITR Window。
  > 166. 删除状态必须能够表达：
  >
  >    ```text
  >    PRIMARY_PURGED
  >    BACKUP_EXPIRY_PENDING
  >    BACKUP_RETENTION_COMPLETED
  >    ```
  >
  > 167. 从旧 Backup 恢复时必须：
  >    - 隔离恢复环境；
  >    - 重放已完成 Deletion Ledger；
  >    - 重新应用 Hold/Erasure 状态；
  >    - 验证已删除数据没有重新进入服务；
  >    - 完成验证后再开放流量。
  > 168. Database Restore 不得使已完成删除的数据静默复活。
  > 169. Backup/PITR 的具体周期与基础设施方案本次不决定。
  > 170. Backup Cleanup 不得由普通业务 Purge Worker直接操作。
  >
  > **3.28 Tombstone 与 Deletion Proof**
  >
  > 171. 删除后可以保留最小 Tombstone/Deletion Proof。
  > 172. 最小证明可以包含：
  >    - Deletion Case ID；
  >    - Subject Scope Hash；
  >    - Data Class；
  >    - Policy Version；
  >    - Disposition；
  >    - Completed Time；
  >    - Storage Planes Completed；
  >    - Hold/Exception Reference；
  >    - Executor Identity。
  > 173. Deletion Proof 不得包含：
  >    - 完整原始 Payload；
  >    - 被要求删除的完整 PII；
  >    - Secret；
  >    - 完整 Provider Response；
  >    - 完整 Source Content。
  > 174. Deletion Proof 必须足以证明执行范围和结果，但不得重新构成被删除数据的副本。
  >
  > **3.29 Readiness Artifact**
  >
  > 175. 在任何正式 Retention 或 Physical Purge 实现授权前，Architecture Readiness Package 必须包含：
  >
  >    ```text
  >    Data Retention, Hold & Deletion Policy Table
  >    ```
  >
  > 176. 该表至少包含：
  >    - Data Class；
  >    - Owning Module；
  >    - Authoritative/Derived；
  >    - Contains PII/Secret；
  >    - Business Purpose；
  >    - Legal/Contractual Basis；
  >    - Retention Trigger；
  >    - Retention Clock；
  >    - Minimum Required Horizon；
  >    - Maximum Permitted Horizon；
  >    - Normal Disposition；
  >    - Exceptional Erasure Action；
  >    - Reference Blockers；
  >    - Hold Types；
  >    - Archive Target；
  >    - Primary Store Deletion；
  >    - Object Store Deletion；
  >    - Index/Cache Deletion；
  >    - Checkpoint Deletion；
  >    - Backup/PITR Treatment；
  >    - Tombstone/Deletion Proof；
  >    - Verification Owner；
  >    - Related DQ/DEC/RFC。
  > 177. DQ-15 接受不授权创建该表。
  > 178. DQ-15 接受不授权填写任何具体保留期限。
  > 179. DQ-15 不新增独立 Matrix。
  >
  > **3.30 Technical Spike**
  >
  > 180. DQ-15 决策归档前不要求执行 Technical Spike。
  > 181. 首个生产 Purge 实现前必须完成单独授权的：
  >
  >    ```text
  >    Retention & Deletion Safety Technical Spike
  >    ```
  >
  > 182. Spike 最低验证：
  >    - Reference-aware Eligibility；
  >    - Legal Hold 阻止删除；
  >    - Security/Incident Hold 阻止删除；
  >    - Idempotent Purge Retry；
  >    - Purge Worker Lease/Fencing；
  >    - Checkpoint Whole-thread Delete；
  >    - Pending Workflow 不被删除；
  >    - 多引用 ContentObject 保护；
  >    - Orphan Blob Grace Period；
  >    - Retrieval Index/Cache Cleanup；
  >    - Provider Payload Cleanup；
  >    - SQL Delete 与 Physical Reclamation 边界；
  >    - Backup Restore 后重放 Deletion Ledger；
  >    - Primary/Object/Index 删除步骤之间的 Crash；
  >    - Deletion Proof 不包含原敏感载荷；
  >    - 不发生跨 Tenant、跨主体或跨安全域误删。
  > 183. Spike 必须使用项目实际选定的 PostgreSQL、Object Storage、Checkpoint 和 Backup 测试环境。
  > 184. Spike 可以共享测试基础设施，但必须拥有独立验收报告。
  > 185. 本次接受不授权创建 Spike Issue、Branch、PR、代码、测试或基础设施。
  > 186. Retention & Deletion Safety Technical Spike = REQUIRED / NOT AUTHORIZED。
  >
  > **3.31 授权边界**
  >
  > 187. DQ-15 只授权决策归档与文档同步。
  > 188. DQ-15 不授权创建：
  >    - Retention Policy Registry；
  >    - Data Retention Policy Table；
  >    - Deletion/Erasure Case；
  >    - Hold Registry；
  >    - Purge Worker；
  >    - Deletion Ledger；
  >    - Tombstone；
  >    - Retention Job；
  >    - Object Lifecycle Rule；
  >    - Checkpoint Cleanup Job；
  >    - Backup Cleanup；
  >    - Database DDL；
  >    - Migration；
  >    - Tests；
  >    - Infrastructure。
  > 189. DQ-15 不授权设置具体保留期限。
  > 190. DQ-15 不授权执行任何数据删除。
  > 191. DQ-15 不授权接受 DQ-16 或 DQ-17。

---

## DQ-16：Persistence Testing Strategy（持久化测试策略）

- **Question：** 用真实 DB 还是 SQLite fake 验证持久化语义？contract / transaction / concurrency / migration / idempotency 测试如何分层？
- **Why：** Spike 用单线程 SQLite，并发/分布式未验证（R-1）；**并发语义在 SQLite 与 PG 间不可移植**（官方推断），测试在 SQLite 通过不代表 PG 行为一致。
- **Constraints（[DEC 约束]）：** 架构基线 §14.9 测试基线；DEC-022 并发需真实验证。
- **[官方能力]：** SQLite 全库单写者 vs PG 行级 MVCC + 40001/死锁重试路径——并发行为差异大；SQLAlchemy sync/async 两条 stack。
- **Candidates：**
  - **A. 单元/契约用 SQLite 快速 fake + 并发/事务/迁移/幂等用语义等价真实 DB（PG）**。
  - **B. 全部真实 PG**：最可信但慢/重。
  - **C. 全部 SQLite fake**：快但并发语义失真。
- **Trade-offs：** A 平衡速度与真实性；B 最可信但 CI 重；C 掩盖并发缺陷。
- **Failure modes：** 全 SQLite→并发缺陷流入生产；迁移测试缺→schema 演进回归。
- **Impact on later RFCs：** 全部（测试基建）。
- **Recommendation：** **[架构推断] 倾向 A**——快速 fake 跑单元/契约，真实目标引擎跑并发/事务/迁移/幂等语义（填 R-1 GAP）。**置信度：中-高**。（**历史提案；Superseded by the Accepted Major Revision below。**）
- **Candidate 处置（2026-08-03 用户正式决定）：** Candidate A = **ACCEPTED WITH MAJOR REVISION**（Accepted Principle = Layered Test Strategy；Formal Model = Pure Domain/Application Unit Tests + Port Contract Parity Tests + Real PostgreSQL Persistence Acceptance Tests + Deterministic Multi-connection Concurrency Tests + Real Migration/Upgrade/Recovery Tests + Crash-window/Fault-injection Tests + Production-topology-specific Qualification；SQLite = OPTIONAL NON-AUTHORITATIVE TEST DOUBLE；SQLite as Persistence Acceptance Engine = PROHIBITED）；Candidate B = **REJECTED AS A UNIVERSAL ALL-TESTS-USE-POSTGRESQL POLICY**；Candidate C = **REJECTED**（All-SQLite testing cannot prove PostgreSQL semantics）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-03 用户正式决定）：**

  > **3.1 正式模型**
  >
  > 1. MVP 采用以下分层测试模型：
  >
  >    ```text
  >    PURE DOMAIN / APPLICATION UNIT TESTS
  >    + PORT CONTRACT PARITY TESTS
  >    + REAL POSTGRESQL PERSISTENCE ACCEPTANCE TESTS
  >    + DETERMINISTIC MULTI-CONNECTION CONCURRENCY TESTS
  >    + REAL MIGRATION / UPGRADE / RECOVERY TESTS
  >    + CRASH-WINDOW / FAULT-INJECTION TESTS
  >    + PRODUCTION-TOPOLOGY-SPECIFIC QUALIFICATION
  >    ```
  >
  > **3.2 Pure Domain 与 Application 测试边界**
  >
  > 2. Pure Domain Unit Test 不使用数据库。
  > 3. Application Use-case Test 可以使用：
  >    - In-memory Fake；
  >    - Stub；
  >    - Spy；
  >    - Deterministic Clock；
  >    - Deterministic ID Generator。
  > 4. Application Test Double 只能证明 Application Contract，不得证明：
  >    - SQL Constraint；
  >    - Transaction Atomicity；
  >    - Commit Visibility；
  >    - PostgreSQL Lock；
  >    - MVCC；
  >    - CAS；
  >    - Migration；
  >    - Idempotency；
  >    - Crash Recovery。
  >
  > **3.3 SQLite 边界**
  >
  > 5. SQLite 仅为可选、非权威开发 Test Double。
  > 6. SQLite 不得作为：
  >    - Persistence Contract；
  >    - Persistence Acceptance Engine；
  >    - Concurrency Proof；
  >    - Transaction Proof；
  >    - Migration Proof；
  >    - Idempotency Proof；
  >    - Release Readiness Evidence。
  >
  > **3.4 真实 PostgreSQL 验收范围**
  >
  > 7. 以下正式持久化测试必须使用真实 PostgreSQL：
  >    - Repository；
  >    - UnitOfWork；
  >    - ORM Mapping；
  >    - PostgreSQL Types；
  >    - Constraint；
  >    - Transaction；
  >    - Commit/Rollback；
  >    - Concurrency；
  >    - CAS；
  >    - Migration；
  >    - Idempotency；
  >    - Lease/Fencing；
  >    - Durable Work Intent；
  >    - Outbox；
  >    - Audit；
  >    - Domain Version；
  >    - Current Truth Pointer；
  >    - Retention Referential Safety。
  > 8. SQLite Test 通过不得被描述为 PostgreSQL 语义通过。
  >
  > **3.5 Port Contract Parity**
  >
  > 9. 每个 Persistence Port 应具有可复用 Contract Suite。
  > 10. 同一 Contract Suite 可以运行于 In-memory Test Double 和 PostgreSQL Adapter，但：
  >
  >    ```text
  >    Fake Pass =
  >    Test Double 符合 Application 可观察契约
  >
  >    PostgreSQL Adapter Pass =
  >    正式 Persistence Adapter 符合持久化契约
  >    ```
  >
  > 11. Fake 通过不得替代 PostgreSQL Adapter 通过。
  > 12. 每个 Test Double 必须明确声明：
  >    - Supported Contract；
  >    - Unsupported Semantics；
  >    - Transaction Model；
  >    - Concurrency Model；
  >    - Error Model；
  >    - Time Model；
  >    - ID Model；
  >    - Cleanup Strategy；
  >    - 与 PostgreSQL 的差异。
  >
  > **3.6 MVP Persistence Stack**
  >
  > 13. MVP 只测试已接受的正式持久化 Stack：
  >
  >    ```text
  >    SQLAlchemy 2.x Synchronous API
  >    + Psycopg 3 Synchronous Driver
  >    ```
  >
  > 14. Async SQLAlchemy、Async Psycopg 或 Asyncpg 不属于 MVP Persistence Acceptance Scope。
  > 15. 未来引入 Async Stack 必须作为新的架构和兼容性决定处理。
  >
  > **3.7 测试环境与证据元数据**
  >
  > 16. 正式测试环境必须使用项目钉定版本的：
  >    - PostgreSQL；
  >    - SQLAlchemy；
  >    - Psycopg；
  >    - Alembic。
  > 17. 正式测试环境必须：
  >    - 使用独立 Test Role；
  >    - 使用隔离 Database 或 Schema；
  >    - 不连接 Shared Development Database；
  >    - 不连接 Production Database；
  >    - 不使用生产数据；
  >    - 不使用真实 Secret；
  >    - 应用正式 Alembic Migration；
  >    - 使用正式默认 Isolation Level。
  > 18. 测试证据必须记录：
  >    - PostgreSQL Version；
  >    - SQLAlchemy Version；
  >    - Psycopg Version；
  >    - Alembic Head；
  >    - Application Commit SHA；
  >    - Isolation Level；
  >    - Worker Count；
  >    - Connection Count；
  >    - Pool/Pooler Mode；
  >    - Test Seed。
  >
  > **3.8 事务 Fixture 边界**
  >
  > 19. 单连接且不验证真实 Commit Visibility 的 Adapter Test，可以使用：
  >
  >    ```text
  >    External Transaction
  >    + SAVEPOINT
  >    + Test-end Rollback
  >    ```
  >
  > 20. 以下测试必须执行真实 Commit：
  >    - Multi-connection；
  >    - Commit Visibility；
  >    - Outbox；
  >    - Consumer；
  >    - Connection Pool；
  >    - Deadlock；
  >    - Serialization Retry；
  >    - Worker Crash；
  >    - Migration；
  >    - Multi-worker Claim；
  >    - Checkpoint；
  >    - 跨存储 Crash Window。
  > 21. 多连接测试不得被一个永不提交的外层事务包裹。
  > 22. 并行 CI Worker 必须拥有独立 Database、Schema、Namespace 或等价隔离。
  >
  > **3.9 确定性并发测试**
  >
  > 23. 并发 Actor 必须使用独立：
  >    - Connection；
  >    - Session；
  >    - Transaction。
  > 24. 不得在多个 Actor 间共享同一 SQLAlchemy Session。
  > 25. 并发测试必须使用：
  >    - Barrier；
  >    - Latch；
  >    - Event；
  >    - 明确 Blocking Point；
  >    - 可观测 Transaction State；
  >    - 受控 Worker Coordination。
  > 26. 并发测试不得主要依赖 `sleep`。
  > 27. 并发测试必须验证：
  >    - 成功 Actor；
  >    - 冲突 Actor；
  >    - 项目错误；
  >    - 真实 SQLSTATE；
  >    - Retry Count；
  >    - Final Business Current Truth；
  >    - 无部分写入；
  >    - 无孤立 Domain Version；
  >    - 无重复 Work Intent；
  >    - 无重复业务效果。
  > 28. Deadlock Test 不得固定断言特定 Worker 必须被终止；应验证一个事务被中止且最终业务不变量成立。
  > 29. 必须真实覆盖：
  >    - 相同 `expected_revision` 竞争；
  >    - CAS 一个成功、一个冲突；
  >    - Version Number 并发分配；
  >    - 命名唯一约束竞争；
  >    - SQLSTATE `40001`；
  >    - SQLSTATE `40P01`；
  >    - 最多三次 Transaction 总尝试；
  >    - Retry 复用同一 Command Identity；
  >    - Retry 不产生额外 Domain Version；
  >    - Work Intent 并发 Claim；
  >    - `SKIP LOCKED` 不重复 Claim；
  >    - Lease Expiry 与 Takeover；
  >    - Stale Fencing Token 无法提交；
  >    - 相同 Idempotency Key + 相同 Fingerprint；
  >    - 相同 Key + 不同 Fingerprint；
  >    - Outbox/Consumer Duplicate Delivery；
  >    - Promotion/Invalidation 竞争；
  >    - Restore/New Write 竞争；
  >    - Purge/New Reference 竞争。
  >
  > **3.10 Atomic Commit Fault Injection**
  >
  > 30. 每个 DEC-035 Atomic Business Commit 必须通过 Fault Injection 验证全有或全无。
  > 31. 至少在以下位置注入失败：
  >    - First Write 前；
  >    - Domain Version Insert 后；
  >    - Current Truth Pointer Update 后；
  >    - Evidence Link 后；
  >    - Audit 后；
  >    - Idempotency Result 后；
  >    - Integration Event Outbox 后；
  >    - Durable Work Intent 后；
  >    - Commit 前；
  >    - Commit/Connection Outcome 不确定时。
  > 32. 必须验证不存在：
  >    - 业务成功但 Audit 缺失；
  >    - 业务失败但 Work Intent 可领取；
  >    - 事务失败但 Outbox 可发布；
  >    - CAS 冲突后部分记录保留；
  >    - Retry 产生重复正式版本。
  > 33. Commit Outcome Unknown 不得只通过 Mock `session.commit()` 抛异常验证。
  > 34. Crash/Failure Test 应覆盖真实或语义等价的：
  >    - Connection Termination；
  >    - Process Kill；
  >    - Timeout；
  >    - Deadlock；
  >    - Serialization Failure；
  >    - Partial External Success。
  >
  > **3.11 Crash Window 覆盖**
  >
  > 35. 必须覆盖以下 Crash Window：
  >    - Business Commit 成功、Checkpoint 写入失败；
  >    - Checkpoint 成功、Business Commit 失败；
  >    - Blob Upload 成功、Database Finalization 失败；
  >    - Database 引用未验证 Blob；
  >    - Provider Side Effect 成功、本地记录失败；
  >    - Work Intent Claim 后 Worker Crash；
  >    - Outbox Publish 后状态更新前 Crash；
  >    - Primary Purge 成功、Object/Index 删除前 Crash；
  >    - Backup Restore 后 Deletion Ledger 未重放。
  >
  > **3.12 幂等覆盖**
  >
  > 36. 每个 Idempotent Use Case 至少覆盖：
  >    - First Execution；
  >    - Exact Replay；
  >    - Concurrent Exact Replay；
  >    - Same Key Different Fingerprint；
  >    - Transient Failure Retry；
  >    - Permanent Failure；
  >    - Commit Outcome Unknown；
  >    - Intentional Rerun；
  >    - Retention Window Closed。
  > 37. 必须验证：
  >    - Replay 返回同一正式结果；
  >    - Provider 不被重复调用；
  >    - 不产生第二个 Business Version；
  >    - 不重复写 Audit；
  >    - 不重复创建 Work Intent；
  >    - Fingerprint Conflict 明确失败；
  >    - Intentional Rerun 使用新身份；
  >    - Retry 与 Rerun 保持不同语义。
  >
  > **3.13 迁移覆盖**
  >
  > 38. Migration Test 必须使用真实 PostgreSQL。
  > 39. Migration Test 至少覆盖：
  >    - Fresh Database → Head；
  >    - Supported Release Baseline → Head；
  >    - Single Head；
  >    - Multiple Head Detection；
  >    - Drift Detection；
  >    - Vendor Schema Exclusion；
  >    - Old Application + Expanded Schema；
  >    - New Application + Expanded Schema；
  >    - Application Rollback + Expanded Schema；
  >    - Backfill Pause/Resume；
  >    - Backfill Idempotency；
  >    - `NOT VALID` / `VALIDATE`；
  >    - Concurrent Index Failure；
  >    - Invalid Index Cleanup；
  >    - Forward Repair；
  >    - Destructive Gate；
  >    - Contract 在旧实例存在时被阻止。
  > 40. `metadata.create_all()` 不得作为 Migration Acceptance 的唯一 Schema 来源。
  >
  > **3.14 PR Required 与 Scheduled Tier**
  >
  > 41. Required PR Checks 必须包含 correctness-critical 的：
  >    - PostgreSQL Transaction；
  >    - Constraint；
  >    - Concurrency；
  >    - Idempotency；
  >    - Migration。
  > 42. 以下测试可以进入 Scheduled/Manual Tier：
  >    - 高强度 Contention；
  >    - 长时间 Recovery；
  >    - Live Provider；
  >    - Backup Restore；
  >    - Performance；
  >    - 长周期 Soak Test。
  > 43. Correctness-critical Invariant 不得只在 Scheduled/Nightly Test 中验证。
  >
  > **3.15 Flaky Test 政策**
  >
  > 44. 禁止通过自动重跑将 Flaky Persistence Test 变绿。
  > 45. 必须区分：
  >
  >    ```text
  >    Application Retry Under Test
  >    ≠
  >    CI Test Retry
  >    ```
  >
  > 46. 基础设施启动失败可以有限重试，但：
  >    - 业务断言失败；
  >    - 并发结果不稳定；
  >    - Timeout；
  >    - SQLSTATE 异常；
  >    - 最终行状态错误；
  >    不得被自动 Retry 掩盖。
  > 47. Flaky Required Check 应视为测试或架构缺陷。
  > 48. 并发失败报告必须包含：
  >    - Seed；
  >    - Actor Timeline；
  >    - Transaction Identity；
  >    - SQLSTATE；
  >    - Retry Count；
  >    - Final Rows；
  >    - Lock/Timeout Diagnostic。
  >
  > **3.16 合成/敏感测试数据**
  >
  > 49. 测试数据必须：
  >    - 使用合成数据；
  >    - 不含生产 PII；
  >    - 不含真实 Credential；
  >    - 不含真实 Provider Token；
  >    - 不复制真实 Checkpoint；
  >    - 不复制真实 Prompt/Provider Payload；
  >    - 使用受控 Secret Injection；
  >    - 失败日志执行 Redaction。
  > 50. 精确 Sensitive Test Fixture 规则继续由 DQ-17 决定。
  >
  > **3.17 Readiness Artifact**
  >
  > 51. Architecture Readiness Package 必须包含：
  >
  >    ```text
  >    Persistence Test Coverage & Fidelity Table
  >    ```
  >
  > 52. 该表至少包括：
  >    - Requirement/Invariant；
  >    - Owning DQ/DEC/RFC；
  >    - Test Layer；
  >    - Test Subject；
  >    - Real PostgreSQL Required；
  >    - Connection Count；
  >    - Process/Worker Count；
  >    - Isolation Level；
  >    - Fixture Strategy；
  >    - Commit Visibility Required；
  >    - Expected SQLSTATE；
  >    - Fault Injection；
  >    - External Dependency；
  >    - Cleanup Strategy；
  >    - CI Tier；
  >    - Required/Optional；
  >    - Evidence Produced；
  >    - Owner。
  > 53. DQ-16 接受不授权创建该表。
  >
  > **3.18 Technical Spike 与 Common Harness**
  >
  > 54. DQ-16 不新增独立通用 Technical Spike。
  > 55. 已有专项 Spike 继续有效：
  >    - PostgreSQL Concurrency；
  >    - External Object Consistency；
  >    - Workflow Checkpoint Isolation；
  >    - Schema Migration Rollout；
  >    - Retention & Deletion Safety。
  > 56. 上述 Spike 必须共享合格的真实 PostgreSQL Test Harness 原则：
  >    - 真实 PostgreSQL；
  >    - 钉定版本；
  >    - 确定性协调；
  >    - 环境记录；
  >    - 可复核证据；
  >    - 不使用 SQLite 作为验收引擎。
  > 57. Common Persistence Test Harness Qualification 必须作为第一个获授权 Persistence Spike 的组成部分。
  > 58. 本次接受不授权创建 Harness、Container、CI Job、Fixture、Contract Suite、测试代码或基础设施。

---

## DQ-17：Security & Sensitive Data Boundary（安全与敏感数据边界）

- **Question：** Secret 与业务数据如何分离？PII 分类？加密责任？redaction？least privilege？credentials ownership？test fixture 限制？
- **Why：** RFC-001-DQ-06 确立 Secret 只注入需要的 Infrastructure Adapter、不进入 Domain/Application/Graph State/Checkpoint/Audit；须把边界落到持久化层但**不实现 Secret 管理**。
- **Constraints（[DEC 约束]）：** RFC-001-DQ-06 Secret 边界；DEC-033 Sensitive Data Boundary；Secret 不进入 Graph State / Checkpoint / Audit / Trace。
- **[官方能力]：** **LangGraph 默认宽松反序列化有 RCE 风险**，须 `LANGGRAPH_STRICT_MSGPACK=true` 白名单；**Secret 会被明文序列化进 checkpoint**（`SecretStr.get_secret_value`）；`EncryptedSerializer`/`LANGGRAPH_AES_KEY` 可用（属 RFC-003 配置）。
- **Candidates：**
  - **A. 明文敏感字段不落 checkpoint/Graph State/Audit；业务库敏感列分类 + 访问最小化；Secret 仅 Adapter 持有**。
  - **B. 应用层字段级加密**：更强但引入密钥管理（超范围）。
  - **C. 依赖 DB 静态加密**：运维层，非应用责任。
- **Trade-offs：** A 满足 DEC 边界且不引入密钥管理；B 强但超 MVP；C 是部署层补充而非应用设计。
- **Failure modes：** Secret 入 Graph State→明文落 checkpoint；PII 未分类→redaction 缺失；test fixture 含真实凭证→泄漏。
- **Impact on later RFCs：** RFC-006（LLM Secret 注入）、RFC-007（日志 redaction）。
- **Recommendation：** **[架构推断] 倾向 A**——Secret 不落持久化真值/checkpoint/审计，业务敏感列分类 + least privilege，checkpoint 反序列化白名单（与 DEC-035 一致），加密/密钥管理移交后续、本 RFC 不实现。**置信度：高**。（**历史提案；Superseded by the Accepted Major Revision below。**）
- **Candidate 处置（2026-08-03 用户正式决定）：** Candidate A = **ACCEPTED WITH MAJOR REVISION**（Formal Model = Classified Sensitive-data Protection + Secret-reference-only Persistence + Ephemeral Adapter-scoped Secret Resolution + Data-minimized Multi-plane Propagation + Strict Allowlisted Checkpoint Serialization + Least-privilege Role/Credential/Pool Separation + Selective Envelope Encryption by Protection Profile + Infrastructure Encryption in Transit/at Rest + Auditable Access/Redaction/Rotation/Incident Response）；Candidate B = **NOT SELECTED AS UNIVERSAL FIELD ENCRYPTION**（应用层字段级加密不作所有字段通用策略；SELECTIVE AUTHENTICATED ENVELOPE ENCRYPTION = CONDITIONAL ON DATA PROTECTION PROFILE）；Candidate C = **REJECTED AS SOLE SECURITY CONTROL**（Infrastructure At-rest Encryption 保留为 REQUIRED INFRASTRUCTURE DEFENSE IN DEPTH，但不替代 Application Authorization/Data Minimization/Redaction/Least Privilege/Retention/Field-level Protection）。
- **User Decision：** ACCEPTED WITH MAJOR REVISION
- **Accepted Candidate：** CANDIDATE A
- **Status：** ACCEPTED
- **Accepted Decision（2026-08-03 用户正式决定）：**

  > **3.1 正式安全模型**
  >
  > MVP 采用以下正式安全模型：
  >
  > ```text
  > CLASSIFIED SENSITIVE-DATA PROTECTION
  > + SECRET-REFERENCE-ONLY PERSISTENCE
  > + EPHEMERAL ADAPTER-SCOPED SECRET RESOLUTION
  > + DATA-MINIMIZED MULTI-PLANE PROPAGATION
  > + STRICT ALLOWLISTED CHECKPOINT SERIALIZATION
  > + LEAST-PRIVILEGE ROLE / CREDENTIAL / POOL SEPARATION
  > + SELECTIVE ENVELOPE ENCRYPTION BY PROTECTION PROFILE
  > + INFRASTRUCTURE ENCRYPTION IN TRANSIT / AT REST
  > + AUDITABLE ACCESS / REDACTION / ROTATION / INCIDENT RESPONSE
  > ```
  >
  > **3.2 Secret 与业务数据分类**
  >
  > 必须保持以下语义独立：
  >
  > ```text
  > SECRET
  > ≠
  > PII
  > ≠
  > SENSITIVE BUSINESS DATA
  > ≠
  > PUBLIC / INTERNAL BUSINESS DATA
  > ```
  >
  > 以下 Credential Value 属于 Secret，而不是可持久化业务数据：
  >    - API Key；
  >    - Access Token；
  >    - Refresh Token；
  >    - Database Password；
  >    - Private Key；
  >    - Webhook Signing Secret；
  >    - Encryption Key；
  >    - Provider Credential；
  >    - 其他能够授予系统访问能力的认证或加密材料。
  >
  > Secret Value 不得进入：
  >    - Domain；
  >    - Application Command；
  >    - Business Current Truth；
  >    - Business Version；
  >    - Graph State；
  >    - Checkpoint；
  >    - Workflow Execution Registry；
  >    - Audit；
  >    - State Transition；
  >    - Domain Event；
  >    - Application Event；
  >    - Integration Event；
  >    - Outbox；
  >    - Durable Work Intent；
  >    - Idempotency Record；
  >    - Idempotency Fingerprint；
  >    - Source；
  >    - SourceVersion；
  >    - Evidence；
  >    - Retrieval Index；
  >    - Cache；
  >    - Log；
  >    - Trace；
  >    - Metric；
  >    - Error；
  >    - Test Snapshot；
  >    - Object Key；
  >    - 其他持久化或派生存储。
  >
  > **3.3 Secret Reference 与解析边界**
  >
  > 允许持久化的只能是无明文能力的引用，例如：
  >
  > ```text
  > credential_ref
  > secret_reference_id
  > provider_account_id
  > secret_version_reference
  > credential_profile_id
  > ```
  >
  > 正式执行流程：
  >
  > ```text
  > Application selects Credential Reference
  > → Infrastructure Adapter resolves Secret ephemerally
  > → Adapter performs one authorized external interaction
  > → Adapter returns sanitized business result
  > → Secret Value is not returned to Application / Workflow / Domain
  > ```
  >
  > Application、Domain 和 Workflow 可以知道使用哪个 Credential Profile，但不得获取 Secret Value。具体 Secret Manager、KMS、Vault、HSM 或部署注入产品不由 RFC-002 决定。
  >
  > **3.4 数据分类模型**
  >
  > 敏感业务数据采用：
  >
  > ```text
  > CONFIDENTIALITY LEVEL
  > +
  > HANDLING TAGS
  > ```
  >
  > Confidentiality Level 至少包括：
  >
  > ```text
  > PUBLIC
  > INTERNAL
  > CONFIDENTIAL
  > RESTRICTED
  > ```
  >
  > Handling Tags 可以包括：
  >
  > ```text
  > PII
  > PROVIDER_PAYLOAD
  > MODEL_CONTENT
  > USER_CONTENT
  > LEGAL_HOLD
  > SECURITY_INCIDENT
  > EXPORT_RESTRICTED
  > AUTH_CREDENTIAL
  > ```
  >
  > `SECRET` 是具有独立禁止持久化规则的特殊类别，不能只当作普通 `RESTRICTED` 字段处理。每个字段或 Payload 必须明确：
  >    - Purpose；
  >    - Data Owner；
  >    - Confidentiality Level；
  >    - Handling Tags；
  >    - Authoritative Store；
  >    - Derived Stores；
  >    - Plaintext Allowed Path；
  >    - Authorized Roles；
  >    - Redaction；
  >    - Transport Encryption；
  >    - At-rest Encryption；
  >    - Field-level Encryption Requirement；
  >    - Retention；
  >    - Erasure；
  >    - Test Fixture Rule；
  >    - Incident Response。
  >
  > **3.5 多持久化平面传播**
  >
  > 数据分类和处理规则必须传播到所有适用的：
  >    - PostgreSQL；
  >    - Object Storage；
  >    - Checkpoint；
  >    - Workflow Registry；
  >    - Audit；
  >    - State Transition；
  >    - Durable Work Intent；
  >    - Integration Event Outbox；
  >    - Retrieval Index；
  >    - Cache；
  >    - Logs；
  >    - Traces；
  >    - Metrics；
  >    - Backup/PITR；
  >    - Test Fixture；
  >    - CI Artifact；
  >    - Dead-letter Record。
  >
  > 不得只对 PostgreSQL Column 做分类，却让完整敏感 Payload 无限制进入派生存储。
  >
  > **3.6 Secret Wrapper 边界**
  >
  > `SecretStr`、Masked String、隐藏 `repr()` 或类似 Wrapper 只能降低偶然显示风险。必须明确：
  >
  > ```text
  > MASKED REPRESENTATION
  > ≠
  > NON-PERSISTENCE GUARANTEE
  > ```
  >
  > 不得依赖 Wrapper 阻止 Secret 被：
  >    - 调用 `get_secret_value()`；
  >    - 转换成普通字符串；
  >    - 放入 Dictionary；
  >    - 放入 Graph State；
  >    - 被 Serializer 序列化；
  >    - 写入错误上下文；
  >    - 写入日志；
  >    - 写入 Checkpoint。
  >
  > Secret Non-persistence 必须由类型边界、架构测试、Serializer Allowlist、Sink Redaction 与禁止路径共同强制。
  >
  > **3.7 Checkpoint 严格序列化**
  >
  > LangGraph Checkpoint 必须采用严格反序列化策略：
  >
  > ```text
  > LANGGRAPH_STRICT_MSGPACK =
  > REQUIRED
  >
  > Explicit allowed_msgpack_modules Allowlist =
  > REQUIRED OR PREFERRED ACCORDING TO PINNED VERSION
  >
  > Pickle Fallback =
  > PROHIBITED
  > ```
  >
  > 不得允许：
  >    - 任意 Python Module；
  >    - 任意未登记 Class；
  >    - 任意 Pydantic Model；
  >    - 任意 Dataclass；
  >    - Pickle Fallback；
  >    - 未审查自定义对象；
  >    - 来自不可信 Checkpoint Storage 的任意类型反序列化。
  >
  > Graph State 优先使用：
  >    - String；
  >    - Integer；
  >    - Boolean；
  >    - List；
  >    - Dict；
  >    - Opaque ID；
  >    - Versioned Typed Primitive Payload。
  >
  > 恶意或损坏的 Checkpoint 必须进入：
  >    - INCOMPATIBLE；
  >    - CORRUPT；
  >    - SECURITY_REJECTED；
  >    - 或等价受控失败分类。
  >
  > 不得尝试不安全降级反序列化。
  >
  > **3.8 Checkpoint 加密边界**
  >
  > Secret Value 无论是否启用 Checkpoint Encryption，都不得进入 Graph State 或 Checkpoint。对于经分类允许持久化的敏感 Runtime State，可以采用经过验证的：
  >    - EncryptedSerializer；
  >    - 或等价加密序列化机制。
  >
  > 必须明确：
  >
  > ```text
  > ENCRYPTED CHECKPOINT
  > ≠
  > PERMISSION TO STORE SECRETS
  > ```
  >
  > 不得假设以下内容全部自动加密：
  >    - Thread ID；
  >    - Checkpoint ID；
  >    - Namespace；
  >    - Metadata；
  >    - 调度字段；
  >    - 查询索引；
  >    - Vendor Migration Metadata；
  >    - Connection Metadata。
  >
  > 实际加密范围必须基于：
  >    - 项目钉定的 LangGraph/PostgresSaver 版本；
  >    - 实际 Serializer；
  >    - 实际 PostgreSQL Schema；
  >    - 实际部署 Pool/Pooler；
  >    - 实际查询路径；
  >    进行验证。
  >
  > Encrypted Checkpoint 仍必须遵守：
  >    - 最小化；
  >    - Least Privilege；
  >    - Retention；
  >    - Whole-thread Deletion；
  >    - Incident Response；
  >    - Access Audit。
  >
  > **3.9 三层加密责任**
  >
  > **Transport Encryption：** PostgreSQL、Object Storage、Secret Provider、KMS、外部 Provider 和其他网络连接必须使用经过验证的加密传输。具体 TLS、CA、证书和部署配置由后续 Infrastructure/Deployment 决策负责。
  >
  > **Infrastructure At-rest Encryption：** 以下存储必须具备基础设施级静态加密：
  >    - PostgreSQL Volume；
  >    - Database Backup/PITR；
  >    - Object Storage；
  >    - Checkpoint Storage；
  >    - Log/Trace Storage；
  >    - 可能包含敏感数据的 CI Artifact；
  >    - 其他持久化平面。
  >
  > 正式语义：
  >
  > ```text
  > INFRASTRUCTURE ENCRYPTION AT REST =
  > REQUIRED BASELINE
  >
  > INFRASTRUCTURE ENCRYPTION AT REST =
  > NOT SUFFICIENT AS SOLE APPLICATION CONTROL
  > ```
  >
  > 它不能替代：
  >    - Application Authorization；
  >    - Data Minimization；
  >    - Redaction；
  >    - Least Privilege；
  >    - Retention；
  >    - Field-level Protection。
  >
  > **Selective Application-level Envelope Encryption：** Candidate B 不作为所有字段的通用策略。正式语义：
  >
  > ```text
  > UNIVERSAL FIELD-LEVEL ENCRYPTION =
  > REJECTED
  >
  > SELECTIVE AUTHENTICATED ENVELOPE ENCRYPTION =
  > CONDITIONAL ON DATA PROTECTION PROFILE
  > ```
  >
  > 以下威胁模型可能要求选择性应用层加密：
  >    - Database Read-only Credential 泄漏；
  >    - Backup 泄漏；
  >    - 运维人员不应读取明文；
  >    - Tenant/Security Domain 需要独立 Key；
  >    - 独立撤销；
  >    - Crypto-shredding；
  >    - 法律、合同或业务保护要求。
  >
  > **3.10 Ciphertext 与 Key 分离**
  >
  > 采用 Envelope Encryption 时，数据库可以保存：
  >    - Ciphertext；
  >    - Algorithm ID；
  >    - Key Reference；
  >    - Key Version；
  >    - Nonce/IV；
  >    - Authentication Tag；
  >    - Encrypted DEK，如适用。
  >
  > 数据库不得保存：
  >    - 明文 DEK；
  >    - 明文 KEK；
  >    - Master Encryption Key；
  >    - Secret Manager Root Credential。
  >
  > 密钥生命周期至少必须能够表达：
  >
  > ```text
  > CREATE
  > ACTIVATE
  > ROTATE
  > RETIRE
  > REVOKE
  > DESTROY
  > COMPROMISE RESPONSE
  > ```
  >
  > 必须区分：
  >    - 新写入使用新 Key；
  >    - 旧数据仍可读取；
  >    - 渐进式 Re-encryption；
  >    - 紧急 Compromise Rotation；
  >    - Backup 中旧 Key 的恢复需求；
  >    - Key Destruction 对历史数据可恢复性的影响。
  >
  > 本次不选择：
  >    - KMS；
  >    - Vault；
  >    - HSM；
  >    - 算法；
  >    - Rotation Period；
  >    - Key Hierarchy 实现。
  >
  > **3.11 禁止未经治理的加密实现**
  >
  > 不得使用未经治理的：
  >
  > ```text
  > pgcrypto raw encrypt/decrypt
  > custom AES helper
  > home-grown crypto
  > key and ciphertext in the same database
  > ```
  >
  > 字段级加密如获授权，必须采用：
  >
  > ```text
  > AUTHENTICATED ENCRYPTION
  > + EXTERNAL KEY MANAGEMENT
  > + ALGORITHM / KEY VERSION METADATA
  > + ROTATION AND RE-ENCRYPTION PLAN
  > ```
  >
  > 本次不授权创建任何 Encryption Adapter、Encrypted Column、Key Registry 或 Re-encryption Job。
  >
  > **3.12 PostgreSQL Least Privilege**
  >
  > 必须区分独立 Role/Pool：
  >
  > ```text
  > Migration Owner Role
  > Business Runtime Write Role
  > Business Read-only Role
  > Checkpoint Runtime Role
  > Dispatch / Worker Role
  > Purge Role
  > Test Role
  > Observability Role
  > ```
  >
  > Runtime Role 不得：
  >    - 是 Superuser；
  >    - 拥有 `BYPASSRLS`；
  >    - 拥有 `CREATEROLE`；
  >    - 拥有 `CREATEDB`；
  >    - 是 Business Table Owner；
  >    - 拥有任意 Business Schema DDL；
  >    - 修改 Alembic Version；
  >    - 修改其他 Persistence Plane；
  >    - 读取未授权敏感列；
  >    - 访问不属于其能力范围的 Schema。
  >
  > Business、Checkpoint、Migration、Purge、Test 与 Observability Connection/Pool 必须保持分离。Migration Credential 不得进入：
  >    - Web Runtime；
  >    - Worker Runtime；
  >    - Checkpoint Runtime；
  >    - Test Runtime；
  >    - Developer Local Config；
  >    - 普通 Application Environment。
  >
  > 应撤销不需要的 `PUBLIC` 权限，保护 `public` Schema，并采用固定、受控的 `search_path`。具体 Role、Grant 与 Schema 本次不授权创建。
  >
  > **3.13 Row-level Security**
  >
  > RLS 可以作为 Multi-tenant 场景的纵深防御，但不替代：
  >    - DQ-02 Module Ownership；
  >    - Application Authorization；
  >    - Public Application Contract；
  >    - Business Invariant；
  >    - Repository Boundary。
  >
  > 正式语义：
  >
  > ```text
  > RLS =
  > OPTIONAL DEFENSE IN DEPTH
  >
  > RLS =
  > NOT REQUIRED FOR EVERY TABLE
  > ```
  >
  > 如果未来启用 RLS，必须验证：
  >    - Runtime Role 不是 Table Owner；
  >    - Runtime Role 没有 `BYPASSRLS`；
  >    - Tenant Context 来源明确；
  >    - Pool 复用不泄漏 Tenant Context；
  >    - Worker 不绕过 Policy；
  >    - Purge、Migration、Incident Role 拥有独立策略；
  >    - 使用真实 PostgreSQL 测试。
  >
  > 本次不授权创建任何 RLS Policy。
  >
  > **3.14 Credential 与连接池分离**
  >
  > 必须保持：
  >
  > ```text
  > BUSINESS POOL
  > ≠
  > CHECKPOINT POOL
  > ≠
  > MIGRATION CONNECTION
  > ≠
  > PURGE CONNECTION
  > ≠
  > TEST CONNECTION
  > ```
  >
  > 不同能力不得共享万能数据库账号。Secret 应尽可能具有：
  >    - 短生命周期；
  >    - 动态签发；
  >    - 最小 Scope；
  >    - 可撤销；
  >    - 自动轮换；
  >    - 独立审计。
  >
  > Purge Credential 只能用于受治理的 Deletion Case，不能成为普通 Runtime Credential。
  >
  > **3.15 Redaction 顺序**
  >
  > 不得采用：
  >
  > ```text
  > Persist Full Payload
  > → Attempt Cleanup Later
  > ```
  >
  > 必须采用：
  >
  > ```text
  > CLASSIFY
  > → MINIMIZE
  > → REDACT
  > → SERIALIZE / EMIT / PERSIST
  > ```
  >
  > Redaction 必须发生在进入以下 Sink 之前：
  >    - Audit；
  >    - State Transition；
  >    - Error；
  >    - Log；
  >    - Trace；
  >    - Metric Label；
  >    - Outbox；
  >    - Durable Work Intent；
  >    - Checkpoint；
  >    - Retrieval Index；
  >    - Cache；
  >    - Dead-letter Record；
  >    - Test Failure Snapshot；
  >    - Provider Diagnostic；
  >    - CI Artifact。
  >
  > Redaction 必须优先基于结构化字段和 Data Classification。不得只依赖全局 Regex。
  >
  > **3.16 安全 Audit**
  >
  > 以下行为应生成安全 Audit Metadata：
  >    - 敏感数据读取；
  >    - 批量导出；
  >    - Decryption；
  >    - Secret Resolution；
  >    - Credential Rotation；
  >    - Key Rotation；
  >    - 权限修改；
  >    - Break-glass Access；
  >    - Deletion/Erasure；
  >    - Hold 创建与解除；
  >    - 数据分类变更；
  >    - 反序列化拒绝；
  >    - Checkpoint Integrity Failure；
  >    - Security Exception。
  >
  > Audit 应记录：
  >
  > ```text
  > actor
  > action
  > target identity
  > classification
  > purpose
  > result
  > occurred_at
  > correlation_id
  > authorization decision
  > ```
  >
  > Audit 不得记录：
  >    - Secret Value；
  >    - 明文 Key；
  >    - 完整敏感 Payload；
  >    - 完整 Decrypted Field；
  >    - 完整 Prompt；
  >    - 完整 Provider Response；
  >    - 完整 Source Content。
  >
  > 本次不授权创建 Security Audit 表或实现。
  >
  > **3.17 Provider、Prompt 与 Model Output**
  >
  > 以下输入必须被视为不可信且可能敏感：
  >    - Provider Response；
  >    - User Prompt；
  >    - Model Output；
  >    - Tool Result；
  >    - Source Content；
  >    - Provider Diagnostic。
  >
  > 它们可能包含：
  >    - PII；
  >    - 被回显 Secret；
  >    - 第三方数据；
  >    - Prompt Injection；
  >    - 临时访问 URL；
  >    - Token；
  >    - Provider Internal Metadata。
  >
  > 不得假设：
  >
  > ```text
  > MODEL-GENERATED =
  > SAFE TO PERSIST
  > ```
  >
  > 进入以下位置前必须重新分类、最小化和 Redact：
  >    - Business Version；
  >    - Source/Evidence；
  >    - Checkpoint；
  >    - Audit；
  >    - Retrieval Index；
  >    - Log/Trace；
  >    - Test Fixture。
  >
  > **3.18 Object Key 与 Content Hash**
  >
  > Object Key 不得包含：
  >    - PII；
  >    - Email；
  >    - Source URL；
  >    - Tenant Name；
  >    - 敏感原始 Filename；
  >    - Credential；
  >    - Token；
  >    - Secret；
  >    - 可直接识别主体的信息。
  >
  > Content Hash 不得：
  >    - 作为公开存在性查询接口；
  >    - 被视为匿名化证明；
  >    - 暴露给未授权调用方；
  >    - 用作 Secret Value 的普通 Idempotency Fingerprint。
  >
  > 低熵敏感内容的 Hash 可能构成存在性或 Dictionary Oracle，因此必须限制访问。需要 Blind Index、Deterministic Encryption 或可搜索加密时，必须作为独立安全设计审查。
  >
  > **3.19 跨 Tenant 与跨安全域去重**
  >
  > DQ-12 暂缓的边界在 DQ-17 正式关闭：
  >
  > ```text
  > CROSS-TENANT CONTENT DEDUPLICATION =
  > PROHIBITED FOR MVP
  >
  > CROSS-SECURITY-DOMAIN CONTENT DEDUPLICATION =
  > PROHIBITED FOR MVP
  > ```
  >
  > 同一 Tenant、同一 Security Domain 内允许的物理 ContentObject 去重仍必须满足：
  >    - 相同 Data Classification；
  >    - 相同访问域；
  >    - Retention 兼容；
  >    - Legal Hold 兼容；
  >    - 不暴露内容是否存在；
  >    - 删除一个逻辑引用不删除其他合法引用；
  >    - DQ-12 Reference Integrity；
  >    - DQ-15 Reference-aware Purge。
  >
  > **3.20 测试数据与 Secret Detection**
  >
  > 测试只能使用合成数据。禁止：
  >    - Production Database Dump；
  >    - 真实用户 PII；
  >    - 真实 API Key；
  >    - 真实 Provider Token；
  >    - Production Checkpoint；
  >    - Production Prompt/Response；
  >    - Production Encryption Key；
  >    - Production Presigned URL；
  >    - Production Credential；
  >    - 真实敏感 Source Content。
  >
  > Test Credential 必须：
  >    - 最小 Scope；
  >    - 只访问 Sandbox；
  >    - 不访问 Production；
  >    - 可自动失效；
  >    - 可立即撤销；
  >    - 不写入 Fixture Snapshot；
  >    - 不暴露给 Fork PR。
  >
  > Secret Detection Failure 必须阻止 Merge。发现 Secret 泄漏后，必须先执行：
  >
  > ```text
  > REVOKE
  > → ROTATE
  > → INVESTIGATE HISTORY / LOG / ARTIFACT EXPOSURE
  > → REMOVE OR REWRITE ONLY WHEN AUTHORIZED
  > ```
  >
  > 不得仅从最新文件删除字符串后声称问题已经解决。
  >
  > **3.21 Retention 与 Erasure 边界**
  >
  > DQ-15 继续拥有：
  >    - Retention Period；
  >    - Deletion Case；
  >    - Hold；
  >    - Purge；
  >    - Backup Expiry。
  >
  > DQ-17 决定：
  >    - Secret Value 不得因 Retention Policy 而长期持久化；
  >    - Encrypted Data 仍属于受保护数据；
  >    - Key Destruction 不得未经验证地等同于完整删除；
  >    - Redacted/Aggregated Data 是否可重识别必须重新评估；
  >    - Backup Restore 必须恢复适用 Key Version 与 Deletion Ledger；
  >    - Legal Hold 不要求保留 Secret Value；
  >    - Deletion Proof 不得保存被删除的敏感 Payload。
  >
  > **3.22 所有权边界**
  >
  > Security Governance 拥有：
  >    - Classification Vocabulary；
  >    - Handling Rules；
  >    - Cryptographic Policy；
  >    - Least-privilege Baseline；
  >    - Security Exception；
  >    - Incident Response；
  >    - Security Review Gate。
  >
  > 业务模块拥有：
  >    - 自身字段分类；
  >    - 处理目的；
  >    - 最小化；
  >    - Application Authorization；
  >    - Redaction Contract；
  >    - Retention Dependency；
  >    - Sensitive Access Audit。
  >
  > Infrastructure 拥有：
  >    - Secret Resolution Adapter；
  >    - KMS/Vault Integration；
  >    - TLS；
  >    - Volume/Backup Encryption；
  >    - PostgreSQL Role/Grant；
  >    - Connection Credential；
  >    - Encrypted Serializer Configuration；
  >    - Credential/Key Rotation Execution。
  >
  > 后续边界：
  >
  > ```text
  > RFC-003 =
  > Graph State / Checkpoint Runtime Configuration
  >
  > RFC-004 =
  > API Authentication / Authorization / Transport
  >
  > RFC-006 =
  > LLM and Provider Secret Injection
  >
  > RFC-007 =
  > Logging / Trace Redaction / Security Monitoring
  >
  > DQ-15 =
  > Retention / Erasure / Backup Expiry
  > ```
  >
  > **3.23 Readiness Artifact**
  >
  > Architecture Readiness Package 必须包含：
  >
  > ```text
  > Sensitive Data, Secret & Cryptographic Control Matrix
  > ```
  >
  > 该 Matrix 至少包含：
  >    - Data Element；
  >    - Owning Module；
  >    - Confidentiality Level；
  >    - Handling Tags；
  >    - Purpose；
  >    - Secret or Business Data；
  >    - Authoritative Store；
  >    - Derived Stores；
  >    - Plaintext Allowed；
  >    - Graph State Allowed；
  >    - Checkpoint Allowed；
  >    - Audit Allowed；
  >    - Outbox/Work Intent Allowed；
  >    - Index/Cache Allowed；
  >    - Object Store Allowed；
  >    - Backup Allowed；
  >    - Required Redaction；
  >    - Transport Encryption；
  >    - Infrastructure At-rest Encryption；
  >    - Field-level Encryption；
  >    - Key Owner/Reference；
  >    - Authorized Roles；
  >    - Retention/Erasure；
  >    - Test Fixture Rule；
  >    - Incident Response；
  >    - Related DQ/DEC/RFC。
  >
  > 正式状态：
  >
  > ```text
  > Sensitive Data, Secret & Cryptographic Control Matrix =
  > REQUIRED / NOT AUTHORIZED
  > ```
  >
  > 本次接受不授权创建该 Matrix。
  >
  > **3.24 Security Qualification 与 Spike**
  >
  > DQ-17 不新增覆盖所有系统的独立通用 Technical Spike。
  >
  > ```text
  > New Independent DQ-17 Technical Spike =
  > NOT REQUIRED
  > ```
  >
  > 必须将 Cross-cutting Persistence Security Qualification 加入首个获授权的：
  >    - PostgreSQL Concurrency Spike；
  >    - External Object Consistency Spike；
  >    - Workflow Checkpoint Isolation Spike；
  >    - Schema Migration Rollout Spike；
  >    - Retention Safety Spike；
  >    - Common Persistence Test Harness Qualification。
  >
  > 最低安全验证包括：
  >    - Strict Msgpack Allowlist；
  >    - Pickle Disabled；
  >    - Malicious Checkpoint 不触发任意代码；
  >    - Secret 不进入 Checkpoint；
  >    - Secret 不进入 Audit；
  >    - Secret 不进入 Log；
  >    - Secret 不进入 Outbox/Work Intent；
  >    - EncryptedSerializer 实际范围；
  >    - PostgreSQL Role Denial；
  >    - Runtime Role 非 Owner/Superuser/BYPASSRLS；
  >    - Schema/Search Path 安全；
  >    - Object Key 无敏感值；
  >    - Cross-tenant/Security-domain Dedup 被拒绝；
  >    - Redaction；
  >    - Synthetic Fixture；
  >    - Secret Scan；
  >    - Backup/Key Version Recovery。
  >
  > 正式状态：
  >
  > ```text
  > Cross-cutting Persistence Security Qualification =
  > REQUIRED IN FIRST AUTHORIZED PERSISTENCE SPIKES
  > NOT AUTHORIZED
  > ```
  >
  > 如果未来选择 Application-level Field Encryption，则必须单独授权：
  >
  > ```text
  > Selective Field Encryption & Key Rotation Spike =
  > CONDITIONALLY REQUIRED
  > NOT AUTHORIZED
  > ```
  >
  > **3.25 候选处置**
  >
  > Candidate A = ACCEPTED WITH MAJOR REVISION（Formal Model = CLASSIFIED SENSITIVE-DATA PROTECTION + SECRET-REFERENCE-ONLY PERSISTENCE + EPHEMERAL ADAPTER-SCOPED SECRET RESOLUTION + DATA-MINIMIZED MULTI-PLANE PROPAGATION + STRICT ALLOWLISTED CHECKPOINT SERIALIZATION + LEAST-PRIVILEGE ROLE / CREDENTIAL / POOL SEPARATION + SELECTIVE ENVELOPE ENCRYPTION BY PROTECTION PROFILE + INFRASTRUCTURE ENCRYPTION IN TRANSIT / AT REST + AUDITABLE ACCESS / REDACTION / ROTATION / INCIDENT RESPONSE）；Candidate B = NOT SELECTED AS UNIVERSAL FIELD ENCRYPTION，CONDITIONALLY REQUIRED BY DATA PROTECTION PROFILE；Candidate C = REJECTED AS SOLE SECURITY CONTROL，RETAINED AS REQUIRED INFRASTRUCTURE DEFENSE IN DEPTH。

---

## 汇总：待用户逐项决定（DQ-01~17 ACCEPTED；全部 DQ 已决定）

```text
RFC-002-DQ-01  Primary Persistence Technology        = ACCEPTED (Candidate A, Accepted with Revision, 2026-08-01) — User Decision: ACCEPTED WITH REVISION
RFC-002-DQ-02  Persistence Ownership / Boundaries    = ACCEPTED (Candidate A, Accepted with Revision, 2026-08-01) — User Decision: ACCEPTED WITH REVISION
RFC-002-DQ-03  Aggregate / Persistence Boundary      = ACCEPTED (Candidate A, Accepted with Revision, 2026-08-02) — User Decision: ACCEPTED WITH REVISION
RFC-002-DQ-04  Domain State Versioning               = ACCEPTED (Candidate A, Accepted with Revision, 2026-08-02) — User Decision: ACCEPTED WITH REVISION
RFC-002-DQ-05  Transaction Boundary                  = ACCEPTED (Candidate A, Accepted with Revision, 2026-08-02) — User Decision: ACCEPTED WITH REVISION
RFC-002-DQ-06  Unit of Work Model                    = ACCEPTED (Candidate A, Accepted with Revision, 2026-08-02) — User Decision: ACCEPTED WITH REVISION
RFC-002-DQ-07  Concurrency Control                   = ACCEPTED (Accepted Direction: Layered Concurrency Control, Accepted with Revision, 2026-08-02) — User Decision: ACCEPTED WITH REVISION
RFC-002-DQ-08  Idempotency Model                     = ACCEPTED (Primary Direction: Candidate B, Supporting Principle: Candidate C, Accepted with Major Revision, 2026-08-02) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-09  Transactional Outbox / Dispatch       = ACCEPTED (Candidate B, Formal Pattern: PostgreSQL-backed Transactional Durable Work Intent, Accepted with Major Revision, 2026-08-02) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-10  Event & Audit Persistence             = ACCEPTED (Candidate A, Six Independent Event/Record Semantics, Append-only Audit in Same Atomic Commit, Transactional Integration Event Outbox, Accepted with Major Revision, 2026-08-02) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-11  Snapshot vs History                   = ACCEPTED (Candidate A, Formal Model: Authoritative Current Truth + Immutable Business Version Snapshots + Append-only Audit/State Transition History + Optional Derived Query Projections, Full Event Sourcing / Current-state-only Overwrite / Delta-only Authoritative History Rejected, Accepted with Major Revision, 2026-08-02) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-12  Source & Evidence Persistence         = ACCEPTED (Candidate A, Formal Model: PostgreSQL Authoritative Source/Evidence Graph + Immutable Content-addressed Source Blobs + Versioned Derived Artifacts and Fragments + Explicit Evidence-to-Claim Links + Rebuildable Non-authoritative Retrieval Index, Universal All-in-PostgreSQL / Universal All-in-Object-Storage Rejected, Accepted with Major Revision, 2026-08-02) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-13  Workflow Checkpoint Separation        = ACCEPTED (Candidate A, Formal Model: Shared PostgreSQL Service + Isolated Checkpoint Persistence Plane + Dedicated Role/Connection Pool/Storage Namespace + Application-owned Workflow Execution Registry + Business-Current-Truth-first Reconciliation, Dedicated Schema Must Be Proven / Dedicated Database Fallback, Independent PostgreSQL Service Not Selected / Shared-Table Rejected, Accepted with Major Revision, 2026-08-02) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-14  Schema Evolution & Migrations         = ACCEPTED (Candidate A, Formal Model: Alembic-managed Business Schema Migrations + Single Business Migration Lineage + Forward-recovery-first Production Policy + Expand-Migrate-Contract Rolling Compatibility + Resumable Application-owned Data Backfills + Explicit Destructive/Non-transactional DDL Gates + Separate Vendor Migration Lifecycles, Universal Safe Downgrade Rejected / Sole Hand-written SQL Rejected, Accepted with Major Revision, 2026-08-03) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-15  Data Retention & Deletion Boundary    = ACCEPTED (Candidate A, Formal Model: Classified Retention & Disposition Policies + Purpose/Legal-basis-driven Retention Clocks + Reference-aware Deletion Eligibility + Legal/Security/Incident Hold Overrides + Normal-lifecycle Immutability for Business History + Governed Exceptional Erasure/Redaction Paths + Idempotent Auditable Purge Orchestration + Separate Primary/Object/Index/Checkpoint/Backup Lifecycles, Universal TTL / Universal Permanent Retention Rejected, Specific Retention Periods Not Decided, Accepted with Major Revision, 2026-08-03) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-16  Persistence Testing Strategy           = ACCEPTED (Candidate A, Accepted Principle: Layered Test Strategy, Formal Model: Pure Domain/Application Unit Tests + Port Contract Parity Tests + Real PostgreSQL Persistence Acceptance Tests + Deterministic Multi-connection Concurrency Tests + Real Migration/Upgrade/Recovery Tests + Crash-window/Fault-injection Tests + Production-topology-specific Qualification, Universal All-Tests-Use-PostgreSQL / All-SQLite Testing Rejected, SQLite = Optional Non-authoritative Test Double Only, Accepted with Major Revision, 2026-08-03) — User Decision: ACCEPTED WITH MAJOR REVISION
RFC-002-DQ-17  Security & Sensitive Data Boundary    = ACCEPTED (Candidate A, Formal Model: Classified Sensitive-data Protection + Secret-reference-only Persistence + Ephemeral Adapter-scoped Secret Resolution + Data-minimized Multi-plane Propagation + Strict Allowlisted Checkpoint Serialization + Least-privilege Role/Credential/Pool Separation + Selective Envelope Encryption by Protection Profile + Infrastructure Encryption in Transit/at Rest + Auditable Access/Redaction/Rotation/Incident Response, Candidate B Not Selected as Universal Field Encryption (Conditional by Data Protection Profile), Candidate C Rejected as Sole Security Control (Retained as Required Infrastructure Defense in Depth), Accepted with Major Revision, 2026-08-03) — User Decision: ACCEPTED WITH MAJOR REVISION

Pending Decision Questions               = 0
All Decision Questions Completed         = YES
RFC-002 Final Acceptance                 = ACCEPTED（2026-08-04 用户正式决定；接受依据与授权边界见 RFC 主文档 §33 Decision Log 2026-08-04 Final Decision 记录；Acceptance ≠ Authorization，Implementation = NOT AUTHORIZED）
Implementation                           = NOT AUTHORIZED
```
