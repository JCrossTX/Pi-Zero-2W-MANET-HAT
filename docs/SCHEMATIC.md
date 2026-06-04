# Component-Level Schematic Design

Block-by-block design detail (reference designators, values, and net
connections) to draw the schematic over the KiCad scaffold sheets. Values marked
**VERIFY** depend on the chosen regulator's reference voltage or a vendor
datasheet — confirm before committing. Conventions: `R` 0402 1%, `C` 0402 X7R
(bulk = electrolytic/tantalum/MLCC as noted), `FB` ferrite bead.

---

## 1. Power (`power.kicad_sch`)

### 1.1 Input from header
- `+5V` from header pins **2 & 4**; `GND` from pins 6/9/14/20/25/30/34/39.
- Input bulk at the header: `C1` 100 µF (≥10 V, low-ESR) ‖ `C2` 10 µF ‖ `C3` 100 nF.
- Optional input protection: `D1` reverse/ESD (e.g. SMAJ5.0A TVS) across +5V/GND;
  `F1` resettable fuse (PTC) or ferrite in series for the HAT load.

### 1.2 Buck-boost → `VPA` (E21 PA rail)
- `U4` = **TI TPS63802** (alt **TPS63070** for more headroom). Topology: 5 V in,
  regulated **~5.0 V** out (set per E21 datasheet — see [`DECISIONS.md`](DECISIONS.md) B4).
- Feedback divider (Vout = Vref·(1 + R_top/R_bot)):
  - TPS63802 **Vref ≈ 0.5 V (VERIFY)** → for 5.0 V, R_top/R_bot = 9.
    `R10` (top) = 910 kΩ, `R11` (bot) = 100 kΩ (E96). If VPA target is 3.3 V,
    R_top/R_bot = 5.6 → `R10` = 560 kΩ.
- `L1` = 1.0 µH (per TPS63802 datasheet, low-DCR, ≥2 A sat).
- `Cin` `C4` 10 µF; `Cout` `C5`+`C6` 2×22 µF; **VPA bulk** `C7` 100–220 µF
  (low-ESR) at the E21 VCC to source TX bursts (see [`POWER.md`](POWER.md)).
- `R12` 100 kΩ enable pull (tie EN to +5V or to a GPIO if soft-start gating wanted).

### 1.3 3V3 rail → `+3V3`
- `U5` = **TI TLV62569** buck (alt LDO **AP2112-3.3 / TLV75533** if load < 0.6 A).
  - Buck FB: TLV62569 **Vref ≈ 0.6 V (VERIFY)** → for 3.3 V, R_top/R_bot = 4.5.
    `R13` = 453 kΩ, `R14` = 100 kΩ (E96). `L2` = 2.2 µH; `Cout` `C8` 22 µF.
- Decoupling fan-out on `+3V3` near each load: 10 µF + 100 nF per device.

### 1.4 GNSS clean supply
- `FB1` ferrite (≈600 Ω @100 MHz, ≥300 mA) from `+3V3` → `+3V3_GNSS`.
- `C9` 10 µF ‖ `C10` 100 nF on `+3V3_GNSS` at the NEO-M9N VCC pin.

