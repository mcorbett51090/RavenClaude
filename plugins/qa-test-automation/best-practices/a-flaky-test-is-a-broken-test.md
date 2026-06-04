# A flaky test is a broken test

Intermittent failures destroy the suite's signal and train the team to ignore red. Never normalize 're-run until green'. Fix the determinism (condition waits, isolation, faked time/RNG) or quarantine the test out of the required gate with an owner and a deadline.
