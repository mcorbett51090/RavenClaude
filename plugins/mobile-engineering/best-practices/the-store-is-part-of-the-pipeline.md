# Treat the app store as part of the pipeline

Code signing, provisioning, review guidelines, phased rollout, and the reality that users do not update instantly are engineering concerns, not afterthoughts. Design the app and its API to tolerate multiple live client versions simultaneously, automate signing and submission in CI/CD, and plan for review latency. An app that breaks when the backend changes because old clients are still live is a versioning failure.

## The build-SDK floor is a hard upload gate (Apple)

Starting **2026-04-28**, every app and game uploaded to Apple App Store Connect must be built with **Xcode 26 or later** against the **iOS 26 / iPadOS 26 / tvOS 26 / visionOS 26 / watchOS 26 SDK or later** — older-SDK uploads are rejected at upload time. This gates **new submissions and updates**; apps already live on the store are not affected until you next submit. It is a **build/SDK** requirement, not a user-OS requirement: your **deployment target can stay lower** (e.g., iOS 16/17), so raising the build SDK does not drop older-OS users. Bake the toolchain floor into your release CI (pin the Xcode/SDK version) so a submission is never bounced for a stale SDK.

**Design/QA side effect — Liquid Glass by default.** Apps built against the iOS 26 SDK get Apple's new "Liquid Glass" appearance applied to native UI components **by default unless the developer opts out**. So the SDK bump is not visually inert: re-QA native controls after moving to the iOS 26 SDK, and decide deliberately whether to adopt Liquid Glass or opt out.

> Sources (retrieved 2026-07-09): Apple Developer — Upcoming Requirements <https://developer.apple.com/news/upcoming-requirements/?id=02032026a>; 9to5Mac, "Apple to update minimum SDK requirements for all App Store submissions" <https://9to5mac.com/2026/02/03/apple-to-update-minimum-sdk-requirements-for-all-app-store-submissions/>
