import { describe, expect, it, vi } from "vitest";

type NeedsInputActionRequest = Readonly<{
  actionRequestId: string;
  taskId: string;
  revision: number;
  status: "open" | "resolved" | "superseded" | "cancelled";
  reasonType: string;
  reasonSummary: string;
  affectedStages: readonly string[];
  sourceReferences: readonly Readonly<{
    resourceKind: string;
    resourceId: string;
  }>[];
  conflictValues: readonly Readonly<{
    fieldPath: string;
    values: readonly string[];
  }>[];
  allowedResolutionTypes: readonly string[];
  expectedRecovery: "resume" | "rerun" | "manual_review" | "none";
  supersededBy: Readonly<{
    resourceKind: string;
    resourceId: string;
    revision: number;
  }> | null;
}>;

const loadGateway = async () => {
  try {
    const modulePath = "./gateway";
    return await import(/* @vite-ignore */ modulePath);
  } catch {
    return null;
  }
};
const loadHttpGateway = async () => {
  try {
    const modulePath = "./httpGateway";
    return await import(/* @vite-ignore */ modulePath);
  } catch {
    return null;
  }
};
const loadDeterministicGateway = async () => {
  try {
    const modulePath = "./deterministicGateway";
    return await import(/* @vite-ignore */ modulePath);
  } catch {
    return null;
  }
};

const dto = {
  actionRequestId: "action-1",
  taskId: "task-1",
  revision: 2,
  status: "open",
  reasonType: "identity_conflict",
  reasonSummary: "商品身份存在两个候选值。",
  affectedStages: ["product_intake_and_fact_extraction"],
  sourceReferences: [
    { resourceKind: "source_version", resourceId: "source-1" },
  ],
  conflictValues: [
    {
      fieldPath: "product.sku",
      values: ["CBP-SYN-001", "CBP-SYN-002"],
    },
  ],
  allowedResolutionTypes: ["choose_existing_value", "cancel_path"],
  expectedRecovery: "resume",
  supersededBy: null,
} as const;

const seededRequest = (): NeedsInputActionRequest => ({
  actionRequestId: dto.actionRequestId,
  taskId: dto.taskId,
  revision: dto.revision,
  status: dto.status,
  reasonType: dto.reasonType,
  reasonSummary: dto.reasonSummary,
  affectedStages: dto.affectedStages,
  sourceReferences: dto.sourceReferences,
  conflictValues: [
    { fieldPath: "product.sku", values: ['"CBP-SYN-001"', '"CBP-SYN-002"'] },
  ],
  allowedResolutionTypes: dto.allowedResolutionTypes,
  expectedRecovery: dto.expectedRecovery,
  supersededBy: null,
});

