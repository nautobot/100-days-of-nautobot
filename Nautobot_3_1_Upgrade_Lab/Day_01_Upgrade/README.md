# Day 1: Upgrade

Today we walk the upgrade from Nautobot 2.3.2 all the way to 3.1.2, following the [Upgrading from Nautobot v2](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/upgrading/from-v2/) doc and the [3.1 release notes upgrade-actions](https://docs.nautobot.com/projects/core/en/stable/release-notes/version-3.1/#upgrade-actions). The path is three image-tag hops: **2.3.2 → 2.4.33 → 3.0.latest → 3.1.2**.

## Strategy

The lab uses a single repeatable pattern at each hop. We never edit running code — we edit version pins and rebuild the container against them.

1. **Snapshot the database.** Take a `pg_dump` to the host. This is our recovery point if anything wedges, and the only way to carry data across the Postgres major-version bump in Hop 2.
2. **Edit version pins** (not source code):
   - Nautobot version → `pyproject.toml`
   - Python version → `tasks.py` (`python_ver` in the invoke config)
   - Postgres version → `environments/docker-compose.postgres.yml`
3. **Regenerate `poetry.lock`** so the build container's poetry resolver does not refuse to install against a stale lock.
4. **Rebuild the image** with `invoke build` — pulls the new Nautobot base image (`ghcr.io/nautobot/nautobot:<ver>-py<py>`).
5. **Start, migrate, post-upgrade.** `invoke start` brings the new image up; `invoke migrate` advances the schema; `invoke post-upgrade` rebuilds caches and content types.
6. **Verify the version banner** and smoke-test the UI before moving on.

Across the entire lab you edit **four files** and run a stable rotation of `invoke` and `docker exec` commands. The hop-to-hop changes are concentrated in the version pins; everything else is the same.

## Environment Setup

Same as [Lab Setup Scenario 1](../../Lab_Setup/scenario_1_setup/README.md):

```
$ cd nautobot-docker-compose/
$ poetry shell
$ invoke build
$ source db_import_prep.sh
$ invoke db-import
$ invoke debug
```

Open a second terminal (also `cd nautobot-docker-compose && poetry shell`) and confirm the starting state:

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server --version
Nautobot version: 2.3.2
Django version: 4.2.16
Configuration file: /opt/nautobot/nautobot_config.py

$ docker exec nautobot_docker_compose-nautobot-1 python --version
Python 3.8.19

$ docker exec nautobot_docker_compose-db-1 psql --version
psql (PostgreSQL) 13.23
```

Python and Postgres are both below the 3.1 floors (Python 3.10+, Postgres 14+). Nautobot 2.4 already dropped Python 3.8, so Python bumps at Hop 1. Postgres bumps at Hop 2.

## Pre-flight Validation (from the v2 upgrade doc)

The [v2 upgrade doc](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/upgrading/from-v2/) requires running `validate_models` before the jump. Run it now:

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server validate_models extras.dynamicgroup extras.savedview
Validating 2 models.
extras.DynamicGroup
extras.SavedView
```

That's the full output — nothing is flagged in the pre-baked Scenario 1 dataset.

> [!NOTE]
> The v2 upgrade doc also references `check_job_approval_status`, which requires Nautobot 2.4.15+. We will run it after Hop 1.

## Check `nautobot_config.py` for Removed Settings (from the 3.1 upgrade-actions)

The [3.1 release notes](https://docs.nautobot.com/projects/core/en/stable/release-notes/version-3.1/#upgrade-actions) list ten settings that were removed. Grep your config:

```
$ grep -E 'DEFAULT_FILE_STORAGE|STATICFILES_STORAGE|STORAGE_BACKEND|STORAGE_CONFIG|JOB_FILE_IO_STORAGE|DATE_FORMAT|DATETIME_FORMAT|TIME_FORMAT|SHORT_DATE_FORMAT|SHORT_DATETIME_FORMAT' config/nautobot_config.py
```

Output is empty — Scenario 1's `config/nautobot_config.py` does not set any of them, so there is nothing to remove. Nautobot's 3.1 defaults will apply on the post-upgrade boot.

### Reference: STORAGES dict for 3.1

For reference only. If your real-world `nautobot_config.py` had set any of the five collapsed storage settings, the [3.1 default shape](https://github.com/nautobot/nautobot/blob/v3.1.2/nautobot/core/settings.py) is:

```python
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "nautobotjobfiles": {
        "BACKEND": "db_file_storage.storage.DatabaseFileStorage",
    },
}
```

## How a Version Bump Works in `nautobot-docker-compose`

Two files control what the image builds against:

| File | What to edit |
|------|--------------|
| `pyproject.toml` | the `nautobot = "<version>"` line — read by `tasks.py` and passed as build arg `NAUTOBOT_VERSION` |
| `tasks.py` | the `python_ver: "<py>"` line in the invoke config — passed as build arg `PYTHON_VER` |

Postgres is pinned separately in `environments/docker-compose.postgres.yml` (`image: "postgres:13-alpine"`).

## Snapshot the Database

Before the first hop, export the current database — we will need it to recover from any wedge and to re-import after the Postgres major-version bump in Hop 2.

> [!IMPORTANT]
> `invoke db-export` has a known wart: it writes `/tmp/nautobot.sql` *inside* the postgres container, where the running user lacks write permission. Bypass it with a host-side redirect:

```
$ docker exec nautobot_docker_compose-db-1 pg_dump -h localhost -d nautobot -U nautobot > nautobot.sql
```

Confirm the dump landed:

```
$ ls -lh nautobot.sql
$ head -3 nautobot.sql
-- PostgreSQL database dump
--
-- Dumped from database version ...
```

The file lives at `~/nautobot-docker-compose/nautobot.sql` — exactly where `invoke db-import` expects to find it.

## Hop 1: 2.3.2 → 2.4.33 (also Python 3.8 → 3.12)

Nautobot 2.4 dropped Python 3.8 — the `ghcr.io/nautobot/nautobot-dev:2.4.33-py3.8` image does not exist. We bump Python at the same time. **Python 3.12 covers the whole upgrade chain** (2.4.33, 3.0.x, and 3.1.2 all support 3.10–3.12).

Edit `pyproject.toml` — three changes:

1. **Nautobot pin** — bump to 2.4.33.
2. **Python constraint** — `nautobot-docker-compose`'s default pin is `>=3.9,<3.12`, which excludes 3.12.
3. **`package-mode = false`** under `[tool.poetry]` — Nautobot's 2.4 build container ships a newer Poetry that, unlike the one in the 2.3 container, refuses to install if it cannot find a project package. Setting `package-mode = false` tells Poetry "I'm only using you for dependencies."

```toml
[tool.poetry]
name = "nautobot-docker-compose"
version = "0.1.1"
package-mode = false   # new line — required for newer Poetry in the 2.4 build image
...

[tool.poetry.dependencies]
# old value: python = ">=3.9,<3.12"
python = ">=3.10,<3.13"

# old value: nautobot = "2.3.2"
nautobot = "2.4.33"
```

Edit `environments/Dockerfile` — in Poetry 2.x the `export` command moved to a separate plugin. Add a `poetry self add` line in the existing build-step `RUN` block (around lines 28–34):

Old block:

```dockerfile
RUN cd /source && \
    poetry install --no-interaction --no-ansi && \
    mkdir /tmp/dist && \
    poetry export --without-hashes -o /tmp/dist/requirements.txt
```

New block:

```dockerfile
RUN cd /source && \
    poetry install --no-interaction --no-ansi && \
    # new line — install the export plugin for Poetry v2; passes silently for v1
    poetry self add poetry-plugin-export || true && \
    mkdir /tmp/dist && \
    poetry export --without-hashes -o /tmp/dist/requirements.txt
```

Edit `tasks.py` at `~/nautobot-docker-compose/tasks.py` (same directory as `pyproject.toml`). Change the `python_ver` default in the `namespace.configure({...})` block near the top of the file. This sticks for all three hops, so we don't have to re-export an env var every session.

```python
namespace.configure(
    {
        "nautobot_docker_compose": {
            "project_name": "nautobot_docker_compose",
            # old value: "python_ver": "3.8",
            "python_ver": "3.12",
            ...
        }
    }
)
```

Regenerate `poetry.lock` so it matches the new `pyproject.toml`. Without this, the build container's poetry will refuse to install because the lock is stale.

```
$ poetry lock
```

Stop the 2.3.2 containers before rebuilding so the new image replaces them cleanly.

```
$ invoke stop
```

Rebuild the Nautobot image. The output banner should read `Building Nautobot 2.4.33 with Python 3.12...`.

```
$ invoke build
```

Start the containers with the new image.

```
$ invoke start
```

Scenario 1's seed data was captured from a Nautobot install slightly ahead of 2.3.2, so a few `dcim` migrations are silently applied at the schema level but not recorded in `django_migrations`. Mark them all as already applied without running their SQL — this prevents `invoke migrate` from trying to add columns that already exist.

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server migrate dcim --fake
```

Run the remaining migrations from 2.3.2 to 2.4.33.

```
$ invoke migrate
```

Apply Nautobot's standard post-upgrade tasks (cache reload, content-type cleanup, etc.).

```
$ invoke post-upgrade
```

Confirm Nautobot and Python both reflect the new versions:

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server --version
Nautobot version: 2.4.33

$ docker exec nautobot_docker_compose-nautobot-1 python --version
Python 3.12.x
```

Now that we are past 2.4.15, the second pre-flight command the v2 upgrade doc referenced is available. Save its output — Day 2 needs it.

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server check_job_approval_status > /workspaces/100-days-of-nautobot/upgrade-notes-preflight.txt
```

### Hop 1 Recap

| What | From → To |
|------|-----------|
| Nautobot | 2.3.2 → 2.4.33 |
| Python | 3.8 → 3.12 |
| Poetry shape in `pyproject.toml` | added `package-mode = false`, widened Python constraint |
| `environments/Dockerfile` | added `poetry self add poetry-plugin-export` |
| `tasks.py` | `python_ver` set to `"3.12"` (persists for all hops) |
| dcim migrations | `--fake`d to reconcile seed-data drift |
| Pre-flight notes | `check_job_approval_status` output saved for Day 2 |

## Hop 2: 2.4.33 → 3.0.11 (also Postgres 13 → 14)

Two things change for this hop: Nautobot and Postgres. Python stays at 3.12. Use a concrete `3.0.11` pin — `tasks.py` reads the version string verbatim and passes it as the Docker image tag, so Poetry-style constraints like `~3.0.0` break the build.

Confirm `~/nautobot-docker-compose/tasks.py` still has `python_ver` at `"3.12"` from Hop 1. If it somehow reverted, set it now — without this, the build will try to pull a `-py3.8` image that does not exist for 3.0.x.

```python
        "nautobot_docker_compose": {
            "project_name": "nautobot_docker_compose",
            # old value: "python_ver": "3.8",
            "python_ver": "3.12",
            "local": False,
```

Edit `pyproject.toml` — bump the Nautobot pin:

```toml
# old value: nautobot = "2.4.33"
nautobot = "3.0.11"
```

Edit `environments/docker-compose.postgres.yml` — bump the Postgres image (3.1's Django 5.2 floor is PG14):

```yaml
services:
  db:
    # old value: image: "postgres:13-alpine"
    image: "postgres:14-alpine"
```

Regenerate the lock file for the new Nautobot pin.

```
$ poetry lock
```

Stop the 2.4.33 containers so we can swap the image and reset the Postgres volume.

```
$ invoke stop
```

PG13's data directory is not directly readable by PG14. Destroy the old Postgres volume so PG14 starts on a fresh data directory.

```
$ docker volume rm nautobot_docker_compose_postgres_data
```

Rebuild the Nautobot image against `3.0.11`. The build banner should read `Building Nautobot 3.0.11 with Python 3.12...`.

```
$ invoke build
```

Start just the db container so PG14 can run `initdb` on the new volume. A fresh PG14 init takes a few seconds — longer than the 2-second sleep `invoke db-import` does internally.

```
$ docker compose -f environments/docker-compose.postgres.yml -f environments/docker-compose.base.yml --project-name nautobot_docker_compose up -d db
```

Wait until Postgres is accepting connections — the loop exits as soon as `pg_isready` reports OK.

```
$ until docker exec nautobot_docker_compose-db-1 pg_isready -U nautobot -d nautobot; do sleep 1; done
```

Re-import the snapshot we took at the start of Day 1 into the fresh PG14 volume.

```
$ invoke db-import
```

Start the containers.

```
$ invoke start
```

Nautobot 3.0 changed how dynamic settings are stored — values in `constance_constance` now have to be JSON-encoded, but the rows imported from the 2.4 snapshot are not. Clear the table so 3.0's autofill repopulates defaults in the right format.

```
$ docker exec nautobot_docker_compose-db-1 psql -U nautobot -d nautobot -c "DELETE FROM constance_constance;"
```

Run the 2.4.33 → 3.0.11 migrations.

```
$ invoke migrate
```

Run the standard post-upgrade tasks.

```
$ invoke post-upgrade
```

Confirm versions:

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server --version
Nautobot version: 3.0.11

$ docker exec nautobot_docker_compose-db-1 psql --version
psql (PostgreSQL) 14.x
```

Smoke-test in the UI — log in, click around, confirm the Retail-r-Us devices are still visible.

### Hop 2 Recap

| What | From → To |
|------|-----------|
| Nautobot | 2.4.33 → 3.0.11 |
| Postgres | 13.23 → 14.x (volume reset + re-import from snapshot) |
| `constance_constance` table | cleared so 3.0's JSON encoding could autofill defaults |
| Django (carried by Nautobot) | 4.2.16 → 4.2.30 |

## Hop 3: 3.0.11 → 3.1.2

The final hop. Same pattern — a single concrete version pin.

Edit `pyproject.toml`:

```toml
# old value: nautobot = "3.0.11"
nautobot = "3.1.2"
```

Regenerate the lock file.

```
$ poetry lock
```

Stop the 3.0.11 containers.

```
$ invoke stop
```

Rebuild against `3.1.2`. The build banner should read `Building Nautobot 3.1.2 with Python 3.12...`.

```
$ invoke build
```

Start the containers.

```
$ invoke start
```

The seed-data drift surfaces once more — `ipam.0055` is a `rename_index` operation that points at an index name the snapshot does not have. Fake only that one migration (we still need the legitimate 3.0 → 3.1 ipam schema changes after it).

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server migrate ipam 0055 --fake
```

Apply the 3.0.11 → 3.1.2 migrations.

```
$ invoke migrate
```

Run post-upgrade.

```
$ invoke post-upgrade
```

Refresh static assets — 3.1 ships new versions of CSS/JS bundles.

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server collectstatic --noinput
```

Confirm:

```
$ docker exec nautobot_docker_compose-nautobot-1 nautobot-server --version
Nautobot version: 3.1.2
```

Compare your UI to [demo.nautobot.com](https://demo.nautobot.com/) — same version, same navigation.

### Hop 3 Recap

| What | From → To |
|------|-----------|
| Nautobot | 3.0.11 → 3.1.2 |
| Django (carried by Nautobot) | 4.2.x → 5.2.x |
| Static assets | refreshed via `collectstatic --noinput` |

The Scenario 1 environment is now on the same Nautobot version that backs [demo.nautobot.com](https://demo.nautobot.com/). The upgrade portion of the lab is complete — Day 2 covers the post-upgrade fix-ups (approvals, jobs, REST API, app audit).

## If It Breaks

```
$ invoke stop
$ docker volume rm nautobot_docker_compose_postgres_data
```

Revert the `pyproject.toml` pin, `invoke build`, then `invoke db-import` to restore from `nautobot.sql`.

## Real-World Correlation

Looking back at Day 1, almost every "fix" we applied — the `--fake` migrations in dcim and ipam, the `DELETE FROM constance_constance`, the Postgres volume rebuild from the SQL snapshot — was about **the database**, not Nautobot or Python. The Nautobot image swaps themselves were boring. It was the data that pushed back.

That mirrors production reality. A few lessons that translate directly:

- **The database is the highest-risk surface of any Nautobot upgrade.** Schema drift between an old snapshot and a new migration tree, dynamic-settings tables (constance) changing encoding, index renames that assume a name your DB does not have — none of these are visible from release notes. They surface only when you migrate real data.
- **Always snapshot before each major hop, not just at the start.** This lab only snapshots once because the lab is short. In production, take a fresh `pg_dump` before *every* hop and label it with the version it came from. Recovery becomes simple — go back to the snapshot from the last known-good version.
- **Run every pre-flight command the docs require.** Today we ran `validate_models` on 2.3.2 and `check_job_approval_status` after reaching 2.4.15+. In production those are non-optional; they tell you which rows of *your* data will fail before you start.
- **Treat `--fake` as a deliberate, narrow tool.** Use it only when you have verified that the schema already reflects what the migration would do. The pattern we used — fake a specific migration number, then resume `migrate` — is the right shape. Faking an entire app is risky if later migrations include real schema changes you actually need.
- **Dynamic-settings stores (constance, django-celery-beat, etc.) often change encoding across versions.** They are easy to miss because they are not part of the model graph that migrations walk. When in doubt, clear them and let the app re-populate defaults, then re-apply customizations from your own records.
- **Postgres major-version bumps cost extra.** You can't reuse PG13's data directory under PG14. The lab does this as a dump → fresh volume → import. In production, plan for the same — pg_upgrade or dump/restore — and budget downtime accordingly.
- **Plan per-hop change windows.** This lab compresses three Nautobot hops into one Day for pedagogy. In production, 2.x → 2.4.latest, 2.4 → 3.0, and 3.0 → 3.1 are three separate change windows with three sets of approvals, smoke tests, and rollback plans.
- **The tooling differs, the pattern doesn't.** Your production environment is probably Kubernetes/Helm or Ansible, not `nautobot-docker-compose`. But the same skeleton applies: pin a new version, rebuild the image, migrate, post-upgrade, smoke-test, verify, repeat.

## Day 1 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/). 

Go ahead and post a screenshot of your upgraded Nautobot 3.1.2 version banner, or share one lesson learned from the migration (the `--fake` migration trick, the constance reset, the PG13→PG14 jump — your pick), on social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress! 

In tomorrow's challenge, we will [tour what is different in 3.1](../Day_02_What_Is_Different_in_3_1/README.md) — UI changes, Django 5.2 deprecations, and what to watch for when replaying Days 1–100 against the upgraded environment. See you tomorrow! 

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+1+of+the+Nautobot+3.1+Upgrade+Lab+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 1 of the Nautobot 3.1 Upgrade Lab of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)
