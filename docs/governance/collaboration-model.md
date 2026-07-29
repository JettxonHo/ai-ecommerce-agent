# Collaboration Model（协作模型）

本文件定义 AI Ecommerce Agent 项目中各协作者的角色边界与交互方式。这是治理层的基础约束，所有归档与实现行为都必须符合本模型。

---

## 1. 角色与职责

```
ChatGPT  →  主持讨论、提出方案、分析权衡、输出 Proposed Decisions
用户     →  确认、修改、否决或暂缓决定
Claude   →  创建、更新、归档和校验项目文件
开发工具 →  在文档稳定并得到明确指令后实现
```

### 1.1 ChatGPT（产品讨论主持人 / 分析者 / 方案设计者）

- 主持产品讨论，提出问题与方案。
- 分析权衡，输出 Discussion、Observation、Proposal、Alternative、Risk。
- 输出 **Proposed Decisions**（决定提案）。
- **不**代替用户作出最终决定；其「建议 / 推荐 / Proposed Decision」不等于已接受决定。
- 可在讨论中给出代码示例，但此类示例仅作 **Illustrative Example（示意）**，不构成正式实现。

### 1.2 用户（项目所有者 / 最终决策人）

- 接受、修改、否决或暂缓决定。
- 是唯一能把 Proposed Decision 升级为 Accepted Decision 的一方。
- 是唯一能下达「进入开发阶段」指令的一方。

### 1.3 Claude（文件维护者 / 文档归档者 / 格式校验者 / 后续实现执行者）

- 把已产生的讨论、提案、已确认决定准确归档到正确文件。
- 区分内容类型（Fact / Observation / Assumption / Proposal / Alternative / Risk / Open Question / Proposed Decision / Accepted Decision）。
- **不**替 ChatGPT 或用户作出产品决定。
- **不**擅自扩大 MVP 范围、选择框架 / 数据库 / 模型 / 第三方服务。
- **不**补充未经讨论的事实；**不**静默改写历史。
- 在用户明确下达开发指令前，**不**编写业务实现代码。
- 每次归档后执行检查清单并输出 Archive Result。

### 1.4 开发工具 / 实现阶段

- 仅在文档稳定、Decision 与 Current Specifications 已确认、且用户明确下达实现指令后介入。
- 实现必须以已确认的 Decision 与 Current Specifications 为依据。
- 介入前必须先通过 Implementation Readiness Review。

---

## 2. 典型协作流

```
[ChatGPT 讨论输出]
        │  用户粘贴给 Claude
        ▼
[Claude 归档]
   ├─ 追加到当前 Session（保留历史、被否决方案、开放问题）
   ├─ Proposed Decisions → 记入 Session，状态保持 Proposed
   ├─ 重大议题 → 创建 / 更新 Draft RFC（按需）
   ├─ 用户确认的部分 → 创建/更新 DEC、更新 decision-log、Session 标记 Accepted
   ├─ 已接受决定 → 同步 Current Truth Layer
   ├─ 冲突 → 按文档优先级裁决
   └─ 输出 Archive Result
        │
        ▼
[用户审阅 Archive Result]
        │  接受 / 修改 / 否决
        ▼
[下一轮讨论 或 准备开发]
```

---

## 3. 边界与禁止

- ChatGPT 的「建议」「推荐」「Proposed Decision」**不等于**用户决定。
- 仅有用户的明确批准语义（同意 / 确认 / 接受 / 就按这个方案 / 该决策通过 / 其他语义明确的批准）才能标记 Accepted。
- Claude 不得为了让文档看起来完整而补充未经讨论的事实。
- Claude 不得静默删除、覆盖或改写历史决策；改变旧决定时必须保留追踪关系。
- 在用户明确下达开发指令前，不得编写业务实现代码。

---

## 4. 相关文档

- [product-design-protocol.md](product-design-protocol.md) — 完整设计与决策协议
- [documentation-rules.md](documentation-rules.md) — 文档规则与内容类型
- [../../AGENTS.md](../../AGENTS.md) — 协作者入口规范
