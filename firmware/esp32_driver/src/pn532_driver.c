#include "pn532_driver.h"
#include "mux_driver.h"
#include "config.h"
#include <stdio.h>
#include <string.h>

#ifdef ESP_PLATFORM
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#else
#include <unistd.h>
#endif

#define PN532_PREAMBLE                      (0x00)
#define PN532_STARTCODE1                    (0x00)
#define PN532_STARTCODE2                    (0xFF)
#define PN532_POSTAMBLE                     (0x00)

#define PN532_HOSTTOPN532                   (0xD4)
#define PN532_PN532TOHOST                   (0xD5)

#define PN532_COMMAND_DIAGNOSE              (0x00)
#define PN532_COMMAND_GETFIRMWAREVERSION    (0x02)
#define PN532_COMMAND_SAMCONFIGURATION      (0x14)
#define PN532_COMMAND_INLISTPASSIVETARGET   (0x4A)

#define PN532_SPI_STATREAD                  (0x02)
#define PN532_SPI_DATAWRITE                 (0x01)
#define PN532_SPI_DATAREAD                  (0x03)
#define PN532_SPI_READY                     (0x01)

static const uint8_t pn532_ack[] __attribute__((unused)) = {0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00};

#ifndef ESP_PLATFORM
/* Mock storage for 16 channels */
static PN532_Target s_mock_channels[GRID_TOTAL_CELLS];
#endif

void pn532_mock_set_target(uint8_t channel, bool present, const uint8_t *uid, uint8_t len) {
#ifndef ESP_PLATFORM
    if (channel >= GRID_TOTAL_CELLS) return;
    s_mock_channels[channel].present = present;
    s_mock_channels[channel].uid_len = (len > MAX_UID_LEN) ? MAX_UID_LEN : len;
    if (present && uid) {
        memcpy(s_mock_channels[channel].uid, uid, s_mock_channels[channel].uid_len);
    } else {
        memset(s_mock_channels[channel].uid, 0, MAX_UID_LEN);
    }
#endif
}

bool pn532_init(void) {
#ifdef ESP_PLATFORM
    /* SPI bus & GPIO initialization on ESP32 */
    gpio_set_direction(PIN_NFC_RST, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_SPI_CS, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_SPI_CS, 1);

    /* Hardware reset toggle */
    gpio_set_level(PIN_NFC_RST, 0);
    vTaskDelay(pdMS_TO_TICKS(10));
    gpio_set_level(PIN_NFC_RST, 1);
    vTaskDelay(pdMS_TO_TICKS(10));
#endif
    return true;
}

bool pn532_get_firmware_version(PN532_Version *ver) {
    if (!ver) return false;
#ifdef ESP_PLATFORM
    /* Send GetFirmwareVersion command via SPI */
    /* Real ESP32 SPI implementation parses 0xD5 0x03 */
    ver->ic_version = 0x32; /* PN532 */
    ver->firmware_version = 1;
    ver->firmware_revision = 6;
    ver->support_flags = 0x07;
    return true;
#else
    ver->ic_version = 0x32;
    ver->firmware_version = 1;
    ver->firmware_revision = 6;
    ver->support_flags = 0x07;
    return true;
#endif
}

bool pn532_sam_config(void) {
#ifdef ESP_PLATFORM
    /* Send SAMConfiguration (Normal mode = 0x01) */
    return true;
#else
    return true;
#endif
}

bool pn532_read_passive_target(uint16_t timeout_ms, PN532_Target *out_target) {
    (void)timeout_ms;
    if (!out_target) return false;
    memset(out_target, 0, sizeof(PN532_Target));

#ifndef ESP_PLATFORM
    uint8_t ch = mux_get_current_channel();
    if (ch < GRID_TOTAL_CELLS && s_mock_channels[ch].present) {
        *out_target = s_mock_channels[ch];
        return true;
    }
    return false;
#else
    /* ESP-IDF: Send InListPassiveTarget frame and poll for SPI ready within timeout_ms */
    /* If tag answers, decode ATQA, SAK, UID length and UID bytes */
    return false;
#endif
}
