# RFC Register（RFC 清单与优先级）

> **Status: ACTIVE — DEC-038 Accepted（RFC Planning Phase）**
> **治理来源：** DEC-034 · [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md)
> **关联：** [Architecture Readiness Review v1 Issue #3](https://github.com/JettxonHo/ai-ecommerce-agent/issues/3)
> **纪律：** 本文件**只**登记 Required RFC 的**清单与优先级**，**不替用户接受任何 RFC**。每个 RFC 的实际创建（`rfc-NNN-*.md`）、讨论、接受与否，均由用户在后续 Decision Gate 决定。RFC ≠ Accepted Decision。
> 
> **当前阶段：** DEC-038 已接受，RFC-001 进入 `DRAFTING`，DQ-01~DQ-06 已接受。下一议题：[RFC-001-DQ-07：Process Boundaries and Sync/Async Execution Strategy](#dq-07-process-boundaries-and-syncasync-execution-strategy)。

---

## 说明

- 优先级 `P0` = 阻塞对应生产模块开始（开始该模块生产实现**前**必须接受）。
- 优先级 `P1` = 建议在相关生产实现早期接受。
- 所有 RFC 当前状态均为 **`PROPOSED（未创建正文）`**；正文与接受与否待用户在后续 Decision Gate 决定。
- 在对应 RFC 被**接受**前，任何生产实现**不得**临场选择相关技术。

## Required RFC 清单

| # | RFC 主题 | Wave | 优先级 | 当前状态 | 阻塞的生产模块 | 关联 DEC / Spec | 关联 Spike 未验证项 |
|---|---|---|---|---|---|---|---|
| RFC-001 | **Repository and Application Architecture**（生产代码仓与应用结构、模块边界、部署单元） | Wave 1 | P0 | `DRAFTING` | 所有生产模块 | DEC-011/021/023 · architecture/system-architecture | R-1 |
| RFC-002 | **Persistence and Transaction Architecture**（生产数据库、ORM、原子提交与幂等的生产实现） | Wave 1 | P0 | `PROPOSED` | Business Repository / Current Truth | DEC-024/029/033 · architecture/data-architecture | R-1, R-4 |
| RFC-003 | **LangGraph Runtime and Checkpoint Architecture**（生产 Checkpointer 选型、Safe Resume、序列化兼容） | Wave 2 | P0 | `PROPOSED` | Workflow Runtime / Resume | DEC-013/023/024/033 · runtime/failure-recovery spec | R-3 |
| RFC-004 | **API and Human Review Protocol**（生产 API 边界、Human Review 提交/暂停协议、权限） | Wave 3 | P0 | `PROPOSED` | Review / Orchestration 接口层 | DEC-007/029 · workflow/human-review spec | R-1 |
| RFC-005 | **Source Processing and Retrieval Architecture**（生产检索：词法/向量/融合、权限与版本过滤、证据装配） | Wave 3 | P0 | `PROPOSED` | Retrieval & Evidence Runtime | DEC-014/025/032 · runtime/hybrid-retrieval spec | R-2 |
| RFC-006 | **LLM Runtime and Structured Output**（生产 LLM Provider、结构化输出、真实模型 Smoke 策略、Secret 注入边界） | Wave 2 | P0 | `PROPOSED` | 所有 LLM 驱动 Skill | DEC-011/026/027/028/030 · skills specs | R-2 |
| RFC-007 | **Observability and Runtime Operations**（结构化日志 / Tracing / Metrics、是否 OpenTelemetry、Retry/Timeout/Backoff/Circuit Breaker 生产参数） | Wave 4 | P1 | `PROPOSED` | Runtime Operations | DEC-033 · runtime/failure-recovery spec | R-1, R-4 |

## 与 Spike-001 Required RFC List 的映射

Spike Report 第 7 节的 7 项与本表对应：1→RFC-003（Checkpointer）、2→RFC-001/002（并发与锁/持久化）、3→RFC-006（LLM Provider 与 Smoke）、4→RFC-005（Retrieval）、5→RFC-002（DB 与 ORM）、6→RFC-007（Observability Provider）、7→RFC-007（Retry/Timeout/Backoff/Circuit Breaker 参数）。

## 接受流程（提醒）

```text
RFC Draft
  -> IN REVIEW（用户与架构审查）
  -> ACCEPTED（用户明确确认）
  -> 对应生产模块方可开始实现
```

> 在 RFC-001—RFC-007 被接受前：**不允许**开始未经 RFC 支持的生产实现；**不允许** Coding Agent 临场选择生产数据库 / Checkpointer / API / ORM / Retrieval / Observability。

## 依赖顺序

```text
RFC-001 Repository and Application Architecture
│
├── RFC-002 Persistence and Transaction Architecture
│   ├── RFC-003 LangGraph Runtime and Checkpoint Architecture
│   │   └── RFC-004 API and Human Review Protocol
│   └── RFC-005 Source Processing and Retrieval Architecture
├── RFC-006 LLM Runtime and Structured Output
└── RFC-007 Observability and Runtime Operations
```

- RFC-003 与 RFC-006 可并行调研和起草。
- RFC-004 可提前整理 API Questions，但接受前须 RFC-002 与 RFC-003 已 `ACCEPTED`。
- RFC-005 可提前比较 Retrieval 方案，但接受前须 RFC-002 已 `ACCEPTED` 且 RFC-006 模型接口边界已明确。
- RFC-007 可提前调研，但最终接受应在 RFC-002 至 RFC-006 主要运行结构明确后。

## Roadmap Gates

### Roadmap Draft v0 Gate

当以下 RFC 被接受：

```text
RFC-001 = ACCEPTED
RFC-002 = ACCEPTED
RFC-003 = ACCEPTED
```

允许生成 MVP Roadmap Draft v0、Epic Skeleton、Dependency Graph、Foundation Issue Candidates。不得生成完整业务功能 Backlog。

### Roadmap v1 Gate

当 RFC-001 至 RFC-007 全部被接受，允许生成 MVP Development Roadmap v1、Final Epic Map、Implementation Backlog、Acceptance Criteria、Traceability Matrix v1。

## RFC-001 Current Status

```text
RFC-001 Status = DRAFTING
RFC-001-DQ-01 Modular Monolith First = ACCEPTED
RFC-001-DQ-02 Backend Language and LangGraph Binding = ACCEPTED
RFC-001-DQ-03 Repository and Package Directory Structure = ACCEPTED
RFC-001-DQ-04 Layer Responsibilities and Dependency Rules = ACCEPTED
RFC-001-DQ-05 Skill Code Shape and Architectural Relationships = ACCEPTED
RFC-001-DQ-06 Dependency Injection, Configuration and Application Bootstrap = ACCEPTED
RFC-001-DQ-07 Process Boundaries and Sync/Async Execution Strategy = PROPOSED
```

## DQ-07: Process Boundaries and Sync/Async Execution Strategy

RFC-001-DQ-07 下一轮优先讨论：

1. API、Worker、CLI 与 Workflow Runtime 的进程边界；
2. 各 Entrypoint 是单进程还是多进程；
3. Workflow Runtime 与 API 是否同进程；
4. 同步 / 异步执行策略；
5. 长运行 Workflow 的执行与调度模型；
6. 是否需要独立 Worker 进程；
7. 是否引入 Queue / Message Broker；
8. Human Review 暂停与 Resume 的进程语义；
9. 并发与资源隔离边界；
10. 进程间通信与状态共享边界；
11. 各进程的配置与生命周期归属（承接 DQ-06 Bootstrap）；
12. 本议题不锁定具体 API Framework、Queue、Deployment Platform。

在 RFC-001-DQ-07 被用户明确接受前：

- 不创建 API；
- 不创建 Worker；
- 不引入 Queue；
- 不决定生产运行模型；
- RFC-001 保持 `DRAFTING`。

## DQ-06: Dependency Injection, Configuration and Application Bootstrap

RFC-001-DQ-06 已接受：

1. 默认采用 Constructor Injection + 显式 Factory Functions + 集中式 Composition Root（`bootstrap/`）；
2. MVP 不引入第三方 DI Framework；
3. 禁止全局 Service Locator 与可变运行状态；
4. 配置仅由 Bootstrap 加载，类型化、验证、不可变，验证失败 fail-fast；
5. Domain 不接收配置；Application 只接收业务流程级配置；Infrastructure 只接收适配器级配置；
6. Secret 只注入需要它的 Infrastructure Adapter，不进入 Domain / Application / Skill / Graph State / Checkpoint / Audit / Trace / API Response / Git / Issue / PR；
7. Repository 只提交 `.env.example`（占位值），`.env` 不得提交；
8. 资源生命周期由 Application Bootstrap 统一管理，按 Application / UseCase / WorkflowRun / SkillExecution 作用域分级；
9. 测试通过注入 Fake / Stub 替换真实 Adapter，无需修改业务代码；
10. 同步/异步与 API / Worker / CLI 进程边界留待 RFC-001-DQ-07；
11. 本 Decision 不选择 DI Framework、Secret Manager、Settings Library 或 Deployment Platform。

## DQ-05: Skill Code Shape and Architectural Relationships

RFC-001-DQ-05 已接受：

1. Skill 是业务模块 Application Layer 内具有明确执行契约、可独立运行和独立评估的无状态业务能力组件；
2. Skill 落位 `modules/<module>/application/skills/<skill_slug>/`；
3. Application Use Case 以 Prepare–Execute–Commit 协调 Skill 与业务事务；
4. Skill 只参与 Execute 阶段，产出 Candidate Result（业务候选，未落库）；
5. Skill 直接访问业务 Repository = PROHIBITED；Skill 业务事务所有权 = NO；
6. Skill 不读/写 Current Truth、不更新 Evidence / Audit / Idempotency；
7. Skill 只能通过 Application 定义的 ModelRuntimePort / RetrievalPort 调用 Provider 能力；
8. Skill 直接 import 具体 Provider SDK = PROHIBITED；
9. LangGraph Node 经 Stage Application Service + Skill Executor 间接调用 Skill，不直接调用；
10. Skill 与 LangGraph Node 不是同一概念；Skill 不感知 LangGraph；
11. Skill 必须能脱离 LangGraph 独立运行与独立评估 = REQUIRED；
12. Skill 版本分 Contract / Implementation / Prompt / Output Schema 四维度分管；
13. Skill 须支持 Contract / Unit / Integration / Evaluation / Architecture 五类测试；
14. 本 Decision 不选择模型 Provider、Retrieval Backend、Schema Library、Prompt Registry 或 Evaluation Framework。

## DQ-04: Layer Responsibilities and Dependency Rules

RFC-001-DQ-04 已接受：

1. Domain 是纯业务核心，不依赖框架、数据库、LangGraph、ORM 或外部 SDK；
2. Application 负责 Use Case、Port 和业务流程协调；
3. Repository、Provider 与 Unit of Work Port 默认由 Application 定义；
4. Infrastructure 实现 Application Port，不得拥有业务规则；
5. 业务事务由 Application Use Case 拥有；
6. 长 Workflow 由多个短 Application Transaction 组成；
7. LangGraph Orchestration 是独立 Adapter Layer；
8. Graph Node 只能调用公开 Application Service，禁止直接访问业务 Repository；
9. Entrypoint 只负责协议转换，不直接调用 Domain 或 Repository；
10. Bootstrap 是 Composition Root；
11. 默认采用 Constructor Injection 和显式 Factory；
12. 跨模块调用必须经过公开 Application Contract；
13. Architecture Tests 必须强制依赖边界；
14. 本 Decision 不选择 ORM、Database、API Framework、DI Framework、Event Broker 或 Deployment。

## Final Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY

Next Topic: RFC-001-DQ-07 Process Boundaries and Sync/Async Execution Strategy
```
