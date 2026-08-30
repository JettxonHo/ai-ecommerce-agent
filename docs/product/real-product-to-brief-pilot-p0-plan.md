# Real Product-to-Brief Pilot — P0 Admission and Contract Freeze Plan

> **Merge-durable status transition:** before this record reaches `main`, P01–P08 are `ADMISSION_PENDING_REVIEW`, the denominator is `FREEZE_PENDING_REVIEW`, P0 is `CONTRACT_FREEZE_PENDING`, and the Pilot is `ACTIVE`. Once this record is present on `main`, P01–P08 are `ADMITTED`, the denominator is exactly eight frozen product/attempt units, P0 is `P0_CONTRACT_FROZEN`, and P1 is `READY_NOT_STARTED`.
>
> **Execution boundary:** `PILOT_EXECUTION_AUTHORIZATION = NOT_AUTHORIZED`. This plan performs no observation, business run, Provider call, participant test, numerator calculation, export, or P1/P2 work.

## 1. Authority and scope

This is the canonical P0 admission and contract-freeze record for [Issue #341](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341). It specializes, but does not amend, the accepted [DEC-086](../decisions/dec-086-real-product-to-brief-pilot.md), [DEC-087](../decisions/dec-087-mvp0l-terminal-rebaseline-and-pilot-activation.md), [Real Product-to-Brief Pilot Goal](../goals/real-product-to-brief-pilot-goal.md), and [Real Product-to-Brief Pilot Contract](real-product-to-brief-pilot-contract.md).

Owner/evidence records used for this freeze are the Issue comments [5462712363](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5462712363), [5462825047](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5462825047), [5467295279](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5467295279), and [5467339162](https://github.com/JettxonHo/ai-ecommerce-agent/issues/341#issuecomment-5467339162). The private research artifacts were read only at their Owner-authorized locations:

- `/Users/ketchup/Private/ai-ecommerce-pilot/inputs/p0-admission-manifest-draft.yaml`
- `/Users/ketchup/Private/ai-ecommerce-pilot/inputs/p0-source-index.md`

The private manifest remains a `RESEARCH_DRAFT_ONLY` input history. This repository record carries only reviewed, sanitized metadata and contract text; it does not copy protected images, long marketing passages, credentials, cookies, personal data, raw Provider payloads, or other unrestricted private material.

## 2. Merge-effective P0 result

The P0 record freezes the following facts before any Pilot observation:

- exact cohort `N = 8`;
- exactly two categories, four samples in each;
- exactly eight admitted product/attempt units, one stable `sample_id` and one score-bearing outcome per unit;
- one qualifying product counts once even when both Marketing and Xiaohongshu exports exist;
- the approved-export formula and `>= 80%` threshold are registered, with no numerator recorded in P0;
- `BLOCKED` remains in the denominator, while `EXCLUDED` is available only before admission and observation;
- no outcome-driven replacement, retry, removal or reclassification is permitted after denominator lock;
- one author/operator role and one confirmed, consented non-author trial-operator role;
- human-review dimensions, sanitized evidence fields and private evidence destinations;
- the sole future P1 handoff: `post-confirm / no-export blocker`, provider-free characterization only.

P0 does not claim that any product has been run, reviewed for business usability, exported, adopted, or counted in a numerator.

## 3. Exact admitted cohort

### 3.1 Cohort and categories

| Category | Samples | Count |
|---|---|---:|
| Category A — consumer electronics / digital accessories | P01, P02, P03, P04 | 4 |
| Category B — daily consumer goods / lifestyle goods | P05, P06, P07, P08 | 4 |
| **Total** | **P01–P08** | **8** |

### 3.2 Stable sample identities

These are the exact Owner-selected identities. No brand, model, specification, claim, source or participant information is inferred beyond the reviewed evidence.

| `sample_id` | Category | Admitted product identity / variant designation |
|---|---|---|
| `P01` | A | Anker Nano Power Bank A1259, Black Stone, official-store variant `42733233766550` |
| `P02` | A | Sony WF-1000XM5, Black / US, `WF1000XM5/B` |
| `P03` | A | IKEA BERGENES, article `104.579.99` |
| `P04` | A | Apple Magic Keyboard with Touch ID and Numeric Keypad, US English / Black Keys, `MXK83LL/A` |
| `P05` | B | Zojirushi SU-BA48, Midnight Black, `SU-BA48-BM` |
| `P06` | B | IKEA SAMLA 12-gallon Clear Box with Lid, composite `694.407.61` |
| `P07` | B | IKEA KNALLA, Black Umbrella, `602.823.32` |
| `P08` | B | The North Face Borealis Backpack 28L, `NF0A52SE / 4HF / OS` |

## 4. Per-sample admission evidence summary

The Owner-authorized manifest supplies structurally complete F1–F9 for every sample. The source index contains 22 unique source IDs; every F4/F7/F8 reference resolves to that index. Source IDs below are references only; the private source pages and raw material remain outside Git.

`F5` and `F6` statuses below are **OWNER_APPROVED** by comment 5467295279. The private manifest's historical `PROPOSED_PENDING_OWNER_APPROVAL` labels are not rewritten. Every sample has `permission_basis = OWNER_APPROVED` and `sanitization_status = NOT_REQUIRED` under the approved public-fact/paraphrase/structured-field boundary. `UNVERIFIED` fields are counted and constrained by the binding rule `UNVERIFIED -> CLAIM NOT ALLOWED`.

| Sample | F1–F9 | F4/F7/F8 source IDs (unique) | F5 | F6 | Permission / sanitization | `UNVERIFIED` count |
|---|---|---|---:|---:|---|---:|
| `P01` | complete | P01-S01, P01-S02, P01-S03 (3) | 2, OWNER_APPROVED | 7, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 3 |
| `P02` | complete | P02-S01, P02-S02, P02-S03 (3) | 3, OWNER_APPROVED | 8, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 3 |
| `P03` | complete | P03-S01, P03-S02, P03-S03 (3) | 3, OWNER_APPROVED | 6, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 3 |
| `P04` | complete | P04-S01, P04-S02, P04-S03 (3) | 3, OWNER_APPROVED | 6, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 4 |
| `P05` | complete | P05-S01, P05-S02, P05-S03 (3) | 3, OWNER_APPROVED | 6, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 3 |
| `P06` | complete | P06-S01, P06-S02, P06-S03 (3) | 3, OWNER_APPROVED | 6, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 3 |
| `P07` | complete | P07-S01, P07-S02, P07-S03 (3) | 2, OWNER_APPROVED | 6, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 3 |
| `P08` | complete | P08-S01 (1) | 3, OWNER_APPROVED | 7, OWNER_APPROVED | OWNER_APPROVED / NOT_REQUIRED | 3 |
| **Total / invariant** | **8/8 complete** | **22/22 resolve** | **22 items** | **52 items** | **all eight** | **25** |

The 25 `UNVERIFIED` entries are explicit restrictions, not inferred product facts. They may not become claims. They do not independently block this admission unless a later stage proves a particular field necessary for fair execution or evaluation; that later stage must stop and return to the Owner if so.

## 5. Frozen F5/F6 contract content

The following Chinese items are the complete reviewed and sanitized F5/F6 content from the Owner-approved candidate material, copied verbatim as the normative contract. They are included because these fields are admission-critical and must remain stable for later human review. No item is added, broadened or converted into a marketing claim.

### P01 — Anker Nano Power Bank A1259

**F5 mandatory messages (2) — normative verbatim:**

1. 商品身份必须保留为 Anker Nano Power Bank、型号 A1259、标称 10,000mAh、内置 USB-C 线。
2. 如提及功率，必须区分 USB-C 单口最高 30W、USB-A 最高 22.5W与多口总输出最高 24W。

**F6 prohibited/restricted claims (7) — normative verbatim:**

1. 不得把 10,000mAh 标称总容量表述为可用输出容量，或据此保证能为某设备完整充电若干次。
2. 不得声称所有接口、所有设备或多口同时使用时均可达到 30W。
3. 不得保证任何设备或电源本体在固定分钟数内达到固定百分比。
4. 不得声称适配所有 USB-C、手机、平板或笔记本；实际功率取决于设备、协议和连接条件。
5. 不得提出未经核验的防水、防摔、航空携带、安全保护或具体认证结论。
6. 不得把 EU Declaration 落地页扩展成未经核验的具体认证清单。
7. 不得使用最好、第一、百分百等绝对化或最高级结论，也不得声称内置线具有未核验的弯折寿命。

### P02 — Sony WF-1000XM5

**F5 mandatory messages (3) — normative verbatim:**

1. 商品身份必须保留为 Sony WF-1000XM5 黑色美国款，designation WF1000XM5/B。
2. 如提及续航，必须使用最长并带 codec、NC on/off、功能和使用条件限定。
3. 如提及防泼溅，必须明确仅耳机本体为 IPX4 equivalent，充电盒不防水且不得浸水。

**F6 prohibited/restricted claims (8) — normative verbatim:**

1. 不得称为防水、可浸水或可游泳使用；不得把 IPX4 扩展到充电盒。
2. 不得把 8/12 小时写成所有 codec、功能设置和环境下的保证续航。
3. 不得保证 3 分钟充电在任何条件下都得到完整 1 小时播放。
4. 不得把 32.80ft 描述为穿墙、复杂干扰环境或任意设备上的保证连接距离。
5. 不得声称适配所有手机、电脑、操作系统或 Bluetooth 设备。
6. 不得声称 LDAC、LC3、多点连接或应用功能在所有设备、地区和固件版本中均可用。
7. 不得声称最佳降噪、市场第一、保证通话清晰、听力保护、治疗或健康改善。
8. 不得依赖官方商品页中标明为 generated FAQ 的内容作为核心事实。

### P03 — IKEA BERGENES

**F5 mandatory messages (3) — normative verbatim:**

1. 商品必须明确为 IKEA BERGENES，article number 104.579.99。
2. 若描述兼容性，必须保留多数手机和平板、最大 11 英寸的边界，并说明逐设备/保护壳适配未核验。
3. 若描述材质，必须写为竹材与透明丙烯酸清漆。

**F6 prohibited/restricted claims (6) — normative verbatim:**

1. 不得声称适合所有手机、平板或所有保护壳，也不得声称适合超过 11 英寸的设备。
2. 不得猜测卡槽宽度、设备厚度上限或具体机型兼容性。
3. 不得声称可调角度、可调高度、旋转、折叠、无线充电、MagSafe 或充电口预留。
4. 不得声称未经来源支持的承重、稳定性、防滑、防跌落、防水、安全或耐久性能。
5. 不得仅因采用竹材而推导环保认证、可持续或低碳结论。
6. 不得提出人体工学、腕部健康或治疗相关结论。

### P04 — Apple Magic Keyboard with Touch ID and Numeric Keypad

**F5 mandatory messages (3) — normative verbatim:**

1. 具体变体必须写明 MXK83LL/A、美式英语布局、黑色键帽、USB-C 版本。
2. Touch ID 与完整系统要求必须限定为 Apple silicon Mac 和 macOS 15.1 或更新版本。
3. 若提及续航，必须保留约一个月或更久及受设置、使用和其他条件影响的限定。

**F6 prohibited/restricted claims (6) — normative verbatim:**

1. 不得声称该 USB-C 型号在 Intel Mac 或 macOS 15.1 之前版本上具备完整功能。
2. 不得声称 Touch ID 可在所有设备或操作系统上使用，也不得把它扩大为账户或整机的绝对安全保证。
3. 不得把约一个月或更久描述为固定或保证续航。
4. 不得声称具备背光、机械轴、特定键程、无线距离、快充、防泼溅、防水或耐久等级。
5. 不得声称具有未经来源支持的游戏延迟、专业电竞或人体工学健康优势。
6. 不得根据商品页列出的 iPhone/iPad 名单推导 Touch ID 或完整功能兼容性。

### P05 — Zojirushi SU-BA48

**F5 mandatory messages (3) — normative verbatim:**

1. 商品身份必须写明 SU-BA48-BM、0.48L、Midnight Black，不得与 SU-BA36 或其他颜色混用。
2. 如使用保温或保冷数字，必须同时保留 6 小时、起始温度、室温、规定装量和直立放置条件。
3. 如宣传运动饮料或洗碗机适用，必须同时保留使用后立即清洗，以及仅限家用洗碗机并遵守说明书的边界。

**F6 prohibited/restricted claims (6) — normative verbatim:**

1. 不得声称零渗漏、百分百防漏或任何条件下均不会洒漏。
2. 不得宣传可盛装干冰、碳酸饮料、高盐汤品、牛奶/乳饮料、果汁、果肉或茶叶。
3. 不得把 74°C / 7°C 的 6 小时结果扩大为任意环境、装量或使用姿态均成立。
4. 不得把家用洗碗机适用扩大为商用洗碗机、商用烘干机或无条件高温清洗。
5. 不得声称微波炉、直火、电热器或 IH 加热兼容。
6. 不得声称未核验的 BPA、FDA、食品接触认证、健康功效或特定车载杯架兼容性。

### P06 — IKEA SAMLA 12-gallon Clear Box with Lid

**F5 mandatory messages (3) — normative verbatim:**

1. 商品身份必须写明组合货号 694.407.61，并说明其包含盒体 301.029.74 与盒盖 704.550.87。
2. 必须保留仅建议室内使用、未获准用于食品接触的边界。
3. 涉及叠放或密闭性时，必须保留最大建议叠放高度 35in、重物置底与幼儿不得进入带盖盒体的安全要求。

**F6 prohibited/restricted claims (6) — normative verbatim:**

1. 不得声称适合直接接触食品、食品级、可作食品保鲜盒或饮用水容器。
2. 不得声称户外适用、防水、防雨、防潮或具备任何 IP/灰尘防护等级。
3. 不得声称儿童安全、可供儿童进入或忽略带盖后的气密警示。
4. 不得声称未核验的承重、抗摔、抗冲击、耐高低温或长期重载能力。
5. 不得把盖上后气密描述为食品保鲜、真空密封或防水密封性能。
6. 不得把 12 gallon 组合款的尺寸、组件或货号扩展到 17 gallon 或其他区域款式。

### P07 — IKEA KNALLA Black Umbrella

**F5 mandatory messages (2) — normative verbatim:**

1. 商品必须明确为 IKEA KNALLA 黑色雨伞，article number 602.823.32，不得与可折叠 KNALLA 款混淆。
2. 如提及开合方式，只能表述为按键自动展开；不得声称自动收伞。

**F6 prohibited/restricted claims (6) — normative verbatim:**

1. 不得声称具备具体防风等级、耐受风速、抗翻转或任何风况保证。
2. 不得声称防水等级、永久不漏、暴雨或任何环境下均能保持干燥。
3. 不得声称可自动收伞、可折叠或具备未列明的收纳功能。
4. 不得声称经测试可容纳两人、适合所有身高或具有未核验的耐久寿命。
5. 不得把至少 90% 再生聚酯伞面扩大为整把雨伞 90% 再生材料。
6. 不得声称 UV/UPF 防护、安全认证或最好、最牢固等最高级结论。

### P08 — The North Face Borealis Backpack 28L

**F5 mandatory messages (3) — normative verbatim:**

1. 商品必须明确为 Borealis Backpack 28L，Style NF0A52SE，TNF Black/TNF Black 4HF，OS。
2. 如提及容量，必须使用 28L；不得与其他 Borealis 变体混用。
3. 如提及笔记本兼容性，必须限定为官方所列独立 16 英寸隔层与 34.9 × 28.6cm 隔层尺寸，实际设备适配取决于外形尺寸。

**F6 prohibited/restricted claims (7) — normative verbatim:**

1. 不得声称防水、可浸水或具备任何 IP 等级；non-PFC DWR 只能按来源原意表述。
2. 不得把 non-PFC DWR 改写为 PFAS-free、无氟或永久防泼水。
3. 不得保证所有标称 16 英寸笔记本都能装入；应以设备实际外形与隔层尺寸为准。
4. 不得声称未经核验的最大承重、抗摔、抗冲击或耐磨等级。
5. 不得声称符合所有航空公司随身行李规则。
6. 不得把纯色面料的再生尼龙规格扩大为整包所有部件均为再生材料。
7. 不得将背负系统或任何认证扩大为治疗、脊椎健康保证或适合所有体型。

**Shared F6 baseline rule — normative verbatim:** 不得声称任何未被 factual basis 支持的规格、认证、性能、时长、兼容性、安全性、健康功效、绝对化或最高级结论。

## 6. Admission, denominator and outcome semantics

### Admission gate

An identity is admitted only before observation when all of the following are true:

1. the Owner has authorized use of the real or authorized sanitized-real material;
2. F1–F9 are present, including explicit F5/F6 values and factual basis;
3. the sample belongs to the frozen two-category cohort and has a stable `sample_id`;
4. the material fits the private-local evidence boundary and contains no prohibited Secret, credential, cookie, personal or uncontrolled production material.

The eight samples above satisfy the recorded pre-admission evidence; their merge-effective status is `ADMITTED` only once this record is present on `main`. If an admission-critical fact or permission boundary later becomes invalid before observation, the sample must be handled under the pre-admission rule and cannot be repaired through an outcome-driven reclassification.

### Fixed denominator

Before observation, the denominator is exactly eight P0-admitted product/attempt units:

```text
approved_export_completion = qualifying admitted products / all P0-admitted products
```

Each admitted product contributes exactly once and has one score-bearing final outcome. A qualifying product yields at least one human-approved immutable Marketing or Xiaohongshu Markdown export. Both exports are not required unless separately accepted, and two exports for one product still count once. The threshold remains `approved_export_completion >= 80%`; with eight units, `7/8 = 87.5%` is the smallest passing count and `6/8 = 75%` does not pass. The threshold does not waive any other Pilot completion condition.

P0 registers the denominator and formula only. It creates no numerator and does not infer a future result.

### Terminal classifications

| Classification | Frozen meaning | Denominator / numerator |
|---|---|---|
| `PASS` | At least one qualifying human-approved immutable export exists and all applicable critical human-review gates pass. | Denominator and numerator once. |
| `FAIL` | The admitted unit runs or reaches review but yields no qualifying approved export, including a terminal Provider, schema, domain or export failure. | Denominator; never numerator. |
| `BLOCKED` | After admission, an external, human, access, environment or unresolved execution gate prevents a qualifying terminal result. It is not success and may not be silently retried away. | Remains denominator; never numerator. |
| `EXCLUDED` | The candidate fails the fixed admission rule before observation and before any Provider/business run. | Never denominator. |

Missing, ambiguous or unreviewed outcomes for an admitted sample remain visible as `BLOCKED` or `FAIL`; they cannot be converted to `EXCLUDED`. After denominator lock, no admitted unit may be removed, replaced, reclassified as `EXCLUDED`, or retried merely to improve the ratio.

## 7. Participants

Only sanitized role/status metadata is retained:

- **Author/operator:** the project author may prepare the cohort, operate the product and perform declared review steps.
- **Non-author trial operator:** `non_author_trial_operator_01 = CONFIRMED_AND_CONSENTED`. The Owner identified and obtained consent from a real non-author who was not involved in core design, implementation or cohort selection and who is expected to perform the later non-author acceptance role.

No name, contact detail or other PII is recorded. Agents do not recruit, contact, fabricate or enroll participants. The participant gate is cleared for this P0 contract freeze; the later P4 clean/other Apple Silicon acceptance remains a separate Stage activity and is not performed here.

## 8. Human-review schema

Each future admitted-sample review must record the following seven dimensions independently from automated checks:

1. **Product fact correctness:** key facts are correct and supported by the admitted input/source.
2. **Mandatory messages:** every applicable F5 message is retained without material distortion.
3. **Prohibited claims:** F6 restrictions and limitations are respected.
4. **Fabrication/misleading content:** no severe unsupported invention, false certainty or materially misleading statement.
5. **Marketing Brief usability:** the relevant Brief is usable for the operator's next step; material edits are recorded.
6. **Xiaohongshu consistency:** when a Xiaohongshu mapping exists or is used as the qualifying export, it is consistent with the confirmed Brief. `NOT_APPLICABLE` is allowed only where the unchanged Pilot Contract permits a Marketing-only qualifying export; an inconsistent produced mapping cannot be hidden as not applicable.
7. **Markdown delivery:** every qualifying export is readable UTF-8 Markdown, downloadable, immutable and traceable to sample, Task/result/review and export identities.

The review record also includes reviewer role, review time, each dimension decision, material edits, overall classification and a concise rationale. Any incorrect critical fact, missing mandatory message, prohibited claim, severe fabrication/misleading content or unusable qualifying export prevents `PASS`.

## 9. Sanitized evidence schema and destinations

### 9.1 Per-sample evidence fields

The future evidence record links:

- P0 `sample_id`, permitted input/source reference and input version;
- repository commit and applicable runtime/profile/schema versions;
- Task, result, review and export identities;
- Provider call count, duration, token usage and available cost data;
- retry/recovery/replay and manual-intervention counts;
- automated gate outcomes;
- the human-review record and terminal `PASS`/`FAIL`/`BLOCKED` outcome;
- immutable export reference(s), when present.

Provider payloads, reasoning, Secrets, credentials, cookies, personal data and unapproved raw product material are never stored in Git or retained evidence. P0 adds no hash requirement.

### 9.2 Owner-selected private roots

The following exact roots are frozen outside Git; this PR creates none of them:

| Destination | Frozen use |
|---|---|
| `/Users/ketchup/Private/ai-ecommerce-pilot/inputs/` | permitted real/sanitized-real material, input versions and controlled source references |
| `/Users/ketchup/Private/ai-ecommerce-pilot/evidence/` | sanitized per-sample evidence and automated gate records |
| `/Users/ketchup/Private/ai-ecommerce-pilot/reviews/` | human-review records and decisions |
| `/Users/ketchup/Private/ai-ecommerce-pilot/exports/` | immutable Marketing/Xiaohongshu Markdown export artifacts and references |
| `/Users/ketchup/Private/ai-ecommerce-pilot/summary/` | final sanitized aggregate summary/evidence pack |

Only a separately reviewed sanitized subset may enter Git. A later Stage must stop if a destination, retention boundary or material permission changes.

## 10. Stage and execution boundaries

- The exact order remains **P0 → P1 → P2 → P3 → P4 → P5 → P6**, one active Stage and one Issue/PR per observable outcome.
- P0 is docs-only admission/contract freeze. It performs no business run and no Provider call.
- Future P1 carries only `post-confirm / no-export blocker` as a provider-free characterization target. It does not infer a root cause, approve a repair, call DeepSeek, access a Secret, retry L5, repair MVP0L, start L6, or start Agent UI.
- The only future real-AI contract remains the official DeepSeek API with `deepseek-v4-pro`; every later paid run needs a new exact-commit Owner authorization for tasks, calls, cost and stop rules. No authorization is inherited here.
- `PILOT_EXECUTION_AUTHORIZATION` remains `NOT_AUTHORIZED`. No Provider/DeepSeek, Secret/env, Docker/PostgreSQL/API/Web/browser, observation, numerator, participant test, P1/P2, MVP0L repair/L5 retry, L6, Agent UI, publishing, platform action, PR #299, old Issue or Dependabot action is authorized.

## 11. Validation and handoff

This record is accepted for merge only when the exact seven-path scope is demonstrated:

1. only the allowlisted paths are changed;
2. the plan and Session-012 are present;
3. DEC-086, DEC-087, the existing Pilot Contract, Session-010/011, the L5 review, product code and tests remain byte-identical;
4. all cohort uniqueness/category/source/F1–F9/F5/F6/permission/sanitization invariants above validate against the Owner-authorized artifacts without modifying them;
5. links, headings, code fences, stale-status wording and `git diff --check` pass;
6. fresh Required Checks are green and an independent reviewer approves the docs-only PR.

The implementer does not review, approve or merge the PR. After merge, the merge-effective statuses in Section 2 are the only P0 admission truth. The next work item is a separately contracted P1; this record is not Pilot execution authorization.
