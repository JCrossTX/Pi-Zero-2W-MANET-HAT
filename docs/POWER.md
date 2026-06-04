# Power Tree, Budget & Regulators

## 1. Power tree

```
Header 5V (pins 2,4) ──┬─────────────► VPA  (buck-boost, regulated ~5.0 V)  ──► E21-900G30S VCC
   (from Pi's 5V,      │                 └── bulk 100–220 µF + RF decoupling
    USB-fed upstream)  │
                       └─────────────► +3V3 (buck or LDO)  ──┬─► MM8108 (I/O / main)
                                                             └─► NEO-M9N VCC

Header 3V3 (pins 1,17) ───────────────► 3V3_PI  (logic reference only — NOT a supply)
```

Everything is sourced from **header 5 V** as required. The Pi's own 3V3 rail is
deliberately **not** loaded (its regulator only has a small margin and powering
radios from it browns out the Pi).

## 2. Why buck-boost for the PA rail

- The whole stack is powered through the Pi's micro-USB **5 V**, which **sags**
  under the ~0.6–0.8 A TX burst of the E21 (cable + connector + Pi PMIC drop).
- A **buck-boost** holds **VPA** in regulation whether the input is momentarily
  above *or below* the target — exactly the case for a 5 V-in / 5 V-out PA rail
  during current transients. A plain buck would drop out as soon as 5V_in falls
  below VPA + headroom.
- Pair it with **bulk capacitance** at the E21 VCC to supply the fast TX edge and
  keep the rail flat (RF spectral purity depends on a clean PA supply).

> **Verify the E21 VCC target.** Per the EBYTE E21 series, VCC is in the
> **3.0–5.5 V** range with **5.0 V recommended** for full 30 dBm. Set the
> buck-boost output to the value the *current* E21-900G30S datasheet revision
> specifies for rated power. If the datasheet calls for a lower rail (e.g. 3.3 V),
> reprogram the feedback divider accordingly — the topology still applies.

## 3. Power budget (estimate — confirm against datasheets)

| Rail | Load | Typical | Peak | Notes (datasheet-confirmed) |
|------|------|--------:|-----:|-------|
| VPA (5.0 V) | E21 PA, TX | 620 mA | **660 mA** | at +30 dBm (E21 ds); RX ~8 mA |
| +3V3_RAD | MM8108 module, TX | — | **~330 mA** | VBAT_TX ≤281 mA + VBAT ~52 mA @3.3 V (Table 6) |
| +3V3_RAD | MM8108 module, RX | ~20–34 mA | — | active RX (Table 7) |
| +3V3 | NEO-M9N | ~30 mA | ~70 mA acq | + active-antenna via VCC_RF (≤200 mA) |
| +3V3 | RTC RV-3028 | <0.1 µA bkp | — | trickle-charges BT1 |
| —    | Pi Zero 2 W itself | 0.4–0.7 A | up to ~1.2 A | not on the HAT, but shares the upstream 5 V |

Worst-case HAT draw at the 5 V input (PA keyed + module TX) ≈ VPA path
(0.66 A·5 V/η ≈ 0.73 A from 5 V) + 3V3 loads (~0.4 A·3.3 V/η ≈ 0.3 A) ≈ **~1.0 A**,
on top of the Pi.

**Upstream 5 V sizing:** HAT loads (~1.0–1.2 A peak at the 5 V input when the PA
keys up, after buck-boost/LDO conversion) **plus** the Pi (~0.7–1.2 A) means the
external 5 V supply feeding the Pi should be a solid **≥ 3 A** source. Budget the
header/connector current: sustained PA + Pi can approach the practical limit of
the 0.1″ header power pins, so keep TX duty cycle in mind and use **both** 5 V
pins (2 and 4) and **multiple GND** pins in parallel.

## 4. Suggested regulators (starting points)

| Function | Candidate | Why |
|----------|-----------|-----|
| Buck-boost → VPA | **TI TPS63802** (≤ 2 A, Vout 1.8–5.2 V) or **TPS63070** (wider Vin, ≤ 2 A) | small, 5 V-in/5 V-out capable, good transient response |
| +3V3 (efficient) | **TI TLV62569 / AP63203** buck (~1–2 A) | efficient 5 V→3V3 for the radio |
| +3V3 (simple/quiet) | **AP2112-3.3 / TLV75533** LDO (≤ 0.6 A) | use only if 3V3 load fits LDO headroom/thermal |
| Antenna bias (GNSS) | inductor/ferrite + cap bias-tee off +3V3, with fuse/limit | for active GNSS antenna |

## 5. Decoupling / layout notes

- **VPA bulk** right at the E21 VCC pin(s): 100–220 µF (low-ESR) + 10 µF + 100 nF
  + small RF value (e.g. 10 nF/1 nF) fanned by frequency.
- Star/short return for the PA ground; keep the high-current TX loop tight.
- Separate quiet analog feed for the NEO-M9N (ferrite from +3V3) — GNSS is
  sensitive to switching-regulator noise. Place the GNSS LNA/antenna path away
  from the buck-boost switch node.
- Keep the buck-boost switch node small and shielded by ground pour; locate it
  away from both U.FL connectors and the 900 MHz / GNSS RF traces.
