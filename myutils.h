#pragma once
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <Adafruit_GFX.h>
#include "bitmaps/Bitmaps200x200.h"

// Pin definitions for Xiao ESP32-S3
#define EPD_CS    D1
#define EPD_DC    D3
#define EPD_RST   D0
#define EPD_BUSY  D5
#define EPD_SCK   D8
#define EPD_MOSI  D10

#include "WatchFace.h"

// include all fonts used, here
#include <Fonts/FreeMonoBold9pt7b.h>
#include "myfonts/CourierPrime_Bold10pt7b.h"
#include "myfonts/StarJedi_DGRW10pt7b.h"
#include "myfonts/StarJedi_DGRW20pt7b.h"
#include "myfonts/DynaPuff_VariableFont_wdth_wght10pt7b.h"
#include "myfonts/Helloworld_ovvY020pt7b.h"
#include "myfonts/BekingBold_1Gqdg20pt7b.h"
#include "myfonts/BekingBold_1Gqdg10pt7b.h"


// include all watchfaces used, here
#include "mywatchfaces/atat.h"
#include "mywatchfaces/atdp.h"
#include "mywatchfaces/b1.h"
#include "mywatchfaces/giraffe1.h"
#include "mywatchfaces/mountain2.h"
#include "mywatchfaces/stormtrooper3_floyd.h"
#include "mywatchfaces/stormtrooper3.h"


extern GxEPD2_BW<GxEPD2_154_D67, GxEPD2_154_D67::HEIGHT> display;

void drawWatchFace(
  const WatchFace* face,
  const String& text1,  // time
  const String& text2   // date
);