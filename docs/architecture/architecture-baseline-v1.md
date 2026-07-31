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
RFC-001 Repository and Application Architecture [ACCEPTED — 2026-07-30]
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

## 10. 已确认 Production Skeleton 范围、Foundation 授权门与 RFC 收口（RFC-001-DQ-10）

> 来源：RFC-001-DQ-10（ACCEPTED）。RFC 接受与开发授权严格分离；RFC-001 最终接受仅开放 **Foundation Planning**，不授权 Foundation Implementation、Business Implementation 或任何生产代码的自动创建。**RFC-001 已于 2026-07-30 整体 ACCEPTED；Foundation Planning 开放，Foundation/Business/Production Implementation 与 Production Skeleton 创建仍 NOT AUTHORIZED。**

### 10.1 Acceptance 与 Authorization 分离

- `RFC-001 Acceptance ≠ Foundation Planning Authorization ≠ Foundation Implementation Authorization ≠ Business Implementation Authorization`。
- 接受某个 DQ 不代表授权开发；接受 RFC-001 整体仅使 Repository and Application Architecture 成为正式 Architecture Baseline，不自动授权生产实现。
- 当前授权状态：`Foundation Planning = NOT AUTHORIZED`、`Foundation Implementation = NOT AUTHORIZED`、`Business Implementation = NOT AUTHORIZED`、`Architecture Readiness / Development = CONDITIONALLY READY`、`Production Implementation = NOT AUTHORIZED`。
- DQ-10 接受后唯一允许的下一步是 **RFC-001 Final Consistency Review**，不得创建 Production Skeleton。

### 10.2 RFC-001 Final Acceptance Flow

`DQ-10 ACCEPTED → Archive DQ-10 → Final Consistency Review → Final Review Report → 用户明确接受 RFC-001 → RFC-001 Status = ACCEPTED → Merge RFC-001 PR → Close RFC-001 Issue → Delete RFC Branch`。PR Merge 不能替代用户接受；用户未明确接受前 RFC-001 保持 `DRAFTING`、PR 不得 Merge、Issue 保持 OPEN、Foundation Planning 不得自动开始。

### 10.3 RFC-001 Acceptance Result

用户最终接受 RFC-001 后：`RFC-001 Status = ACCEPTED`、`Foundation Planning = AUTHORIZED`、`Foundation Implementation = NOT AUTHORIZED`、`Business Implementation = NOT AUTHORIZED`、Readiness/Development 保持 `CONDITIONALLY READY`、Production Implementation 保持 `NOT AUTHORIZED`。RFC-001 接受只开放 Foundation Planning，不开放自动创建 Foundation Issues / 自动执行 Foundation Work / 自动建立 Production Skeleton / 业务功能开发。

### 10.4 Foundation Implementation Authorization

每个 Foundation Issue 必须单独获得用户明确授权：`RFC-001 ACCEPTED → Generate Foundation Issue Candidates → 用户审查范围与依赖 → 用户明确授权单个 Issue → Create Issue → Create Branch → Create PR → Execute bounded Foundation Work → 用户审查并 Merge`。Foundation Planning 已授权不等于自动执行全部 Foundation Issues。

### 10.5 Foundation Work Definition 与 Initial Skeleton Scope

- Foundation Work = 建立生产代码安全进入 Repository 的工程基础，允许范围：Python Package 基础、Python Version Constraint、Dependency Manifest、Lockfile、Ruff、Pyright、pytest、Coverage、Import Linter、Architecture Tests、GitHub Actions、Dependency Audit、Secret Detection、Dependabot、PR/Issue Templates、本地统一质量命令、Backend Developer Documentation。**不包括业务能力实现**。
- RFC-001 最终接受且具体 Foundation Issue 授权后，可按需创建 `apps/backend/`（`pyproject.toml` / `uv.lock` / `.python-version` / `README.md` / `src/ai_ecommerce_agent/__init__.py` / `py.typed` / `tests/{architecture,unit,contract}/`）与 Repository 级 `.github/{workflows,ISSUE_TEMPLATE,pull_request_template.md}` / `scripts/` / `tooling/`。
- 只创建承担真实职责的文件与目录；**不得为匹配架构图批量创建空 Package**。

### 10.6 Business Module Creation Boundary

首批 Foundation Work **不创建** `modules/{product_intake,customer_insight,product_positioning,human_review,marketing_brief,xiaohongshu_adapter,source_evidence}/`。业务模块只能在 `Relevant DEC + Relevant Spec + Accepted RFC + Authorized Implementation Issue` 齐备后按需创建；不得以「提前搭 Skeleton」为由创建空业务模块。

### 10.7 Platform / Orchestration / Entrypoint / Bootstrap Boundary

- 首批不创建具体 `platform/{persistence,workflow_runtime,retrieval_runtime,model_runtime,observability}/` 实现（分别等待 RFC-002 / RFC-003 / RFC-005 / RFC-006 / RFC-007）。
- 首批不创建 Production LangGraph Graph / Graph Nodes / Graph State / Routing / Checkpoint Adapter / Retry / Resume / Worker Runtime（等待 RFC-003）。
- 首批不创建 API（Framework / Routes / Schema / Authentication / Human Review Endpoint / Polling/SSE/WebSocket，等待 RFC-004）、Worker（Queue / Durable Dispatch / Job Consumer / Lease / Heartbeat / Resume Consumer，等待 RFC-003）、空 CLI Entrypoint（Production CLI 在明确 Runtime / Management Issue 中创建）。
- `bootstrap/` 架构位置已确认，但首批 Foundation Work 不实现 Production Bootstrap（Settings/Database/Runtime/API/Worker/Model Provider/Retrieval 均未选择），须等待相关 Accepted RFC 与实施授权。

### 10.8 Persistence / Workflow Runtime / API·HumanReview / Retrieval / LLM / Observability Prohibition

首批 Foundation Work 不得创建：Production Database / ORM / Migration / Repository / Unit of Work / Database Session / 各业务表（RFC-002）；Production LangGraph / Graph State / Checkpointer / Workflow Worker / Queue / Durable Dispatch / Resume / Cancellation / Recovery Runtime（RFC-003）；API Framework / Task/Run/Review Endpoint / Submit·Resume Protocol / Authentication / Authorization / Frontend Status Protocol（RFC-004）；Source Parser / Fragmentation / Embedding / Vector Store / Index / Retrieval Runtime / EvidencePackage Runtime（RFC-005）；Model Provider / Provider Client / Prompt Registry / Structured Output Runtime / Retry·Repair Runtime / Provider Fallback / Live Model Evaluation Runtime（RFC-006）；Production Trace Provider / Metrics Exporter / Alerting / Dashboard / Incident Runtime / Operator Recovery Queue（RFC-007）。

### 10.9 Frontend Boundary

首批 Foundation Work 不创建 Frontend Framework / Web Application / Human Review UI / Task Dashboard / Generated API Client / Frontend Runtime；等待正式 Frontend Architecture Decision 与授权 Issue。

### 10.10 Spike-001 Boundary

Spike-001 继续位于 `spikes/`，仅作为 Architecture Evidence / Failure Catalogue / Regression Scenario Reference / Acceptance Criteria Input / Recovery Test Design Input / Trace Requirement Input；允许提取测试场景、故障模式、设计约束、验收标准、Trace 字段要求、Recovery 测试思路。**禁止** `Copy Spike Source → Rename Package/Imports → Move into Production Package`；Production Implementation 必须依据 Accepted RFC 重新设计与实现。

### 10.11 Foundation Issue Candidates 与 Dependency Order

- **FND-001 Backend Package and Local Tooling Foundation**：`apps/backend/`、Python 3.13 Constraint、`pyproject.toml`、`uv.lock`、`.python-version`、Package Root、`py.typed`、Ruff、Pyright、pytest、Coverage 基础配置、统一本地命令、Backend README；不含业务模块 / Bootstrap / API / Database / LangGraph / Worker / Provider。
- **FND-002 Architecture Enforcement and Test Foundation**（依赖 FND-001）：Import Linter、`tests/architecture/`、Layer Contracts、Public Facade Contract、DAG Contract、Spike Isolation、Architecture Fixture、Negative Architecture Tests、pytest Strict Marker、测试分类基础、Architecture Test Documentation；不含真实业务模块测试 / Production Repository / Production Graph Runtime / Provider Adapter。
- **FND-003 CI, Security and Repository Protection**（依赖 FND-001 + FND-002）：GitHub Actions、稳定 Required Check Names、Ruff/Pyright/pytest/Architecture Checks、`pip-audit`、Secret Detection、Dependabot、PR/Issue Template、Branch Protection、Local/CI Command Consistency；不含 Deployment Pipeline / Production Environment / Cloud Infrastructure / Container Registry / Live Model Evaluation / Production Runtime。
- 依赖顺序 `FND-001 → FND-002 → FND-003`；每个 Issue 用 `One Issue → One Branch → One PR → Required Verification → User Merge Gate`；不得合并为一个无边界大型 Foundation PR（除非用户后续明确修改）。

