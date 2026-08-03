# ARP-02 — Concurrency Scenario Matrix（TS-01 Minimum Slice）

## 0. Artifact Status

```text
Status =
DRAFT — USER REVIEW REQUIRED

Wave =
WAVE 1

Scope =
TS-01 MINIMUM SLICE ONLY

TS-01 Minimum Slice =
CREATED FOR REVIEW

Full ARP-02 Completion =
NOT CLAIMED

Artifact Acceptance =
NOT YET DECIDED

Artifact Creation Authorization =
AUTHORIZED

Technical Spike Planning / Execution =
NOT AUTHORIZED

Implementation =
NOT AUTHORIZED
```

> 本文件由 Wave 1 Readiness Artifact Creation Authorization（Level 2）创建。本 Slice 仅覆盖 TS-01（PostgreSQL Multi-worker Concurrency Technical Spike）所需场景，**不声称完成完整 ARP-02**。`Artifact Creation ≠ Artifact Acceptance`。
> 全部场景 Evidence Status 统一为 `NOT YET EVIDENCED` / `REQUIRES TS-01`；本 Slice 不含任何真实测试结果。

---

## 1. Artifact Identity

| 项 | 值 |
|---|---|
| Artifact ID | ARP-02 |
| Exact Name | Concurrency Scenario Matrix |
| Purpose | 枚举 TS-01 必需的并发场景，标识其并发范围、受保护业务不变量、并发控制机制组合、重试分类与用户可见冲突结果，作为持久化/并发控制实现前置条件。 |
| Scope | TS-01 MINIMUM SLICE ONLY |
| Source / Traceability | RFC-002-DQ-07 §54-56（Concurrency Scenario Matrix = REQUIRED / NOT AUTHORIZED，字段清单）；DQ-09 §94（Dispatch 场景补充）；DQ-11 §154（版本分配/CAS/失效/恢复场景） |
| Decision Status | DRAFT — USER REVIEW REQUIRED |

---

## 2. Owning DQ / DEC / RFC

| 项 | 值 | Source / Traceability |
|---|---|---|
| Primary Owning DQ | RFC-002-DQ-07（Concurrency Control，Accepted Direction = Layered Concurrency Control） | rfc-002-decision-questions.md §DQ-07 |
| Contributing DQ | DQ-08（Idempotency）· DQ-09（Durable Dispatch）· DQ-10（Integration Event 重复投递）· DQ-11（Versioning）· DQ-16（Test）· DQ-17（Security） | rfc-002-decision-questions.md |
| Related DEC | DEC-029（Human Review 并发）· DEC-033（Runtime Retry）· DEC-035（Atomic Commit） | docs/decisions/ |
| Downstream RFC Boundary | RFC-003（Work Retry/Backoff/Dead-letter）· RFC-004（API 冲突状态码 / ETag / If-Match） | rfc-002-analysis-cross-rfc-boundary.md |

---

## 3. Authoritative Inputs

| 输入 | 角色 | Source / Traceability |
|---|---|---|
| RFC-002-DQ-07 Accepted Decision | 分层并发控制模型 + Matrix 字段 + TS-01 Spike 必备验证项 | rfc-002-decision-questions.md §DQ-07 |
| RFC-002-DQ-09 §94/§97 | Dispatch 并发场景（Claim Race / Lease Expiry / Worker Crash / stale fencing / duplicate Delivery / Cancel-vs-complete / simultaneous retry / ordering conflict） | rfc-002-decision-questions.md §DQ-09 |
| RFC-002-DQ-11 §154 | 版本竞争场景（Version Number Allocation / Pointer CAS / Invalidation / Promotion-vs-Invalidation / Restore-vs-New Write / Concurrent Restore / No Orphan Version） | rfc-002-decision-questions.md §DQ-11 |
| RFC-002-DQ-08 | 幂等并发（同 Key±Fingerprint） | rfc-002-decision-questions.md §DQ-08 |

---

## 4. Ownership & Review Roles

| 角色 | 值 | 说明 |
|---|---|---|
| Primary Owner Role | Concurrency / Persistence Architecture Owner | 具体人选 = PENDING USER DECISION。 |
| Contributors | 各业务模块 Owner · Workflow Runtime Owner | 场景受保护不变量来源。 |
| Reviewers | 用户（Product Decision Owner） | Artifact Acceptance 仅由用户决定。 |

---

## 5. Authorization Boundary

