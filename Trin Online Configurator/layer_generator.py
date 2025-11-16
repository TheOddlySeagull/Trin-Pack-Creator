import os
from PIL import Image

# Define input and output folders
REFERENCE_FOLDER = "..\\Website\\reference"
OUTPUT_FOLDER = "..\\Website\\output"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Define color mappings
REPLACE_COLORS = {
    (178, 0, 255): (255, 255, 255),  # B200FF -> FFFFFF
    (255, 0, 220): (255, 255, 255),  # FF00DC -> FFFFFF
    (255, 0, 110): (255, 255, 255),  # FF006E -> FFFFFF
    (127, 51, 0): (130, 130, 130),   # 7F3300 -> 828282
}

LAYER_COLORS = {
    "Interior_Base": (66, 66, 66),      # 424242
    "Interior_Fabric": (130, 130, 130), # 828282
    "Interior_Stitching": (81, 81, 81), # 515151
    "Interior_Accent": (127, 51, 0),    # 7F3300
    "Paint1": (255, 255, 255),          # FFFFFF
    "Paint2": (255, 0, 220),            # FF00DC
    "Paint3": (178, 0, 255),            # B200FF
    "Paint4": (255, 0, 110),            # FF006E
}

def create_base_texture(img, base_filename):
    base_img = img.copy()
    base_pixels = base_img.load()
    
    for x in range(base_img.width):
        for y in range(base_img.height):
            r, g, b, a = base_pixels[x, y]

            # Replace only if exact match in REPLACE_COLORS
            if (r, g, b) in REPLACE_COLORS:
                base_pixels[x, y] = (*REPLACE_COLORS[(r, g, b)], a)
            else:
                base_pixels[x, y] = (r, g, b, a)  # Preserve original

    base_img.save(os.path.join(OUTPUT_FOLDER, f"{base_filename}_Base.png"))



def process_image(image_path):
    img = Image.open(image_path).convert("RGBA")
    base_filename = os.path.splitext(os.path.basename(image_path))[0]

    create_base_texture(img, base_filename)

    for layer_name, layer_color in LAYER_COLORS.items():
        layer_img = img.copy()
        layer_pixels = layer_img.load()
        has_matching_pixels = False
        for x in range(img.width):
            for y in range(img.height):
                if layer_pixels[x, y][:3] != layer_color:
                    layer_pixels[x, y] = (0, 0, 0, 0)
                else:
                    has_matching_pixels = True
        if has_matching_pixels:
            layer_img.save(os.path.join(OUTPUT_FOLDER, f"{base_filename}_{layer_name}.png"))


def main():
    # Process all images in the reference folder
    for filename in os.listdir(REFERENCE_FOLDER):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            process_image(os.path.join(REFERENCE_FOLDER, filename))

if __name__ == "__main__":
    main()