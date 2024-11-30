# Vehicle Damager

`vehicle_damager.py` is a script that adds "damaged" animations to JSON files representing vehicles. It processes all JSON files in a specified folder and its subfolders, adding a new animation for total damage if it does not already exist.

## How It Works

1. **Command Line Argument Parsing**: The script uses the `argparse` module to parse the folder path from the command line.
2. **File Iteration**: It iterates through each JSON file in the specified folder and its subfolders.
3. **Animation Addition**: For each JSON file, it reads the file, checks if a "damage_totaled" animation exists, and if not, adds a new animation with a random rotation axis.
4. **File Saving**: The modified JSON file is saved back to its original location.

## Usage

1. **Clone the Repository**: Clone the repository to your local machine.
2. **Navigate to the Directory**: Open a terminal and navigate to the directory containing `vehicle_damager.py`.
3. **Run the Script**: Execute the script with the folder path containing the JSON files as an argument.

```sh
python vehicle_damager.py --folder_path path/to/your/folder
```

### Example

```sh
python vehicle_damager.py --folder_path input/iv_tvpr_civil/vehicles
```

This command will process all JSON files in the `input/iv_tvpr_civil/vehicles` folder and its subfolders, adding "damaged" animations where necessary.

## Notes

- Ensure that the folder path is correctly specified and accessible.
- The script will print messages to the console indicating the progress and any errors encountered.

## License

This project is licensed under the MIT License.