---
scenario_id: 2026-06-05-netcode-lag-rollback
contributed_at: 2026-06-05
plugin: game-development
product: generic-multiplayer
product_version: "unknown"
scope: likely-general
tags: [netcode, rollback, client-prediction, lag, authority, fighting-game, reconciliation]
confidence: medium
reviewed: false
---

## Problem

A fast-paced 1v1 fighter felt great on LAN and "laggy and unfair" online. Inputs felt mushy, hits that visibly connected didn't register, and players on a 90 ms connection said the game "rubber-banded." The build used a **lockstep / delay-based** model: every client waited for the remote input before advancing the frame, so the whole match ran at the speed of the slowest connection. The instinct was "add an interpolation buffer to smooth it." For a precise fighter, that would have made it worse — more buffer means more input delay.

## Context

- Engine-agnostic multiplayer (the model choice — delay-based lockstep vs rollback vs server-authoritative with prediction — is the load-bearing decision, independent of engine).
- Genre: precision fighting game. **Input latency is the felt metric** — every added frame of delay is perceptible to the players this genre attracts. This constraint drives the whole answer.
- 2 players, peer-to-peer, deterministic simulation already in place (a prerequisite that happened to hold here).
- Delay-based lockstep ties local responsiveness to the remote ping: a 90 ms opponent meant ~5-6 frames of input delay on a 60 Hz sim for *both* players.

## Attempts

- Tried: adding an interpolation/jitter buffer. Outcome: smoother visuals, *worse* feel — it added latency to the one metric this genre cannot spend. A buffer trades latency for smoothness; a fighter needs the opposite trade.
- Tried: classifying the game against the netcode-model decision before writing more code. A precision PvP title with a deterministic sim and a hard input-latency ceiling is the textbook case for **rollback netcode** — predict the remote input locally, advance immediately, and re-simulate ("roll back") the few frames when the real input arrives and differs. Outcome: identified rollback as the right model, not more buffering.
- Tried (the fix): implemented client-side **prediction + rollback** — advance the local sim on predicted remote input with zero added delay, store a short ring of confirmed states, and on a misprediction roll back to the last confirmed frame and re-simulate forward. Capped the rollback window so a spike can't re-simulate an unbounded number of frames. Outcome: local input felt instant regardless of ping; the only visible artifact was an occasional small correction on the *remote* character — the right place to spend the error for this genre.

## Resolution

**Pick the netcode model from the genre's felt metric before writing networking code — adding a buffer is not a substitute for the right model.** The reasoning:

1. **Name the metric the genre cannot spend.** A precision fighter spends *nothing* on input latency; an MMO or a turn-based game spends latency freely and cares about consistency/scale instead. The felt metric selects the model.
2. **Delay-based lockstep** ties your responsiveness to the worst ping in the match — fine for slow/lockstep-tolerant games (RTS with many units), disqualifying for a twitch fighter.
3. **Rollback** (client prediction + re-simulation) keeps local input instant and hides latency on the *remote* entity, at the cost of needing a **deterministic simulation** and a bounded rollback window. It is the standard answer for precise low-player-count PvP.
4. **Server-authoritative with client prediction + reconciliation** is the answer when you need an authority for anti-cheat or many players (shooters, battle royale) — prediction for feel, the server for truth.

The trap: "it's laggy → smooth it with a buffer." Smoothing adds the exact latency a twitch genre can't afford. The lag complaint was a *model* problem, not a tuning problem.

**Action for the next engineer:** before adding buffers or tuning interpolation on a "laggy" multiplayer game, classify it against the netcode-model tree — the genre's felt metric (input latency vs consistency vs scale vs anti-cheat) decides delay-based vs rollback vs server-authoritative, and rollback specifically requires a deterministic sim you may not have. Cross-reference [`../knowledge/gamedev-architecture-and-networking-decision-trees.md`](../knowledge/gamedev-architecture-and-networking-decision-trees.md) (the networking-model tree).
