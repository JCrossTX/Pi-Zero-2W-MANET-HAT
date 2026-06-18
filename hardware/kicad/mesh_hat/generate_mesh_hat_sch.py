#!/usr/bin/env python3
"""Generate an openable KiCad 10 schematic SCAFFOLD for the ZERO 2W MESH HAT.

Single flat sheet (self-contained, no sub-sheet files needed) carrying:
  - one text block per component listing every pin -> net  (the "pin labels"),
  - a column of global labels for every named net.

This is a wiring guide: open it, drop your real symbols on top, and connect
them to the matching global labels. It is NOT a routed/symbol-placed schematic.
Pinouts are from the MM8108-MF15457 and NEO-M9N-00B datasheets.

Re-run to regenerate.  Output: ZERO2W-MESH-HAT.kicad_sch
"""
import os, uuid

SCH_VER = 20260306
GEN_VER = "10.0"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ZERO2W-MESH-HAT.kicad_sch")


def u():
    return str(uuid.uuid4())


# ----- component pin maps (text blocks): (title, body) ----------------------
BLOCKS = [
    ("U1  MM8108-MF15457  (HaLow, SPI host)",
     "2  ANT      -> RF_900 -> C(100pF) -> J3 U.FL ; D4 ESD\\n"
     "4  RESET_N  <- MM_RESET (J1.11/GPIO17) + U9 ; 10k UP\\n"
     "5  WAKE     <- MM_PWR2 (J1.18/GPIO24)\\n"
     "10 VBAT     <- +3V3_RAD ; 10uF+100nF\\n"
     "12 SPI_MISO -> SPI_MISO (J1.21/GPIO9) ; 10k UP\\n"
     "13 SPI_CS   -> SPI_CS   (J1.24/GPIO8)  ; 10k UP\\n"
     "14 SPI_INT  -> MM_IRQ   (J1.29/GPIO5)  ; 10k UP\\n"
     "15 SDIO_D2  -> 10k UP (+3V3_RAD)\\n"
     "16 SPI_MOSI -> SPI_MOSI (J1.19/GPIO10)\\n"
     "17 SPI_SCK  -> SPI_SCLK (J1.23/GPIO11)\\n"
     "22 VDDIO    <- +3V3_RAD ; 100nF\\n"
     "24 VBAT_TX  <- +3V3_RAD ; 10uF+100nF+22uF\\n"
     "25 VDD_USB  : term per ds (USB unused)\\n"
     "27/28 USBDN/P : NC   29 BUSY: spare\\n"
     "6-9 JTAG: NC   18,19,21,31-37 GPIO: spare\\n"
     "1,3,11,20,23,26,30,38 GND"),
    ("U2  NEO-M9N-00B  (GNSS, UART+I2C)",
     "1  SAFEBOOT_N 10k UP +3V3_GNSS\\n"
     "2  D_SEL      open/10k UP (UART+I2C)\\n"
     "3  TIMEPULSE -> GNSS_PPS (J1.12/GPIO18)\\n"
     "4  EXTINT    -> GNSS_EXTINT (J1.15/GPIO22)\\n"
     "8  RESET_N   <- GNSS_RESET (J1.13/GPIO27);10k UP\\n"
     "9  VCC_RF    -> L2(27-68nH) -> RF_GNSS (bias)\\n"
     "11 RF_IN     <- C(100pF) <- J2 U.FL ; D3 ESD\\n"
     "18 SDA       -> GNSS_SDA (J1.3/GPIO2)\\n"
     "19 SCL       -> GNSS_SCL (J1.5/GPIO3)\\n"
     "20 TXD       -> GNSS_TXD -> Pi RXD0 (J1.10)\\n"
     "21 RXD       <- GNSS_RXD <- Pi TXD0 (J1.8)\\n"
     "22 V_BCKP    <- +3V3_GNSS\\n"
     "23 VCC       <- +3V3_GNSS (FB1) ; 10uF+100nF\\n"
     "5,6,7 USB/V_USB: NC   14 LNA_EN: NC\\n"
     "15-17 Reserved: NC   10,12,13,24 GND"),
    ("POWER",
     "+5V (J1.2,4) -> D2 SMAJ5.0A -> U7 TPS22965 -> +5V_SW\\n"
     "+5V_SW -> U5 TLV62569 + L1 2.2uH -> +3V3\\n"
     "+3V3 -> U8 TPS22918 (EN=MM_PWR1 J1.16) -> +3V3_RAD\\n"
     "+3V3 -> FB1 ferrite -> +3V3_GNSS\\n"
     "U9 TPS3839 on +3V3 -> MM_RESET (10k UP)\\n"
     "3V3_PI (J1.1,17) -> U6 only (ref rail)"),
    ("USB-C ETHERNET PASS-THROUGH (no hub)",
     "Pi USB host -> cable -> J7 -> board -> J6 -> dongle\\n"
     "J7 MicroB D+/D- -> USB_DP/USB_DM ; GND ; VBUS/ID NC\\n"
     "D1 USBLC6-2 ESD on USB_DP/USB_DM\\n"
     "J6 USB-C D+(A6,B6)->USB_DP  D-(A7,B7)->USB_DM\\n"
     "J6 VBUS(A4/B4/A9/B9) -> VBUS_C\\n"
     "J6 CC1->56k->VBUS_C  CC2->56k->VBUS_C (Rp host)\\n"
     "U11 FPF2123: IN=+5V OUT=VBUS_C EN=on ILIM~0.5-1A\\n"
     "Pi: dtoverlay=dwc2,dr_mode=host ; OTG cable"),
    ("U6  24LC32 ID EEPROM  +  LEDs  +  SHIELDS",
     "U6 VCC=3V3_PI  GND  SDA=ID_SD(J1.27) SCL=ID_SC(J1.28)\\n"
     "   A0/A1/A2=GND  WP=10k UP 3V3_PI + JP->GND\\n"
     "   2x 3.9k pulls SDA/SCL -> 3V3_PI\\n"
     "D_PWR <- +3V3 (1k)\\n"
     "D_FIX <- LED_FIX (J1.32/GPIO12) (1k)\\n"
     "D_TX  <- LED_TX  (J1.33/GPIO13) (1k)\\n"
     "SH1 (GNSS) / SH2 (MM8108) frames -> GND  [DNP]"),
    ("J1  Pi 40-pin header (key pins)",
     "1,17 3V3_PI   2,4 +5V   GND:6/9/14/20/25/30/34/39\\n"
     "SPI0: 19 MOSI 21 MISO 23 SCLK 24 CE0/CS\\n"
     "29 GPIO5 IRQ  11 GPIO17 RST  16 GPIO23 PWR1  18 GPIO24 PWR2\\n"
     "UART0: 8 TXD0  10 RXD0   12 GPIO18 PPS\\n"
     "I2C1: 3 SDA  5 SCL   13 GPIO27 GNSS_RST  15 GPIO22 EXTINT\\n"
     "27 ID_SD  28 ID_SC   32 GPIO12 LED_FIX  33 GPIO13 LED_TX"),
]

