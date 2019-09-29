#!/usr/bin/env python3

import os
import sys
from xboxpy import nv2a

from common import *


path = sys.argv[1]
mode = int(sys.argv[2])
width = int(sys.argv[3])
height = int(sys.argv[4])
print(mode)


if mode == 201:

  # Working

  compressed = False
  swizzled = True
  mipmap = True

elif mode == 301:

  # Working
  # B0135120-256-256-0x00000301.raw

  compressed = True
  swizzled = True
  mipmap = False
elif mode == 401:

  # Working

  compressed = True
  swizzled = True
  mipmap = True
elif mode == 901:

  # Working

  compressed = False
  swizzled = False
  mipmap = False
else:
  assert(False)


if mipmap:
  level_width = 1
  level_height = 1
  cursor = 6 if mode == 401 else 2 # ???
  #FIXME: Calculate level count?
else:
  level_width = width
  level_height = height
  cursor = 0


with open(path, "rb") as f:

  f.seek(0, os.SEEK_END)
  file_size = f.tell()
  f.seek(0)
  print("file-size", file_size)

  if not compressed:
    data = f.read(file_size)
  else:
    blocks = []
    for _ in range(256):
      block = f.read(8)
      if block in blocks:
        print("Duplicated block..")
      blocks += [block]
      
      # Debug print 4 colors in block
      tmp = []
      for b in range(0, 4):
        tmp += [block[b*2:(b+1)*2].hex()]
      print(tmp)

    assert(len(blocks) == 256)

    # Assemble the data
    data = bytes([])
    for x in range(file_size - f.tell()):
      data += blocks[read8(f)]

  #FIXME: This is stupid
  print(f.tell(), file_size)

  print("data length", len(data))
  open("data.bin", "wb").write(data)


  # Hack for mipmap
  if False:
    skip = 0
    if mode == 201:
      print("Warning: Skipping mipmap levels")
      skip += len(data) - width * height * 2
    elif mode == 401:
      print("Warning: Skipping mipmap levels")
      skip += len(data) - width * height * 2


  # 401 layout for 128x128:

  # (going from highest to lowest address)
  # 0xAB00-80 = 80 bytes garbage? [10 block x 0x00 ?]
  # 0xAB00-80-128*128*2 = 128x128
  # 0xAB00-80-128*128*2-64*64*2 = 64x64
  # 0xAB00-80-128*128*2-64*64*2-32x32*2 = 32x32

  # Untested
  # 0xAB00-80-128*128*2-64*64*2-32x32*2-16x16*2 = 16x16
  # 0xAB00-80-128*128*2-64*64*2-32x32*2-16x16*2-8x8*2 = 8x8
  # 0xAB00-80-128*128*2-64*64*2-32x32*2-16x16*2-8x8*2-4x4*2 = 4x4
  # 0xAB00-80-128*128*2-64*64*2-32x32*2-16x16*2-8x8*2-4x4*2-2x2*2 = 2x2
  # 0xAB00-80-128*128*2-64*64*2-32x32*2-16x16*2-8x8*2-4x4*2-2x2*2-1x1*2 = 1x1

  # Or... from lowest to highest:
  # 1x1 = 6 = only last 2 bytes of first block are chosen
  # 2x2 = 6+(1*1)*2 = 8
  # 4x4 = 6+(1*1+2*2)*2 = 16
  # 8x8 = 6+(1*1+2*2+4*4)*2 = 48
  # 16x16 = 6+(1*1+2*2+4*4+8*8)*2 = 176

  level = 0
  while level_width <= width and level_height <= height:



    pitch = level_width * 2
    image_length = pitch * level_height

    print("level", level, level_width, level_height, "at", cursor, "length", image_length)

    image = data[cursor:cursor+image_length]
    assert(len(image) == image_length)

    #else:
    #  image = bytes([])
    #  for _ in range():
    #    image += blocks[read8(f)]






    if swizzled:
      image = nv2a.Unswizzle(image, 16, (level_width, level_height), pitch)
    open("image-%d.bin" % level, "wb").write(image)


    import PIL.Image
    im = PIL.Image.new("RGB", (level_width, level_height))

    pixels = im.load()

    for y in range(0, level_height):
      for x in range(0, level_width):
        index = (level_width*y+x)*2
        color, = struct.unpack('<H', image[index:index+2])                      
        red = int( ((color & 0xF800) >> 11) / 31.0 * 255.0)
        green = int( ((color & 0x07E0) >> 5) / 63.0 * 255.0)
        blue = int( ((color & 0x001F))  / 31.0 * 255.0)
                                     
        #print red,green,blueh
        pixels[x,y] = (red,green,blue)
    im.save("image-%d.png" % level)

    #FIXME: Decode image and store on disk

    level_width <<= 1
    level_height <<= 1
    level += 1
    cursor += image_length

    #FIXME: Align cursor to DWORD?
    #cursor = (cursor + 3) & ~3

  print(cursor, len(data))
