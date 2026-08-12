# On-Course App — product brief and build plan

**Date:** 2026-08-11
**Input:** iOS + Android app. Login. Background location. Pace-of-play tracking, refreshment-cart
location, in-app food ordering with direct-to-player delivery, mutual player↔cart tracking, plus
"other low hanging fruit."
**Evidence base:** [`docs/research/2026-08-10-golf-app-opportunities/`](../research/2026-08-10-golf-app-opportunities/README.md)

---

## 1. The headline: this exact product already ships, from at least six companies

Checked **2026-08-11**. The described feature set — GPS ordering, delivery to the player's exact
position, live cart tracking — is not a gap. It is a category.

| Product | What it already does |
|---|---|
| **[Fareplay Golf](https://apps.apple.com/us/app/fareplay-golf/id6762677492)** | Browse menu, order, pay, and **watch the cart come to you on a live map with real-time GPS**. This is the described feature, shipped. |
| **[ClubGrub](https://clubgrubapp.com/golfers)** | GPS food/drink ordering delivered to your exact location; explicitly markets itself as improving pace of play; ships a dedicated cart-attendant app. |
| **[BevCarts](https://www.bevcarts.com/)** | Real-time location of the nearest beverage cart, plus summon-the-cart. |
| **[RoundRobin](https://roundrobingolf.com/)** | Order from anywhere, straight to the kitchen, GPS routing to the player — **integrated directly with the course POS**. |
| **[FAIRWAYiQ](https://www.fairwayiq.com/)** | Pace-of-play management **and** F&B ordering, cart screens. 350+ properties, 10+ years. |
| **[Tagmarshal](https://www.tagmarshal.com/)** · **[Gallus](https://gallusgolf.com/app-features/food-beverage-ordering)** · **[Lightspeed](https://www.lightspeedhq.com/golf/pos/golf-restaurant/order-ahead/)** | Pace tracking, cart GPS, F&B ordering, order-ahead — all as course-purchased platforms. |

This is the same discipline the research applied to the other 30 concepts, turned on this one. It
would have been easy — and useless — to write an enthusiastic spec instead.

**This does not mean don't build.** It means the differentiation cannot be the feature list, and the
plan below is built around where the actual opening is.

---

## 2. The structural problem, and it is the important part

Everything in that table is **sold to the golf course**, because the described product structurally
requires the course:

- the refreshment cart is course staff, on a course-owned cart
- the menu, pricing, kitchen, liquor licence and payment are course business
- pace data is most useful to the course's own operations

So building this means **B2B sales against incumbents with a decade of head start and POS
integrations** (RoundRobin's POS link is a genuine moat — it removes duplicate menus and new staff
workflows, which is the actual objection a GM raises).

It also collides with the goal stated at the start of this project — *every golfer thinks they need
this*. An app that only works at partner courses **cannot** reach every golfer. It reaches the
golfers at the courses you have already sold. That is a fundamentally different, slower business.

### The chicken-and-egg, stated plainly

| | Incumbent model | What it costs you |
|---|---|---|
| Who must say yes first | The course | Nothing works until a GM signs. Golfer has zero reason to install at a non-partner course. |
| Golfer value at a non-partner course | **Zero** | Install base cannot grow ahead of sales. Every new market restarts from nothing. |

---

## 3. The recommendation: invert it

**Build the player-side product first — the part that works at every course on earth with no course
involvement — and add F&B only where a course opts in.**

The research found exactly one thing in this space that nobody sells to golfers, and it is backed by
the single highest-engagement complaint in the entire corpus:

> **Golfers have no objective record of their own pace when staff accuse them of being slow.**
> ~3,800 upvotes. One group was accused repeatedly across a round and only vindicated when the resort
> pulled its *own* internal tracking data.
> — [thread](https://reddit.com/r/golf/comments/1sxjk7o/played_the_most_miserable_round_of_my_life_at/)

Every pace product listed above is bought by the course, so **the course owns the data and the
golfer is defenceless**. A player-held pace record flips that. Nobody sells it. It needs no course
adoption, no POS integration, no sales cycle — it works the first time a golfer opens it, anywhere.

That is the wedge. F&B becomes the *monetisation layer* you add once you have golfers, and at that
point you walk into a GM's office with installed users at their course rather than a cold pitch.
That reverses the incumbents' advantage instead of attacking it head-on.

**If you would rather go straight at the F&B market**, that is a legitimate choice — the revenue is
real and immediate — but then treat it as a **sales-led B2B company**, not an app company, and the
first hire is a salesperson, not an engineer. Budget for POS integrations (Lightspeed, Jonas, Club
Prophet, ForeUp) as table stakes. Be deliberate about which business you are starting.

---

## 4. Technical design: background location without wrecking the app

This is where naive designs die. Three findings that should shape the architecture from day one.

### 4.1 You probably do not need the scary permissions

**Android — this is the big one.** A foreground service of type `location` **started while the app is
visible** needs only `ACCESS_FINE_LOCATION`. `ACCESS_BACKGROUND_LOCATION` is required only to start
such a service *from the background*
([developer.android.com](https://developer.android.com/develop/sensors-and-location/location/permissions/background)).

Because a golf round is explicitly user-initiated — the golfer taps **Start Round** — you can start
the foreground service in the foreground, every time, and **never request `ACCESS_BACKGROUND_LOCATION`
at all.** That sidesteps the entire Google Play permission-declaration review, where apps must prove
background location is core functionality, submit a demo video, and survive Data-Safety
cross-referencing against the binary
([Play Console](https://support.google.com/googleplay/android-developer/answer/9799150)). Skipping
that removes a major rejection risk and an ongoing compliance burden.

**iOS.** `When In Use` + `allowsBackgroundLocationUpdates = true` + the Location updates background
mode gives continuous tracking while backgrounded, with the blue status-bar indicator. You do **not**
need `Always` for a user-started round. That matters: iOS "always" opt-in has fallen from near-100%
to [often under 50%](https://www.phonearena.com/news/iOS-background-location-tracking-down-sharply_id121785).
Asking for `Always` would halve your usable install base to buy a capability the product does not need.

**Design rule: the round is a session with a clear start and end.** It makes the permission story
honest, the battery story tractable, and the store review boring. Boring is the goal.

### 4.2 Battery is a product feature, not an implementation detail

The research is unambiguous that golfers already resent this: GPS watches
[dying by hole 11](https://forums.golfwrx.com/topic/1978126-apple-watch-series-9-for-golf-or-is-the-battery-not-up-to-it/),
and one golfer measuring phone-GPS fiddling as adding
[~an hour to a round](https://reddit.com/r/golf/comments/wdgmfi/12_feet_auto_putts_or_300_yard_straight_drives_i/).
A round is 4–5 hours and the golfer needs a working phone afterwards.

- Do **not** use `kCLLocationAccuracyBest`. Ten-metre accuracy is ample for hole-level pace.
- Distance filter ~10–20 m; sample on the order of 15–30 s, not continuously.
- Consider geofence/region monitoring around tees and greens as the low-power backbone, with
  fine-grained sampling only near a pending delivery.
- **Publish the number.** "Uses about 8% battery for 18 holes," measured and honest, is a marketing
  asset in a category where everyone else drains the phone.

### 4.3 Mutual tracking is a people problem before it is a technical one

- **The cart attendant is an employee being location-tracked at work.** That carries labour and
  privacy obligations that vary by jurisdiction, and it needs on-shift-only tracking, a visible
  indicator, and a hard off switch. Get it wrong and you lose the account, not just the feature.
- **Golfer-to-staff visibility should be asymmetric and scoped.** The attendant needs your position
  *while an order is active*, not all round. Default to the minimum and make it expire.
- **Retention is a deliberate choice, not a default.** The pace-receipts feature *requires* keeping
  track history — so decide the window on purpose, disclose it plainly, and let users export and
  delete. This is the one place where storing more data is the point rather than a liability, which
  is exactly why it needs an explicit policy.

### 4.4 Alcohol is a regulated product — flagged because it was not mentioned

Beverage carts sell alcohol. In-app alcohol ordering pulls in age verification, the course's liquor
licence, service-refusal obligations to visibly intoxicated patrons, and liability exposure that
differs by state. `[unverified — not researched]` I have not investigated the specifics, and you
should before writing a line of ordering code. Practical mitigation: **the course holds the licence
and the attendant makes the final service decision in person** — the app takes the order, the human
completes the sale. Design the flow so the app never becomes the seller of record.

---

## 5. Recommended build sequence

**Phase 1 — Player-side, works everywhere, no course needed.**
Login, round session, background location done as in §4.1, live pace vs. the field, and the
**pace record** — an exportable, timestamped log of where the round's time actually went (searching,
putting, waiting on the group ahead, cart routing). This is the differentiator, the thing no
incumbent sells to golfers, and it needs nobody's permission to ship.

**Phase 2 — The insight that makes pace honest.**
Distinguish *your group was slow* from *you were stuck behind a slow group* from *the course sold
8-minute tee intervals*. That last one drew
[1,996 upvotes](https://reddit.com/r/golf/comments/1uf8qcs/abolish_tee_times_every_8_mins/) — a large
share of pace pain is structural, and an app that says "this wasn't your fault, here's the proof" is
doing something no course-bought tool will ever do, because the course is the one being indicted.

**Phase 3 — F&B, at courses that opt in.**
Now the pitch to a GM is "your golfers already use this" rather than a cold start. Build cart
tracking, ordering, and the attendant app. Expect POS integration to be the real cost.

**Phase 4 — Adjacent value.** See §6.

---

## 6. "Low hanging fruit" — ranked by evidence, not by ease

Drawn from the 30 concepts. The ones that share the location/session plumbing you are already
building, so marginal cost is low:

| Add-on | Why it earns a slot | Concept |
|---|---|---|
| **Pre-order for the turn** | A commenter proposed a QR code on the 7th tee and was [baffled it isn't standard](https://reddit.com/r/golf/comments/1uf8qcs/abolish_tee_times_every_8_mins/otqnytv/). Natural extension of the F&B work, and it directly helps pace. | #31 |
| **Self-calibrating yardage book** | Nobody knows their real distances or can look them up mid-round. Uses the location stream you already have. Publish confidence bands, not averages — averages are why golfers come up short. | #2 |
| **Zero-tap shot logging (voice)** | The loudest tech complaint is interaction burden: phone-poking after every hole. Voice is the only input that costs no attention and no pace. | #4 |
| **Lost-ball / provisional helper** | Marks likely landing area, runs the 3-minute clock, handles stroke-and-distance. Pure pace win, trivial given location. | #26 |
| **Beginner mode** | A beginner turning up with a bucket of range balls to play 18 drew [2,273 upvotes](https://reddit.com/r/golf/comments/1mo6iv9/using_range_bucket_to_play_18/). Nobody teaches new golfers the basics, and their fear of holding people up is the same problem as pace. | #15 |

**Deliberately not "low hanging," despite looking it:** side-game/bet settlement, AI rules
assistants, and used-club valuation are each already served by 4+ shipping apps. See the
[saturation scan](../research/2026-08-10-golf-app-opportunities/README.md#the-saturation-scan-what-already-exists).

---

## 7. Open questions that change the plan

1. **Which business are you starting** — player-first (§3, recommended) or sales-led B2B F&B? This
   determines the first hire and the first six months.
2. **Do you have a course relationship already?** One friendly course as a design partner changes the
   F&B timeline enormously. If you have one, Phase 3 could run in parallel rather than after.
3. **What is the revenue model** — subscription, F&B commission, or course licence? Note the research
   found the anger at Arccos is about *billing that continues after cancellation*, not price. A
   one-time purchase or genuinely one-click cancellation is a free trust advantage over the category
   leader.

---

## 8. Honest summary

The feature set as described is **already a competitive category**, sold to courses, with entrenched
incumbents and POS moats. Building it head-on is a sales business, not a product business.

The version worth building is the **player-side pace product** underneath it — which the research
identifies as genuine white space, backed by the highest-engagement complaint found anywhere in the
corpus, and which needs no course to say yes. The cart and F&B features are a strong Phase 3 that
becomes far easier to sell once golfers are already carrying the app.
