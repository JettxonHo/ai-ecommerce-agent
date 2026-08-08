# Architecture Tests（架构测试）

本目录把 RFC-001 已接受的架构规则转换为**可自动执行、可产生清晰违规报告、可供未来 CI 阻断合并**的检查。所有检查均为测试基础设施：**不进入生产包、不被生产代码 import、不代表任何真实业务模块已经创建**。

## 1. 为什么存在 Architecture Tests

RFC-001（DQ-03 / DQ-04 / DQ-05 / DQ-06 / DQ-08 / DQ-09）定义了层方向、模块边界、Public Facade、模块 DAG、Configuration / Skill / Orchestration / Bootstrap 边界与 Spike 隔离等硬规则。文档建议可以被无视，可执行 Contract 不会：

```text
Accepted Architecture Rule
↓
Executable Contract（Import Linter / grimp / AST）
↓
Positive and Negative Fixtures（证明不过严、不放水）
↓
uv run lint-imports && uv run pytest -m architecture
↓
未来 FND-003 CI 的 Merge-blocking Check
```

真实业务模块尚未存在，因此这些检查对生产包当前是**真空但已上线**（vacuous but live）：一旦相应代码进入，检查自动生效。Fixture 证明每条规则确实能识别违规，且不会误伤合法架构。

## 2. 工具职责（单一 Source of Truth，不重复同一规则）

| 工具 | 职责 | 运行方式 |
|---|---|---|
| **Import Linter** | Import Graph 规则：Spike 隔离、模块内层方向、顶层包方向（含 Shared Kernel 独立）、Domain/Application 内外依赖纯度、Bootstrap 方向、Orchestration/Entrypoint 外部依赖 | `uv run lint-imports`（10 条 Contract，配置在 `apps/backend/pyproject.toml` 的 `[tool.importlinter]`） |
| **Custom grimp tests** | Import Linter 内置 Contract 无法表达的相对规则：Public Facade-only 跨模块 Import（"同模块可以、他模块不可以"无法表达）、Module Dependency DAG（`acyclic_siblings` 在 `modules` 包不存在时会硬报错） | `uv run pytest -m architecture`（与 Import Linter 使用同一 grimp 图引擎） |
| **Custom AST tests** | 语义规则（import 边无法表达）：Core Layer 环境访问（os.environ / os.getenv / dotenv）、Public Contract 技术类型泄漏、Skill Boundary | `uv run pytest -m architecture` |
| **Ruff / Pyright** | 保持既有职责（Formatting / Import Sorting / 静态质量 / 类型安全），不承担架构规则 | FND-001 命令 |

每条规则只有唯一权威 Checker。Fixture 合约配置 `fixtures/fixture-importlinter.ini` 与生产 Contract **逐条镜像**（同名同类型，root 为测试专用 `fixture_pkg`），`test_import_contracts.py` 中的镜像同步测试保证两者不漂移。

## 3. Fixture 结构

每个 Fixture 目录包含一个最小的 `fixture_pkg` 包，只验证一项主要规则：

```text
fixtures/
├── fixture-importlinter.ini           # 生产 Contract 的 fixture 镜像（root = fixture_pkg）
├── valid_layered_package/             # 合法：domain <- application <- infrastructure
├── valid_public_facade_dependency/    # 合法：跨模块经 .public；单向模块依赖
├── valid_shared_kernel_dependency/    # 合法：domain 使用 shared_kernel
├── valid_orchestration_dependency/    # 合法：orchestration 经 .public + shared_kernel
├── valid_bootstrap_infrastructure/    # 合法：bootstrap 绑定模块 application + infrastructure（RFC-001 DQ-06）
├── invalid_domain_imports_infrastructure/
├── invalid_application_imports_adapter/
├── invalid_cross_module_private_import/
├── invalid_module_dependency_cycle/   # 经 Public Facade 形成的模块级循环
├── invalid_production_imports_spike/  # spikes 故意不可解析（与生产现实一致）
├── invalid_shared_kernel_dependency/
├── invalid_orchestration_imports_infrastructure/
├── invalid_entrypoint_imports_repository/
├── invalid_core_reads_environment/
├── invalid_public_contract_exposes_technical_type/
└── invalid_skill_boundary/
```

Fixture 规则：不进入 `src/`、不被生产 import、不代表真实业务模块、最小化、无网络、无 Secret、无真实外部资源。技术类 import（sqlalchemy / langgraph 等）**故意不可解析**——FND-002 不安装任何 ORM 或 LangGraph，检测全部为静态分析。Fixture 目录被 Pyright 精准排除（虚构模块无类型价值）；Ruff 照常检查。

## 4. 如何新增 Contract

