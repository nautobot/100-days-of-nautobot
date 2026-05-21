# Day 1: Upgrade Nautobot, then Install Golden Config

Today is two phases:

1. **Upgrade** the Nautobot stack from 2.3.2 / Python 3.10 to 2.4.33 / Python 3.12. Golden Config's current 2.x line (2.6.x) requires Nautobot ≥ 2.4.20 — staying on 2.3.2 would force us onto Golden Config 2.3.0, which is older and missing recent UX. One hop forward gets us the modern stack.
2. **Install** `nautobot-golden-config` and wire it into `PLUGINS` / `PLUGINS_CONFIG`.

By the end of today, the app is loaded, migrations are applied, and the **Apps → Golden Configuration** menu appears in the UI.

## Prerequisites — Bring up the Scenario 1 baseline

This pack starts from the **Scenario 1 baseline** (Python 3.10 / Nautobot 2.3.2, Scenario 1 starter SQL dump loaded). If you already have that baseline running from another expansion pack, skip ahead to Phase 1.

If you launched a fresh Codespace from this repository's **Lab Scenario 1** devcontainer config (`.devcontainer/Lab_Scenario_1/`), `~/nautobot-docker-compose` is already cloned but the stack is not yet running. Bring it up:

```
$ cd ~/nautobot-docker-compose
$ cp invoke.example.yml invoke.yml
```

Edit `invoke.yml` so `python_ver` reads `"3.10"`:

```yaml
nautobot_docker_compose:
  python_ver: "3.10"
  # ... other entries unchanged
```

Then:

```
$ invoke build              # several minutes — builds the Nautobot 2.3.2 / py3.10 image
$ invoke db-import          # loads the Scenario 1 starter SQL dump into the empty Postgres volume
$ invoke debug              # second terminal: brings the stack online in the foreground
```

In a second terminal, confirm Nautobot 2.3.2 is running:

```
$ docker exec nautobot-docker-compose-nautobot-1 nautobot-server --version
Nautobot version: 2.3.2
```

Open the Nautobot UI at `:8080` (forwarded port in the Codespace), log in as `admin / admin`, confirm the footer shows **v2.3.2**. With the baseline healthy, `invoke stop` in the first terminal and continue to Phase 1.

> ⚠️ **Order matters: `invoke db-import` *before* `invoke debug`.** The Postgres volume is empty out of the box. If you run `invoke debug` first, Nautobot initializes the schema against the empty DB, and the next `invoke db-import` then fails with `relation "..." already exists`. If you tripped this, run `invoke stop`, drop the postgres volume (`docker volume ls` to find the name, then `docker volume rm <name>`), and start the bring-up sequence over.

## Phase 1 — Upgrade Nautobot 2.3.2 → 2.4.33

The [3.1 Upgrade Lab Day 1](../../Nautobot_3_1_Upgrade_Lab/Day_01_Upgrade/README.md) walks the full 2.3.2 → 3.1.2 path in three hops. We only need its **first** hop (2.3.2 → 2.4.33). Stop after Hop 1 — do **not** continue to 3.0 / 3.1, because Golden Config 2.x targets Nautobot 2.x.

