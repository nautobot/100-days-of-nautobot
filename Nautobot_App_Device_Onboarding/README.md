# Nautobot Device Onboarding App — Expansion Pack

A four-day walkthrough for installing and using [`nautobot-app-device-onboarding`](https://github.com/nautobot/nautobot-app-device-onboarding) on top of the Lab Scenario 1 environment. By the end of Day 4, you will have onboarded the four Containerlab cEOS devices that ship with Scenario 1 (Boston + NYC) into Nautobot as real Devices with populated platforms, interfaces, and management IPs.

The pack stays on **Nautobot 2.3.2** but bumps the container's Python from 3.8 to **3.10** in Day 1 (the repo's `pyproject.toml` requires `python >= 3.9, < 3.12`, and a fresh `invoke build` needs that). If you want Device Onboarding on the upgraded 3.1.2 environment from the [Nautobot 3.1 Upgrade Lab](../Nautobot_3_1_Upgrade_Lab/README.md), wait for a future companion pack — Device Onboarding 5.x targets Nautobot 3.x and is a different code path.

## Prerequisites

- **Lab Scenario 1 booted** — see [Lab Setup Scenario 1](../Lab_Setup/scenario_1_setup/README.md).
- **Containerlab cEOS topology launched** — requires a one-time Arista cEOS image upload (free Arista account). The setup is documented in `Lab_Setup/scenario_1_setup/README.md` under "Containerlab". Most learners who finished Day009+ already have this.
- Familiarity with [Day041](../Day041_Installing_and_Uninstalling_Apps/README.md) (the install / `PLUGINS` pattern this pack reuses).

## Packages added

| Package | Constraint | Why |
|---------|-----------|-----|
| `nautobot-device-onboarding` | `^4` | The 4.x line targets Nautobot 2.x. 5.x targets Nautobot 3.x. |
| `nautobot-ssot` | `^3` | Paired with Device Onboarding 4.x. SSoT 4.x is for Nautobot 3.x. |
| `nautobot-plugin-nornir` | (transitive) | Pulled in by Device Onboarding; required by the Sync-Data-from-Network job. |

Day 1 adds these via `poetry add` so they end up in `pyproject.toml` + `poetry.lock` and get baked into the image by `invoke build`. Exact patch versions Poetry picks (e.g. `4.2.6`, `3.5.0`) get recorded in `poetry.lock` for reproducibility.

## The four Days

| Day | Topic |
|-----|-------|
| 1 | [Install Device Onboarding](Day_01_Install/README.md) — `poetry add`, `invoke build`, `PLUGINS` + `PLUGINS_CONFIG`, post-upgrade, verify in the UI |
| 2 | [Pre-Onboarding Data](Day_02_Pre_Onboarding_Data/README.md) — Locations, Statuses, Roles, and a SecretsGroup for the cEOS `admin`/`admin` credentials |
| 3 | [Run the Onboarding Job](Day_03_Run_Onboarding_Job/README.md) — look up cEOS container IPs, run the **Perform Device Onboarding** job, inspect what got created |
| 4 | [Validate and Wrap](Day_04_Validate_And_Wrap/README.md) — cross-check populated DCIM data, observe idempotency on a re-run, real-world correlation |

## Reference

- [`nautobot-app-device-onboarding` README](https://github.com/nautobot/nautobot-app-device-onboarding)
- [Install guide (4.2.6)](https://github.com/nautobot/nautobot-app-device-onboarding/blob/v4.2.6/docs/admin/install.md)
- [`demo.nautobot.com`](https://demo.nautobot.com/) — running 3.1.2 but a useful reference for what populated Device data should look like
