# Runtime Intake Questions Design

**Date:** 2026-07-24

**Status:** Approved for planning

## Goal

Give every packaged skill a conditional, portable runtime-intake workflow that
uses Claude `AskUserQuestion`, Codex `request_user_input`, or a plain-text
fallback to resolve material ambiguity before analysis or planning.

## Scope

Apply the behavior to all 22 `skills/*/SKILL.md` packages:

- `cis-controls-ngfw-compliance`
- `cmmc-nist-800-171-ngfw-compliance`
- `firewall-best-practices-audit`
- `firewall-config-conversion`
- `firewall-config-diff`
- `hipaa-ngfw-compliance`
- `iso27001-ngfw-compliance`
- `parsing-cisco-configs`
- `parsing-fortinet-configs`
- `parsing-palo-configs`
- `parsing-srx-configs`
- `pci-ngfw-compliance`
- `sd-onprem-proxmox-deploy`
- `soc2-ngfw-compliance`
- `srx-advpn`
- `srx-autovpn-full-tunnel`
- `srx-dynamic-ip-feed`
- `srx-ipsec-hub-spoke`
- `srx-mnha`
- `srx-mpls-in-flow`
- `srx-nat`
- `srx-policy`

Each package receives:

1. A concise `## Runtime intake` section in `SKILL.md`.
2. A package-local `references/runtime-intake.md` containing the complete
   skill-specific question catalog.

The work also repairs three pre-existing package-validation defects in
`sd-onprem-proxmox-deploy`: add the skill to the expected package inventory,
add the missing `GPT` author, and add Codex UI metadata.

## Architecture

Keep each skill independently installable. Do not introduce a repository-wide
runtime reference that would be missing when an individual skill is installed.

The `SKILL.md` section defines the decision behavior and links to the local
reference. It remains short enough for skills already near the repository's
500-line progressive-disclosure ceiling. Detailed question catalogs live in
references, where they are loaded only when unresolved material ambiguity
exists.

The runtime-intake reference uses a neutral question contract rather than a
literal native-tool payload. For Claude, project each selected neutral entry to
only `question`, `header`, and `options`, then add `multiSelect: false`; never
send `id` or `ask_when`. For Codex, project each selected neutral entry to only
`id`, `header`, `question`, and `options`; never send `ask_when` or
`multiSelect`. For each unresolved material fact whose catalog condition is
true, invoke the native interaction tool before continuing or issuing an
open-ended request. Without a native tool, present each selected catalog
question in concise plain text with its 2-3 labeled choices and a free-text
`Other` path; do not substitute a generic checklist.

## Invocation Decision

Before asking a question, the skill must inspect:

1. The user's request.
2. Supplied configurations and artifacts.
3. Available approved read-only evidence.
4. Answers already provided in the current conversation.

Invoke the interaction tool only when at least one unresolved fact materially
affects:

- assessment or conversion scope;
- technical correctness or platform support;
- safety, authorization, or secret handling;
- confidence in a conclusion; or
- the requested deliverable.

Do not invoke the tool when the answer is already present, can be established
from safe read-only evidence, or would not change the result. Do not present the
entire catalog automatically on every run.

Prioritize unresolved questions in this order:

1. Safety and authorization.
2. Scope and system boundary.
3. Platform, release, topology, or framework basis.
4. Evidence completeness and confidence.
5. Output format and emphasis.

Ask no more than three single-select catalog questions per call. After every
response, ask another round whenever any unresolved material catalog condition
remains true; continue only when none remain. Do not repeat answered questions
or show the full catalog.

## Portable Question Contract

The neutral JSON object has exactly one top-level key, `questions`. Question
objects have exactly `id`, `ask_when`, `header`, `question`, and `options`;
option objects have exactly `label` and `description`. Native-only keys,
including `multiSelect`, are unsupported in the neutral catalog.

Every catalog entry contains:

- `id`: stable, unique, lowercase snake-case identifier;
- `ask_when`: nonblank, stripped observable condition that makes the question
  relevant;
