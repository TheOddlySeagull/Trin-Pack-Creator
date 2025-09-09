import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Constants
BANNER_HEIGHT = 31
PANEL_WIDTH = 9
PANEL_HEIGHT = 27
PADDING = 4
FONT_SIZE = 16

# File paths
DARK_TEXTURE_PATH = "E:/Documents Global/Programmation/Trin/Trin Pack Creator/Trin Online Configurator/backgrounds/metal_dark.png"
LIGHT_TEXTURE_PATH = "E:/Documents Global/Programmation/Trin/Trin Pack Creator/Trin Online Configurator/backgrounds/metal_light.png"
FONT_PATH = "E:/Documents Global/Programmation/Trin/Trin Pack Creator/Trin Online Configurator/EXEPixelPerfect.ttf"

CREATOR_NAME = "TheOddlySeagull"

def tile_background(width, height, tile_image_path):
    tile = Image.open(tile_image_path).convert("RGBA")
    tile_w, tile_h = tile.size
    bg = Image.new("RGBA", (width, height))
    for x in range(0, width, tile_w):
        for y in range(0, height, tile_h):
            bg.paste(tile, (x, y))
    return bg

def draw_text_panel(text, font, background_texture, padding=1):
    dummy_img = Image.new("RGBA", (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    text_bbox = draw_dummy.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    panel_w = text_w + padding
    panel_h = text_h + padding
    panel_bg = tile_background(panel_w, panel_h, background_texture)

    bordered_panel = Image.new("RGBA", (panel_w + 2, panel_h + 2), (0, 0, 0, 0))
    bordered_panel.paste((0, 0, 0), [0, 0, panel_w + 2, panel_h + 2])  # black border
    bordered_panel.paste(panel_bg, (1, 1))

    draw_text = ImageDraw.Draw(bordered_panel)
    text_x = (panel_w // 2) + 2
    text_y = (panel_h // 2)
    draw_text.text((text_x, text_y), text, font=font, fill=(255, 85, 85), anchor="mm")

    return bordered_panel

def draw_fixed_color_panel(banner, base_img):
    """Draws a solid black 9x27 color panel at bottom-left of the image."""
    panel_left = 2
    panel_bottom = banner.height - BANNER_HEIGHT + 2
    panel = Image.new("RGBA", (PANEL_WIDTH, PANEL_HEIGHT), (0, 0, 0, 255))
    banner.paste(panel, (panel_left, panel_bottom), panel)

    # Copy over interior showcase pixels to panel
    copyfrom_left = 3
    copyfrom_top = base_img.height - 15
    copyfrom_right = copyfrom_left + 7
    copyfrom_bottom = copyfrom_top + 12
    iterior_showcase = base_img.crop((copyfrom_left, copyfrom_top, copyfrom_right, copyfrom_bottom))
    banner.paste(iterior_showcase, (panel_left + 1, panel_bottom + 14), iterior_showcase)

    # Copy over exterior showcase pixels to panel
    copyfrom_top = base_img.height - 28
    copyfrom_bottom = copyfrom_top + 12
    exterior_showcase = base_img.crop((copyfrom_left, copyfrom_top, copyfrom_right, copyfrom_bottom))
    banner.paste(exterior_showcase, (panel_left + 1, panel_bottom + 1), exterior_showcase)


def draw_banner_overlay(base_img, trim_name, car_name, banner_date=None):
    width = base_img.width
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE, layout_engine=ImageFont.Layout.BASIC)

    # Banner base
    banner = tile_background(width, BANNER_HEIGHT, DARK_TEXTURE_PATH)
    draw = ImageDraw.Draw(banner)
    draw.rectangle([0, 0, width - 1, BANNER_HEIGHT - 1], outline="black")

    # === Fixed Paint Panel Area (left side) ===
    draw_fixed_color_panel(banner, base_img)

    # === Trim Text Panel (to right of paint panels) ===
    trim_panel = draw_text_panel(trim_name, font, LIGHT_TEXTURE_PATH, padding=2)
    trim_pannel_left = 14
    banner.paste(trim_panel, (trim_pannel_left, (BANNER_HEIGHT - trim_panel.height) // 2), trim_panel)

    # === Center Panel (above): Creator ===
    center_text = f"{CREATOR_NAME}"
    center_panel = draw_text_panel(center_text, font, LIGHT_TEXTURE_PATH, padding=2)
    center_x = (width - center_panel.width) // 2
    banner.paste(center_panel, (center_x, 2), center_panel)

    # === Center Panel (below): Date ===
    # {banner_date or datetime.today().strftime('%d/%m/%Y')}
    date_text = f"{banner_date or datetime.today().strftime('%d/%m/%Y')}"
    date_panel = draw_text_panel(date_text, font, LIGHT_TEXTURE_PATH, padding=2)
    date_x = (width - date_panel.width) // 2
    banner.paste(date_panel, (date_x, (BANNER_HEIGHT - date_panel.height - 2)), date_panel)

    # === Car Name Panel (Right side) ===
    car_panel = draw_text_panel(car_name, font, LIGHT_TEXTURE_PATH, padding=2)
    banner.paste(car_panel, (width - car_panel.width - PADDING, (BANNER_HEIGHT - car_panel.height) // 2), car_panel)

    # Draw banner over original image
    base_img.paste(banner, (0, base_img.height - BANNER_HEIGHT), banner)
    return base_img

# === Example usage ===
if __name__ == "__main__":
    trim = "Military Spec"
    car = "Trin UVTG165"
    img_path = "E:/Documents Global/Programmation/Trin/Trin Pack Creator/Website/reference/trin_ary-uvtg165_BASE.png"
    out_path = "E:/Documents Global/Programmation/Trin/Trin Pack Creator/Website/reference/trin_ary-uvtg165_BASE.png"

    img = Image.open(img_path).convert("RGBA")
    final = draw_banner_overlay(img, trim, car)
    final.save(out_path)
