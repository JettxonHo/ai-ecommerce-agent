import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";
import App from "./App";
import { createDeterministicTaskGateway } from "./tasks/deterministicGateway";

describe("application routes", () => {
  const renderAt = (path: string) => {
    const queryClient = new QueryClient();

    return render(
      <MemoryRouter initialEntries={[path]}>
        <QueryClientProvider client={queryClient}>
          <App taskGateway={createDeterministicTaskGateway()} />
        </QueryClientProvider>
      </MemoryRouter>,
    );
  };

  it("renders the recent-task entry under the application providers", async () => {
    renderAt("/tasks");
    expect(screen.getByRole("main")).toBeTruthy();
    expect(
      await screen.findByRole("heading", { name: "行动首页" }),
    ).toBeTruthy();
  });

  it.each(["/", "/unknown"])(
    "redirects unsupported location %s to the recent-task entry",
    async (path) => {
      renderAt(path);
      expect(
        await screen.findByRole("heading", { name: "行动首页" }),
      ).toBeTruthy();
      expect(
        screen.getByRole("link", { name: "新建商品上新任务" }),
      ).toBeTruthy();
    },
  );

  it("renders the explicit Task creation route", async () => {
    renderAt("/tasks/new");
    expect(
      await screen.findByRole("heading", { name: "Create a task" }),
    ).toBeTruthy();
    expect(screen.getByRole("textbox", { name: "Task name" })).toBeTruthy();
  });
});
