#!/usr/bin/env python3
"""Entry for make.fun bounty: seventeen syllables of debugging.

A haiku about debugging, in strict 5-7-5 form, at most 200 characters:

    Breakpoint holds its breath
    the log swears the bug is gone
    the bug just moved house

Writes the haiku to the output directory (``/output/entry.txt`` by
default, or ``$MAKEFUN_OUTPUT`` when set).

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import re

ENTRY = (
    "Breakpoint holds its breath\n"
    "the log swears the bug is gone\n"
    "the bug just moved house"
)

EXPECTED_SYLLABLES = (5, 7, 5)
MAX_CHARS = 200

# Exact syllable counts for every word in the entry, so validation is
# deterministic and does not depend on a heuristic guess.
SYLLABLES = {
    "breakpoint": 2,
    "holds": 1,
    "its": 1,
    "breath": 1,
    "the": 1,
    "log": 1,
    "swears": 1,
    "bug": 1,
    "is": 1,
    "gone": 1,
    "just": 1,
    "moved": 1,
    "house": 1,
}


def count_syllables(word: str) -> int:
    """Count syllables in one word (lookup first, vowel groups as fallback)."""
    key = word.lower().strip(".,;:!?")
    if key in SYLLABLES:
        return SYLLABLES[key]
    groups = re.findall(r"[aeiouy]+", key)
    count = len(groups)
    if key.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def line_syllables(line: str) -> int:
    """Total syllables in one line."""
    return sum(count_syllables(word) for word in line.split())


def validate(text: str) -> None:
    """The entry must be 3 lines in 5-7-5 form, at most 200 characters."""
    if not text:
        raise ValueError("entry must not be empty")
    if len(text) > MAX_CHARS:
        raise ValueError(f"entry must be at most {MAX_CHARS} characters, got {len(text)}")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    lines = text.split("\n")
    if len(lines) != 3:
        raise ValueError(f"entry must be exactly 3 lines, got {len(lines)}")
    for i, (line, expected) in enumerate(zip(lines, EXPECTED_SYLLABLES), start=1):
        if not line:
            raise ValueError(f"line {i} must not be blank")
        if line != line.strip():
            raise ValueError(f"line {i} must not start or end with whitespace: {line!r}")
        got = line_syllables(line)
        if got != expected:
            raise ValueError(f"line {i} must have {expected} syllables, got {got}: {line!r}")


def resolve_out_path() -> str:
    """Resolve the output file path.

    ``$MAKEFUN_OUTPUT`` may point at a directory (``entry.txt`` is written
    inside it) or directly at a file (used as-is); the default is
    ``/output/entry.txt``, falling back to ``./output/entry.txt``.
    """
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output/entry.txt"
    if requested.endswith(".txt"):
        # A file path is used as-is only if its parent directory is writable;
        # otherwise fall back to ./output/entry.txt instead of failing.
        parent = os.path.dirname(requested) or "."
        try:
            os.makedirs(parent, exist_ok=True)
            probe = os.path.join(parent, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(probe)
        except OSError:
            return os.path.join(os.getcwd(), "output", "entry.txt")
        return requested
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return os.path.join(requested, "entry.txt")
    except OSError:
        return os.path.join(os.getcwd(), "output", "entry.txt")


def main() -> int:
    validate(ENTRY)
    path = resolve_out_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(ENTRY)
    # Verify the written file by reading it back: it must match byte for
    # byte, re-validate against the competition limits, and keep the exact
    # 3-line, 5-7-5 shape (catches newline translation or truncation).
    with open(path, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    if written != ENTRY:
        raise RuntimeError("verification failed: written entry does not match")
    if len(written.encode("utf-8")) != len(ENTRY.encode("utf-8")):
        raise RuntimeError("verification failed: written entry byte length differs")
    validate(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
