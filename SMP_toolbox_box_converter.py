import tkinter as tk
from tkinter import messagebox
import json
import pyperclip
import re

'''
TODO:
- When generating "seat" parts, if X value is positive, add a "isController": true
- When generating "seat" parts, always add "toneIndex": 1
- When generating "ground_wheel" parts, if Z value is superior to 1.0, add a "turnsWithSteer": true
- When generating "ground_wheel" parts, if X value is negative, add a "isMirrored": true and a "rot": [ 0.0, 180.0, 0.0 ]



'''

def extract_order_and_clean(name: str):
    """Extract optional order number in braces from a name and return (order, cleaned_name).

    Examples:
    - "{1}ground_wheel" -> (1, "ground_wheel")
    - "ground_wheel{2}" -> (2, "ground_wheel")
    - "ground{3}_wheel{2}" -> (3, "ground_wheel")  # first occurrence used
    - "ground_wheel" -> (None, "ground_wheel")
    """
    m = re.search(r"\{(\d+)\}", name)
    order = int(m.group(1)) if m else None
    cleaned = re.sub(r"\{\d+\}", "", name)
    return order, cleaned

def _normalize_smp_lines(data: str):
    """Join lines that are broken across newlines so each entry starts with 'Element|'.

    Some exports split the 4th field (name) onto the next line. We coalesce subsequent
    lines until the next line starting with 'Element|'.
    """
    raw_lines = [ln.strip() for ln in data.strip().splitlines() if ln.strip()]
    normalized = []
    current = ""
    for ln in raw_lines:
        if ln.startswith("Element|"):
            if current:
                normalized.append(current)
            current = ln
        else:
            current += ln  # continue previous line (no extra separator needed)
    if current:
        normalized.append(current)
    return normalized

def parse_smp_toolbox_data_hitbox(data):
    lines = _normalize_smp_lines(data)
    collisions_dict = {}
    group_meta = {}  # name -> {order, first_idx}

    for idx, line in enumerate(lines):
        parts = line.split('|')
        # guard against malformed lines
        if len(parts) < 12:
            continue
        order, variable_name = extract_order_and_clean(parts[3])
        vn_lower = variable_name.lower()
        is_static = vn_lower.startswith("hitbox")
        width = min((float(parts[9].replace(',', '.')) / 16), (float(parts[11].replace(',', '.')) / 16))
        height = float(parts[10].replace(',', '.')) / 16
        pos_x = float(parts[6].replace(',', '.')) / 16
        pos_y = -float(parts[7].replace(',', '.')) / 16
        pos_z = float(parts[8].replace(',', '.')) / 16

        # Build collision; only toggles carry variable fields
        collision = {
            "pos": [pos_z, pos_y, pos_x],
            "width": width,
            "height": height
        }
        if not is_static:
            collision["variableName"] = variable_name
            collision["variableType"] = "toggle"

        if variable_name not in collisions_dict:
            # Determine collisionTypes per rules
            if is_static:
                if vn_lower in ("hitbox_side", "hitbox_floor", "hitbox_floor_2", "hitbox_floor_3", "hitbox_wall", "hitbox_side_2", "hitbox_side_3", "hitbox_side_4"):
                    c_types = ["attack", "vehicle", "entity"]
                elif vn_lower in ("hitbox_block"):
                    c_types = ["block", "vehicle"]
                elif vn_lower in ("hitbox_roof", "hitbox"):
                    c_types = ["block", "attack", "vehicle", "entity"]
                else:
                    # Reasonable default for other static hitboxes
                    c_types = ["block", "attack", "vehicle", "entity"]
            else:
                # Toggle hitboxes: only entity and click
                c_types = ["entity", "click"]

            group = {
                "collisionTypes": c_types,
                "collisions": []
            }
            if not is_static:
                group["applyAfter"] = variable_name

            collisions_dict[variable_name] = group
            group_meta[variable_name] = {"order": order, "first_idx": idx}
        else:
            # Update meta with earliest index and smallest explicit order
            meta = group_meta[variable_name]
            if order is not None and (meta["order"] is None or order < meta["order"]):
                meta["order"] = order
            if idx < meta["first_idx"]:
                meta["first_idx"] = idx
        collisions_dict[variable_name]["collisions"].append(collision)
    # Sort groups by order (1,2,...) then by first appearance for stability; items without order go last
    items = list(collisions_dict.items())
    items.sort(key=lambda kv: ((group_meta[kv[0]]["order"] if group_meta[kv[0]]["order"] is not None else float('inf')), group_meta[kv[0]]["first_idx"]))
    return [v for _, v in items]

