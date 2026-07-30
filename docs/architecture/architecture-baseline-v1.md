# Architecture Baseline v1

> **Status: DRAFT — Current Architecture Truth（基于已接受 DEC-001—DEC-037 综合）**
> **治理来源：** 本文件综合当前**已接受**的 DEC 与 Specs，形成 Current Architecture Truth。**不发明任何新的生产技术选择。**
> **关联：** [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md) · [../rfcs/rfc-register.md](../rfcs/rfc-register.md) · Spike-001（MERGED）
> **Base Commit：** `a60ff3b6a24bf8b35e1c2ba1031038bb7123a578`

---

## 0. 本文档定位与纪律

- 本文件描述「系统当前应该怎样工作」，内容**只能来自用户明确接受的 Decision**。
- Spike-001 的临时技术选择**一律标注** `Validated Temporary Implementation / Not Production Commitment`，**不**视为生产承诺。
- 任何尚未通过 RFC + Accepted Decision 收敛的生产技术（数据库 / Checkpointer / API / ORM / Retrieval / Observability / 部署平台）在本文件中标记为 **`PENDING RFC`**，**不得**由 Coding Agent 临场选择。

## 1. 系统分层（System Architecture）

> 来源：DEC-011 / DEC-012 / DEC-013 / DEC-021 / DEC-023 / DEC-024。

- **确定性 Workflow 编排**：以 StateGraph 表达核心工作流，LLM 推理受约束（DEC-011 / DEC-023）。
- **单审查节点 + 异常暂停**：核心流程单一 Human Review 节点，异常路径可暂停（DEC-007）。
- **MVP 不采用 Multi-Agent**：保留 Bounded Worker 扩展空间（DEC-021）。
- **分层状态**：业务状态 / 执行状态 / 检索证据 / Checkpoint 分离（DEC-012 / DEC-013 / DEC-024）。
- **任务级持久状态**：支持跨会话 Resume（DEC-013）。

```text
[Product Input] -> [Workflow Orchestration (StateGraph)]
   -> Skill Nodes (facts / insights / positioning / review / brief)
   -> [Human Review Node] -> [Approved Strategy]
   -> [Platform Adapter (Xiaohongshu brief mapping)]
```

## 2. 状态与版本模型（State & Versioning）

> 来源：DEC-024 / DEC-025 / DEC-029 / DEC-033。Spike 行为级验证：✅。

- **Versioned Domain State**：业务域以 Domain Version 演进；`current_truth_pointer` 指向当前有效版本；旧版本 `superseded`。
- **Compact Graph State**：Graph State 仅存运行身份 + `*_version_id` 引用，不存业务正文。
- **三类存储分离**：Business（Current Truth）/ Runtime（执行记录）/ Checkpoint（Graph 检查点）物理分离；**Checkpoint ≠ Current Truth**。
- **运行身份分层（DEC-033）**：`task_id` / `workflow_run_id` / `skill_run_id` / `node_execution_id` / `attempt_id` / `error_id` / `trace_id` / `recovery_case_id` 全链可关联。

## 3. 事务与幂等（Transaction & Idempotency）

> 来源：DEC-029 / DEC-033。Spike 行为级验证：✅。

- **原子提交契约**：每次正式业务提交在**一个事务**内完成：Create Domain Version + Evidence Links + Update Current Truth Pointer + Update Stage State + Business Audit + Idempotency Record；任一失败整体回滚。
- **幂等**：同一逻辑幂等键重放不产生重复版本；Retry / Recovery 复用同一幂等键。
- **节点不绕过**：Graph 节点不直接写 Current Truth，统一经 Business Commit 路径。

## 4. Human Review 与 Approved Strategy

> 来源：DEC-029。Spike 行为级验证：✅。

- **节点边界**：`create_review_package`（构建固定版本包，幂等）与 `interrupt()`（暂停等待）**分离**；Review Submit 为**独立业务事务**。
- **No Stale Submission**：过期/已 supersede 的 Review Package 不得再次提交（拒绝）。
- **Safe Resume**：Resume 使用相同 `thread_id` + 新 `run_id`，不重建 Review Package、不重生成 Positioning；stale/foreign Checkpoint 在业务写入前被拒绝。

## 5. 检索与证据（Retrieval & Evidence）

> 来源：DEC-014 / DEC-025 / DEC-032。Spike 微型验证：✅（降级不伪造）。

