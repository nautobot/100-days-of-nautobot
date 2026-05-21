# Day 3: Backup Running Configurations (explain-only walkthrough)

Today is the part of the Golden Config workflow that **would** SSH into each in-scope Device, run `show running-config`, and write the output into the backup directory inside the celery_worker container's local clone of the GitRepository. In a real-network lab — for example, after [DO Day 3](../../Nautobot_App_1_Device_Onboarding/Day_03_Run_Onboarding_Job/README.md) — that means a one-click Job that fetches running-configs for the four cEOS devices, parses what came back, and shows you per-device backup status in the UI.

This pack does **not** run that Job. Reaching four cEOS containers from the Nautobot stack inside one Codespace consistently starves the host (see the pack-level [Lab approach section](../README.md#lab-approach--no-containerlab-in-this-pack) for the full reason). Instead, we ship four **pre-committed sample running-configs** in the `golden-config-data/backups/` scaffold — they stand in for what the Backup job would have produced. Today is three steps:

1. Walk through what the Backup job does in production, where it gets its inputs, and what it writes.
2. Inspect the pre-committed samples inside the celery_worker container's local clone of the GitRepository.
3. Identify what is **in** a running-config backup and what is **not** — important context for Day 4's compliance comparison.

No Jobs are run today.

## Step 1 — How the Backup Configurations job works in production

`nautobot-app-golden-config` ships a Nautobot Job called **Perform Configuration Backup**. When you run it (UI: **Jobs → Jobs → Perform Configuration Backup → Run Job Now**), the job:

1. Reads the **Scope** from your Golden Config Settings — for us, `cEOS Lab Settings` → `cEOS Lab Devices` DynamicGroup → the four mock cEOS Devices.
2. For each Device in scope, opens a Nornir/Netmiko SSH session using credentials from the Device's `SecretsGroup` (in a DO-baselined lab this is the `cEOS Lab Credentials` group; mock Devices here have no SecretsGroup, which is one reason we cannot actually run the job).
3. Issues `show running-config`, captures the output.
4. Renders the **Backup Path Template** with the Device as `obj` to get a relative path inside the GitRepository's local clone. For `bos-rtr-01`: `Nautobot_App_2_Golden_Config/golden-config-data/backups/Boston/bos-rtr-01.cfg`.
5. Writes the file. Optionally runs the per-Platform `regex_lines` filter to scrub volatile lines (timestamp comments, banner counters, etc.) before saving.
6. Updates per-Device backup status visible at **Apps → Golden Configuration → Backup → All Backups**.

The local clone is on the celery_worker container's filesystem at `/opt/nautobot/git/golden_config_lab/`. With no Secrets Group on the GitRepository, the job does **not** push the backups back upstream — in production you'd attach a Secrets Group with a deploy key or PAT, point at your own backup-only repo, and let the job push commits.

## Step 2 — Why we are not running it in this pack

Reaching `172.17.0.0/16` from the Nautobot containers in a Codespace requires the four Containerlab cEOS containers up and SSH-reachable. Even on larger Codespace SKUs that consistently starved CPU/RAM hard enough to wedge Docker entirely. The full post-mortem is in the [pack-level Lab approach section](../README.md#lab-approach--no-containerlab-in-this-pack).

So the Backup Configurations job's *output* — four files in the right places with realistic running-config content — was committed to this pack manually. Everything downstream in Golden Config (Intended generation on Day 4, Compliance on Day 4) operates on those files exactly the way it would operate on the job's output.

> 💡 **Want to actually run the Backup Job?** Do the [Device Onboarding pack](../../Nautobot_App_1_Device_Onboarding/README.md) on a 16+ GB Codespace SKU first — that brings up the four cEOS containers and onboards them with a `cEOS Lab Credentials` SecretsGroup. Then attach that SecretsGroup to the four mock Devices this pack seeded (or skip the seed step entirely and use DO's onboarded inventory), and run `Perform Configuration Backup` from the UI as documented in Step 1 above. The Day 2 path templates write the output to the same paths the pre-committed samples occupy — you can keep the samples as a fallback, or delete them and let the live job populate the directories.

## Step 3 — Inspect the pre-committed sample backups

The samples ship at:

```
Nautobot_App_2_Golden_Config/golden-config-data/backups/
├── Boston/
│   ├── bos-acc-01.cfg
│   └── bos-rtr-01.cfg
└── New_York/
    ├── nyc-acc-01.cfg
    └── nyc-rtr-01.cfg
```

Once Day 2's `Create & Sync` pulled the GitRepository, those four files are also inside the celery_worker container's local clone. Verify from the codespace shell:

```
$ docker exec nautobot-docker-compose-celery_worker-1 \
    find /opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/ \
    -name "*.cfg"
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/Boston/bos-acc-01.cfg
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/Boston/bos-rtr-01.cfg
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/New_York/nyc-acc-01.cfg
/opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/New_York/nyc-rtr-01.cfg
```

Pick one and read it through:

```
$ docker exec nautobot-docker-compose-celery_worker-1 \
    cat /opt/nautobot/git/golden_config_lab/Nautobot_App_2_Golden_Config/golden-config-data/backups/Boston/bos-rtr-01.cfg
```

You should see:

- a `hostname` matching the device name,
- two `ntp server` lines at `1.1.1.1` and `8.8.8.8` (these align with the Jinja template Day 4 will render — that is why Day 4's compliance comes out clean for hostname + NTP on every device),
- realistic filler — `interface Management0` with the device's management IP, `interface Ethernet1` / `Ethernet2` with peer-description text, `ip routing`, and on the two router devices (`bos-rtr-01`, `nyc-rtr-01`) a small `router bgp` block.

All four samples are plain Arista IOS-style configurations — same shape that `show running-config` produces on a cEOS Lab device. They differ from each other in hostname, management IP, peer descriptions, and BGP ASN/router-id, so Day 4's compliance treats them as four distinct devices.

## Step 4 — What got captured, what didn't

In a real backup, **`show running-config`** captures:

- All configured state — hostname, users, interfaces, routing protocols, ACLs, etc.
- Plus any volatile metadata at the top (the timestamp comment Arista emits) unless filtered out via the per-Platform `regex_lines` setting.

It does **not** capture:

- Operational state — `show interface counters`, `show route`, neighbor adjacencies. Anything that changes minute-to-minute is out of scope.
- Anything in `startup-config` that did not also make it to `running-config`.

This matters for Day 4: the Compliance comparison checks only config lines present in a running-config backup. State-vs-config comparisons would need a different job — `Perform Configuration Compliance` is specifically diffing two static config snapshots (backup vs. intended).

## Day 3 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of one of your pre-committed sample backups (a `cat` output, or the rendered Markdown view of [`golden-config-data/backups/`](../golden-config-data/backups/) on GitHub) on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress!

In tomorrow's challenge, we will [render intended configurations from the Jinja template and run real Compliance](../Day_04_Intended_And_Compliance/README.md) against today's pre-committed backups — diff intended vs backup, deliberately drift one sample, watch a row flip red, and close out the pack. See you tomorrow!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+3+of+the+Golden+Config+expansion+pack+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 3 of the Golden Config expansion pack of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
