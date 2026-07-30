# RFC-001：Repository and Application Architecture

> **Status:** `DRAFTING`
> **Parent DEC-038 Topic:** RFC Planning and Dependency Order
> **Wave:** Wave 1
> **纪律：** 本文档为 RFC 提案，**不等同**已接受决定。任何被用户明确接受的内容，会同步更新到 `docs/architecture/architecture-baseline-v1.md` 与 Traceability Matrix。

---

## Summary

本 RFC 负责收敛 AI Ecommerce Agent 进入生产实现前所需的**代码仓结构**与**应用架构**决策。核心问题包括：单一仓库与多仓库、单体与服务、部署单元边界、模块划分、依赖方向、数据所有权、Graph Node 与 Repository 的边界、测试架构、未来服务提取边界等。

本 RFC 不选择具体数据库 / ORM / Web Framework / 部署平台，这些由后续 RFC-002 至 RFC-007 决定。

---

## Context

- DEC-038 已接受，项目进入依赖驱动的 RFC 波次。RFC-001 是 Wave 1 首个议题，阻塞所有生产模块的开始。
- DEC-021 已明确 MVP 不采用 Multi-Agent 主架构，但保留 Bounded Worker 扩展空间。
- DEC-023 确定使用 LangGraph StateGraph 作为工作流编排表达。
- DEC-024 定义了 Versioned Domain State + Compact Graph State + 三类存储分离的约束。
- DEC-033 定义了 Runtime Reliability、运行身份分层、幂等、事务等约束。
- Architecture Baseline v1 已将所有生产技术域标记为 `PENDING RFC`，并列出 RFC-001..007。
- Spike-001 的临时技术栈（Python 3.13 + LangGraph + SQLite + SqliteSaver）仅为验证，不构成生产承诺。

---

## Problem

进入生产实现前，必须回答：

1. 项目使用单一 Git Repository 还是多 Repository？
2. 初始生产架构采用 Modular Monolith 还是 Multi-service？
3. 主要后端部署单元是什么？
4. 模块如何划分？业务模块与平台模块的边界在哪？
5. 模块之间通过什么契约协作？
6. Domain / Application / Infrastructure / Interface 的依赖方向是什么？
7. Modular Monolith 内是否允许共享数据库实例？数据所有权如何隔离？
8. Graph Node 能否直接访问 Repository？
9. 如何保留未来服务提取能力？
10. 正式后端语言、目录结构、依赖注入、测试架构等如何决定？

---

## Goals

- 确定生产代码仓与应用架构的基础结构。
- 明确模块边界、协作方式与依赖方向。
- 保持 Domain 与具体框架 / 数据库 / 部署平台的解耦。
- 保留未来从 Modular Monolith 提取服务的能力。
- 为 RFC-002（Persistence）和 RFC-003（LangGraph Runtime）提供清晰的接口边界。

## Non-goals

- 不选择具体数据库、ORM、Web Framework、部署平台。
- 不设计完整 API Schema。
- 不实现业务模块或生产代码。
- 不将 Spike 临时代码直接迁移为生产代码。

---

## Decision Questions

本 RFC 采用 DEC-038 的 Decision Questions Contract：每个核心问题作为一个 Decision Question（DQ），只有用户明确接受的 DQ 才能写入 Current Truth。RFC 整体在全部关键 DQ 被接受前保持 `DRAFTING`。

### DQ-01：Modular Monolith or Multi-service

**Status:** `ACCEPTED`

#### Question

MVP 与首个生产版本应采用 Modular Monolith First 还是 Multi-service First？

#### Decision

采用 **Modular Monolith First**。

其正式含义为：

```text
Single Repository
+
One Primary Backend Deployment Unit
+
Business Capability Modules
+
Platform Capability Modules
+
Strict Dependency Direction
+
Explicit Application and Repository Interfaces
+
Separated Data Ownership
+
Replaceable Infrastructure Adapters
+
Future Service Extraction Boundaries
```

当前不采用 Multi-service 作为初始生产架构。

#### Deployment Boundary

MVP 默认采用：

```text
One Primary Backend Application
```

不在初始阶段拆分为：

- Task Service
- Workflow Service
- Source Service
- Retrieval Service
- Human Review Service
- Brief Service
- Model Runtime Service

未来可以根据实际需求提取服务，但服务拆分不是当前默认架构。

#### Repository Boundary

正式项目使用：

```text
One Git Repository
```

