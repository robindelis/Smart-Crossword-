#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

/*
 * PN532 Single-Antenna Sanity Test (Smart Crossword Board)
 *
 * Hardware Setup:
 *   ESP32-S3 3V3       --> PN532 VCC (3.3V is ideal and matches logic level)
 *   ESP32-S3 GND       --> PN532 GND
 *   ESP32-S3 GPIO 12   --> PN532 SCK
 *   ESP32-S3 GPIO 13   --> PN532 MOSI (MO)
 *   ESP32-S3 GPIO 21   --> PN532 MISO (M / MI)   [Note: GPIO 21 is on the RIGHT header]
 *   ESP32-S3 GPIO 14   --> PN532 CS / NSS / SS
 *   ESP32-S3 GPIO 11   --> PN532 RST (Hardware reset)
 *
 * Switches on PN532:
 *   SET0 = L (0)
 *   SET1 = H (1)
 */

#define PIN_PN532_SCK   12
#define PIN_PN532_MOSI  13
#define PIN_PN532_MISO  21
#define PIN_PN532_SS    14
#define PIN_PN532_RST   11

// Constructor parameter order: (clk, miso, mosi, ss)
Adafruit_PN532 nfc(PIN_PN532_SCK, PIN_PN532_MISO, PIN_PN532_MOSI, PIN_PN532_SS);

bool connected = false;
uint32_t lastRetry = 0;

void setup() {
    Serial.begin(115200);

    // Hardware reset pulse for PN532
    pinMode(PIN_PN532_RST, OUTPUT);
    digitalWrite(PIN_PN532_RST, LOW);
    delay(10);
    digitalWrite(PIN_PN532_RST, HIGH);
    delay(20);

    // Allow serial monitor time to connect, but do not hang
    unsigned long start = millis();
    while (!Serial && (millis() - start < 2500)) {
        delay(10);
    }

    Serial.println("\n==================================================");
    Serial.println("   PN532 Single Antenna Test (ESP32-S3 via SPI)   ");
    Serial.println("==================================================");
    Serial.printf("Configured Pins:\n");
    Serial.printf("  Power: ESP32 3V3  -->  PN532 VCC\n");
    Serial.printf("  GND:   ESP32 GND  -->  PN532 GND\n");
    Serial.printf("  SCK:   GPIO %-2d   -->  PN532 SCK\n", PIN_PN532_SCK);
    Serial.printf("  MOSI:  GPIO %-2d   -->  PN532 MOSI (MO)\n", PIN_PN532_MOSI);
    Serial.printf("  MISO:  GPIO %-2d   -->  PN532 MISO (M / MI) [RIGHT HEADER]\n", PIN_PN532_MISO);
    Serial.printf("  CS:    GPIO %-2d   -->  PN532 CS / NSS\n", PIN_PN532_SS);
    Serial.printf("  RST:   GPIO %-2d   -->  PN532 RST\n", PIN_PN532_RST);
    Serial.println("==================================================");

    nfc.begin();
}

void loop() {
    if (!connected) {
        // Continuous non-blocking retry every 1.5 seconds until detected
        if (millis() - lastRetry > 1500) {
            lastRetry = millis();

            // Refresh hardware reset
            digitalWrite(PIN_PN532_RST, LOW);
            delay(10);
            digitalWrite(PIN_PN532_RST, HIGH);
            delay(20);

            nfc.begin();
            uint32_t versiondata = nfc.getFirmwareVersion();

            if (!versiondata) {
                Serial.println("[WAITING] PN532 not responding yet. Retrying...");
                Serial.println("  -> Green LED: Must be lit on PN532 (proves 3.3V & GND connected)");
                Serial.println("  -> Right Header: Verify GPIO 21 is connected to PN532 M / MI");
                Serial.println("  -> DIP Switches: SET0 = L (0), SET1 = H (1) for SPI\n");
            } else {
                connected = true;
                Serial.println("--------------------------------------------------");
                Serial.print("🎉 [SUCCESS] Connected to PN5");
                Serial.println((versiondata >> 24) & 0xFF, HEX);
                Serial.printf("Firmware Version: %d.%d\n",
                              (versiondata >> 16) & 0xFF,
                              (versiondata >> 8) & 0xFF);
                Serial.println("--------------------------------------------------");

                nfc.SAMConfig();
                Serial.println("\n>>> Ready! Bring an NFC tag or card near the antenna coil <<<\n");
            }
        }
        return;
    }

    // Once connected: continuously poll for cards
    uint8_t success;
    uint8_t uid[7] = {0};
    uint8_t uidLength = 0;

    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 200);

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

        if (uidLength == 7) {
            uint8_t data[32];
            if (nfc.ntag2xx_ReadPage(4, data)) {
                Serial.print("Page 4 Data: ");
                nfc.PrintHexChar(data, 4);
            }
        }
        Serial.println("----------------------------------------------");
        delay(600);
    }
}
