# Day 2: Templates Git Repository and Golden Config Settings

Today we wire Golden Config to a Git repository that holds the **Jinja templates** for our intended configurations, set up the **Golden Config Settings** that tie the wiring together, and scope it all to the four cEOS Devices that Device Onboarding placed in Nautobot.

## Where the templates live

Golden Config reads templates from a Nautobot **GitRepository** with `nautobot_golden_config.jinjatemplate` in its `provided_contents`. The same record can also carry `backupconfigs` and `intendedconfigs` — letting one Git URL serve as the storage for all three roles. That is what we will do, pointing at a small scaffold that ships with this expansion pack.

The scaffold is at [`golden-config-data/`](../golden-config-data/) within this repo:

```
Nautobot_App_2_Golden_Config/golden-config-data/
├── README.md                          # explains the structure
├── templates/
│   └── arista_eos/
│       └── network.j2                 # intended config template for cEOS devices in the "network" role
├── backups/                           # Golden Config writes per-device backups here at runtime
│   └── .gitkeep
└── intended/                          # Golden Config writes per-device intended configs here at runtime
    └── .gitkeep
```

Golden Config writes backups / intended configs into the **local clone** of the GitRepository (inside the Nautobot container's filesystem). Without push credentials configured it will *not* push them back up to GitHub — fine for the lab, since we just inspect the local files via `docker exec` or the Nautobot UI.

## Step 1 — Create the GitRepository in Nautobot

In the Nautobot UI, navigate to **Extensibility → Git Repositories → Add**:

| Field | Value |
|-------|-------|
| **Name** | `Golden Config Lab` |
| **Slug** | `golden-config-lab` (auto-filled from name) |
| **Remote URL** | `https://github.com/nautobot/100-days-of-nautobot.git` |
| **Branch** | `main` |
| **Provided Contents** | tick all three: `Golden Config: backupconfigs`, `Golden Config: intendedconfigs`, `Golden Config: jinjatemplate` |

Leave **Secrets Group** empty — public repo, no credentials needed, no pushes.

Save. Nautobot fetches the repo via the `Sync` action (top-right). Watch the job log; on success, the GitRepository's status flips to `OK`.

## Step 2 — Create a DynamicGroup to scope Golden Config to the cEOS Devices

Golden Config's Settings use a DynamicGroup as their scope — only Devices matching the group get backed up / rendered / checked.

Navigate to **Organization → Dynamic Groups → Add**:

| Field | Value |
|-------|-------|
| **Name** | `cEOS Lab Devices` |
| **Content Type** | `dcim | device` |
| **Filter** | use the filter builder: Platform = `arista_eos` |

Save. The DynamicGroup's **Members** tab should now list the four onboarded Devices (`bos-acc-01`, `bos-rtr-01`, `nyc-acc-01`, `nyc-rtr-01`).

## Step 3 — Configure Golden Config Settings

Navigate to **Apps → Golden Configuration → Golden Config Settings → Add**:

| Field | Value |
|-------|-------|
| **Name** | `cEOS Lab Settings` |
| **Slug** | `ceos-lab-settings` |
| **Weight** | `1000` |
| **Description** | `Backup + intended + compliance for the Containerlab cEOS topology` |
| **Scope** | `cEOS Lab Devices` (the DynamicGroup from Step 2) |
| **Backup Repository** | `Golden Config Lab` |
| **Backup Path Template** | `backups/{{ obj.location.name }}/{{ obj.name }}.cfg` |
| **Intended Repository** | `Golden Config Lab` |
| **Intended Path Template** | `intended/{{ obj.location.name }}/{{ obj.name }}.cfg` |
| **Jinja Repository** | `Golden Config Lab` |
| **Jinja Path Template** | `templates/{{ obj.platform.network_driver }}/{{ obj.role.name }}.j2` |

The path templates are themselves Jinja — `obj` is the Device. So for `bos-acc-01` (location `Boston`, role `network`, platform `arista_eos`):

- Backup → `backups/Boston/bos-acc-01.cfg`
- Intended → `intended/Boston/bos-acc-01.cfg`
- Template → `templates/arista_eos/network.j2`

Leave the **Backup Test** field empty (we'll skip the "is the device reachable before backing up?" pre-check — Nornir's own SSH will tell us soon enough). Leave the GraphQL **SoT Aggregation Query** field empty for now.

Save.

## Step 4 — Validate the wiring

On the **Golden Config Settings** detail page (`cEOS Lab Settings`), each repository link should be clickable and resolve. Click into the **Scope** DynamicGroup — the four cEOS Devices should be listed.

Quick sanity-check from the codespace shell — confirm the local clone of the GitRepository on the Nautobot container's filesystem includes our template scaffold:

```
$ docker exec nautobot-docker-compose-nautobot-1 ls /opt/nautobot/git/golden_config_lab/templates/arista_eos/
network.j2
```

If `network.j2` is listed, the Jinja path template will resolve at render time and Day 4's intended-config job will find the template.

## Day 2 Recap

| What | State after Day 2 |
|------|-------------------|
| Templates scaffold | committed at `golden-config-data/templates/arista_eos/network.j2` |
| GitRepository in Nautobot | `Golden Config Lab` synced, all three `provided_contents` ticked |
| DynamicGroup | `cEOS Lab Devices` scoped to Platform = `arista_eos` (4 members) |
| Golden Config Settings | `cEOS Lab Settings` wiring repo + paths + scope |
| Backups / Intended dirs | empty — Day 3 / Day 4 will fill them |

## Day 2 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of your `cEOS Lab Settings` Golden Config Settings page (showing the wired repository + scope) on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress!

In tomorrow's challenge, we will [back up the cEOS devices' running configurations](../Day_03_Backup_Configurations/README.md) via Golden Config's **Backup Configurations** job, then inspect what landed in the backup repo. See you tomorrow!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+2+of+the+Golden+Config+expansion+pack+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 2 of the Golden Config expansion pack of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
