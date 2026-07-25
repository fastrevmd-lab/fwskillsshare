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
      "id": "cis_goal",
      "ask_when": "The requested assessment outcome is absent.",
      "header": "Goal",
      "question": "What outcome should this CIS assessment produce?",
      "options": [
        {
          "label": "Gap assessment (Recommended)",
          "description": "Identify safeguards, evidence gaps, and remediation priorities."
        },
        {
          "label": "Evidence package",
          "description": "Organize evidence for an existing assessment."
        },
        {
          "label": "Control mapping",
          "description": "Map controls without grading implementation."
        }
      ]
    },
    {
      "id": "cis_version",
      "ask_when": "The governing CIS version is absent.",
      "header": "CIS Version",
      "question": "Which CIS Controls version should govern the assessment?",
      "options": [
        {
          "label": "CIS v8.1 (Recommended)",
          "description": "Use the current v8.1 safeguard structure."
        },
        {
          "label": "CIS v8",
          "description": "Use the original v8 structure."
        },
        {
          "label": "Org profile",
          "description": "Follow a supplied organizational crosswalk."
        }
      ]
    },
    {
      "id": "cis_ig",
      "ask_when": "The Implementation Group is absent and affects safeguard scope.",
      "header": "CIS Group",
      "question": "Which Implementation Group should be assessed?",
      "options": [
        {
          "label": "IG2 (Recommended)",
          "description": "Assess IG1 and IG2 for a typical enterprise."
        },
        {
          "label": "IG1",
          "description": "Limit scope to essential cyber hygiene."
        },
        {
          "label": "IG3",
          "description": "Include all three groups."
        }
      ]
    },
    {
      "id": "cis_scope",
      "ask_when": "Device or boundary scope is absent.",
      "header": "Scope",
      "question": "What firewall scope should be included?",
      "options": [
        {
          "label": "Full estate (Recommended)",
          "description": "Assess all supplied devices and boundaries."
        },
        {
          "label": "Named boundary",
          "description": "Limit the assessment to a specified system or segment."
        },
        {
          "label": "Evidence only",
          "description": "Assess only controls directly supported by supplied evidence."
        }
      ]
    },
    {
      "id": "cis_evidence",
      "ask_when": "Evidence completeness is unclear.",
      "header": "Evidence",
      "question": "How should uncertain evidence completeness be handled?",
      "options": [
        {
          "label": "Inventory evidence (Recommended)",
          "description": "Identify configurations, logs, reviews, tickets, and operating records before grading."
        },
        {
          "label": "Assess supplied artifacts",
          "description": "Assess only supplied evidence and disclose coverage gaps."
        },
        {
          "label": "Build evidence request",
          "description": "List required evidence without grading implementation."
        }
      ]
    },
    {
      "id": "cis_output",
      "ask_when": "Deliverable emphasis is absent.",
      "header": "Output",
      "question": "What deliverable should be emphasized?",
      "options": [
        {
          "label": "Matrix and plan (Recommended)",
          "description": "Produce the safeguard matrix, gaps, and remediation plan."
        },
        {
          "label": "Evidence request",
          "description": "Emphasize missing assessment artifacts."
        },
        {
          "label": "Executive summary",
          "description": "Emphasize risk, coverage, and top actions."
        }
      ]
    }
  ]
}
```
