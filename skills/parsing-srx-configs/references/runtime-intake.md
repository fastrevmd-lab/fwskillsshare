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
      "id": "srxp_goal",
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
      "id": "srxp_format",
      "ask_when": "Display-set versus hierarchical syntax is ambiguous.",
      "header": "Format",
      "question": "Which Junos configuration format was supplied?",
      "options": [
        {
          "label": "Auto-detect (Recommended)",
          "description": "Detect the syntax form."
        },
        {
          "label": "Display set",
          "description": "Parse line-oriented set commands."
        },
        {
          "label": "Hierarchical",
          "description": "Parse brace-delimited configuration."
        }
      ]
    },
    {
      "id": "srxp_scope",
      "ask_when": "Logical-system scope is unclear.",
      "header": "Context",
      "question": "Which Junos contexts should be included?",
      "options": [
        {
          "label": "All detected (Recommended)",
          "description": "Parse main and detected logical contexts."
        },
        {
          "label": "Named context",
          "description": "Limit parsing through Other."
        },
        {
          "label": "Main only",
          "description": "Ignore logical systems."
        }
      ]
    },
    {
      "id": "srxp_coverage",
      "ask_when": "Export completeness is unclear.",
      "header": "Coverage",
      "question": "How complete is the supplied configuration?",
      "options": [
        {
          "label": "Full config (Recommended)",
          "description": "Treat it as complete."
        },
        {
          "label": "Partial excerpt",
          "description": "Mark missing groups and policy unknown."
        },
        {
          "label": "Unsure",
          "description": "Detect unresolved inheritance."
        }
      ]
    },
    {
      "id": "srxp_output",
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
          "description": "Emphasize groups, references, and unsupported syntax."
        }
      ]
    }
  ]
}
```
