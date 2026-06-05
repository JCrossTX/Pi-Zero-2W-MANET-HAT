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
- **Inrush soft-start `U10`** (load switch, TPS22965 w/ controlled slew) between
  header `+5V` and the 3V3 buck input, so bulk caps don't brown out the Pi at
  plug-in. EN = on after a small RC delay (or tied on). (Necessary item N4.)

### 1.2 ~~Buck-boost → VPA~~ — **REMOVED**
The external E21 PA (which needed a 5 V `VPA` rail) is **retired** (see
[`DECISIONS.md`](DECISIONS.md) B11). The MM8108-M20 integrates its PA at the module
supply and the MF15457 fallback has no external PA, so `U4`/`L1`/`VPA` and the VPA
bulk are deleted. Header 5 V now feeds only the 3V3 buck.

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

## 2. HaLow radio — MM8108 module (`halow_radio.kicad_sch`)

**One radio site, two module options** ([`DECISIONS.md`](DECISIONS.md) §C):
- **Primary = MM8108-M20** (integrated 28.5 dBm PA + 902–928 SAW, FCC/IC certified,
  18.5 × 14 mm). **Pinout/power/footprint are TBD until Morse publishes the
  datasheet (B12)** — its ANT goes straight to U.FL (no external PA), and it likely
  needs no extra rail. The SPI/control nets below are shared.
- **Fallback = MM8108-MF15457** (buildable today) — pin-level detail below is the
  concrete baseline; the M20 drops into the same site once its datasheet lands.

Per the MF15457 datasheet ([`../hardware/MM8108-MF15457_Data_Sheet.pdf`](../hardware/MM8108-MF15457_Data_Sheet.pdf)),
38-pin module, **self-contained** (internal clock + PMU + PA). Relevant pins:

| Pin | Name | Use here |
|-----|------|----------|
| 2 | ANT | RF output (post-internal-PA, ~27 dBm) → §3 to U.FL #2 |
| 4 | RESET_N | ← supervisor/Pi GPIO17 (`MM_RESET_N`) |
| 5 | WAKE | ← `MM_PWR2` (GPIO24) |
| 10 | VBAT | +3V3 (3.0–3.6 V) |
| 12/13/14/16/17 | SPI_MISO/SPI_CS/SPI_INT/SPI_MOSI/SPI_SCK | host SPI (alt-fn of SDIO pins) |
| 22 | VDDIO | +3V3 (host I/O, 2.25–3.6 V) |
| 24 | VBAT_TX | +3V3 (PA-domain, ~330 mA TX burst) |
| 25 | VDD_USB | N/C (USB unused) — terminate per datasheet |
| 29 | BUSY | optional → spare Pi GPIO |
| 31/32 | GPIO1/GPIO0 | spare (E21 T/R retired) — route to test pads |

- `U1` = MM8108-MF15457.
- **Power:** `VBAT`(10), `VBAT_TX`(24), `VDDIO`(22) all = `+3V3`. Decoupling per
  pin: 10 µF + 100 nF each; extra bulk 22 µF on `VBAT_TX`. **No external SoC
  inductors / 1V8 / 1V2 / TCXO** — the module integrates them.
- **SPI (to header):** SPI_MOSI(16)/SPI_MISO(12)/SPI_SCK(17)/SPI_CS(13).
  - `R20–R23` series-term option (0 Ω default, 22 Ω pad) for SI at 20 MHz.
  - SDIO/SPI bus pins (except CLK) need **10 kΩ–100 kΩ pull-ups** (datasheet note
    [1]): `R24–R27` 10 kΩ to `+3V3` on MISO/CS/INT/MOSI.
- **Control:** `SPI_INT`(14) → `MM_IRQ` (GPIO5). `RESET_N`(4) → `MM_RESET_N`
  (GPIO17) via supervisor §7; timing t0 ≥ 50 µs after VBAT, reset pulse t1 ≥
  1000 µs. `WAKE`(5) → `MM_PWR2` (GPIO24).
