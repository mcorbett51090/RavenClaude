# Desktop release signing & update checklist

**Version:** <x.y.z>  **Channel:** <stable | beta>  **Date:** <YYYY-MM-DD>

## Signing

- [ ] macOS: Developer ID signed + hardened runtime
- [ ] macOS: `notarytool` submitted + ticket **stapled**
- [ ] Windows: Authenticode signed (EV cert for instant SmartScreen trust)
- [ ] Linux: AppImage/deb/rpm signed per target convention
- [ ] Keys sourced from CI secrets / HSM (never a laptop)
- [ ] Built artifact signature verified before publish

## Auto-update

- [ ] Update artifact signed; client verifies signature **before** apply
- [ ] Rollout staged (start %: ____ → widen on healthy metrics)
- [ ] Rollback path verified
- [ ] Version floor set: ____ (clients below are force-migrated)

## Native integration sanity

- [ ] Single-instance lock + deep-link/file-association handoff tested
- [ ] Tray / menus / notifications correct per OS

**Sign-off:** <who> — CI pipeline mechanics owned by `devops-cicd`.
