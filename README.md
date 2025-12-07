# Trin Pack Creator

The Trin Pack Creator is a collection of Python scripts designed to streamline the creation and customization of vehicle packs for the Immersive Vehicles mod in Minecraft. Trin is one of the largest and most recognized vehicle packs in the community, and these tools reflect the specific needs of its workflow.

## Context
Immersive Vehicles is a Minecraft mod that allows players to add custom vehicles to the game using JSON definitions. Trin Pack Creator simplifies and automates many of the tasks involved in creating and maintaining these JSON files, as well as generating textures and other assets.

## Scripts Overview

### 1. `vehicle_damager.py`
Adds a "totaled" animation to all vehicle JSON files, simulating a destroyed and crashed effect when vehicles reach 0 health. Randomizes the rotation of movable parts like doors, hoods, and tailgates.

#### How It Works
1. **Command Line Argument Parsing**: The script uses the `argparse` module to parse the folder path from the command line.
2. **File Iteration**: It iterates through each JSON file in the specified folder and its subfolders.
3. **Animation Addition**: For each JSON file, it reads the file, checks if a "damage_totaled" animation exists, and if not, adds a new animation with a random rotation axis.
4. **File Saving**: The modified JSON file is saved back to its original location.

#### Usage
```sh
python vehicle_damager.py --folder_path path/to/your/folder
```

---

### 2. `generate_specular_maps.py`
Generates grayscale variants of vehicle skins to support shaders, enabling specularity effects. Works in tandem with `hex_scanner.py`.

#### Features
- Converts images to specular maps using a color mapping.
- Supports multithreading for faster processing.
- Cleans up orphaned specular maps.

#### Usage
Run the script with the following optional arguments:

- `--base-path`: Specify the base path for assets (required).
- `--noise-tolerance`: Set the tolerance for noise in color matching (default: 0).
- `--override-existing`: Override existing specular maps.
- `--use-multithreading`: Enable multithreading for faster processing.

Example:

```sh
python generate_specular_maps.py --base-path path/to/your/assets --noise-tolerance 5 --override-existing --use-multithreading
```

---

### 3. `hex_scanner.py`
Extracts all unique hexadecimal color codes from a PNG image. Useful for configuring the specular map dictionary in `generate_specular_maps.py`.

#### Features
- Reads an image and extracts all unique colors in hexadecimal format.
- Outputs the colors in sorted order.

#### Usage
Run the script and provide the path to the image file when prompted.

---

### 4. `SMP_toolbox_box_converter.py`
GUI tool that converts SMP Toolbox exports into Immersive Vehicles JSON snippets for hitboxes, parts, and animations.

#### Features
- Hitboxes: groups collisions by variable name, sets standard `collisionTypes`, and applies `applyAfter` automatically.
- Parts: generates `pos`, `rot`, `maxValue`, and `types` from SMP Toolbox box data.
- Animations: supports pedals, steering, shifter, hood/boot/tailgate (with durations, easing, and sounds), door left/right hinge logic, window passthrough (`applyAfter`), plus a sensible default when no special rule matches.
- Simple GUI with buttons to generate each JSON type and a one-click “Copy to Clipboard”.

#### Usage
1. Run the script to open the GUI.
2. Paste the SMP Toolbox data (pipe-separated lines) into the input box.
3. Click one of:
	- “Generate Hitbox JSON”
	- “Generate Part JSON”
	- “Generate Animation JSON”
4. Use “Copy to Clipboard” to copy the output.

Dependencies: requires `pyperclip` (install with `pip install pyperclip`). `tkinter` ships with most Python distributions on Windows.

---

### 5. `upholstery_conversion.py`
Replaces outdated crafting ingredients in vehicle JSON files with new elements introduced in recent updates. This script is specific to Trin's workflow.

---

### 6. `add_bodyroll_visibility.py`
Adds a visibility animation to bodyroll variable modifiers (`rlBodyroll`, `rrBodyroll`, `flBodyroll`, `frBodyroll`) in vehicle JSONs. The animation makes bodyroll parts visible only when the engine is running.

#### How It Works
- Scans JSON files under a provided root path.
- For each `variableModifiers` entry matching the bodyroll variables, appends a `visibility` animation targeting `engine_running_1` when none exists.

#### Usage
```sh
python add_bodyroll_visibility.py path/to/assets_root
```

---

### 7. `add_tow_flatbed.py`
Adds missing `tow_flatbed` connection entries to vehicle JSONs based on existing `tow_wheel` and `tow_bumper` connections in the `HOOKUP` connection group.

#### Features
- Derives `pos[1]` (Y) from the first non-heavy `tow_wheel` connection.
- Derives `pos[2]` (Z) from the maximum among non-heavy `tow_bumper` connections.
- Skips any heavy variants and files already containing `tow_flatbed`.
- Supports dry-run, backups, strict error handling, and file limits.

#### Usage
```sh
python add_tow_flatbed.py path/to/assets_root --dry-run
python add_tow_flatbed.py path/to/assets_root --backup-ext .bak
python add_tow_flatbed.py path/to/assets_root --strict
```

---

### 8. `validate_json.py`
Validates JSON files recursively. By default, tolerates common asset-style comments (`//`, `/* */`). Enable strict mode to enforce standard JSON.

#### Usage
```sh
python validate_json.py path/to/assets_root
python validate_json.py path/to/assets_root --no-comments   # strict RFC JSON
python validate_json.py path/to/assets_root --glob "*.mcmeta" --quiet
```

---

## Additional Tools in `Trin Online Configurator`
The `Trin Online Configurator` folder contains additional tools for texture generation and customization. See its [README](./Trin%20Online%20Configurator/README.md) for more details.

---

## Notes
- Ensure that the required dependencies (e.g., `Pillow`, `pyperclip`) are installed before running the scripts.
- Each script includes error handling and logs progress or issues to the console.

## License
This project is licensed under the MIT License.