单一 Repository 不表示：

- 所有代码放在一个文件中；
- 所有模块可以互相 Import；
- 所有模块共享内部实现；
- 所有 Graph Node 可以直接访问数据库；
- 所有模块拥有相同的数据写入权限。

Repository 内必须维持清晰的模块和依赖边界。

#### Module Boundary

系统应按业务能力与平台能力划分模块。

**Business Capability Modules**（概念上）：

```text
Product Intake and Fact Extraction
Customer Insight Analysis
Product Positioning
Human Review
Marketing Brief Generation
Xiaohongshu Mapping Adapter
```

**Platform Capability Modules**（概念上）：

```text
Source and Evidence
Workflow Runtime
Persistence
Retrieval Runtime
Model Runtime
Observability
Configuration
Identity and Access
```

具体目录和 Package 结构尚未确认，将由后续 RFC-001 Decision Questions 决定。

#### Module Collaboration

模块之间必须通过明确边界协作，例如：

- Application Service
- Domain Contract
- Repository Interface
- Provider Interface
- Command
- Query
- Published Application Event

不得：

- 任意访问其他模块的内部类；
- 绕过 Application Layer 修改其他模块数据；
- 直接访问其他模块的 Repository Implementation；
- 使用数据库表作为隐式模块 API；
- 通过 LangGraph State 共享完整业务对象；
- 将 Prompt 作为模块之间唯一契约。

具体允许的协作方式将在 RFC-001 后续 Decision Questions 中确认。

#### Dependency Direction

当前确认原则：

```text
Interface
↓
Application
↓
Domain
```

Infrastructure 负责实现上层定义的技术接口：

```text
Infrastructure
→ implements
→ Repository and Provider Interfaces
```

Domain 不得依赖：

- LangGraph
- FastAPI 或其他 Web Framework
- ORM
- PostgreSQL 或其他具体数据库
- OpenAI SDK 或其他 Model SDK
- Vector Database
- Message Queue
- Observability Provider
- Deployment Platform

具体分层和依赖规则仍需后续 Decision Questions 确认。

#### Data Ownership Boundary

允许 Modular Monolith 在 MVP 阶段共享一个数据库实例，但必须保持：

```text
Shared Database Instance
≠
Shared Data Ownership
```

必须区分：

- Business Domain Data
- Workflow Runtime Data
- Checkpoint Data
- Source and Evidence Data
- Retrieval Index Data
- Audit Data
- Observability Data

模块不得因处于同一个应用或数据库实例中，就任意访问和更新其他模块的数据。

正式数据库、Schema、ORM 和事务方案由 RFC-002 决定，本 Decision 不作选择。

#### Graph and Database Boundary

本 Decision 尚未确认 Graph Node 能否直接访问数据库。

在对应 Decision Question 被接受前，保持以下保守边界：

```text
Graph Node must not become the owner of business persistence rules.
```

Graph Node 不得临场定义：

- Domain Version 写入
- Current Truth 更新
- Evidence Link 事务
- Idempotency
- Audit
- Invalidation

最终 Graph、Application Service 和 Repository 的职责划分由 RFC-001 后续议题决定。

#### Future Service Extraction

Modular Monolith 必须保留未来服务提取边界。

潜在可提取能力包括：

```text
Source Processing
Retrieval Runtime
Workflow Runtime
Model Runtime
Human Review
Observability
```

未来只有在出现可验证需求时才拆分，例如：

- 某模块需要独立扩缩容；
- 某模块具有独立部署周期；
- 多团队需要独立所有权；
- 数据安全要求物理隔离；
- 某能力需要服务多个产品；
- 单体应用出现可测量的性能或可靠性瓶颈；
- 独立故障域能产生明确业务价值。

不得仅因为“微服务更先进”而拆分。

#### Extraction Strategy

未来服务提取应遵循：

```text
Stable In-process Module Interface
↓
Infrastructure Adapter Boundary
↓
Remote API or Message Adapter
↓
Independent Deployment
```

不得直接重写整个系统或让业务模块依赖远程通信细节。

#### Rejected Initial Option

当前拒绝：

```text
Multi-service First
```

主要原因：

- 当前团队和产品阶段不需要多服务所有权；
- MVP 需要较快迭代；
- Human Review 和 Current Truth 存在强事务一致性；
- 过早拆分会引入分布式事务；
- 会增加 Saga、Outbox、消息幂等和网络故障处理；
- 会增加本地开发、部署和测试复杂度；
- 当前没有独立扩缩容和独立部署的证据；
- 不会直接增加首期用户价值。

