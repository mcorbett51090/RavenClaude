# Own state at the right level in the SwiftUI hierarchy

**Status:** Pattern
**Domain:** iOS / SwiftUI
**Applies to:** `mobile-engineering`

---

## Why this exists

SwiftUI views are structs that are recreated frequently; misplacing `@State` causes either lost state (declared too low — resets on redraw) or performance problems and unexpected coupling (declared too high — every descendant re-renders). The property-wrapper hierarchy — `@State`, `@StateObject`, `@ObservedObject`, `@EnvironmentObject`, `@Binding` — each has a specific ownership and lifetime model. Using the wrong one produces views that don't update, update too much, or hold stale data.

## How to apply

```swift
// State ownership rules:
// @State          — simple value type owned AND CREATED by this view
// @StateObject    — reference type (ObservableObject) owned AND CREATED by this view
// @ObservedObject — reference type passed IN from a parent; parent owns the lifetime
// @Binding        — a reference to @State owned by a parent; two-way sync
// @EnvironmentObject — injected from the environment; requires .environmentObject() above

struct CounterView: View {
    @State private var count = 0          // owned here; lives with this view
    @StateObject private var vm = CounterViewModel()  // owned here; survives redraws

    var body: some View {
        VStack {
            Text("\(count)")
            IncrementButton(count: $count)   // passes @Binding down
            CounterDetail(vm: vm)            // passes @ObservedObject (vm not owned by child)
        }
    }
}

struct IncrementButton: View {
    @Binding var count: Int   // NOT @State — parent owns it
    var body: some View { Button("+") { count += 1 } }
}
```

**Do:**
- Use `@StateObject` (not `@ObservedObject`) when the view creates the view model — `@ObservedObject` will recreate the VM on every parent redraw.
- Use `@Binding` for two-way state sync; use a plain `let` for one-way data flow.
- Use `@EnvironmentObject` for values consumed deep in the hierarchy without prop-drilling.
- Keep `@State` private to the view; expose mutations via methods or bindings.

**Don't:**
- Use `@ObservedObject` to create and own a view model — the object will be destroyed and recreated on parent re-renders.
- Declare `@State` in a parent for state that only the child uses — it forces the parent to own unnecessary state.
- Use `@EnvironmentObject` for frequently-changing values; every consumer re-renders on change.

## Edge cases / when the rule does NOT apply

When using Swift Observation framework (`@Observable` / `@Bindable`) introduced in iOS 17+, the property wrapper rules differ — `@Observable` classes are observed selectively per-property, and `@StateObject` is replaced by `@State` for reference types. `[verify-at-build]`

## See also

- [`../agents/ios-engineer.md`](../agents/ios-engineer.md) — owns SwiftUI state and lifecycle.
- [`./respect-the-lifecycle.md`](./respect-the-lifecycle.md) — lifecycle awareness governs when `@StateObject` is initialized and torn down.

## Provenance

Apple SwiftUI documentation (developer.apple.com/documentation/swiftui) and WWDC sessions on data flow. Codifies `ios-engineer`'s SwiftUI state discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
