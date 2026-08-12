import type { components } from "../api/generated/schema";

type SummaryDto = components["schemas"]["TaskSummary"];
type OverviewDto = components["schemas"]["TaskOverview"];
type PrimaryInputDto = components["schemas"]["TaskPrimaryInput"];

export type TaskInput = Readonly<{
  taskName: string;
  productCategory: string;
  promotionGoal: string;
}>;
export type TaskPrimaryInputKind =
  "pasted_text" | "text_file" | "markdown_file";
export type TaskPrimaryInputDraft = Readonly<{
  inputKind: TaskPrimaryInputKind;
  fileName: string | null;
  content: string;
}>;
export type TaskPrimaryInput = TaskPrimaryInputDraft &
  Readonly<{
    taskId: string;
    inputRevision: number;
    byteCount: number;
    updatedAt: string;
  }>;
export type TaskPrimaryAction = Readonly<
  | { kind: "none" }
  | { kind: "navigate"; target: string }
  | { kind: "command"; command: string }
  | { kind: "unavailable" }
>;
export type TaskSummary = Readonly<{
  taskId: string;
  taskName: string;
  productCategory: string;
  taskStatus: string;
  currentStage: string | null;
  waitingReason: string | null;
  updatedAt: string;
  revision: number;
  primaryAction: TaskPrimaryAction;
  capabilities: readonly string[];
}>;
export type TaskStageSummary = Readonly<{
  stage: string;
  status: string;
  waitingReason: string | null;
  updatedAt: string;
}>;
export type NeedsInputRequestReference = Readonly<{
  resourceId: string;
  revision: number;
}>;
export type ReviewPackageReference = Readonly<{
  reviewPackageId: string;
  packageVersion: number;
}>;
export type DomainVersionReference = Readonly<{
  resourceKind: string;
  resourceVersionId: string;
  versionNumber: number;
}>;
export type TaskOverview = TaskSummary &
  Readonly<{
    stages: readonly TaskStageSummary[];
    activeRunId: string | null;
    latestRunId: string | null;
    needsInputRequest: NeedsInputRequestReference | null;
    reviewPackage: ReviewPackageReference | null;
    approvedStrategy: DomainVersionReference | null;
    marketingBrief: DomainVersionReference | null;
    xiaohongshuBrief: DomainVersionReference | null;
  }>;
export type TaskGatewayErrorKind = "temporary" | "missing" | "invalid";

export class TaskGatewayError extends Error {
  constructor(
    readonly kind: TaskGatewayErrorKind,
    message: string,
  ) {
    super(message);
    this.name = "TaskGatewayError";
  }
}
export interface TaskGateway {
  listTasks(): Promise<readonly TaskSummary[]>;
  createTask(input: TaskInput, idempotencyKey: string): Promise<TaskOverview>;
  getTaskOverview(taskId: string): Promise<TaskOverview>;
  /** Primary-input methods are optional for deterministic shell fixtures. */
  getPrimaryInput?(taskId: string): Promise<TaskPrimaryInput>;
  savePrimaryInput?(
    taskId: string,
    input: TaskPrimaryInputDraft,
  ): Promise<TaskPrimaryInput>;
}

const invalid = (message: string) => new TaskGatewayError("invalid", message);
const navigationTargets = "intake needs_input review results recovery".split(
  " ",
);
const commandCapabilities =
  "start cancel resume rerun retry_current_stage restart_from_safe_boundary resolve_needs_input preview_remove_source remove_source preview_replace_source replace_source save_review_draft submit_review request_more_information reject_all_and_request_regeneration withdraw_approved_strategy compare_brief revise_marketing_brief revise_xiaohongshu_brief preview_export confirm_export".split(
    " ",
  );
const objectInput = (value: unknown): Record<string, unknown> => {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw invalid("Task input is invalid.");
  }
  return value as Record<string, unknown>;
};
const nonblank = (value: unknown, message: string): string => {
  if (typeof value !== "string" || value.trim() === "") throw invalid(message);
  return value;
};
const known = (value: unknown, catalog: readonly string[]): value is string =>
  typeof value === "string" && catalog.includes(value);

