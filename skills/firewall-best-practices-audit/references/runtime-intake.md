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
      "id": "audit_goal",
      "ask_when": "The audit purpose is absent.",
      "header": "Goal",
      "question": "What is the primary reason for this firewall audit?",
      "options": [
        {
          "label": "Baseline hygiene (Recommended)",
          "description": "Review the complete rulebase against general practices."
        },
        {
          "label": "Pre-change review",
          "description": "Focus on planned-change risk."
        },
        {
          "label": "Incident focus",
          "description": "Prioritize a suspected attack path."
        }
      ]
    },
    {
      "id": "audit_scope",
      "ask_when": "The included components or boundaries are unclear.",
      "header": "Scope",
      "question": "What should the audit cover?",
      "options": [
        {
          "label": "Full device (Recommended)",
          "description": "Include policy, NAT, objects, zones, routing context, and logging."
        },
        {
          "label": "Rulebase only",
          "description": "Limit analysis to security-policy hygiene."
        },
        {
          "label": "Named boundary",
          "description": "Limit analysis to specified contexts."
        }
      ]
    },
    {
      "id": "audit_evidence",
      "ask_when": "The operational evidence availability is unclear.",
      "header": "Evidence",
      "question": "What evidence can support the audit?",
      "options": [
        {
          "label": "Config and telemetry (Recommended)",
          "description": "Combine configuration with hit counts, logs, and state."
        },
        {
          "label": "Configuration only",
          "description": "Perform static analysis and label telemetry dependencies."
        },
        {
          "label": "Live read-only",
          "description": "Collect approved read-only device evidence."
        }
      ]
    },
    {
      "id": "audit_context",
      "ask_when": "The business criticality and trust context are absent.",
      "header": "Context",
      "question": "How should business and trust context be established?",
      "options": [
        {
          "label": "Provide key context (Recommended)",
          "description": "Use identified assets, trust levels, and required flows."
        },
        {
          "label": "Infer cautiously",
          "description": "Label inferred boundaries."
        },
        {
          "label": "Generic severity",
          "description": "Avoid environment-specific impact claims."
        }
      ]
    },
    {
      "id": "audit_depth",
      "ask_when": "The finding detail is not specified.",
      "header": "Depth",
      "question": "How much finding detail should be returned?",
      "options": [
        {
          "label": "Full findings (Recommended)",
          "description": "Include evidence, impact, confidence, and remediation."
        },
        {
          "label": "Critical and high",
          "description": "Return only material findings."
        },
        {
          "label": "Top actions",
          "description": "Produce a short remediation backlog."
        }
      ]
    },
    {
      "id": "audit_remed",
      "ask_when": "The remediation format is absent.",
      "header": "Fix Format",
      "question": "How should remediation be presented?",
      "options": [
        {
          "label": "Guidance and CLI (Recommended)",
          "description": "Include candidate syntax and verification."
        },
        {
          "label": "Guidance only",
          "description": "Explain intent without syntax."
        },
        {
          "label": "Findings only",
          "description": "Report risk without fixes."
        }
      ]
    }
  ]
}
```
