# MVP Testing Strategy

> **Status: ACCEPTED FOR MVP-0**
> **Authority:** [DEC-010](../decisions/dec-010-three-dimensional-mvp-evaluation-framework.md) · [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) · [DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) · [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) · [DEC-052～070](../decisions/decision-log.md) · [DEC-073](../decisions/dec-073-minimal-observability-and-runtime-operations.md) · [DEC-075](../decisions/dec-075-rapid-mvp0-planning-package-and-goal-activation.md)

本文件定义首个本地端到端演示 MVP 的测试与验收策略。它固化已接受的产品验收基线、RFC-002～007 的运行与契约边界，以及 DEC-055～056 的前端工具、交互与 Web 质量要求；用户已整体接受下列物理布局、命令和证据格式。接受测试策略不代表 Fixture / Suite 已经存在，它们由 Goal Issues 实现和验证。

---

## 1. 质量目标

测试证据必须共同回答：

1. 用户能否完成商品资料到可用 Brief 的任务闭环；
2. 事实、证据、版本、Current Truth、失效和恢复是否可靠；
3. 用户能否在不理解内部 Runtime 的前提下审核、修改、恢复和导出；
4. 新环境能否按权威文档复现相同演示结果。

Rubric 与指标只辅助专业判断，不作为机械评分器。测试优先覆盖代表性路径和关键不变量，不反复堆叠基本不可能发生的防御性变体。

## 2. 固定验收包

四个场景共享一个明确虚构、非管制类的 Anchor SKU：**城市通勤双肩包**。三个资料包只改变与目标行为相关的完整性、冲突和版本，不用于证明真实用户研究或跨品类泛化。

| ID | 场景 | 必须证明的产品行为 |
|---|---|---|
| `fixture-sufficient-v1` | 资料充分的正常任务 | 允许输入可接收；Fact → Insight → Positioning → Human Review → Marketing Brief → Xiaohongshu Brief → Markdown 导出闭环完成；主要结论可追溯。 |
| `fixture-limited-v1` | 资料不足但可运行 | 缺少增强 / 可选资料不阻塞；Hypotheses、Evidence Limitations 与 Insufficient Information 被诚实表达；不为完整率制造事实或 Proof Point。 |
| `fixture-conflict-v1` | 阻断性身份 / 关键事实冲突与恢复 | 进入 Needs Input；有限行动请求展示冲突、影响、来源 / 冲突值、允许动作与恢复范围；补料或确认后从正确阶段恢复，旧失效结果不成为 Current Truth。 |
| `mutation-sufficient-v1` | 基于正常任务的版本与重跑脚本 | Source Version 更新、业务语义编辑、影响预览、陈旧 Review 拒绝、用户确认后的局部重跑，以及导出只使用当前有效版本。 |

表中 ID 是产品策划期的可读逻辑标识，不代表实际文件已经创建。“城市通勤双肩包”及全部资料必须显式标为虚构测试数据。Goal 内独立测试 Issue 按 §8 的物理布局实例化并经 Review；版本变更写入可读 manifest 与变更说明，不使用内容哈希。

## 3. 分层验证

### 3.1 每个代码 PR

- 运行仓库 11 项严格 Required Checks（既有 8 项加 `web / quality`、`web / unit-contract`、`web / chromium`）；`web / change-detection` 是非 Required 的辅助 Job；
- 按变更相关性运行 Unit、Contract、Architecture、Integration、Migration 或 Browser 测试；
- LLM 行为使用确定性替身，不要求真实 Secret、外部网络或 Live Provider；
- 确定性模型验证分为同 Port Contract、注入 SDK Stub 的断网 Adapter Contract、固定资料包 Workflow / Skill Behavior 三层；只覆盖 DEC-054 的一个权威版本代表性分支；
- 只覆盖当前 Issue 的代表性路径和相关错误分支，不把不相关 Live / E2E 场景塞入普通 PR Gate。

### 3.2 持久化与 Workflow

- PostgreSQL 是持久化验收引擎，SQLite 不替代 PostgreSQL Integration / Migration / concurrency 验收；
- 覆盖事务原子性、幂等、版本 Pointer、陈旧 Review、Interrupt / Resume、Cancel、Retry / Rerun、Stage Invalidation 和恢复；
- Checkpoint 不得被测试误当 Business Current Truth。

Fixture 装载方式与故障注入边界按 §8 物理化；RFC-003 / 004 的架构与公共行为已经接受。

### 3.3 Source 与 Retrieval

