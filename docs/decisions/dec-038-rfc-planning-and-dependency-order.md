# DEC-038：RFC Planning and Dependency Order

> **Type:** Architecture Governance / RFC Governance / Implementation Planning  
> **Status:** Accepted  
> **Date:** 2026-07-30  
> **Governance Source:** DEC-034（Technical Spike Plan and Architecture Readiness Gate）  
> **Related Decisions:** DEC-001 through DEC-037  
> **Related RFCs:** None  
> **Amends:** Architecture Readiness Governance — defines the RFC and Roadmap process allowed under `CONDITIONALLY READY`  

---

## Core Decision

AI Ecommerce Agent 在 Architecture Readiness 被确认为 `CONDITIONALLY READY` 后，进入**依赖驱动的 RFC 与实施规划阶段**。

正式流程为：

```text
Accepted DEC and Current Specs
↓
Architecture Baseline
↓
Dependency-driven RFC Planning
↓
RFC Decision Questions
↓
RFC Draft and Review
↓
Explicit User Acceptance
↓
Accepted RFC
↓
Roadmap and Epic Planning
↓
Implementation Issues
↓
Production Implementation
```

没有 Accepted RFC 支持的生产模块，不得进入正式实现。

Coding Agent 不得在单个 Issue、Commit 或 PR 中临时选择生产数据库、ORM、Checkpointer、API、Retrieval、LLM Runtime、Observability 或其他核心基础设施。

## Current Project Status

归档后保持：

```text
Spike Execution Status = COMPLETED
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
```

`Development Status = CONDITIONALLY READY` 仅允许：

- Architecture RFC
- Technical Research
- Additional Technical Spike
- Implementation Planning
- MVP Roadmap Draft
- Epic and Dependency Planning
- Acceptance Criteria Planning
- Technical Risk Resolution

暂不允许：

- Production Business Implementation
- Production Database Implementation
- Production API Implementation
- Production Retrieval Implementation
- Production LLM Runtime Implementation
- Production Observability Implementation
- 正式业务 Coding Issues 的创建与执行
- 将 Spike 代码直接迁移为生产模块
- Coding Agent 临场确定生产技术

## RFC Purpose

RFC 用于决定：已经由 DEC 和 Specs 定义、并由 Technical Spike 证明具备可行实现方式的需求，在生产环境中具体采用什么技术方案实现。

RFC 必须回答：

- Problem
- Context
- Related Decisions
- Related Specifications
- Decision Questions
- Candidate Options
- Chosen Option
- Rejected Alternatives
- Trade-offs
- Architecture Boundaries
- Data and Transaction Boundaries
- Error and Recovery Boundaries
- Security Considerations
- Testing Strategy
- Migration Strategy
- Rollback Strategy
- Operational Impact
- Affected Modules
- Blocking Dependencies
- Open Questions
- User Acceptance Gate

RFC 不得：

- 改变 Accepted Business Requirement
- 静默修改 DEC
- 静默修改 Current Specs
- 用技术限制取消业务规则
- 将 Spike 临时技术自动升级为生产方案
- 隐藏核心生产技术选择
- 由 Coding Agent 在实现过程中临时决定

## RFC Status Model

所有 RFC 采用统一状态：

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

状态含义：

- **PROPOSED** — RFC 已登记，但尚未开始完整讨论。
- **DRAFTING** — 正在调研、讨论 Decision Questions 和编写草案。
- **IN REVIEW** — 主要 Decision Questions 已形成推荐结论，RFC 已进入用户与架构审查。
- **ACCEPTED** — 用户明确接受该 RFC。
- **BLOCKED** — RFC 被依赖问题、Decision Conflict、缺少证据或待补充 Spike 阻塞。
- **REJECTED** — 用户明确拒绝当前方案。
- **WITHDRAWN** — RFC 已不再需要或由提出者撤回。
- **SUPERSEDED** — RFC 已被后续 Accepted RFC 替代。

## RFC Acceptance Authority

Agent 可以：

- 调研
- 收集候选方案
- 起草 RFC
- 比较 Trade-off
- 提交推荐方案
- 创建 RFC Issue
- 创建 RFC Branch
- 创建 RFC Pull Request
- 根据 Review 修改草案
- 提交 Acceptance Recommendation

Agent 不可以：