### 1.5 `3V3_PI` (reference / EEPROM)
- Header pins **1 & 17** = `3V3_PI`; used as a logic reference **and** to power the
  ID EEPROM only (so it is readable at boot before the HAT's own 3V3 exists).
  **Not** a HAT power rail.

---

## 2. HaLow radio — MM8108 (`halow_radio.kicad_sch`)

> Detailed pinout / power-sequencing / RF reference are **NDA-gated**. Treat as a
> parameterised block; transcribe exact pins from the Morse Micro reference
> design or use a module. Nets below are fixed by this board.

- `U1` = MM8108 SoC (5×5 BGA) **or** an MM8108 module exposing the ext-FEM RF path.
- **SPI (to header):** `SPI_MOSI`/`SPI_MISO`/`SPI_SCLK`/`SPI_CS_MM`.
  - Series-term option `R20–R23` (0 Ω default, footprint for 22 Ω) on the 4 SPI
    lines for SI at 20 MHz over the header.
  - `R24` 10 kΩ pull-up on `SPI_CS_MM` to `+3V3` (idle-high CS).
- **Control:** `MM_IRQ` (GPIO5, in), `MM_RESET_N` (GPIO17), `MM_PWR1/2`
  (GPIO23/24). `R25` 10 kΩ pull-up on `MM_RESET_N` to `+3V3`; optional `C` 100 nF
  RC for clean reset. Pulls on PWR lines per the radio's power-on requirement.
- **Power:** `+3V3` (+ any internal 1V8/1V2 per ref design — many parts derive
  these from an internal PMU; provide the required external rails/inductor if the
  PMU needs them). Decoupling array per ref design (one 100 nF per supply ball +
  bulk 4.7–10 µF).
- **Clock:** reference crystal/TCXO `Y1` per the ref design (frequency + load caps
  from Morse Micro). **VERIFY.**
- **RF:** `RF_900` = ext-FEM TX/RX port → §3. `FEM_TX`/`FEM_RX` = FEM-control
  outputs → E21 T/R (§3.4).

---

## 3. 900 MHz front-end — E21-900G30S (`pa_frontend.kicad_sch`)

E21 stamp module pins (typical): `VCC`, `GND`(×n), `TXEN`, `RXEN`, `RFI`
(transceiver/IO side), `RFO`/`ANT` (antenna side). **VERIFY pin map** vs the
current EBYTE datasheet.

### 3.1 Power
- `U2.VCC` = `VPA`. Local decoupling: `C30` 100 µF (bulk, shared with `C7`) ‖
  `C31` 10 µF ‖ `C32` 100 nF ‖ `C33` 10 nF, fanned by frequency, right at VCC.

### 3.2 TX/RX RF path
- **`RF_900` → E21 `RFI`:** 50 Ω microstrip. `C34` 100 pF DC-block in series.
  - **Drive-set attenuator** `RN1` = π-pad footprint (`R30` series, `R31`/`R32`
    shunt), **default `R30`=0 Ω, `R31`/`R32`=DNP**; populate to drop MM8108 drive
    into the E21 linear window after measurement ([`DECISIONS.md`](DECISIONS.md) B3).
- **E21 `RFO` → `ANT_900` → `J3` (U.FL #2):** 50 Ω. `C35` 100 pF DC-block.
  Optional `D30` RF ESD clamp (low-C, e.g. RClamp0521) at the connector.

### 3.3 Antenna connector
- `J3` = U.FL/IPEX SMT, board edge. Ground the shell with vias.

### 3.4 T/R switching
- `U2.TXEN` ← `FEM_TX`; `U2.RXEN` ← `FEM_RX` (from MM8108 FEM ctrl).
- `R33`/`R34` 10 kΩ **pull-downs** on TXEN/RXEN → default **Shutdown** at reset
  (both low). Never allow both high.
- **Optional interlock** `U7` (single-gate, e.g. SN74LVC1G): derive RXEN = NOT
  TXEN if the radio drives only one line, or use as a guard. DNP if MM8108 gives
  clean complementary FEM control.
- **Fallback (DNP):** `R35` 0 Ω from `FEM_TXEN_FB` (hdr GPIO4) to TXEN; `R36` 0 Ω
  from `FEM_RXEN_FB` (hdr GPIO6) to RXEN — bring-up only.

---

## 4. GNSS — NEO-M9N (`gnss.kicad_sch`)

- `U3` = u-blox NEO-M9N.
- **Power:** `VCC` = `+3V3_GNSS` (via `FB1`). `V_BCKP` from `+3V3` through `R40`
  10 Ω (+ optional backup: `B1` coin cell / supercap via `D40` Schottky for
  hot-start). `C40` 10 µF ‖ `C41` 100 nF at VCC.
- **Config:** `D_SEL` left **open/high** (UART + I²C mode). `R41` 10 kΩ pull-up on
  `RESET_N` to `+3V3_GNSS`.
- **Host data:** `GNSS_TXD`/`GNSS_RXD` (UART, 3V3 — direct to Pi).
  `TIMEPULSE` → `GNSS_PPS`. `EXTINT` → `GNSS_EXTINT`. `RESET_N` → `GNSS_RESET_N`.
- **I²C (alt):** `SDA`/`SCL` → header; `R42`/`R43` 4.7 kΩ pull-ups to `+3V3_GNSS`
  (the Pi also has 1.8 kΩ pulls on I²C1 — DNP these if doubling up).
- **RF:** `J2` (U.FL #1) → `C44` 100 pF DC-block → `RF_IN`.
  - **Active-antenna bias:** `U3.VCC_RF` → `L40` RF bias inductor (≈ 27–68 nH, or
    a >300 Ω@900 MHz ferrite) → U.FL center. `R44` 10 Ω series limit. (NEO-M9N
    `VCC_RF` is a filtered supply output intended for this.) DNP for a passive
    antenna.

---

## 5. Header + ID EEPROM (`header_eeprom.kicad_sch`)

- `J1` = 2×20 female, 2.54 mm. Power/GND and all signals per
  [`INTERFACES.md`](INTERFACES.md). Use **both** 5 V pins and all GND pins.
- `U6` = **24AA32A / CAT24C32** ID EEPROM:
  - `VCC` = `3V3_PI` (header pin 1) — **not** the HAT 3V3 reg.
  - `SDA` = `ID_SD` (pin 27), `SCL` = `ID_SC` (pin 28).
  - `A0/A1/A2` = GND (addr 0x50). `R50`/`R51` 3.9 kΩ SDA/SCL pull-ups to `3V3_PI`.
  - `WP`: `R52` pull to `3V3_PI` = **write-protected by default**; `JP1` jumper to
    GND to enable programming.
  - `C50` 100 nF decoupling.

---

## 6. Net ↔ refdes cross-reference
See [`../hardware/netlist/connections.csv`](../hardware/netlist/connections.csv)
for the authoritative net list; this document adds the passive/refdes detail that
sits between those endpoints. Update both together.
