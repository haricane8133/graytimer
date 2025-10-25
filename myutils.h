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

// include all watchfaces used, here
#include "mywatchfaces/atat.h"
#include "mywatchfaces/atdp.h"
#include "mywatchfaces/b1.h"
#include "mywatchfaces/bird.h"
#include "mywatchfaces/bird2.h"
#include "mywatchfaces/bugs.h"
#include "mywatchfaces/crow.h"
#include "mywatchfaces/dog.h"
#include "mywatchfaces/giraffe1.h"
#include "mywatchfaces/h.h"
#include "mywatchfaces/krishna.h"
#include "mywatchfaces/macaw.h"
#include "mywatchfaces/mountain1.h"
#include "mywatchfaces/mountain2.h"
#include "mywatchfaces/peacock.h"
#include "mywatchfaces/peacock3.h"
#include "mywatchfaces/pegasus.h"
#include "mywatchfaces/squares.h"
#include "mywatchfaces/squares_invert.h"
#include "mywatchfaces/stormtrooper2.h"
#include "mywatchfaces/stormtrooper3_floyd.h"
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