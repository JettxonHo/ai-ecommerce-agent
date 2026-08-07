# RFCs（Proposal Layer）

本目录是 AI Ecommerce Agent 项目的 **Proposal Layer（提案层）**，保存重大方案及其替代方案。

> **当前阶段：** RFC Planning and Dependency Order（DEC-038 已接受）。  
> **状态：** Architecture Readiness = `CONDITIONALLY READY` · Development Status = `CONDITIONALLY READY`。  
> **当前状态：** [RFC-003: LangGraph Runtime and Checkpoint Architecture](rfc-003-langgraph-runtime-and-checkpoint-architecture.md) 与 [RFC-006: LLM Runtime and Structured Output](rfc-006-llm-runtime-and-structured-output.md) 均已接受；Product Specification 已于 2026-08-07 整体闭合，当前 [RFC-004: API and Human Review Architecture](rfc-004-api-and-human-review-architecture.md) = `DRAFTING`（Issue #54；P-48A～P-56A / DQ-01～09 已由 DEC-063～065 接受，P-57 / DQ-10 Proposed，Final Review / overall acceptance pending）。Implementation、Spike Execution 与 Goal Activation 仍未授权。

---

## 定位

- RFC 用于决定：已经由 DEC 和 Specs 定义、并由 Technical Spike 证明具备可行实现方式的需求，在生产环境中具体采用什么技术方案实现。
- RFC 必须回答 Problem、Context、Related Decisions、Related Specifications、Decision Questions、Candidate Options、Chosen Option、Rejected Alternatives、Trade-offs、Architecture Boundaries、Data and Transaction Boundaries、Error and Recovery Boundaries、Security Considerations、Testing Strategy、Migration Strategy、Rollback Strategy、Operational Impact、Affected Modules、Blocking Dependencies、Open Questions 和 User Acceptance Gate。
- **RFC ≠ 已接受决定。** 即使 RFC 状态为 `Accepted`，也只有当对应内容被用户明确确认后，才会同步到 Current Truth Layer。
- RFC 不得改变 Accepted Business Requirement、不得静默修改 DEC、不得静默修改 Current Specs、不得用技术限制取消业务规则。

---

## 何时创建 RFC

Architecture Readiness 进入 `CONDITIONALLY READY` 后，项目采用依赖驱动的 RFC 波次（见 [DEC-038](../decisions/dec-038-rfc-planning-and-dependency-order.md)）。当前已登记 7 个 Required RFC，编号 RFC-001 至 RFC-007，覆盖进入生产实现前必须收敛的核心技术域。

RFC 适用情况：

- 影响多个模块
- 难以回滚
- 改变核心数据模型
- 改变 MVP 范围
- 定义 Agent 职责边界
- 引入外部系统或 API
- 涉及安全、权限或隐私
- 存在多个合理方案
- 实现成本较高
- 未来很可能被重新质疑

**不创建 RFC 的情况：** 普通讨论、小型字段命名、临时文案或容易撤销的实现细节。

> 纪律：不得因为出现一个建议就自动创建额外 RFC。RFC-001 至 RFC-007 已覆盖 Architecture Readiness 阶段识别的全部生产技术决策域。

---

## 状态

项目 RFC 状态采用 DEC-038 定义的模型：

| 状态 | 含义 |
|------|------|
| `PROPOSED` | 已登记，尚未开始完整讨论 |
| `DRAFTING` | 正在调研、讨论 Decision Questions 和编写草案 |
| `IN REVIEW` | 主要 Decision Questions 已形成推荐结论，进入用户与架构审查 |
| `ACCEPTED` | 用户明确接受 |
| `BLOCKED` | 被依赖问题、Decision Conflict、缺少证据或待补充 Spike 阻塞 |
| `REJECTED` | 用户明确拒绝 |
| `WITHDRAWN` | 已不再需要或由提出者撤回 |
| `SUPERSEDED` | 已被后续 Accepted RFC 替代 |

