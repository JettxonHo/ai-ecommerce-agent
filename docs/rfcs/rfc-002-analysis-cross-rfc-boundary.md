# RFC-002 Supporting Analysis：跨 RFC 边界分析（Cross-RFC Boundary Matrix）

> **Status:** SUPPORTING ANALYSIS（边界工件，非 Accepted Decision）
> **服务 RFC：** RFC-002 — Persistence and Transaction Architecture
> **目的：** 精确划定 RFC-002 的**决策所有权**（Owns）与**依赖边界**（later RFC dependency），防止 RFC-002 越权替 RFC-003 ~ RFC-007 做决定。
> **纪律：** 每条标注 `RFC-002 OWNS`（本 RFC 决定）、`INTERFACE for later RFC`（本 RFC 定义契约、后续 RFC 消费）、`DEFERRED to RFC-00X`（本 RFC 不决定、显式移交）、`OUT OF SCOPE`（本 RFC 显式不涉及）。
> **Synchronization Note（2026-08-01）：** 矩阵行 1/2 的 DQ-01 已由用户正式决定（**RFC-002-DQ-01 = ACCEPTED，Accepted with Revision**）：PostgreSQL 是唯一受支持的权威数据库语义；技术栈 = PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic；本地开发与正式持久化测试使用真实 PostgreSQL；SQLite-first REJECTED。矩阵行 3 的 DQ-02 已由用户正式决定（**RFC-002-DQ-02 = ACCEPTED，Accepted with Revision**）：MVP 单一 PostgreSQL 服务；每张业务表唯一所有模块；ORM/Repository/Migration/状态修改 Use Case 模块私有；跨模块仅经 Public Application Contract（读经 Public Query、写经 Public Use Case）；Direct SQL/ORM/Repository 跨模块访问禁止；边界由 Import Linter + AST/Architecture Tests + Repository Ownership Tests + Migration Ownership Conventions + PR 审查强制；每模块独立 PostgreSQL schema 暂缓、物理命名留待实现设计。矩阵行 4 的 DQ-03 已由用户正式决定（**RFC-002-DQ-03 = ACCEPTED，Accepted with Revision**，2026-08-02）：聚合边界 = 业务不变量 + 唯一模块所有权；Atomic Business Commit（DEC-035 六要素）是事务提交协议、非聚合成员资格判据（六要素单事务保持有效）；Task Mega Aggregate REJECTED；默认一 Use Case 一主 Aggregate；跨聚合/跨模块显式协调；UoW 形态移交 DQ-05/06（PROPOSED/PENDING）；Aggregate/Invariant Matrix 实施前必备。以上均为 **Accepted user decision**；矩阵各行所有权归属与理由（研究证据）不变。**Business/Runtime/Checkpoint 三类存储物理划分仍由 DQ-13（PROPOSED/PENDING）拥有，未被 DQ-02 决定。** 矩阵行 5 的 DQ-04 已由用户正式决定（**RFC-002-DQ-04 = ACCEPTED，Accepted with Revision**，2026-08-02）：`domain_version_id` / `version_number` / `revision` 三类明确分离；Domain Version ID 由 Application 层 INSERT 前生成（opaque UUID、不可变）；受保护可变记录使用独立 NOT NULL `revision`，状态修改 Command 携带 `expected_revision`，compare-and-swap 条件更新、零影响行 = 冲突整体回滚；SQLAlchemy `version_id_col` 仅为 Infrastructure 机制；PostgreSQL `xmin` 不作权威业务 revision（Candidate B REJECTED）；SERIALIZABLE 不替代显式 revision（Candidate C REJECTED，仍可作为独立隔离策略讨论）；隔离级别与重试策略仍由 DQ-05/07（PROPOSED/PENDING）拥有；RFC-004 可将 revision 映射 ETag/If-Match（HTTP 协议未决）；正式持久化测试使用真实 PostgreSQL（测试策略归 DQ-16）。矩阵行 6 的 DQ-05 已由用户正式决定（**RFC-002-DQ-05 = ACCEPTED，Accepted with Revision**，2026-08-02）：Business Transaction Owner = Application（Entrypoint / Graph Node 不 begin/commit）；Transactional Application Command = 一个短显式事务 + 一个最终提交点；长流程业务操作 = 多个短事务 + 无事务执行阶段；执行模式 Prepare → Execute Outside Transaction → Commit；四项 PROHIBITED（外部调用持有开放事务、Human Review 跨开放事务、Workflow 暂停跨开放事务、SQLAlchemy Session 跨 Workflow 边界）；Commit-time Revision Revalidation 必选（衔接 DQ-04）；DEC-035 六要素单事务保持有效；External Result Before Commit 非 Current Truth；默认 PostgreSQL 隔离级别 = READ COMMITTED（DQ-04 的默认隔离留白由此决定）；更强隔离 / 锁 / 40001 / 40P01 重试 / SELECT FOR UPDATE / 悲观锁 / 重试上限仍由 DQ-07（PROPOSED/PENDING）拥有；SAVEPOINT 仅为有限 Infrastructure 机制；嵌套业务事务禁止；与外部供应商的分布式事务拒绝；UoW Port 形态仍由 DQ-06（PROPOSED/PENDING）拥有。

