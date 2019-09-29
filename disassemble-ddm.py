#!/usr/bin/env python3

import sys

from common import *

with open(sys.argv[1], "rb") as f:

  # Read some header?
  unk1 = read32(f)
  assert(unk1 == 0x00000001)
  file_length = read32(f)
  unk3 = read32(f)
  print(".header 0x%08X %d 0x%08X" % (unk1, file_length, unk3))


  groups = []

  for i in range(unk3):
    offset = read32(f)
    size = read32(f)
    #print("%d: size %d # %d" % (offset, unk, size, i))
    groups += [(offset, size)]

  #f.seek(groups[0])
  for offset, size in groups:
    print()
    print()
    print()
    print()

    print(f.tell(), offset)
    assert(f.tell() == offset)
    f.seek(offset)

    print(f.tell())

    for i in range(1):
      unk = read32(f)
      print("0x%08X # %d" % (unk, i))

    # Might be wrong?
    checksum = read32(f)
    print("Checksum 0x%08X ???" % checksum)

    for i in range(5):
      unk = read32(f)
      print("0x%08X # %d" % (unk, i))

    some_name = read_string(f, 64)
    print("material-name '%s'" % some_name)

    for i in range(7):
      unk = read32(f) # Mostly valid floats?
      print("0x%08X # %d" % (unk, i))

    unk0_count = read32(f)

    unk1_count = read32(f)
    unk2_count = read32(f)
    unk3_count = read32(f)
    print(unk1_count, unk2_count, unk3_count)

    assert(unk0_count == unk3_count)

    for i in range(unk0_count):
      print("")

      some_name1 = read_string(f, 64)
      some_name2 = read_string(f, 64)
      print("name-in-dds: '%s'" % some_name1)
      print("dds-name: '%s'" % some_name2)

      index = read32(f)
      unk1 = read32(f)
      print("%d, 0x%08X" % (index, unk1)) # Some color?
      #assert(unk == 0xFFFFFFFF)

      unk2 = read_float(f) # Mostly 0?
      unk3 = read_float(f)
      unk4 = read_float(f)
      print(unk2, unk3, unk4)

      unk = read32(f)
      print("Unknown: %d" % unk)
      unks = [
        0x00000000,
        0x00000001,
        0x00000002,
        0x00000003
      ]
      assert(unk in unks)

    print(f.tell())

    print()

    for i in range(unk1_count):
      unk = []
      unk += [read_float(f)]
      unk += [read_float(f)]
      unk += [read_float(f)]
      # Some of these don't look like floats, but there's 0x3F800000
      unk += [read_float(f)]
      unk += [read_float(f)]
      unk += [read_float(f)]
      unk += ["0x%08X" % read32(f)]
      unk += [read_float(f)]
      unk += [read_float(f)]
      print("%d. %s" % (i, unk))

    print()

    for i in range(unk2_count):
      v = read16(f) # Probably an index into previous table
      print("%d. 0x%04X" % (i, v))
      assert(v < unk1_count)

    print()

    for i in range(unk3_count):

      u1 = read32(f)
      u2 = read16(f)
      print("0x%08X" % u1, "0x%04X" % u2)
      #assert(u1 == 0x00000000)

  
    #if u2 in [0x46, 0xA]:
    #  f.read(6)

    #data = f.read(offset + size - f.tell())
    #print(unk3_count, "error", len(data), data.hex())
    #assert(len(data) == 0)

    print(f.tell())
