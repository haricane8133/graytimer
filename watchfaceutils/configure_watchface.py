#!/usr/bin/env python3
"""
Interactive Watchface Configurator
Helps create watchface class files by testing different fonts and positions
"""

import os
import sys
from pathlib import Path
from render_watchface import render_watchface_preview, GFXFont

def get_available_fonts():
    """Get list of all available fonts"""
    fonts = []
    font_dir = Path("../myfonts")
    if font_dir.exists():
        for f in sorted(font_dir.glob("*.h")):
            fonts.append(f.stem)
    return fonts


def get_available_watchfaces():
    """Get list of all available watchfaces"""
    watchfaces = []
    wf_dir = Path("../mywatchfaces")
    if wf_dir.exists():
        for w in sorted(wf_dir.glob("*.h")):
            watchfaces.append(w.stem)
    return watchfaces


def select_from_list(items, prompt="Select"):
    """Interactive list selection"""
    print(f"\n{prompt}:")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")

    while True:
        try:
            choice = input(f"\nEnter number (1-{len(items)}): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    return items[idx]
            print("Invalid choice, try again.")
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)


def measure_text_width(font_path, text):
    """Estimate text width using GFX font"""
    try:
        font = GFXFont(font_path)
        width = 0
        for char in text:
            char_code = ord(char)
            if font.first_char <= char_code <= font.last_char:
                glyph_index = char_code - font.first_char
                if glyph_index < len(font.glyphs):
                    width += font.glyphs[glyph_index]['xAdvance']
        return width
    except:
        return 0


def configure_watchface_interactive():
    """Interactive watchface configuration"""
    print("=" * 60)
    print("  E-Paper Watchface Configurator")
    print("=" * 60)

    # Select watchface
    watchfaces = get_available_watchfaces()
    if not watchfaces:
        print("Error: No watchfaces found in ../mywatchfaces/")
        return

    watchface_name = select_from_list(watchfaces, "Select Watchface")
    watchface_path = f"../mywatchfaces/{watchface_name}.h"

    # Select time font
    fonts = get_available_fonts()
    if not fonts:
        print("Error: No fonts found in ../myfonts/")
        return

    print("\n" + "=" * 60)
    time_font_name = select_from_list(fonts, "Select TIME Font")
    time_font_path = f"../myfonts/{time_font_name}.h"

    # Select date font
    print("\n" + "=" * 60)
    print("Select DATE Font (or press Enter for same as time font):")
    same = input("Use same font for date? (Y/n): ").strip().lower()
    if same in ('', 'y', 'yes'):
        date_font_name = time_font_name
        date_font_path = time_font_path
    else:
        date_font_name = select_from_list(fonts, "Select DATE Font")
        date_font_path = f"../myfonts/{date_font_name}.h"

    # Configure text
    print("\n" + "=" * 60)
    time_text = input("Time text to display [6:24 AM]: ").strip() or "6:24 AM"
    date_text = input("Date text to display [Oct 25]: ").strip() or "Oct 25"

    # Ask about AM/PM
    has_ampm = ' AM' in time_text or ' PM' in time_text
    no_ampm = False
    if has_ampm:
        remove_ampm = input("Remove AM/PM from display? (y/N): ").strip().lower()
        if remove_ampm in ('y', 'yes'):
            no_ampm = True
            time_text = time_text.replace(' AM', '').replace(' PM', '')

    # Estimate text widths for centering suggestions
    time_width = measure_text_width(time_font_path, time_text)
    date_width = measure_text_width(date_font_path, date_text)

    # Interactive position adjustment
    print("\n" + "=" * 60)
    print("Position Configuration")
    print("  Display size: 200x200 pixels")
    print(f"  Estimated time text width: ~{time_width}px")
    print(f"  Estimated date text width: ~{date_width}px")
    print("\nSuggested positions:")
    print(f"  Time centered: x={(200-time_width)//2}")
    print(f"  Date centered: x={(200-date_width)//2}")
    print("\nTips:")
    print("  - Y position is baseline (bottom of text)")
    print("  - Negative values move left/up")
    print("  - Use -1 for x to auto-center")
    print("=" * 60)

    # Initial positions
    time_x = int(input(f"Time X position [{(200-time_width)//2}]: ").strip() or str((200-time_width)//2))
    time_y = int(input("Time Y position [20]: ").strip() or "20")
    date_x = int(input(f"Date X position [{(200-date_width)//2}]: ").strip() or str((200-date_width)//2))
    date_y = int(input("Date Y position [190]: ").strip() or "190")

    iteration = 0
    while True:
        iteration += 1
        output_path = f"config_preview_{watchface_name}_{iteration}.png"

        # Render preview
        print(f"\nRendering preview...")
        render_watchface_preview(
            watchface_path,
            time_font_path,
            date_font_path,
            time_x, time_y,
            date_x, date_y,
            time_text, date_text,
            output_path=output_path
        )

        print(f"\nPreview saved: {output_path}")
        print("\nCurrent configuration:")
        print(f"  Time: x={time_x}, y={time_y}")
        print(f"  Date: x={date_x}, y={date_y}")

        # Ask for adjustments
        print("\nAdjust positions or finish?")
        print("  1. Adjust time position")
        print("  2. Adjust date position")
        print("  3. Save and generate code")
        print("  4. Quit without saving")

        choice = input("\nChoice: ").strip()

        if choice == '1':
            adj_x = input(f"Time X [{time_x}]: ").strip()
            adj_y = input(f"Time Y [{time_y}]: ").strip()
            time_x = int(adj_x) if adj_x else time_x
            time_y = int(adj_y) if adj_y else time_y

        elif choice == '2':
            adj_x = input(f"Date X [{date_x}]: ").strip()
            adj_y = input(f"Date Y [{date_y}]: ").strip()
            date_x = int(adj_x) if adj_x else date_x
            date_y = int(adj_y) if adj_y else date_y

        elif choice == '3':
            # Generate C++ code
            print("\n" + "=" * 60)
            print("Generated WatchFace Class Code:")
            print("=" * 60)

            class_name = ''.join(word.capitalize() for word in watchface_name.split('_'))

            code = f"""
struct WatchFace_{watchface_name} : public WatchFace {{
  WatchFace_{watchface_name}() {{
    bitmap = {watchface_name}_bitmap_{watchface_name};

    text1x = {time_x};
    text1y = {time_y};
    text1font = &{time_font_name};

    text2x = {date_x};
    text2y = {date_y};
    text2font = &{date_font_name};
"""

            if no_ampm:
                code += f"    noAMPM = true;\n"

            code += "  }\n};\n"

            print(code)

            # Save to file
            save_choice = input("Save to file? (y/N): ").strip().lower()
            if save_choice in ('y', 'yes'):
                # Add to existing .h file or create snippet
                snippet_file = f"watchface_{watchface_name}_snippet.h"
                with open(snippet_file, 'w') as f:
                    f.write(code)
                print(f"\nCode saved to: {snippet_file}")
                print("Copy this code into ../mywatchfaces/{watchface_name}.h")

            # Update epaper_watch.ino suggestion
            print("\n" + "=" * 60)
            print("To add to epaper_watch.ino, add this line to the allWatchFaces array:")
            print(f"  new WatchFace_{watchface_name}(),")
            print("=" * 60)

            break

        elif choice == '4':
            print("Exiting without saving.")
            break

        else:
            print("Invalid choice.")


if __name__ == '__main__':
    try:
        configure_watchface_interactive()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting...")
