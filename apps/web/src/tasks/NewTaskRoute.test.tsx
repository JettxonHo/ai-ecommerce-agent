import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { createDeterministicTaskGateway } from "./deterministicGateway";
import {
  TaskGatewayError,
  type TaskGateway,
  type TaskInput,
  type TaskOverview,
} from "./gateway";

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

const renderCreate = (
  gateway: TaskGateway,
  queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  }),
) => {
  const result = render(
    <MemoryRouter initialEntries={["/tasks/new"]}>
      <QueryClientProvider client={queryClient}>
        <App taskGateway={gateway} />
      </QueryClientProvider>
    </MemoryRouter>,
  );

  return { ...result, queryClient };
};

const gateway = (): TaskGateway => ({
  listTasks: vi.fn(),
  createTask: vi.fn(),
  getTaskOverview: vi.fn(),
  getPrimaryInput: vi.fn(),
  savePrimaryInput: vi.fn(),
  generateResult: vi.fn(),
  getCurrentResult: vi.fn(),
});

const fill = async (
  user: ReturnType<typeof userEvent.setup>,
  values = {
    taskName: "Launch",
    productCategory: "Backpack",
    promotionGoal: "Awareness",
  },
) => {
  await user.type(
    screen.getByRole("textbox", { name: "Task name" }),
    values.taskName,
  );
  await user.type(
    screen.getByRole("textbox", { name: "Product category" }),
    values.productCategory,
  );
  await user.type(
    screen.getByRole("textbox", { name: "Promotion goal" }),
    values.promotionGoal,
  );
};

