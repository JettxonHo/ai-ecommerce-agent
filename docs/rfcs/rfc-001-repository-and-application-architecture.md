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

**Status:** `ACCEPTED`

#### Question

MVP 与首个生产版本的正式后端语言是否采用 Python？前端是否采用 TypeScript？LangGraph 与业务核心层如何解耦？

#### Decision

AI Ecommerce Agent 的 MVP 与首个生产版本采用：

```text
Production Backend Language:
Python

Backend Version Baseline:
Python 3.13

Frontend Language:
TypeScript

Backend Language Strategy:
Single-language backend for MVP
```

正式关系为：

```text
TypeScript Web Frontend
↓
Versioned API Contract
↓
Python Backend
├── Interface Layer
├── Application Layer
├── Domain Layer
├── Workflow Orchestration
├── Skill Runtime
├── Retrieval Runtime
└── Infrastructure
```

当前不采用 Python 与 TypeScript 混合后端。

#### Backend Language Boundary

MVP 后端默认统一使用 Python，覆盖：

```text
Backend API
Application Services
Domain Model
Workflow Runtime
Skill Runtime
Retrieval Runtime
Source Processing
Background Jobs
Evaluation Jobs
Maintenance CLI Tools
```

使用统一后端语言的目的包括：

- 降低 Modular Monolith 内部的通信复杂度；
- 保持 API、Application、Workflow 和 Repository 在同一运行时；
- 避免 Human Review Submit 与 Workflow Resume 跨语言调用；
- 降低事务、错误和 Idempotency 的跨进程协调成本；
- 延续 Spike-001 已验证的 Python Runtime 行为；
- 降低单人或小团队维护成本。

#### Frontend Language Boundary

正式 Web Frontend 使用：

```text
TypeScript
```

前端不属于 Python 后端 Package。

前后端通过正式版本化契约协作，例如：

```text
OpenAPI
JSON Schema
Generated Client Types
Versioned Request and Response Contracts
Error Code Registry
```

具体 API Framework、Schema Generator 和前端 Framework 尚未确认。

#### No Mixed Backend for MVP

当前拒绝以下初始结构：

```text
TypeScript API Backend
+
Python Workflow Runtime
```

或：

```text
TypeScript Review Service
+
Python LangGraph Service
+
Cross-language RPC
```

主要原因：

- 与 Modular Monolith First 增加不必要张力；
- Human Review 事务和 Resume 需要跨语言协议；
- Idempotency、错误映射和 Trace 被拆散；
- 增加两套构建、测试、部署和依赖体系；
- 当前没有独立服务边界或扩缩容证据；
- 不会直接提升 MVP 的业务价值。

该拒绝只针对 MVP 后端，不表示未来永远不能引入其他语言。

#### LangGraph Language Boundary

生产 Workflow Runtime 使用：

```text
Python LangGraph Implementation
```

正式逻辑关系为：

```text
We choose Python as the backend language
therefore the Workflow Runtime uses Python LangGraph
```

而不是：

```text
LangGraph forces all product code to depend on LangGraph
```

LangGraph 是后端语言选择的一个工程因素，但不是唯一原因，也不应进入业务核心层。

#### Domain Layer Boundary

Domain Layer 不得依赖 LangGraph。

Domain Package 中不得出现：

```python
from langgraph...
```

Domain 负责：

- Business Entities；
- Value Objects；
- Business Rules；
- Version Rules；
- Evidence Rules；
- Review Rules；
- Strategy Rules；
- Invalidation Rules；
- Domain Validation。

Domain 必须能够在不安装、不初始化、不运行 LangGraph 的情况下进行 Unit Test。

Domain 同样不得依赖：

- Web Framework；
- ORM；
- 具体 Database Driver；
- Model SDK；
- Vector Database SDK；
- Message Queue SDK；
- Checkpoint Backend；
- Observability Provider。

#### Application Layer Boundary

Application Service 负责：

- Use Case；
- Command and Query；
- Transaction Coordination；
- Repository Interface 调用；
- Provider Interface 调用；
- Business Validation；
- Business Commit；
- Idempotency Coordination；
- Audit Coordination。

Application Service 不得要求调用方传入：

```text
LangGraph State
StateSnapshot
Checkpoint Object
Command(resume=...)
LangGraph Runtime Context
```

Application Service 接收业务级输入，例如：

```text
SubmitReviewCommand
ApproveStrategyCommand
GenerateFactVersionCommand
GenerateMarketingBriefCommand
```

并返回业务级 Result 或 Error。

#### Orchestration Boundary

LangGraph 位于：

```text
Orchestration / Workflow Runtime Boundary
```

推荐关系：

```text
LangGraph Node
↓
calls
↓
Application Service
↓
uses
↓
Domain + Repository / Provider Interfaces
```

LangGraph Node 主要负责：

- 从 Graph State 读取 ID 和运行引用；
- 构造业务 Command；
- 调用 Application Service；
- 将返回的 Version ID 和 Stage Status 写回 Graph State；
- 进行确定性路由；
- 调用 Interrupt；
- 处理 Workflow Retry、Resume 和 Checkpoint 协调。

LangGraph Node 不拥有：

- Domain Rule；
- Business Transaction；
- Current Truth 写入规则；
- Evidence Link 事务；
- Review Validation；
- Idempotency 规则；
- Invalidation 规则；
- Audit 规则。

#### Framework Replacement Boundary

系统必须允许未来替换 Workflow Engine，例如：

```text
LangGraph
Temporal
Custom State Machine
Queue Worker
Other Workflow Runtime
```

替换时主要影响：

```text
Orchestration Layer
Runtime Adapter
Checkpoint Adapter
Worker Integration
```

不应要求重写：

- Domain；
- Application Services；
- Business Validators；
- Repository Interfaces；
- Skill Contracts；
- Evidence Rules；
- Human Review Business Rules。

#### Python Version Baseline

正式后端基线采用：

```text
Python 3.13
```

建议项目级版本约束：

```text
Python >=3.13,<3.14
```

理由：

