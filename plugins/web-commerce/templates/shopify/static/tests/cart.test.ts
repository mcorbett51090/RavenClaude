import { afterEach, describe, expect, it, vi } from "vitest";
import { createCart, cartLinesAdd, getCart, redirectToCheckout, storefrontFetch } from "../cart";
import type { ShopifyConfig } from "../cart";

const config: ShopifyConfig = {
  storeDomain: "test-store.myshopify.com",
  storefrontToken: "test-storefront-token",
};

function mockFetchOnce(body: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status: ok ? 200 : 500,
      statusText: ok ? "OK" : "Internal Server Error",
      json: async () => body,
    }),
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("storefrontFetch", () => {
  it("posts to the versioned GraphQL endpoint with the storefront token header", async () => {
    mockFetchOnce({ data: { ok: true } });
    await storefrontFetch(config, "query { shop { name } }", {});
    const [url, init] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toBe("https://test-store.myshopify.com/api/2026-07/graphql.json");
    expect((init.headers as Record<string, string>)["X-Shopify-Storefront-Access-Token"]).toBe(
      "test-storefront-token",
    );
  });

  it("throws on a GraphQL-level error", async () => {
    mockFetchOnce({ errors: [{ message: "boom" }] });
    await expect(storefrontFetch(config, "query {}", {})).rejects.toThrow(/boom/);
  });

  it("throws on a non-2xx transport response", async () => {
    mockFetchOnce({}, false);
    await expect(storefrontFetch(config, "query {}", {})).rejects.toThrow(/500/);
  });
});

describe("createCart", () => {
  it("returns checkoutUrl — the ONLY checkout-completion surface this template emits", async () => {
    mockFetchOnce({
      data: {
        cartCreate: {
          cart: {
            id: "gid://shopify/Cart/1",
            checkoutUrl: "https://test-store.myshopify.com/cart/c/1",
            totalQuantity: 1,
            lines: { edges: [] },
          },
          userErrors: [],
        },
      },
    });
    const cart = await createCart(config, [
      { merchandiseId: "gid://shopify/ProductVariant/1", quantity: 1 },
    ]);
    expect(cart.checkoutUrl).toBe("https://test-store.myshopify.com/cart/c/1");
  });

  it("rejects with Shopify's userErrors rather than swallowing them", async () => {
    mockFetchOnce({
      data: {
        cartCreate: {
          cart: null,
          userErrors: [{ field: ["lines"], message: "invalid merchandise" }],
        },
      },
    });
    await expect(
      createCart(config, [{ merchandiseId: "gid://shopify/ProductVariant/bad", quantity: 1 }]),
    ).rejects.toThrow(/invalid merchandise/);
  });

  it("rejects an empty line list before making a request", async () => {
    await expect(createCart(config, [])).rejects.toThrow(/at least one line/);
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

  it("getCart returns null for an expired/unknown cart id", async () => {
    mockFetchOnce({ data: { cart: null } });
    const cart = await getCart(config, "gid://shopify/Cart/expired");
    expect(cart).toBeNull();
  });
});

describe("redirectToCheckout", () => {
  it("navigates via window.location.assign", () => {
    const assign = vi.fn();
    vi.stubGlobal("window", { location: { assign } });
    redirectToCheckout({ checkoutUrl: "https://test-store.myshopify.com/cart/c/1" });
    expect(assign).toHaveBeenCalledWith("https://test-store.myshopify.com/cart/c/1");
  });
});
