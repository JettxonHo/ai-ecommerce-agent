# Session-003：正式开发前策划与长期 Goal 治理

## Metadata

- Status: In Discussion
- Date: 2026-08-06
- Topic: 正式开发前策划、文档一致性、端到端演示 MVP 与长期 Agent 执行治理
- Related RFCs: RFC-001、RFC-002、RFC-003 至 RFC-007
- Related Decisions: DEC-039～DEC-051

## Context

仓库已完成 38 份 Accepted DEC、RFC-001 / RFC-002、Spike-001、FND-001 至 FND-003 与后端工程基础。PR #28 的 Wave 1 Readiness Artifact 已按声明范围接受并合并，但入口文档、后续 RFC、产品交互、公共契约、完整 Readiness 包、测试策略和长期 Goal 尚未形成一致的开发前策划包。

用户要求先完成策划和文档固化，再展示完整结果；在用户再次明确批准前，不启动实际 Goal、不编写业务代码、不执行新的 Technical Spike。

## Goal

- 固化本地端到端演示 MVP 的产品边界；
- 明确适度校验、Git/PR 自主权限、人工 Gate 与模型分工；
- 规划产品规格、RFC-003 至 RFC-007、Readiness Artifact、Spike Charter、测试与长期 Goal；
- 修复 Current Truth 与入口文档，使后续 Agent 能基于权威文档长期执行。

## Non-goals

- 不实现业务功能、数据库、API、Worker、前端或 LLM Adapter；
- 不执行 TS-01 至 TS-05；
- 不创建或启动实际长期 Goal；
- 不在本轮临场选择 LLM Provider、前端框架或公共 API 细节。

## Existing Constraints

- Accepted Decision、Accepted RFC 与当前用户指令优先于旧 Session 和过期入口描述。
- 未确认事项不得写成实现事实；历史改变必须通过 `Amends` / `Supersedes` 追踪。
- PR #28 中 ARP-01 / 04 / 10 为完整 Artifact；ARP-02 / 03 / 09 仅为 TS-01 Minimum Slice，不能误写成完整 Artifact。
- PR #28 的合并不授权 Technical Spike、业务实现或 Goal 启动。

## Discussion

### Facts

- 用户明确接受了“正式开发前策划、文档固化与长期 Goal 接管计划”。
- 用户明确要求适度校验，禁止过度防御、非重大核心风险下的哈希 / SHA-256 要求、低概率 Case 堆叠和机械 Rubric。
- 用户明确指定 Sol/xhigh 负责高推理策划与审阅，Luna/max 负责代码实现。
- 当前可用 Agent 工具未提供 Luna，因此本轮可继续策划，但代码实现阶段必须等待指定模型可用或用户显式修改决定。

### Observations

- 现有治理把 Spike-001 的执行角色和用户 Merge Gate 写得很具体，但不能直接覆盖未来长期 Goal 的普通 PR。
- README、AGENTS、Implementation Readiness、RFC Register、Architecture / Agent 入口存在明显 Current Truth 滞后，需要独立状态同步 PR 处理。
- 产品边界已冻结到演示包络，最终字段、交互状态和公共契约仍需逐项 Decision Gate。

### Assumptions

- 演示阶段 Persona / JTBD 以明确标注的假设支撑；真实访谈在 Beta 前完成。
- 用户提供的文本型资料足以验证首个端到端闭环；OCR、图片理解和联网研究不是该闭环成立的前提。

### Proposals

- 将治理拆为三条 Decision：适度校验、Agent 自主权限与模型角色、演示 MVP 交付包络。
- 后续按“产品规格 → RFC 与公共契约 → Readiness 规划包 → 开发与测试计划 → Goal”顺序完成策划。
- 每个 RFC 采用独立 Issue、Branch、PR 与用户 Acceptance Gate；普通文档 PR 可在检查和 Review 全部通过后自主合并。

### Alternatives

1. 所有 PR 一律等待用户 Merge：控制最强，但会让长期自主执行频繁阻塞；未采用。
2. 所有事项完全自主：效率最高，但会越过产品、架构和不可逆操作的治理边界；未采用。
3. 分级权限：普通低风险工作自主闭环，高风险与治理事项人工确认；采用。

模型分工备选：

1. 单一模型完成策划、实现和 Review：交接成本低，但职责分离弱；未采用。
2. 高推理模型负责策划与 Review，实现模型按冻结规格编码：边界清晰，采用。
3. 指定模型不可用时自动降级：连续性较好但可能静默改变质量与成本假设；未采用。

### Trade-offs

- 自主合并提高吞吐量，但必须依赖小 Issue、独立 PR、完整 Required Checks 和五轴 Review。
- 收紧 MVP 范围降低首轮覆盖面，但保留了业务价值、Human Review、证据追溯和恢复等核心验证目标。
- 固定模型角色提升一致性，但 Luna 不可用时会成为实现阶段显式阻塞项。

### Risks

- Current Truth 同步不彻底会让执行 Agent 读取到相互冲突的状态。
- 产品字段或 API 在 RFC 前被过早写死会导致后续返工。
- “适度校验”可能被误读为降低质量，因此 DEC-039 明确保留关键不变量、Secret 边界和 Required Checks。

## Proposed Decisions

RFC-003 的 `P-19A`～`P-27A` 已全部由用户接受，当前没有未决 RFC-003 子决策。下一项治理 Gate 是 RFC-003 最终一致性 Review 后的整体接受；该 Gate 尚未通过，不能写成 Accepted。

## Accepted Decisions

- [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) — 采用与真实风险相称的校验与审阅治理（用户于 2026-08-06 确认）。
- [DEC-040](../decisions/dec-040-autonomous-agent-execution-and-model-roles.md) — 采用分级自主执行权限与固定模型角色（用户于 2026-08-06 确认）。
- [DEC-041](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md) — 冻结本地端到端演示 MVP 的交付边界（用户于 2026-08-06 确认）。
- [DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) — 确认证据驱动商品上新策略工作台定位、复合 Persona 假设与行为型演示成功边界（用户于 2026-08-06 接受 P-01A / P-02A / P-03A）。
- [DEC-043](../decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md) — 采用 Sol 主控、Luna 实现、Terra 辅助回退的多 Agent 开发编排（用户于 2026-08-06 确认；Amends DEC-040）。
- [DEC-044](../decisions/dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md) — 采用单任务工作台、两级输入门禁与确认式局部重跑（用户于 2026-08-06 接受 P-04A / P-05A / P-06A；Amends DEC-005 / 009 / 041）。
- [DEC-045](../decisions/dec-045-minimum-input-file-limits-and-conflict-handling.md) — 冻结最小输入、演示文件限制与分级冲突处理（用户于 2026-08-06 接受 P-07A / P-08A / P-09A；Amends DEC-005 / DEC-044，不改变 DEC-026）。
- [DEC-046](../decisions/dec-046-review-brief-and-export-product-contract.md) — 冻结审核、Brief、版本、revision 与导出的产品契约（用户于 2026-08-06 接受 P-10A / P-11A / P-12A；Amends DEC-006 / 024 / 029 / 030 / 031）。
- [DEC-047](../decisions/dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) — 采用渐进式证据披露、结构化编辑意图与行动导向恢复交互（用户于 2026-08-06 接受 P-13A / P-14A / P-15A；Amends DEC-007 / 008 / 009 / 044 / 046）。
- [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md) — 采用小型代表性验收包、行为门禁与 Markdown-first 导出（用户于 2026-08-06 接受 P-16A / P-17A / P-18A；Amends DEC-010 / 042 / 046 / 047）。
- [DEC-049](../decisions/dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md) — 采用独立 PostgreSQL Checkpoint Database、同步持久性、可重入 Node 与 Business-Current-Truth-first Reconciliation（用户于 2026-08-06 接受 P-19A / P-20A / P-21A；Amends DEC-013 / 023 / 024 / 033）。
- [DEC-050](../decisions/dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md) — 采用 PostgreSQL Durable Work Intent + Poll-and-claim、数据库权威 Lease / Heartbeat / Fencing Token 与持久化协作式取消 / Supersession（用户于 2026-08-06 接受 P-22A / P-23A / P-24A；Amends DEC-013 / 033，Complements DEC-049）。
- [DEC-051](../decisions/dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md) — 采用显式 Compatibility Tuple、Current-Truth-first 七动作 Recovery Decision、受控迁移和 Forward Repair 证据边界（用户于 2026-08-06 接受 P-25A / P-26A / P-27A；Amends DEC-013 / 033，Complements DEC-049 / 050）。

