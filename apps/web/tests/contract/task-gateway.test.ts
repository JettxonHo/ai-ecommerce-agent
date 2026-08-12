import { describe, expect, it, vi } from "vitest";
import { createApiClient } from "../../src/api/client";
import type { components } from "../../src/api/generated/schema";
import {
  cloneTaskOverview,
  mapTaskOverview,
  TaskGatewayError,
  type TaskGateway,
  type TaskInput,
  type TaskOverview,
} from "../../src/tasks/gateway";
import { createDeterministicTaskGateway } from "../../src/tasks/deterministicGateway";
import { createHttpTaskGateway } from "../../src/tasks/httpGateway";

const overviewBaseline: TaskOverview = {
  taskId: "task-1",
  taskName: "Launch",
  productCategory: "Backpack",
  taskStatus: "draft",
  currentStage: null,
  waitingReason: null,
  updatedAt: "2026-08-12T00:00:00Z",
  revision: 0,
  primaryAction: { kind: "none" },
  capabilities: [],
  stages: [],
  activeRunId: null,
  latestRunId: null,
  needsInputRequest: null,
  reviewPackage: null,
  approvedStrategy: null,
  marketingBrief: null,
  xiaohongshuBrief: null,
};
const overview = (overrides: Partial<TaskOverview> = {}): TaskOverview => ({
  ...overviewBaseline,
  ...overrides,
});

const generatedOverview = (
  overrides: Partial<components["schemas"]["TaskOverview"]> = {},
): components["schemas"]["TaskOverview"] => ({
  taskId: "task-1",
  taskName: "Launch",
  productCategory: "Backpack",
  taskStatus: "draft",
  currentStage: null,
  waitingReason: null,
  updatedAt: "2026-08-12T00:00:00Z",
  revision: 0,
  primaryAction: { type: "NoPrimaryAction" },
  capabilities: [],
  stages: [],
  activeRun: null,
  latestRun: null,
  needsInputRequest: null,
  reviewPackage: null,
  approvedStrategy: null,
  marketingBrief: null,
  xiaohongshuBrief: null,
  ...overrides,
});

const generatedPrimaryInput = (
  overrides: Partial<components["schemas"]["TaskPrimaryInput"]> = {},
): components["schemas"]["TaskPrimaryInput"] => ({
  taskId: "task-1",
  inputRevision: 0,
  inputKind: "pasted_text",
  fileName: null,
  content: "Saved context",
  byteCount: 13,
  updatedAt: "2026-08-12T00:00:00Z",
  ...overrides,
});

const input: TaskInput = {
  taskName: "Launch",
  productCategory: "Backpack",
  promotionGoal: "Awareness",
};

const response = (body: unknown, status = 200): Response =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