### 10.12 Architecture Fixture Boundary

业务模块尚未创建时，不得创建虚假生产业务模块以验证 Architecture Rules。允许在 `apps/backend/tests/architecture/fixtures/` 建立测试 Fixture，模拟 Domain 错误 Import Infrastructure / 模块绕过 Public Facade / 循环依赖 / Production Import Spike；Fixture 只属于 Test Code、不得被 Production Import、不代表真实生产模块、用于证明 Architecture Checker 能识别违规。

### 10.13 Foundation Verification Requirements 与 PR Evidence

- Foundation PR 至少证明 15 项：Formatting / Lint / Type 违规失败；Domain Import Infrastructure 失败；跨模块绕过 Public Facade 失败；模块依赖循环失败；Production Import Spike 失败；未注册 pytest Marker 失败；Unit Test 失败阻止 Merge；Coverage Gate 启用后低于阈值失败；Dependency Vulnerability 被检测；Secret Detection 阻止合并；本地与 CI 同一工具配置；Required Check Names 稳定；故意构造的 Architecture Violation 被正确拒绝。**不得通过空测试或无效 Fixture 伪造质量证据。**
- 每个 Foundation PR 输出：创建/更新文件、本地命令、测试结果、Architecture Check 结果、Type Check 结果、Dependency Audit 结果、Secret Scan 结果、Scope Deviations、未完成项、对应 Issue、相关 DEC/RFC、是否发现新 Architecture Decision、是否触发 Mandatory Stop Condition。

### 10.14 Mandatory Stop Conditions

Foundation Agent 在需要：选择 Database / ORM / API Framework / Worker Framework / Queue·Broker；创建生产 LangGraph / 业务模块；复制 Spike Source；降低 Accepted Quality Gate；修改 Accepted RFC；改变 Repository Root Structure；DQ 间出现矛盾；工具无法实现已接受 Architecture Contract；修改 Branch Protection 绕过失败；发现 Secret 或真实凭证；实施范围超出当前 Issue；创建后续 RFC 范围内技术实现 —— 时必须停止，并提交 Decision Conflict Report 或 Mandatory Stop Report，不得静默决定。

### 10.15 Production Business Implementation Gate

即使 RFC-001 与全部 Foundation Issues 完成，仍不得自动开始业务开发。按 DEC-038：`RFC-001/002/003 = ACCEPTED` 后才生成 MVP Roadmap Draft v0 / Epic Skeleton / Foundation Dependency Graph / Foundation·Runtime Issue Candidates；完整业务 Roadmap / Implementation Backlog / Business Issues 必须等待 `RFC-001 through RFC-007 = ACCEPTED`。

**Hard Rules：** RFC-001 Acceptance / DQ-10 Acceptance 均 DOES NOT AUTHORIZE IMPLEMENTATION；Foundation Planning 仅在 RFC-001 FINAL ACCEPTANCE 后授权；Foundation Implementation 需单独明确授权；Business Implementation 保持未授权；Initial Foundation Scope = PACKAGE + QUALITY + ARCHITECTURE TESTS + CI + REPOSITORY SECURITY；Initial Business Modules / Production Bootstrap / API·Worker·CLI / Database·ORM·Migration / Production LangGraph / Model·Retrieval·Observability 均 NOT IMPLEMENTED；Spike Source Migration PROHIBITED；Foundation Issue Order = FND-001→FND-002→FND-003；RFC-001 Final Acceptance 需 Final Consistency Review + 用户明确接受。

## 11. 已确认质量工具链、Architecture Enforcement、CI Quality Gate 与测试基线（RFC-001-DQ-09）

> 来源：RFC-001-DQ-09（ACCEPTED）。生产代码采用 Ruff、Pyright、pytest、Import Linter 与自定义 Architecture Tests 构成统一质量工具链；所有 PR 必须通过类型、架构、确定性测试、覆盖率、依赖和 Secret 检查，`main` 由 Required Status Checks 保护，AI Live Evaluation 与普通确定性 Merge Gate 分离。**RFC-001 已于 2026-07-30 ACCEPTED；Production CI 与 Skeleton 创建仍 NOT AUTHORIZED。**

### 10.1 Quality Governance Model

质量治理链路：`Accepted Architecture Decision → Machine-checkable Rule → CI Required Check → Merge Block`。质量检查分为 Code Correctness、Architecture Correctness、Business Behavior Correctness、Repository Governance Correctness。能自动验证的规则必须转化为工具配置、Architecture Test 或 Required CI Check，不得仅依赖文档理解边界。

### 10.2 Python Quality Toolchain

| 关注点 | 工具 |
|---|---|
| Formatter | Ruff Formatter |
| Linter | Ruff Linter |
| Type Checker | Pyright |
| Test Runner | pytest |
| Import Architecture | Import Linter |
| Semantic Architecture | Custom pytest Architecture Tests |
| Coverage | coverage.py / pytest 集成 |
| Dependency Vulnerability Audit | pip-audit |

不并行引入 Black / isort / Flake8 作为平行 Source of Truth。配置集中于 `apps/backend/pyproject.toml`。工具版本于 Foundation Implementation 经 Lockfile 固定（本 Decision 不锁定版本）。

### 10.3 Type Discipline

**Strict-first Type Discipline**：严格要求优先适用于 Domain / Application / Public Contract / Command / Query / Result / Public Error / Snapshot / Skill Input / Skill Result / Graph State / Runtime Identifier / Repository Port / Model Runtime Port / Retrieval Port / Dispatch Payload。`Any` 只能存在于明确外部边界（未验证 JSON / Provider SDK 原始响应 / 第三方动态对象 / Schema Validation 前协议输入），遵循 `External Dynamic Data → Entrypoint/Infrastructure Validation → Typed Contract → Application/Domain`。禁止全局 `Any` / 全局 Ignore / 关闭核心诊断绕过检查；第三方动态类型在 Infrastructure Adapter 边界收窄。原则：*Fix the type boundary before suppressing the checker*。

### 10.4 Architecture Enforcement

双层机制：Import Linter（Import Graph 可表达的结构规则）+ 自定义 pytest Architecture Tests（语义规则，位于 `apps/backend/tests/architecture/`）。Import Linter 初始 Contract：Domain Independence、Application Independence、Business Module Isolation、Public Facade-only 跨模块 Import、Orchestration Boundary、Entrypoint Boundary、Spike/Prototype Isolation、Shared Kernel Independence、Module Dependency DAG。语义 Architecture Tests 覆盖 Public Contract Shape、Skill Boundary、Orchestration Boundary、Configuration Boundary、Entrypoint Boundary。

### 10.5 Test Classification

```text
unit / integration / contract / architecture / e2e / evaluation / live / slow
```

所有 pytest Marker 必须预先注册，CI 启用严格 Marker 模式；未知或拼写错误的 Marker 必须导致失败。

### 10.6 Test Baselines

- Unit：确定性（无网络 / 真实模型 / 生产 DB / 生产 Secret；Fake Clock、确定性 ID、Scripted Model Runtime、固定 Retrieval Fixture、顺序无关、可重复）。
- Integration：真实技术边界（Repository / Unit of Work / Transaction / Migration / Checkpointer / Durable Dispatch / Model Runtime / Retrieval / Bootstrap / Resource Cleanup），隔离、可重建、可清理、验证 Commit 与 Rollback。
- Contract：Public Command/Query/Result/Error、Ports、Event / Dispatch Payload、API Schema、Graph State Schema、Adapter Compliance；阻止字段静默删除、ID/Version 语义改变、Query 副作用、Public Error Code 漂移、Event 泄漏内部 Entity 等。
- E2E：完整主流程 + 关键失败场景（Duplicate Submit / Stale Review / Worker Crash / Duplicate Resume / Stage Rerun / Downstream Invalidation / Provider Failure / Retry Exhaustion / Recovery / Cancellation），不只覆盖 Happy Path。
- Evaluation：验证 AI 结果质量而非确定性软件行为。固定 Fixture 的 Deterministic Evaluation 可进入普通 PR Gate；Live Evaluation（真实模型/Provider，有成本、网络、波动）默认运行于 Manual / Nightly / Prompt-or-Model-Policy-Change / Release Candidate，不作为普通 PR 唯一合并 Gate。

### 10.7 External Network Boundary

