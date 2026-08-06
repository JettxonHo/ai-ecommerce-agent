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

首个演示 MVP 已确定使用一个真实 LLM Provider 与一个确定性测试替身，但生产 Provider、模型、SDK、项目内 Model Runtime Port、Structured Output、错误修复、版本记录、Secret 和 Live Smoke 边界尚未冻结。若把这些选择留给单个实现 Issue 临场决定，四个 Core Skills 会直接耦合厂商 SDK，并可能把 Provider 输出、业务 Validator、Workflow Retry 和 Current Truth 写入混成同一职责。

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
| DQ-01 Provider / Model / SDK Capability Baseline | P-28 | PROPOSED |
| DQ-02 Model Runtime Port, DI and Configuration | P-29 | PROPOSED |
| DQ-03 Structured Output Contract and Schema Authority | P-30 | PROPOSED |
| DQ-04 Provider Failure, Repair, Retry, Cancellation and Call Identity | P-31 | NOT YET PROPOSED |
| DQ-05 Prompt / Model / Schema / Execution Configuration Versioning | P-32 | NOT YET PROPOSED |
| DQ-06 Skill-specific Invocation Profiles and Context Assembly | P-33 | NOT YET PROPOSED |
| DQ-07 Secret, Provider Payload, Persistence and Telemetry Boundary | P-34 | NOT YET PROPOSED |
| DQ-08 Deterministic Substitute, Contract Tests and Live Smoke | P-35 | NOT YET PROPOSED |

未获得用户明确接受前，任何推荐方案都只是 Proposed Decision，不得写入 Current Truth 或实现。

## Proposed Decision Round 1

### P-28：Provider / Model / SDK Capability Baseline

#### P-28A（推荐）：OpenAI Responses API + GPT-5.6 Terra + 官方 Python SDK

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

P-28A 是基于当前官方能力说明与项目已接受架构边界作出的**适配度推断**：OpenAI Responses API 已同时提供本 RFC 需要的结构化输出、refusal / incomplete、usage metadata 和 Python 支持，因此预计额外协议适配最少；这不是三家模型质量 Benchmark 的结论。三案的账号可用性、固定验收包质量、实际延迟和成本证据均尚未执行，必须在实施前置兼容检查与 Release Candidate Smoke 中验证。推荐不等于接受；本 RFC 不授权安装 SDK、读取 Secret 或调用模型。

### P-29：Model Runtime Port, DI and Configuration

#### P-29A（推荐）：项目自有窄型同步 Port + 单一已接受 Provider Adapter

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

#### P-30A（推荐）：Provider-native Strict Schema + 项目 Schema + Domain Validator

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

## Remaining Decision Questions

### DQ-04 — P-31：Provider Failure, Repair, Retry, Cancellation and Call Identity

待决定 Provider error taxonomy、refusal / incomplete / invalid output、transient retry 与 structured repair / regeneration 的分离、调用 Deadline、取消传播、Provider Call Identity、commit-unknown 处理和有界上限。RFC-003 拥有总体 Workflow Retry / Rerun / Cancellation；RFC-006 不得自行触发业务 Rerun。

### DQ-05 — P-32：Prompt / Model / Schema / Execution Configuration Versioning

待决定 Prompt Template、Model ID、Provider API、Output Schema、Skill Contract、Validator 与 Execution Profile 的版本身份、兼容性、运行记录、变更发布和回归触发条件。身份机制保持算法中立，不引入 Hash / SHA-256 要求。

### DQ-06 — P-33：Skill-specific Invocation Profiles and Context Assembly

待决定四个 Skills 与 Adapter 的命名 Profile、Reasoning / Token / Output 上限、Evidence Package 装配、上下文裁剪、工具权限和 Stage 间差异。Provider 不得决定 Retrieval Scope、权限、流程路由或 Current Truth。

### DQ-07 — P-34：Secret, Provider Payload, Persistence and Telemetry Boundary

待决定 Credential Reference、运行时 Secret Resolution、Prompt / Response / Diagnostic 数据分类、最小持久化、Provider `store` 控制、Redaction 和允许交给 RFC-007 的 Metadata。不得默认把完整 Prompt / Response 写入日志或 Trace。

### DQ-08 — P-35：Deterministic Substitute, Contract Tests and Live Smoke

待决定同 Port 的 Scripted Fake、错误脚本、Schema / refusal / incomplete / repair 场景、网络隔离、固定资料包、Release Candidate 一次 Live Smoke、人工验收证据和停止条件。Spike-001 只可作为测试设计证据，禁止迁移其生产代码。

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

- OpenAI：[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)、[GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)、[Error Codes](https://developers.openai.com/api/docs/guides/error-codes)、[Data Controls](https://developers.openai.com/api/docs/guides/your-data)
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
