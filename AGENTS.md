# AGENTS.md

本文件是 AI Ecommerce Agent 项目的协作者入口规范。任何进入本仓库的 Agent 都必须先阅读并遵守本文件，再处理项目文件。

---

## 1. 当前阶段

- **项目名称：** AI Ecommerce Agent
- **当前阶段：** MVP-0 Goal Activation and Development
- **开发状态：** ACTIVE — RFC-001～007、Development Plan、Testing Strategy、MVP-0 Goal 与 Readiness Review 已接受；PR #59 已合并，正在 Goal / Issue 合同范围内持续开发。详见 [docs/handoffs/implementation-readiness.md](docs/handoffs/implementation-readiness.md)。
- **已确认基础：** 主要用户为中小电商商家的商品运营与内容运营人员；核心任务为商品上新定位分析与 Marketing Brief；统一 Ecommerce Agent + 确定性 LangGraph StateGraph；4 个 Core Skills + 1 个小红书 Adapter；Task / Fact Stage 最低门禁、默认文件限制与分级冲突处理；Review / Brief 产品语义组、正式对象版本、Review Draft revision 与导出快照；渐进式证据、编辑影响、阶段进度、行动导向恢复与导出确认；Needs Input 使用由真实阻断派生的有限结构化行动请求；验收使用虚构“城市通勤双肩包”Anchor SKU 的三个资料变体 + 一个变更脚本、行为硬门禁 + 人工可用性判断，以及 Markdown-first 用户导出；产品语义与公共 HTTP / Retrieval / Observability / 测试物理载体的权威边界已冻结；声明完整性采用证据约束并禁止通用合规引擎，用户资料默认 Task-scoped 并只提供可逆移除 / 替换，固定工作区提供最小最近任务入口与稳定深链；生产 Checkpoint 已冻结为同 PostgreSQL Service 下的独立 Database + 同步 `PostgresSaver`，并采用可重入 Node 与 Business-Current-Truth-first Reconciliation；Durable Dispatch 已冻结为 PostgreSQL Work Intent + Poll-and-claim，Worker 使用数据库权威 Lease / Heartbeat / 单调 Fencing Token，运行中取消采用持久化协作式取消 + Commit Fence；显式 Compatibility Tuple、Current-Truth-first 七动作 Recovery Decision、受控迁移和 Forward Repair 证据边界已冻结；单一 OpenAI Responses Provider、窄型同步 Model Runtime Port、Structured Output、有界 Recovery、可读 Version Tuple、固定 Profile、Adapter Secret / Payload 边界、确定性替身与单次人工 RC Smoke 已冻结；Frontend Architecture P-36～P-41 及整体已接受：`apps/web/` React 19 + TypeScript + Vite 8 SPA、显式状态所有权、OpenAPI 类型生成、一个深 TaskWorkbench、Native / 按需 Radix + CSS Modules、私有 WorkbenchProjection、revision-safe Autosave / Diff、WCAG / Desktop Chrome / Reflow 与 Evidence-driven Performance；RFC-004 DQ-01～10 已由 DEC-063～066 接受：Contract-first `/api/v1`、窄 Resource + typed Command、语义 revision / 项目定义 Idempotency-Key、耐久 Receipt + Run Monitor、窄 Task / Recovery / Review、不可变 Brief / Export Snapshot、有限 RFC 9457 Problem Catalog、server-bound fixed Workspace + loopback same-origin transport，以及最终 Operation / Schema / state catalog、有界窗口、additive compatibility、generated-client adoption 与 Contract Tests；RFC-005 DQ-01～03 已由 DEC-067 接受：版本化 Source / Task Association、逐资料耐久处理、六值 processing lifecycle、格式感知 Fragment / Locator，以及不使用 Evidence Package `package_hash` 的可读重现边界；DQ-04～06 已由 DEC-068 接受：PostgreSQL-native derived retrieval plane、filtered exact NN、单一版本化 OpenAI Embedding Profile、immutable index generation、确定性 Direct-first Planner、RRF、4 / 20 / 60 / 12 seed bounds 与首 Goal 无 LLM rewrite / baseline reranker；DQ-07～09 已由 DEC-069 接受：server-derived SQL authorized candidate relation、窄 Source / Evidence 投影与 cursor、immutable RetrievalRun + referenced EvidencePackage、DatasetStatistic / Formal Evidence atomic commit、代表性评测硬门禁与显式降级；RFC-001～006 与 FND-001 至 FND-003 已完成；Wave 1 Readiness Artifact 已按各自声明范围接受。
- **已闭合事项：** P-68A～P-70A 与 RFC-007 整体（DEC-073）、P-71A～P-73A（DEC-074）、Development Plan / Testing Strategy / Goal / Readiness Review（DEC-075）均已接受。完整 ARP-02 / 03 / 09、ARP-05～08、TS-02 / 04 / 05 不再阻塞 MVP-0，进入 MVP-1 / 后续风险 Gate。
- **当前 Gate：** M1 Contract & Compatibility 已完成：Issues #63～#67 全部关闭，PR #69 / #70 / #71 / #72 / #74 已合并；authored OpenAPI、虚构验收资料、local PostgreSQL、TS-01 与 TS-03 均形成可复核证据，两个 stop-first Slice 均为 PASS，但不等于生产业务模块已实现。M2 的 Task Management vertical slice 已完成：#77 / #78 / #79 与 tracking parent #80 已关闭；#80 的七个子 Issue（#87 / #90 / #91 / #88 / #95 / #98 / #89）均已关闭，PR #84 / #85 / #86 / #92 / #93 / #94 / #96 / #97 / #99 / #100 均已合并，Task / Run / Stage 的 migration、adapter、application 与 CAS 证据已通过。首个 Source foundation wave 也已完成：Issues #109～#113 已关闭，PR #114～#118 已合并，当前 main 为 `5415411`；A1 catalogs/snapshots、A2 SourceVersion/processing domain、A3 association domain、A4 typed ports，以及单一 `0003_source_evidence` Alembic head 与 real PostgreSQL migration evidence 已交付。该 wave 仍只覆盖 catalogs/snapshots、domain、ports 与 migration：ORM mappings、concrete repositories/UoW/bootstrap、application registration/read、application/persistence processing CAS、Source-owned atomic remove/replace participant、parser/fragment/retrieval/evidence、HTTP/API、Worker、Provider 与 Web UI 均未实现；submitted-input metadata 仍 deferred/additive，minimal identity schema 不是 final intake schema。#81 仍为 OPEN tracking parent，M2 仍为 PARTIAL；#82 仍为 OPEN，既有 migration-head 与 typed transaction-participant prerequisites 不变。M7 当前为 PARTIAL：MVP0-036 Web Foundation 已由 PR #104 合并（merge `adcc38f`），提供 React/Vite no-API shell、锁定工具链与确定性 Web checks；业务路由、generated client、API-backed Workbench 和其他 M7 slices 仍未实现。用户已于 2026-08-09 接受 P-74A～P-81A，并由 DEC-076 / DEC-077 冻结 Source、Review / Brief / Export 的实现所有权与原子边界；Goal 已恢复执行。不得声称 Source foundation 之外的 Source / Review / Brief / Export / Runtime / API / Provider 或 Web 业务能力已实现；继续按独立 Issue 和任务合同实现，Technical Spike / Live Provider 仅在相应 Issue 明确授权的受控边界内执行。

