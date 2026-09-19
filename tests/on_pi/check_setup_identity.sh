#!/bin/bash
# Verifies #130: setup.sh hostname and MQTT identity handling.
#
# Runs the real functions from bin/setup.sh in a sandbox: sudo, hostnamectl,
# hostname and systemctl are stubbed, and /etc/hosts and /etc/hostname are
# redirected to temp files. Nothing on the system is changed, so this is safe
# on the Pi and off-Pi.
#
#   tests/on_pi/check_setup_identity.sh
#
# Snippets passed to run_sandboxed are single-quoted on purpose: they expand
# inside the sandbox shell.
# shellcheck disable=SC2016
set -u

REPO=$(cd "$(dirname "$0")/../.." && pwd)
SETUP="$REPO/bin/setup.sh"
PASS=0
FAIL=0

ok() { echo "  PASS  $*"; PASS=$((PASS + 1)); }
bad() { echo "  FAIL  $*"; FAIL=$((FAIL + 1)); }
check() { # check "<description>" <command...>
    local desc="$1"; shift
    if "$@"; then ok "$desc"; else bad "$desc"; fi
}

# Extract a function definition from setup.sh by name.
extract() {
    sed -n "/^function $1\b/,/^}/p" "$SETUP"
}

# Run a snippet with the setup.sh functions loaded against a fresh sandbox.
# Usage: run_sandboxed <sandbox-dir> <snippet>
run_sandboxed() {
    local sb="$1" snippet="$2"
    local funcs
    funcs=$(for f in _backup_file resolve_hostname _env_default ensure_mqtt_identity setup_mdns_hostname; do
        extract "$f"
    done | sed -e "s#/etc/hosts#$sb/etc/hosts#g" -e "s#/etc/hostname#$sb/etc/hostname#g")
    (
        cd "$sb" || exit 99
        # shellcheck disable=SC2030
        export INSTALL_DIR="$sb" SB="$sb"
        bash -c "
            log_info() { echo \"[info] \$*\" >&2; }
            log_error() { echo \"[error] \$*\" >&2; }
            log_pass() { :; }
            log() { :; }
            sudo() { \"\$@\"; }
            hostname() { cat \"\$SB/etc/hostname\"; }
            hostnamectl() { [ \"\$1\" = set-hostname ] && echo \"\$2\" > \"\$SB/etc/hostname\"; }
            systemctl() { :; }
            ENV_CREATED=\${ENV_CREATED:-false}
            $funcs
            $snippet
        "
    )
}

new_sandbox() {
    local sb
    sb=$(mktemp -d)
    mkdir -p "$sb/etc"
    echo "raspberrypi" > "$sb/etc/hostname"
    printf '127.0.0.1\tlocalhost\n::1\t\tlocalhost ip6-localhost\n127.0.1.1\traspberrypi\n' > "$sb/etc/hosts"
    echo "$sb"
}

env_get() { sed -n "s/^$2=//p" "$1/.env" | tail -n 1; }
count_hosts_lines() { grep -c '^127\.0\.1\.1' "$1/etc/hosts"; }

echo "== resolve_hostname"
sb=$(new_sandbox)
printf 'GARDEN_HOSTNAME="gardyn-04a"\n' > "$sb/.env"
out=$(unset GARDEN_HOSTNAME; run_sandboxed "$sb" 'resolve_hostname; echo "$GARDEN_HOSTNAME"' 2>/dev/null)
check "reads GARDEN_HOSTNAME from .env (quotes stripped)" [ "$out" = "gardyn-04a" ]
out=$(GARDEN_HOSTNAME=from-shell run_sandboxed "$sb" 'resolve_hostname; echo "$GARDEN_HOSTNAME"' 2>/dev/null)
check "shell environment wins over .env" [ "$out" = "from-shell" ]
rm -f "$sb/.env"
out=$(unset GARDEN_HOSTNAME; run_sandboxed "$sb" 'resolve_hostname; echo "$GARDEN_HOSTNAME"' 2>/dev/null)
check "defaults to gardyn without .env or shell value" [ "$out" = "gardyn" ]
for badname in "-lead" "trail-" "has_underscore" "has.dot" "sp ace"; do
    GARDEN_HOSTNAME="$badname" run_sandboxed "$sb" 'resolve_hostname' >/dev/null 2>&1
    check "rejects invalid hostname '$badname'" [ $? -eq 1 ]
done
rm -rf "$sb"

echo "== ensure_mqtt_identity"
sb=$(new_sandbox)
cp "$REPO/.env-dist" "$sb/.env"
ENV_CREATED=true GARDEN_HOSTNAME=gardyn-04a run_sandboxed "$sb" 'ensure_mqtt_identity' 2>/dev/null
check "fresh .env: MQTT_IDENTIFIER derived from hostname" [ "$(env_get "$sb" MQTT_IDENTIFIER)" = "gardyn_04a" ]
check "fresh .env: MQTT_BASETOPIC derived from hostname" [ "$(env_get "$sb" MQTT_BASETOPIC)" = "gardyn_04a" ]
check "fresh .env: GARDEN_HOSTNAME recorded" [ "$(env_get "$sb" GARDEN_HOSTNAME)" = "gardyn-04a" ]
check "fresh .env: keys appear exactly once" \
    [ "$(grep -c '^MQTT_IDENTIFIER=' "$sb/.env")$(grep -c '^MQTT_BASETOPIC=' "$sb/.env")$(grep -c '^GARDEN_HOSTNAME=' "$sb/.env")" = "111" ]
rm -rf "$sb"

sb=$(new_sandbox)
printf 'MQTT_IDENTIFIER=my_tower\nMQTT_BASETOPIC=garden/one\n' > "$sb/.env"
ENV_CREATED=false GARDEN_HOSTNAME=gardyn-04a run_sandboxed "$sb" 'ensure_mqtt_identity' 2>/dev/null
check "existing .env: MQTT_IDENTIFIER kept" [ "$(env_get "$sb" MQTT_IDENTIFIER)" = "my_tower" ]
check "existing .env: MQTT_BASETOPIC kept" [ "$(env_get "$sb" MQTT_BASETOPIC)" = "garden/one" ]
before=$(md5sum < "$sb/.env")
ENV_CREATED=false GARDEN_HOSTNAME=gardyn-04a run_sandboxed "$sb" 'ensure_mqtt_identity' 2>/dev/null
check "re-running does not change .env" [ "$(md5sum < "$sb/.env")" = "$before" ]
rm -rf "$sb"

echo "== setup_mdns_hostname"
sb=$(new_sandbox)
GARDEN_HOSTNAME=gardyn-04a run_sandboxed "$sb" 'setup_mdns_hostname' 2>/dev/null
check "hostname set" [ "$(cat "$sb/etc/hostname")" = "gardyn-04a" ]
check "/etc/hostname backed up with the old name" [ "$(cat "$sb/etc/hostname.garden.bak" 2>/dev/null)" = "raspberrypi" ]
check "127.0.1.1 line replaced, not appended" [ "$(count_hosts_lines "$sb")" = "1" ]
check "127.0.1.1 points at the new name" grep -qP '^127\.0\.1\.1\tgardyn-04a$' "$sb/etc/hosts"
check "localhost lines untouched" grep -q '^127\.0\.0\.1' "$sb/etc/hosts"
GARDEN_HOSTNAME=gardyn-04a run_sandboxed "$sb" 'setup_mdns_hostname' 2>/dev/null
check "idempotent: still one 127.0.1.1 line after a second run" [ "$(count_hosts_lines "$sb")" = "1" ]
rm -rf "$sb"

sb=$(new_sandbox)
echo "gardyn-03" > "$sb/etc/hostname"
sed -i 's/raspberrypi/gardyn-03/' "$sb/etc/hosts"
GARDEN_HOSTNAME=gardyn run_sandboxed "$sb" 'setup_mdns_hostname' 2>/dev/null
check "'gardyn' is not mistaken for existing 'gardyn-03' in /etc/hosts" grep -qP '^127\.0\.1\.1\tgardyn$' "$sb/etc/hosts"
rm -rf "$sb"

sb=$(new_sandbox)
sed -i '/^127\.0\.1\.1/d' "$sb/etc/hosts"
GARDEN_HOSTNAME=gardyn-04a run_sandboxed "$sb" 'setup_mdns_hostname' 2>/dev/null
check "adds a 127.0.1.1 line when none exists" [ "$(count_hosts_lines "$sb")" = "1" ]
rm -rf "$sb"

sb=$(new_sandbox)
out=$(GARDEN_HOSTNAME=gardyn-04a run_sandboxed "$sb" 'hostnamectl() { return 1; }; setup_mdns_hostname; echo "rc=$?"' 2>&1)
check "hostnamectl failure is reported, not swallowed" bash -c "grep -q 'hostnamectl failed' <<<\"\$1\" && grep -q 'rc=1' <<<\"\$1\"" _ "$out"
rm -rf "$sb"

echo "== dry run on this checkout"
out=$(GARDEN_HOSTNAME=gardyn-04a "$SETUP" --dry-run 2>&1)
check "dry run exits 0" [ $? -eq 0 ]
check "dry-run plan names the resolved hostname" grep -q "set hostname 'gardyn-04a'" <<<"$out"

echo
echo "check_setup_identity: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
