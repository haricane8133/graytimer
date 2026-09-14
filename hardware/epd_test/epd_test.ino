// Display diagnostic for the 1.54" SSD1681 panel (GDEH0154D67 / GDEY0154D67 /
// Waveshare 1.54" V2) on the Xiao nRF52840. Standalone sketch - open this folder
// in the Arduino IDE, NOT the main graytimer sketch.
//
// Requires BUSY wired to D9 (any free GPIO works - change EPD_BUSY). With the
// library diagnostics on, a healthy panel prints "_Update_Full : ~2000000" (µs)
// and visibly flashes white -> black -> checkerboard, then alternates black/white
// forever so the breakout's boost rails can be probed with a meter.
// "Busy Timeout!" = controller not answering.  Sane times but no image change =
// the high-voltage boost is dead (see docs/HARDWARE.md, Repair log).
// Serial monitor at 115200.
#include <GxEPD2_BW.h>

#define EPD_CS   D1
#define EPD_DC   D3
#define EPD_RST  D0
#define EPD_BUSY D9

GxEPD2_BW<GxEPD2_154_D67, GxEPD2_154_D67::HEIGHT> display(
  GxEPD2_154_D67(EPD_CS, EPD_DC, EPD_RST, EPD_BUSY));

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("\n=== EPD diagnostic ===");

  pinMode(EPD_BUSY, INPUT);
  Serial.print("BUSY idle level (expect 0 = LOW): ");
  Serial.println(digitalRead(EPD_BUSY));

  // init(serial_diag_bitrate, initial, reset_duration_ms, pulldown_rst_mode)
  // With diag enabled the library prints "_PowerOn : N" / "_Update_Full : N"
  // (N = ms spent waiting on BUSY) or "Busy Timeout!" if BUSY never rises/falls.
  display.init(115200, true, 2, false);

  Serial.println("Full refresh: all WHITE");
  display.setFullWindow();
  display.firstPage();
  do { display.fillScreen(GxEPD_WHITE); } while (display.nextPage());
  delay(1000);

  Serial.println("Full refresh: all BLACK");
  display.firstPage();
  do { display.fillScreen(GxEPD_BLACK); } while (display.nextPage());
  delay(1000);

  Serial.println("Full refresh: checkerboard + box");
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    for (int y = 0; y < 200; y += 20)
      for (int x = 0; x < 200; x += 20)
        if (((x + y) / 20) & 1) display.fillRect(x, y, 20, 20, GxEPD_BLACK);
    display.fillRect(60, 60, 80, 80, GxEPD_WHITE);
    display.drawRect(60, 60, 80, 80, GxEPD_BLACK);
  } while (display.nextPage());

  Serial.println("Now refreshing black/white forever so the HV rails can be probed.");
}

void loop() {
  static bool black = false;
  black = !black;
  display.firstPage();
  do { display.fillScreen(black ? GxEPD_BLACK : GxEPD_WHITE); } while (display.nextPage());
  delay(500);
}
