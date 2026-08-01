# RFC-002 Supporting Research：持久化需求矩阵（Persistence Requirements Matrix）

> **Status:** SUPPORTING EVIDENCE（研究工件，非 Accepted Decision）
> **服务 RFC：** RFC-002 — Persistence and Transaction Architecture
> **来源层：** 全部提取自已 Accepted 的 DEC（DEC-012/013/014/022/023/024/025/029/032/033/034/035）、RFC-001（ACCEPTED）、Architecture Baseline v1、Current Specs、Spike-001 证据。
> **纪律：** 本文件**只**汇总与分类**已接受的**持久化/事务需求与**已明确留白**的开放点；**不**替用户做任何技术选型。凡属 RFC-002 待决项，一律标注 `→ RFC-002-DQ-xx（PENDING）`。
> **Synchronization Note（2026-08-01）：** RFC-002-DQ-01 已由用户正式决定（**ACCEPTED，Accepted with Revision**）：PostgreSQL 是唯一受支持的权威数据库语义；技术栈 = PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic；本地开发与正式持久化测试使用真实 PostgreSQL；SQLite-first → PostgreSQL-later 路线 REJECTED。RFC-002-DQ-02 已由用户正式决定（**ACCEPTED，Accepted with Revision**）：MVP 单一 PostgreSQL 服务；每张业务表唯一所有模块；ORM/Repository/Migration/状态修改 Use Case 模块私有；跨模块仅经 Public Application Contract；Direct SQL/ORM/Repository 跨模块访问禁止；架构测试强制；每模块独立 PostgreSQL schema 暂缓、物理命名留待实现设计；三类存储物理划分继续归 DQ-13。RFC-002-DQ-03 已由用户正式决定（**ACCEPTED，Accepted with Revision**，2026-08-02）：聚合边界 = 业务不变量 + 唯一模块所有权；Atomic Business Commit（DEC-035 六要素）是事务提交协议、非聚合成员资格判据（六要素单事务保持有效）；Task Mega Aggregate REJECTED；默认一 Use Case 一主 Aggregate；跨聚合/跨模块显式协调；UoW/事务实现形态移交 DQ-05/06；Aggregate/Invariant Matrix 持久化实施前必备。RFC-002-DQ-04 已由用户正式决定（**ACCEPTED，Accepted with Revision**，2026-08-02）：Domain Version Identity（`domain_version_id`，Application 层 INSERT 前生成、opaque UUID、不可变不复用）、Domain Version Number（`version_number`，逻辑对象内单调递增、`(logical_object_id, version_number)` 唯一性约束、不复用）与 Concurrency Revision（受保护可变记录独立 NOT NULL 乐观并发 token）明确分离；状态修改 Command 携带 `expected_revision`，compare-and-swap 条件更新、零影响行 = 冲突且 Atomic Business Commit 整体回滚；SQLAlchemy `version_id_col` 仅为 Infrastructure 机制（`StaleDataError` 等翻译为项目自有冲突语义，mapper/Session 细节不泄漏进 Domain/Public Contract）；PostgreSQL `xmin` 不作权威业务 revision（Candidate B REJECTED）；SERIALIZABLE 不替代显式 revision（Candidate C REJECTED，仍可作为独立隔离策略由后续 DQ 讨论）；隔离级别与重试策略移交 DQ-05/DQ-07（PROPOSED/PENDING）；DEC-035 六要素保持同一事务；RFC-004 可将 revision 映射 ETag/If-Match（HTTP 协议不由 DQ-04 决定）；正式持久化测试使用真实 PostgreSQL（详细测试策略归 DQ-16）。RFC-002-DQ-05 已由用户正式决定（**ACCEPTED，Accepted with Revision**，2026-08-02）：Business Transaction Owner = Application（Entrypoint / Graph Node 不 begin/commit）；Transactional Application Command = 一个短显式事务 + 一个最终提交点；长流程业务操作 = 多个短事务 + 无事务执行阶段；执行模式 Prepare → Execute Outside Transaction → Commit；四项 PROHIBITED（外部调用持有开放事务、Human Review 跨开放事务、Workflow 暂停跨开放事务、SQLAlchemy Session 跨 Workflow 边界）；Commit-time Revision Revalidation 必选（衔接 DQ-04 `expected_revision` 协议）；DEC-035 六要素单事务保持有效；External Result Before Commit 非 Current Truth；默认 PostgreSQL 隔离级别 = READ COMMITTED（DQ-04 遗留的「默认隔离级别」留白由此决定）；更强隔离级别、锁、SELECT FOR UPDATE / SKIP LOCKED、40001 / 40P01 重试与重试上限仍由 DQ-07 拥有；SAVEPOINT 仅为有限 Infrastructure 机制；嵌套业务事务禁止；与外部供应商的分布式事务拒绝；UoW Port 形态仍由 DQ-06 拥有。RFC-002-DQ-06 已由用户正式决定（**ACCEPTED，Accepted with Revision**，2026-08-02）：UnitOfWork Port 由 Application 层定义、生产 UnitOfWork 实现属于 Infrastructure 层（可使用 SQLAlchemy）；SQLAlchemy Session 是 Infrastructure 实现细节，不暴露给 Domain/Application/Entrypoint/API handler/LangGraph node/Workflow adapter/Public Application Contract/外部 Provider adapter；每个 Transactional Application Command 创建一个新的 UnitOfWork 实例；一个 UoW 对应一个短数据库事务、一个 SQLAlchemy Session、一个显式业务状态迁移、一个最终 commit 或 rollback 结果；UoW 是一次性生命周期对象（NEW → ACTIVE → COMMITTED/ROLLED_BACK → CLOSED），commit/rollback/close 后不得重用；Application Use Case 必须显式调用 commit()，正常 context-manager 退出不得自动提交；未成功 commit 退出或异常退出必须 rollback、close、discard（释放连接、UoW 不可用、原始失败在 Application 错误边界保留或翻译）；每个 Transactional Command 最多成功 commit 一次，非法生命周期操作显式失败；UoW 仅暴露显式类型化 Repository Ports，禁止 get_repository(name)/registry/Service Locator/raw Session accessor/通用 execute_sql()/动态 Repository 解析；Repository 模块所有权与 DQ-02 一致，共享同一 UoW 的 Repositories 内部共享 Infrastructure 事务与 Session 但不经公共接口暴露；Repository 不得调用或控制 begin/commit/rollback/close/begin_nested/SAVEPOINT 生命周期/UoW 生命周期迁移，职责限于加载/暂存/查询/返回项目结果/上抛失败；嵌套业务 UnitOfWork 禁止（持有活动 UoW 的 Use Case 不得调用另一个创建新 UoW 或独立提交的 Transactional Use Case；可复用行为提取为 Domain Service / transaction-neutral Application Service / 接收显式 Ports 的内部操作；检测企图必须经项目自有错误立即失败）；Explicit Composite Application Use Case 拥有唯一外层 UnitOfWork 与唯一最终提交点（记录跨 Aggregate 不变量、显式类型化 Ports、唯一模块/表所有权、必要时 Public Application Contracts）；ACTIVE 期间禁止加入 ambient UoW / 打开第二个业务 UoW / 子操作 commit 作部分提交 / SAVEPOINT 作嵌套业务 commit / commit 权移交 Repository / UoW 存入全局、thread-local 或 Workflow 状态；SAVEPOINT 不是嵌套 UnitOfWork、不由 Application UoW Port 暴露，有限 Infrastructure 级使用仍受 DQ-05 治理；UoW Port 默认不暴露 flush()，内部 flush 非业务 commit，flush 失败必须回滚并丢弃当前 UoW；Engine 与 sessionmaker 可为 Composition Root 长生命周期资源，具体 Session 短生命周期（一个 UoW 一个本地 Command），全局可变 Session 禁止，scoped_session/thread-local/ContextVar ambient 机制不得作为主要事务所有权或依赖注入机制；并发 Command/Worker 执行/Retry/Rerun/Resume 使用独立 UoW 与独立 Session；与 DQ-05 一致（Prepare 与 Commit 不同 UoW 实例、Execute Outside Transaction 无活动 UoW、Human Review/Interrupt/retry backoff 不持有 UoW、UoW 绝不序列化进 Checkpoint、绝不在 Resume 恢复）；纯读 Application Query 使用独立短 Query Scope（不暴露 commit、查询后关闭 Session 释放连接、不返回 ORM entities 或 lazy-loaded relationships、不复用 Command UoW、不成为跨模块持久化 API），读取结果参与后续原子变更或并发决策时须在拥有最终 commit 的 UoW 内或于 Commit 事务内重新校验（衔接 DQ-04/05）；Candidate A 以此修订被接受，Candidate B（装饰器/context-manager 退出自动提交）作为项目 UnitOfWork 模型被拒绝（Context Manager 仍允许用于生命周期清理但不得自动提交业务状态），Candidate C（Repository 管理事务）被拒绝；剩余所有权：并发/锁/重试 → DQ-07、幂等 → DQ-08、Outbox/Durable Dispatch → DQ-09、Event/Audit → DQ-10、HTTP 请求作用域 → RFC-004、Workflow/Checkpoint 运行时 → RFC-003、测试分类 → DQ-16；持久化语义验证使用真实 PostgreSQL（覆盖清单见 DQ-06 第 50 点）。RFC-002-DQ-07 已由用户正式决定（**ACCEPTED，Accepted with Revision**，2026-08-02，Accepted Direction = Layered Concurrency Control）：项目采用分层并发控制而非单一通用锁机制；普通 Business Current Truth、Aggregate Roots、Current Truth Pointers、Stage State、Review Package state 等受保护可变记录的状态修改默认使用 DQ-04 乐观并发协议（revision + expected_revision + 条件更新 + affected-row 校验），expected_revision 不匹配是语义业务冲突、不得作为瞬时数据库失败盲目重试（并发审批返回冲突、过期 Human Review 拒绝、同时失效仅一个成功、后写者不得静默覆盖、过期外部结果不得重绑较新 Domain Version）；数据库唯一约束是重复业务事实的最终完整性防线（唯一约束违反不得统一视为可重试，错误边界必须识别命名约束并至少区分已完成重复操作/幂等重放/version-number 分配竞争/重复 Review Decision/真实完整性缺陷/未分类违反；完整幂等键层级、输入指纹、结果重放与去重存储仍由 DQ-08 拥有）；Duplicate Resume、并发 Worker 执行与同一并发范围的执行所有权要求 Durable Execution Guard / Durable Lease（concurrency_scope_id、holder/Attempt identity、获取时间、过期时间、单调递增 generation/fencing_token、active/released/expired 生命周期；确切表名/字段名/索引/物理存储留实现设计与 DQ-13），Lease 获取在短 PostgreSQL 事务内完成且必须在长执行开始前提交、提交后释放行锁/Session/UoW/连接，Worker 在 LLM 执行/外部 HTTP 或工具调用/Human Review 等待/Workflow Interrupt/retry backoff/长计算/跨进程执行期间不得持有 PostgreSQL 行锁；每次成功获取/接管/重新分配颁发单调递增 fencing_token，Worker Commit 在最终短事务内验证 expected_revision + 当前 Lease Holder + 当前 fencing_token + 当前 Attempt/Run identity + 后续 DQ-08 接受的适用幂等身份 + 业务不变量，持旧 fencing_token 的过期 Worker 即使仍运行且返回看似有效结果也不得提交；进程本地 asyncio.Lock/threading.Lock/mutex/内存任务锁仅为非权威优化（减少重复工作）、不得作为业务正确性来源，正确性须在进程重启/Worker 崩溃/多 Worker 进程/多部署副本/机器替换/内存状态丢失下保持；SELECT FOR UPDATE SKIP LOCKED 仅限显式队列式 Claim 短事务（select candidate → lock → assign durable holder/Lease/fencing token → commit → release → execute outside transaction），不得用于普通 Current Truth 读取、Human Review 读取、完整结果集查询、绕过 expected_revision 冲突、静默忽略正在修改的业务对象、跨外部调用持有执行所有权；SELECT FOR UPDATE/NOWAIT 等悲观行锁不是全局默认（采用须记录受保护不变量/为何乐观不足/锁定行/确定性锁顺序/行为/最大事务时长/超时与错误翻译/重试安全性/真实 PostgreSQL 证据；多对象事务使用确定性全局锁顺序）；Session-level PostgreSQL Advisory Locks 作为默认或权威机制被禁止，Transaction-level Advisory Locks 非默认（仅自然行无法表达并发范围时经独立架构审查考虑）；SQLSTATE 40001 serialization_failure 与 40P01 deadlock_detected 归类为可能瞬时的数据库事务失败，有限自动重试由 Application Transaction Runner / Command Executor 拥有（Repository/Session/UoW 实现不得静默自重试循环），每次重试 = 重新开始整个短事务 + 全新一一次性 UoW + 全新 Session + 重新加载状态 + 重新评估前置条件 + 重新运行 revision 与 Lease 验证 + 丢弃失败尝试 ORM entities，默认预算 = 1 次初始 + 最多 2 次重试 = 共计 3 次尝试，无限/无界重试禁止，backoff/jitter 在开放事务/UoW/Session 之外（具体参数/指标/阈值可在 RFC-007 配置，有界要求不得移除）；不得盲目或自动重试：expected_revision 不匹配、stale fencing_token、丢失/过期 Lease、过期 Human Review 提交、业务不变量拒绝、过期外部结果、未分类 unique_violation、未定义策略的 lock_not_available/NOWAIT 失败（已分类重复操作仅在 DQ-08 幂等语义下转换为幂等响应）；外部 LLM/HTTP Provider/工具执行不得进入数据库事务重试循环，Commit 事务可在业务前置条件有效时使用已产生的不可变外部结果重试但不得自动重新调用 Provider；五类并发场景控制组合：duplicate resume = Durable Lease + fencing_token + DQ-08 幂等身份、concurrent approval = expected_revision CAS + 唯一 Review Decision identity、stale worker = Lease Holder 验证 + fencing_token + expected_revision、repeated command = 命名数据库唯一约束 + DQ-08 幂等记录、simultaneous invalidation = 对所属 Aggregate/Stage State/Current Truth Pointer 的 expected_revision CAS；LangGraph thread_id 与 Checkpoint identity 仅定位工作流状态与恢复位置，不得视为 Business Concurrency Lock/Durable Lease/fencing_token/业务 Idempotency Record/单一活动 Resume 证明；Concurrency Scenario Matrix（13 字段）为持久化或并发控制实现开始前的必备产出、真实 PostgreSQL 多 Worker Concurrency Technical Spike（9 项验证）为并发控制实现授权前的必备验证——二者均 REQUIRED 但不由 DQ-07 接受授权（Matrix 需后续规划或实现就绪授权；Spike Issue/Branch/PR/代码/测试/基础设施创建需单独明确用户授权）；剩余所有权：完整幂等键层级与响应重放 → DQ-08、Outbox/Dispatch Claim 实现 → DQ-09、Event/Audit 持久化顺序 → DQ-10、Checkpoint 并发与 Runtime 对账 → RFC-003、API 冲突状态码或 ETag/If-Match 协议 → RFC-004、完整持久化测试分类与 CI 执行设计 → DQ-16、运维重试指标与阈值 → RFC-007；详细持久化测试组织归 DQ-16，所有正式并发语义测试必须使用真实 PostgreSQL（非 SQLite 或内存替代品）。**官方能力与项目决定的区分（续，DQ-07）：** PostgreSQL 官方能力为「SELECT FOR UPDATE / SKIP LOCKED / NOWAIT 悲观行锁、Session-level 与 Transaction-level Advisory Locks、SQLSTATE 40001 serialization_failure 与 40P01 deadlock_detected、MVCC 行级并发」，SQLAlchemy 官方能力为「`with_for_update(nowait/skip_locked)` 渲染 FOR UPDATE 系列、`version_id_col` 乐观并发」，LangGraph 官方事实为「OSS 无同一 thread_id 并发 resume 的锁/乐观并发/CAS」；**项目 Accepted Decision 采用分层并发控制**（乐观 revision 默认 + 命名唯一约束最终防线 + Durable Lease + 单调 fencing_token 执行所有权 + SKIP LOCKED 受限为队列式 Claim + Session-level Advisory Lock 禁止 + Application Transaction Runner 有界三次重试）——Lease 与 fencing_token 是 **Accepted Architecture Decision（项目用户决定）**，**非 PostgreSQL 或 LangGraph 官方强制架构**；完整幂等键层级、Outbox/Dispatch Claim、Event/Audit 顺序、Checkpoint 并发与 Runtime 对账、API 冲突协议与完整测试分类仍为留白（Deferred decision）。**官方能力与项目决定的区分：** SQLAlchemy 官方能力为「Session 天然 = UoW + identity map、技术上可跨顺序事务使用」；**项目 Accepted Decision 采用更严格的一次性 UoW 与显式 commit**（非 SQLAlchemy 强制规则，而是项目用户决定）；并发、Outbox 与 runtime 细节仍为留白（Deferred decision）。第 8 项的 DQ-08（Idempotency Model）已由用户正式决定（**RFC-002-DQ-08 = ACCEPTED，Accepted with Major Revision**，2026-08-02，Primary Direction = Candidate B，Supporting Principle = Candidate C，Rejected Direction = Candidate A as Universal Table）：项目采用**分层幂等模型**——各幂等层由相应 Owning Module 分层持久化（模块私有、与自身业务更新同一 PostgreSQL 事务提交、不得成为跨模块共享读写表），所有幂等层共享统一概念与行为契约（logical operation identity / owning module / idempotency scope / idempotency key / input fingerprint / execution status / retry-rerun semantics / unique constraint / result replay semantics / atomic transaction boundary；**统一概念契约不意味着统一物理表**），跨模块、跨 Command/Workflow/Consumer/Dispatch/Provider 调用的万能 Idempotency Table 被拒绝；Candidate B（分层各自存储）接受为主要持久化方向，Candidate C（天然幂等 set/ensure/replace-to-desired-state/compare-and-set 语义）接受为强制设计原则（不得替代显式记录、唯一约束或执行所有权控制）；七类身份 Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity 明确区分不得混用；Retry = same Command ID/Idempotency Key/Stage Run ID/Input Fingerprint + new Attempt ID（不创建新 Domain Version），Intentional Rerun = 新逻辑身份 + rerun_of 关系（成功后可产生新 Domain Version），由明确 Application Intent 区分；Versioned Input Fingerprint（规范化业务有效输入、版本化规则、只含决定业务效果的字段）；同 Scope+Key+相同 Fingerprint 重放原 Application Result（不重复业务副作用），不同 Fingerprint 返回 Idempotency Key Conflict（不覆盖/不执行/不误重放/不盲目重试）；幂等成功记录与 Business Current Truth 同一 DEC-035 Atomic Business Commit 提交（回滚不留 SUCCEEDED；响应丢失重放项目自有稳定结果）；Consumer Dedup Marker 与消费业务更新同事务（不得先提交 Marker）；IN_PROGRESS 执行所有权与 DQ-07 Durable Lease / Lease Holder / Attempt ID / fencing_token 协同（旧 Worker 不得写入 SUCCEEDED；Checkpoint/thread_id 不作为业务幂等记录）；瞬时基础设施失败（连接超时/40001/40P01/临时 Provider 不可用/Worker Crash/Lease 过期/网络故障）不永久固化为终局结果，确定性终局语义结果可稳定重放；Provider Retry 复用同一 Provider Call Identity（DB 事务重试不重调已完成 Provider 调用；无原生幂等则维护 Durable Call Ledger）；具体表/Retention/安全留 DQ-13/15/17，Outbox/Dispatch 留 DQ-09，Event/Audit 留 DQ-10，HTTP 幂等协议留 RFC-004，测试分类留 DQ-16；**Idempotency Identity Matrix（18 字段）为幂等实现前置条件——REQUIRED 但不被本决定授权**（不新增独立 Spike；DQ-07 的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效并应覆盖幂等并发场景）。**官方能力与项目决定的区分（续，DQ-08）：** Idempotent Consumer/Receiver（dedup 表 + 主键判重、**去重须与业务更新同事务**）与 Stripe 幂等键（持久化首个响应原样重放、客户端生成键、唯一约束、参数比对防误用）是**官方/权威模式能力**（模式定义研究）；PostgreSQL 命名唯一约束是官方能力；**分层模块私有幂等存储 + 统一概念契约（非统一物理表）、项目七类身份模型与 Retry/Rerun 身份语义、Versioned Input Fingerprint 规范化规则、IN_PROGRESS/FAILED_TERMINAL 等状态机表达、Provider Call Ledger 与 Durable Call Ledger 要求、天然幂等 set/ensure/replace 设计原则均为 Accepted Architecture Decision（项目用户决定），非 Stripe、AWS 或 PostgreSQL 官方强制架构**；具体物理表结构、Retention、加密/PII 与 Outbox/Event-Audit/HTTP 幂等协议仍为留白（Deferred decision，→ DQ-09/10/13/15/16/17/RFC-004）。以上均为 **Accepted user decision**，非研究证据；本文件证据底座（DEC/RFC-001/官方能力引用）保持不变。§8 第 1 项的 DQ-01 部分、第 2 项的 DQ-02 部分、第 3 项（DQ-03）、第 4 项的 DQ-04 部分、第 5 项（DQ-05）、第 6 项（DQ-06）、第 7 项（DQ-07）与第 8 项（DQ-08）自此为 ACCEPTED；DQ-09/DQ-14 等部分仍 PENDING。
> **重要事实校正：** 全仓库**无**字面等号短语「Business Database = Current Truth」「Checkpointer = Recovery」。权威原文为 Architecture Baseline §2：「三类存储分离：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）物理分离；**Checkpoint ≠ Current Truth**」，及 DEC-023「LangGraph Checkpointer **仅**承载执行恢复、图状态快照、Interrupt 和 Resume」。本文件与 RFC-002 一律引用真实原文。

