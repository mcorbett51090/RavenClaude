# CollectUI
URL: https://collectui.com
Retrieved: 2026-09-01
Type: UI inspiration gallery (live, curated from Dribbble Daily UI)

## What's valuable here
CollectUI is a hand-curated gallery of real interface shots, organized around Dribbble's "Daily UI"
challenge — a canonical list of ~100 named UI-pattern categories (Sign Up, Pricing, Checkout,
Onboarding, Empty States, Dashboard, etc.), each with its own `/challenges/<slug>` page holding
hundreds of real designs. Its value isn't transcribable content — it's a **ready-made checklist of
UI-pattern names a design agent should recognize and browse live** before designing a matching
screen, so ideation starts from a broad current sample instead of one remembered layout.

**Verification note:** the homepage/nav chrome (Home / Designers / Categories / Trending /
Favorites, the sponsor network) was directly fetched and confirmed live. The actual gallery grids on
category pages did **not** render through WebFetch (JS-driven infinite-scroll content — the fetch
returned only nav chrome on `/challenges/pricing` too). Category names + live counts (e.g. "Pricing
(99)", "Checkout (276)", "Home Monitoring Dashboard (432)", "Onboarding (337)", "Sign Up (336)",
"Empty States (11)", "Landing Page (1825)") were confirmed via web search against real
`collectui.com/challenges/<slug>` result pages — verified as live categories, not fabricated. The
full ~100-name Daily UI challenge taxonomy below (which CollectUI organizes its archive around, per
its own "collects daily inspiration from the daily UI archive and beyond" description) was sourced
from a community-maintained list, cross-checked against the category names search confirmed live.

## Concrete extractable patterns/techniques
The categories, grouped by the page-type work they map to:

- **Auth & account entry** — Sign Up, Select User Type, Terms of Service, Password/Settings
- **Account & profile** — User Profile, Settings, Avatar, Badge
- **Commerce & checkout** — Credit Card Checkout, E-Commerce Shop (Single Item), Shopping Cart,
  Pricing, Redeem Coupon, Invoice, Email Receipt, Pre-Order, Currently In-Stock, Customize Product
- **Landing & marketing** — Landing Page (above the fold), Testimonials, F.A.Q., Press Page,
  Advertisement, Curated For You, Product Tour, News, Coming Soon, Thank You
- **Onboarding & first-run** — Onboarding, Splash Screen, Product Tour, Select User Type
- **Navigation & structure** — Header Navigation, Breadcrumbs, Dropdown, Pagination, Categories
- **Dashboards & data** — Home Monitoring Dashboard, Analytics Chart, Statistics, Leaderboard,
  Activity Feed, Trending
- **Search & discovery** — Search, Map, Location Tracker, Event Listing, Job Listing
- **Forms & inputs** — Form, Button, Calculator, EMI Calculator, Date Picker, Color Picker,
  Countdown Timer, File Upload, On/Off Switch, Dropdown
- **Feedback & status** — Flash Message (Error/Success), Notifications, Loading..., Progress Bar,
  Tooltip, Pending Invitation, Status Update, Empty States *(a live CollectUI category, though not
  a numbered Daily UI challenge — worth noting for empty-state work specifically)*
- **Messaging & social** — Direct Messaging, Social Share, Subscribe, Contact Us
- **Media & content** — Music Player, Video Player, Image Slider, Blog Post, Food/Drink Menu,
  Background Pattern, Icon Set
- **Booking & scheduling** — Calendar, Schedule, Hotel Booking, Flight Search, Boarding Pass,
  Confirm Reservation, Itinerary, Weather
- **Misc app-specific** — TV App, Car Interface, Workout Tracker, ToDo List, Crowdfunding Campaign,
  Notes Widget, Favorites, Info Card, Giveaway, Virtual Reality, Download App, App Icon

## Where this should feed into RavenClaude
- Recommend adding to: `plugins/web-design/skills/gold-standard-website-pipeline/SKILL.md` — G1
  Discovery / G2 IA could cite this taxonomy as the checklist for "which UI patterns does this
  site's page inventory actually need" before wireframing starts.
- Recommend adding to: `plugins/web-design/skills/conversion-design/SKILL.md` — its pricing-page,
  trust-signal, and CTA-copy sections already give prescriptive patterns; a live-gallery pointer for
  Pricing/Checkout/Testimonials categories complements the prescriptive rules with current visual
  range.
- Recommend adding to: `plugins/ravenclaude-core/skills/design-clone/SKILL.md` — when a user names a
  UI-pattern type rather than a reference URL ("give me a good empty state"), this taxonomy is the
  category list to browse before drafting, upstream of `design-clone`'s capture+apply flow.
- NOT a fit for `plugins/web-design/knowledge/design-references.md` (that file curates whole-site
  exemplars, not per-pattern galleries) — keep this as its own dated source file instead.

## Refresh recipe
- Re-check: consult this category list at the start of designing a given screen type (e.g. before
  building a pricing page, open `collectui.com/challenges/pricing` and browse current shots) — not a
  periodic re-verification task.
- What to watch for: n/a (live inspiration source, not versioned)
