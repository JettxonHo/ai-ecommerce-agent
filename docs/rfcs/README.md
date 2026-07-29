# RFCs（Proposal Layer）

本目录是 AI Ecommerce Agent 项目的 **Proposal Layer（提案层）**，保存重大方案及其替代方案。

---

## 定位

- RFC 是**提案**，记录一个重大方案的 Context、Problem、Goals、Proposed Solution、Alternatives、Trade-offs、Risks 等。
- **RFC ≠ 已接受决定。** 即使 RFC 状态为 `Accepted`，也只有当对应内容被用户明确接受并记为 Accepted Decision 后，才会同步到 Current Truth Layer。
- 一个被接受的 RFC 通常会产出一条或多条 DEC（见 [../decisions/](../decisions/)）。

---

## 何时创建 RFC

只有符合以下情况之一的议题才**建议**创建 RFC：

- 影响多个模块
- 难以回滚
- 改变核心数据模型
- 改变 MVP 范围
- 定义 Agent 职责边界
- 引入外部系统或 API
- 涉及安全、权限或隐私
- 存在多个合理方案
- 实现成本较高
- 未来很可能被重新质疑

**不创建 RFC 的情况：** 普通讨论、小型字段命名、临时文案或容易撤销的实现细节。

> 纪律：不得因为出现一个建议就自动创建大量 RFC。可在 Session 中先记录为 Proposal / Open Question，确认其重大性后再提升为 RFC。

---

## 状态

RFC 状态只能使用以下取值：

| 状态 | 含义 |
|------|------|
| `Draft` | 起草中，尚未进入正式讨论 |
| `In Discussion` | 正在讨论 |
| `Accepted` | 方案被接受（仍需走 Decision Gate 才能成为 Accepted Decision 并同步当前事实） |
| `Rejected` | 被否决 |
| `Superseded` | 被后续 RFC 取代（必须指向取代它的 RFC） |
| `Implemented` | 已落地实现（仅在进入开发阶段后使用） |

---

## 编号与命名

- 起始编号：`RFC-001`
- 文件名格式：`rfc-NNN-topic-name.md`

---

## 模板

新建 RFC 请复制 [rfc-template.md](rfc-template.md)。

---

## 当前 RFC 列表

> 暂无。第一个 RFC 将在出现符合「何时创建 RFC」标准的重大议题时创建。
