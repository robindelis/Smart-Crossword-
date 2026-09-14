#include <Arduino.h>

/*
 * CD74HC4067 16-Channel Multiplexer Interactive Step-Tester
 * Smart Crossword Board - 4x4 Test Grid Hardware Verification
 *
 * Wiring from ESP32-S3 to 4x4 PCB (Header J1):
 *   ESP32 3V3       -->  J1 Pin 1 or 2 (Power)
 *   ESP32 GND       -->  J1 Pin 13, 15, 17, or 19 (Ground)
 *   ESP32 GPIO 15   -->  J1 Pin 11 (MUX_S0: Address bit 0)
 *   ESP32 GPIO 7    -->  J1 Pin 9  (MUX_S1: Address bit 1)
 *   ESP32 GPIO 5    -->  J1 Pin 5  (MUX_S2: Address bit 2)
 *   ESP32 GPIO 4    -->  J1 Pin 3  (MUX_S3: Address bit 3)
 *   ESP32 GPIO 6    -->  J1 Pin 7  (MUX_EN: Active-Low Enable)
 */

#define PIN_MUX_S0   15
#define PIN_MUX_S1   7
#define PIN_MUX_S2   5
#define PIN_MUX_S3   4
#define PIN_MUX_EN   6

int currentChannel = 0;
bool muxEnabled = true;
bool autoStep = false;
unsigned long lastAutoStep = 0;
String inputBuffer = "";

void setMuxChannel(uint8_t ch, bool enable) {
    if (!enable) {
        digitalWrite(PIN_MUX_EN, HIGH); // Disabled (High-Z)
        return;
    }

    // Set address bits
    digitalWrite(PIN_MUX_S0, (ch & 0x01) ? HIGH : LOW);
    digitalWrite(PIN_MUX_S1, (ch & 0x02) ? HIGH : LOW);
    digitalWrite(PIN_MUX_S2, (ch & 0x04) ? HIGH : LOW);
    digitalWrite(PIN_MUX_S3, (ch & 0x08) ? HIGH : LOW);

    // Assert Active-Low Enable
    digitalWrite(PIN_MUX_EN, LOW);
}

void printDashboard() {
    uint8_t row = currentChannel / 4;
    uint8_t col = currentChannel % 4;

    Serial.println("\n==================================================");
    Serial.println("   4x4 PCB MULTIPLEXER (CD74HC4067) STEP-TESTER   ");
    Serial.println("==================================================");

    // 4x4 Visual Representation
    Serial.println("   Board Layout (Top View):");
    Serial.println("      Col 0   Col 1   Col 2   Col 3");
    Serial.println("    +-------+-------+-------+-------+");
    for (uint8_t r = 0; r < 4; r++) {
        Serial.printf("Row%d|", r);
        for (uint8_t c = 0; c < 4; c++) {
            uint8_t ch = r * 4 + c;
            if (muxEnabled && r == row && c == col) {
                Serial.printf(" [*%2d] |", ch);
            } else {
                Serial.printf("   %2d  |", ch);
            }
        }
        Serial.println();
        Serial.println("    +-------+-------+-------+-------+");
    }

    Serial.println();
    if (muxEnabled) {
        Serial.printf("  ACTIVE CHANNEL : Channel %d (Row %d, Col %d)\n", currentChannel, row, col);
        Serial.printf("  BINARY ADDRESS : S3=%d, S2=%d, S1=%d, S0=%d (0b%d%d%d%d)\n",
                      (currentChannel >> 3) & 1,
                      (currentChannel >> 2) & 1,
                      (currentChannel >> 1) & 1,
                      currentChannel & 1,
                      (currentChannel >> 3) & 1,
                      (currentChannel >> 2) & 1,
                      (currentChannel >> 1) & 1,
                      currentChannel & 1);
        Serial.println("  MUX STATUS     : ENABLED (EN / GPIO 6 = LOW, 0V)");
    } else {
        Serial.println("  MUX STATUS     : DISABLED (EN / GPIO 6 = HIGH, 3.3V - All channels disconnected)");
    }

    Serial.println("\n  GPIO Pin States (Measurable with Multimeter):");
    Serial.printf("    - EN (GPIO 6)  : %s (%s)\n", muxEnabled ? "LOW " : "HIGH", muxEnabled ? "0.0V" : "3.3V");
    Serial.printf("    - S3 (GPIO 4)  : %s (%s)\n", (currentChannel & 0x08) ? "HIGH" : "LOW ", (currentChannel & 0x08) ? "3.3V" : "0.0V");
    Serial.printf("    - S2 (GPIO 5)  : %s (%s)\n", (currentChannel & 0x04) ? "HIGH" : "LOW ", (currentChannel & 0x04) ? "3.3V" : "0.0V");
    Serial.printf("    - S1 (GPIO 7)  : %s (%s)\n", (currentChannel & 0x02) ? "HIGH" : "LOW ", (currentChannel & 0x02) ? "3.3V" : "0.0V");
    Serial.printf("    - S0 (GPIO 15) : %s (%s)\n", (currentChannel & 0x01) ? "HIGH" : "LOW ", (currentChannel & 0x01) ? "3.3V" : "0.0V");

    Serial.println("\n  Multimeter Continuity/Resistance Check:");
    Serial.printf("    Probe 1 on J3 center pad (RF_SIG), Probe 2 on Coil %d feed trace:\n", currentChannel);
    Serial.println("    -> Selected channel should measure ~70 Ohms (internal switch Ron).");
    Serial.println("    -> All other 15 channels should measure OPEN circuit (>1 MegaOhm).");

    Serial.println("--------------------------------------------------");
    Serial.print("  Commands: [ENTER]=Next | [p]=Prev | [0..15]=Jump | [a]=Auto | [e]=Enable/Disable\n> ");
}