def parse_smp_toolbox_data_part(data):
    lines = _normalize_smp_lines(data)
    parts = []  # will hold tuples (order, idx, part)

    for idx, line in enumerate(lines):
        parts_data = line.split('|')
        if len(parts_data) < 15:
            continue
        order, variable_name = extract_order_and_clean(parts_data[3])
        width = float(parts_data[9].replace(',', '.')) / 16
        height = float(parts_data[10].replace(',', '.')) / 16
        depth = float(parts_data[11].replace(',', '.')) / 16
        pos_x = float(parts_data[6].replace(',', '.')) / 16
        pos_y = -float(parts_data[7].replace(',', '.')) / 16
        pos_z = float(parts_data[8].replace(',', '.')) / 16

        # Extract and process rotation
        rot_x = -float(parts_data[14].replace(',', '.'))
        rot_y = float(parts_data[13].replace(',', '.'))
        rot_z = float(parts_data[12].replace(',', '.'))

        max_value = max(width, height, depth)
        types = [name.strip() for name in variable_name.split(',')]

        part = {
            "pos": [pos_z, pos_y, pos_x],
            "maxValue": max_value,
            "types": types
        }
        # Only include rotation if it's not (approximately) zero; covers [-0.0, 0.0, 0.0]
        if not (abs(rot_x) < 1e-9 and abs(rot_y) < 1e-9 and abs(rot_z) < 1e-9):
            part["rot"] = [rot_x, rot_y, rot_z]
        # Special case: ground_wheel mirrored when rotation is 180 deg on any axis
        if any(t == "ground_wheel" for t in types):
            def _is_180(angle: float) -> bool:
                a = angle % 360
                return abs(a - 180.0) < 1e-6
            if _is_180(rot_x) or _is_180(rot_y) or _is_180(rot_z):
                part["isMirrored"] = True
        parts.append((order, idx, part))

    # Sort by order then original index; items without order come after ordered ones
    parts.sort(key=lambda t: ((t[0] if t[0] is not None else float('inf')), t[1]))
    return [p for _, _, p in parts]

