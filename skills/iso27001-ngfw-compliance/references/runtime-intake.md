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
      "id": "iso_goal",
      "ask_when": "Engagement type is absent.",
      "header": "Audit Goal",
      "question": "What kind of ISO 27001 activity is this?",
      "options": [
        {
          "label": "Internal readiness (Recommended)",
          "description": "Identify evidence and operation gaps."
        },
        {
          "label": "Certification audit",
          "description": "Prepare certification or surveillance evidence."
        },
        {
          "label": "Corrective action",
          "description": "Focus on known findings."
        }
      ]
    },
    {
      "id": "iso_scope",
      "ask_when": "The ISMS boundary is unclear.",
      "header": "ISMS Scope",
      "question": "Is the ISMS scope defined?",
      "options": [
        {
          "label": "Defined scope (Recommended)",
          "description": "Use supplied organizational and system boundaries."
        },
        {
          "label": "Draft scope",
          "description": "Validate assumptions."
        },
        {
          "label": "Unknown scope",
          "description": "Begin discovery and avoid conformity claims."
        }
      ]
    },
    {
      "id": "iso_soa",
      "ask_when": "Statement of Applicability evidence is absent.",
      "header": "SoA",
      "question": "What Statement of Applicability evidence is available?",
      "options": [
        {
          "label": "Current SoA (Recommended)",
          "description": "Use organizational applicability decisions."
        },
        {
          "label": "Partial SoA",
          "description": "Flag missing applicability evidence."
        },
        {
          "label": "No SoA",
          "description": "Use generic mapping without organizational claims."
        }
      ]
    },
    {
      "id": "iso_basis",
      "ask_when": "Control applicability basis is unclear.",
      "header": "Basis",
      "question": "Which control basis should drive conclusions?",
      "options": [
        {
          "label": "Org risk plan (Recommended)",
          "description": "Follow the SoA and risk treatment plan."
        },
        {
          "label": "Annex A only",
          "description": "Map against ISO 27001 Annex A."
        },
        {
          "label": "Custom overlay",
          "description": "Include supplied ISO 27002 or customer mappings."
        }
      ]
    },
    {
      "id": "iso_period",
      "ask_when": "Operating evidence period is unclear.",
      "header": "Evidence",
      "question": "What operating evidence is available?",
      "options": [
        {
          "label": "Dated samples (Recommended)",
          "description": "Use records covering the assessment period."
        },
        {
          "label": "Current state only",
          "description": "Avoid effectiveness claims."
        },
        {
          "label": "Design only",
          "description": "Assess intended control design."
        }
      ]
    },
    {
      "id": "iso_output",
      "ask_when": "Deliverable is absent.",
      "header": "Output",
      "question": "What deliverable is needed?",
      "options": [
        {
          "label": "Control matrix (Recommended)",
          "description": "Provide mapping, evidence, gaps, and actions."
        },
        {
          "label": "Audit evidence",
          "description": "Emphasize traceable artifacts."
        },
        {
          "label": "Risk treatment",
          "description": "Emphasize treatment and residual risk."
        }
      ]
    }
  ]
}
```
