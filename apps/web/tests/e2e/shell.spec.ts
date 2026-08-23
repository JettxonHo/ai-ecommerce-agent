import { expect, test } from "@playwright/test";

const task = {
  taskId: "task/7",
  taskName: "City launch",
  productCategory: "Backpack",
  taskStatus: "running",
  currentStage: "product_positioning",
  waitingReason: null,
  updatedAt: "2026-08-12T00:00:00Z",
  revision: 1,
  primaryAction: { type: "none" },
  capabilities: [],
  stages: [
    {
      stage: "product_intake_and_fact_extraction",
      status: "valid",
      currentVersion: null,
      lastValidVersion: null,
      lastRun: null,
      waitingReason: null,
      updatedAt: "2026-08-11T00:00:00Z",
    },
    {
      stage: "product_positioning",
      status: "running",
      currentVersion: null,
      lastValidVersion: null,
      lastRun: null,
      waitingReason: null,
      updatedAt: "2026-08-12T00:00:00Z",
    },
  ],
};
const primaryInput = {
  taskId: "shell-primary-input",
  inputRevision: 0,
  inputKind: "pasted_text",
  fileName: null,
  content: "Existing saved input",
  byteCount: 20,
  updatedAt: "2026-08-12T00:00:00Z",
};
const missingCurrentResult = (instance: string) => ({
  type: "urn:ai-ecommerce-agent:problem:not-found",
  title: "Not found",
  status: 404,
  detail: "The current result was not found.",
  instance,
  action: "none",
});
const missingCurrentResultStatus = "status of 404 (Not Found)";

test("renders recent tasks and restores a stable deep link without errors", async ({
  page,
}) => {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];

  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (
      message.type() === "error" &&
      !message.text().includes(missingCurrentResultStatus)
    ) {
      consoleErrors.push(message.text());
    }
  });

  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }
    if (url.pathname === "/api/v1/tasks") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [task], limit: 20 }),
      });
      return;
    }
    if (decodeURIComponent(url.pathname) === "/api/v1/tasks/task/7") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(task),
      });
      return;
    }
    await route.abort();
  });

  await page.goto("/");

  await expect(page).toHaveTitle("商品上新行动工作台");
  await expect(page).toHaveURL(/\/tasks$/);
  await expect(page.getByRole("heading", { name: "行动首页" })).toBeVisible();
  await page
    .getByRole("region", { name: "继续处理" })
    .getByRole("link", { name: "City launch" })
    .click();
  await expect(page).toHaveURL(/\/tasks\/task%2F7$/);
  await expect(page.getByRole("heading", { name: "当前工作区" })).toBeVisible();
  await expect(
    page
      .locator('section[aria-labelledby="task-workbench-heading"]')
      .getByRole("heading", { name: "City launch" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "资料输入", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await page.getByRole("link", { name: "进度", exact: true }).click();
  await expect(page).toHaveURL(
    /\/tasks\/task%2F7\?panel=progress&stage=product_positioning$/,
  );
  await page.reload();
  await expect(
    page
      .locator('section[aria-labelledby="task-workbench-heading"]')
      .getByRole("heading", { name: "City launch" }),
  ).toBeVisible();
  await expect(page).toHaveURL(
    /\/tasks\/task%2F7\?panel=progress&stage=product_positioning$/,
  );
  await expect(
    page.getByRole("link", { name: "进度", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test("canonicalizes an invalid panel and stage selection on the same Task URL", async ({
  page,
}) => {
  const requestPaths: string[] = [];
  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    requestPaths.push(`${route.request().method()} ${url.pathname}`);
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }
    if (decodeURIComponent(url.pathname) === "/api/v1/tasks/task/7") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(task),
      });
      return;
    }
    await route.abort();
  });

  await page.goto(
    "/tasks/task%2F7?filter=mine&panel=unknown&panel=review&stage=not-a-stage",
  );

  await expect(page).toHaveURL(
    /\/tasks\/task%2F7\?filter=mine&panel=intake&stage=product_positioning$/,
  );
  await expect(
    page.getByRole("heading", { name: "City launch" }),
  ).toBeVisible();
  await page.reload();
  await expect(page).toHaveURL(
    /\/tasks\/task%2F7\?filter=mine&panel=intake&stage=product_positioning$/,
  );
  expect(requestPaths).toEqual([
    "GET /api/v1/tasks/task%2F7",
    "GET /api/v1/tasks/task%2F7/current-result",
    "GET /api/v1/tasks/task%2F7",
    "GET /api/v1/tasks/task%2F7/current-result",
  ]);
});

