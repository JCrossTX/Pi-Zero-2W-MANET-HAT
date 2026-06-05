# Board Bring-Up & Test Plan

Stage-gated power-on so a fault in one block can't damage another. The external
1 W PA is retired (B11) — the radio module integrates its own PA.

## Stage 0 — Bare-board / pre-power
- [ ] Visual + DFM: no shorts on `+5V`/`+3V3` to `GND` (ohm-meter).
- [ ] Confirm 40-pin footprint aligns to a real Pi Zero 2 W (dry-fit, no power).
- [ ] Check bottom-side clearance vs the Pi's HDMI/USB/SD/camera/RF-can.

## Stage 1 — Power rails (HAT off the Pi, bench 5 V, current-limited ~0.3 A)
- [ ] Inject 5 V on the header `+5V`/`GND`. Confirm `+3V3` = 3.30 V ±3% after the
      inrush switch. Check ripple. (No `VPA`/buck-boost — E21 retired.)
- [ ] `+3V3_GNSS` present after `FB1`. `3V3_PI` only present when fed by the Pi.
- [ ] Load-step `+3V3` (electronic load to the radio's TX peak) — bulk holds the
      rail; no buck dropout. Validates [`POWER.md`](POWER.md) sizing. (Confirm the
      M20 TX current target once its datasheet lands, B12.)

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

## Stage 4 — HaLow radio (MM8108 module) over SPI
- [ ] Load the Morse driver against `spi0.0` (CS0/GPIO8, IRQ GPIO5, reset GPIO17,
      power GPIO23/24). Driver probes; firmware + **BCF** load (MF15457:
      `bcf_mf15457`; M20: its own BCF — B11).
- [ ] `morsectrl`/iw shows the interface; scan/associate into a **50 Ω dummy load**
      on U.FL #2 first.

## Stage 5 — RF output / antenna — **into a 50 Ω dummy load + power meter first**
- [ ] TX into dummy load: measure output ≈ **27 dBm (MF15457)** / **~28.5 dBm (M20)**
      at the U.FL; check spectrum (harmonics, spurs) and module temperature at duty.
- [ ] If MF15457 harmonics are marginal, populate the optional `FL2` LPF and re-check.
- [ ] RX: confirm sensitivity meets the datasheet at representative MCS.

## Stage 6 — Antennas, coexistence, range
- [ ] Swap dummy load for U.FL #2 antenna (legal antenna/power for 902–928 region —
      [`RF.md`](RF.md) §5).
- [ ] **Coexistence (B6):** key the radio at full power; re-check GNSS C/N₀ and fix.
      If GNSS desenses, populate the GNSS pre-filter `FL1` / improve isolation.
- [ ] OpenMANET mesh: two nodes associate; throughput + range vs link budget.

## Instruments
Bench PSU (current limit), DMM, scope (≥100 MHz), spectrum analyzer + 50 Ω
attenuated tap / power meter, 50 Ω dummy load, GNSS antenna, thermal camera/probe.

## Cross-refs
Risks driving these checks: [`DECISIONS.md`](DECISIONS.md) B6/B9/B11/B12.
