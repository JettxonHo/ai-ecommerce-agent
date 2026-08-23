import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router";
import { describe, expect, it, vi } from "vitest";
import App from "../App";
import { createDeterministicTaskGateway } from "./deterministicGateway";
import { TaskRoutes } from "./TaskRoutes";
import {
  TaskGatewayError,
  type TaskGateway,
  type TaskPrimaryInput,
  type TaskOverview,
} from "./gateway";
import type {
  NeedsInputActionRequest,
  NeedsInputGateway,
} from "../needsInput/gateway";
import { NeedsInputGatewayError } from "../needsInput/gateway";

const overviewBaseline: TaskOverview = {
  taskId: "task-1",
  taskName: "Launch",
  productCategory: "Backpack",
  taskStatus: "running",
  currentStage: "product_positioning",
  waitingReason: null,
  updatedAt: "2026-08-12T00:00:00Z",
  revision: 2,
  primaryAction: { kind: "none" },
  capabilities: [],
  stages: [
    {
      stage: "product_intake_and_fact_extraction",
      status: "valid",
      waitingReason: "Source accepted",
      updatedAt: "2026-08-11T00:00:00Z",
    },
    {
      stage: "product_positioning",
      status: "running",
      waitingReason: null,
      updatedAt: "2026-08-12T00:00:00Z",
    },
  ],
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
const savedPrimaryInput: TaskPrimaryInput = {
  taskId: "task-1",
  inputRevision: 0,
  inputKind: "pasted_text",
  fileName: null,
  content: "Saved context",
  byteCount: 13,
  updatedAt: "2026-08-12T00:00:00Z",
};

const renderRoutes = (
  path = "/tasks",
  gateway = createDeterministicTaskGateway(),
) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <MemoryRouter initialEntries={[path]}>
      <QueryClientProvider client={queryClient}>
        <App taskGateway={gateway} />
      </QueryClientProvider>
    </MemoryRouter>,
  );
};

const gatewayFor = (
  tasks: readonly TaskOverview[],
  listTasks: TaskGateway["listTasks"] = async () => tasks,
  getTaskOverview: TaskGateway["getTaskOverview"] = async (taskId) => {
    const task = tasks.find((candidate) => candidate.taskId === taskId);
    if (!task) throw new TaskGatewayError("missing", "Task not found.");
    return task;
  },
): TaskGateway => ({
  listTasks,
  getTaskOverview,
  createTask: vi.fn(),
  getPrimaryInput: async () => {
    throw new TaskGatewayError("missing", "Primary input not found.");
  },
  savePrimaryInput: async () => {
    throw new TaskGatewayError("invalid", "Primary input is unavailable.");
  },
  generateResult: vi.fn(),
  getCurrentResult: vi.fn(),
});

