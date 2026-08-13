# Phase 1 — Player-side pace product: technical spec

**Date:** 2026-08-11
**Decision taken:** player-first (see [on-course app brief](2026-08-11-on-course-app-brief.md) §3).
**Pilot site:** Cimarrone Golf Club, Jacksonville FL — semi-private, 18 holes, par 72, ~6,891 yds,
[public tee times available](https://www.cimarronegolf.com/).
**Evidence base:** [`docs/research/2026-08-10-golf-app-opportunities/`](../research/2026-08-10-golf-app-opportunities/README.md)

---

## 1. What Phase 1 is, in one paragraph

A golfer taps **Start Round**. The phone goes in their pocket. Four and a half hours later they have
a **Pace Card**: hole-by-hole elapsed time, split into *time they spent playing* versus *time they
spent waiting*, measured against the course's pace standard, exportable and shareable. It works at
any course. It requires nothing from the course. It is the only pace tool in the market held by the
player rather than bought by the operator.

**Nothing else ships in Phase 1.** No F&B, no cart tracking, no social, no shot tracking.

---

## 2. The core insight the product is built on

> **If you are standing on a tee box unable to hit, you are — by definition — not the group holding
> anyone up.**

Time spent stationary at a tee is not ambiguous, does not require knowing anything about the group
ahead, and is the single most defensible fact a golfer can hold. It is *direct* evidence of innocence.

This is what makes the product different from every pace system on the market. Those are bought by
courses to find slow groups. This one is carried by golfers to **prove they weren't one** — the
complaint with the highest engagement anywhere in the research corpus
([~3,800 upvotes](https://reddit.com/r/golf/comments/1sxjk7o/played_the_most_miserable_round_of_my_life_at/),
where a group was vindicated only when the resort pulled its own internal data).

Everything below serves producing that number accurately.

---

## 3. The pace algorithm

### 3.1 Inputs

| Input | Source | Notes |
|---|---|---|
| GPS fix stream | Device | `{lat, lon, accuracy, speed, timestamp}` @ 15–30 s |
| Hole geometry | Course map (§5) | Tee polygon, green polygon, centreline per hole |
| Tee time | User-entered or detected | Anchor for the cumulative benchmark |
| Pace standard | Course-published, else default | Cimarrone target TBC on site; default 4:15 |

### 3.2 Stage 1 — hole segmentation

Reduce a noisy fix stream to 18 clean `(hole, entered_at, exited_at)` intervals.

1. **Zone containment.** For each fix, test membership in every tee/green polygon (PostGIS
   `ST_Contains`, spatial index). Discard fixes with `accuracy > 25 m` before testing.
2. **Debounce.** A zone transition only counts after **≥3 consecutive fixes** inside, or ≥60 s dwell.
   Raw GPS will otherwise flicker across a polygon edge and shred the segmentation.
3. **Hole start** = first debounced entry into hole *n*'s tee zone after leaving hole *n−1*'s green.
4. **Hole end** = last debounced fix in hole *n*'s green zone before entering hole *n+1*'s tee zone.
5. **Monotonicity guard.** Holes must advance 1→18 (allow a configured shotgun start). An
   out-of-order match is a false positive — a green adjacent to another hole's tee, common at
   Cimarrone-era layouts with tight routing — and gets rejected.

### 3.3 Stage 2 — time attribution

Decompose each hole's elapsed time into buckets. **This is the product.**

| Bucket | Detection rule | Confidence |
|---|---|---|
| **Waiting (tee)** | Stationary (< 0.5 m/s) inside a tee polygon for > 90 s after arrival | **High** — observed, not inferred |
| **Waiting (fairway)** | Stationary > 90 s in the fairway corridor, not near a ball-search pattern | Medium |
| **Playing** | Movement along the hole centreline, plus short stationary bursts (shot routine) | High |
| **Green** | Dwell inside the green polygon | High |
| **Searching** | Stationary or slow-wandering **off** the centreline corridor, > 60 s | Medium |
| **Transit** | Movement green → next tee | High |

**Report confidence honestly.** "Waiting (tee)" is directly observed and should be stated as fact.
"Searching" is inferred from movement shape and should be labelled as an estimate. Overclaiming here
destroys the product's entire value, which is *credibility as evidence*.

### 3.4 Stage 3 — the benchmark

Two numbers, because they answer different questions:

- **Cumulative vs. standard** — `elapsed_since_tee_off` against the hole-by-hole expected curve.
  Answers *"are we behind?"*
- **Own-play time vs. standard** — the same, with all `Waiting` buckets subtracted. Answers
  *"is it us?"*

The gap between those two lines **is the whole argument.** A group can be 25 minutes behind the clock
while their own play is under standard — that is the case the golfer currently cannot make, and the
one the Reddit thread turned on.

### 3.5 Known limitation, stated up front

Without other app users nearby or course data, the app **cannot see the group ahead**. It infers
congestion from your own stationary time. That is sound for the tee case (you're stopped on a tee ⇒
the hole ahead isn't clear) and weaker elsewhere.

Do **not** paper over this. The Pace Card should show what was observed versus inferred. Once density
of users on the same course rises, cross-referencing anonymised positions gives true field awareness
— but that is a later network effect, not a Phase 1 promise.

---

## 4. The Pace Card (the deliverable artifact)

One screen, shareable as an image, exportable as PDF/CSV.

```
CIMARRONE GOLF CLUB          Sat 16 Aug 2026, 8:10 tee
────────────────────────────────────────────────────
Round time            4:52      Standard 4:15   +37
Your play             3:58      Standard 4:15   −17   ← the headline
Waiting                 54 min  (41 on tee boxes)
────────────────────────────────────────────────────
Hole   Elapsed   Playing   Waiting   vs std
1      0:14      0:14      —         +1
...
7      0:31      0:12      0:19      +17   ⟵ backed up
────────────────────────────────────────────────────
Longest wait: 19 min on the 7th tee
```

Headline copy is the point: **"You waited 54 minutes. Your own play was 17 minutes under standard."**

---

## 5. Course geometry

Phase 1 needs one course. Hand-digitise Cimarrone: 18 tee polygons, 18 green polygons, 18
centrelines, traced from satellite imagery and corrected on a validation walk. Half a day of work.

Store as PostGIS geometries, `SRID 4326`, GiST-indexed. Model it as a normal course record from day
one — the pilot course is row #1, not a special case — so scaling is a data problem, not a rewrite.

**Scaling course data is the real cost of this product** and should be scoped before Phase 2:
commercial course-geometry licensing, or crowdsourced tracing from user GPS traces (your own users
walking a course produce exactly the centreline data you need — a genuine compounding asset).

---

## 6. Stack

Chosen rather than asked; rationale given so it can be overridden.

| Layer | Choice | Why |
|---|---|---|
| App | **React Native + Expo** | One codebase for both stores, OTA updates for fast pilot iteration. |
| Location | **`react-native-background-geolocation`** (Transistor) | Paid, and worth it. Both platforms' background-location quirks, battery heuristics, and motion detection are its entire product. Rolling this yourself is the classic way to lose a month. |
| Backend | **Supabase** | Postgres + **PostGIS** (the geo queries in §3 are native), Auth (covers "users can log in"), Row-Level Security, Realtime (already there for Phase 3 cart tracking). |
| Maps | MapLibre + satellite raster | Avoids per-view licence costs at pilot scale. |

Expo's own `expo-location` + `expo-task-manager` can do background tracking and is worth prototyping
with first — if it holds up over a full 4.5-hour round at Cimarrone, keep it and save the licence fee.
**Test that before buying.**

---

## 7. Permissions and battery — the implementation rules

From the brief §4, restated as build constraints:

- **Android:** start the `location`-type foreground service **while the app is visible** (user taps
  Start Round). This needs only `ACCESS_FINE_LOCATION` — **do not request
  `ACCESS_BACKGROUND_LOCATION`**, which would drag the app into Play's permission-declaration review
  ([docs](https://developer.android.com/develop/sensors-and-location/location/permissions/background)).
- **iOS:** `When In Use` + Location updates background mode + `allowsBackgroundLocationUpdates`.
  **Do not ask for `Always`** — its opt-in has fallen
  [below 50%](https://www.phonearena.com/news/iOS-background-location-tracking-down-sharply_id121785)
  and the product does not need it.
- `pausesLocationUpdatesAutomatically = false` (iOS will otherwise stop updates mid-round).
- Accuracy ~10 m, **not** `Best`. Distance filter 10–20 m.
- **End the session** on round completion, automatically. Tracking that outlives the round is the
  fastest way to earn a one-star review and a store complaint.
- **Budget: < 10% battery for 18 holes.** Measure it every pilot round; it is a release gate, not a
  nice-to-have. Golfers already resent
  [watches dying at hole 11](https://forums.golfwrx.com/topic/1978126-apple-watch-series-9-for-golf-or-is-the-battery-not-up-to-it/).

---

## 8. Data model (sketch)

```
users            id, auth_id, display_name, home_course_id
courses          id, name, geom_bounds, pace_standard_minutes
holes            id, course_id, number, par, tee_geom, green_geom, centreline_geom
rounds           id, user_id, course_id, tee_time, started_at, ended_at, status
fixes            id, round_id, ts, geom(Point), accuracy_m, speed_mps   ← raw, retention-bounded
hole_splits      id, round_id, hole_id, entered_at, exited_at,
                 playing_s, waiting_tee_s, waiting_other_s, green_s, searching_s, transit_s,
                 confidence
pace_cards       id, round_id, generated_at, payload_json, shared_token
```

`fixes` is the raw evidence and the privacy liability at once. Set an explicit retention window
(suggest: raw fixes 90 days, derived `hole_splits` and `pace_cards` indefinite), disclose it plainly,
and ship export + delete from day one. The receipts feature *needs* retention — which is precisely
why the policy must be deliberate rather than inherited from a default.

---

## 9. The Cimarrone pilot

The point of a home course is **ground truth**. Without it you cannot tell a working algorithm from a
plausible-looking one.

**Setup**
1. Digitise the 18 holes (§5); walk the course once to correct tee/green polygons.
2. Confirm the course's published pace standard and typical tee interval with the pro shop — the tee
   interval alone predicts congestion, and it is the [structural cause](https://reddit.com/r/golf/comments/1uf8qcs/abolish_tee_times_every_8_mins/) the app is meant to expose.

**Protocol — 6–10 rounds, varied conditions**
- Deliberately sample: early weekday (empty), Saturday morning (packed), and a shotgun/outing day.
- Every round, keep a **manual stopwatch log** per hole: arrival at tee, first shot, holed out. This
  is the ground truth the algorithm is scored against.
- Log phone battery at start and end, and phone model.

**Release gates**

| Metric | Target | Why this number |
|---|---|---|
| Hole segmentation accuracy | **≥ 95%** of 18 boundaries correct | One bad boundary corrupts two holes' splits. |
| Waiting-time error vs. manual log | **within ±2 min per round** | Below the threshold where a golfer would dispute the card. |
| Battery per 18 holes | **< 10%** | Product-killer above this. |
| Crash-free round completion | **100%** across pilot | A round that ends with no card is worse than no app. |

**The one question the pilot must answer:** *does the Pace Card tell a golfer something true that they
could not otherwise prove?* If the card ever says "you were waiting" when they were not — or misses a
wait they clearly experienced — the credibility premise collapses and the algorithm goes back to §3.

---

## 10. Explicitly out of scope for Phase 1

F&B ordering · cart tracking · mutual location · shot tracking · handicap · social/matchmaking ·
multi-course rollout. Each is Phase 2+ in the brief. Shipping the pace card well at one course beats
shipping six half-features everywhere.

---

## 11. Open items

1. **Where does the app code live?** This repo is a Claude Code plugin marketplace — application code
   does not belong here under `.repo-layout.json`. Needs a new repository; not created unilaterally
   since that is an outward-facing action.
2. **Cimarrone relationship.** Playing there as a neighbour is enough for the pilot — no permission
   needed to record your own rounds. A conversation with the pro shop becomes valuable at Phase 3.
3. **Pace standard.** Confirm Cimarrone's published target and tee interval on the next visit.
4. **Revenue model** — deferred to post-pilot. Note the research finding: resentment of the category
   leader is about [billing that continues after cancellation](https://reddit.com/r/golf/comments/1nqfsqn/reporting_arccos_shady_business_practices_to_ftc/ng6jbgu/),
   not price. One-time purchase or one-click cancellation is a free trust advantage.
