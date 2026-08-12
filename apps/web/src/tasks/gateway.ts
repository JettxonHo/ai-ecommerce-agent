import type { components } from "../api/generated/schema";

type SummaryDto = components["schemas"]["TaskSummary"];
type OverviewDto = components["schemas"]["TaskOverview"];
type PrimaryInputDto = components["schemas"]["TaskPrimaryInput"];
type CurrentResultDto = components["schemas"]["CurrentTaskResult"];

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
export type TaskResultStatus =
  "awaiting_review" | "insufficient_input" | "confirmed";
export type TaskResultConfirmation = Readonly<{
  marketingBriefVersion: DomainVersionReference;
  xiaohongshuBriefVersion: DomainVersionReference;
  confirmedAt: string;
}>;
export type TaskCurrentResult = Readonly<{
  taskId: string;
  resultRevision: number;
  inputRevision: number;
  status: TaskResultStatus;
  generatedAt: string;
  missingInformation: readonly string[];
  productIntake: Record<string, unknown> | null;
  customerInsight: Record<string, unknown> | null;
  productPositioning: Record<string, unknown> | null;
  marketingBrief: Record<string, unknown> | null;
  xiaohongshuBrief: Record<string, unknown> | null;
  confirmation: TaskResultConfirmation | null;
}>;
export type ExportBriefKind = "marketing" | "xiaohongshu";
export type ExportBasis = Readonly<{
  taskId: string;
  taskRevision: number;
  briefKind: ExportBriefKind;
  briefVersion: DomainVersionReference;
  upstreamVersions: readonly DomainVersionReference[];
  hypotheses: readonly string[];
  evidenceLimitations: readonly string[];
  risks: readonly string[];
}>;
export type ExportPreview = Readonly<{
  basis: ExportBasis;
  templateVersion: string;
  fileName: string;
  mediaType: string;
}>;
export type ExportSnapshot = Readonly<{
  exportSnapshotId: string;
  taskId: string;
  briefKind: ExportBriefKind;
  briefVersion: DomainVersionReference;
  upstreamVersions: readonly DomainVersionReference[];
  exportedAt: string;
  fileName: string;
  mediaType: string;
  contentLocation: string;
  templateVersion: string;
}>;
export type ExportDownload = Readonly<{
  snapshot: ExportSnapshot;
  content: string;
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
  getPrimaryInput(taskId: string): Promise<TaskPrimaryInput>;
  savePrimaryInput(
    taskId: string,
    input: TaskPrimaryInputDraft,
  ): Promise<TaskPrimaryInput>;
  generateResult(
    taskId: string,
    idempotencyKey: string,
    expectedInputRevision: number,
  ): Promise<TaskCurrentResult>;
  getCurrentResult(taskId: string): Promise<TaskCurrentResult | null>;
  confirmCurrentResult?: (
    taskId: string,
    idempotencyKey: string,
    expectedResultRevision: number,
    input: Readonly<{
      marketingCoreMessage: string;
      xiaohongshuTitleDirection: string;
    }>,
  ) => Promise<TaskCurrentResult>;
  previewExport?: (
    taskId: string,
    briefKind: ExportBriefKind,
  ) => Promise<ExportPreview>;
  createExportSnapshot?: (
    idempotencyKey: string,
    basis: ExportBasis,
  ) => Promise<ExportSnapshot>;
  downloadExportContent?: (
    snapshot: ExportSnapshot,
  ) => Promise<Readonly<{ snapshot: ExportSnapshot; content: string }>>;
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
const rfc3339DateTime =
  /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):(\d{2}))$/u;

const validPrimaryInputTimestamp = (value: unknown): value is string => {
  if (typeof value !== "string") return false;
  const match = rfc3339DateTime.exec(value);
  if (match === null) return false;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const hour = Number(match[4]);
  const minute = Number(match[5]);
  const second = Number(match[6]);
  const offsetHour = match[7] === undefined ? 0 : Number(match[7]);
  const offsetMinute = match[8] === undefined ? 0 : Number(match[8]);
  const leapYear = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const daysInMonth = [
    31,
    leapYear ? 29 : 28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
  ];
  return (
    month >= 1 &&
    month <= 12 &&
    day >= 1 &&
    day <= (daysInMonth[month - 1] ?? 0) &&
    hour <= 23 &&
    minute <= 59 &&
    second <= 59 &&
    offsetHour <= 23 &&
    offsetMinute <= 59 &&
    Number.isFinite(Date.parse(value))
  );
};