---

## 0. 权威依据（官方研究结论摘要）

本矩阵的「DEC 已定边界」全部来自已 Accepted 的 DEC-012/013/024/025/029/032/033/035 与 RFC-001（DQ-04~08）。
本矩阵的「官方能力边界」来自四条一手研究（仅官方文档/官方源码，无博客）：

| 研究 | 关键官方边界 |
|---|---|
| **SQLAlchemy 2.x** | Session=UoW+identity map，生命周期须外置、事务要短、非并发（Session per thread）；`version_id_col` 原生乐观并发（仅 flush 单行生效）；`begin_nested`=SAVEPOINT 但 commit 总作用最外层；事务存续期独占 checkout 连接（池上限=pool_size+max_overflow，默认 5+10）；sync/async 两条独立 stack；commit 后 expire / close 后 detach；`with_for_update()` 渲染 FOR UPDATE 系列；ID 支持 client-side callable 与 server-side `server_default`/`Identity` |
| **LangGraph Checkpointer** | 生产推荐 PostgresSaver（SqliteSaver 不上生产、InMemory 仅测试）；4 张专用表 + setup()、无扩展依赖；checkpoint_id 单调（uuid6）可排序；interrupt 节点 resume **从头重执行**、interrupt 前副作用须幂等；**默认宽松反序列化有 RCE 风险，须 `LANGGRAPH_STRICT_MSGPACK=true`**；**Secret 会被明文序列化进 checkpoint**；Checkpointer=per-thread vs Store=cross-thread 两个不同原语；当前钉版 `prune` 不可用、无内建 TTL（官方建议应用层 cron 清理）；durability=sync/async/exit 默认 async、exit 仅退出时落库；**OSS 框架无同一 thread_id 并发 resume 的锁/乐观并发/CAS**（multitask 策略属 LangSmith Deployment） |
| **PostgreSQL / SQLite / Alembic** | PG：ACID + SAVEPOINT、MVCC、**无内建行 version 列**（乐观锁需应用层 version 列或引擎隔离级 40001 重试）、FOR UPDATE 悲观锁、jsonb+GIN、约束完备、TOAST 大文本/bytea/Large Object、快速加列 + `CREATE INDEX CONCURRENTLY` + `NOT VALID`+`VALIDATE` 两段式、DDL 事务性（除 CONCURRENTLY）。SQLite：ACID、**全库单写者**（WAL 下读者不阻塞写者）、多进程同机可读但任意时刻一写、网络文件锁不可靠、JSON=TEXT（无 GIN）。Alembic：autogenerate 必须人工 review（改名误判 add/drop）、forward-only 是项目策略非强制、batch mode（SQLite move-copy）、offline SQL、跨方言迁移脚本不可直接复用 |
| **模式定义** | Transactional Outbox（同库事务写 outbox + 独立 relay，at-least-once → 消费端必幂等）；relay=Polling（可移植）vs Log Tailing（低延迟、库特定、Debezium）；Idempotent Consumer/Receiver（dedup 表 + 主键判重、去重须与业务同事务）；Guaranteed Delivery（store-and-forward=Durable Dispatch 概念根源）；Fowler 四类事件（Notification/State Transfer/ES/CQRS 不可混淆）；Audit Log（append-only、问责、简单）≠ Domain Event（通知、触发）；完整 Event Sourcing 已 DEC-013 排除；Saga=长事务拆短本地事务+补偿 |