---

## 0. 总纲：三类存储分离 + 四类状态边界（不可被 RFC-002 推翻的既有约束）

| 约束 | 权威原文（文件:行号） |
|---|---|
| 三类存储物理/逻辑分离 | architecture-baseline-v1.md §2：「三类存储分离：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）物理分离；Checkpoint ≠ Current Truth」 |
| 逻辑分离≠物理分离 | data-architecture.md（DEC-034）：「三类 Repository 逻辑分离……即使同一物理存储也须保持逻辑边界，`LangGraph Checkpoint Store ≠ Business Current Truth Repository`」 |
| Checkpointer 仅恢复 | data-architecture.md（DEC-023）：「LangGraph Checkpointer **仅**承载执行恢复、图状态快照、Interrupt 和 Resume……**不得**把 LangGraph Checkpoint 数据库作为整个产品唯一的业务数据库」 |
| 业务库权威 | data-architecture.md（DEC-023）：「正式业务数据查询、当前有效版本、用户修改、审计记录以业务数据库为准；Checkpoint 数据不作为业务查询的权威来源」 |
| Checkpointer 五「不」 | integration-boundaries.md（DEC-033）：「不保存业务 Current Truth、不替代业务 Repository、不判断业务版本是否有效、不覆盖较新的业务状态、不创建正式业务对象」 |
| 四类状态 | dec-024：`Authoritative Business State`（Business Database）/ `Workflow Execution State`（Compact LangGraph State）/ `Execution Recovery`（LangGraph Checkpointer）/ `User-facing Interaction State`（派生，非独立 Current Truth） |
| Product Query Rule | dec-024:753-762：「不得将 LangGraph Checkpoint 数据库直接作为：产品查询 API / 唯一业务数据库 / 唯一 Current Truth / 唯一版本系统 / 唯一审计系统」 |