- Spike-001 已在 Python 3.13 环境完成验证；
- LangGraph 和 Checkpoint 行为已有验证证据；
- 当前没有必须采用更高 Minor Version 的业务需求；
- 保持与 Spike Evidence 的工程连续性；
- 减少 RFC 和初始生产实现中的变量。

#### Version Pinning Boundary

建议通过以下文件表达 Python 版本要求：

```text
.python-version
pyproject.toml
uv.lock
```

开发环境固定到 Python 3.13 系列。

生产构建或镜像应固定到明确 Patch Version，例如：

```text
3.13.x
```

具体 Patch Version 尚未在本 Decision 中锁定。

Patch 升级可以通过：

```text
Dependency Compatibility Test
Full Test Suite
Normal Pull Request Review
```

完成，一般不需要新 RFC。

#### Minor and Major Runtime Upgrade

从 Python 3.13 升级到未来 Minor Version，例如：

```text
Python 3.14
Python 3.15
```

必须至少经过：

- Dependency Compatibility；
- LangGraph Compatibility；
- Checkpointer Compatibility；
- Full Test Suite；
- Runtime and Deployment Verification；
- Migration Note；
- Pull Request Review。

若升级改变：

- 并发模型；
- Worker 模型；
- Deployment；
- Runtime Isolation；
- Security Boundary；

则必须补充 RFC 或正式技术 Decision。

#### Frontend and Backend Contract

Python 与 TypeScript 不直接共享业务源码。

允许共享或生成的是：

```text
OpenAPI Schema
JSON Schema
Generated TypeScript Client
Generated Request and Response Types
Enum Registry
Error Code Registry
```

不得依赖人工在 Python 和 TypeScript 两边重复维护业务 Contract，而没有自动校验机制。

具体 Contract Generation 和 API Versioning 由后续 RFC 决定。

#### Future Polyglot Boundary

未来允许特定独立能力采用其他语言，但必须满足明确触发条件。

潜在例子：

- 高吞吐 Source Parser；
- Media Processing Worker；
- Browser Automation Service；
- 独立 Retrieval Service；
- 特殊数据处理任务。

至少需要一种可验证触发条件：

- Python 存在可测量性能瓶颈；
- 关键 SDK 只在其他语言中可靠；
- 模块已有稳定远程接口；
- 模块需要独立扩缩容；
- 独立团队负责该模块；
- 安全或部署要求物理隔离；
- 该能力需要服务多个产品。

不得仅因为个人语言偏好引入第二种后端语言。

#### Spike Code Boundary

Spike-001 中的 Python 代码：

```text
Validated Architecture Evidence
```

不是：

```text
Production Application Code
```

不得直接：

- 将 Spike Package 移动到正式生产目录；
- 将临时 SQLite Schema 视为正式 Schema；
- 将 ScriptedModelProvider 视为生产 Model Runtime；
- 将 MockRetrievalRuntime 视为生产 Retrieval；
- 将 Local JSONL Trace 视为生产 Observability；
- 将 Spike Graph 改名后作为正式 Graph。

正式代码必须在 RFC-001 完成，并满足后续 RFC Gate 后重新建立。

#### Production Technology Boundary

本 Decision 没有确认：

- FastAPI；
- Django；
- Flask；
- Pydantic；
- SQLAlchemy；
- PostgreSQL；
- Redis；
- Celery；
- Temporal；
- Docker；
- Kubernetes；
- LangSmith；
- OpenTelemetry；
- Cloud Provider；
- Deployment Platform。

确认 Python 不自动接受上述技术。

#### Trade-offs

Positive：

- 延续 Spike-001 的验证证据；
- 降低后端运行时数量；
- 减少跨语言事务和错误协议；
- API、Workflow、Skill 和 Retrieval 可在同一应用中协作；
- 更适合当前 Modular Monolith；
- 更适合单人或小团队；
- 保留 TypeScript 前端的 Web 开发优势；
- 通过分层避免 LangGraph 渗透业务核心。

Risks：

- Python 静态类型约束弱于部分 TypeScript 工作流；
- 前后端需要严格 Schema 同步；
- Agent 可能直接在 Domain 中 Import LangGraph；
- Application Service 可能泄漏 Graph State；
- Spike 代码可能被误用为生产代码；
- 未来团队语言结构可能发生变化。

#### Required Mitigations

后续 RFC-001 必须明确：

- Package Import Rules；
- Architecture Tests；
- Domain Framework Independence；
- Application Command and Result Contracts；
- Orchestration Adapter Boundary；
- API Schema Generation；
- Type Checking；
- Test Layering；
- Production and Spike Physical Isolation。

#### Decision Boundary

本 Decision 已确认：

1. MVP 正式后端统一使用 Python；
2. 后端版本基线为 Python 3.13；
3. 建议项目版本约束为 `>=3.13,<3.14`；
4. 正式前端使用 TypeScript；
5. MVP 不采用双语言后端；
6. API、Application、Workflow、Skill、Retrieval 和 Background Jobs 默认使用 Python；
7. Workflow Runtime 使用 Python LangGraph；
8. Domain Layer 不依赖 LangGraph；
9. Application Service 不依赖 Graph State 或 Checkpoint；
10. LangGraph 位于 Orchestration / Runtime Boundary；
11. Graph Node 通过 Application Service 执行业务 Use Case；
12. 前后端通过正式 Schema Contract 协作；
13. Python 与 TypeScript 不直接共享业务源码；
14. 未来允许在明确服务或 Adapter 边界引入其他语言；
15. 引入其他语言必须由可验证需求触发；
16. Patch Version 可通过测试和普通 PR 更新；
17. Spike Python 代码不得直接成为生产代码；
18. 本 Decision 不选择 Web Framework、数据库、ORM、Worker、Queue 或部署平台。

本 Decision 尚未确认：

- 正式 Repository 和 Package Directory；
- 具体分层目录；
- API Framework；
- Schema Library；
- Dependency Injection；
- Configuration Library；
- Type Checker；
- Linter；
- ORM；
- Database；
- Worker；
- Queue；
- Checkpointer；
- Deployment Platform；
- Frontend Framework。

---
### DQ-03：Repository and Package Directory Structure

**Status:** `ACCEPTED`

#### Question