- **On-demand Hybrid RAG**：按需混合检索（词法/向量/融合），分层数据访问（DEC-014）。
- **Versioned Sources / Fragments / Evidence Links**：来源与证据版本化、可追溯（DEC-025）。
- **降级不伪造**：检索降级时记录 degraded 状态，不伪造候选或覆盖度。
- **生产实现**：`PENDING RFC`（Source Processing and Retrieval Architecture）。

## 6. 运行时失败 / 恢复 / 重试 / 可观测（Runtime Reliability）

> 来源：DEC-033。Spike 行为级验证：✅。

- **有界重试**：仅重试 transient 基础设施错误；non-transient（如 Invalid Structured Output）不重试；预算耗尽抛 `RetryBudgetExhausted`（无无限重试）。
- **取消无部分写入**：取消后不留 partial business state。
- **Manual Recovery**：失败提交经同一幂等键恢复，不重复。
- **Observability**：结构化 Trace + 运行身份关联 + Checkpoint Summary + JUnit（**生产 Provider `PENDING RFC`**）。

## 7. 集成边界（Integration Boundaries）

> 来源：DEC-004 / DEC-020 / DEC-031。

- **平台中立核心 + Xiaohongshu Demo**（DEC-004）。
- **MVP 四大核心 Skill + Xiaohongshu Adapter**（DEC-020）。
- **Xiaohongshu Brief Mapping Adapter 契约**（DEC-031）。
- **生产 API / Human Review Protocol**：`PENDING RFC`。

## 8. 临时技术栈（Spike-001）

> 以下仅为 Spike-001 的**临时**落地，**不构成生产承诺**。

```text
Validated Temporary Implementation — Not Production Commitment
- Python 3.13（uv 管理）          [临时]
- LangGraph StateGraph 1.2.9      [临时，精确固定]
- Synchronous Invoke              [临时]
- 三个分离 SQLite + SqliteSaver   [临时 Checkpointer]
- Python sqlite3 Transactions     [临时]
- Scripted Model + Mock Retrieval [临时]
- pytest + 本地 JSONL Trace + CLI [临时]
```

> 生产后端语言 / 数据库 / Checkpointer / ORM / LLM / Retrieval / Observability / 部署平台：**全部 `PENDING RFC`**（见 [../rfcs/rfc-register.md](../rfcs/rfc-register.md)）。

## 9. RFC Governance and Production Decision Gate

> 来源：DEC-038。

进入正式生产实现前，每个生产技术域必须先经过 RFC 提案、用户 Acceptance Gate 并被接受为 `ACCEPTED`。

```text
RFC-001 Repository and Application Architecture [DRAFTING — DQ-01 ACCEPTED]
↓
RFC-002 Persistence and Transaction Architecture
↓
RFC-003 LangGraph Runtime and Checkpoint Architecture
↓
RFC-004 API and Human Review Protocol
↓
RFC-005 Source Processing and Retrieval Architecture
↓
RFC-006 LLM Runtime and Structured Output
↓
RFC-007 Observability and Runtime Operations
```

- PR Merge 不自动等于 RFC Accepted。
- 每个 RFC 使用独立的 Issue / Branch / PR。
- 未接受对应 RFC 前，不得开始该域的生产实现；Coding Agent 不得临场选择生产数据库 / Checkpointer / API / ORM / Retrieval / LLM Runtime / Observability。

## 10. 已确认 Repository 与 Package 目录结构（RFC-001-DQ-03）

> 来源：RFC-001-DQ-03（ACCEPTED）。

### 10.1 Repository Model

项目采用：

