#!/usr/bin/env python3
"""Notice friction with the cmem-plugin-template at the end of a session.

This is a Claude Code ``Stop`` hook, wired up in ``.claude/settings.json`` and
run through ``task template:feedback-check``. It belongs to the template - see
``.claude/rules/copier-template.md``.

It says nothing at all unless the session left evidence that a template owned
file got in the way, and then it asks the agent to consider whether that is
worth reporting upstream. Deciding there is nothing to report is a valid
answer; the hook fires at most once per session either way.

Two rules govern everything below. Print **nothing** unless there is something
to say, because stdout is the hook's JSON channel. And always exit 0, whatever
goes wrong - a broken hook must never keep a session from ending.

This file is not part of the package and is not covered by ``task check``, so
keep it small, dependency free and readable.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

OPT_OUT = Path(".claude") / "no-template-feedback"

# Paths the template owns. The shipped rules tell the agent not to edit these,
# so a modification here is the strongest available signal that something in
# the template did not fit.
TEMPLATE_OWNED = (
    ".claude/",
    ".github/workflows/",
    ".gitlab-ci.yml",
    ".pre-commit-config.yaml",
    "Taskfile.yaml",
)

# An added line silencing a check. The rules forbid these outright, so a new
# one always means a rule lost an argument with real code.
SILENCER = re.compile(r"^\+.*#\s*(noqa|type:\s*ignore)")

# A rule code added to a list in pyproject.toml - almost always the ruff
# ignore list growing.
RUFF_RULE = re.compile(r'^\+\s*"[A-Z]{1,4}[0-9]{1,4}"')

# What copier leaves behind when an update could not be merged.
CONFLICT = re.compile(r"^\+?<{7} ")

# Colour codes git writes when the user configured `color.diff = always`, which
# it does even when the output is a pipe.
ANSI = re.compile(r"\x1b\[[0-9;]*m")

TIMEOUT = 10


def git(*args: str) -> str:
    """Run a git command and return its plain output, or "" on any failure.

    Colour is both switched off and stripped afterwards. ``color.diff`` is a
    common setting, it outranks ``color.ui``, and it paints diff output even
    into a pipe - which would leave every pattern above matching nothing at
    all, silently.
    """
    try:
        result = subprocess.run(
            ["git", "--no-pager", "-c", "color.ui=false", *args],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return ANSI.sub("", result.stdout) if result.returncode == 0 else ""


def marker_for(session_id: str) -> Path:
    """Return the once-per-session marker file for a session id."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "", session_id)[:64] or "unknown"
    return Path(tempfile.gettempdir()) / f"cmem-template-feedback-{safe}"


def collect_evidence() -> list[str]:
    """Return human readable evidence of template friction, newest first."""
    evidence = []

    status = git("status", "--porcelain")
    touched = sorted(
        {
            path
            for line in status.splitlines()
            for path in [line[3:].split(" -> ")[-1].strip()]
            if path.startswith(TEMPLATE_OWNED)
        }
    )
    if touched:
        evidence.append(f"template owned files were changed here: {', '.join(touched)}")

    rejects = [
        line[3:].strip() for line in status.splitlines() if line[3:].strip().endswith(".rej")
    ]
    if rejects:
        evidence.append(f"a copier update left rejected hunks behind: {', '.join(rejects)}")

    diff = git("diff", "HEAD")
    if any(SILENCER.match(line) for line in diff.splitlines()):
        evidence.append("a '# noqa' or '# type: ignore' was added")
    if any(CONFLICT.match(line) for line in diff.splitlines()):
        evidence.append("conflict markers are still in the working tree")

    if any(RUFF_RULE.match(line) for line in git("diff", "HEAD", "--", "pyproject.toml").splitlines()):
        evidence.append("a lint rule was added to the ignore list in pyproject.toml")

    return evidence


def main() -> None:
    """Read the hook payload, and block once if there is something to report."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, OSError):
        return

    if not isinstance(payload, dict) or payload.get("stop_hook_active"):
        return
    if OPT_OUT.exists():
        return

    marker = marker_for(str(payload.get("session_id", "")))
    if marker.exists():
        return

    evidence = collect_evidence()
    if not evidence:
        return

    try:
        marker.touch()
    except OSError:
        return

    reason = (
        "Before finishing: this session shows signs that something in the "
        "cmem-plugin-template got in the way - "
        + "; ".join(evidence)
        + ". Consider whether that is a finding other generated projects would "
        "share. If it is, use the 'template-feedback' skill to check what has "
        "already been decided and to draft an issue for the template, which "
        "you must show the user before filing anything. If it is specific to "
        "this project, say so in one sentence and stop - that is a complete "
        "answer and this check will not ask again in this session."
    )
    json.dump({"decision": "block", "reason": reason}, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
