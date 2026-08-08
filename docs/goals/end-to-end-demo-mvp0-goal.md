# 端到端演示 MVP-0 Goal

> **Status: ACCEPTED — ACTIVATES ON PR #59 MERGE**
>
> **Owner:** Sol `ORCHESTRATOR_REVIEWER`
>
> **Implementer:** exact custom Agent `luna-worker` (`gpt-5.6-luna` / `max`, model status recorded per task)
>
> **Activation:** RFC-007、P-71A～P-73A、Development Plan、Testing Strategy、本 Goal 与精简 Readiness Review 已全部接受（DEC-073～075）。PR #59 合并后按 DEC-072 激活并创建首批 Issues。

## 1. 最终目标

依据全部 Accepted 产品、架构、接口、测试和治理文档，交付一个本地可复现、受控单工作区、使用单一真实 OpenAI Responses Provider 的端到端 AI Ecommerce Agent 演示 MVP。用户能够提交文本型商品资料，完成事实、洞察、定位、人工审核、通用 Marketing Brief、小红书 Brief 映射与 Markdown 导出闭环。

## 2. 背景与当前状态

- Product Specification、Frontend Architecture、RFC-001～007 已 Accepted；Foundation FND-001～003 与 disposable Spike-001 已完成。
- Production Package 当前是空业务 Foundation；API、PostgreSQL 实现、Migration、Worker、LangGraph Runtime、Model / Retrieval Runtime、业务 Skills 与 Frontend 尚不存在。
- MVP-0 按 DEC-070 使用 JSON / text / TXT / Markdown / CSV + Direct / Exact / PostgreSQL Lexical；PDF 与 Embedding / Semantic / Hybrid 后移 MVP-1。
- P-71A～P-73A 与完整策划包已接受；Goal 在规划 PR #59 合并后进入 ACTIVE。

## 3. 权威文档与阅读顺序

每个任务先读与自身范围相关的最小集合，不要求把全部历史 Session 塞进 Agent 上下文：

1. [AGENTS.md](../../AGENTS.md)
2. 本 Goal 与 [Implementation Readiness](../handoffs/implementation-readiness.md)
3. [Product Requirements](../product/prd.md)、[MVP Scope](../product/mvp-scope.md)、[User Flows](../product/user-flows.md)
4. [System Architecture](../architecture/system-architecture.md)、[Architecture Baseline](../architecture/architecture-baseline-v1.md)、[Frontend Architecture](../architecture/frontend-architecture.md)
5. 与 Issue 相关的 Accepted RFC / DEC / Spec；公共 HTTP 任务必须读 RFC-004，Source / Evidence 任务必须读 RFC-005，模型任务必须读 RFC-006，运行与日志任务必须读 RFC-003 / 007
6. [Development Plan](../development/mvp0-development-plan.md) 与 [Testing Strategy](../development/testing-strategy.md)
7. GitHub Issue、任务合同、依赖 PR 与当前实际代码 / 测试

冲突按 AGENTS 文档优先级处理；历史 Session 只解释来由，不能覆盖 Accepted Current Truth。

## 4. 工作范围与非工作范围

### Scope

- 固定工作区、本地浏览器 Task Workbench；
- 受支持文本资料 intake、版本、processing、Evidence 与 lexical retrieval；
- durable Task / Run / Stage / Review / Brief / Export Current Truth；
- PostgreSQL Business / Checkpoint、LangGraph、Durable Worker、恢复 / 幂等 / 取消；
- 一个真实 OpenAI Provider、确定性替身、四个 Core Skills 与小红书 Adapter；
- typed `/api/v1`、generated client、React SPA；
- 最小 RFC-007 运行证据；
- 固定验收包、真实 PostgreSQL测试、Browser E2E、一次 RC Live Smoke。

### Non-scope

