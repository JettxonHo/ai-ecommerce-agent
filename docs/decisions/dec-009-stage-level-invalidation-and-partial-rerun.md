# DEC-009：MVP 采用阶段级依赖失效与局部重跑

## Type

Product

## Status

Accepted — Amended by DEC-044 / DEC-047

> **Current amendments:** [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md) 保留本决定的阶段级失效范围，并确认“展示失效预览 → 用户确认 → 局部重跑 → 受影响内容重新审核”；[DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md) 冻结重要 / 非重要修改的产品识别方式与语义组差异。以下原文保留为 2026-07-27 的历史决定。

## Decision

AI Ecommerce Agent 的 MVP 按照「事实层 — 洞察层 — 策略层 — 执行层」的阶段关系，处理用户修改后的结果失效和重新生成。

MVP **不在首个版本中实现精细的字段级依赖图**，而是采用**阶段级依赖关系**：

```
事实层
  ↓
洞察层
  ↓
策略层
  ↓
执行层
```

当上游阶段的重要内容发生修改时，其下游阶段应被标记为失效，并重新生成。

## Stage-Level Rerun Rules

### 1. 修改事实层

当用户修改商品价格、参数、功能、材质、已确认卖点或其他重要事实时：

```
事实层更新
  → 洞察层失效
  → 策略层失效
  → 执行层失效
  → 重新生成洞察、策略和执行结果
```

系统**不得**继续使用基于旧事实生成的下游结论。

### 2. 修改洞察层

当用户修改目标用户、用户需求、购买动机、购买阻碍、使用场景或其他重要洞察时：

```
洞察层更新
  → 策略层失效
  → 执行层失效
  → 重新生成策略和执行结果
```

事实层保持不变。

### 3. 修改策略层

当用户修改商品定位、价值主张、卖点优先级、差异化表达或内容传播方向时：

```
策略层更新
  → 执行层失效
  → 重新生成执行 Brief
```

事实层和洞察层保持不变。

### 4. 修改执行层

当用户直接编辑最终营销 Brief 时：

```
保存用户编辑
  → 默认不触发上游重新分析
```

执行层的人工编辑被视为最终业务调整。

> 是否保留 AI 生成版本与用户编辑版本的差异，尚未确定。

## Material and Non-material Changes

不是所有文字修改都必须触发重跑。

### 重要业务修改

以下类型的修改通常需要使下游结果失效：

- 商品价格；
- 核心参数；
- 商品功能；
- 商品限制；
- 目标用户；
- 用户需求；
- 购买阻碍；
- 卖点优先级；
- 商品定位；
- 对外传播边界；
- 其他会改变业务判断的内容。

### 非重要文字修改

以下修改可以不触发自动重跑：

- 错别字；
- 标点；
- 不改变含义的语言润色；
- 格式调整；
- 展示顺序的轻微调整。

> 具体如何自动区分重要与非重要修改，尚未确认。

MVP 可以通过：

- 用户主动选择「重新生成受影响内容」；
- 系统提示修改可能影响下游；
- 对明确结构化字段使用预设规则；

实现基本控制。

> 具体交互方式仍需后续讨论。

## Invalidation Principle

被标记为失效的内容：

- 不得继续显示为当前有效结果；
- 不得进入最终营销 Brief；
- 不得继续作为后续生成依据；
- 应明确提示用户需要重新生成。

系统可以保留旧版本作为历史记录，但是否实现版本历史尚未确定。

## Human Review After Rerun

局部重跑完成后，用户应重新查看受影响的分析内容。

- 如果重跑发生在常规审核节点之前，更新后的内容进入同一个审核节点。
- 如果用户已经完成审核后又修改上游重要内容，则相关下游结果需要重新生成，并再次由用户确认。

> 具体是否需要强制二次确认，仍需在交互设计阶段进一步明确。

## Reason

全部重跑虽然简单，但会导致：

- 不相关内容被重新改写；
- 生成时间和模型成本增加；
- 用户已经认可的内容发生无意义变化；
- 用户难以理解修改影响。

只更新用户直接修改的字段，又会导致：

- 下游结论继续依赖旧信息；
- 事实、洞察、策略和 Brief 互相矛盾；
- 输出可靠性降低。

精细的字段级依赖图长期更准确，但会明显增加：

