# Collaboration Model（协作模型）

本文件定义 AI Ecommerce Agent 项目中各协作者的角色、模型、权限与交接方式。这是治理层的基础约束，所有策划、归档、Review 与实现行为都必须符合本模型。

---

## 1. 角色与职责

### 1.1 用户（项目所有者 / 最终决策人）

- 接受、修改、否决或暂缓决定。
- 是唯一能把 Proposed Decision 升级为 Accepted Decision 的一方。
- 是唯一能接受 RFC、批准范围变化与下达「进入 Goal 执行阶段」指令的一方。
- 批准破坏性操作、重大架构变更、数据迁移、不可逆外部操作和最终发布条件。

### 1.2 策划与审阅 Agent（GPT-5.6 Sol / `xhigh`）

- 主持产品和架构讨论，提供 2～3 个有意义的方案、权衡与推荐。
- 负责 RFC、复杂任务拆分、风险判断、复杂诊断和 PR / 阶段 / Goal Review。
- 将未确认内容保持为 Proposal、Assumption 或 Open Question，不替用户接受 Decision / RFC。
- 校验强度遵守 [DEC-039](../decisions/dec-039-proportional-validation-and-review-governance.md)，不建设泛化过度防御。

### 1.3 代码实现 Agent（GPT-5.6 Luna / `max`）

- 仅在规格冻结、Goal 被用户激活且 Issue 可独立验收后介入。
- 按 Accepted Decision、RFC、Spec 和单一 Issue 范围实现；不得临场更换框架、数据库、Provider 或公共契约。
- 执行必要的静态检查、测试与构建，记录失败和已知限制。
- 不得为了完成任务降低验收标准或扩大产品范围。

### 1.4 文档与 Git 操作者

- 准确归档讨论、提案、决定、证据与进度，区分所有内容类型。
- 在授权范围内创建或整理 Issue、Branch、Commit、PR 与 Review 修复。
- 普通低风险 PR 在验收和 Required Checks 全部通过后可自主合并；高风险事项必须停在用户 Gate。
- 每次归档后执行检查清单并输出 Archive Result。

### 1.5 模型可用性

指定模型是任务约束，不是偏好。平台无法提供对应模型时，必须暂停该任务类型并报告，不得静默使用其他模型替代。Luna 不可用不阻塞策划文档，但阻塞代码实现。

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
Sol/xhigh decomposes a bounded Issue
↓
Luna/max implements on a dedicated branch
↓
Required checks and deterministic tests
↓
Sol/xhigh five-axis review
↓
Fix and rerun checks
↓
ordinary low-risk PR: agent merge and close
high-risk trigger: stop and request user decision
```

自主合并不改变 Decision / RFC 状态，也不能替代 Goal 激活、范围批准和最终发布 Gate。

---

## 4. 边界与禁止

- ChatGPT 的「建议」「推荐」「Proposed Decision」**不等于**用户决定。
- 仅有用户的明确批准语义（同意 / 确认 / 接受 / 就按这个方案 / 该决策通过 / 其他语义明确的批准）才能标记 Accepted。
- Agent 不得为了让文档看起来完整而补充未经讨论的事实。
- Agent 不得静默删除、覆盖或改写历史决策；改变旧决定时必须保留追踪关系。
- 在用户明确激活 Goal 前，不得编写业务实现代码或执行新的 Technical Spike。
- 指定模型不可用时不得静默替换；需求与 Accepted 文档冲突时不得强行继续。
- 不得隐藏失败测试、已知缺陷或未解决风险。
- 不得为低概率 Case 堆叠防御、机械 Rubric 或非重大核心风险引入哈希要求。

---

## 5. 相关文档

- [product-design-protocol.md](product-design-protocol.md) — 完整设计与决策协议
- [documentation-rules.md](documentation-rules.md) — 文档规则与内容类型
- [../../AGENTS.md](../../AGENTS.md) — 协作者入口规范
- [../decisions/dec-039-proportional-validation-and-review-governance.md](../decisions/dec-039-proportional-validation-and-review-governance.md) — 适度校验
- [../decisions/dec-040-autonomous-agent-execution-and-model-roles.md](../decisions/dec-040-autonomous-agent-execution-and-model-roles.md) — 自主权限与模型角色
- [../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md](../decisions/dec-041-end-to-end-demo-mvp-delivery-envelope.md) — 演示 MVP 包络
