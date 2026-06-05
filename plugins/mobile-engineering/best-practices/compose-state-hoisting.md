# Hoist state in Jetpack Compose — composables should be stateless

**Status:** Pattern
**Domain:** Android / Jetpack Compose
**Applies to:** `mobile-engineering`

---

## Why this exists

A Compose composable that owns its own `mutableStateOf` is hard to preview, hard to test, and hard to reuse because the state is hidden inside it. State hoisting — moving state up to the caller and passing it in as a parameter along with a lambda to change it — makes composables stateless, predictable, and testable in isolation. Stateless composables also recompose only when their inputs change, improving performance. This is the same pattern as React's controlled components applied to Compose.

## How to apply

```kotlin
// Stateful (anti-pattern for reusable composables)
@Composable
fun NameInput() {
    var name by remember { mutableStateOf("") }
    TextField(value = name, onValueChange = { name = it })
}

// Stateless (correct — state hoisted to the caller)
@Composable
fun NameInput(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    TextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier,
    )
}

// ViewModel holds the state; the screen composable connects them
@Composable
fun CreateUserScreen(viewModel: CreateUserViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    NameInput(
        value = uiState.name,
        onValueChange = viewModel::onNameChanged,
    )
}
```

**Do:**
- Pass state down as parameters and event callbacks up (single-direction data flow).
- Keep `remember { mutableStateOf(...) }` at the screen/ViewModel level, not inside leaf composables.
- Use a sealed class or data class `UiState` to pass a coherent state snapshot to screen composables.
- Use `rememberSaveable` (not `remember`) for state that must survive configuration changes.

**Don't:**
- Put business logic inside composables — that belongs in the ViewModel.
- Use `mutableStateOf` inside a deeply nested composable for state shared with siblings.
- Hoist state so high it becomes global — hoist to the lowest common ancestor of the components that need it.

## Edge cases / when the rule does NOT apply

Purely internal UI state (animation progress, hover state, dropdown open/closed) that is not observable to the ViewModel may stay local inside the composable. `AnimatedVisibility` state is a typical example of legitimate internal state.

## See also

- [`../agents/android-engineer.md`](../agents/android-engineer.md) — owns Jetpack Compose implementation.
- [`./respect-the-lifecycle.md`](./respect-the-lifecycle.md) — lifecycle scopes govern ViewModel lifetime and `rememberSaveable` restoration.

## Provenance

Android developer documentation on state hoisting in Compose (developer.android.com/jetpack/compose/state). Codifies `android-engineer`'s Compose data-flow discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
