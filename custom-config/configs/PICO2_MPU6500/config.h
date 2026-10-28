// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once

#define FC_TARGET_MCU RP2350A
#define BOARD_NAME PICO2_MPU6500
#define MANUFACTURER_ID RASP
#define LED0_PIN PA25

#define USE_ACC
#define USE_GYRO
#define USE_ACC_SPI_MPU6500
#define USE_GYRO_SPI_MPU6500
#define USE_GYRO_EXTI

// Betaflight's PA<n> names refer to RP2350 GPIO<n>.
#define SPI0_SCK_PIN PA18
#define SPI0_SDI_PIN PA16
#define SPI0_SDO_PIN PA19
#define GYRO_1_SPI_INSTANCE SPI0
#define GYRO_1_CS_PIN PA17
#define GYRO_1_EXTI_PIN PA20
#define GYRO_1_ALIGN CW0_DEG
