# Tracking plan

| Event (object_action) | When | Properties (typed) | Version |
|---|---|---|---|
| signup_completed | after first auth | {method:string, plan:string} | 1 |
| checkout_started | on cart->pay | {cart_value:number, items:int} | 1 |

- Naming convention: object_action, snake_case. Typed + validated. Versioned.
- Identity: anonymous_id -> user_id on identify (stitching).
- Routed via CDP; warehouse copy -> data-platform.
