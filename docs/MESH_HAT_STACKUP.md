# ZERO 2W MESH HAT — Stackup & Controlled Impedance

Controlled-impedance targets:
- **50 Ω single-ended** — HaLow + GNSS RF nets: `RF_900`, `ANT_900`, `RF_GNSS`
- **90 Ω differential** — USB nets: `USB_DP` / `USB_DM`

> Trace widths below are a **starting geometry for the JLCPCB `JLC04161H-7628`
> 4-layer / 1.6 mm stackup**. Always confirm the final widths with your fab's
> impedance calculator (or order the board as **controlled-impedance** and let them
> adjust) — the numbers depend on the exact prepreg Dk and copper finish.

## 1. Recommended 4-layer stackup (1.6 mm)
Put **all RF and the USB pair on L1 (top)** referenced to a **solid ground on L2**.
The thin (~0.21 mm) L1→L2 prepreg gives narrow, well-controlled traces and a tight
return path — essential for RF and USB.

| Layer | Use | Copper | Dielectric below |
|-------|-----|--------|------------------|
| **L1 top** | RF + USB + components | 1 oz (35 µm) | prepreg **7628 ≈ 0.2104 mm**, Dk ≈ 4.5 |
| **L2** | **solid GND plane** (RF/USB reference) | 0.5 oz | core ≈ 1.065 mm |
| **L3** | power (+3V3 / +5V) + GND fill | 0.5 oz | prepreg ≈ 0.2104 mm |
| **L4 bottom** | components + signals | 1 oz (35 µm) | — |

**Rule:** every 50 Ω / 90 Ω trace must run over **uninterrupted L2 ground** — no
plane splits, gaps, or other-net traces crossing underneath. Keep L2 continuous
under all RF and the USB pair.

## 2. Geometry (for the stackup above; verify with fab tool)

### 50 Ω single-ended — `RF_900`, `ANT_900`, `RF_GNSS`
| Option | Width | Notes |
|--------|-------|-------|
| **Microstrip** (L1 over L2) | **≈ 0.345 mm** (13.5 mil) | simplest |
| **CPWG** (L1, coplanar GND each side) — *preferred for RF* | **≈ 0.30 mm**, ground **gap 0.25 mm** | better isolation; stitch the side grounds with vias |

- Keep RF runs **as short and straight as possible**; U.FL jacks are already at the
  board edge near U1 (900 MHz) and U2 (GNSS).
- **Via-fence** both sides of the RF traces to L2 (vias every ≤ λ/10, ~2–3 mm).
- Ground the U.FL connector shells with multiple vias.
- 100 pF DC-blocks (C7, C10) sit in-line; keep pads matched to the 50 Ω width.
- Place the RF ESD clamps (D3, D4) as a short stub right at the connector.

### 90 Ω differential — `USB_DP` / `USB_DM`
| Param | Value |
|-------|-------|
| Type | edge-coupled microstrip, L1 over L2 |
| Trace width | **≈ 0.20 mm** (8 mil) |
| Pair spacing (gap) | **≈ 0.13 mm** (5 mil) |
| Diff target | **90 Ω ±10 %** |

- Route `USB_DP`/`USB_DM` as a **tightly-coupled pair**, equal length,
  **intra-pair skew < 1 mm** (≈ < 5 ps). Add small serpentine on the short leg to match.
- Keep the pair short (J7 → D1 → J6); the USBLC6-2 (D1) goes **in-line near J7**,
  with the ESD stubs symmetric on both lines.
- No stubs, no vias mid-pair if avoidable; if you must via, via both lines together
  and keep a ground via adjacent for return continuity.
- Maintain pair spacing through the connector breakouts; gap to other copper ≥ 3×W.

## 3. KiCad net classes (Board Setup → Net Classes)
Create two classes and assign the nets, so the router enforces the widths:

| Class | Nets | Track width | Diff pair W / gap |
|-------|------|-------------|-------------------|
| **RF50** | `RF_900`, `ANT_900`, `RF_GNSS` | 0.30 mm (CPWG) / 0.345 mm (µstrip) | — |
| **USB90** | `USB_DP`, `USB_DM` | 0.20 mm | W 0.20 mm / gap 0.13 mm |

Then set the L1↔L2 dielectric in **Board Setup → Physical Stackup** to match the
fab stackup so KiCad's impedance hints line up.

## 4. Fab checklist
- Specify **controlled impedance**: 50 Ω single-ended + 90 Ω differential, both
  referenced to L2, on L1.
- Give the fab the net-class widths; let them fine-tune for their measured Dk.
- Request the **JLC04161H-7628** (or equivalent) stackup so the thin top prepreg
  holds the geometry above; a generic "1.6 mm 4-layer" with a thick top dielectric
  would force much wider traces.