NETS = [
    "+5V", "+5V_SW", "VBUS_C", "+3V3", "+3V3_RAD", "+3V3_GNSS", "3V3_PI", "GND",
    "SPI_MOSI", "SPI_MISO", "SPI_SCLK", "SPI_CS", "MM_IRQ", "MM_RESET",
    "MM_PWR1", "MM_PWR2",
    "GNSS_TXD", "GNSS_RXD", "GNSS_PPS", "GNSS_SDA", "GNSS_SCL",
    "GNSS_RESET", "GNSS_EXTINT",
    "RF_900", "ANT_900", "RF_GNSS",
    "USB_DP", "USB_DM", "ID_SD", "ID_SC",
    "LED_PWR", "LED_FIX", "LED_TX",
]


def build():
    L = []
    a = L.append
    a("(kicad_sch")
    a(f"\t(version {SCH_VER})")
    a('\t(generator "eeschema")')
    a(f'\t(generator_version "{GEN_VER}")')
    a(f'\t(uuid "{u()}")')
    a('\t(paper "A2")')
    a("\t(lib_symbols)")

    # Title
    a('\t(text "ZERO 2W MESH HAT - schematic scaffold (pin labels + nets)\\n'
      'MM8108-MF15457 HaLow (SPI) + NEO-M9N GNSS + USB-C Ethernet pass-through\\n'
      'Drop real symbols on top and wire to the matching global labels. '
      'See docs/MESH_HAT_SCHEMATIC.md." '
      f'(exclude_from_sim no) (at 20 12 0) '
      f'(effects (font (size 2 2) (thickness 0.3)) (justify left top)) (uuid "{u()}"))')

    # Component pin-map text blocks laid out in a grid
    cols = [25, 170, 320]
    rows = [40, 140, 240]
    for i, (title, body) in enumerate(BLOCKS):
        cx = cols[i % 3]
        cy = rows[i // 3]
        a(f'\t(text "{title}" (exclude_from_sim no) (at {cx} {cy} 0) '
          f'(effects (font (size 1.6 1.6) (thickness 0.25)) (justify left top)) '
          f'(uuid "{u()}"))')
        a(f'\t(text "{body}" (exclude_from_sim no) (at {cx} {cy + 6} 0) '
          f'(effects (font (size 1.1 1.1)) (justify left top)) (uuid "{u()}"))')

    # Global labels for every net, in two columns down the right edge
    gx0, gy0, dy = 470, 40, 7
    for i, net in enumerate(NETS):
        col = i // 17
        row = i % 17
        gx = gx0 + col * 60
        gy = gy0 + row * dy
        a(f'\t(global_label "{net}" (shape bidirectional) (at {gx} {gy} 0) '
          f'(fields_autoplaced yes) '
          f'(effects (font (size 1.27 1.27)) (justify left)) (uuid "{u()}"))')

    a('\t(sheet_instances')
    a('\t\t(path "/" (page "1"))')
    a('\t)')
    a(")")
    return "\n".join(L) + "\n"


def main():
    with open(OUT, "w") as f:
        f.write(build())
    print("Generated", os.path.relpath(OUT, HERE))


if __name__ == "__main__":
    main()
