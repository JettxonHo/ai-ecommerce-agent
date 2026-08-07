# Session-003：正式开发前策划与长期 Goal 治理

## Metadata

- Status: In Discussion
- Date: 2026-08-06
- Last Updated: 2026-08-07
- Topic: 正式开发前策划、文档一致性、端到端演示 MVP 与长期 Agent 执行治理
- Related RFCs: RFC-001、RFC-002、RFC-003 至 RFC-007
- Related Decisions: DEC-039～DEC-062
- Frontend Proposal Status: P-36～P-41 全部 Accepted；Frontend Architecture overall Accepted
- Current Planning Gate: RFC-004（Product Specification 已于 2026-08-07 整体闭合；随后依次为 RFC-005、RFC-007）
- Product Closure Status: P-42～P-47 = Accepted；Product Specification Final Consistency Review = PASS；User Overall Acceptance = Accepted

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

- 当前无未接受的 Frontend Architecture Proposal；P-36～P-41 的完整提案与接受过程保留在下方各 Decision Round。
- Frontend Architecture 整体接受不授权安装依赖、生成脚手架或编写前端，未接受的 RFC-004 / 005 / 007 公共契约不得被提前写成实现事实。
- 产品规格闭合首轮 `P-42A / P-43A / P-44A` 已由用户明确接受并归档为 DEC-057～059。
- 产品开放问题复核后形成的第二轮 `P-45A / P-46A / P-47A` 已由用户明确接受并归档为 DEC-060～062；当前不再存在未接受的产品 Proposal，等待 Product Specification Final Consistency Review。

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
- [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md) — 采用单一 OpenAI Responses Provider、窄型同步 Model Runtime Port 与 Structured Output 权威边界（用户于 2026-08-06 接受 P-28A / P-29A / P-30A）。
- [DEC-053](../decisions/dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md) — 采用有界 Model Recovery、可读 Version Tuple 与确定性 Skill Profiles（用户于 2026-08-06 接受 P-31A / P-32A / P-33A；Amends DEC-052）。
- [DEC-054](../decisions/dec-054-adapter-secret-payload-boundary-and-deterministic-model-verification.md) — 采用 Adapter Secret / Payload 边界、同 Port Scripted Substitute 与单次人工 RC Smoke（用户于 2026-08-06 接受 P-34A / P-35A；Amends DEC-052 / 053）。
- [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md) — 采用 React / Vite SPA、显式前端状态所有权、OpenAPI 生成与 npm + Vitest / Testing Library + Playwright Chromium 验证基础（用户于 2026-08-06 接受 P-36A / P-37A / P-38A）。
- [DEC-056](../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md) — 采用深 TaskWorkbench、revision-safe 交互投影与适度 Web 质量边界（用户于 2026-08-06 接受 P-39A / P-40A / P-41A；2026-08-07 接受 Frontend Architecture 整体）。
- [DEC-057](../decisions/dec-057-product-semantics-and-technical-contract-authority-boundary.md) — 以稳定产品语义闭合产品规格，并将公共 API、Retrieval、Observability 和测试物理载体交给各自权威文档（用户于 2026-08-07 接受 P-42A）。
- [DEC-058](../decisions/dec-058-fictional-anchor-sku-acceptance-fixture-strategy.md) — 采用同一虚构“城市通勤双肩包”Anchor SKU 的三个资料变体与一个 mutation（用户于 2026-08-07 接受 P-43A；Amends DEC-048）。
- [DEC-059](../decisions/dec-059-targeted-needs-input-action-request-model.md) — Needs Input 采用由当前真实阻断派生的有限结构化行动请求（用户于 2026-08-07 接受 P-44A；Amends DEC-044 / 045 / 047）。
- [DEC-060](../decisions/dec-060-evidence-bound-claim-integrity-and-proportional-compliance-boundary.md) — 采用证据约束的声明完整性与适度合规边界（用户于 2026-08-07 接受 P-45A；Amends DEC-007 / 026 / 030 / 031）。
- [DEC-061](../decisions/dec-061-task-scoped-private-material-and-reversible-removal.md) — 用户资料采用 Task 范围私有与可逆移除，不提供首个 Goal 的永久删除界面（用户于 2026-08-07 接受 P-46A；Amends DEC-014 / 025 / 041 / 044）。
- [DEC-062](../decisions/dec-062-minimal-recent-task-index-and-stable-deep-links.md) — 采用最小最近任务入口与稳定深链，不建设运营 Dashboard（用户于 2026-08-07 接受 P-47A；Amends DEC-044 / 056）。

## Rejected Approaches

- 将过期入口声明继续视为 Current Truth。
- 在产品字段、公共契约或 RFC 未接受前直接开始业务代码。
- 用哈希清单、极低概率变体或机械评分替代核心行为验证。
- 在指定实现模型不可用时静默切换模型。

## Open Questions

- 产品定位、Persona / JTBD 假设与行为型成功边界已由 DEC-042 解决；工作台、输入和重跑触发已由 DEC-044 / 045 / 059 解决；审核 / Brief / 版本由 DEC-046 解决；证据 / 编辑 / 进度 / 恢复 / 导出确认由 DEC-047 解决；代表性验收包与 Anchor SKU、必要行为门禁和 Markdown-first 用户导出由 DEC-048 / 058 解决。
- 声明风险的最小产品边界、受控本地演示的数据生命周期体验，以及跨会话返回任务的最小入口已由 DEC-060～062 解决；产品规格仅待 Current Truth 全量同步和 Final Consistency Review，不再有未接受的产品 Proposal。
- 根据 DEC-057，下列均为下游技术或实例化交接，不再冒充产品开放问题：Review / Brief 最终公共字段、API / 数据库 Schema、并发实现、公共 Change Set、状态 / 错误映射、Markdown 模板与下载协议；Fixture 物理数据、测试工具、最终浏览器 E2E 步骤和 Live Smoke 手册。
- RFC-003、RFC-006 与 Frontend Architecture 均已整体接受；RFC-004 / 005 / 007、精确实施版本、最终公共字段与运维参数仍开放。
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
- 新增 DEC-052～054，接受 RFC-006 DQ-01～08；完成 Final Consistency Review、用户整体接受、PR #49 合并和 Issue #48 关闭。
- 新增 DEC-055 / DEC-056，接受 Frontend Architecture P-36A～P-41A，完成 Final Consistency Review 与整体接受，并同步 `docs/architecture/frontend-architecture.md` Current Truth。
- 新增 DEC-057～059，接受 P-42A～P-44A，明确产品 / RFC 权威边界、虚构 Anchor SKU 验收策略和 Needs Input 行动请求模型。
- 新增 DEC-060～062，接受 P-45A～P-47A，冻结声明完整性、Task 范围资料生命周期与最小最近任务入口，并显式修订既有 Product / Skill / Frontend Decision。

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

## Decision Round — RFC-006 Secret, Payload, Test Substitute and Live Smoke（2026-08-06）

### User Acceptances

- 用户明确接受 `P-34A`：Bootstrap 只选择固定 Credential Reference，Infrastructure Adapter 在自身边界解析进程环境并创建 Client；Responses 显式 `store=false`；项目只保存最小 Provider Ledger、Provider-neutral Candidate / Diagnostic Candidate 与 Payload-free Telemetry，不持久化完整 Prompt、Context 或原始响应，并诚实记录 Provider 外部留存。
- 用户明确接受 `P-35A`：使用同 Port `ScriptedModelRuntime`、断网三层 Contract Tests 与代表性失败分支；Release Candidate 只在显式 `live` / `RUN_LIVE_MODEL_SMOKE=1` / Secret / 已接受版本同时满足时，人工执行一次 `fixture-sufficient-v1` 完整闭环，不使用机械总分或额外 Live Edge-case Matrix。

### Accepted Result

- [DEC-054](../decisions/dec-054-adapter-secret-payload-boundary-and-deterministic-model-verification.md) 归档 P-34A / P-35A。
- [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md) 的 DQ-01～DQ-08 已全部闭合。
- RFC-006 仍为 `DRAFTING`；下一 Gate 是 Final Consistency Review，之后才可请求用户单独接受 RFC 整体。

### Authorization Boundary

- RFC Acceptance、SDK 安装、Secret 读取、真实模型调用、Live Smoke、Implementation、Spike Execution 与 Goal Activation 均为 `NOT GRANTED`。
- 本轮只归档用户决定、同步 Current Truth 并执行 RFC Final Consistency Review；不编写业务代码、不执行 TS-01～TS-05、不创建或激活长期 Goal。

## Final Consistency Review — RFC-006（2026-08-06）

### Review Result

- RFC-006 的 DQ-01～DQ-08 已由 DEC-052～054 全部闭合，输入完整性检查通过。
- Provider / Port / Structured Output、Recovery / Version / Profiles、Secret / Payload / Tests 三组决定内部一致，DEC-053 / 054 对 DEC-052 的修订关系已双向记录。
- RFC-001 的 Application-owned Port / Infrastructure Adapter、RFC-002 的短事务边界与 RFC-003 的 Workflow / Run 恢复职责均未被越界；Model Operation Retry 与 Workflow Retry / Rerun 已明确分层。
- 适度校验约束保持有效：未新增 Hash / SHA-256、泛化安全平台、低概率 Case 矩阵或机械 Rubric。
- Provider 外部留存、`store=false`、非 ZDR 边界与人工 Live Smoke 均被如实记录；SDK、Secret、真实调用与实现仍未授权。
- 独立五轴 Review 结果为 `PASS`：Critical = 0、Required = 0、Optional = 0；本地 Markdown 链接检查为 1512 / 1512 通过。

### Gate Result

- RFC-006 Status 从 `DRAFTING` 进入 `IN REVIEW`；Final Consistency Review = `PASS`。
- 下一且唯一的 RFC Gate 是用户明确接受 RFC-006 整体；PR 合并本身不能替代整体接受。
- RFC Overall Acceptance、SDK 安装、Secret 读取、真实模型调用、Live Smoke、Implementation、Spike Execution 与 Goal Activation 仍为 `NOT GRANTED`。

## Final Decision — RFC-006 Overall Acceptance（2026-08-06）

### User Acceptance