describe("TaskGateway HTTP contract", () => {
  it("validates the primary-input projection before exposing it", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(response(generatedPrimaryInput()))
      .mockResolvedValueOnce(response({}));
    const gateway = createHttpTaskGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    await expect(gateway.getPrimaryInput("task-1")).resolves.toMatchObject({
      taskId: "task-1",
      content: "Saved context",
      byteCount: 13,
    });
    await expect(gateway.getPrimaryInput("task-1")).rejects.toMatchObject({
      kind: "invalid",
    });
  });

  it("keeps file metadata basename-safe and accepts case-insensitive extensions", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(
        response(
          generatedPrimaryInput({
            inputKind: "text_file",
            fileName: "NOTES.TXT",
            updatedAt: "2026-08-12T01:02:03+08:00",
          }),
        ),
      )
      .mockResolvedValueOnce(
        response(
          generatedPrimaryInput({
            inputKind: "text_file",
            fileName: "../notes.txt",
          }),
        ),
      );
    const gateway = createHttpTaskGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    await expect(gateway.getPrimaryInput("task-1")).resolves.toMatchObject({
      inputKind: "text_file",
      fileName: "NOTES.TXT",
    });
    await expect(gateway.getPrimaryInput("task-1")).rejects.toMatchObject({
      kind: "invalid",
    });
  });

  it("rejects date-only and impossible primary-input timestamps", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(
        response(generatedPrimaryInput({ updatedAt: "2026-08-12" })),
      )
      .mockResolvedValueOnce(
        response(generatedPrimaryInput({ updatedAt: "2026-02-30T00:00:00Z" })),
      );
    const gateway = createHttpTaskGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    await expect(gateway.getPrimaryInput("task-1")).rejects.toMatchObject({
      kind: "invalid",
    });
    await expect(gateway.getPrimaryInput("task-1")).rejects.toMatchObject({
      kind: "invalid",
    });
  });

  it("maps every TaskOverview related reference to detached identity-only values", () => {
    const dto = generatedOverview({
      activeRun: { runId: "run-active" },
      latestRun: { runId: "run-latest" },
      needsInputRequest: {
        resourceKind: "needs_input",
        resourceId: "input-1",
        revision: 4,
      },
      reviewPackage: { reviewPackageId: "review-1", packageVersion: 7 },
      approvedStrategy: {
        resourceKind: "strategy",
        resourceVersionId: "strategy-1",
        versionNumber: 2,
      },
      marketingBrief: {
        resourceKind: "marketing_brief",
        resourceVersionId: "brief-1",
        versionNumber: 3,
      },
      xiaohongshuBrief: {
        resourceKind: "xiaohongshu_brief",
        resourceVersionId: "xhs-1",
        versionNumber: 4,
      },
    });

    const mapped = mapTaskOverview(dto);
    expect(mapped).toEqual({
      taskId: "task-1",
      taskName: "Launch",
      productCategory: "Backpack",
      taskStatus: "draft",
      currentStage: null,
      waitingReason: null,
      updatedAt: "2026-08-12T00:00:00Z",
      revision: 0,
      primaryAction: { kind: "none" },
      capabilities: [],
      stages: [],
      activeRunId: "run-active",
      latestRunId: "run-latest",
      needsInputRequest: { resourceId: "input-1", revision: 4 },
      reviewPackage: { reviewPackageId: "review-1", packageVersion: 7 },
      approvedStrategy: {
        resourceKind: "strategy",
        resourceVersionId: "strategy-1",
        versionNumber: 2,
      },
      marketingBrief: {
        resourceKind: "marketing_brief",
        resourceVersionId: "brief-1",
        versionNumber: 3,
      },
      xiaohongshuBrief: {
        resourceKind: "xiaohongshu_brief",
        resourceVersionId: "xhs-1",
        versionNumber: 4,
      },
    });
    expect(Object.keys(mapped.needsInputRequest ?? {}).sort()).toEqual([
      "resourceId",
      "revision",
    ]);
    expect(Object.keys(mapped.reviewPackage ?? {}).sort()).toEqual([
      "packageVersion",
      "reviewPackageId",
    ]);
    for (const reference of [
      mapped.approvedStrategy,
      mapped.marketingBrief,
      mapped.xiaohongshuBrief,
    ]) {
      expect(Object.keys(reference ?? {}).sort()).toEqual([
        "resourceKind",
        "resourceVersionId",
        "versionNumber",
      ]);
    }
    for (const reference of [
      mapped.needsInputRequest,
      mapped.reviewPackage,
      mapped.approvedStrategy,
      mapped.marketingBrief,
      mapped.xiaohongshuBrief,
    ]) {
      expect(reference).not.toBeNull();
      expect(Object.isFrozen(reference)).toBe(true);
    }
    expect(Object.isFrozen(mapped)).toBe(true);
    for (const [mappedReference, dtoReference] of [
      [mapped.needsInputRequest, dto.needsInputRequest],
      [mapped.reviewPackage, dto.reviewPackage],
      [mapped.approvedStrategy, dto.approvedStrategy],
      [mapped.marketingBrief, dto.marketingBrief],
      [mapped.xiaohongshuBrief, dto.xiaohongshuBrief],
    ]) {
      expect(mappedReference).not.toBe(dtoReference);
    }

    const clone = cloneTaskOverview(mapped);
    expect(clone).toEqual(mapped);
    expect(clone).not.toBe(mapped);
    for (const [cloned, original] of [
      [clone.needsInputRequest, mapped.needsInputRequest],
      [clone.reviewPackage, mapped.reviewPackage],
      [clone.approvedStrategy, mapped.approvedStrategy],
      [clone.marketingBrief, mapped.marketingBrief],
      [clone.xiaohongshuBrief, mapped.xiaohongshuBrief],
    ]) {
      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
      expect(Object.isFrozen(cloned)).toBe(true);
    }
  });

  it("uses the generated Task operations and preserves server order/action data", async () => {
    const first = {
      ...generatedOverview({ taskId: "first" }),
      primaryAction: { type: "navigate", target: "intake" },
    };
    const second = {
      ...generatedOverview({ taskId: "second", capabilities: ["start"] }),
      primaryAction: { type: "future_action", command: "start" },
    };
    const fetch = vi.fn(
      async (request: RequestInfo | URL, init?: RequestInit) => {
        const requestObject =
          request instanceof Request ? request : new Request(request, init);
        if (
          requestObject.method === "GET" &&
          requestObject.url.endsWith("/api/v1/tasks?limit=20")
        ) {
          return response({ items: [first, second], limit: 20 });
        }
        if (requestObject.method === "POST")
          return response(generatedOverview(), 201);
        return response(generatedOverview());
      },
    );
    const gateway = createHttpTaskGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    const listed = await gateway.listTasks();
    const created = await gateway.createTask(input, "key-1");
    const read = await gateway.getTaskOverview("task-1");

    expect(listed.map((task) => task.taskId)).toEqual(["first", "second"]);
    expect(listed[0]?.primaryAction).toEqual({
      kind: "navigate",
      target: "intake",
    });
    expect(listed[1]?.primaryAction).toEqual({ kind: "unavailable" });
    expect(created.taskId).toBe("task-1");
    expect(read.taskId).toBe("task-1");
    expect(fetch).toHaveBeenCalledTimes(3);

    const listRequest = fetch.mock.calls[0]?.[0];
    const createRequest = fetch.mock.calls[1]?.[0];
    const overviewRequest = fetch.mock.calls[2]?.[0];
    expect(listRequest).toBeInstanceOf(Request);
    expect(createRequest).toBeInstanceOf(Request);
    expect(overviewRequest).toBeInstanceOf(Request);
    if (!(createRequest instanceof Request))
      throw new Error("expected create Request");
    expect(createRequest.headers.get("Idempotency-Key")).toBe("key-1");
    expect(await createRequest.json()).toEqual(input);
    expect((overviewRequest as Request).url).toBe(
      "https://example.test/api/v1/tasks/task-1",
    );
  });

  it.each([
    [400, "invalid"],
    [409, "invalid"],
    [422, "invalid"],
    [404, "missing"],
    [500, "temporary"],
    [503, "temporary"],
  ] as const)(
    "maps HTTP %s to a safe %s gateway error",
    async (status, kind) => {
      const fetch = vi.fn(async () =>
        response({ detail: "private provider trace" }, status),
      );
      const gateway = createHttpTaskGateway(
        createApiClient({ baseUrl: "https://example.test", fetch }),
      );

      const failure = gateway.getTaskOverview("task-1");
      await expect(failure).rejects.toMatchObject({ kind });
      await expect(failure).rejects.not.toThrow("private provider trace");
    },
  );

  it.each([
    ["null JSON", () => response(null, 200)],
    ["empty body", () => new Response("", { status: 200 })],
    [
      "invalid JSON",
      () =>
        new Response("{invalid", {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
    ],
    ["payload too large", () => response({ detail: "private" }, 413)],
    ["unsupported media type", () => response({ detail: "private" }, 415)],
  ] as const)(
    "maps %s to invalid without leaking response details",
    async (_label, body) => {
      const fetch = vi.fn(async () => body());
      const gateway = createHttpTaskGateway(
        createApiClient({ baseUrl: "https://example.test", fetch }),
      );

      await expect(gateway.getTaskOverview("task-1")).rejects.toMatchObject({
        kind: "invalid",
      });
      await expect(gateway.getTaskOverview("task-1")).rejects.not.toThrow(
        "private",
      );
    },
  );

  it("projects only authored primary-action targets and capabilities", async () => {
    const actions = [
      { type: "navigate", target: "intake" },
      { type: "NavigatePrimaryAction", target: "review" },
      { type: "navigate", target: "" },
      { type: "command", command: "start" },
      { type: "CommandPrimaryAction", command: "submit_review" },
      { type: "command", command: "future_command" },
      { type: "command", command: "" },
    ];
    const fetch = vi.fn(async () =>
      response({
        items: actions.map((primaryAction, index) => ({
          ...generatedOverview({ taskId: `task-${index}` }),
          primaryAction,
        })),
        limit: 20,
      }),
    );
    const gateway = createHttpTaskGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    const result = await gateway.listTasks();
    expect(result.map((task) => task.primaryAction)).toEqual([
      { kind: "navigate", target: "intake" },
      { kind: "navigate", target: "review" },
      { kind: "unavailable" },
      { kind: "command", command: "start" },
      { kind: "command", command: "submit_review" },
      { kind: "unavailable" },
      { kind: "unavailable" },
    ]);
  });

  it("maps a network failure to temporary without exposing the cause", async () => {
    const fetch = vi.fn(async () => {
      throw new Error("private socket details");
    });
    const gateway = createHttpTaskGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );

    await expect(gateway.listTasks()).rejects.toMatchObject({
      kind: "temporary",
    });
    await expect(gateway.listTasks()).rejects.not.toThrow(
      "private socket details",
    );
  });

  it("rejects blank real inputs before generated-client I/O", async () => {
    const fetch = vi.fn(async () => response({ items: [], limit: 20 }));
    const gateway = createHttpTaskGateway(
      createApiClient({ baseUrl: "https://example.test", fetch }),
    );
    const invalidInputs: readonly unknown[] = [
      { taskName: "", productCategory: "Category", promotionGoal: "Goal" },
      { taskName: "Task", productCategory: " ", promotionGoal: "Goal" },
      { taskName: "Task", productCategory: "Category", promotionGoal: 42 },
    ];
    for (const invalid of invalidInputs) {
      await expect(
        gateway.createTask(invalid as TaskInput, "key-1"),
      ).rejects.toMatchObject({
        kind: "invalid",
      });
    }
    await expect(gateway.createTask(input, " ")).rejects.toMatchObject({
      kind: "invalid",
    });
    await expect(gateway.getTaskOverview(" ")).rejects.toMatchObject({
      kind: "invalid",
    });
    expect(fetch).not.toHaveBeenCalled();
  });
});