项目应采用怎样的代码仓结构、应用根目录与后端 Package 目录结构？业务模块、平台能力、编排、入口与依赖装配如何组织？

#### Decision

Repository 采用：

```text
Single Repository
+
Multi-project Layout
```

正式应用位于根目录：

```text
apps/
```

概念结构：

```text
AI Ecommerce Agent/
├── AGENTS.md
├── README.md
│
├── apps/
│   ├── backend/
│   └── web/
│
├── contracts/
├── docs/
├── spikes/
├── prototypes/
├── scripts/
├── tooling/
└── .github/
```

具体目录只在存在真实文件和已授权工作时创建，不得批量制造空目录。

#### Application Roots

**Python Backend**

正式 Python 后端位于：

```text
apps/backend/
```

生产 Python 源码唯一合法根路径：

```text
apps/backend/src/ai_ecommerce_agent/
```

正式 Python Package 名：

```text
ai_ecommerce_agent
```

**TypeScript Frontend**

正式 TypeScript Web Frontend 位于：

```text
apps/web/
```

本 Decision 不选择具体前端 Framework。

**Shared Contracts**

前后端正式契约位于：

```text
contracts/
```

概念结构可以包括：

```text
contracts/
├── openapi/
├── json-schema/
└── error-codes/
```

具体 Contract Generation、Schema Library 与 API Versioning 由后续 RFC 决定。

#### Python Package Layout

正式后端采用：

```text
src Layout
```

建议结构：

```text
apps/backend/
├── pyproject.toml
├── uv.lock
├── .python-version
├── README.md
│
├── src/
│   └── ai_ecommerce_agent/
│
├── tests/
├── migrations/
└── scripts/
```

采用 `src/` Layout 的目的：

- 避免测试意外从 Repository Working Directory 直接 Import；
- 验证 Package 安装和 Import 配置；
- 降低本地环境与部署环境不一致；
- 提前暴露缺失依赖和 Package 配置错误；
- 明确生产源码唯一根目录。

#### Backend Package Organization

正式后端采用：

```text
Business Capability Modules First
+
Independent Platform Capabilities
+
Dedicated Orchestration
+
Explicit Entrypoints
+
Central Composition Root
```

推荐概念结构：

```text
apps/backend/src/ai_ecommerce_agent/
├── modules/
├── platform/
├── orchestration/
├── entrypoints/
├── bootstrap/
└── shared_kernel/
```

该结构是正式 Architecture Contract，但本次任务不得直接创建生产目录。

#### Business Capability Modules

业务能力位于：

```text
modules/
```

概念模块包括：

```text
modules/
├── product_intake/
├── customer_insight/
├── product_positioning/
├── human_review/
├── marketing_brief/
├── xiaohongshu_adapter/
└── source_evidence/
```

具体模块边界可在后续 RFC 或 Spec 中细化，但不得违背已接受的 MVP Skill 和 Workflow Decisions。

**Internal Business Module Structure**

单个业务模块内部采用：

```text
domain/
application/
infrastructure/
public.py
```

概念示例：

```text
modules/
└── product_positioning/
    ├── domain/
    ├── application/
    ├── infrastructure/
    ├── public.py
    └── __init__.py
```

不存在实际内容时，不要求创建对应空目录或空文件。

**Domain Directory**

`domain/` 用于：

- Entity；
- Value Object；
- Domain Service；
- Business Rule；
- Domain Error；
- Domain Validation；
- Version Rule；
- Evidence Rule；
- Review Rule；
- Invalidation Rule。

Domain 不得依赖：

- LangGraph；
- Web Framework；
- ORM；
- Database Driver；
- Model SDK；
- Vector Database SDK；
- Message Queue SDK；
- Checkpoint Backend；
- Observability Provider。

**Application Directory**

`application/` 用于：

- Command；
- Query；
- Application Service；
- Port；
- Result；
- Use Case；
- Transaction Coordination；
- Idempotency Coordination；
- Audit Coordination。

Application 可以依赖本模块 Domain。

Application 不得依赖具体 Infrastructure Implementation。

**Infrastructure Directory**

`infrastructure/` 用于：

- Repository Implementation；
- Persistence Adapter；
- External Provider Adapter；
- ORM Mapping；
- Database Integration；
- Third-party SDK Adapter。

Infrastructure 负责实现 Application 或 Domain 定义的 Port。

具体 Database、ORM 和 Adapter 技术不在本 Decision 中选择。

**Module Public Contract**

每个业务模块使用明确的公开表面，例如：

```text
public.py
```

其可以导出：

- Public Command；
- Public Query；
- Application Service Protocol；
- Public Result；
- Public Error；
- Published Application Event。

其他模块不得直接访问目标模块的：

```text
infrastructure/
internal domain implementation
private repository implementation
```

模块间调用必须通过公开 Application Contract 或正式 Port。

#### Platform Capabilities

平台能力位于：

```text
platform/
```

概念结构：

```text
platform/
├── persistence/
├── workflow_runtime/
├── model_runtime/
├── retrieval_runtime/
├── observability/
├── configuration/
├── identity/
└── messaging/
```

平台模块不等于业务模块。其负责多个业务能力共享的技术设施和 Adapter，但不得拥有业务规则。

具体平台技术由后续 RFC 决定。

#### Orchestration Boundary

LangGraph 与跨模块 Workflow 位于：

```text
orchestration/
```

概念结构：

```text
orchestration/
├── workflows/
└── adapters/
    └── langgraph/
```

跨模块主流程，例如：

```text
Product Intake
→ Customer Insight
→ Product Positioning
→ Human Review
→ Marketing Brief
→ Xiaohongshu Adapter
```

属于 Application-level Orchestration，不属于单个业务模块内部。

`orchestration/` 可以依赖：

- 各业务模块的公开 Application Contract；
- Workflow Runtime Platform；
- Runtime-level Types。

不得：

- 实现 Domain Rule；
- 拥有 Business Transaction；
- 直接更新 Current Truth；
- 直接使用其他模块的 Repository Implementation；
- 直接写 ORM Model；
- 将完整 Domain Object 放入 Graph State。

Graph Node 的完整职责已由 RFC-001-DQ-04 确认。