- 自行将 RFC 标记为 `ACCEPTED`
- 因为测试通过就宣布 RFC 已接受
- 因为 PR 已 Merge 就宣布 RFC 已接受
- 修改 Accepted DEC 以适配推荐方案
- 绕过用户 Decision Gate
- 将未接受的 RFC 作为生产实现依据

只有用户明确确认后，RFC 才能进入：

```text
Status = ACCEPTED
```

## Dependency-driven RFC Order

项目采用以下 RFC 依赖结构：

```text
RFC-001 Repository and Application Architecture
│
├── RFC-002 Persistence and Transaction Architecture
│   │
│   ├── RFC-003 LangGraph Runtime and Checkpoint Architecture
│   │   └── RFC-004 API and Human Review Protocol
│   │
│   └── RFC-005 Source Processing and Retrieval Architecture
│
├── RFC-006 LLM Runtime and Structured Output
│   └── 与 RFC-003 和 RFC-005 建立正式集成边界
│
└── RFC-007 Observability and Runtime Operations
    └── 在 RFC-002 至 RFC-006 的运行结构基本稳定后最终确认
```

## RFC Waves

### Wave 1：Application and Persistence Foundation

#### RFC-001：Repository and Application Architecture

RFC-001 是所有正式生产代码的根依赖。至少决定：

- Modular Monolith 或 Multi-service
- 正式 Repository Layout
- Domain Layer
- Application Layer
- Infrastructure Layer
- Interface Layer
- Dependency Direction
- LangGraph 所属层级
- Skill 的生产代码形态
- Graph Node 的职责
- Repository Interface
- Dependency Injection
- Configuration Management
- Environment Boundary
- Test Layout
- Spike 与 Production 隔离
- Package Boundary
- Import Boundary

RFC-001 接受前：

- 不创建正式产品代码目录
- 不建立生产 Package Structure
- 不创建正式业务模块
- 不让 Coding Agent 决定分层

#### RFC-002：Persistence and Transaction Architecture

依赖：

```text
RFC-001 = ACCEPTED
```

至少决定：

- Production Database
- ORM 或 Data Access Strategy
- Domain Version Persistence
- Current Truth Pointer
- Evidence Link
- Source Version
- Review Package
- Approved Strategy
- Idempotency Record
- Audit Record
- Runtime Repository
- Transaction Boundary
- Migration Tool
- Concurrency Control
- Locking
- Isolation
- Backup and Recovery
- Data Retention
- Workspace Isolation

RFC-002 接受前：

- 不创建正式数据库 Schema
- 不创建正式 Migration
- 不实现生产 Repository
- 不选择生产 ORM

### Wave 2：Workflow Runtime and LLM Runtime

#### RFC-003：LangGraph Runtime and Checkpoint Architecture

依赖：

```text
RFC-001 = ACCEPTED
RFC-002 = ACCEPTED
```

至少决定：

- Production Graph Module
- Graph State
- Checkpointer Backend
- `task_id`、`thread_id`、`run_id` 映射
- Interrupt
- Resume
- Retry
- Rerun
- Stale Checkpoint Reconciliation
- Cancellation
- Runtime Record
- Worker Model
- Sync or Async
- Queue Boundary
- Graph Versioning
- Deployment Runtime
- Checkpoint Security
- Recovery Protocol

RFC-003 接受前：

- 不实现正式业务 StateGraph
- 不创建生产 Checkpointer
- 不实现正式 Resume Runtime

#### RFC-006：LLM Runtime and Structured Output

RFC-006 可以与 RFC-003 并行调研和起草。在正式接受前，必须至少明确 RFC-001 和 RFC-002 提供的接口与持久化边界。至少决定：

- Model Provider Interface
- Default Provider
- Model-neutral Boundary
- Structured Output Schema
- Parse
- Normalize
- Repair
- Regeneration
- Prompt Versioning
- Model Configuration
- Token Metadata
- Cost Metadata
- Latency Metadata
- Retry Boundary
- Provider Error Mapping
- Evaluation Hook
- Secret Management
- Fallback Boundary
- Model Safety Boundary

RFC-006 接受前：

- 不编写正式 Skill Prompt Runtime
- 不锁定生产模型供应商
- 不建立正式 Prompt Registry

### Wave 3：API, Human Review and Retrieval

