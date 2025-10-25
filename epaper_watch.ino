#include "myutils.h"

// ==================== CONFIGURATION ====================
const bool ENABLE_TIME_SETUP = true;  // Enable serial time input on boot
const bool ENABLE_PARTIAL_REFRESH = true;  // Enable partial refresh for faster updates
const uint8_t FULL_REFRESH_INTERVAL = 10;  // Full refresh when minute % N == 0 (e.g., :00, :10, :20, etc.)
const bool ENABLE_WATCHFACE_CYCLING = true;  // Auto-cycle through watchfaces every 10 mins

// Smart polling strategy for battery optimization
const uint16_t POLL_INTERVAL_MS = 200;      // Poll every 200ms during active window
const uint8_t WAKE_BEFORE_MINUTE_SEC = 55;  // Wake at second 55 (5-second polling window)
                                            // Range: 50-57 recommended (10s-3s window)
                                            // Lower = more battery, higher = safer

// Global RTC manager
RTCManager rtcManager;

// Track last displayed minute to detect changes
uint8_t lastDisplayedMinute = 255;  // Force first update
bool displayInitialized = false;  // Track if display has been initialized
bool firstUpdate = true;  // Track first update to force full refresh

// Watchface cycling - array of all available watchfaces
WatchFace* allWatchFaces[] = {
  new WatchFace_atat(),
  new WatchFace_atdp(),
  new WatchFace_b1(),
  new WatchFace_bird(),
  new WatchFace_bird2(),
  new WatchFace_bugs(),
  new WatchFace_giraffe1(),
  new WatchFace_mountain2(),
  new WatchFace_stormtrooper3floyd()
};
const uint8_t NUM_WATCHFACES = sizeof(allWatchFaces) / sizeof(allWatchFaces[0]);
uint8_t currentWatchFaceIndex = 0;
WatchFace* currentWatchFace = allWatchFaces[currentWatchFaceIndex];

/**
 * Setup - runs once on power-on
 */
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== E-Paper Watch ===");

  // Initialize RTC
  if (!rtcManager.begin()) {
    Serial.println("ERROR: RTC not found!");
    while (1) delay(1000);
  }

  // Optional: Set time via Serial
  if (ENABLE_TIME_SETUP) {
    rtcManager.setupTimeViaSerial();
  }

  // Initial display update
  Serial.println("Initializing display...");
  updateDisplay();
  lastDisplayedMinute = rtcManager.getCurrentMinute();

  Serial.println("Watch ready!");
  Serial.print("Smart polling: Sleep until :");
  Serial.print(WAKE_BEFORE_MINUTE_SEC);
  Serial.print("s, then poll every ");
  Serial.print(POLL_INTERVAL_MS);
  Serial.println("ms");
}

/**
 * Smart polling loop - optimized for battery life with NO DRIFT
 *
 * Strategy (drift-proof):
 * 1. After display update, check current second
 * 2. Calculate safe sleep time (to wake at WAKE_BEFORE_MINUTE_SEC)
 * 3. Sleep until configured wake second
 * 4. Poll every POLL_INTERVAL_MS until minute changes
 * 5. Repeat
 *
 * This ensures we ALWAYS catch the minute change
 * Power consumption: ~200-500µA average
 */
void loop() {
  uint8_t currentMinute = rtcManager.getCurrentMinute();

  // Check if minute changed
  if (currentMinute != lastDisplayedMinute) {
    Serial.print("Minute ");
    Serial.print(lastDisplayedMinute);
    Serial.print(" → ");
    Serial.println(currentMinute);

    updateDisplay();
    lastDisplayedMinute = currentMinute;

    // Get current second to calculate sleep duration
    DateTime now = rtcManager.rtc.now();
    uint8_t currentSecond = now.second();

    // Calculate how long to sleep to wake up at WAKE_BEFORE_MINUTE_SEC
    // We want to wake a few seconds before the minute changes to start polling
    uint16_t sleepSeconds;
    if (currentSecond < WAKE_BEFORE_MINUTE_SEC) {
      // If we're before wake time, sleep until wake second
      sleepSeconds = WAKE_BEFORE_MINUTE_SEC - currentSecond;
    } else {
      // If we're after wake time, sleep until next minute's wake second
      sleepSeconds = (60 - currentSecond) + WAKE_BEFORE_MINUTE_SEC;
    }

    // Sleep for calculated duration (minus 1 second for safety)
    if (sleepSeconds > 1) {
      sleepSeconds -= 1;  // Wake up 1 second early to be safe
      Serial.print("Sleeping for ");
      Serial.print(sleepSeconds);
      Serial.println(" seconds...");
      Serial.flush();
      delay(sleepSeconds * 1000);
    }

    // Now we're at approximately WAKE_BEFORE_MINUTE_SEC
    // Poll every POLL_INTERVAL_MS until minute changes
    Serial.print("Active polling (");
    Serial.print(POLL_INTERVAL_MS);
    Serial.println("ms) - waiting for minute change");
  }

  // Active polling mode - check every POLL_INTERVAL_MS
  // This catches the minute change quickly
  delay(POLL_INTERVAL_MS);
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

  // Check if it's time for full refresh (every 10 mins: :00, :10, :20, etc.)
  bool isFullRefreshTime = (currentMinute % FULL_REFRESH_INTERVAL == 0);

  // Cycle to next watchface if enabled and it's full refresh time
  if (ENABLE_WATCHFACE_CYCLING && isFullRefreshTime && !firstUpdate) {
    currentWatchFaceIndex = (currentWatchFaceIndex + 1) % NUM_WATCHFACES;
    currentWatchFace = allWatchFaces[currentWatchFaceIndex];
    Serial.print("Cycling to watchface #");
    Serial.print(currentWatchFaceIndex);
    Serial.print(" (");
    Serial.print(NUM_WATCHFACES);
    Serial.println(" total)");
  }

  // Determine refresh mode
  // FULL refresh: First update OR every 10 minutes (for ghosting prevention)
  // PARTIAL refresh: All other times (faster, no flicker)
  bool usePartialRefresh = ENABLE_PARTIAL_REFRESH &&
                          !firstUpdate &&
                          !isFullRefreshTime;

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
