# Session-001：项目定位、目标用户与核心业务场景

> 本 Session 记录项目初始分析及其后续演化的已接受决定。截至 2026-07-27，用户已接受 **DEC-001**、**DEC-002**、**DEC-003**、**DEC-004**、**DEC-005**、**DEC-006**、**DEC-007**、**DEC-008**、**DEC-009**、**DEC-010**（见「Accepted Decisions」）。
> 本 Session 已完成阶段性正式固化（见文末「Formal Consolidation（阶段性正式固化）」）：产品定位与 MVP 原则层议题收尾，下一阶段转入 Agent 工作流与可靠性架构（Session-002 计划）。
> `Proposal-001`（商品上新运营助手）的核心方向已被采纳——用户（DEC-002）、核心任务（DEC-003）、平台范围（DEC-004）、输入分层（DEC-005）、四层输出主结构（DEC-006）、人机协作审核机制（DEC-007）、分级证据与结论可追溯（DEC-008）、阶段级失效与局部重跑（DEC-009）、三维评价框架（DEC-010）均已确认；但「产品正式名称 / 定位表述」未单独作为决定，各层字段 / 输出格式 / 工作流与数据技术实现仍待讨论。

## Metadata

- Status: Completed（阶段性正式固化完成；项目尚未进入开发，**非** Implemented）
- Date: 2026-07-27
- Topic: AI Ecommerce Agent 项目定位、目标用户与 MVP 核心场景
- Related RFCs: None
- Related Decisions: DEC-001, DEC-002, DEC-003, DEC-004, DEC-005, DEC-006, DEC-007, DEC-008, DEC-009, DEC-010
- Development Status: NOT READY

## Context

项目所有者正在准备 AI 产品经理、AI 项目经理或相关岗位的简历与作品集，希望完成一个具备真实业务场景、Agent 架构和产品设计过程的电商项目。

项目计划允许参考、Fork 或组合 GitHub 上已有的开源项目，以避免重复实现已经成熟的底层能力。

但项目不能只是：

- 修改开源项目名称；
- 替换 UI；
- 更换 Prompt；
- 将通用聊天机器人包装成电商 Agent；
- 堆叠 LangGraph、RAG、Multi-Agent 等技术关键词。

项目需要体现：

- 对电商业务问题的理解；
- 对用户工作流程的理解；
- 对 Agent 能力边界的设计；
- 对开源技术的选择和改造能力；
- 从需求分析到产品、架构、实现和评估的完整过程。

当前仓库已经完成文档治理骨架初始化。在产品定位、MVP、Agent 边界、数据和技术方案得到确认前，不开始开发。

## Goal

本 Session 需要逐步解决以下核心问题：

1. 项目首先服务哪一类用户；
2. 该用户最值得解决的一个核心业务问题是什么；
3. Agent 应完成怎样的端到端任务闭环；
4. 项目的 MVP 应该展示什么，而不展示什么；
5. 怎样使项目既具有真实业务价值，又适合作为简历作品集；
6. 后续技术架构应该由哪些业务需求驱动。

## Non-goals

本 Session 暂不决定：

- 是否正式采用 LangGraph；
- 是否采用 Multi-Agent；
- RAG 的具体框架和向量数据库；
- Skill 的最终技术实现形式；
- 使用哪个 GitHub 仓库作为底座；
- 前端和后端技术栈；
- LLM 模型供应商；
- 部署方式；
- 详细数据模型；
- 具体 UI 页面；
- 是否进行微调；
- 生产级权限、安全和计费系统。

上述问题将在项目定位和 MVP 场景确认后单独讨论。

## Existing Constraints

### Constraint 1：项目用于求职作品集

项目不仅需要可以运行，还必须能够让面试官快速理解：

- 用户是谁；
- 问题是什么；
- 为什么需要 Agent；
- Agent 比普通工作流或聊天机器人多解决了什么；
- 项目所有者具体进行了哪些原创设计和改造。

### Constraint 2：允许使用开源项目

可以：

- Fork 开源仓库；
- 参考其架构；
- 重用框架和基础组件；
- 修改与扩展已有实现；
- 组合多个开源能力。

但必须明确记录：

- 原项目是什么；
- 原项目解决什么问题；
- 保留了哪些能力；
- 删除了哪些能力；
- 新增了哪些业务设计；
- 做出了哪些架构调整；
- 项目所有者的原创贡献是什么。

### Constraint 3：先文档，后开发

在以下内容足够稳定前，不进入实现阶段：

- 目标用户；
- 核心问题；
- MVP 任务闭环；
- 关键输入和输出；
- Agent 职责；
- 数据需求；
- 基本验收标准。

### Constraint 4：MVP 范围必须可控

项目不应一开始同时覆盖：

- 选品；
- 定价；
- 库存；
- 客服；
- 内容生成；
- 广告投放；
- 竞品监控；
- 评论分析；
- 销售预测；
- 商家经营分析。

必须先选择一个核心场景，完成端到端闭环，再考虑扩展。

## Questions to Resolve

### Question-001：首要目标用户是谁？

> **阶段性解决（2026-07-27，DEC-002）：** 用户选择「中小电商商家的商品运营 / 内容运营人员」（B + C 合并）作为 MVP 首要用户。Persona 设计细节（复合 Persona 还是拆分、职责边界、购买者、最高频使用者）仍为 Open Question，见「Open Questions」。

候选：

- A. 中小商家老板
- B. 商品运营人员
- C. 内容运营人员
- D. 用户研究或评论分析人员
- E. 消费者

### Question-002：MVP 应解决哪一个核心任务？

> **已确认（2026-07-27，DEC-003）：** 用户接受候选 A「商品上新定位与营销 Brief」作为 MVP 核心任务方向。候选 B / C / D / E 不标记为永久拒绝，作为后续扩展或参考方案保留（见「Deferred Topics」）。

候选：

- A. 商品上新定位与营销 Brief ← **已接受（DEC-003）**
- B. 用户评论洞察
- C. 商品内容批量生成
- D. 消费者选购推荐
- E. 综合经营诊断

### Question-003：项目的主要评价目标是什么？

> **框架层已确认（2026-07-27，DEC-010）：** MVP 采用「任务质量 + 结果可靠性 + 用户效率」三维评价框架，优先六项指标，**不**把语言流畅度或最终销量作为唯一标准；对应候选 E（以上目标的平衡）方向被采纳。每项指标公式 / 阈值 / 测试方式仍开放。

候选：

- A. 最强的简历展示效果
- B. 最接近真实商业产品
- C. 最容易在较短周期内完成
- D. 最能学习 Agent 技术
- E. 以上目标的平衡 ← **框架层已采纳（DEC-010）**

### Question-004：项目是否需要优先适配某个平台？

