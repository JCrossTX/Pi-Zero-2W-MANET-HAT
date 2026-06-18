#!/usr/bin/env python3
"""Generate KiCad 9 schematic symbols for the custom parts on the ZERO 2W MESH HAT
(MM8108-MF15457, NEO-M9N-00B) from their datasheet pinouts, so they can be placed
in the schematic. Footprints are pre-associated to the board's custom footprints.

Output: ZERO2W_MeshHat.kicad_sym  (version 20250114 = KiCad 9)
Pins are laid out in numeric order, left column then right column.
"""
import os

VER = 20250114
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ZERO2W_MeshHat.kicad_sym")

# (number, name, type)   type in: power_in, input, output, bidirectional, passive
MM8108 = [
    ("1","GND","power_in"),("2","ANT","passive"),("3","GND","power_in"),
    ("4","RESET_N","input"),("5","WAKE","input"),("6","JTAG_TMS","bidirectional"),
    ("7","JTAG_TCK","bidirectional"),("8","JTAG_TDO","bidirectional"),
    ("9","JTAG_TDI","bidirectional"),("10","VBAT","power_in"),("11","GND","power_in"),
    ("12","SDIO_D0/SPI_MISO","bidirectional"),("13","SDIO_D3/SPI_CS","bidirectional"),
    ("14","SDIO_D1/SPI_INT","bidirectional"),("15","SDIO_D2","bidirectional"),
    ("16","SDIO_CMD/SPI_MOSI","bidirectional"),("17","SDIO_CLK/SPI_SCK","bidirectional"),
    ("18","GPIO5","bidirectional"),("19","GPIO4","bidirectional"),("20","GND","power_in"),
    ("21","GPIO3","bidirectional"),("22","VDDIO","power_in"),("23","GND","power_in"),
    ("24","VBAT_TX","power_in"),("25","VDD_USB","power_in"),("26","GND","power_in"),
    ("27","USB_D_N","bidirectional"),("28","USB_D_P","bidirectional"),
    ("29","BUSY","output"),("30","GND","power_in"),("31","GPIO1","bidirectional"),
    ("32","GPIO0","bidirectional"),("33","GPIO6","bidirectional"),
    ("34","GPIO7","bidirectional"),("35","GPIO8","bidirectional"),
    ("36","GPIO9","bidirectional"),("37","GPIO10","bidirectional"),("38","GND","power_in"),
]
NEO = [
    ("1","SAFEBOOT_N","input"),("2","D_SEL","input"),("3","TIMEPULSE","output"),
    ("4","EXTINT","input"),("5","USB_DM","bidirectional"),("6","USB_DP","bidirectional"),
    ("7","V_USB","power_in"),("8","RESET_N","input"),("9","VCC_RF","output"),
    ("10","GND","power_in"),("11","RF_IN","input"),("12","GND","power_in"),
    ("13","GND","power_in"),("14","LNA_EN","output"),("15","Reserved","passive"),
    ("16","Reserved","passive"),("17","Reserved","passive"),
    ("18","SDA/SPI_CS","bidirectional"),("19","SCL/SPI_SCK","bidirectional"),
    ("20","TXD/SPI_SDO","output"),("21","RXD/SPI_SDI","input"),
    ("22","V_BCKP","power_in"),("23","VCC","power_in"),("24","GND","power_in"),
]


def font():
    return "(effects (font (size 1.27 1.27)))"


def symbol(name, value, footprint, pins):
    n = len(pins)
    per = (n + 1) // 2
    half = per * 2.54
    top = round(half / 2 + 1.27, 2)
    bot = -top
    xL, xR = -20.32, 20.32
    rx = 15.24
    L = []
    a = L.append
    a(f'\t(symbol "{name}"')
    a('\t\t(pin_names (offset 1.016))')
    a('\t\t(exclude_from_sim no)')
    a('\t\t(in_bom yes)')
    a('\t\t(on_board yes)')
    a(f'\t\t(property "Reference" "U" (at {xL} {round(top + 1.27, 2)} 0) '
      f'(effects (font (size 1.27 1.27)) (justify left)))')
    a(f'\t\t(property "Value" "{value}" (at {xL} {round(bot - 1.27, 2)} 0) '
      f'(effects (font (size 1.27 1.27)) (justify left)))')
    a(f'\t\t(property "Footprint" "{footprint}" (at 0 0 0) '
      f'(effects (font (size 1.27 1.27)) (hide yes)))')
    a('\t\t(property "Datasheet" "" (at 0 0 0) '
      '(effects (font (size 1.27 1.27)) (hide yes)))')
    # body
    a(f'\t\t(symbol "{name}_0_1"')
    a(f'\t\t\t(rectangle (start {-rx} {top}) (end {rx} {bot}) '
      f'(stroke (width 0.254) (type default)) (fill (type background)))')
    a('\t\t)')
    # pins
    a(f'\t\t(symbol "{name}_1_1"')
    for i, (num, pname, ptype) in enumerate(pins):
        if i < per:                       # left column, top->down, point right (0 deg)
            y = round(top - 1.27 - i * 2.54, 2)
            a(f'\t\t\t(pin {ptype} line (at {xL} {y} 0) (length 5.08) '
              f'(name "{pname}" {font()}) (number "{num}" {font()}))')
        else:                             # right column, top->down, point left (180)
            y = round(top - 1.27 - (i - per) * 2.54, 2)
            a(f'\t\t\t(pin {ptype} line (at {xR} {y} 180) (length 5.08) '
              f'(name "{pname}" {font()}) (number "{num}" {font()}))')
    a('\t\t)')
    a('\t)')
    return "\n".join(L)


def main():
    out = ["(kicad_symbol_lib",
           f"\t(version {VER})",
           '\t(generator "kicad_symbol_editor")',
           '\t(generator_version "9.0")']
    out.append(symbol("MM8108-MF15457", "MM8108-MF15457",
                      "cm4mesh:Morse_MM8108-MF15457_LGA38_11x10", MM8108))
    out.append(symbol("NEO-M9N-00B", "NEO-M9N-00B",
                      "cm4mesh:ublox_NEO-M9N_LCC24_12x16", NEO))
    out.append(")")
    with open(OUT, "w") as f:
        f.write("\n".join(out) + "\n")
    print("Generated", os.path.basename(OUT),
          f"({len(MM8108)} + {len(NEO)} pins)")


if __name__ == "__main__":
    main()
