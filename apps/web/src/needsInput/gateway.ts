import type { components } from "../api/generated/schema";

export type NeedsInputStatus = "open" | "resolved" | "superseded" | "cancelled";
export type NeedsInputExpectedRecovery =
  "resume" | "rerun" | "manual_review" | "none";
export type NeedsInputResolutionType =
  | "provide_source_reference"
  | "choose_existing_value"
  | "submit_correction"
  | "confirm_known_limitation"
  | "cancel_path";

export type JsonValue =
  | null
  | boolean
  | number
  | string
  | readonly JsonValue[]
  | { readonly [key: string]: JsonValue };

export type NeedsInputResourceReference = Readonly<{
  resourceKind: string;
  resourceId: string;
}>;

export type NeedsInputMutableReference = NeedsInputResourceReference &
  Readonly<{ revision: number }>;

export type NeedsInputConflictValue = Readonly<{
  fieldPath: string;
  /** Canonical JSON.stringify text, kept as text so raw values cannot escape. */
  values: readonly string[];
}>;

export type NeedsInputActionRequest = Readonly<{
  actionRequestId: string;
  taskId: string;
  revision: number;
  status: NeedsInputStatus;
  reasonType: string;
  reasonSummary: string;
  affectedStages: readonly string[];
  sourceReferences: readonly NeedsInputResourceReference[];
  conflictValues: readonly NeedsInputConflictValue[];
  allowedResolutionTypes: readonly NeedsInputResolutionType[];
  expectedRecovery: NeedsInputExpectedRecovery;
  supersededBy: NeedsInputMutableReference | null;
}>;

export type NeedsInputResolution =
  | Readonly<{
      type: "provide_source_reference";
      sourceReferences: readonly NeedsInputResourceReference[];
      notes?: string;
    }>
  | Readonly<{
      type: "choose_existing_value";
      selectedValue: JsonValue;
      notes?: string;
    }>
  | Readonly<{
      type: "submit_correction";
      correctedValue: JsonValue;
      notes?: string;
    }>
  | Readonly<{
      type: "confirm_known_limitation";
      notes?: string;
    }>
  | Readonly<{
      type: "cancel_path";
      notes?: string;
    }>;

export type NeedsInputResolutionResult = Readonly<{
  actionRequest: NeedsInputActionRequest;
  task: Readonly<{ taskId: string }>;
}>;

export interface NeedsInputGateway {
  getNeedsInputActionRequest(
    actionRequestId: string,
  ): Promise<NeedsInputActionRequest>;
  resolveNeedsInput(
    actionRequestId: string,
    expectedRevision: number,
    resolution: NeedsInputResolution,
    idempotencyKey: string,
  ): Promise<NeedsInputResolutionResult>;
}

export type NeedsInputGatewayErrorKind =
  "temporary" | "missing" | "stale" | "invalid";

export class NeedsInputGatewayError extends Error {
  constructor(
    readonly kind: NeedsInputGatewayErrorKind,
    message: string,
  ) {
    super(message);
    this.name = "NeedsInputGatewayError";
  }
}

const statuses: readonly NeedsInputStatus[] = [
  "open",
  "resolved",
  "superseded",
  "cancelled",
];
const recoveries: readonly NeedsInputExpectedRecovery[] = [
  "resume",
  "rerun",
  "manual_review",
  "none",
];
const resolutionTypes: readonly NeedsInputResolutionType[] = [
  "provide_source_reference",
  "choose_existing_value",
  "submit_correction",
  "confirm_known_limitation",
  "cancel_path",
];
const maxNotesLength = 4096;
const invalidRead = () =>
  new NeedsInputGatewayError("invalid", "The Needs Input response is invalid.");
const invalidRequest = (message = "The Needs Input request is invalid.") =>
  new NeedsInputGatewayError("invalid", message);

const isPlainObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" &&
  value !== null &&
  !Array.isArray(value) &&
  (Object.getPrototypeOf(value) === Object.prototype ||
    Object.getPrototypeOf(value) === null);

const nonblank = (value: unknown, message: string): string => {
  if (typeof value !== "string" || value.trim() === "") {
    throw invalidRequest(message);
  }
  return value;
};

const revision = (value: unknown): number => {
  if (!Number.isInteger(value) || (value as number) < 0) {
    throw invalidRead();
  }
  return value as number;
};

const enumValue = <T extends string>(
  value: unknown,
  values: readonly T[],
): T => {
  if (typeof value !== "string" || !values.includes(value as T)) {
    throw invalidRead();
  }
  return value as T;
};

