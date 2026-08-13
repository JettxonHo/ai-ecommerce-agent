# DEC-079：MVP-0 FL-2 改用 DeepSeek V4 Pro 官方 API

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-13
- **Decision Type:** LLM Runtime / Provider Amendment / Structured Output / Release Evidence
- **Source:** [Session-005](../sessions/session-005-deepseek-v4-pro-provider-amendment.md)；用户明确确认使用 DeepSeek 官方 API
- **Issue:** [#268](https://github.com/JettxonHo/ai-ecommerce-agent/issues/268)
- **Amends:** [DEC-052](dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md)、[DEC-053](dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md)、[DEC-054](dec-054-adapter-secret-payload-boundary-and-deterministic-model-verification.md)、[DEC-078](dec-078-mvp0-fast-lane-execution-rebaseline.md) 与 [RFC-006](../rfcs/rfc-006-llm-runtime-and-structured-output.md) 的 MVP-0 Provider-specific 条款
- **Amended by:** [DEC-080](dec-080-fl2-xiaohongshu-profile-v2-and-deadline-fence.md) 只把 Xiaohongshu execution profile 提升为 `v2` 并增加同步调用返回后的 deadline fence；本文件的 `v1` 表保留为首次 live 的历史合同

## Context

Fast Lane 的确定性 Task → 五阶段流水线 → Review → Markdown 导出已实现，OpenAI Responses 离线 Runtime 与 opt-in smoke seam 也已合并，但操作者无法提供 `OPENAI_API_KEY`，因此 Issue #255 没有形成真实 Provider 证据。

补充 Qwen Token Plan adapter 已由 PR #266 合并且没有执行 live call。后续审计确认 Token Plan 个人版禁止把套餐用于自动化脚本或自定义应用后端，Issue #264 的 pytest / FastAPI / PostgreSQL smoke 因而与 Provider Terms 冲突；同时当前官方 Chat Completions 文档没有支撑该 adapter 发送的 strict `json_schema` 形状，且其 Profile reasoning effort 没有进入请求体。更换为同一 Token Plan 中的其他模型不能绕过条款或把离线实现变成 live evidence。

用户随后明确选择直接调用 DeepSeek 官方 API，而不是阿里云百炼托管的 DeepSeek。DeepSeek 当前官方文档明确列出：

- OpenAI-compatible Base URL `https://api.deepseek.com`；
- Model ID `deepseek-v4-pro`；
- synchronous Chat Completions；
- `thinking` toggle 与 `reasoning_effort=high`；
- JSON Output 的 `response_format={"type":"json_object"}`。

DeepSeek JSON Output 只保证合法 JSON，不提供项目此前使用的 Provider-native strict JSON Schema。项目 Schema / Pydantic projection 与 Skill Domain Validator 因此继续是不可削弱的结构和业务权威。

DeepSeek 隐私政策适用于 API，并说明可能收集输入、在中华人民共和国处理和存储个人信息，且没有为本调用承诺固定的短期保留上限。首个 live smoke 只能发送仓库内明确虚构的 Anchor SKU，不得发送真实用户、商家或敏感资料，也不得宣称 Zero Data Retention。

## Decision

### 1. 单一真实 Provider 改为 DeepSeek 官方 API

MVP-0 FL-2 的唯一真实 Provider proof 改为：

| Field | Frozen value |
|---|---|
| `provider_id` | `deepseek` |
| `api_family` | `chat_completions` |
| Base URL | `https://api.deepseek.com` |
| Model | `deepseek-v4-pro` |
| Credential reference | `deepseek_primary` |
| Process Secret | `DEEPSEEK_API_KEY` |
| SDK | 当前已锁定的官方 `openai==2.53.0` Python SDK；无已复现兼容问题时不升级 |
| Client retry | `max_retries=0` |
| Operation | synchronous, non-streaming `chat.completions.create` |
| Thinking | 显式 `extra_body={"thinking":{"type":"enabled"}}` |
| Reasoning effort | 五阶段全部显式 `high` |

DeepSeek adapter 继续位于项目自有同步 `ModelRuntimePort` 后方。Application、Domain、公共 HTTP / OpenAPI 和 Web 不得依赖 DeepSeek SDK-shaped 类型。不得增加 Provider Registry、运行时 model picker、fallback、failover、repair model 或第二个 live Provider。

现有 OpenAI 与 Qwen adapter 作为已实现历史能力冻结，不进入默认启动路径，也不再构成当前 FL-2 的 live Gate。

### 2. JSON Mode 后由项目执行权威校验

每次 DeepSeek 请求必须：

- 使用 `response_format={"type":"json_object"}`；
- 在指令中明确要求 JSON，并给出由当前项目 Schema 派生的确定性字段形状或示例，不改变字段语义；
- 使用 Chat Completions 的 `max_tokens` 映射现有 Profile output ceiling；
- 不发送 `type=json_schema`、`strict=true`、tools、functions、files、URLs、Web Search、MCP、conversation history、streaming 或 background execution；
- 将 Provider 返回值视为不可信输入，固定执行：单一 assistant content string → JSON parse → 项目 JSON Schema / Pydantic validation → Skill Domain Validator → Candidate admission；
- 对 empty content、malformed JSON、schema mismatch、unexpected response shape、domain-invalid candidate 或 Provider error 返回安全的 Provider-neutral failure。

原始 response、reasoning content、SDK object 与 traceback-sensitive 临时值不得逃逸 adapter 或进入日志、Problem、数据库、导出与 evidence。

### 3. 五个 DeepSeek Profile

现有 Profile ID / version、输出上限与 timeout 保持可读且固定；DeepSeek 不支持原来的 low / medium 差异化意图，因此五阶段全部显式使用 `high`：

| Stage | Profile / version | Effort | `max_tokens` | Timeout |
|---|---|---:|---:|---:|
| Product Intake | `product_intake_v1` / `v1` | high | 8192 | 120 s |
| Customer Insight | `customer_insight_v1` / `v1` | high | 12288 | 180 s |
| Product Positioning | `product_positioning_v1` / `v1` | high | 16384 | 240 s |
| Marketing Brief | `marketing_brief_v1` / `v1` | high | 16384 | 180 s |
| Xiaohongshu mapping | `xiaohongshu_mapping_v1` / `v1` | high | 12288 | 120 s |

每个阶段只有通过本地 Schema 和 Domain Validator 的结果才能进入下一阶段上下文。模型 alias 或实际 resolved model 变化必须进入可读 Version Tuple，并在新的受控 smoke 前重新审查。

### 4. 首次付费 Gate 严格为一个 Task、五次调用

DeepSeek RC smoke 只允许 `fixture-sufficient-v1` 的一个 Task 与按顺序发生的五个初始 Provider calls。对于这一次 live Gate：

- SDK retry 为零；
- 不执行项目 transport retry、model-assisted repair、regeneration 或第二模型调用；
- 任一 timeout、ambiguous transport failure、empty / invalid output、schema / domain failure、access / balance / model failure 都立即停止；
- 失败后如需再次调用，必须重新获得用户明确授权；
- 不自动充值，不运行第二 Task，不执行 live error / recovery / load / quality matrix。

DEC-053 的 Provider-neutral 有界 Recovery 设计继续作为历史和未来能力保留，但不授权在本次五调用 DeepSeek smoke 中消耗额外 Provider attempt。

### 5. Secret、资料和证据边界

- `DEEPSEEK_API_KEY` 只由 private adapter factory 从进程环境解析；缺失或空白时必须在 Client、PostgreSQL 和网络 I/O 前 fail-fast。
- 不加载 `.env`，不把 Secret 放入配置对象、GitHub、CI、源代码、数据库、日志、Trace、Fixture、evidence 或聊天。
- Live 只发送虚构 Anchor SKU 的受控文本、阶段指令、当前已验证的上游结果和 Schema-derived shape；不发送真实用户资料、整份 Workspace、无关 Source、原始数据库行或 evidence 文件。
- Evidence 使用操作者指定、tracked source 之外的新文件且不得覆盖旧 evidence；只记录 commit/timing/disposition、Provider/API/model、五个 call / attempt ID、安全 request / response ID、Version Tuple、token usage、latency、retry count（应为零）与行为 Gate。
- Evidence 不得包含 Secret、账户身份或余额、fixture 文本、prompt、context、raw response、reasoning content、Candidate、Markdown 内容或 traceback。

成功结果只标记为 **DeepSeek V4 Pro direct live verified**，不能标记为 OpenAI 或 Qwen proof。

### 6. Issue 与旧实现处置

- 本文档合并后，Issue #255 作为被本决定取代的 OpenAI live Gate 关闭；不得执行其旧 smoke 手册。
- Issue #264 记录 `BLOCKED_BY_PROVIDER_TERMS` 后关闭；不得运行 Token Plan live smoke。
- PR #266 的离线 Qwen adapter 不在本变更中回退或删除。它保持 frozen，待 FL-2 得出 terminal result 后由唯一 bounded legacy cleanup Issue 按真实消费者与依赖证据分类为 `retain`、`freeze for later` 或 `remove now`。
- 本文档 PR 关闭 Issue #268 的治理结果；DeepSeek adapter 与 smoke seam 使用后续独立实现 Issue、分支和 PR。

## Alternatives Rejected

### 继续等待 OpenAI Secret

这会保留技术现状但不能推进用户已明确改变的 Provider 方向，因此不再是当前 FL-2 Gate。已合并 OpenAI adapter 不删除。

### 使用 Qwen 或 DeepSeek Token Plan 个人版运行后端 smoke

套餐模型支持列表不能覆盖其禁止自动化脚本和自定义应用后端的使用条款，因此拒绝。

### 通过阿里云百炼普通按量或同时保留多个 live Provider

用户确认的是 DeepSeek 官方 API。百炼普通按量、Provider router、fallback 和比较矩阵会扩大计费、Secret 与验证面，均不进入本 Goal。

### 把 JSON Mode 当作 strict JSON Schema

官方只保证合法 JSON。跳过项目 Schema / Domain Validator 会削弱 Accepted Contract，因此拒绝。

## Consequences

### Positive

- FL-2 获得一个用户可提供凭证、官方文档已验证的直接 Provider 路径；
- Application-owned Port、确定性五阶段、Schema / Domain authority 与 Secret boundary 保持不变；
- 五次调用上限让首次付费验证的成本和外部副作用可审计；
- Qwen 条款冲突不会被模型可用性误导或静默绕过。

### Costs and Risks

- DeepSeek JSON Mode 可能返回空内容或不符合项目 Schema，首次失败将直接阻塞而不会付费修复；
- DeepSeek privacy / retention 不等同于 OpenAI `store=false`，因此当前 live 只能使用虚构 Fixture；
- 五阶段统一 `high` 可能增加延迟与 token 消耗，需要从一次 smoke 记录真实 evidence；
- Provider 价格和 model alias 会变化，live 前必须再次核对 access、balance、model 和 exact reviewed commit。

## Authorization Boundary

本文档合并后授权创建一个边界清晰的 DeepSeek 离线实现 Issue，并由准确名称的 `luna-worker` 在 fresh isolated clone 中实现和测试。配置证据与运行时身份必须分开记录；不得静默回退 Terra。

本文档不授权读取或注入 Secret、账户充值、Provider 调用或 live smoke。真实调用仍需 adapter PR 在 exact head 上通过 Required Checks 与 Sol 独立五轴 Review，然后由用户单独明确授权一次付费 smoke。

## Official Evidence

- [DeepSeek API first call and model IDs](https://api-docs.deepseek.com/)
- [DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)
- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/)
- [DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)
- [DeepSeek Privacy Policy](https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html)
- [DeepSeek Open Platform Terms](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html)
- [Alibaba Cloud Token Plan Personal terms and supported models](https://help.aliyun.com/zh/model-studio/token-plan-personal-overview)
- [Alibaba Cloud Token Plan unsupported tool types](https://help.aliyun.com/zh/model-studio/more-tools)
