# Day 1: Install Device Onboarding

> 🚧 **Desk-verified, not yet live-verified.** Versions, file paths, and the SSoT job's form fields were confirmed against `nautobot-app-device-onboarding` v4.2.6 source. Steps still need a dry-run in a live Scenario 1 Codespace.

Today we install [`nautobot-device-onboarding`](https://github.com/nautobot/nautobot-app-device-onboarding) on top of Scenario 1 and confirm it shows up in the Nautobot UI. No devices get onboarded today — that is Day 3.

## Environment Setup

Same as [Lab Setup Scenario 1](../../Lab_Setup/scenario_1_setup/README.md). Skip `invoke build` / `invoke db-import` if your Codespace was restarted from a previous session:

```
$ cd nautobot-docker-compose/
$ poetry shell
$ invoke build
$ invoke db-import
$ invoke debug
```

The Containerlab cEOS topology is **not** needed today — we will spin it up on Day 2.

## Install the App

Attach to the Nautobot container:

```
$ docker exec -it nautobot_docker_compose-nautobot-1 bash
```

Install Device Onboarding 4.2.6 along with an explicit SSoT pin. Both pins are needed: Device Onboarding 4.3.0+ requires Python ≥3.9.2, and SSoT 3.6.0+ requires Python ≥3.9.2. The versions below are the last in their lines that still support Scenario 1's Python 3.8.

```
nautobot@<container>:~$ pip install nautobot-device-onboarding==4.2.6 nautobot-ssot==3.5.0
```

`nautobot-plugin-nornir` is pulled in transitively at a 2.x version, which works on Python 3.8 without an explicit pin.

Exit the container shell (`exit`) so we can edit the config file on the host.

## Wire Into `nautobot_config.py`

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

## Apply Migrations

Run `post-upgrade` so Device Onboarding and SSoT create their database tables. (Invoke's CLI accepts the dash form even though the underlying Python task is `post_upgrade` — both work.)

```
$ invoke post-upgrade
```

Restart Nautobot if it did not auto-reload:

```
$ invoke stop
$ invoke debug
```

## Confirm in the UI

Open the Nautobot UI on port 8080. Under **Apps → Installed Apps**, you should now see:

- `nautobot_plugin_nornir`
- `nautobot_ssot`
- `nautobot_device_onboarding`

A new **Apps → Device Onboarding** entry should also appear in the navigation.

## What's Next

[Day 2](../Day_02_Pre_Onboarding_Data/README.md) — set up the Locations, Statuses, Roles, and a SecretsGroup for the cEOS `admin` / `admin` credentials, so Day 3's onboarding job has the data scaffolding it expects.
