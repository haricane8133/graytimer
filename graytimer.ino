#include "myutils.h"
#include <XIAO_nRF52840_NFC.h>

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
// back to false and re-flash for deployment. Or set it from a phone over NFC
// (see the NFC section below).
const bool ENABLE_TIME_SETUP = false;  // Enable serial time input on cold boot
const bool ENABLE_PARTIAL_REFRESH = true;  // Enable partial refresh for faster updates
const uint8_t FULL_REFRESH_INTERVAL = 10;  // Full refresh when minute % N == 0 (e.g., :00, :10, :20, etc.)
const bool ENABLE_WATCHFACE_CYCLING = true;  // Shuffle mode: a random face every 10 mins (phone writes 0)
const bool ENABLE_SERIAL_DEBUG = false;  // Disable Serial to save ~1-2mA power (set false for deployment)

// Serial debug macros (only print if enabled)
#define DEBUG_PRINT(x) if(ENABLE_SERIAL_DEBUG) Serial.print(x)
#define DEBUG_PRINTLN(x) if(ENABLE_SERIAL_DEBUG) Serial.println(x)
#define DEBUG_FLUSH() if(ENABLE_SERIAL_DEBUG) Serial.flush()

// Global RTC manager
RTCManager rtcManager;

bool displayInitialized = false;  // Track if display has been initialized

// Face catalog. A face's number is its position here; it is what a phone
// writes over NFC to pin that face, and docs/CATALOG.md lists them (generated
// by watchfaceutils/generate_gallery.py, which also checks the numbers below).
// Numbers are permanent: add new faces at the end, and retire a face by
// replacing its line with "nullptr,  // N retired", never by deleting it.
WatchFace* allWatchFaces[] = {
  nullptr,  // 0 = shuffle, not a face
  new WatchFace_atat(),  // 1
  new WatchFace_atdp(),  // 2
  new WatchFace_b1(),  // 3
  new WatchFace_ben10(),  // 4
  new WatchFace_bird(),  // 5
  new WatchFace_bird2(),  // 6
  new WatchFace_bugs(),  // 7
  new WatchFace_claw2(),  // 8
  new WatchFace_claw3(),  // 9
  new WatchFace_dog(),  // 10
  new WatchFace_guitar1(),  // 11
  new WatchFace_guitar2(),  // 12
  new WatchFace_h(),  // 13
  new WatchFace_harley(),  // 14
  new WatchFace_harry934(),  // 15
  new WatchFace_herbert(),  // 16
  new WatchFace_hogwarts(),  // 17
  new WatchFace_hogwarts2(),  // 18
  new WatchFace_hogwarts3(),  // 19
  new WatchFace_hogwarts4(),  // 20
  new WatchFace_jitsu1(),  // 21
  new WatchFace_jitsu2(),  // 22
  new WatchFace_jitsu3(),  // 23
  new WatchFace_jitsu4(),  // 24
  new WatchFace_jitsu5(),  // 25
  new WatchFace_krishna(),  // 26
  new WatchFace_macaw(),  // 27
  new WatchFace_mikew(),  // 28
  new WatchFace_mountain1(),  // 29
  new WatchFace_mountain2(),  // 30
  new WatchFace_peacock(),  // 31
  new WatchFace_peacock3(),  // 32
  new WatchFace_pegasus(),  // 33
  new WatchFace_penguin_beatles(),  // 34
  new WatchFace_penguins(),  // 35
  new WatchFace_planets(),  // 36
  new WatchFace_ps(),  // 37
  new WatchFace_saturn(),  // 38
  new WatchFace_sensei(),  // 39
  new WatchFace_sortinghat(),  // 40
  new WatchFace_stormtrooper2(),  // 41
  new WatchFace_stormtrooper3floyd(),  // 42
  new WatchFace_sullivan(),  // 43
  new WatchFace_thiruman(),  // 44
  new WatchFace_tom(),  // 45
  new WatchFace_tree(),  // 46
  new WatchFace_walker(),  // 47
  new WatchFace_xwing(),  // 48
  new WatchFace_zebra(),  // 49
  // generated geometric set
  new WatchFace_tie(),  // 50
  new WatchFace_deathstar(),  // 51
  new WatchFace_hallows(),  // 52
  new WatchFace_prism(),  // 53
  new WatchFace_orbit(),  // 54
  new WatchFace_orion(),  // 55
  new WatchFace_kolam(),  // 56
  new WatchFace_vinyl(),  // 57
  new WatchFace_sunburst(),  // 58
  new WatchFace_minimal(),  // 59
  new WatchFace_moon(),  // 60
  new WatchFace_glasses(),  // 61
  new WatchFace_snitch(),  // 62
  new WatchFace_lightsaber(),  // 63
  new WatchFace_rocket(),  // 64
  new WatchFace_cassette(),  // 65
  new WatchFace_equalizer(),  // 66
  new WatchFace_mandala(),  // 67
  new WatchFace_forest(),  // 68
  new WatchFace_dial(),  // 69
  new WatchFace_waves(),  // 70
  new WatchFace_r2d2(),  // 71
  new WatchFace_falcon(),  // 72
  new WatchFace_hedwig(),  // 73
  new WatchFace_penguin(),  // 74
  new WatchFace_headphones(),  // 75
  new WatchFace_ufo(),  // 76
  new WatchFace_balloon(),  // 77
  new WatchFace_lighthouse(),  // 78
  new WatchFace_diya(),  // 79
  new WatchFace_coffee(),  // 80
  new WatchFace_bicycle(),  // 81
  new WatchFace_whale(),  // 82
  new WatchFace_thunderjaw(),  // 83
  new WatchFace_watcher(),  // 84
  new WatchFace_sawtooth(),  // 85
  new WatchFace_stormbird(),  // 86
  new WatchFace_strider(),  // 87
  new WatchFace_vader(),  // 88
  new WatchFace_mando(),  // 89
  new WatchFace_boodoor(),  // 90
  new WatchFace_astronaut(),  // 91
  new WatchFace_cat(),  // 92
  new WatchFace_camera(),  // 93
  new WatchFace_sailboat(),  // 94
  new WatchFace_hari(),  // 95
};
static_assert(sizeof(allWatchFaces) / sizeof(allWatchFaces[0]) <= 128,
              "face number is saved in 7 bits of RTC RAM");