```text
Single Repository
+
Multi-project Layout
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

### 10.2 Application Roots

| 应用 | 路径 | 说明 |
|---|---|---|
| Python Backend | `apps/backend/` | 生产源码根路径 `apps/backend/src/ai_ecommerce_agent/` |
| TypeScript Frontend | `apps/web/` | 本 Decision 不选择具体前端 Framework |
| Shared Contracts | `contracts/` | OpenAPI / JSON Schema / Error Codes 等正式契约 |

正式 Python Package 名：

```text
ai_ecommerce_agent
```

### 10.3 Backend Package Organization

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

### 10.4 Business Capability Modules

业务能力位于 `modules/`，概念模块包括：

```text
product_intake/
customer_insight/
product_positioning/
human_review/
marketing_brief/
xiaohongshu_adapter/
source_evidence/
```

单个业务模块内部采用：

```text
domain/
application/
infrastructure/
public.py
```

- `domain/`：Entity、Value Object、Domain Service、Business Rule、Domain Validation、Evidence/Review/Invalidation Rule
- `application/`：Command、Query、Application Service、Port、Result、Transaction/Idempotency/Audit Coordination
- `infrastructure/`：Repository Implementation、Persistence Adapter、External Provider Adapter、ORM Mapping
- `public.py`：Public Command、Query、Service Protocol、Result、Error、Published Event

Domain 不得依赖 LangGraph / Web Framework / ORM / Database Driver / Model SDK / Vector DB SDK / Message Queue / Checkpoint Backend / Observability Provider。

Application 可以依赖本模块 Domain，不得依赖具体 Infrastructure Implementation。

Infrastructure 负责实现 Application 或 Domain 定义的 Port。

### 10.5 Platform Capabilities

平台能力位于 `platform/`，概念结构：

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

平台模块不等于业务模块；负责多个业务能力共享的技术设施和 Adapter，但不得拥有业务规则。

### 10.6 Orchestration Boundary

LangGraph 与跨模块 Workflow 位于 `orchestration/`，概念结构：

```text
orchestration/
├── workflows/
└── adapters/
    └── langgraph/
```

跨模块主流程属于 Application-level Orchestration，不属于单个业务模块内部。

`orchestration/` 可以依赖各业务模块的公开 Application Contract 和 Workflow Runtime Platform，不得实现 Domain Rule、拥有 Business Transaction、直接更新 Current Truth、直接使用其他模块 Repository Implementation、直接写 ORM Model、或将完整 Domain Object 放入 Graph State。

Graph Node 的完整职责将在 RFC-001-DQ-04 中确认。

### 10.7 Entrypoints

外部入口位于 `entrypoints/`：

```text
entrypoints/
├── api/
├── worker/
└── cli/
```

- `api/`：HTTP Route、Request/Response Schema、Authentication Adapter、API Error Mapping
- `worker/`：Background Job Consumer、Scheduled Job、Queue Handler、Workflow Worker Entry
- `cli/`：管理命令、数据检查、Recovery 入口、本地维护任务

Entrypoint 不得放置 Domain Rule 或业务事务，不得绕过 Application Service 直接修改业务数据。

### 10.8 Bootstrap and Composition Root

依赖装配位于 `bootstrap/`，负责：

- 加载 Configuration；
- 创建 Application；
- 创建数据库连接；
- 创建 Repository Implementation；
- 创建 Provider Adapter；
- 装配 Workflow；
- 装配 API、Worker、CLI；
- 管理 Application Lifecycle。

Bootstrap 是少数允许同时了解 Application Port、Infrastructure Implementation、Orchestration 和 Entrypoint 的区域。具体 Dependency Injection 技术尚未选择。

### 10.9 Shared Kernel

允许保留严格受限的 `shared_kernel/`，只允许放置：

- 通用 Identifier 类型；
- Clock Protocol；
- 无业务语义的 Result；
- 通用 Error Base；
- 基础 Typing Utility。

不得放置具体业务规则、Repository Implementation、LangGraph State、ORM Base Model 或各业务模块为了方便而共享的任意代码。

### 10.10 Test Layout

正式后端测试位于 `apps/backend/tests/`，分为：

```text
unit/
integration/
contract/
architecture/
e2e/
```

- Unit：Domain Rule、Application Service、Validator、纯函数；不依赖网络/数据库/LangGraph/真实模型
- Integration：Repository、Transaction、Database、Checkpointer、Provider/Retrieval Adapter、Workflow Runtime Integration
- Contract：API、Provider、Repository、Generated Schema、前后端 Contract、Adapter Compliance
- Architecture：Import Boundary、Domain→LangGraph 禁止、模块内部目录隔离、Production↔Spike 隔离
- E2E：完整 Workflow、Human Review、Retry/Recovery、API 到业务结果、关键 Demo 场景

Unit Test 大体镜像生产模块；Integration / Contract / Architecture / E2E 按验证场景组织，不要求每个源码文件机械对应一个同名测试文件。

### 10.11 Database Migrations

正式数据库 Migration 位于 `apps/backend/migrations/`，不放入可 Import 的生产 Python Package。具体 Migration Tool、Database 和 Schema Strategy 由 RFC-002 决定。

### 10.12 Configuration and Secret Boundary

目录层面允许未来使用：

```text
apps/backend/.env.example
apps/backend/src/ai_ecommerce_agent/bootstrap/settings.py
```

- `.env.example` 只能包含变量名称和非敏感示例；
- `.env`、Secret、Token 不得提交；
- Domain 和 Application 不直接读取环境变量；
- Configuration 由 Bootstrap 加载并注入。

### 10.13 Spike and Prototype Isolation

技术验证继续位于 Repository 根目录 `spikes/` 和 `prototypes/`。

生产 Package 禁止 `from spikes...` / `from prototypes...`。

允许关系：Spike Evidence → informs RFC and Production Tests → production implementation is rebuilt under accepted architecture。

禁止关系：Spike Source → rename or move → Production Source。

现有 Spike-001 继续作为 Architecture Evidence 保存。

### 10.14 Import Boundary

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
domain → application / infrastructure / orchestration / entrypoints
application → infrastructure implementation / LangGraph / API framework
module A → module B infrastructure / private implementation
production → spikes / prototypes
```

