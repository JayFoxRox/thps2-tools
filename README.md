This is a collection of tools for Tony Hawk's Pro Skater 2.

There's a lot of overlap with these other games, potentially based on the Neversoft Big Guns engine:

- SW: Skeleton Warriors
- AP: Apocalypse
- MDK: MDK (PlayStation)
- SM: Spiderman
- THPS1!April9: Tony Hawk's Pro Skater 1 (April 9 1999 build)
- THPS1!July7: Tony Hawk's Pro Skater 1 (July 7 1999 build)
- THPS1!July10: Tony Hawk's Pro Skater 1 (July 10 1999 build)
- THPS1: Tony Hawk's Pro Skater 1
- SM2: Spider-Man 2: Enter: Electro
- THPS2: Tony Hawk's Pro Skater 2
- THPS2X: Tony Hawk's Pro Skater 2x
- MH: Mat Hoffman's Pro BMX
- THPS3: Tony Hawk's Pro Skater 3 (PlayStation / N64)
- SDH: Sea-Doo Hydrocross (PlayStation)
- THPS4: Tony Hawk's Pro Skater 4 (PlayStation)


## Known formats

### DDX: extract-ddx.py (THPS2X-Xbox)

Extracts THPS2X DDX files (Texture collections).

### DDM: disassemble-ddm.py (THPS2X-Xbox)

Make THPS2X DDM files (Material collections) human-readable.

### TRG: disassemble-trg.py (THPS1 / THPS2 / SM)

Make THPS2 TRG files (Scripts / Commands and level meta-data) human-readable.

A lot of this is based on SYMBOLS.TDF, which is included in THPS2 (Windows).

### PRK: disassemble-prk.py (THPS2 / THPS2X)

Disassembles THPS2 PKR files (User created skatepark).

### PKR: extract-pkr.py (?)

Extracts PKR file.

### PSX: psxviewer.c (THPS1 / THPS2 / SM)

Viewer for PSX files.

Stolen from https://gist.github.com/iamgreaser/2a67f7473d9c48a70946018b73fa1e40


## Unknown formats

There's additional file formats which are commonly found in THPS2:

- BON (THPS2X-Xbox) = Likely mesh and texture for characters.
- REC (THPS2-Windows) = Replay files
- THPS2 CRETEX.BIN = A list of items for skater editor.
- THPS2 PRE = Container format for small files, assembled from S files
- THPS2 PSX = Level files (psxviewer.c exists, but Blender 2.80 importer would be good)
- THPS2 FNT = Font glyph map
- THPS2 CD.HET/CD.HEP = List of files on CD
- THPS2 CD.HED/CD.WAD = Container for files on CD
- THPS2 SBL = Some debug symbols
- THPS2 SFX = Some sound-effect list
- THPS2 TS = Trick list



## Other formats

### STR

PlayStation STR video file format. See https://github.com/m35/jpsxdec/blob/readme/jpsxdec/PlayStation1_STR_format.txt

### SFX.VAB (THPS1!-PlayStation)

PlayStation VAB audio file format.

### CT.PAL (THPS1!-PlayStation)

Microsoft RIFF Palette.

### title_h.zlb (THPS1!-PlayStation)

`gunzip` to extract BMR image; 640x480, 16 bit per pixel little-endian grayscale.

### BMR (THPS1!-PlayStation)

Raw image files, 16 bit per pixel, with 8 byte zero-footer.
Typically 640x480, or 512x240.

### SYMBOLS.TDF (THPS2-Windows)

This was likely assembled from a SYMBOLS.S (using a tool called stotdf.exe)

### PSH (THPS2-Windows)

Header files

### S

Assembler directives. The following files are named in other files, or exist.
The assembler was either something custom, or common.
Possibly different tools were used for different tasks.

#### SCRIPT.S

This uses another tool to handle S files.

### BMP (THPS2-Windows)

Windows Bitmap.

### DDS (THPS2X-Xbox)

DirectDraw Surface file.

### WAV (THPS2-Windows)

RIFF file format for audio.
Windows version uses: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 44100 Hz.

### TXT

Most of these are left-overs from debugging / development.

However, there's some additional files which the game potentially uses.

#### CDPARKS.TXT

List of user created parks that are included with the game.


## Further reading

* [Hex Editing Created Parks (THPS2)](http://webcache.googleusercontent.com/search?q=cache:uUdAddR8ZGoJ:planettonyhawk.gamespy.com/Viewf0fe.php)
* [Mick West Blog article: Practical Hash IDs (Used in Tony Hawk engine)](http://cowboyprogramming.com/2007/01/04/practical-hash-ids/)
* [Mick West Blog article: Evolve Your Hierarchy (Used in later Tony Hawk games; also describes earlier games)](http://cowboyprogramming.com/2007/01/05/evolve-your-heirachy/)
* [THPS blender importer/exporter (io_thps_scene)](https://github.com/denetii/io_thps_scene)
* [PSX file format documentation](https://gist.github.com/iamgreaser/b54531e41d77b69d7d13391deb0ac6a5)
* [List of all bruteforced filenames in THPS1 (PlayStation)](https://gist.github.com/iamgreaser/ee48ac4adb0a18fc8928eb8494703730)
* [spidey-tools](https://github.com/krystalgamer/spidey-tools)

