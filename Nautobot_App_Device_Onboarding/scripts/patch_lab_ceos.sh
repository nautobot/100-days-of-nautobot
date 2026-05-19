#!/usr/bin/env bash
# Re-applies the runtime patches needed for the Device Onboarding lesson
# against the Scenario 1 Containerlab cEOS topology.
#
# Run this once after every `invoke debug` (the patches live in the running
# containers' filesystem / network state, so they are lost when containers
# are recreated). Safe to run multiple times — each step is idempotent.
#
# Usage:
#   bash Nautobot_App_Device_Onboarding/scripts/patch_lab_ceos.sh

set -euo pipefail

WORKER=nautobot-docker-compose-celery_worker-1
NAUTOBOT=nautobot-docker-compose-nautobot-1
BEAT=nautobot-docker-compose-celery_beat-1

echo "==> Bridging Nautobot stack containers onto the default Containerlab network..."
for c in "$WORKER" "$NAUTOBOT" "$BEAT"; do
    if docker network inspect bridge --format '{{json .Containers}}' | grep -q "\"Name\":\"$c\""; then
        echo "    $c already on bridge — skipping"
    else
        docker network connect bridge "$c"
        echo "    attached $c to bridge"
    fi
done

echo
echo "==> Patching arista_eos_show_version TextFSM template for cEOS extra lines..."
docker exec -u 0 -i "$WORKER" python <<'PYEOF'
import ntc_templates, os
path = os.path.dirname(ntc_templates.__file__) + '/templates/arista_eos_show_version.textfsm'
text = open(path).read()
if 'cEOS' not in text:
    new_rules = (
        '  ^cEOS\\s+tools\\s+version:.*\n'
        '  ^Kernel\\s+version:.*\n'
        '  ^. -> Error'
    )
    text = text.replace('  ^. -> Error', new_rules)
    open(path, 'w').write(text)
    print('    TextFSM template PATCHED')
else:
    print('    TextFSM template already patched')
PYEOF

echo
echo "==> Patching nautobot_device_onboarding arista_eos.yml mapper (malformed hostname entry)..."
docker exec -u 0 -i "$WORKER" python <<'PYEOF'
import nautobot_device_onboarding, os
path = os.path.dirname(nautobot_device_onboarding.__file__) + '/command_mappers/arista_eos.yml'
text = open(path).read()
# The shipping YAML has 'commands:' followed by 'command:' directly (a dict),
# instead of '- command:' (a list item). Fix the hostname entry only.
broken = '  hostname:\n    commands:\n      command: "show hostname"\n      parser: "textfsm"\n      jpath: "[*].hostname"'
fixed  = '  hostname:\n    commands:\n      - command: "show hostname"\n        parser: "textfsm"\n        jpath: "[*].hostname"'
if broken in text:
    text = text.replace(broken, fixed)
    open(path, 'w').write(text)
    print('    arista_eos.yml hostname mapper PATCHED')
elif fixed in text:
    print('    arista_eos.yml hostname mapper already patched')
else:
    print('    arista_eos.yml hostname mapper: pattern not found (upstream may have fixed it)')
PYEOF

echo
echo "==> Done. Lab should now be ready for Day 3's Sync Devices From Network job."
