# Bill of Materials (preliminary)

> **One radio site, two module options** ([`DECISIONS.md`](DECISIONS.md) §C):
> **`U1` = MM8108-M20 (primary)** — integrated 28.5 dBm PA + 902–928 SAW, FCC/IC
> certified — or **MM8108-MF15457 (fallback)**, the build-today baseline. The
> external **E21 PA, 5 V buck-boost, drive pad, T/R control and RF bypass are
> retired** (B11); no `VPA` rail.

Quantities for one HAT. MPNs are *candidates / starting points* — confirm
availability, footprint, and the electrical notes in [`POWER.md`](POWER.md) /
[`RF.md`](RF.md) before ordering.

## Core / functional

| Ref | Qty | Part | MPN (candidate) | Notes |
|-----|----:|------|-----------------|-------|
| U1  | 1 | Wi-Fi HaLow module | **MM8108-M20** (primary) / **MM8108-MF15457** (fallback) | M20: integ. 28.5 dBm PA + 902–928 SAW, FCC/IC cert, 18.5×14 mm, SPI; **pinout/power TBD (B12)**. MF15457: self-contained, ~27 dBm, build-today baseline |
| U3  | 1 | GNSS receiver | u-blox **NEO-M9N-00B** | VCC 2.7–3.6 V; UART+I²C+PPS; VCC_RF for active ant; 12.2×16.0 mm |
| U5  | 1 | 3V3 regulator | TI **TLV62569** buck (or **AP2112-3.3** LDO) | module + GNSS + RTC digital |
| U6  | 1 | HAT ID EEPROM | **24AA32A / CAT24C32** (I²C, WP) | ID_SD/ID_SC, VCC = Pi 3V3 |
| U10 | 1 | Inrush soft-start load switch | TI **TPS22965** | +5V → 3V3 buck in; tames bulk inrush (N4) |
| U11 | 1 | Voltage supervisor | TI **TPS3839** (3.3 V) | gates module RESET_N (N5) |
| U12 | 1 | Radio-rail load switch | TI **TPS22918 / TPS22965** | EN = MM_PWR1 (GPIO23); OpenMANET power-gpios (N6) |
| U13 | 1 | I²C RTC | Micro Crystal **RV-3028-C7** (alt **DS3231M**) | addr 0x52, 45 nA, **trickle charger** |

> **Retired (B11):** `U2` E21 PA, `U4` buck-boost, `U8/U9` auto-T/R detector,
> `RN1` drive pad, `C_BYP` RF bypass, `VPA` bulk, `L1`. Both module options drive
> the antenna directly.

## RF / antenna

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| J2, J3 | 2 | **U.FL / IPEX SMT** receptacle | #1 GNSS, #2 900 MHz |
| C35, C44 | 2 | 100 pF RF DC-block | series in the two RF paths |
| D30 | 0–1 | low-C RF ESD clamp | at U.FL #2 |
| FL2 | 0–1 | 900 MHz LPF (DNP default) | MF15457 only, if measured harmonics need it; M20 has integ. SAW (N3) |
| D8 | 1 | low-C TVS (GNSS U.FL) | ESD on RF_GNSS (N8) |
| FL1 | 0–1 | GNSS SAW/bandpass filter | add if radio leakage desenses GNSS |
| L40, R44 | 0–2 | bias inductor (27–68 nH) + 10 Ω | active GNSS antenna via VCC_RF |
| — | — | 50 Ω matching (TBD) | per chosen module's RF reference design |

## Connectors / power

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| J1  | 1 | **2×20 (40-pin) female header**, 2.54 mm | mates to Pi Zero 2 W; std or stacking height (see MECHANICAL) |
| L2 | 0–1 | 2.2 µH buck inductor | if U5 is a buck |
| FB1 | 1 | ferrite ~600 Ω@100 MHz | +3V3 → +3V3_GNSS |
| R13–R14, R20–R52 | many | 0402 1% | FB divider, SPI term, pulls |
| C1–C50 | many | 0402/0603 + bulk | decoupling per docs/SCHEMATIC.md |
| D1 | 0–1 | SMAJ5.0A TVS | 5 V input protection |
| JP1 | 1 | EEPROM WP jumper | default = write-protected |

## Power-management / indicators / RTC

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| BT1 | 1 | **Seiko MS621FE** (or Panasonic ML414H/ML621) rechargeable, solder-tab | RTC backup, trickle-charged from +3V3 (PCB-soldered) |
| D_PWR/D_TX/D_FIX | 3 | LEDs (green/red/green) + R70–R72 1 kΩ | power-good / TX-active (host GPIO) / GNSS-fix |
| R24–R27 | 4 | 10 kΩ | SPI/SDIO bus pull-ups (module note [1]) |
| R60 | 1 | 10 kΩ | supervisor pull-up |

## Mechanical / RF shielding

| Ref | Qty | Part | Notes |
|-----|----:|------|-------|
| SH1/SH2 | 1–2 | board-level RF shield frame + lid | over radio and/or GNSS (EMC + coexistence) |
| — | 4 | M2.5 standoff + screw set | matches Pi Zero 2 W hole pattern |
| — | as req | spacers / taller header | if bottom-side clearance is tight |
| — | — | radio thermal: Cu pour + via array (optional heatsink) | M20 integ. PA dissipation |

## Notable open BOM decisions (see [`DECISIONS.md`](DECISIONS.md))
1. **MM8108-M20 vs MF15457** (B11) — M20 is the certified high-power primary but
   datasheet/sourcing are pending; MF15457 is the build-today fallback. Same site.
2. **M20 footprint/power** (B12) — finalize `U1` land pattern + decoupling and
   whether any extra rail is needed once Morse publishes the datasheet.
3. **GNSS pre-filter** — populate only if coexistence testing requires it.
