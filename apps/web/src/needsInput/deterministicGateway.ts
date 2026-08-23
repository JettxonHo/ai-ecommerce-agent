import {
  canonicalJson,
  cloneNeedsInputActionRequest,
  mapNeedsInputResolution,
  NeedsInputGatewayError,
  resolutionIdentity,
  type NeedsInputActionRequest,
  type NeedsInputGateway,
  type NeedsInputResolution,
  type NeedsInputResolutionResult,
} from "./gateway";

export type DeterministicNeedsInputGatewayOptions = Readonly<{
  actionRequests?: readonly NeedsInputActionRequest[];
}>;

const cloneResult = (
  value: NeedsInputResolutionResult,
): NeedsInputResolutionResult => ({
  actionRequest: cloneNeedsInputActionRequest(value.actionRequest),
  task: Object.freeze({ taskId: value.task.taskId }),
});

type Replay = Readonly<{
  expectedRevision: number;
  resolution: string;
  result: NeedsInputResolutionResult;
}>;

export const createDeterministicNeedsInputGateway = (
  options: DeterministicNeedsInputGatewayOptions = {},
): NeedsInputGateway => {
  const current = new Map<string, NeedsInputActionRequest>();
  for (const seeded of options.actionRequests ?? []) {
    const request = cloneNeedsInputActionRequest(seeded);
    if (current.has(request.actionRequestId)) {
      throw new NeedsInputGatewayError(
        "invalid",
        "Duplicate Needs Input request identity.",
      );
    }
    current.set(request.actionRequestId, request);
  }

  const replays = new Map<string, Replay>();

  const getNeedsInputActionRequest = async (
    actionRequestId: string,
  ): Promise<NeedsInputActionRequest> => {
    if (typeof actionRequestId !== "string" || actionRequestId.trim() === "") {
      throw new NeedsInputGatewayError("invalid", "补充请求身份无效。");
    }
    const request = current.get(actionRequestId);
    if (request === undefined) {
      throw new NeedsInputGatewayError("missing", "该补充请求已不存在。");
    }
    return cloneNeedsInputActionRequest(request);
  };

  const resolveNeedsInput = async (
    actionRequestId: string,
    expectedRevision: number,
    candidate: NeedsInputResolution,
    idempotencyKey: string,
  ): Promise<NeedsInputResolutionResult> => {
    if (typeof actionRequestId !== "string" || actionRequestId.trim() === "") {
      throw new NeedsInputGatewayError("invalid", "补充请求身份无效。");
    }
    if (
      !Number.isInteger(expectedRevision) ||
      expectedRevision < 0 ||
      typeof idempotencyKey !== "string" ||
      idempotencyKey.trim() === ""
    ) {
      throw new NeedsInputGatewayError("invalid", "补充动作输入无效。");
    }
    const resolution = mapNeedsInputResolution(candidate);
    const resolutionKey = resolutionIdentity(resolution);
    const replayKey = `${actionRequestId}\u0000${idempotencyKey}`;
    const replay = replays.get(replayKey);
    if (replay !== undefined) {
      if (
        replay.expectedRevision !== expectedRevision ||
        replay.resolution !== resolutionKey
      ) {
        throw new NeedsInputGatewayError(
          "invalid",
          "该幂等键已用于另一项补充动作。",
        );
      }
      return cloneResult(replay.result);
    }

    const request = current.get(actionRequestId);
    if (request === undefined) {
      throw new NeedsInputGatewayError("missing", "该补充请求已不存在。");
    }
    if (request.status !== "open" || request.revision !== expectedRevision) {
      throw new NeedsInputGatewayError(
        "stale",
        "当前补充请求已变化，请先刷新任务事实。",
      );
    }
    if (!request.allowedResolutionTypes.includes(resolution.type)) {
      throw new NeedsInputGatewayError(
        "invalid",
        "该补充动作当前不在服务端允许范围内。",
      );
    }
    if (resolution.type === "choose_existing_value") {
      if (request.conflictValues.length !== 1) {
        throw new NeedsInputGatewayError(
          "invalid",
          "当前冲突不能安全地选择单个既有值。",
        );
      }
      const allowedValues = request.conflictValues[0]?.values ?? [];
      if (!allowedValues.includes(canonicalJson(resolution.selectedValue))) {
        throw new NeedsInputGatewayError(
          "invalid",
          "所选值不在服务端提供的候选范围内。",
        );
      }
    }

    const resolved = cloneNeedsInputActionRequest({
      ...request,
      revision: request.revision + 1,
      status: resolution.type === "cancel_path" ? "cancelled" : "resolved",
      allowedResolutionTypes: Object.freeze([]),
      supersededBy: null,
    });
    const result: NeedsInputResolutionResult = Object.freeze({
      actionRequest: resolved,
      task: Object.freeze({ taskId: request.taskId }),
    });
    current.set(actionRequestId, resolved);
    replays.set(replayKey, {
      expectedRevision,
      resolution: resolutionKey,
      result,
    });
    return cloneResult(result);
  };

  return Object.freeze({
    getNeedsInputActionRequest,
    resolveNeedsInput,
  });
};
