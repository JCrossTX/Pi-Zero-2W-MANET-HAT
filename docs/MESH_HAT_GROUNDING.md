# ZERO 2W MESH HAT — Grounding, Shielding & Routing Order

Companion to [`MESH_HAT_STACKUP.md`](MESH_HAT_STACKUP.md). Covers ground via
stitching, the (optional) RF shield-can plan, and the layer-by-layer routing
order. Stackup assumed: 4-layer, **L1 signal / L2 solid GND / L3 power+GND / L4
signal** (RF + USB on L1 over L2).

## 1. Ground via stitching

| Where | Via pitch | Purpose |
|-------|-----------|---------|
| **RF trace fence** (both sides of every 50 Ω CPWG: `RF_900`, `ANT_900`, `RF_GNSS`) | **≤ 3 mm** | confine fields, continuous return |
| **U.FL shell ground** (J2, J3) | 4–6 vias per shell | low-inductance RF ground |
| **Board-edge guard ring** (perimeter) | ~5 mm | edge fence, EMC |
| **Plane stitching** (L2↔L3 GND + L1/L4 GND pours) | 5–10 mm grid | one solid ground system |
| **Module ground pads** (U1 LGA GND/EP) | full via array to L2 | RF ground + heat |
| **900 MHz ↔ GNSS isolation moat** (a stitched ground wall between U1/J3 and U2/J2) | ≤ 3 mm | coexistence isolation |
| **Shield-frame solder ring** (if SH populated) | ~2.5 mm under the fence | grounded can wall |

- Vias: 0.3 mm drill / 0.6 mm pad is fine for stitching.
- Keep **L2 continuous** under all RF/USB — stitching never substitutes for an
  unbroken reference plane.
- Put the U1 / U2 / regulator local decoupling caps' ground pads on their own
  vias straight to L2 (short return).

## 2. Coexistence (900 MHz ↔ GNSS)
- Physically separate: **U1 + J3 (900 MHz) at one end, U2 + J2 (GNSS) at the
  opposite end** (already in the placement plan), U.FL jacks on opposite edges.
- Run a **stitched ground moat** between the two RF sections.
- Keep the 3V3 buck (U5) switch node away from both RF areas and from J2/J3.

## 3. RF shield cans — OPTIONAL (DNP by default)
The **MM8108-MF15457 module is internally shielded**, and this board runs ~27 dBm
with **no external PA**, so external cans are usually unnecessary. Place the
footprints (ground fence + solder ring) but leave **DNP**; populate only if
bench coexistence testing shows GNSS C/N₀ degradation when the radio keys.

| Ref | Over | Footprint (stock) | Default |
|-----|------|-------------------|---------|
| SH1 | GNSS front-end (U2 + RF_GNSS + bias) | `RF_Shielding:Wuerth_36103205_20x20mm` | **DNP** |
| SH2 | MM8108 (U1) — module already shielded | `RF_Shielding:Laird_Technologies_BMI-S-209-F_29.36x18.50mm` | **DNP** |

- Use the **two-piece (`-F` frame + removable lid)** style so you can rework
  underneath; surround the frame land with the 2.5 mm ground via ring.
- Size the can to your final placement — swap to a larger/smaller stock frame as
  needed (Laird BMI-S / Würth 36103xxx families are all in the library).

## 4. Layer-by-layer routing order
Route in this sequence so the critical nets get the clean geometry first:

1. **Lock placement** — RF parts + U.FL at opposite edges; USB connectors (J6/J7)
   together; power (U5/U7/U8) away from RF; respect the Pi bottom-side keepouts.
2. **L1 — RF first:** `RF_900`→C7→J3 and J2→C10→U2 as **50 Ω CPWG**, shortest/
   straightest, with the ≤3 mm via fence. DC-blocks + ESD inline at the connectors.
3. **L1 — USB pair:** `USB_DP`/`USB_DM` as the **90 Ω matched pair** J7→D1→J6.
4. **L2 — pour solid GND:** no routing; verify it's unbroken under all RF/USB.
5. **L3 — power:** polygons for `+5V`, `+5V_SW`, `+3V3`, `+3V3_RAD`, `+3V3_GNSS`
   (+ GND fill in the gaps); keep VBUS_C/5V switch loop tight.
6. **L4 / L1 — digital:** SPI (`SPI_*`, `MM_*`), UART/I²C (`GNSS_*`, `ID_*`),
   control GPIO, LEDs. Keep digital off the RF/GNSS zones.
7. **GND pours** on L1 and L4; then run all the **via stitching** from §1.
8. **DRC + impedance check**; confirm net-class widths (RF50 / USB90) held.

## 5. What this adds to the design
- **BOM:** SH1, SH2 shield frames (DNP) — see [`MESH_HAT_BOM.md`](MESH_HAT_BOM.md).
- **Schematic:** SH1/SH2 are mechanical/ground parts — tie each frame pin to `GND`.
- **PCB:** the via stitching, fence, moat, and shield lands are layout features
  (no extra schematic nets beyond `GND`).
