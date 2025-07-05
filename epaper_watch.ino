#include "myutils.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  display.init(115200, true, 2, false); // force full update
  display.setRotation(0);               // try 0 if 1 is not visible

  // new WatchFace_atat()
  // new WatchFace_atdp()
  // new WatchFace_stormtrooper3floyd()
  // new WatchFace_stormtrooper3()
  // new WatchFace_b1()
  // new WatchFace_giraffe1()
  // new WatchFace_mountain2()
  drawWatchFace(new WatchFace_mountain2(), "6:24 AM", "Jun 24");

  // Sleep to preserve battery
  display.hibernate();
}

void loop() {
  // nothing to do
}
