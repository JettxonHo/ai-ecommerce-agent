# DEC-052：采用 OpenAI Responses、窄型 Model Runtime Port 与项目权威 Structured Output 契约

> **DEC-079 Amendment（2026-08-13）：** 本文的 OpenAI / Responses / `gpt-5.6-terra` / Provider-native strict JSON Schema 条款作为历史基线保留；MVP-0 FL-2 的当前单一真实 Provider 已改为 DeepSeek 官方 `deepseek-v4-pro` Chat Completions + JSON Mode + 项目本地 Schema / Domain validation。Application-owned sync Port、无 router / fallback、确定性流程与本地校验权威继续有效。见 [DEC-079](dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)。

## Type

LLM Runtime / Provider Architecture / Structured Output / Dependency Injection

## Status

Accepted — Provider-specific portions amended by [DEC-079](dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)

## Date

2026-08-06

## Decision

### 单一真实 Provider 与模型基线

首个演示 MVP 只实现一个 OpenAI Provider Adapter，使用 Responses API、官方 Python SDK 与 `gpt-5.6-terra` 作为默认生产模型。模型调用只使用受控文本输入与 Structured Output，不开放 Web Search、File Search、Computer Use、Hosted Shell 或其他 Provider-hosted Tools，也不建设多 Provider 路由、自动降级或容灾。

实施时必须固定并记录已验证的 SDK / API / Model ID 组合；如存在适用的稳定 Model Snapshot，优先固定 Snapshot，否则固定已验证的稳定 Model ID。账号访问、结构化输出兼容性、固定验收包质量、延迟与成本仍须在实施授权后的兼容检查和 Release Candidate Smoke 中验证。若任一项形成阻塞，不得静默更换 Provider 或模型，必须暂停真实 Adapter 并提交 RFC Amendment。

### 项目自有窄型同步 Model Runtime Port

Application 定义项目自有、typed、Provider-neutral、同步的 Model Runtime Port；`platform/model_runtime` 提供唯一已接受 Provider 的 Infrastructure Adapter；Composition Root 创建并注入 Client / Adapter。Skill Application Service 只依赖 Port，不依赖 OpenAI SDK。

> **DEC-054 Amendment（2026-08-06）：** Composition Root 仍拥有 Adapter 生命周期与注入职责，但不直接解析 Secret 或构造 OpenAI Client。它调用 Infrastructure Adapter Factory；Factory 在 Adapter 边界解析 `credential_ref`、创建 Client / Adapter，并只把已构造的 Adapter 返回给 Composition Root。

Port 的概念输入只包含 `ModelCallRequest`、`StructuredOutputSpec`、`ModelExecutionProfile`、调用身份与受控上下文；概念结果只包含 Provider-neutral Output Envelope、Provider Call Metadata 与稳定内部 Error。SDK Client、SDK 类型、Credential 与原始 Response 对象只存在于 Infrastructure Adapter。

该 Port 只抽象首个 MVP 实际需要的语义，不承诺 Provider 可无成本替换，不实现 Provider Registry、Gateway、路由或 fallback。

### Structured Output 的项目权威边界

每个模型调用使用 Provider-native Strict Structured Output，但项目内 Pydantic / JSON Schema 仍是结构契约的权威来源，Skill Domain Validator 仍是业务语义的权威 Gate。Adapter 只能生成 Provider 支持的等价 Schema 表达；不支持的约束必须由本地原始 Schema / Domain Validator 保留，禁止静默丢失约束或改变字段语义。

固定处理链为：

```text
Provider Response
  -> Refusal / Incomplete / Transport Classification
  -> Structured Payload Parse
  -> Project Schema Validation
  -> Semantics-preserving Deterministic Normalization
  -> Skill Domain Validator
  -> Candidate Result
```

> **DEC-053 Amendment（2026-08-06）：** 上述历史链中的 Normalization 执行语义以后续决定为准：Parse / Project Schema 失败时只允许语义不变 Normalization，随后重新 Parse / Validate；仍失败才可使用共享的唯一 Model-assisted Recovery。Skill Domain Validator 只在结构通过后执行，且其 Candidate Regeneration 与 incomplete / repair 共用同一 Recovery Budget。

Schema 合规只代表结构有效，不代表事实、证据、战略或业务语义正确。Unknown Field 默认拒绝；禁止隐式弱类型转换、生成不存在的 Source / Fragment / Fact ID，或绕过 Skill Validator。`refusal`、`incomplete` 与无内容结果是显式非成功分支，不能伪装成合法 Schema 对象。修复、重新生成、Retry、取消和调用身份仍由 RFC-006 DQ-04 决定。

## Alternatives Considered

### Anthropic Claude API 或 Google Gemini API 作为首个真实 Provider

两者均具备 Structured Output 能力，但会增加不同程度的 Schema 子集、SDK / API 映射与数据边界验证成本。首个 Goal 只需要一个真实 Provider，因此不采用；这不是三家模型质量 Benchmark 的结论。