- `header`: nonblank, stripped user-facing label of at most 12 characters;
- `question`: one nonblank, stripped direct question sentence with exactly one
  question mark;
- `options`: two or three mutually exclusive choices.

Every option contains:

- `label`: nonblank, stripped short choice label;
- `description`: one nonblank, stripped sentence explaining the effect of the
  choice.

The first option is the recommended safe default and its label ends with
`(Recommended)`. When the triggering fact is unresolved, that default must not
assert that the missing fact is known, complete, available, valid, or verified.
Rewrite a factual prompt as an action or workflow decision when necessary so a
safe discovery, inventory, inspection, mapping, tracing, confirmation, or
verification option directly answers the question.

Every option set is a mutually exclusive single-select choice along one
material axis. Do not mix evidence availability with collection method, current
state with requested workflow, or address family with special traffic. The
native free-text `Other` path remains available for exact values and choices
not represented in the catalog.

Each `references/runtime-intake.md` contains:

1. `# Runtime Intake`
2. `## When to ask`
3. `## Tool adaptation`
4. `## Question catalog`
5. One parseable JSON `questions` object implementing the neutral contract.

JSON is used inside the Markdown reference so repository validation can check
the catalog with the Python standard library and both agents can translate it
deterministically.

## Runtime Data Flow

1. Load the skill and begin its normal workflow.
2. Inspect request and evidence before loading the runtime-intake reference.
3. If no material ambiguity remains, continue without asking questions.
4. If ambiguity remains, load `references/runtime-intake.md`.
5. Filter entries whose `ask_when` conditions are true.
6. Remove entries already answered or rendered irrelevant by evidence.
7. Select up to three highest-priority entries.
8. Project them to the exact Claude or Codex native key set defined above.
9. If no native tool is available, ask the same questions in concise plain
   text with a free-text `Other` path.
10. Re-evaluate the catalog after the response.
11. Continue, make an explicit assumption, or stop on a documented blocker.

## Safety and Error Handling

- Never request passwords, PSKs, private keys, tokens, device credentials,
  unredacted customer configurations, or other secrets.
- Ask how secrets will be supplied outside the conversation, or use
  placeholders for planning output.
- Treat intake answers as task context, not approval for configuration,
  commit, upgrade, reboot, deletion, or failover.
- Obtain separate explicit approval immediately before any live or destructive
  action.
- When a native question tool is unavailable, use plain text without changing
  the question's meaning.
- Treat free text as the `Other` value, not as a malformed predefined choice.
- If the user skips a noncritical question, use the safest documented
  assumption and disclose it.
- If an unanswered question could make the result unsafe or materially
  incorrect, stop and state the exact blocker.
- If options are not mutually exclusive, repair the catalog instead of relying
  on multi-select, because the portable contract is single-select.

## Validation Strategy

Add `scripts/check-runtime-intake.py` and invoke it from repository validation.
The script accepts an optional skill name for sequential RED/GREEN testing and
validates all skills when no name is supplied.

Add `scripts/check-runtime-intake-safety.py` after structural validation. It
parses all 22 Appendix A catalogs and all 22 package catalogs, requires exact
ordered question-object equality for every skill, rejects duplicate Appendix
sections, rejects noncanonical lexical numbering such as `A.01` and incorrect
A.1 through A.22 number/name pairings, rejects duplicate package JSON members,
and preserves same-line whitespace so noncanonical tabs or doubled spaces
cannot be normalized away. It resolves each semantic regression key exactly
once and checks the complete 155-question corpus, the exact 102 safe first
labels, and 58 single-axis option tuples identified by final review.

The safety checker also locks the complete content and question order of all
22 catalogs with canonical SHA-256 digests. Its optional skill argument limits
equality, digest, safe-default, and option-tuple assertions to the selected
catalog, but every focused run still parses all 22 plan and package catalogs
and resolves every manifest key. Focused success output reports selected
assertion counts separately from that whole-corpus work.