- **RF:** `ANT`(2) → `RF_900` (50 Ω) → §3.

---

## 3. 900 MHz RF output / antenna (`pa_frontend.kicad_sch`)

> **The external E21 PA is retired** ([`DECISIONS.md`](DECISIONS.md) B11). Both
> module options drive the antenna directly — the M20 has an **integrated PA + SAW**
> and the MF15457 outputs ~27 dBm from its internal PA — so this section is now just
> a clean 50 Ω hand-off to the connector, no PA / drive pad / T-R control.

### 3.1 RF path
- **Radio `ANT` (`RF_900`, 50 Ω) → `C35` 100 pF DC-block → `ANT_900` → `J3`
  (U.FL #2).** Keep it a short, continuous 50 Ω microstrip with stitched ground.
- **`FL2` (optional, MF15457 only):** π-LC low-pass / 915 MHz ceramic pad,
  **DNP by default**. The M20 integrates a 902–928 SAW; MF15457 is modular-certified
  on its own — populate only if measured harmonics need it.
- `D30` low-C RF ESD clamp (e.g. RClamp0521) at the connector.

### 3.2 Antenna connector
- `J3` = U.FL/IPEX SMT, board edge. Ground the shell with vias.

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

## 6. Power management & supervisor (`power.kicad_sch`)
- **Radio-rail load switch `U12`** (TPS22918/TPS22965): `+3V3` → module
  `VBAT`/`VBAT_TX`/`VDDIO`, `EN` = `MM_PWR1` (GPIO23) — implements the OpenMANET
  `power-gpios` semantics + soft-start for the module. (Item N6.)
- **Supervisor `U11`** (TPS3839, 3.3 V): open-drain `RESET` wired-AND with Pi
  `MM_RESET_N` (GPIO17) into module `RESET_N`(4); holds reset until +3V3 valid and
  meets t0/t1 timing. `R60` pull-up to `+3V3`. (Item N5.)

## 7. Status LEDs (`power.kicad_sch` / `header_eeprom.kicad_sch`)
- `D_PWR` green ← `+3V3` via `R70` 1 kΩ (power good).
- `D_TX` red ← Pi GPIO (`LED_TX`) via `R71` 1 kΩ, host-driven on TX activity
  (the old hardware `PA_TX_CTL` source is gone with the E21).
- `D_FIX` green ← Pi `GPIO12` (pin 32, `LED_FIX`) via `R72` 1 kΩ (GNSS fix,
  driven by host from PPS/fix status). (Item N9.)

## 8. RTC + soldered backup cell (`gnss.kicad_sch` or `header_eeprom.kicad_sch`)
- `U13` = **RV-3028-C7** I²C RTC (addr **0x52**). `VCC` = `+3V3`; `SDA`/`SCL` on
  **I²C1** (shared with GNSS DDC — no address clash). `INT`/`CLKOUT` → Pi
  `GPIO26` (pin 37, `RTC_INT`) for alarms/wake (optional). `C80` 100 nF.
- `BT1` = **Seiko MS621FE** (or Panasonic ML414H/ML621) rechargeable, **solder-tab**
  coin cell on `VBACKUP`; **trickle-charged** from `+3V3` via the RV-3028's internal
  charger (enable + series-R per datasheet) so it never needs replacing.
- Overlay: `dtoverlay=i2c-rtc,rv3028`. The GNSS 1 PPS can discipline the RTC.

## 9. RF shields & thermal
- **Shield frames** over the radio and/or GNSS (footprint = shield-clip fence + lid)
  for EMC and radio↔GNSS isolation. (Item N7.)
- **Radio thermal:** copper pour + thermal via array under the module (the M20's
  integrated PA dissipates more than a bare MF15457); optional heatsink land. (N10.)

## 10. Net ↔ refdes cross-reference
See [`../hardware/netlist/connections.csv`](../hardware/netlist/connections.csv)
for the authoritative net list; this document adds the passive/refdes detail that
sits between those endpoints. Update both together.