const stubUuid = (...keys: string[]) => {
  const randomUUID = vi.fn(() => keys.shift() ?? "uuid-exhausted");
  vi.stubGlobal("crypto", { randomUUID });
  return randomUUID;
};

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("NewTaskRoute", () => {
  it("renders the three-field Task creation form and separate workflow copy", () => {
    renderCreate(gateway());

    expect(screen.getByRole("heading", { name: "Create a task" })).toBeTruthy();
    expect(screen.getByRole("textbox", { name: "Task name" })).toBeTruthy();
    expect(
      screen.getByRole("textbox", { name: "Product category" }),
    ).toBeTruthy();
    expect(
      screen.getByRole("textbox", { name: "Promotion goal" }),
    ).toBeTruthy();
    expect(
      screen.getByText(/Workflow execution is a separate action/i),
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "Create task" })).toBeTruthy();
  });

  it("shows field-local errors and makes no gateway call for blank or whitespace input", async () => {
    const createTask = vi.fn();
    const user = userEvent.setup();
    renderCreate({ ...gateway(), createTask });

    await user.click(screen.getByRole("button", { name: "Create task" }));
    expect(await screen.findByText("Task name is required.")).toBeTruthy();
    expect(screen.getByText("Product category is required.")).toBeTruthy();
    expect(screen.getByText("Promotion goal is required.")).toBeTruthy();
    expect(createTask).not.toHaveBeenCalled();

    await user.type(screen.getByRole("textbox", { name: "Task name" }), "   ");
    await user.type(
      screen.getByRole("textbox", { name: "Product category" }),
      "   ",
    );
    await user.type(
      screen.getByRole("textbox", { name: "Promotion goal" }),
      "   ",
    );
    await user.click(screen.getByRole("button", { name: "Create task" }));
    expect(createTask).not.toHaveBeenCalled();
  });

  it("normalizes the exact three-field body, sends one UUID key, and does not start execution", async () => {
    const task = overview({ taskId: "task/created" });
    const createTask = vi.fn(async () => task);
    const getTaskOverview = vi.fn(async () => task);
    const randomUUID = stubUuid("uuid-1");
    const user = userEvent.setup();
    renderCreate({ ...gateway(), createTask, getTaskOverview });

    await fill(user, {
      taskName: "  Launch  ",
      productCategory: " Backpack ",
      promotionGoal: " Awareness ",
    });
    await user.click(screen.getByRole("button", { name: "Create task" }));

    expect(createTask).toHaveBeenCalledWith(
      {
        taskName: "Launch",
        productCategory: "Backpack",
        promotionGoal: "Awareness",
      },
      "uuid-1",
    );
    expect(createTask).toHaveBeenCalledTimes(1);
    expect(randomUUID).toHaveBeenCalledTimes(1);
    expect(screen.queryByText("uuid-1")).toBeNull();
    expect(await screen.findByText("Task ID: task/created")).toBeTruthy();
    expect(getTaskOverview).toHaveBeenCalledWith("task/created");
  });

  it("disables the submit control while creating and prevents duplicate concurrent calls", async () => {
    let resolve: (task: TaskOverview) => void = () => undefined;
    const pending = new Promise<TaskOverview>((done) => {
      resolve = done;
    });
    const createTask = vi.fn(() => pending);
    stubUuid("uuid-pending");
    const user = userEvent.setup();
    renderCreate({
      ...gateway(),
      createTask,
      getTaskOverview: vi.fn(async () => overview()),
    });
    await fill(user);

    const submit = screen.getByRole("button", { name: "Create task" });
    await user.click(submit);
    expect(submit.hasAttribute("disabled")).toBe(true);
    await user.click(submit);
    expect(createTask).toHaveBeenCalledTimes(1);
    resolve(overview());
    expect(await screen.findByText("Task ID: task-1")).toBeTruthy();
  });

  it("preserves values and offers an explicit retry after a temporary failure", async () => {
    const task = overview();
    const createTask = vi
      .fn<(input: TaskInput, key: string) => Promise<TaskOverview>>()
      .mockRejectedValueOnce(new TaskGatewayError("temporary", "private"))
      .mockResolvedValueOnce(task);
    const randomUUID = stubUuid("uuid-retry");
    const user = userEvent.setup();
    renderCreate({
      ...gateway(),
      createTask,
      getTaskOverview: vi.fn(async () => task),
    });
    await fill(user);
    await user.click(screen.getByRole("button", { name: "Create task" }));

    expect((await screen.findByRole("alert")).textContent).toContain(
      "Your entries are preserved",
    );
    expect(
      (screen.getByRole("textbox", { name: "Task name" }) as HTMLInputElement)
        .value,
    ).toBe("Launch");
    expect(
      screen
        .getByRole("button", { name: "Retry create" })
        .hasAttribute("disabled"),
    ).toBe(false);
    await user.click(screen.getByRole("button", { name: "Retry create" }));
    expect(await screen.findByText("Task ID: task-1")).toBeTruthy();
    expect(createTask).toHaveBeenCalledTimes(2);
    expect(createTask.mock.calls[0]?.[1]).toBe("uuid-retry");
    expect(createTask.mock.calls[1]?.[1]).toBe("uuid-retry");
    expect(randomUUID).toHaveBeenCalledTimes(1);
  });

  it("reuses a key for presentation-only whitespace changes and rotates it for changed normalized input", async () => {
    const createTask = vi
      .fn<(input: TaskInput, key: string) => Promise<TaskOverview>>()
      .mockRejectedValueOnce(new TaskGatewayError("temporary", "private"))
      .mockRejectedValueOnce(new TaskGatewayError("temporary", "private"))
      .mockResolvedValue(overview());
    stubUuid("uuid-same", "uuid-new");
    const user = userEvent.setup();
    renderCreate({
      ...gateway(),
      createTask,
      getTaskOverview: vi.fn(async () => overview()),
    });
    await fill(user);
    await user.click(screen.getByRole("button", { name: "Create task" }));
    await screen.findByRole("alert");

    const taskName = screen.getByRole("textbox", { name: "Task name" });
    await user.clear(taskName);
    await user.type(taskName, "  Launch  ");
    await user.click(screen.getByRole("button", { name: "Retry create" }));
    await screen.findByRole("alert");
    expect(createTask.mock.calls[1]?.[1]).toBe("uuid-same");

    const category = screen.getByRole("textbox", { name: "Product category" });
    await user.clear(category);
    await user.type(category, "Tote");
    await user.click(screen.getByRole("button", { name: "Retry create" }));
    expect(await screen.findByText("Task ID: task-1")).toBeTruthy();
    expect(createTask.mock.calls[2]?.[1]).toBe("uuid-new");
    expect(createTask.mock.calls[2]?.[0]).toEqual({
      taskName: "Launch",
      productCategory: "Tote",
      promotionGoal: "Awareness",
    });
  });

  it("keeps deterministic invalid failures safe and does not expose the key", async () => {
    const createTask = vi.fn(async () => {
      throw new TaskGatewayError("invalid", "private uuid-unsafe");
    });
    stubUuid("uuid-private");
    const user = userEvent.setup();
    renderCreate({ ...gateway(), createTask });
    await fill(user);
    await user.click(screen.getByRole("button", { name: "Create task" }));

    expect((await screen.findByRole("alert")).textContent).toContain(
      "could not be completed",
    );
    expect(screen.getByRole("alert").textContent).not.toContain("uuid-private");
    expect(screen.getByRole("alert").textContent).not.toContain("private uuid");
    expect(screen.queryByText("uuid-private")).toBeNull();
    expect(createTask).toHaveBeenCalledTimes(1);
    expect(
      (screen.getByRole("textbox", { name: "Task name" }) as HTMLInputElement)
        .value,
    ).toBe("Launch");
  });

  it("reuses the key after a malformed-success invalid failure and rotates only for changed normalized input", async () => {
    const task = overview({ taskId: "task/malformed" });
    const createTask = vi
      .fn<(input: TaskInput, key: string) => Promise<TaskOverview>>()
      .mockRejectedValueOnce(
        new TaskGatewayError("invalid", "The task response is invalid."),
      )
      .mockRejectedValueOnce(
        new TaskGatewayError("invalid", "The task response is invalid."),
      )
      .mockResolvedValueOnce(task);
    stubUuid("uuid-malformed", "uuid-changed");
    const user = userEvent.setup();
    renderCreate({
      ...gateway(),
      createTask,
      getTaskOverview: vi.fn(async () => task),
    });
    await fill(user);

    await user.click(screen.getByRole("button", { name: "Create task" }));
    await screen.findByRole("alert");
    await user.click(screen.getByRole("button", { name: "Retry create" }));
    await screen.findByRole("alert");
    expect(createTask.mock.calls[0]?.[1]).toBe("uuid-malformed");
    expect(createTask.mock.calls[1]?.[1]).toBe("uuid-malformed");

    await user.clear(screen.getByRole("textbox", { name: "Product category" }));
    await user.type(
      screen.getByRole("textbox", { name: "Product category" }),
      "Tote",
    );
    await user.click(screen.getByRole("button", { name: "Retry create" }));
    expect(await screen.findByText("Task ID: task/malformed")).toBeTruthy();
    expect(createTask.mock.calls[2]?.[1]).toBe("uuid-changed");
    expect(createTask.mock.calls[2]?.[0]).toEqual({
      taskName: "Launch",
      productCategory: "Tote",
      promotionGoal: "Awareness",
    });
  });

  it("invalidates the Task query family before navigating to the created overview", async () => {
    const task = overview({ taskId: "task/with slash" });
    const createTask = vi.fn(async () => task);
    const getTaskOverview = vi.fn(async () => task);
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    const invalidate = vi.spyOn(queryClient, "invalidateQueries");
    const user = userEvent.setup();
    stubUuid("uuid-cache");
    renderCreate({ ...gateway(), createTask, getTaskOverview }, queryClient);
    await fill(user);
    await user.click(screen.getByRole("button", { name: "Create task" }));

    expect(await screen.findByText("Task ID: task/with slash")).toBeTruthy();
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["tasks"] });
  });

  it("shows a newly created Task through the deterministic gateway adapter", async () => {
    stubUuid("uuid-deterministic");
    const user = userEvent.setup();
    renderCreate(createDeterministicTaskGateway());
    await fill(user);
    await user.click(screen.getByRole("button", { name: "Create task" }));

    expect(await screen.findByRole("heading", { name: "Launch" })).toBeTruthy();
    expect(screen.getByText("Task ID: task-1")).toBeTruthy();
  });
});
