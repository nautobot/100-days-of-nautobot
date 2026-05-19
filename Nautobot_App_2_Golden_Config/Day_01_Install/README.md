# Day 1: Install Golden Config

> 📝 **Draft stub.** Day 1's full walkthrough lands in the next commit. Skeleton sections below mirror the structure of Device Onboarding Day 1 (install via `poetry add` + `invoke build`, wire `PLUGINS` / `PLUGINS_CONFIG`, `invoke post-upgrade`, verify in the UI).

## Step 1 — Add `nautobot-golden-config` as a Poetry dependency

(Coming next: the `poetry add 'nautobot-golden-config@^2'` line, why `^2`, and any transitive deps.)

## Step 2 — Wire into `nautobot_config.py`

(Coming next: the `PLUGINS` list addition and the `PLUGINS_CONFIG["nautobot_golden_config"]` block.)

## Step 3 — Rebuild the image

(Coming next: `invoke stop` + `invoke build`, with the same volume / Codespace caveats from Device Onboarding Day 1.)

## Step 4 — Start the stack and re-apply lab patches

(Coming next: `invoke debug`, then re-run [`patch_lab_ceos.sh`](../../Nautobot_App_1_Device_Onboarding/scripts/patch_lab_ceos.sh) since `invoke stop` recycles containers.)

## Step 5 — Apply migrations

(Coming next: `invoke post-upgrade`, expected output excerpt.)

## Step 6 — UI tour

(Coming next: quick walk of **Apps → Golden Config** — Settings, Backups, Intended, Compliance menus.)
