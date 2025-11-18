#!/usr/bin/env python3
"""Recursively validate JSON files under a directory.

Defaults to tolerating comments (// and /* */) commonly found in asset JSONs.
Use --no-comments for strict RFC 8259 JSON validation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List


COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def strip_json_comments(text: str) -> str:
    # Remove block comments first
    text = COMMENT_BLOCK_RE.sub("", text)
    # Remove line comments // outside of strings
    out_lines: List[str] = []
    for line in text.splitlines():
        if "//" not in line:
            out_lines.append(line)
            continue
        new_line_chars: List[str] = []
        in_string = False
        escape = False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '"' and not escape:
                in_string = not in_string
            if not in_string and ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                # start of line comment outside string
                break
            new_line_chars.append(ch)
            if ch == '\\' and not escape:
                escape = True
            else:
                escape = False
            i += 1
        out_lines.append(''.join(new_line_chars))
    return "\n".join(out_lines)


def validate_file(path: Path, allow_comments: bool) -> tuple[bool, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"read error: {e}"
    data = raw
    if allow_comments:
        data = strip_json_comments(raw)
    try:
        json.loads(data)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON error at line {e.lineno}, column {e.colno}: {e.msg}"
    except Exception as e:
        return False, f"parse error: {e}"


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description="Validate JSON files recursively")
    p.add_argument("root", help="Root directory to scan")
    p.add_argument("--no-comments", action="store_true", help="Disable comment stripping (strict JSON)")
    p.add_argument("--glob", default="*.json", help="Glob pattern for files (default: *.json)")
    p.add_argument("--quiet", "-q", action="store_true", help="Only print summary")
    p.add_argument("--fail-fast", action="store_true", help="Exit on first error with non-zero code")
    args = p.parse_args(argv)

    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        print(f"[ERROR] Not a directory: {root}")
        return 2

    files = sorted(root.rglob(args.glob))
    if not args.quiet:
        print(f"[INFO] Validating {len(files)} files under {root}")

    ok_count = 0
    err_count = 0
    for f in files:
        valid, err = validate_file(f, allow_comments=not args.no_comments)
        if valid:
            ok_count += 1
            if not args.quiet:
                print(f"OK   {f}")
        else:
            err_count += 1
            print(f"FAIL {f}: {err}")
            if args.fail_fast:
                print(f"[SUMMARY] OK: {ok_count}  FAIL: {err_count}")
                return 1

    print(f"[SUMMARY] OK: {ok_count}  FAIL: {err_count}")
    return 0 if err_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
