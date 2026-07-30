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
RFC-001 Repository and Application Architecture [DRAFTING — DQ-01~06 ACCEPTED]
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

## 10. 已确认 Skill 代码形态与架构关系（RFC-001-DQ-05）

> 来源：RFC-001-DQ-05（ACCEPTED）。

### 10.1 Skill Architectural Position

Skill 是业务模块 Application Layer 内具有明确执行契约、可独立运行和独立评估的**无状态业务能力组件**，落位 `modules/<module>/application/skills/<skill_slug>/`。Skill 不是独立 Package、不是 Domain Service、不是 Application Use Case 同义词，也不是 Entrypoint。

### 10.2 Prepare-Execute-Commit Model

Application Use Case 以 **Prepare–Execute–Commit** 协调 Skill 与业务事务：Prepare 装配 Skill 输入并开启业务事务；Execute 调用 Skill 产出 Candidate Result（业务候选，未落库）；Commit 由 Application Use Case 决定是否写入 Current Truth 并提交业务事务。Skill 只参与 Execute 阶段。

### 10.3 Skill Repository and Transaction Boundary

**Skill Direct Business Repository Access = PROHIBITED；Skill Business Transaction Ownership = NO。** Skill 不读/写 Current Truth、不持久化业务结果、不开启/提交业务事务、不更新 Evidence / Audit / Idempotency；所需数据由 Use Case 在 Prepare 阶段以输入契约注入。

### 10.4 Skill Provider Access Boundary

Skill 只能通过 Application 定义的 **ModelRuntimePort / RetrievalPort** 调用 Provider 能力；**Skill 直接 import 或实例化具体 Provider SDK = PROHIBITED**。Skill 不知道具体 Provider、模型名、连接串或凭证。

### 10.5 Skill LangGraph Boundary

调用链：`LangGraph Node → Stage Application Service → Skill Executor → Skill`。**LangGraph Node 直接调用 Skill = PROHIBITED。** Skill 与 LangGraph Node 不是同一概念、不一一对应；Skill 不感知 LangGraph、不读 Graph State、不写 Checkpoint。

### 10.6 Skill Independent Execution and Version

**Skill Independent Execution = REQUIRED**：Skill 必须能脱离 LangGraph 独立运行与独立评估。Skill 版本分 **Contract / Implementation / Prompt / Output Schema** 四个维度分别管理，可独立演进且须可追踪关联。

### 10.7 Skill Test Boundary

Skill 须支持 **Contract / Unit / Integration / Evaluation / Architecture** 五类测试。Architecture Test 强制：Skill 不直接访问 Repository、不 import Provider SDK、不依赖 LangGraph。

### 10.8 Decision Boundary

已确认：Skill 为 Application Layer 无状态业务能力组件；Prepare–Execute–Commit 协调；Skill 不直接访问 Repository、不拥有业务事务、不更新 Current Truth/Evidence/Audit；仅经 ModelRuntimePort/RetrievalPort 调用 Provider；经 Stage Application Service + Skill Executor 被 LangGraph 间接调用；可独立运行；版本四维度分管；五类测试。

尚未确认：具体模型 Provider、Retrieval Backend、Schema/Validation Library、Prompt Registry、Evaluation Framework、Skill Executor 具体实现机制。

本 Decision 不选择模型 Provider / Retrieval Backend / Schema Library / Prompt Registry / Evaluation Framework；RFC-001 保持 `DRAFTING`；Production Implementation 保持 `NOT AUTHORIZED`。

## 11. 已确认依赖注入、配置与应用装配（RFC-001-DQ-06）

> 来源：RFC-001-DQ-06（ACCEPTED）。

### 11.1 Dependency Injection Model

默认采用 **Constructor Injection + 显式 Factory Functions + 集中式 Composition Root（`bootstrap/`）**；MVP **不引入第三方 DI Framework**（无容器、无自动注入魔法）。**Global Service Locator = PROHIBITED。** 业务代码不做服务定位、不自行装配。

### 11.2 Composition Root

所有对象图构造与依赖装配只在 Composition Root 完成；它是唯一知道 Application Port 与 Infrastructure Implementation 绑定关系的代码。各 Entrypoint（API / Worker / CLI）不自行装配，统一由 Bootstrap 提供已装配对象图。

