# ZERO 2W MESH HAT — Schematic Reference (build map)

Complete, authoritative connection map for the **ZERO 2W MESH HAT** board:
**MM8108-MF15457 HaLow (SPI) + NEO-M9N GNSS (UART/I²C) + USB-C Ethernet
pass-through**, on a Pi Zero 2 W HAT (65 × 30 mm), powered from the 40-pin header.

Pinouts are taken from the vendor datasheets (MM8108-MF15457, NEO-M9N-00B).
The companion openable scaffold is
[`../hardware/kicad/mesh_hat/ZERO2W-MESH-HAT.kicad_sch`](../hardware/kicad/mesh_hat/ZERO2W-MESH-HAT.kicad_sch)
(global-label nets + per-part pin labels — drop your symbols onto it and wire to
the labels).

> **Dropped vs. the original placement** (confirmed infeasible on a Pi Zero 2 W):
> the **AP6275S** (SDIO/UART only — no USB; SDIO not on the header) and the
> **USB2514B hub** (pointless once only one USB device remains). With them go the
> 1.8 V rail, **both crystals**, and 2 of the 4 U.FL. See chat history / datasheets.

## Reference designators
| Ref | Part | Footprint |
|-----|------|-----------|
| J1 | Pi 40-pin header | `Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical` |
| U1 | MM8108-MF15457 HaLow | `cm4mesh:Morse_MM8108-MF15457_LGA38_11x10` |
| U2 | NEO-M9N GNSS | `cm4mesh:ublox_NEO-M9N_LCC24_12x16` |
| U5 | TLV62569 3V3 buck | `Package_TO_SOT_SMD:SOT-23-6` |
| U6 | 24LC32 ID EEPROM | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| U7 | TPS22965 inrush switch | `Package_TO_SOT_SMD:SOT-23-6` |
| U8 | TPS22918 radio load switch | `Package_TO_SOT_SMD:SOT-23-6` |
| U9 | TPS3839 supervisor | `Package_TO_SOT_SMD:SOT-23-5` |
| U11 | FPF2123 USB-C VBUS switch | `Package_TO_SOT_SMD:SOT-23-5` |
| D1 | USBLC6-2 USB ESD | `Package_TO_SOT_SMD:SOT-23-6` |
| D2 | SMAJ5.0A input TVS | `Diode_SMD:D_SMA` |
| D3,D4 | low-C RF ESD | `Diode_SMD:D_SOD-323` |
| D_PWR/D_FIX/D_TX | status LEDs | `LED_SMD:LED_0603_1608Metric` |
| J2,J3 | U.FL (GNSS, 900 MHz) | `Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical` |
| J6 | USB-C receptacle | `Connector_USB:USB_C_Receptacle_GCT_USB4085` |
| J7 | USB Micro-B (to Pi) | `Connector_USB:USB_Micro-B_GCT_USB3076-30-A` |
| L1 | 2.2 µH buck inductor | `Inductor_SMD:L_Wuerth_MAPI-4020` |
| L2 | 27–68 nH GNSS RF bias | `Inductor_SMD:L_0402_1005Metric` |
| FB1 | 600 Ω ferrite (GNSS) | `Inductor_SMD:L_0603_1608Metric` |
| MH1–4 | M2.5 mounting | `MountingHole:MountingHole_2.7mm_M2.5` |
| SH1,SH2 | RF shield frames (DNP) → GND | `RF_Shielding:*` (see grounding doc) |

## Nets
`+5V` `+5V_SW` `VBUS_C` `+3V3` `+3V3_RAD` `+3V3_GNSS` `3V3_PI` `GND`
· `SPI_MOSI` `SPI_MISO` `SPI_SCLK` `SPI_CS` `MM_IRQ` `MM_RESET` `MM_PWR1` `MM_PWR2`
· `GNSS_TXD` `GNSS_RXD` `GNSS_PPS` `GNSS_SDA` `GNSS_SCL` `GNSS_RESET` `GNSS_EXTINT`
· `RF_900` `ANT_900` `RF_GNSS` · `USB_DP` `USB_DM` · `ID_SD` `ID_SC`
· `LED_PWR` `LED_FIX` `LED_TX`

---

## U1 — MM8108-MF15457 (HaLow, SPI host)
| Pin | Name | Net / connection |
|-----|------|------------------|
| 2 | ANT | `RF_900` → C(100 pF) → **J3 U.FL**; D4 ESD→GND |
| 4 | RESET_N | `MM_RESET` (J1-11/GPIO17) wired-AND U9; 10 k↑ +3V3_RAD |
| 5 | WAKE | `MM_PWR2` (J1-18/GPIO24) |
| 10 | VBAT | `+3V3_RAD`; 10 µF + 100 nF |
| 12 | SDIO_D0 / **SPI_MISO** | `SPI_MISO` (J1-21/GPIO9); 10 k↑ |
| 13 | SDIO_D3 / **SPI_CS** | `SPI_CS` (J1-24/GPIO8/CE0); 10 k↑ |
| 14 | SDIO_D1 / **SPI_INT** | `MM_IRQ` (J1-29/GPIO5); 10 k↑ |
| 15 | SDIO_D2 | 10 k↑ +3V3_RAD (unused in SPI) |
| 16 | SDIO_CMD / **SPI_MOSI** | `SPI_MOSI` (J1-19/GPIO10) |
| 17 | SDIO_CLK / **SPI_SCK** | `SPI_SCLK` (J1-23/GPIO11) |
| 22 | VDDIO | `+3V3_RAD`; 100 nF |
| 24 | VBAT_TX | `+3V3_RAD`; 10 µF + 100 nF + 22 µF bulk |
| 25 | VDD_USB | terminate per datasheet (USB unused) |
| 27/28 | USB_D_N/P | NC |
| 29 | BUSY | optional → spare GPIO/test |
| 6–9 | JTAG TMS/TCK/TDO/TDI | NC (optional test pads) |
| 18,19,21,31–37 | GPIO5/4/3/1/0/6–10 | spare → NC/test |
| 1,3,11,20,23,26,30,38 | GND | `GND` |

