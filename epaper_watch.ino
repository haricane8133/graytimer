#include "myutils.h"

// ==================== CONFIGURATION ====================
const bool ENABLE_TIME_SETUP = true;  // Enable serial time input on boot

// Global RTC manager
RTCManager rtcManager;

// Track last displayed minute to detect changes
uint8_t lastDisplayedMinute = 255;  // Force first update

// new WatchFace_atat()
// new WatchFace_atdp()
// new WatchFace_b1()
// new WatchFace_bird()
// new WatchFace_bird2()
// new WatchFace_bugs()
// new WatchFace_giraffe1()
// new WatchFace_mountain2()
// new WatchFace_stormtrooper3floyd()
// new WatchFace_stormtrooper3()
WatchFace* currentWatchFace = new WatchFace_mountain2();

/**
 * Setup - runs once on power-on
 */
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== E-Paper Watch - Simple RTC Version ===");

  // Initialize display
  display.init(115200, true, 2, false);
  display.setRotation(0);

  // Initialize RTC
  if (!rtcManager.begin()) {
    Serial.println("FATAL: RTC initialization failed!");
    Serial.println("Check wiring: VCC→3V3, GND→GND, SDA→D4, SCL→D5");
    while (1) {
      delay(1000);  // Halt - cannot function without RTC
    }
  }

  // Optional: Set time via Serial
  if (ENABLE_TIME_SETUP) {
    rtcManager.setupTimeViaSerial();
  }

  // Initial display update
  Serial.println("Performing initial display update...");
  updateDisplay();
  lastDisplayedMinute = rtcManager.getCurrentMinute();

  Serial.println("\n=== Watch initialized ===");
  Serial.println("Checking RTC every second for minute changes...\n");
}

/**
 * Loop - checks RTC every second
 */
void loop() {
  // Get current minute from RTC
  uint8_t currentMinute = rtcManager.getCurrentMinute();

  // Check if minute has changed
  if (currentMinute != lastDisplayedMinute) {
    Serial.println("\n--- Minute Changed ---");
    Serial.print("Old: ");
    Serial.print(lastDisplayedMinute);
    Serial.print(" → New: ");
    Serial.println(currentMinute);

    // Update display with new time
    updateDisplay();

    // Remember this minute
    lastDisplayedMinute = currentMinute;
  }

  // Wait 1 second before checking again
  delay(1000);
}

/**
 * Update e-paper display with current time from RTC
 */
void updateDisplay() {
  // Get formatted time and date from RTC
  String timeStr = rtcManager.getFormattedTime(!currentWatchFace->noAMPM);
  String dateStr = rtcManager.getFormattedDate();

  Serial.print("Updating display - Time: ");
  Serial.print(timeStr);
  Serial.print(", Date: ");
  Serial.println(dateStr);

  unsigned long startTime = millis();

  // Draw watchface
  drawWatchFace(currentWatchFace, timeStr, dateStr);

  unsigned long elapsed = millis() - startTime;
  Serial.print("Display updated in ");
  Serial.print(elapsed);
  Serial.println(" ms\n");

  // Put display in low-power mode
  display.hibernate();
}
