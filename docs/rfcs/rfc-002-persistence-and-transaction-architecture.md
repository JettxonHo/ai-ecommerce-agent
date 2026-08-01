# RFC-002 — Persistence and Transaction Architecture（持久化与事务架构）

> **治理：** DEC-036（Controlled Git/GitHub Execution）· DEC-038（RFC and Issue Governance）
> **纪律：** 本 RFC 是**架构提案**。**只有用户**能把任何 Decision Question 或本 RFC 整体标记为 ACCEPTED；Coding Agent **不得**自行接受、Merge 或据其实施生产代码。

---

## 1. Metadata（元数据）

| 字段 | 值 |
|---|---|
| RFC | RFC-002 |
| Title | Persistence and Transaction Architecture（持久化与事务架构） |
| **Status** | **IN REVIEW** |
| Decision Questions | **DQ-01 = ACCEPTED**・**DQ-02 = ACCEPTED**（均 2026-08-01）・**DQ-03 = ACCEPTED**・**DQ-04 = ACCEPTED**・**DQ-05 = ACCEPTED**・**DQ-06 = ACCEPTED**・**DQ-07 = ACCEPTED**（DQ-03/04/05/06/07 均 2026-08-02；均用户正式决定，Accepted with Revision）・**DQ-08 = ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Primary Direction = Candidate B，Supporting Principle = Candidate C）；DQ-09 ~ DQ-17 = **PROPOSED** |
| Recommendation | **PROPOSED**（非 Accepted；DQ-01/02/03/04/05/06/07/08 的历史 Recommendation 已被各自 Accepted Decision 取代） |
| User Decisions | **DQ-01 = ACCEPTED WITH REVISION**；**DQ-02 = ACCEPTED WITH REVISION**；**DQ-03 = ACCEPTED WITH REVISION**；**DQ-04 = ACCEPTED WITH REVISION**；**DQ-05 = ACCEPTED WITH REVISION**；**DQ-06 = ACCEPTED WITH REVISION**；**DQ-07 = ACCEPTED WITH REVISION**；**DQ-08 = ACCEPTED WITH MAJOR REVISION**；DQ-09 ~ DQ-17 = **PENDING**（9 项） |
| Implementation | **NOT AUTHORIZED** |
| Depends on | RFC-001（ACCEPTED）· DEC-012/013/022/023/024/025/029/032/033/034/035 |
| Blocks | Business Repository / Current Truth；为 RFC-003/004/005/006/007 提供持久化契约 |
| Spike gaps addressed | R-1（并发/分布式未验证）· R-3（生产 Checkpointer 未锁定）· R-4（规模/性能未验证） |
| Branch | `rfc/002-persistence-transaction-architecture` |
| Supporting artifacts | `rfc-002-research-persistence-requirements.md` · `rfc-002-analysis-cross-rfc-boundary.md` · `rfc-002-decision-questions.md` |

---

## 2. Summary（摘要）

本 RFC 定义 AI Ecommerce Agent 的**持久化与事务架构**：生产 Business Current Truth Repository 的技术选型方向、模块持久化所有权、聚合与原子提交边界、领域状态版本化、事务边界、Unit of Work、并发控制、幂等模型、Transactional Outbox / Durable Dispatch 落库形态、事件与审计持久化、快照与历史模型、来源与证据持久化、Workflow Checkpoint 分离、Schema 演进、数据保留、持久化测试策略、安全与敏感数据边界。

它把 DEC-024（三类存储分离、四类状态、四个标识符、六类版本指针）、DEC-029（人工审核持久化与并发）、DEC-033（失败/重试/恢复/幂等）与 RFC-001（Application 拥有事务、Durable Dispatch Boundary、Port 所有权）转化为 **17 个 Decision Question（DQ-01/02 已于 2026-08-01、DQ-03/04/05/06/07/08 已于 2026-08-02 由用户正式决定，ACCEPTED；DQ-09~17 仍 PROPOSED、User Decision PENDING）**，每个 DQ 给出候选方案、取舍、失败模式、对后续 RFC 的影响与一份**架构建议（非 Accepted；DQ-01/02/03/04/05/06/07/08 的建议已被用户正式决定取代）**。

本 RFC **不**实现任何持久化、数据库、ORM、迁移、Repository、UoW、Outbox、Queue、LangGraph、API 或业务代码。

---

## 3. Status（状态）

```text
RFC-002 Status                = IN REVIEW
RFC-002-DQ-01                 = ACCEPTED（2026-08-01 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-02                 = ACCEPTED（2026-08-01 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-03                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-04                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-05                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-06                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-07                 = ACCEPTED（2026-08-02 用户正式决定，Accepted Direction: Layered Concurrency Control，Accepted with Revision）
RFC-002-DQ-08                 = ACCEPTED（2026-08-02 用户正式决定，Primary Direction: Candidate B，Supporting Principle: Candidate C，Accepted with Major Revision）
RFC-002 Decision Questions    = DQ-01~08 ACCEPTED；DQ-09~17 PROPOSED
RFC-002 Recommendation        = PROPOSED（非 Accepted；DQ-01/02/03/04/05/06/07/08 Recommendation Superseded by Accepted Decision）
RFC-002 Pull Request          = OPEN（PR #24）
Required Checks               = PASS（8/8）
User Decisions                = DQ-01~07 = ACCEPTED WITH REVISION；DQ-08 = ACCEPTED WITH MAJOR REVISION；DQ-09~17 = PENDING（9 项）
Implementation                = NOT AUTHORIZED
```

---

## 4. Context（背景）

### 4.1 治理定位

RFC-002 是 Wave 1 / P0 RFC，阻塞 `Business Repository / Current Truth` 的生产实现。按 DEC-038 与 rfc-register 的依赖顺序，它**依赖 RFC-001（ACCEPTED）**，并为 RFC-003（LangGraph Runtime/Checkpoint）、RFC-004（API/Human Review Protocol）、RFC-005（Source Processing/Retrieval）、RFC-006（LLM Runtime）、RFC-007（Observability）提供持久化契约。

**Traceability 映射说明：** 现行追溯矩阵使用 legacy 字母码——**RFC-B ≈ RFC-002**、RFC-C ≈ RFC-003、RFC-D ≈ RFC-004、RFC-E ≈ RFC-005、RFC-F ≈ RFC-006、RFC-G ≈ RFC-007、RFC-A ≈ RFC-001。本 RFC 一律用正式编号。

### 4.2 既有决定（本 RFC 不得推翻）

| 决定 | 内容 |
|---|---|
| DEC-012 | 原始输入不被模型结果覆盖；原始与解析分离 |
| DEC-013 | 任务级持久状态 + 跨会话 Resume；**完整事件溯源不属 MVP** |
| DEC-022 | 乐观锁或等效并发控制（未选型） |
| DEC-023 | LangGraph Checkpointer **仅**承载执行恢复、图状态快照、Interrupt、Resume |
| DEC-024 | 三类存储分离（Business/Runtime/Checkpoint）、四类状态、四个标识符、六类版本指针、版本化 Domain Object、Current Truth Pointer、Invalidation |
| DEC-025 | Source/SourceVersion/Fragment/EvidenceLink 独立语义 |
| DEC-029 | Review Package Version 固定快照、18 步原子提交、不得静默覆盖较新 Draft、重复 submit 幂等 |
| DEC-032 | 直接优先确定性检索（非工作流控制器） |
| DEC-033 | 五层运行身份、Retry≠Rerun、有界重试、安全恢复边界、Checkpoint Reconciliation、取消无部分写入、幂等键/Input Fingerprint |
| DEC-034 | 三类 Repository 逻辑分离，即使同一物理存储也须保持逻辑边界 |
| DEC-035 | Atomic Business Commit 六要素单事务；分节点契约；Graph Node 不绕过 BusinessCommitService |
| RFC-001 | Modular Monolith First；Domain 纯；Application 拥有用例/端口/事务；Infrastructure 实现端口；Composition Root；API/Worker 可分离；Sync-first；Durable Dispatch Boundary |
| RFC-002-DQ-01（2026-08-01 用户 ACCEPTED） | PostgreSQL 是 Business Current Truth 唯一受支持的权威数据库语义；技术栈 = PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic；本地开发与正式持久化测试使用真实 PostgreSQL；SQLite 不受支持；SQLite-first → PostgreSQL-later 路线被拒绝（详见 §33 Decision Log） |
| RFC-002-DQ-02（2026-08-01 用户 ACCEPTED） | MVP 单一 PostgreSQL 数据库服务；每张业务表有且仅有一个所有模块；ORM/Persistence Models、Repository、schema/migration 变更、状态修改 Use Case 由所有模块独占拥有；跨模块读取经目标模块 Public Application Query、状态修改经所有模块 Public Application Use Case；Direct SQL/ORM/Repository 跨模块访问禁止；边界由 Import Linter + AST/Architecture Tests + Repository Ownership Tests + Migration Ownership Conventions + PR 审查强制；每模块独立 PostgreSQL schema 暂缓（MVP 不要求），物理命名留待实现设计；三类存储物理划分归 DQ-13（详见 §33 Decision Log） |
| RFC-002-DQ-03（2026-08-02 用户 ACCEPTED） | Aggregate 边界 = 业务不变量 + 唯一模块所有权；Atomic Business Commit（DEC-035 六要素）是事务提交协议而非聚合成员资格判据（六要素单事务保持有效）；Task Mega Aggregate 拒绝；默认一个 Use Case 一个主 Aggregate；跨聚合/跨模块显式协调；UoW/事务实现形态移交 DQ-05/06；Aggregate/Invariant Matrix 持久化实施前必备（详见 §33 Decision Log） |
| RFC-002-DQ-04（2026-08-02 用户 ACCEPTED） | `domain_version_id` / `version_number` / `revision` 三类版本语义明确分离、不得共享字段；Domain Version ID 由 Application 层在 INSERT 前生成（opaque UUID，不可变、不复用）；Version Number 在逻辑业务对象内单调递增、受 `(logical_object_id, version_number)` 唯一性约束保护、删除/失效后不复用；受并发保护的 Current Truth Pointer / Aggregate Root / Stage State / Review Package 等可变记录使用独立 NOT NULL `revision`；状态修改 Command 携带 `expected_revision`，compare-and-swap 条件更新，零影响行 = 冲突且 Atomic Business Commit 整体回滚；SQLAlchemy `version_id_col` 仅为 Infrastructure 机制（`StaleDataError` 等翻译为项目自有冲突语义，mapper/Session 细节不得泄漏进 Domain / Public Contract，bulk UPDATE/DELETE 不得绕过 revision）；PostgreSQL `xmin` 不是权威业务 revision；SERIALIZABLE 不替代显式 revision（隔离级别/重试策略留 DQ-05/07）；DEC-035 六要素保持同一事务；RFC-004 可将 revision 映射 ETag/If-Match（HTTP 协议不由 DQ-04 决定）；持久化语义验证使用真实 PostgreSQL（详细测试策略归 DQ-16）（详见 §33 Decision Log） |
| RFC-002-DQ-05（2026-08-02 用户 ACCEPTED） | Business Transaction Owner = Application（Entrypoint / Graph Node 不 begin/commit）；Transactional Application Command = 一个短显式事务 + 一个最终提交点；长流程业务操作 = 多个短事务 + 无事务执行阶段；执行模式 Prepare → Execute Outside Transaction → Commit；四项 PROHIBITED（外部调用持有开放数据库事务、Human Review 跨开放事务、Workflow 暂停跨开放事务、SQLAlchemy Session 跨 Workflow 边界）；Commit-time Revision Revalidation 必选（衔接 DQ-04 `expected_revision` 协议）；DEC-035 六要素单事务保持有效；External Result Before Commit 非 Current Truth；默认 PostgreSQL 隔离级别 = READ COMMITTED（DQ-04 遗留的「默认隔离级别」空白由此决定）；更强隔离 / 锁 / 重试策略留 DQ-07；SAVEPOINT 仅为有限 Infrastructure 机制；嵌套业务事务禁止；与外部供应商的分布式事务拒绝；UoW Port 形态留 DQ-06（详见 §33 Decision Log） |
| RFC-002-DQ-06（2026-08-02 用户 ACCEPTED） | UnitOfWork Port 由 Application 层定义、生产实现属 Infrastructure 层（可使用 SQLAlchemy）；SQLAlchemy Session 是不暴露的 Infrastructure 实现细节（不暴露给 Domain/Application/Entrypoint/API handler/Graph node/Workflow adapter/Public Contract/外部 Provider adapter）；每个 Transactional Application Command 创建一个新的 UnitOfWork 实例；一个 UoW 对应一个短事务、一个 Session、一个显式业务状态迁移、一个最终 commit 或 rollback 结果；UoW 是一次性生命周期对象（NEW → ACTIVE → COMMITTED/ROLLED_BACK → CLOSED），commit/rollback/close 后不得重用；Application Use Case 必须显式调用 commit()，正常 context-manager 退出不得自动提交；未成功 commit 退出或异常退出必须 rollback、close、discard（释放连接、UoW 不可用、原始失败在 Application 错误边界保留或翻译）；每个 Transactional Command 最多成功 commit 一次；非法生命周期操作（二次 commit、commit 后 rollback、close 后访问 Repository、rollback 后用事务、重用失败 UoW、跨 Workflow 边界重用 UoW）必须显式失败；UoW 仅暴露显式类型化 Repository Ports，不得提供 get_repository(name)/registry/Service Locator/raw Session accessor/通用 execute_sql()/动态 Repository 解析；Repository 不得 begin/commit/rollback/close/begin_nested/控制 SAVEPOINT 或 UoW 生命周期、不暴露 Session，职责限于加载/暂存/查询/返回项目结果/上抛失败（模块所有权与 DQ-02 一致）；嵌套业务 UnitOfWork 禁止（ACTIVE 期间禁止隐式加入 ambient UoW、开第二个业务 UoW、子操作 commit 作部分提交、SAVEPOINT 作嵌套业务 commit、commit 权移交 Repository、UoW 存入全局/thread-local/Workflow 状态），检测企图必须经项目自有错误立即失败；可复用业务行为提取为 Domain Service / transaction-neutral Application Service / 接收显式 Ports 的内部操作；Explicit Composite Application Use Case 拥有唯一外层 UoW 与唯一最终提交点（记录跨 Aggregate 不变量、显式类型化 Ports、保持唯一模块/表所有权、必要时经 Public Application Contract）；SAVEPOINT 不是嵌套 UoW、不由 Application UoW Port 暴露，有限 Infrastructure 级使用仍受 DQ-05 治理（不创建独立业务 commit、不拆分 DEC-035、不包裹外部调用/等待、不授予 Repository 提交权、不削弱失败回滚）；UoW Port 默认不暴露 flush()，Infrastructure 内部 flush 非业务 commit、不代表业务成功，flush 失败必须回滚并丢弃当前 UoW；Engine/sessionmaker 可为 Composition Root 长生命周期资源，具体 Session 短生命周期（一个 UoW 一个本地 Command），全局可变 Session 禁止，scoped_session/thread-local/ContextVar ambient 机制不得作主要事务所有权或依赖注入机制；每个并发 Command/Worker 执行/Retry/Rerun/Resume 使用独立 UoW 与独立 Session；与 DQ-05 一致（Prepare 与 Commit 不同 UoW、Execute Outside Transaction 无 UoW、Human Review/Interrupt/backoff 不持有 UoW、UoW 不序列化进 Checkpoint、不在 Resume 恢复）；纯读 Application Query 使用独立短 Query Scope（不暴露 commit、查询后关闭 Session 释放连接、不返回 ORM entity/lazy 关系、不复用 Command UoW、不成为跨模块持久化 API），读取结果参与后续原子变更或并发决策时须在拥有最终 commit 的 UoW 内或于 Commit 事务内重新校验（衔接 DQ-04/05）；Candidate B（退出自动提交）作为项目 UoW 模型拒绝（Context Manager 仍允许生命周期清理）、Candidate C（Repository 管理事务）拒绝；并发/锁/重试留 DQ-07、幂等留 DQ-08、Outbox/Dispatch 留 DQ-09、Event/Audit 留 DQ-10、HTTP 请求作用域留 RFC-004、Workflow/Checkpoint 运行时留 RFC-003、测试分类留 DQ-16；持久化语义验证使用真实 PostgreSQL（覆盖清单见 DQ-06 第 50 点）（详见 §33 Decision Log） |

| RFC-002-DQ-07（2026-08-02 用户 ACCEPTED） | 分层并发控制（Layered Concurrency Control）取代单一通用锁机制；普通业务状态修改（Business Current Truth、Aggregate Roots、Current Truth Pointers、Stage State、Review Package state 等受保护可变记录）默认使用 DQ-04 乐观并发协议（revision + expected_revision + 条件更新 + affected-row 校验），expected_revision 不匹配是语义业务冲突、不得盲目重试（并发审批返回冲突、过期 Human Review 拒绝、同时失效仅一个成功、后写者不得静默覆盖、过期外部结果不得重绑新 Domain Version），`version_id_col` 仍为 Infrastructure 机制（stale-state 翻译为项目自有结果）、ORM bulk UPDATE/DELETE 不得绕过 revision；命名数据库唯一约束是重复业务事实的最终完整性防线（至少覆盖重复 Domain Version identity/numbering、重复正式 Review Decision identity、重复已提交业务 Command identity、后续决定要求的重复 Dispatch/Attempt identities、其他命名业务唯一性不变量），唯一约束违反不得统一视为可重试，错误边界必须识别命名约束并至少区分已完成重复操作/幂等重放/version-number 分配竞争/重复 Review Decision/真实完整性缺陷/未分类违反（完整幂等键层级留 DQ-08）；Duplicate Resume / 并发 Worker 执行 / 同一并发范围执行所有权要求 Durable Execution Guard / Durable Lease（concurrency_scope_id、holder/Attempt identity、获取时间、过期时间、单调递增 generation/fencing_token、active/released/expired 生命周期；确切表/字段/索引/物理存储留实现设计与 DQ-13），Lease 获取在短 PostgreSQL 事务内完成且必须在长执行开始前提交、提交后释放行锁/Session/UoW/连接，Worker 在 LLM 执行/外部 HTTP 或工具调用/Human Review 等待/Workflow Interrupt/retry backoff/长计算/跨进程执行期间不得持有 PostgreSQL 行锁；每次成功获取/接管/重新分配颁发单调递增 fencing_token，持旧 fencing_token 的过期 Worker 即使仍运行且返回看似有效结果也不得提交 Business Current Truth；Worker Commit 必须在最终短事务内验证 expected_revision + 当前 Lease Holder + 当前 fencing_token + 当前 Attempt/Run identity + 后续 DQ-08 接受的适用幂等身份 + Command 要求的全部业务不变量，Lease 过期/释放/被他人获取则旧 Worker 结果作为 stale 拒绝；进程本地 asyncio.Lock/threading.Lock/mutex/内存任务锁仅为非权威优化（减少重复工作），不得作为业务正确性来源，正确性须在进程重启/Worker 崩溃/多 Worker 进程/多部署副本/机器替换/内存状态丢失下保持；SELECT FOR UPDATE SKIP LOCKED 仅限显式队列式 Claim 短事务（select candidate → lock → assign durable holder/Lease/fencing token → commit → release lock and connection → execute outside the transaction），不得用于普通 Current Truth 读取、Human Review 读取、完整结果集查询、绕过 expected_revision 冲突、静默忽略正在修改的业务对象、跨外部调用持有执行所有权；SELECT FOR UPDATE/NOWAIT 等悲观行锁不是全局默认，Use Case 采用须记录受保护不变量/为何乐观不足/确切锁定行/确定性锁顺序/blocking-NOWAIT-SKIP LOCKED 行为/最大事务时长/超时与错误翻译/重试安全性/真实 PostgreSQL 证据，多对象事务使用确定性全局锁顺序；Session-level PostgreSQL Advisory Locks 作为默认或权威机制被禁止，Transaction-level Advisory Locks 非默认（仅自然行无法表达并发范围时经独立架构审查考虑）；SQLSTATE 40001 serialization_failure 与 40P01 deadlock_detected 归类为可能瞬时的数据库事务失败，有限自动重试由 Application Transaction Runner / Command Executor 拥有，Repository/Session/UoW 实现不得静默自重试循环，每次重试重新开始整个短事务 + 全新一一次性 UoW + 全新 Session + 重新加载状态 + 重新评估前置条件 + 重新运行 revision 与 Lease 验证 + 丢弃失败尝试 ORM entities，默认预算 = 1 次初始 + 最多 2 次重试 = 共计 3 次尝试，无限/无界重试禁止，backoff/jitter 在开放事务/UoW/Session 之外（具体参数/指标/告警阈值可在 RFC-007 配置，有界要求不得移除）；不得盲目或自动重试：expected_revision 不匹配、stale fencing_token、丢失/过期 Lease、过期 Human Review 提交、业务不变量拒绝、过期外部结果、未分类 unique_violation、未定义策略的 lock_not_available/NOWAIT 失败（已分类重复操作仅在 DQ-08 幂等语义下转换为幂等响应）；外部 LLM/HTTP Provider/工具执行不得进入数据库事务重试循环，业务前置条件仍有效时 Commit 事务可使用已产生的不可变外部结果重试但不得自动重新调用 Provider；五类并发场景控制组合：duplicate resume = Durable Lease + fencing_token + DQ-08 幂等身份，concurrent approval = expected_revision CAS + 唯一 Review Decision identity，stale worker = Lease Holder 验证 + fencing_token + expected_revision，repeated command = 命名数据库唯一约束 + DQ-08 幂等记录，simultaneous invalidation = 对所属 Aggregate/Stage State/Current Truth Pointer 的 expected_revision CAS；LangGraph thread_id 与 Checkpoint identity 仅定位工作流状态与恢复位置，不得视为 Business Concurrency Lock / Durable Lease / fencing_token / 业务 Idempotency Record / 单一活动 Resume 证明；Concurrency Scenario Matrix 为持久化或并发控制实现开始前的必备产出（至少标识 Scenario/Concurrency Scope/Protected Business Invariant/Optimistic Revision/Database Unique Constraint/Durable Lease/fencing_token/Pessimistic Lock/Retry classification/Retry owner/maximum attempts/user-visible conflict result/related DQ-DEC-RFC），其创建不由 DQ-07 接受授权；真实 PostgreSQL 多 Worker Concurrency Technical Spike 为并发控制实现授权前的必备验证（真实 PostgreSQL + 多个独立连接 + 至少两个独立执行 Worker/进程 + 确定性故障与时序注入 + 冲突后零部分 Current Truth 写入证据；至少验证两并发 Resume 产生一个权威 Lease、Lease 过期接管产生更高 fencing_token、旧 Worker 无法提交、同 expected_revision 两审批仅一个提交、SKIP LOCKED 不双重领取、40001/40P01 重试使用全新 UoW/Session、事务重试不重复 Provider 调用、并发版本分配无重复 Domain Version、冲突回滚零部分写入），Spike 必需但本决定不授权、Spike Issue/Branch/PR/代码/测试/基础设施创建需单独明确用户授权；DQ-07 不决定完整幂等键层级与响应重放（→DQ-08）、Outbox 与 Dispatch Claim 实现（→DQ-09）、Event/Audit 持久化顺序（→DQ-10）、Checkpoint 并发与 Runtime 对账（→RFC-003）、API 冲突状态码或 ETag/If-Match 协议（→RFC-004）、完整持久化测试分类与 CI 执行设计（→DQ-16）、运维重试指标与阈值（→RFC-007）；详细持久化测试组织归 DQ-16，所有正式并发语义测试使用真实 PostgreSQL（详见 §33 Decision Log） |

