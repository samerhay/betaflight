// SPDX-License-Identifier: GPL-3.0-or-later
#include "platform.h"

#include "config/config.h"
#include "drivers/bus.h"
#include "io/serial.h"
#include "pg/gyrodev.h"

static void restoreUnassignedSerialPins(serialPortIdentifier_e identifier, ioTag_t tx, ioTag_t rx)
{
    const int index = serialResourceIndex(identifier);
    serialPinConfig_t *pins = serialPinConfigMutable();
    if (index >= 0 && !pins->ioTagTx[index] && !pins->ioTagRx[index]) {
        pins->ioTagTx[index] = tx;
        pins->ioTagRx[index] = rx;
    }
}

void targetValidateConfiguration(void)
{
    // Betaflight config bus 1 is hardware SPI0; config bus 0 is disabled.
    // Older saved settings can override the already-correct board default.
    gyroDeviceConfig_t *gyro = gyroDeviceConfigMutable(0);
    if (gyro->busType == BUS_TYPE_SPI && gyro->spiBus == 0) {
        gyro->spiBus = 1;
    }

    // The earlier sensor-only image saved four UARTs with no assigned pins.
    // Fill only empty pairs; preserve remapped and one-direction ports.
    restoreUnassignedSerialPins(SERIAL_PORT_UART0, IO_TAG(UART0_TX_PIN), IO_TAG(UART0_RX_PIN));
    restoreUnassignedSerialPins(SERIAL_PORT_UART1, IO_TAG(UART1_TX_PIN), IO_TAG(UART1_RX_PIN));
    restoreUnassignedSerialPins(SERIAL_PORT_PIOUART0, IO_TAG(PIOUART0_TX_PIN), IO_TAG(PIOUART0_RX_PIN));
    restoreUnassignedSerialPins(SERIAL_PORT_PIOUART1, IO_TAG(PIOUART1_TX_PIN), IO_TAG(PIOUART1_RX_PIN));
}