---

## 2. 协作角色

| 角色 | 职责 |
|------|------|
| **用户** | 项目所有者与最终决策人。接受、修改、否决或暂缓 Decision / RFC；批准范围变化、高风险操作、Goal 激活与发布条件。 |
| **主控与审阅 Agent** | GPT-5.6 Sol、`xhigh`，逻辑角色 `ORCHESTRATOR_REVIEWER`；负责策划、架构、复杂拆分、任务合同、调度、复杂诊断和 PR / 阶段 / Goal Review。 |
| **代码实现 Agent** | 自定义 Agent `luna-worker`，配置模型 GPT-5.6 Luna、`max`，逻辑角色 `IMPLEMENTER`；仅在规格冻结并进入 Goal 后，按单一 Issue 和任务合同实现与修复。 |
| **辅助 Agent** | GPT-5.6 Terra、`xhigh`，逻辑角色 `AUXILIARY_IMPLEMENTER`；只有用户对具体任务明确许可时才可参与，不作为 Luna 不可用时的自动或默认实现回退，也不得代替 Sol 作最终裁决。 |
| **文档与 Git 操作者** | 按已授权范围维护文件、Issue、Branch、Commit、PR、测试证据和进度；不替用户接受 Decision / RFC。 |

禁止静默替换模型。创建实现线程必须使用准确的自定义 Agent 名称 `luna-worker`，加载 `~/.codex/agents/luna-worker.toml`；不得用“Luna Max”逻辑角色或单独模型字符串代替。若当前会话无法发现该 Agent，必须输出 `STATUS: BLOCKED_LUNA_WORKER_UNAVAILABLE` 并停止新的实现任务，不得自动回退 Terra。配置已验证、运行时实例模型未暴露时只记录 `CONFIG_VERIFIED`；其余状态见 DEC-072。Sol 直接实现仅限 [DEC-043](docs/decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md) 保留的例外，并必须由独立 Agent 或人工完成最终 Review；最新路由规则见 [DEC-071](docs/decisions/dec-071-luna-worker-exclusive-implementation-routing.md) 与 [DEC-072](docs/decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md)。

