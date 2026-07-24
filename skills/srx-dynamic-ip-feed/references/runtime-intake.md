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
      "id": "dif_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this dynamic-feed run accomplish?",
      "options": [
        {
          "label": "Design or review (Recommended)",
          "description": "Produce or assess a safe integration."
        },
        {
          "label": "Troubleshoot",
          "description": "Diagnose download, parsing, mapping, or policy behavior."
        },
        {
          "label": "Migration",
          "description": "Convert an existing feed workflow."
        }
      ]
    },
    {
      "id": "dif_release",
      "ask_when": "Model or release is absent and affects capability.",
      "header": "Platform",
      "question": "Are the SRX model and Junos release known?",
      "options": [
        {
          "label": "Exact details (Recommended)",
          "description": "Apply release-specific capabilities."
        },
        {
          "label": "Infer outputs",
          "description": "Infer cautiously from evidence."
        },
        {
          "label": "Unknown",
          "description": "Produce prerequisite checks."
        }
      ]
    },
    {
      "id": "dif_source",
      "ask_when": "Feed artifacts or publishing design is incomplete.",
      "header": "Feed Source",
      "question": "What feed artifacts are available?",
      "options": [
        {
          "label": "URL and archive (Recommended)",
          "description": "Use documented URLs and archive layout."
        },
        {
          "label": "Existing failing feed",
          "description": "Diagnose the supplied implementation."
        },
        {
          "label": "Need feed design",
          "description": "Define structure and publishing first."
        }
      ]
    },
    {
      "id": "dif_tls",
      "ask_when": "Publisher trust method is absent.",
      "header": "TLS",
      "question": "How should the HTTPS publisher be authenticated?",
      "options": [
        {
          "label": "Trusted CA (Recommended)",
          "description": "Validate an approved CA chain."
        },
        {
          "label": "Private CA",
          "description": "Include controlled CA import and rotation."
        },
        {
          "label": "Lab unverified",
          "description": "Classify bypass as non-production."
        }
      ]
    },
    {
      "id": "dif_auth",
      "ask_when": "Application authentication is required but unspecified.",
      "header": "Feed Auth",
      "question": "What application authentication is required?",
      "options": [
        {
          "label": "No extra auth (Recommended)",
          "description": "Rely on authenticated TLS and network controls."
        },
        {
          "label": "Mutual TLS",
          "description": "Use client certificates via approved secret delivery."
        },
        {
          "label": "Basic auth",
          "description": "Protect credentials outside chat."
        }
      ]
    },
    {
      "id": "dif_route",
      "ask_when": "Feed-server routing context is absent.",
      "header": "Routing",
      "question": "Which routing context reaches the feed server?",
      "options": [
        {
          "label": "Default instance (Recommended)",
          "description": "Use default routing after reachability validation."
        },
        {
          "label": "Named instance",
          "description": "Use the specified instance and source."
        },
        {
          "label": "Unknown",
          "description": "Collect route, DNS, and connection evidence."
        }
      ]
    },
    {
      "id": "dif_effect",
      "ask_when": "Feed enforcement intent is absent.",
      "header": "Policy Use",
      "question": "How will feed entries affect security policy?",
      "options": [
        {
          "label": "Blocklist deny (Recommended)",
          "description": "Deny new matching sessions with logging."
        },
        {
          "label": "Allowlist permit",
          "description": "Permit members within constrained policy."
        },
        {
          "label": "Both uses",
          "description": "Define separate objects and precedence."
        }
      ]
    },
    {
      "id": "dif_session",
      "ask_when": "Existing-session behavior matters and is absent.",
      "header": "Sessions",
      "question": "What should happen to existing sessions when the feed changes?",
      "options": [
        {
          "label": "New sessions only (Recommended)",
          "description": "Apply changes to new evaluations."
        },
        {
          "label": "Clear matches",
          "description": "Include separately approved targeted clearing."
        },
        {
          "label": "Need decision",
          "description": "Explain enforcement timing first."
        }
      ]
    },
    {
      "id": "dif_poll",
      "ask_when": "Refresh requirements are absent.",
      "header": "Polling",
      "question": "What refresh behavior is required?",
      "options": [
        {
          "label": "Standard interval (Recommended)",
          "description": "Use a conservative supported interval."
        },
        {
          "label": "Faster updates",
          "description": "Validate load and reliability."
        },
        {
          "label": "Custom cadence",
          "description": "Use a value supplied through Other."
        }
      ]
    }
  ]
}
```
