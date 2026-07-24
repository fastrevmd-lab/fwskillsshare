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
      "id": "nat_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this NAT run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess a NAT design."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose translation, routing, proxy, or session failures."
        },
        {
          "label": "Migration",
          "description": "Convert NAT behavior from another platform."
        }
      ]
    },
    {
      "id": "nat_release",
      "ask_when": "The model or release is absent and affects feature support.",
      "header": "Platform",
      "question": "Are the SRX model and Junos release known?",
      "options": [
        {
          "label": "Exact details (Recommended)",
          "description": "Apply supported features and syntax."
        },
        {
          "label": "Infer outputs",
          "description": "Infer cautiously from evidence."
        },
        {
          "label": "Unknown",
          "description": "Avoid release-dependent claims."
        }
      ]
    },
    {
      "id": "nat_family",
      "ask_when": "The translation family is absent.",
      "header": "NAT Type",
      "question": "Which NAT behavior is required?",
      "options": [
        {
          "label": "Source NAT (Recommended)",
          "description": "Design outbound or inter-zone source translation."
        },
        {
          "label": "Destination or static",
          "description": "Design inbound or bidirectional mapping."
        },
        {
          "label": "Advanced NAT",
          "description": "Cover NAT64, CGN, persistent NAT, or hairpinning."
        }
      ]
    },
    {
      "id": "nat_tuple",
      "ask_when": "The pre- or post-translation tuple is incomplete.",
      "header": "Traffic",
      "question": "Is the pre- and post-translation traffic tuple complete?",
      "options": [
        {
          "label": "Complete tuple (Recommended)",
          "description": "Use source, destination, service, zones, and translated values."
        },
        {
          "label": "Partial tuple",
          "description": "Mark unresolved fields."
        },
        {
          "label": "Need discovery",
          "description": "Build a flow worksheet."
        }
      ]
    },
    {
      "id": "nat_context",
      "ask_when": "Zone, interface, or routing-instance classification is unclear.",
      "header": "Context",
      "question": "How is traffic classified?",
      "options": [
        {
          "label": "Zones and interfaces (Recommended)",
          "description": "Use explicit ingress and egress."
        },
        {
          "label": "Routing instances",
          "description": "Include tenant-aware translation."
        },
        {
          "label": "Both contexts",
          "description": "Model all classification inputs."
        }
      ]
    },
    {
      "id": "nat_reach",
      "ask_when": "Translated-address reachability is unclear.",
      "header": "Reachability",
      "question": "How will translated addresses be reachable?",
      "options": [
        {
          "label": "Routed prefix (Recommended)",
          "description": "Use explicit routing."
        },
        {
          "label": "Proxy ARP or NDP",
          "description": "Include neighbor-proxy behavior."
        },
        {
          "label": "Unknown",
          "description": "Validate routing and adjacency."
        }
      ]
    },
    {
      "id": "nat_return",
      "ask_when": "Traffic symmetry is unclear.",
      "header": "Return Path",
      "question": "Does return traffic traverse the same SRX?",
      "options": [
        {
          "label": "Symmetric return (Recommended)",
          "description": "Preserve stateful return through the translator."
        },
        {
          "label": "Asymmetric return",
          "description": "Redesign or validate session risk."
        },
        {
          "label": "Unknown path",
          "description": "Collect routing and flow evidence."
        }
      ]
    },
    {
      "id": "nat_evidence",
      "ask_when": "Troubleshooting evidence is incomplete.",
      "header": "Evidence",
      "question": "What troubleshooting evidence is available?",
      "options": [
        {
          "label": "Config and sessions (Recommended)",
          "description": "Use NAT config, routes, counters, sessions, and logs."
        },
        {
          "label": "Configuration only",
          "description": "Limit conclusions to static logic."
        },
        {
          "label": "Error or trace",
          "description": "Begin with observed failure evidence."
        }
      ]
    }
  ]
}
```
