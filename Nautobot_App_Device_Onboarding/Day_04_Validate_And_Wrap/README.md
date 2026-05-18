# Day 4: Validate and Wrap

> 🚧 **Desk-verified, not yet live-verified.** The two-job flow (Sync Devices → Sync Network Data) reflects 4.2.6's actual behavior per `nautobot_device_onboarding/jobs.py`. Idempotency expectations still need a live-env confirmation.

The four cEOS devices are now real Devices in Nautobot, but only their management interface is populated. Today we pull in the rest (interfaces, VLANs, VRFs) with a second job, cross-check what landed, watch idempotency on a re-run, and close out.

## Populate Full Interface Data

The `Sync Devices From Network` job from Day 3 onboarded the device, its platform, and the management interface. To populate the **rest** of each device's interfaces (plus VLANs, VRFs, and cabling) we run a second job: **Sync Network Data From Network**.

In the UI:

- **Jobs** → **Jobs** → **Sync Network Data From Network** → **Run Job Now**.
- Select the four onboarded devices from the **Devices** picker (or pass them via filter).
- **Sync VLANs**, **Sync VRFs**, **Sync Cables** — leave at their defaults; for the lab the cEOS devices have all three to pick up.
- **Secrets group**: should auto-populate from each device's SecretsGroup association set during Day 3.
- Click **Run**.

After the job completes, the Device detail pages should show their full interface list (Ethernet1, Ethernet2, …) with link types, VLANs, and IPs as configured on the cEOS side.

## Cross-Check the Populated Data

Pick `bos-rtr-01`. Compare what Nautobot has against `show version` and `show interfaces` on the actual cEOS container.

```
$ ssh admin@<bos-rtr-01-ip>
ceos-01> show version
ceos-01> show interfaces
```

In the Nautobot UI, open the matching Device. Verify:

| Field | Should match |
|-------|--------------|
| Hostname | `show version` system hostname |
| Manufacturer | Arista |
| Platform | `arista_eos` |
| Serial | `show version` serial |
| Management interface | the interface you onboarded against, marked as primary |
| Other interfaces | one row per `show interfaces` entry (after running Sync Network Data) |
| Primary IPv4 | the management IP we onboarded against |

## Idempotency Re-Run

Re-run both jobs (`Sync Devices From Network`, then `Sync Network Data From Network`) with the same inputs. The job logs should show "no changes" for each device (or only diff-driven updates). Confirm in the UI that no duplicate Devices, Interfaces, or VLANs were created.

## Change Something Upstream, Re-Run

SSH into `bos-rtr-01` and change its hostname:

```
ceos-01> enable
ceos-01# config terminal
ceos-01(config)# hostname bos-rtr-01-new
```

Re-run the job for that IP. Observe in the Nautobot UI that the Device's Name updated. This is the value Device Onboarding adds in production — your Nautobot stays a faithful mirror as devices change.

## Real-World Correlation

The lab boils down a real-world onboarding flow:

- **Credentials live in Nautobot Secrets, not in code.** The same SecretsGroup pattern you set up here scales to production secrets backends (Vault, AWS Secrets Manager) — only the *provider* changes.
- **The job is idempotent.** That means it's safe to schedule (e.g. nightly) so Nautobot reflects whatever's currently on the network, even when devices change without your knowing.
- **Containerlab is a stand-in for real network gear.** Replace the cEOS IPs with your actual data-center management IPs, and the same job onboards real hardware. Nothing about the Nautobot-side workflow changes.
- **Batching scales.** Production onboarding usually feeds the IPs from a CSV, an IPAM query, or another SoT. Look at the **Bulk Onboarding** flow in the Device Onboarding docs once you outgrow the per-run form.

## Wrap-up

You have:

- Installed a real-world Nautobot App against the Scenario 1 base.
- Wired the dependency chain (Device Onboarding → SSoT → Nornir → Nautobot Secrets).
- Onboarded four lab devices into Nautobot end-to-end.
- Seen the job behave idempotently and pick up upstream changes.

The Retail-r-Us network in your Codespace is now backed by a Source of Truth that mirrors reality.

## What's Next

A future expansion pack will likely cover **Golden Config** — the next step after you have devices in Nautobot is generating, comparing, and deploying their intended configurations. Watch this repo.
