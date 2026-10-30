# E-Paper Watch

* A fully customizable, ePaper, battery-optimized smartwatch.
* Auto shuffles between available watchfaces every 10 mins.
* Pick a watchface or set the clock from any phone over NFC, with a generic NFC tag app (no custom app).
* Make this if you want to build/solder every component rather than building on a compact PCB.

<table>
  <tr>
    <td align="center" width="45%">
      <img src="./docs/pics/gif_full_refresh.gif" width="400"/><br/>
      <b>Full refresh</b>
    </td>
    <td align="center" width="45%">
      <img src="./docs/pics/gif_partial_refresh.gif" width="400"/><br/>
      <b>Partial Refresh</b>
    </td>
  </tr>
</table>

**[📋 Watchface catalog: all 115 watchfaces, and how to pick one from your phone →](docs/CATALOG.md)**

[📸 Photos of the finished watch](docs/GALLERY.md)

---

## Quick Start

### Hardware Requirements

- **MCU**: Seeed Xiao nRF52840
- **Display**: GoodDisplay 1.54" (GDEH0154D67 / GDEY0154D67) on a GoodDisplay DESPI-C02 adapter
- **RTC**: RV-8803 (SmartElex module), INT wired to D2 to wake the MCU from System OFF
- **Battery**: LiPo 3.7V (300-500mAh recommended)
- **NFC antenna**: on the Xiao's NFC pads; a phone's field wakes the watch

**[📋 Detailed Hardware Guide →](docs/HARDWARE.md)**

### Software Setup

1. **Install Arduino IDE** (v1.8.x or v2.x)

2. **Add Seeed nRF52 Board Support**
   - Preferences → Additional Board URLs
   - Add: `https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json`
   - Tools → Board → Boards Manager → Search "Seeed nRF52" → Install

3. **Install Required Libraries** (via Library Manager)
   - GxEPD2 by Jean-Marc Zingg
   - Adafruit GFX Library
   - SparkFun Qwiic RTC RV8803 Arduino Library
   - Seeed's [XIAO_nRF52840_NFC](https://github.com/limengdu/XIAO_nRF52840_NFC)
     (not in Library Manager: Sketch → Include Library → Add .ZIP Library)

4. **Build and upload** with the board *Seeed XIAO nRF52840*: see
   [Programming](docs/HARDWARE.md#programming) (on macOS the IDE needs a UTF-8 locale).

**[📖 Complete API Reference →](docs/API.md)**

### Hardware

The `/hardware` folder contains the designs to 3D print for the watch case.

---

## Project Structure

```
graytimer/
├── graytimer.ino           # Main sketch
├── myutils.h               # Headers and includes
├── myutils.cpp             # Display rendering logic
├── WatchFace.h             # WatchFace class definition
├── RTCManager.h            # Time management
│
├── myfonts/                # Custom GFX fonts (66 fonts)
├── mywatchfaces/           # Watchface definitions (115 watchfaces)
│
├── hardware/               # Case models
├── watchfaceutils/         # Python development tools
│   ├── configure_watchface.py
│   ├── render_watchface.py
│   └── generate_all_previews.py
│
└── docs/                   # Documentation
    ├── README.md           # Documentation index
    ├── CATALOG.md          # All watchfaces by collection, and the NFC commands
    ├── GALLERY.md          # Photos of the finished watch
    ├── API.md              # WatchFace API reference
    └── HARDWARE.md         # Detailed hardware guide
```

---

## 📚 Full Documentation

For detailed information including configuration, troubleshooting, development tools, and more:

**[→ Read the complete documentation in the /docs folder](docs/README.md)**

---

Thanks to @vu2ow for helping out!