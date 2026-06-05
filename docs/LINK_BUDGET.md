# Range & Throughput Analysis — by TX power / data rate

Quantifies range vs TX power using the **MM8108-MF15457** datasheet
rate/sensitivity/TX tables. The external E21 columns are retained as the analysis
that **led to retiring it** (B11); the **chosen radio is now the MM8108-M20** at
~28.5 dBm — see §8 and [`MODULE_OPTIONS.md`](MODULE_OPTIONS.md).

## 1. Assumptions
- Band 915 MHz. Antennas **Gt = Gr = 2 dBi** (small whip/U.FL). **Fade margin
  10 dB.** Symmetric link (both nodes identical).
- Path-loss models:
  - **Free space (n=2)** — `PL = 91.66 + 20·log10(d_km)` — only for true LoS
    (elevated/aerial nodes, clear Fresnel). Optimistic upper bound.
  - **Realistic (n=3.5)**, d0=100 m — `PL = 71.66 + 35·log10(d/0.1km)` —
    ground-level/foliage/suburban. Use this for handheld/vehicle MANET.
- Max allowable path loss: `MAPL = Pt + Gt + Gr − margin − RxSens = Pt − 6 + |RxSens|`.
- Range: `d(km) = 0.1 × 10^((MAPL − 71.66)/35)` (n=3.5); `10^((MAPL−91.66)/20)` (FS).

## 2. Inputs from the MM8108-MF15457 datasheet
RX sensitivity (10% PER, dBm) and PHY rate (Mbps), 1 SS:

| MCS | 1 MHz | 2 MHz | 4 MHz | 8 MHz |
|----|-------|-------|-------|-------|
| 0  | 0.3 / −106 | 0.7 / −103 | 1.5 / −102 | 3.3 / −98 |
| 4  | 2.0 / −96  | 4.3 / −93  | 9.0 / −90  | 20 / −87 |
| 7  | 3.3 / −89  | 7.2 / −86  | 15 / −83   | 33 / −80 |
| 9  | 4.4 / −83  | —          | 20 / −78   | **43 / −74** |

**TX power at the module ANT (Table 12) is NOT flat** — high-order QAM backs off
for linearity: MCS0/1 MHz = **+25.5 dBm**, but MCS9/8 MHz = **only +16 dBm**.
- **Module (IEEE default):** Table 12 values.
- **Module + OpenMANET BCF:** ~**+27 dBm** for robust low MCS; still backs off at
  MCS8/9 (256-QAM is EVM/linearity-limited, not power-limited).
- **Module + E21:** ~**+30 dBm** for robust MCS; at 256-QAM the E21 must also back
  off (~+22–24 dBm best case) or EVM collapses — so the PA mostly helps **low-MCS,
  long-range** modes, *not* peak throughput.

## 3. Range by operating point (realistic n=3.5)

| Mode (rate) | Sens | Module IEEE | +BCF ~27 | +E21 ~30 | BCF→E21 |
|-------------|------|-------------|----------|----------|---------|
| MCS0 1 MHz (**0.3 Mbps**, max range) | −106 | +25.5→**3.45 km** | **3.81 km** | **4.65 km** | **+22 %** |
| MCS0 8 MHz (3.3 Mbps) | −98 | +22.5→1.68 km | 2.25 km | 2.74 km | +22 % |
| MCS4 2 MHz (4.3 Mbps) | −93 | +24.5→1.45 km | 1.62 km | 1.97 km | +22 % |
| MCS7 8 MHz (33 Mbps)  | −80 | +20→0.44 km | ~0.60 km | ~0.90 km* | +50 %* |
| MCS9 8 MHz (**43 Mbps**, max rate) | −74 | +16→0.26 km | ~0.26 km | ~0.38 km* | marginal* |

\* high-MCS rows assume the PA holds EVM at reduced backoff — **optimistic and
risky** (256-QAM). Treat MCS7–9 PA gains as best-case, not expected.

