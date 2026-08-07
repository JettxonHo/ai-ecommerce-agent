# DEC-057：以稳定产品语义闭合产品规格，并将技术契约交给对应 RFC

## Type

Product Governance / Specification Authority / Contract Handoff

## Status

Accepted

## Decision

产品规格是否闭合，以用户可见目标、范围、输入门禁、工作台流程、审核、版本与失效、证据、结果、导出和验收语义是否完整、一致且可追溯为判断依据。产品层保留稳定的业务语义组、用户行为与关键不变量，不复制公共传输或存储 Schema。

下列技术契约分别由唯一权威文档冻结：

- 公共 Resource、字段名、类型、状态、错误、revision、幂等、Conflict 与下载协议：RFC-004；
- Source、Locator、Pagination、Retrieval 与 Evidence Package 传输：RFC-005；
- Logs、Traces、Metrics、运维参数与演示环境运行边界：RFC-007；
- Fixture 物理文件、具体 expected-output 表示、最终 E2E 步骤与证据格式：Testing Strategy 与 Goal 内独立测试 Issue。

上述下游细节尚未冻结，不再单独构成产品规格未闭合的理由。对应 RFC 和 Testing Strategy 必须实现已接受产品语义，不得用技术限制静默改变产品行为；如果确有冲突，应返回新的 Decision Gate。

Product Current Truth 可以引用概念身份、版本和语义组，但不得把概念字段机械地一对一提升为 OpenAPI、数据库列或实现事实。RFC 也不得重复定义另一套产品目标、范围或用户流程。

## Alternatives Considered

### P-42B：产品与传输字段一起冻结

- 优点：单份产品文档可以看到所有字段与类型。
- 缺点：与 RFC-004 / 005 形成两套 Schema 权威，在接口设计前过早锁死字段并增加返工。
- 结论：不采用。

### P-42C：等待全部 RFC 完成后再判断产品规格

- 优点：最终可以一次同步产品和技术内容。
- 缺点：产品语义与技术实现长期混在同一 Gate，RFC 缺少稳定上游输入，也可能让技术限制反向代替产品决定。
- 结论：不采用。

## Reason

产品规格需要稳定回答“为谁解决什么问题、用户如何完成任务、系统必须保持哪些行为”，而公共接口需要稳定回答“这些行为如何跨进程表达”。将二者拆成明确权威来源，既能在 RFC 前闭合产品输入，也避免平行 Schema 和静默漂移。

## Impact

- Product Vision、PRD、MVP Scope、User Flows 的状态与开放问题必须区分“产品未决”与“下游技术交接”。
- RFC-004 / 005 / 007 必须追溯到 Accepted Product Decision，并在发现冲突时停止而不是改写产品语义。
- Testing Strategy 可以在产品验收场景已接受后继续保持 `PARTIAL`，直到物理 Fixture、可执行命令和证据格式完成；该状态不反向表示产品目标未定义。
- 本决定不接受 RFC-004 / 005 / 007，不冻结任何公共字段或实现，不授权 Technical Spike、业务实现或 Goal 创建 / 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-004、RFC-005、RFC-007；本决定只冻结权威边界，不接受其方案。

## Supersedes

None.

## Amends

- Product Vision、PRD、MVP Scope 与 User Flows 中将公共 Schema、Retrieval 传输、Observability 或测试物理载体混列为产品开放问题的旧状态说明。

## Decision Boundary

本决定不表示产品规格已经自动通过最终一致性 Review。尚存的真实产品开放问题仍需独立提案与用户接受；只有这些问题闭合、Current Truth 同步且最终一致性 Review 通过后，才把产品规格标记为完整。

## Notes

用户于 2026-08-07 明确接受 `P-42A`。Issue #52 / Draft PR #53 负责本决定和产品 Current Truth 的归档。
