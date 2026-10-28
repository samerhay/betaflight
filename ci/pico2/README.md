# Pico 2 with SPI MPU6500

The workflow in this fork's `pico2-mpu6500` branch builds the real Betaflight
2026.6.1 release, commit `6dbc4218fd6bc33bf16ea32c670304d4f89321d5`.
The branch's newer development source is deliberately not relabeled as 2026.6.1.
The workflow checks out that release from this fork into `firmware/` and this
branch's board files into `board/`. It never updates master.

`BETAFLIGHT_CONFIG` explicitly selects this fork's `custom-config` directory.
`CONFIG=PICO2_MPU6500` loads its `config.h` through Betaflight's normal config
handling. The separate upstream config submodule is hydrated at the release's
pinned revision for build dependencies, but is not used to select the board.
Do not invoke `make configs` against `custom-config`: it is a tracked directory,
not an independent clone of betaflight/config.

| MPU6500 signal | Pico 2 GPIO | Betaflight name |
| --- | --- | --- |
| SCK | GP18 | SPI0_SCK_PIN PA18 |
| MISO | GP16 | SPI0_SDI_PIN PA16 |
| MOSI | GP19 | SPI0_SDO_PIN PA19 |
| CS | GP17 | GYRO_1_CS_PIN PA17 |
| INT | GP20 | GYRO_1_EXTI_PIN PA20 |

This is RP2350A with the release's native 4 MB flash setting, not HELLBENDER
RP2350B. Both `USE_ACC_SPI_MPU6500` and `USE_GYRO_SPI_MPU6500` are enabled.
LED is GP25. Sensor alignment defaults to CW0 and must match physical mounting.
Motor and receiver wiring is intentionally unassigned; this is a sensor bring-up
image, not a flight-tested complete FC configuration.

Each successful artifact includes UF2, ELF, map, compiler macros, preprocessed
SPI/gyro defaults, symbol list, build log, picotool inspection, SHA256, and a
machine-checked verification report. Hardware sensor detection and orientation
must still be confirmed on the physical board via USB before use.

For a local Linux build, check out the release into `firmware`, then:

```sh
cd firmware
make SDK=pico_sdk platform-sdk-hydrate
make SDK=pico_sdk platform-tools-install
BETAFLIGHT_CONFIG=/absolute/path/to/branch/custom-config make -j2 CONFIG=PICO2_MPU6500 uf2
```