test("renders representative intake, active-run, and recovery modes without extra requests", async ({
  page,
}) => {
  const activeRunTask = {
    ...task,
    taskId: "task-active",
    taskName: "Active run",
    activeRun: { runId: "run-active" },
    latestRun: null,
    needsInputRequest: null,
    reviewPackage: null,
    approvedStrategy: null,
    marketingBrief: null,
    xiaohongshuBrief: null,
  };
  const recoveryTask = {
    ...task,
    taskId: "task-recovery",
    taskName: "Recovery task",
    taskStatus: "failed",
    activeRun: null,
    latestRun: { runId: "run-latest" },
    needsInputRequest: null,
    reviewPackage: null,
    approvedStrategy: null,
    marketingBrief: null,
    xiaohongshuBrief: null,
  };
  const tasks = new Map([
    [task.taskId, task],
    [activeRunTask.taskId, activeRunTask],
    [recoveryTask.taskId, recoveryTask],
  ]);
  const requestPaths: string[] = [];
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (
      message.type() === "error" &&
      !message.text().includes(missingCurrentResultStatus)
    ) {
      consoleErrors.push(message.text());
    }
  });
  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    requestPaths.push(`${route.request().method()} ${url.pathname}`);
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }
    const taskId = url.pathname.split("/").pop() ?? "";
    const selected = tasks.get(decodeURIComponent(taskId));
    if (selected) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(selected),
      });
      return;
    }
    await route.abort();
  });

  await page.goto("/tasks/task%2F7?panel=intake&stage=product_positioning");
  await expect(page.getByRole("heading", { name: "当前工作区" })).toBeVisible();
  await expect(page.getByText("资料已准备好，可以保存。")).toBeVisible();

  await page.goto(
    "/tasks/task-active?panel=progress&stage=product_positioning",
  );
  await expect(page.getByRole("heading", { name: "当前工作区" })).toBeVisible();
  await expect(page.getByText("处理中").first()).toBeVisible();
  const activeRunPanel = page.getByRole("region", { name: "正在处理" });
  await activeRunPanel.getByText("技术详情", { exact: true }).click();
  await expect(page.getByText("run-active")).toBeVisible();

  await page.goto(
    "/tasks/task-recovery?panel=progress&stage=product_positioning",
  );
  await expect(page.getByRole("heading", { name: "当前工作区" })).toBeVisible();
  await expect(page.getByText("需要恢复").first()).toBeVisible();
  const recoveryReferences = page
    .getByRole("heading", { name: "当前引用" })
    .locator("..")
    .locator("details");
  await recoveryReferences.getByText("技术详情", { exact: true }).click();
  await expect(page.getByText("run-latest")).toBeVisible();

  expect(requestPaths).toEqual([
    "GET /api/v1/tasks/task%2F7",
    "GET /api/v1/tasks/task%2F7/current-result",
    "GET /api/v1/tasks/task-active",
    "GET /api/v1/tasks/task-active/current-result",
    "GET /api/v1/tasks/task-recovery",
    "GET /api/v1/tasks/task-recovery/current-result",
  ]);
  expect(requestPaths.some((path) => path.includes("/commands/"))).toBe(false);
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test("renders long reference identities as literal text without overflow or execution", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 800 });
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  const requestPaths: string[] = [];
  const marker = '<img src=x onerror="window.__shellInjected=1">';
  const reference = (label: string) => `${marker}${label}${"x".repeat(260)}`;
  const references = {
    activeRunId: reference("active-run"),
    latestRunId: reference("latest-run"),
    needsInputResourceId: reference("needs-input"),
    reviewPackageId: reference("review-package"),
    strategyVersionId: reference("strategy"),
    marketingVersionId: reference("marketing"),
    xiaohongshuVersionId: reference("xiaohongshu"),
  };
  const longReferenceTask = {
    ...task,
    taskId: "task-long-references",
    taskName: "Long references",
    taskStatus: "waiting_for_input",
    activeRun: { runId: references.activeRunId },
    latestRun: { runId: references.latestRunId },
    needsInputRequest: {
      resourceId: references.needsInputResourceId,
      revision: 5,
    },
    reviewPackage: {
      reviewPackageId: references.reviewPackageId,
      packageVersion: 2,
    },
    approvedStrategy: {
      resourceKind: "strategy",
      resourceVersionId: references.strategyVersionId,
      versionNumber: 3,
    },
    marketingBrief: {
      resourceKind: "marketing_brief",
      resourceVersionId: references.marketingVersionId,
      versionNumber: 4,
    },
    xiaohongshuBrief: {
      resourceKind: "xiaohongshu_brief",
      resourceVersionId: references.xiaohongshuVersionId,
      versionNumber: 5,
    },
  };

  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (
      message.type() === "error" &&
      !message.text().includes(missingCurrentResultStatus)
    ) {
      consoleErrors.push(message.text());
    }
  });
  await page.addInitScript(() => {
    (window as unknown as { __shellInjected?: boolean }).__shellInjected =
      false;
  });
  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    requestPaths.push(`${route.request().method()} ${url.pathname}`);
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }
    if (url.pathname === "/api/v1/tasks/task-long-references") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(longReferenceTask),
      });
      return;
    }
    await route.abort();
  });

  await page.goto(
    "/tasks/task-long-references?panel=evidence&stage=product_positioning",
  );
  await expect(
    page.getByRole("heading", { name: "Long references" }),
  ).toBeVisible();
  const context = page.getByRole("complementary", {
    name: "上下文与执行信息",
  });
  await context.locator(":scope > details > summary").click();
  const referenceDetails = context
    .getByRole("heading", { name: "当前引用" })
    .locator("..")
    .locator("details");
  await referenceDetails.getByText("技术详情", { exact: true }).click();

  const expectedReferenceText = [
    references.activeRunId,
    references.latestRunId,
    `${references.needsInputResourceId} · revision 5`,
    `${references.reviewPackageId} · version 2`,
    `strategy: ${references.strategyVersionId} · version 3`,
    `marketing_brief: ${references.marketingVersionId} · version 4`,
    `xiaohongshu_brief: ${references.xiaohongshuVersionId} · version 5`,
  ];
  for (const value of expectedReferenceText) {
    await expect(page.getByText(value, { exact: true })).toBeVisible();
  }

  await page.waitForTimeout(50);
  const dimensions = await page.evaluate(() => ({
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    bodyClientWidth: document.body.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }));
  expect(dimensions.documentScrollWidth).toBe(dimensions.documentClientWidth);
  expect(dimensions.bodyScrollWidth).toBe(dimensions.bodyClientWidth);

  expect(
    await page.evaluate(
      () =>
        (window as unknown as { __shellInjected?: boolean }).__shellInjected,
    ),
  ).toBe(false);
  expect(
    await page.evaluate((payloadMarker) => {
      const executableNodes = Array.from(
        document.querySelectorAll("img, [onerror], [onclick]"),
      );
      const scriptsWithPayload = Array.from(document.scripts).some((script) =>
        script.textContent?.includes(payloadMarker),
      );
      return executableNodes.length === 0 && !scriptsWithPayload;
    }, marker),
  ).toBe(true);

  const evidenceLink = page.getByRole("link", {
    name: "证据",
    exact: true,
  });
  await page.keyboard.press("Tab");
  await evidenceLink.focus();
  await expect(evidenceLink).toBeFocused();
  expect(
    await evidenceLink.evaluate(
      (element) => getComputedStyle(element).outlineStyle,
    ),
  ).not.toBe("none");

  expect(requestPaths).toEqual([
    "GET /api/v1/tasks/task-long-references",
    "GET /api/v1/tasks/task-long-references/current-result",
  ]);
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test("reflows long Task values without page-level horizontal overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 800 });
  const longValue = "x".repeat(300);
  const longTask = {
    ...task,
    taskId: "task-1",
    taskName: longValue,
    productCategory: longValue,
  };

  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }
    if (url.pathname === "/api/v1/tasks") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [longTask], limit: 20 }),
      });
      return;
    }
    if (url.pathname === "/api/v1/tasks/task-1") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(longTask),
      });
      return;
    }
    await route.abort();
  });

  await page.goto("/tasks");
  const recentTasks = page.getByRole("region", { name: "最近任务" });
  await expect(
    recentTasks.getByRole("link", { name: longValue }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth <=
        document.documentElement.clientWidth,
    ),
  ).toBe(true);

  await recentTasks.getByRole("link", { name: longValue }).click();
  await expect(page).toHaveURL(/\/tasks\/task-1$/);
  await expect(
    page
      .locator('section[aria-labelledby="task-workbench-heading"]')
      .getByRole("heading", { name: longValue }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth <=
        document.documentElement.clientWidth,
    ),
  ).toBe(true);
});

