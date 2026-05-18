# Day 2: Pre-Onboarding Data

> 🚧 **Desk-verified, not yet live-verified.** Containerlab topology paths and SecretsGroup pairings were confirmed against the repo and `nautobot-plugin-nornir` source. Steps still need a dry-run in a live Scenario 1 + Containerlab Codespace.

Device Onboarding does not invent your data model — it populates an existing one. Today we set up the scaffolding the onboarding job expects: **Locations**, **Statuses**, **Roles**, and a **SecretsGroup** carrying the cEOS `admin` / `admin` credentials.

We also spin up the Containerlab cEOS topology, since Day 3 will point the job at those devices.

## Bring up Containerlab

If the cEOS topology is not already running, follow the Containerlab section of [Lab Setup Scenario 1](../../Lab_Setup/scenario_1_setup/README.md). The topology gives you four devices:

| Hostname | Role hint | Location |
|----------|-----------|----------|
| `bos-acc-01` | access switch | Boston |
| `bos-rtr-01` | router | Boston |
| `nyc-acc-01` | access switch | New York |
| `nyc-rtr-01` | router | New York |

Confirm they are up and grab their management IPs (we will need them on Day 3):

```
$ sudo containerlab inspect --topo clab/ceos-lab.clab.yml
```

The output table includes an **IPv4 Address** column — those are the addresses you will paste into the onboarding job on Day 3.

## Create Locations

In the Nautobot UI under **Organization → Locations**, create two locations (or reuse what you set up during earlier 100 Days work):

- **Boston** — use whatever Location Type Scenario 1's seed data already defines (typically `Site` or `Building` from the Retail-r-Us preamble). Match the existing type so the onboarding job's location dropdown finds them.
- **New York** — same Location Type as Boston.

## Create a Role and Status

If your Scenario 1 install does not already have these:

- **Role:** `network` (matches Device Onboarding's `default_device_role`)
- **Status:** `Active` (Nautobot 2.3 ships this by default; just confirm it exists)

## Create a SecretsGroup for cEOS Credentials

Device Onboarding's Sync Data from Network job uses Nornir, and our Nornir credentials adapter (set on Day 1) reads from Nautobot Secrets.

1. **Secrets** → **Secrets** → **Add**:
   - Username Secret: name `cEOS Username`, provider Environment Variable, parameter `NAUTOBOT_DEVICE_USERNAME`.
   - Password Secret: name `cEOS Password`, provider Environment Variable, parameter `NAUTOBOT_DEVICE_PASSWORD`.

2. **Secrets** → **Secrets Groups** → **Add**:
   - Name: `cEOS Lab Credentials`.
   - Add two associations: one for **Generic / Username** pointing at `cEOS Username`, one for **Generic / Password** pointing at `cEOS Password`.

3. Set the env vars on the Nautobot container side. Edit `nautobot-docker-compose/environments/creds.env` and append:

   ```
   NAUTOBOT_DEVICE_USERNAME=admin
   NAUTOBOT_DEVICE_PASSWORD=admin
   ```

   (Both `environments/creds.env` and `environments/local.env` are loaded into the Nautobot, celery_worker, and celery_beat containers per `environments/docker-compose.base.yml`. Credentials by convention go in `creds.env`.)

4. Restart Nautobot so the env vars are picked up:

   ```
   $ invoke stop && invoke debug
   ```

## Day 2 Recap

| What | State after Day 2 |
|------|-------------------|
| Containerlab cEOS topology | running; 4 device IPs known |
| Locations | Boston, New York |
| Status | Active confirmed |
| Role | network created |
| SecretsGroup | `cEOS Lab Credentials` wired to env vars |

## What's Next

[Day 3](../Day_03_Run_Onboarding_Job/README.md) — run the **Perform Device Onboarding** job against `bos-rtr-01` first, then batch the remaining three.