普通 Required PR Tests 默认无实时外部 Provider / 网络访问；需真实网络的测试标记 `live`。Unit / Contract / Architecture 不得意外调用 Model / Embedding Provider、Vector SaaS、外部网页、生产 DB、生产 Secret Manager；测试环境应能阻断未声明网络访问。

### 10.8 Coverage Policy

首批可执行生产代码进入后启用 Branch Coverage Measurement，Global Fail-under = 80%。Coverage 是风险指标而非业务正确性。Domain Invariant、Human Review、Current Truth、Idempotency、Evidence、Version、Stale Input、Retry、Recovery、Downstream Invalidation 即使覆盖率达 80% 仍必须有明确行为测试。允许精准排除；禁止大范围 `# pragma: no cover`。Skeleton 阶段不制造空测试抬高覆盖率，Coverage Gate 于可执行生产代码进入时启用。

### 10.9 Warning / Flaky / Randomness / Snapshot Policy

- Warnings = Errors by default；例外须精准匹配、说明原因、有清理条件；禁止 `ignore all warnings`。
- Required CI 禁止用自动重跑掩盖 Flaky Test；发现后记录 Issue、定位原因、必要时隔离、修复后恢复 Gate；被隔离/未运行测试不得描述为已通过。
- 随机性须固定 Seed、失败时输出 Seed、确定性 ID、控制时间/模型输出/Retrieval 排序。
- Skip / XFail 仅用于明确环境限制或已知缺陷（有关联 Issue、严格模式）；不得隐藏未完成 Acceptance Criteria、架构违规或必须通过的规则。
- Golden / Snapshot 内容可读、差异可审查、无 Secret / 随机时间戳，更新需人工语义审查，Coding Agent 不得自动接受所有变化。

### 10.10 Dependency and Secret Security

PR Dependency Audit 使用 pip-audit；启用 Dependabot Alerts 与受控 Security Updates。依赖变更须更新 Lockfile、通过完整 CI、说明用途、检查安全与 License。CI 必须具备 Secret Detection Gate（API Key / Private Key / Token / `.env` / Authorization Header / Cloud / Database Credential），具体 Scanner 于 Foundation Implementation 选择；检出后 `CI Failure → 移除 → 若为真实凭证则轮换/吊销`。

### 10.11 CI Gate Layers

- Layer 1 Fast Static Gate（每个 PR）：Repository Hygiene、Ruff Format Check、Ruff Lint、Pyright、Import Linter、Architecture Tests。
- Layer 2 Deterministic Test Gate（每个 PR）：Unit、Contract、Coverage、Dependency Audit、Secret Detection。
- Layer 3 Runtime Confidence Gate（生产 Runtime 建立后按变更范围）：Integration、Migration、Bootstrap、E2E Smoke、Recovery Tests。
- Extended Gate（Nightly / 手动 / Release Candidate）：Full E2E、Live Model Evaluation、Performance、Long Recovery、Dependency Compatibility。

### 10.12 Required Status Checks and Branch Protection

`main` 使用稳定 Required Check 名称（如 `quality/format`、`quality/lint`、`quality/typecheck`、`quality/architecture`、`test/unit-contract`、`test/integration`、`test/e2e-smoke`、`security/dependency-audit`、`security/secret-detection`），不得频繁修改。`main` 必须经 PR 合并、禁止直接 Push、禁止 Force Push、Required Status Checks 必须通过、Review Conversation 必须解决；用户保留最终 Merge 权限；当前个人 Portfolio Repository 不强制第二名 Reviewer。

### 10.13 Coding Agent CI Governance

CI 失败时 Coding Agent 不得删除失败测试、降低 Coverage Threshold、关闭 Pyright、添加全局 Ignore、删除 Import Linter Contract / Architecture Test、将 Required Check 改为 Optional、修改 Branch Protection、无审查更新全部 Snapshot、将失败改为 Skip 或自动 Merge。正确流程：`CI Failure → Determine Root Cause → Fix Code or Justified Test → Add Regression Test → Run All Affected Gates`。

### 10.14 Frontend / Foundation / Unified Commands

未来 TypeScript 生产代码至少要求 Strict Mode、Formatter、Linter、Unit test runner、Build check、Generated API contract drift check；具体工具（ESLint/Biome 等）延后至前端 Framework 决策。本地与 CI 使用统一命令入口（`quality-format` / `quality-lint` / `quality-type` / `quality-architecture` / `test-fast` / `test-integration` / `test-e2e` / `quality-all`），`Local checks = CI checks`。Foundation Skeleton 必须证明质量工具能阻止真实违规代码（格式 / Lint / 类型 / 架构 / Marker / Unit / Coverage / Dependency / Secret / Required Checks / 本地=CI / 故意构造的架构违规可被自动检测）。

### 10.15 Decision Boundary

已确认：Ruff formatter+linter（无 Black/isort/Flake8 平行 SoT）、Pyright strict-first、pytest + 严格 Marker、8 类测试分类、Required PR 无实时外部 Provider、Import Linter、自定义 Architecture Tests、确定性 Unit、隔离 Integration、Contract、E2E 失败覆盖、Evaluation 分离、分支覆盖率 80%（可执行代码后）、Warnings=Error、禁止 Flaky 自动重跑、Skip/XFail 规则、Snapshot 人工审查、pip-audit、Dependabot、Secret Detection、main 受 Required Checks 保护、无强制第二 Reviewer、用户最终 Merge Gate、禁止 Coding Agent CI 绕过、四层 CI Gate、TypeScript strict、前端工具延后、Foundation Skeleton 须阻止真实违规、本地=CI 统一命令。本 Decision 不锁定工具版本 / Secret Scanner / 前端工具 / CI YAML，且**接受后仍不授权创建 Production CI 或 Skeleton**。

尚未确认：Production Skeleton 范围、Foundation Issue 拆分、首批允许创建的目录/文件、CI Workflow 具体实现、Secret Scanner、工具版本、前端 Framework 与工具、Foundation Work Authorization、RFC-001 整体接受条件。

## 12. 已确认模块公开契约、跨模块协作与循环依赖治理（RFC-001-DQ-08）

> 来源：RFC-001-DQ-08（ACCEPTED）。

### 11.1 Module Public Facade

每个业务模块通过唯一稳定入口 `modules.<module>.public`（概念路径 `modules/<module>/public.py`）暴露跨模块契约。其他模块**只能**通过该 Public Facade 使用目标模块的公开能力；`public.py` 可重新导出内部定义的稳定 Contract，但对外 Import Path 必须保持为 `modules.<module>.public`。

### 11.2 Public Contract Surface

Public Facade 可以暴露：`Public Command / Public Query / Public Result / Public Error / Application Service Protocol / Published Application Event / Stable Identifier / Version Reference / Immutable Snapshot`。不得暴露：`ORM Model / Database Session / Repository Implementation / Mutable Domain Entity / Aggregate Internal / Infrastructure Adapter / Infrastructure Error / Graph State / LangGraph Node / Checkpoint Object / Provider SDK Type / Global Settings / Secret / Database Table Structure / Internal Helper`。Public Contract 必须 `Typed / Immutable / Serializable / Version-aware / Infrastructure-neutral`。

### 11.3 Public Snapshot Boundary

跨模块数据读取必须返回不可变公开 Snapshot（如 `ApprovedStrategySnapshot / ProductFactsSnapshot / ReviewPackageSnapshot / MarketingBriefSnapshot`），不得返回内部 Aggregate / ORM Entity / Lazy-loaded Relationship。外部模块不得持有或修改目标模块内部 Aggregate。业务类型被多模块使用**不代表**应移到 `shared_kernel/`；优先使用 `Owner Module Public Snapshot` 而非共享可变业务模型。

### 11.4 Command Contract and Cross-module Command Rule

Command 表达业务意图（`SubmitReview / ApproveStrategy / CreateMarketingBriefVersion / InvalidateDownstreamStage`），含目标业务 ID、必要 Version/Expected Version、Idempotency Key、调用者/授权上下文引用；不含 ORM Entity / Database Session / Graph State / Secret。Command 必须由拥有目标状态的 Application Service 执行。`Direct module-to-module state-changing Command = PROHIBITED BY DEFAULT`；跨 Stage 状态变化默认由 `Orchestration` 或 `Explicit Composite Application Use Case` 协调。例外须同时满足：明确业务所有权、单向依赖、不形成循环、不隐藏跨模块事务、已在 Spec/RFC/Architecture Review 声明、具有对应 Contract 与 Architecture Test。

### 11.5 Query Contract and Cross-module Read Rule

Query 只读、无副作用、不触发 Workflow、不发布业务 Event、返回 Public Snapshot、执行读取权限与业务可见性检查、返回结构化 Public Error；不得隐藏写入。跨模块读取正式采用 `Consumer Module → Target Module Public Query → Application Query Handler → Public Snapshot`；禁止 `Consumer Module → Target Module Repository → Direct SQL / ORM / Internal Table`。共享 Database Instance ≠ 共享数据所有权；数据库表不得成为模块间隐式 API。

