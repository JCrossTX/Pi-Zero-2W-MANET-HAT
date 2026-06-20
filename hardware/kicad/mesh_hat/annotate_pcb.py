#!/usr/bin/env python3
"""Annotate the placed footprints on the ZERO 2W MESH HAT PCB so that
'Update PCB from Schematic' matches them by reference instead of duplicating.

Assignment is by signal-flow proximity to the anchor ICs (MM8108 / NEO / USB-C).
Confident parts are renamed; genuinely ambiguous / surplus parts are left as REF**
and reported so the user assigns or deletes them deliberately.
"""
import sys, re

SRC = sys.argv[1]
OUT = sys.argv[2]

# (footprint-basename, x, y) -> new refdes      (x,y rounded to 0.1 mm)
MAP = {
    ("Morse_MM8108-MF15457_LGA38_11x10", 153.0, 84.0): "U2",   # LoRa-mesh radio
    ("ublox_NEO-M9N_LCC24_12x16",        117.0, 93.0): "U3",   # GNSS
    ("SOIC-8_3.9x4.9mm_P1.27mm",         128.5, 95.0): "U1",   # ID EEPROM (matches sch U1)
    ("USB_C_Receptacle_GCT_USB4085",     106.85,79.55):"J6",   # USB-C
    ("D_SMA",                            138.5, 79.0): "D1",   # input TVS
    ("L_0402_1005Metric",                108.0, 96.5): "L2",   # GNSS bias inductor
    ("U.FL_Hirose_U.FL-R-SMT-1_Vertical",162.0, 90.0): "J2",   # 900 MHz ant (by MM8108)
    ("U.FL_Hirose_U.FL-R-SMT-1_Vertical",104.0, 90.5): "J3",   # GNSS ant (by NEO)
    ("SOT-23-5",                         111.36,78.95):"U7",   # RT9742 VBUS sw (by USB-C)
    ("SOT-23-5",                         127.86,88.05):"U8",   # TPS3839 supervisor
    ("SOT-23-6",                         111.36,83.05):"U9",   # USBLC6-2 (by USB-C)
    ("SOT-23-6",                         116.86,79.0): "U4",   # AP63200 buck (by inductor)
    ("SOT-23-6",                         116.86,83.05):"U5",   # MIC2007 input switch
    ("SOT-23-6",                         154.5, 92.0): "U6",   # MIC2007 radio-rail sw (by MM8108)
    ("L_Wuerth_MAPI-4020",               125.69,79.5): "L1",   # buck inductor (by U4)
    ("L_0603_1608Metric",                107.5, 93.5): "FB1",  # GNSS-rail ferrite (by NEO)
}
# everything else stays REF** (reported below)

def blocks(s):
    for m in re.finditer(r'\(footprint ', s):
        st = m.start(); depth = 0; j = st; instr = esc = False
        while j < len(s):
            c = s[j]
            if esc: esc = False
            elif c == '\\' and instr: esc = True
            elif c == '"': instr = not instr
            elif not instr:
                if c == '(': depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0: break
            j += 1
        yield st, j + 1

def main():
    s = open(SRC).read()
    spans = list(blocks(s))
    out = []; prev = 0; renamed = []; left = []
    for st, en in spans:
        out.append(s[prev:st])
        blk = s[st:en]
        fp = re.search(r'\(footprint "([^"]+)"', blk).group(1).split(':')[-1]
        at = re.search(r'\(at ([-\d.]+) ([-\d.]+)', blk)
        x, y = round(float(at.group(1)), 2), round(float(at.group(2)), 2)
        key = next((k for k in MAP if k[0] == fp
                    and abs(k[1]-x) < 0.15 and abs(k[2]-y) < 0.15), None)
        if key:
            newref = MAP[key]
            blk2 = re.sub(r'(\(property "Reference" ")[^"]*(")',
                          lambda m: m.group(1)+newref+m.group(2), blk, count=1)
            out.append(blk2); renamed.append((newref, fp, x, y))
        else:
            out.append(blk)
            if not any(t in fp for t in ("MountingHole", "PinSocket")):
                left.append((fp, x, y))
        prev = en
    out.append(s[prev:])
    open(OUT, "w").write("".join(out))

    print(f"RENAMED {len(renamed)}:")
    for r, fp, x, y in sorted(renamed):
        print(f"   {r:4} <- {fp[:34]:35} ({x},{y})")
    print(f"\nLEFT as REF** (assign or delete) {len(left)}:")
    for fp, x, y in left:
        print(f"        {fp[:34]:35} ({x},{y})")

if __name__ == "__main__":
    main()
