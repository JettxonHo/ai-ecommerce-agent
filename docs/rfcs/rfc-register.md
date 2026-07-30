# RFC Register（RFC 清单与优先级）

> **Status: DRAFT — PENDING USER REVIEW**
> **治理来源：** DEC-034 · [../readiness/architecture-readiness-report-v1.md](../readiness/architecture-readiness-report-v1.md)
> **关联：** [Architecture Readiness Review v1 Issue #3](https://github.com/JettxonHo/ai-ecommerce-agent/issues/3)
> **纪律：** 本文件**只**登记 Required RFC 的**清单与优先级**，**不替用户接受任何 RFC**。每个 RFC 的实际创建（`rfc-NNN-*.md`）、讨论、接受与否，均由用户在后续 Decision Gate 决定。RFC ≠ Accepted Decision。

---

## 说明

- 优先级 `P0` = 阻塞对应生产模块开始（开始该模块生产实现**前**必须接受）。
- 优先级 `P1` = 建议在相关生产实现早期接受。
- 所有 RFC 当前状态均为 **`Proposed（未创建正文）`**；正式编号与正文待用户确认后创建。
- 在对应 RFC 被**接受**前，任何生产实现**不得**临场选择相关技术。

## Required RFC 清单

| # | RFC 主题 | 优先级 | 阻塞的生产模块 | 关联 DEC / Spec | 关联 Spike 未验证项 |
|---|---|---|---|---|---|
| RFC-A | **Repository and Application Architecture**（生产代码仓与应用结构、模块边界、部署单元） | P0 | 所有生产模块 | DEC-011/021/023 · architecture/system-architecture | R-1 |
| RFC-B | **Persistence and Transaction Architecture**（生产数据库、ORM、原子提交与幂等的生产实现） | P0 | Business Repository / Current Truth | DEC-024/029/033 · architecture/data-architecture | R-1, R-4 |
| RFC-C | **LangGraph Runtime and Checkpoint Architecture**（生产 Checkpointer 选型、Safe Resume、序列化兼容） | P0 | Workflow Runtime / Resume | DEC-013/023/024/033 · runtime/failure-recovery spec | R-3 |
| RFC-D | **API and Human Review Protocol**（生产 API 边界、Human Review 提交/暂停协议、权限） | P0 | Review / Orchestration 接口层 | DEC-007/029 · workflow/human-review spec | R-1 |
| RFC-E | **Source Processing and Retrieval Architecture**（生产检索：词法/向量/融合、权限与版本过滤、证据装配） | P0 | Retrieval & Evidence Runtime | DEC-014/025/032 · runtime/hybrid-retrieval spec | R-2 |
| RFC-F | **LLM Runtime and Structured Output**（生产 LLM Provider、结构化输出、真实模型 Smoke 策略、Secret 注入边界） | P0 | 所有 LLM 驱动 Skill | DEC-011/026/027/028/030 · skills specs | R-2 |
| RFC-G | **Observability and Runtime Operations**（结构化日志 / Tracing / Metrics、是否 OpenTelemetry、Retry/Timeout/Backoff/Circuit Breaker 生产参数） | P1 | Runtime Operations | DEC-033 · runtime/failure-recovery spec | R-1, R-4 |

## 与 Spike-001 Required RFC List 的映射

Spike Report 第 7 节的 7 项与本表对应：1→RFC-C（Checkpointer）、2→RFC-A/B（并发与锁/持久化）、3→RFC-F（LLM Provider 与 Smoke）、4→RFC-E（Retrieval）、5→RFC-B（DB 与 ORM）、6→RFC-G（Observability Provider）、7→RFC-G（Retry/Timeout/Backoff/Circuit Breaker 参数）。

## 接受流程（提醒）

```text
RFC Draft（本任务不创建正文）
  -> In Discussion（用户评审）
  -> Accepted（仍需 Decision Gate 产出 DEC 并同步 Current Truth）
  -> 对应生产模块方可开始实现
```

> 在 RFC-A—RFC-G 被接受前：**不允许**开始未经 RFC 支持的生产实现；**不允许** Coding Agent 临场选择生产数据库 / Checkpointer / API / ORM / Retrieval / Observability。

## Final Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = PENDING USER REVIEW
Development Status = NOT READY
```