与 Development Plan §3 Non-goals 完全一致。Issue 不得通过“顺手实现”引入账号、部署、抓取、OCR / 图片、PDF、向量、完整内容生成、自动发布、多 Agent Runtime、多 Provider 或平台运维系统。

## 5. 里程碑

| Milestone | Outcome | Exit Gate |
|---|---|---|
| M0 Planning | RFC-007、Plan、Test、Goal、Readiness Accepted | Goal 状态切换为 ACTIVE，首批 Issues 创建 |
| M1 Contract & Compatibility | OpenAPI、fixtures、local PostgreSQL、TS-01 / TS-03 bounded evidence | Stop-first slices PASS；公共 Contract / Fixture 可供消费者使用 |
| M2 Domain & Persistence | 核心身份、状态、版本、UoW 与 PostgreSQL Current Truth | Migration / transaction / invariant Integration PASS |
| M3 Source & Retrieval | MVP-0 Source processing、lexical retrieval、Evidence commit | 固定 retrieval evaluation 与 Scope hard gates PASS |
| M4 Runtime | Durable Worker、LangGraph、Model Port、Observability | Resume / idempotency / cancel / failure evidence PASS |
| M5 Business Skills | Fact / Insight / Positioning / Marketing Brief / XHS Adapter | 固定 fixtures 的 deterministic behavior PASS |
| M6 API & Review | `/api/v1` 纵向协议完整 | OpenAPI / generated client / Contract / integration PASS |
| M7 Web Workbench | 浏览器完整主路径与恢复路径 | component / contract / build / affected E2E PASS |
| M8 Release & Final Review | 新环境演示、Live Smoke、统一 Review | Goal completion criteria 全部满足 |

## 6. Implementation Backlog 候选

这些 ID 是 Goal 内候选，不是已创建 GitHub Issues。激活后 Sol 以当时代码和依赖重新核对，再逐个创建。

### M1

1. `MVP0-001` — authored OpenAPI 3.1 catalog、lint 与 contract-diff foundation。
2. `MVP0-002` — 虚构 Anchor SKU 物理 fixture / manifest / expected behavior pack。
3. `MVP0-003` — P-72A local PostgreSQL service、preflight 与受控 lifecycle。
4. `MVP0-004` — TS-01 bounded PostgreSQL transaction / multi-worker compatibility evidence。
5. `MVP0-005` — TS-03 bounded LangGraph `PostgresSaver` isolation / reconciliation evidence。

### M2

6. `MVP0-006` — shared identities、revision、version 与 error value objects。
7. `MVP0-007` — synchronous UoW / repository ports 与 PostgreSQL adapter base。
8. `MVP0-008` — Alembic baseline、fresh / one-step / recovery verification。
9. `MVP0-009` — Task / Run / Stage persistence vertical slice。
10. `MVP0-010` — Source / Source Version / Association persistence vertical slice。
11. `MVP0-011` — Review / Approved Strategy / Brief / Export persistence slice。

### M3

12. `MVP0-012` — JSON / manual text intake and processing lane。
13. `MVP0-013` — TXT / Markdown lane and format-aware locators。
14. `MVP0-014` — CSV record lane、bounded row issues 与 partial acceptance。
15. `MVP0-015` — authorized candidate relation、Direct / Exact / lexical retrieval。
16. `MVP0-016` — RetrievalRun / EvidencePackage / Validator / atomic Formal Evidence。
17. `MVP0-017` — fixed MVP-0 retrieval evaluation and explicit degradation。

### M4

18. `MVP0-018` — PostgreSQL Work Intent claim、Lease / Heartbeat / Fencing。
19. `MVP0-019` — cooperative cancellation、supersession 与 Commit Fence。
20. `MVP0-020` — LangGraph compact state、nodes、checkpoint topology。
21. `MVP0-021` — interrupt / resume、invalidation、seven-action reconciliation。
22. `MVP0-022` — narrow ModelRuntimePort、scripted substitute、structured output validators。
23. `MVP0-023` — OpenAI Responses Adapter、bounded recovery 与 offline contracts。
24. `MVP0-024` — RFC-007 logging / correlation / RuntimeErrorRecord / release evidence support。

