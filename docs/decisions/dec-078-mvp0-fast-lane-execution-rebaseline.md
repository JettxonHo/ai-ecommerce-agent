# DEC-078：采用 MVP-0 Fast Lane 执行重基线

## Status

Accepted

## Date

2026-08-12

## Type

Product Delivery / Goal / Testing / Review Governance

## Context

MVP-0 已积累大量 Foundation、持久化、Runtime、Contract、Output Schema、Web 与测试基础，但尚未形成浏览器到真实后端再到 Brief 导出的完整用户闭环。

当前仓库还存在三个直接拖慢交付的问题：

1. 剩余工作继续按 M1～M8 横向补齐基础设施，而不是围绕一个用户任务纵向完成；
2. 后端测试规模已显著超过生产代码，部分私有模块使用大量 AST、精确文件清单、类型变体和递归 Schema 组合证明内部结构；
3. README、旧 Goal 与 Readiness 已落后于实际合并状态，Agent 需要反复协调过期计划和真实代码。

这些做法已偏离 [DEC-001](dec-001-business-value-before-agent-complexity.md) 的业务价值优先原则和 [DEC-039](dec-039-proportional-validation-and-review-governance.md) 的适度校验要求。

用户于 2026-08-12 明确选择“方案 B：MVP Fast Lane”，确认先精简规划文档、生成新的 Goal，再让 Agent 从最新 `main` 重新按纵向闭环执行；随后明确接受 [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md) 的详细条款。

## Decision

### 1. 激活 Fast Lane Goal

[MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md) 在承载本决定的文档 PR 合并后成为剩余 MVP-0 的唯一 Active Goal。

原 [端到端演示 MVP-0 Goal](../goals/end-to-end-demo-mvp0-goal.md) 保留为历史执行记录，其未完成的 M1～M8 横向 Backlog 不再自动产生新 Issue。

本决定 amends DEC-075 对剩余 MVP-0 的执行计划、测试与 Readiness；不撤销已经完成的工作，也不删除历史 RFC、DEC、Session 或代码。

### 2. 冻结最小用户闭环

Fast Lane 只需交付：

1. 创建 Task；
2. 提交一份粘贴文本或 UTF-8 TXT / Markdown 资料，最大 1 MiB；
3. 使用确定性流程完成 Facts → Insight → Positioning → Marketing Brief → Xiaohongshu Brief；
4. 完成一次查看、有限修改与确认；
5. 导出当前结果为 UTF-8 Markdown；
6. 确定性闭环通过后执行一次真实 OpenAI happy-path smoke。

第一阶段采用单进程纵向实现。现有 PostgreSQL、Model Runtime、Output Contract、generated client、Web route 和 Markdown renderer 在能减少工作时直接复用；不得为了完整旧设计而先补齐没有当前消费者的基础设施。

### 3. 延后高级能力

下列能力后移 MVP-1 或后续独立 Goal：

- JSON / CSV / PDF / 图片 / OCR 和任意办公文件输入；
- Embedding、Semantic / Hybrid Retrieval、RRF、完整 EvidencePackage / DatasetStatistic；
- Multi-worker Lease / Heartbeat / Fencing、完整 Durable Dispatch 与分布式 Commit Fence；
- Durable Checkpoint Recovery、七动作 Reconciliation、完整 Cancel / Resume / Partial Rerun；
- Source replace/remove preview-confirm 与永久删除；
- Review Autosave / Diff / stale recovery / 多 Outcome；
- Brief comparison、完整版本历史和未被 Fast Lane UI 消费的公共 API；
- Login、RBAC、多租户、公网部署、通用合规、Telemetry 或 Performance 平台。

相关 Accepted Decision 作为未来设计继续有效，但不再是本 Goal 的实现前置或完成条件。恢复任一延期能力必须说明当前 Fast Lane 消费者和收益；不得以“旧 Backlog 尚未完成”为唯一理由。

### 4. 收敛测试与 Review

- 每个实现 PR 优先证明用户可见行为或真实外部边界，只要求代表性正常路径、主要可恢复错误和关键不变量。
- 不再为每个私有模块增加 AST Scanner、精确目录清单、sole-consumer、exact builtin subclass 或递归 every-field 组合测试。
- Architecture 测试集中到公共边界和少量仓库级规则；既有过度测试不要求在本 Goal 内清理，除非它阻塞纵向开发。
- 本地运行受影响测试和静态检查；全局回归由 CI 兜底。Required Checks 的去重通过独立低风险 CI 变更完成，不用直接关闭 Gate 规避失败。
- 所有 PR 审查 Correctness、Readability 与 Architecture；Security / Performance 只在变更相关时审查。
- Re-review 聚焦原 Finding 和其回归面，不继续扩张新的低风险防御变体。
- PR 描述保留 Problem、Scope、Evidence、Risk 和 Rollback intent；精确 SHA 链、反向 Commit inventory、重复模型状态口号和人工 LOC 算术不再是接受条件。

### 5. 保留真实安全边界

Fast Lane 继续强制：外部输入边界、Task / fixed-workspace scope、参数化 SQL、用户可见结果的原子提交、React / Markdown 安全投影、loopback same-origin、mutation 幂等、Secret / provider payload / traceback 隔离、安全错误，以及适度依赖和 Secret 扫描。

本地固定工作区不建设 Login、Token、RBAC、Tenant 或公网攻击面矩阵。

### 6. 改为纵向 Issue

FL-1 原则上不超过三个实现 Issue：

1. Input + real backend routes；
2. deterministic pipeline + current results；
3. review + Brief views + Markdown export。

每个 Issue 必须带真实消费者。没有同一纵向或紧邻下一纵向消费者的 DTO、Protocol、Facade、Repository 或 Output Contract 不得作为独立交付物。

## Consequences

### Positive

- 将开发资源集中到第一个用户可用闭环；
- 减少规划读取、测试编写、Review 往返和 PR 元数据维护；
- 保留已实现资产和真实安全边界，不进行昂贵重写；
- 通过一次确定性 E2E 和一次真实 Provider Smoke 得到更强的产品证据。

### Trade-offs

- 第一版不证明完整分布式恢复、检索、版本和高级审核能力；
- 部分既有架构在 MVP-0 内保持未消费或冻结状态；
- 后续恢复高级能力时仍需重新验证其真实消费者和成本收益。

## Amendments and relationships

- **Amends:** DEC-075 对剩余 MVP-0 的 Goal、Testing 和 Readiness 执行方式。
- **Applies DEC-039:** 将适度校验从原则变成 Fast Lane 的具体 Issue / Test / Review 约束。
- **Defers implementation, does not revoke design:** DEC-050 / 051、DEC-056 的高级交互部分、DEC-063～070 中未被 Fast Lane 消费的 Runtime / API / Retrieval 能力。
- **Preserves:** DEC-001 / 003 / 004 / 011 / 020 / 048 / 052 / 055 / 062 / 065 / 071 / 072 的核心产品、技术栈、安全与 Agent 路由边界。

## Related

- [Session-004](../sessions/session-004-mvp0-fast-lane-rebaseline.md)
- [MVP-0 Fast Lane Goal](../goals/mvp0-fast-lane-goal.md)
- [Implementation Readiness](../handoffs/implementation-readiness.md)
- [Testing Strategy](../development/testing-strategy.md)

## Activation record

本决定与 Fast Lane Goal 的详细范围由用户于 2026-08-12 明确确认。承载本决定的文档 PR 合并后，Fast Lane Goal 激活；业务实现仍从独立 FL-1 Issue 开始。
