# DEC-077：冻结 Review / Brief / Export 持久化所有权与原子结果边界

## Type

Review Architecture / Versioning / Current Truth / Atomic Outcomes

## Status

Accepted

## Date

2026-08-09

## Decision

用户接受 P-78A、P-79A、P-80A 与 P-81A，并冻结以下实现边界：

### Module ownership

- `modules/human_review/` 唯一拥有 Review cycle、不可变 Review Package snapshot、Review Draft、不可变 Review Decision 与 Approved Strategy version。
- `modules/marketing_brief/` 唯一拥有 Marketing Brief version 与 comparison。
- `modules/xiaohongshu_adapter/` 唯一拥有 Xiaohongshu Brief version 与 comparison。
- 窄 `modules/export_delivery/` 唯一拥有跨 version family 的 Export Snapshot 与 basis validation。
- Task Management 继续唯一拥有 Task / Stage Current Truth。其他模块不得直接写 Task Management 的表、ORM 或 Repository。

### Identity and version boundary

- `ReviewId` 表示稳定 review cycle identity。
- 每个不可变 Review Package snapshot 拥有自己的 `ReviewPackageId` 和在该 `ReviewId` 内唯一、正数单调的 package `VersionNumber`。
- 每个 exact current Package 只有一个 `ReviewDraftId`，其 `Revision` 单调增加；Draft 不是正式 Domain Version，也不表示批准。
- 不可变 `ReviewDecisionId` 绑定 exact Review、Package identity + version、Draft identity + revision。
- Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 使用不可变 `DomainVersionId`，并在 `(task_id, resource_family)` 内分别使用单调 `VersionNumber`；不增加 speculative logical-series identity。
- 不可变 content row 与所属 family 的可变 Version State 分离；Version State 只表达 `valid`、typed invalidation reason、`revision` 与 `updated_at`。
- `ExportSnapshotId` 是不可变导出身份；Export Snapshot 不获得 Current Truth promotion。

### Current Truth and atomic outcome sequencing

Task Management-owned Stage `current_version` / `last_valid_version` 以及 Task status / revision 是 Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 唯一持久化 Current Truth 映射。Task Overview 顶层结果引用只能由这些 Stage records 投影；不得增加平行 pointer table，也不得用 `MAX(version)` 推断 Current Truth。

Issue #82 改为 tracking parent。Domain、schema、adapter、Draft CAS、immutable reads 与非 dispatch persistence primitives 可以按有界子 Issue推进；最终 Review outcome commands 在以下 typed participants 全部可加入同一事务前保持阻塞：Audit、Idempotency Result、Task / Stage participant 与 PostgreSQL Durable Work Intent。

完整 outcome 只能由一个 Composite Application Use Case 拥有一个 outer UoW 和一次 commit，同时写入适用的：Review Decision、Approved Strategy、Task / Stage / pointers、Audit、idempotency result 与唯一 continuation Work Intent。不得先暴露部分或替代性的 `SubmitReview`。

QC passed、validator passed、selection 或 generation success 均不等于人工批准；只有显式、current、revision-safe 的用户提交可以创建 Approved Strategy。

## Reason

DEC-029～031 与 RFC-004 已冻结产品和公共 HTTP 语义，但 ARP-01 仍把 exact package ownership 标为实现前阻塞；同时完整 submit 所需的跨模块原子参与者尚未落地。P-78A～P-81A 关闭所有权、identity/version 和 Current Truth 决策，同时保留 Durable Resume 与一次业务提交的正确性，不以缩小范围为由降低验收标准。

## Impact

- #82 的领域与持久化基础可以拆分规划；其 migration 仍须串行依赖 #81 的实际 single head。
- 完整 Review outcome 不因本 Decision 自动可执行；缺少任一事务参与者即停止相关命令实现。
- HTTP handler、Frontend、模型生成、Skills、retrieval / evidence validation、Markdown render / download、通用 workflow engine、自动批准与公共 OpenAPI 变化继续不在本切片范围。
- 不新增 Export Hash、SHA 或 digest。

## Relations

- Concretizes [DEC-029](dec-029-human-review-and-approved-strategy-contract.md), [DEC-030](dec-030-marketing-brief-generation-skill-contract.md), [DEC-031](dec-031-xiaohongshu-brief-mapping-adapter-contract.md) and [DEC-046](dec-046-review-brief-and-export-product-contract.md)
- Resolves ARP-01 的 Review / Strategy / Brief / Export package ownership implementation blocker
- Extends [RFC-002](../rfcs/rfc-002-persistence-and-transaction-architecture.md) atomic business commit ownership
- Preserves [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md) as the public HTTP authority

## Related

- [Issue #107](https://github.com/JettxonHo/ai-ecommerce-agent/issues/107)
- [Issue #82](https://github.com/JettxonHo/ai-ecommerce-agent/issues/82)
- [P-78～P-81 proposal](https://github.com/JettxonHo/ai-ecommerce-agent/issues/82#issuecomment-5227772862)
- [Aggregate Invariant Matrix](../readiness/artifacts/aggregate-invariant-matrix.md)
- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Source

用户于 2026-08-09 明确回复：“接受 P-78A、P-79A、P-80A、P-81A”，并要求恢复 Goal 执行。
