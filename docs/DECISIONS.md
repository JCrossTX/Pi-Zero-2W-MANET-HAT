# Design Decisions & Open Risks

## A. Decisions made (with rationale)

### A1. No external USB-A port — **dropped**
The original spec called for a USB-A 3.0 female host port "supplied by the 40-pin
header." This is **not physically achievable** for a top-mounted, removable,
non-soldered HAT:
- The Pi Zero 2 W's 40-pin header carries **no USB** at all.
- Its only USB is a **single USB 2.0** OTG link, exposed on **bottom-side test
  pads PP22 (D−) / PP23 (D+)** beside the micro-USB "USB" port.
- A HAT on **top** cannot reach bottom-side pads with downward pogo pins (those
  only work for a board mounted *under* the Pi, e.g. UUGear Zero4U).
- (Also note: a USB-A *3.0* connector would still only run at USB **2.0** speed,
  since the Pi has no SuperSpeed.)

Rejected alternatives and why:
- **Micro-USB U-cable jumper** Pi "USB" port → HAT: works and is removable, but
  adds an external cable.
- **Bottom pogo interposer**: sandwiches the Pi, fiddly alignment.
- **Edge-wrap pogo/flex**: fragile.

**Decision (user):** drop the external USB-A port entirely. Frees significant area
on the 65 × 30 mm board and removes the only soldered/cabled-to-Pi dependency.

### A2. MM8108 host interface = **SPI**
Of the MM8108's USB 2.0 / SDIO 2.0 / SPI options, only **SPI** is available on the
Pi's 40-pin header (SDIO is used by the SD card + onboard Wi-Fi; USB is not on the
header). Accepted trade-off: SPI caps throughput below HaLow's max raw rate, but
it needs no hub/cable and keeps the HAT a single top board.

### A3. PA powered by **buck-boost from header 5 V** — **superseded (see B11)**
Was required for the external E21 PA's 5 V rail. The **MM8108-M20** integrates the
PA at the module supply, and the **MF15457 fallback** has no external PA, so the
5 V buck-boost (`U4`/`VPA`) is **removed** from the active design. The header still
feeds the 3V3 buck through the inrush switch. See [`POWER.md`](POWER.md).

### A4. GNSS on **UART + PPS** (I²C alternate)
UART0 for NMEA/UBX + a GPIO for 1 PPS time sync; I²C kept available (UART+I²C
coexist on the NEO-M9N; SPI mode would disable I²C, so SPI was not chosen for the
GNSS).

### A5. Deliverable = **design package + KiCad scaffold (KiCad 10 format)**
Engineer-ready docs plus a **KiCad 10** project (`kicad_sch` v20260306,
`kicad_pcb` v20260206, `generator_version "10.0"`) with correct mechanical
outline, mounting holes, placement zones, and a hierarchical schematic skeleton
with named nets — not a finished/routed board.

### A6. **OpenMANET SPI firmware compatibility**
The MM8108 SPI lines and control GPIOs match the OpenMANET Pi Zero 2 W SPI
variant exactly (**CS0=GPIO8, RESET=GPIO17, power=GPIO23/24, IRQ=GPIO5, SPI0 @
20 MHz, `morse,mm610x-spi`**) so OpenMANET firmware runs with no changes — only
this board's device-tree overlay is added. This applies to the **MF15457
fallback** today; the **MM8108-M20** is the same MM8108 SPI stack but needs its own
**BCF** (and OpenMANET M20 support, TBD — B11). See
[`../firmware/openmanet/README.md`](../firmware/openmanet/README.md).
> Confirm the kernel `compatible` string of the *specific* OpenMANET build you
> flash (`morse,mm610x-spi` vs an `mm8108`-specific string) and update the overlay
> if needed.

## B. Open risks / must-resolve-before-fab

> **Datasheets now in [`../hardware/`](../hardware/)** (MM8108-MF15457,
> E21-900G30S, NEO-M9N-00B) — several risks below are resolved or refined. Full
> component-by-component status: [`COMPONENTS_GAP.md`](COMPONENTS_GAP.md).