Add `scripts/test-runtime-intake-safety.py` immediately after the safety
checker in `just lint`. Its standard-library temporary-file tests must exercise
all 50 explicitly pinned semantic IDs, duplicate or container-nested Appendix
sections and lookalikes, incorrect Appendix number/name pairing, noncanonical
lexical numbering, duplicate package JSON members, inactive package catalogs,
inactive Appendix decoy rows, same-line doubled whitespace in Appendix
questions, labels, and descriptions, exact focused output counts, complete
digest-manifest coverage, and synchronized content and order mutations that
equality alone would miss.

For each skill, validate:

- `SKILL.md` contains a `## Runtime intake` section;
- the section names Claude `AskUserQuestion` and Codex
  `request_user_input`;
- before section extraction, the validator conservatively rejects either HTML
  comment delimiter (`<!--` or `-->`) anywhere in `SKILL.md`, including escaped
  text, inline code, and fenced code;
- the validator then masks standard backtick or tilde fenced-code regions,
  including fences opened directly after a CommonMark list marker, without
  changing length, newline positions, or offsets; direct list-item openers
  allow zero to three spaces before `-`/`+`/`*` or a one-to-nine-digit ordered
  marker ending in `.`/`)` and one to four following spaces;
- bullet markers may interrupt an open paragraph, but an ordered list-item
  fence may do so only when its parsed numeric value is `1` (including a
  leading-zero spelling within the one-to-nine-digit limit); non-`1` ordered
  markers remain active paragraph continuation unless they occur at document
  start, after a blank line, or after a recognized ATX-heading block boundary;
  unfamiliar active syntax conservatively keeps paragraph context open;
- blank lines remain inside an open list-item fence regardless of indentation;
  a nonblank line lacking the captured list continuation indentation ends the
  containing list item and its fence, then that same physical line is
  reprocessed by the ordinary fence, comment, and active-Markdown path;
- correctly indented list-fence closing candidates are evaluated only after
  removing the captured continuation indentation; ordinary and top-level
  unclosed-fence behavior remains unchanged;
- ordinary fence closer recognition remains unchanged, invalid backtick info
  strings remain active, and prose with a later fence sequence, ten-digit
  ordered markers, four-space-indented markers, and invalid marker spacing do
  not become fence openers;
- the validator rejects every CommonMark 0.31.2 raw HTML block opener family
  in the resulting active Markdown, including blocks nested in list or
  blockquote containers: case-insensitive type 1
  `pre`/`script`/`style`/`textarea` tags, processing instructions,
  declarations, CDATA, the complete type 6 block-tag list with its specified
  boundary, and complete generic type 7 opening or closing tag lines, all with
  at most three leading spaces;
- raw HTML block syntax inside fenced code and inline placeholder tags that do
  not meet a block-start rule remain permitted; runtime headings with zero to
  three leading spaces or active list/blockquote container prefixes are
  discovered only in the same active-Markdown mask, while four-space-indented
  forms remain code; Setext equivalence is evaluated from the complete heading
  paragraph so a multiline heading ending in `Runtime intake` is not an exact
  duplicate; the sole approved primary `## Runtime intake` heading must still
  begin at column zero, then the original section is sliced by the preserved
  offsets;
- the section-scoped validator normalizes whitespace across that complete
  original section and requires equality to the approved standard template or
  the skill-selected `srx-mnha`/`srx-policy` compact template;
- the exact template mandates catalog questions before continuing or issuing
  an open-ended request, limits each round to three single-select catalog
  questions, requires another round while any unresolved material catalog
  condition remains true, continues only when none remain, defines no-repeat
  and no-full-catalog behavior, preserves each selected question's 2-3 labeled
  choices and free-text `Other` in plain-text fallback, and forbids
  generic-checklist substitution;
