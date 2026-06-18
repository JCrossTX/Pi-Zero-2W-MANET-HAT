# ZERO 2W MESH HAT — Per-Reference BOM

Every reference designator with its value and exact footprint, matching
[`MESH_HAT_SCHEMATIC.md`](MESH_HAT_SCHEMATIC.md). Assign these values to the
symbols as you place them. Footprint = `Library:Name` (stock KiCad unless noted).

R/C default = **0402**; bump to 0603 if you prefer hand-soldering (same library,
`…_0402_1005Metric` → `…_0603_1608Metric`). `DNP` = place footprint, do not stuff.

## ICs / modules
| Ref | Value / Part | Footprint |
|-----|--------------|-----------|
| U1 | MM8108-MF15457 | `cm4mesh:Morse_MM8108-MF15457_LGA38_11x10` *(custom)* |
| U2 | NEO-M9N-00B | `cm4mesh:ublox_NEO-M9N_LCC24_12x16` *(custom)* |
| U5 | TLV62569DBVR (3.3 V buck) | `Package_TO_SOT_SMD:SOT-23-6` |
| U6 | 24LC32 (I²C EEPROM) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| U7 | TPS22965 (inrush load switch) | `Package_TO_SOT_SMD:SOT-23-6` |
| U8 | TPS22918 (radio load switch) | `Package_TO_SOT_SMD:SOT-23-6` |
| U9 | TPS3839L30 (3.0 V supervisor) | `Package_TO_SOT_SMD:SOT-23-5` |
| U11 | FPF2123 (USB-C VBUS switch) | `Package_TO_SOT_SMD:SOT-23-5` |

## Connectors / mechanical
| Ref | Value / Part | Footprint |
|-----|--------------|-----------|
| J1 | 2×20 socket (Pi header) | `Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical` |
| J2 | U.FL (GNSS) | `Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical` |
| J3 | U.FL (900 MHz) | `Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical` |
| J6 | USB-C (GCT USB4085) | `Connector_USB:USB_C_Receptacle_GCT_USB4085` |
| J7 | USB Micro-B (GCT USB3076) | `Connector_USB:USB_Micro-B_GCT_USB3076-30-A` |
| JP1 | EEPROM WP jumper | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| MH1–MH4 | M2.5 mount (×4) | `MountingHole:MountingHole_2.7mm_M2.5` |

## Diodes / LEDs
| Ref | Value / Part | Footprint |
|-----|--------------|-----------|
| D1 | USBLC6-2SC6 (USB ESD) | `Package_TO_SOT_SMD:SOT-23-6` |
| D2 | SMAJ5.0A (5 V TVS) | `Diode_SMD:D_SMA` |
| D3 | low-C RF TVS (GNSS, e.g. ESD9B5.0) | `Diode_SMD:D_SOD-323` |
| D4 | low-C RF TVS (900 MHz) | `Diode_SMD:D_SOD-323` |
| D_PWR | LED green | `LED_SMD:LED_0603_1608Metric` |
| D_FIX | LED green | `LED_SMD:LED_0603_1608Metric` |
| D_TX | LED red | `LED_SMD:LED_0603_1608Metric` |

## Inductors / ferrites
| Ref | Value | Footprint |
|-----|-------|-----------|
| L1 | 2.2 µH (≥1.5 A, buck) | `Inductor_SMD:L_Wuerth_MAPI-4020` |
| L2 | 33 nH (GNSS ant. bias) | `Inductor_SMD:L_0402_1005Metric` |
| FB1 | ferrite 600 Ω@100 MHz, ≥300 mA | `Inductor_SMD:L_0603_1608Metric` |