详细职责分工见 [docs/governance/collaboration-model.md](docs/governance/collaboration-model.md)。

---

## 3. 文档优先级（冲突时以此为准）

当新旧内容冲突时，按以下优先级裁决，**不得让旧 Session 覆盖新 Decision**：

1. 用户当前明确指令
2. 最新 Accepted Decision（见 [docs/decisions/decision-log.md](docs/decisions/decision-log.md)）
3. 当前产品 / Agent / 架构 / 契约规格（[docs/product/](docs/product/)、[docs/agents/](docs/agents/)、[docs/architecture/](docs/architecture/)）
4. Accepted RFC（[docs/rfcs/](docs/rfcs/)）
5. Product Vision（[docs/product/vision.md](docs/product/vision.md)）
6. Governance 文档（[docs/governance/](docs/governance/)）
7. 历史 Session（[docs/sessions/](docs/sessions/)）
8. 非正式备注

---

## 4. 内容类型（必须严格区分）

在 Session、RFC、Decision 与规格中必须明确标注以下类型，**不得混用**：

- **Fact**：已确认的事实
- **Observation**：讨论中的观察
- **Assumption**：尚未验证的假设
- **Proposal**：建议方案
- **Alternative**：备选方案
- **Risk**：风险
- **Open Question**：开放问题
- **Proposed Decision**：等待用户确认的决定提案
- **Accepted Decision**：用户明确接受的决定

---

## 5. 核心禁止事项

1. **禁止把 ChatGPT 的建议自动视为用户决定。** Proposed Decision 在用户明确接受前一律保持 Proposed。
2. **禁止扩大 MVP 范围。**
3. **禁止擅自选择框架、数据库、模型或第三方服务。**
4. **禁止为了让文档看起来完整而补充未经讨论的事实。** 信息缺失时保留为 Open Question，不得自行补全。
5. **禁止静默删除、覆盖或改写历史决策。** 改变旧决定时，必须保留追踪关系（Supersedes / Amends / 双向链接）。
6. **禁止提前实现。** 在完整策划包、所有重大 Proposal 与精简 Readiness Review 被接受前，不得编写业务代码、接入模型 API、创建生产 RAG、数据库、前后端、迁移、部署或 Docker 配置；代码示例只能视为 Illustrative Example。全部 Gate 闭合后，DEC-072 已提供 Accepted Goal 的持续执行授权，无需重复固定启动口令。
7. **禁止越权降级。** 不得为推进任务而更换已接受的数据库、运行时、Provider、公共契约或质量 Gate；实现路由以 DEC-071 为准，未经用户明确许可不得把 `luna-worker` 自动或默认替换为 Terra，也不得静默替换或错误归因。
8. **禁止隐藏失败。** 不得隐藏失败测试、已知缺陷、Decision Conflict 或未解决风险。

---

## 6. 适度校验与 Review

- 安全、异常、性能与测试校验必须与真实风险、演示边界和核心功能相称。
- 不新增哈希或 SHA-256 要求；只有影响核心功能的重大完整性或安全风险，才允许提交独立提案。既有内容身份概念保持算法中立。
- 有代表性路径和关键不变量已经覆盖后，不反复堆叠基本不可能发生的防御性变体。
- Rubric 辅助专业判断，不作为机械评分或自动接受器。
- 上述约束不取消边界校验、Secret 保护、事务一致性、故障恢复、Required Checks 或关键行为测试。

详见 [DEC-039](docs/decisions/dec-039-proportional-validation-and-review-governance.md)。

---

## 7. Decision 与 RFC 接受权

只有用户的明确批准语义才能把 Proposed Decision 或 RFC 升级为 Accepted，例如：

- 同意
- 确认
- 接受
- 就按这个方案
- 该决策通过
- 其他语义明确的批准表达

ChatGPT 单方面输出的「建议」「推荐」「Proposed Decision」一律不能标记为 Accepted。

---

## 8. Issue、Branch、PR 与 Merge

- 一个 Issue 只交付一个可独立验证的结果；一个 Issue 对应独立分支和 PR。
- PR 必须说明问题、方案、范围、测试、风险、回滚和文档影响。
- 合并前必须完成正确性、可读性、架构、安全、性能五轴 Review；安全与性能按变更相关性执行。
- 可执行代码 PR 原则上由准确名称的 `luna-worker` 实现；Terra 只有在用户对具体任务明确许可时才可实现。实现 Agent 自审不能替代 Sol/xhigh 对实际 Diff 和测试结果的独立五轴 Review。
- 实现 Agent 不得最终批准或合并自己实现的 PR。普通低风险 PR 在验收标准和 Required Checks 全部通过、Sol 无阻塞 Finding 后，可由 Sol 主控或另一非实现 Agent 合并、关闭 Issue 并同步文档。
- Sol 仅在 DEC-043 列出的例外下直接实现；此时必须由另一独立审查 Agent 或人工完成最终批准。
- 破坏性操作、重大架构或公共契约变更、数据迁移、不可逆外部操作、安全事故或核心风险、产品范围变化和 Decision Conflict 必须暂停并请求用户确认。
- 自主 Merge 不等于 Decision / RFC Accepted，也不等于 Goal 已启动或最终发布获批。

