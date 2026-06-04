# Component Gap Analysis (datasheet-grounded)

Resolves "what other components does this PCB need." Now grounded in the
datasheets in [`../hardware/`](../hardware/): **MM8108-MF15457** module,
**E21-900G30S**, **NEO-M9N-00B**. Status as of this revision.

## Headline finding — the module changes the PA story

`MM8108-MF15457` is a **self-contained, FCC/IC-certified module**:
- Only needs **VBAT 3.0–3.6 V**, **VBAT_TX 3.0–3.6 V**, **VDDIO 2.25–3.6 V** —
  **no external SoC inductors, no 1.8 V/1.2 V rails, no external TCXO** (clock is
  internal). "No strict power-up sequencing requirements."
- Exposes a **single `ANT` pin (pin 2)** that is **after** its internal PA. There
  is **no pre-PA tap / external-FEM RF port** and **no hardware TX/RX FEM-control
  output** on the module pinout.
- Module TX output at ANT ≈ **+22 to +25.5 dBm** (per BW/MCS, Table 12).

The E21-900G30S wants **~+20 dBm drive → +30 dBm out (12 dB gain)**, **VCC 5.0 V
(4.75–5.25)**, **~620 mA TX**, **TX_EN/RX_EN at 3.3 V**, pin 6 `PIN` =
transceiver side, pin 9 `ANT` = antenna side.

**Consequences for the external E21 PA (see [`DECISIONS.md`](DECISIONS.md) B2/B3/B5):**
1. **Drive level:** module +22…+25.5 dBm vs E21's +20 dBm target → add a **small
   fixed pad (~3–5 dB)** between module ANT and E21 `PIN` to land near +20 dBm and
   stay below the hottest-case input. (Less than first feared — they nearly match.)
2. **T/R control:** the module gives **no hardware T/R line**, so E21 `TX_EN`/`RX_EN`
   must be driven by **either** (a) two **module GPIOs** toggled by **OpenMANET
   firmware** as a PA-enable/T-R indicator (cleanest — confirm OpenMANET supports
   a PA-control GPIO; Morse GPIO alt-functions need custom FW), **or** (b) an
   on-board **RF-sense auto-T/R** (VOX) circuit, **or** (c) Pi GPIO (too slow for
   per-burst TDD — bring-up only).
3. **Net benefit is modest:** +22…25 → +30 dBm is only ~**+5 to +8 dB** of system
   gain for ~3 W of extra DC. Worth it for the +30 dBm/1 W reach target, but know
   the trade.
4. **Certification:** bolting a PA after the certified module **voids its FCC/IC
   modular approval** → the end product needs **recertification** at +30 dBm.

> If the OpenMANET firmware cannot drive a module-GPIO PA-enable, the realistic
> path is the **RF-sense auto-T/R** circuit (item N4 below).

---

## Necessary (#1–#4)

| # | Need | Status / decision | Parts to add |
|---|------|-------------------|--------------|
| N1 | MM8108 power rails | **Resolved by module** — feed VBAT, VBAT_TX, VDDIO from +3V3. No SoC inductors/extra rails. | per-pin decoupling only (10 µF + 100 nF on VBAT/VBAT_TX/VDDIO); bulk on VBAT_TX for its ~330 mA TX burst |
| N2 | Reference clock | **Resolved by module** (internal). | none |
| N3 | 900 MHz harmonic filter (1 W) | E21 has a **built-in filter/limiter**, but +30 dBm end-product compliance may still need more. | **FL2** π-LC low-pass or 915 MHz ceramic BPF between E21 `ANT` and U.FL #2 — populate per measured harmonics |
| N4 | Inrush + E21 T/R control | Inrush from VPA bulk can brown out the Pi; module has no T/R line. | **U10** soft-start load switch (TPS22965) on +5V→buck-boost in; **PA T/R source**: route 2 module GPIOs → E21 TX_EN/RX_EN (preferred) **or** auto-T/R: directional coupler + RF detector (LTC5564/ADL6010) + comparator driving TX_EN/RX_EN |

## Recommended (#5–#10, all approved)

| # | Item | Parts |
|---|------|-------|
| N5 | Reset/voltage supervisor | **U11** TPS3839 (3.3 V) → wired-AND with Pi GPIO17 into module RESET_N; respects t0≥50 µs / t1≥1000 µs (Tables 1–2) |
| N6 | Radio-rail load switch (OpenMANET `power-gpios`) | **U12** TPS22918/TPS22965 gating module 3.3 V, EN = MM_PWR1 (GPIO23); WAKE = MM_PWR2 (GPIO24) |
| N7 | RF shield cans | shield frame + lid over PA section and/or module (EMC + PA↔GNSS isolation) |
| N8 | GNSS antenna ESD | **D8** low-C TVS on RF_GNSS at U.FL #1 |
| N9 | Status LEDs | **D_PWR** (3V3 good), **D_TX** (off E21 TX_EN), **D_FIX** (GNSS, Pi GPIO12) + 1 kΩ resistors |
| N10 | E21 thermal relief | copper pour + thermal via array under E21 (~1.5–2 W); optional clip heatsink |

## Added by request — RTC with soldered backup cell

| Ref | Part | Notes |
|-----|------|-------|
| U13 | **RV-3028-C7** I²C RTC (addr 0x52) | 45 nA backup, ±1/5 ppm, **built-in trickle charger** — pairs perfectly with a soldered rechargeable cell so it never needs replacing. Alt: DS3231M/SN (0x68, internal TCXO). |
| BT1 | **Seiko MS621FE** (or Panasonic ML414H/ML621) rechargeable 3 V Mn-Li, **solder-tab** | trickle-charged from +3V3 via the RV-3028 charger; PCB-soldered per request |
| — | RTC: SDA/SCL on **I²C1** (shared w/ GNSS DDC, no addr clash); INT/CLKOUT → Pi **GPIO26 (pin 37)**; VCC = +3V3; backup = BT1 | overlay: `dtoverlay=i2c-rtc,rv3028` |

> RTC role: holdover time when GNSS has no fix / system is dark; the GNSS **1 PPS**
> can discipline it. GNSS supplies fix-derived time when locked.

## Explicitly NOT added
- **Debug UART pads / JTAG header** — declined (module JTAG pins 6–9 left N/C).
- **Test points** — declined.
- **Level shifters** — not needed; Pi, module (VDDIO=3.3 V), GNSS, RTC all 3.3 V.
- **USB components** — USB-A port dropped earlier.

## Open confirmations
- Does **OpenMANET firmware** expose a module-GPIO **PA-enable / T-R** signal? If
  yes → N4 option (a); if no → build N4 auto-T/R (b). (Drives the whole PA sheet.)
- Final **VPA = 5.0 V** (confirmed by E21) — set buck-boost FB accordingly.
- Harmonic margin at +30 dBm → whether **FL2** is LC vs ceramic BPF.
