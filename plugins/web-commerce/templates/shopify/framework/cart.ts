/**
 * Shopify Storefront API (GraphQL) Cart client — framework tier (Next.js /
 * Astro). This is the ONLY sanctioned checkout path for the Shopify track.
 * Every cart mutation ends at `cart.checkoutUrl`; the buyer completes
 * payment entirely on Shopify's hosted checkout page. This file contains NO
 * checkout-creation call, NO JS Buy SDK import, and NO card field — see
 * ../../../knowledge/deprecated-paths-do-not-scaffold.md.
 *
 * Framework-agnostic on purpose: no `next/headers` or Astro-specific import,
 * so the same module works from a Next.js Route Handler / Server Component
 * or an Astro server endpoint. Wire cart-id persistence (an httpOnly cookie
 * is the standard pattern for a server-rendered cart session) in your
 * route/page — see README.md for both frameworks' cookie snippets.
 */

export interface ShopifyConfig {
  /** e.g. "your-store.myshopify.com" — never include a protocol. */
  storeDomain: string;
  /** Storefront API access token. Read from env server-side; also safe client-side. */
  storefrontToken: string;
  /** Storefront GraphQL API version path segment. Defaults to "2026-07". */
  apiVersion?: string;
}

export interface CartLineInput {
  /** Shopify ProductVariant GID, e.g. "gid://shopify/ProductVariant/123456789". */
  merchandiseId: string;
  quantity: number;
}

export interface ShopifyCartLine {
  id: string;
  quantity: number;
  merchandiseId: string;
}

/**
 * Shopify is `capabilities.catalogSourceOfTruth: "provider"` — the cart never
 * carries a caller-supplied price; `checkoutUrl` is the sole checkout surface.
 */
export interface ShopifyCart {
  id: string;
  checkoutUrl: string;
  totalQuantity: number;
  lines: ShopifyCartLine[];
}

interface GraphQLResponse<T> {
  data?: T;
  errors?: Array<{ message: string }>;
}

interface CartFieldsFragmentShape {
  id: string;
  checkoutUrl: string;
  totalQuantity: number;
  lines: { edges: Array<{ node: { id: string; quantity: number; merchandise: { id: string } } }> };
}

function toShopifyCart(raw: CartFieldsFragmentShape): ShopifyCart {
  return {
    id: raw.id,
    checkoutUrl: raw.checkoutUrl,
    totalQuantity: raw.totalQuantity,
    lines: raw.lines.edges.map((edge) => ({
      id: edge.node.id,
      quantity: edge.node.quantity,
      merchandiseId: edge.node.merchandise.id,
    })),
  };
}

/**
 * Thin GraphQL POST helper. Called server-side in this tier (Route
 * Handler / Astro endpoint / Server Component), which is where
 * `SHOPIFY_STOREFRONT_TOKEN` should be read from `process.env` — see
 * provider.ts for the env-loading example.
 */
export async function storefrontFetch<T>(
  config: ShopifyConfig,
  query: string,
  variables: Record<string, unknown>,
): Promise<T> {
  const apiVersion = config.apiVersion ?? "2026-07";
  const res = await fetch(`https://${config.storeDomain}/api/${apiVersion}/graphql.json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Storefront-Access-Token": config.storefrontToken,
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!res.ok) {
    throw new Error(`Shopify Storefront API request failed: ${res.status} ${res.statusText}`);
  }

  const json = (await res.json()) as GraphQLResponse<T>;
  if (json.errors?.length) {
    throw new Error(
      `Shopify Storefront API error: ${json.errors.map((e) => e.message).join("; ")}`,
    );
  }
  if (!json.data) {
    throw new Error("Shopify Storefront API returned no data");
  }
  return json.data;
}

const CART_FIELDS = `
  id
  checkoutUrl
  totalQuantity
  lines(first: 100) {
    edges {
      node {
        id
        quantity
        merchandise {
          ... on ProductVariant {
            id
          }
        }
      }
    }
  }
`;

const CART_CREATE_MUTATION = `
  mutation CartCreate($lines: [CartLineInput!]!) {
    cartCreate(input: { lines: $lines }) {
      cart { ${CART_FIELDS} }
      userErrors { field message }
    }
  }
`;

const CART_LINES_ADD_MUTATION = `
  mutation CartLinesAdd($cartId: ID!, $lines: [CartLineInput!]!) {
    cartLinesAdd(cartId: $cartId, lines: $lines) {
      cart { ${CART_FIELDS} }
      userErrors { field message }
    }
  }
`;

const CART_QUERY = `
  query CartQuery($cartId: ID!) {
    cart(id: $cartId) { ${CART_FIELDS} }
  }
`;

interface CartMutationPayload {
  cart: CartFieldsFragmentShape | null;
  userErrors: Array<{ field: string[] | null; message: string }>;
}

function assertNoUserErrors(userErrors: CartMutationPayload["userErrors"], action: string): void {
  if (userErrors.length > 0) {
    throw new Error(`Shopify ${action} rejected: ${userErrors.map((e) => e.message).join("; ")}`);
  }
}

/**
 * Create a cart. Unlike the static tier's direct "buy now" flow, the
 * framework tier commonly starts a cart with ZERO lines (an empty session
 * cart created on first visit) and adds lines as the buyer shops — so, unlike
 * the static tier, an empty `lines` array is allowed here.
 */
export async function createCart(
  config: ShopifyConfig,
  lines: CartLineInput[] = [],
): Promise<ShopifyCart> {
  const data = await storefrontFetch<{ cartCreate: CartMutationPayload }>(
    config,
    CART_CREATE_MUTATION,
    {
      lines,
    },
  );
  assertNoUserErrors(data.cartCreate.userErrors, "cartCreate");
  if (!data.cartCreate.cart) {
    throw new Error("Shopify cartCreate returned no cart");
  }
  return toShopifyCart(data.cartCreate.cart);
}

export async function cartLinesAdd(
  config: ShopifyConfig,
  cartId: string,
  lines: CartLineInput[],
): Promise<ShopifyCart> {
  const data = await storefrontFetch<{ cartLinesAdd: CartMutationPayload }>(
    config,
    CART_LINES_ADD_MUTATION,
    {
      cartId,
      lines,
    },
  );
  assertNoUserErrors(data.cartLinesAdd.userErrors, "cartLinesAdd");
  if (!data.cartLinesAdd.cart) {
    throw new Error("Shopify cartLinesAdd returned no cart");
  }
  return toShopifyCart(data.cartLinesAdd.cart);
}

export async function getCart(config: ShopifyConfig, cartId: string): Promise<ShopifyCart | null> {
  const data = await storefrontFetch<{ cart: CartFieldsFragmentShape | null }>(config, CART_QUERY, {
    cartId,
  });
  return data.cart ? toShopifyCart(data.cart) : null;
}

/**
 * Server-side session helper: reuse an existing cart id (from an httpOnly
 * cookie — see README.md) if it still resolves to a live cart, otherwise
 * start a new empty one. The caller is responsible for persisting the
 * returned cart's `id` back into the cookie (this module never touches
 * cookies directly, to stay framework-agnostic).
 */
export async function getOrCreateCart(
  config: ShopifyConfig,
  existingCartId?: string,
): Promise<ShopifyCart> {
  if (existingCartId) {
    const existing = await getCart(config, existingCartId);
    if (existing) return existing;
  }
  return createCart(config, []);
}