## 4. Same data, free-space (LoS / aerial upper bound)
MCS0 1 MHz: IEEE +25.5 → **49 km**, +BCF 27 → **58 km**, +E21 30 → **83 km**
(+41 % BCF→E21). Free space turns every +3 dB into **×1.41 range**; n=3.5 only
**×1.22**; n=4 **×1.19**.

## 5. Throughput view (at a fixed distance)
Each MCS step in the mid-table ≈ ~3 dB of sensitivity. So **+3 dB (E21 over BCF) ≈
one MCS step** at a given range — i.e. roughly **+40–100 % instantaneous PHY rate**
right at the edge of a given link, *but only in the SNR-limited middle of the
curve*. It does nothing once you're already at max MCS (close in) or floored at
MCS0 (far out).

## 6. The RX side (the uncertain half)
Symmetric link margin = ΔTX(one end) + ΔRX-sensitivity(other end).
- **E21 TX:** +3 dB vs BCF (robust MCS) — reliable.
- **E21 LNA RX:** datasheet claims +3 dB sensitivity, **but** the module already
  has an LNA, and a real MM8108+external-PA build reported a **low-RX-rate
  regression** ([`FIRMWARE_PA.md`](FIRMWARE_PA.md)). So RX gain is **0 to +3 dB,
  uncertain, with downside risk**.
- **Best case** (TX+RX both deliver, +6 dB): n=3.5 **×1.48 (+48 %)**, FS ×2.0.
- **Expected** (TX only, +3 dB): n=3.5 **×1.22 (+22 %)**, FS ×1.41.
- **Downside:** RX throughput *regresses* (documented) — net-negative.

## 7. Bottom line
| | Module alone (OpenMANET BCF) | + E21 |
|--|------------------------------|-------|
| TX power (robust) | ~27 dBm | ~30 dBm (+3 dB) |
| Peak throughput | 43 Mbps @ 8 MHz | **same** (PA backs off at 256-QAM) |
| Range, realistic n=3.5 | baseline | **+20–25 %** (TX), up to +48 % if RX LNA delivers |
| Range, LoS/aerial | baseline | **+40 %** (TX), up to +100 % if RX LNA delivers |
| Cost | — | ~620 mA+heat, board area, **recert**, custom-BCF T/R, RX-rate risk |

**Where the E21 is worth it:** long-range **LoS/elevated** nodes (aerial, masts)
running **robust low-MCS** links — there the +3 dB → +40 % range (and the LoS
multiplier compounds). **Where it isn't:** short-range or **high-throughput**
(256-QAM backs off) or dense NLOS clutter (n≈4 → only +19 %), where the ~3 dB is
swamped by environment and the RX/cert/thermal costs dominate.

The single biggest *free* win is already the **OpenMANET BCF (~27 dBm)** — that's
+2–5 dB over the IEEE default at no hardware cost. The E21 was the expensive,
conditional last +3 dB.

## 8. Chosen radio: MM8108-M20 (~28.5 dBm, integrated + certified)
The M20 reaches **28.5 dBm** — about **+1.5 dB over the BCF ~27 dBm** baseline and
only **~1.5 dB below** the old +30 dBm E21 plan — but as a single **FCC/IC-certified
integrated module** with none of the E21's RX-rate risk, ~620 mA PA draw, heat,
recert, or T/R-control burden.

| | MF15457 (BCF ~27) | **MM8108-M20 ~28.5** | (retired) +E21 ~30 |
|--|-------------------|----------------------|--------------------|
| Range vs BCF, n=3.5 | baseline | **+~10 %** (TX, robust MCS) | +20–25 % |
| Range vs BCF, LoS | baseline | **+~18 %** | +40 % |
| RX side | baseline | **no regression** (integrated) | 0…+3 dB, **risk** |
| Cost | — | certified module, simpler board | recert, T/R, heat, RX risk |

So the M20 captures most of the realistic NLOS range benefit the E21 promised,
without the downside that made the E21 not worth populating by default. The
MF15457 remains the buildable-today fallback at ~27 dBm.
