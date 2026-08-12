import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const sourceRoot = resolve(import.meta.dirname, "../../src");
const read = (file: string) => readFileSync(resolve(sourceRoot, file), "utf8");

describe("read-only Task route boundaries", () => {
  it("keeps the exact outer route inventory and excludes create behavior", () => {
    const app = read("App.tsx");
    const paths = [...app.matchAll(/<Route\s+path="([^"]+)"/g)].map(
      (match) => match[1],
    );

    expect(paths).toEqual(["/", "/tasks", "/tasks/:taskId", "*"]);
    expect(app).not.toContain('path="/tasks/new"');
    expect(app).not.toContain("createTask");
  });

  it("keeps the route module on the private gateway and Query seam", () => {
    const routes = read("tasks/TaskRoutes.tsx");

    expect(routes).toContain("useQuery");
    expect(routes).toContain('["tasks", "recent"]');
    expect(routes).toContain('["tasks", "overview", taskId]');
    expect(routes).toContain("type TaskGateway");
    expect(routes).not.toMatch(/generated\/schema|\bfetch\s*\(|openapi-fetch/);
    expect(routes).not.toMatch(/dangerouslySetInnerHTML|innerHTML/);
    expect(routes).not.toMatch(
      /\b(useState|useReducer|localStorage|sessionStorage)\b/,
    );
  });

  it("composes production HTTP only and keeps deterministic transport in tests", () => {
    const main = read("main.tsx");
    const appTest = read("App.test.tsx");
    const shellTest = read("../tests/contract/shell-no-network.test.tsx");

    expect(main).toContain("createHttpTaskGateway(createApiClient())");
    expect(main).not.toContain("createDeterministicTaskGateway");
    expect(appTest).toContain("createDeterministicTaskGateway");
    expect(shellTest).toContain("createDeterministicTaskGateway");
  });
});
