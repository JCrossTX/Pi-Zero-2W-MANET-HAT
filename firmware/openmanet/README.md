# OpenMANET compatibility

This HAT is wired to be **drop-in compatible with the OpenMANET Raspberry Pi
Zero 2 W MM8108 _SPI_ firmware variant** — no firmware changes are required, only
this board's device-tree overlay.

## Why it just works
OpenMANET's Pi Zero 2 W build talks to the Morse Micro radio over **SPI** (not
USB/SDIO), which is exactly the interface this HAT exposes on the 40-pin header.
The board uses the **same GPIO assignments** the OpenMANET overlay expects:

| Function | BCM | Phys pin |
|----------|-----|----------|
| SPI0 CS0 | GPIO8  | 24 |
| RESET    | GPIO17 | 11 |
| Power/wake | GPIO23, GPIO24 | 16, 18 |
| IRQ/BUSY | GPIO5  | 29 |
| SPI clock | 20 MHz | — |
| compatible | `morse,mm610x-spi` | — |

(Reference: OpenMANET project + community discussion #26 "Raspberry pi Zero 2 +
HAT + WM6108". The MM8108 is pin/driver-compatible with the mm610x SPI binding;
confirm the `compatible` string against the exact OpenMANET kernel module you
flash.)

## Files
- `manet-hat-overlay.dts` — device-tree overlay matching this board (radio on
  SPI0/CS0 + reset/power/IRQ GPIOs, UART0 for GNSS, 1 PPS on GPIO18).

## Build & install
```sh
dtc -@ -I dts -O dtb -o manet-hat.dtbo manet-hat-overlay.dts
sudo cp manet-hat.dtbo /boot/firmware/overlays/
# add to /boot/firmware/config.txt:
#   dtparam=spi=on
#   enable_uart=1
#   dtoverlay=disable-bt
#   dtoverlay=manet-hat
```

## Hardware difference vs. stock OpenMANET nodes
This HAT uses an integrated high-power MM8108 module (no external PA — the E21 was
retired, B11):
- **MF15457 fallback** — runs stock OpenMANET unchanged with `bcf_mf15457`; the
  SPI/control map here is exactly the OpenMANET Pi Zero 2 W SPI variant.
- **MM8108-M20 primary** — same MM8108 SPI stack, but needs its **own BCF** for the
  integrated PA (OpenMANET M20 support TBD). This overlay is unchanged either way.

See [`../../docs/RF.md`](../../docs/RF.md),
[`../../docs/MODULE_OPTIONS.md`](../../docs/MODULE_OPTIONS.md) and
[`../../docs/DECISIONS.md`](../../docs/DECISIONS.md) (B11/B12).