**对 RFC-002 的含义：** RFC-002 必须把「三类持久化存储」落地为明确的表/库边界，**但**逻辑职责分离是恒定约束——即使生产用同一数据库实例，也**不得**让 Checkpoint Store 变成业务 Current Truth。此边界由 DEC-023/024/033/034/035 共同固定，RFC-002 不得推翻。

---

## 1. Business Current Truth（业务当前真值）

| 需求 | 关键原文（来源:行号） |
|---|---|
| Task identity（稳定业务 ID） | dec-024:608-620「task_id 是长期稳定的产品业务 ID……不因 Resume 或重新运行而改变」；dec-013「每次流程视为独立任务，拥有稳定 task_id」 |
| Task lifecycle | dec-024:224-244 Task Status 枚举（draft/running/waiting_for_input/waiting_for_review/paused/completed/failed/cancelled） |
| Current stage + Stage state | dec-024:253-294 统一 StageState（current_version_id/last_valid_version_id/based_on_versions）+ Stage Status 枚举 |
| Structured business items | dec-012:240-263「item_id/content/evidence_type/source_refs/status/generated_by/user_modified」，不得只存一段不可拆分自由文本 |
| Approved strategy | dec-029:384-417；「Approved Strategy 是 Marketing Brief Generation 唯一允许读取的战略输入」 |
| Marketing brief / Platform mapping output | dec-024:71-72；dec-030/031 版本化 Domain Object |
| Human review decision | dec-024:577-586 ReviewDecision；dec-029 Review Decisions |
| Version history（版本化 Domain Object） | dec-024:298-354「正式业务结果不得通过直接覆盖的方式修改……均应创建新版本」 |
| Current Truth Version Pointers | dec-024:358-390 6 个 version_id 指针；「不得通过字段是否为空推断阶段有效性」 |
| Version dependencies | dec-024:394-422 下游记录 based_on 上游版本，运行前校验一致 |
| Invalidation state | dec-024:426-469 InvalidationEvent 8 条（保留旧版本/标 invalid/清 Pointer/记原因/不删历史/不重跑有效上游） |
| Rerun relationship | dec-024:471-503（承接 DEC-009 失效链） |

