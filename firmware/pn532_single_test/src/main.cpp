#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

/*
 * ============================================================================
 *   SMART CROSSWORD BOARD - UNIFIED 4x4 HARDWARE BENCH TESTER
 *   Subsystems: CD74HC4067 (16-Channel MUX) + PN532 (NFC Transceiver via SPI)
 * ============================================================================
 *
 * Hardware Pin Connections on ESP32-S3 DevKit:
 *
 * --- Multiplexer CD74HC4067 (Header J1) ---
 *   ESP32 3V3       -->  J1 Pin 1 or 2 (Power)
 *   ESP32 GND       -->  J1 Pin 13, 15, 17, or 19 (Ground)
 *   ESP32 GPIO 15   -->  J1 Pin 11 (MUX_S0: Address bit 0)
 *   ESP32 GPIO 7    -->  J1 Pin 9  (MUX_S1: Address bit 1)
 *   ESP32 GPIO 5    -->  J1 Pin 5  (MUX_S2: Address bit 2)
 *   ESP32 GPIO 4    -->  J1 Pin 3  (MUX_S3: Address bit 3)
 *   ESP32 GPIO 6    -->  J1 Pin 7  (MUX_EN: Active-Low Enable)
 *
 * --- PN532 NFC Module (SPI Interface) ---
 *   ESP32 3V3       -->  PN532 VCC
 *   ESP32 GND       -->  PN532 GND
 *   ESP32 GPIO 12   -->  PN532 SCK
 *   ESP32 GPIO 13   -->  PN532 MOSI (MO)
 *   ESP32 GPIO 21   -->  PN532 MISO (M / MI)   [⚠️ RIGHT HEADER on YD-ESP32-S3]
 *   ESP32 GPIO 14   -->  PN532 CS / NSS / SS
 *   ESP32 GPIO 11   -->  PN532 RST (Hardware Reset)
 *
 *   DIP Switches on PN532: SET0 = L (0), SET1 = H (1)
 * ============================================================================
 */

// --- Pin Definitions ---
#define PIN_MUX_S0        15
#define PIN_MUX_S1        7
#define PIN_MUX_S2        5
#define PIN_MUX_S3        4
#define PIN_MUX_EN        6

#define PIN_PN532_SCK     12
#define PIN_PN532_MOSI    13
#define PIN_PN532_MISO    21
#define PIN_PN532_SS      14
#define PIN_PN532_RST     11

// --- PN532 Software SPI Instance ---
Adafruit_PN532 nfc(PIN_PN532_SCK, PIN_PN532_MISO, PIN_PN532_MOSI, PIN_PN532_SS);

// --- State Variables ---
int currentChannel = 0;
bool muxEnabled = true;
bool pn532Ready = false;
uint32_t lastPn532Retry = 0;
unsigned long lastHeartbeat = 0;
bool autoStep = false;
unsigned long lastAutoStep = 0;
bool continuousSweep = false;

// Last detected tag info
uint8_t lastUid[7] = {0};
uint8_t lastUidLen = 0;
int lastTagChannel = -1;
unsigned long lastTagDetectTime = 0;

// Grid detection state (16 squares)
struct GridCell {
    bool hasTag;
    uint8_t uid[7];
    uint8_t uidLen;
    char assignedLetter;
};
GridCell grid[16];

// Simple Tag-to-Letter dictionary (up to 32 enrolled tags)
struct TagMapping {
    uint8_t uid[7];
    uint8_t uidLen;
    char letter;
    uint8_t points;
};
TagMapping tagDb[32];
int tagDbCount = 0;

// Standard Scrabble letter score table
uint8_t getLetterPoints(char c) {
    if (c >= 'a' && c <= 'z') c -= 32;
    switch (c) {
        case 'A': case 'E': case 'I': case 'O': case 'U':
        case 'L': case 'N': case 'S': case 'T': case 'R': return 1;
        case 'D': case 'G': return 2;
        case 'B': case 'C': case 'M': case 'P': return 3;
        case 'F': case 'H': case 'V': case 'W': case 'Y': return 4;
        case 'K': return 5;
        case 'J': case 'X': return 8;
        case 'Q': case 'Z': return 10;
        default: return 0; // Blank tile or unknown
    }
}

