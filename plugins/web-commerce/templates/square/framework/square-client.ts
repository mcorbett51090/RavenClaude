/**
 * Minimal first-party fetch wrapper for the Square REST API.
 *
 * No vendored Square SDK dependency here on purpose (CLAUDE.md §2 #6) --
 * the REST surface used by this tier (Orders, Payments, Refunds, Catalog,
 * Inventory) is small and stable enough that a typed `fetch` wrapper is
 * less maintenance risk than a pinned SDK version.
 */

export interface SquareClientConfig {
  accessToken: string;
  environment: "sandbox" | "production";
  /** Abort a request Square has not answered within this many ms. Default 10_000. */
  timeoutMs?: number;
}

const DEFAULT_TIMEOUT_MS = 10_000;

// [unverified -- training knowledge] bump per Square's API version
// changelog before go-live: https://developer.squareup.com/docs/build-basics/api-lifecycle
const SQUARE_API_VERSION = "2026-01-16";

export class SquareApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "SquareApiError";
    this.status = status;
    this.body = body;
  }
}

/**
 * Square did not answer within `timeoutMs`. The request may still have been
 * applied upstream, so retry a mutating call with the SAME idempotency key.
 */
export class SquareTimeoutError extends Error {
  readonly timeoutMs: number;

  constructor(path: string, timeoutMs: number) {
    super(`Square API request to ${path} timed out after ${timeoutMs} ms`);
    this.name = "SquareTimeoutError";
    this.timeoutMs = timeoutMs;
  }
}

function isAbortOrTimeout(err: unknown): boolean {
  const name = (err as { name?: unknown } | null)?.name;
  return name === "TimeoutError" || name === "AbortError";
}

/** Reads Square credentials from env only -- never hard-code a key (CLAUDE.md §2 #4). */
export function readSquareConfig(): SquareClientConfig {
  const accessToken = process.env.SQUARE_ACCESS_TOKEN;
  if (!accessToken) {
    throw new Error("SQUARE_ACCESS_TOKEN is not set -- see .env.example");
  }
  const environment =
    (process.env.SQUARE_ENVIRONMENT as "sandbox" | "production" | undefined) ?? "sandbox";
  return { accessToken, environment };
}

function baseUrl(environment: "sandbox" | "production"): string {
  return environment === "production"
    ? "https://connect.squareup.com"
    : "https://connect.squareupsandbox.com";
}

/**
 * Call the Square REST API. Never logs the request body or headers -- both
 * may carry the access token, a single-use card token, or a payment
 * reference.
 */
export async function squareFetch<T>(
  path: string,
  init: { method: "GET" | "POST"; body?: unknown },
  config: SquareClientConfig,
): Promise<T> {
  const timeoutMs = config.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  let response: Response;
  try {
    response = await fetch(baseUrl(config.environment) + path, {
      method: init.method,
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${config.accessToken}`,
        "square-version": SQUARE_API_VERSION,
      },
      body: init.body === undefined ? undefined : JSON.stringify(init.body),
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (err) {
    if (isAbortOrTimeout(err)) throw new SquareTimeoutError(path, timeoutMs);
    throw err;
  }

  // The signal also covers a body that stalls after the headers arrive.
  const json = (await response.json().catch((err: unknown) => {
    if (isAbortOrTimeout(err)) throw new SquareTimeoutError(path, timeoutMs);
    return {};
  })) as unknown;
  if (!response.ok) {
    throw new SquareApiError(
      `Square API request to ${path} failed with ${response.status}`,
      response.status,
      json,
    );
  }
  return json as T;
}