```text
Artifact Creation Authorization =
AUTHORIZED（本文件创建属 Level 2）

Artifact Acceptance =
NOT YET DECIDED

Technical Spike Planning / Execution =
NOT AUTHORIZED

TS-01 Execution =
NOT AUTHORIZED

Implementation =
NOT AUTHORIZED
```

---

## 6. Column Index（16 正式列映射）

本 Slice 的 16 个正式列按主题分组呈现于第 7 节 Table A–D；各表共享同一 `CONC-xxx` 行 ID 与行序。列映射如下：

| 正式列 | 所在表 |
|---|---|
| Scenario · Concurrency Scope · Protected Business Invariant | Table A |
| Optimistic Revision · Database Unique Constraint · Durable Lease · fencing_token · Pessimistic Lock | Table B |
| Retry Classification · Retry Owner · Maximum Attempts · User-visible Conflict Result | Table C |
| Related DQ / DEC / RFC · Source / Traceability · Decision Status · Evidence Status | Table D |

> Table B 单元格受控取值：`REQUIRED` / `DEFAULT` / `NOT REQUIRED` / `PROHIBITED` / `RESTRICTED（queue-claim only）` / `NOT APPLICABLE`。

---

## 7. Matrix（TS-01 Minimum Slice）

> 行 ID 规则：`CONC-001`…（Artifact Traceability ID，非数据库主键 / 生产 ID）。

### Table A — Scenario Identity & Scope

| Row ID | Scenario | Concurrency Scope | Protected Business Invariant（→ ARP-01） |
|---|---|---|---|
| CONC-001 | `expected_revision` compare-and-swap 并发（普通业务写） | 单业务对象 Current Truth 更新 | 冲突回滚零部分写入（INV-002~INV-008） |
| CONC-002 | Current Truth Pointer Promotion Race | Task 级 Pointer CAS | 仅一个正式版本被提升为 Current Truth（INV-001） |
| CONC-003 | Named Unique Constraint Race（重复业务事实） | 命名唯一约束范围 | 重复业务事实最终防线（INV-002~INV-008） |
| CONC-004 | Concurrent Work Intent Claim | Durable Work Intent 队列式 Claim | 一个 Intent 仅被一个 Worker 有效领取（REC-009） |
| CONC-005 | `SKIP LOCKED` No-double-claim | 短事务队列式 Claim | 不双重领取同一队列项（REC-009） |
| CONC-006 | Lease Expiry and Takeover | 执行所有权（Lease + fencing） | 接管产生更高 fencing_token（REC-009） |
| CONC-007 | Stale `fencing_token` Commit Rejection | 最终提交重验 | 旧 Worker 不得完成提交（REC-009） |
| CONC-008 | SQLSTATE `40001` serialization_failure | 数据库事务失败分类 | 事务重试身份保持（INV-001~INV-011） |
| CONC-009 | SQLSTATE `40P01` deadlock_detected | 数据库事务失败分类 | 事务重试身份保持（INV-001~INV-011） |
| CONC-010 | Transaction Retry Identity Preservation | 重试复用 Command ID 等身份 | Retry 不创建新 Domain Version（IDEM 边界） |
| CONC-011 | Same Idempotency Key + Same Fingerprint | 幂等重放 | 重放原 Application Result，不重复副作用 |
| CONC-012 | Same Idempotency Key + Different Fingerprint | 幂等冲突 | 返回 Idempotency Key Conflict，不覆盖不执行 |
| CONC-013 | Duplicate Delivery / Consumer Dedup | Integration Event Consumer | 重复投递仅一次业务效果（REC-009/REC-010） |
| CONC-014 | Worker Crash after Claim | Work Intent 领取后崩溃 | 崩溃后可重新领取，不丢失不重复 |
| CONC-015 | Commit Outcome Unknown | 提交结果未知重试 | 重试不重复外部 Provider 调用 |
| CONC-016 | Atomic Business Commit Fault Windows | DEC-035 原子提交故障窗口 | 全有或全无，无部分写入 |
| CONC-017 | No Partial Business Commit | 冲突回滚 | 零部分 Current Truth 写入 |
| CONC-018 | No Orphan Domain Version | 并发版本分配 | Domain Version 与 Evidence Link 同生共死（INV-010） |
| CONC-019 | No Duplicate Work Intent | Intent 唯一性 | 同一 Intent 不重复创建（REC-009） |
| CONC-020 | Restore-versus-new-write（限 RFC-002 已由 TS-01 验证的语义） | Business Restore 与新写并发 | Restore 为新前向 Command，不覆盖较新写 |
| CONC-021 | Concurrent Version Number Allocation | 并发 version_number 分配 | 不产生重复 Domain Version |
| CONC-022 | Current Version Invalidation Race | Invalidation 与读/写并发 | Invalidation 不删版本、不静默回退 |
| CONC-023 | Promotion-versus-Invalidation | 提升与失效并发 | 显式语义，不产生冲突 Current Truth |
| CONC-024 | Cancel-versus-complete（Dispatch） | 取消与完成并发 | 协作式取消不产生部分写（REC-009） |

