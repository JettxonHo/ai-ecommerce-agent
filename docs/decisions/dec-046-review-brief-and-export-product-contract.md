# DEC-046：冻结审核、Brief 与导出的产品语义和版本行为

## Type

Product / Review Contract / Output Contract / Versioning / Export

## Status

Accepted — Amended by DEC-047

> **Current amendment:** [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) 补充正式对象差异展示、编辑意图和导出前确认交互；本决定的产品语义组、Domain Version、Draft revision 与导出快照内容保持有效。

## Decision

### 决策导向的 Review Package

Review Package 是进入单一 Human Review Gate 的不可变输入快照。产品必须按以下固定语义组组织审核内容：

1. 版本上下文：Task、Review、Package 及其所依赖的 Facts、Insights、Positioning、Source Set 版本；
2. Positioning Candidates：供用户选择、编辑、合并或拒绝的定位候选；
3. 关键 Facts 与 Insights：只集中呈现实际影响本次战略判断的事实和洞察；
4. Hypotheses：影响战略但仍需验证的假设及其当前证据身份；
5. Evidence Limitations：会限制判断或表达的证据不足；
6. Conflicts 与 Strategic Risks：需要用户理解或处理的冲突和战略风险；
7. Model Recommendation：模型推荐及其理由，作为建议而非自动决定。

这些组属于产品契约，审核界面和公共契约必须能够完整表达。固定分组不要求展示全部上游对象，也不要求为凑齐内容而制造假设、限制、冲突或风险；没有适用项时应诚实表达为空或不适用。

Review Package 创建后不可被后台静默修改。上游有效版本发生变化时，旧 Package 过期并拒绝提交，继续遵守 DEC-029 / DEC-044。

### Strategy Draft 与 Approved Strategy

Strategy Draft 是 Review 内可保存、可继续编辑的临时工作内容，不属于 Current Truth，也不得被下游读取。

Approved Strategy 只有在用户明确提交并通过既有确定性校验后才能成为正式版本化 Domain Object。其产品语义固定为以下六组：

1. 目标与情境：Target Segment、Usage Context、Core Job / Need；
2. 定位：Category Frame、Value Proposition、Differentiation；
3. 说服结构：Benefit Priority、Reasons to Believe、Proof Points；
4. 假设决策：接受执行、接受测试、编辑、拒绝或请求证据；
5. 证据与风险：Evidence Limitations、Strategic Risks；
6. 审核与版本元数据：Review / Package / 上游版本引用、用户决定和批准上下文。

每个语义组必须可被正式契约表达，但组内具体字段是否必填仍应遵循业务适用性和已有校验规则。例如没有可靠 Proof Point 时不得为满足结构而创建无依据内容；Evidence Limitation 也不得因用户接受而被删除。

### 平台中立 Marketing Brief

Marketing Brief 是 Approved Strategy 的平台中立执行结构，不是重新制定战略的场所。产品契约固定为以下六组：

1. Objective and Audience：传播目标、目标受众与使用 / 内容情境；
2. Message Architecture：Core Message、Message Hierarchy、Benefit Hierarchy；
3. Reasons to Believe and Evidence：Reasons to Believe、Proof Points 与证据关系；
4. Execution Direction：Objections、Responses、Content Angles、Tone and Voice、CTA Objective；
5. Constraints and Honesty：Mandatory Messages、Prohibited Claims、Hypotheses、Evidence Limitations、Risks；
6. Version and Workflow Context：对象版本、Approved Strategy 与必要上游引用、当前有效性和工作流决定。

Marketing Brief 不包含平台专属最终内容，不得改变 Approved Strategy、创建无依据 Proof Point 或删除证据限制。

### Xiaohongshu Brief 映射

本决定中的 **Xiaohongshu Brief** 指 DEC-031 既有的 **Xiaohongshu Execution Brief（方向）**，不引入第二种平台输出对象。它是平台中立 Marketing Brief 的显式平台映射，产品契约固定为以下六组：

1. Platform and Campaign Context：适用的平台政策上下文、账号 / 活动上下文和传播目标；
2. Note Format and Content Mode：图文 / 视频 Brief 方向与主要内容模式；
3. Creative Structure Directions：标题方向、封面方向、叙事结构、内容重点与证据放置方向；
4. Discovery and Action Directions：搜索意图、关键词、话题、互动与 CTA 方向；
5. Evidence and Platform Constraints：Proof Points、Hypotheses、Evidence Limitations、Prohibited Claims 与平台风险；
6. Workflow and Version Context：Xiaohongshu Brief、Marketing Brief、Approved Strategy 和 Platform Policy Snapshot 的版本引用与有效性。

