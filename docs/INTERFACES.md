# Interfaces & 40-Pin Header Map

All host I/O and power cross the **2×20 (40-pin) female header** that mates with
the Pi Zero 2 W male header. BCM = Broadcom GPIO number.

> **OpenMANET-compatible pinout.** The MM8108 control/SPI lines below match the
> OpenMANET Pi Zero 2 W **SPI** firmware variant so the stock device-tree overlay
> works unchanged: **SPI0**, **CS0 = GPIO8**, **RESET = GPIO17**, **power/wake =
> GPIO23 + GPIO24**, **IRQ/BUSY = GPIO5**, `spi-max-frequency = 20 MHz`,
> compatible `morse,mm610x-spi`. See [`../firmware/openmanet/`](../firmware/openmanet/)
> and [`DECISIONS.md`](DECISIONS.md) §A6.

## 1. Full 40-pin assignment

| Phys | Name / BCM        | HAT net            | Used by        | Notes |
|-----:|-------------------|--------------------|----------------|-------|
| 1    | 3V3               | `3V3_PI` (ref)     | —              | Reference only; not a HAT supply |
| 2    | 5V                | `+5V`              | Power in       | 3V3 regulator main input |
| 3    | GPIO2 / SDA1      | `GNSS_SDA`         | NEO-M9N        | I²C (alt control bus) |
| 4    | 5V                | `+5V`              | Power in       | Parallel 5 V feed |
| 5    | GPIO3 / SCL1      | `GNSS_SCL`         | NEO-M9N        | I²C (alt control bus) |
| 6    | GND               | `GND`              | —              | |
| 7    | GPIO4             | `SPARE4`           | spare          | (E21 T/R retired) |
| 8    | GPIO14 / TXD0     | `GNSS_RXD`         | NEO-M9N        | Pi TX → GNSS RX |
| 9    | GND               | `GND`              | —              | |
| 10   | GPIO15 / RXD0     | `GNSS_TXD`         | NEO-M9N        | GNSS TX → Pi RX |
| 11   | **GPIO17**        | `MM_RESET_N`       | **MM8108**     | **OpenMANET reset-gpios** (active low) |
| 12   | GPIO18            | `GNSS_PPS`         | NEO-M9N        | 1 PPS time pulse (pps-gpio) |
| 13   | GPIO27            | `GNSS_RESET_N`     | NEO-M9N        | GNSS reset (optional) |
| 14   | GND               | `GND`              | —              | |
| 15   | GPIO22            | `GNSS_EXTINT`      | NEO-M9N        | EXTINT (optional) |
| 16   | **GPIO23**        | `MM_PWR1`          | **MM8108**     | **OpenMANET power-gpios[0]** |
| 17   | 3V3               | `3V3_PI` (ref)     | —              | Reference only |
| 18   | **GPIO24**        | `MM_PWR2`          | **MM8108**     | **OpenMANET power-gpios[1]** |
| 19   | GPIO10 / MOSI0    | `SPI_MOSI`         | **MM8108**     | SPI0 |
| 20   | GND               | `GND`              | —              | |
| 21   | GPIO9 / MISO0     | `SPI_MISO`         | **MM8108**     | SPI0 |
| 22   | GPIO25            | `SPARE25`          | spare          | |
| 23   | GPIO11 / SCLK0    | `SPI_SCLK`         | **MM8108**     | SPI0 |
| 24   | **GPIO8 / CE0**   | `SPI_CS_MM`        | **MM8108**     | **OpenMANET CS0** |
| 25   | GND               | `GND`              | —              | |
| 26   | GPIO7 / CE1       | `SPARE_CE1`        | spare          | Free SPI CS |
| 27   | ID_SD / GPIO0     | `ID_SD`            | ID EEPROM      | HAT EEPROM data (reserved) |
| 28   | ID_SC / GPIO1     | `ID_SC`            | ID EEPROM      | HAT EEPROM clock (reserved) |
| 29   | **GPIO5**         | `MM_IRQ`           | **MM8108**     | **OpenMANET spi-irq-gpios** (IRQ/BUSY) |
| 30   | GND               | `GND`              | —              | |
| 31   | GPIO6             | `SPARE6`           | spare          | (E21 T/R retired) |
| 32   | GPIO12            | `LED_FIX`          | status LED     | GNSS-fix LED (host-driven, PWM-capable) |
| 33   | GPIO13            | `LED_TX`           | status LED     | TX-activity LED (host-driven, PWM-capable) |
| 34   | GND               | `GND`              | —              | |
| 35   | GPIO19            | `SPARE19`          | spare          | |
| 36   | GPIO16            | `SPARE16`          | spare          | |
| 37   | GPIO26            | `SPARE26`          | spare          | |
| 38   | GPIO20            | `SPARE20`          | spare          | |
| 39   | GND               | `GND`              | —              | |
| 40   | GPIO21            | `SPARE21`          | spare          | |

