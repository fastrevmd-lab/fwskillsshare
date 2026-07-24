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
      "id": "hipaa_role",
      "ask_when": "HIPAA organizational role is absent.",
      "header": "Org Role",
      "question": "What HIPAA role applies to the assessed organization?",
      "options": [
        {
          "label": "Covered entity (Recommended)",
          "description": "Assess from the covered-entity perspective."
        },
        {
          "label": "Business associate",
          "description": "Include business-associate responsibilities."
        },
        {
          "label": "Both or unsure",
          "description": "Evaluate both roles and flag ownership."
        }
      ]
    },
    {
      "id": "hipaa_goal",
      "ask_when": "Review purpose is absent.",
      "header": "Goal",
      "question": "What is the purpose of this HIPAA review?",
      "options": [
        {
          "label": "Risk assessment (Recommended)",
          "description": "Identify ePHI risks and remediation."
        },
        {
          "label": "Audit evidence",
          "description": "Organize audit artifacts."
        },
        {
          "label": "Design review",
          "description": "Review architecture without operational claims."
        }
      ]
    },
    {
      "id": "hipaa_scope",
      "ask_when": "The ePHI boundary is unclear.",
      "header": "ePHI Scope",
      "question": "How well defined is the ePHI environment?",
      "options": [
        {
          "label": "Defined scope (Recommended)",
          "description": "Use identified systems, flows, users, and parties."
        },
        {
          "label": "Draft scope",
          "description": "Validate a preliminary boundary."
        },
        {
          "label": "Unknown scope",
          "description": "Begin discovery and avoid completeness claims."
        }
      ]
    },
    {
      "id": "hipaa_vendor",
      "ask_when": "Third-party ePHI paths are unclear.",
      "header": "Vendors",
      "question": "How should third-party ePHI paths be handled?",
      "options": [
        {
          "label": "Include all paths (Recommended)",
          "description": "Assess vendors, remote access, cloud, and transmission."
        },
        {
          "label": "Named vendors",
          "description": "Limit review to identified parties."
        },
        {
          "label": "Technical only",
          "description": "Exclude contract conclusions and note BAA needs."
        }
      ]
    },
    {
      "id": "hipaa_evidence",
      "ask_when": "Evidence period is unclear.",
      "header": "Evidence",
      "question": "What evidence period is available?",
      "options": [
        {
          "label": "Config plus records (Recommended)",
          "description": "Use current configuration and dated evidence."
        },
        {
          "label": "Current state only",
          "description": "Avoid period-of-operation claims."
        },
        {
          "label": "Evidence request",
          "description": "Produce a targeted collection list."
        }
      ]
    },
    {
      "id": "hipaa_output",
      "ask_when": "Report emphasis is absent.",
      "header": "Output",
      "question": "What should the report emphasize?",
      "options": [
        {
          "label": "Safeguard matrix (Recommended)",
          "description": "Map evidence, gaps, risk, and remediation."
        },
        {
          "label": "Risk register",
          "description": "Emphasize likelihood, impact, owners, and treatment."
        },
        {
          "label": "Executive brief",
          "description": "Summarize exposure and top actions."
        }
      ]
    }
  ]
}
```
