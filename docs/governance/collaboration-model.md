# Collaboration Model（协作模型）

本文件定义 AI Ecommerce Agent 项目中各协作者的角色、模型、权限与交接方式。这是治理层的基础约束，所有策划、归档、Review 与实现行为都必须符合本模型。

---

## 1. 角色与职责

### 1.1 用户（项目所有者 / 最终决策人）

- 接受、修改、否决或暂缓决定。
- 是唯一能把 Proposed Decision 升级为 Accepted Decision 的一方。
- 是唯一能接受 RFC、重大技术 / 产品 Proposal 与范围变化的一方；已通过 DEC-072 提供全部 Gate 闭合后的长期 Goal 持续执行授权。
- 批准破坏性操作、重大架构变更、数据迁移、不可逆外部操作和最终发布条件。

### 1.2 主控与审阅 Agent（GPT-5.6 Sol / `xhigh` / `ORCHESTRATOR_REVIEWER`）

- 主持产品和架构讨论，提供 2～3 个有意义的方案、权衡与推荐。
- 负责 RFC、Goal、里程碑、复杂任务拆分、依赖 / 并行判断、风险、复杂诊断和任务合同。
- 路由实现任务，并检查实际 Diff、测试、文档同步和回归风险，完成 PR / 阶段 / Goal Review。
- 将未确认内容保持为 Proposal、Assumption 或 Open Question，不替用户接受 Decision / RFC。
- 校验强度遵守 [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md)，不建设泛化过度防御。
- 原则上不承担普通实现；只在 DEC-043 列出的复杂、阻塞、原型或实现 Agent 不可用等例外下直接修改代码，并交由独立 Agent 或人工最终审查。实现路由不可用时不得把该例外当作静默降级。

### 1.3 代码实现 Agent（自定义 Agent `luna-worker` / GPT-5.6 Luna / `max` / `IMPLEMENTER`）

- 仅在规格冻结、Goal 被用户激活且 Issue 可独立验收后介入。
- 按 Accepted Decision、RFC、Spec、Issue 和任务合同实现；不得临场更换框架、数据库、Provider、公共契约或验收标准。
- 执行必要的静态检查、单元 / 集成 / E2E 测试与构建，记录失败、限制、风险和回滚方式。
- 创建并更新 PR，根据 Sol Review 修复后重新运行验证。
- 不得为了完成任务降低验收标准或扩大产品范围。
- 需求不明、文档冲突、范围扩大、跨模块失败、公共接口 / 重大依赖 / 数据迁移或产品取舍时，暂停受影响工作并升级给 Sol；可以继续不受影响的独立任务。
- 不得最终批准或合并自己实现的 PR。
- 创建线程时必须请求准确名称 `luna-worker`，不得把逻辑角色“Luna Max”或单独模型字符串当作 Agent 名称。

### 1.4 辅助 Agent（GPT-5.6 Terra / `xhigh` / `AUXILIARY_IMPLEMENTER`）

- 只有用户对具体任务明确许可时，才可执行代码库调查、文件 / 符号定位、测试、文档整理、独立分析、边界明确的实现、Bug 初步定位、类型 / 构建修复、测试补充或初步 Review。
- 不作为 `luna-worker` 不可用时的自动或默认实现回退；Issue、任务合同和 PR 必须记录实际模型，不得把 Terra 成果标记为 Luna 完成。
- 不替代 Sol 作产品 / 核心架构决定、高风险拆分、跨模块裁决、最终 PR 批准或 Goal 验收。
- 用户明确许可的替代路由也不得改变范围、测试、Review 独立性、验收标准或人工 Gate。

### 1.5 文档与 Git 操作者

- 准确归档讨论、提案、决定、证据与进度，区分所有内容类型。
- 在授权范围内创建或整理 Issue、Branch、Commit、PR 与 Review 修复。
- 普通低风险 PR 在验收和 Required Checks 全部通过后可自主合并；高风险事项必须停在用户 Gate。
- 每次归档后执行检查清单并输出 Archive Result。

### 1.6 模型路由与可用性

禁止静默替换和错误归因。实现任务必须请求准确的自定义 Agent 名称 `luna-worker`，并在创建前记录逻辑角色、配置路径、配置模型、推理强度、实际运行时模型可见性与验证状态。配置已验证但运行时实例模型未暴露时只记 `CONFIG_VERIFIED`；Agent 自述不能成为 `RUNTIME_VERIFIED`。若当前会话无法发现 `luna-worker`，必须输出 `STATUS: BLOCKED_LUNA_WORKER_UNAVAILABLE`、停止新的实现任务并报告上下文；不得自动回退 Terra。Sol 直接实现只适用于 DEC-043 保留的例外，并必须更换最终 Reviewer。详细迁移、身份与失败协议见 DEC-071 / 072。

---

## 2. 策划与 Decision 流

