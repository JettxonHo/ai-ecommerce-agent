import { expect, test } from "@playwright/test";

test.skip(
  process.env.MVP0_RUN_REAL_BACKEND_E2E !== "1",
  "set MVP0_RUN_REAL_BACKEND_E2E=1 with the local FastAPI/PostgreSQL server",
);

test("creates a Task and persists primary input through the real backend", async ({
  page,
}) => {
  const input =
    "fixture-sufficient-v1 fictional synthetic non-regulated\n" +
    "anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包\n" +
    "工作日城市通勤时携带电脑、文件和日常随身物品，约 18 升，" +
    "可放入 14 英寸级别笔记本电脑。\n" +
    "表面有防泼水处理。source-sufficient-product-v1 product.json direct_source。";

  await page.goto("/tasks");
  await page.getByRole("link", { name: "Create a task" }).click();
  await page.getByLabel("Task name").fill("Chromium persisted intake");
  await page.getByLabel("Product category").fill("Backpack");
  await page.getByLabel("Promotion goal").fill("Urban commuter positioning");
  await page.getByRole("button", { name: "Create task" }).click();

  await expect(page).toHaveURL(/\/tasks\/[^/]+$/);
  await expect(
    page.getByRole("heading", { name: "Current workspace: intake" }),
  ).toBeVisible();
  await page.getByLabel("Pasted text").fill(input);
  await page.getByRole("button", { name: "Save primary input" }).click();
  await expect(
    page.getByText("Saved revision 0.", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Saved input preview" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Saved input preview" }).getByText(input),
  ).toBeVisible();

  await page.getByRole("button", { name: "Generate result" }).click();
  await expect(
    page.getByRole("heading", { name: "Current result" }),
  ).toBeVisible();
  await expect(
    page.getByText("awaiting_review", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Marketing Brief" }),
  ).toBeVisible();

  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Chromium persisted intake" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Intake", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Saved input preview" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Saved input preview" }).getByText(input),
  ).toBeVisible();
  await page.getByRole("link", { name: "Results", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Current result" }),
  ).toBeVisible();
  await expect(
    page.getByText("awaiting_review", { exact: true }),
  ).toBeVisible();
});

test("confirms current result and downloads both immutable Markdown exports", async ({
  page,
}) => {
  const input =
    "fixture-sufficient-v1 fictional synthetic non-regulated\n" +
    "anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包\n" +
    "工作日城市通勤时携带电脑、文件和日常随身物品，约 18 升，可放入 14 英寸级别笔记本电脑。\n" +
    "表面有防泼水处理。source-sufficient-product-v1 product.json direct_source。";

  await page.goto("/tasks");
  await page.getByRole("link", { name: "Create a task" }).click();
  await page.getByLabel("Task name").fill("Chromium review export");
  await page.getByLabel("Product category").fill("Backpack");
  await page.getByLabel("Promotion goal").fill("Review export");
  await page.getByRole("button", { name: "Create task" }).click();
  await page.getByLabel("Pasted text").fill(input);
  await page.getByRole("button", { name: "Save primary input" }).click();
  await page.getByRole("button", { name: "Generate result" }).click();
  await expect(
    page.getByText("awaiting_review", { exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Review", exact: true }).click();
  await expect(page).toHaveURL(/panel=review/);
  await expect(
    page.getByRole("heading", { name: "Review current result" }),
  ).toBeVisible();
  await page
    .getByLabel("Marketing core message")
    .fill("Chromium confirmed commuter message");
  await page
    .getByLabel("Xiaohongshu title direction")
    .fill("Chromium confirmed commuter title");
  await page.getByRole("button", { name: "Confirm current result" }).click();
  await page.getByRole("link", { name: "Results", exact: true }).click();
  await expect(page.getByText("confirmed", { exact: true })).toBeVisible();
  const marketingDownload = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Download Marketing Markdown" })
    .click();
  expect((await marketingDownload).suggestedFilename()).toMatch(
    /marketing.*\.md$/u,
  );
  const xhsDownload = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Download Xiaohongshu Markdown" })
    .click();
  expect((await xhsDownload).suggestedFilename()).toMatch(
    /xiaohongshu.*\.md$/u,
  );
});
