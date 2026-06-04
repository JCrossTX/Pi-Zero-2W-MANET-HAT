# RF Chain, Front-End Switching & Antennas

## 1. Two independent RF chains

| Chain | Frequency | Path |
|-------|-----------|------|
| HaLow data | ~850–950 MHz (sub-GHz ISM) | MM8108 ⇄ E21-900G30S ⇄ **U.FL #2** |
| GNSS | 1.16–1.61 GHz (L1/L2/L5 bands) | **U.FL #1** ⇄ NEO-M9N |

Both U.FL connectors are **surface-mount**, placed at the board edge for short RF
runs and easy pigtail routing.

## 2. 900 MHz HaLow chain with external PA

```
                 TX  ─────────────────────────────►
MM8108 RF(FEM) ──► RF_900 (50Ω) ──► E21 RFI ─┤PA├─┐
   ▲                                          T/R ├─► E21 RFO ──► ANT_900 (50Ω) ──► U.FL #2 ──► antenna
   └───────────────────────────── E21 RFO ─┤LNA├─┘
                 RX  ◄─────────────────────────────
```

- The MM8108's RF port is configured for an **external front-end module (FEM)** so
  the **E21 provides the +30 dBm TX power and the RX LNA gain** — the chip's
  internal PA is *not* used into the E21.
- **Drive level matters.** The E21 expects a low-level transceiver drive (order of
  0…+10 dBm) to produce 30 dBm out. The MM8108 external-FEM TX output must sit in
  the E21's linear input window. **Verify the MM8108 ext-FEM output power vs. the
  E21 RFI input spec and add a small fixed pad (attenuator) if needed** to avoid
  saturating/over-driving the PA. This is the single most important RF bring-up
  check — see [`DECISIONS.md`](DECISIONS.md).
- Keep `RF_900` (MM8108↔E21) and `ANT_900` (E21↔U.FL) as **50 Ω controlled
  impedance** microstrip, as short as possible, with ground stitching either side.

### 2.1 T/R (FEM) switching

E21 control truth table (3.3 V logic):

| Mode    | TXEN | RXEN |
|---------|:----:|:----:|
| Transmit| 1    | 0    |
| Receive | 0    | 1    |
| Shutdown| 0    | 0    |
| **Invalid** | 1 | 1   | do not assert both |

- Drive `E21.TXEN`/`E21.RXEN` from the **MM8108 FEM-control outputs** (`FEM_TX`,
  `FEM_RX`). These switch synchronously with the PHY TX/RX burst (µs scale), which
  Pi GPIO cannot do reliably.
- Provide a **glue/interlock** so both lines can never be high together (the
  MM8108 FEM control is normally already complementary; a small logic gate or
  pulldowns enforce safe states at reset). Pulldowns on both → default Shutdown.
- `FEM_TXEN_FB` / `FEM_RXEN_FB` from the header are **DNP 0 Ω fallbacks** for
  Pi-driven control during bring-up only.

## 3. GNSS chain (NEO-M9N)

- `U.FL #1` → optional **antenna bias-tee** → NEO-M9N `RF_IN`.
- Supports **passive** or **active** antennas:
  - Active: feed antenna DC through a bias inductor/ferrite from **+3V3** (or a
    dedicated `V_ANT`) with a series limit/fuse and the u-blox open/short
    detection circuit (optional).
  - Passive: no bias; just AC-couple to `RF_IN`.
- NEO-M9N has an internal SAW + LNA; keep its RF input trace short and clear of
  the buck-boost switch node and the 900 MHz PA. The PA's 900 MHz fundamental and
  harmonics must not desensitise the GNSS front-end — physical separation + ground
  fencing + the E21's own filtering help; add a GNSS pre-filter if isolation is
  marginal.

## 4. Coexistence & isolation

- 900 MHz PA (up to +30 dBm) and the GNSS receiver share a 65 × 30 mm board —
  **isolation is the hard part.** Mitigations:
  - Place the two U.FL connectors on **opposite ends** of the board.
  - Keep the GNSS LNA/trace far from the PA output and the buck-boost.
  - Ground pour + via fencing between the 900 MHz section and the GNSS section.
  - Consider a SAW/bandpass on the GNSS input if PA leakage degrades C/N₀.
- The Pi Zero 2 W's own 2.4 GHz Wi-Fi/BT chip antenna is on the Pi; the HAT RF
  sections should avoid sitting directly over it where practical.

## 5. Antenna selection

| Port | Band | Antenna |
|------|------|---------|
| U.FL #2 | 850–950 MHz | 868/915 MHz whip or external via U.FL→SMA pigtail; sized for the regulatory band in use |
| U.FL #1 | GNSS L1 (1575 MHz) | active GNSS patch/whip (recommended) or passive |

> **Regulatory:** 1 W (30 dBm) EIRP in the 902–928 MHz US ISM band (or 868 MHz
> EU) is subject to FCC Part 15.247 / ETSI EN 300 220 duty-cycle and power limits.
> Confirm the radiated power + antenna gain combination is legal for the target
> region before keying the PA at full power.