### 11.6 Orchestration Responsibility

跨 Stage 协调（Stage 完成后启动下一个 Stage、Positioning 后创建 Review Package、Review 提交后调度 Resume、Approved Strategy 后启动 Marketing Brief、Rerun 使下游失效、Cancel/Resume/Recovery、跨模块 Workflow Routing、多 Stage 状态协调）由 `orchestration/` 或明确 Coordinator 执行。Orchestration 可调用模块 Public Application Contract、根据明确 Result 决定确定性路由、管理 Interrupt/Resume/Runtime Retry；不得拥有模块业务规则、直接访问模块 Infrastructure、直接读写模块内部表、直接更新 Current Truth、直接提交跨模块隐藏事务。

### 11.7 Composite Application Use Case

跨模块原子操作只能通过明确建模的 `Composite Application Use Case` 执行：有明确业务所有者、输入/输出/错误 Contract、事务边界；通过 Public Port 或正式协调接口访问参与模块；不直接 Import 其他模块 Infrastructure；不允许参与 Service 各自隐藏 Commit；具有原子性、失败和幂等测试；与 RFC-002 持久化事务架构一致。禁止 `Service A begins transaction → Service B begins hidden transaction → Partial commit`。默认跨模块流程采用多个短事务 `Transaction A → commit → Orchestration → Transaction B`。

### 11.8 Domain Event and Application Event

Domain Event 表示模块内部 Domain 已发生事实（过去式语义，如 `StrategyApproved / ReviewPackageSuperseded / ProductFactsInvalidated`），由 Domain 产生、不含 Infrastructure 类型、不负责发送、默认模块内部、不自动等于跨模块 Published Application Event。Application Event 表示一个 Application Transaction 已成功提交、允许其他能力响应（如 `StrategyApprovedEvent / MarketingBriefVersionCreatedEvent / SourceSetReindexedEvent`），必须在业务 Commit 成功后产生，可用于通知、非关键索引、Analytics、非关键 Projection、可重建缓存、外部集成、提交后非原子副作用。

### 11.9 Event Boundary and Choreography Prohibition

`Required Immediate Consistency → Command or Composite Use Case`；`Post-commit Non-critical Reaction → Application Event`。Human Review Approval、Current Truth 更新、Idempotency、同一业务 Commit 原子数据、必须立即返回的业务验证、LangGraph 核心确定性路由、Durable Resume Intent（除非可靠 Outbox）**不得**依赖普通最终一致 Event。核心 Workflow 不得隐藏为 Event 链（`Event A → Handler B → Event C → Handler D`）；具有明确 Stage / Human Interrupt / Resume / Retry / Cancellation / 状态查询 / Recovery / 可审计路由的流程必须由 LangGraph Orchestration 表达。`Workflow Orchestration ≠ Event Choreography`。

### 11.10 In-process Event Bus and Event Handler Rules

进程内 Event Dispatcher 仅用于非关键、可重试、可忽略或可重建、不要求跨进程保证的提交后动作；纯进程内 Event Bus 不得承担 API→Worker Durable Dispatch、Durable Resume、跨进程可靠工作、关键业务副作用、必须保证的通知。Event Handler 可接收已提交 Application Event、调用自身模块公开 Application Service、创建非关键 Projection、创建新的 Durable Work Intent、记录 Metrics/Analytics；不得直接访问其他模块 Repository、修改发布者模块内部状态、假设 Event 只执行一次、无限发布 Event、失败后伪造成功。Event Handler 必须具备 `Idempotent` 或 `Duplicate-consumption-safe` 语义。本 Decision 不选择 Event Bus、Outbox 或 Broker。

### 11.11 Module Dependency Graph and Circular Dependency Resolution

模块依赖必须形成 `Directed Acyclic Graph`；每个模块明确依赖哪些目标模块、依赖哪种 Public Contract、属于 Query/Event 或经批准的 Command Dependency、数据所有权、上下游关系。禁止 `A→B 且 B→A`，也禁止无 Import 循环但存在逻辑业务调用循环。发生循环依赖不得用延迟 Import / 函数内部 Import / 修改 `PYTHONPATH` / 把大量类型移入 Shared Kernel / 全局 Event Bus 隐藏调用 / 直接访问共享数据库掩盖；须通过：提升控制权到 Orchestration、只读需求改为 Public Query、需方定义 Port 经 Bootstrap 注入、提取真正稳定基础概念、重新划分业务模块、明确 Composite Use Case 解决。`shared_kernel/` 只保存真正稳定、无单一业务所有者的基础类型，不得为减少 Import 数量而扩大。

### 11.12 Public Error Contract and Versioning

模块对外错误必须是稳定的 Application-level Error，至少含 `error_code / category / message / retryability / relevant_reference`；不得暴露 Database Driver Error / ORM Exception / Provider SDK Error / Internal File Path / Database Table Name / Raw Stack Trace / Secret。调用者只能依据 Public Error Code、Category、Retryability 处理，不得解析异常字符串决定业务路由。Public Contract 必须区分 `Contract-compatible Change` 与 `Contract-breaking Change`；Breaking Change 必须更新 Contract Version、更新 Consumer、更新 Contract Test、在统一 Release 中协调，必要时修订 RFC 或 Architecture Baseline。

### 11.13 Contract and Architecture Test Requirements

Contract Tests：Schema Tests（字段/类型/必填/默认/序列化/Version）、Consumer Contract Tests（调用者只依赖公开字段与行为）、Error Contract Tests（Error Code 稳定、Retryability 明确、技术异常不泄漏）、Event Contract Tests（Commit 后产生、有 Event ID、Payload 可序列化、不含 Secret 或内部 Entity、重复消费安全）。Architecture Tests：`Cross-module imports must target modules.<target>.public`；禁止跨模块 Import `domain/application/infrastructure/application.skills`；模块依赖图无环；`shared_kernel` 不依赖业务模块；Public Contract 不 Import ORM / LangGraph；Public Result 不含可变 Domain Entity；Event Handler 不访问其他模块 Infrastructure；Orchestration 只 Import 模块 Public Facade；Production 不通过数据库表绕过 Public Contract；Event 不从失败或未提交事务正式发布。

### 11.14 Decision Boundary

已确认：唯一 `modules.<module>.public` 入口；Public Facade 不暴露 ORM/Repository/Session/Graph State/内部 Entity/Provider SDK；跨模块读取经 Public Query 返回不可变 Snapshot；状态修改由数据所有模块 Application Service 执行；模块间直接状态修改 Command 默认禁止；跨 Stage 协调由 Orchestration；跨模块原子操作仅经 Composite Application Use Case；共享数据库不作模块间隐式 API；Domain Event 模块内部、Application Event 表示已提交事实、非关键提交后副作用可用 Application Event；Human Review/Current Truth/Idempotency/核心路由不依赖普通 Event 最终一致；Event 链不替代 LangGraph Workflow；进程内 Event Bus 不承担 API→Worker 可靠调度；Event Handler 重复消费安全；模块依赖图为 DAG；Shared Kernel 最小化；Public Error 稳定结构化不泄漏技术异常；Breaking Change 显式版本化；Architecture Tests 强制跨模块 Import 指向 Public Facade 且依赖图无环；本 Decision 不选择 Event Bus / Outbox / Schema Library / Contract Test Framework；接受后仍不授权创建正式 Public Contract、Event Bus 或生产业务代码。

尚未确认：Python Formatter；Linter；Type Checker；Architecture Test 工具；Contract Test Framework；CI Quality Gate；Coverage Policy；Dependency Scan；Security Scan；Warning Policy；Foundation Skeleton 最低质量标准；Event Bus；Outbox；Schema Library；Production Public Contract Implementation。

本 Decision 不选择 Event Bus / Outbox / Schema Library / Contract Test Framework；RFC-001 已于 2026-07-30 ACCEPTED；**正式 Public Contract、Application Event Runtime、Event Bus、生产 Command/Query 实现、跨模块 Composite Use Case 创建保持 NOT AUTHORIZED**；Production Implementation 保持 `NOT AUTHORIZED`。

## 13. 已确认进程边界与同步/异步执行策略（RFC-001-DQ-07）

> 来源：RFC-001-DQ-07（ACCEPTED）。

### 12.1 Architecture, Release and Process Boundary

`Application Architecture ≠ Release Artifact ≠ Runtime Process`。系统保持：`One Modular Monolith Application + One Shared Backend Codebase + One Versioned Release Boundary + Multiple Role-specific Runtime Processes`。“一个主要后端部署单元”指一个统一逻辑后端应用 + 一个统一版本化发布边界 + 一个共享可部署制品 + 多个不同运行角色的进程，**不要求所有能力运行在同一个操作系统进程中**。