完整职责和依赖规则将在 RFC-001-DQ-04 中确认。

### 10.15 Cross-module Data Boundary

模块之间不得使用数据库表作为隐式 API。即使共享同一 Database Instance，也不得直接写入其他模块内部表、通过其他模块 ORM Model 修改数据、绕过 Application Contract、或直接调用其他模块 Repository Implementation。

跨模块读取和写入必须通过 Public Application Contract、Application Port、明确 Query Service 或用户后续确认的 Published Application Event。

### 10.16 Directory Creation Boundary

接受本 Decision 不等于立即创建生产目录。本阶段只授权更新 RFC / Architecture Baseline / Traceability / RFC Register / 记录未来 Architecture Test 要求。

暂不授权：

- 创建 `apps/backend/src/ai_ecommerce_agent/`；
- 创建正式 Python Package；
- 批量创建空目录；
- 创建 Production Skeleton；
- 迁移 Spike 代码；
- 创建业务模块源码；
- 创建数据库 Migration；
- 创建 API、Worker 或 CLI 实现。

正式 Skeleton 必须等待 `RFC-001 = ACCEPTED` + Foundation Work explicitly authorized。

### 10.17 Decision Boundary

已确认：

1. 单仓库、多项目布局；
2. `apps/` 为应用根；
3. Python 后端位于 `apps/backend/`；
4. TypeScript 前端位于 `apps/web/`；
5. 共享契约位于 `contracts/`；
6. 后端采用 `src/` Layout；
7. 正式 Python Package 名为 `ai_ecommerce_agent`；
8. 生产源码唯一根路径为 `apps/backend/src/ai_ecommerce_agent/`；
9. 业务能力模块优先组织；
10. 业务模块内部使用 `domain/application/infrastructure/public` 边界；
11. 平台能力位于 `platform/`；
12. LangGraph 与跨模块 Workflow 位于 `orchestration/`；
13. API/Worker/CLI 位于 `entrypoints/`；
14. 依赖装配位于 `bootstrap/`；
15. `shared_kernel/` 必须最小化；
16. 测试分为 unit/integration/contract/architecture/e2e；
17. Migration 位于 `apps/backend/migrations/`；
18. Spike/Prototype 与生产代码物理隔离；
19. 模块间通过公开 Application Contract 协作；
20. 数据库表不能作为隐式模块 API；
21. Architecture Tests 必须验证 Import Boundary；
22. 目录按需创建；
23. 当前不创建生产 Skeleton，不迁移 Spike 代码。

尚未确认：

- Domain、Application、Infrastructure、Entrypoint 的完整职责；
- Port 应由 Domain 还是 Application 定义；
- Transaction 在哪一层开始；
- Graph Node 是否可以直接访问 Repository Interface；
- API Handler 是否可以调用 Domain；
- 跨模块同步调用和事件规则；
- Dependency Injection 形式；
- Configuration 技术；
- Architecture Test 工具；
- API Framework、Database、ORM、Worker、Queue、Deployment Platform。

## 11. 已确认生产技术语言边界（RFC-001-DQ-02）

> 来源：RFC-001-DQ-02（ACCEPTED）。

AI Ecommerce Agent MVP 与首个生产版本采用：

```text
Production Backend Language:
Python 3.13

Frontend Language:
TypeScript

Workflow Runtime:
Python LangGraph

Framework Boundary:
Domain and Application remain independent of LangGraph-specific state and checkpoint types
```

### 10.1 Backend Language

正式后端统一使用 Python，覆盖：

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

当前不采用 Python + TypeScript 混合后端。

Python 版本基线：

```text
Python >=3.13,<3.14
```

