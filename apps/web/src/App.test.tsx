import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";
import App from "./App";
import { createDeterministicTaskGateway } from "./tasks/deterministicGateway";
import type { TaskOverview } from "./tasks/gateway";
import type {
  NeedsInputActionRequest,
  NeedsInputGateway,
} from "./needsInput/gateway";

describe("application routes", () => {
  const renderAt = (
    path: string,
    taskGateway = createDeterministicTaskGateway(),
    needsInputGateway?: NeedsInputGateway,
  ) => {
    const queryClient = new QueryClient();

    return render(
      <MemoryRouter initialEntries={[path]}>
        <QueryClientProvider client={queryClient}>
          <App
            taskGateway={taskGateway}
            needsInputGateway={needsInputGateway}
          />
        </QueryClientProvider>
      </MemoryRouter>,
    );
  };

  it("renders the recent-task entry under the application providers", async () => {
    renderAt("/tasks");
    expect(screen.getByRole("main")).toBeTruthy();
    expect(
      await screen.findByRole("heading", { name: "行动首页" }),
    ).toBeTruthy();
  });

  it.each(["/", "/unknown"])(
    "redirects unsupported location %s to the recent-task entry",
    async (path) => {
      renderAt(path);
      expect(
        await screen.findByRole("heading", { name: "行动首页" }),
      ).toBeTruthy();
      expect(
        screen.getByRole("link", { name: "新建商品上新任务" }),
      ).toBeTruthy();
    },
  );

  it("renders the explicit Task creation route", async () => {
    renderAt("/tasks/new");
    expect(
      await screen.findByRole("heading", { name: "Create a task" }),
    ).toBeTruthy();
    expect(screen.getByRole("textbox", { name: "Task name" })).toBeTruthy();
  });

  it("composes the Needs Input gateway through the application routes", async () => {
    const task: TaskOverview = {
      taskId: "task-1",
      taskName: "Launch",
      productCategory: "Backpack",
      taskStatus: "waiting_for_input",
      currentStage: "product_intake_and_fact_extraction",
      waitingReason: "商品身份存在两个候选值。",
      updatedAt: "2026-08-12T00:00:00Z",
      revision: 2,
      primaryAction: { kind: "navigate", target: "needs_input" },
      capabilities: [],
      stages: [
        {
          stage: "product_intake_and_fact_extraction",
          status: "waiting_input",
          waitingReason: "商品身份存在两个候选值。",
          updatedAt: "2026-08-12T00:00:00Z",
        },
      ],
      activeRunId: null,
      latestRunId: null,
      needsInputRequest: { resourceId: "action-1", revision: 2 },
      reviewPackage: null,
      approvedStrategy: null,
      marketingBrief: null,
      xiaohongshuBrief: null,
    };
    const request: NeedsInputActionRequest = {
      actionRequestId: "action-1",
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
    const getNeedsInputActionRequest = vi.fn(async () => request);
    const needsInputGateway: NeedsInputGateway = {
      getNeedsInputActionRequest,
      resolveNeedsInput: vi.fn(),
    };

    renderAt(
      "/tasks/task-1",
      createDeterministicTaskGateway({ tasks: [task] }),
      needsInputGateway,
    );

    expect(
      await screen.findByRole("heading", { name: "需要补充信息" }),
    ).toBeTruthy();
    expect(getNeedsInputActionRequest).toHaveBeenCalledWith("action-1");
  });
});
