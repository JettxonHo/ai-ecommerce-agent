# MVP Testing Strategy

> **Status: PARTIAL — product acceptance baseline accepted; implementation tooling and executable suites pending RFC / Goal**
> **Authority:** [DEC-010](../decisions/dec-010-three-dimensional-mvp-evaluation-framework.md) · [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) · [DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) · [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) · [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md) · [DEC-053](../decisions/dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md) · [DEC-054](../decisions/dec-054-adapter-secret-payload-boundary-and-deterministic-model-verification.md) · [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md) · [DEC-056](../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md) · [DEC-058](../decisions/dec-058-fictional-anchor-sku-acceptance-fixture-strategy.md) · [DEC-059](../decisions/dec-059-targeted-needs-input-action-request-model.md) · [DEC-060](../decisions/dec-060-evidence-bound-claim-integrity-and-proportional-compliance-boundary.md) · [DEC-061](../decisions/dec-061-task-scoped-private-material-and-reversible-removal.md) · [DEC-062](../decisions/dec-062-minimal-recent-task-index-and-stable-deep-links.md) · [DEC-063](../decisions/dec-063-contract-first-semantic-concurrency-and-durable-api-acceptance.md)

本文件定义首个本地端到端演示 MVP 的测试与验收策略。它当前固化已接受的产品验收基线、DEC-052～054 / RFC-006 的模型契约，以及 DEC-055～056 的前端工具、交互与 Web 质量验证边界；不授权业务实现，也不提前冻结公共接口、Fixture 或未实例化的测试步骤。

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

表中 ID 是产品策划期的可读逻辑标识，不代表实际文件已经创建。“城市通勤双肩包”及全部资料必须显式标为虚构测试数据。具体资料、expected output 和物理目录由 Goal 内独立测试 Issue 实例化并经 Review；版本变更写入变更说明，不使用内容哈希。

## 3. 分层验证

### 3.1 每个代码 PR

- 运行仓库既有 8 项 Required Checks；
- 按变更相关性运行 Unit、Contract、Architecture、Integration、Migration 或 Browser 测试；
- LLM 行为使用确定性替身，不要求真实 Secret、外部网络或 Live Provider；
- 确定性模型验证分为同 Port Contract、注入 SDK Stub 的断网 Adapter Contract、固定资料包 Workflow / Skill Behavior 三层；只覆盖 DEC-054 的一个权威版本代表性分支；
- 只覆盖当前 Issue 的代表性路径和相关错误分支，不把不相关 Live / E2E 场景塞入普通 PR Gate。

### 3.2 持久化与 Workflow

- PostgreSQL 是持久化验收引擎，SQLite 不替代 PostgreSQL Integration / Migration / concurrency 验收；
- 覆盖事务原子性、幂等、版本 Pointer、陈旧 Review、Interrupt / Resume、Cancel、Retry / Rerun、Stage Invalidation 和恢复；
- Checkpoint 不得被测试误当 Business Current Truth。

最终工具、命令、Fixture 装载方式与故障注入边界在 RFC-003 / 004 接受后补充。

### 3.3 前端与端到端

