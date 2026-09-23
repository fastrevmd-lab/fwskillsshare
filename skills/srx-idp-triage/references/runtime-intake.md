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
      "id": "idpt_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this IDP triage run accomplish?",
      "options": [
        {
          "label": "Analyze and recommend (Recommended)",
          "description": "Read detections and policy state, then propose a reviewed change without committing."
        },
        {
          "label": "Analysis only",
          "description": "Report what fired and what each rule currently does, with no change proposal."
        },
        {
          "label": "Recommend and apply",
          "description": "Propose a change and, after separate explicit approval, commit it under confirmed commit."
        }
      ]
    },
    {
      "id": "idpt_evidence",
      "ask_when": "It is unclear where IDP detections should be read from.",
      "header": "Evidence",
      "question": "Where should IDP detections be read from?",
      "options": [
        {
          "label": "Discover first (Recommended)",
          "description": "Check syslog configuration for a dedicated IDP log file before choosing a source."
        },
        {
          "label": "Supplied log excerpt",
          "description": "Analyze only the log lines provided, and limit conclusions to them."
        },
        {
          "label": "Collector or SIEM",
          "description": "Use detections already exported off-box, and pull only policy state from the device."
        }
      ]
    },
    {
      "id": "idpt_log_size",
      "ask_when": "The on-box log file is too large to read in one pull.",
      "header": "Large log",
      "question": "How should an IDP log too large for one pull be handled?",
      "options": [
        {
          "label": "Archive, then read (Recommended)",
          "description": "Copy the file aside with a timestamped name and read the copy; nothing is deleted."
        },
        {
          "label": "Use off-box logs",
          "description": "Read the same detections from a collector or SIEM instead of the device."
        },
        {
          "label": "Clear after archiving",
          "description": "Archive the file, then clear it for a fresh slice; clearing needs separate approval."
        }
      ]
    },
    {
      "id": "idpt_platform",
      "ask_when": "Model, Junos release, or chassis-cluster state is absent and affects the commands used.",
      "header": "Platform",
      "question": "How should missing SRX model, release, or cluster details be handled?",
      "options": [
        {
          "label": "Discover first (Recommended)",
          "description": "Identify model, release, and cluster state read-only before any command selection."
        },
        {
          "label": "Exact details supplied",
          "description": "Apply release-specific commands and per-node checks as supplied."
        },
        {
          "label": "Assume generic behavior",
          "description": "Use common commands and flag everything release-dependent."
        }
      ]
    },
    {
      "id": "idpt_action",
      "ask_when": "Enforcement is proposed and no action has been validated for this traffic.",
      "header": "Action",
      "question": "Which enforcement action should the proposal use?",
      "options": [
        {
          "label": "Validated in this environment (Recommended)",
          "description": "Use only an action already confirmed by before-and-after log evidence here."
        },
        {
          "label": "Stage and test",
          "description": "Propose a candidate action, then prove it with test traffic before calling it done."
        },
        {
          "label": "Keep monitoring",
          "description": "Leave rules in no-action and report the detections only."
        }
      ]
    }
  ]
}
```
