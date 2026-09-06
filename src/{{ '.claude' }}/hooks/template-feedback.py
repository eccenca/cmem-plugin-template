#!/usr/bin/env python3
"""Notice friction with the cmem-plugin-template at the end of a session.

This is a Claude Code ``Stop`` hook. ``.claude/settings.json`` runs it
directly, and not through a task, because a task runner writes to stdout and
picks its own exit codes - and stdout is this hook's JSON channel. It reads the
hook payload from stdin, so a hand run needs one::

    echo '{}' | python3 .claude/hooks/template-feedback.py

It belongs to the template - see ``.claude/rules/copier-template.md``.

It says nothing at all unless the session left evidence that a template owned
file got in the way, and then it asks the agent to consider whether that is
worth reporting upstream. Deciding there is nothing to report is a valid
answer; the hook fires at most once per session either way.

Three rules govern everything below. Print **nothing** unless there is
something to say, because stdout is the hook's JSON channel. Always exit 0,
whatever goes wrong - a broken hook must never keep a session from ending. And
when a fact cannot be established, drop the evidence rather than guessing: a
false positive blocks a session, a false negative only misses one report.

This file is not part of the package and is not covered by ``task check``, so
keep it small, dependency free and readable.
"""

import json
import re
import subprocess
import sys
import tempfile
import tomllib
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

# The one template owned file that *documents* what a conflict looks like, in
# a fenced example. Every copier update that rewrites it adds those markers to
# the diff, which would block the session during the very workflow this hook
# exists to support.
CONFLICT_PROSE = ".claude/skills/copier-update/SKILL.md"

# Suffixes the suppression comments below can appear in at all. Without this,
# a CHANGELOG entry or a rules file merely naming `# noqa` counts as one.
PYTHON_SUFFIXES = (".py", ".pyi")

# A comment silencing a check. The rules forbid these outright, so a new one
# means a rule lost an argument with real code. Counted per file against the
# removed side, so editing a line that already carried one is not a finding.
SILENCER = re.compile(r"#\s*(noqa|type:\s*ignore)")

# What copier leaves behind when an update could not be merged. Only an added
# line counts; a marker already committed is this project's problem, not the
# template's.
CONFLICT = re.compile(r"^\+<{7} ")

# A changed `_commit` in the copier answers file. Its presence means the
# working tree *is* a copier update, so the template owned files it rewrote
# were not edited by anyone and are not evidence of anything.
COPIER_UPDATE = re.compile(r"^\+_commit:")

# Colour codes git writes when the user configured `color.diff = always`, which
# it does even when the output is a pipe.
ANSI = re.compile(r"\x1b\[[0-9;]*m")

# Enough of a file to find a suppression in, without reading a data fixture
# somebody left untracked.
READ_LIMIT = 512 * 1024

# The shortest useful `git status --porcelain` record: "XY " and one character
# of path.
MIN_STATUS_FIELD = 4

TIMEOUT = 10