> **已确认（2026-07-27，DEC-004）：** 用户选择方案 C「通用能力 + 小红书演示模板」——核心保持平台中立，小红书商品种草作为首个 MVP 演示场景。其他平台支持、小红书模板字段与适配层技术实现仍为 Open Question。

例如：

- 淘宝；
- 天猫；
- 小红书；
- 抖音电商；
- 亚马逊；
- 通用电商，不绑定平台。

## Discussion

### Facts

#### Fact-001
项目所有者希望完成一个与电商业务有关的 Agent 项目，并用于简历和作品集展示。

#### Fact-002
项目所有者倾向考虑 LangGraph、RAG 和 Skill，但这些技术尚未最终确定。

#### Fact-003
项目允许基于 GitHub 开源项目进行改造，不要求从零实现所有基础组件。

#### Fact-004
项目采用 ChatGPT 负责讨论和方案设计、用户负责最终决策、Claude 负责仓库归档和后续实现的协作方式。

#### Fact-005
当前阶段只进行产品探索、决策和文档固化，开发状态为 NOT READY。

### Observations

#### Observation-001
"AI 电商 Agent" 目前仍然是一个过于宽泛的项目名称。电商涉及多个角色：

- 消费者；
- 商家老板；
- 商品运营；
- 内容运营；
- 投放运营；
- 客服；
- 供应链人员；
- 平台运营。

不同角色对应完全不同的 Agent 架构、数据来源和价值指标。

#### Observation-002
"商品分析、内容生成、评论分析、竞品分析" 虽然都与电商有关，但简单地把这些功能放在一起，并不自然构成一个完整产品。项目需要围绕一个具体工作目标组织这些能力，而不是围绕技术模块组织功能。

#### Observation-003
对求职作品集而言，项目范围越大不一定越有价值。一个边界清晰、业务闭环完整、可以评估效果的 Agent，通常比一个包含许多浅层 Agent 的系统更容易解释和验证。

### Assumptions

> 以下假设均**尚未经过用户确认**。

#### Assumption-001
项目初期可能无法接入真实商家的销售后台、广告后台和私有经营数据。因此 MVP 可能需要使用：

- 用户上传的商品资料；
- CSV 评论数据；
- 公开商品页面；
- 公开竞品信息；
- 人工整理的运营知识；
- 示例或合成数据。

> 注：DEC-005 已确认「评论 / 竞品 / 行业资料为增强输入、非必填」；Assumption-001 关于「数据可得性」的判断仍成立，但「是否使用公开页面 / 抓取」属于 DEC-005 Decision Boundary 中尚未确认的采集方式。

#### Assumption-002
项目的首要目标可能不是立即商业化，而是证明项目所有者具备 AI 产品设计、Agent 工作流设计和开源项目改造能力。

#### Assumption-003
为了保证项目能够完成，MVP 最好聚焦一次具体运营任务，而不是构建完整电商经营平台。

### Alternatives

#### Alternative A：消费者购物助手

- **目标用户：** 普通消费者。
- **典型任务：**
  - 根据需求推荐商品；
  - 比较商品参数；
  - 回答商品问题；
  - 生成购物清单；
  - 提供购买建议。
- **优点：**
  - 场景容易理解；
  - 公开商品数据较多；
  - 容易找到相似开源项目；
  - 容易制作对话式 Demo。
- **缺点：**
  - 同类项目非常多；
  - 容易变成普通 RAG 商品问答；
  - 很难证明真实交易价值；
  - 与大量已有 AI Shopping Assistant 项目同质化；
  - 对 AI 产品经理能力的展示可能较弱。

#### Alternative B：商家经营综合助手

- **目标用户：** 中小商家老板或综合运营人员。
- **典型任务：**
  - 分析经营数据；
  - 诊断销量变化；
  - 生成运营计划；
  - 分析竞品；
  - 提出商品、内容和定价建议。
- **优点：**
  - 业务价值较强；
  - 可以展示复杂 Agent 架构；
  - 适合扩展成多 Agent 系统。
- **缺点：**
  - 范围过大；
  - 依赖销售、流量、广告和库存等真实数据；
  - MVP 容易失控；
  - 很难在没有真实商家系统的情况下验证结论。

#### Alternative C：商品上新运营助手

- **目标用户：** 中小商家的商品运营或内容运营人员。
- **典型任务：** 用户提供一个待推广商品的资料，Agent 完成：
  1. 整理商品事实；
  2. 提取核心卖点；
  3. 识别目标人群；
  4. 分析用户需求和购买阻碍；
  5. 检索相关运营方法或案例；
  6. 形成商品定位；
  7. 生成内容策略或营销 Brief；
  8. 对结果进行检查和引用溯源。
- **优点：**
  - 输入和输出边界相对清楚；
  - 可以自然使用商品资料、评论、竞品和运营知识；
  - 可以体现 RAG、Tool、Skill 和工作流设计；
  - 不必依赖完整销售后台；
  - 适合展示从信息收集到运营方案的端到端流程；
  - 后续可以扩展内容生成和多 Agent。
- **缺点：**
  - 仍需定义 "商品上新" 的具体完成标准；
  - 运营方案效果难以直接通过销量验证；
  - 需要设计合理的评估方式，避免只评价文案是否好看。

> 注：Alternative C（商品上新运营助手）的方向已被采纳——其目标用户由 DEC-002 确认、其核心任务由 DEC-003 确认。注意区分：Question-002 候选 A（商品上新定位与营销 Brief）即被接受的核心任务；而本节 Alternative A 是消费者购物助手，未被接受。

#### Alternative D：用户评论洞察 Agent

- **目标用户：** 商品运营、用户研究或客服负责人。
- **典型任务：** 用户上传大量评论后，Agent 完成：

  - 评论清洗；
  - 主题聚类；
  - 情绪与诉求分析；
  - 高频优点和问题识别；
  - 用户人群推断；
  - 产品优化建议；
  - 内容营销建议；
  - 生成洞察报告。

- **优点：**
  - 任务范围清晰；
  - 数据容易获得或构造；
  - 结果相对容易评估；
  - 可以展示数据处理、RAG、Agent 分析和报告生成；
  - 更容易完成高质量 MVP。
- **缺点：**
  - "电商 Agent" 的范围相对窄；
  - 如果只做聚类和摘要，可能更像数据分析工具；
  - 需要明确 Agent 相比普通 NLP Pipeline 的价值。

> 注：以下 Alternative E / F 属于 **DEC-007「人机协作机制」** 的备选方案（不同于上文 A–D 的**项目定位**备选方案），在 DEC-007 评估时未被采用，但**未被永久禁止**，保留为后续可重新评估的备选。

#### Alternative E：完全自动生成（无审核节点）

