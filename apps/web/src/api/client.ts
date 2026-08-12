import createClient, { type Client } from "openapi-fetch";
import type { paths } from "./generated/schema";

export type ApiClient = Client<paths>;

type ClientOptions = {
  baseUrl?: string;
  fetch?: typeof globalThis.fetch;
};

const invalidBaseUrl = (message: string): never => {
  throw new TypeError(message);
};

function resolveBaseUrl(baseUrl: string | undefined): string {
  if (baseUrl === undefined) {
    return globalThis.location.origin;
  }
  if (
    typeof baseUrl !== "string" ||
    baseUrl.trim() !== baseUrl ||
    baseUrl === ""
  ) {
    return invalidBaseUrl(
      "baseUrl must be a nonblank absolute http or https URL",
    );
  }

  let parsed: URL;
  try {
    parsed = new URL(baseUrl);
  } catch {
    return invalidBaseUrl(
      "baseUrl must be a nonblank absolute http or https URL",
    );
  }
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    return invalidBaseUrl(
      "baseUrl must be a nonblank absolute http or https URL",
    );
  }
  if (parsed.username || parsed.password) {
    return invalidBaseUrl(
      "baseUrl must be an absolute root URL without credentials",
    );
  }
  if (parsed.pathname !== "/") {
    return invalidBaseUrl(
      "baseUrl must be an absolute root URL without a path",
    );
  }
  if (parsed.search || parsed.hash) {
    return invalidBaseUrl(
      "baseUrl must be an absolute root URL without a query or fragment",
    );
  }
  return parsed.origin;
}

export function createApiClient(options: ClientOptions = {}): ApiClient {
  if (
    typeof options !== "object" ||
    options === null ||
    Array.isArray(options)
  ) {
    throw new TypeError("client options must be an object");
  }
  const optionsPrototype = Object.getPrototypeOf(options);
  if (optionsPrototype !== Object.prototype && optionsPrototype !== null) {
    throw new TypeError("client options must be an object");
  }
  if (options.fetch !== undefined && typeof options.fetch !== "function") {
    throw new TypeError("fetch must be a function");
  }
  return createClient<paths>({
    baseUrl: resolveBaseUrl(options.baseUrl),
    fetch: options.fetch ?? globalThis.fetch,
  });
}
