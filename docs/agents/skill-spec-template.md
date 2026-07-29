# Skill Specification 模板

> 本文件是**通用 Skill 规格模板**。复制本文件可创建某个具体 Skill 的当前规格。
> 来源：[DEC-015 — Skill 定义为带执行契约的可复用业务能力包](../decisions/dec-015-contract-based-reusable-business-skills.md)（Accepted，Agent，2026-07-27）。
>
> **重要：**
> - 本模板只包含 DEC-015 已确认的**通用结构**，**不**代表任何具体 Skill 已进入 MVP。
> - 创建本模板**不等于**创建任何具体 MVP Skill、Skill 代码、Prompt 实现、Tool 实现、Skill 注册器、动态路由或测试代码。
> - Skill Spec 描述**当前有效**的契约；尚未确认的 Prompt、模型或技术实现**不得**写成当前事实，应放入 `## Open Questions`。
> - Skill 编号方式、版本规则、最终 Schema 技术、目录与代码接口**均尚未确认**（见 DEC-015 Decision Boundary）。

---

# Skill：名称

<!-- 文件名建议：skill-<short-kebab-id>.md；具体编号方式待定。 -->

## Metadata

- Skill ID：
- Version：
- Status：<!-- Candidate / Draft / Active / Deprecated（具体状态枚举待定） -->
- Owner or Responsibility：

## Business Goal

<!-- 说明该 Skill 解决的业务任务（不是「调用 LLM 分析资料」这类空泛目标）。 -->

## Applicability

<!-- 何时可调用：当前业务阶段 / 需要哪些输入 / 哪些前置状态必须有效 / 哪些情况不适用 / 是否需要增强资料。 -->

## Preconditions

<!-- 前置阶段有效性、必需来源、用户确认等先决条件（失效的上游状态不得作为输入）。 -->

## Input Contract

<!-- Skill 可读取的输入（来自明确的 Workflow State、Tool 输出或用户输入；不得依赖隐含聊天上下文）。具体 Schema 技术待定。 -->

## Execution Steps

<!-- 高层执行过程，可含确定性处理 / LLM 分析 / RAG 检索 / Tool 调用 / 规则校验 / 暂停与人工补充。 -->

## Tool and Capability Dependencies

<!-- 显式声明依赖：文档解析 / 关键词检索 / 语义检索 / Schema 校验 / 风险规则 / 来源查询 / LLM / 用户确认等。不应隐式调用未声明能力。 -->

## Output Contract

<!-- 结构化输出，应可写入明确的 Workflow State 区域；LLM 自由文本不得成为唯一正式输出。 -->

## Validation Rules

<!-- 输出须通过的确定性校验（来源存在性 / Schema / 字段格式 / 失效状态拦截等）；可程序完成的不得全交 LLM 判断。 -->

## Failure and Pause Conditions

<!-- 区分：可自动重试 / 可降级继续 / 需要暂停 / 需要用户补充 / 无法执行。 -->

## Evaluation Criteria

<!-- 事实来源可追溯率 / 无依据事实数量 / Schema 通过率 / 冲突识别率 / 人工接受率 / 平均修改数 / 耗时 / 失败率等；具体阈值待定。 -->

## Test Scenarios

<!-- 至少覆盖：正常输入 / 信息缺失 / 来源不存在 / 资料冲突 / 结构化输出失败 / LLM 返回无效内容 / 检索无证据 / 用户修改上游 / 阶段已失效 / 重试或暂停。具体测试框架待定。 -->

## Related Workflow Stages

<!-- 与工作流阶段 / 节点的关系（Skill 与节点不要求一一对应）。 -->

## Related Decisions

<!-- 相关 DEC，至少引用 DEC-015。 -->

## Open Questions

<!-- 该 Skill 尚未确认的事项（数量、名称、实现框架、代码接口、测试框架等）。 -->
