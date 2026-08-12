import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";
import App from "../App";
import { createDeterministicTaskGateway } from "./deterministicGateway";
import {
  TaskGatewayError,
  type TaskGateway,
  type TaskOverview,
} from "./gateway";

const overview = (overrides: Partial<TaskOverview> = {}): TaskOverview =>
  ({
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
        waitingReason: null,
        updatedAt: "2026-08-11T00:00:00Z",
      },
      {
        stage: "product_positioning",
        status: "running",
        waitingReason: null,
        updatedAt: "2026-08-12T00:00:00Z",
      },
    ],
    activeRun: null,
    latestRun: null,
    needsInputRequest: null,
    reviewPackage: null,
    approvedStrategy: null,
    marketingBrief: null,
    xiaohongshuBrief: null,
    ...overrides,
  }) as TaskOverview;

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
});

describe("TaskRoutes", () => {
  it("renders the normal empty recent-task state", async () => {
    renderRoutes();

    expect(
      await screen.findByRole("heading", { name: "Recent tasks" }),
    ).toBeTruthy();
    expect(await screen.findByText("No tasks yet.")).toBeTruthy();
  });

  it("loads a stable deep-link overview and preserves stage order", async () => {
    const task = overview({ taskId: "task/7" });
    renderRoutes(
      "/tasks/task%2F7",
      createDeterministicTaskGateway({ tasks: [task] }),
    );

    expect(await screen.findByRole("heading", { name: "Launch" })).toBeTruthy();
    const stages = screen.getAllByRole("listitem");
    expect(stages.map((stage) => stage.textContent)).toEqual([
      expect.stringContaining("product_intake_and_fact_extraction"),
      expect.stringContaining("product_positioning"),
    ]);
    expect(
      screen
        .getByRole("link", { name: "Back to recent tasks" })
        .getAttribute("href"),
    ).toBe("/tasks");
  });

  it("exposes an accessible loading state while listing recent tasks", () => {
    const listTasks = () => new Promise<readonly TaskOverview[]>(() => {});
    renderRoutes("/tasks", gatewayFor([], listTasks));

    expect(screen.getByRole("status").textContent).toContain(
      "Loading recent tasks",
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
      .click(screen.getByRole("button", { name: "Retry" }));
    expect(
      await screen.findByRole("link", { name: "Retry launch" }),
    ).toBeTruthy();
    expect(attempts).toBe(2);
  });

  it("keeps server order, renders the bounded summary, and encodes task links", async () => {
    const first = overview({
      taskId: "task/first id",
      taskName: "First <script>alert(1)</script>",
      currentStage: null,
      waitingReason: "Needs a source",
      primaryAction: { kind: "navigate", target: "needs_input" },
    });
    const second = overview({
      taskId: "second",
      taskName: "Second",
      currentStage: "customer_insight_analysis",
      taskStatus: "waiting_for_review",
      primaryAction: { kind: "command", command: "start" },
    });
    const third = overview({
      taskId: "third",
      taskName: "Third",
      primaryAction: { kind: "unavailable" },
    });
    renderRoutes("/tasks", gatewayFor([first, second, third]));

    const links = await screen.findAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual([
      first.taskName,
      second.taskName,
      third.taskName,
    ]);
    expect(links[0]?.getAttribute("href")).toBe("/tasks/task%2Ffirst%20id");
    expect(screen.getByText("Needs a source")).toBeTruthy();
    expect(screen.getByText("Continue in needs_input")).toBeTruthy();
    expect(screen.getByText("Next action: start")).toBeTruthy();
    expect(screen.getByText("Next action unavailable")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "start" })).toBeNull();
    expect(screen.queryByRole("button", { name: /create/i })).toBeNull();
    expect(screen.queryByText(first.taskName)).toBeTruthy();
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
    expect(screen.queryByRole("button", { name: "Retry" })).toBeNull();
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
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "Retry" }));
    expect(
      await screen.findByRole("heading", { name: "Recovered task" }),
    ).toBeTruthy();
    expect(screen.getByText("Task ID: retry/7")).toBeTruthy();
    expect(attempts).toBe(2);
  });
});
