# RFC-006：LLM Runtime and Structured Output

## Metadata

- **Status:** DRAFTING
- **Date:** 2026-08-06
- **Issue:** [#48](https://github.com/JettxonHo/ai-ecommerce-agent/issues/48)
- **Pull Request:** [#49](https://github.com/JettxonHo/ai-ecommerce-agent/pull/49)（Draft）
- **RFC Acceptance:** NOT GRANTED
- **Implementation Authorization:** NOT GRANTED
- **Spike Execution Authorization:** NOT GRANTED
- **Goal Activation:** NOT GRANTED

## Problem

首个演示 MVP 已确定使用一个真实 LLM Provider 与一个确定性测试替身；DEC-052 / 053 已进一步冻结生产 Provider、默认模型、SDK 能力基线、项目内 Model Runtime Port、Structured Output Authority、有界 Recovery、可读版本元组与确定性 Skill Profile。Secret / Payload / Telemetry、确定性测试替身和 Live Smoke 边界仍未冻结。若把剩余选择留给单个实现 Issue 临场决定，Provider Output、运行证据、敏感内容、测试替身和 Current Truth 仍可能被写入同一职责。

RFC-006 需要在不实现 Prompt Runtime、不调用真实模型、不扩大 MVP 的前提下，冻结一个足够窄、可测试、可追溯的生产 LLM Runtime 契约。

## Context

RFC-006 必须同时满足：

- 首个 Goal 只实现一个真实 Provider，不建设多 Provider 路由或容灾；
- LLM 只生成 Candidate / Inference / Hypothesis / Draft，不能直接写 Business Current Truth；
- Workflow、Evidence、版本、失效、Validator、Human Review 和业务提交仍由确定性程序控制；
- Skill、Application 和 Public Contract 不得暴露 Provider SDK 类型；
- Provider Call 不得跨 Business Transaction，Retry 不等于业务 Rerun；
- 普通 PR 使用确定性替身，真实 Provider 只用于 Release Candidate 的一次正常任务 Smoke；
- 安全与校验保持适度，不新增 Hash / SHA-256、低概率防御矩阵或机械模型评分；
- 本 RFC 的产品运行模型选择与开发 Agent 的 Sol / Luna / Terra 角色分工是两个独立维度，互不替代。

## Related Decisions and Specifications

- [DEC-011](../decisions/dec-011-deterministic-workflow-with-constrained-llm-reasoning.md)
- [DEC-022](../decisions/dec-022-workflow-framework-capability-requirements.md)
- [DEC-023](../decisions/dec-023-select-langgraph-stategraph-for-mvp-workflow.md)
- [DEC-026](../decisions/dec-026-product-intake-and-fact-extraction-skill-contract.md)
- [DEC-027](../decisions/dec-027-customer-insight-analysis-skill-contract.md)
- [DEC-028](../decisions/dec-028-product-positioning-skill-contract.md)
- [DEC-030](../decisions/dec-030-marketing-brief-generation-skill-contract.md)
- [DEC-033](../decisions/dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)
- [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md)
- [DEC-041](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md)
- [DEC-048](../decisions/dec-048-small-acceptance-pack-behavior-gates-and-markdown-export.md)
- [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md)
- [DEC-053](../decisions/dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md)
- [RFC-001](rfc-001-repository-and-application-architecture.md)
- [RFC-002](rfc-002-persistence-and-transaction-architecture.md)
- [RFC-003](rfc-003-langgraph-runtime-and-checkpoint-architecture.md)
- [Integration Boundaries](../architecture/integration-boundaries.md)
- [Testing Strategy](../development/testing-strategy.md)

## Scope

- 单一生产 Provider、默认模型、API 与 SDK 能力基线；
- 项目自有 Model Runtime Port、同步调用与依赖注入边界；
- Provider-native Structured Output 与项目 Schema / Validator 的职责；
- Provider 错误、拒绝、不完整输出、解析、标准化、修复、重新生成、Retry 和取消边界；
- Prompt / Model / Schema / Skill Contract / Validator / Execution Profile 版本身份；
- 各 Skill 的模型调用 Profile、上下文装配和工具权限；
- Secret、Provider Payload、持久化和 Telemetry 允许边界；
- 确定性替身、Contract Tests、固定验收包与 Release Candidate Live Smoke。

## Non-goals

- 多 Provider 路由、故障转移、自动降级或 Provider Marketplace；
- Multi-Agent、LLM Supervisor、ReAct 主流程或自治工具选择；
- Embedding、Vector Store、Retrieval Fusion 或联网研究能力（RFC-005）；
- HTTP 状态、Frontend 状态或公共 API Error Contract（RFC-004）；
- 日志 / Trace SaaS、告警与最终 Timeout / Backoff / Circuit Breaker 参数（RFC-007）；
- 正式业务 Prompt、Provider Adapter、Prompt Registry、测试 Harness 或 Live Spike 实现；
- 完整小红书正文、图片 / 视频生成、自动发布或其他非 MVP 能力；
- 执行 TS-01～TS-05 或激活长期 Goal。

## Decision Status

| Decision Question | Proposal | Status |
|---|---|---|
| DQ-01 Provider / Model / SDK Capability Baseline | P-28A | ACCEPTED INPUT（DEC-052） |
| DQ-02 Model Runtime Port, DI and Configuration | P-29A | ACCEPTED INPUT（DEC-052） |
| DQ-03 Structured Output Contract and Schema Authority | P-30A | ACCEPTED INPUT（DEC-052） |
| DQ-04 Provider Failure, Repair, Retry, Cancellation and Call Identity | P-31A | ACCEPTED INPUT（DEC-053） |
| DQ-05 Prompt / Model / Schema / Execution Configuration Versioning | P-32A | ACCEPTED INPUT（DEC-053） |
| DQ-06 Skill-specific Invocation Profiles and Context Assembly | P-33A | ACCEPTED INPUT（DEC-053） |
| DQ-07 Secret, Provider Payload, Persistence and Telemetry Boundary | P-34 | PROPOSED |
| DQ-08 Deterministic Substitute, Contract Tests and Live Smoke | P-35 | PROPOSED |

用户已于 2026-08-06 明确接受 P-28A～P-30A 与 P-31A～P-33A，分别由 [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md) 与 [DEC-053](../decisions/dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md) 归档。DQ-01～DQ-06 已闭合；DQ-07～DQ-08、RFC-006 Final Consistency Review 与 RFC 整体接受仍未完成。

## Accepted Decision Round 1

### P-28：Provider / Model / SDK Capability Baseline

#### P-28A（已接受）：OpenAI Responses API + GPT-5.6 Terra + 官方 Python SDK

首个 Goal 只实现 OpenAI 一个真实 Provider Adapter，使用 Responses API、官方 Python SDK 与 `gpt-5.6-terra` 作为默认生产模型。模型调用保持纯文本输入 / Structured Output，不开放内置 Web Search、File Search、Computer Use、Hosted Shell 或其他 Provider-hosted Tools。部署时固定已验证的 SDK / API 组合，并在 Compatibility Matrix 记录实际 Model ID；若厂商提供可用的稳定 Snapshot，优先固定 Snapshot，否则固定已验证的稳定 Model ID 并把模型变更视为受控配置变更。

- **优点：** 官方文档明确支持 Responses API、Structured Outputs、Pydantic 解析、显式 refusal / incomplete 状态与 usage metadata；Terra 定位为智能与成本平衡档，适合本地演示的多阶段分析；与 Python sync-first 后端自然对接。
- **缺点：** 单厂商依赖；当前文档化 Model ID 仍需在实施时验证行为稳定性和账号可用性；标准数据控制下 Provider 可能保留请求相关数据，具体最小发送与 `store` 策略仍须由 DQ-07 冻结；Provider 服务不可用时 MVP 不具备自动容灾。
- **停止条件：** 实施时若账号无法访问所选模型、Structured Output 与同步 SDK 组合不兼容，或固定验收包出现阻塞性质量问题，暂停真实 Adapter，实现不得静默换 Provider / 模型，须提交 RFC Amendment。

#### P-28B：Anthropic Claude API + Sonnet 档模型 + 官方 Python SDK

首个 Goal 只实现 Anthropic 一个真实 Provider Adapter，使用 Messages API 的 JSON Structured Outputs、官方 Python SDK 与当前文档化的 `claude-sonnet-4-6`。

- **优点：** 官方 Structured Outputs 支持 JSON Schema、Pydantic 与显式 refusal / max_tokens；错误类型和 request ID 明确；可保持同样的单 Provider 边界。
- **缺点：** SDK 会转换部分不受支持的 Schema 约束，项目仍须保留本地原始 Schema / Validator；需要额外验证 Messages API 参数与项目 sync-first Port 的映射；标准商业 API 数据保留政策需单独评估。
- **停止条件：** 与 P-28A 相同；账号访问、Structured Output 兼容或固定验收包质量任一阻塞时，禁止静默换模型或 Provider。

#### P-28C：Google Gemini API + Stable API / Model + 官方 Python SDK

首个 Goal 只实现 Gemini 一个真实 Provider Adapter，显式使用稳定 `v1` API、官方 Python SDK 与当前文档化的稳定 `gemini-2.5-pro`。

- **优点：** 官方支持 JSON Schema / Pydantic Structured Output；稳定 API 版本和大上下文能力明确。
- **缺点：** Structured Output 只支持 JSON Schema 子集；官方 SDK 默认 API 版本可能与稳定 `v1` 不同；近期 API 形态存在迁移记录，首个 MVP 需要承担更多兼容验证。
- **停止条件：** 与 P-28A 相同；账号访问、稳定 API / Structured Output 兼容或固定验收包质量任一阻塞时，禁止静默换模型或 Provider。

#### 推荐理由

P-28A 是基于当前官方能力说明与项目已接受架构边界作出的**适配度推断**：OpenAI Responses API 已同时提供本 RFC 需要的结构化输出、refusal / incomplete、usage metadata 和 Python 支持，因此预计额外协议适配最少；这不是三家模型质量 Benchmark 的结论。三案的账号可用性、固定验收包质量、实际延迟和成本证据均尚未执行，必须在实施前置兼容检查与 Release Candidate Smoke 中验证。用户已接受 P-28A，但本 RFC 仍不授权安装 SDK、读取 Secret 或调用模型。

### P-29：Model Runtime Port, DI and Configuration

#### P-29A（已接受）：项目自有窄型同步 Port + 单一已接受 Provider Adapter

由 Application 定义项目自有、Provider-neutral、typed 的同步 Port，并在 `platform/model_runtime` 提供单一已接受 Provider 的 Infrastructure Adapter。概念输入只包含 `ModelCallRequest`、`StructuredOutputSpec`、`ModelExecutionProfile`、调用身份与受控上下文；概念结果只包含解析前的 Provider-neutral Output Envelope、Provider Call Metadata 和稳定内部 Error。具体 SDK Client、SDK 类型、Credential 和 Response 对象只存在于 Infrastructure Adapter。Composition Root 创建并注入单例 Client / Adapter，Skill Application Service 依赖 Port，不依赖厂商 SDK。

Port 只抽象 MVP 实际需要的共同语义，不承诺能无成本更换 Provider，也不实现多 Provider 注册、路由或 fallback。

- **优点：** 满足 RFC-001 的模块、DI 与 sync-first 边界；测试替身可实现同一 Port；未来更换 Provider 时影响收敛于 Adapter 与兼容验证。
- **缺点：** 需要维护少量项目自有类型和错误映射；若抽象过宽会退化成内部通用 SDK，因此必须限制字段。

#### P-29B：Application-owned Provider-shaped Low-level Port

仍由 Application 定义 Port、Infrastructure 隔离 SDK，但 Port 暴露较低层的 Message、Reasoning、Output Token、Response Format 与 Provider Capability 参数；Skill 或 Skill Executor 负责组合这些参数。

- **优点：** 更容易利用已选 Provider 的高级参数；Adapter 映射较薄；不会直接暴露 SDK 类型。
- **缺点：** Provider 参数和调用细节会上浮到 Skill / Application；确定性替身必须模拟更多低层能力；未来 Model ID 或 API 变化会扩大影响面。

#### P-29C：按 Skill 划分的 Application Model Ports

为 Product Intake、Customer Insight、Positioning、Marketing Brief 与 Xiaohongshu Adapter 分别定义窄型 Application Port，各 Port 返回对应 Skill 的 typed Candidate，由共享 Infrastructure Client 和内部 Adapter 复用底层调用。

- **优点：** 每个 Skill 的接口最贴近业务语义，调用方几乎看不到通用模型参数；单个 Port 容易阅读。
- **缺点：** 五套 Port 容易重复错误、元数据、版本和测试替身逻辑；跨 Skill 的统一调用身份、Profile 和 Structured Output 策略更难集中治理；更换公共运行行为需要多处同步。

#### 推荐理由

P-29A 是“单 Provider 实现”与“领域不依赖厂商 SDK”的最小交集。它不假装 Provider 可无成本替换，也不建设当前不用的容灾层。

### P-30：Structured Output Contract and Schema Authority

#### P-30A（已接受）：Provider-native Strict Schema + 项目 Schema + Domain Validator

每个模型调用使用 Provider-native Strict Structured Output；项目内 Pydantic / JSON Schema 是结构契约的权威来源，Adapter 负责生成 Provider 支持的等价 Schema 表达并把响应收敛为 Provider-neutral Envelope。Provider 不支持的约束必须在预检中显式识别并由本地原始 Schema / Domain Validator 保留，禁止静默丢弃约束或改变字段语义。处理链固定为：

```text
Provider Response
  -> Refusal / Incomplete / Transport Classification
  -> Structured Payload Parse
  -> Project Schema Validation
  -> Semantics-preserving Deterministic Normalization
  -> Skill Domain Validator
  -> Candidate Result
```

Schema 合规只证明结构有效，不证明事实、证据、战略或业务语义正确。Unknown Field 默认拒绝；禁止隐式弱类型转换、生成不存在的 Source / Fragment / Fact ID，或绕过各 Skill Validator。`refusal`、`incomplete` 与无内容结果是显式非成功分支，不能伪装成 Schema 对象。具体修复、重新生成与上限由 DQ-04 决定。

- **优点：** 消除常见 JSON 语法 / 必填字段错误，同时保留项目自己的业务权威；可用同一 Schema 驱动确定性替身和 Contract Test；与 DEC-033 的 Parse / Normalize / Repair / Regeneration 分层一致。
- **缺点：** Provider 支持的是 JSON Schema 子集，复杂业务约束仍需本地 Validator；Schema 转换和版本兼容需要明确测试。

#### P-30B：Prompt-only JSON + 本地解析

- **优点：** 不依赖 Provider Structured Output 功能，Prompt 简单时接入快。
- **缺点：** 语法、必填字段和枚举更易失败，增加不必要的修复调用；在已有原生 Structured Output 的前提下可靠性较低。

#### P-30C：全部结果建模为 Strict Tool Call

- **优点：** Tool Input 可用 Schema 约束，适合真实工具动作。
- **缺点：** 四个 Skills 的主要产物是结构化分析结果而非工具动作；把最终输出伪装成 Tool Call 会混淆“模型输出”和“外部副作用”。

#### 推荐理由

P-30A 同时利用 Provider 的结构保证与项目 Validator 的业务保证，不把 Structured Output 当作自动接受器，也不堆叠重复的防御性解析变体。

## Accepted Decision Round 2

### P-31：Provider Failure, Repair, Retry, Cancellation and Call Identity

#### P-31A（已接受）：项目统一预算 + 共享单次传输重试 + 单次 Model-assisted Recovery

Model Runtime Adapter 将 Provider / SDK 结果收敛为少量稳定内部类别：`configuration_or_access`、`invalid_request`、`transient_provider_failure`、`refusal`、`incomplete_output`、`invalid_candidate`、`cancelled_or_superseded`。Provider 的细粒度异常保留在诊断 metadata，不上浮为公共业务契约，也不为每个低概率子类型建立独立防御分支。

项目禁用 OpenAI Python SDK 的隐式重试（Client `max_retries=0`），由 Model Runtime 在 DEC-033 的单一 Retry Budget 与 Deadline 内控制：

- 一个 Model Operation 最多包含 **2 个 Model Call**（1 个初始调用 + 1 个 Model-assisted Recovery），并在两者之间共享 **最多 1 次额外传输重试**；因此整个 Operation 最多发起 **3 次 Provider Transport Attempt**，且 Overall Deadline 可进一步提前终止；
- 连接失败、显式 Timeout、429 与可重试 5xx 可以消耗这唯一的额外传输重试；存在 `Retry-After` 且仍能满足 Deadline 时遵守，否则直接失败；若初始 Model Call 已消耗该重试，Recovery Call 发生传输失败时不得获得新预算；
- Authentication / Permission / Model Access / Invalid Request 不重试；
- `refusal` 不自动重试，也不伪装成结构化结果；
- `incomplete` 仅在 Profile 预先定义了适用恢复变体、且 Deadline / Budget 允许时使用 1 次 Model-assisted Recovery，否则失败；
- Parse / Project Schema 失败时，只对 DEC-033 允许的语义不变表达问题执行零调用的 Deterministic Normalization，随后必须重新 Parse 并重新验证 Schema；仍失败时可使用精简 Schema 反馈执行 1 次 Constrained Repair；
- Skill Domain Validator 失败发生在 Schema 与 Normalization 已通过之后，不重复执行 Normalization；可使用精简 Validator 反馈执行 1 次 Candidate Regeneration；
- `incomplete` 恢复、Constrained Repair 与 Candidate Regeneration 共享同一个 **最多 1 次 Model-assisted Recovery** 预算。Responses API 没有独立的项目修复通道，因此这一次恢复在传输层表现为新的 Model Call，并以恢复原因区分 `repair` / `regeneration`；不得形成“修复 + 再修复 + 再生成”链，再次失败即终止当前 Model Operation；该收紧是对 DEC-033 条件式 Recovery Stages 的具体预算化，不删除其中任何校验步骤，也不允许先 Repair 再 Regenerate；
- Retry 只重发同一请求，不创建业务版本；Regeneration 是新的语义调用，也不能自行触发 Workflow Rerun。

每个相同语义请求使用稳定 `model_call_id`，每次传输尝试创建新的 `provider_attempt_id`；任何 Model-assisted Recovery 都创建新的 `model_call_id`，以 `recovers_call_id` 关联原调用，并用 `recovery_kind = incomplete | repair | regeneration` 区分原因。成功或失败时记录 Provider `response_id`（如存在）、SDK 暴露的 request ID、实际 Model ID、Attempt 次序与 disposition。模型调用没有项目外部业务副作用；Timeout 或连接中断后未观察到的 Provider 输出永远不能提交，只有当前有效 Ownership / Cancellation / Revision 下成功接收并通过 Validator 的 Candidate 才可进入 Commit。

同步调用不切换为 Responses Background Mode。由于 OpenAI Cancel API 只支持 `background=true` 的 Response，本项目的取消边界固定为：调用前检查 → 受控 Timeout → 调用返回后检查 → Node / Commit 前检查；在取消、Supersession 或 Ownership Loss 后返回的结果必须丢弃。

- **优点：** Retry Budget 只有一个所有者，避免 SDK 默认重试与 Workflow Retry 嵌套放大；失败分支少而明确；与同步 Port、协作式取消和 Current-Truth-first Commit 一致。
- **缺点：** Adapter 需显式映射可重试状态并尊重 `Retry-After`；同步请求不能向 Provider 发起中途取消，最坏仍需等待受控 Timeout。

#### P-31B：保留 SDK 默认重试，再由项目处理修复与再生成

- **优点：** Adapter 代码少，官方 SDK 已覆盖连接、408、409、429 与 5xx 的默认重试。
- **缺点：** SDK 默认重试、Model Runtime 重试与 Workflow Retry 形成嵌套预算；Timeout 也可能被 SDK再次尝试，Deadline 与真实调用次数不易解释。

#### P-31C：所有 Provider / Structured Output 失败立即终止，不做自动重试或再生成

- **优点：** 行为最简单、成本最可预测。
- **缺点：** 把一次瞬时网络 / 限流或一次可纠正的 Candidate 失败直接升级为用户可见失败，不符合本地演示的可靠性目标。

#### 推荐理由

P-31A 以“最多 2 个 Model Call、共享 1 次额外传输重试、整个 Operation 最多 3 次 Provider Attempt”的硬上限覆盖最常见且真实的失败，不建设复杂修复树。显式关闭 SDK 默认重试使 DEC-033 的 Budget、Deadline、Trace 与实际 Provider 调用次数保持一致。

### P-32：Prompt / Model / Schema / Execution Configuration Versioning

#### P-32A（已接受）：项目自有可读 Version Tuple + 每次调用固化快照

项目在 Source Control 中维护可读、显式的 Model Runtime Version Tuple，不引入外部 Prompt Management SaaS，也不使用内容 Hash 作为身份。每个 Model Call 至少绑定：

- `provider_id` 与 `api_family`；
- 锁文件中的 `sdk_version`；
- `configured_model_id` 与响应返回的 `resolved_model_id`（如 Provider 提供）；
- `prompt_template_id` / `prompt_template_version`；
- `output_schema_id` / `output_schema_version`；
- `skill_contract_version`；
- `domain_validator_version`；
- `execution_profile_id` / `execution_profile_version`；
- `context_assembly_version`。

以上使用人类可读、单调演进的显式版本；每次调用把实际 Tuple 固化到 Model Call Record 与 Candidate metadata，后续不得随配置漂移回写历史。Prompt、Schema、Validator、Profile 或 Context Assembly 的行为变化必须提升对应版本；破坏兼容的变化必须创建新 Major / 新 ID。Model alias 或 Snapshot 变化属于受控配置发布，必须经过固定验收包回归和适用 Live Smoke，不能只改环境变量后静默生效。

- **优点：** 运行结果可解释、可回归、可定位；不会把厂商 Prompt 对象或部署平台当项目权威；不需要 Hash / SHA-256。
- **缺点：** 需要维护一个小型版本清单并在变更 PR 中同步多个显式版本；人工漏升版本需要 Contract Test 发现。

#### P-32B：使用 OpenAI 托管 Prompt ID / Version 作为主要权威

- **优点：** Prompt 发布与回滚可由 Provider 管理，运行请求较简洁。
- **缺点：** 项目历史和 Review 依赖外部控制面；Prompt 与项目 Schema / Validator / Skill Contract 的复合兼容仍需另建本地记录；不利于本地可复现目标。

#### P-32C：只记录应用 Release Version，不拆分 Prompt / Schema / Validator / Profile

- **优点：** 字段最少，发布管理简单。
- **缺点：** 无法判断同一 Release 内哪项模型配置造成回归，也无法安全执行局部重跑和历史结果解释。

#### 推荐理由

P-32A 只记录真正影响模型行为与结果契约的身份，足以支持回归、Resume 和审计，又不引入通用配置平台、内容指纹或机械版本矩阵。

### P-33：Skill-specific Invocation Profiles and Context Assembly

#### P-33A（已接受）：五个命名 Profile + 确定性 Context Assembly + 无工具调用

四个 Core Skills 与 Xiaohongshu Adapter 各使用一个版本化、不可在运行中由模型改写的命名 Profile，并共用 DEC-052 接受的 Provider / Model：

| Profile | 初始 Reasoning Effort | 说明 |
|---|---:|---|
| `product_intake_v1` | `low` | 受 Schema 与 Evidence ID 约束的事实候选提取 |
| `customer_insight_v1` | `medium` | 多条证据的主题与需求归纳 |
| `product_positioning_v1` | `high` | 多候选战略推理与权衡，是 MVP 最高推理档 |
| `marketing_brief_v1` | `medium` | 在 Approved Strategy Lock 下生成平台中立 Brief |
| `xiaohongshu_mapping_v1` | `low` | 在 Brief Lock 下做方向化平台映射 |

所有 Profile 的 Provider-hosted Tools 均为 `none`。`max_output_tokens`、Call Timeout 与一次恢复变体必须写入同一 Versioned Profile；策划阶段不虚构秒数或 Token 数，实施前由固定 Schema 大小、三个验收资料包与 P-31 Budget 校准，并在该 Profile 的实现 PR 中由 Sol 独立审查。实现 Agent 不得在运行时自由改变 Reasoning、Token、Timeout 或工具权限。

Context 由 Application / Retrieval Runtime 在调用前确定性装配，Provider 不能扩大范围。优先级固定为：

1. Stage 指令、输出 Schema、Validator 约束与允许动作；
2. 当前有效且明确授权的 Domain Version / Approved Strategy / Marketing Brief；
3. 当前 Source Set Version 对应的 Evidence Package、允许引用的 ID、Conflicts、Hypotheses 与 Limitations；
4. 仍有预算时加入的补充 Fragment。

预算不足时只按已版本化的装配规则裁剪第 4 层，并保留来源定位与原始 ID；不得截断关键 ID、删除 Evidence Limitation、把旧版本或越权 Source 补入上下文，也不得让模型自行检索更多资料。若第 1～3 层无法完整装入已批准 Profile，返回显式 `context_budget_exceeded` 技术失败并停止该 Stage，不静默摘要或缩小业务约束。Profile / Context Assembly 的任何行为变化按 P-32 提升版本并触发固定验收包回归。

- **优点：** 将推理成本集中到 Positioning，其他 Stage 保持适度；上下文可复现且不绕过 Retrieval / Permission / Current Truth；不用建设动态 Router。
- **缺点：** 五个 Profile 需要分别校准；固定 Profile 不会自动利用未来模型能力变化，升级须显式评测与版本变更。

#### P-33B：所有 Skill 共用一个全局 Profile 与相同 Context 模板

- **优点：** 配置最少，初始实现简单。
- **缺点：** Extraction、Strategic Reasoning 与 Platform Mapping 的成本 / 质量需求明显不同；单一大模板容易携带不相关上下文并扩大输出。

#### P-33C：由模型或运行时根据输入动态选择 Reasoning / Context / Tools

- **优点：** 理论上可自适应任务难度。
- **缺点：** 难以复现和回归；把成本、权限与工具边界交给模型，违反确定性工作流和本 RFC 的单一无工具 Provider 边界。

#### 推荐理由

P-33A 用五个显式 Profile 覆盖真实 Stage 差异，并把 Context Scope、权限、Current Truth 与 Evidence ID 控制留在确定性 Application / Retrieval 层。精确数值以小型固定资料包校准，避免在无证据时机械固定大参数矩阵。

## Proposed Decision Round 3

### P-34：Secret, Provider Payload, Persistence and Telemetry Boundary

#### P-34A（推荐）：Adapter 边界环境解析 + `store=false` + 最小 Provider Ledger + Payload-free Telemetry

首个本地演示只使用一个固定 Credential Reference（概念名 `openai_primary`）。Bootstrap / Composition Root 只选择该 Reference 并调用 Infrastructure Adapter Factory；Adapter 在自身边界内把 Reference 解析为进程环境中的 `OPENAI_API_KEY` 并创建 OpenAI Client，Secret Value 不回传 Bootstrap 配置对象。Secret Value 只在 Adapter 进程内存中短暂存在，不进入 Application / Domain、配置对象序列化、数据库、Checkpoint、Work Intent、Audit、日志、Trace、Fixture、导出或 Git。应用本身不加载或管理 `.env`，也不在 MVP 建设 Vault / KMS / Rotation Service；开发者可由 Shell 或外部启动器注入环境变量。

创建真实 Adapter 时缺少 Secret 必须 fail-fast；Provider 在调用时报告无效、撤销或无权访问的 Credential，则映射为 `configuration_or_access` 并停止受影响路径。两者均不得静默切换到测试替身。确定性测试的 Composition Root 显式注入 Scripted Substitute，因此不需要真实 Secret。

每次 Responses 请求显式设置 `store=false`，不使用 Conversations、Background Mode、Provider-hosted Tools 或 Provider Files。发送内容只包含 P-33 允许的 Stage Contract、Version Tuple、当前权威引用与已授权 Evidence Context，不把整份 Source、无关 Workspace 内容或 Secret 发送给 Provider。`store=false` 关闭 Response 对象默认至少 30 天的持久化，但不代表 Zero Data Retention，也不关闭所有 Provider Application State。按 2026-08-06 OpenAI 官方说明，标准 API 默认仍可能生成并最长保留 30 天 Abuse Monitoring Logs；未启用 ZDR 时，受支持模型的请求还会使用 Extended Prompt Caching，加密 Key / Value Tensor 位于 GPU-local Storage，最长约 24 小时。本地演示不假设账号已获 Modified Abuse Monitoring / Zero Data Retention。

项目持久化边界固定为：

- Provider Call Ledger 只保存调用身份、Version Tuple、Provider response / request ID（存在时）、Model ID、Attempt / Recovery 关系、时间、Latency、Token Usage、Status、Error Category 与 disposition；保存 `credential_ref`，不保存 Secret Value；
- 通过项目 Schema / Validator 的 Provider-neutral Candidate 按对应业务版本生命周期保存，不保存原始 SDK / HTTP Response；
- DEC-033 要求保留的失败候选只保存为 Provider-neutral Diagnostic Candidate：包含最小结构化候选、Validation Errors、Evidence / Version References 与失败身份，分类为 `MODEL_CONTENT / PROVIDER_PAYLOAD`，不进入 Current Truth、Audit 原文、日志或 Trace；具体删除期限由 ARP-08 / Retention Plan 决定；
- Rendered Prompt、完整 Context、原始 Provider Response、SDK Object、HTTP Body 与 Chain-of-thought 不单独持久化。历史解释依靠 Version Tuple、权威业务版本、Evidence Package 与 Provider-neutral Candidate；
- Logs / Traces 只允许相关 ID、Version、Usage、Latency、Status、Error Category、Retry / Recovery Count 与 disposition。RFC-007 决定 Sink / Trace Provider、采样和最终 Redaction 实现，但不得扩大本 RFC 的 Payload Allowlist。

不建设通用内容扫描、复杂 Redaction Rule Engine 或低概率 Secret 变体矩阵。Secret 通过“从不进入可序列化数据结构”的边界保护；既有 Secret Detection Required Check 继续作为仓库泄漏 Gate。

- **优点：** 与 ARP-10、RFC-001 配置边界、P-29 Port 隔离和本地演示范围一致；数据面最小、可追溯而不过度建设安全平台。
- **缺点：** 默认没有完整 Prompt / Response 可用于事后逐字回放；标准 Provider Abuse Monitoring 与 Prompt Cache Retention 不受项目 `store=false` 控制；本地环境变量由操作者负责注入。

#### P-34B：本地持久化完整 Prompt / Response，按日志 Redaction 处理

- **优点：** Provider 兼容问题和质量回归容易逐字调试。
- **缺点：** 重复保存用户资料、Evidence 与模型输出，扩大 Retention / Export / Backup / Redaction 范围；日志 Redaction 不能把敏感 Payload 自动变成低风险数据。

#### P-34C：使用 Provider `store=true`、Conversation State 与远程 Trace 作为运行证据

- **优点：** Provider 侧调试、历史续接与可视化较方便。
- **缺点：** 与同步、项目权威状态、本地可复现和最小外部持久化边界冲突；把运行证据依赖外部控制面，并扩大数据留存。

#### 推荐理由

P-34A 通过数据结构和职责边界避免 Secret / Payload 泄漏，而不是事后堆叠扫描器。最小 Ledger 足以支持 P-31 / P-32 的 Retry、版本和对账；业务 Candidate 与失败 Diagnostic Candidate 保留项目需要的证据，不复制原始 Provider Payload。

### P-35：Deterministic Substitute, Contract Tests and Live Smoke

#### P-35A（推荐）：同 Port Scripted Substitute + 分层 Contract Suite + 单次人工 RC Smoke

项目实现一个与生产 Adapter 遵守同一 Model Runtime Port 的 `ScriptedModelRuntime`。它按人类可读 `scenario_id`、Profile、Schema Version 与 Call Ordinal 校验请求并返回预先声明的 Provider-neutral Result / Error；不解析 Prompt 来猜测答案，不模拟模型语言能力，也不包含真实 SDK 类型。Spike-001 的 Scripted Model 只提供场景设计证据，不复制其生产代码。

确定性测试分三层：

1. **Port Contract：** Scripted Substitute 验证 Request / Result / Error、Version Tuple、Profile、Call / Attempt / Recovery Identity；
2. **OpenAI Adapter Contract：** 注入 SDK Client Stub 与最小 SDK-shaped Fixtures，验证 Responses 参数、`store=false`、Structured Output 映射、Provider IDs、Usage 与 Error Classification，全程断网；
3. **Workflow / Skill Behavior：** 使用固定资料包验证 Candidate → Validator → Current Truth / Failure 的行为，不断言模型措辞。

只覆盖已接受契约中的代表性分支：valid success、transient failure then success、refusal、incomplete + one Recovery、Schema-invalid + one Repair、Domain-invalid → one Regeneration → second invalid → bounded failure，以及 cancelled / superseded late result rejection。Domain-invalid 的唯一权威场景明确验证恢复预算耗尽后的终止；不再为“恢复后成功”重复增加一组 Case。每个分支只保留一个权威场景和必要的 Skill-specific Schema Fixture，不为基本不可能出现的排列组合重复建 Case。

普通 PR 继续默认断网并排除 `live` marker。Release Candidate 仅在同时满足显式命令 / `live` marker、显式 `RUN_LIVE_MODEL_SMOKE=1`、可用 `OPENAI_API_KEY` 与已接受 Model / Profile Version 时，人工执行一次 `fixture-sufficient-v1` 完整端到端 Smoke；Secret 存在本身不得自动触发 Live Call。该 Smoke 依次经过五个 Profile、Human Review、通用 Brief、小红书映射与 Markdown 导出，不执行额外 Live Edge-case Matrix，也不依赖 Provider Evals / Prompt Management 平台。

Live Smoke 必须记录 Commit、Version Tuple、Run / Model Call IDs、Provider IDs（存在时）、Usage、Latency、Retry / Recovery Count、最终 disposition、行为门禁结果与人工 `PASS / FAIL` 理由；不得保存 Secret、完整 Prompt、原始 Response 或用户资料副本。质量验收使用 DEC-048 的固定行为门禁和人工判断，不要求相同措辞，不生成加权总分。Smoke 失败必须保留失败记录并阻塞 Release Candidate；修复后可以产生新的独立 Run 证据，但不得覆盖原失败或通过放宽 Schema / Validator / Gate 使其通过。

- **优点：** PR 快速、可复现、无 Secret / 网络成本；生产 Adapter 映射仍有直接 Contract Test；真实 Provider 只验证确定性测试无法证明的兼容与质量闭环。
- **缺点：** Scripted Substitute 不能证明真实模型质量；SDK-shaped Fixture 在 SDK 升级时需要同步；RC Smoke 仍可能受账号、限流和 Provider 波动影响。

#### P-35B：只 Mock OpenAI SDK，不定义同 Port Scripted Substitute

- **优点：** 初始测试代码较少，直接贴近 Adapter。
- **缺点：** Skill / Workflow 测试耦合 Provider SDK 结构，难以稳定表达业务级 refusal、recovery、version 与 late-result 场景，也违反 P-29 的 Port 隔离目标。

#### P-35C：普通 PR 直接运行真实 Provider 测试

- **优点：** 每次改动都能看到真实模型结果。
- **缺点：** 需要 Secret 和网络，产生费用与波动，可能泄漏 Fork / CI 上下文；失败不能可靠区分代码回归与 Provider 波动，不适合作为普通 Required Check。

#### 推荐理由

P-35A 把软件契约正确性、Adapter 映射和真实模型可用性分开验证。它复用现有断网 Gate、固定验收包与人工判断，不引入外部 Evals 平台，也不把一次 Live Smoke 扩张成昂贵的全场景模型测试。

## Cross-RFC Ownership

| Topic | Owner | RFC-006 boundary |
|---|---|---|
| Worker / Checkpoint / Resume / overall retry budget / business rerun | RFC-003 | 只定义单次 Model Call 与输出修复语义 |
| HTTP / Client status / Human Review public protocol | RFC-004 | 只产生稳定内部 Application / Runtime Error |
| Source / Retrieval / permission and version filtering / Evidence Package | RFC-005 | 只消费已授权 Evidence Package，不扩大 Source Scope |
| Logs / Traces / Metrics / alerts / final operational thresholds | RFC-007 | 只定义允许产生的 Model Call metadata 与 error fields |
| Module / Port / DI | RFC-001 | 遵守既有边界，不重新设计仓库结构 |
| Transaction / persistence / Secret classification | RFC-002 | 外部调用不跨事务，遵守持久化和 Secret 边界 |

## Official Evidence Snapshot（2026-08-06）

这些链接证明候选能力在策划日存在，不构成长期兼容保证；实施时仍须复核官方文档、锁文件与最小兼容证据。

- OpenAI：[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)、[GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)、[Error Codes](https://developers.openai.com/api/docs/guides/error-codes)、[Cancel Response](https://developers.openai.com/api/reference/python/resources/responses/methods/cancel)、[Official Python SDK](https://github.com/openai/openai-python)、[Data Controls](https://developers.openai.com/api/docs/guides/your-data)、[Production Best Practices](https://developers.openai.com/api/docs/guides/production-best-practices)、[Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- Anthropic：[Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)、[API Errors](https://platform.claude.com/docs/en/api/errors)、[API and Data Retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- Google：[Structured Outputs](https://ai.google.dev/gemini-api/docs/structured-output)、[API Versions](https://ai.google.dev/gemini-api/docs/api-versions)、[Model Version Patterns](https://ai.google.dev/gemini-api/docs/models)

## Acceptance and Authorization Boundary

每组 DQ 需要用户明确接受后才能归档为 Accepted Decision。全部 DQ 闭合后仍须执行 RFC-006 Final Consistency Review，并由用户另行明确接受 RFC-006 整体。

即使 RFC-006 整体被接受，也只代表架构决策成立；以下事项仍保持未授权，直到完整策划包展示并且用户明确批准“进入 Goal 执行阶段”：

- 安装或升级 Provider SDK；
- 读取真实 Provider Secret；
- 调用真实模型或执行 Live Smoke；
- 编写 Model Runtime、Provider Adapter、业务 Prompt 或 Prompt Registry；
- 执行 Technical Spike、TS-01～TS-05 或业务实现；
- 创建或激活实际长期 Goal。
