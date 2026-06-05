---
name: app-store-release-pipeline
description: "Step-by-step guide for automating the iOS App Store and Google Play release pipeline — code signing, build automation with Fastlane, TestFlight and internal track distribution, phased rollout, and the common pipeline failure modes."
---

# App Store Release Pipeline

## When to invoke

Use when automating the app release process for the first time, diagnosing a signing failure in CI, designing a phased rollout, or establishing the review and release checklist for a mobile team.

## Step 1 — iOS code signing strategy

Choose one signing approach before writing any CI config:

| Approach | Managed by | Best for |
|---|---|---|
| Xcode Automatic (local only) | Xcode + Apple Developer portal | Solo developer, no CI |
| **match (Fastlane)** | Git-encrypted cert repo | Teams + CI — recommended |
| Manual profiles | You | Legacy; avoid for new pipelines |

**Fastlane match setup:**

```bash
# One-time setup
fastlane match init
# Choose: git, S3, or Google Cloud Storage
# Sets MATCH_GIT_URL in CI secrets

fastlane match appstore   # creates/renews App Store cert + profile
fastlane match development
```

`match` stores encrypted certificates in a private Git repo or cloud bucket — every CI runner decrypts on demand using `MATCH_PASSWORD`. No developer ever manages profiles manually.

## Step 2 — Android signing

```
# keystore (one-time, keep the .jks file outside the repo)
keytool -genkey -v -keystore release.jks \
  -alias release -keyalg RSA -keysize 2048 -validity 10000

# Store in CI secrets:
#   KEYSTORE_BASE64    = base64 -i release.jks
#   KEY_ALIAS          = release
#   KEY_PASSWORD       = ...
#   STORE_PASSWORD     = ...
```

`build.gradle` signing config reads from env at build time — the `.jks` file is never committed:

```groovy
android {
  signingConfigs {
    release {
      storeFile file(System.getenv("KEYSTORE_PATH") ?: "debug.jks")
      storePassword System.getenv("STORE_PASSWORD")
      keyAlias System.getenv("KEY_ALIAS")
      keyPassword System.getenv("KEY_PASSWORD")
    }
  }
}
```

## Step 3 — Fastlane lanes

**`Fastfile` structure:**

```ruby
platform :ios do
  lane :beta do
    match(type: "appstore")
    increment_build_number(
      build_number: ENV["BUILD_NUMBER"] || Time.now.to_i.to_s
    )
    build_app(
      scheme: "MyApp",
      configuration: "Release",
      export_method: "app-store"
    )
    upload_to_testflight(
      skip_waiting_for_build_processing: true,
      changelog: changelog_from_git_commits(commits_count: 5)
    )
  end

  lane :release do
    beta
    upload_to_app_store(
      submit_for_review: false,   # manual review trigger
      automatic_release: false,
      phased_release: true
    )
  end
end

platform :android do
  lane :beta do
    gradle(
      task: "bundle",
      build_type: "Release",
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
        ...
      }
    )
    upload_to_play_store(track: "internal")
  end
end
```

## Step 4 — CI pipeline shape (GitHub Actions example)

```yaml
name: Mobile Release

on:
  push:
    tags: ['v*']

jobs:
  ios-beta:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { bundler-cache: true }
      - name: Setup signing
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_URL: ${{ secrets.MATCH_GIT_URL }}
        run: bundle exec fastlane ios beta
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          APP_STORE_CONNECT_API_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY_CONTENT: ${{ secrets.ASC_KEY_CONTENT }}

  android-beta:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > keystore.jks
      - run: bundle exec fastlane android beta
        env:
          KEYSTORE_PATH: keystore.jks
          STORE_PASSWORD: ${{ secrets.STORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
          GOOGLE_PLAY_JSON_KEY: ${{ secrets.GOOGLE_PLAY_JSON_KEY }}
```

## Step 5 — Phased rollout

**iOS TestFlight → App Store:**
1. `upload_to_testflight` → internal testers (0 review delay).
2. Add external tester group → Apple review (1–3 days).
3. `upload_to_app_store(phased_release: true)` → starts at 1% day 1, 2% day 2, 5% day 3, 10% day 4, 20% day 5, 50% day 6, 100% day 7.
4. Monitor crash rate in Crashlytics/Xcode Organizer. Pause rollout in App Store Connect if crash-free rate drops >0.2%.

**Google Play tracks:** `internal` → `alpha` → `beta` (% rollout configurable) → `production`.

## Step 6 — Version and build number discipline

| Platform | Version shown to user | Build/version code |
|---|---|---|
| iOS | `CFBundleShortVersionString` (semver) | `CFBundleVersion` (monotonically increasing integer) |
| Android | `versionName` (semver) | `versionCode` (monotonically increasing integer) |

**Rule:** `versionCode` / `CFBundleVersion` must be strictly increasing — the stores reject a build with a lower or equal build number. Use `CI_BUILD_NUMBER` (pipeline run number) as the build number.

## Pitfalls

- **Committing the `.jks` keystore or `match` certificates** — the signing artifacts are the crown jewels; store them in secrets/encrypted storage only.
- **Using Xcode Automatic Signing in CI** — it tries to modify the Xcode project and fails without a logged-in Apple ID; always use `match` in CI.
- **Not setting `skip_waiting_for_build_processing: true` on TestFlight uploads** — the default waits up to 30 minutes for Apple processing, blocking the CI job; let it process asynchronously.
- **Forgetting to increment the build number** — re-uploading the same build number fails at the store upload step; automate the increment, don't rely on developers to bump it.
- **No phased rollout on major releases** — a full 100% rollout of a breaking change means all users hit a crash simultaneously; phased rollout is the mobile equivalent of a canary deploy.
