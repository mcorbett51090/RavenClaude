# Prefer for_each over count for collections

`count` indexes resources by position, so removing or reordering an element forces destroy/recreate of everything after it. `for_each` keys by a stable identifier, so the collection can change without churning unrelated resources. Use `count` only for a true 0/1 conditional.