const deepFreeze = <T>(value: T): T => {
  if (typeof value !== "object" || value === null) return value;
  if (Object.isFrozen(value)) return value;
  Object.freeze(value);
  for (const child of Object.values(value as Record<string, unknown>)) {
    deepFreeze(child);
  }
  return value;
};

/**
 * Serialize a value with the platform JSON.stringify rules while rejecting
 * values that JSON.stringify would silently drop or coerce.
 */
export const canonicalJson = (value: unknown): string => {
  const seen = new WeakSet<object>();
  let serialized: string | undefined;
  try {
    serialized = JSON.stringify(value, (_key, current: unknown) => {
      if (
        typeof current === "undefined" ||
        typeof current === "function" ||
        typeof current === "symbol" ||
        typeof current === "bigint"
      ) {
        throw new Error("non-json");
      }
      if (typeof current === "number" && !Number.isFinite(current)) {
        throw new Error("non-json");
      }
      if (typeof current === "object" && current !== null) {
        if (seen.has(current)) throw new Error("circular");
        seen.add(current);
      }
      return current;
    });
  } catch {
    throw invalidRequest("A conflict value is not valid JSON.");
  }
  if (serialized === undefined) {
    throw invalidRequest("A conflict value is not valid JSON.");
  }
  return serialized;
};

const detachedJson = (value: unknown): JsonValue => {
  const text = canonicalJson(value);
  return JSON.parse(text) as JsonValue;
};

const mapReference = (value: unknown): NeedsInputResourceReference => {
  if (!isPlainObject(value)) throw invalidRead();
  return deepFreeze({
    resourceKind: nonblank(
      value.resourceKind,
      "The Needs Input response is invalid.",
    ),
    resourceId: nonblank(
      value.resourceId,
      "The Needs Input response is invalid.",
    ),
  });
};

const mapMutableReference = (value: unknown): NeedsInputMutableReference => {
  if (!isPlainObject(value)) throw invalidRead();
  return deepFreeze({
    ...mapReference(value),
    revision: revision(value.revision),
  });
};

const mapConflictValue = (value: unknown): NeedsInputConflictValue => {
  if (!isPlainObject(value) || !Array.isArray(value.values))
    throw invalidRead();
  const fieldPath = nonblank(
    value.fieldPath,
    "The Needs Input response is invalid.",
  );
  const values = value.values.map((item) => canonicalJson(item));
  if (values.length === 0) throw invalidRead();
  return deepFreeze({ fieldPath, values: Object.freeze(values) });
};

export const mapNeedsInputActionRequest = (
  value: unknown,
): NeedsInputActionRequest => {
  if (!isPlainObject(value)) throw invalidRead();
  const affectedStages = value.affectedStages;
  const sourceReferences = value.sourceReferences;
  const conflictValues = value.conflictValues;
  const allowed = value.allowedResolutionTypes;
  if (
    !Array.isArray(affectedStages) ||
    affectedStages.some(
      (item) => typeof item !== "string" || item.trim() === "",
    ) ||
    !Array.isArray(sourceReferences) ||
    !Array.isArray(conflictValues) ||
    !Array.isArray(allowed)
  ) {
    throw invalidRead();
  }
  const supersededBy =
    value.supersededBy === null || value.supersededBy === undefined
      ? null
      : mapMutableReference(value.supersededBy);
  const request: NeedsInputActionRequest = {
    actionRequestId: nonblank(
      value.actionRequestId,
      "The Needs Input response is invalid.",
    ),
    taskId: nonblank(value.taskId, "The Needs Input response is invalid."),
    revision: revision(value.revision),
    status: enumValue(value.status, statuses),
    reasonType: nonblank(
      value.reasonType,
      "The Needs Input response is invalid.",
    ),
    reasonSummary: nonblank(
      value.reasonSummary,
      "The Needs Input response is invalid.",
    ),
    affectedStages: Object.freeze(affectedStages.map((item) => item as string)),
    sourceReferences: Object.freeze(sourceReferences.map(mapReference)),
    conflictValues: Object.freeze(conflictValues.map(mapConflictValue)),
    allowedResolutionTypes: Object.freeze(
      allowed.map((item) => enumValue(item, resolutionTypes)),
    ),
    expectedRecovery: enumValue(value.expectedRecovery, recoveries),
    supersededBy,
  };
  return deepFreeze(request);
};