### M5

25. `MVP0-025` — Fact Skill vertical slice。
26. `MVP0-026` — Insight Skill vertical slice。
27. `MVP0-027` — Positioning Skill vertical slice。
28. `MVP0-028` — Marketing Brief Skill vertical slice。
29. `MVP0-029` — Xiaohongshu Brief Adapter vertical slice。

### M6

30. `MVP0-030` — HTTP adapter foundation、Problem Details、fixed workspace boundary。
31. `MVP0-031` — Task / Source operations vertical slice。
32. `MVP0-032` — Run monitor / recovery / cancel / resume / rerun operations。
33. `MVP0-033` — Human Review save / submit / conflict operations。
34. `MVP0-034` — Brief / comparison / revise / Markdown export operations。
35. `MVP0-035` — generated TypeScript client adoption and API contract closure。

### M7

36. `MVP0-036` — React / Vite application foundation and CI scripts。
37. `MVP0-037` — `/tasks` recent list、create and stable deep links。
38. `MVP0-038` — intake / source processing / progress Workbench modes。
39. `MVP0-039` — Needs Input and recovery interactions。
40. `MVP0-040` — Review draft、autosave、diff、stale conflict and submit。
41. `MVP0-041` — Brief comparison、result and export interactions。
42. `MVP0-042` — accessibility / reflow / performance evidence for critical path。

### M8

43. `MVP0-043` — deterministic full Browser E2E and failure path suite。
44. `MVP0-044` — local one-command stack、new-environment rehearsal and operator guide。
45. `MVP0-045` — Release Candidate evidence、single opt-in OpenAI live smoke and human usability。
46. `MVP0-046` — Goal-wide final Review、documentation reconciliation and completion report。

Sol 可在创建 Issue 时进一步拆小，但不得合并无关目标或改变上述范围。编号变化必须在 Goal / status mapping 中记录。

## 7. Issue 与 PR 规则

- 每个 Issue 写明目标、背景、权威文档、In Scope、Non-goals、依赖、允许文件、冻结契约、验收、测试、风险、停止条件、PR / rollback 与 Reviewer。
- 一个 Issue 对应一个 `codex/` 分支和一个 PR；默认 100～300 行实质修改。测试 / generated file / lockfile / 单一 Migration 可说明例外。
- 实现 Agent 不能批准或合并自己的 PR。Sol 自己实现则必须由另一独立 Agent 或人工最终批准。
- 每个 PR 在合并前完成正确性、可读性、架构、安全、性能五轴 Review；后两轴按变更相关性，不机械制造无关检查。
- Required Checks、受影响 suite 与文档同步全部通过后，普通低风险 PR 可由 Sol 合并；人工 Gate 范围停止。

## 8. Agent 分配与并行

### 固定路由

```text
ORCHESTRATOR_REVIEWER: Sol / xhigh
IMPLEMENTER: exact custom agent luna-worker
config: ~/.codex/agents/luna-worker.toml
requested model: gpt-5.6-luna
requested effort: max
Terra fallback: prohibited unless current-task user authorization
```

每次 spawn 前读取配置并记录 `CONFIG_VERIFIED` / `RUNTIME_VERIFIED` / `UNVERIFIED_RUNTIME_MODEL` / `MODEL_MISMATCH`。当前环境已验证配置与可发现性，但未暴露实例模型，因此是 `CONFIG_VERIFIED`。

### 并行边界