#### RFC-004：API and Human Review Protocol

依赖：

```text
RFC-002 = ACCEPTED
RFC-003 = ACCEPTED
DEC-029 = ACCEPTED
```

至少决定：

- Task API
- Run API
- Review Package API
- Save Draft
- Submit
- Withdraw
- Resume
- Idempotency Key
- Optimistic Concurrency
- Stale Review Error
- API Error Contract
- Polling or Event Notification
- Review Package Version
- Authentication Boundary
- Authorization Boundary
- Request and Response Schema
- Human Review State Machine

RFC-004 接受前：

- 不实现正式 Human Review API
- 不实现正式 Resume Endpoint
- 不建立前端与 Workflow Runtime 的生产协议

#### RFC-005：Source Processing and Retrieval Architecture

依赖：

```text
RFC-001 = ACCEPTED
RFC-002 = ACCEPTED
RFC-006 的模型接口边界已明确
```

至少决定：

- Source Upload
- Source Version
- Parser
- Document
- Record
- Fragment
- Indexing
- Lexical Retrieval
- Semantic Retrieval
- Embedding
- Vector Store
- Metadata Filter
- Source Scope Isolation
- Product Identity Isolation
- EvidencePackage
- Dataset Statistics
- Retrieval Evaluation
- Index Rebuild
- Deletion
- Source Invalidation
- Retention
- Permission Filtering

RFC-005 接受前：

- 不创建正式 Vector Database
- 不实现生产 Retrieval Pipeline
- 不锁定 Embedding Model
- 不建立生产 Index

### Wave 4：Observability and Runtime Operations

#### RFC-007：Observability and Runtime Operations

RFC-007 可以提前调研和起草，但应在 RFC-002 至 RFC-006 的主要运行结构明确后最终接受。至少决定：

- Structured Logging
- Trace
- Metrics
- Alerting
- Runtime Error
- Recovery Case
- Manual Recovery Queue
- Sensitive Data Redaction
- Token and Cost Tracking
- Business Audit 与 Runtime Log 边界
- Retention
- Dashboard
- Circuit Breaker
- Operational Runbook
- Incident Handling
- Correlation IDs
- Production Fault Handling

RFC-007 接受前：

- 可以使用最低限度开发日志
- 不锁定生产 Observability Provider
- 不建立生产告警体系
- 不建立生产 Recovery Operations

## Parallel Drafting Boundary

RFC 可以并行调研和起草，但必须按依赖 Gate 接受。

允许：

- RFC-003 与 RFC-006 并行调研
- RFC-004 提前整理 API Questions
- RFC-005 提前比较 Retrieval 方案
- RFC-007 提前整理 Observability Requirements

不允许：

- 在依赖 RFC 未接受时锁定依赖接口
- 将 Draft RFC 作为生产编码依据
- 因为并行起草而忽略依赖变化
- 同时接受相互依赖但尚未对齐的 RFC

推荐接受顺序：

```text
RFC-001
↓
RFC-002
↓
RFC-003
↓
RFC-004
↓
RFC-005
↓
RFC-006
↓
RFC-007
```

RFC-006 可以根据实际依赖对齐情况，在 RFC-004 或 RFC-005 前接受，但必须确保其接口不与 RFC-003、RFC-005 冲突。

## Single RFC GitHub Workflow

每个 RFC 使用：

```text
1 RFC
=
1 GitHub Issue
+
1 Dedicated Branch
+
1 Pull Request
```

例如：

```text
Issue:
RFC-001: Repository and Application Architecture

Branch:
rfc/001-repository-application-architecture

PR:
docs(rfc): define repository and application architecture
```

## RFC Issue Contract

每个 RFC Issue 至少包含：

- RFC ID
- Problem
- Context
- Related DEC
- Related Specs
- Dependencies
- Scope
- Non-goals
- Decision Questions
- Candidate Options
- Research Requirements
- Acceptance Checklist
- Blocking Modules
- Open Risks
- Current Status
- Branch
- Pull Request
- User Decision

Issue 不替代正式 RFC 文档。

## RFC Branch Contract

RFC Branch 主要允许修改：

```text
docs/rfcs/**
docs/architecture/**
docs/traceability/**
docs/readiness/**
```

必要时可以增加最小技术验证，但必须位于：

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

