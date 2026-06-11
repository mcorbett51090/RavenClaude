---
name: conference-talk-and-cfp-strategy
description: "Win the CFP and give a talk that converts — choose a problem-first angle reviewers accept, structure the talk around a developer's job-to-be-done, design the post-talk activation path, and measure the talk by activations rather than applause."
---

# Conference Talk & CFP Strategy

**Purpose:** get accepted to the right talks and give ones that move developers toward value — a talk
that ends in applause but no activations is a vanity win.

---

## Steps

### 1. Pick the talk that fits the funnel stage

Most conference talks live at the **awareness** or **evaluation** stage. Don't try to make a talk do
activation's job — its goal is to make developers want to try, then route them to the quickstart that
activates them.

### 2. Write a problem-first CFP angle

Reviewers accept talks that solve a problem their audience has, not product tours. The winning angle
names a real, specific developer pain and promises a concrete takeaway:

- Weak: "Introduction to our Platform"
- Strong: "Cutting cold-start latency from 800ms to 80ms: what actually worked"

A title a developer would search for is a title a reviewer accepts.

### 3. Structure around the job-to-be-done

Open with the problem the audience feels, show the journey (including what didn't work), land the
technique, and prove it with something runnable. Avoid the feature-list march; developers tune out
the moment a talk becomes a brochure.

### 4. Design the post-talk activation path

Decide before submitting how the talk converts: a short URL to a repo, a quickstart, a sandbox the
audience can open during or right after. A talk with no activation path leaks its entire audience the
moment it ends.

### 5. Measure by activations, not the room

Track post-talk repo visits, quickstart starts, and activations attributable to the talk via
[`../../scripts/devrel_calc.py`](../../scripts/devrel_calc.py) `content_roi`. Applause and headcount
are inputs; activations are the outcome (constitution rule 2).

---

## Output

A CFP angle, a talk outline anchored on the job-to-be-done, the post-talk activation path, and the
measurement plan. Use the [`conference-talk-brief`](../../templates/conference-talk-brief.md) template.
