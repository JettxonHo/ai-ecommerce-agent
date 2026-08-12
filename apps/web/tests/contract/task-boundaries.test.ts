import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const sourceRoot = resolve(import.meta.dirname, "../../src/tasks");
const read = (file: string) => readFileSync(resolve(sourceRoot, file), "utf8");

describe("private Task gateway boundaries", () => {
  it("keeps the exact three-method private seam and no framework dependencies", () => {
    const gateway = read("gateway.ts");
    expect(gateway).toContain("export interface TaskGateway");
    expect(gateway).toContain("listTasks(): Promise<readonly TaskSummary[]>");
    expect(gateway).toContain(
      "createTask(input: TaskInput, idempotencyKey: string): Promise<TaskOverview>",
    );
    expect(gateway).toContain(
      "getTaskOverview(taskId: string): Promise<TaskOverview>",
    );
    expect(gateway).not.toMatch(
      /React|react-router|@tanstack\/react-query|openapi-fetch/,
    );
    expect(gateway).not.toMatch(/\bfetch\s*\(/);
    expect(gateway).not.toMatch(/\bResponse\b/);
  });

  it("keeps HTTP transport on the generated ApiClient and forbids a third transport", () => {
    const http = read("httpGateway.ts");
    const deterministic = read("deterministicGateway.ts");
    expect(http).toContain('client.GET("/api/v1/tasks"');
    expect(http).toContain('client.POST("/api/v1/tasks"');
    expect(http).toContain('client.GET("/api/v1/tasks/{taskId}"');
    expect(http).not.toMatch(/\bfetch\s*\(/);
    expect(http).not.toContain("openapi-fetch");
    expect(deterministic).not.toMatch(/\bfetch\s*\(/);
    expect(deterministic).not.toContain("openapi-fetch");
    expect(deterministic).not.toContain("@tanstack/react-query");
  });

  it("keeps production composition free of import-time I/O and a third transport", () => {
    const http = read("httpGateway.ts");
    const deterministic = read("deterministicGateway.ts");
    expect(http).not.toMatch(/\bglobalThis\.(fetch|window|document)\b/);
    expect(http).not.toContain("createDeterministicTaskGateway");
    expect(deterministic).not.toMatch(
      /\bglobalThis\.(fetch|window|document)\b/,
    );
  });
});
