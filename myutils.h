#pragma once
#include <SPI.h>
#include <Wire.h>
#include <GxEPD2_BW.h>
#include <Adafruit_GFX.h>
#include <RTClib.h>
#include "bitmaps/Bitmaps200x200.h"

// E-Paper Display Pin Definitions (GoodDisplay 1.54" - GDEH0154D67)
#define EPD_MOSI  D10  // SPI MOSI (DAT) - Hardware SPI
#define EPD_SCK   D8   // SPI Clock (CLK) - Hardware SPI
#define EPD_CS    D1   // Chip Select (CS) - GPIO
#define EPD_DC    D3   // Data/Command (DC) - GPIO
#define EPD_RST   D0   // Reset (RES) - GPIO
#define EPD_BUSY  D6   // Busy Signal (BUSY) - GPIO (was D5 in breakout board, moved to free I2C)

// RTC (DS3231) Pin Definitions
// Using default hardware I2C pins (no Wire.begin(SDA,SCL) needed)
#define RTC_SDA           D4   // I2C SDA (Hardware I2C)
#define RTC_SCL           D5   // I2C SCL (Hardware I2C)
#define RTC_INTERRUPT_PIN D2   // SQW/INT alarm interrupt - GPIO

// Future: Button for time sync / menu navigation
#define BUTTON_PIN        D7   // User input (with internal pull-up) - GPIO

#include "WatchFace.h"
#include "RTCManager.h"

// include all fonts used, here
#include <Fonts/FreeMonoBold9pt7b.h>
#include "myfonts/CourierPrime_Bold10pt7b.h"
#include "myfonts/CourierPrime_Bold20pt7b.h"
#include "myfonts/StarJedi_DGRW10pt7b.h"
#include "myfonts/StarJedi_DGRW20pt7b.h"
#include "myfonts/DynaPuff_VariableFont_wdth_wght10pt7b.h"
#include "myfonts/DynaPuff_VariableFont_wdth_wght20pt7b.h"
#include "myfonts/Helloworld_ovvY040pt7b.h"
#include "myfonts/Helloworld_ovvY030pt7b.h"
#include "myfonts/Helloworld_ovvY020pt7b.h"
#include "myfonts/Helloworld_ovvY010pt7b.h"
#include "myfonts/BekingBold_1Gqdg20pt7b.h"
#include "myfonts/BekingBold_1Gqdg10pt7b.h"
#include "myfonts/OctoberTwilight_Ooe610pt7b.h"
#include "myfonts/OctoberTwilight_Ooe615pt7b.h"
#include "myfonts/ToughCookiesBold_owZ1d10pt7b.h"
#include "myfonts/ToughCookiesBold_owZ1d20pt7b.h"
#include "myfonts/Caveat_VariableFont_wght10pt7b.h"
#include "myfonts/Caveat_VariableFont_wght20pt7b.h"
#include "myfonts/Beyblade_Metal_Fight_Font20pt7b.h"
#include "myfonts/Beyblade_Metal_Fight_Font10pt7b.h"
#include "myfonts/Neuton_Bold20pt7b.h"
#include "myfonts/Neuton_Bold10pt7b.h"
#include "myfonts/BADABB__20pt7b.h"
#include "myfonts/BADABB__10pt7b.h"
#include "myfonts/CompactaBT20pt7b.h"
#include "myfonts/CompactaBT10pt7b.h"
#include "myfonts/HARRYP__20pt7b.h"
#include "myfonts/HARRYP__10pt7b.h"
#include "myfonts/Bumbastika_edited10pt7b.h"
#include "myfonts/Bumbastika_edited7pt7b.h"
#include "myfonts/Monster_AG20pt7b.h"
#include "myfonts/Monster_AG10pt7b.h"
#include "myfonts/Bootle_4B9l10pt7b.h"
#include "myfonts/Bootle_4B9l20pt7b.h"
#include "myfonts/Bootle_4B9l30pt7b.h"
#include "myfonts/PsBold_2Oy2w20pt7b.h"
#include "myfonts/PsBold_2Oy2w10pt7b.h"

// include all watchfaces used, here
#include "mywatchfaces/atat.h"
#include "mywatchfaces/atdp.h"
#include "mywatchfaces/b1.h"
#include "mywatchfaces/ben10.h"
#include "mywatchfaces/bird.h"
#include "mywatchfaces/bird2.h"
#include "mywatchfaces/bugs.h"
#include "mywatchfaces/claw.h"
#include "mywatchfaces/claw2.h"
#include "mywatchfaces/claw3.h"
#include "mywatchfaces/crow.h"
#include "mywatchfaces/dog.h"
#include "mywatchfaces/giraffe1.h"
#include "mywatchfaces/guitar1.h"
#include "mywatchfaces/guitar2.h"
#include "mywatchfaces/h.h"
#include "mywatchfaces/harley.h"
#include "mywatchfaces/harry934.h"
#include "mywatchfaces/herbert.h"
#include "mywatchfaces/hogwarts.h"
#include "mywatchfaces/hogwarts2.h"
#include "mywatchfaces/hogwarts3.h"
#include "mywatchfaces/hogwarts4.h"
#include "mywatchfaces/jitsu1.h"
#include "mywatchfaces/jitsu2.h"
#include "mywatchfaces/jitsu3.h"
#include "mywatchfaces/jitsu4.h"
#include "mywatchfaces/jitsu5.h"
#include "mywatchfaces/krishna.h"
#include "mywatchfaces/macaw.h"
#include "mywatchfaces/mikew.h"
#include "mywatchfaces/mountain1.h"
#include "mywatchfaces/mountain2.h"
#include "mywatchfaces/peacock.h"
#include "mywatchfaces/peacock3.h"
#include "mywatchfaces/pegasus.h"
#include "mywatchfaces/penguin_beatles.h"
#include "mywatchfaces/penguins.h"
#include "mywatchfaces/planets.h"
#include "mywatchfaces/ps.h"
#include "mywatchfaces/saturn.h"
#include "mywatchfaces/sensei.h"
#include "mywatchfaces/sortinghat.h"
#include "mywatchfaces/squares.h"
#include "mywatchfaces/squares_invert.h"
#include "mywatchfaces/stormtrooper2.h"
#include "mywatchfaces/stormtrooper3_floyd.h"
#include "mywatchfaces/sullivan.h"
#include "mywatchfaces/thiruman.h"
#include "mywatchfaces/tom.h"
#include "mywatchfaces/tree.h"
#include "mywatchfaces/walker.h"
#include "mywatchfaces/xwing.h"
#include "mywatchfaces/zebra.h"


extern GxEPD2_BW<GxEPD2_154_D67, GxEPD2_154_D67::HEIGHT> display;

void drawWatchFace(
  const WatchFace* face,
  String text1,  // time
  String text2,  // date
  bool partialRefresh
);