# AGENTS.md

本文件是 AI Ecommerce Agent 项目的协作者入口规范。任何进入本仓库的 Agent（包括 Claude、其他开发工具与未来参与实现的执行体）都必须先阅读并遵守本文件，再处理任何项目文件。

---

## 1. 当前阶段

- **项目名称：** AI Ecommerce Agent
- **当前阶段：** Product Discovery（产品探索 / 方案设计 / 决策治理 / 文档固化）
- **开发状态：** NOT READY — 当前禁止编写业务实现代码。详见 [docs/handoffs/implementation-readiness.md](docs/handoffs/implementation-readiness.md)。
- **当前不意味着已确定：** 目标用户、商家端或消费者端、单 Agent 或 Multi-Agent、是否使用 LangGraph、RAG 具体实现、Skill 具体定义、开源底座、最终技术栈、MVP 功能范围。

---

## 2. 协作角色

| 角色 | 职责 |
|------|------|
| **用户** | 项目所有者与最终决策人。接受、修改、否决或暂缓决定；下达进入开发阶段的指令。 |
| **ChatGPT** | 产品讨论主持人、分析者、方案设计者与决策提案者。输出 Discussion、Proposals、Proposed Decisions。 |
| **Claude** | 项目文件维护者、文档归档者、格式校验者与后续实现执行者。创建、更新、归档、校验文件，不替任何一方作出产品决定。 |
| **开发工具** | 仅在文档稳定且用户明确下达实现指令后介入。实现必须以已确认的 Decision 与 Current Specifications 为依据。 |

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
6. **禁止提前实现。** 在用户明确下达开发指令前，不得编写业务代码、接入模型 API、创建 RAG Pipeline、数据库、前后端、部署或 Docker 配置；ChatGPT 给出的代码示例只能视为 Illustrative Example。

---

## 6. 仅当用户明确表达以下语义时，决定才可标记为 Accepted

- 同意
- 确认
- 接受
- 就按这个方案
- 该决策通过
- 其他语义明确的批准表达

ChatGPT 单方面输出的「建议」「推荐」「Proposed Decision」一律不能标记为 Accepted。

---

## 7. 每次归档后的检查要求

每次把 ChatGPT 输出归档后，Claude 必须自检：

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

## 8. 开发阶段开启条件

进入开发阶段至少需要全部满足（详见 [docs/handoffs/implementation-readiness.md](docs/handoffs/implementation-readiness.md)）：

- 项目定位、目标用户、核心问题、MVP 范围已确认
- 关键 Agent 边界、RAG 与 Skill 职责已确认
- 开源项目使用方式已确认
- 必要 RFC 已 Accepted、关键 Decision Records 已完成
- PRD 与架构文档已同步、数据契约与验收标准明确
- 文档不存在未同步或冲突部分
- **用户明确发出「进入开发阶段」指令**
- 已通过 Implementation Readiness Review 并再次获得用户批准

在以上条件全部满足前，仓库中只允许存在文档与模板，**不得**出现 `backend/`、`frontend/`、`src/`、`api/`、Agent 的代码实现、RAG 实现、Docker 配置、数据库迁移或部署配置等业务代码目录。

---

## 9. 文档目录速览

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
prompts/                                   ← 人机协作提示词模板
```