### Table B — Control Mechanisms

| Row ID | Optimistic Revision | Database Unique Constraint | Durable Lease | fencing_token | Pessimistic Lock |
|---|---|---|---|---|---|
| CONC-001 | DEFAULT（expected_revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-002 | DEFAULT（Pointer 独立 revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-003 | NOT REQUIRED | REQUIRED（命名唯一约束） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-004 | NOT REQUIRED | REQUIRED（Intent 领取唯一性） | REQUIRED | REQUIRED | RESTRICTED（SKIP LOCKED 短事务） |
| CONC-005 | NOT REQUIRED | NOT REQUIRED | REQUIRED | REQUIRED | RESTRICTED（SKIP LOCKED，仅 queue claim） |
| CONC-006 | NOT REQUIRED | NOT REQUIRED | REQUIRED | REQUIRED（单调递增） | NOT REQUIRED |
| CONC-007 | REQUIRED（最终提交重验 expected_revision） | NOT REQUIRED | REQUIRED（重验 Lease Holder） | REQUIRED（重验 fencing_token） | NOT REQUIRED |
| CONC-008 | DEFAULT（重试后重验） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-009 | DEFAULT（重试后重验） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-010 | DEFAULT | 按 DQ-08 | 按 DQ-08/DQ-09 | 按 DQ-09 | NOT REQUIRED |
| CONC-011 | DEFAULT | REQUIRED（Scope+Key+Fingerprint） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-012 | DEFAULT | REQUIRED（Scope+Key） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-013 | DEFAULT | REQUIRED（Consumer Dedup Marker） | 按 Consumer | 按 Consumer | NOT REQUIRED |
| CONC-014 | NOT REQUIRED | REQUIRED | REQUIRED | REQUIRED | RESTRICTED（SKIP LOCKED） |
| CONC-015 | DEFAULT | 按 DQ-08 | 按 DQ-09 | 按 DQ-09 | NOT REQUIRED |
| CONC-016 | DEFAULT | 按参与者 | 按参与者 | 按参与者 | NOT REQUIRED |
| CONC-017 | DEFAULT | 按参与者 | 按参与者 | 按参与者 | NOT REQUIRED |
| CONC-018 | DEFAULT | REQUIRED（版本唯一性） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-019 | NOT REQUIRED | REQUIRED（Intent 唯一性） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-020 | DEFAULT（Restore 新前向 Command） | 按 DQ-11 | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-021 | DEFAULT | REQUIRED（version_number 唯一性） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-022 | DEFAULT（revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-023 | DEFAULT（revision CAS） | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED | NOT REQUIRED |
| CONC-024 | DEFAULT | 按 DQ-09 | REQUIRED | REQUIRED | NOT REQUIRED |

> 悲观锁说明：`SELECT FOR UPDATE / NOWAIT / 悲观行锁` 不是全局默认（DQ-07 §30）；`SKIP LOCKED` 仅限显式队列式 Claim 的短事务（DQ-07 §28-29）；Session-level Advisory Lock = PROHIBITED（DQ-07 §33）。

### Table C — Retry & Outcome

