from PIL import Image

def extract_hex_colors(image_path):
    with Image.open(image_path).convert("RGBA") as img:
        pixels = img.getdata()
        unique_colors = {f"#{r:02X}{g:02X}{b:02X}" for r, g, b, a in pixels if a != 0}
        return sorted(unique_colors)

if __name__ == "__main__":
    path = input("Enter image path: ").strip()
    hex_colors = extract_hex_colors(path)
    print("Hex colors found:")
    for hex_color in hex_colors:
        print(hex_color)
