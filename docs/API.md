# WatchFace API Reference

Complete API documentation for creating custom watchfaces.

---

## WatchFace Structure

```cpp
struct WatchFace {
  // Bitmap properties
  const unsigned char* bitmap;
  int bitmap_x_start = 0;
  int bitmap_y_start = 0;
  int bitmap_x_end = 200;
  int bitmap_y_end = 200;
  uint16_t bitmap_color = GxEPD_BLACK;

  // Layout mode
  int layout = 0;           // 0=single-line, 1=two-line
  bool noAMPM = false;      // Hide AM/PM for 24h format

  // Text 1 (Time)
  int text1x = -1;          // -1=center, 0-100=percentage
  int text1y = -1;
  uint16_t text1color = GxEPD_BLACK;
  const GFXfont* text1font;

  // Text 2 (Date)
  int text2x = -1;
  int text2y = -1;
  uint16_t text2color = GxEPD_BLACK;
  const GFXfont* text2font;
};
```

---

## Property Reference

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| **Bitmap Properties** |
| `bitmap` | `const unsigned char*` | - | Pointer to PROGMEM array | Background image bitmap data |
| `bitmap_x_start` | `int` | `0` | 0-200 | Crop region start X coordinate (pixels) |
| `bitmap_y_start` | `int` | `0` | 0-200 | Crop region start Y coordinate (pixels) |
| `bitmap_x_end` | `int` | `200` | 0-200 | Crop region end X coordinate (pixels) |
| `bitmap_y_end` | `int` | `200` | 0-200 | Crop region end Y coordinate (pixels) |
| `bitmap_color` | `uint16_t` | `GxEPD_BLACK` | `GxEPD_BLACK` (0), `GxEPD_WHITE` (1) | Bitmap rendering color |
| **Layout Properties** |
| `layout` | `int` | `0` | `0` (single-line), `1` (two-line) | Text layout mode |
| `noAMPM` | `bool` | `false` | `true`, `false` | Hide AM/PM indicator for 24h format |
| **Time Text (text1) Properties** |
| `text1x` | `int` | `-1` | `-1` (center), `0-100` (%) | Horizontal position as percentage of screen width |
| `text1y` | `int` | `-1` | `-1` (center), `0-100` (%) | Vertical position as percentage of screen height |
| `text1color` | `uint16_t` | `GxEPD_BLACK` | `GxEPD_BLACK` (0), `GxEPD_WHITE` (1) | Time text color |
| `text1font` | `const GFXfont*` | - | Pointer to font | Font for time display |
| **Date Text (text2) Properties** |
| `text2x` | `int` | `-1` | `-1` (center), `0-100` (%) | Horizontal position as percentage (layout=1 only) |
| `text2y` | `int` | `-1` | `-1` (center), `0-100` (%) | Vertical position as percentage (layout=1 only) |
| `text2color` | `uint16_t` | `GxEPD_BLACK` | `GxEPD_BLACK` (0), `GxEPD_WHITE` (1) | Date text color |
| `text2font` | `const GFXfont*` | - | Pointer to font | Font for date display |

---

## Layout Modes

### Layout 0: Single-Line

Time and date appear on the same line with a 6-pixel gap. Only `text1x` and `text1y` are used.

```
┌──────────────────────────────────────┐
│                                      │
│        6:24 AM  Jun 24               │  ← Both use text1x/text1y
│                                      │
└──────────────────────────────────────┘
```

**Example**:
```cpp
struct WatchFace_simple : public WatchFace {
  WatchFace_simple() {
    bitmap = my_bitmap;
    layout = 0;              // Single-line
    text1x = -1;             // Center horizontally
    text1y = 50;             // 50% from top
    text1font = &Font20pt7b;
    text2font = &Font10pt7b;
  }
};
```

### Layout 1: Two-Line

Time and date have independent positioning using their respective coordinates.

```
┌──────────────────────────────────────┐
│             6:24 AM                  │  ← text1x, text1y
│                                      │
│             Jun 24                   │  ← text2x, text2y
└──────────────────────────────────────┘
```

**Example**:
```cpp
struct WatchFace_twolines : public WatchFace {
  WatchFace_twolines() {
    bitmap = my_bitmap;
    layout = 1;              // Two-line

    text1x = -1;             // Center time
    text1y = 40;             // 40% from top
    text1font = &Font20pt7b;

    text2x = -1;             // Center date
    text2y = 60;             // 60% from top
    text2font = &Font10pt7b;
  }
};
```

---

## Positioning System

### Percentage-Based Coordinates

All positions use percentages (0-100) of screen dimensions, or -1 for auto-center.

```cpp
// -1: Auto-center
text1x = -1;  // Horizontal center
text1y = -1;  // Vertical center

// 0-100: Percentage of screen
text1x = 50;  // 50% = 100 pixels on 200px screen
text1y = 25;  // 25% = 50 pixels on 200px screen
```

### Common Patterns

```
Top-Left:        Top-Right:       Center:
text1x = 5       text1x = 95      text1x = -1
text1y = 5       text1y = 5       text1y = -1

Bottom-Left:     Bottom-Right:    Custom:
text1x = 5       text1x = 95      text1x = 33
text1y = 95      text1y = 95      text1y = 67
```