- **MVP-0 Gate：** 覆盖 JSON / text / TXT / Markdown / CSV、六值 processing、Direct / Exact / PostgreSQL Lexical、server-derived Scope、Evidence Validator 与 atomic commit；不要求 PDF、pgvector、Embedding / Semantic / Hybrid。
- 每 Source 原子登记与处理测试覆盖合法兄弟项不因失败项回滚、六值 processing lifecycle、CSV 合法行 / 有界 row issues，以及 TXT / Markdown 不制造伪部分成功；文本 PDF 的代表性处理进入 MVP-1。
- MVP-0 format-aware lane 验证 Fragment 不跨 Source Version / CSV Record，原文展示与 normalized search text 分离；PDF page Locator 在 MVP-1 补齐。不扩展 OCR、任意办公格式或低概率字符矩阵。
- MVP-0 PostgreSQL Integration 使用同一 authorized candidate relation 验证 Direct、Exact、`tsvector` / GIN 与 bounded `pg_trgm` / GIN 的 scope / eligibility；应用层 post-filter 不作为通过路径。`pgvector` filtered exact NN 属 MVP-1。
- MVP-1 immutable vector generation 测试覆盖 expected / present / missing / extra reconciliation、部分 generation 不切换、原子 current-generation switch、remove / replace / restriction 立即从 eligibility 排除，以及历史 Retrieval Run 保留 generation / profile reference；
- MVP-0 deterministic Planner 测试覆盖 Direct-first、exact identifier 原样保留、Lexical candidate bounds、stable Fragment dedup 与 zero-result `insufficient_information`；MVP-1 再覆盖最多 4 query variants、每通道 20、RRF 60、最多 12 fused、Semantic fallback。这些是行为边界，不计算机械质量总分；
- server-derived Scope 测试验证 Browser / Skill / Provider input 不能扩大 Workspace / Task / Product / Source 范围，所有 channel 在 ranking 前复用同一 SQL authorized candidate relation；公共投影不暴露 vector、raw index、private storage ref、Provider payload 或 rank-as-confidence；
- RetrievalRun / EvidencePackage / DatasetStatistic / Formal Evidence 测试验证 immutable run、reference-based package、完整可计数数据集、Evidence Validator，以及 Domain Version + Formal Evidence Link + Current Truth + audit 原子提交；Candidate / rank / QC 不得提前变成 Formal Evidence 或 approval；
- 固定 Retrieval evaluation 的 MVP-0 Slice 覆盖 exact、CJK lexical、counter-evidence、scope isolation、complete statistic、zero result、remove / replace 与 deterministic order；MVP-1 增加 semantic / hybrid、semantic outage 与 vector generation。Scope / stale / Top-K extrapolation / fabricated zero-result / exact identifier / atomic Formal Evidence 始终是硬门禁；Relevance 不合成机械总分；
- degraded behavior 必须传播 limitation，不扩大 Scope、不使用 incomplete / unsafe generation。没有安全兼容 generation 时返回 temporary unavailable / actionable recovery，不允许 Frontend 模拟服务端终态；
- 首个 Goal 不测试或实现 baseline ANN、LLM Query Rewrite、Reranker、多 Embedding Provider 或外部 Search / Vector Service。若固定评测后来证明需要，必须通过独立提案和 before / after evidence 解锁。

### 3.4 前端与端到端

