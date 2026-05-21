# Nautobot Golden Config App — Expansion Pack

A four-day walkthrough for installing and using [`nautobot-app-golden-config`](https://github.com/nautobot/nautobot-app-golden-config) on a fresh Scenario 1 baseline. By the end of Day 4 you will have running-config backups stored in Git, intended configurations rendered from Jinja templates with Nautobot data, and a per-feature compliance dashboard diffing the two — against four mock cEOS Devices we seed into Nautobot on Day 2.

The pack runs on **Nautobot 2.4.33 / Python 3.12** — Golden Config's current 2.x line (2.6.x) requires Nautobot ≥ 2.4.20, so Day 1 starts by upgrading the stack from Scenario 1's 2.3.2 / Python 3.10 baseline. The upgrade is one hop (the same Hop 1 the [3.1 Upgrade Lab Day 1](../Nautobot_3_1_Upgrade_Lab/Day_01_Upgrade/README.md#hop-1-232--2433-also-python-38--312) walks).

## Prerequisites

This pack is **self-contained** — you do not need to do any other expansion pack first. You only need:

- A fresh Codespace launched from this repository.
- The `nautobot-docker-compose` stack on the **Scenario 1 baseline**: Python 3.10 / Nautobot 2.3.2 with the Scenario 1 starter SQL dump imported and the UI serving on `:8080`. (Day 1 of this pack upgrades you to Python 3.12 / Nautobot 2.4.33.)

If you have already completed the [Device Onboarding pack](../Nautobot_App_1_Device_Onboarding/README.md), you also have this baseline plus four real cEOS Devices in Nautobot. That is fine; this pack does not interfere with that data. But this pack does **not require** Device Onboarding and does **not run jobs against the cEOS containers** — see the **Lab approach** section below for why.

## Lab approach — no Containerlab in this pack

Early drafts of this pack relied on the four Containerlab cEOS containers Device Onboarding deploys. Across multiple verification attempts on different Codespace SKUs we got **uneven results** — sometimes all four cEOS containers came up and Golden Config's Backup Job ran clean; sometimes only part of the topology came up; sometimes Containerlab's `postdeploy` stalled and the lab needed a fresh Codespace to recover. The combined footprint of four cEOS instances plus the Golden-Config-fattened Nautobot stack just sits too close to the resource ceiling of typical Codespace SKUs to ship as a required step.

Rather than gate the whole pack on a beefier machine SKU, this pack teaches Golden Config **entirely through Nautobot's data model and Git-stored configs**, with no SSH ever leaving the Nautobot container:

| Resource | Real-network version | This pack |
|----------|----------------------|-----------|
| Devices in Nautobot | DO pack onboards them from the cEOS containers | Day 2 seeds four **mock** Devices via a script that hits the Nautobot REST API |
| Backup running-configs | GC's **Backup Configurations** job SSHes each device and writes the output | Day 3 walks through **pre-committed sample running-configs** in the pack's `golden-config-data/backups/` scaffold. The job is shown but never executed. |
| Intended configs | GC's **Generate Intended Configurations** job renders Jinja templates with Nautobot data | Day 4 runs the **real** job — it does not need SSH, just Nautobot data + the templates |
| Compliance | GC's **Perform Configuration Compliance** job compares backup vs. intended | Day 4 runs the **real** job — both inputs are Git-stored content, no SSH |

So Days 1, 4, and most of Day 2 use the real Golden Config jobs against the real Nautobot data and Git content. Only Day 3's **Backup** job is shown without being run (it would need SSH-reachable devices). For the rest of the workflow, mock devices and pre-committed backups give you the same data flow a real-network lab would have.

**Want to verify Golden Config end-to-end against actual cEOS devices?** Do the [Device Onboarding pack](../Nautobot_App_1_Device_Onboarding/README.md) **first** on a 16+ GB Codespace SKU, then come back to this pack and replace Day 2's seed-script step with the live onboarded inventory. Everything else in the pack works the same.

## Packages added

| Package | Constraint | Why |
|---------|-----------|-----|
| `nautobot-golden-config` | `~2.6` | The 2.6.x line is current and requires Nautobot ≥ 2.4.20 (we will be on 2.4.33 by then). 3.x targets Nautobot 3.x. |

Day 1 adds this via `poetry add` so it lands in `pyproject.toml` + `poetry.lock` and gets baked into the image by `invoke build`. `nautobot-plugin-nornir` is pulled in as a transitive dependency (Golden Config uses Nornir internally for the Backup job, even though we will not run that job here).

## The four Days

| Day | Topic |
|-----|-------|
| 1 | [Install Golden Config](Day_01_Install/README.md) — upgrade Nautobot 2.3.2 → 2.4.33, `poetry add` Golden Config, wire `PLUGINS` + `PLUGINS_CONFIG`, run migrations, verify the **Apps → Golden Configuration** menu appears |
| 2 | [Seed mock devices, wire templates + settings](Day_02_Templates_And_Settings/README.md) — run the seed script to populate four mock cEOS Devices, create the templates GitRepository, scope a DynamicGroup, configure Golden Config Settings |
| 3 | [Backup running configurations (explain-only)](Day_03_Backup_Configurations/README.md) — what the **Backup Configurations** job does in production, walk through pre-committed sample configs as the "would have been produced" output |
| 4 | [Intended configurations and compliance](Day_04_Intended_And_Compliance/README.md) — run the real **Generate Intended Configurations** job, run the real **Perform Configuration Compliance** job, walk the per-feature dashboard, drift demo |

## Reference

- [`nautobot-app-golden-config` README](https://github.com/nautobot/nautobot-app-golden-config)
- [Golden Config user docs](https://docs.nautobot.com/projects/golden-config/en/latest/)
- [Network to Code: Golden Configuration use case overview](https://blog.networktocode.com/post/golden-configuration-network-to-code/)