## Rejected Approaches

- 将过期入口声明继续视为 Current Truth。
- 在产品字段、公共契约或 RFC 未接受前直接开始业务代码。
- 用哈希清单、极低概率变体或机械评分替代核心行为验证。
- 在指定实现模型不可用时静默切换模型。

## Open Questions

- 产品定位、Persona / JTBD 假设与行为型成功边界已由 DEC-042 解决；工作台、输入和重跑触发已由 DEC-044 / 045 解决；审核 / Brief / 版本由 DEC-046 解决；证据 / 编辑 / 进度 / 恢复 / 导出确认由 DEC-047 解决；代表性验收包、必要行为门禁和 Markdown-first 用户导出由 DEC-048 解决。
- Review / Brief 的最终公共字段、API / 数据库 Schema、并发实现、Diff 算法、状态 / 错误映射、Markdown 模板与下载协议。
- Fixture 具体业务数据、测试工具、最终浏览器 E2E 步骤、Live Smoke 手册与 Beta 指标。
- RFC-003 已进入 `IN REVIEW`；其 DQ-01～09 已由 DEC-049～051 全部解决，整体仍待最终一致性 Review 后由用户单独接受。精确实施版本与公共字段不在 DEC-051 中虚构，继续由实施证据、RFC-004 / 007 冻结。RFC-004 至 RFC-007 与 Frontend Architecture 的具体技术选择仍开放。
- ARP-02 / 03 / 09 完整 Artifact、ARP-05 至 ARP-08 和 TS-01 至 TS-05 Charter。
- Luna 不可用时的路由已由 DEC-043 解决为 Terra 显式回退或外部 Luna 任务包；每个实际 Issue 仍需记录所用模型与独立 Reviewer。

## Deferred Topics

公开部署、Beta 用户研究执行、生产账号权限、计费、多租户、联网抓取、OCR、多媒体生成、自动发布与 Multi-Agent 扩展。

## Documentation Updates

- 新增 DEC-039～DEC-045 并更新 Decision Log。
- 更新 AGENTS.md 与 Collaboration Model。
- 后续独立 PR 同步 README、Implementation Readiness、RFC Register、Architecture / Agent 入口、Foundation、Traceability 与本地链接。
- 新增 DEC-048 与首版 Testing Strategy，更新产品 Current Truth、Readiness、Traceability 和本 Session。
- 新增 DEC-049 与 RFC-003 Draft，更新架构 Current Truth、Readiness、Traceability、RFC Register 和本 Session。
- 新增 DEC-050，接受 RFC-003 DQ-04～06，并将 DQ-07～09 的 P-25A～P-27A 方案写入 RFC Draft。
- 新增 DEC-051，接受 RFC-003 DQ-07～09，将 RFC-003 推进到 `IN REVIEW` 并同步 Compatibility、Safe Resume、迁移 / 回滚和验收证据边界。

## Synchronization Checklist

- [x] 本轮讨论已完整记录（含推理、备选、风险、被否决、开放问题）
- [x] Proposed Decisions 已记录且状态保持 Proposed
- [x] Accepted Decisions 已写入 DEC 并更新 decision-log
- [x] 受影响的治理 Current Specifications 已更新（仅限已接受决定）
- [x] 与 RFC / DEC 的双向链接已保留
- [x] 未创建任何业务实现代码

## Progress Archive — 2026-08-06

- Wave 1 Gate：PR #28 已合并，Issue #27 已关闭；六份 Artifact 按各自声明范围归档，未授权 Spike 或业务实现。
- Governance：DEC-039～041、AGENTS、Collaboration Model 与本 Session 经 Issue #30 / PR #31 归档；Sol/xhigh 五轴 Review 与 8/8 Required Checks 通过，PR #31 已按 DEC-040 自主合并，Issue #30 已关闭。
- Current Truth Sync：Issue #32 / PR #33 已合并并关闭，范围限定为入口状态、产品 Current Truth、Readiness / RFC / Foundation / Traceability 同步和 30 个失效本地 Markdown 链接修复；不包含新产品字段、RFC-003～007 技术选择、业务代码、Spike 执行或 Goal 激活。
- Link Audit：排除 `.claude/worktrees`、`.venv` 和生成目录后，Tracked Workspace Markdown 本地链接由 30 个损坏修复为 0。
- Current Truth Review：经 Sol/xhigh 独立复审三轮修正，产品、架构、Readiness、Traceability 与治理口径最终结果 = `PASS`；未把未接受事项写成实现事实。
- Product Identity and Agent Orchestration：Issue #34 / PR #35 已合并并关闭；DEC-042 / 043、Product Current Truth 与 Sol/Luna/Terra 协作规则已归档，8/8 Required Checks 全绿，未启动 Goal 或业务编码。

## Decision Round — Product Identity and Multi-Agent Orchestration（2026-08-06）

### User Acceptances

- 用户明确接受 `P-01A`：产品定位为面向中小电商商品与内容运营人员的证据驱动商品上新策略工作台。
- 用户明确接受 `P-02A`：采用一个复合主 Persona，商品运营与内容运营作为职责视角；详细 Persona / JTBD 继续标为待验证假设，真实访谈是 Beta 前门禁。
- 用户明确接受 `P-03A`：演示成功采用端到端行为与人工可用性判断，不用机械总分或销量承诺自动接受。
- 用户明确指定 Sol XHigh = `ORCHESTRATOR_REVIEWER`、Luna Max = 首选 `IMPLEMENTER`、Terra XHigh = `AUXILIARY_IMPLEMENTER` 与 Luna 不可用时的显式回退。
- 用户明确要求实现 Agent 不得最终批准或合并自己的 PR；Sol 直接实现时必须更换独立 Reviewer 或升级人工 Gate。
- 用户明确要求线程间通过文档、Issue、任务合同、Git、PR、Review 和测试记录交接，聊天上下文不能作为唯一事实来源。

### Amendment to Prior Round