### 11.3 Configuration Loading and Layer Boundary

配置**仅由 Bootstrap 加载**，加载后立即**类型化 + 验证 + 不可变**，验证失败 **fail-fast**。业务代码不直接读取环境变量/配置文件。分层可见性：Domain 不接收任何配置；Application 只接收业务流程级配置（超时/重试/开关）；Infrastructure 只接收适配器级配置（连接串/Endpoint/凭证引用）；Bootstrap 加载、验证并分发全部配置。

### 11.4 Secret Boundary

**Secret 只注入需要它的 Infrastructure Adapter。** Secret 不得进入 Domain / Application Command / Application Result / Skill Input / Skill Result / Graph State / Checkpoint / Business Audit / Runtime Trace Payload / API Response / Git Repository / GitHub Issue or PR；不得打印或持久化完整 API Key / Database Password / Authorization Header / `.env` 内容 / Secret Manager 返回值。

### 11.5 Environment File Boundary

Repository **只提交 `.env.example`（占位值，无真实凭证）= REQUIRED**；`.env`（真实凭证）**提交 = PROHIBITED**，须被 `.gitignore` 排除。生产凭证来源（Secret Manager 等）留待后续 RFC。

### 11.6 Resource Lifetime Management

资源生命周期由 **Application Bootstrap 统一管理**，按 **Application / UseCase / WorkflowRun / SkillExecution** 四级作用域分级。**Global Mutable Runtime State = PROHIBITED；模块级可变单例持有连接/状态 = PROHIBITED。**

### 11.7 Test Replacement and Sync/Async Boundary

测试通过 Constructor / Factory 注入 **Fake / Stub** 替换真实 Adapter，无需修改业务代码或容器魔法。同步/异步执行策略与 API/Worker/CLI 进程边界**不在本 Decision 范围**，留待 **RFC-001-DQ-07**。

### 11.8 Decision Boundary

已确认：Constructor Injection + 显式 Factory + `bootstrap/` Composition Root；MVP 无第三方 DI Framework；无全局 Service Locator；配置仅 Bootstrap 加载、类型化/验证/不可变/fail-fast；Domain 无配置、Application 业务级、Infrastructure 适配器级；Secret 仅注入所需 Infrastructure Adapter 且不外泄；只提交 `.env.example`；资源生命周期 Bootstrap 统一分级管理；测试注入 Fake 替换。

尚未确认：第三方 DI Framework（后续是否引入）、Settings/Configuration Library、Secret Manager 与生产凭证来源、API Framework、Worker/Queue、同步/异步与进程边界（DQ-07）、Database 和 ORM、Architecture Test 工具、Deployment Platform、Production Skeleton。

本 Decision 不选择 DI Framework / Secret Manager / Settings Library / Deployment Platform；RFC-001 保持 `DRAFTING`；Production Implementation 保持 `NOT AUTHORIZED`。

## 12. 已确认分层职责、事务所有权与依赖规则（RFC-001-DQ-04）

> 来源：RFC-001-DQ-04（ACCEPTED）。

### 12.1 Core Architecture Model

正式调用方向：

```text
Entrypoint / Orchestration
        ↓
Application
        ↓
Domain
```

Infrastructure 实现 Application Port；Bootstrap 装配实现。

核心原则：业务规则向内保持纯净；框架、数据库、外部服务只能通过 Adapter 与 Port 接入。

### 12.2 Domain Layer

Domain 是纯业务核心，负责 Entity / Value Object / Aggregate / Domain Service / Business Rule / Domain Event / Version / Evidence / Review / Invalidation Rule。

Domain 仅可依赖 Python Standard Library、本模块 Domain 内部代码、严格受限的 `shared_kernel` 基础类型。不得依赖 Application / Infrastructure / Entrypoint / Orchestration / LangGraph / Web Framework / ORM / Database Driver / Repository Implementation / Model SDK / Vector DB SDK / Queue SDK / Checkpoint Backend / Observability Provider / Environment Variable。

Domain 必须可在无数据库、网络、LangGraph、真实模型条件下完成 Unit Test。

### 12.3 Application Layer

Application 负责 Command / Query / Application Service / Use Case Coordination / Repository / Provider / Unit of Work Port / Transaction Coordination / Idempotency / Current Truth / Evidence Link / Audit Coordination。