| RFC-002-DQ-08（2026-08-02 用户 ACCEPTED） | 分层幂等模型（Layered Idempotency Model）：项目采用分层幂等模型，不采用一张跨模块、跨所有语义（Command、Workflow、Consumer、Dispatch、Provider 调用）的 Universal Idempotency Table；不同幂等层由相应 Owning Module 持久化（每份幂等记录有且仅有一个 Owning Module，遵守 DQ-02 表所有权与跨模块访问边界；具体模块可为自身同类 Commands 使用模块私有 Command Idempotency Table）；所有幂等层共享统一概念与行为契约（logical operation identity / owning module / idempotency scope / idempotency key / input fingerprint / execution status / retry-rerun semantics / unique constraint / result replay semantics / atomic transaction boundary），统一概念契约不意味着统一物理表；Candidate B（分层各自存储）作为主要持久化方向接受，Candidate C（天然幂等语义设计）作为强制设计原则接受（状态修改尽量采用 set/ensure/replace-to-desired-state/compare-and-set，避免无保护 increment/append/toggle/duplicate create，但不得替代显式记录、唯一约束或执行所有权控制，尤其涉及创建 Domain Version、外部副作用、Review Decision、Dispatch、计费或配额、append-only Audit、只能发生一次的正式业务事实），Candidate A 作为跨模块万能 Idempotency Table 拒绝；身份模型必须明确区分 Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity，不得混用或由通用 ID 字段隐式取代：Command ID 表示一次逻辑状态修改 Command（Application 层生成），数据库 Retry 或执行 Retry 复用同一 Command ID，Intentional Rerun 创建新 Command ID 并保留 `rerun_of`/`parent_command_id` 或等价关系；Idempotency Key 表示调用者要求去重与结果重放的逻辑身份，必须在明确 Idempotency Scope 内唯一（Scope 至少等价表达 owning module / operation type / target business scope / tenant-account scope 如未来存在 / idempotency key），不得只按整库裸 Key 推断语义；Attempt ID 表示一次具体执行尝试、每次 Retry 创建新 Attempt ID、不是业务幂等 Key、不得用于判断逻辑 Command 是否已完成；Stage Run ID 表示一次有意启动的 Stage Run，同一 Stage Run 内 Retry 保持相同 Stage Run ID，Intentional Rerun 创建新 Stage Run ID；Retry 不得创建新的正式 Domain Version，Intentional Rerun 成功后可以产生新的正式 Domain Version；Review Decision ID 是不可变正式业务决定身份、必须由命名唯一约束保护、同一 Review Decision 不得正式提交两次；Dispatch ID 的产生、Outbox 持久化和 Delivery 语义继续由 DQ-09 决定；Retry 身份语义 = same Command ID + same Idempotency Key + same Stage Run ID + same Input Fingerprint + new Attempt ID + no new intended business operation，Intentional Rerun 身份语义 = new Command ID + new logical Idempotency identity + new Stage Run ID + new Attempt ID + explicit relation to previous run + may produce new business version after successful commit，Retry 与 Rerun 不得通过是否发生异常隐式判断、必须由明确 Application Intent 区分；每个需要幂等保护的操作必须计算 Versioned Input Fingerprint（基于规范化后的业务有效输入，不得直接依赖原始 JSON 字节顺序或任意序列化结果；定义必须明确 canonicalization version / fingerprint schema version / hash algorithm / included business fields / excluded transport and observability fields；应包含决定业务效果的字段——target business identity、expected revision、base Domain Version、Command parameters、Source/Evidence Version references、selected operation mode；不应包含 trace ID、arrival timestamp、retry counter、Attempt ID、connection metadata、不影响业务效果的观测字段）；同一 Scope + Key + 相同 Fingerprint 表示同一逻辑操作（重放），同一 Scope + Key + 不同 Fingerprint 必须返回 Idempotency Key Conflict（不得覆盖原记录、不得执行新业务操作、不得把旧结果重放为新请求结果、不得盲目自动重试）；幂等执行状态机至少表达 IN_PROGRESS / SUCCEEDED / FAILED_TERMINAL / ABANDONED-EXPIRED-RETRYABLE 等非终局状态（精确 Enum 名称留实现设计）：IN_PROGRESS 表示逻辑操作已被一个有效 Attempt 领取，重复请求看到有效 IN_PROGRESS 不得再次执行相同业务副作用；IN_PROGRESS 执行所有权必须与 DQ-07 的 Durable Lease / Lease Holder / Attempt ID / fencing_token 协同，只有当前有效 Lease Holder 和 fencing_token 可以把幂等记录转换为最终成功状态，Lease 过期/被接管/fencing_token 失效后旧 Worker 不得写入 SUCCEEDED；Checkpoint 和 LangGraph thread_id 不作为 Business Idempotency Record；业务成功时 Business Current Truth 更新、Domain Version、Formal Evidence Links、Current Truth Pointer、Stage State、Audit Record、Idempotency Record 成功状态、不可变 Application Result Snapshot 或结果引用必须在同一个 DEC-035 Atomic Business Commit 中提交，业务事务回滚不得留下 SUCCEEDED Idempotency Record，业务 Commit 成功但响应丢失时相同 Scope + Key + Fingerprint 后续请求必须重放原 Application Result（重放不得再次执行业务副作用；重放结果必须是项目自有稳定 Application Result Snapshot 或不可变结果引用；幂等记录不得直接保存或返回 ORM Entity / SQLAlchemy Session / Python Exception 对象 / 原始数据库错误 / 未脱敏 Secret / 与传输层强绑定的可变对象）；HTTP Status / Headers / Response Body 和 Header 名称继续由 RFC-004 决定；失败分类：确定性终局业务结果（已正式确定且再次执行不会改变的业务拒绝或冲突）可以记录并稳定重放，瞬时基础设施失败（连接超时、SQLSTATE 40001、SQLSTATE 40P01、临时 Provider 不可用、Worker Crash、Lease 过期、可恢复网络故障）不得永久固化为终局结果，瞬时失败可以使用相同逻辑幂等身份重试但必须创建新 Attempt ID 且继续受 DQ-07 有限重试、Lease 和 Fencing Token 规则约束，领取操作和副作用开始前的纯输入验证失败可以不创建可重放终局记录；分层幂等四层：(a) Business Command Idempotency Record 由执行该业务状态修改的模块拥有、与业务状态更新同一 PostgreSQL 事务提交、不得成为跨模块共享读写表；(b) Message Consumer Deduplication Record 由消费模块拥有、使用 Message ID/Dispatch ID + Consumer Scope 组合唯一、Dedup Marker 必须与消费产生的业务更新同事务提交、不得先提交 Dedup Marker 再执行实际业务写入；(c) Workflow Retry Idempotency 中 Runtime 负责 Attempt 和运行位置、Business Module 负责防止重复 Business Commit、Resume 必须经过 Command Identity + 数据库幂等记录 + Lease 与 Fencing 校验、Checkpoint 不替代业务幂等记录；(d) External Provider Idempotency 中 Provider Adapter 使用稳定 Provider Call Identity、同一逻辑调用 Retry 复用相同 Provider Idempotency Key、Intentional Rerun 使用新 Provider Call Identity、Provider Key 必须绑定 Input Fingerprint、数据库事务 Retry 不得生成新的 Provider Key；Provider 原生支持 Idempotency Key 时应稳定映射系统逻辑调用身份，不支持原生 Idempotency 时 Provider/Integration 模块必须维护 Durable Call Ledger（至少记录 Provider Call Identity / Input Fingerprint / execution status / Attempt relationship / result reference / reconciliation state），已完成 Provider 调用不得因数据库事务重试被自动再次调用，具体 Provider 对账和补偿策略留给相应 Provider RFC 或 Adapter 设计；物理模型与后续边界：具体表名、字段名、索引、分区与 Storage Placement 留实现设计和 DQ-13，Retention / TTL / 删除和 Key 再利用策略由 DQ-15 决定（DQ-15 决定前不得假设 Key 可被短期删除、自动复用归档 Key、依赖内存 Cache 作为权威幂等存储），Fingerprint 和结果存储不得无必要复制敏感原始载荷，Hashing / Encryption / Redaction / Secret 和 PII 规则继续由 DQ-17 决定；DQ-08 不提前决定 Outbox/Dispatch 表和 Relay（→DQ-09）、Event/Audit 分类和持久化顺序（→DQ-10）、Workflow Runtime/Checkpoint 协调（→RFC-003）、HTTP 幂等 Header/状态码和响应协议（→RFC-004）、Retention 数值（→DQ-15）、完整测试分类和 CI（→DQ-16）、Security/Encryption/PII（→DQ-17）；开始幂等实现前必须完成 Idempotency Identity Matrix（至少包含 Operation / Owning Module / Logical Command ID / Idempotency Scope / Idempotency Key Source / Retry Identity / Rerun Identity / Attempt ID / Stage Run ID / Input Fingerprint Fields / Fingerprint Schema Version / State Machine / Unique Constraint / Atomic Transaction Boundary / Result Replay / Provider Idempotency / Retention Owner / Related DQ/DEC/RFC），DQ-08 接受不授权创建该 Matrix（Idempotency Identity Matrix Creation = NOT AUTHORIZED），本决定不要求新增独立 Technical Spike（DQ-07 已要求的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效并应覆盖幂等并发场景）；所有正式幂等语义验证必须使用真实 PostgreSQL，后续测试至少覆盖同 Key+同 Fingerprint 并发请求只有一次业务效果、同 Key+不同 Fingerprint 返回冲突、Commit 成功但响应丢失后重放原结果、Retry 不创建新 Domain Version、Intentional Rerun 创建新逻辑身份、Review Decision 只提交一次、Consumer Dedup 与业务更新同事务、Worker Crash 后 IN_PROGRESS 接管、stale fencing_token 无法完成记录、Provider 成功但数据库 Commit 失败后不重复调用、瞬时失败创建新 Attempt、终局结果稳定重放，详细测试组织和 CI 策略继续由 DQ-16 决定（详见 §33 Decision Log） |

### 4.3 事实校正（重要）

全仓库**无**字面等号短语「Business Database = Current Truth」「Checkpointer = Recovery」。**权威原文**为 architecture-baseline-v1 §2：「三类存储分离：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）物理分离；**Checkpoint ≠ Current Truth**」，及 DEC-023「LangGraph Checkpointer **仅**承载执行恢复、图状态快照、Interrupt 和 Resume」。本 RFC 一律引用真实原文，不用转述等号形式。

### 4.4 Spike 证据与缺口

Spike-001 以三个物理 SQLite 文件（`business/runtime/checkpoints.sqlite`）验证了关键运行时安全（25/25 测试）：spike-04 中提交回滚（partial_write_count==0）、spike-06 重复 review submit 拒绝、spike-08 过期 checkpoint 拒绝、spike-10 取消无部分写入。但留下缺口：**R-1（并发/分布式未验证——单线程同步）、R-3（生产 Checkpointer 未锁定）、R-4（规模/性能未验证）**。这些缺口是 DQ-01/07/13/16 的直接动机。

---

## 5. Problem（问题）

在 RFC-001 确立「Application 拥有事务、Port 由 Application 定义、Infrastructure 实现、Durable Dispatch Boundary」之后，项目仍缺少一份**生产可用的持久化与事务架构**，具体表现为：

1. **主持久化技术未选型**——业务 Current Truth 用 PostgreSQL 还是 SQLite 未定；SQLite 全库单写者能否支撑 API+Worker 两进程并发写未知。（**DQ-01 已于 2026-08-01 由用户正式决定：PostgreSQL 是唯一受支持的权威数据库语义，此问题已解决，见 §33 Decision Log。**）
2. **并发控制未定型**——DEC-029「Optimistic Lock/Revision Number/ETag/Database Lock 尚未确认」；Spike 单线程未验证并发（R-1）。（**DQ-07 已于 2026-08-02 由用户正式决定：分层并发控制（Layered Concurrency Control）——乐观 revision 默认 + 命名唯一约束最终防线 + Durable Lease + 单调 fencing_token 执行所有权 + SKIP LOCKED 仅限队列式 Claim + Session-level Advisory Lock 禁止 + 40001/40P01 由 Application Transaction Runner 最多三次总尝试重试（语义冲突不盲目重试）；Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Technical Spike 为实现前置条件（均 REQUIRED 但未授权），见 §33 Decision Log。**）
3. **幂等模型未落地**——DEC-033 要求多层幂等，但存储形态、键体系、判重与业务更新的事务关系未定。（**DQ-08 已于 2026-08-02 由用户正式决定：分层幂等模型——Candidate B 为主（各幂等层由 Owning Module 分层存储）+ Candidate C 为强制设计原则（天然幂等 set/ensure/replace 语义，不替代显式幂等记录与数据库唯一约束）+ 统一语义契约（非统一物理表）；Candidate A 作为跨模块万能 Idempotency Table 被拒绝；Retry 复用 Command ID/Idempotency Key/Stage Run ID/Input Fingerprint 并创建新 Attempt ID，Intentional Rerun 创建新逻辑身份；同 Scope+Key+Fingerprint 重放原 Application Result、不同 Fingerprint 返回 Idempotency Key Conflict；幂等成功记录与 Business Current Truth 同一 DEC-035 原子提交；IN_PROGRESS 与 DQ-07 Durable Lease/Fencing Token 协同；Idempotency Identity Matrix 为实现前置条件（REQUIRED 但未授权），见 §33 Decision Log。**）
4. **Durable Dispatch 落库形态未定**——RFC-001-DQ-07 把 backend 候选移交 RFC-002/003，是否引入 Transactional Outbox 未决。
5. **Checkpoint 与业务库的物理边界未定**——逻辑分离已定（DEC-024/034），但同库/分库、生命周期、对账权威未落地（R-3）。
6. **Schema 演进、数据保留、测试策略、安全边界**——均「仍待确认」。

没有这些决定，任何 Business Repository / Current Truth 的生产实现都只能是临场技术选择（DEC-038 明令禁止）。

---

## 6. Goals（目标）

- 把 DEC-024/029/033 与 RFC-001 的持久化约束转化为 **17 个完整 Decision Question**，每个含候选、取舍、失败模式、对后续 RFC 的影响与架构建议。
- 用**一手官方证据**（SQLAlchemy 2.x、LangGraph Checkpointer、PostgreSQL/SQLite/Alembic、Fowler/microservices.io/EIP 模式定义）支撑每个候选，并区分 `[DEC 约束]/[官方能力]/[架构推断]/[未决假设]`。
- 给出**推荐架构（Proposed，非 Accepted）**：一组相互自洽的 Recommendation，供用户逐项审查。
- 严格划定 RFC-002 决策权边界，**不**替 RFC-003~007 做实现决定。
- 填补 Spike R-1/R-3/R-4 的**决策层**缺口（测试验证留 DQ-16）。

## 7. Non-goals（非目标）

- **不**实现任何持久化、数据库、ORM、迁移、Repository、UoW、Outbox、Queue、LangGraph、API 或业务代码。
- **不**创建或修改 `apps/backend/src/**`、database models、ORM entities、SQLAlchemy/Alembic 配置、迁移文件、Repository/UoW/Outbox 实现、API endpoints、worker 代码、queue 配置、LangGraph 生产图、业务模块、部署文件、生产 secret。
- **不**修改 Accepted RFC-001、Accepted DEC 文件、FND-001/002/003 实现、GitHub Actions、Branch Protection、Dependabot/Secret Scanner 配置。
- **不**决定 LangGraph 节点结构、API endpoints、HTTP schema、检索 chunking、向量库、embedding 模型、LLM provider、prompt 运行时、logging vendor、metrics backend、deployment topology。
- **不**虚构数据保留周期数值。

---

## 8. Decision Questions（决策问题）

**DQ-01/02 已于 2026-08-01、DQ-03/04/05/06/07/08 已于 2026-08-02 由用户正式决定（均 ACCEPTED；DQ-01~07 Accepted with Revision，DQ-08 Accepted with Major Revision，见 §33 Decision Log）；DQ-09~17 仍 PROPOSED — User Decision: PENDING**。完整 13 字段版本见 [rfc-002-decision-questions.md](rfc-002-decision-questions.md)。

| DQ | 主题 | 归属 | 置信度 |
|---|---|---|---|
| DQ-01 | Primary Persistence Technology | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-01） | 中-高（历史置信度） |
| DQ-02 | Persistence Ownership / Boundaries | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-01） | 高（历史置信度） |
| DQ-03 | Aggregate / Persistence Boundary | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 高（历史置信度） |
| DQ-04 | Domain State Versioning | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 中-高（历史置信度） |
| DQ-05 | Transaction Boundary | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 中-高（历史置信度） |
| DQ-06 | Unit of Work Model | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 高（历史置信度） |
| DQ-07 | Concurrency Control | RFC-002 OWNS — **ACCEPTED**（Layered Concurrency Control，2026-08-02） | 中（历史置信度） |
| DQ-08 | Idempotency Model | RFC-002 OWNS — **ACCEPTED**（Candidate B primary + Candidate C principle，2026-08-02） | 中-高（历史置信度） |
| DQ-09 | Transactional Outbox / Dispatch | RFC-002 OWNS（backend 移交 RFC-003） | 中 |
| DQ-10 | Event & Audit Persistence | RFC-002 OWNS | 高 |
| DQ-11 | Snapshot vs History | RFC-002 OWNS | 高 |
| DQ-12 | Source & Evidence Persistence | RFC-002 OWNS（检索移交 RFC-005） | 中 |
| DQ-13 | Workflow Checkpoint Separation | RFC-002 OWNS（实现移交 RFC-003） | 高 |
| DQ-14 | Schema Evolution & Migrations | RFC-002 OWNS（不创建真实迁移） | 中-高 |
| DQ-15 | Data Retention & Deletion Boundary | RFC-002 OWNS（不虚构周期） | 中 |
| DQ-16 | Persistence Testing Strategy | RFC-002 OWNS | 中-高 |
| DQ-17 | Security & Sensitive Data Boundary | RFC-002 OWNS（不实现 Secret 管理） | 高 |

---

## 9. Proposed Solution（提案方案）

### 9.1 架构主线

在 RFC-001 的分层骨架内，持久化与事务架构的核心主张（Recommendation；**其中第 1、2 条已分别由 DQ-01、DQ-02 Accepted Decision 取代，第 3 条的事务边界与执行模式已由 DQ-05 Accepted Decision（2026-08-02）取代、其 Unit of Work Port 形态已由 DQ-06 Accepted Decision（2026-08-02）正式决定，第 4 条的聚合边界解释已由 DQ-03 Accepted Decision 修订、版本语义与提交协议已由 DQ-04 Accepted Decision（2026-08-02）补充正式决定，第 5 条的并发版本底座已由 DQ-04 Accepted Decision 取代、分层并发控制模型已由 DQ-07 Accepted Decision（2026-08-02）正式决定，第 6 条的幂等模型已由 DQ-08 Accepted Decision（2026-08-02）正式决定（重大修订：分层模块私有幂等存储取代统一幂等表），见 §33**）：

