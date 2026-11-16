# 02: macOS service, sleep, unlock, and remote access

Checked 2026-11-16. The runners for this factory live in a Linux VM ([03](03-virtualization.md)). The Mac's job is to stay awake, boot the VM, and be reachable. A native actions runner on macOS is described so the difference is on the page. It is not the install this pack recommends.

## What svc.sh installs on macOS

GitHub's [configure-the-application](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application) doc says that on macOS `./svc.sh install` installs a launchd service, and that a custom service must start through **runsvc.sh**. The template at [actions.runner.plist.template](https://github.com/actions/runner/blob/main/src/Misc/layoutbin/actions.runner.plist.template), fetched 2026-11-16, sets:

- ProgramArguments = runsvc.sh
- UserName, WorkingDirectory, RunAtLoad
- stdout and stderr under the user's Library/Logs
- ACTIONS_RUNNER_SVC=1
- ProcessType = Interactive
- SessionCreate present as an empty boolean, which plist treats as true

The fetched template has no KeepAlive key.

[actions/runner issue 1959](https://github.com/actions/runner/issues/1959) reports that svc.sh start failed to load the user agent until someone logged in at the GUI, and the thread's workaround is automatic login or moving the plist. That report is from older macOS releases. This session did not re-run it on macOS 27. The probe that would come out differently if a user LaunchAgent now starts with nobody logged in: install with svc.sh install, reboot, leave the login window up, and launchctl print for that user's gui domain shows the service running. The [runbook](README.md) uses a different shape, so that report is not load-bearing: a LaunchDaemon starts limactl, and the runners are systemd units inside the guest. The reboot test in the runbook is the probe for that shape.

ProcessType Interactive together with SessionCreate asks launchd for a GUI session. Copying the stock plist into /Library/LaunchDaemons is what several field write-ups do, and issue 1959 also records a case where loading it into the system domain did not survive a restart. A daemon whose only job is limactl start should be written as a daemon: RunAtLoad, KeepAlive, ThrottleInterval around 30 seconds, UserName set to ghrunner, and no SessionCreate. Whether that plist brings Lima up before a login is the reboot test. This research did not execute that test.

Inside the guest, svc.sh install is a systemd unit. That is the path the same GitHub doc describes for Linux, and it is the path these runners use.

## Sleep and power loss

| Setting | Why it is in the runbook |
|---|---|
| sudo pmset -a sleep 0 | System sleep timer, in minutes. A Mac that sleeps pauses the VM. The November research ties a sleep mid-job to lost communication ([05](../2026-11-15-self-hosted-runners/05-availability-sleep-updates.md), [actions/runner issue 3862](https://github.com/actions/runner/issues/3862)) |
| disksleep 0 | Disk sleep off. On an SSD this is belt and braces against an Energy setting turning it back on |
| displaysleep 10 | An attached panel can sleep. sleep 0 is what keeps the system up |
| autorestart 1 | The pmset form of start up after a power failure |
| womp 1 and tcpkeepalive 1 | Wake on LAN, and keep TCP sessions |
| powernap 0, standby 0, autopoweroff 0 | The delayed-sleep keys, set off so a machine with sleep 0 has a second path into standby closed |
| Rear Ethernet, not Wi-Fi | actions/runner issue 3862 reports the long-poll dropping across network changes |

Read man pmset on the machine before trusting a key name. Energy settings in System Settings can rewrite this set after a macOS update. pmset -g after the command is the check that the keys stuck. [verify-at-use]

caffeinate -s is documented as preventing idle system sleep on AC power. It is the tool the November research uses for the MacBook. On this desktop the durable setting is pmset. A LaunchDaemon that runs caffeinate is only a backup for the case where an update restores the Energy defaults. caffeinate is a userspace process, so it is available after macOS has booted. The FileVault password screen is earlier than that. The reboot test is what shows whether the VM is up after unlock.

macOS updates reboot on their own schedule when automatic install is on. A reboot during a job is the same lost-communication failure the November doc describes. Apply updates while both runners are idle. The runner application's own auto-update is a different mechanism and stays enabled (the 63-day rule).

## FileVault

Apple's [login-window help](https://support.apple.com/guide/mac-help/a-login-window-start-mac-mchlp1158/mac), fetched 2026-11-16, says: "When FileVault is turned on, automatic login is disabled." MDM write-ups of the same behavior say the preboot unlock screen on Apple silicon has no network, so Remote Login has no path to that password. This session did not boot an M6 with FileVault. The runbook still turns FileVault on, and the reboot test is the probe: power-cycle, and see whether SSH answers before anyone types a password. If SSH answers with no password typed, that preboot description is wrong for this OS, and the runbook step that asks for a keyboard unlock can be dropped.

FileVault stays in the recommendation until that probe says otherwise. The disk holds a checkout of a private repo and the runner credentials file. The cost, if the published behavior holds, is one keyboard unlock after each power cut. autorestart 1 still powers the machine on. It is not, by itself, a way past that screen.

## Gatekeeper and TCC

These apply to programs macOS launches. Binaries inside the Linux guest are outside that path.

- A tarball saved by a browser gets a quarantine attribute. curl usually leaves the attribute off. xattr -dr com.apple.quarantine on a quarantined directory clears it before the first execution. With the runners in the guest, the Mac-side binary is Lima, installed with Homebrew.
- TCC prompts for Desktop, Documents, and Downloads fire when a Mac process touches those folders. Keep the VM image and the runner homes in ghrunner's home, outside those folders. Skip Full Disk Access, Accessibility, and Automation for that user.
- Playwright browsers installed on macOS are the usual first-launch Gatekeeper prompt. Install them in the guest.

## Remote management

| | Use it for | Leave it |
|---|---|---|
| Remote Login (SSH) | The admin user, from the home LAN, with a key | Open to the internet. ghrunner needs no remote shell of its own once the VM starts at boot |
| Screen Sharing | First boot, while a display is attached | A guessed path past FileVault, until the reboot test shows a remote unlock |
| Remote Management (Apple Remote Desktop) | Two runners have no need for it | Off |

SSH and a LaunchDaemon have no need for a display. Whether macOS 27 Screen Sharing paints a desktop on this mini when no display has ever been plugged in was not tested. Do the first setup with a display, then use SSH.

Reach the guest with limactl shell ci from the Mac. Leave the guest SSH port unpublished.
