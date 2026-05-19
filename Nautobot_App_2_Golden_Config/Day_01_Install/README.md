# Day 1: Install Golden Config

Today we install [`nautobot-app-golden-config`](https://github.com/nautobot/nautobot-app-golden-config) on top of the Nautobot stack you built in the [Device Onboarding pack](../../Nautobot_App_1_Device_Onboarding/README.md). No backups, no templates, no compliance yet — that is Day 2 onward. By the end of today, the app is loaded, migrations are applied, and the **Apps → Golden Config** menu shows up in the UI.

## Step 1 — Pick the right version pin

`nautobot-golden-config` has shipped both Nautobot-2.x and Nautobot-3.x compatible lines:

| GC version | Targets Nautobot |
|------------|------------------|
| `2.0.x` – `2.3.x` | `>=2.0, <3.0` ✓ (works on our 2.3.2) |
| `2.4.x` – `2.6.x` | `>=2.4.2` ✗ (will not resolve against 2.3.2) |
| `3.x` | Nautobot 3.x only |

An unconstrained `poetry add 'nautobot-golden-config@^2'` would pick **2.6.4** (the latest 2.x), which then fails to resolve against `nautobot = "2.3.2"`. The right pin is **`~2.3`** (tilde-2.3 = `>=2.3.0, <2.4.0`):

```
$ cd ~/nautobot-docker-compose
$ poetry shell
(nautobot-docker-compose-py3.10) $ poetry add 'nautobot-golden-config@~2.3'
```

Poetry resolves to `2.3.0` and pulls these new transitive dependencies along the way: `hier-config`, `matplotlib`, `deepdiff`, `django-pivot`, `xmldiff`, `nautobot-capacity-metrics`, `netutils`, `toml`, `numpy`. `nautobot-plugin-nornir` is already installed by Device Onboarding, so Poetry just confirms it.

This updates `pyproject.toml` + `poetry.lock`. The exact patch versions Poetry picks are recorded in `poetry.lock` for reproducibility.

## Step 2 — Wire into `nautobot_config.py`

Edit `nautobot-docker-compose/config/nautobot_config.py`. **Append** `nautobot_golden_config` to the existing `PLUGINS` list (do not replace — Device Onboarding's three entries must stay) and add a minimal `PLUGINS_CONFIG` entry:

```python
# from Device Onboarding Day 1:
PLUGINS = [
    "nautobot_plugin_nornir",
    "nautobot_ssot",
    "nautobot_device_onboarding",
    "nautobot_golden_config",   # <-- new
]

PLUGINS_CONFIG = {
    # ... existing entries from Device Onboarding ...
    "nautobot_golden_config": {
        "enable_backup": True,
        "enable_compliance": True,
        "enable_intended": True,
        "enable_sotagg": True,
    },
}
```

The `enable_*` flags surface their corresponding jobs and UI sub-pages. We will use `backup`, `intended`, and `compliance` on Days 3 and 4; `sotagg` (SOT aggregation) is left on so the Jinja templates we write on Day 2 can pull richer GraphQL context if we want.

## Step 3 — Rebuild the image

```
(nautobot-docker-compose-py3.10) $ invoke stop
(nautobot-docker-compose-py3.10) $ invoke build
```

`invoke build` re-runs `poetry install` inside the builder stage with the new dependency. Several minutes. The Postgres data volume is preserved (your Device Onboarding state — the onboarded cEOS devices, SecretsGroup, etc. — survives this rebuild).

## Step 4 — Start the stack, then re-apply the lab patches

```
(nautobot-docker-compose-py3.10) $ invoke debug
```

In a **second terminal**, re-apply the Containerlab compatibility patches (the previous containers were destroyed by `invoke stop`, so the runtime patches we applied during Device Onboarding are gone):

```
$ cd ~/100-days-of-nautobot
$ bash Nautobot_App_1_Device_Onboarding/scripts/patch_lab_ceos.sh
```

The script bridges the Nautobot containers onto Containerlab's network, patches the `arista_eos_show_version` TextFSM template, and patches the `arista_eos.yml` mapper YAML's hostname entry. Same patches Golden Config will need on Day 3 when its Backup job SSH's into the cEOS devices via Nornir.

## Step 5 — Apply migrations

Still in the second terminal:

```
$ cd ~/nautobot-docker-compose
$ poetry shell
(nautobot-docker-compose-py3.10) $ invoke post-upgrade
```

Look for `nautobot_golden_config` in the migrations list — those are the Golden Config tables (Compliance Rules, Compliance Features, Settings, ConfigPlans, etc.) being created.

## Step 6 — Verify in the UI

Open the Nautobot UI on port 8080. Under **Apps → Installed Apps**, you should now see four apps:

- `Nautobot Plugin for Nornir`
- `Single Source of Truth`
- `Device Onboarding`
- `Golden Configuration` ← new

The left nav should also gain a new top-level **Apps → Golden Configuration** group with sub-items like:

- **Compliance**
  - Configuration Compliance
  - Compliance Rules
  - Compliance Features
- **Configuration**
  - Config Overview
  - Backup
  - Intended
  - Config Plans
- **Settings**
  - Golden Config Settings
  - Remediation Settings

We will configure **Golden Config Settings** on Day 2.

## Day 1 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of the new **Apps → Golden Configuration** menu in your Nautobot UI on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress!

In tomorrow's challenge, we will [set up the templates Git repository and Golden Config Settings](../Day_02_Templates_And_Settings/README.md) — the per-Platform wiring that tells Golden Config where to read Jinja templates from and where to write backups / intended configs. See you tomorrow!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+1+of+the+Golden+Config+expansion+pack+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 1 of the Golden Config expansion pack of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