#### Entrypoints

外部入口位于：

```text
entrypoints/
├── api/
├── worker/
└── cli/
```

**API Entrypoint**

未来负责：

- HTTP Route；
- Request Schema；
- Response Schema；
- Authentication Adapter；
- API Error Mapping；
- 请求级依赖入口。

不得放置 Domain Rule 或业务事务。

**Worker Entrypoint**

未来负责：

- Background Job Consumer；
- Scheduled Job；
- Queue Handler；
- Workflow Worker Entry。

是否独立进程、是否使用 Queue，尚未决定。

**CLI Entrypoint**

未来负责：

- 管理命令；
- 数据检查；
- Recovery 入口；
- 本地维护任务；
- 开发辅助执行。

CLI 不得绕过 Application Service 直接修改业务数据。

#### Bootstrap and Composition Root

依赖装配位于：

```text
bootstrap/
```

概念职责：

- 加载 Configuration；
- 创建 Application；
- 创建数据库连接；
- 创建 Repository Implementation；
- 创建 Provider Adapter；
- 装配 Workflow；
- 装配 API、Worker、CLI；
- 管理 Application Lifecycle。

Bootstrap 是少数允许同时了解：

- Application Port；
- Infrastructure Implementation；
- Orchestration；
- Entrypoint；

的区域。

具体 Dependency Injection 技术尚未选择。

#### Shared Kernel

允许保留严格受限的：

```text
shared_kernel/
```

只允许放置：

- 通用 Identifier 类型；
- Clock Protocol；
- 无业务语义的 Result；
- 通用 Error Base；
- 基础 Typing Utility。

不得放置：

- 具体业务规则；
- Product Positioning；
- Human Review；
- Evidence Business Rule；
- Marketing Brief Schema；
- Repository Implementation；
- LangGraph State；
- ORM Base Model；
- 各业务模块为了方便而共享的任意代码。

具有明确业务所有权的概念必须属于对应业务模块。

#### Test Layout

正式后端测试位于：

```text
apps/backend/tests/
```

测试类别：

```text
tests/
├── unit/
├── integration/
├── contract/
├── architecture/
└── e2e/
```

**Unit Tests**

验证：

- Domain Rule；
- Value Object；
- Application Service；
- Validator；
- 纯函数；
- 确定性业务逻辑。

不依赖：

- 网络；
- 真实数据库；
- LangGraph Runtime；
- 真实模型。

**Integration Tests**

验证：

- Repository Implementation；
- Transaction；
- Database；
- Checkpointer；
- Provider Adapter；
- Retrieval Adapter；
- Workflow Runtime Integration。

**Contract Tests**

验证：

- API Contract；
- Provider Contract；
- Repository Contract；
- Generated Schema；
- 前后端 Contract；
- Adapter Compliance。

**Architecture Tests**

验证：

- Domain 不 Import LangGraph；
- Domain 不 Import Infrastructure；
- Application 不 Import Infrastructure Implementation；
- 模块不 Import 其他模块内部目录；
- Production 不 Import `spikes/`；
- Production 不 Import `prototypes/`；
- Graph Node 不直接 Import ORM Model；
- Entrypoint 不包含 Domain Rule；
- Import Boundary 与 Package Boundary。

具体 Architecture Test 工具尚未选择。

**End-to-End Tests**

验证：

- 完整 Workflow；
- Human Review；
- Retry 和 Recovery；
- API 到业务结果；
- 关键 Portfolio Demo 场景。

**Test Organization**

Unit Test 大体镜像生产模块，例如：

```text
tests/unit/modules/product_positioning/
tests/unit/modules/human_review/
```

Integration、Contract、Architecture 与 E2E 按验证场景组织，例如：

```text
tests/integration/persistence/
tests/integration/workflow_runtime/
tests/architecture/test_import_boundaries.py
tests/e2e/test_marketing_brief_workflow.py
```

不要求每个源码文件机械对应一个同名测试文件。

#### Database Migrations

正式数据库 Migration 位于：

```text
apps/backend/migrations/
```

不放入可 Import 的生产 Python Package。

具体 Migration Tool、Database 和 Schema Strategy 由 RFC-002 决定。

#### Configuration and Secret Boundary

目录层面允许未来使用：

```text
apps/backend/.env.example
apps/backend/src/ai_ecommerce_agent/bootstrap/settings.py
```

规则：

- `.env.example` 只能包含变量名称和非敏感示例；
- `.env`、Secret、Token 不得提交；
- Domain 和 Application 不直接读取环境变量；
- Configuration 由 Bootstrap 加载并注入。

具体 Configuration Library 尚未决定。

#### Spike and Prototype Isolation

技术验证继续位于 Repository 根目录：

```text
spikes/
prototypes/
```

正式规定：

```text
spikes/
≠
apps/backend/src/
```

生产 Package 禁止：

```python
from spikes...
from prototypes...
```

允许关系：

```text
Spike Evidence
→ informs RFC and Production Tests
→ production implementation is rebuilt under accepted architecture
```

禁止关系：

```text
Spike Source
→ rename or move
→ Production Source
```

现有 Spike-001 继续作为 Architecture Evidence 保存。

#### Repository-level Directories

`docs/`

继续保存：

- Decisions；
- Specs；
- RFCs；
- Architecture；
- Readiness；
- Roadmap；
- Traceability；
- Sessions。

`scripts/`

保存 Repository 级辅助脚本，例如：

- 文档校验；
- Repository 检查；
- Schema Generation Entry；
- 本地开发辅助。

业务运行脚本应优先放在所属应用内部。

`tooling/`

保存实际存在的 Repository 级工程工具，例如：

- Architecture Test 配置；
- Schema Generation；
- CI 辅助；
- Lint 和 Formatting Integration。

不得在没有实际工具时创建空目录。

`.github/`

保存：

- Workflow；
- Issue Template；
- Pull Request Template；
- Repository Automation。

具体 CI 方案尚未决定。

#### Import Boundary

当前确认的方向性规则：

```text
entrypoints
↓
bootstrap / orchestration
↓
application public contracts
↓
domain
```

Infrastructure：

```text
infrastructure
→ implements
→ application or domain ports
```

