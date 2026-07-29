# DEC-015：Skill 定义为带执行契约的可复用业务能力包

> 本决定记录用户已明确接受的 Agent 层定义。相关 Session：[Session-002](../sessions/session-002-agent-workflow-reliability-and-technical-capabilities.md)。
> 已登记于 [decision-log.md](decision-log.md)。

## Type

Agent

## Status

Accepted（2026-07-27，用户对 Skill 的契约化业务能力包定义明确回复「确认」，通过 Decision Gate）

## Decision

在 AI Ecommerce Agent 项目中，Skill 被定义为：

> **面向特定业务目标、具备明确执行语义和可验证契约的可复用业务能力包。**

一个完整 Skill 原则上由以下内容共同构成：

```
业务目标
+ 适用条件
+ 输入契约
+ 执行步骤
+ 可调用工具或依赖能力
+ 输出契约
+ 确定性校验规则
+ 失败与暂停条件
+ 评价标准
```

Skill 可以包含 LLM 调用、确定性程序、检索、Tool 调用和人工审核逻辑中的一种或多种，但**不要求**所有 Skill 都必须使用 LLM。

Skill **不自动等同于**：

- 一个 Prompt 文件；
- 一个 Tool 函数；
- 一个工作流节点；
- 一个独立 Agent；
- 一份 Markdown SOP；
- 一次模型调用。

## Skill Purpose

Skill 用于将稳定、可复用的业务处理方式从整个工作流中分离出来，使系统能够：

- 明确每项能力解决什么业务问题；
- 定义能力所需输入；
- 约束执行步骤；
- 约束模型输出；
- 声明依赖的工具和数据；
- 在输入不足或结果不可靠时暂停；
- 对结果进行确定性校验；
- 使用固定测试用例进行验证；
- 在不同工作流阶段复用；
- 记录技能版本和运行效果。

## Minimum Skill Contract

一个 Skill Specification 至少需要表达以下内容。

### 1. Identifier

用于唯一识别 Skill，例如：

```
skill_id
name
version
status
```

> 具体编号方式和版本规则尚未确定。

### 2. Business Goal

说明 Skill 解决的业务任务。

示例：从商品资料中提取可追溯的候选事实，并识别关键缺失或冲突。

业务目标**不能**只写成：「调用 LLM 分析资料」。

### 3. Applicability

说明何时可以调用该 Skill，例如：

- 当前处于哪个业务阶段；
- 需要哪些输入；
- 哪些前置状态必须有效；
- 哪些情况不适用；
- 是否需要用户提供增强资料。

### 4. Input Contract

定义 Skill 可以读取的输入，例如：

```
raw_product_input
source_fragments
promotion_goal
current_valid_facts
```

输入必须来自明确的 Workflow State、Tool 输出或用户输入，**不能**依赖隐含聊天上下文猜测。

> 具体输入 Schema 技术尚未确定（文中字段名为概念示意）。

### 5. Execution Steps

定义 Skill 的高层执行过程。

例如，Product Fact Extraction Skill 可以包括：

```
1. 读取商品原始资料；
2. 识别候选商品事实；
3. 为事实关联来源片段；
4. 区分明确事实与待确认内容；
5. 检查关键字段缺失；
6. 检测资料冲突；
7. 输出结构化候选事实；
8. 运行确定性校验。
```

执行步骤可以包含：

- 确定性处理；
- LLM 分析；
- RAG 检索；
- Tool 调用；
- 规则校验；
- 暂停与人工补充。

### 6. Tool and Capability Dependencies

定义 Skill 依赖的能力，例如：

- 文档解析；
- 关键词检索；
- 语义检索；
- Schema 校验；
- 风险规则；
- 来源查询；
- LLM；
- 用户确认。

Skill **不应**隐式调用未声明的外部能力。

### 7. Output Contract

定义 Skill 输出的结构化结果。

例如：

```
facts[]
missing_information[]
detected_conflicts[]
warnings[]
```

输出应能够写入明确的 Workflow State 区域。LLM 自由文本**不应**成为唯一正式输出。

### 8. Validation Rules

定义输出需要通过的校验。例如：

- 每个明确事实必须存在真实 `source_ref`；
- 来源 ID 必须能够在当前任务中找到；
- 商品价格必须符合合法数据格式；
- 无来源内容不得标记为明确事实；
- 输出必须符合 Schema；
- 失效的上游状态不得作为输入。

校验规则中可通过确定性程序完成的内容，**不应**完全交给 LLM 自行判断。

### 9. Failure and Pause Conditions

定义不能继续执行的情况，例如：

