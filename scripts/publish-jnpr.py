#!/usr/bin/env python3
"""Publish a de-branded copy of this repository to a downstream org.

This repository is upstream. The published copy deliberately shares no git
history with it, so no merge can carry mechub branding downstream, and no
downstream contribution can pull third-party copyright back into upstream.
Syncing is one-way, by design; bring downstream fixes back by hand.

The de-branding is verified, not assumed: `gate()` fails the run if any
forbidden token survives into the staged tree. A silent transform is not proof.

Default behaviour is a dry run that stages and verifies without touching any
target clone. Pushing is never automated -- the command to run is printed.

The whole catalog is published or nothing is. A partial export fails six of the
repo's own validators -- they assert the full inventory, and the skill-specific
checks crash outright when their skill is absent -- so shipping one would mean a
distribution that cannot pass its own checks. Curate by choosing when to sync,
not by choosing which skills go.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "docs" / "publish"

UPSTREAM_SLUG = "fastrevmd-lab/fwskillsshare"

# Allowlist, not denylist: anything not named here is never published, so a new
# directory of lab notes cannot leak by being forgotten.
PUBLISH_FILES = (
    "install.sh",
    "LICENSE",
    "README.md",
    "justfile",
    "mise.toml",
    ".editorconfig",
    ".gitignore",
    ".python-version",
    ".pre-commit-config.yaml",
    ".gitleaks.toml",  # the security workflow reads it; shipping one without the other
                       # scans downstream copies with no allowlist
    ".github/workflows/security.yml",
)
PUBLISH_DIRS = ("skills", "scripts")

# Excluded even though their parent directory is published.
# These read from docs/, which is upstream-only process material, so they cannot
# run downstream. gate() independently detects this class of breakage.
EXCLUDE_PATHS = (
    "scripts/check-readme-branding.py",      # asserts upstream branding
    "scripts/check-audit-rule-contract.py",  # reads docs/skill-tests/
    "scripts/check-runtime-intake-safety.py",
    "scripts/test-runtime-intake-safety.py",  # imports the checker above
    "scripts/publish-jnpr.py",                # upstream tooling; not part of the distribution
)

FORBIDDEN = re.compile(r"mechub|fastrevmd|violet", re.IGNORECASE)

# Citations of real field evidence, kept deliberately: stripping the URL turns a
# sourced claim into a bare assertion, which is the failure mode these skills exist
# to prevent. Attribution in the footer is an MIT courtesy, not branding.
PROVENANCE_OK = re.compile(re.escape(UPSTREAM_SLUG))

# Nested metadata.sources[].author entries are left as the upstream author on
# purpose -- they credit whoever did the underlying lab work, and rewriting them
# would attribute that evidence to the downstream org. They are provenance, not
# branding, so the gate must not treat them as a leak.
SOURCE_ATTRIBUTION_LINE = re.compile(r"^\s+author:\s*fastrevmd-lab\s*$")

# Lab-specific values that are fine upstream but must not ship downstream.
SANITIZE = (
    ("O=mechub", "O=example"),
)

BROKEN_LINK = re.compile(r"\]\((?:\./)?docs/")


def run(args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    """Run a command, returning stdout; raises CalledProcessError on failure."""
    return subprocess.run(
        args, cwd=cwd, env=env, check=True, capture_output=True, text=True
    ).stdout


def head_sha() -> str:
    """Return the full SHA of upstream HEAD."""
    return run(["git", "rev-parse", "HEAD"], cwd=ROOT).strip()


def working_tree_is_clean() -> bool:
    """True when there are no staged or unstaged changes."""
    return not run(["git", "status", "--porcelain"], cwd=ROOT).strip()


def archive_ref(allow_dirty: bool) -> tuple[str, bool]:
    """Return (ref to export, whether it differs from HEAD).

    With --allow-dirty the export must be the working tree, so it is captured by
    building a throwaway index rather than with `git stash create`. A stash
    commit holds only tracked changes -- untracked files hang off a separate
    parent and never appear in `git archive` -- so a newly added, uncommitted
    skill would have been silently omitted while the provenance claimed a clean,
    reproducible HEAD. Writing a tree from a scratch index picks up tracked
    modifications, deletions, and untracked files alike, still honours
    .gitignore, and leaves the real index untouched.

    Comparing that tree to HEAD's is also an exact dirtiness test, rather than
    inferring it from the flag.
    """
    head_tree = run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT).strip()
    if not allow_dirty:
        return "HEAD", False

    with tempfile.TemporaryDirectory(prefix="publish-jnpr-index-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        try:
            run(["git", "read-tree", "HEAD"], cwd=ROOT, env=env)
            run(["git", "add", "-A"], cwd=ROOT, env=env)
            tree = run(["git", "write-tree"], cwd=ROOT, env=env).strip()
        except subprocess.CalledProcessError as error:
            raise SystemExit(
                f"could not snapshot the working tree for a dirty export: "
                f"{error.stderr.strip() or error}"
            ) from error
    return tree, tree != head_tree


def stage_tree(dest: Path, ref: str) -> None:
    """Export tracked files at ref into dest, then apply the allowlist."""
    dest.mkdir(parents=True, exist_ok=True)
    # A fixed name beside dest would truncate, then delete, an unrelated file
    # that happened to sit there. Keep the archive in its own temp directory.
    with tempfile.TemporaryDirectory(prefix="publish-jnpr-archive-") as tmp:
        archive = Path(tmp) / "export.tar"
        with archive.open("wb") as handle:
            subprocess.run(
                ["git", "archive", "--format=tar", ref],
                cwd=ROOT, check=True, stdout=handle,
            )
        run(["tar", "-xf", str(archive), "-C", str(dest)])

    keep = {Path(name) for name in PUBLISH_FILES}
    for path in sorted(dest.rglob("*"), reverse=True):
        rel = path.relative_to(dest)
        if path.is_dir():
            if not any(path.iterdir()):
                path.rmdir()
            continue
        allowed = rel in keep or rel.parts[0] in PUBLISH_DIRS
        if not allowed or str(rel) in EXCLUDE_PATHS:
            path.unlink()

    for cache in dest.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def brand_block(name: str, **fields: str) -> str:
    """Load a neutral brand block template and fill its {PLACEHOLDERS}."""
    text = (BRAND_DIR / f"brand-{name}-neutral.md").read_text(encoding="utf-8").rstrip("\n")
    for key, value in fields.items():
        text = text.replace("{" + key + "}", value)
    return text


def swap_marked_block(text: str, name: str, replacement: str) -> str:
    """Replace the content between <!-- brand:NAME:start/end --> markers."""
    pattern = re.compile(
        rf"<!-- brand:{name}:start -->\n.*?\n<!-- brand:{name}:end -->",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(f"README.md is missing the brand:{name} markers")
    return pattern.sub(lambda _: replacement, text)


def transform_readme(dest: Path, repo_slug: str, skill_count: int) -> None:
    """Swap branded blocks for neutral ones and repoint upstream-only links."""
    path = dest / "README.md"
    text = path.read_text(encoding="utf-8")
    repo_name = repo_slug.split("/")[-1]

    # Sweep first: clone URLs, installer URLs, issue links all point downstream.
    # The brand blocks swapped in below deliberately reintroduce upstream credit.
    text = text.replace(UPSTREAM_SLUG, repo_slug)

    text = swap_marked_block(
        text, "header",
        brand_block("header", REPO_NAME=repo_name, SKILL_COUNT=str(skill_count)),
    )
    text = swap_marked_block(text, "disclaimer", brand_block("disclaimer"))
    text = swap_marked_block(text, "trademark", brand_block("trademark"))
    text = swap_marked_block(text, "footer", brand_block("footer"))

    # docs/ is never published; repoint its links at upstream so they still resolve.
    text = BROKEN_LINK.sub(f"](https://github.com/{UPSTREAM_SLUG}/blob/main/docs/", text)

    path.write_text(text, encoding="utf-8")


def pad_to_width(line: str, old: str, new: str) -> str:
    """Swap old->new inside a box-drawn banner line, preserving its display width.

    Padding is adjusted against the closing bar, so a shorter or longer slug does
    not shear the box. Box characters are single-column, so len() is the width.
    """
    if old not in line or "\u2551" not in line:
        return line
    swapped = line.replace(old, new)
    delta = len(line) - len(swapped)
    if delta == 0:
        return swapped
    head, bar, tail = swapped.rpartition("\u2551")
    if delta > 0:
        return head + " " * delta + bar + tail
    return re.sub(r" {0,%d}$" % -delta, "", head) + bar + tail


def transform_install(dest: Path, repo_slug: str) -> None:
    """Repoint the installer at the downstream repo."""
    path = dest / "install.sh"
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        line = pad_to_width(line, UPSTREAM_SLUG, repo_slug)
        out.append(line.replace(UPSTREAM_SLUG, repo_slug))
    path.write_text("\n".join(out), encoding="utf-8")
    path.chmod(0o755)


def transform_skill_frontmatter(dest: Path, author: str) -> None:
    """Rewrite only the top-level author list in every published SKILL.md.

    Scoped deliberately. `metadata.sources[].author` credits the person who did
    the underlying lab work, and rewriting those would attribute upstream field
    evidence to the downstream org -- a false provenance claim, and the exact
    thing these skills exist to prevent. Only the package's own author list,
    which is a top-level key with two-space list items, is rewritten.
    """
    for skill in sorted((dest / "skills").rglob("SKILL.md")):
        lines = skill.read_text(encoding="utf-8").split("\n")
        if not lines or lines[0].strip() != "---":
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            continue

        in_author_block = False
        for index in range(1, end):
            line = lines[index]
            if not line.startswith((" ", "\t")) and line.rstrip().endswith(":"):
                in_author_block = line.rstrip() == "author:"
                continue
            if in_author_block and line == "  - fastrevmd-lab":
                lines[index] = f"  - {author}"
        skill.write_text("\n".join(lines), encoding="utf-8")


def transform_skill_checker(dest: Path, author: str) -> None:
    """Point the package checker at the downstream author it will actually see."""
    path = dest / "scripts" / "check-skill-packages.py"
    if not path.is_file():
        return
    text = re.sub(r'"fastrevmd-lab"', f'"{author}"', path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")


def sanitize(dest: Path) -> None:
    """Strip lab-specific values that carry no meaning downstream."""
    for path in sorted(dest.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".py", ".sh"}:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for needle, replacement in SANITIZE:
            updated = updated.replace(needle, replacement)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def transform_justfile(dest: Path) -> None:
    """Drop recipe lines invoking checks that do not ship downstream."""
    dropped = {Path(p).name for p in EXCLUDE_PATHS}
    path = dest / "justfile"
    kept = [
        line for line in path.read_text(encoding="utf-8").split("\n")
        if not any(name in line for name in dropped)
    ]
    path.write_text("\n".join(kept), encoding="utf-8")


def write_provenance(dest: Path, sha: str, dirty: bool, skills: list[str]) -> None:
    """Record what this copy was built from, so the next sync knows the delta.

    A dirty export comes from a `git stash create` object, not HEAD, so naming
    HEAD would point the next sync at a revision that cannot reproduce this
    tree. Say so instead.
    """
    provenance = (
        f"- Upstream commit: `{sha}`\n" if not dirty else
        f"- Upstream commit: `{sha}` **plus uncommitted changes** -- this export\n"
        f"  was taken from the working tree and cannot be reproduced from that\n"
        f"  commit. Re-publish from a clean tree before relying on it.\n"
    )
    (dest / "UPSTREAM.md").write_text(
        "# Upstream\n\n"
        f"This repository is a de-branded distribution of [{UPSTREAM_SLUG}]"
        f"(https://github.com/{UPSTREAM_SLUG}), published under the MIT License.\n\n"
        f"{provenance}"
        f"- Skills published: {len(skills)}\n\n"
        "Changes are made upstream and synced here one-way by "
        "`scripts/publish-jnpr.py`. Downstream fixes are welcome; they are "
        "carried back upstream by hand so that authorship stays unambiguous.\n",
        encoding="utf-8",
    )


def scrub_source_attribution(rel: Path, text: str) -> str:
    """Blank out author lines that sit under metadata.sources in SKILL.md frontmatter.

    Scoped rather than global: an indented `author: fastrevmd-lab` anywhere else
    is branding that must still trip the gate, so only entries proven to be
    inside the sources block are exempt.
    """
    if rel.name != "SKILL.md":
        return text
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    try:
        end = lines.index("---", 1)
    except ValueError:
        return text

    in_metadata = False
    in_sources = False
    for index in range(1, end):
        line = lines[index]
        indent = len(line) - len(line.lstrip())
        if line.strip() and indent == 0:
            in_metadata = line.rstrip() == "metadata:"
            in_sources = False
            continue
        if in_metadata and indent == 2 and line.strip() == "sources:":
            in_sources = True
            continue
        if in_metadata and in_sources and indent <= 2 and line.strip():
            in_sources = False
        if in_sources and SOURCE_ATTRIBUTION_LINE.match(line):
            lines[index] = ""
    return "\n".join(lines)


def gate(dest: Path) -> list[str]:
    """Fail-closed verification. Returns human-readable violations."""
    violations: list[str] = []
    for path in sorted(dest.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(dest)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            violations.append(f"{rel}: binary file in published tree")
            continue

        scrubbed = PROVENANCE_OK.sub("", scrub_source_attribution(rel, text))
        for number, line in enumerate(scrubbed.split("\n"), start=1):
            if FORBIDDEN.search(line):
                violations.append(f"{rel}:{number}: forbidden token -> {line.strip()[:90]}")
        if path.suffix == ".py" and rel.parts[0] == "scripts" and re.search(r'"docs"|docs/', text):
            violations.append(f"{rel}: published script depends on unpublished docs/")
        if path.suffix == ".md":
            for number, line in enumerate(text.split("\n"), start=1):
                if BROKEN_LINK.search(line):
                    violations.append(f"{rel}:{number}: link into unpublished docs/")
    return violations


def remote_slug(url: str) -> str | None:
    """Normalize a git remote URL to owner/repo, lowercased.

    A substring test is not enough: `JNPRAutomate/fwskillsshare` is a substring
    of `JNPRAutomate/fwskillsshare-backup`, and accepting the wrong clone means
    staging the deletion of every tracked file in it.
    """
    cleaned = url.strip().removesuffix(".git")
    match = re.search(r"[:/]([^/:]+)/([^/]+)$", cleaned)
    return f"{match.group(1)}/{match.group(2)}".lower() if match else None


def validate_target(target: Path, repo_slug: str) -> str | None:
    """Check everything about the target that can refuse the run, mutating nothing.

    Split out from sync_to_target so it can run before the export is staged.
    Left inside, a bad target was only detected after stage_tree() had already
    written the export, so a refused run still left generated files behind.

    Returns an error message, or None when the target is usable.
    """
    # `.git` is a file, not a directory, inside a linked worktree -- and this repo
    # uses worktrees -- so test with git itself rather than by inspecting the path.
    probe = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=target, capture_output=True, text=True,
    )
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return f"not a git working tree: {target}"
    if target == ROOT or target in ROOT.parents or ROOT in target.parents:
        return f"refusing to sync into the upstream repo or a path containing it: {target}"
    try:
        remote = run(["git", "remote", "get-url", "origin"], cwd=target).strip()
    except subprocess.CalledProcessError:
        return f"target has no origin remote to verify: {target}"
    if remote_slug(remote) != repo_slug.lower():
        return f"target origin {remote!r} does not match --repo-slug {repo_slug!r}"
    if run(["git", "status", "--porcelain"], cwd=target).strip():
        return f"target clone has uncommitted changes: {target}"
    return None


def ignored_collisions(staged: Path, target: Path) -> list[str]:
    """Return target paths holding ignored files that the export would overwrite.

    `git rm` leaves ignored files alone and `git status` never reports them, so
    they survive the removal step and then get clobbered by the copy. That
    contradicts the preservation this sync promises, and the loss is silent and
    unrecoverable -- the file was never in git. Detect the overlap and refuse.
    """
    candidates = [
        str(path.relative_to(staged))
        for path in staged.rglob("*")
        if path.is_file() and (target / path.relative_to(staged)).is_file()
    ]
    if not candidates:
        return []
    result = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=target, input="\n".join(candidates),
        capture_output=True, text=True,
    )
    # exit 0 = some ignored, 1 = none ignored, >1 = real error
    if result.returncode > 1:
        raise SystemExit(f"could not check ignored paths in {target}: {result.stderr.strip()}")
    return sorted(line for line in result.stdout.split("\n") if line.strip())


def sync_to_target(staged: Path, target: Path, sha: str, dirty: bool, repo_slug: str, commit: bool) -> None:
    """Mirror the staged tree into a target clone as a single squashed commit.

    Stale files are removed with `git rm`, never with a recursive filesystem
    delete. That keeps every removal recoverable from git history and leaves
    untracked and ignored files (a local .env, for instance) alone -- a plain
    wipe would take those with it, and `git status --porcelain` would not even
    have shown them.

    The target is revalidated here even though main() already checked it.
    Staging and gating take time and the clone is not held, so between the
    preflight and this point another process can dirty it, change its remote,
    or add untracked files the copy would overwrite. Check once to fail early,
    again immediately before mutating.
    """
    problem = validate_target(target, repo_slug)
    if problem:
        raise SystemExit(problem)
    collisions = ignored_collisions(staged, target)
    if collisions:
        listed = "\n  ".join(collisions[:10])
        more = f"\n  ... and {len(collisions) - 10} more" if len(collisions) > 10 else ""
        raise SystemExit(
            "refusing to sync: these target paths hold ignored local files that the "
            f"export would overwrite:\n  {listed}{more}\n"
            "Move or delete them, or drop them from the export."
        )

    if run(["git", "ls-files"], cwd=target).strip():
        run(["git", "rm", "-r", "-q", "--", "."], cwd=target)

    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for entry in staged.iterdir():
        dst = target / entry.name
        if entry.is_dir():
            # dirs_exist_ok: `git rm` leaves a directory behind when it still
            # holds ignored files (a stray __pycache__), and a plain copytree
            # would raise FileExistsError in exactly the case this preserves.
            shutil.copytree(entry, dst, ignore=ignore, dirs_exist_ok=True)
        else:
            shutil.copy2(entry, dst)

    run(["git", "add", "-A"], cwd=target)
    if not run(["git", "status", "--porcelain"], cwd=target).strip():
        print("target already matches upstream; nothing to commit")
        return
    if not commit:
        print(f"staged into {target} (not committed; pass --commit)")
        return

    message = (
        f"chore: sync skills from upstream\n\n"
        f"De-branded export of {UPSTREAM_SLUG}.\n\n"
        f"Upstream-Commit: {sha}\n"
    )
    run(["git", "commit", "-m", message], cwd=target)
    print(f"committed to {target}")
    print("\nReview, then push yourself:")
    print(f"  git -C {target} push origin HEAD")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--repo-slug", default="JNPRAutomate/fwskillsshare",
                        help="downstream org/repo (default: %(default)s)")
    parser.add_argument("--author", default="JNPRAutomate",
                        help="value for the authors: frontmatter field")
    parser.add_argument("--out", type=Path, help="keep the staged tree at this path")
    parser.add_argument("--target", type=Path, help="local clone of the downstream repo")
    parser.add_argument("--commit", action="store_true", help="commit in the target clone")
    parser.add_argument("--allow-dirty", action="store_true",
                        help="publish from a dirty working tree (not recommended)")
    args = parser.parse_args()

    if not args.allow_dirty and not working_tree_is_clean():
        print("ERROR: working tree is dirty; commit first or pass --allow-dirty", file=sys.stderr)
        return 1

    sha = head_sha()
    ref, dirty = archive_ref(args.allow_dirty)

    # Everything that can refuse the run happens before a single file is
    # written. The refusal inside sync_to_target() is too late on its own: with
    # --out pointing inside --target, staging populates the target before the
    # sync is ever called.
    if args.target:
        target = args.target.resolve()
        problem = validate_target(target, args.repo_slug)
        if problem:
            print(f"ERROR: {problem}", file=sys.stderr)
            return 1
        if dirty and args.commit:
            print("ERROR: refusing to commit a dirty export: the trailer would name a "
                  "commit that cannot reproduce this tree. Re-run from a clean working "
                  "tree.", file=sys.stderr)
            return 1
        if args.out:
            out = args.out.resolve()
            if out == target or target in out.parents or out in target.parents:
                print(f"ERROR: --out {out} overlaps --target {target}; staging would "
                      "write into the clone being synced.", file=sys.stderr)
                return 1

    scratch = Path(tempfile.mkdtemp(prefix="publish-jnpr-"))
    staged = args.out.resolve() if args.out else scratch / "tree"
    if staged.exists() and any(staged.iterdir()):
        print(f"ERROR: --out path is not empty, refusing to write into it: {staged}",
              file=sys.stderr)
        return 1

    try:
        stage_tree(staged, ref)
        skills = sorted(p.name for p in (staged / "skills").iterdir() if p.is_dir())
        transform_readme(staged, args.repo_slug, len(skills))
        transform_install(staged, args.repo_slug)
        transform_skill_frontmatter(staged, args.author)
        transform_skill_checker(staged, args.author)
        transform_justfile(staged)
        sanitize(staged)
        write_provenance(staged, sha, dirty, skills)

        violations = gate(staged)
        if violations:
            print(f"ERROR: de-branding gate failed ({len(violations)} violation(s)):", file=sys.stderr)
            for violation in violations:
                print(f"  {violation}", file=sys.stderr)
            return 1

        print(f"OK: staged {len(skills)} skill(s) from {sha[:12]}, de-branding gate clean")
        print(f"    tree: {staged}")

        if args.target:
            sync_to_target(staged, args.target.resolve(), sha, dirty, args.repo_slug, args.commit)
        else:
            print("    dry run -- pass --target <clone> to sync")
    except SystemExit:
        shutil.rmtree(scratch, ignore_errors=True)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
