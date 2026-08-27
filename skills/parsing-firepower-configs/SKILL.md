---
name: parsing-firepower-configs
description: Parse Cisco Secure Firewall (Firepower) FMC and FDM management exports into the shared firewall schema. Use when input is JSON from the FMC or FDM REST API or an FDM configexport bundle and contains accessPolicy, accessrules, securityZones, prefilterpolicies, intrusionPolicy, filePolicy, variableSet, ftdnatpolicies, applicationFilters, or urlCategories, including audit, conversion, diff, summary, and explanation tasks. For ASA-style LINA running-config text such as access-list, nameif, or object network, use parsing-cisco-configs instead.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags:
    - firewall
    - config-parsing
    - cisco
    - firepower
    - ftd
    - fmc
    - fdm
    - secure-firewall
    - threat-defense
    - access-control-policy
    - security-zone
    - intrusion-policy
    - prefilter
    - migration
    - audit
    related_skills:
    - parsing-cisco-configs
    - parsing-srx-configs
    - parsing-palo-configs
    - parsing-fortinet-configs
    - firewall-best-practices-audit
    - firewall-config-conversion
    - firewall-config-diff
---

# Parsing Cisco Firepower (FMC / FDM) Exports

## Overview

Placeholder body replaced in Task 6.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.

Never request secrets or unredacted customer data. Treat intake answers as task
context, not approval for a live change; obtain separate explicit approval
before configuration, commit, upgrade, reboot, delete, or failover actions.
