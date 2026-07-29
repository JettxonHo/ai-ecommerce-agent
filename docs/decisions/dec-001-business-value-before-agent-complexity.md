# DEC-001：真实电商业务价值优先于 Agent 技术复杂度

## Type

Product

## Status

Accepted

## Decision

AI Ecommerce Agent 项目在产品设计、MVP 范围和技术选择上，应优先证明项目所有者对真实电商用户、业务问题、工作流程和价值闭环的理解。

LangGraph、RAG、Skill、Multi-Agent、Tool Calling 等技术只在能够改善业务任务完成效果、可靠性、可追溯性或用户体验时采用。

不得为了展示技术复杂度而无业务依据地增加 Agent 数量、框架组件或系统层级。

## Reason

项目主要用于 AI 产品经理、AI 项目经理及相关岗位的简历和作品集展示。

仅展示复杂 Agent 架构，容易形成脱离业务的技术 Demo；仅展示业务方案，又不足以证明 AI 产品落地能力。

因此，项目应首先建立真实、清晰和可验证的业务闭环，再选择能够支撑该闭环的 Agent 技术。

## Impact

该决定将影响后续：

- 目标用户选择；
- 核心业务场景选择；
- MVP 范围；
- Agent 职责设计；
- LangGraph 是否采用；
- 单 Agent 或 Multi-Agent 选择；
- RAG 与 Skill 的使用边界；
- GitHub 开源项目筛选；
- 项目评价指标；
- README、PRD 和简历表达。

后续所有技术方案都需要回答：该技术具体解决了哪一个业务问题或可靠性问题？无法回答该问题的技术能力，默认不进入 MVP。

## Related Session

Session-001：项目定位、目标用户与核心业务场景（[../sessions/session-001-project-positioning-and-mvp.md](../sessions/session-001-project-positioning-and-mvp.md)）

## Related RFC

None

## Supersedes

None

## Amends

None

## Notes

- 用户于 2026-07-27 明确回复「接受」，通过 Decision Gate。
- 用户确认的项目导向权重（**方向性表达，非固定量化考核指标**）：约 60% 用户问题 / 业务流程 / 产品闭环 / 效果评估；约 40% LangGraph / RAG / Skill / Agent 工作流 / 可靠性设计。
- **本决定仅确认总体项目导向**，不构成对以下任何一项的确认：具体目标用户、具体核心任务、LangGraph/RAG/Skill/Multi-Agent 的采用、平台范围、MVP 功能范围的扩大。
- 已同步至 [../product/vision.md](../product/vision.md) 与 [../product/prd.md](../product/prd.md)（产品设计原则）。Agent 与 Architecture 规格未更新（具体架构尚未决定）。
- `Proposal-001`（商品上新运营助手）仍为探索阶段 Proposal，未转为决定。
