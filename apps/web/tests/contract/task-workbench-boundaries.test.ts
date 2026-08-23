import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const sourceRoot = resolve(import.meta.dirname, "../../src/tasks");
const read = (file: string) => readFileSync(resolve(sourceRoot, file), "utf8");

describe("TaskWorkbench boundaries", () => {
  it("keeps the route thin and makes Workbench the sole projection consumer", () => {
    const routes = read("TaskRoutes.tsx");
    const workbench = read("workbench/TaskWorkbench.tsx");

    expect(routes).toContain(
      'import { TaskWorkbench } from "./workbench/TaskWorkbench"',
    );
    const workbenchConsumers = routes.match(/<TaskWorkbench\b/g) ?? [];
    expect(workbenchConsumers).toHaveLength(1);
    expect(routes).toContain("task={query.data}");
    expect(routes).not.toMatch(/deriveWorkbenchMode|deriveWorkbenchLocation/);
    expect(workbench).toContain("deriveWorkbenchMode");
    expect(workbench).toContain("deriveWorkbenchLocation");
  });

  it("keeps the shell read-only and private to the Task gateway seam", () => {
    const workbench = read("workbench/TaskWorkbench.tsx");
    const styles = read("workbench/TaskWorkbench.module.css");

    expect(workbench).toContain('from "../gateway"');
    expect(workbench).toContain("NeedsInputActionRequest");
    expect(workbench).toContain("resolveNeedsInput");
    expect(workbench).toContain("allowedResolutionTypes");
    expect(workbench).not.toMatch(/TaskGateway|taskGateway|createTask/);
    expect(workbench).not.toMatch(
      /\b(fetch|localStorage|sessionStorage|window|document|setInterval|setTimeout)\b/,
    );
    expect(workbench).not.toMatch(
      /generated\/schema|openapi-fetch|dangerouslySetInnerHTML|innerHTML/,
    );
    expect(workbench).not.toMatch(/commands?\/|startTask|runTask|poll/);
    expect(workbench).not.toMatch(
      /export \*|export \{[^}]*TaskWorkbench[^}]*\} from/,
    );
    expect(styles).toContain("overflow-wrap: anywhere");
  });

  it("uses one replace navigation only for the projection's canonical search", () => {
    const workbench = read("workbench/TaskWorkbench.tsx");

    expect(workbench).toContain("replaceSearch");
    expect(workbench).toContain("navigate(");
    expect(workbench).toContain("{ replace: true }");
    expect(workbench).toContain("attemptedReplacement");
    expect(workbench).not.toMatch(/window\.history|history\.replaceState/);
  });
});