def parse_smp_toolbox_data_animation(data):
    lines = _normalize_smp_lines(data)
    animations = []  # will hold tuples (order, idx, animation)

    # Configuration for special cases
    config = {
        "pedal_accel": {"variable": "throttle", "axis": [-20.0, 0.0, 0.0]},
        "gas": {"variable": "throttle", "axis": [-20.0, 0.0, 0.0]},
        "steer": {"variable": "rudder", "axis": [0.0, 0.0, 1.0]},
        "pedal_brake": {"variable": "brake", "axis": [-20.0, 0.0, 0.0]},
        "brake": {"variable": "brake", "axis": [-20.0, 0.0, 0.0]},
        "p_brake": {"variable": "p_brake", "axis": [-30.0, 0.0, 0.0]},
        "shifter": {"variable": "engine_gearshift_1", "axis": [1.0, 0.0, 0.0]},
        "shift": {"variable": "engine_gearshift_1", "axis": [1.0, 0.0, 0.0]},
        "door_boot": {"variable": "door_boot", "axis": [-90.0, 0.0, 0.0], "duration": 15, "forwardsEasing": "easeoutquint", "reverseEasing": "easeincubic", "forwardsStartSound": "iv_tpp:bootopen", "reverseEndSound": "iv_tpp:bootclose"},
        "tailgate": {"variable": "door_boot", "axis": [0.0, 90.0, 0.0], "duration": 15, "forwardsEasing": "easeoutquint", "reverseEasing": "easeincubic", "forwardsStartSound": "iv_tpp:bootopen", "reverseEndSound": "iv_tpp:bootclose"},
        "door_hood": {"variable": "door_hood", "axis": [-90.0, 0.0, 0.0], "duration": 25, "forwardsEasing": "easeoutquint", "reverseEasing": "easeincubic", "forwardsStartSound": "iv_tpp:hoodopen", "reverseStartSound": "iv_tpp:hoodclose"},
        "pedal_clutch": {"variable": "clutch", "axis": [-30.0, 0.0, 0.0], "extra": {"animationType": "visibility", "variable": "engine_isautomatic_1"}},
        "clutch": {"variable": "clutch", "axis": [-30.0, 0.0, 0.0], "extra": {"animationType": "visibility", "variable": "engine_isautomatic_1"}},
    }

    for idx, line in enumerate(lines):
        parts = line.split('|')
        if len(parts) < 12:
            continue
        order, object_name = extract_order_and_clean(parts[3])
        pos_x = float(parts[6].replace(',', '.')) / 16
        pos_y = -float(parts[7].replace(',', '.')) / 16
        pos_z = float(parts[8].replace(',', '.')) / 16

        center_point = [pos_z, pos_y, pos_x]
        animation = {"objectName": object_name, "animations": []}

        # Handle special cases
        handled = False
        for key, value in config.items():
            if key in object_name:
                anim = {
                    "animationType": "rotation",
                    "variable": value["variable"],
                    "centerPoint": center_point,
                    "axis": value["axis"]
                }
                if "duration" in value:
                    anim.update({
                        "duration": value["duration"],
                        "forwardsEasing": value["forwardsEasing"],
                        "reverseEasing": value["reverseEasing"],
                        "forwardsStartSound": value["forwardsStartSound"]
                    })
                    if "reverseEndSound" in value:
                        anim["reverseEndSound"] = value["reverseEndSound"]
                    if "reverseStartSound" in value:
                        anim["reverseStartSound"] = value["reverseStartSound"]
                animation["animations"].append(anim)

                if "extra" in value:
                    animation["animations"].insert(0, value["extra"])
                handled = True
                break

        if handled:
            animations.append((order, idx, animation))
            continue

        # Handle doors
        if object_name.startswith(("doorF", "doorR", "door", "door_f", "door_r", "door_")):
            # Special case: names like door_fl_top -> applyAfter door_fl (no separate rotation)
            if object_name.startswith("door_"):
                name_parts = object_name.split("_")
                if len(name_parts) >= 3:
                    base_root = "_".join(name_parts[:2])  # e.g., door_fl
                    animation.update({"applyAfter": base_root})
                    animations.append((order, idx, animation))
                    continue
            direction = "left" if "l" in object_name[-2:] else "right"
            axis = [0.0, -60.0, 0.0] if direction == "left" else [0.0, 60.0, 0.0]
            anim = {
                "animationType": "rotation",
                "variable": object_name.lower(),
                "centerPoint": center_point,
                "axis": axis,
                "duration": 15,
                "forwardsEasing": "easeoutback",
                "reverseEasing": "easeincubic",
                "forwardsStartSound": "iv_tpp:dooropen",
                "reverseEndSound": "iv_tpp:doorclose"
            }
            animation["animations"].append(anim)

        # Handle windows
        elif object_name.startswith("window_"):
            apply_after = object_name.replace("window_", "")
            # Special case: window_door_fr_top -> applyAfter door_fr
            if apply_after.startswith("door_"):
                segs = apply_after.split("_")
                if len(segs) >= 3:
                    apply_after = "_".join(segs[:2])
            animation.update({"applyAfter": apply_after})
            animations.append((order, idx, animation))
            continue  # Skip default case for windows

        # Default case
        if not animation["animations"]:
            animation.update({"applyAfter": object_name})

        animations.append((order, idx, animation))

    # Sort by order then original index
    animations.sort(key=lambda t: ((t[0] if t[0] is not None else float('inf')), t[1]))
    return [a for _, _, a in animations]


def generate_hitbox_json():
    data = text_entry.get("1.0", tk.END)
    try:
        json_data = parse_smp_toolbox_data_hitbox(data)
        json_str = json.dumps(json_data, indent=4)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, json_str)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def generate_part_json():
    data = text_entry.get("1.0", tk.END)
    try:
        json_data = parse_smp_toolbox_data_part(data)
        json_str = json.dumps(json_data, indent=4)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, json_str)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def generate_animation_json():
    data = text_entry.get("1.0", tk.END)
    try:
        json_data = parse_smp_toolbox_data_animation(data)
        json_str = json.dumps(json_data, indent=4)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, json_str)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def copy_to_clipboard():
    json_str = output_text.get("1.0", tk.END)
    pyperclip.copy(json_str)
    messagebox.showinfo("Copied", "JSON object copied to clipboard")

# Create the main window
root = tk.Tk()
root.title("Collision Generator")

# Create and place the widgets
tk.Label(root, text="Paste SMP Toolbox data:").pack()
text_entry = tk.Text(root, height=10, width=80)
text_entry.pack()

generate_hitbox_button = tk.Button(root, text="Generate Hitbox JSON", command=generate_hitbox_json)
generate_hitbox_button.pack()

generate_part_button = tk.Button(root, text="Generate Part JSON", command=generate_part_json)
generate_part_button.pack()

generate_animation_button = tk.Button(root, text="Generate Animation JSON", command=generate_animation_json)
generate_animation_button.pack()

output_text = tk.Text(root, height=10, width=80)
output_text.pack()

copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack()

# Run the application
root.mainloop()