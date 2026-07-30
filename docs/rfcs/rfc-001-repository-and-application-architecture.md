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

### DQ-05：Skill Code Shape and Architectural Relationships

#### Question

Skill 的正式代码形态是什么？它在架构中处于什么位置、与 Application Use Case、Repository、LLM/Retrieval、LangGraph Node、事务和版本管理的关系是什么？

#### Decision

Status: ACCEPTED

Skill 是**业务模块 Application Layer 内**具有明确执行契约、可独立运行和独立评估的**无状态业务能力组件**。Application Use Case 通过 **Prepare–Execute–Commit** 协调 Skill 与业务事务：Skill 只负责**业务能力执行**（如生成、抽取、检索、评估），**不**直接访问业务 Repository、**不**拥有 Current Truth、**不**开启或提交业务事务，也**不**与 LangGraph Node 等同。

Skill 的正式代码形态落位为：

```text
modules/<module>/application/skills/<skill_slug>/
```

每个 Skill 是一个内聚单元，包含执行契约、实现、Prompt 资产与输出 Schema 的版本化组合；它不是独立 Package、不是 Domain Service、不是 Application Use Case 的同义词，也不是 Entrypoint。

#### Skill Architectural Position

Skill 属于 Application Layer，位于所属业务模块内部：

```text
modules/<module>/
└── application/
    ├── use_cases/          # Application Use Case（拥有业务事务）
    ├── services/           # Stage / Coordination Application Service
    └── skills/
        └── <skill_slug>/   # Skill（无状态业务能力组件）
            ├── contract        # Skill 输入/输出契约
            ├── implementation  # Skill 业务能力实现
            ├── prompts         # Prompt 资产（如适用）
            └── schemas         # 输出 Schema（如适用）
```

- Skill 归业务模块所有，**不**放入 shared kernel 作为通用工具；
- Skill 不是跨模块自由调用的公共服务；跨模块使用必须经过所属模块的公开 Application Contract（见 DQ-04 跨模块边界）；
- Skill 是 Application Layer 的组成，不是独立 Layer。

#### Skill Stateless Boundary

Skill 是**无状态**业务能力组件：

1. Skill 不持有跨执行的可变业务状态；
2. Skill 不读取或写入 Current Truth；
3. Skill 不持久化业务结果；
4. Skill 的输入完全由其执行契约的入参提供；
5. Skill 的输出通过 Candidate Result 返回给调用方；
6. Skill 运行所需的运行时依赖（Model Runtime、Retrieval）通过注入获得，Skill 不自行创建。

无状态不等于无依赖——Skill 依赖注入的 Port，但不拥有业务状态与持久化。

#### Prepare-Execute-Commit Model

Application Use Case 以 **Prepare–Execute–Commit** 协调 Skill 与业务事务：

```text
Prepare   —— Application Use Case 准备 Skill 输入（从 Current Truth /
             Evidence / 入参装配），并开启业务事务边界
Execute   —— 调用 Skill 执行，得到 Candidate Result（未落库的业务候选）
Commit    —— Application Use Case 校验并决定是否将 Candidate Result
             写入 Current Truth，随后提交业务事务
```

- Skill 只参与 **Execute** 阶段，产出 Candidate Result；
- 写入 Current Truth、更新 Evidence/Audit/Idempotency 由 Application Use Case 在 Commit 阶段完成；
- 因此 Skill 失败不直接导致部分业务落库；业务一致性由 Application Use Case 与 DQ-04 事务边界保证。

#### Skill Repository and Transaction Boundary

| 能力 | Skill 是否允许 |
|------|----------------|
| 直接访问业务 Repository | **PROHIBITED** |
| 读取 Current Truth | **PROHIBITED**（由 Use Case Prepare 注入输入） |
| 写入 Current Truth | **PROHIBITED** |
| 开启 / 提交业务事务 | **PROHIBITED** |
| 拥有 Current Truth | **NO** |
| 更新 Evidence / Audit / Idempotency | **PROHIBITED**（由 Use Case 负责） |

```text
Skill Direct Business Repository Access:
PROHIBITED

Skill Business Transaction Ownership:
NO
```

Skill 所需数据由 Application Use Case 在 Prepare 阶段以输入契约形式注入；Skill 不反向查询业务持久层。

#### Skill Provider Access Boundary

Skill 可以调用 Provider 能力，但**只能**通过 Application 定义的抽象 Port：

1. Skill 通过注入的 **ModelRuntimePort** 调用 LLM 能力；
2. Skill 通过注入的 **RetrievalPort** 调用检索能力；
3. Skill **不得**直接 import 或实例化任何具体 Provider SDK（OpenAI/Anthropic/向量库等）；
4. ModelRuntimePort / RetrievalPort 由 Application 定义、由 Infrastructure 实现（见 DQ-04 Port Ownership）；
5. Skill 不知道具体 Provider、模型名、连接串或凭证。

```text
Skill Direct Provider SDK Access:
PROHIBITED

Skill Allowed Provider Access:
ModelRuntimePort / RetrievalPort (Application-defined abstractions only)
```

#### Skill Input and Output Contract

每个 Skill 具有明确的执行契约：

1. **输入契约**：Skill 入参的结构化定义，由 Application Use Case 在 Prepare 阶段装配；
2. **输出契约**：Skill 产出 Candidate Result 的结构化定义；
3. 输入/输出契约是 Skill 的公开边界，调用方与 Skill 实现解耦；
4. Candidate Result 是**业务候选**，不是已确认的 Current Truth——是否落库由 Application Use Case 决定；
5. Skill 输入/输出契约的变化必须反映在 Skill 版本中（见 Version Boundary）。

#### Skill LangGraph Boundary

Skill 与 LangGraph 的关系经由 Application Layer 间接建立，二者**不直接耦合**：

```text
LangGraph Node
  -> Stage / Coordination Application Service
    -> Skill Executor
      -> Skill
```

1. LangGraph Node 只调用公开 Application Service（DQ-04 已确认）；
2. Application Service 通过 **Skill Executor** 调用具体 Skill；
3. LangGraph Node **不**直接 import、构造或调用 Skill；
4. Skill **不**感知 LangGraph 的存在，不读取 Graph State、不写 Checkpoint；
5. Skill 与 LangGraph Node **不是**同一概念、不一一对应。

```text
LangGraph Node Direct Skill Invocation:
PROHIBITED

Skill == LangGraph Node:
NO
```

#### Skill Independent Execution

Skill **必须**能够脱离 LangGraph 独立运行和独立评估：

1. Skill 可在不启动 LangGraph 的情况下被直接调用执行（给定符合契约的输入）；
2. Skill 可独立进行单元测试与评估测试；
3. Skill 的执行不依赖 Graph State、Node 上下文或 Checkpoint；
4. 独立运行能力是 Skill 可评估性（Evaluation）与可测试性的前提。

```text
Skill Independent Execution:
REQUIRED
```

#### Skill Version Boundary

Skill 的版本由多个可独立演进的部分组合而成，必须分别管理：

| 版本维度 | 内容 |
|----------|------|
| Contract Version | 输入/输出契约版本 |
| Implementation Version | 业务能力实现版本 |
| Prompt Version | Prompt 资产版本（如适用） |
| Output Schema Version | 输出结构化 Schema 版本（如适用） |

1. 四个维度可独立变更，但必须可被追踪与关联；
2. Contract 变更是破坏性变更的最高信号，调用方依赖 Contract Version；
3. Prompt 与 Output Schema 变更影响输出质量与解析，须纳入 Evaluation 覆盖；
4. Skill 版本用于评估对比、回归检测与可追溯性；
5. 具体版本存储形式（文件/注册表）不在本 Decision 范围，见 Open Questions。

#### Skill Evaluation and Test Boundary

Skill 作为可独立运行组件，须支持以下测试层次：

1. **Contract Test**：验证 Skill 输入/输出契约符合定义；
2. **Unit Test**：以注入的 Fake Port 测试 Skill 业务能力逻辑，不依赖真实 Provider；
3. **Integration Test**：经 Stage Application Service + Skill Executor 调用 Skill 的集成路径；
4. **Evaluation Test**：针对 Prompt/Output Schema/实现版本的输出质量评估；
5. **Architecture Test**：强制 Skill 不直接访问 Repository、不直接 import Provider SDK、不依赖 LangGraph。

```text
Skill Direct Repository Access (Architecture Test):
ENFORCED — PROHIBITED

Skill Direct Provider SDK Import (Architecture Test):
ENFORCED — PROHIBITED

Skill LangGraph Dependency (Architecture Test):
ENFORCED — PROHIBITED
```

#### Decision Boundary

本 Decision 已确认：

1. Skill 是业务模块 Application Layer 内的无状态业务能力组件；
2. Skill 落位 `modules/<module>/application/skills/<skill_slug>/`；
3. Skill 不是独立 Package、不是 Domain Service、不是 Use Case 同义词；
4. Skill 是无状态的，不持有跨执行可变业务状态；
5. Skill 不读取或写入 Current Truth；
6. Skill 不持久化业务结果；
7. Application Use Case 以 Prepare–Execute–Commit 协调 Skill 与业务事务；
8. Skill 只参与 Execute 阶段，产出 Candidate Result；
9. Candidate Result 是业务候选，是否落库由 Application Use Case 决定；
10. Skill 直接访问业务 Repository = PROHIBITED；
11. Skill 业务事务所有权 = NO；
12. Skill 不更新 Evidence / Audit / Idempotency；
13. Skill 所需数据由 Use Case 在 Prepare 阶段以输入契约注入；
14. Skill 只能通过 Application 定义的 ModelRuntimePort / RetrievalPort 调用 Provider 能力；
15. Skill 直接 import 或实例化具体 Provider SDK = PROHIBITED；
16. LangGraph Node 经 Stage Application Service + Skill Executor 调用 Skill；
17. LangGraph Node 直接调用 Skill = PROHIBITED；
18. Skill 与 LangGraph Node 不是同一概念、不一一对应；
19. Skill 不感知 LangGraph、不读 Graph State、不写 Checkpoint；
20. Skill 必须能脱离 LangGraph 独立运行与独立评估 = REQUIRED；
21. Skill 版本分 Contract / Implementation / Prompt / Output Schema 四个维度分别管理；
22. Skill 须支持 Contract / Unit / Integration / Evaluation / Architecture 五类测试；
23. Architecture Test 强制 Skill 不直接访问 Repository、不 import Provider SDK、不依赖 LangGraph；
24. 本 Decision 不选择模型 Provider、Retrieval Backend、Schema Library、Prompt Registry 或 Evaluation Framework；
25. 本 Decision 接受后仍不授权生产实现。

本 Decision 尚未确认：

- 具体模型 Provider；
- Retrieval Backend；
- Schema / Validation Library；
- Prompt 存储与版本注册形式（Prompt Registry）；
- Evaluation Framework 与评测数据集形式；
- Skill Executor 的具体实现机制；
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
- RFC-001-DQ-04：Layer Responsibilities, Transaction Ownership and Dependency Rules；
- DEC-015：Skill Execution Contract；
- DEC-020：MVP Skills Scope；
- DEC-026：Skill Specification；
- DEC-027 / DEC-028 / DEC-030：MVP Skill Specifications；
- DEC-033：Runtime Reliability；
- DEC-038：RFC Governance；
- Architecture Baseline v1；
- Spike-001 Transaction and Recovery Evidence。

