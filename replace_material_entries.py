import argparse
import json
from pathlib import Path
from typing import Any


def load_mapping(mapping_path: Path) -> dict[str, list[str]]:
    with mapping_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    replacements = payload.get("replacements", {})
    normalized: dict[str, list[str]] = {}
    for source, target in replacements.items():
        if isinstance(target, str):
            normalized[source] = [target]
        elif isinstance(target, list) and all(isinstance(entry, str) for entry in target):
            normalized[source] = target
        else:
            raise ValueError(
                f"Invalid mapping for '{source}'. Expected string or list of strings."
            )
    return normalized


def replace_in_json_node(node: Any, replacements: dict[str, list[str]]) -> tuple[Any, int]:
    replacement_count = 0

    if isinstance(node, dict):
        updated: dict[str, Any] = {}
        for key, value in node.items():
            updated_value, child_count = replace_in_json_node(value, replacements)
            updated[key] = updated_value
            replacement_count += child_count
        return updated, replacement_count

    if isinstance(node, list):
        updated_list: list[Any] = []
        for item in node:
            if isinstance(item, str) and item in replacements:
                updated_list.extend(replacements[item])
                replacement_count += 1
                continue

            updated_item, child_count = replace_in_json_node(item, replacements)
            updated_list.append(updated_item)
            replacement_count += child_count
        return updated_list, replacement_count

    return node, replacement_count


def process_file(file_path: Path, replacements: dict[str, list[str]], dry_run: bool) -> int:
    with file_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    updated_data, replacements_done = replace_in_json_node(data, replacements)

    if replacements_done > 0 and not dry_run:
        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(updated_data, handle, indent=4, ensure_ascii=False)
            handle.write("\n")

    return replacements_done


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace exact JSON list entries using a mapping file (supports 1-to-many)."
    )
    parser.add_argument(
        "--target",
        default="./mccore/src/main/resources/assets/iv_tcp_v3_civil/jsondefs/vehicles",
        help="Directory to scan for JSON files.",
    )
    parser.add_argument(
        "--mapping",
        default="./paint_replacements.json",
        help="Path to JSON mapping file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would be changed without writing files.",
    )
    parser.add_argument(
        "--pattern",
        default="*.json",
        help="Glob pattern for files inside target directory.",
    )
    args = parser.parse_args()

    target_dir = Path(args.target).resolve()
    mapping_file = Path(args.mapping).resolve()

    if not target_dir.exists() or not target_dir.is_dir():
        raise FileNotFoundError(f"Target directory not found: {target_dir}")
    if not mapping_file.exists() or not mapping_file.is_file():
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")

    replacements = load_mapping(mapping_file)

    files_scanned = 0
    files_changed = 0
    total_replacements = 0

    for file_path in target_dir.rglob(args.pattern):
        if not file_path.is_file():
            continue

        files_scanned += 1
        replacements_done = process_file(file_path, replacements, args.dry_run)

        if replacements_done > 0:
            files_changed += 1
            total_replacements += replacements_done
            action = "Would update" if args.dry_run else "Updated"
            print(f"{action}: {file_path} ({replacements_done} replacements)")

    mode = "Dry run" if args.dry_run else "Run"
    print(
        f"{mode} complete. Scanned {files_scanned} files, "
        f"changed {files_changed}, total replacements {total_replacements}."
    )


if __name__ == "__main__":
    main()