**归属：** 以上全部属 **Business Current Truth Repository**（业务库权威）。

---

## 2. Raw Inputs and Sources（原始输入与来源/证据）

| 需求 | 关键原文（来源:行号） |
|---|---|
| Raw product input 不被覆盖 | dec-012「原始输入不能被模型生成结果覆盖；AI 解析结果与用户原始内容必须分开保存」 |
| Source metadata | dec-025:76-90 Source（source_id/task_id/source_type/source_scope/ownership/.../current_version_id） |
| Source version / content integrity | dec-025:112-154；SourceVersion 含 `content_hash`；「业务结果必须引用具体 source_version_id 而不能只引用可能持续变化的 source_id」 |
| Fragment 可回原文 + checksum + provenance | dec-025:219-236 / source-and-evidence-specification:139-166 Fragment（fragment_id/source_version_id/locator/content_hash/parser_version），`parser_version` 即 extraction provenance |
| Evidence Link（独立关系对象） | dec-025:479-494 / source-and-evidence-specification:245-260 EvidenceLink（evidence_link_id/target_entity_type/target_version_id/fragment_id/evidence_role/support_strength/validator_status） |
| Deduplication | hybrid-retrieval spec:304-309「按稳定 fragment_id 去重……用户评论类去重须保留 record_id，不得合并不同评论记录」 |
| 原始 vs 业务结论权威边界 | source-and-evidence-specification:508-522「Raw Information Current Truth = Source Version + Document/Record + Fragment；Business Conclusion Current Truth = Versioned Domain Object + Current Truth Pointer；二者关系 = Evidence Link；临时检索 = Retrieved Candidate Fragment（非正式 Current Truth）」 |
| Retrieval Index 独立存储类别 | dec-024:712-719「Business Database / Object Storage / Retrieval Index / Run Log Storage。LangGraph State 只保存对应引用」 |

