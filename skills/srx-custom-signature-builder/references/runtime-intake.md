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
      "id": "csig_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this signature run produce?",
      "options": [
        {
          "label": "Design and validate offline (Recommended)",
          "description": "Check existing coverage, draft the signature and rule, and validate syntax without activating."
        },
        {
          "label": "Coverage check only",
          "description": "Decide whether a predefined signature already covers the finding, and stop."
        },
        {
          "label": "Stage in monitor mode",
          "description": "After separate explicit approval, commit the signature under confirmed commit with no-action."
        }
      ]
    },
    {
      "id": "csig_finding",
      "ask_when": "The finding lacks a concrete request, payload, or response sample.",
      "header": "Finding",
      "question": "What evidence of the finding is available?",
      "options": [
        {
          "label": "Sanitized sample (Recommended)",
          "description": "A redacted request, payload, or response that shows the bytes to match."
        },
        {
          "label": "Scanner result only",
          "description": "A scanner or pentest finding name; the pattern must be derived and marked unproven."
        },
        {
          "label": "Packet capture",
          "description": "A sanitized capture reviewed locally, never pushed through the device transport."
        }
      ]
    },
    {
      "id": "csig_scope",
      "ask_when": "Where the signature will be enforced is unstated.",
      "header": "Scope",
      "question": "Where should the signature apply?",
      "options": [
        {
          "label": "One lab host (Recommended)",
          "description": "Scope the rule by destination address to a single lab or test target."
        },
        {
          "label": "Named production hosts",
          "description": "Scope to specific hosts and require a false-positive review before enforcement."
        },
        {
          "label": "Device-wide",
          "description": "Apply broadly; stays in monitor mode until a false-positive review is complete."
        }
      ]
    },
    {
      "id": "csig_platform",
      "ask_when": "Model, Junos release, or IDP package version is absent and affects valid syntax.",
      "header": "Platform",
      "question": "How should missing SRX model, release, or IDP package details be handled?",
      "options": [
        {
          "label": "Discover first (Recommended)",
          "description": "Read model, release, and security-package version before drafting syntax."
        },
        {
          "label": "Exact details supplied",
          "description": "Draft against the supplied release and package version."
        },
        {
          "label": "Assume generic behavior",
          "description": "Draft common syntax and flag every release-dependent statement."
        }
      ]
    }
  ]
}
```
