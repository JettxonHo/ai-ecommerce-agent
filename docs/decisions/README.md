# Decisions（Decision Layer）

本目录是 AI Ecommerce Agent 项目的 **Decision Layer（决定层）**，只保存用户明确接受的决定及原因。

---

## 定位

- 这里只记录 **Accepted Decision**（用户明确接受的决定）及其 Reason / Impact / 追踪关系。
- 任何由 ChatGPT 输出但**尚未**得到用户明确确认的 Proposed Decision，都**不能**写成 Accepted Decision。Proposed Decisions 保留在对应 Session 中。
- Decision Record 解释「为什么这么决定」；Current Specification（`docs/product/`、`docs/agents/`、`docs/architecture/`）说明「系统当前应该怎样工作」。

---

## 何时可标记为 Accepted

只有当用户明确表达以下语义之一时，决定才可标记为 `Accepted`：

- 同意
- 确认
- 接受
- 就按这个方案
- 该决策通过
- 其他语义明确的批准表达

> ChatGPT 单方面输出的「建议」「推荐」「Proposed Decision」一律不能标记为 Accepted。

---

## 类型（Type）

可使用：`Product` / `Architecture` / `UX` / `Data` / `Agent` / `Integration` / `Security` / `Governance`

## 状态（Status）

可使用：`Proposed` / `Accepted` / `Rejected` / `Deferred` / `Amended` / `Superseded` / `Deprecated`

---

## 编号与命名

- 起始编号：`DEC-001`
- 文件名格式：`dec-NNN-short-title.md`（小写、连字符）

---

## 流程

1. ChatGPT 在 Session 中输出 Proposed Decision（状态 Proposed）。
2. 用户明确接受后，Claude：
   - 创建或更新对应 DEC（状态 Accepted）；
   - 在 [decision-log.md](decision-log.md) 追加一行；
   - 在对应 Session 的「Accepted Decisions」标记并双向链接 DEC；
   - 更新受影响的 Current Specifications；
   - 在 Session 的 Synchronization Checklist 记录修改；
   - 保留与 Session / RFC 的双向链接。
3. 后续决定改变旧决定时：旧 DEC 标记为 `Superseded` 或 `Amended`，并指向新 DEC；**不删除**旧记录。

---

## 模板

新建 DEC 请复制 [decision-template.md](decision-template.md)。

---

## 索引

见 [decision-log.md](decision-log.md)。当前最新 Accepted Decision 为 [DEC-069](dec-069-authoritative-retrieval-scope-referenced-evidence-and-explicit-degradation.md)；旧决定被修订时保留原文并通过 `Amends / Amended by` 追踪。
