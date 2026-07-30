# Foundation Issue Candidates（Foundation 议题候选）

> **Status: FOUNDATION PLANNING — DEC-038 · RFC-001-DQ-10 Foundation Authorization Gate**
> **治理来源：** [../decisions/](../decisions/) DEC-034 / DEC-036 / DEC-038 · [../rfcs/rfc-register.md](../rfcs/rfc-register.md)
> **Parent Architecture Input：** RFC-001 Repository and Application Architecture（**Status = ACCEPTED**，2026-07-30）
> **纪律：** 本文件**只**记录 Foundation Issue Candidates（候选议题），供用户审查。**它不创建任何 GitHub Issue、不创建 Branch、不创建 Pull Request、不修改 Repository、不创建 `apps/backend/`、不安装 Dependency、不创建 Lockfile、不开始任何 Foundation Implementation。** 每个 Foundation Issue 在被创建或实施前，都必须获得用户**单独、明确**的授权。

---

## 授权边界（恒定成立）

```text
RFC-001 Status = ACCEPTED

Foundation Candidate Planning Status = COMPLETED
Foundation Candidate Final Review = PASS

FND-001 Candidate Status = READY FOR AUTHORIZATION
FND-002 Candidate Status = READY, BLOCKED BY FND-001
FND-003 Candidate Status = READY, BLOCKED BY FND-001 AND FND-002

FND-001 Issue Creation = AUTHORIZED（2026-07-30，用户明确授权「确认授权创建并实施 FND-001」，GitHub Issue #6 已创建）
FND-001 Implementation = IN REVIEW（2026-07-30，Branch foundation/001-backend-package-local-tooling；PR #7 已创建待用户审查；Merge = USER DECISION REQUIRED）

FND-002 Issue Creation = NOT AUTHORIZED
FND-002 Implementation = NOT AUTHORIZED

FND-003 Issue Creation = NOT AUTHORIZED
FND-003 Implementation = NOT AUTHORIZED

Foundation Planning Status = AUTHORIZED
Foundation Implementation Status = NOT AUTHORIZED（仅 FND-001 单项授权，不代表 Foundation 整体授权）
Business Implementation Status = NOT AUTHORIZED

Architecture Readiness = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
Production Implementation = NOT AUTHORIZED
```

**Acceptance 与 Authorization 严格分离：**
`接受 Candidate ≠ 授权创建 Issue ≠ 授权创建 Branch/PR ≠ 授权实施 Foundation ≠ 授权 Business/Production Implementation`。

接受 FND-001 / FND-002 / FND-003 Candidate 仅表示用户接受其**候选范围、边界、依赖与验收方向**；**不**授权创建 GitHub Issue、Branch、Pull Request、修改 Repository、安装工具、编写 Architecture Tests、创建 GitHub Actions、配置 Branch Protection、启用 Dependabot、安装 Secret Scanner 或执行 Foundation Implementation。

---

## Candidate 总览与依赖顺序

```text
FND-001  Backend Package and Local Tooling Foundation        (无前置 Foundation Issue)
FND-002  Architecture Enforcement and Test Foundation        (deps: FND-001)
FND-003  CI, Security and Repository Protection              (deps: FND-001 + FND-002)
```

执行顺序遵循依赖：`FND-001 → FND-002 → FND-003`，遵循 **One Issue → One Branch → One PR → Required Verification → User Merge Gate**。Foundation Candidate Final Review（PASS，2026-07-30）后，FND-001 已升级为 `READY FOR AUTHORIZATION`，FND-002 / FND-003 分别为 `READY, BLOCKED BY FND-001` / `READY, BLOCKED BY FND-001 AND FND-002`；任一 Candidate 在被单独授权创建 Issue 前，其 Issue Creation / Implementation 均保持 `NOT AUTHORIZED`。

| Candidate | 主题 | 依赖 | Candidate Status | Issue Creation | Implementation |
|---|---|---|---|---|---|
| **FND-001** | Backend Package and Local Tooling Foundation | RFC-001 = ACCEPTED（无前置 Foundation Issue） | **READY FOR AUTHORIZATION** | **AUTHORIZED（Issue #6）** | **IN REVIEW（PR #7）** |
| **FND-002** | Architecture Enforcement and Test Foundation | FND-001 | **READY, BLOCKED BY FND-001** | NOT AUTHORIZED | NOT AUTHORIZED |
| **FND-003** | CI, Security and Repository Protection | FND-001 + FND-002 | **READY, BLOCKED BY FND-001 AND FND-002** | NOT AUTHORIZED | NOT AUTHORIZED |

