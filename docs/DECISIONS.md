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

| # | Item | Why it matters | Action |
|---|------|----------------|--------|
| B1 | **MM8108 detailed design is NDA-gated** | Exact pinout, power sequencing, crystal, and RF reference are needed for a real schematic | Get the Morse Micro reference design / module datasheet under NDA; **strongly consider a pre-certified MM8108 module** that breaks out the external-FEM RF path + control |
| B2 | **External-FEM RF path availability** | The E21 PA is only useful if the MM8108 RF can bypass its internal PA into an external FEM. A module that only exposes a post-internal-PA antenna port can't drive the E21 cleanly | Confirm the chosen MM8108 variant supports/breaks out external FEM; if not, reconsider PA topology |
| B3 | **MM8108 → E21 drive level** | Over-driving the E21 RFI saturates/can damage the PA; under-driving loses power | Measure MM8108 ext-FEM TX output; add a fixed **attenuator pad** to land in the E21 linear input window |
| B4 | **E21 VCC / VPA voltage** | Sets buck-boost FB divider and current budget | Read the *current* E21-900G30S datasheet (3.0–5.5 V, ~5.0 V rec.); set VPA accordingly |
| B5 | **FEM T/R timing source** | Pi GPIO is too slow for per-burst T/R; both-high is illegal | Drive E21 TXEN/RXEN from MM8108 FEM-control outputs; add interlock/pulldowns; Pi-GPIO fallback links are DNP |
| B6 | **900 MHz PA ↔ GNSS coexistence** | +30 dBm next to a GNSS RX on a tiny board can desense it | Opposite-end U.FL, ground fencing, optional GNSS pre-filter; validate C/N₀ with PA keyed |
| B7 | **Bottom-side clearance to Pi** | Pi connectors / SD / camera FPC / RF can limit bottom components | Build keepouts from the Pi Zero 2 W DXF; use taller header/standoffs if needed |
| B8 | **Header position exactness** | Must match Pi Zero 2 W to mate | Place the real 2×20 footprint at the DXF-exact location (scaffold marks nominal `VERIFY`) |
| B9 | **Upstream 5 V capacity & regulatory** | PA + Pi can need ≥3 A; 1 W EIRP is power/duty-limited | Spec ≥3 A supply; confirm FCC Part 15.247 / ETSI EN 300 220 compliance for region |

## C. Suggested implementation order
1. Resolve **B1/B2** (MM8108 SoC-vs-module + ext-FEM) — gates the whole schematic.
2. Lock **VPA (B4)** and finalize the power schematic.
3. Draw schematics over the scaffold sheets; pull real symbols/footprints.
4. Place to the [`MECHANICAL.md`](MECHANICAL.md) two-sided plan; build Pi keepouts.
5. Route 50 Ω RF first, then power, then digital; flood ground; fence RF sections.
6. RF bring-up: drive level (**B3**), T/R timing (**B5**), GNSS coexistence (**B6**).
