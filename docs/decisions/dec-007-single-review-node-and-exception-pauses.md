# DEC-007：MVP 采用单一关键审核节点与异常暂停机制

## Type

Product

## Status

Accepted — Amended by DEC-047

> **Current amendment:** [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) 冻结异常暂停后的用户可见原因、业务影响和行动导向恢复交互；本决定以下原文保留为 2026-07-27 的原则层历史记录。

## Decision

AI Ecommerce Agent 的 MVP 采用 Human-in-the-loop 人机协作流程。

正常情况下，系统设置一个**强制关键审核节点**：

```
用户提交商品资料
        ↓
系统执行资料完整性与冲突检查
        ↓
生成事实层、洞察层和初步策略层
        ↓
用户审核、修改和确认
        ↓
生成最终执行层营销 Brief
        ↓
用户查看、编辑和导出
```

在常规流程中，**不要求**用户在事实、洞察和策略的每一层分别确认。

用户在一个集中审核节点中检查和调整分析草稿，再决定是否继续生成最终营销 Brief。

除常规审核节点外，当系统识别到重要异常时，可以暂停工作流并向用户提出补充问题。

## Normal Review Node

常规审核节点出现在：

- 事实层、洞察层和初步策略层已经生成之后；
- 最终执行层营销 Brief 生成之前。

在该节点，用户可以：

- 修正商品事实；
- 补充缺失资料；
- 删除不合理的洞察；
- 接受或否定关键假设；
- 调整目标用户判断；
- 调整卖点优先级；
- 调整商品定位；
- 标记不能公开表达的信息；
- 选择继续生成最终 Brief；
- 退回并重新分析。

> 具体编辑界面、字段粒度和交互控件尚未确定。

## Exceptional Pause Conditions

以下情况可以触发额外暂停：

- 商品资料之间存在明显矛盾；
- 关键商品参数严重缺失；
- 用户提供的卖点缺乏资料依据；
- 目标用户或使用场景无法合理判断；
- 基础资料与增强资料明显冲突；
- 系统无法可靠区分事实与推断；
- 内容可能包含夸大、无法验证或高风险表达；
- 继续生成可能使错误传递到后续策略和执行层。

异常暂停后，系统应：

1. 说明检测到的问题；
2. 指出冲突或缺失信息；
3. 提出具体补充问题；
4. 等待用户回复；
5. 根据用户补充继续或重新执行相关步骤。

> 系统**不得**在关键事实冲突时自行猜测并继续生成最终 Brief。

## Human Authority Principle

商品运营和内容运营人员保留最终业务判断权。

Agent 的职责是：

- 整理资料；
- 提取事实；
- 形成分析；
- 暴露假设；
- 提供策略建议；
- 生成结构化交付物。

Agent **不应**替代用户对以下事项的最终确认：

- 商品事实；
- 目标人群；
- 商品定位；
- 卖点优先级；
- 对外传播边界；
- 最终营销 Brief。

## Reason

完全自动生成虽然流程简单，但事实识别错误可能继续污染洞察、策略和执行结果。

每一层都设置审核节点，又会导致：

- 交互步骤过多；
- 用户频繁被打断；
- 工作流过于繁琐；
- MVP 开发成本显著增加。

单一关键审核节点在可靠性与使用效率之间取得平衡：

- 在生成最终交付物前阻断重要错误；
- 保留运营人员的业务判断权；
- 避免每一步都要求人工确认；
- 可以体现 Agent 与用户协作，而不是一次性生成；
- 为后续暂停、恢复和状态保存提供明确业务依据。

## Impact

该决定将影响：

- User Flow；
- PRD；
- MVP Scope；
- 页面与交互设计；
- Agent 状态模型；
- 中间产物保存；
- 工作流暂停与恢复；
- 用户修改后的重新执行逻辑；
- Checkpoint 需求；
- Human-in-the-loop 技术方案；
- LangGraph 或其他工作流框架评估；
- 开源基底仓库筛选；
- 异常处理；
- 验收标准。

> 后续技术选型必须能够解释：系统如何在审核节点暂停、保存上下文、接收用户修改，并从正确的位置继续执行？

## Related Session

Session-001：项目定位、目标用户与核心业务场景（[../sessions/session-001-project-positioning-and-mvp.md](../sessions/session-001-project-positioning-and-mvp.md)）

## Related RFC

None

## Supersedes

None

## Amends

None

## Amended By

[DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)

## Decision Boundary

**本决定已经确认：**

- MVP 存在一个常规强制审核节点；
- 审核发生在分析草稿生成后、最终 Brief 生成前；
- 用户可以修改和确认分析草稿；
- 资料矛盾、关键缺失或高风险表达可触发额外暂停；
- 关键冲突不能由系统自行猜测后继续；
- 用户保留最终业务判断权。

**本决定尚未确认：**

> 以下为本决定接受时的边界；审核产品语义后来由 DEC-029 / DEC-046 细化，异常暂停后的进度、错误与恢复交互由 DEC-047 解决。其余技术实现仍未确认。

- 是否采用 LangGraph；
- 是否使用 LangGraph Interrupt；
- 是否需要数据库级持久化；
- Checkpoint 的实现方式；
- 用户修改后重跑全部流程还是局部流程；
- 审核页面结构；
- 草稿字段的编辑粒度；
- 异常判断规则；
- 高风险表达的具体范围；
- 是否需要多人协作审核；
- 是否保留版本历史；
- 用户是否可以跳过常规审核节点。

## Notes

- 用户于 2026-07-27 对该人机协作方案明确回复「确认」，通过 Decision Gate。
- 评估时存在的另外两个方案——**完全自动生成（无审核节点）** 与 **每层分别审核确认**——**未被采用**，但**未被永久禁止**，作为备选方案保留（见 Session-001「Alternatives」）。本决定采用两者之间的折中：单一关键审核节点 + 异常暂停。
- **架构影响提示（不立即行动）：** 本决定是首个对工作流状态、暂停 / 恢复、Checkpoint、局部重跑提出明确业务要求的决定，具有潜在架构影响。但当前**不创建正式 Architecture Decision**，**不创建 RFC**；后续讨论「工作流状态、暂停恢复与局部重跑」技术方案时，再判断是否需要建立架构 RFC（见 Decision Boundary 与 Session-001「Deferred Topics」）。
- 本决定确认的是**人机协作模式（单一关键审核节点 + 异常暂停 + 用户最终判断权）**，不构成对 LangGraph / Interrupt API / Checkpoint 数据库 / Agent 数量 / 前端框架 / 状态存储方案 / 审核页面设计 / 自动风险审核规则的确认（见 Decision Boundary）。
- 已同步至 [../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。Agent 与 Architecture 规格未更新（工作流状态、Checkpoint、HITL 技术实现尚未确认）。
