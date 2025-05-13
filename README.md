# Trin Pack Creator

This repository contains a collection of Python scripts designed to assist with various tasks related to JSON file processing, image manipulation, and data generation. Below is an overview of each script and its functionality.

## Scripts Overview

### 1. `vehicle_damager.py`

This script adds "damaged" animations to JSON files representing vehicles. It processes all JSON files in a specified folder and its subfolders, adding a new animation for total damage if it does not already exist.

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

This script generates specular maps for images by mapping pixel colors based on a predefined color map. It supports multithreading for faster processing and includes options to exclude certain files or directories.

#### Features

- Converts images to specular maps using a color mapping.
- Supports multithreading for faster processing.
- Cleans up orphaned specular maps.

#### Usage

Run the script directly to process images in the specified base path.

---

### 3. `hex_scanner.py`

This script extracts unique hexadecimal color codes from an image file.

#### Features

- Reads an image and extracts all unique colors in hexadecimal format.
- Outputs the colors in sorted order.

#### Usage

Run the script and provide the path to the image file when prompted.

---

### 4. `collision_generator.py`

This script provides a GUI for generating JSON data for hitboxes and parts based on input from the SMP Toolbox.

#### Features

- Parses SMP Toolbox data to generate hitbox and part JSON objects.
- Includes a GUI for easy input and output.
- Allows copying the generated JSON to the clipboard.

#### Usage

Run the script to open the GUI and paste the SMP Toolbox data for processing.

---

## Notes

- Ensure that the required dependencies (e.g., `Pillow`, `pyperclip`) are installed before running the scripts.
- Each script includes error handling and logs progress or issues to the console.

## License

This project is licensed under the MIT License.