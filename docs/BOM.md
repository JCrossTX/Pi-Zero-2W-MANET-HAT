# Bill of Materials (preliminary)

> **Two build variants on one PCB** ([`DECISIONS.md`](DECISIONS.md) §C):
> **Variant A (default)** = module-only ~27 dBm, low power — depopulates the E21,
> buck-boost, LPF, drive pad and fits the `C_BYP` RF bypass. **Variant B
> (optional, extended-range)** = +30 dBm — populates those and removes `C_BYP`.
> Rows below tagged *Variant B / DNP default* ship unpopulated on the standard board.


Quantities for one HAT. MPNs are *candidates / starting points* — confirm
availability, footprint, and the electrical notes in [`POWER.md`](POWER.md) /
[`RF.md`](RF.md) before ordering.

## Core / functional

| Ref | Qty | Part | MPN (candidate) | Notes |
|-----|----:|------|-----------------|-------|
| U1  | 1 | Wi-Fi HaLow module | Morse Micro **MM8108-MF15457** | 38-pin, self-contained (internal clock+PMU+PA), SPI host; VBAT/VBAT_TX/VDDIO 3.0–3.6 V; single ANT pin |
| U2  | 1 | 900 MHz PA/LNA front-end | EBYTE **E21-900G30S** | **Variant B / DNP default.** 30 dBm, VCC **5.0 V**, ~620 mA TX, +20 dBm in→+30 dBm out; pin6=PIN, pin9=ANT |
| U3  | 1 | GNSS receiver | u-blox **NEO-M9N-00B** | VCC 2.7–3.6 V; UART+I²C+PPS; VCC_RF for active ant; 12.2×16.0 mm |
| U4  | 1 | Buck-boost regulator | TI **TPS63802** (or TPS63070) | **Variant B / DNP default.** 5 V→VPA = **5.0 V**, ≥1 A (E21 ~620 mA) |
| U5  | 1 | 3V3 regulator | TI **TLV62569** buck (or **AP2112-3.3** LDO) | module + GNSS + RTC digital |
| U6  | 1 | HAT ID EEPROM | **24AA32A / CAT24C32** (I²C, WP) | ID_SD/ID_SC, VCC = Pi 3V3 |
| U10 | 1 | Inrush soft-start load switch | TI **TPS22965** | +5V → buck-boost in; tames VPA-bulk inrush (N4) |
| U11 | 1 | Voltage supervisor | TI **TPS3839** (3.3 V) | gates module RESET_N (N5) |
| U12 | 1 | Radio-rail load switch | TI **TPS22918 / TPS22965** | EN = MM_PWR1 (GPIO23); OpenMANET power-gpios (N6) |
| U13 | 1 | I²C RTC | Micro Crystal **RV-3028-C7** (alt **DS3231M**) | addr 0x52, 45 nA, **trickle charger** |
| U8/U9 | 0 | Auto-T/R detector + comparator (DNP) | **LTC5564/ADL6010** + comparator | only if FW can't drive PA T/R (N4b) |

## RF / antenna

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| J2, J3 | 2 | **U.FL / IPEX SMT** receptacle | #1 GNSS, #2 900 MHz |
| C_BYP | 1 | 50 Ω RF bypass (series cap / RF jumper) | **Variant A default:** module ANT → U.FL #2, skipping the DNP E21 |
| FL2, RN1 | — | LPF + drive pad | **Variant B only** (see core table) |
| C34, C35, C44 | 3 | 100 pF RF DC-block | series in RF paths |
| RN1 (R30–R32) | 0–3 | π-pad attenuator (0402) | DNP default; set MM8108→E21 drive (B3) |
| D30 | 0–1 | low-C RF ESD clamp | at U.FL #2 |
| FL2 | 0–1 | 900 MHz LPF / 915 MHz ceramic BPF | E21 ANT → U.FL #2; +30 dBm harmonic compliance (N3) |
| D8 | 1 | low-C TVS (GNSS U.FL) | ESD on RF_GNSS (N8) |
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

## Power-management / indicators / RTC

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| BT1 | 1 | **Seiko MS621FE** (or Panasonic ML414H/ML621) rechargeable, solder-tab | RTC backup, trickle-charged from +3V3 (PCB-soldered) |
| D_PWR/D_TX/D_FIX | 3 | LEDs (green/red/green) + R70–R72 1 kΩ | power-good / PA-TX / GNSS-fix |
| RN1 (R30–R32) | 0–3 | π-pad attenuator (~3–5 dB) | module ANT → E21 PIN drive set |
| R24–R27 | 4 | 10 kΩ | SPI/SDIO bus pull-ups (module note [1]) |
| R33/R34, R60 | 3 | 10 kΩ | E21 TX/RX_EN pull-downs; supervisor pull-up |

## Mechanical / RF shielding

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| SH1/SH2 | 1–2 | board-level RF shield frame + lid | over PA and/or module (EMC + coexistence) |
| — | 4 | M2.5 standoff + screw set | matches Pi Zero 2 W hole pattern |
| — | as req | spacers / taller header | if bottom-side clearance is tight |
| — | — | E21 thermal: Cu pour + via array (optional clip heatsink) | ~1.5–2 W dissipation |

## Notable open BOM decisions (see [`DECISIONS.md`](DECISIONS.md))
1. **MM8108 bare SoC vs. module** — drives most of the schematic/layout effort and
   whether the external-FEM RF path is even accessible.
2. **VPA voltage** (3.3 V vs 5.0 V) — set per the E21 datasheet revision; fixes the
   buck-boost feedback divider.
3. **MM8108→E21 attenuator pad** — value depends on measured ext-FEM drive level.
4. **GNSS pre-filter** — populate only if coexistence testing requires it.
