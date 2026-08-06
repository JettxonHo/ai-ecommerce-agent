# Implementation Readiness（开发就绪状态）

> **Status: CONDITIONALLY READY — PRE-DEVELOPMENT PLANNING ONLY**
>
> Foundation 与 RFC-001 / RFC-002 已完成，但 Business / Production Implementation、TS-01～TS-05 执行和实际 Goal 均未授权。已完成的 Spike-001 不在本禁令所指范围内。

进入开发至少需要以下条件**全部**满足，并须先通过 Implementation Readiness Review（见 [../reviews/](../reviews/)），再由用户明确批准。

---

## 前置条件 Checklist

- [x] 项目定位与端到端演示交付包络已确认（DEC-041 / DEC-042）
- [x] 首要目标用户、复合 Persona 策划方式与 JTBD 基线假设已确认；真实访谈是 Beta 前门禁（DEC-002 / DEC-042）
- [x] 核心问题已确认
- [x] MVP 高层范围与非范围已确认
- [x] 单任务工作台、两级输入门禁、Needs Input、失效预览与用户确认后局部重跑已确认（DEC-044）
- [x] Task / Fact Stage 最低门禁、演示默认文件限制、单文件部分接受与分级冲突处理已确认（DEC-045）
- [x] Review Package、Approved Strategy、Marketing Brief、Xiaohongshu Brief 产品语义组，以及 Domain Version / Review Draft revision / Current Truth / 导出快照行为已确认（DEC-046）
- [x] 渐进式证据、语义组差异与编辑意图、阶段时间线、行动导向恢复和导出前确认已确认（DEC-047）
- [x] 三个固定资料包 + 一个变更脚本、行为门禁 + 人工可用性判断、Release Candidate Live Smoke 和 Markdown-first 用户导出已确认（DEC-048）
- [x] RFC-003 的 Checkpointer 拓扑、同步持久性、可重入 Node 与 Business-Current-Truth-first Reconciliation 已确认（DEC-049；RFC-003 整体仍未 Accepted）
- [x] RFC-003 的 PostgreSQL Durable Dispatch、数据库权威 Lease / Heartbeat / Fencing Token 与协作式取消 / Supersession 已确认（DEC-050；RFC-003 整体仍未 Accepted）
- [x] 关键 Agent、Workflow、Human Review 与 Skill 边界已确认
- [x] Retrieval / Evidence 与 Skill 的概念职责已确认
- [x] 外部 Skill 供体的 Adapt / Reference 策略已确认
- [ ] 必要 RFC 已完成（且相关 RFC 状态为 Accepted）
- [ ] 关键 Decision Records 已完成（状态为 Accepted）
- [ ] PRD 和架构文档已同步
- [ ] 最终公共数据契约、API 与状态 / 错误映射已明确
- [ ] 完整测试与验收标准已存在（产品验收包与必要行为门禁已由 DEC-048 确认；测试工具、Fixture 实例与最终 E2E 步骤待 Testing Strategy 补全）
- [ ] 文档不存在未同步或冲突部分
- [ ] ARP-02 / 03 / 09 完整 Artifact、ARP-05～08 与 TS-01～TS-05 Charter 已完成
- [ ] MVP Development Plan、Testing Strategy 与长期 Goal 文本已接受
- [x] 已确认可用实现路由与独立 Reviewer：Luna/max 优先；不可用时按 DEC-043 显式路由 Terra/xhigh 或外部 Luna 线程
- [ ] 已通过 Implementation Readiness Review
- [ ] 用户明确发出「进入 Goal 执行阶段」指令

---

## 当前状态

- **Architecture Readiness:** CONDITIONALLY READY
- **Development Status:** CONDITIONALLY READY（仅策划与治理）
- **Spike-001:** COMPLETED
- **RFC:** RFC-001 / RFC-002 = ACCEPTED；RFC-003 = DRAFTING（DEC-049 / DEC-050 已接受 DQ-01～06 输入，整体未 Accepted）；RFC-004～RFC-007 = PROPOSED
- **Foundation:** FND-001 / FND-002 / FND-003 = COMPLETED
- **Wave 1 Artifact:** ARP-01 / 04 / 10 完整 Accepted；ARP-02 / 03 / 09 仅 TS-01 Minimum Slice Accepted
- **产品交互与验收:** 单任务工作台、确认式局部重跑、Task / Fact Stage 最低门禁、默认文件限制、分级冲突、审核 / Brief 产品语义和版本 / revision / 导出、渐进式证据、编辑影响、阶段进度、行动导向恢复、固定验收包、行为门禁与 Markdown-first 用户导出 = ACCEPTED（DEC-044～048）；最终公共 Schema、视觉组件、Diff 算法、并发实现、测试工具与公共状态映射仍待 Frontend Architecture / RFC / Testing Strategy
- **Workflow Runtime:** 独立 PostgreSQL Checkpoint Database、同步 `PostgresSaver`、`sync` durability、可重入 Node 与 Current-Truth-first Reconciliation = ACCEPTED INPUT（DEC-049）；PostgreSQL Work Intent + Poll-and-claim、数据库权威 Lease / Heartbeat / Fencing Token、协作式 Cancellation / Supersession + Commit Fence = ACCEPTED INPUT（DEC-050）；Compatibility、Safe Resume Action Matrix、迁移 / 回滚与验收证据仍待 RFC-003
- **允许工作:** 产品规格、Architecture RFC、Readiness Artifact / Spike Charter 规划、测试策略、开发计划、Goal 文档与一致性 Review
- **禁止工作:** Business / Production Implementation、TS-01～TS-05 执行、公开部署、实际 Goal 启动
- **用户 Goal 指令:** 未下达
- **Agent 路由:** Luna/max 为首选实现 Agent；当前工具不能创建 Luna 时，可输出外部 Luna 任务包或显式使用 Terra/xhigh 回退，不因 Luna 暂时不可用单独阻塞 Goal，但必须保持任务合同、实际模型披露和 Review 独立性

---

## 状态变更规则

- `CONDITIONALLY READY` 只表示允许完成正式开发前策划，不表示业务实现已就绪。
- 只有前置条件全部满足、完整策划包已展示、Implementation Readiness Review 通过且用户明确批准后，才可将状态改为 `READY` 并激活 Goal。
- 任何必需条件未满足，Business / Production Implementation 保持 `NOT AUTHORIZED`。
- 状态变更须在 [../decisions/decision-log.md](../decisions/decision-log.md) 记录或在审查文件中留痕。
