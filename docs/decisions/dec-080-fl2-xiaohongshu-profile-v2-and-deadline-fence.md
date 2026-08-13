# DEC-080：FL-2 小红书 Profile v2 与同步调用 Deadline Fence

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-13
- **Decision Type:** LLM Runtime / Execution Profile / Deadline / Release Evidence
- **Source:** 用户明确回复 `APPROVE BOUNDED FL-2 REPAIR`
- **Issue:** [#277](https://github.com/JettxonHo/ai-ecommerce-agent/issues/277)
- **Amends:** [DEC-079](dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md) 的 Xiaohongshu execution profile
- **Applies:** [DEC-053](dec-053-bounded-model-recovery-readable-versioning-and-deterministic-skill-profiles.md) 的可读 Version Tuple 与调用返回后检查

## Context

唯一一次获授权的 DeepSeek smoke 在 exact reviewed `main@1c7c2107ead332235d492ed063b67101784d35f1` 上执行了一个虚构 Task 的五次初始调用，`retry_count=0`、`recovery_count=0`，随后在进入 `awaiting_review` 前安全失败。第五个 Xiaohongshu call 记录的 output token 数恰好为旧 Profile 上限 12,288，latency 为 136,622 ms，而旧 timeout 为 120 s。

Sanitized evidence 没有保存 raw finish reason 或错误类别，因此上述值只能证明旧 token/time 边界同时被触及，不能证明唯一根因。项目不得读取或保留 raw Provider material 来补做诊断，也不得把这次结果写成 live success。

DeepSeek 官方 Chat Completions 契约把 `max_tokens` 定义为最大生成 token 数；`finish_reason=length` 表示达到请求上限，JSON Output 文档也要求设置足够的 token 上限以避免 JSON 被截断。当前项目使用同步 SDK 调用，不能诚实宣称在任意时刻强制取消已经进入 SDK 的 in-flight 调用，但可以在调用前和调用返回后执行 application deadline fence，并拒绝接纳迟到结果。

## Decision

### 1. 只新增 Xiaohongshu execution profile v2

保留 `xiaohongshu_mapping_v1` 作为稳定 Profile ID，把它的可读 execution profile version 从 `v1` 提升为 `v2`：

| Field | Historical `v1` | Accepted `v2` |
|---|---:|---:|
| `max_tokens` | 12,288 | 16,384 |
| timeout | 120 s | 240 s |
| reasoning effort | `high` | `high` |

16,384 与 240 s 都已存在于当前五阶段 Catalog，不引入新的仓库级最大量级。其他四个 DeepSeek Profile 及其版本、token 和 timeout 完全不变。

Coordinator 必须显式请求 `xiaohongshu_mapping_v1 / v2`，并把 `v2` 写入 Provider-neutral Version Tuple。实现不得把传入的 `v1` 静默解释为新参数，也不得继续记录 `v1` 却发送 16,384 / 240 s。

### 2. 同步调用增加返回后 Deadline Fence

DeepSeek 单次同步调用采用以下固定顺序：

1. 调用前检查 application deadline；
2. 将 `min(profile timeout, remaining deadline)` 传给 SDK；
3. SDK 返回后立即再次读取单调时钟；
4. 如果 deadline 已过，删除/丢弃 response，不执行 response mapping、Schema/Domain validation 或 Candidate admission，并返回固定安全的 Provider-neutral transient failure；
5. 保持 `max_retries=0`，不自动发起第二次 Provider call。

该 fence 约束项目是否接纳返回值，但不宣称 force-cancel 已经进入同步 SDK 的 in-flight 网络调用。不得为了制造硬取消语义引入 thread、process、async runtime 或第二 client。

### 3. 其余 Provider 与产品合同保持冻结

本决定不改变：

- `https://api.deepseek.com`、`deepseek-v4-pro`、Chat Completions、JSON Mode、enabled thinking 与五阶段 `reasoning_effort=high`；
- 本地 JSON Schema / Pydantic / Skill Domain Validator 权威；
- 一个 Task / 五个初始 calls、零 SDK retry、零项目 retry / repair / regeneration；
- Prompt、Schema、Domain admission、evidence schema、token-usage contract、Secret/payload/reasoning/traceback 隔离；
- 公共 HTTP/OpenAPI、数据库迁移、依赖/lockfile、Qwen/OpenAI 历史代码或 [Issue #274](https://github.com/JettxonHo/ai-ecommerce-agent/issues/274) 的分类。

首次 live 结果继续为 `GOAL_BLOCKED`。Profile v2 的离线实现、CI 或合并都不等于 live verification。

## Alternatives Rejected

### 静默扩大 v1

DEC-053 已把 token、timeout 与 execution profile version 绑定。继续记录 `v1` 会让历史 Metadata 无法解释，因此拒绝。

### 只增加 token 或只增加 timeout

唯一 sanitized evidence 同时触及旧 token ceiling 和旧 time boundary，单边修改会留下同一条已观测边界。采用当前 Catalog 已存在的 16,384 / 240 s 是最小、可读且不新增量级的双边修复。

### 根据 raw response、reasoning 或 traceback 精确诊断

这会扩大已经接受的 Provider payload 与 evidence 禁止边界；当前修复不需要该材料，因此拒绝。

### 自动重试或立即运行第二次 smoke

这会扩大五次调用和付费 Gate。失败后的下一次真实调用仍必须获得用户新的明确授权。

## Consequences

- Xiaohongshu 阶段最多增加 4,096 个生成 token 的预算，timeout 上限增加 120 s；成本和等待时间上界因此可见增加。
- 迟到的同步 response 即使被 SDK 返回，也不能越过 application deadline 进入业务结果。
- 这次改动只提供更合理的可接受边界，不保证模型一定生成 schema/domain-valid 结果，也不把首次失败改写成成功。
- 如果离线实现通过，仍需 exact-head Required Checks、独立五轴 Review 和新的人工付费授权，才可执行至多一个 Task / 五次 calls 的第二次 smoke。

## Authorization Boundary

本决定合并后授权创建一个独立、tests-first 的离线实现 Issue，由准确名称的自定义 Agent `luna-worker` 在 fresh isolated clone 中实现。必须单独记录 `CONFIG_VERIFIED` 与运行时身份；不得静默回退 Terra。

本决定不授权读取/注入 Secret、Provider/PostgreSQL live action、账户充值、第二次 smoke、raw Provider material 检查或 [Issue #274](https://github.com/JettxonHo/ai-ecommerce-agent/issues/274) Phase B 写入。任何真实调用仍需实现 PR 在 exact head 上通过 Required Checks 与独立五轴 Review 后，再由用户单独明确授权。

## Official Evidence

- [DeepSeek Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)
- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/)
- [DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)
