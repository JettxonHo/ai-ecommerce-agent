# DEC-044：采用单任务工作台、两级输入门禁与确认式局部重跑交互

## Type

Product / Interaction / Input Gate / Versioning / Rerun

## Status

Accepted — Amended by DEC-045 / DEC-047 / DEC-059

> **Current amendments:** [DEC-045](dec-045-minimum-input-file-limits-and-conflict-handling.md) 冻结 Task 创建门禁、Fact Stage 最低条件、演示默认文件限制与分级冲突处理；[DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) 具体化渐进式证据、编辑影响、阶段进度和行动导向恢复；[DEC-059](dec-059-targeted-needs-input-action-request-model.md) 将 Needs Input 具体化为由当前真实阻断派生的有限结构化行动请求。以下原文保留为本决定的原则层记录。

## Decision

### 单任务工作台

首个演示采用**单任务工作台**承载完整闭环。一个任务在同一工作台中持续呈现：

- 阶段导航：显示当前阶段、已完成阶段、待处理阶段、需要补充资料和已失效阶段；
- 当前工作区：承载当前阶段的输入、进度、问题、结构化结果、审核或导出操作；
- 可收起的证据 / 上下文面板：按当前条目查看来源、主要依据、假设、资料限制和冲突，不要求用户离开任务上下文。

任务创建和首次资料提交进入该工作台；暂停、跨会话恢复、审核、重跑和结果查看均返回同一稳定 `task_id` 的工作台。聊天记录不作为业务状态或恢复依据。

本决定冻结信息架构，不冻结最终视觉布局、导航方向、组件库、前端框架或像素级设计。

### 两级输入门禁

输入采用两级产品门禁：

1. **可运行门禁：** 满足既有最低可运行输入后允许启动基础流程；
2. **增强提示：** 推荐增强与可选资料只用于提高分析覆盖和证据质量，缺少它们不得阻断基础流程。

只有真实阻塞项可以阻止启动或恢复，例如：

- 无法识别当前商品或任务目标，导致最低可运行身份不成立；
- 文件格式不在 DEC-041 允许范围内、文件无法读取或受密码保护；
- 当前商品的关键事实存在无法由系统自行裁决的冲突；
- 其他会使系统无法形成诚实、可追溯基础结果的最低条件缺失。

非阻塞的资料不足不得伪装为技术失败，也不得要求用户补齐所有增强资料。系统应继续可可靠完成的部分，显式说明资料限制、受影响结论和建议补充项。

当运行中需要用户补充资料时，工作台进入用户可见的 **Needs Input（需要补充资料）** 交互态，展示：阻塞原因、受影响阶段、需要补充或确认的内容，以及补充后如何继续。该名称是产品交互语言；最终 API / 数据库状态枚举及其与既有 `waiting_for_input` / `waiting_input` 概念状态的映射由 RFC-003 / RFC-004 冻结。

最低字段与文件限制后来由 DEC-045 补全；Needs Input 行动请求模型后来由 DEC-059 补全。具体公共字段名、数据类型与 API / 数据库枚举由 RFC-004 / 005 冻结，前端组件组合留给实现 Issue。

### 版本、失效预览与确认式局部重跑

- 用户修改表单资料、替换文件或重新导入评论时，按照 DEC-025 创建新的 **Source Version**；不得静默覆盖旧 Source Version。
- 用户直接修改事实、洞察、策略或执行层业务内容时，按照 DEC-024 创建相应的版本化 Domain Object；不得把业务结果编辑误记为 Source Version。
- 系统依据 DEC-009 的阶段级依赖计算受影响阶段，并在重跑前展示失效预览：变更来源 / 内容、将失效的阶段、保留有效的阶段，以及建议从哪个最早阶段开始重跑。
- 除恢复未完成的同一次运行外，资料或上游业务内容变化后**不自动立即启动新的生成**。用户确认失效预览后，系统才启动受影响阶段的局部重跑。
- 用户取消或暂不确认时，变更可以保存，但已被判定失效的旧下游结果不得继续显示为当前有效结果、不得进入最终 Brief，也不得作为后续生成依据。
- 局部重跑完成后，用户重新查看受影响内容；若变化影响审核输入，则创建新的 Review Package，并重新进入同一个 Human Review Gate。
- 基于旧 Facts / Insights / Positioning / Source Set Version 的 Review Package 自动标记为 `superseded`；旧审核提交必须拒绝，不得自动迁移为对新版本的批准。

