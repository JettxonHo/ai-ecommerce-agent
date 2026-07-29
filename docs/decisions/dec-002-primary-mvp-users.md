# DEC-002：MVP 首要用户为中小电商商家的商品运营与内容运营人员

## Type

Product

## Status

Accepted

## Decision

AI Ecommerce Agent 的 MVP 首要目标用户确定为：中小电商商家的**商品运营人员**和**内容运营人员**。

项目应优先围绕该用户群体的真实工作任务、信息输入、决策过程、交付物和效果评价设计产品。

当前将「商品运营人员」和「内容运营人员」视为同一个首要用户群体，但**尚未决定**：

- 是否建立一个复合 User Persona；
- 是否拆分为商品运营和内容运营两个子 Persona；
- 两类角色的职责边界；
- 哪一个角色是最终购买者；
- 哪一个角色是产品的最高频使用者。

上述问题继续保留为后续 Persona 设计中的开放问题。

## Reason

与中小商家老板相比，商品运营和内容运营人员的工作职责更具体，能够围绕明确任务形成边界清晰、可验证的 MVP。

该用户群体通常涉及：

- 商品信息整理；
- 商品卖点提炼；
- 用户需求分析；
- 商品定位；
- 营销 Brief；
- 内容策略；
- 运营素材准备。

这些任务有机会形成完整的 Agent 工作闭环，同时避免在 MVP 阶段扩展到全店经营、库存、广告、供应链和财务等过大范围。

## Impact

该决定将影响后续：

- User Persona 设计；
- 用户访谈和需求研究范围；
- 核心业务任务选择；
- 用户输入与系统输出；
- 用户流程设计；
- MVP 功能边界；
- Agent 的职责与能力；
- RAG 数据来源；
- Skill 设计；
- 项目验收指标；
- GitHub 开源项目筛选标准；
- README、PRD 和简历项目描述。

后续所有 MVP 功能都应回答：这项功能是否直接服务于商品运营或内容运营人员的一项真实核心任务？无法直接回答该问题的功能，默认不进入 MVP。

## Related Session

Session-001：项目定位、目标用户与核心业务场景（[../sessions/session-001-project-positioning-and-mvp.md](../sessions/session-001-project-positioning-and-mvp.md)）

## Related RFC

None

## Supersedes

None

## Amends

None

## Notes

- 用户于 2026-07-27 明确表示「我觉得 B 就不错，MVP 首要用户选择'中小电商商家的商品运营／内容运营人员'」——选择 B（商品运营）并合并 C（内容运营）作为同一首要群体，通过 Decision Gate。
- 对应 Session-001 的 Question-001（阶段性解决）；Persona 拆分、职责边界、购买者、最高频使用者等仍为 Open Question。
- **本决定仅确认 MVP 首要用户群体**，不构成对以下任何一项的确认：
  - 最终产品定位（如「商品上新运营助手」仍只是 Proposal-001）；
  - MVP 核心任务（如「商品上新营销 Brief」尚未确认）；
  - 次要用户（商家老板或其他角色是否为次要用户尚未决定）；
  - 平台范围（未确认适配小红书、淘宝或其他特定平台）；
  - LangGraph、RAG、Skill、Multi-Agent 的采用。
- 已同步至 [../product/vision.md](../product/vision.md)、[../product/prd.md](../product/prd.md)、[../product/user-personas.md](../product/user-personas.md)。Agent 与 Architecture 规格未更新（具体架构尚未决定）。
