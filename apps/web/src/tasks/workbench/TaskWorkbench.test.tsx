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
  it("presents Running as an honest business stage with a next action", () => {
    renderWorkbench(
      task({
        taskStatus: "running",
        currentStage: "customer_insight_analysis",
        activeRunId: "run-commuter-1",
        stages: [
          {
            stage: "product_intake_and_fact_extraction",
            status: "valid",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
          {
            stage: "customer_insight_analysis",
            status: "running",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
        ],
      }),
      "?panel=progress&stage=customer_insight_analysis",
    );

    expect(screen.getByRole("heading", { name: "正在处理" })).toBeTruthy();
    expect(screen.getAllByText("当前阶段").length).toBeGreaterThan(0);
    expect(screen.getByRole("heading", { name: "用户洞察" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "下一步" })).toBeTruthy();
    const runningPanel = screen.getByRole("region", { name: "正在处理" });
    expect(within(runningPanel).queryByText(/%|预计完成|ETA/u)).toBeNull();
  });

  it("renders Review as semantic business groups with only the two bounded edits", () => {
    const reviewResult: TaskCurrentResult = {
      taskId: taskBaseline.taskId,
      resultRevision: 4,
      inputRevision: 1,
      status: "awaiting_review",
      generatedAt: "2026-08-12T00:00:00Z",
      missingInformation: [],
      productIntake: { facts: ["约 18 升", "可放入 14 英寸级别笔记本电脑"] },
      customerInsight: {
        customer_insights: [
          { statement: "工作日城市通勤需要有序携带电脑和文件" },
        ],
      },
      productPositioning: {
        positioning_candidates: [
          {
            candidate_title: "城市通勤的清晰收纳方案",
            target_segment: "工作日城市通勤者",
            value_proposition: "用清晰收纳支持日常通勤携带",
            proof_points: [{ statement: "可放入 14 英寸级别笔记本电脑" }],
            evidence_limitations: ["没有竞品资料或用户规模数据"],
            strategic_risks: ["不得将防泼水描述写成绝对防水"],
          },
        ],
      },
      marketingBrief: {
        brief_candidate: {
          objective_and_audience: { audience: "工作日城市通勤者" },
          message_architecture: {
            core_message: "为工作日通勤提供清晰的电脑与日常物品收纳",
          },
          constraints_and_honesty: {
            evidence_limitations: ["没有真实用户研究"],
            risk_notes: ["防泼水只按资料原文表达"],
          },
        },
      },
      xiaohongshuBrief: {
        xiaohongshu_brief_candidate: {
          creative_structure_directions: {
            title_directions: [
              { title_direction: "通勤包如何把电脑和日常物品放得更清楚" },
            ],
          },
          evidence_and_platform_constraints: {
            evidence_limitations: ["合成资料，不代表真实用户研究"],
            platform_risk_notes: ["遵守事实和证据边界"],
          },
        },
      },
      confirmation: null,
    };

    render(
      <MemoryRouter
        initialEntries={[
          `/tasks/${encodeURIComponent(taskBaseline.taskId)}?panel=review&stage=product_positioning`,
        ]}
      >
        <TaskWorkbench
          task={task({
            reviewPackage: { reviewPackageId: "review-1", packageVersion: 4 },
          })}
          currentResult={reviewResult}
          confirmCurrentResult={vi.fn()}
        />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "商品定位" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "营销 Brief" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "小红书 Brief" })).toBeTruthy();
    expect(screen.getByText("城市通勤的清晰收纳方案")).toBeTruthy();
    expect(
      screen.getAllByText("为工作日通勤提供清晰的电脑与日常物品收纳").length,
    ).toBeGreaterThan(0);
    expect(
      screen.getAllByText("通勤包如何把电脑和日常物品放得更清楚").length,
    ).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "确认并生成结果" })).toBeTruthy();
    expect(screen.getByLabelText("营销核心信息")).toBeTruthy();
    expect(screen.getByLabelText("小红书标题方向")).toBeTruthy();
    expect(screen.getByText("技术细节")).toBeTruthy();
    expect(screen.queryByText(/brief_candidate/u)).toBeNull();
  });

  it("keeps Results views separate and previews Markdown as escaped text", async () => {
    const confirmedResult: TaskCurrentResult = {
      taskId: taskBaseline.taskId,
      resultRevision: 5,
      inputRevision: 1,
      status: "confirmed",
      generatedAt: "2026-08-12T00:00:00Z",
      missingInformation: [],
      productIntake: { facts: ["约 18 升"] },
      customerInsight: {
        customer_insights: [{ statement: "通勤需要有序携带" }],
      },
      productPositioning: {
        positioning_candidates: [
          {
            candidate_title: "城市通勤的清晰收纳方案",
            target_segment: "工作日城市通勤者",
            proof_points: [{ statement: "可放入 14 英寸级别笔记本电脑" }],
          },
        ],
      },
      marketingBrief: {
        brief_candidate: {
          objective_and_audience: { audience: "工作日城市通勤者" },
          message_architecture: {
            core_message: "收纳清晰，通勤取用更从容 <strong>字面内容</strong>",
          },
          reasons_to_believe_and_evidence: {
            proof_points: [{ proof_point: "可放入 14 英寸级别笔记本电脑" }],
          },
          constraints_and_honesty: {
            evidence_limitations: ["没有真实用户研究"],
            risk_notes: ["不宣称绝对防水"],
          },
        },
      },
      xiaohongshuBrief: {
        xiaohongshu_brief_candidate: {
          creative_structure_directions: {
            title_directions: [{ title_direction: "通勤收纳路径" }],
          },
          evidence_and_platform_constraints: {
            proof_points: ["约 18 升容量"],
            evidence_limitations: ["合成资料"],
            platform_risk_notes: ["遵守事实和证据边界"],
          },
        },
      },
      confirmation: {
        marketingBriefVersion: {
          resourceKind: "marketing_brief",
          resourceVersionId: "brief-marketing",
          versionNumber: 1,
        },
        xiaohongshuBriefVersion: {
          resourceKind: "xiaohongshu_brief",
          resourceVersionId: "brief-xhs",
          versionNumber: 1,
        },
        confirmedAt: "2026-08-12T00:00:00Z",
      },
    };
    const exportBrief = vi.fn(async () => ({
      snapshot: {
        exportSnapshotId: "export-1",
        taskId: taskBaseline.taskId,
        briefKind: "marketing" as const,
        briefVersion: {
          resourceKind: "marketing_brief",
          resourceVersionId: "brief-marketing",
          versionNumber: 1,
        },
        upstreamVersions: [],
        exportedAt: "2026-08-12T00:00:00Z",
        fileName: "task-7-marketing-v1-20260812T000000Z.md",
        mediaType: "text/markdown; charset=utf-8",
        contentLocation: "local://export-1",
        templateVersion: "mvp0-markdown-v1",
      },
      content: "# Marketing Brief\n\n收纳清晰",
    }));

    render(
      <MemoryRouter
        initialEntries={[
          `/tasks/${encodeURIComponent(taskBaseline.taskId)}?panel=results&stage=marketing_brief_generation`,
        ]}
      >
        <TaskWorkbench
          task={task({
            marketingBrief: {
              resourceKind: "marketing_brief",
              resourceVersionId: "brief-marketing",
              versionNumber: 1,
            },
            xiaohongshuBrief: {
              resourceKind: "xiaohongshu_brief",
              resourceVersionId: "brief-xhs",
              versionNumber: 1,
            },
          })}
          currentResult={confirmedResult}
          exportBrief={exportBrief}
        />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "定位摘要" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "目标用户" })).toBeTruthy();
    expect(
      screen.getByRole("heading", { name: "Proof Points / 证据" }),
    ).toBeTruthy();
    expect(screen.getByRole("heading", { name: "风险与限制" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "下一步" })).toBeTruthy();
    const tabs = screen.getByRole("tablist", { name: "结果视图" });
    const user = userEvent.setup();
    const marketingTab = within(tabs).getByRole("tab", {
      name: "营销 Brief",
    });
    const xiaohongshuTab = within(tabs).getByRole("tab", {
      name: "小红书 Brief",
    });
    for (const tab of [marketingTab, xiaohongshuTab]) {
      const panelId = tab.getAttribute("aria-controls");
      expect(panelId).not.toBeNull();
      expect(document.getElementById(panelId ?? "")).not.toBeNull();
    }
    expect(marketingTab.getAttribute("aria-selected")).toBe("true");
    expect(xiaohongshuTab.getAttribute("aria-selected")).toBe("false");
    await user.click(marketingTab);
    await user.keyboard("{ArrowRight}");
    expect(xiaohongshuTab.getAttribute("aria-selected")).toBe("true");
    expect(document.activeElement).toBe(xiaohongshuTab);
    await user.keyboard("{Home}");
    expect(marketingTab.getAttribute("aria-selected")).toBe("true");
    expect(document.activeElement).toBe(marketingTab);
    await user.keyboard("{End}");
    expect(xiaohongshuTab.getAttribute("aria-selected")).toBe("true");
    expect(document.activeElement).toBe(xiaohongshuTab);
    for (const tab of [marketingTab, xiaohongshuTab]) {
      const panelId = tab.getAttribute("aria-controls");
      expect(document.getElementById(panelId ?? "")).not.toBeNull();
    }
    expect(screen.getByRole("button", { name: "预览 Markdown" })).toBeTruthy();
    expect(
      screen.getByRole("button", { name: "导出营销 Markdown" }),
    ).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "预览 Markdown" }));
    expect(screen.getByRole("region", { name: "Markdown 预览" })).toBeTruthy();
    expect(
      screen.getAllByText(/<strong>字面内容<\/strong>/u).length,
    ).toBeGreaterThan(0);
    expect(document.querySelector("script")).toBeNull();
    await user.click(screen.getByRole("tab", { name: "小红书 Brief" }));
    expect(
      document.getElementById("xiaohongshu-brief-panel")?.textContent,
    ).toContain("通勤收纳路径");
    expect(
      document.getElementById("marketing-brief-panel")?.hasAttribute("hidden"),
    ).toBe(true);
  });

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
    expect(within(stageNavigation).getAllByRole("link")).toHaveLength(5);
    for (const label of [
      "资料整理",
      "用户洞察",
      "商品定位",
      "营销 Brief",
      "小红书 Brief",
    ]) {
      expect(
        within(stageNavigation).getByRole("link", {
          name: new RegExp(`^${label}`),
        }),
      ).toBeTruthy();
    }
    expect(WORKBENCH_STAGES).toHaveLength(6);
    expect(screen.getByTestId("location").textContent).toContain(
      "stage=human_review",
    );
  });

  it("keeps authoritative stage statuses distinct in the rail and summary", () => {
    renderWorkbench(
      task({
        currentStage: "product_positioning",
        stages: [
          {
            stage: "product_intake_and_fact_extraction",
            status: "ready",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
          {
            stage: "customer_insight_analysis",
            status: "waiting_input",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
          {
            stage: "product_positioning",
            status: "invalid",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
          {
            stage: "marketing_brief_generation",
            status: "skipped",
            waitingReason: null,
            updatedAt: "2026-08-12T00:00:00Z",
          },
        ],
      }),
      "?panel=progress&stage=product_positioning",
    );

    const summaries = screen.getByRole("list", { name: "Stage summaries" });
    expect(within(summaries).getByText("可开始")).toBeTruthy();
    expect(within(summaries).getByText("需补资料")).toBeTruthy();
    expect(within(summaries).getByText("已失效/需重新处理")).toBeTruthy();
    expect(within(summaries).getByText("已跳过")).toBeTruthy();
    expect(within(summaries).queryByText("已完成")).toBeNull();

    const stageNavigation = screen.getByRole("navigation", {
      name: "业务阶段",
    });
    expect(
      within(stageNavigation).getByRole("link", {
        name: /资料整理.*可开始/,
      }),
    ).toBeTruthy();
    expect(
      within(stageNavigation).getByRole("link", {
        name: /用户洞察.*需补资料/,
      }),
    ).toBeTruthy();
    expect(
      within(stageNavigation).getByRole("link", {
        name: /商品定位.*当前.*已失效\/需重新处理/,
      }),
    ).toBeTruthy();
    expect(
      within(stageNavigation).getByRole("link", {
        name: /营销 Brief.*已跳过/,
      }),
    ).toBeTruthy();
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
    expect(within(summaries).getAllByText("可开始").length).toBeGreaterThan(0);
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
    await waitFor(() =>
      expect(screen.getByTestId("location").textContent).toContain(
        "?keep=one&panel=results&stage=product_positioning",
      ),
    );
  });

  it("renders authoritative task metadata, mode, selection, and stage order", async () => {
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

    expect(screen.getByRole("heading", { name: "当前引用" })).toBeTruthy();
    expect(screen.queryByText("run-active")).toBeNull();
    const references = screen
      .getByRole("heading", { name: "当前引用" })
      .closest("section");
    expect(references).not.toBeNull();
    if (references !== null) {
      await userEvent.setup().click(within(references).getByText("技术详情"));
      expect(within(references).getByText("run-active")).toBeTruthy();
      expect(within(references).getByText("run-latest")).toBeTruthy();
      expect(within(references).getByText(/input\/1.*revision 5/)).toBeTruthy();
      expect(within(references).getByText(/review-1.*version 2/)).toBeTruthy();
      expect(
        within(references).getByText(/strategy-3.*version 3/),
      ).toBeTruthy();
      expect(within(references).getByText(/brief-2.*version 2/)).toBeTruthy();
      expect(within(references).getByText(/xhs-1.*version 1/)).toBeTruthy();
    }
  });

  it("omits absent references and does not fabricate actions", () => {
    renderWorkbench(task({ taskStatus: "draft" }), "");

    expect(screen.queryByRole("heading", { name: "当前引用" })).toBeNull();
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
    expect(within(stageNav).getAllByRole("link")).toHaveLength(5);
    expect(
      within(stageNav)
        .getByRole("link", { name: /商品定位/ })
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
      screen.getByRole("link", { name: /商品定位/ }).getAttribute("href"),
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
