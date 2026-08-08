# DEC-043：采用 Sol 主控、Luna 实现、Terra 辅助回退的多 Agent 开发编排

## Type

Agent Governance / Development Orchestration / Model Roles / Review Independence

## Status

Accepted — Amended by [DEC-071](dec-071-luna-worker-exclusive-implementation-routing.md) and [DEC-072](dec-072-long-running-autonomy-and-agent-identity-governance.md)

> **Amendment notice（2026-08-08）：** 本文所记录的 Terra 显式实现回退是当时的 Accepted 历史决定。当前路由由 DEC-071 修订为：后续实现必须使用准确的自定义 Agent `luna-worker`；未经用户对具体任务明确许可，不得把实现自动或默认回退给 Terra。任务合同、线程隔离、成果保护与 Review 独立性继续有效。
>
> DEC-072 进一步冻结模型状态语义与长期 Goal 持续执行授权；高风险人工 Gate 和未接受 Proposal 仍然阻塞受影响实现。

## Decision

项目的**开发协作系统**采用三个逻辑角色。该决定只治理开发 Agent 与线程，不改变 DEC-021 / DEC-041 中“产品运行时不采用 Multi-Agent 主架构”的产品边界。

### Sol XHigh — `ORCHESTRATOR_REVIEWER`

```text
模型：GPT-5.6 Sol
推理强度：XHigh
逻辑角色：ORCHESTRATOR_REVIEWER
```

Sol 是主控、策划、调度与审查 Agent，负责：

- 调查代码库、文档、Issue、PR、分支、测试和当前风险；
- 主持产品与架构策划，提出有意义的备选、权衡、推荐和停止条件；
- 固化 Decision、RFC、规格、Development Plan、Testing Strategy 与 Goal；
- 将 Goal 拆为里程碑、依赖明确的 Issues 和可并行工作；
- 为实现 Agent 编写任务合同并进行任务路由；
- 处理跨模块问题、复杂缺陷和架构冲突；
- 检查实际代码、测试证据、文档同步和潜在回归，完成 PR / 阶段 / Goal Review；
- 判断普通低风险 PR 是否满足合并条件，并在 Goal 完成后输出全局验收结论。

Sol 原则上不承担普通、重复或边界明确的实现。仅在以下情况可以直接修改代码：

- 实现 Agent 多次修复后仍不能解决；
- 复杂架构、跨模块重构或高强度诊断与实现不可分离；
- 紧急问题阻塞整个 Goal；
- 需要受控技术验证原型；
- Luna 和适用的辅助实现 Agent 不可用；
- 任务本身与重大架构决定不可分离。

Sol 直接实现时仍必须走独立 Issue、Branch、测试和 PR。最终批准必须交给另一个独立审查 Agent 或人工 Gate；同一执行上下文不得同时完成实现和最终批准。

### Luna Max — `IMPLEMENTER`

```text
模型：GPT-5.6 Luna
推理强度：Max
逻辑角色：IMPLEMENTER
```

Luna 是首选代码实现 Agent。它必须读取任务合同、权威文档、Issue 和现有代码，先给出简要实现计划，再在独立分支内完成范围内实现、必要测试、静态检查、类型检查、构建和相关文档更新，并提交 Commit 与 PR。PR 必须说明问题、方案、范围、验证、风险、回滚和文档影响；根据 Sol Review 修复后须重新运行验证并更新 PR。

Luna 不得自行：

- 改变产品目标、Issue 范围、核心架构、主要技术方案或验收标准；
- 引入重大依赖，修改公共接口、跨模块数据协议或执行不可逆迁移；
- 把临时方案视为最终方案，跳过或隐藏失败测试、缺陷和风险；
- 在任务合同不清晰时猜测产品需求；
- 最终批准或合并自己实现的 PR。

需求不明确、文档冲突、Issue 与代码不一致、范围扩大、架构不支持、公共接口或重大依赖变化、数据迁移、跨模块测试失败、产品取舍或质量标准变化时，Luna 必须暂停受影响部分并升级给 Sol。与阻塞无关且边界独立的工作可以继续。

### Terra XHigh — `AUXILIARY_IMPLEMENTER`

```text
模型：GPT-5.6 Terra
推理强度：XHigh
逻辑角色：AUXILIARY_IMPLEMENTER
```

Terra 可承担代码库调查、文件和符号定位、测试运行、文档整理、独立方案分析、边界明确的实现、Bug 初步定位、类型与构建修复、测试补充、初步 Review 和 GitHub 状态核对。

Terra 不替代 Sol 作出产品决定、核心架构决定、高风险拆分、跨模块冲突裁决、最终 PR 批准或 Goal 级验收。

Luna 不可用时，Terra XHigh 可以作为实现回退。必须在 Issue、任务合同和 PR 中记录实际模型与逻辑角色，不得把 Terra 的工作标记为 Luna 完成。回退不得改变 Issue 范围、任务合同、测试要求、Review 独立性、验收标准或人工 Gate。

### 模型路由与回退

