# Architecture（架构规格）

本目录是 Current Truth Layer 的一部分，存放 AI Ecommerce Agent 项目的系统、数据与集成架构规格。

---

## 定位

- 架构规格描述「系统当前应该怎样工作」，其内容只能来自用户明确接受的 Decision。
- **当前没有任何已确认的架构。** 尚未决定：技术栈、是否使用 LangGraph、RAG 实现、开源底座、数据结构与集成边界。

---

## 文件

- [system-architecture.md](system-architecture.md) — 系统架构（NOT READY）
- [data-architecture.md](data-architecture.md) — 数据架构与数据契约（NOT READY）
- [integration-boundaries.md](integration-boundaries.md) — 集成边界（外部系统 / API）（NOT READY）

---

## 同步规则

- 仅在决定被明确接受后更新本目录文件。
- 架构必须与 [../decisions/](../decisions/)、[../agents/](../agents/)、[../product/](../product/) 保持一致。
- 不得为使文档「完整」而补充未经讨论的架构事实（不得擅自选择框架 / 数据库 / 模型 / 第三方服务）。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