Patch 升级可通过 Dependency Compatibility Test + Full Test Suite + Normal PR Review 完成；Minor/Major 升级若改变并发模型、Worker 模型、Deployment、Runtime Isolation 或 Security Boundary，则须补充 RFC 或正式技术 Decision。

### 10.2 Frontend Language

正式 Web Frontend 使用 TypeScript。前端不属于 Python 后端 Package。

前后端通过版本化契约协作：

```text
OpenAPI / JSON Schema / Generated Client Types / Error Code Registry
```

具体 API Framework、Schema Generator 和前端 Framework 尚未确认。

### 10.3 LangGraph Binding Boundary

生产 Workflow Runtime 使用 Python LangGraph，但逻辑关系是：

```text
We choose Python as the backend language
therefore the Workflow Runtime uses Python LangGraph
```

LangGraph 位于 **Orchestration / Workflow Runtime Boundary**，不属于 Domain Layer。

推荐调用关系：

```text
LangGraph Node
↓
Application Service
↓
Domain + Repository / Provider Interfaces
```

- Domain Layer 不得依赖 LangGraph，也不得依赖 Web Framework、ORM、Database Driver、Model SDK、Vector DB SDK、Message Queue、Checkpoint Backend 或 Observability Provider；
- Application Service 不得要求调用方传入 LangGraph State、StateSnapshot、Checkpoint Object 或 LangGraph Runtime Context；
- LangGraph Node 只负责构造业务 Command、调用 Application Service、将 Version ID / Stage Status 写回 Graph State、确定性路由、Interrupt 与 Resume 协调；
- LangGraph Node 不拥有 Domain Rule、Business Transaction、Current Truth 写入规则、Evidence Link 事务、Review Validation、Idempotency、Invalidation 或 Audit 规则。

### 10.4 Framework Replacement Boundary

系统须允许未来替换 Workflow Engine（LangGraph / Temporal / Custom State Machine / Queue Worker 等），替换范围应限于：

```text
Orchestration Layer
Runtime Adapter
Checkpoint Adapter
Worker Integration
```

不应要求重写 Domain、Application Services、Business Validators、Repository Interfaces、Skill Contracts、Evidence Rules 或 Human Review Business Rules。

### 10.5 Future Polyglot Boundary

未来允许特定独立能力采用其他语言，但必须满足至少一种可验证触发条件：

- Python 存在可测量性能瓶颈；
- 关键 SDK 只在其他语言中可靠；
- 模块已有稳定远程接口；
- 模块需要独立扩缩容；
- 独立团队负责该模块；
- 安全或部署要求物理隔离；
- 该能力需要服务多个产品。

不得仅因个人语言偏好引入第二种后端语言。

### 10.6 Decision Boundary

本 Decision 已确认：

1. 后端统一使用 Python 3.13；
2. 前端使用 TypeScript；
3. 不采用双语言后端；
4. Workflow Runtime 使用 Python LangGraph；
5. Domain 不依赖 LangGraph 或具体框架；
6. Application Service 不依赖 Graph State 或 Checkpoint；
7. 前后端通过正式 Schema Contract 协作；
8. Python 与 TypeScript 不直接共享业务源码；
9. 未来可在明确边界引入其他语言；
10. Spike Python 代码不得直接成为生产代码。

尚未确认：

- 正式 Repository 和 Package Directory；
- 具体分层目录；
- API Framework；
- Schema Library；
- Dependency Injection；
- Configuration Library；
- Type Checker / Linter；
- ORM；
- Database；
- Worker / Queue；
- Checkpointer；
- Deployment Platform；
- Frontend Framework。

## 11. 已确认应用架构（RFC-001-DQ-01）

> 来源：RFC-001-DQ-01（ACCEPTED）。

AI Ecommerce Agent 的 MVP 与首个生产版本采用：

```text
Application Architecture Style:
Modular Monolith First
```

正式含义：

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

### 11.1 Deployment Boundary

MVP 默认采用：

```text
One Primary Backend Application
```

初始不拆分为独立服务（Task / Workflow / Source / Retrieval / Human Review / Brief / Model Runtime Service）。

### 11.2 Repository Boundary

项目使用一个 Git Repository，但 Repository 内必须维持清晰的模块和依赖边界。

### 11.3 Module Boundary（概念划分）

**Business Capability Modules：**

```text
Product Intake and Fact Extraction
Customer Insight Analysis
Product Positioning
Human Review
Marketing Brief Generation
Xiaohongshu Mapping Adapter
```

**Platform Capability Modules：**

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

### 11.4 Module Collaboration

模块之间必须通过明确边界协作：