- **含义：** 用户提交资料后，系统一次性生成四层结构与最终营销 Brief，全程不设置人工审核或暂停节点。
- **优点：**
  - 流程最简单；
  - 交互步骤最少；
  - 开发成本最低。
- **缺点：**
  - 事实识别错误会继续污染洞察、策略与执行结果；
  - 用户无法在交付前纠偏；
  - 难以体现 Agent 与用户的协作，易退化为一键文案生成器。
- **状态：** DEC-007 评估时**未采用**；作为备选保留（**非永久禁止**）。

#### Alternative F：每层分别审核确认

- **含义：** 在事实层、洞察层、策略层、执行层**每一层**都设置独立的人工审核与确认节点。
- **优点：**
  - 每一层错误都能被及时拦截；
  - 可追溯性与可控性最强。
- **缺点：**
  - 交互步骤过多；
  - 用户频繁被打断；
  - 工作流过于繁琐；
  - MVP 开发成本显著增加。
- **状态：** DEC-007 评估时**未采用**；作为备选保留（**非永久禁止**）。

> DEC-007 选择了 E 与 F 之间的折中：**单一关键审核节点（草稿生成后、最终 Brief 前）+ 异常暂停**。

> 注：以下 Alternative G / H 属于 **DEC-008「证据与结论可靠性」** 的备选方案（不同于 A–D 的项目定位、E–F 的协作机制），在 DEC-008 评估时未被采用，但**未被永久禁止**，保留为后续可重新评估的备选。

#### Alternative G：只展示最终结论

- **含义：** 系统仅输出最终的商品定位与营销 Brief，不区分事实 / 洞察 / 推断 / 假设，不保留任何依据关系。
- **优点：** 界面最简单；实现成本最低。
- **缺点：** 用户无法判断信息来源、哪些是事实、哪些是模型推测、输入不足时是否在编造、为何形成某定位。
- **状态：** DEC-008 评估时**未采用**；作为备选保留（**非永久禁止**）。

#### Alternative H：所有结论强制逐条原文引用

- **含义：** 要求每一句结论都对应一条完全相同的原文出处。
- **优点：** 可追溯性最强；依据最严格。
- **缺点：** 界面复杂；综合策略难以表达；容易出现形式化或错误引用；增加不必要的实现成本。
- **状态：** DEC-008 评估时**未采用**；作为备选保留（**非永久禁止**）。

> DEC-008 选择了 G 与 H 之间的折中：**分级证据标记（五类）+ 重要结论可追溯**——事实必须有来源、洞察需有依据、推断须显式标记、假设须用户确认、资料不足须诚实表达。

> 注：以下 Alternative I / J 属于 **DEC-009「修改后失效与重跑」** 的备选方案，在 DEC-009 评估时未被采用，但**未被永久禁止**，保留为后续可重新评估的备选。

#### Alternative I：每次修改后全量重跑

- **含义：** 用户任意修改后，重新生成全部下游内容（不区分阶段、不区分重要 / 非重要修改）。
- **优点：** 实现最简单；一致性最强。
- **缺点：** 不相关内容被重新改写；生成时间与模型成本增加；用户已认可内容无意义变化；用户难理解修改影响。
- **状态：** DEC-009 评估时**未采用**；作为备选保留（**非永久禁止**）。

#### Alternative J：只修改直接字段、不更新下游依赖

- **含义：** 只保存用户修改的字段，不使下游结论失效、不重跑。
- **优点：** 改动范围最小；实现简单。
- **缺点：** 下游继续依赖旧信息；事实 / 洞察 / 策略 / Brief 互相矛盾；输出可靠性降低。
- **状态：** DEC-009 评估时**未采用**；作为备选保留（**非永久禁止**）。

> DEC-009 选择了 I 与 J 之间的折中：**阶段级失效 + 局部重跑**——按事实 → 洞察 → 策略 → 执行阶段关系失效并重生成。另：**精细字段级依赖图暂缓到后续版本**（不进入 MVP），见「Deferred Topics」。

### Proposals

#### Proposal-001：优先探索 "商品上新运营助手"

> **状态：核心方向已被采纳（DEC-002 用户 + DEC-003 核心任务 + DEC-004 平台范围 + DEC-005 输入分层 + DEC-006 四层输出主结构 + DEC-007 人机协作审核机制 + DEC-008 分级证据与结论可追溯 + DEC-009 阶段级失效与局部重跑 + DEC-010 三维评价框架）。**
> 「产品正式名称 / 定位表述」未单独作为决定；各层字段 / 输出格式、工作流与数据技术实现仍待讨论。Proposal 本身不再仅是探索性提案，其方向已落入已接受决定。

当前建议优先将项目定位为：**面向中小电商商家运营人员的 AI 商品上新运营助手。**

初步任务闭环可以是：

```
输入商品资料
+ 用户评论或调研资料
+ 可选竞品信息
+ 运营知识库

        ↓

检查资料完整性

        ↓

提取商品事实与卖点

        ↓

分析目标用户、需求和购买阻碍

        ↓

检索运营方法和相关案例

        ↓

形成商品定位与内容策略

        ↓

生成结构化商品上新 Brief

        ↓

执行质量检查与引用溯源
```

> 注：DEC-005 已将上述输入明确为「最低可运行输入 + 推荐 / 可选增强输入」分层；评论 / 竞品 / 运营知识库属增强输入，非基础流程前置条件。
> 注：DEC-006 已将「形成商品定位与内容策略 → 生成结构化上新 Brief」的输出明确为「事实 → 洞察 → 策略 → 执行」四层结构，后层内容可追溯前层依据；完整小红书标题 / 正文不作为 MVP 核心交付物。

### Trade-offs

#### Rationale for Proposal-001

推荐该方向的主要原因：

1. 比消费者购物助手更容易体现商家业务价值；
2. 比综合经营助手更适合控制 MVP 范围；
3. 能自然引出 RAG、Skill、工作流和 Agent 质量检查；
4. 不要求项目初期接入真实 ERP、广告或交易系统；
5. 可以基于公开或用户上传的数据完成 Demo；
6. 适合后续扩展评论分析、内容生成和竞品分析；
7. 容易展示项目所有者对用户流程和 Agent 边界的设计，而不只是框架使用。

### Risks

#### Risk-001：输出可能只是高级 Prompt 生成结果

如果 Agent 只是读取商品资料后生成营销文案，项目会缺乏技术和产品差异。后续需要设计：

- 多步骤任务状态；
- 信息完整性检查；
- 检索依据；
- 结构化中间产物；
- 质量评价；
- 失败重试或人工确认；
- 输出引用和可追溯性。

#### Risk-002：业务效果难以验证

