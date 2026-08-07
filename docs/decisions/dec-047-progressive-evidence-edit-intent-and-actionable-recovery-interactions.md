# DEC-047：采用渐进式证据披露、结构化编辑意图与行动导向恢复交互

## Type

Product / Interaction / Evidence / Editing / Recovery / Export

## Status

Accepted — Amended by DEC-048 / DEC-059

> **Current amendments:** [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) 冻结代表性验收包、必要行为门禁和 Markdown-first 用户导出；[DEC-059](dec-059-targeted-needs-input-action-request-model.md) 补全 Needs Input 的有限结构化行动请求。本决定的证据、编辑、进度、恢复与导出确认语义保持有效。

## Decision

### 渐进式证据披露

单任务工作台继续使用 DEC-008 的五类结论标记，并以渐进披露方式把结论与依据放在同一任务上下文中：

1. 影响业务判断的 Fact、Insight、Inference、Hypothesis、Evidence Limitation 与 Recommendation 必须显示其结论类型，并提供“查看依据”入口；
2. 用户从当前条目打开证据卡片或可收起的证据 / 上下文面板，不需要先离开当前阶段进入独立证据页面；
3. 证据详情应表达来源标签、来源类型、Source Version、可用定位、支持关系，以及适用的 Evidence Limitation 或 Conflict；
4. PDF 页码、CSV 行范围、文本段落或其他精确定位只在解析结果真实提供时展示；不存在可靠定位时不得伪造；
5. 直接证据可以显示短摘录，综合洞察和策略可以显示忠实摘要与主要依据关系，不要求每句话机械绑定一段原文；
6. 无直接证据的内容必须保持为模型推断、待验证假设或资料不足，不能通过界面样式暗示其已被证实。

MVP 不显示未经校准的数字置信度，也不使用证据覆盖总分或 Rubric 自动决定是否接受。最终来源公共结构、Locator Schema、Evidence API 与权限过滤由 RFC-004 / RFC-005 冻结。

### 结构化编辑、差异与编辑意图

审核与正式 Brief 使用语义组内的结构化编辑。产品必须让用户理解“改了什么、由谁修改、影响哪些当前结果”，但不冻结像素级差异组件或最终公共字段。

- Review Draft 的保存继续递增 DEC-046 的 revision；提交后形成新的不可变 Approved Strategy Domain Version。
- Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 的业务编辑继续创建新 Domain Version，不静默覆盖旧版本。
- 差异至少按语义组展示修改前后内容、模型或用户来源，以及相关对象版本。最终使用行内、并排或摘要式 Diff 由 Frontend Architecture 决定。
- 明确改变 Fact、Insight、Approved Strategy 或其他上游结构化业务语义的修改，直接视为重要业务修改，并采用 DEC-009 / DEC-044 的阶段级失效预览与确认式局部重跑。
- Marketing Brief 的业务修改创建新版本并使当前 Xiaohongshu Brief 失效；Xiaohongshu Brief 的业务修改创建自身新版本，不反向使上游 Strategy 或 Marketing Brief 失效。
- 只改变错别字、标点、格式或表达方式且不改变业务含义的修改，可以标记为“展示性润色”，不触发上游重跑。
- 对不能由被编辑语义组和确定性规则明确判断的自由文本修改，系统在保存或继续前只要求用户确认一次“业务内容修改”或“展示性润色”；默认不得由 LLM 分类器替用户作最终 Gate。

编辑意图只决定既有阶段级失效规则是否适用，不创建字段级依赖图。被判定为重要修改后仍必须展示失效与保留范围，并由用户确认是否局部重跑；不得因用户暂不重跑而把旧下游结果继续显示为有效。

### 阶段进度与行动导向恢复

长任务使用阶段时间线表达进度，而不是虚构精确百分比。工作台至少应让用户看见：当前阶段、已经完成或待处理的阶段、最近更新时间、当前等待原因和下一项可执行动作。

这里的阶段进度和等待名称是产品交互语义，不是最终 API / 数据库状态枚举。轮询、推送、事件流或其他传输方式由 Frontend Architecture 与 RFC-003 / RFC-004 冻结。