### Provider-shaped Low-level Port 或按 Skill 分设 Model Port

低层 Port 会把 Provider 参数上浮到 Skill / Application；按 Skill 分设 Port 会重复错误、元数据、版本与测试替身逻辑。两者都比单一窄型 Model Runtime Port 扩大治理面，因此不采用。

### Prompt-only JSON 或把全部结果建模为 Tool Call

Prompt-only JSON 会增加不必要的语法修复；把分析结果伪装为 Tool Call 会混淆模型输出与外部副作用。两者均不采用。

## Reason

OpenAI Responses API、官方 Python SDK 与项目的 sync-first Python 后端边界匹配，并提供本 RFC 所需的原生结构化输出、显式 refusal / incomplete 与 usage metadata。项目自有窄型 Port 将厂商类型收敛在 Infrastructure，同时避免为首个 MVP建设通用模型网关。Provider 的结构保证与项目 Schema / Domain Validator 分层，既减少常见格式失败，又不把 Schema 或 Rubric 误当自动接受器。

## Consequences

### Positive

- 四个 Core Skills 与 Xiaohongshu Adapter 不直接依赖 OpenAI SDK；
- 确定性测试替身可实现同一 Port；
- Provider 格式、项目结构契约与业务语义校验职责清晰；
- 首个 Goal 不承担多 Provider 容灾、Provider-hosted Tools 或通用 Gateway 的复杂度。

### Costs and Risks

- 首个 MVP 存在单 Provider 依赖，Provider 不可用时没有自动容灾；
- 需要维护少量项目自有请求、响应、元数据和错误类型；
- Provider 支持的 JSON Schema 子集、账号权限、模型稳定性、质量、延迟与成本仍须以实施时证据验证；
- 本决定形成时 DQ-04～DQ-08 尚未闭合；后续由 DEC-053 / 054 闭合，仍不得由实现 Agent 绕过最新 Accepted Decision 临场决定。

## Amendments and Relationships

- **Conforms to [DEC-011](dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)：** LLM 只生成 Candidate / Inference / Hypothesis / Draft，不能直接写 Business Current Truth。
- **Complements [DEC-033](dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)：** 本决定冻结 Structured Output 分层；具体有界修复、重试、取消和错误处置仍由 RFC-006 DQ-04 与 DEC-033 共同约束。
- **Amended by [DEC-053](dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md)：** 收敛 Normalization / Repair / Domain Validator / Regeneration 顺序与共享 Recovery Budget。
- **Conforms to [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 不新增 Hash / SHA-256，不堆叠低概率防御变体，不以机械评分接受模型结果。
- **Conforms to [RFC-001](../rfcs/rfc-001-repository-and-application-architecture.md)：** 遵守 Application-owned Port、Infrastructure Adapter、Composition Root、sync-first 与 Provider 类型隔离。
- **Conforms to [RFC-002](../rfcs/rfc-002-persistence-and-transaction-architecture.md)：** Provider Call 不跨 Business Transaction，Secret 与外部数据遵守既有边界。
- **Amended by [DEC-054](dec-054-adapter-secret-payload-boundary-and-deterministic-model-verification.md)：** Composition Root 只调用 Infrastructure Adapter Factory 并管理返回 Adapter 的生命周期；Secret 解析与 OpenAI Client 构造收敛在 Adapter 边界。
- **Input to [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md)：** 接受 DQ-01～DQ-03；DQ-01～DQ-08 后续均已闭合且 Final Consistency Review 已通过，用户已于 2026-08-06 明确接受 RFC-006 整体。

## Authorization Boundary

本决定只授权 Decision、RFC、Current Truth、Readiness 与 Traceability 文档同步：

- 不接受 RFC-006 整体；
- 不授权安装或升级 OpenAI SDK、读取真实 Secret、调用真实模型或执行 Live Smoke；
- 不授权创建 Model Runtime、Provider Adapter、Prompt、Prompt Registry、Schema Runtime 或测试替身实现；
- 不授权执行 TS-01～TS-05、业务实现、生产实现或长期 Goal；
- 本决定形成时 DQ-04～DQ-08 是后续 Gate；它们后由 DEC-053 / 054 闭合。Final Consistency Review 与用户 RFC 整体接受仍是后续 Gate。

## Accepted From

- Session-003：P-28A、P-29A、P-30A；用户于 2026-08-06 明确回复“接受 P-28A、P-29A、P-30A”。
- RFC-006 Draft：[LLM Runtime and Structured Output](../rfcs/rfc-006-llm-runtime-and-structured-output.md)。
- GitHub：[Issue #48](https://github.com/JettxonHo/ai-ecommerce-agent/issues/48) / [Draft PR #49](https://github.com/JettxonHo/ai-ecommerce-agent/pull/49)。
