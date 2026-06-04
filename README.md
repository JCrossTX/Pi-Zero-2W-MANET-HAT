# Pi-Zero-2W-MANET-HAT

A long-range **MANET (Mobile Ad-hoc Network) HAT** for the **Raspberry Pi Zero 2 W**.

The board adds a sub-GHz Wi-Fi HaLow (802.11ah) mesh radio with an external 1 W
power amplifier front-end, plus a precision GNSS receiver for position/time, all
on a board the same perimeter (65 × 30 mm) as the Pi Zero 2 W and powered from the
40-pin header.

## Function block summary

| Block            | Part                  | Host interface (40-pin)            | Antenna        |
|------------------|-----------------------|------------------------------------|----------------|
| HaLow radio      | Morse Micro **MM8108**| **SPI0** + IRQ/RESET/wake          | via PA → U.FL  |
| RF front-end (PA/LNA) — **optional Variant B** | EBYTE **E21-900G30S** (1 W) | BCF FEM GPIO (Variant B only) | **U.FL #2 (900 MHz)** |
| GNSS             | u-blox **NEO-M9N**    | **UART0** + **PPS** (I²C alternate)| **U.FL #1 (GNSS)** |
| PA power         | Buck-boost from header **5 V** | —                         | —              |
| HAT ID           | 24Cxx EEPROM          | **ID_SD / ID_SC** (pins 27/28)     | —              |

> **Two build variants on one board** (see [`docs/DECISIONS.md`](docs/DECISIONS.md) §C):
> **Variant A (default)** ships module-only at **~27 dBm** (OpenMANET BCF) — low
> power, certified path, ideal for ground/handheld/vehicle nodes; the E21 PA,
> buck-boost and LPF are **depopulated** and an RF bypass carries the module ANT
> to U.FL #2. **Variant B (optional)** populates the E21 for **+30 dBm** extended
> range (fixed/elevated LoS nodes) — needs custom-BCF T/R control + recert. The
> ~3 dB only buys ~20 % range in NLOS, so it's off by default
> ([`docs/LINK_BUDGET.md`](docs/LINK_BUDGET.md)).

> **OpenMANET-compatible.** The MM8108 SPI + control GPIOs match the OpenMANET
> Pi Zero 2 W SPI firmware variant (CS0=GPIO8, RESET=GPIO17, power=GPIO23/24,
> IRQ=GPIO5, SPI0 @ 20 MHz, `morse,mm610x-spi`), so OpenMANET runs unchanged —
> just add this board's device-tree overlay. See
> [`firmware/openmanet/`](firmware/openmanet/).

> **No external USB-A port.** The original USB-A 3.0 requirement was dropped:
> the Pi Zero 2 W exposes **no USB on the 40-pin header**, and its only USB (a
> single **USB 2.0** OTG link) is on **bottom-side test pads (PP22/PP23)** that a
> *top-mounted, non-soldered, removable* HAT cannot reach. See
> [`docs/DECISIONS.md`](docs/DECISIONS.md) for the full rationale and the
> rejected alternatives.

## Repository layout

```
docs/                 Engineer-ready design package
  DESIGN.md           Architecture + block diagram
  INTERFACES.md       40-pin header pin map + signal assignments
  SCHEMATIC.md        Component-level subcircuits (refdes + values + nets)
  POWER.md            Power tree, budget, regulator selection, decoupling
  RF.md               RF chain, FEM switching, matching, antennas
  MECHANICAL.md       Outline, mounting holes, two-sided placement, clearances
  BOM.md              Bill of materials (MPNs) + Variant A/B builds
  COMPONENTS_GAP.md   Datasheet-grounded gap analysis (what else the PCB needs)
  LINK_BUDGET.md      Range & throughput: module-only vs +E21
  FIRMWARE_PA.md      OpenMANET/Morse firmware external-PA findings
  BRINGUP.md          Stage-gated power-on & test plan
  DECISIONS.md        Design decision log + open risks + Variant A/B
hardware/             Vendor datasheets (MM8108-MF15457, E21, NEO-M9N)
hardware/
  kicad/              KiCad 10 project scaffold (project, board outline, sheets)
  netlist/            connections.csv — human/tool-readable net list
firmware/
  openmanet/          Device-tree overlay matching OpenMANET's SPI pinout
```

## Status

This is a **design package + KiCad scaffold**, not a finished board. The KiCad
project carries the correct mechanical outline, mounting holes, placement zones,
and a hierarchical schematic skeleton with named nets. Real component symbols,
footprints, RF matching values, and routing are the next implementation step —
see [`docs/DECISIONS.md`](docs/DECISIONS.md) for the items that must be resolved
against vendor datasheets (several MM8108 details are NDA-gated).

## Key external references

- Raspberry Pi Zero 2 W test pads / mechanical: <https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-test-pads.pdf>
- Morse Micro MM8108 SoC: <https://www.morsemicro.com/chips/>
- EBYTE E21-900G30S: <https://www.cdebyte.com/products/E21-900G30S>
- u-blox NEO-M9N: <https://www.u-blox.com/en/product/neo-m9n-module>
