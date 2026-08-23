import type { TaskCurrentResult } from "../gateway";

type JsonRecord = Record<string, unknown>;

export type ResultBriefKind = "marketing" | "xiaohongshu";

export type ResultProjection = Readonly<{
  positioningTitle: string | null;
  positioningSummary: string | null;
  audience: string | null;
  audienceContext: readonly string[];
  proofPoints: readonly string[];
  evidenceLimitations: readonly string[];
  risks: readonly string[];
  nextSteps: readonly string[];
  marketing: Readonly<{
    coreMessage: string | null;
    primaryMessage: string | null;
    secondaryBenefits: readonly string[];
    supportingFeatures: readonly string[];
  }>;
  xiaohongshu: Readonly<{
    titleDirection: string | null;
    messagePriority: readonly string[];
    contentAngle: string | null;
    proofPoints: readonly string[];
  }>;
}>;

const record = (value: unknown): JsonRecord | null =>
  typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as JsonRecord)
    : null;

const stringValue = (value: unknown): string | null =>
  typeof value === "string" && value.trim() !== "" ? value.trim() : null;

const firstString = (value: JsonRecord | null, keys: readonly string[]) => {
  if (value === null) return null;
  for (const key of keys) {
    const candidate = stringValue(value[key]);
    if (candidate !== null) return candidate;
  }
  return null;
};

const stringList = (value: unknown): string[] => {
  const direct = stringValue(value);
  if (direct !== null) return [direct];
  if (!Array.isArray(value)) return [];
  return value.flatMap((item) => {
    const itemText = stringValue(item);
    if (itemText !== null) return [itemText];
    const itemRecord = record(item);
    if (itemRecord === null) return [];
    return [
      firstString(itemRecord, [
        "statement",
        "proof_point",
        "title_direction",
        "angle_title",
        "content_direction",
        "response",
      ]),
    ].filter((item): item is string => item !== null);
  });
};

const dedupe = (values: readonly string[]): readonly string[] =>
  Object.freeze([...new Set(values.filter((value) => value.trim() !== ""))]);

const firstRecord = (value: unknown): JsonRecord | null => {
  if (!Array.isArray(value)) return null;
  for (const item of value) {
    const candidate = record(item);
    if (candidate !== null) return candidate;
  }
  return null;
};

const candidateRecord = (value: unknown, key: string): JsonRecord | null =>
  record(record(value)?.[key]);

const marketingCandidate = (result: TaskCurrentResult): JsonRecord | null =>
  candidateRecord(result.marketingBrief, "brief_candidate");

const xiaohongshuCandidate = (result: TaskCurrentResult): JsonRecord | null =>
  candidateRecord(result.xiaohongshuBrief, "xiaohongshu_brief_candidate");

const positioningCandidate = (result: TaskCurrentResult): JsonRecord | null =>
  firstRecord(record(result.productPositioning)?.positioning_candidates);

