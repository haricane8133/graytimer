# Hardware Reference

Detailed hardware information for the e-paper watch project.

---

## Bill of Materials

| Component | Specification | Notes |
|-----------|---------------|-------|
| MCU | Seeed Xiao nRF52840 Sense | Nordic nRF52840, 64MHz, 1MB Flash, 256KB RAM, BLE 5.0 |
| Display | GoodDisplay GDEH0154D67 | 1.54", 200×200, SPI, partial refresh capable |
| RTC | DS3231 Module | I2C, ±3.5ppm, integrated TCXO, backup battery |
| Battery | LiPo 3.7V | Recommend 300-500mAh, JST connector |
| Button | Tactile switch (optional) | For future features |

---

## Pin Connections

### E-Paper Display (SPI)

```
MCU Pin     | Function      | EPD Pin  | Description
------------|---------------|----------|---------------------------
D10 (P1.11) | SPI MOSI      | DIN      | Data from MCU to display
D8  (P1.13) | SPI SCK       | CLK      | SPI clock signal
D1  (P0.02) | GPIO (CS)     | CS       | Chip select (active low)
D3  (P0.29) | GPIO (DC)     | DC       | Data/Command selection
D0  (P0.26) | GPIO (RST)    | RES      | Reset (active low)
D6  (P1.14) | GPIO (BUSY)   | BUSY     | Busy signal from display
            | Power         | VCC      | 3.3V from MCU
            | Ground        | GND      | Common ground
```

### RTC (I2C)

```
MCU Pin     | Function      | RTC Pin  | Description
------------|---------------|----------|---------------------------
D4  (P0.04) | I2C SDA       | SDA      | I2C data line
D5  (P0.05) | I2C SCL       | SCL      | I2C clock line
D2  (P1.10) | GPIO (INT)    | SQW/INT  | Optional: interrupt/alarm
            | Power         | VCC      | 3.3V from MCU
            | Ground        | GND      | Common ground
```

**Note**: RTC module should have backup coin cell battery (CR2032) for timekeeping during power loss.

### Optional Peripherals

```
MCU Pin     | Function      | Purpose
------------|---------------|--------------------------------
D7  (P1.15) | GPIO (Button) | User input (future features)
```

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
       │                ├─────────► DS3231 RTC (3.3V)
       │                └─────────► Peripherals
       │
       └─────────► Charging Circuit (USB-C on Xiao)
```

---

## Electrical Specifications

### nRF52840
- Operating Voltage: 3.3V (regulated from battery)
- Active Current: ~5mA
- Sleep Current: ~50µA (with RTC)
- Flash: 1MB
- RAM: 256KB

### E-Paper Display
- Operating Voltage: 3.3V
- Active Current: ~5-8mA (during refresh)
- Sleep Current: ~1µA (hibernate mode)
- Refresh Time: Partial ~200ms, Full ~1-2s
- Resolution: 200×200 pixels (1-bit)
- Size: 1.54 inches

### DS3231 RTC
- Operating Voltage: 3.3V
- Active Current: ~200µA
- Backup Current: ~3µA (from coin cell)
- Temperature Range: -40°C to +85°C
- Accuracy: ±3.5ppm (±2 minutes per year)

---

## Power Consumption

| Mode | Current | Duty Cycle | Average |
|------|---------|------------|---------|
| nRF52840 Sleep | 50µA | 95% | 47.5µA |
| nRF52840 Active | 1mA | 5% | 50µA |
| Display Partial | 5mA | 0.4% | 20µA |
| Display Full | 8mA | 0.04% | 3.2µA |
| RTC Always On | 200µA | 100% | 200µA |
| **Total** | | | **~320µA** |

**Real-world measurements**: 200-500µA depending on configuration and temperature

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
- Use: Every 10 minutes, watchface changes

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
5. **RTC backup battery** - ensure CR2032 is installed correctly
6. **Display ribbon cable** - handle carefully, easy to damage
7. **Button debouncing** - add 100nF capacitor if implementing button

---

## Troubleshooting

### Display Issues

**Display shows nothing**:
- Check 3.3V power to display
- Verify all 6 SPI connections
- Test BUSY pin (should pulse during updates)
- Try full refresh mode

**Display is garbled**:
- Check SPI connections
- Verify ground is common
- Lower SPI speed (library handles this)
- Ensure correct display model (GDEH0154D67)

**Ghosting**:
- Increase full refresh frequency
- Lower temperature improves performance
- Use full refresh more often

### RTC Issues

**RTC not detected**:
- Verify I2C connections (SDA, SCL)
- Check I2C address (0x68)
- Test with I2C scanner
- Try different RTC module

**Time drifts**:
- Check temperature (DS3231 has limits)
- Verify backup battery
- Replace RTC module if drift persists

### Power Issues

**Battery drains quickly**:
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

## Recommended Tools

- Soldering iron (temperature controlled)
- Multimeter (for voltage/current testing)
- Logic analyzer (for debugging SPI/I2C)
- USB-C cable (for programming and charging)
- JST connector crimper (for battery connections)

---

**Back to**: [Main README](README.md)