1. **主持久化 = PostgreSQL，Business Current Truth Repository 唯一受支持的权威数据库语义（DQ-01 Accepted Decision，2026-08-01）**：技术栈 = **PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**；**本地开发使用 PostgreSQL**；schema、约束、迁移、事务行为、并发行为与持久化正确性均以 PostgreSQL 语义定义；SQLite **不是**受支持的 backend（SQLite-first → PostgreSQL-later 路线已拒绝）。历史 Recommendation「PG 为目标、本地可用 SQLite 以 PG 语义为准」已被取代（Superseded by Accepted Revision）。（原提案中 SQLAlchemy sync-first 与 Alembic 的方向延续自 RFC-001-DQ-07 Sync-first 约束。）
2. **持久化所有权与模块边界（DQ-02 Accepted Decision，2026-08-01）**：MVP **单一 PostgreSQL 数据库服务**；**每张业务表有且仅有一个所有模块**；所有模块独占拥有其 Repository Port 定义、Infrastructure Repository 实现、ORM / Persistence Models、schema 与 migration 变更、状态修改 Application Use Cases；跨模块读取经目标模块 **Public Application Query**、跨模块状态修改经所有模块 **Public Application Use Case**；**Direct SQL / ORM / Repository 跨模块访问禁止**，边界由 Import Linter + AST/Architecture Tests + Repository Ownership Tests + Migration Ownership Conventions + PR 审查规则强制（单独代码审查不充分）。**每模块独立 PostgreSQL schema 暂缓**（MVP 不要求；具体物理命名留待实现设计，不得削弱所有权）。历史 Recommendation「单库 + 按模块分 schema/表前缀」中的独立 schema 部分未被采纳（Superseded by Accepted Revision）。**三类存储逻辑分离恒定**（DEC-034）：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）的逻辑职责分离不受影响；**其物理划分（同实例/独立 schema/Checkpoint 数据库产品/Runtime 物理存储/Checkpoint 生命周期）不由 DQ-02 决定，继续由 DQ-13 决定（PROPOSED / PENDING）**。
3. **业务事务由 Application Use Case 拥有，事务边界与执行模式由 DQ-05 Accepted Decision（2026-08-02）正式决定**：Business Transaction Owner = Application（Entrypoint / Graph Node 不 begin/commit）；Transactional Application Command = 一个短显式事务 + 一个最终提交点；长流程业务操作 = 多个短事务 + 无事务执行阶段；执行模式 = Prepare → Execute Outside Transaction → Commit；**外部调用不持有开放数据库事务、Human Review 不跨开放事务、Workflow 暂停不跨开放事务、SQLAlchemy Session 不跨 Workflow 边界（四项 PROHIBITED）**；**Commit-time Revision Revalidation 必选**（衔接 DQ-04 `expected_revision` compare-and-swap 协议）；DEC-035 六要素单事务保持有效；**External Result Before Commit 非 Current Truth**；**默认 PostgreSQL 隔离级别 = READ COMMITTED**（更强隔离级别、悲观锁、SELECT FOR UPDATE / SKIP LOCKED、40001 / 40P01 重试与重试上限已由 **DQ-07 Accepted Decision（2026-08-02）** 正式决定：分层并发控制——悲观锁非全局默认、SKIP LOCKED 仅限队列式 Claim 短事务、Session-level Advisory Lock 禁止、40001/40P01 由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试、语义冲突不盲目重试，见第 5 条与 §33）；**SAVEPOINT 仅为有限 Infrastructure 机制、嵌套业务事务禁止、与外部供应商的分布式事务拒绝**。历史 Recommendation「Use Case 拥有唯一提交点、外部调用不持有 DB 事务、长流程拆多个短事务（[架构推断]）」已被取代（Superseded by Accepted Revision）。**UoW Port 形态已由 DQ-06 Accepted Decision（2026-08-02）正式决定：UnitOfWork Port 由 Application 定义、Infrastructure 提供 SQLAlchemy 实现（Session 为不暴露的 Infrastructure 细节）；一次性 UoW（NEW→ACTIVE→COMMITTED/ROLLED_BACK→CLOSED）对应一个 Session / 一个短事务 / 一个最终结果；Application Use Case 显式 commit、Context 退出不得自动提交、未 commit 或异常退出 = rollback/close/discard；Repository 无 begin/commit/rollback/close 权限且不暴露 Session、无 Registry/Service Locator；嵌套业务 UoW 禁止（检测必须立即失败）；Composite Application Use Case 拥有唯一外层 UoW 与唯一最终提交点；纯读 Query 使用独立短 Query Scope（见 §33）**。
4. **Atomic Business Commit 六要素单事务**（DEC-035）为统一事务**提交协议**（恒定有效；「以六要素划分聚合边界」的解释已由 **DQ-03 Accepted Decision，2026-08-02** 修订：聚合边界 = 业务不变量 + 唯一模块所有权，六要素不是聚合成员资格判据）。**版本语义与提交协议由 DQ-04 Accepted Decision（2026-08-02）正式决定**：`domain_version_id`（不可变、Application 层 INSERT 前生成、opaque UUID）/ `version_number`（逻辑业务对象内单调递增、唯一性约束）/ `revision`（受保护可变记录的独立 NOT NULL 乐观并发 token）三类分离；产生新顺序版本时，版本分配与 Current Truth revision 校验构成一个安全提交协议（读取 pointer → 校验 `expected_revision` → 分配 `version_number` → 插入不可变 Domain Version → 条件更新 pointer → 递增 `revision` → commit），任何 revision/唯一性冲突或写入失败整体回滚；六要素保持同一事务。
5. **分层并发控制（DQ-07 Accepted Decision，2026-08-02，Accepted Direction = LAYERED CONCURRENCY CONTROL）**：项目采用分层并发控制而非单一通用锁机制，四层各司其职——**① 普通业务状态修改默认乐观 revision**（DQ-04 协议：revision + expected_revision + 条件更新 + affected-row 校验；expected_revision 不匹配是语义业务冲突，不得作为瞬时数据库失败盲目重试：并发审批返回冲突、过期 Human Review 拒绝、同时失效仅一个成功、后写者不得静默覆盖较新状态、过期外部执行结果不得重绑较新 Domain Version）；**② 命名数据库唯一约束是重复业务事实的最终完整性防线**（至少覆盖重复 Domain Version identity/numbering、重复正式 Review Decision identity、重复已提交业务 Command identity、后续决定要求的重复 Dispatch/Attempt identities、其他命名业务唯一性不变量；唯一约束违反不得统一视为可重试，错误边界必须识别命名约束并至少区分已完成重复操作/幂等重放/version-number 分配竞争/重复 Review Decision/真实完整性缺陷/未分类违反；完整幂等键层级留 DQ-08）；**③ Durable Lease + 单调递增 fencing_token 是执行所有权机制**（Duplicate Resume、并发 Worker 执行、同一并发范围执行所有权要求 Durable Lease；Lease 获取在短 PostgreSQL 事务内完成且必须在长执行开始前提交、提交后释放行锁/Session/UoW/连接；Worker 在 LLM 执行/外部 HTTP 或工具调用/Human Review 等待/Workflow Interrupt/retry backoff/长计算/跨进程执行期间不得持有 PostgreSQL 行锁；每次成功获取/接管/重新分配颁发单调递增 fencing_token；Worker Commit 在最终短事务内验证 expected_revision + Lease Holder + fencing_token + Attempt/Run identity + 后续 DQ-08 幂等身份 + 业务不变量；持旧 fencing_token 的过期 Worker 即使仍运行也不得提交；进程本地 asyncio.Lock/threading.Lock/mutex 仅为非权威优化，正确性须在进程重启/崩溃/多进程/多副本/机器替换/内存丢失下保持）；**④ SELECT FOR UPDATE SKIP LOCKED 仅限显式队列式 Claim 短事务**（select candidate → lock → assign durable holder/Lease/fencing token → commit → release → execute outside transaction；不得用于普通 Current Truth 读取、Human Review 读取、完整结果集查询、绕过 expected_revision 冲突、静默忽略正在修改的对象、跨外部调用持有执行所有权）。悲观行锁（FOR UPDATE/NOWAIT）不是全局默认，采用须完整记录（受保护不变量/为何乐观不足/锁定行/确定性锁顺序/行为/最大事务时长/超时与错误翻译/重试安全性/真实 PostgreSQL 证据），多对象事务使用确定性全局锁顺序；**Session-level PostgreSQL Advisory Locks 禁止为默认或权威机制，Transaction-level Advisory Locks 非默认（仅自然行无法表达并发范围时经独立架构审查考虑）**。**40001 serialization_failure 与 40P01 deadlock_detected 归类为可能瞬时的数据库事务失败**：有限自动重试由 **Application Transaction Runner / Command Executor** 拥有（Repository/Session/UoW 不得静默自重试循环），每次重试 = 全新一次性 UoW + 全新 Session + 重新加载状态 + 重新评估前置条件 + 重新运行 revision 与 Lease 验证 + 丢弃失败尝试 ORM entities；**默认预算 = 1 次初始 + 最多 2 次重试 = 共计 3 次尝试**，无限/无界重试禁止，backoff/jitter 在开放事务之外（具体参数可在 RFC-007 配置，有界要求不得移除）；**不得盲目重试**：expected_revision 不匹配、stale fencing_token、丢失/过期 Lease、过期 Human Review 提交、业务不变量拒绝、过期外部结果、未分类 unique_violation、未定义策略的 NOWAIT 失败；**外部 LLM/HTTP/工具执行不得进入事务重试循环**，Commit 事务可在业务前置条件有效时使用已产生的不可变外部结果重试、但不得自动重新调用 Provider。**五类并发场景控制组合**：duplicate resume = Durable Lease + fencing_token + DQ-08 幂等身份；concurrent approval = expected_revision CAS + 唯一 Review Decision identity；stale worker = Lease Holder 验证 + fencing_token + expected_revision；repeated command = 命名数据库唯一约束 + DQ-08 幂等记录；simultaneous invalidation = 对所属 Aggregate/Stage State/Current Truth Pointer 的 expected_revision CAS。**LangGraph thread_id 与 Checkpoint identity 仅定位工作流状态与恢复位置，不得视为 Business Concurrency Lock / Durable Lease / fencing_token / 业务 Idempotency Record / 单一活动 Resume 证明**。**Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Concurrency Technical Spike 均为实现前置条件（REQUIRED），但均不由 DQ-07 接受授权**（Matrix 需后续规划或实现就绪授权；Spike 的 Issue/Branch/PR/代码/测试/基础设施创建需单独明确用户授权）。历史 Recommendation「DB 唯一约束兜底 + 乐观 version + task 领取悲观/SKIP LOCKED + 同 task 应用层序列化（[架构推断]）」已被取代（Superseded by Accepted Revision：乐观 revision 接受为默认、唯一约束接受为最终防线、SKIP LOCKED 受限接受为仅队列式 Claim、进程内序列化修订为非权威优化、新增 Durable Lease + fencing_token 执行所有权要求与 Transaction Runner 有界重试）。**版本底座已由 DQ-04 Accepted Decision（2026-08-02）正式决定，默认隔离级别已由 DQ-05 Accepted Decision（2026-08-02）决定为 READ COMMITTED**；完整幂等键层级留 DQ-08、Outbox/Dispatch Claim 实现留 DQ-09、Event/Audit 顺序留 DQ-10、Checkpoint 并发与 Runtime 对账留 RFC-003、API 冲突协议（状态码/ETag/If-Match）留 RFC-004、完整测试分类留 DQ-16、运维重试指标与阈值留 RFC-007。
6. **分层幂等模型（DQ-08 Accepted Decision，2026-08-02，ACCEPTED WITH MAJOR REVISION；Primary Direction = Candidate B，Supporting Principle = Candidate C，Rejected Direction = Candidate A as Universal Table）**：项目采用**分层幂等模型**，不采用一张跨模块、跨所有语义的 Universal Idempotency Table——**① 各幂等层由相应 Owning Module 分层持久化**（每份幂等记录有且仅有一个 Owning Module，遵守 DQ-02 表所有权与跨模块访问边界；模块可为自身同类 Commands 使用模块私有 Command Idempotency Table）；**② 所有幂等层共享统一概念与行为契约**（logical operation identity / owning module / idempotency scope / idempotency key / input fingerprint / execution status / retry-rerun semantics / unique constraint / result replay semantics / atomic transaction boundary），统一概念契约**不**意味着统一物理表；**③ Candidate B（分层各自存储）作为主要持久化方向接受，Candidate C（天然幂等语义）作为强制设计原则接受**（状态修改尽量采用 set/ensure/replace-to-desired-state/compare-and-set，避免无保护 increment/append/toggle/duplicate create；天然幂等语义**不得替代**显式记录、唯一约束或执行所有权控制，尤其涉及创建 Domain Version、外部副作用、Review Decision、Dispatch、计费或配额、append-only Audit、只能发生一次的正式业务事实）；**④ Candidate A 作为跨模块万能 Idempotency Table 拒绝**。**身份模型**必须明确区分 Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity，不得混用或由通用 ID 字段隐式取代：**Retry = same Command ID + same Idempotency Key + same Stage Run ID + same Input Fingerprint + new Attempt ID（no new intended business operation）；Intentional Rerun = new Command ID + new logical Idempotency identity + new Stage Run ID + new Attempt ID + explicit `rerun_of` relation（成功后可产生新 Domain Version）**；Attempt ID 不是业务幂等 Key、不得判断逻辑 Command 是否完成；Retry 不得创建新 Domain Version；Review Decision ID 由命名唯一约束保护、不得正式提交两次；Retry 与 Rerun 必须由明确 Application Intent 区分，不得以是否发生异常隐式判断；Dispatch ID 语义留 DQ-09。**Versioned Input Fingerprint**：每个幂等保护操作计算版本化指纹（明确 canonicalization version / fingerprint schema version / hash algorithm / included business fields / excluded transport-observability fields；基于规范化业务有效输入，不依赖原始 JSON 字节顺序；含 target business identity / expected revision / base Domain Version / Command parameters / Source-Evidence Version references / operation mode；不含 trace ID / arrival timestamp / retry counter / Attempt ID / connection metadata）。**同 Scope + Key + 相同 Fingerprint = 重放原 Application Result（不重复执行业务副作用）；同 Scope + Key + 不同 Fingerprint = Idempotency Key Conflict（不得覆盖原记录、不得执行新业务操作、不得把旧结果重放为新请求结果、不得盲目自动重试）**。**状态机**至少表达 IN_PROGRESS / SUCCEEDED / FAILED_TERMINAL / 非终局状态（精确 Enum 名留实现设计）；**IN_PROGRESS 执行所有权与 DQ-07 Durable Lease / Lease Holder / Attempt ID / fencing_token 协同——只有当前有效 Lease Holder 和 fencing_token 可把记录转换为最终成功状态，Lease 过期/被接管/fencing_token 失效后旧 Worker 不得写入 SUCCEEDED**；Checkpoint 与 LangGraph thread_id 不作为 Business Idempotency Record。**DEC-035 原子提交**：业务成功时 Business Current Truth 更新 + Domain Version + Formal Evidence Links + Current Truth Pointer + Stage State + Audit Record + Idempotency Record 成功状态 + 不可变 Application Result Snapshot/结果引用**同一事务提交**；业务回滚不得留下 SUCCEEDED 记录；Commit 成功但响应丢失时同 Scope+Key+Fingerprint 后续请求重放原结果；重放结果为项目自有稳定快照或不可变引用，不得保存/返回 ORM Entity / Session / Exception / 原始数据库错误 / 未脱敏 Secret / 传输层可变对象；HTTP 状态/Headers/响应协议留 RFC-004。**失败分类**：确定性终局业务结果（已确定且再执行不变的业务拒绝/冲突）可记录并稳定重放；瞬时基础设施失败（连接超时、40001、40P01、临时 Provider 不可用、Worker Crash、Lease 过期、可恢复网络故障）**不得永久固化为终局结果**，可用相同逻辑幂等身份 + 新 Attempt ID 重试（受 DQ-07 有界重试/Lease/Fencing 约束）；副作用前的纯输入验证失败可不创建可重放终局记录。**分层幂等四层**：(a) Business Command Idempotency Record 由执行业务状态修改的模块拥有、与业务更新同一 PostgreSQL 事务提交、不得成为跨模块共享读写表；(b) Message Consumer Deduplication Record 由消费模块拥有（Message ID/Dispatch ID + Consumer Scope 组合唯一），**Dedup Marker 必须与消费产生的业务更新同事务提交，不得先提交 Dedup Marker 再执行业务写入**；(c) Workflow Retry Idempotency：Runtime 负责 Attempt 与运行位置、Business Module 防止重复 Business Commit、Resume 经 Command Identity + 数据库幂等记录 + Lease 与 Fencing 校验、Checkpoint 不替代业务幂等记录；(d) External Provider Idempotency：Provider Adapter 使用稳定 Provider Call Identity，Retry 复用相同 Provider Idempotency Key（绑定 Input Fingerprint），Intentional Rerun 用新 Provider Call Identity，**数据库事务 Retry 不得生成新 Provider Key、不得自动重新调用已完成的 Provider 调用**；Provider 无原生 Idempotency 时 Provider/Integration 模块维护 Durable Call Ledger（Provider Call Identity / Input Fingerprint / execution status / Attempt relationship / result reference / reconciliation state），对账与补偿留相应 Provider RFC / Adapter 设计。**物理模型留白**：表名/字段/索引/分区/Storage Placement 留实现设计与 DQ-13；Retention/TTL/删除/Key 再利用留 DQ-15（DQ-15 前不得假设 Key 短期删除、自动复用归档 Key、依赖内存 Cache 作权威幂等存储）；敏感载荷不无必要复制；Hashing/Encryption/Redaction/Secret/PII 留 DQ-17；Outbox/Dispatch → DQ-09、Event/Audit → DQ-10、Workflow Runtime/Checkpoint 协调 → RFC-003、HTTP 幂等 Header/状态码/响应协议 → RFC-004、Retention 数值 → DQ-15、测试分类/CI → DQ-16。**Idempotency Identity Matrix 为幂等实现开始前的必备产出（18 字段：Operation / Owning Module / Logical Command ID / Idempotency Scope / Idempotency Key Source / Retry Identity / Rerun Identity / Attempt ID / Stage Run ID / Input Fingerprint Fields / Fingerprint Schema Version / State Machine / Unique Constraint / Atomic Transaction Boundary / Result Replay / Provider Idempotency / Retention Owner / Related DQ/DEC/RFC），但其创建不由 DQ-08 接受授权（NOT AUTHORIZED）**；本决定不要求新增独立 Technical Spike（DQ-07 已要求的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效并应覆盖幂等并发场景）；所有正式幂等语义验证使用真实 PostgreSQL，12 项最低覆盖清单见 DQ-08 第 88 点，详细测试组织归 DQ-16。历史 Recommendation「统一幂等表为主 + 设值语义为辅（[架构推断]）」已被重大修订取代（Superseded by Accepted Major Revision：统一万能表拒绝、分层模块私有存储接受为主要方向、天然幂等语义接受为强制设计原则、新增统一语义契约 + 身份模型 + Versioned Input Fingerprint + Lease 协同执行所有权 + DEC-035 原子提交 + Provider Call Ledger 要求）。
7. **Durable Work Intent 落库**（DQ-09）：首版以 DB Job Table 形态（逻辑等价最简 Outbox）与业务写入同事务；relay/backend 移交 RFC-003。
8. **审计 append-only 同事务原子写 + Application Event 提交后通知**（DQ-10）；**不采用完整 Event Sourcing**（DQ-11，与 DEC-013 一致）。
9. **Source/Evidence**：DB 存中小原始内容与全部证据元数据/链接，特大/二进制走外部对象存储 + 引用（DQ-12）。
10. **Checkpoint 同实例独立 schema、应用层清理、对账以 Business Current Truth 为权威**（DQ-13）。
11. **Alembic forward-only + autogenerate 必经人工 review + expand-contract 滚动兼容**（DQ-14）。
12. **数据保留分类定责**，业务真值/审计不删、checkpoint/运行记录可回收、原始来源留合规决定（DQ-15，不虚构周期）。
13. **测试分层**：单元/契约用快速 fake，并发/事务/迁移/幂等用语义等价真实 DB（DQ-16，填 R-1）。
14. **Secret 不落持久化真值/checkpoint/审计**，业务敏感列分类 + least privilege，checkpoint 反序列化白名单（DQ-17）。

### 9.2 推荐架构（Proposed Architecture — 非 Accepted）

> 本节为**推荐架构提案**，供用户审查；**不是**已接受决定、**不是**实施授权。所有组件名均为契约性占位，非生产代码承诺。

#### 9.2.1 端到端 Command 流程（Proposed）

```text
Entrypoint (API/CLI)
   │  仅协议转换，不触 Repository / Domain
   ▼
Application Use Case                        ◄── 拥有业务事务
   │  Prepare：装载 Current Truth（只读短事务）
   │  Execute：经 ModelRuntimePort/RetrievalPort 调用 Skill（无 DB 事务持有）
   │  Commit：BusinessCommitService 单事务原子提交
   ▼
BusinessCommitService（统一事务模板，DEC-035 六要素）
   │  Create Domain Version + Formal Evidence Links
   │  + Update Current Truth Pointer + Update Stage State
   │  + Write Audit + Write Idempotency Record   ──► 同一事务，任一失败整体回滚
   ▼
Durable Work Intent（与业务写入同事务落库）   ◄── API 返回 accepted 前必须可靠记录
   ▼
WorkflowDispatchPort ──（relay/backend 移交 RFC-003）──► Workflow Worker
```

**Unit of Work 边界（DQ-06 Accepted Decision，2026-08-02）：** 每个 Transactional Application Command 创建一个新的**一次性 UnitOfWork**（NEW → ACTIVE → COMMITTED / ROLLED_BACK → CLOSED）——一个 UoW 对应一个 SQLAlchemy Session、一个短数据库事务、一个显式业务状态迁移、一个最终 commit 或 rollback 结果；Use Case 显式调用 `commit()`，正常 Context 退出不得自动提交；未成功 commit 退出或异常退出 = rollback → close → discard。**Execute Outside Transaction 阶段不持有任何 UnitOfWork**；Prepare 与 Commit 作为不同 Transactional Command 时使用不同 UoW 实例。

**并发控制边界（DQ-07 Accepted Decision，2026-08-02）：** 分层并发控制覆盖上图全流程——Commit 阶段的 BusinessCommitService 使用 DQ-04 `expected_revision` compare-and-swap（零影响行 = 冲突整体回滚），并以命名数据库唯一约束作为重复业务事实的最终防线；**涉及 Worker 执行所有权的流程须先经短事务获取 Durable Lease（获取成功即提交、随即释放行锁/Session/UoW/连接），再于事务外执行 LLM/外部调用，Worker Commit 的最终短事务同时验证 expected_revision + 当前 Lease Holder + 当前 fencing_token + Attempt/Run identity**；队列式领取（如 Durable Work Intent 的 Worker Claim）仅可用 SELECT FOR UPDATE SKIP LOCKED 短事务（select → lock → assign holder/Lease/fencing token → commit → release → execute outside）。**进程内锁仅减少重复工作、不提供业务正确性；40001/40P01 由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试，语义冲突不盲目重试；外部 Provider 调用不进入事务重试循环。**

**幂等边界（DQ-08 Accepted Decision，2026-08-02）：** 上图 Commit 阶段的 `Write Idempotency Record` 遵循分层幂等模型——Business Command Idempotency Record 由执行业务状态修改的模块拥有，其成功状态与 DEC-035 六要素在**同一个 Atomic Business Commit** 中提交（业务回滚不得留下 SUCCEEDED 记录）；Commit 成功但响应丢失时，相同 Idempotency Scope + Key + Input Fingerprint 的后续请求重放原 Application Result（不重复执行业务副作用），不同 Fingerprint 返回 Idempotency Key Conflict。Retry 复用同一 Command ID / Idempotency Key / Stage Run ID / Input Fingerprint 并创建新 Attempt ID；Intentional Rerun 创建新逻辑身份并保留 `rerun_of` 关系。**IN_PROGRESS 执行所有权由 DQ-07 Durable Lease Holder + fencing_token + Attempt ID 保护**（旧 Worker 不得把记录转换为 SUCCEEDED）；Checkpoint/thread_id 不是业务幂等记录。消费端 Dedup Marker 与消费产生的业务更新同事务提交；数据库事务重试不得重新调用已完成的外部 Provider 调用（复用同一 Provider Call Identity）。幂等物理表/状态机/唯一约束均未创建——Idempotency Identity Matrix 为实现前置条件（REQUIRED / NOT AUTHORIZED）。

#### 9.2.2 外部 LLM 调用流程（Proposed）

```text
Use Case.Execute
   │  不持有 DB 事务
   ▼
Skill（无状态，经 ModelRuntimePort）
   │  调用 LLM / Retrieval（外部 I/O，耗时长）
   ▼
Candidate Result（业务候选，未落库）
   ▼
Use Case.Commit → BusinessCommitService（新短事务原子提交）
```

依据：SQLAlchemy 官方——事务存续期连接被独占 checkout、池上限有限（默认 5+10）、超时即报错 ⇒ **外部调用应在事务边界之外**（原为[架构推断]；**已由 DQ-05 Accepted Decision（2026-08-02）正式决定为 PROHIBITED：外部调用不得持有开放数据库事务**；官方仍未以明令形式写明，本条为项目用户决定）。

---

## 10. Recommended Architecture（推荐架构总表）

