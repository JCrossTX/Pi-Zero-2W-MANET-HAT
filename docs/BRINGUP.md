# Board Bring-Up & Test Plan

Stage-gated power-on so a fault in one block can't damage another (especially the
1 W PA). Do **not** key the PA until stages 1–4 pass.

## Stage 0 — Bare-board / pre-power
- [ ] Visual + DFM: no shorts on `+5V`/`VPA`/`+3V3` to `GND` (ohm-meter).
- [ ] Confirm 40-pin footprint aligns to a real Pi Zero 2 W (dry-fit, no power).
- [ ] Check bottom-side clearance vs the Pi's HDMI/USB/SD/camera/RF-can.

## Stage 1 — Power rails (HAT off the Pi, bench 5 V, current-limited ~0.3 A)
- [ ] Inject 5 V on the header `+5V`/`GND`. Confirm `VPA` = target (≈5.0 V, or per
      E21 datasheet) and `+3V3` = 3.30 V ±3%. Check ripple on `VPA` (< ~50 mV).
- [ ] `+3V3_GNSS` present after `FB1`. `3V3_PI` only present when fed by the Pi.
- [ ] Load-step `VPA` (electronic load 0→0.8 A) — bulk holds the rail; no dropout
      from the buck-boost. Validates [`POWER.md`](POWER.md) sizing.

## Stage 2 — Host detect & buses (HAT on the Pi)
- [ ] Pi boots with the HAT mounted; no brownout. Measure 5 V at the header under
      Pi+HAT idle.
- [ ] ID EEPROM reads at boot (`/proc/device-tree/hat/`), powered from `3V3_PI`.
- [ ] `i2cdetect` finds the EEPROM (0x50) and the NEO-M9N (if I²C enabled).
- [ ] SPI0 present; toggle `MM_RESET_N`/`MM_PWR1/2`, confirm GPIO levels.

## Stage 3 — GNSS
- [ ] Apply `manet-hat` overlay + `disable-bt`; `ttyAMA0` streams NMEA/UBX.
- [ ] U.FL #1 antenna (active): confirm `VCC_RF` bias present; get a fix; check
      C/N₀ on satellites.
- [ ] `pps-gpio` on GPIO18: `ppstest /dev/pps0` shows 1 Hz pulses; chrony locks.

## Stage 4 — HaLow radio (MM8108) over SPI
- [ ] Load the OpenMANET Morse driver against `spi0.0` (CS0/GPIO8, IRQ GPIO5,
      reset GPIO17, power GPIO23/24). Driver probes; firmware loads.
- [ ] `morsectrl`/iw shows the interface; scan/associate at **low power, internal
      path or dummy load** first if the part allows — do **not** rely on the E21
      yet.

## Stage 5 — RF front-end (E21) — **into a 50 Ω dummy load + power meter first**
- [ ] Confirm FEM control: `FEM_TX`/`FEM_RX` follow TX/RX bursts on a scope; both
      never high together (Shutdown at reset = both low). ([`RF.md`](RF.md) §2.1)
- [ ] **Drive level (B3):** measure MM8108 ext-FEM TX power into E21 `RFI`; verify
      it's in the E21 linear input window. Populate the attenuator pad `RN1` if
      over-driven *before* full-power TX.
- [ ] TX into dummy load: measure output ≈ +30 dBm; check spectrum (harmonics,
      spurs) and E21 temperature at duty.
- [ ] RX: confirm LNA path sensitivity improvement vs internal-only.

## Stage 6 — Antennas, coexistence, range
- [ ] Swap dummy load for U.FL #2 antenna (legal antenna/power for region —
      [`RF.md`](RF.md) §5).
- [ ] **Coexistence (B6):** key the PA at full power; re-check GNSS C/N₀ and fix.
      If GNSS desenses, populate the GNSS pre-filter `FL1` / improve isolation.
- [ ] OpenMANET mesh: two nodes associate; throughput + range vs link budget.

## Instruments
Bench PSU (current limit), DMM, scope (≥100 MHz), spectrum analyzer + 50 Ω
attenuated tap / power meter, 50 Ω dummy load, GNSS antenna, thermal camera/probe.

## Cross-refs
Risks driving these checks: [`DECISIONS.md`](DECISIONS.md) B2/B3/B5/B6/B9.
