# Scenario: did the price increase actually work?

**The ask:** "We raised list prices 20% two quarters ago. ARPA is up 12% — win,
right? Marketing wants to announce it."

**Routes to:** `monetization-analyst` (read) — with a hard seam to `applied-statistics`.

**The answer shape:**
1. **Decompose before celebrating.** A 12% ARPA rise from a 20% list increase is
   suspicious — it can be a real lift *or* low-end churn dragging the average up, or a
   mix-shift toward larger new logos. Separate lift / mix-shift / cohort effects.
2. **Read the scoreboard, not the average:** pull **NRR, GRR, contraction, and new-
   business win-rate** on the affected cohorts (`monetization-metrics.md`). If GRR
   fell and contraction rose, the "ARPA win" is partly manufactured by losing cheap
   customers.
3. **Check realized, not list:** is the 20% holding net of discount, or did the field
   discount it back? Decompose **discount leakage** by segment.
4. **Mind the clock:** with annual contracts, two quarters may be **too early** —
   say so if a full renewal cycle hasn't turned.
5. **Route the significance:** whether the cohort difference is statistically real →
   `applied-statistics`. Report effect size + CI, not a bare "up 12%."
6. **Verdict:** a defensible "worked / didn't / too early" with the decomposition,
   not a headline.

**Why it's a good illustration:** "ARPA is up" is the single most common way to
*sound* analytical while saying nothing — decomposition and the retention scoreboard
are the whole job.
