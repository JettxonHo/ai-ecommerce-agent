# DEC-083：激活本地 Action Workbench 产品化分阶段 Goal

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-23
- **Decision Type:** Product Delivery / Goal Governance / Stage Sequencing / Local Boundary
- **Source:** [Session-008](../sessions/session-008-local-productization-goal-activation.md)；用户在 [Issue #301](https://github.com/JettxonHo/ai-ecommerce-agent/issues/301) 明确确认
- **Related human review:** [Issue #300 comment 5386010673](https://github.com/JettxonHo/ai-ecommerce-agent/issues/300#issuecomment-5386010673)

## Context

当前 [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md) 已有两个相互独立的 DeepSeek 受控失败记录。其 FL-2 结论是 terminal `GOAL_BLOCKED`；[DEC-081](dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) 的离线 Phase A 只证明多个真实 mapper / schema / domain-admission rejection boundary 可以产生相同保留安全签名，结论为 `INSUFFICIENT_SANITIZED_EVIDENCE`，没有 production repair、Phase B contract 或 Provider acceptance。

[DEC-082](dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) 已冻结固定本地单用户 Action Workbench 的产品方向。用户随后审阅了 A+C hybrid，并在 [Issue #300](https://github.com/JettxonHo/ai-ecommerce-agent/issues/300) 的明确评论中选择 `HUMAN_SELECTED_AC_BASELINE`。该选择是设计基线，不等于 [PR #299](https://github.com/JettxonHo/ai-ecommerce-agent/pull/299) 已合并，也不授权 Provider、平台或候选开源项目行为。

用户在 [Issue #301](https://github.com/JettxonHo/ai-ecommerce-agent/issues/301) 明确授权：建立一个 successor long-running Goal，按一个 Stage / 一个独立可审阅结果串行推进；P0 先完成 current-truth reconciliation，只有 P0 PR 合并后才开始 P1。普通、可逆且合同内的本地仓库 / 测试 / 分支 / PR 工作可使用既有长期授权，但不覆盖人工 Gate、实现 Agent 路由或 Issue 范围。

## Decision

### 1. Successor Goal and terminal historical record

- 接受并激活唯一的 successor Goal：[MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md)。本 Decision 所在文档 PR 合并后，该 Goal 成为唯一 active productization execution entry point。
- 旧 [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md) 改为 terminal `GOAL_BLOCKED` historical execution record，不得写成成功或重新作为剩余产品化 backlog 的入口。
- 旧 Goal 必须保留两次 DeepSeek 失败的事实、DEC-081 的 `INSUFFICIENT_SANITIZED_EVIDENCE` 与 observational ambiguity、无 Provider acceptance、无 production repair / Phase B contract 以及已消耗的 live authorization。

### 2. Exact serial Stage order

Stage 顺序冻结为 **P0 → P1 → P2 → P3 → P4 → P5**。同一时刻最多一个 implementation Stage active；前一 Stage 的 PR 未经独立 Review 并合并，不得创建或启动下一 implementation Stage。

1. **P0 — Goal activation and current-truth reconciliation**：本 Issue，docs-only；同步八个 allowlisted 文档、Decision / Goal / Session 链接与 terminal Fast Lane 状态。
2. **P1 — Action Home and A+C production shell**：实现中文优先 Action Home、Task identity/header、宽桌面横向五阶段轨道、一个 Active Workspace 与 responsive Context Rail；保留现有 generated client / gateway / data behavior，不改后端或 public contract。
3. **P2 — Core TaskWorkbench states**：针对当前 backend 行为产品化 Running、Review、Results；结构化业务分组、Marketing / Xiaohongshu 分视图、安全 Markdown preview/export、raw JSON 技术披露，以及 1280/1024/320 reflow。
4. **P3 — Needs Input and essential recovery**：复用或协调 [Issue #247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247)，不得创建重复 Issue；只实现本地产品所需的有界 structured Needs Input 与最小可恢复错误路径。
5. **P4 — Deterministic local release acceptance**：使用 fictional data 验证真实 browser → FastAPI → PostgreSQL deterministic path、one-command demo、现有 export 与代表性 recovery；不进行 live model / Provider / platform call，并完成独立五轴 Review 与 Goal Review。
6. **P5 — Spider_XHS feasibility Gate**：先做 docs / research only，审计 exact upstream commit、license、commercial-use permission、平台条款 / 风险、Cookie / Secret、dependency / security 与窄 read-only research seam。未经正面接受，冻结或拒绝候选；publishing 不属于本 Goal。

P1 是 P0 合并后的唯一 next implementation Stage。不得预先创建全部 implementation Issues，也不得把 open Dependabot 工作或其他无关旧 Issue 纳入上述顺序。

### 3. A+C human baseline is not production

`HUMAN_SELECTED_AC_BASELINE` 只表示用户选择了设计基线：中文任务身份与稳定业务 / 状态阅读顺序、宽桌面横向五阶段轨道、Context Rail、一个 dominant current action、渐进披露、1024px in-flow disclosure、真实 320 CSS-px reflow、四个业务状态与 raw JSON 非主界面。

该选择不等于 PR #299 合并、不等于生产 Web 实现、不等于 ignored prototype 被接纳，也不授权 Kimi、Terra、Provider、平台或 Spider_XHS 行为。后续实现仍须精确 Stage contract、适用 taste skills（重要前端工作）和 Sol / ORCHESTRATOR_REVIEWER 独立 Review。

### 4. Spider_XHS is conditional feasibility only

Spider_XHS 只作为 P5 的条件性可行性候选。当前审计记录 upstream tree 未检测到 LICENSE，同时 README 存在 MIT badge 与非商业措辞冲突；不得从这些材料推断复用或商业许可。

在 P5 feasibility Gate 通过且另有明确授权前，禁止：代码复制或复用、clone、vendor / dependency install、Cookie / login、proxy、fingerprint / signature execution、任何 Xiaohongshu platform request、scraping、publishing 或生产接入。即使 P5 被拒绝，本地产品 Goal 仍可独立完成。

### 5. Access and implementation boundaries

- 本 Decision 不改变固定本地单用户、现有 backend Current Truth、same-origin、Secret、public-contract、migration、dependency、Provider 与安全边界。
- 普通 full local access 只覆盖合同内、可逆的仓库 / 测试 / branch / PR / local lifecycle 操作；不覆盖破坏性操作、真实凭证、额外 Provider / model call、平台行为、公共契约 / migration、产品范围变化、独立 Review 或 exact implementation-agent rule。
- P0 不进行 Kimi、Terra、Provider、model、Secret、network / platform 或 live action，也不进行 TDD；代码、测试、配置、依赖、lockfile、migration、OpenAPI 与 Web 实现均为 non-goal。
- P1 及后续 Stage 仍按 [DEC-071](dec-071-luna-worker-exclusive-implementation-routing.md) / [DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md) 路由；未在本 Stage contract 明确授权的模型、Provider 或前端例外不得调用。

## Consequences

- 仓库拥有一个可追踪的 active productization Goal，同时保留 Fast Lane 的失败历史与诊断边界。
- 交付优先级从旧横向 backlog 收敛为一个可观察的本地行动工作台；每个 Stage 都有独立消费者、验收和 stop conditions。
- A+C 设计选择可以指导 P1，但不会把未合并 PR 或人工设计判断冒充生产事实。
- Spider_XHS 的研究价值与平台 / 许可风险被隔离在 P5 Gate，不会阻塞 P1～P4，也不会自动授权任何外部动作。

## Relationships

- **Amends:** [DEC-078](dec-078-mvp0-fast-lane-execution-rebaseline.md) 的剩余 MVP-0 执行入口与 Goal 状态；旧 Goal 作为 terminal history 保留。
- **Preserves:** [DEC-039](dec-039-proportional-validation-and-review-governance.md)、[DEC-081](dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) 的适度校验、两次 DeepSeek failure、`INSUFFICIENT_SANITIZED_EVIDENCE`、无 Provider acceptance 与 no-Phase-B 边界；[DEC-082](dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) 的产品方向与窄前端例外。
- **Related Goals:** [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)（terminal historical record）；[MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md)（successor active entry）。
- **Related Session:** [Session-008](../sessions/session-008-local-productization-goal-activation.md)。
- **Related Issues:** [#301](https://github.com/JettxonHo/ai-ecommerce-agent/issues/301)、[#300](https://github.com/JettxonHo/ai-ecommerce-agent/issues/300)、[#299](https://github.com/JettxonHo/ai-ecommerce-agent/pull/299)、[#247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247)。

## Authorization Boundary

本 Decision 只把本地产品化执行入口和 Stage 顺序写入 Current Truth。P0 的八文件 allowlist 与 docs-only 限制以 Issue #301 为准；本 PR 不授权任何 Provider / model / Kimi / Terra call、Secret 访问、代码或 Web 实现、依赖安装、migration、OpenAPI、平台行为、Spider_XHS reuse 或 publishing。后续 Stage 必须在各自 Issue / task contract、独立 Review 与适用人工 Gate 内推进。