> **FND-001 执行状态（2026-07-30）：** 用户明确回复「确认授权创建并实施 FND-001」，授权 FND-001 Issue Creation + Implementation。已创建 [GitHub Issue #6](https://github.com/JettxonHo/ai-ecommerce-agent/issues/6) 与 Branch `foundation/001-backend-package-local-tooling`，实施完成并提交 [PR #7](https://github.com/JettxonHo/ai-ecommerce-agent/pull/7)（含完整验证证据），现待用户审查。**Merge 仍为 USER DECISION REQUIRED**；FND-002 / FND-003 与任何业务实现均未授权。

---

## FND-001：Backend Package and Local Tooling Foundation（READY FOR AUTHORIZATION）

**用户确认：** 「确认形成」——接受 FND-001 的候选范围、边界、依赖与验收方向。Final Review（2026-07-30）通过后，Candidate Status 由 `APPROVED FOR ISSUE PLANNING` 升级为 `READY FOR AUTHORIZATION`。

**Candidate Status：**

```text
FND-001 Candidate Status = READY FOR AUTHORIZATION
FND-001 Issue Creation = AUTHORIZED（2026-07-30，GitHub Issue #6）
FND-001 Implementation = IN REVIEW（2026-07-30，Branch foundation/001-backend-package-local-tooling；PR #7 已创建待用户审查；Merge = USER DECISION REQUIRED）
```

### 主要追踪

```text
RFC-001-DQ-02  Python 3.13 Backend
RFC-001-DQ-03  Repository and Package Layout
RFC-001-DQ-09  Quality Toolchain and Test Baseline
RFC-001-DQ-10  Foundation Scope and Authorization Gate
DEC-036        Controlled Git and GitHub Execution
DEC-038        RFC and Issue Governance
```

### Candidate Goal

建立最小、可安装、可构建、可测试并可运行本地质量检查的 Python 后端生产包基础，为后续 Architecture Enforcement、CI 和 Runtime 工作提供统一工程入口。

FND-001 只解决：

```text
生产 Python 代码放在哪里
+ 依赖如何锁定
+ 本地质量检查如何统一执行
+ 最小 Package 如何被构建、安装和测试
```

FND-001 **不**实现业务能力、生产运行时或外部接口。

### Proposed Issue Title

```text
FND-001: Establish backend package and local tooling foundation
```

**候选标签：**

```text
type: foundation
area: backend
status: planned
implementation: authorization-required
```

**候选依赖：** `RFC-001 = ACCEPTED`；FND-001 没有前置 Foundation Issue。

### In Scope（仅在未来获得独立实施授权后允许创建）

**Backend Project Root**

```text
apps/backend/
├── pyproject.toml
├── uv.lock
├── .python-version
├── README.md
├── src/
│   └── ai_ecommerce_agent/
│       ├── __init__.py
│       └── py.typed
└── tests/
    └── unit/
        └── test_package_import.py
```

只创建承担真实职责的目录和文件；不得为了匹配完整架构图创建空 Package。

**Python Version**

```text
Python >=3.13,<3.14
```

`.python-version` 指向实施时经过验证的 Python 3.13 补丁版本。不得降级到 Python 3.12；不得未经决策扩大到 Python 3.14；不得因工具兼容问题静默修改 Accepted Language Boundary。

**Python Package**

正式 Package：`ai_ecommerce_agent`；Source Layout：`apps/backend/src/ai_ecommerce_agent/`。初始只允许创建 `__init__.py` 与 `py.typed` 及构建 / Package Metadata 所必需的最小内容。

**Package Import 必须保持无副作用。** 执行 `import ai_ecommerce_agent` 不得：读取环境变量、加载 `.env`、创建数据库连接、初始化 Model Client、启动 LangGraph、建立网络连接、创建文件、输出敏感配置、自动导入尚未存在的业务模块。

**Dependency Management** — 正式采用 `uv`（项目环境 / Dependency Resolution / Development Dependencies / Lockfile / 本地命令执行）。允许提交 `apps/backend/uv.lock`。基础开发依赖可包括 Ruff、Pyright、pytest、coverage.py 或 pytest Coverage Integration；每个依赖必须具有明确用途。

**Ruff Foundation** — 在 `apps/backend/pyproject.toml` 建立 Ruff Formatter / Linter / Import Sorting / Python 3.13 Target / Source 和 Test Path / 必要精准排除；检查 `src/` 与 `tests/`。不得全局忽略全部规则、排除整个生产 Package、创建宽泛 `noqa`、为不存在的业务代码提前加例外、同时引入 Black/isort/Flake8 作为平行 Source of Truth。完整模块 Architecture Import Contract 留给 FND-002。

**Pyright Foundation** — Strict-first 类型检查基础，至少检查 `src/` 与 `tests/`，生产 Package 不得被排除。不得全局关闭核心诊断、用大量 `Any` 让 Skeleton 通过、对整个 Package 宽泛 Ignore、为尚未引入的第三方 SDK 提前加类型例外。

**pytest Foundation** — Test Discovery / Strict Marker / Warning-as-error / 最小 Unit Test / 无生产网络和生产资源的默认边界。最小真实测试 `tests/unit/test_package_import.py` 至少验证：Package 可从安装环境导入、使用正确的 `src` Layout、Package Import 无资源初始化副作用。完整 Marker 分类、Architecture Fixtures 与 Contract Test Foundation 留给 FND-002。

**Coverage Foundation** — 建立 Branch-aware Coverage Measurement；但按 RFC-001-DQ-09，`Global fail-under 80%` 只在首批可执行生产逻辑进入后正式作为 Merge Gate 启用。FND-001 不得通过空测试 / 单纯 Import Test / 大范围 Coverage Exclusion 伪造业务覆盖率。当前阶段记录：

```text
Coverage Measurement = AVAILABLE
Coverage Merge Threshold = DEFERRED
```

**Unified Local Commands** — 建立开发者和 Coding Agent 可统一使用的本地质量入口，至少覆盖概念能力 `format` / `format-check` / `lint` / `typecheck` / `test-unit` / `quality`。优先复用 `uv run` 和项目脚本；底层执行概念包括：

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

具体脚本形式在实施时决定，但不得额外引入没有必要的复杂 Task Runner。这些命令必须能被 FND-003 的 CI 原样或等价复用。

**Backend README** — `apps/backend/README.md` 至少说明：Python 版本要求、uv 环境初始化、Dependency Sync、Format Check、Lint、Type Check、Test、Package Build、当前 Foundation 范围、尚未实现的能力、Spike Source 不得复制到 Production Package。README 不得声称 API / Database / Worker / LangGraph Runtime / Model Runtime / Retrieval Runtime / Business Workflow 已存在。

### Out of Scope（FND-001 明确不包括）

- **Business Modules** — 不得创建 `product_intake / customer_insight / product_positioning / human_review / marketing_brief / xiaohongshu_adapter / source_evidence`；不得批量创建 `modules/ platform/ orchestration/ entrypoints/ bootstrap/ shared_kernel/` 空 Package。
- **Business Architecture Implementation** — 不得创建 Domain Entity / Aggregate / Application Service / Skill / Public Facade / Command / Query / Repository Port / Unit of Work / Composite Use Case。
- **Persistence** — 不得创建或选择 Database / ORM / Migration Tool / Schema / Repository Implementation / Unit of Work Implementation / Transaction Runtime / Current Truth Table / Idempotency Table（等待 RFC-002）。
- **Workflow Runtime** — 不得创建或引入 LangGraph / Production Graph / Graph State / Graph Node / Checkpointer / Worker / Durable Dispatch / Queue / Resume Runtime / Recovery Runtime（等待 RFC-003）。
- **Entrypoints** — 不得创建 API / HTTP Server / Worker Entrypoint / Production CLI / Human Review Endpoint / Authentication（API 等待 RFC-004）。
- **Platform Runtime** — 不得创建 Model / Retrieval / Observability / Identity / Messaging Runtime 或 Secret Provider（等待对应后续 RFC）。
- **Architecture Enforcement** — 不含完整 Import Linter Contract / Layer Architecture Contract / Public Facade Enforcement / Module DAG Enforcement / Negative Architecture Fixtures / Semantic Architecture Tests（属 FND-002）。
- **Repository Automation** — 不含 GitHub Actions / Branch Protection / Dependabot / Secret Scanner / PR Template / Issue Template / Required Status Checks（属 FND-003）。

### Acceptance Criteria（未来完成时必须满足）

1. `apps/backend/` 是有效独立 Python Project；
2. Python Constraint 为 `>=3.13,<3.14`；
3. 使用 `src/ai_ecommerce_agent/` Layout；
4. Package 名为 `ai_ecommerce_agent`；
5. Package 包含 `py.typed`；
6. 干净环境能够根据 Lockfile 安装；
7. `uv sync --locked` 成功；
8. Package Build 成功；
9. Package Installation 成功；
10. Package Import Test 成功；
11. Package Import 无网络和资源初始化副作用；
12. Ruff Format Check 成功；
13. Ruff Lint 成功；
14. Pyright 成功；
15. pytest 成功；
16. 未注册 pytest Marker 会失败；
17. Warning 默认导致 Test Failure；
18. Branch-aware Coverage Measurement 可运行；
19. 80% Merge Threshold 没有被虚假启用；
20. Backend README 命令可执行；
21. 本地质量命令可被未来 CI 复用；
22. 没有业务模块；
23. 没有 API；
24. 没有 Database；
25. 没有 Worker；
26. 没有 LangGraph；
27. 没有从 Spike 复制的 Production Source；
28. 没有无用途 Dependency；
29. 所有文件均属于 FND-001 Scope；
30. PR 明确记录仍未授权的能力。

### Required Verification（未来 FND-001 PR 至少运行）

```text
uv sync --locked
Ruff format check
Ruff lint
Pyright
pytest
Coverage measurement
Package build
Package installation
Package import validation
```

还必须验证：
- **Clean Environment Installation** — 从干净环境按照 `pyproject.toml` 和 `uv.lock` 完成安装。
- **Source Layout** — 测试确认 Package 不是因为 Repository Root 偶然位于 `PYTHONPATH` 而导入成功。
- **Build Artifact** — 构建产物只包含预期 Python Package 和 Metadata。
- **Import Side Effects** — 导入 Package 时不得读取 `.env`、建立网络连接、初始化数据库、创建文件、打印 Secret、启动 Runtime。

### Required PR Evidence（未来实施 PR 必须输出）

最终文件树；Python / uv / Ruff / Pyright / pytest / Coverage 工具版本；Lockfile 变更；安装命令和结果；Format Check / Lint / Type Check / Test / Coverage Measurement 结果；Package Build / Installation 结果；Import Side-effect 检查结果；新增 Dependency 及用途；Out-of-scope 检查；Mandatory Stop Condition 状态。**不得只输出"所有检查通过"。**

### Mandatory Stop Conditions（实施时遇以下情况必须停止）

1. Python 3.13 与已接受工具链出现无法解决的兼容问题；
2. 需要改用 Python 3.12；
3. 需要扩大至 Python 3.14；
4. 需要选择 API Framework；
5. 需要选择 Database、ORM 或 Migration Tool；
6. 需要引入 LangGraph；
7. 需要创建业务模块；
8. 需要创建 Production Bootstrap；
9. 需要创建 Worker、Queue 或 Durable Dispatch；
10. 需要复制 Spike Source；
11. 需要降低 RFC-001-DQ-09 的质量原则；
12. 需要全局关闭 Pyright 或 Ruff；
13. 需要批量创建空 Architecture Directory；
14. 当前 Repository Root Layout 与 RFC-001 冲突；
15. 发现真实 Secret；
16. Issue Scope 必须扩大才能继续；
17. 发现需要修改 Accepted RFC-001。

出现以上情况必须提交 `Mandatory Stop Report` 或 `Decision Conflict Report`，**不得静默扩大 Scope 或自行改变架构**。

### Candidate Git and GitHub Plan（候选，未授权执行）

```text
候选 Issue   : FND-001: Establish backend package and local tooling foundation
候选 Branch  : foundation/001-backend-package-local-tooling
候选 PR      : foundation: establish backend package and local tooling
```

候选阶段性 Commit：

```text
build: initialize Python backend package
chore: configure local quality toolchain
test: add backend package foundation checks
docs: document backend development commands
```

实际 Commit 必须依据真实变更组织，不得机械创建无意义 Commit。

---

## FND-002：Architecture Enforcement and Test Foundation（READY, BLOCKED BY FND-001）

**用户确认：** 「确认」——接受 FND-002 的候选范围、依赖、验收标准和禁止边界。Final Review（2026-07-30）通过后，Candidate Status 由 `APPROVED FOR ISSUE PLANNING` 升级为 `READY, BLOCKED BY FND-001`。

**Candidate Status：**

```text
FND-002 Candidate Status = READY, BLOCKED BY FND-001
FND-002 Issue Creation = NOT AUTHORIZED
FND-002 Implementation = NOT AUTHORIZED
```

**Parent Architecture Input：**

```text
RFC-001: Repository and Application Architecture — Status = ACCEPTED
```

**Dependency：**

```text
FND-001 = MERGED
```

FND-002 在 FND-001 完成并合并前**不得实施**。

### 主要追踪

```text
RFC-001-DQ-03  Repository and Package Layout
RFC-001-DQ-04  Layer Responsibilities and Dependency Direction
RFC-001-DQ-05  Skill Architecture
RFC-001-DQ-06  Configuration and Bootstrap Boundary
RFC-001-DQ-08  Public Facade and Module Dependency DAG
RFC-001-DQ-09  Quality Toolchain and Architecture Enforcement
RFC-001-DQ-10  Foundation Scope and Authorization Gate
DEC-036        Controlled Git and GitHub Execution
DEC-038        RFC and Issue Governance
```

### Candidate Goal

将 RFC-001 已接受的 Layer、Module、Public Facade、Skill、Configuration、Orchestration 和 Spike Isolation 规则转化为**可自动执行、可产生清晰违规报告并可由未来 CI 阻断**的 Architecture Contracts 和测试。

正式治理链路：

```text
Accepted Architecture Rule
↓
Executable Architecture Contract
↓
Positive and Negative Fixtures
↓
Automated Verification
↓
Merge-blocking Check in future FND-003
```

FND-002 只建立：Architecture Enforcement、Test Classification、Positive / Negative Architecture Fixtures、本地可执行测试命令、架构测试文档。

FND-002 **不**实现：真实业务模块、生产数据库、API、Worker、LangGraph Runtime、CI、Branch Protection、后续 RFC 范围内的生产能力。

### Proposed Issue Information

**Candidate Issue Title：**

```text
FND-002: Establish architecture enforcement and test foundation
```

**Candidate Labels：**

```text
type: foundation
area: architecture
area: testing
status: planned
implementation: authorization-required
```

**Candidate Branch：**

```text
foundation/002-architecture-test-foundation
```

**Candidate Pull Request：**

```text
foundation: enforce architecture and test boundaries
```

### In Scope（仅在未来获得独立实施授权后允许创建）

**Architecture Test Structure** — 未来获得独立实施授权后，按真实职责创建：

```text
apps/backend/tests/
├── architecture/
│   ├── fixtures/
│   ├── helpers/
│   └── test_*.py
├── contract/
├── integration/
├── e2e/
└── evaluation/
```

不得为了展示完整目录而创建大量空文件。只创建已有真实测试 / Marker 配置 / Fixture / 文档职责的目录和文件。

**Import Linter** — 正式引入 `Import Linter`，检查 Python Import Graph 中可静态表达的架构规则。配置集中在 `apps/backend/pyproject.toml`（或 Import Linter 明确要求的单一配置入口）；不得让不同业务模块维护相互冲突的 Import Contract。具体工具版本在实施时通过 FND-001 的 `uv.lock` 锁定。

**Initial Import Contracts** — FND-002 至少建立以下 10 条 Contract：

1. **Production and Spike Isolation** — 生产源码 `apps/backend/src/ai_ecommerce_agent/` 不得 Import `spikes/` / `prototypes/`；测试代码读取 Spike 材料必须经明确 Test-only Boundary，且不得让 Production Package 间接依赖 Spike。
2. **Domain Independence** — 任何 `modules.<module>.domain` 不得依赖 `application / infrastructure / orchestration / entrypoints / bootstrap / platform / langgraph / ORM / web framework / provider SDK`；只允许 Python Standard Library、同模块 Domain、被批准的最小 Shared Kernel、纯业务 Value Object 和 Policy。
3. **Application Independence** — 任何 `modules.<module>.application` 可依赖同模块 Domain、自身定义的 Port、最小 Shared Kernel、公开且与 Infrastructure 无关的 Contract；不得依赖 Infrastructure Implementation / Bootstrap / Entrypoint / LangGraph / Web Framework / Concrete ORM Model / Provider SDK / Database Session。Application 可定义 Port 但不能 Import Port 的技术实现。
4. **Infrastructure Direction** — Infrastructure 可实现 Application Port 并依赖必要技术 SDK；核心层不得反向依赖 Infrastructure。必须自动阻止 `Application → Infrastructure Implementation` 与 `Domain → Infrastructure`。
5. **Public Facade-only Cross-module Import** — 跨业务模块 Import 只能指向 `modules.<target_module>.public`；禁止 `modules.<target>.domain / .application / .infrastructure / .application.skills`。
6. **Orchestration Boundary** — `orchestration/` 可依赖 `modules.<module>.public` / `platform.workflow_runtime` public contract / `shared_kernel`；不得依赖 Module Infrastructure / Private Application Implementation / ORM Model / Database Session / Repository Implementation / Provider SDK。
7. **Entrypoint Boundary** — `entrypoints/` 可依赖公开 Application Contract 和窄化 Runtime；不得直接依赖 Business Repository Implementation / ORM Model / Database Session / Internal Domain Entity / Skill Implementation / Provider Client。Entrypoint 不得绕过 Application Layer。
8. **Bootstrap Direction** — `bootstrap/` 可了解并装配 Application Port / Infrastructure Adapter / Platform Resource / Entrypoint Runtime / Workflow Runtime / Settings / Resource Lifecycle；但 Domain / Application / Skill / Module Public Contract 不得 Import Bootstrap（`Core Business Code -X→ Bootstrap`）。
9. **Shared Kernel Independence** — `shared_kernel/` 不得依赖任何业务模块；方向为 `Business Module → Shared Kernel`；禁止 `Shared Kernel → Business Module`；不得通过 Shared Kernel 掩盖模块循环依赖。
10. **Module Dependency DAG** — 业务模块依赖必须形成 Directed Acyclic Graph；任何 `Module A → Module B → Module A` 必须失败；应形成模块级依赖图并识别通过 Public Facade 建立的业务模块循环（不只识别 Python 文件级 Import Cycle）。

**Architecture Fixtures** — 真实业务模块尚未创建时，不得创建虚假 Production Module。允许在 `apps/backend/tests/architecture/fixtures/` 建立最小 Test-only Fixture（如 `valid_layered_package / invalid_domain_imports_infrastructure / invalid_application_imports_adapter / invalid_cross_module_private_import / invalid_module_dependency_cycle / invalid_production_imports_spike / invalid_shared_kernel_dependency / invalid_orchestration_imports_infrastructure / invalid_entrypoint_imports_repository / invalid_core_reads_environment / invalid_public_contract_exposes_technical_type / invalid_skill_boundary`）。Fixture 必须：只属于测试代码、不位于 Production Package、不被 Production Import、不代表已创建真实业务模块、只包含触发目标规则所需的最小代码。

**Positive Architecture Tests** — 每个关键 Contract 至少具有合法 Fixture（如 `valid_layered_package / valid_public_facade_dependency / valid_orchestration_dependency / valid_shared_kernel_dependency`），防止 Architecture Contract 过严错误阻止合法架构。

**Negative Architecture Tests** — 每个重要硬规则至少一个故意违规 Fixture。正式验证链路：`Load Invalid Fixture → Run Relevant Architecture Checker → Checker Reports Expected Rule Violation → Test Passes`。Negative Test 必须验证 Checker 确实运行、Fixture 被正确发现、失败由目标架构违规引起、输出包含预期 Source 和 Target、不是因语法/路径/配置错误假通过。不得通过"Checker 没有检查 Fixture"获得虚假成功。

**Semantic Architecture Tests** — Import Linter 只能验证 Import Graph，FND-002 同时建立自定义 pytest Architecture Tests，首批至少验证：
- **Public Contract Technical Leakage** — Public Contract 不得暴露 ORM Base / ORM Entity / Database Session / Repository Implementation / LangGraph State / Provider SDK Type / Secret Type / Infrastructure Exception（用 Test-only Fixture 证明检查机制能识别）。
- **Environment and Configuration Boundary** — `domain/ / application/ / application/skills/` 不得直接使用 `os.environ / os.getenv(...) / dotenv`；Production Core 不得加载 `.env`。
- **Skill Boundary** — Test-only Skill Fixture 证明能识别 Skill Import LangGraph / Repository Implementation / ORM、Skill 读取环境变量、Skill Context 持有 Database Session、Skill Import Spike。不得创建真实生产 Skill。
- **Orchestration and Graph Node Boundary** — 通过 Test-only Fixture 验证 Graph Node / Orchestration Component 不得 Import ORM / 业务 Repository、持有 Database Session、直接访问 Infrastructure Adapter、绕过模块 Public Facade。FND-002 **不引入 LangGraph**；Fixture 可用普通 Python 模块模拟目录和依赖结构。

**pytest Test Classification** — 正式注册 `unit / integration / contract / architecture / e2e / evaluation / live / slow`；pytest 必须启用严格 Marker，未知 Marker 必须导致错误（如 `@pytest.mark.intergration` 不得被静默接受）。

**Marker Semantics** — `unit`（单一规则/小范围 Use Case、无真实外部资源、无网络、Fake+固定时间）；`integration`（真实技术 Adapter/隔离资源、未来数据库/Checkpointer、不连 Production）；`contract`（Public Contract / Port / Adapter Compliance / Schema / Event / Dispatch Payload）；`architecture`（Layer Direction / Module Boundary / Public Facade / DAG / Configuration Boundary / Spike Isolation）；`e2e`（完整业务或 Runtime 流程）；`evaluation`（AI 输出质量评估、固定 Fixture 或评分器）；`live`（真实外部网络/Provider、有成本或非确定性）；`slow`（超出普通快速测试预算、不代表可永久跳过）。

**Default Test Selection** — 建立本地统一命令能力 `test-unit / test-contract / test-architecture / test-fast / test-all-local`；建议 `test-fast = unit + contract + architecture，excluding live and slow`。普通默认测试不得访问真实外部网络。

**Network Access Protection** — 建立 `Unit / Contract / Architecture Tests -X→ External Network` 默认保护：未声明的网络访问立即失败、`live` 测试必须显式运行、Architecture Fixture 不访问网络、Package Import Test 不访问网络、默认测试不调用真实 Model / Embedding / 网页 / 生产服务。具体 Network Blocking Library 为有界工程选择，新增依赖必须说明用途；若无法在不扩大 Scope 下实现，必须提交 Mandatory Stop Report，不得声称已完成网络阻断。

**Test Fixture Rules** — 所有 Fixture 必须：可重复运行、无真实 Secret、无生产资源、无不可控网络、不依赖执行顺序、使用临时目录、测试结束后清理、不含随机时间和不稳定数据、保持最小化。不得复制完整生产模块设计到 Fixture。

**Architecture Helpers** — 允许创建 `apps/backend/tests/architecture/helpers/`（Package Discovery / AST Scanning / Import Graph Loading / Module Dependency Graph Construction / Fixture Execution / Violation Formatting）。Helper 必须只属于 Test Code、不被 Production Import、接受 Ruff 和 Pyright 检查、输出可定位结果、不隐藏 Import Linter 或 AST Checker 自身错误。不得建立无法解释结果的巨大自定义架构框架。

**Violation Reporting** — Architecture Check 失败必须包含可定位信息，至少 `Rule / Source / Illegal Target / Expected Boundary`（示例：`Rule: Cross-module imports must use public facade` / `Source: modules.marketing_brief.application.service` / `Illegal Target: modules.human_review.domain.entities` / `Expected Boundary: modules.human_review.public`）。不得只输出 `Architecture test failed`。

**Tool Responsibility Boundary** —
- **Ruff**：Formatting、Import Sorting、普通静态代码质量、常见 Python 错误。
- **Pyright**：类型安全、Public Contract 类型、未知类型扩散、测试 Helper 类型。
- **Import Linter**：Import Graph、Layer Direction、Module Dependency、Public Facade Import Boundary、DAG。
- **Custom Architecture Tests**：AST 和语义规则、Environment Access、Public Contract 技术类型泄漏、特殊目录约束、Fixture-based Negative Verification。

不得让多个工具重复实现同一检查并产生冲突 Source of Truth。

**No Real Business Contracts** — FND-002 不创建真实生产 `modules/product_intake/public.py` 等，也不创建真实 Command / Query / Snapshot / Public Error / Application Event。FND-002 只证明：未来真实 Public Facade 出现后，越界 Import 和技术类型泄漏能够被自动识别。

**Documentation** — 允许创建 `apps/backend/tests/architecture/README.md`，至少说明 Architecture Test 目的、Import Linter 与自定义测试职责、Fixture 组织方式、如何增加 Architecture Contract、如何运行、如何阅读失败报告、如何申请精准例外、禁止删除规则或宽泛 Ignore、与 RFC-001 的追踪关系。可更新 Backend README 加入测试命令。不得重复复制完整 RFC-001 内容，应引用正式 RFC 文档。

### Out of Scope（FND-002 明确不包括）

- **Production Business Code** — 业务模块、Domain Entity、Aggregate、Application Service、Skill、Public Command、Public Query、Composite Use Case。
- **Persistence** — Database、ORM、Migration、Repository、Unit of Work、Outbox、Current Truth Schema（等待 RFC-002）。
- **Workflow Runtime** — LangGraph、Production Graph、Node、State、Worker、Queue、Checkpointer、Durable Dispatch（等待 RFC-003）。
- **API** — API Framework、Route、Request / Response、Human Review Protocol、Authentication（等待 RFC-004）。
- **CI and Repository Protection** — GitHub Actions、Required Status Checks、Branch Protection、Dependabot、Secret Scanner、PR / Issue Template（属 FND-003）。
- **Coverage Merge Gate** — 不正式启用生产代码 80% Coverage Merge Threshold。
- **Frontend** — 不建立任何 TypeScript 或 Frontend 测试工具链。

### Acceptance Criteria（未来完成时必须满足）

1. Import Linter 已通过 Lockfile 引入；
2. Architecture Tests 具有统一运行命令；
3. pytest Marker 全部注册；
4. 未知 Marker 会失败；
5. `architecture` Marker 可以单独运行；
6. `test-fast` 排除 `live` 和 `slow`；
7. Production Import Spike 违规会被识别；
8. Domain Import Infrastructure 违规会被识别；
9. Application Import Infrastructure Implementation 违规会被识别；
10. 跨模块 Private Import 违规会被识别；
11. 合法 Public Facade Import 能够通过；
12. Module Dependency Cycle 会被识别；
13. Shared Kernel Import Business Module 会被识别；
14. Orchestration Import Module Infrastructure 会被识别；
15. Entrypoint Import Repository Implementation 会被识别；
16. Core Layer 读取环境变量会被识别；
17. Public Contract 暴露技术类型会被识别；
18. Skill Boundary 违规会被识别；
19. 每个关键 Contract 至少具有正向和负向验证；
20. Negative Test 不会因 Fixture 路径或语法错误假通过；
21. 违规报告包含 Rule、Source、Target；
22. Unit、Contract、Architecture Test 默认无网络；
23. FND-001 的全部质量检查仍然通过；
24. 没有创建真实业务模块；
25. 没有引入 LangGraph；
26. 没有引入 ORM 或 API Framework；
27. 没有创建生产 Runtime；
28. 文档说明如何运行和维护 Architecture Tests；
29. 本地命令可供未来 FND-003 CI 直接复用；
30. 没有修改 Accepted RFC 或 DEC。

### Required Verification（未来 FND-002 PR 至少运行）

```text
uv sync --locked
ruff format --check
ruff check
pyright
pytest -m unit
pytest -m contract
pytest -m architecture
pytest excluding live and slow
import-linter check
package build
```

还必须验证：
- **Positive Fixtures** — 合法 Fixture 全部通过。
- **Negative Fixtures** — 每个违规 Fixture：被目标 Contract 拒绝、输出预期 Source 和 Target、不因语法或配置问题失败。
- **Marker Strictness** — 通过测试专用 Fixture 或独立验证，证明未知 Marker 会失败；不得把永久失败测试留在正式测试集合中。
- **Network Blocking** — 故意在非 `live` Fixture 中访问网络时，测试必须失败。
- **Regression** — FND-001 的 Package Import / Package Build / Ruff / Pyright / pytest / Coverage Measurement 继续通过。

### Required PR Evidence（未来实施 PR 必须输出）

最终 Architecture Test 文件树；Import Linter 版本；pytest Marker 列表；Import Contract 清单；Positive Fixture 清单；Negative Fixture 清单；每条 Contract 的验证结果；Architecture Test 命令与结果；Import Linter 命令与结果；Ruff / Pyright / pytest 分类结果；Network Blocking 结果；Marker Strictness 结果；Package Build 结果；新增依赖及用途；测试执行时间；Out-of-scope 审查；Mandatory Stop Condition 状态。**不得只输出"Architecture Tests passed"。**

### Mandatory Stop Conditions（实施时遇以下情况必须停止）

1. 需要创建真实业务模块才能验证规则；
2. 需要引入 LangGraph；
3. 需要引入 ORM 或数据库；
4. 需要创建 API、Worker 或 Production CLI；
5. 需要创建 Production Bootstrap；
6. Import Linter 无法表达某条核心规则，且不存在合理自定义测试方案；
7. 需要修改 RFC-001 的 Layer 或 Dependency Direction；
8. 需要允许跨模块 Private Import；
9. 需要扩大 Shared Kernel；
10. 需要关闭或弱化 Pyright、Ruff；
11. 需要将 Architecture Rule 降级为文档建议；
12. 需要依赖真实网络或生产资源；
13. 需要使用真实 Secret；
14. FND-001 结构与 RFC-001 存在冲突；
15. 需要建立 GitHub Actions 或 Branch Protection；
16. Scope 必须扩展到 FND-003；
17. 已接受硬规则无法稳定检测；
18. 发现真实 Credential；
19. 需要修改 Accepted RFC 或 DEC；
20. 实际修改范围超出 FND-002。

出现这些情况必须提交 `Mandatory Stop Report` 或 `Decision Conflict Report`，**不得**通过删除 Contract、添加宽泛 Ignore、跳过 Negative Fixture、关闭检查、伪造测试继续实施。

### Candidate Commit Plan（候选，未授权执行）

```text
test: configure architecture test classification
chore: add import architecture contracts
test: add positive and negative architecture fixtures
docs: document architecture enforcement workflow
```

实际 Commit 必须按真实修改组织，不得机械拆分。

---

## FND-003：CI, Security and Repository Protection（READY, BLOCKED BY FND-001 AND FND-002）

**用户确认：** 「确认」——接受 FND-003 的候选范围、依赖、验收标准、安全规则和禁止边界。Final Review（2026-07-30）通过后，Candidate Status 由 `APPROVED FOR ISSUE PLANNING` 升级为 `READY, BLOCKED BY FND-001 AND FND-002`。

**Candidate Status：**

```text
FND-003 Candidate Status = READY, BLOCKED BY FND-001 AND FND-002
FND-003 Issue Creation = NOT AUTHORIZED
FND-003 Implementation = NOT AUTHORIZED
```

**Parent Architecture Input：**

```text
RFC-001: Repository and Application Architecture — Status = ACCEPTED
```

**Dependencies：**

```text
FND-001 = MERGED
FND-002 = MERGED
```

FND-003 在 FND-001 和 FND-002 完成并合并前**不得实施**。

### 主要追踪

```text
RFC-001-DQ-06  Bootstrap and Configuration Boundary
RFC-001-DQ-08  Module Public Contract and DAG
RFC-001-DQ-09  Quality Toolchain, Architecture Enforcement and CI Gates
RFC-001-DQ-10  Foundation Scope and Authorization Gate
DEC-036        Controlled Git and GitHub Execution
DEC-038        RFC and Issue Governance
```

### Candidate Goal

将 FND-001 和 FND-002 已建立的本地质量、测试和 Architecture Enforcement 命令接入 GitHub，形成**可审查、可复现并能够阻止违规代码进入 `main`** 的 CI、安全与 Repository Protection 基础。

正式治理链路：

```text
Local Quality Command
↓
GitHub Actions
↓
Stable Required Status Check
↓
Branch Protection
↓
User Final Merge Gate
```

FND-003 只建立：GitHub Actions、Stable Required Checks、Dependency Audit、Secret Detection、Dependabot、PR Template、Issue Templates、`main` Branch Protection、Repository Governance Documentation。

FND-003 **不**建立：Production Deployment、Business Modules、Database、API、Worker、LangGraph Runtime、Model Runtime、Retrieval Runtime、Live AI Evaluation、Production Secret。

### Proposed Issue Information

**Candidate Issue Title：**

```text
FND-003: Establish CI, security and repository protection
```

**Candidate Labels：**

```text
type: foundation
area: ci
area: security
area: repository
status: planned
implementation: authorization-required
```

**Candidate Branch：**

```text
foundation/003-ci-security-repository-protection
```

**Candidate Pull Request：**

```text
foundation: establish CI and repository protection
```

### Core CI Principle

正式采用：`Local Configuration = CI Configuration`。CI 必须复用 Repository 中已经存在并经过 FND-001、FND-002 验证的 Ruff / Pyright / pytest / Import Linter Contracts / Architecture Tests / Lockfile / Unified Local Commands。**禁止**在 GitHub Actions 中建立与本地不同的第二套质量规则。

### In Scope（仅在未来获得独立实施授权后允许创建）

```text
.github/
├── workflows/
│   ├── backend-quality.yml
│   ├── backend-tests.yml
│   └── repository-security.yml
├── ISSUE_TEMPLATE/
│   ├── implementation.yml
│   ├── architecture-decision.yml
│   └── bug.yml
├── dependabot.yml
└── pull_request_template.md
```

实际 Workflow 可合理合并或拆分，但必须：职责清晰；Job 名称稳定；失败容易定位；避免重复安装和重复检查；不创建始终通过的空 Job。

#### CI Gate Layers

**Fast Static Gate**（每个 PR 必运行）：Repository Hygiene / Ruff Format Check / Ruff Lint / Pyright / Import Linter / Architecture Tests。建议 Stable Required Check：`quality / format`、`quality / lint`、`quality / typecheck`、`quality / architecture`。

**Deterministic Test Gate**（每个 PR 必运行）：Unit Tests / Contract Tests / Fast Local Test Set / Package Build / Locked Dependency Validation。建议：`test / unit-contract`、`test / package-build`。**不得**创建虚假的 Integration、E2E 或 Runtime Test。

**Security Gate**（每个 PR 必运行）：Dependency Vulnerability Audit / Secret Detection / Repository Hygiene Validation。建议：`security / dependency-audit`、`security / secret-detection`。

**Extended Gate**（仅保留未来扩展方向，不得在 FND-003 中伪造）：Full E2E / Live Model Evaluation / Performance Tests / Long Recovery Tests / Deployment Validation。

**Required Check Names** 初始建议集合（8 项）：`quality / format`、`quality / lint`、`quality / typecheck`、`quality / architecture`、`test / unit-contract`、`test / package-build`、`security / dependency-audit`、`security / secret-detection`。规则：不使用动态 Job 名称；不把 Python Patch Version 放入 Required Check 名称；不频繁改名；改名必须同步更新 Branch Protection；不创建职责重叠且名称相近的多个 Check；Experimental Check 必须明确标记为非 Required。

**Python and Dependency Installation** — CI 必须使用 `Python >=3.13,<3.14` 并通过 `uv sync --locked` 安装依赖。必须：使用已提交 `uv.lock`；Lockfile 与 Manifest 不一致时失败；CI 不自动更新 Lockfile；不执行未锁定的 `pip install -U`；Cache Key 包含 Lockfile Hash；Cache Miss 时仍可完整安装。

**Workflow Permissions** — `Default Workflow Permissions = read-only`；普通质量 Workflow 原则上只需要 `contents: read`。写权限必须：使用独立 Workflow、明确说明用途、采用最小权限、不在不可信 Fork PR 上执行、不向普通 Test Job 暴露写 Token。禁止所有 Workflow 默认获得写权限。

**Third-party Action Governance** — 优先级 `Official GitHub Action → Widely adopted maintained Action → Repository-owned script`。安全规则：不使用来源不明的 Action；不使用浮动 `main` 分支；优先固定到 Commit SHA；新 Action 必须记录用途和权限；Action 不得获取无关 Secret；Action 升级通过独立 Dependency PR 审查。

**Secret Detection** — 必须选择正式 Secret Scanner（候选：Gitleaks / TruffleHog / GitHub Secret Scanning / 其他满足要求的 Scanner）；具体选择作为 FND-003 实施中的有界工程决策，但必须记录：选择理由、维护状态、扫描范围、PR Diff 或 Git History 策略、本地复用方式、假阳性处理、Allowlist 规则、日志 Redaction、失败修复流程。至少检测：API Keys / Access Tokens / Private Keys / Cloud Credentials / Database Credentials / Authorization Headers / Real `.env` Files / Provider Secrets。

**Secret Incident Handling** — 正式流程：`Secret Detected → Block Pull Request → Determine whether credential is real → Remove from repository → Rotate or revoke credential → Review history exposure → Add regression protection if required`。仅删除文件或修改 Commit 不足以处理真实 Credential 泄漏；真实 Secret 必须轮换或撤销。

**Secret Allowlist** — 只能用于明确假阳性（Scanner 官方测试 Token / 明显虚假的文档占位符 / 精准的测试 Fixture）。必须：精确到具体内容、说明原因、不宽泛跳过整个目录、不跳过所有 `.env` 或测试内容、不使用看似真实的凭证。

**Dependency Audit** — 正式采用 `pip-audit`，检查 Lockfile 对应的 Python Dependency。默认：`Known actionable vulnerability → CI failure`。漏洞结果需区分 `Fix available / No fix available / False positive / Not reachable / Accepted temporary risk`。无修复版本但无法移除时必须：创建安全 Issue、记录 CVE、说明影响、说明临时缓解、设定复查条件、获得用户明确接受。**禁止** Coding Agent 添加宽泛 Ignore 让 Audit 通过。

**Dependabot** — Repository 应启用 `Dependabot Alerts / Dependabot Security Updates / Controlled Version Updates`；Python 依赖建议 `weekly` 更新节奏。Dependabot PR 必须：更新 Lockfile、通过完整 Required CI、不自动 Merge、不混入业务修改、Major Upgrade 说明 Breaking Risk、由用户完成最终 Merge。

**Pull Request Template** — 创建 `.github/pull_request_template.md`，至少要求：`Summary / Related Issue / Relevant DEC·RFC·Spec / In Scope / Out of Scope / Acceptance Criteria / Tests Executed / Evidence / Architecture Impact / Security Impact / Dependency Changes / Migration·Rollback Impact / Known Limitations / Mandatory Stop Conditions`。Foundation PR 还须说明：对应 FND Issue、对应 RFC-001 DQ、新增工具、新增依赖、本地命令、CI 结果、是否触发新架构决定。允许对不适用项填 `Not applicable — reason`，但不得只填 `Tests passed`。

**Issue Templates** — Implementation Issue（Goal / Relevant DEC / Relevant Spec / Accepted RFC / Dependencies / In Scope / Out of Scope / Acceptance Criteria / Required Tests / Required Evidence / Rollback Considerations / Mandatory Stop Conditions / Authorization Status）；Architecture Decision Issue（Decision Question / Candidates / Trade-offs / Recommendation / User Decision / Status / Affected DEC·RFC·Specs / Implementation Prohibition）；Bug Issue（Observed Behavior / Expected Behavior / Reproduction / Environment / Impact / Evidence / Regression Test Requirement / Related Version·Commit）。模板**不能**自动授予开发权限。

**Branch Protection** — `main` 建议配置：Require Pull Request / Require Required Status Checks / Require Conversation Resolution / Block Force Push / Block Branch Deletion / Require Branch Up to Date or equivalent safe policy。用户保留最终 Merge Gate；当前为个人 Portfolio Repository，不强制不存在的第二名 Reviewer，但仍要求：所有变更通过 PR、用户人工审查、Review Conversation 解决、Required Checks 全部通过、Coding Agent 不得自行 Merge。

**Administrator and Plan Limitations** — 建议管理员也遵守 Branch Protection。若 GitHub Plan、权限或 Repository 设置限制某项保护，必须明确记录 `Configured Protection / Unavailable Protection / Reason / Residual Risk / Manual Compensating Control`。**不得**声称未实际启用的能力已经生效。

**Merge Strategy** — `Pull Request → Required Checks → User Review → Merge Commit`。不得：绕过 PR 直接进入 `main`；自动合并 Dependabot PR；允许 Coding Agent 自行 Merge；使用失败 Check 合并；使用 Force Push 修正历史。Merge 后按 Repository 规则删除 Feature Branch。

**CI Trigger Events** — Required CI 至少响应 `pull_request targeting main / push to main / workflow_dispatch`。用途：Pull Request = Merge Gate；Push to `main` = 验证合并结果；Manual Dispatch = 诊断和重跑。FND-003 不创建定时 Live AI Evaluation。

**Path Filters** — 可减少无关执行但不得遗漏关键变更。以下变化必须触发完整后端质量检查：`apps/backend/**`、`uv.lock`、`pyproject.toml and tool configuration`、`architecture test configuration`、`GitHub workflow files`。纯文档改动至少仍运行 Secret Detection / Repository Hygiene / 必要 Governance Check。禁止过宽 Path Filter 导致代码或配置变化未运行测试。

**CI Concurrency** — 允许 PR 级 Concurrency：`New commit arrives → Cancel obsolete PR run → Run newest commit`。不得取消：`main` 合并后验证、必须保留结果的安全流程、Release 或关键审计流程。

**CI Cache** — 允许缓存 uv Cache / Python Download / 安全的工具 Cache。Cache 必须：Key 包含 OS、Python Version 和 Lockfile Hash；不缓存 Secret；Cache Miss 时仍可完整运行；不能让旧依赖污染新 Lockfile；CI 正确性不依赖 Cache。

**Failure Policy** — Required Check 必须继承 `Warnings = Errors by default`。禁止：Required Job 使用 `continue-on-error`；使用 `|| true` 绕过检查；Secret Scan 永远返回成功；Dependency Audit 失败被隐藏；自动重跑 Flaky Test 直到通过；将失败 Job 伪装为成功。非阻断实验 Job 必须明确标记 `experimental / non-required`。

**CI Negative Verification** — 不仅创建 YAML，还必须证明失败路径真实有效。至少验证：1. Format Violation 导致 `quality / format` 失败；2. Lint Violation 导致 `quality / lint` 失败；3. Type Error 导致 `quality / typecheck` 失败；4. Architecture Violation 导致 `quality / architecture` 失败；5. Unit Test Failure 导致 `test / unit-contract` 失败；6. Lockfile Drift 导致失败；7. 模拟 Secret 导致 `security / secret-detection` 失败；8. Dependency Audit 失败路径可以工作；9. 修复违规后全部 Check 恢复通过。验证必须通过受控临时 Commit、测试 Branch、官方测试模式、最小安全 Fixture。**不得**提交真实 Secret，也不得长期保留已知漏洞依赖。

**Repository Hygiene** — 至少验证：不提交 `.env` / 虚拟环境 / Python Cache / 本地数据库 / Build Artifact / Coverage 临时文件 / IDE 私有状态 / 真实 Credential；Manifest 与 Lockfile 一致。可由 `.gitignore`、Secret Scanner、自定义脚本、Git Diff 检查组合完成。

**CI Log Security** — CI 日志不得输出 GitHub Token / Secret Scanner 原始 Secret / Provider Key / Authorization Header / 私有环境变量 / 生产 Credential。Scanner 和脚本必须尽可能 Redact 匹配值。

**Supply-chain Rules** — 必须记录：Lockfile 必须提交；第三方 Action 固定版本；Workflow 使用最小权限；不从 PR 内容动态执行不可信 Shell；Fork PR 不接收 Repository Secret；不使用 `pull_request_target` 执行不可信代码（除非另有安全设计）；自动生成内容必须接受 Diff 审查；Dependabot PR 不自动 Merge。

**Documentation** — 允许创建或更新 `docs/development/ci-and-repository-governance.md`，至少说明：Workflow 和 Job、Required Check、本地复现方式、Dependency Audit、Secret Detection、Dependabot、Branch Protection、PR 流程、Coding Agent 禁止事项、CI Failure 处理、GitHub Plan 限制、Residual Risk、Emergency Bypass 原则。默认 `No automatic emergency bypass`；未来确需紧急绕过时必须：用户明确授权、记录原因、保存证据、事后恢复保护、创建补充检查 Issue。

### Out of Scope（FND-003 明确不包括）

- **Production Deployment** — Docker Production Image、Container Registry、Cloud Platform、Staging、Production Environment、CD Pipeline、Infrastructure as Code、Runtime Secret Manager、Domain 或 HTTPS。
- **Business and Runtime** — 业务模块、Database、ORM、Migration、API、Worker、LangGraph、Queue、Model Provider、Retrieval、Observability Runtime。
- **Live AI Evaluation** — 真实模型调用、定时 Prompt Evaluation、Token Cost Report、Model Provider Secret。
- **Release Automation** — PyPI Publish、GitHub Release、Semantic Release、自动版本发布、Production Rollback。
- **Advanced Security** — Container Scan、SBOM、Code Signing、Artifact Attestation、完整 SAST Platform。

这些能力等待真实部署或产物需求。

### Acceptance Criteria（未来完成时必须满足）

1. GitHub Actions 已创建并正常运行；
2. CI 复用 FND-001、FND-002 的本地配置和命令；
3. Python 依赖通过 `uv sync --locked` 安装；
4. Lockfile Drift 导致失败；
5. `quality / format` 稳定存在；
6. `quality / lint` 稳定存在；
7. `quality / typecheck` 稳定存在；
8. `quality / architecture` 稳定存在；
9. `test / unit-contract` 稳定存在；
10. `test / package-build` 稳定存在；
11. `security / dependency-audit` 稳定存在；
12. `security / secret-detection` 稳定存在；
13. Required Check 名称与 Branch Protection 一致；
14. Secret Scanner 已选择并记录理由；
15. 模拟 Secret 能被检测；
16. Scanner 测试不使用真实 Secret；
17. `pip-audit` 已接入；
18. 可操作漏洞会阻止合并；
19. Dependabot Alerts 已启用；
20. Dependabot Security Updates 已配置；
21. Version Update 使用受控节奏；
22. Dependabot PR 不自动 Merge；
23. PR Template 已建立；
24. Implementation、Architecture Decision、Bug Issue Template 已建立；
25. `main` 要求通过 PR；
26. `main` 禁止 Force Push；
27. Required Checks 全部通过后才能 Merge；
28. Review Conversation 必须解决；
29. 用户保留最终 Merge Gate；
30. Required Job 不使用 `continue-on-error`；
31. Workflow 默认最小权限；
32. 第三方 Action 不使用浮动 `main`；
33. Fork PR 不获得 Repository Secret；
34. CI 日志不泄漏 Secret；
35. 本地可以复现 Required Check；
36. CI Negative Verification 已完成；
37. 修复违规后全部 Required Checks 通过；
38. GitHub 权限限制被准确记录；
39. 没有创建 Deployment Pipeline；
40. 没有创建业务或 Runtime 代码；
41. 没有修改 Accepted RFC 或 DEC；
42. 文档反映真实保护能力和残余风险。

### Required Verification（未来 FND-003 PR 至少执行）

```text
uv sync --locked
Ruff format check
Ruff lint
Pyright
Import Linter
Architecture tests
Unit and contract tests
Package build
pip-audit
Secret scan
Workflow syntax validation
```

还必须完成：
- **CI Trigger Verification** — 确认 Pull Request 能触发所有 Required Job。
- **Required Check Verification** — 确认 Branch Protection 引用了正确且稳定的 Check 名称。
- **Negative Quality Verification** — 受控证明 Format / Lint / Type / Architecture / Test / Lockfile 违规会失败。
- **Secret Verification** — 使用 Scanner 官方测试 Token 或明显虚假值验证，不提交真实 Credential。
- **Dependency Audit Verification** — 使用 Audit Tool 官方能力或隔离 Fixture 验证失败路径，不长期引入已知漏洞。
- **Merge Protection Verification** — 确认存在 Required Check 失败时 PR 无法正常 Merge。

### Required PR Evidence（未来实施 PR 必须输出）

Workflow 文件清单；Workflow 和 Job 职责；Stable Required Check 名称；Python 和 uv 安装方式；Cache Key 设计；Workflow Permissions；第三方 Action 及固定版本；Secret Scanner 选择理由；Secret Scan 结果；`pip-audit` 结果；Dependabot 配置；PR Template；Issue Templates；Branch Protection 配置证据；Negative Verification 结果；全部 Required Check 最终通过结果；GitHub Plan 或权限限制；Residual Risk；Out-of-scope 审查；Mandatory Stop Condition 状态。**不得只输出 `CI is green`。**

### Mandatory Stop Conditions（实施时遇以下情况必须停止）

1. FND-001 尚未 Merge；
2. FND-002 尚未 Merge；
3. 需要修改 FND-001 或 FND-002 的已接受范围；
4. 本地命令与 CI 无法复用同一配置；
5. 需要降低 Ruff、Pyright、Architecture Test 或 pytest Gate；
6. 需要将 Required Job 设为 `continue-on-error`；
7. 需要向 Fork PR 注入 Secret；
8. 需要使用高权限 GitHub Token；
9. 需要使用不可信第三方 Action；
10. Secret Scanner 会在日志泄漏 Secret；
11. Dependency Audit 需要宽泛忽略全部漏洞；
12. GitHub Plan 无法提供某项保护且没有补偿控制；
13. 需要创建 Deployment Pipeline；
14. 需要创建 Production Secret；
15. 需要创建 API、Worker、Database 或 LangGraph；
16. 需要开始 Live Model Evaluation；
17. 需要自动合并 Dependabot PR；
18. 需要让 Coding Agent 获得 Merge 权限；
19. 发现 Repository 中存在真实 Secret；
20. 需要修改 Accepted RFC 或 DEC；
21. Issue Scope 超出 CI、Security 和 Repository Protection；
22. Required Check 名称无法稳定；
23. 实际修改范围超出 FND-003。

出现这些情况必须输出 `Mandatory Stop Report` 或 `Decision Conflict Report`，**不得**通过关闭检查、夸大实际保护能力或忽略安全风险继续实施。

### Candidate Commit Plan（候选，未授权执行）

```text
ci: add backend quality and test workflows
security: add dependency and secret scanning
chore: configure dependency update automation
docs: add issue and pull request governance
docs: document repository protection
```

实际 Commit 必须按真实变更组织，不机械拆分。

---

## Foundation Candidate Final Review（PASS，2026-07-30）

> **Status: FINAL REVIEW COMPLETE — 审查非授权。** 本节记录已完成的 Foundation Candidate Final Review 结论。Final Review **不**创建 GitHub Issue、不创建 Branch、不创建 Pull Request、不修改 Repository、不执行 Foundation Implementation。每个 Foundation Issue 仍需**单独、明确的用户授权**。

### 一、审查对象

```text
FND-001  Backend Package and Local Tooling Foundation
FND-002  Architecture Enforcement and Test Foundation
FND-003  CI, Security and Repository Protection
```

审查前状态：三者均 `APPROVED FOR ISSUE PLANNING`；`Foundation Candidate Planning = COMPLETED`；所有 Issue Creation / Implementation 均 `NOT AUTHORIZED`。

### 二、范围完整性审查

**FND-001：Backend Package and Local Tooling** — 建立 `apps/backend/` Python 项目、Python 3.13 约束、`src/ai_ecommerce_agent/` Package、`pyproject.toml`、`uv.lock`、Ruff、Pyright、pytest、Coverage 测量基础、统一本地质量命令、Backend README、Package Build/Install/Import 验证。回答：生产后端代码放在哪里、如何安装、如何构建、如何在本地执行最基本的质量检查。**范围结论：COMPLETE。**

**FND-002：Architecture Enforcement and Test Foundation** — 建立 Import Linter、Architecture Test 分类、pytest Strict Markers、Layer Direction Contract、Public Facade-only Import Contract、Module Dependency DAG、Spike Isolation、Configuration/Skill/Orchestration Boundary、Positive/Negative Fixtures、默认无网络测试边界、清晰的 Architecture Violation Report。回答：如何把 RFC-001 的架构原则转化为机器可执行、可产生失败结果的检查。**范围结论：COMPLETE。**

**FND-003：CI, Security and Repository Protection** — 建立 GitHub Actions、Stable Required Status Checks、`uv sync --locked`、`pip-audit`、Secret Detection、Dependabot、PR Template、三类 Issue Template、`main` Branch Protection、Workflow 最小权限、第三方 Action 治理、CI Negative Verification、Repository Governance 文档。回答：如何保证本地质量规则不能被绕过，并阻止违规代码进入 `main`。**范围结论：COMPLETE。**

### 三、职责重复审查

- **Ruff / Pyright / pytest 配置** — 主要归属 FND-001；FND-002 只扩展 pytest Marker / Architecture Tests / Import Linter / Test Selection；FND-003 只调用既有命令。**NO DUPLICATION。**
- **Architecture Enforcement** — 主要归属 FND-002；FND-001 只建立基础工具；FND-003 只把 Architecture Check 接入 CI。**NO DUPLICATION。**
- **GitHub Actions 与 Branch Protection** — 唯一归属 FND-003；FND-001/002 只保证本地命令可被未来 CI 复用。**NO DUPLICATION。**
- **Security** — FND-001（不引入无用途 Dependency / 不读取生产 Secret / Package Import 无副作用）、FND-002（测试默认无网络 / Configuration 和 Secret Boundary Fixture）、FND-003（Secret Scanner / Dependency Audit / Workflow 权限 / Supply-chain 和 Repository Protection）分属不同层级，无冲突。**NO DUPLICATION。**

### 四、依赖顺序审查

正式顺序 `FND-001 → FND-002 → FND-003`。FND-002 依赖 FND-001（需有效 Python Project / `uv.lock` / pytest / Ruff / Pyright / 统一命令入口），不能先于 FND-001 实施——**DEPENDENCY VALID**。FND-003 依赖 FND-001 + FND-002（需接入前者安装和质量命令、后者 Import Linter 和 Architecture Tests），提前实施只能创建空 CI 或重复配置——**DEPENDENCY VALID**。整体依赖图：**ACYCLIC**。

### 五、后续 RFC 范围泄漏审查

三个 Foundation Candidate 均未选择或创建以下任何能力，均 **NO SCOPE LEAKAGE**：

- **RFC-002** — 未选 Database / ORM / Migration / Repository Implementation / Unit of Work / Outbox / Current Truth Schema / Idempotency Schema。
- **RFC-003** — 未创建 LangGraph / Production Graph / Graph State / Checkpointer / Worker / Queue / Durable Dispatch / Resume Runtime（FND-002 仅用普通 Python Fixture 模拟边界，不安装 LangGraph）。
- **RFC-004** — 未选 API Framework / Route / Request-Response / Authentication / Human Review Endpoint / SSE / WebSocket。
- **RFC-005** — 未创建 Parser / Embedding / Vector Store / Retrieval Runtime / Source Index。
- **RFC-006** — 未选 Model Provider / Model SDK / Prompt Registry / Structured Output Runtime / Provider Fallback / Live Model Evaluation。
- **RFC-007** — 未创建 Trace Provider / Metrics Exporter / Alerting / Dashboard / Runtime Operations / Production Redaction Runtime。

### 六、与 RFC-001-DQ-10 的一致性

RFC-001-DQ-10 允许首批 Foundation Work 包含 Python Package、本地质量工具、Architecture Tests、CI、Repository Security——三个 Candidate 恰好分别覆盖（FND-001 = Package + Local Tooling；FND-002 = Architecture Tests；FND-003 = CI + Repository Security），同时继续禁止业务模块、Production Bootstrap、Database、API、Worker、Production LangGraph、Model/Retrieval/Observability Runtime。**一致性结论：PASS。**

### 七、Acceptance Criteria 可执行性

- **FND-001** — 可由 `uv sync --locked` / Package Build / Install / Import / Ruff / Pyright / pytest / Coverage Measurement / Import Side-effect Test 验证。**EXECUTABLE。**
- **FND-002** — 可由 Import Linter / Positive/Negative Fixtures / Marker Strictness / Network Blocking / Architecture Violation Output / FND-001 Regression Checks 验证。**EXECUTABLE。**
- **FND-003** — 可由 GitHub Actions Runs / Stable Status Check Names / Branch Protection / Secret Scanner Test Token / `pip-audit` / Lockfile Drift / Negative CI Commits / PR Merge Blocking / GitHub 设置证据验证。**EXECUTABLE。**

### 八、Mandatory Stop Conditions 审查

三个 Candidate 已覆盖主要越界风险：Python 版本冲突；需选择 Database/ORM/API/Queue；需引入 LangGraph；需创建真实业务模块；需复制 Spike Source；需削弱 Ruff/Pyright/Architecture Gate；需扩大 Shared Kernel；需依赖真实网络或 Secret；需提高 Workflow 权限；需绕过 Branch Protection；发现真实 Credential；需修改 Accepted RFC/DEC；实施范围超出当前 Issue。**结论：SUFFICIENT。**

### 九、主要风险与缓解

1. **Foundation 过度复杂** — 缓解：FND-001 只建最小 Python Package；FND-002 只实现已接受硬规则；FND-003 只接入已有命令；禁止空业务模块和空 CI Job；每个新增 Dependency 必须说明用途。
2. **Architecture Fixture 与真实架构脱节** — 缓解：Fixture 保持最小；每个 Contract 同时具有正/负向示例；真实业务模块进入后继续增加真实 Architecture Regression Tests；Fixture 不作为 Production Design Source。
3. **CI 配置成本过高** — 缓解：本地和 CI 使用相同命令；Stable Required Checks；Cache 只优化速度不改变正确性；不创建尚未存在的 Integration/E2E/Live Job。
4. **GitHub Plan 限制** — 缓解：真实记录可用/不可用能力；记录 Residual Risk；建立人工补偿控制；不声称未启用的保护已经存在。

### 十、Decision Conflict Review

```text
Conflict between FND-001 and FND-002: NONE
Conflict between FND-002 and FND-003: NONE
Conflict with RFC-001: NONE
Conflict with Accepted DEC: NONE
Scope leakage into RFC-002 through RFC-007: NONE
Circular Foundation dependency: NONE
Implementation accidentally authorized: NO
```

不存在需要额外 RFC 或 Technical Spike 才能启动 FND-001 的阻塞问题。

### 十一、最终 Candidate 状态

```text
FND-001 Candidate Status = READY FOR AUTHORIZATION
FND-002 Candidate Status = READY, BLOCKED BY FND-001
FND-003 Candidate Status = READY, BLOCKED BY FND-001 AND FND-002

FND-001 Implementation = NOT AUTHORIZED
FND-002 Implementation = NOT AUTHORIZED
FND-003 Implementation = NOT AUTHORIZED
```

### 十二、推荐授权边界

建议下一步**只**授权：`FND-001 Issue Creation + FND-001 Implementation`，不同时授权 FND-002 或 FND-003。原因：FND-002 依赖 FND-001 的真实 Package 和工具配置；FND-003 依赖前两个 Issue 的真实命令；分阶段授权便于用户逐个审查；符合 RFC-001-DQ-10；可在 FND-001 中及时发现 Python 3.13 或工具兼容问题；防止 Foundation 变成超大实施任务。

### 十三、FND-001 推荐执行流程（用户正式授权后）

```text
Create FND-001 GitHub Issue
↓
Create foundation/001-backend-package-local-tooling
↓
Create bounded Pull Request
↓
Implement only FND-001 scope
↓
Run required verification
↓
Produce PR evidence
↓
User reviews
↓
User decides merge
```

用户授权 FND-001 **不**代表：自动 Merge、自动执行 FND-002、自动执行 FND-003、自动创建业务模块、自动进入 RFC-002。

### 十四、最终审查结论

```text
Candidate Completeness: PASS
Responsibility Separation: PASS
Dependency Order: PASS
RFC-001 Alignment: PASS
Later RFC Scope Protection: PASS
Acceptance Criteria: EXECUTABLE
Mandatory Stop Conditions: SUFFICIENT
Decision Conflict: NONE
Foundation Candidate Final Review: PASS
```

**正式建议：** 批准进入 FND-001 的 Issue Creation and Implementation Authorization Gate。

---

## Immediate Next Topic

```text
FND-001 Issue Creation and Implementation Authorization Gate
```

Foundation Candidate Planning 与 Final Review 均已完成（Final Review = PASS）。**下一正式 Gate：** 只有用户明确回复类似「确认授权创建并实施 FND-001」，才能授权创建 FND-001 GitHub Issue、创建 FND-001 Branch、创建 FND-001 Pull Request、修改 Repository、执行 FND-001 范围内的 Foundation Implementation。该授权仍**不**包括 FND-002、FND-003 或任何业务实现。**在用户明确授权前：不创建任何 Foundation Issue、不创建 Branch、不创建 PR、不修改 Repository、不执行 Foundation Implementation。**
