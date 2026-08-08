import { expect, test } from "@playwright/test";

test("renders the shell without page or console errors", async ({ page }) => {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];

  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });

  await page.goto("/");

  await expect(page).toHaveTitle("AI Ecommerce Agent");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "AI Ecommerce Agent",
  );
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});
