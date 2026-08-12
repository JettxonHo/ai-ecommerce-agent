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
  type TaskCurrentResult,
  type TaskOverview,
  type ExportBriefKind,
  type ExportBasis,
  type ExportPreview,
  type ExportSnapshot,
} from "./gateway";

export type DeterministicTaskGatewayOptions = Readonly<{
  tasks?: readonly TaskOverview[];
  results?: readonly TaskCurrentResult[];
}>;

const createdAt = "2026-08-12T00:00:00Z";

const sameInput = (left: TaskInput, right: TaskInput): boolean =>
  left.taskName === right.taskName &&
  left.productCategory === right.productCategory &&
  left.promotionGoal === right.promotionGoal;

const clonePrimaryInput = (value: TaskPrimaryInput): TaskPrimaryInput =>
  Object.freeze({ ...value });

const cloneJson = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

const replaceCandidateLeaf = (
  candidate: Record<string, unknown> | null,
  path: readonly string[],
  replacement: string,
): Record<string, unknown> => {
  if (candidate === null) {
    throw new TaskGatewayError("invalid", "The review candidate is missing.");
  }
  const copy = cloneJson(candidate);
  let current: unknown = copy;
  for (const segment of path.slice(0, -1)) {
    if (typeof current !== "object" || current === null) {
      throw new TaskGatewayError(
        "invalid",
        "The review candidate is malformed.",
      );
    }
    if (Array.isArray(current)) {
      const index = Number(segment);
      current = Number.isInteger(index) ? current[index] : undefined;
    } else {
      current = (current as Record<string, unknown>)[segment];
    }
  }
  const leaf = path[path.length - 1];
  if (typeof current !== "object" || current === null || leaf === undefined) {
    throw new TaskGatewayError("invalid", "The review candidate is malformed.");
  }
  if (Array.isArray(current)) {
    const index = Number(leaf);
    if (!Number.isInteger(index) || typeof current[index] !== "string") {
      throw new TaskGatewayError(
        "invalid",
        "The review candidate is malformed.",
      );
    }
    current[index] = replacement;
  } else {
    const mapping = current as Record<string, unknown>;
    if (typeof mapping[leaf] !== "string") {
      throw new TaskGatewayError(
        "invalid",
        "The review candidate is malformed.",
      );
    }
    mapping[leaf] = replacement;
  }
  return copy;
};

const sameExportBasis = (left: ExportBasis, right: ExportBasis): boolean =>
  JSON.stringify(left) === JSON.stringify(right);

