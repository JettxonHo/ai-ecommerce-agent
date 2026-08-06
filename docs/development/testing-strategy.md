# MVP Testing Strategy

> **Status: PARTIAL — product acceptance baseline accepted; implementation tooling and executable suites pending RFC / Goal**
> **Authority:** [DEC-010](../decisions/dec-010-three-dimensional-mvp-evaluation-framework.md) · [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) · [DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) · [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) · [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md)

本文件定义首个本地端到端演示 MVP 的测试与验收策略。它当前只固化已接受的产品验收基线与 DEC-052 的模型契约输入，不授权业务实现，也不提前选择测试框架、浏览器工具或公共接口。

---

## 1. 质量目标

测试证据必须共同回答：

1. 用户能否完成商品资料到可用 Brief 的任务闭环；
2. 事实、证据、版本、Current Truth、失效和恢复是否可靠；
3. 用户能否在不理解内部 Runtime 的前提下审核、修改、恢复和导出；
4. 新环境能否按权威文档复现相同演示结果。

Rubric 与指标只辅助专业判断，不作为机械评分器。测试优先覆盖代表性路径和关键不变量，不反复堆叠基本不可能发生的防御性变体。

## 2. 固定验收包

| ID | 场景 | 必须证明的产品行为 |
|---|---|---|
| `fixture-sufficient-v1` | 资料充分的正常任务 | 允许输入可接收；Fact → Insight → Positioning → Human Review → Marketing Brief → Xiaohongshu Brief → Markdown 导出闭环完成；主要结论可追溯。 |
| `fixture-limited-v1` | 资料不足但可运行 | 缺少增强 / 可选资料不阻塞；Hypotheses、Evidence Limitations 与 Insufficient Information 被诚实表达；不为完整率制造事实或 Proof Point。 |
| `fixture-conflict-v1` | 阻断性身份 / 关键事实冲突与恢复 | 进入 Needs Input；展示冲突值、来源、影响和用户动作；补料或确认后从正确阶段恢复，旧失效结果不成为 Current Truth。 |
| `mutation-sufficient-v1` | 基于正常任务的版本与重跑脚本 | Source Version 更新、业务语义编辑、影响预览、陈旧 Review 拒绝、用户确认后的局部重跑，以及导出只使用当前有效版本。 |

表中 ID 是产品策划期的可读逻辑标识，不代表实际文件已经创建。具体资料、expected output 和物理目录由 Goal 内独立测试 Issue 实例化并经 Review；版本变更写入变更说明，不使用内容哈希。

## 3. 分层验证

### 3.1 每个代码 PR

- 运行仓库既有 8 项 Required Checks；
- 按变更相关性运行 Unit、Contract、Architecture、Integration、Migration 或 Browser 测试；
- LLM 行为使用确定性替身，不要求真实 Secret、外部网络或 Live Provider；
- 只覆盖当前 Issue 的代表性路径和相关错误分支，不把不相关 Live / E2E 场景塞入普通 PR Gate。

### 3.2 持久化与 Workflow

- PostgreSQL 是持久化验收引擎，SQLite 不替代 PostgreSQL Integration / Migration / concurrency 验收；
- 覆盖事务原子性、幂等、版本 Pointer、陈旧 Review、Interrupt / Resume、Cancel、Retry / Rerun、Stage Invalidation 和恢复；
- Checkpoint 不得被测试误当 Business Current Truth。

最终工具、命令、Fixture 装载方式与故障注入边界在 RFC-003 / 004 接受后补充。

### 3.3 前端与端到端

- 组件与状态转换测试覆盖输入、进度、Needs Input、Review、恢复、结果和导出；
- API Contract 测试验证前后端状态、错误和版本映射；
- Browser E2E 使用固定验收包覆盖正常闭环、冲突恢复和 mutation script；
- 最终浏览器工具、步骤和截图 / Trace 证据格式待 Frontend Architecture 冻结。

### 3.4 真实 Provider Smoke

- 仅在 Release Candidate 使用 `fixture-sufficient-v1` 执行一次完整端到端 Smoke；
- Secret 只经环境变量或运行环境注入，不写入仓库、Fixture、日志或导出；
- Live Smoke 不进入普通 PR Required Checks；
- Live Smoke 使用 DEC-052 接受的 OpenAI Responses API / `gpt-5.6-terra` 路径；具体操作手册、版本身份、错误边界与证据格式待 RFC-006 DQ-04～08 冻结；
- 验收目标是契约、闭环和诚实证据行为，不要求每次生成完全相同措辞，也不使用语言流畅度总分。

## 4. 行为硬门禁

Goal 完成前必须同时满足：

- 所有 Required Checks 和适用确定性测试通过；
- 固定验收包的 Required Behaviors 全部通过；
- 伪造 Source 或可用 Locator 数量为零；
- 陈旧 Review 拒绝、Current Truth、失效、恢复与确认式局部重跑结果正确；
- 必需语义组存在，或诚实标记资料不足 / 不适用；
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

- Fixture 的具体业务数据、许可、文件布局与 expected-output 表示；
- 测试框架、浏览器 E2E 工具、命令、CI 分组和证据保存格式；
- Prompt / Schema / Model Execution 版本、错误与重试边界，以及 Live Smoke 操作手册；Provider / 默认模型已由 DEC-052 冻结；
- Integration / Migration / concurrency / failure-injection 的最终场景矩阵；
- Markdown 模板、文件名、下载协议与视觉样式；
- 性能基线、Beta 用户样本、埋点和 Dashboard。

这些事项必须由对应 Accepted RFC、Frontend Architecture、Development Plan 或 Goal Issue 冻结；未接受内容不得写成实现事实。

## 9. 停止条件

遇到下列情况时停止受影响工作并升级给 Sol / 用户：

- 测试暴露 Accepted Decision / RFC 冲突；
- 核心事务、Resume、幂等、Current Truth 或证据一致性无法满足；
- 必须降低验收标准、扩大 MVP 或更换已接受技术方案才能继续；
- 需要真实凭证、破坏性数据操作、不可逆迁移或其他人工 Gate。

## 10. 完成边界

本文只有在架构 RFC、Frontend Architecture、可执行测试命令、Fixture 实例、Goal 验收步骤和最终一致性 Review 均完成后，才能从 `PARTIAL` 更新为最终 Testing Strategy。DEC-048 的产品验收基线已经 Accepted，但实际 Goal 仍未创建或激活。
