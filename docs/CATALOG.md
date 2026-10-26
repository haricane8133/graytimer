# Watchface Catalog

Every watchface has a fixed number. To put a face on the watch, write that
number to it from a phone over NFC; to set the clock, write the date and time.

## Using a phone

Any app that writes NFC tags works; these steps are for **NFC Tools** (iOS and
Android):

1. **Write** → **Add a record** → **Text**, and enter one of:

   | Text | What the watch does |
   |------|---------------------|
   | `0` | Shuffle mode: a random face every 10 minutes, starting with a new one now |
   | `1`, `2`, ... | Shows that face and keeps it (numbers below) |
   | `2026-10-25 14:30:00` | Sets the date and time: `YYYY-MM-DD HH:MM:SS`, 24-hour, all of it |

2. Tap **Write** and hold the phone to the watch's antenna. The phone's field
   wakes the watch; the phone ticks when the write is done, and the watch
   redraws with the change.

The time is set at the moment of the tick, so start the write about a second
before the time you entered. Anything else is ignored and the watch keeps what
it shows.

**Read** in NFC Tools shows the watch's status: a link to this page, the face
number, the mode (pinned or shuffle) and the time when the phone woke it.

A reset or power loss puts the watch back in shuffle mode.

## Faces

<!-- catalog:start -->
<table>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/atat.png" width="150"/><br/>
      <b>1 · AT-AT</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/atdp.png" width="150"/><br/>
      <b>2 · AT-DP</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/b1.png" width="150"/><br/>
      <b>3 · B1 Battle Droid</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/ben10.png" width="150"/><br/>
      <b>4 · Ben 10</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/bird.png" width="150"/><br/>
      <b>5 · Bird</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/bird2.png" width="150"/><br/>
      <b>6 · Bird 2</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/bugs.png" width="150"/><br/>
      <b>7 · Bugs Bunny</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/claw2.png" width="150"/><br/>
      <b>8 · Claw 2</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/claw3.png" width="150"/><br/>
      <b>9 · Claw 3</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/dog.png" width="150"/><br/>
      <b>10 · Dog</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/guitar1.png" width="150"/><br/>
      <b>11 · Guitar 1</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/guitar2.png" width="150"/><br/>
      <b>12 · Guitar 2</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/h.png" width="150"/><br/>
      <b>13 · haricane8133</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/harley.png" width="150"/><br/>
      <b>14 · Harley Davidson</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/harry934.png" width="150"/><br/>
      <b>15 · Harry Potter</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/herbert.png" width="150"/><br/>
      <b>16 · Herbert</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hogwarts.png" width="150"/><br/>
      <b>17 · Hogwarts</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hogwarts2.png" width="150"/><br/>
      <b>18 · Hogwarts 2</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hogwarts3.png" width="150"/><br/>
      <b>19 · Hogwarts 3</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hogwarts4.png" width="150"/><br/>
      <b>20 · Hogwarts 4</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/jitsu1.png" width="150"/><br/>
      <b>21 · Card Jitsu 1</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/jitsu2.png" width="150"/><br/>
      <b>22 · Card Jitsu 2</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/jitsu3.png" width="150"/><br/>
      <b>23 · Card Jitsu 3</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/jitsu4.png" width="150"/><br/>
      <b>24 · Card Jitsu 4</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/jitsu5.png" width="150"/><br/>
      <b>25 · Card Jitsu 5</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/krishna.png" width="150"/><br/>
      <b>26 · Krishna</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/macaw.png" width="150"/><br/>
      <b>27 · Macaw</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/mikew.png" width="150"/><br/>
      <b>28 · Mike Wazowski</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/mountain1.png" width="150"/><br/>
      <b>29 · Mountain 1</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/mountain2.png" width="150"/><br/>
      <b>30 · Mountain 2</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/peacock.png" width="150"/><br/>
      <b>31 · Peacock</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/peacock3.png" width="150"/><br/>
      <b>32 · Peacock 3</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/pegasus.png" width="150"/><br/>
      <b>33 · Pegasus</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/penguin_beatles.png" width="150"/><br/>
      <b>34 · Penguin Beatles</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/penguins.png" width="150"/><br/>
      <b>35 · Penguins of Madagascar</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/planets.png" width="150"/><br/>
      <b>36 · Planets</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/ps.png" width="150"/><br/>
      <b>37 · PlayStation</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/saturn.png" width="150"/><br/>
      <b>38 · Saturn</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/sensei.png" width="150"/><br/>
      <b>39 · Sensei</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/sortinghat.png" width="150"/><br/>
      <b>40 · Sorting Hat</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/stormtrooper2.png" width="150"/><br/>
      <b>41 · Stormtrooper 2</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/stormtrooper3_floyd.png" width="150"/><br/>
      <b>42 · Stormtrooper 3</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/sullivan.png" width="150"/><br/>
      <b>43 · Sulley</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/thiruman.png" width="150"/><br/>
      <b>44 · Thiruman</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/tom.png" width="150"/><br/>
      <b>45 · Tom (Tom & Jerry)</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/tree.png" width="150"/><br/>
      <b>46 · Tree</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/walker.png" width="150"/><br/>
      <b>47 · Walker</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/xwing.png" width="150"/><br/>
      <b>48 · X-Wing</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/zebra.png" width="150"/><br/>
      <b>49 · Zebra</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/tie.png" width="150"/><br/>
      <b>50 · TIE Fighter*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/deathstar.png" width="150"/><br/>
      <b>51 · Death Star*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hallows.png" width="150"/><br/>
      <b>52 · Deathly Hallows*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/prism.png" width="150"/><br/>
      <b>53 · Prism (Dark Side of the Moon)*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/orbit.png" width="150"/><br/>
      <b>54 · Orbits*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/orion.png" width="150"/><br/>
      <b>55 · Orion*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/kolam.png" width="150"/><br/>
      <b>56 · Kolam*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/vinyl.png" width="150"/><br/>
      <b>57 · Vinyl*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/sunburst.png" width="150"/><br/>
      <b>58 · Sunburst*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/minimal.png" width="150"/><br/>
      <b>59 · Minimal*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/moon.png" width="150"/><br/>
      <b>60 · Moon*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/glasses.png" width="150"/><br/>
      <b>61 · Glasses & Scar*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/snitch.png" width="150"/><br/>
      <b>62 · Golden Snitch*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/lightsaber.png" width="150"/><br/>
      <b>63 · Lightsaber*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/rocket.png" width="150"/><br/>
      <b>64 · Rocket*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/cassette.png" width="150"/><br/>
      <b>65 · Cassette*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/equalizer.png" width="150"/><br/>
      <b>66 · Equalizer*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/mandala.png" width="150"/><br/>
      <b>67 · Mandala*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/forest.png" width="150"/><br/>
      <b>68 · Forest*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/dial.png" width="150"/><br/>
      <b>69 · Dial*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/waves.png" width="150"/><br/>
      <b>70 · Waves*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/r2d2.png" width="150"/><br/>
      <b>71 · R2-D2*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/falcon.png" width="150"/><br/>
      <b>72 · Millennium Falcon*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hedwig.png" width="150"/><br/>
      <b>73 · Hedwig*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/penguin.png" width="150"/><br/>
      <b>74 · Penguin*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/headphones.png" width="150"/><br/>
      <b>75 · Headphones*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/ufo.png" width="150"/><br/>
      <b>76 · UFO*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/balloon.png" width="150"/><br/>
      <b>77 · Hot-Air Balloon*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/lighthouse.png" width="150"/><br/>
      <b>78 · Lighthouse*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/diya.png" width="150"/><br/>
      <b>79 · Diya*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/coffee.png" width="150"/><br/>
      <b>80 · Coffee*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/bicycle.png" width="150"/><br/>
      <b>81 · Bicycle*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/whale.png" width="150"/><br/>
      <b>82 · Whale*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/thunderjaw.png" width="150"/><br/>
      <b>83 · Thunderjaw*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/watcher.png" width="150"/><br/>
      <b>84 · Watcher*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/sawtooth.png" width="150"/><br/>
      <b>85 · Sawtooth*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/stormbird.png" width="150"/><br/>
      <b>86 · Stormbird*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/strider.png" width="150"/><br/>
      <b>87 · Strider*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/vader.png" width="150"/><br/>
      <b>88 · Darth Vader*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/mando.png" width="150"/><br/>
      <b>89 · Mandalorian*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/boodoor.png" width="150"/><br/>
      <b>90 · Boo's Door*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/astronaut.png" width="150"/><br/>
      <b>91 · Astronaut*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/cat.png" width="150"/><br/>
      <b>92 · Cat*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/camera.png" width="150"/><br/>
      <b>93 · Camera*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/sailboat.png" width="150"/><br/>
      <b>94 · Sailboat*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hari.png" width="150"/><br/>
      <b>95 · Hari (Tamil)*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/nectar.png" width="150"/><br/>
      <b>96 · Nectar*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/ambrosia.png" width="150"/><br/>
      <b>97 · Ambrosia*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/darkness.png" width="150"/><br/>
      <b>98 · Darkness*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/chthonickey.png" width="150"/><br/>
      <b>99 · Chthonic Key*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/titanblood.png" width="150"/><br/>
      <b>100 · Titan Blood*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/diamond.png" width="150"/><br/>
      <b>101 · Diamond*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/gemstone.png" width="150"/><br/>
      <b>102 · Gemstones*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/obol.png" width="150"/><br/>
      <b>103 · Charon's Obol*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/centaurheart.png" width="150"/><br/>
      <b>104 · Centaur Heart*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/pom.png" width="150"/><br/>
      <b>105 · Pom of Power*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hammer.png" width="150"/><br/>
      <b>106 · Daedalus Hammer*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/spikedcollar.png" width="150"/><br/>
      <b>107 · Old Spiked Collar*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/butterfly.png" width="150"/><br/>
      <b>108 · Pierced Butterfly*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/owlpendant.png" width="150"/><br/>
      <b>109 · Owl Pendant*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/cosmicegg.png" width="150"/><br/>
      <b>110 · Cosmic Egg*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/hourglass.png" width="150"/><br/>
      <b>111 · Bone Hourglass*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/skullearring.png" width="150"/><br/>
      <b>112 · Skull Earring*</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/coinpurse.png" width="150"/><br/>
      <b>113 · Chthonic Coin Purse*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/rose.png" width="150"/><br/>
      <b>114 · Eternal Rose*</b>
    </td>
    <td align="center" width="25%">
      <img src="../watchfaceutils/previews/luckytooth.png" width="150"/><br/>
      <b>115 · Lucky Tooth*</b>
    </td>
  </tr>
</table>
<!-- catalog:end -->