- 数据结构复杂度；
- 依赖维护成本；
- 工作流设计难度；
- 测试范围；
- MVP 开发时间。

因此，阶段级失效和局部重跑能够在结果一致性与 MVP 可实现性之间取得平衡。

## Impact

该决定将影响：

- PRD；
- MVP Scope；
- User Flow；
- 四层 Brief 的状态设计；
- 用户编辑流程；
- 结果失效标记；
- 工作流重跑能力；
- 中间状态保存；
- Checkpoint 与恢复需求；
- Agent 节点划分；
- 前端状态提示；
- 测试与验收标准；
- LangGraph 或其他工作流框架评估；
- 开源仓库筛选标准。

> 后续技术方案必须能够回答：用户修改某一阶段后，系统如何判断哪些阶段失效，并从正确的位置重新执行？

## Related Session

Session-001：项目定位、目标用户与核心业务场景（[../sessions/session-001-project-positioning-and-mvp.md](../sessions/session-001-project-positioning-and-mvp.md)）

## Related RFC

None

## Supersedes

None

## Amends

None

## Amended By

- [DEC-044](dec-044-guided-task-workbench-input-gates-and-confirmed-partial-rerun.md)
- [DEC-047](dec-047-progressive-evidence-edit-intent-and-actionable-recovery-interactions.md)

## Decision Boundary

**本决定已经确认：**

- MVP 采用阶段级依赖关系；
- 修改事实层会使洞察、策略和执行层失效；
- 修改洞察层会使策略和执行层失效；
- 修改策略层会使执行层失效；
- 最终 Brief 的直接编辑默认不触发上游重跑；
- 重要业务修改和纯文字修改应区别处理；
- MVP 暂不实现精细字段级依赖图。

**本决定尚未确认：**

> 以下为本决定接受时的边界；“自动或手动重跑”与“再次审核”后来由 DEC-044 解决，重要修改识别与修改前后差异后来由 DEC-047 解决。其余项目仍未确认。

- 是否采用 LangGraph；
- 工作流节点的具体划分；
- 是否使用 Interrupt、Command 或 Checkpoint；
- 状态保存数据库；
- 失效状态的数据结构；
- 如何自动识别重要修改；
- 是否保留历史版本；
- 是否显示修改前后差异；
- 是否自动重跑或由用户手动触发；
- 是否强制进行第二次人工审核；
- 字段级依赖图是否进入后续版本。

## Notes

- 用户于 2026-07-27 对该方案明确回复「确认」，通过 Decision Gate。
- 评估时存在的另外两个方案——**全部重跑（每次修改重生成全部下游）** 与 **只修改直接字段、不更新下游依赖**——**未被采用**，但**未被永久禁止**，作为备选方案保留（见 Session-001「Alternatives」I / J）。本决定采用两者之间的折中：阶段级失效 + 局部重跑。
- **精细字段级依赖图暂缓到后续版本**（不进入 MVP），作为后续扩展保留（见 Session-001「Deferred Topics」）。
- 与 [DEC-006](dec-006-four-layer-structured-marketing-brief.md)（四层结构）、[DEC-007](dec-007-single-review-node-and-exception-pauses.md)（审核节点 + 异常暂停）、[DEC-008](dec-008-tiered-evidence-and-traceable-conclusions.md)（修改产生依赖影响 Principle 6）协同：阶段级失效是 DEC-008「修改产生依赖影响」原则的具体执行机制，与 DEC-007「修改后重跑」同源。
- **架构 RFC 业务约束：** 本决定与 DEC-007（工作流暂停 / 恢复）、DEC-008（结论 / 依据 / 依赖关系存储与失效）共同构成后续架构 RFC 的业务约束。当前**不创建 RFC**；后续进入「工作流状态、暂停恢复与技术实现方案比较」时，以 DEC-007 / DEC-008 / DEC-009 作为业务约束。
- 本决定确认的是**阶段级失效与局部重跑规则**；自动重跑交互后来由 DEC-044 修订为失效预览与用户确认后的局部重跑。LangGraph / Checkpoint / Interrupt / 状态数据库 / 完整版本历史 / 字段级依赖图 / 像素级前端界面 / Agent 或节点数量仍不由本决定确认（见 Decision Boundary）。
- 已同步至 [../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。Agent 与 Architecture 规格未更新（工作流节点划分、Checkpoint、失效状态数据结构等技术实现尚未确认）。
