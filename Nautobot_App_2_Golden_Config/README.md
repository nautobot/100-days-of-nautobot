# Nautobot Golden Config App — Expansion Pack

A four-day walkthrough for installing and using [`nautobot-app-golden-config`](https://github.com/nautobot/nautobot-app-golden-config) on top of the lab environment left behind by the [Device Onboarding pack](../Nautobot_App_1_Device_Onboarding/README.md). By the end of Day 4, you will have running-config backups stored in Git, intended configurations rendered from Jinja templates with Nautobot data, and a per-feature compliance dashboard diffing the two — against the four cEOS devices that Device Onboarding put into Nautobot.

The pack stays on **Nautobot 2.3.2 / Python 3.10** — the same image you built in Device Onboarding Day 1.

## Prerequisites

This pack assumes you have **completed the [Device Onboarding expansion pack](../Nautobot_App_1_Device_Onboarding/README.md) end-to-end**. Specifically, you should have:

- The `nautobot-docker-compose` stack on **Python 3.10**, image rebuilt via `invoke build` with `python_ver: "3.10"` in `invoke.yml`.
- The Containerlab cEOS topology deployed with the **corrected hostnames** (`bos-acc-01`, `bos-rtr-01`, `nyc-acc-01`, `nyc-rtr-01`).
- The Nautobot stack containers attached to the default Docker `bridge` network (see [Device Onboarding Day 2](../Nautobot_App_1_Device_Onboarding/Day_02_Pre_Onboarding_Data/README.md#bridge-the-nautobot-stack-onto-the-containerlab-network)), or re-applied via [`patch_lab_ceos.sh`](../Nautobot_App_1_Device_Onboarding/scripts/patch_lab_ceos.sh).
- The four cEOS devices **onboarded into Nautobot** by Device Onboarding Days 3–4 — each with role `network`, platform `arista_eos`, a Primary IPv4, full interface inventory, and a `cEOS Lab Credentials` SecretsGroup association.
- `nautobot-ssot` and `nautobot-plugin-nornir` already installed (Device Onboarding installed them as dependencies; Golden Config uses Nornir too).

If any of those are not in place, start with Device Onboarding first — Golden Config will not have anything useful to operate on otherwise.

## Packages added

| Package | Constraint | Why |
|---------|-----------|-----|
| `nautobot-golden-config` | `^2` | The 2.x line targets Nautobot 2.x. 3.x targets Nautobot 3.x. |

Day 1 adds this via `poetry add` so it lands in `pyproject.toml` + `poetry.lock` and gets baked into the image by `invoke build`. Backup + intended-config jobs use `nautobot-plugin-nornir` (already a transitive dep), so no extra pin needed.

## The four Days

| Day | Topic |
|-----|-------|
| 1 | [Install Golden Config](Day_01_Install/README.md) — `poetry add`, `invoke build`, `PLUGINS` + `PLUGINS_CONFIG`, `invoke post-upgrade`, UI tour |
| 2 | [Templates Git repository + Golden Config Settings](Day_02_Templates_And_Settings/README.md) — wire a Jinja-template repo into Nautobot, scope to the cEOS Devices |
| 3 | [Backup running configurations](Day_03_Backup_Configurations/README.md) — run the **Backup Configurations** job, inspect the per-device files in the backup Git repo |
| 4 | [Intended configurations and compliance](Day_04_Intended_And_Compliance/README.md) — render Jinja templates with Nautobot data, run **Compliance**, walk the dashboard, real-world correlation |

## Reference

- [`nautobot-app-golden-config` README](https://github.com/nautobot/nautobot-app-golden-config)
- [Golden Config user docs](https://docs.nautobot.com/projects/golden-config/en/latest/)
- [Network to Code: Golden Configuration use case overview](https://blog.networktocode.com/post/golden-configuration-network-to-code/)