**待决（→ RFC-002-DQ-12）：** 原始内容是否直接存业务库 vs 只存引用+对象存储；大内容/二进制边界；checksum/normalized source；evidence-to-claim linkage 的持久化形态；Retrieval Index 与 Current Truth 的持久化关系。

---

## 3. Workflow Recovery（工作流恢复）

| 需求 | 关键原文（来源:行号） |
|---|---|
| Checkpoint / Resume / Interrupt | dec-024「Checkpointer 负责执行快照、Interrupt、Resume 和故障恢复」 |
| 持久化时机（9 个） | dec-013:62-100（任务创建/来源处理/分析草稿/进入审核/用户修改/阶段失效/局部重跑/最终 Brief/工作流异常） |
| Node execution state（五层运行身份） | dec-033:86-92 `Task / Workflow Run / Skill Run / Node Execution / Execution Attempt` |
| Failure metadata | dec-033:299-321 RuntimeErrorRecord（error_id/error_category/severity/retryability/failure_disposition/cause_chain[]/...） |
| Idempotency key / Input Fingerprint | dec-033:460-462「task_id/skill_name/input_version_ids/source_set_version_id/skill_contract_version/execution_configuration_version/logical_operation」 |
| Safe Resume Boundary | dec-033:482「只允许从安全边界 Resume」；484「不得从中间状态任意恢复」 |
| Checkpoint Reconciliation（对账） | dec-033:490-492「Resume 前必须验证 checkpoint.task_id/thread_id/input_version_ids/current_truth_pointers/stage_validity/review_package_version。旧业务版本 → checkpoint_status=stale……不得自动覆盖新的业务版本」 |
| Retry ≠ Rerun | dec-033:149-153「Retry = Technical Recovery；Rerun = New Business Computation」；Retry 五要素含「Same Idempotency Identity」「Retry 不得创建新的业务版本」 |
| Cancellation 无部分写入 | dec-033:440-450「不得在事务中间强制终止并留下部分业务状态」 |
| Manual Recovery 不重复 | dec-033:551「不得手工伪造 Fact / 绕过 Validator / 直接修改 Evidence Link / 强制旧 Checkpoint 应用于新版本 / 删除失败历史 / 直接修改 Current Truth Pointer」 |

