# Use FlatList with keyExtractor and getItemLayout for performant lists

**Status:** Absolute rule
**Domain:** React Native performance
**Applies to:** `mobile-engineering`

---

## Why this exists

A React Native `ScrollView` that renders all items at once is a performance cliff: every item is mounted on screen load, memory grows linearly, and slow scrolling (jank) begins at around 100 items. `FlatList` is the correct list primitive — it virtualizes the list and only renders items near the current scroll position. Without `keyExtractor`, React falls back to index-based keys that produce incorrect reconciliation on sorted or filtered lists. Without `getItemLayout` (for fixed-height items), the list cannot calculate scroll position without rendering all items, defeating the virtualization.

## How to apply

```typescript
import { FlatList, ListRenderItemInfo } from 'react-native';

const ITEM_HEIGHT = 72;

function OrderList({ orders }: { orders: Order[] }) {
  return (
    <FlatList
      data={orders}
      keyExtractor={(item) => item.id}  // stable, unique key per item
      renderItem={({ item }: ListRenderItemInfo<Order>) => (
        <OrderRow order={item} />
      )}
      getItemLayout={(_data, index) => ({  // fixed height only
        length: ITEM_HEIGHT,
        offset: ITEM_HEIGHT * index,
        index,
      })}
      initialNumToRender={10}             // render enough for the visible viewport
      maxToRenderPerBatch={5}             // render 5 items per animation frame
      windowSize={5}                      // keep 5 viewports' worth of items mounted
      removeClippedSubviews={true}        // unmount off-screen native views
    />
  );
}
```

**Do:**
- Always provide `keyExtractor` returning a stable, unique identifier (never the array index).
- Provide `getItemLayout` if all items have the same height — enables instant scroll-to-index and improves rendering.
- Memoize `renderItem` with `useCallback` and the item component with `React.memo` to prevent unnecessary re-renders.
- Use `FlashList` (Shopify) instead of `FlatList` for very large lists — it is faster with less boilerplate. `[verify-at-build]`

**Don't:**
- Use `ScrollView` to render lists with more than ~50 items.
- Use the array index as the key — reordering or filtering causes incorrect DOM reconciliation.
- Render complex, heavy components inline in `renderItem` — extract and memoize them.

## Edge cases / when the rule does NOT apply

For heterogeneous variable-height items where `getItemLayout` cannot be precomputed, omit it and accept the minor initialization cost. For short, fixed-count lists (< 20 items) that never change, `ScrollView` is simpler and acceptable.

## See also

- [`../agents/cross-platform-engineer.md`](../agents/cross-platform-engineer.md) — owns React Native performance and list rendering.
- [`./keep-the-main-thread-free.md`](./keep-the-main-thread-free.md) — main thread pressure from expensive renderItem is the most common list jank cause.

## Provenance

React Native documentation on FlatList and list optimization (reactnative.dev). Shopify FlashList project. Codifies `cross-platform-engineer`'s React Native performance discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