- 前端静态与构建基线使用 Prettier、ESLint、`tsc --noEmit` 与 Vite Production Build；
- Unit / Module / State Transition 使用 Vitest + React Testing Library / `user-event`；类型化 Client Contract 使用注入式 Typed Transport / Fixture；
- 组件与状态转换测试覆盖输入、进度、Needs Input 有限行动请求、Review、恢复、结果和导出；
- 代表性 Claim Integrity 行为覆盖 Verified Fact → Proof Point、Documented Claim 保持待验证、无依据声明被排除但 Task 继续，以及策略无可信替代时进入 Needs Input；不建设法规、法域、敏感词变体或合规总分矩阵；
- Source 生命周期覆盖从当前 Task 有效资料集可逆移除 / 替换、影响预览、陈旧 Review、Current Truth 失效和确认式局部重跑；产品 E2E 不声称或模拟尚未实现的物理永久删除；
- API Contract 测试验证前后端状态、错误和版本映射；
- API Contract 测试覆盖 `/api/v1` 窄 Resource / typed Command 分离、首次异步 `202` + `Location`、同 Key 同输入 `200` 重放同一 Receipt、同 Key 不同输入 `409`、真正 stale revision `409`、失败 Run 的 `200` Representation，以及活动轮询在等待用户 / 审核 / 恢复和终态停止；不增加通用 Action、Push Transport 或 ETag 双协议矩阵；
- API Contract 测试覆盖同步 Task 创建首次 `201` / 重放 `200` 同一 Task、server-bounded 最近列表、revision-bound Summary / Overview Capability、Needs Input supersession、Source Preview / Confirm basis conflict、Cancel requested、Resume / Rerun 创建新 Run identity，以及 Manual Recovery 不暴露内部 Checkpoint / Lease / fencing；
- API / Frontend Contract 测试覆盖不可变 Marketing / Xiaohongshu Brief Current Truth、semantic-group Comparison、typed revise 影响、Export Preview basis conflict、首次 `201` / 重放 `200` 同一 Markdown Snapshot，以及历史 Snapshot 不被误标当前；
- Problem Contract 只覆盖 DEC-065 有限 RFC 9457 type / action 目录的代表性分支，并验证 Needs Input、waiting Review、manual recovery 与 failed Run 是 `200` Resource state；不展开内部异常或无客户端动作的防御矩阵；
- fixed-workspace 测试验证 Browser 不能选择 Workspace、跨 scope identity 为 `404`、默认 loopback / same-origin、CORS closed 与 state-changing Origin 匹配；不增加 Login、Token、RBAC、Tenant 或公网安全矩阵；
- Browser E2E 使用 Playwright Chromium 与确定性本地 API / Model Substitute，按固定验收包覆盖正常闭环、冲突恢复和 mutation script；
- Browser E2E 覆盖 `/tasks` 空状态、创建 / 最近任务返回稳定深链、Task 摘要下一步动作和暂时读取失败；不增加搜索、分页、批量、归档或 Dashboard 矩阵；
- 相关前端 PR 运行受影响的关键 E2E，Release Candidate 运行完整固定 Browser E2E；普通测试不得访问真实 Provider；
- Module / State Transition 测试覆盖 WorkbenchProjection 的模式优先级、stale snapshot、Capability / Intent、轮询停止，以及 Mutation 成功后刷新而非乐观 Current Truth；
- Review 测试覆盖 latest-buffer 串行 Save、成功 revision 链、歧义编辑意图、Save / Flush / Conflict 阻止 Submit，以及 Stale / Superseded 保留缓冲；
- Review Contract / Integration 测试覆盖不可变 Package、full-snapshot Draft save、各 Outcome 的不同副作用、Submit 对 Review Decision / Approved Strategy / Current Truth / Audit / Idempotency / 唯一 Durable Resume Work Intent 的原子性、首次 `201` / 重放 `200` 同一 continuation，以及客户端不发送第二个 Resume；
- 不可信文本使用普通 React Text Rendering；若出现已接受的 Markdown Preview，覆盖 Raw HTML 关闭和安全 Link Protocol；不测试不存在的泛化 Sanitizer 平台；
- 少量代表性 `@axe-core/playwright` A / AA 检查与人工键盘、Focus、Announcement、200% Text Resize、等价 320 CSS px / 400% Zoom Reflow 共同构成无障碍证据；自动扫描不替代人工判断；
- 正式支持当前稳定 Desktop Chrome；Edge / Firefox / Safari 为 Best-effort。Firefox / WebKit、Visual Regression 和手机矩阵不机械加入首个 Goal；
- 首个完整纵向切片建立固定本地性能 Profile，Release Candidate 同 Profile 复测。输入卡顿 / 丢失、轮询整页闪烁、无界 Fetch / Render、Focus 丢失或 Evidence 阻塞主操作是 Blocking Finding；先 Profile 再优化，不使用无实现基线的机械分数。

### 3.5 真实 Provider Smoke

- 仅在 Release Candidate 使用 `fixture-sufficient-v1` 执行一次完整端到端 Smoke；
- Bootstrap 只选择 Credential Reference，Infrastructure Adapter 在自身边界解析环境 Secret；Secret 不写入仓库、Fixture、日志或导出；
- Live Smoke 不进入普通 PR Required Checks；
- Live Smoke 使用 DEC-052～054 接受的 OpenAI Responses API / `gpt-5.6-terra`、Version Tuple、Profile、有界 Recovery 与最小证据；仅在显式 `live` + `RUN_LIVE_MODEL_SMOKE=1` + Secret + 已接受版本同时满足时人工执行；
- 只运行一次 `fixture-sufficient-v1` 完整闭环，不增加 Live Edge-case Matrix；失败证据保留并阻塞 Release Candidate，修复后创建新 Run，不覆盖失败或降低 Gate；
- 验收目标是契约、闭环和诚实证据行为，不要求每次生成完全相同措辞，也不使用语言流畅度总分。