| 维度 | Recommendation（PROPOSED）/ Accepted Decision | 关键依据 |
|---|---|---|
| 引擎与语义 | **PostgreSQL 是唯一受支持的权威数据库语义；本地开发与正式持久化测试均使用真实 PostgreSQL；SQLite 不受支持**（**DQ-01 ACCEPTED，2026-08-01**） | DQ-01 Accepted Decision：并发写/托管/约束 |
| 技术栈 | **PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**（**DQ-01 ACCEPTED**） | DQ-01 Accepted Decision |
| ORM | SQLAlchemy 2.x sync-first（受 DQ-01 Accepted Decision 约束） | DQ-01/06：契合 RFC-001-DQ-07 |
| 迁移 | Alembic forward-only + 人工 review autogenerate（Recommendation，PROPOSED） | DQ-14 |
| 模块边界与所有权 | **单一 PG 服务 + 每表唯一所有模块；ORM/Repository/Migration/状态修改 Use Case 模块私有；跨模块仅经 Public Application Contract；Direct SQL/ORM/Repository 禁止；架构测试强制；每模块独立 schema 暂缓、物理命名留待实现设计**（**DQ-02 ACCEPTED，2026-08-01**） | DQ-02 Accepted Decision：DEC-034 + RFC-001-DQ-08 |
| 聚合边界 | **业务不变量 + 唯一模块所有权；Atomic Business Commit（DEC-035 六要素）= 事务提交协议，非聚合成员资格判据；Task Mega Aggregate REJECTED；默认一 Use Case 一主 Aggregate；跨聚合/跨模块显式协调（Explicit Composite Use Case）；UoW 形态移交 DQ-05/06；Aggregate/Invariant Matrix 实施前必备**（**DQ-03 ACCEPTED，2026-08-02**） | DQ-03 Accepted Decision：DEC-035 + RFC-001-DQ-08 |
| 版本化 | **`domain_version_id`（不可变、Application 层 INSERT 前生成、opaque UUID、不复用）/ `version_number`（逻辑对象内单调递增、`(logical_object_id, version_number)` 唯一性约束、删除/失效后不复用）/ `revision`（独立 NOT NULL 乐观并发 token）三类分离；`expected_revision` compare-and-swap 条件更新 + affected-row 校验，零行 = 冲突整体回滚；`version_id_col` 仅 Infrastructure 机制；`xmin` 非权威 revision；SERIALIZABLE 不替代 revision；隔离/重试留 DQ-05/07**（**DQ-04 ACCEPTED，2026-08-02**） | DQ-04 Accepted Decision |
| 事务边界 | **Business Transaction Owner = Application；一短显式事务 + 一最终提交点；长流程 = 多短事务 + 无事务执行阶段；Prepare → Execute Outside Transaction → Commit；外部调用 / Human Review / Workflow 暂停不入或不跨开放事务、Session 不跨 Workflow 边界（四项 PROHIBITED）；Commit-time Revision Revalidation 必选；External Result Before Commit 非 Current Truth；默认隔离 READ COMMITTED；SAVEPOINT 仅基础设施机制；嵌套业务事务禁止；与外部供应商的分布式事务拒绝；强隔离/锁/重试留 DQ-07**（**DQ-05 ACCEPTED，2026-08-02**） | DQ-05 Accepted Decision |
| UoW | **UnitOfWork Port 由 Application 定义、Infrastructure 提供 SQLAlchemy 实现（Session 为不暴露的 Infrastructure 细节）；一个 Transactional Command 创建一个一次性 UoW（NEW→ACTIVE→COMMITTED/ROLLED_BACK→CLOSED，commit/rollback/close 后不可重用）= 一个 Session + 一个短事务 + 一个最终结果；Use Case 显式 commit、Context 退出不得自动提交；未 commit / 异常退出 = rollback/close/discard；非法生命周期操作显式失败；UoW 仅暴露类型化 Repository Ports，禁止 Registry/Service Locator/raw Session/动态 lookup；Repository 无 begin/commit/rollback/close/SAVEPOINT 权限且不暴露 Session；嵌套业务 UoW 禁止且检测必须立即失败；Composite Application Use Case 唯一外层 UoW + 唯一最终提交点；SAVEPOINT 不由 Port 暴露（有限 Infrastructure 使用受 DQ-05 治理）；Port 默认不暴露 flush()、内部 flush 非业务 commit、flush 失败丢弃 UoW；Engine/sessionmaker 长生命周期 vs concrete Session 短生命周期；全局/ambient Session 禁止；并发 Command/Worker/Retry/Rerun/Resume 独立 UoW 与 Session；UoW 不入 Checkpoint、不跨 Workflow 边界；纯读 Query 独立短 Query Scope**（**DQ-06 ACCEPTED，2026-08-02**） | DQ-06 Accepted Decision |
| 并发 | **分层并发控制（Layered Concurrency Control）：① 乐观 revision 为普通业务写默认（DQ-04 协议；expected_revision 不匹配 = 语义冲突，不盲目重试）；② 命名数据库唯一约束为重复业务事实最终防线（唯一约束违反不统一重试，错误边界识别命名约束并分类；完整幂等键留 DQ-08）；③ Durable Lease + 单调 fencing_token 为执行所有权（短事务获取 + 提交后释放；Worker 不跨 LLM/外部调用/Human Review/Interrupt/backoff 持行锁；Worker Commit 验证 revision + Holder + fencing_token + Attempt/Run identity；旧 Worker 持旧 token 不得提交；进程内锁仅非权威优化）；④ SKIP LOCKED 仅限队列式 Claim 短事务；悲观锁非全局默认（采用须完整记录 + 确定性锁顺序）；Session-level Advisory Lock 禁止、Transaction-level 非默认；40001/40P01 由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试（backoff/jitter 在事务外、参数留 RFC-007）；语义冲突（stale revision/fencing/Lease/review/外部结果、业务不变量拒绝、未分类唯一违反、未定义策略 NOWAIT）不盲目重试；外部 Provider 不入重试循环（Commit 可用不可变外部结果重试但不重调 Provider）；五类场景组合映射；thread_id/Checkpoint 不得视为业务锁/Lease/fencing/幂等记录；Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Technical Spike 为实现前置条件（均 REQUIRED、均未授权）**（**DQ-07 ACCEPTED，2026-08-02**） | DQ-07 Accepted Decision |
| 幂等 | **分层幂等模型（Layered Idempotency Model）：Candidate B 为主（各幂等层由 Owning Module 分层存储、模块私有、同业务事务提交）+ Candidate C 为强制设计原则（set/ensure/replace-to-desired-state/compare-and-set，不替代显式记录/唯一约束/执行所有权）+ 统一语义契约（非统一物理表）；Candidate A 跨模块万能 Idempotency Table 拒绝；Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity 明确区分不得混用；Retry = same Command ID/Key/Stage Run ID/Input Fingerprint + new Attempt ID（不创建新 Domain Version），Intentional Rerun = 新逻辑身份 + rerun_of（成功后可产生新 Domain Version）；Versioned Input Fingerprint（规范化业务输入、版本化规则）；同 Scope+Key+Fingerprint 重放原 Application Result、不同 Fingerprint = Idempotency Key Conflict（不覆盖/不执行/不误重放/不盲目重试）；状态机 IN_PROGRESS/SUCCEEDED/FAILED_TERMINAL/非终局（Enum 名留实现设计）；IN_PROGRESS 与 DQ-07 Durable Lease/Holder/Attempt ID/fencing_token 协同（旧 Worker 不得写 SUCCEEDED）；Checkpoint/thread_id 非业务幂等记录；幂等成功记录 + DEC-035 六要素同一原子事务提交（回滚不留 SUCCEEDED）；响应丢失重放项目自有稳定结果快照（不保存/返回 ORM Entity/Session/Exception/Secret）；Consumer Dedup Marker 与消费业务更新同事务（不得先提交 Marker）；Provider Retry 复用同一 Provider Call Identity（DB 事务重试不重调 Provider、不生成新 Provider Key；无原生幂等则 Durable Call Ledger）；瞬时失败（连接超时/40001/40P01/Provider 暂不可用/Worker Crash/Lease 过期/网络故障）不永久固化为终局、可用同身份+新 Attempt 重试；确定性终局语义结果可稳定重放；表/字段/索引/分区留 DQ-13、Retention/Key 再利用留 DQ-15（前不得假设短期删除/复用归档 Key/内存 Cache 权威）、Hashing/Encryption/PII 留 DQ-17、Outbox 留 DQ-09、Event/Audit 留 DQ-10、Runtime/Checkpoint 协调留 RFC-003、HTTP 幂等协议留 RFC-004、测试分类留 DQ-16；Idempotency Identity Matrix（18 字段）为实现前置条件（REQUIRED / NOT AUTHORIZED）；不新增独立 Spike（DQ-07 Spike 覆盖幂等并发场景）；正式幂等测试用真实 PostgreSQL**（**DQ-08 ACCEPTED，2026-08-02**） | DQ-08 Accepted Decision |
| Dispatch | DB Job Table 形态 Durable Intent，同事务；backend 移交 RFC-003 | DQ-09 |
| 事件/审计 | 审计 append-only 同事务；事件提交后通知 | DQ-10：Fowler |
| 历史 | current truth + 版本化历史 + append-only 审计；不上 ES | DQ-11：DEC-013 |
| 来源/证据 | DB 存中小内容+证据元数据；特大走外部存储+引用 | DQ-12 |
| Checkpoint | 同实例独立 schema、应用层清理、对账业务真值权威 | DQ-13 |
| 保留 | 分类定责；真值/审计不删；checkpoint/运行可回收 | DQ-15 |
| 测试 | 单元 fake + 并发/事务/迁移/幂等**对真实 PostgreSQL 运行**（DQ-01 Accepted Decision 约束测试引擎；单元/契约层 fake 边界属 DQ-16，PROPOSED） | DQ-16：填 R-1 |
| 安全 | Secret 不落真值/checkpoint/审计；least privilege | DQ-17 |

---

## 11. Alternatives Considered（已考虑的替代方案）

| 决策点 | 替代方案 | 拒绝/保留理由 |
|---|---|---|
| 引擎 | SQLite 作生产引擎 | API+Worker 并发写撞全库单写者、网络文件锁不可靠、托管受限（**2026-08-01 用户正式拒绝：SQLite 不是受支持的 Business Current Truth backend**） |
| 引擎 | MVP SQLite → 后期迁 PG | 迁移脚本跨方言不可复用、类型/并发/序列需重做（真实成本，非零切换）（**2026-08-01 用户正式拒绝：SQLite-first strategy = REJECTED**） |
| 事务 | Use Case 全程一个事务 | 外部调用拉长事务→连接池耗尽风险（**2026-08-02 用户正式拒绝（Candidate B）：外部调用不得持有开放数据库事务；Transactional Application Command = 一个短显式事务 + 一个最终提交点**） |
| 事务 | SAVEPOINT 作业务部分提交 / 部分回滚机制（Candidate C 混合策略） | 先 flush、易误写中间态、嵌套「业务 commit」并不真持久化（**2026-08-02 用户正式拒绝为业务事务策略：SAVEPOINT 仅为有限 Infrastructure 机制；嵌套业务事务禁止**） |
| 事务 | 与外部供应商协调的分布式事务 / 两阶段提交 | 外部 provider 不可靠、协调与恢复语义复杂（**2026-08-02 用户正式拒绝：业务写入与外部效果的一致性经由 DQ-05 事务边界模式 + 幂等 / Durable Dispatch（DQ-08/09）实现**） |
| UoW | 隐式 UoW：装饰器 / context-manager 退出自动 commit（Candidate B） | 提交点隐式、正常退出被等同于业务成功、失败语义模糊（**2026-08-02 用户正式拒绝作为项目 UnitOfWork 模型：成功业务提交必须显式；Context Manager 仍允许用于生命周期清理，但不得自动提交业务状态**） |
| UoW | Repository 内部自管理事务（Candidate C） | 违反 Application 事务所有权与单一提交点、Repository 获得 begin/commit/rollback 权（**2026-08-02 用户正式拒绝：Repository 不得 begin/commit/rollback/close/begin_nested、不控制 SAVEPOINT 与 UoW 生命周期、不暴露 Session**） |
| 版本化 | PostgreSQL `xmin` / 服务端触发器作权威 Revision | 耦合后端、不可移植、非稳定跨系统契约（**2026-08-02 用户正式拒绝：`xmin` 不是 Domain Version、不是 Public Contract 字段、不是 Review Package revision、不是权威业务 revision**） |
| 并发 | 纯引擎隔离级（SERIALIZABLE 40001 重试）**替代显式 revision** | 高冲突重试风暴、对批量更新无效（**2026-08-02 用户正式拒绝作为 revision 替代：SERIALIZABLE 不是显式 Concurrency Revision 的替代方案；SERIALIZABLE 仍可能作为独立隔离策略由后续 DQ 讨论**） |
| 并发 | 单一通用锁机制覆盖全部并发问题；进程内 asyncio.Lock/threading.Lock 作业务正确性权威 | 无单一机制可同时覆盖语义冲突、重复事实、执行所有权与队列领取；进程内锁跨进程/跨副本/崩溃后失效（**2026-08-02 用户正式拒绝：采用分层并发控制；进程内锁仅为非权威优化，正确性须在多进程/多副本/崩溃/机器替换下保持**） |
| 并发 | Session-level PostgreSQL Advisory Lock 作默认/权威并发控制机制 | 会话级 advisory lock 生命周期与连接耦合、易泄漏、难审计、与短事务纪律冲突（**2026-08-02 用户正式禁止为默认或权威机制；Transaction-level Advisory Lock 非默认，仅自然行无法表达并发范围时经独立架构审查考虑**） |
| 并发 | SKIP LOCKED 用于普通业务查询 / 掩盖 expected_revision 冲突 / 跨外部调用持锁 | 静默跳过正在修改的对象破坏一致性语义、持锁跨外部调用耗尽连接（**2026-08-02 用户正式限制：SKIP LOCKED 仅限显式队列式 Claim 短事务**） |
| 并发 | 无限/无界重试；stale revision 或语义冲突自动重试；Repository/Session/UoW 静默自重试；事务重试内重新调用外部 Provider | 重试风暴、重复外部副作用、提交权威与重试所有权混乱（**2026-08-02 用户正式拒绝：40001/40P01 仅由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试；语义冲突不盲目重试；外部 Provider 不入重试循环**） |
| 幂等 | 分层各自存储（Candidate B） | 表分散但语义清晰（**2026-08-02 用户正式接受为主要持久化方向：各幂等层由相应 Owning Module 分层持久化，共享统一概念与行为契约，统一契约不意味着统一物理表**） |
| 幂等 | 跨模块万能 Idempotency Table（Candidate A，一处判重覆盖 Command/Workflow/Consumer/Dispatch/Provider 全部语义） | 表语义混杂、违反每表唯一模块所有权（DQ-02）、无法表达各层事务边界与执行所有权（**2026-08-02 用户正式拒绝为跨模块万能表：项目采用分层幂等模型**） |
| 幂等 | 仅依赖天然幂等语义（Candidate C 单独使用）替代显式幂等记录 | 设值语义无法覆盖创建 Domain Version / 外部副作用 / Review Decision / Dispatch / 计费配额 / append-only Audit / 只能发生一次的正式业务事实（**2026-08-02 用户正式接受为强制设计原则，但不得替代显式记录、唯一约束或执行所有权控制**） |
| 幂等 | Attempt ID 作幂等 Key / Retry 创建新 Command ID 或新 Stage Run / Rerun 复用旧 Command ID / 以是否异常区分 Retry 与 Rerun | Retry≠Rerun 身份语义破坏、判重与重放混乱（**2026-08-02 用户正式决定：七类身份明确区分不得混用；Retry 复用 Command ID/Key/Stage Run ID/Fingerprint + 新 Attempt ID；Rerun 新逻辑身份 + rerun_of；由明确 Application Intent 区分**） |
| 幂等 | Dedup Marker 先于业务写入提交 / SUCCEEDED 幂等记录可在业务事务外提交 / 相同 Key 不比较 Input Fingerprint / 不同 Fingerprint 重放旧结果 | 判重失效、部分成功被误重放、同键不同参数被误判（**2026-08-02 用户正式决定：Consumer Dedup 与业务更新同事务；幂等成功记录与 Business Current Truth 同一 DEC-035 原子提交；同 Scope+Key+Fingerprint 重放、不同 Fingerprint 返回冲突且不覆盖/不执行/不误重放/不盲目重试**） |
| 幂等 | 瞬时基础设施失败永久固化为终局结果 / 数据库事务重试自动重新调用外部 Provider / Retry 生成新 Provider Key | 合法重试被阻断、外部副作用重复、Provider 对账破坏（**2026-08-02 用户正式决定：连接超时/40001/40P01/临时 Provider 不可用/Worker Crash/Lease 过期/网络故障不固化为终局（同身份 + 新 Attempt 重试，受 DQ-07 约束）；确定性终局语义结果可稳定重放；Retry 复用同一 Provider Call Identity 与 Provider Key，DB 事务重试不重调已完成 Provider 调用**） |
| Dispatch | 独立 Message Broker | 引入额外基础设施，超 MVP 倾向 |
| 历史 | 完整 Event Sourcing | DEC-013 已排除；LLM 外部交互重放/bi-temporal 复杂度高 |
| 来源 | 全部外部对象存储 | DB 指针+外部对象一致性协调复杂 |
| Checkpoint | 完全独立物理库 | 隔离最强但运维重，超 MVP 需求 |
| 迁移 | 支持 downgrade | 含数据迁移的 downgrade 常无法无损 |

（每个 DQ 的完整候选与取舍见 `rfc-002-decision-questions.md`。）

---

## 12. Trade-offs（取舍）

- **PostgreSQL-only（DQ-01 Accepted Decision，2026-08-01）**带来生产正确性与语义一致（本地开发、CI 持久化测试、生产同引擎），但本地开发引入服务依赖，上手成本高于 SQLite 零配置（此代价已由用户接受）。
- **短事务 + 外部调用不入事务（DQ-05 Accepted Decision，2026-08-02）**减少连接占用、恢复清晰，但要求 Use Case 显式编排外部调用位置（Prepare → Execute Outside Transaction → Commit），比「全程一事务」复杂（此代价已由用户接受：Candidate B 全程一事务被拒绝）。
- **一次性 UoW + 显式 commit（DQ-06 Accepted Decision，2026-08-02）**使提交点显式、可审计并与「单一最终提交点」对齐，但要求 Use Case 显式调用 commit 并处理未提交/异常退出的 rollback/close/discard，比「Context 退出自动提交」更显式繁重（此代价已由用户接受：Candidate B 隐式自动提交被拒绝）。一次性生命周期限制了 Session 复用弹性，但避免 Session 状态跨事务/跨 Workflow 边界的歧义——SQLAlchemy 官方能力「Session 技术上可跨顺序事务使用」**不**被采纳为项目模式（项目决定采用更严格的一次性 UoW）。
- **分层并发控制（DQ-07 Accepted Decision，2026-08-02）**覆盖全面（乐观 revision + 命名唯一约束 + Durable Lease/fencing_token + 受限 SKIP LOCKED），但四层组合比单一机制难推理、Use Case 需显式编排 Lease 获取与 Worker Commit 多要素验证、重试须丢弃全部 ORM entities 重建 UoW/Session（此代价已由用户接受：单一通用锁与进程内权威锁被拒绝）。Durable Lease + fencing_token 引入持久化执行所有权开销，但换来跨进程/跨副本/崩溃下的执行正确性；有界重试（3 次总尝试）限制了瞬时故障下的自动恢复窗口，但杜绝重试风暴与重复外部副作用——具体 backoff/jitter/指标/阈值可在 RFC-007 配置，有界要求不得移除。**Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Technical Spike 是实现前置条件（均 REQUIRED 但未授权）**，实现前须另行授权。**版本底座已由 DQ-04 Accepted Decision（2026-08-02）正式决定**（三类版本语义分离 + `expected_revision` 条件更新 + 冲突整体回滚），**默认隔离级别已由 DQ-05 Accepted Decision（2026-08-02）决定为 READ COMMITTED**。
- **分层幂等模型（DQ-08 Accepted Decision，2026-08-02）**以模块私有分层存储 + 统一语义契约取代跨模块万能幂等表：每层幂等记录遵守 DQ-02 表所有权、与所属业务更新同事务提交，语义清晰且事务边界明确，但多个 Owning Module 各自维护幂等存储比「一张表」分散（此代价已由用户接受：Candidate A 万能表被拒绝）。七类身份（Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity）与 Versioned Input Fingerprint 使 Retry/Rerun/重放/冲突语义精确可验证，但要求 Application 层显式生成与传递身份、规范化业务输入（canonicalization），比隐式键设计更繁重（此代价已由用户接受：Retry≠Rerun 必须由明确 Application Intent 区分）。IN_PROGRESS 执行所有权叠加 DQ-07 Durable Lease/fencing_token 保证旧 Worker 无法完成幂等记录，但增加 Commit 路径的验证要素。**瞬时失败不永久固化、终局语义结果可重放**的区分需要错误边界精确分类，换来合法重试不被阻断与重复请求的确定性响应。**Idempotency Identity Matrix（18 字段）是实现前置条件（REQUIRED 但未授权）**，幂等实现前须另行授权；物理表/Retention/安全细节留 DQ-13/15/17。
- **DB Job Table 形态 dispatch**最简单且与业务写入同事务，但高吞吐下轮询负载与 relay 复杂度移交 RFC-003。
- **同实例 Checkpoint 独立 schema**运维最简，但隔离弱于独立物理库；对账权威必须在应用层强制「业务真值优先」。
- **不上完整 ES**避免 LLM 重放/bi-temporal 复杂度，代价是放弃「事件流重建任意历史状态」能力（DEC-013 已接受此代价）。

---

## 13. Risks（风险）

