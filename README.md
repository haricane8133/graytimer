# E-Paper Watch

* A fully customizable, ePaper, battery-optimized smartwatch.
* Auto shuffles between available watchfaces every 10 mins.
* Make this if you want to build/solder every component rather than building on a compact PCB.

[Watchface Gallery!](docs/GALLERY.md)

---

## Quick Start

### Hardware Requirements

- **MCU**: Seeed Xiao nRF52840
- **Display**: GoodDisplay 1.54" (GDEH0154D67)
- **RTC**: DS3231 with backup battery
- **Battery**: LiPo 3.7V (300-500mAh recommended)

**[📋 Detailed Hardware Guide →](docs/HARDWARE.md)**

### Software Setup

1. **Install Arduino IDE** (v1.8.x or v2.x)

2. **Add Seeed nRF52 Board Support**
   - Preferences → Additional Board URLs
   - Add: `https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json`
   - Tools → Board → Boards Manager → Search "Seeed nRF52" → Install
   - Initially had the idea of using NFC for changing watchface and setting time. So this micro controller was chosen. But we later found out that NFC tag type 4, which is required for receiving NDEF NFC records weren't supported by the arduino libraries.

3. **Install Required Libraries** (via Library Manager)
   - GxEPD2 by Jean-Marc Zingg
   - Adafruit GFX Library
   - RTClib by Adafruit

**[📖 Complete API Reference →](docs/API.md)**

---

## Project Structure

```
epaper_watch/
├── epaper_watch.ino        # Main sketch
├── myutils.h               # Headers and includes
├── myutils.cpp             # Display rendering logic
├── WatchFace.h             # WatchFace class definition
├── RTCManager.h            # Time management
│
├── myfonts/                # Custom GFX fonts (66 fonts)
├── mywatchfaces/           # Watchface definitions (54 watchfaces)
│
├── watchfaceutils/         # Python development tools
│   ├── configure_watchface.py
│   ├── render_watchface.py
│   └── generate_all_previews.py
│
└── docs/                   # Documentation
    ├── README.md           # Documentation index
    ├── GALLERY.md          # All watchfaces with previews
    ├── API.md              # WatchFace API reference
    └── HARDWARE.md         # Detailed hardware guide
```

---

## 📚 Full Documentation

For detailed information including configuration, troubleshooting, development tools, and more:

**[→ Read the complete documentation in the /docs folder](docs/README.md)**

---

Thanks to @vu2ow for helping out!