export const createDeterministicTaskGateway = (
  options: DeterministicTaskGatewayOptions = {},
): TaskGateway => {
  const tasks = (options.tasks ?? []).map(cloneTaskOverview);
  const byId = new Map(tasks.map((task) => [task.taskId, task]));
  const byKey = new Map<string, { input: TaskInput; task: TaskOverview }>();
  const primaryInputs = new Map<string, TaskPrimaryInput>();
  const currentResults = new Map(
    (options.results ?? []).map((result) => [result.taskId, result]),
  );
  const exportSnapshots = new Map<
    string,
    { snapshot: ExportSnapshot; content: string }
  >();
  const confirmationReplays = new Map<
    string,
    {
      resultRevision: number;
      inputRevision: number;
      marketingCoreMessage: string;
      xiaohongshuTitleDirection: string;
      result: TaskCurrentResult;
    }
  >();
  const exportReplays = new Map<
    string,
    { basis: ExportBasis; snapshot: ExportSnapshot; content: string }
  >();
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
    generateResult: async (value, valueKey, expectedInputRevision) => {
      const taskId = normalizeTaskIdentity(value);
      normalizeIdempotencyKey(valueKey);
      const input = primaryInputs.get(taskId);
      if (!input)
        throw new TaskGatewayError("missing", "Primary input not found.");
      if (input.inputRevision !== expectedInputRevision) {
        throw new TaskGatewayError(
          "invalid",
          "The primary input changed; refresh before retrying.",
        );
      }
      const previous = currentResults.get(taskId);
      if (previous && previous.inputRevision === expectedInputRevision) {
        return Object.freeze({ ...previous });
      }
      const sufficient =
        input.content.includes("anchor-city-commuter-backpack") &&
        input.content.includes("CBP-SYN-001") &&
        input.content.includes("18 升");
      const result: TaskCurrentResult = Object.freeze({
        taskId,
        resultRevision: previous ? previous.resultRevision + 1 : 0,
        inputRevision: expectedInputRevision,
        status: sufficient ? "awaiting_review" : "insufficient_input",
        generatedAt: createdAt,
        missingInformation: sufficient
          ? Object.freeze([])
          : Object.freeze(["Provide Anchor SKU product identity evidence."]),
        productIntake: sufficient
          ? Object.freeze({ stage: "Product Intake" })
          : null,
        customerInsight: sufficient
          ? Object.freeze({ stage: "Customer Insight" })
          : null,
        productPositioning: sufficient
          ? Object.freeze({
              stage: "Product Positioning",
              positioning_candidates: [],
            })
          : null,
        marketingBrief: sufficient
          ? Object.freeze({
              brief_candidate: {
                message_architecture: {
                  core_message: "为工作日通勤提供清晰的电脑与日常物品收纳",
                },
              },
            })
          : null,
        xiaohongshuBrief: sufficient
          ? Object.freeze({
              xiaohongshu_brief_candidate: {
                creative_structure_directions: {
                  title_directions: [{ title_direction: "通勤收纳路径" }],
                },
              },
            })
          : null,
        confirmation: null,
      });
      currentResults.set(taskId, result);
      return Object.freeze({ ...result });
    },
    getCurrentResult: async (value) => {
      const taskId = normalizeTaskIdentity(value);
      if (!byId.has(taskId))
        throw new TaskGatewayError("missing", "Task not found.");
      const result = currentResults.get(taskId);
      return result ? Object.freeze({ ...result }) : null;
    },
    confirmCurrentResult: async (value, key, expectedResultRevision, input) => {
      const taskId = normalizeTaskIdentity(value);
      const replayKey = `${taskId}:${normalizeIdempotencyKey(key)}`;
      const currentInput = primaryInputs.get(taskId);
      const replay = confirmationReplays.get(replayKey);
      if (replay) {
        if (
          replay.resultRevision !== expectedResultRevision ||
          replay.marketingCoreMessage !== input.marketingCoreMessage ||
          replay.xiaohongshuTitleDirection !== input.xiaohongshuTitleDirection
        ) {
          throw new TaskGatewayError(
            "invalid",
            "The retry key belongs to another confirmation.",
          );
        }
        const current = currentResults.get(taskId);
        if (
          (currentInput !== undefined &&
            currentInput.inputRevision !== replay.inputRevision) ||
          current?.inputRevision !== replay.inputRevision ||
          current?.resultRevision !== replay.resultRevision
        ) {
          throw new TaskGatewayError(
            "invalid",
            "The current result changed; refresh before confirming.",
          );
        }
        return cloneJson(replay.result);
      }
      const result = currentResults.get(taskId);
      if (!result || result.resultRevision !== expectedResultRevision) {
        throw new TaskGatewayError(
          "invalid",
          "The current result changed; refresh before confirming.",
        );
      }
      if (result.status === "insufficient_input") {
        throw new TaskGatewayError(
          "invalid",
          "Insufficient input cannot be confirmed.",
        );
      }
      if (result.status === "confirmed") {
        throw new TaskGatewayError(
          "invalid",
          "The current result is already confirmed.",
        );
      }
      if (currentInput && currentInput.inputRevision !== result.inputRevision) {
        throw new TaskGatewayError(
          "invalid",
          "The current result changed; refresh before confirming.",
        );
      }
      const marketingBrief = replaceCandidateLeaf(
        result.marketingBrief,
        ["brief_candidate", "message_architecture", "core_message"],
        input.marketingCoreMessage,
      );
      const xiaohongshuBrief = replaceCandidateLeaf(
        result.xiaohongshuBrief,
        [
          "xiaohongshu_brief_candidate",
          "creative_structure_directions",
          "title_directions",
          "0",
          "title_direction",
        ],
        input.xiaohongshuTitleDirection,
      );
      const confirmed: TaskCurrentResult = Object.freeze({
        ...result,
        status: "confirmed",
        marketingBrief,
        xiaohongshuBrief,
        confirmation: Object.freeze({
          marketingBriefVersion: Object.freeze({
            resourceKind: "marketing_brief",
            resourceVersionId: `brief-${taskId}-marketing`,
            versionNumber: 1,
          }),
          xiaohongshuBriefVersion: Object.freeze({
            resourceKind: "xiaohongshu_brief",
            resourceVersionId: `brief-${taskId}-xiaohongshu`,
            versionNumber: 1,
          }),
          confirmedAt: createdAt,
        }),
      });
      currentResults.set(taskId, confirmed);
      confirmationReplays.set(replayKey, {
        resultRevision: expectedResultRevision,
        inputRevision: result.inputRevision,
        marketingCoreMessage: input.marketingCoreMessage,
        xiaohongshuTitleDirection: input.xiaohongshuTitleDirection,
        result: confirmed,
      });
      return Object.freeze({ ...confirmed });
    },
    previewExport: async (
      value,
      briefKind: ExportBriefKind,
    ): Promise<ExportPreview> => {
      const taskId = normalizeTaskIdentity(value);
      const result = currentResults.get(taskId);
      if (
        !result ||
        result.status !== "confirmed" ||
        result.confirmation === null
      ) {
        throw new TaskGatewayError(
          "invalid",
          "Only a confirmed result can be exported.",
        );
      }
      const input = primaryInputs.get(taskId);
      if (input && input.inputRevision !== result.inputRevision) {
        throw new TaskGatewayError(
          "invalid",
          "The current result changed; refresh the export preview.",
        );
      }
      const basis: ExportBasis = Object.freeze({
        taskId,
        taskRevision: 0,
        briefKind,
        briefVersion:
          briefKind === "marketing"
            ? result.confirmation.marketingBriefVersion
            : result.confirmation.xiaohongshuBriefVersion,
        upstreamVersions: [],
        hypotheses: [],
        evidenceLimitations: [],
        risks: [],
      });
      return Object.freeze({
        basis,
        templateVersion: "mvp0-markdown-v1",
        fileName: `task-${taskId}-${briefKind}-v1-20260812T000000Z.md`,
        mediaType: "text/markdown; charset=utf-8",
      });
    },
    createExportSnapshot: async (
      key,
      basis: ExportBasis,
    ): Promise<ExportSnapshot> => {
      const replayKey = `${basis.taskId}:${normalizeIdempotencyKey(key)}`;
      const replay = exportReplays.get(replayKey);
      if (replay) {
        if (!sameExportBasis(replay.basis, basis)) {
          throw new TaskGatewayError(
            "invalid",
            "The retry key belongs to another export basis.",
          );
        }
        const currentInput = primaryInputs.get(basis.taskId);
        const currentResult = currentResults.get(basis.taskId);
        if (
          currentInput &&
          currentResult &&
          currentInput.inputRevision !== currentResult.inputRevision
        ) {
          throw new TaskGatewayError(
            "invalid",
            "The current result changed; refresh the export preview.",
          );
        }
        return replay.snapshot;
      }
      const currentResult = currentResults.get(basis.taskId);
      const currentInput = primaryInputs.get(basis.taskId);
      if (
        !currentResult ||
        currentResult.status !== "confirmed" ||
        (currentInput &&
          currentInput.inputRevision !== currentResult.inputRevision)
      ) {
        throw new TaskGatewayError(
          "invalid",
          "The current result changed; refresh the export preview.",
        );
      }
      const exportSnapshotId = `export-${basis.taskId}-${basis.briefKind}-${
        exportReplays.size + 1
      }`;
      const snapshot: ExportSnapshot = Object.freeze({
        exportSnapshotId,
        taskId: basis.taskId,
        briefKind: basis.briefKind,
        briefVersion: basis.briefVersion,
        upstreamVersions: basis.upstreamVersions,
        exportedAt: createdAt,
        fileName: `task-${basis.taskId}-${basis.briefKind}-v1-20260812T000000Z.md`,
        mediaType: "text/markdown; charset=utf-8",
        contentLocation: `/api/v1/export-snapshots/${exportSnapshotId}/content`,
        templateVersion: "mvp0-markdown-v1",
      });
      const item = {
        snapshot,
        content: `# ${basis.briefKind === "marketing" ? "Marketing" : "Xiaohongshu"} Brief\n\nExported from deterministic preview.\n`,
      };
      exportSnapshots.set(exportSnapshotId, item);
      exportReplays.set(replayKey, { basis, ...item });
      return snapshot;
    },
    downloadExportContent: async (snapshot) => {
      const item = exportSnapshots.get(
        normalizeTaskIdentity(snapshot.exportSnapshotId),
      );
      if (!item)
        throw new TaskGatewayError("missing", "Export snapshot not found.");
      return item;
    },
  };
};
