# RFC Register（RFC 清单与优先级）

> **Status: ACTIVE — DEC-038 Accepted（RFC Planning Phase）**
> **治理来源：** DEC-034 · [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md)
> **关联：** [Architecture Readiness Review v1 Issue #3](https://github.com/JettxonHo/ai-ecommerce-agent/issues/3)
> **纪律：** 本文件**只**登记 Required RFC 的**清单与优先级**，**不替用户接受任何 RFC**。每个 RFC 的实际创建（`rfc-NNN-*.md`）、讨论、接受与否，均由用户在后续 Decision Gate 决定。RFC ≠ Accepted Decision。
> 
> **当前阶段：** DEC-038 已接受，进入依赖驱动的 RFC Planning 阶段。当前所有 RFC 初始状态均为 `PROPOSED`。下一议题：[RFC-001 Repository and Application Architecture](#required-rfc-清单)。

---

## 说明

- 优先级 `P0` = 阻塞对应生产模块开始（开始该模块生产实现**前**必须接受）。
- 优先级 `P1` = 建议在相关生产实现早期接受。
- 所有 RFC 当前状态均为 **`PROPOSED（未创建正文）`**；正文与接受与否待用户在后续 Decision Gate 决定。
- 在对应 RFC 被**接受**前，任何生产实现**不得**临场选择相关技术。

## Required RFC 清单

| # | RFC 主题 | Wave | 优先级 | 当前状态 | 阻塞的生产模块 | 关联 DEC / Spec | 关联 Spike 未验证项 |
|---|---|---|---|---|---|---|---|
| RFC-001 | **Repository and Application Architecture**（生产代码仓与应用结构、模块边界、部署单元） | Wave 1 | P0 | `PROPOSED` | 所有生产模块 | DEC-011/021/023 · architecture/system-architecture | R-1 |
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

## Final Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY

Next Topic: RFC-001 Repository and Application Architecture
```