export const normalizeTaskInput = (value: unknown): TaskInput => {
  const input = objectInput(value);
  const taskName = nonblank(input.taskName, "Task name is required.").trim();
  const productCategory = nonblank(
    input.productCategory,
    "Product category is required.",
  ).trim();
  const promotionGoal = nonblank(
    input.promotionGoal,
    "Promotion goal is required.",
  ).trim();
  return Object.freeze({ taskName, productCategory, promotionGoal });
};
export const normalizeIdempotencyKey = (value: unknown): string =>
  nonblank(value, "A retry key is required.");
export const normalizeTaskIdentity = (value: unknown): string =>
  nonblank(value, "A task identity is required.");

const primaryKinds: readonly TaskPrimaryInputKind[] = [
  "pasted_text",
  "text_file",
  "markdown_file",
];
const encoder = (): TextEncoder => new TextEncoder();
const primaryInputError = (message: string): TaskGatewayError =>
  invalid(message);

export const normalizePrimaryInput = (
  value: unknown,
): TaskPrimaryInputDraft => {
  const input = objectInput(value);
  const inputKind = input.inputKind;
  if (
    typeof inputKind !== "string" ||
    !primaryKinds.includes(inputKind as TaskPrimaryInputKind)
  ) {
    throw primaryInputError("Choose pasted text, a .txt file, or a .md file.");
  }
  const contentValue = input.content;
  if (typeof contentValue !== "string") {
    throw primaryInputError("Primary input content is required.");
  }
  const content = contentValue.replace(/\r\n?/g, "\n");
  if (content.trim() === "") {
    throw primaryInputError("Primary input content is required.");
  }
  const byteCount = encoder().encode(content).byteLength;
  if (byteCount > 1024 * 1024) {
    throw primaryInputError("Primary input is too large (1 MiB maximum).");
  }
  const fileNameValue = input.fileName;
  const fileName =
    fileNameValue === null || fileNameValue === undefined
      ? null
      : nonblank(fileNameValue, "A file name is required.").trim();
  if (inputKind === "pasted_text" && fileName !== null) {
    throw primaryInputError("Pasted text does not have a file name.");
  }
  if (inputKind !== "pasted_text") {
    if (fileName === null || /[\\/]/u.test(fileName)) {
      throw primaryInputError("Choose one .txt or .md file.");
    }
    const suffix = fileName.slice(fileName.lastIndexOf(".")).toLowerCase();
    const expected = inputKind === "text_file" ? ".txt" : ".md";
    if (suffix !== expected) {
      throw primaryInputError(`Choose a ${expected} file.`);
    }
  }
  return Object.freeze({
    inputKind: inputKind as TaskPrimaryInputKind,
    fileName,
    content,
  });
};

const action = (value: unknown): TaskPrimaryAction => {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return Object.freeze({ kind: "unavailable" });
  }
  const item = value as Record<string, unknown>;
  if (item.type === "none" || item.type === "NoPrimaryAction") {
    return Object.freeze({ kind: "none" });
  }
  if (
    (item.type === "navigate" || item.type === "NavigatePrimaryAction") &&
    known(item.target, navigationTargets)
  ) {
    return Object.freeze({ kind: "navigate", target: item.target });
  }
  if (
    (item.type === "command" || item.type === "CommandPrimaryAction") &&
    known(item.command, commandCapabilities)
  ) {
    return Object.freeze({ kind: "command", command: item.command });
  }
  return Object.freeze({ kind: "unavailable" });
};

export const mapTaskSummary = (dto: SummaryDto): TaskSummary =>
  Object.freeze({
    taskId: dto.taskId,
    taskName: dto.taskName,
    productCategory: dto.productCategory,
    taskStatus: dto.taskStatus,
    currentStage: dto.currentStage,
    waitingReason: dto.waitingReason,
    updatedAt: dto.updatedAt,
    revision: dto.revision,
    primaryAction: action(dto.primaryAction),
    capabilities: Object.freeze([...dto.capabilities]),
  });
const mapStage = (stage: OverviewDto["stages"][number]): TaskStageSummary =>
  Object.freeze({
    stage: stage.stage,
    status: stage.status,
    waitingReason: stage.waitingReason,
    updatedAt: stage.updatedAt,
  });