---

### DQ-06：Dependency Injection, Configuration and Application Bootstrap

#### Question

系统如何进行依赖注入与对象装配？配置在哪里加载与验证、Secret 的边界是什么、资源生命周期由谁管理、Application Bootstrap 的职责与形态是什么？

#### Decision

Status: ACCEPTED

系统采用 **Constructor Injection + 显式 Factory Functions + 集中式 Composition Root（`bootstrap/`）**；MVP **不**引入第三方 DI Framework。**配置仅由 Bootstrap 加载、类型化、验证并冻结为不可变对象**，启动失败即 fail-fast；**Secret 只注入需要它的 Infrastructure Adapter**，不进入 Domain / Application / Skill / Graph State / API Response；**禁止全局 Service Locator 与可变运行状态**；**资源生命周期由 Application Bootstrap 统一管理**。

#### Dependency Injection Model

1. 默认采用 **Constructor Injection**：依赖通过构造函数显式传入；
2. 使用**显式 Factory Functions** 构造复杂对象及其依赖；
3. MVP 阶段**不引入第三方 DI Framework**（无容器、无自动注入魔法）；
4. 依赖关系在代码中显式可见，便于审查、测试与推理；
5. 装配逻辑集中在 Composition Root，业务代码不做服务定位。

```text
DI Framework for MVP:
NONE (Constructor Injection + Explicit Factory)

Global Service Locator:
PROHIBITED
```

#### Composition Root

**Composition Root** 集中位于 `bootstrap/`：

1. 所有对象图的构造与依赖装配**只**在 Composition Root 完成；
2. Composition Root 是**唯一**知道具体实现（Infrastructure Adapter）与接口（Application Port）绑定关系的代码；
3. 业务层（Domain / Application）不参与装配，不知道具体实现；
4. 各 Entrypoint（API / Worker / CLI）不自行装配，统一由 Bootstrap 提供已装配的对象图；
5. 测试通过注入 Fake / Stub 替换真实 Adapter，无需修改业务代码。

```text
Composition Root Location:
bootstrap/

Business Code Self-wiring / Service Location:
PROHIBITED
```

#### Configuration Loading and Validation

1. 配置**仅**由 **Bootstrap** 加载；
2. 配置在加载后立即**类型化**（typed）与**验证**（validated）；
3. 验证失败的配置导致**启动失败（fail-fast）**，不进入部分可用状态；
4. 验证通过的配置被冻结为**不可变（immutable）**配置对象后注入；
5. 业务代码不直接读取环境变量或配置文件；
6. 配置按边界分层，各层只接收自己需要的配置子集。

```text
Configuration Load Location:
Bootstrap only

Configuration Validation:
typed + validated + immutable, fail-fast on error

Business Code Direct env/config Access:
PROHIBITED
```

#### Configuration Layer Boundary

| 层 | 配置可见性 |
|----|-----------|
| Domain | **不接收**任何配置；纯业务核心 |
| Application | 只接收**业务流程级**配置（如超时、重试策略、开关），不接收连接串/凭证 |
| Infrastructure | 接收**适配器级**配置（连接串、Endpoint、凭证引用、Provider 参数） |
| Bootstrap | 加载、验证并分发全部配置；唯一全量配置持有者 |

1. Domain 配置依赖 = PROHIBITED；
2. Application 不知道 Infrastructure 的连接细节；
3. Infrastructure 适配器只接收自身所需配置，不持有全量配置；
4. 配置分发由 Bootstrap 在装配时完成。

#### Secret Boundary

Secret（API Key、Database Password、Token 等）的边界**严格受限**：

1. Secret **只**注入**需要它的 Infrastructure Adapter**；
2. Secret **不得**进入 Domain / Application Command / Application Result / Skill Input / Skill Result / Graph State / Checkpoint / Business Audit / Runtime Trace Payload / API Response；
3. Secret **不得**写入 Git Repository、GitHub Issue 或 PR；
4. **不得**打印或持久化完整 API Key / Database Password / Authorization Header / `.env` 内容 / Secret Manager 返回值；
5. Secret 的获取方式（环境变量 / Secret Manager）由 Infrastructure 适配器封装，业务层无感知。

```text
Secret Injection Target:
Infrastructure Adapter that needs it ONLY

Secret in Domain / Application / Skill / Graph State / Checkpoint /
Audit / Trace / API Response / Git / Issue / PR:
PROHIBITED

Logging or Persisting full Secret value:
PROHIBITED
```

#### Environment File Boundary

1. Repository **只**提交 `.env.example`（占位值，无真实凭证）；
2. `.env`（真实凭证）**不得**提交，须被 `.gitignore` 排除；
3. `.env.example` 列出全部必需配置键，便于 Bootstrap 校验完整性；
4. 生产环境凭证来源（Secret Manager 等）不在本 Decision 范围，见 Open Questions。

```text
.env committed to Repository:
PROHIBITED

.env.example (placeholder only) committed:
REQUIRED
```

#### Resource Lifetime Management

资源生命周期由 **Application Bootstrap 统一管理**，按作用域分级：

| 作用域 | 含义 | 示例 |
|--------|------|------|
| Application | 进程级长生命周期 | 连接池、Model Runtime Client、全局配置 |
| UseCase | 单个 Use Case 执行期 | Unit of Work、事务资源 |
| WorkflowRun | 单次 Workflow 运行期 | Graph 运行上下文、Checkpoint 句柄 |
| SkillExecution | 单次 Skill 执行期 | 单次模型调用、检索会话 |

1. 长生命周期资源（连接池等）由 Bootstrap 创建并在进程结束时关闭；
2. 短生命周期资源由对应作用域创建与释放；
3. **禁止**模块级可变单例持有连接或运行状态；
4. **禁止**全局可变运行状态。

```text
Global Mutable Runtime State:
PROHIBITED

Module-level Mutable Singleton holding connection/state:
PROHIBITED

Resource Lifetime Owner:
Application Bootstrap (scoped)
```

#### Test Replacement Boundary

依赖注入形态必须支持测试替换：

1. 测试通过 Constructor / Factory 注入 **Fake / Stub** 替换真实 Infrastructure Adapter；
2. 替换**不**需要修改业务代码或依赖容器魔法；
3. Composition Root 显式装配使测试可构造精简对象图；
4. Skill / Use Case 可在不启动真实 Provider / 数据库的情况下测试（与 DQ-05 独立运行一致）。

```text
Test Replacement Mechanism:
Injected Fakes / Stubs via Constructor / Factory

Test Requiring Real Provider / Database for Business Logic:
NOT REQUIRED
```

#### Sync and Async Boundary

同步 / 异步执行策略、API / Worker / CLI 的进程边界**不**在本 Decision 范围，留待 RFC-001-DQ-07 决定。本 Decision 仅确认装配、配置、Secret 与资源生命周期模型，与具体同步/异步运行模型正交。

#### Decision Boundary

本 Decision 已确认：

1. 默认采用 Constructor Injection；
2. 使用显式 Factory Functions 装配；
3. MVP 不引入第三方 DI Framework；
4. Composition Root 集中位于 `bootstrap/`；
5. Composition Root 是唯一绑定接口与实现的位置；
6. 全局 Service Locator = PROHIBITED；
7. 业务代码不做服务定位、不自行装配；
8. 配置仅由 Bootstrap 加载；
9. 配置类型化、验证、不可变，验证失败 fail-fast；
10. 业务代码不直接读取环境变量 / 配置文件；
11. Domain 不接收任何配置；
12. Application 只接收业务流程级配置；
13. Infrastructure 只接收适配器级配置；
14. Secret 只注入需要它的 Infrastructure Adapter；
15. Secret 不进入 Domain / Application / Skill / Graph State / Checkpoint / Audit / Trace / API Response / Git / Issue / PR；
16. 不打印或持久化完整 Secret 值；
17. Repository 只提交 `.env.example`（占位值），`.env` 不得提交；
18. 资源生命周期由 Application Bootstrap 统一管理；
19. 资源按 Application / UseCase / WorkflowRun / SkillExecution 作用域分级；
20. 全局可变运行状态 = PROHIBITED；
21. 模块级可变单例持有连接 / 状态 = PROHIBITED；
22. 测试通过注入 Fake / Stub 替换真实 Adapter，无需修改业务代码；
23. 同步 / 异步与 API / Worker / CLI 进程边界留待 DQ-07；
24. 本 Decision 不选择 DI Framework、Secret Manager、Settings Library 或 Deployment Platform；
25. 本 Decision 接受后仍不授权生产实现。

本 Decision 尚未确认：

- 第三方 DI Framework（MVP 不引入，后续是否引入未决）；
- Settings / Configuration Library；
- Secret Manager 及生产凭证来源；
- API Framework；
- Worker 和 Queue；
- 同步 / 异步执行策略与进程边界（DQ-07）；
- Database 和 ORM；
- Architecture Test 工具；
- Deployment Platform；
- Production Skeleton。

#### Traceability

- RFC-001-DQ-01：Modular Monolith First；
- RFC-001-DQ-02：Python Backend and LangGraph Boundary；
- RFC-001-DQ-03：Repository and Package Layout（Bootstrap and Composition Root）；
- RFC-001-DQ-04：Layer Responsibilities, Transaction Ownership and Dependency Rules（Constructor Injection / Composition Root）；
- RFC-001-DQ-05：Skill Code Shape（Provider Port 注入边界）；
- DEC-023：LangGraph StateGraph；
- DEC-024：State Separation；
- DEC-033：Runtime Reliability；
- DEC-038：RFC Governance；
- Architecture Baseline v1；
- Spike-001 Transaction and Recovery Evidence。

---

## Decision Question 07: Process Boundaries and Sync/Async Execution Strategy

> **Decision Status:** `ACCEPTED`
> **User Decision:** `ACCEPTED`

**Decision:** One modular monolith application and one shared release boundary. Production runtime separates API Process and Workflow Worker Process. Long workflows execute through durable background dispatch. Human Review submit synchronously commits business state and durably schedules asynchronous resume. Application Core is sync-first and Domain is synchronous only.

### Architecture, Release and Process Boundary

必须明确区分：

```text
Application Architecture
≠
Release Artifact
≠
Runtime Process
```

项目继续采用：

```text
One Modular Monolith Application
+
One Shared Backend Codebase
+
One Versioned Release Boundary
+
Multiple Role-specific Runtime Processes
```

“一个主要后端部署单元”在本 Decision 中解释为：一个统一逻辑后端应用 + 一个统一版本化发布边界 + 一个共享可部署制品 + 多个不同运行角色的进程。它不要求所有能力运行在同一个操作系统进程中。

### Runtime Process Roles

生产运行时至少区分：

```text
API Process
Workflow Worker Process
CLI Process
```

#### API Process

API Process 负责：创建 Task；创建 Workflow Run；查询 Task、Stage 和 Run 状态；获取 Review Package；保存 Review Draft；提交 Human Review；请求 Cancel / Rerun / Resume；Authentication 和 Authorization；Request Validation；Correlation ID；将 Application Result 映射为协议响应。

API Process 不得：在 HTTP Request 中执行完整长 Workflow；在 Route 中执行多个 LangGraph Node；长时间等待 LLM、Retrieval 或 Human Review；使用进程内临时 Background Task 承担必须可靠完成的生产工作；依赖客户端连接存活维持 Workflow；将正式任务状态只保存在内存中。