Application 不得依赖具体 Repository Implementation / ORM Model / Database Session / LangGraph State / Checkpoint Object / Web Request-Response / 具体 Model SDK / 具体 Retrieval SDK。

业务事务由 **Application Use Case** 拥有；Entrypoint 与 Graph Node 不开启/提交业务事务；Repository 不得自行 Commit；Unit of Work Implementation 仅提供技术能力，Commit/Rollback 由 Application Use Case 控制。

一次完整业务提交（Domain Version + Evidence Links + Current Truth Pointer + Stage State + Audit Record + Idempotency Record）必须在同一 Application Transaction 中 Commit Together 或 Rollback Together。

### 12.4 Port Ownership

Repository / Provider / Unit of Work / Clock / ID Generator / Event Publisher 等 Port 默认由 **Application Layer** 定义（推荐 `modules/<module>/application/ports.py`）。Application 声明能力，Infrastructure 实现，Bootstrap 注入。

仅真正属于纯业务抽象的 Policy 可定义在 Domain；数据库 Repository / LLM Provider / Retrieval Provider / Unit of Work / 外部 Event Publisher 不属于 Domain。

### 12.5 Infrastructure Layer

Infrastructure 负责 Repository Implementation / ORM Mapping / Database Integration / Unit of Work Implementation / Model / Retrieval / File Storage / Queue / Checkpoint / Observability Adapter / Third-party SDK。

Infrastructure 可依赖 Application Ports / Domain Types / Platform Infrastructure / 第三方 SDK；不得定义业务规则 / 改变 Domain Invariant / 在 Repository 中隐藏业务流程 / 自行更新 Current Truth / 自行决定 Review Approval / 自行执行 Downstream Invalidation / 在 ORM Hook 中执行业务逻辑 / 直接调用其他模块内部 Infrastructure / 绕过 Application Service 提交业务状态。

Repository Implementation 职责限于 Load / Persist / Query / Map，不得承担 Approve / Invalidate / Resume / Select Strategy / Generate Business Decision。

### 12.6 Orchestration Layer

LangGraph 位于独立 Orchestration / Workflow Adapter Layer，角色类似长运行 Application Client。Graph Node 通过 Module Public Application Contract 调用 Application Use Case，再使用 Domain + Ports。

Orchestration 可读取 Graph State、构造 Command、调用公开 Application Service、写回 Version ID / Stage Status、执行确定性路由、触发 `interrupt()`、协调 Retry/Resume/Cancellation、记录 Runtime Trace。

Orchestration 不得执行 Domain Rule / 拥有业务事务 / 直接调用业务 Repository / 直接使用 ORM Model / 直接更新 Current Truth / 直接写 Evidence Link / 直接执行 Review Approval / 直接执行 Idempotency Commit / 直接访问其他模块 Infrastructure / 在 Graph State 中长期保存完整业务对象。

**Graph Node Direct Business Repository Access = PROHIBITED。** 即使访问 Repository Interface 也会绕过 Application Validation、Transaction Boundary、Idempotency、Audit、Current Truth、Evidence Link、Application Error Mapping。Workflow Runtime 数据应通过 Workflow Runtime Service / Runtime Repository 读取。

### 12.7 Entrypoint Layer

Entrypoint 包括 API / Worker / CLI，仅负责将外部协议转换为 Application Command / Query。

Entrypoint 可解析输入、协议级 Schema Validation、Authentication / Authorization、构造 Command/Query、调用 Application Service、映射 Result / Error、添加 Correlation ID。

Entrypoint 不得直接调用 Domain Entity 完成业务流程 / 直接调用业务 Repository / 直接访问 ORM Model / 开启或提交业务事务 / 直接更新数据库 / 直接调用 LangGraph 内部 Node / 在 Route/Worker/CLI 中编写业务规则 / 绕过 Application Service 执行恢复。紧急恢复须通过明确的 Recovery Application Service 并产生 Audit Record。

### 12.8 Bootstrap and Composition Root

Bootstrap 是集中装配具体实现的 Composition Root，可了解 Application Port / Infrastructure Implementation / Orchestration Adapter / Entrypoint / Configuration / Application Lifecycle，负责加载 Settings、创建 Database Connection / Unit of Work / Repository / Provider Adapter / Application Service / Workflow / API / Worker / CLI Entrypoint、管理生命周期。

