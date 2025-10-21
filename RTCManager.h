#pragma once
#include <RTClib.h>
#include <Wire.h>

/**
 * RTCManager - Handles all RTC (DS3231) operations
 *
 * Responsibilities:
 * - Initialize DS3231 RTC module
 * - Configure alarm interrupts for minute-based wake-up
 * - Read current time and format for display
 * - Set initial time (for configuration)
 */
class RTCManager {
private:
  RTC_DS3231 rtc;
  bool initialized;

  const char* monthNames[12] = {
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
  };

public:
  RTCManager() : initialized(false) {}

  /**
   * Initialize RTC module
   * Returns true if successful, false otherwise
   */
  bool begin() {
    // Use default I2C pins (D4=SDA, D5=SCL)
    Wire.begin();

    if (!rtc.begin()) {
      Serial.println("ERROR: DS3231 RTC not found!");
      Serial.println("Check wiring: VCC→3V3, GND→GND, SDA→D4, SCL→D5");
      initialized = false;
      return false;
    }

    if (rtc.lostPower()) {
      Serial.println("WARNING: RTC lost power, time may be incorrect!");
      // Don't set time automatically - user should set it via setTime()
    }

    initialized = true;
    Serial.println("RTC initialized successfully");
    return true;
  }

  /**
   * Configure DS3231 to trigger alarm every minute at :00 seconds
   * This enables interrupt-driven wake-up
   */
  bool configureMinuteAlarm() {
    if (!initialized) return false;

    // Disable both alarms first
    rtc.disableAlarm(1);
    rtc.disableAlarm(2);

    // Clear any pending alarm flags
    rtc.clearAlarm(1);
    rtc.clearAlarm(2);

    // Set Alarm 1 to trigger at the start of every minute (:00 seconds)
    // DS3231_A1_Minute mode: Alarm when seconds=0, ignores minute/hour/day
    DateTime now = rtc.now();
    rtc.setAlarm1(DateTime(2000, 1, 1, 0, 0, 0), DS3231_A1_Minute);

    // Enable interrupt output on SQW/INT pin
    rtc.writeSqwPinMode(DS3231_OFF);  // Disable square wave, enable alarm interrupts

    Serial.println("RTC alarm configured for minute-based wake-up");
    return true;
  }

  /**
   * Clear the alarm flag (must be called after wake-up)
   */
  void clearAlarmFlag() {
    if (!initialized) return;
    rtc.clearAlarm(1);
  }

  /**
   * Check if alarm has fired
   */
  bool alarmFired() {
    if (!initialized) return false;
    return rtc.alarmFired(1);
  }

  /**
   * Get current time formatted as "H:MM AM/PM" (e.g., "6:24 AM")
   * Matches existing watchface format
   */
  String getFormattedTime(bool includeAMPM = true) {
    if (!initialized) return "ERR";

    DateTime now = rtc.now();

    int hour = now.hour();
    int minute = now.minute();

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

    DateTime now = rtc.now();

    int month = now.month() - 1;  // 1-based to 0-based
    if (month < 0 || month > 11) month = 0;  // Safety check

    int day = now.day();

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

    DateTime newTime(year, month, day, hour, minute, second);
    rtc.adjust(newTime);

    Serial.print("RTC time set to: ");
    Serial.println(newTime.timestamp());
    return true;
  }

  /**
   * Get current minute (0-59) - useful for detecting minute changes
   */
  uint8_t getCurrentMinute() {
    if (!initialized) return 0;
    return rtc.now().minute();
  }

  /**
   * Get RTC temperature (DS3231 has built-in temperature sensor)
   * Useful for future battery/power monitoring
   */
  float getTemperature() {
    if (!initialized) return 0.0;
    return rtc.getTemperature();
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
        Serial.print("New time: ");
        Serial.print(getFormattedTime());
        Serial.print(" ");
        Serial.println(getFormattedDate());
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
};
