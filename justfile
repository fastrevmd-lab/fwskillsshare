set dotenv-load := false
set export := false

setup:
    pre-commit install

dev:
    python3 scripts/check-skill-packages.py

fmt:
    git diff --check

lint:
    python3 scripts/check-skill-packages.py
    python3 scripts/test-runtime-intake-validator.py
    python3 scripts/check-runtime-intake.py
    python3 scripts/check-runtime-intake-safety.py
    python3 scripts/test-runtime-intake-safety.py
    python3 scripts/check-readme-branding.py

test:
    python3 scripts/check-shared-schema.py
    python3 scripts/check-installer.py
    python3 scripts/check-sd-bundle-server.py
    python3 scripts/check-srx-policy-global-default.py
    python3 scripts/check-audit-rule-contract.py
    python3 scripts/check-srx-stig-catalog.py
    python3 scripts/check-srx-stig-behavior.py
    python3 scripts/check-srx-license-signature-contract.py

guard: lint test

# Stage a de-branded copy for the downstream org and verify it. Dry run by
# default; pass --target <clone> --commit to land it. Never pushes.
publish-jnpr *ARGS:
    python3 scripts/publish-jnpr.py {{ARGS}}

# --ignore-user-config loads no MCP servers: nothing here needs them, and unlike a
# per-server denylist in .codex/config.toml it cannot be broken by a server rename.
# Codex review of a single commit (default: HEAD)
review COMMIT="HEAD":
    codex exec --ignore-user-config review --commit "$(git rev-parse {{COMMIT}})" --json \
      | jq -rR 'fromjson? | select(.type=="item.completed") | .item | select(.type=="agent_message") | .text'

integration:
    @echo "Real-device validation is intentionally opt-in and is not automated by this repository."

e2e:
    ./install.sh --help >/dev/null
    python3 scripts/test-installer.py
    python3 scripts/check-installer.py

security:
    trivy fs --scanners vuln,misconfig,secret --exit-code 1 .

release-check: lint test guard security