#### Workflow Worker Process

Worker Process 负责：领取 Workflow Start / Resume / Rerun Intent；领取 Cancellation 或 Recovery Work；创建 Workflow Runtime Context；执行 LangGraph；调用 Stage Application Service；执行 Interrupt 和 Resume；管理 Workflow Retry Budget；响应 Cancellation；更新 Runtime Record；写入或更新 Checkpoint；记录 Runtime Trace；创建 Recovery Case；确认工作完成、失败或等待人工。

Worker 不得：绕过 Application Service；直接更新 Current Truth；直接调用业务 Repository；将 Queue Message 当作业务事实；使用进程内内存作为唯一 Runtime State；无限重试；因重复投递产生重复业务版本。

#### CLI Process

CLI 是按需启动的临时 Entrypoint。允许：查询 Task 和 Runtime 状态；创建开发或测试 Task；提交明确授权的 Recovery Command；执行 Evaluation；检查配置；调用管理 Use Case；提交 Workflow Work Intent。CLI 必须调用相同的 Application Layer。CLI 不得：直接修改数据库；直接删除 Checkpoint；绕过 Audit / Idempotency / Human Review；输出 Secret；在生产中默认以内联方式执行完整长 Workflow。

### Unified Release Boundary

API 和 Worker 使用相同 Python Package、相同业务模块、相同 Application Service、相同 Domain Contract、相同 Schema 和 Runtime Identifier，默认从同一个 Release Version 构建和部署，不被视为两个独立业务服务。初始 MVP 不设计复杂跨版本兼容矩阵。至少需记录：`Application Version / Graph Version / Workflow Definition Version / Job Payload Version / Schema Version`。新版 API 不得创建当前 Worker 无法理解的工作。滚动升级与长期 Graph Versioning 由 RFC-003、RFC-007 决定。

### Long Workflow HTTP Boundary

正式规则：

```text
Long Workflow inside HTTP Request = PROHIBITED
```

生产请求采用：

```text
Submit
↓
Persist Business or Runtime Intent
↓
Create Durable Dispatch Intent
↓
Return Task / Run Identity and Status
```

而不是 `Submit → Execute Entire Workflow → Wait for Final Result → Return`。API 返回成功表示工作已被可靠接受，不表示 Workflow 已完成。具体 Endpoint、HTTP Status 和 Response Schema 由 RFC-004 决定。

### Durable Dispatch Boundary

API 与 Worker 之间必须存在可靠工作交接边界，抽象为 `WorkflowDispatchPort`，能力至少包括：

```text
schedule_start
schedule_resume
schedule_rerun
schedule_cancel
schedule_recovery
```

API 返回“已接受”之前，Durable Work Intent 必须已被可靠记录。禁止使用 `asyncio.create_task(run_workflow())` 或 Web Framework 临时 Background Task 作为生产可靠任务机制。本 Decision 不选择具体实现（候选：Database-backed Job Table / Transactional Outbox / Redis Queue / Message Broker / Cloud Queue / Managed Workflow Runtime），具体由 RFC-002 和 RFC-003 决定。

### Worker Recovery Requirements

Worker Crash 不能导致工作永久丢失。恢复语义必须结合 `Durable Dispatch + Runtime Record + Checkpoint + Application Idempotency`，至少满足：未完成工作可重新领取；重复投递不产生重复 Domain Version；已成功提交的 Application Transaction 不重复提交；未提交 Skill Result 不视为 Current Truth；Resume 使用正确 `thread_id`；每次独立执行尝试具有明确 `run_id`；Stale Input 或 Stale Checkpoint 在正式业务写入前被拒绝；Worker Failure 可进入 Retry、Pause 或 Recovery 状态。Lease、Heartbeat、Ack、Visibility Timeout 和 Retry Policy 由 RFC-003 决定。

### Human Review Submit and Resume

Human Review Submit 采用 `Synchronous Business Commit + Asynchronous Workflow Resume`。推荐流程：

```text
Review Submit Request
↓
SubmitReview Application Use Case
↓
Validate Review Package Version
↓
Check Stale Review
↓
Check Idempotency
↓
Commit Approved Strategy
↓
Write Audit and Idempotency
↓
Create Durable Resume Intent
↓
Return
```

HTTP Request 必须同步完成：Review Version Validation；Stale Review Detection；Duplicate Submit Detection；Approved Strategy Business Commit；Audit；Idempotency；Durable Resume Intent 的可靠记录。HTTP Request 不等待后续 Marketing Brief Skill、Xiaohongshu Adapter、LangGraph Node 或整个 Workflow 完成。返回状态可概念性表达为 `review_status = approved` + `workflow_status = resume_scheduled`。具体 API Schema 由 RFC-004 决定。

### Atomic Resume Coordination

正式要求：

```text
Approved Strategy Commit + Durable Resume Intent = Atomic or Reliably Reconciled
```

不得出现：Approved Strategy 已成功提交但 Resume 永久丢失；Resume 已安排但 Approved Strategy 事务失败；重复 Review Submit 产生多个有效 Resume；Worker Resume 读取到未提交或错误版本的业务状态。具体实现（Transactional Outbox / Database Job Table / Post-commit Reconciliation / 其他可靠协调机制）由 RFC-002、RFC-003 决定。

### Business Asynchrony vs Python Async

**Business-level Asynchrony**（HTTP Request returns first, Workflow continues in background）为项目正式采用的业务语义。**Python `async/await`** 是代码执行模型，不等于后台任务架构。本 Decision 不因为采用后台 Workflow，就要求全部 Python 代码采用 `async/await`。

### Sync-first Application Core

正式采用：

```text
Domain:               Synchronous only
Application Core:     Sync-first
Workflow Semantics:   Asynchronous background execution
Concurrency:          Bounded Worker Processes or Worker Slots
Infrastructure:       Execution mode must be explicit
```

- **Domain**：禁止 `async` 业务接口、Event Loop、网络或数据库等待、Async Framework 类型；保持纯同步业务逻辑。
- **Application**：Use Case 默认同步接口与同步事务语义；不得无规则同时提供 `execute()` / `execute_async()`，除非后续 RFC 明确迁移或兼容策略。
- **Worker**：初始可使用同步 LangGraph 执行模式；并发优先采用 Bounded Worker Concurrency（多个 Worker Process / 有界 Worker Slot / 明确任务领取限制），禁止无限创建并发 Task。
- **Infrastructure**：Adapter 必须明确其执行模式；允许 Async-native Adapter，但必须隔离在明确 Port 后、不污染 Domain、不让 Application 无规则混合 Sync/Async、明确 Resource Lifecycle、明确 Timeout/Cancellation/Error Mapping。禁止业务代码随意调用 `asyncio.run()`、在同步调用内部创建不可关闭的 Event Loop、隐藏未受控线程、在 Event Loop 内执行不可控阻塞调用。

**Why Sync-first：** Spike-001 已验证同步 StateGraph、Interrupt、Resume、Retry 与 Recovery；MVP 当前目标是正确性、可靠性、Human Review 与可演示性；当前没有高并发证据要求全栈 Async-first；API 与 Worker 分进程已解决 HTTP 长时间阻塞问题；Sync-first 降低事务、测试与 Coding Agent 混用复杂度；未来可基于性能证据调整部分 Adapter 或 Runtime。“Sync-first” **不等于** 永远禁止使用任何异步技术：Application Core 默认同步；业务时间上后台异步；需要异步的技术能力通过明确 Adapter 隔离；架构变更必须有证据。

### API and Worker Bootstrap

API 和 Worker 共享核心 Application Factory，但使用窄化的不同 Runtime Factory：

```text
build_core_resources()
↓
build_application_services()
↓
├── build_api_runtime()
└── build_worker_runtime()
```

- **API Runtime** 只装配：API 所需 Command 和 Query；Auth Adapter；HTTP Error Mapper；Correlation Context；Workflow Dispatch Port。API Runtime 不自动启动完整 Workflow Worker。
- **Worker Runtime** 装配：Workflow Runtime；Dispatch Consumer；Checkpointer；Stage Application Services；Recovery Services；Worker Lifecycle。Worker Runtime 不自动启动 HTTP Server。

### Dispatch Payload Boundary

API 与 Worker 之间只传递轻量 Runtime Reference。允许字段：`task_id / run_id / thread_id / workflow_name / workflow_version / command_type / idempotency_key / requested_at / correlation_id`。不得传递：完整 Product Facts；完整 Evidence Package；完整 Prompt；完整 Marketing Brief；ORM Entity；Database Session；Secret；Provider Client；LangGraph Checkpoint 二进制；可变 Domain Object。Worker 根据 ID 从正式业务存储和 Runtime Store 加载所需状态。

### Frontend Progress Boundary

Frontend 不依赖持续连接维持 Workflow。基本流程 `Submit Work → Receive task_id / run_id → Query Task or Run Status`。初始前端可采用 Polling / Conditional Polling / Manual Refresh；未来可增加 Server-Sent Events / WebSocket / Push Notification。具体机制由 RFC-004 决定。Workflow 正确性不得依赖前端连接存在。

### Cancellation Boundary

取消采用 Durable Cancellation Intent：`Cancel Request → Application validates permission and state → Persist Durable Cancellation Intent → Worker observes cancellation → Current bounded work stops safely → Runtime status updated`。需区分 `cancellation_requested / cancelling / cancelled / cancellation_failed`。HTTP Cancel 请求成功不表示 Worker 已经即时停止。具体 Cancellation State Machine 由 RFC-003 和 RFC-004 决定。

### Local and Test Runtime

允许本地和测试环境提供 `Combined Development Runtime`（一个命令启动 API + Local Worker + Local Dispatch Adapter），还可提供明确的 `Inline Execution Mode`，但仅限 `local / test / evaluation`，并且必须：显式标记非生产；使用相同 Application Service；不绕过 Idempotency；不绕过 Checkpoint；不改变业务事务规则；不成为生产默认路径。Production CLI Inline Workflow 仍然禁止。

### Process Responsibility Matrix

| Capability               |    API Process | Workflow Worker |    CLI Process |
| ------------------------ | -------------: | --------------: | -------------: |
| HTTP Protocol            |              是 |               否 |              否 |
| Create Task              | 通过 Application |  通过 Application | 通过 Application |
| Query Status             |              是 |           内部可读取 |              是 |
| Execute LangGraph        |              否 |               是 |         仅本地/测试 |
| Long Model Skill         |              否 |               是 | 仅测试/Evaluation |
| Submit Human Review      |              是 |               否 |         授权管理场景 |
| Create Resume Intent     | 通过 Application |    可用于 Recovery |        可提交管理请求 |
| Execute Resume           |              否 |               是 |           生产中否 |
| Business Transaction     | 通过 Application |  通过 Application | 通过 Application |
| Direct Repository Access |              否 |               否 |              否 |
| Runtime Recovery         |           提交请求 |              执行 |         授权管理入口 |

### Hard Rules

```text
Backend Architecture:              One Modular Monolith Application
Release Boundary:                  One Shared Versioned Backend Release
Runtime Roles:                     API Process + Workflow Worker Process + CLI Process
Long Workflow in HTTP Request:     PROHIBITED
Production In-memory Background Task: PROHIBITED for durable work
Workflow Dispatch:                 DURABLE
Human Review Submit:               Synchronous business commit
Workflow Resume:                   Asynchronously scheduled
Application Core:                  SYNC-FIRST
Domain:                            SYNCHRONOUS ONLY
Concurrency:                       BOUNDED WORKER CONCURRENCY
API and Worker Version:            Same release by default
Production CLI Inline Workflow:    PROHIBITED
Local/Test Combined Runtime:       ALLOWED
```

