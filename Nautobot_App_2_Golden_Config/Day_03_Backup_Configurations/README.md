# Day 3: Backup Running Configurations

> 📝 **Draft stub.** Day 3's full walkthrough lands in a subsequent commit.

Today we capture each cEOS device's running configuration in Git. Golden Config's **Backup Configurations** job SSH's into the devices via Nornir (reusing the SecretsGroup from Device Onboarding Day 2), pulls `show running-config`, and writes one file per device into the backup Git repository configured on Day 2.

## Sections planned

- **Enable the Backup job** — Jobs ship disabled by default; flip the Enabled flag (same pattern as Device Onboarding Day 3).
- **Run Backup Configurations** — pick the four cEOS Devices, run, watch the log.
- **Inspect the backup Git repository** — one file per device, contents = `show running-config` output.
- **What got captured vs. what didn't** — calling out cEOS-specific lines, dynamic data scrubbing options.
- **Cross-check** — open a backup file, compare against a fresh SSH `show running-config`.