### 12.2 Runtime Process Roles

生产运行时至少区分 **API Process / Workflow Worker Process / CLI Process**。API 处理短生命周期请求（Create Task / Run、查询状态、获取 Review Package、提交 Human Review、请求 Cancel/Rerun/Resume、Auth、Request Validation、协议映射）；Worker 负责领取 Start/Resume/Rerun/Cancellation Intent、执行 LangGraph、调用 Stage Application Service、Interrupt/Resume、Retry Budget、Checkpoint、Runtime Trace、Recovery；CLI 为按需临时进程，仅经同一 Application Layer 调用授权管理 Use Case。三者**均不得直接访问业务 Repository / Current Truth**。

### 12.3 Unified Release Boundary

API 与 Worker 使用相同 Python Package、业务模块、Application Service、Domain Contract、Schema 与 Runtime Identifier，默认从**同一 Release Version** 构建部署，不是两个独立业务服务。至少记录 `Application / Graph / Workflow Definition / Job Payload / Schema Version`。新版 API 不得创建当前 Worker 无法理解的工作。滚动升级与 Graph Versioning 由 RFC-003、RFC-007 决定。

### 12.4 Long Workflow HTTP Boundary and Durable Dispatch

**Long Workflow inside HTTP Request = PROHIBITED。** 生产请求采用 `Submit → Persist Business/Runtime Intent → Create Durable Dispatch Intent → Return Task/Run Identity and Status`；API 返回成功表示工作已被**可靠接受**，不表示 Workflow 已完成。API 与 Worker 之间通过 **`WorkflowDispatchPort`**（`schedule_start / schedule_resume / schedule_rerun / schedule_cancel / schedule_recovery`）协作；API 返回“已接受”前 Durable Work Intent 必须已被可靠记录。**禁止 `asyncio.create_task(...)` 或 Web Framework 临时 Background Task 作为生产可靠任务机制。** 具体 Dispatch Backend（Job Table / Outbox / Redis Queue / Broker / Cloud Queue / Managed Runtime）由 RFC-002、RFC-003 决定。

### 12.5 Worker Recovery Requirements

Worker Crash 不能导致工作永久丢失。恢复语义结合 `Durable Dispatch + Runtime Record + Checkpoint + Application Idempotency`：未完成工作可重新领取；重复投递不产生重复 Domain Version；已成功提交的 Application Transaction 不重复提交；未提交 Skill Result 不视为 Current Truth；Resume 使用正确 `thread_id`；每次独立执行尝试具有明确 `run_id`；Stale Input/Checkpoint 在正式业务写入前被拒绝；Worker Failure 可进入 Retry/Pause/Recovery。Lease、Heartbeat、Ack、Visibility Timeout、Retry Policy 由 RFC-003 决定。

### 12.6 Human Review Submit and Resume

Human Review Submit 采用 **Synchronous Business Commit + Asynchronous Workflow Resume**。HTTP Request 同步完成 Review Version Validation、Stale Review Detection、Duplicate Submit Detection、Approved Strategy Business Commit、Audit、Idempotency、Durable Resume Intent 的可靠记录；**不等待**后续 Marketing Brief Skill / Xiaohongshu Adapter / LangGraph Node / 整个 Workflow 完成。返回可概念性表达为 `review_status = approved` + `workflow_status = resume_scheduled`。

### 12.7 Atomic Resume Coordination

`Approved Strategy Commit + Durable Resume Intent = Atomic or Reliably Reconciled`。不得出现：Approved Strategy 已提交但 Resume 永久丢失；Resume 已安排但事务失败；重复 Submit 产生多个有效 Resume；Worker Resume 读取到未提交或错误版本的业务状态。具体实现（Transactional Outbox / Database Job Table / Post-commit Reconciliation）由 RFC-002、RFC-003 决定。

### 12.8 Sync-first Application Core

区分 **Business-level Asynchrony**（HTTP 先返回、Workflow 后台继续——项目正式采用）与 **Python `async/await`**（代码执行模型，不等于后台任务架构）。正式采用：`Domain: Synchronous only；Application Core: Sync-first；Workflow Semantics: Asynchronous background execution；Concurrency: Bounded Worker Processes or Worker Slots；Infrastructure: Execution mode explicit`。Domain 禁止 `async` 业务接口 / Event Loop / 网络或数据库等待 / Async Framework 类型。Application 不得无规则同时提供 `execute()` / `execute_async()`。并发优先 Bounded Worker Concurrency，禁止无限创建并发 Task。Infrastructure Async-native Adapter 必须隔离在明确 Port 后、不污染 Domain、不让 Application 无规则混合 Sync/Async；禁止业务代码随意 `asyncio.run()` / 创建不可关闭的 Event Loop / 隐藏未受控线程。**Sync-first ≠ 永远禁止任何异步技术。**

### 12.9 API and Worker Bootstrap

API 与 Worker 共享核心 Application Factory，但使用窄化的不同 Runtime Factory：`build_core_resources() → build_application_services() → { build_api_runtime() | build_worker_runtime() }`。API Runtime 只装配 API 所需 Command/Query、Auth Adapter、HTTP Error Mapper、Correlation Context、Workflow Dispatch Port（不自动启动完整 Worker）；Worker Runtime 装配 Workflow Runtime、Dispatch Consumer、Checkpointer、Stage Application Services、Recovery Services、Worker Lifecycle（不自动启动 HTTP Server）。

### 12.10 Dispatch Payload and Frontend Boundary

API 与 Worker 之间只传递轻量 Runtime Reference（`task_id / run_id / thread_id / workflow_name / workflow_version / command_type / idempotency_key / requested_at / correlation_id`）；不得传递完整 Product Facts / Evidence Package / Prompt / Marketing Brief / ORM Entity / Database Session / Secret / Provider Client / Checkpoint 二进制 / 可变 Domain Object。Frontend 不依赖持续连接维持 Workflow，通过 Task / Run 状态查询获得进度（初始 Polling / Conditional Polling / Manual Refresh；SSE / WebSocket / Push 由 RFC-004 决定）。

### 12.11 Cancellation Boundary

取消采用 Durable Cancellation Intent：`Cancel Request → Application validates → Persist Durable Cancellation Intent → Worker observes → bounded work stops safely → status updated`。区分 `cancellation_requested / cancelling / cancelled / cancellation_failed`；HTTP Cancel 成功不表示 Worker 已即时停止。State Machine 由 RFC-003、RFC-004 决定。

### 12.12 Local and Test Runtime

允许 `Combined Development Runtime`（一个命令启动 API + Local Worker + Local Dispatch Adapter）与明确的 `Inline Execution Mode`，但仅限 `local / test / evaluation`：显式标记非生产、使用相同 Application Service、不绕过 Idempotency / Checkpoint、不改变业务事务规则、不成为生产默认路径。Production CLI Inline Workflow 仍然禁止。

### 12.13 Decision Boundary

已确认：Modular Monolith 不要求同进程；统一 Backend Application 与版本化 Release Boundary；API / Worker / CLI 三进程角色；长 Workflow 禁止在 HTTP 内执行完成、采用后台异步业务语义；API 在 Durable Work Intent 可靠记录后才返回接受；生产可靠任务禁止进程内临时 Background Task；Worker 只经 Application Service 提交业务状态、Crash 后可重新领取、重复投递经 Idempotency 防重复业务版本；Human Review Submit 同步提交业务、异步调度 Resume、Approved Commit 与 Resume Intent 原子或可靠协调；Domain 纯同步、Application Sync-first、并发优先有界 Worker；API/Worker 窄化 Bootstrap Factory；Dispatch Payload 只含 ID/版本/Runtime Reference；Cancellation 使用 Durable Intent；Local/Test 允许 Combined Runtime 与 Inline Runner。

尚未确认：Durable Dispatch 具体实现；Worker Framework；Queue / Broker；Job Lease / Heartbeat / Ack / Visibility Timeout；Checkpoint Backend；Resume State Machine；API Framework / HTTP Endpoint；Polling / SSE / WebSocket；Deployment Platform；Process Health Check；Worker Scaling Policy；Graph Version Migration；Production Runtime Implementation。

本 Decision 不选择 API Framework / Queue / Database Driver / Worker Framework / Deployment Platform；RFC-001 已于 2026-07-30 ACCEPTED；**API、Worker、Production Runtime 创建保持 NOT AUTHORIZED**；Production Implementation 保持 `NOT AUTHORIZED`。

## 14. 已确认 Skill 代码形态与架构关系（RFC-001-DQ-05）

> 来源：RFC-001-DQ-05（ACCEPTED）。