详见 [DEC-040](docs/decisions/dec-040-autonomous-agent-execution-and-model-roles.md)。

### 8.1 任务合同与线程隔离

- 一个实现线程原则上只处理一个边界清晰的 Issue，或一组高度相关且写入边界不冲突的 Issues。
- Sol 路由任务前必须提供任务合同：模型 / 角色、目标、权威文档与阅读顺序、范围、Non-goals、依赖、允许修改边界、冻结契约、验收、测试、风险、停止条件、PR 与独立 Reviewer。
- 并行任务必须先冻结接口、依赖和文件 / 模块所有权；不得让多个实现线程无边界地修改同一核心模块。
- 不假设线程自动共享上下文。重要事实必须写入项目文档、权威 Goal、GitHub Issue、任务合同、分支、Commit、PR、Review、Readiness / Current Status、Decision Log 或测试记录。
- 聊天记录不是项目事实的唯一来源；Issue 不替代 Decision / RFC / Spec，PR 描述不替代实际代码 Review。

详见 [DEC-043](docs/decisions/dec-043-sol-luna-terra-multi-agent-development-orchestration.md)、[DEC-071](docs/decisions/dec-071-luna-worker-exclusive-implementation-routing.md) 与 [DEC-072](docs/decisions/dec-072-long-running-autonomy-and-agent-identity-governance.md)。

---

## 9. 每次归档后的检查要求

每次归档讨论或决定后，负责 Agent 必须自检：

- [ ] Session 已追加本轮讨论（未删除历史，未改变原结论含义）
- [ ] Proposed Decisions 已记入 Session，状态保持 Proposed，未被写成 Accepted
- [ ] 用户确认的决定已写入 DEC、更新 decision-log、在 Session 标记为 Accepted
- [ ] 仅在决定被明确接受后才更新 Current Truth Layer
- [ ] 未确认内容未写成当前事实
- [ ] 冲突已按文档优先级裁决
- [ ] 与 Session、RFC、Decision 的双向链接已保留
- [ ] 未创建任何业务实现代码
- [ ] 已输出 Archive Result 报告

完整归档流程见 [docs/governance/product-design-protocol.md](docs/governance/product-design-protocol.md) 与 [docs/governance/documentation-rules.md](docs/governance/documentation-rules.md)。

---

## 10. Goal 与开发阶段开启条件

进入开发阶段至少需要全部满足（详见 [docs/handoffs/implementation-readiness.md](docs/handoffs/implementation-readiness.md)）：

- 项目定位、目标用户、核心问题、MVP 范围已确认
- 关键 Agent 边界、RAG 与 Skill 职责已确认
- 开源项目使用方式已确认
- 必要 RFC 已 Accepted、关键 Decision Records 已完成
- PRD 与架构文档已同步、数据契约与验收标准明确
- 文档不存在未同步或冲突部分
- 已展示完整策划结果、文档变更与 Goal 执行计划
- **用户已提供长期 Goal 持续执行授权（DEC-072）；全部重大 Proposal 与 Readiness Gate 闭合后可激活，不要求重复固定口令**
- 已通过 Implementation Readiness Review 并再次获得用户批准

仓库已经包含经授权完成的 Foundation 后端工程基础，不能再使用“不得出现 backend 目录”作为状态判断。在以上条件全部满足前，不得在既有基础上新增业务模块、生产数据库实现、API、Worker、Frontend、LLM / Retrieval Runtime、迁移或部署能力。

Goal 激活后，普通低风险 Issue 可按第 8 节自主推进；触发人工 Gate 时必须停止受影响工作。

---

## 11. 文档目录速览

```
AGENTS.md                                  ← 本文件：协作者入口规范
README.md                                  ← 项目当前事实速览
docs/governance/                           ← 协议、协作模型、文档规则
docs/sessions/                             ← Exploration Layer：讨论历史
docs/rfcs/                                 ← Proposal Layer：重大方案
docs/decisions/                            ← Decision Layer：已接受决定
docs/product/  docs/agents/  docs/architecture/  ← Current Truth Layer
docs/reviews/                              ← 实现就绪审查
docs/handoffs/                             ← 交接与开发就绪
docs/development/                          ← CI 治理、测试策略与开发计划
docs/goals/                                ← 待接受与已激活的长期 Goal
prompts/                                   ← 人机协作提示词模板
```
