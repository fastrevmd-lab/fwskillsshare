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
      "id": "autovpn_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this AutoVPN run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess a full-tunnel design."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose tunnel, routing, or backhaul problems."
        },
        {
          "label": "Migration",
          "description": "Plan transition from static or split-tunnel VPN."
        }
      ]
    },
    {
      "id": "autovpn_release",
      "ask_when": "Model or release is absent and affects support.",
      "header": "Platform",
      "question": "Are the SRX models and Junos releases known?",
      "options": [
        {
          "label": "Exact details (Recommended)",
          "description": "Apply release-specific behavior."
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
      "id": "autovpn_traffic",
      "ask_when": "Backhaul behavior is unclear.",
      "header": "Traffic",
      "question": "What traffic model is required?",
      "options": [
        {
          "label": "Full backhaul (Recommended)",
          "description": "Send spoke traffic through the hub."
        },
        {
          "label": "Split tunnel",
          "description": "Preserve specified local paths."
        },
        {
          "label": "Compare models",
          "description": "Evaluate both designs."
        }
      ]
    },
    {
      "id": "autovpn_auth",
      "ask_when": "Peer authentication is absent.",
      "header": "Auth",
      "question": "What peer authentication model should be used?",
      "options": [
        {
          "label": "PKI zero-touch (Recommended)",
          "description": "Use certificates and scalable group identity."
        },
        {
          "label": "Unique PSKs",
          "description": "Use a distinct secret per spoke."
        },
        {
          "label": "Existing legacy",
          "description": "Assess a shared-secret design and document risk."
        }
      ]
    },
    {
      "id": "autovpn_lans",
      "ask_when": "Spoke prefix allocation is incomplete.",
      "header": "LAN Prefixes",
      "question": "How are spoke LAN prefixes allocated?",
      "options": [
        {
          "label": "Summarizable (Recommended)",
          "description": "Use non-overlapping scalable ranges."
        },
        {
          "label": "Discontiguous",
          "description": "Generate explicit handling and capacity caveats."
        },
        {
          "label": "Overlapping",
          "description": "Stop and resolve overlap."
        }
      ]
    },
    {
      "id": "autovpn_nat",
      "ask_when": "NAT between spokes and hub is unclear.",
      "header": "Underlay",
      "question": "What NAT exists between spokes and the hub?",
      "options": [
        {
          "label": "Known NAT path (Recommended)",
          "description": "Apply NAT-T to a documented path."
        },
        {
          "label": "No NAT",
          "description": "Use directly reachable peers."
        },
        {
          "label": "Unknown or double",
          "description": "Require NAT behavior tests."
        }
      ]
    },
    {
      "id": "autovpn_route",
      "ask_when": "Management and default-route separation is unclear.",
      "header": "Routing",
      "question": "How is hub management and default routing separated?",
      "options": [
        {
          "label": "Separate management (Recommended)",
          "description": "Keep management independent of tunnel defaults."
        },
        {
          "label": "Competing defaults",
          "description": "Analyze recursion."
        },
        {
          "label": "Unknown state",
          "description": "Collect routing evidence."
        }
      ]
    },
    {
      "id": "autovpn_evidence",
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
          "description": "Limit findings to static design."
        },
        {
          "label": "Error output",
          "description": "Begin with failures and collect targeted evidence."
        }
      ]
    }
  ]
}
```
