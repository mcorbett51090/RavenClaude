# Pseudo-localize continuously

A pseudo-locale (accented characters, length inflated 30-40%+, strings bracketed) is the cheapest bug-finder in localization: it surfaces hardcoded strings, concatenation, and layout truncation/overflow *before* a cent is spent on real translation. Wire it in as a first-class locale and run it in CI on every PR — not just before a translation drop — so a newly hardcoded string or a fixed-width container is caught the day it's added, not three sprints later by a user in production.