商品上新方案无法在作品集阶段直接证明会提升真实销量。后续可能需要定义代理指标，例如：

- 商品事实准确率；
- 引用正确率；
- 卖点覆盖率；
- 人群与痛点的一致性；
- Brief 完整率；
- 不同运行结果的一致性；
- 人工修改时间减少比例；
- 用户任务完成时间；
- 运营人员主观评分。

#### Risk-003：范围再次膨胀

商品上新可能逐渐扩展到：

- 自动生成大量文案；
- 自动发布；
- 广告投放；
- 销量预测；
- 库存分析；
- 全店经营。

这些能力暂时应作为 Deferred Topics，不应自动进入 MVP。

## Proposed Decisions

None。

本轮尚未形成等待确认的正式 Proposed Decision。`Proposal-001` 的核心方向已通过 DEC-002 / DEC-003 / DEC-004 / DEC-005 被采纳，无需再作为 Proposed Decision。

## Accepted Decisions

- **DEC-001 — 真实电商业务价值优先于 Agent 技术复杂度**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 明确回复「接受」，通过 Decision Gate。
  - 决定记录：[../decisions/dec-001-business-value-before-agent-complexity.md](../decisions/dec-001-business-value-before-agent-complexity.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/vision.md](../product/vision.md)、[../product/prd.md](../product/prd.md)。
  - 用户确认的导向权重（方向性，非量化指标）：约 60% 业务 / 约 40% 技术。
  - **范围说明：** DEC-001 仅确认总体项目导向；**未**确认目标用户、核心任务、LangGraph/RAG/Skill/Multi-Agent、平台范围，也未扩大 MVP。

- **DEC-002 — MVP 首要用户为中小电商商家的商品运营与内容运营人员**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 明确表示「我觉得 B 就不错，MVP 首要用户选择'中小电商商家的商品运营／内容运营人员'」（B + C 合并），通过 Decision Gate。
  - 决定记录：[../decisions/dec-002-primary-mvp-users.md](../decisions/dec-002-primary-mvp-users.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/vision.md](../product/vision.md)、[../product/prd.md](../product/prd.md)、[../product/user-personas.md](../product/user-personas.md)。
  - 对应 Question-001（阶段性解决）；Persona 拆分 / 职责边界 / 购买者 / 最高频使用者仍为 Open Question。
  - **范围说明：** DEC-002 仅确认 MVP 首要用户群体；**未**确认核心任务、产品定位、次要用户、平台范围、技术选型。