---

## Configuration Examples

### 1. Basic Centered Layout
```cpp
struct WatchFace_simple : public WatchFace {
  WatchFace_simple() {
    bitmap = my_bitmap;
    layout = 0;
    text1x = -1;
    text1y = -1;
    text1font = &Font20pt7b;
    text2font = &Font10pt7b;
  }
};
```

### 2. Top and Bottom Layout
```cpp
struct WatchFace_topbottom : public WatchFace {
  WatchFace_topbottom() {
    bitmap = my_bitmap;
    layout = 1;

    text1x = -1;
    text1y = 10;
    text1font = &Font20pt7b;

    text2x = -1;
    text2y = 90;
    text2font = &Font10pt7b;
  }
};
```

### 3. Dark Background (White Text)
```cpp
struct WatchFace_dark : public WatchFace {
  WatchFace_dark() {
    bitmap = dark_bitmap;
    layout = 1;

    text1x = -1;
    text1y = 50;
    text1color = GxEPD_WHITE;
    text1font = &Font20pt7b;

    text2x = -1;
    text2y = 70;
    text2color = GxEPD_WHITE;
    text2font = &Font10pt7b;
  }
};
```

### 4. Corner Placement
```cpp
struct WatchFace_corner : public WatchFace {
  WatchFace_corner() {
    bitmap = my_bitmap;
    layout = 1;

    text1x = 5;              // 5% from left
    text1y = 5;              // 5% from top
    text1font = &Font20pt7b;

    text2x = 75;             // 75% from left
    text2y = 95;             // 95% from top
    text2font = &Font10pt7b;
  }
};
```

### 5. 24-Hour Format
```cpp
struct WatchFace_24h : public WatchFace {
  WatchFace_24h() {
    bitmap = my_bitmap;
    layout = 1;
    noAMPM = true;           // Hide AM/PM

    text1x = -1;
    text1y = 50;
    text1font = &Font20pt7b;

    text2x = -1;
    text2y = 70;
    text2font = &Font10pt7b;
  }
};
```

### 6. Cropped/Zoomed Bitmap
```cpp
struct WatchFace_zoomed : public WatchFace {
  WatchFace_zoomed() {
    bitmap = large_bitmap;

    // Display center 100x100 area
    bitmap_x_start = 50;
    bitmap_y_start = 50;
    bitmap_x_end = 150;
    bitmap_y_end = 150;

    layout = 1;
    text1x = -1;
    text1y = 50;
    text1font = &Font20pt7b;

    text2x = -1;
    text2y = 70;
    text2font = &Font10pt7b;
  }
};
```

---

## Creating Your Watchface

### Step-by-Step Process

**1. Prepare Artwork**
- Size: 200×200 pixels
- Format: Monochrome (1-bit)
- Use [image2cpp](https://javl.github.io/image2cpp/)

**2. Create Header File**

```cpp
// mywatchfaces/custom.h
const unsigned char custom_bitmap[] PROGMEM = {
  // ... bitmap data from image2cpp ...
};

// Array wrapper (required)
static const int custom_bitmap_allArray_LEN = 1;
static const unsigned char* custom_bitmap_allArray[1] = {
  custom_bitmap
};

// WatchFace class
struct WatchFace_custom : public WatchFace {
  WatchFace_custom() {
    bitmap = custom_bitmap;
    layout = 1;

    text1x = -1;
    text1y = 40;
    text1font = &MyFont20pt7b;

    text2x = -1;
    text2y = 60;
    text2font = &MyFont10pt7b;
  }
};
```

**3. Add Font Includes** (in `myutils.h`):
```cpp
#include "myfonts/MyFont20pt7b.h"
#include "myfonts/MyFont10pt7b.h"
```

**4. Include Watchface** (in `myutils.h`):
```cpp
#include "mywatchfaces/custom.h"
```

**5. Add to Array** (in `epaper_watch.ino`):
```cpp
WatchFace* allWatchFaces[] = {
  // ... existing watchfaces ...
  new WatchFace_custom(),
};
```

---

## Python Tools

Use the included tools for faster development:

```bash
cd watchfaceutils

# Interactive configurator
python3 configure_watchface.py

# Test single watchface
python3 render_watchface.py \
  --watchface ../mywatchfaces/custom.h \
  --time-font ../myfonts/MyFont20pt7b.h \
  --date-font ../myfonts/MyFont10pt7b.h \
  --time-x -1 --time-y 40

# Generate all previews
python3 generate_all_previews.py
```

---

## Tips & Best Practices

1. **Test positioning** with Python tools before uploading to hardware
2. **Use preview images** to verify text doesn't overlap with artwork
3. **Consider text color** - white text for dark backgrounds
4. **Layout mode 0** when text positions aren't critical (simpler)
5. **Layout mode 1** for precise artistic placement
6. **Center (-1)** is often the safest choice
7. **Font size** affects readability - test on actual display
8. **Bitmap cropping** useful for zooming or using sections of larger art

---

**Back to**: [Main README](README.md) | [Gallery](GALLERY.md)