### Decision Boundary

本 Decision 已确认：

1. Modular Monolith 不要求所有能力运行在同一个进程；
2. 使用统一 Backend Application；
3. 使用统一版本化 Release Boundary；
4. API Process 与 Workflow Worker Process 在生产运行时分离；
5. CLI 为按需运行的临时进程；
6. API、Worker、CLI 使用同一 Python Package 和 Application Layer；
7. API 与 Worker 默认从同一 Release Version 构建；
8. API 只处理短生命周期请求；
9. 长 Workflow 禁止在 HTTP Request 中执行完成；
10. 长 Workflow 采用后台异步业务语义；
11. API 必须在 Durable Work Intent 可靠记录后再返回接受状态；
12. 生产可靠任务禁止依赖进程内临时 Background Task；
13. API 与 Worker 通过 Durable Dispatch Port 协作；
14. 当前不选择具体 Queue、Broker 或 Dispatch Backend；
15. Worker 负责 LangGraph Start、Resume、Retry、Cancellation 和 Recovery；
16. Worker 仍只能通过 Application Service 提交业务状态；
17. Worker Crash 后工作必须可重新领取；
18. 重复投递通过 Idempotency 防止重复业务版本；
19. Human Review Submit 同步完成业务校验和 Approved Strategy 提交；
20. Human Review Submit 不等待后续 Workflow；
21. Approved Strategy Commit 与 Resume Intent 必须原子或可靠协调；
22. Workflow Resume 由 Worker 异步执行；
23. Domain 保持纯同步；
24. Application Core 采用 Sync-first；
25. 当前不采用全栈 Async-first；
26. 并发优先通过有界 Worker Process 或 Worker Slot；
27. Infrastructure Adapter 必须声明执行模式；
28. 禁止业务代码随意使用 `asyncio.run()`；
29. API 与 Worker 使用不同的窄化 Bootstrap Factory；
30. CLI 必须调用同一 Application Layer；
31. Production CLI 默认不 Inline 执行长 Workflow；
32. Local/Test 允许 Combined Runtime 和 Inline Runner；
33. Dispatch Payload 只包含 ID、版本和 Runtime Reference；
34. Frontend 通过 Task / Run 状态查询获得进度；
35. Polling、SSE 或 WebSocket 由 RFC-004 决定；
36. Cancellation 使用 Durable Cancellation Intent；
37. 本 Decision 不选择 API Framework、Queue、Database Driver、Worker Framework 或部署平台；
38. 本 Decision 接受后仍不授权创建 API、Worker 或生产 Runtime。

本 Decision 尚未确认：Durable Dispatch 的具体实现；Worker Framework；Queue 或 Broker；Job Lease 与 Heartbeat；Ack 和 Visibility Timeout；Checkpoint Backend；Resume State Machine；API Framework；HTTP Endpoint；Polling、SSE 或 WebSocket；Deployment Platform；Process Health Check；Worker Scaling Policy；Graph Version Migration；Production Runtime Implementation。

### Traceability

关联：RFC-001-DQ-01 Modular Monolith First；RFC-001-DQ-02 Python Backend and LangGraph Boundary；RFC-001-DQ-03 Repository Layout；RFC-001-DQ-04 Layer Responsibilities and Transaction Ownership；RFC-001-DQ-05 Skill Architecture；RFC-001-DQ-06 Bootstrap and Resource Lifecycle；DEC-011 Deterministic Workflow Control；DEC-013 Persistent Task State and Resume；DEC-021 Primary Agent Architecture；DEC-023 LangGraph StateGraph；DEC-024 Business and Runtime State Separation；DEC-029 Human Review；DEC-033 Failure, Retry and Recovery；DEC-035 Sync StateGraph Spike Stack；DEC-038 RFC Governance；Spike-001 Runtime Evidence；Architecture Baseline v1。

---

## Decision Question 08: Module Public Contracts, Cross-module Collaboration and Cycle Governance

> **Decision Status:** `ACCEPTED`
> **User Decision:** `ACCEPTED`

**Decision:** Business modules expose one Public Facade. Cross-module reads use synchronous Public Queries returning immutable snapshots. State changes remain owned by the target module. Cross-stage coordination is performed by Orchestration. Only non-critical post-commit reactions use Application Events. Module dependencies must remain acyclic and are enforced through Architecture Tests.

### Module Public Facade

每个业务模块通过唯一稳定入口暴露跨模块契约：

```text
modules.<module>.public
```

概念路径：`modules/<module>/public.py`。其他模块只能通过该 Public Facade 使用目标模块的公开能力。

允许：

```python
from ai_ecommerce_agent.modules.human_review.public import (
    GetApprovedStrategy,
    ApprovedStrategySnapshot,
)
```

禁止：

```python
from ai_ecommerce_agent.modules.human_review.domain import ...
from ai_ecommerce_agent.modules.human_review.application.services import ...
from ai_ecommerce_agent.modules.human_review.infrastructure import ...
from ai_ecommerce_agent.modules.human_review.application.skills import ...
```

`public.py` 可以重新导出内部定义的稳定 Contract，但对外 Import Path 必须保持为 `modules.<module>.public`。

### Public Contract Surface

Public Facade 可以暴露：`Public Command / Public Query / Public Result / Public Error / Application Service Protocol / Published Application Event / Stable Identifier / Version Reference / Immutable Snapshot`。

Public Facade 不得暴露：`ORM Model / Database Session / Repository Implementation / Mutable Domain Entity / Aggregate Internal / Infrastructure Adapter / Infrastructure Error / Graph State / LangGraph Node / Checkpoint Object / Provider SDK Type / Global Settings / Secret / Database Table Structure / Internal Helper`。

Public Contract 必须：`Typed / Immutable / Serializable / Version-aware / Infrastructure-neutral`。

### Public Snapshot Boundary

跨模块数据读取必须返回不可变公开 Snapshot，而不是内部 Domain Entity。推荐：`ApprovedStrategySnapshot / ProductFactsSnapshot / ReviewPackageSnapshot / MarketingBriefSnapshot`。禁止返回：`ApprovedStrategyAggregate / ProductFactsEntity / ORM Entity / Lazy-loaded Relationship`。外部模块不得持有或修改目标模块内部 Aggregate。某个业务类型被多个模块使用，不代表它应被移动到 `shared_kernel/`；优先使用 `Owner Module Public Snapshot` 而非共享可变业务模型。

### Command Contract

Command 表示请求状态所有模块执行一个业务状态变化。推荐业务意图命名：`SubmitReview / ApproveStrategy / CreateMarketingBriefVersion / InvalidateDownstreamStage`。禁止持久化实现命名：`UpdateReviewRow / SetStatusColumn / InsertStrategyRecord`。Public Command 必须：表达业务意图；包含目标业务 ID；包含必要 Version 或 Expected Version；支持 Idempotency Key；包含必要调用者或授权上下文引用；不包含 ORM Entity / Database Session / Graph State / Secret。Command 必须由拥有目标状态的 Application Service 执行。

### Cross-module Command Rule

正式默认规则：`Direct module-to-module state-changing Command = PROHIBITED BY DEFAULT`。Module A 不得任意调用 Module B 的状态修改 Command。跨 Stage 状态变化默认由 `Orchestration` 或 `Explicit Composite Application Use Case` 协调。例如 `Workflow Orchestration → RunProductPositioningStage → CreateReviewPackage → Interrupt for Human Review`，而不是 `product_positioning module` 直接控制 `human_review module state machine`。允许例外必须同时满足：明确业务所有权；单向依赖；不形成循环；不隐藏跨模块事务；已在 Spec、RFC 或 Architecture Review 中声明；具有对应 Contract Test 和 Architecture Test。

### Query Contract

Query 表示只读业务请求。例如：`GetApprovedStrategy / GetCurrentProductFacts / GetReviewPackageStatus / GetMarketingBriefVersion`。Query 必须：无业务副作用；不修改状态；不触发 Workflow；不发布业务 Event；返回 Public Snapshot；执行读取权限和业务可见性检查；返回结构化 Public Error。Query 不得通过读取操作隐藏写入（更新业务状态 / 修改 Current Truth / 发布 Event / 触发下游 Stage / 自动恢复 Workflow）。

### Cross-module Read Rule

跨模块读取正式采用：`Consumer Module → Target Module Public Query → Target Module Application Query Handler → Public Snapshot`。禁止：`Consumer Module → Target Module Repository → Direct SQL / ORM / Internal Table`。共享 Database Instance 不等于共享数据所有权；数据库表不得成为模块间隐式 API。

### Orchestration Responsibility

以下操作应由 `orchestration/` 或明确跨模块 Coordinator 执行：一个 Stage 完成后启动下一个 Stage；Product Positioning 后创建 Human Review Package；Human Review 提交后调度 Resume；Approved Strategy 后启动 Marketing Brief；Rerun 导致下游 Stage 失效；Cancel、Resume、Recovery；跨模块 Workflow Routing；多 Stage 状态协调。Orchestration 可以：调用模块 Public Application Contract；根据明确 Result 决定确定性路由；管理 Interrupt、Resume 和 Runtime Retry。Orchestration 不得：拥有模块业务规则；直接访问模块 Infrastructure；直接读写模块内部表；直接更新 Current Truth；直接提交跨模块隐藏事务。

### Composite Application Use Case

跨模块原子操作只能通过明确建模的 `Composite Application Use Case` 执行。Composite Use Case 必须：有明确业务所有者；有明确输入、输出和错误 Contract；有明确事务边界；通过 Public Port 或正式协调接口访问参与模块；不直接 Import 其他模块 Infrastructure；不允许参与 Service 各自进行隐藏 Commit；具有原子性、失败和幂等测试；与 RFC-002 的持久化事务架构保持一致。禁止 `Service A begins transaction → Service B begins hidden transaction → Partial commit`。默认跨模块流程继续采用多个短事务：`Transaction A → commit → Orchestration → Transaction B`。

### Domain Event

Domain Event 表示模块内部 Domain 已发生的业务事实。例如：`StrategyApproved / ReviewPackageSuperseded / ProductFactsInvalidated`。Domain Event：由 Domain 产生；使用过去式语义；不包含 Infrastructure 类型；不负责发送；不直接调用其他模块；默认属于发布模块内部；不自动等于跨模块 Published Application Event。

### Application Event

Application Event 表示：一个 Application Transaction 已成功提交，并允许其他能力响应该事实。例如：`StrategyApprovedEvent / MarketingBriefVersionCreatedEvent / SourceSetReindexedEvent`。Application Event 可以用于：通知；非关键索引更新；Analytics；非关键 Projection；可重建缓存；外部集成；提交后非原子副作用。Application Event 必须在业务 Commit 成功后产生。

### Event Boundary

正式规则：`Required Immediate Consistency → Command or Composite Use Case`；`Post-commit Non-critical Reaction → Application Event`。以下能力不得依赖普通最终一致 Event：Human Review Approval；Current Truth 更新；Idempotency；同一业务 Commit 的原子数据；必须立即返回的业务验证；LangGraph 核心确定性路由；Durable Resume Intent（除非使用可靠 Outbox 或等价机制）。