**归属：** Runtime Repository（运行记录）+ Checkpoint Store（图执行恢复）。**恢复时以 Business Current Truth 为权威，Checkpoint 让步**（`checkpoint.rejected_as_stale`）。
**待决（→ RFC-002-DQ-13）：** Checkpointer 是否与业务库同服务/同库/同 Schema；checkpoint 生命周期与删除策略；Business State 与 Graph State 对账的持久化机制。

---

## 4. Human Review（人工审核）

| 需求 | 关键原文（来源:行号） |
|---|---|
| Review Package Version（固定输入快照） | dec-029:91-128「固定审核时的 Facts/Insights/Positioning/Source Set Versions/Candidates/Evidence Limitations；审核开始后不得后台静默替换」 |
| Review Package Version Validity | dec-029:131-159 上游版本变化 → 原 Package 标 superseded，旧提交被阻止 |
| Strategy Draft（临时，非 Current Truth） | dec-029:349-381「不属于业务 Current Truth；不允许下游使用；须记版本；提交前必须通过 Validator」 |
| Review Decisions（结构化） | dec-029 Review Decisions（Hypothesis/Proof Point/Evidence Limitation Decisions） |
| Approved Strategy Version + approver/timestamp | dec-029:384-417（approved_by/approved_at/version_status） |
| Submission Transaction（18 步原子） | dec-029:559-594「submit 必须作为原子事务处理……失败时不创建 Approved Strategy Version / 不更新 Current Truth Pointer / 不改变下游阶段状态」 |
| Stale review detection | dec-029:616-625「若提交使用的 Package/Draft/Facts/Insights/Positioning Version 已过期，则必须拒绝」 |
| Duplicate submit 幂等 | dec-029:607-614「相同 idempotency_key 重复提交：返回第一次成功生成的 Approved Strategy；不创建第二个版本；不重复推进 Workflow」 |
| Resume after approval | dec-024:806-816 Human Review Resume 流程 |
| Review Audit History | dec-029:670-700 保留 17 类记录（含失败校验记录） |
| Withdrawal Record | dec-029 撤回创建记录、保留原版本、清除 Pointer、下游失效 |

**归属：** Business Current Truth Repository（Review Package/Strategy Draft/Approved Strategy/Review Audit）+ 独立 Submission Transaction。
**待决（→ RFC-002-DQ-07 并发，自此 ACCEPTED 2026-08-02）：** 多标签页/客户端并发编辑「不得静默覆盖较新 Draft」的并发控制实现（dec-029:627-638「Optimistic Lock / Revision Number / ETag / Database Lock 尚未确认」）——**DQ-07 Accepted Decision 已决定：普通业务状态修改默认使用 DQ-04 `expected_revision` compare-and-swap（并发审批返回冲突、过期 Human Review 提交拒绝、同时失效仅一个成功），唯一 Review Decision identity 由命名数据库唯一约束保护；ETag / If-Match 的 HTTP 协议映射仍由 RFC-004 决定**。

---

## 5. Auditability（可审计性）

| 需求 | 关键原文（来源:行号） |
|---|---|
| created_at / updated_at | dec-024:263-265；业务版本 created_at |
| actor / created_by / creation_type | dec-024:326-342（created_by ∈ system/model/user；creation_type ∈ initial_generation/user_edit/...） |
| causation（based_on / triggered_by） | dec-024:319 based_on_version_ids；dec-024:436 InvalidationEvent.triggered_by |
| command identity | dec-029:601-605 提交携带 review_id/package_version/draft_version/idempotency_key |
| state transition record | dec-033:565 概念事件清单（workflow.*/transaction.committed/transaction.rolled_back/checkpoint.saved/checkpoint.rejected_as_stale/...） |
| immutable history（不删除） | dec-024:469「不删除历史结果」；dec-024:841「Invalidation Does Not Mean Deletion」 |
| mutable projection | dec-024:159-160 Interaction State 派生、非独立 Current Truth |
| evidence traceability | dec-025:642-651 Proof Point → Fact → Evidence Link → Fragment → Source Version |
| audit record（事务一部分） | dec-029:582 提交事务步骤含 Write Audit Record |
| business audit vs observability log 分离 | business_audit 属 Business Store；observability 日志属 Runtime Store（dec-033:563-592） |
| 完整事件溯源不属 MVP | dec-013:170-190「MVP 暂不实现完整事件溯源系统……可保存必要运行历史和用户修改记录」 |

