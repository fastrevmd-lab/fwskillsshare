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
      "question": "How should an uncertain CUI boundary be handled?",
      "options": [
        {
          "label": "Map boundary first (Recommended)",
          "description": "Identify CUI assets, flows, and protection dependencies before assessing."
        },
        {
          "label": "Assess supplied boundary",
          "description": "Use a supplied final boundary and disclose unverified assumptions."
        },
        {
          "label": "Validate supplied draft",
          "description": "Test a supplied draft and mark unresolved scope."
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
      "question": "How should uncertain evidence completeness be handled?",
      "options": [
        {
          "label": "Inventory evidence (Recommended)",
          "description": "Identify configurations, logs, approvals, reviews, and procedures before grading."
        },
        {
          "label": "Assess supplied artifacts",
          "description": "Assess only supplied evidence and disclose practice gaps."
        },
        {
          "label": "Build evidence request",
          "description": "List required evidence without grading implementation."
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
