#include "myutils.h"

// ==================== CONFIGURATION ====================
// Serial time setup: on boot the watch waits 15 s for a line on the Serial
// Monitor (115200 baud) in the format  YYYY,MM,DD,HH,MM,SS  (24-hour clock),
// e.g.  2026,9,14,17,30,0  -> 14 Sep 2026, 5:30:00 PM.  Send with a newline.
// No input within 15 s -> keeps the current RTC time.  Serial.begin() only runs
// when ENABLE_SERIAL_DEBUG is true, so enable both, set the time, then set both
// back to false and re-flash for deployment.
const bool ENABLE_TIME_SETUP = false;  // Enable serial time input on boot
const bool ENABLE_PARTIAL_REFRESH = true;  // Enable partial refresh for faster updates
const uint8_t FULL_REFRESH_INTERVAL = 10;  // Full refresh when minute % N == 0 (e.g., :00, :10, :20, etc.)
const bool ENABLE_WATCHFACE_CYCLING = true;  // Auto-cycle through watchfaces every 10 mins
const bool ENABLE_SERIAL_DEBUG = false;  // Disable Serial to save ~1-2mA power (set false for deployment)

// Smart polling strategy for battery optimization
const uint16_t POLL_INTERVAL_MS = 200;      // Poll every 200ms during active window
const uint8_t WAKE_BEFORE_MINUTE_SEC = 57;  // Wake at second 57 (3-second polling window)
                                            // Range: 50-57 recommended (10s-3s window)
                                            // Lower = more battery, higher = safer
                                            // Changed from 55 to 57 for better battery (2s more sleep)

// Serial debug macros (only print if enabled)
#define DEBUG_PRINT(x) if(ENABLE_SERIAL_DEBUG) Serial.print(x)
#define DEBUG_PRINTLN(x) if(ENABLE_SERIAL_DEBUG) Serial.println(x)
#define DEBUG_FLUSH() if(ENABLE_SERIAL_DEBUG) Serial.flush()

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
  new WatchFace_ben10(),
  new WatchFace_bird(),
  new WatchFace_bird2(),
  new WatchFace_bugs(),
  // new WatchFace_claw(),
  new WatchFace_claw2(),
  new WatchFace_claw3(),
  // new WatchFace_crow(),
  new WatchFace_dog(),
  // new WatchFace_giraffe1(),
  new WatchFace_guitar1(),
  new WatchFace_guitar2(),
  new WatchFace_h(),
  new WatchFace_harley(),
  new WatchFace_harry934(),
  new WatchFace_herbert(),
  new WatchFace_hogwarts(),
  new WatchFace_hogwarts2(),
  new WatchFace_hogwarts3(),
  new WatchFace_hogwarts4(),
  new WatchFace_jitsu1(),
  new WatchFace_jitsu2(),
  new WatchFace_jitsu3(),
  new WatchFace_jitsu4(),
  new WatchFace_jitsu5(),
  new WatchFace_krishna(),
  new WatchFace_macaw(),
  new WatchFace_mikew(),
  new WatchFace_mountain1(),
  new WatchFace_mountain2(),
  new WatchFace_peacock(),
  new WatchFace_peacock3(),
  new WatchFace_pegasus(),
  new WatchFace_penguin_beatles(),
  new WatchFace_penguins(),
  new WatchFace_planets(),
  new WatchFace_ps(),
  new WatchFace_saturn(),
  new WatchFace_sensei(),
  new WatchFace_sortinghat(),
  new WatchFace_stormtrooper2(),
  new WatchFace_stormtrooper3floyd(),
  new WatchFace_sullivan(),
  new WatchFace_thiruman(),
  new WatchFace_tom(),
  new WatchFace_tree(),
  new WatchFace_walker(),
  new WatchFace_xwing(),
  new WatchFace_zebra(),
  // generated geometric set
  new WatchFace_tie(),
  new WatchFace_deathstar(),
  new WatchFace_hallows(),
  new WatchFace_prism(),
  new WatchFace_orbit(),
  new WatchFace_orion(),
  new WatchFace_kolam(),
  new WatchFace_vinyl(),
  new WatchFace_sunburst(),
  new WatchFace_minimal(),
  new WatchFace_moon(),
  new WatchFace_glasses(),
  new WatchFace_snitch(),
  new WatchFace_lightsaber(),
  new WatchFace_rocket(),
  new WatchFace_cassette(),
  new WatchFace_equalizer(),
  new WatchFace_mandala(),
  new WatchFace_forest(),
  new WatchFace_dial(),
  new WatchFace_waves(),
  new WatchFace_r2d2(),
  new WatchFace_falcon(),
  new WatchFace_hedwig(),
  new WatchFace_penguin(),
  new WatchFace_headphones(),
  new WatchFace_ufo(),
  new WatchFace_balloon(),
  new WatchFace_lighthouse(),
  new WatchFace_diya(),
  new WatchFace_coffee(),
  new WatchFace_bicycle(),
  new WatchFace_whale(),
  new WatchFace_thunderjaw(),
  new WatchFace_watcher(),
  new WatchFace_sawtooth(),
  new WatchFace_stormbird(),
  new WatchFace_strider(),
  new WatchFace_vader(),
  new WatchFace_mando(),
  new WatchFace_boodoor(),
  new WatchFace_astronaut(),
  new WatchFace_cat(),
  new WatchFace_camera(),
  new WatchFace_sailboat(),
  new WatchFace_hari()
};
const uint8_t NUM_WATCHFACES = sizeof(allWatchFaces) / sizeof(allWatchFaces[0]);
uint8_t currentWatchFaceIndex = 0;
WatchFace* currentWatchFace = allWatchFaces[currentWatchFaceIndex];

