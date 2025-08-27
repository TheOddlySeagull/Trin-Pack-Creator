import tkinter as tk
from tkinter import messagebox
import json
import pyperclip

def parse_smp_toolbox_data_hitbox(data):
    lines = data.strip().split('\n')
    collisions_dict = {}

    for line in lines:
        parts = line.split('|')
        variable_name = parts[3]
        width = min((float(parts[9].replace(',', '.')) / 16), (float(parts[11].replace(',', '.')) / 16))
        height = float(parts[10].replace(',', '.')) / 16
        pos_x = float(parts[6].replace(',', '.')) / 16
        pos_y = -float(parts[7].replace(',', '.')) / 16
        pos_z = float(parts[8].replace(',', '.')) / 16

        collision = {
            "pos": [pos_z, pos_y, pos_x],
            "width": width,
            "height": height,
            "variableName": variable_name,
            "variableType": "toggle"
        }

        if variable_name not in collisions_dict:
            collisions_dict[variable_name] = {
                "isInterior": True,
                "collisions": [],
                "animations": []
            }
        collisions_dict[variable_name]["collisions"].append(collision)

    return list(collisions_dict.values())

def parse_smp_toolbox_data_part(data):
    lines = data.strip().split('\n')
    parts = []

    for line in lines:
        parts_data = line.split('|')
        variable_name = parts_data[3]
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
            "rot": [rot_x, rot_y, rot_z],
            "maxValue": max_value,
            "types": types
        }
        parts.append(part)

    return parts

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

output_text = tk.Text(root, height=10, width=80)
output_text.pack()

copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack()

# Run the application
root.mainloop()