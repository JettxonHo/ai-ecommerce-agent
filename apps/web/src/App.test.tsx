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
      await screen.findByRole("heading", { name: "Recent tasks" }),
    ).toBeTruthy();
  });

  it.each(["/", "/unknown", "/tasks/new"])(
    "redirects unsupported location %s to the recent-task entry",
    async (path) => {
      renderAt(path);
      expect(
        await screen.findByRole("heading", { name: "Recent tasks" }),
      ).toBeTruthy();
      expect(screen.queryByText(/create/i)).toBeNull();
    },
  );
});