void setup() {
    Serial.begin(115200);

    pinMode(PIN_MUX_S0, OUTPUT);
    pinMode(PIN_MUX_S1, OUTPUT);
    pinMode(PIN_MUX_S2, OUTPUT);
    pinMode(PIN_MUX_S3, OUTPUT);
    pinMode(PIN_MUX_EN, OUTPUT);

    // Initial state: Channel 0 Enabled
    setMuxChannel(currentChannel, muxEnabled);

    // Give CDC time to open
    unsigned long start = millis();
    while (!Serial && (millis() - start < 2000)) {
        delay(10);
    }

    printDashboard();
}

void loop() {
    // Check for auto-step mode
    if (autoStep && (millis() - lastAutoStep >= 1500)) {
        lastAutoStep = millis();
        currentChannel = (currentChannel + 1) % 16;
        setMuxChannel(currentChannel, muxEnabled);
        printDashboard();
    }

    // Read user console input
    while (Serial.available() > 0) {
        char c = Serial.read();

        if (c == '\r' || c == '\n') {
            inputBuffer.trim();
            if (inputBuffer.length() == 0) {
                // Just ENTER pressed: Next channel
                autoStep = false;
                currentChannel = (currentChannel + 1) % 16;
                muxEnabled = true;
            } else if (inputBuffer.equalsIgnoreCase("p")) {
                // Previous channel
                autoStep = false;
                currentChannel = (currentChannel + 15) % 16;
                muxEnabled = true;
            } else if (inputBuffer.equalsIgnoreCase("a")) {
                // Toggle auto-step
                autoStep = !autoStep;
                lastAutoStep = millis();
                Serial.printf("\n[Auto-Step %s]\n", autoStep ? "STARTED (1.5s per channel)" : "STOPPED");
            } else if (inputBuffer.equalsIgnoreCase("e")) {
                // Toggle Enable/Disable
                muxEnabled = !muxEnabled;
                Serial.printf("\n[MUX %s]\n", muxEnabled ? "ENABLED" : "DISABLED");
            } else {
                // Check if user entered a number (0..15)
                int num = inputBuffer.toInt();
                if (num >= 0 && num <= 15 && (inputBuffer == "0" || num > 0)) {
                    autoStep = false;
                    currentChannel = num;
                    muxEnabled = true;
                } else {
                    Serial.printf("\n[Unknown command: '%s']\n", inputBuffer.c_str());
                }
            }

            setMuxChannel(currentChannel, muxEnabled);
            printDashboard();
            inputBuffer = "";
        } else {
            inputBuffer += c;
        }
    }
}