### 12.1 Skill Architectural Position

Skill 是业务模块 Application Layer 内具有明确执行契约、可独立运行和独立评估的**无状态业务能力组件**，落位 `modules/<module>/application/skills/<skill_slug>/`。Skill 不是独立 Package、不是 Domain Service、不是 Application Use Case 同义词，也不是 Entrypoint。

### 12.2 Prepare-Execute-Commit Model

Application Use Case 以 **Prepare–Execute–Commit** 协调 Skill 与业务事务：Prepare 装配 Skill 输入并开启业务事务；Execute 调用 Skill 产出 Candidate Result（业务候选，未落库）；Commit 由 Application Use Case 决定是否写入 Current Truth 并提交业务事务。Skill 只参与 Execute 阶段。

### 12.3 Skill Repository and Transaction Boundary

**Skill Direct Business Repository Access = PROHIBITED；Skill Business Transaction Ownership = NO。** Skill 不读/写 Current Truth、不持久化业务结果、不开启/提交业务事务、不更新 Evidence / Audit / Idempotency；所需数据由 Use Case 在 Prepare 阶段以输入契约注入。

### 12.4 Skill Provider Access Boundary

Skill 只能通过 Application 定义的 **ModelRuntimePort / RetrievalPort** 调用 Provider 能力；**Skill 直接 import 或实例化具体 Provider SDK = PROHIBITED**。Skill 不知道具体 Provider、模型名、连接串或凭证。

### 12.5 Skill LangGraph Boundary

调用链：`LangGraph Node → Stage Application Service → Skill Executor → Skill`。**LangGraph Node 直接调用 Skill = PROHIBITED。** Skill 与 LangGraph Node 不是同一概念、不一一对应；Skill 不感知 LangGraph、不读 Graph State、不写 Checkpoint。

### 12.6 Skill Independent Execution and Version

**Skill Independent Execution = REQUIRED**：Skill 必须能脱离 LangGraph 独立运行与独立评估。Skill 版本分 **Contract / Implementation / Prompt / Output Schema** 四个维度分别管理，可独立演进且须可追踪关联。

### 12.7 Skill Test Boundary

Skill 须支持 **Contract / Unit / Integration / Evaluation / Architecture** 五类测试。Architecture Test 强制：Skill 不直接访问 Repository、不 import Provider SDK、不依赖 LangGraph。

### 12.8 Decision Boundary

已确认：Skill 为 Application Layer 无状态业务能力组件；Prepare–Execute–Commit 协调；Skill 不直接访问 Repository、不拥有业务事务、不更新 Current Truth/Evidence/Audit；仅经 ModelRuntimePort/RetrievalPort 调用 Provider；经 Stage Application Service + Skill Executor 被 LangGraph 间接调用；可独立运行；版本四维度分管；五类测试。

尚未确认：具体模型 Provider、Retrieval Backend、Schema/Validation Library、Prompt Registry、Evaluation Framework、Skill Executor 具体实现机制。

本 Decision 不选择模型 Provider / Retrieval Backend / Schema Library / Prompt Registry / Evaluation Framework；RFC-001 已于 2026-07-30 ACCEPTED；Production Implementation 保持 `NOT AUTHORIZED`。

## 15. 已确认依赖注入、配置与应用装配（RFC-001-DQ-06）

> 来源：RFC-001-DQ-06（ACCEPTED）。

### 13.1 Dependency Injection Model

默认采用 **Constructor Injection + 显式 Factory Functions + 集中式 Composition Root（`bootstrap/`）**；MVP **不引入第三方 DI Framework**（无容器、无自动注入魔法）。**Global Service Locator = PROHIBITED。** 业务代码不做服务定位、不自行装配。

### 13.2 Composition Root

所有对象图构造与依赖装配只在 Composition Root 完成；它是唯一知道 Application Port 与 Infrastructure Implementation 绑定关系的代码。各 Entrypoint（API / Worker / CLI）不自行装配，统一由 Bootstrap 提供已装配对象图。

### 13.3 Configuration Loading and Layer Boundary

配置**仅由 Bootstrap 加载**，加载后立即**类型化 + 验证 + 不可变**，验证失败 **fail-fast**。业务代码不直接读取环境变量/配置文件。分层可见性：Domain 不接收任何配置；Application 只接收业务流程级配置（超时/重试/开关）；Infrastructure 只接收适配器级配置（连接串/Endpoint/凭证引用）；Bootstrap 加载、验证并分发全部配置。

### 13.4 Secret Boundary

**Secret 只注入需要它的 Infrastructure Adapter。** Secret 不得进入 Domain / Application Command / Application Result / Skill Input / Skill Result / Graph State / Checkpoint / Business Audit / Runtime Trace Payload / API Response / Git Repository / GitHub Issue or PR；不得打印或持久化完整 API Key / Database Password / Authorization Header / `.env` 内容 / Secret Manager 返回值。

### 13.5 Environment File Boundary

Repository **只提交 `.env.example`（占位值，无真实凭证）= REQUIRED**；`.env`（真实凭证）**提交 = PROHIBITED**，须被 `.gitignore` 排除。生产凭证来源（Secret Manager 等）留待后续 RFC。

### 13.6 Resource Lifetime Management

资源生命周期由 **Application Bootstrap 统一管理**，按 **Application / UseCase / WorkflowRun / SkillExecution** 四级作用域分级。**Global Mutable Runtime State = PROHIBITED；模块级可变单例持有连接/状态 = PROHIBITED。**

### 13.7 Test Replacement and Sync/Async Boundary

测试通过 Constructor / Factory 注入 **Fake / Stub** 替换真实 Adapter，无需修改业务代码或容器魔法。同步/异步执行策略与 API/Worker/CLI 进程边界**不在本 Decision 范围**，留待 **RFC-001-DQ-07**。

### 13.8 Decision Boundary

已确认：Constructor Injection + 显式 Factory + `bootstrap/` Composition Root；MVP 无第三方 DI Framework；无全局 Service Locator；配置仅 Bootstrap 加载、类型化/验证/不可变/fail-fast；Domain 无配置、Application 业务级、Infrastructure 适配器级；Secret 仅注入所需 Infrastructure Adapter 且不外泄；只提交 `.env.example`；资源生命周期 Bootstrap 统一分级管理；测试注入 Fake 替换。

尚未确认：第三方 DI Framework（后续是否引入）、Settings/Configuration Library、Secret Manager 与生产凭证来源、API Framework、Worker/Queue、同步/异步与进程边界（DQ-07）、Database 和 ORM、Architecture Test 工具、Deployment Platform、Production Skeleton。

本 Decision 不选择 DI Framework / Secret Manager / Settings Library / Deployment Platform；RFC-001 已于 2026-07-30 ACCEPTED；Production Implementation 保持 `NOT AUTHORIZED`。

## 16. 已确认分层职责、事务所有权与依赖规则（RFC-001-DQ-04）

> 来源：RFC-001-DQ-04（ACCEPTED）。

### 14.1 Core Architecture Model

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

### 14.2 Domain Layer

Domain 是纯业务核心，负责 Entity / Value Object / Aggregate / Domain Service / Business Rule / Domain Event / Version / Evidence / Review / Invalidation Rule。

Domain 仅可依赖 Python Standard Library、本模块 Domain 内部代码、严格受限的 `shared_kernel` 基础类型。不得依赖 Application / Infrastructure / Entrypoint / Orchestration / LangGraph / Web Framework / ORM / Database Driver / Repository Implementation / Model SDK / Vector DB SDK / Queue SDK / Checkpoint Backend / Observability Provider / Environment Variable。

Domain 必须可在无数据库、网络、LangGraph、真实模型条件下完成 Unit Test。

### 14.3 Application Layer

Application 负责 Command / Query / Application Service / Use Case Coordination / Repository / Provider / Unit of Work Port / Transaction Coordination / Idempotency / Current Truth / Evidence Link / Audit Coordination。

Application 不得依赖具体 Repository Implementation / ORM Model / Database Session / LangGraph State / Checkpoint Object / Web Request-Response / 具体 Model SDK / 具体 Retrieval SDK。

业务事务由 **Application Use Case** 拥有；Entrypoint 与 Graph Node 不开启/提交业务事务；Repository 不得自行 Commit；Unit of Work Implementation 仅提供技术能力，Commit/Rollback 由 Application Use Case 控制。

一次完整业务提交（Domain Version + Evidence Links + Current Truth Pointer + Stage State + Audit Record + Idempotency Record）必须在同一 Application Transaction 中 Commit Together 或 Rollback Together。

### 14.4 Port Ownership

Repository / Provider / Unit of Work / Clock / ID Generator / Event Publisher 等 Port 默认由 **Application Layer** 定义（推荐 `modules/<module>/application/ports.py`）。Application 声明能力，Infrastructure 实现，Bootstrap 注入。