DEC-040 的“Luna 不可用即阻塞代码实现”规则由本轮明确修订：Luna 仍为首选；当前工具不能创建 Luna 时，Sol 输出标准任务包供外部 Luna 使用，或显式路由 Terra XHigh。不得假装调用 Luna、不得错误归因、不得降低范围 / 测试 / Review / 验收 / 人工 Gate。

### Alternatives and Trade-offs

- “AI 营销 Brief 生成器”表达简单但弱化定位、证据与审核；未采用。
- “电商 Agent 工作台”扩展性强但范围过宽；未采用。
- 当前拆成两个完整 Persona 更细，但缺乏访谈证据；未采用。
- 立即使用统一机械评分便于自动判断，但会制造虚假精确；未采用。
- Luna 不可用即停止全部实现能保持最严格模型固定，但形成单点阻塞；由 Terra 显式回退替代。
- 单一 Agent 完成策划、实现和最终批准交接少，但缺乏独立性；未采用。
- 无任务合同的多线程并行吞吐表面较高，但接口漂移与冲突风险不可控；未采用。

### Archive Scope

- Issue #34 / PR #35 负责 DEC-042 / DEC-043、AGENTS、Collaboration Model、Product Current Truth、Readiness、Decision Log 与本 Session 的一致性归档。
- 本轮不编写业务代码、不执行 TS-01～TS-05、不创建或启动实际 Goal。

## Decision Round — Workbench, Input Gate and Partial Rerun Interaction（2026-08-06）

### User Acceptances

- 用户明确接受 `P-04A`：采用单任务工作台，以阶段导航、当前工作区和可收起证据 / 上下文面板承载完整任务。
- 用户明确接受 `P-05A`：采用两级输入门禁；最低可运行输入通过即可启动，增强 / 可选资料不强制，真实阻塞进入 Needs Input。
- 用户明确接受 `P-06A`：资料变化创建新 Source Version，系统先展示受影响阶段，由用户确认后局部重跑；旧审核自动过期且不得提交。

### Domain Clarification

- Source 内容变化沿用 DEC-025 的 `Source Version`；事实、洞察、策略或 Brief 的用户编辑沿用 DEC-024 的 Versioned Domain Object。二者不得混为同一版本类型。
- `Needs Input` 是用户可见的产品交互语言，不提前冻结 RFC-003 / 004 的 API 或数据库枚举；既有 `waiting_for_input` / `waiting_input` 概念状态的最终映射仍由 RFC 决定。
- 失效范围继续遵守 DEC-009 的阶段级依赖；DEC-044 只冻结“预览 → 用户确认 → 局部重跑 → 必要时重新审核”的交互，不引入字段级依赖图。
- DEC-029 的 No Stale Review Package Submission 保持有效；旧审核不得自动迁移为对新版本的批准。

### Alternatives and Trade-offs

- 全屏线性向导首次使用简单，但恢复、审核和证据回看上下文割裂；未采用。
- 每阶段独立页面隔离清楚，但导航与状态交接成本更高；未采用为主信息架构。
- 任意资料都允许启动摩擦最低，但会产生无法形成基础事实层的运行；未采用。
- 所有资料完整后才能启动更整齐，但会把增强资料机械化为强制项并造成过度防御；未采用。
- 编辑后自动立即重跑或每次全量重跑操作较少，但会增加调用、竞态和无关内容变化；未采用。
- 当前方案增加一次影响预览和用户确认，但换取可理解的版本变化、局部成本控制和审核安全。

### Remaining Boundaries

- 尚未确认最终输入字段类型 / 逐字段必填、文件大小 / 页数 / CSV 行数限制和具体补充问题。
- 尚未确认详细控件、视觉布局、版本差异 UI、重要 / 非重要修改的确定性识别与公共状态 / 错误映射。
- 尚未确认四层 Brief、Review Package、Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 的最终字段和外部契约。

### Archive Scope

- Issue #36 / PR #37 负责 DEC-044、被修订 Decision、Product Current Truth、Readiness、Traceability 与本 Session 的一致性归档。
- 本轮不冻结前端框架或公共 API，不编写业务代码、不执行 TS-01～TS-05、不创建或启动实际 Goal。

## Decision Round — Minimum Input, File Limits and Conflict Handling（2026-08-06）

### User Acceptances

- 用户明确接受 `P-07A`：Task 创建与 Fact Stage 使用不同门禁。Task 创建需商品名称 / 临时名称、品类和推广目标；Fact Stage 沿用 DEC-026 的核心用途、当前商品来源、有来源核心属性与无阻断性身份冲突。价格和商家当前卖点不作为全局硬必填。
- 用户明确接受 `P-08A`：演示默认上限为每任务 20 文件、10 MB / 文件、文本型 PDF 100 页、评论 CSV 10,000 行；限制可配置，但默认值属于契约。失败文件单独拒绝，已接受文件保持有效。
- 用户明确接受 `P-09A`：商品身份和形成诚实事实层必需的关键事实冲突进入 Needs Input；非阻断性证据差异继续处理并显示资料限制和受影响结论；模型不得静默选择阻断性冲突值。

### Domain Clarification

- Task 创建门禁只创建稳定 `task_id` 和工作台上下文，不代表 Fact Stage 已可运行。
- 结构化表单中的手动输入可以构成当前商品来源，不强制上传文件；竞品来源仍不能替代当前商品来源。
- DEC-045 修订 DEC-005 的旧最低字段清单，具体化 DEC-044 的两级门禁，但不改变 DEC-026 的 Fact Stage Minimum Runnable Input。
- `Needs Input` 仍是用户可见语言；正式 API / 数据库状态枚举、字段名、错误代码与前端控件由 RFC-003 / 004 和 Frontend Architecture 冻结。

### Alternatives and Trade-offs

- 把 DEC-005 的全部旧字段设为硬必填能获得更齐的表单，但价格 / 当前卖点并非所有任务都成立，会造成机械阻断；未采用。
- 只用名称 / 品类 / 目标运行全部流程摩擦最低，但无法建立有来源的事实层；三项只用于创建 Task。
- 更保守的 10 文件 / 5 MB / 50 页 / 5,000 行资源压力较低，但缺少收紧证据且限制演示资料；未采用。
- 完全不设产品限制规则最少，但错误反馈和可复现性会依赖解析器偶然行为；未采用。
- 所有冲突一律阻断规则简单但会过度防御；模型自动选择虽不中断，却破坏证据与用户判断权；均未采用。

### Remaining Boundaries

- 尚未确认公共字段名 / 数据类型、API / 数据库状态与错误枚举、前端控件和具体补充问题文案。
- 尚未确认四层 Brief、Review Package、Approved Strategy、Marketing Brief 与 Xiaohongshu Brief 的最终字段、版本和 revision 规则。
- 文件默认值已冻结；生产部署容量、性能预算与 Retention / Deletion 仍由后续 RFC、Readiness Artifact 和 Testing Strategy 处理，不从演示上限外推。

### Archive Scope

- Issue #38 / PR #39 负责 DEC-045、被修订 Decision、Product Current Truth、Readiness、Traceability 与本 Session 的一致性归档。
- 本轮不冻结公共 Schema、前端框架或 API 枚举，不编写业务代码、不执行 TS-01～TS-05、不创建或启动实际 Goal。

## Decision Round — Review, Brief and Export Product Contract（2026-08-06）

### User Acceptances

