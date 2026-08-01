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
| Decision Questions | **DQ-01 = ACCEPTED**・**DQ-02 = ACCEPTED**（均 2026-08-01）・**DQ-03 = ACCEPTED**・**DQ-04 = ACCEPTED**・**DQ-05 = ACCEPTED**・**DQ-06 = ACCEPTED**（DQ-03/04/05/06 均 2026-08-02；均用户正式决定，Accepted with Revision）；DQ-07 ~ DQ-17 = **PROPOSED** |
| Recommendation | **PROPOSED**（非 Accepted；DQ-01/02/03/04/05/06 的历史 Recommendation 已被各自 Accepted Decision 取代） |
| User Decisions | **DQ-01 = ACCEPTED WITH REVISION**；**DQ-02 = ACCEPTED WITH REVISION**；**DQ-03 = ACCEPTED WITH REVISION**；**DQ-04 = ACCEPTED WITH REVISION**；**DQ-05 = ACCEPTED WITH REVISION**；**DQ-06 = ACCEPTED WITH REVISION**；DQ-07 ~ DQ-17 = **PENDING**（11 项） |
| Implementation | **NOT AUTHORIZED** |
| Depends on | RFC-001（ACCEPTED）· DEC-012/013/022/023/024/025/029/032/033/034/035 |
| Blocks | Business Repository / Current Truth；为 RFC-003/004/005/006/007 提供持久化契约 |
| Spike gaps addressed | R-1（并发/分布式未验证）· R-3（生产 Checkpointer 未锁定）· R-4（规模/性能未验证） |
| Branch | `rfc/002-persistence-transaction-architecture` |
| Supporting artifacts | `rfc-002-research-persistence-requirements.md` · `rfc-002-analysis-cross-rfc-boundary.md` · `rfc-002-decision-questions.md` |

---

## 2. Summary（摘要）

本 RFC 定义 AI Ecommerce Agent 的**持久化与事务架构**：生产 Business Current Truth Repository 的技术选型方向、模块持久化所有权、聚合与原子提交边界、领域状态版本化、事务边界、Unit of Work、并发控制、幂等模型、Transactional Outbox / Durable Dispatch 落库形态、事件与审计持久化、快照与历史模型、来源与证据持久化、Workflow Checkpoint 分离、Schema 演进、数据保留、持久化测试策略、安全与敏感数据边界。

它把 DEC-024（三类存储分离、四类状态、四个标识符、六类版本指针）、DEC-029（人工审核持久化与并发）、DEC-033（失败/重试/恢复/幂等）与 RFC-001（Application 拥有事务、Durable Dispatch Boundary、Port 所有权）转化为 **17 个 Decision Question（DQ-01/02 已于 2026-08-01、DQ-03/04/05/06 已于 2026-08-02 由用户正式决定，ACCEPTED；DQ-07~17 仍 PROPOSED、User Decision PENDING）**，每个 DQ 给出候选方案、取舍、失败模式、对后续 RFC 的影响与一份**架构建议（非 Accepted；DQ-01/02/03/04/05/06 的建议已被用户正式决定取代）**。

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
RFC-002 Decision Questions    = DQ-01~06 ACCEPTED；DQ-07~17 PROPOSED
RFC-002 Recommendation        = PROPOSED（非 Accepted；DQ-01/02/03/04/05/06 Recommendation Superseded by Accepted Decision）
RFC-002 Pull Request          = OPEN（PR #24）
Required Checks               = PASS（8/8）
User Decisions                = DQ-01~06 = ACCEPTED WITH REVISION；DQ-07~17 = PENDING（11 项）
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

### 4.3 事实校正（重要）

全仓库**无**字面等号短语「Business Database = Current Truth」「Checkpointer = Recovery」。**权威原文**为 architecture-baseline-v1 §2：「三类存储分离：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）物理分离；**Checkpoint ≠ Current Truth**」，及 DEC-023「LangGraph Checkpointer **仅**承载执行恢复、图状态快照、Interrupt 和 Resume」。本 RFC 一律引用真实原文，不用转述等号形式。

