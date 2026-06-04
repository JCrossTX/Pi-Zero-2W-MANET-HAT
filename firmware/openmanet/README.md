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
Stock OpenMANET Pi Zero 2 W setups use a module with an **internal** PA. This HAT
adds an **external E21-900G30S 1 W PA/LNA front-end** on the MM8108 RF path. That
changes nothing on the SPI/control side, but it does require:
1. an MM8108 configured for an **external FEM** RF path, and
2. the E21 T/R switch driven by the **MM8108 FEM-control outputs** (on-board, not
   via the header).

See [`../../docs/RF.md`](../../docs/RF.md) and
[`../../docs/DECISIONS.md`](../../docs/DECISIONS.md) (risks B2, B3, B5).
