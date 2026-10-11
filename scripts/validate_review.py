#!/usr/bin/env python3
"""Fail-closed parser for Hermes Agent's --format stream-json event stream.

Hermes emits a terminal {"type":"result","exit_code":0,"text":"..."} event.
Any missing/ambiguous result or nonzero exit code fails.
"""
import json
import pathlib
import sys


def final_result(path: pathlib.Path) -> tuple[bool, str]:
    completed = []
    try:
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                event = json.loads(line)
                if not isinstance(event, dict):
                    return False, "Non-object Hermes JSONL event"
                if event.get("type") == "result":
                    completed.append(event)
    except (OSError, ValueError, TypeError) as error:
        return False, f"Invalid or missing Hermes JSON stream: {type(error).__name__}"
    if len(completed) != 1:
        return False, f"Expected one terminal Hermes result; found {len(completed)}"
    final = completed[0]
    if final.get("exit_code") != 0 or final.get("error"):
        return False, "Hermes run did not complete successfully"
    text = final.get("text")
    if not isinstance(text, str) or not text.strip():
        return False, "Hermes run ended without a text result"
    return True, text.strip()


def check_run(path: pathlib.Path) -> tuple[bool, str]:
    ok, result = final_result(path)
    return (ok, "Hermes completed successfully" if ok else result)


def check_review(path: pathlib.Path) -> tuple[bool, str]:
    ok, text = final_result(path)
    if not ok:
        return False, text
    if text != "PASS":
        return False, f"Review did not return exact PASS: {text[:250]!r}"
    return True, "Independent Hermes review: PASS"


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: validate_review.py <hermes-stream.jsonl>")
    good, detail = check_review(pathlib.Path(sys.argv[1]))
    print(detail)
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
