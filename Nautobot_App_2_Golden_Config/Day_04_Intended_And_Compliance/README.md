# Day 4: Intended Configurations and Compliance

Today closes the loop. We render an **intended configuration** for each mock cEOS Device from the Jinja template we shipped on Day 2, using each Device's Nautobot data as the source of truth. Then we run **Compliance** — diffing each Device's pre-committed sample backup (Day 3) against its rendered intended (today), per feature. We finish with a deliberate-drift demo to see compliance flip from PASS to FAIL.

Both of today's jobs run **for real** — they operate on Nautobot data and Git-stored configs, no SSH needed. The pre-committed sample backups from Day 3 are designed to match what the Jinja template renders for hostname and NTP, so compliance comes out clean on the first run; the interesting part is what happens when something drifts (Step 6).

## Step 1 — Enable the Intended and Compliance jobs

Two jobs to enable, both via **Jobs → Jobs → \<name\> → Edit → tick Enabled → Update**:

- **Generate Intended Configurations**
- **Perform Configuration Compliance**

## Step 2 — Define Compliance Features and Rules

Compliance works by partitioning a config into **features** (each defined by a CLI prefix) and diffing intended-vs-backup per feature. Two features for our small template:

**Apps → Golden Configuration → Compliance → Compliance Features → Add** — twice:

| Name | Slug | Description |
|------|------|-------------|
| `hostname` | `hostname` | Matches the `hostname` line |
| `ntp` | `ntp` | Matches `ntp ...` lines |

**Apps → Golden Configuration → Compliance → Compliance Rules → Add** — one per (Platform, Feature):

| Feature | Platform | Config to Match | Config Type |
|---------|----------|-----------------|-------------|
| `hostname` | `arista_eos` | `hostname` | CLI |
| `ntp` | `arista_eos` | `ntp` | CLI |

`Config to Match` is the CLI prefix the parser looks for at the start of each line — Compliance picks up every line beginning with that token. So `hostname` matches `hostname bos-rtr-01`, and `ntp` matches `ntp server 1.1.1.1` (as well as `ntp server 8.8.8.8`, `ntp authentication key ...`, etc.).

## Step 3 — Run Generate Intended Configurations

Click **Jobs → Jobs → Generate Intended Configurations → Run Job Now**. Leave **Dryrun** unchecked, leave **Device** empty to run against the full `cEOS Lab Devices` scope (all four mock Devices).

After the job runs, check the intended files:

```
$ docker exec nautobot-docker-compose-nautobot-1 \
    find /opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/intended/ \
    -name "*.cfg"
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/intended/Boston/bos-acc-01.cfg
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/intended/Boston/bos-rtr-01.cfg
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/intended/New_York/nyc-acc-01.cfg
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/intended/New_York/nyc-rtr-01.cfg

$ docker exec nautobot-docker-compose-nautobot-1 \
    cat /opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/intended/Boston/bos-rtr-01.cfg
!
! Intended configuration for bos-rtr-01 (network / arista_eos)
! Rendered by Nautobot Golden Config from templates/arista_eos/network.j2
!
hostname bos-rtr-01
!
ntp server 1.1.1.1
ntp server 8.8.8.8
!
end
```

The hostname line was rendered from `{{ obj.name }}` (`obj` is the Device); the NTP lines are static template content. The four rendered intended configs differ only in hostname — they are intentionally minimal so today's compliance demo is easy to read.

## Step 4 — Run Perform Configuration Compliance

Click **Jobs → Jobs → Perform Configuration Compliance → Run Job Now**, leave Device empty, **Run**.

The job diffs `intended/.../<name>.cfg` against `backups/.../<name>.cfg` for each Device, broken down by each Compliance Rule's feature. Per-feature, you get one of:

- **Compliant** — every intended line is present in the backup, no extra lines for that feature in the backup.
- **Non-Compliant** — there is a diff (either intended has lines backup is missing, or backup has feature-matching lines intended did not declare).
- **Not Applicable** — no lines of that feature exist on either side.

## Step 5 — Walk the Compliance dashboard

**Apps → Golden Configuration → Compliance → Configuration Compliance** shows the per-(Device, Feature) result grid. Expected for the lab on a fresh run:

| Device | hostname | ntp |
|--------|----------|-----|
| `bos-acc-01` | Compliant ✅ | Compliant ✅ |
| `bos-rtr-01` | Compliant ✅ | Compliant ✅ |
| `nyc-acc-01` | Compliant ✅ | Compliant ✅ |
| `nyc-rtr-01` | Compliant ✅ | Compliant ✅ |

All green — because the pre-committed sample backups (Day 3) already include the same `hostname <name>` and `ntp server 1.1.1.1` / `ntp server 8.8.8.8` lines that the Day 2 Jinja template renders into intended. The Backup → Intended → Compliance pipeline is doing exactly what it should: matching what the device *should* look like (intended, from Nautobot data) against what it *does* look like (backup, from the pre-committed sample), per feature.

The interesting part is what happens when something drifts — Step 6.

## Step 6 — Deliberate drift demo

In production, drift happens when someone makes a change on a real device that the intended template does not allow. The next Backup run would capture that change, and the next Compliance run would flag it. To simulate the same effect without an SSH-reachable device, we edit one of the pre-committed sample backups directly inside the Nautobot container's local clone of the GitRepository and re-run Compliance.