| 风险 | 影响 | 缓解（Recommendation） |
|---|---|---|
| 并发语义在 SQLite 与 PG 不可移植 | SQLite 测试通过 ≠ PG 一致 | **DQ-01 Accepted Decision：正式持久化测试对真实 PostgreSQL 运行**；DQ-16：并发/事务/迁移/幂等用真实目标引擎验证 |
| SQLite→PG 迁移成本被低估 | schema/并发/序列回归 | **已由 DQ-01 Accepted Decision（2026-08-01）消除：不采用 SQLite-first 路线，不存在跨方言切换迁移** |
| Checkpoint 被误作业务真值 | 一致性破坏 | DQ-13：逻辑/物理分离 + 对账业务真值权威 |
| 开发者提交业务后忘写 dispatch | Intent 丢失 | DQ-09：与业务写入同事务 |
| Secret 明文落 checkpoint | 凭证泄漏 | DQ-17：Secret 不入 Graph State/checkpoint + 反序列化白名单 |
| autogenerate 误判改名 | 错误迁移 | DQ-14：autogenerate 必经人工 review |
| 同一 thread_id 并发 resume（OSS 无防护） | 重复推进 | **DQ-07 Accepted Decision（2026-08-02）：执行所有权经 Durable Lease + 单调 fencing_token（Worker Commit 验证 Holder + fencing_token + expected_revision），不依赖 thread_id/Checkpoint 作业务锁**；运行时对账机制移交 RFC-003 |
| 过期 Worker 在 Lease 接管后仍提交 | 旧结果覆盖新状态、双写冲突 | **DQ-07 Accepted Decision（2026-08-02）：每次 Lease 获取/接管颁发单调递增 fencing_token；Worker Commit 在最终短事务内验证 Holder + fencing_token；持旧 token 的 Worker 即使仍运行且返回看似有效结果也不得提交** |
| 语义冲突被当作瞬时错误盲目重试 / 无界重试 | 重试风暴、重复外部副作用、静默覆盖 | **DQ-07 Accepted Decision（2026-08-02）：expected_revision 不匹配、stale fencing_token、过期 Lease、过期 review、业务不变量拒绝、过期外部结果、未分类 unique_violation 不盲目重试；40001/40P01 仅由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试；外部 Provider 不入重试循环** |
| SKIP LOCKED / Advisory Lock / 悲观锁误用为通用机制 | 静默跳过冲突对象、连接耗尽、死锁 | **DQ-07 Accepted Decision（2026-08-02）：SKIP LOCKED 仅限队列式 Claim 短事务；Session-level Advisory Lock 禁止为默认/权威机制；悲观锁非全局默认，采用须完整记录并使用确定性全局锁顺序** |
| ORM bulk UPDATE/DELETE 绕过 revision 检查 | 静默覆盖受保护记录 | **DQ-04 Accepted Decision（2026-08-02）禁止绕过 revision 的批量修改**；明确需要的批量操作必须定义 expected revision 规则、条件更新与 affected-row 校验 |
| 长事务 + 外部调用持有开放事务 | 高并发下连接池 checkout 耗尽、API/Worker 不可用 | **DQ-05 Accepted Decision（2026-08-02）：外部调用不得持有开放事务；长流程 = 多短事务 + 无事务执行阶段** |
| Human Review / Workflow 暂停跨越开放事务 | 连接长期占用、事务内状态与审核/等待耦合 | **DQ-05 Accepted Decision（2026-08-02）：Human Review 与 Workflow 暂停不得跨开放事务；暂停前状态必须已提交** |
| 跨 Workflow 边界持有 SQLAlchemy Session | detached/expire 状态、恢复语义混乱 | **DQ-05 Accepted Decision（2026-08-02）：Session 不得跨 Workflow 边界；Resume 以新 Session、新事务重新执行** |
| Session 泄漏给 Application / Graph Node / API / Checkpoint | ORM 细节耦合、UoW 边界崩溃、恢复与并发语义混乱 | **DQ-06 Accepted Decision（2026-08-02）：Session 是不暴露的 Infrastructure 实现细节；UoW Port 仅暴露显式类型化 Repository Ports；UoW 不序列化进 Checkpoint、不在 Resume 恢复** |
| 嵌套业务 UoW / 子 Use Case 独立提交 | 「以为已提交实际未提交」的部分提交假象、提交权威分散 | **DQ-06 Accepted Decision（2026-08-02）：嵌套业务 UoW 禁止且检测企图必须立即失败；可复用行为提取为 Domain Service / transaction-neutral Application Service / 接收显式 Ports 的内部操作；Composite Application Use Case 唯一外层 UoW + 唯一最终提交点** |
| 全局 / ambient Session（scoped_session / thread-local / ContextVar） | 事务所有权与依赖注入机制不明、并发与恢复语义腐蚀 | **DQ-06 Accepted Decision（2026-08-02）：全局可变 Session 禁止；ambient 机制不得作为主要事务所有权或依赖注入机制；每个并发 Command / Worker 执行 / Retry / Rerun / Resume 使用独立 UoW 与独立 Session** |
| 幂等判重与业务更新不同事务 / Dedup Marker 先于业务写入提交 | 判重失效、崩溃窗口内重复执行业务副作用 | **DQ-08 Accepted Decision（2026-08-02）：Business Command Idempotency Record 与业务状态更新同一 PostgreSQL 事务提交；Consumer Dedup Marker 必须与消费产生的业务更新同事务提交，不得先提交 Dedup Marker 再执行实际业务写入** |
| 相同 Idempotency Key 不比较 Input Fingerprint / 不同 Fingerprint 重放旧结果 | 同键不同参数被误判重放、调用方拿到不匹配的结果 | **DQ-08 Accepted Decision（2026-08-02）：Versioned Input Fingerprint（规范化业务输入、版本化规则、只含决定业务效果的字段）；同 Scope+Key+相同 Fingerprint 重放原 Application Result，不同 Fingerprint 返回 Idempotency Key Conflict（不覆盖原记录、不执行新业务操作、不把旧结果重放为新请求结果、不盲目自动重试）** |
| Retry / Rerun 身份混用（Attempt ID 当幂等 Key、Retry 建新 Command、Rerun 复用旧身份） | 重复请求被误当新操作、Rerun 被误重放旧结果、Domain Version 重复或丢失 | **DQ-08 Accepted Decision（2026-08-02）：七类身份明确区分不得混用；Retry 复用 Command ID/Idempotency Key/Stage Run ID/Input Fingerprint + 新 Attempt ID（不创建新 Domain Version）；Intentional Rerun 创建新逻辑身份并保留 rerun_of（成功后可产生新 Domain Version）；由明确 Application Intent 区分，不得以是否发生异常隐式判断** |
| 瞬时基础设施失败被永久固化为终局结果 / 数据库事务重试自动重新调用外部 Provider | 合法重试被阻断、外部副作用与计费重复、Provider 对账破坏 | **DQ-08 Accepted Decision（2026-08-02）：连接超时 / 40001 / 40P01 / 临时 Provider 不可用 / Worker Crash / Lease 过期 / 可恢复网络故障不固化为终局结果（同逻辑幂等身份 + 新 Attempt ID 重试，受 DQ-07 有界重试与 Lease/Fencing 约束）；确定性终局语义结果可记录并稳定重放；Provider Retry 复用同一 Provider Call Identity（绑定 Input Fingerprint），DB 事务重试不生成新 Provider Key、不自动重调已完成 Provider 调用；无原生幂等的 Provider 维护 Durable Call Ledger** |
| 过期 Worker 把 IN_PROGRESS 幂等记录写成 SUCCEEDED / Checkpoint-thread_id 被当作业务幂等记录 | 旧结果覆盖、重复业务提交、恢复语义混乱 | **DQ-08 Accepted Decision（2026-08-02）：IN_PROGRESS 执行所有权与 DQ-07 Durable Lease / Lease Holder / Attempt ID / fencing_token 协同，只有当前有效 Holder 和 fencing_token 可转换为最终成功状态，Lease 过期/被接管/fencing_token 失效后旧 Worker 不得写入 SUCCEEDED；Checkpoint 与 LangGraph thread_id 不作为 Business Idempotency Record** |

---

## 14. Migration & Compatibility（迁移与兼容）

- 本 RFC **不创建真实迁移**；仅定 schema 演进纪律（DQ-14）。
- DQ-01 已于 2026-08-01 由用户正式决定（ACCEPTED）：PostgreSQL 是唯一受支持的权威数据库语义，本地开发也使用 PostgreSQL，SQLite-first → PostgreSQL-later 路线被拒绝——**不再存在「SQLite → PG 切换」场景**，迁移直接面向 PostgreSQL 方言基线构建。迁移所有权与演进纪律归属 **RFC-002-DQ-14（Schema Evolution and Migrations）**（早期文档中的错误引用「RFC-014」已修正为 DQ-14）。
- 滚动升级兼容采用 **expand-contract**：先加（`ADD COLUMN`/`CREATE INDEX CONCURRENTLY`/`NOT VALID`）→ 应用双写/回填 → 后删（`DROP`/`VALIDATE`）；改列类型会重写并强锁，不兼容滚动。
- PG `CREATE INDEX CONCURRENTLY` 等在线低锁操作**不能**在事务内，迁移中需单独处理。

---

## 15. Open Questions（开放问题）

> 以下**不阻塞**本 RFC 的 DQ 决定，但需在实施前或后续 RFC 中明确：

1. MVP 部署形态（本地单容器 vs 托管）——原为影响 DQ-01 引擎最终拍板的输入；**DQ-01 已于 2026-08-01 由用户正式决定（PostgreSQL 唯一受支持的权威数据库语义），本问题不再阻塞引擎选型**，仅保留为部署形态决策的输入。
2. 原始来源数据的合规保留周期——DQ-15 显式留用户/合规决定，不虚构数值。
3. 高吞吐下 DB Job Table 轮询负载是否可接受——DQ-09 与 RFC-003 backend 协同。
4. 是否引入 LangGraph Store 承载「跨任务用户偏好类记忆」（非 Current Truth）——留 RFC-003。
5. 同一 thread_id 并发 resume 的应用层防护具体机制——**执行所有权机制已由 DQ-07 Accepted Decision（2026-08-02）决定为 Durable Lease + 单调 fencing_token（thread_id/Checkpoint 不得视为业务锁/Lease/幂等记录）；与 Checkpoint 运行时的对账机制仍留 RFC-003**。

---

## 16. Cross-RFC Boundary（跨 RFC 边界）

完整边界矩阵见 [rfc-002-analysis-cross-rfc-boundary.md](rfc-002-analysis-cross-rfc-boundary.md)。要点：

- **RFC-002 OWNS**：DQ-01~17（持久化与事务架构）。
- **INTERFACE for later RFC**：持久化契约/落库形态（版本指针、幂等键、Evidence Link、Durable Intent、审计、Checkpoint 边界）——后续 RFC 消费但不可改其语义。
- **DEFERRED**：LangGraph 生产 Checkpointer 实现/durability/serde/并发防护、dispatch backend/relay → **RFC-003**；API endpoint/HTTP/审核提交协议 → **RFC-004**；检索 chunking/向量/embedding → **RFC-005**；LLM provider/prompt/结构化输出 → **RFC-006**；logging/metrics/tracing/retry 参数 → **RFC-007**。
- **OUT OF SCOPE**：完整 Event Sourcing（DEC-013 已排除）、生产部署拓扑、Secret 管理实现、真实 Alembic 迁移脚本。

---

## 17. Dependencies（依赖）

- **上游（已 ACCEPTED）**：RFC-001（Modular Monolith、Application 拥有事务、Port 所有权、Durable Dispatch Boundary、Sync-first）；DEC-012/013/022/023/024/025/029/032/033/034/035。
- **下游（本 RFC 提供契约）**：RFC-003/004/005/006/007。
- **证据**：Spike-001（运行时安全验证 + R-1/R-3/R-4 缺口）。

---

## 18. Impact on Later RFCs（对后续 RFC 的影响）

| 后续 RFC | 本 RFC 提供的契约 | 本 RFC 移交的决定 |
|---|---|---|
| RFC-003 LangGraph Runtime/Checkpoint | Checkpoint 与业务库边界、对账权威、Resume 幂等键、Durable Intent 落库 | 生产 Checkpointer 实现、durability、serde、并发防护、dispatch backend/relay |
| RFC-004 API/Human Review | Review 持久化实体、并发控制、submit 幂等键 | API endpoint、HTTP schema、提交协议、权限 |
| RFC-005 Source/Retrieval | Source/Fragment/EvidenceLink 落库形态、索引落点边界 | 检索实现、chunking、向量库、embedding |
| RFC-006 LLM Runtime | LLM 执行记录落库、Secret 不落 checkpoint/Graph State | LLM provider、prompt、结构化输出、Secret 注入 |
| RFC-007 Observability | 审计/事件/运行记录落库形态 | logging/metrics/tracing 栈、retry/timeout 参数 |

---

## 19. Out of Scope（明确范围外）

LangGraph 节点结构 · API endpoints · HTTP schema · 检索 chunking · 向量数据库 · embedding 模型 · LLM provider · prompt 运行时 · logging vendor · metrics backend · deployment topology · 完整 Event Sourcing · 生产 Secret 管理实现 · 真实 Alembic 迁移脚本 · 任何生产代码。

---

## 20. Security & Privacy（安全与隐私）

- **Secret 边界（DQ-17）**：Secret 只注入需要的 Infrastructure Adapter，不进入 Domain/Application/Graph State/Checkpoint/Audit/Trace。LangGraph 官方证实 **Secret 会被明文序列化进 checkpoint**（`SecretStr.get_secret_value`），且默认宽松反序列化有 RCE 风险——生产须 `LANGGRAPH_STRICT_MSGPACK=true`（与 DEC-035 一致；serde 配置属 RFC-003）。
- **敏感数据**：业务敏感列分类 + least privilege + credentials ownership；test fixture 不得含真实凭证。
- **本 RFC 不实现** Secret 管理/密钥管理/字段级加密。

---

## 21. Observability（可观测性）

持久化层为 RFC-007 提供**可观测的落库载体**（审计记录、状态转换记录、运行记录、概念事件清单），但 logging/metrics/tracing 栈、retry/timeout/backoff/circuit-breaker 生产参数全部移交 **RFC-007**。本 RFC 不吸收观测范围。

---

## 22. Test Strategy（测试策略）

见 DQ-16。原则：**并发/事务/迁移/幂等使用真实 PostgreSQL**——**DQ-01 Accepted Decision（2026-08-01）：repository contract tests、persistence integration tests、transaction tests、concurrency tests 与 migration tests 必须对真实 PostgreSQL 运行；SQLite 不是受支持的 Business Current Truth backend，也不是 PostgreSQL 持久化语义的权威替代**。**DQ-04 Accepted Decision（2026-08-02）：持久化语义验证必须使用真实 PostgreSQL，并至少覆盖——两个写者使用相同 `expected_revision`、过期 Human Review 提交、重复 resume 尝试、Domain Version 与 Pointer 的原子更新、防止无保护的批量更新、冲突回滚且零部分业务写入**。单元/契约层是否可用快速 fake 属 DQ-16（PROPOSED，PENDING）。因并发语义不可移植（SQLite 全库单写者 vs PG 行级 MVCC）。覆盖：Atomic Commit 回滚（partial_write==0）、重复 submit/resume 幂等、过期 checkpoint 拒绝、取消无部分写入、并发编辑不静默覆盖、迁移前向兼容。**DQ-05 Accepted Decision（2026-08-02）确立的事务边界语义（外部调用 / Human Review / 暂停不跨开放事务、Session 不跨 Workflow 边界、commit 前方非 Current Truth）亦以真实 PostgreSQL 为验证基准；具体测试分类归 DQ-16**。**DQ-06 Accepted Decision（2026-08-02）确立的 UoW 语义（显式 commit 成功、未 commit 退出回滚、异常退出回滚、flush 失败回滚并丢弃 Session、Repository 无法独立 commit/rollback、嵌套 UoW 被拒绝、Composite 唯一外层 UoW、commit 后不可重用、并发 Commands 独立 Sessions、Prepare/Commit 不同 UoW、Execute Outside Transaction 无 Session/连接、只读 Query Scope 干净关闭、UoW 不跨 Human Review/Interrupt/Retry/Resume）同样以真实 PostgreSQL 为验证基准（覆盖清单见 DQ-06 第 50 点；详细测试组织与 CI 执行归 DQ-16，PROPOSED / PENDING）**。**DQ-07 Accepted Decision（2026-08-02）确立的并发语义同样以真实 PostgreSQL 为验证基准，所有正式并发语义测试不得使用 SQLite 或内存替代品；真实 PostgreSQL 多 Worker Concurrency Technical Spike 为并发控制实现授权前的必备验证，至少覆盖——两个并发 Resume 产生一个权威 Lease、Lease 过期与接管产生更高 fencing_token、持 stale fencing_token 的旧 Worker 无法提交、相同 expected_revision 的两个审批仅一个提交、SKIP LOCKED 不双重领取、40001/40P01 重试创建全新 UoW 与 Session、事务重试不重复外部 Provider 调用、并发版本分配无重复 Domain Version、冲突回滚零部分 Current Truth 写入（完整清单见 DQ-07 第 59 点）；Concurrency Scenario Matrix（13 字段，见 DQ-07 第 55 点）为持久化或并发控制实现开始前的必备产出——Matrix 创建与 Spike 执行均 REQUIRED 但本 RFC 不授权（详细测试分类与 CI 执行归 DQ-16，PROPOSED / PENDING）**。**DQ-08 Accepted Decision（2026-08-02）确立的幂等语义同样以真实 PostgreSQL 为验证基准，所有正式幂等语义验证不得使用 SQLite 或内存替代品；后续测试至少覆盖——同 Key + 同 Fingerprint 并发请求只有一次业务效果、同 Key + 不同 Fingerprint 返回冲突、Commit 成功但响应丢失后重放原结果、Retry 不创建新 Domain Version、Intentional Rerun 创建新逻辑身份、Review Decision 只提交一次、Consumer Dedup 与业务更新同事务、Worker Crash 后 IN_PROGRESS 接管、stale fencing_token 无法完成记录、Provider 成功但数据库 Commit 失败后不重复调用、瞬时失败创建新 Attempt、终局结果稳定重放（完整清单见 DQ-08 第 88 点）；Idempotency Identity Matrix（18 字段，见 DQ-08 第 82 点）为幂等实现开始前的必备产出——Matrix 创建 REQUIRED 但本决定不授权；DQ-07 已要求的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效并应覆盖幂等并发场景（本决定不新增独立 Spike；详细测试组织与 CI 策略归 DQ-16，PROPOSED / PENDING）**。填补 Spike R-1（并发）与 R-4（规模）。

---

## 23. Rollout Plan（推进计划）

1. **本 RFC 审查（当前 Gate）**：用户逐项审查并决定 DQ-01~17——**DQ-01/02/03/04/05/06/07/08 已由用户正式决定（DQ-01/02 于 2026-08-01、DQ-03/04/05/06/07/08 于 2026-08-02，均 ACCEPTED；DQ-01~07 Accepted with Revision，DQ-08 Accepted with Major Revision）；DQ-09~17 仍 PENDING（9 项）**。
2. **DQ 接受后**：用户明确接受 RFC-002 整体（Acceptance ≠ Authorization）。
3. **后续**：RFC-002 ACCEPTED 后，按其契约推进 RFC-003（Checkpointer/dispatch 实现），并仍**不**自动授权任何持久化生产实现——实施需用户另行明确授权。

---

## 24. Acceptance Criteria（验收标准）

按 rfcs/README 的四项标准：

- **Decision Completeness**：17 个 DQ 全部提出且含完整 13 字段、候选、取舍、失败模式、对后续 RFC 影响——✅ 本 RFC + DQ 文档满足。
- **Architecture Compatibility**：全部 DQ 与 RFC-001（Application 拥有事务、Port 所有权、Durable Dispatch、Sync-first）及 DEC-024/029/033/034/035 一致、无推翻——✅。
- **Implementation Readiness**：每个 DQ 给出可落地的候选与 Recommendation，实施者可据接受的 DQ 开始——⏳ DQ-01/02/03/04/05/06/07/08 ACCEPTED（2026-08-01/02）；DQ-09~17 待用户接受。注：DQ 接受 ≠ 实施授权（Implementation = NOT AUTHORIZED 恒定；DQ-03 另要求 Aggregate/Invariant Matrix 在持久化实施前完成；DQ-04 的三类版本语义、`expected_revision` 协议与持久化语义验证清单、DQ-05 的事务边界与执行模式决定、DQ-06 的 Unit of Work 模型决定、DQ-07 的分层并发控制决定、DQ-08 的分层幂等模型决定同样不授权实施；**DQ-07 另要求 Concurrency Scenario Matrix 与真实 PostgreSQL 多 Worker Concurrency Technical Spike 在并发控制实现前完成，二者均 REQUIRED 但未授权；DQ-08 另要求 Idempotency Identity Matrix 在幂等实现前完成，REQUIRED 但未授权**）。
- **Traceability**：每条需求追溯到 DEC/RFC-001/官方证据——✅（研究矩阵 + 边界矩阵 + DQ 标注）。

**Acceptance Gate：** 仅用户可将 DQ/RFC 标记 ACCEPTED；Coding Agent 不得自行接受。

---

## 25. Implementation Handoff（实施交接）

**本 RFC 不含实施交接内容**——Implementation = NOT AUTHORIZED。接受后，实施须以「用户单独明确授权」为前提，遵循 DEC-036 的 Controlled Execution 与 DEC-038 的 One Issue → One Branch → One PR → Required Verification → User Merge Gate。

---

## 26. Authorization Boundary（授权边界）

```text
RFC-002 Repository Audit            = AUTHORIZED
RFC-002 Research                    = AUTHORIZED
RFC-002 Decision Question Discovery = AUTHORIZED
RFC-002 Issue Creation              = AUTHORIZED
RFC-002 Branch Creation             = AUTHORIZED
RFC-002 Drafting                    = AUTHORIZED
RFC-002 Pull Request Creation       = AUTHORIZED
RFC-002 PR Description / Comment    = AUTHORIZED
RFC-002 Documentation Fixes         = AUTHORIZED
RFC-002 CI Failure Fixes            = AUTHORIZED WITHIN DOCUMENTATION SCOPE

RFC-002 Decision Question Acceptance = USER DECISION REQUIRED
RFC-002 Acceptance                   = USER DECISION REQUIRED
RFC-002 Merge                        = USER DECISION REQUIRED

Persistence Implementation   = NOT AUTHORIZED
Database Implementation      = NOT AUTHORIZED
Business Implementation      = NOT AUTHORIZED
Production Runtime           = NOT AUTHORIZED
```

---

## 27. Decision Matrix（决策矩阵）

| 评估维度 | PG 优先 | SQLite 生产 | MVP-SQLite→PG |
|---|---|---|---|
| API+Worker 并发写 | ✅ 行级 MVCC | ❌ 全库单写者 | ⚠️ 前期受限 |
| 托管部署 | ✅ | ❌ 网络文件锁 | ⚠️ 后期迁移 |
| 迁移成本 | — | — | ❌ 脚本不可复用 |
| 上手速度 | ⚠️ 需服务 | ✅ 零配置 | ✅ |
| 生产正确性 | ✅ 高 | ⚠️ 中 | ⚠️ 中 |

> **2026-08-01 用户决定：采纳「PG 优先」列（Candidate A）并修订为 PostgreSQL-only——本地开发也使用 PostgreSQL，不建立 SQLite 方言兼容承诺；「SQLite 生产」与「MVP-SQLite→PG」两列被正式拒绝。** 矩阵保留为历史决策依据。

（其余 DQ 的决策矩阵见 `rfc-002-decision-questions.md` 各 Candidates/Trade-offs。）

---

## 28. Review Checklist（审查清单）

供用户逐项审查：