**PR Merge 不自动等于 RFC Accepted。** 正式顺序：

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

---

## 编号与命名

- 起始编号：`RFC-001`
- 文件名格式：`rfc-NNN-topic-name.md`

当前已登记 Required RFC：

| RFC | 主题 | Wave | 当前状态 |
|-----|------|------|----------|
| RFC-001 | Repository and Application Architecture | Wave 1 | `ACCEPTED` |
| RFC-002 | Persistence and Transaction Architecture | Wave 1 | `ACCEPTED` |
| RFC-003 | LangGraph Runtime and Checkpoint Architecture | Wave 2 | `ACCEPTED` |
| RFC-004 | [API and Human Review Architecture](rfc-004-api-and-human-review-architecture.md) | Wave 3 | `DRAFTING`（Issue #54；DQ-01～09 Accepted，DQ-10 Proposed as P-57） |
| RFC-005 | Source Processing and Retrieval Architecture | Wave 3 | `PROPOSED` |
| RFC-006 | LLM Runtime and Structured Output | Wave 2 | `ACCEPTED`（2026-08-06 用户明确整体接受） |
| RFC-007 | Observability and Runtime Operations | Wave 4 | `PROPOSED` |

完整清单与依赖关系见 [rfc-register.md](rfc-register.md)。

---

## 模板

新建 RFC 请复制 [rfc-template.md](rfc-template.md)，并遵循 DEC-038 的 Decision Questions Contract 与 PR Contract。

---

## 工作流

每个 RFC 使用：

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

---

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

---

## Roadmap Gates

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

---

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

缺少 Accepted RFC 的工作只能标记为 `type: research`、`type: spike` 或 `type: planning`，不得标记为 `type: implementation`。

---

## Conflict Handling

RFC 起草期间若发现 Accepted DEC 无法实现、Specs 冲突、Spike 结论不能推广到生产、生产方案要求改变业务边界、RFC 之间接口冲突，必须创建 **Decision Conflict Report**，不得直接在 RFC 中改写上游 Decision 或 Spec。

---

## Acceptance Criteria

提交用户接受的 RFC 必须满足：

- **Decision Completeness** — 核心技术问题有结论、候选方案完整、拒绝原因完整、Trade-off 清晰、无隐藏核心选择、Open Questions 不阻塞实现。
- **Architecture Compatibility** — 不违反 Accepted DEC 与 Current Specs，符合 Architecture Baseline，与其他 Accepted RFC 一致，不错误推广 Spike 临时方案。
- **Implementation Readiness** — 模块边界、接口、数据责任、事务边界、错误边界、测试策略、Migration、Rollback、Security Boundary 明确。
- **Traceability** — 关联 Requirement、DEC、Spec、Architecture、RFC、Future Epic、Future Test。

---

## Agent Authority

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

---

## 当前 RFC 列表

完整清单见 [rfc-register.md](rfc-register.md)。

| RFC | 主题 | Wave | 当前状态 |
|-----|------|------|----------|
| RFC-001 | Repository and Application Architecture | Wave 1 | `ACCEPTED` |
| RFC-002 | Persistence and Transaction Architecture | Wave 1 | `ACCEPTED` |
| RFC-003 | LangGraph Runtime and Checkpoint Architecture | Wave 2 | [`ACCEPTED`](rfc-003-langgraph-runtime-and-checkpoint-architecture.md) |
| RFC-004 | [API and Human Review Architecture](rfc-004-api-and-human-review-architecture.md) | Wave 3 | `DRAFTING`（Issue #54；DQ-01～09 Accepted，DQ-10 Proposed as P-57） |
| RFC-005 | Source Processing and Retrieval Architecture | Wave 3 | `PROPOSED` |
| RFC-006 | [LLM Runtime and Structured Output](rfc-006-llm-runtime-and-structured-output.md) | Wave 2 | `ACCEPTED`（2026-08-06 用户明确整体接受） |
| RFC-007 | Observability and Runtime Operations | Wave 4 | `PROPOSED` |