- 必需输入不存在；
- 关键资料互相矛盾；
- 来源引用不存在；
- 输出多次无法通过 Schema 校验；
- 高风险表达需要人工确认；
- 当前阶段状态已经失效；
- 外部检索失败且没有足够资料继续。

Skill 需要明确区分：

- 可自动重试；
- 可降级继续；
- 需要暂停；
- 需要用户补充；
- 无法执行。

### 10. Evaluation Criteria

定义 Skill 是否有效，例如：

- 事实来源可追溯率；
- 无依据事实数量；
- Schema 通过率；
- 冲突识别率；
- 人工接受率；
- 平均修改数量；
- 运行耗时；
- 失败率。

> 具体指标阈值尚未确定。

## Skill Composition

一个 Skill 可以由以下构件组成：

```
Skill Specification
+ Prompt or Model Instructions
+ Structured Output Schema
+ Deterministic Validation
+ Tool Calls
+ Retrieval Rules
+ Failure Handling
+ Test Cases
```

其中：

- **Skill Specification**：解释业务目标、契约和执行规则。
- **Prompt or Model Instructions**：只负责需要 LLM 完成的语义任务。Prompt 是 Skill 的一个组成部分，**不代表完整 Skill**。
- **Structured Output Schema**：约束模型或程序返回的结果结构。
- **Deterministic Validation**：检查来源、状态、字段和业务规则。
- **Tool Calls**：完成文档解析、检索、数据库读取或其他技术动作。
- **Failure Handling**：定义异常、重试、降级和暂停方式。
- **Test Cases**：用于验证 Skill 在正常、缺失、冲突和失败输入下的行为。

## Skill and Prompt Boundary

以下形式**不能**单独被视为完整 Skill：

```
skills/analyze_product.md
"请分析以下商品并给出卖点。"
```

原因包括：

- 没有明确输入结构；
- 没有明确输出结构；
- 没有来源要求；
- 没有校验；
- 没有失败处理；
- 没有测试标准；
- 不知道何时调用；
- 无法保证运行一致性。

Prompt 可以存放于 Skill 目录中，但必须受 Skill Contract 约束。

## Skill and Tool Boundary

Tool 代表可调用的技术动作，例如：

```
parse_document()
search_reviews()
read_product_record()
validate_schema()
```

Skill 代表完成业务目标的能力包。例如 `Product Fact Extraction Skill` 可能依赖：

```
parse_document()
search_source_fragments()
validate_source_refs()
```

因此：

```
Tool ≠ Skill
```

一个 Skill 可以调用多个 Tool；同一个 Tool 也可以被多个 Skill 复用。

## Skill and Workflow Node Boundary

Skill 与工作流节点**不要求**一一对应。可能出现：

```
一个节点调用一个 Skill
```

也可能出现：

```
一个业务阶段调用多个 Skills
```

或：

```
同一个 Skill 被不同节点复用
```

> 具体节点划分需要在工作流设计中确定。**本决定不得被解释为：每个 Skill 必须是一个 LangGraph Node。**

## Skill and Agent Boundary

Skill 是能力；Agent 是承担职责、并在一定权限范围内使用能力的执行角色或运行实体。可能关系为：

```
Agent → 调用多个 Skills
```

也可能是：

```
确定性工作流 → 直接调用 Skill
```

因此 Skill **不要求**必须由独立 Agent 调用。一个 Skill 是否需要独立 Agent，应由以下因素决定：

- 是否需要独立上下文；
- 是否需要独立目标；
- 是否需要长期状态；
- 是否需要自主选择多个工具；
- 是否需要与其他 Agent 协作；
- 是否具备足够独立的业务责任。

**不得为了展示 Multi-Agent 而将每个 Skill 包装成独立 Agent。**

## Candidate MVP Skills

基于当前已确认业务流程，后续可能讨论的 Skill 包括（**仅为候选能力清单**）：

| 候选 Skill | 目标 |
|------------|------|
| Product Input Assessment Skill | 检查商品资料完整性、缺失信息和潜在冲突 |
| Product Fact Extraction Skill | 从商品资料中提取带来源的候选事实 |
| Customer Insight Analysis Skill | 根据事实、评论和调研资料形成用户需求、购买动机与购买阻碍 |
| Product Positioning Skill | 根据当前有效事实和洞察形成商品定位、价值主张和卖点优先级建议 |
| Evidence Retrieval Skill | 从长文档、评论和运营知识中检索与当前分析任务有关的证据片段 |
| Analysis Review Preparation Skill | 整理事实、洞察、策略和待确认假设，生成供用户审核的分析草稿 |
| Marketing Brief Generation Skill | 根据已确认的事实、洞察和策略形成结构化执行 Brief |
| Xiaohongshu Brief Mapping Skill | 将通用营销 Brief 映射为小红书商品种草场景的 Brief 模板 |