### 4.4 Spike 证据与缺口

Spike-001 以三个物理 SQLite 文件（`business/runtime/checkpoints.sqlite`）验证了关键运行时安全（25/25 测试）：spike-04 中提交回滚（partial_write_count==0）、spike-06 重复 review submit 拒绝、spike-08 过期 checkpoint 拒绝、spike-10 取消无部分写入。但留下缺口：**R-1（并发/分布式未验证——单线程同步）、R-3（生产 Checkpointer 未锁定）、R-4（规模/性能未验证）**。这些缺口是 DQ-01/07/13/16 的直接动机。

---

## 5. Problem（问题）

在 RFC-001 确立「Application 拥有事务、Port 由 Application 定义、Infrastructure 实现、Durable Dispatch Boundary」之后，项目仍缺少一份**生产可用的持久化与事务架构**，具体表现为：

1. **主持久化技术未选型**——业务 Current Truth 用 PostgreSQL 还是 SQLite 未定；SQLite 全库单写者能否支撑 API+Worker 两进程并发写未知。（**DQ-01 已于 2026-08-01 由用户正式决定：PostgreSQL 是唯一受支持的权威数据库语义，此问题已解决，见 §33 Decision Log。**）
2. **并发控制未定型**——DEC-029「Optimistic Lock/Revision Number/ETag/Database Lock 尚未确认」；Spike 单线程未验证并发（R-1）。
3. **幂等模型未落地**——DEC-033 要求多层幂等，但存储形态、键体系、判重与业务更新的事务关系未定。
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

**DQ-01/02 已于 2026-08-01、DQ-03/04/05/06 已于 2026-08-02 由用户正式决定（均 ACCEPTED，Accepted with Revision，见 §33 Decision Log）；DQ-07~17 仍 PROPOSED — User Decision: PENDING**。完整 13 字段版本见 [rfc-002-decision-questions.md](rfc-002-decision-questions.md)。

| DQ | 主题 | 归属 | 置信度 |
|---|---|---|---|
| DQ-01 | Primary Persistence Technology | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-01） | 中-高（历史置信度） |
| DQ-02 | Persistence Ownership / Boundaries | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-01） | 高（历史置信度） |
| DQ-03 | Aggregate / Persistence Boundary | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 高（历史置信度） |
| DQ-04 | Domain State Versioning | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 中-高（历史置信度） |
| DQ-05 | Transaction Boundary | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 中-高（历史置信度） |
| DQ-06 | Unit of Work Model | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-02） | 高（历史置信度） |
| DQ-07 | Concurrency Control | RFC-002 OWNS | 中 |
| DQ-08 | Idempotency Model | RFC-002 OWNS | 中-高 |
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

在 RFC-001 的分层骨架内，持久化与事务架构的核心主张（Recommendation；**其中第 1、2 条已分别由 DQ-01、DQ-02 Accepted Decision 取代，第 3 条的事务边界与执行模式已由 DQ-05 Accepted Decision（2026-08-02）取代、其 Unit of Work Port 形态已由 DQ-06 Accepted Decision（2026-08-02）正式决定，第 4 条的聚合边界解释已由 DQ-03 Accepted Decision 修订、版本语义与提交协议已由 DQ-04 Accepted Decision（2026-08-02）补充正式决定，第 5 条的并发版本底座已由 DQ-04 Accepted Decision 取代，见 §33**）：

