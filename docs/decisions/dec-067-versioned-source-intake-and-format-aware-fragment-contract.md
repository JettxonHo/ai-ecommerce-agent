# DEC-067：采用版本化 Source 关联、逐资料耐久处理与格式感知 Fragment 契约

## Metadata

- **Status:** Accepted
- **Date:** 2026-08-07
- **Decision Type:** Source Architecture / Processing Lifecycle / Evidence Provenance / Fragment and Locator Contract
- **Source:** Session-003；用户明确接受 `P-58A / P-59A / P-60A`
- **Related Issue:** [#56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56)
- **Related PR:** [#57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)

## Context

RFC-002 已将 PostgreSQL 确立为 Source / Evidence 身份、关系、状态与 Provenance 的权威，并把 Retrieval Index 定义为可重建的非权威派生层；DEC-025 / DEC-032 已定义 Source Version、Fragment、Evidence Link、Source Set Version 与 Evidence Package 的概念边界。产品规格又要求单个坏文件不回滚其他已接受资料、资料移除 / 替换可逆且可追踪，并且首个 Goal 只处理结构化表单 / 文本、TXT / Markdown、文本型 PDF 与评论 CSV。

尚未闭合的是 Task 成员关系放在哪里、输入如何登记与处理、部分接受如何表达，以及四类输入怎样产生诚实可定位的 Fragment。DEC-032 的概念 Evidence Package 还包含一个额外 `package_hash`，与后续接受的适度校验治理不再相称。

## Decision

### 1. Authoritative Versioned Source Graph

- RFC-002 的 PostgreSQL Source / Evidence 图继续是唯一权威。内容位置继续由其 Inline / External 分类决定；本决定不选择对象存储 Provider，也不建立第二事实源。
- `Source`、不可变 `SourceVersion`、可变 `TaskSourceAssociation` 与版本化 `DerivedArtifact` 必须分离。Task 的 active / removed / replaced 成员关系由带单调 `revision` 的 `TaskSourceAssociation` 表达，不直接写入 Source identity。
- remove / replace 更新关联及其影响 / 失效路径，不改写历史 Source Version，也不等于物理删除。用户资料仍按 DEC-061 默认 Task-scoped；这一隔离通过关联与查询范围实现，而不是复制或合并 Source identity。
- 每次处理或检索输入由 `SourceSetVersion` 固定，manifest 至少引用稳定的 Source Association identity、精确 Source Version identity 与当时 eligibility。历史结果不得在读取时改绑到 Source 的最新版本。
- Parser、Fragmenter 或其他派生处理规则改变时创建新的 Derived Artifact / Fragment 集合及可读组件版本引用，不原地覆盖旧 Provenance。

### 2. Readable Reproducibility Without a Package Digest

- Evidence Package 的可复现输入由 Source Set manifest、Retrieval Plan version、Retrieval Run identities、Derived Artifact / Fragment identities 与可读组件版本组合说明。
- 不新增或公开 `package_hash`、SHA-256 或 client-visible digest；Evidence Package 接受、质量、置信或审核结果不得由 Digest 推断。
- DEC-032 中“计算 `package_hash`”步骤与 EvidencePackage 概念字段 `package_hash` 由本决定明确移除。DEC-032 的其余 Direct-first、Scope / Version filtering、Candidate / Formal Evidence 边界与可复现要求保持有效。
- RFC-002 已接受的 ContentObject / 外部对象完整性边界保持私有、算法中立且不向 Evidence Package 或公共 API 扩散；本决定不新增该边界之外的完整性机制。

### 3. Per-source Atomic Registration and Durable Processing

- 多项输入请求是 batch envelope，不是一个全成全败的业务聚合。每个 Source 独立完成边界校验与原子登记；不支持的媒体类型、超限或其他边界无效项逐项拒绝，合法兄弟项不回滚。
- 成功登记先提交不可变的 submitted input reference 与 Source Version，再由 RFC-003 已接受的 Durable Work Intent / Worker / Run 路径处理；进程内 background task 不承担正确性。
- 小型结构化表单 / 手工文本可以同步完成确定性规范化。TXT / Markdown、文本型 PDF 与评论 CSV 使用同一显式处理协议并允许异步完成；Frontend 不得模拟服务端终态。
- Source Version processing lifecycle 固定为 `registered / processing / ready / ready_with_rejections / failed / superseded`。Task association、availability、integrity 与 processing status 是不同维度，不塞入同一个枚举。
- typed per-item result 返回已接受 identity 或 RFC-004 Problem item detail。评论 CSV 可在有效子集仍诚实可用时接受合法 Record，并以有界 row issues 标记 `ready_with_rejections`；TXT / Markdown / PDF 不制造页级伪部分成功。
- 处理失败保留已登记 Source Version 与安全失败摘要，但不产生 eligible Fragment、Source Set membership 或 Current Truth。技术 Retry 保持同一逻辑操作并创建新 Attempt；用户 replace 创建新的 Source Version / association basis。
- processing success 只是候选资料可用，不等于 Fact verified、QC passed、Strategy approved 或下游 Workflow 已获启动授权。

### 4. Format-aware Fragment and Locator Lanes

- structured form / manual text：每个已接受字段形成 Record，并使用 `formSection / fieldName` Locator；长字段可在同一字段边界内产生多个 Fragment。
- TXT / Markdown：使用 heading / paragraph-aware block，Locator 保留规范化 line range 与 heading path。
- text PDF：使用 page-bound extracted block，Locator 保留 page number 与该页提取文本内的 block / character range；不承诺 OCR bounding box 或图片坐标。
- review CSV：每个合法 row 是一个独立 Record，Locator 保留 source row number 与稳定 column names；可选 sentence-level Fragment 必须保留父 Record identity，不能把一条评论计算成多个用户。
- Fragment 不跨 Source Version、Record identity 或 PDF page。展示 / 引证使用原文；normalized search text 是独立派生字段，不能替代用户可核对的 evidence text。
- 结构单元只为已接受的 context bound 作确定性组合 / 拆分。目标尺寸与有限 overlap 由后续 Retrieval Evaluation 控制，不成为产品语义；overlap 不产生额外独立证据计数。
- `fragmentId` 只在精确 Source Version + Derived Artifact version 内稳定。重新解析或 Fragmenter 版本变化创建新 identity；历史 Evidence Link 仍解析旧 Fragment，并遵守 availability / retention 规则。
- 验证只覆盖四条受支持 Lane 的代表性路径与 Anchor SKU Fixture，不扩展 OCR、任意办公格式或低概率字符变体矩阵。

## Alternatives Considered

### Self-contained Evidence Package + All-or-nothing Intake + Universal Token Chunks

把全文复制进每个 Evidence Package、任一输入失败就回滚整批，并将所有格式切成统一 token chunk。该组合表面统一，但会复制私有资料、破坏历史移除 / 保留边界、丢失 CSV 可计数 Record 和 PDF 页定位，并直接违反已接受的单文件部分接受产品行为，因此不采用。

### Latest-at-read Source + Eager HTTP Parsing + Query-time Fragments

读取时解析最新 Source、在上传请求内完成全部处理，并按查询临时产生 Fragment。该组合实现记录较少，但历史结果无法证明实际输入，客户端断开会破坏长任务恢复，Fragment / Locator 也无法稳定支撑 Evidence Link，因此不采用。

## Reason

该方案把权威 Source 图、Task 成员关系、耐久处理和 Evidence 引用拆成可独立验证的职责，同时直接满足单文件部分接受、异步处理、可逆替换、评论可计数和文本 PDF 可核对等核心演示行为。它移除了没有额外业务价值的 Evidence Package digest，又保留 RFC-002 已接受的核心对象完整性边界，符合适度校验原则。

## Consequences

- RFC-005 DQ-01～03 已闭合；DQ-04～10 与 RFC-005 整体仍未接受。
- Source / Evidence、Worker、API 与 Frontend 实现必须共享上述 processing / association / locator 语义，不能各自发明平行状态。
- SourceSet manifest 与组件版本比单个 opaque digest 更易审阅，但重放时必须比较结构化 reference set。
- 四条处理 Lane 比通用 splitter 多出有限实现路径；该复杂度来自真实格式语义，不扩展为通用文档平台。
- 物理对象一致性、保留 / Hold / 删除、精确 Parser / Embedding / Index 技术与参数仍由后续 RFC / Readiness / Goal Gate 决定。

## Relationships

- **Amends [DEC-025](dec-025-versioned-sources-fragments-and-evidence-links.md)：** Task 成员关系以独立 `TaskSourceAssociation` 表达，并把四类 Fragment / Locator Lane 具体化；其 Evidence Link 与 Source Version 不变量保持有效。
- **Amends [DEC-032](dec-032-hybrid-retrieval-and-evidence-runtime-architecture.md)：** 移除 Evidence Package `package_hash` 步骤 / 字段；其余 Retrieval 与 Evidence 边界不变。
- **Amends [DEC-033](dec-033-workflow-runtime-failure-recovery-retry-and-observability-contract.md)：** 将概念 Source processing 状态收敛为本决定的六值生命周期，并把 association / availability / integrity 分离；其 Retry / Run / error 规则不变。
- **Concretizes [DEC-045](dec-045-minimum-input-file-limits-and-conflict-handling.md)：** 用 per-source result 与 CSV row issues 实现已接受的单文件部分接受。
- **Concretizes [DEC-061](dec-061-task-scoped-private-material-and-reversible-removal.md)：** 用 revisioned Task association 实现 Task-scoped、remove / replace 与影响路径。
- **Conforms to [DEC-039](dec-039-proportional-validation-and-review-governance.md)：** 不新增 Hash / SHA-256，不堆叠不现实防御性变体。
- **Input to [RFC-005](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md)：** 接受 DQ-01～03，并开放 DQ-04～06 的策划讨论。

## Authorization Boundary

本决定只授权 Decision、RFC、Current Truth、Readiness、Testing 与 Traceability 文档同步：

- 不接受 RFC-005 整体，不授权合并 PR #57 或关闭 Issue #56；
- 不授权创建 Source Schema、数据库表、Migration、对象存储、Parser、Fragmenter、Embedding、Index、Retrieval Runtime、API、Frontend、Fixture 或 Test Implementation；
- 不授权依赖安装、Technical Spike、Live Provider 调用、RFC-007、业务实现或长期 Goal；
- 下一 Gate 仅为 RFC-005 DQ-04～06 的 PostgreSQL Retrieval topology、Embedding / Index versioning 与 deterministic planning / fusion 决策。

## Accepted From

- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)：P-58A / P-59A / P-60A；用户于 2026-08-07 明确回复“接受 P-58A、P-59A、P-60A”。
- [RFC-005 Proposal Round 1](../rfcs/rfc-005-source-processing-and-retrieval-architecture.md#proposal-round-1)。
- GitHub：[Issue #56](https://github.com/JettxonHo/ai-ecommerce-agent/issues/56) / [Draft PR #57](https://github.com/JettxonHo/ai-ecommerce-agent/pull/57)。
