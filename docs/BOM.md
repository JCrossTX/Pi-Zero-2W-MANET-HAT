# Bill of Materials (preliminary)

Quantities for one HAT. MPNs are *candidates / starting points* — confirm
availability, footprint, and the electrical notes in [`POWER.md`](POWER.md) /
[`RF.md`](RF.md) before ordering.

## Core / functional

| Ref | Qty | Part | MPN (candidate) | Notes |
|-----|----:|------|-----------------|-------|
| U1  | 1 | Wi-Fi HaLow SoC / module | Morse Micro **MM8108** (SoC) or MM8108-based module | SPI host iface; configured for **external FEM**. Prefer a module if it breaks out the ext-FEM RF + control (see DECISIONS) |
| U2  | 1 | 900 MHz PA/LNA front-end | EBYTE **E21-900G30S** | 30 dBm, 850–931 MHz, built-in LNA + T/R; stamp-hole, 27.5×18 mm |
| U3  | 1 | GNSS receiver | u-blox **NEO-M9N-00B** | UART+I²C+PPS; 12.2×16.0 mm |
| U4  | 1 | Buck-boost regulator | TI **TPS63802** (or TPS63070) | 5 V→VPA (~5.0 V), ≤2 A |
| U5  | 1 | 3V3 regulator | TI **TLV62569** buck (or **AP2112-3.3** LDO) | radio + GNSS digital |
| U6  | 1 | HAT ID EEPROM | **24AA32A / CAT24C32** (I²C, WP) | ID_SD/ID_SC, per HAT spec |
| U7  | 0–1 | T/R interlock logic (optional) | single-gate (e.g. SN74LVC1G) | enforce no TXEN+RXEN both-high |

## RF / antenna

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| J2, J3 | 2 | **U.FL / IPEX SMT** receptacle | #1 GNSS, #2 900 MHz |
| C34, C35, C44 | 3 | 100 pF RF DC-block | series in RF paths |
| RN1 (R30–R32) | 0–3 | π-pad attenuator (0402) | DNP default; set MM8108→E21 drive (B3) |
| D30 | 0–1 | low-C RF ESD clamp | at U.FL #2 |
| FL1 | 0–1 | GNSS SAW/bandpass filter | add if PA leakage desenses GNSS |
| L40, R44 | 0–2 | bias inductor (27–68 nH) + 10 Ω | active GNSS antenna via VCC_RF |
| — | — | 50 Ω matching (TBD) | per MM8108 ref design + E21 ports |

## Connectors / power

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| J1  | 1 | **2×20 (40-pin) female header**, 2.54 mm | mates to Pi Zero 2 W; std or stacking height (see MECHANICAL) |
| C7/C30 | 1–2 | 100–220 µF low-ESR | VPA bulk for TX bursts |
| L1 | 1 | 1.0 µH buck-boost inductor | per TPS63802 datasheet |
| L2 | 0–1 | 2.2 µH buck inductor | if U5 is a buck |
| FB1 | 1 | ferrite ~600 Ω@100 MHz | +3V3 → +3V3_GNSS |
| R10–R14, R20–R52 | many | 0402 1% | FB dividers, SPI term, pulls, pulldowns |
| C1–C50 | many | 0402/0603 + bulk | decoupling per docs/SCHEMATIC.md |
| D1 | 0–1 | SMAJ5.0A TVS | 5 V input protection |
| JP1 | 1 | EEPROM WP jumper | default = write-protected |

## Mechanical

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| — | 4 | M2.5 standoff + screw set | matches Pi Zero 2 W hole pattern |
| — | as req | spacers / taller header | if bottom-side clearance is tight |

## Notable open BOM decisions (see [`DECISIONS.md`](DECISIONS.md))
1. **MM8108 bare SoC vs. module** — drives most of the schematic/layout effort and
   whether the external-FEM RF path is even accessible.
2. **VPA voltage** (3.3 V vs 5.0 V) — set per the E21 datasheet revision; fixes the
   buck-boost feedback divider.
3. **MM8108→E21 attenuator pad** — value depends on measured ext-FEM drive level.
4. **GNSS pre-filter** — populate only if coexistence testing requires it.