1. **主持久化 = PostgreSQL，Business Current Truth Repository 唯一受支持的权威数据库语义（DQ-01 Accepted Decision，2026-08-01）**：技术栈 = **PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**；**本地开发使用 PostgreSQL**；schema、约束、迁移、事务行为、并发行为与持久化正确性均以 PostgreSQL 语义定义；SQLite **不是**受支持的 backend（SQLite-first → PostgreSQL-later 路线已拒绝）。历史 Recommendation「PG 为目标、本地可用 SQLite 以 PG 语义为准」已被取代（Superseded by Accepted Revision）。（原提案中 SQLAlchemy sync-first 与 Alembic 的方向延续自 RFC-001-DQ-07 Sync-first 约束。）
2. **持久化所有权与模块边界（DQ-02 Accepted Decision，2026-08-01）**：MVP **单一 PostgreSQL 数据库服务**；**每张业务表有且仅有一个所有模块**；所有模块独占拥有其 Repository Port 定义、Infrastructure Repository 实现、ORM / Persistence Models、schema 与 migration 变更、状态修改 Application Use Cases；跨模块读取经目标模块 **Public Application Query**、跨模块状态修改经所有模块 **Public Application Use Case**；**Direct SQL / ORM / Repository 跨模块访问禁止**，边界由 Import Linter + AST/Architecture Tests + Repository Ownership Tests + Migration Ownership Conventions + PR 审查规则强制（单独代码审查不充分）。**每模块独立 PostgreSQL schema 暂缓**（MVP 不要求；具体物理命名留待实现设计，不得削弱所有权）。历史 Recommendation「单库 + 按模块分 schema/表前缀」中的独立 schema 部分未被采纳（Superseded by Accepted Revision）。**三类存储逻辑分离恒定**（DEC-034）：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）的逻辑职责分离不受影响；**其物理划分（同实例/独立 schema/Checkpoint 数据库产品/Runtime 物理存储/Checkpoint 生命周期）不由 DQ-02 决定，继续由 DQ-13 决定（PROPOSED / PENDING）**。
3. **业务事务由 Application Use Case 拥有，事务边界与执行模式由 DQ-05 Accepted Decision（2026-08-02）正式决定**：Business Transaction Owner = Application（Entrypoint / Graph Node 不 begin/commit）；Transactional Application Command = 一个短显式事务 + 一个最终提交点；长流程业务操作 = 多个短事务 + 无事务执行阶段；执行模式 = Prepare → Execute Outside Transaction → Commit；**外部调用不持有开放数据库事务、Human Review 不跨开放事务、Workflow 暂停不跨开放事务、SQLAlchemy Session 不跨 Workflow 边界（四项 PROHIBITED）**；**Commit-time Revision Revalidation 必选**（衔接 DQ-04 `expected_revision` compare-and-swap 协议）；DEC-035 六要素单事务保持有效；**External Result Before Commit 非 Current Truth**；**默认 PostgreSQL 隔离级别 = READ COMMITTED**（更强隔离级别、悲观锁、SELECT FOR UPDATE / SKIP LOCKED、40001 / 40P01 重试与重试上限仍由 DQ-07 决定，PROPOSED / PENDING）；**SAVEPOINT 仅为有限 Infrastructure 机制、嵌套业务事务禁止、与外部供应商的分布式事务拒绝**。历史 Recommendation「Use Case 拥有唯一提交点、外部调用不持有 DB 事务、长流程拆多个短事务（[架构推断]）」已被取代（Superseded by Accepted Revision）。**UoW Port 形态已由 DQ-06 Accepted Decision（2026-08-02）正式决定：UnitOfWork Port 由 Application 定义、Infrastructure 提供 SQLAlchemy 实现（Session 为不暴露的 Infrastructure 细节）；一次性 UoW（NEW→ACTIVE→COMMITTED/ROLLED_BACK→CLOSED）对应一个 Session / 一个短事务 / 一个最终结果；Application Use Case 显式 commit、Context 退出不得自动提交、未 commit 或异常退出 = rollback/close/discard；Repository 无 begin/commit/rollback/close 权限且不暴露 Session、无 Registry/Service Locator；嵌套业务 UoW 禁止（检测必须立即失败）；Composite Application Use Case 拥有唯一外层 UoW 与唯一最终提交点；纯读 Query 使用独立短 Query Scope（见 §33）**。
4. **Atomic Business Commit 六要素单事务**（DEC-035）为统一事务**提交协议**（恒定有效；「以六要素划分聚合边界」的解释已由 **DQ-03 Accepted Decision，2026-08-02** 修订：聚合边界 = 业务不变量 + 唯一模块所有权，六要素不是聚合成员资格判据）。**版本语义与提交协议由 DQ-04 Accepted Decision（2026-08-02）正式决定**：`domain_version_id`（不可变、Application 层 INSERT 前生成、opaque UUID）/ `version_number`（逻辑业务对象内单调递增、唯一性约束）/ `revision`（受保护可变记录的独立 NOT NULL 乐观并发 token）三类分离；产生新顺序版本时，版本分配与 Current Truth revision 校验构成一个安全提交协议（读取 pointer → 校验 `expected_revision` → 分配 `version_number` → 插入不可变 Domain Version → 条件更新 pointer → 递增 `revision` → commit），任何 revision/唯一性冲突或写入失败整体回滚；六要素保持同一事务。
5. **并发控制分层组合**（DQ-07）：DB 唯一约束兜底幂等 + 应用层 version 列乐观校验 + task 领取悲观/SKIP LOCKED + 同 task 应用层序列化。**版本底座已由 DQ-04 Accepted Decision（2026-08-02）正式决定**：受并发保护的 Current Truth Pointer / Aggregate Root / Stage State / Review Package 等可变记录使用独立 NOT NULL `revision`；状态修改 Command 携带 `expected_revision`，compare-and-swap 条件更新，零影响行 = stale write / 并发冲突且 Atomic Business Commit 整体回滚；SQLAlchemy `version_id_col` 仅为 Infrastructure 层机制（`StaleDataError` 等翻译为项目自有冲突语义，mapper/Session 细节不得泄漏进 Domain / Public Contract，bulk UPDATE/DELETE 不得绕过 revision）；PostgreSQL `xmin` 不是权威业务 revision；SERIALIZABLE 不替代显式 revision；**默认隔离级别已由 DQ-05 Accepted Decision（2026-08-02）决定为 READ COMMITTED；更强隔离级别、悲观锁与重试策略仍由 DQ-07 决定（PROPOSED / PENDING）**。
6. **统一幂等表 + 设值语义**（DQ-08），判重与业务更新同事务。
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
| 并发 | 唯一约束兜底 + 乐观 version + SKIP LOCKED 领取 + task 序列化 | DQ-07 |
| 幂等 | 统一幂等表（含 input fingerprint + 首次结果）+ 设值语义 | DQ-08 |
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
| 幂等 | 分层各自存储 | 表分散；统一表 + 唯一约束更可控 |
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
- **分层并发控制**覆盖全面，但组合（乐观+悲观+唯一约束+应用锁）比单一机制难推理，需 DQ-16 真实 DB 验证。**版本底座已由 DQ-04 Accepted Decision（2026-08-02）正式决定**（三类版本语义分离 + `expected_revision` 条件更新 + 冲突整体回滚）；隔离级别与重试策略的取舍仍归 DQ-05/07（PROPOSED / PENDING）。
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
| 同一 thread_id 并发 resume（OSS 无防护） | 重复推进 | DQ-07/13：应用层幂等键/序列化（机制移交 RFC-003） |
| ORM bulk UPDATE/DELETE 绕过 revision 检查 | 静默覆盖受保护记录 | **DQ-04 Accepted Decision（2026-08-02）禁止绕过 revision 的批量修改**；明确需要的批量操作必须定义 expected revision 规则、条件更新与 affected-row 校验 |
| 长事务 + 外部调用持有开放事务 | 高并发下连接池 checkout 耗尽、API/Worker 不可用 | **DQ-05 Accepted Decision（2026-08-02）：外部调用不得持有开放事务；长流程 = 多短事务 + 无事务执行阶段** |
| Human Review / Workflow 暂停跨越开放事务 | 连接长期占用、事务内状态与审核/等待耦合 | **DQ-05 Accepted Decision（2026-08-02）：Human Review 与 Workflow 暂停不得跨开放事务；暂停前状态必须已提交** |
| 跨 Workflow 边界持有 SQLAlchemy Session | detached/expire 状态、恢复语义混乱 | **DQ-05 Accepted Decision（2026-08-02）：Session 不得跨 Workflow 边界；Resume 以新 Session、新事务重新执行** |
| Session 泄漏给 Application / Graph Node / API / Checkpoint | ORM 细节耦合、UoW 边界崩溃、恢复与并发语义混乱 | **DQ-06 Accepted Decision（2026-08-02）：Session 是不暴露的 Infrastructure 实现细节；UoW Port 仅暴露显式类型化 Repository Ports；UoW 不序列化进 Checkpoint、不在 Resume 恢复** |
| 嵌套业务 UoW / 子 Use Case 独立提交 | 「以为已提交实际未提交」的部分提交假象、提交权威分散 | **DQ-06 Accepted Decision（2026-08-02）：嵌套业务 UoW 禁止且检测企图必须立即失败；可复用行为提取为 Domain Service / transaction-neutral Application Service / 接收显式 Ports 的内部操作；Composite Application Use Case 唯一外层 UoW + 唯一最终提交点** |
| 全局 / ambient Session（scoped_session / thread-local / ContextVar） | 事务所有权与依赖注入机制不明、并发与恢复语义腐蚀 | **DQ-06 Accepted Decision（2026-08-02）：全局可变 Session 禁止；ambient 机制不得作为主要事务所有权或依赖注入机制；每个并发 Command / Worker 执行 / Retry / Rerun / Resume 使用独立 UoW 与独立 Session** |

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
5. 同一 thread_id 并发 resume 的应用层防护具体机制（幂等键/分布式锁/队列串行化）——留 RFC-003。

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

