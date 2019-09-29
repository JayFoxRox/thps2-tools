#!/usr/bin/env python3

import sys

from common import *

# This must be activated for THPS1 files
thps1_file = False

for path in sys.argv[1:]:

  filename = path.rpartition('/')[2]

  print("# Disassembly of %s" % filename)

  with open(path, "rb") as f:

    def read_array():
      count = read16(f)
      array = []
      for i in range(count):
        value = read16(f)
        array += [value]
      return array

    def read_vector():
      x = read32s(f) / 4096.0
      y = read32s(f) / 4096.0
      z = read32s(f) / 4096.0
      return (x, y, z)

    # Object parser
    def parse_ob():

      nodes = read_array()

      pad = align(f, 4)
      checksum = read32(f)

      return [nodes, "%4s" % pad.hex(), "0x%08X" % checksum]

    #FIXME: Inline again - this is from early format RE which has proven wrong
    def handle_script_garbage(debug=False):
      unk1 = []
     
      unk2 = read_array()

      # These are only in baddys?
      if not debug:

        v4 = read16(f)
        v5 = read16(f)
        unk1 += ["0x%04X" % v4, "0x%04X" % v5]

        assert(v4 in [0x200, 0x201])
        assert(v5 in [0xFF04, 0xFF05])

      pad = align(f, 4)
      x, y, z = read_vector()
      unk1 += [x, y, z]

      v9 = read16(f)
      v10 = read16(f)
      v11 = read16(f)
      unk1 += ["0x%04X" % v9, "0x%04X" % v10, "0x%04X" % v11]

      print("Script-garbage: %4s %s # %s" % (pad.hex(), unk1, unk2))


    def disassemble_script():

      def disassemble_script_value(setter=False):
        command = read16s(f)

        #print("-> 0x%04X" % command)

        if command < 0x2000:
          assert(not setter)
          return "%d" % command

        #FIXME: Disallow setter for some of these

        elif command == 0x2120:
          index = read16(f)
          if setter:
            value = disassemble_script_value()
            return "V_REGISTER(%d, %s)" % (index, value)
          else:
            return "V_REGISTER(%d)" % index

        elif command == 0x2123:
          enable = read16(f)
          return "V_APPLY_GRAVITY(%d)" % enable #FIXME: ??

        elif command == 0x2125:
          unk1 = read16(f)
          unk2 = read16(f)
          return "V_ATTRIBUTE(%d, %d)" % (unk1, unk2)
        elif command == 0x2127:
          x = disassemble_script_value()
          y = disassemble_script_value()
          z = disassemble_script_value()
          return "V_ANGULAR_VELOCITY(%s, %s, %s)" % (x, y, z)
        elif command == 0x2128:
          x = read16s(f)
          y = read16s(f)
          z = read16s(f)
          return "V_ANGULAR_ACCELERATION(%d, %d, %d)" % (x, y, z)
        elif command == 0x2129:
          unk1 = read16(f)
          return "V_RANDOM(%d)" % unk1
        elif command == 0x212A:
          return "V_MY_NODE()"
        elif command == 0x212B:
          node = disassemble_script_value()
          return "V_LINKED_NODE(%s)" % node
        elif command == 0x212C:
          if setter:
            value = read16(f)
            return "V_INPUT_SIGNAL(%d)" % value
          else:
            return "V_INPUT_SIGNAL()"
        elif command == 0x212F:
          align(f, 4)
          checksum = read32(f)
          return "V_MODEL_CHECKSUM(0x%08X)" % checksum
        elif command == 0x2132:
          return "V_BRUCE_XZ_DIST()"
        elif command == 0x2134:
          x = read16s(f)
          y = read16s(f)
          z = read16s(f)
          return "V_VELOCITY(%d, %d, %d)" % (x, y, z)
        elif command == 0x2137:
          x = read16s(f)
          y = read16s(f)
          z = read16s(f)
          return "V_ANGLES(%d, %d, %d)" % (x, y, z)

        #FIXME: Disallow getters in this block?

        elif command == 0x4100:
          return "C_DONE()"
        elif command == 0x4102:
          label = read16(f)
          return "C_GOTO_BREAK(%d)" % label
        elif command == 0x4104:
          unk1 = read16(f)
          return "C_LABEL(%d)" % unk1
        elif command == 0x4105:
          #FIXME: !!!!
          return "C_READ_LABELS()"
        elif command == 0x4110:
          a = disassemble_script_value()
          b = disassemble_script_value()
          return "C_ADD(%s, %s)" % (a, b) #FIXME: ?
        elif command == 0x4112:
          a = disassemble_script_value()
          b = disassemble_script_value()
          return "C_IF_GT(%s, %s)" % (a, b)
        elif command == 0x4113:
          a = disassemble_script_value()
          b = disassemble_script_value()
          return "C_IF_LT(%s, %s)" % (a, b)
        elif command == 0x4114:
          a = disassemble_script_value()
          b = disassemble_script_value()
          return "C_IF_EQ(%s, %s)" % (a, b)
        elif command == 0x4116:
          a = read16(f)
          return "C_IF_FLAG_CLEAR(%s)" % (a)
        elif command == 0x4120:
          return "C_ENDIF()"
        elif command == 0x4203:
          return "C_DISPLAY_ON()"
        elif command == 0x4204:
          return "C_DISPLAY_OFF()"
        elif command == 0x4205:
          return "C_DIE_QUIETLY()"
        elif command == 0x4280:
          duration = disassemble_script_value()
          return "C_WAIT(%s)" % duration
        elif command == 0x4281:
          return "C_WAIT_FOR_SIGNAL()"
        elif command == 0x4290:
          n = read16s(f)
          return "C_PLAY_SFX(%d)" % n
        elif command == 0x4291:
          n = read16s(f)
          return "C_PLAY_POSITIONAL_SFX(%d)" % n
        elif command == 0x4292:
          count = read16(f)
          return "C_SPARK(%d)" % count
        elif command == 0x4293:
          align(f, 4)
          checksum = read32(f)
          return "C_SET_FMV_CHECKSUM(0x%08X)" % checksum
        elif command == 0x4294:
          return "C_START_FMV()"
        elif command == 0x4297:
          frames = read16(f)
          return "C_MIDI_FADE_OUT(%d)" % frames
        elif command == 0x4298:
          strength = read16(f)
          return "C_SHAKE_CAMERA(%d)" % strength
        elif command == 0x4299:
          track = read16(f)
          return "C_SET_FMV_TRACK(%d)" % track
        elif command == 0x429B:
          length = read16(f)
          damage = read16(f)
          r = read16(f)
          g = read16(f)
          b = read16(f)
          scrollspeed = read16(f)
          return "C_SMOKEJET_ON(%d, %d, %d, %d, %d, %d)" % (length, damage, r, g, b, scrollspeed)
        elif command == 0x429C:
          r = read16(f)
          g = read16(f)
          b = read16(f)
          duration = read16(f)
          sort = read16(f)
          return "C_FLASH_SCREEN(%d, %d, %d, %d, %d)" % (r, g, b, duration, sort)
        elif command == 0x429E:
          return "C_SET_WATER_LEVEL()"
        elif command == 0x429F:
          return "C_SMOKEJET_OFF()"
        elif command == 0x4221:
          node = disassemble_script_value()
          return "C_MOVE_TO_NODE(%s)" % (node)
        elif command == 0x42B0:
            name = read_string(f)
            align(f, 2)
            return "C_TEXT_MESSAGE(%s)" % code_string(name)
        elif command == 0x42B1:
          node = disassemble_script_value()
          return "C_SEND_PULSE_TO_LINKS(%s)" % node
        elif command == 0x42B2:
          node = disassemble_script_value()
          return "C_SEND_PULSE_TO_LINKS(%s)" % node
        elif command == 0x42B3:
          node = disassemble_script_value()
          return "C_SEND_SIGNAL_TO_NODE(%s)" % node
        elif command == 0x42B4:
          node = disassemble_script_value()
          return "C_SEND_PULSE_TO_NODE(%s)" % node
        elif command == 0x42C0:
          index = read16(f)
          return "C_GOALCOUNTER(%d)" % index
        elif command == 0x4301:
          return "C_SHATTER()"
        elif command == 0x4306:
          percent = read16s(f)
          frames = read16(f)
          return "C_SCALE_X(%d, %d)" % (percent, frames)
        elif command == 0x4307:
          percent = read16s(f)
          frames = read16(f)
          return "C_SCALE_Y(%d, %d)" % (percent, frames)
        elif command == 0x4308:
          percent = read16s(f)
          frames = read16(f)
          return "C_SCALE_Z(%d, %d)" % (percent, frames)
        elif command == 0x4309:
          enable = read16(f)
          return "C_IS_BOUNCY(%d)" % enable
        elif command == 0x4503:
          count = read16(f)
          return "C_MAKE_RAIN(%d)" % count
        elif command == 0x4507:
          n = read16s(f)
          return "C_PLAY_LOOPING_SFX(%d)" % n
        elif command == 0x4508:
          n = read16s(f)
          u = read16(f)
          return "C_PLAY_LOOPING_POSITIONAL_SFX(%d, %d)" % (n, u)
        elif command == 0x4509:
          return "C_STOP_LOOPING_SFX()"

        print("Unknown script-command: 0x%04X, alignment: %d" % (command, f.tell() % 4))

        return "Unknown:0x%04X" % command


      # There's blocks which are reached from others, so they have a indentation already
      indent_bias = 1

      indent = indent_bias
      while f.tell() < next_offset:
        s = disassemble_script_value(True)
        assert(s.count("(") == s.count(")"))
        if s[0:8] == "C_ENDIF(":
          indent -= 1
          assert(indent >= 0) #FIXME: This can't be done as the baddys seem to connect?
          indent = max(indent, 0) #FIXME: This hack shouldn't be needed
        print("%d" % indent + "  " * indent + " %d " % f.tell() +  s)
        if s[0:5] == "C_IF_":
          indent += 1

      # Reachable ENDIF when no IF is present
      true_bugs = []
      true_bugs += [645, 646, 666, 682, 683, 694, 698, 717, 724] # SKSF_T.TRG

      # Unreachable ENDIF when no IF is present
      false_bugs = []
      false_bugs += [576, 657] # SKMAR_T.TRG
      false_bugs += [626, 628, 629, 630, 631, 661, 662, 663, 664, 665] # SKNY_T.TRG
      false_bugs += [721] # SKSL2_T.TRG
      false_bugs += [430] # SKVEN_T.TRG

      assert(indent == indent_bias or node_i in [*false_bugs, *true_bugs])

    # Command disassembler
    def disassemble_commands():

      while True:

        command = read16(f)

        def disassemble_commands_command():
          if command == 2:
            names = []
            while True:
              #FIXME: The 2 player restart code in "Re_2P" somehow has no way to know how many strings will follow?!
              name = read_string(f)
              align(f, 2)
              if len(name) == 0:
                break
              names += [code_string(name)]
            return "SetCheatRestarts(%s)" % ", ".join(names)
          elif command == 3:
            return "SendPulse()"
          elif command == 4:
            return "SendActivate()"
          elif command == 5:
            return "SendSuspend()"
          elif command == 10:
            return "SendSignal()"
          elif command == 11:
            return "SendKill()"
          elif command == 12:
            return "SendKillLoudly()"
          elif command == 13:
            unk1 = read16(f)
            return "SendVisible(%d)" % unk1
          elif command == 104:
            unk1 = read16(f) # Start?
            unk2 = read16(f) # End?
            unk3 = read16(f) / 4096.0 # Unknown
            return "SetFoggingParams(%d, %d, %f)" % (unk1, unk2, unk3)
          elif command == 126:
            name = read_string(f)
            align(f, 2)
            return "SpoolIn(%s)" % code_string(name)
          elif command == 128:
            name = read_string(f)
            align(f, 2)
            return "SpoolIn(%s)" % code_string(name)
          elif command == 130:
            unk1 = read16(f)
            unk2 = read16(f)
            return "SetCamAngle(%d, %d)" % (unk1, unk2)
          elif command == 131:
            unk = read16(f)
            return "BackgroundOn(%d)" % unk
          elif command == 132:
            unk = read16(f)
            return "BackgroundOff(%d)" % unk
          elif command == 134:
            unk = read16s(f)
            return "SetInitialPulses(%d)" % unk
          elif command == 135:
            unk1 = read16(f)
            unk2 = read16(f)
            return "SetCamDistXZ(%d, %d)" % (unk1, unk2)
          elif command == 140:
            name = read_string(f)
            align(f, 2)
            return "SetRestart(%s)" % code_string(name)
          elif command == 141:
            #0: Invisible
            #1: Visible
            #2: InvisibleBoth
            #3: VisibleBoth

            #0: OutsideBox
            #1: InsideBox

            unk1 = read16(f)


            #FIXME: How does this work? These should be boxes with { vec3, vec3 } each
            if False:
              pad = align(f, 4)
            unk2 = []
            while True:
              unkx = read16(f)
              if unkx == 0xFF:
                break
              if False:
                unky = read16(f)
                v = (unkx << 16) | unky
                unk2 += ["\n" "0x%08X" % v]
                for _ in range(5):
                  v = read32(f)
                  unk2 += ["0x%08X" % v]
                print(unk2)
            return "SetVisibilityInBox(%d, %s)" % (unk1, ", ".join(unk2))
          elif command == 142:
            name = read_string(f)
            align(f, 2)
            return "SetObjFile(%s)" % code_string(name)
          elif command == 143:
            unk1 = read16(f)
            unk2 = read16(f)
            return "SetCamDistY(%d, %d)" % (unk1, unk2)
          elif command == 144:
            unk1 = read16(f)
            unk2 = read16(f)
            return "SetCamOffsetX(%d, %d)" % (unk1, unk2)
          elif command == 145:
            unk1 = read16(f)
            unk2 = read16(f)
            return "SetCamOffsetY(%d, %d)" % (unk1, unk2)
          elif command == 146:
            unk1 = read16(f)
            unk2 = read16(f)
            return "SetCamOffsetZ(%d, %d)" % (unk1, unk2)
          elif command == 147:
            index = read16(f)
            return "SetGameLevel(%d)" % index
          elif command == 149:
            return "Endif()"
          elif command == 151:
            size = read16(f)
            return "SetDualBufferSize(%d)" % size
          elif command == 152:
            #FIXME: Might take an argument?
            return "KillBruce()"
          elif command == 153:
            unk = read16(f)
            return "SetCamColijSide(%d)" % unk
          elif command == 155:
            unk = read16(f)
            return "MIDIFadeIn(%d)" % unk
          elif command == 157:
            unk = read16(f)
            return "SetReverbType(%d)" % unk
          elif command == 158:
            return "EndLevel()"
          elif command == 166:
            unk = read16(f)
            return "SetOTPushback(%d)" % unk
          elif command == 167:
            unk1 = read16(f)
            unk2 = read16(f)
            return "SetCamZoom(%d, %d)" % (unk1, unk2)
          elif command == 169:
            unk = read16(f)
            return "SetOTPushback2(%d)" % unk
          elif command == 171:  
            align(f, 4)
            checksum = read32(f)
            unk2 = read16(f)
            unk3 = read16(f)
            unk4 = read16(f)
            assert(unk2 == 0)
            assert(unk3 == 0)
            assert(unk4 == 0)
            return "BackgroundCreate(0x%08X, %d, %d, %d)" % (checksum, unk2, unk3, unk4)
          elif command == 178:
            name = read_string(f)
            align(f, 2)
            return "SetRestart2(%s)" % code_string(name)
          elif command == 200:
            color_hi = read16(f)
            color_lo = read16(f)
            color = (color_hi << 16) | color_lo
            return "SetFadeColor(0x%08X)" % color
          elif command == 202:
            color_hi = read16(f)
            color_lo = read16(f)
            color = (color_hi << 16) | color_lo
            return "SetSkyColor(0x%08X)" % color
          elif command == 203:
            unk = read16(f)
            return "SetCareerFlag(%d)" % unk
          elif command == 204:
            unk = read16(f)
            return "IfCareerFlag(%d)" % unk
          elif command == 201:
            align(f, 4)
            checksum = read32(f)
            unk3 = read16s(f)
            return "GapPolyHit(0x%08X, %d)" % (checksum, unk3)
          elif command == 65535:
            return "EndCommandList()"

          print("Unknown commands-command: 0x%04X, alignment: %d" % (command, f.tell() % 4))

          return "Unknown:0x%04X" % command
        
        s = disassemble_commands_command()
        assert(s.count("(") == s.count(")"))
        print(s)
        if s == "EndCommandList()":
          break

    # Read some header?
    magic = read32(f)
    version = read32(f)
    print(".header 0x%08X 0x%08X" % (magic, version))

    assert(magic == 0x4752545F)
    assert(version == 2)

    previous_cursor = None

    bad_node_types = []

    # Read each node
    node_count = read32(f)
    node_offsets = []
    for i in range(node_count):
      offset = read32(f)
      node_offsets += [offset]

    for node_i, (offset, next_offset) in enumerate(zip(node_offsets, node_offsets[1:])):

      assumed_size = next_offset - offset

      f.seek(offset)

      node_type = read16(f)

      print()
      print("# node %d at %d (assumed size: %d): type %d" % (node_i, offset, assumed_size, node_type))

      #print(node_type)
      if node_type == 1: # Baddy ?!


        unk1 = []

        v1 = read16(f)
        v2 = read16(f)
        unk1 += ["0x%04X" % v1, "0x%04X" % v2]

        al = f.tell() % 4
        
        print("%3d: %s %d Baddy: %s %d" % (node_i, filename, al, unk1, f.tell() - offset))

        assert(v1 in [203, 213, 215, 216, 217, 218, 219] + [0x192] + [0xD1]) # Game object identifier (= baddy type)
        assert(v2 in [0x1000, 0x1001])

        if v2 == 0x1001:
          unk1 = read_array()
          unk2 = read16(f)
          unk3 = read16(f)
          align(f, 4)
          x, y, z = read_vector()
          unk4 = f.read(6).hex()

          assumed_gap = next_offset - f.tell()
          print(assumed_gap)
          if assumed_gap == 0:
            print("THPS1/THPS2")
          elif assumed_gap >= 2:
            v = read16(f)
            print("THPS2-COMMANDS: 0x%04X" % v)
            assert(v == 0x0000)

            # This probably doesn't include a script, but some of them still contain a C_DONE()
            disassemble_script()


          # This is the same header as for script
          print("unk: %s 0x%04X, 0x%04X, %4s %f %f %f %s" % (unk1, unk2, unk3, pad.hex(), x, y, z, unk4)) #FIXME: There's still a script-command sometimes.. when?!

          #FIXME: If there is still more bytes (only very few files of THPS1 + Bullring), then there must be 2 bytes, followed by script-commands


        else:
          handle_script_garbage(False)
          disassemble_script()


      elif node_type == 2: # Crate

        unk1 = read16(f)
        assert(unk1 == 0)

        pad = align(f, 4)
        checksum = read32(f)

        print("Crate 0x%04X %4s 0x%08X" % (unk1, pad.hex(), checksum))

      elif node_type == 3: # Point ?!

        nodes = read_array()
        pad = align(f, 4)
        x, y, z = read_vector()

        print("Point %s %4s %f %f %f" % (nodes, pad.hex(), x, y, z))

      elif node_type == 4: # AutoExec

        print("AutoExec:")
        disassemble_commands()

      elif node_type == 5: # PowrUp ?!

        # For THPS2 (PC)
        pickup_types = {
          4: "KPickup",
          5: "SPickup",
          6: "APickup",
          10: "EPickup",
          15: "TPickup",
          16: "TapePickup",
          21: "BonusPickup100", # Alias: BonusPickup
          22: "BonusPickup200",
          23: "BonusPickup500",
          24: "MoneyPickup250", # Alias: MoneyPickup20
          25: "MoneyPickup50",
          26: "MoneyPickup100",
          33: "LevelPickup"
        }

        al = f.tell() % 8

        pickup_type = read16(f) # Type
        unk2 = read16(f)

        unk = []

        tmp = align(f, 4)

        # There appears to be a bug in SKNY_T.TRG where additional info is present for LevelPickup
    
        assumed_gap = next_offset - f.tell()
        print(assumed_gap)
        if assumed_gap == 20:
          print("THPS1")
        elif assumed_gap == 18:
          print("THPS2")
        elif assumed_gap == 22:
          u7 = read16(f)
          v8 = read16(f)
          unk += ["0x%04X:0x%04X" % (u7, v8)]
          print("THPS2-NYBUG")


        x, y, z = read_vector()
        unk += ["%f %f %f" % (x, y, z)]

        u7 = read16(f)
        v8 = read16(f)
        unk += ["0x%04X:0x%04X" % (u7, v8)]
        print(unk)
        assert(u7 in [0x0000, 0x0001]) #FIXME: 0x0001 is never seen in THPS2-Windows
        assert(v8 == 0x0001)

        v = read16(f)
        unk += ["0x%04X" % v]

        #print(unk)
        assert(v == 0xFFFF)

        # Another 0xFFFF for THPS1
        if assumed_gap == 20:
          v = read16(f)
          unk += ["0x%04X" % v]
          assert(v == 0xFFFF)


        print("%s %d PowrUp: %4s %02d %s # %s" % (filename, al, tmp.hex(), pickup_type, unk, pickup_types[pickup_type]))

        #assert(v2 in [0x0000, 0xFFFE, 0xFFFF])
        #assert(v4 in [0x0000, 0xFFFF])
        #assert(v6 in [0x0000, 0x0001, 0xFFFE, 0xFFFF])


      elif node_type == 6: # CommandPoint

        nodes = read_array()      
        align(f, 4)
        checksum = read32(f)
        print("CommandPoint: %s, 0x%08X" % (nodes, checksum))
        
        disassemble_commands()

        pass #FIXME

      elif node_type == 8: # Restart

        # Seems to be a list of CommandPoints?
        unk_count = read16(f)
        unk1 = []
        for j in range(unk_count):
          unk1 += [read16(f)]

        al = f.tell() % 4

       #FIXME: Read this, so we can assert 0 padding?


        # Same stuff as in script-garbage?

        pad = align(f, 4)
        x, y, z = read_vector()

        unk2 = read16(f)
        unk3 = read16(f)
        unk4 = read16(f)
        #assert(unk3 == 0x0000)


        print(f.tell())

        name = read_string(f) # I assumed 64 bytes, but then we read too much sometimes
        align(f, 2)

        #print(read16(f))
        #print(read16(f))

        if False:
          while True:
            unk = read_string(f) # I assumed 64 bytes, but then we read too much sometimes
            align(f, 2)
            print(unk)
            if len(unk) == 0:
              break

        print("%d %4s Restart: '%s' %s %f %f %f 0x%04X 0x%04X 0x%04X" % (al, pad.hex(), name, unk1, x, y, z, unk2, unk3, unk4))

        disassemble_commands()

      elif node_type == 10: # RailPoint

        unk2 = read_array()

        al = f.tell() % 4

        pad = align(f, 4)
        x, y, z = read_vector()
        unk4 = ["%f %f %f" % (x, y, z)]

        unk5 = read16(f)

        assumed_gap = next_offset - f.tell()
        if assumed_gap == 6:
          unk6 = "THPS1 Prototype: %s" % f.read(4).hex()
          unk7 = read16(f)
          unk6 += "0x%04X" % unk7
          assert(unk7 == 0xFFFF)          
        elif assumed_gap == 8:
          unk6 = "THPS1: %s" % f.read(8).hex()
        elif assumed_gap == 4:
          unk6 = "THPS2-SKATE_T: %s" % f.read(4).hex()
        else:
          unk6 = "UNK/THPS2" #FIXME: Also in THPS1 prototype - I assume they added some arguments at some point, but then removed them again?

        print("%s %d RailPoint: %s" % (filename, al, [unk2, "%4s" % pad.hex(), unk4, unk5, unk6]))

      elif node_type == 11: # RailDef

        al = f.tell() % 4

        unk1 = read_array()

        pad = align(f, 4)
        x, y, z = read_vector()
        unk2 = ["%f %f %f" % (x, y, z)]

        unk3 = f.read(2).hex()

        assumed_gap = next_offset - f.tell()
        print(assumed_gap)
        unk_extra = []
        if assumed_gap == 8:
          print("THPS1")
          unk_extra += [f.read(6)]
          v = read16(f)
          unk_extra += ["0x%04X" % v]
          assert(v == 0xFFFF)
        else:
          print("THPS2")

        print("%s %d RailDef: %s" % (filename, al, [unk1, "%4s" % pad.hex(), unk2, unk3, unk_extra]))

      elif node_type == 12: # TrickOb

        # THPS1 Prototype stuff
        if True:

          assumed_gap = next_offset - f.tell()
          if assumed_gap == 6:
            pad = align(f, 4)
            checksum = read32(f)

            assumed_gap = next_offset - f.tell()
            if assumed_gap == 2:
              v = read16(f)
              unk = "THPS1-Prototype=Extra=%d: 0x%08X 0x%04X" % (assumed_gap, checksum, v)
              assert(v == 0xFFFF)
            else:
              unk = "THPS1=%d: 0x%08X" % (assumed_gap, checksum)

          elif assumed_gap > 6:
            nodes = read_array()
            pad = align(f, 4)
            checksum = read32(f)

            assumed_gap = next_offset - f.tell()
            if assumed_gap == 2:
              v = read16(f)
              unk = "THPS1-Extra=%d: %s 0x%08X 0x%04X" % (assumed_gap, nodes, checksum, v)
              assert(v == 0xFFFF)
            else:
              unk = "THPS2=%d: %s 0x%08X" % (assumed_gap, nodes, checksum)


          elif assumed_gap == 14:
            unk = parse_ob()

            unk = "THPS2 %s" % unk

            if thps1_file:
              v = read16(f)
              unk += ["0x%04X" % v]
              #assert(v == 0xFFFF)
          else:
            unk = "???=%d" % assumed_gap


          print("TrickOb: %4s %s" % (pad.hex(), unk))


      elif node_type == 13: # CamPt

        #CamPtNormal				= 1
        #CamPtFollow				= 2
        #CamPtFollow_Close		= 0
        #CamPtFollow_CloseLow	= 1
        #CamPtFollow_Normal		= 2
        #CameraModeNormal		= 3
        #CamPtLead_Close		= 4
        #CamPtLead_CloseLow	= 5
        #CamPtLead_Normal		= 6
        #CameraModeBoss			= 18

        # Bogus names, but this kind of order is expected
        cam_link = read16(f)
        assert(cam_link == 0)
        pad = align(f, 4)
        x, y, z = read_vector()
        cam_radius = read16(f)
        cam_type = read16(f)
        print("CamPt: %d %4s %f %f %f, 0x%04X, 0x%04X" % (cam_link, pad.hex(), x, y, z, cam_radius, cam_type))

      elif node_type == 14: # GoalOb

        unk = parse_ob()

        assumed_gap = next_offset - f.tell()
        print(assumed_gap)
        if assumed_gap == 2:
          v = read16(f)
          assert(v == 0xFFFF)
          print("THPS1: 0x%04X" % v)
        else:
          print("THPS2")

        print("GoalOb: %s" % unk)

      elif node_type == 15: # AutoExec2

        print("AutoExec2:")
        disassemble_commands()

      elif node_type == 255: # Terminator

        print("Terminator")

      elif node_type == 501: # OffLight
    
        align(f, 4)
        x, y, z = read_vector()
        print("OffLight: %f %f %f %s" % (x, y, z, f.read(20).hex()))

      elif node_type == 1000: # ScriptPoint

        print("ScriptPoint:")
        handle_script_garbage(True)
        disassemble_script()

      else:
        print("Unknown node-type %d" % node_type)

      cursor = f.tell()
      size = cursor - offset

      # Before we seek, check if we will go where we expect
      if size != assumed_size:
        delta = assumed_size - size
        data = f.read(max(0, delta))
        print("# Bad read size in node (type %d); Reached %d, expected %d (%+d): %s" % (node_type, cursor, offset, delta, data.hex()))
        #assert(delta > 0) #FIXME: Re-enable
        if not node_type in bad_node_types:
          bad_node_types += [node_type]

    print("%s: Review sizes in the following types: %s" % (filename, bad_node_types))


