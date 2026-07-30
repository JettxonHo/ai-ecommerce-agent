# Foundation Issue Candidates（Foundation 议题候选）

> **Status: FOUNDATION PLANNING — DEC-038 · RFC-001-DQ-10 Foundation Authorization Gate**
> **治理来源：** [../decisions/](../decisions/) DEC-034 / DEC-036 / DEC-038 · [../rfcs/rfc-register.md](../rfcs/rfc-register.md)
> **Parent Architecture Input：** RFC-001 Repository and Application Architecture（**Status = ACCEPTED**，2026-07-30）
> **纪律：** 本文件**只**记录 Foundation Issue Candidates（候选议题），供用户审查。**它不创建任何 GitHub Issue、不创建 Branch、不创建 Pull Request、不修改 Repository、不创建 `apps/backend/`、不安装 Dependency、不创建 Lockfile、不开始任何 Foundation Implementation。** 每个 Foundation Issue 在被创建或实施前，都必须获得用户**单独、明确**的授权。

---

## 授权边界（恒定成立）

```text
RFC-001 Status = ACCEPTED

FND-001 Candidate Status = APPROVED FOR ISSUE PLANNING
FND-001 Issue Creation = NOT AUTHORIZED
FND-001 Implementation = NOT AUTHORIZED

FND-002 Candidate Status = APPROVED FOR ISSUE PLANNING
FND-002 Issue Creation = NOT AUTHORIZED
FND-002 Implementation = NOT AUTHORIZED

Foundation Planning Status = AUTHORIZED
Foundation Implementation Status = NOT AUTHORIZED
Business Implementation Status = NOT AUTHORIZED

Architecture Readiness = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
Production Implementation = NOT AUTHORIZED
```

**Acceptance 与 Authorization 严格分离：**
`接受 Candidate ≠ 授权创建 Issue ≠ 授权创建 Branch/PR ≠ 授权实施 Foundation ≠ 授权 Business/Production Implementation`。

接受 FND-001 / FND-002 Candidate 仅表示用户接受其**候选范围、边界、依赖与验收方向**；**不**授权创建 GitHub Issue、Branch、Pull Request、修改 Repository、安装工具、编写 Architecture Tests 或执行 Foundation Implementation。

---

## Candidate 总览与依赖顺序

```text
FND-001  Backend Package and Local Tooling Foundation        (无前置 Foundation Issue)
FND-002  Architecture Enforcement and Test Foundation        (deps: FND-001)
FND-003  CI, Security and Repository Protection              (deps: FND-001 + FND-002)
```

执行顺序遵循依赖：`FND-001 → FND-002 → FND-003`，遵循 **One Issue → One Branch → One PR → Required Verification → User Merge Gate**。任一 Candidate 在被单独授权创建 Issue 前，都停留在 `APPROVED FOR ISSUE PLANNING` / `PROPOSED` 状态。

| Candidate | 主题 | 依赖 | Candidate Status | Issue Creation | Implementation |
|---|---|---|---|---|---|
| **FND-001** | Backend Package and Local Tooling Foundation | RFC-001 = ACCEPTED（无前置 Foundation Issue） | **APPROVED FOR ISSUE PLANNING** | NOT AUTHORIZED | NOT AUTHORIZED |
| **FND-002** | Architecture Enforcement and Test Foundation | FND-001 | **APPROVED FOR ISSUE PLANNING** | NOT AUTHORIZED | NOT AUTHORIZED |
| FND-003 | CI, Security and Repository Protection | FND-001 + FND-002 | PROPOSED（未单独确认） | NOT AUTHORIZED | NOT AUTHORIZED |

---

## FND-001：Backend Package and Local Tooling Foundation（APPROVED FOR ISSUE PLANNING）

**用户确认：** 「确认形成」——接受 FND-001 的候选范围、边界、依赖与验收方向。

**Candidate Status：**

```text
FND-001 Candidate Status = APPROVED FOR ISSUE PLANNING
FND-001 Issue Creation = NOT AUTHORIZED
FND-001 Implementation = NOT AUTHORIZED
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

## FND-002：Architecture Enforcement and Test Foundation（APPROVED FOR ISSUE PLANNING）

**用户确认：** 「确认」——接受 FND-002 的候选范围、依赖、验收标准和禁止边界。

**Candidate Status：**

```text
FND-002 Candidate Status = APPROVED FOR ISSUE PLANNING
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

## Immediate Next Topic

```text
FND-003：CI, Security and Repository Protection
```

下一轮只规划 FND-003 的 GitHub Actions / Required Check Names / Dependency Audit / Secret Detection / Dependabot / PR / Issue Templates / Branch Protection / Acceptance Criteria / Required Verification / Mandatory Stop Conditions / Git / GitHub Candidate Plan。**不得自动创建或实施 FND-003。**