1. Sol 优先将冻结且边界清晰的实现任务路由给 Luna Max。
2. 当前工具可直接创建 Luna 时，由 Sol 按任务合同创建 Luna 执行线程。
3. 当前工具不能创建 Luna 时，Sol 不得假装已经调用 Luna；应输出标准化 Luna 任务包，由用户、上层调度器或外部编排器创建 Luna 线程。
4. 若当前环境可以创建 Terra，则可明确改由 Terra XHigh 执行，不因 Luna 暂时不可用而中断整个项目。
5. Sol 直接实现只适用于本 DEC 列出的例外，并必须满足独立最终 Review。

任何模型替换都必须显式披露；禁止静默替换和错误归因。

### 线程与并行隔离

- Sol 主控线程维护全局策划、调度、Review 和验收。
- 每个实现线程原则上只处理一个边界清晰的 Issue，或一组高度相关且不会发生写入冲突的 Issues。
- 并行任务必须先冻结接口、依赖、文件或模块所有权；不得让多个实现线程无边界地同时修改同一核心模块。
- 不假设不同线程自动共享完整上下文；交接必须通过项目文档、AGENTS、权威 Goal、GitHub Issue、任务合同、分支、Commit、PR、Review、Readiness / Current Status、Decision Log 和测试记录完成。
- 聊天记录不能作为项目事实的唯一来源；重要信息必须进入持久化载体。

### 标准任务合同

Sol 路由实现任务前，任务合同至少包含：

1. Agent 模型、推理强度和逻辑角色；
2. Issue、目标和可独立验证的交付物；
3. 权威文档及阅读顺序；
4. In Scope、Non-goals、依赖与允许修改的模块 / 文件边界；
5. 已冻结的接口、状态、数据与错误契约；
6. 验收标准和必须执行的测试 / Required Checks；
7. 风险、停止条件、升级路径与允许继续的独立工作；
8. PR 描述、文档同步、回滚和 Review 要求；
9. 指定独立 Reviewer 及合并权限。

任务合同不替代 Accepted Decision、RFC 或 Spec；Issue 不得重新定义产品和架构事实。

### Review 与合并独立性

- 实现 Agent 必须自检，但不得最终批准或合并自己的 PR。
- Sol 必须检查实际 Diff 与测试结果，不能只根据 PR 描述批准。
- 普通低风险 PR 在任务合同满足、Required Checks 全绿、Sol 无阻塞 Finding 后，可由 Sol 主控或另一具备权限的非实现 Agent 合并并关闭 Issue。
- Sol 自己实现的 PR 必须由独立 Agent 或人工审查；高风险和 DEC-040 保留的事项继续走人工 Gate。

## Alternatives Considered

### Luna 不可用即停止全部实现

- 优点：模型角色最严格。
- 缺点：将工具可用性变成整个 Goal 的单点阻塞。
- 结论：由本 DEC 修订；改为 Terra 显式回退，质量与 Review 要求不变。

### 单一 Agent 完成策划、实现和最终批准

- 优点：交接成本低。
- 缺点：缺乏审查独立性，容易产生范围和确认偏差。
- 结论：不采用。

### 无任务合同的多线程并行

- 优点：表面吞吐量高。
- 缺点：接口漂移、文件冲突和上下文丢失风险高。
- 结论：不采用。

## Reason

高推理策划与最终 Review、边界明确的实现、辅助调查和模型可用性回退需要不同职责。显式任务合同、线程隔离和实际模型披露可以维持长期自主开发连续性，同时避免实现 Agent 自批、静默模型替换和对聊天上下文的依赖。

## Impact

- AGENTS、Collaboration Model、Issue / PR Workflow、Development Plan、Goal 和任务包必须使用本角色与合同。
- Luna 仍是首选实现 Agent；Terra 是可审计回退，不是静默等价替代。
- Implementation Readiness 不再以 Luna 当前可用作为唯一模型前置条件，而要求存在符合本 DEC 的可用实现路由和独立 Reviewer。
- 本决定不授权创建实际 Goal、执行 TS-01～TS-05 或编写业务代码。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related RFC

RFC-001 至 RFC-007；本决定不改变其技术结论。

## Supersedes

None.

## Amends

- DEC-040：保留分级自主权限、Sol/Luna 主分工和人工 Gate；把“指定实现模型不可用即阻塞实现”修订为“Luna 优先，Terra XHigh 可显式回退，Sol 仅在列明例外下实现”。
- DEC-036 / DEC-037：仅修订未来 Goal 的 Agent 协作与合并方式；Spike-001 历史执行事实不变。

## Does Not Amend

- DEC-021 / DEC-041：产品运行时继续不采用 Multi-Agent 主架构。开发协作 Agent 不属于产品运行时 Agent。

## Notes

本 DEC 规定开发协作架构，不代表当前 Goal 已激活，也不代表当前环境已经创建 Luna 或 Terra 实现线程。

## Amended By

[DEC-071 — `luna-worker` 专属实现路由并暂停 Terra 自动回退](dec-071-luna-worker-exclusive-implementation-routing.md)

[DEC-072 — 长期自主开发授权与严格 Agent 身份治理](dec-072-long-running-autonomy-and-agent-identity-governance.md)
