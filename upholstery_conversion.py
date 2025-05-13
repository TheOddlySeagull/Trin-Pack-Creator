import os
import json
import math

# === Define your wool-to-upholstery mapping ===
WOOL_TO_UPHOLSTERY = {
    frozenset(["minecraft:wool:7", "minecraft:wool:8"]): "gray",
    frozenset(["minecraft:wool:4", "minecraft:wool:0"]): "tan",
    frozenset(["minecraft:wool:7", "minecraft:wool:14"]): "red",
    frozenset(["minecraft:wool:15", "minecraft:wool:14"]): "red",
    frozenset(["minecraft:wool:8", "minecraft:wool:0"]): "white",
    frozenset(["minecraft:wool:12", "minecraft:wool:7"]): "brown"
}

UPHOLSTERY_PREFIX = "mts:iv_tpp.upholstery_pile_"

def identify_upholstery(materials):
    wool_counts = {}
    for item in materials:
        parts = item.split(":")
        if len(parts) == 4 and parts[0] == "minecraft" and parts[1] == "wool":
            key = f"{parts[0]}:{parts[1]}:{parts[2]}"
            count = int(parts[3])
            wool_counts[key] = wool_counts.get(key, 0) + count
    if not wool_counts:
        return None, None

    key_set = frozenset(wool_counts.keys())
    upholstery_color = WOOL_TO_UPHOLSTERY.get(key_set)

    if not upholstery_color:
        print(f"[WARN] Unknown wool combination: {key_set}")
        return None, None

    total_wool = sum(wool_counts.values())
    upholstery_count = math.ceil(total_wool / 2)

    return upholstery_color, upholstery_count

def update_material_list(materials):
    upholstery_color, upholstery_count = identify_upholstery(materials)
    if not upholstery_color:
        return materials  # No change

    new_materials = [
        item for item in materials
        if not (item.startswith("minecraft:wool"))
    ]

    new_materials.append(f"{UPHOLSTERY_PREFIX}{upholstery_color}:0:{upholstery_count}")
    return new_materials

def process_json_file(path, out_path=None):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False

    if "definitions" in data:
        for definition in data["definitions"]:
            if "extraMaterialLists" in definition:
                for i, material_list in enumerate(definition["extraMaterialLists"]):
                    updated_list = update_material_list(material_list)
                    if updated_list != material_list:
                        definition["extraMaterialLists"][i] = updated_list
                        changed = True

    if changed:
        out_file = out_path or path
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[OK] Updated: {os.path.basename(path)}")
    else:
        print(f"[--] No change: {os.path.basename(path)}")

def batch_process_folder(folder_path, output_folder=None):
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):
                in_path = os.path.join(root, filename)
                if output_folder:
                    relative_path = os.path.relpath(root, folder_path)
                    out_dir = os.path.join(output_folder, relative_path)
                    os.makedirs(out_dir, exist_ok=True)
                    out_path = os.path.join(out_dir, filename)
                else:
                    out_path = None
                process_json_file(in_path, out_path)

# === Usage Example ===
if __name__ == "__main__":
    input_folder = "E:/Documents Global/Programmation/Trin/NOT TRIN/immersive_vehicles_vanity/mccore/src/main/resources/assets/ivv/jsondefs_base_ivlabs/jsondefs/skins/trin"
    output_folder = "E:/Documents Global/Programmation/Trin/NOT TRIN/immersive_vehicles_vanity/mccore/src/main/resources/assets/ivv/jsondefs_base_ivlabs/jsondefs/skins/trin"

    os.makedirs(output_folder, exist_ok=True)
    batch_process_folder(input_folder, output_folder)
