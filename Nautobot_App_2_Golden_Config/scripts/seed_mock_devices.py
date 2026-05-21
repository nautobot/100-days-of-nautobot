#!/usr/bin/env python3
"""
Seed four mock cEOS Devices for the Golden Config expansion pack.

Creates the minimum Nautobot data the pack needs:

- LocationType "Site", with content type dcim.device
- Locations "Boston" and "New York"
- Role "network"
- Manufacturer "Arista"
- Platform "arista_eos" (network_driver "arista_eos")
- DeviceType "cEOS Lab" (Arista)
- Devices: bos-acc-01, bos-rtr-01 in Boston; nyc-acc-01, nyc-rtr-01 in New York

These are mock Devices — no Primary IPv4, no Interfaces. This pack does
not run the Golden Config Backup job (which would require SSH-reachable
devices). Day 3 inspects pre-committed sample running-configs; Day 4's
Intended and Compliance jobs operate against those configs plus Nautobot
data.

Usage from the codespace shell:

    $ pip install pynautobot
    $ NAUTOBOT_TOKEN=<your-admin-api-token> \
      python Nautobot_App_2_Golden_Config/scripts/seed_mock_devices.py

NAUTOBOT_TOKEN must be set to your admin user's actual API token (grab it
from the Nautobot UI: top-right user dropdown -> Profile -> API Tokens ->
Add). The Lab Scenario 1 baseline has NAUTOBOT_CREATE_SUPERUSER=false in
creds.env, so the example NAUTOBOT_SUPERUSER_API_TOKEN value the env file
ships with is NOT written into the database; the script defaults to that
value only as a sentinel that fails fast with 403 if you forget to
override.

NAUTOBOT_URL defaults to http://localhost:8080 (correct for a fresh
Codespace from this repo's Lab Scenario 1 config). Override only if your
Nautobot is reachable at a different URL.

Idempotent - safe to re-run.
"""

import os
import sys

try:
    import pynautobot
except ImportError:
    sys.stderr.write(
        "pynautobot is required. Install it with `pip install pynautobot`, then re-run.\n"
    )
    sys.exit(1)


NAUTOBOT_URL = os.environ.get("NAUTOBOT_URL", "http://localhost:8080")
NAUTOBOT_TOKEN = os.environ.get(
    "NAUTOBOT_TOKEN",
    "0123456789abcdef0123456789abcdef01234567",
)


def ensure(endpoint, lookup, payload):
    """Get-or-create helper.

    Looks up an object via ``endpoint.get(**lookup)``. If present, returns
    it untouched. Otherwise creates it with ``endpoint.create(**payload)``.
    """
    existing = endpoint.get(**lookup)
    label = next(iter(lookup.values()))
    if existing is not None:
        print(f"  - {label}: already present, leaving as-is")
        return existing
    created = endpoint.create(**payload)
    print(f"  - {label}: CREATED")
    return created


def main():
    nb = pynautobot.api(url=NAUTOBOT_URL, token=NAUTOBOT_TOKEN)
    nb.http_session.verify = False

    status_active = nb.extras.statuses.get(name="Active")
    if status_active is None:
        sys.exit(
            "Status 'Active' not found in Nautobot — Scenario 1 baseline not loaded?"
        )

    print("LocationType + Locations:")
    loc_type_site = ensure(
        nb.dcim.location_types,
        {"name": "Site"},
        {"name": "Site", "content_types": ["dcim.device"]},
    )
    bos = ensure(
        nb.dcim.locations,
        {"name": "Boston"},
        {
            "name": "Boston",
            "location_type": loc_type_site.id,
            "status": status_active.id,
        },
    )
    nyc = ensure(
        nb.dcim.locations,
        {"name": "New York"},
        {
            "name": "New York",
            "location_type": loc_type_site.id,
            "status": status_active.id,
        },
    )

    print("\nRole + Manufacturer + Platform + DeviceType:")
    role_network = ensure(
        nb.extras.roles,
        {"name": "network"},
        {"name": "network", "content_types": ["dcim.device"]},
    )
    mfr_arista = ensure(
        nb.dcim.manufacturers,
        {"name": "Arista"},
        {"name": "Arista"},
    )
    plat_arista_eos = ensure(
        nb.dcim.platforms,
        {"name": "arista_eos"},
        {
            "name": "arista_eos",
            "network_driver": "arista_eos",
            "manufacturer": mfr_arista.id,
        },
    )
    dtype_ceos = ensure(
        nb.dcim.device_types,
        {"model": "cEOS Lab"},
        {"model": "cEOS Lab", "manufacturer": mfr_arista.id},
    )

    print("\nDevices:")
    location_by_city = {"Boston": bos.id, "New York": nyc.id}
    devices = [
        ("bos-acc-01", "Boston"),
        ("bos-rtr-01", "Boston"),
        ("nyc-acc-01", "New York"),
        ("nyc-rtr-01", "New York"),
    ]
    for name, city in devices:
        ensure(
            nb.dcim.devices,
            {"name": name},
            {
                "name": name,
                "location": location_by_city[city],
                "role": role_network.id,
                "device_type": dtype_ceos.id,
                "platform": plat_arista_eos.id,
                "status": status_active.id,
            },
        )

    print(
        "\nDone. Visit /dcim/devices/ in the Nautobot UI to confirm — "
        "should see all four mock devices listed."
    )


if __name__ == "__main__":
    main()
