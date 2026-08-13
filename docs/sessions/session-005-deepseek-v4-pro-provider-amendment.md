# Session-005：MVP-0 FL-2 DeepSeek V4 Pro Provider Amendment

## Metadata

- Status: Concluded
- Date: 2026-08-13
- Topic: Qwen Token Plan 条款阻断、OpenAI Gate 取代与 DeepSeek 官方 API 合同
- Related Decisions: [DEC-052](../decisions/dec-052-openai-responses-narrow-model-runtime-port-and-structured-output-authority.md), [DEC-053](../decisions/dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md), [DEC-054](../decisions/dec-054-adapter-secret-payload-boundary-and-deterministic-model-verification.md), [DEC-078](../decisions/dec-078-mvp0-fast-lane-execution-rebaseline.md), [DEC-079](../decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md)
- Related Issues: [#255](https://github.com/JettxonHo/ai-ecommerce-agent/issues/255), [#264](https://github.com/JettxonHo/ai-ecommerce-agent/issues/264), [#268](https://github.com/JettxonHo/ai-ecommerce-agent/issues/268)

## Context

OpenAI FL-2 adapter 与 smoke seam 已离线完成，但操作者无法提供 `OPENAI_API_KEY`。用户曾批准 Qwen 补充验证，PR #266 合并了 Token Plan adapter；在真实调用前，独立接管审计发现 Token Plan 个人版禁止自动化脚本和自定义应用后端，因而立即冻结 live。

用户提出改用不支持多模态的 `deepseek-v4-pro`。当前 Fast Lane 本来只接受粘贴文本、TXT 与 Markdown，因此多模态缺失不影响当前 Goal。主开发任务提出“DeepSeek 官方 API，而不是百炼托管”的单一关键选择，用户随后明确回复确认建立变更合同。

## Goal

在不调用 Provider、不读取 Secret、不产生费用的前提下，把用户确认的 DeepSeek 官方 Provider 方向转化为可实现、可审阅且与旧 Decision 有明确追踪关系的 FL-2 合同。

## Non-goals

- 不实现 adapter、composition 或 live smoke；
- 不注入 Secret、充值或发起 Provider 请求；
- 不增加多模态、OCR、PDF、Retrieval、Provider router 或 fallback；
- 不在 FL-2 terminal result 前清理已合并的 Qwen / OpenAI 代码。

## Discussion

### Facts

- `main@1469eefe6db75ceee949b2c7431df5ac06a25f40` 包含 PR #266 的离线 Qwen adapter；没有 Qwen、DeepSeek 或 OpenAI live call。
- DeepSeek 官方文档当前列出 `https://api.deepseek.com`、`deepseek-v4-pro`、Chat Completions、JSON Output、Thinking Mode 与 `reasoning_effort=high`。
- DeepSeek JSON Output 使用 `json_object`，不是 strict JSON Schema；官方提示可能偶发空内容。
- DeepSeek 隐私政策适用于 API，输入可能被收集并在中华人民共和国处理/存储；当前没有与 OpenAI `store=false` 等价的已验证短期保留承诺。
- Qwen Token Plan live 与套餐使用条款冲突，模型本身可用不能消除该冲突。
- PR #266 的 Qwen request 使用当前官方 Chat Completions 文档未明确支持的 strict `json_schema`，且 Profile reasoning effort 未发送；其绿色离线测试不能作为 Provider runtime proof。

### Accepted Decision

用户确认使用 DeepSeek 官方 API。DEC-079 将该方向冻结为单一 DeepSeek FL-2 Gate，保留项目 Port、确定性五阶段、本地 Schema / Domain Validator、Secret/payload 隔离与一次人工付费 smoke。

### Alternatives

1. 继续等待 OpenAI Secret；
2. 用 Token Plan 个人版运行 Qwen 或 DeepSeek 后端 smoke；
3. 改用百炼普通按量；
4. 直接使用 DeepSeek 官方 API。

### Trade-offs

- 方案 1 不引入变更，但无法闭合用户当前可用的 Provider 路径。
- 方案 2 与官方套餐条款冲突。
- 方案 3 引入用户未选择的计费与 Base URL 边界。
- 方案 4 与用户选择一致并可复用 OpenAI-compatible SDK，但 strict Schema 降为 JSON Mode，必须依赖本地权威校验。

### Risks

- JSON Mode 的空/非法或 schema-invalid 输出会使一次五调用 smoke 直接失败；不以自动付费修复隐藏风险。
- DeepSeek 数据处理边界不同于 OpenAI；首次 live 只允许虚构 Anchor SKU。
- 已合并的 Qwen code 可能成为 legacy，但提前回退会违反已接受 cleanup sequencing。

## Documentation Updates

- 新增 DEC-079；
- 给 DEC-052 / 053 / 054、DEC-078 与 RFC-006 添加显式 amendment notice；
- 更新 Fast Lane Goal、AGENTS、README、Testing Strategy 与 Implementation Readiness；
- 冻结 OpenAI / Qwen 旧 live handoff；
- 更新 Decision Log 与 Session index。

## Synchronization Checklist

- [x] Fact、Alternative、Trade-off、Risk 与用户接受语义已分开记录
- [x] 新决定使用 `Amends` 关系，不删除旧 Decision / RFC 正文
- [x] 当前 Goal 与入口文档不再把 OpenAI 描述为待完成 Gate
- [x] Qwen live 明确记录为 `BLOCKED_BY_PROVIDER_TERMS`
- [x] 未创建业务实现代码、未读取 Secret、未调用 Provider
