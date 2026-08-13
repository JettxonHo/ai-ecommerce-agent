# Session-006：MVP-0 FL-2 Terminal Diagnosis Decision

## Metadata

- Status: Concluded
- Date: 2026-08-14
- Topic: 两次 DeepSeek terminal failure 后的 Goal 状态与离线恢复路径
- Related Decisions: [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md), [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md), [DEC-080](../decisions/dec-080-fl2-xiaohongshu-profile-v2-and-deadline-fence.md), [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md)
- Related Issues: [#281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281), [#283](https://github.com/JettxonHo/ai-ecommerce-agent/issues/283), [#285](https://github.com/JettxonHo/ai-ecommerce-agent/issues/285)

## Context

FL-1 deterministic vertical 与 local demo 已完成。两次经过授权的 DeepSeek smoke 都以安全失败结束，当前 Goal 为 `GOAL_BLOCKED`。用户在重新审视原始开发哲学后明确选择 Option B：保留该状态，把 FL-1 作为 foundation，并建立一个先诊断、后决定是否修复的有界离线路径。

## Goal

把用户确认的 Option B 归档为可执行但不越过 Provider / Secret / product Gate 的 Accepted Decision，并区分已知事实、诊断观察、风险、决定与仍待 Phase A 回答的问题。

## Non-goals

- 不诊断历史 Provider failure 的根因；
- 不实现 Phase A harness 或 Phase B repair；
- 不修改 Profile、Prompt、Schema、Domain、Provider、公共契约、migration 或依赖；
- 不读取 Secret / raw Provider material，不执行 Provider、PostgreSQL 或 live action；
- 不授权第三次真实调用或自动 retry / recovery。

## Discussion

### Fact

- FL-1 deterministic Task → input → pipeline → review → two Briefs → Markdown export 已实现并具有 provider-free browser / backend evidence。
- 首次 DeepSeek smoke 完成五个 calls 后在 `awaiting_review` 前安全失败；第二次在 exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de` 只运行 `product_intake_v1 / v1` 一次即以固定安全 HTTP 500 终止。
- 第二次 safe metadata 为 input / output / total = 2,353 / 8,192 / 10,545，latency = 106,434 ms，低于 120 s profile timeout；retry / recovery = 0 / 0，全部 behavior gates 为 false，stage 2～5 未运行。
- Sanitized evidence 不含 `finish_reason`、raw output、reasoning、prompt、candidate、traceback 或内部错误类别。
- 当前 adapter 对 length、empty content、malformed / non-object JSON、unexpected response shape、Schema mismatch 与 Domain-invalid candidate 有彼此独立的安全失败路径。
- 两次 live authorization 都已消费；当前没有新的 Provider run authority。

### Observation

- `8,192 == max_tokens` 使 length / truncation 成为高价值假设，但不足以证明历史调用的 finish reason。
- 第二次 latency 低于 120 s，因此当前 metadata 没有显示 application deadline boundary 被触及。
- 多个 adapter failure branch 可以产生同一外部 safe HTTP 500；只有通过 red-capable offline repro 才能逐项淘汰。
- DeepSeek 官方说明可帮助设计 length、truncation 与 empty-content fixtures，但不能替代项目内的历史证据。

### Risk

- 直接扩大 token budget 可能修错边界并增加未来付费成本。
- 为获得确定答案而访问 raw material 或发起新 live call 会突破已接受的安全与人工 Gate。
- 把 FL-1 foundation 写成完整 Goal 成功会隐藏真实 Provider failure。
- 过度构造离线矩阵会违反 DEC-039；Phase A 应围绕真实 adapter branches 和 observed boundary 保持最小。

### Accepted Decision

- [DEC-081](../decisions/dec-081-mvp0-fl2-offline-diagnosis-and-bounded-repair.md) — 用户于 2026-08-14 明确确认 Option B：Goal 保持 `GOAL_BLOCKED`，FL-1 只作为 accepted foundation；授权 Phase A 离线诊断，Phase B 仅在 Phase A 独立审阅并冻结 exact repair contract 后才可由主控授权。
- Phase A 在 sanitized evidence 无法区分假设时必须返回 `INSUFFICIENT_SANITIZED_EVIDENCE` 并停止。
- 任何未来真实 Provider run 仍需新的 exact-commit contract 与用户明确授权。

### Open Question

- 哪个最小 synthetic fixture 能在不模拟整个 HTTP / PostgreSQL vertical 的情况下复现 exact first-stage safe failure boundary？
- 当前安全 metadata 是否足以把候选假设缩小到一个可修复边界，还是 Phase A 必须以 `INSUFFICIENT_SANITIZED_EVIDENCE` 结束？
- 只有 Phase A evidence 可以回答 Phase B 是否存在、修改哪个模块以及最小验收是什么；当前不预选 repair。

## Alternatives

1. 把 deterministic FL-1 foundation 接受为完整 Fast Lane result；
2. 依据 token ceiling 立即修改 Product Intake Profile；
3. 读取 raw Provider material 或发起新调用；
4. 保持 `GOAL_BLOCKED`，先执行 bounded offline diagnosis。

## Rejected Approaches

- 方案 1 隐藏未完成的真实 Provider Goal 条件；
- 方案 2 把诊断线索误当作因果证据；
- 方案 3 突破 Secret / payload / paid-call Gate；
- 用户明确选择方案 4。

## Documentation Updates

- 新增 DEC-081 与本 Session；
- 更新 Decision Log；
- 同步 Fast Lane Goal、AGENTS、README、Implementation Readiness 与 DeepSeek handoff；
- 保留 DEC-079 / DEC-080 历史事实，不改写原始 evidence。

## Synchronization Checklist

- [x] Fact、Observation、Risk、Accepted Decision 与 Open Question 已分开记录
- [x] DEC-081 记录 Accepted / Amends / Applies / Preserves 关系
- [x] Current Truth 保持 `GOAL_BLOCKED`，没有把 FL-1 写成完整 MVP 接受
- [x] Phase A / Phase B 顺序与 `INSUFFICIENT_SANITIZED_EVIDENCE` stop 已记录
- [x] 没有创建业务实现、读取 Secret / raw material 或授权 Provider action
