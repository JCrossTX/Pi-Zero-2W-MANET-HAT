# KiCad 10 scaffold

**KiCad 10.0** project (`kicad_sch` v20260306, `kicad_pcb` v20260206,
`generator_version "10.0"`). Open `PiZero2W-MANET-HAT.kicad_pro` in KiCad 10+.

## What's here
| File | Contents |
|------|----------|
| `PiZero2W-MANET-HAT.kicad_pro` | Project (net classes: Default / Power / RF50) |
| `PiZero2W-MANET-HAT.kicad_pcb` | **65 × 30 mm** rounded-rect Edge.Cuts outline, 4× M2.5 NPTH mounting holes (Pi Zero pattern), header keepout + placement silk. No footprints yet. |
| `PiZero2W-MANET-HAT.kicad_sch` | Root schematic with 5 hierarchical sheets |
| `power.kicad_sch` | 5V → buck-boost → VPA; 3V3; bulk |
| `halow_radio.kicad_sch` | MM8108 (SPI, OpenMANET pinout, ext-FEM RF) |
| `pa_frontend.kicad_sch` | E21-900G30S PA/LNA + T/R |
| `gnss.kicad_sch` | NEO-M9N (UART/I²C/PPS) + U.FL |
| `header_eeprom.kicad_sch` | 40-pin header J1 + ID EEPROM |
| `generate_scaffold.py` | Regenerates all of the above |

The sub-sheets carry the **named nets** (global labels) from
[`../netlist/connections.csv`](../netlist/connections.csv) so you can wire to
them directly. They intentionally contain **no component symbols/footprints** —
that's the next implementation step.

## This is a scaffold
It was generated programmatically and **has not been opened in KiCad** in this
environment (no `kicad-cli` available here). Before building on it:
1. Open in KiCad 10; let it migrate/clean if prompted, then save.
2. Add real symbols/footprints over the placement zones (see
   [`../../docs/MECHANICAL.md`](../../docs/MECHANICAL.md)).
3. Replace the **nominal** 40-pin header keepout with the real 2×20 footprint at
   the **DXF-exact** Pi Zero 2 W position (silk is flagged `VERIFY`).
4. Resolve the open items in [`../../docs/DECISIONS.md`](../../docs/DECISIONS.md)
   (notably the NDA-gated MM8108 detail and the external-FEM RF path).

## Regenerate
```sh
python3 generate_scaffold.py
```
