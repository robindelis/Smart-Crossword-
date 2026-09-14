#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

/*
 * PN532 Single-Antenna Sanity Test (Smart Crossword Board)
 * 
 * Hardware Setup:
 *   ESP32 5V / VIN  --> PN532 VDD5V (or 5V)
 *   ESP32 GND       --> PN532 GND
 *   ESP32 GPIO 12   --> PN532 SCK
 *   ESP32 GPIO 13   --> PN532 MOSI
 *   ESP32 GPIO 21   --> PN532 MISO
 *   ESP32 GPIO 14   --> PN532 SS / NSS / CS
 *   ESP32 GPIO 10   --> PN532 IRQ
 *   ESP32 GPIO 11   --> PN532 RST
 *
 * Switches on PN532:
 *   SET0 = L (Low)
 *   SET1 = H (High)
 *
 * Antenna:
 *   Using the ONBOARD blue coil antenna on the PN532 module.
 *   (Do NOT cut the jumpers for this standalone test).
 */

#define PIN_PN532_SCK   12
#define PIN_PN532_MOSI  13
#define PIN_PN532_MISO  21
#define PIN_PN532_SS    14
#define PIN_PN532_IRQ   10
#define PIN_PN532_RST   11

Adafruit_PN532 nfc(PIN_PN532_SCK, PIN_PN532_MISO, PIN_PN532_MOSI, PIN_PN532_SS);

void setup() {
    // Native USB CDC serial initialization
    Serial.begin(115200);
    
    // Give USB-CDC time to connect
    delay(2000);

    Serial.println("\n==================================================");
    Serial.println("   PN532 Single Antenna Test (ESP32-S3 via SPI)   ");
    Serial.println("==================================================");
    Serial.printf("SPI Pins: SCK=%d, MOSI=%d, MISO=%d, CS=%d\n",
                  PIN_PN532_SCK, PIN_PN532_MOSI, PIN_PN532_MISO, PIN_PN532_SS);

    nfc.begin();

    uint32_t versiondata = nfc.getFirmwareVersion();
    if (!versiondata) {
        Serial.println("\n[ERROR] Could not find PN532 board!");
        Serial.println("Troubleshooting Checklist:");
        Serial.println("  1. Verify SET0 is set to 'L' and SET1 is set to 'H' (SPI mode).");
        Serial.println("  2. Verify 5V and GND are firmly connected.");
        Serial.println("  3. Double check SCK=12, MOSI=13, MISO=21, CS=14.");
        Serial.println("  4. Power cycle the board by unplugging and replugging USB.");
        while (1) {
            delay(1000);
        }
    }

    // Success: print chip info
    Serial.print("\n[SUCCESS] Connected to PN5");
    Serial.println((versiondata >> 24) & 0xFF, HEX);
    Serial.print("Firmware Version: ");
    Serial.print((versiondata >> 16) & 0xFF, DEC);
    Serial.print('.');
    Serial.println((versiondata >> 8) & 0xFF, DEC);
    Serial.print("Chip Support Flags: 0x0");
    Serial.println(versiondata & 0xFF, HEX);

    // Set normal SAM (Security Access Module) configuration
    nfc.SAMConfig();

    Serial.println("\n>>> Ready! Bring an NFC tag or card near the blue antenna <<<\n");
}

void loop() {
    uint8_t success;
    uint8_t uid[7] = {0};
    uint8_t uidLength = 0;

    // Poll for an ISO14443A tag (NTAG213, Mifare, etc.) with 250ms timeout
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 250);

    if (success) {
        Serial.println("----------------------------------------------");
        Serial.print("Tag Detected! Type: ");
        if (uidLength == 7) {
            Serial.println("NTAG213 / Ultralight (7-byte UID)");
        } else if (uidLength == 4) {
            Serial.println("Classic / 1K (4-byte UID)");
        } else {
            Serial.printf("Unknown (%d bytes)\n", uidLength);
        }

        Serial.print("UID (HEX): ");
        for (uint8_t i = 0; i < uidLength; i++) {
            if (uid[i] < 0x10) Serial.print("0");
            Serial.print(uid[i], HEX);
            if (i < uidLength - 1) Serial.print(":");
        }
        Serial.println();

        // If it is an NTAG tag, attempt reading page 4 (first user data page)
        if (uidLength == 7) {
            uint8_t data[32];
            success = nfc.ntag2xx_ReadPage(4, data);
            if (success) {
                Serial.print("Page 4 Data: ");
                nfc.PrintHexChar(data, 4);
            }
        }
        Serial.println("----------------------------------------------");

        // Small delay to prevent flooding serial while tag is held on coil
        delay(800);
    }
}
