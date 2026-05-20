# Nautobot Golden Config App — Expansion Pack

A four-day walkthrough for installing and using [`nautobot-app-golden-config`](https://github.com/nautobot/nautobot-app-golden-config) on top of the lab environment left behind by the [Device Onboarding pack](../Nautobot_App_1_Device_Onboarding/README.md). By the end of Day 4, you will have running-config backups stored in Git, intended configurations rendered from Jinja templates with Nautobot data, and a per-feature compliance dashboard diffing the two — against the four cEOS devices that Device Onboarding put into Nautobot.

The pack runs on **Nautobot 2.4.33 / Python 3.12** — Golden Config's current 2.x line (2.6.x) requires Nautobot ≥ 2.4.20, so Day 1 starts by upgrading the stack from Device Onboarding's 2.3.2 / Python 3.10 baseline. The upgrade is one hop (the same Hop 1 the [3.1 Upgrade Lab Day 1](../Nautobot_3_1_Upgrade_Lab/Day_01_Upgrade/README.md#hop-1-232--2433-also-python-38--312) walks).

## Prerequisites

This pack assumes you have **completed the [Device Onboarding expansion pack](../Nautobot_App_1_Device_Onboarding/README.md) end-to-end**. Specifically, you should have:

- The `nautobot-docker-compose` stack on **Python 3.10 / Nautobot 2.3.2**. (Day 1 of this pack upgrades you to 3.12 / 2.4.33.)
- The Containerlab cEOS topology deployed with the **corrected hostnames** (`bos-acc-01`, `bos-rtr-01`, `nyc-acc-01`, `nyc-rtr-01`).
- The Nautobot stack containers attached to the default Docker `bridge` network (see [Device Onboarding Day 2](../Nautobot_App_1_Device_Onboarding/Day_02_Pre_Onboarding_Data/README.md#bridge-the-nautobot-stack-onto-the-containerlab-network)), or re-applied via [`patch_lab_ceos.sh`](../Nautobot_App_1_Device_Onboarding/scripts/patch_lab_ceos.sh).
- The four cEOS devices **onboarded into Nautobot** by Device Onboarding Days 3–4 — each with role `network`, platform `arista_eos`, a Primary IPv4, full interface inventory, and a `cEOS Lab Credentials` SecretsGroup association.
- `nautobot-ssot` and `nautobot-plugin-nornir` already installed (Device Onboarding installed them as dependencies; Golden Config uses Nornir too).

If any of those are not in place, start with Device Onboarding first — Golden Config will not have anything useful to operate on otherwise. There is no need to do anything from the 3.1 Upgrade Lab in advance — Day 1 of this pack pulls in just the first hop's commands directly.

## Packages added

| Package | Constraint | Why |
|---------|-----------|-----|
| `nautobot-golden-config` | `~2.6` | The 2.6.x line is current and requires Nautobot ≥ 2.4.20 (we will be on 2.4.33 by then). 3.x targets Nautobot 3.x. |

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