## 4. 行为硬门禁

Goal 完成前必须同时满足：

- 所有 Required Checks 和适用确定性测试通过；
- 固定验收包的 Required Behaviors 全部通过；
- 伪造 Source 或可用 Locator 数量为零；
- 陈旧 Review 拒绝、Current Truth、失效、恢复与确认式局部重跑结果正确；
- 必需语义组存在，或诚实标记资料不足 / 不适用；
- Claim / Fact / Proof Point 未越权升格，无依据高风险声明不进入 Current Brief，有诚实替代时 Task 不被过度阻断；
- 从当前 Task 移除的 Source 不再支撑 Current Truth，界面未把可逆移除伪装为物理永久删除；
- 跨 Task / Scope / Product leakage、stale / unavailable / non-current-generation candidate、Top-K frequency extrapolation、zero-result fabrication 与 Validator 前 Formal Evidence 数量均为零；
- 用户可以从最小最近任务入口通过稳定深链返回持久 Task；
- 当前有效 Marketing Brief 与 Xiaohongshu Brief 的 Markdown Export Snapshot 与版本引用一致；
- Release Candidate Live Smoke 通过；
- Critical / Blocking 缺陷为零。

失败场景、已知限制和未解决风险必须公开记录。不得隐藏失败测试，也不得通过降低标准或扩大忽略范围让 Gate 变绿。

## 5. 人工可用性验收

人工验收者从复合主 Persona 视角执行固定正常任务和必要恢复步骤，并判断：

- 是否无需开发者解释内部实现即可完成任务；
- 是否理解主要结论、证据、假设、限制与冲突；
- 是否能完成审核、编辑、影响确认、恢复和导出；
- Marketing Brief 与 Xiaohongshu Brief 是否可用于后续内容策划。

最终记录为 `PASS` 或 `FAIL`，并附理由、主要人工修改、未解决限制和阻塞 Finding。辅助 Checklist 不转换为加权总分，也不自动接受 Goal。

## 6. 观察指标

以下指标在演示中记录，用于后续比较和 Beta 研究，但首个 Goal 不设置缺少真实基线的机械发布阈值：

- 关键结论人工接受与修改情况；
- 从提交资料到可用 Brief 的总耗时；
- 补充资料轮次、交互步骤和人工修改量；
- 与人工流程比较的潜在节省时间。

固定验收包中的事实可追溯、无依据事实、语义完整和下游失效作为行为不变量处理，不并入加权总分。

## 7. Markdown 导出验收

当前有效的 Marketing Brief 与 Xiaohongshu Brief 必须能分别导出为 UTF-8 Markdown，并包含 DEC-048 规定的 Task、版本、上游、语义组、假设、限制、风险、证据与导出时间上下文。失效、被取代或部分提交对象不得作为当前结果导出。

首个 Goal 不验收用户侧 PDF 或 JSON 文件导出。API JSON 属于 RFC-004 公共契约，不与用户导出格式混用。

## 8. MVP-0 物理测试计划

### 8.1 Fixture authority

唯一仓库级验收资料权威计划为：

```text
tests/fixtures/mvp0/
  README.md                         fictional-data notice and use rules
  manifest.yaml                     scenario IDs, readable versions, expected behaviors
  sufficient-v1/                    JSON/text/TXT/Markdown/CSV source set
  limited-v1/                       intentionally limited source set
  conflict-v1/                      blocking identity/fact conflict source set
  mutation-sufficient-v1/           readable mutation instructions and changed sources
  expected/                         semantic-group and behavior expectations, not exact prose snapshots
```

- Backend、Browser E2E 与人工验收都引用同一 manifest，不复制三套业务数据；
- expected 文件描述必需语义组、证据引用、限制、状态与动作，不固定完整模型措辞；
- Fixture 不包含真实个人资料、真实评论、Secret、Provider payload 或外部下载依赖；
- 版本身份使用可读 ID 与 manifest，不新增内容哈希；
- MVP-0 不放入 PDF、图片、Embedding 或 Semantic expected data。

### 8.2 Backend commands

既有命令保持权威：

```text
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run lint-imports
uv run pytest -m unit
uv run pytest -m contract
uv run pytest -m architecture
uv run pytest -m "not live and not slow"
uv build
```

生产持久化进入后新增并在 `apps/backend/README.md` / CI 复用：

