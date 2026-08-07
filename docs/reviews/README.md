# Reviews（实现就绪与交付审查）

本目录用于存放进入开发前后的审查记录，包括 Implementation Readiness Review 与后续交付 / 阶段审查。

---

## 定位

- 审查是 **Execution Gate（执行门）** 的一部分：在用户下达开发指令后、实际编码前，必须先通过 Implementation Readiness Review。
- 审查记录保存为单独文件，命名建议 `review-YYYY-MM-DD-<topic>.md`。
- 审查通过**不等于**可以自动开始开发——仍需用户再次明确批准。

---

## Implementation Readiness Review 检查项

进入开发前至少检查：

- 是否存在未解决的关键产品问题
- 是否存在互相冲突的 Decision
- PRD 是否与 MVP Scope 一致
- Agent 规格是否明确
- Architecture 是否与 Decision 一致
- 数据契约是否明确
- 验收标准是否存在
- 必要 RFC 是否已 Accepted
- 文档是否存在未同步部分

当前就绪状态见 [../handoffs/implementation-readiness.md](../handoffs/implementation-readiness.md)。

---

## 当前审查记录

- [2026-08-07 Product Specification Final Consistency Review](review-2026-08-07-product-specification-final-consistency.md)：`PASS`，用户整体接受已记录；这不是 Implementation Readiness Review，也不授权开发。
- [2026-08-07 RFC-004 Final Consistency Review](review-2026-08-07-rfc-004-final-consistency.md)：`PASS`，RFC 整体接受仍待用户决定；不授权 OpenAPI / API 实现、Spike 或 Goal。
