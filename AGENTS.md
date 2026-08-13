# AGENTS.md

本文件是 AI Ecommerce Agent 项目的协作者入口规范。任何进入本仓库的 Agent 都必须先阅读并遵守本文件，再处理项目文件。

---

## 1. 当前阶段

- **项目名称：** AI Ecommerce Agent
- **当前阶段：** MVP-0 Fast Lane FL-2 Terminal `GOAL_BLOCKED` and Post-FL-2 Reconciliation
- **开发状态：** ACTIVE / `GOAL_BLOCKED` — FL-1 deterministic browser-to-backend loop 与 one-command local demo 已完成；[PR #271](https://github.com/JettxonHo/ai-ecommerce-agent/pull/271) 已按 [DEC-079](docs/decisions/dec-079-deepseek-v4-pro-mvp0-real-provider-amendment.md) 合并 direct DeepSeek official `deepseek-v4-pro` private adapter、项目 Schema / bounded Domain admission 与 opt-in smoke seam，[PR #280](https://github.com/JettxonHo/ai-ecommerce-agent/pull/280) 已将 DEC-080 的 Xiaohongshu v2 deadline-fence repair 离线合并，[Issue #274](https://github.com/JettxonHo/ai-ecommerce-agent/issues/274) 的 bounded legacy cleanup 也已合并完成。2026-08-13 的首次受控 smoke 在 `main@1c7c2107ead332235d492ed063b67101784d35f1` 完成五次调用后安全失败；随后 [Issue #281](https://github.com/JettxonHo/ai-ecommerce-agent/issues/281) 在 exact `main@ac4edfed6e8e216e9938affdc734298c8630d2de` 执行第二次受控 smoke，仅发生 `product_intake_v1 / v1` 一次调用即在 `awaiting_review` 前以固定安全 HTTP 500 终止。两次均不是 live acceptance。#281 授权已消耗且 Issue 已关闭，不再授权第三次或额外 Provider 调用；Goal 继续为 `GOAL_BLOCKED`。旧 [MVP-0 Goal](docs/goals/end-to-end-demo-mvp0-goal.md) 的已完成工作保留，剩余横向 Backlog 不再自动执行。
- **最小目标：** 固定本地工作区中完成 Task 创建 → 一份粘贴文本/TXT/Markdown 输入（最大 1 MiB）→ Facts → Insight → Positioning → Marketing Brief → Xiaohongshu Brief → 一次 Review → Markdown 导出；direct DeepSeek V4 Pro proof 已以两次受控失败结束并保持 `GOAL_BLOCKED`，当前不授权新的 Provider 调用。
- **当前事实：** 仓库已有 Task/Source 持久化、Durable Dispatch 与 Model Runtime seams、五类 output contracts、安全 Markdown renderer、FastAPI fixed-workspace business routes、authored OpenAPI、generated client、Task gateway、`/tasks` list/create/read routes、Task-scoped input/result/review/export、Workbench projection、deterministic scripted pipeline、private DeepSeek adapter / opt-in smoke seam 与 real-backend Chromium coverage；`scripts/mvp0/demo` 提供固定 PostgreSQL + API + Vite 的前台本地启动路径。OpenAI/Qwen provider-specific legacy adapters、direct tests、live handoffs 与 provider-only guard 已按 Issue #274 remove-now inventory 删除；共享 `_live_evidence.py`、DeepSeek 路径与 provider-neutral seams 保留。OpenAI SDK `2.53.0` 仍由 DeepSeek 使用并保留。DeepSeek 现有两次相互独立的受控失败证据，没有 live acceptance；第二次 #281 授权已消耗并关闭。
- **当前 Gate：** FL-2 已得出 terminal `GOAL_BLOCKED` result。首次五调用 smoke 的第五阶段记录 12,288 output tokens 与 136,622 ms latency，触及历史 Xiaohongshu v1 的 token/time 边界；第二次 #281 smoke 只调用 `product_intake_v1 / v1` 一次，记录 input 2,353 / output 8,192 / total 10,545 tokens 与 106,434 ms latency，并在 120 s 内以固定安全 HTTP 500 停止。8,192 恰等于第一阶段上限只是诊断线索；脱敏 evidence 不含 finish reason、raw response 或内部错误类别，不能将其写成已证明根因。两次 retry/recovery 均为 0，第二次所有行为 Gate 为 false 且没有 stage 2～5 调用。当前不授权任何后续 Provider run；新 repair、Provider 或产品方向必须由新的用户 Decision 与独立合同授权。Secret 不得进入聊天、GitHub、source、logs、CI 或 evidence。JSON/CSV/PDF/图片、完整 Retrieval/Evidence、分布式 Worker/Checkpoint Recovery、高级 Review/Diff、完整 API catalog、Auth/Multi-tenant/Public Deployment 均后移。
- **质量方向：** 严格执行 DEC-039。保留外部输入、scope、SQL、原子提交、XSS/Markdown、same-origin、幂等与 Secret 边界；停止新增没有已复现风险的 AST scanner、精确私有目录、sole-consumer、类型子类或 every-field 穷举测试。

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

- 一个实现线程原则上只处理一个边界清晰的 Issue，或一组高度相关且写入边界不冲突的 Issues。
- Fast Lane Issue 必须交付用户可观察的纵向结果。没有同一纵向或紧邻下一纵向真实消费者的 DTO、Protocol、Facade、Repository、Schema 或架构守卫不得成为独立 Issue。
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