允许：

```text
module.application → module.domain
module.infrastructure → module.application ports
orchestration → module.public
entrypoints → bootstrap
bootstrap → application + infrastructure + orchestration
```

禁止：

```text
domain → application
domain → infrastructure
domain → orchestration
domain → entrypoints

application → infrastructure implementation
application → LangGraph
application → API framework

module A → module B infrastructure
module A → module B private implementation

production → spikes
production → prototypes
```

完整职责和依赖规则已由 RFC-001-DQ-04 确认。

#### Cross-module Data Boundary

模块之间不得使用数据库表作为隐式 API。

即使共享同一 Database Instance，也不得：

- 直接写入其他模块的内部表；
- 通过其他模块 ORM Model 修改数据；
- 绕过 Application Contract；
- 直接调用其他模块 Repository Implementation。

跨模块读取和写入必须通过：

- Public Application Contract；
- Application Port；
- 明确 Query Service；
- 用户后续确认的 Published Application Event。

#### Directory Creation Boundary

接受本 Decision 不等于立即创建生产目录。

本阶段只授权：

- 更新 RFC；
- 更新 Architecture Baseline；
- 更新 Traceability；
- 更新 RFC Register；
- 记录未来 Architecture Test 要求。

暂不授权：

- 创建 `apps/backend/src/ai_ecommerce_agent/`；
- 创建正式 Python Package；
- 批量创建空目录；
- 创建 Production Skeleton；
- 迁移 Spike 代码；
- 创建业务模块源码；
- 创建数据库 Migration；
- 创建 API、Worker 或 CLI 实现。

正式 Skeleton 必须等待：

```text
RFC-001 = ACCEPTED
+
Foundation Work explicitly authorized
```

#### Rejected Alternatives

**Technology-layer-first Root Layout**

未选择：

```text
domain/
application/
infrastructure/
interfaces/
```

作为整个应用的顶层主要组织方式。

原因：

- 单个业务能力被拆散；
- 模块所有权不清晰；
- 随业务增长跨目录跳转增加；
- 不利于未来模块提取；
- Coding Agent 修改范围难以限定。

技术层仍保留在业务模块内部。

**Flat Application Layout**

拒绝：

```text
app.py
services.py
repositories.py
models.py
utils.py
```

原因：

- 无法体现模块边界；
- 容易演化为公共代码堆积；
- LangGraph、API、事务和业务规则容易混合；
- 无法通过路径约束 Agent。

**Multi-repository Initial Layout**

当前不采用多个 Repository。

原因：

- 与 Modular Monolith First 不一致；
- 增加版本协调和本地开发复杂度；
- 当前没有独立服务和团队边界。

#### Trade-offs

Positive：

- 正式生产代码路径明确；
- 业务能力代码集中；
- 平台、编排和入口职责可分离；
- 更利于 Coding Agent 限定修改范围；
- 支持未来模块提取；
- Spike 与生产代码物理隔离；
- Architecture Tests 可以验证边界；
- 前后端契约有独立位置。

Risks：

- 模块内部结构可能机械复制；
- `platform/` 可能成为技术垃圾场；
- `shared_kernel/` 可能膨胀；
- `public.py` 可能暴露过多内部细节；
- 跨模块调用可能绕过公开接口；
- Orchestration 可能吸收业务逻辑；
- Agent 可能提前创建大量空目录。

#### Required Mitigations

后续必须明确：

- Domain、Application、Infrastructure、Entrypoint 与 Orchestration 职责；
- Port Ownership；
- Transaction Ownership；
- Public Contract Rules；
- Cross-module Call Rules；
- Architecture Test Rules；
- Empty Directory Prohibition；
- Production Skeleton Authorization Gate。

#### Decision Boundary

本 Decision 已确认：

1. Repository 使用单仓库、多项目布局；
2. 正式应用位于 `apps/`；
3. Python 后端位于 `apps/backend/`；
4. TypeScript 前端位于 `apps/web/`；
5. 共享正式契约位于 `contracts/`；
6. 后端采用 `src/` Layout；
7. 正式 Python Package 名为 `ai_ecommerce_agent`；
8. 生产源码唯一根路径为 `apps/backend/src/ai_ecommerce_agent/`；
9. 后端以业务能力模块优先组织；
10. 业务模块内部使用 `domain/application/infrastructure/public` 边界；
11. 平台能力位于 `platform/`；
12. LangGraph 与跨模块 Workflow 位于 `orchestration/`；
13. API、Worker、CLI 位于 `entrypoints/`；
14. 依赖装配位于 `bootstrap/`；
15. `shared_kernel/` 必须最小化；
16. 后端测试分为 unit、integration、contract、architecture、e2e；
17. Unit Test 大体镜像生产模块；
18. Migration 位于 `apps/backend/migrations/`；
19. Spike 和 Prototype 保持在根目录独立区域；
20. Production 禁止 Import Spike 或 Prototype；
21. 模块间通过公开 Application Contract 协作；
22. 数据库表不能作为隐式模块 API；
23. Architecture Tests 必须验证 Import Boundary；
24. 目录按实际文件按需创建；
25. 当前不选择 API Framework、Database、ORM、Queue、前端 Framework 或部署平台；
26. 当前不创建生产 Skeleton，不迁移 Spike 代码。

本 Decision 尚未确认：

- Domain、Application、Infrastructure、Entrypoint 的完整职责；
- Port 应由 Domain 还是 Application 定义；
- Transaction 在哪一层开始；
- Graph Node 是否可以直接访问 Repository Interface；
- API Handler 是否可以调用 Domain；
- 跨模块同步调用和事件规则；
- Dependency Injection 形式；
- Configuration 技术；
- Architecture Test 工具；
- API Framework；
- Database；
- ORM；
- Worker；
- Queue；
- Deployment Platform。

---

### DQ-04：Layer Responsibilities, Transaction Ownership and Dependency Rules

**Status:** `ACCEPTED`

#### Question

Domain、Application、Infrastructure、Entrypoint、Orchestration 与 Bootstrap 的正式职责、依赖方向、Port 所有权、事务边界、Graph Node 与 Repository 边界、跨模块协作规则与 Architecture Test 要求是什么？

