# Evolve schemas with expand/contract

Change schemas in reversible steps across separate deploys: add the new structure safely, backfill in throttled batches, switch reads, then drop the old. Avoid DDL that takes a heavy lock on a hot table (volatile-default adds, type changes, non-concurrent index builds, blanket SET NOT NULL) by using the online-safe form. A big-bang blocking migration mid-traffic is a self-inflicted outage.