Adapter 只能映射表达与组织方式，不能重新制定战略、修改 Marketing Brief 或新增 Proof Point。该 Brief 仍不包含最终可发布标题、正文、Hashtags、封面文字、图片 / 视频或自动发布能力。

### Version、Revision 与 Current Truth

产品使用三种不同的变化标识，不得混用：

- **Review Package Version：** 审核输入的不可变快照版本；它固定上游输入，但不是 Approved Strategy 等业务结果的 Domain Version。
- **Domain Version：** Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 等正式业务对象的不可变版本。
- **Review Draft Revision：** 同一临时 Review Draft 在保存过程中的单调递增修订号。它不是正式 Domain Version，也不是 Current Truth。

行为规则如下：

1. Review Package 是不可变快照；上游变化后创建新 Package，不改写旧 Package。
2. 每次成功保存 Review Draft 都产生更高的 `revision`；客户端基于旧 revision 保存或提交时必须拒绝，并提供刷新 / 比较后继续的恢复路径。
3. Review Draft 的自动保存频率、传输字段名和并发实现机制不由本决定冻结。
4. Approved Strategy 的首次批准、经审核的用户修改或重新生成均创建新 Domain Version，不覆盖旧版本。
5. Marketing Brief 与 Xiaohongshu Brief 的首次模型生成、用户业务编辑和重跑均创建新 Domain Version，不覆盖旧版本。
6. Task 使用 Current Truth Pointer 指向当前有效的 Approved Strategy、Marketing Brief 与 Xiaohongshu Brief；下游不得自行猜测“最新记录”。
7. 用户修改 Approved Strategy 必须遵守 Human Review 和既有失效规则；新版本不能绕过审核直接成为下游输入。
8. 纯展示层变化不创建业务版本；是否改变业务语义的确定性识别规则仍待后续交互与接口规格冻结。

### Export Snapshot

导出必须冻结用户发起导出时的当前有效结果快照，并至少携带或展示：

- 被导出的 Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 的对象版本；
- 必要上游版本和证据引用；
- 当前 Hypotheses、Evidence Limitations 与 Risks；
- 导出时间；
- 能够解释该导出对应哪个 Task 与 Current Truth 的上下文。

导出不会创建新的业务事实，也不会改变 Current Truth。导出文件格式、模板、下载协议和视觉布局由后续产品交互与 RFC-004 冻结。

本决定不引入 Hash、SHA-256 或内容指纹要求。若未来出现影响核心功能的重大完整性或安全风险，必须按 DEC-039 提交独立提案。

## Alternatives Considered

### P-10B：把每个概念字段一对一冻结为公共 Schema

- 优点：字段最完整，后续实现歧义少。
- 缺点：在 RFC-004 和数据契约设计前过早绑定字段名、必填性和传输结构，容易把概念说明误当稳定 API。
- 结论：不采用；冻结产品语义组，具体公共字段由 RFC-004 处理。

### P-10C：审核只保留候选选择、编辑和备注

- 优点：Review UI 最轻。
- 缺点：不足以让用户理解关键依据、假设、限制和风险，也无法形成可靠 Approved Strategy。
- 结论：不采用。

### P-11B：把通用 Brief 与 Xiaohongshu Brief 合并

- 优点：对象更少，演示页面表面更直接。
- 缺点：平台规则会泄漏到核心战略与通用执行结构，削弱平台中立边界。
- 结论：不采用。

### P-11C：只做很薄的通用 Brief，由 Adapter 补齐大部分内容

- 优点：通用层字段较少。
- 缺点：Adapter 将被迫重新做 Message Architecture 和业务取舍，绕过 Approved Strategy 与 Marketing Brief Lock。
- 结论：不采用。

### P-12B：每次草稿自动保存都创建完整 Domain Version

- 优点：所有编辑都有正式快照。
- 缺点：大量无业务意义版本会淹没审核历史，并把临时工作状态误当 Current Truth 候选。
- 结论：不采用；Review Draft 使用 revision，正式结果使用不可变 version。

### P-12C：只保留可覆盖的 latest 对象和审计日志

