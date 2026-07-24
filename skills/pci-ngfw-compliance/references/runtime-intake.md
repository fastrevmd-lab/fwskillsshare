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
      "id": "pci_version",
      "ask_when": "The governing PCI version is absent.",
      "header": "PCI Version",
      "question": "Which PCI DSS version should govern the assessment?",
      "options": [
        {"label": "PCI DSS 4.0.1 (Recommended)", "description": "Use PCI DSS 4.0.1."},
        {"label": "Specified version", "description": "Use a version supplied through Other."},
        {"label": "Custom overlay", "description": "Include QSA or customer interpretations."}
      ]
    },
    {
      "id": "pci_stage",
      "ask_when": "The assessment type is absent.",
      "header": "Assess Type",
      "question": "What kind of PCI assessment is this?",
      "options": [
        {"label": "Readiness review (Recommended)", "description": "Identify gaps before formal assessment."},
        {"label": "ROC support", "description": "Organize QSA evidence."},
        {"label": "SAQ support", "description": "Tailor evidence to self-assessment."}
      ]
    },
    {
      "id": "pci_scope",
      "ask_when": "The CDE boundary is unclear.",
      "header": "CDE Scope",
      "question": "How mature is the CDE boundary?",
      "options": [
        {"label": "Defined CDE (Recommended)", "description": "Use identified account-data and connected systems."},
        {"label": "Draft CDE", "description": "Validate proposed scope."},
        {"label": "Unknown CDE", "description": "Begin with data-flow discovery."}
      ]
    },
    {
      "id": "pci_segment",
      "ask_when": "Segmentation reliance is unclear.",
      "header": "Segmentation",
      "question": "Is network segmentation relied upon for scope reduction?",
      "options": [
        {"label": "Scope reduction (Recommended)", "description": "Test segmentation design and evidence."},
        {"label": "Not relied upon", "description": "Treat connected networks as in scope."},
        {"label": "Unknown", "description": "Identify evidence needed to decide."}
      ]
    },
    {
      "id": "pci_evidence",
      "ask_when": "Evidence completeness is unclear.",
      "header": "Evidence",
      "question": "What evidence is available?",
      "options": [
        {"label": "Config plus records (Recommended)", "description": "Include configuration, reviews, logs, scans, and records."},
        {"label": "Configuration only", "description": "Mark procedural gaps."},
        {"label": "Evidence request", "description": "Produce required artifacts and sampling."}
      ]
    },
    {
      "id": "pci_output",
      "ask_when": "The deliverable is absent.",
      "header": "Output",
      "question": "What deliverable is needed?",
      "options": [
        {"label": "Requirement matrix (Recommended)", "description": "Map evidence, gaps, and remediation."},
        {"label": "Segmentation report", "description": "Emphasize CDE isolation."},
        {"label": "Executive brief", "description": "Emphasize scope risk and top actions."}
      ]
    }
  ]
}
```
