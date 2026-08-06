# DEC-053：采用有界模型恢复、可读版本身份与确定性 Skill Profile

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-06
- **Decision Type:** LLM Runtime / Failure Recovery / Versioning / Invocation Profile
- **Source:** Session-003；用户明确接受 P-31A、P-32A、P-33A
- **Related RFC:** [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)（Accepted；2026-08-06 用户明确整体接受）
- **Amends:** [DEC-033](dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md) 与 [DEC-052](dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md)（Structured Output Recovery 顺序与共享预算）

## Context

[DEC-052](dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md) 已冻结单一 OpenAI Responses Provider、窄型同步 Model Runtime Port 与 Structured Output Authority，但错误恢复预算、调用身份、版本记录和五个 Skill / Adapter 的调用 Profile 尚未冻结。若这些内容留给实现 Issue 临场决定，SDK Retry、Workflow Retry 与 Model Repair 可能嵌套放大，历史结果也可能因 Prompt、Schema 或 Profile 漂移而不可解释。

## Decision

### 1. 单一有界 Model Operation Budget

OpenAI Python SDK 的隐式 Retry 必须关闭（`max_retries=0`），由项目在 DEC-033 的单一 Retry Budget 与 Overall Deadline 内控制调用：

- 一个 Model Operation 最多包含 2 个 Model Call：1 个初始调用与最多 1 个 Model-assisted Recovery；
- 两个 Model Call 共享最多 1 次额外传输 Retry，因此整个 Operation 最多发起 3 次 Provider Transport Attempt；
- 连接失败、Timeout、429 与可重试 5xx 可以消耗该传输 Retry；Authentication、Permission、Model Access 与 Invalid Request 不重试；
- `refusal` 不自动重试；`incomplete` 只有在 Profile 预先定义适用恢复变体时才能使用唯一 Recovery；
- Parse / Schema 失败只对语义不变表达问题执行 Deterministic Normalization，随后重新 Parse 与重新验证 Schema；
- Domain Validator 失败发生在 Schema / Normalization 通过之后，不重复 Normalization；
- `incomplete` Recovery、Constrained Repair 与 Candidate Regeneration 共享唯一 Model-assisted Recovery，不允许形成 Repair 后再 Regenerate 的链；
- Retry 不创建业务版本，Recovery 不能自行触发 Workflow Rerun。

相同语义请求使用稳定 `model_call_id`，每次传输尝试创建新的 `provider_attempt_id`。Recovery 创建新的 `model_call_id`，以 `recovers_call_id` 关联原调用，并记录 `recovery_kind = incomplete | repair | regeneration`。Provider response / request ID、实际 Model ID、Attempt 次序与 disposition 在存在时进入 Provider-neutral Metadata。

同步调用不切换为 Responses Background Mode。取消使用调用前检查、受控 Timeout、调用返回后检查与 Node / Commit 前检查；Cancellation、Supersession 或 Ownership Loss 后返回的结果必须丢弃。

### 2. 项目权威、可读的 Version Tuple

项目在 Source Control 中维护显式、可读、单调演进的 Model Runtime Version Tuple，不使用内容 Hash / SHA-256 作为身份，也不引入外部 Prompt Management SaaS。每个 Model Call 至少绑定：

- `provider_id` / `api_family` / `sdk_version`；
- `configured_model_id` / `resolved_model_id`（Provider 提供时）；
- `prompt_template_id` / `prompt_template_version`；
- `output_schema_id` / `output_schema_version`；
- `skill_contract_version` / `domain_validator_version`；
- `execution_profile_id` / `execution_profile_version`；
- `context_assembly_version`。

实际 Tuple 必须固化到 Model Call Record 与 Candidate Metadata，不得以后续配置回写历史。行为变化提升对应版本；Breaking Change 创建新 Major / 新 ID。Model Alias 或 Snapshot 变化属于受控发布，必须触发固定验收包回归和适用 Live Smoke。

### 3. 五个固定 Invocation Profile

首个 Goal 使用五个版本化 Profile，全部调用 DEC-052 接受的同一 Provider / Model，且 Provider-hosted Tools 固定为 `none`：

