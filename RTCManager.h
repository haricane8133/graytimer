#pragma once
#include <SparkFun_RV8803.h>
#include <Wire.h>

/**
 * RTCManager - Handles all RTC (RV-8803) operations
 *
 * Responsibilities:
 * - Initialize the RV-8803 and its once-per-minute INT pulse (wakes the nRF52840)
 * - Read current time and format for display
 * - Set initial time (for configuration)
 * - Keep one byte of watch state in the RTC's user RAM across System OFF
 */
class RTCManager {
public:
  RV8803 rtc;  // Public for direct register access

private:
  bool initialized;

  // RV-8803 user RAM register (0x07) bit 7 marks a saved watchface index.
  // The library only touches this register from setEpoch()/setTimeZoneQuarterHours(),
  // which this sketch never calls.
  static const uint8_t FACE_VALID = 0x80;

  const char* monthNames[12] = {
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
  };

public:
  RTCManager() : initialized(false) {}

  /**
   * Initialize RTC module and arm the minute interrupt
   * Returns true if successful, false otherwise
   */
  bool begin() {
    // D4=SDA, D6=SCL (see myutils.h); must be set before Wire.begin()
    Wire.setPins(RTC_SDA, RTC_SCL);
    Wire.begin();

    if (!rtc.begin()) {
      Serial.println("ERROR: RV-8803 RTC not found!");
      Serial.println("Check wiring: 3V3→3V3, GND→GND, SDA→D4, SCL→D6, INT→D2");
      initialized = false;
      return false;
    }

    rtc.set24Hour();  // Library defaults to 12-hour conversion; we format AM/PM ourselves

    // INT (open-drain, active low) pulses at every minute rollover (second 00).
    // Written on every boot so the setting heals itself if the RTC was reset.
    rtc.setPeriodicTimeUpdateFrequency(TIME_UPDATE_1_MINUTE);
    rtc.enableHardwareInterrupt(UPDATE_INTERRUPT);

    initialized = true;
    return refresh();
  }

  /**
   * True if the RTC supply dropped low enough that the time is invalid
   * (V2F flag). Cleared by setTime().
   */
  bool lostPower() {
    if (!initialized) return true;
    return rtc.getInterruptFlag(FLAG_V2F);
  }

  /**
   * Read the time registers into the library's cache. All getters below
   * format from that cache, so call this once per wake.
   */
  bool refresh() {
    if (!initialized) return false;
    return rtc.updateTime();
  }

  /**
   * Clear the minute-update flag. Must happen before System OFF: a set flag
   * keeps the next minute from producing a fresh falling edge on INT.
   */
  void clearMinuteInterrupt() {
    if (!initialized) return;
    rtc.clearInterruptFlag(FLAG_UPDATE);
  }

  /**
   * True if a minute rolled over since the last clearMinuteInterrupt()
   */
  bool minuteInterruptPending() {
    if (!initialized) return false;
    return rtc.getInterruptFlag(FLAG_UPDATE);
  }

  /**
   * Watchface index saved before the last System OFF, or -1 if none
   */
  int loadFaceIndex() {
    if (!initialized) return -1;
    uint8_t v = rtc.readRegister(RV8803_RAM);
    return (v & FACE_VALID) ? (v & 0x7F) : -1;
  }

  void saveFaceIndex(uint8_t index) {
    if (!initialized) return;
    rtc.writeRegister(RV8803_RAM, FACE_VALID | (index & 0x7F));
  }

  /**
   * Get current time formatted as "H:MM AM/PM" (e.g., "6:24 AM")
   * Matches existing watchface format
   */
  String getFormattedTime(bool includeAMPM = true) {
    if (!initialized) return "ERR";

    int hour = rtc.getHours();
    int minute = rtc.getMinutes();

    // Convert to 12-hour format
    bool isPM = (hour >= 12);
    if (hour == 0) {
      hour = 12;  // Midnight = 12 AM
    } else if (hour > 12) {
      hour -= 12;  // 13:00 → 1 PM
    }

    // Format: "H:MM AM/PM" (no leading zero on hour)
    String timeStr = String(hour) + ":";

    if (minute < 10) {
      timeStr += "0";  // Add leading zero to minutes
    }
    timeStr += String(minute);

    if (includeAMPM) {
      timeStr += isPM ? " PM" : " AM";
    }

    return timeStr;
  }

