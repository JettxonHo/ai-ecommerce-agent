import { afterEach, describe, expect, it, vi } from "vitest";
import { createApiClient } from "./client";

describe("generated API client adapter", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uses the browser origin by default and performs no import-time I/O", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>(
      async () =>
        new Response(JSON.stringify({ items: [] }), {
          headers: { "content-type": "application/json" },
        }),
    );

    const client = createApiClient({ fetch });
    await client.GET("/api/v1/tasks", { params: { query: { limit: 20 } } });

    expect(fetch).toHaveBeenCalledTimes(1);
    const request = fetch.mock.calls[0]?.[0];
    expect(request).toBeInstanceOf(Request);
    if (!(request instanceof Request)) {
      throw new Error(
        "openapi-fetch should pass a Request to the injected fetch",
      );
    }
    expect(request.url).toBe(
      `${globalThis.location.origin}/api/v1/tasks?limit=20`,
    );
    expect(request.method).toBe("GET");
  });

  it("performs exactly one typed POST request with query, headers, and body", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>(
      async () =>
        new Response(JSON.stringify({}), {
          headers: { "content-type": "application/json" },
        }),
    );
    const client = createApiClient({ baseUrl: "https://example.test", fetch });

    await client.POST("/api/v1/tasks", {
      params: {
        header: { "Idempotency-Key": "request-1" },
      },
      body: {
        taskName: "Task",
        productCategory: "Category",
        promotionGoal: "Goal",
      },
    });

    expect(fetch).toHaveBeenCalledTimes(1);
    const request = fetch.mock.calls[0]?.[0];
    expect(request).toBeInstanceOf(Request);
    if (!(request instanceof Request)) {
      throw new Error(
        "openapi-fetch should pass a Request to the injected fetch",
      );
    }
    expect(request.url).toBe("https://example.test/api/v1/tasks");
    expect(request.method).toBe("POST");
    expect(request.headers.get("Idempotency-Key")).toBe("request-1");
    expect(await request.text()).toBe(
      JSON.stringify({
        taskName: "Task",
        productCategory: "Category",
        promotionGoal: "Goal",
      }),
    );
  });

  it("accepts absolute http and https root URLs", () => {
    for (const baseUrl of ["http://example.test", "https://example.test/"]) {
      expect(() => createApiClient({ baseUrl })).not.toThrow();
    }
  });

  it("rejects raw, null, wrong, String-object, credential, path, query, and fragment roots", () => {
    const fetch = vi.fn<typeof globalThis.fetch>();
    vi.stubGlobal("fetch", fetch);
    const invalidOptions: readonly [unknown, string][] = [
      [null, "client options must be an object"],
      [[], "client options must be an object"],
      ["options", "client options must be an object"],
      [new String("options"), "client options must be an object"],
    ];
    for (const [options, message] of invalidOptions) {
      expect(() => createApiClient(options as never)).toThrowError(message);
    }

    const invalidRoots: readonly [unknown, string][] = [
      [null, "baseUrl must be a nonblank absolute http or https URL"],
      [42, "baseUrl must be a nonblank absolute http or https URL"],
      [true, "baseUrl must be a nonblank absolute http or https URL"],
      [
        new String("https://example.test"),
        "baseUrl must be a nonblank absolute http or https URL",
      ],
      ["", "baseUrl must be a nonblank absolute http or https URL"],
      [" ", "baseUrl must be a nonblank absolute http or https URL"],
      ["example.test", "baseUrl must be a nonblank absolute http or https URL"],
      [{}, "baseUrl must be a nonblank absolute http or https URL"],
      [
        "ftp://example.test",
        "baseUrl must be a nonblank absolute http or https URL",
      ],
      [
        "https://user:pass@example.test",
        "baseUrl must be an absolute root URL without credentials",
      ],
      [
        "https://example.test/api",
        "baseUrl must be an absolute root URL without a path",
      ],
      [
        "https://example.test/?tenant=one",
        "baseUrl must be an absolute root URL without a query or fragment",
      ],
      [
        "https://example.test/#fragment",
        "baseUrl must be an absolute root URL without a query or fragment",
      ],
    ];
    for (const [baseUrl, message] of invalidRoots) {
      expect(() => createApiClient({ baseUrl, fetch } as never)).toThrowError(
        message,
      );
    }
    expect(fetch).not.toHaveBeenCalled();
  });

  it("does not perform I/O while the adapter module is imported", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>(() => {
      throw new Error("import-time network access is forbidden");
    });
    vi.stubGlobal("fetch", fetch);
    vi.resetModules();

    const imported = await import("./client");

    expect(imported.createApiClient).toBeTypeOf("function");
    expect(fetch).not.toHaveBeenCalled();

    const client = imported.createApiClient({
      baseUrl: "https://example.test",
      fetch,
    });
    expect(client).toBeDefined();
    expect(fetch).not.toHaveBeenCalled();
  });
});
