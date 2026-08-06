# Session-003：正式开发前策划与长期 Goal 治理

## Metadata

- Status: In Discussion
- Date: 2026-08-06
- Topic: 正式开发前策划、文档一致性、端到端演示 MVP 与长期 Agent 执行治理
- Related RFCs: RFC-001、RFC-002、RFC-003 至 RFC-007
- Related Decisions: DEC-039～DEC-044

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

当前无未决治理提案。产品字段、交互、前端方案、RFC-003 至 RFC-007 和完整 Readiness Artifact 仍将在后续独立 Decision Gate 中提出方案。

## Accepted Decisions

- [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md) — 采用与真实风险相称的校验与审阅治理（用户于 2026-08-06 确认）。
- [DEC-040](../decisions/dec-040-autonomous-agent-execution-and-model-roles.md) — 采用分级自主执行权限与固定模型角色（用户于 2026-08-06 确认）。
- [DEC-041](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md) — 冻结本地端到端演示 MVP 的交付边界（用户于 2026-08-06 确认）。
- [DEC-042](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) — 确认证据驱动商品上新策略工作台定位、复合 Persona 假设与行为型演示成功边界（用户于 2026-08-06 接受 P-01A / P-02A / P-03A）。
- [DEC-043](../decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md) — 采用 Sol 主控、Luna 实现、Terra 辅助回退的多 Agent 开发编排（用户于 2026-08-06 确认；Amends DEC-040）。
- [DEC-044](../decisions/dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md) — 采用单任务工作台、两级输入门禁与确认式局部重跑（用户于 2026-08-06 接受 P-04A / P-05A / P-06A；Amends DEC-005 / 009 / 041）。

## Rejected Approaches

- 将过期入口声明继续视为 Current Truth。
- 在产品字段、公共契约或 RFC 未接受前直接开始业务代码。
- 用哈希清单、极低概率变体或机械评分替代核心行为验证。
- 在指定实现模型不可用时静默切换模型。

## Open Questions

- 产品定位、Persona / JTBD 假设与行为型成功边界已由 DEC-042 解决；任务工作台信息架构、输入门禁和重跑触发已由 DEC-044 解决；最终字段、详细控件、Fixture 与必要阈值仍开放。
- 四层 Brief、Review Package、Approved Strategy 与 Xiaohongshu Brief 的最终 Schema 和版本规则。
- RFC-003 至 RFC-007 与 Frontend Architecture 的具体技术选择。
- ARP-02 / 03 / 09 完整 Artifact、ARP-05 至 ARP-08 和 TS-01 至 TS-05 Charter。
- Luna 不可用时的路由已由 DEC-043 解决为 Terra 显式回退或外部 Luna 任务包；每个实际 Issue 仍需记录所用模型与独立 Reviewer。

## Deferred Topics

公开部署、Beta 用户研究执行、生产账号权限、计费、多租户、联网抓取、OCR、多媒体生成、自动发布与 Multi-Agent 扩展。

## Documentation Updates

- 新增 DEC-039～DEC-044 并更新 Decision Log。
- 更新 AGENTS.md 与 Collaboration Model。
- 后续独立 PR 同步 README、Implementation Readiness、RFC Register、Architecture / Agent 入口、Foundation、Traceability 与本地链接。

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
