# Mechanical: Outline, Mounting, Placement & Clearances

## 1. Board outline

- **Perimeter: 65.0 × 30.0 mm** — identical to the Raspberry Pi Zero 2 W.
- Corner radius **3.0 mm** (matches the Pi Zero outline).
- 2-layer minimum recommended; **4-layer** preferred for clean 50 Ω RF + a solid
  ground plane (strongly advised given the 1 W PA + GNSS coexistence). See
  [`POWER.md`](POWER.md)/[`RF.md`](RF.md).

Origin convention used in the KiCad scaffold: **(0,0) = top-left**, X right, Y
down (KiCad screen convention).

## 2. Mounting holes

Same 4-hole pattern as the Pi Zero 2 W:

| Hole | Center (X, Y) mm |
|------|------------------|
| H1 | (3.5, 3.5) |
| H2 | (61.5, 3.5) |
| H3 | (3.5, 26.5) |
| H4 | (61.5, 26.5) |

- Hole Ø **2.75 mm** (M2.5 clearance), spacing **58.0 × 23.0 mm**, **3.5 mm**
  from each edge. Non-plated. Keep copper/components ~6 mm keepout (M2.5 standoff
  pad).

## 3. 40-pin header

- 2×20, **2.54 mm** pitch, **female**, running along the long (65 mm) edge to mate
  with the Pi Zero 2 W male header.
- Header body ≈ **50.8 × 5.0 mm**; pin field 2×20 spans 48.26 mm (pin1→pin39).
- **Exact placement must equal the Pi Zero 2 W header position** so it mates — take
  it from the official Raspberry Pi Zero 2 W mechanical DXF. The scaffold marks a
  **nominal** keepout (centered along X, row centerline 3.5 mm from the top long
  edge) flagged `VERIFY` on the silkscreen; replace with the DXF-exact location
  when the real connector footprint is placed.

## 4. Two-sided placement plan

The board is *small* and the E21 module alone is ~27.5 × 18 mm, so both sides are
used. **Top** = the side facing away from the Pi; **Bottom** = the side facing the
Pi (clearance-limited).

### Top side (away from Pi — no clearance limit)
- **40-pin female header** along the top long edge (mounts through; body on top,
  receptacle mates downward onto the Pi).
- **E21-900G30S** PA module (largest part) — gets the most area; near U.FL #2.
- **NEO-M9N** GNSS — opposite end from the PA for isolation; near U.FL #1.
- **U.FL #1 (GNSS)** and **U.FL #2 (900 MHz)** at **opposite board edges**.

### Bottom side (faces the Pi — keep low-profile, avoid Pi tall parts)
- **MM8108** + RF matching (low BGA, fits the gap).
- **Buck-boost** + **3V3 regulator** + bulk caps (keep switch node away from RF).
- **ID EEPROM** and small passives.

> **Bottom-side clearance:** with a standard 2×20 female header the HAT-to-Pi gap
> is only a couple of mm. Bottom components must be **low-profile** and must avoid
> the Pi Zero 2 W's taller features and connectors:
> - mini-HDMI and the two micro-USB (PWR / USB) connectors on one long edge,
> - the microSD card holder (overhangs an end),
> - the CSI camera FPC connector,
> - the RF shield can over the SoC/Wi-Fi.
>
> Map these against the Pi Zero 2 W mechanical drawing and add **keepout zones**
> on the HAT bottom before placing parts. If clearance is too tight, raise the HAT
> with a **taller stacking header / spacer** (and longer standoffs).

```
  TOP (away from Pi)                          BOTTOM (faces Pi)
  +------------------------------------+      +------------------------------------+
  | [====== 40-pin female header =====]|      |  (header receptacle protrudes)     |
  |                                    |      |                                    |
  | U.FL#1   [ NEO-M9N ]      [ E21  ] |      |  [buck-boost] [3V3]   [ MM8108 ]   |
  | (GNSS)                    [ PA   ] |      |  [bulk caps]          [RF match]   |
  |                          U.FL#2    |      |  [EEPROM]   (keepouts: HDMI/USB/   |
  | o H3                       H4 o    |      |   o          SD/camera/RF-can)  o  |
  +------------------------------------+      +------------------------------------+
   (silkscreen placement zones only — see KiCad scaffold)
```

## 5. Antenna access
- Both U.FL connectors face the board edge so pigtails (U.FL→SMA/RP-SMA bulkhead,
  or direct U.FL antennas) route out without crossing the other RF section.

## 6. KiCad scaffold mechanical content
`hardware/kicad/PiZero2W-MANET-HAT.kicad_pcb` contains, as a real openable board:
- the 65 × 30 mm rounded-rect **Edge.Cuts** outline,
- the 4 **mounting holes** (NPTH, Ø2.75),
- silkscreen **placement-zone** labels and the **header keepout** (flagged VERIFY).

It deliberately has **no component footprints yet** — add real footprints over
these zones during implementation.
