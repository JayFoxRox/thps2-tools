#!/usr/bin/env python3

import sys
import os

from common import *

with open(sys.argv[1], "rb") as f:
  magic = read32(f)
  version = read32(f)
  num_dir = read32(f)
  num_file = read32(f)

  known_files = 0

  for i in range(num_dir):
    name = read_string(f, 32)
    print("dir: '%s'" % name)
    offset = read32(f)
    count = read32(f)
    
    # Create path
    path = name.split('/')
    dir_export_path = os.path.join("out", *path)
    os.makedirs(dir_export_path, exist_ok=True)

    known_files += count

    # Dump all files
    cursor = f.tell()
    f.seek(offset)
    for j in range(count):

      name = read_string(f, 32)
      print("\tfile: '%s'" % name)
      unk1 = read32(f)
      assert(unk1 == 0xFFFFFFFE)
      data_offset = read32(f)
      size1 = read32(f)
      size2 = read32(f)
      assert(size1 == size2)

      file_cursor = f.tell()
      f.seek(data_offset)

      # Construct path
      file_export_path = os.path.join(dir_export_path, name)

      # Extract file
      with open(file_export_path, "wb") as fo:
        data = f.read(size1)
        fo.write(data)

      f.seek(file_cursor)

    f.seek(cursor)


print("%d / %d files known" % (known_files, num_file))