const uint8_t NUM_WATCHFACES = sizeof(allWatchFaces) / sizeof(allWatchFaces[0]);  // slot 0 included

// Saved in the RV-8803's RAM byte across System OFF: bit 7 = face pinned over
// NFC, bits 0-6 = number of the face on screen (0 = nothing saved, which is
// what the RTC's RAM holds after it loses power).
const uint8_t FACE_PINNED = 0x80;
const uint8_t FACE_NUMBER = 0x7F;

uint8_t currentWatchFaceIndex = 0;  // the face's catalog number
WatchFace* currentWatchFace = nullptr;
bool facePinned = false;  // false = shuffle mode

bool isFace(uint8_t n) {
  return n > 0 && n < NUM_WATCHFACES && allWatchFaces[n];
}

void setWatchFace(uint8_t n) {
  currentWatchFaceIndex = n;
  currentWatchFace = allWatchFaces[n];
}

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
// (0 = none shown), skipping retired slots
uint8_t pickNextWatchFace(uint8_t current) {
  uint8_t n;
  do { n = 1 + hwRandom(NUM_WATCHFACES - 1); } while (!isFace(n) || n == current);
  return n;
}

// ==================== NFC ====================
// With the antenna the watch is an NFC tag that a phone reads and writes with
// any generic NDEF app (e.g. NFC Tools). A phone's field wakes the watch from
// System OFF; it serves the tag until the phone has been gone for NFC_IDLE_MS.
// The phone writes one Text record:
//   0                    -> shuffle mode, starting with a new random face
//   1, 2, ...            -> pin that face (numbers in docs/CATALOG.md)
//   YYYY-MM-DD HH:MM:SS  -> set the clock (24-hour). It is applied when the
//                           phone's field drops, i.e. at the phone's tick.
// Anything else is ignored. Reading the tag shows a status text: the watch, a
// link to the catalog, the face and mode, and the time when the phone woke it.
// Needs Seeed's XIAO_nRF52840_NFC library. NEVER run the core's nfc_to_gpio
// example: it permanently turns the NFC pads into GPIOs.
const uint32_t NFC_IDLE_MS = 3000;  // a phone's field comes and goes while it polls