describe("NeedsInputGateway", () => {
  it("maps the detached read model and canonicalizes conflict values", async () => {
    const module = await loadHttpGateway();
    expect(module).not.toBeNull();
    if (module === null) return;
    const client = {
      GET: vi.fn(async () => ({
        data: dto,
        response: new Response(null, { status: 200 }),
      })),
    };
    const gateway = module.createHttpNeedsInputGateway(client as never);

    const request = await gateway.getNeedsInputActionRequest("action-1");

    expect(request).toEqual(seededRequest());
    expect(Object.isFrozen(request)).toBe(true);
    expect(Object.isFrozen(request.affectedStages)).toBe(true);
    expect(Object.isFrozen(request.conflictValues[0])).toBe(true);
    expect(client.GET).toHaveBeenCalledWith(
      "/api/v1/needs-input-requests/{actionRequestId}",
      { params: { path: { actionRequestId: "action-1" } } },
    );
  });

  it("rejects non-JSON conflict values without exposing raw details", async () => {
    const module = await loadHttpGateway();
    expect(module).not.toBeNull();
    if (module === null) return;
    const client = {
      GET: vi.fn(async () => ({
        data: {
          ...dto,
          conflictValues: [{ fieldPath: "product.sku", values: [undefined] }],
        },
        response: new Response(null, { status: 200 }),
      })),
    };
    const gateway = module.createHttpNeedsInputGateway(client as never);

    await expect(
      gateway.getNeedsInputActionRequest("action-1"),
    ).rejects.toMatchObject({ kind: "invalid" });
  });

  it("serializes a typed resolution through the generated POST seam", async () => {
    const module = await loadHttpGateway();
    expect(module).not.toBeNull();
    if (module === null) return;
    const client = {
      POST: vi.fn(async () => ({
        data: {
          actionRequest: {
            ...dto,
            revision: 3,
            status: "resolved" as const,
            allowedResolutionTypes: [],
          },
          task: { taskId: "task-1" },
        },
        response: new Response(null, { status: 200 }),
      })),
    };
    const gateway = module.createHttpNeedsInputGateway(client as never);

    await gateway.resolveNeedsInput(
      "action-1",
      2,
      { type: "choose_existing_value", selectedValue: "CBP-SYN-001" },
      "needs-input:action-1:2:choose-existing",
    );

    expect(client.POST).toHaveBeenCalledWith(
      "/api/v1/needs-input-requests/{actionRequestId}/commands/resolve",
      {
        params: {
          path: { actionRequestId: "action-1" },
          header: {
            "Idempotency-Key": "needs-input:action-1:2:choose-existing",
          },
        },
        body: {
          expectedRevision: 2,
          resolution: {
            resolutionType: "choose_existing_value",
            selectedValue: "CBP-SYN-001",
          },
        },
      },
    );
  });

  it("requires an advanced terminal status in resolve responses", async () => {
    const invalidClient = {
      POST: vi.fn(async () => ({
        data: {
          actionRequest: { ...dto, revision: 2, status: "open" as const },
          task: { taskId: "task-1" },
        },
        response: new Response(null, { status: 200 }),
      })),
    };
    const invalidModule = await loadHttpGateway();
    expect(invalidModule).not.toBeNull();
    if (invalidModule === null) return;
    const invalidGateway = invalidModule.createHttpNeedsInputGateway(
      invalidClient as never,
    );

    await expect(
      invalidGateway.resolveNeedsInput(
        "action-1",
        2,
        { type: "choose_existing_value", selectedValue: "CBP-SYN-001" },
        "key-invalid-response",
      ),
    ).rejects.toMatchObject({ kind: "invalid" });

    const validCases = [
      {
        resolution: { type: "cancel_path" } as const,
        status: "cancelled" as const,
      },
      {
        resolution: {
          type: "choose_existing_value",
          selectedValue: "CBP-SYN-001",
        } as const,
        status: "resolved" as const,
      },
    ];
    for (const { resolution, status } of validCases) {
      const client = {
        POST: vi.fn(async () => ({
          data: {
            actionRequest: {
              ...dto,
              revision: 3,
              status,
              allowedResolutionTypes: [],
            },
            task: { taskId: "task-1" },
          },
          response: new Response(null, { status: 200 }),
        })),
      };
      const module = await loadHttpGateway();
      expect(module).not.toBeNull();
      if (module === null) return;
      const gateway = module.createHttpNeedsInputGateway(client as never);

      const result = await gateway.resolveNeedsInput(
        "action-1",
        2,
        resolution,
        `key-${status}`,
      );

      expect(result.actionRequest.revision).toBe(3);
      expect(result.actionRequest.status).toBe(status);
    }
  });

  it("maps HTTP failures to fixed safe error categories", async () => {
    const statuses = [
      [404, "missing"],
      [409, "stale"],
      [422, "invalid"],
      [503, "temporary"],
    ] as const;

    for (const [status, kind] of statuses) {
      const module = await loadHttpGateway();
      expect(module).not.toBeNull();
      if (module === null) return;
      const client = {
        GET: vi.fn(async () => ({ response: new Response(null, { status }) })),
      };
      const gateway = module.createHttpNeedsInputGateway(client as never);
      await expect(
        gateway.getNeedsInputActionRequest("action-1"),
      ).rejects.toMatchObject({
        kind,
      });
      await expect(
        gateway.getNeedsInputActionRequest("action-1"),
      ).rejects.not.toThrow(/action-1|status|Response|detail/iu);
    }
  });

  it("resolves a deterministic request once and replays the same key", async () => {
    const module = await loadDeterministicGateway();
    expect(module).not.toBeNull();
    if (module === null) return;
    const gateway = module.createDeterministicNeedsInputGateway({
      actionRequests: [seededRequest()],
    });
    const resolution = {
      type: "choose_existing_value" as const,
      selectedValue: "CBP-SYN-001",
    };

    const first = await gateway.resolveNeedsInput(
      "action-1",
      2,
      resolution,
      "key-1",
    );
    const replay = await gateway.resolveNeedsInput(
      "action-1",
      2,
      resolution,
      "key-1",
    );

    expect(first.actionRequest.status).toBe("resolved");
    expect(first.actionRequest.revision).toBe(3);
    expect(first.task).toEqual({ taskId: "task-1" });
    expect(replay).toEqual(first);
    expect(replay).not.toBe(first);
    expect(() => {
      first.actionRequest.allowedResolutionTypes.push("cancel_path");
    }).toThrow();
    await expect(
      gateway.resolveNeedsInput(
        "action-1",
        2,
        { type: "cancel_path" },
        "key-1",
      ),
    ).rejects.toMatchObject({ kind: "invalid" });
  });

  it("uses only the server allowlist and rejects stale writes", async () => {
    const module = await loadDeterministicGateway();
    expect(module).not.toBeNull();
    if (module === null) return;
    const gateway = module.createDeterministicNeedsInputGateway({
      actionRequests: [seededRequest()],
    });

    await expect(
      gateway.resolveNeedsInput(
        "action-1",
        1,
        { type: "confirm_known_limitation" },
        "key-stale",
      ),
    ).rejects.toMatchObject({ kind: "stale" });
    await expect(
      gateway.resolveNeedsInput(
        "action-1",
        2,
        { type: "confirm_known_limitation" },
        "key-not-allowed",
      ),
    ).rejects.toMatchObject({ kind: "invalid" });
  });

  it("uses a safe public error shape", () => {
    return loadGateway().then((module) => {
      expect(module).not.toBeNull();
      if (module === null) return;
      const error = new module.NeedsInputGatewayError(
        "temporary",
        "暂时无法读取该请求。",
      );
      expect(error.name).toBe("NeedsInputGatewayError");
      expect(error.kind).toBe("temporary");
      expect(error.message).toBe("暂时无法读取该请求。");
    });
  });
});
