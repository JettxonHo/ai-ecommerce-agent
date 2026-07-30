# RFC Planning and Dependency Order Specification

> **Type:** Governance Specification  
> **Status:** Accepted  
> **Governance Source:** [DEC-038 — RFC Planning and Dependency Order](../decisions/dec-038-rfc-planning-and-dependency-order.md)  
> **Related DEC:** DEC-034 through DEC-037  

---

## 1. Purpose

本文档定义 Architecture Readiness 进入 `CONDITIONALLY READY` 后，项目如何通过依赖驱动的 RFC 波次、单 RFC Issue/Branch/PR 工作流、用户 Acceptance Gate 与分阶段 Roadmap 生成流程，逐步收敛生产技术决策。

RFC 用于决定：已经由 DEC 和 Specs 定义、并由 Technical Spike 证明具备可行实现方式的需求，在生产环境中具体采用什么技术方案实现。

## 2. RFC Scope Boundary

RFC 必须回答技术实现方案，不得改变 Accepted Business Requirement、不得静默修改 DEC、不得静默修改 Current Specs、不得用技术限制取消业务规则。

## 3. RFC Status Model

```text
PROPOSED
↓
DRAFTING
↓
IN REVIEW
↓
ACCEPTED
```

其他允许状态：

```text
BLOCKED
REJECTED
WITHDRAWN
SUPERSEDED
```

含义：

- **PROPOSED** — 已登记，尚未开始完整讨论。
- **DRAFTING** — 正在调研与编写草案。
- **IN REVIEW** — 主要 Decision Questions 已形成推荐结论，进入用户与架构审查。
- **ACCEPTED** — 用户明确接受。
- **BLOCKED** — 被依赖、冲突、缺少证据或待补充 Spike 阻塞。
- **REJECTED** — 用户明确拒绝。
- **WITHDRAWN** — 不再需要或已撤回。
- **SUPERSEDED** — 已被后续 Accepted RFC 替代。

## 4. Acceptance Authority

- Agent 可以调研、起草、比较、推荐、创建 Issue/Branch/PR、根据 Review 修改。
- **只有用户明确确认后，RFC 才能标记为 ACCEPTED。**
- PR Merge 不自动等于 RFC Accepted。

## 5. Issue / Branch / PR Workflow

每个 RFC：

```text
1 GitHub Issue
+
1 Dedicated Branch（如 rfc/001-repository-application-architecture）
+
1 Pull Request
```

RFC Branch 主要允许修改：

```text
docs/rfcs/**
docs/architecture/**
docs/traceability/**
docs/readiness/**
```

必要时可增加最小技术验证，但只能位于：

```text
spikes/**
prototypes/**
```

RFC Branch 不得：

- 开始正式业务功能实现
- 创建正式生产模块
- 将 Prototype 直接写入生产目录
- 修改 Accepted DEC 的含义
- 静默修改 Current Specs
- 创建完整 MVP Backlog

## 6. Decision Questions

每个 RFC 必须先拆成有限的 Decision Questions。每个问题至少包含：

```text
Question
Context
Constraints
Candidate Options
Advantages
Disadvantages
Risks
Compatibility with DEC and Specs
Recommended Option
User Decision
```

关键 Decision Question 必须由用户逐项或成组明确确认。

## 7. Dependency Rules

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
- RFC-004 可提前整理 API Questions，但接受前须 RFC-002 与 RFC-003 已 ACCEPTED。
- RFC-005 可提前比较 Retrieval 方案，但接受前须 RFC-002 已 ACCEPTED 且 RFC-006 模型接口边界已明确。
- RFC-007 可提前调研，但最终接受应在 RFC-002 至 RFC-006 主要运行结构明确后。

不允许：

- 在依赖 RFC 未接受时锁定依赖接口。
- 将 Draft RFC 作为生产编码依据。
- 同时接受相互依赖但尚未对齐的 RFC。

## 8. Merge Boundary

RFC PR Merge 不等于 RFC Accepted。

正式顺序：

```text
RFC Draft
↓
PR Review
↓
User explicitly accepts RFC
↓
RFC Status updated to ACCEPTED
↓
Merge RFC PR
```

若先 Merge Draft 文档以保留 Review 记录，文档状态必须保持 `IN REVIEW`，不得因 Merge 自动变为 `ACCEPTED`。

## 9. Roadmap Gates

### Roadmap Draft v0 Gate

条件：

```text
RFC-001 = ACCEPTED
RFC-002 = ACCEPTED
RFC-003 = ACCEPTED
```

允许生成：

```text
MVP Roadmap Draft v0
Epic Skeleton
Dependency Graph
Foundation Issue Candidates
```

不得生成完整业务功能 Backlog。

### Roadmap v1 Gate

条件：

```text
RFC-001 through RFC-007 = ACCEPTED
```

允许生成：

```text
MVP Development Roadmap v1
Final Epic Map
Implementation Backlog
Acceptance Criteria
Traceability Matrix v1
```

## 10. Implementation Issue Gate

正式 Production Implementation Issue 必须至少关联：

```text
Relevant DEC
+
Relevant Spec
+
Accepted RFC
+
Acceptance Criteria
+
Required Tests
+
Dependency Status
```

缺少 Accepted RFC 的工作只能标记为 `type: research`、`type: spike` 或 `type: planning`，不得标记为 `type: implementation`。

## 11. Conflict Handling

RFC 起草期间若发现 Accepted DEC 无法实现、Specs 冲突、Spike 结论不能推广到生产、生产方案要求改变业务边界、RFC 之间接口冲突，必须创建 **Decision Conflict Report**，不得直接在 RFC 中改写上游 Decision 或 Spec。

## 12. Acceptance Criteria

提交用户接受的 RFC 必须满足：

- **Decision Completeness** — 核心技术问题有结论、候选方案完整、拒绝原因完整、Trade-off 清晰、无隐藏核心选择、Open Questions 不阻塞实现。
- **Architecture Compatibility** — 不违反 Accepted DEC 与 Current Specs，符合 Architecture Baseline，与其他 Accepted RFC 一致，不错误推广 Spike 临时方案。
- **Implementation Readiness** — 模块边界、接口、数据责任、事务边界、错误边界、测试策略、Migration、Rollback、Security Boundary 明确。
- **Traceability** — 关联 Requirement、DEC、Spec、Architecture、RFC、Future Epic、Future Test。

## 13. Agent Authority

RFC Agent 可以：

- 创建 RFC Issue/Branch/Draft/PR
- 搜索文档、比较方案、创建最小 Prototype、运行技术验证
- 更新 Traceability、提交 Recommendation、根据 Review 修改 RFC

RFC Agent 不得：

- 自行接受 RFC
- Merge 未经用户接受的 RFC PR
- 创建正式业务实现或完整生产 Backlog
- 修改 Accepted DEC 或 Current Specs 业务含义
- 将 Prototype 直接转成生产代码
- 将 Architecture Readiness / Development Status 更新为完全 READY

## 14. Current Status

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
```

下一议题：**RFC-001 Repository and Application Architecture**。