// Check if a UID matches an enrolled tag
char lookupLetter(const uint8_t *uid, uint8_t len) {
    for (int i = 0; i < tagDbCount; i++) {
        if (tagDb[i].uidLen == len && memcmp(tagDb[i].uid, uid, len) == 0) {
            return tagDb[i].letter;
        }
    }
    return '?'; // Unenrolled
}

// Enroll or update a tag mapping
void enrollTag(const uint8_t *uid, uint8_t len, char letter) {
    if (letter >= 'a' && letter <= 'z') letter -= 32;
    for (int i = 0; i < tagDbCount; i++) {
        if (tagDb[i].uidLen == len && memcmp(tagDb[i].uid, uid, len) == 0) {
            tagDb[i].letter = letter;
            tagDb[i].points = getLetterPoints(letter);
            return;
        }
    }
    if (tagDbCount < 32) {
        memcpy(tagDb[tagDbCount].uid, uid, len);
        tagDb[tagDbCount].uidLen = len;
        tagDb[tagDbCount].letter = letter;
        tagDb[tagDbCount].points = getLetterPoints(letter);
        tagDbCount++;
    }
}

// --- Multiplexer Control ---
void setMuxChannel(uint8_t ch, bool enable) {
    if (!enable) {
        digitalWrite(PIN_MUX_EN, HIGH); // Disable all channels (High-Z)
        return;
    }

    // Set 4-bit address lines
    digitalWrite(PIN_MUX_S0, (ch & 0x01) ? HIGH : LOW);
    digitalWrite(PIN_MUX_S1, (ch & 0x02) ? HIGH : LOW);
    digitalWrite(PIN_MUX_S2, (ch & 0x04) ? HIGH : LOW);
    digitalWrite(PIN_MUX_S3, (ch & 0x08) ? HIGH : LOW);

    // Enable MUX (Active-Low)
    digitalWrite(PIN_MUX_EN, LOW);
    delayMicroseconds(50); // Small settling time
}