- [x] DQ-01 引擎选型方向——**2026-08-01 用户正式决定：Candidate A（PostgreSQL 唯一受支持的权威数据库语义；SQLAlchemy 2.x sync + Psycopg 3 sync + Alembic；本地与正式测试用真实 PostgreSQL），ACCEPTED WITH REVISION，见 §33 Decision Log**。
- [x] DQ-02 持久化所有权与模块边界——**2026-08-01 用户正式决定：Candidate A 修订版（单一 PG 服务 + 每表唯一所有模块 + 模块私有 ORM/Repository/Migration/状态修改 Use Case + 跨模块仅经 Public Application Contract + 架构测试强制；每模块独立 PostgreSQL schema 暂缓、物理命名留待实现设计；三类存储物理划分归 DQ-13），ACCEPTED WITH REVISION，见 §33 Decision Log**。
- [x] DQ-03 Aggregate 与持久化边界——**2026-08-02 用户正式决定：Candidate A 修订版（聚合边界 = 业务不变量 + 唯一模块所有权；Atomic Business Commit = 事务提交协议、非聚合成员资格判据；Task Mega Aggregate REJECTED；默认一 Use Case 一主 Aggregate；跨聚合/跨模块显式协调；UoW/事务实现移交 DQ-05/06；Aggregate/Invariant Matrix 持久化实施前必备），ACCEPTED WITH REVISION，见 §33 Decision Log**。
- [x] DQ-04 Domain State Versioning——**2026-08-02 用户正式决定：Candidate A 修订版（`domain_version_id` / `version_number` / `revision` 三类明确分离、不得共享字段；Domain Version ID 由 Application 层 INSERT 前生成（opaque UUID、不可变、不复用）；Version Number 逻辑对象内单调递增 + `(logical_object_id, version_number)` 唯一性约束、不复用；受保护可变记录（Current Truth Pointer / Aggregate Root / Stage State / Review Package 等）使用独立 NOT NULL `revision`；状态修改 Command 携带 `expected_revision`，compare-and-swap 条件更新、零影响行 = 冲突且整体回滚；SQLAlchemy `version_id_col` 仅为 Infrastructure 机制（`StaleDataError` 翻译为项目自有冲突语义，mapper/Session 细节不泄漏进 Domain/Public Contract，bulk UPDATE/DELETE 不得绕过 revision）；PostgreSQL `xmin` 不作权威业务 revision；SERIALIZABLE 不替代显式 revision；隔离级别/重试策略留 DQ-05/07；DEC-035 六要素保持同事务；RFC-004 可映射 ETag/If-Match（HTTP 协议不由 DQ-04 决定）；正式持久化测试使用真实 PostgreSQL，测试策略归 DQ-16），ACCEPTED WITH REVISION，见 §33 Decision Log**。
- [x] DQ-05 Transaction Boundary——**2026-08-02 用户正式决定：Candidate A 修订版（Business Transaction Owner = Application；Transactional Application Command = 一短显式事务 + 一最终提交点；长流程 = 多短事务 + 无事务执行阶段；执行模式 Prepare → Execute Outside Transaction → Commit；四项 PROHIBITED（外部调用持有开放事务、Human Review 跨开放事务、Workflow 暂停跨开放事务、SQLAlchemy Session 跨 Workflow 边界）；Commit-time Revision Revalidation 必选；DEC-035 六要素保持有效；External Result Before Commit 非 Current Truth；默认 PostgreSQL 隔离 = READ COMMITTED；更强隔离/锁/重试留 DQ-07；SAVEPOINT 仅有限 Infrastructure 机制；嵌套业务事务禁止；与外部供应商的分布式事务拒绝；UoW Port 形态留 DQ-06），ACCEPTED WITH REVISION，见 §33 Decision Log**。
- [x] DQ-06 Unit of Work Model——**2026-08-02 用户正式决定：Candidate A 修订版（UnitOfWork Port 由 Application 定义 + Infrastructure SQLAlchemy 实现（Session 为不暴露的 Infrastructure 细节）；每个 Transactional Command 创建一个一次性 UoW（NEW→ACTIVE→COMMITTED/ROLLED_BACK→CLOSED，commit/rollback/close 后不可重用），一个 UoW = 一个 Session + 一个短事务 + 一个最终结果；Application Use Case 显式调用 commit()、Context 退出不得自动提交；未 commit / 异常退出 = rollback/close/discard；非法生命周期操作显式失败；UoW 仅暴露类型化 Repository Ports，禁止 Registry/Service Locator/raw Session/动态 lookup；Repository 无 begin/commit/rollback/close/SAVEPOINT 权限且不暴露 Session；嵌套业务 UoW 禁止且检测必须立即失败；Composite Application Use Case 唯一外层 UoW + 唯一最终提交点；SAVEPOINT 不由 Port 暴露、Port 默认不暴露 flush()、内部 flush 非业务 commit 且失败丢弃 UoW；Engine/sessionmaker 长生命周期 vs concrete Session 短生命周期；全局/ambient Session 禁止；并发 Command/Worker/Retry/Rerun/Resume 独立 UoW 与 Session；UoW 不入 Checkpoint、不跨 Workflow 边界；纯读 Query 独立短 Query Scope；Candidate B 退出自动提交与 Candidate C Repository 管理事务拒绝；并发/幂等/Outbox/Event-Audit/HTTP/Runtime/测试分类留 DQ-07~10/RFC-004/RFC-003/DQ-16），ACCEPTED WITH REVISION，见 §33 Decision Log**。
- [x] DQ-07 并发控制分层组合是否覆盖五类并发场景？——**2026-08-02 用户正式决定：Accepted Direction = LAYERED CONCURRENCY CONTROL，修订版（分层并发控制取代单一通用锁：① 乐观 revision 为普通业务写默认（DQ-04 协议；expected_revision 不匹配 = 语义业务冲突，不盲目重试——并发审批返回冲突、过期 Human Review 拒绝、同时失效仅一个成功、后写者不得静默覆盖、过期外部结果不得重绑新 Domain Version）；② 命名数据库唯一约束为重复业务事实最终完整性防线（唯一约束违反不统一重试、错误边界识别命名约束并分类；完整幂等键层级留 DQ-08）；③ Durable Lease + 单调递增 fencing_token 为执行所有权（短事务获取 + 提交后释放行锁/Session/UoW/连接；Worker 不跨 LLM/外部调用/Human Review/Interrupt/backoff/长计算/跨进程执行持行锁；Worker Commit 验证 revision + Holder + fencing_token + Attempt/Run identity + 后续 DQ-08 幂等身份 + 业务不变量；旧 Worker 持旧 token 不得提交；进程内锁仅非权威优化，正确性须在重启/崩溃/多进程/多副本/机器替换/内存丢失下保持）；④ SKIP LOCKED 仅限显式队列式 Claim 短事务；悲观锁非全局默认（采用须完整记录 + 确定性全局锁顺序）；Session-level Advisory Lock 禁止、Transaction-level 非默认（独立架构审查）；40001/40P01 由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试（Repository/Session/UoW 不得静默自重试；backoff/jitter 在事务外、参数留 RFC-007、有界要求不得移除）；语义冲突不盲目重试（stale revision/fencing/Lease/review、业务不变量拒绝、过期外部结果、未分类 unique_violation、未定义策略 NOWAIT）；外部 Provider 不入重试循环（Commit 可用不可变外部结果重试但不重调 Provider）；五类场景控制组合映射；thread_id/Checkpoint 不得视为业务锁/Lease/fencing/幂等记录/单一活动 Resume 证明；Concurrency Scenario Matrix（13 字段）与真实 PostgreSQL 多 Worker Technical Spike（9 项验证）为实现前置条件——均 REQUIRED 但本决定不授权，Spike Issue/Branch/PR/代码/测试/基础设施创建需单独明确用户授权；完整幂等/Outbox/Event-Audit/Checkpoint 对账/API 冲突协议/测试分类/运维重试指标留 DQ-08~10/RFC-003/RFC-004/DQ-16/RFC-007），ACCEPTED WITH REVISION，见 §33 Decision Log**。
- [x] DQ-08 幂等模型分层与身份语义是否成立？——**2026-08-02 用户正式决定：ACCEPTED WITH MAJOR REVISION（Primary Direction = Candidate B：各幂等层由 Owning Module 分层存储、模块私有、同业务事务提交；Supporting Principle = Candidate C：天然幂等 set/ensure/replace/compare-and-set 语义为强制设计原则，不替代显式记录/唯一约束/执行所有权；Rejected Direction = Candidate A as Universal Table：跨模块万能 Idempotency Table 拒绝；统一概念与行为契约（10 要素）不意味着统一物理表；七类身份（Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity）明确区分不得混用；Retry = same Command ID/Key/Stage Run ID/Input Fingerprint + new Attempt ID（不创建新 Domain Version），Intentional Rerun = 新逻辑身份 + rerun_of（成功后可产生新 Domain Version），由明确 Application Intent 区分不得以异常隐式判断；Versioned Input Fingerprint（规范化业务输入 + 版本化规则 + 只含决定业务效果的字段）；同 Scope+Key+相同 Fingerprint 重放原 Application Result（不重复副作用），不同 Fingerprint = Idempotency Key Conflict（不覆盖/不执行/不误重放/不盲目重试）；状态机 IN_PROGRESS/SUCCEEDED/FAILED_TERMINAL/非终局（Enum 名留实现设计）；IN_PROGRESS 与 DQ-07 Durable Lease/Lease Holder/Attempt ID/fencing_token 协同（只有当前有效 Holder 和 fencing_token 可转换为最终成功状态；旧 Worker 不得写 SUCCEEDED；Checkpoint/thread_id 非业务幂等记录）；幂等成功记录 + DEC-035 六要素同一原子事务提交（回滚不留 SUCCEEDED；响应丢失重放项目自有稳定结果快照；不保存/返回 ORM Entity/Session/Exception/原始错误/未脱敏 Secret/传输层可变对象）；Consumer Dedup Marker 与消费业务更新同事务（不得先提交 Marker）；Workflow Resume 经 Command Identity + 数据库幂等记录 + Lease 与 Fencing 校验（Checkpoint 不替代业务幂等记录）；Provider Retry 复用同一 Provider Call Identity（绑定 Input Fingerprint；DB 事务重试不生成新 Provider Key、不自动重调已完成 Provider 调用；无原生幂等则 Durable Call Ledger 六字段）；瞬时失败（连接超时/40001/40P01/临时 Provider 不可用/Worker Crash/Lease 过期/网络故障）不永久固化为终局（同身份 + 新 Attempt 重试，受 DQ-07 约束）；确定性终局语义结果可稳定重放；副作用前纯输入验证失败可不创建可重放终局记录；表/字段/索引/分区留 DQ-13、Retention/TTL/Key 再利用留 DQ-15（前不得假设短期删除/复用归档 Key/内存 Cache 权威）、Hashing/Encryption/Redaction/PII 留 DQ-17、Outbox/Dispatch 留 DQ-09、Event/Audit 留 DQ-10、Runtime/Checkpoint 协调留 RFC-003、HTTP 幂等 Header/状态码/响应协议留 RFC-004、测试分类/CI 留 DQ-16；Idempotency Identity Matrix（18 字段）为幂等实现前置条件——REQUIRED 但 NOT AUTHORIZED；不新增独立 Technical Spike（DQ-07 Spike 覆盖幂等并发场景）；所有正式幂等语义验证使用真实 PostgreSQL（12 项最低覆盖清单见 DQ-08 第 88 点），见 §33 Decision Log**。
- [ ] DQ-09 是否首版引入 Durable Work Intent 落库（而非直接 broker）？
- [ ] DQ-11 「不上完整 ES」立场是否确认（与 DEC-013 一致）？
- [ ] DQ-13 Checkpoint 同实例独立 schema + 应用层清理是否可接受？
- [ ] DQ-15 各类数据保留责任划分是否留待合规决定（未虚构周期）？
- [ ] 全部 17 项 User Decision 是否逐项拍板（DQ-01~08 已决定；DQ-09~17 PENDING）？

---

## 29. Mandatory Stop Conditions（强制停止条件）

本 RFC 起草全程遵守以下停止条件；任一触发即停止并提交 Decision Conflict Report / Mandatory Stop Report，不静默决定：

Foundation 未完成 · RFC-001 未 ACCEPTED · 存在冲突 RFC-002 对象 · main 无法同步 · 工作树有无归属改动 · 发现真实 secret · 需改 Accepted DEC · 需改 RFC-001 · 不可调和的 Accepted 决定冲突 · 需生产代码 · 需 DB 配置 · 需 ORM/迁移 · 需 Repository/UoW 实现 · 需 Outbox 实现 · 需 LangGraph 实现 · 需 API/Worker · 需改 GitHub Actions · 需改 Branch Protection · 需改依赖 · 需处理 Dependabot PR · 需处理 PR #11/#12/#16/#20/#21 · 需自行接受 DQ · 需自行接受 RFC · 需自行 Merge · 需开始业务开发 · 实际范围超出 RFC 起草。

（本次起草未触发任何一条。）

---

## 30. Related Sessions / Documents（相关会话与文档）

- [rfc-002-research-persistence-requirements.md](rfc-002-research-persistence-requirements.md) — 需求矩阵（6 类 + 17 待决项映射）
- [rfc-002-analysis-cross-rfc-boundary.md](rfc-002-analysis-cross-rfc-boundary.md) — 跨 RFC 边界矩阵
- [rfc-002-decision-questions.md](rfc-002-decision-questions.md) — 完整 DQ 集（13 字段）
- [rfc-001-repository-and-application-architecture.md](rfc-001-repository-and-application-architecture.md) — 上游（ACCEPTED）
- `docs/architecture/data-architecture.md` · `docs/architecture/architecture-baseline-v1.md` · `docs/decisions/dec-012~035`

---

## 31. Related Decisions（相关决定）

DEC-012 · DEC-013 · DEC-022 · DEC-023 · DEC-024 · DEC-025 · DEC-029 · DEC-032 · DEC-033 · DEC-034 · DEC-035 · DEC-036 · DEC-038 · RFC-001（DQ-04/05/06/07/08）。

---

## 32. Traceability（可追溯性）

| 需求来源 | 落到 DQ | 证据 |
|---|---|---|
| DEC-024 三类存储/四状态/四标识符/六版本指针 | DQ-01/02/04/13 | 需求矩阵 §0/§1/§3 |
| DEC-029 审核持久化/并发/幂等 | DQ-04/07/08 | 需求矩阵 §4 |
| DEC-033 失败/重试/恢复/幂等/对账 | DQ-05/07/08/13 | 需求矩阵 §3/§6 |
| DEC-035 原子提交六要素 | DQ-03/05/06 | 需求矩阵 §7 |
| DEC-013 完整 ES 不属 MVP / 保留历史 | DQ-11/15 | 需求矩阵 §5 |
| DEC-025 Source/Evidence 独立语义 | DQ-12 | 需求矩阵 §2 |
| RFC-001-DQ-04/05/06 事务与端口所有权 | DQ-05/06 | RFC-001 |
| RFC-001-DQ-07 Durable Dispatch Boundary | DQ-09 | RFC-001 |
| RFC-001-DQ-08 事件区分 | DQ-10 | RFC-001 |
| Spike R-1 并发未验证 | DQ-07/16 | 需求矩阵 §6 |
| Spike R-3 生产 Checkpointer 未锁定 | DQ-13 | 需求矩阵 §3 |
| Spike R-4 规模未验证 | DQ-16 | 需求矩阵 §6 |
| SQLAlchemy 官方（UoW/乐观并发/事务/checkout） | DQ-04/05/06/07 | 边界矩阵 §0 |
| LangGraph 官方（生产 PostgresSaver/无同库建议/RCE/无并发防护） | DQ-13/17 | 边界矩阵 §0 |
| PG/SQLite/Alembic 官方（并发/迁移/TOAST） | DQ-01/12/14/16 | 边界矩阵 §0 |
| 模式权威（Outbox/Idempotent Consumer/Audit Log/ES） | DQ-08/09/10/11 | 边界矩阵 §0 |
| 用户决定（2026-08-01）DQ-01 Accepted：PostgreSQL + SQLAlchemy 2.x sync + Psycopg 3 sync + Alembic；PostgreSQL-only 语义；SQLite-first 拒绝；RFC-014→DQ-14 修正 | DQ-01 → 约束 DQ-14/16 与全部后续持久化落点 | §33 Decision Log · PR #24 |
| 用户决定（2026-08-01）DQ-02 Accepted：单一 PG 服务 + 每表唯一所有模块 + 模块私有 ORM/Repository/Migration + 跨模块 Public Contract + 架构测试强制；独立 schema 暂缓；存储物理划分归 DQ-13 | DQ-02 → INTERFACE → RFC-003/004/005 各模块表边界 | §33 Decision Log · PR #24 |
| 用户决定（2026-08-02）DQ-03 Accepted：聚合边界 = 业务不变量 + 唯一模块所有权；Atomic Business Commit = 事务协议非聚合成员资格；Task Mega Aggregate REJECTED；一 Use Case 一主聚合；跨聚合/跨模块显式协调；UoW 移交 DQ-05/06；Aggregate/Invariant Matrix 实施前必备 | DQ-03 → INTERFACE → RFC-004（Review 提交事务）/RFC-005（Evidence Link 一致性） | §33 Decision Log · PR #24 |
| 用户决定（2026-08-02）DQ-04 Accepted：`domain_version_id` / `version_number` / `revision` 三类分离；Domain Version ID 由 Application 层 INSERT 前生成；Version Number 单调递增 + 唯一性约束；受保护可变记录独立 NOT NULL `revision`；`expected_revision` compare-and-swap 条件更新 + 冲突整体回滚；`version_id_col` 仅 Infrastructure 机制；`xmin` 非权威 revision；SERIALIZABLE 不替代 revision；隔离/重试留 DQ-05/07；DEC-035 六要素同事务；持久化语义验证用真实 PostgreSQL（测试策略归 DQ-16） | DQ-04 → INTERFACE → RFC-004（可映射 ETag/If-Match，HTTP 协议未决）/DQ-05/07（隔离与重试）/DQ-16（测试分类） | §33 Decision Log · PR #24 |
| 用户决定（2026-08-02）DQ-05 Accepted：Business Transaction Owner = Application；一短显式事务 + 一最终提交点；长流程 = 多短事务 + 无事务执行阶段；Prepare → Execute Outside Transaction → Commit；四项 PROHIBITED（外部调用 / Human Review / Workflow 暂停 / Session 跨 Workflow 边界）；Commit-time Revision Revalidation 必选；DEC-035 保持有效；External Result Before Commit 非 Current Truth；默认 READ COMMITTED；SAVEPOINT 仅基础设施机制；嵌套业务事务禁止；与外部供应商的分布式事务拒绝 | DQ-05 → INTERFACE → RFC-003（节点边界 / Resume 新事务）/RFC-007（超时/重试参数；锁与重试策略归 DQ-07）；DQ-04 的「默认隔离级别」留白由此决定；UoW Port 形态归 DQ-06 | §33 Decision Log · PR #24 |
| 用户决定（2026-08-02）DQ-06 Accepted：UnitOfWork Port 由 Application 定义、Infrastructure SQLAlchemy 实现（Session 为不暴露的 Infrastructure 细节）；一次性 UoW（NEW→ACTIVE→COMMITTED/ROLLED_BACK→CLOSED）= 一个 Session + 一个短事务 + 一个最终结果；显式 commit、Context 退出不得自动提交、未 commit / 异常退出 = rollback/close/discard；Repository 无事务控制权与 Session 暴露、禁止 Registry/Service Locator；嵌套业务 UoW 禁止（检测立即失败）；Composite 唯一外层 UoW；SAVEPOINT/flush 边界；全局/ambient Session 禁止；并发执行独立 UoW/Session；UoW 不入 Checkpoint、不跨 Workflow 边界；纯读 Query Scope；Candidate B/C 拒绝 | DQ-06 → INTERFACE → 全部写路径；DQ-05 的「UoW Port 形态」留白由此决定；并发/锁/重试归 DQ-07、幂等归 DQ-08、Outbox 归 DQ-09、Event/Audit 归 DQ-10、HTTP 请求作用域归 RFC-004、Workflow/Checkpoint 运行时归 RFC-003、测试分类归 DQ-16 | §33 Decision Log · PR #24 |
| 用户决定（2026-08-02）DQ-07 Accepted：分层并发控制（Layered Concurrency Control）——乐观 revision 为普通业务写默认（DQ-04 协议；语义冲突不盲目重试）+ 命名数据库唯一约束为重复业务事实最终防线（分类识别、完整幂等键留 DQ-08）+ Durable Lease + 单调 fencing_token 为执行所有权（短事务获取后释放、Worker Commit 验证 revision/Holder/fencing_token/Attempt identity、旧 Worker 不得提交、进程内锁仅非权威优化）+ SKIP LOCKED 仅限队列式 Claim 短事务；悲观锁非全局默认（完整记录 + 确定性锁顺序）；Session-level Advisory Lock 禁止、Transaction-level 非默认；40001/40P01 由 Application Transaction Runner 以全新 UoW/Session 最多三次总尝试重试（Repository/Session/UoW 不静默自重试；backoff/jitter 事务外、参数留 RFC-007）；语义冲突与未分类唯一违反不盲目重试；外部 Provider 不入重试循环；五类场景控制组合映射；thread_id/Checkpoint 不得视为业务锁/Lease/fencing/幂等记录；Concurrency Scenario Matrix（13 字段）与真实 PostgreSQL 多 Worker Technical Spike（9 项验证）为实现前置条件（均 REQUIRED、均未授权） | DQ-07 → INTERFACE → 全部写路径与 Worker 执行；DQ-04/05 的「隔离/锁/重试」留白由此决定；完整幂等归 DQ-08、Outbox/Dispatch Claim 归 DQ-09、Event/Audit 顺序归 DQ-10、Checkpoint 并发与 Runtime 对账归 RFC-003、API 冲突协议（状态码/ETag/If-Match）归 RFC-004、完整测试分类归 DQ-16、运维重试指标与阈值归 RFC-007 | §33 Decision Log · PR #24 |
| 用户决定（2026-08-02）DQ-08 Accepted：分层幂等模型（Layered Idempotency Model）——Candidate B（分层各自存储）为主要持久化方向（各幂等层由 Owning Module 分层持久化、模块私有、同业务事务提交、不得成为跨模块共享读写表）+ Candidate C（天然幂等语义 set/ensure/replace/compare-and-set）为强制设计原则（不替代显式记录/唯一约束/执行所有权）+ 统一概念与行为契约（logical operation identity / owning module / idempotency scope / idempotency key / input fingerprint / execution status / retry-rerun semantics / unique constraint / result replay semantics / atomic transaction boundary，不意味着统一物理表）；Candidate A 作为跨模块、跨 Command/Workflow/Consumer/Dispatch/Provider 的万能 Idempotency Table 被拒绝（ACCEPTED WITH MAJOR REVISION）；七类身份（Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity）明确区分不得混用或由通用 ID 字段隐式取代；Retry = same Command ID / same Idempotency Key / same Stage Run ID / same Input Fingerprint / new Attempt ID / no new intended business operation（Retry 不创建新 Domain Version），Intentional Rerun = new Command ID / new logical Idempotency identity / new Stage Run ID / new Attempt ID / rerun_of 关系（成功后可产生新 Domain Version），由明确 Application Intent 区分、不以是否异常隐式判断；Idempotency Key 在明确 Scope 内唯一（Scope 至少 owning module / operation type / target business scope / tenant-account scope / idempotency key）；Versioned Input Fingerprint（canonicalization version / fingerprint schema version / hash algorithm / included business fields / excluded transport-observability fields；含 target identity / expected revision / base Domain Version / Command parameters / Source-Evidence references / operation mode；不含 trace ID / arrival timestamp / retry counter / Attempt ID / connection metadata）；同 Scope+Key+相同 Fingerprint = 重放原 Application Result（不重复副作用），不同 Fingerprint = Idempotency Key Conflict（不覆盖原记录 / 不执行新业务操作 / 不把旧结果重放为新请求结果 / 不盲目自动重试）；状态机至少 IN_PROGRESS / SUCCEEDED / FAILED_TERMINAL / 非终局状态（精确 Enum 名留实现设计）；IN_PROGRESS 执行所有权与 DQ-07 Durable Lease / Lease Holder / Attempt ID / fencing_token 协同（只有当前有效 Holder 和 fencing_token 可转换为最终成功状态；Lease 过期/被接管/fencing_token 失效后旧 Worker 不得写入 SUCCEEDED）；Checkpoint 与 LangGraph thread_id 不作为 Business Idempotency Record；业务成功时 Business Current Truth 更新 + Domain Version + Formal Evidence Links + Current Truth Pointer + Stage State + Audit Record + Idempotency Record 成功状态 + 不可变 Application Result Snapshot/结果引用同一 DEC-035 Atomic Business Commit 提交（回滚不留 SUCCEEDED）；响应丢失后同 Scope+Key+Fingerprint 重放项目自有稳定结果（不保存/返回 ORM Entity / Session / Exception / 原始数据库错误 / 未脱敏 Secret / 传输层可变对象）；HTTP Status/Headers/响应协议留 RFC-004；确定性终局业务结果可记录并稳定重放；瞬时基础设施失败（连接超时 / 40001 / 40P01 / 临时 Provider 不可用 / Worker Crash / Lease 过期 / 可恢复网络故障）不永久固化为终局结果（同逻辑幂等身份 + 新 Attempt ID 重试，受 DQ-07 有界重试/Lease/Fencing 约束）；副作用前纯输入验证失败可不创建可重放终局记录；Consumer Dedup Marker 与消费业务更新同事务（不得先提交 Marker 再业务写入）；Workflow Resume 经 Command Identity + 数据库幂等记录 + Lease 与 Fencing 校验（Checkpoint 不替代业务幂等记录）；Provider Adapter 使用稳定 Provider Call Identity（Retry 复用同一 Provider Idempotency Key 且绑定 Input Fingerprint；Intentional Rerun 用新 Provider Call Identity；DB 事务 Retry 不生成新 Provider Key、不自动重调已完成 Provider 调用；无原生幂等则 Provider/Integration 模块维护 Durable Call Ledger：Provider Call Identity / Input Fingerprint / execution status / Attempt relationship / result reference / reconciliation state；对账与补偿留相应 Provider RFC/Adapter）；表名/字段/索引/分区/Storage Placement 留实现设计与 DQ-13；Retention/TTL/删除/Key 再利用留 DQ-15（DQ-15 前不得假设 Key 短期删除 / 自动复用归档 Key / 依赖内存 Cache 作权威幂等存储）；敏感载荷不无必要复制；Hashing/Encryption/Redaction/Secret/PII 留 DQ-17；Outbox/Dispatch → DQ-09、Event/Audit → DQ-10、Workflow Runtime/Checkpoint 协调 → RFC-003、HTTP 幂等 Header/状态码/响应协议 → RFC-004、Retention 数值 → DQ-15、测试分类/CI → DQ-16；Idempotency Identity Matrix（18 字段）为幂等实现前置条件——REQUIRED 但 NOT AUTHORIZED；不新增独立 Technical Spike（DQ-07 真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效并应覆盖幂等并发场景）；所有正式幂等语义验证使用真实 PostgreSQL（12 项最低覆盖清单见 DQ-08 第 88 点），详细测试组织归 DQ-16；历史 Recommendation「统一幂等表为主 + 设值语义为辅」被重大修订取代（Superseded by Accepted Major Revision） | DQ-08 | DQ 文档 DQ-08 节 + 本 §33 |

