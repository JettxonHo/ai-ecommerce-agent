import { render, screen, within } from "@testing-library/react";
import { MemoryRouter, useLocation } from "react-router";
import { describe, expect, it } from "vitest";
import type { TaskOverview } from "../gateway";
import { WORKBENCH_PANELS, WORKBENCH_STAGES } from "./projection";
import { TaskWorkbench } from "./TaskWorkbench";

const taskBaseline: TaskOverview = {
  taskId: "task/7",
  taskName: "City launch",
  productCategory: "Backpack",
  taskStatus: "running",
  currentStage: "product_positioning",
  waitingReason: null,
  updatedAt: "2026-08-12T00:00:00Z",
  revision: 4,
  primaryAction: { kind: "none" },
  capabilities: [],
  stages: [
    {
      stage: "product_positioning",
      status: "running",
      waitingReason: null,
      updatedAt: "2026-08-12T00:00:00Z",
    },
    {
      stage: "product_intake_and_fact_extraction",
      status: "valid",
      waitingReason: "Source accepted",
      updatedAt: "2026-08-11T00:00:00Z",
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

const task = (overrides: Partial<TaskOverview> = {}): TaskOverview => ({
  ...taskBaseline,
  ...overrides,
});

const LocationProbe = () => {
  const location = useLocation();
  return (
    <span data-testid="location">
      {location.pathname}
      {location.search}
    </span>
  );
};

const renderWorkbench = (
  value: TaskOverview = task(),
  search = "?keep=one&panel=review&stage=product_positioning",
) =>
  render(
    <MemoryRouter
      initialEntries={[`/tasks/${encodeURIComponent(value.taskId)}${search}`]}
    >
      <TaskWorkbench task={value} />
      <LocationProbe />
    </MemoryRouter>,
  );

describe("TaskWorkbench", () => {
  it("renders authoritative task metadata, mode, selection, and stage order", () => {
    renderWorkbench(
      task({
        taskStatus: "waiting_for_input",
        currentStage: null,
        waitingReason: "Needs a source",
        needsInputRequest: { resourceId: "input/1", revision: 5 },
        activeRunId: "run-active",
        latestRunId: "run-latest",
        reviewPackage: { reviewPackageId: "review-1", packageVersion: 2 },
        approvedStrategy: {
          resourceKind: "strategy",
          resourceVersionId: "strategy-3",
          versionNumber: 3,
        },
        marketingBrief: {
          resourceKind: "marketing_brief",
          resourceVersionId: "brief-2",
          versionNumber: 2,
        },
        xiaohongshuBrief: {
          resourceKind: "xiaohongshu_brief",
          resourceVersionId: "xhs-1",
          versionNumber: 1,
        },
      }),
      "?keep=one&panel=review&stage=human_review",
    );

    expect(screen.getByRole("heading", { name: "City launch" })).toBeTruthy();
    expect(screen.getByText("Task ID: task/7")).toBeTruthy();
    expect(screen.getByText("Backpack")).toBeTruthy();
    expect(screen.getByText("waiting_for_input")).toBeTruthy();
    expect(screen.getByText("Needs a source")).toBeTruthy();
    expect(screen.getByText("Current workspace: needs_input")).toBeTruthy();
    expect(screen.getByText("Current panel:")).toBeTruthy();
    expect(screen.getByText("human_review")).toBeTruthy();

    const summaries = screen.getByRole("list", { name: "Stage summaries" });
    expect(within(summaries).getAllByRole("listitem")).toHaveLength(2);
    expect(
      within(summaries).getAllByRole("listitem")[0]?.textContent,
    ).toContain("product_positioning");
    expect(
      within(summaries).getAllByRole("listitem")[1]?.textContent,
    ).toContain("product_intake_and_fact_extraction");

    expect(screen.getByText("run-active")).toBeTruthy();
    expect(screen.getByText("run-latest")).toBeTruthy();
    expect(screen.getByText(/input\/1.*revision 5/)).toBeTruthy();
    expect(screen.getByText(/review-1.*version 2/)).toBeTruthy();
    expect(screen.getByText(/strategy-3.*version 3/)).toBeTruthy();
    expect(screen.getByText(/brief-2.*version 2/)).toBeTruthy();
    expect(screen.getByText(/xhs-1.*version 1/)).toBeTruthy();
  });

  it("omits absent references and does not fabricate actions", () => {
    renderWorkbench(task({ taskStatus: "draft" }), "");

    expect(
      screen.queryByRole("heading", { name: "Current references" }),
    ).toBeNull();
    expect(screen.queryByText(/Active Run/)).toBeNull();
    expect(screen.queryByRole("button")).toBeNull();
    expect(
      screen.getByText(/Intake resources and actions are not implemented/),
    ).toBeTruthy();
  });

  it.each(WORKBENCH_PANELS)(
    "renders one neutral message for the selected %s panel",
    (panel) => {
      renderWorkbench(task(), `?panel=${panel}&stage=product_positioning`);
      const status = screen.getByRole("status");
      expect(status.textContent).toMatch(/not implemented in this slice/i);
      expect(status.textContent).not.toMatch(
        /upload|start|run|review content|results content|evidence content/i,
      );
    },
  );

  it("publishes exact panel and stage catalogs with one current selection each", () => {
    renderWorkbench(
      task({
        stages: [
          ...taskBaseline.stages,
          {
            stage: "human_review",
            status: "ready",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
        ],
      }),
      "?keep=one&panel=results&stage=human_review",
    );

    const panelNav = screen.getByRole("navigation", { name: "Task panels" });
    expect(
      within(panelNav)
        .getAllByRole("link")
        .map((link) => link.textContent),
    ).toEqual(["Intake", "Progress", "Review", "Results", "Evidence"]);
    expect(
      within(panelNav)
        .getByRole("link", { name: "Results" })
        .getAttribute("aria-current"),
    ).toBe("page");

    const stageNav = screen.getByRole("navigation", { name: "Task stages" });
    expect(
      within(stageNav)
        .getAllByRole("link")
        .map((link) => link.textContent),
    ).toEqual([...WORKBENCH_STAGES]);
    expect(
      within(stageNav)
        .getByRole("link", { name: "human_review" })
        .getAttribute("aria-current"),
    ).toBe("step");
  });

  it("preserves the encoded task pathname and unrelated query parameters in links", () => {
    renderWorkbench(
      task({
        taskId: "task/with spaces",
        stages: [
          ...taskBaseline.stages,
          {
            stage: "human_review",
            status: "ready",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
        ],
      }),
      "?filter=mine&panel=review&filter=all&stage=human_review",
    );

    expect(
      screen.getByRole("link", { name: "Evidence" }).getAttribute("href"),
    ).toBe(
      "/tasks/task%2Fwith%20spaces?filter=mine&filter=all&panel=evidence&stage=human_review",
    );
    expect(
      screen
        .getByRole("link", { name: "product_positioning" })
        .getAttribute("href"),
    ).toBe(
      "/tasks/task%2Fwith%20spaces?filter=mine&filter=all&panel=review&stage=product_positioning",
    );
  });

  it("canonicalizes invalid selections exactly once and keeps the path", async () => {
    renderWorkbench(
      task({ taskId: "task/with spaces" }),
      "?filter=mine&panel=unknown&panel=review&stage=not-a-stage",
    );

    expect((await screen.findByTestId("location")).textContent).toContain(
      "/tasks/task%2Fwith%20spaces?filter=mine&panel=intake&stage=product_positioning",
    );
    expect(
      screen.getByRole("link", { name: "Intake" }).getAttribute("aria-current"),
    ).toBe("page");
  });

  it("does not canonicalize absent or valid selections", () => {
    renderWorkbench(task(), "?filter=mine");
    expect(screen.getByTestId("location").textContent).toContain(
      "/tasks/task%2F7?filter=mine",
    );
  });
});
