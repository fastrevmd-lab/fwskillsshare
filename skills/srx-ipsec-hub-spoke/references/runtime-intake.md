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
      "id": "hsvpn_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this hub-and-spoke run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess a static route-based design."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose IKE, IPsec, routing, or policy."
        },
        {
          "label": "Migration",
          "description": "Plan transition from policy-based or shared-tunnel VPN."
        }
      ]
    },
    {
      "id": "hsvpn_release",
      "ask_when": "The model or release is absent and affects syntax.",
      "header": "Platform",
      "question": "Are all SRX models and Junos releases known?",
      "options": [
        {
          "label": "Exact details (Recommended)",
          "description": "Apply platform-specific syntax."
        },
        {
          "label": "Infer outputs",
          "description": "Infer cautiously from evidence."
        },
        {
          "label": "Unknown",
          "description": "Produce discovery checks."
        }
      ]
    },
    {
      "id": "hsvpn_topo",
      "ask_when": "Peer, prefix, NAT, HA, or st0 data is incomplete.",
      "header": "Topology",
      "question": "Is the complete hub-and-spoke topology available?",
      "options": [
        {
          "label": "Complete map (Recommended)",
          "description": "Use supplied peers, LANs, WANs, NAT, HA, and st0 allocation."
        },
        {
          "label": "Partial map",
          "description": "Mark unresolved selectors and routes."
        },
        {
          "label": "Need design",
          "description": "Create a topology worksheet."
        }
      ]
    },
    {
      "id": "hsvpn_traffic",
      "ask_when": "Spoke path requirements are unclear.",
      "header": "Traffic",
      "question": "How should spoke traffic be routed?",
      "options": [
        {
          "label": "Central backhaul (Recommended)",
          "description": "Route required traffic through the hub."
        },
        {
          "label": "Split or local",
          "description": "Preserve specified local paths."
        },
        {
          "label": "Compare models",
          "description": "Evaluate both."
        }
      ]
    },
    {
      "id": "hsvpn_auth",
      "ask_when": "Peer authentication is absent.",
      "header": "Auth",
      "question": "What peer authentication should be used?",
      "options": [
        {
          "label": "Certificates (Recommended)",
          "description": "Use PKI where available."
        },
        {
          "label": "Unique PSKs",
          "description": "Use distinct secrets via approved delivery."
        },
        {
          "label": "Shared lab PSK",
          "description": "Classify as lab-only."
        }
      ]
    },
    {
      "id": "hsvpn_route",
      "ask_when": "Management reachability and tunnel defaults may conflict.",
      "header": "Routing",
      "question": "Is management reachability protected from tunnel defaults?",
      "options": [
        {
          "label": "Separate route path (Recommended)",
          "description": "Keep management and peer paths independent."
        },
        {
          "label": "Competing defaults",
          "description": "Analyze recursion."
        },
        {
          "label": "Unknown state",
          "description": "Collect route evidence."
        }
      ]
    },
    {
      "id": "hsvpn_evidence",
      "ask_when": "Troubleshooting evidence is incomplete.",
      "header": "Evidence",
      "question": "What troubleshooting evidence is available?",
      "options": [
        {
          "label": "Config and SAs (Recommended)",
          "description": "Use configuration, SAs, routes, sessions, and logs."
        },
        {
          "label": "Configuration only",
          "description": "Limit runtime conclusions."
        },
        {
          "label": "Error output",
          "description": "Begin with failures and request targeted evidence."
        }
      ]
    }
  ]
}
```
