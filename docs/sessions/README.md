# Sessions（Exploration Layer）

本目录是 AI Ecommerce Agent 项目的 **Exploration Layer（探索层）**，保存产品讨论的历史记录。

---

## 定位

- Session 是**历史记录**：保存讨论背景、假设、备选方案、权衡过程、被否决方案、开放问题与决策形成过程。
- Session **不是**当前产品事实的唯一来源。当前事实以 `docs/decisions/`（Accepted Decision）与 `docs/product/`、`docs/agents/`、`docs/architecture/`（Current Specifications）为准。
- 文档冲突时，Session 的优先级低于 Accepted Decision 与 Current Specifications（见 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节）。

---

## 写作要求

- **不得只保存最终结论。** 必须保留重要讨论演化过程、被拒绝方案与开放问题。
- 追加新内容时**不删除**之前内容；可整理格式、删除纯重复，但不得改变原始结论含义。
- 必须保留：关键推理过程、方案差异、风险、被否决方案、未决问题。
- 必须区分内容类型：Fact / Observation / Assumption / Proposal / Alternative / Risk / Open Question / Proposed Decision / Accepted Decision。
- ChatGPT 输出的 Proposed Decision 记入「Proposed Decisions」，状态保持 Proposed；只有在用户明确接受后，才在「Accepted Decisions」与 `docs/decisions/` 中记录。

---

## 编号与命名

- 起始编号：`Session-001`
- 文件名格式：`session-NNN-topic-name.md`（如 `session-001-project-positioning-and-mvp.md`）

---

## 模板

新建 Session 请复制 [session-template.md](session-template.md)。

---

## 当前 Session 列表

| Session | 主题 | 状态 | 日期 |
|---------|------|------|------|
| [Session-001](session-001-project-positioning-and-mvp.md) | 项目定位、目标用户与 MVP 核心场景 | Completed（阶段性正式固化） | 2026-07-27 |
| [Session-002](session-002-agent-workflow-reliability-and-technical-capabilities.md) | Agent 工作流、可靠性架构与技术能力需求 | In Discussion | 2026-07-27 |

> Session-001 已完成阶段性正式固化（DEC-001 ~ DEC-010 已接受；产品定位与 MVP 原则层议题收尾）。项目**尚未进入开发**，Development Status 仍 `NOT READY`。
> Session-002 已初始化为 `In Discussion`；Spike Execution Status = COMPLETED，Architecture Readiness Status = CONDITIONALLY READY，Development Status = CONDITIONALLY READY。**RFC-001 已于 2026-07-30 被用户正式接受（`ACCEPTED`）**——DQ-01~DQ-10 全部 ACCEPTED 且 Final Consistency Review 通过。RFC-001 的接受**仅开放 Foundation Planning**。**FND-001、FND-002 与 FND-003 Issue Candidate 均已经形成并经用户确认，Foundation Candidate Planning 与 Final Review（PASS，2026-07-30）均已完成**。Final Review 后 Candidate 状态：**FND-001 = READY FOR AUTHORIZATION；FND-002 = READY, BLOCKED BY FND-001；FND-003 = READY, BLOCKED BY FND-001 AND FND-002**；三者 Issue Creation 与 Implementation 均仍 **NOT AUTHORIZED**。下一正式 Gate 为 **FND-001 Issue Creation and Implementation Authorization Gate**（只有用户明确回复「确认授权创建并实施 FND-001」才可授权创建 FND-001 Issue / Branch / PR 并执行 FND-001 范围内的 Foundation Implementation；该授权不包括 FND-002 / FND-003 或任何业务实现；用户明确授权前不创建任何 Foundation Issue / Branch / PR，不执行 Foundation Implementation）。**不确认生产技术框架，不创建生产代码，Foundation / Business / Production Implementation 仍未授权。**