| Row ID | Retry Classification | Retry Owner | Maximum Attempts | User-visible Conflict Result |
|---|---|---|---|---|
| CONC-001 | 语义冲突（stale revision）不盲目重试 | 调用方 / Application 明确策略 | NOT APPLICABLE（不自动重试） | stale revision 拒绝；冲突语义呈现（HTTP 协议留 RFC-004） |
| CONC-002 | 语义冲突不盲目重试 | Application | NOT APPLICABLE | Pointer 未被非法提升 |
| CONC-003 | unique_violation 未分类不盲目重试 | Application（按 DQ-08 转幂等响应） | NOT APPLICABLE | 重复业务事实被拒或幂等响应 |
| CONC-004 | Claim 失败不重试同一领取 | Worker | NOT APPLICABLE | 未被领取者可再次 Claim |
| CONC-005 | 未领取到项不视为错误 | Worker | NOT APPLICABLE | 无双重领取 |
| CONC-006 | Lease 过期由接管处理 | Worker/Runtime（RFC-003 前为 DQ-09 语义） | NOT APPLICABLE | 旧 Holder 失去执行所有权 |
| CONC-007 | stale fencing 拒绝，不重试 | Application Transaction Runner | NOT APPLICABLE | 旧 Worker 提交被拒 |
| CONC-008 | 可能瞬时（transient） | Application Transaction Runner / Command Executor | 3 次总事务尝试（1 初始 + 2 重试；DQ-07 §40） | 重试后成功或终局失败 |
| CONC-009 | 可能瞬时（transient） | Application Transaction Runner / Command Executor | 3 次总事务尝试（DQ-07 §40） | 重试后成功或终局失败 |
| CONC-010 | Retry 复用 Command ID/Idempotency Key/Stage Run ID/Fingerprint，新 Attempt ID | Application Transaction Runner | 按 DQ-07/DQ-08 | 无新 Domain Version |
| CONC-011 | 幂等重放（非重试错误） | 幂等层 Owning Module | NOT APPLICABLE | 重放原 Application Result |
| CONC-012 | 幂等冲突（不覆盖不执行不盲目重试） | 幂等层 Owning Module | NOT APPLICABLE | Idempotency Key Conflict |
| CONC-013 | Consumer Dedup（同事务 Dedup Marker） | Consumer 模块 | NOT APPLICABLE | 一次业务效果 |
| CONC-014 | Crash 后重新领取（新 Attempt） | Worker/Runtime | 按 DQ-09/RFC-003 | 工作不丢失不重复 |
| CONC-015 | Commit 重试复用已产生不可变外部结果，不重调 Provider | Application Transaction Runner | 按 DQ-07 §47-48 | 不重复外部副作用 |
| CONC-016 | Fault Injection 验证全有或全无 | Test（TS-01） | NOT APPLICABLE | 无部分写入 |
| CONC-017 | 冲突回滚 | Application | NOT APPLICABLE | 零部分 Current Truth 写入 |
| CONC-018 | 版本与 Evidence Link 同事务 | Application | NOT APPLICABLE | 无孤儿版本 |
| CONC-019 | Intent 唯一约束 | Dispatch Capability | NOT APPLICABLE | 不重复 Intent |
| CONC-020 | Restore 为新前向 Command | Application | NOT APPLICABLE | 不覆盖较新写 |
| CONC-021 | 并发版本分配不重复 | Application | NOT APPLICABLE | 无重复 Domain Version |
| CONC-022 | Invalidation 显式 | Application | NOT APPLICABLE | 不静默回退 |
| CONC-023 | 显式语义 | Application | NOT APPLICABLE | 无冲突 Current Truth |
| CONC-024 | Cancel 协作式传播 | Runtime（RFC-003） | NOT APPLICABLE | 无部分写 |

### Table D — Traceability

| Row ID | Related DQ / DEC / RFC | Source / Traceability | Decision Status | Evidence Status |
|---|---|---|---|---|
| CONC-001 | DQ-07 · DQ-04 · DEC-024 | rfc-002-decision-questions.md §DQ-07 §49 | Scenario = ACCEPTED DECISION（DQ-07） | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-002 | DQ-11 · DQ-07 · DEC-024 | rfc-002-decision-questions.md §DQ-11 §154 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-003 | DQ-07 · DQ-08 | rfc-002-decision-questions.md §DQ-07 §49 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-004 | DQ-09 · DQ-07 | rfc-002-decision-questions.md §DQ-09 §94/97 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-005 | DQ-09 · DQ-07 §28-29 | rfc-002-decision-questions.md §DQ-07/09 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-006 | DQ-07 · DQ-09 | rfc-002-decision-questions.md §DQ-07 §59 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-007 | DQ-07 · DQ-09 | rfc-002-decision-questions.md §DQ-07 §59 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-008 | DQ-07 §36-40 | rfc-002-decision-questions.md §DQ-07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-009 | DQ-07 §36-40 | rfc-002-decision-questions.md §DQ-07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-010 | DQ-07 §39 · DQ-08 | rfc-002-decision-questions.md §DQ-07/08 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-011 | DQ-08 | rfc-002-decision-questions.md §DQ-08 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-012 | DQ-08 | rfc-002-decision-questions.md §DQ-08 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-013 | DQ-10 · DQ-08 | rfc-002-decision-questions.md §DQ-10 §121 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-014 | DQ-09 · DQ-07 | rfc-002-decision-questions.md §DQ-09 §97 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-015 | DQ-07 §47-48 · DQ-16 | rfc-002-decision-questions.md §DQ-07/16 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-016 | DQ-16 · DEC-035 | rfc-002-decision-questions.md §DQ-16 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-017 | DQ-07 §59 · DEC-035 | rfc-002-decision-questions.md §DQ-07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-018 | DQ-11 · DQ-07 §59 | rfc-002-decision-questions.md §DQ-11/07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-019 | DQ-09 | rfc-002-decision-questions.md §DQ-09 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-020 | DQ-11 §154 | rfc-002-decision-questions.md §DQ-11 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-021 | DQ-11 §154 · DQ-07 §59 | rfc-002-decision-questions.md §DQ-11/07 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-022 | DQ-11 §154 | rfc-002-decision-questions.md §DQ-11 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-023 | DQ-11 §154 | rfc-002-decision-questions.md §DQ-11 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |
| CONC-024 | DQ-09 §94 · DEC-033 | rfc-002-decision-questions.md §DQ-09 | Scenario = ACCEPTED DECISION | NOT YET EVIDENCED / REQUIRES TS-01 |

