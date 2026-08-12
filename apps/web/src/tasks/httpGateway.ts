import type { ApiClient } from "../api/client";
import {
  mapTaskOverview,
  mapTaskSummary,
  normalizeIdempotencyKey,
  normalizeTaskIdentity,
  normalizeTaskInput,
  TaskGatewayError,
  type TaskGateway,
} from "./gateway";

type ClientResult<T> = { data?: T; response?: { status?: number } };
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
});