---

## 33. Decision Log（决定记录）

| 日期 | 决定 | 决定者 | 内容 |
|---|---|---|---|
| 2026-08-01 | **RFC-002-DQ-01 = ACCEPTED（Accepted with Revision）** | 用户 | 接受 Candidate A 并修订：PostgreSQL 是 Business Current Truth Repository 唯一受支持的权威数据库语义；技术栈 = **PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**；schema/约束/迁移/事务/并发/持久化正确性均以 PostgreSQL 语义定义；**本地开发与正式持久化测试**（repository contract / persistence integration / transaction / concurrency / migration tests）**均对真实 PostgreSQL 运行**；SQLite 不是受支持的 backend，也不是 PostgreSQL 持久化语义的权威替代；SQLite-first → PostgreSQL-later 路线 **REJECTED**；错误引用「RFC-014（迁移策略）」修正为 **RFC-002-DQ-14（Schema Evolution and Migrations）**。原历史 Recommendation「PG 为目标、本地可用 SQLite 以 PG 语义为准」标记为 **Superseded by Accepted Revision**；不建立 SQLite 方言兼容承诺。 |
| 2026-08-01 | **RFC-002-DQ-02 = ACCEPTED（Accepted with Revision）** | 用户 | 接受 Candidate A 并修订：MVP 使用**单一 PostgreSQL 数据库服务**；**每张业务表有且仅有一个所有模块**；所有模块独占拥有其 Repository Port 定义、Infrastructure Repository 实现、ORM / Persistence Models、schema 与 migration 变更、状态修改 Application Use Cases；其他模块不得 import 其 ORM/Persistence Models、获取或复用其 Database Session、调用其 Repository 实现、直接以 SQL/ORM 查询或修改其表、以共享表绕过 Public Application Contract；跨模块读取经目标模块 **Public Application Query**、跨模块状态修改经所有模块 **Public Application Use Case**；直接模块间状态修改访问默认禁止（与 RFC-001-DQ-08 一致）；边界由 **Import Linter + AST/Architecture Tests + Repository Ownership Tests + Migration Ownership Conventions + PR 审查规则**强制（单独代码审查不充分）；架构接受显式命名空间与所有权约定，但 **MVP 不要求每模块独立 PostgreSQL schema**；具体物理命名（PostgreSQL schema/表前缀/等价命名空间）**留待实现设计**（不得削弱所有权；此为 Deferred，非「不需要命名约定」）；**Business/Runtime/Checkpoint 三类存储物理划分不由 DQ-02 决定，继续指派 RFC-002-DQ-13（PROPOSED/PENDING）**。原历史 Recommendation「按模块分 schema/表前缀」中的独立 schema 部分标记为 **Superseded by Accepted Revision**（作为候选历史保留）。 |
| 2026-08-02 | **RFC-002-DQ-03 = ACCEPTED（Accepted with Revision）** | 用户 | 接受 Candidate A 并修订：**Aggregate 边界 = 业务不变量 + 唯一模块所有权**（聚合 = 强制同一组业务不变量的最小单元，其数据归属唯一所有模块，与 DQ-02 Accepted Decision 一致）；**Atomic Business Commit（DEC-035 六要素）是事务提交协议（transaction protocol），不是聚合成员资格判据（not aggregate membership）**，六要素单事务不可拆约束保持有效；**Task Mega Aggregate REJECTED**（不采用整个 Task 单一大聚合）；**默认一个 Application Use Case 提交一个主 Aggregate**；**跨聚合 / 跨模块协调要求显式协调**（Explicit Composite Application Use Case，与 RFC-001-DQ-08 一致）；**Unit of Work / 事务实现形态移交 DQ-05（Transaction Boundary）/ DQ-06（Unit of Work Model）**（均 PROPOSED/PENDING）；**Aggregate / Invariant Matrix 是持久化实施前的必备产出（REQUIRED BEFORE PERSISTENCE IMPLEMENTATION）**，该要求不授权任何实施。原历史 Recommendation「以六要素为聚合边界 / 聚合 = 一次原子提交必须一致的最小单元」标记为 **Superseded by Accepted Revision**（候选历史保留）。 |
| 2026-08-02 | **RFC-002-DQ-04 = ACCEPTED（Accepted with Revision）** | 用户 | 接受 Candidate A 并修订：架构明确区分 **Domain Version Identity**（`domain_version_id`）、**Domain Version Number**（`version_number`）与 **Concurrency Revision**（`revision`），三者不得共享同一字段、不得视为可互换；**Domain Version Identity** = 每个不可变 Domain Version 拥有稳定且全局唯一的 `domain_version_id`，**由 Application 层在 INSERT 前生成**，采用应用生成的 opaque UUID（具体 UUID variant 可在实现设计时选择），不可变且绝不得复用，不得解释为乐观锁计数器 / SQLAlchemy Mapper Version / PostgreSQL `xmin` / 审核 Revision；**Domain Version Number** = 每个逻辑业务对象维护单调递增的 `version_number`（例如 Strategy Version 1、2、3），唯一性约束至少覆盖 `(logical_object_id, version_number)`，历史版本在删除或失效后不得覆盖、重新编号或复用，不得默认与 `revision` 相等；**Concurrency Revision** = 需要并发保护的可变记录（Current Truth Pointers、Aggregate Roots、Stage State、Review Package state 及后续设计识别的其他可变协调记录）使用独立 `revision` 字段，为 NOT NULL 单调递增整数，表达成功的状态变更，不代表 Domain Version Identity / Number，不得用作不可变标识；**每一个针对 revision 保护记录的状态修改 Command 必须携带 `expected_revision` 或等效显式并发前置条件**；更新使用显式 compare-and-swap 语义（`UPDATE ... WHERE id = :id AND revision = :expected_revision`），成功更新递增 `revision`，**零影响行 = stale write / 并发冲突，Atomic Business Commit 必须回滚、不得静默覆盖较新状态**；SQLAlchemy 2.x `version_id_col` **可**作为 Infrastructure 层乐观并发机制，但 mapper 概念 / Session 异常 / `version_id_col` 细节不得泄漏进 Domain Models 或 Public Application Contracts；Infrastructure 必须将 SQLAlchemy stale-state 行为（含适用时的 `StaleDataError`）转换为项目自有并发冲突结果或异常（如 ConcurrencyConflict / StaleRevision / ExpectedRevisionMismatch 类语义，具体命名留待实现设计，本决定不创建代码）；revision 保护记录**不得**经绕过 revision 检查的 ORM bulk UPDATE / DELETE 修改，明确需要的批量操作必须定义 expected revision 规则、条件更新行为与 affected-row 校验；**PostgreSQL `xmin` 不是项目权威业务 revision**（非 Domain Version、非 Public Contract 字段、非 Review Package revision、非稳定跨系统持久化契约——Candidate B 方向拒绝）；**PostgreSQL SERIALIZABLE 隔离不是显式 Concurrency Revision 的替代方案**（Candidate C 方向拒绝；SERIALIZABLE 仍可能作为独立隔离策略由后续 DQ 讨论）；Transaction Isolation 与 Optimistic Revision 正交；**默认隔离级别 / 强隔离 Use Cases / 40001 serialization-failure 重试 / 40P01 deadlock 重试 / SELECT FOR UPDATE / 悲观锁 / retry 所有权与上限留待 DQ-05 与 DQ-07**（均 PROPOSED / PENDING）；DEC-035 Atomic Business Commit 六要素（创建不可变 Domain Version、Formal Evidence Links、更新 Current Truth Pointer、更新 Stage State、写 Audit Record、写 Idempotency Record）**保持同一事务**；Pointer / Aggregate Root / 受保护协调记录的 revision 检查必须在同一 Atomic Business Commit 内；产生新顺序 Version Number 时，版本分配与 Current Truth revision 校验构成一个安全提交协议（读取 pointer/version → 校验 expected_revision → 分配/校验下一 version_number → 插入不可变 Domain Version → 条件更新 pointer → 递增 revision → commit），任何 revision 冲突 / 唯一性冲突 / 写入失败整体回滚；RFC-004 可将 Concurrency Revision 映射为 HTTP ETag / If-Match 语义，但 **HTTP 协议不由 DQ-04 决定**；持久化语义验证**必须使用真实 PostgreSQL**，至少覆盖：两个写者使用相同 expected_revision、过期 Human Review 提交、重复 resume 尝试、Domain Version 与 Pointer 原子更新、防止无保护批量更新、冲突回滚且零部分业务写入；**详细持久化测试策略归 DQ-16**（PROPOSED / PENDING）。原历史 Recommendation「应用层 version 列 + ORM 乐观校验（单一 version 概念）」标记为 **Superseded by Accepted Revision**（候选历史保留：A 接受并修订、B/C 拒绝）。 |
| 2026-08-02 | **RFC-002-DQ-05 = ACCEPTED（Accepted with Revision）** | 用户 | 接受 Candidate A 并修订：**Business Transaction Owner = Application**（业务事务由 Application Use Case 拥有；Entrypoint / Graph Node 不 begin/commit，与架构基线 §14.3、RFC-001-DQ-04 一致）；**Transactional Application Command = 一个短显式事务 + 一个最终提交点**（Use Case 唯一提交点）；**长流程业务操作 = 多个短事务 + 无事务执行阶段**（不存在跨越整个长流程的单一长业务事务，与架构基线 §14.12 一致）；**执行模式 = Prepare → Execute Outside Transaction → Commit**（Prepare 装载所需状态且读取在进入 Execute 前完成；Execute 不持有数据库事务；Commit 以新短显式事务原子提交）；**四项 PROHIBITED**：外部调用（LLM/HTTP/外部工具/供应商 I/O）不得持有开放数据库事务、Human Review 等待不得跨越开放事务（进入审核前相关状态已提交、Resume 用新事务）、Workflow 暂停（interrupt/suspend/waiting）不得跨越开放事务（恢复所需状态暂停前已提交，与 DEC-033 Safe Resume Boundary 一致）、SQLAlchemy Session 不得跨 Workflow 边界（节点 / interrupt / resume 之间；Session 生命周期外置于 Use Case 边界，Resume 以新 Session、新事务重新执行）；**Commit-time Revision Revalidation = REQUIRED**：DQ-04 定义的 revision 保护记录 `expected_revision` compare-and-swap 校验必须在提交事务内发生，不得以提交前读取阶段获得的 revision 值跳过重新校验，零影响行 = 冲突且 Atomic Business Commit 整体回滚；**DEC-035 Atomic Business Commit 六要素单事务保持有效**（DQ-05 定义事务边界与执行模式，不拆分六要素、不修改 DEC-035）；**External Result Before Commit = NOT CURRENT TRUTH**：提交前获得的外部调用执行结果不是 Business Current Truth，仅经成功提交的 Atomic Business Commit 持久化后成为正式业务状态，提交前返回调用方的结果不得视为权威业务真值；**默认 PostgreSQL 隔离级别 = READ COMMITTED**（DQ-04 第 13 点遗留的「默认事务隔离级别」空白由本决定正式确定）；**更强隔离级别（如 SERIALIZABLE / REPEATABLE READ）Use Cases、悲观锁、SELECT FOR UPDATE / SKIP LOCKED、40001 serialization-failure 重试、40P01 deadlock 重试、retry 所有权与重试上限留待 DQ-07**（PROPOSED/PENDING；DQ-05 不决定任何锁或重试策略）；**SAVEPOINT 仅为有限 Infrastructure 机制**（`begin_nested` 仅用于少数事务内部分回滚场景，非业务事务机制、不构成嵌套业务事务，提交语义服从 SQLAlchemy 2.0 官方行为「commit 总作用最外层事务」）；**嵌套业务事务禁止**（业务提交点不得嵌套，不得以 SAVEPOINT 构造嵌套「业务 commit」语义）；**与外部供应商协调的分布式事务 / 两阶段提交拒绝**（业务写入与外部效果的一致性经由 DQ-05 事务边界模式——先提交再外部效果、或外部执行后再新事务提交——与幂等 / Durable Dispatch（DQ-08/09，PROPOSED/PENDING）实现）；**UoW Port 形态（显式/隐式、接口位置、Commit/Rollback 负责方）仍由 DQ-06 拥有**（PROPOSED/PENDING；嵌套业务事务禁止这一规则已由本 DQ-05 决定固定）。原历史 Recommendation「Use Case 拥有唯一提交点、外部调用不持有 DB 事务、长流程拆多个短事务、SAVEPOINT 仅留少数部分回滚场景（[架构推断]）」标记为 **Superseded by Accepted Revision**（候选历史保留：A 接受并修订、B 全程一事务拒绝、C SAVEPOINT 业务混合策略拒绝）。 |
| 2026-08-02 | **RFC-002-DQ-06 = ACCEPTED（Accepted with Revision）** | 用户 | 接受 Candidate A 并修订：**UnitOfWork Port 由 Application 层定义**；**生产 UnitOfWork 实现属于 Infrastructure 层，可使用 SQLAlchemy**；**SQLAlchemy Session 是 Infrastructure 实现细节**，不得暴露给 Domain Models/Domain Services、Application Use Cases、Entrypoints/API handlers、LangGraph nodes/Workflow adapters、Public Application Contracts、外部 Provider adapters；**每个 Transactional Application Command 创建一个新的 UnitOfWork 实例**；**一个 UnitOfWork 实例对应**一个短数据库事务、一个 SQLAlchemy Session、一个显式业务状态迁移、一个最终 commit 或 rollback 结果；**UnitOfWork 是一次性生命周期对象**（NEW → ACTIVE → COMMITTED or ROLLED_BACK → CLOSED），**commit、rollback 或 close 之后不得重用**；UnitOfWork 可暴露显式上下文边界（conceptually：`with uow_factory() as uow: ... uow.commit()`）；**Application Use Case 必须显式调用 commit()**；**正常 context-manager 退出不得自动提交**；**未成功显式 commit 即退出作用域必须**回滚活动事务、关闭并丢弃 Session、释放数据库连接、使 UnitOfWork 不可用；**Use Case 抛出异常时 UnitOfWork 必须**回滚、关闭并丢弃 Session、释放连接、在 Application 错误边界保留或翻译原始失败；Application 可在必要时显式请求 rollback，但强制安全规则不变（exception or exit without commit → rollback → close → discard）；**每个 Transactional Application Command 最多成功 commit 一次**；**非法生命周期操作必须显式失败**（第二次 commit、成功 commit 之后 rollback、close 之后访问 Repository、rollback 之后使用事务、重用失败的 UnitOfWork、跨 Workflow 边界重用 UnitOfWork）；**UnitOfWork 仅暴露所属 Application 能力或事务性操作所需的显式、类型化 Repository Ports**；**UnitOfWork 不得提供** `get_repository(name)`、通用 repository 字典或 registry、Service Locator、raw Session accessor、通用 `execute_sql()`、任意跨模块 Repository lookup、按字符串或运行时类型的动态 Repository 解析；**每个业务模块继续拥有其 Repository Ports、Infrastructure Repository 实现、ORM models 与 tables**（与 DQ-02 一致）；参与同一 UnitOfWork 的 Repositories 内部共享同一 Infrastructure 事务与 Session，但该 Session 不得经其公共接口暴露；**Repository 实现不得调用或控制** `begin()`/`commit()`/`rollback()`/`close()`/`begin_nested()`/SAVEPOINT 生命周期/UnitOfWork 生命周期迁移；**Repository 职责限于**加载其 Port 允许的 Aggregates 或持久化记录、在当前 UoW 内暂存或持久化 Aggregate 变更、执行所属模块允许的查询、返回项目自有的 Domain/Application 结果、将持久化失败传播到 UoW/Application 边界；**嵌套业务 UnitOfWork 被禁止**——已拥有活动 UnitOfWork 的 Transactional Application Use Case 不得调用另一个会创建新 UnitOfWork 或独立提交的 Transactional Use Case；**可复用业务行为必须改为提取为** Domain Service、transaction-neutral Application Service、接收显式 Ports 的内部 Application 操作、在既有外层 UoW 下执行的另一个操作；**当多个操作必须参与同一个即时一致性事务时，由 Explicit Composite Application Use Case 拥有唯一外层 UnitOfWork 与唯一最终提交点**；Composite Application Use Case 必须记录跨 Aggregate 业务不变量、使用显式类型化 Repository Ports、保持唯一模块与表所有权、在模块边界需要处使用 Public Application Contracts、避免共享全局 Session 状态、避免多个嵌套 UnitOfWork 实例、保留唯一外层提交权威；**UnitOfWork 处于 ACTIVE 期间禁止**隐式加入另一个 ambient UnitOfWork、打开第二个业务 UnitOfWork、把子操作的 commit 解释为部分提交、以 SAVEPOINT 作为嵌套业务 commit、把 commit 所有权移交给 Repository、把 UnitOfWork 存入全局/thread-local/Workflow 状态；**检测到嵌套业务 UnitOfWork 企图必须立即失败**（经项目自有的架构或事务错误，确切错误名留待实现设计）；**SAVEPOINT 不是嵌套 UnitOfWork，也不由 Application UnitOfWork Port 暴露**；任何有限的 Infrastructure 级 SAVEPOINT 使用仍受 DQ-05 治理，且不得创建独立业务 commit、拆分 DEC-035 Atomic Business Commit、包裹外部调用或等待期、授予 Repository 提交权威、削弱失败即回滚语义；**UnitOfWork Port 默认不暴露 flush()**；Infrastructure 可在数据库约束、生成值或持久化排序需要时执行内部 SQLAlchemy flush；**内部 flush 不是业务 commit，不得表示为业务成功完成**；**flush 失败时**当前数据库事务必须回滚、Session 必须关闭并丢弃、当前 UnitOfWork 变为不可用、同一 UnitOfWork 不得继续追加业务写入；**Engine 与 sessionmaker 可作为 Composition Root 拥有的长生命周期 Infrastructure 资源**；**每个具体 Session 是短生命周期的**，由一个 UnitOfWork 为一个本地 Transactional Application Command 创建；**全局可变 Session 被禁止**；**`scoped_session`、thread-local Session、基于 ContextVar 的 ambient Session 或 ambient UnitOfWork 不得作为主要事务所有权或依赖注入机制**；**每个并发 Command、Worker 执行、Retry、Rerun 或 Resume 使用独立 UnitOfWork 与独立 Session**；**与 DQ-05 一致**：Prepare 与 Commit 作为不同 Transactional Application Commands 时使用不同 UnitOfWork 实例、Execute Outside Transaction 无活动 UnitOfWork、Human Review 等待不持有 UnitOfWork、LangGraph Interrupt 不持有 UnitOfWork、retry backoff 不持有 UnitOfWork、UnitOfWork 绝不序列化进 Checkpoint、UnitOfWork 绝不在 Resume 时恢复；**UnitOfWork 适用于状态修改的 Transactional Application Commands**；**纯读 Application Queries 使用独立的短 Query Scope 或 Read Model Adapter**——纯 Query Scope 不暴露 commit()、查询结束后关闭 Session 并释放连接、不返回 ORM entities 或 lazy-loaded relationships、不复用 Command UnitOfWork、不成为跨模块持久化 API；**若读取结果参与后续原子状态变更或并发决策，它必须**发生在拥有最终 commit 的 UnitOfWork 内、或在 Commit 事务内重新校验（与 DQ-04 和 DQ-05 一致）；**Candidate A 以此修订被接受**；**Candidate B（装饰器或 context-manager 退出自动提交）作为项目 UnitOfWork 模型被拒绝**（Context managers 仍允许用于生命周期清理，但成功的业务提交必须保持显式）；**Candidate C（Repository 管理事务）被拒绝**（违反 Application 事务所有权与单一提交点）；**RFC-002-DQ-06 不决定**乐观与悲观并发组合、数据库锁选择、序列化或死锁重试策略、幂等键层级、Outbox API 或 dispatch 实现、Event 或 Audit 发布顺序、HTTP 请求作用域、LangGraph 运行时作用域、Checkpoint 实现、完整持久化测试分类；**剩余所有权分配**：并发/锁/重试 → DQ-07、幂等 → DQ-08、Outbox 与 Durable Dispatch → DQ-09、Event 与 Audit 语义 → DQ-10、API 与 HTTP 请求协议 → RFC-004、Workflow 与 Checkpoint 运行时 → RFC-003、详细持久化测试策略 → DQ-16；**持久化语义验证必须使用真实 PostgreSQL**，至少覆盖：显式 Use Case commit 成功、未 commit 退出回滚、异常退出回滚、flush 失败回滚并丢弃 Session、Repository 无法独立 commit 或 rollback、嵌套 UnitOfWork 被拒绝、Composite Application Use Case 使用唯一外层 UnitOfWork、UnitOfWork 在 commit 后不可重用、并发 Commands 使用独立 Sessions、Prepare 与 Commit 使用不同 UnitOfWork 实例、Execute Outside Transaction 不持有 Session 或连接、只读 Query Scope 干净关闭、无 UnitOfWork 跨越 Human Review/Interrupt/Retry/Resume（详细测试组织与 CI 执行仍由 DQ-16 拥有）。原历史 Recommendation「显式 UoW、禁止嵌套业务事务（SAVEPOINT 仅基础设施级部分回滚）」标记为 **Superseded by Accepted Revision**（候选历史保留：A 接受并修订、B 退出自动提交拒绝为项目 UoW 模型、C Repository 管理事务拒绝；Context Manager 允许用于生命周期清理但不得自动提交业务状态）。 |
| 2026-08-02 | **RFC-002-DQ-07 = ACCEPTED（Accepted with Revision；Accepted Direction = Layered Concurrency Control）** | 用户 | 接受分层并发控制修订方案：**项目采用分层并发控制（layered concurrency control），而非依赖单一通用锁机制**；**普通 Business Current Truth、Aggregate Roots、Current Truth Pointers、Stage State、Review Package state 及其他受保护可变记录的状态修改，默认使用 RFC-002-DQ-04 接受的乐观并发协议**（revision；expected_revision；conditional update；affected-row validation）；**乐观 revision 是普通业务状态修改的默认并发机制**；**expected_revision 不匹配是语义业务冲突，不得作为瞬时数据库失败盲目重试**——并发审批必须返回冲突、过期 Human Review 提交必须拒绝、同时失效只允许一个成功提交、后提交者不得静默覆盖较新状态、过期外部执行结果不得重新绑定到较新 Domain Version；SQLAlchemy `version_id_col` 可继续作为 Infrastructure 实现机制，但 Infrastructure 必须将 stale-state 行为翻译为项目自有的并发结果；revision 保护记录不得经绕过 expected_revision 与 affected-row 校验的 ORM bulk UPDATE/DELETE 更新；**数据库唯一约束是防止重复业务事实的最终完整性防线**，最终必须至少覆盖：重复的不可变 Domain Version identity 或 numbering、重复的正式 Review Decision identity、重复的已提交业务 Command identity、后续接受的决定所要求的重复 Dispatch 或 Attempt identities、其他已命名的业务唯一性不变量；**唯一约束违反不得被统一视为可重试错误**，Infrastructure 与 Application 错误边界必须识别被违反的命名约束并至少区分：已完成的重复操作、幂等重放、version-number 分配竞争、重复 Review Decision、真实数据完整性缺陷、未分类唯一约束违反；**完整幂等键层级、输入指纹、结果重放与去重存储仍由 DQ-08 拥有**；**Duplicate Resume、并发 Worker 执行以及同一并发范围的执行所有权需要 Durable Execution Guard 或 Durable Lease**——Lease 模型必须包含 `concurrency_scope_id` 或等效持久化范围标识、当前持有者或当前 Attempt identity、Lease 获取时间、Lease 过期时间、单调递增的 generation 或 `fencing_token`、active/released/expired 生命周期语义（确切表名/字段名/索引/物理存储位置留待实现设计与 DQ-13 边界）；**Lease 获取必须发生在一个短的 PostgreSQL 事务内，成功获取必须在长时间执行开始前提交，提交之后行锁、Session、UnitOfWork 与数据库连接必须被释放**；**Worker 在 LLM 执行、外部 HTTP 或工具调用、Human Review 等待、Workflow Interrupt、retry backoff、长时间计算、跨进程执行期间不得持有 PostgreSQL 行锁**；**每次成功的 Lease 获取、接管或重新分配必须颁发一个单调递增的 fencing_token 或 generation；持有较旧 fencing_token 的过期 Worker 不得提交 Business Current Truth——即使它仍在运行并最终返回一个看似有效的结果**；**Worker Commit 必须在最终短事务内验证**：expected_revision、当前 Lease Holder、当前 fencing_token、当前 Attempt 或 Run identity、后续由 DQ-08 接受的适用幂等身份、Application Command 要求的全部业务不变量；**若 Lease 已过期、已释放或被另一 Worker 获取，旧 Worker 的结果必须作为 stale 被拒绝**；**进程本地 asyncio.Lock、threading.Lock、mutex 或内存任务锁只能作为非权威优化使用（减少重复工作），不得成为业务正确性的来源**；正确性必须在进程重启、Worker 崩溃、多个 Worker 进程、多个部署副本、机器替换、内存状态丢失下保持完整；**SELECT FOR UPDATE SKIP LOCKED 仅允许用于显式的队列式 Claim 操作**，且必须使用短事务：select candidate → lock candidate → assign durable holder / Lease / fencing token → commit → release the lock and connection → execute outside the transaction；**SKIP LOCKED 不得用于**普通 Current Truth 读取、Human Review 读取、需要完整一致结果集的查询、绕过 expected_revision 冲突、静默忽略正在被修改的业务对象、跨外部调用持有执行所有权；**SELECT FOR UPDATE、NOWAIT 及其他悲观行锁机制不是全局默认**——Use Case 只有在记录以下内容时才可采用悲观锁：受保护的业务不变量、为何乐观 expected_revision 不足、要锁定的确切行、确定性锁顺序、blocking/NOWAIT/SKIP LOCKED 行为、最大事务时长、超时与错误翻译、任何自动重试是否安全、真实 PostgreSQL 并发测试证据；锁定多个业务对象的事务必须使用确定性全局锁顺序以降低死锁风险；**Session-level PostgreSQL Advisory Locks 作为项目默认或权威并发控制机制被禁止**；**Transaction-level PostgreSQL Advisory Locks 不是默认机制**，只有在自然数据库行无法表达并发范围时才可经独立架构审查考虑；**PostgreSQL SQLSTATE 40001 serialization_failure 与 SQLSTATE 40P01 deadlock_detected 被归类为可能瞬时的数据库事务失败**；**40001 与 40P01 的有限自动重试由 Application Transaction Runner 或 Command Executor 拥有**；**Repository 实现、SQLAlchemy Session 对象与 UnitOfWork 实现不得静默执行自己的事务重试循环**；**每次事务重试必须**重新开始整个短事务、创建新的一次性 UnitOfWork、创建新的 SQLAlchemy Session、重新加载当前状态、重新评估业务前置条件、重新运行 revision 与 Lease 验证、丢弃失败尝试中的全部 ORM entities；**默认重试预算 = 一次初始事务尝试 + 最多两次重试尝试 = 共计三次事务尝试；无限或无界重试被禁止**；**retry backoff 与 jitter 必须发生在任何开放数据库事务、UnitOfWork 或 Session 之外**（具体 backoff 时长、jitter 参数、指标与告警阈值可在 RFC-007 下配置，但有界重试要求不得被移除）；**以下冲突不得盲目或自动重试**：expected_revision 不匹配、stale fencing_token、丢失或过期的 Lease、过期 Human Review 提交、业务不变量拒绝、过期外部结果、未分类的 unique_violation、lock_not_available 或 NOWAIT 失败（除非特定 Use Case 定义了可接受的重试策略）；已分类的重复操作只有在 DQ-08 幂等语义下才可转换为幂等响应；**外部 LLM、HTTP Provider 或工具执行不得在数据库事务重试循环内运行**；当业务前置条件仍然有效时，Commit 事务可使用已产生的、不可变的外部结果进行重试；**重试 Commit 事务不得自动重新调用外部 Provider**；**五类必备并发场景的控制组合**：duplicate resume = Durable Lease + fencing_token + DQ-08 幂等身份；concurrent approval = expected_revision compare-and-swap + 唯一 Review Decision identity；stale worker = Lease Holder 验证 + fencing_token + expected_revision；repeated command = 命名数据库唯一约束 + DQ-08 幂等记录；simultaneous invalidation = 对所属 Aggregate、Stage State 或 Current Truth Pointer 的 expected_revision compare-and-swap；**LangGraph thread_id 与 Checkpoint identity 用于定位工作流状态与恢复位置，不得被视为** Business Concurrency Lock、Durable Lease、fencing_token、业务 Idempotency Record、只有一个 Resume 处于活动状态的证明；**RFC-002-DQ-07 不决定**完整幂等键层级与响应重放模型、Outbox 与 Dispatch Claim 实现、Event 与 Audit 持久化顺序、Checkpoint 并发与 Runtime 对账、API 冲突状态码或 ETag/If-Match 协议、完整持久化测试分类与 CI 执行设计；**剩余所有权分配**：幂等层级与重放 → DQ-08；Outbox / Durable Dispatch → DQ-09；Event / Audit 语义 → DQ-10；Checkpoint 并发与 Runtime 对账 → RFC-003；API 冲突协议与 ETag / If-Match → RFC-004；完整测试策略 → DQ-16；运维重试指标与阈值 → RFC-007；**Concurrency Scenario Matrix 在持久化或并发控制实现开始之前是必需的**，必须至少标识：Scenario、Concurrency Scope、Protected Business Invariant、Optimistic Revision requirement、Database Unique Constraint、Durable Lease requirement、fencing_token requirement、Pessimistic Lock requirement、Retry classification、Retry owner、maximum attempts、user-visible conflict result、related DQ/DEC/RFC——**Matrix 的创建不由 DQ-07 的接受授权**，需要后续的规划或实现就绪授权；**真实 PostgreSQL 多 Worker Concurrency Technical Spike 在并发控制实现被授权之前是必需的**，必须使用真实 PostgreSQL、多个独立数据库连接、至少两个独立执行的 Workers 或进程、确定性故障与时序注入、没有任何部分 Current Truth 写入在冲突后存活的证据，并至少验证：两个并发 Resume 尝试产生一个权威 Lease、Lease 过期与接管产生更高的 fencing_token、持有 stale fencing_token 的旧 Worker 无法提交、两个使用相同 expected_revision 的审批只允许一个提交、SKIP LOCKED 不会对一个队列项双重领取、40001 与 40P01 重试创建全新 UoW 与 Session 实例、事务重试不重复外部 Provider 调用、并发版本分配不产生重复 Domain Version、冲突回滚产生零部分 Current Truth 写入——**Concurrency Technical Spike 是必需的，但不被本 Accepted Decision 授权；Spike Issue、Branch、PR、代码、测试或基础设施的创建需要单独明确的用户授权**；详细持久化测试组织仍由 DQ-16 拥有；**所有正式并发语义测试必须使用真实 PostgreSQL，而非 SQLite 或内存替代品**。原历史 Recommendation「DB 唯一约束兜底幂等 + 乐观 version 列做 Current Truth 更新 + task 领取用悲观/SKIP LOCKED + 同 task 应用层序列化（[架构推断]，置信度中）」标记为 **Superseded by Accepted Revision**（候选历史保留：Optimistic revision 接受为默认业务写控制、Database unique constraints 接受为最终完整性防线、SKIP LOCKED 以受限方式接受为仅队列式 Claim、进程内序列化修订为非权威优化；新增 Durable Lease + fencing_token 执行所有权要求、Session-level Advisory Lock 禁止、Application Transaction Runner 有界重试、语义冲突不盲目重试、Matrix 与 Spike 实现前置条件）。 |
| 2026-08-02 | **RFC-002-DQ-08 = ACCEPTED（Accepted with Major Revision；Primary Direction = Candidate B；Supporting Principle = Candidate C；Rejected Direction = Candidate A as Universal Table）** | 用户 | 接受分层幂等模型重大修订方案：**项目采用分层幂等模型，不采用一张跨模块、跨所有语义的 Universal Idempotency Table**——各幂等层由相应 Owning Module 持久化（每份幂等记录有且仅有一个 Owning Module，遵守 DQ-02 表所有权与跨模块访问边界；模块可为自身同类 Commands 使用模块私有 Command Idempotency Table），所有幂等层共享统一概念与行为契约（logical operation identity / owning module / idempotency scope / idempotency key / input fingerprint / execution status / retry-rerun semantics / unique constraint / result replay semantics / atomic transaction boundary），**统一概念契约不意味着统一物理表**；**Candidate B（分层各自存储）作为主要持久化方向接受，Candidate C（天然幂等 set/ensure/replace-to-desired-state/compare-and-set 语义）作为强制设计原则接受（不得替代显式记录、唯一约束或执行所有权控制，尤其涉及创建 Domain Version、外部副作用、Review Decision、Dispatch、计费或配额、append-only Audit、只能发生一次的正式业务事实；避免无保护 increment/append/toggle/duplicate create），Candidate A 作为跨模块、跨 Command/Workflow/Consumer/Dispatch/Provider 调用的万能 Idempotency Table 拒绝**；**身份模型**：Command ID / Idempotency Key / Attempt ID / Stage Run ID / Review Decision ID / Dispatch ID / Provider Call Identity 明确区分不得混用、不得由通用 ID 字段隐式取代——Command ID（Application 层生成的一次逻辑状态修改 Command）在数据库 Retry 或执行 Retry 中复用、Intentional Rerun 创建新 Command ID 并保留 `rerun_of`/`parent_command_id` 或等价关系；Idempotency Key（调用者要求去重与结果重放的逻辑身份）在明确 Idempotency Scope 内唯一（Scope 至少等价表达 owning module / operation type / target business scope / tenant-account scope 如未来存在 / idempotency key），不得只按整库裸 Key 推断语义；Attempt ID（一次具体执行尝试）每次 Retry 新建、不是业务幂等 Key、不得判断逻辑 Command 是否完成；Stage Run ID 同一 Stage Run 内 Retry 保持、Intentional Rerun 新建；Retry 不得创建新 Domain Version，Intentional Rerun 成功后可产生新 Domain Version；Review Decision ID 不可变、命名唯一约束保护、不得正式提交两次；Dispatch ID 语义留 DQ-09；**Retry 与 Rerun 身份语义**：Retry = same Command ID / same Idempotency Key / same Stage Run ID / same Input Fingerprint / new Attempt ID / no new intended business operation；Intentional Rerun = new Command ID / new logical Idempotency identity / new Stage Run ID / new Attempt ID / explicit relation to previous run / may produce new business version after successful commit；不得通过是否发生异常隐式判断、必须由明确 Application Intent 区分；**Versioned Input Fingerprint**：每个幂等保护操作必须计算版本化指纹（基于规范化业务有效输入，不依赖原始 JSON 字节顺序或任意序列化；定义明确 canonicalization version / fingerprint schema version / hash algorithm / included business fields / excluded transport and observability fields；含 target business identity / expected revision / base Domain Version / Command parameters / Source-Evidence Version references / selected operation mode；不含 trace ID / arrival timestamp / retry counter / Attempt ID / connection metadata / 观测字段）；**同 Scope + Key + 相同 Fingerprint = 同一逻辑操作（重放原 Application Result，不重复执行业务副作用）；同 Scope + Key + 不同 Fingerprint = Idempotency Key Conflict（不得覆盖原记录、不得执行新业务操作、不得把旧结果重放为新请求结果、不得盲目自动重试）**；**状态机与执行所有权**：至少表达 IN_PROGRESS / SUCCEEDED / FAILED_TERMINAL / ABANDONED-EXPIRED-RETRYABLE 等非终局状态（精确 Enum 名留实现设计）；IN_PROGRESS = 逻辑操作已被有效 Attempt 领取，重复请求看到有效 IN_PROGRESS 不得再次执行相同业务副作用；**IN_PROGRESS 执行所有权与 DQ-07 Durable Lease / Lease Holder / Attempt ID / fencing_token 协同——只有当前有效 Lease Holder 和 fencing_token 可把幂等记录转换为最终成功状态；Lease 过期/被接管/fencing_token 失效后旧 Worker 不得写入 SUCCEEDED；Checkpoint 与 LangGraph thread_id 不作为 Business Idempotency Record**；**原子提交与结果重放**：业务成功时 Business Current Truth 更新 / Domain Version / Formal Evidence Links / Current Truth Pointer / Stage State / Audit Record / Idempotency Record 成功状态 / 不可变 Application Result Snapshot 或结果引用必须在同一个 DEC-035 Atomic Business Commit 中提交；业务事务回滚不得留下 SUCCEEDED Idempotency Record；Commit 成功但响应丢失时相同 Scope+Key+Fingerprint 后续请求重放原 Application Result（不重复副作用）；重放结果为项目自有稳定快照或不可变引用；幂等记录不得保存/返回 ORM Entity / SQLAlchemy Session / Python Exception / 原始数据库错误 / 未脱敏 Secret / 传输层强绑定可变对象；HTTP Status/Headers/Response Body/Header 名称留 RFC-004；**失败分类**：确定性终局业务结果（已正式确定且再执行不变的业务拒绝或冲突）可记录并稳定重放；瞬时基础设施失败（连接超时 / SQLSTATE 40001 / SQLSTATE 40P01 / 临时 Provider 不可用 / Worker Crash / Lease 过期 / 可恢复网络故障）不得永久固化为终局结果，可用相同逻辑幂等身份 + 新 Attempt ID 重试（继续受 DQ-07 有界重试、Lease、Fencing Token 约束）；领取与副作用前的纯输入验证失败可不创建可重放终局记录；**分层幂等四层**：(a) Business Command Idempotency Record 由执行业务状态修改的模块拥有、与业务更新同一 PostgreSQL 事务提交、不得成为跨模块共享读写表；(b) Message Consumer Deduplication Record 由消费模块拥有（Message ID/Dispatch ID + Consumer Scope 组合唯一）、Dedup Marker 必须与消费产生的业务更新同事务提交、不得先提交 Dedup Marker 再执行业务写入；(c) Workflow Retry Idempotency：Runtime 负责 Attempt 与运行位置、Business Module 防止重复 Business Commit、Resume 经 Command Identity + 数据库幂等记录 + Lease 与 Fencing 校验、Checkpoint 不替代业务幂等记录；(d) External Provider Idempotency：Provider Adapter 使用稳定 Provider Call Identity、Retry 复用同一 Provider Idempotency Key（绑定 Input Fingerprint）、Intentional Rerun 用新 Provider Call Identity、DB 事务 Retry 不生成新 Provider Key；Provider 原生支持 Idempotency Key 时稳定映射系统逻辑调用身份；不支持原生 Idempotency 时 Provider/Integration 模块维护 Durable Call Ledger（Provider Call Identity / Input Fingerprint / execution status / Attempt relationship / result reference / reconciliation state）；已完成 Provider 调用不得因 DB 事务重试被自动再次调用；对账与补偿留相应 Provider RFC/Adapter；**物理模型与边界**：表名/字段/索引/分区/Storage Placement 留实现设计与 DQ-13；Retention/TTL/删除/Key 再利用留 DQ-15（决定前不得假设 Key 短期删除 / 自动复用归档 Key / 依赖内存 Cache 作权威幂等存储）；敏感载荷不无必要复制；Hashing/Encryption/Redaction/Secret/PII 留 DQ-17；DQ-08 不提前决定 Outbox/Dispatch 表和 Relay（→DQ-09）、Event/Audit 分类和持久化顺序（→DQ-10）、Workflow Runtime/Checkpoint 协调（→RFC-003）、HTTP 幂等 Header/状态码/响应协议（→RFC-004）、Retention 数值（→DQ-15）、完整测试分类和 CI（→DQ-16）、Security/Encryption/PII（→DQ-17）；**Idempotency Identity Matrix（18 字段：Operation / Owning Module / Logical Command ID / Idempotency Scope / Idempotency Key Source / Retry Identity / Rerun Identity / Attempt ID / Stage Run ID / Input Fingerprint Fields / Fingerprint Schema Version / State Machine / Unique Constraint / Atomic Transaction Boundary / Result Replay / Provider Idempotency / Retention Owner / Related DQ/DEC/RFC）为幂等实现开始前的必备产出，但 DQ-08 接受不授权创建该 Matrix（Idempotency Identity Matrix Creation = NOT AUTHORIZED）；本决定不要求新增独立 Technical Spike，DQ-07 已要求的真实 PostgreSQL 多 Worker Concurrency Technical Spike 继续有效并应覆盖幂等并发场景**；**测试前置**：所有正式幂等语义验证使用真实 PostgreSQL，后续测试至少覆盖同 Key+同 Fingerprint 并发请求仅一次业务效果 / 同 Key+不同 Fingerprint 返回冲突 / Commit 成功但响应丢失后重放 / Retry 不创建新 Domain Version / Intentional Rerun 创建新逻辑身份 / Review Decision 只提交一次 / Consumer Dedup 与业务更新同事务 / Worker Crash 后 IN_PROGRESS 接管 / stale fencing_token 无法完成记录 / Provider 成功但 DB Commit 失败后不重复调用 / 瞬时失败创建新 Attempt / 终局结果稳定重放（详细测试组织与 CI 归 DQ-16）；历史 Recommendation「统一幂等表为主 + 设值语义为辅（[架构推断]，置信度中-高）」被重大修订取代（Superseded by Accepted Major Revision） |

