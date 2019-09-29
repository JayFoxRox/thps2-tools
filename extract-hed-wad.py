#!/usr/bin/env python3

import sys
import os

from common import *

# Open the HED file
with open(sys.argv[1], "rb") as f:

  # Get file size to know where it ends
  f.seek(0, os.SEEK_END) 
  file_size = f.tell()
  f.seek(0)

  # Also open the WAD file
  with open(sys.argv[2], "rb") as fw:

    # Loop over HED entries
    while f.tell() < file_size - 7:
      print(f.tell(), file_size)
      name = read_string(f)
      #FIXME: Check for terminator?
      align(f, 4)
      offset = read32(f)
      size = read32(f)

      print("file: '%s'" % name)

      fw.seek(offset)

      # Construct path
      file_export_path = os.path.join("out", name)

      # Extract file
      with open(file_export_path, "wb") as fo:
        data = fw.read(size)
        fo.write(data)

  terminator = read8(f)
  assert(terminator == 0xFF)