| Profile | Initial Reasoning Effort | Purpose |
|---|---:|---|
| `product_intake_v1` | `low` | 受 Schema 与 Evidence ID 约束的事实候选提取 |
| `customer_insight_v1` | `medium` | 多条证据的主题与需求归纳 |
| `product_positioning_v1` | `high` | 多候选战略推理与权衡 |
| `marketing_brief_v1` | `medium` | Approved Strategy Lock 下的平台中立 Brief |
| `xiaohongshu_mapping_v1` | `low` | Brief Lock 下的方向化平台映射 |

`max_output_tokens`、Call Timeout 与一次恢复变体必须进入同一 Versioned Profile；精确值不在策划阶段虚构，而是在实施授权后根据固定 Schema 大小、三个验收资料包与已接受 Retry Budget 校准，并由 Sol 独立审查。实现 Agent 不得在运行时自由改变 Reasoning、Token、Timeout 或工具权限。

Context 由 Application / Retrieval Runtime 确定性装配，优先级固定为：Stage / Schema / Validator / Allowed Actions → 当前权威 Domain Version / Approved Strategy / Brief → 当前 Source Set 的 Evidence Package、允许 ID、Conflicts、Hypotheses、Limitations → 可选补充 Fragment。预算不足只裁剪最后一层；不得截断 ID、删除限制、混入旧版本或越权 Source。前三层无法完整装入时返回 `context_budget_exceeded`，不静默摘要或缩小约束。

## Alternatives Rejected

### 保留 SDK 默认 Retry 并叠加项目 Retry

会形成难以解释的嵌套预算、Deadline 与调用次数，因此拒绝。

### 所有 Provider / Candidate 失败立即终止

虽然最简单，但一次瞬时失败或一次可纠正输出会直接破坏演示闭环，因此拒绝。

### Provider 托管 Prompt 作为权威，或只记录应用 Release

前者使项目历史依赖外部控制面，后者无法解释局部模型配置回归，均不满足本地可复现与历史可解释目标。

### 所有 Skill 共用全局 Profile，或由模型动态选择 Profile / Tool

前者无法反映 Stage 的真实成本与推理差异；后者把权限、成本与确定性边界交给模型，均拒绝。

## Consequences

- Provider 调用次数、成本和恢复路径具有硬上限；
- Prompt、Schema、Validator、Profile 和 Context 变化可以被明确追踪；
- 五个 Stage 的推理投入不同，但不会建设动态 Router、多模型路由或工具自治；
- 精确 Token / Timeout 值仍需实施证据，不得由实现 Agent 无审查决定；
- 本决定形成时 P-34 / P-35 仍待冻结；后续已由 DEC-054 接受并补全 Secret / Payload / Telemetry、确定性替身、Contract Tests 与 Live Smoke。

## Relationships

- **Builds on and Amends [DEC-052](dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md)：** 在已接受 Provider / Port / Schema 权威上补全 DQ-04～DQ-06，并收敛 Normalization 后重新 Parse / Validate、Repair / Regeneration 分工与共享 Recovery Budget。
- **Amends [DEC-033](dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)：** 把条件式 LLM Recovery Stages 收紧为单次共享 Recovery 与单一 Retry Budget，并明确 Parse / Schema 失败后的语义不变 Normalization 必须重新 Parse / Validate；不删除任何 Schema / Validator Gate。
- **Applies [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 只覆盖代表性真实失败，不建设修复树、低概率错误矩阵、内容 Hash 或机械评分。
- **Input to [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)：** 接受 DQ-04～DQ-06；DQ-01～DQ-08 后续均已闭合且 Final Consistency Review 已通过，用户已于 2026-08-06 明确接受 RFC-006 整体。

## Authorization Boundary

本决定：

- 不接受 RFC-006 整体；
- 本决定本身不接受 P-34 / P-35；它们后由 DEC-054 单独接受；
- 不固定未经实施证据校准的 Token / Timeout 数值；
- 不授权安装或升级 OpenAI SDK、读取真实 Secret、调用真实模型或执行 Live Smoke；
- 不授权创建 Model Runtime、Prompt、Provider Adapter、Profile Registry 或业务实现；
- 不授权执行 TS-01～TS-05、创建或激活长期 Goal。

## Evidence

- Session-003：P-31A、P-32A、P-33A；用户于 2026-08-06 明确回复“接受 P-31A、P-32A、P-33A”。
- RFC-006 Draft：[LLM Runtime and Structured Output](../rfcs/rfc-006-llm-runtime-and-structured-output.md)。