- 用户在 RFC-006 Final Consistency Review、独立五轴 Review 与最新 Required Checks 结果展示后，明确回复「接受 RFC-006 整体」。
- RFC-006 Status 由 `IN REVIEW` 变为 `ACCEPTED`；DQ-01～DQ-08 及 DEC-052～054 共同构成正式 LLM Runtime and Structured Output 架构基线。

### Authorization Boundary

- RFC Acceptance 不等于实现授权；SDK Installation、Secret Read、Live Model Call、Implementation、Spike Execution 与 Goal Activation 继续为 `NOT GRANTED`。
- 本次不安装或升级 Provider SDK，不读取真实 Secret，不调用真实模型或执行 Live Smoke，不创建 Model Runtime、Provider Adapter、Prompt、Fixture 或测试 Harness，不执行 TS-01～TS-05，也不创建或激活长期 Goal。
- 下一策划议题按既定依赖顺序为 Frontend Architecture；之后继续闭合 RFC-004 / 005 / 007、Readiness 规划包、Testing Strategy、Development Plan 与 Goal 文本。

## Proposal Round — Frontend Application, State and Verification Foundation（2026-08-06）

### Context and Investigation

- RFC-006 合并后已创建 Frontend Architecture Issue [#50](https://github.com/JettxonHo/ai-ecommerce-agent/issues/50) 与独立分支 `codex/frontend-architecture`。仓库当前不存在前端包、JavaScript Package Manager Lockfile 或前端实现，因此本轮没有兼容遗留前端的负担，也不得借策划名义安装依赖或生成脚手架。
- 已接受的产品形态是受控单工作区的引导式任务工作台，浏览器负责资料输入、长任务进度、补充资料、结构化审核、结果查看与 Markdown 导出；业务状态属于后端 Task / Run / Review / Brief，不属于聊天记录或浏览器内存。
- 首个 Goal 没有公开部署、SEO、服务端渲染、账号、多租户或前端直连 Provider 的需求；前端与独立 Python REST API / Worker 进程协作，长任务允许轮询，公共资源、状态与错误契约由后续 RFC-004 冻结。
- Vite 官方文档提供 React + TypeScript 模板、开发代理和静态构建；React Router 官方把 Declarative Mode 定位为由应用自行拥有数据层时的基础路由方式，而 Data / Framework Mode 增加 loader、action、pending state 或服务端能力。Next.js Static Export 可以产出静态站点，但其 Server Features 在该模式下不可用。
- TanStack Query 提供可按 Query 状态动态停止的 `refetchInterval`；`openapi-typescript` / `openapi-fetch` 可从 OpenAPI 3.1 生成 `paths` 类型并提供基于原生 `fetch` 的类型化客户端；React Hook Form 提供 TypeScript 表单、Field Array 和低重渲染的受控边界。
- Vitest 与 Vite 共享配置和转换管线；Playwright 可以在测试前启动一个或多个本地 Web Server，并保存失败诊断证据。首个 Goal 只需要代表性 Chromium E2E，不需要在每个 PR 机械运行三浏览器矩阵或再建设一层通用 Mock Server。

### P-36 — Application Shape, Framework, Routing and Build

#### Option A — React 19 + TypeScript + Vite 8 SPA + React Router Declarative Mode（推荐）

- 在 RFC-001 已接受的唯一前端根 `apps/web/` 建立纯浏览器 SPA；React 19 负责 UI，Vite 8 负责开发与静态构建，React Router Declarative Mode 只负责可链接的 Task / Stage / Panel 导航。
- 浏览器只调用同源 `/api`；开发期由 Vite Proxy 转发到本地 Python API，构建产物为静态资源。首个 Goal 不使用 SSR、React Server Components、Route Loader / Action 作为业务状态层，也不让 Node 成为生产 API 进程。
- 冻结 Major-line 与能力边界；精确 Patch、Node 兼容组合和 Lockfile 只在实施 Issue 中依据官方兼容性证据固定，不由实现 Agent 临场改架构。
- 优点：与独立 Python API、P-37 选择的独立数据层和本地演示边界贴合；开发 / 构建链短；路由、远程状态和表单职责分离。
- 代价：需要项目自行定义工作台模块、Error Boundary 与数据预取规则；未来若确需 SSR，要另立架构 Decision。

#### Option B — React Router Framework Mode

- 使用同一 React Router 同时承担路由、Loader / Action、Pending State、代码分割与可选服务端渲染。
- 优点：路由数据约定完整，未来增加 SSR 的路径更直接。
- 代价：若与 P-37A 组合，Loader / Action 会与 TanStack Query 的缓存、Mutation 和长轮询职责重叠；只有选择 P-37C 时才充分利用该模式，但仍会引入首个 Goal 不需要的服务端 / 构建约定。

#### Option C — Next.js App Router + Static Export

- 使用 Next.js App Router，但演示环境只产出 Static Export，并继续调用独立 Python API。
- 优点：生态成熟，文件路由、代码分割和未来公开站点能力完整。
- 代价：Static Export 下 Server Features 不可用；为了当前无 SEO / SSR 需求的内部工作台承担额外缓存、Server / Client Component 与构建语义。

#### Recommendation

选择 `P-36A`，并与 `P-37A` 组合。它把浏览器客户端保持为浅层适配器：路由表达位置，独立 Query Layer 表达远程状态，后端仍是业务状态权威；不会为首个本地演示引入第二个应用服务器模型。

### P-37 — Remote State, Form State and Generated API Contract

#### Option A — Explicit Ownership + TanStack Query + React Hook Form + OpenAPI Generation（推荐）

- TanStack Query v5 独占 Task / Run / Source / Review / Brief 等远程资源缓存、Mutation、失效和长任务自适应轮询；终态、`needs_input`、待审核或错误态出现后停止对应轮询，后台标签页沿用库的节流 / 暂停语义。
- React Hook Form v7 只拥有尚未保存的输入、补充资料和 Review 表单编辑缓冲；已经保存的 Review Draft、单调 revision 与跨标签恢复状态仍属于后端远程资源，由 TanStack Query 的 Query / Mutation 同步。React 局部状态只保存短命视觉状态，URL Route / Search Params 保存可分享的 Task、Stage 与 Panel 选择。首个 Goal 不引入 Redux 或 Zustand。
- RFC-004 产出的已提交 OpenAPI 3.1 Artifact 是 HTTP Contract 唯一权威；`openapi-typescript` 生成类型，`openapi-fetch` 提供原生 `fetch` Client。生成文件是不可手改的派生产物，随 Contract 变更提交，并由 `api:generate` + clean-diff Gate 防止漂移，不创建第二套手写 DTO。
- 组件不得直接调用 `fetch`。一个窄型 API Client / Query Adapter 负责 Request Identity、标准错误归一化和 DTO 到 View Model 的投影；业务 Revision / Idempotency / Stale Conflict 语义仍由 RFC-004 定义。
- 前端同步校验只服务即时 UX；后端和公共 Contract 保持最终权威。首个 Goal 不把全部后端 Schema 机械复制为 Zod，也不为同项目 API 的每个响应重复运行通用 Runtime Validation；真正的非类型输入在其边界做针对性解析。
- 优点：远程、表单、URL 和视觉状态边界明确；适合长轮询与结构化审核；Contract Drift 可被 CI 直接发现。
- 代价：需要维护 Query Key / Invalidation 约定和生成步骤；如果未来出现大量跨页纯客户端状态，再单独评估 Store。

#### Option B — Redux Toolkit + RTK Query + Centralized Draft State

- Server Cache、Form Draft、Wizard 和视觉状态统一进入 Redux Store。
- 优点：单一调试面板和集中式事件流，复杂跨页离线编辑时有优势。
- 代价：当前单任务工作台会把后端 Current Truth、表单草稿和短命 UI State 混在一起；Boilerplate 和失效逻辑重于实际需求。

#### Option C — React Router Framework Data APIs + Native Form / Custom Fetch（仅兼容 P-36B）

- 用 Loader / Action / Fetcher 管理所有远程读写，自建轮询和缓存；复杂表单使用原生 React State。
- 优点：依赖少，导航和请求生命周期统一。
- 代价：长任务轮询、跨 Panel Cache、Revision Conflict 和 Field Array 会转化为项目自有基础设施；Route 生命周期与业务执行状态耦合。

#### Recommendation

选择 `P-37A`。它只为已经存在的三类复杂度选专用工具，不提前建设全局客户端状态平台；OpenAPI 生成链把 RFC-004 公共契约连接到前端而不产生手写重复定义。

#### Compatibility Matrix

| Application choice | P-37A | P-37B | P-37C |
|---|---:|---:|---:|
| P-36A — Vite SPA + Declarative Router | 推荐 | 可兼容，但偏重 | 不兼容；需改选 P-36B |
| P-36B — React Router Framework Mode | 可兼容，但须禁用重复 Loader / Action 数据职责 | 可兼容，但偏重 | 原生组合 |
| P-36C — Next.js Static Export | 可兼容 | 可兼容，但偏重 | 不兼容；不是 React Router Runtime |

推荐组合是 `P-36A + P-37A`。若用户选择表中“不兼容”的组合，该组不能归档为 Accepted，必须重新裁决或通过后续 Decision 正式修订，而不是让实现 Agent 自行调和。

### P-38 — Frontend Verification, Package Policy and Local Execution

#### Option A — npm + Vitest / Testing Library + Playwright Chromium（推荐）

- 使用实施开始时仍处于 Active LTS、且被已接受 Vite Major 官方支持的 Node 版本，配套 npm 与提交的 `package-lock.json`；精确版本在实施 Issue 的兼容性证据中固定，不为单一前端包引入 pnpm Workspace、Yarn 或 Bun。依赖升级和 Major 迁移保持独立 Issue / PR。
- PR 基线为 Prettier Format Check、ESLint、`tsc --noEmit`、Vitest + React Testing Library / `user-event` 的 Unit / Component / State Transition Tests、类型化 API Client Contract Tests 和 Vite Production Build。
- Playwright Chromium 覆盖关键浏览器纵向切片；涉及关键流程的前端 PR 跑相关 E2E，Release Candidate 跑完整固定 E2E。Firefox / WebKit 与 Visual Regression 只有出现明确发布目标或代表性缺陷时再提案，不作为首个 Goal 的机械矩阵。
- Unit / Component Tests 使用注入式 Typed Transport / Fixture；Playwright 使用确定性本地 API / Model Substitute。首个 Goal 不额外建设通用 MSW 平台，也不允许测试访问真实 Provider。
- `npm run dev` 是前端单独启动入口，使用固定严格端口和同源 `/api` Development Proxy；`npm run build` 是可发布构建入口，`npm run preview` 只用于本地构建预览、不冒充 Production Server。完整数据库 / API / Worker / Frontend 一键命令在 RFC-004 / 005 / 007 后由 Development Plan 冻结，但必须调用这些标准脚本并正确回收子进程。
- 优点：Vite-native、配置少、失败反馈快；把行为测试和真实浏览器 E2E 分层，符合适度校验原则。
- 代价：jsdom Component Test 不是完整浏览器；由少量关键 Playwright E2E 补齐，而不是把所有组件测试搬进浏览器。

#### Option B — pnpm Workspace + Vitest Browser Mode + Playwright Chromium（Browser-first Stack）

- 使用 pnpm Workspace 管理前端及未来可能的 TypeScript Package；Component Test 使用 Vitest Browser Mode，关键 E2E 仍使用 Playwright Chromium。Firefox / WebKit 与 P-38A 一样只在明确发布目标出现后启用，不绑定每 PR 三浏览器矩阵。
- 优点：依赖存储高效，组件交互在真实浏览器运行；若后续确实出现多个 TypeScript Package，Workspace 边界更自然。
- 代价：仓库当前只有一个计划中的前端 Package；额外 Package Manager / Workspace 约定没有即时收益，Browser Mode 与 Playwright E2E 仍存在两层浏览器测试职责和更高运行成本。

#### Option C — npm + Jest / Testing Library + Cypress

- 优点：工具成熟、交互式调试体验广泛。
- 代价：Jest 需维护与 Vite 不同的转换 / Alias 配置，Cypress 又形成另一套 Dev Server 和 E2E 约定；没有证据表明这些额外边界能提升本项目首个 Goal 的可靠性。

#### Recommendation

选择 `P-38A`。它提供静态检查、行为测试、Contract、Build 和关键浏览器闭环，同时刻意不扩大为多 Package Manager、多浏览器或泛化 Mock 平台。

### Primary Sources

- [Vite Guide](https://vite.dev/guide/) 与 [Vite Server Proxy](https://vite.dev/config/server-options.html#server-proxy)
- [React `createRoot`](https://react.dev/reference/react-dom/client/createRoot)
- [React Router Modes](https://reactrouter.com/start/modes) 与 [Declarative Routing](https://reactrouter.com/start/declarative/routing)
- [Next.js Static Exports](https://nextjs.org/docs/pages/guides/static-exports) 与 [Single-Page Applications](https://nextjs.org/docs/app/guides/single-page-applications)
- [TanStack Query `useQuery`](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery)
- [OpenAPI TypeScript](https://openapi-ts.dev/) 与 [OpenAPI Fetch](https://openapi-ts.dev/openapi-fetch/)
- [React Hook Form](https://github.com/react-hook-form/react-hook-form)
- [Vitest Guide](https://vitest.dev/guide/) 与 [Playwright Web Server](https://playwright.dev/docs/test-webserver)

### Decision and Authorization Status

- `P-36 / P-37 / P-38 = PROPOSED`；推荐项分别为 `P-36A / P-37A / P-38A`，用户尚未接受任何选项。
- `P-39～P-41`（工作台模块 / UI Primitive、运行 / 审核 / 冲突状态投影、可访问性 / 浏览器 / 响应式 / 性能边界）将在首轮裁决后提出，避免把相互依赖的六项决定一次性机械打包。
- Frontend Architecture Current Truth、Decision Record、Implementation、依赖安装、脚手架生成、浏览器测试执行与 Goal Activation 均为 `NOT GRANTED`。

## Decision Round — Frontend Application, State and Verification Foundation（2026-08-06）

### User Acceptance

- 用户明确确认推荐组合 `P-36A + P-37A + P-38A`。
- 应用基础采用 `apps/web/` 下的 React 19 + TypeScript + Vite 8 SPA 与 React Router Declarative Mode；状态采用 TanStack Query / React Hook Form / URL / React Local State 的显式所有权；HTTP Contract 使用 RFC-004 OpenAPI 3.1 Artifact → `openapi-typescript` / `openapi-fetch` 生成链；验证采用 npm + Vitest / Testing Library + Playwright Chromium。

### Accepted Result

- [DEC-055](../decisions/dec-055-frontend-application-state-and-verification-foundation.md) 归档 P-36A / P-37A / P-38A。
- [Frontend Architecture](../architecture/frontend-architecture.md) 只同步已经接受的应用、状态、生成契约与验证基础，并明确标记 `PARTIAL CURRENT TRUTH`。
- Draft PR #51 的首轮 8 项 Required Checks 全部通过；独立审查结果 Critical = 0、Required = 0、Optional = 0。

### Authorization Boundary and Next Gate

- 接受不授权依赖安装、脚手架、组件、路由、样式、Client、测试、CI、业务实现、Spike 或 Goal。
- Frontend Architecture 仍未整体闭合；下一轮 P-39～P-41 负责工作台 Module / UI Primitive / Styling、状态 / 错误投影与自动保存 / Diff，以及可访问性 / 浏览器 / 响应式 / 性能边界。

## Proposal Round — Frontend Workbench Modules, Interaction Projection and Quality Boundary（2026-08-06）

### Investigation and Design-It-Twice Result

- 三个独立 Sol 设计上下文分别以“最小 Interface / 最大 Depth”“最大扩展性”“默认目标用户路径最简单”为目标，设计了 Workbench Module 的不同 Seam；均只读审阅 DEC-044～048、RFC-001 与 DEC-055，没有修改文件或冻结 RFC-004 字段。
- 最小 Interface 与默认路径方案均收敛为一个深 `TaskWorkbench Module`：Router 只负责打开新任务或稳定 Task Context，Query、RHF、轮询、Review revision、失效、证据、恢复和导出复杂度隐藏在 Module 内部。
- 最大扩展性方案提出静态 Feature Contribution Registry；它适合频繁增加 Stage / Panel，但会引入 Registry、Contribution Taxonomy、排序和配置诊断。首个 Goal 的 Stage / Panel 已固定，没有证据支持提前建设内部插件框架。
- Radix Primitives 官方定位为可增量采用、无样式且处理复杂控件 ARIA、键盘与焦点细节的低层 Primitive；shadcn/ui 把实际组件源码交给项目并以 Tailwind 提供默认样式；Material UI 提供完整 Material 组件体系。三者都可行，但锁定程度和本地维护面不同。
- WCAG 2.2 是 W3C Recommendation；Playwright 官方说明 `@axe-core/playwright` 只能发现部分常见问题，仍须键盘 / 焦点等人工检查。性能要求遵循 Measure → Identify → Fix → Verify，不在没有实现基线时机械复制公共网站预算或 Lighthouse 总分。

### P-39 — Workbench Module, UI Primitive and Styling

#### Option A — One Deep TaskWorkbench Module + Native/Radix Primitives + CSS Modules（推荐）

- `app` 层只负责 Composition、Provider 和外层 Declarative Router；它拥有 `/tasks/new` 与稳定 Task Route 的匹配和 Task Identity 提取。一个深 `TaskWorkbench Module` 负责校验 / 规范化该 Task 内可链接的 Stage / Panel 位置并投影 Active Workspace；Router 不学习 Upload、Start、Resume、Review、Rerun 或 Export 的逐动作回调。
- Workbench 内部保持固定的私有 Module：Intake、Progress / Recovery、Review、Results / Export、Evidence / Context；它们共同消费 P-40 的 `WorkbenchProjection`、产生语义化 `WorkbenchIntent`，不直接消费 HTTP DTO，也不互相导入 Implementation。
- Python API 属于 remote-but-owned 依赖，在内部 Seam 只保留两个真实 Adapter：基于生成 Client 的 Typed HTTP Adapter，以及驱动固定资料包 / 变更脚本的 Deterministic Test Adapter。TanStack Query 包装该 Seam 并拥有 Cache、Mutation、失效和轮询。
- UI Primitive Module 优先使用语义化原生 HTML；只在 Dialog、Alert Dialog、Popover、Tabs、Tooltip、Collapsible 等原生能力不足的复杂交互按需使用兼容 React 19 的 Radix Primitives，不一次性安装或暴露整套控件。
- 用户、Source 与 Model 提供的文本默认只通过 React Text Rendering 展示，禁止 `dangerouslySetInnerHTML` 或 Raw HTML。若某个已接受的用户路径需要 Markdown Preview，则关闭 Raw HTML、只允许明确的安全 Link Protocol，并用行为测试覆盖代表性文本 / 链接；在没有 Raw HTML 边界时不建设泛化 Sanitizer 平台。
- Styling 使用 CSS Modules + 少量语义 CSS Custom Properties，集中定义 Color、Typography、Spacing、Radius、Elevation、Focus 与 Motion Token；不引入 Tailwind、CSS-in-JS Runtime 或完整主题框架。
- 视觉方向为专业、证据优先的信息工作台：稳定 Stage Timeline、清晰 Active Workspace、按需 Evidence Context、一个主要 Accent；禁止 Chat Bubble 主界面、无意义 Card Grid、虚构百分比 / 置信度和只靠颜色表达状态。
- 优点：外部 Interface 最小，删除 Workbench Module 后复杂度会重新散落，说明其 Depth / Leverage 真实；HTTP、状态投影、视觉 Primitive 与 Feature Change 各有明确 Locality；视觉不受 Material 或通用模板支配。
- 代价：WorkBench 内部较深，必须通过私有 Module 保持可维护；CSS 视觉实现比采用完整组件套件需要更多项目自有设计判断。

#### Option B — Static Contribution Registry + shadcn/ui / Tailwind

- Stage 与 Panel Module 通过静态 Registry 贡献 Route、Placement、Renderer 和 Action；使用 shadcn/ui 源码组件、Tailwind Utility 与 CSS Variable Theme。
- 优点：新增已批准 Stage / Panel 时 Host 基本不变；开源组件有较好默认视觉，源码可直接修改。
- 代价：当前固定工作台会承担 Registry、Contribution、排序与生成组件维护；若继续增加 Slot / Hook / Middleware 容易演变为内部插件框架，Tailwind Class 与生成源码也扩大 Review 面。

#### Option C — Route-first Stage Pages + Material UI

- 每个 Stage 作为独立 Route Feature，使用 Material UI 完整组件与 Theme；共享 Query / Form Utility 协调远程状态。
- 优点：上手快、组件丰富，独立 Stage Page 易于局部开发。
- 代价：跨 Stage 的 Current Truth、Evidence、Review revision、恢复和导出规则会散落到多个 Route；Material 视觉与 Runtime Styling 锁定更强，单任务上下文与深 Module 的 Locality 较弱。

#### Recommendation

选择 `P-39A`。它结合最小 Interface 与默认路径两项独立方案，并拒绝为尚未出现的扩展需求提前建设 Contribution Registry。Radix 只解决真正复杂的可访问交互，CSS Modules 与语义 Token 保留工作台自身的视觉语言。

### P-40 — Interaction Projection, Autosave, Diff and Recovery Surface

#### Option A — Derived WorkbenchProjection + Intent / Capability + Serialized Autosave（推荐）

- 在 `TaskWorkbench Module` 内建立私有、判别明确的 `WorkbenchProjection`；它由 RFC-004 资源、TanStack Query 状态、当前 Mutation、URL 与本地编辑缓冲确定性派生，不是第二套业务状态机或公共枚举。
- Active Workspace 使用产品模式表达 `intake`、`running`、`needs_input`、`review`、`invalidation_preview`、`results`、`recovery` 与 `unavailable`；实际 RFC-004 状态名可不同。每次突出一个当前主要动作，Stage Timeline、最后有效结果与少量合法次动作保持可达。
- 可用 Action 只能来自 RFC-004 接受的 Resource / Command Capability 与本地 Mutation 状态；前端不得根据显示文案或未知状态猜测写操作。业务 Cancel 是显式 Intent，浏览器 Abort 只取消等待。
- 状态同时出现时使用固定产品优先级：无可用成功快照且首次读取明确失败 / Task 不存在 → Unavailable；当前写入 Conflict / Confirmation → 恢复或确认面；Needs Input → 补料 / 裁决；Human Review → Review；待确认失效 → Invalidation Preview；Active Run → Running；当前有效结果 → Results；其余 → Intake。已有成功快照但暂时刷新失败时保持原产品模式并加 `stale + retry` 状态，而非改成 Unavailable；依赖新鲜前置条件的远程写入暂停到刷新成功，本地编辑缓冲保留。旧有效结果可以作为明确标记的辅助内容查看，但失效结果不得显示为 Current Truth 或导出。
- Review Draft 使用短空闲 Debounce 自动保存，实施默认值为 1 秒且一次只允许一个 Save Mutation；In-flight Save 期间继续编辑时只排队最新缓冲，前一 Save 成功后使用其返回的新 revision 保存最新缓冲，不回放中间快照。保存状态明确显示 `saving / saved / unsaved / conflict` 产品语义。1 秒是可由真实输入体验证据在实施 Issue 中调整的起始配置，不改变状态所有权或提交语义时无需另立架构 Decision；精确 HTTP revision 字段和并发实现仍由 RFC-004 冻结。
- DEC-047 所定义的歧义自由文本必须先由用户确认编辑意图，才能进入相应 Save Queue；未确认内容保留为本地未保存缓冲。自动保存失败时保留缓冲并显示持久 `unsaved` 与手动重试，不无限重试或丢弃内容。Submit 必须等待 In-flight Save 与最新缓冲 Flush，且只使用最后一次成功 Flush 返回的新 revision；任何 Save / Flush 失败、Conflict 或未确认编辑意图都阻止 Submit，不得退回旧 revision 提交。Stale / Superseded 时保留本地缓冲、刷新权威 Draft、按语义组比较并由用户决定重新应用或放弃，不自动 Merge / 覆盖 / 提交。
- Diff 的权威单位是结构化语义组 + Field Path + Before / After + Model / User Origin + Object Version；长文本可提供基于词或行的视觉辅助，但不改变 Field-level Change Set，也不使用 LLM 分类器替用户作编辑意图 Gate。
- Field Error 放在字段旁；单文件拒绝留在文件行；Needs Input / Review / Invalidation 是正常 Workspace；暂时读取失败保留最后成功快照、更新时间与手动重试；不可恢复 UI Error 进入 Route Error Boundary。Toast 只用于非关键短暂确认，不作为错误、Conflict 或未保存状态的唯一载体。
- Query Mutation 不乐观制造 Current Truth。成功后按统一规则失效 / 刷新再投影；轮询只在 Active Run 等需要远程变化的模式继续，并在业务等待、审核、终态或明确错误时停止。
- 优点：可靠性规则集中且可通过 Module Interface 验证；不会复制后端 FSM；自动保存、Conflict、Diff 和错误都与已接受 revision / Current Truth 语义一致。
- 代价：Projection 和 Intent Mapping 需要集中维护；默认 1 秒 Autosave 仍须用真实表单交互验证，若证据显示影响输入，应在实施 Issue 中调整并记录，但不得改变串行保存、revision 链与 Submit 阻断语义。

#### Option B — XState Client Actor + Explicit Statechart

- 用 XState v5 Actor / Statechart 表达 Workbench 模式、Autosave、轮询、Conflict 和恢复，TanStack Query 作为被调用 Actor。
- 优点：复杂并发状态可视化，Transition 与 Guard 明确，适合多个客户端拥有的长流程。
- 代价：本项目业务流程已经由后端 Domain / Workflow / Runtime 拥有；再建 Client Statechart 容易复制状态和 Transition，增加 Query / Actor 同步、Hydration 和调试复杂度。

#### Option C — Route-local Conditions + Explicit Save + Toast-oriented Feedback

- 每个 Stage Page 自行组合 Query、Form、条件判断和 Toast；Review 只用显式 Save，Diff 使用通用文本比较。
- 优点：首批页面代码直观，中央 Projection 较少。
- 代价：状态优先级、轮询、未保存、Conflict、最后有效结果和恢复规则散落；通用文本 Diff 无法可靠表达语义组、来源与版本，Toast 也不能承载持久恢复状态。

#### Recommendation

选择 `P-40A`。它把复杂度放在一个深 Module 内的私有 Projection / Intent Seam，而不是复制后端状态机；1 秒串行 Autosave、语义组 Diff 和持久恢复面能直接验证 DEC-046 / 047 的核心用户行为。

### P-41 — Accessibility, Browser, Responsive and Performance Boundary

#### Option A — WCAG 2.2 AA Baseline + Chromium Support + Evidence-driven Performance（推荐）

- WCAG 2.2 A / AA 作为所有首个 Goal Workbench 状态的设计与验证基线，但不宣称未经完整审计的法律合规认证。使用语义化 HTML、完整 Label / Description、键盘导航、可见 Focus、合理 Focus 进入 / 返回、非颜色唯一状态、`prefers-reduced-motion` 与必要的异步状态 Announcement。
- 关键 Browser E2E 在现有 Playwright Chromium 中加入少量代表性 `@axe-core/playwright` A / AA 自动检查；同时人工验证完整键盘主路径、Dialog / Drawer Focus、动态状态 Announcement、200% Text Resize，以及主流程在等价 `320 CSS px` 宽度 / 400% Zoom 下的 WCAG Reflow。自动扫描不能替代人工判断，也不建立大量页面扫描矩阵。
- 首个 Goal 的正式支持目标是当前稳定 Desktop Chrome；Playwright Chromium 是硬 Gate，Release Candidate 在实际 Chrome 上人工 Smoke。Edge / Firefox / Safari 保持 Best-effort，不作支持声明或阻塞 Gate；出现明确发布目标或代表性缺陷时再升级。
- 视觉以 `1280×800` 桌面工作台为主要目标；`1024×768` 保持完整多区布局或可收起 Context；`768×1024` 使用单列 Active Workspace，Stage Navigation 与 Evidence Context 变为可访问的折叠区 / Sheet，仍可完成资料、Needs Input、Review、结果与导出主路径。等价 `320 CSS px` 只验证支持桌面 Chrome 在高缩放下的关键路径 Reflow，不构成手机设备、触控手势或手机专用布局的发布支持；手机专用优化不进入首个 Goal。
- 页面级不允许横向滚动；宽表或长 Locator 可以在自身 Region 内滚动。证据、历史和长 Diff 按需加载；评论 / Evidence 列表不得无界抓取或一次渲染全部记录，精确 Pagination Contract 由 RFC-004 / 005 冻结。
- 性能采用 Measure → Identify → Fix → Verify：首个完整纵向切片形成固定本地 Profile 基线，记录冷构建后的 Shell 可见、Task Hydration、表单输入、Stage 切换、轮询更新和 Evidence / Diff 打开体验；Release Candidate 在同一 Profile 复测并保留差异理由。
- 在取得基线前不设置公共网站 Core Web Vitals、Lighthouse 总分、Bundle KB 或固定毫秒为自动 Goal Gate。可观察的输入卡顿 / 丢失、长任务轮询导致整页闪烁、无界 Fetch / Render、失去 Focus、Evidence 打开阻塞主操作属于阻塞 Finding；具体 Bottleneck 必须先 Profile 再优化，不预先散布 `memo` / `useMemo` 或通用虚拟化。
- 优点：对真实工作台风险建立明确、代表性且可执行的质量边界；支持常用桌面与平板宽度，不扩大为手机或三浏览器产品；性能要求有证据而非虚假精确度。
- 代价：Firefox / Safari 与手机不是首个发布承诺；没有前置数字预算意味着首个纵向切片必须认真建立可复测基线和人工可用性结论。

#### Option B — Full Modern-browser + Mobile + Automated Compliance / Performance Matrix

- Chrome、Edge、Firefox、Safari 与手机视口全部作为硬支持；每 PR 运行多浏览器 E2E、全状态 Axe、Visual Regression 与 Lighthouse / Bundle 数字预算。
- 优点：覆盖广、自动指标完整。
- 代价：明显扩大首个本地演示的设计、CI、调试和发布范围；自动工具仍不能证明完整可访问性，固定预算在没有实现基线时容易机械化。

#### Option C — Desktop Chromium Visual QA Only

- 只保证 1280 桌面 Chromium 视觉可用，依赖 Radix 默认行为，不设显式 WCAG、窄屏、键盘或性能验证。
- 优点：首轮实现最少。
- 代价：会遗漏审核、Drawer、错误恢复和长表单的键盘 / Focus 问题，也不能发现轮询闪烁、无界列表和窄屏阻断，低于产品人工可用性要求。

#### Recommendation

选择 `P-41A`。它把可访问性、Viewport 与性能检查限制在首个 Goal 的真实用户路径，使用一个浏览器引擎、两个代表性布局和少量关键状态，而不把项目扩张为完整公开 Web 产品质量平台。

### Primary Sources

- [Radix Primitives Introduction](https://www.radix-ui.com/primitives/docs/overview/introduction)、[Accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility) 与 [Styling](https://www.radix-ui.com/primitives/docs/guides/styling)
- [shadcn/ui Introduction](https://ui.shadcn.com/docs) 与 [Tailwind v4 Integration](https://ui.shadcn.com/docs/tailwind-v4)
- [Material UI Overview](https://mui.com/material-ui/getting-started/)
- [XState v5 Documentation](https://stately.ai/docs)
- [WCAG 2.2 W3C Recommendation](https://www.w3.org/TR/WCAG22/)
- [Playwright Accessibility Testing](https://playwright.dev/docs/accessibility-testing)
- [Web Vitals](https://web.dev/articles/vitals)

### Decision and Authorization Status

- `P-39 / P-40 / P-41 = PROPOSED`；推荐项分别为 `P-39A / P-40A / P-41A`，用户尚未接受任何选项。
- 用户接受后还须创建 DEC、同步 Frontend Architecture Current Truth、Testing Strategy 与 Readiness，并完成 Frontend Architecture Final Consistency Review；Acceptance 之前不得安装 Radix / axe 或任何前端依赖。
- 本轮不冻结 RFC-004 / 005 / 007 字段、路径、枚举、错误代码、Pagination 或运维参数；不生成脚手架、代码、样式、Fixture 或测试，不执行 Browser / Spike / Live，不创建或激活 Goal。

## Decision Round — Frontend Workbench, Interaction and Web Quality Boundary（2026-08-06）

### User Acceptance

- 用户明确接受 `P-39A + P-40A + P-41A`。
- 选择一个深 `TaskWorkbench Module` + Native / 按需 Radix Primitives + CSS Modules；私有 `WorkbenchProjection` + Capability / Intent + revision-safe 串行 Autosave；WCAG 2.2 A / AA 基线 + Desktop Chrome + 代表性 Reflow / Accessibility + Evidence-driven Performance。

### Accepted Result

- [DEC-056](../decisions/dec-056-deep-task-workbench-revision-safe-interaction-and-proportional-web-quality.md) 归档 P-39A / P-40A / P-41A，并明确 Concretizes DEC-055 / 044 / 046 / 047、Applies DEC-039。
- [Frontend Architecture](../architecture/frontend-architecture.md) 同步全部已接受的 P-36～P-41；产品 / Module / 交互 / Web 质量决策已闭合，最终 HTTP Contract、精确依赖版本与实现证据仍待 RFC / Development Plan / Goal。
- 接受不改变 RFC-004 对最终 Resource、字段、状态、错误、revision、幂等、Conflict 和下载协议的权威，也不改变 RFC-005 对 Pagination / Retrieval Contract 的权威。

### Authorization Boundary and Next Gate

- 接受不授权安装 Radix、axe 或其他依赖，不授权脚手架、组件、样式、Client、测试、CI、业务实现、Spike、PR 合并或 Goal。
- 下一步是完成 Frontend Architecture Final Consistency Review，展示整体收口结果并取得用户对 Frontend Architecture 整体的明确接受；之后才可合并 Draft PR #51、关闭 Issue #50，并继续下一个策划议题。
- 全部策划、最终策划包与 Goal 文本展示并获用户明确“进入 Goal 执行阶段”批准前，仍不启动自动开发。

## Final Consistency Review — Frontend Architecture（2026-08-06）

### Independent Review Result

- 独立 `Sol / xhigh` Reviewer 审阅 DEC-055 / DEC-056、P-36～P-41、Frontend Current Truth、Testing、Readiness、Traceability 与实际 Diff。
- 第一轮发现 3 项 Required 状态口径：Integration Boundaries 未同步 DEC-055 / 056；PRD / MVP Scope 与 Frontend 主规格把“逐项接受”写得像“整体接受”。均已修正，未改变产品或架构内容。
- 快速复审结果：`Critical = 0 / Required = 0 / Optional = 0`，Final Consistency Review = `PASS`。
- 正确性、可读性、架构、安全与性能五轴均通过；公共 RFC-004 / 005 / 007 权威、Accepted / Proposed、历史快照与授权边界无冲突。

### Validation and Next Gate

- 本地 Markdown 链接损坏数为 0；`git diff --check` 与仓库既有格式、Lint、Type、Architecture、Fast Tests、Lock、Build、Dependency Audit 均通过。
- P-36～P-41 已满足进入 Frontend Architecture 整体接受 Gate 的条件。
- 用户整体接受前，不安装依赖、不实施前端、不合并 PR #51、不关闭 Issue #50、不执行 Spike、不创建或激活 Goal。

## Overall Acceptance — Frontend Architecture（2026-08-07）

### User Acceptance

- 用户在 P-36～P-41 全部逐项接受、DEC-055 / DEC-056 归档、Current Truth 同步和 Final Consistency Review = `PASS` 后明确回复：“接受 Frontend Architecture 整体”。
- Frontend Architecture 整体状态由 `OVERALL ACCEPTANCE PENDING` 更新为 `ACCEPTED`。

### Accepted Result and Boundary

- React / Vite SPA、显式状态所有权、OpenAPI 生成链、深 TaskWorkbench、Native / 按需 Radix + CSS Modules、私有 WorkbenchProjection、revision-safe Autosave / Diff、WCAG / Desktop Chrome / Reflow 与 Evidence-driven Performance 构成首个 Goal 的已接受 Frontend Architecture。
- RFC-004 继续拥有公共 Resource / 字段 / 状态 / 错误 / revision / 幂等 / Conflict / 下载协议；RFC-005 继续拥有 Pagination / Retrieval Contract；RFC-007 继续拥有 Observability 与运维边界。
- 整体接受不授权依赖安装、Frontend Implementation、Technical Spike、业务实现或 Goal 创建 / 激活。
- PR #51 只有在最新提交的 Required Checks 全部通过且最终五轴 Review 无阻塞 Finding 后才可合并；合并后关闭 Issue #50 并继续产品规格与 RFC-004 / 005 / 007 策划。

## Gate Confirmation — Product Specification and Remaining RFCs（2026-08-07）

### User Confirmation

- 用户明确确认下一 Gate 为：**产品规格闭合及 RFC-004、RFC-005、RFC-007**。
- 为保持单一结果、独立验收和依赖顺序，执行顺序解释为：产品规格闭合 → RFC-004 → RFC-005 → RFC-007；四项分别使用独立 Issue / Branch / PR 与用户 Decision / Acceptance Gate。
- [Issue #52](https://github.com/JettxonHo/ai-ecommerce-agent/issues/52) 仅承载产品规格闭合。RFC-004 / 005 / 007 将在前一依赖 Gate 完成后分别建立独立策划项。

### Authorization Boundary

- 本确认授权继续策划和文档归档，不接受下列任一产品提案，不接受 RFC-004 / 005 / 007，不授权 Technical Spike、依赖安装、业务实现或 Goal 创建 / 激活。
- 产品 Current Truth 只能在相应 Proposal 获得用户明确接受后更新；公共 HTTP / Retrieval / Observability 契约不得借产品文档提前冻结。

## Proposal Round — Product Specification Closure I（2026-08-07）

### P-42 — Product Specification Closure Boundary

#### Option A — Stable Product Semantics + Explicit Contract Handoff（推荐）

- 产品规格在用户可见目标、范围、输入门禁、工作台流程、审核、版本 / 失效、证据、结果、导出与验收语义完整后即可判定闭合。
- 公共 Resource / 字段名 / 类型 / 状态 / 错误 / revision / 幂等 / Conflict / 下载协议交给 RFC-004；Source / Locator / Pagination / Retrieval / Evidence Package 传输交给 RFC-005；日志 / Trace / Metrics / 运维参数交给 RFC-007；Fixture 文件内容与最终 E2E 证据格式交给 Testing Strategy。
- 产品文档保留稳定的业务语义组与行为不变量，不复制 OpenAPI 或数据库 Schema；RFC 不得反向改变已接受产品行为。
- 优点：产品与技术各有一个权威来源，公共契约可以独立演进和测试；避免把概念字段机械地一对一提升为 API。
- 代价：阅读者需要沿 Traceability 从产品语义跳转到 RFC 才能看到传输细节。

#### Option B — Freeze Every Product and Wire Field Together

- 在产品闭合 PR 中同时冻结全部字段、类型、状态、错误和文件模板，三份 RFC 只选实现技术。
- 优点：单份文档看起来最完整。
- 代价：重复 RFC-004 / 005 的职责，容易形成两套 Schema 权威；字段会在接口设计前过早锁死，返工和冲突风险高。

#### Option C — Keep Product Specification Partial Until All RFCs Finish

- 不单独判定产品规格闭合，等 RFC-004 / 005 / 007 全部接受后再统一更新产品状态。
- 优点：最终一次同步即可看到完整产品与技术合同。
- 代价：产品语义与技术实现长期混为同一个 Gate，无法判断 RFC 的上游输入是否已稳定，也会让技术限制反向替代产品决定。

#### Recommendation

选择 `P-42A`。它闭合产品层而不制造平行 Schema，符合 Contract-first 和稳定接口最小暴露原则，也保留 RFC 对技术契约的权威。

### P-43 — Fixed Acceptance Fixture Product Strategy

#### Option A — One Fictional Anchor SKU, Three Variants + One Mutation（推荐）

- 使用一个明确标注为虚构的非管制类商品“城市通勤双肩包”作为固定 Anchor SKU；三个资料包分别表达资料充分、资料不足但可运行、阻断性冲突与恢复，一个变更脚本在正常任务上修改重要商品事实并验证失效 / 局部重跑。
- 三个资料包共享基础商品身份和大部分可比内容，只改变与目标行为相关的资料完整性、冲突和版本。
- 优点：能把结果差异主要归因于系统行为而不是品类差异；无真实品牌授权、商标和内容漂移问题；功能、材质、容量、通勤场景与评论数据足以支撑四层分析和小红书 Brief 映射。
- 代价：只验证一个品类，不能证明跨品类泛化；Fixture 必须显式标为测试数据，不能伪装成真实用户研究。

#### Option B — Three Different Fictional Product Categories

- 资料充分、可运行不足和冲突恢复分别使用不同商品品类。
- 优点：表面覆盖更多业务表达和输入结构。
- 代价：品类差异与状态差异相互混杂，失败时难以定位是工作流问题还是领域内容差异；资料维护量更大。

#### Option C — One Real Brand / Real Listing Dataset

- 选用真实商品详情与评论作为三个资料包基础。
- 优点：演示观感更接近现实。
- 代价：来源许可、商标、隐私、内容变化和可复现性形成额外负担；真实资料也不能替代 Beta 用户研究。

#### Recommendation

选择 `P-43A`。首个演示应优先验证版本、审核、证据与恢复闭环；单一虚构 Anchor SKU 能在不扩大范围的情况下提供最清晰的可复现证据。

### P-44 — Needs Input Supplement Request Model

#### Option A — Targeted Action Request Derived from the Current Blocker（推荐）

- Needs Input 不采用一张不断扩张的固定问卷，也不退化为无结构聊天。系统针对当前真实阻断生成有限的行动请求，每项说明：缺少或冲突的业务信息、为什么影响当前阶段、当前可见来源 / 冲突值、用户可采取的结构化补充或裁决动作，以及完成后将恢复或重跑的范围。
- 非阻断增强资料继续以建议呈现，不冒充必填；同一阻断已有代表性请求后，不重复制造基本不可能出现的防御性变体。
- 请求内容只能基于已存在的 Task、Source、冲突和阶段上下文，不得补造外部事实；公共字段与错误码由 RFC-004 / 005 冻结。
- 优点：与行动导向恢复和两级门禁一致；用户知道为什么被阻断以及如何继续；能测试又不把 Rubric 或问卷机械化。
- 代价：后端需把阻断原因投影为结构化行动语义，具体映射要在 RFC-004 / 005 中保持一致。

#### Option B — Exhaustive Category Questionnaire

- 为每个商品展示固定、完整的长问卷，缺任何预设字段都要求回答。
- 优点：字段覆盖统一，表单实现直观。
- 代价：违背最低可运行输入与非阻断增强资料原则；会将低概率缺失机械化为强制防御。

#### Option C — Free-form Chat Follow-up

- 只显示自由文本追问，由用户与模型多轮对话补齐。
- 优点：表达灵活，前期字段设计少。
- 代价：聊天成为事实来源，冲突裁决、版本、恢复和自动化验收难以可靠追踪，违反已接受工作台边界。

#### Recommendation

选择 `P-44A`。它延续 DEC-044 / 045 / 047 的真实阻断、分级资料和行动导向恢复，同时不给首个 Goal 增加通用问卷或聊天状态机。

### Proposal Status and Next Decision Gate

- 用户于 2026-08-07 明确接受 `P-42A / P-43A / P-44A`；三项分别归档为 DEC-057 / DEC-058 / DEC-059，并同步 Product Current Truth、Testing Strategy 输入、Readiness 与 Traceability。
- 接受只关闭本轮三个决定，不自动接受 RFC-004 / 005 / 007，也不自动通过 Product Specification Final Consistency Review。
- 本轮不创建 Fixture 数据文件，不冻结 OpenAPI / Retrieval / Observability 字段，不执行测试、Spike 或 Goal，不编写任何业务代码。

## Acceptance Archive — Product Specification Closure I（2026-08-07）

### User Decision

- 用户明确接受 `P-42A`：产品规格以稳定用户可见语义和行为不变量闭合，公共 HTTP、Retrieval、Observability 与测试物理载体分别交给 RFC-004 / 005 / 007 和 Testing Strategy。
- 用户明确接受 `P-43A`：固定虚构非管制商品“城市通勤双肩包”为唯一 Anchor SKU，以三个资料变体和一个重要事实 mutation 验证核心行为。
- 用户明确接受 `P-44A`：Needs Input 只针对当前真实阻断形成有限结构化行动请求，不建设完整问卷或自由聊天状态机。

### Archive Result

- `P-42 / P-43 / P-44 = ACCEPTED`；DEC-057～059 为对应权威 Decision。
- Product Current Truth 只同步已接受的权威边界、Fixture 策略和 Needs Input 行为；公共字段、API、索引、状态、错误、下载与运维参数仍未冻结。
- 产品开放问题复核后，仅保留确有产品取舍的声明风险、数据生命周期体验和任务返回入口；其余公共契约与测试实例化问题按 DEC-057 路由到下游权威文档。

## Proposal Round — Product Specification Closure II（2026-08-07）

### P-45 — Claim Integrity and High-risk Expression Boundary

#### Option A — Evidence-bound Claim Integrity, Not a Compliance Engine（推荐）

- 首个 Goal 只做与当前商品资料和 Brief 诚实性直接相关的声明完整性控制：有直接证据的 verified fact 可以作为 Proof Point；只有商品页自述、但缺少检测或认证资料的内容保持 `documented_claim / claim_to_verify`，不得提升为已验证事实。
- 对无依据绝对化、功效、认证或贬低式比较声明，只阻断该声明进入 Current Brief；若移除或降级后仍能形成诚实 Brief，任务继续并在 Review 显示风险和建议动作。只有当前策略本身必须依赖该声明、且没有可信替代表达时，才进入 Needs Input。
- 系统不宣称法律意见、平台审核保证或实时法规合规；首个 Goal 不建设全品类法规库、自动法律分类器、主动联网规则抓取或独立 Compliance Agent。用户提供或已接受的约束、禁用表达和必要免责声明仍可进入结构化 Brief。
- 优点：保护事实与对外声明的核心可靠性，同时与非管制 Anchor SKU、单一人工审核和适度校验一致。
- 代价：不能替用户完成特定法域或平台的最终合规判断，需在结果中明确这一限制。

#### Option B — Broad Automated Compliance Gate

- 为所有品类维护法规 / 平台规则并在生成前自动判定允许与否。
- 优点：表面覆盖更广。
- 代价：需要实时规则来源、法域、敏感品类分类和专业验证，超出本地演示范围，并易形成过度防御与错误法律保证。

#### Option C — Human Review Only, No Deterministic Claim Boundary

- 所有声明都交给最终审核者判断，系统不区分 verified fact 与 documented claim。
- 优点：实现最少。
- 代价：会允许无依据声明进入 Brief 草稿并削弱既有 Fact / Evidence 契约。

#### Recommendation

选择 `P-45A`。它控制真正影响 Brief 诚实性的声明风险，但不把项目扩大为安全攻防或法律合规系统。

### P-46 — Controlled Demo Data Lifecycle Experience

#### Option A — Task-scoped Private Material + Reversible Removal, No Purge UI（推荐）

- 固定单工作区中的用户资料默认只属于当前 Task，不静默提升为跨任务共享知识；通用运营知识与商品任务证据保持逻辑分离。
- 用户可以把 Source 从当前有效资料集中移除或替换；该操作创建可追踪的版本变化、显示影响预览，并遵守 Current Truth / 局部重跑规则，不等于立即物理擦除历史。
- 首个 Goal 不建设登录、RBAC、多人权限或不可逆“永久删除”产品按钮。物理保留、Hold、删除安全、开发环境清理与操作员重置方式由 ARP-08、RFC-005 / 007 和开发文档冻结；在这些边界接受前不得把软移除伪装成彻底删除。
- 优点：用户能纠正当前资料集，同时避免在本地演示中仓促承诺不可逆删除和复杂权限。
- 代价：首个 Goal 不提供面向最终用户的一键永久清除体验，需要清楚说明本地数据处理边界。

#### Option B — Full User-facing Hard Delete in First Goal

- Task、Source、所有版本、索引、Checkpoint 和导出均提供立即永久删除。
- 优点：用户控制最直接。
- 代价：跨存储一致性、恢复、审计和误删风险显著扩大，必须先完成 Retention / Deletion Safety 规划和验证。

#### Option C — Workspace-wide Reuse by Default

- 上传资料默认进入共享知识库，并可被其他任务自动检索。
- 优点：后续任务可能复用资料。
- 代价：扩大权限、来源范围、过期和跨商品污染风险，违反受控首个 Goal 的最小边界。

#### Recommendation

选择 `P-46A`。它把“从当前分析移除”和“物理永久删除”明确分开，既支持真实纠错，又把不可逆数据操作留给 Readiness 与人工 Gate。

### P-47 — Cross-session Task Return Entry

#### Option A — Minimal Recent-task Index + Stable Deep Links（推荐）

- 在 `/tasks/new` 与稳定 Task Route 之外，为固定工作区提供一个最小任务入口：创建任务、查看最近任务，并按 Task 名称 / 品类、当前阶段或等待状态、最近更新时间和主要下一步动作返回工作台。
- 保留稳定深链；首个 Goal 不做全文搜索、高级筛选、批量操作、归档策略、分页优化或运营 Dashboard。任务索引只是跨会话恢复入口，不成为第二套业务状态。
- 优点：用户无需保存 URL 才能返回持久任务；与任务级跨会话恢复和行动导向状态一致。
- 代价：RFC-004 需要增加最小 List / Summary 契约，Frontend Architecture 的外层 Router 边界需由新 DEC 显式补充。

#### Option B — Stable Deep Links Only

- 只支持 `/tasks/new` 和已知 `task_id` 的工作台链接。
- 优点：页面和 API 最少。
- 代价：用户关闭页面后必须自行保存 URL，削弱跨会话恢复的产品可用性。

#### Option C — Full Operations Dashboard

- 同时提供搜索、筛选、排序、批量操作、统计和异常队列。
- 优点：更接近成熟运营平台。
- 代价：明显扩大 MVP，并引入当前没有验收依据的列表、批量和报表需求。

#### Recommendation

选择 `P-47A`。一个最小最近任务入口足以让持久化与 Resume 对目标用户真正可用，不需要建设完整运营 Dashboard。

### Proposal Status and Next Decision Gate

- 用户于 2026-08-07 明确接受 `P-45A / P-46A / P-47A`；三项分别归档为 DEC-060 / DEC-061 / DEC-062，并同步 Product、Frontend、Testing、Readiness 与 Traceability Current Truth。
- DEC-062 显式 Amend DEC-056 的 Router 边界；历史 Frontend Architecture 不被静默改写，深 TaskWorkbench 与 Router-thin 原则保持不变。
- 第二轮接受归档后执行 Product Specification Final Consistency Review；只有 Review 无阻塞、文档状态与开放问题清理一致且用户明确接受产品规格闭合，才结束 Issue #52 并进入 RFC-004 Gate。
- 本轮不创建页面、API、Fixture、数据库、索引或删除实现，不执行 Technical Spike 或 Goal。

## Acceptance Archive — Product Specification Closure II（2026-08-07）

### User Decision

- 用户明确接受 `P-45A`：首个 Goal 采用证据约束的声明完整性，只阻断无依据高风险声明进入 Current Brief；有诚实替代路径时 Task 继续，不建设通用法律或平台合规引擎。
- 用户明确接受 `P-46A`：用户资料默认只属于当前 Task，可逆移除 / 替换创建版本变化和影响预览；首个 Goal 不提供用户侧永久删除，物理保留与清理由后续权威文档冻结。
- 用户明确接受 `P-47A`：固定工作区提供最小最近任务入口和稳定深链；不建设搜索、批量、归档、统计或完整运营 Dashboard。

### Archive Result

- `P-45 / P-46 / P-47 = ACCEPTED`；DEC-060～062 为对应权威 Decision。
- DEC-060 显式修订 DEC-007 / 026 / 030 / 031；DEC-061 显式修订 DEC-014 / 025 / 041 / 044；DEC-062 显式修订 DEC-044 / 056。
- 产品层已无未接受 Proposal；公共字段、API、Retrieval、Observability、物理删除 / 清理和测试实例化仍按 DEC-057 交给 RFC-004 / 005 / 007、ARP-08、Development Plan 与 Testing Strategy。
- 下一动作是 Product Specification Final Consistency Review；通过并经用户接受前，Issue #52 / PR #53 保持开放，RFC-004 不启动。

## Product Specification Final Consistency Review（2026-08-07）

### Review Findings and Remediation

- 独立 GPT-5.6 Sol / `xhigh` Reviewer 首轮发现：PRD、User Flows 与 Vision 将已确认事项 / 下游交接保留在“待讨论的开放问题”标题下；User Flows 的旧 Needs Input 图只表达补料；部分 RFC 交接仍把已接受的 RFC-003 / 006 写成待定。
- 已修正三份产品文档的分型标题与旧占位表述，将 Needs Input 同步为补充 / 选择 / 纠正 / 确认 / 取消，并精确区分 RFC-002 / 003 / 004 / 005 / 006 / 007 与实施 Issue 的权威范围。
- 定点复审后 `Critical = 0`、`Important = 0`、`Suggestion = 0`，五轴 Review 全部 PASS，无阻塞 Finding。

### Review Result

- `Product Specification Final Consistency Review = PASS`；详见 [Review Record](../reviews/review-2026-08-07-product-specification-final-consistency.md)。
- `Ready for User Overall Acceptance = YES`，但 Review PASS 不是用户整体接受。
- 用户整体接受前，PR #53 / Issue #52 保持开放，RFC-004 不启动；业务实现、Technical Spike 与 Goal 继续未授权。

## Product Specification Overall Acceptance Gate（2026-08-07）

### User Decision

- 用户明确接受 Product Specification 整体闭合。
- 用户明确授权合并 PR #53、关闭 Issue #52，并进入 RFC-004 策划 Gate。

### Archive Result

- `Product Specification Overall Closure = ACCEPTED`；P-42～P-47、DEC-057～062 与 Final Consistency Review 共同构成该闭合证据。
- PR #53 可在最新 Required Checks 通过且合并前五轴 Review 无阻塞 Finding 后合并；Issue #52 随后关闭。
- 下一活动 Gate 为 RFC-004 API and Human Review Architecture 策划。RFC-004 本身仍为 `PROPOSED`，必须继续经过方案、用户 Decision、Final Consistency Review 与整体接受流程。
- 本接受不授权 RFC-005、RFC-007、Technical Spike、依赖安装、业务实现、数据迁移、Goal 创建 / 激活或发布。

## RFC-004 Gate Start and Proposal Round I（2026-08-07）

### Gate Transition

- PR #53 已在最新 8 项 Required Checks 全部通过、独立 Sol / `xhigh` 五轴 Review 无阻塞 Finding后合并；Merge Commit 为 `ff4a178`。
- Issue #52 已关闭；[Issue #54](https://github.com/JettxonHo/ai-ecommerce-agent/issues/54) 成为 RFC-004 的独立策划事实来源，分支为 `codex/rfc-004-api-human-review`。
- [RFC-004 Draft](../rfcs/rfc-004-api-and-human-review-architecture.md) 已创建，状态为 `DRAFTING`；创建 Draft 与进入 Gate 不等于接受 RFC 或任一 Proposal。

### Standards and Project Evidence

- OpenAPI 3.1 的语言无关 HTTP Contract、OAS feature version 与 API 自身版本分离能力来自官方 OpenAPI Specification；项目已由 DEC-055 接受 OpenAPI 3.1 → TypeScript Generated Client 边界。
- `202 Accepted`、strong ETag / `If-Match` 和 `Retry-After` 的标准语义来自 RFC 9110；`202` 只表示请求已接受处理，不表示处理完成。
- 公共错误共同形态参考 RFC 9457 `application/problem+json`；Human-readable detail 不作为机器控制数据。
- `Idempotency-Key` 在本次核验时仍只是 2026-04-18 已过期的 IETF Internet-Draft，不是最终 RFC。若项目采用该字段名，完整行为必须由 RFC-002 DQ-08 与 RFC-004 自行冻结，不依赖草案状态。

### P-48 — Contract Authority, Namespace and Interface Topology

- **P-48A（推荐）：** OpenAPI 3.1 Contract-first；`/api/v1` 单一当前主版本；查询使用显式 Resource，状态修改使用逐项 typed Command；拒绝让客户端 Patch 状态或调用 generic action dispatcher。
- **P-48B：** Pure REST Resource Mutation；路径较统一，但容易把非法状态转换和业务 Command 伪装为普通字段更新。
- **P-48C：** One Workbench Endpoint + Generic Action Dispatcher；路由少，但耦合 UI、削弱类型生成并形成不受控通用入口。

### P-49 — Revision Preconditions, Idempotency and Conflict

- **P-49A（推荐）：** 受保护写操作携带真正需要的 semantic precondition；可重试非幂等 Command 使用项目自定义完整语义的 `Idempotency-Key`；stale precondition 返回 typed `409`，不在首 Goal 强制维护第二套 ETag write authority。异步命令首次接受返回 `202`，已提交的同 Key / 同输入重放固定返回 `200` + 完全相同的不可变 Command Receipt 与 monitor identity；当前 Run 状态只从 `Location` 获取，响应 Schema 不随时间改变。
- **P-49B：** 所有受保护写使用 strong ETag / `If-Match`，非幂等操作另加 Idempotency Key；更 HTTP-native，但多资源业务 Command 和前端 revision-safe 编辑需要额外 Transport Validator 状态。
- **P-49C：** 单资源编辑使用 ETag / `If-Match`，多资源 Command 使用 Body precondition；能够精细采用 HTTP 条件请求，但形成 `409 / 412` 两套冲突与两个并发 Transport，对首个受控客户端不相称。
- 幂等重放必须在已知 Key 场景先于当前 revision 重检，否则“首次提交成功但响应丢失”的重试会被错误判定为 stale；Public Contract 不暴露 Hash / Digest，Idempotency Key 与 Command / Run / Attempt Identity 分离。

### P-50 — Durable Async Acceptance, Polling and Error Projection

- **P-50A（推荐）：** 只有真正异步的 Start / Resume / Rerun / Cancel 等操作在权威耐久接受记录提交后返回 `202` + Command Receipt + canonical Run monitor；Start / Resume / Rerun 提交 Durable Work Intent，Cancel 提交 `cancellation_requested`，不要求 Cancel 新建第二个 Work Intent。Draft Save 等同步写使用真实 `200 / 201`。活动期窄轮询 Run，阶段 / 终态变化后刷新窄 Task Overview 与受影响 Resource，由前端重新派生私有 WorkbenchProjection；Capability 是 revision-bound advisory allowlist，不是授权凭证。4xx / 5xx 采用 RFC 9457 Problem Details，Needs Input / Review Wait / Manual Recovery 和已接受后的 Run Failure 属于 Resource 状态而非 HTTP Error。
- **P-50B：** `202` + Task Snapshot only；资源少，但 Run / retry / rerun / cancel / receipt replay 语义被迫挤进 Task。
- **P-50C：** Push-first SSE / WebSocket；更新更即时，但扩大连接、部署、恢复和测试范围，不符合首个本地单工作区 Goal。

### Proposal Status and Authorization Boundary

- `P-48 / P-49 / P-50 = PROPOSED`；用户明确接受前不得创建 DEC 或同步为 Accepted Current Truth。
- 本轮只创建 RFC Draft、更新 Proposal / Current Gate 状态并提出方案；不创建 OpenAPI Artifact、API / Frontend / Worker / Database / Migration / Test Implementation，不安装依赖，不执行 Technical Spike，不创建或激活 Goal。
- 用户完成本轮 Decision Gate 后，下一轮才继续 DQ-04～06：Task / Workbench Query、Recovery Command 与 Human Review Protocol。

## RFC-004 Acceptance Archive I and Proposal Round II（2026-08-07）

### User Decision

- 用户明确接受 `P-48A`：OpenAPI 3.1 `/api/v1` 作为唯一公共 HTTP Contract；使用窄 Resource Query 与逐项 typed Command，不公开 Workbench mega-payload、通用 Action Dispatcher 或内部 Runtime 类型。
- 用户明确接受 `P-49A`：使用业务语义 precondition、单调 revision 与项目定义完整语义的 `Idempotency-Key`；同 Key / 同输入重放优先于 revision 重检，真正 stale 与 Key reuse 使用 typed `409`，公共契约不暴露 Hash / Digest。
- 用户明确接受 `P-50A`：真正异步操作在耐久接受后返回 `202` Receipt + canonical Run Monitor；同输入重放固定 `200` 同一 Receipt；Frontend 活动期轮询窄 Run，Capability 为 revision-bound advisory allowlist，4xx / 5xx 使用 RFC 9457 Problem Details。

### Archive Result

- `P-48 / P-49 / P-50 = ACCEPTED`；DEC-063 是三项权威 Decision，RFC-004 DQ-01～03 已闭合。
- RFC-004 仍为 `DRAFTING`；DQ-04～10、Final Consistency Review 与用户整体接受仍未完成。
- 接受只授权策划文档同步，不创建 OpenAPI、API、Client、Database / Migration、测试实现、Technical Spike 或 Goal。

### P-51 — Task Creation, Recent Index and Workbench Read Model

- **P-51A（推荐）：** 同步创建 Task（首次 `201`、重放 `200` 同一 identity），提供 server-bounded 最近任务列表和窄 Task Overview；列表只含名称、品类、阶段 / 等待语义、更新时间、Task revision 与绑定该 revision 的主要 Capability，详情正文仍由独立 Resource 读取。
- **P-51B：** Task Overview 嵌入多个最新 Resource Summary；首屏请求少，但产生重复和半 mega-payload。
- **P-51C：** 无 Task Overview，Frontend 扇出所有 Resource 并自行推断导航状态；Resource 最窄，但容易形成第二套状态机。

### P-52 — Needs Input and Recovery Commands

- **P-52A（推荐）：** revision-bound Needs Input Action Request + typed Resolution；Source remove / replace 使用无副作用 Preview + 完整 typed version / revision Basis 的 Confirm；Cancel、Resume、confirmed Rerun 与 Manual Recovery 保持显式 typed Command，由服务端 Capability 决定是否合法。Resume 保留兼容 execution context 但创建新 Run / Attempt，不复用旧 Run identity。
- **P-52B：** 单一 Generic Recovery Command；路由少但违反 DEC-063 typed Command 边界。
- **P-52C：** Frontend 自行编排 Source mutation / Resume / Rerun；会把恢复状态机移到浏览器。

### P-53 — Human Review Protocol

- **P-53A（推荐）：** 不可变 Review Package + 每 Package 一个 active Review Draft；Autosave 发送 revision-guarded full structured snapshot，Submit / Request More Information / Regeneration / Withdraw 使用独立 typed Outcome Command。Submit 原子创建不可变 Review Decision / Approved Strategy 与唯一 Durable Resume Work Intent，并返回 `201` 主结果 + continuation Receipt；客户端不再另发 Resume。Reject-all-and-request-regeneration 使用 `202` 新 Run Receipt，Request More Information 与 Withdraw 不自动调度。
- **P-53B：** JSON Patch Draft；传输小，但数组 / merge / conflict 和类型生成复杂度不相称。
- **P-53C：** Public Review Operation Log；审计细，但扩大为 Event Editing Protocol 和协作模型。

### Proposal Status and Next Gate

- `P-51 / P-52 / P-53 = PROPOSED`；未获用户确认，不能同步为 Accepted Current Truth。
- 接受后只归档 DQ-04～06，并继续 DQ-07～09；不合并 PR #55、不关闭 Issue #54、不接受 RFC 整体、不实现 API 或启动 Goal。

## RFC-004 Acceptance Archive II and Proposal Round III（2026-08-07）

### User Decision

- 用户明确接受 `P-51A`：同步创建 Task，提供 server-bounded 最近任务列表和窄、revision-bound Task Summary / Overview；Frontend 不从多个 Resource 猜测主要业务状态。
- 用户明确接受 `P-52A`：使用 revision-bound Needs Input Action Request、typed Resolution、Source Preview / Confirm basis，以及显式 Cancel / Resume / confirmed Rerun / Manual Recovery；每次 Resume / Rerun 创建新 Run identity。
- 用户明确接受 `P-53A`：使用不可变 Review Package、revision-guarded full-snapshot Draft 与显式 Outcome Commands；Review Submit 原子提交 Approved Strategy 与唯一 Durable Resume Work Intent，客户端不再另发 Resume。

### Archive Result

- `P-51 / P-52 / P-53 = ACCEPTED`；[DEC-064](../decisions/dec-064-task-recovery-and-human-review-public-protocol.md) 是三项权威 Decision，RFC-004 DQ-04～06 已闭合。
- RFC-004 仍为 `DRAFTING`；DQ-07～10、Final Consistency Review 与用户整体接受仍未完成。
- 接受只授权策划文档同步，不创建 OpenAPI、API、Client、Database / Migration、测试实现、Technical Spike 或 Goal。

### P-54 — Brief Version, Comparison and Markdown Export

- **P-54A（推荐）：** Marketing Brief / Xiaohongshu Brief 使用独立不可变 Version Resource 与 Task Current Truth references；同 family 版本可请求无副作用的 semantic-group Comparison；用户编辑使用 typed revise Command；导出使用 Preview → Confirm 创建可重放的单 Brief UTF-8 Markdown Export Snapshot，固定模板和服务端文件名，不新增 PDF / JSON、异步文档任务或内容 Hash。
- **P-54B：** Mutable Current Brief + 下载时即时导出；接口少，但无法可靠解释历史版本或重放相同文件。
- **P-54C：** 异步多格式 Export Job；扩展性强，但扩大为 PDF / JSON、Job、对象存储与保留平台。

### P-55 — Problem Types and Recovery Actions

- **P-55A（推荐）：** RFC 9457 + 小型稳定 Problem Catalog；只为客户端真实可执行的 `correct / refresh / compare / retry later / open current / contact operator` 行为提供 typed context，区分有限 `400 / 404 / 409 / 413 / 415 / 422 / 429 / 500 / 503`，不暴露内部异常矩阵。
- **P-55B：** Status + free-text only；简单，但 Frontend 只能解析文案或猜动作。
- **P-55C：** 穷举内部 Domain / Workflow / Provider Error；诊断细但泄漏实现、扩大兼容承诺并违反适度校验。

### P-56 — Fixed-workspace Identity and Transport

- **P-56A（推荐）：** Workspace identity 由服务端固定配置注入，Browser 不选择 Workspace；API 默认 loopback + same-origin `/api/v1`、CORS closed，并对 Browser state-changing Origin 做适度匹配。首个 Goal 不建设 Login、Cookie / Token、RBAC、多租户或多人审核，也不把该边界描述为公网认证。
- **P-56B：** Client-supplied Workspace Header；看似便于扩展，但未认证 Header 会制造伪多租户和错误安全感。
- **P-56C：** Local Login / Shared API Token；更像远程服务，但没有真实账号 / 租户需求却增加 Credential 与权限矩阵。

### Proposal Status and Next Gate

- `P-54 / P-55 / P-56 = PROPOSED`；未获用户确认，不能同步为 Accepted Current Truth。
- 接受后只归档 DQ-07～09，并进入 DQ-10 OpenAPI Closure / Adoption / Contract Test 最终提案；不合并 PR #55、不关闭 Issue #54、不接受 RFC 整体、不实现 API 或启动 Goal。

## RFC-004 Acceptance Archive III and Final Proposal Round（2026-08-07）

### User Decision

- 用户明确接受 `P-54A`：Marketing Brief / Xiaohongshu Brief 使用独立不可变 Version Resource、Task Current Truth references、semantic-group Comparison 与 typed revise；导出通过 Preview → Confirm 创建可重放的单 Brief UTF-8 Markdown Export Snapshot，不增加 PDF / JSON、异步文档任务或内容 Hash。
- 用户明确接受 `P-55A`：所有 4xx / 5xx 使用 RFC 9457 Problem Details，采用有限稳定 Problem Type / typed action catalog；正常 Needs Input、waiting Review、manual recovery 与 failed Run 保持 Resource state，不暴露内部异常矩阵。
- 用户明确接受 `P-56A`：Workspace 由服务端固定配置，Browser 不选择 Workspace；首个 Goal 采用 loopback + same-origin `/api/v1`、CORS closed 与 state-changing Origin 匹配，不建设 Login、Token、RBAC、多租户或公网认证。

### Archive Result

- `P-54 / P-55 / P-56 = ACCEPTED`；[DEC-065](../decisions/dec-065-immutable-brief-export-problem-and-fixed-workspace-api-boundary.md) 是三项权威 Decision，RFC-004 DQ-07～09 已闭合。
- RFC-004 仍为 `DRAFTING`；DQ-10、Final Consistency Review 与用户整体接受仍未完成。
- 接受只授权策划文档同步，不创建 OpenAPI、API、Client、Export / Database / Migration、测试实现、Technical Spike 或 Goal。

### P-57 — OpenAPI Closure, Compatibility, Generated Client and Contract Tests

- **P-57A（推荐）：** Goal 激活后先创建唯一 `contracts/openapi/openapi.yaml` entry contract；冻结 Task、Run / Recovery、Needs Input、Source-change、Review、Brief 与 Export 的 first-Goal Operation catalog，Task recent 默认 / 最大窗口 `20 / 50`、Brief history `10 / 25`，以及 Task / Stage / Run、Resource / Command / Problem Schema family；只允许 `/api/v1` additive evolution，公共 enum 新值须同 PR 更新 unknown fallback；使用 `openapi-typescript` + `openapi-fetch` 派生不可手改客户端并执行 clean-diff，Contract Tests 验证 OAS、examples、status / media、幂等 / conflict、Review / Export 与 fixed-workspace 代表性行为。RFC-005 / 007 只补齐各自拥有的 refs / extensions，不创建第二 Contract authority。
- **P-57B：** 先实现 Handler，再从 Backend implementation 生成 OpenAPI 并复制给 Frontend；启动快，但把实现变为事实源、Contract Review 后置且易产生快照漂移。
- **P-57C：** 开发前穷举 Source / Evidence / Observability / Auth / Tenant / Retention / Search / Push / 全部内部错误；表面完整，但越过 RFC-005 / 007 与 MVP 范围并制造无需求依据的长期兼容承诺。

### Proposal Status and Next Gate

- `P-57 = PROPOSED`；未获用户确认，不能同步为 Accepted Current Truth 或 DEC。
- 当前 DQ-01～09 已接受；接受 P-57A 后只归档 DQ-10 并执行 RFC-004 Final Consistency Review。
- Final Review 完成后仍须单独取得用户对 RFC-004 整体的明确接受，才可合并 PR #55、关闭 Issue #54 并进入 RFC-005 Gate；本轮不实现 API 或启动 Goal。
