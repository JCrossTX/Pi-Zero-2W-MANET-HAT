# Power Tree, Budget & Regulators

> **Updated for B11:** the external E21 PA and its 5 V `VPA` buck-boost are
> **retired**. The radio (`U1`) is now a single MM8108 module — **MM8108-M20**
> (integrated PA, primary) or **MF15457** (fallback) — both fed from a 3V3 rail.
> M20 supply rails/current are **TBD until the datasheet publishes (B12)**; figures
> below use the known MF15457 baseline and are revised when M20 data lands.

## 1. Power tree

```
Header 5V (pins 2,4) ──► U10 inrush sw ──► +3V3 (buck or LDO) ──┬─► U12 load sw ─► MM8108 radio
   (from Pi's 5V,                                               ├─► NEO-M9N VCC (via FB1)
    USB-fed upstream)                                           └─► RV-3028 RTC

Header 3V3 (pins 1,17) ─────────────────► 3V3_PI  (logic reference + ID EEPROM only — NOT a supply)
```

Everything is sourced from **header 5 V**. The Pi's own 3V3 rail is deliberately
**not** loaded (its regulator only has a small margin and powering radios from it
browns out the Pi). With the PA gone there is **no 5 V buck-boost / `VPA` rail** —
a single 3V3 buck feeds the whole HAT.

## 2. M20 supply (TBD) vs MF15457

The MF15457 runs entirely from 3.0–3.6 V (VBAT/VBAT_TX/VDDIO) with internal PMU —
no external PA rail. The **MM8108-M20 adds an integrated PA**, so it likely draws a
higher peak current on its supply (and may expose a dedicated PA pin); **confirm
the M20 rail topology, voltage and TX current from the datasheet (B12)** and size
the 3V3 buck + bulk accordingly. Keep generous bulk at the module to source TX
bursts regardless of which module is fitted.

## 3. Power budget (estimate — confirm against datasheets)

No PA burst rail anymore. MF15457 baseline:

| Rail | Load | Typical | Peak | Notes (datasheet-confirmed) |
|------|------|--------:|-----:|-------|
| +3V3_RAD | MF15457 module, TX | — | **~330 mA** | VBAT_TX ≤281 mA + VBAT ~52 mA @3.3 V (Table 6) |
| +3V3_RAD | MF15457 module, RX | ~20–34 mA | — | active RX (Table 7) |
| +3V3_RAD | **MM8108-M20, TX** | — | **TBD** | integrated PA — higher peak; confirm (B12) |
| +3V3 | NEO-M9N | ~30 mA | ~70 mA acq | + active-antenna via VCC_RF (≤200 mA) |
| +3V3 | RTC RV-3028 | <0.1 µA bkp | — | trickle-charges BT1 |
| —    | Pi Zero 2 W itself | 0.4–0.7 A | up to ~1.2 A | not on the HAT, but shares the upstream 5 V |

MF15457 HAT draw at the 5 V input (module TX + GNSS/RTC) ≈ ~0.4 A·3.3 V/η ≈
**~0.3 A**, on top of the Pi — well within a normal supply. **The M20 TX peak will
raise this; re-tally once its current is known.**

**Upstream 5 V sizing:** even with the M20's higher PA draw, total HAT load stays
modest next to the Pi (~0.7–1.2 A). A **≥ 2.5–3 A** supply feeding the Pi remains
the safe target. Use **both** 5 V pins (2 and 4) and **multiple GND** pins.

## 4. Suggested regulators (starting points)

| Function | Candidate | Why |
|----------|-----------|-----|
| +3V3 (efficient) | **TI TLV62569 / AP63203** buck (~1–2 A) | efficient 5 V→3V3 for the radio; size ≥1 A for M20 PA peak |
| +3V3 (simple/quiet) | **AP2112-3.3 / TLV75533** LDO (≤ 0.6 A) | only if the (MF15457) 3V3 load fits LDO headroom/thermal |
| Antenna bias (GNSS) | inductor/ferrite + cap bias-tee off +3V3, with fuse/limit | for active GNSS antenna |

## 5. Decoupling / layout notes

- **Module bulk** right at the radio supply pin(s): 22–100 µF + 10 µF + 100 nF
  fanned by frequency, to source the TX edge (more bulk for the M20's PA).
- Keep the TX supply loop tight; star/short ground return at the module.
- Separate quiet analog feed for the NEO-M9N (ferrite from +3V3) — GNSS is
  sensitive to switching-regulator noise. Keep the GNSS LNA/antenna path away from
  the 3V3 buck switch node.
- Keep the buck switch node small and shielded by ground pour; locate it away from
  both U.FL connectors and the 900 MHz / GNSS RF traces.
