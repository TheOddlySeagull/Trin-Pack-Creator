import os
import json
import random
import argparse

# Parse the folder path from the command line
parser = argparse.ArgumentParser(description="Add 'damaged' animations to JSON files or a single JSON file")
parser.add_argument("--folder_path", required=True, help="Path to the folder containing JSON files or a single .json file")
args = parser.parse_args()
folder_path = os.path.normpath(args.folder_path)

# Function to add "damaged" animations to a JSON file
def add_damaged_animation(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    print(f"inside a json file: {json_file}")

    for obj in data["rendering"]["animatedObjects"]:
        print(f"inside an object: {obj['objectName']}")
        #print the number of animations in the object
        print(f"number of animations: {len(obj.get('animations', []))}")
        # if this animation has not already been added
        if not any(anim.get("variable", None) == "damage_totaled" for anim in obj.get("animations", []) ):
            print("damage_totaled animation does not exist")
            # Iterate through each animation in the object
            # Collect new animations first to avoid mutating the list while iterating
            new_animations = []
            for anim in obj.get("animations", []):
                # If animation not of "variable" "damage_totaled"
                if anim.get("variable", None) != "damage_totaled":
                    print(f"inside an animation: type {anim.get('animationType')}, variable {anim.get('variable')}")
                    # inside the animation, get the "centerPoint" key
                    center_point = anim.get("centerPoint", None)
                    print(f"center point: {center_point}")

                    # Determine whether center_point is valid. Support both dict {x,y,z} and list/tuple [x,y,z].
                    valid_center = False
                    if center_point is None:
                        valid_center = False
                    elif isinstance(center_point, dict):
                        # dict-style centerPoint: check values
                        valid_center = all(coord is not None for coord in center_point.values()) and len(center_point) > 0
                    elif isinstance(center_point, (list, tuple)):
                        # list/tuple-style centerPoint: expect at least 3 numeric entries
                        valid_center = len(center_point) >= 3 and all(coord is not None for coord in center_point)
                    else:
                        valid_center = False

                    if valid_center:
                        # Create a new animation
                        new_anim = {
                            "animationType": "rotation",
                            "variable": "damage_totaled",
                            "centerPoint": center_point,
                            "axis": [
                                round(random.uniform(-10, 10), 3),
                                round(random.uniform(-10, 10), 3),
                                round(random.uniform(-10, 10), 3)
                            ]
                        }
                        print(f"new animation: {new_anim}")

                        # Queue the new animation to add after iteration
                        new_animations.append(new_anim)
                    else:
                        print("Skipping damaged animation due to invalid centerPoint or coordinates")

            # Add any newly-created animations to the object's animations list
            if new_animations:
                obj.setdefault("animations", []).extend(new_animations)
        else:
            print("damage_totaled animation already exists")
            # for all the animation, if of type "damage_totaled", but "centerPoint": null, then delete the animation
            for anim in obj.get("animations", []):
                if anim.get("variable", None) == "damage_totaled" and anim.get("centerPoint", None) == None:
                    obj["animations"].remove(anim)
                    print("removed damage_totaled animation due to null centerPoint")
            
        

    # Save the modified JSON file
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

# If the provided path is a single JSON file, process only that file.
if os.path.isfile(folder_path):
    if folder_path.lower().endswith('.json'):
        try:
            add_damaged_animation(folder_path)
            print(f"Modified: {folder_path}")
        except Exception as e:
            print(f"Error processing {folder_path}: {e}")
    else:
        print(f"Provided path is a file but not a JSON: {folder_path}")
# If the provided path is a directory, walk it as before.
elif os.path.isdir(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                # try to add a damaged animation to the file
                try:
                    add_damaged_animation(file_path)
                    print(f"Modified: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
else:
    print(f"Provided path does not exist: {folder_path}")

print("Done!")
