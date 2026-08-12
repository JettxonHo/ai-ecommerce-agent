import type { TaskOverview } from "../gateway";

export const WORKBENCH_PANELS = Object.freeze([
  "intake",
  "progress",
  "review",
  "results",
  "evidence",
] as const);
export const panelCatalog = WORKBENCH_PANELS;
export type WorkbenchPanel = (typeof WORKBENCH_PANELS)[number];

export const WORKBENCH_STAGES = Object.freeze([
  "product_intake_and_fact_extraction",
  "customer_insight_analysis",
  "product_positioning",
  "human_review",
  "marketing_brief_generation",
  "xiaohongshu_brief_mapping",
] as const);
export const stageCatalog = WORKBENCH_STAGES;
export type WorkbenchStage = (typeof WORKBENCH_STAGES)[number];

export type WorkbenchMode =
  "needs_input" | "review" | "running" | "results" | "recovery" | "intake";

export type WorkbenchLocation = Readonly<{
  panel: WorkbenchPanel;
  stage: WorkbenchStage;
  replaceSearch: string | null;
}>;

const isCatalogValue = <T extends string>(
  value: unknown,
  catalog: readonly T[],
): value is T => typeof value === "string" && catalog.includes(value as T);

const isWorkbenchPanel = (value: unknown): value is WorkbenchPanel =>
  isCatalogValue(value, WORKBENCH_PANELS);
const isWorkbenchStage = (value: unknown): value is WorkbenchStage =>
  isCatalogValue(value, WORKBENCH_STAGES);

export const deriveWorkbenchMode = (task: TaskOverview): WorkbenchMode => {
  if (task.needsInputRequest !== null) return "needs_input";
  if (task.reviewPackage !== null) return "review";
  if (task.activeRunId !== null) return "running";
  if (task.marketingBrief !== null || task.xiaohongshuBrief !== null) {
    return "results";
  }
  if (
    task.taskStatus === "failed" ||
    task.taskStatus === "paused" ||
    (task.primaryAction.kind === "navigate" &&
      task.primaryAction.target === "recovery")
  ) {
    return "recovery";
  }
  return "intake";
};

const defaultPanel = (mode: WorkbenchMode): WorkbenchPanel => {
  if (mode === "running" || mode === "recovery") return "progress";
  if (mode === "review") return "review";
  if (mode === "results") return "results";
  return "intake";
};

const defaultStage = (task: TaskOverview): WorkbenchStage => {
  if (isWorkbenchStage(task.currentStage)) return task.currentStage;
  const firstSummaryStage = task.stages.find((stage) =>
    isWorkbenchStage(stage.stage),
  );
  if (firstSummaryStage && isWorkbenchStage(firstSummaryStage.stage)) {
    return firstSummaryStage.stage;
  }
  return WORKBENCH_STAGES[0];
};

const selectedStageIsApplicable = (
  task: TaskOverview,
  stage: WorkbenchStage,
): boolean =>
  task.stages.length === 0 ||
  task.stages.some((summary) => summary.stage === stage);

const canonicalSearch = (
  searchParams: URLSearchParams,
  panel: WorkbenchPanel,
  stage: WorkbenchStage,
): string => {
  const canonicalParams = new URLSearchParams();
  for (const [key, value] of searchParams.entries()) {
    if (key !== "panel" && key !== "stage") canonicalParams.append(key, value);
  }
  canonicalParams.set("panel", panel);
  canonicalParams.set("stage", stage);
  return `?${canonicalParams.toString()}`;
};

export const deriveWorkbenchLocation = (
  task: TaskOverview,
  search: string,
): WorkbenchLocation => {
  const mode = deriveWorkbenchMode(task);
  const safePanel = defaultPanel(mode);
  const safeStage = defaultStage(task);
  const searchParams = new URLSearchParams(search);
  const panelValues = searchParams.getAll("panel");
  const stageValues = searchParams.getAll("stage");
  const hasPanel = panelValues.length > 0;
  const hasStage = stageValues.length > 0;
  const suppliedPanel = panelValues[0];
  const suppliedStage = stageValues[0];
  const panelValid =
    panelValues.length === 1 && isWorkbenchPanel(suppliedPanel);
  const stageValid =
    stageValues.length === 1 &&
    isWorkbenchStage(suppliedStage) &&
    selectedStageIsApplicable(task, suppliedStage);
  const panel = panelValid ? suppliedPanel : safePanel;
  const stage = stageValid ? suppliedStage : safeStage;
  const invalidSelection =
    (hasPanel && !panelValid) || (hasStage && !stageValid);

  return Object.freeze({
    panel,
    stage,
    replaceSearch: invalidSelection
      ? canonicalSearch(searchParams, panel, stage)
      : null,
  });
};