---

## 1. 边界矩阵（Topic → RFC-002 归属 → 后续 RFC 依赖 → 移交）

> **列含义：** `RFC-002 OWNS` = 本 RFC 必须给出 Decision；`INTERFACE` = 本 RFC 定义契约、后续 RFC 必须消费但不可改其语义；`DEFERRED` = 本 RFC 不决定、移交指定 RFC；`OUT OF SCOPE` = 本 RFC 明确不涉及。

| # | Topic | RFC-002 归属 | 依赖/移交 | 理由（官方/DEC 依据） |
|---|---|---|---|---|
| 1 | **主持久化技术（Business DB 引擎）** | **RFC-002 OWNS**（DQ-01 **ACCEPTED 2026-08-01**） | INTERFACE → RFC-003（Checkpointer 需同实例评估）、RFC-005（检索索引落点） | 业务库选型属持久化决策；SQLite 全库单写者 vs PG 行级 MVCC 是 DQ-01 权衡输入 |
| 2 | **ORM 与数据访问** | **RFC-002 OWNS**（DQ-01 **ACCEPTED 2026-08-01**） | INTERFACE → 全部 | SQLAlchemy sync-first 契合 RFC-001 DQ-07；detached/expire 行为是 Repository 不泄漏 ORM 实体的技术根因 |
| 3 | **持久化所有权 / 模块边界** | **RFC-002 OWNS**（DQ-02 **ACCEPTED 2026-08-01**） | INTERFACE → RFC-003/004/005（各模块表边界） | DEC-034 逻辑分离恒定；Shared Instance ≠ Shared Ownership |
| 4 | **Aggregate 与持久化边界** | **RFC-002 OWNS**（DQ-03 **ACCEPTED 2026-08-02**） | INTERFACE → 全部模块 | Atomic Business Commit 六要素单事务（DEC-035，提交协议） |
| 5 | **Domain State Versioning** | **RFC-002 OWNS**（DQ-04 **ACCEPTED 2026-08-02**） | INTERFACE → RFC-003（对账需读版本）、RFC-004（审核版本；revision → ETag/If-Match 映射可能，HTTP 协议未决） | DEC-024 六类版本指针 + DEC-029 并发版本未选型；三类分离 + `expected_revision` 协议已为用户决定；`xmin`/SERIALIZABLE 替代方案被拒绝 |
| 6 | **Transaction Boundary（Use Case↔事务）** | **RFC-002 OWNS**（DQ-05 **ACCEPTED 2026-08-02**） | INTERFACE → RFC-003（节点边界 / Resume 新事务）、RFC-007（超时/重试参数；锁与重试策略归 DQ-07） | 架构基线 §14.3 业务事务由 Use Case 拥有、§14.12 长流程多短事务；外部调用不入事务由连接 checkout 机制推断并已由用户正式决定为 PROHIBITED；默认 READ COMMITTED；SAVEPOINT 仅基础设施机制；嵌套/分布式事务拒绝；UoW Port 形态归 DQ-06、强隔离/锁/重试归 DQ-07 |
| 7 | **Unit of Work Model** | **RFC-002 OWNS**（DQ-06） | INTERFACE → 全部 | SQLAlchemy Session=UoW；生命周期外置 + per-use-case 边界（架构推断） |
| 8 | **Concurrency Control** | **RFC-002 OWNS**（DQ-07） | INTERFACE → RFC-003（重复 resume）、RFC-004（并发编辑） | DEC-022/029 乐观锁未选型；SQLAlchemy version_id_col 是一等能力；Spike R-1 GAP |
| 9 | **Idempotency Model** | **RFC-002 OWNS**（DQ-08） | INTERFACE → RFC-003（resume 幂等）、RFC-004（submit 幂等） | DEC-033 幂等键/Input Fingerprint；Idempotent Consumer 权威；at-least-once→消费端幂等 |
| 10 | **Transactional Outbox / Durable Dispatch** | **RFC-002 OWNS**（DQ-09：是否首版引入 + 落库形态） | INTERFACE → RFC-003（dispatch backend 具体实现）、RFC-007（relay 观测） | RFC-001 DQ-07 已立 Durable Dispatch Boundary，候选明确移交 RFC-002/003；Outbox 双写问题权威 |
| 11 | **Event & Audit Persistence** | **RFC-002 OWNS**（DQ-10） | INTERFACE → RFC-007（观测事件流） | Audit Log≠Domain Event（Fowler）；审计走同事务原子写、事件走提交后通知；不吸收 RFC-007 观测范围 |
| 12 | **Snapshot vs History** | **RFC-002 OWNS**（DQ-11） | INTERFACE → RFC-003（恢复证据）、RFC-007（回放观测） | DEC-013 完整 ES 不属 MVP；current truth + 版本化历史 + append-only 审计 |
| 13 | **Source & Evidence Persistence** | **RFC-002 OWNS**（DQ-12：落库形态） | INTERFACE → RFC-005（检索索引/embedding/chunking） | DEC-025 Source/Evidence 独立语义；大内容走 TOAST/bytea/外部存储；**不决定检索实现** |
| 14 | **Workflow Checkpoint Separation** | **RFC-002 OWNS**（DQ-13：同库/分库、生命周期、对账权威） | INTERFACE → RFC-003（Checkpointer 生产选型、durability、serde） | DEC-023/024 Checkpoint 仅恢复、≠Current Truth；官方生产推荐 PostgresSaver；**不决定生产 Checkpointer 具体实现**（RFC-003） |
| 15 | **Schema Evolution & Migrations** | **RFC-002 OWNS**（DQ-14） | INTERFACE → 全部 | Alembic forward-only/autogenerate 纪律/batch/expand-contract；**不创建真实迁移** |
| 16 | **Data Retention & Deletion Boundary** | **RFC-002 OWNS**（DQ-15） | INTERFACE → RFC-003（checkpoint 保留）、RFC-007（日志保留） | DEC-013/025 保留周期未确认；checkpoint 官方无内建 TTL、应用层 cron；**不虚构保留周期** |
| 17 | **Persistence Testing Strategy** | **RFC-002 OWNS**（DQ-16） | INTERFACE → 全部（测试基建） | 真实 DB vs SQLite fake、contract/transaction/concurrency/migration/idempotency 测试 |
| 18 | **Security & Sensitive Data Boundary** | **RFC-002 OWNS**（DQ-17） | INTERFACE → RFC-006（LLM Secret）、RFC-007（日志 redaction） | DEC-033 Sensitive Data Boundary；Secret 明文序列化进 checkpoint 风险；**不实现 Secret 管理** |

