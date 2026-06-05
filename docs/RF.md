# RF Chain, Front-End Switching & Antennas

## 1. Two independent RF chains

| Chain | Frequency | Path |
|-------|-----------|------|
| HaLow data | 902–928 MHz (sub-GHz ISM) | MM8108 module `ANT` ⇄ **U.FL #2** |
| GNSS | 1.16–1.61 GHz (L1/L2/L5 bands) | **U.FL #1** ⇄ NEO-M9N |

Both U.FL connectors are **surface-mount**, placed at the board edge for short RF
runs and easy pigtail routing.

## 2. 900 MHz HaLow chain (integrated-PA module)

```
MM8108 module ANT (50Ω, post-internal-PA) ──► RF_900 ──► C35 DC-block
   ──► [FL2 LPF, DNP] ──► ANT_900 (50Ω) ──► U.FL #2 ──► antenna
```

- The **external E21 PA is retired** (B11). Both module options drive the antenna
  directly: the **MM8108-M20** has an integrated PA (~28.5 dBm) + a 902–928 SAW;
  the **MF15457** outputs ~27 dBm from its internal PA. So this chain is a clean
  50 Ω hand-off — no FEM, no drive pad, no T/R control.
- Keep `RF_900`/`ANT_900` (module `ANT` → U.FL) as **50 Ω controlled-impedance**
  microstrip, as short as possible, with ground stitching either side.
- `FL2` is an **optional DNP** harmonic LPF land for the MF15457 path; populate only
  if measured harmonics need it. The M20's integrated SAW makes it unnecessary.

### 2.1 T/R switching — not applicable
The integrated modules handle their own TX/RX switching internally; there are no
`TXEN`/`RXEN` lines to drive and no external T/R interlock (all retired with the
E21).

## 3. GNSS chain (NEO-M9N)

- `U.FL #1` → optional **antenna bias-tee** → NEO-M9N `RF_IN`.
- Supports **passive** or **active** antennas:
  - Active: feed antenna DC through a bias inductor/ferrite from **+3V3** (or a
    dedicated `V_ANT`) with a series limit/fuse and the u-blox open/short
    detection circuit (optional).
  - Passive: no bias; just AC-couple to `RF_IN`.
- NEO-M9N has an internal SAW + LNA; keep its RF input trace short and clear of
  the 3V3 buck switch node and the 900 MHz radio. The radio's 900 MHz fundamental
  and harmonics must not desensitise the GNSS front-end — physical separation +
  ground fencing + the module's own filtering help; add a GNSS pre-filter if
  isolation is marginal.

## 4. Coexistence & isolation

- The 900 MHz radio (~27–28.5 dBm) and the GNSS receiver share a 65 × 30 mm board —
  **isolation is the hard part.** Mitigations:
  - Place the two U.FL connectors on **opposite ends** of the board.
  - Keep the GNSS LNA/trace far from the radio output and the 3V3 buck.
  - Ground pour + via fencing between the 900 MHz section and the GNSS section.
  - Consider a SAW/bandpass on the GNSS input if radio leakage degrades C/N₀.
- The Pi Zero 2 W's own 2.4 GHz Wi-Fi/BT chip antenna is on the Pi; the HAT RF
  sections should avoid sitting directly over it where practical.

## 5. Antenna selection

| Port | Band | Antenna |
|------|------|---------|
| U.FL #2 | 902–928 MHz | 915 MHz whip or external via U.FL→SMA pigtail (M20-US is US/Canada band) |
| U.FL #1 | GNSS L1 (1575 MHz) | active GNSS patch/whip (recommended) or passive |

> **Regulatory:** the **MM8108-M20 is FCC/IC certified** as a module — operate it
> within its certified conditions (approved antenna / gain) and the end-product
> burden is far lighter than the old +30 dBm external-PA path, which required full
> recertification. The MF15457 fallback is likewise modular-certified. Still confirm
> the antenna-gain / EIRP combination is legal for 902–928 MHz (FCC Part 15.247)
> in the target region.
