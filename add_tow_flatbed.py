#!/usr/bin/env python3
"""Add missing tow_flatbed connection entries to vehicle JSON definition files.

Rules:
 - Recursively scan a provided assets root directory for *.json files.
 - For each file, parse JSON (tolerates // and /* */ comments).
 - Locate the HOOKUP connection group inside "connectionGroups".
 - If a non-heavy "tow_flatbed" already exists, skip file.
 - Otherwise derive Y from the first non-heavy "tow_wheel" connection pos[1].
 - Derive Z from the maximum pos[2] among non-heavy "tow_bumper" connections.
 - Insert new connection: {"type": "tow_flatbed", "pos": [0.0, Y, Z], "distance": 2.0}.
 - Skip any *_heavy variants entirely (tow_bumper_heavy, tow_wheel_heavy, tow_flatbed_heavy).
 - Create an optional backup of modified files.

Edge cases handled:
 - Missing HOOKUP group: file skipped with warning.
 - Missing tow_wheel: cannot derive Y; file skipped.
 - Missing tow_bumper: cannot derive Z; file skipped.
 - Non-standard formatting or comments: stripped before json.loads.

Exit code is 0 even if some files are skipped; failures parsing raise warnings unless --strict.
"""

from __future__ import annotations

import argparse
import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
COMMENT_LINE_RE = re.compile(r"(?m)(^|\s)//.*?$")


def strip_json_comments(text: str) -> str:
    """Remove // line comments and /* */ block comments from JSON-like text.
    Attempts to avoid stripping sequences inside string literals by a simplistic approach:
    It first removes block comments, then line comments not inside quotes.
    This is not a perfect JSON-with-comments parser but should suffice for typical asset files.
    """
    # Remove block comments
    text = COMMENT_BLOCK_RE.sub("", text)

    # For line comments, we process line by line and skip if inside quotes roughly.
    cleaned_lines: List[str] = []
    for line in text.splitlines():
        # Quick heuristic: if '//' appears, remove from first occurrence not inside a quoted string.
        if "//" in line:
            new_line = []
            in_string = False
            escape = False
            i = 0
            while i < len(line):
                ch = line[i]
                if ch == '"' and not escape:
                    in_string = not in_string
                if not in_string and ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    # start of comment outside string
                    break
                new_line.append(ch)
                escape = (ch == '\\' and not escape)
                if ch != '\\':
                    escape = False if escape else escape
                i += 1
            cleaned_lines.append(''.join(new_line))
        else:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Cannot read {path}: {e}")
        return None
    stripped = strip_json_comments(raw)
    try:
        return json.loads(stripped)
    except Exception as e:
        print(f"[WARN] JSON parse failed for {path}: {e}")
        return None


def find_hookup_group(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    groups = data.get("connectionGroups")
    if not isinstance(groups, list):
        return None
    for g in groups:
        if isinstance(g, dict) and g.get("groupName") == "HOOKUP":
            return g
    return None


def connection_has_type(conn: Dict[str, Any], type_value: str) -> bool:
    return isinstance(conn, dict) and conn.get("type") == type_value


def already_has_flatbed(hookup: Dict[str, Any]) -> bool:
    connections = hookup.get("connections")
    if not isinstance(connections, list):
        return False
    for c in connections:
        if connection_has_type(c, "tow_flatbed"):
            return True
    return False


def extract_positions(hookup: Dict[str, Any], type_prefix: str) -> List[List[float]]:
    positions: List[List[float]] = []
    connections = hookup.get("connections")
    if not isinstance(connections, list):
        return positions
    for c in connections:
        if not isinstance(c, dict):
            continue
        t = c.get("type")
        if not isinstance(t, str):
            continue
        # Skip heavy variants
        if t.endswith("_heavy"):
            continue
        if t == type_prefix:
            pos = c.get("pos")
            if (isinstance(pos, list) and len(pos) == 3 and
                    all(isinstance(v, (int, float)) for v in pos)):
                positions.append([float(pos[0]), float(pos[1]), float(pos[2])])
    return positions


def add_tow_flatbed(hookup: Dict[str, Any], y_value: float, z_value: float) -> bool:
    connections = hookup.get("connections")
    if not isinstance(connections, list):
        return False
    new_conn = {
        "type": "tow_flatbed",
        "pos": [0.0, y_value, z_value],
        "distance": 2.0
    }
    connections.append(new_conn)
    return True


def process_file(path: Path, write: bool, backup_ext: Optional[str], strict: bool) -> bool:
    data = load_json(path)
    if data is None:
        return False
    hookup = find_hookup_group(data)
    if hookup is None:
        print(f"[SKIP] No HOOKUP group: {path}")
        return False
    if already_has_flatbed(hookup):
        print(f"[SKIP] Already has tow_flatbed: {path}")
        return False
    wheel_positions = extract_positions(hookup, "tow_wheel")
    if not wheel_positions:
        print(f"[SKIP] No non-heavy tow_wheel found: {path}")
        return False
    bumper_positions = extract_positions(hookup, "tow_bumper")
    if not bumper_positions:
        print(f"[SKIP] No non-heavy tow_bumper found: {path}")
        return False
    # Derive Y from first tow_wheel (consistent with requirement)
    y_value = wheel_positions[0][1]
    # Derive Z from maximum Z among tow_bumper
    z_value = max(p[2] for p in bumper_positions)
    changed = add_tow_flatbed(hookup, y_value, z_value)
    if not changed:
        print(f"[FAIL] Could not modify connections: {path}")
        return False
    if write:
        if backup_ext:
            try:
                backup_path = path.with_suffix(path.suffix + backup_ext)
                backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception as e:
                msg = f"[WARN] Backup failed for {path}: {e}"
                if strict:
                    raise RuntimeError(msg)
                print(msg)
        try:
            path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            msg = f"[ERROR] Failed to write {path}: {e}"
            if strict:
                raise RuntimeError(msg)
            print(msg)
            return False
        print(f"[ADDED] tow_flatbed inserted: {path}")
    else:
        print(f"[DRY-RUN] Would add tow_flatbed (Y={y_value}, Z={z_value}): {path}")
    return True


def iter_json_files(root: Path) -> List[Path]:
    return [p for p in root.rglob("*.json") if p.is_file()]


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Add missing tow_flatbed connection entries to vehicle JSONs.")
    parser.add_argument("root", help="Root directory to recursively scan (assets root).")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes, only report.")
    parser.add_argument("--backup-ext", default=".bak", help="Extension for backup copy (set to empty string to disable).")
    parser.add_argument("--strict", action="store_true", help="Raise on errors instead of continuing.")
    parser.add_argument("--limit", type=int, default=0, help="Process only first N JSON files (debug).")
    args = parser.parse_args(argv)

    root_path = Path(args.root).resolve()
    if not root_path.exists():
        print(f"[ERROR] Root path does not exist: {root_path}")
        return 2
    if not root_path.is_dir():
        print(f"[ERROR] Root path is not a directory: {root_path}")
        return 2

    files = iter_json_files(root_path)
    if args.limit > 0:
        files = files[:args.limit]
    print(f"[INFO] Scanning {len(files)} JSON files under {root_path}")

    write_changes = not args.dry_run
    backup_ext = args.backup_ext if args.backup_ext else None

    modified = 0
    for f in files:
        try:
            if process_file(f, write_changes, backup_ext, args.strict):
                modified += 1
        except Exception as e:
            print(f"[ERROR] Exception processing {f}: {e}")
            if args.strict:
                raise
    print(f"[SUMMARY] Modified files: {modified}; Unmodified/skipped: {len(files) - modified}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
