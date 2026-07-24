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
      "id": "cmmc_basis",
      "ask_when": "The governing framework or revision is absent.",
      "header": "Basis",
      "question": "Which assessment basis should be used?",
      "options": [
        {
          "label": "CMMC Level 2 (Recommended)",
          "description": "Assess CMMC Level 2 readiness."
        },
        {
          "label": "NIST 800-171",
          "description": "Map to the specified NIST revision."
        },
        {
          "label": "Contract overlay",
          "description": "Include supplied DFARS or customer requirements."
        }
      ]
    },
    {
      "id": "cmmc_stage",
      "ask_when": "Assessment stage is absent.",
      "header": "Stage",
      "question": "What is the assessment being prepared for?",
      "options": [
        {
          "label": "Readiness review (Recommended)",
          "description": "Identify gaps before formal assessment."
        },
        {
          "label": "SSP and POAM",
          "description": "Produce SSP and POA&M evidence."
        },
        {
          "label": "C3PAO support",
          "description": "Organize defensible external assessment evidence."
        }
      ]
    },
    {
      "id": "cmmc_boundary",
      "ask_when": "The CUI boundary maturity is unknown.",
      "header": "CUI Scope",
      "question": "How mature is the CUI boundary definition?",
      "options": [
        {
          "label": "Defined boundary (Recommended)",
          "description": "Use the supplied CUI enclave boundary."
        },
        {
          "label": "Draft boundary",
          "description": "Validate and flag assumptions."
        },
        {
          "label": "Unknown boundary",
          "description": "Begin with discovery and avoid completeness claims."
        }
      ]
    },
    {
      "id": "cmmc_assets",
      "ask_when": "Asset classes in scope are unclear.",
      "header": "Assets",
      "question": "Which assets should be assessed?",
      "options": [
        {
          "label": "CUI and SPA (Recommended)",
          "description": "Include CUI assets and security protection assets."
        },
        {
          "label": "Named controls",
          "description": "Limit review to specified requirements or devices."
        },
        {
          "label": "Full environment",
          "description": "Include adjacent systems that affect CUI protection."
        }
      ]
    },
    {
      "id": "cmmc_evidence",
      "ask_when": "Evidence completeness is unclear.",
      "header": "Evidence",
      "question": "What evidence is available?",
      "options": [
        {
          "label": "Config plus records (Recommended)",
          "description": "Use configurations, logs, approvals, reviews, and procedures."
        },
        {
          "label": "Configuration only",
          "description": "Assess technical state and mark practice gaps."
        },
        {
          "label": "Request list",
          "description": "Produce an evidence request without grading."
        }
      ]
    },
    {
      "id": "cmmc_output",
      "ask_when": "The deliverable is absent.",
      "header": "Output",
      "question": "Which deliverable is most useful?",
      "options": [
        {
          "label": "Assessment matrix (Recommended)",
          "description": "Provide mappings, evidence, gaps, and remediation."
        },
        {
          "label": "SSP narrative",
          "description": "Emphasize implementer-ready SSP language."
        },
        {
          "label": "POAM actions",
          "description": "Emphasize owners, milestones, and residual risk."
        }
      ]
    }
  ]
}
```
