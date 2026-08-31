#!/usr/bin/env bash
#
# canary-undelivered-channel.sh — THE PERMANENTLY-RED CANARY. Plan P4.4.
#
# ⛔ DO NOT "FIX" THIS FILE. IT IS WRONG ON PURPOSE, FOREVER.
#
# This fixture writes its sentinel to STDERR and exits 0 — a channel measured to
# reach the model on NO event. inventory-sweep.py probes it with an assertion
# that the sentinel arrives on the DELIVERED channel (hookSpecificOutput
# .additionalContext on stdout). That assertion therefore CANNOT succeed.
#
# It mirrors the incident this whole initiative exists to close: five advisory
# hooks spent their entire service life writing to a channel nothing read, with
# every test passing, because the tests asserted on stderr — which is what the
# hooks produced. The tests could not fail.
#
# ⛔ WHY A PERMANENTLY-RED FIXTURE IS THE ONLY THING THAT MAKES A GREEN SWEEP
# READABLE. In steady state a static check-class reporting zero findings for many
# consecutive runs is EXPECTED, and is not by itself evidence of blindness. So a
# long green streak cannot distinguish "nothing broke" from "the sweep stopped
# looking". This fixture is the discriminator: if the sweep ever reports it
# PASSING, the sweep is broken and its own gate fails loud.
#
# If you are here because a run reported this canary GREEN: do not edit this
# file. Find what changed in the sweep assertion or in the delivered-channel
# contract. A green canary is a finding, not a chore.

set -uo pipefail

# stderr at exit 0. Measured: reaches the model on no event.
echo "canary-sentinel: this line is written to a channel nothing reads" >&2

# ⛔ NOTHING is written to stdout. Emitting an additionalContext envelope here
# would make the canary pass and silently disarm the only control that separates
# a working sweep from a blind one.
exit 0
