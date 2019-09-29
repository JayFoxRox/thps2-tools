#!/usr/bin/env python3

import sys
import os

from common import *

with open(sys.argv[1], "rb") as f:

  out_path = os.path.join("out")

  try:
    os.mkdir(out_path)
  except FileExistsError:
    pass

  unk1 = read32(f)
  unk2 = read32(f)
  data_base = read32(f)
  count = read32(f)

  print("0x%08X" % unk1)
  print("0x%08X" % unk2) # filesize?
  print("%d" % data_base)
  print("%d files" % count)

  for i in range(count):
    offset = read32(f)
    size = read32(f)
    name = read_string(f, 256)
    print("%d: name: '%s' %d %d" % (i, name, offset, size))
  
    # Extract file
    if True:
      file_export_path = os.path.join(out_path, name)
      cursor = f.tell()
      with open(file_export_path, "wb") as fo:
        f.seek(data_base + offset)
        data = f.read(size)
        fo.write(data)
      f.seek(cursor)

      # Export texture metadata to MTL
      mtl = WavefrontMtl()
      mtl.NewMaterial("texture-%d" % i)
      mtl.IlluminationMode(9)
      mtl.DiffuseMap("%s" % name, scale=(512.0, -512.0, 1.0))
      #FIXME: Blender would use RGB channel for the alpha value
      #mtl.DissolveMap("%s" % name, scale=(512.0, -512.0, 1.0))
      mtl.Save(os.path.join("out", "texture-%d.mtl" % i))


