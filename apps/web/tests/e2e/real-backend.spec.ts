import { readFile } from "node:fs/promises";

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
  await expect(page.getByRole("heading", { name: "结果已就绪" })).toBeVisible();
  await expect(page.getByText("待审核", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "营销 Brief" })).toBeVisible();

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
  await expect(page.getByRole("heading", { name: "结果已就绪" })).toBeVisible();
  await expect(page.getByText("待审核", { exact: true })).toBeVisible();
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
  await expect(page.getByText("待审核", { exact: true })).toBeVisible();
  await page.getByRole("link", { name: "Review", exact: true }).click();
  await expect(page).toHaveURL(/panel=review/);
  await expect(
    page.getByRole("heading", { name: "审核候选结果" }),
  ).toBeVisible();
  await page.setViewportSize({ width: 320, height: 900 });
  const viewport = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(viewport.scrollWidth).toBeLessThanOrEqual(viewport.clientWidth);
  const marketingCorrection =
    "# Confirmed heading [safe link](https://example.test) <strong>literal</strong> ``ticks``";
  const xiaohongshuCorrection =
    "# Title [safe link](https://example.test) <em>literal</em> ``ticks``";
  await page.getByLabel("营销核心信息").fill(marketingCorrection);
  await page.getByLabel("小红书标题方向").fill(xiaohongshuCorrection);
  await page.getByLabel("营销核心信息").focus();
  expect(await page.evaluate(() => document.activeElement?.id)).toBe(
    "review-marketing-message",
  );
  await page.getByRole("button", { name: "确认并生成结果" }).click();
  await expect(page).toHaveURL(/panel=results/u);
  await expect(page.getByText("已确认", { exact: true })).toBeVisible();
  const resultRegion = page.getByRole("region", { name: "结果已就绪" });
  await resultRegion.getByText("技术细节", { exact: true }).click();
  await expect(
    page.locator("pre").filter({ hasText: marketingCorrection }),
  ).toBeVisible();
  await expect(
    page.locator("pre").filter({ hasText: xiaohongshuCorrection }),
  ).toBeVisible();

  const assertDownload = async (
    buttonName: string,
    kind: "marketing" | "xiaohongshu",
    expected: string,
  ) => {
    const downloadEvent = page.waitForEvent("download");
    await page.getByRole("button", { name: buttonName }).click();
    const download = await downloadEvent;
    const path = await download.path();
    expect(path).not.toBeNull();
    const bytes = await readFile(path as string);
    expect(bytes.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf]))).toBe(
      false,
    );
    const content = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    expect(content).toContain(expected);
    expect(content.endsWith("\n")).toBe(true);
    expect(content.endsWith("\n\n")).toBe(false);
    expect(download.suggestedFilename()).toMatch(
      new RegExp(`${kind}-v1-\\d{8}T\\d{6}Z\\.md$`, "u"),
    );
  };
  await assertDownload("导出营销 Markdown", "marketing", marketingCorrection);
  await assertDownload(
    "导出小红书 Markdown",
    "xiaohongshu",
    xiaohongshuCorrection,
  );

  await page.reload();
  await expect(page.getByText("已确认", { exact: true })).toBeVisible();
  const reloadedResultRegion = page.getByRole("region", { name: "结果已就绪" });
  await reloadedResultRegion.getByText("技术细节", { exact: true }).click();
  await expect(
    page.locator("pre").filter({ hasText: marketingCorrection }),
  ).toBeVisible();
  await expect(
    page.locator("pre").filter({ hasText: xiaohongshuCorrection }),
  ).toBeVisible();
});

test("does not expose review or export actions for an insufficient result", async ({
  page,
}) => {
  await page.goto("/tasks");
  await page.getByRole("link", { name: "Create a task" }).click();
  await page.getByLabel("Task name").fill("Chromium insufficient result");
  await page.getByLabel("Product category").fill("Backpack");
  await page.getByLabel("Promotion goal").fill("Insufficient fixture");
  await page.getByRole("button", { name: "Create task" }).click();
  await page.getByLabel("Pasted text").fill("fixture-insufficient-v1 only");
  await page.getByRole("button", { name: "Save primary input" }).click();
  await page.getByRole("button", { name: "Generate result" }).click();

  await expect(
    page.getByRole("heading", { name: "需要补充资料" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "确认并生成结果" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "导出营销 Markdown" }),
  ).toHaveCount(0);
  await page.getByRole("link", { name: "Review", exact: true }).click();
  await expect(page.getByRole("heading", { name: "审核候选结果" })).toHaveCount(
    0,
  );
  await expect(
    page.getByRole("button", { name: "确认并生成结果" }),
  ).toHaveCount(0);
});