export const mapNeedsInputResolution = (
  value: unknown,
): NeedsInputResolution => {
  if (!isPlainObject(value)) throw invalidRequest();
  const type = enumValue(value.type, resolutionTypes);
  const notes =
    value.notes === undefined
      ? undefined
      : (() => {
          if (typeof value.notes !== "string") throw invalidRequest();
          const normalized = value.notes.trim();
          if (normalized.length > maxNotesLength) throw invalidRequest();
          return normalized;
        })();
  if (type === "provide_source_reference") {
    if (
      !Array.isArray(value.sourceReferences) ||
      value.sourceReferences.length < 1
    ) {
      throw invalidRequest();
    }
    return deepFreeze({
      type,
      sourceReferences: Object.freeze(value.sourceReferences.map(mapReference)),
      ...(notes === undefined ? {} : { notes }),
    });
  }
  if (type === "choose_existing_value") {
    if (!("selectedValue" in value)) throw invalidRequest();
    return deepFreeze({
      type,
      selectedValue: detachedJson(value.selectedValue),
      ...(notes === undefined ? {} : { notes }),
    });
  }
  if (type === "submit_correction") {
    if (!("correctedValue" in value)) throw invalidRequest();
    return deepFreeze({
      type,
      correctedValue: detachedJson(value.correctedValue),
      ...(notes === undefined ? {} : { notes }),
    });
  }
  return deepFreeze({
    type,
    ...(notes === undefined ? {} : { notes }),
  });
};

export const resolutionToWire = (
  value: NeedsInputResolution,
): components["schemas"]["NeedsInputResolution"] => {
  const resolution = mapNeedsInputResolution(value);
  switch (resolution.type) {
    case "provide_source_reference":
      return {
        resolutionType: "provide_source_reference",
        sourceReferences: resolution.sourceReferences.map((reference) => ({
          resourceKind: reference.resourceKind,
          resourceId: reference.resourceId,
        })),
        ...(resolution.notes === undefined ? {} : { notes: resolution.notes }),
      } as unknown as components["schemas"]["NeedsInputResolution"];
    case "choose_existing_value":
      return {
        resolutionType: "choose_existing_value",
        selectedValue: resolution.selectedValue,
        ...(resolution.notes === undefined ? {} : { notes: resolution.notes }),
      } as unknown as components["schemas"]["NeedsInputResolution"];
    case "submit_correction":
      return {
        resolutionType: "submit_correction",
        correctedValue: resolution.correctedValue,
        ...(resolution.notes === undefined ? {} : { notes: resolution.notes }),
      } as unknown as components["schemas"]["NeedsInputResolution"];
    case "confirm_known_limitation":
      return {
        resolutionType: "confirm_known_limitation",
        ...(resolution.notes === undefined ? {} : { notes: resolution.notes }),
      } as unknown as components["schemas"]["NeedsInputResolution"];
    case "cancel_path":
      return {
        resolutionType: "cancel_path",
        ...(resolution.notes === undefined ? {} : { notes: resolution.notes }),
      } as unknown as components["schemas"]["NeedsInputResolution"];
  }
};

export const mapNeedsInputResolutionResult = (
  value: unknown,
): NeedsInputResolutionResult => {
  if (!isPlainObject(value) || !isPlainObject(value.task)) throw invalidRead();
  const actionRequest = mapNeedsInputActionRequest(value.actionRequest);
  const taskId = nonblank(
    value.task.taskId,
    "The Needs Input response is invalid.",
  );
  if (taskId !== actionRequest.taskId) throw invalidRead();
  return deepFreeze({ actionRequest, task: { taskId } });
};

export const cloneNeedsInputActionRequest = (
  request: NeedsInputActionRequest,
): NeedsInputActionRequest =>
  mapNeedsInputActionRequest({
    ...request,
    affectedStages: [...request.affectedStages],
    sourceReferences: request.sourceReferences.map((reference) => ({
      ...reference,
    })),
    conflictValues: request.conflictValues.map((conflict) => ({
      fieldPath: conflict.fieldPath,
      values: conflict.values.map((value) => JSON.parse(value) as unknown),
    })),
    allowedResolutionTypes: [...request.allowedResolutionTypes],
    supersededBy:
      request.supersededBy === null ? null : { ...request.supersededBy },
  });

export const resolutionIdentity = (resolution: NeedsInputResolution): string =>
  JSON.stringify(mapNeedsInputResolution(resolution));
