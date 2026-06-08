---
name: golden-path-design
description: "Author a golden path / paved road: scope the supported create-build-deploy-run journey for the common service shape, bake in defaults (CI, observability, security baseline, ownership), make the supported way the easiest way, and design the escape hatch so the 20% case stays allowed-but-unsupported."
---

# Golden Path Design

**Purpose:** define the opinionated, supported, easiest-by-design way to ship a service — with an
escape hatch — so teams choose it because it's the path of least resistance.

## Steps

1. **Find the 80% shape.** The common service/workload most teams build. If everything is bespoke,
   don't force a path yet — gather the common shape first.
2. **Pave create -> build -> deploy -> run.** Each step has a supported, automated default.
3. **Bake in the defaults a team should get for free:** CI wiring, observability/telemetry, a security
   baseline, and an owner + catalog entry. A service created on the path is already instrumented and
   owned.
4. **Make it the lazy way.** If doing it right is harder than rolling your own, it isn't paved — keep
   removing friction until the supported way wins on ergonomics.
5. **Design the escape hatch.** Stepping off the road is *allowed and unsupported*. Document what
   "off-road" means and how to get back on.
6. **Watch the escapes.** A recurring escape is a signal — fold it into a new supported variant.

## The create step

The paved road's entry point is usually a **software template / scaffolder** (built with
`idp-portal-engineer`) that drops a team onto the road already wired. A template that creates an empty
repo with none of the wiring is a fancy `cookiecutter`, not a golden path.

## Anti-patterns

- A path with no escape hatch (the cage -> shadow platform).
- A "supported" way that's harder than the DIY way.
- Defaults missing observability, security baseline, or ownership.
- A create step that doesn't actually wire the road.

## Output

A golden-path spec — use [`../../templates/golden-path-spec.md`](../../templates/golden-path-spec.md).
Hand the create step to `idp-portal-engineer`, the pipeline to `devops-cicd`, the modules to
`terraform-iac`/`cloud-native-kubernetes`.