test("keeps the Context Rail visible wide and collapsible in-flow at narrow widths", async ({
  page,
}) => {
  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }
    if (decodeURIComponent(url.pathname) === "/api/v1/tasks/task/7") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(task),
      });
      return;
    }
    await route.abort();
  });

  const context = page.getByRole("complementary", {
    name: "上下文与执行信息",
  });
  const contextDetails = context.locator(":scope > details");
  const contextSummary = context.locator(":scope > details > summary");

  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/tasks/task%2F7?panel=progress&stage=product_positioning");
  await expect(contextDetails).toHaveAttribute("open", "");
  await expect(context.getByText("当前任务", { exact: true })).toBeVisible();
  expect(
    await page
      .locator('[class*="workbenchGrid"] > *')
      .evaluateAll((elements) =>
        elements.map(
          (element) =>
            element.getAttribute("aria-label") ??
            element.getAttribute("aria-labelledby"),
        ),
      ),
  ).toEqual(["active-workspace-heading", "上下文与执行信息"]);

  for (const width of [1024, 320]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/tasks/task%2F7?panel=progress&stage=product_positioning");
    await expect(contextDetails).not.toHaveAttribute("open", "");
    expect(
      await page
        .locator('[class*="workbenchGrid"] > *')
        .evaluateAll((elements) =>
          elements.map(
            (element) =>
              element.getAttribute("aria-label") ??
              element.getAttribute("aria-labelledby"),
          ),
        ),
    ).toEqual(["上下文与执行信息", "active-workspace-heading"]);
    await contextSummary.focus();
    await expect(contextSummary).toBeFocused();
    await contextSummary.click();
    await expect(contextDetails).toHaveAttribute("open", "");
    await expect(context.getByText("当前任务", { exact: true })).toBeVisible();
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth <=
          document.documentElement.clientWidth,
      ),
    ).toBe(true);
  }
});

