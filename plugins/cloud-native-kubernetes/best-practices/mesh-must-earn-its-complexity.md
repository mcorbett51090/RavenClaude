# A service mesh must earn its complexity

Sidecars add latency, memory, and operational surface. Install a mesh only when you need mTLS-everywhere, fine-grained traffic-splitting, or mesh-wide per-call resilience across many services — and name which one you're buying. For simple exposure, Gateway API ingress plus app-level resilience and NetworkPolicies is the lighter, better answer.