### Event Choreography Prohibition

核心 Workflow 不得被隐藏为 Event 链：`Event A → Handler B → Event C → Handler D`。具有以下特征的流程必须由 LangGraph Orchestration 表达：明确 Stage；Human Interrupt；Resume；Retry；Cancellation；状态查询；Recovery；可审计路由。正式规则：`Workflow Orchestration ≠ Event Choreography`。

### In-process Event Bus Boundary

未来可以使用进程内 Event Dispatcher 处理：非关键、可重试、可忽略或可重建、不要求跨进程保证的提交后动作。纯进程内 Event Bus 不得承担：API → Worker Durable Dispatch；Durable Resume；跨进程可靠工作；关键业务副作用；必须保证的通知。本 Decision 不选择 Event Bus、Outbox 或 Broker。

### Event Handler Rules

Event Handler 可以：接收已提交的 Application Event；调用自身模块公开 Application Service；创建非关键 Projection；创建新的 Durable Work Intent；记录 Metrics 和 Analytics。Event Handler 不得：直接访问其他模块 Repository；修改发布者模块内部状态；假设 Event 只执行一次；无限发布 Event；使用 Event 顺序作为未经声明的不变量；失败后伪造成功。Event Handler 必须具备 `Idempotent` 或 `Duplicate-consumption-safe` 语义。

### Module Dependency Graph

模块依赖必须形成 `Directed Acyclic Graph`（有向无环图）。每个模块必须明确：依赖哪些目标模块；依赖目标模块的哪种 Public Contract；属于 Query、Event 或经批准的 Command Dependency；数据所有权；上游和下游关系。禁止 `Module A → Module B 且 Module B → Module A`；也禁止没有 Import 循环但存在逻辑业务调用循环。

### Circular Dependency Resolution

发生循环依赖时，不得使用以下方式掩盖：延迟 Import；函数内部 Import；修改 `PYTHONPATH`；把大量类型移动到 Shared Kernel；使用全局 Event Bus 隐藏调用；直接访问共享数据库。必须从以下方式解决：1) 将控制权提升到 Orchestration；2) 将只读需求改为 Public Query；3) 由需要能力的一方定义 Port，并通过 Bootstrap 注入；4) 提取真正稳定的基础概念；5) 重新划分业务模块；6) 通过明确 Composite Use Case 处理必要原子操作。

### Shared Kernel Boundary

`shared_kernel/` 只允许保存真正稳定、无单一业务所有者的基础类型，例如：`Identifier Base / Version Reference / Clock Protocol / Correlation ID / Generic Pagination / Infrastructure-neutral Result Base / Generic Technical Error Base`。不得保存：`Product Facts Entity / Customer Insight Entity / Approved Strategy Aggregate / Marketing Brief Domain Model / Review State Machine / Evidence Business Rule / Skill-specific Schema`。不得为了减少 Import 数量而扩大 Shared Kernel。

### Public Error Contract

模块对外错误必须是稳定的 Application-level Error。例如：`ReviewPackageNotFound / ReviewPackageStale / ReviewAlreadySubmitted / ApprovedStrategyUnavailable`。Public Error 至少应包含：`error_code / category / message / retryability / relevant_reference`；需要时可以包含：`expected_version / actual_version / conflicting_state / recovery_hint`。不得暴露：`Database Driver Error / ORM Exception / Provider SDK Error / Internal File Path / Database Table Name / Raw Stack Trace / Secret`。调用者只能依据 Public Error Code、Category 和 Retryability 处理，不得解析异常字符串决定业务路由。

### Public Contract Versioning

虽然当前使用单 Repository 和统一 Release，Public Contract 仍必须区分 `Contract-compatible Change` 与 `Contract-breaking Change`。通常兼容：新增可选字段；新增独立 Query；新增不影响现有调用者的 Public Error；新增 Event Metadata。通常不兼容：删除字段；修改字段业务含义；改变 ID 或 Version 语义；将 Query 改为有副作用；修改 Command 幂等语义；将 Snapshot 替换为内部 Entity；改变 Event 所表示的业务事实。Breaking Change 必须：更新 Contract Version；更新 Consumer；更新 Contract Test；在统一 Release 中协调；必要时修订 RFC 或 Architecture Baseline。

### Contract Test Requirements

每个 Public Contract 至少需要：

- **Schema Tests**：验证字段、类型、必填项、默认值、序列化、Version。
- **Consumer Contract Tests**：验证调用者只依赖公开字段和公开行为。
- **Error Contract Tests**：验证 Error Code 稳定、Retryability 明确、技术异常不会泄漏。
- **Event Contract Tests**：验证 Event 在 Commit 后产生、具有 Event ID、Payload 可序列化、不包含 Secret 或内部 Entity、重复消费安全。

### Architecture Test Requirements

未来 Architecture Tests 至少验证：`Cross-module imports must target: modules.<target>.public`。禁止跨模块 Import `modules.<target>.domain / .application / .infrastructure / .application.skills`。还必须验证：模块依赖图无环；`shared_kernel` 不依赖业务模块；Public Contract 不 Import ORM；Public Contract 不 Import LangGraph；Public Result 不包含可变 Domain Entity；Event Handler 不访问其他模块 Infrastructure；Orchestration 只 Import 模块 Public Facade；Production 不通过数据库表绕过 Public Contract；Event 不从失败或未提交事务中正式发布。

### Collaboration Matrix

| Collaboration Type                   | Decision              | Default Owner       |
| ------------------------------------ | --------------------- | ------------------- |
| Cross-module Public Query            | Allowed               | Calling Application |
| Direct Repository Read               | Prohibited            | —                   |
| Direct Module-to-module Command      | Prohibited by default | Orchestration       |
| Cross-stage Coordination             | Allowed               | Orchestration       |
| Cross-module Atomic Write            | Exception only        | Composite Use Case  |
| Post-commit Non-critical Side Effect | Allowed               | Application Event   |
| Event-driven Core Workflow           | Prohibited            | LangGraph           |
| Shared Mutable Domain Entity         | Prohibited            | Public Snapshot     |
| Shared Database as Module API        | Prohibited            | Public Query        |
| Circular Module Dependency           | Prohibited            | DAG Enforcement     |

### Hard Rules

```text
Stable Cross-module Import:          modules.<module>.public
Cross-module Internal Import:        PROHIBITED
Public Mutable Domain Entity:        PROHIBITED
Cross-module Read:                   Public Query Contract
Cross-module State Change:           Owning Application Service
Cross-stage Coordination:            Orchestration
Direct Module-to-module Command:     PROHIBITED BY DEFAULT
Cross-module Atomic Operation:       Explicit Composite Application Use Case only
Core Workflow through Events:        PROHIBITED
Post-commit Non-critical Side Effects: Application Events allowed
Module Dependency Graph:             DIRECTED ACYCLIC GRAPH
Shared Database as Module API:       PROHIBITED
Technical Exception Leakage:         PROHIBITED
```

### Decision Boundary

本 Decision 已确认：每个模块通过 `modules.<module>.public` 提供唯一稳定公开入口；`public.py` 是 Public Facade；其他模块不得 Import 目标模块内部 Domain、Application、Infrastructure 或 Skill；Public Contract 可以暴露 Command、Query、Result、Public Error、Service Protocol、Published Event 和不可变 Snapshot；Public Contract 不得暴露 ORM、Repository、Database Session、Graph State、内部 Entity 或 Provider SDK；Public 输入输出必须类型化、不可变、可序列化并与 Infrastructure 无关；跨模块读取通过目标模块 Public Query；Query 必须无副作用并返回 Public Snapshot；状态修改由拥有状态的模块 Application Service 执行；模块之间直接调用状态修改 Command 默认禁止；跨 Stage 协调由 Orchestration 完成；经审查的单向 Command 例外可以存在但不得形成循环或隐藏事务；跨模块流程默认由多个短事务组成；跨模块原子操作只能通过 Composite Application Use Case；共享数据库不得成为模块间隐式 API；禁止跨模块直接 SQL 或 ORM 访问；Domain Event 默认属于模块内部；Application Event 表示已提交的业务事实；非关键提交后副作用可以使用 Application Event；Human Review、Current Truth、Idempotency 和核心路由不得依赖普通 Event 最终一致性；Event 链不得替代 LangGraph Workflow；进程内 Event Bus 不得承担 API 到 Worker 的可靠调度；Event Handler 必须重复消费安全；模块依赖图必须为 DAG；禁止通过延迟 Import 掩盖循环依赖；Shared Kernel 必须保持最小；跨模块业务数据优先使用 Owner Module Public Snapshot；Public Error 必须稳定、结构化且不泄漏技术异常；调用者只能依据 Public Error Contract 处理；Breaking Change 必须显式版本化并更新 Consumer Contract Tests；Architecture Tests 必须验证跨模块 Import 只能指向 Public Facade 且模块依赖图无环；本 Decision 不选择 Event Bus、Outbox、Schema Library 或 Contract Test Framework；本 Decision 接受后仍不授权创建正式 Public Contract、Event Bus 或生产业务代码。

本 Decision 尚未确认：Python Formatter；Linter；Type Checker；Architecture Test 工具；Contract Test Framework；CI Quality Gate；Coverage Policy；Dependency Scan；Security Scan；Warning Policy；Foundation Skeleton 最低质量标准；Event Bus；Outbox；Schema Library；Production Public Contract Implementation。

### Traceability

关联：RFC-001-DQ-01 Modular Monolith First；RFC-001-DQ-03 Repository and Module Layout；RFC-001-DQ-04 Layer and Transaction Boundaries；RFC-001-DQ-05 Skill Architecture；RFC-001-DQ-07 API and Worker Process Boundary；DEC-011 Deterministic Workflow；DEC-015 Contract-based Skills；DEC-021 Primary Agent Architecture；DEC-024 Business State Ownership；DEC-029 Human Review；DEC-031 Xiaohongshu Mapping Adapter；DEC-033 Retry and Recovery；DEC-038 RFC Governance；Architecture Baseline v1。

---

## Decision Question 09: Quality Toolchain, Architecture Enforcement, CI Quality Gates and Test Baseline

> **Status:** `ACCEPTED`
> **User Decision:** `ACCEPTED`

### Decision

Production code adopts Ruff, Pyright, pytest, Import Linter, and custom Architecture Tests as a unified quality toolchain. All PRs must pass type, architecture, deterministic test, coverage, dependency, and Secret checks. `main` is protected by Required Status Checks. AI Live Evaluation is separated from the ordinary deterministic Merge Gate.

### Quality Governance Model

```text
Accepted Architecture Decision
↓
Machine-checkable Rule
↓
CI Required Check
↓
Merge Block
```

Quality checks are divided into: **Code Correctness**, **Architecture Correctness**, **Business Behavior Correctness**, **Repository Governance Correctness**. A Coding Agent must not rely on documentation alone to understand boundaries; any rule that can be verified automatically must become a tool configuration, Architecture Test, or Required CI Check.

### Python Quality Toolchain

| Concern | Tool |
|---|---|
| Python Formatter | Ruff Formatter |
| Python Linter | Ruff Linter |
| Python Type Checker | Pyright |
| Test Runner | pytest |
| Import Architecture | Import Linter |
| Semantic Architecture | Custom pytest Architecture Tests |
| Coverage | coverage.py / pytest integration |
| Dependency Vulnerability Audit | pip-audit |

