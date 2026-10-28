// SPDX-License-Identifier: GPL-3.0-or-later
#include "platform.h"

#include "config/config.h"
#include "drivers/bus.h"
#include "pg/gyrodev.h"

void targetValidateConfiguration(void)
{
    // Betaflight config bus 1 is hardware SPI0; config bus 0 is disabled.
    // Older saved settings can override the already-correct board default.
    gyroDeviceConfig_t *gyro = gyroDeviceConfigMutable(0);
    if (gyro->busType == BUS_TYPE_SPI && gyro->spiBus == 0) {
        gyro->spiBus = 1;
    }
}