test("captures Running Review Results visual evidence with reflow and keyboard proof", async ({
  page,
}) => {
  const visualResult = {
    taskId: "task-visual-review",
    resultRevision: 5,
    inputRevision: 1,
    status: "awaiting_review",
    generatedAt: "2026-08-12T00:00:00Z",
    missingInformation: [],
    productIntake: { facts: ["约 18 升"] },
    customerInsight: {
      customer_insights: [{ statement: "工作日城市通勤需要有序携带" }],
    },
    productPositioning: {
      positioning_candidates: [
        {
          candidate_title: "城市通勤的清晰收纳方案",
          target_segment: "工作日城市通勤者",
          value_proposition: "用清晰收纳支持日常通勤携带",
          proof_points: [{ statement: "可放入 14 英寸级别笔记本电脑" }],
          evidence_limitations: ["没有真实用户研究"],
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
          evidence_limitations: ["合成资料，不代表真实用户研究"],
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
      },
    },
    confirmation: null,
  };
  const confirmedVisualResult = {
    ...visualResult,
    taskId: "task-visual-results",
    status: "confirmed",
    confirmation: {
      marketingBriefVersion: {
        resourceKind: "marketing_brief",
        resourceVersionId: "visual-marketing",
        versionNumber: 1,
      },
      xiaohongshuBriefVersion: {
        resourceKind: "xiaohongshu_brief",
        resourceVersionId: "visual-xiaohongshu",
        versionNumber: 1,
      },
      confirmedAt: "2026-08-12T00:00:00Z",
    },
  };
  const visualTasks = new Map([
    [
      "task-visual-running",
      {
        ...task,
        taskId: "task-visual-running",
        activeRun: { runId: "run-visual" },
      },
    ],
    [
      "task-visual-review",
      {
        ...task,
        taskId: "task-visual-review",
        activeRun: null,
        reviewPackage: { reviewPackageId: "visual-review", packageVersion: 1 },
      },
    ],
    [
      "task-visual-results",
      {
        ...task,
        taskId: "task-visual-results",
        activeRun: null,
        reviewPackage: null,
        marketingBrief: {
          resourceKind: "marketing_brief",
          resourceVersionId: "visual-marketing",
          versionNumber: 1,
        },
        xiaohongshuBrief: {
          resourceKind: "xiaohongshu_brief",
          resourceVersionId: "visual-xiaohongshu",
          versionNumber: 1,
        },
      },
    ],
  ]);
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    const path = decodeURIComponent(url.pathname);
    const taskId = path.split("/").at(-1) ?? "";
    if (path.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    if (path.endsWith("/current-result")) {
      const resultTaskId = path.split("/").at(-2) ?? "";
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          resultTaskId === "task-visual-results"
            ? confirmedVisualResult
            : visualResult,
        ),
      });
      return;
    }
    const selected = visualTasks.get(taskId);
    if (selected === undefined) {
      await route.abort();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(selected),
    });
  });

  const states = [
    {
      name: "running",
      taskId: "task-visual-running",
      panel: "progress",
      stage: "product_positioning",
      heading: "正在处理",
    },
    {
      name: "review",
      taskId: "task-visual-review",
      panel: "review",
      stage: "human_review",
      heading: "审核候选结果",
    },
    {
      name: "results",
      taskId: "task-visual-results",
      panel: "results",
      stage: "marketing_brief_generation",
      heading: "结果已就绪",
    },
  ] as const;
  for (const state of states) {
    for (const width of [1280, 1024, 320]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(
        `/tasks/${state.taskId}?panel=${state.panel}&stage=${state.stage}`,
      );
      await expect(
        page.getByRole("heading", { name: state.heading }),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () =>
            document.documentElement.scrollWidth <=
            document.documentElement.clientWidth,
        ),
      ).toBe(true);
      expect(
        await page.evaluate(
          () =>
            globalThis.matchMedia("(prefers-reduced-motion: reduce)").matches,
        ),
      ).toBe(true);
      await page.screenshot({
        path: `test-results/issue305/${state.name}-${width}.png`,
        fullPage: true,
      });
    }
  }
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto(
    "/tasks/task-visual-results?panel=results&stage=marketing_brief_generation",
  );
  const resultTabs = page.getByRole("tablist", { name: "结果视图" });
  const marketingTab = resultTabs.getByRole("tab", { name: "营销 Brief" });
  const xiaohongshuTab = resultTabs.getByRole("tab", {
    name: "小红书 Brief",
  });
  await marketingTab.focus();
  await expect(marketingTab).toBeFocused();
  await page.keyboard.press("ArrowRight");
  await expect(xiaohongshuTab).toBeFocused();
  await expect(xiaohongshuTab).toHaveAttribute("aria-selected", "true");
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test("creates a Task through the generated HTTP client and reuses its key on explicit retry", async ({
  page,
}) => {
  const createdTask = {
    ...task,
    taskId: "task/e2e created",
    taskName: "City launch",
    productCategory: "Backpack",
  };
  const createRequests: Array<{ body: unknown; key: string | undefined }> = [];
  const requestPaths: string[] = [];
  let createAttempts = 0;
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (
      message.type() === "error" &&
      !message.text().includes("status of 503 (Service Unavailable)") &&
      !message.text().includes(missingCurrentResultStatus)
    ) {
      consoleErrors.push(message.text());
    }
  });

  await page.route("**/api/v1/tasks**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    requestPaths.push(url.pathname);
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }

    if (request.method() === "POST" && url.pathname === "/api/v1/tasks") {
      createAttempts += 1;
      createRequests.push({
        body: JSON.parse(request.postData() ?? "null"),
        key: request.headers()["idempotency-key"],
      });
      if (createAttempts === 1) {
        await route.fulfill({
          status: 503,
          contentType: "application/problem+json",
          body: JSON.stringify({ detail: "private temporary detail" }),
        });
      } else {
        await route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify(createdTask),
        });
      }
      return;
    }
    if (request.method() === "GET" && url.pathname === "/api/v1/tasks") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [], limit: 20 }),
      });
      return;
    }
    if (
      request.method() === "GET" &&
      decodeURIComponent(url.pathname) === `/api/v1/tasks/${createdTask.taskId}`
    ) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(createdTask),
      });
      return;
    }
    await route.abort();
  });

  await page.goto("/tasks/new");
  await page.getByLabel("Task name").fill("  City launch  ");
  await page.getByLabel("Product category").fill(" Backpack ");
  await page.getByLabel("Promotion goal").fill(" awareness ");
  await page.getByRole("button", { name: "Create task" }).click();

  await expect(page.getByRole("alert")).toContainText(
    "Your entries are preserved",
  );
  await expect(page.getByLabel("Task name")).toHaveValue("  City launch  ");
  await page.getByRole("button", { name: "Retry create" }).click();

  await expect(page).toHaveURL(/\/tasks\/task%2Fe2e%20created$/);
  await expect(
    page.getByRole("heading", { name: "City launch" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "City launch" }),
  ).toBeVisible();

  expect(createRequests).toHaveLength(2);
  expect(createRequests[0]?.body).toEqual({
    taskName: "City launch",
    productCategory: "Backpack",
    promotionGoal: "awareness",
  });
  expect(createRequests[1]?.body).toEqual(createRequests[0]?.body);
  expect(createRequests[0]?.key).toBeTruthy();
  expect(createRequests[1]?.key).toBe(createRequests[0]?.key);
  expect(page.getByText(createRequests[0]?.key ?? "missing-key")).toHaveCount(
    0,
  );
  expect(requestPaths.some((path) => path.includes("/commands/"))).toBe(false);
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test("reuses the same key after a malformed-success response and rotates it only after input changes", async ({
  page,
}) => {
  const createdTask = {
    ...task,
    taskId: "task/malformed",
    taskName: "City launch",
    productCategory: "Tote",
  };
  const createRequests: Array<{ body: unknown; key: string | undefined }> = [];
  let createAttempts = 0;

  await page.route("**/api/v1/tasks**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname.endsWith("/primary-input")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(primaryInput),
      });
      return;
    }
    if (url.pathname.endsWith("/current-result")) {
      await route.fulfill({
        status: 404,
        contentType: "application/problem+json",
        body: JSON.stringify(missingCurrentResult(url.pathname)),
      });
      return;
    }
    if (request.method() === "POST" && url.pathname === "/api/v1/tasks") {
      createAttempts += 1;
      createRequests.push({
        body: JSON.parse(request.postData() ?? "null"),
        key: request.headers()["idempotency-key"],
      });
      if (createAttempts < 3) {
        await route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({}),
        });
      } else {
        await route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify(createdTask),
        });
      }
      return;
    }
    if (request.method() === "GET" && url.pathname === "/api/v1/tasks") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [], limit: 20 }),
      });
      return;
    }
    if (
      request.method() === "GET" &&
      decodeURIComponent(url.pathname) === "/api/v1/tasks/task/malformed"
    ) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(createdTask),
      });
      return;
    }
    await route.abort();
  });

  await page.goto("/tasks/new");
  await page.getByLabel("Task name").fill("Launch");
  await page.getByLabel("Product category").fill("Backpack");
  await page.getByLabel("Promotion goal").fill("Awareness");

  await page.getByRole("button", { name: "Create task" }).click();
  await expect(page.getByRole("alert")).toContainText("could not be completed");
  await page.getByRole("button", { name: "Retry create" }).click();
  await expect(page.getByRole("alert")).toContainText("could not be completed");

  await page.getByLabel("Product category").fill("Tote");
  await page.getByRole("button", { name: "Retry create" }).click();
  await expect(page).toHaveURL(/\/tasks\/task%2Fmalformed$/);
  await expect(
    page.getByRole("heading", { name: "City launch" }),
  ).toBeVisible();

  expect(createRequests).toHaveLength(3);
  expect(createRequests[0]?.key).toBeTruthy();
  expect(createRequests[1]?.key).toBe(createRequests[0]?.key);
  expect(createRequests[2]?.key).toBeTruthy();
  expect(createRequests[2]?.key).not.toBe(createRequests[0]?.key);
  expect(createRequests[0]?.body).toEqual({
    taskName: "Launch",
    productCategory: "Backpack",
    promotionGoal: "Awareness",
  });
  expect(createRequests[1]?.body).toEqual(createRequests[0]?.body);
  expect(createRequests[2]?.body).toEqual({
    taskName: "Launch",
    productCategory: "Tote",
    promotionGoal: "Awareness",
  });
  expect(page.getByText(createRequests[0]?.key ?? "missing-key")).toHaveCount(
    0,
  );
});