- 用户明确接受 `P-10A`：Review Package 和 Approved Strategy 使用决策导向的固定产品语义组；冻结业务语义而不把每个概念字段一对一提升为公共 Schema。
- 用户明确接受 `P-11A`：保留平台中立 Marketing Brief，并通过显式 Xiaohongshu Brief 分组做平台映射；Adapter 不得重新制定战略或补造证据。
- 用户明确接受 `P-12A`：正式业务对象使用不可变 Domain Version，Review Draft 使用单调递增 revision，Task 使用 Current Truth Pointer，导出冻结当前结果快照。

### Domain Clarification

- Review Package 是不可变审核输入快照；固定分组不代表必须展示所有上游对象，也不要求为空分组制造内容。
- Strategy Draft 是临时 Review 工作状态，不属于 Current Truth；每次成功保存 revision 递增，陈旧保存或提交拒绝。自动保存频率与 ETag / 请求头 / 数据库锁等实现留给 Frontend Architecture 和 RFC-004。
- Approved Strategy、Marketing Brief、Xiaohongshu Brief 的模型生成、用户业务编辑与重跑创建新 Domain Version，不覆盖历史。Approved Strategy 的修改仍必须经过 Human Review。
- Marketing Brief 固定六组：Objective and Audience / Message Architecture / Reasons to Believe and Evidence / Execution Direction / Constraints and Honesty / Version and Workflow Context。
- Xiaohongshu Brief 固定六组：Platform and Campaign Context / Note Format and Content Mode / Creative Structure Directions / Discovery and Action Directions / Evidence and Platform Constraints / Workflow and Version Context。
- 导出保存发起时的当前对象版本、必要上游 / 证据引用、Hypotheses / Limitations / Risks、Task 上下文和导出时间；不新增 Hash 或 SHA-256 要求。

### Alternatives and Trade-offs

- 把概念字段逐项冻结为公共 Schema 可减少实现歧义，但会在 RFC-004 前过早绑定 API / 数据库；未采用。
- 只保留候选选择、编辑和备注能简化 Review UI，但不足以支持证据、假设、限制与风险判断；未采用。
- 合并平台中立 Brief 与 Xiaohongshu Brief 会减少对象，却让平台规则泄漏到核心结构；未采用。
- 让 Adapter 从薄 Brief 补齐大量业务内容会迫使 Adapter 重新做战略；未采用。
- 每次草稿保存创建 Domain Version 会制造无业务意义的历史；可覆盖 latest + 审计日志又与 DEC-024 冲突；均未采用。

### Remaining Boundaries

> 以下为 DEC-046 归档当时的开放边界；其中引用、差异、编辑影响、进度、错误、恢复与导出确认后来由 DEC-047 部分解决，Markdown-first 用户导出后来由 DEC-048 解决。最终实现项继续开放。

- 产品语义组和版本行为已确认；最终 JSON / OpenAPI / 数据库字段、类型、枚举、逐字段必填表达和错误代码仍待 RFC-004 / 006。
- Draft 自动保存频率、Patch / Snapshot 存储、revision 传输与数据库并发机制、版本差异 UI、导出文件格式和下载交互仍待 Frontend Architecture / RFC-004。
- 引用卡片、证据覆盖、编辑粒度、进度 / 错误 / 恢复的详细交互仍待后续产品 Decision Gate。

### Archive Scope

- Issue #40 / PR #41 负责 DEC-046、被修订 Decision、Product Current Truth、Readiness、Traceability 与本 Session 的一致性归档。
- 本轮不冻结公共 Schema、前端框架、API 路径、数据库表、Prompt 或 Provider，不编写业务代码、不执行 TS-01～TS-05、不创建或启动实际 Goal。

## Decision Round — Evidence, Editing, Progress and Recovery Interactions（2026-08-06）

### User Acceptances

- 用户明确接受 `P-13A`：在当前任务上下文中使用五类标记、证据卡片或可收起面板渐进展示依据；不要求每句话密集引用，不显示未经校准数字置信度。
- 用户明确接受 `P-14A`：审核与正式 Brief 使用结构化语义组编辑和差异；明确业务修改按既有阶段级规则失效，展示性润色不触发上游重跑，歧义自由文本由用户确认一次编辑意图。
- 用户明确接受 `P-15A`：长任务使用阶段时间线、最近更新时间、等待原因和下一步动作；错误按业务恢复动作组织；导出前确认当前对象版本和限制摘要。

### Domain Clarification

- Evidence Detail 展示 Source Label、Source Version、真实可用定位、支持关系、Evidence Limitation 与 Conflict；没有可靠页码、CSV 行或文本段落时不得伪造定位。
- 直接证据可显示短摘录，综合 Insight / Strategy 可显示忠实摘要和主要依据关系；证据覆盖总分或 Rubric 不作自动接受器。
- 语义组差异至少表达修改前后、模型 / 用户来源和对象版本；最终使用行内、并排或摘要式组件仍待 Frontend Architecture。
- Marketing Brief 业务编辑创建新版本并使当前 Xiaohongshu Brief 失效；Xiaohongshu Brief 自身编辑不反向使 Approved Strategy 或 Marketing Brief 失效。
- LLM 可以解释差异，但不作为重要 / 非重要修改的最终分类 Gate；MVP 不建设字段级依赖图。
- 阶段进度是产品交互语义，不冻结 API / 数据库状态；轮询、SSE、WebSocket 或其他传输方式仍待 Frontend Architecture / RFC。
- 返回最后有效结果不改变对象有效性；失效或部分提交结果不得恢复为 Current Truth 或作为当前结果导出。

### Alternatives and Trade-offs

- 所有结论密集内联引用可见性高，但界面拥挤并容易把综合判断机械化为逐句引用；未采用。
- 独立证据页面实现表面简单，但会切断结论与当前审核上下文；不作为主要交互。
- 由模型自动判断编辑影响可减少一次确认，但不可预测且难形成确定性测试；不作为最终 Gate。
- 所有编辑一律触发失效规则最简单，却会让错别字与格式调整产生无意义重跑；未采用。
- 技术日志和百分比主导包含更多内部信息，但目标用户不应理解 Runtime，且无可靠计算基础的百分比会误导；未采用。
- 仅用 Spinner / Toast 成本最低，但不能支撑长任务、Needs Input、Review、恢复与重跑；未采用。

### Remaining Boundaries

> 以下为 DEC-047 归档当时的开放边界；其中代表性验收包、必要行为门禁和 Markdown-first 用户导出后来由 DEC-048 解决。具体模板、测试工具和浏览器步骤继续开放。

- 最终组件、布局、视觉样式、Diff 算法、逐字段编辑控件和自动保存频率。
- 最终 Source / Locator / Evidence、进度、状态、错误与恢复公共 Schema；轮询 / SSE / WebSocket 等传输方式。
- 导出文件格式、模板、下载协议与视觉布局。
- 代表性 Fixture、必要阈值和最终浏览器 E2E 步骤。

### Archive Scope

- Issue #42 / PR #43 负责 DEC-047、被修订 Decision、Product Current Truth、相关概念规格、Readiness、Traceability 与本 Session 的一致性归档。
- 本轮不冻结公共 Schema、前端框架、API 路径、数据库表、传输协议、Diff 算法、导出格式、Prompt 或 Provider，不编写业务代码、不执行 TS-01～TS-05、不创建或启动实际 Goal。