const mapNeedsInputRequest = (
  reference: OverviewDto["needsInputRequest"],
): NeedsInputRequestReference | null =>
  reference == null
    ? null
    : Object.freeze({
        resourceId: reference.resourceId,
        revision: reference.revision,
      });
const mapReviewPackage = (
  reference: OverviewDto["reviewPackage"],
): ReviewPackageReference | null =>
  reference == null
    ? null
    : Object.freeze({
        reviewPackageId: reference.reviewPackageId,
        packageVersion: reference.packageVersion,
      });
const mapDomainVersion = (
  reference: OverviewDto["approvedStrategy"],
): DomainVersionReference | null =>
  reference == null
    ? null
    : Object.freeze({
        resourceKind: reference.resourceKind,
        resourceVersionId: reference.resourceVersionId,
        versionNumber: reference.versionNumber,
      });
export const mapTaskOverview = (dto: OverviewDto): TaskOverview =>
  Object.freeze({
    ...mapTaskSummary(dto),
    stages: Object.freeze(dto.stages.map(mapStage)),
    activeRunId: dto.activeRun?.runId ?? null,
    latestRunId: dto.latestRun?.runId ?? null,
    needsInputRequest: mapNeedsInputRequest(dto.needsInputRequest),
    reviewPackage: mapReviewPackage(dto.reviewPackage),
    approvedStrategy: mapDomainVersion(dto.approvedStrategy),
    marketingBrief: mapDomainVersion(dto.marketingBrief),
    xiaohongshuBrief: mapDomainVersion(dto.xiaohongshuBrief),
  });

export const mapTaskPrimaryInput = (dto: PrimaryInputDto): TaskPrimaryInput =>
  Object.freeze({
    taskId: dto.taskId,
    inputRevision: dto.inputRevision,
    inputKind: dto.inputKind,
    fileName: dto.fileName,
    content: dto.content,
    byteCount: dto.byteCount,
    updatedAt: dto.updatedAt,
  });

const cloneAction = (value: TaskPrimaryAction): TaskPrimaryAction => {
  if (typeof value !== "object" || value === null) {
    return Object.freeze({ kind: "unavailable" });
  }
  if (value.kind === "navigate" && typeof value.target === "string") {
    return Object.freeze({ kind: "navigate", target: value.target });
  }
  if (value.kind === "command" && typeof value.command === "string") {
    return Object.freeze({ kind: "command", command: value.command });
  }
  return value.kind === "none"
    ? Object.freeze({ kind: "none" })
    : Object.freeze({ kind: "unavailable" });
};
const cloneNeedsInputRequest = (
  reference: NeedsInputRequestReference | null,
): NeedsInputRequestReference | null =>
  reference == null ? null : Object.freeze({ ...reference });
const cloneReviewPackage = (
  reference: ReviewPackageReference | null,
): ReviewPackageReference | null =>
  reference == null ? null : Object.freeze({ ...reference });
const cloneDomainVersion = (
  reference: DomainVersionReference | null,
): DomainVersionReference | null =>
  reference == null ? null : Object.freeze({ ...reference });
export const cloneTaskOverview = (task: TaskOverview): TaskOverview =>
  Object.freeze({
    taskId: task.taskId,
    taskName: task.taskName,
    productCategory: task.productCategory,
    taskStatus: task.taskStatus,
    currentStage: task.currentStage,
    waitingReason: task.waitingReason,
    updatedAt: task.updatedAt,
    revision: task.revision,
    primaryAction: cloneAction(task.primaryAction),
    capabilities: Object.freeze([...task.capabilities]),
    stages: Object.freeze(
      task.stages.map((stage) => Object.freeze({ ...stage })),
    ),
    activeRunId: task.activeRunId ?? null,
    latestRunId: task.latestRunId ?? null,
    needsInputRequest: cloneNeedsInputRequest(task.needsInputRequest),
    reviewPackage: cloneReviewPackage(task.reviewPackage),
    approvedStrategy: cloneDomainVersion(task.approvedStrategy),
    marketingBrief: cloneDomainVersion(task.marketingBrief),
    xiaohongshuBrief: cloneDomainVersion(task.xiaohongshuBrief),
  });
