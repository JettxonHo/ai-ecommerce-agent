import type { ApiClient } from "../api/client";
import {
  mapTaskOverview,
  mapTaskPrimaryInput,
  mapTaskCurrentResult,
  mapTaskExportPreview,
  mapTaskExportSnapshot,
  mapTaskSummary,
  normalizeIdempotencyKey,
  normalizeTaskIdentity,
  normalizeTaskInput,
  normalizePrimaryInput,
  TaskGatewayError,
  type TaskGateway,
  type ExportBriefKind,
  type ExportBasis,
  type ExportSnapshot,
} from "./gateway";

type ClientResult<T> = { data?: T; response?: Response };
const failure = (
  status: number | undefined,
  operation: string,
): TaskGatewayError => {
  if (status === 404) return new TaskGatewayError("missing", "Task not found.");
  if (status === 400 || status === 409 || status === 422) {
    return new TaskGatewayError(
      "invalid",
      "The task request could not be completed.",
    );
  }
  if (status === 413) {
    return new TaskGatewayError(
      "invalid",
      "Primary input is too large (1 MiB maximum).",
    );
  }
  if (status !== undefined && status < 500) {
    return new TaskGatewayError(
      "invalid",
      "The task request could not be completed.",
    );
  }
  return new TaskGatewayError(
    "temporary",
    `${operation} is temporarily unavailable. Try again.`,
  );
};
const request = async <T, R>(
  operation: string,
  call: () => Promise<ClientResult<T>>,
  map: (value: T) => R,
): Promise<R> => {
  let received = false;
  try {
    const result = await call();
    received = true;
    if (result.data === undefined || result.data === null) {
      throw failure(result.response?.status, operation);
    }
    try {
      return map(result.data);
    } catch {
      throw new TaskGatewayError("invalid", "The task response is invalid.");
    }
  } catch (error) {
    if (error instanceof TaskGatewayError) throw error;
    if (error instanceof SyntaxError) {
      throw new TaskGatewayError("invalid", "The task response is invalid.");
    }
    if (received)
      throw new TaskGatewayError("invalid", "The task response is invalid.");
    throw failure(undefined, operation);
  }
};