见 DQ-16。原则：**并发/事务/迁移/幂等使用真实 PostgreSQL**——**DQ-01 Accepted Decision（2026-08-01）：repository contract tests、persistence integration tests、transaction tests、concurrency tests 与 migration tests 必须对真实 PostgreSQL 运行；SQLite 不是受支持的 Business Current Truth backend，也不是 PostgreSQL 持久化语义的权威替代**。**DQ-04 Accepted Decision（2026-08-02）：持久化语义验证必须使用真实 PostgreSQL，并至少覆盖——两个写者使用相同 `expected_revision`、过期 Human Review 提交、重复 resume 尝试、Domain Version 与 Pointer 的原子更新、防止无保护的批量更新、冲突回滚且零部分业务写入**。单元/契约层是否可用快速 fake 属 DQ-16（PROPOSED，PENDING）。因并发语义不可移植（SQLite 全库单写者 vs PG 行级 MVCC）。覆盖：Atomic Commit 回滚（partial_write==0）、重复 submit/resume 幂等、过期 checkpoint 拒绝、取消无部分写入、并发编辑不静默覆盖、迁移前向兼容。**DQ-05 Accepted Decision（2026-08-02）确立的事务边界语义（外部调用 / Human Review / 暂停不跨开放事务、Session 不跨 Workflow 边界、commit 前方非 Current Truth）亦以真实 PostgreSQL 为验证基准；具体测试分类归 DQ-16**。**DQ-06 Accepted Decision（2026-08-02）确立的 UoW 语义（显式 commit 成功、未 commit 退出回滚、异常退出回滚、flush 失败回滚并丢弃 Session、Repository 无法独立 commit/rollback、嵌套 UoW 被拒绝、Composite 唯一外层 UoW、commit 后不可重用、并发 Commands 独立 Sessions、Prepare/Commit 不同 UoW、Execute Outside Transaction 无 Session/连接、只读 Query Scope 干净关闭、UoW 不跨 Human Review/Interrupt/Retry/Resume）同样以真实 PostgreSQL 为验证基准（覆盖清单见 DQ-06 第 50 点；详细测试组织与 CI 执行归 DQ-16，PROPOSED / PENDING）**。填补 Spike R-1（并发）与 R-4（规模）。

