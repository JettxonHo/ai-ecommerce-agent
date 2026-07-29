# Spike-001 — Limitations（局限性）

> **Status: S6 — FINAL**
> 这些是 Spike 的固有边界；它们**不**削弱已验证的架构行为，但界定了结论的适用范围。

## 范围边界（重要）

1. **不是 MVP / 不是生产实现**：Spike 验证**架构运行时行为**，不验证业务输出质量、不验证最终 Prompt、不验证四个核心 Skill 的生产逻辑。
2. **临时技术栈**：所有技术选择（SQLite / SqliteSaver / 同步 invoke / Scripted Model / Mock Retrieval / 本地 JSONL）均为**临时**，**不构成生产承诺**。生产后端语言 / 数据库 / Checkpointer / ORM / LLM / Retrieval / Observability / 部署平台仍待后续 RFC。
3. **Mock / Scripted**：模型输出是脚本化的、检索是内存 Mock。真实模型的非确定性、长上下文、成本与延迟**未**在本 Spike 验证。可选 Real Model Smoke Test 未启用（无 Secret，自动 Skip）。
4. **单线程 / 单进程**：同步 `invoke`、单 SQLite 连接。**未**验证并发、多任务锁、分布式 Checkpoint、多副本一致性。
5. **规模**：数据量为最小样本。**未**验证大规模下的性能、索引、检索召回质量、Checkpoint 体积增长。
6. **持久化介质**：Checkpoint 用本地 SQLite。生产若换 Postgres/Redis 等 Checkpointer，需重新验证 Safe Resume 与序列化兼容性。

## 已验证 vs 未验证

- **已验证（行为级）**：StateGraph 编译/同步 invoke、Interrupt/Resume、三类存储分离、原子提交回滚、幂等提交、有界重试、Stale Review 拒绝、Stale Checkpoint 防推进、检索降级不伪造、取消无部分写入、失败恢复不重复、Trace 关联、场景可复现。
- **未验证**：真实 LLM 行为、真实检索质量、并发与分布式、性能与规模、安全与权限在生产环境的实现、正式 Schema、UI、平台 Adapter 实际映射。

## 对 Readiness 的含义

- Spike 通过 **≠** Architecture READY。`Merge PR ≠ READY`、`Issue Closed ≠ READY`、`Claude Recommendation ≠ READY`。
- 进入 READY 仍需：Spike 证据 + Readiness Review + **用户明确确认**三者同时满足；并补足「未验证」清单中影响生产的关键 RFC（见 `spike-report.md` 的 Required RFC List）。
