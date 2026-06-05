# Component Gap Analysis (datasheet-grounded)

Resolves "what other components does this PCB need." Now grounded in the
datasheets in [`../hardware/`](../hardware/): **MM8108-MF15457** module,
**E21-900G30S**, **NEO-M9N-00B**. Status as of this revision.

## Headline finding — the high-power module removes the PA front-end

**Decision B11:** the radio is now a **single integrated MM8108 module** — primary
**MM8108-M20** (integrated 28.5 dBm PA + 902–928 SAW, FCC/IC certified), fallback
**MM8108-MF15457** (~27 dBm). The **external E21 PA and its whole support
ecosystem are retired**. Full comparison: [`MODULE_OPTIONS.md`](MODULE_OPTIONS.md).

`MM8108-MF15457` (the buildable-today baseline) is a **self-contained, FCC/IC-certified module**:
- Only needs **VBAT 3.0–3.6 V**, **VBAT_TX 3.0–3.6 V**, **VDDIO 2.25–3.6 V** —
  **no external SoC inductors, no 1.8 V/1.2 V rails, no external TCXO** (clock is
  internal). "No strict power-up sequencing requirements."
- Exposes a **single `ANT` pin (pin 2)** after its internal PA → straight to U.FL.
- Module TX output at ANT ≈ **+22 to +25.5 dBm** IEEE (Table 12); ~27 dBm via the
  OpenMANET BCF.

**What the E21 retirement removes** (vs the earlier plan): the drive-pad attenuator,
the 5 V buck-boost / `VPA` rail, the harmonic-LPF requirement, the unsolved T/R
control, the RF-sense VOX fallback, and the +30 dBm recertification. The M20 gets
~the same range as the +30 dBm E21 plan as a single certified part.

**M20 caveat:** no datasheet yet — its exact rails/current, footprint and any PA
pin are **TBD (B12)**; treat the radio supply as "MF15457 baseline + headroom"
until Morse publishes.

---

## Necessary (#1–#4)

| # | Need | Status / decision | Parts to add |
|---|------|-------------------|--------------|
| N1 | MM8108 power rails | **Resolved by module** — feed VBAT, VBAT_TX, VDDIO from +3V3. No SoC inductors/extra rails. M20 PA current TBD (B12). | per-pin decoupling (10 µF + 100 nF); bulk at the module for the TX burst (more for M20) |
| N2 | Reference clock | **Resolved by module** (internal). | none |
| N3 | 900 MHz harmonic filter | M20 integrates a **902–928 SAW**; MF15457 is modular-certified. | **FL2** optional π-LC LPF (DNP) — MF15457 only, populate per measured harmonics |
| N4 | Inrush soft-start | Bulk-cap inrush at plug-in can brown out the Pi. | **U10** soft-start load switch (TPS22965) on +5V → 3V3 buck in. *(E21 T/R control deleted with B11.)* |

## Recommended (#5–#10, all approved)

| # | Item | Parts |
|---|------|-------|
| N5 | Reset/voltage supervisor | **U11** TPS3839 (3.3 V) → wired-AND with Pi GPIO17 into module RESET_N; respects t0≥50 µs / t1≥1000 µs (Tables 1–2) |
| N6 | Radio-rail load switch (OpenMANET `power-gpios`) | **U12** TPS22918/TPS22965 gating module 3.3 V, EN = MM_PWR1 (GPIO23); WAKE = MM_PWR2 (GPIO24) |
| N7 | RF shield cans | shield frame + lid over the radio and/or GNSS (EMC + radio↔GNSS isolation) |
| N8 | GNSS antenna ESD | **D8** low-C TVS on RF_GNSS at U.FL #1 |
| N9 | Status LEDs | **D_PWR** (3V3 good), **D_TX** (host GPIO, TX activity), **D_FIX** (GNSS, Pi GPIO12) + 1 kΩ resistors |
| N10 | Radio thermal relief | copper pour + thermal via array under the module (M20 integrated PA dissipation); optional heatsink |

## Added by request — RTC with soldered backup cell

| Ref | Part | Notes |
|-----|------|-------|
| U13 | **RV-3028-C7** I²C RTC (addr 0x52) | 45 nA backup, ±1/5 ppm, **built-in trickle charger** — pairs perfectly with a soldered rechargeable cell so it never needs replacing. Alt: DS3231M/SN (0x68, internal TCXO). |
| BT1 | **Seiko MS621FE** (or Panasonic ML414H/ML621) rechargeable 3 V Mn-Li, **solder-tab** | trickle-charged from +3V3 via the RV-3028 charger; PCB-soldered per request |
| — | RTC: SDA/SCL on **I²C1** (shared w/ GNSS DDC, no addr clash); INT/CLKOUT → Pi **GPIO26 (pin 37)**; VCC = +3V3; backup = BT1 | overlay: `dtoverlay=i2c-rtc,rv3028` |

> RTC role: holdover time when GNSS has no fix / system is dark; the GNSS **1 PPS**
> can discipline it. GNSS supplies fix-derived time when locked.

## Explicitly NOT added
- **External E21 PA + buck-boost + T/R + drive pad** — retired (B11).
- **Debug UART pads / JTAG header** — declined (module JTAG pins 6–9 left N/C).
- **Test points** — declined.
- **Level shifters** — not needed; Pi, module (VDDIO=3.3 V), GNSS, RTC all 3.3 V.
- **USB components** — USB-A port dropped earlier.

## Open confirmations
- **MM8108-M20 datasheet (B12):** pinout, supply rails/voltage, TX current, exact
  footprint, and whether any extra rail/decoupling is needed. Finalizes `U1`.
- **M20 sourcing:** confirm `MM8108-M20-US` is obtainable (sampling to certified
  partners). If not, build the **MF15457 fallback** now.
- **OpenMANET M20 support:** the M20 needs its own **BCF** (MF15457 BCF runs the
  fallback today). SPI driver path is the same MM8108 stack.