1. 确认规则来自 Accepted RFC/DEC（不接受临场发明架构规则）；
2. 判定工具归属：import 图规则 → Import Linter；相对/语义规则 → 自定义 grimp/AST 测试；不得用两个工具重复实现同一规则；
3. Import Linter 规则：在 `pyproject.toml` 的 `[tool.importlinter]` 增加 `[[tool.importlinter.contracts]]`，并**同步**在 `fixtures/fixture-importlinter.ini` 增加镜像条目（root 换成 `fixture_pkg`）——镜像同步测试会强制这一点；
4. 至少新增一个 Positive Fixture（证明不误伤）与一个 Negative Fixture（证明能识别）；
5. 注意既有工具限制（见第 7 节），必要时在本文档记录。

## 5. 如何执行检查

```bash
cd apps/backend
uv run lint-imports                 # Import Linter 生产 Contract
uv run pytest -m architecture       # 自定义架构测试（grimp + AST + fixture 验证）
uv run pytest -m "not live and not slow"   # test-fast（含架构测试）
```

统一命令语义见 `apps/backend/README.md`。未来 FND-003 CI 直接复用这些命令。

## 6. 如何阅读失败

Import Linter 输出包含 Contract 名与完整 import 链（含行号），例如：

```text
Module layer direction
----------------------
fixture_pkg.modules.brief.domain is not allowed to import
fixture_pkg.modules.brief.infrastructure:
- fixture_pkg.modules.brief.domain.model -> fixture_pkg.modules.brief.infrastructure.adapter (l.1)
```

自定义测试的失败消息固定包含四个字段：

```text
Rule: Cross-module imports must use the public facade
Source: fixture_pkg.modules.beta.application.service
Illegal Target: fixture_pkg.modules.alpha.domain.model
Expected Boundary: fixture_pkg.modules.alpha.public
```

修复方向只有两个：**修正代码使其合法**，或（极少数）申请精确例外（见下）。`Architecture test failed` 这类无定位信息的失败被视为缺陷。

## 7. 如何申请精确例外

确需例外时（如迁移期临时依赖）：

- Import Linter：使用 Contract 级 `ignore_imports`（精确到 `importer -> imported` 单条 import），并附注释说明原因、批准依据与移除条件；
- 自定义测试：在对应 Checker 增加**精确**的、有注释的例外参数，不得整体跳过。

任何例外必须可追溯到一个 Accepted Decision 或用户明确批准。

## 8. 禁止事项

- 禁止删除或弱化 Contract 让检查通过；
- 禁止宽泛 Ignore（整个目录 / 整个包 / `# noqa` 式跳过）；
- 禁止跳过 Negative Fixture 或让其永远失败地留在 Branch 中；
- 禁止用空测试或"Checker 没有检查 Fixture"制造虚假成功；
- 禁止把 Fixture 当作 Production Skeleton 或让生产代码 import Fixture。

## 9. 已知表达限制（有记录，非静默）

- Import Linter `forbidden` Contract 的**字面量** source 在模块不存在时硬报错，通配符只能替换完整段——因此尚不存在的 `orchestration/` `entrypoints/` 包的 `__init__.py` 级外部依赖暂由 Facade 测试兜底（模块内部 import 已被覆盖）；这些包落地后，将通配 source 升级为字面量即可补齐。
- `acyclic_siblings` 在 ancestor 不存在时硬报错，故 Module DAG 当前由自定义 grimp 检查承担；`modules` 包出现后可迁移。
- 外部 forbidden 只接受顶层包名（`sqlalchemy` 而非 `sqlalchemy.orm`），由 `include_external_packages = true` 支撑。

## 10. 与 RFC-001 的追踪关系

| 规则 | RFC-001 决定 | 执行器 |
|---|---|---|
| Spike 隔离 | DQ-10 | Import Linter `Production and Spike isolation` |
| 模块内层方向（Domain/Application/Infrastructure） | DQ-04 | Import Linter `Module layer direction` |
| 顶层包方向 + Shared Kernel 独立 | DQ-03 / DQ-08 | Import Linter `Top-level package direction` |
| Domain / Application 依赖纯度 | DQ-04 | Import Linter `Domain/Application internal/external dependencies` |
| Bootstrap 方向 | DQ-06 | Import Linter `Bootstrap not imported by core` |
| Orchestration / Entrypoint 边界 | DQ-04 / DQ-07 | Import Linter `Orchestration/Entrypoint external dependencies` + Facade 测试 |
| Public Facade-only 跨模块 Import | DQ-08；Composition Root 对 Infrastructure 的精确例外见 DQ-06 | 自定义 grimp 测试（`helpers/rules.py`） |
| Module Dependency DAG | DQ-08 | 自定义 grimp 测试（`helpers/rules.py`） |
| Core 环境访问 / Configuration 边界 | DQ-06 | 自定义 AST 测试（`helpers/ast_scanner.py`） |
| Public Contract 技术泄漏 | DQ-08 | 自定义 AST 测试 |
| Skill Boundary | DQ-05 | 自定义 AST 测试 |

完整规则文本以正式 RFC 文档为准（`docs/rfcs/rfc-001-repository-and-application-architecture.md`），本目录不复制 RFC 内容。
