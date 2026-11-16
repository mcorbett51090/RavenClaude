# Sources (all checked 2026-11-15)

## GitHub docs and changelog
- Self-hosted runners reference (routing, autoscaling, ephemeral, updates, domains): https://docs.github.com/en/actions/reference/runners/self-hosted-runners
- Choosing the runner for a job (`runs-on`, labels, groups): https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- Runner scale sets concept: https://docs.github.com/en/actions/concepts/runners/runner-scale-sets
- REST API, self-hosted runners (JIT config, tokens, labels, deprecations): https://docs.github.com/en/rest/actions/self-hosted-runners
- Secure use reference (self-hosted hardening, JIT): https://docs.github.com/en/actions/reference/security/secure-use
- Runner as a service (svc.sh, launchd, needrestart): https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application
- Removing runners (14-day / 1-day auto-removal): https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/remove-runners
- Customising job containers (container hooks): https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/customize-containers
- ARC 0.14.0 (multi-label scale sets, scaleset client): https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0/
- ARC 0.15.0: https://github.blog/changelog/2026-10-01-actions-runner-controller-release-0-15-0/
- Runner version enforcement date: https://github.blog/changelog/2026-09-28-self-hosted-runner-version-enforcement-date-has-moved/
- Minimum version enforcement timeline: https://github.blog/changelog/2026-06-12-github-actions-minimum-version-enforcement-timeline-for-self-hosted-runners/
- Actions pricing update and postponed self-hosted fee: https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/
- Cache can exceed 10 GB (billed): https://github.blog/changelog/2025-11-20-github-actions-cache-size-can-now-exceed-10-gb-per-repository/
- Runner groups (organisations): https://github.blog/changelog/2024-10-17-actions-runner-groups-now-available-for-organizations-on-free-plan/

## Upstream projects
- actions/runner releases (v2.338.2 notes): https://github.com/actions/runner/releases/tag/v2.338.2
- actions/runner#3862 (lost communication): https://github.com/actions/runner/issues/3862 · #2040: https://github.com/actions/runner/issues/2040
- actions/scaleset (Go client, examples/dockerscaleset): https://github.com/actions/scaleset
- actions/actions-runner-controller: https://github.com/actions/actions-runner-controller
- cloudbase/garm and its pools doc: https://github.com/cloudbase/garm · https://github.com/cloudbase/garm/blob/main/doc/pools-and-scaling.md
- github-aws-runners/terraform-aws-github-runner: https://github-aws-runners.github.io/terraform-aws-github-runner/
- Podman container hooks: https://github.com/UniversityofWarwick/github-runner-podman-hooks

## macOS / Apple Silicon
- Tartelet: https://github.com/framna-dk/tartelet
- Tart on-demand runners and the 2-VM limit: https://github.com/cirruslabs/tart/issues/237
- apple/container, the VM limit discussion: https://github.com/apple/container/discussions/234
- Joseph Duffy, self-hosting macOS runners: https://josephduffy.co.uk/posts/self-hosting-macos-github-runners
- Mac runner sleep and LaunchAgent behaviour: https://keepmacawake.com/blog/github-runner-mac-sleep
- Mac mini runner as a LaunchDaemon: https://aipps.dev/articles/self-hosted-mac-mini-runner-github-actions-keychains-xcodes
- workerd linux-arm64 package: https://www.npmjs.com/package/@cloudflare/workerd-linux-arm64
- ARM runner gotchas: https://dev.to/kalemi/github-actions-arm-runners-what-breaks-when-you-switch-1kb2

## Linux resources, Node and tests
- systemd resource control: https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html
- libuv cgroup parallelism: https://github.com/libuv/libuv/pull/4278 · https://github.com/libuv/libuv/issues/5375 · https://github.com/nodejs/node/issues/58428
- vitest maxWorkers / pool: https://vitest.dev/config/maxworkers · https://vitest.dev/config/pool
- Matching test workers to cores: https://berrybox.io/playbooks/slow-tests/match-workers-to-cores
- WSL config: https://github.com/MicrosoftDocs/WSL/blob/main/WSL/wsl-config.md · https://github.com/microsoft/WSL/discussions/9245
- GitLab runner fleet sizing guide (cross-check): https://docs.gitlab.com/topics/runner_fleet_design_guides/gitlab_runner_fleet_config_and_best_practices/

## Cost round-ups (secondary)
- RunsOn fee status: https://runs-on.com/blog/github-self-hosted-runner-fee-2026/
- Lizard pricing: https://lizard.build/blog/github-actions-pricing
