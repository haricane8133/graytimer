#!/usr/bin/env python3
"""
Generate preview images for all configured watchfaces
Automatically parses .h files to extract configuration
"""

import re
import os
from pathlib import Path
from render_watchface import render_watchface_preview

def parse_watchface_config(watchface_h_path):
    """
    Parse a watchface .h file to extract configuration
    Returns dict with font paths and positions
    """
    with open(watchface_h_path, 'r') as f:
        content = f.read()

    config = {
        'name': Path(watchface_h_path).stem,
        'watchface_path': watchface_h_path,
        'time_x': -1,  # Default to center
        'time_y': -1,
        'date_x': -1,
        'date_y': -1,
        'layout': 0,   # Default to single-line (matches WatchFace.h default)
    }

    # Extract font assignments
    time_font_match = re.search(r'text1font\s*=\s*&(\w+);', content)
    date_font_match = re.search(r'text2font\s*=\s*&(\w+);', content)

    if time_font_match:
        font_name = time_font_match.group(1)
        config['time_font'] = f"../myfonts/{font_name}.h"

    if date_font_match:
        font_name = date_font_match.group(1)
        config['date_font'] = f"../myfonts/{font_name}.h"

    # Extract positions (percentages 0-100 or -1 for center)
    text1x_match = re.search(r'text1x\s*=\s*(-?\d+);', content)
    text1y_match = re.search(r'text1y\s*=\s*(-?\d+);', content)
    text2x_match = re.search(r'text2x\s*=\s*(-?\d+);', content)
    text2y_match = re.search(r'text2y\s*=\s*(-?\d+);', content)

    if text1x_match:
        config['time_x'] = int(text1x_match.group(1))
    if text1y_match:
        config['time_y'] = int(text1y_match.group(1))
    if text2x_match:
        config['date_x'] = int(text2x_match.group(1))
    if text2y_match:
        config['date_y'] = int(text2y_match.group(1))

    # Extract layout
    layout_match = re.search(r'layout\s*=\s*(\d+);', content)
    if layout_match:
        config['layout'] = int(layout_match.group(1))

    # Check for noAMPM flag
    no_ampm_match = re.search(r'noAMPM\s*=\s*(true|false);', content)
    if no_ampm_match:
        config['noAMPM'] = no_ampm_match.group(1) == 'true'

    # Extract text colors (GxEPD_BLACK=0, GxEPD_WHITE=1)
    text1color_match = re.search(r'text1color\s*=\s*GxEPD_(BLACK|WHITE);', content)
    text2color_match = re.search(r'text2color\s*=\s*GxEPD_(BLACK|WHITE);', content)

    config['time_color'] = 1 if (text1color_match and text1color_match.group(1) == 'WHITE') else 0
    config['date_color'] = 1 if (text2color_match and text2color_match.group(1) == 'WHITE') else 0

    # Extract bitmap positioning
    bitmap_x_start_match = re.search(r'bitmap_x_start\s*=\s*(\d+);', content)
    bitmap_y_start_match = re.search(r'bitmap_y_start\s*=\s*(\d+);', content)
    bitmap_x_end_match = re.search(r'bitmap_x_end\s*=\s*(\d+);', content)
    bitmap_y_end_match = re.search(r'bitmap_y_end\s*=\s*(\d+);', content)

    if bitmap_x_start_match:
        config['bitmap_x_start'] = int(bitmap_x_start_match.group(1))
    if bitmap_y_start_match:
        config['bitmap_y_start'] = int(bitmap_y_start_match.group(1))
    if bitmap_x_end_match:
        config['bitmap_x_end'] = int(bitmap_x_end_match.group(1))
    if bitmap_y_end_match:
        config['bitmap_y_end'] = int(bitmap_y_end_match.group(1))

    return config


