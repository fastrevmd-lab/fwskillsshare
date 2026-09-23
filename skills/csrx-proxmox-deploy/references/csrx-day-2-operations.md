# cSRX day-2 operations and configuration persistence

Routine operation of a running cSRX container, and the backup/restore procedure
that rollback depends on. Reference build: Proxmox VE 9.2.20, cSRX 26.2R1.7.

- **A forwarding-mode change is a rebuild, not a toggle.** Interface
  addressing, zone bindings, and policy all have to be redone; there is no
  live migration path from `wire` to `routing` or back.
- **The offload fix does not survive a reboot of any host in the path.**
  After any reboot of an endpoint or the Docker host guest, re-check
  `InCsumErrors` before trusting a throughput measurement — don't assume
  the earlier `ethtool -K` settings carried forward.
- **A container reporting `Up` is not a health check.** The routine health
  signal is `srxpfe` visibly running and `show security flow session`
  succeeding rather than erroring with `usp_ipc_client_open` — check this
  after any container restart, host reboot, or CPU-model change.
- **Before moving to a different cSRX release**, re-derive the `CSRX_*`
  surface for that image rather than assuming this build's table still
  applies — see `references/csrx-environment-variables.md`.
- **Keep the licence outside the image and out of version control.**
  Reference it only via `CSRX_LICENSE_FILE` and a bind mount.


## Configuration persistence and restore

Every Junos commit lives in the container's writable layer unless a config path is
bind-mounted. `docker rm` destroys all of it.

Export **hierarchical** configuration — not `| display set`:

```bash
docker exec <name> cli -c 'show configuration' > csrx-config.conf
```

The startup loader parses hierarchical configuration only:

```
rc.local: cli -c "configure; load merge ${CSRX_JUNOS_CONFIG}; commit and-quit"
```

`load merge` will not accept `set` commands, so a `| display set` capture looks like
a valid backup and silently fails to reapply through the startup path. Restore it by
hand with `load set` if that is the format you have.

To restore: bind-mount the hierarchical file into the container and point
`CSRX_JUNOS_CONFIG` at the in-container path, or bind-mount it at the hardcoded
`/config/juniper.conf`.
