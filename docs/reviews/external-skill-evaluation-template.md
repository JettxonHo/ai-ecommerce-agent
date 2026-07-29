# External Skill Evaluation 模板

> 本文件是**外部 Skill 评估模板**。复制本文件可创建某个具体候选 Skill 的评估记录，建议存放于 [external-skills/](external-skills/)。
> 来源：[DEC-016 — 优先研究成熟电商 Skills，并通过契约化改造后复用](../decisions/dec-016-external-skill-research-and-contract-based-adaptation.md)（Accepted，Agent，2026-07-27）。
>
> **重要：**
> - 本模板只包含 DEC-016 已确认的**评估结构**，不代表任何候选已被评估或进入 MVP。
> - 评估是**研究对象记录**，**不等于**采纳；任何候选须走完 DEC-016 的改造流程并形成 Accepted Decision 后才能成为项目正式 Skill。
> - 不得将第三方代码 / Prompt / 文件直接复制到正式 Skill 目录；复用须遵守 License 并记录来源（Attribution Principle）。
> - Reuse Recommendation 仅在评估完成时填写；未完成的候选保持「待评估」。

---

# External Skill Evaluation

## Repository and Skill

<!-- 仓库名称、Skill 名称、链接、访问日期、commit/版本。 -->

## License

<!-- License 类型、是否允许修改与再发布、是否需保留版权声明。 -->

## Original Business Goal

<!-- 该 Skill 原本解决什么业务问题。 -->

## Original Target User

## Inputs

## Workflow

## Outputs

## Reliability Mechanisms

<!-- 是否保留来源、是否区分事实与推断、是否编造数据、是否含冲突识别、是否支持资料不足标记。 -->

## Human Review Mechanisms

<!-- 是否存在确认 Gate、是否支持暂停、用户能否修改中间结果、修改后能否重新生成。 -->

## Strengths

## Conflicts with Current Decisions

<!-- 与 DEC-001~016 的冲突点，尤其 DEC-008（分级证据）、DEC-007（审核/暂停）、DEC-011（受约束 LLM）、DEC-015（Skill Contract）。 -->

## Reusable Components

<!-- 可复用的业务分析框架 / 执行步骤 / 输入清单 / 输出结构 / 风险规则 / 测试场景 / 确定性工具代码等。 -->

## Required Modifications

<!-- 需删除的无关模块、需重构为 Skill Contract 的部分、需增加的来源关系/结构化状态/暂停条件/校验/测试。 -->

## Reuse Recommendation

<!-- 仅评估完成时填写一项： -->

- Adopt
- Adapt
- Reference Only
- Reject

## Estimated Adaptation Effort

## Risks

<!-- 业务方向不匹配 / 依赖未确认技术 / 编造信息 / 无来源或伪引用 / 自动高风险操作 / License 不兼容 / 质量过低 / 改造成本过高。 -->

## Related MVP Skill

<!-- 若可对接，对应 DEC-015 候选 MVP Skill（如 Customer Insight Analysis Skill）。仅为候选关联，不代表进入 MVP。 -->

## Open Questions

---

## 评估维度参考（来自 DEC-016，至少覆盖）

1. **Business Fit** — 是否服务商品 / 内容运营人员；是否支持上新定位与营销 Brief；属核心分析 / 执行 / 扩展层；是否超出 MVP。
2. **Input Fit** — 所需输入；最低可运行输入下能否工作；是否支持增强输入；缺失信息处理；是否偷偷假设不存在的数据。
3. **Output Fit** — 能否映射事实 / 洞察 / 策略 / 执行四层；是否结构化；是否适合作为 Workflow State 条目；是否过大过宽。
4. **Evidence and Reliability** — 来源、事实/推断区分、编造风险、冲突识别、合规边界、资料不足标记。
5. **Human-in-the-loop** — 确认 Gate、暂停、中间结果可修改、修改后重生成。
6. **Contract Completeness** — 业务目标 / 适用条件 / 输入契约 / 执行步骤 / 工具依赖 / 输出契约 / 校验 / 失败暂停 / 评价 / 测试。
7. **Engineering Quality** — 可执行代码、测试、验证脚本、可拆分、运行时依赖、接入 Workflow State 难度。
8. **Legal and Attribution** — License 明确性、修改与再发布、版权声明、README 标注、原创贡献可说明性。