#### Decision

正式调用方向：

```text
Entrypoint / Orchestration
        ↓
Application
        ↓
Domain
```

Infrastructure 负责实现 Application 定义的技术接口：

```text
Application
→ declares Ports
Infrastructure
→ implements Ports
Bootstrap
→ assembles implementations
```

核心原则：

> 业务规则向内保持纯净；框架、数据库和外部服务只能通过明确的 Adapter 与 Port 接入。

#### Domain Layer

Domain 是纯业务核心，负责：

- Entity；
- Value Object；
- Aggregate 和业务不变量；
- Domain Service；
- Business Rule；
- Domain Validation；
- Domain Error；
- Domain Event；
- Version Rule；
- Evidence Classification Rule；
- Human Review Rule；
- Invalidation Rule。

Domain 允许依赖：

- Python Standard Library；
- 本模块 Domain 内部代码；
- 严格受限的 `shared_kernel` 基础类型。

Domain 不得依赖：

- Application；
- Infrastructure；
- Entrypoint；
- Orchestration；
- LangGraph；
- Web Framework；
- ORM；
- Database Driver；
- Repository Implementation；
- Model SDK；
- Vector Database SDK；
- Queue SDK；
- Checkpoint Backend；
- Observability Provider；
- Environment Variable。

Domain 必须能够在没有数据库、网络、LangGraph 和真实模型的条件下完成 Unit Test。

#### Application Layer

Application 负责执行完整业务 Use Case，包括：

- Command；
- Query；
- Application Service；
- Use Case Coordination；
- Repository 和 Provider Port；
- Unit of Work Port；
- Transaction Coordination；
- Domain Rule 调用；
- Idempotency Coordination；
- Current Truth 更新协调；
- Evidence Link 协调；
- Audit Coordination；
- Application Result；
- Application Error Mapping。

概念流程：

```text
Application Command
↓
Validate
↓
Begin Unit of Work
↓
Load Current Business State
↓
Execute Domain Rules
↓
Call Repository / Provider Ports
↓
Persist Domain Version
↓
Update Current Truth
↓
Write Evidence / Audit / Idempotency
↓
Commit or Rollback
```

Application 不得依赖：

- 具体 Repository Implementation；
- ORM Model；
- Database Session；
- LangGraph State；
- Checkpoint Object；
- Web Request 或 Response；
- 具体 Model SDK；
- 具体 Retrieval SDK。

#### Port Ownership

Repository、Provider、Unit of Work、Clock、ID Generator 和 Event Publisher 等 Port，默认由 **Application Layer** 定义。

推荐位置：

```text
modules/<module>/application/ports.py
```

正式关系为：

```text
Application defines the capability it needs
Infrastructure implements that capability
Bootstrap injects the implementation
```

只有真正属于纯业务抽象的 Policy 才可以定义在 Domain。

数据库 Repository、LLM Provider、Retrieval Provider、Unit of Work 和外部 Event Publisher 不属于 Domain。

#### Infrastructure Layer

Infrastructure 负责技术实现，包括：

- Repository Implementation；
- ORM Mapping；
- Database Integration；
- Unit of Work Implementation；
- Model Provider Adapter；
- Retrieval Adapter；
- File Storage Adapter；
- Queue Adapter；
- Checkpoint Adapter；
- Observability Adapter；
- Third-party SDK Integration。

Infrastructure 可以依赖：

- Application Ports；
- Domain Types；
- Platform Infrastructure；
- 第三方技术 SDK。

Infrastructure 不得：

- 定义业务规则；
- 改变 Domain Invariant；
- 在 Repository 中隐藏完整业务流程；
- 自行更新 Current Truth；
- 自行决定 Review Approval；
- 自行执行 Downstream Invalidation；
- 在 ORM Hook 中执行核心业务逻辑；
- 直接调用其他业务模块的内部 Infrastructure；
- 绕过 Application Service 提交业务状态。

Repository Implementation 的职责限于：

```text
Load
Persist
Query
Map
```

不得承担：

```text
Approve
Invalidate
Resume
Select Strategy
Generate Business Decision
```

#### Transaction Ownership

业务事务由 **Application Use Case** 拥有。

正式规则：

> 一个 Application Command 对应一个清晰、有限且可重试的业务事务边界。

Entrypoint 不开启或提交业务事务。
Graph Node 不开启或提交业务事务。
Repository 不得在每次 `save()` 中自行 Commit。
Infrastructure 的 Unit of Work Implementation 可以提供事务技术能力，但 Commit/Rollback 时机由 Application Use Case 控制。

#### Atomic Business Commit

以下记录如果共同构成一次业务提交：

```text
Domain Version
Evidence Links
Current Truth Pointer
Stage State
Audit Record
Idempotency Record
```

必须在同一 Application Transaction 中：

```text
Commit Together
or
Rollback Together
```

不得出现：

- Domain Version 已写入，但 Current Truth 未更新；
- Current Truth 已更新，但 Evidence 未写入；
- Review 已批准，但 Idempotency Record 未记录；
- Audit 已记录成功，但业务事务实际失败。

具体持久化和事务技术由 RFC-002 决定。

#### Long-running Workflow Transaction Boundary

整个 LangGraph Workflow 不得持有一个长期数据库事务。

正确形式：

```text
Workflow Node A
→ Application Use Case A
→ Transaction A Commit
Workflow Node B
→ Application Use Case B
→ Transaction B Commit
Human Review Interrupt
Review Submit
→ Application Use Case
→ Transaction Commit
Workflow Resume
→ Next Application Use Case
```

这样才能支持：

- Interrupt；
- Resume；
- Retry；
- Recovery；
- Stage-level Rerun；
- 长时间人工等待；
- 幂等业务提交；
- 独立错误恢复。

#### Orchestration Layer

LangGraph 位于独立 **Orchestration / Workflow Adapter Layer**，其角色类似于长运行的 Application Client。

推荐关系：

```text
LangGraph Node
↓
Module Public Application Contract
↓
Application Use Case
↓
Domain + Ports
```

Orchestration 可以：

