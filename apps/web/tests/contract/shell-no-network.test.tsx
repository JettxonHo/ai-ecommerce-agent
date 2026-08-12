import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App";
import { createDeterministicTaskGateway } from "../../src/tasks/deterministicGateway";

describe("foundation startup contract", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("does not make a network request while rendering the shell", () => {
    const fetchSpy = vi.fn(() => {
      throw new Error("Network access is disabled in the foundation shell");
    });
    vi.stubGlobal("fetch", fetchSpy);

    render(
      <BrowserRouter>
        <QueryClientProvider client={new QueryClient()}>
          <App taskGateway={createDeterministicTaskGateway()} />
        </QueryClientProvider>
      </BrowserRouter>,
    );

    expect(screen.getByRole("heading", { name: "Recent tasks" })).toBeTruthy();
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