const projectionFor = (result: TaskCurrentResult): ResultProjection => {
  const positioning = positioningCandidate(result);
  const marketing = marketingCandidate(result);
  const xiaohongshu = xiaohongshuCandidate(result);
  const marketingAudience = record(marketing?.objective_and_audience);
  const marketingMessage = record(marketing?.message_architecture);
  const marketingHierarchy = record(marketingMessage?.message_hierarchy);
  const marketingBenefitHierarchy = record(marketingMessage?.benefit_hierarchy);
  const marketingEvidence = record(marketing?.reasons_to_believe_and_evidence);
  const marketingConstraints = record(marketing?.constraints_and_honesty);
  const xhsStructure = record(xiaohongshu?.creative_structure_directions);
  const xhsEvidence = record(xiaohongshu?.evidence_and_platform_constraints);
  const xhsAngle = firstRecord(xhsStructure?.content_angle_mappings);
  const xhsTitle = firstRecord(xhsStructure?.title_directions);
  const xhsCta = record(
    record(xiaohongshu?.discovery_and_action_directions)?.cta_mapping,
  );

  const audience =
    firstString(marketingAudience, ["audience", "audience_segment"]) ??
    firstString(positioning, ["target_segment"]);
  const audienceContext = dedupe([
    ...stringList(marketingAudience?.audience_context),
    ...stringList(marketingAudience?.context),
    ...stringList(marketingAudience?.usage_context),
  ]);
  const proofPoints = dedupe([
    ...stringList(positioning?.proof_points),
    ...stringList(marketingEvidence?.proof_points),
    ...stringList(marketingHierarchy?.supporting_proof_points),
    ...stringList(xhsEvidence?.proof_points),
    ...stringList(xhsAngle?.proof_points),
  ]);
  const evidenceLimitations = dedupe([
    ...stringList(positioning?.evidence_limitations),
    ...stringList(marketingConstraints?.evidence_limitations),
    ...stringList(xhsEvidence?.evidence_limitations),
    ...stringList(xhsAngle?.limitations),
  ]);
  const risks = dedupe([
    ...stringList(positioning?.strategic_risks),
    ...stringList(marketingConstraints?.risk_notes),
    ...stringList(marketingConstraints?.prohibited_claims),
    ...stringList(xhsEvidence?.platform_risk_notes),
    ...stringList(xhsAngle?.risk_notes),
    ...stringList(xhsCta?.risk_notes),
  ]);
  const nextSteps = dedupe(
    stringList(marketingConstraints?.hypotheses_to_test),
  );

  const positioningSummary =
    firstString(positioning, ["value_proposition", "job_or_core_need"]) ??
    firstString(positioning, ["candidate_title"]);
  return Object.freeze({
    positioningTitle: firstString(positioning, ["candidate_title"]),
    positioningSummary,
    audience,
    audienceContext,
    proofPoints,
    evidenceLimitations,
    risks,
    nextSteps,
    marketing: Object.freeze({
      coreMessage: firstString(marketingMessage, ["core_message"]),
      primaryMessage: firstString(marketingHierarchy, ["primary_message"]),
      secondaryBenefits: dedupe([
        ...stringList(marketingHierarchy?.secondary_benefits),
        ...stringList(marketingBenefitHierarchy?.secondary_benefits),
      ]),
      supportingFeatures: dedupe(
        stringList(marketingBenefitHierarchy?.supporting_features),
      ),
    }),
    xiaohongshu: Object.freeze({
      titleDirection: firstString(xhsTitle, ["title_direction"]),
      messagePriority: dedupe(stringList(xhsStructure?.message_priority)),
      contentAngle: firstString(xhsAngle, [
        "xiaohongshu_angle",
        "content_direction",
      ]),
      proofPoints: dedupe([
        ...stringList(xhsEvidence?.proof_points),
        ...stringList(xhsAngle?.proof_points),
      ]),
    }),
  });
};

export const projectResult = (result: TaskCurrentResult): ResultProjection =>
  projectionFor(result);

const line = (label: string, value: string | null): string[] =>
  value === null ? [] : [`${label}：${value}`];

export const renderMarkdownProjection = (
  result: TaskCurrentResult,
  briefKind: ResultBriefKind,
): string => {
  const projection = projectResult(result);
  const title = briefKind === "marketing" ? "营销 Brief" : "小红书 Brief";
  const body =
    briefKind === "marketing"
      ? [
          ...line("核心信息", projection.marketing.coreMessage),
          ...line("目标用户", projection.audience),
          ...line("定位摘要", projection.positioningSummary),
          ...(projection.proofPoints.length > 0
            ? ["证据", ...projection.proofPoints.map((item) => `- ${item}`)]
            : []),
          ...(projection.risks.length > 0
            ? ["风险与限制", ...projection.risks.map((item) => `- ${item}`)]
            : []),
          ...(projection.nextSteps.length > 0
            ? ["下一步", ...projection.nextSteps.map((item) => `- ${item}`)]
            : []),
        ]
      : [
          ...line("标题方向", projection.xiaohongshu.titleDirection),
          ...line("内容角度", projection.xiaohongshu.contentAngle),
          ...line("目标用户", projection.audience),
          ...(projection.xiaohongshu.proofPoints.length > 0
            ? [
                "证据",
                ...projection.xiaohongshu.proofPoints.map(
                  (item) => `- ${item}`,
                ),
              ]
            : []),
          ...(projection.risks.length > 0
            ? ["风险与限制", ...projection.risks.map((item) => `- ${item}`)]
            : []),
          ...(projection.nextSteps.length > 0
            ? ["下一步", ...projection.nextSteps.map((item) => `- ${item}`)]
            : []),
        ];
  return [`# ${title}`, "", ...body].join("\n").trimEnd() + "\n";
};
