#!/usr/bin/env python3

import sys

from common import *

for path in sys.argv[1:]:
  with open(path, "rb") as f:

    # Read some header?
    unk1 = read32(f)
    unk2 = read32(f)
    unk3 = read32(f) # Probably theme
    print(".header 0x%08X 0x%08X 0x%08X" % (unk1, unk2, unk3))

    # Read objects?

    themes = [
      "Power Plant",
      "Industrial",
      "Outdoor",
      "School"
    ]

    park_sizes = [
      (16, 16),
      (24, 24),
      (30, 30),
      (30, 18),
      (60, 6)
    ]

    park_size = park_sizes[unk2]
    for i in range(park_size[0] * park_size[1]): # range(256):

      # These are probably parts on this location (some might overlap?)
      unk1 = read8(f) # Mostly 0xFF, probably part index [see PSH file]
      unk2 = read8(f) # Mostly 0xFF
      unk3 = read8(f) # Mostly 0xFF
      unk4 = read8(f)
      unk5 = read8(f)

      # Padding?
      unk6 = read8(f)

      # Some flags probably
      unk7 = read8(f) # Mostly 0x01

      # Some index probably
      unk8 = read8(f) # Mostly 0x00
      print(".object 0x%02X 0x%02X 0x%02X 0x%02X  | 0x%02X 0x%02X 0x%02X 0x%02X # %d" % (unk1, unk2, unk3, unk4, unk5, unk6, unk7, unk8, i))

      unk4s = [0x16, 0x3C, 0x4E, 0x5A, 0x92, 0xC9, 0xFF]
      unk5s = [0x0E, 0x10, 0x1B, 0x29, 0x2A, 0x2D, 0x34, 0x39, 0x3A, 0x3D, 0x3F, 0x4A, 0x5C, 0x6D, 0x90, 0x91, 0x92, 0xFF]
      unk7s = [0x01, 0x02, 0x03, 0x04, 0x05, 0x09, 0x0D, 0x11, 0x13, 0x15, 0x19, 0x1A, 0x1B, 0x1D, 0x22, 0x52, 0x62, 0x7A, 0x83, 0x84, 0x85, 0x9B, 0x9D, 0xEA]
      unk8s = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0E, 0x10, 0x011, 0x18, 0x19, 0x1E, 0x1F]

      #assert(unk4 in unk4s) - Probably part index
      #assert(unk5 in unk5s) - Probably part index
      assert(unk6 == 0x33)
      assert(unk8 in unk8s)
      # assert(unk7 in unk7s) - too many values.. wtf is this?

    
    # Read all gaps
    for i in range(10):

      # This is sometimes padding, so it's probably additional info
      unk = f.read(8)
      print(unk)

      # This is always valid
      gap_info = f.read(3)
      print(gap_info)

      name = read_string(f, 25)
      print(".gap '%s'" % name)

    # Read all highscores?
    for i in range(8):
      hs = f.read(8)
      print(hs)

    pad = f.read(76)
    print(pad)
    assert(pad == bytes([0x33] * len(pad)))
