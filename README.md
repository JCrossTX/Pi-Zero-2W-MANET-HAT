# Pi-Zero-2W-MANET-HAT

A long-range **MANET (Mobile Ad-hoc Network) HAT** for the **Raspberry Pi Zero 2 W**.

The board adds a sub-GHz Wi-Fi HaLow (802.11ah) mesh radio (high-power, integrated
PA) plus a precision GNSS receiver for position/time, all on a board the same
perimeter (65 × 30 mm) as the Pi Zero 2 W and powered from the 40-pin header.

## Function block summary

| Block            | Part                  | Host interface (40-pin)            | Antenna        |
|------------------|-----------------------|------------------------------------|----------------|
| HaLow radio (primary) | Morse Micro **MM8108-M20** (integ. PA, ~28.5 dBm, cert) | **SPI0** + IRQ/RESET/wake | **U.FL #2 (900 MHz)** |
| HaLow radio (fallback) | Morse Micro **MM8108-MF15457** (~27 dBm) | **SPI0** + IRQ/RESET/wake | **U.FL #2 (900 MHz)** |
| GNSS             | u-blox **NEO-M9N**    | **UART0** + **PPS** (I²C alternate)| **U.FL #1 (GNSS)** |
| Power            | 3V3 buck from header **5 V** (no PA rail) | —                | —              |
| HAT ID           | 24Cxx EEPROM          | **ID_SD / ID_SC** (pins 27/28)     | —              |

> **One radio site, two module options** (see [`docs/DECISIONS.md`](docs/DECISIONS.md) §C
> and [`docs/MODULE_OPTIONS.md`](docs/MODULE_OPTIONS.md)). **Primary = MM8108-M20**:
> Morse's new high-power module with an **integrated 28.5 dBm PA + 902–928 SAW,
> FCC/IC certified** — same range as a +30 dBm external PA with none of the
> integration/cert pain. **Fallback = MM8108-MF15457** (~27 dBm, OpenMANET-ready
> today) keeps the board buildable while the M20 datasheet/sourcing land. The
> earlier **external E21 1 W PA path is retired** — both modules drive the antenna
> directly, so there's no buck-boost, no T/R control, and no +30 dBm recert.
> M20-US is **902–928 MHz (US/Canada)**.

> **OpenMANET-compatible.** The MM8108 SPI + control GPIOs match the OpenMANET
> Pi Zero 2 W SPI firmware variant (CS0=GPIO8, RESET=GPIO17, power=GPIO23/24,
> IRQ=GPIO5, SPI0 @ 20 MHz, `morse,mm610x-spi`), so OpenMANET runs unchanged on the
> **MF15457 fallback** — just add this board's device-tree overlay. The **M20** is
> the same MM8108 SPI stack but needs its own **BCF** (OpenMANET M20 support TBD).
> See [`firmware/openmanet/`](firmware/openmanet/).

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
  RF.md               RF chain, matching, antennas
  MECHANICAL.md       Outline, mounting holes, two-sided placement, clearances
  BOM.md              Bill of materials (MPNs); M20 primary / MF15457 fallback
  COMPONENTS_GAP.md   Datasheet-grounded gap analysis (what else the PCB needs)
  MODULE_OPTIONS.md   MF15457 vs MF15457+E21 vs MM8108-M20 comparison
  LINK_BUDGET.md      Range & throughput by TX power / data rate
  FIRMWARE_PA.md      OpenMANET/Morse firmware + BCF notes
  BRINGUP.md          Stage-gated power-on & test plan
  DECISIONS.md        Design decision log + open risks + radio options
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
against vendor datasheets (notably the **MM8108-M20** pinout/power, pending its
datasheet — the MF15457 fallback is fully specified and buildable today).

## Key external references

- Raspberry Pi Zero 2 W test pads / mechanical: <https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-test-pads.pdf>
- Morse Micro MM8108 SoC: <https://www.morsemicro.com/chips/>
- EBYTE E21-900G30S: <https://www.cdebyte.com/products/E21-900G30S>
- u-blox NEO-M9N: <https://www.u-blox.com/en/product/neo-m9n-module>
