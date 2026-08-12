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

test("renders recent tasks and restores a stable deep link without errors", async ({
  page,
}) => {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];

  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });

  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
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

  await expect(page).toHaveTitle("AI Ecommerce Agent");
  await expect(page).toHaveURL(/\/tasks$/);
  await expect(
    page.getByRole("heading", { name: "Recent tasks" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "City launch" }).click();
  await expect(page).toHaveURL(/\/tasks\/task%2F7$/);
  await expect(
    page.getByRole("heading", { name: "City launch" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Current workspace: intake" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Intake", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await page.getByRole("link", { name: "Progress" }).click();
  await expect(page).toHaveURL(
    /\/tasks\/task%2F7\?panel=progress&stage=product_positioning$/,
  );
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "City launch" }),
  ).toBeVisible();
  await expect(page).toHaveURL(
    /\/tasks\/task%2F7\?panel=progress&stage=product_positioning$/,
  );
  await expect(
    page.getByRole("link", { name: "Progress", exact: true }),
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
    requestPaths.push(`${route.request().method()} ${url.pathname}`);
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
    "GET /api/v1/tasks/task%2F7",
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
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  await page.route("**/api/v1/tasks**", async (route) => {
    const url = new URL(route.request().url());
    requestPaths.push(`${route.request().method()} ${url.pathname}`);
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
  await expect(
    page.getByRole("heading", { name: "Current workspace: intake" }),
  ).toBeVisible();
  await expect(
    page.getByText(/Intake resources and actions are not implemented/),
  ).toBeVisible();

  await page.goto(
    "/tasks/task-active?panel=progress&stage=product_positioning",
  );
  await expect(
    page.getByRole("heading", { name: "Current workspace: running" }),
  ).toBeVisible();
  await expect(page.getByText("run-active")).toBeVisible();

  await page.goto(
    "/tasks/task-recovery?panel=progress&stage=product_positioning",
  );
  await expect(
    page.getByRole("heading", { name: "Current workspace: recovery" }),
  ).toBeVisible();
  await expect(page.getByText("run-latest")).toBeVisible();

  expect(requestPaths).toEqual([
    "GET /api/v1/tasks/task%2F7",
    "GET /api/v1/tasks/task-active",
    "GET /api/v1/tasks/task-recovery",
  ]);
  expect(requestPaths.some((path) => path.includes("/commands/"))).toBe(false);
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
  await expect(page.getByRole("link", { name: longValue })).toBeVisible();
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth <=
        document.documentElement.clientWidth,
    ),
  ).toBe(true);

  await page.getByRole("link", { name: longValue }).click();
  await expect(page).toHaveURL(/\/tasks\/task-1$/);
  await expect(page.getByRole("heading", { name: longValue })).toBeVisible();
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth <=
        document.documentElement.clientWidth,
    ),
  ).toBe(true);
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
      !message.text().includes("status of 503 (Service Unavailable)")
    ) {
      consoleErrors.push(message.text());
    }
  });

  await page.route("**/api/v1/tasks**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    requestPaths.push(url.pathname);

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
