# The CSRX_* environment-variable surface

No vendor release notes existed for the build this table is drawn from
(cSRX 26.2R1.7), so the variable set was derived directly from the image's
own init scripts. Treat this as **build-specific evidence, not a stable
public contract** — re-derive it (method below) for any different release
before relying on a value here.

## Genuinely env-driven (a `docker run -e` value is read and used)

| Variable | Accepted values | Default |
|---|---|---|
| `CSRX_FORWARD_MODE` | `routing`, `wire` | `routing` |
| `CSRX_SIZE` | `large` plus a full `CSRX-<N>CPU-<N>G` enum (19 total values, e.g. `CSRX-2CPU-2G` through `CSRX-32CPU-64G`) | `large` |
| `CSRX_SWG_MODE` | `yes` / `no` | `no` |
| `CSRX_PACKET_DRIVER` | `poll`, `interrupt`, `dpdk`, `virtio` | `interrupt` on small sizes, else `dpdk` |
| `CSRX_HUGEPAGES` | `yes` / anything else | `no` |
| `CSRX_USER_DATA` | `yes` / anything else | `no` |
| `CSRX_AUTO_ASSIGN_IP` | freeform, no validation seen | `no` |
| `CSRX_MGMT_PORT_REORDER` | `yes` / anything else | `no` |
| `CSRX_TCP_CKSUM_CALC` | freeform | `no` |
| `CSRX_PORT_NUM` | integer; forced to a minimum of 3 when `CSRX_FORWARD_MODE=wire` | `3` |
| `CSRX_CTRL_CPU` / `CSRX_DATA_CPU` | hex CPU mask | derived from `CSRX_SIZE` |
| `HOST_CSRX_CTRL_CPU` / `HOST_CSRX_DATA_CPU` | hex CPU mask | mirrors the above |
| `CSRX_ARP_TIMEOUT` / `CSRX_NDP_TIMEOUT` | integer (ms) | `1200000` |
| `CSRX_LICENSE_FILE` | path to a license file (typically bind-mounted in) | empty |
| `CSRX_BUILD_WITH_SIG` | freeform | empty |
| `CSRX_DPDK_VDEV` | freeform, only consulted when the packet driver is `dpdk`/unset | empty |
| `CSRX_SD_HOST` / `CSRX_SD_USER` / `CSRX_SD_DEVICE_PORT` / `CSRX_SD_DEVICE_IP` | freeform (Security Director onboarding) | empty |
| `CSRX_MGMT_MAC_ADDR` | must equal one specific hardcoded SSR MAC or is rejected with a warning | empty |
| `CSRX_SSR_MEM_THRESHOLD` | integer, only applied when `CSRX_MGMT_MAC_ADDR` matches that MAC | `24` |
| `CSRX_PKID_BINDKEY` | freeform path | `/var/db/pbk` |
| `CSRX_CRPD` | implied `enable`/`disable` | `disable` — read from the image, never exercised; see SKILL.md's cRPD section |
| `CSRX_JUNOS_CONFIG` | path to a config file; loaded with `load merge` if it exists | unset |

## Present in the image but silently hardcoded (an `-e` value is discarded)

These names look exactly like the env-driven set above — same `CSRX_`
prefix, same apparent shape — but the init script unconditionally
reassigns them to a fixed value **after** sourcing the environment and
**before** first use, so anything supplied at `docker run` time is thrown
away with no warning.

| Variable | What it's actually pinned to |
|---|---|
| `CSRX_JUNIPER_CONFIG` | `/config/juniper.conf` — **the sharpest trap in the whole surface.** Its name reads as "supply startup config"; it is not settable at all. Use `CSRX_JUNOS_CONFIG` instead, or bind-mount a file directly at `/config/juniper.conf`. |
| `CSRX_PASSWORD_CONFIG_FILE` | `/var/local/csrx_password_config_file` |
| `CSRX_PFE_DST_FILE` | `/var/platform/CSRX-L/conf/dst_pfe_capacity.conf` |
| `CSRX_PFE_DST_TMP_FILE` | `/var/platform/CSRX-L/conf/tmp.conf` |
| `CSRX_PVT_KEY_FILE` / `CSRX_PUBLIC_KEY_FILE` | `/var/etc/id_rsa[.pub]` |

`CSRX_ROOT_PASSWORD` / `CSRX_SD_PASSWORD` are a third category: present in
the image (referenced only in a defensive `unset` at the very end of the
init script, "in case passwords were set unknowingly using ENV variables")
but with no consumer found by name anywhere in the scripts inspected here.
Treat as **unconfirmed, not working** — verify directly before relying on
either to set credentials.

## How to rediscover this table for a different release

Documentation lags the image, every time — don't wait for release notes
that may not exist. The image itself is authoritative:

```bash
docker run --rm <image>:<tag> cat /etc/rc.local
```

**A flat `grep -oE 'CSRX_[A-Z_]+'` of that output alone is not sufficient**
— in the build this table is drawn from, it missed `CSRX_FORWARD_MODE`
entirely, despite that variable controlling the single most consequential
behavior (routing vs. secure-wire). The reason: `rc.local` sources one or
more helper scripts and calls a function from them (here,
`set_env_variables`, defined across `/var/local/.csrxenv` and
`/etc/rc_funcs.sh`) that does the real parsing, validation, and defaulting
— the variable names live inside that sourced function, not as literal
strings in `rc.local` itself.

The complete method:

1. `docker run --rm <image>:<tag> cat /etc/rc.local` — read it fully, and
   note every `source <path>` line.
2. `docker run --rm <image>:<tag> cat <each sourced path>` — read every one
   of them **in full**, not just grep them. Look specifically for a
   `save_env_variable`/`set_env_variable`-style helper function; that
   function body is where the accepted-values validation and the default
   value live.
3. For each name found, determine whether it is genuinely env-driven or
   silently hardcoded: read forward from the `source` line to the
   variable's first use, and check whether anything **unconditionally
   reassigns** it in between (a plain `VAR="fixed/path"`, not a
   `${VAR:=default}` conditional default) before it's consumed. If so, it's
   decorative — the name exists, the environment path into it does not.
4. Union the results of the flat grep and the full script read; the
   difference between the two is itself worth recording — it's exactly how
   `CSRX_FORWARD_MODE` was nearly missed here.

Keep this read-only and disposable throughout: override `Cmd` (e.g. with
`cat`), no `--privileged`, no network attachment, `--rm`. No cSRX process
needs to actually start to extract this information.
