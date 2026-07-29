# Prompt: 把 ChatGPT 输出交接给 Claude 归档

> 用途：当用户把 ChatGPT 的产品讨论输出粘贴给 Claude 时，可在输出前附上本提示词，以触发标准归档流程。
> 本提示词仅触发归档，**不**让 Claude 替 ChatGPT 或用户作出产品决定。

---

## 提示词正文（复制下方内容，附在 ChatGPT 输出前）

```
请按项目治理协议处理以下 ChatGPT 讨论输出。严格遵守 AGENTS.md 与 docs/governance/ 的规则：

1. 判断内容类型：识别 Discussion Summary、Fact、Observation、Assumption、Proposal、Alternative、Risk、Open Question、Deferred Topic、Proposed Decision、Accepted Decision、Rejected Decision、文档同步要求。严格区分 Proposed Decision 与 Accepted Decision。
2. 更新当前 Session：追加本轮讨论，不删除历史，不改原结论含义；保留推理过程、方案差异、风险、被否决方案、未决问题。
3. 判断是否需要 RFC：仅对重大、跨模块、难回滚议题创建/更新 Draft RFC，或建议需要 RFC；不得因一个建议自动创建大量 RFC。
4. 处理 Proposed Decisions：记入 Session 的 Proposed Decisions，状态保持 Proposed，不得写成 Accepted。
5. 处理用户确认：仅当用户明确表达批准语义时，才创建/更新 DEC、更新 decision-log、Session 标记 Accepted、更新 Current Truth、保留双向链接。
6. 同步 Current Truth：仅在决定被明确接受后才更新 product/agents/architecture 与 AGENTS.md。
7. 检查冲突：按文档优先级裁决，不得让旧 Session 覆盖新 Decision。
8. 输出 Archive Result 报告（Files Created / Files Updated / Decisions Recorded / RFC Changes / Current Specifications Updated / Open Questions Preserved / Conflicts or Ambiguities / Development Status）。

约束：
- 不得把 ChatGPT 的建议自动视为用户决定。
- 不得补充未经讨论的事实；信息缺失时保留为 Open Question。
- 不得编写业务实现代码；代码示例仅视为 Illustrative Example。
- 若存在歧义，保留为 Open Question 或 Conflict，不要自行补全。

以下是 ChatGPT 的讨论输出：
---
<在此粘贴 ChatGPT 输出>
```
