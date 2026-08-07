# Implementation Readiness（开发就绪状态）

> **Status: CONDITIONALLY READY — PRE-DEVELOPMENT PLANNING ONLY**
>
> Foundation、Product Specification、RFC-001～006 已完成。Business / Production Implementation、Spike / Live call 和实际 Goal 均未授权。
>
> **Current Gate（2026-08-07）：** RFC-005 已整体接受，Final Consistency Review = PASS。用户已确认快速 MVP-0 Gate：之后只闭合最小 RFC-007、Development Plan、Testing Strategy、Goal 文本与精简 Readiness Review。完整展示前不启动开发。

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
- [x] 产品语义与 RFC / Testing 下游权威边界已确认（DEC-057）
- [x] 虚构“城市通勤双肩包”Anchor SKU、三个资料变体与一个 mutation 已确认（DEC-058）
- [x] Needs Input 的有限结构化行动请求模型已确认（DEC-059）
- [x] 声明风险、受控数据生命周期体验和跨会话任务返回入口已确认（DEC-060～062）
- [x] Product Specification Final Consistency Review 已通过
- [x] 用户已于 2026-08-07 明确接受 Product Specification 整体闭合
- [x] RFC-003 的 Checkpointer 拓扑、同步持久性、可重入 Node 与 Business-Current-Truth-first Reconciliation 已确认（DEC-049）
- [x] RFC-003 的 PostgreSQL Durable Dispatch、数据库权威 Lease / Heartbeat / Fencing Token 与协作式取消 / Supersession 已确认（DEC-050）
- [x] RFC-003 的显式 Compatibility Tuple、Current-Truth-first 七动作 Recovery Decision、受控迁移、前向恢复与风险切片证据边界已确认（DEC-051）
- [x] RFC-003 Final Consistency Review 已通过，用户已于 2026-08-06 明确接受 RFC-003 整体
- [x] RFC-006 的单一 OpenAI Responses / `gpt-5.6-terra` 基线、Application-owned 窄型同步 Model Runtime Port 与 Structured Output Authority 已确认（DEC-052；仅 DQ-01～03）
- [x] RFC-006 的有界 Model Recovery、可读 Version Tuple、五个固定 Profile 与确定性 Context Assembly 已确认（DEC-053；DQ-04～06）
- [x] RFC-006 的 Adapter Secret / Payload / Telemetry Allowlist、同 Port Scripted Substitute、断网 Contract Tests 与单次人工 RC Smoke 已确认（DEC-054；DQ-07～08）
- [x] RFC-006 Final Consistency Review 已通过，用户已于 2026-08-06 明确接受 RFC-006 整体
- [x] Frontend Foundation 已确认：React 19 + TypeScript + Vite 8 SPA、React Router Declarative Mode、TanStack Query / React Hook Form 显式状态所有权、OpenAPI 类型生成、npm + Vitest / Testing Library + Playwright Chromium（DEC-055；P-36～P-38）
- [x] Frontend Workbench / Interaction / Web Quality 已确认：深 TaskWorkbench、Native / 按需 Radix + CSS Modules、私有 WorkbenchProjection、revision-safe Autosave / Diff、WCAG / Desktop Chrome / Reflow 与 Evidence-driven Performance（DEC-056；P-39～P-41）
- [x] Frontend Architecture Final Consistency Review 已通过，用户已于 2026-08-07 明确接受 Frontend Architecture 整体
- [x] RFC-004 Contract Authority、语义 revision / Idempotency、耐久 `202` Receipt、Run Monitor、Capability 与 Problem Details 基础已确认（DEC-063；DQ-01～03）
- [x] RFC-004 Task 创建 / 最近列表 / Overview、revision-bound Needs Input / Source Preview-Confirm / Run Recovery 与不可变 Human Review 主协议已确认（DEC-064；DQ-04～06）
- [x] RFC-004 不可变 Brief / Comparison / typed revise / Markdown Export Snapshot、有限 RFC 9457 Problem action 与 fixed-workspace loopback same-origin transport 已确认（DEC-065；DQ-07～09）
- [x] RFC-004 单一 OpenAPI entry、有限 Operation / Schema / state catalog、有界最近窗口、additive compatibility、generated-client clean diff 与分层 Contract Tests 已确认（DEC-066；DQ-10）
- [x] RFC-004 Final Consistency Review 已通过
- [x] 用户已于 2026-08-07 明确接受 RFC-004 整体
- [x] RFC-005 Source authority / Task association、逐资料登记与处理、格式感知 Fragment / Locator 已确认（DEC-067；DQ-01～03）
- [x] RFC-005 PostgreSQL-native retrieval topology、单一版本化 Embedding Profile、immutable index generation、确定性 Planner / RRF 与有界候选已确认（DEC-068；DQ-04～06）
- [x] RFC-005 server-derived Scope、窄 Source / Evidence transport、immutable RetrievalRun + referenced EvidencePackage、Formal Evidence atomic commit、代表性评测与显式降级已确认（DEC-069；DQ-07～09）
- [x] RFC-005 exact Embedding Profile、Source / Evidence Operation / Schema catalog 与快速 MVP-0 staging 已接受（DEC-070；P-67A / DQ-10）；Final Consistency Review = PASS
- [x] 用户已明确接受 RFC-005 整体（2026-08-07）
- [ ] 最小 RFC-007（日志、correlation、有限 timeout / retry / backoff、错误与 Secret redaction；无完整 telemetry platform）已接受
- [x] 关键 Agent、Workflow、Human Review 与 Skill 边界已确认
- [x] Retrieval / Evidence 与 Skill 的概念职责已确认
- [x] 外部 Skill 供体的 Adapt / Reference 策略已确认
- [ ] 必要 RFC 已完成（且相关 RFC 状态为 Accepted）
- [ ] 关键 Decision Records 已完成（状态为 Accepted）
- [ ] PRD 和架构文档已同步
- [ ] 最终公共数据契约、API 与状态 / 错误映射已明确
- [ ] 完整测试与验收标准已存在（产品验收包与必要行为门禁由 DEC-048 确认；Frontend 工具 / 质量边界由 DEC-055 / 056 确认；Fixture 实例与最终 E2E 步骤待 Testing Strategy 补全）
- [ ] 文档不存在未同步或冲突部分
- [x] 快速 MVP-0 Gate 已确认：完整 ARP-02 / 03 / 09、ARP-05～08、TS-02 / 04 / 05 不再阻塞 MVP-0，进入 MVP-1 / 对应风险 Gate
- [ ] TS-01 / TS-03 的 stop-first bounded compatibility slice 已写入对应 Foundation Issue 合同（不先建设大型独立 Spike）
- [ ] MVP-0 Development Plan、Testing Strategy 与 Goal 文本已接受
- [x] 已确认可用实现路由与独立 Reviewer：Luna/max 优先；不可用时按 DEC-043 显式路由 Terra/xhigh 或外部 Luna 线程
- [ ] 已通过 Implementation Readiness Review
- [ ] 用户明确发出「进入 MVP-0 Goal」指令