用户可见错误与暂停信息按行动组织：

1. 说明发生了什么、受影响的阶段，以及最近有效业务结果是否仍然可用；
2. 给出与当前情形匹配的动作，例如补充资料后继续、恢复未完成运行、重试当前阶段、查看失效预览并确认重跑、刷新并比较陈旧 Draft，或取消当前运行；
3. 允许用户返回最后有效结果，但不得把已失效或部分提交结果标成 Current Truth；
4. 可收起技术详情可以提供错误类别和关联标识，不能向用户暴露 Secret、原始凭证或无必要的内部堆栈；
5. 自动技术重试继续遵守 DEC-033 的有界策略；业务等待、资料不足或用户尚未确认不得伪装成反复重试的技术故障。

产品不要求用户理解 Worker、Checkpoint、Provider 或内部节点名称。恢复动作必须映射到已确认的业务语义；最终错误代码、Retry / Resume API、状态映射和 Checkpoint 对账由 RFC-003 / RFC-004 / RFC-007 冻结。

### 导出确认

导出前展示本次将冻结的当前 Approved Strategy、Marketing Brief、Xiaohongshu Brief 版本，以及适用的上游引用、Hypotheses、Evidence Limitations 与 Risks 摘要。用户确认后按 DEC-046 创建导出快照。

失效结果不得作为当前结果导出。本文接受时把导出文件格式、模板、下载协议、视觉布局和是否提供多种格式留给 Frontend Architecture 与 RFC-004；后续 DEC-056 已冻结前端视觉与确认交互边界，DEC-065 / DEC-066 与已接受的 RFC-004 已冻结 Markdown-only、固定模板版本、文件名和下载协议；实际模板内容仍待 Goal 激活后的独立实施 Issue。本决定不新增 Hash、SHA-256 或内容指纹要求。

## Alternatives Considered

### P-13B：所有结论密集内联引用

- 优点：引用始终可见。
- 缺点：审核界面拥挤，并会把综合判断机械化为逐句引用或制造错误精确感。
- 结论：不采用；重要内容保留入口，证据按需展开。

### P-13C：独立证据页面

- 优点：证据列表实现表面简单。
- 缺点：结论与依据脱离当前任务和审核上下文。
- 结论：不作为主要交互；证据可以有汇总视图，但上下文入口不可缺失。

### P-14B：由模型自动判断修改是否影响业务含义

- 优点：减少一次用户选择。
- 缺点：不可预测，难以形成确定性失效与测试契约。
- 结论：不采用为最终 Gate；模型可以辅助解释差异，不能替代明确规则或用户确认。

### P-14C：所有编辑一律触发失效

- 优点：规则简单。
- 缺点：错别字和格式调整也会产生无意义重跑，属于过度机械化。
- 结论：不采用。

### P-15B：技术日志和百分比主导

- 优点：内部运行信息丰富。
- 缺点：目标用户不应理解内部 Runtime，且无可靠计算基础的百分比会误导。
- 结论：不采用为主视图；必要技术详情只按需展开。

### P-15C：仅使用 Spinner 与 Toast

- 优点：实现成本低。
- 缺点：不能支撑长任务、跨会话恢复、Needs Input、Human Review 或失效重跑。
- 结论：不采用。

## Reason

结论与证据需要在审核语境中直接关联，但逐句引用和置信度数字会增加噪声与虚假精确感。结构化编辑与一次性编辑意图确认使阶段级失效保持可预测，同时避免所有文字修改都触发重跑。阶段时间线和行动导向错误让用户围绕业务任务恢复，不需要理解运行时实现。

该组合落实 DEC-039 的适度校验与非机械 Rubric 原则，并保持 DEC-008 / DEC-009 / DEC-033 / DEC-044 / DEC-046 的可靠性、失效、恢复和版本边界。

## Impact

