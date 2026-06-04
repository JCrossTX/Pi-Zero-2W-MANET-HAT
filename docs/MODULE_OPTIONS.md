# HaLow Module Options — MF15457 vs MF15457+E21 vs MM8108-M20

Comparison of the three ways to hit "long range" for this HAT. Triggered by the
**MM8108-M20** announcement (2026-06-01). **No M20 datasheet yet** — figures below
are from the press release/coverage and are provisional.

## Side-by-side

| | **A. MF15457 only** (current default) | **B. MF15457 + E21** (Variant B) | **C. MM8108-M20** |
|--|--------------------------------------|----------------------------------|-------------------|
| TX power | ~22–25 dBm IEEE; **~27 dBm** OpenMANET BCF | **~30 dBm** | **~28.5 dBm** (integrated PA) |
| PA | module internal | + external EBYTE E21 | **integrated, vendor-characterized** |
| Harmonic filter | (module) | external LPF needed | **integrated SAW (902–928)** |
| T/R control | n/a | **custom BCF GPIO, not turnkey; RX-rate risk** | **handled in module** |
| Certification | module modular cert | **end-product RECERT at +30 dBm** | **FCC/IC certified** |
| Host | SPI (OpenMANET today) | SPI | SPI / SDIO / USB |
| Size (HaLow+PA) | small module | module **+ E21 27.5×18 mm** + buck-boost + LPF | **one 18.5×14 mm module** |
| Extra power rail | no | **5 V buck-boost, ~620 mA TX** | likely none (PA at module rail) — TBD |
| Band | 850–950 | 850–931 (E21) | **902–928 only (US/Canada)** |
| Availability | available | available | **sampling to certified partners only** |
| OpenMANET support | **yes** (bcf_mf15457) | needs custom BCF | **needs M20 BCF/config (likely not yet)** |

## What the M20 changes
It delivers **~the same power as the E21 path (28.5 vs 30 dBm — only 1.5 dB less)**
as a **single certified module**, and it **eliminates**: the external E21, the
5 V buck-boost + bulk, the harmonic LPF, the unsolved T/R-control problem, the
RX-rate regression risk, the recertification burden, and the largest part on the
board. Net: simpler, smaller, cooler, certified, and ~33 % more range than a
26 dBm baseline (per Morse) — i.e. it makes **Variant B (E21) obsolete**.

## Open risks before committing to the M20
1. **No datasheet** — pinout, supply rails/current, exact footprint, and SPI
   control lines are unknown. Can't finalize the HaLow/power schematic until it
   publishes.
2. **Availability** — "sampling to **certified module partners**" suggests it is
   not yet generally purchasable; confirm you can actually obtain `MM8108-M20-US`.
3. **OpenMANET support** — OpenMANET targets `MF15457` today; the M20 needs its
   own BCF + config. Likely requires upstream/your work until OpenMANET adds it.
   SPI driver path should otherwise be the same MM8108 stack.
4. **Band** — `-US` is **902–928 only**. Fine for US/Canada MANET; wrong part if
   EU 863–868 / other regions are needed.

## Recommendation
For this project's **ground/handheld/vehicle, US-band** target, the **M20 is the
better architecture** — it gets essentially the same range as the E21 plan with
none of the integration, power, thermal, or certification pain, on a smaller
board. Pending: (a) datasheet, (b) you can source it, (c) OpenMANET M20 BCF.

Pragmatic path: **design the board M20-primary** (drop the E21/buck-boost/LPF
path), but keep the layout able to fall back to MF15457 if sourcing/firmware slip.