  /**
   * Get current date formatted as "Mon DD" (e.g., "Jun 24")
   * Matches existing watchface format
   */
  String getFormattedDate() {
    if (!initialized) return "ERR";

    int month = rtc.getMonth() - 1;  // 1-based to 0-based
    if (month < 0 || month > 11) month = 0;  // Safety check

    int day = rtc.getDate();

    String dateStr = String(monthNames[month]) + " " + String(day);
    return dateStr;
  }

  /**
   * Set RTC time manually
   * Example: setTime(2025, 10, 20, 17, 30, 0) = Oct 20, 2025, 5:30:00 PM
   */
  bool setTime(uint16_t year, uint8_t month, uint8_t day,
               uint8_t hour, uint8_t minute, uint8_t second) {
    if (!initialized) return false;

    if (!rtc.setTime(second, minute, hour, dayOfWeek(year, month, day), day, month, year)) {
      return false;
    }
    rtc.clearInterruptFlag(FLAG_V2F);
    rtc.clearInterruptFlag(FLAG_V1F);
    refresh();

    Serial.print("RTC time set to: ");
    Serial.print(getFormattedTime());
    Serial.print(" ");
    Serial.println(getFormattedDate());
    return true;
  }

  /**
   * Get current minute (0-59) from the last refresh()
   */
  uint8_t getCurrentMinute() {
    if (!initialized) return 0;
    return rtc.getMinutes();
  }

  /**
   * Check if RTC is initialized and working
   */
  bool isInitialized() {
    return initialized;
  }

  /**
   * Interactive time setup via Serial
   * Waits for user input in format: YYYY,MM,DD,HH,MM,SS
   * Timeout after 15 seconds
   */
  bool setupTimeViaSerial(unsigned long timeoutMs = 15000) {
    Serial.println("\n=== RTC Time Setup ===");
    Serial.println("Enter current time in format: YYYY,MM,DD,HH,MM,SS");
    Serial.println("Example: 2025,10,20,17,30,0  (Oct 20, 2025, 5:30:00 PM)");
    Serial.print("Waiting ");
    Serial.print(timeoutMs / 1000);
    Serial.println(" seconds for input...");

    unsigned long startTime = millis();
    String input = "";

    while (millis() - startTime < timeoutMs) {
      if (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
          if (input.length() > 0) {
            return parseAndSetTime(input);
          }
        } else {
          input += c;
        }
      }
      delay(10);  // Small delay to prevent tight loop
    }

    refresh();
    Serial.println("Timeout - using current RTC time");
    Serial.print("Current RTC time: ");
    Serial.print(getFormattedTime());
    Serial.print(" ");
    Serial.println(getFormattedDate());
    return false;
  }

  /**
   * Parse time string and set RTC
   * Format: YYYY,MM,DD,HH,MM,SS
   * Returns true if successfully parsed and set
   */
  bool parseAndSetTime(String input) {
    int year, month, day, hour, minute, second;

    if (sscanf(input.c_str(), "%d,%d,%d,%d,%d,%d",
               &year, &month, &day, &hour, &minute, &second) == 6) {

      if (setTime(year, month, day, hour, minute, second)) {
        Serial.println("✓ RTC time set successfully!");
        return true;
      } else {
        Serial.println("✗ Failed to set RTC time");
        return false;
      }
    } else {
      Serial.println("✗ Invalid format - using current RTC time");
      return false;
    }
  }

private:
  // 0 = Sunday ... 6 = Saturday (Sakamoto's method)
  static uint8_t dayOfWeek(int y, int m, int d) {
    static const int t[] = {0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4};
    if (m < 3) y -= 1;
    return (y + y / 4 - y / 100 + y / 400 + t[m - 1] + d) % 7;
  }
};
