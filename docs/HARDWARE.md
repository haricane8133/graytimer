# Hardware Reference

Detailed hardware information for the e-paper watch project.

---

## Bill of Materials

| Component | Specification | Notes |
|-----------|---------------|-------|
| MCU | Seeed Xiao nRF52840 | Nordic nRF52840, 64MHz, 1MB Flash, 256KB RAM, BLE 5.0 |
| Display | GoodDisplay GDEY0154D67 (ribbon marked FPC-B001) | 1.54", 200×200, SPI, partial refresh capable; driven with GxEPD2's `GxEPD2_154_D67` |
| Display adapter | GoodDisplay DESPI-C02 | 24-pin FPC breakout with the high-voltage boost; RESE switch |
| RTC | SmartElex RV-8803 module | I2C, ±3ppm temperature compensated, 0.24µA, INT wakes the MCU, onboard backup cell |
| Battery | LiPo 3.7V | Recommend 300-500mAh, JST connector |
| NFC antenna | 13.56 MHz coil | On the Xiao's NFC pads; a phone picks the face or sets the time |
| Button | Tactile switch (optional) | For future features |

---

## Pin Connections

### E-Paper Display (SPI)

Breakout boards label the same two SPI lines differently; all names in the
"EPD Pin" column are equivalent.

```
MCU Pin     | Function      | EPD Pin            | Description
------------|---------------|--------------------|---------------------------
D10 (P1.15) | SPI MOSI      | DAT / DIN / SDA    | Data from MCU to display
D8  (P1.13) | SPI SCK       | SCL / CLK / SCK    | SPI clock signal
D1  (P0.03) | GPIO (CS)     | CS                 | Chip select (active low)
D3  (P0.29) | GPIO (DC)     | DC                 | Data/Command selection
D0  (P0.02) | GPIO (RST)    | RES / RST          | Reset (active low)
D9  (P1.14) | GPIO (BUSY)   | BUSY               | Busy signal from display
            | Power         | VCC / 3V3          | 3.3V from MCU (not 5V)
            | Ground        | GND                | Common ground
```

DESPI-C02 labels: SDI = MOSI (D10), SCK = SCK (D8), RES = RST (D0), D/C = DC (D3).

**BUSY note**: the firmware reads BUSY on **D9** so each wake ends as soon as the
panel finishes instead of sleeping through worst-case fixed delays. If BUSY
misbehaves, pass `-1` for it in `myutils.cpp` to fall back to fixed delays.
If the display breakout has a MISO/SDO pin, leave it unconnected.

### RTC (I2C)

```
MCU Pin     | Function      | RTC Pin  | Description
------------|---------------|----------|---------------------------
D4  (P0.04) | I2C SDA       | SDA      | I2C data line
D6  (P1.11) | I2C SCL       | SCL      | I2C clock line (see note)
D2  (P0.28) | GPIO (INT)    | INT      | Minute pulse, wakes MCU from System OFF
            | Power         | 3V3      | 3.3V from MCU
            | Ground        | GND      | Common ground
            | —             | EVI      | Not connected (event input, unused)
            | —             | CLKOUT   | Not connected
            | —             | CLKOE    | Not connected (see note)
```

**SCL is on D6, not the Xiao's default D5.** The firmware sets the pins with
`Wire.setPins(RTC_SDA, RTC_SCL)`; to use another pin, change `RTC_SCL` in `myutils.h`.

**Notes** (from the SparkFun RV-8803 Qwiic design, which the SmartElex board
appears to follow — check against your board):
- **Cut the power-LED jumper** ("LED"). The LED sits on 3V3 and draws on the
  order of a milliamp, more than everything else in the watch put together.
- CLKOE is pulled to GND by a 100k resistor on the board, so the 32 kHz CLKOUT
  is already off. Leave it unconnected; tying it high would waste current.
- INT is open-drain with a 100k pull-up on the board.
- The backup coin cell on the back keeps time while the LiPo is flat or
  disconnected. If it ever runs down too, the RV-8803 sets its V2F flag and
  the time must be set again over serial.
- The board's 4.7k I2C pull-ups ("I2C" jumper) are the only ones on the bus;
  leave them in.

### NFC Antenna

```
MCU Pad       | Function | Description
--------------|----------|---------------------------
NFC1 (P0.09)  | NFC      | Antenna coil, either end
NFC2 (P0.10)  | NFC      | Antenna coil, other end
```