---

## 2. RFC-002 必须**不**决定的后续 RFC 主题（显式 DEFERRED / OUT OF SCOPE）

下列主题**不是** RFC-002 的决策范围。RFC-002 仅为它们提供**持久化契约/落库形态**，绝不替它们做实现或选型决定：

| 主题 | 归属 RFC | RFC-002 的正确姿态 |
|---|---|---|
| LangGraph 生产 Checkpointer **具体实现**（PostgresSaver 配置、durability 模式、serde 加密、interrupt 节点结构） | **RFC-003** | RFC-002 只定「Checkpoint 与业务库的物理/逻辑边界 + 对账权威」；durability/serde/节点结构移交 |
| LangGraph 节点结构 / Graph 拓扑 / Node 拆分 | **RFC-003** | 完全不涉及；仅引用 DEC-035 已定的分节点契约 |
| 生产 dispatch backend（具体 Queue/Broker/Redis/Job Table 实现） | **RFC-003** | RFC-002 只定「是否引入 Outbox + Durable Work Intent 落库形态」；backend 移交 |
| API endpoints / HTTP schema / Human Review 提交协议 / 权限 | **RFC-004** | RFC-002 只定「Review 相关持久化实体 + 并发控制 + 幂等键」；HTTP 层移交 |
| Retrieval chunking / 向量库 / embedding 模型 / 检索索引实现 / 证据装配 | **RFC-005** | RFC-002 只定「Source/Fragment/Evidence 的持久化形态 + 索引落点边界」；检索实现移交 |
| LLM Provider / Prompt runtime / 结构化输出 / 模型 Secret 注入 | **RFC-006** | RFC-002 只定「LLM 执行记录的持久化形态 + Secret 不落 Graph State/checkpoint」；LLM 实现移交 |
| Logging vendor / Metrics backend / Tracing / OpenTelemetry / Retry-Timeout-Backoff-CircuitBreaker 生产参数 | **RFC-007** | RFC-002 只定「审计/事件/运行记录的持久化形态」；观测栈移交 |
| Deployment topology / 容器 / 托管平台 | **超出全部 RFC（后续）** | 不涉及 |

