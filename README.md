# DIY . watch . eInk . NFC

- GrayTimer is a fully customizable watch powered by my two most favorite technologies - eInk and NFC!
- Solder the whole thing easily, rather than building a PCB.
- 3D print yourself a case. Sew up a regular strap. Stuff everything in.
- Tap your phone to pick a watch face, set the time, clear ghosting, or get ready for a firmware update, all without opening the case.
- Run Claude Code, Codex or any AI coding agent, to assist you develop code or generate watch faces

<table>
  <tr>
    <td rowspan="3" align="center">
      <img src="./docs/pics/hero.jpg" alt="Gray Timer: a watch made by Hari &amp; Rajesh" width="300"/>
    </td>
    <td align="center" valign="top">
      <img src="./docs/pics/photo_gem.jpg" alt="The watch showing a gem watchface" width="200"/><br/>
      A new face every 10 minutes
    </td>
  </tr>
  <tr>
    <td align="center" valign="top">
      <img src="./docs/pics/photo_feather.jpg" alt="The watch showing a peacock feather watchface" width="200"/><br/>
      Line art looks crisp on e-paper
    </td>
  </tr>
  <tr>
    <td align="center" valign="top">
      <img src="./docs/pics/photo_dfu.jpg" alt="The watch in a hand, showing its firmware update screen" width="200"/><br/>
      Ready for an update with one tap
    </td>
  </tr>
</table>

**[See all 116 watchfaces / Get NFC commands](docs/CATALOG.md)**

[Photos of the finished watch](docs/GALLERY.md) · [How it was built](docs/BUILD.md)

---

## Build your own

### What you need

- **MCU**: Seeed Xiao nRF52840
- **Display**: GoodDisplay 1.54" e-paper (GDEY0154D67 / GDEH0154D67). Either the bare panel on a
  GoodDisplay DESPI-C02 adapter, or a Waveshare 1.54" e-Paper Module with the panel already on it
- **RTC**: RV-8803 (SmartElex module), with INT wired to D2 so it can wake the Xiao
- **Battery**: LiPo 3.7V, 300-500mAh
- **NFC antenna**: on the Xiao's NFC pads
- **Case**: 3D print the main box and lid in [`/hardware`](hardware) ([print notes](docs/HARDWARE.md#case))

**[Wiring, power and assembly →](docs/HARDWARE.md)**

### Software

1. **Install the Arduino IDE.**

2. **Add the Seeed nRF52 boards**
   - Preferences → Additional Board URLs
   - Add: `https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json`
   - Tools → Board → Boards Manager → search "Seeed nRF52" → Install

3. **Install the libraries** (from the Library Manager)
   - GxEPD2 by Jean-Marc Zingg
   - Adafruit GFX Library
   - SparkFun Qwiic RTC RV8803 Arduino Library
   - Seeed's [XIAO_nRF52840_NFC](https://github.com/limengdu/XIAO_nRF52840_NFC)
     (not in the Library Manager: Sketch → Include Library → Add .ZIP Library)

4. **Upload** with the board *Seeed XIAO nRF52840*. The watch sleeps with USB off, so first
   write `dfu` from your phone (or double-tap the reset button), then upload. On macOS the IDE
   needs one small fix first: see [Programming](docs/HARDWARE.md#programming).

**[Make your own watchface →](docs/API.md)**

---

## What's inside

```
graytimer/
├── graytimer.ino           # The sketch: settings, the list of faces, sleep and NFC
├── myutils.h / .cpp        # Drawing the time on the display
├── WatchFace.h             # What a watchface is made of
├── RTCManager.h            # The clock chip
├── dfu_screen.h            # The screen shown while waiting for an upload
│
├── myfonts/                # Fonts
├── mywatchfaces/           # One file per watchface
│
├── hardware/               # Case models to 3D print
├── watchfaceutils/         # Python tools to make and preview watchfaces
├── docs/                   # Catalog, gallery, hardware guide and API
└── AGENTS.md               # A short guide for AI coding agents
```

**[→ All the documentation](docs/README.md)**

---

Thanks to @vu2ow for the help and inspiration behind all my projects!
