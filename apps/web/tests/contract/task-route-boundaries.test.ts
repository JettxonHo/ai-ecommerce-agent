import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const sourceRoot = resolve(import.meta.dirname, "../../src");
const read = (file: string) => readFileSync(resolve(sourceRoot, file), "utf8");

describe("Task route boundaries", () => {
  it("keeps the exact outer route inventory and excludes workflow actions", () => {
    const app = read("App.tsx");
    const create = read("tasks/NewTaskRoute.tsx");
    const paths = [...app.matchAll(/<Route\s+path="([^"]+)"/g)].map(
      (match) => match[1],
    );

    expect(paths).toEqual(["/", "/tasks", "/tasks/new", "/tasks/:taskId", "*"]);
    expect(app).toContain('path="/tasks/new"');
    expect(app).toContain("NewTaskRoute");
    expect(create).toContain("type TaskGateway");
    expect(create).toContain("taskGateway.createTask(input, key)");
    expect(create).not.toMatch(/commands\/start|startTask|runTask|\.run\(/);
    expect(create).not.toMatch(/generated\/schema|openapi-fetch|\bfetch\s*\(/);
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