The pads are on the back of the Xiao. The firmware makes the watch an NFC Type 2
tag (Seeed's XIAO_nRF52840_NFC library); see [the catalog](CATALOG.md) for what a
phone can write.

**Range**: with Seeed's 13.56 MHz antenna (made for their PN532 reader boards)
the phone must be held very close and well aligned, and iOS now and then says
"Tag not supported". The Xiao has no matching capacitors on these pads, so the
coil is untuned. Seeed reports the Molex 1462360051 and Taoglas FXR.07.A.DG
working without capacitors, and the Taoglas better with 43 pF (C0G) from each pad
to GND. Keep the coil away from the LiPo's metal foil, or put a ferrite sheet
between them.

**NEVER run the core's `nfc_to_gpio` example**: it permanently turns these pads
into GPIOs (a one-way UICR change).

### Optional Peripherals

```
MCU Pin     | Function      | Purpose
------------|---------------|--------------------------------
D7  (P1.12) | GPIO (Button) | User input (future features)
```

Free pin: **D5** (P0.05). Every other Xiao pin is assigned above.

---

## Power Distribution

```
┌──────────────┐
│   LiPo       │
│   Battery    │
│   3.7V       │
└──────┬───────┘
       │
       ├─────────► nRF52840 (onboard regulator → 3.3V)
       │                │
       │                ├─────────► E-Paper Display (3.3V)
       │                ├─────────► RV-8803 RTC (3.3V)
       │                └─────────► Peripherals
       │
       └─────────► Charging Circuit (USB-C on Xiao)
```

---

## Electrical Specifications

### nRF52840
- Operating Voltage: 3.3V (regulated from battery)
- Active Current: ~5mA
- System OFF: ~0.4µA (RAM off, woken by a GPIO edge as a reset)
- Flash: 1MB
- RAM: 256KB

### E-Paper Display
- Operating Voltage: 3.3V
- Active Current: ~5-8mA (during refresh)
- Sleep Current: ~1µA (hibernate mode)
- Refresh Time: Partial ~200ms, Full ~1-2s
- Resolution: 200×200 pixels (1-bit)
- Size: 1.54 inches

### RV-8803 RTC
- Operating Voltage: 3.3V
- Timekeeping Current: ~0.24µA
- Temperature Range: -40°C to +85°C
- Accuracy: ±3ppm temperature compensated (±1.6 minutes per year)

---

## Power Consumption

The watch sits in nRF52840 System OFF. At every minute rollover the RV-8803
pulls INT (D2) low, which resets the chip into `setup()`; it reads the time,
refreshes the display, hibernates it, clears the RTC flag and goes back to
System OFF. The face number and mode (shuffle or pinned) survive in the
RV-8803's user RAM register.

A phone's NFC field also wakes it: the NFCT peripheral keeps sensing for a field
in System OFF, a passive detector that adds next to nothing to the sleep
current. An NFC wake serves the tag until the phone has been gone for 3 s,
redraws only if the phone wrote a command, and goes back to System OFF. The tag
and its 64 MHz crystal never start on a minute wake, so those cost the same as
before.

Estimates (not yet measured):

| Mode | Current | Duty Cycle | Average |
|------|---------|------------|---------|
| Sleep floor (nRF System OFF, RTC, panel deep sleep, regulator, flash standby) | ~3–10µA | ~98% | ~3–10µA |
| Wake + partial refresh, 9 of every 10 minutes | ~5mA for ~0.7s | 1.1% | ~55µA |
| Wake + full refresh, every 10th minute | ~5mA for ~2.5s | 0.4% | ~20µA |
| **Total** | | | **~80–90µA** |

A face pinned over NFC gets a full refresh only at :00 and :30
(`PINNED_FULL_REFRESH_INTERVAL`), which saves a little more.

The display refreshes are now almost the whole budget, so the remaining levers
are fewer refreshes (e.g. `FULL_REFRESH_INTERVAL`) rather than sleep current.
Each wake also spends ~0.5 s in the bootloader before `setup()` runs.

---

## Display Technology

### E-Paper Characteristics

**Advantages**:
- Ultra-low power (only consumes power during updates)
- Readable in bright sunlight
- Wide viewing angle (~180°)
- Retains image without power
- No backlight needed

**Limitations**:
- Slow refresh rate (1-2 seconds)
- Monochrome only (1-bit)
- Ghosting with partial refresh
- Temperature sensitive

### Refresh Modes

**Full Refresh**:
- Duration: ~1-2 seconds
- Power: ~8mA
- Effect: Complete redraw, eliminates ghosting
- Use: Every 10 minutes in shuffle mode (with a new face), at :00 and :30 for a pinned face

**Partial Refresh**:
- Duration: ~200-500ms
- Power: ~5mA
- Effect: Update changed areas only
- Use: Minute updates
- Limitation: May accumulate ghosting

---

## Assembly Notes

1. **Test components** individually before assembly
2. **Check polarity** of battery and power connections
3. **Verify voltage** is 3.3V at all component inputs
4. **Secure connections** - loose wires cause intermittent issues
5. **RTC power LED** - cut the RV-8803 board's LED jumper before closing the case
6. **Display ribbon cable** - handle carefully, easy to damage. The DESPI-C02
   connector contacts both faces, so a flipped ribbon still connects but with
   the pin order reversed. Match pin 1 (or the orientation the panel had on its
   original board) before powering, then confirm with `ENABLE_SERIAL_DEBUG`
   on: GxEPD2 printing `_Update_Full` of about 2,180,000 µs on a cold boot
   means it is seated correctly. Keep case edges
   off the two glass corners beside the ribbon.
7. **DESPI-C02 RESE switch** - start at 0.47Ω
8. **Button debouncing** - add 100nF capacitor if implementing button

---

## Troubleshooting

### Display Issues

**Display shows nothing**:
- Check 3.3V power to display
- Verify the 5 signal connections (DAT, SCL, CS, DC, RES) plus GND
- Set `ENABLE_SERIAL_DEBUG = true` and watch a cold boot: GxEPD2 prints its
  diagnostics (`_Update_Full : <µs>` or `Busy Timeout!`)
- If the RTC is not found the firmware halts *before* touching the display
  (`setup()` loops forever) — a dead display can really be an RTC wiring fault
- Try full refresh mode

**GxEPD2 prints `_Update_Full : 0`**: the panel controller is not answering.
The ribbon is reversed or not seated (see the ribbon note in Assembly Notes).

**`_Update_Full` ≈ 2,180,000 µs but the image never changes**: the controller
works but the high voltage does not reach the ink. Try the DESPI-C02 RESE switch
in its other position; otherwise the panel is damaged (check the glass corners
next to the ribbon for chips or cracks).

**Display is garbled**:
- Check SPI connections
- Verify ground is common
- Lower SPI speed (library handles this)
- Ensure correct display model (GDEY0154D67, ribbon FPC-B001; GDEH0154D67 works the same)

**Ghosting**:
- Increase full refresh frequency
- Lower temperature improves performance
- Use full refresh more often

### RTC Issues

**RTC not detected**:
- Verify I2C connections (SDA, SCL)
- Check I2C address (0x32)
- Test with I2C scanner
- Try different RTC module

**Display never updates after the first boot**: INT is not reaching D2, or the
RV-8803 lost its settings. The firmware re-arms the minute interrupt on every
boot, so a reset fixes the latter.

**Watch redraws in a tight loop / battery drains fast**: INT is stuck low. The
firmware clears the update flag before sleeping; check that nothing else pulls
D2 low.

**Time drifts**:
- Check the backup cell on the RTC board
- Replace RTC module if drift persists

### Power Issues

**Battery drains quickly**:
- Cut the RTC board's power LED jumper
- Disable serial debug
- Check for shorts
- Measure current with multimeter
- Verify display hibernates after updates

**Device won't power on**:
- Check battery voltage (should be >3.0V)
- Verify polarity
- Test USB charging circuit
- Check for shorts

---

## Programming

Board: **Seeed nRF52 Boards → Seeed XIAO nRF52840** (FQBN
`Seeeduino:nrf52:xiaonRF52840`), not the mbed "XIAO nRF52840 (No Updates)" board.

The core's uploader, `adafruit-nrfutil`, refuses to run without a UTF-8 locale.
On macOS the Arduino IDE 2 gets none when started from the Dock (and it rewrites
`LC_ALL` to `C` when `LC_ALL` is set), so IDE uploads fail with a "Python was
configured to use ASCII" error. Give apps a UTF-8 `LANG`, then restart the IDE;
this lasts until the next reboot:

```bash
launchctl setenv LANG en_US.UTF-8
```

Or build and upload from a terminal:

```bash
cd graytimer && LC_ALL=en_US.UTF-8 "/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli" --config-file ~/.arduinoIDE/arduino-cli.yaml compile --upload -p "$(ls /dev/cu.usbmodem* | head -1)" --fqbn Seeeduino:nrf52:xiaonRF52840 .
```

The watch needs Seeed's [XIAO_nRF52840_NFC](https://github.com/limengdu/XIAO_nRF52840_NFC)
library (Sketch → Include Library → Add .ZIP Library).

The watch spends nearly all its time in System OFF, where USB is not running, so
the automatic upload (1200-baud touch) cannot reach it. Put it in the bootloader
first, either way:

- **Over NFC:** write the text `dfu` from a phone (see [the catalog](CATALOG.md)).
  This works with the watch closed in its case.
- **Reset button:** double-tap the Xiao's reset button. This is the fallback if
  a broken firmware no longer answers NFC.

After `dfu` the screen says "GrayTimer is now in DFU mode" and the bootloader
waits for an upload, as it does after a double-tap. It keeps USB running, which
drains the battery far faster than sleep, so upload soon. Any upload, even of
the same firmware, brings the watch back.

A cold boot (reset button, power-on, upload) waits for the serial time line when `ENABLE_TIME_SETUP` and
`ENABLE_SERIAL_DEBUG` are on; the time can also be set from a phone over NFC
(see [the catalog](CATALOG.md)).

---

## Recommended Tools

- Soldering iron (temperature controlled)
- Multimeter (for voltage/current testing)
- Logic analyzer (for debugging SPI/I2C)
- USB-C cable (for programming and charging)
- JST connector crimper (for battery connections)

---

**Back to**: [Main README](README.md)