Bootstrap 不得执行业务 Use Case / 包含 Domain Rule / 成为全局 Service Locator / 允许模块任意读取全局 Container。

### 12.9 Dependency Injection and Cross-module Rules

默认采用 Constructor Injection + Explicit Factory Functions + Central Composition Root；不采用全局 Service Locator。

模块间同步调用必须通过目标模块公开 Application Contract（`public.py`），允许公开 Command / Query / Result / Public Error / Application Service Protocol / Published Application Event；禁止访问 infrastructure / ORM model / private repository / Direct SQL。当前不允许通过共享数据库任意 Join 其他模块内部表。

Domain Event 表示 Domain 已发生业务事实，Domain 可产生但不发布；Application Event 由 Application 在业务提交后发布，用于非关键副作用，当前不锁定 Message Broker，核心一致性流程优先同步调用。

错误转换方向：Infrastructure Error → Application Error → Protocol Error / Workflow Route；Graph Node 不得解析技术错误字符串决定业务路由。

### 12.10 Architecture Test Requirements

未来 Architecture Tests 至少验证：

- Domain 不 import application / infrastructure / orchestration / entrypoints / langgraph / web framework / orm；
- Application 不 import infrastructure implementations / entrypoints / langgraph / web framework / concrete database session；
- Infrastructure 可 import application ports / domain types / SDKs，不得定义业务规则 / use cases；
- Orchestration 不 import module infrastructure / ORM / database sessions / private implementation；
- Entrypoint 不 import repository implementations / ORM / private domain；
- Module A 不 import Module B infrastructure / private files；
- Production package 不 import spikes / prototypes。

具体 Architecture Test 工具尚未选择。

### 12.11 Responsibility Matrix

| Layer | Business Rules | Transaction Ownership | Defines Ports | Implements Ports | LangGraph | Protocol Handling |
|---|---|---|---|---|---|---|
| Domain | 是 | 否 | 仅纯业务 Policy | 否 | 否 | 否 |
| Application | 协调 | 是 | 是 | 否 | 否 | 否 |
| Infrastructure | 否 | 提供技术能力 | 否 | 是 | Adapter 可有 | 否 |
| Orchestration | 否 | 否 | 否 | Workflow Adapter | 是 | Workflow |
| Entrypoint | 否 | 否 | 否 | Protocol Adapter | 不直接 | 是 |
| Bootstrap | 否 | 否 | 知道接口 | 知道实现 | 装配 | 装配 |

### 12.12 Decision Boundary

已确认：

1. Domain 只负责纯业务模型、规则和不变量；
2. Domain 不依赖框架、数据库、LangGraph、ORM 或外部 SDK；
3. Application 负责 Use Case、Port 和业务流程协调；
4. Repository、Provider 与 Unit of Work Port 默认由 Application 定义；
5. Infrastructure 实现 Application Port，不得拥有业务规则；
6. 业务事务由 Application Use Case 拥有；
7. 长 Workflow 由多个短 Application Transaction 组成；
8. LangGraph Orchestration 是独立 Adapter Layer；
9. Graph Node 只能调用公开 Application Service，禁止直接访问业务 Repository；
10. Entrypoint 只负责协议转换，不直接调用 Domain / Repository；
11. Bootstrap 是 Composition Root，不执行业务 Use Case；
12. 跨模块调用必须经过公开 Application Contract；
13. Architecture Tests 必须强制依赖边界；
14. 本 Decision 不选择 ORM、Database、API Framework、DI Framework、Event Broker 或 Deployment。

尚未确认：Configuration Management、API Framework、Database 和 ORM、Worker 和 Queue、Architecture Test 工具、Production Skeleton。

RFC-001 保持 `DRAFTING`；Production Implementation 保持 `NOT AUTHORIZED`。

## 13. 已确认 Repository 与 Package 目录结构（RFC-001-DQ-03）

> 来源：RFC-001-DQ-03（ACCEPTED）。

### 13.1 Repository Model

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

### 13.2 Application Roots