// Swallows the NFC library's log
class NullPrint : public Print {
  size_t write(uint8_t) override { return 1; }
} nfcLog;

XIAONrf52840Nfc::NfcType2Tag nfcTag;

// Fills the tag's data area with one NDEF Text record holding the status text
void writeStatusRecord(uint8_t *data, uint16_t size) {
  RV8803 &rtc = rtcManager.rtc;
  char text[128];  // at most 119 characters; the data area holds 154
  uint8_t n = snprintf(text, sizeof(text),
                       "graytimer by Hari R\n"
                       "github.com/haricane8133/graytimer/blob/master/docs/CATALOG.md\n"
                       "Face %d, %s\n%04d-%02d-%02d %02d:%02d:%02d",
                       currentWatchFaceIndex, facePinned ? "pinned" : "shuffle",
                       rtc.getYear(), rtc.getMonth(), rtc.getDate(),
                       rtc.getHours(), rtc.getMinutes(), rtc.getSeconds());
  memset(data, 0, size);
  uint8_t *p = data;
  *p++ = 0x03;      // NDEF message TLV
  *p++ = 7 + n;     // its length: record header 4, status byte, "en", text
  *p++ = 0xD1;      // MB, ME, SR, well-known type
  *p++ = 1;         // type length
  *p++ = 3 + n;     // payload length
  *p++ = 'T';
  *p++ = 2;         // UTF-8, language code length 2
  *p++ = 'e';
  *p++ = 'n';
  memcpy(p, text, n);
  p[n] = 0xFE;      // terminator TLV
}

void startNfcTag() {
  // The library requires a URI (58 characters at most), but writeStatusRecord
  // replaces it, so phones never see this one
  XIAONrf52840Nfc::NfcType2TagConfig config("github.com/haricane8133/graytimer", true, false, nfcLog);
  config.dataInitializer = writeStatusRecord;
  if (nfcTag.begin(config) != XIAONrf52840Nfc::NfcType2TagBeginResult::Started) {
    DEBUG_PRINTLN("ERROR: NFC tag failed to start");  // the watch carries on without it
  }
}

// Copies the text of the phone's message into text (at most size - 1
// characters) if its first record is a Text record; otherwise text is ""
void readPhoneText(char *text, uint8_t size) {
  const uint8_t *a = nfcTag.dataArea();
  uint16_t areaSize = nfcTag.dataAreaSize();
  uint16_t i = 0;
  text[0] = '\0';
  while (i < areaSize && a[i] == 0x00) i++;  // NULL TLVs
  if (i + 7 > areaSize || a[i] != 0x03) return;

  // Short well-known record: header, type length 1, payload length, 'T',
  // then the payload: status byte (language code length), language, text
  uint8_t recLen = a[i + 1];
  const uint8_t *r = a + i + 2;
  if (i + 2 + recLen > areaSize || recLen < 5 ||
      (r[0] & 0x3F) != 0x11 || r[1] != 1 || r[3] != 'T') return;
  uint8_t payLen = r[2], lang = r[4] & 0x3F;
  if (4 + payLen > recLen || 1 + lang > payLen) return;
  uint8_t n = payLen - 1 - lang;
  if (n >= size) return;
  memcpy(text, r + 5 + lang, n);
  text[n] = '\0';
}

