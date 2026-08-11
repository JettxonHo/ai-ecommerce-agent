# Implementation Readiness（开发就绪状态）

> **Status: READY FOR MVP-0 — ACTIVATION AUTHORIZED**
>
> Foundation、Product Specification、RFC-001～007、Development Plan、Testing Strategy、MVP-0 Goal 与精简 Readiness Review 已接受。Business / Production Implementation 已在 Active Goal 与有界 Issues 内授权。
>
> **Current Gate（2026-08-12；实现基线 `main@544fe9865a318737636f4cd59e4705261d833494`，PR #218 merge）：** MVP-0 Goal 已激活并由用户明确恢复执行；M1 与 Task Management vertical slice 已交付，Source persistence slices through PR #155 仍是 Source 的实现边界。#81（Source）与 #82（Review / Brief / Export）仍 OPEN；P-87A/P-88A/P-89A 与 P-82A～P-86A 均保持 Proposed/pending，registration/intake、submitted-input/content storage classification、Source intake OpenAPI adoption、parser/retrieval/evidence runtime、Review lifecycle/schema 与 complete outcomes 仍未实现。Durable Dispatch 已合并 bounded claim/lease/heartbeat、cancellation/supersession controls 与 public completion contracts；Issue #190 仍 OPEN，fresh direct authorization for forward-only `0006` migration and completion-result persistence/participant 尚未满足，不能声称 final cross-module Commit Fence 或 Business Current Truth commit。Workflow 仅有 provider-neutral checkpoint header seam（PR #192）。Model Runtime 已合并 provider-neutral Port/contracts、scripted substitute、structured-output/schema compatibility、request preparation、response mapping、one-attempt execution 与 bounded transport retry（PR #194/#196/#198/#201/#202/#204/#206/#208），但 profiles/context/prompt/client factory/full adapter/recovery/ledger/live Provider evidence 仍未实现。MVP0-025～029 的五个 module-private provider-neutral candidate output contracts（PR #210/#212/#214/#216/#218）是 output-only prerequisites，不是完整 Skill verticals。M7 仍为 no-API foundation；业务路由、generated client、API-backed Workbench 与其他 Web slices 仍未实现。高风险事项仍按 DEC-072 暂停并请求人工确认。

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
- [x] 最小 RFC-007（日志、correlation、有限 timeout / retry / backoff、错误与 Secret redaction；无完整 telemetry platform）已接受（DEC-073）
- [x] P-71A HTTP Adapter、P-72A local stack、P-73A Worker process 方案已接受（DEC-074）
- [x] 关键 Agent、Workflow、Human Review 与 Skill 边界已确认
- [x] Retrieval / Evidence 与 Skill 的概念职责已确认
- [x] 外部 Skill 供体的 Adapt / Reference 策略已确认
- [x] 必要 RFC 已完成（RFC-001～007 Accepted）
- [x] 关键 Decision Records 已完成（DEC-001～077）
- [x] PRD 和架构文档已同步
- [x] 最终公共数据契约、API 与状态 / 错误映射已明确；物理 OpenAPI 由 Goal Issue 交付
- [x] 完整测试与验收标准已存在；Fixture 与 E2E 物理载体由 Goal Issues 交付
- [x] 开发前 Current Truth 文档不存在已知阻塞冲突
- [x] 快速 MVP-0 Gate 已确认：完整 ARP-02 / 03 / 09、ARP-05～08、TS-02 / 04 / 05 不再阻塞 MVP-0，进入 MVP-1 / 对应风险 Gate
- [x] TS-01 / TS-03 的 stop-first bounded compatibility slice 已写入 Proposed Goal 的 `MVP0-004 / MVP0-005` Foundation compatibility task contracts（不先建设大型独立 Spike）
- [x] MVP-0 Development Plan、Testing Strategy 与 Goal 完整 Draft 已存在
- [x] MVP-0 Development Plan、Testing Strategy 与 Goal 文本已接受（DEC-075）
- [x] 已确认实现路由与独立 Reviewer：使用准确的自定义 Agent `luna-worker`（配置 `gpt-5.6-luna` / `max`）；不可用时阻塞新的实现任务并报告，不自动回退 Terra（DEC-071）
- [x] 已通过 Implementation Readiness Review，并由用户整体接受（DEC-075）
- [x] 用户已通过 DEC-072 提供所有 Gate 闭合后的长期 Goal 持续执行授权；无需重复固定口令

---

## 当前状态

