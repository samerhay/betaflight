"""Run the board's real validation hook against retained configuration cases."""
from pathlib import Path
import subprocess
import tempfile

source = Path(__file__).resolve().parents[2] / 'custom-config/configs/PICO2_MPU6500/config.c'
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    headers = {
        'platform.h': '#pragma once\n#include <stdint.h>\n',
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
static gyroDeviceConfig_t settings;
gyroDeviceConfig_t *gyroDeviceConfigMutable(int index) {
    assert(index == 0);
    return &settings;
}
int main(void) {
    settings = (gyroDeviceConfig_t){BUS_TYPE_SPI, 0};
    targetValidateConfiguration();
    assert(settings.busType == BUS_TYPE_SPI && settings.spiBus == 1);
    targetValidateConfiguration();
    assert(settings.spiBus == 1);
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
print('PASS: retained SPI bus 0 corrected; valid buses, I2C and disabled gyro preserved')