- M1-001 Contract 与 M1-002 Fixture 可并行；它们分别拥有 `contracts/` 与 `tests/fixtures/mvp0/`。
- M1-003 local PostgreSQL 完成后，M1-004 与 M1-005 可以使用隔离 Database 并行，但不得同时修改共享 Compose / lifecycle scripts。
- Domain / persistence foundation 先于其 Source、Runtime、API 消费者。
- 各 Skill 在 Model Port、Evidence contract 与 Domain interfaces 冻结后可按独立模块并行。
- Web foundation 与后端业务能力可有限并行，但 generated client contract 未冻结前只能使用 typed fixture transport，不得猜测 API。
- 多个写入 Agent 不得无边界修改同一 core module、Migration head、OpenAPI authority、fixture manifest 或 lockfile。

## 9. 第一批标准任务合同

以下任务包只有 Goal 激活后才能派发；派发时必须补实际 GitHub Issue、Branch、base Commit、相关 PR / handoff 与最新测试状态。

### Contract MVP0-001 — Authored OpenAPI Foundation

```text
逻辑角色：IMPLEMENTER
自定义 Agent：luna-worker
目标：物理化 RFC-004 唯一 OpenAPI 3.1 authority，并建立 lint / diff / contract test 最小链路
权威文档：AGENTS → Goal → RFC-004 → DEC-063～066 → API specs → Testing Strategy
允许修改：contracts/openapi/**；受控 tooling / test files；直接相关 README / CI
禁止修改：业务实现、DB/Migration、Worker、Frontend 页面、Provider
验收：Operation/Schema/state/problem catalog 与 RFC-004 一致；无第二 contract authority；本地命令可重复；现有 8 checks 不回归
停止：发现 RFC-004 字段/状态冲突、需要选择未接受公共接口、生成工具反向覆盖 authored contract
Reviewer：Sol；实现者不得批准/合并
```

### Contract MVP0-002 — Acceptance Fixture Pack

```text
逻辑角色：IMPLEMENTER
自定义 Agent：luna-worker
目标：创建虚构 Anchor SKU 的三个资料包、mutation 与 expected behavior manifest
权威文档：DEC-048 / 058～062 → Product Requirements → Testing Strategy §2/§8
允许修改：tests/fixtures/mvp0/**；直接相关测试 loader / docs
禁止修改：业务代码、Prompt、Provider、公共 API、真实用户资料
验收：四个逻辑 ID 物理存在；明确 fictional；JSON/text/TXT/MD/CSV only；expected 不锁死完整模型措辞；无 hash
停止：需要真实资料、PDF/图片/联网数据、产品语义组不明确
Reviewer：Sol
```

### Contract MVP0-003 — Local PostgreSQL Lifecycle

```text
逻辑角色：IMPLEMENTER
自定义 Agent：luna-worker
目标：按 P-72A 提供一个 PostgreSQL Service、两个独立 Database 的受控本地 lifecycle 和 preflight
权威文档：RFC-002 / 003 → Development Plan P-72A → Testing Strategy
允许修改：compose.yaml；scripts 下窄 lifecycle；example env；直接相关 docs/tests
禁止修改：生产 schema、Migration、API/Worker/Web 实现、真实 Secret
验收：health/readiness、up/down、非破坏性默认、明确 reset-demo 人工动作、进程退出清理、文档新环境可执行
停止：需要额外 service、自动删除非 demo 数据、依赖未接受平台
Reviewer：Sol
```

### Contract MVP0-004 — PostgreSQL Compatibility Slice

```text
逻辑角色：IMPLEMENTER
自定义 Agent：luna-worker
目标：用真实 PostgreSQL 证明同步 SQLAlchemy/Psycopg/Alembic、短事务、多连接 claim / fencing 的 bounded compatibility
依赖：MVP0-003
允许修改：专用 compatibility test module、最小 test-only schema/migration、证据文档、锁文件的必要依赖
禁止修改：正式业务表、通用安全框架、完整 Worker、SQLite 验收
验收：fresh migration、rollback/repair、two-worker claim、higher fencing、stale commit rejection、零部分 Current Truth；证据可复现
停止：任何核心不变量失败；停止 M2/M4 相关生产 Issue并回到架构 Gate
Reviewer：Sol
```

