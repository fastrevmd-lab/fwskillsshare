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
      "id": "cisco_goal",
      "ask_when": "The downstream purpose is absent and affects parsing depth.",
      "header": "Goal",
      "question": "What will the parsed result be used for?",
      "options": [
        {
          "label": "Full normalization (Recommended)",
          "description": "Populate the shared schema and all quality gates."
        },
        {
          "label": "Focused analysis",
          "description": "Parse sections relevant to the investigation."
        },
        {
          "label": "Downstream task",
          "description": "Prepare for conversion, diff, audit, or compliance."
        }
      ]
    },
    {
      "id": "cisco_platform",
      "ask_when": "ASA versus FTD cannot be established from the artifact.",
      "header": "Platform",
      "question": "Which Cisco platform produced the configuration?",
      "options": [
        {
          "label": "Auto-detect (Recommended)",
          "description": "Infer ASA versus FTD and report uncertainty."
        },
        {
          "label": "Cisco ASA",
          "description": "Apply ASA parsing assumptions."
        },
        {
          "label": "Cisco FTD",
          "description": "Account for FTD-managed gaps."
        }
      ]
    },
    {
      "id": "cisco_coverage",
      "ask_when": "Export completeness is unclear.",
      "header": "Coverage",
      "question": "How complete is the supplied configuration?",
      "options": [
        {
          "label": "Full export (Recommended)",
          "description": "Treat it as a complete running configuration."
        },
        {
          "label": "Partial excerpt",
          "description": "Mark absent sections unknown."
        },
        {
          "label": "Unsure",
          "description": "Detect likely omissions."
        }
      ]
    },
    {
      "id": "cisco_scope",
      "ask_when": "The requested normalized components are absent.",
      "header": "Scope",
      "question": "Which components should be normalized?",
      "options": [
        {
          "label": "All sections (Recommended)",
          "description": "Include all supported components."
        },
        {
          "label": "Policy and NAT",
          "description": "Focus on traffic selection."
        },
        {
          "label": "Named sections",
          "description": "Restrict parsing through Other."
        }
      ]
    },
    {
      "id": "cisco_output",
      "ask_when": "Output form is absent.",
      "header": "Output",
      "question": "What output should be returned?",
      "options": [
        {
          "label": "JSON and gates (Recommended)",
          "description": "Return normalized JSON and quality gates."
        },
        {
          "label": "Normalized JSON",
          "description": "Return the schema only."
        },
        {
          "label": "Quality report",
          "description": "Return coverage and ambiguity only."
        }
      ]
    }
  ]
}
```
