#!/usr/bin/env python3

import sys
import os
import PIL.ImagePalette

from common import *

export = True

for path in sys.argv[1:]:

  print("Converting '%s'" % path)

  with open(path, "rb") as f:
    
    # Header 0x0003 0x0002 - THPS1 prototype april 9 1999
    # Header 0x0004 0x0002 - THPS1 release version
    # Header 0x0006 0x0002 - THPS2X release version

    version = read16(f)
    unk = read16(f)

    print("Header 0x%04X 0x%04X" % (version, unk))
    assert(version in [3, 4, 6])
    assert(unk == 0x0002)

    tag_start = read32(f)
    print(tag_start)

    # Read objects    
    object_count = read32(f)
    print("Objects (%d total)" % object_count)
    objects = []
    for i in range(object_count):
      class Object():
        def __init__(self):
          self.flags = read32(f)
          self.x = read32s(f)
          self.y = read32s(f)
          self.z = read32s(f)
          self.unk1 = read32(f)
          self.unk2 = read16(f)
          self.model_index = read16(f)
          self.unk_x = read16s(f)
          self.unk_y = read16s(f)
          self.unk3 = read32(f)
          self.unk_rgbx = read32(f)
          print("%d. flags:0x%08X, %d %d %d, 0x%08X, 0x%04X, model:%d, %d %d, 0x%08X, rgbx-pointer:0x%08X" % (i,
                                                                                                              self.flags,
                                                                                                              self.x, self.y, self.z,
                                                                                                              self.unk1,
                                                                                                              self.unk2,
                                                                                                              self.model_index,
                                                                                                              self.unk_x, self.unk_y,
                                                                                                              self.unk3,
                                                                                                              self.unk_rgbx))
          assert(self.unk1 == 0x00000000)
          assert(self.unk2 == 0x0000)
          assert(self.unk3 == 0x00000000)

      objects += [Object()]

    # Read models
    model_offsets = []
    model_count = read32(f)
    print("Models (%d total)" % model_count)
    for i in range(model_count):
      offset = read32(f)
      model_offsets += [offset]
    models = []
    for i, offset in enumerate(model_offsets):
      f.seek(offset)

      class Model():
        def __init__(self):

          model = self

          # Counts not exported, as implied by list lengths
          if version >= 4:
            self.unknown_flags = read16(f)
            vertex_count = read16(f)
            normal_count = read16(f)
            face_count = read16(f)
            print("0x%X" % self.unknown_flags)
            assert(self.unknown_flags in [0x8, 0xA, 0x88])
          else:
            self.unknown_flags = read32(f)
            vertex_count = read32(f)
            normal_count = read32(f)
            face_count = read32(f)
            print("0x%X" % self.unknown_flags)
            assert(self.unknown_flags in [0x8, 0xA, 0x9, 0x88, 0x8A])

          self.radius = read32(f)
          self.xmax = read16s(f)
          self.xmin = read16s(f)
          self.ymax = read16s(f)
          self.ymin = read16s(f)
          self.zmax = read16s(f)
          self.zmin = read16s(f)
          self.unknown_value = read32(f)

          print("%d. flags: 0x%08X radius:%d x:(%d,%d), y:(%d,%d), z:(%d,%d) 0x%08X" % (i, self.unknown_flags,
                                                                             self.radius,
                                                                             self.xmax, self.xmin,
                                                                             self.ymax, self.ymin,
                                                                             self.zmax, self.zmin,
                                                                             self.unknown_value))

          print("Vertices (%d total)" % vertex_count)
          self.vertices = []
          for j in range(vertex_count):
            class Vertex():
              def __init__(self):
                self.x, self.y, self.z = read_struct(f, "<hhh")
                self.pad = read16(f)

            self.vertices += [Vertex()]

          #FIXME: Rename to normals
          print("Normals (%d total)" % normal_count)
          self.normals = []
          for j in range(normal_count):
            class Normal():
              def __init__(self):
                self.x, self.y, self.z = read_struct(f, "<hhh")
                self.pad = read16(f)

            self.normals += [Normal()]

          print("Faces (%d total)" % face_count)
          self.faces = []
          for j in range(face_count):
            class Face():
              def __init__(self):

                doc = """
                  0x0003 - both set if textured, cleared if flat.
                      Having either enabled enables texturing, but both should be enabled.
                      0x0001 on its own enables texturing and texcoords, but does not look up the correct texture.
                      0x0002 on its own enables texturing, but gives garbage coordinates.
                  0x0010 - set if triangle, cleared if quad.
                  0x0080 - set if invisible and non-physical, cleared if visible and physical.
                  0x0800 - set if gouraud-shaded, cleared if flat-shaded.
                  0x1000 - set if this polygon needs to be subdivided.
                      This should be enabled for textured polys, and disabled for untextured.
                      Attempting to subdivide an untextured poly results in it disappearing.
                """
                self.base_flags = read16(f)
                print("%d. base-flags:0x%04X" % (j, self.base_flags))

                length = read16(f)
                next_offset = f.tell() + length - 4

                if version >= 4:
                  self.vertex_indices = read_struct(f, "<BBBB")
                else:
                  self.vertex_indices = read_struct(f, "<HHHH")
                for vertex_index in self.vertex_indices:
                  assert(vertex_index < vertex_count)

                doc = """
                  Gouraud case: Per-vertex RGBs palette indices. For triangles the last one is 0.
                  Flat case: The first 32-bit word of a PS1 GPU command...
                      First three bytes are (R, G, B).
                      Fourth byte is the command:
                          0x20 - Untextured, opaque, flat-shaded triangle.
                          0x22 - Untextured, translucent, flat-shaded triangle.
                          0x24 - Textured, opaque, flat-shaded triangle.
                          0x26 - Textured, translucent, flat-shaded triangle.
                          0x28 - Untextured, opaque, flat-shaded quad.
                          0x2A - Untextured, translucent, flat-shaded quad.
                          0x2C - Textured, opaque, flat-shaded quad.
                          0x2E - Textured, translucent, flat-shaded quad.
                """
                self.gpu_cmd = read_struct(f, "<BBBB")

                #FIXME: Rename to normals
                self.normal_index = read16(f)
                assert(self.normal_index < normal_count)

                #FIXME: Improve these docs
                doc = """
                  0x0010 - set if wallrideable.
                  0x0040 - set for a quarterpipe's "large polygon". Typically has base flag 0x0080 set.
                  0x0080 - set if... I don't know what this does actually.
                  0x0100 - cleared if you can skate on it.
                """
                self.surface_flags = read16(f)

                #FIXME: Should this be handled using gpu_cmd instead?

                if model.unknown_flags & 1 == 0: #FIXME: Just a guess.. 0x9 unknown_flags fucks up logic otherwise
                  if self.base_flags & 2:
                    self.texture_index = read32(f)
                    print("texture-index: %d" % self.texture_index)

                if self.base_flags & 1:
                  u = []
                  v = []
                  if version >= 6:
                    for _ in range(4):
                      u += [read16(f)]
                    for _ in range(4):
                      v += [read16(f)]
                  else:
                    for _ in range(4):
                      u += [read8(f)]
                      v += [read8(f)]
                  self.uvs = list(zip(u, v))

                if self.base_flags & 0x8:
                  v1 = read32(f)
                  v2 = read32(f)
                  print("Unknown-0x8-flag: 0x%08X 0x%08X" % (v1, v2))
                  #FIXME: Buggy in THPS1 proto april 9
                  #assert(v1 == 0x00000000)
                  #assert(v2 == 0x00000000)

                if model.unknown_flags & 1 == 0: #FIXME: Just a guess.. 0x9 unknown_flags fucks up logic otherwise
                  if self.base_flags & 0x20:
                    v = read32(f)
                    print("Unknown-0x20-flag: 0x%08X" % v)
                    assert(v in [0x00000000])

                print(f.tell(), next_offset)

                # 0x3 is always dual
                #FIXME: according to iamgreaser docs, this should also affect 0x1000
                #if self.base_flags & 0x2: assert(self.base_flags & 0x1) #FIXME: Violated in THPS1 proto april 9
                if self.base_flags & 0x1: assert(self.base_flags & 0x2)

                unhandled_base_flags = self.base_flags & ~(0x4000 | 0x2000 | 0x1000 | 0x800 | 0x400 | 0x100 | 0x80 | 0x40 | 0x20 | 0x10 | 0x8 | 0x4 | 0x2 | 0x1)
                if unhandled_base_flags != 0:
                  print("Unhandled flags: 0x%04X in 0x%04X" % (unhandled_base_flags, self.base_flags))
                  assert(False)

                assert(f.tell() == next_offset)
                f.seek(next_offset) #FIXME: Remove

            self.faces += [Face()]

      models += [Model()]




    #FIXME: There exist other flags which add zeros after this, but the purpose of those flags are unknown.

    # Read tags
    f.seek(tag_start)

    while True:
      tag_type = read32(f)
      if tag_type == 0xFFFFFFFF:
        break

      tag_length = read32(f)
      next_offset = f.tell() + tag_length

      print("Tag 0x%08X at %d" % (tag_type, f.tell()))

      if tag_type == 0x0000000A:
        print("Blockmap")
      elif tag_type == 0x73424752:
        print("RGBs")
      else:
        print("Unknown tag: 0x%08X" % tag_type)

      #FIXME: Assert that we ended up there?
      f.seek(next_offset)

    # Read model names
    print("Model names")
    model_names = []
    for i in range(model_count):
      name = read32(f)
      print("%d. %08X" % (i, name))
      model_names += [name]

    # Read texture names
    texture_name_count = read32(f)
    texture_names = []
    print("Texture names (%d total)" % texture_name_count)
    for i in range(texture_name_count):
      name = read32(f)
      print("%d. %08X" % (i, name))
      texture_names += [name]

    # Read 4bpp palettes
    palette4_count = read32(f)
    palettes4 = {}
    print("Palettes-4bpp (%d total)" % palette4_count)
    for i in range(palette4_count):
      name = read32(f)
      print("%d. %08X" % (i, name))
      palette = read_struct(f, "H"*16)
      palettes4[name] = palette

    # Read 8bpp palettes
    palette8_count = read32(f)
    palettes8 = {}
    print("Palettes-8bpp (%d total)" % palette8_count)
    for i in range(palette8_count):
      name = read32(f)
      print("%d. %08X" % (i, name))
      palette = read_struct(f, "H"*256)
      palettes8[name] = palette

    # Read textures
    texture_offsets = []
    texture_count = read32(f)
    if version >= 6:
      if (texture_count == 0xFFFFFFFF):
        print("???")

        # Read texture references (?)
        texture_reference_count = read32(f)
        print("Texture references (%d total)" % texture_reference_count)
        for i in range(texture_reference_count):
          name = read_string(f, 32)
          unk = read32(f)
          print("%d. Texture reference '%s' 0x%08X" % (i, name, unk))
          assert(unk == 0x00000001)

        # Read cubemap texture references (?)
        cubemap_texture_reference_count = read32(f)
        print("Cubemap Texture references (%d total)" % cubemap_texture_reference_count)
        for i in range(cubemap_texture_reference_count):
          name = read_string(f, 32)
          unk = read32(f)
          assert(unk == 0x00000001)
          print("%d. Cubemap Texture reference '%s' 0x%08X" % (i, name, unk))
          #FIXME: Ensure we have read the data that follows this

        texture_count = read32(f)

    print(f.tell())

    print("Textures (%d total)" % texture_count)
    for i in range(texture_count):
      offset = read32(f)
      print(f.tell(), offset)
      texture_offsets += [offset]


    textures = []
    for i, offset in enumerate(texture_offsets):


      if f.tell() != offset:
        delta = offset - f.tell()
        print("BROKEN %d bytes left !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n\n" % delta)
        assert(False)
      else:
        assert(f.tell() == offset)
      f.seek(offset)

      class Texture():
        def __init__(self):
          self.unk1 = read32(f)
          self.color_count = read32(f)
          self.palette_name = read32(f)
          self.name_index = read32(f)
          self.width = read16(f)
          self.height = read16(f)
          if self.color_count == 16:
            alignment = 3 # 4 pixels
          elif self.color_count == 256:
            alignment = 1 # 2 pixels
          elif self.color_count == 65536:
            alignment = 0
          else:
            alignment = 0
            assert(False)
          self.aligned_width = (self.width + alignment) & ~alignment
          self.aligned_height = (self.height + alignment) & ~alignment
          #FIXME: Read this texture pixel data as part of texture loading, but don't apply palette yet
          print("%d. %d %d 0x%08X %d (-> 0x%08X) %dx%d" % (i, self.unk1, self.color_count, self.palette_name, self.name_index, texture_names[self.name_index], self.width, self.height))

      texture = Texture()
      textures += [texture]

      texture_name = texture_names[texture.name_index]

      # Find the right palette
      #FIXME: Might not be necessary? Are all palettes in one table?
      if texture.color_count == 16:
        palette15 = palettes4[texture.palette_name]
      elif texture.color_count == 256:
        palette15 = palettes8[texture.palette_name]
      elif texture.color_count == 65536:
        palette15 = list(range(256)) #palettes16[texture.palette_name] # ???
      else:
        palette15 = []
        assert(False)

      # Convert palette to RGB
      #FIXME: Just construct DDS header instead
      def color15_to_rgb(color15):
        #FIXME: Check for magic constant which marks texture as alpha?
        r = int(((color15 >> 0) & 0x1F) / 31.0 * 0xFF)
        g = int(((color15 >> 5) & 0x1F) / 31.0 * 0xFF)
        b = int(((color15 >> 10) & 0x1F) / 31.0 * 0xFF)
        #assert(color15 >> 15 == 0) #FIXME: This triggers
        return r, g, b
      palette_rgb = [channel
                     for color15 in palette15
                     for channel in color15_to_rgb(color15)]

      if version >= 6:
        # Path taken in SkDemo.psx from THPS2X

        #FIXME: Pick this automatically
        if texture.unk1 & 512 or texture.unk1 & 1024 or texture.unk1 & 2048:
          unku = f.read(8)
          print("version 6 unknown 1a: %s" % unku.hex())
        else:
          unku = bytes([])
        if texture.unk1 & 4096:
          unkv = f.read(4) # Only second half of 1a?
          print("version 6 unknown 1b: %s" % unkv.hex())
        else:
          unkv = bytes([])
        print(f.tell())
        unk = read32(f)
        print("version 6 unknown 2: 0x%08X" % unk)
        assert(unk in [0x00000201, 0x00000301, 0x00000401, 0x00000901])
        length = read32(f)
        print("version 6 unknown 3: %d (length?)" % length)

        # SkDemo
        #
        #1. 1 65536 0x00000000 0 128x128
        #60532
        #version 6 unknown 2: 0x00000401
        #version 6 unknown 3: 7528 (length?)
        #
        # In reality, this is 32x32 RGB565 [maybe?]


        # Unknown origin:
        #
        #2. 16 65536 0x00000000 61 128x64
        #798900
        #version 6 unknown 2: 0x00000901
        #version 6 unknown 3: 16392 (length?)
        #version 6 unknown data:
        #
        # Trustworthy. 128x64 R5G6B5; clearly readable text in image


        data = f.read(length - 8)
        with open(os.path.join("out", "RAW-unk-%08X__%08X-0x%08X-%d-%d-%s-%s.raw" % (unk, texture_name, texture.unk1, texture.width, texture.height, unku.hex(), unkv.hex())), "wb") as fo:
          fo.write(data)

        #unk = f.read(10) # Unknown, probably should be *after* data
        #print("version 6 unknown data: %s" % data.hex())

        f1 = read_float(f)
        f2 = read_float(f)
        print("version 6 unknown pair: %f %f" % (f1, f2))
        continue

        mipmap_levels = 5 #FIXME: This is just an assumption
      else:
        mipmap_levels = 1

      for mipmap_level in range(mipmap_levels):

        width = texture.aligned_width >> mipmap_level
        height = texture.aligned_height >> mipmap_level

        print("Doing mipmap %dx%d" % (width, height))

        # Create a fitting array for an 8-bit palette
        texture_data = bytearray([0x00] * width * height)

        def put_pixel(x, y, palette_index):
          color = palette_rgb[palette_index]
          texture_data[y * width + x] = palette_index

        # Convert palette indices to 8-bit
        #FIXME: Could be more optimized
        for y in range(height):
          for x in range(width):
            if texture.color_count == 16:
              # We process 2 pixels at a time for 4bpp
              if x % 2 == 0:
                try:
                  palette_indices = read8(f)
                except:
                  print(x, y)
                  assert(False)
                put_pixel(x + 0, y, palette_indices & 0xF)
                put_pixel(x + 1, y, (palette_indices >> 4) & 0xF)
            elif texture.color_count == 256:
              palette_index = read8(f)
              put_pixel(x, y, palette_index)
            elif texture.color_count == 65536:
              texture_data[(y * width) + x] = read16(f) & 0xFF
            else:
              assert(False)

        if export:

          # Export texture data to PNG
          pil_image = PIL.Image.frombytes("P", (width, height), bytes(texture_data))
          pil_image.putpalette(palette_rgb, "RGB")
          pil_image.save(os.path.join("out", "%08X-%d.png" % (texture_name, mipmap_level)))

      if export:

        # Export texture metadata to MTL
        mtl = WavefrontMtl()
        mtl.NewMaterial("%08X" % texture_name)
        mtl.DiffuseMap("%08X-0.png" % texture_name, scale=(texture.aligned_width, -texture.aligned_height, 1.0))
        mtl.Save(os.path.join("out", "%08X.mtl" % texture_name))

    #FIXME: Make assumption where f.tell() should be
    #       = end of file in version >= 6 ?
    print(f.tell())

    print("Exporting Wavefront OBJ")

    # Create Wavefront OBJ for the world
    obj = WavefrontObj()

    # Export models
    for object_ in objects:

      model = models[object_.model_index]
      model_name = model_names[object_.model_index]

      obj.Object("%08X" % model_name)

      obj_vertex_indices = []
      for vertex in model.vertices:
        #obj_vertex_indices += [obj.Vertex(vertex.x, vertex.y, vertex.z)]
        obj_vertex_indices += [obj.Vertex((object_.x / 4096.0 + vertex.x) / 4096.0,
                                          (object_.y / 4096.0 + vertex.y) / 4096.0,
                                          (object_.z / 4096.0 + vertex.z) / 4096.0)]

      obj_normal_indices = []
      for normal in model.normals:
        obj_normal_indices += [obj.Normal(normal.x, normal.y, normal.z)]

      for j, face in enumerate(model.faces):

        # Skip invisible faces
        #FIXME: Just important them separately or something
        if face.base_flags & 0x80:
          continue

        # Helper to remove last vertex for triangles / re-order vertices for quad
        def pick_vertices(vertices):
          if face.base_flags & 0x10:
            return [vertices[2], vertices[1], vertices[0]]
          else:
            return [vertices[0], vertices[2], vertices[3], vertices[1]]
        
        # Get vertices
        obj_vertex = []
        for vertex_index in pick_vertices(face.vertex_indices):
          obj_vertex += [obj_vertex_indices[vertex_index]]

        # Set material
        if face.base_flags & 2:
          if model.unknown_flags & 1 == 0: #FIXME: Just a guess.. 0x9 unknown_flags fucks up logic otherwise
            texture_name = texture_names[face.texture_index]
          else:
            texture_name = 0xFFFFFFFF00000000

          if version >= 6:
            #FIXME: Hack, because we don't know the texture names when exporting DDX (yet?)
            #FIXME: Hack doesn't work
            # I also tried:
            # - textures[face.texture_index].name_index
            # - face.texture_index
            for texture_index, texture in enumerate(textures):
              if texture.name_index == face.texture_index:
                break
            if texture.unk1 & 512:
              # Some DDS texture?
              obj.MaterialLibrary("texture-%d.mtl" %  texture_index)
              obj.UseMaterial("texture-%d" % texture_index)
            else:
              # Seems to use embedded texture?
              name = "unknown-0x%08X-face:%d-list:%d:0x%08X" %  (texture.unk1,face.texture_index,texture_index,texture_names[texture.name_index])
              obj.MaterialLibrary("%s.mtl" % name )
              obj.UseMaterial("%s" % name)
          else:
            obj.MaterialLibrary("%08X.mtl" % texture_name)
            obj.UseMaterial("%08X" % texture_name)
        else:
          obj.MaterialLibrary("None")
          obj.UseMaterial("None")

        # Get optional UVs
        if face.base_flags & 1:
          obj_texture_coordinate = []
          for u, v in pick_vertices(face.uvs):

            # This is probably a bad idea.. just do this transform while rendering
            if False:
              # Normalize UV
              if face.base_flags & 2:
                texture_name = texture_names[face.texture_index]
                texture = textures[texture_name]
                u /= texture.width
                v /= texture.height
              else:
                # What to do now?
                assert(False)

            obj_texture_coordinate += [obj.TextureCoordinate(u, v)]
        else:
          obj_texture_coordinate = None

        # Get normal
        obj_normal = [obj_normal_indices[face.normal_index]] * len(obj_vertex)

        # Create face
        #print(obj_vertex)
        #print(obj_texture_coordinate)
        #print(obj_normal)
        obj.Face(obj_vertex, obj_texture_coordinate, obj_normal)

      print(object_.model_index)

    #obj.Save(os.path.join("out", "%d.obj" % object_.model_index))
    obj.Save(os.path.join("out", "world.obj"))

