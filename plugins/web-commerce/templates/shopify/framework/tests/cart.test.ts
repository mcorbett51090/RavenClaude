import { afterEach, describe, expect, it, vi } from "vitest";
import { createCart, cartLinesAdd, getCart, getOrCreateCart, storefrontFetch } from "../cart";
import type { ShopifyConfig } from "../cart";

const config: ShopifyConfig = {
  storeDomain: "test-store.myshopify.com",
  storefrontToken: "test-storefront-token",
};

function fakeResponse(body: unknown, ok = true) {
  return {
    ok,
    status: ok ? 200 : 500,
    statusText: ok ? "OK" : "Internal Server Error",
    json: async () => body,
  };
}

/** Stubs `fetch` to answer every call (not just the first) with `body`. */
function mockFetchOnce(body: unknown, ok = true) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(fakeResponse(body, ok)));
}

/** Stubs `fetch` to answer successive calls with successive bodies, in order. */
function mockFetchSequence(bodies: unknown[]) {
  const fn = vi.fn();
  for (const body of bodies) {
    fn.mockResolvedValueOnce(fakeResponse(body));
  }
  vi.stubGlobal("fetch", fn);
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("storefrontFetch", () => {
  it("targets the versioned GraphQL endpoint", async () => {
    mockFetchOnce({ data: {} });
    await storefrontFetch(config, "query {}", {});
    const [url] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toBe("https://test-store.myshopify.com/api/2026-07/graphql.json");
  });
});

describe("createCart (framework tier allows an empty session cart)", () => {
  it("creates an empty cart with no lines", async () => {
    mockFetchOnce({
      data: {
        cartCreate: {
          cart: {
            id: "gid://shopify/Cart/1",
            checkoutUrl: "https://test-store.myshopify.com/cart/c/1",
            totalQuantity: 0,
            lines: { edges: [] },
          },
          userErrors: [],
        },
      },
    });
    const cart = await createCart(config);
    expect(cart.totalQuantity).toBe(0);
    expect(cart.checkoutUrl).toContain("myshopify.com");
  });

  it("surfaces Shopify userErrors rather than swallowing them", async () => {
    mockFetchOnce({
      data: {
        cartCreate: { cart: null, userErrors: [{ field: null, message: "cart limit exceeded" }] },
      },
    });
    await expect(
      createCart(config, [{ merchandiseId: "gid://shopify/ProductVariant/1", quantity: 1 }]),
    ).rejects.toThrow(/cart limit exceeded/);
  });
});

describe("getOrCreateCart", () => {
  it("reuses an existing cart id when it still resolves", async () => {
    mockFetchOnce({
      data: {
        cart: {
          id: "gid://shopify/Cart/existing",
          checkoutUrl: "https://test-store.myshopify.com/cart/c/existing",
          totalQuantity: 3,
          lines: { edges: [] },
        },
      },
    });
    const cart = await getOrCreateCart(config, "gid://shopify/Cart/existing");
    expect(cart.id).toBe("gid://shopify/Cart/existing");
  });

  it("starts a fresh cart when no cart id was passed", async () => {
    mockFetchOnce({
      data: {
        cartCreate: {
          cart: {
            id: "gid://shopify/Cart/new",
            checkoutUrl: "https://test-store.myshopify.com/cart/c/new",
            totalQuantity: 0,
            lines: { edges: [] },
          },
          userErrors: [],
        },
      },
    });
    const cart = await getOrCreateCart(config, undefined);
    expect(cart.id).toBe("gid://shopify/Cart/new");
  });

  it("starts a fresh cart when the stored cart id no longer resolves (expired)", async () => {
    mockFetchSequence([
      { data: { cart: null } }, // first call: getCart(existingCartId) -> not found
      {
        data: {
          cartCreate: {
            cart: {
              id: "gid://shopify/Cart/replacement",
              checkoutUrl: "https://test-store.myshopify.com/cart/c/replacement",
              totalQuantity: 0,
              lines: { edges: [] },
            },
            userErrors: [],
          },
        },
      }, // second call: cartCreate fallback
    ]);
    const cart = await getOrCreateCart(config, "gid://shopify/Cart/expired");
    expect(cart.id).toBe("gid://shopify/Cart/replacement");
  });
});

describe("cartLinesAdd / getCart", () => {
  it("cartLinesAdd returns the updated cart", async () => {
    mockFetchOnce({
      data: {
        cartLinesAdd: {
          cart: {
            id: "gid://shopify/Cart/1",
            checkoutUrl: "https://test-store.myshopify.com/cart/c/1",
            totalQuantity: 2,
            lines: { edges: [] },
          },
          userErrors: [],
        },
      },
    });
    const cart = await cartLinesAdd(config, "gid://shopify/Cart/1", [
      { merchandiseId: "gid://shopify/ProductVariant/2", quantity: 1 },
    ]);
    expect(cart.totalQuantity).toBe(2);
  });

  it("getCart returns null for an unknown cart id", async () => {
    mockFetchOnce({ data: { cart: null } });
    const cart = await getCart(config, "gid://shopify/Cart/unknown");
    expect(cart).toBeNull();
  });
});
