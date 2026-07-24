# Runtime Intake

## When to ask

Use this catalog only after inspecting the request and evidence. Ask an entry
when its `ask_when` condition is true and the answer would materially affect
the result. Skip answered or irrelevant entries. Prioritize safety, scope,
platform or framework basis, evidence quality, then output preference.

## Tool adaptation

- Claude: send at most three entries to `AskUserQuestion`; omit `id` and set
  `multiSelect: false`.
- Codex: send at most three entries to `request_user_input`; retain `id` and
  omit `multiSelect`.
- Fallback: ask the same questions in plain text.
- Preserve free-text `Other`. Never request secrets.

## Question catalog

```json
{
  "questions": [
    {
      "id": "sd_stage",
      "ask_when": "The deployment stage is absent.",
      "header": "Stage",
      "question": "What stage is the deployment in?",
      "options": [
        {"label": "Plan or dry-run (Recommended)", "description": "Validate prerequisites and produce a plan."},
        {"label": "Fresh deployment", "description": "Prepare candidate commands."},
        {"label": "Troubleshooting", "description": "Diagnose an existing deployment."}
      ]
    },
    {
      "id": "sd_release",
      "ask_when": "The exact SD On-Prem release is absent.",
      "header": "Release",
      "question": "Which Security Director On-Prem release is being deployed?",
      "options": [
        {"label": "Verified release (Recommended)", "description": "Use the exact release and guide."},
        {"label": "Different release", "description": "Supply the release through Other."},
        {"label": "Unknown release", "description": "Identify media and documentation first."}
      ]
    },
    {
      "id": "sd_media",
      "ask_when": "Media presence or integrity is unclear.",
      "header": "Artifacts",
      "question": "Are the required release artifacts available and verified?",
      "options": [
        {"label": "Both verified (Recommended)", "description": "Disk image and bundle checksums are valid."},
        {"label": "One missing", "description": "Identify the missing artifact."},
        {"label": "Unverified", "description": "Stop and verify integrity."}
      ]
    },
    {
      "id": "sd_size",
      "ask_when": "The appliance flavor is absent.",
      "header": "Sizing",
      "question": "Which supported appliance size should be used?",
      "options": [
        {"label": "Smallest fitting (Recommended)", "description": "Select the lowest flavor meeting measured requirements."},
        {"label": "Known flavor", "description": "Use a flavor supplied through Other."},
        {"label": "Need sizing", "description": "Collect device, log, retention, and growth requirements."}
      ]
    },
    {
      "id": "sd_proxmox",
      "ask_when": "VM placement values are incomplete.",
      "header": "Proxmox",
      "question": "Are the Proxmox placement values known?",
      "options": [
        {"label": "Values ready (Recommended)", "description": "VMID, node, storage, bridge, and resources are known."},
        {"label": "Need selection", "description": "Inspect capacity read-only."},
        {"label": "Existing VM", "description": "Validate an existing VM."}
      ]
    },
    {
      "id": "sd_network",
      "ask_when": "IP, route, or internal CIDR values are incomplete.",
      "header": "Network",
      "question": "Is the complete IP and routing plan available?",
      "options": [
        {"label": "Plan ready (Recommended)", "description": "Required addresses, gateway, and internal CIDR are defined."},
        {"label": "Partial plan", "description": "Identify missing values."},
        {"label": "Need design", "description": "Produce a connectivity worksheet."}
      ]
    },
    {
      "id": "sd_services",
      "ask_when": "Supporting service reachability is unverified.",
      "header": "DNS and NTP",
      "question": "Have supporting services been validated?",
      "options": [
        {"label": "Both verified (Recommended)", "description": "DNS and NTP tests pass."},
        {"label": "Need tests", "description": "Provide safe validation commands."},
        {"label": "Not ready", "description": "Treat service readiness as a blocker."}
      ]
    },
    {
      "id": "sd_transfer",
      "ask_when": "The bundle delivery method is absent.",
      "header": "Transfer",
      "question": "How will the installer bundle reach the appliance?",
      "options": [
        {"label": "Approved HTTPS (Recommended)", "description": "Use controlled HTTPS and checksums."},
        {"label": "SCP transfer", "description": "Use approved SCP without exposing credentials."},
        {"label": "Existing method", "description": "Validate the supplied mechanism."}
      ]
    },
    {
      "id": "sd_secrets",
      "ask_when": "Secret delivery is needed for a later step.",
      "header": "Secrets",
      "question": "How will deployment secrets be supplied?",
      "options": [
        {"label": "Interactive entry (Recommended)", "description": "Enter secrets at a trusted console."},
        {"label": "Secret manager", "description": "Use an approved delivery workflow."},
        {"label": "Supply later", "description": "Use placeholders and stop before secret-dependent execution."}
      ]
    },
    {
      "id": "sd_onboard",
      "ask_when": "Post-deployment scope is absent.",
      "header": "Onboarding",
      "question": "How far should the runbook go after deployment?",
      "options": [
        {"label": "Health validation (Recommended)", "description": "Validate the platform without production onboarding."},
        {"label": "Device onboarding", "description": "Include approved device connectivity."},
        {"label": "Full operations", "description": "Include logging, licensing, backup, and monitoring."}
      ]
    }
  ]
}
```
