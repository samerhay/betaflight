"""Run the board's real validation hook against retained configuration cases."""
from pathlib import Path
import subprocess
import tempfile

source = Path(__file__).resolve().parents[2] / 'custom-config/configs/PICO2_MPU6500/config.c'
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    headers = {
        'platform.h': '#pragma once\n#include <stdint.h>\n#include "board.h"\n',
        'board.h': source.with_suffix('.h').read_text(),
        'io/serial.h': '''#pragma once
typedef uint8_t ioTag_t;
#define PA0 0
#define PA1 1
#define PA4 4
#define PA5 5
#define PA6 6
#define PA7 7
#define PA8 8
#define PA9 9
#define IO_TAG(pin) (100 + (pin))
typedef enum { SERIAL_PORT_UART0, SERIAL_PORT_UART1,
               SERIAL_PORT_PIOUART0, SERIAL_PORT_PIOUART1 } serialPortIdentifier_e;
typedef struct { ioTag_t ioTagTx[4]; ioTag_t ioTagRx[4]; } serialPinConfig_t;
int serialResourceIndex(serialPortIdentifier_e identifier);
serialPinConfig_t *serialPinConfigMutable(void);
''',
        'config/config.h': 'void targetValidateConfiguration(void);\n',
        'drivers/bus.h': 'enum { BUS_TYPE_NONE, BUS_TYPE_I2C, BUS_TYPE_SPI };\n',
        'pg/gyrodev.h': '''typedef struct {
    uint8_t busType;
    uint8_t spiBus;
} gyroDeviceConfig_t;
gyroDeviceConfig_t *gyroDeviceConfigMutable(int index);
''',
    }
    for name, content in headers.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    harness = root / 'test.c'
    harness.write_text('''#include <assert.h>
#include "platform.h"
#include "config/config.h"
#include "drivers/bus.h"
#include "pg/gyrodev.h"
#include "io/serial.h"
static gyroDeviceConfig_t settings;
static serialPinConfig_t pins;
int serialResourceIndex(serialPortIdentifier_e identifier) { return (int)identifier; }
serialPinConfig_t *serialPinConfigMutable(void) { return &pins; }
gyroDeviceConfig_t *gyroDeviceConfigMutable(int index) {
    assert(index == 0);
    return &settings;
}
int main(void) {
    settings = (gyroDeviceConfig_t){BUS_TYPE_SPI, 0};
    targetValidateConfiguration();
    assert(settings.busType == BUS_TYPE_SPI && settings.spiBus == 1);
    assert(pins.ioTagTx[0] == IO_TAG(PA0) && pins.ioTagRx[0] == IO_TAG(PA1));
    assert(pins.ioTagTx[1] == IO_TAG(PA4) && pins.ioTagRx[1] == IO_TAG(PA5));
    assert(pins.ioTagTx[2] == IO_TAG(PA6) && pins.ioTagRx[2] == IO_TAG(PA7));
    assert(pins.ioTagTx[3] == IO_TAG(PA8) && pins.ioTagRx[3] == IO_TAG(PA9));
    pins.ioTagTx[0] = 120;
    pins.ioTagRx[0] = 121;
    pins.ioTagTx[1] = 0;
    pins.ioTagRx[1] = 122;
    targetValidateConfiguration();
    assert(settings.spiBus == 1);
    assert(pins.ioTagTx[0] == 120 && pins.ioTagRx[0] == 121);
    assert(pins.ioTagTx[1] == 0 && pins.ioTagRx[1] == 122);
    settings.spiBus = 2;
    targetValidateConfiguration();
    assert(settings.spiBus == 2);
    settings = (gyroDeviceConfig_t){BUS_TYPE_I2C, 0};
    targetValidateConfiguration();
    assert(settings.busType == BUS_TYPE_I2C && settings.spiBus == 0);
    settings = (gyroDeviceConfig_t){BUS_TYPE_NONE, 0};
    targetValidateConfiguration();
    assert(settings.busType == BUS_TYPE_NONE && settings.spiBus == 0);
}
''')
    executable = root / 'test-config'
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', str(root),
                    str(source), str(harness), '-o', str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
print('PASS: gyro bus corrected; all four empty UART pin pairs restored; remapped and RX-only ports preserved')
