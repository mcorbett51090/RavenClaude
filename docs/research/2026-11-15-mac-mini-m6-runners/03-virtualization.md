# 03: Native macOS, Linux VMs, and the tools around them

Checked 2026-11-16.

## Why the runners are Linux guests

The live Commerce CI guard, in `.github/workflows/commerce-ci.yml` on `main` (read 2026-11-16), exits if `RUNNER_OS` is not `Linux`, and then requires the legacy `box-…` name. A native macOS runner fails the first check even if its name matched. The pending name pattern (`rp-macmini-fast-1` and its siblings) still sits behind that Linux check. So a darwin runner cannot take a current Commerce CI job, and giving it `lane-fast` would only make those jobs fail after they had been assigned.

A native runner also shares the Mac user's files, keychain, and TCC permissions. A VM has its own kernel and its own disk. For pull-request code on a personal Mac, that boundary is the point.

Native macOS remains the right place for a future job that actually needs macOS (signing, a Mac-only toolchain). That job needs its own workflow, without this guard, and a label no current workflow requests (`lane-macos` is the name already reserved in the November research). Do not attach `lane-fast`, `lane-medium`, or `lane-slow` to it.

## The two-macOS-VM limit

The [macOS 27 software license](https://www.apple.com/legal/sla/docs/macOS27.pdf), section 2B(iii), read 2026-11-16:

> up to two (2) additional copies or instances of the Apple Software … within virtual operating system environments on each Apple-branded computer you own or control that is already running the Apple Software, for purposes of: (a) software development; (b) testing during software development; (c) using macOS Server; or (d) personal, non-commercial use.

The same clause forbids using those copies for a service bureau, time-sharing, or a similar service. Virtualization.framework enforces a two-guest ceiling for macOS as well; Tart's maintainers describe it as both a license rule and a framework limit ([tart discussion on the two-VM cap](https://github.com/cirruslabs/tart/issues/237), and the same point in the November research). Linux guests are not in that sentence and are not in that cap.

One personal mini does not need two macOS VMs. It needs zero, until a macOS-only job exists.

## Guest memory is a budget, allocated as the guest touches it

Apple's `VZVirtualMachineConfiguration.memorySize` documentation: the value is the physical memory the guest sees. The host reserves a contiguous virtual range and allocates pages on demand; it does not wire the whole size at boot. Under load the guest can occupy the whole cap. Size the Mac as if a busy VM uses all of its 6 GB. An idle VM costs less, which is why a coding-agent session and a busy medium job are the combination to avoid, not an idle VM by itself.

## Tool by tool

| Tool | What it is | For this machine |
|---|---|---|
| **Lima** | Linux VMs on Virtualization.framework (`vmType: vz`), arm64 guests, `limactl` | **The host of the two runners.** One Ubuntu 24.04 arm64 VM, left running |
| **Tart** (OpenAI, since 2026; previously Cirrus Labs) | Linked-clone VMs, macOS or Linux, on the same framework. Tartelet and similar loops do clone, boot, one job, delete | The tool to reach for if a job later needs a fresh VM per run. Two macOS VMs at once run about 12% slower than one (Tartelet, cited in the November doc). A 6 GB clone per job on a 16 GB Mac means one job at a time, plus boot time. That is a worse fit than one resident VM until isolation inside the guest is not enough |
| **UTM** | GUI front end on the same framework, plus qemu | Fine for a manual experiment. Worse to start at boot than Lima |
| **OrbStack** | Commercial Linux VM and Docker front end, fast on Apple silicon | A second hypervisor next to Lima. Skip it unless Lima fails a test we have not seen |
| **colima** | A Lima wrapper aimed at Docker | Pulls in a Docker daemon this factory's current jobs do not need |
| **Docker Desktop** | Its own Linux VM, plus a disk image that grows | Skip. It spends the RAM and the 256 GB disk that the runner VM needs. `container:` and `services:` jobs are not in today's Commerce CI lane for this host |
| **`apple/container` and `apple/containerization`** | Apple's Swift stack. Each Linux container is a lightweight VM on Virtualization.framework, with its own kernel. OCI images. Rosetta for linux/amd64 | A good later runtime for one-container-per-job. A bad home for a systemd runner service: `container system start` registers a **per-user** service and wants a logged-in launchd domain (see the GitHub Actions discussion of running it headless). That fights the FileVault / no-auto-login setup in [02](02-macos-service.md). GitHub-hosted macOS runners also cannot run it (`kern.hv_support=0`, nested virtualization). This mini can, because it is bare metal |
| **Anka** (Veertu) and **Orka** (MacStadium) | macOS VM fleets for a rack of Macs | The orchestrators a Mac stadium uses. They do not raise the two-VM cap on one mini, and they are a product to operate. Out of scope for a single machine |
| **Cirrus Runners / Cirrus's own Tart fleet** | A hosted macOS CI product that uses Tart | Someone else's Macs. Not a way to run this mini |

## Ephemeral VMs versus ephemeral runners

Two different "ephemeral"s:

1. **A fresh VM per job** (Tart clone, or one `apple/container` VM). Strongest isolation. On 16 GB the clone's memory cap plus macOS leaves room for one job, and the clone's disk copies add up on a 256 GB SSD unless they are deleted every time.
2. **A fresh runner process per job**, inside one resident VM (`config.sh --ephemeral`, or a JIT config). The guest OS stays up, so `npm ci` can use a warm per-runner cache, and the job still gets a new work directory and a new registration. This is the shape the [November research](../2026-11-15-self-hosted-runners/01-autoscaling-and-ephemeral.md) recommends, and it is the follow-up once a control host mints the tokens.

Day one is (2) without the minting loop: two persistent systemd services in one VM, each with its own cache and a cleanup hook. Moving to a real ephemeral loop does not require changing hypervisors.

## arm64 images

The guest is arm64. Ubuntu 24.04 LTS publishes an arm64 cloud image; confirm the Lima template name on the day of install (`template://ubuntu-24.04`) `[verify-at-use]`. Do not install an amd64 guest and translate it with Rosetta. Commerce CI should see real `linux` / `arm64`, which is what the dry-run in the [runbook](README.md) prints. Rosetta is the escape hatch inside `apple/container` for a single amd64 image, and it is a different architecture from the x64 box, with its own bugs. It is not the lane.
