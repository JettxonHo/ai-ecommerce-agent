import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const sourceRoot = resolve(import.meta.dirname, "../../src/needsInput");
const read = (file: string) => readFileSync(resolve(sourceRoot, file), "utf8");

describe("Needs Input private seam boundaries", () => {
  it("keeps the read and typed resolve interface framework-free", () => {
    const gateway = read("gateway.ts");

    expect(gateway).toContain("export interface NeedsInputGateway");
    expect(gateway).toContain("getNeedsInputActionRequest(");
    expect(gateway).toContain("resolveNeedsInput(");
    expect(gateway).toContain("export type NeedsInputResolution");
    expect(gateway).toContain("export type NeedsInputActionRequest");
    expect(gateway).not.toMatch(
      /React|react-router|@tanstack\/react-query|openapi-fetch|\bfetch\s*\(/,
    );
    expect(gateway).not.toMatch(/\b(Response|Request)\b/);
  });

  it("keeps HTTP and deterministic adapters as the only transport implementations", () => {
    const http = read("httpGateway.ts");
    const deterministic = read("deterministicGateway.ts");

    expect(http).toContain('import type { ApiClient } from "../api/client";');
    expect(http).toContain(
      'client.GET("/api/v1/needs-input-requests/{actionRequestId}"',
    );
    expect(http).toContain(
      'client.POST(\n          "/api/v1/needs-input-requests/{actionRequestId}/commands/resolve"',
    );
    expect(http).toContain('"Idempotency-Key"');
    expect(http).not.toMatch(/\bfetch\s*\(|openapi-fetch/);
    expect(deterministic).not.toMatch(
      /\b(fetch|localStorage|sessionStorage|setTimeout|setInterval|Math\.random|Date\.now)\b/,
    );
    expect(deterministic).not.toContain("openapi-fetch");
  });

  it("does not leak raw transport values or capability dispatchers", () => {
    const gateway = read("gateway.ts");
    const http = read("httpGateway.ts");
    const deterministic = read("deterministicGateway.ts");
    const combined = `${gateway}\n${http}\n${deterministic}`;

    expect(combined).not.toMatch(/dangerouslySetInnerHTML|innerHTML/);
    expect(combined).not.toMatch(/generic|questionnaire|chat|dispatcher/i);
    expect(combined).not.toMatch(/provider|secret|database|storage/i);
  });
});