该拒绝仅针对初始架构，不表示系统永远不得拆分服务。

#### Trade-offs

Positive：

- 减少 MVP 开发和部署复杂度；
- 更容易维护原子事务；
- 更容易实现端到端测试；
- 更适合当前单人或小团队开发；
- Agent 更容易在明确边界内工作；
- 能集中验证核心业务价值；
- 保留未来服务拆分路径。

Risks：

- 模块边界可能逐渐退化；
- 共享数据库可能造成跨模块直连；
- Graph、Application 和 Domain 职责可能混合；
- 单一部署单元未来可能出现扩缩容限制；
- Agent 可能为追求方便绕过接口。

#### Required Mitigations

后续 RFC-001 必须明确：

- Package Boundary
- Import Rules
- Application Service Boundary
- Graph Node Boundary
- Repository Interface
- Dependency Injection
- Test Architecture
- Architecture Tests
- Future Extraction Boundary

#### Decision Boundary

本 Decision 已确认：

1. MVP 采用 Modular Monolith First；
2. 当前不采用 Multi-service First；
3. MVP 使用一个主要后端部署单元；
4. 项目使用一个 Git Repository；
5. 内部按业务能力和平台能力划分模块；
6. 模块之间必须通过明确接口协作；
7. 不允许模块任意访问其他模块内部实现；
8. 共享数据库实例不代表共享数据所有权；
9. Domain 不依赖具体框架或基础设施；
10. 保留未来服务提取能力；
11. 服务拆分必须由可验证的规模、组织、安全、性能或可靠性需求触发；
12. 当前决定不选择数据库、ORM、Web Framework 或部署平台。

本 Decision 尚未确认：

- 正式后端语言；
- 正式目录结构；
- 具体 Domain、Application、Infrastructure、Interface 分层；
- LangGraph 所属层；
- Graph Node 是否可以直接访问 Repository；
- Skill 的代码形态；
- Repository Interface 位置；
- Repository Implementation 位置；
- Dependency Injection；
- Configuration Management；
- Test Layering；
- API 和 Worker 接入方式；
- Production Database；
- ORM；
- Deployment Platform。

### DQ-02：Backend Language and LangGraph Binding

**Status:** `PROPOSED`

下一轮优先讨论：

- Python 是否适合作为正式后端语言；
- 是否因 LangGraph 而绑定 Python；
- Python 与 TypeScript 的业务和工程权衡；
- API、Worker 和数据任务是否统一语言；
- 是否允许前端独立使用 TypeScript；
- 是否保留未来多语言服务边界；
- Python 版本策略；
- 语言选择是否构成部署承诺。

在 RFC-001-DQ-02 被用户明确接受前：

- 不创建正式生产代码；
- 不建立正式 Python Package；
- 不将 Spike Python 代码迁移为生产代码；
- RFC-001 保持 `DRAFTING`。

---

## Open Questions

1. DQ-02：正式后端语言是否采用 Python，以及语言决策与 LangGraph 的绑定边界。
2. 目录结构：业务模块与平台模块的具体 Package 层级。
3. Graph Node 是否允许直接调用 Repository / Application Service。
4. Dependency Injection 机制选择。
5. Configuration Management 策略。
6. Test Architecture 分层。
7. 是否需要 Architecture Tests（如 import-linter）。
8. API / Worker / CLI 等接入方式的边界。
9. 未来服务提取的具体接口形态。

---

## Related Sessions

- session-002-agent-workflow-reliability-and-technical-capabilities.md（RFC Planning Phase）

## Related Decisions

- DEC-001：业务价值优先
- DEC-011：Deterministic Workflow Control
- DEC-015：Contract-based Skills
- DEC-020：MVP Skills Scope
- DEC-021：不采用 Multi-Agent 主架构
- DEC-023：LangGraph StateGraph
- DEC-024：Versioned Domain State
- DEC-033：Runtime Reliability
- DEC-034：Technical Spike and Readiness Gate
- DEC-038：Dependency-driven RFC Governance

## Related Specifications

- specs/workflow/workflow-state-specification
- specs/runtime/workflow-runtime-failure-recovery-retry-and-observability
- architecture/system-architecture

## Related Spike Evidence

- Spike-001（LangGraph Runtime and Recovery）