Not introduced as parallel Source of Truth: **Black**, **isort**, **Flake8** — to avoid duplicate or conflicting format / import / lint rules. Tool versions will be pinned via Lockfile during Foundation Implementation; this Decision does not lock versions.

### Ruff Boundary

Ruff is responsible for: Python formatting, import sorting, unused imports, undefined names, common logic errors, suspicious exception handling, unified static code style, and project-approved modern Python rules. Formatting Source of Truth = Ruff Formatter; Linting Source of Truth = Ruff Linter. Configuration is centralized in `apps/backend/pyproject.toml`. Business modules must not maintain conflicting independent lint configs. Lint exceptions must point to a specific rule, be scoped to a line/file, state a technical reason, not hide real business/architecture errors, and where needed link a cleanup Issue; broad `# noqa` over whole files or large `per-file-ignores` excluding Domain/Application/Public Contract/Architecture Tests from core checks are prohibited.

### Type Discipline

**Strict-first Type Discipline.** Strict requirements apply first to Domain, Application, Public Contract, Command, Query, Result, Public Error, Snapshot, Skill Input, Skill Result, Graph State, Runtime Identifier, Repository Port, Model Runtime Port, Retrieval Port, Dispatch Payload. Infrastructure Adapters facing untyped third-party SDKs may build narrowing Adapters, but must not let unknown types spread into Application and Domain.

**`Any` Boundary** — `Any` may exist only at explicit external boundaries (unverified JSON, raw Provider SDK responses, third-party dynamic objects, protocol input before Schema Validation), following `External Dynamic Data → Entrypoint/Infrastructure Validation → Typed Contract → Application/Domain`. The chain `Provider Response[Any] → Graph State[Any] → Application[Any] → Domain[Any]` is prohibited. Do not degrade explicit business types to `dict[str, object]` or broad `Any` just to pass the type checker.

**Type Ignore Rules** — prohibited: project-level disabling of core diagnostics, skipping whole packages, broad `type: ignore` without a diagnostic code, changing types to `Any` to pass CI, excluding key business directories via config. Precise type exceptions must specify a diagnostic, state the third-party/technical limitation, stay within the Infrastructure Adapter boundary, and link a cleanup Issue. Principle: *Fix the type boundary before suppressing the checker.*

### Architecture Enforcement Model

Two layers: **Import Linter** (structural rules expressible in the Import Graph) + **Custom pytest Architecture Tests** (semantic rules the Import Graph cannot fully express), located at `apps/backend/tests/architecture/`.

Import Linter initial contracts: Domain Independence, Application Independence, Business Module Isolation, Public Facade-only Cross-module Imports, Orchestration Boundary, Entrypoint Boundary, Spike/Prototype Isolation, Shared Kernel Independence, Module Dependency DAG.

Custom Architecture Tests at minimum cover: Public Contract Shape, Skill Boundary, Orchestration Boundary, Configuration Boundary, Entrypoint Boundary — implemented via AST, Import Graph, type reflection, Contract Registry, or file scanning.

### Test Classification

```text
unit / integration / contract / architecture / e2e / evaluation / live / slow
```

All pytest markers must be pre-registered; CI enables strict marker mode. Unknown or misspelled markers (e.g. `@pytest.mark.intergration`) must fail, never be silently accepted.

### Test Baselines

- **Unit** — deterministic: no network, no real model, no production DB, no production Secret, Fake Clock, deterministic ID, Scripted Model Runtime, fixed Retrieval Fixture, order-independent, repeatable. Focus: Domain Invariant, Application Validation, Idempotency, Stale Input, Version Rule, Evidence Rule, Human Review, Public Error Mapping, Skill Validator, Deterministic Routing, Downstream Invalidation.
- **Integration** — real technical boundaries (Repository, Unit of Work, DB Transaction, Migration, Checkpointer, Durable Dispatch, Model Runtime, Retrieval, Bootstrap Lifecycle, Resource Cleanup) on isolated, rebuildable, cleaned-up resources that verify Commit and Rollback.
- **Contract** — Public Command/Query/Result/Error, Ports, Event Payload, Dispatch Payload, API Schema, Graph State Schema, Adapter Compliance; must block silent field removal, ID/Version semantic change, Query side-effects, Public Error Code drift, Event leaking internal Entity, non-compliant Adapter, Dispatch Payload carrying full business objects.
- **E2E** — full main flow (Create Task → Product Intake → Customer Insight → Product Positioning → Human Review Interrupt → Review Submit → Resume → Marketing Brief → Xiaohongshu Mapping) plus key failure scenarios (Duplicate Submit, Stale Review, Worker Crash, Duplicate Resume Delivery, Stage Rerun, Downstream Invalidation, Provider Failure, Retry Exhaustion, Recovery, Cancellation). Not Happy-Path-only.
- **Evaluation** — AI result quality, not deterministic software behavior. Deterministic Evaluation (fixed input/response/fixture/scorer) may enter the normal PR gate. **Live Evaluation** (real model/provider; cost, network, variance) runs Manual / Nightly / on Prompt-or-Model-Policy-Change / Release Candidate; it is not the sole merge gate for a normal PR.

### External Network Test Boundary

Normal Required PR Tests default to **no live external provider or network access**. Tests needing the real network must be marked `live`. Unit/Contract/Architecture tests must not accidentally call a Model Provider, Embedding Provider, Vector SaaS, external web, production DB, or production Secret Manager. The test environment should be able to block undeclared network access.

### Coverage Policy

After the first executable production code lands: **Branch Coverage measurement, global fail-under = 80%**. Coverage is a risk indicator, not business correctness. Domain Invariant, Human Review, Current Truth, Idempotency, Evidence, Version, Stale Input, Retry, Recovery, Downstream Invalidation must have explicit behavior tests even at 80%. Precise exclusions allowed (pure type declarations, unreachable defensive branches, generated code, Migration tool templates, thin bootstrap entry). Broad `# pragma: no cover` hiding untested business logic is prohibited. During Skeleton stage (no executable business logic): no empty tests to inflate coverage, no fake coverage over empty dirs; focus on tool runnability and real Architecture Contract verification; the Coverage Gate activates when executable production code begins.

### Warning / Flaky / Randomness / Skip-XFail / Snapshot

- **Warnings = Errors by default** (Python Deprecation, pytest, unregistered marker, Resource, unclosed client, config, ORM/Provider deprecation). Exceptions must be precisely matched, justified, have a cleanup condition, and link an upgrade Issue. `ignore all warnings` prohibited.
- **Flaky Test Policy** — Required CI must not mask flaky tests via auto-rerun (`fail → auto-rerun → one pass → green` is prohibited). On a flaky test: record Issue, locate time/random/concurrency/resource cause, isolate explicitly if needed, restore the Gate after fixing. Isolated or un-run tests must not be described as passed.
- **Randomness** — fix Seed, output Seed on failure, deterministic ID generator, control time/model output/Retrieval ordering, avoid order dependence.
- **Skip / XFail** — only for genuinely unsupported environment (with reason, Issue, removal condition) or known defect (strict mode, accurate expectation, review Unexpected Pass). Never to hide incomplete Acceptance Criteria, architecture violations, must-pass business rules, or failures the Agent cannot fix.
- **Golden / Snapshot Tests** — readable content, reviewable diff, no Secret, no random timestamps, human semantic check on update; Coding Agents must not auto-accept all Snapshot changes (`changed → review semantic diff → human accept/reject`).

### Dependency Security

PR Dependency Audit via **pip-audit**; repository enables **Dependabot Alerts** and **Controlled Security Updates**. Routine version updates use a controlled cadence (no mass of disordered auto-PRs). Dependency changes must update the Lockfile, pass full CI, state the new dependency's purpose, check security and License impact, avoid mixing with unrelated business changes, and avoid duplicate-functionality libraries. A Coding Agent must not introduce new dependencies casually.

### Secret Detection

CI must have a **Secret Detection Gate** covering at least API Key, Private Key, Token, `.env`, Authorization Header, Cloud Credential, Database Credential. The specific Secret Scanner is chosen during Foundation Implementation. Handling: `Detected Secret → CI Failure → Remove from repository → Rotate/revoke if the credential was real`. Deleting a real Secret from Git alone is insufficient.

### CI Gate Layers

- **Layer 1 — Fast Static Gate** (every PR): Repository Hygiene, Ruff Format Check, Ruff Lint, Pyright, Import Linter, Architecture Tests.
- **Layer 2 — Deterministic Test Gate** (every PR): Unit Tests, Contract Tests, Coverage, Dependency Audit, Secret Detection.
- **Layer 3 — Runtime Confidence Gate** (after production runtime, by change scope): Integration Tests, Migration Tests, Bootstrap Tests, E2E Smoke Tests, Recovery Tests.
- **Extended Gate** (Nightly / manual / Release Candidate): Full E2E, Live Model Evaluation, Performance Tests, Long Recovery Scenarios, Dependency Compatibility Tests.

### Required Status Checks & Branch Protection

`main` uses stable Required Check names, e.g. `quality/format`, `quality/lint`, `quality/typecheck`, `quality/architecture`, `test/unit-contract`, `test/integration`, `test/e2e-smoke`, `security/dependency-audit`, `security/secret-detection`. Check names must not change frequently. `main` must: merge via Pull Request, forbid direct Push, forbid Force Push, require Required Status Checks, resolve Review Conversations; the user retains final Merge permission. A second Reviewer is not enforced for the current solo portfolio repository. Human gate: `User reviews PR → User decides merge`.

### Coding Agent CI Governance

On CI failure a Coding Agent must NOT: delete failing tests, lower Coverage Threshold, disable Pyright, add global Ignore, delete Import Linter Contracts, delete Architecture Tests, turn Required Checks Optional, modify Branch Protection, update all Snapshots without review, turn failing tests into Skip, or auto-merge. Correct flow: `CI Failure → Determine Root Cause → Fix Code or Justified Test → Add Regression Test → Run All Affected Gates`.

### Frontend Quality Boundary

Future TypeScript production code at minimum requires: TypeScript strict mode, Formatter, Linter, Unit test runner, Build check, Generated API contract drift check. Concrete tool choices (ESLint or Biome, Formatter, Test Runner, Framework Build Tool) are deferred to the frontend framework decision. Fixed principles: `TypeScript strict = REQUIRED`, `Generated API types = CHECKED`, `Build warnings = REVIEWED`.

### Documentation and Traceability Gate

Production Implementation PRs should check: references to relevant DEC and Accepted RFC, Acceptance Criteria, declared Required Tests, Traceability updates, Contract Test updates on Public Contract change, Architecture Documentation updates on architecture change, Migration Rollback/compatibility notes. Implemented progressively via PR Template, Issue Template, doc scripts, and CI Governance Checks.

### Foundation Skeleton Quality Baseline & Verification

After RFC-001 is accepted as a whole and Foundation Work Authorization is granted, the first Foundation PRs should establish: central pyproject configuration, Ruff config, Pyright config, pytest strict-marker config, Coverage config, Import Linter contracts, Architecture test directory, CI workflows, Dependency audit, Secret detection, Developer command documentation. Do not create masses of empty business modules for directory completeness. Foundation Work must at least prove that: format/lint/type errors fail CI; Domain importing Infrastructure, cross-module bypass of Public Facade, and module dependency cycles fail CI; unregistered markers fail CI; Unit Test failure blocks Merge; Coverage below threshold fails once enabled; Dependency Vulnerability fails or enters explicit review; Secret Detection blocks merge; `main` Required Checks are configured; local and CI use the same tool config; and a deliberately constructed Architecture Violation is auto-detected.

