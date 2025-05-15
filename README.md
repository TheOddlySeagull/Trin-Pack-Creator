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
Run the script directly to process images in the specified base path.

---

### 3. `hex_scanner.py`
Extracts all unique hexadecimal color codes from a PNG image. Useful for configuring the specular map dictionary in `generate_specular_maps.py`.

#### Features
- Reads an image and extracts all unique colors in hexadecimal format.
- Outputs the colors in sorted order.

#### Usage
Run the script and provide the path to the image file when prompted.

---

### 4. `collision_generator.py` (Rename Pending)
Provides a GUI for generating JSON data for hitboxes and parts based on input from the SMP Toolbox. It allows users to create collision and part definitions for vehicles.

#### Features
- Parses SMP Toolbox data to generate hitbox and part JSON objects.
- Includes a GUI for easy input and output.
- Allows copying the generated JSON to the clipboard.

#### Usage
Run the script to open the GUI and paste the SMP Toolbox data for processing.

---

### 5. `upholstery_conversion.py`
Replaces outdated crafting ingredients in vehicle JSON files with new elements introduced in recent updates. This script is specific to Trin's workflow.

---

## Additional Tools in `Trin Online Configurator`
The `Trin Online Configurator` folder contains additional tools for texture generation and customization. See its [README](./Trin%20Online%20Configurator/README.md) for more details.

---

## Notes
- Ensure that the required dependencies (e.g., `Pillow`, `pyperclip`) are installed before running the scripts.
- Each script includes error handling and logs progress or issues to the console.

## License
This project is licensed under the MIT License.