```text
uv run pytest -m integration
uv run pytest -m "integration and migration"
uv run pytest -m "integration and concurrency"
uv run pytest -m e2e
uv run pytest -m evaluation
```

若 pytest 物理 marker 不能表达子类别，Issue 可以采用明确测试路径而不新增泛化 marker；命令必须在 PR 中写实，不把不存在的命令标为已通过。真实 PostgreSQL Test Service 由 Development Plan 的本地栈提供，每个 suite 使用隔离 Database / Schema 与确定性清理。

### 8.3 Frontend commands

DEC-055 已冻结 `npm run dev / build / preview`。Frontend Foundation Issue 需一次性冻结并在 `apps/web/README.md` 与 CI 复用以下窄脚本名：

```text
npm run format:check
npm run lint
npm run typecheck
npm run test:unit
npm run test:contract
npm run test:e2e
npm run build
```

不创建平行的第二 formatter / linter / test runner。`test:e2e` 默认使用确定性本地 API / Model Substitute；Live Provider 不由 Browser Suite 启动。

### 8.4 Required check evolution

- 现有 11 项稳定 Gate 在整个 Goal 保持必需（既有 8 项加 3 项 Web checks）；不得改名或关闭以规避失败。`web / change-detection` 仅负责 bounded path detection，不是 Required Check。
- Backend 生产逻辑首次进入时，在独立 CI Issue 启用 branch coverage 80% Gate；关键业务不变量仍需行为测试，覆盖率不能代替。
- OpenAPI lint / generated-client clean diff、真实 PostgreSQL Integration 和 Frontend checks 按其 foundation Issue 加入稳定 Required Checks；MVP0-036 已将 Web foundation 的 quality / unit-contract / Chromium shell smoke 加入稳定 Required Checks，并证明本地命令等价。Web workflow 对无关 diff 保留稳定上下文并执行 checkout-free no-op，对受影响 diff 与手动 dispatch 执行真实 suite。
- Integration / Browser / Live 不机械塞入每个无关 PR；受影响测试按 Task Contract 执行，完整矩阵在 Release Candidate 执行。

### 8.5 Evidence records

每个 PR 在描述中记录命令、退出状态与适用范围；CI 是合并证据。Release Candidate 在 `docs/reviews/` 保存一个可读的 Release Evidence Summary，包含：Commit、环境版本、fixture version、deterministic suites、Migration、concurrency / failure injection、Browser 截图索引、人工可用性、一次 Live Smoke、失败与限制。日志中只保存 RFC-007 接受的 allowlisted correlation 信息。

### 8.6 Migration / concurrency / failure matrix

最小矩阵必须覆盖：

- fresh upgrade、one-step upgrade、失败回滚 / forward repair、旧进程 compatibility refusal；
- two-worker claim、Lease takeover / higher fencing、stale worker commit rejection、concurrent review CAS、duplicate command replay；
- Checkpoint 与 Business Current Truth 不一致的七动作 reconciliation；
- Provider timeout / malformed structured output / bounded recovery exhaustion；
- Source partial acceptance、CSV row issues、zero result、removed / replaced source exclusion；
- API idempotency conflict、stale revision、Needs Input、cancel / resume / rerun；
- Browser reload / deep link / polling stop / stale review / export basis conflict。

每类先覆盖代表性分支与关键不变量，不为基本不可能的排列组合扩展矩阵。

### 8.7 Deferred beyond MVP-0

- text PDF、Embedding / Semantic / Hybrid、pgvector、ANN、Reranker / rewrite；
- 物理永久删除 / Hold 平台、完整跨版本 Migration 矩阵；
- Firefox / WebKit、手机设备矩阵、Visual Regression；
- Observability Dashboard、Beta 用户样本、埋点与机械性能阈值。

## 9. 停止条件

遇到下列情况时停止受影响工作并升级给 Sol / 用户：

- 测试暴露 Accepted Decision / RFC 冲突；
- 核心事务、Resume、幂等、Current Truth 或证据一致性无法满足；
- 必须降低验收标准、扩大 MVP 或更换已接受技术方案才能继续；
- 需要真实凭证、破坏性数据操作、不可逆迁移或其他人工 Gate。

## 10. 完成边界

本文随快速 MVP-0 策划包被接受后可更新为 `ACCEPTED FOR MVP-0`。物理 Fixture、测试脚本与 CI Job 仍由 Goal 内独立 Issues 创建；在对应 PR 合并前不得声称它们已存在或已通过。DEC-048、DEC-058～062 的产品验收基线已经 Accepted；当前 Goal 仍未激活。
