# Day 1: Install Device Onboarding

> 🚧 **Partially live-verified.** Install mechanism switched from in-container `pip install` to `poetry add` + `invoke build` after the original draft hit a `ModuleNotFoundError: No module named 'nautobot_plugin_nornir'` on container restart (the in-container install is ephemeral and is lost the moment `invoke stop` recreates the container). Container Python is bumped to 3.10 to match this repo's `pyproject.toml` (`python = ">=3.9,<3.12"`).

Today we install [`nautobot-device-onboarding`](https://github.com/nautobot/nautobot-app-device-onboarding) on top of Scenario 1 and confirm it shows up in the Nautobot UI. No devices get onboarded today — that is Day 3.

The Containerlab cEOS topology is **not** needed today — we will spin it up on Day 2.

## Why we bake the apps into the image

`nautobot-docker-compose` builds its Nautobot image via `environments/Dockerfile`, which copies the repo's `pyproject.toml` and `poetry.lock` into the image and runs `poetry install` at build time. Any `pip install` we do **inside a running container** disappears as soon as `invoke stop` removes that container — the next `invoke debug` will recreate it from the base image without our apps. So the right move is to add the apps as managed Poetry dependencies and rebuild the image once.

## Step 1 — Pin Python 3.10 in `invoke.yml`

`pyproject.toml` requires `python >= 3.9, < 3.12`. The build will fail if the container is built on Python 3.8. Create an `invoke.yml` (none exists by default — only `invoke.example.yml`) and set `python_ver` to `"3.10"`:

```
$ cd ~/nautobot-docker-compose
$ cp invoke.example.yml invoke.yml
```

Edit `invoke.yml` so the `python_ver` line reads:

```yaml
nautobot_docker_compose:
  project_name: "nautobot-docker-compose"
  python_ver: "3.10"
  local: false
  compose_dir: "environments/"
  compose_files:
    - "docker-compose.postgres.yml"
    - "docker-compose.base.yml"
    - "docker-compose.local.yml"
```

This drives the `PYTHON_VER` build arg consumed by `environments/Dockerfile`, which resolves the base image to `ghcr.io/nautobot/nautobot:2.3.2-py3.10`.

## Step 2 — Add the apps as Poetry dependencies

From inside the Poetry shell on the host (not inside the container):

```
$ cd ~/nautobot-docker-compose
$ poetry shell
(nautobot-docker-compose-py3.10) $ poetry add 'nautobot-device-onboarding@^4' 'nautobot-ssot@^3'
```

The `^4` / `^3` major-version constraints are deliberate:

| Package | Constraint | Why |
|---------|-----------|-----|
| `nautobot-device-onboarding` | `^4` (i.e. `>=4, <5`) | The 4.x line targets Nautobot 2.x. Version 5.x targets Nautobot 3.x and is a different code path. |
| `nautobot-ssot` | `^3` (i.e. `>=3, <4`) | Paired with Device Onboarding 4.x. SSoT 4.x ships against Nautobot 3.x. |

An unconstrained `poetry add` would pick the latest majors (currently 5.x + 4.x), which are the **wrong** majors for a Nautobot 2.3.2 image — Poetry would either fail to resolve, or worse, succeed and produce an image that crashes at runtime. `nautobot-plugin-nornir` is pulled in transitively as a dependency of Device Onboarding — no explicit pin needed.

This updates `pyproject.toml` + `poetry.lock`. The exact patch versions Poetry picks (e.g. 4.2.6, 3.5.0) get recorded in `poetry.lock` for reproducibility.

> ℹ️ If you see a resolver error, double-check `python_ver` from Step 1 — most version-conflict errors at this step are actually a stale py3.8 environment trying to install a py3.9-only package.

## Step 3 — Wire into `nautobot_config.py`

Edit `nautobot-docker-compose/config/nautobot_config.py`. Append the three new app names to the `PLUGINS` list and add their settings to `PLUGINS_CONFIG`:

```python
# old value: PLUGINS = []
PLUGINS = ["nautobot_plugin_nornir", "nautobot_ssot", "nautobot_device_onboarding"]

PLUGINS_CONFIG = {
    # ... existing entries ...
    "nautobot_plugin_nornir": {
        "nornir_settings": {
            "credentials": "nautobot_plugin_nornir.plugins.credentials.nautobot_secrets.CredentialsNautobotSecrets",
            "runner": {
                "plugin": "threaded",
                "options": {
                    "num_workers": 20,
                },
            },
        },
    },
    "nautobot_ssot": {},
    "nautobot_device_onboarding": {},
}
```

The `CredentialsNautobotSecrets` reference is required for the **Sync Data from Network** job we use on Day 3. We will create the matching Secrets on Day 2.

## Step 4 — Rebuild the image

Stop any running stack first so containers come up fresh against the new image:

```
(nautobot-docker-compose-py3.10) $ invoke stop
(nautobot-docker-compose-py3.10) $ invoke build
```

`invoke build` is the long step (several minutes — base image pull + `poetry install` inside the builder stage). When it finishes, the new image has Device Onboarding, SSoT, and `nautobot-plugin-nornir` baked in.

> 🧹 Any earlier in-container `pip install` from a previous attempt is discarded by this rebuild — that is intentional.

## Step 5 — Start the stack

```
(nautobot-docker-compose-py3.10) $ invoke debug
```

`invoke debug` runs `docker compose up` in the foreground so you can watch the logs. You should **not** see `ModuleNotFoundError: No module named 'nautobot_plugin_nornir'` — if you do, the build did not produce the expected image. Check `docker images | grep nautobot` and re-run `invoke build`.

## Step 6 — Apply migrations

Device Onboarding and SSoT ship database migrations. Run `post-upgrade` to apply them.

> ⚠️ **Heads up:** open a **second terminal** so `invoke debug` keeps streaming logs in the first. In the second terminal, re-enter the Poetry shell — `invoke` is provided by that virtualenv, not by the system shell.
>
> ```
> $ cd ~/nautobot-docker-compose
> $ poetry shell
> (nautobot-docker-compose-py3.10) $   # prompt should now show the venv
> ```

```
(nautobot-docker-compose-py3.10) $ invoke post-upgrade
```

(`invoke`'s CLI accepts the dash form even though the underlying Python task is `post_upgrade` — both work.)

Nautobot watches its config and reloads automatically. If for some reason the worker still complains, restart with `invoke restart` (which keeps the containers but restarts the processes) — **avoid `invoke stop`**, which would remove and recreate the containers.

## Step 7 — Confirm in the UI

Open the Nautobot UI on port 8080. Under **Apps → Installed Apps**, you should now see:

- `nautobot_plugin_nornir`
- `nautobot_ssot`
- `nautobot_device_onboarding`

A new **Apps → Device Onboarding** entry should also appear in the navigation.

## What's Next

[Day 2](../Day_02_Pre_Onboarding_Data/README.md) — set up the Locations, Statuses, Roles, and a SecretsGroup for the cEOS `admin` / `admin` credentials, so Day 3's onboarding job has the data scaffolding it expects.
