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
| Decision Questions | **DQ-01 = ACCEPTED**（2026-08-01 用户正式决定，Accepted with Revision）；DQ-02 ~ DQ-17 = **PROPOSED** |
| Recommendation | **PROPOSED**（非 Accepted；DQ-01 的历史 Recommendation 已被其 Accepted Decision 取代） |
| User Decisions | **DQ-01 = ACCEPTED WITH REVISION**；DQ-02 ~ DQ-17 = **PENDING** |
| Implementation | **NOT AUTHORIZED** |
| Depends on | RFC-001（ACCEPTED）· DEC-012/013/022/023/024/025/029/032/033/034/035 |
| Blocks | Business Repository / Current Truth；为 RFC-003/004/005/006/007 提供持久化契约 |
| Spike gaps addressed | R-1（并发/分布式未验证）· R-3（生产 Checkpointer 未锁定）· R-4（规模/性能未验证） |
| Branch | `rfc/002-persistence-transaction-architecture` |
| Supporting artifacts | `rfc-002-research-persistence-requirements.md` · `rfc-002-analysis-cross-rfc-boundary.md` · `rfc-002-decision-questions.md` |

---

## 2. Summary（摘要）

本 RFC 定义 AI Ecommerce Agent 的**持久化与事务架构**：生产 Business Current Truth Repository 的技术选型方向、模块持久化所有权、聚合与原子提交边界、领域状态版本化、事务边界、Unit of Work、并发控制、幂等模型、Transactional Outbox / Durable Dispatch 落库形态、事件与审计持久化、快照与历史模型、来源与证据持久化、Workflow Checkpoint 分离、Schema 演进、数据保留、持久化测试策略、安全与敏感数据边界。

它把 DEC-024（三类存储分离、四类状态、四个标识符、六类版本指针）、DEC-029（人工审核持久化与并发）、DEC-033（失败/重试/恢复/幂等）与 RFC-001（Application 拥有事务、Durable Dispatch Boundary、Port 所有权）转化为 **17 个 Decision Question（DQ-01 已于 2026-08-01 由用户正式决定，ACCEPTED；DQ-02~17 仍 PROPOSED、User Decision PENDING）**，每个 DQ 给出候选方案、取舍、失败模式、对后续 RFC 的影响与一份**架构建议（非 Accepted；DQ-01 的建议已被用户正式决定取代）**。

本 RFC **不**实现任何持久化、数据库、ORM、迁移、Repository、UoW、Outbox、Queue、LangGraph、API 或业务代码。

---

## 3. Status（状态）

