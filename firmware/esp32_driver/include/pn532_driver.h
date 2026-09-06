#ifndef PN532_DRIVER_H
#define PN532_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include "config.h"

typedef struct {
    uint8_t ic_version;
    uint8_t firmware_version;
    uint8_t firmware_revision;
    uint8_t support_flags;
} PN532_Version;

typedef struct {
    bool present;
    uint8_t uid_len;
    uint8_t uid[MAX_UID_LEN];
    uint16_t atqa;
    uint8_t sak;
} PN532_Target;

/**
 * Initialize PN532 SPI communication bus and control lines.
 */
bool pn532_init(void);

/**
 * Query PN532 firmware version to verify SPI communication.
 */
bool pn532_get_firmware_version(PN532_Version *ver);

/**
 * Configure Security Access Module (SAM) to standard normal mode.
 */
bool pn532_sam_config(void);

/**
 * Poll for an ISO 14443A passive target (106 kbps / MIFARE / NTAG213)
 * on the currently energized antenna coil.
 * 
 * @param timeout_ms Maximum time to wait for a response in milliseconds.
 * @param out_target Pointer to target result structure.
 * @return true if a card was detected, false if timeout/no card.
 */
bool pn532_read_passive_target(uint16_t timeout_ms, PN532_Target *out_target);

/* Mock injection for simulation / CI testing */
void pn532_mock_set_target(uint8_t channel, bool present, const uint8_t *uid, uint8_t len);

#endif /* PN532_DRIVER_H */
