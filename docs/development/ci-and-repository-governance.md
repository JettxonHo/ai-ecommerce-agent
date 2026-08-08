# CI and Repository Governance（FND-003）

> **治理来源：** RFC-001（ACCEPTED，DQ-06 / DQ-08 / DQ-09 / DQ-10）· DEC-036 · DEC-038
> **实施：** [FND-003 Issue #14](https://github.com/JettxonHo/ai-ecommerce-agent/issues/14)
> **核心原则：** Local Configuration = CI Configuration。CI 复用 `apps/backend/` 的同一份 `pyproject.toml` / `uv.lock` / Ruff / Pyright / pytest / Import Linter 配置、`apps/web/` 的 `package-lock.json` / npm scripts 与 [backend README](../../apps/backend/README.md) 的统一命令。**不存在第二套 CI 专用质量规则。**
> **Current merge governance（2026-08-08）：** 本文中“用户最终 Merge”描述的是 FND-003 形成时的历史规则。未来 Goal 以 [DEC-040](../decisions/dec-040-autonomous-agent-execution-and-model-roles.md)、[DEC-043](../decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md)、[DEC-071](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md) 与 [AGENTS.md](../../AGENTS.md) 为准：实现 Agent 必须按准确名称路由 `luna-worker`，不得自批或自合并；普通低风险 PR 可在 Required Checks 全绿、Sol 独立 Review 无阻塞后由 Sol 或另一非实现 Agent 合并；高风险事项保留人工 Gate。

---

## 1. Workflows 与 Stable Required Checks

四个 Workflow 按职责分离，Workflow 级 `name:` 与 Job key 组合产生稳定检查名（不含 Python Patch Version、Matrix 动态值、随机标识或工具版本）：

| Workflow 文件 | Workflow `name` | Job | Stable Check Name | 执行内容 |
|---|---|---|---|---|
| `.github/workflows/backend-quality.yml` | `quality` | `format` | `quality / format` | `uv run ruff format --check .` |
| | | `lint` | `quality / lint` | `uv run ruff check .` |
| | | `typecheck` | `quality / typecheck` | `uv run pyright`（strict） |
| | | `architecture` | `quality / architecture` | `uv run lint-imports`（10 contracts）**＋** `uv run pytest -m architecture`（分步执行，失败输出可区分两者） |
| `.github/workflows/backend-tests.yml` | `test` | `unit-contract` | `test / unit-contract` | `pytest -m unit` ＋ `pytest -m contract` ＋ `pytest -m "not live and not slow"` |
| | | `package-build` | `test / package-build` | `uv lock --check`（Lockfile Drift）＋ `uv build` ＋ 隔离 venv 安装 wheel 的 Package Import Regression |
| `.github/workflows/repository-security.yml` | `security` | `dependency-audit` | `security / dependency-audit` | `uv run pip-audit --progress-spinner off --skip-editable` ＋ `npm ci --no-audit --no-fund` ＋ `npm audit --registry=https://registry.npmjs.org`（分别覆盖 `uv.lock` 与 `apps/web/package-lock.json`） |
| | | `secret-detection` | `security / secret-detection` | gitleaks（全历史 + 工作树，`--redact`） |
| `.github/workflows/web.yml` | `web` | `quality` | `web / quality` | `npm ci --no-audit --no-fund` ＋ `npm run format:check` ＋ `npm run lint` ＋ `npm run typecheck` ＋ `npm run build` |
| | | `unit-contract` | `web / unit-contract` | `npm ci --no-audit --no-fund` ＋ `npm run test:unit` ＋ `npm run test:contract` |
| | | `chromium` | `web / chromium` | `npm ci` ＋ `npm run test:e2e` |

除 MVP0-036 的 `web / chromium` foundation shell smoke 外，不存在的检查（也**不得**创建）：backend Integration / full product E2E / Live AI / Deployment Required Check。`live` 标记测试（真实外部网络或 Provider）永远不会在 CI 中运行。

这 11 个 Stable Check Name（既有 8 项加 3 项 Web checks）与 `main` Branch Protection 的 Required Status Checks 一一对应。`web / change-detection` 是非 Required 的辅助 Job；三个 Web contexts 在每个 PR / `main` push / 手动 dispatch 都会出现，无关 diff 只执行 checkout-free bounded no-op，受影响 diff 才安装依赖并运行 suite。改名必须先更新 Branch Protection 并经过用户审查。

## 2. 本地复现 Required Checks

Backend 命令在 `apps/backend/` 下执行，Web 命令在 `apps/web/` 下执行，与 CI 完全一致：

| Stable Check | 本地命令 |
|---|---|
| `quality / format` | `uv run ruff format --check .` |
| `quality / lint` | `uv run ruff check .` |
| `quality / typecheck` | `uv run pyright` |
| `quality / architecture` | `uv run lint-imports && uv run pytest -m architecture` |
| `test / unit-contract` | `uv run pytest -m unit && uv run pytest -m contract && uv run pytest -m "not live and not slow"` |
| `test / package-build` | `uv lock --check && uv build`（Import Regression 见下） |
| `security / dependency-audit` | Backend: `uv run pip-audit --progress-spinner off --skip-editable`; Web: `npm ci --no-audit --no-fund && npm audit --registry=https://registry.npmjs.org` |
| `security / secret-detection` | `gitleaks detect --source . --verbose --redact --no-banner` |
| `web / quality` | `npm run format:check && npm run lint && npm run typecheck && npm run build`（在 `apps/web/`） |
| `web / unit-contract` | `npm run test:unit && npm run test:contract`（在 `apps/web/`） |
| `web / chromium` | `npm run test:e2e`（在 `apps/web/`） |

一键质量门（backend README 统一入口，不含 security 两项）：

```bash
uv run ruff format --check . && uv run ruff check . && uv run pyright && uv run lint-imports && uv run pytest -m "not live and not slow"
```

Package Import Regression 本地复现：

```bash
uv build
uv venv /tmp/import-regression
VIRTUAL_ENV=/tmp/import-regression uv pip install dist/ai_ecommerce_agent-*.whl
/tmp/import-regression/bin/python - <<'PY'
import importlib.resources as resources

import ai_ecommerce_agent

assert resources.files("ai_ecommerce_agent").joinpath("py.typed").is_file()
print("package import OK; py.typed present")
PY
```

Secret Detection 本地复现（gitleaks 安装方式任选官方发布渠道；版本应与 CI 一致，见 §6）：

```bash
# macOS 示例
brew install gitleaks
gitleaks detect --source . --verbose --redact --no-banner
```

## 3. 依赖安装与 Lockfile 纪律

- 锁定环境分别使用 `uv sync --locked`（Backend）与 `npm ci --no-audit --no-fund`（Web；本地与 CI 相同）。
- **禁止**在 CI 中执行 `pip install -U`、`uv lock`、`uv sync`（无 `--locked`）或 `npm install` 等会静默更新 Lockfile 的命令。
- Lockfile Drift 由 Backend 的 `uv sync --locked` / `uv lock --check` 与 Web 的 `npm ci` 拦截；安全 Job 再对两份锁定环境执行审计。
- Lockfile 的合法更新只发生在本地开发分支：Backend 修改 `pyproject.toml` 后执行 `uv lock`，Web 修改 `package.json` 后使用 npm 受控更新，把需求文件与对应 lockfile 一并提交，由 CI 验证一致性。

## 4. 工具版本锚定

| 工具 | 锚定值 | 锚定位置 |
|---|---|---|
| Python | `3.13.14` | `apps/backend/.python-version`（本地）＋ Workflow `python-version`（CI） |
| uv | `0.12.0` | Workflow `setup-uv` 的 `version` 输入 |
| Ruff / Pyright / pytest / pytest-cov / pytest-socket / import-linter / pip-audit | `uv.lock` 精确版本 | `apps/backend/uv.lock` |
| gitleaks | `8.30.1` ＋ 硬编码 SHA-256 | `.github/workflows/repository-security.yml` |

升级任何工具都是一次独立变更（Dependency PR 或专门的工具升级 PR），不得混入业务变更。

### 第三方 Action 清单

| Action | SHA Pin | 版本 | 来源 / 维护者 | License | 用途 | 授予权限 |
|---|---|---|---|---|---|---|
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | v7.0.1 | GitHub 官方（`actions` org） | MIT | 检出仓库代码 | `contents: read`（Workflow 级） |
| `astral-sh/setup-uv` | `c771a70e6277c0a99b617c7a806ffedaca235ff9` | v9.0.0 | Astral 官方（`astral-sh` org） | MIT | 安装 uv（锚定 0.12.0）＋ Python（3.13.14）＋依赖缓存 | `contents: read`（Workflow 级） |

gitleaks 不以 Action 引入（发布二进制 ＋ SHA-256 校验，见 §6）。新增第三方 Action 必须先在本表登记（SHA Pin ＋ 来源 ＋ License ＋ 用途 ＋ 权限），并经用户审查。

## 5. Dependency Audit（pip-audit + npm audit）

- `pip-audit` 作为 **dev/security 依赖锁定在 `uv.lock`**（`apps/backend/pyproject.toml` 的 `dev` 组）。
- 审计对象是 `uv sync --locked` 后的**锁定环境**本身，因此审计结果与 `uv.lock` 的精确版本逐一对应。
- 可操作（actionable）的已知漏洞 → 非零退出 → Required Check 失败。**没有** `--ignore-vuln` 条目、没有 `|| true`、没有 `continue-on-error`。
- `--skip-editable` 只跳过**一个**包：本项目自身（未发布到 PyPI、运行时依赖为零）。该跳过会在 pip-audit 输出的 Skip 表中显式列出，除此之外所有依赖（含全部 dev 依赖）均被审计。`--skip-editable` 不是宽泛忽略：它无法按包名或漏洞编号跳过任何第三方依赖。

### 漏洞结果分类与处理

| 分类 | 处理 |
|---|---|
| Fix available | 升级依赖（独立 PR 或 Dependabot PR），通过全部 Required Checks 后由用户 Merge |
| No fix available | 评估替代依赖或缓解措施，记录为 Known Limitation |
| False positive | 需要证据（上游 issue / advisory 链接）；不得在无证据时忽略 |
| Not reachable | 需要可达性分析证据；不得在无证据时忽略 |
| Accepted temporary risk | **必须**：单独 Issue ＋ 明确 CVE ＋ 明确影响 ＋ 明确缓解 ＋ **用户明确接受**。Agent 不得自行接受任何安全风险 |

当前状态：`pip-audit` 审计结果 = **No known vulnerabilities found**（FND-003 实施时基线）。

### npm 锁定环境

- Web 审计对象是 `apps/web/package-lock.json` 对应的 Node 24.18.0 / npm 11.16.0 锁定安装环境。
- `security / dependency-audit` 先执行 `npm ci --no-audit --no-fund`，再执行 `npm audit --registry=https://registry.npmjs.org`；命令不忽略漏洞、不使用 `continue-on-error`，可操作漏洞以非零退出阻断检查。

## 6. Secret Detection（gitleaks）

### 选型记录

| 候选 | 结论 | 理由 |
|---|---|---|
| **Gitleaks**（✅ 选用，v8.30.1） | Required Check 实现 | MIT License；维护活跃（持续发布）；规则集覆盖 API Keys / Access Tokens / Private Keys / Cloud Credentials / Database Credentials / Authorization Headers / `.env` 内容 / Provider Secrets；支持 Git 全历史 + 工作树扫描；`--redact` 保证匹配值不进日志；单一发布二进制即可本地复用，本地与 CI 行为一致 |
| TruffleHog | 未选用 | 维护活跃，但 AGPL-3.0（许可约束更重）；核心能力依赖在线 verification（对第三方服务发起网络请求），作为确定性 Required Check 不如离线规则扫描稳定；运行更重 |
| GitHub Secret Scanning | **补充层**（非 Required Check） | 平台原生、Public 仓库免费、含 Push Protection；已在仓库设置中启用（见 §10）。但其告警是异步平台信号，不是可在 PR 上确定性阻塞的检查，因此不能替代 CI Required Check；两者互补 |

### 安装与供应链

- CI 中 gitleaks 以**发布二进制**方式安装（不使用第三方 Action）：从官方 Release 下载 `linux_x64` 压缩包，用 Workflow 内硬编码的 SHA-256 校验通过后才会执行。供应链恰好是一个经过校验的 Release 产物。
- 未使用 `gitleaks/gitleaks-action` 的原因：该 Action 引入额外的专有许可证密钥语义（`GITLEAKS_LICENSE`），而直接使用 MIT 工具的二进制发布更简单、审计面更小。
- gitleaks 升级 = 专门的 Dependency PR：同时更新 `GITLEAKS_VERSION` 与 `GITLEAKS_SHA256`，通过 Required Checks 后由用户 Merge。

### 扫描策略

| 维度 | 策略 |
|---|---|
| PR Diff | `pull_request` 触发时在 merge ref 上运行（含 PR 变更） |
| Working Tree | 始终扫描 |
| Git History | `fetch-depth: 0` 全历史扫描——「提交后再删除」的 Secret 仍会被发现 |
| 本地复用 | 同一命令（内置默认规则，无自定义配置；见下方 Known Limitation） |
| 日志 Redaction | `--redact`：报告中匹配值被掩码，CI 日志不含 Secret 物料 |
| 假阳性策略 | 默认规则集；出现假阳性时逐条加入精确 Allowlist 并在本文档登记原因 |
| Allowlist | 使用 gitleaks 内置默认规则（不自带自定义配置文件；见 Known Limitation），当前**零** Allowlist 条目。**禁止**整目录排除（`tests/`、`docs/`、`config/`、`.env*` 等一律不得整体跳过） |
| 测试用 Secret | **绝不使用真实 Secret**。负向验证只使用扫描器官方测试模式与明显假值（如 AWS 文档示例键），且只存在于临时验证 Branch，证据采集后立即删除 |

**Known Limitation（负向验证发现）：** gitleaks 8.30.1 下，带 `useDefault = true` 的自定义配置会**静默漏检**内置默认规则本可检出的模式（FND-003 负向验证实证：同一假值在移除配置文件后立即被检出）。因此本仓库**不携带自定义 gitleaks 配置**运行（使用内置默认规则）。未来如确需 Allowlist，必须：(1) 使用显式完整配置而非 `useDefault`；(2) 上线前通过假值**正向检出复测**（检不出假值的扫描等于没有保护）；(3) 在本节登记每个 Allowlist 条目的假阳性原因。

## 7. Dependabot

- 配置文件：`.github/dependabot.yml`。
- 两个生态：`github-actions`（更新 SHA-pinned Actions）与 `uv`（`/apps/backend`，同时维护 `pyproject.toml` 与 `uv.lock`——因此 Dependabot PR 不会引入 Lockfile Drift）。当前未配置 `npm` ecosystem；`apps/web` 的 npm Dependabot policy 是未来有界治理变更，不属于本次文档同步范围。
- 频率：weekly。
- 纪律：
  - Dependabot PR **不自动 Merge**（仓库无任何 auto-merge 配置）；
  - Dependabot PR 必须通过全部 Required Checks；
  - Major Update 单独成 PR 并附 Release Notes，Breaking Risk 显式可见；
  - 依赖更新不与业务变更混合；
  - 用户保留最终 Merge 决定。
- 仓库设置侧：Dependabot Alerts 与 Dependabot Security Updates 已启用（见 §10）。

## 8. Workflow 触发器、并发与缓存

| 维度 | 配置 |
|---|---|
| 触发器 | `pull_request`（全部目标分支，含 `main`）＋ `push: branches: [main]` ＋ `workflow_dispatch` |
| 并发 | `group: ${{ github.workflow }}-${{ github.ref }}`；`cancel-in-progress` 仅在非 `main` ref 上为 true——PR 新 Commit 到达取消旧 Run，`main` 合并后验证**永不取消** |
| 缓存 | `astral-sh/setup-uv` 内置缓存；Key = OS ＋ arch ＋ `uv.lock` 哈希（`cache-dependency-glob: apps/backend/uv.lock`）＋ Python 版本后缀（`cache-suffix: py3.13.14`） |
| 缓存安全 | 缓存只含 uv 下载产物，不含任何 Secret；Cache Miss 时 `uv sync --locked` 完整安装，正确性不依赖缓存命中；lock 哈希入 Key，旧 Lockfile 不会污染新构建 |

## 9. Workflow 权限与 Fork 安全

- 四个 Workflow 一律 `permissions: contents: read`（最小权限）。没有任何 Job 获得 `contents: write` / `actions: write` / `pull-requests: write` / `issues: write`。
- **仓库没有配置任何 Repository Secret**，Workflow 也不引用任何 Secret——Fork PR 天然无法获得 Secret。
- 全仓库不使用 `pull_request_target`；普通测试 Job 不暴露任何写 Token。
- 如未来某个操作确实需要更高权限：必须放在**独立 Workflow** 中、写明理由、经用户审查，且绝不在执行不可信 PR 代码的触发器上运行。

## 10. Branch Protection 与仓库安全设置

`main` 分支保护（经 `gh api` 配置，实际状态以仓库设置为准）：

| 保护项 | 状态 |
|---|---|
| Require Pull Request（合并必须经过 PR） | 启用（`required_approving_review_count = 0`：个人 Portfolio 仓库，不配置不存在的 Reviewer 要求，避免用户无法自行 Merge） |
| Require Required Status Checks（11 个 Stable Checks） | 启用，`strict = true`（要求分支与 `main` 保持最新） |
| Require Conversation Resolution | 启用 |
| Block Force Push | 启用（默认行为，未允许） |
| Block Branch Deletion | 启用（默认行为，未允许） |
| 管理员同样遵守保护规则（enforce_admins） | 启用——包括用户与 Agent 在内的所有人都不能绕过 Required Checks |

仓库安全设置：

| 设置 | 状态 |
|---|---|
| Dependabot Alerts | 启用 |
| Dependabot Security Updates | 启用 |
| GitHub Secret Scanning（含 Push Protection） | 启用（Public 仓库免费；作为 CI gitleaks 检查的平台补充层） |

**GitHub Plan 限制记录：** 本仓库为 Public 仓库（GitHub Free），上述保护与安全能力均可用，无 Plan 受限项。若未来转为 Private（Free Plan），classic Branch Protection 与 Secret Scanning 将不可用，届时必须记录：Unavailable Protection / Reason / Residual Risk / Manual Compensating Control，并评估迁移到 Rulesets 或 GitHub Pro。

**用户 Merge Gate：** 保护规则保证 Required Checks 全绿 + 会话全部解决后 PR 才可合并；是否合并、何时合并始终由用户决定。Acceptance ≠ Authorization。

## 11. PR 与 Issue 流程

- PR 模板：`.github/pull_request_template.md`（Summary / Related Issue / DEC·RFC·Spec / In·Out of Scope / Acceptance / Tests / Evidence / Architecture·Security Impact / Dependency Changes / Rollback / Known Limitations / Mandatory Stop Conditions）。
- Issue 模板：`implementation.yml`（含 Authorization Status 强制字段）、`architecture-decision.yml`（含 Implementation Prohibition）、`bug.yml`（含 Regression Test Requirement）。
- **模板不授予任何开发权限。** Authorization Status 未明确为 AUTHORIZED 前不得开始实施；Merge 一律由用户决定。
- 标准链路：Issue（授权状态明确）→ 独立 Branch → 实施 → 本地质量门 → PR（Required Checks 全绿）→ 用户审查 → 用户 Merge。

## 12. Agent 禁止事项（FND-003 相关）

Coding Agent 在本仓库中**不得**：

1. 自行 Merge 任何 PR（含 Dependabot PR、验证 PR）；
2. 修改本文件 §1 的 Stable Check Name 或削弱任何质量门（Ruff / Pyright / pytest / Architecture / pip-audit / npm audit / gitleaks）；
3. 在 CI 中引入 `continue-on-error`、`|| true` 或宽泛漏洞忽略；
4. 使用 `pull_request_target`、向 Fork PR 注入 Secret、引用任何真实 Secret；
5. 使用浮动 `main` 或不可信第三方 Action；新增第三方 Action 必须 SHA Pin ＋ 记录来源/用途/权限；
6. 为了绕过失败而删除或降级 Required Check；
7. 自动接受安全风险（Accepted temporary risk 必须用户明确接受）；
8. 绕过 Branch Protection（包括以管理员身份 bypass）；
9. 在未经授权的 Issue/Branch 上开始业务实现、Database / API / Worker / LangGraph / Deployment。

## 13. CI Failure 处理

1. 定位失败 Check 与步骤（Job / Step 名称即错误归属）。
2. 在本地用 §2 的同一命令复现。
3. 修复根因——**不得**通过禁用检查、放宽规则或 `continue-on-error` 让 CI 变绿。
4. 如失败来自上游漏洞披露（pip-audit）：按 §5 分类处理；需要临时风险接受时开单独 Issue 等待用户决定。
5. 如失败来自基础设施（Runner / 网络）：重跑该 Run；连续失败时记录证据并报告，不得静默忽略。

## 14. Emergency Bypass 原则

```text
No automatic emergency bypass
```

- 不存在自动绕过 Branch Protection 或 Required Checks 的机制，也不预先授权任何绕过行为。
- 真正的紧急情况下，绕过只能由**用户本人**显式执行（GitHub 管理员操作），事后必须补记录：原因、范围、补救 PR、复查结果。
- Agent 在任何情况下都不得执行或建议静默绕过。

## 15. Residual Risk（残余风险）

| 风险 | 现状与补偿控制 |
|---|---|
| gitleaks 默认规则集之外的新型 Secret 格式 | GitHub Secret Scanning（平台层）互补；规则集随 gitleaks 升级而更新 |
| gitleaks `useDefault = true` 配置静默漏检（8.30.1 实证） | 不使用自定义配置；引入任何 Allowlist 前必须通过假值正向检出复测（§6 Known Limitation） |
| pip-audit 依赖 OSV 数据的时效性 | Dependabot Alerts 提供第二路漏洞告警；两者互补 |
| SHA-pinned Action 上游被攻破 | Pinning 固定了代码版本；Dependabot 每周检查 Actions 更新并由用户审查；checkout/setup-uv 均为官方或 Astral 官方维护 |
| uv 版本锚定（0.12.0）落后于本地 | 本地与 CI 同版本是刻意选择（可复现优先）；升级走专门 PR |
| Coverage 合并阈值仍 DEFERRED | 沿用 FND-001 决定（RFC-001-DQ-09）：真实生产逻辑落地后激活 80% fail-under，当前不以导入型测试伪造覆盖率 |
| 仓库转 Private 后保护能力受 Free Plan 限制 | 见 §10 Plan 限制记录；届时记录 Unavailable / Reason / Residual Risk / Manual Compensating Control |
