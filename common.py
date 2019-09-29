import struct

def read_string(f, n=0):
  if n == 0:
    s = b''
    while True:
      c = f.read(1)
      if c == b'\0':
        break
      s += c
  else:
    s = f.read(n)
    s = s.partition(b'\0')[0]
  try:
    s = s.decode('ascii')
  except:
    s = s.decode('latin-1') #FIXME: This is a poor fallback
  return s

def read8(f):
  return struct.unpack("<B", f.read(1))[0]

def read16(f):
  return struct.unpack("<H", f.read(2))[0]

def read16s(f):
  return struct.unpack("<h", f.read(2))[0]

def read32(f):
  return struct.unpack("<I", f.read(4))[0]

def read32s(f):
  return struct.unpack("<i", f.read(4))[0]

def read_float(f):
  return struct.unpack("<f", f.read(4))[0]

def read_struct(f, fmt):
  size = struct.calcsize(fmt)
  return struct.unpack(fmt, f.read(size))

def align(f, n):
  return f.read((n - (f.tell() % n)) % n)

def is_repeating(p, v):
  for x in list(p):
    if x != v:
      return False
  return True

def code_string(s):
  s = s.encode('unicode_escape')
  s = s.decode('utf-8')
  return "\"%s\"" % s.replace('"', '\\"')

def code_float(f):
  #FIXME: Remove trailing zeroes
  return "%f" % f

def crc32(data, start=0xFFFFFFFF):
  result = start
  for byte in data:
    mask = result ^ byte
    for _ in range(8):
      result = ((result << 1) | (result >> 31)) & 0xFFFFFFFF
      if mask & 1:
        result ^= 0xEDB88320
      mask >>= 1

  #FIXME: Make this work somehow?
  if False:
    import zlib
    ref = zlib.crc32(data, 0xFFFFFFFF)
    ref2 = ref ^ 0xFFFFFFFF
    print("%08X == %08X (needs to be %08X)" % (ref, ref2, result))

  return result

#FIXME: Remove, this is a check for the CRC algo
if False:
  import sys
  for arg in sys.argv[1:]:
    print("0x%08X: '%s'" % (crc32(arg.encode('ascii')), arg)) # must be B57D1831

#FIXME: Remove, this is a (rather slow) bruteforce algorithm
if False:


  alphabet = [x.encode('ascii') for x in "abcdefghijklmnopqrstuvwxyz_0123456789."] # ["%d" % i for i in range(10)]

  symbols = [0]
  results = [0xFFFFFFFF, 0]

  first_valid = 0

  checksums = [
    0xB57D1831,
    0xFDA4795D,
    0xFDD2C22E,
    0x59BFF7DD,
    0xA438A846,
    0x00559DB5,
    0x8E26EDC7,
    0x2A4BD834,
    0xF345F263,
    0x5728C790,
    0x7B88F05C,
    0xDFE5C5AF,
    0xC32151A1,
    0x674C6452
  ]

  while True:

    # Update all invalid hashes
    for i in range(first_valid+1, len(symbols)+1):
      results[i] = crc32(alphabet[symbols[i - 1]], results[i - 1])

    # Try the longest one, with all known extensions
    prefix_list = [b"", b"load"] # Common prefix can be removed
    suffix_list = [b"", b".bmp", b".pre", b".psx", b".vab", b".sfx", b".txt", b".psh"] #FIXME: Can check dot once etc. = sort and trim

    if False:
      for prefix in prefix_list:
        helper = crc32(prefix, results[0])
        #FIXME: Need to combine prefix CRC with later CRC; see zlib crc32_combine
        #       Also see https://stackoverflow.com/questions/23122312/crc-calculation-of-a-mostly-static-data-stream/23126768#23126768
        #results[-1]

    for suffix in suffix_list:
      checksum = crc32(suffix, results[-1])
      if checksum in checksums:
        word = b"".join([alphabet[symbol] for symbol in symbols])
        print("Found '%s' for 0x%08X" % (word + suffix, checksum))

    if False:
      print()
      crc = crc32(word)
      print(word, "< ref word (0x%08X)" % crc)
      assert(results[-1] == crc)
    
    # Go to next letter
    first_valid = len(symbols) - 1
    symbols[first_valid] += 1

    # Handle overflow
    while symbols[first_valid] >= len(alphabet):
      # Check if need a new letter
      if first_valid == 0:
        # Add a new symbol and reset
        symbols = [0] * (len(symbols) + 1)
        results += [0]
        print("Length %d" % len(symbols))
        break
      else:
        # Update the prior one
        symbols[first_valid] = 0
        first_valid -= 1
        symbols[first_valid] += 1

    if False:
      for i in range(0, first_valid+1):
        result = results[i]
        print(result, "< hash old [%d %d]" % (i, len(result)))

      for i in range(first_valid+1, len(symbols)+1):
        results[i] = results[i - 1] + alphabet[symbols[i - 1]]
        result = results[i]
        print(result, "< hash updated [%d %d]" % (i, len(result)))

      for i in range(0, len(results)):
        result = results[i]
        assert(len(result) == i)

      print("O" * first_valid)
      print(" " * first_valid + "N" * (len(symbols) - first_valid))





