# Gray Timer docs

Everything about Gray Timer, from soldering it together to drawing your own
watchface. Start wherever you like.

- **[Watchface catalog](CATALOG.md)**: Browse all 116 watchfaces by collection, and pick one or set the time from a phone over NFC
- **[Gallery](GALLERY.md)**: photos of the finished watch
- **[Build story](BUILD.md)**: how V2 came together, in photos
- **[Hardware guide](HARDWARE.md)**: parts, wiring, the case, power, uploading and troubleshooting
- **[WatchFace API](API.md)**: every setting a watchface has, and how to place the time on it

**Collections**: Star Wars (13) • Harry Potter (10) • Club Penguin (8) • Animals (9) • Other Characters (11) • Horizon Zero Dawn (6) • Hades (20) • Prince of Persia (1) • Music & Entertainment (8) • Nature & Landscapes (9) • Space (7) • Cultural & Spiritual (6) • Everyday Things (3) • Abstract & Patterns (5)

---

## How it works

- **It sleeps almost all the time.** The nRF52840 sits in System OFF, its
  deepest sleep. Once a minute the RV-8803 clock pulls D2 low, which wakes the
  chip. It draws the new minute and goes straight back to sleep.
- **Your phone can wake it too.** The watch is an NFC tag. Hold a phone with any
  NFC tag app to it and write a short text: a face number, `0` for shuffle, the
  date and time, `refresh` or `dfu`. The [catalog](CATALOG.md#using-a-phone)
  explains each one.
- **It remembers one thing while asleep:** a single byte in the clock's RAM
  that holds the face number and whether it's pinned. A reset or power loss
  puts it back in shuffle mode.
- **Two kinds of refresh.** A quick partial refresh every minute, and a full
  refresh that clears ghosting: every 10 minutes in shuffle mode (with a new
  face), every 30 minutes for a pinned face, or whenever a phone writes
  `refresh`.

---

## Settings

They're at the top of [`graytimer.ino`](../graytimer.ino):

```cpp
const bool ENABLE_TIME_SETUP = false;              // Ask for the time on the Serial Monitor after a reset
const bool ENABLE_PARTIAL_REFRESH = true;          // false = a full refresh every minute
const uint8_t FULL_REFRESH_INTERVAL = 10;          // Shuffle mode: new face and full refresh every 10 min
const uint8_t PINNED_FULL_REFRESH_INTERVAL = 30;   // A pinned face: full refresh every 30 min
const bool ENABLE_WATCHFACE_CYCLING = true;        // Shuffle between faces
const bool ENABLE_SERIAL_DEBUG = false;            // Keep false on the wrist: Serial costs power
```

Refreshes use nearly all of the power, and a full one costs about three times
a partial one, so `FULL_REFRESH_INTERVAL` is the setting that matters most for
battery life. The [hardware guide](HARDWARE.md#power-consumption) has the
numbers.

---

## Making your own watchface

A watchface is a 200×200 black-and-white picture plus the fonts and positions
for the time and date.

1. **Make the picture.** Start from your own art with
   [image2cpp](https://javl.github.io/image2cpp/), then place the time with
   `configure_watchface.py`. Or draw a face in code in `generate_geometric.py`.
   Dither photos at their final size with `dither_source.py`; line art looks
   best simply thresholded.
2. **Include it** in [`myutils.h`](../myutils.h):
   `#include "mywatchfaces/<name>.h"`
3. **Add it to the end** of `allWatchFaces[]` in
   [`graytimer.ino`](../graytimer.ino), with its number in a comment:
   `new WatchFace_<name>(),  // 117`
4. **Add it to the catalog.** Put it in `GROUPS` in `generate_catalog.py`, then
   in `watchfaceutils/` run `python3 generate_all_previews.py` and
   `python3 generate_catalog.py`.

Face numbers never change, because phones use them. To retire a face, replace
its line with `nullptr,  // N retired` rather than deleting it.

Flash is nearly full. The bootloader refuses uploads bigger than about 790 KB,
even though the IDE allows more, so crop new art to its ink and check the size
after you compile.

**[📖 The full WatchFace API →](API.md)**

---

## Python tools

They live in [`watchfaceutils/`](../watchfaceutils) and need only Pillow
(`pip3 install Pillow`). Each one explains its options at the top of the file.

| Tool | What it does |
|------|--------------|
| `configure_watchface.py` | Try fonts and positions on a picture, step by step, and write the watchface file |
| `render_watchface.py` | Draw one watchface to a PNG |
| `generate_all_previews.py` | Draw a preview of every watchface |
| `generate_catalog.py` | Rebuild the catalog and the face counts in the docs |
| `generate_geometric.py` | Draw watchfaces in code, no artwork needed |
| `dither_source.py` | Turn a colour picture into a 1-bit one, at its final size |
| `ttf_to_gfx.py` | Turn a TTF or OTF font into a font the watch can use |
| `glyphs_to_gfx.py` | Turn a folder of pixel-font glyphs into a font |
| `generate_dfu_screen.py` | Build the firmware update screen |
| `generate_readme_banner.py` | Build the title art and photos for the README |

---

## When something's not right

| What you see | What to try |
|--------------|-------------|
| The screen draws once and never changes | The RV-8803's INT must reach D2: that's what wakes the watch each minute |
| The time is wrong | Write the date and time from your phone: `2026-10-25 14:30:00` |
| Faint leftovers of old faces | Write `refresh`, or set a smaller `FULL_REFRESH_INTERVAL` |
| The upload won't start | Write `dfu` first (or double-tap reset). On macOS, see [Programming](HARDWARE.md#programming) |
| The battery runs down fast | Keep `ENABLE_SERIAL_DEBUG` false, cut the RTC board's LED jumper, and check the solder joints |

More in the [hardware guide](HARDWARE.md#troubleshooting).

---

## At a glance

| | |
|---|---|
| **MCU** | Seeed Xiao nRF52840 (Cortex-M4, 64 MHz, 1 MB flash, 256 KB RAM) |
| **Display** | GoodDisplay GDEY0154D67: 1.54", 200×200, black and white, SPI |
| **Clock** | Micro Crystal RV-8803: ±3 ppm, 0.24 µA |
| **Phone link** | NFC Type 2 tag on the Xiao's NFC pads |
| **Battery** | 3.7 V LiPo, 300-500 mAh |
| **Refresh** | Partial every minute, full every 10 minutes (30 when pinned) |
