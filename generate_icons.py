"""
Run this script once after setup to generate PWA icons.
Usage: python generate_icons.py

Requires Pillow: pip install Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'icons')
os.makedirs(OUTPUT_DIR, exist_ok=True)

RED = (192, 57, 43)
WHITE = (255, 255, 255)

def create_icon(size):
    img = Image.new('RGB', (size, size), RED)
    draw = ImageDraw.Draw(img)

    # White rounded rectangle background for letter
    margin = int(size * 0.15)
    r = int(size * 0.15)
    inner_size = size - 2 * margin
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=r,
        fill=WHITE
    )

    # Draw "T" letter
    font_size = int(size * 0.45)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), "TREMHUB", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "TREMHUB  ", fill=RED, font=font)

    path = os.path.join(OUTPUT_DIR, f'icon-{size}.png')
    img.save(path, 'PNG')
    print(f'Created {path}')

for s in SIZES:
    create_icon(s)

print('\nAll icons generated successfully!')
