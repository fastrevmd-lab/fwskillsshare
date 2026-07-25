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
      "question": "How should missing SRX model or Junos release details be handled?",
      "options": [
        {
          "label": "Discover first (Recommended)",
          "description": "Identify exact models and releases before support conclusions."
        },
        {
          "label": "Exact details supplied",
          "description": "Apply release-specific behavior."
        },
        {
          "label": "Infer conservatively",
          "description": "Limit output to evidence-supported design and disclose uncertainty."
        }
      ]
    },
    {
      "id": "autovpn_traffic",
      "ask_when": "Backhaul behavior is unclear.",
      "header": "Traffic",
      "question": "How should an unspecified AutoVPN traffic model be resolved?",
      "options": [
        {
          "label": "Confirm model first (Recommended)",
          "description": "Confirm the traffic model before designing spoke forwarding."
        },
        {
          "label": "Use supplied full backhaul",
          "description": "Backhaul all scoped spoke traffic through the hub as supplied."
        },
        {
          "label": "Use supplied split tunnel",
          "description": "Preserve the supplied split-tunnel and local path requirements."
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
      "question": "How should incomplete spoke LAN allocation be handled?",
      "options": [
        {
          "label": "Map LANs first (Recommended)",
          "description": "Identify every spoke prefix and overlap before route design."
        },
        {
          "label": "Use supplied scalable ranges",
          "description": "Use supplied non-overlapping summarizable prefixes."
        },
        {
          "label": "Use supplied explicit prefixes",
          "description": "Handle supplied discontiguous prefixes without summarization."
        }
      ]
    },
    {
      "id": "autovpn_nat",
      "ask_when": "NAT between spokes and hub is unclear.",
      "header": "Underlay",
      "question": "How should uncertain underlay NAT be handled?",
      "options": [
        {
          "label": "Trace NAT first (Recommended)",
          "description": "Test peer reachability and translation behavior before tunnel design."
        },
        {
          "label": "Use supplied NAT path",
          "description": "Apply NAT-T to the supplied documented translation path."
        },
        {
          "label": "Use supplied no-NAT path",
          "description": "Use supplied directly reachable peer paths."
        }
      ]
    },
    {
      "id": "autovpn_route",
      "ask_when": "Management and default-route separation is unclear.",
      "header": "Routing",
      "question": "How should uncertain management-route separation be handled?",
      "options": [
        {
          "label": "Inspect routes first (Recommended)",
          "description": "Trace management, peer, and default paths before route changes."
        },
        {
          "label": "Use supplied separate path",
          "description": "Preserve a supplied independent management path."
        },
        {
          "label": "Analyze competing defaults",
          "description": "Evaluate supplied competing defaults for recursion."
        }
      ]
    },
    {
      "id": "autovpn_evidence",
      "ask_when": "Troubleshooting evidence is incomplete.",
      "header": "Evidence",
      "question": "How should incomplete troubleshooting evidence be handled?",
      "options": [
        {
          "label": "Inventory evidence (Recommended)",
          "description": "Identify available configuration, SAs, routes, sessions, and logs before diagnosis."
        },
        {
          "label": "Use supplied artifacts",
          "description": "Diagnose only from supplied artifacts and limit runtime conclusions."
        },
        {
          "label": "Approved live collection",
          "description": "Collect targeted read-only device evidence with approval."
        }
      ]
    }
  ]
}
```
