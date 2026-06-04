#!/usr/bin/env python3
"""Generate the KiCad 10 scaffold for the Pi Zero 2 W MANET HAT.

Outputs (KiCad 10.0 s-expression formats):
  - PiZero2W-MANET-HAT.kicad_pcb   board outline + mounting holes + placement silk
                                   (kicad_pcb version 20260206)
  - PiZero2W-MANET-HAT.kicad_sch   root schematic with hierarchical sheets
  - power/halow_radio/pa_frontend/gnss/header_eeprom .kicad_sch  sub-sheets
                                   (kicad_sch version 20260306)

Re-run after editing to regenerate. The .kicad_pro is maintained by hand/KiCad.
This is a SCAFFOLD: it carries the correct mechanics + named nets, not symbols,
footprints, or routing.
"""
import os
import uuid

SCH_VER = 20260306          # KiCad 10.0 schematic file format
PCB_VER = 20260206          # KiCad 10.0 board file format
GEN_VER = "10.0"
PROJECT = "PiZero2W-MANET-HAT"
HERE = os.path.dirname(os.path.abspath(__file__))


def u():
    return str(uuid.uuid4())


# --------------------------------------------------------------------------- #
# Board
# --------------------------------------------------------------------------- #
def build_pcb():
    L = []
    a = L.append
    a("(kicad_pcb")
    a(f"\t(version {PCB_VER})")
    a('\t(generator "pcbnew")')
    a(f'\t(generator_version "{GEN_VER}")')
    a("\t(general")
    a("\t\t(thickness 1.6)")
    a("\t\t(legacy_teardrops no)")
    a("\t)")
    a('\t(paper "A4")')
    a("\t(layers")
    a('\t\t(0 "F.Cu" signal)')
    a('\t\t(31 "B.Cu" signal)')
    a('\t\t(34 "B.Paste" user)')
    a('\t\t(35 "F.Paste" user)')
    a('\t\t(36 "B.SilkS" user "B.Silkscreen")')
    a('\t\t(37 "F.SilkS" user "F.Silkscreen")')
    a('\t\t(38 "B.Mask" user)')
    a('\t\t(39 "F.Mask" user)')
    a('\t\t(40 "Dwgs.User" user "User.Drawings")')
    a('\t\t(41 "Cmts.User" user "User.Comments")')
    a('\t\t(44 "Edge.Cuts" user)')
    a('\t\t(45 "Margin" user)')
    a('\t\t(46 "B.CrtYd" user "B.Courtyard")')
    a('\t\t(47 "F.CrtYd" user "F.Courtyard")')
    a('\t\t(48 "B.Fab" user)')
    a('\t\t(49 "F.Fab" user)')
    a("\t)")
    a("\t(setup")
    a("\t\t(pad_to_mask_clearance 0)")
    a("\t)")
    a('\t(net 0 "")')

    # 65 x 30 mm rounded-rect outline (r = 3), origin top-left
    for s, e in [((3, 0), (62, 0)), ((65, 3), (65, 27)),
                 ((62, 30), (3, 30)), ((0, 27), (0, 3))]:
        a(f'\t(gr_line (start {s[0]} {s[1]}) (end {e[0]} {e[1]}) '
          f'(stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{u()}"))')
    for s, m, e in [((0, 3), (0.879, 0.879), (3, 0)),
                    ((62, 0), (64.121, 0.879), (65, 3)),
                    ((65, 27), (64.121, 29.121), (62, 30)),
                    ((3, 30), (0.879, 29.121), (0, 27))]:
        a(f'\t(gr_arc (start {s[0]} {s[1]}) (mid {m[0]} {m[1]}) (end {e[0]} {e[1]}) '
          f'(stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{u()}"))')

    # Mounting holes (Pi Zero pattern, 2.75 mm NPTH)
    for i, (x, y) in enumerate([(3.5, 3.5), (61.5, 3.5),
                                (3.5, 26.5), (61.5, 26.5)], 1):
        a(f'\t(footprint "MountingHole:MountingHole_2.7mm_M2.5"')
        a(f'\t\t(layer "F.Cu")')
        a(f'\t\t(uuid "{u()}")')
        a(f'\t\t(at {x} {y})')
        a(f'\t\t(attr exclude_from_pos_files exclude_from_bom allow_missing_courtyard)')
        a(f'\t\t(property "Reference" "H{i}" (at 0 -2.2 0) (layer "F.SilkS") '
          f'(uuid "{u()}") (effects (font (size 0.7 0.7) (thickness 0.12))))')
        a(f'\t\t(property "Value" "M2.5_NPTH" (at 0 2.2 0) (layer "F.Fab") '
          f'(hide yes) (uuid "{u()}") (effects (font (size 0.7 0.7) (thickness 0.12))))')
        a(f'\t\t(pad "" np_thru_hole circle (at 0 0) (size 2.75 2.75) '
          f'(drill 2.75) (layers "*.Cu" "*.Mask") (uuid "{u()}"))')
        a(f'\t)')

    # 40-pin header keepout (nominal — VERIFY against Pi Zero 2W DXF)
    a('\t(gr_rect (start 7.1 2.0) (end 57.9 7.6) '
      '(stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS") '
      f'(uuid "{u()}"))')

    # Silkscreen placement labels
    f_silk = [
        ("40-pin hdr (VERIFY pos vs Pi Zero 2W DXF)", 8.5, 1.0, 0.7),
        ("MANET HAT - Pi Zero 2W (TOP)", 18.0, 11.5, 1.0),
        ("NEO-M9N", 10.5, 16.0, 0.9),
        ("U.FL1 GNSS", 2.0, 22.0, 0.7),
        ("E21-900G30S PA 1W", 38.0, 16.0, 0.9),
        ("U.FL2 900MHz", 50.0, 22.0, 0.7),
        ("4-layer recommended", 19.0, 26.5, 0.7),
    ]
    for txt, x, y, sz in f_silk:
        a(f'\t(gr_text "{txt}" (at {x} {y} 0) (layer "F.SilkS") (uuid "{u()}") '
          f'(effects (font (size {sz} {sz}) (thickness 0.12)) (justify left)))')
    b_silk = [
        ("MM8108 + RF match (BTM)", 30.0, 12.0, 0.9),
        ("BUCK-BOOST / 3V3 (BTM)", 30.0, 18.0, 0.9),
        ("EEPROM (BTM)", 30.0, 23.0, 0.8),
        ("KEEPOUT: Pi HDMI/USB/SD/cam/RF-can", 30.0, 26.5, 0.7),
    ]
    for txt, x, y, sz in b_silk:
        a(f'\t(gr_text "{txt}" (at {x} {y} 0) (layer "B.SilkS") (uuid "{u()}") '
          f'(effects (font (size {sz} {sz}) (thickness 0.12)) (justify left mirror)))')

    a(")")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #
# Schematic
# --------------------------------------------------------------------------- #
SHEETS = [
    ("Power", "power.kicad_sch",
     "POWER + PWR MGMT (see docs/SCHEMATIC.md S1,S6,S7)\\n"
     "5V (hdr) -> U10 inrush switch -> U4 buck-boost -> VPA=5.0V (E21)\\n"
     "+5V_SW -> U5 buck -> +3V3 ; U12 load sw -> +3V3_RAD (module)\\n"
     "FB1 -> +3V3_GNSS. U11 supervisor -> RESET_N. LEDs. 3V3_PI=ref+EEPROM.",
     "Refdes: U4/U5 regs; U10 inrush; U11 supervisor; U12 load sw; L1/L2; "
     "C1-C10; FB1; R10-R14 FB; D1 TVS; D_PWR/D_TX/D_FIX + R70-72",
     ["+5V", "+5V_SW", "GND", "VPA", "+3V3", "+3V3_RAD", "+3V3_GNSS", "3V3_PI",
      "MM_PWR1", "MM_RESET_N", "LED_PWR", "LED_TX", "LED_FIX"]),
    ("HaLow_Radio_MM8108", "halow_radio.kicad_sch",
     "MM8108-MF15457 module U1 (38-pin, self-contained, SPI host).\\n"
     "Power: VBAT(10)/VBAT_TX(24)/VDDIO(22) = +3V3_RAD. Single ANT(2).\\n"
     "SPI: MOSI16/MISO12/SCK17/CS13; INT14->IRQ; RST_N(4); WAKE(5).\\n"
     "ANT(2)->RF_900->E21. GPIO0(32)/GPIO1(31)->PA_TX/RX_CTL (OpenMANET FW).",
     "Refdes: U1 MF15457; R20-R23 SPI term; R24-R27 10k SDIO/SPI pulls; dec",
     ["SPI_MOSI", "SPI_MISO", "SPI_SCLK", "SPI_CS_MM", "MM_IRQ",
      "MM_RESET_N", "MM_PWR2", "+3V3_RAD", "GND",
      "RF_900", "PA_TX_CTL", "PA_RX_CTL"]),
    ("PA_Frontend_E21", "pa_frontend.kicad_sch",
     "E21-900G30S U2 (VCC=5.0V, ~620mA TX, +20dBm in->+30dBm out).\\n"
     "RF_900 (module ANT +22..25dBm) -> C34 -> RN1 ~3-5dB pad -> PIN(6).\\n"
     "ANT(9) -> FL2 LPF -> C35 -> J3 U.FL2 (+30dBm harmonic compliance).\\n"
     "TX_EN(3)/RX_EN(4) <- PA_TX/RX_CTL; R33/R34 pulldown=Shutdown default.",
     "Refdes: U2 E21; J3 U.FL; FL2 LPF; RN1 pad; C30-C35; R33-R36; D30 ESD",
     ["RF_900", "ANT_900", "PA_TX_CTL", "PA_RX_CTL", "VPA", "GND",
      "FEM_TXEN_FB", "FEM_RXEN_FB"]),
    ("GNSS_RTC", "gnss.kicad_sch",
     "u-blox NEO-M9N U3 (UART0 + 1PPS GPIO18, I2C1). VCC via FB1.\\n"
     "RF_GNSS <- J2 U.FL1 -> C44 -> RF_IN(11); VCC_RF(9) -> L40 bias; D8 ESD.\\n"
     "RV-3028 RTC U13 on I2C1 (0x52), trickle-charged BT1 solder cell.\\n"
     "RTC_INT -> GPIO26. 1PPS can discipline the RTC. Keep RF from PA/buck.",
     "Refdes: U3 NEO-M9N; U13 RV-3028; BT1 MS621FE; J2 U.FL; L40/R44; D8; C40-44",
     ["GNSS_RXD", "GNSS_TXD", "GNSS_PPS", "GNSS_SDA", "GNSS_SCL",
      "GNSS_RESET_N", "GNSS_EXTINT", "RF_GNSS", "ANT_BIAS", "+3V3_GNSS",
      "RTC_INT", "RTC_VBAT", "+3V3", "GND"]),
    ("Header_EEPROM", "header_eeprom.kicad_sch",
     "40-pin female header J1 + HAT ID EEPROM U6 (24Cxx on ID_SD/ID_SC).\\n"
     "U6 VCC = 3V3_PI (Pi 3V3, pin1) so it reads at boot. WP=protected default.\\n"
     "All header nets land here. See docs/INTERFACES.md for the full map.",
     "Refdes: J1 2x20 hdr; U6 24Cxx; R50/R51 I2C pulls; R52 WP; JP1; C50",
     ["+5V", "GND", "3V3_PI", "ID_SD", "ID_SC",
      "SPI_MOSI", "SPI_MISO", "SPI_SCLK", "SPI_CS_MM",
      "MM_IRQ", "MM_RESET_N", "MM_PWR1", "MM_PWR2",
      "GNSS_RXD", "GNSS_TXD", "GNSS_PPS", "GNSS_SDA", "GNSS_SCL",
      "GNSS_RESET_N", "GNSS_EXTINT", "RTC_INT", "LED_FIX",
      "FEM_TXEN_FB", "FEM_RXEN_FB"]),
]