const validPrimaryInputFileName = (
  value: unknown,
  expectedExtension: ".txt" | ".md",
): value is string =>
  typeof value === "string" &&
  value.trim() !== "" &&
  value !== "." &&
  value !== ".." &&
  !/[\\/]/u.test(value) &&
  value.toLowerCase().endsWith(expectedExtension);

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
  (() => {
    const input = objectInput(dto);
    const taskId = input.taskId;
    const inputRevision = input.inputRevision;
    const inputKind = input.inputKind;
    const fileNameValue = input.fileName;
    const content = input.content;
    const byteCount = input.byteCount;
    const updatedAt = input.updatedAt;
    const responseError = () =>
      primaryInputError("The primary input response is invalid.");

    if (typeof taskId !== "string" || taskId.trim() === "") {
      throw responseError();
    }
    if (!Number.isInteger(inputRevision) || (inputRevision as number) < 0) {
      throw responseError();
    }
    if (
      typeof inputKind !== "string" ||
      !primaryKinds.includes(inputKind as TaskPrimaryInputKind)
    ) {
      throw responseError();
    }
    if (typeof content !== "string" || content.trim() === "") {
      throw responseError();
    }
    if (
      !Number.isInteger(byteCount) ||
      (byteCount as number) < 0 ||
      (byteCount as number) > 1024 * 1024 ||
      encoder().encode(content).byteLength !== byteCount
    ) {
      throw responseError();
    }
    if (!validPrimaryInputTimestamp(updatedAt)) {
      throw responseError();
    }

    let fileName: string | null;
    if (inputKind === "pasted_text") {
      if (fileNameValue !== null) throw responseError();
      fileName = null;
    } else {
      const expectedExtension = inputKind === "text_file" ? ".txt" : ".md";
      if (!validPrimaryInputFileName(fileNameValue, expectedExtension)) {
        throw responseError();
      }
      fileName = fileNameValue;
    }

    return Object.freeze({
      taskId,
      inputRevision: inputRevision as number,
      inputKind: inputKind as TaskPrimaryInputKind,
      fileName,
      content,
      byteCount,
      updatedAt,
    });
  })();

export const mapTaskCurrentResult = (
  dto: CurrentResultDto,
): TaskCurrentResult => {
  const input = objectInput(dto);
  const invalidResult = () =>
    new TaskGatewayError("invalid", "The current result response is invalid.");
  const taskId = input.taskId;
  const resultRevision = input.resultRevision;
  const inputRevision = input.inputRevision;
  const status = input.status;
  const generatedAt = input.generatedAt;
  const missingInformation = input.missingInformation;
  if (
    typeof taskId !== "string" ||
    taskId.trim() === "" ||
    !Number.isInteger(resultRevision) ||
    (resultRevision as number) < 0 ||
    !Number.isInteger(inputRevision) ||
    (inputRevision as number) < 0 ||
    (status !== "awaiting_review" &&
      status !== "insufficient_input" &&
      status !== "confirmed") ||
    !validPrimaryInputTimestamp(generatedAt) ||
    !Array.isArray(missingInformation) ||
    missingInformation.some(
      (value) => typeof value !== "string" || value.trim() === "",
    )
  ) {
    throw invalidResult();
  }
  const candidate = (value: unknown): Record<string, unknown> | null => {
    if (value === null) return null;
    if (typeof value !== "object" || Array.isArray(value))
      throw invalidResult();
    return value as Record<string, unknown>;
  };
  const versionReference = (value: unknown): DomainVersionReference => {
    const reference = objectInput(value);
    if (
      typeof reference.resourceKind !== "string" ||
      reference.resourceKind.trim() === "" ||
      typeof reference.resourceVersionId !== "string" ||
      reference.resourceVersionId.trim() === "" ||
      !Number.isInteger(reference.versionNumber) ||
      (reference.versionNumber as number) < 1
    ) {
      throw invalidResult();
    }
    return Object.freeze({
      resourceKind: reference.resourceKind,
      resourceVersionId: reference.resourceVersionId,
      versionNumber: reference.versionNumber as number,
    });
  };
  const confirmation = (value: unknown): TaskResultConfirmation | null => {
    if (value === null) return null;
    const item = objectInput(value);
    if (!validPrimaryInputTimestamp(item.confirmedAt)) throw invalidResult();
    return Object.freeze({
      marketingBriefVersion: versionReference(item.marketingBriefVersion),
      xiaohongshuBriefVersion: versionReference(item.xiaohongshuBriefVersion),
      confirmedAt: item.confirmedAt,
    });
  };
  const result: TaskCurrentResult = {
    taskId,
    resultRevision: resultRevision as number,
    inputRevision: inputRevision as number,
    status,
    generatedAt,
    missingInformation: Object.freeze(
      (missingInformation as unknown[]).map((value) => String(value)),
    ),
    productIntake: candidate(input.productIntake),
    customerInsight: candidate(input.customerInsight),
    productPositioning: candidate(input.productPositioning),
    marketingBrief: candidate(input.marketingBrief),
    xiaohongshuBrief: candidate(input.xiaohongshuBrief),
    confirmation: confirmation(input.confirmation),
  };
  if (status === "awaiting_review") {
    if (
      result.productIntake === null ||
      result.customerInsight === null ||
      result.productPositioning === null ||
      result.marketingBrief === null ||
      result.xiaohongshuBrief === null ||
      result.missingInformation.length !== 0
    ) {
      throw invalidResult();
    }
    if (result.confirmation !== null) {
      throw invalidResult();
    }
  } else if (status === "confirmed") {
    if (
      result.productIntake === null ||
      result.customerInsight === null ||
      result.productPositioning === null ||
      result.marketingBrief === null ||
      result.xiaohongshuBrief === null ||
      result.missingInformation.length !== 0 ||
      result.confirmation === null
    ) {
      throw invalidResult();
    }
  } else if (
    result.productIntake !== null ||
    result.customerInsight !== null ||
    result.productPositioning !== null ||
    result.marketingBrief !== null ||
    result.xiaohongshuBrief !== null ||
    result.missingInformation.length === 0 ||
    result.confirmation !== null
  ) {
    throw invalidResult();
  }
  return Object.freeze(result);
};

