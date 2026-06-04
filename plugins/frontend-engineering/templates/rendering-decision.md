# Rendering strategy decision

| Route | SEO? | Personalized? | Interactivity | Strategy |
|---|---|---|---|---|
| /(marketing) | yes | no | low | SSG |
| /blog/[slug] | yes | no | low | ISR |
| /dashboard | no | yes | high | CSR (or RSC shell) |
| /product/[id] | yes | partial | medium | SSR / RSC |

RSC: default server components; hydrate interactive islands.
