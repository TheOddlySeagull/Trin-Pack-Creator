import tkinter as tk
from tkinter import messagebox
import json
import pyperclip

def parse_smp_toolbox_data(data):
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

def generate_json():
    data = text_entry.get("1.0", tk.END)
    try:
        json_data = parse_smp_toolbox_data(data)
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

generate_button = tk.Button(root, text="Generate JSON", command=generate_json)
generate_button.pack()

output_text = tk.Text(root, height=10, width=80)
output_text.pack()

copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack()

# Run the application
root.mainloop()