| 应用 | 路径 | 说明 |
|---|---|---|
| Python Backend | `apps/backend/` | 生产源码根路径 `apps/backend/src/ai_ecommerce_agent/` |
| TypeScript Frontend | `apps/web/` | 本 Decision 不选择具体前端 Framework |
| Shared Contracts | `contracts/` | OpenAPI / JSON Schema / Error Codes 等正式契约 |

正式 Python Package 名：

```text
ai_ecommerce_agent
```

### 13.3 Backend Package Organization

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

### 13.4 Business Capability Modules

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

### 13.5 Platform Capabilities

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

### 13.6 Orchestration Boundary

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

### 13.7 Entrypoints

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

### 13.8 Bootstrap and Composition Root

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

### 13.9 Shared Kernel

允许保留严格受限的 `shared_kernel/`，只允许放置：

- 通用 Identifier 类型；
- Clock Protocol；
- 无业务语义的 Result；
- 通用 Error Base；
- 基础 Typing Utility。

不得放置具体业务规则、Repository Implementation、LangGraph State、ORM Base Model 或各业务模块为了方便而共享的任意代码。

### 13.10 Test Layout

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

### 13.11 Database Migrations

正式数据库 Migration 位于 `apps/backend/migrations/`，不放入可 Import 的生产 Python Package。具体 Migration Tool、Database 和 Schema Strategy 由 RFC-002 决定。

### 13.12 Configuration and Secret Boundary

目录层面允许未来使用：

```text
apps/backend/.env.example
apps/backend/src/ai_ecommerce_agent/bootstrap/settings.py
```

- `.env.example` 只能包含变量名称和非敏感示例；
- `.env`、Secret、Token 不得提交；
- Domain 和 Application 不直接读取环境变量；
- Configuration 由 Bootstrap 加载并注入。

### 13.13 Spike and Prototype Isolation

技术验证继续位于 Repository 根目录 `spikes/` 和 `prototypes/`。

生产 Package 禁止 `from spikes...` / `from prototypes...`。

允许关系：Spike Evidence → informs RFC and Production Tests → production implementation is rebuilt under accepted architecture。

禁止关系：Spike Source → rename or move → Production Source。

现有 Spike-001 继续作为 Architecture Evidence 保存。

### 13.14 Import Boundary

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

### 13.15 Cross-module Data Boundary

模块之间不得使用数据库表作为隐式 API。即使共享同一 Database Instance，也不得直接写入其他模块内部表、通过其他模块 ORM Model 修改数据、绕过 Application Contract、或直接调用其他模块 Repository Implementation。

跨模块读取和写入必须通过 Public Application Contract、Application Port、明确 Query Service 或用户后续确认的 Published Application Event。

### 13.16 Directory Creation Boundary

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

### 13.17 Decision Boundary

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

- Skill 的正式代码形态（RFC-001-DQ-05）；
- Configuration Management；
- API Framework；
- Database 和 ORM；
- Worker 和 Queue；
- Architecture Test 工具；
- Deployment Platform；
- Production Skeleton Authorization Gate。

## 14. 已确认生产技术语言边界（RFC-001-DQ-02）

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

### 14.1 Backend Language

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

### 14.2 Frontend Language

正式 Web Frontend 使用 TypeScript。前端不属于 Python 后端 Package。

前后端通过版本化契约协作：

```text
OpenAPI / JSON Schema / Generated Client Types / Error Code Registry
```

具体 API Framework、Schema Generator 和前端 Framework 尚未确认。

### 14.3 LangGraph Binding Boundary

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

### 14.4 Framework Replacement Boundary

系统须允许未来替换 Workflow Engine（LangGraph / Temporal / Custom State Machine / Queue Worker 等），替换范围应限于：

```text
Orchestration Layer
Runtime Adapter
Checkpoint Adapter
Worker Integration
```

不应要求重写 Domain、Application Services、Business Validators、Repository Interfaces、Skill Contracts、Evidence Rules 或 Human Review Business Rules。

### 14.5 Future Polyglot Boundary

未来允许特定独立能力采用其他语言，但必须满足至少一种可验证触发条件：

- Python 存在可测量性能瓶颈；
- 关键 SDK 只在其他语言中可靠；
- 模块已有稳定远程接口；
- 模块需要独立扩缩容；
- 独立团队负责该模块；
- 安全或部署要求物理隔离；
- 该能力需要服务多个产品。

不得仅因个人语言偏好引入第二种后端语言。

