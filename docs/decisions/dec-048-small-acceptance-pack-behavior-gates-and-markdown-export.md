# DEC-048：采用小型代表性验收包、行为门禁与 Markdown-first 导出

## Type

Product / Acceptance / Testing / Export

## Status

Accepted

## Decision

### 小型代表性验收包

首个端到端演示使用**三个固定资料包 + 一个变更脚本**作为产品验收基线：

1. **资料充分的正常任务：** 使用 DEC-041 允许的输入，完成 Fact、Insight、Positioning、Human Review、Marketing Brief、Xiaohongshu Brief 与导出闭环；
2. **资料不足但仍可运行的任务：** 缺少增强或可选资料时继续处理，并正确标记 Hypotheses、Evidence Limitations、Insufficient Information 与不可作出的结论；
3. **阻断性冲突与恢复任务：** 商品身份或形成诚实 Fact Layer 所需的关键事实冲突进入 Needs Input，显示冲突值、来源、影响和所需动作；用户补充或确认资料后可以从相应阶段恢复；
4. **基于正常任务的变更脚本：** 至少覆盖 Source Version 更新、明确业务语义编辑、影响预览、陈旧 Review 保存或提交拒绝，以及用户确认后的局部重跑。

Fixture 使用可读的 `fixture_id` 与 `fixture_version` 维护。版本变化必须在变更说明中解释，但不要求内容哈希、SHA-256 或指纹。具体商品、文案、文件名与物理目录由后续 Testing Strategy 实例化任务确定，不得改变上述场景语义或扩大产品范围。

普通 PR 使用确定性模型替身运行适用验收场景。Release Candidate 使用“资料充分的正常任务”对最终选定的单一真实 Provider 完成一次手动端到端 Smoke；该 Smoke 不进入普通 PR Required Checks，也不把偶发模型措辞变化误判为代码回归。

### 行为硬门禁与人工可用性判断

MVP 验收分为两类证据，不使用加权总分自动接受：

#### 行为硬门禁

- 所有适用 Required Checks、确定性契约测试和固定验收场景通过；
- 固定资料包中的事实、来源与可用 Locator 不得伪造；
- 陈旧 Review 拒绝、Current Truth、阶段失效、恢复和确认式局部重跑符合 Accepted Decision；
- 必需产品语义组存在；资料不足或不适用时诚实表达，不得为了完整率制造事实、证据、假设或风险；
- Goal 验收时 Critical / Blocking 缺陷为零；
- Release Candidate 完成一次真实 Provider 正常任务端到端 Smoke。

#### 人工可用性判断

人工验收者从目标用户视角确认：

- 不需要开发者解释内部 Runtime，能够完成资料提交、审核、补料或恢复和导出；
- 能够理解主要结论、证据身份、Hypotheses、Evidence Limitations 与 Conflicts；
- 能够判断和修改策略与 Brief，并知道修改造成的影响；
- 导出的交付物可以用于后续内容策划。

人工结论记录为 `PASS` 或 `FAIL`，并附理由、主要修改与未解决限制。Rubric 可以帮助检查遗漏，但不得作为机械评分器或自动批准器。

DEC-010 的事实来源可追溯、无依据事实、语义完整与下游失效指标，在固定验收包中按上述关键不变量判断。关键结论接受情况、任务完成时间、交互步骤和人工修改量在首个演示中记录为观察数据，不设置缺少真实用户基线的机械发布阈值；真实用户访谈和对照结果仍是 Beta 前工作。

### Markdown-first 用户导出

首个 Goal 的用户侧导出采用 UTF-8 Markdown：

- 当前有效的 Marketing Brief 与 Xiaohongshu Brief 可以分别导出；
- 每份文件必须表达 Task 上下文、被导出对象版本、必要上游版本引用、当前产品语义组、Hypotheses、Evidence Limitations、Risks、可用证据引用与导出时间；
- 导出内容必须对应发起导出时的 Current Truth Snapshot；失效、被取代或部分提交的对象不得作为当前结果导出；
- 用户侧 PDF 与 JSON 文件导出不进入首个 Goal；API 是否使用 JSON 由 RFC-004 独立决定，不受本文件格式决定限制；
- 导出不新增内容哈希、SHA-256 或指纹要求。

最终文件名、Markdown 模板、元数据排版、下载协议与视觉样式由 Frontend Architecture / RFC-004 在上述内容边界内确定。

## Alternatives Considered

### P-16B：10～20 个行业 Benchmark

- 优点：品类和资料组合覆盖更广。
- 缺点：在首个本地演示前产生较高的数据维护、预期结果和模型评测成本，容易把 MVP 扩大为独立评测工程。
- 结论：不采用；Beta 或真实试点可在当前小型基线之上扩展。

### P-16C：仅人工临时演示

- 优点：准备成本最低。
- 缺点：不可重复、不能稳定发现回归，也无法为长期 Agent 提供明确完成证据。
- 结论：不采用。