For the full reasoning behind each step, read [Hop 1 in the Upgrade Lab](../../Nautobot_3_1_Upgrade_Lab/Day_01_Upgrade/README.md#hop-1-232--2433-also-python-38--312). The condensed commands you need to run are below.

### Snapshot the DB first

```
$ cd ~/nautobot-docker-compose
$ docker exec nautobot-docker-compose-db-1 pg_dump -h localhost -d nautobot -U nautobot > nautobot.sql
```

### Edit `pyproject.toml`

Three changes:

```toml
[tool.poetry]
name = "nautobot-docker-compose"
version = "0.1.1"
package-mode = false   # NEW — required for Poetry 2.x in the 2.4 build image

[tool.poetry.dependencies]
# old: python = ">=3.9,<3.12"
python = ">=3.10,<3.13"

# old: nautobot = "2.3.2"
nautobot = "2.4.33"
```

### Edit `environments/Dockerfile`

In the existing `RUN cd /source && poetry install ...` block, add the `poetry self add poetry-plugin-export` line so the build image gets the Poetry-2.x export plugin:

```dockerfile
RUN cd /source && \
    poetry install --no-interaction --no-ansi && \
    poetry self add poetry-plugin-export || true && \
    mkdir /tmp/dist && \
    poetry export --without-hashes -o /tmp/dist/requirements.txt
```

### Edit `invoke.yml`

You created `invoke.yml` in the prerequisites section above with `python_ver: "3.10"`. Bump it to `"3.12"`:

```yaml
nautobot_docker_compose:
  python_ver: "3.12"     # was "3.10"
  # ... other entries unchanged
```

> ℹ️ The 3.1 Upgrade Lab Day 1 edits `tasks.py` for this same value — it doesn't have an `invoke.yml`. We do (from the Scenario 1 baseline setup above), and `invoke.yml`'s value **overrides** anything in `tasks.py`. So we only need to edit `invoke.yml`; `tasks.py`'s long-standing `"3.8"` default is moot for us.

### Rebuild and migrate

```
$ poetry lock
$ invoke stop
$ docker pull ghcr.io/nautobot/nautobot:2.4.33-py3.12
$ docker pull ghcr.io/nautobot/nautobot-dev:2.4.33-py3.12
$ invoke build         # several minutes — uses the pre-pulled base images above
$ invoke start
$ docker exec nautobot-docker-compose-nautobot-1 nautobot-server migrate dcim --fake
$ invoke migrate
$ invoke post-upgrade
```

The `--fake dcim` step reconciles seed-data drift in the Scenario 1 starter dump — without it, `invoke migrate` will try to add columns the database already has.

### Verify

```
$ docker exec nautobot-docker-compose-nautobot-1 nautobot-server --version
Nautobot version: 2.4.33

$ docker exec nautobot-docker-compose-nautobot-1 python --version
Python 3.12.x
```

## Phase 2 — Install Golden Config

### Step 1 — Add `nautobot-golden-config` as a Poetry dependency

Now that we are on Nautobot 2.4.33, the current 2.6.x line of Golden Config is what we want. Pin to the 2.6 line specifically:

```
(nautobot-docker-compose-py3.10) $ poetry shell
(nautobot-docker-compose-py3.10) $ poetry add 'nautobot-golden-config@~2.6'
```

`~2.6` resolves to `>=2.6.0, <3.0.0` in Poetry — currently picks 2.6.4 (the latest 2.x). Transitive deps pulled in: `hier-config`, `matplotlib`, `deepdiff`, `django-pivot`, `xmldiff`, `nautobot-capacity-metrics`, `netutils`, `toml`, and importantly **`nautobot-plugin-nornir`** (Golden Config uses Nornir internally for its Backup job — we will not run that job in this pack, but the dependency comes along anyway).

### Step 2 — Wire into `nautobot_config.py`

Edit `config/nautobot_config.py`. Add `nautobot_golden_config` to the `PLUGINS` list and add the `PLUGINS_CONFIG` block:

```python
PLUGINS = [
    "nautobot_golden_config",
]

PLUGINS_CONFIG = {
    "nautobot_golden_config": {
        "enable_backup": True,
        "enable_compliance": True,
        "enable_intended": True,
        "enable_sotagg": True,
    },
}
```

We will use `backup`, `intended`, and `compliance` on Days 3 and 4. `sotagg` (SOT aggregation) is left on so the Jinja templates we write on Day 2 have the option of pulling richer GraphQL context if we extend them later.

> 💡 **Already completed the Device Onboarding pack in this codespace?** Your `PLUGINS` list already contains DO's three entries (`nautobot_plugin_nornir`, `nautobot_ssot`, `nautobot_device_onboarding`) and `PLUGINS_CONFIG` has matching entries. Keep all of them — just **append** `nautobot_golden_config` to the existing list and add the `PLUGINS_CONFIG["nautobot_golden_config"]` entry alongside the DO ones.

### Step 3 — Rebuild the image (again, with GC this time)

```
(nautobot-docker-compose-py3.10) $ invoke stop
(nautobot-docker-compose-py3.10) $ invoke build
```

### Step 4 — Start the stack

```
(nautobot-docker-compose-py3.10) $ invoke debug
```

`invoke debug` runs the stack in the foreground so you can watch the logs as Nautobot loads the Golden Config app on startup.

### Step 5 — Apply Golden Config migrations

In a **second terminal**:

```
$ cd ~/nautobot-docker-compose
$ poetry shell
(nautobot-docker-compose-py3.10) $ invoke post-upgrade
```

The job output starts with a one-time security warning (Golden Config installs a custom API root view — expected, harmless), then walks through the migration list. The opening looks like this:

```
Running docker compose command "ps --services --filter status=running"
Running docker compose command "exec nautobot nautobot-server post_upgrade"
01:00:35.739 WARNING nautobot.core.api.routers routers.py                   get_api_root_view() :
  Something has changed an OrderedDefaultRouter's APIRootView attribute to a custom class. Please verify that class GoldenConfigRootView implements appropriate authentication controls.
Performing database migrations...
Operations to perform:
  Apply all migrations: admin, auth, circuits, cloud, constance, contenttypes, dcim, django_celery_beat, django_celery_results, extras, ipam, nautobot_golden_config, sessions, silk, social_django, taggit, tenancy, users, virtualization, wireless
```

Look for **`nautobot_golden_config`** in that `Apply all migrations:` list — those are the Golden Config tables (Compliance Rules, Compliance Features, Settings, ConfigPlans, etc.) being created in this run.

### Step 6 — Verify in the UI

Open the Nautobot UI on port 8080. The footer should show **v2.4.33** now. Under **Apps → Installed Apps**, you should see **Golden Configuration** listed. (If you came in from the Device Onboarding pack, you will also see `Nautobot Plugin for Nornir`, `Single Source of Truth`, and `Device Onboarding` from there.)

![Apps → Installed Apps page in the Nautobot UI showing Golden Configuration installed after Day 1](../images/day1_installed_apps.png)

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

![Apps → Golden Configuration menu group in the Nautobot left nav after Day 1 install](../images/day1_golden_config_menu.png)

We will seed four mock cEOS Devices and configure **Golden Config Settings** on Day 2.

## Day 1 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of your new Nautobot 2.4.33 footer + the **Apps → Golden Configuration** menu in your Nautobot UI on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress!

In tomorrow's challenge, we will [seed four mock cEOS Devices and set up the templates Git repository and Golden Config Settings](../Day_02_Templates_And_Settings/README.md) — the per-Platform wiring that tells Golden Config where to read Jinja templates from and where to write backups / intended configs. See you tomorrow!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+1+of+the+Golden+Config+expansion+pack+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 1 of the Golden Config expansion pack of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