| # | Item | Why it matters | Action |
|---|------|----------------|--------|
| B1 | ~~MM8108 NDA-gated~~ **RESOLVED** | — | Using the **MF15457 module**: self-contained, only VBAT/VBAT_TX/VDDIO 3.0–3.6 V, internal clock, no external SoC inductors/rails, no strict sequencing |
| B11 | **Radio = MM8108-M20 primary, MF15457 fallback** — RESOLVED (direction) | M20 = certified, integrated 28.5 dBm PA + SAW; ~same range as the old +30 dBm E21 plan with none of the integration/cert pain. Sourcing is *uncertain* (sampling to certified partners), so MF15457 keeps the board buildable today | **Retire the external E21** (and its VPA/LPF/T-R/bypass). Same radio site + SPI nets accept either module. **Gating:** M20 datasheet (pinout/power/footprint), sourcing, OpenMANET M20 BCF. See [`MODULE_OPTIONS.md`](MODULE_OPTIONS.md), §C |
| ~~B2–B5, B10~~ | **External-E21 issues — RETIRED** | All were E21-specific (FEM tap, drive pad, VPA 5 V, T/R control, DNP-optional) | Dropped with B11; the integrated/fallback modules need none of them |
| B6 | 900 MHz radio ↔ GNSS coexistence | ~27–28.5 dBm beside a GNSS RX on 65×30 mm | Opposite-end U.FL, ground fencing, **RF shield cans**, optional GNSS pre-filter; validate C/N₀ with radio keyed |
| B7 | Bottom-side clearance to Pi | Pi connectors/SD/camera/RF-can | Build keepouts from the Pi Zero 2 W DXF; taller header/standoffs if needed |
| B8 | Header position exactness | Must mate with Pi Zero 2 W | Place real 2×20 footprint at DXF-exact location (scaffold = nominal `VERIFY`) |
| B9 | Upstream 5 V capacity + inrush | Radio+Pi current; bulk-cap inrush can brown out the Pi | Spec ≥3 A supply; **soft-start load switch** on +5 V. M20 is FCC/IC certified (cert burden largely removed vs the old +30 dBm recert) |
| B12 | **M20 datasheet unknowns** | Pinout, supply rails/current, exact footprint, SPI control lines all TBD until Morse publishes | Hold the M20 radio schematic at placeholder; keep MF15457 pin-level detail as the buildable baseline; finalize M20 on datasheet |

## C. Radio build options (one radio site, two module choices)

The external E21 PA path is **retired**. The board carries **one HaLow radio site**
fed by the same SPI/control nets; either module populates it. Full comparison:
[`MODULE_OPTIONS.md`](MODULE_OPTIONS.md).

| | **Primary — MM8108-M20** | **Fallback — MM8108-MF15457** |
|--|--------------------------|-------------------------------|
| TX power | **~28.5 dBm** (integrated PA) | **~27 dBm** (OpenMANET BCF) |
| PA / filter | integrated PA + 902–928 SAW | module internal PA |
| Certification | **FCC/IC certified** | module modular cert |
| Host | SPI (also SDIO/USB) | SPI |
| Firmware | needs **M20 BCF** (OpenMANET TBD) | **OpenMANET today** (`bcf_mf15457`) |
| Size | 18.5 × 14 mm | MF15457 footprint |
| Extra rails | none (PA at module rail) — **TBD** | none |
| Availability | **sampling, partners only** | available now |
| Status | **design target**; pinout/power TBD (B12) | **buildable baseline now** |

Why this split: M20 gets ~the same range as the old +30 dBm E21 plan as a single
certified part — no buck-boost, no LPF, no T/R-control problem, no recert, smaller
board. But sourcing is uncertain and there's no datasheet yet, so **MF15457 stays
the build-today baseline** and the M20 drops into the same site once it lands.
Region note: M20-US is **902–928 only** (fine for the US/Canada MANET target).

## D. Suggested implementation order
1. **B11/B12:** lay out the radio site + SPI/control nets so either module fits;
   build to **MF15457** (buildable today) as the baseline.
2. Finalize 3V3 power + radio + GNSS + RTC (no VPA / buck-boost anymore).
3. Draw schematics over the scaffold sheets; pull real symbols/footprints.
4. Place to the [`MECHANICAL.md`](MECHANICAL.md) two-sided plan; build Pi keepouts.
   The retired E21/VPA frees board area.
5. Route 50 Ω RF (radio ANT → U.FL), then power, then digital.
6. When the **M20 datasheet** publishes: finalize its footprint/power, confirm
   sourcing + OpenMANET M20 BCF, then swap it into the radio site.
