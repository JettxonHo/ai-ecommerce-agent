# RFC-002 Decision Questions：持久化与事务架构决策问题集（PROPOSED）

> **Status:** PROPOSED（全部 DQ 均为提案，**无一 Accepted**）
> **服务 RFC：** RFC-002 — Persistence and Transaction Architecture
> **治理：** DEC-036（Controlled Git/GitHub Execution）· DEC-038（RFC and Issue Governance）
> **证据底座：** `rfc-002-research-persistence-requirements.md`（需求矩阵）· `rfc-002-analysis-cross-rfc-boundary.md`（边界矩阵）· 四条一手官方研究（SQLAlchemy / LangGraph Checkpointer / PostgreSQL-SQLite-Alembic / 模式定义）
> **纪律（恒定成立）：**
> - 每个 DQ 的 `User Decision = PENDING`，`Status = PROPOSED`；**只有用户**能把 DQ 标记为 ACCEPTED。
> - `Recommendation` 是**架构建议**，**绝不**写成 Accepted Decision；采纳与否由用户在 Decision Gate 决定。
> - 每条区分：**[DEC 约束]**（已 Accepted 的项目决定，RFC 不得推翻）/ **[官方能力]**（官方文档/源码明确能力）/ **[架构推断]**（由官方事实推导的建议）/ **[未决假设]**。
> - 真正的架构分歧**写入 DQ**，不替用户私下决定。

---

## DQ 总览

| DQ | 主题 | 核心分歧 | 主要证据 |
|---|---|---|---|
| DQ-01 | 主持久化技术（Business DB 引擎） | PostgreSQL vs SQLite vs MVP-SQLite→PG | PG/SQLite 官方并发与部署边界 |
| DQ-02 | 持久化所有权 / 模块边界 | 逻辑 schema 分离粒度 | DEC-034 逻辑分离恒定 |
| DQ-03 | Aggregate 与持久化边界 | 原子提交单元如何划分 | DEC-035 六要素单事务 |
| DQ-04 | Domain State Versioning | 并发版本由谁产生、隔离级别 | SQLAlchemy version_id_col 边界 |
| DQ-05 | Transaction Boundary | Use Case↔事务对齐、外部调用不入事务 | 连接 checkout 机制（推断） |
| DQ-06 | Unit of Work Model | 显式 UoW Port 形态、嵌套事务 | SQLAlchemy Session=UoW |
| DQ-07 | Concurrency Control | 乐观/悲观/CAS/约束/应用锁取舍 | DEC-022/029 未选型；R-1 GAP |
| DQ-08 | Idempotency Model | 四层幂等是否统一存储 | Idempotent Consumer 权威 |
| DQ-09 | Transactional Outbox / Durable Dispatch | 是否首版引入 Outbox | 双写问题权威；RFC-001 移交 |
| DQ-10 | Event & Audit Persistence | 审计 vs 事件分离与持久化 | Fowler Audit Log≠Domain Event |
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
- **Impact on later RFCs：** RFC-003（Checkpointer 是否同实例）、RFC-005（检索索引落点）、RFC-014（迁移策略）。
- **Recommendation：** **[架构推断] 倾向 A（PostgreSQL 为目标生产引擎），本地开发可用 SQLite 但须以 PG 语义为准**——依据：API+Worker 两进程并发写、托管部署、DEC-024 多指针/约束/版本化的关系完整性需求，均指向行级 MVCC。**置信度：中-高**（取决于 MVP 部署形态）。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——以模块分逻辑边界（命名/schema），用架构测试强制「不得跨模块直读表」。**置信度：高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——聚合边界服务于六要素原子提交。**置信度：高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——应用层 version 列 + ORM 乐观校验，ID/版本由 Application 产生（契合显式传值优先 + INSERT 前可知 + 幂等键）。**置信度：中-高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——Use Case 拥有唯一提交点、外部调用不持有 DB 事务、长流程拆多个短事务；SAVEPOINT 仅留少数确需部分回滚场景。**置信度：中-高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A 显式 UoW、禁止嵌套业务事务**（SAVEPOINT 仅基础设施级部分回滚）。**置信度：高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 分层组合**——以 **DB 唯一约束兜底幂等** + **乐观 version 列做 Current Truth 更新** + **task 领取用悲观/SKIP LOCKED** + **同 task 应用层序列化**。**置信度：中**（并发场景需真实 DB 验证，见 DQ-16）。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A 为主 + C 为辅**——统一带唯一约束的幂等表（含 input fingerprint + 首次结果），操作尽量设计为设值语义。**置信度：中-高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 B（DB Job Table 形态的 Durable Work Intent，逻辑等价最简 Outbox）首版引入**，与业务写入同事务；relay/具体 backend 移交 RFC-003。**置信度：中**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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
- **Recommendation：** **[架构推断] 倾向 A**——审计 append-only 同事务原子写、Application Event 提交后通知（不持久化为 Current Truth）。**置信度：高**。
- **User Decision：** PENDING
- **Status：** PROPOSED

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

## 汇总：待用户逐项决定

```text
RFC-002-DQ-01  Primary Persistence Technology        = PROPOSED — User Decision: PENDING
RFC-002-DQ-02  Persistence Ownership / Boundaries    = PROPOSED — User Decision: PENDING
RFC-002-DQ-03  Aggregate / Persistence Boundary      = PROPOSED — User Decision: PENDING
RFC-002-DQ-04  Domain State Versioning               = PROPOSED — User Decision: PENDING
RFC-002-DQ-05  Transaction Boundary                  = PROPOSED — User Decision: PENDING
RFC-002-DQ-06  Unit of Work Model                    = PROPOSED — User Decision: PENDING
RFC-002-DQ-07  Concurrency Control                   = PROPOSED — User Decision: PENDING
RFC-002-DQ-08  Idempotency Model                     = PROPOSED — User Decision: PENDING
RFC-002-DQ-09  Transactional Outbox / Dispatch       = PROPOSED — User Decision: PENDING
RFC-002-DQ-10  Event & Audit Persistence             = PROPOSED — User Decision: PENDING
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
