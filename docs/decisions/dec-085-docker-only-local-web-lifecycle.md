# DEC-085 Docker-only local Web 生命周期

## 状态

**Accepted** — 2026-08-28

**Authority:** [Issue #331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331) 的 owner-confirmed L3 contract；实现证据记录在 [MVP-0L L3 review](../reviews/mvp0l-l3-docker-local-web-lifecycle.md)。

**Amends:** [DEC-084](dec-084-apple-silicon-local-ai-web-app-goal.md) 只补充 L3 的可执行本地 Web 生命周期；不改变 Apple Silicon、Docker Desktop、system-default-browser、MBL-first stage order、Provider/Secret、public-contract、migration 或后续 L4/L5/L6 边界。

## Accepted Decision

1. 首发本地 Web 运行面限定为 Apple Silicon macOS（`Darwin arm64`），Docker Desktop 由用户安装和管理；不安装、下载或替换 Docker Desktop。
2. 根目录 `AI Ecommerce Agent.command` 是唯一双击入口，并委托 `scripts/mvp0/local-web`。入口执行有界 preflight，正常打开 Docker Desktop 应用路径，然后轮询 `docker info`；应用路径使用 macOS `open "$app_path"`，轮询次数有界，失败即停止且不创建 Compose 资源。
3. Docker-only local Web 只使用 Compose 的 `local-web` profile 和显式 `--env-file /dev/null` wrapper。profile 精确包含 `postgres`、`api`、`web` 三个服务：PostgreSQL 保持现有 named volume；FastAPI API 仅在 Compose 网络暴露 `8000`，Web 以 nginx 静态构建产物绑定 `127.0.0.1:5173`，并通过 `/api` 代理到 API。API 仅在 PostgreSQL healthy 后启动，Web 仅在 API healthy 后启动；浏览器只在 API、PostgreSQL、Web health 和 loopback Web probe 均通过后打开。
4. local-Web wrapper 为 `MVP0_ADMIN_*`、`MVP0_BUSINESS_*`、`MVP0_CHECKPOINT_*` 与 `MVP0_POSTGRES_PORT` 传入固定的本地 demo interpolation values；调用者 shell 环境不得改变这些值。Compose project 和 volume 只接受经过 scope guard 验证的默认配对，或 repository-prefixed ephemeral project 与精确 `${project}-pg` volume。Docker-only 路径不读取 project `.env`、Secret、Provider 或 model。
5. 默认停止只移除当前 project 的 containers/network/orphans 并保留 `ai-ecommerce-agent-mvp0-postgres-data`；`--ephemeral` 停止或失败清理只使用同一次验证的 project/paired volume，并允许该 scope 的 `down --volumes --remove-orphans`。不允许 raw Compose、广泛 volume 清理或第二个 runtime scope。
6. Backend local image 使用锁定的两阶段 `uv sync --locked`：先 `--no-install-project` 建依赖层，再复制 README/source/migrations/alembic 后执行 locked non-editable project install。Web build/runtime images、Node/npm tuple、OpenAPI generated client 与现有 public contract 保持不变。
7. 既有 host-development lifecycle 保持原样：`mvp0_compose` 仍按历史约定有条件地加载 root `.env`，默认 `preflight` 仍只验证 PostgreSQL；只有 `preflight --local-web` 和 `local-web` 才选择 Docker-only profile/no-`.env` wrapper。

## Non-goals and stop conditions

- 不增加 API health endpoint、HTTP/public contract、migration/schema、dependency 或 lockfile；不修改 Agent UI、L4/L5 Provider、Secret、real-data、public deployment、Intel、native App/WebView、signing/notarization、login/RBAC/multi-user 或 Spider_XHS 行为。
- 这项决定不等于真实 Provider/AI acceptance、clean-Mac acceptance、PR approval、merge 或 Goal completion。任何运行时失败在资源创建后都停止并记录，不重试、不改变 scope、不执行 raw Compose。

## Evidence and relationships

离线证据（RED→GREEN、rendered Compose、shell/static checks、backend/Web tests、lock/API identity、fake lifecycle and cleanup proof）及运行证据记录于 [L3 review](../reviews/mvp0l-l3-docker-local-web-lifecycle.md)。第一次 provider-free `--ephemeral` runtime 在 API image build 因未发布的 `uv==0.12.8` 处于历史 `HOLD`，无服务、health 或 browser 结果；测试先行将官方 pin 修复为 `uv==0.12.6` 后，唯一一次新的 provider-free runtime 通过两镜像构建、PostgreSQL/API/Web health、health 后浏览器、一次有界 `/tasks` 读取、Ctrl-C 130 与精确清理，直接检查的 5173/55432 端口空闲。独立五轴 review 已在 `f831519` 为 `PASS`，fresh Required Checks 为 `12/12`，Ready PR #332 保持 `OPEN`/未合并；L3 仅在该 reviewed record 到达 `main` 后成为 merge-effective/current，L4 仍为 gated/not started。除待授权 merge 外，证据对账、普通 commit/Ready PR 与 checks 已完成；不继承 L2、Fast Lane 或任何 Provider authorization，也不再授权 runtime 重试。

- Goal: [MVP-0L Local AI Web App Delivery Goal](../goals/mvp0-local-ai-web-app-delivery-goal.md)
- Issue: [#331](https://github.com/JettxonHo/ai-ecommerce-agent/issues/331)
- Prior decision: [DEC-084](dec-084-apple-silicon-local-ai-web-app-goal.md)
- Review: [mvp0l-l3-docker-local-web-lifecycle.md](../reviews/mvp0l-l3-docker-local-web-lifecycle.md)
