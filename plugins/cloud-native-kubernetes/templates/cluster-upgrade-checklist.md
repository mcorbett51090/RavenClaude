# Cluster upgrade checklist

- [ ] Read the target version's deprecated/removed API guide
- [ ] Audit manifests for removed APIs (e.g. with a checker)
- [ ] Test in a non-prod cluster of the same version
- [ ] Confirm add-on (CNI/CSI/mesh) compatibility
- [ ] Stay within control-plane↔node version-skew policy
- [ ] Drain nodes respecting PodDisruptionBudgets
- [ ] Rollback posture defined (node pool / control-plane)