## RFC Pull Request Contract

RFC PR 至少包含：

- Problem
- Related Decisions
- Related Specs
- Dependencies
- Decision Questions
- Chosen Option
- Alternatives
- Trade-offs
- Architecture Impact
- Data Impact
- Security Impact
- Migration
- Rollback
- Testing
- Open Questions
- Decision Status
- User Acceptance Gate

PR Merge 不自动等于 RFC Accepted。

正式流程：

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

如果项目为了保留 Review 记录先 Merge Draft 文档，则该文档状态必须继续保持 `IN REVIEW`，不得因 Merge 自动变为 `ACCEPTED`。

## Decision Questions Contract

每个 RFC 必须先拆成有限的 Decision Questions。每个 Decision Question 至少包含：

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

关键 Decision Question 必须由用户逐项或成组明确确认。Agent 不得在一份大型 RFC 中隐藏未经确认的核心技术选择。

## RFC-001 Initial Decision Questions

RFC-001 至少讨论：

1. 正式应用采用 Modular Monolith 还是 Multi-service
2. 正式项目目录结构
3. Domain、Application、Infrastructure、Interface 分层
4. Domain 是否依赖 LangGraph
5. LangGraph 位于哪一层
6. Graph Node 是否可以直接访问数据库
7. Skill 是 Function、Service、Package 还是其他代码形态
8. Repository Interface 位于哪一层
9. Repository Implementation 位于哪一层
10. Dependency Injection
11. Configuration Management
12. Environment Boundary
13. Test Layering
14. Spike 和 Production 的隔离
15. Package Import Boundary
16. 未来 Worker 和 API 如何接入应用层

## Roadmap Generation Gates

Roadmap 采用分阶段生成。

### Roadmap Draft v0 Gate

当以下 RFC 被接受：

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

此阶段主要允许规划：

- Repository Foundation
- Database Foundation
- Runtime Foundation
- Test Foundation
- CI Foundation
- Shared Contracts

是否创建具体 Foundation Implementation Issues，必须根据对应 Accepted RFC 单独确认。不得生成完整业务功能 Backlog。

### Roadmap v1 Gate

当：

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

届时才允许系统化拆分：

- Product Intake and Fact Extraction
- Customer Insight Analysis
- Product Positioning
- Human Review
- Marketing Brief Generation
- Xiaohongshu Adapter
- Evaluation
- Reliability
- Portfolio Demo

## Implementation Issue Gate

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

Issue 模板至少包括：

- Goal
- Business Requirement
- Relevant DEC
- Relevant Spec
- Relevant RFC
- In Scope
- Out of Scope
- Implementation Notes
- Acceptance Criteria
- Required Tests
- Dependencies
- Evidence Required
- Rollback Considerations

缺少 Accepted RFC 的工作只能标记为：

```text
type: research
type: spike
type: planning
```

不得标记为：

```text
type: implementation
```

## RFC Conflict Handling

RFC 起草期间若发现：

- Accepted DEC 无法实现
- 两个 Specs 冲突
- Spike 结论不能推广到生产
- 生产方案要求改变业务边界
- 两个 RFC 出现无法调和的接口冲突

必须创建：

```text
Decision Conflict Report
```

至少包括：

- Conflict ID
- Conflicting Decisions or Specs
- Actual Conflict
- Impact
- Reproduction or Evidence
- Candidate Resolutions
- DEC Revision Required
- Spec Revision Required
- Additional Spike Required
- Recommended Action
- User Decision Required

不得在 RFC 中直接改写上游 Decision 或 Spec。

## RFC Acceptance Criteria

RFC 只有满足以下条件，才能提交用户接受。

### Decision Completeness

- 核心技术问题有明确结论
- 候选方案完整
- 拒绝原因完整
- Trade-off 清晰
- 没有隐藏核心选择
- Open Questions 不阻塞对应实现

### Architecture Compatibility

- 不违反 Accepted DEC
- 不违反 Current Specs
- 符合 Architecture Baseline
- 与其他 Accepted RFC 一致
- 不错误推广 Spike 临时方案

### Implementation Readiness

- 模块边界明确
- 接口明确
- 数据责任明确
- 事务边界明确
- 错误边界明确
- 测试策略明确
- Migration 明确
- Rollback 明确
- Security Boundary 明确

