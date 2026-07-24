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
      "id": "forti_goal",
      "ask_when": "The downstream purpose is absent and affects parsing depth.",
      "header": "Goal",
      "question": "What will the parsed result be used for?",
      "options": [
        {
          "label": "Full normalization (Recommended)",
          "description": "Populate the schema and quality gates."
        },
        {
          "label": "Focused analysis",
          "description": "Parse relevant sections only."
        },
        {
          "label": "Downstream task",
          "description": "Prepare for conversion, diff, audit, or compliance."
        }
      ]
    },
    {
      "id": "forti_coverage",
      "ask_when": "Export completeness is unclear.",
      "header": "Coverage",
      "question": "How complete is the FortiGate export?",
      "options": [
        {
          "label": "Full backup (Recommended)",
          "description": "Treat it as a full configuration."
        },
        {
          "label": "Partial excerpt",
          "description": "Mark omitted tables and defaults unknown."
        },
        {
          "label": "Unsure",
          "description": "Detect likely omissions."
        }
      ]
    },
    {
      "id": "forti_vdom",
      "ask_when": "Included VDOMs are unclear.",
      "header": "VDOM Scope",
      "question": "Which VDOM scope should be included?",
      "options": [
        {
          "label": "All detected (Recommended)",
          "description": "Parse global state and every VDOM."
        },
        {
          "label": "Named VDOMs",
          "description": "Limit parsing through Other."
        },
        {
          "label": "Global only",
          "description": "Exclude VDOM policy."
        }
      ]
    },
    {
      "id": "forti_scope",
      "ask_when": "Included configuration tables are absent.",
      "header": "Sections",
      "question": "Which configuration areas should be normalized?",
      "options": [
        {
          "label": "All sections (Recommended)",
          "description": "Include all supported components."
        },
        {
          "label": "Policy and NAT",
          "description": "Focus on policy and translation."
        },
        {
          "label": "Named sections",
          "description": "Restrict parsing through Other."
        }
      ]
    },
    {
      "id": "forti_output",
      "ask_when": "Output form is absent.",
      "header": "Output",
      "question": "What output should be returned?",
      "options": [
        {
          "label": "JSON and gates (Recommended)",
          "description": "Return normalized JSON and quality results."
        },
        {
          "label": "Normalized JSON",
          "description": "Return the schema only."
        },
        {
          "label": "Quality report",
          "description": "Emphasize unresolved references and defaults."
        }
      ]
    }
  ]
}
```
