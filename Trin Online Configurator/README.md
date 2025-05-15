# Trin Online Configurator

The `Trin Online Configurator` folder contains tools designed to assist with creating and customizing vehicle textures and configurations for the Immersive Vehicles mod in Minecraft. These tools are tailored to Trin's workflow, one of the largest and most recognized vehicle packs in the community.

## Tools Overview

### 1. `generate_texture_banner.py`
Generates credit banners for vehicle textures, including overlays and fixed color panels. This is useful for creating visually appealing credits with your name, date, and model name.

#### Features
- Adds banners with trim names, creator names, and dates.
- Includes fixed color panels for showcasing interior and exterior details.

#### Usage
Run the script and provide the required image paths and details (e.g., trim name, car name).

---

### 2. `layer_generator.py`
Processes vehicle texture images to generate individual layers for different parts of the vehicle, such as paint, interior, and accents. Supports predefined color mappings for layer extraction.

#### Features
- Extracts layers based on predefined color mappings.
- Generates separate images for each layer.

#### Usage
Place the input images in the `reference` folder and run the script. The output will be saved in the `output` folder.

---

## Notes
- Ensure that the required dependencies (e.g., `Pillow`) are installed before running the scripts.
- Each script includes error handling and logs progress or issues to the console.

## License
This project is licensed under the MIT License.
