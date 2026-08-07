# Architecture（架构规格）

本目录是 Current Truth Layer 的一部分，存放 AI Ecommerce Agent 项目的系统、数据与集成架构规格。

---

## 定位

- 架构规格描述「系统当前应该怎样工作」，其内容只能来自用户明确接受的 Decision。
- **已确认：** Modular Monolith、Python 后端、LangGraph StateGraph 确定性编排、版本化 Domain State 与紧凑 Workflow State、Source / Fragment / Evidence Link、按需混合检索、单一 Human Review、API / Worker / CLI 进程边界、模块依赖规则、PostgreSQL + SQLAlchemy 2.x Sync + Psycopg 3 Sync + Alembic 持久化栈，以及 DEC-055～056 的 React / Vite SPA 边界。DEC-067 已进一步冻结 revisioned TaskSourceAssociation、逐资料 Durable Processing、六值 processing lifecycle、SourceSet reference manifest、格式感知 Fragment / Locator 与无 Evidence Package `package_hash` 的重现方式。
- **已完成：** RFC-001、RFC-002、RFC-003、Spike-001 与 FND-001～003。
- **已接受的 RFC-003：** DEC-049 已冻结同 PostgreSQL Service 下的独立 Checkpoint Database、同步 `PostgresSaver`、`sync` durability、可重入 Node 与 Business-Current-Truth-first Reconciliation；DEC-050 已冻结 PostgreSQL Durable Work Intent + Poll-and-claim、数据库权威 Lease / Heartbeat / Fencing Token 与协作式取消 / Supersession；DEC-051 已冻结显式 Compatibility Tuple、Current-Truth-first 七动作 Recovery Decision、受控迁移和 Forward Repair 证据边界。RFC-003 的 DQ-01～09 已闭合，并于 2026-08-06 被用户整体接受。
- **已接受的 RFC-006 架构：** DEC-052 已冻结单一 OpenAI Responses API / `gpt-5.6-terra` 基线、窄型同步 Model Runtime Port 与 Structured Output；DEC-053 已冻结有界 Recovery、可读 Version Tuple、五个固定 Profile 与确定性 Context Assembly；DEC-054 已冻结 Adapter Secret / Payload Allowlist、同 Port Scripted Substitute、断网 Contract Tests 与单次人工 RC Smoke。DQ-01～08 已闭合、Final Consistency Review = PASS，用户已于 2026-08-06 明确接受 RFC-006 整体。
- **仍待闭合：** RFC-004 已整体接受；RFC-005 DQ-01～03 已由 DEC-067 接受，DQ-04～10 与 RFC-005 整体仍待策划；RFC-007、Retrieval Backend、Observability、部署方式与精确实施版本仍待完成。Frontend Architecture 已整体接受。
- 业务与生产实现未授权；概念架构 Accepted 不等于对应生产模块已经实现。

---

## 文件

- [system-architecture.md](system-architecture.md) — 已接受的系统架构概念与仍待 RFC 决定的实现边界
- [data-architecture.md](data-architecture.md) — 已接受的数据 / 状态 / 事务概念与仍待冻结的公共 Schema
- [integration-boundaries.md](integration-boundaries.md) — 已接受的集成边界与仍待 RFC-004 / 005 / 007 决定的协议细节
- [architecture-baseline-v1.md](architecture-baseline-v1.md) — Spike-001 与 RFC 规划使用的架构基线
- [frontend-architecture.md](frontend-architecture.md) — 已接受的前端应用、深工作台、状态 / 交互、生成契约、验证与适度 Web 质量边界

---

## 同步规则

- 仅在决定被明确接受后更新本目录文件。
- 架构必须与 [../decisions/](../decisions/)、[../agents/](../agents/)、[../product/](../product/) 保持一致。
- 不得为使文档「完整」而补充未经讨论的架构事实（不得擅自选择框架 / 数据库 / 模型 / 第三方服务）。
- 冲突时按 [../governance/documentation-rules.md](../governance/documentation-rules.md) 第 6 节优先级裁决。