### Contract MVP0-005 — LangGraph Checkpoint Compatibility Slice

```text
逻辑角色：IMPLEMENTER
自定义 Agent：luna-worker
目标：用独立 PostgreSQL Checkpoint DB 证明 sync PostgresSaver、thread isolation、interrupt/resume 与 Current-Truth-first reconciliation
依赖：MVP0-003；可与 MVP0-004 在数据库与文件所有权隔离后并行
允许修改：专用 compatibility harness/tests、证据文档、必要锁文件依赖
禁止修改：复制 Spike source、正式业务 Graph/Skills、SQLite acceptance、Live Provider
验收：隔离、stale checkpoint、resume、七动作代表路径、compatibility refusal；失败无业务 Current Truth 污染
停止：Checkpoint 需要成为业务权威、无法安全 resume/reconcile、依赖版本不兼容
Reviewer：Sol
```

每次正式派发还必须附：当前线程、Issue、Branch / worktree、base / latest Commit、已存在修改、实际测试命令、其他 Agent 文件所有权、标准结果包格式。

## 10. 测试、Review 与验收

以 [Testing Strategy](../development/testing-strategy.md) 为权威。普通 PR 不运行 Live Provider；真实 PostgreSQL是持久化验收引擎；Browser E2E 使用确定性 Model Substitute。Release Candidate 只执行一次 opt-in OpenAI Smoke，不把语言措辞机械评分。

Sol Review 必须检查实际 Diff 和证据，不根据 PR 描述直接批准。`CHANGES_REQUESTED` 的每项 Finding 包含位置、影响、证据和期望；修复交回 `luna-worker`，重新验证后再审。

## 11. 风险与停止条件

立即停止受影响工作并请求用户确认：

- 与 Accepted Decision / RFC / Spec 冲突；
- 需要扩大 MVP-0 或启用明确 Non-scope 能力；
- 更换已接受数据库、Runtime、Provider、Frontend major stack、HTTP framework（接受后）或公共契约；
- compatibility slice 暴露核心 transaction、resume、idempotency、scope 或 evidence consistency 缺陷；
- 需要数据破坏、不可逆 Migration、生产凭证、高风险外部操作；
- 需要降低测试、Review 或验收标准；
- `luna-worker` 不可用，且用户未授权替代 Agent。

## 12. Goal 完成标准

只有以下全部满足才可标记 `COMPLETE`：

- 计划 Issues 正确关闭，PR 均独立 Review、测试并合并；
- 新环境按文档启动本地栈；
- 浏览器完成资料输入到 Marketing Brief / Xiaohongshu Brief / Markdown export 闭环；
- Human Review、恢复、幂等、取消、失效重跑、版本与证据追溯符合规格；
- Required Checks、确定性测试、真实 PostgreSQL suites、build、Browser E2E 全部通过；
- 一次真实 OpenAI Provider RC Smoke 通过；
- Critical / Blocking 缺陷为零，其他限制有记录与处置；
- 文档、DEC、RFC、Traceability 与最终实现一致；
- Goal 级统一 Review 完成，并输出功能 / 里程碑、Issues / PR、测试 / 构建、决策、限制、风险、债务、发布建议和最终验收结论。

最终状态只允许 `GOAL_APPROVED`、`GOAL_APPROVED_WITH_FOLLOW_UPS`、`GOAL_BLOCKED` 或 `GOAL_REJECTED`。

## 13. 当前进度与下一步

```text
M0 Planning: IN PROGRESS
M1–M8: NOT STARTED
Active implementation Issues: 0
Active luna-worker write tasks: 0
Current blockers: P-68A/P-69A/P-70A, RFC-007 overall, P-71A/P-72A/P-73A,
                  Development Plan, Testing Strategy, Goal, Readiness acceptance
Next: complete consistency/readiness review, display package, obtain user decisions
```
