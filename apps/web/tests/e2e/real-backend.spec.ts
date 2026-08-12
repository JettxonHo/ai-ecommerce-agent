import { expect, test } from "@playwright/test";

test.skip(
  process.env.MVP0_RUN_REAL_BACKEND_E2E !== "1",
  "set MVP0_RUN_REAL_BACKEND_E2E=1 with the local FastAPI/PostgreSQL server",
);

test("creates a Task and persists primary input through the real backend", async ({
  page,
}) => {
  const input =
    "City commute backpack for weekday transit: lightweight recycled nylon, " +
    "separate laptop sleeve, weather-resistant zippers, and comfortable straps. " +
    "Position the product for practical urban commuters who need quick access " +
    "without sacrificing a clean silhouette.";

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

  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Chromium persisted intake" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Saved input preview" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Saved input preview" }).getByText(input),
  ).toBeVisible();
});