Pull-ups (10 k to +3V3_RAD): pins 12,13,14,15. Decoupling per the supply pins above.

## U2 — NEO-M9N (GNSS, UART + I²C mode)
| Pin | Name | Net / connection |
|-----|------|------------------|
| 1 | SAFEBOOT_N | 10 k↑ +3V3_GNSS (leave high) |
| 2 | D_SEL | open / 10 k↑ → UART+I²C mode |
| 3 | TIMEPULSE | `GNSS_PPS` (J1-12/GPIO18) |
| 4 | EXTINT | `GNSS_EXTINT` (J1-15/GPIO22) |
| 8 | RESET_N | `GNSS_RESET` (J1-13/GPIO27); 10 k↑ |
| 9 | VCC_RF | bias out → L2 (27–68 nH) → `RF_GNSS` (DC on coax) |
| 11 | RF_IN | C(100 pF) → **J2 U.FL**; D3 ESD; bias from pin 9 |
| 14 | LNA_EN | optional → NC |
| 18 | SDA | `GNSS_SDA` (J1-3/GPIO2) |
| 19 | SCL | `GNSS_SCL` (J1-5/GPIO3) |
| 20 | TXD | `GNSS_TXD` → Pi RXD0 (J1-10/GPIO15) |
| 21 | RXD | `GNSS_RXD` ← Pi TXD0 (J1-8/GPIO14) |
| 22 | V_BCKP | `+3V3_GNSS` (no backup cell) |
| 23 | VCC | `+3V3_GNSS` (from +3V3 via FB1); 10 µF + 100 nF |
| 5,6,7 | USB_DM/DP/V_USB | NC / V_USB→GND |
| 15,16,17 | Reserved | NC |
| 10,12,13,24 | GND | `GND` |

I²C pull-ups: 4.7 k on SDA/SCL → +3V3_GNSS (DNP if relying on the Pi's 1.8 k).

## Power
- `+5V` (J1-2,4) → **D2 SMAJ5.0A** to GND → **U7 TPS22965** inrush → `+5V_SW`
- `+5V_SW` → **U5 TLV62569** + **L1 2.2 µH** + FB divider + in/out caps → `+3V3`
- `+3V3` → **U8 TPS22918** (EN=`MM_PWR1` J1-16/GPIO23) → `+3V3_RAD`
- `+3V3` → **FB1** ferrite → `+3V3_GNSS`
- **U9 TPS3839** on `+3V3`, open-drain → `MM_RESET`, 10 k↑
- `3V3_PI` (J1-1,17) powers **U6** only (reference rail, not a HAT supply)

## USB-C Ethernet pass-through (no hub)
Path: **Pi USB (host) → cable → J7 → board → J6 USB-C → dongle (device).**
| Node | Connection |
|------|------------|
| J7 (Micro-B) D+/D− | `USB_DP` / `USB_DM` |
| J7 GND / VBUS / ID | `GND` / NC (self-powered) / NC |
| **D1 USBLC6-2** | ESD on `USB_DP`/`USB_DM` (+VBUS) |
| J6 (USB-C) D+ A6+B6 / D− A7+B7 | `USB_DP` / `USB_DM` |
| J6 VBUS (A4/B4/A9/B9) | `VBUS_C` |
| J6 CC1 → 56 k → VBUS_C; CC2 → 56 k → VBUS_C | Rp (host advertise) |
| J6 GND / SBU | `GND` / NC |
| **U11 FPF2123** | IN=`+5V`, OUT=`VBUS_C`, EN=on, ILIM ≈ 0.5–1 A |

> Pi: `dtoverlay=dwc2,dr_mode=host`; Pi-side cable = micro-USB **OTG** (ID grounded).

## U6 — 24LC32 ID EEPROM  +  LEDs
- U6: VCC=`3V3_PI` (J1-1) · GND=GND · SDA=`ID_SD` (J1-27) · SCL=`ID_SC` (J1-28) ·
  A0/A1/A2=GND · WP=10 k↑ 3V3_PI + jumper→GND · 2× 3.9 k pulls on SDA/SCL→3V3_PI
- LEDs (1 k series each): D_PWR ← `+3V3` · D_FIX ← `LED_FIX` (J1-32/GPIO12) ·
  D_TX ← `LED_TX` (J1-33/GPIO13)

## Passive totals (estimate)
`R_0402_1005Metric` ≈ 24 · `C_0402_1005Metric` ≈ 25 · `C_0805_2012Metric` ≈ 6 ·
`C_1206_3216Metric` ≈ 3 · **crystals: 0**.

## Host config (Pi)
```ini
dtparam=spi=on
enable_uart=1
dtoverlay=disable-bt
dtoverlay=pps-gpio,gpiopin=18
dtoverlay=dwc2,dr_mode=host
```