```text
RFC-002 Status                = IN REVIEW
RFC-002-DQ-01                 = ACCEPTED（2026-08-01 用户正式决定，Candidate A，Accepted with Revision）
RFC-002 Decision Questions    = DQ-01 ACCEPTED；DQ-02~17 PROPOSED
RFC-002 Recommendation        = PROPOSED（非 Accepted；DQ-01 Recommendation Superseded by Accepted Decision）
RFC-002 Pull Request          = OPEN（PR #24）
Required Checks               = PASS（8/8）
User Decisions                = DQ-01 = ACCEPTED WITH REVISION；DQ-02~17 = PENDING（16 项）
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

**DQ-01 已于 2026-08-01 由用户正式决定（ACCEPTED，Accepted with Revision，见 §33 Decision Log）；DQ-02~17 仍 PROPOSED — User Decision: PENDING**。完整 13 字段版本见 [rfc-002-decision-questions.md](rfc-002-decision-questions.md)。

| DQ | 主题 | 归属 | 置信度 |
|---|---|---|---|
| DQ-01 | Primary Persistence Technology | RFC-002 OWNS — **ACCEPTED**（Candidate A，2026-08-01） | 中-高（历史置信度） |
| DQ-02 | Persistence Ownership / Boundaries | RFC-002 OWNS | 高 |
| DQ-03 | Aggregate / Persistence Boundary | RFC-002 OWNS | 高 |
| DQ-04 | Domain State Versioning | RFC-002 OWNS | 中-高 |
| DQ-05 | Transaction Boundary | RFC-002 OWNS | 中-高 |
| DQ-06 | Unit of Work Model | RFC-002 OWNS | 高 |
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

在 RFC-001 的分层骨架内，持久化与事务架构的核心主张（Recommendation；**其中第 1 条已由 DQ-01 Accepted Decision 取代，见 §33**）：

1. **主持久化 = PostgreSQL，Business Current Truth Repository 唯一受支持的权威数据库语义（DQ-01 Accepted Decision，2026-08-01）**：技术栈 = **PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**；**本地开发使用 PostgreSQL**；schema、约束、迁移、事务行为、并发行为与持久化正确性均以 PostgreSQL 语义定义；SQLite **不是**受支持的 backend（SQLite-first → PostgreSQL-later 路线已拒绝）。历史 Recommendation「PG 为目标、本地可用 SQLite 以 PG 语义为准」已被取代（Superseded by Accepted Revision）。（原提案中 SQLAlchemy sync-first 与 Alembic 的方向延续自 RFC-001-DQ-07 Sync-first 约束。）
2. **三类存储逻辑分离恒定**（DEC-034）：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）即使同实例也保持独立 schema/表边界（DQ-02、DQ-13）。
3. **业务事务由 Application Use Case 拥有**，长 Workflow 由多个短事务组成（DQ-05、DQ-06），外部调用不持有 DB 事务（[架构推断]，Recommendation）。
4. **Atomic Business Commit 六要素单事务**（DEC-035）为统一事务模板（DQ-03）。
5. **并发控制分层组合**（DQ-07）：DB 唯一约束兜底幂等 + 应用层 version 列乐观校验 + task 领取悲观/SKIP LOCKED + 同 task 应用层序列化。
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

依据：SQLAlchemy 官方——事务存续期连接被独占 checkout、池上限有限（默认 5+10）、超时即报错 ⇒ **外部调用应在事务边界之外**（[架构推断]，Recommendation，非官方明令）。

---

## 10. Recommended Architecture（推荐架构总表）

| 维度 | Recommendation（PROPOSED）/ Accepted Decision | 关键依据 |
|---|---|---|
| 引擎与语义 | **PostgreSQL 是唯一受支持的权威数据库语义；本地开发与正式持久化测试均使用真实 PostgreSQL；SQLite 不受支持**（**DQ-01 ACCEPTED，2026-08-01**） | DQ-01 Accepted Decision：并发写/托管/约束 |
| 技术栈 | **PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**（**DQ-01 ACCEPTED**） | DQ-01 Accepted Decision |
| ORM | SQLAlchemy 2.x sync-first（受 DQ-01 Accepted Decision 约束） | DQ-01/06：契合 RFC-001-DQ-07 |
| 迁移 | Alembic forward-only + 人工 review autogenerate（Recommendation，PROPOSED） | DQ-14 |
| 模块边界 | 单库按模块分逻辑边界 + 架构测试强制 | DQ-02：DEC-034 |
| 聚合 | 以六要素原子提交为边界 | DQ-03：DEC-035 |
| 版本化 | 应用层 version 列 + ORM 乐观校验 | DQ-04 |
| 事务边界 | Use Case 唯一提交点、外部调用不入事务、长流程拆短事务 | DQ-05 |
| UoW | 显式 UoW、禁止嵌套业务事务 | DQ-06 |
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
| 事务 | Use Case 全程一个事务 | 外部调用拉长事务→连接池耗尽风险 |
| 并发 | 纯引擎隔离级（40001 重试） | 高冲突重试风暴、对批量更新无效 |
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
- **短事务 + 外部调用不入事务**减少连接占用、恢复清晰，但要求 Use Case 显式编排外部调用位置，比「全程一事务」复杂。
- **分层并发控制**覆盖全面，但组合（乐观+悲观+唯一约束+应用锁）比单一机制难推理，需 DQ-16 真实 DB 验证。
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

见 DQ-16。原则：**并发/事务/迁移/幂等使用真实 PostgreSQL**——**DQ-01 Accepted Decision（2026-08-01）：repository contract tests、persistence integration tests、transaction tests、concurrency tests 与 migration tests 必须对真实 PostgreSQL 运行；SQLite 不是受支持的 Business Current Truth backend，也不是 PostgreSQL 持久化语义的权威替代**。单元/契约层是否可用快速 fake 属 DQ-16（PROPOSED，PENDING）。因并发语义不可移植（SQLite 全库单写者 vs PG 行级 MVCC）。覆盖：Atomic Commit 回滚（partial_write==0）、重复 submit/resume 幂等、过期 checkpoint 拒绝、取消无部分写入、并发编辑不静默覆盖、迁移前向兼容。填补 Spike R-1（并发）与 R-4（规模）。

---

## 23. Rollout Plan（推进计划）

1. **本 RFC 审查（当前 Gate）**：用户逐项审查并决定 DQ-01~17——**DQ-01 已于 2026-08-01 由用户正式决定（ACCEPTED，Accepted with Revision）；DQ-02~17 仍 PENDING**。
2. **DQ 接受后**：用户明确接受 RFC-002 整体（Acceptance ≠ Authorization）。
3. **后续**：RFC-002 ACCEPTED 后，按其契约推进 RFC-003（Checkpointer/dispatch 实现），并仍**不**自动授权任何持久化生产实现——实施需用户另行明确授权。

---

## 24. Acceptance Criteria（验收标准）

按 rfcs/README 的四项标准：

- **Decision Completeness**：17 个 DQ 全部提出且含完整 13 字段、候选、取舍、失败模式、对后续 RFC 影响——✅ 本 RFC + DQ 文档满足。
- **Architecture Compatibility**：全部 DQ 与 RFC-001（Application 拥有事务、Port 所有权、Durable Dispatch、Sync-first）及 DEC-024/029/033/034/035 一致、无推翻——✅。
- **Implementation Readiness**：每个 DQ 给出可落地的候选与 Recommendation，实施者可据接受的 DQ 开始——⏳ DQ-01 ACCEPTED（2026-08-01）；DQ-02~17 待用户接受。注：DQ 接受 ≠ 实施授权（Implementation = NOT AUTHORIZED 恒定）。
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
- [ ] DQ-05「外部调用不入事务」Recommendation 是否接受为设计原则？
- [ ] DQ-07 并发控制分层组合是否覆盖五类并发场景？
- [ ] DQ-09 是否首版引入 Durable Work Intent 落库（而非直接 broker）？
- [ ] DQ-11 「不上完整 ES」立场是否确认（与 DEC-013 一致）？
- [ ] DQ-13 Checkpoint 同实例独立 schema + 应用层清理是否可接受？
- [ ] DQ-15 各类数据保留责任划分是否留待合规决定（未虚构周期）？
- [ ] 全部 17 项 User Decision 是否逐项拍板（DQ-01 已决定；DQ-02~17 PENDING）？

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

---

## 33. Decision Log（决定记录）

| 日期 | 决定 | 决定者 | 内容 |
|---|---|---|---|
| 2026-08-01 | **RFC-002-DQ-01 = ACCEPTED（Accepted with Revision）** | 用户 | 接受 Candidate A 并修订：PostgreSQL 是 Business Current Truth Repository 唯一受支持的权威数据库语义；技术栈 = **PostgreSQL + SQLAlchemy 2.x synchronous API + Psycopg 3 synchronous driver + Alembic**；schema/约束/迁移/事务/并发/持久化正确性均以 PostgreSQL 语义定义；**本地开发与正式持久化测试**（repository contract / persistence integration / transaction / concurrency / migration tests）**均对真实 PostgreSQL 运行**；SQLite 不是受支持的 backend，也不是 PostgreSQL 持久化语义的权威替代；SQLite-first → PostgreSQL-later 路线 **REJECTED**；错误引用「RFC-014（迁移策略）」修正为 **RFC-002-DQ-14（Schema Evolution and Migrations）**。原历史 Recommendation「PG 为目标、本地可用 SQLite 以 PG 语义为准」标记为 **Superseded by Accepted Revision**；不建立 SQLite 方言兼容承诺。 |

### Open User Decisions（待用户决定）

```text
RFC-002-DQ-02 ~ DQ-17 = PROPOSED — User Decision: PENDING（16 项）
RFC-002 Acceptance    = USER DECISION REQUIRED
RFC-002 Merge         = USER DECISION REQUIRED
Implementation        = NOT AUTHORIZED（DQ-01 接受不授权任何实施）
```

---

## Outcome（结果）

```text
RFC-002 Status                = IN REVIEW
RFC-002-DQ-01                 = ACCEPTED（2026-08-01 用户正式决定，Candidate A，Accepted with Revision）
RFC-002 Decision Questions    = DQ-01 ACCEPTED；DQ-02~17 PROPOSED
RFC-002 Recommendation        = PROPOSED（DQ-01 Recommendation Superseded by Accepted Decision）
RFC-002 Pull Request          = OPEN（PR #24）
Required Checks               = PASS（8/8）
User Decisions                = DQ-01 = ACCEPTED WITH REVISION；DQ-02~17 = PENDING（16 项）
Implementation                = NOT AUTHORIZED

Immediate Next Gate = 用户审查并决定 RFC-002-DQ-02 Persistence Ownership and Module Boundaries
```

**Coding Agent 不自行接受任何 DQ、不接受 RFC-002、不 Merge PR、不开始任何持久化/数据库/业务/生产运行时实现。**
