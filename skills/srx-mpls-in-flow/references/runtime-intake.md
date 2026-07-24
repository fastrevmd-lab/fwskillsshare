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
      "id": "mpls_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this MPLS-in-flow run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess a secure MPLS design."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose label, VRF, routing, or policy failures."
        },
        {
          "label": "Migration",
          "description": "Plan conversion to flow mode."
        }
      ]
    },
    {
      "id": "mpls_release",
      "ask_when": "The model or release is absent.",
      "header": "Platform",
      "question": "Are the SRX model and Junos release known?",
      "options": [
        {
          "label": "Exact supported (Recommended)",
          "description": "Verify minimum supported release."
        },
        {
          "label": "Infer outputs",
          "description": "Infer cautiously from evidence."
        },
        {
          "label": "Unknown",
          "description": "Treat support as a blocker."
        }
      ]
    },
    {
      "id": "mpls_role",
      "ask_when": "PE, CPE, or transit role is unclear.",
      "header": "Device Role",
      "question": "What role does the SRX perform?",
      "options": [
        {
          "label": "Secure PE or CPE (Recommended)",
          "description": "Apply security at the VPN edge."
        },
        {
          "label": "Transit P role",
          "description": "Re-evaluate requested security function."
        },
        {
          "label": "Existing mixed role",
          "description": "Document current responsibilities."
        }
      ]
    },
    {
      "id": "mpls_family",
      "ask_when": "The required address families are absent.",
      "header": "IP Family",
      "question": "Which address families are required?",
      "options": [
        {
          "label": "IPv4 and VPNv4 (Recommended)",
          "description": "Design the common IPv4 L3VPN case."
        },
        {
          "label": "Dual stack",
          "description": "Include IPv6 and VPNv6."
        },
        {
          "label": "IPv6 focused",
          "description": "Limit design to IPv6."
        }
      ]
    },
    {
      "id": "mpls_signal",
      "ask_when": "Label signaling is absent.",
      "header": "Signaling",
      "question": "Which label and transport protocols are used?",
      "options": [
        {
          "label": "Existing protocols (Recommended)",
          "description": "Preserve documented LDP, RSVP, or BGP label design."
        },
        {
          "label": "LDP design",
          "description": "Build an LDP transport."
        },
        {
          "label": "Need selection",
          "description": "Compare supported options."
        }
      ]
    },
    {
      "id": "mpls_vrf",
      "ask_when": "The VRF or route-target inventory is incomplete.",
      "header": "VRF Scope",
      "question": "Is the VRF and route-target inventory complete?",
      "options": [
        {
          "label": "Complete inventory (Recommended)",
          "description": "Use supplied VRFs, RDs, RTs, interfaces, and prefixes."
        },
        {
          "label": "Partial inventory",
          "description": "Mark import/export unresolved."
        },
        {
          "label": "Need design",
          "description": "Create a service matrix."
        }
      ]
    },
    {
      "id": "mpls_policy",
      "ask_when": "The VRF-aware policy model is absent.",
      "header": "Policy Model",
      "question": "How should security policy be organized?",
      "options": [
        {
          "label": "VRF policy groups (Recommended)",
          "description": "Use the scalable supported model."
        },
        {
          "label": "VRF to zone",
          "description": "Preserve existing zone design where supported."
        },
        {
          "label": "Need validation",
          "description": "Select after release checks."
        }
      ]
    },
    {
      "id": "mpls_service",
      "ask_when": "Inspection services are absent.",
      "header": "Services",
      "question": "Which security services must apply to MPLS traffic?",
      "options": [
        {
          "label": "Base policy (Recommended)",
          "description": "Start with stateful policy and logging."
        },
        {
          "label": "NAT or App-ID",
          "description": "Include explicitly required controls."
        },
        {
          "label": "Full inspection",
          "description": "Include IPS or advanced services with capacity validation."
        }
      ]
    }
  ]
}
```
