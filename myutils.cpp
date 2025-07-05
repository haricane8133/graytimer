#include "myutils.h"

GxEPD2_BW<GxEPD2_154_D67, GxEPD2_154_D67::HEIGHT> display(
  GxEPD2_154_D67(EPD_CS, EPD_DC, EPD_RST, EPD_BUSY)
); // GDEH0154D67 200x200, SSD1681

void drawWatchFace(
  const WatchFace* face,
  const String& text1,
  const String& text2
) {
  const int screenW = 200;
  const int screenH = 200;

  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);

    // Draw bitmap
    display.drawBitmap(
      face->bitmap_x_start,
      face->bitmap_y_start,
      face->bitmap,
      face->bitmap_x_end,
      face->bitmap_y_end,
      face->bitmap_color
    );

    // --- Get Text Bounds ---
    display.setFont(face->text1font);
    int16_t x1, y1;
    uint16_t w1, h1;
    display.getTextBounds(text1, 0, 0, &x1, &y1, &w1, &h1);

    display.setFont(face->text2font);
    int16_t x2, y2;
    uint16_t w2, h2;
    display.getTextBounds(text2, 0, 0, &x2, &y2, &w2, &h2);

    uint16_t totalW = w1 + w2 + 6; // 6px spacing
    uint16_t totalH = max(h1, h2);

    if (face->layout == 0) {
      // --- Single-line layout ---

      int originX = (face->text1x < 0)
        ? (screenW - totalW) / 2
        : (int)(screenW * (face->text1x / 100.0));

      int baselineY = (face->text1y < 0)
        ? (screenH - totalH) / 2
        : (int)(screenH * (face->text1y / 100.0));

      // Text1
      display.setFont(face->text1font);
      display.setTextColor(face->text1color);
      display.setCursor(originX - x1, baselineY - y1);
      display.print(text1);

      // Text2
      display.setFont(face->text2font);
      display.setTextColor(face->text2color);
      display.setCursor(originX + w1 + 6 - x2, baselineY - y2);
      display.print(text2);

    } else {
      // --- Two-line layout ---

      int drawX1 = (face->text1x < 0)
        ? (screenW - w1) / 2 - x1
        : (int)(screenW * (face->text1x / 100.0)) - x1;

      int drawY1 = (face->text1y < 0)
        ? (screenH - h1) / 2 - y1
        : (int)(screenH * (face->text1y / 100.0)) - y1;

      int drawX2 = (face->text2x < 0)
        ? (screenW - w2) / 2 - x2
        : (int)(screenW * (face->text2x / 100.0)) - x2;

      int drawY2 = (face->text2y < 0)
        ? (screenH - h2) / 2 - y2
        : (int)(screenH * (face->text2y / 100.0)) - y2;

      display.setFont(face->text1font);
      display.setTextColor(face->text1color);
      display.setCursor(drawX1, drawY1);
      display.print(text1);

      display.setFont(face->text2font);
      display.setTextColor(face->text2color);
      display.setCursor(drawX2, drawY2);
      display.print(text2);
    }
  } while (display.nextPage());
}