以上**不代表**：

- 所有 Skill 都进入 MVP；
- Skill 数量已经确认；
- 名称已经确认；
- 每项 Skill 都使用 LLM；
- 每项 Skill 都是独立节点；
- 每项 Skill 都是独立 Agent。

## Reusability Principle

Skill 应尽量围绕**稳定业务能力**设计，而不是围绕单一模型或供应商设计。例如优先使用：

```
Product Fact Extraction Skill
```

而不是：

```
GPT Product Analyzer
```

Skill 的业务契约应尽量保持稳定，内部模型、Prompt、检索实现和校验方式可以后续替换。

## Testability Principle

每个进入 MVP 的 Skill 至少需要能够测试：

- 正常输入；
- 信息缺失；
- 来源不存在；
- 资料冲突；
- 结构化输出失败；
- LLM 返回无效内容；
- 检索不到证据；
- 用户修改上游状态；
- 当前阶段已经失效；
- 重试或暂停行为。

> 具体测试框架尚未确定。

## Skill Documentation Principle

Skill 文档应描述**当前有效**的 Skill Specification。历史讨论和方案比较保存在 Session 或 RFC 中。Skill 文档**不得**把尚未确认的 Prompt、模型或技术实现写成当前事实。

## Reason

仅把 Prompt 文件称为 Skill，无法证明项目具备：

- 稳定业务能力；
- 明确执行边界；
- 结构化输入输出；
- 可测试性；
- 错误处理；
- 来源校验；
- 复用能力；
- 可靠性设计。

只把 Tool 函数称为 Skill，又无法表达完整业务 SOP。采用带契约的业务能力包定义，可以将用户所理解的「Agent 像员工，Skill 是 SOP」进一步转化为可以**执行、检查、复用和测试**的系统设计。这也能够体现项目所有者不仅会编写 Prompt，还能够设计 Agent 能力边界和可靠性机制。

## Impact

该决定将影响：

- Agent 架构；
- 工作流节点设计；
- Skill 目录和规范；
- Prompt 管理；
- Tool 设计；
- 结构化输出 Schema；
- 校验机制；
- RAG 调用；
- 暂停与错误处理；
- 测试策略；
- 评价指标；
- 开源仓库筛选；
- README 与简历项目表达；
- 后续 Agent 与 Multi-Agent 决策。

后续技术方案必须回答：**它是否支持将业务能力封装为具有明确输入输出、校验、失败处理和测试标准的可复用 Skill，而不是只管理 Prompt 文本？**

## Decision Boundary

**本决定已经确认：**

- Skill 是带执行契约的可复用业务能力包；
- Prompt 只是 Skill 的组成部分；
- Tool 不等于 Skill；
- Skill 不等于工作流节点；
- Skill 不等于独立 Agent；
- Skill 可以组合 LLM、确定性程序、检索和 Tool；
- Skill 需要输入输出契约；
- Skill 需要校验规则；
- Skill 需要失败与暂停条件；
- Skill 需要评价标准和测试能力；
- Skill 应以业务目标而不是模型供应商命名。

**本决定尚未确认：**

- Skill 的最终数量；
- 哪些候选 Skill 进入 MVP；
- Skill 文件目录；
- Skill Specification 最终模板；
- Skill 的代码接口；
- Skill 注册和发现机制；
- Skill 是否允许运行时动态选择；
- Prompt 管理方式；
- Schema 技术；
- Skill 版本机制；
- Skill 测试框架；
- 是否使用 Anthropic Skills、OpenAI Skills 或其他实现；
- LangGraph；
- Agent 数量；
- Multi-Agent；
- 具体 GitHub 基底仓库。

## Related Session

Session-002：Agent 工作流、可靠性架构与技术能力需求

## Related RFC

None（当前不创建 RFC）

## Supersedes

None

## Amends

None

## Notes

- 本决定为 Session-002 的首个 **Agent** 类型决定；对应 Question-007（Skill 应如何定义），将其在**定义层**解决（Skill 的契约化定义已确认；具体实现机制仍开放）。
- 候选 MVP Skills 列表与候选评估仅供后续讨论，**不**代表任何 Skill 已进入 MVP，也**不**代表任何候选被标记为 Adopt / Adapt。
- 本决定**不**确认 Anthropic Skills、OpenAI Skills、MCP、LangGraph、LangChain Tools 或任何具体 Agent 框架 / 目录 / 代码接口 / GitHub 仓库。
