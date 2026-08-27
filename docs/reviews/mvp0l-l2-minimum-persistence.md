# MVP-0L L2 最小持久化复核

## 结论与边界

**事实：** Issue [#329](https://github.com/JettxonHo/ai-ecommerce-agent/issues/329) 是 MVP-0L 的 L2「Minimum Source/Brief persistence acceptance and reconciliation」Stage。本文记录一次全新的、隔离克隆中的实现与运行证据；它不是独立五轴 Review，也不批准或合并 PR。精确复核基线为 `origin/main@ae3c87b6661c6741ec87c73f255be220afd32e4e`（PR #328 merge commit），分支为 `codex/mvp0l-l2-minimum-persistence-reconciliation`。

**事实：** 之前一次运行记录为 `6 passed / 1 failed`，分类为 `TEST_FIXTURE_PRECONDITION_MISMATCH`；此前两个临时 #329 clone 与未提交的八路径 diff 已丢失，主 checkout 未受影响。没有建立产品缺陷证据，也没有授权生产代码变更。本次是 owner comment 中授权的唯一一次修正重建；若持久化不变量失败，合同要求停止并回报精确缺口。

**配置事实：** 使用 Python 3.12 解析 `/Users/ketchup/.codex/agents/luna-worker.toml`，仅记录 `CONFIG_VERIFIED`：精确 `luna-worker` / `gpt-5.6-luna` / `max`。运行时没有暴露实例身份，因此不作 runtime identity claim；未使用 Terra 或默认回退。

## 允许范围

实际 diff 只包含以下八个路径：

1. `apps/backend/tests/integration/test_task_http_postgres.py`
2. `AGENTS.md`
3. `README.md`
4. `apps/web/README.md`
5. `docs/goals/mvp0-local-ai-web-app-delivery-goal.md`
6. `docs/handoffs/implementation-readiness.md`
7. `docs/reviews/mvp0l-l1-needs-input-backend.md`
8. `docs/reviews/mvp0l-l2-minimum-persistence.md`（本文，新文件）

没有修改 production source、migration/schema、OpenAPI/generated client、public contract、CSS、Compose/lifecycle script、Provider、Secret、`.env`、dependency/lockfile 或 Agent UI；Issue #81 与 #82 保持 open 且未写入。没有启动 L3/L4/L5/L6。

## Source-level fixture proof

**事实：** 编辑前先对当前生产确定性管线做离线/source-level 精确字符串证明，没有提出 behavioral RED。实际 v2 fixture 为 `410` 字节，使用显式虚构修订说明：`资料修订 v2：新增可逆运营备注，核心商品事实保持不变。`。Python 3.12 扫描证明以下六组 canonical markers 均存在，且 v2 只增加可逆运营备注、保留核心商品事实：

- identity：`fixture-sufficient-v1`、`anchor-city-commuter-backpack`、`CBP-SYN-001`、`城市通勤双肩包`；
- use：`通勤`；
- capacity：`约 18 升`；
- laptop：`14 英寸`；
- weather：`防泼水`；
- source：`source-sufficient-product-v1`、`product.json`、`direct_source`。

这只是 source/fixture 充分性证据，不把字符串扫描写成行为通过或 Provider 证明。

## 测试结构与行为证据

集成文件仍然 collection 为 **6 tests**。本次没有新增第七个测试，而是扩展/替换原有 `test_generate_result_is_durable_atomic_and_revision_fenced` 为 `test_anchor_persistence_survives_recomposition_and_newer_cycle`，使一个已有的 durable atomic/revision-fenced characterization 覆盖完整 L2 单 Task 生命周期。

该 characterization 对同一个 fictional Anchor SKU 证明：

1. 保存 primary input 后，新的 application composition 可读回输入；生成的 Marketing 与 Xiaohongshu 结果在 recomposition 前后均保持一致，并可用原 idempotency key replay。
2. 确认两个结果投影（Marketing / Xiaohongshu）后，新的 composition 可读回 `confirmed` current truth；生成与确认命令 replay 保持同一结果。
3. 分别创建 Marketing 与 Xiaohongshu export snapshots；replay 返回同一 snapshot，下载内容为 UTF-8 Markdown，且保留媒体类型、换行与确认文本。
4. 保存 materially newer 输入（明确 `资料修订 v2`），使 `inputRevision/resultRevision` 从 `0` 前进到 `1`，生成并确认新的 current truth；新的 composition 可 replay 新周期。
5. 新周期之后再次下载旧 Marketing/Xiaohongshu snapshots，并比较数据库完整 snapshot row 与原始 bytes；两者 identifiers、metadata、content 均不可变。

没有伪造 RED，也没有为满足测试修改生产行为。该文件证明的是既有 HTTP/PostgreSQL 持久化表面的最小连贯行为，不是完整 Source/Review 平台或 Agent runtime。

## 离线与一次性运行证据

**离线检查事实：** 新克隆缺少 Web 依赖时，仅执行一次 owner 授权命令：

```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

命令成功安装 227 packages；随后 shell wrapper 的变量命名错误发生在命令完成之后，未重试。`apps/web/package.json` 前后 SHA-256 均为 `580d9f7c95db0046516befafba78b2412290a459ae794aecb0b23c0ca427de429`，`apps/web/package-lock.json` 前后均为 `521592eae80e4fc6db29eb4af2f45fdba0b8a8f12a88122fea4e09a161056530`，tracked dependency/lock diff 为空。

离线/static/collection 检查通过：source marker proof、6-test collection、Ruff format/check（受影响测试）、targeted Pyright（0 errors）、Web Prettier、ESLint、TypeScript、`api:check`、unit（8 files / 120 passed）、contract（10 files / 50 passed）、Vite production build 与 `git diff --check`。没有其它 dependency command。

**一次性 runtime 事实：** 只使用 repository wrapper、Node 24 prefix 与精确配对的 ephemeral project/volume：

```text
PATH=/opt/homebrew/opt/node@24/bin:$PATH ./scripts/mvp0/demo --ephemeral
MVP0_RUN_TASK_HTTP_POSTGRES=1 PATH=/opt/homebrew/opt/node@24/bin:$PATH uv run --project apps/backend --locked pytest -q apps/backend/tests/integration/test_task_http_postgres.py
```

wrapper 生成 project `ai-ecommerce-agent-mvp0-ephemeral-260827112255-17309-00806` 与 paired volume `ai-ecommerce-agent-mvp0-ephemeral-260827112255-17309-00806-pg`，Browser URL readiness 到达；集成选择只运行一次，结果为 **6 passed in 5.16s**。未运行 raw Compose、第二 scope、retry/recovery、Provider/model、Secret 或 `.env` 操作。终止只发送一次 Ctrl-C；guarded cleanup 只执行一次。随后按 emitted names 验证 container、network、paired volume 均不存在，端口 `8000`、`5173`、`55432`、`55433` 均 free；未读取、创建、重命名或删除 protected/default/historical volume，Docker 保持初始状态。

## Current Truth 与后续 Gate

Issue #318 / PR #328 已为 merge-effective 的 L1；本 L2 evidence 使当前文档如实记录 Issue #329 的一次 provider-free runtime `PASS`，但 **independent five-axis review、Ready PR、merge 与 fresh Required Checks 尚未开始/尚未通过**，因此 L2 尚未 merge-effective，L3 继续 gated。实现者不批准、不合并、不关闭 Issue。

本次结果不主张 Provider acceptance、真实 AI、public deployment、完整 Source/Review、Agent-first Figma UI 或产品缺陷修复。若后续独立 Review 发现证据不足，应按 Issue 合同停止并返回 exact gap；不得扩大路径、重跑 runtime 或静默修复 production。