### Unified Local and CI Commands

Developers and Coding Agents use a unified command entry (conceptually `quality-format`, `quality-lint`, `quality-type`, `quality-architecture`, `test-fast`, `test-integration`, `test-e2e`, `quality-all`). The concrete mechanism (`uv run` scripts, Python Script, Makefile, Task Runner) is decided by Foundation Implementation. `Local checks = CI checks`; two inconsistent quality configs must not be maintained.

### Performance Targets

Initial targets, not permanent hard limits: Fast Static Gate ≤ 2 min; Unit + Architecture + Contract ≤ 5 min; Required PR Gate total ≤ 10 min; Live Evaluation = separate workflow. When the Required Gate slows: parallelize, cache, optimize fixtures, split by category, reduce duplicate installs — do not delete necessary tests.

### Hard Rules

```text
Python Formatter = RUFF
Python Linter = RUFF
Python Type Checker = PYRIGHT
Production Type Discipline = STRICT-FIRST
Test Runner = PYTEST
Unknown Markers = ERROR
Import Architecture = IMPORT LINTER
Semantic Architecture = CUSTOM PYTEST ARCHITECTURE TESTS
Required PR Tests = NO LIVE EXTERNAL PROVIDER
Coverage = BRANCH-AWARE, GLOBAL FAIL-UNDER 80%, AFTER EXECUTABLE PRODUCTION CODE BEGINS
Warnings = ERROR BY DEFAULT
Flaky Test Auto-rerun = PROHIBITED IN REQUIRED GATE
Dependency Audit = REQUIRED
Secret Detection = REQUIRED
Cross-module Boundary Violation = CI FAILURE
Main Branch = PROTECTED BY REQUIRED CHECKS
Coding Agent CI Bypass = PROHIBITED
Live AI Evaluation = SEPARATE FROM NORMAL DETERMINISTIC MERGE GATE
```

### Decision Boundary

This Decision confirms the full 44-point list (Ruff formatter+linter, no parallel Black/isort/Flake8, Pyright strict-first on Domain/Application/Public Contract, no global `Any`/Ignore, narrow third-party dynamic types at Infrastructure, pytest + strict markers, 8-category test classification, no live provider in Required PR tests, Import Linter, custom Architecture Tests, deterministic Unit tests, isolated Integration tests, Contract tests, E2E failure coverage, Evaluation separation, fixed-fixture Evaluation in PR, Live Evaluation Nightly/manual/release, branch coverage after executable code, 80% fail-under, behavior tests for critical rules, warnings-as-errors, no flaky auto-rerun, Skip/XFail rules, human Snapshot review, pip-audit, Dependabot, Secret Detection, protected main via PR + Required Checks, no enforced 2nd reviewer, user final merge gate, no Coding-Agent CI bypass, 4-layer CI gates, Extended Gate, TypeScript strict, deferred frontend tools, Foundation Skeleton must block real violations, unified local/CI commands) and that this Decision does not lock tool versions, Secret Scanner, frontend tools, or CI YAML, and does not authorize creating Production CI or Skeleton.

This Decision has NOT confirmed: Production Skeleton scope; Foundation Issue breakdown; the first allowed directories/files; the concrete CI Workflow implementation; the Secret Scanner; tool versions; frontend framework and tools; Foundation Work Authorization; RFC-001 overall acceptance conditions.

### Traceability

Related: RFC-001-DQ-01~08; DEC-033 Runtime Reliability; DEC-034 Architecture Readiness; DEC-035 Spike Test Stack; DEC-036 GitHub Workflow; DEC-038 RFC Governance; Spike-001 Regression Evidence; Architecture Baseline v1.

---

## Decision Question 10: Production Skeleton Scope, Foundation Authorization Gate and RFC Closure

> **Status:** `ACCEPTED`
> **User Decision:** `ACCEPTED`
> **RFC-001 Status:** `DRAFTING`

### Decision

RFC acceptance and implementation authorization are strictly separate.

RFC-001 final acceptance opens **Foundation Planning only** — it does not authorize Foundation Implementation, Business Implementation, or automatic creation of any production code.

Each Foundation Issue requires **separate explicit user authorization**. Accepting RFC-001 (or DQ-10) does not authorize development.

Initial Foundation Work is limited to **package, quality tooling, architecture tests, CI and repository security**. Business modules, persistence, API, workers, production LangGraph, model runtime, retrieval runtime and observability remain unauthorized.

### Acceptance and Authorization Separation

```text
RFC-001 Acceptance
≠ Foundation Planning Authorization
≠ Foundation Implementation Authorization
≠ Business Implementation Authorization
```

Accepting a Decision Question does not authorize development. Accepting RFC-001 as a whole only makes Repository and Application Architecture the formal Architecture Baseline — it does not automatically authorize production implementation.

### Current Authorization State

```text
RFC-001 Status = DRAFTING

Foundation Planning Status = NOT AUTHORIZED
Foundation Implementation Status = NOT AUTHORIZED
Business Implementation Status = NOT AUTHORIZED

Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
Production Implementation = NOT AUTHORIZED
```

After DQ-10 acceptance, the only permitted next step is **RFC-001 Final Consistency Review**. No Production Skeleton may be created.

### RFC-001 Final Acceptance Flow

```text
RFC-001-DQ-10 = ACCEPTED
↓
Archive DQ-10
↓
RFC-001 Final Consistency Review
↓
RFC-001 Final Review Report
↓
User explicitly accepts RFC-001
↓
RFC-001 Status = ACCEPTED
↓
Merge RFC-001 PR
↓
Close RFC-001 Issue
↓
Delete RFC Branch
```

PR Merge cannot replace user acceptance. Before the user explicitly accepts RFC-001:

- RFC-001 stays `DRAFTING`;
- RFC-001 PR must NOT be merged;
- RFC-001 Issue stays OPEN;
- Foundation Planning must not start automatically.

### RFC-001 Acceptance Result

After the user finally accepts RFC-001:

```text
RFC-001 Status = ACCEPTED

Foundation Planning Status = AUTHORIZED
Foundation Implementation Status = NOT AUTHORIZED
Business Implementation Status = NOT AUTHORIZED

Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
Production Implementation = NOT AUTHORIZED
```

RFC-001 acceptance opens **Foundation Planning only**. It does NOT open: automatic Foundation Issue creation, automatic Foundation Work execution, automatic Production Skeleton, or business feature development.

### Foundation Implementation Authorization

Each Foundation Issue must be individually and explicitly authorized by the user.

```text
RFC-001 = ACCEPTED
↓
Generate Foundation Issue Candidates
↓
User reviews scope and dependencies
↓
User explicitly authorizes one Foundation Issue
↓
Create Issue
↓
Create Branch
↓
Create PR
↓
Execute bounded Foundation Work
↓
User reviews and merges
```

Authorized Foundation Planning does not auto-execute all Foundation Issues.

### Foundation Work Definition

Foundation Work establishes the engineering foundation for production code to safely enter the Repository. Permitted scope includes:

- Python Package base; Python Version Constraint; Dependency Manifest; Lockfile
- Ruff; Pyright; pytest; Coverage; Import Linter; Architecture Tests
- GitHub Actions; Dependency Audit; Secret Detection; Dependabot
- PR / Issue Templates; local unified quality commands; Backend Developer Documentation

Foundation Work does NOT include business capability implementation.

### Initial Foundation Skeleton Scope

After RFC-001 final acceptance AND a specific Foundation Issue is authorized, the following may be created on demand:

```text
apps/
└── backend/
    ├── pyproject.toml
    ├── uv.lock
    ├── .python-version
    ├── README.md
    ├── src/
    │   └── ai_ecommerce_agent/
    │       ├── __init__.py
    │       └── py.typed
    └── tests/
        ├── architecture/
        ├── unit/
        └── contract/
```

Repository-level (per authorized scope):

```text
.github/
├── workflows/
├── ISSUE_TEMPLATE/
└── pull_request_template.md

scripts/
tooling/
```

Only files and directories with real responsibilities may be created. Do NOT bulk-create empty Packages to match the architecture diagram.

### Business Module Creation Boundary

The first Foundation Work does NOT create:

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

Business modules may only be created on demand after:

```text
Relevant DEC
+ Relevant Spec
+ Accepted RFC
+ Authorized Implementation Issue
```

Do NOT create empty business modules under the pretext of "setting up the Skeleton early".

### Platform Boundary

The first Foundation Work does NOT create concrete production platform implementations:

```text
platform/persistence/
platform/workflow_runtime/
platform/retrieval_runtime/
platform/model_runtime/
platform/observability/
```

These await acceptance and authorization of RFC-002 (Persistence), RFC-003 (Workflow Runtime), RFC-005 (Retrieval), RFC-006 (LLM Runtime), RFC-007 (Observability) respectively.

### Orchestration Boundary

The first Foundation Work does NOT create: Production LangGraph Graph, Graph Nodes, Graph State, Routing, Checkpoint Adapter, Retry Runtime, Resume Runtime, or Worker Runtime. Awaits RFC-003 ACCEPTED + Authorized Runtime Implementation Issue.

### Entrypoint Boundary

- **API** — no API Framework, Routes, Request/Response Schema, Authentication, Human Review Endpoint, Polling/SSE/WebSocket. Awaits RFC-004.
- **Worker** — no Worker, Queue, Durable Dispatch, Job Consumer, Lease, Heartbeat, Resume Consumer. Awaits RFC-003.
- **CLI** — no empty CLI Entrypoint required. Production CLI should be created in an explicit Runtime or Management Issue.

### Bootstrap Boundary

Although the architectural position of `bootstrap/` is confirmed, the first Foundation Work does NOT implement Production Bootstrap, because the Settings Library, Database, Runtime, API, Worker, Model Provider, and Retrieval are all unselected. Production Bootstrap awaits the relevant Accepted RFCs and implementation authorization.

### Persistence Prohibition

The first Foundation Work must NOT create: Production Database, ORM, Migration, Repository Implementation, Unit of Work Implementation, Database Session, Current Truth Table, Version Table, Evidence Link Table, Audit Table, Idempotency Table, or Review Table. Awaits RFC-002.

### Workflow Runtime Prohibition

The first Foundation Work must NOT create: Production LangGraph, Graph State, Checkpointer, Workflow Worker, Queue, Durable Dispatch, Resume Runtime, Cancellation Runtime, or Recovery Runtime. Awaits RFC-003.

### API and Human Review Prohibition

The first Foundation Work must NOT create: API Framework, Task Endpoint, Run Endpoint, Review Endpoint, Submit/Resume Protocol, Authentication, Authorization, or Frontend Status Protocol. Awaits RFC-004.

### Retrieval Prohibition

The first Foundation Work must NOT create: Source Parser, Fragmentation, Embedding, Vector Store, Index, Retrieval Runtime, or EvidencePackage Runtime. Awaits RFC-005.

### LLM Runtime Prohibition

