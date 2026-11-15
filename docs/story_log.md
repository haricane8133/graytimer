---

## The longer story

The photos above cover three weeks. The watch itself took a bit longer.

**2025: the first watch**

- **July 2025.** The first commit: a Xiao nRF52840, a 1.54" e-paper panel, a
  handful of fonts and watchfaces, and a little framework for placing the time
  on a picture.
- **October 2025.** A real-time clock, fast partial refreshes, a light sleep
  between minutes, and the shuffle: a random face every 10 minutes. Two
  batches of faces land as "A fistful of watchfaces" and "For a few
  watchfaces more".
- **November 2025.** The orange 3D-printed case, and the first photos.
- **February 2026.** The last change to the first watch. This is the V1
  release.

**September 2026: new faces, then a dead screen**

- A big watchface refresh: 21 geometric faces drawn in code, clip art, Star
  Wars helmets and the machines of Horizon Zero Dawn. Detailed art looks best
  dithered on e-paper. The favourite is still the Macaw.
- Then a teardown and a resolder, with the battery still connected. After a
  short, the screen showed only noise. A few hours with a multimeter, probing
  the display board's high-voltage circuit, said the panel or its booster was
  gone.
- V1 also lasted only about 3.5 days on a charge. The plan for V2: a new
  clock chip, the RV-8803, that can wake the processor from its deepest sleep.
  NFC was on the wish list too, but it looked out of reach from Arduino.

**October 2026: V2 comes together**

- **24 Oct.** New parts on the table. The firmware is rewritten to sleep in
  System OFF and wake on the clock's minute pulse. The old panel turns out to
  be cracked (a bigger 5.76" panel works on the same wires), and one pad on the
  new Xiao leaks, so the clock's SCL moves to D6. By evening the clock wakes
  the watch every minute.
- **25 Oct.** NFC, take two. Hand-written NFC code saw the phone but never got
  picked. Seeed's NFC library worked. Soon a phone could wake the
  watch from deep sleep and write a plain text to it. The plan: every face gets
  a number, `0` means shuffle, a date sets the clock, and reading the tag shows
  the watch's status. No app needed.
- **26 Oct.** Twenty faces from Hades, and the Horizon faces in the game's own
  font. The repo gets an AGENTS.md, so an AI coding agent knows the project
  from its first message.
- **30 Oct.** The Waveshare module goes in, and the first V2 flash works:
  tapping a phone changes the face. A pinned face now refreshes fully only
  twice an hour. Two new phone commands: `dfu`, so a firmware update no longer
  means opening the case, and `refresh`, to clear ghosting.
- **31 Oct.** The NFC antenna struggles behind the e-paper panel, so where it
  sits in the case matters.

**November 2026: the case, and the last bumps**

- **7 to 14 Nov.** The case is printed.
- **8 to 10 Nov.** V2 runs about 7 days on a 400 mAh battery, twice V1's time
  on twice the battery, so the average current hasn't dropped yet. While
  swapping batteries, a dry solder joint on the ground lead, then a loose power
  wire on the display adapter, made the screen stall. Both were found with a
  multimeter and resoldered.
- **14 Nov.** `dfu` kept slipping out of the bootloader on battery; a short
  USB pause fixed it. One USB cable turned out to carry power but no data.
  The update screen got its Prince of Persia look, from the 1989 game's title
  art and its in-game font, and the same art became face 116. Then every
  upload died halfway, until it was clear the bootloader refuses anything
  over about 790 KB. Storing every generated face cropped to its ink saved
  93 KB, and the upload went through.
- **15 Nov.** Everything into the black case, onto the strap, and out for the
  photos above.

**What's next:** finding where the battery goes, a better spot for the NFC
antenna, and more faces.