- conservative ambiguity checks reject complete runtime regions hidden in HTML
  comments or any CommonMark raw HTML block family before heading discovery
  and cannot be bypassed with escaped or inline-code comment delimiters;
  active-heading discovery rejects a complete region in a code fence, while a
  one-to-three-space duplicate runtime heading remains active, including after
  a list-fence deindent; non-`1` ordered markers continuing prose cannot mask
  an indented duplicate heading or raw HTML block; complete-section equality
  rejects inactive fence wrappers inside an active section, extra or
  contradictory prose, missing approved text, and duplicate active runtime
  sections while permitting whitespace-only variation;
- the exact section retains secret safety and separate live-change approval
  and links to `references/runtime-intake.md`;
- the reference contains the four exact active headings in canonical order,
  rejects active list/blockquote duplicates, and contains one active,
  column-zero, line-anchored JSON catalog fence inside the Question catalog
  section;
- the exact Claude projection, Codex projection, and plain-text fallback with
  free-text `Other` language remain inside the Tool adaptation section;
- raw JSON objects contain no duplicate member names;
- Appendix A contains exactly one section for each expected skill, numbered
  lexically and canonically from A.1 through A.22 without leading zeros;
  container-nested headings/lookalikes and raw HTML remain active and cannot
  bypass detection, while fenced or commented decoy rows remain inactive and
  cannot pollute adjacent active rows;
- Appendix prose preserves canonical same-line whitespace without tabs or
  doubled spaces in catalog fields;
- the neutral catalog, question objects, and option objects contain exactly
  their documented keys and no tool-specific or unknown keys;
- every question has a unique `id`, nonblank stripped `ask_when`, nonblank
  stripped `header`, exactly one nonblank stripped question sentence, and two
  or three options;
- every option has a nonblank stripped short `label` and exactly one nonblank
  stripped sentence in `description`;
- sentence-boundary checks ignore an initialism-ending period only when the
  next non-space token begins with a lowercase letter or digit; an uppercase
  token is conservatively treated as a new sentence;
- the first label ends with `(Recommended)`;
- standard-library negative contract tests exercise rejected keys, whitespace,
  sentence boundaries, and stale adaptation language;
- standard-library safety tests exercise the complete semantic and canonical
  catalog lock, including synchronized plan/package mutations;
- installer tests require byte-identical `SKILL.md`,
  `references/runtime-intake.md`, and source-present `agents/openai.yaml`
  artifacts for every family and explicit installation;
- all other package and line-limit checks continue to pass.

Follow a sequential test-first cycle:

1. Add the validator before editing skills.
2. Run it against one unchanged skill and observe the expected missing-feature
   failure.
3. For each skill, run the focused validator before editing and confirm the
   expected failure.
4. Add the minimal runtime section and catalog.
5. Re-run focused validation and require success before moving to the next
   skill.
6. Run all repository checks after all 22 skills pass individually.

Fresh-agent forward testing is not part of this change because the current
session is not authorized to delegate to subagents. Deterministic structural
validation is the release gate; lack of independent behavioral evaluation is
reported as remaining risk.

## Repository Checks

Run the required checks from the project instructions:

- `just fmt`
- `just lint`
- `just test`
- `just guard`
- `just security`
- `just release-check`

The current workstation does not have `just` installed. If it remains
unavailable, run each underlying command from `justfile` directly and report
the missing runner as an environment limitation. `just integration` remains
non-device and may be reported separately; no real-device validation is
authorized.

## Success Criteria

- All 22 skills implement conditional runtime intake.
- Every skill remains independently portable.
- No `SKILL.md` exceeds the 500-line limit.
- Claude and Codex can derive valid native question calls from the same
  catalog.
- Questions already answered are not repeated.
- No secret is requested and no intake answer is treated as live-change
  authorization.
- Focused validation passes for every skill.
- Repository validation passes except for explicitly reported unavailable
  workstation tooling.

## Non-Goals

- Do not execute configuration changes on firewalls, Proxmox, or deployed
  services.
- Do not add a multi-select question contract.
- Do not change shared normalized firewall schemas.
- Do not rewrite unrelated skill workflows or vendor guidance.
- Do not claim runtime behavioral coverage from deterministic validation
  alone.
