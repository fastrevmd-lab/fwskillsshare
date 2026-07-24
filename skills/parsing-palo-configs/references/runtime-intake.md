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
      "id": "palo_goal",
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
      "id": "palo_format",
      "ask_when": "XML versus set format or management context is ambiguous.",
      "header": "Format",
      "question": "What type of PAN-OS configuration was supplied?",
      "options": [
        {
          "label": "Auto-detect (Recommended)",
          "description": "Detect format and management context."
        },
        {
          "label": "PAN-OS XML",
          "description": "Parse XML hierarchy."
        },
        {
          "label": "Set format",
          "description": "Parse CLI set statements."
        }
      ]
    },
    {
      "id": "palo_scope",
      "ask_when": "Panorama inheritance scope is unclear.",
      "header": "Hierarchy",
      "question": "How should Panorama or inherited configuration be handled?",
      "options": [
        {
          "label": "Resolve all (Recommended)",
          "description": "Combine applicable shared, device-group, template, and local values."
        },
        {
          "label": "Named context",
          "description": "Limit resolution through Other."
        },
        {
          "label": "Local only",
          "description": "Avoid effective inherited-policy claims."
        }
      ]
    },
    {
      "id": "palo_coverage",
      "ask_when": "Export completeness is unclear.",
      "header": "Coverage",
      "question": "How complete is the supplied configuration?",
      "options": [
        {
          "label": "Full export (Recommended)",
          "description": "Treat it as complete."
        },
        {
          "label": "Partial excerpt",
          "description": "Mark omitted hierarchy unknown."
        },
        {
          "label": "Unsure",
          "description": "Detect missing hierarchy and references."
        }
      ]
    },
    {
      "id": "palo_output",
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
          "description": "Emphasize inheritance and reference ambiguity."
        }
      ]
    }
  ]
}
```