## Decision Round — Acceptance Pack, Behavior Gates and Markdown Export（2026-08-06）

### User Acceptances

- 用户明确接受 `P-16A`：首个演示使用三个固定资料包（资料充分、资料不足但可运行、阻断性冲突与恢复）和一个基于正常任务的变更脚本；Fixture 使用可读版本，不新增 Hash / SHA-256 要求。
- 用户明确接受 `P-17A`：验收采用行为硬门禁 + 人工可用性判断；固定场景关键不变量、Required Checks、Critical / Blocking = 0 与 Release Candidate 单次 Live Smoke 属完成门禁，Rubric 不作机械总分或自动接受器。
- 用户明确接受 `P-18A`：当前有效 Marketing Brief 与 Xiaohongshu Brief 分别导出 UTF-8 Markdown；首个 Goal 不提供用户侧 PDF / JSON 文件导出，API JSON 不受此用户文件决定限制。

### Acceptance Clarification

- 正常资料包完成 Fact、Insight、Positioning、Human Review、Marketing Brief、Xiaohongshu Brief 与 Markdown 导出闭环。
- 资料不足资料包必须诚实显示 Hypotheses、Evidence Limitations 与 Insufficient Information，不能为满足结构制造事实或 Proof Point。
- 冲突资料包进入 Needs Input，补料或确认后从正确阶段恢复；旧失效结果不成为 Current Truth。
- 变更脚本至少覆盖 Source Version 更新、业务语义编辑、影响预览、陈旧 Review 拒绝和用户确认后的局部重跑。
- 普通 PR 使用确定性替身；真实 Provider 只在 Release Candidate 使用正常资料包执行一次端到端 Smoke。
- 人工验收记录 `PASS / FAIL` 与理由，确认无需理解内部 Runtime 即可审核、编辑、恢复和使用导出交付物。

### Alternatives and Trade-offs

- 10～20 个行业 Benchmark 覆盖更广，但会在首个演示前形成独立评测工程；未采用。
- 仅人工临时演示准备最少，但不可重复、无法稳定发现回归；未采用。
- 加权 Rubric 总分便于比较，但在缺少样本与真实基线时制造虚假精确；未采用。
- 完全主观 Review 无法保护版本、证据、Current Truth、失效和恢复不变量；未采用。
- Markdown + 用户侧 JSON 增加机器可读性，但扩大第二套公共契约；不进入首个 Goal。
- PDF-first 展示正式，但增加排版 / 渲染链路且不利于继续编辑；不进入首个 Goal。

### Remaining Boundaries

- Fixture 的具体商品、内容、文件、目录、数据许可与 expected-output 表示。
- 测试框架、浏览器工具、命令、CI 分组、故障注入和最终 E2E 步骤。
- 最终 Provider、Prompt / Schema 版本和 Live Smoke 操作手册。
- Markdown 文件名、模板、Front Matter、下载协议和视觉样式。
- API JSON / OpenAPI、数据库字段、状态、错误与并发契约。
- Beta 用户样本、性能阈值、埋点、Dashboard 与真实业务对照实验。

### Archive Scope

- Issue #44 / PR #45 负责 DEC-048、被修订 Decision、Testing Strategy、Product Current Truth、Readiness、Traceability 与本 Session 的一致性归档。
- 本轮不创建实际 Fixture、不选择测试框架 / Provider、不冻结 API / Schema / 前端技术，不编写业务代码、不执行 TS-01～TS-05、不创建或启动实际 Goal。

## Decision Round — RFC-003 Checkpointer, Durability and Reconciliation（2026-08-06）

### User Acceptances

- 用户明确接受 `P-19A`：同一 PostgreSQL Service 下使用独立 Checkpoint Database，采用官方同步 `PostgresSaver`，并隔离 Runtime Role、Credential、Pool 与 setup / migration 生命周期。
- 用户明确接受 `P-20A`：正式 Graph 使用 `sync` durability；Graph State 紧凑、引用化；Node 可重入并遵守 `Prepare → Execute → Commit`；不承诺 Node exactly-once，只保证业务效果 duplicate-safe。
- 用户明确接受 `P-21A`：Resume / Recovery 采用 Business-Current-Truth-first Reconciliation；compatible Checkpoint 可继续，stale / foreign / incompatible Checkpoint 不得写 Current Truth，并须进入安全重跑或 Manual Recovery。

### Acceptance Clarification

- Checkpoint 与 Business Database 可共享 PostgreSQL Service，但不共享 Database、Role、Credential、Pool、Repository、Session、事务或 migration chain。
- Checkpointer setup / migration 由受控部署任务执行，API / Worker 启动不隐式修改数据库结构。
- `sync` durability 提供清晰的 Super-step 故障边界；节点仍可能在 Replay、Retry 或 Resume 中从起点重执行。
- Checkpoint 是恢复候选证据，不是恢复授权器；恢复前和业务 Commit 前均须验证 Current Truth、版本、Review、Invalidation、Lease / fencing 与幂等身份。
- Time Travel / Replay 不得作为 Business Restore 或回退 Current Truth 的机制。

### Accepted Result

- [DEC-049](../decisions/dec-049-dedicated-postgres-checkpoint-sync-durability-and-current-truth-reconciliation.md) 归档上述三项决定。
- [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md) 从 `PROPOSED` 进入 `DRAFTING`，但整体 Acceptance 仍为 `NOT GRANTED`。
- Issue #46 / PR #47 / 分支 `codex/rfc-003-runtime-checkpoint` 承载 RFC-003；Draft PR 合并不接受 RFC、不授权 TS-03、迁移、业务实现或 Goal。

### Proposed Next Decisions

- `P-22A`（推荐）：PostgreSQL Durable Work Intent + 短事务 Poll-and-claim；轮询是正确性基线，`LISTEN / NOTIFY` 只作可选 Wake-up，不引入 Broker。
- `P-23A`（推荐）：数据库权威 Lease + 单调 Fencing Token + 短事务 Heartbeat；过期 Worker 即使晚到也不能提交。
- `P-24A`（推荐）：持久化协作式取消 / Supersession + Commit Fence；外部调用可能完成，但结果在取消或失去所有权后必须丢弃。

三个提案的完整备选、优缺点与推荐理由见 RFC-003；用户明确接受前保持 Proposed。

### Archive Scope

- Issue #46 / PR #47 负责 DEC-049、RFC Draft、Architecture Current Truth、Readiness、Traceability、RFC Register 与本 Session 的一致性归档。
- 本轮不安装 LangGraph Checkpointer、不创建 Checkpoint Database、不执行 setup / migration 或 Technical Spike、不实现 Worker / Graph / API / 业务能力，也不创建或激活长期 Goal。

## Decision Round — RFC-003 Durable Dispatch, Worker Ownership and Cancellation（2026-08-06）

### User Acceptances

- 用户明确接受 `P-22A`：采用 PostgreSQL Transactional Durable Work Intent + 短事务 Poll-and-claim；轮询是工作重新发现的正确性基线，`LISTEN / NOTIFY` 仅可作为可选 Wake-up，首个 Goal 不引入独立 Broker。
- 用户明确接受 `P-23A`：采用数据库权威 Lease + Heartbeat + 单调 Fencing Token；接管后的旧 Worker 即使晚到，也不得完成 Work Intent 或提交 Current Truth。
- 用户明确接受 `P-24A`：采用持久化协作式取消 / Supersession + Commit Fence；取消请求不冒充终态，无法即时中断的 Provider 调用返回后须在取消、取代或 Ownership Loss 情况下丢弃结果。

