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

Foundation Planning Status = AUTHORIZED
Foundation Implementation Status = NOT AUTHORIZED
Business Implementation Status = NOT AUTHORIZED

Architecture Readiness = CONDITIONALLY READY
Development Status = CONDITIONALLY READY
Production Implementation = NOT AUTHORIZED
```

**Acceptance 与 Authorization 严格分离：**
`接受 Candidate ≠ 授权创建 Issue ≠ 授权创建 Branch/PR ≠ 授权实施 Foundation ≠ 授权 Business/Production Implementation`。

接受 FND-001 Candidate 仅表示用户接受其**候选范围、边界、依赖与验收方向**；**不**授权创建 GitHub Issue、Branch、Pull Request、修改 Repository 或执行 Foundation Implementation。

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
| FND-002 | Architecture Enforcement and Test Foundation | FND-001 | PROPOSED（未单独确认） | NOT AUTHORIZED | NOT AUTHORIZED |
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

## Immediate Next Topic

```text
FND-002：Architecture Enforcement and Test Foundation
```

下一轮只规划 FND-002 的 Scope / Out of Scope / Import Linter Contracts / Architecture Fixtures / Test Classification / Acceptance Criteria / Required Verification / Mandatory Stop Conditions / Git / GitHub Candidate Plan。**不得自动创建或实施 FND-002。**
