# MVP-0L L2 最小持久化复核

## 结论与边界

**事实：** Issue [#329](https://github.com/JettxonHo/ai-ecommerce-agent/issues/329) 是 MVP-0L 的 L2「Minimum Source/Brief persistence acceptance and reconciliation」Stage。本文记录从 reviewed `main` 开始的持久化 characterization、一次性 provider-free runtime 及其当前真相文档复核；它不批准或合并 PR。代码/测试的精确 follow-up head 为 `2c1c1d39c44b77803f587785f07f741f8374ef29`，基线为 `origin/main@ae3c87b6661c6741ec87c73f255be220afd32e4e`（PR #328 merge commit）。

**事实：** PR [#330](https://github.com/JettxonHo/ai-ecommerce-agent/pull/330) 在本次文档提交期间仍为 `OPEN`、未合并；其 follow-up code/test head `2c1c1d3` 已完成独立五轴复核并获 `PASS`，fresh Required Checks 为 `12/12 successful`。因此 L2 的证据与复核结论为 `PASS`，但 L2 只有在该 PR 经复核闭合并到达 `main` 后才 merge-effective；L3 继续 gated。本文不替实现者批准、合并或关闭 Issue。

**历史事实：** 早先一次运行记录为 `6 passed / 1 failed`，分类为 `TEST_FIXTURE_PRECONDITION_MISMATCH`；此前两个临时 #329 clone 与未提交的八路径 diff 已丢失，主 checkout 未受影响。该记录没有建立产品缺陷，也没有授权生产修复；本次修正只恢复测试保护的不变量。

**配置事实：** 使用 Python 3.12 解析 `/Users/ketchup/.codex/agents/luna-worker.toml`，仅记录 `CONFIG_VERIFIED`：精确 `luna-worker` / `gpt-5.6-luna` / `max`。运行时没有暴露实例身份，因此不作 runtime identity claim；未使用 Terra 或默认回退。

## 允许范围与路径证据

**累计事实：** PR #330 的累计实际 diff 恰为以下八个路径；其中第一个是 test-only follow-up，其余七个是本次 current-truth 文档 reconciliation：

1. `apps/backend/tests/integration/test_task_http_postgres.py`
2. `AGENTS.md`
3. `README.md`
4. `apps/web/README.md`
5. `docs/goals/mvp0-local-ai-web-app-delivery-goal.md`
6. `docs/handoffs/implementation-readiness.md`
7. `docs/reviews/mvp0l-l1-needs-input-backend.md`
8. `docs/reviews/mvp0l-l2-minimum-persistence.md`（本文）

**本次 follow-up 事实：** 文档提交只修改上述第 2–8 项七个路径；相对 follow-up 前的 `2c1c1d3`，没有修改测试、production source、migration/schema、OpenAPI/generated client、public contract、CSS、Compose/lifecycle script、Provider、Secret、`.env`、dependency/lockfile 或 Agent UI。Issue #81 与 #82 保持 open 且未写入。

没有启动 L3/L4/L5/Agent UI/L6。owner 确认的 MBL-first 顺序仍为 **L2 → L3 → L4 → L5 → Agent UI → L6**；Agent UI 只有在真实 AI MBL 通过后才可进入其后续生产合同。

## Source-level fixture proof

**事实：** 编辑前先对当前生产确定性管线做离线/source-level 精确字符串证明，没有提出 behavioral RED。v2 fixture 为 `410` 字节，带有明确的虚构修订说明：`资料修订 v2：新增可逆运营备注，核心商品事实保持不变。`。Python 3.12 扫描证明以下六组 canonical markers 均存在，且 v2 只增加可逆运营备注、保留核心商品事实：

- identity：`fixture-sufficient-v1`、`anchor-city-commuter-backpack`、`CBP-SYN-001`、`城市通勤双肩包`；
- use：`通勤`；
- capacity：`约 18 升`；
- laptop：`14 英寸`；
- weather：`防泼水`；
- source：`source-sufficient-product-v1`、`product.json`、`direct_source`。

这只是 source/fixture 充分性证据，不把字符串扫描写成行为通过或 Provider 证明。

## 测试结构、阻塞发现与行为证据

**事实：** 集成文件 collection 仍为 **6 tests**。没有新增第七个测试；follow-up 只在原有 characterization 中恢复 stale revision/idempotency fence 覆盖，将 `test_generate_result_is_durable_atomic_and_revision_fenced` 扩展/替换为 `test_anchor_persistence_survives_recomposition_and_newer_cycle`，覆盖一个完整 L2 单 Task 生命周期。

**历史 Review finding：** 原 expanded test 曾移除受保护的 stale assertions：输入 revision 前进后，`expectedInputRevision=0` 的新 generate、旧 `result-key-1` replay 与旧 `confirm-key-1` replay 必须返回 `409`，并且 recomposition 后仍不得成功。该 finding 是测试保护缺口，不是生产行为缺陷。

**事实 — test-only resolution at `2c1c1d3`：**

- v2 input 保存后，stale `result-key-stale-v2` generation、旧 `result-key-1` replay 与旧 `confirm-key-1` replay 均返回 `409`；同一时点 current truth 仍为 v1 confirmed body；
- 新 v2 generation/confirmation 成功推进到 `inputRevision/resultRevision = 1`；
- recomposition 后，新周期 keys/revisions 可 replay；旧 `result-key-1` 与 `confirm-key-1` 以及 revision `0` replays 仍返回 `409`，且 current truth 不变；
- 原有 Marketing 与 Xiaohongshu export snapshot rows、metadata、identifiers 与 UTF-8 Markdown bytes 在新周期后保持不变。

该 characterization 对同一个 fictional Anchor SKU 证明：

1. 保存 primary input 后，新的 application composition 可读回输入；生成的 Marketing 与 Xiaohongshu 结果在 recomposition 前后均保持一致，并可用原 idempotency key replay。
2. 确认两个结果投影（Marketing / Xiaohongshu）后，新的 composition 可读回 `confirmed` current truth；生成与确认命令 replay 保持同一结果。
3. 分别创建 Marketing 与 Xiaohongshu export snapshots；replay 返回同一 snapshot，下载内容为 UTF-8 Markdown，且保留媒体类型、换行与确认文本。
4. 保存 materially newer 输入（明确 `资料修订 v2`），使 revision 从 `0` 前进到 `1`，生成并确认新的 current truth；新的 composition 可 replay 新周期。
5. 新周期之后再次下载旧 Marketing/Xiaohongshu snapshots，并比较数据库完整 snapshot row 与原始 bytes；两者 identifiers、metadata、content 均不可变。

没有伪造 RED，也没有为满足测试修改生产行为。该文件证明的是既有 HTTP/PostgreSQL 持久化表面的最小连贯行为，不是完整 Source/Review 平台或 Agent runtime。

## 离线与一次性运行证据

**离线检查事实：** 新克隆缺少 Web 依赖时，按 owner 授权仅执行一次：

```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

命令成功安装 227 packages；随后 shell wrapper 的变量命名错误发生在命令完成之后，未重试。`apps/web/package.json` 前后 SHA-256 均为 `580d9f7c95db0046516befafba78b2412290a459ae794aecb0b23c0ca427de429`，`apps/web/package-lock.json` 前后均为 `521592eae80e4fc6db29eb4af2f45fdba0b8a8f12a88122fea4e09a161056530`，tracked dependency/lock diff 为空。

离线/static/collection 检查通过：source marker proof、6-test collection、Ruff format/check（受影响测试）、targeted Pyright（`0 errors, 0 warnings, 0 informations`）、Web Prettier、ESLint、TypeScript、`api:check`、unit（8 files / 120 passed）、contract（10 files / 50 passed）、Vite production build 与 `git diff --check`。没有其它 dependency command。

**一次性 runtime 事实：** 只使用 repository wrapper、Node 24 prefix 与精确配对的 ephemeral project/volume：

```text
PATH=/opt/homebrew/opt/node@24/bin:$PATH ./scripts/mvp0/demo --ephemeral
MVP0_RUN_TASK_HTTP_POSTGRES=1 PATH=/opt/homebrew/opt/node@24/bin:$PATH uv run --project apps/backend --locked pytest -q apps/backend/tests/integration/test_task_http_postgres.py
```

wrapper 生成 project `ai-ecommerce-agent-mvp0-ephemeral-260827115305-28302-00226` 与 paired volume `ai-ecommerce-agent-mvp0-ephemeral-260827115305-28302-00226-pg`，Browser URL readiness 到达；集成选择只运行一次，结果为 **6 passed in 1.41s**。未运行 raw Compose、第二 scope、retry/recovery、Provider/model、Secret 或 `.env` 操作。终止只发送一次 Ctrl-C；guarded cleanup 只执行一次。随后按 emitted names 验证 container、network、paired volume 均不存在，端口 `8000`、`5173`、`55432`、`55433` 均 free；未读取、创建、重命名或删除 protected/default/historical volume，Docker 保持初始状态。

## Validation and current-truth gate

**事实：** exact follow-up code/test head `2c1c1d39c44b77803f587785f07f741f8374ef29` 的 fresh Required Checks 为 **12/12 successful**（0 failing, 0 cancelled, 0 skipped）。独立五轴复核在 durable resolution comment [#5438696727](https://github.com/JettxonHo/ai-ecommerce-agent/pull/330#issuecomment-5438696727) 中为 `PASS`：correctness（含 stale revision/idempotency fences）、readability、architecture、security 与 proportional performance 均通过。

**事实：** Issue #318 / PR #328 已使 L1 merge-effective/current。Issue #329 / PR #330 的 provider-free runtime 与独立五轴 review 在上述精确 code/test head 均为 `PASS`；PR #330 在本文提交时仍 `OPEN`、未合并，所以 L2 尚未 merge-effective，且 L3 继续 gated。文档提交只完成 current-truth reconciliation，不改变生产行为。

本次不主张 Provider acceptance、真实 AI、Agent UI production、public deployment、完整 Source/Review 平台或产品缺陷修复；不授权新的 migration、public contract、generated client、dependency/lockfile、Provider、Secret、`.env`、Docker/PG/API/Web 运行时或其它 Stage。Fast Lane 的终态 `GOAL_BLOCKED`、P5 的 `P5_REUSE_FROZEN`、PR #299 `OPEN`/未合并及 `.env`/Secret 边界均保持不变。

若后续独立 Review 或 main closure 发现证据不足，应按 Issue 合同停止并返回 exact gap；不得扩大路径、重跑 runtime 或静默修复 production。