**待决（→ RFC-002-DQ-10/DQ-11）：** Domain Event / Integration Event / Audit Record / State Transition Record / Observability Event 是否分离、哪些需持久化；不采用完整 Event Sourcing 时如何满足 replay evidence / audit / historical comparison / rollback analysis。

---

## 6. Concurrent Processes（并发进程）

| 需求 | 关键原文（来源:行号） |
|---|---|
| API Process vs Workflow Worker | 架构基线 §12（DQ-07）：API/Worker/CLI 三进程；「三者均不得直接访问业务 Repository / Current Truth」 |
| Durable Dispatch | 架构基线 §12.4 WorkflowDispatchPort（schedule_start/resume/rerun/cancel/recovery）；「API 返回已接受前 Durable Work Intent 必须已被可靠记录；禁止 asyncio.create_task / Web Framework 临时 Background Task」 |
| Duplicate commands | dec-029:607-614；dec-033:462 Worker 重启重复到达返回首次成功结果 |
| Simultaneous resume / Duplicate resume | dec-033:498-502「Resume 尚未被重复处理。Human Review Resume 必须幂等」；spike-05 实证 |
| Retry race / side effect | dec-033:418「Side-effect Tool……必须使用 idempotency_key。第一次调用是否成功不确定时，不得盲目重复执行」 |
| Stale writes / 并发编辑 | dec-029:627-638「多个标签页或客户端同时编辑时，不得静默覆盖较新的 Draft」 |
| Optimistic concurrency（**未选型**） | dec-022「乐观锁或等效并发控制」；dec-029:634-638「Optimistic Lock / Revision Number / ETag / Database Lock 尚未确认」 |
| Transaction boundary ownership | 架构基线 §14.3「业务事务由 Application Use Case 拥有」；§14.12「长 Workflow 由多个短 Application Transaction 组成」 |
| Atomic Resume Coordination | 架构基线 §12.7「Approved Strategy Commit + Durable Resume Intent = Atomic or Reliably Reconciled」 |

**待决（→ RFC-002-DQ-09；DQ-07 并发控制与 DQ-08 幂等模型自此 ACCEPTED 2026-08-02）：** ~~乐观并发/CAS/数据库约束/应用锁/task-level 序列化的取舍~~（**已由 DQ-07 Accepted Decision 决定：分层并发控制——乐观 revision 默认 + 命名唯一约束最终防线 + Durable Lease + fencing_token 执行所有权 + SKIP LOCKED 仅限队列式 Claim + 进程内锁仅非权威优化**）；~~Command ID/Idempotency Key/Attempt ID/Run ID/Review Decision ID/Dispatch ID 的唯一性约束~~（**已由 DQ-08 Accepted Decision 决定：分层幂等模型——七类身份（Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity）明确区分不得混用；Idempotency Key 在明确 Scope 内唯一；Review Decision ID 由命名唯一约束保护；Retry 复用同一逻辑身份 + 新 Attempt ID，Intentional Rerun 创建新逻辑身份；同 Scope+Key+Fingerprint 重放、不同 Fingerprint 冲突；幂等成功记录与 Business Current Truth 同一 DEC-035 原子提交；完整身份矩阵留 Idempotency Identity Matrix（REQUIRED / NOT AUTHORIZED）**）；是否首版引入 Transactional Outbox（留 DQ-09）。
**Spike 明确 GAP（R-1）：** readiness L119「并发/分布式未验证（单线程同步）……生产部署前需并发模型与一致性 RFC」。

---

## 7. 原子业务提交契约（Atomic Business Commit）— 统一事务模板

六要素单事务（不可拆分，Commit Together or Rollback Together）：

| 要素 | 来源 |
|---|---|
| Create Domain Version | 架构基线 §3 / §14.3；data-architecture DEC-035 |
| Create Formal Evidence Links | 同上 |
| Update Current Truth Pointer | 同上 |
| Update Stage State | 同上 |
| Write Audit Record | 同上 |
| Write Idempotency Record | 同上 |

**规则：** 任一失败整体回滚，不留 Partial Current Truth，不推进 Workflow，Retry 使用相同幂等身份。Graph Node **不得**绕过统一 BusinessCommitService 分别写入（data-architecture DEC-035）。Skill 不拥有业务事务（架构基线 §12.3 DQ-05「Skill Business Transaction Ownership = NO」）。
**Spike 实证：** spike-04（mid-commit 失败整体回滚，partial_write_count==0）、test_transaction_idempotency（同 key 重放 committed==False，valid_version_count==1）。

---

## 8. 已被显式指派给 RFC-002 的待决项（DEC/RFC-001/Readiness 留白汇总）

