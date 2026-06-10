# Data-access routes — Reddit (the recurring scan) + LinkedIn (2026-06-10)

**Author:** `claude`
**Task:** "Research how to get around the [Reddit] block. I also want to get data from LinkedIn."
**Outcome:** Reddit automated via the **official API** (script shipped: [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py)); LinkedIn mapped to its three legitimate routes (one already wired in this session).

> **The boundary this doc holds.** "Around the block" here means the **sanctioned front door**, never circumvention. We do **not** spoof user-agents, rotate proxies, drive headless browsers against anti-bot, or use grey-market scrapers — those defeat an access control a site set deliberately, with real ToS/tort exposure. Everything below is an official API, a first-party export, or a purpose-built sanctioned data source.

---

## 1. Reddit — the block has a front door (DONE)

**The block is on Anthropic's crawler user-agent, not on Reddit's data.** A Claude Code session can't read subreddits via WebFetch/WebSearch (verified six ways — see [`../2026-06-10-claude-subreddit-scan/README.md`](../2026-06-10-claude-subreddit-scan/README.md) §1), but Reddit's **official OAuth2 Data API** is open and, for this repo's use, free.

**Why a committed script (not an MCP) is the recommended automated path:** it runs **headless in CI / locally without depending on an MCP being wired into every session**, persists into the existing `docs/research/*-claude-subreddit-scan/` pattern, is auditable + diffable, and carries zero new dependencies (stdlib-only). An MCP remains a fine *interactive* option (recommend-not-bundle, since it needs per-user creds + a security pass), but the script is the durable automation.

### Setup (~5 min, one-time)

1. Go to <https://www.reddit.com/prefs/apps> → **create another app** → type **script** → redirect URI `http://localhost:8080`.
2. Copy the **client id** (under the app name) and **secret**.
3. Export them (never commit them):

   ```shell
   export REDDIT_CLIENT_ID=...    REDDIT_CLIENT_SECRET=...
   ```

   In CI, store both as repository secrets and inject as env vars.

### Run

```shell
python3 scripts/reddit-scan.py \
  --subreddits ClaudeAI Claude ClaudeCode \
  --listing top --time month --limit 50 --min-score 25 \
  --out docs/research/$(date +%F)-claude-subreddit-scan/raw
```

Writes per-subreddit JSON + a `digest.md` table of kept posts. The next scan reads that real data instead of web-search aggregations — closing the provenance gap flagged in every scan so far.

### Tier / terms (verified 2026-06-10)

| | Free tier | Commercial |
| --- | --- | --- |
| Auth | OAuth2 required (this script uses app-only `client_credentials`) | same |
| Rate | ~100 req/min | contract-negotiated |
| Use | personal / **research** / open-source | any business use → **paid contract** (~$12k/yr for 100 rpm) |

The recurring scan is internal R&D → non-commercial. **One thing for Matt to confirm:** RavenClaude is a *private marketplace* and Closebook is commercial; if subreddit data ever feeds a monetized product, that crosses Reddit's commercial-use line and needs the paid contract. Sources: [Reddit Data API Wiki](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki) · [API pricing 2026](https://octolens.com/blog/reddit-api-pricing) · [script-app guide](https://redaccs.com/reddit-api-guide/).

> **Note on the required User-Agent:** Reddit's API *mandates* a unique, descriptive UA string. Setting one (the script does) is a documented API requirement that identifies the client honestly — the opposite of the UA-spoofing we refuse to do to evade the crawler block.

---

## 2. LinkedIn — "all of the above," mapped honestly

LinkedIn is the most aggressively anti-scraping site on the web. The legitimate routes fork hard by **what data + whose data**, so each leg below is mapped to its real, sanctioned path. **Direct scraping of profiles is off the table** — and note the *hiQ v. LinkedIn* nuance: scraping **public** data likely isn't a **CFAA** crime (9th Cir. 2022), but hiQ still **lost** on breach-of-contract + trespass-to-chattels + misappropriation (a **$500k judgment + permanent injunction**). "Not a federal crime" ≠ "allowed." ([hiQ — Wikipedia](https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn) · [Morgan Lewis](https://www.morganlewis.com/blogs/sourcingatmorganlewis/2022/12/linkedin-v-hiq-landmark-data-scraping-suit-provides-guidance-to-data-scrapers-and-web-operators))

