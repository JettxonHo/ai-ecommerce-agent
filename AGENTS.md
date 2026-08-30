# AGENTS.md

本文件是 AI Ecommerce Agent 项目的协作者入口规范。任何进入本仓库的 Agent 都必须先阅读并遵守本文件，再处理项目文件。

---

## 1. 当前阶段

- **项目名称：** AI Ecommerce Agent
- **当前阶段：** [DEC-087](docs/decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md) 已在 `main` 生效：MVP-0L 为 `TERMINAL_INCOMPLETE_L5_FAILED`、Real Product-to-Brief Pilot 为 `ACTIVE`。Issue #341 / PR #342 已合并，P01–P08 为 `ADMITTED`、denominator exact 8 frozen、P0 为 `P0_CONTRACT_FROZEN`、P1 为 `READY_NOT_STARTED`。Issue #343 当前分支推进 P1 provider-free characterization；本分支状态为 `P1_CHARACTERIZATION_IN_PROGRESS`，精确 disposition 仅在本 PR 到达 `main` 后成为 merge-effective truth。
- **开发状态：** MVP-0L L0–L4 accepted evidence remains preserved. L5 [Issue #335](https://github.com/JettxonHo/ai-ecommerce-agent/issues/335) / [PR #336](https://github.com/JettxonHo/ai-ecommerce-agent/pull/336) is terminal `L5_REAL_AI_ACCEPTANCE_FAIL_NO_EXPORTS` at exact head `2210d68ad6e09e1a402dd63b0cd9b2a52cdfe74f`: five ordered `deepseek-v4-pro` calls with retry/recovery `0/0`, confirmed result true, export gates false, UTF-8/download false and no export files. Its authorization is consumed; no further Provider run is authorized. L6 is `NOT_EXECUTED`; Agent UI remains frozen. The historical Fast Lane remains `GOAL_BLOCKED`, and `P5_REUSE_FROZEN` remains unchanged.
- **最小目标：** preserve the working deterministic/local foundation and maintain the bounded Real Product-to-Brief business Pilot. Issue #343 performs only the exact seven-path P1 provider-free characterization workflow: no Pilot observation or execution, no MVP0L repair, L5 retry, L6, Agent UI, Provider/Secret action or runtime.
- **当前事实：** the repository has Task/Source persistence, fixed-workspace routes, generated client, Workbench projection, deterministic scripted pipeline and local demo path. Issue #318 provides the real PostgreSQL-backed Needs Input read/resolve boundary, current-request projection, bounded recovery reconciliation and the existing Web one-page Intake consumer without changing OpenAPI/generated types. Issue #329's test-only characterization proves the existing Task primary input, generated/confirmed Marketing and Xiaohongshu results, and both immutable Markdown export snapshots survive recomposition/replay and a materially newer fictional input; stale revision/idempotency replays remain rejected with `409` before and after recomposition. Acceptance uses fictional/sanitized data only. Native macOS App/WebView, signing/notarization, login/RBAC/multi-user/public deployment and Keychain/Secret UI are Deferred. Intel support is Deferred; excluded from the first release. The later project-root Git-ignored `.env` convention is accepted; outside the single owner-authorized L5 run, no Stage may create/read/inspect it or any Secret, and no Secret value is retained in repository/evidence material.
- **当前 Gate：** Issue #343 is the single P1 characterization Issue. Its exact seven-path PR must preserve the accepted DEC-086/087, Pilot Contract and P0 freeze semantics, add no eighth path, and must not claim a run, numerator, Pilot outcome or Goal completion. No production source, public contract/generated client, migration/schema, dependency/lockfile, runtime, Provider/model call, Secret access, native App, public deployment or Spider_XHS action is authorized.
- **Pilot Gate：** [Real Product-to-Brief Pilot Goal](docs/goals/real-product-to-brief-pilot-goal.md), its [Pilot Contract](docs/product/real-product-to-brief-pilot-contract.md), and the [P0 admission/contract-freeze plan](docs/product/real-product-to-brief-pilot-p0-plan.md) retain the exact **P0 → P1 → P2 → P3 → P4 → P5 → P6** order and accepted denominator. Issue #341 / PR #342 is merge-effective: P0 is `P0_CONTRACT_FROZEN`, P01–P08 are `ADMITTED`, denominator exact 8 is frozen, and P1 is `READY_NOT_STARTED` before this PR. On this branch P1 is `P1_CHARACTERIZATION_IN_PROGRESS`; the report's exact disposition (`CONFIRMED` / `NOT_REPRODUCED` / `INCONCLUSIVE`) becomes merge-effective only after this PR reaches `main`. `PILOT_EXECUTION_AUTHORIZATION=NOT_AUTHORIZED` in both states.
- **质量方向：** strictly apply [DEC-039](docs/decisions/dec-039-proportional-validation-and-review-governance.md): representative behavior, boundary and required-check evidence proportional to risk; do not add speculative defensive test matrices.
- **前端产品方向：** the accepted A+C baseline is Chinese-first “运营编辑部 / 策略桌”: stable business/status reading order, wide-desktop horizontal five-stage rail, one dominant action, progressive disclosure, Context Rail and 1024/320 reflow. Issue #303, #305 and #247 are merged/current P1–P3 deliveries; Issue #308 reconciles the real-backend harness and Issue #310 records the predecessor journey. Issue #318 keeps the one-page authority-first Needs Input panel before the existing Intake editor and records a 4/4 real-backend recovery/reload pass; Issue #329 changes no UI and records only backend persistence evidence, including the restored stale revision/idempotency fences. No modal, wizard or new page was added.

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

[DEC-082](docs/decisions/dec-082-local-single-user-action-workbench-and-kimi-frontend-routing.md) 对 DEC-071 / 072 增加一个窄例外：本机 Kimi Code + Kimi K3 只有在用户已接受的精确前端设计或实现合同下才能处理合同内前端文件。它不是 Luna / Terra 的默认回退，不授权后端、Provider、Secret、PostgreSQL、migration、OpenAPI、公开部署、认证或多租户；请求配置证据与运行时身份必须分开记录。重要前端设计必须使用适用 taste skills。Kimi 产出的变更不得自我批准或合并，仍由 Sol `ORCHESTRATOR_REVIEWER` 独立五轴 Review 和判断合并。Issue #291 本身不授权 Kimi model call。

[Issue #339 owner routing amendment](https://github.com/JettxonHo/ai-ecommerce-agent/issues/339#issuecomment-5461745399) adds one narrower docs-only exception: requested dispatch configuration `gpt-5.6-sol` / `xhigh`, logical role `SOL_DOCS_IMPLEMENTER`, for the exact 13-path rebaseline only. No separate runtime identity is inferred. The implementer cannot independently review, approve or merge this PR, and the exception creates no Sol fallback for later Issues.

子 Agent 完成任务后必须及时关闭，避免占用并发与上下文资源；只有存在立即开始、范围明确的同一任务 follow-up 时才可短暂保留。

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

- 用户已向主开发 / 操作 Session 提供普通、可逆且合同内本地操作的长期预授权，包括只读诊断、fresh isolated clone / worktree、测试 / build / static checks、临时文件 / cache、有界本地 Docker / PostgreSQL / API lifecycle、evidence path setup 与合同要求的 cleanup；应合并并尽量减少重复的语义审批请求，但平台强制 approval card 仍可能需要一次机械点击。此预授权绝不扩大 Issue / Task Contract，也不授权额外或已消耗的 Provider run、付费调用、Secret / raw provider material 访问、广泛或破坏性数据操作、公共契约 / migration / 产品方向变更、模型角色回退或绕过 stop condition。
- 一个实现线程原则上只处理一个边界清晰的 Issue，或一组高度相关且写入边界不冲突的 Issues。
- Productization Stage Issue 必须交付用户可观察的结果。没有同一 Stage 或紧邻下一 Stage 真实消费者的 DTO、Protocol、Facade、Repository、Schema 或架构守卫不得成为独立 Issue。
- 任务合同保持短而完整：目标、范围/非范围、真实边界、验收、相关测试、停止条件、文件所有权与 Reviewer。不得把精确 SHA 链、人工 LOC 算术、重复模型状态口号或穷举变体矩阵作为常规接受条件。
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
- **用户已提供长期 Goal 持续执行授权（DEC-072）；DEC-084 的 L0 文档 Gate 合并后，后续 L Stage 可按精确合同持续执行，不要求重复固定口令**
- 已通过 Implementation Readiness Review 并再次获得用户批准

仓库已经包含经授权完成的 deterministic local foundation，不能再使用“不得出现 backend 目录”作为状态判断。L0 不新增业务实现；L1 及后续 Stage 只能在各自精确合同、独立 Review 和人工 Gate 边界内推进，不得擅自新增 Provider、公共契约、migration、依赖或部署能力。Apple Silicon 是首发硬边界；Docker Desktop 由用户安装；本地 Web 使用系统默认浏览器。

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
