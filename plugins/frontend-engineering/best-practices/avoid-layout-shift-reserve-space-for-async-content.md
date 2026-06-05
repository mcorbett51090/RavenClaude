# Reserve space for async content to avoid layout shift

**Status:** Absolute rule
**Domain:** Core Web Vitals / CLS
**Applies to:** `frontend-engineering`

---

## Why this exists

Cumulative Layout Shift (CLS) is a Core Web Vital that measures how much page content jumps around as assets load or dynamic content appears. Every time an image pops in without reserved space, a font swaps, an ad injects, or a skeleton is replaced by differently-sized content, the layout shifts — and the user loses their place or accidentally taps the wrong thing. A CLS score above 0.1 fails the "good" threshold and directly impacts search ranking and user trust.

## How to apply

```css
/* Reserve space for images with explicit dimensions */
img {
  width: 100%;
  aspect-ratio: 16 / 9;  /* prevents shift before image loads */
}

/* Font loading — prevent FOUT causing layout shift */
@font-face {
  font-family: 'MyFont';
  font-display: optional;  /* don't swap after first render */
}
```

```tsx
// Skeleton with the same dimensions as the loaded content
function UserCard({ userId }: { userId: string }) {
  const { data, isLoading } = useQuery({ queryKey: ['user', userId], queryFn: fetchUser });

  if (isLoading) {
    // Same height/width as the loaded card — no layout shift
    return <div className="user-card-skeleton" aria-hidden />;
  }
  return <UserCardContent user={data} />;
}
```

**Do:**
- Set `width` and `height` attributes on all `<img>` elements so the browser reserves space before the image loads.
- Use `aspect-ratio` in CSS for responsive images and videos.
- Make skeletons the same size as the content they replace.
- Use `font-display: optional` or `font-display: swap` with a system-font fallback of matching metrics.
- Avoid injecting content above existing content (banners, cookie notices, ads) after the page has rendered.

**Don't:**
- Rely on images loading quickly enough that a shift "won't be noticed."
- Let a dynamic component render at zero height and then expand when data arrives.
- Use `font-display: swap` without a fallback font that closely matches the web font metrics (size-adjust, ascent-override).

## Edge cases / when the rule does NOT apply

Content that appears only below the visible viewport does not contribute to CLS. Shift triggered by user interaction (expanding an accordion, clicking a button) is excluded from CLS measurement. User-initiated animations and transitions are also excluded.

## See also

- [`../agents/frontend-performance-engineer.md`](../agents/frontend-performance-engineer.md) — owns CLS and Core Web Vitals engineering.
- [`./optimize-images-and-fonts.md`](./optimize-images-and-fonts.md) — image and font optimization that works in tandem with CLS prevention.

## Provenance

Google Core Web Vitals specification for CLS (web.dev/cls). Standard practice for passing the "good" CLS threshold of < 0.1. Codifies `frontend-performance-engineer` responsibility.

---

_Last reviewed: 2026-06-05 by `claude`_