### Route A — Prospecting / lead data → Vibe-Prospecting MCP (LIVE in this session, sanctioned)

If the goal is **leads / company / prospect data** (Closebook's likely ICP: SMB finance, fractional-CFO firms), the cleanest route doesn't touch LinkedIn at all: this session has the **`Vibe-Prospecting` MCP** (Explorium-backed) connected — a purpose-built, licensed B2B data source.

- **Flow:** `autocomplete` (free) → `fetch-entities` (sample, free) → `enrich-prospects` (contacts/profiles) → `estimate-cost` → `export-to-csv`.
- **Spend discipline (hard rule):** enrichment + export consume **Explorium credits**. The MCP itself enforces "never auto-export; always show a cost estimate and wait for explicit confirmation." I will **not** spend credits without (a) your **target criteria** (industry, geography, titles, company size, tech stack, intent topics) and (b) your sign-off on the cost estimate.
- **To fire it, give me the ICP**, e.g. *"US fractional-CFO / outsourced-accounting firms, 10–200 employees, titles: founder / managing partner / controller."* I'll run the free `autocomplete` + sample first, then an `estimate-cost`, then stop for your go/no-go before any export.

### Route B — Your own org's page (analytics / posts) → official Community Management / Marketing API

For **your own company page** content + analytics (post, pull engagement, manage comments on behalf of the org):

- Requires the **LinkedIn Partner Program** (incorporated company; the **Community Management API** / Marketing Developer Platform). Application = legal-entity verification + a specific use case; review takes weeks–months. ([Microsoft Learn — getting access](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access))
- **Feasible** for "manage/measure our own content"; **not** a path to bulk third-party profile data — LinkedIn has granted ~no new *data-extraction* API access since 2018. ([Clura 2026](https://clura.ai/blog/linkedin-api))
- **Next step (needs Matt):** decide whether to apply as RavenPower/Closebook. Once approved, you'd get a client id/secret + OAuth; I can then build a fetch/post script in the same shape as `reddit-scan.py`. I can draft the application's use-case text on request.

### Route C — Your own account/connections → official data export (I can process it)

For **your own** profile, connections, and activity, LinkedIn offers a **self-serve data export** (Settings → Data Privacy → *Get a copy of your data*). It returns CSVs (Connections, messages, etc.).

- **This is the one I can act on with zero approvals or spend** — download the export, drop the CSV(s) in the repo (or hand them to me), and I'll parse, dedupe, and shape them into whatever you need (e.g. a contacts table, a research input).
- **Next step (needs Matt):** request the export from LinkedIn (it emails a download link, usually within minutes–24h), then point me at the file.

---

## 3. What's done vs. your turn

**✅ Done (shipped this branch):**

- `scripts/reddit-scan.py` — official-API subreddit fetcher (stdlib-only, app-only OAuth, rate-limit-aware, fails loudly without creds). Syntax-checked; argparse + creds-missing paths smoke-tested.
- This route doc.

**👉 Your turn (each is one short action):**

1. **Reddit:** create the script-app at <https://www.reddit.com/prefs/apps>, set `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` (locally or as CI secrets). Then the recurring scan reads real data. *(Optional: confirm the non-commercial-use line is fine for now.)*
2. **LinkedIn A (prospecting):** send me the **ICP criteria** → I'll run free autocomplete + sample + a cost estimate, then stop for your go/no-go before any credit spend.
3. **LinkedIn B (own org):** say the word if you want me to draft the Partner Program use-case application.
4. **LinkedIn C (own export):** request your LinkedIn data export and point me at the CSV → I'll process it immediately.

---

## 4. Sources

- Reddit: [Data API Wiki](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki) · [pricing 2026](https://octolens.com/blog/reddit-api-pricing) · [script-app guide](https://redaccs.com/reddit-api-guide/)
- LinkedIn API: [Microsoft Learn — getting access](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access) · [Clura — what exists / what's restricted (2026)](https://clura.ai/blog/linkedin-api)
- Scraping legality: [hiQ Labs v. LinkedIn (Wikipedia)](https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn) · [Morgan Lewis analysis](https://www.morganlewis.com/blogs/sourcingatmorganlewis/2022/12/linkedin-v-hiq-landmark-data-scraping-suit-provides-guidance-to-data-scrapers-and-web-operators)
