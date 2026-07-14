/**
 * Shopify Storefront API (GraphQL) Cart client — static tier.
 *
 * This is the ONLY sanctioned checkout path for the Shopify track. Every cart
 * mutation ends at `cart.checkoutUrl`; the buyer completes payment entirely on
 * Shopify's hosted checkout page. This file contains NO checkout-creation
 * call, NO JS Buy SDK import, and NO card field — see
 * ../../../knowledge/deprecated-paths-do-not-scaffold.md for why both of
 * those paths are dead (JS Buy SDK checkout: hard cutover 2025-07-01; the
 * custom Checkout API: shut down 2025-04-01).
 *
 * Runs in the browser: the Storefront API's public access token is designed
 * for client-side use (unlike the webhook signing secret, which is server-
 * only — see webhook.ts). No bundler is required to USE this module at
 * runtime; ship it as an ES module. TypeScript itself still needs a one-time
 * transpile (e.g. `npx esbuild cart.ts --bundle --format=esm --outfile=cart.js`
 * or `tsc`) since browsers don't execute `.ts` directly — see README.md.
 */

export interface ShopifyConfig {
  /** e.g. "your-store.myshopify.com" — never include a protocol. */
  storeDomain: string;
  /** Storefront API public access token. Safe to expose client-side. */
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
 * carries a caller-supplied price. `checkoutUrl` is the only field the buyer
 * flow needs; everything else here is for rendering an on-page cart summary.
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

/** Thin GraphQL POST helper. Throws on transport, GraphQL-level, or missing-data errors. */
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

/** Create a new cart from one or more lines. Returns `checkoutUrl` for the redirect. */
export async function createCart(
  config: ShopifyConfig,
  lines: CartLineInput[],
): Promise<ShopifyCart> {
  if (lines.length === 0) {
    throw new Error("createCart requires at least one line");
  }
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

/** Add lines to an existing cart (e.g. "add to cart" on a PDP once a cart already exists). */
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

/** Re-fetch a cart by id (e.g. to render an up-to-date cart summary). */
export async function getCart(config: ShopifyConfig, cartId: string): Promise<ShopifyCart | null> {
  const data = await storefrontFetch<{ cart: CartFieldsFragmentShape | null }>(config, CART_QUERY, {
    cartId,
  });
  return data.cart ? toShopifyCart(data.cart) : null;
}

/**
 * Redirect the buyer to Shopify's hosted checkout. This is the ONLY
 * checkout-completion step this template performs — everything else (PCI,
 * payment methods, 3DS, tax, shipping) is Shopify's hosted page. Uses
 * `location.assign` (not `.href =`) so the navigation is testable/mockable.
 */
export function redirectToCheckout(cart: Pick<ShopifyCart, "checkoutUrl">): void {
  if (typeof window === "undefined") {
    throw new Error("redirectToCheckout must run in a browser context");
  }
  window.location.assign(cart.checkoutUrl);
}
