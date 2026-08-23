import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useContext, useMemo, type ReactNode } from "react";
import {
  MemoryRouter,
  Route,
  Routes,
  UNSAFE_NavigationContext,
  useLocation,
} from "react-router";
import { describe, expect, it, vi } from "vitest";
import { TaskRoutes } from "../TaskRoutes";
import type { TaskGateway, TaskOverview } from "../gateway";
import type { TaskCurrentResult, TaskPrimaryInput } from "../gateway";
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

const replaceSpy = vi.fn();

const NavigationSpy = ({ children }: Readonly<{ children: ReactNode }>) => {
  const navigation = useContext(UNSAFE_NavigationContext);
  const navigator = useMemo(
    () => ({
      ...navigation.navigator,
      replace: (...args: Parameters<typeof navigation.navigator.replace>) => {
        replaceSpy(...args);
        return navigation.navigator.replace(...args);
      },
    }),
    [navigation.navigator],
  );

  return (
    <UNSAFE_NavigationContext.Provider value={{ ...navigation, navigator }}>
      {children}
    </UNSAFE_NavigationContext.Provider>
  );
};

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
) => {
  const result = render(
    <MemoryRouter
      initialEntries={[`/tasks/${encodeURIComponent(value.taskId)}${search}`]}
    >
      <TaskWorkbench task={value} />
      <LocationProbe />
    </MemoryRouter>,
  );
  return result;
};