The first Foundation Work must NOT create: Model Provider, Provider Client, Prompt Registry, Structured Output Runtime, Retry/Repair Runtime, Provider Fallback, or Live Model Evaluation Runtime. Awaits RFC-006.

### Observability Prohibition

The first Foundation Work must NOT create: Production Trace Provider, Metrics Exporter, Alerting, Dashboard, Incident Runtime, or Operator Recovery Queue. Awaits RFC-007.

### Frontend Boundary

The first Foundation Work does NOT create: Frontend Framework, Web Application, Human Review UI, Task Dashboard, Generated API Client, or Frontend Runtime. Awaits a formal Frontend Architecture Decision and authorized Issue.

### Spike-001 Boundary

Spike-001 stays in `spikes/`. It serves only as: Architecture Evidence, Failure Catalogue, Regression Scenario Reference, Acceptance Criteria Input, Recovery Test Design Input, Trace Requirement Input.

Permitted extraction: test scenarios, failure modes, design constraints, acceptance criteria, Trace field requirements, Recovery test approaches.

Prohibited:

```text
Copy Spike Source
↓
Rename Package or Imports
↓
Move into Production Package
```

Production Implementation must be redesigned and re-implemented based on Accepted RFCs.

### Foundation Issue Candidates

After RFC-001 final acceptance, the following Foundation Issue Candidates may be generated.

**FND-001: Backend Package and Local Tooling Foundation** — scope: `apps/backend/`; Python 3.13 Constraint; `pyproject.toml`; `uv.lock`; `.python-version`; Backend Package Root; `py.typed`; Ruff; Pyright; pytest; Coverage base config; unified local commands; Backend README. Excludes: business modules, Bootstrap, API, Database, LangGraph, Worker, Provider.

**FND-002: Architecture Enforcement and Test Foundation** — depends on FND-001. Scope: Import Linter; `tests/architecture/`; Layer Contracts; Public Facade Contract; DAG Contract; Spike Isolation; Architecture Fixture; Negative Architecture Tests; pytest Strict Marker; test classification base; Architecture Test Documentation. Excludes: real business module tests, Production Repository, Production Graph Runtime, Provider Adapter.

**FND-003: CI, Security and Repository Protection** — depends on FND-001 + FND-002. Scope: GitHub Actions; stable Required Check Names; Ruff; Pyright; pytest; Architecture Checks; `pip-audit`; Secret Detection; Dependabot; PR Template; Issue Template; Branch Protection; Local/CI Command Consistency. Excludes: Deployment Pipeline, Production Environment, Cloud Infrastructure, Container Registry, Live Model Evaluation, Production Runtime.

### Foundation Dependency Order

```text
FND-001 → FND-002 → FND-003
```

Each Foundation Issue uses: One Issue → One Branch → One PR → Required Verification → User Merge Gate. Do NOT merge into one unbounded large Foundation PR unless the user explicitly modifies this plan later.

### Architecture Fixture Boundary

While business modules do not yet exist, do NOT create fake production business modules to validate Architecture Rules. Test Fixtures simulating violations (Domain importing Infrastructure, module bypassing Public Facade, circular dependency, Production importing Spike) may be built under `apps/backend/tests/architecture/fixtures/`. Fixtures belong only to Test Code, must not be imported by Production, do not represent real production modules, and exist to prove the Architecture Checker detects violations.

### Foundation Verification Requirements

A Foundation PR must at least prove: (1) Formatting Violation fails; (2) Lint Violation fails; (3) Type Error fails; (4) Domain importing Infrastructure fails; (5) cross-module Public Facade bypass fails; (6) module dependency cycle fails; (7) Production importing Spike fails; (8) unregistered pytest Marker fails; (9) failing Unit Test blocks Merge; (10) Coverage Gate below threshold fails once enabled; (11) Dependency Vulnerability is detected; (12) Secret Detection blocks merge; (13) local and CI use the same tool config; (14) Required Check Names are stable; (15) a deliberately constructed Architecture Violation is correctly rejected.

Do NOT forge quality evidence via empty tests or invalid Fixtures.

### Foundation PR Evidence

Each Foundation PR must output: created/updated files; local commands run; test results; Architecture Check results; Type Check results; Dependency Audit results; Secret Scan results; Scope Deviations; unfinished items; corresponding Issue; related DEC and RFC; whether a new Architecture Decision was discovered; whether a Mandatory Stop Condition was triggered.

### Mandatory Stop Conditions

The Foundation Agent must stop when it needs to: (1) choose a Database; (2) choose an ORM; (3) choose an API Framework; (4) choose a Worker Framework; (5) choose a Queue or Broker; (6) create production LangGraph; (7) create a business module; (8) copy Spike Source; (9) lower an Accepted Quality Gate; (10) modify an Accepted RFC; (11) change the Repository Root Structure; (12) resolve a contradiction between DQs; (13) when a tool cannot implement an accepted Architecture Contract; (14) modify Branch Protection to bypass a failure; (15) when a Secret or real credential is found; (16) when implementation scope exceeds the current Issue; (17) create a technical implementation within a later RFC's scope. Must submit a Decision Conflict Report or Mandatory Stop Report. Do NOT decide silently.

### Production Business Implementation Gate

Even after RFC-001 and all Foundation Issues are complete, business development must NOT start automatically. Per DEC-038, after `RFC-001 = ACCEPTED`, `RFC-002 = ACCEPTED`, `RFC-003 = ACCEPTED`, the following may be generated: MVP Roadmap Draft v0, Epic Skeleton, Foundation Dependency Graph, Foundation/Runtime Issue Candidates. The full business Roadmap, Implementation Backlog and Business Issues must wait for `RFC-001 through RFC-007 = ACCEPTED`.

### Hard Rules

```text
RFC-001 Acceptance:          DOES NOT AUTHORIZE IMPLEMENTATION
DQ-10 Acceptance:            DOES NOT AUTHORIZE IMPLEMENTATION
Foundation Planning:         AUTHORIZED ONLY AFTER RFC-001 FINAL ACCEPTANCE
Foundation Implementation:   REQUIRES SEPARATE EXPLICIT USER AUTHORIZATION
Business Implementation:     REMAINS UNAUTHORIZED
Initial Foundation Scope:    PACKAGE + QUALITY + ARCHITECTURE TESTS + CI + REPOSITORY SECURITY
Initial Business Modules:    NOT CREATED
Production Bootstrap:        NOT IMPLEMENTED
API / Worker / CLI:          NOT IMPLEMENTED
Database / ORM / Migration:  NOT IMPLEMENTED
Production LangGraph:        NOT IMPLEMENTED
Model / Retrieval / Observability: NOT IMPLEMENTED
Spike Source Migration:      PROHIBITED
Foundation Issue Order:      FND-001 → FND-002 → FND-003
RFC-001 Final Acceptance:    REQUIRES FINAL CONSISTENCY REVIEW AND EXPLICIT USER ACCEPTANCE
```

### Decision Boundary

This Decision confirms (34 points): RFC-001 Acceptance does not auto-authorize Foundation Implementation; DQ-10 Acceptance does not auto-authorize Foundation Implementation; Final Consistency Review is required after DQ-10; RFC-001 must be explicitly accepted by the user; RFC-001 acceptance opens only Foundation Planning; each Foundation Issue requires separate user authorization; Foundation, Business and Production Implementation status are managed separately; initial Foundation Work covers only Package, quality tooling, Architecture Tests, CI and Repository Security; the first batch may create `apps/backend/` and a formal Python Package Root; may create `pyproject.toml`, Lockfile, `.python-version` and Backend README; may create Architecture Test Fixtures; may configure Ruff, Pyright, pytest, Coverage, Import Linter and `pip-audit`; may create GitHub Actions, Dependabot, Secret Detection and PR/Issue Templates; does NOT bulk-create business modules, concrete `platform/` implementations, Production Orchestration, API/Worker/Production CLI, Production Bootstrap, Database/ORM/Migration/Repository/Unit of Work, Queue/Dispatch/Checkpointer/Worker Runtime, or Model/Retrieval/Observability Runtime; Spike-001 serves only as Evidence and Test Design Input; copying or renaming Spike Source into Production is prohibited; Foundation is planned as FND-001/FND-002/FND-003 executed in dependency order with independent Branch/PR per Issue and full verification evidence per PR; the Agent must stop on unresolved architecture questions; RFC-001 stays `DRAFTING` after DQ-10; RFC-001 becomes `ACCEPTED` only after Final Review and explicit user acceptance; Architecture Readiness stays `CONDITIONALLY READY` and Business Implementation stays unauthorized after RFC-001 acceptance; Roadmap Draft v0 is generated only after RFC-001~003 accepted; Roadmap v1 and the full business Backlog only after RFC-001~007 accepted.

### Traceability

Related: RFC-001-DQ-01 (Modular Monolith); DQ-02 (Language Boundary); DQ-03 (Repository Layout); DQ-04 (Layer and Transaction Boundary); DQ-05 (Skill Architecture); DQ-06 (Bootstrap and Configuration); DQ-07 (Process Boundary); DQ-08 (Public Contract and DAG); DQ-09 (Quality Toolchain); DEC-034 (Architecture Readiness Gate); DEC-036 (GitHub Execution Governance); DEC-038 (RFC Governance); Spike-001 Evidence; Architecture Baseline v1; MVP Traceability Matrix.

---

## Open Questions

DQ-01~DQ-10 已全部 ACCEPTED。RFC-001 下一步为 **RFC-001 Final Consistency Review**（见 Decision Question 10）；RFC-001 保持 `DRAFTING`，Foundation Planning 未开始。以下为仍需后续 RFC / Decision 收敛的开放技术问题：

1. Durable Dispatch 的具体实现（RFC-002 / RFC-003）。
2. API Framework 与 HTTP Endpoint（RFC-004）。
3. Database 和 ORM（RFC-002）。
4. Queue / Broker / Worker Framework（RFC-003）。
5. Checkpoint Backend 与 Resume State Machine（RFC-003）。
6. Polling、SSE 或 WebSocket（RFC-004）。
7. Settings / Configuration Library。
8. Secret Manager 与生产凭证来源 / Secret Scanner。
9. Prompt Registry 与版本注册形式。
10. Evaluation Framework 与评测数据集形式。
11. Event Bus / Outbox（跨进程可靠调度）。
12. Schema Library 与 Contract Test Framework。
13. Deployment Platform 与 Process Health Check / Worker Scaling Policy。
14. Graph Version Migration（RFC-003 / RFC-007）。
15. 质量工具版本（Lockfile 固定）、前端 Framework 与工具、CI Workflow 具体实现。

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
- RFC-001-DQ-05：Skill Code Shape and Architectural Relationships
- RFC-001-DQ-06：Dependency Injection, Configuration and Application Bootstrap
- RFC-001-DQ-07：Process Boundaries and Sync/Async Execution Strategy
- RFC-001-DQ-08：Module Public Contracts, Cross-module Collaboration and Cycle Governance
- RFC-001-DQ-09：Quality Toolchain, Architecture Enforcement, CI Quality Gates and Test Baseline
- RFC-001-DQ-10：Production Skeleton Scope, Foundation Authorization Gate and RFC Closure

## Related Specifications

- specs/workflow/workflow-state-specification
- specs/runtime/workflow-runtime-failure-recovery-retry-and-observability
- architecture/system-architecture

## Related Spike Evidence

- Spike-001（LangGraph Runtime and Recovery）
