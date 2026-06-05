# Add accessibility labels to every interactive and image element

**Status:** Absolute rule
**Domain:** Mobile accessibility
**Applies to:** `mobile-engineering`

---

## Why this exists

A VoiceOver (iOS) or TalkBack (Android) user navigating your app hears a description of every element they focus on. An icon button without an accessibility label is announced as "button" or worse, nothing — the user has no idea what it does. An image without a label is silent. The result is an app that is unusable for millions of users with visual impairments. Accessibility labels are not a final polish step; they are a correctness requirement that belongs in the component at implementation time.

## How to apply

```swift
// iOS SwiftUI
Button(action: deleteOrder) {
    Image(systemName: "trash")
}
.accessibilityLabel("Delete order")      // required — icon alone says nothing
.accessibilityHint("Removes the order from your history")  // optional but helpful

// An image that conveys meaning
Image("product-thumbnail")
    .accessibilityLabel("Red running shoes, size 10")

// A purely decorative image — hide from accessibility tree
Image("background-pattern")
    .accessibilityHidden(true)
```

```kotlin
// Android Jetpack Compose
IconButton(
    onClick = { deleteOrder() },
    modifier = Modifier.semantics { contentDescription = "Delete order" }
) {
    Icon(imageVector = Icons.Default.Delete, contentDescription = "Delete order")
    // contentDescription on Icon is the accessibility label
}

// Decorative image — no content description
Image(
    painter = painterResource(id = R.drawable.background),
    contentDescription = null   // null = decorative; excluded from TalkBack
)
```

**Do:**
- Provide a concise, action-oriented label for every interactive element: "Add to cart", "Delete message", "Open menu".
- Use `contentDescription = null` (Android) / `accessibilityHidden(true)` (iOS) for purely decorative images.
- Group related elements with `accessibilityElement(children: .combine)` (iOS) or `Modifier.semantics(mergeDescendants = true)` (Android) so VoiceOver/TalkBack reads them as one.
- Test with VoiceOver / TalkBack turned on before every release — there is no substitute for actually using the accessibility tools.

**Don't:**
- Use button text alone as the label when the text is an icon — add an explicit label.
- Include the element type in the label ("Button: Delete") — the accessibility API announces the type automatically.
- Use the same label for multiple different actions on the same screen.

## Edge cases / when the rule does NOT apply

Text elements that are the only description of themselves (a label, a body paragraph) do not need an explicit `accessibilityLabel` — the text content is the label. Tab bar items with a title already have their label from the title.

## See also

- [`../agents/ios-engineer.md`](../agents/ios-engineer.md) — owns iOS accessibility implementation.
- [`../agents/android-engineer.md`](../agents/android-engineer.md) — owns Android accessibility with Compose semantics.

## Provenance

Apple Human Interface Guidelines — Accessibility; Android Accessibility guidelines (developer.android.com); WCAG 2.2 SC 1.1.1 (Non-text Content). Codifies platform-specific accessibility requirements for both iOS and Android engineers.

---

_Last reviewed: 2026-06-05 by `claude`_
