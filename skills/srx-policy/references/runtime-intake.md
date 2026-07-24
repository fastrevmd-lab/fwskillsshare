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
      "id": "policy_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this policy run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess security-policy intent."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose lookup, session, or application failures."
        },
        {
          "label": "Migration",
          "description": "Convert from another platform."
        }
      ]
    },
    {
      "id": "policy_release",
      "ask_when": "The model, release, or licensing is absent and affects features.",
      "header": "Platform",
      "question": "Are the SRX model, Junos release, and licenses known?",
      "options": [
        {
          "label": "Exact details (Recommended)",
          "description": "Apply supported policy and services."
        },
        {
          "label": "Read-only check",
          "description": "Determine capabilities from approved evidence."
        },
        {
          "label": "Unknown",
          "description": "Mark feature conclusions unresolved."
        }
      ]
    },
    {
      "id": "policy_model",
      "ask_when": "The architecture is absent.",
      "header": "Policy Model",
      "question": "Which policy architecture should be used?",
      "options": [
        {
          "label": "Global policy (Recommended)",
          "description": "Use global policy where it safely reduces duplication."
        },
        {
          "label": "Preserve zone-pair",
          "description": "Retain explicit zone organization."
        },
        {
          "label": "Review existing",
          "description": "Assess the supplied mix first."
        }
      ]
    },
    {
      "id": "policy_flow",
      "ask_when": "The traffic intent is incomplete.",
      "header": "Traffic",
      "question": "How complete are the traffic requirements?",
      "options": [
        {
          "label": "Complete intent (Recommended)",
          "description": "Use source, destination, application, service, zones, and purpose."
        },
        {
          "label": "Partial intent",
          "description": "Produce discovery gaps."
        },
        {
          "label": "Migration source",
          "description": "Derive intent from normalized source policy."
        }
      ]
    },
    {
      "id": "policy_nat",
      "ask_when": "NAT involvement is unclear.",
      "header": "NAT Context",
      "question": "Is NAT involved in the policy flow?",
      "options": [
        {
          "label": "No NAT (Recommended)",
          "description": "Evaluate original addresses and routing."
        },
        {
          "label": "NAT involved",
          "description": "Model the correct pre/post-NAT tuple."
        },
        {
          "label": "Unknown",
          "description": "Build a packet-flow trace."
        }
      ]
    },
    {
      "id": "policy_service",
      "ask_when": "Inspection services are absent.",
      "header": "Services",
      "question": "Which inspection services are required?",
      "options": [
        {
          "label": "Base policy (Recommended)",
          "description": "Start with least privilege and logging."
        },
        {
          "label": "App-ID or AppFW",
          "description": "Include application enforcement."
        },
        {
          "label": "Advanced security",
          "description": "Include licensed UTM, NGFW, ATP, or IPS."
        }
      ]
    },
    {
      "id": "policy_ip",
      "ask_when": "Address-family scope is absent.",
      "header": "IP Family",
      "question": "Which traffic families must be covered?",
      "options": [
        {
          "label": "IPv4 and IPv6 (Recommended)",
          "description": "Evaluate controls for both."
        },
        {
          "label": "IPv4 only",
          "description": "Report IPv6 exposure."
        },
        {
          "label": "Special traffic",
          "description": "Include multicast, discovery, or control-plane needs."
        }
      ]
    },
    {
      "id": "policy_session",
      "ask_when": "Existing-session behavior matters and is absent.",
      "header": "Sessions",
      "question": "How should existing sessions be treated after a policy change?",
      "options": [
        {
          "label": "New sessions only (Recommended)",
          "description": "Validate newly established sessions."
        },
        {
          "label": "Existing sessions matter",
          "description": "Include separately approved targeted handling."
        },
        {
          "label": "Maintenance window",
          "description": "Build verification and rollback around the change."
        }
      ]
    }
  ]
}
```
