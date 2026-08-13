# DEC-081：MVP-0 FL-2 离线诊断与有界修复路径

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-14
- **Decision Type:** Goal Governance / Offline Diagnosis / Bounded Repair / Provider Gate
- **Source:** [Session-006](../sessions/session-006-mvp0-fl2-terminal-diagnosis-decision.md)；用户明确确认 Option B
- **Issue:** [#285](https://github.com/JettxonHo/ai-ecommerce-agent/issues/285)
- **Amends:** [DEC-078](dec-078-mvp0-fast-lane-execution-rebaseline.md) 的 FL-2 terminal result 后续执行顺序
- **Applies:** [DEC-079](dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)、[DEC-080](dec-080-fl2-xiaohongshu-profile-v2-and-deadline-fence.md) 与 [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)
- **Preserves:** [DEC-039](dec-039-proportional-validation-and-review-governance.md) 的适度验证；DEC-079 / DEC-080 的 Provider、Schema / Domain、Secret、retry 与 evidence 边界；两次 terminal smoke 事实与 `GOAL_BLOCKED`

## Context

FL-1 deterministic browser-to-backend-to-export vertical 与 one-command local demo 已完成并经过离线验证。这是可复用的产品与工程基础，不等于完整 MVP-0 Fast Lane Goal 已接受或真实 Provider 路径已通过。

两次受控 DeepSeek smoke 都在进入 `awaiting_review` 前安全失败：第一次完成五个有序调用，第二次在 exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de` 只执行一个 `product_intake_v1 / v1` call 后以固定安全 HTTP 500 终止。第二次 safe metadata 为 input / output / total = 2,353 / 8,192 / 10,545，latency = 106,434 ms，低于 120 s profile timeout；retry / recovery = 0 / 0，全部 behavior gates 为 false，stage 2～5 未运行。

`8,192 == max_tokens` 是诊断线索，不是已证明根因。Sanitized evidence 不包含 `finish_reason`、raw output、reasoning、prompt、candidate、traceback 或内部错误类别。当前 adapter 对 `finish_reason=length`、empty content、malformed / non-object JSON、unexpected response shape、Schema mismatch 与 Domain-invalid candidate 分别存在安全失败映射，因此不能仅凭 token ceiling 相等选择其中一种历史失败类别。

DeepSeek 官方资料说明 `finish_reason=length` 可表示输出达到 `max_tokens` 或 context-length 边界，JSON Output 需要合理 token limit 以避免截断，也可能偶发 empty content。这些资料只提供可证伪假设，不证明历史调用属于其中任何一种。

## Decision

### 1. Canonical Goal 状态与 FL-1 边界

Canonical status 保持：**MVP-0 Fast Lane `GOAL_BLOCKED`; bounded offline diagnosis authorized, not yet diagnosed or repaired.**

FL-1 deterministic completion 是已验证 foundation。它不满足完整 Goal 的真实 Provider happy-path 条件，也不改变两次 terminal smoke 的失败事实。

### 2. Phase A — diagnosis

授权创建一个独立、离线、tests-first 的 Phase A Issue，目标是在不使用 Provider material 或真实调用的情况下，为 exact `product_intake_v1 / v1` first-stage failure boundary 建立快速、确定性、red-capable feedback loop。

Phase A 必须：

1. 从当前安全 adapter / mapper / Schema / Domain boundary 建立最小行为入口；
2. 明确列出并排序多个可证伪假设，而不是预选结论；
3. 至少区分 `finish_reason=length` / truncation、empty content、malformed 或 non-object JSON、unexpected response shape、Schema mismatch 与 Domain-invalid candidate 等当前真实分支；
4. 先捕获能对应观测边界的 TRUE RED，再最小化复现；
5. 在复现与最小化完成前，不修改生产 repair 行为；
6. 只使用 synthetic、fictional、sanitized offline fixtures，不读取历史 raw Provider material。

如果现有 sanitized metadata 与安全边界不能在不访问 raw Provider material、Secret 或新 live call 的情况下区分假设，Phase A 必须返回固定结论 `INSUFFICIENT_SANITIZED_EVIDENCE` 并停止；不得为了产出修复而猜测根因。

### 3. Phase B — minimal repair

Phase B 只有在 `ORCHESTRATOR_REVIEWER` 独立审阅 Phase A 的复现、假设淘汰与最小失败边界后才能开始。主控必须基于该证据冻结一个新的 exact bounded repair contract，包含允许文件、non-goals、tests-first 入口、验收与 stop conditions。

在 Phase A 证据充分、Phase B 合同完全位于本决定边界内且没有触发 stop condition 时，主控可授权普通离线 Phase B repair，无需再次取得语义层用户确认。这项授权不允许主控选择新的 Provider、产品方向、公共契约或付费行为。

### 4. 保持关闭的 Provider 与高风险边界

本决定不授权：

- Secret 读取、注入、回显或凭证环境操作；
- raw response、reasoning、prompt、candidate、traceback、账户或余额检查；
- Provider / network call、付费动作、PostgreSQL live smoke、第三次真实运行、retry、recovery 或 regeneration；
- model / Provider / Base URL substitution；
- public API / OpenAPI、migration、dependency / lockfile 或产品方向变更。

任何未来真实 Provider run 都必须使用新的 exact-commit execution contract，并再次获得用户明确授权。普通本地操作预授权不能替代这一 Gate。

## Alternatives Considered

### 接受 FL-1 deterministic 结果作为完整 Fast Lane MVP

拒绝。FL-1 证明本地纵向产品基础，但 Goal 的真实 Provider happy path 仍未通过，把 foundation 写成完整接受会隐藏 FL-2 失败。

### 立即按 token ceiling 扩大 Product Intake Profile

拒绝。Ceiling equality 只缩小假设空间；缺少 `finish_reason` 与安全错误类别时，直接修改 Profile 会把相关性写成因果关系。

### 访问历史 raw material 或再运行一次 Provider 来诊断

拒绝。这会突破已接受的 Secret / payload / evidence 与付费 Gate，也与两次授权均已消费的事实冲突。

### 先离线诊断，再基于复现证据决定最小修复

接受。该路径保留真实失败、允许快速学习，并把任何生产改动推迟到 red-capable evidence 之后。

## Consequences

- 项目可以继续利用已完成的 FL-1 foundation，而不把它误写为完整 Goal 成功。
- Phase A 可能以 `INSUFFICIENT_SANITIZED_EVIDENCE` 结束；这是诚实的 terminal diagnosis result，不是交付失败。
- Phase B 不保证存在，也不预先冻结 repair 方向；只有 Phase A evidence 可以定义它。
- 任何生产修复仍需 tests-first、Required Checks 与独立五轴 Review。
- 本决定不重新打开 live execution authority；未来真实调用仍是独立人工 Gate。

## Authorization Boundary

本文档合并后只授权主控建立 Phase A 的独立离线 Issue / Task Contract。可执行代码仍按 DEC-071 / DEC-072 路由给准确名称的 `luna-worker`，并分别记录配置与运行时身份；不得静默回退 Terra。

Phase B 在 Phase A 独立审阅与 exact contract 之前保持未授权。任何 stop condition、证据不足、范围扩大、Provider / Secret / public contract / migration / dependency / product-direction 需要都必须返回主控和用户，不得自行继续。

## Official Hypothesis Inputs

- [DeepSeek Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion)
- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/)
- [DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode)

这些链接只支持 Phase A 的假设设计，不构成历史失败类别证明。