def git(*args: str) -> str | None:
    """Run a git command and return its plain output, or None if it failed.

    "Failed" and "said nothing" must stay apart. `git diff HEAD` exits non-zero
    on an unborn HEAD, and a caller reading that as an empty diff would go half
    blind - seeing every untracked file through `git status` while believing
    nothing had changed. The same applies when git is missing from PATH or
    another process holds `index.lock`.

    The configuration passed here pins the output format the parsers assume:
    colour off (`color.diff` outranks `color.ui` and paints even into a pipe),
    the `a/` and `b/` diff prefixes on, and paths unquoted.
    """
    command = [
        "git",
        "--no-pager",
        "-c",
        "color.ui=false",
        "-c",
        "core.quotePath=false",
        "-c",
        "diff.noprefix=false",
        "-c",
        "diff.mnemonicPrefix=false",
        *args,
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return ANSI.sub("", result.stdout)


def entries(status: str) -> list[tuple[str, str]]:
    """Return the (status, path) pairs of a `git status --porcelain -uall -z`.

    `-z` is what makes this safe to parse: paths arrive verbatim, so neither
    `core.quotePath` nor a space in a name can defeat a prefix or suffix test.
    A rename is emitted as the new path followed by the original one, and only
    the new path is of any interest here.
    """
    fields = [field for field in status.split("\0") if field]
    pairs = []
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if len(field) < MIN_STATUS_FIELD:
            continue
        code, path = field[:2], field[3:]
        pairs.append((code, path))
        if code[0] in "RC" or code[1] in "RC":
            index += 1  # the original path of a rename or copy
    return pairs


def attributed(diff: str) -> list[tuple[str | None, str]]:
    """Pair every content line of a diff with the file it belongs to.

    A flat scan cannot tell a project's own code from a template owned file
    that merely *writes about* the thing being looked for - the rules file
    discusses `# noqa`, and matching that prose reports the template to itself.

    A line whose file could not be established is paired with None, and every
    caller drops those. That happens for a deletion, whose `+++` side is
    `/dev/null`, and it is the safe direction: unattributed evidence is no
    evidence.
    """
    pairs: list[tuple[str | None, str]] = []
    path: str | None = None
    in_header = False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            path, in_header = None, True
        elif not in_header:
            pairs.append((path, line))
        elif line.startswith("@@"):
            in_header = False
        elif line.startswith("+++ b/"):
            # Git pads the path with a tab when the name needs it.
            path = line[len("+++ b/") :].split("\t")[0]
    return pairs


def owned(path: str | None) -> bool:
    """Say whether a path is one the template writes."""
    return path is not None and path.startswith(TEMPLATE_OWNED)


def added_silencers(pairs: list[tuple[str | None, str]], untracked: list[str]) -> bool:
    """Say whether this project gained a suppression comment.

    Three things have to line up. The file must be one this project authored -
    a `# noqa` inside a template owned file was written by the template. It
    must be Python, or prose naming the comment counts as using it. And the
    file must end up with more of them than it started with, so editing a line
    that has always carried one is not a finding.

    Untracked files are read from disk, because `git diff HEAD` does not list
    them and writing a new module is the most common way a suppression arrives.
    """
    counts: dict[str, int] = {}
    for path, line in pairs:
        if owned(path) or path is None or not path.endswith(PYTHON_SUFFIXES):
            continue
        if not SILENCER.search(line[1:]):
            continue
        if line.startswith("+"):
            counts[path] = counts.get(path, 0) + 1
        elif line.startswith("-"):
            counts[path] = counts.get(path, 0) - 1
    if any(count > 0 for count in counts.values()):
        return True
    for path in untracked:
        if owned(path) or not path.endswith(PYTHON_SUFFIXES):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")[:READ_LIMIT]
        except OSError:
            continue
        if SILENCER.search(text):
            return True
    return False


def collect_evidence() -> list[str]:
    """Return human readable evidence of template friction, newest first."""
    status = git("status", "--porcelain", "-uall", "-z")
    diff = git("diff", "HEAD")
    if status is None or diff is None:
        return []

    pairs = attributed(diff)
    listed = entries(status)
    evidence = []

    # A `copier update` rewrites every template owned path by definition. Do not
    # report the act of taking a new template version as friction with it - a
    # suppression written by hand while resolving an update conflict is still a
    # real finding, and is caught below because it lands in this project's own
    # source rather than in a template owned file.
    updating = any(COPIER_UPDATE.match(line) for _, line in pairs)

    touched = sorted({path for _, path in listed if path.startswith(TEMPLATE_OWNED)})
    if touched and not updating:
        evidence.append(f"template owned files were changed here: {', '.join(touched)}")

    rejects = sorted({path for _, path in listed if path.endswith(".rej")})
    if rejects:
        evidence.append(f"a copier update left rejected hunks behind: {', '.join(rejects)}")

    if added_silencers(pairs, [path for code, path in listed if code == "??"]):
        evidence.append("a '# noqa' or '# type: ignore' was added")

    # Conflict markers are the opposite case: one inside a template owned file
    # is precisely the "the update could not be merged" report worth having.
    if any(
        CONFLICT.match(line)
        for path, line in pairs
        if path is not None and path != CONFLICT_PROSE
    ):
        evidence.append("conflict markers are still in the working tree")

    # `pyproject.toml` is not template owned, but its lint configuration is
    # rendered - so during an update a new ignore entry arrived with the
    # template rather than being chosen here.
    try:
        current = Path("pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        current = None
    silenced = set() if updating else added_ignores(git("show", "HEAD:pyproject.toml"), current)
    if silenced:
        evidence.append(
            "these lint rules joined the ruff ignore list in pyproject.toml: "
            + ", ".join(sorted(silenced))
        )

    return evidence


def added_ignores(before: str | None, after: str | None) -> set[str]:
    """Return the rule codes `[tool.ruff.lint] ignore` gained, comparing two files.

    Reading the table is the whole point. Matching a quoted rule code against
    the diff cannot tell which table it is in, so it fired on `extend-select`,
    which *tightens* linting, on a `[tool.deptry]` entry, and on the
    `per-file-ignores` relaxation for tests that the shipped rules prescribe -
    reporting the project for doing what it was told.

    `per-file-ignores` is deliberately not looked at for that reason. Anything
    unreadable on either side yields no codes, because a suppression that
    cannot be established is not evidence.
    """

    def ignores(source: str | None) -> set[str] | None:
        if source is None:
            return None
        try:
            lint = tomllib.loads(source)["tool"]["ruff"]["lint"]
        except (tomllib.TOMLDecodeError, ValueError, KeyError, TypeError):
            return None
        listed = lint.get("ignore") if isinstance(lint, dict) else None
        if not isinstance(listed, list):
            return set()
        return {code for code in listed if isinstance(code, str)}

    old, new = ignores(before), ignores(after)
    if old is None or new is None:
        return set()
    return new - old


def marker_for(session_id: str) -> Path:
    """Return the once-per-session marker file for a session id."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "", session_id)[:64] or "unknown"
    return Path(tempfile.gettempdir()) / f"cmem-template-feedback-{safe}"


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