> The integrated MM8108 module (M20 / MF15457) handles its own TX/RX switching, so
> there are **no FEM T/R lines** on the header anymore — GPIO4/6 revert to spares
> and GPIO12/13 drive the status LEDs. (External E21 retired — B11.)

## 2. Bus summary

| Bus    | Pi peripheral | Signals (phys pins)                  | Device   |
|--------|---------------|--------------------------------------|----------|
| SPI0   | spi0.0        | MOSI 19, MISO 21, SCLK 23, CE0 24    | MM8108   |
| UART0  | ttyAMA0       | TXD 8, RXD 10                        | NEO-M9N  |
| I²C1   | i2c-1         | SDA 3, SCL 5                         | NEO-M9N (alt) |
| I²C0   | i2c-0 (ID)    | ID_SD 27, ID_SC 28                   | ID EEPROM (VCC = Pi 3V3, pin 1) |
| GPIO   | —             | IRQ 29, RESET 11, PWR 16/18 (MM8108); PPS 12 (GNSS) | per overlay |

## 3. MM8108 ↔ OpenMANET overlay mapping

| OpenMANET DTS property | BCM | Phys | HAT net |
|------------------------|-----|------|---------|
| `spi0` CS0 (`cs-gpios`)| 8   | 24   | `SPI_CS_MM` |
| `reset-gpios`          | 17  | 11   | `MM_RESET_N` |
| `power-gpios` [0]      | 23  | 16   | `MM_PWR1` |
| `power-gpios` [1]      | 24  | 18   | `MM_PWR2` |
| `spi-irq-gpios`        | 5   | 29   | `MM_IRQ` |
| `spi-max-frequency`    | —   | —    | 20 MHz |

## 4. Internal (non-header) nets

| Net        | From            | To              | Notes |
|------------|-----------------|-----------------|-------|
| `RF_900`   | module `ANT`    | C35 DC-block    | 50 Ω controlled impedance, short |
| `ANT_900`  | C35 (→[FL2 DNP])| U.FL #2         | 50 Ω, board edge; ESD clamp |
| `RF_GNSS`  | U.FL #1         | NEO-M9N RF_IN   | 50 Ω; optional antenna bias |
| `+3V3`     | 3V3 reg out     | radio / NEO-M9N | radio + GNSS digital (no VPA rail) |

Machine-readable version: [`../hardware/netlist/connections.csv`](../hardware/netlist/connections.csv).

## 5. Host configuration cheat-sheet

```ini
# /boot/firmware/config.txt
dtparam=spi=on
enable_uart=1
dtoverlay=disable-bt            # free PL011 UART0 for GNSS on a Zero 2 W
dtparam=i2c_arm=on              # only if using GNSS I2C
dtoverlay=pps-gpio,gpiopin=18   # 1 PPS on GPIO18 (phys 12)
dtoverlay=manet-hat             # this board's overlay (firmware/openmanet/)
```
- Disable the serial login console so `ttyAMA0` is free for the NEO-M9N.
- MM8108: the OpenMANET SPI overlay binds the Morse driver to `spi0.0`
  (CS0/GPIO8) with IRQ on GPIO5, reset on GPIO17, power on GPIO23/24.