### 14.6 Decision Boundary

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

- Skill 的正式代码形态（RFC-001-DQ-05）；
- Configuration Management；
- API Framework；
- Schema Library；
- Type Checker / Linter；
- ORM；
- Database；
- Worker / Queue；
- Checkpointer；
- Deployment Platform；
- Frontend Framework。

## 15. 已确认应用架构（RFC-001-DQ-01）

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

### 15.1 Deployment Boundary

MVP 默认采用：

```text
One Primary Backend Application
```

初始不拆分为独立服务（Task / Workflow / Source / Retrieval / Human Review / Brief / Model Runtime Service）。

### 15.2 Repository Boundary

项目使用一个 Git Repository，但 Repository 内必须维持清晰的模块和依赖边界。

### 15.3 Module Boundary（概念划分）

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

### 15.4 Module Collaboration

模块之间必须通过明确边界协作：

- Application Service
- Domain Contract
- Repository Interface
- Provider Interface
- Command
- Query
- Published Application Event

不得任意访问其他模块内部类、绕过 Application Layer 修改数据、直接访问其他模块 Repository Implementation、以数据库表作为隐式 API、通过 LangGraph State 共享完整业务对象、或将 Prompt 作为唯一契约。

### 15.5 Dependency Direction

```text
Interface
↓
Application
↓
Domain

Infrastructure → implements → Repository and Provider Interfaces
```

Domain 不得依赖具体框架、数据库、ORM、LLM SDK、Vector DB、Message Queue、Observability Provider 或部署平台。

### 15.6 Data Ownership Boundary

允许 Modular Monolith 在 MVP 阶段共享一个数据库实例，但必须保持：

```text
Shared Database Instance ≠ Shared Data Ownership
```

必须区分 Business Domain / Workflow Runtime / Checkpoint / Source and Evidence / Retrieval Index / Audit / Observability Data。正式数据库、Schema、ORM 和事务方案由 RFC-002 决定。

### 15.7 Graph and Database Boundary

Graph Node 不得成为业务持久化规则的所有者。在 RFC-001 后续 DQ 接受前，Graph Node 不得临场定义 Domain Version 写入、Current Truth 更新、Evidence Link 事务、幂等、审计或失效逻辑。

### 15.8 Future Service Extraction

必须保留未来服务提取边界，但服务拆分只能由可验证的规模、组织、安全、性能或可靠性需求触发，不得仅因“微服务更先进”而拆分。

### 15.9 Decision Boundary

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

- Skill 的正式代码形态：PENDING RFC-001-DQ-05；
- Configuration Management：PENDING RFC；
- API Framework：PENDING RFC；
- Test Layering：PENDING RFC；
- Production Database / ORM：PENDING RFC-002；
- Web Framework：PENDING RFC；
- Deployment Platform：PENDING RFC。

## 16. 未决技术决策（PENDING RFC）

| 领域 | 状态 | RFC |
|---|---|---|
| Repository and Application Architecture | DRAFTING — DQ-01~06 ACCEPTED | RFC-001 |
| Persistence and Transaction Architecture（生产 DB / ORM） | PENDING RFC | RFC-002 |
| LangGraph Runtime and Checkpoint Architecture（生产 Checkpointer） | PENDING RFC | RFC-003 |
| API and Human Review Protocol | PENDING RFC | RFC-004 |
| Source Processing and Retrieval Architecture | PENDING RFC | RFC-005 |
| LLM Runtime and Structured Output | PENDING RFC | RFC-006 |
| Observability and Runtime Operations | PENDING RFC | RFC-007 |

> RFC-001 仍为 `DRAFTING`，API/Worker/CLI 进程边界与同步/异步执行策略（DQ-07）尚未确认。其余 RFC 仍为 `PROPOSED`。上述在生产实现前必须先经 RFC 提案 + 用户 Accepted Decision 收敛；**不得**临场选择。详见 [../decisions/dec-038-rfc-planning-and-dependency-order.md](../decisions/dec-038-rfc-planning-and-dependency-order.md) 与 [../specs/governance/rfc-planning-and-dependency-order.md](../specs/governance/rfc-planning-and-dependency-order.md)。

## 17. Final Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY

Next Topic: RFC-001-DQ-07 Process Boundaries and Sync/Async Execution Strategy
```
