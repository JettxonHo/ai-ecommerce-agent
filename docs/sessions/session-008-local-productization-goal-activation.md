# Session-008：本地产品化 Goal 激活与 Current-Truth Reconciliation

## Metadata

- Status: Concluded
- Date: 2026-08-23
- Topic: successor Action Workbench productization Goal、终止 Fast Lane 执行入口与 P0→P5 串行 Stage
- Related Decision: [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md)
- Related Goals: [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)、[MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md)
- Related Issues / PRs: [#301](https://github.com/JettxonHo/ai-ecommerce-agent/issues/301)、[#300](https://github.com/JettxonHo/ai-ecommerce-agent/issues/300)、[#299](https://github.com/JettxonHo/ai-ecommerce-agent/pull/299)、[#247](https://github.com/JettxonHo/ai-ecommerce-agent/issues/247)

## Context

FL-1 deterministic browser-to-backend-to-export loop 与 one-command local demo 已形成可复用 foundation，但两次授权的 DeepSeek smoke 都安全失败。旧 Fast Lane Goal 不能被写成成功；它的 terminal 状态是 `GOAL_BLOCKED`，并且 [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) Phase A 只得到 `INSUFFICIENT_SANITIZED_EVIDENCE` 与跨 mapper / schema / domain-admission boundary 的 observational ambiguity。没有 production repair、Phase B contract 或 Provider acceptance，且两次 live authorization 均已消耗。

[DEC-082](../decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) 已确定固定本地单用户 Action Workbench 方向。用户在 [Issue #300 comment 5386010673](https://github.com/JettxonHo/ai-ecommerce-agent/issues/300#issuecomment-5386010673) 明确选择 A+C hybrid，状态为 `HUMAN_SELECTED_AC_BASELINE`。该选择不等于 [PR #299](https://github.com/JettxonHo/ai-ecommerce-agent/pull/299) 合并，不接纳 ignored prototype，也不授权 Provider、平台或 Spider_XHS 行为。

用户在 [Issue #301](https://github.com/JettxonHo/ai-ecommerce-agent/issues/301) 明确确认：建立一个 successor long-running Goal，按一个 Stage / 一个独立结果串行执行，并赋予普通合同内本地仓库、测试、branch 与 PR 操作的 full access；这些权限不覆盖 Issue scope、独立 Review、Secret / Provider / platform gate、破坏性操作、public contract / migration gate 或 exact implementation-agent rule。

## Goal

把上述用户决定归档为 [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md)，并使 [MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md) 成为唯一 active productization entry。P0 只做八文件 docs-only reconciliation；P0 合并后，且仅此时，P1 是唯一 next implementation Stage。

## Non-goals

- 不修改业务代码、测试、配置、依赖、lockfile、migration、OpenAPI 或 Web 实现；
- 不调用 Kimi、Terra、DeepSeek 或任何 Provider / model，不读取 Secret，不访问平台；
- 不重写、删除或淡化两次 DeepSeek failure、DEC-081 ambiguity、`GOAL_BLOCKED`、无 Provider acceptance、无 production repair / Phase B contract；
- 不把 A+C human selection 写成 production merge，不关闭或替代 PR #299；
- 不创建全部后续 implementation Issues，不把 Dependabot 或无关旧 Issues 纳入 Stage；
- 不复制、clone、安装、登录、Cookie、proxy、fingerprint / signature、请求、scrape 或发布 Spider_XHS；
- 不进行 TDD：P0 没有代码行为变更，适用验证是文档与边界校验。

## Discussion

### Fact

- 旧 Fast Lane Goal 的两次受控 DeepSeek 运行均非 live acceptance；第一次完成五 calls 后失败，第二次在 `product_intake_v1 / v1` 一次 call 后以固定安全 HTTP 500 终止。
- DEC-081 Phase A 的 terminal disposition 是 `INSUFFICIENT_SANITIZED_EVIDENCE`；证据只支持 observational ambiguity，不支持历史根因、production repair 或 Phase B contract。
- DEC-082 已接受固定本地单用户 Action Workbench；用户在 Issue #300 明确选择 A+C baseline，PR #299 仍 open / unmerged。
- Issue #301 的 P0 allowlist 只有八个 Markdown / rules 文件，并要求 exact serial order P0 → P1 → P2 → P3 → P4 → P5。
- Spider_XHS 是条件性 P5 feasibility candidate；当前没有复用、许可、平台或 publishing authorization。

### Observation

- 继续把旧 Fast Lane 当作 active entry 会让 foundation、Provider failure 与产品化工作混在同一状态，增加错误恢复或重复 Issue 的风险。
- A+C 的 human selection 已足以作为 P1 shell 的设计基线，但没有替代 exact frontend contract、taste-skill evidence、代码实现或独立 Review。
- Stage-by-stage gating 把本地产品价值与 Spider_XHS / Provider 的高风险边界解耦；P5 失败或冻结不应阻塞 P1～P4。

### Risk

- 把 `HUMAN_SELECTED_AC_BASELINE`、PR #299 或 deterministic foundation 写成 production acceptance，会制造虚假 current truth。
- 为了推进而预先创建全部 implementation Issues，或将 open Dependabot / unrelated work 带入 Goal，会扩大范围。
- 把 full local access 解释为 Provider、Secret、平台、migration 或模型调用授权，会越过人工 Gate 和 DEC-071 / 072 路由。
- Spider_XHS README 的 MIT badge 与非商业措辞冲突且上游未检测到 LICENSE；未经 positive feasibility Gate 推断 reuse permission 会造成许可和平台风险。

### Alternatives

1. 保持 Fast Lane 作为 active Goal，继续等待或修复 DeepSeek：拒绝，既无法解释 terminal `GOAL_BLOCKED`，也会重新打开已消耗的 Provider Gate。
2. 把 A+C verdict 或 PR #299 直接写成生产实现：拒绝，human selection 与 merged / deployed / runtime evidence 是不同事实。
3. 一次性创建 P1～P5 全部 Issues：拒绝，违反串行 Stage 与真实消费者边界。
4. 接受 DEC-083 的 successor Goal、P0 reconciliation 与严格 P0→P5 gate：用户明确选择并接受。

### Accepted Decision

- [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md) 为 Accepted；successor Goal 在 P0 文档 PR 合并后成为唯一 active productization entry。
- 旧 Fast Lane Goal 保持 terminal `GOAL_BLOCKED` historical record，完整保留两次 DeepSeek failure、DEC-081 ambiguity、no-Provider-acceptance、no-production-repair / no-Phase-B truth。
- Stage 顺序冻结为 P0 → P1 → P2 → P3 → P4 → P5；P1 是 P0 merge 后唯一 next implementation Stage，每个后续 Stage 必须等前一 PR 独立 Review 并合并。
- A+C 只标记为 `HUMAN_SELECTED_AC_BASELINE`；PR #299 保持 open / unmerged，不是 production implementation。
- Spider_XHS 只进入条件性 P5 docs/research feasibility Gate；无 reuse、code copy、clone/install、Cookie/login、proxy/signature、platform request、scrape 或 publishing authorization。
- P0 exact-eight allowlist、docs-only、no Kimi/Terra/provider/model call 与 TDD N/A 保持不变。

### Open Question

- P1 的精确 frontend implementation contract、taste-skill choice、文件所有权与 visual evidence 由后续独立 Issue 冻结；P0 不预选实现细节。
- P3 如何与 Issue #247 的既有边界协调，须在 P3 contract 中以当前 code / Issue evidence 确认；P0 不创建 duplicate。
- P5 的 upstream commit、许可证解释、平台条款与 read-only research seam 只能在 Gate 内验证；P0 不作许可或可行性结论。

## Documentation Updates

- 新增 [DEC-083](../decisions/dec-083-local-action-workbench-productization-goal.md)、[MVP-0P Local Action Workbench Productization Goal](../goals/mvp0-local-action-workbench-productization-goal.md) 与本 Session；
- 更新 `AGENTS.md`、`README.md`、[Decision Log](../decisions/decision-log.md)、[MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md) 与 [Implementation Readiness](../handoffs/implementation-readiness.md)；
- 在 Decision / Goal / Session 之间保留双向链接，并把 DEC-083 记录为 Accepted；
- 保留 DEC-078 / 081 的 historical failure / diagnosis wording，未授权新的 Provider、model、平台或产品方向行为。

## Synchronization Checklist

- [x] Fact、Observation、Risk、Alternative、Accepted Decision 与 Open Question 分开记录
- [x] DEC-083 明确 Amends / Preserves / Related Goal / Related Session 关系
- [x] 旧 Fast Lane Goal terminal `GOAL_BLOCKED`，两次 DeepSeek failure、DEC-081 ambiguity 与 no-Provider-acceptance 保留
- [x] A+C 仅为 `HUMAN_SELECTED_AC_BASELINE`；PR #299 open / unmerged
- [x] P0→P1→P2→P3→P4→P5 顺序、P1-only-next 与 one-Stage-at-a-time 规则已记录
- [x] Spider_XHS 条件性 P5 Gate 与 no-reuse / no-platform / no-publishing 边界已记录
- [x] P0 exact-eight allowlist、docs-only、no model/provider calls、TDD N/A 已记录
- [x] open Dependabot / unrelated Issues 排除，full local access 不覆盖人工 Gate
