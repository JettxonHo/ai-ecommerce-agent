# DEC-054：采用 Adapter Secret / Payload 边界与确定性模型验证

> **DEC-079 Amendment（2026-08-13）：** Secret / payload / telemetry allowlist 与“普通 PR 断网、单次人工 RC smoke”原则继续有效；当前 FL-2 使用 `deepseek_primary` / `DEEPSEEK_API_KEY` 与 DeepSeek 官方 API，只允许虚构 Anchor SKU，且不得把 DeepSeek 数据处理边界表述为 OpenAI `store=false` 或 ZDR。见 [DEC-079](dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)。

## Metadata

- **Status:** Accepted — MVP-0 Provider/Secret/live-smoke portions amended by [DEC-079](dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)
- **Date:** 2026-08-06
- **Decision Type:** LLM Runtime / Secret and Payload Boundary / Model Testing / Live Smoke
- **Source:** Session-003；用户明确接受 P-34A、P-35A
- **Related RFC:** [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)（Accepted；2026-08-06 用户明确整体接受）
- **Amends:** [DEC-052](dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md)（Secret 解析与 OpenAI Client 构造职责）

## Context

[DEC-052](dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md) 与 [DEC-053](dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md) 已冻结 Provider、Port、Structured Output、Recovery、Version Tuple 与五个 Profile。RFC-006 仍需决定 Secret 获取、Provider Payload、持久化与 Telemetry 的允许边界，以及如何在普通 PR 保持确定性、又在 Release Candidate 验证真实 Provider 闭环。

本决定只补全这两个运行契约，不建设泛化安全平台、外部 Evals 平台或 Live 测试矩阵。

## Decision

### 1. Adapter 边界解析 Secret

首个 Goal 只使用固定 Credential Reference `openai_primary`：

- Bootstrap / Composition Root 只选择该 Reference 并调用 Infrastructure Adapter Factory；
- Adapter 在自身边界内把 Reference 解析为进程环境中的 `OPENAI_API_KEY` 并创建 OpenAI Client；
- Secret Value 不回传 Bootstrap 配置对象，只在 Adapter 进程内存中短暂存在；
- Secret 不进入 Application / Domain、可序列化配置、数据库、Checkpoint、Work Intent、Audit、日志、Trace、Fixture、导出或 Git；
- 应用不加载或管理 `.env`，首个 Goal 不建设 Vault / KMS / Rotation Service；操作者通过 Shell 或外部启动器提供进程环境；
- 创建真实 Adapter 时缺少 Secret 必须 fail-fast；Provider 报告无效、撤销或无权访问时映射为 `configuration_or_access`；两者均不得静默切换到测试替身。

### 2. Provider 外部状态与最小发送

每次 Responses 请求显式设置 `store=false`，不使用 Conversations、Background Mode、Provider-hosted Tools 或 Provider Files。发送内容只包含 DEC-053 允许的 Stage Contract、Version Tuple、当前权威引用与已授权 Evidence Context，不发送整份 Source、无关 Workspace 内容或 Secret。

`store=false` 关闭 Response 对象默认至少 30 天的持久化，但不代表 Zero Data Retention，也不关闭所有 Provider Application State。按策划日 OpenAI 官方说明：

- 标准 API Abuse Monitoring Logs 可能包含客户内容并最长保留 30 天；
- 未启用 ZDR 时，受支持模型请求使用 Extended Prompt Caching；加密 Key / Value Tensor 位于 GPU-local Storage，最长约 24 小时；
- 本地演示不得假设账号已获 Modified Abuse Monitoring 或 Zero Data Retention。

### 3. 项目持久化与 Telemetry Allowlist

- Provider Call Ledger 只保存调用身份、Version Tuple、Provider response / request ID（存在时）、Model ID、Attempt / Recovery 关系、时间、Latency、Token Usage、Status、Error Category、disposition 与无明文 `credential_ref`；
- 通过项目 Schema / Validator 的 Provider-neutral Candidate 按对应业务版本生命周期保存，不保存原始 SDK / HTTP Response；
- 失败候选只保存为最小 Provider-neutral Diagnostic Candidate：结构化候选、Validation Errors、Evidence / Version References 与失败身份；它不进入 Current Truth、Audit 原文、日志或 Trace，删除期限由 ARP-08 决定；
- Rendered Prompt、完整 Context、原始 Provider Response、SDK Object、HTTP Body 与 Chain-of-thought 不单独持久化；
- Logs / Traces 只允许相关 ID、Version、Usage、Latency、Status、Error Category、Retry / Recovery Count 与 disposition。RFC-007 可以决定 Sink、采样与实现，但不得扩大本 Allowlist；
- 不建设通用内容扫描、复杂 Redaction Rule Engine 或低概率 Secret 变体矩阵。既有 Secret Detection Required Check 继续作为仓库泄漏 Gate。

### 4. 同 Port 确定性替身与分层 Contract Tests

实现 `ScriptedModelRuntime`，遵守与生产 Adapter 相同的 Model Runtime Port。它按可读 `scenario_id`、Profile、Schema Version 与 Call Ordinal 校验请求，并返回预先声明的 Provider-neutral Result / Error；不解析 Prompt 猜测答案、不模拟语言能力、不包含真实 SDK 类型。Spike-001 只提供测试设计证据，不复制其临时代码。

