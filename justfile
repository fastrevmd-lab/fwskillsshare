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
    python3 scripts/check-readme-branding.py

test:
    python3 scripts/check-shared-schema.py

guard: lint test

integration:
    @echo "Real-device validation is intentionally opt-in and is not automated by this repository."

e2e:
    ./install.sh --help >/dev/null
    python3 scripts/check-installer.py

security:
    trivy fs --scanners vuln,misconfig,secret --exit-code 1 .

release-check: lint test guard security