// --- Dashboard & Visual Display ---
void printDashboard() {
    uint8_t row = currentChannel / 4;
    uint8_t col = currentChannel % 4;

    Serial.println("\n=======================================================");
    Serial.println("  🎯 SMART CROSSWORD BOARD - UNIFIED 4x4 BENCH TESTER  ");
    Serial.println("=======================================================");

    // 4x4 Grid Representation
    Serial.println("   Board Matrix (Top View):");
    Serial.println("         Col 0       Col 1       Col 2       Col 3");
    Serial.println("      +-----------+-----------+-----------+-----------+");
    for (uint8_t r = 0; r < 4; r++) {
        Serial.printf(" Row%d |", r);
        for (uint8_t c = 0; c < 4; c++) {
            uint8_t ch = r * 4 + c;
            char marker = (muxEnabled && r == row && c == col) ? '*' : ' ';
            char letter = grid[ch].hasTag ? grid[ch].assignedLetter : '.';

            if (grid[ch].hasTag) {
                Serial.printf(" %c%2d:[%c]   |", marker, ch, letter);
            } else {
                Serial.printf(" %c%2d: .    |", marker, ch);
            }
        }
        Serial.println();
        Serial.println("      +-----------+-----------+-----------+-----------+");
    }

    Serial.println();
    if (muxEnabled) {
        Serial.printf("  ACTIVE CHANNEL : Channel %d (Row %d, Col %d)\n", currentChannel, row, col);
        Serial.printf("  BINARY ADDRESS : S3=%d, S2=%d, S1=%d, S0=%d (0b%d%d%d%d)\n",
                      (currentChannel >> 3) & 1, (currentChannel >> 2) & 1,
                      (currentChannel >> 1) & 1, currentChannel & 1,
                      (currentChannel >> 3) & 1, (currentChannel >> 2) & 1,
                      (currentChannel >> 1) & 1, currentChannel & 1);
        Serial.println("  MUX STATUS     : ENABLED (EN / GPIO 6 = LOW, 0.0V)");
    } else {
        Serial.println("  MUX STATUS     : DISABLED (EN / GPIO 6 = HIGH, 3.3V - All channels open)");
    }

    // PN532 Status
    Serial.printf("  NFC TRANSCEIVER: %s\n", pn532Ready ? "🟢 CONNECTED (PN532 v1.6 SPI)" : "🟡 SEARCHING (Check SPI & Power)...");

    if (lastUidLen > 0 && (millis() - lastTagDetectTime < 10000)) {
        Serial.printf("  LAST TAG SCANNED: UID=");
        for (uint8_t i = 0; i < lastUidLen; i++) {
            Serial.printf("%02X%s", lastUid[i], (i + 1 < lastUidLen) ? ":" : "");
        }
        char let = lookupLetter(lastUid, lastUidLen);
        Serial.printf(" (%d bytes) -> Letter: '%c' (Square %d)\n", lastUidLen, let, lastTagChannel);
    }

    Serial.println("-------------------------------------------------------");
    Serial.println("  Commands:");
    Serial.println("    [SPACE/ENTER] : Step to next channel (0 -> 1 -> ... -> 15)");
    Serial.println("    [p]           : Step to previous channel");
    Serial.println("    [0]..[15]     : Jump directly to channel number (type number + enter)");
    Serial.println("    [s]           : Full 16-channel Matrix Sweep (scans all 16 squares)");
    Serial.println("    [c]           : Toggle Continuous 16-Channel Sweep loop");
    Serial.println("    [t]           : Enroll last scanned tag as a Letter (A..Z)");
    Serial.println("    [e]           : Toggle MUX Enable / High-Z");
    Serial.println("    [?]           : Show this dashboard");
    Serial.println("-------------------------------------------------------");
    Serial.print("> ");
}

// --- Run a single sweep across all 16 channels ---
void performMatrixSweep() {
    Serial.println("\n>>> Starting 16-Channel Matrix Sweep...");
    unsigned long sweepStart = micros();
    int foundCount = 0;

    for (uint8_t ch = 0; ch < 16; ch++) {
        setMuxChannel(ch, true);

        // Fast poll with 20ms timeout
        uint8_t uid[7] = {0};
        uint8_t uidLen = 0;
        bool found = false;

        if (pn532Ready) {
            found = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLen, 25);
        }

        if (found) {
            foundCount++;
            grid[ch].hasTag = true;
            grid[ch].uidLen = uidLen;
            memcpy(grid[ch].uid, uid, uidLen);
            grid[ch].assignedLetter = lookupLetter(uid, uidLen);

            Serial.printf("  [TAG FOUND] Square %2d (R%d,C%d): Letter '%c' | UID=", ch, ch / 4, ch % 4, grid[ch].assignedLetter);
            for (uint8_t i = 0; i < uidLen; i++) {
                Serial.printf("%02X%s", uid[i], (i + 1 < uidLen) ? ":" : "");
            }
            Serial.println();
        } else {
            grid[ch].hasTag = false;
        }
    }

    unsigned long sweepTime = micros() - sweepStart;
    // Restore current channel
    setMuxChannel(currentChannel, muxEnabled);

    Serial.printf("<<< Sweep Finished: %d tiles detected across 16 squares in %lu µs (%.2f ms)\n",
                  foundCount, sweepTime, sweepTime / 1000.0);
    printDashboard();
}

