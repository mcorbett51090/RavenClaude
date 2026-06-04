# Component skeleton (typed, accessible)

```tsx
type Props = { items: Item[]; onSelect: (id: string) => void };

export function ItemList({ items, onSelect }: Props) {
  return (
    <ul role="list">
      {items.map((it) => (
        <li key={it.id}>
          <button data-testid={`item-${it.id}`} onClick={() => onSelect(it.id)}>
            {it.label}
          </button>
        </li>
      ))}
    </ul>
  );
}
```
- Typed props (no `any`). Semantic elements. Stable test ids. Composition over flags.
