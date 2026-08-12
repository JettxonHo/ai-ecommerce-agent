import { describe, expect, it, vi } from "vitest";
import { createApiClient } from "../../src/api/client";
import {
  TaskGatewayError,
  type TaskGateway,
  type TaskInput,
  type TaskOverview,
} from "../../src/tasks/gateway";
import { createDeterministicTaskGateway } from "../../src/tasks/deterministicGateway";
import { createHttpTaskGateway } from "../../src/tasks/httpGateway";

const overview = (overrides: Record<string, unknown> = {}): TaskOverview =>
  ({
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
    activeRun: null,
    latestRun: null,
    needsInputRequest: null,
    reviewPackage: null,
    approvedStrategy: null,
    marketingBrief: null,
    xiaohongshuBrief: null,
    ...overrides,
  }) as TaskOverview;

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
  it("uses the generated Task operations and preserves server order/action data", async () => {
    const first = {
      ...overview({
        taskId: "first",
        primaryAction: { type: "navigate", target: "intake" },
      }),
    };
    const second = {
      ...overview({
        taskId: "second",
        primaryAction: { type: "future_action", command: "start" },
        capabilities: ["start"],
      }),
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
        if (requestObject.method === "POST") return response(overview(), 201);
        return response(overview());
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
      "getTaskOverview",
      "listTasks",
    ]);
  });
});
