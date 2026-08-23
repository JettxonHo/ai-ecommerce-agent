import type { ApiClient } from "../api/client";
import {
  mapNeedsInputActionRequest,
  mapNeedsInputResolution,
  mapNeedsInputResolutionResult,
  NeedsInputGatewayError,
  resolutionToWire,
  type NeedsInputGateway,
  type NeedsInputResolution,
} from "./gateway";

type ClientResult<T> = { data?: T; response?: Response };

const safeFailure = (
  status: number | undefined,
  operation: string,
): NeedsInputGatewayError => {
  if (status === 404) {
    return new NeedsInputGatewayError("missing", "该补充请求已不存在。");
  }
  if (status === 409) {
    return new NeedsInputGatewayError(
      "stale",
      "当前补充请求已变化，请先刷新任务事实。",
    );
  }
  if (status !== undefined && status >= 400 && status < 500) {
    return new NeedsInputGatewayError("invalid", "该补充动作无法提交。");
  }
  return new NeedsInputGatewayError(
    "temporary",
    `${operation}暂时不可用，请稍后重试。`,
  );
};

const identity = (value: unknown): string => {
  if (typeof value !== "string" || value.trim() === "") {
    throw new NeedsInputGatewayError("invalid", "补充请求身份无效。");
  }
  return value;
};

const expectedRevision = (value: unknown): number => {
  if (!Number.isInteger(value) || (value as number) < 0) {
    throw new NeedsInputGatewayError("invalid", "补充请求版本无效。");
  }
  return value as number;
};

const idempotencyKey = (value: unknown): string => {
  if (typeof value !== "string" || value.trim() === "") {
    throw new NeedsInputGatewayError("invalid", "补充动作幂等键无效。");
  }
  return value;
};

const request = async <T, R>(
  operation: string,
  call: () => Promise<ClientResult<T>>,
  map: (value: T) => R,
): Promise<R> => {
  let result: ClientResult<T>;
  try {
    result = await call();
  } catch {
    throw safeFailure(undefined, operation);
  }
  if (result.data === undefined || result.data === null) {
    throw safeFailure(result.response?.status, operation);
  }
  try {
    return map(result.data);
  } catch (error) {
    if (error instanceof NeedsInputGatewayError && error.kind === "temporary") {
      throw error;
    }
    throw new NeedsInputGatewayError("invalid", "补充请求响应无效。");
  }
};

export const createHttpNeedsInputGateway = (
  client: ApiClient,
): NeedsInputGateway => ({
  getNeedsInputActionRequest: async (actionRequestId) => {
    const identityValue = identity(actionRequestId);
    return request(
      "补充请求读取",
      () =>
        client.GET("/api/v1/needs-input-requests/{actionRequestId}", {
          params: { path: { actionRequestId: identityValue } },
        }),
      (value) => {
        const mapped = mapNeedsInputActionRequest(value);
        if (mapped.actionRequestId !== identityValue) {
          throw new NeedsInputGatewayError("invalid", "补充请求响应无效。");
        }
        return mapped;
      },
    );
  },
  resolveNeedsInput: async (
    actionRequestId,
    revision,
    value: NeedsInputResolution,
    key,
  ) => {
    const identityValue = identity(actionRequestId);
    const expected = expectedRevision(revision);
    const idempotency = idempotencyKey(key);
    const resolution = mapNeedsInputResolution(value);
    return request(
      "补充动作提交",
      () =>
        client.POST(
          "/api/v1/needs-input-requests/{actionRequestId}/commands/resolve",
          {
            params: {
              path: { actionRequestId: identityValue },
              header: { "Idempotency-Key": idempotency },
            },
            body: {
              expectedRevision: expected,
              resolution: resolutionToWire(resolution),
            },
          },
        ),
      (response) => {
        const mapped = mapNeedsInputResolutionResult(response);
        const expectedStatus =
          resolution.type === "cancel_path" ? "cancelled" : "resolved";
        if (
          mapped.actionRequest.actionRequestId !== identityValue ||
          mapped.actionRequest.taskId !== mapped.task.taskId ||
          mapped.actionRequest.revision <= expected ||
          mapped.actionRequest.status !== expectedStatus
        ) {
          throw new NeedsInputGatewayError("invalid", "补充请求响应无效。");
        }
        return mapped;
      },
    );
  },
});
