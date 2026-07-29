# Product Design Protocol（产品设计与决策协议）

本文件定义 AI Ecommerce Agent 项目的产品设计与决策全流程。所有讨论、提案、决定与文档同步都必须遵循本协议。

---

## 0. 总原则

- **ChatGPT 负责主持讨论与输出方案；用户负责决定；Claude 负责把已确认内容准确写入正确文件。**
- Claude **不得**把 ChatGPT 的建议自动视为用户决定。
- Claude **不得**为了让文档看起来完整而补充未经讨论的事实。
- Claude **不得**静默删除、覆盖或改写历史决策。
- 信息缺失时，保留为 Open Question 或 Conflict，**不得**自行补全。

---

## 1. 流程总览

讨论与决定按以下阶段流转。每个阶段都有对应的文档载体与状态约束。

```
Exploration → Proposal → Decision → Current Specifications → Implementation → Review
   Session       RFC        DEC         product/agents/        tasks/src        reviews/handoffs
                                       architecture/
```

### 1.1 Exploration（探索）

- **载体：** `docs/sessions/`
- **做什么：** 保存讨论历史、问题背景、假设、备选方案、权衡过程、被否决方案、开放问题与决策形成过程。
- **约束：** Session 是历史记录，**不能**被当成唯一的当前产品事实。Session 必须保留重要讨论演化过程，不得只保存最终结论。

### 1.2 Proposal（提案）

- **载体：** `docs/rfcs/`
- **做什么：** 保存重大方案及其替代方案。
- **何时创建 RFC：** 影响多模块、难以回滚、改变核心数据模型、改变 MVP 范围、定义 Agent 职责边界、引入外部系统或 API、涉及安全/权限/隐私、存在多个合理方案、实现成本较高、未来很可能被重新质疑。
- **何时不创建：** 普通讨论、小型字段命名、临时文案或易撤销的实现细节。
- **约束：** RFC 是提案，**不等于**已接受决定。不得因为出现一个建议就自动创建大量 RFC。

### 1.3 Decision（决定）

- **载体：** `docs/decisions/`
- **做什么：** 只保存用户明确接受的决定及原因。
- **约束：** 任何由 ChatGPT 输出但尚未得到用户明确确认的 Proposed Decision，都不能写成 Accepted Decision。

### 1.4 Current Specifications（当前规格）

- **载体：** `docs/product/`、`docs/agents/`、`docs/architecture/`
- **做什么：** 描述当前有效的产品和系统事实。
  - Decision Record 解释「为什么这么决定」。
  - Current Specification 说明「系统当前应该怎样工作」。
- **约束：** 仅在决定被明确接受后才更新；不得把未确认提案写成当前事实。

### 1.5 Implementation（实现）

- **未来载体：** `tasks/`、`issues/`、`src/`、`tests/` 等。
- **约束：** **当前阶段不得创建。** 实现必须以已确认的 Decision 与 Current Specifications 为依据。

### 1.6 Review（审查）

- **载体：** `docs/reviews/`、`docs/handoffs/`
- **做什么：** 进入开发前的 Implementation Readiness Review 与后续交付审查。
- **约束：** 只有审查通过且用户再次明确批准后，才能开始开发。

---

## 2. 文档同步原则

- **顺序约束：** 先有 Accepted Decision，才能更新 Current Truth Layer。
- **不得越级：** 不得用 Session 或 RFC 直接改写 Current Specifications。
- **不得补全：** 文档中信息缺失时，保留为 Open Question；不得为了「完整」而写入未讨论的事实。
- **保留历史：** 更新旧内容时，不删除旧记录；通过 Supersedes / Amends / 双向链接保留追踪关系。
- **双向链接：** Session ↔ RFC ↔ DEC ↔ 受影响的 Current Specifications 必须互相引用。

---

## 3. Decision Gate（决策门）

一个 Proposed Decision 成为 Accepted Decision，必须通过此门：

1. 出现在某 Session 的「Proposed Decisions」中，状态为 Proposed。
2. （如适用）对应 RFC 状态为 Accepted。
3. **用户明确表达批准语义**（同意 / 确认 / 接受 / 就按这个方案 / 该决策通过 / 其他语义明确的批准）。
4. Claude 创建或更新 DEC、更新 `decision-log.md`、在 Session 标记为 Accepted。
5. 更新受影响的 Current Specifications。
6. 在 Session 的 Synchronization Checklist 中记录修改。

ChatGPT 单方面输出的「建议」「推荐」「Proposed Decision」**一律不通过此门**。

---

## 4. 文档冲突优先级

当新旧内容冲突时，按以下优先级裁决：

1. 用户当前明确指令
2. 最新 Accepted Decision
3. 当前产品 / Agent / 架构 / 契约规格（Current Specifications）
4. Accepted RFC
5. Product Vision
6. Governance 文档
7. 历史 Session
8. 非正式备注

**不得让旧 Session 覆盖新 Decision。**

---

## 5. 每次收到 ChatGPT 输出后的处理流程

1. **判断内容类型**：识别 Discussion Summary、Fact、Observation、Assumption、Proposal、Alternative、Risk、Open Question、Deferred Topic、Proposed Decision、Accepted Decision、Rejected Decision、文档同步要求。
2. **更新 Session**：追加本轮讨论，不删除历史，不改原结论含义；保留推理过程、方案差异、风险、被否决方案、未决问题。
3. **判断是否需要 RFC**：重大 / 跨模块 / 难回滚议题可创建 Draft RFC、更新现有 RFC，或建议需要 RFC；不得因一个建议自动创建大量 RFC。
4. **处理 Proposed Decisions**：记入 Session 的 Proposed Decisions，状态保持 Proposed，不写成 Accepted。
5. **处理用户确认**：当用户明确接受时——创建/更新 DEC、更新 decision-log、Session 标记 Accepted、更新 Current Specifications、同步清单记录、保留双向链接。
6. **同步 Current Truth**：仅在决定被明确接受后才更新 vision / prd / mvp-scope / user-personas / user-flows / Agent Specs / Architecture Specs / Data Contracts / Integration Boundaries / AGENTS.md。
7. **检查冲突**：按第 4 节优先级裁决。
8. **输出归档报告**：只输出 Archive Result，不重新展开产品讨论，不替 ChatGPT 继续提大量方案。

---

## 6. 相关文档

- [collaboration-model.md](collaboration-model.md) — 角色职责
- [documentation-rules.md](documentation-rules.md) — 文档规则与内容类型
- [../sessions/session-template.md](../sessions/session-template.md) — Session 模板
- [../rfcs/rfc-template.md](../rfcs/rfc-template.md) — RFC 模板
- [../decisions/decision-template.md](../decisions/decision-template.md) — Decision 模板
- [../handoffs/implementation-readiness.md](../handoffs/implementation-readiness.md) — 开发就绪状态
