# DEC-072：采用长期自主开发授权与严格 Agent 身份治理

## Type

Agent Governance / Long-running Execution / Model Identity / Human Gates

## Status

Accepted

## Decision

用户以《多 Agent 项目策划与长期自主开发总指令（Luna Worker 正确版）》明确授权：在产品、架构、测试、Goal、Issue 与任务合同已经闭合，且不存在本决定保留的人工确认条件时，主控 Agent 应连续推进既定 Goal，不停留在重复计划或只输出任务包。

本授权不取消开发前策划，也不把未接受 Proposal 自动升级为 Accepted。当前必须先完成并接受最小 RFC-007、快速 MVP-0 Development Plan、Testing Strategy、Goal、精简 Readiness Review，以及所有会改变主要技术栈或产品取舍的开放决定。上述 Gate 完成后，已接受 Goal 可直接激活并按普通开发循环持续执行，不再要求额外重复一条固定措辞作为第二次启动口令。

### Agent 身份与模型状态

实现任务必须请求准确的 Codex 自定义 Agent `luna-worker`，并记录：逻辑角色、Agent 类型、配置文件、配置模型、配置推理强度、运行时模型可见性、线程、Issue、Branch / worktree 与基准 Commit。`luna-worker` 的当前配置为：

```text
逻辑角色：IMPLEMENTER
请求的 Agent 类型：luna-worker
配置文件：~/.codex/agents/luna-worker.toml
配置模型：gpt-5.6-luna
配置推理强度：max
```

模型状态只能使用：

- `CONFIG_VERIFIED`：已读取并验证配置，但运行时没有单独暴露实际模型或推理强度；
- `RUNTIME_VERIFIED`：运行环境明确暴露并确认实际模型与推理强度；
- `UNVERIFIED_RUNTIME_MODEL`：无法验证配置或实际运行时模型；
- `MODEL_MISMATCH`：运行时明确显示的模型与请求配置不一致。

配置文件可读、内容正确且自定义 Agent 可被创建，但实例元数据未暴露时，记录 `CONFIG_VERIFIED`，不再并列记录 `UNVERIFIED_RUNTIME_MODEL`。Agent 自述不能成为 `RUNTIME_VERIFIED` 证据。

### Terra 与失败关闭

- Terra 不是自动回退实现者；只有用户在当前任务中明确授权具体范围、模型状态与写入权限后才可使用。
- `luna-worker` 不可发现时输出 `STATUS: BLOCKED_LUNA_WORKER_UNAVAILABLE`，停止新的实现任务，不得用默认 Agent、worker、Terra 或模型覆盖冒充。
- 已有 Terra 成果必须如实保留与归因；迁移须先取得交接检查点并停止同文件并发。

### 自主权限与人工 Gate

在 Accepted Goal、任务合同、文件边界和安全条件内，主控可自主进行只读调查、分支与受控 worktree、项目文件修改、测试与构建、Issue / PR / Commit / Push、独立 Review、普通低风险 Merge、Issue 关闭和状态文档更新。

以下事项仍必须先请求用户确认：

- 删除生产数据或不可逆数据迁移；
- 高风险发布、生产配置或不可逆外部操作；
- 认证、授权、支付、隐私、合规或敏感数据处理逻辑变化；
- 更换主要技术栈、大规模重写核心模块或修改公共契约；
- 明显额外费用、真实生产凭证或安全控制绕过；
- Goal / 产品方向重大变化、多个合理方案只能由产品取舍决定、显著扩大范围；
- 降低质量、测试或验收标准。

受阻事项不影响其他独立工作时，主控继续推进不受影响的范围。

### 持久化事实与任务合同

仓库继续复用现有等价权威路径：`docs/goals/` 承载 Goal，`docs/handoffs/implementation-readiness.md` 承载当前状态，`docs/decisions/decision-log.md` 承载决定索引，`docs/governance/collaboration-model.md` 承载 Agent 协作。不得机械创建重复的根级文件造成事实分裂。

每个 `luna-worker` 任务必须有边界完整的任务合同，并返回模型状态、Issue、Branch / worktree、基准与最新 Commit、修改文件、完成 / 未完成工作、测试、未提交修改、风险、阻塞与下一步。实现者不得最终批准或合并自己的 PR；主控必须审查实际 Diff 与测试证据。

## Reason

长期 Goal 需要明确的连续推进授权，同时必须防止把配置、运行时身份、任务成功和验收成功混为一谈。严格的自定义 Agent 路由、任务合同、独立 Review 与持久化交接能维持自主开发连续性，又保留产品方向和高风险事项的人类最终控制。

## Impact

- 现有“完整策划包接受后还必须重复固定启动短语”的要求被修订为：本指令已提供持续执行授权，但所有仍未接受的产品 / 架构 Proposal 和 Readiness Gate 必须先闭合。
- 当前 P-68A / P-69A / P-70A、最小 RFC-007 整体、Development Plan 新提案、Testing Strategy、Goal 与 Readiness Review 仍未因本 DEC 自动接受。
- 当前不授权业务实现、Technical Spike、Live Provider、依赖安装、公开部署或高风险操作。
- 后续 Goal 采用 Sol 主控 / 独立 Review、`luna-worker` 实现；未经当前任务明确许可不使用 Terra。

## Related Session

[Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Amends

- [DEC-040](dec-040-autonomous-agent-execution-and-model-roles.md)：保留风险分级与人工 Gate，补充长期 Goal 的持续执行授权。
- [DEC-043](dec-043-sol-luna-terra-multi-agent-development-orchestration.md)：保留任务合同、线程隔离与独立 Review；实际实现 Agent 名称与 Terra 规则以 DEC-071 / 本 DEC 为准。
- [DEC-070](dec-070-fixed-embedding-contract-and-accelerated-mvp0-adoption.md)：不改变快速 MVP-0 分期；把“完整策划包后再重复固定启动口令”修订为“全部重大 Proposal 与 Readiness Gate 接受后依据本 DEC 持续执行”。
- [DEC-071](dec-071-luna-worker-exclusive-implementation-routing.md)：修正模型状态语义，并明确在策划 / Readiness Gate 完成后的持续执行授权。

## Does Not Amend

- 产品运行时单 Agent 边界、Accepted 产品范围、RFC-001～006 技术结论与适度校验原则。
- 用户对破坏性操作、重大架构 / 产品变化、安全与不可逆事项的最终确认权。

## Source

用户于 2026-08-08 提供的《多 Agent 项目策划与长期自主开发总指令（Luna Worker 正确版）》全文。
