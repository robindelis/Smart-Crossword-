#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>
#include <stdbool.h>

/* Board Architecture */
#define GRID_ROWS 4
#define GRID_COLS 4
#define GRID_TOTAL_CELLS (GRID_ROWS * GRID_COLS)

/* CD74HC4067 Multiplexer GPIO Pin Assignment (ESP32-S3 DevKitC-1) */
#define PIN_MUX_S0   15  /* J1 Pin 11: Address bit 0 */
#define PIN_MUX_S1   7   /* J1 Pin 9:  Address bit 1 */
#define PIN_MUX_S2   5   /* J1 Pin 5:  Address bit 2 */
#define PIN_MUX_S3   4   /* J1 Pin 3:  Address bit 3 */
#define PIN_MUX_EN   6   /* J1 Pin 7:  Active-Low Enable */

/* PN532 NFC Transceiver SPI Pin Assignment */
#define PIN_SPI_SCK  12  /* J1 Pin 18: SPI Clock */
#define PIN_SPI_MOSI 13  /* J1 Pin 14: Master Out Slave In */
#define PIN_SPI_MISO 21  /* J1 Pin 20: Master In Slave Out */
#define PIN_SPI_CS   14  /* J1 Pin 16: SPI Chip Select */
#define PIN_NFC_IRQ  10  /* J1 Pin 10: NFC Interrupt */
#define PIN_NFC_RST  11  /* J1 Pin 12: NFC Reset */

/* Spare GPIOs */
#define PIN_GPIO_AUX 16  /* J1 Pin 4:  Tactile Button / Debug LED */
#define PIN_I2C_SDA  8   /* J1 Pin 6:  Spare I2C SDA */
#define PIN_I2C_SCL  9   /* J1 Pin 8:  Spare I2C SCL */

/* Timing Constraints (Invariants from wise.md) */
#define MUX_SETTLE_US          20    /* Analog switch propagation + settling delay */
#define NFC_POLL_TIMEOUT_MS    4     /* Max wait time per channel when checking tag presence */
#define SCAN_DEBOUNCE_CYCLES   2     /* Number of consecutive identical reads before state change */
#define SCAN_INTERVAL_IDLE_MS  100   /* Delay between continuous sweep passes */

/* Maximum NFC UID length (4 bytes for MIFARE Classic / Ultralight, 7 bytes for NTAG213) */
#define MAX_UID_LEN            7

#endif /* CONFIG_H */