仅真正属于纯业务抽象的 Policy 可定义在 Domain；数据库 Repository / LLM Provider / Retrieval Provider / Unit of Work / 外部 Event Publisher 不属于 Domain。

### 14.5 Infrastructure Layer

Infrastructure 负责 Repository Implementation / ORM Mapping / Database Integration / Unit of Work Implementation / Model / Retrieval / File Storage / Queue / Checkpoint / Observability Adapter / Third-party SDK。

Infrastructure 可依赖 Application Ports / Domain Types / Platform Infrastructure / 第三方 SDK；不得定义业务规则 / 改变 Domain Invariant / 在 Repository 中隐藏业务流程 / 自行更新 Current Truth / 自行决定 Review Approval / 自行执行 Downstream Invalidation / 在 ORM Hook 中执行业务逻辑 / 直接调用其他模块内部 Infrastructure / 绕过 Application Service 提交业务状态。

Repository Implementation 职责限于 Load / Persist / Query / Map，不得承担 Approve / Invalidate / Resume / Select Strategy / Generate Business Decision。

### 14.6 Orchestration Layer

LangGraph 位于独立 Orchestration / Workflow Adapter Layer，角色类似长运行 Application Client。Graph Node 通过 Module Public Application Contract 调用 Application Use Case，再使用 Domain + Ports。

Orchestration 可读取 Graph State、构造 Command、调用公开 Application Service、写回 Version ID / Stage Status、执行确定性路由、触发 `interrupt()`、协调 Retry/Resume/Cancellation、记录 Runtime Trace。

Orchestration 不得执行 Domain Rule / 拥有业务事务 / 直接调用业务 Repository / 直接使用 ORM Model / 直接更新 Current Truth / 直接写 Evidence Link / 直接执行 Review Approval / 直接执行 Idempotency Commit / 直接访问其他模块 Infrastructure / 在 Graph State 中长期保存完整业务对象。

**Graph Node Direct Business Repository Access = PROHIBITED。** 即使访问 Repository Interface 也会绕过 Application Validation、Transaction Boundary、Idempotency、Audit、Current Truth、Evidence Link、Application Error Mapping。Workflow Runtime 数据应通过 Workflow Runtime Service / Runtime Repository 读取。

### 14.7 Entrypoint Layer

Entrypoint 包括 API / Worker / CLI，仅负责将外部协议转换为 Application Command / Query。

Entrypoint 可解析输入、协议级 Schema Validation、Authentication / Authorization、构造 Command/Query、调用 Application Service、映射 Result / Error、添加 Correlation ID。

Entrypoint 不得直接调用 Domain Entity 完成业务流程 / 直接调用业务 Repository / 直接访问 ORM Model / 开启或提交业务事务 / 直接更新数据库 / 直接调用 LangGraph 内部 Node / 在 Route/Worker/CLI 中编写业务规则 / 绕过 Application Service 执行恢复。紧急恢复须通过明确的 Recovery Application Service 并产生 Audit Record。

### 14.8 Bootstrap and Composition Root

Bootstrap 是集中装配具体实现的 Composition Root，可了解 Application Port / Infrastructure Implementation / Orchestration Adapter / Entrypoint / Configuration / Application Lifecycle，负责加载 Settings、创建 Database Connection / Unit of Work / Repository / Provider Adapter / Application Service / Workflow / API / Worker / CLI Entrypoint、管理生命周期。

Bootstrap 不得执行业务 Use Case / 包含 Domain Rule / 成为全局 Service Locator / 允许模块任意读取全局 Container。

### 14.9 Dependency Injection and Cross-module Rules

默认采用 Constructor Injection + Explicit Factory Functions + Central Composition Root；不采用全局 Service Locator。

模块间同步调用必须通过目标模块公开 Application Contract（`public.py`），允许公开 Command / Query / Result / Public Error / Application Service Protocol / Published Application Event；禁止访问 infrastructure / ORM model / private repository / Direct SQL。当前不允许通过共享数据库任意 Join 其他模块内部表。

Domain Event 表示 Domain 已发生业务事实，Domain 可产生但不发布；Application Event 由 Application 在业务提交后发布，用于非关键副作用，当前不锁定 Message Broker，核心一致性流程优先同步调用。

错误转换方向：Infrastructure Error → Application Error → Protocol Error / Workflow Route；Graph Node 不得解析技术错误字符串决定业务路由。

### 14.10 Architecture Test Requirements

未来 Architecture Tests 至少验证：

- Domain 不 import application / infrastructure / orchestration / entrypoints / langgraph / web framework / orm；
- Application 不 import infrastructure implementations / entrypoints / langgraph / web framework / concrete database session；
- Infrastructure 可 import application ports / domain types / SDKs，不得定义业务规则 / use cases；
- Orchestration 不 import module infrastructure / ORM / database sessions / private implementation；
- Entrypoint 不 import repository implementations / ORM / private domain；
- Module A 不 import Module B infrastructure / private files；
- Production package 不 import spikes / prototypes。

具体 Architecture Test 工具尚未选择。

### 14.11 Responsibility Matrix

| Layer | Business Rules | Transaction Ownership | Defines Ports | Implements Ports | LangGraph | Protocol Handling |
|---|---|---|---|---|---|---|
| Domain | 是 | 否 | 仅纯业务 Policy | 否 | 否 | 否 |
| Application | 协调 | 是 | 是 | 否 | 否 | 否 |
| Infrastructure | 否 | 提供技术能力 | 否 | 是 | Adapter 可有 | 否 |
| Orchestration | 否 | 否 | 否 | Workflow Adapter | 是 | Workflow |
| Entrypoint | 否 | 否 | 否 | Protocol Adapter | 不直接 | 是 |
| Bootstrap | 否 | 否 | 知道接口 | 知道实现 | 装配 | 装配 |

### 14.12 Decision Boundary

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

RFC-001 已于 2026-07-30 ACCEPTED；Production Implementation 保持 `NOT AUTHORIZED`。

## 17. 已确认 Repository 与 Package 目录结构（RFC-001-DQ-03）

> 来源：RFC-001-DQ-03（ACCEPTED）。

### 14.1 Repository Model

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

### 14.2 Application Roots

| 应用 | 路径 | 说明 |
|---|---|---|
| Python Backend | `apps/backend/` | 生产源码根路径 `apps/backend/src/ai_ecommerce_agent/` |
| TypeScript Frontend | `apps/web/` | 本 Decision 不选择具体前端 Framework |
| Shared Contracts | `contracts/` | OpenAPI / JSON Schema / Error Codes 等正式契约 |

正式 Python Package 名：

```text
ai_ecommerce_agent
```

### 14.3 Backend Package Organization

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

### 14.4 Business Capability Modules

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

### 14.5 Platform Capabilities

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

### 14.6 Orchestration Boundary

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

### 14.7 Entrypoints

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

### 14.8 Bootstrap and Composition Root

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

### 14.9 Shared Kernel

允许保留严格受限的 `shared_kernel/`，只允许放置：

- 通用 Identifier 类型；
- Clock Protocol；
- 无业务语义的 Result；
- 通用 Error Base；
- 基础 Typing Utility。

不得放置具体业务规则、Repository Implementation、LangGraph State、ORM Base Model 或各业务模块为了方便而共享的任意代码。

### 14.10 Test Layout

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

### 14.11 Database Migrations

正式数据库 Migration 位于 `apps/backend/migrations/`，不放入可 Import 的生产 Python Package。具体 Migration Tool、Database 和 Schema Strategy 由 RFC-002 决定。

### 14.12 Configuration and Secret Boundary

目录层面允许未来使用：

```text
apps/backend/.env.example
apps/backend/src/ai_ecommerce_agent/bootstrap/settings.py
```

- `.env.example` 只能包含变量名称和非敏感示例；
- `.env`、Secret、Token 不得提交；
- Domain 和 Application 不直接读取环境变量；
- Configuration 由 Bootstrap 加载并注入。

### 14.13 Spike and Prototype Isolation

技术验证继续位于 Repository 根目录 `spikes/` 和 `prototypes/`。

生产 Package 禁止 `from spikes...` / `from prototypes...`。

允许关系：Spike Evidence → informs RFC and Production Tests → production implementation is rebuilt under accepted architecture。

禁止关系：Spike Source → rename or move → Production Source。

现有 Spike-001 继续作为 Architecture Evidence 保存。

### 14.14 Import Boundary

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

### 14.15 Cross-module Data Boundary

模块之间不得使用数据库表作为隐式 API。即使共享同一 Database Instance，也不得直接写入其他模块内部表、通过其他模块 ORM Model 修改数据、绕过 Application Contract、或直接调用其他模块 Repository Implementation。