确定性测试分三层：

1. Port Contract：Request / Result / Error、Version Tuple、Profile 与 Call / Attempt / Recovery Identity；
2. OpenAI Adapter Contract：注入 SDK Client Stub 与最小 SDK-shaped Fixtures，断网验证 Responses 参数、`store=false`、Structured Output、Provider IDs、Usage 与 Error Classification；
3. Workflow / Skill Behavior：使用固定资料包验证 Candidate → Validator → Current Truth / Failure，不断言模型措辞。

只覆盖一个权威版本的代表性分支：valid success、transient failure then success、refusal、incomplete + one Recovery、Schema-invalid + one Repair、Domain-invalid → one Regeneration → second invalid → bounded failure，以及 cancelled / superseded late-result rejection。不得继续堆叠基本不可能出现的排列组合。

### 5. 单次人工 Release Candidate Smoke

普通 PR 默认断网并排除 `live` marker。真实 Smoke 只有同时满足以下条件才可由人工显式执行：

- 显式命令 / `live` marker；
- `RUN_LIVE_MODEL_SMOKE=1`；
- 可用 `OPENAI_API_KEY`；
- 已接受的 Model / Profile Version。

Secret 存在本身不得触发 Live Call。Release Candidate 只对 `fixture-sufficient-v1` 执行一次完整闭环，依次经过五个 Profile、Human Review、通用 Brief、小红书映射与 Markdown 导出；不运行额外 Live Edge-case Matrix，也不依赖 Provider Evals / Prompt Management 平台。

Smoke 证据只记录 Commit、Version Tuple、Run / Model Call IDs、Provider IDs（存在时）、Usage、Latency、Retry / Recovery Count、最终 disposition、行为门禁结果与人工 `PASS / FAIL` 理由。不得保存 Secret、完整 Prompt、原始 Response 或用户资料副本，不生成加权总分。失败证据必须保留并阻塞 Release Candidate；修复后产生新的 Run 证据，不覆盖原失败，也不得放宽 Schema、Validator 或 Gate。

## Alternatives Rejected

### 本地保存完整 Prompt / Response 或使用 Provider 远程状态

会重复保存用户资料、扩大 Retention / Backup / Redaction 范围，或让项目 Current Truth 与运行证据依赖外部控制面，因此拒绝。

### 只 Mock SDK，不提供同 Port Scripted Substitute

会使 Workflow / Skill 测试耦合 Provider SDK，难以稳定表达业务级 Result / Error / Recovery，因此拒绝。

### 普通 PR 直接调用真实 Provider

需要 Secret、网络和费用，结果具有波动，不能可靠区分代码回归与 Provider 波动，因此拒绝。

## Consequences

- Secret 与 Provider Payload 的数据面保持最小，职责边界清晰；
- 项目诚实记录 `store=false` 无法控制的 Provider 留存，不把它误称为 ZDR；
- 普通 PR 可以离线、确定性地验证软件契约；
- 单次 RC Smoke 只验证真实 Provider 兼容与完整用户闭环，不扩张成昂贵的 Live 测试矩阵；
- Fixture、SDK Stub 与 Smoke 操作手册仍须在 Goal 内形成独立、可审查的实现任务；
- P-34A / P-35A 的接受闭合 RFC-006 DQ-07～DQ-08，但不接受 RFC-006 整体。

## Relationships

- **Amends [DEC-052](dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md)：** 保留 Composition Root 的生命周期与注入职责，但把 Secret 解析和 OpenAI Client 构造收敛到 Infrastructure Adapter Factory。
- **Complements [DEC-053](dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md)：** 补全 Provider Adapter 的数据与验证边界。
- **Concretizes [DEC-048](dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)：** 将“确定性 PR 验证 + 单次 RC Smoke”落实为三层 Contract Suite 与人工 opt-in 规则，不改变非机械验收原则。
- **Applies [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 不使用 Hash / SHA-256，不建设泛化安全工程或低概率 Case 矩阵。
- **Applies RFC-001 / ARP-10：** Secret 获取封装在 Infrastructure Adapter，Secret Value 只在适配器内存短暂存在。
- **Input to [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)：** 接受 DQ-07～DQ-08；DQ-01～DQ-08 已全部闭合且 Final Consistency Review 已通过，用户已于 2026-08-06 明确接受 RFC-006 整体。

## Authorization Boundary

本决定：

- 不接受 RFC-006 整体；
- 不授权安装或升级 OpenAI SDK、读取真实 Secret、调用真实模型或执行 Live Smoke；
- 不授权创建 Model Runtime、Provider Adapter、Prompt、Fixture、Scripted Substitute、测试 Harness 或业务实现；
- 不授权执行 TS-01～TS-05、创建或激活长期 Goal；
- 不固定仍须实施证据校准的 Token / Timeout 数值或 RFC-007 运维参数。

## Evidence

- Session-003：用户于 2026-08-06 明确回复“接受 P-34A、P-35A”。
- RFC-006 Draft：[LLM Runtime and Structured Output](../rfcs/rfc-006-llm-runtime-and-structured-output.md)。
- [OpenAI Data Controls](https://developers.openai.com/api/docs/guides/your-data)
- [OpenAI Production Best Practices](https://developers.openai.com/api/docs/guides/production-best-practices)
- [OpenAI Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