## Resistors — `Resistor_SMD:R_0402_1005Metric`
| Ref | Value | Purpose |
|-----|-------|---------|
| R1 | 10 k | U1.12 SPI_MISO pull-up |
| R2 | 10 k | U1.13 SPI_CS pull-up |
| R3 | 10 k | U1.14 SPI_INT pull-up |
| R4 | 10 k | U1.15 SDIO_D2 pull-up |
| R5 | 10 k | U1.4 RESET_N pull-up |
| R6 | 10 k | U9 supervisor open-drain pull-up |
| R7 | 453 k 1% | U5 FB top (3.3 V, Vref 0.6 V) |
| R8 | 100 k 1% | U5 FB bottom |
| R9 | 4.7 k | GNSS SDA pull-up (DNP if using Pi's) |
| R10 | 4.7 k | GNSS SCL pull-up (DNP if using Pi's) |
| R11 | 10 k | U2.1 SAFEBOOT_N pull-up |
| R12 | 10 k | U2.2 D_SEL pull-up (DNP=leave open) |
| R13 | 10 k | U2.8 GNSS RESET_N pull-up |
| R14 | 3.9 k | U6 ID_SD pull-up → 3V3_PI |
| R15 | 3.9 k | U6 ID_SC pull-up → 3V3_PI |
| R16 | 10 k | U6 WP pull-up → 3V3_PI |
| R17 | 56 k | J6 CC1 Rp (host advertise) |
| R18 | 56 k | J6 CC2 Rp |
| R19 | RSET per ds (~52 k ≈ 1 A) | U11 ILIM set |
| R20 | 100 k | U11 EN pull-up |
| R21 | 1 k | D_PWR series |
| R22 | 1 k | D_FIX series |
| R23 | 1 k | D_TX series |
| R24 | 10 Ω | U2.9 VCC_RF bias series |
| R25–R28 | 0 Ω DNP | SPI series-term option (MOSI/MISO/SCK/CS) |

## Capacitors
**`Capacitor_SMD:C_0402_1005Metric`** (100 pF / 1 nF / 100 nF / 1 µF)
| Ref | Value | At |
|-----|-------|----|
| C1 | 100 nF | U1 VBAT (10) |
| C3 | 100 nF | U1 VDDIO (22) |
| C4 | 100 nF | U1 VBAT_TX (24) |
| C7 | 100 pF | U1 ANT DC-block (RF_900) |
| C8 | 100 nF | U2 VCC (23) |
| C10 | 100 pF | U2 RF_IN DC-block |
| C11 | 100 nF | U2 V_BCKP |
| C14 | 100 nF | U5 Vin bypass |
| C16 | 100 nF | 5 V input bypass |
| C17 | 1 µF | U7 input/CT |
| C18 | 1 µF | U8 output |
| C19 | 100 nF | U8 input |
| C20 | 100 nF | U9 VDD |
| C22 | 100 nF | +3V3_GNSS (after FB1) |
| C23 | 100 nF | U6 VCC |
| C24 | 100 nF | VBUS_C bypass |
| C25 | 1 µF | VBUS_C bulk |
| C26 | 100 nF | U11 input |

**`Capacitor_SMD:C_0805_2012Metric`** (10 µF)
| Ref | Value | At |
|-----|-------|----|
| C2 | 10 µF | U1 VBAT |
| C5 | 10 µF | U1 VBAT_TX |
| C9 | 10 µF | U2 VCC |
| C12 | 10 µF | U5 Vin |
| C15 | 10 µF | 5 V input bulk |
| C21 | 10 µF | +3V3_GNSS |

**`Capacitor_SMD:C_1206_3216Metric`** (22 µF)
| Ref | Value | At |
|-----|-------|----|
| C6 | 22 µF | U1 VBAT_TX bulk |
| C13 | 22 µF | U5 Vout (+3V3) |

## Totals by footprint
| Footprint | Qty |
|-----------|----:|
| `Resistor_SMD:R_0402_1005Metric` | 28 (4 DNP) |
| `Capacitor_SMD:C_0402_1005Metric` | 18 |
| `Capacitor_SMD:C_0805_2012Metric` | 6 |
| `Capacitor_SMD:C_1206_3216Metric` | 2 |
| `Package_TO_SOT_SMD:SOT-23-6` | 4 (U5,U7,U8,D1) |
| `Package_TO_SOT_SMD:SOT-23-5` | 2 (U9,U11) |
| `Connector_Coaxial:U.FL_…_Vertical` | 2 |
| `Inductor_SMD:L_0402/0603 + MAPI-4020` | 3 |
| `Diode_SMD:D_SMA` / `D_SOD-323` | 1 / 2 |
| `LED_SMD:LED_0603_1608Metric` | 3 |
| `MountingHole:MountingHole_2.7mm_M2.5` | 4 |
| Crystals | 0 |
