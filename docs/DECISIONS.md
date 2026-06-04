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

### A3. PA powered by **buck-boost from header 5 V**
Per spec. Holds the PA rail regulated through the 5 V sag caused by TX current
bursts. See [`POWER.md`](POWER.md).

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
this board's device-tree overlay is added. The board-specific addition (external
E21 PA front-end) is transparent to the SPI/control interface; see risks B2/B3/B5
and [`../firmware/openmanet/README.md`](../firmware/openmanet/README.md).
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
| B2 | **Module has integrated PA + single ANT, no FEM tap** | The external E21 cannot tap a pre-PA RF port; it must cascade off the module's +22…+25.5 dBm ANT output | Cascade module ANT → pad → E21 `PIN`; accept ~+5–8 dB net system gain; **recertify** end product at +30 dBm |
| B3 | **MM8108 → E21 drive level** — refined | Module +22…+25.5 dBm vs E21 +20 dBm target | Add a **fixed ~3–5 dB pad** (RN1) at E21 `PIN`; confirm against hottest BW/MCS so E21 input stays ≤ spec |
| B4 | **VPA = 5.0 V** — RESOLVED | E21 needs 4.75–5.25 V, ~620 mA TX | Buck-boost output = **5.0 V**; bulk for the 620 mA burst |
| B5 | **E21 T/R control — only via custom BCF; not turnkey on MF15457** | Function of chip GPIOs is set by Morse **BCF**/firmware; mapping the internal TXRX switch to a GPIO is **not a shipping feature** on MF15457 (Morse planned a separate ext-FEM variant), and a builder hit a low-RX-rate issue with MM8108+ext-PA. See [`FIRMWARE_PA.md`](FIRMWARE_PA.md). | Requires a **custom BCF** exposing a FEM/TXRX GPIO → E21 TX_EN/RX_EN; RF-sense auto-T/R as fallback; Pi GPIO bring-up only. **Also weigh dropping the PA** (B10) |
| B10 | **PA value vs OpenMANET's ~27 dBm BCF** | OpenMANET's BCF already yields ~27 dBm from the bare module; E21 adds only ~3 dB for big cost (T/R support risk, RX-rate gotcha, ~620 mA+heat, area, recert) | **Decision pending** — keep / drop / make E21 DNP-optional (see chat) |
| B6 | 900 MHz PA ↔ GNSS coexistence | +30 dBm beside a GNSS RX on 65×30 mm | Opposite-end U.FL, ground fencing, **RF shield cans**, optional GNSS pre-filter; validate C/N₀ with PA keyed |
| B7 | Bottom-side clearance to Pi | Pi connectors/SD/camera/RF-can | Build keepouts from the Pi Zero 2 W DXF; taller header/standoffs if needed |
| B8 | Header position exactness | Must mate with Pi Zero 2 W | Place real 2×20 footprint at DXF-exact location (scaffold = nominal `VERIFY`) |
| B9 | Upstream 5 V capacity, **cert**, inrush | PA+module+Pi current; +30 dBm power/duty limits; bulk-cap inrush can brown out the Pi | Spec ≥3 A supply; **soft-start load switch** on +5 V; **recertify** end product (FCC 15.247 / ETSI EN 300 220) |

## C. Suggested implementation order
1. Resolve **B1/B2** (MM8108 SoC-vs-module + ext-FEM) — gates the whole schematic.
2. Lock **VPA (B4)** and finalize the power schematic.
3. Draw schematics over the scaffold sheets; pull real symbols/footprints.
4. Place to the [`MECHANICAL.md`](MECHANICAL.md) two-sided plan; build Pi keepouts.
5. Route 50 Ω RF first, then power, then digital; flood ground; fence RF sections.
6. RF bring-up: drive level (**B3**), T/R timing (**B5**), GNSS coexistence (**B6**).