// Value of n decimal digits at p, or -1 if any is not a digit
int digits(const char *p, uint8_t n) {
  int v = 0;
  while (n--) {
    if (*p < '0' || *p > '9') return -1;
    v = v * 10 + (*p++ - '0');
  }
  return v;
}

bool validDate(int y, int m, int d) {
  static const uint8_t days[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  if (y < 2000 || y > 2099 || m < 1 || m > 12 || d < 1) return false;  // RV-8803 years 00-99
  return d <= days[m - 1] + (m == 2 && y % 4 == 0);
}

// Acts on what the phone wrote. Returns true if the display must be redrawn.
bool applyPhoneCommand() {
  char s[24];
  readPhoneText(s, sizeof(s));
  uint8_t len = strlen(s);
  DEBUG_PRINT("NFC: ");
  DEBUG_PRINTLN(s);

  int n = (len >= 1 && len <= 3) ? digits(s, len) : -1;
  if (n == 0) {
    facePinned = false;
    setWatchFace(pickNextWatchFace(currentWatchFaceIndex));
    return true;
  }
  if (n > 0) {
    if (!isFace(n)) return false;
    facePinned = true;
    setWatchFace(n);
    return true;
  }

  // YYYY-MM-DD HH:MM:SS
  if (len != 19 || s[4] != '-' || s[7] != '-' || s[10] != ' ' || s[13] != ':' || s[16] != ':') return false;
  int year = digits(s, 4), month = digits(s + 5, 2), day = digits(s + 8, 2);
  int hour = digits(s + 11, 2), minute = digits(s + 14, 2), second = digits(s + 17, 2);
  if (!validDate(year, month, day) || hour < 0 || hour > 23 ||
      minute < 0 || minute > 59 || second < 0 || second > 59) return false;
  return rtcManager.setTime(year, month, day, hour, minute, second);
}

/**
 * Setup - runs on every boot. The watch spends almost all its time in System OFF
 * (~0.4µA nRF52840 + ~0.24µA RV-8803). Two things wake it, both as a reset into
 * setup(): the RV-8803 pulling INT (D2) low at every minute rollover, and a
 * phone's NFC field. Each pass here does that wake's work and goes back to
 * System OFF.
 *
 * Cold boot (power-on, reset button, fresh upload): optional serial time setup,
 * shuffle mode with a random face, full refresh.
 * RTC wake: same face as last minute (saved in RTC RAM), partial refresh; in
 * shuffle mode a new face + full refresh at :00, :10, ...
 * NFC wake: serve the tag; redraw only for a phone command or a minute that
 * rolls over meanwhile.
 */
void setup() {
  uint32_t resetReason = readResetReason();
  bool nfcWake = resetReason & POWER_RESETREAS_NFC_Msk;
  bool wokeFromSleep = nfcWake || (resetReason & POWER_RESETREAS_OFF_Msk);

  if (ENABLE_SERIAL_DEBUG) {
    Serial.begin(115200);
    if (!wokeFromSleep) while (!Serial) delay(10);  // USB won't enumerate in time on a wake
  }

  DEBUG_PRINTLN(nfcWake ? "\n=== E-Paper Watch (NFC wake) ==="
                : wokeFromSleep ? "\n=== E-Paper Watch (wake) ===" : "\n=== E-Paper Watch ===");

  // Initialize RTC
  if (!rtcManager.begin()) {
    DEBUG_PRINTLN("ERROR: RTC not found!");
    while (1) delay(1000);
  }

  uint8_t saved = rtcManager.loadFaceState();
  bool coldStart = !wokeFromSleep || !isFace(saved & FACE_NUMBER);

  if (coldStart) {
    if (rtcManager.lostPower()) {
      DEBUG_PRINTLN("WARNING: RTC lost power, time may be incorrect!");
    }

    // Optional: Set time via Serial
    if (ENABLE_TIME_SETUP) {
      rtcManager.setupTimeViaSerial();
    }

    // Shuffle mode with a random face (hardware RNG, no seeding needed)
    facePinned = false;
    setWatchFace(pickNextWatchFace(0));
    DEBUG_PRINT("Initial random watchface #");
  } else {
    facePinned = saved & FACE_PINNED;
    setWatchFace(saved & FACE_NUMBER);
    DEBUG_PRINT(facePinned ? "Pinned watchface #" : "Resuming watchface #");
  }
  DEBUG_PRINTLN(currentWatchFaceIndex);

  // Before any display work, so the phone that woke us finds the tag quickly.
  // Its status text is a snapshot of this moment.
  if (nfcWake) startNfcTag();

  // Cold boot draws at once and an RTC wake draws for its minute flag. An NFC
  // wake draws only for a phone command or a minute that rolls over meanwhile.
  bool redraw = coldStart;
  bool forceFull = coldStart;
  uint8_t minutes = 0;  // cap in case a bad I2C read keeps reporting the flag
  uint32_t phoneSeenMs = millis();
  for (;;) {
    bool newMinute = minutes < 3 && rtcManager.minuteInterruptPending();
    if (newMinute || redraw) {
      if (newMinute) minutes++;
      // Clear the flag first, then read the time: a minute that rolls over
      // while the display refreshes sets the flag again, and we redraw for it.
      rtcManager.clearMinuteInterrupt();
      rtcManager.refresh();
      updateDisplay(newMinute, forceFull, coldStart);
      redraw = forceFull = false;
      continue;
    }
    if (!nfcWake) break;

    // The library answers the phone from its interrupt, so a phone's write
    // completes even while the display is refreshing.
    nfcTag.update();
    if (nfcTag.fieldPresent()) phoneSeenMs = millis();
    if (nfcTag.takeWriteSessionEnded()) {  // the phone wrote and its field dropped
      redraw = forceFull = applyPhoneCommand();
      phoneSeenMs = millis();
    } else if (millis() - phoneSeenMs > NFC_IDLE_MS) {
      break;
    }
    delay(5);
  }

  rtcManager.saveFaceState((facePinned ? FACE_PINNED : 0) | currentWatchFaceIndex);
  goToSleep();
}

/**
 * Never reached: setup() always ends in System OFF, and the next wake
 * starts over at setup().
 */
void loop() {
}

/**
 * Enter System OFF until the RV-8803 pulls INT low at the next minute or a
 * phone's NFC field appears. RAM and the CPU are powered down; waking is a
 * reset. Pins keep their configured levels, so the display's CS/RST stay
 * driven high while it hibernates. If INT is already low here, the chip wakes
 * straight away, so a minute that slips in after the last check is not lost.
 */
void goToSleep() {
  DEBUG_PRINTLN("System OFF until next minute or NFC field");
  DEBUG_FLUSH();
  NRF_NFCT->TASKS_SENSE = 1;  // field detection stays on in System OFF and wakes the chip
  systemOff(RTC_INTERRUPT_PIN, LOW);
}

/**
 * Update e-paper display with the time from the last rtcManager.refresh()
 *
 * newMinute:   this draw is for a minute rollover; in shuffle mode a new face
 *              is picked at :00, :10, ...
 * forceFull:   full refresh regardless of the minute (cold boot, phone command)
 * initialBoot: the panel content is unknown, so GxEPD2 must not assume the
 *              previous frame is still in controller RAM. On a wake the panel
 *              kept it through hibernate, so partial refresh works.
 */
void updateDisplay(bool newMinute, bool forceFull, bool initialBoot) {
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

  // In shuffle mode, a random watchface when a new minute is full refresh time
  if (ENABLE_WATCHFACE_CYCLING && !facePinned && newMinute && isFullRefreshTime && !forceFull) {
    // Independent uniform draw each time, excluding only the face on screen now
    setWatchFace(pickNextWatchFace(currentWatchFaceIndex));
    timeStr = rtcManager.getFormattedTime(!currentWatchFace->noAMPM);
    DEBUG_PRINT("Random watchface #");
    DEBUG_PRINTLN(currentWatchFaceIndex);
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