- 前端静态与构建基线使用 Prettier、ESLint、`tsc --noEmit` 与 Vite Production Build；
- Unit / Module / State Transition 使用 Vitest + React Testing Library / `user-event`；类型化 Client Contract 使用注入式 Typed Transport / Fixture；
- 组件与状态转换测试覆盖输入、进度、Needs Input 有限行动请求、Review、恢复、结果和导出；
- 代表性 Claim Integrity 行为覆盖 Verified Fact → Proof Point、Documented Claim 保持待验证、无依据声明被排除但 Task 继续，以及策略无可信替代时进入 Needs Input；不建设法规、法域、敏感词变体或合规总分矩阵；
- Source 生命周期覆盖从当前 Task 有效资料集可逆移除 / 替换、影响预览、陈旧 Review、Current Truth 失效和确认式局部重跑；产品 E2E 不声称或模拟尚未实现的物理永久删除；
- API Contract 测试验证前后端状态、错误和版本映射；
- API Contract 测试覆盖 `/api/v1` 窄 Resource / typed Command 分离、首次异步 `202` + `Location`、同 Key 同输入 `200` 重放同一 Receipt、同 Key 不同输入 `409`、真正 stale revision `409`、失败 Run 的 `200` Representation，以及活动轮询在等待用户 / 审核 / 恢复和终态停止；不增加通用 Action、Push Transport 或 ETag 双协议矩阵；
- Browser E2E 使用 Playwright Chromium 与确定性本地 API / Model Substitute，按固定验收包覆盖正常闭环、冲突恢复和 mutation script；
- Browser E2E 覆盖 `/tasks` 空状态、创建 / 最近任务返回稳定深链、Task 摘要下一步动作和暂时读取失败；不增加搜索、分页、批量、归档或 Dashboard 矩阵；
- 相关前端 PR 运行受影响的关键 E2E，Release Candidate 运行完整固定 Browser E2E；普通测试不得访问真实 Provider；
- Module / State Transition 测试覆盖 WorkbenchProjection 的模式优先级、stale snapshot、Capability / Intent、轮询停止，以及 Mutation 成功后刷新而非乐观 Current Truth；
- Review 测试覆盖 latest-buffer 串行 Save、成功 revision 链、歧义编辑意图、Save / Flush / Conflict 阻止 Submit，以及 Stale / Superseded 保留缓冲；
- 不可信文本使用普通 React Text Rendering；若出现已接受的 Markdown Preview，覆盖 Raw HTML 关闭和安全 Link Protocol；不测试不存在的泛化 Sanitizer 平台；
- 少量代表性 `@axe-core/playwright` A / AA 检查与人工键盘、Focus、Announcement、200% Text Resize、等价 320 CSS px / 400% Zoom Reflow 共同构成无障碍证据；自动扫描不替代人工判断；
- 正式支持当前稳定 Desktop Chrome；Edge / Firefox / Safari 为 Best-effort。Firefox / WebKit、Visual Regression 和手机矩阵不机械加入首个 Goal；
- 首个完整纵向切片建立固定本地性能 Profile，Release Candidate 同 Profile 复测。输入卡顿 / 丢失、轮询整页闪烁、无界 Fetch / Render、Focus 丢失或 Evidence 阻塞主操作是 Blocking Finding；先 Profile 再优化，不使用无实现基线的机械分数。

### 3.4 真实 Provider Smoke

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

## 8. 尚待冻结

- Anchor SKU 的具体虚构业务数据、文件布局与 expected-output 表示；
- 前端精确工具版本、除 `dev` / `build` / `preview` 外的最终命令、CI Job 分组和浏览器证据保存格式；前端框架、核心测试工具、Accessibility / Browser / Reflow / Performance 边界已由 DEC-055 / 056 冻结；
- Fixture / SDK Stub 的物理实现、Live Smoke 操作手册与证据文件格式；Provider、Version、Profile、Recovery、Secret / Payload / Telemetry、确定性替身分层与 Smoke 触发边界已由 DEC-052～054 冻结；
- Integration / Migration / concurrency / failure-injection 的最终场景矩阵；
- Markdown 模板、文件名与下载协议；视觉架构与样式边界已由 DEC-056 冻结；
- 物理保留、Hold、删除 / 清理顺序与操作员重置证据；产品层只验收 DEC-061 的 Task 范围可逆移除，物理生命周期由 ARP-08、RFC-005 / 007 和 Development Plan 冻结；
- 实际性能 Profile 基线、Beta 用户样本、埋点和 Dashboard；性能判定方法已由 DEC-056 冻结。

这些事项必须由对应 Accepted RFC、Frontend Architecture、Development Plan 或 Goal Issue 冻结；未接受内容不得写成实现事实。

## 9. 停止条件

遇到下列情况时停止受影响工作并升级给 Sol / 用户：

- 测试暴露 Accepted Decision / RFC 冲突；
- 核心事务、Resume、幂等、Current Truth 或证据一致性无法满足；
- 必须降低验收标准、扩大 MVP 或更换已接受技术方案才能继续；
- 需要真实凭证、破坏性数据操作、不可逆迁移或其他人工 Gate。

## 10. 完成边界

本文只有在架构 RFC、Frontend Architecture、可执行测试命令、Fixture 实例、Goal 验收步骤和最终一致性 Review 均完成后，才能从 `PARTIAL` 更新为最终 Testing Strategy。DEC-048、DEC-058～062 的产品验收基线、Anchor SKU、Needs Input、Claim Integrity、Task 资料生命周期和最近任务行为已经 Accepted，但实际 Goal 仍未创建或激活。