describe("TaskRoutes", () => {
  it("conditionally reads the authoritative Needs Input request and exposes the bounded workspace", async () => {
    const request: NeedsInputActionRequest = {
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
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const getNeedsInputActionRequest = vi.fn(async () => request);
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest,
      resolveNeedsInput: vi.fn(),
    };
    const taskGateway = gatewayFor([
      overview({
        taskId: "task-1",
        taskStatus: "waiting_for_input",
        currentStage: "product_intake_and_fact_extraction",
        needsInputRequest: { resourceId: "action-1", revision: 2 },
        primaryAction: { kind: "navigate", target: "needs_input" },
      }),
    ]);

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByRole("heading", { name: "Launch" })).toBeTruthy();
    expect(screen.getByText("Backpack")).toBeTruthy();
    expect(
      await screen.findByRole("heading", { name: "需要补充信息" }),
    ).toBeTruthy();
    expect(getNeedsInputActionRequest).toHaveBeenCalledWith("action-1");
  });

  it("preserves a selected value and offers a manual retry with the same idempotency key after a temporary resolve failure", async () => {
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-retry",
      taskId: "task-1",
      revision: 2,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在两个候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const resolvedRequest: NeedsInputActionRequest = {
      ...request,
      revision: request.revision + 1,
      status: "resolved",
      allowedResolutionTypes: [],
    };
    const resolveNeedsInput = vi
      .fn<NeedsInputGateway["resolveNeedsInput"]>()
      .mockRejectedValueOnce(
        new NeedsInputGatewayError("temporary", "temporary"),
      )
      .mockResolvedValue({
        actionRequest: resolvedRequest,
        task: { taskId: request.taskId },
      });
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest: vi.fn(async () => request),
      resolveNeedsInput,
    };
    const taskGateway = gatewayFor([
      overview({
        taskStatus: "waiting_for_input",
        currentStage: "product_intake_and_fact_extraction",
        needsInputRequest: {
          resourceId: request.actionRequestId,
          revision: request.revision,
        },
        primaryAction: { kind: "navigate", target: "needs_input" },
      }),
    ]);

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    const radio = within(panel).getByRole("radio", {
      name: /CBP-SYN-001/u,
    });
    await user.click(radio);
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(1));
    expect((radio as HTMLInputElement).checked).toBe(true);
    expect(
      within(panel).getByText("补充请求暂时未提交，请手动重试。"),
    ).toBeTruthy();
    expect(
      within(panel).getByRole("button", { name: "重试提交" }),
    ).toBeTruthy();

    await user.click(within(panel).getByRole("button", { name: "重试提交" }));
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(2));
    const firstKey = resolveNeedsInput.mock.calls[0]?.[3];
    const secondKey = resolveNeedsInput.mock.calls[1]?.[3];
    expect(secondKey).toBe(firstKey);
  });

  it("blocks a stale authority response and offers an explicit Task refresh instead of replay", async () => {
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-stale",
      taskId: "task-1",
      revision: 2,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在两个候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const resolveNeedsInput = vi.fn(async (): Promise<never> => {
      throw new NeedsInputGatewayError("stale", "stale");
    });
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest: vi.fn(async () => request),
      resolveNeedsInput,
    };
    const taskGateway = gatewayFor([
      overview({
        taskStatus: "waiting_for_input",
        currentStage: "product_intake_and_fact_extraction",
        needsInputRequest: {
          resourceId: request.actionRequestId,
          revision: request.revision,
        },
        primaryAction: { kind: "navigate", target: "needs_input" },
      }),
    ]);

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    await user.click(
      within(panel).getByRole("radio", { name: /CBP-SYN-001/u }),
    );
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(1));
    expect(
      within(panel).getByText("补充请求已变化，请刷新任务事实后再提交。"),
    ).toBeTruthy();
    expect(
      within(panel).queryByRole("button", { name: "重试提交" }),
    ).toBeNull();
    expect(
      within(panel).getByRole("button", { name: "刷新任务事实" }),
    ).toBeTruthy();
  });

  it("blocks a fetched request whose identity or revision disagrees with the Task Overview", async () => {
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-mismatch",
      taskId: "task-1",
      revision: 3,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在两个候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const matchingRequest = { ...request, revision: 2 };
    let reads = 0;
    const getNeedsInputActionRequest = vi.fn(async () => {
      reads += 1;
      return reads === 1 ? request : matchingRequest;
    });
    const resolveNeedsInput = vi.fn();
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest,
      resolveNeedsInput,
    };
    const task = overview({
      taskStatus: "waiting_for_input",
      currentStage: "product_intake_and_fact_extraction",
      needsInputRequest: {
        resourceId: request.actionRequestId,
        revision: 2,
      },
      primaryAction: { kind: "navigate", target: "needs_input" },
    });
    const getTaskOverview = vi.fn(async () => task);
    const taskGateway = gatewayFor([task], undefined, getTaskOverview);

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    expect(getNeedsInputActionRequest).toHaveBeenCalledWith(
      request.actionRequestId,
    );
    expect(within(panel).getByText("需刷新事实")).toBeTruthy();
    expect(
      within(panel).getByRole("button", { name: "刷新任务事实" }),
    ).toBeTruthy();
    const submit = within(panel).getByRole("button", {
      name: "确认采用此值",
    });
    expect((submit as HTMLButtonElement).disabled).toBe(true);
    expect(resolveNeedsInput).not.toHaveBeenCalled();

    await user.click(
      within(panel).getByRole("button", { name: "刷新任务事实" }),
    );
    await waitFor(() => expect(getTaskOverview).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect(getNeedsInputActionRequest).toHaveBeenCalledTimes(2),
    );
    const refreshedRadio = within(panel).getAllByRole("radio")[0];
    expect((refreshedRadio as HTMLInputElement).disabled).toBe(false);
    await user.click(refreshedRadio);
    const refreshedSubmit = within(panel).getByRole("button", {
      name: "确认采用此值",
    });
    expect((refreshedSubmit as HTMLButtonElement).disabled).toBe(false);
    expect(resolveNeedsInput).not.toHaveBeenCalled();
  });

  it("reuses a failed input key only for the same resolution and rotates it when the selection changes", async () => {
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-rotate",
      taskId: "task-1",
      revision: 2,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在两个候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const resolveNeedsInput = vi
      .fn<NeedsInputGateway["resolveNeedsInput"]>()
      .mockRejectedValue(new NeedsInputGatewayError("temporary", "temporary"));
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest: vi.fn(async () => request),
      resolveNeedsInput,
    };
    const taskGateway = gatewayFor([
      overview({
        taskStatus: "waiting_for_input",
        currentStage: "product_intake_and_fact_extraction",
        needsInputRequest: {
          resourceId: request.actionRequestId,
          revision: request.revision,
        },
        primaryAction: { kind: "navigate", target: "needs_input" },
      }),
    ]);

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    await user.click(
      within(panel).getByRole("radio", { name: /CBP-SYN-001/u }),
    );
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(1));
    const firstKey = resolveNeedsInput.mock.calls[0]?.[3];
    await user.click(within(panel).getByRole("button", { name: "重试提交" }));
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(2));
    const retryKey = resolveNeedsInput.mock.calls[1]?.[3];
    expect(retryKey).toBe(firstKey);

    await user.click(
      within(panel).getByRole("radio", { name: /CBP-SYN-002/u }),
    );
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(3));
    const rotatedKey = resolveNeedsInput.mock.calls[2]?.[3];
    expect(rotatedKey).not.toBe(firstKey);
  });

  it("keeps the Needs Input idempotency key opaque and bounded for long canonical values", async () => {
    const selectedValue = `selected-${"x".repeat(256)}`;
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-opaque-key",
      taskId: "task-1",
      revision: 2,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在一个很长的候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: [JSON.stringify(selectedValue)],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const resolveNeedsInput = vi
      .fn<NeedsInputGateway["resolveNeedsInput"]>()
      .mockRejectedValue(new NeedsInputGatewayError("temporary", "temporary"));
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest: vi.fn(async () => request),
      resolveNeedsInput,
    };
    const taskGateway = gatewayFor([
      overview({
        taskStatus: "waiting_for_input",
        currentStage: "product_intake_and_fact_extraction",
        needsInputRequest: {
          resourceId: request.actionRequestId,
          revision: request.revision,
        },
        primaryAction: { kind: "navigate", target: "needs_input" },
      }),
    ]);

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    await user.click(within(panel).getByRole("radio"));
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(1));

    const key = resolveNeedsInput.mock.calls[0]?.[3] ?? "";
    expect(key.length).toBeLessThanOrEqual(200);
    expect(key).not.toContain(selectedValue);
  });

  it("rotates the failed-input key when the authoritative request revision changes", async () => {
    let revision = 2;
    const requestFor = (value: number): NeedsInputActionRequest => ({
      actionRequestId: "action-revision",
      taskId: "task-1",
      revision: value,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在两个候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    });
    const taskFor = (value: number): TaskOverview =>
      overview({
        taskStatus: "waiting_for_input",
        currentStage: "product_intake_and_fact_extraction",
        revision: value,
        needsInputRequest: {
          resourceId: "action-revision",
          revision: value,
        },
        primaryAction: { kind: "navigate", target: "needs_input" },
      });
    const getTaskOverview = vi.fn(async () => taskFor(revision));
    const getNeedsInputActionRequest = vi.fn(async () => requestFor(revision));
    const resolveNeedsInput = vi
      .fn<NeedsInputGateway["resolveNeedsInput"]>()
      .mockRejectedValue(new NeedsInputGatewayError("temporary", "temporary"));
    const taskGateway = gatewayFor(
      [taskFor(revision)],
      undefined,
      getTaskOverview,
    );
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest,
      resolveNeedsInput,
    };
    const queryClient = new QueryClient();

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={queryClient}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    await user.click(
      within(panel).getByRole("radio", { name: /CBP-SYN-001/u }),
    );
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(1));
    const firstKey = resolveNeedsInput.mock.calls[0]?.[3];

    revision = 3;
    await queryClient.invalidateQueries({
      queryKey: ["tasks", "overview", "task-1"],
    });
    await waitFor(() =>
      expect(getNeedsInputActionRequest).toHaveBeenLastCalledWith(
        "action-revision",
      ),
    );
    const refreshedPanel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    await user.click(
      within(refreshedPanel).getByRole("radio", { name: /CBP-SYN-001/u }),
    );
    await user.click(
      within(refreshedPanel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(2));
    const rotatedKey = resolveNeedsInput.mock.calls[1]?.[3];
    expect(rotatedKey).not.toBe(firstKey);
  });

  it("announces successful resolution after the authoritative overview refetch", async () => {
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-success",
      taskId: "task-1",
      revision: 2,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在两个候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const initialTask = overview({
      taskStatus: "waiting_for_input",
      currentStage: "product_intake_and_fact_extraction",
      needsInputRequest: {
        resourceId: request.actionRequestId,
        revision: request.revision,
      },
      primaryAction: { kind: "navigate", target: "needs_input" },
    });
    const refreshedTask = overview({
      taskStatus: "running",
      currentStage: "product_intake_and_fact_extraction",
      activeRunId: "run-1",
      needsInputRequest: null,
      primaryAction: { kind: "none" },
    });
    let resolved = false;
    const getTaskOverview = vi.fn(async () =>
      resolved ? refreshedTask : initialTask,
    );
    const resolveNeedsInput = vi.fn(async () => {
      resolved = true;
      return {
        actionRequest: {
          ...request,
          revision: request.revision + 1,
          status: "resolved" as const,
          allowedResolutionTypes: [],
        },
        task: { taskId: request.taskId },
      };
    });
    const taskGateway = gatewayFor([initialTask], undefined, getTaskOverview);
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest: vi.fn(async () => request),
      resolveNeedsInput,
    };

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    await user.click(
      within(panel).getByRole("radio", { name: /CBP-SYN-001/u }),
    );
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(1));
    await waitFor(() =>
      expect(getTaskOverview.mock.calls.length).toBeGreaterThan(1),
    );
    expect(screen.getByText("补充请求已处理，任务事实已刷新。")).toBeTruthy();
  });

  it("does not claim refreshed authority when resolution succeeds but Task refresh fails", async () => {
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-refresh-failure",
      taskId: "task-1",
      revision: 2,
      status: "open",
      reasonType: "identity_conflict",
      reasonSummary: "商品身份存在两个候选值。",
      affectedStages: ["product_intake_and_fact_extraction"],
      sourceReferences: [],
      conflictValues: [
        {
          fieldPath: "product.sku",
          values: ['"CBP-SYN-001"', '"CBP-SYN-002"'],
        },
      ],
      allowedResolutionTypes: ["choose_existing_value"],
      expectedRecovery: "resume",
      supersededBy: null,
    };
    const initialTask = overview({
      taskStatus: "waiting_for_input",
      currentStage: "product_intake_and_fact_extraction",
      needsInputRequest: {
        resourceId: request.actionRequestId,
        revision: request.revision,
      },
      primaryAction: { kind: "navigate", target: "needs_input" },
    });
    const getTaskOverview = vi
      .fn<TaskGateway["getTaskOverview"]>()
      .mockResolvedValueOnce(initialTask)
      .mockRejectedValue(new TaskGatewayError("temporary", "temporary"));
    const resolveNeedsInput = vi.fn(async () => ({
      actionRequest: {
        ...request,
        revision: request.revision + 1,
        status: "resolved" as const,
        allowedResolutionTypes: [],
      },
      task: { taskId: request.taskId },
    }));
    const taskGateway = gatewayFor([initialTask], undefined, getTaskOverview);
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest: vi.fn(async () => request),
      resolveNeedsInput,
    };

    render(
      <MemoryRouter initialEntries={["/tasks/task-1"]}>
        <QueryClientProvider client={new QueryClient()}>
          <Routes>
            <Route
              path="/tasks/:taskId"
              element={
                <TaskRoutes
                  taskGateway={taskGateway}
                  needsInputGateway={needsInputGateway}
                />
              }
            />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>,
    );

    const panel = await screen.findByRole("region", {
      name: "需要补充信息",
    });
    const user = userEvent.setup();
    await user.click(
      within(panel).getByRole("radio", { name: /CBP-SYN-001/u }),
    );
    await user.click(
      within(panel).getByRole("button", { name: "确认采用此值" }),
    );
    await waitFor(() => expect(resolveNeedsInput).toHaveBeenCalledTimes(1));
    await waitFor(() =>
      expect(getTaskOverview.mock.calls.length).toBeGreaterThan(1),
    );

    expect(screen.queryByText("补充请求已处理，任务事实已刷新。")).toBeNull();
    expect(screen.getByText("需刷新事实")).toBeTruthy();
    expect(screen.getByRole("button", { name: "刷新任务事实" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "重试提交" })).toBeNull();
    expect(resolveNeedsInput).toHaveBeenCalledTimes(1);
  });

  it("presents a Chinese Action Home with one deterministic priority resume item", async () => {
    const needsInput = overview({
      taskId: "needs-input",
      taskName: "补资料任务",
      productCategory: "城市通勤包",
      taskStatus: "waiting_for_input",
      currentStage: null,
      waitingReason: "需要补充商品资料",
      primaryAction: { kind: "navigate", target: "needs_input" },
      updatedAt: "2026-08-09T00:00:00Z",
    });
    const review = overview({
      taskId: "review",
      taskName: "待审核任务",
      productCategory: "旅行包",
      taskStatus: "waiting_for_review",
      currentStage: "human_review",
      primaryAction: { kind: "navigate", target: "review" },
      updatedAt: "2026-08-12T00:00:00Z",
    });
    const failed = overview({
      taskId: "failed",
      taskName: "可恢复任务",
      productCategory: "配件",
      taskStatus: "failed",
      currentStage: null,
      primaryAction: { kind: "navigate", target: "recovery" },
      updatedAt: "2026-08-13T00:00:00Z",
    });

    renderRoutes("/tasks", gatewayFor([failed, review, needsInput]));

    expect(
      await screen.findByRole("heading", { name: "行动首页" }),
    ).toBeTruthy();
    expect(
      screen
        .getByRole("link", { name: "新建商品上新任务" })
        .getAttribute("href"),
    ).toBe("/tasks/new");

    const resume = await screen.findByRole("region", { name: "继续处理" });
    expect(
      within(resume).getByRole("link", { name: "补资料任务" }),
    ).toBeTruthy();
    expect(within(resume).getAllByRole("link")).toHaveLength(1);
    const resumeTime = resume.querySelector("time");
    expect(resumeTime).not.toBeNull();
    expect(resumeTime?.getAttribute("dateTime")).toBe("2026-08-09T00:00:00Z");
    expect(resumeTime?.textContent).toContain("2026年8月9日 00:00");

    const recent = screen.getByRole("region", { name: "最近任务" });
    expect(within(recent).getAllByRole("article")).toHaveLength(3);
  });

  it("renders the normal empty recent-task state", async () => {
    renderRoutes();

    expect(
      await screen.findByRole("heading", { name: "行动首页" }),
    ).toBeTruthy();
    expect(await screen.findByText("还没有商品上新任务。")).toBeTruthy();
  });

  it("loads a stable deep-link overview and preserves stage order", async () => {
    const task = overview({ taskId: "task/7" });
    renderRoutes(
      "/tasks/task%2F7",
      createDeterministicTaskGateway({ tasks: [task] }),
    );

    expect(await screen.findByRole("heading", { name: "Launch" })).toBeTruthy();
    const overviewRegion = screen.getByRole("region", {
      name: "Launch",
    });
    expect(within(overviewRegion).getByText("Task ID: task/7")).toBeTruthy();
    expect(within(overviewRegion).getByText("Backpack")).toBeTruthy();
    const context = screen.getByRole("complementary", {
      name: "上下文与执行信息",
    });
    const taskDetails = context.querySelector("dl");
    expect(taskDetails).not.toBeNull();
    expect(within(taskDetails!).getByText("处理中")).toBeTruthy();
    expect(within(taskDetails!).getByText("商品定位")).toBeTruthy();
    expect(within(taskDetails!).getByText("2026年8月12日 00:00")).toBeTruthy();
    const stages = within(
      screen.getByRole("list", { name: "Stage summaries" }),
    ).getAllByRole("listitem");
    expect(stages).toHaveLength(2);
    expect(within(stages[0]!).getByText("资料整理")).toBeTruthy();
    expect(within(stages[0]!).getByText("已完成")).toBeTruthy();
    expect(within(stages[0]!).getByText("Source accepted")).toBeTruthy();
    expect(within(stages[0]!).getByText("2026年8月11日 00:00")).toBeTruthy();
    expect(within(stages[1]!).getByText("商品定位")).toBeTruthy();
    expect(within(stages[1]!).getByText("处理中")).toBeTruthy();
    expect(within(stages[1]!).getByText("2026年8月12日 00:00")).toBeTruthy();
    expect(
      screen.getByRole("link", { name: "返回最近任务" }).getAttribute("href"),
    ).toBe("/tasks");
  });

  it("exposes an accessible loading state while listing recent tasks", () => {
    const listTasks = () => new Promise<readonly TaskOverview[]>(() => {});
    renderRoutes("/tasks", gatewayFor([], listTasks));

    expect(screen.getByRole("status").textContent).toContain(
      "正在读取最近任务…",
    );
  });

  it("exposes an accessible loading state while reading a Task overview", () => {
    const getTaskOverview = () => new Promise<TaskOverview>(() => {});
    renderRoutes(
      "/tasks/task-1",
      gatewayFor([], async () => [], getTaskOverview),
    );

    expect(screen.getByRole("status").textContent).toContain(
      "Loading task overview…",
    );
  });

  it("offers an explicit retry for temporary list failures", async () => {
    const task = overview({ taskId: "retry-task", taskName: "Retry launch" });
    let attempts = 0;
    const listTasks = vi.fn(async () => {
      attempts += 1;
      if (attempts === 1) {
        throw new TaskGatewayError("temporary", "private failure");
      }
      return [task];
    });
    renderRoutes("/tasks", gatewayFor([], listTasks));

    expect(await screen.findByRole("alert")).toBeTruthy();
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "重试读取任务" }));
    expect(
      await within(screen.getByRole("region", { name: "最近任务" })).findByRole(
        "link",
        { name: "Retry launch" },
      ),
    ).toBeTruthy();
    expect(attempts).toBe(2);
  });

  it("keeps server order, renders the bounded summary, and encodes task links", async () => {
    const first = overview({
      taskId: "task/first id",
      taskName: "First <script>alert(1)</script>",
      productCategory: "Outdoor packs",
      taskStatus: "waiting_for_input",
      currentStage: null,
      waitingReason: "Needs a source",
      updatedAt: "2026-08-10T00:00:00Z",
      primaryAction: { kind: "navigate", target: "needs_input" },
    });
    const second = overview({
      taskId: "second",
      taskName: "Second",
      productCategory: "Travel bags",
      currentStage: "customer_insight_analysis",
      taskStatus: "waiting_for_review",
      updatedAt: "2026-08-11T00:00:00Z",
      primaryAction: { kind: "command", command: "start" },
    });
    const third = overview({
      taskId: "third",
      taskName: "Third",
      productCategory: "Accessories",
      currentStage: null,
      waitingReason: null,
      taskStatus: "completed",
      updatedAt: "2026-08-12T00:00:00Z",
      primaryAction: { kind: "unavailable" },
    });
    const createTask = vi.fn();
    const gateway = gatewayFor([first, second, third]);
    gateway.createTask = createTask;
    renderRoutes("/tasks", gateway);

    expect(screen.getByRole("link", { name: "新建商品上新任务" })).toBeTruthy();
    await screen.findByRole("heading", { name: "最近任务" });
    const recent = screen.getByRole("region", { name: "最近任务" });
    await within(recent).findByRole("link", { name: first.taskName });
    const taskLinks = within(recent)
      .getAllByRole("link")
      .filter((link) => link.getAttribute("href")?.startsWith("/tasks/"));
    expect(
      screen.getByRole("link", { name: "跳到主要内容" }).getAttribute("href"),
    ).toBe("#main-content");
    expect(taskLinks.map((link) => link.textContent)).toEqual([
      first.taskName,
      second.taskName,
      third.taskName,
    ]);
    expect(taskLinks[0]?.getAttribute("href")).toBe("/tasks/task%2Ffirst%20id");
    const cards = within(recent).getAllByRole("article");
    expect(cards).toHaveLength(3);
    expect(within(cards[0]!).getByText("Outdoor packs")).toBeTruthy();
    expect(within(cards[0]!).getByText("Needs a source")).toBeTruthy();
    expect(within(cards[0]!).getByText("2026年8月10日 00:00")).toBeTruthy();
    expect(within(cards[0]!).getByText("补充资料")).toBeTruthy();
    expect(within(cards[1]!).getByText("Travel bags")).toBeTruthy();
    expect(within(cards[1]!).getByText("待审核")).toBeTruthy();
    expect(within(cards[1]!).getByText("2026年8月11日 00:00")).toBeTruthy();
    expect(within(cards[1]!).getByText("开始处理")).toBeTruthy();
    expect(within(cards[2]!).getByText("Accessories")).toBeTruthy();
    expect(within(cards[2]!).getByText("已完成")).toBeTruthy();
    expect(within(cards[2]!).getByText("2026年8月12日 00:00")).toBeTruthy();
    expect(within(cards[2]!).getByText("下一步暂不可用")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "start" })).toBeNull();
    expect(screen.queryByRole("button", { name: /next action/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /新建/i })).toBeNull();
    expect(createTask).not.toHaveBeenCalled();
    expect(within(recent).getAllByText(first.taskName)).toHaveLength(1);
    expect(document.querySelector("script")).toBeNull();
  });

  it("distinguishes a missing overview from a temporary error", async () => {
    const missingGateway = gatewayFor(
      [],
      async () => [],
      async () => {
        throw new TaskGatewayError("missing", "Task not found.");
      },
    );
    renderRoutes("/tasks/missing", missingGateway);
    expect(
      await screen.findByRole("heading", { name: "Task not found" }),
    ).toBeTruthy();
    expect(
      screen.getByRole("link", { name: "Back to recent tasks" }),
    ).toBeTruthy();
    expect(screen.getByRole("alert").textContent).toContain(
      "This task is not available in the fixed workspace.",
    );
    expect(screen.queryByRole("button", { name: "Retry" })).toBeNull();
  });

  it("shows a waiting reason when an overview has no current stage", async () => {
    const task = overview({
      currentStage: null,
      waitingReason: "Needs a source",
      taskStatus: "waiting_for_input",
    });
    renderRoutes(
      "/tasks/task-1",
      createDeterministicTaskGateway({ tasks: [task] }),
    );

    const region = await screen.findByRole("region", {
      name: "Launch",
    });
    expect(within(region).getByText("Needs a source")).toBeTruthy();
    expect(within(region).queryByText("Not started")).toBeNull();
    expect(
      within(
        screen.getByRole("complementary", { name: "上下文与执行信息" }),
      ).getByText("待补充资料"),
    ).toBeTruthy();
  });

  it("offers overview retry and then renders the URL-selected task", async () => {
    const task = overview({ taskId: "retry/7", taskName: "Recovered task" });
    let attempts = 0;
    const getTaskOverview = vi.fn(async () => {
      attempts += 1;
      if (attempts === 1) {
        throw new TaskGatewayError("temporary", "private failure");
      }
      return task;
    });
    renderRoutes(
      "/tasks/retry%2F7",
      gatewayFor([], async () => [], getTaskOverview),
    );

    expect(
      await screen.findByRole("heading", { name: "Task overview unavailable" }),
    ).toBeTruthy();
    expect(screen.getByRole("alert").textContent).toContain(
      "The task overview is temporarily unavailable.",
    );
    expect(
      screen
        .getByRole("link", { name: "Back to recent tasks" })
        .getAttribute("href"),
    ).toBe("/tasks");
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "Retry" }));
    expect(
      await screen.findByRole("heading", { name: "Recovered task" }),
    ).toBeTruthy();
    expect(screen.getByText("Task ID: retry/7")).toBeTruthy();
    expect(attempts).toBe(2);
  });

  it("opens an empty editor only when the gateway reports missing input", async () => {
    const task = overview({ taskId: "task-1" });
    const gateway = gatewayFor([task]);
    gateway.getPrimaryInput = vi.fn(async () => {
      throw new TaskGatewayError("missing", "Task not found.");
    });
    gateway.savePrimaryInput = vi.fn(async () => savedPrimaryInput);

    renderRoutes("/tasks/task-1", gateway);

    expect(
      await screen.findByRole("heading", { name: "商品资料" }),
    ).toBeTruthy();
    expect(
      screen
        .getByRole("textbox", { name: "粘贴文本" })
        .hasAttribute("disabled"),
    ).toBe(false);
    expect(
      screen
        .getByRole("button", { name: "保存商品资料" })
        .hasAttribute("disabled"),
    ).toBe(false);
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("blocks malformed primary-input reads until retry returns valid data", async () => {
    const task = overview({ taskId: "task-1" });
    const gateway = gatewayFor([task]);
    let attempts = 0;
    gateway.getPrimaryInput = vi.fn(async () => {
      attempts += 1;
      if (attempts === 1) {
        throw new TaskGatewayError(
          "invalid",
          "The primary input response is invalid.",
        );
      }
      return savedPrimaryInput;
    });
    const savePrimaryInput = vi.fn(async () => savedPrimaryInput);
    gateway.savePrimaryInput = savePrimaryInput;

    renderRoutes("/tasks/task-1", gateway);

    expect(await screen.findByRole("heading", { name: "Launch" })).toBeTruthy();
    expect(
      await screen.findByText("Saved input is unavailable. Retry to continue."),
    ).toBeTruthy();
    expect(
      screen.getByRole("button", { name: "重试读取商品资料" }),
    ).toBeTruthy();
    expect(screen.queryByRole("textbox", { name: "粘贴文本" })).toBeNull();
    expect(screen.queryByRole("button", { name: "保存商品资料" })).toBeNull();
    expect(savePrimaryInput).not.toHaveBeenCalled();

    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "重试读取商品资料" }));
    const content = await screen.findByRole("textbox", { name: "粘贴文本" });
    expect(content.hasAttribute("disabled")).toBe(false);
    const save = screen.getByRole("button", { name: "保存商品资料" });
    expect(save.hasAttribute("disabled")).toBe(false);
    await userEvent.setup().click(save);
    expect(savePrimaryInput).toHaveBeenCalledWith("task-1", {
      inputKind: "pasted_text",
      fileName: null,
      content: "Saved context",
    });
    expect(attempts).toBe(3);
  });

  it("generates persisted result candidates from intake and keeps the retry key stable", async () => {
    const task = overview({ taskId: "task-1" });
    const gateway = createDeterministicTaskGateway({ tasks: [task] });
    await gateway.savePrimaryInput("task-1", {
      inputKind: "pasted_text",
      fileName: null,
      content:
        "anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包，约 18 升，可放入 14 英寸设备。",
    });
    const generateResult = vi.spyOn(gateway, "generateResult");

    renderRoutes(
      "/tasks/task-1?panel=intake&stage=product_positioning",
      gateway,
    );

    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "生成结果" }));
    expect(
      await screen.findByRole("heading", { name: "结果已就绪" }),
    ).toBeTruthy();
    expect(screen.getByText("待审核")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "营销 Brief" })).toBeTruthy();
    expect(generateResult).toHaveBeenCalledTimes(1);

    await userEvent
      .setup()
      .click(screen.getByRole("link", { name: "资料输入" }));
    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "保存商品资料" }));
    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "生成结果" }));
    expect(generateResult).toHaveBeenCalledTimes(2);
    expect(generateResult.mock.calls[0]?.[1]).toBe(
      generateResult.mock.calls[1]?.[1],
    );
    expect(generateResult.mock.calls[0]?.[2]).toBe(0);

    await userEvent
      .setup()
      .click(screen.getByRole("link", { name: "资料输入" }));
    await userEvent
      .setup()
      .clear(await screen.findByRole("textbox", { name: "粘贴文本" }));
    await userEvent
      .setup()
      .type(
        screen.getByRole("textbox", { name: "粘贴文本" }),
        "anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包，约 18 升，可放入 14 英寸设备。changed",
      );
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "保存商品资料" }));
    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "生成结果" }));
    expect(generateResult).toHaveBeenCalledTimes(3);
    expect(generateResult.mock.calls[2]?.[1]).not.toBe(
      generateResult.mock.calls[0]?.[1],
    );
    expect(generateResult.mock.calls[2]?.[2]).toBe(1);
  });

  it("navigates to Results and hands focus to its heading after confirmation succeeds", async () => {
    const task = overview({
      taskId: "task-1",
      taskStatus: "waiting_for_review",
      currentStage: "human_review",
      reviewPackage: { reviewPackageId: "review-1", packageVersion: 1 },
    });
    const gateway = createDeterministicTaskGateway({ tasks: [task] });
    await gateway.savePrimaryInput("task-1", {
      inputKind: "pasted_text",
      fileName: null,
      content:
        "anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包，约 18 升，可放入 14 英寸设备。",
    });
    await gateway.generateResult("task-1", "result-key", 0);

    renderRoutes(
      "/tasks/task-1?filter=mine&panel=review&stage=human_review",
      gateway,
    );

    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "确认并生成结果" }));

    const resultsHeading = await screen.findByRole("heading", {
      name: "结果已就绪",
    });
    expect(
      screen
        .getByRole("link", { name: /^结果$/u })
        .getAttribute("aria-current"),
    ).toBe("page");
    expect(
      screen.getByRole("link", { name: /^结果$/u }).getAttribute("href"),
    ).toBe("/tasks/task-1?filter=mine&panel=results&stage=human_review");
    expect(document.activeElement).toBe(resultsHeading);
  });

  it("keeps Review in place with a safe status when confirmation fails", async () => {
    const task = overview({
      taskId: "task-1",
      taskStatus: "waiting_for_review",
      currentStage: "human_review",
      reviewPackage: { reviewPackageId: "review-1", packageVersion: 1 },
    });
    const gateway = createDeterministicTaskGateway({ tasks: [task] });
    await gateway.savePrimaryInput("task-1", {
      inputKind: "pasted_text",
      fileName: null,
      content:
        "anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包，约 18 升，可放入 14 英寸设备。",
    });
    await gateway.generateResult("task-1", "result-key", 0);
    gateway.confirmCurrentResult = vi.fn(async () => {
      throw new TaskGatewayError("temporary", "confirmation unavailable");
    });

    renderRoutes(
      "/tasks/task-1?filter=mine&panel=review&stage=human_review",
      gateway,
    );

    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "确认并生成结果" }));

    expect(
      await screen.findByRole("heading", { name: "审核候选结果" }),
    ).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "结果已就绪" })).toBeNull();
    expect(
      screen
        .getByRole("link", { name: /^Review$/u })
        .getAttribute("aria-current"),
    ).toBe("page");
    expect(screen.getByText("确认失败，请重试。").textContent).toBe(
      "确认失败，请重试。",
    );
  });

  it("renders an insufficient-input result without candidate panels", async () => {
    const task = overview({ taskId: "task-1" });
    const gateway = createDeterministicTaskGateway({ tasks: [task] });
    await gateway.savePrimaryInput("task-1", {
      inputKind: "pasted_text",
      fileName: null,
      content: "A generic backpack with no Anchor SKU evidence.",
    });

    renderRoutes(
      "/tasks/task-1?panel=intake&stage=product_positioning",
      gateway,
    );

    await userEvent
      .setup()
      .click(await screen.findByRole("button", { name: "生成结果" }));
    expect(
      await screen.findByRole("heading", { name: "需要补充资料" }),
    ).toBeTruthy();
    expect(
      screen.getByText("Provide Anchor SKU product identity evidence."),
    ).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "营销 Brief" })).toBeNull();
  });
});
