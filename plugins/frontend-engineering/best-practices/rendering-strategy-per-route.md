# Choose the rendering strategy per route

SSG/ISR for static content, SSR/RSC for personalized or SEO-critical pages, and CSR for behind-login interactive shells. Forcing one global rendering mode on the whole application guarantees a mismatch somewhere — a static page paying for client hydration, or a personalized page that can't render on the server. Decide per route by SEO, personalization, and interactivity needs.