- 从 Graph State 读取 ID 和 Runtime Reference；
- 构造 Application Command；
- 调用公开 Application Service；
- 接收 Application Result；
- 将 Version ID、Stage Status 和运行引用写回 Graph State；
- 执行确定性 Workflow Routing；
- 触发 `interrupt()`；
- 协调 Retry、Resume、Cancellation；
- 记录 Runtime-level Trace。

Orchestration 不得：

- 执行 Domain Rule；
- 拥有业务事务；
- 直接调用业务 Repository；
- 直接使用 ORM Model；
- 直接更新 Current Truth；
- 直接写 Evidence Link；
- 直接执行 Review Approval；
- 直接执行 Idempotency Commit；
- 直接访问其他模块 Infrastructure；
- 将完整业务对象长期保存在 Graph State。

#### Graph Node Repository Boundary

正式决定：

```text
Graph Node Direct Business Repository Access = PROHIBITED
```

即使访问的是 Repository Interface，也会绕过：

- Application Validation；
- Transaction Boundary；
- Idempotency；
- Audit；
- Current Truth；
- Evidence Link；
- Application Error Mapping。

如果 Workflow Runtime 需要读取运行时数据，应调用：

```text
Workflow Runtime Service
Runtime Repository
```

而不是业务模块 Repository。

#### Entrypoint Layer

Entrypoint 包括：

```text
API
Worker
CLI
```

其职责是将外部协议转换为 Application Command 或 Query。

Entrypoint 可以：

- 解析输入；
- 执行协议级 Schema Validation；
- Authentication；
- Authorization；
- 构造 Command 或 Query；
- 调用 Application Service；
- 将 Result 映射为协议响应；
- 将 Application Error 映射为 HTTP、CLI 或 Worker Error；
- 添加 Correlation ID。

Entrypoint 不得：

- 直接调用 Domain Entity 完成业务流程；
- 直接调用业务 Repository；
- 直接访问 ORM Model；
- 开启或提交业务事务；
- 直接更新数据库；
- 直接调用 LangGraph 内部 Node；
- 在 Route、Worker Handler 或 CLI Command 中编写业务规则；
- 绕过 Application Service 执行恢复或管理员操作。

紧急恢复操作必须通过明确的：

```text
Recovery Application Service
```

并产生 Audit Record。

#### Bootstrap and Composition Root

Bootstrap 是集中装配具体实现的 Composition Root。

Bootstrap 可以了解：

- Application Port；
- Infrastructure Implementation；
- Orchestration Adapter；
- Entrypoint；
- Configuration；
- Application Lifecycle。

Bootstrap 负责：

- 加载 Settings；
- 创建 Database Connection；
- 创建 Unit of Work；
- 创建 Repository；
- 创建 Provider Adapter；
- 创建 Application Service；
- 创建 Workflow；
- 创建 API、Worker 和 CLI Entrypoint；
- 管理应用生命周期。

Bootstrap 不得：

- 执行业务 Use Case；
- 包含 Domain Rule；
- 成为运行时全局 Service Locator；
- 允许模块任意读取全局 Container。

#### Dependency Injection

默认采用：

```text
Constructor Injection
+
Explicit Factory Functions
+
Central Composition Root
```

不采用隐藏依赖的全局 Service Locator。

示例概念：

```python
service = SubmitReviewService(
    unit_of_work=unit_of_work,
    clock=clock,
    id_generator=id_generator,
)
```

具体 DI Framework 尚未选择，也不要求使用 DI Framework。

#### Cross-module Collaboration

模块间同步调用必须通过目标模块公开 Application Contract，例如：

```text
Module A
↓
Module B public.py
↓
Module B Application Query or Command
```

允许公开：

- Command；
- Query；
- Result；
- Public Error；
- Application Service Protocol；
- Published Application Event。

禁止：

```text
Module A
→ Module B infrastructure
Module A
→ Module B ORM model
Module A
→ Module B private repository
Module A
→ Direct SQL against Module B tables
```

跨模块调用链必须：

- 有明确所有权；
- 无循环依赖；
- 输入输出使用稳定公共 Contract；
- 不共享可变内部 Entity；
- 不泄露目标模块持久化结构。

#### Cross-module Query

默认使用：

```text
Target Module Public Query Service
```

概念关系：

```text
Consumer Module
→ Target Module Public Query
→ Target Application Query Handler
```

当前不允许通过共享数据库任意 Join 其他模块内部表。

未来独立 Read Model 必须由 RFC-002 或专门 RFC 决定其：

- 数据来源；
- 一致性；
- 同步方式；
- 权限；
- 失效规则。

#### Domain Event and Application Event

**Domain Event**：表示 Domain 已经发生的业务事实，例如：

```text
StrategyApproved
ReviewPackageSuperseded
```

Domain 可以产生 Event，但不负责通过消息系统发布。

**Application Event**：由 Application 在业务提交后发布，用于：

- 非关键副作用；
- 通知；
- 索引更新；
- 非原子跨模块处理；
- Runtime Integration。

当前初始原则：

- 核心一致性流程优先同步 Application 调用；
- 非关键副作用可以使用进程内 Application Event；
- 不将所有业务流程改为异步；
- 当前不锁定 Message Broker；
- Outbox 和消息持久化由 RFC-002 或后续 RFC 决定。

#### Error Boundary

错误类别区分为：

```text
Domain Error
Application Error
Infrastructure Error
Workflow Runtime Error
Entrypoint Protocol Error
```

转换方向：

```text
Infrastructure Error
↓ mapped by Application
Application Error
↓ mapped by Entrypoint or Orchestration
Protocol Error / Workflow Route
```

Graph Node 应根据明确 Application Error 类型决定：

- Retry；
- Pause；
- Fail；
- Manual Recovery；
- Degraded Mode。

Graph Node 不得解析 Database Driver、HTTP Client 或 SDK 的错误字符串来决定业务路由。

#### Architecture Test Requirements

未来 Architecture Tests 至少验证以下规则。

**Domain Independence**

```text
domain must not import:
- application
- infrastructure
- orchestration
- entrypoints
- langgraph
- web framework
- orm
```

**Application Independence**

```text
application must not import:
- infrastructure implementations
- entrypoints
- langgraph
- web framework
- concrete database session
```