### P-17B：加权 Rubric 总分

- 优点：便于生成单一分数和横向比较。
- 缺点：在样本、权重与真实用户基线不足时制造虚假精确度，并可能让 Agent 为分数优化而偏离业务可用性。
- 结论：不采用。

### P-17C：完全依赖主观 Review

- 优点：灵活、无需维护确定性场景。
- 缺点：无法稳定验证版本、失效、恢复、证据和 Current Truth 等核心不变量。
- 结论：不采用。

### P-18B：Markdown + 用户侧 JSON

- 优点：同时适合人工交接和机器消费。
- 缺点：扩大用户导出契约、版本兼容和测试范围；首个演示已有 API 公共契约规划，不需要重复建设机器导出面。
- 结论：不进入首个 Goal；未来存在明确集成需求时再提案。

### P-18C：PDF-first

- 优点：排版更正式，适合不可编辑的展示文件。
- 缺点：引入字体、分页、渲染和视觉模板工作，不利于用户继续编辑，也不是验证核心闭环的必要条件。
- 结论：不进入首个 Goal。

## Reason

三个固定资料包覆盖正常、诚实降级和阻断恢复三个真实业务分支，单独的变更脚本覆盖版本与局部重跑核心风险；继续增加罕见变体的收益低于维护成本。行为硬门禁保护可重复的可靠性不变量，人工判断保留对业务可用性的专业判断，符合 DEC-039 的适度校验原则。

Markdown 与运营人员的阅读、复制和继续编辑习惯一致，也能表达 DEC-046 / DEC-047 所需的版本、限制和证据上下文；暂缓 PDF 和用户侧 JSON 可以让首个 Goal 聚焦端到端价值，而不增加并非核心的排版或第二套公共契约。

## Impact

- PRD、MVP Scope、User Flows、Testing Strategy、Traceability、Implementation Readiness 与长期 Goal 必须使用本验收包、验收方法和用户导出边界。
- Testing Strategy 必须把三个资料包、一个变更脚本、确定性 PR 验证、Release Candidate Live Smoke 与人工验收分别定义，不得混成单一机械分数。
- RFC-004 / Frontend Architecture 必须支持 Current Truth Markdown 导出，但仍自行冻结 API、状态、错误、模板和下载实现。
- RFC-006 必须支持确定性替身与单一真实 Provider 的分离验证边界。
- 本决定不授权创建实际 Fixture、执行 Technical Spike、编写业务代码或激活 Goal。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-004、RFC-006；本决定不接受其技术实现方案。

## Supersedes

None.

## Amends

- [DEC-010](dec-010-three-dimensional-mvp-evaluation-framework.md)：为首个演示冻结代表性验收包和必要行为门禁；不推翻三维评价框架。
- [DEC-042](dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md)：补全行为型演示成功标准的 Fixture、执行方法和人工判断边界。
- [DEC-046](dec-046-review-brief-and-export-product-contract.md)：在既有 Export Snapshot 语义上选择 Markdown-first 用户文件格式。
- [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：补全导出文件格式与代表性验收场景；不改变导出确认、证据、编辑或恢复语义。

## Does Not Amend

- DEC-039：适度校验、禁止普通 Hash / SHA-256 要求和非机械 Rubric 继续有效。
- DEC-041：受控单工作区、输入格式、单一真实 Provider 和非范围边界保持不变。

## Decision Boundary

**本决定已经确认：**

- 三个固定资料包与一个变更脚本的场景结构；
- 普通 PR 的确定性验证与 Release Candidate 单次真实 Provider Smoke 边界；
- 行为硬门禁 + 人工 `PASS / FAIL` 判断，不使用加权总分自动接受；
- Goal 验收时 Critical / Blocking 缺陷为零；
- Marketing Brief 与 Xiaohongshu Brief 的 UTF-8 Markdown 用户导出；
- 用户侧 PDF / JSON 导出不进入首个 Goal；
- Fixture 与导出不新增 Hash、SHA-256 或内容指纹。

**本决定尚未确认：**

- Fixture 的具体商品、内容、文件名、目录、数据许可证与最终 expected-output 表示；
- 测试框架、浏览器 E2E 工具、具体命令、并行方式与 CI Job；
- 最终真实 Provider、模型、Prompt、Structured Output 与 Live Smoke 运行手册；
- 性能耗时阈值、真实用户样本量、埋点、Dashboard 与 Beta 对照实验；
- Markdown 文件名、模板、Front Matter、视觉排版、下载路径与传输协议；
- API JSON、OpenAPI、数据库字段、状态、错误与并发契约。

## Notes

- 用户于 2026-08-06 明确接受 `P-16A`、`P-17A` 与 `P-18A`。
- 本决定只关闭首个演示的产品验收方法和用户导出格式，不把未接受的技术选项写成当前事实。
- Issue #44 / PR #45 负责本决定及 Current Truth 一致性归档。
