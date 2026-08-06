# Session-003：正式开发前策划与长期 Goal 治理

## Metadata

- Status: In Discussion
- Date: 2026-08-06
- Topic: 正式开发前策划、文档一致性、端到端演示 MVP 与长期 Agent 执行治理
- Related RFCs: RFC-001、RFC-002、RFC-003 至 RFC-007
- Related Decisions: DEC-039、DEC-040、DEC-041

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

## Rejected Approaches

- 将过期入口声明继续视为 Current Truth。
- 在产品字段、公共契约或 RFC 未接受前直接开始业务代码。
- 用哈希清单、极低概率变体或机械评分替代核心行为验证。
- 在指定实现模型不可用时静默切换模型。

## Open Questions

- 产品定位句、最终 JTBD / Persona、任务工作台流程与演示成功标准的完整字段。
- 四层 Brief、Review Package、Approved Strategy 与 Xiaohongshu Brief 的最终 Schema 和版本规则。
- RFC-003 至 RFC-007 与 Frontend Architecture 的具体技术选择。
- ARP-02 / 03 / 09 完整 Artifact、ARP-05 至 ARP-08 和 TS-01 至 TS-05 Charter。
- Luna/max 的可用时间或后续是否由用户显式修改实现模型决定。

## Deferred Topics

公开部署、Beta 用户研究执行、生产账号权限、计费、多租户、联网抓取、OCR、多媒体生成、自动发布与 Multi-Agent 扩展。

## Documentation Updates

- 新增 DEC-039、DEC-040、DEC-041 并更新 Decision Log。
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
- Current Truth Sync：Issue #32 / PR #33 已创建，范围限定为入口状态、产品 Current Truth、Readiness / RFC / Foundation / Traceability 同步和 30 个失效本地 Markdown 链接修复；不包含新产品字段、RFC-003～007 技术选择、业务代码、Spike 执行或 Goal 激活。
- Link Audit：排除 `.claude/worktrees`、`.venv` 和生成目录后，Tracked Workspace Markdown 本地链接由 30 个损坏修复为 0。
- Current Truth Review：经 Sol/xhigh 独立复审三轮修正，产品、架构、Readiness、Traceability 与治理口径最终结果 = `PASS`；未把未接受事项写成实现事实。