def build_subsheet(title, note, refdes, nets):
    fid = u()
    L = []
    a = L.append
    a("(kicad_sch")
    a(f"\t(version {SCH_VER})")
    a('\t(generator "eeschema")')
    a(f'\t(generator_version "{GEN_VER}")')
    a(f'\t(uuid "{fid}")')
    a('\t(paper "A4")')
    a("\t(lib_symbols)")
    a(f'\t(text "{title}" (exclude_from_sim no) (at 20 15 0) '
      f'(effects (font (size 2 2) (thickness 0.3)) (justify left top)) (uuid "{u()}"))')
    a(f'\t(text "{note}" (exclude_from_sim no) (at 20 22 0) '
      f'(effects (font (size 1.27 1.27)) (justify left top)) (uuid "{u()}"))')
    a(f'\t(text "{refdes}" (exclude_from_sim no) (at 20 34 0) '
      f'(effects (font (size 1.0 1.0)) (justify left top)) (uuid "{u()}"))')
    # lay out global labels in two columns
    x0, y0, dy = 40, 50, 6
    for i, net in enumerate(nets):
        col = i // 12
        row = i % 12
        x = x0 + col * 45
        y = y0 + row * dy
        a(f'\t(global_label "{net}" (shape bidirectional) (at {x} {y} 0) '
          f'(fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify left)) '
          f'(uuid "{u()}"))')
    a(")")
    return fid, "\n".join(L) + "\n"


