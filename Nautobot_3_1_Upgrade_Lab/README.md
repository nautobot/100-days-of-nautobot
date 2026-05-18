# Nautobot 3.1 Upgrade Lab

A two-day walkthrough for upgrading an existing Nautobot 2.x environment to [Nautobot 3.1.2](https://demo.nautobot.com/) in-place.

The lab boots [Lab Scenario 1](../Lab_Setup/scenario_1_setup/README.md) (Nautobot 2.3.2 via `nautobot-docker-compose`) and walks the version chain to 3.1.2. When you want to see what 3.1.2 looks like, open [demo.nautobot.com](https://demo.nautobot.com/) in another tab. [next.demo.nautobot.com](https://next.demo.nautobot.com/) tracks the 3.2 preview.

| Day | Topic |
|-----|-------|
| 1 | [Upgrade](Day_01_Upgrade/README.md) — pre-flight, then three image-tag hops: 2.3.2 → 2.4.33 → 3.0.latest → 3.1.2 |
| 2 | [What's Different in 3.1](Day_02_What_Is_Different_in_3_1/README.md) — reference notes for replaying Days 1–100 on the upgraded environment |

Reference docs:

- [Upgrading from Nautobot v2](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/upgrading/from-v2/)
- [Nautobot 3.1 release notes — upgrade actions](https://docs.nautobot.com/projects/core/en/stable/release-notes/version-3.1/#upgrade-actions)
