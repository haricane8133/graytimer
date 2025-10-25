#!/usr/bin/env python3
"""
E-Paper Watchface Renderer
Renders watchface previews from .h files to PNG images
"""

import re
import os
from PIL import Image, ImageDraw
from pathlib import Path
import argparse

class GFXFont:
    """Parser for Adafruit GFX font format (.h files)"""

    def __init__(self, font_path):
        self.font_path = font_path
        self.font_name = Path(font_path).stem
        self.bitmap = []
        self.glyphs = []
        self.first_char = 0x20
        self.last_char = 0x7E
        self.y_advance = 0
        self._parse_font()

    def _parse_font(self):
        """Parse the .h font file to extract bitmap and glyph data"""
        with open(self.font_path, 'r') as f:
            content = f.read()

        # Extract bitmap data
        bitmap_match = re.search(r'const uint8_t \w+Bitmaps\[\] PROGMEM = \{([^}]+)\}', content, re.DOTALL)
        if bitmap_match:
            hex_values = re.findall(r'0x([0-9A-Fa-f]{2})', bitmap_match.group(1))
            self.bitmap = [int(h, 16) for h in hex_values]

        # Extract glyph data
        # Match the entire glyph array including nested braces
        glyph_match = re.search(r'const GFXglyph \w+Glyphs\[\] PROGMEM = \{(.*?)\};', content, re.DOTALL)
        if glyph_match:
            glyph_lines = glyph_match.group(1).strip().split('\n')
            for line in glyph_lines:
                # Parse: {  offset,  width,  height,  xAdvance,  xOffset,  yOffset }
                # Allow for variable spacing and leading spaces
                match = re.search(r'\{\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\s*\}', line)
                if match:
                    self.glyphs.append({
                        'bitmapOffset': int(match.group(1)),
                        'width': int(match.group(2)),
                        'height': int(match.group(3)),
                        'xAdvance': int(match.group(4)),
                        'xOffset': int(match.group(5)),
                        'yOffset': int(match.group(6))
                    })

        # Extract font metadata (first char, last char, y advance)
        # Look specifically for the GFXfont struct definition
        font_match = re.search(r'const GFXfont \w+ PROGMEM = \{[^}]*0x([0-9A-Fa-f]{2}),\s*0x([0-9A-Fa-f]{2}),\s*(\d+)', content, re.DOTALL)
        if font_match:
            self.first_char = int(font_match.group(1), 16)
            self.last_char = int(font_match.group(2), 16)
            self.y_advance = int(font_match.group(3))

    def render_char(self, char, x, y, image_draw, color=0):
        """Render a single character at position (x, y)

        Args:
            color: 0 = black (default), 1 = white (inverted)
        """
        char_code = ord(char)

        if char_code < self.first_char or char_code > self.last_char:
            return x  # Return unchanged x if character not in font

        glyph_index = char_code - self.first_char
        if glyph_index >= len(self.glyphs):
            return x

        glyph = self.glyphs[glyph_index]

        # Get glyph dimensions and offsets
        bitmap_offset = glyph['bitmapOffset']
        width = glyph['width']
        height = glyph['height']
        x_offset = glyph['xOffset']
        y_offset = glyph['yOffset']
        x_advance = glyph['xAdvance']

        # Determine pixel color (0=black, 1=white)
        fill_color = 1 if color == 1 else 0

        # Render bitmap
        for h in range(height):
            for w in range(width):
                bit_index = h * width + w
                byte_index = bitmap_offset + (bit_index // 8)
                bit_position = 7 - (bit_index % 8)

                if byte_index < len(self.bitmap):
                    if (self.bitmap[byte_index] >> bit_position) & 1:
                        px = x + x_offset + w
                        py = y + y_offset + h
                        image_draw.point((px, py), fill=fill_color)

        return x + x_advance

    def render_text(self, text, x, y, image_draw, color=0):
        """Render text string at position (x, y)

        Args:
            color: 0 = black (default), 1 = white (inverted)
        """
        cursor_x = x
        for char in text:
            cursor_x = self.render_char(char, cursor_x, y, image_draw, color)
        return cursor_x

    def get_text_bounds(self, text):
        """
        Calculate text bounding box similar to Adafruit GFX getTextBounds()
        Returns (x1, y1, width, height)
        """
        if not text:
            return (0, 0, 0, 0)

        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0
        cursor_x = 0

        for char in text:
            char_code = ord(char)
            if char_code < self.first_char or char_code > self.last_char:
                continue

            glyph_index = char_code - self.first_char
            if glyph_index >= len(self.glyphs):
                continue

            glyph = self.glyphs[glyph_index]

            # Calculate glyph bounds
            glyph_x = cursor_x + glyph['xOffset']
            glyph_y = glyph['yOffset']
            glyph_w = glyph['width']
            glyph_h = glyph['height']

            # Update bounding box
            min_x = min(min_x, glyph_x)
            max_x = max(max_x, glyph_x + glyph_w)
            min_y = min(min_y, glyph_y)
            max_y = max(max_y, glyph_y + glyph_h)

            cursor_x += glyph['xAdvance']

        width = max_x - min_x
        height = max_y - min_y

        return (min_x, min_y, width, height)


class Watchface:
    """Parser and renderer for watchface bitmap"""

    def __init__(self, watchface_path):
        self.watchface_path = watchface_path
        self.watchface_name = Path(watchface_path).stem
        self.bitmap = []
        self.width = 200
        self.height = 200
        self._parse_watchface()

    def _parse_watchface(self):
        """Parse the .h watchface file to extract bitmap data"""
        with open(self.watchface_path, 'r') as f:
            content = f.read()

        # Extract bitmap data (watchface background)
        bitmap_match = re.search(r'const unsigned char \w+_bitmap_\w+ \[\] PROGMEM = \{([^}]+)\}', content, re.DOTALL)
        if bitmap_match:
            hex_values = re.findall(r'0x([0-9A-Fa-f]{2})', bitmap_match.group(1))
            self.bitmap = [int(h, 16) for h in hex_values]

    def render(self):
        """Render the watchface bitmap to a PIL Image"""
        # Create white background (e-paper style)
        image = Image.new('1', (self.width, self.height), 1)
        pixels = image.load()

        # Render bitmap (1-bit packed format, MSB first)
        for y in range(self.height):
            for x in range(self.width):
                bit_index = y * self.width + x
                byte_index = bit_index // 8
                bit_position = 7 - (bit_index % 8)

                if byte_index < len(self.bitmap):
                    if (self.bitmap[byte_index] >> bit_position) & 1:
                        pixels[x, y] = 0  # Black pixel

        return image


def render_watchface_preview(watchface_path, time_font_path, date_font_path,
                            time_x, time_y, date_x, date_y,
                            time_text="6:24 AM", date_text="Oct 25",
                            output_path=None, layout=0,
                            time_color=0, date_color=0,
                            bitmap_x_start=0, bitmap_y_start=0,
                            bitmap_x_end=200, bitmap_y_end=200):
    """
    Render a complete watchface preview with time and date

    Args:
        watchface_path: Path to watchface .h file
        time_font_path: Path to time font .h file
        date_font_path: Path to date font .h file
        time_x, time_y: Position for time text (percentage 0-100, or -1 for center)
        date_x, date_y: Position for date text (percentage 0-100, or -1 for center)
        time_text: Time string to display
        date_text: Date string to display
        output_path: Where to save PNG (default: watchface_name.png)
        layout: 0 = single line (default), 1 = two lines
        time_color: 0 = black, 1 = white (inverted)
        date_color: 0 = black, 1 = white (inverted)
        bitmap_x_start, bitmap_y_start: Bitmap offset
        bitmap_x_end, bitmap_y_end: Bitmap size
    """
    screenW = 200
    screenH = 200

    # Parse watchface
    watchface = Watchface(watchface_path)

    # Render bitmap with cropping support
    if bitmap_x_start != 0 or bitmap_y_start != 0 or bitmap_x_end != 200 or bitmap_y_end != 200:
        # Create full white canvas
        image = Image.new('1', (screenW, screenH), 1)
        # Render watchface (will be cropped)
        wf_image = watchface.render()
        # Paste cropped region
        image.paste(wf_image.crop((bitmap_x_start, bitmap_y_start, bitmap_x_end, bitmap_y_end)),
                   (bitmap_x_start, bitmap_y_start))
    else:
        image = watchface.render()

    draw = ImageDraw.Draw(image)

    # Parse fonts
    time_font = GFXFont(time_font_path)
    date_font = GFXFont(date_font_path)

    # Get text bounds (matching GFX getTextBounds behavior)
    x1, y1, w1, h1 = time_font.get_text_bounds(time_text)
    x2, y2, w2, h2 = date_font.get_text_bounds(date_text)

    # Calculate positions based on layout (matching myutils.cpp logic)
    if layout == 1:
        # Two-line layout (most common)
        # time_x/time_y are percentages (0-100) or -1 for center

        # Calculate time position
        if time_x < 0:
            # Center horizontally
            drawX1 = (screenW - w1) // 2 - x1
        else:
            # Percentage-based position
            drawX1 = int(screenW * (time_x / 100.0)) - x1

        if time_y < 0:
            # Center vertically
            drawY1 = (screenH - h1) // 2 - y1
        else:
            # Percentage-based position
            drawY1 = int(screenH * (time_y / 100.0)) - y1

        # Calculate date position
        if date_x < 0:
            # Center horizontally
            drawX2 = (screenW - w2) // 2 - x2
        else:
            # Percentage-based position
            drawX2 = int(screenW * (date_x / 100.0)) - x2

        if date_y < 0:
            # Center vertically
            drawY2 = (screenH - h2) // 2 - y2
        else:
            # Percentage-based position
            drawY2 = int(screenH * (date_y / 100.0)) - y2

        # Render text
        time_font.render_text(time_text, drawX1, drawY1, draw, time_color)
        date_font.render_text(date_text, drawX2, drawY2, draw, date_color)

    else:
        # Single-line layout (time and date on same line)
        totalW = w1 + w2 + 6  # 6px gap
        totalH = max(h1, h2)

        if time_x < 0:
            originX = (screenW - totalW) // 2
        else:
            originX = int(screenW * (time_x / 100.0))

        if time_y < 0:
            baselineY = (screenH - totalH) // 2
        else:
            baselineY = int(screenH * (time_y / 100.0))

        # Render time and date side by side
        time_font.render_text(time_text, originX - x1, baselineY - y1, draw, time_color)
        date_font.render_text(date_text, originX + w1 + 6 - x2, baselineY - y2, draw, date_color)

    # Save output
    if output_path is None:
        output_path = f"{watchface.watchface_name}.png"

    image.save(output_path)
    print(f"Saved: {output_path}")
    return image


def generate_all_configured_watchfaces(output_dir="previews"):
    """Generate preview images for all configured watchfaces"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Configured watchfaces (from epaper_watch.ino)
    watchfaces = [
        {
            'name': 'atat',
            'watchface': '../mywatchfaces/atat.h',
            'time_font': '../myfonts/StarJedi_DGRW10pt7b.h',
            'date_font': '../myfonts/StarJedi_DGRW10pt7b.h',
            'time_x': -1,
            'time_y': 5,
            'date_x': 0,  # Will be calculated based on watchface defaults
            'date_y': 0,
        },
        # Add more as you configure them...
    ]

    for wf in watchfaces:
        try:
            output_path = os.path.join(output_dir, f"{wf['name']}.png")
            render_watchface_preview(
                wf['watchface'],
                wf['time_font'],
                wf['date_font'],
                wf['time_x'],
                wf['time_y'],
                wf.get('date_x', 0),
                wf.get('date_y', 190),
                output_path=output_path
            )
        except Exception as e:
            print(f"Error rendering {wf['name']}: {e}")


def interactive_mode(watchface_path, font_path):
    """
    Interactive mode: Try different positions and see results
    """
    print("=== Interactive Watchface Renderer ===")
    print(f"Watchface: {Path(watchface_path).name}")
    print(f"Font: {Path(font_path).name}")
    print()

    while True:
        try:
            time_text = input("Time text [6:24 AM]: ").strip() or "6:24 AM"
            date_text = input("Date text [Oct 25]: ").strip() or "Oct 25"
            time_x = int(input("Time X position [-1]: ").strip() or "-1")
            time_y = int(input("Time Y position [5]: ").strip() or "5")
            date_x = int(input("Date X position [0]: ").strip() or "0")
            date_y = int(input("Date Y position [190]: ").strip() or "190")

            output_name = f"preview_{Path(watchface_path).stem}.png"

            render_watchface_preview(
                watchface_path, font_path, font_path,
                time_x, time_y, date_x, date_y,
                time_text, date_text,
                output_path=output_name
            )

            print(f"\nGenerated: {output_name}")
            print("\nWatchFace class snippet:")
            print(f"    text1x = {time_x};")
            print(f"    text1y = {time_y};")
            print(f"    text2x = {date_x};")
            print(f"    text2y = {date_y};")
            print(f"    text1font = &{Path(font_path).stem};")
            print(f"    text2font = &{Path(font_path).stem};")
            print()

            again = input("Try again? (y/n): ").strip().lower()
            if again != 'y':
                break

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render e-paper watchface previews')
    parser.add_argument('watchface', nargs='?', help='Path to watchface .h file')
    parser.add_argument('--font', help='Path to font .h file')
    parser.add_argument('--time-font', help='Path to time font .h file')
    parser.add_argument('--date-font', help='Path to date font .h file')
    parser.add_argument('--time-x', type=int, default=-1, help='Time X position')
    parser.add_argument('--time-y', type=int, default=5, help='Time Y position')
    parser.add_argument('--date-x', type=int, default=0, help='Date X position')
    parser.add_argument('--date-y', type=int, default=190, help='Date Y position')
    parser.add_argument('--time-text', default='6:24 AM', help='Time text to display')
    parser.add_argument('--date-text', default='Oct 25', help='Date text to display')
    parser.add_argument('--output', '-o', help='Output PNG path')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--all', action='store_true', help='Generate all configured watchfaces')

    args = parser.parse_args()

    if args.all:
        generate_all_configured_watchfaces()
    elif args.interactive and args.watchface and args.font:
        interactive_mode(args.watchface, args.font)
    elif args.watchface:
        time_font = args.time_font or args.font
        date_font = args.date_font or args.font

        # if not time_font:
        #     print("Error: --font or --time-font required")
        #     exit(1)

        render_watchface_preview(
            args.watchface,
            time_font,
            date_font or time_font,
            args.time_x,
            args.time_y,
            args.date_x,
            args.date_y,
            args.time_text,
            args.date_text,
            args.output
        )
    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Render single watchface")
        print("  ./render_watchface.py ../mywatchfaces/atat.h --font ../myfonts/StarJedi_DGRW10pt7b.h")
        print()
        print("  # Interactive mode to find perfect positions")
        print("  ./render_watchface.py ../mywatchfaces/bird.h --font ../myfonts/FreeSansBold20pt7b.h -i")
        print()
        print("  # Custom positions and text")
        print("  ./render_watchface.py ../mywatchfaces/mountain2.h --font ../myfonts/Orbitron_Medium20pt7b.h \\")
        print("    --time-x 10 --time-y 20 --date-x 50 --date-y 180 --time-text '12:00 PM' -o test.png")