- 优点：读取模型简单。
- 缺点：与 DEC-024 的版本化 Current Truth 冲突，难以可靠解释失效、重跑与导出结果。
- 结论：不采用。

## Reason

决策导向分组让用户聚焦真正影响定位与执行的内容，同时避免把全部上游数据机械化地塞进审核。平台中立 Brief 与显式 Xiaohongshu 映射保持 Skill / Adapter 边界。将临时草稿 revision 与正式 Domain Version 分离，既支持多标签页和恢复，又避免无意义版本膨胀；导出快照则让演示结果能被准确追溯，而无需引入与当前风险不相称的内容哈希工程。

## Impact

- PRD、MVP Scope、User Flows、Human Review / Marketing Brief / Xiaohongshu Adapter 规格、Frontend Architecture、RFC-004 / 006、Testing Strategy 与 Goal 必须采用本产品契约。
- RFC-004 必须为 Draft revision 冲突、不可变对象版本、Current Truth Pointer、过期提交和导出快照提供公共接口与错误映射。
- 测试至少覆盖 Review Package 不可变、陈旧 revision 保存 / 提交拒绝、正式对象不覆盖、用户编辑创建新版本、Current Truth 指向有效版本、导出版本与上游引用一致，以及 Brief / Adapter 不越界。
- 本决定不授权业务实现、Technical Spike 执行或实际 Goal 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-004、RFC-006；本决定不接受其技术实现方案。

## Supersedes

None.

## Amends

- [DEC-006](dec-006-four-layer-structured-marketing-brief.md)：将四层主结构中的策略审核与执行层输出具体化为稳定产品语义组，不冻结最终公共字段。
- [DEC-024](dec-024-versioned-domain-state-and-compact-langgraph-state.md)：明确 Review Draft revision 与不可变 Domain Version 的边界，并补充导出快照行为；不改变版本化 Current Truth 原则。
- [DEC-029](dec-029-human-review-and-approved-strategy-contract.md)：冻结 Review Package 与 Approved Strategy 的产品语义组，并选择单调递增 Draft revision；不改变强制 Human Review、事务提交和过期 Package 拒绝。
- [DEC-030](dec-030-marketing-brief-generation-skill-contract.md)：将既有概念输出收束为六个稳定的 Marketing Brief 产品语义组。
- [DEC-031](dec-031-xiaohongshu-brief-mapping-adapter-contract.md)：将既有概念输出收束为六个稳定的 Xiaohongshu Brief 产品语义组。

## Does Not Amend

- DEC-039：适度校验、禁止普通 Hash / SHA-256 要求和非机械 Rubric 继续有效。
- DEC-041：受控单工作区、输入格式和非范围边界保持不变。
- DEC-044：单任务工作台、失效预览、用户确认后局部重跑和过期审核拒绝保持不变。

## Amended By

- [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：补充语义组差异、编辑影响与导出前确认交互，不改变版本和快照契约。

## Decision Boundary

**本决定已经确认：**

- Review Package 与 Approved Strategy 的固定产品语义组；
- 平台中立 Marketing Brief 与 Xiaohongshu Brief 映射的固定六组产品语义；
- Review Package 的不可变快照版本，以及 Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 的不可变 Domain Version 行为；
- Review Draft 使用单调递增 revision，陈旧保存 / 提交必须拒绝；
- Task 使用 Current Truth Pointer；
- 导出冻结当前有效对象、上游引用、限制与时间上下文；
- 不使用 Hash 或 SHA-256 作为本产品契约要求。

**本决定尚未确认：**

> 以下为本决定接受时的边界；版本差异与导出前确认的产品语义后来由 DEC-047 解决。最终组件、Diff 算法、导出格式和传输实现仍未确认。

- 最终 JSON / OpenAPI / 数据库字段名、类型、枚举和必填表达；
- API 路径、请求 / 响应结构、错误代码和状态映射；
- ETag、If-Match、数据库锁或其他并发实现机制；
- Draft 自动保存频率、Patch / Snapshot 存储方式和版本差异 UI；
- 导出文件格式、模板、下载协议与视觉布局；
- 前端控件、组件、框架和像素级设计；
- Prompt、模型、Provider 与生产 Runtime。

## Notes

用户于 2026-08-06 明确接受 P-10A、P-11A、P-12A。本决定冻结的是产品可见语义与行为，不把 DEC-029～031 的概念字段逐项提升为最终公共 Schema，也不替 RFC-004 / RFC-006 作出实现选择。
