# Golden Config Lab — Data Scaffold

This directory is the **single source repository** that the Golden Config expansion pack points all three of its roles at:

| Subdirectory | Role | Provided Contents flag | Populated by |
|--------------|------|------------------------|--------------|
| `templates/` | Jinja templates for intended configurations | `nautobot_golden_config.jinjatemplate` | committed to this repo (today) |
| `backups/` | Per-device backups of `show running-config` | `nautobot_golden_config.backupconfigs` | Golden Config's **Perform Configuration Backup** job at runtime (Day 3) |
| `intended/` | Per-device rendered intended configs | `nautobot_golden_config.intendedconfigs` | Golden Config's **Generate Intended Configurations** job at runtime (Day 4) |

Day 2 of the pack creates one Nautobot **GitRepository** record pointing at `https://github.com/nautobot/100-days-of-nautobot.git` with all three `Provided Contents` flags ticked. Golden Config Settings then carry per-role **path templates** that resolve into the three subdirectories above.

The `backups/` and `intended/` subdirectories ship empty (just a `.gitkeep`) — they get populated locally inside the Nautobot container when the corresponding jobs run, **without** pushing back upstream (no Secrets Group attached to the GitRepository, so it operates read-only against this remote and writes only to its local clone).

## Template layout

The Jinja path template configured on Day 2 is:

```
templates/{{ obj.platform.network_driver }}/{{ obj.role.name }}.j2
```

So a Device with Platform `arista_eos` and Role `network` (i.e. all four of our cEOS devices, after Device Onboarding) renders against:

```
templates/arista_eos/network.j2
```

That is the only template we ship today. Adding more platforms or roles is just a matter of creating the matching `<network_driver>/<role>.j2` files.