---

## 当前状态

- **Architecture Readiness:** CONDITIONALLY READY
- **Development Status:** CONDITIONALLY READY（仅策划与治理）
- **Spike-001:** COMPLETED
- **RFC:** RFC-001～006 = ACCEPTED；RFC-005 Final Review = PASS；RFC-007 = DRAFTING（Issue #58；P-68A / P-69A / P-70A proposed）
- **Foundation:** FND-001 / FND-002 / FND-003 = COMPLETED
- **Wave 1 Artifact:** ARP-01 / 04 / 10 完整 Accepted；ARP-02 / 03 / 09 仅 TS-01 Minimum Slice Accepted
- **产品交互与验收:** 单任务工作台、确认式局部重跑、输入门禁、审核 / Brief / Evidence / Recovery / Markdown 导出 = ACCEPTED（DEC-044～048）；产品 / 技术权威边界、虚构 Anchor SKU、有限结构化 Needs Input、证据约束声明完整性、Task 范围资料与可逆移除、最小最近任务入口 = ACCEPTED（DEC-057～062）；前端应用 / 状态 / Contract Generation / Verification Foundation = ACCEPTED（DEC-055）；深 TaskWorkbench、Primitive / Styling、私有投影、revision-safe Autosave / Diff、Accessibility / Browser / Reflow / Performance = ACCEPTED，外层 Router 由 DEC-062 增加 `/tasks` 入口（DEC-056 / 062）。Product Final Consistency Review = PASS，Product Specification 整体闭合已由用户接受；API 主协议与最终 OpenAPI Operation / Schema / state / adoption closure 已由 DEC-063～066 接受，RFC-004 Final Review = PASS，用户已明确接受 RFC-004 整体；物理生命周期与 Fixture 载体仍待 Readiness / Testing Strategy
- **Workflow Runtime:** 独立 PostgreSQL Checkpoint Database、同步 `PostgresSaver`、`sync` durability、可重入 Node 与 Current-Truth-first Reconciliation = ACCEPTED（DEC-049 / RFC-003）；PostgreSQL Work Intent + Poll-and-claim、数据库权威 Lease / Heartbeat / Fencing Token、协作式 Cancellation / Supersession + Commit Fence = ACCEPTED（DEC-050 / RFC-003）；显式 Compatibility Tuple、Current-Truth-first 七动作 Recovery Decision、受控迁移、Forward Repair 与风险切片证据边界 = ACCEPTED（DEC-051 / RFC-003）。精确实施版本、最终公共字段与运维参数仍待实施证据、RFC-004 / 007
- **LLM Runtime:** OpenAI Responses API + `gpt-5.6-terra`、typed sync Port、Adapter 隔离、Strict Output → 项目 Schema → Domain Validator、有界 Recovery、可读 Version Tuple、五个固定 Profile、确定性 Context Assembly、Adapter Secret / Payload Allowlist、同 Port Scripted Substitute、断网三层 Contract Tests 与单次人工 RC Smoke = ACCEPTED（DEC-052～054 / RFC-006）；精确实施版本、Token / Timeout 与实际 Provider 兼容性仍待实施证据
- **允许工作:** 最小 RFC-007、快速 MVP-0 测试 / 开发 / Goal 文档、精简 Readiness Review 与一致性 Review
- **禁止工作:** Business / Production Implementation、Spike / Live Provider、依赖安装、公开部署、实际 Goal 启动
- **用户 Goal 指令:** 未下达
- **Agent 路由:** Luna/max 为首选实现 Agent；当前工具不能创建 Luna 时，可输出外部 Luna 任务包或显式使用 Terra/xhigh 回退，不因 Luna 暂时不可用单独阻塞 Goal，但必须保持任务合同、实际模型披露和 Review 独立性

---

## 状态变更规则

- `CONDITIONALLY READY` 只表示允许完成快速 MVP-0 策划，不表示业务实现已就绪。
- 只有上面的快速 Gate 前置条件满足、完整快速策划包已展示、精简 Implementation Readiness Review 通过且用户明确批准“进入 MVP-0 Goal”后，才可将状态改为 `READY FOR MVP-0` 并激活 Goal。
- 任何必需条件未满足，Business / Production Implementation 保持 `NOT AUTHORIZED`。
- 状态变更须在 [../decisions/decision-log.md](../decisions/decision-log.md) 记录或在审查文件中留痕。