```
[Sol/xhigh 讨论与方案]
        │
        ▼
[文档归档]
   ├─ 追加到当前 Session（保留历史、被否决方案、开放问题）
   ├─ Proposed Decisions → 记入 Session，状态保持 Proposed
   ├─ 重大议题 → 创建 / 更新 Draft RFC（按需）
   ├─ 用户确认的部分 → 创建/更新 DEC、更新 decision-log、Session 标记 Accepted
   ├─ 已接受决定 → 同步 Current Truth Layer
   ├─ 冲突 → 按文档优先级裁决
   └─ 输出 Archive Result
        │
        ▼
[用户审阅 Decision / RFC / Archive Result]
        │  接受 / 修改 / 否决
        ▼
[下一轮策划 或 Readiness Review]
```

---

## 3. Goal 激活后的 Issue / PR 流

```text
Accepted Goal and authoritative docs
↓
Sol/xhigh creates bounded Issue + task contract + dependency/file boundaries
↓
Sol records model verification and creates exact custom Agent `luna-worker`
↓
Implementer self-check + Required Checks + deterministic tests
↓
Sol/xhigh reviews actual diff, tests and documentation
↓
Implementer fixes and reruns checks
↓
ordinary low-risk PR: Sol or another non-implementer merges and closes
high-risk trigger: stop and request user decision
```

自主合并不改变 Decision / RFC 状态，也不能替代 Goal 激活、范围批准和最终发布 Gate。

---

## 4. 边界与禁止

- ChatGPT 的「建议」「推荐」「Proposed Decision」**不等于**用户决定。
- 仅有用户的明确批准语义（同意 / 确认 / 接受 / 就按这个方案 / 该决策通过 / 其他语义明确的批准）才能标记 Accepted。
- Agent 不得为了让文档看起来完整而补充未经讨论的事实。
- Agent 不得静默删除、覆盖或改写历史决策；改变旧决定时必须保留追踪关系。
- 在所有重大 Proposal、策划包与 Readiness Gate 被接受前，不得编写业务实现代码或执行新的 Technical Spike；闭合后按 DEC-072 持续执行 Accepted Goal。
- 实现路由必须按 DEC-071 使用 `luna-worker`；未经用户明确许可不得自动或默认改用 Terra，也不得静默替换、错误归因或降低质量要求。
- 实现 Agent 不得最终批准或合并自己的 PR；Sol 实现时必须更换独立 Reviewer。
- 不得隐藏失败测试、已知缺陷或未解决风险。
- 不得为低概率 Case 堆叠防御、机械 Rubric 或非重大核心风险引入哈希要求。

---

## 5. 持久化交接与线程隔离

- Sol 主控线程维护全局策划、调度、Review 和最终验收。
- 每个实现线程原则上只处理一个 Issue；并行任务必须先冻结接口、依赖、文件或模块所有权。
- 线程之间不假设自动共享上下文。持久化交接载体包括：项目文档、AGENTS、权威 Goal、GitHub Issue、任务合同、Git 分支 / Commit、PR、Review、Implementation Readiness / Current Status、Decision Log、测试与构建记录。
- 仓库继续使用现有权威路径，不为相同事实新建重复的根级 `GOAL.md`、`docs/current-status.md` 或 `docs/decision-log.md`；长期 Goal、当前状态和决定分别写入 `docs/goals/`、`docs/handoffs/implementation-readiness.md` 和 `docs/decisions/decision-log.md`。
- 聊天记录不是项目事实的唯一来源；任何影响后续执行的信息必须进入上述持久化载体。

### 标准任务合同

任务合同至少包含：模型与逻辑角色、Issue / 目标 / 交付物、权威文档与阅读顺序、In Scope / Non-goals、依赖与允许修改边界、冻结接口 / 状态 / 数据 / 错误契约、验收与测试、风险 / 停止 / 升级条件、PR / 文档 / 回滚要求、独立 Reviewer 与合并权限。

---

## 6. 相关文档

- [product-design-protocol.md](product-design-protocol.md) — 完整设计与决策协议
- [documentation-rules.md](documentation-rules.md) — 文档规则与内容类型
- [../../AGENTS.md](../../AGENTS.md) — 协作者入口规范
- [../decisions/dec-039-proportional-validation-and-review-governance.md](../decisions/dec-039-proportional-validation-and-review-governance.md) — 适度校验
- [../decisions/dec-040-autonomous-agent-execution-and-model-roles.md](../decisions/dec-040-autonomous-agent-execution-and-model-roles.md) — 自主权限与模型角色
- [../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md) — 演示 MVP 包络
- [../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md](../decisions/dec-042-evidence-driven-launch-strategy-workbench-positioning-and-demo-success.md) — 产品定位与演示成功边界
- [../decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md](../decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md) — 多 Agent 开发编排与任务合同
- [../decisions/dec-071-luna-worker-exclusive-implementation-routing.md](../decisions/dec-071-luna-worker-exclusive-implementation-routing.md) — `luna-worker` 专属实现路由与迁移协议
- [../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md](../decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md) — 长期自主开发授权、模型状态与人工 Gate
- [../handoffs/agent-model-routing-migration-2026-08-08.md](../handoffs/agent-model-routing-migration-2026-08-08.md) — 本次迁移审计报告