def generate_all_configured_watchfaces(output_dir="previews",
                                       time_text="6:24 AM",
                                       date_text="Jun 24"):
    """Generate preview images for all configured watchfaces"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Find all configured watchfaces from epaper_watch.ino
    configured_watchfaces = [
        'atat', 'atdp', 'b1', 'bird', 'bird2', 'bugs', 'crow', 'dog', 'giraffe1', 'mountain2', 'stormtrooper3_floyd',
        'h', 'krishna', 'macaw', 'mountain1', 'peacock', 'peacock3', 'pegasus', 'squares_invert', 'squares',
        'stormtrooper2', 'tom', 'bugs', 'tree', 'walker', 'xwing', 'zebra', 'ben10', 'claw', 'claw2', 'claw3',
        'guitar1', 'guitar2', 'harley', 'harry934', 'herbert', 'hogwarts', 'hogwarts2', 'hogwarts3', 'hogwarts4', 'jitsu1',
        'jitsu2', 'jitsu3', 'jitsu4', 'jitsu5', 'mikew', 'penguin_beatles', 'penguins', 'planets', 'ps', 'saturn',
        'sensei', 'sortinghat', 'sullivan', 'thiruman'
    ]

    print(f"Generating previews for {len(configured_watchfaces)} watchfaces...\n")

    success_count = 0
    for wf_name in configured_watchfaces:
        wf_path = f"../mywatchfaces/{wf_name}.h"

        if not os.path.exists(wf_path):
            print(f"⚠️  {wf_name}: Watchface file not found")
            continue

        try:
            # Parse configuration from .h file
            config = parse_watchface_config(wf_path)

            # Check if fonts exist
            if 'time_font' not in config or not os.path.exists(config['time_font']):
                print(f"⚠️  {wf_name}: Time font not found")
                continue

            if 'date_font' not in config or not os.path.exists(config['date_font']):
                print(f"⚠️  {wf_name}: Date font not found")
                continue

            # Adjust time text if noAMPM is set
            display_time = time_text
            if config.get('noAMPM', False):
                display_time = time_text.replace(' AM', '').replace(' PM', '')

            # Render preview
            output_path = os.path.join(output_dir, f"{wf_name}.png")
            render_watchface_preview(
                config['watchface_path'],
                config['time_font'],
                config['date_font'],
                config.get('time_x', -1),
                config.get('time_y', -1),
                config.get('date_x', -1),
                config.get('date_y', -1),
                display_time,
                date_text,
                output_path=output_path,
                layout=config.get('layout', 0),
                time_color=config.get('time_color', 0),
                date_color=config.get('date_color', 0),
                bitmap_x_start=config.get('bitmap_x_start', 0),
                bitmap_y_start=config.get('bitmap_y_start', 0),
                bitmap_x_end=config.get('bitmap_x_end', 200),
                bitmap_y_end=config.get('bitmap_y_end', 200)
            )
            print(f"✓ {wf_name}: {output_path}")
            success_count += 1

        except Exception as e:
            print(f"✗ {wf_name}: Error - {e}")

    print(f"\n{success_count}/{len(configured_watchfaces)} watchfaces rendered successfully")
    print(f"Output directory: {output_dir}/")


def list_all_watchfaces_and_fonts():
    """List all available watchfaces and fonts for reference"""

    print("=== Available Watchfaces ===")
    wf_dir = Path("../mywatchfaces")
    if wf_dir.exists():
        watchfaces = sorted(wf_dir.glob("*.h"))
        for wf in watchfaces:
            print(f"  - {wf.stem}")
    print()

    print("=== Available Fonts ===")
    font_dir = Path("../myfonts")
    if font_dir.exists():
        fonts = sorted(font_dir.glob("*.h"))
        # Group fonts by family
        font_families = {}
        for f in fonts:
            # Extract base name without size suffix
            base = re.sub(r'\d+pt7b$', '', f.stem)
            if base not in font_families:
                font_families[base] = []
            font_families[base].append(f.stem)

        for family, variants in sorted(font_families.items()):
            print(f"  - {family}")
            for variant in sorted(variants):
                size_match = re.search(r'(\d+)pt7b$', variant)
                if size_match:
                    print(f"    → {size_match.group(1)}pt")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate watchface previews')
    parser.add_argument('--output-dir', '-o', default='previews', help='Output directory')
    parser.add_argument('--time', default='6:24 AM', help='Time text to display')
    parser.add_argument('--date', default='Jun 24', help='Date text to display')
    parser.add_argument('--list', '-l', action='store_true', help='List all available watchfaces and fonts')

    args = parser.parse_args()

    if args.list:
        list_all_watchfaces_and_fonts()
    else:
        generate_all_configured_watchfaces(args.output_dir, args.time, args.date)