---

## 3. 关键「边界即事实」校正（避免越权或误述）

1. **「Business Database = Current Truth / Checkpointer = Recovery」非字面等号短语。** 权威原文为 architecture-baseline-v1 §2「三类存储分离：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）物理分离；**Checkpoint ≠ Current Truth**」与 DEC-023「LangGraph Checkpointer **仅**承载执行恢复、图状态快照、Interrupt 和 Resume」。RFC-002 一律引用真实原文。
2. **Checkpoint 分离是项目契约（DEC-024/033），非 LangGraph 官方强制。** 官方对「Checkpointer 与业务库同库/分库」**无建议**——这是 RFC-002/DQ-13 的真实决策空间，不得假装是官方约束。
3. **「不得跨外部调用持有 DB 事务」原为架构推断（Recommendation），官方事实仅「事务存续期独占 checkout 连接、池有上限、超时报错」，官方未以「建议」形式写明。此条已由 **DQ-05 Accepted Decision（2026-08-02）** 正式决定为 PROHIBITED（项目用户决定；官方仍未明令）。
4. **Traceability matrix 用 legacy 字母码：** RFC-B≈RFC-002、RFC-C≈RFC-003、RFC-D≈RFC-004、RFC-E≈RFC-005、RFC-F≈RFC-006、RFC-G≈RFC-007、RFC-A≈RFC-001。RFC-002 正文引用时须用正式编号并注明映射。
5. **durability / pending-writes / 同一 thread_id 并发防护属 RFC-003**（它们依赖生产 Checkpointer 选型与 Graph 结构）；RFC-002 只提供「Checkpoint 不存业务真值、可视为可回收执行副产物」的落库边界，**不**替 RFC-003 选 durability 模式或并发防护机制。
6. **Outbox relay（Polling vs Log Tailing/Debezium）与 dispatch backend 属 RFC-003**；RFC-002/DQ-09 只决定「是否首版引入 Transactional Outbox + Durable Work Intent 的落库形态」，relay 实现移交。

---

## 4. 非决策清单（Explicit Non-Decisions of RFC-002）

RFC-002 **显式不**为以下各项做决定（全部移交或排除）：

- LangGraph 生产 Checkpointer 具体实现与 durability/serde 配置 → **RFC-003**
- dispatch backend / Queue / Broker 实现与 relay → **RFC-003**
- API endpoint / HTTP contract / Human Review 提交协议 → **RFC-004**
- Retrieval 实现（chunking/vector/embedding/index）→ **RFC-005**
- LLM provider / prompt / 结构化输出 → **RFC-006**
- 观测栈（logging/metrics/tracing/retry 参数）→ **RFC-007**
- 完整 Event Sourcing → **已由 DEC-013 排除（非 RFC-002 重开）**
- 生产部署拓扑 / 容器 / 托管平台 → **后续（超出 RFC-001~007 当前阶段）**
- Secret 管理实现 / 加密密钥管理 → **RFC-002 仅定边界，不实现（DQ-17）**
- 真实 Alembic 迁移脚本 / DB schema DDL → **RFC-002 不创建真实迁移（DQ-14）**

---

> **结论：** RFC-002 的决策权严格限定在「持久化与事务架构」17 个 DQ；所有依赖生产运行时形态（Checkpointer/Queue/API/检索/LLM/观测）的决定全部显式移交，符合 DEC-038 与 RFC-001 的 Acceptance≠Authorization 纪律。