- **DEC-003 — MVP 核心任务为商品上新定位分析与营销 Brief 生成**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 明确回复「接受」，通过 Decision Gate。
  - 决定记录：[../decisions/dec-003-product-launch-positioning-and-marketing-brief.md](../decisions/dec-003-product-launch-positioning-and-marketing-brief.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/vision.md](../product/vision.md)、[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。
  - 对应 Question-002（已确认，候选 A 被接受）；候选 B / C / D / E 不标记为永久拒绝，作为后续扩展或参考保留。
  - **范围说明：** DEC-003 仅确认 MVP 核心任务与交付物及任务闭环方向；**未**确认平台、输入资料、Brief 字段、技术实现等。

- **DEC-004 — 产品核心保持平台中立，小红书种草作为首个 MVP 演示场景**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 选择 **C：通用能力 + 小红书演示模板**，通过 Decision Gate。
  - 决定记录：[../decisions/dec-004-platform-neutral-core-xiaohongshu-demo.md](../decisions/dec-004-platform-neutral-core-xiaohongshu-demo.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/vision.md](../product/vision.md)、[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。
  - 对应 Question-004（已确认）；引入已确认的产品逻辑边界：通用层（通用定位 + Brief）+ 平台适配层（首个＝小红书种草模板）。
  - **范围说明：** DEC-004 仅确认平台范围与首个演示场景；**未**确认小红书模板字段、完整笔记生成、抓取 / API、其他平台支持、适配层技术实现、独立平台 Agent / Skill。

- **DEC-005 — MVP 采用最低可运行输入与增强输入分层**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 对 MVP 输入原则明确回复「同意」，通过 Decision Gate。
  - 决定记录：[../decisions/dec-005-layered-mvp-inputs.md](../decisions/dec-005-layered-mvp-inputs.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。
  - 解决了「MVP 输入资料范围」的**原则层**问题：最低可运行输入（商品基础资料 + 推广目标）即可运行；评论 / 品牌 / 已有内容 / 竞品 / 运营资料为增强输入；缺少增强输入不阻断基础流程。
  - **范围说明：** DEC-005 仅确认输入分层原则与字段范围；**未**确认字段数据类型、最低字段是否全部强制、图片是否技术必填、文件格式、商品链接 / 自动抓取、评论 / 竞品自动采集、联网搜索、长期知识库 / 向量库、文档切分检索、完整度评分算法、信息不足时具体询问内容、隐私 / 权限 / 数据保存策略。

- **DEC-006 — MVP 输出采用四层结构化营销 Brief**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 对四层结构化 Brief 方案明确回复「可以」，通过 Decision Gate。
  - 决定记录：[../decisions/dec-006-four-layer-structured-marketing-brief.md](../decisions/dec-006-four-layer-structured-marketing-brief.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。
  - 解决了「MVP 输出主结构」的**原则层**问题：输出采用 **事实层 → 洞察层 → 策略层 → 执行层** 四层结构，后层可追溯前层依据；**完整小红书标题与正文暂不属于 MVP 核心交付物**（小红书种草 Brief 是执行层的一种平台映射，与 DEC-004 一致）。
  - **范围说明：** DEC-006 仅确认四层输出主结构、追溯原则及「小红书完整笔记非核心交付物」；**未**确认四层最终字段、哪些字段必填、输出格式（Markdown / JSON / 表格 / 其他）、引用显示形式、置信度计算方式、是否将完整小红书笔记作为附加能力、用户能否单独编辑某一层、人工审核节点、Agent / RAG / Skill 技术实现、数据库存储方式。

- **DEC-007 — MVP 采用单一关键审核节点与异常暂停机制**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 对该人机协作方案明确回复「确认」，通过 Decision Gate。
  - 决定记录：[../decisions/dec-007-single-review-node-and-exception-pauses.md](../decisions/dec-007-single-review-node-and-exception-pauses.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。
  - 解决了「人机协作 / 审核节点」的**原则层**问题：MVP 采用 Human-in-the-loop——**一个常规强制审核节点**（分析草稿生成后、最终 Brief 生成前）+ **异常暂停与追问**（资料矛盾 / 关键缺失 / 高风险表达时）+ **用户保留最终业务判断权**。常规流程**不要求**每层分别确认。
  - **未采用但保留为备选（非永久禁止，见「Alternatives」E / F）：** 完全自动生成（无审核节点）、每层分别审核确认。
  - **范围说明：** DEC-007 仅确认人机协作模式（单一关键审核节点 + 异常暂停 + 用户最终判断权）；**未**确认是否采用 LangGraph / Interrupt API、是否需要数据库级持久化 / Checkpoint 实现方式、用户修改后重跑全部还是局部流程、审核页面结构、草稿编辑粒度、异常判断规则、高风险表达具体范围、是否多人协作审核、是否保留版本历史、用户能否跳过常规审核节点。
  - **架构影响提示：** 本决定是首个对工作流状态、暂停 / 恢复、Checkpoint、局部重跑提出明确业务要求的决定，具有**潜在架构影响**；但当前**不创建正式 Architecture Decision**，**不创建 RFC**——后续讨论「工作流状态、暂停恢复与局部重跑」技术方案时，再判断是否建立架构 RFC。

- **DEC-008 — MVP 采用分级证据标记与结论可追溯机制**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 对该可靠性方案明确回复「确认」，通过 Decision Gate。
  - 决定记录：[../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md](../decisions/dec-008-tiered-evidence-and-traceable-conclusions.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。
  - 解决了「输出可靠性与可追溯性」的**原则层**问题：MVP 采用**五类结论标记**（明确事实 / 有证据洞察 / 模型推断 / 待验证假设 / 资料不足）+ 七条最低可靠性原则（事实可追溯、事实与推断分离、重要洞察保留依据、资料不足保持诚实、策略可回溯、修改产生依赖影响、禁止伪造来源）。重要结论须保留与主要依据 / 输入资料 / 前序分析的关系。
  - **未采用但保留为备选（非永久禁止，见「Alternatives」G / H）：** 只展示最终结论、所有结论强制逐条原文引用。
  - **范围说明：** DEC-008 仅确认可靠性原则与五类标记；**未**确认引用 UI、是否显示置信度数值、置信度算法、来源 ID 与数据结构、是否使用 RAG / 向量数据库 / 网页检索 / 知识图谱、是否保存原始文档片段、全量或局部重跑、LangGraph State / Checkpoint、数据库存储方式、外部来源可信度评估规则。
  - **架构 / 仓库选型约束（重要）：** 可靠性原则已成为后续**架构设计与开源仓库选型的硬约束**——技术方案与基底仓库必须能支持「为每项重要结论保存类型、依据与依赖关系，并在上游修改时使下游失效」。当前**不创建 RFC**；后续讨论「结论类型 / 依据 / 依赖关系的数据结构与存储」时，可再判断是否建架构 RFC。

- **DEC-009 — MVP 采用阶段级依赖失效与局部重跑**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 对该方案明确回复「确认」，通过 Decision Gate。
  - 决定记录：[../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md](../decisions/dec-009-stage-level-invalidation-and-partial-rerun.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)、[../product/user-flows.md](../product/user-flows.md)。
  - 解决了「修改后失效与重跑」的**规则层**问题：按事实 → 洞察 → 策略 → 执行**阶段级依赖**处理失效与重跑——改事实层使洞察 / 策略 / 执行失效；改洞察层使策略 / 执行失效；改策略层使执行失效；直接编辑执行层默认不触发上游。重要业务修改触发下游失效，纯文字修改可不触发；失效内容不得显示为有效 / 入最终 Brief / 作后续依据。
  - **未采用但保留为备选（非永久禁止，见「Alternatives」I / J）：** 全量重跑、只改直接字段不更新下游。**精细字段级依赖图暂缓到后续版本**（不进入 MVP），见「Deferred Topics」。
  - **范围说明：** DEC-009 仅确认阶段级失效规则；**未**确认 LangGraph / Checkpoint / Interrupt / 状态数据库 / 失效状态数据结构 / 如何自动识别重要修改 / 是否保留历史版本 / 是否显示差异 / 自动或手动重跑 / 是否强制二次审核 / 字段级依赖图是否进后续版本。
  - **架构 RFC 业务约束：** 与 DEC-007（工作流暂停 / 恢复）、DEC-008（结论 / 依据 / 依赖存储与失效）共同构成后续架构 RFC 的业务约束。当前**不创建 RFC**；后续进入「工作流状态、暂停恢复与技术实现方案比较」时，以 DEC-007 / 008 / 009 为业务约束。

- **DEC-010 — MVP 采用任务质量、可靠性与用户效率三维评价框架**（Type: Product，Status: Accepted，2026-07-27）
  - 用户于 2026-07-27 对该评价方案明确回复「确认」，通过 Decision Gate。对应 **Question-003 在框架层已确认**。
  - 决定记录：[../decisions/dec-010-three-dimensional-mvp-evaluation-framework.md](../decisions/dec-010-three-dimensional-mvp-evaluation-framework.md)；已登记于 [../decisions/decision-log.md](../decisions/decision-log.md)。
  - 已同步至 Current Truth：[../product/prd.md](../product/prd.md)、[../product/mvp-scope.md](../product/mvp-scope.md)（**未同步 user-flows**——评价框架不改变用户流程结构）。
  - 解决了「产品评价目标（Question-003）」的**框架层**问题：MVP 同时评估 **任务质量 / 结果可靠性 / 用户效率**，**不**把语言流畅度或最终销量作为唯一成功标准；优先六项指标（事实来源可追溯率、无依据事实数量、四层 Brief 完整率、关键结论人工接受率、生成可用 Brief 任务完成时间、下游失效正确率）；销量 / 点击 / 转化 / 互动为未来真实试点业务指标，**非** MVP 唯一验收依据。
  - **未采用但保留为未采用方案（非永久禁止，见「Rejected or Unselected Alternatives」）：** 只评价内容流畅度、只评价任务效率、只以销量作为成功指标。
  - **范围说明：** DEC-010 仅确认评价框架与方向；**未**确认每项指标公式、目标阈值、测试数据集、用户测试人数、人工评分标准、是否使用 LLM-as-a-Judge、埋点方案、对照组设计、测试环境、是否接入真实业务数据、是否展示评测 Dashboard。

## Rejected Approaches

None。

Question-002 的候选 B（用户评论洞察）/ C（商品内容批量生成）/ D（消费者选购推荐）/ E（综合经营诊断）**未被永久拒绝**，仅暂未作为 MVP 核心任务；作为后续扩展或参考方案保留（见「Deferred Topics」）。

DEC-007 评估时存在的两个协作方案——**完全自动生成（无审核节点）** 与 **每层分别审核确认**——**未被采用，也未被永久禁止**；作为备选方案保留在「Alternatives」E / F，后续可重新评估。

DEC-008 评估时存在的两个可靠性方案——**只展示最终结论** 与 **所有结论强制逐条原文引用**——**未被采用，也未被永久禁止**；作为备选方案保留在「Alternatives」G / H，后续可重新评估。

DEC-009 评估时存在的两个重跑方案——**每次修改后全量重跑** 与 **只修改直接字段、不更新下游依赖**——**未被采用，也未被永久禁止**；作为备选方案保留在「Alternatives」I / J，后续可重新评估。**精细字段级依赖图暂缓到后续版本**（不进入 MVP），见「Deferred Topics」。

DEC-010 评估时存在的三个单维度评价方案——**只评价内容流畅度**、**只评价任务效率**、**只以销量作为成功指标**——**未被采用，也未被永久禁止**；作为未采用方案保留，后续可重新评估。

## Open Questions

保留 Question-001 至 Question-004（见上文「Questions to Resolve」）：

- Question-001：首要目标用户是谁？—— **阶段性解决**（DEC-002）。衍生开放问题：复合 Persona 还是拆分、职责边界、购买者、最高频使用者、次要用户。
- Question-002：MVP 应解决哪一个核心任务？—— **已确认**（DEC-003）。衍生开放问题：输入资料范围（**原则层已由 DEC-005 解决**；字段类型 / 格式 / 采集方式仍开放）、Brief 字段、验收标准。
- Question-003：项目的主要评价目标是什么？—— **框架层已确认**（DEC-010：三维评价 + 六项优先指标；不以流畅度 / 销量为唯一标准）。衍生开放问题：指标公式 / 阈值 / 测试集 / 人数 / 埋点 / Dashboard。
- Question-004：项目是否需要优先适配某个平台？—— **已确认**（DEC-004）。衍生开放问题：小红书模板字段、其他平台支持、适配层技术实现。

> 另有跨问题开放项：通用营销 Brief 输出结构（**四层主结构已由 DEC-006 确认**：事实 / 洞察 / 策略 / 执行；各层字段 / 必填 / 输出格式仍开放）；输出可靠性与可追溯（**五类结论标记 + 七条可靠性原则已由 DEC-008 确认**；引用 UI / 置信度算法 / 来源数据结构 / RAG / 向量库 / 知识图谱仍开放）；人机协作 / 审核节点（**原则层已由 DEC-007 确认**：单一关键审核节点 + 异常暂停 + 用户最终判断权；审核页面 / 编辑粒度 / 异常规则 / 工作流技术实现仍开放）；修改后失效与重跑（**阶段级规则已由 DEC-009 确认**；自动重跑交互 / 版本历史 / 字段级依赖图仍开放）；产品评价（**框架层已由 DEC-010 确认**：三维评价 + 六项优先指标；公式 / 阈值 / 测试方式仍开放）；小红书种草 Brief 字段；Agent / RAG / Skill 架构；GitHub 开源项目选择与改造边界。

## Deferred Topics

- LangGraph 是否采用；
- RAG 架构（含是否向量库、文档切分与检索方式、联网搜索均未确认）；
- Skill 定义；
- 单 Agent 或 Multi-Agent（含「平台适配层是否独立 Agent / Skill」未确认）；
- 输入完整度检查的技术实现（含完整度评分算法、信息不足时具体询问内容均未确认）；
- 数据采集方式（商品链接 / 自动抓取商品页面 / 评论 / 竞品数据、长期知识库、隐私 / 权限 / 数据保存均未确认）；
- 输出层的技术实现（含四层各层字段契约、必填规则、输出格式、引用机制、置信度算法、用户单层编辑、人工审核节点交互、是否生成完整小红书笔记作为附加能力、Agent 状态设计 / Skill 职责 / RAG 输出方式均未确认）；
- 工作流状态 / 暂停恢复 / Checkpoint / 局部重跑的技术实现（DEC-007 引入；含是否采用 LangGraph / Interrupt API、是否数据库级持久化、Checkpoint 实现方式、用户修改后重跑全部还是局部流程、审核页面结构、草稿编辑粒度、异常判断规则、高风险表达范围、多人协作审核、版本历史、能否跳过常规审核节点均未确认）；
- 结论可靠性 / 可追溯的技术实现（DEC-008 引入；含引用 UI、是否显示置信度数值、置信度算法、来源 ID 与数据结构、是否使用 RAG / 向量数据库 / 网页检索 / 知识图谱、是否保存原始文档片段、全量或局部重跑、外部来源可信度评估规则均未确认）；
- 阶段级失效 / 局部重跑的技术实现（DEC-009 引入；含 LangGraph / Checkpoint / Interrupt、工作流节点划分、状态数据库、失效状态数据结构、自动识别重要修改、版本历史、修改前后差异、自动或手动重跑、强制二次审核均未确认）；**精细字段级依赖图暂缓到后续版本**（不进入 MVP）；
- GitHub 开源项目选择；
- 模型和数据库选型；
- 前后端技术栈；
- 部署方式；
- 自动发布和平台 API 集成（含小红书 API、抓取小红书公开内容、分析爆款笔记均未确认）；
- **后续扩展候选（Question-002 未被采纳的方向，非永久拒绝）：** 用户评论洞察、商品内容批量生成、消费者选购推荐、综合经营诊断、竞品自动监控、多平台批量生成、广告投放、销售预测、库存分析、客服、完整店铺经营诊断；
- **其他平台支持（DEC-004 未确认）：** 淘宝、抖音等平台的适配模板。

> 注（架构影响，DEC-007）：本决定是首个对工作流状态、暂停 / 恢复、Checkpoint、局部重跑提出明确业务要求的决定，具有潜在架构影响。**当前不创建正式 Architecture Decision，不创建 RFC**；后续讨论「工作流状态、暂停恢复与局部重跑」技术方案时，再判断是否建立架构 RFC。

> 注（架构 / 仓库选型约束，DEC-008）：DEC-008 的可靠性原则（事实可追溯、事实与推断分离、重要洞察保留依据、修改产生依赖影响、禁止伪造来源）已成为**后续架构设计与开源仓库选型的硬约束**——任何技术方案与基底仓库必须能支持「为每项重要结论保存类型、依据与依赖关系，并在上游修改时使下游失效」。当前**不创建 RFC**；后续讨论「结论类型 / 依据 / 依赖关系的数据结构与存储」时，可再判断是否建架构 RFC。

## Documentation Updates

本轮执行：

1. 创建本文件 `docs/sessions/session-001-project-positioning-and-mvp.md`；
2. 将本轮内容作为 Session-001 的初始化内容；
3. 状态设置为 `In Discussion`；
4. 不创建 Decision Record；
5. 不创建正式 RFC；
6. 不更新 Current Specifications；
7. 将初始化报告中的 "约 9 类开放问题" 修正为 "10 类开放问题"，但不修改其实际语义；
8. 保持 Development Status 为 `NOT READY`。

> 后续追加（DEC-001 / DEC-002 / DEC-003 / DEC-004 / DEC-005 / DEC-006 / DEC-007 / DEC-008 / DEC-009 / DEC-010 归档时）：
>
> - DEC-001：用户「接受」→ 创建 DEC-001、更新 decision-log、同步 vision/prd。
> - DEC-002：用户「我觉得 B 就不错…」→ 创建 DEC-002、更新 decision-log、同步 vision/prd/user-personas；Question-001 标记阶段性解决。
> - DEC-003：用户「接受」→ 创建 DEC-003、更新 decision-log、同步 vision/prd/mvp-scope/user-flows；Question-002 标记已确认；候选 B/C/D/E 转入 Deferred Topics。
> - DEC-004：用户选「C：通用能力 + 小红书演示模板」→ 创建 DEC-004、更新 decision-log、同步 vision/prd/mvp-scope/user-flows；Question-004 标记已确认；引入通用层 / 平台适配层逻辑边界。
> - DEC-005：用户「同意」输入分层 → 创建 DEC-005、更新 decision-log、同步 prd/mvp-scope/user-flows（本次未同步 vision）；解决输入资料范围原则层问题。
> - DEC-006：用户「可以」四层结构化 Brief → 创建 DEC-006、更新 decision-log、同步 prd/mvp-scope/user-flows（本次未同步 vision / user-personas）；解决输出主结构原则层问题。
> - DEC-007：用户「确认」单一审核节点 + 异常暂停 → 创建 DEC-007、更新 decision-log、同步 prd/mvp-scope/user-flows（本次未同步 vision / user-personas）；解决人机协作原则层问题；两个未采用方案记为 Alternatives E/F（非永久禁止）；标记潜在架构影响，暂不建 Architecture Decision / RFC。
> - DEC-008：用户「确认」分级证据标记 + 可追溯 → 创建 DEC-008、更新 decision-log、同步 prd/mvp-scope/user-flows（本次未同步 vision / user-personas）；解决输出可靠性原则层问题；两个未采用方案记为 Alternatives G/H（非永久禁止）；可靠性原则成为架构 / 仓库选型硬约束，暂不建 RFC。
> - DEC-009：用户「确认」阶段级失效 + 局部重跑 → 创建 DEC-009、更新 decision-log、同步 prd/mvp-scope/user-flows（本次未同步 vision / user-personas）；解决修改后失效与重跑规则层问题；两个未采用方案记为 Alternatives I/J（非永久禁止）；字段级依赖图暂缓到后续版本；与 DEC-007/008 同为架构 RFC 业务约束。
> - DEC-010：用户「确认」三维评价框架 → 创建 DEC-010、更新 decision-log、同步 prd/mvp-scope（**未同步 user-flows**——评价框架不改变用户流程；未同步 vision / user-personas）；Question-003 框架层解决；三个单维度评价方案记为未采用（非永久禁止）。
> - **阶段固化：** DEC-009 / DEC-010 归档后，Session Status 改为 `Completed`，新增「Formal Consolidation（阶段性正式固化）」章节，并在 `docs/sessions/README.md` 记录 Session-002 计划。Development Status 仍 `NOT READY`。

## Synchronization Checklist

- [x] Session 初始化
- [x] 目标用户确认（DEC-002：商品运营 / 内容运营人员；Persona 细节仍开放）
- [x] 核心业务问题确认（DEC-003：商品上新定位 + 营销 Brief）
- [x] MVP 核心任务确认（DEC-003；交付物＝结构化营销 Brief）
- [~] 产品定位确认（用户 DEC-002 + 任务 DEC-003 + 平台 DEC-004 + 输入 DEC-005 + 输出 DEC-006 已明确；正式名称 / 定位表述、技术选型仍待确认）
- [x] 平台范围确认（DEC-004：核心中立 + 小红书首个演示）
- [x] 输入设计确认（DEC-005：最低可运行 + 增强 / 可选分层；字段类型 / 采集方式 / 技术实现仍开放）
- [x] 输出设计确认（DEC-006：事实 / 洞察 / 策略 / 执行四层主结构 + 追溯原则；各层字段 / 必填 / 输出格式 / 引用 / 置信度仍开放）
- [x] 人机协作确认（DEC-007：单一关键审核节点 + 异常暂停 + 用户最终判断权；完全自动 / 每层分别确认方案记为备选；工作流技术实现仍开放）
- [x] 可靠性确认（DEC-008：五类结论标记 + 七条可靠性原则 + 重要结论可追溯；只展示结论 / 强制逐条原文引用方案记为备选；引用 UI / 置信度算法 / RAG / 向量库 / 知识图谱仍开放；可靠性原则成为架构 / 仓库选型硬约束）
- [x] 失效重跑确认（DEC-009：阶段级失效 + 局部重跑 + 重要 / 非重要修改区分；全量重跑 / 只改直接字段方案记为备选；字段级依赖图暂缓；LangGraph / Checkpoint / 自动重跑交互 / 版本历史仍开放）
- [x] 评价框架确认（DEC-010：任务质量 / 可靠性 / 用户效率三维 + 六项优先指标；不以流畅度 / 销量为唯一标准；公式 / 阈值 / 测试集 / 人数 / 埋点 / Dashboard 仍开放）
- [x] Proposed Decisions 输出（Session-001 议题已收尾；Proposal-001 核心已被 DEC-001~010 采纳）
- [x] 用户 Decision Gate（DEC-001 ~ DEC-010 通过）
- [x] Decision Records 创建（DEC-001 ~ DEC-010）
- [x] Current Specifications 同步（vision.md、prd.md、user-personas.md、mvp-scope.md、user-flows.md）
- [x] RFC 必要性复核（DEC-001 ~ DEC-010 均暂不创建 RFC；DEC-007 / 008 / 009 有潜在架构影响，工作流与数据结构方案讨论时再判断是否建架构 RFC）
- [x] Session 阶段性正式固化（Status = Completed；见「Formal Consolidation」）
- [ ] Implementation Readiness Review

---

## Formal Consolidation（阶段性正式固化）

> 本节为 Session-001 的阶段性正式固化总结，于 DEC-010 归档后形成。固化的是「产品定位与 MVP 原则层」议题；项目**尚未进入开发**，Development Status 仍为 `NOT READY`。下一阶段转入 Session-002（Agent 工作流、可靠性架构与技术能力需求）。

### Session Status

- **Status: Completed**（阶段性正式固化完成；语义等价于正式结束本阶段讨论）。
- **不使用 `Implemented`**：项目尚未进入开发阶段，无任何业务实现。

### Formal Discussion Summary（正式讨论总结）

Session-001 达成的产品共识（均已落入 Accepted Decision）：

1. 项目用于 **AI 产品相关岗位作品集**（Fact / Constraint）；
2. **真实电商业务价值优先于 Agent 技术复杂度**（DEC-001，约 60/40 业务 / 技术方向性权重）；
3. 首要用户是 **中小电商商家的商品运营与内容运营人员**（DEC-002）；
4. 核心任务是 **商品上新定位分析与营销 Brief 生成**（DEC-003）；
5. 产品核心 **平台中立**（DEC-004）；
6. **小红书种草是首个演示场景**（DEC-004，通用层 + 平台适配层）；
7. 输入采用 **最低可运行输入 + 推荐增强 + 可选扩展** 分层（DEC-005）；
8. 输出采用 **事实 / 洞察 / 策略 / 执行四层结构**（DEC-006）；
9. 存在 **一个常规人工审核节点**（草稿后、最终 Brief 前；DEC-007）；
10. **关键异常会暂停并追问**（资料矛盾 / 关键缺失 / 高风险表达；DEC-007）；
11. 采用 **五类证据与结论标记**（明确事实 / 有证据洞察 / 模型推断 / 待验证假设 / 资料不足；DEC-008）；
12. 上游修改采用 **阶段级失效与局部重跑**（DEC-009）；
13. MVP 使用 **任务质量 / 可靠性 / 用户效率三维评价**（DEC-010）。

### Accepted Decisions（DEC-001 ~ DEC-010 索引）

详见上文「Accepted Decisions」与 [../decisions/decision-log.md](../decisions/decision-log.md)：

| DEC | 标题 | 状态 |
|-----|------|------|
| DEC-001 | 真实电商业务价值优先于 Agent 技术复杂度 | Accepted |
| DEC-002 | MVP 首要用户为商品运营与内容运营人员 | Accepted |
| DEC-003 | MVP 核心任务为商品上新定位分析与营销 Brief 生成 | Accepted |
| DEC-004 | 平台中立 + 小红书种草首个演示 | Accepted |
| DEC-005 | 最低可运行输入与增强输入分层 | Accepted |
| DEC-006 | 四层结构化营销 Brief（事实 / 洞察 / 策略 / 执行） | Accepted |
| DEC-007 | 单一关键审核节点与异常暂停 | Accepted |
| DEC-008 | 分级证据标记与结论可追溯 | Accepted |
| DEC-009 | 阶段级依赖失效与局部重跑 | Accepted |
| DEC-010 | 任务质量 / 可靠性 / 用户效率三维评价框架 | Accepted |

### Rejected or Unselected Alternatives（保留，不永久禁止）

以下方案在 Session-001 期间**未采用**，但**均未被永久禁止**，记录为未采用或延期方案，后续可重新评估：

- 消费者购物助手（Alternative A，定位）；
- 全店综合经营助手（Alternative B，定位）；
- 评论洞察作为唯一核心任务（Question-002 候选 B）；
- 多平台内容生成作为唯一核心任务（Question-002 候选 C）；
- 产品完全绑定小红书（DEC-004 单平台方案）；
- 完全自动生成（Alternative E，DEC-007）；
- 每层强制人工确认（Alternative F，DEC-007）；
- 只展示最终结论（Alternative G，DEC-008）；
- 所有结论强制逐条原文引用（Alternative H，DEC-008）；
- 每次修改后全量重跑（Alternative I，DEC-009）；
- 只修改直接字段、不处理下游依赖（Alternative J，DEC-009）；
- MVP 直接实现精细字段级依赖图（DEC-009，暂缓到后续版本）；
- 只评价内容流畅度（DEC-010）；
- 只评价任务效率（DEC-010）；
- 只以销量作为成功指标（DEC-010）。

### Open Questions（Session-001 结束后保留）

（详见上文「Open Questions」）至少保留以下开放问题：

- 商品运营与内容运营是否拆分为两个 Persona；
- 通用 Brief 的最终字段；
- 小红书 Brief 的具体映射结构；
- 输入文件类型与采集方式；
- 引用和证据的 UI 表现；
- 重要修改与文字修改的识别方式；
- 局部重跑的具体交互；
- 人工审核页面；
- 具体指标公式与目标阈值；
- 数据、隐私和保存策略；
- Agent、RAG 与 Skill 架构；
- 开源项目选择和改造边界。

### Deferred Topics（继续延期）

（详见上文「Deferred Topics」）继续延期：

- LangGraph 是否采用；
- 单 Agent 或 Multi-Agent；
- RAG 具体实现；
- Skill 的定义和执行机制；
- Checkpoint；
- 状态数据库；
- 向量数据库；
- 前端和后端技术栈；
- 模型供应商；
- 自动发布；
- 小红书 API；
- 其他平台适配；
- 部署方案。

> 架构 RFC 业务约束：DEC-007（工作流暂停 / 恢复）、DEC-008（结论 / 依据 / 依赖存储与失效）、DEC-009（阶段级失效与局部重跑）共同构成后续架构 RFC 的业务约束。当前**不创建 RFC**；进入 Session-002 工作流与可靠性架构讨论时再判断。

### Documentation Sync Checklist（DEC-001 ~ DEC-010 同步核对）

各 DEC 仅按其归档时明确的 sync 列表同步到「受影响」的 Current Truth 文件；DEC-005~010 为产品细节决定，按既定 sync 列表未写入 vision / user-personas（不属遗漏）。核对结果：

| 文件 | 已反映的 DEC |
|------|--------------|
| [../product/vision.md](../product/vision.md) | DEC-001 ~ DEC-004（愿景层决定） |
| [../product/prd.md](../product/prd.md) | DEC-001 ~ DEC-010（全量） |
| [../product/mvp-scope.md](../product/mvp-scope.md) | DEC-002 ~ DEC-010 |
| [../product/user-personas.md](../product/user-personas.md) | DEC-002（首要用户群体） |
| [../product/user-flows.md](../product/user-flows.md) | DEC-003 ~ DEC-009（DEC-010 评价框架不改变流程，按归档要求未同步） |
| [../decisions/decision-log.md](../decisions/decision-log.md) | DEC-001 ~ DEC-010（全量索引） |

> 核对结论：**无遗漏的已确认内容**；不同步项均为各 DEC 归档时明确指定，不补充新的产品结论。

### Next Session

下一阶段计划 Session（已在 [README.md](README.md) 登记为计划项）：

```
Session-002：Agent 工作流、可靠性架构与技术能力需求
```

> 本阶段**只创建 Session 索引 / 计划项**。不确认 LangGraph / RAG / Multi-Agent，不创建具体 Architecture Decision，不创建业务代码，不开始实现。Development Status 仍 `NOT READY`。