### Acceptance Clarification

- Work Intent 产生继续遵守 RFC-002 的事务边界；Worker Claim 用短事务建立所有权，模型、检索和文件处理在事务外执行。
- Heartbeat、完成、释放和由该 Worker 执行产生的正式业务 Commit 都验证当前 Holder + Fencing Token；Lease 过期后的新 Owner 使用更高 Token。
- 轮询、批大小、Lease / Heartbeat、并发与 Shutdown 参数不在本轮机械固定，由 TS-01 / RFC-007 按证据校准。
- 取消当前 Run 不删除先前有效的 Domain Version；Task 删除、Retention 与 Legal Hold 是独立边界。
- 本决定不承诺 Worker 或外部调用 exactly-once，只保护重复或陈旧执行不形成重复 / 过期 Business Current Truth。

### Accepted Result

- [DEC-050](../decisions/dec-050-postgres-durable-dispatch-fenced-worker-ownership-and-cooperative-cancellation.md) 归档上述三项决定，并明确 Amends DEC-013 / DEC-033、Complements DEC-049。
- [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md) 的 DQ-04～DQ-06 变为 `ACCEPTED INPUT`；整体仍为 `DRAFTING`，Acceptance / Implementation / Spike / Goal 均未授权。
- Issue #46 / Draft PR #47 继续承载同一 RFC；不另建重复 Issue、Branch 或 PR。

### Proposed Next Decisions

- `P-25A`（推荐）：显式 Compatibility Tuple + 受控前向升级；只恢复明确兼容或有已测试纯转换器的状态，不原地改写历史 Checkpoint。
- `P-26A`（推荐）：Current-Truth-first Deterministic Recovery Decision；在 `resume_same_thread`、已提交结果对账、阶段 Retry、最早失效阶段 Rerun、安全边界重启、Manual Recovery 与拒绝请求之间做确定性选择。
- `P-27A`（推荐）：风险切片证据包 + Forward-compatible Rollback Matrix；真实 PostgreSQL 验证多 Worker、接管、取消、恢复和迁移，不能安全降级时停止领取并 Roll Forward。

三个提案的完整备选、优缺点与推荐理由见 RFC-003；用户明确接受前保持 Proposed。

### Archive Scope

- Issue #46 / PR #47 负责 DEC-050、RFC Draft、Architecture Current Truth、Runtime Spec、Readiness、Traceability、RFC Register 与本 Session 的一致性归档。
- 本轮不创建 Worker、Claim SQL、Lease / Heartbeat、Cancellation API、数据库或迁移，不执行 TS-01～TS-05，不编写业务代码，也不创建或激活长期 Goal。

## Decision Round — RFC-003 Compatibility, Safe Resume and Recovery Evidence（2026-08-06）

### User Acceptances

- 用户明确接受 `P-25A`：采用显式 Compatibility Tuple + 受控前向升级；可恢复执行绑定 Workflow Definition、Graph State Schema、Serializer Profile 与已验证的 Checkpointer Package / Store Schema 兼容范围，只恢复明确兼容或存在已测试纯转换器的状态，不原地改写历史 Checkpoint。
- 用户明确接受 `P-26A`：采用 Current-Truth-first Deterministic Recovery Decision；Application 层在恢复前对账 Runtime Registry、Work Intent / Ownership、Checkpoint metadata、Current Truth、Source / Review / Stage revisions、失效和幂等结果，并只返回七类受控恢复动作。
- 用户明确接受 `P-27A`：采用风险切片证据包 + Forward-compatible Rollback Matrix；真实 PostgreSQL 证据覆盖多 Worker、接管、取消、恢复与迁移，不能证明安全降级时停止领取新工作并 Forward Repair。

### Acceptance Clarification

- Compatibility Tuple 冻结兼容策略，不在策划阶段虚构精确依赖版本；实施时以官方资料、锁文件与 TS-03 证据固定实际组合。
- 七类 Recovery Action 为 `resume_same_thread`、`reconcile_committed_result`、`retry_current_stage`、`rerun_from_earliest_invalid_stage`、`restart_from_safe_boundary`、`manual_recovery_required` 与 `reject_request`。
- 每次实际恢复保留稳定 `task_id` / `thread_id`，创建新的 `run_id` 与 Attempt；Checkpoint ID 不构成客户端恢复授权。
- 历史 Checkpoint 不原地改写；旧、新 Worker 只有在各自领取兼容工作且共同遵守 Lease / fencing 时才可短暂共存。
- Checkpoint Store 不可用时只从受控备份恢复，或依据 Business Current Truth / Runtime Registry 创建安全新运行；Checkpoint 不能晋升为业务真相。
- stale Worker 成功提交、跨 Task Resume、过期 Review 被接受、取消后结果成为 Current Truth、隐式迁移或不可解释恢复分支均为停止条件。

### Accepted Result

- [DEC-051](../decisions/dec-051-explicit-runtime-compatibility-deterministic-safe-resume-and-forward-recovery-evidence.md) 归档上述三项决定，并明确 Amends DEC-013 / DEC-033、Complements DEC-049 / DEC-050。
- [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md) 的 DQ-07～DQ-09 变为 `ACCEPTED INPUT`；DQ-01～DQ-09 已全部闭合，RFC 进入 `IN REVIEW`，整体 Acceptance / Implementation / Spike / Goal 仍未授权。
- Issue #46 / Draft PR #47 继续承载同一 RFC；不另建重复 Issue、Branch 或 PR。

### Goal Sequencing Clarification

- “完成所有策划”指首个 Goal 开工所必需的产品、架构、公共契约、测试、治理与 Readiness 策划全部闭合并获得接受，不是穷举未来所有可能决定。
- 完整策划包与 Goal 文本必须先展示；Implementation Readiness Review 必须通过；用户再明确批准“进入 Goal 执行阶段”后，才能创建并启动长期 Goal。
- 在该明确批准前，不执行 TS-01～TS-05，不创建生产数据库 / 迁移 / Runtime / API / Frontend，也不编写业务代码。

### Next Gate

- 完成 RFC-003 最终一致性 Review，展示结论后由用户单独决定是否接受 RFC-003 整体。
- RFC-003 整体接受仍不自动激活 Goal；后续继续完成 RFC-006、Frontend Architecture、RFC-004 / 005 / 007、Readiness 规划包、Testing Strategy、Development Plan 与 Goal 文本。

### Archive Scope

- Issue #46 / PR #47 负责 DEC-051、RFC-003 `IN REVIEW` 状态、Architecture Current Truth、Runtime Spec、Readiness、Traceability、RFC Register 与本 Session 的一致性归档。
- 本轮不固定精确依赖版本，不创建 Compatibility Matrix 实例、转换器、Runtime Registry、Worker、数据库或迁移，不执行 TS-01～TS-05，不编写业务代码，也不创建或激活长期 Goal。

## Final Decision — RFC-003 Overall Acceptance（2026-08-06）

