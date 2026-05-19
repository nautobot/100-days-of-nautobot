# Day 4: Intended Configurations and Compliance

Today closes the loop. We render an **intended configuration** for each cEOS device from the Jinja template we shipped on Day 2, using each Device's Nautobot data as the source of truth. Then we run **Compliance** — diffing each device's backup (Day 3) against its intended (today), per feature. We finish with a deliberate-drift demo to see compliance flip from PASS to FAIL.

## Step 1 — Enable the Intended and Compliance jobs

Two jobs to enable, same edit-tick-update pattern as Day 3:

- **Jobs → Jobs → Generate Intended Configurations** → Edit → tick **Enabled** → Update.
- **Jobs → Jobs → Perform Configuration Compliance** → Edit → tick **Enabled** → Update.

## Step 2 — Define Compliance Features and Rules

Compliance works by partitioning the running-config into **features** (each defined by a CLI prefix) and diffing intended-vs-backup per feature. Two features for our small template:

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

`Config to Match` is the CLI prefix the parser looks for at the start of each line — Compliance picks up every line that begins with that token. So `hostname` matches `hostname bos-rtr-01`, and `ntp` matches `ntp server 1.1.1.1`.

## Step 3 — Run Generate Intended Configurations

Click **Jobs → Jobs → Generate Intended Configurations → Run Job Now**. Same form as Backup — leave **Dryrun** unchecked, leave **Device** empty to run against the full `cEOS Lab Devices` scope.

After the job runs, check the intended files:

```
$ docker exec nautobot-docker-compose-nautobot-1 find /opt/nautobot/git/golden_config_lab/intended/ -name "*.cfg"
/opt/nautobot/git/golden_config_lab/intended/Boston/bos-acc-01.cfg
/opt/nautobot/git/golden_config_lab/intended/Boston/bos-rtr-01.cfg
/opt/nautobot/git/golden_config_lab/intended/New York/nyc-acc-01.cfg
/opt/nautobot/git/golden_config_lab/intended/New York/nyc-rtr-01.cfg

$ docker exec nautobot-docker-compose-nautobot-1 cat /opt/nautobot/git/golden_config_lab/intended/Boston/bos-rtr-01.cfg
!
hostname bos-rtr-01
!
ntp server 1.1.1.1
ntp server 8.8.8.8
!
end
```

The hostname line was rendered from `{{ obj.name }}` (`obj` = the Device); the NTP lines are static template content. We deliberately included NTP in the template even though the cEOS devices don't have it — so compliance has something to flag.

## Step 4 — Run Perform Configuration Compliance

Click **Jobs → Jobs → Perform Configuration Compliance → Run Job Now**, leave Device empty, **Run**.

The job diffs `intended/.../<name>.cfg` against `backups/.../<name>.cfg` for each Device, broken down by each Compliance Rule's feature. Per-feature, you get one of:

- **Compliant** — every intended line is present in the backup, no extra lines for that feature in the backup.
- **Non-Compliant** — there is a diff.
- **Not Applicable** — no lines of that feature exist on either side.

## Step 5 — Walk the Compliance dashboard

**Apps → Golden Configuration → Compliance → Configuration Compliance** shows the per-(Device, Feature) result grid. Expected for the lab:

| Device | hostname | ntp |
|--------|----------|-----|
| `bos-acc-01` | Compliant ✅ | Non-Compliant ❌ |
| `bos-rtr-01` | Compliant ✅ | Non-Compliant ❌ |
| `nyc-acc-01` | Compliant ✅ | Non-Compliant ❌ |
| `nyc-rtr-01` | Compliant ✅ | Non-Compliant ❌ |

- **hostname** is Compliant because the device backups already match `hostname <name>` (we fixed the Containerlab startup-configs in Device Onboarding).
- **ntp** is Non-Compliant because the intended template says we want two NTP servers, but the cEOS devices have none.

Click into any Non-Compliant cell to see the per-line diff: the two `ntp server ...` lines from intended are missing from the backup.

## Step 6 — Deliberate drift demo

Now flip the result for one device. SSH into `bos-rtr-01` and add the NTP config the template expects:

```
$ ssh admin@<bos-rtr-01-ip>
ceos-01> enable
ceos-01# configure terminal
ceos-01(config)# ntp server 1.1.1.1
ceos-01(config)# ntp server 8.8.8.8
ceos-01(config)# end
ceos-01# write memory
```

Re-run **Perform Configuration Backup** (to capture the new state) and then **Perform Configuration Compliance**. The `bos-rtr-01` row's `ntp` cell should now be **Compliant**. The other three devices stay Non-Compliant.

This is the day-to-day Golden Config workflow in miniature:
1. **Intended** says what *should* be on the device.
2. **Backup** captures what *is* on the device.
3. **Compliance** tells you the gap.
4. You (or a remediation pipeline) close the gap.

## Real-World Correlation

The lab boils down a production Golden Config flow into one Day:

- **The intended config is the source of truth.** In production it is generated from your Nautobot data — interface tables, BGP peerings, VRFs, custom fields — via Jinja templates much richer than our `hostname + ntp` toy. The discipline is the same: any config decision must be expressible as data in Nautobot first, then rendered into the device config.
- **Compliance is observability for configuration drift.** Once the dashboard is wired up, you stop asking "is device X compliant?" and start asking "*which* features drifted *since when* on *which* devices?". The dashboard answers continuously.
- **Backup is your audit log + your rollback substrate.** A daily backup repo is a free git-log of every device config that ever ran in production.
- **Remediation has two paths.** Manual (use the diff as a punch-list and apply by hand) or automated (Config Plans + a deploy job, which Golden Config 2.x also supports via the `enable_plan` / `enable_deploy` flags we left off). Start manual; automate once you trust the dashboard.
- **The same flow works at scale.** What we did against 4 cEOS containers works against 4,000 real devices — the bottleneck moves from Nornir runners to your template authoring discipline.

## Wrap-up

You have:

- Installed Golden Config on top of the Device Onboarding stack.
- Wired three roles (templates, backups, intended) into a single Git repository.
- Scoped Golden Config to the cEOS Devices via a DynamicGroup.
- Backed up real running configs from real devices into the local Git clone.
- Rendered intended configs from Jinja templates using Nautobot data.
- Diffed intended vs. backup per feature, deliberately drifted one device, and watched compliance follow.

Two expansion packs in, the Retail-r-Us network in your Codespace is fully populated and continuously checked.

## Day 4 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of your **Configuration Compliance** dashboard (the per-(Device, Feature) grid, ideally after the deliberate-drift demo flipped one cell), or share one lesson learned about closing the intended-vs-running gap, on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress!

This wraps the **Golden Config** expansion pack — the second in the popular-apps series. A future expansion pack may cover **Data Validation Engine** (rule-driven validation of the data we just spent so much time importing) or **ChatOps** (Slack/Teams integration). Watch the repo. See you in the next pack!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+4+of+the+Golden+Config+expansion+pack+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 4 of the Golden Config expansion pack of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