### Traceability

必须关联：

```text
Requirement
DEC
Spec
Architecture
RFC
Future Epic
Future Test
```

## Agent Authority

RFC Agent 可以：

- 创建 RFC Issue
- 创建 RFC Branch
- 创建 RFC Draft
- 创建 RFC PR
- 搜索官方技术文档
- 比较技术方案
- 创建最小 Prototype
- 运行技术验证
- 更新 Traceability
- 提交 RFC Recommendation
- 根据 Review 修改 RFC

RFC Agent 不得：

- 自行接受 RFC
- Merge 尚未经过用户接受的 RFC PR
- 创建正式业务实现
- 创建完整生产 Backlog
- 修改 Accepted DEC
- 修改 Current Specs 的业务含义
- 将 Prototype 直接转成生产代码
- 将 Architecture Readiness 更新为完全 READY
- 将 Development Status 更新为完全 READY

## Contract Summary

```text
Decision:
DEC-038

Planning Model:
Dependency-driven RFC Waves

RFC Workflow:
Issue
→ Decision Questions
→ Draft
→ Branch
→ Pull Request
→ Review
→ Explicit User Acceptance
→ ACCEPTED
→ Merge

RFC Root Dependency:
RFC-001 Repository and Application Architecture

Roadmap Draft v0 Gate:
RFC-001, RFC-002 and RFC-003 accepted

Roadmap v1 Gate:
RFC-001 through RFC-007 accepted

Hard Rule:
No production implementation without relevant Accepted RFC
```

## Reason

Technical Spike 已证明关键 Runtime、Persistence、Human Review、Retry、Recovery、Checkpoint 和 Observability 行为具备可行实现方式。但 Spike 使用的是临时技术栈：

- Python 3.13
- LangGraph 1.2.9
- SQLite
- SqliteSaver
- Scripted Model
- Mock Retrieval
- JSONL Trace

这些选择不是生产承诺。在进入正式开发前，必须通过 RFC 确定：

- 正式项目结构
- 正式数据持久化
- 正式 Workflow Runtime
- 正式 Human Review API
- 正式 Retrieval
- 正式 LLM Runtime
- 正式 Observability

依赖驱动的 RFC 流程可以避免 Coding Agent 在实现过程中临时决定核心架构，并使每项技术选择能够追溯到 DEC、Spec、Spike Evidence、RFC、Epic 和 Test。

## Impact

该决定将影响：

- RFC Register
- RFC Issue
- RFC Branch
- RFC Pull Request
- Architecture Documents
- Roadmap Draft
- Epic Planning
- Implementation Issue Gate
- Coding Agent 权限
- Traceability Matrix
- Development Status Governance

## Decision Boundary

本决定已经确认：

- 依赖驱动 RFC Planning
- RFC 状态模型
- 用户 Acceptance Authority
- RFC-001 至 RFC-007 的职责
- RFC 依赖结构
- RFC Waves
- 并行调研边界
- 单 RFC Issue / Branch / PR
- PR Merge 不自动等于 RFC Accepted
- Decision Questions
- Roadmap Draft v0 Gate
- Roadmap v1 Gate
- Implementation Issue Gate
- RFC Conflict Handling
- RFC Acceptance Criteria
- Agent Authority
- 当前下一议题为 RFC-001

本决定尚未确认：

- RFC-001 的具体架构方案
- Modular Monolith 或 Multi-service
- 正式代码目录
- 正式后端语言
- Production Database
- ORM
- Production Checkpointer
- API Framework
- Worker 和 Queue
- Model Provider
- Embedding
- Vector Database
- Observability Provider
- Deployment Platform
- 实际 RFC Issue 编号
- 实际 RFC Branch
- 实际 RFC PR
- Roadmap 内容
- Epic 内容
- Production Implementation Issues

## Related Decisions

- DEC-001 through DEC-037
- 特别关联：
  - DEC-023
  - DEC-024
  - DEC-025
  - DEC-029
  - DEC-032
  - DEC-033
  - DEC-034
  - DEC-035
  - DEC-036
  - DEC-037

## Related Architecture Readiness

```text
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
```

## Related RFC

None.

## Supersedes

None.

## Amends

Architecture Readiness Governance by defining the RFC and Roadmap process allowed under `CONDITIONALLY READY`.