describe("TaskGateway deterministic contract", () => {
  it("supports empty and seeded reads in stable order with detached results", async () => {
    const first = overview({ taskId: "first", capabilities: ["start"] });
    const second = overview({ taskId: "second", taskName: "Second" });
    const gateway = createDeterministicTaskGateway({ tasks: [first, second] });

    const firstRead = await gateway.listTasks();
    expect(firstRead.map((task) => task.taskId)).toEqual(["first", "second"]);
    expect(firstRead[0]).not.toBe(first);
    expect(firstRead[0]?.capabilities).not.toBe(first.capabilities);
    expect(firstRead[0]?.capabilities).toEqual(["start"]);
    expect(Object.isFrozen(firstRead)).toBe(true);
    expect(Object.isFrozen(firstRead[0])).toBe(true);
    expect(Object.isFrozen(firstRead[0]?.capabilities)).toBe(true);

    const secondRead = await gateway.listTasks();
    expect(secondRead).not.toBe(firstRead);
    expect(secondRead).toEqual(firstRead);
    expect((await gateway.getTaskOverview("second")).taskName).toBe("Second");
    await expect(gateway.getTaskOverview("missing")).rejects.toMatchObject({
      kind: "missing",
    });
  });

  it("detaches and freezes every seeded/read/replayed reference and keeps create defaults exact", async () => {
    const seeded = overview({
      activeRunId: "run-active",
      latestRunId: "run-latest",
      needsInputRequest: { resourceId: "input-1", revision: 2 },
      reviewPackage: { reviewPackageId: "review-1", packageVersion: 3 },
      approvedStrategy: {
        resourceKind: "strategy",
        resourceVersionId: "strategy-1",
        versionNumber: 1,
      },
      marketingBrief: {
        resourceKind: "marketing_brief",
        resourceVersionId: "brief-1",
        versionNumber: 1,
      },
      xiaohongshuBrief: {
        resourceKind: "xiaohongshu_brief",
        resourceVersionId: "xhs-1",
        versionNumber: 1,
      },
    });
    const gateway = createDeterministicTaskGateway({ tasks: [seeded] });
    const read = await gateway.getTaskOverview("task-1");

    expect(read).toEqual(seeded);
    for (const [received, original] of [
      [read.needsInputRequest, seeded.needsInputRequest],
      [read.reviewPackage, seeded.reviewPackage],
      [read.approvedStrategy, seeded.approvedStrategy],
      [read.marketingBrief, seeded.marketingBrief],
      [read.xiaohongshuBrief, seeded.xiaohongshuBrief],
    ]) {
      expect(received).not.toBe(original);
      expect(Object.isFrozen(received)).toBe(true);
    }

    const created = await gateway.createTask(input, "key-created");
    expect({
      activeRunId: created.activeRunId,
      latestRunId: created.latestRunId,
      needsInputRequest: created.needsInputRequest,
      reviewPackage: created.reviewPackage,
      approvedStrategy: created.approvedStrategy,
      marketingBrief: created.marketingBrief,
      xiaohongshuBrief: created.xiaohongshuBrief,
    }).toEqual({
      activeRunId: null,
      latestRunId: null,
      needsInputRequest: null,
      reviewPackage: null,
      approvedStrategy: null,
      marketingBrief: null,
      xiaohongshuBrief: null,
    });

    const createdRead = await gateway.getTaskOverview(created.taskId);
    const replay = await gateway.createTask(input, "key-created");
    expect(createdRead).toEqual(created);
    expect(replay).toEqual(created);
    expect(replay).not.toBe(created);
    expect(createdRead).not.toBe(created);
  });

  it("creates, replays idempotently, and rejects same-key different-input without mutation", async () => {
    const gateway = createDeterministicTaskGateway();
    const original = {
      taskName: "  Launch  ",
      productCategory: " Backpack ",
      promotionGoal: " Awareness ",
    };
    const created = await gateway.createTask(original, "key-1");
    expect(original).toEqual({
      taskName: "  Launch  ",
      productCategory: " Backpack ",
      promotionGoal: " Awareness ",
    });
    expect(created).toMatchObject({
      taskId: "task-1",
      taskName: "Launch",
      productCategory: "Backpack",
      taskStatus: "draft",
    });
    const replay = await gateway.createTask(
      {
        taskName: "Launch",
        productCategory: "Backpack",
        promotionGoal: "Awareness",
      },
      "key-1",
    );
    expect(replay).toEqual(created);
    expect(replay).not.toBe(created);

    const beforeConflict = await gateway.listTasks();
    await expect(
      gateway.createTask(
        {
          taskName: "Other",
          productCategory: "Backpack",
          promotionGoal: "Awareness",
        },
        "key-1",
      ),
    ).rejects.toMatchObject({ kind: "invalid" });
    expect(await gateway.listTasks()).toEqual(beforeConflict);
  });

  it("rejects invalid input and key without mutation", async () => {
    const gateway = createDeterministicTaskGateway();
    await expect(
      gateway.createTask(
        { taskName: "", productCategory: "x", promotionGoal: "y" },
        "key",
      ),
    ).rejects.toBeInstanceOf(TaskGatewayError);
    await expect(gateway.createTask(input, "")).rejects.toMatchObject({
      kind: "invalid",
    });
    expect(await gateway.listTasks()).toEqual([]);
  });

  it("keeps every gateway operation on the private interface", () => {
    const gateway: TaskGateway = createDeterministicTaskGateway();
    expect(Object.keys(gateway).sort()).toEqual([
      "createTask",
      "generateResult",
      "getCurrentResult",
      "getPrimaryInput",
      "getTaskOverview",
      "listTasks",
      "savePrimaryInput",
    ]);
  });
});
