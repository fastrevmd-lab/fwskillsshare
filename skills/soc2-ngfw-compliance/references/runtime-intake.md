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
      "id": "soc2_type",
      "ask_when": "Engagement type is absent.",
      "header": "Report Type",
      "question": "What SOC 2 engagement is being supported?",
      "options": [
        {
          "label": "Readiness review (Recommended)",
          "description": "Identify gaps before examination."
        },
        {
          "label": "Type I",
          "description": "Assess a point in time."
        },
        {
          "label": "Type II",
          "description": "Assess operation over a period."
        }
      ]
    },
    {
      "id": "soc2_tsc",
      "ask_when": "Trust Services categories are absent.",
      "header": "TSC Scope",
      "question": "Which Trust Services Criteria categories apply?",
      "options": [
        {
          "label": "Security only (Recommended)",
          "description": "Assess the Common Criteria."
        },
        {
          "label": "Security plus A/C",
          "description": "Include availability or confidentiality."
        },
        {
          "label": "Custom scope",
          "description": "Use categories supplied through Other."
        }
      ]
    },
    {
      "id": "soc2_period",
      "ask_when": "Evidence period is absent.",
      "header": "Period",
      "question": "What evidence period should be used?",
      "options": [
        {
          "label": "Defined period (Recommended)",
          "description": "Use dated evidence for the stated period."
        },
        {
          "label": "Point in time",
          "description": "Avoid operating-period conclusions."
        },
        {
          "label": "Not established",
          "description": "Identify retention and sampling needs."
        }
      ]
    },
    {
      "id": "soc2_system",
      "ask_when": "System description or control matrix availability is unclear.",
      "header": "System Docs",
      "question": "What system-description and control-matrix evidence is available?",
      "options": [
        {
          "label": "Both available (Recommended)",
          "description": "Use both current documents."
        },
        {
          "label": "Partial documents",
          "description": "Flag missing ownership."
        },
        {
          "label": "None available",
          "description": "Produce discovery questions."
        }
      ]
    },
    {
      "id": "soc2_vendor",
      "ask_when": "Subservice organization treatment is unclear.",
      "header": "Providers",
      "question": "How are subservice organizations treated?",
      "options": [
        {
          "label": "Carve-out method (Recommended)",
          "description": "Identify complementary controls."
        },
        {
          "label": "Inclusive method",
          "description": "Include provider evidence."
        },
        {
          "label": "Unknown method",
          "description": "Flag the governance decision."
        }
      ]
    },
    {
      "id": "soc2_output",
      "ask_when": "Deliverable is absent.",
      "header": "Output",
      "question": "What deliverable should be emphasized?",
      "options": [
        {
          "label": "Control matrix (Recommended)",
          "description": "Provide criteria mapping, evidence, gaps, and remediation."
        },
        {
          "label": "Evidence request",
          "description": "Emphasize period artifacts and samples."
        },
        {
          "label": "Management brief",
          "description": "Summarize exceptions and top actions."
        }
      ]
    }
  ]
}
```
