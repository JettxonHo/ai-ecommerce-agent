import {
  cloneTaskOverview,
  normalizeIdempotencyKey,
  normalizePrimaryInput,
  normalizeTaskInput,
  normalizeTaskIdentity,
  TaskGatewayError,
  type TaskGateway,
  type TaskInput,
  type TaskPrimaryInput,
  type TaskPrimaryInputDraft,
  type TaskOverview,
} from "./gateway";

export type DeterministicTaskGatewayOptions = Readonly<{
  tasks?: readonly TaskOverview[];
}>;

const createdAt = "2026-08-12T00:00:00Z";

const sameInput = (left: TaskInput, right: TaskInput): boolean =>
  left.taskName === right.taskName &&
  left.productCategory === right.productCategory &&
  left.promotionGoal === right.promotionGoal;

const clonePrimaryInput = (value: TaskPrimaryInput): TaskPrimaryInput =>
  Object.freeze({ ...value });

export const createDeterministicTaskGateway = (
  options: DeterministicTaskGatewayOptions = {},
): TaskGateway => {
  const tasks = (options.tasks ?? []).map(cloneTaskOverview);
  const byId = new Map(tasks.map((task) => [task.taskId, task]));
  const byKey = new Map<string, { input: TaskInput; task: TaskOverview }>();
  const primaryInputs = new Map<string, TaskPrimaryInput>();
  let nextId = 1;

  const allocateId = (): string => {
    while (byId.has(`task-${nextId}`)) nextId += 1;
    const id = `task-${nextId}`;
    nextId += 1;
    return id;
  };

  return {
    listTasks: async () => Object.freeze(tasks.map(cloneTaskOverview)),
    createTask: async (value, valueKey) => {
      const input = normalizeTaskInput(value);
      const key = normalizeIdempotencyKey(valueKey);
      const replay = byKey.get(key);
      if (replay) {
        if (!sameInput(replay.input, input)) {
          throw new TaskGatewayError(
            "invalid",
            "The retry key belongs to another input.",
          );
        }
        return cloneTaskOverview(replay.task);
      }

      const task: TaskOverview = Object.freeze({
        taskId: allocateId(),
        taskName: input.taskName,
        productCategory: input.productCategory,
        taskStatus: "draft",
        currentStage: null,
        waitingReason: null,
        updatedAt: createdAt,
        revision: 0,
        primaryAction: Object.freeze({ kind: "none" as const }),
        capabilities: Object.freeze([]),
        stages: Object.freeze([]),
        activeRunId: null,
        latestRunId: null,
        needsInputRequest: null,
        reviewPackage: null,
        approvedStrategy: null,
        marketingBrief: null,
        xiaohongshuBrief: null,
      });
      tasks.unshift(task);
      byId.set(task.taskId, task);
      byKey.set(key, { input, task });
      return cloneTaskOverview(task);
    },
    getTaskOverview: async (value) => {
      const task = byId.get(normalizeTaskIdentity(value));
      if (!task) throw new TaskGatewayError("missing", "Task not found.");
      return cloneTaskOverview(task);
    },
    getPrimaryInput: async (value) => {
      const taskId = normalizeTaskIdentity(value);
      if (!byId.has(taskId)) {
        throw new TaskGatewayError("missing", "Task not found.");
      }
      const saved = primaryInputs.get(taskId);
      if (!saved) {
        throw new TaskGatewayError("missing", "Primary input not found.");
      }
      return clonePrimaryInput(saved);
    },
    savePrimaryInput: async (value, input: TaskPrimaryInputDraft) => {
      const taskId = normalizeTaskIdentity(value);
      if (!byId.has(taskId)) {
        throw new TaskGatewayError("missing", "Task not found.");
      }
      const draft = normalizePrimaryInput(input);
      const existing = primaryInputs.get(taskId);
      if (
        existing &&
        existing.inputKind === draft.inputKind &&
        existing.fileName === draft.fileName &&
        existing.content === draft.content
      ) {
        return clonePrimaryInput(existing);
      }
      const saved: TaskPrimaryInput = Object.freeze({
        taskId,
        inputRevision: existing ? existing.inputRevision + 1 : 0,
        ...draft,
        byteCount: new TextEncoder().encode(draft.content).byteLength,
        updatedAt: createdAt,
      });
      primaryInputs.set(taskId, saved);
      return clonePrimaryInput(saved);
    },
  };
};
