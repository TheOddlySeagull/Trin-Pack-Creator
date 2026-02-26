import argparse
import json
from pathlib import Path


def collect_item_pngs(assets_dir: Path) -> list[Path]:
    png_files: list[Path] = []
    for pack_dir in assets_dir.iterdir():
        if not pack_dir.is_dir():
            continue

        items_dir = pack_dir / "textures" / "items"
        if not items_dir.exists() or not items_dir.is_dir():
            continue

        png_files.extend(path for path in items_dir.rglob("*.png") if path.is_file())
        png_files.extend(path for path in items_dir.rglob("*.PNG") if path.is_file())

    return sorted(set(png_files))


def build_model_json(pack_id: str, texture_path: str) -> dict:
    return {
        "parent": "mts:item/basic",
        "textures": {
            "layer0": f"{pack_id}:{texture_path}",
        },
    }


def generate_models(base_path: Path) -> tuple[int, int]:
    assets_dir = base_path / "mccore" / "src" / "main" / "resources" / "assets"
    output_dir = assets_dir / "mts" / "models" / "item"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not assets_dir.exists():
        raise FileNotFoundError(f"Assets directory not found: {assets_dir}")

    png_files = collect_item_pngs(assets_dir)

    written_count = 0
    for png_path in png_files:
        try:
            pack_id = png_path.relative_to(assets_dir).parts[0]
        except (ValueError, IndexError):
            continue

        texture_name = png_path.stem
        textures_root = assets_dir / pack_id / "textures"
        texture_path = png_path.relative_to(textures_root).with_suffix("").as_posix()
        model_name = f"{pack_id}.{texture_name}.json"
        model_path = output_dir / model_name

        model_data = build_model_json(pack_id, texture_path)
        model_path.write_text(json.dumps(model_data, separators=(",", ":")), encoding="utf-8")
        written_count += 1

    return len(png_files), written_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate item model JSON files from assets/*/textures/items PNG textures."
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Project root path. Defaults to this script's directory.",
    )
    args = parser.parse_args()

    scanned, written = generate_models(args.base_path.resolve())
    print(f"Scanned {scanned} PNG texture(s), wrote {written} model JSON file(s).")


if __name__ == "__main__":
    main()
