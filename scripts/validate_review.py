#!/usr/bin/env python3
"""Fail-closed read-only OpenCode review result checker.

OpenCode emits JSON lines. Never trust free-form logs or stdout regexes for PASS.
"""
import json
import pathlib
import sys


def check_review(path: pathlib.Path) -> tuple[bool, str]:
    parts = []
    failed = False
    try:
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                event_type = entry.get("type")
                if event_type == "error":
                    failed = True
                elif event_type == "text":
                    text = entry.get("part", {}).get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
    except (OSError, ValueError, TypeError) as error:
        return False, f"Invalid or missing OpenCode JSON output: {type(error).__name__}"
    if failed or not parts:
        return False, "Reviewer returned an error or did not produce a final text verdict"
    if parts[-1] != "PASS":
        return False, f"Reviewer did not provide exact PASS (received {parts[-1][:300]!r})"
    return True, "Independent review: PASS"


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: validate_review.py <opencode.jsonl>")
    passed, reason = check_review(pathlib.Path(sys.argv[1]))
    print(reason)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
