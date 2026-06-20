# HANDOFF — ZERO 2W MESH HAT (continue in a LOCAL Claude Code session)

**Read this first.** This file lets a *local* Claude Code session (running in the
Claude desktop app on the user's machine, with KiCad 10 + `kicad-cli` available)
pick up exactly where the cloud session left off. The cloud session had **no KiCad**,
so everything below was validated *structurally only* and must be **re-validated with
`kicad-cli` now that it's available**.

Project: Raspberry Pi Zero 2 W HAT — **MM8108 Wi-Fi HaLow (LoRa-mesh) + NEO-M9N GNSS**.
Branch: `claude/pi-zero-hat-design-2mOoW`.
KiCad project base name (note the **spaces**): `ZERO 2W MESH HAT`.

## THE FIRST THING TO DO LOCALLY
Validate the generated files against real KiCad 10 — this is the gap that caused
earlier breakage:
```
kicad-cli version
kicad-cli sch erc  "ZERO 2W MESH HAT.kicad_sch"  --output erc.rpt   # then read erc.rpt
kicad-cli pcb drc  "ZERO 2W MESH HAT.kicad_pcb"  --output drc.rpt
```
Expect ERC to flag **PWR_FLAG** on the derived rails (`+3V3_RAD`, `+3V3_GNSS`,
`VBUS_USB`, `+5V_SW`) — add a `PWR_FLAG` to each; that's normal for label-driven rails.

## What exists (in `hardware/kicad/mesh_hat/`)
| File | What it is |
|------|-----------|
| `ZERO_2W_MESH_HAT.kicad_sch` | **Completed schematic** — user's J1 header + ID-EEPROM block, plus 46 added parts. Built by `build_schematic.py` (kiutils). Connectivity is **net-labels on pins** (electrically complete; not hand-wired). 0 floating pins, no dup refdes. |
| `ZERO_2W_MESH_HAT.kicad_pcb` | User's placed board with **16 footprints annotated** to match the schematic refdes (`annotate_pcb.py`). New parts (passives/Micro-B/LEDs) **not yet placed**. |
| `ZERO_2W_MESH_HAT.kicad_pro` | User's project + **RF50 / USB90 net classes** added. |
| `ZERO2W_MeshHat.kicad_sym` | Custom symbols **MM8108-MF15457** (38-pin) + **NEO-M9N-00B** (24-pin), footprints pre-linked. KiCad 10 (v20260206). |
| `build_schematic.py` / `annotate_pcb.py` / `generate_symbols.py` | Regenerators (idempotent). The netlist (per-pin nets) lives in `build_schematic.py` `COMPONENTS`. |

Docs: `MESH_HAT_NETREPORT.md` (every net + members), `MESH_HAT_BOM_FINAL.md`
(real-component BOM), `MESH_HAT_WIRING_INTO_PROJECT.md`, `MESH_HAT_STACKUP.md`,
`MESH_HAT_GROUNDING.md`.

## KNOWN ISSUES / WHY (fix these locally)
1. **Validation gap** — no KiCad in the cloud; nothing was ERC/DRC'd. Re-validate now.
2. **PCB ↔ schematic linking** — the user *hand-placed* the footprints, so they have **no
   UUID `(path)` link** to schematic symbols. *Update PCB from Schematic* matches by UUID
   by default → it **duplicated** everything. Fix one of two ways:
   - In *Update PCB from Schematic*, **check "Re-link footprints to schematic symbols based
     on their reference designators"** (refdes were already matched by `annotate_pcb.py`), **or**
   - Add `(path "/<sheet-uuid>/<symbol-uuid>")` to each placed footprint (cleaner; can be scripted).
3. **New parts not placed** — after a clean Update, ~30 new footprints land at the origin;
   place them (clusters: power near U4/L1; USB near J6/J7/U9; GNSS RF near U3/J3/L2/FB1;
   HaLow RF near U2/J2). Route per RF50/USB90 net classes.
4. **kiutils corrupts the PCB** — it strips the board's **embedded 3D-model blob**
   (836 KB → 88 KB). **Never** write the `.kicad_pcb` with kiutils; edit it as text or with
   KiCad/`kicad-cli`. (kiutils is fine for the `.kicad_sch`.)
5. **3D models** — standard footprints carry `(model …)` refs that resolve in KiCad 10.
   **MM8108 / NEO-M9N STEP** models must come from Morse Micro / u-blox (not redistributable here).

## Part substitutions already baked in (user-approved)
- Buck `U4` = **AP63200WU** (was TLV62569 — only ships as an `extends` symbol).
- Load switches `U5/U6` = **MIC2007YM6** (was TPS22965 / TPS22918).
- VBUS switch `U7` = **RT9742AGJ5F** (was FPF2123).

## Refdes map (board placement ↔ schematic)
U1=EEPROM(SOIC-8), U2=MM8108, U3=NEO-M9N, U4=buck, U5=input load-sw, U6=radio-rail
load-sw, U7=VBUS sw, U8=supervisor, U9=USBLC6-2; J2/J3=U.FL(900M/GNSS), J6=USB-C,
J7=Micro-B; D1=input TVS, D2/D3=RF ESD, D4–D6=LEDs; L1=buck ind, L2=GNSS bias, FB1=ferrite.
On the PCB, 7 footprints were left as `REF**` (4× SOD-323 → pick D2/D3, the rest are
surplus from the old AP6275S/hub plan → delete).

## Suggested local next steps
1. ERC/DRC with `kicad-cli` (above); add PWR_FLAGs.
2. Link footprints (re-link by reference) → *Update PCB from Schematic*.
3. Place new parts; assign 3D STEP for MM8108/NEO.
4. Route (RF50 = 50 Ω CPWG, USB90 = 90 Ω diff); pour grounds per `MESH_HAT_GROUNDING.md`.
5. `kicad-cli pcb export gerbers/drill` for fab; verify against `MESH_HAT_BOM_FINAL.md`.