Add an unauthorized NTP server to `bos-rtr-01.cfg`:

```
$ docker exec nautobot-docker-compose-nautobot-1 \
    sh -c "sed -i 's|^ntp server 8.8.8.8|ntp server 8.8.8.8\nntp server 192.0.2.99|' \
        /opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/Boston/bos-rtr-01.cfg"

$ docker exec nautobot-docker-compose-nautobot-1 \
    grep '^ntp' /opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/Boston/bos-rtr-01.cfg
ntp server 1.1.1.1
ntp server 8.8.8.8
ntp server 192.0.2.99
```

> ⚠️ **Do not click Sync on the GitRepository between these steps.** Clicking Sync triggers a `git pull` against the upstream remote, which would overwrite our local edit with the clean upstream version. We are intentionally working with the local-only modification — that is what "drift" means in this lab simulation.

Now re-run **Perform Configuration Compliance** — leave Device empty, **Run**.

When it finishes, the dashboard's `bos-rtr-01` row should flip on `ntp`:

| Device | hostname | ntp |
|--------|----------|-----|
| `bos-acc-01` | Compliant ✅ | Compliant ✅ |
| `bos-rtr-01` | Compliant ✅ | **Non-Compliant ❌** |
| `nyc-acc-01` | Compliant ✅ | Compliant ✅ |
| `nyc-rtr-01` | Compliant ✅ | Compliant ✅ |

Click into the Non-Compliant `ntp` cell — the per-line diff shows `ntp server 192.0.2.99` present in backup but not in intended. That is the gap a remediation pipeline would close (manual fix, or an automated Config Plan + deploy job).

**To restore the all-green state**, either undo the edit directly:

```
$ docker exec nautobot-docker-compose-nautobot-1 \
    sh -c "sed -i '/^ntp server 192.0.2.99/d' \
        /opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/Boston/bos-rtr-01.cfg"
```

…or click **Sync** on the GitRepository to pull the clean upstream version back. Re-run **Perform Configuration Compliance** and the `bos-rtr-01` row should be green again.

This is the day-to-day Golden Config workflow in miniature:

1. **Intended** says what *should* be on the device (rendered from Nautobot data + Jinja templates).
2. **Backup** captures what *is* on the device. (In this pack: pre-committed; in production: from the Backup job over SSH.)
3. **Compliance** tells you the gap.
4. You (or a remediation pipeline) close the gap.

## Real-World Correlation

The lab boils down a production Golden Config flow into one Day:

- **The intended config is the source of truth.** In production it is generated from your Nautobot data — interface tables, BGP peerings, VRFs, custom fields — via Jinja templates much richer than our `hostname + ntp` toy. The discipline is the same: any config decision must be expressible as data in Nautobot first, then rendered into the device config.
- **Compliance is observability for configuration drift.** Once the dashboard is wired up, you stop asking "is device X compliant?" and start asking "*which* features drifted *since when* on *which* devices?". The dashboard answers continuously.
- **Backup is your audit log + your rollback substrate.** A daily backup repo is a free git-log of every device config that ever ran in production — even though we did not exercise the live Backup job here.
- **Remediation has two paths.** Manual (use the diff as a punch-list and apply by hand) or automated (Config Plans + a deploy job, which Golden Config 2.x supports via the `enable_plan` / `enable_deploy` flags we left off in `PLUGINS_CONFIG`). Start manual; automate once you trust the dashboard.
- **The same flow works at scale.** What we did against four mock Devices works against 4,000 real devices — the bottleneck moves from Nornir runners to your template-authoring discipline.

## Wrap-up

You have:

- Installed Golden Config on top of a fresh Scenario 1 Nautobot 2.4.33 stack.
- Seeded four mock cEOS Devices into Nautobot via the pack's `seed_mock_devices.py` script.
- Wired three roles (templates, backups, intended) into a single GitRepository.
- Scoped Golden Config to the mock cEOS Devices via a DynamicGroup.
- Walked through how the Backup Configurations job would behave in production, and inspected pre-committed sample running-configs that stand in for its output.
- Rendered real intended configs from Jinja templates using real Nautobot data.
- Run real Compliance, deliberately drifted one Device's backup, and watched the dashboard follow.

You did all of this without running a single SSH session against a network device — which is the point of the lab approach for this pack. When you graduate to a real network, the only step that changes is Day 3: the Backup job actually runs, the `golden-config-data/backups/` directory gets populated by Nornir instead of from this repo, and drift demos use real device CLI sessions instead of the `sed` edit above.

## Day 4 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of your **Configuration Compliance** dashboard (the per-(Device, Feature) grid, ideally captured after the deliberate-drift demo flipped one cell), or share one lesson learned about closing the intended-vs-running gap, on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress!

This wraps the **Golden Config** expansion pack. A future expansion pack may cover **Data Validation Engine** (rule-driven validation of the data we just spent so much time importing) or **ChatOps** (Slack/Teams integration). Watch the repo. See you in the next pack!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+4+of+the+Golden+Config+expansion+pack+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 4 of the Golden Config expansion pack of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
