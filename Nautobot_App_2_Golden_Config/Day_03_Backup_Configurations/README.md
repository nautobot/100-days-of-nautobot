# Day 3: Backup Running Configurations

Today is the first payoff. We run Golden Config's **Backup Configurations** job against the four cEOS devices that Device Onboarding placed in Nautobot. The job SSH's in via Nornir (reusing the `cEOS Lab Credentials` SecretsGroup from Device Onboarding Day 2), pulls `show running-config`, and writes one file per device into the backup directory inside the Nautobot container's local clone of the `Golden Config Lab` Git repository.

## Step 1 — Confirm the Containerlab patches are in place

Golden Config's Backup job uses Nornir + Netmiko to reach the devices on `172.17.0.0/16`. If you stopped/restarted the stack since Device Onboarding, re-apply the runtime patches:

```
$ cd ~/100-days-of-nautobot
$ bash Nautobot_App_1_Device_Onboarding/scripts/patch_lab_ceos.sh
```

The script is idempotent — safe to re-run. It bridges the Nautobot containers to the default Docker network and reapplies the cEOS-compatibility patches.

## Step 2 — Enable the Backup job

Like every Nautobot Job, **Backup Configurations** ships disabled by default. Enable it once:

- **Jobs → Jobs** → filter for "Golden Config" or "Backup".
- Click into **Perform Configuration Backup**.
- **Edit** (top-right) → tick **Enabled** → **Update**.

You should now see **Run Job Now** on the job's detail page.

## Step 3 — Run the job against one device first

Smart to validate against a single device before batching. Click **Perform Configuration Backup → Run Job Now**. The form is short:

| Field | Set to |
|-------|--------|
| **Dryrun** | leave **unchecked** (we want files written to disk) |
| **Debug** | leave unchecked |
| **Device** | `bos-rtr-01` (or any one of the four cEOS devices) |

Click **Run**. The job log streams; refresh until completion.

Expected log highlights:

```
Starting backup jobs.
Pull Device data
Backup configurations starting.
bos-rtr-01: Backup running-config file is locked.
bos-rtr-01: Backup running-config: <local path under /opt/nautobot/git/golden_config_lab/backups/>
Performing backup compliance for nautobot-config.
Backup configurations ended.
```

## Step 4 — Inspect the per-device backup

The job wrote a config file inside the Nautobot container at the path your **Backup Path Template** from Day 2 resolved to. For `bos-rtr-01` (location `Boston`):

```
$ docker exec nautobot-docker-compose-nautobot-1 ls /opt/nautobot/git/golden_config_lab/backups/Boston/
bos-rtr-01.cfg

$ docker exec nautobot-docker-compose-nautobot-1 head -20 /opt/nautobot/git/golden_config_lab/backups/Boston/bos-rtr-01.cfg
```

You should see the device's running-config — the same content `show running-config` would produce over SSH. Compare against a fresh manual SSH to confirm:

```
$ ssh admin@<bos-rtr-01-ip> show running-config | head -20
```

The two should match line-for-line (minus the timestamp comment at the top of `show running-config`, which Golden Config's `regex_lines` settings can scrub if you want — leave it for now).

In the UI: **Apps → Golden Configuration → Backup → All Backups** — the row for `bos-rtr-01` should show the backup status and a link to view the file via Nautobot.

## Step 5 — Batch the remaining three

Re-run **Perform Configuration Backup**. This time, leave the **Device** field empty — when nothing is specified, the job runs against the full **Scope** of the `cEOS Lab Settings` (the `cEOS Lab Devices` DynamicGroup, all four cEOS devices).

After the run, the backup directory should contain all four files:

```
$ docker exec nautobot-docker-compose-nautobot-1 find /opt/nautobot/git/golden_config_lab/backups/ -name "*.cfg"
/opt/nautobot/git/golden_config_lab/backups/Boston/bos-acc-01.cfg
/opt/nautobot/git/golden_config_lab/backups/Boston/bos-rtr-01.cfg
/opt/nautobot/git/golden_config_lab/backups/New York/nyc-acc-01.cfg
/opt/nautobot/git/golden_config_lab/backups/New York/nyc-rtr-01.cfg
```

## Step 6 — What got captured, what didn't

Notice what is **in** the backup file:

- Everything from `show running-config` — hostname, users, interfaces, OSPF, etc.
- Including the timestamp comment Arista emits at the top.

And what is **not**:

- Operational state (`show interface counters`, `show route`, neighbors). Backup is configuration only — anything that changes minute-to-minute is out of scope.
- Anything from the device's startup config that is not also in running config.

This matters for compliance on Day 4: we will only be able to compare against config lines that show up in `running-config`, never against operational state.

> 💡 **Why is the backup only on the Nautobot container, not pushed to GitHub?** The `Golden Config Lab` GitRepository has no Secrets Group attached, so the Backup job clones the repo locally inside the container and writes there. It does not push back. For production you would attach a Secrets Group with a PAT or deploy key, point at your own backup repository, and let the job push commits up.

## Day 3 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of your backup directory listing (the four `.cfg` files under `backups/Boston/` and `backups/New York/`) or the **All Backups** page in the Nautobot UI on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress!

In tomorrow's challenge, we will [render intended configurations from the Jinja template and run Compliance](../Day_04_Intended_And_Compliance/README.md) — diff intended vs backup, watch a deliberately-drifted device get flagged, and close out the pack. See you tomorrow!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+3+of+the+Golden+Config+expansion+pack+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 3 of the Golden Config expansion pack of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