---

## 23. Rollout Plan（推进计划）

1. **本 RFC 审查（当前 Gate）**：用户逐项审查并决定 DQ-01~17——**DQ-01/02/03/04/05/06 已由用户正式决定（DQ-01/02 于 2026-08-01、DQ-03/04/05/06 于 2026-08-02，均 ACCEPTED，Accepted with Revision）；DQ-07~17 仍 PENDING（11 项）**。
2. **DQ 接受后**：用户明确接受 RFC-002 整体（Acceptance ≠ Authorization）。
3. **后续**：RFC-002 ACCEPTED 后，按其契约推进 RFC-003（Checkpointer/dispatch 实现），并仍**不**自动授权任何持久化生产实现——实施需用户另行明确授权。

---

## 24. Acceptance Criteria（验收标准）

按 rfcs/README 的四项标准：

- **Decision Completeness**：17 个 DQ 全部提出且含完整 13 字段、候选、取舍、失败模式、对后续 RFC 影响——✅ 本 RFC + DQ 文档满足。
- **Architecture Compatibility**：全部 DQ 与 RFC-001（Application 拥有事务、Port 所有权、Durable Dispatch、Sync-first）及 DEC-024/029/033/034/035 一致、无推翻——✅。
- **Implementation Readiness**：每个 DQ 给出可落地的候选与 Recommendation，实施者可据接受的 DQ 开始——⏳ DQ-01/02/03/04/05/06 ACCEPTED（2026-08-01/02）；DQ-07~17 待用户接受。注：DQ 接受 ≠ 实施授权（Implementation = NOT AUTHORIZED 恒定；DQ-03 另要求 Aggregate/Invariant Matrix 在持久化实施前完成；DQ-04 的三类版本语义、`expected_revision` 协议与持久化语义验证清单、DQ-05 的事务边界与执行模式决定、DQ-06 的 Unit of Work 模型决定同样不授权实施）。
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
- [ ] DQ-07 并发控制分层组合是否覆盖五类并发场景？
- [ ] DQ-09 是否首版引入 Durable Work Intent 落库（而非直接 broker）？
- [ ] DQ-11 「不上完整 ES」立场是否确认（与 DEC-013 一致）？
- [ ] DQ-13 Checkpoint 同实例独立 schema + 应用层清理是否可接受？
- [ ] DQ-15 各类数据保留责任划分是否留待合规决定（未虚构周期）？
- [ ] 全部 17 项 User Decision 是否逐项拍板（DQ-01~06 已决定；DQ-07~17 PENDING）？

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

### Open User Decisions（待用户决定）

```text
RFC-002-DQ-07 ~ DQ-17 = PROPOSED — User Decision: PENDING（11 项）
RFC-002 Acceptance    = USER DECISION REQUIRED
RFC-002 Merge         = USER DECISION REQUIRED
Implementation        = NOT AUTHORIZED（DQ-01/02/03/04/05/06 接受不授权任何实施）
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
RFC-002 Decision Questions    = DQ-01~06 ACCEPTED；DQ-07~17 PROPOSED
RFC-002 Recommendation        = PROPOSED（DQ-01/02/03/04/05/06 Recommendation Superseded by Accepted Decision）
RFC-002 Pull Request          = OPEN（PR #24）
Required Checks               = PASS（8/8）
User Decisions                = DQ-01~06 = ACCEPTED WITH REVISION；DQ-07~17 = PENDING（11 项）
Implementation                = NOT AUTHORIZED

Immediate Next Gate = 用户审查并决定 RFC-002-DQ-07 Concurrency Control
```

**Coding Agent 不自行接受任何 DQ、不接受 RFC-002、不 Merge PR、不开始任何持久化/数据库/业务/生产运行时实现。**
