# Day 4: Intended Configurations and Compliance

> 📝 **Draft stub.** Day 4's full walkthrough lands in a subsequent commit.

Today closes the loop. We render an **intended configuration** for each cEOS device from the Jinja templates set up on Day 2, using Nautobot's data as the source of truth. Then we run **Compliance**, which diffs each device's backup (Day 3) against its intended config, per feature.

## Sections planned

- **Enable the Intended and Compliance jobs.**
- **Run Intended Configuration** — renders templates per Device, writes to the intended Git repo.
- **Inspect a generated intended config** — open a file, compare structure vs. backup.
- **Run Compliance** — diffs intended vs. backup per feature (interfaces, routing, NTP, …).
- **Walk the Compliance dashboard** — per-feature pass/fail, per-device drill-down.
- **Deliberate drift demo** — change a config on the cEOS device, re-run Backup + Compliance, watch the diff appear.
- **Real-world correlation** — scheduled compliance runs, CI integration, drift alerts, exporting reports.
- **Pack wrap-up + social CTA.**
