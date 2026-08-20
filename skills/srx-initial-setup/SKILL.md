---
name: srx-initial-setup
description: Bring a new or factory-reset Juniper SRX from its shipped state to a reachable, zoned, screened, and minimally policied device. Use when performing first-time setup or Day-0 and Day-1 bring-up on SRX300 or SRX400 Branch, SRX1600 or SRX4120 campus, or SRX4300, SRX4700, or SRX5000 datacenter platforms, when removing or adopting factory-default configuration, when establishing management access, NTP, DNS, and system services, when creating interfaces, zones, and host-inbound-traffic, when applying starter screens, or when reading which licensed feature sets are entitled, configured, and active. Not for chassis-cluster formation, ZTP, Junos upgrades, or full policy design.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, initial-setup, day-zero, day-one, bring-up, factory-default, zeroize, management-plane, zones, host-inbound-traffic, screens, ids-option, commit-confirmed, rollback, entitlement, branch-srx]
    related_skills: [srx-policy, srx-nat, srx-syslog-logging, srx-license-signature-maintenance, srx-chassis-cluster-proxmox, srx-mnha, parsing-srx-configs]
---

# SRX first-time setup

## Overview

Placeholder body replaced in Task 15. Core model references: `references/entry-state-assessment.md`, `references/gap-model.md`, `references/factory-default-branch.md`.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.
Never request secrets or unredacted customer data. Treat intake answers as task context, not approval for a live change; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover actions.
