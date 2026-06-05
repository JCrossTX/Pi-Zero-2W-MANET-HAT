# OpenMANET / Morse Firmware — PA / BCF Findings

Investigation of whether the OpenMANET / Morse Micro firmware can drive an
external E21 PA's TX/RX (FEM) switching for the **MM8108-MF15457** module.

> **Outcome (B11):** these findings — uncertain external-FEM support + a documented
> RX-rate regression — are a big reason the **external E21 was retired** in favour
> of the integrated **MM8108-M20** (which does its own T/R internally). See §"M20
> firmware" below and [`MODULE_OPTIONS.md`](MODULE_OPTIONS.md).

## How GPIO/FEM function is set
- Morse chip GPIO functions are **not fixed** — they're defined by the **firmware
  build + Board Configuration File (BCF)**. BCFs live in `morse-firmware/bcf/`
  (`bcf/morsemicro` for reference designs + partner subdirs). The MF15457 module
  uses `bcf_mf15457.mbin` with `mm8108b2-rl.mbin` firmware and
  `CONFIG_MMHAL_CHIP_TYPE_MM8108=y`.
- The MM8108 **SoC** officially supports an external PCB-mount PA/FEM ("for
  ultra-long-reach"). So the silicon can do it.

## What OpenMANET actually ships today
- A **custom BCF that raises the module's _internal_ PA from ~21 dBm (Seeed
  default) to ~27 dBm.** This is **TX-power tuning of the module's own PA** — it is
  **not** external-PA T/R control. No public evidence OpenMANET currently toggles
  an external PA via GPIO.

## State of external-FEM support on MF15457 (the caveats)
- Community thread *"MM8108-MF15457 TXRX RF Switch signal"* asks exactly how to
  map/duplicate the module's internal TX/RX switch signal to a GPIO. The takeaway:
  Morse indicated a **separate MM8108 variant for external FEM** was planned →
  i.e. the **current MF15457 does not cleanly expose a turnkey FEM-control GPIO**;
  doing it needs custom BCF/firmware work.
- Community thread *"MM8108 + External PA (GRF5509)"*: a builder put an external
  PA on the TX path and hit a **documented RX problem** — receiving nodes see high
  RSSI from the PA node but the **RX data rate stays unexpectedly low**. A real
  integration pitfall for MM8108 + external PA.

## Conclusion
**Half-covered.** ✅ Boosting TX power via BCF is a solved, shipping OpenMANET
feature — and it already reaches **~27 dBm from the bare module, no external PA**.
⚠️ Driving an **external** PA's T/R from a module GPIO is **not** a clean,
supported feature on MF15457 today; it requires custom BCF/firmware and has a
known RX-rate gotcha.

## Why this matters for the board
The E21 gives **+30 dBm**; OpenMANET's BCF already gives **~27 dBm** from the
module alone. The external PA therefore adds only **~3 dB (~1.4× range)** while
adding: uncertain/custom T/R-control support, a documented RX-rate regression
risk, ~620 mA + heat, board area, and **FCC/IC recertification**. The trade was
marginal — and the project **retired the E21** for the integrated M20 (B11).

## M20 firmware (the new primary)
The **MM8108-M20** integrates the PA and its T/R, so **none of the external-FEM
problems above apply** — no GPIO T/R mapping, no RX-rate gotcha. It is the same
MM8108 SPI silicon, so the OpenMANET driver/overlay path is unchanged, **but it
needs its own BCF** characterizing the integrated PA. Open items:
- Confirm an **M20 BCF** exists (`bcf_*` for the M20) or that Morse supplies one to
  certified partners; OpenMANET M20 support may need to be added upstream.
- Until then, the **MF15457 fallback runs OpenMANET today** (`bcf_mf15457.mbin`).

## Sources
- OpenMANET firmware & docs: https://github.com/OpenMANET/firmware ,
  https://openmanet.github.io/docs/ , https://github.com/OpenMANET/morse-feed
- Morse firmware BCF dir: https://github.com/MorseMicro/morse-firmware
- Threads: https://community.morsemicro.com/t/mm8108-mf15457-txrx-rf-switch-signal/946 ,
  https://community.morsemicro.com/t/external-amplification-mm8108/1629 ,
  https://community.morsemicro.com/t/request-for-support-low-rx-tx-rate-issue-with-mm8108-external-pa-e-g-grf5509/1319
- MF15457 Hardware Design Guide:
  https://www.morsemicro.com/resources/design_packages/MM8108-MF15457_Hardware_Design_Guide.pdf
