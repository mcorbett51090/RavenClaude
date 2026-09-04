import cubejs, { CubeApi } from "@cubejs-client/core";

let cachedClient: CubeApi | null = null;
let cachedToken: string | null = null;
let cachedTokenExpiryMs = 0;

const REFRESH_MARGIN_MS = 60_000; // refetch 60s before actual expiry

async function fetchToken(): Promise<string> {
  const now = Date.now();
  if (cachedToken && now < cachedTokenExpiryMs - REFRESH_MARGIN_MS) {
    return cachedToken;
  }

  const res = await fetch("/api/cube-token", { method: "POST" });
  if (!res.ok) throw new Error(`cube-token fetch failed: ${res.status}`);
  const { token, expiresIn } = await res.json();
  cachedToken = token;
  cachedTokenExpiryMs = now + expiresIn * 1000;
  return token;
}

/**
 * Returns a CubeApi client whose token is fetched from our own
 * /api/cube-token route (never minted client-side) and reused until it's
 * close to expiry. Same pattern as the Next.js starter's lib/cube-client.ts.
 */
export function getCubeClient(): CubeApi {
  if (cachedClient) return cachedClient;

  cachedClient = cubejs(fetchToken, {
    apiUrl: import.meta.env.PUBLIC_CUBE_API_URL || "http://localhost:4000/cubejs-api/v1",
  });

  return cachedClient;
}
