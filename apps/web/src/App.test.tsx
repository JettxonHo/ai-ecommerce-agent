import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("foundation shell", () => {
  it("renders an accessible main heading under the application providers", () => {
    const queryClient = new QueryClient();

    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </BrowserRouter>,
    );

    expect(screen.getByRole("main")).toBeTruthy();
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe(
      "AI Ecommerce Agent",
    );
  });
});
