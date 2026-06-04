# Respect the platform lifecycle

Mobile apps are backgrounded, killed, and restored at the OS's discretion, and background execution is tightly limited (Doze, background-task budgets). Use lifecycle-aware components, save state for restoration, scope work to the right lifecycle, and use the sanctioned background APIs (WorkManager/BGTaskScheduler). Code that assumes the app stays alive loses data, leaks, and crashes.
