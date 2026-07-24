# Runtime Intake

## When to ask

Use this catalog only after inspecting the request and evidence. Ask an entry
when its `ask_when` condition is true and the answer would materially affect
the result. Skip answered or irrelevant entries. Prioritize safety, scope,
platform or framework basis, evidence quality, then output preference.

## Tool adaptation

- Claude: select at most three neutral entries, project each to only `question`,
  `header`, and `options`, then add `multiSelect: false`; do not send `id` or
  `ask_when`.
- Codex: select at most three neutral entries and project each to only `id`,
  `header`, `question`, and `options`; do not send `ask_when` or `multiSelect`.
- Fallback: ask the same questions in concise plain text with a free-text
  `Other` path.
- Never request secrets.

## Question catalog

```json
{
  "questions": [
    {
      "id": "advpn_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this ADVPN run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess a read-only architecture and candidate configuration."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose shortcut or forwarding problems."
        },
        {
          "label": "Migration",
          "description": "Plan transition from static or hub-only IPsec."
        }
      ]
    },
    {
      "id": "advpn_release",
      "ask_when": "Model or release is absent and affects support.",
      "header": "Platform",
      "question": "Are the SRX models and Junos releases known?",
      "options": [
        {
          "label": "Exact details (Recommended)",
          "description": "Apply model- and release-specific limits."
        },
        {
          "label": "Infer outputs",
          "description": "Infer cautiously from supplied evidence."
        },
        {
          "label": "Unknown",
          "description": "Produce discovery checks first."
        }
      ]
    },
    {
      "id": "advpn_topo",
      "ask_when": "Site, addressing, NAT, or HA topology is incomplete.",
      "header": "Topology",
      "question": "Is the hub, spoke, addressing, and NAT topology complete?",
      "options": [
        {
          "label": "Complete map (Recommended)",
          "description": "Use supplied sites, addresses, LANs, NAT, and HA roles."
        },
        {
          "label": "Partial map",
          "description": "Mark unresolved elements."
        },
        {
          "label": "Need design",
          "description": "Build a topology worksheet."
        }
      ]
    },
    {
      "id": "advpn_auth",
      "ask_when": "Peer authentication is absent.",
      "header": "Auth",
      "question": "What authentication design is available?",
      "options": [
        {
          "label": "PKI available (Recommended)",
          "description": "Use certificate authentication."
        },
        {
          "label": "PKI planned",
          "description": "Include enrollment prerequisites."
        },
        {
          "label": "PSK only",
          "description": "Report ADVPN limitations."
        }
      ]
    },
    {
      "id": "advpn_route",
      "ask_when": "Overlay routing is absent.",
      "header": "Routing",
      "question": "Which overlay routing model should be used?",
      "options": [
        {
          "label": "OSPF P2MP (Recommended)",
          "description": "Use the documented point-to-multipoint model."
        },
        {
          "label": "Existing routing",
          "description": "Preserve and assess the supplied protocol."
        },
        {
          "label": "Need design",
          "description": "Compare supported models."
        }
      ]
    },
    {
      "id": "advpn_traffic",
      "ask_when": "Branch path requirements are unclear.",
      "header": "Traffic",
      "question": "What branch traffic behavior is required?",
      "options": [
        {
          "label": "Shortcuts plus hub (Recommended)",
          "description": "Support hub paths and spoke shortcuts."
        },
        {
          "label": "Shortcuts only",
          "description": "Focus on spoke-to-spoke formation."
        },
        {
          "label": "Central backhaul",
          "description": "Re-evaluate AutoVPN fit."
        }
      ]
    },
    {
      "id": "advpn_gateway",
      "ask_when": "Release-specific gateway form is unresolved.",
      "header": "Gateway",
      "question": "How should release-specific gateway limitations be handled?",
      "options": [
        {
          "label": "Conservative static (Recommended)",
          "description": "Use the documented safe form."
        },
        {
          "label": "Dynamic gateway",
          "description": "Use only with confirmed support."
        },
        {
          "label": "Validate first",
          "description": "Run read-only checks before selecting syntax."
        }
      ]
    },
    {
      "id": "advpn_evidence",
      "ask_when": "Troubleshooting evidence is incomplete.",
      "header": "Evidence",
      "question": "What troubleshooting evidence is available?",
      "options": [
        {
          "label": "Config and SAs (Recommended)",
          "description": "Use redacted configuration, SAs, routes, and flow evidence."
        },
        {
          "label": "Configuration only",
          "description": "Limit runtime conclusions."
        },
        {
          "label": "Error output",
          "description": "Begin with errors and request targeted evidence."
        }
      ]
    }
  ]
}
```
