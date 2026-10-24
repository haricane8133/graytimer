#include "myutils.h"

// systemOff() and readResetReason() come from the Adafruit-based Seeed nRF52 core.
#if !defined(ARDUINO_ARCH_NRF52)
#error "Select Tools > Board > Seeed nRF52 Boards > Seeed XIAO nRF52840 (not the mbed 'XIAO nRF52840 (No Updates)' board)"
#endif

// ==================== CONFIGURATION ====================
// Serial time setup: on a cold boot (power-on, reset button, fresh upload; not
// the per-minute RTC wake) the watch waits 15 s for a line on the Serial
// Monitor (115200 baud) in the format  YYYY,MM,DD,HH,MM,SS  (24-hour clock),
// e.g.  2026,9,14,17,30,0  -> 14 Sep 2026, 5:30:00 PM.  Send with a newline.
// No input within 15 s -> keeps the current RTC time.  Serial.begin() only runs
// when ENABLE_SERIAL_DEBUG is true, so enable both, set the time, then set both
// back to false and re-flash for deployment.
const bool ENABLE_TIME_SETUP = false;  // Enable serial time input on cold boot
const bool ENABLE_PARTIAL_REFRESH = true;  // Enable partial refresh for faster updates
const uint8_t FULL_REFRESH_INTERVAL = 10;  // Full refresh when minute % N == 0 (e.g., :00, :10, :20, etc.)
const bool ENABLE_WATCHFACE_CYCLING = true;  // Auto-cycle through watchfaces every 10 mins
const bool ENABLE_SERIAL_DEBUG = false;  // Disable Serial to save ~1-2mA power (set false for deployment)

// Serial debug macros (only print if enabled)
#define DEBUG_PRINT(x) if(ENABLE_SERIAL_DEBUG) Serial.print(x)
#define DEBUG_PRINTLN(x) if(ENABLE_SERIAL_DEBUG) Serial.println(x)
#define DEBUG_FLUSH() if(ENABLE_SERIAL_DEBUG) Serial.flush()

// Global RTC manager
RTCManager rtcManager;

bool displayInitialized = false;  // Track if display has been initialized

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
static_assert(sizeof(allWatchFaces) / sizeof(allWatchFaces[0]) <= 128,
              "face index is saved in 7 bits of RTC RAM");
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
 * Setup - runs on every boot. The watch spends almost all its time in System OFF
 * (~0.4µA nRF52840 + ~0.24µA RV-8803); the RV-8803 pulls INT (D2) low at every
 * minute rollover, which resets the chip into setup() again. So each pass here
 * is one minute's work: read time, refresh display, go back to System OFF.
 *
 * Cold boot (power-on, reset button, upload): optional serial time setup,
 * random watchface, full refresh. Wake from System OFF: same watchface as last
 * minute (saved in RTC RAM), partial refresh, new face + full refresh at :00, :10, ...
 */
void setup() {
  bool wokeFromSleep = readResetReason() & POWER_RESETREAS_OFF_Msk;

  if (ENABLE_SERIAL_DEBUG) {
    Serial.begin(115200);
    if (!wokeFromSleep) while (!Serial) delay(10);  // USB won't enumerate in time on a wake
  }

  DEBUG_PRINTLN(wokeFromSleep ? "\n=== E-Paper Watch (wake) ===" : "\n=== E-Paper Watch ===");

  // Initialize RTC
  if (!rtcManager.begin()) {
    DEBUG_PRINTLN("ERROR: RTC not found!");
    while (1) delay(1000);
  }

  int savedFace = rtcManager.loadFaceIndex();
  bool coldStart = !wokeFromSleep || savedFace < 0 || savedFace >= NUM_WATCHFACES;

  if (coldStart) {
    if (rtcManager.lostPower()) {
      DEBUG_PRINTLN("WARNING: RTC lost power, time may be incorrect!");
    }

    // Optional: Set time via Serial
    if (ENABLE_TIME_SETUP) {
      rtcManager.setupTimeViaSerial();
    }

    // Pick a random initial watchface (hardware RNG, no seeding needed)
    currentWatchFaceIndex = hwRandom(NUM_WATCHFACES);
    DEBUG_PRINT("Initial random watchface #");
  } else {
    currentWatchFaceIndex = savedFace;
    DEBUG_PRINT("Resuming watchface #");
  }
  currentWatchFace = allWatchFaces[currentWatchFaceIndex];
  DEBUG_PRINTLN(currentWatchFaceIndex);

  // Clear the flag first, then read the time: a minute that rolls over while
  // the display refreshes sets the flag again, and we redraw for it.
  bool forceFull = coldStart;
  uint8_t passes = 0;  // cap in case a bad I2C read keeps reporting the flag
  do {
    rtcManager.clearMinuteInterrupt();
    rtcManager.refresh();
    updateDisplay(forceFull, coldStart);
    forceFull = false;
  } while (rtcManager.minuteInterruptPending() && ++passes < 3);

  rtcManager.saveFaceIndex(currentWatchFaceIndex);
  goToSleep();
}

/**
 * Never reached: setup() always ends in System OFF, and the next RTC tick
 * starts over at setup().
 */
void loop() {
}

/**
 * Enter System OFF until the RV-8803 pulls INT low at the next minute.
 * RAM and the CPU are powered down; waking is a reset. Pins keep their
 * configured levels, so the display's CS/RST stay driven high while it
 * hibernates. If INT is already low here, the chip wakes straight away,
 * so a minute that slips in after the last check is not lost.
 */
void goToSleep() {
  DEBUG_PRINTLN("System OFF until next minute");
  DEBUG_FLUSH();
  systemOff(RTC_INTERRUPT_PIN, LOW);
}

/**
 * Update e-paper display with the time from the last rtcManager.refresh()
 *
 * forceFull:   full refresh regardless of the minute (cold boot)
 * initialBoot: the panel content is unknown, so GxEPD2 must not assume the
 *              previous frame is still in controller RAM. On a wake the panel
 *              kept it through hibernate, so partial refresh works.
 */
void updateDisplay(bool forceFull, bool initialBoot) {
  // Initialize display ONLY ONCE per boot
  if (!displayInitialized) {
    display.init(ENABLE_SERIAL_DEBUG ? 115200 : 0, initialBoot, 2, false);
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
  if (ENABLE_WATCHFACE_CYCLING && isFullRefreshTime && !forceFull) {
    // Independent uniform draw each time, excluding only the face on screen now
    currentWatchFaceIndex = pickNextWatchFace(currentWatchFaceIndex);
    currentWatchFace = allWatchFaces[currentWatchFaceIndex];
    timeStr = rtcManager.getFormattedTime(!currentWatchFace->noAMPM);
    DEBUG_PRINT("Random watchface #");
    DEBUG_PRINT(currentWatchFaceIndex);
    DEBUG_PRINT(" (");
    DEBUG_PRINT(NUM_WATCHFACES);
    DEBUG_PRINTLN(" total)");
  }

  // Determine refresh mode
  // FULL refresh: cold boot OR every 10 minutes (for ghosting prevention)
  // PARTIAL refresh: All other times (faster, no flicker)
  bool usePartialRefresh = ENABLE_PARTIAL_REFRESH &&
                          !forceFull &&
                          !isFullRefreshTime;

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