**Infrastructure Direction**

```text
infrastructure may import:
- application ports
- domain types
- technical SDKs
infrastructure must not define:
- domain business rules
- application use cases
```

**Orchestration Boundary**

```text
orchestration may import:
- module public contracts
- workflow runtime contracts
orchestration must not import:
- module infrastructure
- ORM models
- database sessions
- private module implementation
```

**Entrypoint Boundary**

```text
entrypoints may import:
- application public contracts
- bootstrap entry factories
entrypoints must not import:
- repository implementations
- ORM models
- private domain implementation
```

**Module Boundary**

```text
module A must not import:
- module B infrastructure
- module B private domain/application files
```

**Spike Isolation**

```text
production package must not import:
- spikes
- prototypes
```

具体 Architecture Test 工具尚未选择。

#### Responsibility Matrix

| Layer | Business Rules | Transaction Ownership | Defines Ports | Implements Ports | LangGraph | Protocol Handling |
|---|---|---|---|---|---|---|
| Domain | 是 | 否 | 仅纯业务 Policy | 否 | 否 | 否 |
| Application | 协调 | 是 | 是 | 否 | 否 | 否 |
| Infrastructure | 否 | 提供技术能力 | 否 | 是 | Adapter 可有 | 否 |
| Orchestration | 否 | 否 | 否 | Workflow Adapter | 是 | Workflow |
| Entrypoint | 否 | 否 | 否 | Protocol Adapter | 不直接 | 是 |
| Bootstrap | 否 | 否 | 知道接口 | 知道实现 | 装配 | 装配 |

#### Hard Rules

```text
Domain Framework Dependency:
PROHIBITED

Application Infrastructure Implementation Dependency:
PROHIBITED

Transaction Owner:
Application Use Case

Repository Self-commit:
PROHIBITED

Graph Node Direct Business Repository Access:
PROHIBITED

Entrypoint Direct Repository Access:
PROHIBITED

Entrypoint Direct Domain Workflow:
PROHIBITED

Cross-module Internal Implementation Access:
PROHIBITED

Production Import from Spike:
PROHIBITED
```

#### Decision Boundary

本 Decision 已确认：

1. Domain 只负责纯业务模型、规则和不变量；
2. Domain 不依赖框架、数据库、LangGraph、ORM 或外部 SDK；
3. Application 负责 Use Case、Port 和业务流程协调；
4. Repository、Provider 与 Unit of Work Port 默认由 Application 定义；
5. Infrastructure 实现 Application Port；
6. Infrastructure 不得拥有业务规则；
7. 一个 Application Command 对应一个明确业务事务；
8. 业务事务由 Application Use Case 开启和提交；
9. Repository 不得自行提交独立业务事务；
10. Entrypoint 和 Graph Node 不拥有业务事务；
11. 长 Workflow 由多个短 Application Transaction 组成；
12. LangGraph Orchestration 是独立 Adapter Layer；
13. Graph Node 只能调用公开 Application Service；
14. Graph Node 默认禁止访问业务 Repository；
15. Graph Node 不直接更新 Current Truth、Evidence、Audit 或 Idempotency；
16. API、Worker 和 CLI 只负责协议转换；
17. Entrypoint 不直接调用 Domain 完成业务流程；
18. Entrypoint 不访问业务 Repository 或持久化实现；
19. Bootstrap 是 Composition Root；
20. 默认采用 Constructor Injection 和显式 Factory；
21. 不采用全局 Service Locator；
22. 跨模块调用必须经过公开 Application Contract；
23. 模块不得访问其他模块 Infrastructure 或内部表；
24. 核心一致性流程优先同步调用；
25. 非关键副作用可以通过 Application Event；
26. 当前不锁定 Message Broker；
27. Infrastructure Error 转换为 Application Error；
28. Graph Node 不解析技术错误字符串决定业务路由；
29. Architecture Tests 必须强制上述依赖边界；
30. 本 Decision 不选择 ORM、Database、API Framework、DI Framework、Event Broker 或 Deployment；
31. 本 Decision 接受后仍不授权生产实现。

本 Decision 尚未确认：

- Skill 的正式代码形态；
- Skill 与 Application Service 的关系；
- Skill 是否属于业务模块；
- Skill 是否可以直接调用 Provider Port；
- Skill 的输入输出 Contract；
- Skill 的版本管理；
- Skill 与 LangGraph Node 的映射关系；
- Configuration Management；
- API Framework；
- Database 和 ORM；
- Worker 和 Queue；
- Architecture Test 工具；
- Production Skeleton。

#### Traceability

- RFC-001-DQ-01：Modular Monolith First；
- RFC-001-DQ-02：Python Backend and LangGraph Boundary；
- RFC-001-DQ-03：Repository and Package Layout；
- DEC-011：Deterministic Workflow Control；
- DEC-015：Skill Execution Contract；
- DEC-021：Primary Agent Architecture；
- DEC-023：LangGraph StateGraph；
- DEC-024：State Separation；
- DEC-029：Human Review Contract；
- DEC-033：Runtime Reliability；
- DEC-038：RFC Governance；
- Architecture Baseline v1；
- Spike-001 Transaction and Recovery Evidence。


---

## Open Questions

1. Skill 的正式代码形态（RFC-001-DQ-05）。
2. Configuration Management。
3. API Framework。
4. Database 和 ORM。
5. Worker 和 Queue。
6. Architecture Test 工具。
7. Deployment Platform。
8. Production Skeleton Authorization Gate。

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
- DEC-035：Temporary Spike Stack
- DEC-038：Dependency-driven RFC Governance
- RFC-001-DQ-01：Modular Monolith First
- RFC-001-DQ-02：Backend Language and LangGraph Binding
- RFC-001-DQ-03：Repository and Package Directory Structure
- RFC-001-DQ-04：Layer Responsibilities and Dependency Rules

## Related Specifications

- specs/workflow/workflow-state-specification
- specs/runtime/workflow-runtime-failure-recovery-retry-and-observability
- architecture/system-architecture

## Related Spike Evidence

- Spike-001（LangGraph Runtime and Recovery）