def build_root(sheet_meta):
    root = u()
    L = []
    a = L.append
    a("(kicad_sch")
    a(f"\t(version {SCH_VER})")
    a('\t(generator "eeschema")')
    a(f'\t(generator_version "{GEN_VER}")')
    a(f'\t(uuid "{root}")')
    a('\t(paper "A4")')
    a("\t(lib_symbols)")
    a('\t(text "Pi Zero 2W MANET HAT - root sheet\\n'
      'HaLow (MM8108/SPI, OpenMANET-compatible) + E21 1W PA + NEO-M9N GNSS.\\n'
      'See docs/ for full design. Sub-sheets carry named nets; add symbols next." '
      f'(exclude_from_sim no) (at 20 12 0) '
      f'(effects (font (size 1.5 1.5)) (justify left top)) (uuid "{u()}"))')
    # place hierarchical sheet boxes
    positions = [(30, 40), (95, 40), (160, 40), (30, 95), (95, 95)]
    page = 2
    for (name, fname, _note, _rd, _nets), (sx, sy) in zip(sheet_meta, positions):
        suid = u()
        a("\t(sheet")
        a(f"\t\t(at {sx} {sy})")
        a("\t\t(size 55 35)")
        a("\t\t(exclude_from_sim no)")
        a("\t\t(in_bom yes)")
        a("\t\t(on_board yes)")
        a("\t\t(dnp no)")
        a("\t\t(fields_autoplaced yes)")
        a("\t\t(stroke (width 0.1524) (type solid))")
        a("\t\t(fill (color 0 0 0 0.0000))")
        a(f'\t\t(uuid "{suid}")')
        a(f'\t\t(property "Sheetname" "{name}" (at {sx} {sy - 0.64} 0) '
          f'(effects (font (size 1.27 1.27)) (justify left bottom)))')
        a(f'\t\t(property "Sheetfile" "{fname}" (at {sx} {sy + 35.5} 0) '
          f'(effects (font (size 1.27 1.27)) (justify left top)))')
        a("\t\t(instances")
        a(f'\t\t\t(project "{PROJECT}"')
        a(f'\t\t\t\t(path "/{root}" (page "{page}"))')
        a("\t\t\t)")
        a("\t\t)")
        a("\t)")
        page += 1
    a("\t(sheet_instances")
    a('\t\t(path "/" (page "1"))')
    a("\t)")
    a(")")
    return "\n".join(L) + "\n"


def main():
    with open(os.path.join(HERE, f"{PROJECT}.kicad_pcb"), "w") as f:
        f.write(build_pcb())
    for name, fname, note, refdes, nets in SHEETS:
        _, content = build_subsheet(name, note, refdes, nets)
        with open(os.path.join(HERE, fname), "w") as f:
            f.write(content)
    with open(os.path.join(HERE, f"{PROJECT}.kicad_sch"), "w") as f:
        f.write(build_root(SHEETS))
    print("Generated KiCad 10 scaffold:",
          f"{PROJECT}.kicad_pcb, {PROJECT}.kicad_sch, and 5 sub-sheets.")


if __name__ == "__main__":
    main()