---

## 8. Cross-artifact References

| 本 Artifact 元素 | 引用目标 | 关系 |
|---|---|---|
| CONC-xxx Protected Business Invariant | ARP-01 INV-xxx | 受保护不变量指向 ARP-01。 |
| CONC-004/005/006/007/013/014/019/024 | ARP-04 REC-009 / REC-010 | Work Intent / Provider Call 记录类。 |
| CONC-010/011/012/015 | ARP-03 IDEM-xxx | 幂等身份边界。 |
| CONC-008/009/016/017 | ARP-09 TEST-xxx | 对应测试覆盖行。 |

---

## 9. Review Checklist（Artifact-specific）

- [ ] 覆盖并从 RFC-002 重新提取全部 TS-01 必需场景（expected_revision CAS / Pointer Promotion / Named Unique Constraint / Work Intent Claim / SKIP LOCKED / Lease Expiry-Takeover / Stale fencing_token / 40001 / 40P01 / Retry Identity / Idempotency Key±Fingerprint / Duplicate Delivery / Worker Crash / Commit Outcome Unknown / Atomic Commit Fault Windows / No Partial Write / No Orphan Version / No Duplicate Work Intent / Restore-vs-new-write / Version Number Allocation / Invalidation / Promotion-vs-Invalidation / Cancel-vs-complete）。
- [ ] 每行有 Source / Traceability。
- [ ] 全部行 Evidence Status = `NOT YET EVIDENCED` / `REQUIRES TS-01`；未出现 PASS / SUPPORTED / VERIFIED。
- [ ] 未填写真实测试结果。
- [ ] Maximum Attempts 对 40001/40P01 = 3 次总事务尝试（DQ-07），语义冲突不盲目重试。
- [ ] Pessimistic Lock 未作为全局默认；Session-level Advisory Lock = PROHIBITED。
- [ ] 16 正式列全部出现于 Table A–D（见第 6 节 Column Index）。
- [ ] 明确 `Full ARP-02 Completion = NOT CLAIMED`。

---

## 10. Open Questions

| # | 问题 | 决定所有者 | 下一 Gate |
|---|---|---|---|
| OQ-1 | API 冲突状态码 / ETag / If-Match 协议 | 用户 | DEFERRED TO RFC-004 |
| OQ-2 | Work Retry / Backoff / Dead-letter / 人工恢复参数 | 用户 | DEFERRED TO RFC-003 |
| OQ-3 | 完整 ARP-02（非 TS-01 场景）补齐范围 | 用户 | 后续 Wave / Full ARP-02 Gate |

---

## 11. Explicit Non-decisions

- 本 Slice 不填写任何真实测试结果（全部 NOT YET EVIDENCED / REQUIRES TS-01）。
- 本 Slice 不声称完成完整 ARP-02（Full ARP-02 Completion = NOT CLAIMED）。
- 本 Slice 不定义具体 HTTP Status Code / Header（留 RFC-004）。
- 本 Slice 不设置 Retry backoff / jitter 数值（留 RFC-007）。
- 本 Slice 不接受自身（Artifact Acceptance = NOT YET DECIDED）。
- 本 Slice 不授权 TS-01 Planning / Execution 或任何实现。
