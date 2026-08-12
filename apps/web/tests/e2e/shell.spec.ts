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
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "City launch" }),
  ).toBeVisible();
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
