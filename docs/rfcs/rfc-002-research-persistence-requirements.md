# RFC-002 Supporting Research：持久化需求矩阵（Persistence Requirements Matrix）

> **Status:** SUPPORTING EVIDENCE（研究工件，非 Accepted Decision）
> **服务 RFC：** RFC-002 — Persistence and Transaction Architecture
> **来源层：** 全部提取自已 Accepted 的 DEC（DEC-012/013/014/022/023/024/025/029/032/033/034/035）、RFC-001（ACCEPTED）、Architecture Baseline v1、Current Specs、Spike-001 证据。
> **纪律：** 本文件**只**汇总与分类**已接受的**持久化/事务需求与**已明确留白**的开放点；**不**替用户做任何技术选型。凡属 RFC-002 待决项，一律标注 `→ RFC-002-DQ-xx（PENDING）`。
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
**待决（→ RFC-002-DQ-07 并发）：** 多标签页/客户端并发编辑「不得静默覆盖较新 Draft」的并发控制实现（dec-029:627-638「Optimistic Lock / Revision Number / ETag / Database Lock 尚未确认」）。

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

**待决（→ RFC-002-DQ-07/DQ-08/DQ-09）：** 乐观并发/CAS/数据库约束/应用锁/task-level 序列化的取舍；Command ID/Idempotency Key/Attempt ID/Run ID/Review Decision ID/Dispatch ID 的唯一性约束；是否首版引入 Transactional Outbox。
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
| 1 | 生产数据库 / ORM / Migration / Schema Strategy | baseline §14.11/§16.6/§20；data-arch DEC-024「仍待确认」 | DQ-01/DQ-14 |
| 2 | Repository / Unit of Work / Database Session 实现形态 | baseline §10.8（列为 RFC-002 禁建项） | DQ-02/DQ-06 |
| 3 | Aggregate 与持久化边界（哪些更新原子提交） | RFC-001 DQ-04 Atomic Business Commit；DEC-024 | DQ-03 |
| 4 | Domain state versioning 与 optimistic concurrency version 语义 | dec-024（6 类版本已固定概念）；dec-029:634-638（并发版本未选型） | DQ-04/DQ-07 |
| 5 | Transaction boundary（Use Case↔事务、外部调用不入事务、Review 暂停结束事务、Worker retry 新事务） | baseline §14.3/§12.4；DEC-033 | DQ-05 |
| 6 | Unit of Work model（显式 UoW、接口位置、Commit/Rollback 负责方、嵌套事务禁止） | baseline §14.4 UoW Port 由 Application 定义 | DQ-06 |
| 7 | Concurrency control（optimistic/pessimistic/CAS/约束/应用锁/task 序列化；覆盖 duplicate resume/concurrent approval/stale worker/repeated command/simultaneous invalidation） | dec-022/dec-029；readiness R-1 | DQ-07 |
| 8 | Idempotency model（Command ID/Idempotency Key/Attempt ID/Stage Run ID/Review Decision ID/Dispatch ID 及四层幂等语义） | dec-033:456/460 | DQ-08 |
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