export const createHttpTaskGateway = (client: ApiClient): TaskGateway => ({
  listTasks: async () =>
    Object.freeze(
      await request(
        "Recent tasks",
        () => client.GET("/api/v1/tasks", { params: { query: { limit: 20 } } }),
        (value) => value.items.map(mapTaskSummary),
      ),
    ),
  createTask: async (input, idempotencyKey) => {
    const body = normalizeTaskInput(input);
    const key = normalizeIdempotencyKey(idempotencyKey);
    return request(
      "Task creation",
      () =>
        client.POST("/api/v1/tasks", {
          params: { header: { "Idempotency-Key": key } },
          body,
        }),
      mapTaskOverview,
    );
  },
  getTaskOverview: async (taskId) => {
    const identity = normalizeTaskIdentity(taskId);
    return request(
      "Task overview",
      () =>
        client.GET("/api/v1/tasks/{taskId}", {
          params: { path: { taskId: identity } },
        }),
      mapTaskOverview,
    );
  },
  getPrimaryInput: async (taskId) => {
    const identity = normalizeTaskIdentity(taskId);
    return request(
      "Primary input",
      () =>
        client.GET("/api/v1/tasks/{taskId}/primary-input", {
          params: { path: { taskId: identity } },
        }),
      mapTaskPrimaryInput,
    );
  },
  savePrimaryInput: async (taskId, input) => {
    const identity = normalizeTaskIdentity(taskId);
    const body = normalizePrimaryInput(input);
    return request(
      "Primary input",
      () =>
        client.PUT("/api/v1/tasks/{taskId}/primary-input", {
          params: { path: { taskId: identity } },
          body,
        }),
      mapTaskPrimaryInput,
    );
  },
  generateResult: async (taskId, idempotencyKey, expectedInputRevision) => {
    const identity = normalizeTaskIdentity(taskId);
    const key = normalizeIdempotencyKey(idempotencyKey);
    if (!Number.isInteger(expectedInputRevision) || expectedInputRevision < 0) {
      throw new TaskGatewayError(
        "invalid",
        "The expected input revision is invalid.",
      );
    }
    return request(
      "Deterministic result",
      () =>
        client.POST("/api/v1/tasks/{taskId}/commands/generate-result", {
          params: {
            path: { taskId: identity },
            header: { "Idempotency-Key": key },
          },
          body: { expectedInputRevision },
        }),
      mapTaskCurrentResult,
    );
  },
  getCurrentResult: async (taskId) => {
    const identity = normalizeTaskIdentity(taskId);
    try {
      return await request(
        "Current result",
        () =>
          client.GET("/api/v1/tasks/{taskId}/current-result", {
            params: { path: { taskId: identity } },
          }),
        mapTaskCurrentResult,
      );
    } catch (error) {
      if (error instanceof TaskGatewayError && error.kind === "missing") {
        return null;
      }
      throw error;
    }
  },
  confirmCurrentResult: async (
    taskId,
    idempotencyKey,
    expectedResultRevision,
    input,
  ) => {
    const identity = normalizeTaskIdentity(taskId);
    const key = normalizeIdempotencyKey(idempotencyKey);
    if (
      !Number.isInteger(expectedResultRevision) ||
      expectedResultRevision < 0
    ) {
      throw new TaskGatewayError(
        "invalid",
        "The expected result revision is invalid.",
      );
    }
    return request(
      "Result confirmation",
      () =>
        client.POST("/api/v1/tasks/{taskId}/commands/confirm-current-result", {
          params: {
            path: { taskId: identity },
            header: { "Idempotency-Key": key },
          },
          body: { expectedResultRevision, ...input },
        }),
      mapTaskCurrentResult,
    );
  },
  previewExport: async (taskId, briefKind: ExportBriefKind) => {
    const identity = normalizeTaskIdentity(taskId);
    if (briefKind !== "marketing" && briefKind !== "xiaohongshu") {
      throw new TaskGatewayError("invalid", "The export family is invalid.");
    }
    return request(
      "Export preview",
      () =>
        client.POST("/api/v1/tasks/{taskId}/export-previews", {
          params: { path: { taskId: identity } },
          body: { briefKind },
        }),
      mapTaskExportPreview,
    );
  },
  createExportSnapshot: async (idempotencyKey, basis: ExportBasis) => {
    const key = normalizeIdempotencyKey(idempotencyKey);
    return request(
      "Export snapshot",
      () =>
        client.POST("/api/v1/export-snapshots", {
          params: { header: { "Idempotency-Key": key } },
          body: {
            basis: {
              ...basis,
              upstreamVersions: [...basis.upstreamVersions],
              hypotheses: [...basis.hypotheses],
              evidenceLimitations: [...basis.evidenceLimitations],
              risks: [...basis.risks],
            },
          },
        }),
      mapTaskExportSnapshot,
    );
  },
  downloadExportContent: async (snapshot: ExportSnapshot) => {
    const identity = normalizeTaskIdentity(snapshot.exportSnapshotId);
    let result: ClientResult<string>;
    try {
      result = await client.GET(
        "/api/v1/export-snapshots/{exportSnapshotId}/content",
        { params: { path: { exportSnapshotId: identity } }, parseAs: "text" },
      );
    } catch {
      throw new TaskGatewayError(
        "temporary",
        "Export download is temporarily unavailable.",
      );
    }
    if (result.data === undefined || result.data === null) {
      throw failure(result.response?.status, "Export download");
    }
    const header = result.response?.headers.get("content-disposition") ?? "";
    const filenameMatch = /filename="([^"]+)"/u.exec(header);
    if (filenameMatch === null || filenameMatch[1] !== snapshot.fileName) {
      throw new TaskGatewayError("invalid", "The export response is invalid.");
    }
    return { snapshot, content: result.data };
  },
});
