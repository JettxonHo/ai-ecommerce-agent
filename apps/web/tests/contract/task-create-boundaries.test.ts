import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const sourceRoot = resolve(import.meta.dirname, "../../src");
const readSource = (file: string) =>
  readFileSync(resolve(sourceRoot, file), "utf8");

describe("Task creation boundaries", () => {
  it("uses the private gateway, RHF buffer, and the existing normalizer", () => {
    const source = readSource("tasks/NewTaskRoute.tsx");

    expect(source).toContain('from "react-hook-form"');
    expect(source).toContain("useForm");
    expect(source).toContain("normalizeTaskInput");
    expect(source).toContain("type TaskGateway");
    expect(source).toContain("taskGateway.createTask(input, key)");
    expect(source).not.toMatch(/generated\/schema|openapi-fetch|\bfetch\s*\(/);
    expect(source).not.toMatch(
      /localStorage|sessionStorage|dangerouslySetInnerHTML|innerHTML/,
    );
    expect(source).not.toMatch(/commands\/start|startTask|runTask|\.run\(/);
  });

  it("keeps retry and UUID handling private to the form mutation", () => {
    const source = readSource("tasks/NewTaskRoute.tsx");

    expect(source).toContain("retry: false");
    expect(source).toContain("globalThis.crypto.randomUUID");
    expect(source).toContain('queryKey: ["tasks"]');
    expect(source).toContain("encodeURIComponent(task.taskId)");
    expect(source).toContain("sameInput");
    expect(source).not.toContain("console.");
  });

  it("keeps the package addition exact", () => {
    const packageJson = JSON.parse(
      readFileSync(resolve(import.meta.dirname, "../../package.json"), "utf8"),
    ) as { dependencies: Record<string, string> };
    expect(packageJson.dependencies).toEqual(
      expect.objectContaining({ "react-hook-form": "7.85.0" }),
    );
  });
});
