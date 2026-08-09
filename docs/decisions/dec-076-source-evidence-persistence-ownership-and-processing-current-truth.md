# DEC-076：冻结 Source / Evidence 持久化所有权与处理 Current Truth

## Type

Source Architecture / Persistence / Ownership / Current Truth

## Status

Accepted

## Date

2026-08-09

## Decision

用户接受 P-74A、P-75A、P-76A 与 P-77A，并冻结以下实现边界：

1. `modules/source_evidence/` 是 Source、SourceVersion、SourceVersionProcessing、TaskSourceAssociation，以及后续 Formal Evidence Link 的唯一业务所有模块。其他模块只能经其公开的类型化 Application Contract 协作，不得直接写其 Repository、ORM 或表。
2. Source 替换不会原地改写旧关联：旧 TaskSourceAssociation 进入 `replaced`，同一事务创建绑定 replacement SourceVersion 的新 `active` association identity；旧记录保存 `replaced_by_association_id`。历史 manifest 继续引用旧 association identity、revision 与 SourceVersion；新运行只使用新的 active association。
3. SourceVersion processing 使用以下有界迁移图：
   - 初始状态为 `registered`；
   - `registered` 或 `failed` 可进入 `processing`；
   - `registered` 或 `processing` 可进入 `ready`、`ready_with_rejections` 或 `failed`；
   - 任意非 `superseded` 状态均可前向进入终态 `superseded`；
   - `superseded` 没有出向迁移。
4. 不可变 SourceVersion identity、version 与 submission metadata 和可变 SourceVersionProcessing Current Truth 分开持久化。后者只承载 processing `status`、`revision`、safe failure summary 与 `updated_at`；公共 SourceVersion projection 组合二者。TaskSourceAssociation 仍是独立的 revisioned membership record。

Association membership 的 `active / removed / replaced`、SourceVersion processing、availability 与 integrity 是不同维度，不得用一个状态字段互相代替。

## Reason

Accepted RFC-005 已要求 Source、不可变 SourceVersion、revisioned Task association 与 processing lifecycle 分离，但没有冻结具体 package、replace identity 和“不可变版本 vs 可变处理态”的物理所有权。P-74A～P-77A 关闭了这些实现前阻塞项，同时避免 Task mega-aggregate、Event Sourcing、可变 SourceVersion 和额外历史对象。

## Impact

- Issue #81 改为 tracking parent；实现按 catalogs / DTOs、domain / ports、single-head migration、adapter / UoW、application / CAS 的有界子 Issue 推进。
- RFC-004 Preview / Confirm 继续是 remove / replace 的公共 authority；本 Decision 不改变 authored OpenAPI。
- 本 Decision 不授权 parser、Fragment / Locator、retrieval / index、content blob / object storage、HTTP、Worker、物理删除、PDF / OCR / image 或公共 Schema 扩展。
- 不新增 Hash、SHA 或 digest 要求；DEC-039 的适度校验继续适用。

## Relations

- Concretizes [DEC-067](dec-067-versioned-source-intake-and-format-aware-fragment-contract.md)
- Resolves ARP-01 的 Source / Evidence package ownership implementation blocker
- Conforms [DEC-039](dec-039-proportional-validation-and-review-governance.md)
- Preserves [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md) Preview / Confirm authority

## Related

- [Issue #107](https://github.com/JettxonHo/ai-ecommerce-agent/issues/107)
- [Issue #81](https://github.com/JettxonHo/ai-ecommerce-agent/issues/81)
- [P-74～P-77 proposal](https://github.com/JettxonHo/ai-ecommerce-agent/issues/81#issuecomment-5227664121)
- [RFC-005](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md)
- [Aggregate Invariant Matrix](../readiness/artifacts/aggregate-invariant-matrix.md)
- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Source

用户于 2026-08-09 明确回复：“接受 P-74A、P-75A、P-76A、P-77A”，并要求恢复 Goal 执行。
