# Wiring the radios into YOUR KiCad project

Your `ZERO 2W MESH HAT` schematic currently has J1 (header) + the ID EEPROM block.
This is how to add the rest, matching your conventions (KiCad 9; header nets labeled
with Pi-GPIO names like `GPIO10{slash}SPI0.MOSI`).

## 0. Add the custom symbols
Add [`../hardware/kicad/mesh_hat/ZERO2W_MeshHat.kicad_sym`](../hardware/kicad/mesh_hat/ZERO2W_MeshHat.kicad_sym)
as a symbol library (Preferences → Manage Symbol Libraries → Add). It contains
**MM8108-MF15457** and **NEO-M9N-00B** (footprints already linked). Place them, then
wire per below. Other parts (regulators, switches, USB-C, ESD, R/C) are stock symbols.

## 1. MM8108 (place as e.g. U2) → attach these pins to your existing header labels
| MM8108 pin | Net label to attach |
|------------|---------------------|
| 16 SDIO_CMD/SPI_MOSI | `GPIO10{slash}SPI0.MOSI` |
| 12 SDIO_D0/SPI_MISO | `GPIO9{slash}SPI0.MISO` |
| 17 SDIO_CLK/SPI_SCK | `GPIO11{slash}SPI0.SCLK` |
| 13 SDIO_D3/SPI_CS | `GPIO8{slash}SPI0.CE0` |
| 14 SDIO_D1/SPI_INT | `GPIO5` |
| 4 RESET_N | `GPIO17` (+ TPS3839, 10k pull-up) |
| 5 WAKE | `GPIO24` |
| (load-switch EN) | `GPIO23` |

Local nets: 10 VBAT, 22 VDDIO, 24 VBAT_TX → `+3V3_RAD`; 2 ANT → `RF_900`;
pull-ups 10k on 12,13,14,15 → `+3V3_RAD`. Decouple per
[`MESH_HAT_BOM.md`](MESH_HAT_BOM.md) (C1–C6). GNDs → `GND`. Unused (6–9 JTAG,
18,19,21,31–37 GPIO, 25/27/28 USB) → leave/no-connect flags.

## 2. NEO-M9N (place as e.g. U3)
| NEO pin | Net label |
|---------|-----------|
| 20 TXD | `GPIO15{slash}RXD0` (GNSS TX → Pi RX) |
| 21 RXD | `GPIO14{slash}TXD0` (Pi TX → GNSS RX) |
| 3 TIMEPULSE | `GPIO18{slash}PCM.CLK` (1 PPS) |
| 18 SDA | `GPIO2{slash}SDA1` |
| 19 SCL | `GPIO3{slash}SCL1` |
| 4 EXTINT | `GPIO22` |
| 8 RESET_N | `GPIO27` (10k pull-up) |

Local nets: 23 VCC, 22 V_BCKP → `+3V3_GNSS`; 9 VCC_RF → bias L → `RF_GNSS`;
11 RF_IN → DC-block → `RF_GNSS`; 1 SAFEBOOT_N, 2 D_SEL → 10k pull-ups (UART+I²C
mode); 5/6/7 USB → NC/GND; GNDs → `GND`.

## 3. Power tree (stock symbols)
`+5V` → TPS22965 → TLV62569 (+ L 2.2µH) → `+3V3` → TPS22918 (EN=`GPIO23`) →
`+3V3_RAD`; `+3V3` → ferrite → `+3V3_GNSS`; TPS3839 → MM8108 `RESET_N`.
Input SMAJ5.0A on `+5V`. Values: [`MESH_HAT_BOM.md`](MESH_HAT_BOM.md).

## 4. USB-C Ethernet pass-through (stock symbols)
Add USB Micro-B (J?) + USB-C (J?) + USBLC6-2 + FPF2123. Wire J7 D±—USBLC6—J6 D±
as `USB_DP`/`USB_DM`; J6 VBUS ← FPF2123 from `+5V`; CC1/CC2 → 56k → VBUS.
See [`MESH_HAT_SCHEMATIC.md`](MESH_HAT_SCHEMATIC.md) §USB.

## 5. Net classes (you currently have only Default + Power)
Add in Schematic/Board Setup → Net Classes (see
[`MESH_HAT_STACKUP.md`](MESH_HAT_STACKUP.md)):
| Class | Nets | Width / diff |
|-------|------|--------------|
| **RF50** | `RF_900`, `RF_GNSS` | 0.30 mm (CPWG) |
| **USB90** | `USB_DP`, `USB_DM` | 0.20 mm / gap 0.13 mm |

## 6. Then sync the PCB
Annotate → assign footprints (most pre-linked) → **Tools → Update PCB from
Schematic**. That nets + pulls in every footprint onto the board you already
placed; then route per [`MESH_HAT_GROUNDING.md`](MESH_HAT_GROUNDING.md).

> Refdes note: your EEPROM is already **U1**. Pick the next free numbers for the
> radios (e.g. U2 = MM8108, U3 = NEO-M9N); the BOM's exact numbers are a guide.
