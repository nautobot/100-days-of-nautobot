# Golden Config Lab — Data Scaffold

This directory is the **single source repository** that the Golden Config expansion pack points all three of its roles at:

| Subdirectory | Role | Provided Contents flag | Populated by |
|--------------|------|------------------------|--------------|
| `templates/` | Jinja templates for intended configurations | `nautobot_golden_config.jinjatemplate` | committed to this repo |
| `backups/` | Per-device backups of `show running-config` | `nautobot_golden_config.backupconfigs` | **pre-committed for this lab** — see note below |
| `intended/` | Per-device rendered intended configs | `nautobot_golden_config.intendedconfigs` | Golden Config's **Generate Intended Configurations** job at runtime (Day 4) |

Day 2 of the pack creates one Nautobot **GitRepository** record pointing at `https://github.com/nautobot/100-days-of-nautobot.git` with all three `Provided Contents` flags ticked. Golden Config Settings then carry per-role **path templates** that resolve into the three subdirectories above.

**Why `backups/` is pre-populated rather than empty:** In a production deployment, Golden Config's **Perform Configuration Backup** job SSHes each in-scope Device, captures `show running-config`, and writes the output into the local clone of this GitRepository. This pack does **not** run that job — see the pack-level [Lab approach section](../README.md#lab-approach--no-containerlab-in-this-pack) for the resource-constraint reason. To still let Days 3 and 4 demonstrate the full Backup → Intended → Compliance pipeline against realistic data, we ship four sample running-configs in `backups/Boston/` and `backups/New_York/` that match the four mock Devices Day 1 / Day 2's seed script creates.

The `intended/` subdirectory ships empty (just a `.gitkeep`) — Day 4's **Generate Intended Configurations** job populates it locally inside the Nautobot container at runtime. No Secrets Group is attached to the GitRepository, so the local clone never pushes back upstream.

## Template layout

The Jinja path template configured on Day 2 is:

```
templates/{{ obj.platform.network_driver }}/{{ obj.role.name }}.j2
```

So a Device with Platform `arista_eos` and Role `network` (i.e. all four of our mock cEOS Devices seeded by Day 2's `seed_mock_devices.py`) renders against:

```
templates/arista_eos/network.j2
```

That is the only template we ship today. Adding more platforms or roles is just a matter of creating the matching `<network_driver>/<role>.j2` files.