const exportBriefKinds: readonly ExportBriefKind[] = [
  "marketing",
  "xiaohongshu",
];
const exportFileName =
  /^task-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-(marketing|xiaohongshu)-v[0-9]+-[0-9]{8}T[0-9]{6}Z\.md$/u;
const mapExportVersion = (value: unknown): DomainVersionReference => {
  const item = objectInput(value);
  if (
    typeof item.resourceKind !== "string" ||
    item.resourceKind.trim() === "" ||
    typeof item.resourceVersionId !== "string" ||
    item.resourceVersionId.trim() === "" ||
    !Number.isInteger(item.versionNumber) ||
    (item.versionNumber as number) < 1
  ) {
    throw invalid("The export response is invalid.");
  }
  return Object.freeze({
    resourceKind: item.resourceKind,
    resourceVersionId: item.resourceVersionId,
    versionNumber: item.versionNumber as number,
  });
};
const mapExportStringList = (value: unknown): readonly string[] => {
  if (
    !Array.isArray(value) ||
    value.some((item) => typeof item !== "string" || item.trim() === "")
  ) {
    throw invalid("The export response is invalid.");
  }
  return Object.freeze(value.map((item) => item as string));
};
const mapExportBasis = (value: unknown): ExportBasis => {
  const item = objectInput(value);
  const briefKind = item.briefKind;
  if (
    typeof item.taskId !== "string" ||
    item.taskId.trim() === "" ||
    !Number.isInteger(item.taskRevision) ||
    (item.taskRevision as number) < 0 ||
    typeof briefKind !== "string" ||
    !exportBriefKinds.includes(briefKind as ExportBriefKind)
  ) {
    throw invalid("The export response is invalid.");
  }
  const upstream = item.upstreamVersions;
  if (!Array.isArray(upstream))
    throw invalid("The export response is invalid.");
  return Object.freeze({
    taskId: item.taskId,
    taskRevision: item.taskRevision as number,
    briefKind: briefKind as ExportBriefKind,
    briefVersion: mapExportVersion(item.briefVersion),
    upstreamVersions: Object.freeze(upstream.map(mapExportVersion)),
    hypotheses: mapExportStringList(item.hypotheses),
    evidenceLimitations: mapExportStringList(item.evidenceLimitations),
    risks: mapExportStringList(item.risks),
  });
};
export const mapTaskExportPreview = (value: unknown): ExportPreview => {
  const item = objectInput(value);
  if (
    typeof item.templateVersion !== "string" ||
    item.templateVersion !== "mvp0-markdown-v1" ||
    typeof item.fileName !== "string" ||
    !exportFileName.test(item.fileName) ||
    item.mediaType !== "text/markdown; charset=utf-8"
  ) {
    throw invalid("The export response is invalid.");
  }
  return Object.freeze({
    basis: mapExportBasis(item.basis),
    templateVersion: item.templateVersion,
    fileName: item.fileName,
    mediaType: item.mediaType,
  });
};
export const mapTaskExportSnapshot = (value: unknown): ExportSnapshot => {
  const item = objectInput(value);
  if (
    typeof item.exportSnapshotId !== "string" ||
    item.exportSnapshotId.trim() === "" ||
    typeof item.taskId !== "string" ||
    item.taskId.trim() === "" ||
    typeof item.briefKind !== "string" ||
    !exportBriefKinds.includes(item.briefKind as ExportBriefKind) ||
    !validPrimaryInputTimestamp(item.exportedAt) ||
    typeof item.fileName !== "string" ||
    !exportFileName.test(item.fileName) ||
    item.mediaType !== "text/markdown; charset=utf-8" ||
    typeof item.contentLocation !== "string" ||
    item.contentLocation.trim() === "" ||
    item.templateVersion !== "mvp0-markdown-v1"
  ) {
    throw invalid("The export response is invalid.");
  }
  return Object.freeze({
    exportSnapshotId: item.exportSnapshotId,
    taskId: item.taskId,
    briefKind: item.briefKind as ExportBriefKind,
    briefVersion: mapExportVersion(item.briefVersion),
    upstreamVersions: Object.freeze(
      (Array.isArray(item.upstreamVersions) ? item.upstreamVersions : []).map(
        mapExportVersion,
      ),
    ),
    exportedAt: item.exportedAt,
    fileName: item.fileName,
    mediaType: item.mediaType,
    contentLocation: item.contentLocation,
    templateVersion: item.templateVersion,
  });
};

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