- PRD、MVP Scope、User Flows、Human Review / Evidence / Workflow Runtime 规格、Frontend Architecture、RFC-003～005 / 007、Testing Strategy 与 Goal 必须采用本交互契约。
- 测试至少覆盖五类标记与证据展开、无定位时不伪造、重要修改的失效预览、展示性润色不触发上游重跑、歧义修改的一次确认、Marketing Brief 修改使 Xiaohongshu Brief 失效、阶段进度不伪造百分比、错误动作与当前状态一致、陈旧 Draft 恢复，以及失效结果不可导出。
- 本决定不授权业务实现、Technical Spike 执行或实际 Goal 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-003、RFC-004、RFC-005、RFC-007；本决定不接受其技术实现方案。

## Supersedes

None.

## Amends

- [DEC-007](dec-007-single-review-node-and-exception-pauses.md)：具体化异常暂停后的用户可见原因、业务影响与恢复动作；不改变单一强制 Human Review 或异常触发范围。
- [DEC-008](dec-008-tiered-evidence-and-traceable-conclusions.md)：冻结五类标记的渐进式证据呈现，并明确不显示未经校准的数字置信度；不改变证据真实性要求。
- [DEC-009](dec-009-stage-level-invalidation-and-partial-rerun.md)：冻结重要 / 非重要修改的产品识别方式与语义组差异要求；不引入字段级依赖图。
- [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)：具体化证据面板、阶段进度、编辑影响预览和行动导向恢复；不改变确认式局部重跑。
- [DEC-046](dec-046-review-brief-and-export-product-contract.md)：补充正式对象差异展示和导出前确认；不改变产品语义组、Domain Version、Draft revision 或导出快照内容。

## Does Not Amend

- DEC-039：适度校验、禁止普通 Hash / SHA-256 要求和非机械 Rubric 继续有效。
- DEC-041：受控单工作区、输入格式、模型范围和非范围边界保持不变。

## Amended By

- [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)
- [DEC-059](dec-059-targeted-needs-input-action-request-model.md)：具体化补料继续与冲突裁决的行动结构。

## Decision Boundary

**本决定已经确认：**

- 五类结论标记 + 当前上下文入口 + 证据卡片 / 可收起面板的渐进式披露；
- 来源版本、可用定位、支持关系、限制和冲突的用户可见语义；
- 无真实定位时不得伪造，不使用未经校准数字置信度或机械覆盖总分；
- 语义组差异、修改来源和对象版本必须可理解；
- 明确业务字段自动视为重要修改，纯展示润色不触发上游重跑，歧义自由文本由用户确认一次编辑意图；
- 不使用 LLM 分类器作为编辑影响最终 Gate，不建设字段级依赖图；
- 阶段时间线、最近更新时间、等待原因与下一步动作，不显示虚构百分比；
- 行动导向错误 / 暂停 / 恢复与返回最后有效结果；
- 导出前展示将冻结的 Current Truth 版本和限制摘要，失效结果不可作为当前结果导出。

**本决定尚未确认：**

> 以下为本决定接受时的开放边界。代表性验收包、必要行为门禁和 Marketing Brief / Xiaohongshu Brief 的 Markdown-first 用户导出后来由 DEC-048 解决；具体模板、测试工具和最终浏览器步骤继续开放。

- 最终组件、布局、导航方向、视觉样式与逐字段编辑控件；
- 最终 JSON / OpenAPI / 数据库字段、Locator Schema、状态枚举与错误代码；
- Diff 算法、行内 / 并排 / 摘要表现、自动保存频率与并发机制；
- 轮询、SSE、WebSocket 或其他进度传输方式；
- Retry 次数、Timeout、Backoff、Checkpoint、Worker 与恢复实现；
- 导出文件格式、模板、下载协议与视觉布局；
- 代表性 Fixture、必要阈值和最终浏览器 E2E 步骤。

## Notes

用户于 2026-08-06 明确接受 P-13A、P-14A、P-15A。本决定冻结产品可见交互语义，不把产品用语提升为最终公共状态，不替 Frontend Architecture 或 RFC-003～005 / 007 作出实现选择。
