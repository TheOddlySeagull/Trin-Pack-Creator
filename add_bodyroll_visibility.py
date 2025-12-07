import argparse
import json
import os
from typing import Any, Dict, List


TARGET_VARIABLES = {"rlBodyroll", "rrBodyroll", "flBodyroll", "frBodyroll"}
VISIBILITY_SNIPPET = {
    "animationType": "visibility",
    "variable": "engine_running_1",
    "clampMin": 1.0,
    "clampMax": 1.0,
}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    # Preserve a readable, consistent formatting without trailing spaces.
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")


def ensure_visibility_animation(modifier: Dict[str, Any]) -> bool:
    """
    Returns True if a visibility animation was added; False otherwise.
    """
    animations = modifier.get("animations")
    if not isinstance(animations, list):
        return False

    # Check if visibility already exists.
    for anim in animations:
        if isinstance(anim, dict) and anim.get("animationType") == "visibility":
            return False  # Already implemented

    # Optional: verify translations are present (not strictly needed to add visibility)
    # translation_found = any(
    #     isinstance(anim, dict) and anim.get("animationType") == "translation" for anim in animations
    # )

    # Append the visibility animation at the end.
    animations.append(dict(VISIBILITY_SNIPPET))
    return True


def process_file(path: str) -> bool:
    try:
        data = load_json(path)
    except Exception:
        return False

    if not isinstance(data, dict):
        return False

    modifiers = data.get("variableModifiers")
    if not isinstance(modifiers, list):
        return False

    changed = False
    for modifier in modifiers:
        if not isinstance(modifier, dict):
            continue
        var_name = modifier.get("variable")
        if var_name in TARGET_VARIABLES:
            if ensure_visibility_animation(modifier):
                changed = True

    if changed:
        try:
            save_json(path, data)
            return True
        except Exception:
            return False
    return False


def iter_json_files(root: str) -> List[str]:
    paths: List[str] = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith(".json"):
                paths.append(os.path.join(dirpath, name))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Recursively add bodyroll visibility animations to vehicle JSON files."
        )
    )
    parser.add_argument(
        "root",
        help="Root folder to scan recursively for .json files",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    files = iter_json_files(root)

    modified = 0
    skipped = 0
    for path in files:
        if process_file(path):
            print(f"Modified: {path}")
            modified += 1
        else:
            skipped += 1

    print(f"Done. Modified {modified} files. Skipped {skipped} files.")


if __name__ == "__main__":
    main()
