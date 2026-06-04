# A backup is only real if the restore is tested

Automate backups and PITR to meet the RPO, but periodically restore them to a scratch environment to prove they work and measure the RTO. Untested backups fail silently — wrong scope, corrupt files, missing WAL — and you discover it during the incident, when it's too late. The restore drill is the actual deliverable.
