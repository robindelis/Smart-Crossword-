package com.example.crosswordcompanion

import com.example.crosswordcompanion.bluetooth.BleProtocol
import org.junit.Assert.*
import org.junit.Test

class BleProtocolTest {

    @Test
    fun testParseBoardState_emptyBoard() {
        val emptyBytes = ByteArray(16) { 0 }
        val parsed = BleProtocol.parseBoardState(emptyBytes)
        assertTrue("Empty byte array should result in empty tile map", parsed.isEmpty())
    }

    @Test
    fun testParseBoardState_dottedBoard() {
        val dotBytes = "................".toByteArray(Charsets.US_ASCII)
        val parsed = BleProtocol.parseBoardState(dotBytes)
        assertTrue("Dotted board should result in empty tile map", parsed.isEmpty())
    }

    @Test
    fun testParseBoardState_validTiles() {
        // Construct 16-byte board: Square 0='W', Square 5='O', Square 6='R', Square 7='D'
        val bytes = ByteArray(16) { 0 }
        bytes[0] = 'W'.code.toByte()
        bytes[5] = 'O'.code.toByte()
        bytes[6] = 'R'.code.toByte()
        bytes[7] = 'D'.code.toByte()

        val parsed = BleProtocol.parseBoardState(bytes)
        assertEquals(4, parsed.size)
        assertEquals('W', parsed[0])
        assertEquals('O', parsed[5])
        assertEquals('R', parsed[6])
        assertEquals('D', parsed[7])
        assertNull(parsed[1])
    }

    @Test
    fun testParseScanTelemetry_activeScanning() {
        // Channel 5 energized, scanning
        val packet = byteArrayOf(5.toByte(), BleProtocol.STATUS_ENERGIZED.toByte())
        val telemetry = BleProtocol.parseScanTelemetry(packet)
        assertEquals(5, telemetry.activeChannel)
        assertEquals(BleProtocol.STATUS_ENERGIZED, telemetry.status)
    }

    @Test
    fun testParseScanTelemetry_tagHit() {
        // Channel 12 tag detected
        val packet = byteArrayOf(12.toByte(), BleProtocol.STATUS_TAG_DETECTED.toByte())
        val telemetry = BleProtocol.parseScanTelemetry(packet)
        assertEquals(12, telemetry.activeChannel)
        assertEquals(BleProtocol.STATUS_TAG_DETECTED, telemetry.status)
    }

    @Test
    fun testParseScanTelemetry_idle() {
        // Sweep complete / idle
        val packet = byteArrayOf(0xFF.toByte(), BleProtocol.STATUS_IDLE.toByte())
        val telemetry = BleProtocol.parseScanTelemetry(packet)
        assertNull(telemetry.activeChannel)
        assertEquals(BleProtocol.STATUS_IDLE, telemetry.status)
    }
}