describe("TaskWorkbench", () => {
  it("shows exactly five Chinese business stages while retaining the six-value internal catalog and deep links", () => {
    renderWorkbench(
      task({
        stages: WORKBENCH_STAGES.map((stage) => ({
          stage,
          status: "ready",
          waitingReason: null,
          updatedAt: "2026-08-12T00:00:00Z",
        })),
      }),
      "?panel=review&stage=human_review",
    );

    const stageNavigation = screen.getByRole("navigation", {
      name: "业务阶段",
    });
    expect(
      within(stageNavigation)
        .getAllByRole("link")
        .map((link) => link.getAttribute("aria-label")),
    ).toEqual([
      "资料整理",
      "用户洞察",
      "商品定位",
      "营销 Brief",
      "小红书 Brief",
    ]);
    expect(within(stageNavigation).getAllByRole("link")).toHaveLength(5);
    expect(WORKBENCH_STAGES).toHaveLength(6);
    expect(screen.getByTestId("location").textContent).toContain(
      "stage=human_review",
    );
  });

  it("provides one active workspace and an in-flow Context Rail disclosure", () => {
    renderWorkbench(task(), "?panel=review&stage=product_positioning");

    expect(screen.getAllByRole("heading", { name: "当前工作区" })).toHaveLength(
      1,
    );
    expect(screen.getByRole("region", { name: "当前工作区" })).toBeTruthy();

    const context = screen.getByRole("complementary", {
      name: "上下文与执行信息",
    });
    const rail = context.querySelector("details");
    expect(rail).not.toBeNull();
    expect(rail?.querySelector("summary")?.textContent).toContain(
      "上下文与执行信息",
    );
  });

  it("keeps visible Context Rail summaries business-readable with stable timestamps", () => {
    renderWorkbench(
      task({
        stages: WORKBENCH_STAGES.map((stage) => ({
          stage,
          status: stage === "product_positioning" ? "running" : "ready",
          waitingReason: null,
          updatedAt: "2026-08-12T00:00:00Z",
        })),
      }),
      "?panel=progress&stage=product_positioning",
    );

    const context = screen.getByRole("complementary", {
      name: "上下文与执行信息",
    });
    const summaries = within(context).getByRole("list", {
      name: "Stage summaries",
    });
    expect(within(summaries).getByText("资料整理")).toBeTruthy();
    expect(within(summaries).getByText("商品定位")).toBeTruthy();
    expect(within(summaries).getAllByText("已完成").length).toBeGreaterThan(0);
    expect(within(summaries).getByText("处理中")).toBeTruthy();
    expect(within(summaries).queryByText("valid")).toBeNull();
    expect(within(summaries).queryByText("running")).toBeNull();
    expect(
      within(summaries).queryByText("product_intake_and_fact_extraction"),
    ).toBeNull();
    const timestamp = context.querySelector(
      'time[dateTime="2026-08-12T00:00:00Z"]',
    );
    expect(timestamp).not.toBeNull();
    expect(timestamp?.textContent).toContain("2026年8月12日 00:00");
    const headerTimestamp = screen
      .getByRole("banner")
      .querySelector('time[dateTime="2026-08-12T00:00:00Z"]');
    expect(headerTimestamp).not.toBeNull();
    expect(headerTimestamp?.textContent).toContain("2026年8月12日 00:00");
  });

  it("keeps TaskGateway actions and canonical query semantics behind the shell", async () => {
    const primaryInput: TaskPrimaryInput = {
      taskId: taskBaseline.taskId,
      inputRevision: 0,
      inputKind: "pasted_text",
      fileName: null,
      content: "城市通勤双肩包 CBP-SYN-001",
      byteCount: 37,
      updatedAt: "2026-08-12T00:00:00Z",
    };
    const generatedResult = {
      taskId: taskBaseline.taskId,
      resultRevision: 1,
      inputRevision: 0,
      status: "insufficient_input",
      generatedAt: "2026-08-12T00:00:00Z",
      missingInformation: ["需要更多资料"],
      productIntake: null,
      customerInsight: null,
      productPositioning: null,
      marketingBrief: null,
      xiaohongshuBrief: null,
      confirmation: null,
    } satisfies TaskCurrentResult;
    const generateResult = vi.fn().mockResolvedValue(generatedResult);

    render(
      <MemoryRouter
        initialEntries={[
          `/tasks/${encodeURIComponent(taskBaseline.taskId)}?keep=one&panel=intake&stage=product_positioning`,
        ]}
      >
        <TaskWorkbench
          task={task()}
          primaryInput={primaryInput}
          savePrimaryInput={vi.fn(async () => primaryInput)}
          generateResult={generateResult}
        />
        <LocationProbe />
      </MemoryRouter>,
    );

    const generate = await screen.findByRole("button", { name: "生成结果" });
    await userEvent.setup().click(generate);
    expect(generateResult).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId("location").textContent).toContain(
      "?keep=one&panel=results&stage=product_positioning",
    );
  });

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
    expect(
      within(
        screen.getByRole("complementary", { name: "上下文与执行信息" }),
      ).getByText("待补充资料"),
    ).toBeTruthy();
    expect(
      screen.getByRole("link", { name: "Review" }).getAttribute("aria-current"),
    ).toBe("page");
    expect(screen.getByText("human_review")).toBeTruthy();

    const summaries = screen.getByRole("list", { name: "Stage summaries" });
    expect(within(summaries).getAllByRole("listitem")).toHaveLength(2);
    expect(
      within(summaries).getAllByRole("listitem")[0]?.textContent,
    ).toContain("资料整理");
    expect(
      within(summaries).getAllByRole("listitem")[0]?.textContent,
    ).toContain("已完成");
    expect(
      within(summaries).getAllByRole("listitem")[1]?.textContent,
    ).toContain("商品定位");
    expect(
      within(summaries).getAllByRole("listitem")[1]?.textContent,
    ).toContain("处理中");

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
    expect(screen.getByRole("status").textContent).toBe(
      "在这里粘贴或保存商品资料。",
    );
  });

  it.each(WORKBENCH_PANELS)(
    "renders one neutral message for the selected %s panel",
    (panel) => {
      renderWorkbench(task(), `?panel=${panel}&stage=product_positioning`);
      const status = screen.getByRole("status");
      expect(status.textContent).toBe(
        {
          intake: "在这里粘贴或保存商品资料。",
          progress: "任务正在处理，状态会在本地工作区更新。",
          review: "审核材料会在需要人工判断时出现在这里。",
          results: "结果与导出会在任务完成后出现在这里。",
          evidence: "证据、来源与限制会在上下文栏中保留。",
        }[panel],
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

    const panelNav = screen.getByRole("navigation", { name: "工作区面板" });
    expect(
      within(panelNav)
        .getAllByRole("link")
        .map((link) => link.textContent),
    ).toEqual(["资料输入", "进度", "Review", "结果", "证据"]);
    expect(
      within(panelNav)
        .getByRole("link", { name: "结果" })
        .getAttribute("aria-current"),
    ).toBe("page");

    const stageNav = screen.getByRole("navigation", { name: "业务阶段" });
    expect(
      within(stageNav)
        .getAllByRole("link")
        .map((link) => link.getAttribute("aria-label")),
    ).toEqual([
      "资料整理",
      "用户洞察",
      "商品定位",
      "营销 Brief",
      "小红书 Brief",
    ]);
    expect(
      within(stageNav)
        .getByRole("link", { name: "商品定位" })
        .getAttribute("aria-current"),
    ).toBeNull();
    const internalStageNav = screen.getByRole("navigation", {
      name: "内部阶段深链",
    });
    expect(within(internalStageNav).getAllByRole("link")).toHaveLength(6);
    expect(
      within(internalStageNav)
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
      screen.getByRole("link", { name: "证据" }).getAttribute("href"),
    ).toBe(
      "/tasks/task%2Fwith%20spaces?filter=mine&filter=all&panel=evidence&stage=human_review",
    );
    expect(
      screen.getByRole("link", { name: "商品定位" }).getAttribute("href"),
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
      screen
        .getByRole("link", { name: "资料输入" })
        .getAttribute("aria-current"),
    ).toBe("page");
  });

  it("does not canonicalize absent or valid selections", () => {
    renderWorkbench(task(), "?filter=mine");
    expect(screen.getByTestId("location").textContent).toContain(
      "/tasks/task%2F7?filter=mine",
    );
  });

  it.each([
    {
      label: "a blank panel",
      search: "?panel=",
      expectedSearch: "?panel=intake&stage=product_positioning",
      replaceCount: 1,
    },
    {
      label: "a blank stage",
      search: "?stage=",
      expectedSearch: "?panel=intake&stage=product_positioning",
      replaceCount: 1,
    },
    {
      label: "repeated panel values",
      search: "?panel=review&panel=results&stage=product_positioning",
      expectedSearch: "?panel=intake&stage=product_positioning",
      replaceCount: 1,
    },
    {
      label: "an inapplicable stage",
      search: "?panel=review&stage=human_review",
      expectedSearch: "?panel=review&stage=product_positioning",
      replaceCount: 1,
    },
    {
      label: "a valid selection",
      search: "?panel=review&stage=product_positioning",
      expectedSearch: null,
      replaceCount: 0,
    },
    {
      label: "absent parameters",
      search: "",
      expectedSearch: null,
      replaceCount: 0,
    },
  ])(
    "integrated TaskRoutes performs exactly one canonical replace for $label",
    async ({ search, expectedSearch, replaceCount }) => {
      replaceSpy.mockClear();
      const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false } },
      });
      const getTaskOverview = vi.fn().mockResolvedValue(task());
      const gateway: TaskGateway = {
        listTasks: () => Promise.resolve([]),
        createTask: () => Promise.resolve(task()),
        getTaskOverview,
        getPrimaryInput: async () => {
          throw new Error("Primary input is not available in this test.");
        },
        savePrimaryInput: async () => {
          throw new Error("Primary input is not available in this test.");
        },
        generateResult: vi.fn(),
        getCurrentResult: vi.fn(),
      };

      render(
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={[`/tasks/task-7${search}`]}>
            <NavigationSpy>
              <Routes>
                <Route
                  path="/tasks/:taskId"
                  element={<TaskRoutes taskGateway={gateway} />}
                />
              </Routes>
            </NavigationSpy>
          </MemoryRouter>
        </QueryClientProvider>,
      );

      await waitFor(() =>
        expect(
          screen.getByRole("heading", { name: "City launch" }),
        ).toBeTruthy(),
      );
      if (replaceCount === 1) {
        await waitFor(() => expect(replaceSpy).toHaveBeenCalledTimes(1));
        expect(replaceSpy.mock.calls[0]?.[0]).toEqual({
          hash: "",
          pathname: "/tasks/task-7",
          search: expectedSearch,
        });
      } else {
        await new Promise((resolve) => setTimeout(resolve, 25));
      }
      expect(replaceSpy).toHaveBeenCalledTimes(replaceCount);
      expect(getTaskOverview).toHaveBeenCalledTimes(1);
    },
  );
});