- Application Service
- Domain Contract
- Repository Interface
- Provider Interface
- Command
- Query
- Published Application Event

不得任意访问其他模块内部类、绕过 Application Layer 修改数据、直接访问其他模块 Repository Implementation、以数据库表作为隐式 API、通过 LangGraph State 共享完整业务对象、或将 Prompt 作为唯一契约。

### 11.5 Dependency Direction

```text
Interface
↓
Application
↓
Domain

Infrastructure → implements → Repository and Provider Interfaces
```

Domain 不得依赖具体框架、数据库、ORM、LLM SDK、Vector DB、Message Queue、Observability Provider 或部署平台。

### 11.6 Data Ownership Boundary

允许 Modular Monolith 在 MVP 阶段共享一个数据库实例，但必须保持：

```text
Shared Database Instance ≠ Shared Data Ownership
```

必须区分 Business Domain / Workflow Runtime / Checkpoint / Source and Evidence / Retrieval Index / Audit / Observability Data。正式数据库、Schema、ORM 和事务方案由 RFC-002 决定。

### 11.7 Graph and Database Boundary

Graph Node 不得成为业务持久化规则的所有者。在 RFC-001 后续 DQ 接受前，Graph Node 不得临场定义 Domain Version 写入、Current Truth 更新、Evidence Link 事务、幂等、审计或失效逻辑。

### 11.8 Future Service Extraction

必须保留未来服务提取边界，但服务拆分只能由可验证的规模、组织、安全、性能或可靠性需求触发，不得仅因“微服务更先进”而拆分。

### 11.9 Decision Boundary

已确认：

1. Modular Monolith First；
2. 不采用 Multi-service First；
3. One Primary Backend Deployment Unit；
4. One Git Repository；
5. 按业务能力与平台能力划分模块；
6. 模块通过明确接口协作；
7. 不允许任意访问其他模块内部实现；
8. 共享数据库实例不代表共享数据所有权；
9. Domain 不依赖具体框架或基础设施；
10. 保留未来服务提取能力；
11. 服务拆分由可验证需求触发。

尚未确认：

- 正式后端语言：**Python 3.13**（RFC-001-DQ-02 已确认）；
- 正式目录结构：PENDING RFC-001-DQ-03；
- 具体 Domain / Application / Infrastructure / Interface 分层：PENDING RFC-001-DQ-03；
- LangGraph 所属层：**Orchestration / Workflow Runtime Boundary**（RFC-001-DQ-02 已确认）；
- Graph Node 是否可直接访问 Repository：PENDING RFC-001 后续 DQ；
- Skill 代码形态：PENDING RFC-001-DQ-03；
- Repository Interface / Implementation 位置：PENDING RFC-001-DQ-03；
- Dependency Injection：PENDING RFC；
- Configuration Management：PENDING RFC；
- Test Layering：PENDING RFC；
- API / Worker 接入方式：PENDING RFC-001-DQ-03 / RFC-004；
- Production Database / ORM：PENDING RFC-002；
- Web Framework：PENDING RFC；
- Deployment Platform：PENDING RFC。

## 13. 未决技术决策（PENDING RFC）

| 领域 | 状态 | RFC |
|---|---|---|
| Repository and Application Architecture | DRAFTING — DQ-01~03 ACCEPTED | RFC-001 |
| Persistence and Transaction Architecture（生产 DB / ORM） | PENDING RFC | RFC-002 |
| LangGraph Runtime and Checkpoint Architecture（生产 Checkpointer） | PENDING RFC | RFC-003 |
| API and Human Review Protocol | PENDING RFC | RFC-004 |
| Source Processing and Retrieval Architecture | PENDING RFC | RFC-005 |
| LLM Runtime and Structured Output | PENDING RFC | RFC-006 |
| Observability and Runtime Operations | PENDING RFC | RFC-007 |

> RFC-001 仍为 `DRAFTING`，层职责与依赖规则尚未确认。其余 RFC 仍为 `PROPOSED`。上述在生产实现前必须先经 RFC 提案 + 用户 Accepted Decision 收敛；**不得**临场选择。详见 [../decisions/dec-038-rfc-planning-and-dependency-order.md](../decisions/dec-038-rfc-planning-and-dependency-order.md) 与 [../specs/governance/rfc-planning-and-dependency-order.md](../specs/governance/rfc-planning-and-dependency-order.md)。

## 14. Final Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY

Next Topic: RFC-001-DQ-04 Layer Responsibilities and Dependency Rules
```
