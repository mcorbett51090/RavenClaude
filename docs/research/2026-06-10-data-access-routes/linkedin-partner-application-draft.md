# LinkedIn Partner Program — application draft (Route B)

> **Status:** DRAFT for Matt's review. Fill the `〈…〉` placeholders, confirm the legal entity, then submit at <https://developer.linkedin.com/> → *Create app* → request the relevant product. **This route is for managing/measuring your OWN org's content — not third-party data extraction** (LinkedIn grants ~no new extraction access; that's Route A via Vibe-Prospecting, or Route C via your own export). Sourced from [Microsoft Learn — getting access](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access) (verified 2026-06-10).

---

## 0. Which product to request

| If you want to… | Request | Notes |
| --- | --- | --- |
| Post to / pull analytics for **your own** company page; manage comments | **Community Management API** | The realistic, grantable ask for an org managing its own presence. |
| Run ads / page-level marketing analytics | **Marketing Developer Platform** | Heavier review; only if you actually run LinkedIn ads. |
| "Sign in with LinkedIn" on your own app | **Sign In with LinkedIn (OpenID Connect)** | Self-serve, no partner review — separate from the above. |

**Recommendation:** request **Community Management API** for the company page. Don't over-ask — extra products lengthen review and invite rejection.

---

## 1. App + company details (fill in)

- **App name:** 〈Closebook〉 / 〈RavenPower〉 company-page manager
- **LinkedIn Company Page:** 〈URL of the page the app will manage〉 (you must be an **admin** of it)
- **Legal entity:** 〈Registered company name + country of incorporation〉 — *required; individual developers are not eligible.*
- **Website:** 〈https://…〉
- **Privacy policy URL:** 〈https://…/privacy〉 (LinkedIn checks this exists)
- **App logo:** 〈square PNG〉
- **OAuth redirect URL(s):** 〈https://…/auth/linkedin/callback〉

## 2. Use-case description (paste, then tailor)

> 〈Company〉 operates the LinkedIn Company Page at 〈page URL〉. We are requesting Community Management API access to **manage our own organization's presence**: scheduling and publishing first-party posts (text/image/article), retrieving **our own** page's content analytics (impressions, engagement, follower growth) to measure content performance, and moderating comments/reactions on our own posts.
>
> The integration acts **only on behalf of our own organization**, authenticated by an admin of the page via OAuth. We do **not** request, store, or process third-party member data, and we will **not** scrape, bulk-export, resell, or share LinkedIn data outside this approved use case. Data retrieved is limited to our own page's content and aggregate analytics, retained only as needed to render our internal content dashboard, and handled per our privacy policy at 〈URL〉.

## 3. Scopes to request (Community Management)

- `r_organization_social` — read our org's posts + their social actions/analytics
- `w_organization_social` — publish posts on behalf of our org
- `rw_organization_admin` — read page analytics / manage as admin
- *(plus `openid profile email` if you also add Sign In with LinkedIn)*

Request the **minimum** that covers post + analytics + moderation; unused scopes raise review friction.

## 4. Compliance checklist (LinkedIn looks for these)

- [ ] You are an **admin** of the company page the app manages.
- [ ] Acting **on behalf of your own org only** — no third-party member data.
- [ ] **No scraping / bulk export / resale / off-purpose sharing** stated explicitly (it's in the use-case text above).
- [ ] A real, reachable **privacy policy URL**.
- [ ] Data minimization + retention stated.

## 5. After approval — what I can build

Once you have the **client id + secret** (store as env vars / CI secrets, never commit), I'll build a fetcher/poster in the same shape as [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py):

- `linkedin-org.py --analytics` → pull your page's post analytics into `docs/research/…` or a dashboard feed.
- `linkedin-org.py --post --file draft.md` → publish a first-party post (human-gated; never auto-posts).

Same discipline as the Reddit script: official OAuth, stdlib-only, creds from env, fails loudly without them, no scraping surface.

---

## Realistic expectations (honest)

- Review takes **weeks to months**; data-*extraction* framing gets rejected — keep it strictly "manage our own page."
- If the goal was ever third-party prospect data, this route **won't** deliver it — use **Route A (Vibe-Prospecting MCP)** or **Route C (your own export)** instead. See [`README.md`](./README.md).