### Open User Decisions（待用户决定）

```text
RFC-002-DQ-09 ~ DQ-17 = PROPOSED — User Decision: PENDING（9 项）
RFC-002 Acceptance    = USER DECISION REQUIRED
RFC-002 Merge         = USER DECISION REQUIRED
Implementation        = NOT AUTHORIZED（DQ-01/02/03/04/05/06/07/08 接受不授权任何实施；Concurrency Scenario Matrix 创建、Concurrency Technical Spike 执行与 Idempotency Identity Matrix 创建均需另行授权）
```

---

## Outcome（结果）

```text
RFC-002 Status                = IN REVIEW
RFC-002-DQ-01                 = ACCEPTED（2026-08-01 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-02                 = ACCEPTED（2026-08-01 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-03                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-04                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-05                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-06                 = ACCEPTED（2026-08-02 用户正式决定，Candidate A，Accepted with Revision）
RFC-002-DQ-07                 = ACCEPTED（2026-08-02 用户正式决定，Accepted Direction: Layered Concurrency Control，Accepted with Revision）
RFC-002-DQ-08                 = ACCEPTED（2026-08-02 用户正式决定，Primary Direction: Candidate B，Supporting Principle: Candidate C，Accepted with Major Revision）
RFC-002 Decision Questions    = DQ-01~08 ACCEPTED；DQ-09~17 PROPOSED
RFC-002 Recommendation        = PROPOSED（DQ-01/02/03/04/05/06/07/08 Recommendation Superseded by Accepted Decision）
RFC-002 Pull Request          = OPEN（PR #24）
Required Checks               = PASS（8/8）
User Decisions                = DQ-01~07 = ACCEPTED WITH REVISION；DQ-08 = ACCEPTED WITH MAJOR REVISION；DQ-09~17 = PENDING（9 项）
Implementation                = NOT AUTHORIZED

Immediate Next Gate = 用户审查并决定 RFC-002-DQ-09 Transactional Outbox / Durable Dispatch
```

**Coding Agent 不自行接受任何 DQ、不接受 RFC-002、不 Merge PR、不开始任何持久化/数据库/业务/生产运行时实现。**