class _FileWriter():
  def __init__(self):
    self._contents = []
  def _write(self, data):
    self._contents += [data]
  def Save(self, path):
    with open(path, "wb") as fo:
      fo.write(''.join(self._contents).encode('utf-8'))

class WavefrontMtl(_FileWriter):
  def __init__(self):
    _FileWriter.__init__(self)
  def NewMaterial(self, name):
    #FIXME: How to handle spaces?
    self._write("newmtl %s\n" % name)
  def _map(self, target, name, scale=None):
    line = "map_%s" % target
    if scale != None:
      line += " -s %f %f %f" % scale
    #FIXME: Bugs in blender prevent use of quotation marks? Debug..
    #       For now, replace spaces by underscore
    line += " %s\n" % name.replace(" ", "_")
    self._write(line)
  def IlluminationMode(self, mode):
    self._write("illum %d\n" % mode)
  def DiffuseMap(self, name, scale=None):
    self._map("Kd", name, scale)
  def DissolveMap(self, name, scale=None):
    self._map("d", name, scale)

class WavefrontObj(_FileWriter):
  def __init__(self):
    _FileWriter.__init__(self)
    self._vertex_count = 0
    self._normal_count = 0
    self._texture_coordinate_count = 0
  def Object(self, name):
    self._write("o %s\n" % name)
  def MaterialLibrary(self, name):
    self._write("mtllib %s\n" % name)
  def UseMaterial(self, name):
    self._write("usemtl %s\n" % name)
  def Comment(self, comment):
    #FIXME: Split by line and ensure "# " prefix
    self._write("# %s\n" % comment)
  def Vertex(self, x, y, z):
    self._write("v %f %f %f\n" % (x, y, z))
    self._vertex_count += 1
    return self._vertex_count
  def TextureCoordinate(self, u, v):
    self._write("vt %f %f\n" % (u, v))
    self._texture_coordinate_count += 1
    return self._texture_coordinate_count
  def Normal(self, x, y, z):
    self._write("vn %f %f %f\n" % (x, y, z))
    self._normal_count += 1
    return self._normal_count
  def Face(self, vertex_indices, texture_coordinate_indices, normal_indices):
    assert(texture_coordinate_indices == None or len(texture_coordinate_indices) == len(vertex_indices))
    assert(normal_indices == None or len(normal_indices) == len(vertex_indices))

    line = "f"
    for i, vertex_index in enumerate(vertex_indices):

      line += " %d" % vertex_index

      # Helper to keep a clean file
      def index(line, indices, skipped=0):
        if indices != None:
          line += "/" * skipped + "/%d" % indices[i]
          return line, 0
        return line, skipped + 1

      # Write additional information
      line, skipped = index(line, texture_coordinate_indices)
      line, skipped = index(line, normal_indices, skipped)

    line += "\n"

    self._write(line)