// True random numbers from the nRF52840 RNG peripheral (thermal noise, with
// bias correction). Direct register access is fine because this sketch never
// enables the SoftDevice (no BLE). Each byte takes ~120us with DERCEN on.
uint8_t hwRandomByte() {
  NRF_RNG->CONFIG = RNG_CONFIG_DERCEN_Msk;
  NRF_RNG->EVENTS_VALRDY = 0;
  NRF_RNG->TASKS_START = 1;
  while (NRF_RNG->EVENTS_VALRDY == 0) {}
  uint8_t v = NRF_RNG->VALUE;
  NRF_RNG->TASKS_STOP = 1;
  return v;
}

// Uniform integer in [0, n) with no modulo bias (rejection sampling)
uint8_t hwRandom(uint8_t n) {
  uint16_t limit = 256 - (256 % n);
  uint16_t v;
  do { v = hwRandomByte(); } while (v >= limit);
  return v % n;
}

// Independent uniform pick over every face except the one currently shown
uint8_t pickNextWatchFace(uint8_t current) {
  if (NUM_WATCHFACES < 2) return 0;
  uint8_t r = hwRandom(NUM_WATCHFACES - 1);
  return (r >= current) ? r + 1 : r;  // skip `current` without re-rolling
}

/**
 * Setup - runs once on power-on
 */
void setup() {
  if (ENABLE_SERIAL_DEBUG) {
    Serial.begin(115200);
    while (!Serial) delay(10);
  }

  DEBUG_PRINTLN("\n=== E-Paper Watch ===");

  // Initialize RTC
  if (!rtcManager.begin()) {
    DEBUG_PRINTLN("ERROR: RTC not found!");
    while (1) delay(1000);
  }

  // Pick a random initial watchface (hardware RNG, no seeding needed)
  currentWatchFaceIndex = hwRandom(NUM_WATCHFACES);

  currentWatchFace = allWatchFaces[currentWatchFaceIndex];
  DEBUG_PRINT("Initial random watchface #");
  DEBUG_PRINTLN(currentWatchFaceIndex);

  // Optional: Set time via Serial
  if (ENABLE_TIME_SETUP) {
    rtcManager.setupTimeViaSerial();
  }

  // Initial display update
  DEBUG_PRINTLN("Initializing display...");
  updateDisplay();
  lastDisplayedMinute = rtcManager.getCurrentMinute();

  DEBUG_PRINTLN("Watch ready!");
  DEBUG_PRINT("Smart polling: Sleep until :");
  DEBUG_PRINT(WAKE_BEFORE_MINUTE_SEC);
  DEBUG_PRINT("s, then poll every ");
  DEBUG_PRINT(POLL_INTERVAL_MS);
  DEBUG_PRINTLN("ms");
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
    DEBUG_PRINT("Minute ");
    DEBUG_PRINT(lastDisplayedMinute);
    DEBUG_PRINT(" → ");
    DEBUG_PRINTLN(currentMinute);

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
      DEBUG_PRINT("Sleeping for ");
      DEBUG_PRINT(sleepSeconds);
      DEBUG_PRINTLN(" seconds...");
      DEBUG_FLUSH();
      delay(sleepSeconds * 1000);
    }

    // Now we're at approximately WAKE_BEFORE_MINUTE_SEC
    // Poll every POLL_INTERVAL_MS until minute changes
    DEBUG_PRINT("Active polling (");
    DEBUG_PRINT(POLL_INTERVAL_MS);
    DEBUG_PRINTLN("ms) - waiting for minute change");
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

  // Cycle to random watchface if enabled and it's full refresh time
  if (ENABLE_WATCHFACE_CYCLING && isFullRefreshTime && !firstUpdate) {
    // Independent uniform draw each time, excluding only the face on screen now
    currentWatchFaceIndex = pickNextWatchFace(currentWatchFaceIndex);
    currentWatchFace = allWatchFaces[currentWatchFaceIndex];
    DEBUG_PRINT("Random watchface #");
    DEBUG_PRINT(currentWatchFaceIndex);
    DEBUG_PRINT(" (");
    DEBUG_PRINT(NUM_WATCHFACES);
    DEBUG_PRINTLN(" total)");
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
  DEBUG_PRINT(timeStr);
  DEBUG_PRINT(" (");
  DEBUG_PRINT(usePartialRefresh ? "partial" : "full");
  DEBUG_PRINT(", ");
  DEBUG_PRINT(elapsed);
  DEBUG_PRINTLN("ms)");

  // Put display in low-power mode
  display.hibernate();
}
