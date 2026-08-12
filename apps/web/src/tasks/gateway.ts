import type { components } from "../api/generated/schema";

type SummaryDto = components["schemas"]["TaskSummary"];
type OverviewDto = components["schemas"]["TaskOverview"];

export type TaskInput = Readonly<{
  taskName: string;
  productCategory: string;
  promotionGoal: string;
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
export type TaskOverview = TaskSummary &
  Readonly<{ stages: readonly TaskStageSummary[] }>;
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
}

const invalid = (message: string) => new TaskGatewayError("invalid", message);
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
    typeof item.target === "string"
  ) {
    return Object.freeze({ kind: "navigate", target: item.target });
  }
  if (
    (item.type === "command" || item.type === "CommandPrimaryAction") &&
    typeof item.command === "string"
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
export const mapTaskOverview = (dto: OverviewDto): TaskOverview =>
  Object.freeze({
    ...mapTaskSummary(dto),
    stages: Object.freeze(dto.stages.map(mapStage)),
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
  });