### User Acceptance

- 用户在 RFC-003 Final Consistency Review、独立五轴 Review 与最新 Required Checks 结果展示后，明确回复「接受 RFC-003 整体」。
- RFC-003 Status 由 `IN REVIEW` 变为 `ACCEPTED`；DQ-01～DQ-09 及 DEC-049～051 共同构成正式 Workflow Runtime / Checkpoint Architecture 基线。

### Authorization Boundary

- RFC Acceptance 不等于实现授权；Implementation、Spike Execution 与 Goal Activation 继续为 `NOT GRANTED`。
- 本次不安装生产 Checkpointer，不创建 Checkpoint Database、Runtime Registry、Worker、Graph、API、迁移或 Compatibility Matrix 实例，不执行 TS-01～TS-05，也不创建或激活长期 Goal。
- 下一策划议题为 RFC-006；之后依次闭合 Frontend Architecture、RFC-004 / 005 / 007、Readiness 规划包、Testing Strategy、Development Plan 与 Goal 文本。

## Proposal Round — RFC-006 Provider, Model Runtime Port and Structured Output（2026-08-06）

### Context and Investigation

- RFC-003 合并后，按既定依赖顺序创建 RFC-006 Issue #48、独立分支、RFC 正文与 Draft PR #49；当前只授权策划和文档，不授权 Provider 接入、模型调用、Spike、业务实现或 Goal 激活。
- 仓库调查确认 RFC-006 之前只有 RFC Register 登记，没有生产 Model Runtime、Provider Adapter 或 Prompt Registry；Spike-001 的 `ScriptedModelProvider` 只可作为测试设计参考，禁止迁入生产。
- 官方资料调查覆盖 OpenAI、Anthropic 与 Google 的 Structured Output、模型 / API 版本、错误和数据处理边界。时效性能力只作为 2026-08-06 Proposal 证据；实施时仍须复核账号访问、官方兼容性与固定验收包结果。
- RFC-006 被拆成 8 个 DQ：Provider / Model / SDK；Model Runtime Port / DI；Structured Output；Failure / Repair / Retry / Cancellation；版本；Skill Profiles / Context；Secret / Payload / Telemetry；Deterministic Substitute / Live Smoke。

### Proposed Decisions

- `P-28A`（推荐）：首个 Goal 采用 OpenAI Responses API + `gpt-5.6-terra` + 官方 Python SDK，只实现一个真实 Provider Adapter，不开放 Provider-hosted Tools；这是基于当前官方能力与项目边界的适配度推断，不是三家模型质量 Benchmark 结论。
- `P-29A`（推荐）：Application 定义窄型、typed、Provider-neutral 同步 Model Runtime Port，`platform/model_runtime` 实现单一已接受 Provider Adapter，Composition Root 注入；不建设多 Provider Gateway。
- `P-30A`（推荐）：Provider-native Strict Structured Output + 项目权威 Pydantic / JSON Schema + Skill Domain Validator；严格遵守 `Parse → Project Schema Validation → Deterministic Normalization → Domain Validator`，refusal / incomplete 为显式非成功分支。

完整的 B / C 备选、优缺点、官方证据和停止条件见 [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)。

### Decision and Authorization Status

- `P-28 / P-29 / P-30 = PROPOSED`；用户尚未接受任何选项。
- RFC-006 Status = `DRAFTING`；RFC Acceptance、Implementation、Spike Execution 与 Goal Activation 均为 `NOT GRANTED`。
- 在用户裁决前，不安装 Provider SDK、不读取 Secret、不调用模型、不创建 Prompt Runtime / Registry、不执行 Live Smoke，也不把推荐方案写成 Current Truth。

## Decision Round — RFC-006 Provider, Model Runtime Port and Structured Output（2026-08-06）

### User Acceptances

- 用户明确接受 `P-28A`：首个 Goal 只实现 OpenAI Responses API + 官方 Python SDK + `gpt-5.6-terra` 的单一真实 Provider Adapter，不开放 Provider-hosted Tools，也不建设多 Provider 路由或容灾。
- 用户明确接受 `P-29A`：Application 定义项目自有、typed、Provider-neutral 的窄型同步 Model Runtime Port，`platform/model_runtime` 实现单一 OpenAI Infrastructure Adapter，由 Composition Root 注入；Skill 不依赖 Provider SDK。
- 用户明确接受 `P-30A`：每次模型调用使用 Provider-native Strict Structured Output，但项目 Pydantic / JSON Schema 与 Skill Domain Validator 保持权威；refusal / incomplete / 无内容是显式非成功分支。

### Acceptance Clarification

- 这是基于当前官方能力与项目架构适配度的选择，不是 OpenAI / Anthropic / Google 三家模型质量 Benchmark 结论。
- 实施时记录已验证的 SDK / API / Model ID 组合；账号访问、Structured Output 兼容、固定验收包质量、延迟与成本仍须用实施证据验证。
- 若真实 Adapter 被账号、兼容性或阻塞性质量问题卡住，不得静默更换 Provider 或模型，须暂停并提交 RFC Amendment。
- Port 只抽象首个 MVP 需要的语义，不承诺无成本换 Provider，也不建设通用 Gateway。
- Structured Output 固定顺序为 Provider 分类 → Parse → 项目 Schema → 语义保持的确定性 Normalization → Skill Domain Validator → Candidate Result；结构有效不代表业务正确。

### Accepted Result

- [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md) 归档 P-28A / P-29A / P-30A。
- [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md) 的 DQ-01～DQ-03 变为 `ACCEPTED INPUT`；RFC 整体仍为 `DRAFTING`。
- Issue #48 / Draft PR #49 继续承载同一 RFC；不另建重复 Issue、Branch 或 PR。

### Remaining Decisions and Authorization Boundary

- DQ-04～DQ-08（P-31～P-35）仍未闭合；错误 / 修复 / Retry / 取消、版本、Skill Profiles、Secret / Payload / Telemetry、确定性替身与 Live Smoke 仍不得由实现 Agent 临场决定。
- RFC Acceptance、SDK 安装、Secret 读取、真实模型调用、Implementation、Spike Execution 与 Goal Activation 均为 `NOT GRANTED`。
- 本轮只归档用户决定并同步 Current Truth；不编写业务代码、不执行 TS-01～TS-05、不创建或激活长期 Goal。

## Proposal Round — RFC-006 Failure, Versioning and Skill Profiles（2026-08-06）

### Official Evidence and Constraint Check

- OpenAI 官方错误文档与 Python SDK 说明：SDK 默认会对连接错误、408、409、429 和 5xx 做有限重试，Timeout 也可能被重试；若项目再叠加 Model Runtime / Workflow Retry，会形成难以解释的嵌套预算。
- Responses Cancel API 仅能取消 `background=true` 的 Response；本项目已接受同步窄型 Port，因此不能假设 Provider 支持同步调用的中途取消，必须依赖调用前后检查、受控 Timeout 与晚到结果丢弃。
- Structured Outputs 官方示例将 `incomplete`、`refusal` 与无可解析内容作为独立非成功分支，支持 P-31 将传输失败、拒绝、不完整输出和 Candidate 校验失败分层处理。
- GPT-5.6 Terra 官方模型说明支持 `low / medium / high` 等 Reasoning Effort；P-33 只为真实 Stage 差异建立五个命名 Profile，不开放工具或动态模型路由。

