#include "myutils.h"

// ==================== CONFIGURATION ====================
const bool ENABLE_TIME_SETUP = true;  // Enable serial time input on boot
const bool ENABLE_PARTIAL_REFRESH = true;  // Enable partial refresh for faster updates
const uint8_t FULL_REFRESH_INTERVAL = 10;  // Full refresh when minute % N == 0 (e.g., :00, :10, :20, etc.)

// Global RTC manager
RTCManager rtcManager;

// Track last displayed minute to detect changes
uint8_t lastDisplayedMinute = 255;  // Force first update
bool displayInitialized = false;  // Track if display has been initialized
bool firstUpdate = true;  // Track first update to force full refresh

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
  // Initialize display ONLY ONCE on first call
  if (!displayInitialized) {
    display.init(115200, true, 2, false);
    display.setRotation(0);
    displayInitialized = true;
  }

  // Get formatted time and date from RTC
  String timeStr = rtcManager.getFormattedTime(!currentWatchFace->noAMPM);
  String dateStr = rtcManager.getFormattedDate();
  uint8_t currentMinute = rtcManager.getCurrentMinute();

  // Determine refresh mode
  // FULL refresh: First update OR every 10 minutes (for ghosting prevention)
  // PARTIAL refresh: All other times (faster, no flicker)
  bool usePartialRefresh = ENABLE_PARTIAL_REFRESH &&
                          !firstUpdate &&
                          (currentMinute % FULL_REFRESH_INTERVAL != 0);

  if (firstUpdate) {
    firstUpdate = false;
  }

  unsigned long startTime = millis();

  // Draw watchface
  drawWatchFace(currentWatchFace, timeStr, dateStr, usePartialRefresh);

  unsigned long elapsed = millis() - startTime;
  Serial.print(timeStr);
  Serial.print(" (");
  Serial.print(usePartialRefresh ? "partial" : "full");
  Serial.print(", ");
  Serial.print(elapsed);
  Serial.println("ms)");

  // Put display in low-power mode
  display.hibernate();
}