跨模块读取和写入必须通过 Public Application Contract、Application Port、明确 Query Service 或用户后续确认的 Published Application Event。

### 14.16 Directory Creation Boundary

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

### 14.17 Decision Boundary

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

## 18. 已确认生产技术语言边界（RFC-001-DQ-02）

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

### 15.1 Backend Language

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

### 15.2 Frontend Language

正式 Web Frontend 使用 TypeScript。前端不属于 Python 后端 Package。

前后端通过版本化契约协作：

```text
OpenAPI / JSON Schema / Generated Client Types / Error Code Registry
```

具体 API Framework、Schema Generator 和前端 Framework 尚未确认。

### 15.3 LangGraph Binding Boundary

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

### 15.4 Framework Replacement Boundary

系统须允许未来替换 Workflow Engine（LangGraph / Temporal / Custom State Machine / Queue Worker 等），替换范围应限于：

```text
Orchestration Layer
Runtime Adapter
Checkpoint Adapter
Worker Integration
```

不应要求重写 Domain、Application Services、Business Validators、Repository Interfaces、Skill Contracts、Evidence Rules 或 Human Review Business Rules。

### 15.5 Future Polyglot Boundary

未来允许特定独立能力采用其他语言，但必须满足至少一种可验证触发条件：

- Python 存在可测量性能瓶颈；
- 关键 SDK 只在其他语言中可靠；
- 模块已有稳定远程接口；
- 模块需要独立扩缩容；
- 独立团队负责该模块；
- 安全或部署要求物理隔离；
- 该能力需要服务多个产品。

不得仅因个人语言偏好引入第二种后端语言。

### 15.6 Decision Boundary

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

## 19. 已确认应用架构（RFC-001-DQ-01）

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

### 16.1 Deployment Boundary

MVP 默认采用：

```text
One Primary Backend Application
```

初始不拆分为独立服务（Task / Workflow / Source / Retrieval / Human Review / Brief / Model Runtime Service）。

### 16.2 Repository Boundary

项目使用一个 Git Repository，但 Repository 内必须维持清晰的模块和依赖边界。

### 16.3 Module Boundary（概念划分）

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

### 16.4 Module Collaboration

模块之间必须通过明确边界协作：

- Application Service
- Domain Contract
- Repository Interface
- Provider Interface
- Command
- Query
- Published Application Event

不得任意访问其他模块内部类、绕过 Application Layer 修改数据、直接访问其他模块 Repository Implementation、以数据库表作为隐式 API、通过 LangGraph State 共享完整业务对象、或将 Prompt 作为唯一契约。

### 16.5 Dependency Direction

```text
Interface
↓
Application
↓
Domain

Infrastructure → implements → Repository and Provider Interfaces
```

Domain 不得依赖具体框架、数据库、ORM、LLM SDK、Vector DB、Message Queue、Observability Provider 或部署平台。

### 16.6 Data Ownership Boundary

允许 Modular Monolith 在 MVP 阶段共享一个数据库实例，但必须保持：

```text
Shared Database Instance ≠ Shared Data Ownership
```

必须区分 Business Domain / Workflow Runtime / Checkpoint / Source and Evidence / Retrieval Index / Audit / Observability Data。正式数据库、Schema、ORM 和事务方案由 RFC-002 决定。

### 16.7 Graph and Database Boundary

Graph Node 不得成为业务持久化规则的所有者。在 RFC-001 后续 DQ 接受前，Graph Node 不得临场定义 Domain Version 写入、Current Truth 更新、Evidence Link 事务、幂等、审计或失效逻辑。

### 16.8 Future Service Extraction

必须保留未来服务提取边界，但服务拆分只能由可验证的规模、组织、安全、性能或可靠性需求触发，不得仅因“微服务更先进”而拆分。

### 16.9 Decision Boundary

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

## 20. 未决技术决策（PENDING RFC）

| 领域 | 状态 | RFC |
|---|---|---|
| Repository and Application Architecture | ACCEPTED — 2026-07-30 | RFC-001 |
| Persistence and Transaction Architecture（生产 DB / ORM） | PENDING RFC | RFC-002 |
| LangGraph Runtime and Checkpoint Architecture（生产 Checkpointer） | PENDING RFC | RFC-003 |
| API and Human Review Protocol | PENDING RFC | RFC-004 |
| Source Processing and Retrieval Architecture | PENDING RFC | RFC-005 |
| LLM Runtime and Structured Output | PENDING RFC | RFC-006 |
| Observability and Runtime Operations | PENDING RFC | RFC-007 |

> **RFC-001 已于 2026-07-30 被用户正式接受（`ACCEPTED`）**——DQ-01~10 全部 ACCEPTED 且 Final Consistency Review 通过。DQ-10 已确认 Acceptance 与 Authorization 严格分离、Foundation Scope（Package + Quality + Architecture Tests + CI + Repository Security）、Foundation Issue Candidates（FND-001/002/003）与 Mandatory Stop Conditions。RFC-001 Acceptance 不自动授权实现；**Foundation Planning 现已开放（AUTHORIZED）**，但仅允许生成并审查 FND-001/002/003 Issue Candidates（不自动创建 Issue）；**FND-001、FND-002 与 FND-003 Issue Candidate 均已经形成，Foundation Candidate Planning 与 Final Review（PASS，2026-07-30，Decision Conflict = NONE）均已完成**——当前 Candidate 状态（以 [../foundation/foundation-issue-candidates.md](../foundation/foundation-issue-candidates.md)「授权边界（恒定成立）」为基准）：FND-001 = COMPLETED（PR #7 已合并，Merge Commit 5b75bcf，归档 PR #8），FND-002 = IN REVIEW（Issue #9 已创建，实施完成并提交 PR #10，Merge = USER DECISION REQUIRED），FND-003 = READY BLOCKED BY FND-002，Issue Creation / Implementation 均未授权；**Foundation Implementation 仍需单独明确授权（NOT AUTHORIZED；除 FND-001 / FND-002 单项授权外）**；Production CI、Production Skeleton、质量工具版本锁定、Secret Scanner、业务模块、API、Worker、CLI、Database、Production LangGraph 与 Production Runtime 创建仍 **NOT AUTHORIZED**。其余 RFC 仍为 `PROPOSED`。上述在生产实现前必须先经 RFC 提案 + 用户 Accepted Decision 收敛；**不得**临场选择。详见 [../decisions/dec-038-rfc-planning-and-dependency-order.md](../decisions/dec-038-rfc-planning-and-dependency-order.md) 与 [../specs/governance/rfc-planning-and-dependency-order.md](../specs/governance/rfc-planning-and-dependency-order.md)。

## 21. Final Status

```text
Spike Execution Status = COMPLETED
RFC-001 Status = ACCEPTED (2026-07-30)
Architecture Readiness Status = CONDITIONALLY READY
Development Status = CONDITIONALLY READY

Foundation Planning = AUTHORIZED（生成并审查 FND Issue Candidates）
Foundation Candidate Planning = COMPLETED（FND-001 / FND-002 / FND-003 均已形成）
Foundation Candidate Final Review = PASS（2026-07-30，Decision Conflict = NONE）
FND-001 Candidate Status = COMPLETED
FND-001 Issue Creation = COMPLETED（2026-07-30，Issue #6）
FND-001 Implementation = COMPLETED（2026-07-30，PR #7 已合并，Merge Commit 5b75bcf，归档 PR #8）
FND-002 Candidate Status = IN REVIEW
FND-002 Issue Creation = COMPLETED（2026-07-30，Issue #9）
FND-002 Implementation = COMPLETED（2026-07-30，PR #10）
FND-002 Status = IN REVIEW（PR #10 待用户审查；Merge = USER DECISION REQUIRED）
FND-003 Candidate Status = READY, BLOCKED BY FND-002
FND-003 Issue Creation = NOT AUTHORIZED
FND-003 Implementation = NOT AUTHORIZED
Foundation Implementation = NOT AUTHORIZED（除 FND-001 / FND-002 单项授权外）
Business Implementation = NOT AUTHORIZED
Production Implementation = NOT AUTHORIZED

Next Topic: FND-002 Pull Request Review and Merge Gate（FND-001 = COMPLETED；FND-002 已经用户单独明确授权「确认授权创建并实施 FND-002」，Issue #9 已创建，实施完成并提交 PR #10，待用户审查并决定 Merge；FND-002 Merge = USER DECISION REQUIRED，Coding Agent 不得自行 Merge，用户 Merge 前 FND-002 Status 不标记 COMPLETED；该授权不包括 FND-003 或任何业务实现；FND-002 完成并合并前不创建 FND-003 Issue、不开始 FND-003 实施）
```