最终执行层 Brief 的纯展示或不改变业务含义的文字编辑继续遵守 DEC-009：默认不触发上游重跑。重要 / 非重要修改的最终确定性识别规则与修改前后差异 UI 仍待后续规格冻结。

## Alternatives Considered

### 全屏线性向导

- 优点：首次流程简单。
- 缺点：跨会话恢复、审核回看、证据查看和失效重跑时上下文割裂。
- 结论：不采用为主信息架构。

### 每个阶段独立页面

- 优点：阶段隔离清楚。
- 缺点：导航和状态交接成本较高，容易让用户失去完整任务上下文。
- 结论：不采用；阶段可以有独立视图，但仍属于同一任务工作台。

### 任意资料均可启动

- 优点：输入摩擦最低。
- 缺点：会产生无法形成基本事实层的无意义运行。
- 结论：不采用。

### 所有资料完整后才允许启动

- 优点：输入一致性较高。
- 缺点：把增强资料机械化为强制项，违背分层输入与适度校验原则。
- 结论：不采用。

### 编辑后自动立即重跑或每次全量重跑

- 优点：用户操作更少或实现表面更简单。
- 缺点：产生不必要调用、竞态和无关内容变化，也削弱用户对影响范围的理解与控制。
- 结论：不采用；使用失效预览 + 用户确认 + 阶段级局部重跑。

## Reason

单任务工作台能维持长期任务上下文；两级门禁避免资料不足被过度防御；失效预览和确认式局部重跑让版本变化对用户可见，同时保持 DEC-009 的一致性与 DEC-029 的审核安全。

## Impact

- Product User Flows、PRD、MVP Scope、Frontend Architecture、RFC-003 / 004 / 005、Testing Strategy 与 Goal 必须使用本交互契约。
- API 与前端必须能表达稳定任务身份、Needs Input、受影响阶段、失效预览、用户确认、局部重跑和过期审核拒绝。
- 测试至少覆盖最低输入可启动、增强资料缺失不阻塞、真实阻塞进入 Needs Input、取消重跑后旧结果不再有效、确认后仅重跑受影响阶段、过期审核提交被拒绝。
- 本决定不授权业务实现、Technical Spike 执行或实际 Goal 激活。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-003、RFC-004、RFC-005；本决定不接受其技术实现方案。

## Supersedes

None.

## Amends

- DEC-005：补充两级输入门禁、真实阻塞边界与 Needs Input 产品交互态；不改变输入分层和缺少增强资料不得阻断的原则。
- DEC-009：确认失效预览、用户确认后局部重跑与受影响内容重新审核；不改变阶段级依赖范围。
- DEC-041：将“引导式任务工作台”具体化为单任务工作台信息架构；不扩大演示范围。

## Does Not Amend

- DEC-024 / DEC-025：继续使用 Versioned Domain Object 与 Source Version 的既有边界。
- DEC-029：继续执行 No Stale Review Package Submission；本决定只确认相应产品交互。

## Amended By

- [DEC-045](dec-045-minimum-input-file-limits-and-conflict-handling.md)：补全 Task / Fact Stage 门禁、默认文件限制与分级冲突行为。
- [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)：补全证据披露、修改影响识别、进度、错误、恢复与导出确认交互。
- [DEC-059](dec-059-targeted-needs-input-action-request-model.md)：补全由真实阻断派生的行动请求内容与结构化恢复动作。

## Notes

`Needs Input` 是用户可见交互语言，不是已冻结的公共 API 枚举。本决定不新增字段级依赖图、自动内容抓取、严格完整度总分或泛化防御性校验。