// --- Initialize or Reconnect PN532 ---
bool tryConnectPN532() {
    // Hardware reset pulse
    pinMode(PIN_PN532_RST, OUTPUT);
    digitalWrite(PIN_PN532_RST, LOW);
    delay(10);
    digitalWrite(PIN_PN532_RST, HIGH);
    delay(20);

    nfc.begin();
    uint32_t versiondata = nfc.getFirmwareVersion();

    if (!versiondata) {
        return false;
    }

    // Configure Secure Access Module (SAM) to normal mode
    nfc.SAMConfig();
    // Allow standard retries so tag has time to harvest RF power and respond
    nfc.setPassiveActivationRetries(0xFF);

    Serial.println("\n--------------------------------------------------");
    Serial.print("🎉 [PN532 CONNECTED] Found chip PN5");
    Serial.println((versiondata >> 24) & 0xFF, HEX);
    Serial.printf("   Firmware: v%d.%d (Support: ISO14443A Mifare / NTAG213)\n",
                  (versiondata >> 16) & 0xFF,
                  (versiondata >> 8) & 0xFF);
    Serial.println("--------------------------------------------------");
    return true;
}

void setup() {
    Serial.begin(115200);

    // Initialize Multiplexer control GPIOs
    pinMode(PIN_MUX_S0, OUTPUT);
    pinMode(PIN_MUX_S1, OUTPUT);
    pinMode(PIN_MUX_S2, OUTPUT);
    pinMode(PIN_MUX_S3, OUTPUT);
    pinMode(PIN_MUX_EN, OUTPUT);

    // Default: Channel 0 Enabled
    setMuxChannel(currentChannel, muxEnabled);

    // Clear grid state
    for (int i = 0; i < 16; i++) {
        grid[i].hasTag = false;
        grid[i].assignedLetter = '.';
    }

    // Pre-populate some dummy mappings for demo
    uint8_t demo_uid_p[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x10};
    uint8_t demo_uid_l[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x11};
    uint8_t demo_uid_a[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x12};
    uint8_t demo_uid_y[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x13};
    enrollTag(demo_uid_p, 7, 'P');
    enrollTag(demo_uid_l, 7, 'L');
    enrollTag(demo_uid_a, 7, 'A');
    enrollTag(demo_uid_y, 7, 'Y');

    // Wait briefly for native USB CDC
    delay(1000);

    // Attempt PN532 connection
    pn532Ready = tryConnectPN532();

    printDashboard();
}