### Proposed Decisions

- `P-31A`（推荐）：关闭 SDK 隐式重试；一个 Model Operation 最多 2 个 Model Call（初始 + 一次共享的 Model-assisted Recovery），两者共享最多 1 次额外传输重试，故最多 3 次 Provider Attempt；Parse / Schema 失败只对语义不变表达问题先做 Normalization 并重验，Domain Validator 失败不重复 Normalization；Incomplete Recovery、Constrained Repair 与 Candidate Regeneration 共享唯一 Recovery；Refusal 不重试；同步取消采用前后检查 + Timeout + 丢弃晚到结果；稳定 `model_call_id` / `provider_attempt_id` 并记录 Provider IDs。
- `P-32A`（推荐）：使用项目自有、可读的 Model Runtime Version Tuple，记录 Provider / API / SDK / configured+resolved Model / Prompt / Schema / Skill Contract / Validator / Profile / Context Assembly 版本；每次调用固化快照，不使用 Hash / SHA-256，不引入外部 Prompt Management SaaS。
- `P-33A`（推荐）：五个命名 Profile，初始 Reasoning 分别为 Fact=`low`、Insight=`medium`、Positioning=`high`、Marketing Brief=`medium`、Xiaohongshu Mapping=`low`；全部禁用 Provider-hosted Tools；Context 由 Application / Retrieval Runtime 按权威版本与 Evidence Package 确定性装配。

完整的 B / C 备选、优缺点、调用身份、上下文优先级、停止条件和官方链接见 [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)。

### Decision and Authorization Status

- `P-31 / P-32 / P-33 = PROPOSED`；用户尚未接受任何选项。
- RFC-006 仍为 `DRAFTING`；P-34 / P-35 尚未提出，RFC Acceptance、Implementation、Spike Execution 与 Goal Activation 均为 `NOT GRANTED`。
- 在用户裁决前，不把 Reasoning Profile、Retry 次数、版本 Tuple 或 Context Assembly 写成实现事实，也不安装 SDK、读取 Secret、调用模型或执行 Live Smoke。

## Decision Round — RFC-006 Failure, Versioning and Skill Profiles（2026-08-06）

### User Acceptances

- 用户明确接受 `P-31A`：关闭 SDK 隐式重试；单个 Model Operation 最多 2 个 Model Call、共享 1 次额外传输重试、最多 3 次 Provider Attempt；唯一 Model-assisted Recovery 覆盖 incomplete / repair / regeneration；同步取消使用前后检查、Timeout 与晚到结果丢弃。
- 用户明确接受 `P-32A`：使用项目自有可读 Version Tuple，按调用固化 Provider / API / SDK / Model / Prompt / Schema / Skill Contract / Validator / Profile / Context Assembly 版本，不使用 Hash / SHA-256 或外部 Prompt Management SaaS。
- 用户明确接受 `P-33A`：五个固定命名 Profile，Reasoning 初始档位为 Fact=`low`、Insight=`medium`、Positioning=`high`、Marketing Brief=`medium`、Xiaohongshu Mapping=`low`；无 Provider-hosted Tools；Context 由 Application / Retrieval Runtime 确定性装配。

### Accepted Result

- [DEC-053](../decisions/dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md) 归档 P-31A / P-32A / P-33A。
- [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md) 的 DQ-01～DQ-06 均为 `ACCEPTED INPUT`；RFC 整体仍为 `DRAFTING`。
- 精确 Token / Timeout 仍需实施授权后的固定资料包校准与独立 Review，不得由实现 Agent 临场自由选择。

### Authorization Boundary

- DQ-07～DQ-08（P-34 / P-35）、RFC Final Consistency Review 与 RFC 整体接受仍未闭合。
- RFC Acceptance、SDK 安装、Secret 读取、真实模型调用、Implementation、Spike Execution 与 Goal Activation 均为 `NOT GRANTED`。
- 本轮只归档用户决定并同步 Current Truth；不编写业务代码、不执行 TS-01～TS-05、不创建或激活长期 Goal。

## Proposal Round — RFC-006 Secret, Payload, Test Substitute and Live Smoke（2026-08-06）

### Official Evidence and Constraint Check

- OpenAI 官方 Production Best Practices 建议 API Key 不进入代码或公开仓库，而通过环境变量或 Secret Management Service 暴露给应用；项目 ARP-10 已进一步要求 Secret Value 只在 Adapter 内存短暂存在、任何持久化平面只允许无明文 Reference。
- OpenAI Data Controls 说明 API 数据默认不用于训练；Responses 默认或 `store=true` 时具有至少 30 天 Response Object Application State，标准 API Abuse Monitoring Logs 默认最多保留 30 天；未启用 ZDR 时，受支持模型还使用最长约 24 小时的加密 Prompt Cache Application State。`store=false` 不等于 Zero Data Retention，也不关闭这些外部留存边界。
- OpenAI Evaluation Best Practices 强调代表性、任务特定测试并结合人工判断；同时官方 Evals Platform 已进入弃用时间线。项目使用本地固定验收包与人工 `PASS / FAIL`，不依赖 Provider Evals 平台，也不把 Rubric 机械化。
- 仓库已有非 `live` 测试默认断网、`live` 显式 opt-in、`.env*` 忽略与 Secret Detection Required Check；P-35 直接复用，不建设第二套泛化测试安全层。

### Proposed Decisions

- `P-34A`（推荐）：Bootstrap 只选择固定 Credential Reference，Infrastructure Adapter 在自身边界把它解析为 `OPENAI_API_KEY` 进程环境并创建 Client；应用不加载 `.env`、不建设 Vault；Responses 显式 `store=false`，同时如实记录 Abuse Monitoring 与 Prompt Cache 的外部留存；Provider Ledger 只保存身份 / Version / Usage / Latency / Disposition；通过的 Provider-neutral Candidate 按业务生命周期保存，失败候选按 DEC-033 保存最小 Diagnostic Candidate；不持久化 Rendered Prompt、完整 Context、原始 Response 或 SDK Object；Logs / Traces 只含允许 Metadata。
- `P-35A`（推荐）：实现同 Port 的 `ScriptedModelRuntime`、断网 Port / Adapter / Workflow 三层 Contract Tests，并只覆盖已接受的代表性失败分支；Release Candidate 在显式 `live` + `RUN_LIVE_MODEL_SMOKE=1` + Secret 条件下人工执行一次 `fixture-sufficient-v1` 完整闭环，记录最小证据与人工 `PASS / FAIL`，不进入普通 PR Gate、不依赖 Provider Evals 平台。

完整 B / C 备选、数据分类、持久化允许清单、测试分层、Live Smoke 证据和停止条件见 [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)。

### Decision and Authorization Status

- `P-34 / P-35 = PROPOSED`；用户尚未接受任何选项。
- RFC-006 仍为 `DRAFTING`；全部 DQ 只有在 P-34 / P-35 被用户接受后才闭合，随后还须 Final Consistency Review 与单独的 RFC Overall Acceptance。
- 在用户裁决前，不把 Secret Resolution、`store=false`、Payload Persistence、Scripted Substitute 或 Live Smoke 流程写成实现事实，也不安装 SDK、读取 Secret、调用模型或执行 Live Smoke。
