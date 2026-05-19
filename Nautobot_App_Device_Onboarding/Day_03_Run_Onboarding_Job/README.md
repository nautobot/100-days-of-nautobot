# Day 3: Run the Onboarding Job

Today is the payoff. We run Device Onboarding's job against `bos-rtr-01` first to inspect what it creates, then batch the remaining three cEOS devices.

## Look Up cEOS Container IPs

Containerlab's bridge network assigns IPs dynamically, so we look them up at run-time rather than hard-coding.

```
$ sudo containerlab inspect --topo clab/ceos-lab.clab.yml
```

Note the IPv4 address of each node. For the rest of this Day we will use `bos-rtr-01`'s address; replace with whatever yours shows.

## Find the Onboarding Job

In the Nautobot UI:

- **Jobs** → **Jobs** → filter for "onboarding".

You should see one visible job from `nautobot_device_onboarding`:

- **Sync Devices From Network** — the SSoT-based job that uses Nornir + the SecretsGroup we created on Day 2. (Class `SSOTSyncDevices` in `nautobot_device_onboarding/jobs.py`.)

> [!NOTE]
> 4.2.6 still ships the legacy `Perform Device Onboarding (Original)` job, but it is marked `hidden = True` and does not appear in the UI's job list by default. We use the SSoT-based job in this lab.

## Run the Job Against One Device

Click **Sync Devices From Network** → **Run Job Now**. The form has 16 fields; here is what to set (everything else can stay at its default):

| Field | Set to |
|-------|--------|
| **Debug** | leave unchecked |
| **Connectivity test** | leave unchecked (the job will SSH to verify regardless) |
| **CSV file** | leave empty (we use IP Addresses instead) |
| **Location** | `Boston` |
| **Namespace** | `Global` (or your install's default) |
| **IP Addresses** | the IPv4 of `bos-rtr-01` from `containerlab inspect` |
| **Port** | `22` |
| **Timeout** | `30` |
| **Set mgmt only** | leave at default (True) |
| **Update devices without primary IP** | leave at default (False) |
| **Device role** | `network` (from Day 2) |
| **Device status** | `Active` |
| **Interface status** | `Active` |
| **IP address status** | `Active` |
| **Secrets group** | `cEOS Lab Credentials` (from Day 2) |
| **Platform** | leave empty (Device Onboarding auto-detects `arista_eos`) |

Click **Run**. The job redirects to its log view; refresh until it completes.

## Inspect What Was Created

After a successful run, browse:

- **Devices** → **Devices** — `bos-rtr-01` should appear, status Active, role network, in Boston.
- The device detail page should show its **Manufacturer** (Arista), **Platform** (`arista_eos`), **Serial number** (from cEOS), and the **management interface** with its IP set as the **Primary IPv4**.

> [!IMPORTANT]
> **Sync Devices From Network only populates the management interface and primary IP.** Full interface inventory, VLANs, VRFs, and cables come from a *second* job — `Sync Network Data From Network`. Day 4 walks that step.

## Batch the Rest

Re-run the same job with all four IPs in one go. **IP Addresses** is a comma-separated `StringVar`, so you can paste:

```
<bos-acc-01-ip>, <bos-rtr-01-ip>, <nyc-acc-01-ip>, <nyc-rtr-01-ip>
```

Adjust **Location** as appropriate — if all four belong to different sites, you may need to run the job once per Location. For the Boston pair, set Location = Boston and pass both Boston IPs; repeat with New York for the NYC pair.

## What's Next

[Day 4](../Day_04_Validate_And_Wrap/README.md) — validate the populated DCIM, observe idempotency on a re-run, and close out with real-world correlation.
