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
      "id": "mnha_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this MNHA run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess an architecture."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose synchronization, forwarding, or failover."
        },
        {
          "label": "Migration",
          "description": "Plan migration from chassis cluster or standalone SRX."
        }
      ]
    },
    {
      "id": "mnha_release",
      "ask_when": "Node models or releases are absent.",
      "header": "Platform",
      "question": "Are every node model and Junos release known?",
      "options": [
        {
          "label": "Exact details (Recommended)",
          "description": "Apply release-specific syntax."
        },
        {
          "label": "Infer outputs",
          "description": "Infer cautiously from evidence."
        },
        {
          "label": "Unknown",
          "description": "Avoid implementation-ready configuration."
        }
      ]
    },
    {
      "id": "mnha_mode",
      "ask_when": "Forwarding mode is absent.",
      "header": "MNHA Mode",
      "question": "Which MNHA forwarding model is required?",
      "options": [
        {
          "label": "Routed mode (Recommended)",
          "description": "Use explicit routing and SRGs."
        },
        {
          "label": "Gateway mode",
          "description": "Provide default-gateway service behavior."
        },
        {
          "label": "Hybrid mode",
          "description": "Combine only for documented requirements."
        }
      ]
    },
    {
      "id": "mnha_migrate",
      "ask_when": "Starting state is unclear.",
      "header": "Migration",
      "question": "What is the starting state?",
      "options": [
        {
          "label": "New deployment (Recommended)",
          "description": "Design without legacy cluster constraints."
        },
        {
          "label": "Chassis cluster",
          "description": "Include staged migration and rollback."
        },
        {
          "label": "Existing MNHA",
          "description": "Audit or repair."
        }
      ]
    },
    {
      "id": "mnha_topo",
      "ask_when": "Inter-node topology is incomplete.",
      "header": "Topology",
      "question": "What inter-node topology exists?",
      "options": [
        {
          "label": "Symmetric links (Recommended)",
          "description": "Use matched interfaces and direct links."
        },
        {
          "label": "Asymmetric links",
          "description": "Include inter-cluster data paths."
        },
        {
          "label": "Unknown topology",
          "description": "Collect diagrams."
        }
      ]
    },
    {
      "id": "mnha_service",
      "ask_when": "Stateful service scope is absent.",
      "header": "Services",
      "question": "Which stateful services must survive failover?",
      "options": [
        {
          "label": "Firewall and NAT (Recommended)",
          "description": "Preserve core session and NAT behavior."
        },
        {
          "label": "IPsec services",
          "description": "Include tunnel ownership and rekey."
        },
        {
          "label": "Advanced services",
          "description": "Include DHCP or security services."
        }
      ]
    },
    {
      "id": "mnha_route",
      "ask_when": "Upstream failover signaling is absent.",
      "header": "Routing",
      "question": "How will upstream failover be signaled?",
      "options": [
        {
          "label": "Dynamic routing (Recommended)",
          "description": "Use supported routing and fast detection."
        },
        {
          "label": "Static or VIP",
          "description": "Use explicit tracking and ownership."
        },
        {
          "label": "Need design",
          "description": "Compare convergence models."
        }
      ]
    },
    {
      "id": "mnha_objective",
      "ask_when": "Resilience priority is absent.",
      "header": "Objectives",
      "question": "What resilience objective matters most?",
      "options": [
        {
          "label": "Stateful failover (Recommended)",
          "description": "Prioritize session continuity."
        },
        {
          "label": "Fast routing",
          "description": "Prioritize convergence."
        },
        {
          "label": "Active-active use",
          "description": "Validate placement and symmetry."
        }
      ]
    },
    {
      "id": "mnha_test",
      "ask_when": "Validation depth is absent.",
      "header": "Test Plan",
      "question": "What validation depth is required?",
      "options": [
        {
          "label": "Full failure matrix (Recommended)",
          "description": "Test node, link, service, routing, and recovery."
        },
        {
          "label": "Named failures",
          "description": "Test specified cases."
        },
        {
          "label": "One failure",
          "description": "Reproduce the reported case safely."
        }
      ]
    }
  ]
}
```
