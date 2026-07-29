# Documentation Rules（文档规则）

本文件是 AI Ecommerce Agent 项目的文档纪律总则：文档层级、内容类型、归档流程、命名与编号规则、冲突裁决与禁止事项。所有文件写入与更新都必须符合本规则。

---

## 1. 文档层级

项目采用五层文档结构（外加 Governance 与 Execution Gate）：

| 层级 | 位置 | 用途 |
|------|------|------|
| **Governance** | `docs/governance/` | 协议、协作模型、文档规则 |
| **Exploration** | `docs/sessions/` | 讨论历史、假设、备选、被否决方案、开放问题、决策形成过程。Session 是历史记录，**不**是当前事实的唯一来源。 |
| **Proposal** | `docs/rfcs/` | 重大方案及替代方案。RFC ≠ 已接受决定。 |
| **Decision** | `docs/decisions/` | 只保存用户明确接受的决定及原因。 |
| **Current Truth** | `docs/product/`、`docs/agents/`、`docs/architecture/` | 当前有效的产品与系统事实。Decision Record 解释「为什么」，Current Specification 说明「怎样工作」。 |
| **Execution Gate** | `docs/reviews/`、`docs/handoffs/` | 实现就绪审查与交接。 |
| **Execution（未来）** | `tasks/`、`issues/`、`src/`、`tests/` | 实现。**当前阶段不得创建。** |

---

## 2. 内容类型（必须严格区分）

在 Session、RFC、Decision 与规格中必须明确标注，**不得混用**：

- **Fact**：已确认的事实
- **Observation**：讨论中的观察
- **Assumption**：尚未验证的假设
- **Proposal**：建议方案
- **Alternative**：备选方案
- **Risk**：风险
- **Open Question**：开放问题
- **Proposed Decision**：等待用户确认的决定提案
- **Accepted Decision**：用户明确接受的决定

> 关键纪律：**Proposed Decision 与 Accepted Decision 必须区分。** ChatGPT 输出的 Proposed Decision 在用户明确接受前一律保持 Proposed。

---

## 3. 归档流程（每次收到 ChatGPT 输出后）

1. **判断内容类型**（见第 2 节）。
2. **更新 Session**：追加本轮讨论；不删除历史；不改原结论含义；可整理格式、删纯重复，但必须保留推理过程、方案差异、风险、被否决方案、未决问题。
3. **判断是否需要 RFC**：重大 / 跨模块 / 难回滚议题可创建 Draft RFC、更新现有 RFC 或建议需要 RFC；不得因一个建议自动创建大量 RFC。
4. **处理 Proposed Decisions**：记入 Session 的 Proposed Decisions，状态保持 Proposed，不写成 Accepted。
5. **处理用户确认**：用户明确接受时——创建/更新 DEC、更新 decision-log、Session 标记 Accepted、更新 Current Specifications、同步清单记录、保留双向链接。
6. **同步 Current Truth**：仅在决定被明确接受后才更新 vision / prd / mvp-scope / user-personas / user-flows / Agent Specs / Architecture Specs / Data Contracts / Integration Boundaries / AGENTS.md。
7. **检查冲突**：按第 6 节优先级裁决。
8. **输出归档报告**：只输出 Archive Result，不重新展开产品讨论，不替 ChatGPT 继续提大量方案。若存在歧义，保留为 Open Question 或 Conflict，不得自行补全。

---

## 4. 命名与编号规则

### 4.1 Session

- 起始编号：`Session-001`
- 文件名：`session-001-topic-name.md`
- 至少包含：Metadata、Context、Goal、Non-goals、Existing Constraints、Questions to Resolve、Discussion（Facts / Observations / Assumptions / Proposals / Alternatives / Trade-offs / Risks）、Proposed Decisions、Accepted Decisions、Rejected Approaches、Open Questions、Deferred Topics、Documentation Updates、Synchronization Checklist。
- **Session 不得只保存最终结论**，必须保留讨论演化过程、被拒绝方案与开放问题。

### 4.2 RFC

- 起始编号：`RFC-001`
- 文件名：`rfc-001-topic-name.md`
- 状态只能使用：`Draft` / `In Discussion` / `Accepted` / `Rejected` / `Superseded` / `Implemented`。
- RFC 是提案，不等于已接受决定。

### 4.3 Decision

- 起始编号：`DEC-001`
- 类型可使用：`Product` / `Architecture` / `UX` / `Data` / `Agent` / `Integration` / `Security` / `Governance`。
- 状态可使用：`Proposed` / `Accepted` / `Rejected` / `Deferred` / `Amended` / `Superseded` / `Deprecated`。
- 仅当用户明确表达批准语义（同意 / 确认 / 接受 / 就按这个方案 / 该决策通过 / 其他语义明确的批准）时，才可标记为 `Accepted`。

完整模板见各目录下的 `*-template.md`。

---

## 5. 仅在决定被明确接受后才可更新的 Current Truth 文件

- `docs/product/vision.md`
- `docs/product/prd.md`
- `docs/product/mvp-scope.md`
- `docs/product/user-personas.md`
- `docs/product/user-flows.md`
- Agent Specifications（`docs/agents/`）
- Architecture Specifications（`docs/architecture/`）
- Data Contracts、Integration Boundaries
- `AGENTS.md`

> **不得把未确认提案写成当前事实。** 当前这些文件均为 NOT READY / 待讨论的初始化桩文件。

---

## 6. 文档冲突优先级

当新旧内容冲突时，按以下优先级裁决：

1. 用户当前明确指令
2. 最新 Accepted Decision
3. 当前产品 / Agent / 架构 / 契约规格（Current Specifications）
4. Accepted RFC
5. Product Vision
6. Governance 文档（含本文件）
7. 历史 Session
8. 非正式备注

**不得让旧 Session 覆盖新 Decision。**

---

## 7. 禁止事项

1. 禁止把 ChatGPT 的建议自动视为用户决定。
2. 禁止扩大 MVP 范围。
3. 禁止擅自选择框架、数据库、模型或第三方服务。
4. 禁止为了让文档看起来完整而补充未经讨论的事实。
5. 禁止静默删除、覆盖或改写历史决策；改变旧决定时必须保留追踪关系（Supersedes / Amends / 双向链接）。
6. 禁止提前实现：在用户明确下达开发指令前，不得编写业务代码、接入模型 API、创建 RAG Pipeline、数据库、前后端、部署或 Docker 配置；ChatGPT 给出的代码示例只能视为 Illustrative Example。

---

## 8. 归档后检查清单

- [ ] Session 已追加本轮讨论（未删历史、未改原结论含义）
- [ ] Proposed Decisions 保持 Proposed，未被写成 Accepted
- [ ] 用户确认的决定已写入 DEC、更新 decision-log、Session 标记 Accepted
- [ ] 仅在决定被明确接受后才更新 Current Truth Layer
- [ ] 未确认内容未写成当前事实
- [ ] 冲突已按第 6 节优先级裁决
- [ ] 与 Session / RFC / DEC 的双向链接已保留
- [ ] 未创建任何业务实现代码
- [ ] 已输出 Archive Result 报告

---

## 9. 相关文档

- [product-design-protocol.md](product-design-protocol.md) — 完整设计与决策协议
- [collaboration-model.md](collaboration-model.md) — 角色职责
- [../sessions/session-template.md](../sessions/session-template.md) — Session 模板
- [../rfcs/rfc-template.md](../rfcs/rfc-template.md) — RFC 模板
- [../decisions/decision-template.md](../decisions/decision-template.md) — Decision 模板
