import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const sourceRoot = resolve(import.meta.dirname, "../../src/tasks/workbench");
const read = (file: string) => readFileSync(resolve(sourceRoot, file), "utf8");

describe("private Workbench projection boundaries", () => {
  it("is a pure private module over the private Task gateway", () => {
    const projection = read("projection.ts");
    expect(projection).toContain('from "../gateway"');
    expect(projection).not.toMatch(/React|react-router|@tanstack\/react-query/);
    expect(projection).not.toMatch(/generated\/schema|openapi-fetch/);
    expect(projection).not.toMatch(
      /\b(fetch|localStorage|sessionStorage|window|document)\b/,
    );
    expect(projection).not.toMatch(/\b(Date|Math\.random|crypto)\b/);
  });
});
