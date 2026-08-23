import { describe, expect, it, vi } from "vitest";
import { createApiClient } from "../../src/api/client";
import { createHttpNeedsInputGateway } from "../../src/needsInput/httpGateway";
import type { NeedsInputResolution } from "../../src/needsInput/gateway";

const requestDto = {
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
    { fieldPath: "product.sku", values: ["CBP-SYN-001", "CBP-SYN-002"] },
  ],
  allowedResolutionTypes: ["choose_existing_value"],
  expectedRecovery: "resume",
  supersededBy: null,
} as const;

const responseDto = {
  actionRequest: {
    ...requestDto,
    revision: 3,
    status: "resolved",
    allowedResolutionTypes: [],
  },
  task: { taskId: "task-1" },
} as const;

const jsonResponse = (value: unknown, status = 200): Response =>
  new Response(JSON.stringify(value), {
    status,
    headers: { "content-type": "application/json" },
  });

const resolution: NeedsInputResolution = {
  type: "choose_existing_value",
  selectedValue: "CBP-SYN-001",
};

describe("Needs Input gateway HTTP contract", () => {
  it("reads the typed action request through the generated same-origin client", async () => {
    const fetch = vi.fn().mockResolvedValue(jsonResponse(requestDto));
    const gateway = createHttpNeedsInputGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    const mapped = await gateway.getNeedsInputActionRequest("action-1");
    const [request] = fetch.mock.calls[0] as [Request];

    expect(request.url).toBe(
      "https://example.test/api/v1/needs-input-requests/action-1",
    );
    expect(request.method).toBe("GET");
    expect(mapped).not.toBe(requestDto);
    expect(Object.isFrozen(mapped)).toBe(true);
    expect(Object.isFrozen(mapped.conflictValues[0])).toBe(true);
    expect(mapped.conflictValues[0]?.values).toEqual([
      '"CBP-SYN-001"',
      '"CBP-SYN-002"',
    ]);
  });

  it("sends only the typed resolution body and idempotency header", async () => {
    const fetch = vi.fn().mockResolvedValue(jsonResponse(responseDto));
    const gateway = createHttpNeedsInputGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    await gateway.resolveNeedsInput("action-1", 2, resolution, "needs-key-1");
    const [request] = fetch.mock.calls[0] as [Request];

    expect(request.url).toBe(
      "https://example.test/api/v1/needs-input-requests/action-1/commands/resolve",
    );
    expect(request.method).toBe("POST");
    expect(request.headers.get("Idempotency-Key")).toBe("needs-key-1");
    expect(JSON.parse(await request.text())).toEqual({
      expectedRevision: 2,
      resolution: {
        resolutionType: "choose_existing_value",
        selectedValue: "CBP-SYN-001",
      },
    });
  });

  it("maps transport failures to fixed safe categories", async () => {
    const fetch = vi
      .fn()
      .mockRejectedValueOnce(new Error("private network detail"))
      .mockResolvedValueOnce(
        jsonResponse({ detail: "private server detail" }, 503),
      )
      .mockResolvedValueOnce(
        jsonResponse({ detail: "private server detail" }, 503),
      );
    const gateway = createHttpNeedsInputGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    await expect(
      gateway.getNeedsInputActionRequest("action-1"),
    ).rejects.toMatchObject({ kind: "temporary" });
    await expect(
      gateway.getNeedsInputActionRequest("action-1"),
    ).rejects.toMatchObject({ kind: "temporary" });
    await expect(
      gateway.getNeedsInputActionRequest("action-1"),
    ).rejects.not.toThrow("private");
  });
});
