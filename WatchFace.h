#ifndef WATCHFACE_H
#define WATCHFACE_H

struct WatchFace {
  const unsigned char* bitmap;

  int bitmap_x_start = 0;
  int bitmap_y_start = 0;
  int bitmap_x_end = 200;
  int bitmap_y_end = 200;
  uint16_t bitmap_color = GxEPD_BLACK;

  int layout = 0; // 0 - text1 and text 2 are in single line ; 1 - text1 and text 2 are in multiple lines
  bool noAMPM = false;

  int text1x = -1; // -1 to center text 1 along x axis; else start text at a percentage of total x axis screen length
  int text1y = -1; // -1 to center text 1 along y axis; else start text at a percentage of total y axis screen length
  uint16_t text1color = GxEPD_BLACK;
  const GFXfont* text1font;

  int text2x = -1; // -1 to center text 2 along x axis; else start text at a percentage of total x axis screen length
  int text2y = -1; // -1 to center text 2 along y axis; else start text at a percentage of total y axis screen length
  uint16_t text2color = GxEPD_BLACK;
  const GFXfont* text2font;
};

#endif // WATCHFACE_H
