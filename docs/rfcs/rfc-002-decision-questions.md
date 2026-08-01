# RFC-002 Decision Questions：持久化与事务架构决策问题集（DQ-01~10 ACCEPTED；DQ-11~17 PROPOSED）

> **Status:** DQ-01 = **ACCEPTED**（2026-08-01 用户正式决定，Accepted with Revision）；DQ-02 = **ACCEPTED**（2026-08-01 用户正式决定，Accepted with Revision）；DQ-03 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-04 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-05 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-06 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision）；DQ-07 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Revision，Accepted Direction = Layered Concurrency Control）；DQ-08 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Primary Direction = Candidate B，Supporting Principle = Candidate C）；DQ-09 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate B，Formal Pattern = PostgreSQL-backed Transactional Durable Work Intent）；DQ-10 = **ACCEPTED**（2026-08-02 用户正式决定，Accepted with Major Revision，Accepted Candidate = Candidate A）；DQ-11~DQ-17 = PROPOSED（**无一 Accepted**）
> **服务 RFC：** RFC-002 — Persistence and Transaction Architecture
> **治理：** DEC-036（Controlled Git/GitHub Execution）· DEC-038（RFC and Issue Governance）
> **证据底座：** `rfc-002-research-persistence-requirements.md`（需求矩阵）· `rfc-002-analysis-cross-rfc-boundary.md`（边界矩阵）· 四条一手官方研究（SQLAlchemy / LangGraph Checkpointer / PostgreSQL-SQLite-Alembic / 模式定义）
> **纪律（恒定成立）：**
> - DQ-01~DQ-10 已由用户正式决定（均 `Status = ACCEPTED`；DQ-01~DQ-07 的 `User Decision = ACCEPTED WITH REVISION`，DQ-08/DQ-09/DQ-10 的 `User Decision = ACCEPTED WITH MAJOR REVISION`）；DQ-11~DQ-17 的 `User Decision = PENDING`，`Status = PROPOSED`；**只有用户**能把 DQ 标记为 ACCEPTED。
> - `Recommendation` 是**架构建议**，**绝不**写成 Accepted Decision；采纳与否由用户在 Decision Gate 决定。DQ-01/02/03/04/05/06/07/08/09/10 的历史 Recommendation 已被各自的 Accepted Decision 取代（Superseded by Accepted Revision / Major Revision）。
> - 每条区分：**[DEC 约束]**（已 Accepted 的项目决定，RFC 不得推翻）/ **[官方能力]**（官方文档/源码明确能力）/ **[架构推断]**（由官方事实推导的建议）/ **[未决假设]**。
> - 真正的架构分歧**写入 DQ**，不替用户私下决定。

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
| DQ-11 | Snapshot vs History | 版本化历史 + 审计，不上完整 ES | DEC-013 排除 ES |
| DQ-12 | Source & Evidence Persistence | 原始内容存 DB vs 引用 + 大内容边界 | PG TOAST/bytea/外部存储 |
| DQ-13 | Workflow Checkpoint Separation | 同库/分库、生命周期、对账权威 | DEC-023/024；官方无同库建议 |
| DQ-14 | Schema Evolution & Migrations | forward-only、autogenerate 纪律 | Alembic 官方立场 |
| DQ-15 | Data Retention & Deletion Boundary | 各类数据保留策略归属 | checkpoint 无内建 TTL |
| DQ-16 | Persistence Testing Strategy | 真实 DB vs SQLite fake | 并发语义不可移植 |
| DQ-17 | Security & Sensitive Data Boundary | Secret/PII 不落 checkpoint | Secret 明文序列化风险 |

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
- **Recommendation：** **[架构推断] 倾向 A**——current truth + 版本化历史 + append-only 审计；**显式立场：不采用完整 Event Sourcing**（与 DEC-013 一致）。**置信度：高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——DB 存中小原始内容与全部证据元数据/链接（含 content_hash、parser_version provenance），特大/二进制走外部对象存储 + 引用；Retrieval Index 落点边界定给 RFC-005。**置信度：中**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——同实例独立 schema/表、逻辑分离；checkpoint 保留/清理由应用层实现（cron），对账以 Business Current Truth 为权威、checkpoint 让步。**置信度：高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——forward-only、autogenerate 必经人工 review、破坏性变更显式 gate、滚动升级用 expand-contract、大 backfill 拆独立步骤。**置信度：中-高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——分类定责，业务真值/审计 append-only 不删，checkpoint/运行记录由应用层可回收，原始来源保留策略留合规决定（**具体周期数值由用户定，不虚构**）。**置信度：中**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——快速 fake 跑单元/契约，真实目标引擎跑并发/事务/迁移/幂等语义（填 R-1 GAP）。**置信度：中-高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——Secret 不落持久化真值/checkpoint/审计，业务敏感列分类 + least privilege，checkpoint 反序列化白名单（与 DEC-035 一致），加密/密钥管理移交后续、本 RFC 不实现。**置信度：高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

---

## 汇总：待用户逐项决定（DQ-01~10 ACCEPTED；DQ-11~17 PENDING）

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
RFC-002-DQ-11  Snapshot vs History                   = PROPOSED — User Decision: PENDING
RFC-002-DQ-12  Source & Evidence Persistence         = PROPOSED — User Decision: PENDING
RFC-002-DQ-13  Workflow Checkpoint Separation        = PROPOSED — User Decision: PENDING
RFC-002-DQ-14  Schema Evolution & Migrations         = PROPOSED — User Decision: PENDING
RFC-002-DQ-15  Data Retention & Deletion Boundary    = PROPOSED — User Decision: PENDING
RFC-002-DQ-16  Persistence Testing Strategy          = PROPOSED — User Decision: PENDING
RFC-002-DQ-17  Security & Sensitive Data Boundary    = PROPOSED — User Decision: PENDING

RFC-002 Acceptance = USER DECISION REQUIRED
Implementation     = NOT AUTHORIZED
```