| # | 待决项 | 显式留白来源 | 对应 DQ |
|---|---|---|---|
| 1 | 生产数据库 / ORM / Migration / Schema Strategy | baseline §14.11/§16.6/§20；data-arch DEC-024「仍待确认」 | DQ-01（**ACCEPTED 2026-08-01**）/DQ-14 |
| 2 | Repository / Unit of Work / Database Session 实现形态 | baseline §10.8（列为 RFC-002 禁建项） | DQ-02（**ACCEPTED 2026-08-01**：所有权与访问边界）/DQ-06（**ACCEPTED 2026-08-02**：UoW 模型） |
| 3 | Aggregate 与持久化边界（哪些更新原子提交） | RFC-001 DQ-04 Atomic Business Commit；DEC-024 | DQ-03（**ACCEPTED 2026-08-02**） |
| 4 | Domain state versioning 与 optimistic concurrency version 语义 | dec-024（6 类版本已固定概念）；dec-029:634-638（并发版本未选型） | DQ-04（**ACCEPTED 2026-08-02**：`domain_version_id`/`version_number`/`revision` 三类分离 + `expected_revision` 条件更新；`xmin`/SERIALIZABLE 作为权威 revision 被拒绝）/DQ-07（**ACCEPTED 2026-08-02**：分层并发控制，隔离/锁/重试的留白由此决定） |
| 5 | Transaction boundary（Use Case↔事务、外部调用不入事务、Review 暂停结束事务、Worker retry 新事务） | baseline §14.3/§12.4；DEC-033 | DQ-05（**ACCEPTED 2026-08-02**：Application 拥有业务事务、一短显式事务一最终提交点、长流程多短事务 + 无事务执行阶段、四项 PROHIBITED、Commit-time Revision Revalidation、默认 READ COMMITTED、SAVEPOINT 仅基础设施机制、嵌套/分布式事务拒绝；强隔离/锁/重试留 DQ-07（自此 ACCEPTED）；UoW Port 形态留 DQ-06） |
| 6 | Unit of Work model（显式 UoW、接口位置、Commit/Rollback 负责方；嵌套业务事务禁止已由 DQ-05 ACCEPTED 决定） | baseline §14.4 UoW Port 由 Application 定义 | DQ-06（**ACCEPTED 2026-08-02**：UoW Port 由 Application 定义、Infrastructure SQLAlchemy 实现（Session 为不暴露的 Infrastructure 细节）、一次性 UoW = 一个 Session + 一个短事务 + 一个最终结果、显式 commit（Context 退出不自动提交）、未 commit/异常退出 = rollback/close/discard、Repository 无事务控制权与 Session 暴露、禁止 Registry/Service Locator、嵌套业务 UoW 禁止、Composite 唯一外层 UoW、纯读独立短 Query Scope；并发/锁/重试留 DQ-07、测试分类留 DQ-16） |
| 7 | Concurrency control（optimistic/pessimistic/CAS/约束/应用锁/task 序列化；覆盖 duplicate resume/concurrent approval/stale worker/repeated command/simultaneous invalidation） | dec-022/dec-029；readiness R-1 | DQ-07（**ACCEPTED 2026-08-02**：分层并发控制——乐观 revision 默认（DQ-04 协议，语义冲突不盲目重试）+ 命名数据库唯一约束最终防线（完整幂等键留 DQ-08）+ Durable Lease + 单调 fencing_token 执行所有权（Worker Commit 验证 revision/Holder/fencing_token；进程内锁仅非权威优化）+ SKIP LOCKED 仅限队列式 Claim 短事务；悲观锁非全局默认；Session-level Advisory Lock 禁止、Transaction-level 非默认；40001/40P01 由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试；五类场景控制组合映射；thread_id/Checkpoint 不得视为业务锁/Lease/fencing/幂等记录；Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Technical Spike 为实现前置条件（均 REQUIRED、均未授权）；幂等层级留 DQ-08、Outbox 留 DQ-09、Event/Audit 留 DQ-10、Checkpoint 对账留 RFC-003、API 冲突协议留 RFC-004、测试分类留 DQ-16、运维重试指标留 RFC-007） |
| 8 | Idempotency model（Command ID/Idempotency Key/Attempt ID/Stage Run ID/Review Decision ID/Dispatch ID/Provider Call Identity 及分层幂等语义） | dec-033:456/460 | DQ-08（**ACCEPTED 2026-08-02**，Accepted with Major Revision：分层模块私有存储（Candidate B 为主）+ 天然幂等设计原则（Candidate C）+ 统一语义契约（非统一物理表）；Candidate A 万能表拒绝；Retry/Rerun 身份语义；Versioned Input Fingerprint；同 Key 同 Fingerprint 重放、不同 Fingerprint 冲突；幂等成功记录与 DEC-035 同事务；Consumer Dedup 同事务；IN_PROGRESS 协同 DQ-07 Lease/fencing；瞬时失败不固化、终局结果可重放；Provider Call Identity 复用；Matrix REQUIRED / NOT AUTHORIZED） |
| 9 | Transactional Outbox & durable dispatch（是否首版引入、API 如何触发 Worker、dispatch failure 恢复） | baseline §12.4/§12.7（显式指派 RFC-002/003） | DQ-09 |
| 10 | Event & audit persistence（Domain/Integration/Audit/State Transition/Observability Event 分离与持久化） | dec-013/dec-033；DEC-024 | DQ-10 |
| 11 | Snapshot vs history model（mutable projection/append-only history/versioned snapshots；是否 Event Sourcing） | dec-013「完整事件溯源不属 MVP」 | DQ-11 |
| 12 | Source & evidence persistence（原始内容存 DB vs 引用、大内容/二进制、checksum、normalized source、provenance、retrieval index 关系） | dec-025；source-and-evidence spec | DQ-12 |
| 13 | Workflow checkpoint separation（同服务/同库/同 Schema、生命周期、删除策略、对账、recovery 权威） | dec-024/dec-033；readiness R-3 | DQ-13 |
| 14 | Schema evolution & migrations（migration ownership、forward-only、rollback、滚动升级兼容、backfill、destructive gate、schema version） | baseline §14.11 | DQ-14 |
| 15 | Data retention & deletion boundary（Task/raw source/evidence/checkpoints/audit/model responses 保留策略归属） | dec-013/dec-025「数据保留周期/删除策略」待确认 | DQ-15 |
| 16 | Testing strategy for persistence semantics（contract/transaction/concurrency/migration/idempotency/real-DB vs SQLite fake） | baseline §14.9 测试基线；dec-022 | DQ-16 |
| 17 | Security & sensitive data boundary（Secret 与业务数据分离、PII 分类、加密责任、redaction、least privilege、credentials ownership、test fixture 限制） | RFC-001 DQ-06 Secret 边界；dec-033 Sensitive Data Boundary | DQ-17 |

> 命名说明：DQ 编号对应任务指令的 RFC-002-DQ-01 ~ RFC-002-DQ-17。最终 DQ 集合（拆分/合并/重命名）在 RFC-002 正文 Phase C 中确定并说明理由。