- **Architecture Readiness:** READY FOR MVP-0
- **Development Status:** AUTHORIZED WITHIN ACTIVE MVP-0 GOAL
- **Spike-001:** COMPLETED
- **RFC:** RFC-001～007 = ACCEPTED；RFC-007 由 DEC-073 接受
- **Foundation:** FND-001 / FND-002 / FND-003 = COMPLETED
- **Wave 1 Artifact:** ARP-01 / 04 / 10 完整 Accepted；ARP-02 / 03 / 09 仅 TS-01 Minimum Slice Accepted
- **产品交互与验收:** 单任务工作台、确认式局部重跑、输入门禁、审核 / Brief / Evidence / Recovery / Markdown 导出 = ACCEPTED（DEC-044～048）；产品 / 技术权威边界、虚构 Anchor SKU、有限结构化 Needs Input、证据约束声明完整性、Task 范围资料与可逆移除、最小最近任务入口 = ACCEPTED（DEC-057～062）；前端应用 / 状态 / Contract Generation / Verification Foundation = ACCEPTED（DEC-055）；深 TaskWorkbench、Primitive / Styling、私有投影、revision-safe Autosave / Diff、Accessibility / Browser / Reflow / Performance = ACCEPTED，外层 Router 由 DEC-062 增加 `/tasks` 入口（DEC-056 / 062）。Product Final Consistency Review = PASS，Product Specification 整体闭合已由用户接受；API 主协议与最终 OpenAPI Operation / Schema / state / adoption closure 已由 DEC-063～066 接受，RFC-004 Final Review = PASS，用户已明确接受 RFC-004 整体；authored OpenAPI 与虚构 Fixture 物理载体已由 M1 交付；MVP0-036 已交付 no-API Web foundation shell 与 shell Browser smoke，API-backed / business Browser E2E 仍待后续里程碑
- **Workflow Runtime:** 独立 PostgreSQL Checkpoint Database、同步 `PostgresSaver`、`sync` durability、可重入 Node 与 Current-Truth-first Reconciliation = ACCEPTED（DEC-049 / RFC-003）；PostgreSQL Work Intent + Poll-and-claim、数据库权威 Lease / Heartbeat / Fencing Token、协作式 Cancellation / Supersession + Commit Fence = ACCEPTED（DEC-050 / RFC-003）。已合并 Durable Dispatch bounded claim/lease/heartbeat/control/completion seams 与 provider-neutral checkpoint header；但 Issue #190 的 completion migration/participant、完整 compact state/node graph、Worker、resume/recovery 和 E2E 仍未实现；最终公共字段与运维参数继续受 RFC-004 / 007 约束
- **Source / Evidence foundation:** Source persistence slices through PR #155 are merged at the PR #155 Source implementation baseline (merge `cd6bd02fc09a6698d4991dda671131ce03217bcf`): #109～#113 catalogs/snapshots, SourceVersion/processing and association domains, typed ports and single-head `0003_source_evidence`; #121/#124/#126 SQLAlchemy Core tables/mappings, PostgreSQL repositories and specialized UoW/factory; #128/#130 processing application contracts/service/CAS composition; #151/#153 Source-owned association remove/replace contracts/service; and #155 additive immutable no-commit SourceVersion/processing and Task-owned association reads. #81 仍为 OPEN tracking parent，M2 仍为 PARTIAL；registration/intake、submitted-input/content storage classification、final RFC-005 Source HTTP/wire DTOs or API/generated client、parser/fragment/retrieval/evidence remain unimplemented；`0003_source_evidence` 的 minimal schema 不是 final intake schema。#82 仍为 OPEN；P-82A～P-86A remain Proposed/pending, and Review lifecycle/schema plus complete outcomes remain unimplemented
- **LLM Runtime:** OpenAI Responses API + `gpt-5.6-terra`、typed sync Port、Adapter 隔离、Strict Output → 项目 Schema → Domain Validator、有界 Recovery、可读 Version Tuple、五个固定 Profile、确定性 Context Assembly、Adapter Secret / Payload Allowlist、同 Port Scripted Substitute、断网三层 Contract Tests 与单次人工 RC Smoke = ACCEPTED（DEC-052～054 / RFC-006）；当前只实现 provider-neutral Port/contracts、scripted substitute、structured-output/schema compatibility、request preparation、response mapping、one-attempt execution 与 bounded transport retry（PR #194/#196/#198/#201/#202/#204/#206/#208）；五个 calibrated profiles、真实 Skill prompts/context、composition-root Secret/client factory、full public adapter、recovery orchestration、call ledger 与 live Provider evidence仍待实施证据
- **Candidate output seams:** MVP0-025～029 分别合并 module-private provider-neutral candidate schema/facade（Product Intake、Customer Insight、Product Positioning、Marketing Brief、Xiaohongshu mapping；PR #210/#212/#214/#216/#218）。它们只提供 output-only prerequisites；未实现真实 context/prompt、Domain Validator、Evidence Link/Current Truth commit、node、persistence、API 或 E2E，因此不得写成完整 Skill vertical 或 live capability
- **Planning Package:** Development Plan / Testing Strategy / Goal / Readiness Review = ACCEPTED；P-71A / P-72A / P-73A = ACCEPTED
- **允许工作:** Active Goal 内的 Issues、实现、测试、PR、独立 Review 和普通低风险合并
- **禁止工作:** Goal Non-goals、公开部署、未经 Issue 授权的 Live Provider / Spike、不可逆或高风险操作
- **用户 Goal 指令:** 用户已明确确认“进入 Goal 执行阶段”；Goal = ACTIVE
- **Agent 路由:** 边界明确的实现使用准确名称 `luna-worker`；每次创建前记录配置与运行时验证状态。不可发现时输出 `BLOCKED_LUNA_WORKER_UNAVAILABLE` 并停止新的实现任务；未经用户对具体任务明确许可，不得改用 Terra。任务合同、实际模型披露和 Review 独立性继续为硬约束

---

## 状态变更规则

- `READY FOR MVP-0` 只授权 Accepted Goal 和当前 Issue 合同范围，不扩大产品范围。
- 高风险人工 Gate、停止条件和 Non-goals 继续有效。
- 每个实现 PR 仍必须独立测试、Review 和验收；Goal 完成后执行统一最终 Review。
- 状态变更须在 [../decisions/decision-log.md](../decisions/decision-log.md) 记录或在审查文件中留痕。
