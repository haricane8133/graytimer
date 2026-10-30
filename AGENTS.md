# AGENTS.md

A guide for AI agents working on graytimer. It is the map; the details live in
`docs/` and in comments in the code. Read the linked file before you change its area.

## What this is

A hand-built e-paper smartwatch:

- **MCU:** Seeed Xiao nRF52840.
- **Display:** 1.54" 200×200 1-bit GoodDisplay panel (GDEY0154D67), on a DESPI-C02 adapter or a Waveshare 1.54" module. Both work.
- **RTC:** RV-8803.
- **Phone link:** NFC tag, no app needed.

It shows the time over a watchface (a bitmap plus fonts). There are 115 watchfaces, and it shuffles to a new one every 10 minutes unless a phone pins one over NFC.

## Where things are

| Need | Look in |
|------|---------|
| Build, flash, pinout, power, troubleshooting | [docs/HARDWARE.md](docs/HARDWARE.md) |
| `WatchFace` fields, layouts, positioning, making a face by hand | [docs/API.md](docs/API.md), [WatchFace.h](WatchFace.h) |
| Settings (`ENABLE_*`), face catalog `allWatchFaces[]`, sleep/wake, NFC | [graytimer.ino](graytimer.ino) (top-of-section comments) |
| Rendering, display driver, includes of every font and face | [myutils.cpp](myutils.cpp), [myutils.h](myutils.h) |
| All faces by collection with numbers and previews, and the phone (NFC) commands | [docs/CATALOG.md](docs/CATALOG.md) |
| Photos of the finished watch | [docs/GALLERY.md](docs/GALLERY.md) |
| Python tools: generate, dither, preview, convert fonts | docstrings at the top of each `watchfaceutils/*.py` |
| Licences and sources of third-party art and fonts | `watchfaceutils/sources/*/README.md` |
| Notes on the user's own unit: repair log, damaged pads (gitignored, may be absent) | `local/` |

Some older docs say `epaper_watch.ino`. The sketch is `graytimer.ino`.

## How it runs

The watch sleeps in nRF52840 System OFF.

**Wakes.** Two things wake it, and either one resets the chip into `setup()`: the RV-8803 minute pulse on D2, or a phone's NFC field. Then `setup()` redraws the display and powers off again. `loop()` barely matters.

**State across sleep.** Only one byte survives sleep: the RV-8803 RAM byte. Bit 7 means the face is pinned, and bits 0-6 hold the face number. A cold boot puts the watch back in shuffle mode.

**NFC tag.** The watch is a Type 2 tag (Seeed's `XIAO_nRF52840_NFC` library). A phone writes a Text record, and the watch applies it when the phone ticks:

- `0` turns on shuffle.
- `N` pins face N.
- `YYYY-MM-DD HH:MM:SS` sets the clock.
- `refresh` does a full refresh, to clear ghosting.
- `dfu` puts it in the bootloader for a USB upload.

Reading the tag gives a status text from `writeStatusRecord`.

**Power.** Display refreshes use nearly all the power. Keep `ENABLE_SERIAL_DEBUG = false` in anything you commit.

## Rules that are easy to break

- **Face numbers are permanent.** A face's number is its position in `allWatchFaces[]`, and phones use these numbers.
  - Add new faces at the end only.
  - To retire a face, replace its line with `nullptr,  // N retired`. Never delete or reorder lines.
  - Keep the `// N` comment on every line: `generate_catalog.py` checks them.
  - There can be at most 127 faces, because the number is stored in 7 bits.
- **Flash is about 96% full.** Store new art faces cropped (`write_header(..., crop=True)` in `generate_geometric.py`), then compile and check the size.
- **Artwork is 1-bit at 200×200.**
  - Dither photos at their final size (`dither_source.py`) and never resample them afterwards.
  - Line art and geometric faces are thresholded, not dithered.
  - Dithered faces look much better on the panel than in PNG previews. Don't call them muddy or suggest retiring them. Only text that can't be read is a problem.
- **Don't hand-edit generated doc sections.** Content between the `<!-- catalog:start/end -->` markers, and the face counts, is written by `generate_catalog.py`.
- **Never run the core's `nfc_to_gpio` example.** It turns the NFC pads into GPIOs permanently.
- **Don't patch the Seeed core, board files or installed libraries.** Work around them in the sketch.
- **RTC SCL is on D6, not the Xiao default D5.** Keep it there; `local/REPAIR_LOG.md` says why.

## Adding a watchface

1. **Make the header.** Generated faces get a function in `watchfaceutils/generate_geometric.py`; run `python3 generate_geometric.py <name>`. Hand-made faces start from image2cpp output; see [docs/API.md](docs/API.md).
2. **Include it.** Add `#include "mywatchfaces/<name>.h"` to `myutils.h`.
3. **Register it.** Append `new WatchFace_<name>(),  // N` to `allWatchFaces[]`.
4. **Add it to the catalog.** Add `(name, label)` to `GROUPS` in `generate_catalog.py`. A trailing `*` in the label marks a generated face.
5. **Update the docs.** In `watchfaceutils/`, run `python3 generate_all_previews.py`, then `python3 generate_catalog.py`.
6. **Check it.** Compile (below), then look at the preview in `watchfaceutils/previews/<name>.png`. The text must be legible over the art.

New third-party art or fonts get a note in `watchfaceutils/sources/<set>/README.md` giving the source and licence. Convert fonts with `ttf_to_gfx.py`.

## Building

```bash
LC_ALL=en_US.UTF-8 "/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli" \
  --config-file ~/.arduinoIDE/arduino-cli.yaml compile --fqbn Seeeduino:nrf52:xiaonRF52840 .
```

- **Board:** use Seeed nRF52 → *Seeed XIAO nRF52840*, not the mbed board.
- **Locale:** the uploader needs a UTF-8 locale; [docs/HARDWARE.md](docs/HARDWARE.md#programming) explains the macOS IDE workaround.
- **Uploading:** USB is off in System OFF, so put the watch in the bootloader first: the user writes `dfu` over NFC (works in the case) or double-taps reset. Then upload with arduino-cli (`compile --upload -p <port>`) or from the Arduino IDE.
- **Hardware results:** you can't see the hardware, so ask the user what the display shows rather than assuming it works.
- **Local-only files:** test sketches go in `hardware/tests/`, and notes about this one physical watch (repairs, damaged pins) go in `local/`. Both are gitignored.

## Git

- **Signing:** every commit is GPG signed. Plain `git commit` signs; use `-S` when rebuilding commits.
- **No co-author:** never add a `Co-Authored-By` trailer.
- **History:** keep it to a few squashed commits.
- **Rewrites:** rewrite with `rebase`/`cherry-pick` plus re-signing, then confirm with `git verify-commit`. Never use `filter-branch`, because it strips signatures.
- **Branches:** V2 work (RTC System OFF + NFC) lives on `v2`. It merges to `master` only when the user says V2 is ready.
- **Pushing:** never push or force-push without asking.
