# DEC-071：采用 `luna-worker` 专属实现路由并暂停 Terra 自动回退

## Type

Agent Governance / Development Orchestration / Model Routing / Review Independence

## Status

Accepted

## Decision

项目将后续边界明确的实现、测试与修复任务路由到 Codex 自定义 Agent `luna-worker`。该名称是创建实现 Agent 时必须使用的准确 Agent 名称，不得用逻辑角色“Luna Max”、单独的模型字符串或其他 Agent 名称替代。

实现路由的已接受配置为：

```text
逻辑角色：IMPLEMENTER
请求的自定义 Agent：luna-worker
配置文件：~/.codex/agents/luna-worker.toml
配置模型：gpt-5.6-luna
配置推理强度：max
```

Sol XHigh 继续担任 `ORCHESTRATOR_REVIEWER`，负责策划、任务拆分、任务合同、调度、独立 PR Review 与 Goal 验收。`luna-worker` 只在规格冻结、Goal 已由用户明确激活、且 Issue 与任务合同边界清晰后执行实现。实现者不得最终批准或合并自己的 PR。

### Terra 路由规则

- 停止自动或默认把实现任务路由给 Terra。
- 未经用户对具体任务明确许可，不得新建 Terra 实现 Agent。
- Terra 可以继续承担用户明确授权的辅助工作；它不再是 Luna 不可用时的自动实现回退。
- 已由 Terra 产生的有效代码、Commit、Branch、PR 与测试证据必须保留，不得因路由变化机械重做、删除、重置或覆盖。
- 已完成并创建 PR 的 Terra 工作进入 Sol 独立 Review；未完成工作只有在取得交接检查点、停止同文件并发后，才可把剩余范围交给 `luna-worker`。

### Active Terra 迁移协议

发现仍在运行的 Terra Agent 时，Sol 必须先要求其停止扩大范围并生成交接检查点。检查点至少记录：Agent 任务名称、Issue、Branch / worktree、基准与最新 Commit、修改文件、已完成与未完成工作、测试命令与结果、未提交修改、阻塞项、已知风险和下一步建议。获得检查点后停止 Terra；Terra 停止前和 `luna-worker` 开始前，不得让两者并发修改同一组文件。

### `luna-worker` 任务合同

每次创建实现 Agent 前必须记录上述逻辑角色、Agent 名称、配置路径、配置模型与推理强度，并在运行环境可见时记录实际模型。验证状态只允许：

- `CONFIG_VERIFIED`：配置文件与可调用的自定义 Agent 已确认；
- `RUNTIME_VERIFIED`：运行时明确暴露并确认实际模型；
- `UNVERIFIED_RUNTIME_MODEL`：运行时不暴露实例模型元数据，不得把配置推断写成运行时事实。

重新派发必须基于边界明确的 Issue 或剩余任务，并附原任务合同、Terra 交接检查点（如适用）、Branch / worktree、基准 Commit、既有修改、允许与禁止修改边界、验收、测试、停止条件和独立 Reviewer。`luna-worker` 必须先检查已有工作，不得覆盖或重复已完成实现，并在完成后返回标准结果包。

### 不可用处理

若当前会话无法发现或创建名为 `luna-worker` 的自定义 Agent：

1. 不自动回退到 Terra；
2. 不声称已启动 Luna；
3. 不开始新的实现任务；
4. 输出 `STATUS: BLOCKED_LUNA_WORKER_UNAVAILABLE`；
5. 报告已检查的配置路径、可见 Agent、Active Terra、已完成交接检查点，以及需要重启 Codex、重新打开任务或由用户确认的事项。

该阻塞只停止实现路由，不自动阻止不依赖实现 Agent 的已授权策划与独立 Review。

## Reason

运行时现已能按准确名称发现并创建 `luna-worker`。使用自定义 Agent 名称可确保加载已验证配置，也避免把逻辑角色、配置模型和实际运行时身份混为一谈。暂停 Terra 自动回退可消除错误归因和意外模型替换，同时通过交接协议保护已有成果。

## Impact

- 后续任务合同、Issue 与 PR 必须写明 `luna-worker` 和模型验证状态。
- `luna-worker` 不可用会阻塞新的实现任务，除非用户另行明确授权具体替代方案。
- 当前迁移不改变 Issue 范围、验收标准、测试要求、Review 独立性或人工 Gate。
- 当前迁移不启动 MVP-0 Goal，不授权业务实现、Technical Spike、依赖安装或 Live Provider。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Related Issue

[Issue #61](https://github.com/JettxonHo/ai-ecommerce-agent/issues/61)

## Supersedes

None.

## Amends

- [DEC-040](dec-040-autonomous-agent-execution-and-model-roles.md)：保留分级自主权限、Sol / Luna 分工和人工 Gate；实现 Agent 的准确路由与不可用处理以本 DEC 为准。
- [DEC-043](dec-043-sol-luna-terra-multi-agent-development-orchestration.md)：保留多 Agent 任务合同、线程隔离与 Review 独立性；暂停 Luna→Terra 自动或默认实现回退，改用准确的 `luna-worker` 自定义 Agent。

## Does Not Amend

- RFC-006 / DEC-052 的产品运行时 OpenAI Provider 模型；开发协作 Agent Terra 与产品所调用的模型不是同一治理对象。
- DEC-021 / DEC-041 的产品运行时单 Agent 边界。

## Notes

2026-08-08 的只读路由探针确认 `luna-worker` 可按准确名称创建，配置文件存在且声明 `gpt-5.6-luna` / `max`；当前工具未暴露实例模型元数据，因此验证记录为 `CONFIG_VERIFIED` 与 `UNVERIFIED_RUNTIME_MODEL`，不得宣称 `RUNTIME_VERIFIED`。
