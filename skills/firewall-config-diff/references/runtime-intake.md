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
      "id": "diff_goal",
      "ask_when": "Comparison intent is absent.",
      "header": "Goal",
      "question": "What relationship should the comparison test?",
      "options": [
        {
          "label": "Planned drift (Recommended)",
          "description": "Treat A as baseline and B as candidate."
        },
        {
          "label": "HA parity",
          "description": "Find unintended peer differences."
        },
        {
          "label": "Migration parity",
          "description": "Compare intent across vendors."
        }
      ]
    },
    {
      "id": "diff_direction",
      "ask_when": "Input roles are ambiguous.",
      "header": "Direction",
      "question": "How should the two inputs be labeled?",
      "options": [
        {
          "label": "A base, B new (Recommended)",
          "description": "Classify changes directionally."
        },
        {
          "label": "Unordered peers",
          "description": "Treat inputs equally."
        },
        {
          "label": "Custom roles",
          "description": "Use roles supplied through Other."
        }
      ]
    },
    {
      "id": "diff_scope",
      "ask_when": "Compared components are absent.",
      "header": "Scope",
      "question": "Which configuration areas should be compared?",
      "options": [
        {
          "label": "All sections (Recommended)",
          "description": "Compare every supported component."
        },
        {
          "label": "Policy and NAT",
          "description": "Focus on traffic behavior."
        },
        {
          "label": "Named sections",
          "description": "Restrict comparison through Other."
        }
      ]
    },
    {
      "id": "diff_identity",
      "ask_when": "Rename matching policy affects results.",
      "header": "Identity",
      "question": "How should renamed elements be matched?",
      "options": [
        {
          "label": "Semantic matching (Recommended)",
          "description": "Match resolved meaning before names."
        },
        {
          "label": "Stable names",
          "description": "Use names as primary identity."
        },
        {
          "label": "Strict values",
          "description": "Report every name or value difference."
        }
      ]
    },
    {
      "id": "diff_ignore",
      "ask_when": "Intentional local differences may exist.",
      "header": "Exceptions",
      "question": "Are any differences expected and approved?",
      "options": [
        {
          "label": "No allowlist (Recommended)",
          "description": "Report all material differences."
        },
        {
          "label": "Known local deltas",
          "description": "Exclude a supplied allowlist."
        },
        {
          "label": "Generated noise",
          "description": "Ignore known non-semantic ordering or metadata."
        }
      ]
    },
    {
      "id": "diff_output",
      "ask_when": "Result detail is absent.",
      "header": "Output",
      "question": "How detailed should the result be?",
      "options": [
        {
          "label": "Full diff report (Recommended)",
          "description": "Include equivalence, additions, removals, impact, and confidence."
        },
        {
          "label": "Risk summary",
          "description": "Return material differences only."
        },
        {
          "label": "Machine output",
          "description": "Emphasize structured diff data."
        }
      ]
    }
  ]
}
```