void loop() {
    // 1. Retry PN532 connection periodically if not ready
    if (!pn532Ready) {
        if (millis() - lastPn532Retry >= 2000) {
            lastPn532Retry = millis();
            pn532Ready = tryConnectPN532();
            if (pn532Ready) {
                printDashboard();
            }
        }
    }

    // 2. If in continuous sweep mode, run sweeps
    if (continuousSweep) {
        performMatrixSweep();
        delay(300);
    } else {
        // Continuous scan on the ACTIVE CHANNEL
        if (pn532Ready && muxEnabled) {
            uint8_t uid[7] = {0};
            uint8_t uidLen = 0;

            // Poll with 150ms timeout (allows tag time to energize while keeping console responsive)
            bool success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLen, 150);

            if (success) {
                // Check if new or different tag
                bool isNew = (lastTagChannel != currentChannel) ||
                             (lastUidLen != uidLen) ||
                             (memcmp(lastUid, uid, uidLen) != 0) ||
                             (millis() - lastTagDetectTime > 2000);

                if (isNew) {
                    memcpy(lastUid, uid, uidLen);
                    lastUidLen = uidLen;
                    lastTagChannel = currentChannel;
                    lastTagDetectTime = millis();

                    grid[currentChannel].hasTag = true;
                    grid[currentChannel].uidLen = uidLen;
                    memcpy(grid[currentChannel].uid, uid, uidLen);
                    grid[currentChannel].assignedLetter = lookupLetter(uid, uidLen);

                    Serial.println();
                    Serial.println("**************************************************");
                    Serial.printf("  🎯 [TAG DETECTED ON CHANNEL %d (Row %d, Col %d)]\n",
                                  currentChannel, currentChannel / 4, currentChannel % 4);
                    Serial.print("     UID: ");
                    for (uint8_t i = 0; i < uidLen; i++) {
                        Serial.printf("%02X%s", uid[i], (i + 1 < uidLen) ? ":" : "");
                    }
                    Serial.printf(" (%d-byte %s)\n", uidLen, (uidLen == 7) ? "NTAG213" : "Mifare");
                    Serial.printf("     Assigned Letter: '%c' (Points: %d)\n",
                                  grid[currentChannel].assignedLetter,
                                  getLetterPoints(grid[currentChannel].assignedLetter));
                    Serial.println("     -> Press [t] to assign/change this tag's letter!");
                    Serial.println("**************************************************");
                    Serial.print("> ");
                }
            }
        }
    }

    // 3. Periodic dashboard refresh every 10 seconds if idle (no spammy single-line heartbeat)
    if (!continuousSweep && !autoStep && (millis() - lastHeartbeat >= 10000)) {
        lastHeartbeat = millis();
        printDashboard();
    }

    // 4. Handle Terminal Commands
    while (Serial.available() > 0) {
        char c = Serial.read();

        if (c == ' ' || c == '\n' || c == '\r' || c == 'n' || c == 'N') {
            currentChannel = (currentChannel + 1) % 16;
            setMuxChannel(currentChannel, muxEnabled);
            printDashboard();
        } else if (c == 'p' || c == 'P') {
            currentChannel = (currentChannel + 15) % 16;
            setMuxChannel(currentChannel, muxEnabled);
            printDashboard();
        } else if (c == 's' || c == 'S') {
            performMatrixSweep();
        } else if (c == 'c' || c == 'C') {
            continuousSweep = !continuousSweep;
            Serial.printf("\n>>> Continuous 16-Channel Sweep: %s <<<\n", continuousSweep ? "ENABLED" : "DISABLED");
            if (!continuousSweep) printDashboard();
        } else if (c == 'e' || c == 'E') {
            muxEnabled = !muxEnabled;
            setMuxChannel(currentChannel, muxEnabled);
            Serial.printf("\n>>> MUX: %s <<<\n", muxEnabled ? "ENABLED" : "DISABLED (High-Z)");
            printDashboard();
        } else if (c == 't' || c == 'T') {
            // Enroll tag
            if (lastUidLen == 0) {
                Serial.println("\n⚠️ No tag scanned yet! Scan a tag first, then press [t].");
            } else {
                Serial.println("\n--- TAG ENROLLMENT ---");
                Serial.print("Current Tag UID: ");
                for (uint8_t i = 0; i < lastUidLen; i++) {
                    Serial.printf("%02X%s", lastUid[i], (i + 1 < lastUidLen) ? ":" : "");
                }
                Serial.println("\nType the letter you want to assign to this tile (A-Z) and press ENTER:");
                while (Serial.available() == 0) { delay(10); }
                char letter = Serial.read();
                if ((letter >= 'a' && letter <= 'z') || (letter >= 'A' && letter <= 'Z')) {
                    enrollTag(lastUid, lastUidLen, letter);
                    Serial.printf("✅ Successfully enrolled Tag as Letter '%c' (%d pts)!\n",
                                  (letter >= 'a' && letter <= 'z') ? letter - 32 : letter,
                                  getLetterPoints(letter));
                } else {
                    Serial.println("❌ Invalid character. Enrollment cancelled.");
                }
            }
            printDashboard();
        } else if (c == '?' || c == 'h' || c == 'H') {
            printDashboard();
        } else if (c >= '0' && c <= '9') {
            // Check if there is a second digit
            delay(10);
            int val = c - '0';
            if (Serial.available() > 0) {
                char nextC = Serial.peek();
                if (nextC >= '0' && nextC <= '9') {
                    val = val * 10 + (Serial.read() - '0');
                }
            }
            if (val >= 0 && val < 16) {
                currentChannel = val;
                setMuxChannel(currentChannel, muxEnabled);
                printDashboard();
            } else {
                Serial.printf("\n⚠️ Invalid channel %d! Choose 0 to 15.\n> ", val);
            }
        }
    }
}
