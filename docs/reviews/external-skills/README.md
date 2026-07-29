# External Skills — 候选评估目录

> 本目录用于存放外部候选 Skill 的评估记录（每个候选一个文件，复制 [../external-skill-evaluation-template.md](../external-skill-evaluation-template.md)）。
> 来源：[DEC-016 — 优先研究成熟电商 Skills，并通过契约化改造后复用](../../decisions/dec-016-external-skill-research-and-contract-based-adaptation.md)（Accepted，Agent，2026-07-27）。

---

## 首轮候选（仅研究对象）

> **首轮三候选已全部完成评估：Reuse Recommendation 均为 Adapt（Candidate 1 [DEC-017](../../decisions/dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)、Candidate 2 [DEC-018](../../decisions/dec-018-adapt-product-differentiation-for-positioning-skill.md)、Candidate 3 [DEC-019](../../decisions/dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)，2026-07-27，仍为研究与改造方向，不代表已进入 MVP）。** Adapt 不等于已实现，候选须经 DEC-016 改造流程并形成后续 Skill Spec 才能成为正式 Skill。

| 候选 | 仓库 | 拟评估用途（来自 DEC-016） | 评估状态 |
|------|------|----------------------------|----------|
| Candidate 1 | `nexscope-ai/eCommerce-Skills/product-review-analysis` | Customer Insight Analysis Skill 的业务方法和输出框架供体 | **已评估：Adapt**（[DEC-017](../../decisions/dec-017-adapt-product-review-analysis-for-customer-insight-skill.md)；[评估记录](product-review-analysis-evaluation.md)；研究方向，未进入 MVP） |
| Candidate 2 | `nexscope-ai/eCommerce-Skills/product-differentiation-shopify` | Product Positioning Skill 的差异化分析、渐进输入和定位框架供体 | **已评估：Adapt**（[DEC-018](../../decisions/dec-018-adapt-product-differentiation-for-positioning-skill.md)；[评估记录](product-differentiation-shopify-evaluation.md)；研究方向，未进入 MVP） |
| Candidate 3 | `feichanggege/ecommerce-visual-copywriting-skill` | 输入缺失处理、人工确认 Gate、合规检查、执行层营销与视觉 Brief 的供体 | **已评估：Adapt**（[DEC-019](../../decisions/dec-019-adapt-ecommerce-visual-copywriting-for-execution-brief-skills.md)；[评估记录](ecommerce-visual-copywriting-skill-evaluation.md)；研究方向，未进入 MVP） |

---

## 规则

- 评估记录只是**研究对象记录**，**不等于**采纳；任何候选须走完 DEC-016 的「发现→审计→裁剪→重构为 Skill Contract→校验→接入 Workflow State」流程，并形成 Accepted Decision 后才能成为项目正式 Skill。
- **不得**将第三方代码 / Prompt / 文件直接复制到正式 Skill 目录；复用须遵守 License 并记录来源。
- **不得**擅自将任何候选标记为 Adopt / Adapt / Reference Only 或进入 MVP。
